# Local project settings

The `.claude/settings.local.json` I keep in a project: the commands Claude Code runs without asking, a hook that stops Claude from reading `.env` files, and a higher cap on web searches.

**Navigation**

- [Where the file lives](#where-the-file-lives)
- [The allow list](#the-allow-list)
- [The deny list](#the-deny-list)
- [The hook](#the-hook)
- [How the hook decides](#how-the-hook-decides)
- [What the hook blocks and what it lets through](#what-the-hook-blocks-and-what-it-lets-through)
- [The env block](#the-env-block)
- [Use it in a project](#use-it-in-a-project)
- [Sources](#sources)

Files: [settings.local.json](settings.local.json) (the settings) · [hooks/block-env-read.py](hooks/block-env-read.py) (the hook script)

## Where the file lives

| Part | What it means |
|---|---|
| `.claude/settings.local.json` | Your own settings for one project. Claude Code reads it from the root of the git repository, even when you start in a subfolder. In a linked worktree it reads the one in the main checkout. On Windows, outside a git repository, when the repository root is your home folder, or when the repository root, its `.git` or its `.claude` is not owned by your user, it reads the file from the folder you start in instead, so a session started in a subfolder or a worktree runs without this file and without the guard. |
| Precedence | It wins over the project's shared `.claude/settings.json` and your `~/.claude/settings.json`. Managed settings and `claude --settings` win over it. |
| Lists | List keys such as `permissions.allow` are merged across files: this file adds rules, it does not replace the rules in other files. |
| Git | The first time Claude Code writes the file in a repository that does not ignore it yet, it adds `**/.claude/settings.local.json` to your global git excludes, which covers every repository. A file you copy in by hand may not be covered yet: check it (step 3 of [Use it in a project](#use-it-in-a-project)). |

Keep it out of git. A tracked copy counts as supplied by the repository, so Claude Code holds its allow rules until you trust the folder.

## The allow list

`permissions.allow` lists the tool calls that run without a permission prompt.

| Rule | What runs without a prompt |
|---|---|
| `WebSearch` | Every web search. |
| `WebFetch(domain:modelcontextprotocol.io)` | Page fetches from that host only, not from its subdomains. |
| `WebFetch(domain:docs.astral.sh)` | Page fetches from the uv and ruff docs. |
| `Bash(uv run ruff check:*)`, `Bash(uv run ruff format:*)`, `Bash(uv run pyright:*)`, `Bash(uv run pytest:*)`, `Bash(uv sync:*)` | The Python checks and tests, and installing the project's dependencies. |
| `Bash(pnpm test:*)`, `Bash(pnpm typecheck:*)`, `Bash(pnpm lint:*)`, `Bash(npm test:*)`, `Bash(npm run lint:*)`, `Bash(npm run build:*)` | The JavaScript tests, checks and build. |
| `Bash(make test:*)`, `Bash(make check:*)` | The same through a Makefile. |
| `Bash(git show:*)`, `Bash(git status:*)`, `Bash(git diff:*)` | git commands that show the repository's state. `git diff --output=<file>` and `git show --output=<file>` write that file instead, and these rules let them run without a prompt too. |

How a `Bash` rule matches:

- `:*` at the end means "this command, alone or with anything after a space". `Bash(git diff:*)` matches `git diff` and `git diff --cached`, but not `git difftool`. It matches the same commands as `Bash(git diff *)`, the form Claude Code's permission prompt writes when you choose "don't ask again".
- A compound command runs without a prompt only when every part matches a rule or is one of Claude Code's built-in read-only commands, such as `ls` or a `cd` inside the project. `uv sync && rm -rf build` still asks about `rm`.
- `npm test`, `pnpm lint` and `make check` run whatever the project's `package.json` or `Makefile` defines. An allow rule for them trusts those files, so allow them only in projects whose scripts you trust.

Other calls, such as `git commit`, `git push`, `rm` or a fetch from another host, go through the permission mode you run in: a prompt in Manual mode, the classifier in auto mode.

## The deny list

`permissions.deny` lists the tool calls that never run. Here it is empty, so this file adds no deny rules. Deny rules from your other settings files still apply.

Claude Code checks the rules in this order: deny, then ask, then allow. The first match decides, so a deny rule in any settings file wins over an allow rule in any other.

The `.env` guard here is the hook, not a deny rule.

## The hook

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Read|Grep|Bash|PowerShell",
      "hooks": [
        { "type": "command", "command": "\"$(git -C \"${CLAUDE_PROJECT_DIR}\" rev-parse --path-format=absolute --git-common-dir)/../.claude/hooks/block-env-read.py\"",
          "onFailure": "block" }
      ]
    }
  ]
}
```

| Part | What it means |
|---|---|
| `PreToolUse` | The event: the hook runs before each matching tool call, before any permission prompt. |
| `"matcher": "Read\|Grep\|Bash\|PowerShell"` | The tools the hook runs for. A matcher made of names and `\|` is a list of exact tool names, not a regular expression. Other tools, such as `Glob`, never reach the script. PowerShell is Claude Code's shell tool on Windows, so a hook that checks shell commands matches it next to Bash. |
| `"type": "command"` | Run a program. Claude Code passes the tool call to it as JSON on stdin. |
| `"command"` | The path to the script, worked out at each call. The hook runs in Claude's current folder, which moves when Claude runs `cd` inside the project, so the command asks git about `${CLAUDE_PROJECT_DIR}`, the folder the session started in, which stays put. From there `git rev-parse --git-common-dir` prints the main checkout's `.git` folder, whether the session started at the root, in a subfolder or in a linked worktree, so the hook runs the one script in the main checkout's `.claude/hooks/`, also after Claude moves into a submodule or another repository. Claude Code reads this settings file from the same main checkout, except in the cases listed in [Where the file lives](#where-the-file-lives). The quotes keep a path with a space in one piece. It needs git 2.31 or later, and the project must be a git repository. `${CLAUDE_PROJECT_DIR}` alone would not work: from a subfolder or a worktree it points where the script is not. The command also needs a POSIX shell: Claude Code uses `sh` on macOS and Linux and Git Bash on Windows. On Windows without Git Bash, Claude Code runs the command in PowerShell, which prints a quoted string instead of running it: the script never starts, the hook exits with 0, and the guard is off with no error. |
| `"onFailure": "block"` | When the hook cannot run under `sh` or Git Bash — the script is missing or not executable, `python3` is not on `PATH`, the folder is not a git repository, the script crashes or times out — Claude Code blocks the call instead of letting it through. This does not cover PowerShell: there the command prints its path and exits with 0, which Claude Code counts as success (see `"command"` above). The default, `continue`, would let a `.env` read through with only a hook error. It needs Claude Code 2.1.295 or later. |
| no `timeout` | The default applies: 600 seconds for a command hook. |

## How the hook decides

The script reads `tool_name` and `tool_input` from stdin and checks the tool's fields against one rule. It decodes stdin as UTF-8 itself, because on Windows Python would read a pipe in the ANSI code page. A protected name is the last part of a path that is `.env`, or starts with `.env.` (a variant such as `.env.local`), or starts with `.env*`, `.env?` or `.env[` (a pattern that matches `.env` files). `.env.example` and `.env.local.example` are not protected. Backslashes count as `/`, so Windows paths work.

| Tool | Field it reads | It blocks when |
|---|---|---|
| `Read` | `file_path` | The path ends in a protected name. |
| `Grep` | `path`, `glob` | The path ends in a protected name, or a part of the glob is one. The glob is split into parts at `{`, `}`, `,` and `/`. |
| `Bash`, `PowerShell` | `command` | A word of the command ends in a protected name. The command is split into words at whitespace, quotes, shell operators, redirections, `=` and `:`, and each word is checked. The hook does not run or parse the command. |

To block, the script prints this JSON and exits with 0:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Reading protected .env files is forbidden: /repo/.env"
  }
}
```

Claude Code then blocks the call and shows the reason to Claude, so Claude knows why and can work without the file. The deny holds even when an allow rule matches the call. When the script prints nothing and exits with 0, the call goes on to the normal permission rules.

## What the hook blocks and what it lets through

I ran the script on these inputs (macOS, Python 3.9, 2026-10-11).

| Input | Result | Why |
|---|---|---|
| Read `.env`, `.env.local`, `.env.production.local`, and the Windows path `C:\repo\.env` | blocked | Protected file names. |
| Read `C:\Проекты\app\.env`, with stdin in the Windows ANSI code page (simulated with `PYTHONIOENCODING=cp1252`) | blocked | The script decodes stdin as UTF-8 itself, so a non-ASCII path does not switch the check off. |
| Grep with glob `.env*`, `**/.env*` or `{.env.example,.env}`, or with path `.env` | blocked | The search targets protected files. |
| `cat .env`, `cat ./.env`, `grep KEY .env.local`, `sed -n '1,10p' apps/api/.env`, `cat .env.production.local`, `cat .env.local.bak`, `source .env.test.local`, `cat .env.*`, `grep API_URL .env*`, `docker run --env-file=.env app` | blocked | The command names a protected file, or a pattern that matches one. |
| `python -c "open('.env').read()"`, `cp .env /tmp/x` | blocked | Same: the hook reads the text, not the program. |
| PowerShell `Get-Content .env`, `Get-Content -Path .\.env.local` | blocked | The same rule as in Bash. On Windows without Git Bash the hook does not run at all (see `"command"` in [The hook](#the-hook)). |
| Read `.env.example`, `.env.local.example`, `.envrc`, `config.env` | allowed | Not protected files, on purpose. |
| `cat .env.example`, `cat .env.local.example` | allowed | The allowed example files. |
| `echo 'copy .env.example to .env'` | blocked | A false block: the text names `.env`, though nothing reads it. |
| `cat .e*` | allowed | A gap: the pattern does not start with `.env`. |
| `grep -r KEY .` | allowed | A gap: a folder search never names the file. |
| Grep over a whole folder with no glob | allowed | A gap: the hook checks only `path` and `glob`. |
| Grep with glob `*.env` or `*.env*` | allowed | A gap: the hook checks only names that start with `.env`. |
| Input that is not a JSON object (bad JSON, a JSON array, bad UTF-8) | allowed | The script exits with 0 and prints nothing. |

If the hook cannot run under `sh` or Git Bash (see `onFailure` in [The hook](#the-hook)), Claude Code blocks every Read, Grep, Bash and PowerShell call and shows a hook error, so a broken guard is loud. On Windows without Git Bash it is silent: see `"command"` in [The hook](#the-hook). I checked the loud case with Claude Code 2.1.296: with the script missing, a Read was blocked; without `onFailure`, the same Read went through.

So the hook stops Claude from opening `.env` by accident. It is not a security boundary. For a limit that holds for every process, Claude Code's docs point to the sandbox.

## The env block

`env` sets environment variables that Claude Code applies to its sessions in this project. This file sets one.

| Part | What it means |
|---|---|
| `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` | The cap on WebSearch calls in one interactive session. The default is 200, and the main conversation and its subagents share it. At the cap, a search returns a notice that tells Claude to go on with what it already found. |
| `"3000"` | 15 times the default, so long sessions with parallel research agents do not hit it. Claude Code takes a positive whole number; anything else is ignored and the default applies. The cap can be raised but not turned off. It needs Claude Code 2.1.212 or later. |

The value is written as a string, as in the examples in Claude Code's docs.

## Use it in a project

1. Copy `settings.local.json` into the project's `.claude/` folder. That is where Claude Code looks for your own project settings. If the project already has the file, merge the keys by hand: copying over it deletes the approvals Claude Code saved there.
2. Copy `hooks/block-env-read.py` into `.claude/hooks/` of the main checkout and keep it executable (`chmod +x .claude/hooks/block-env-read.py`). The `command` path points there through git, also when you work in a linked worktree, and Claude Code runs the file through `sh` or Git Bash, which read its `#!/usr/bin/env python3` line. On Windows, install Git Bash first.
3. Check that git ignores the settings file: `git check-ignore -v .claude/settings.local.json` prints the rule that ignores it, and prints nothing when no rule does. The hook script is a separate file: commit it so the team gets it, or ignore it as well.
4. Run `/status` in Claude Code to see that the file loaded. Claude Code reloads settings files when they change, so a running session picks up the edit.
5. Check the guard without touching the real file. Run `/hooks` in Claude Code: the hook is listed from local settings. Then ask Claude to read `.env.hook-check`, a file that does not exist. Claude Code shows a block as a hook error, and the text after it tells the cases apart. `Reading protected .env files is forbidden: …`: the guard works. A message about a missing file or a command that failed: the hook cannot run, see `onFailure` in [The hook](#the-hook). Claude says the file does not exist: the hook is not active (on Windows, check that Git Bash is installed).

## Sources

- Anthropic, "Settings files and precedence": https://code.claude.com/docs/en/settings (where `settings.local.json` lives, the precedence order, merged lists, the global git excludes, the `env` block as an ordinary key, `/status`, reloads on change)
- Anthropic, "Configure permissions": https://code.claude.com/docs/en/permissions (deny, ask, allow order; `:*` equals a trailing ` *`; compound commands; `WebFetch(domain:…)`; a blocking hook over allow rules; trust for a tracked local file; the sandbox for limits on every process)
- Anthropic, "Choose a permission mode": https://code.claude.com/docs/en/permission-modes (Manual mode and the auto mode classifier)
- Anthropic, "Hooks reference": https://code.claude.com/docs/en/hooks (matcher forms, `${CLAUDE_PROJECT_DIR}`, quoting a path placeholder in shell form, the PreToolUse input fields, `permissionDecision` and where its reason goes, exit codes, `onFailure`, the 600-second default timeout)
- Anthropic, "Environment variables": https://code.claude.com/docs/en/env-vars (`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`, the `env` key)
- Anthropic, "Tools reference": https://code.claude.com/docs/en/tools-reference (the session search limit, shared with subagents; the PowerShell tool, and matching `Bash|PowerShell`)
- Git, 2.31.0 release notes: https://www.kernel.org/pub/software/scm/git/docs/RelNotes/2.31.0.adoc (`git rev-parse --path-format`)
