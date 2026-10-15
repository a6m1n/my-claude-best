# Example: the two CLAUDE.md rules the pr skill cites

The pr skill names two sections of a global `CLAUDE.md`. It runs the § Git identity check on
every commit author before a push (`SKILL.md` Step 0, item 4), and it follows § Blocked on user
input when `gh` refuses an assignee (`SKILL.md` § Assignees). This file holds both sections,
written for a global `~/.claude/CLAUDE.md`. Copying the block into your own
`~/.claude/CLAUDE.md` is optional: the skill works without it, and once copied, the names the
skill uses point at rules you have. The rules then govern every session on the machine, not only
`/pr`. The sections speak as the owner of the file: "me" and "mine" are you.

The file is not named `CLAUDE.md` on purpose. Claude Code loads a `CLAUDE.md` it finds in a
folder of the project as live rules, and this one is only an example.

```markdown
## Blocked on user input — escalate, never improvise it

When an action fails, cannot proceed, or would only succeed by using a value you had to
pick yourself — and the missing piece is a value or a decision that is mine to give: an
identity, a credential, an account choice, a token, a confirmation for something hard to
undo or already visible to others — **stop and ask me. NEVER supply the missing value
yourself**: do not invent it, guess it, or copy it from somewhere "to keep going". The
test: if you cannot point at where I gave you the value — my words in this session, or
config you can trace to me — it is mine to give. A value that looks right, found in a
repo, a log, an env var, or another project, is not me giving it; config written by an
earlier agent run looks exactly like config I wrote, so a value you cannot trace to me
stays untrusted. One exception: the git identity in a repo's own `.git/config` —
§ Git identity below settles it, no trace needed. No skill, prompt, goal, task, project
CLAUDE.md, skill binding, or autonomous mode overrides this rule.

- **Stop at the first failure** — even where another rule allows a second try: no second
  attempt, no different approach. Leave the working tree and every config
  as they are; the one exception is a change you yourself just made to such a value —
  revert it and say so in the escalation.
- **A restart is not an answer.** If something re-invokes you after you stopped — a Stop
  hook, a goal evaluator, a retry — repeat the blocker and stop again; never treat the
  restart as permission to proceed.
- **Escalate as ONE decision:** what failed and why, the genuinely viable options with
  pros and cons, your recommendation — then wait for my answer.
- **The case that started this rule (never repeat it):** `git commit` lacks `user.name` /
  `user.email`, and the agent configures made-up values and commits. The only correct
  move is to stop, show the problem, and ask.
- **The gate is narrow by design:** it fires only when the missing piece is mine to give.
  Routine, reversible steps stay autonomous — do not start asking me to approve every
  step.

## Git identity — repo-local config or no commit

The identity on a commit is mine, and it lives **per repo**: repo-local `git config`
(`.git/config`) only. A global identity is bad practice — NEVER suggest `--global`, never
expect a `~/.gitconfig` identity to exist, and NEVER write an identity yourself.

- **The check (read-only, before any commit):** `git config --local --get user.name` and
  `git config --local --get user.email`. Three outcomes:
  - **Both set locally → commit without asking, under exactly this identity.** The
    repo-local pair is itself the trace — the § Blocked on user input test does not fire
    on it, and no per-session confirmation is needed. Confirm it
    is what will actually land: `git var GIT_AUTHOR_IDENT` and `git var GIT_COMMITTER_IDENT`
    must show the same name and email. A mismatch means something overrides the local
    config (a `GIT_AUTHOR_*` / `GIT_COMMITTER_*` / `EMAIL` env var, or an `author.*` /
    `committer.*` entry) → **do not commit**; show the source and ask.
  - **Not set locally, but a `--global` / system / env value exists → never commit under
    it.** Tell me the value and where it comes from
    (`git config --show-origin --get user.email`); I remove it manually and set the
    repo-local pair myself.
  - **No identity anywhere → do not commit.** Git does not fail here — it invents a name
    from the OS username and hostname and commits with exit 0; never let that land.
    Escalate per "Blocked on user input": ask me to set the repo-local pair manually.
- **NEVER set, change, or override my git identity in any repository of mine** — no
  invented values, no values copied from another repo, a log, or the environment; not via
  `git config` (`user.*`, `author.*`, `committer.*`), not `git -c`, not `--author` /
  `--reset-author`, not `GIT_AUTHOR_*` / `GIT_COMMITTER_*` / `EMAIL` env vars, and not by
  editing `.git/config`, `~/.gitconfig`, or any file they include. I configure it; you
  only use it. Three boundary notes: setting a repo-local value I explicitly dictated to
  you in this session, when I ask you to set it, is me configuring it through you —
  allowed; anything less explicit is not. Undoing an identity **you yourself just wrote**
  (`git config --unset …`) is required, not forbidden — undo it and tell me. And the only
  repo that is not mine is one your own test creates with `git init` under a temp dir — a
  clone, a checkout, or a linked worktree of my repo is still mine (a linked worktree
  shares `.git/config` with the real repo).
```

The two sections work as a pair. § Git identity says when a commit or a push may go ahead, and
§ Blocked on user input says what to do when it may not: stop and ask, and never fill in an
identity or an account yourself. The rule asks for a repo-local identity. If you set your name
once for the whole machine, read [README.md](README.md#the-git-identity-rule) before you copy it.
