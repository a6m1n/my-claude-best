# pr

A Claude Code skill that writes the pull request for the current branch from one fixed template,
shows you the draft, and opens or updates the pull request only after your yes.

**Navigation**

- [What it does](#what-it-does)
- [Install](#install)
- [What to fill in](#what-to-fill-in)
- [Where it departs from git.md](#where-it-departs-from-gitmd)
- [Files](#files)

## What it does

You type `/pr`, or say "open a PR" or "update the PR". The skill checks whether the branch
already has an open pull request and works in one of two modes:

| Mode | When | What it does after your yes |
| --- | --- | --- |
| CREATE | the branch has no open pull request | pushes the branch and runs `gh pr create`, with you as the assignee |
| UPDATE | the branch has an open pull request | pushes new commits and runs `gh pr edit`; sections that others added to the description stay word for word |

It reads every commit and the whole diff, then writes the title and the description. The
description has Summary, the ticket link, What's Changed and Verification, plus ⚠️ Breaking
Changes, Notes and Risks only when the change has something real to put in them. It shows the
draft in one code block, says in one line what your yes will do, and stops. Nothing is pushed,
and no `gh pr create` or `gh pr edit` runs, before your yes; until then the skill only reads.
The one exception is an explicit ask to push, such as "push the commit": then it pushes after
the author check below, and on your own open pull request with an empty Assignees field it adds
you.

It also handles stacked pull requests, where one pull request sits on top of another open one.
GitHub offers stacks as a public preview, through the `gh-stack` extension of the GitHub CLI.

[output_example.md](output_example.md) shows what the skill prints in each mode, on invented
values. Read it first to see what you get.

## Install

The skill needs Claude Code, git, and the GitHub CLI `gh`, signed in to the account that opens
your pull requests (`gh auth status` shows which one). It also expects a name and email set with
`git config --local` in each repository (`git config --local --get user.email` prints it);
without them it stops before every push (see [The git identity rule](#the-git-identity-rule)).

1. From a clone of this repository, copy the skill folder into your user-level skills folder:

   ```bash
   mkdir -p ~/.claude/skills
   cp -R skills/pr ~/.claude/skills/
   ```

   If you already have a skill named `pr`, back it up first: the copy replaces
   `~/.claude/skills/pr/`. A command named `pr` in `.claude/commands/` stops working, because a
   skill wins over a command of the same name. And a project that already has its own skill at
   `.claude/skills/pr/SKILL.md` hands that file to this skill as its binding.

   Install it at the user level, not in a project's `.claude/skills/`. The skill reads facts
   about a project from a binding file at `.claude/skills/pr/SKILL.md` in that project (see
   [What to fill in](#what-to-fill-in)). When a skill of the same name sits in both places,
   Claude Code runs the user-level one, so the project's file stays free to act as the binding.
   A copy in a project's `.claude/skills/pr/` works too, but it then reads itself as its own
   binding: write that project's facts into the copy itself.

2. Optional: copy the block from [claude-md-example.md](claude-md-example.md) into your
   `~/.claude/CLAUDE.md`. The skill's author check and its "ask the user" step name these two
   rules, § Git identity and § Blocked on user input, but the skill's own text already spells out
   both checks, so it works without them. Once copied, the rules govern every session on the
   machine, not only `/pr`: for example, with no repo-local name and email, Claude Code refuses
   to commit in any repository.

3. Start a new Claude Code session, so it loads the skill. On a branch with commits, type
   `/pr`. You get the draft and one line that says what your yes will do.

For stacked pull requests, the skill also needs the `gh-stack` extension (`gh extension list`
shows it). When it is missing, the skill asks before it installs it.

The trigger phrases sit in the `description` field of the `SKILL.md` front matter, in English.
To start the skill with phrases in your own language, add them to that field. Keep the addition
short: the field is about 1,320 characters, and Claude Code cuts the listing text of a skill at
1,536 characters, so a longer text loses its end.

`SKILL.md` mentions a separate skill for posting review comments, "where present". It is not in
this repository, and this skill works without it.

## What to fill in

Nothing else is required to start when your default branch is `main`, your remote is `origin`,
and each repository has its own name and email (see Install). If your branch names carry ticket
keys, also add the ticket section's title and the tracker URL template, or check the ticket link
in each draft. Without a binding, the skill finds the ticket pattern in the branch names and
commits, and the check commands in the project's instruction files. Fill in what you want it to
use every time.

### The project binding

Create `.claude/skills/pr/SKILL.md` in a project and commit it, so every clone and worktree of
the project has it. With the skill installed at the user level, Claude Code does not run this
file as a skill: the skill reads it at the start of each run, and where the two conflict, the
binding wins. It holds facts about that repository only:

| Fact | What the skill does with it | Without a binding |
| --- | --- | --- |
| The ticket-key pattern | Finds the ticket in the branch name, such as `PROJ-123` in `feat/PROJ-123-short-name` | Taken from the branch names and commits |
| The ticket section's title and the tracker URL template | Writes the ticket section, such as `## Jira Ticket` with `[PROJ-123](https://tracker.example.com/browse/PROJ-123)` | `SKILL.md` gives only an example here (`## Jira Ticket`, a link to `tracker.example.com`), so without these two facts the section can carry that example's title and a link that goes nowhere: read it in the draft before your yes, or add these two facts |
| The check commands, per stack | Lists them in Verification: the ones run in this session, with their results, under *Checked in this session*; the rest under *For the reviewer* | Taken from the project's instruction files or build config |
| The repository's catalog of breaking changes | Knows what to put in ⚠️ Breaking Changes | Only the general list in `SKILL.md` Step 3 |
| Paths outside the reviewable change | Leaves them out when it reads the diff, such as a folder of working notes | `SKILL.md` names no other source for them: list them here to be sure |

A binding can be this short:

```markdown
---
name: pr
description: Project facts for the pr skill. Not a skill of its own.
user-invocable: false
disable-model-invocation: true
---

- Ticket key: `PROJ-123`, in the branch name as `feat/PROJ-123-short-name`.
- Ticket section: `## Jira Ticket`, link `https://tracker.example.com/browse/<KEY>`.
- Checks: backend `make test lint`; web `npm run test && npm run lint`.
- Breaking changes here: a renamed API field, a new required environment variable.
- Not part of the change: `docs/artifacts/`.
```

With `user-invocable: false` and `disable-model-invocation: true`, a teammate who has not
installed the skill gets no `/pr` made of the binding's fact lines.

### The default branch and the remote

The skill takes `main` as the base of a new pull request, and it stops when you run it on `main`
(`SKILL.md` Step 0, items 1 and 2, and § Stacked PRs). If one repository's default branch has
another name, such as `master` or `develop`, add a line to that repository's binding, such as
`- Default branch: develop. Use it wherever SKILL.md says main.` The binding wins on conflict
(`SKILL.md` § Project binding), but `SKILL.md` does not list the default branch among the
binding's facts, so on the first run check the base in the line that says what your yes will do
(`gh pr create --base …`). Edit `main` in your copy only when every repository you use has the
same other default branch, because the copy in `~/.claude/skills/pr/` serves all of them.

The skill also pushes to and compares with the remote named `origin` (`SKILL.md` Step 0, item 4,
and Step 5). If yours has another name, add a line to the binding as for `main`. For a pull
request whose branch lives in someone else's fork, push the branch yourself, and answer no when
the line on what your yes will do says the skill pushes: its `git push -u origin HEAD` would put
the branch on `origin` as a new branch and leave the pull request as it was.

The skill compares your branch with your local `main` and does not fetch. Bring your local `main`
up to date with the remote before you run `/pr`, or the description also covers commits that are
already merged.

### The git identity rule

Before every push, the skill checks the author of every commit between the base branch and your
branch (`git log <base>..HEAD`), commits already on the remote included, by § Git identity from
[claude-md-example.md](claude-md-example.md). A teammate's commit on your branch stops the push
too. An author passes only when it is the name and email set in the repository's own config
(`git config --local`). An author that git made up from the computer's user and host name stops
the push, and so does any other author. The skill then asks you and never changes an author
itself.

If you set your name once for the whole machine (`git config --global`), this check stops before
every push, and with the block from [claude-md-example.md](claude-md-example.md) in your
`CLAUDE.md`, Claude Code also refuses commits under such a name. Either set the name and email
in each repository with `git config --local`, or change two places together in your copy: the
check in `SKILL.md` Step 0 item 4, and the rule in your `CLAUDE.md`.

### Permissions

The `allowed-tools` line in the `SKILL.md` front matter lists the commands the skill may run with
no permission prompt: git reads, `git push`, and `gh pr`, `gh repo` and `gh stack` commands.
Claude Code applies that grant only in the turn that starts the skill
([skills docs](https://code.claude.com/docs/en/skills)). After a draft, the push and
`gh pr create` or `gh pr edit` run after your yes, in a new turn, so there your own permission
settings decide whether Claude Code asks first. An explicit ask to push is different: the push,
and the assignee change on your own pull request, run in the turn that starts the skill, under
this grant. Remove a command from the line if you want a prompt for it even in the first turn.

The wide entries `Bash(git push *)`, `Bash(gh pr *)`, `Bash(gh repo *)` and `Bash(gh stack *)`
also match commands the skill does not run unless you ask for them, such as `gh pr merge`,
`gh pr close`, `gh repo delete`, `gh stack merge`, `git push --force` and
`git push origin --delete`. In the first turn the skill also reads text other people wrote:
commit messages and the pull request description. Such text can ask Claude to run one of those
commands, and in that turn it runs with no prompt. If you want a prompt for those commands,
replace the wide entries in your copy with the ones the steps use: `Bash(git push -u origin HEAD)`,
`Bash(gh pr view *)`, `Bash(gh pr list *)`, `Bash(gh pr create *)`, `Bash(gh pr edit *)`,
`Bash(gh stack link *)` and `Bash(gh extension list)`.

## Where it departs from git.md

This skill was written before the git practice of this repository,
[git.md](../../docs/engineering/any-language/git/git.md), and it is published as it is. In
four places it does not follow that practice:

| | The skill | git.md |
| --- | --- | --- |
| Title type | one of `feat`, `fix`, `refactor`, left out for a mixed change (`SKILL.md` Step 2) | one of six: `feat`, `fix`, `refactor`, `docs`, `test`, `chore` (sections 2 and 4) |
| Section order in the `description` field | Notes before ⚠️ Breaking Changes | ⚠️ Breaking Changes, Notes, Risks (section 4) |
| Base of a stacked pull request | the branch of the layer below (`SKILL.md` § Stacked PRs) | `main` (section 4); section 6 leaves stacked pull requests to each project's policy |
| Stack maintenance | on your explicit ask, it runs `gh stack merge`, `rebase`, `sync`, `modify` or `push` itself (`SKILL.md` § Stacked PRs): merge lands pull requests, and `push` and `sync` force-push the rewritten branches (with a lease) | a human lands the pull request, and an agent never merges its own (section 5); an agent never force-pushes, and section 6 leaves stacked pull requests to each project's policy, where the agent stops and asks |

The section order in the `description` field is only the listing text Claude reads to pick the
skill. The template the skill writes by, `SKILL.md` Step 3, uses the order of git.md. A full
pull request in that form is in
[pr-example.md](../../docs/engineering/any-language/git/pr-example.md). If you follow git.md
too, change the title types, the stacked base and the stack-maintenance line in your copy, or
keep them and know where the two differ.

## Files

- [SKILL.md](SKILL.md): the procedure, from finding the mode to the commands after your yes,
  with the template. Read it before you change what the skill writes or runs.
- [output_example.md](output_example.md): what the skill prints in each mode, on invented
  values. Read it first.
- [claude-md-example.md](claude-md-example.md): the two global `CLAUDE.md` rules that the skill
  names. Optional: copy its block
  into your `~/.claude/CLAUDE.md` (Install, step 2).
