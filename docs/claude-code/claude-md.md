# CLAUDE.md: what to put in it, and what to keep out

Claude Code reads `CLAUDE.md` at the start of every session, and reads the project-root file again after every `/compact`. Every line in it sits in the context window during every task, whether the task needs it or not. That is the design constraint: the file is a rule sheet the agent always has in front of it, not a project description.

**Navigation**

- [The one test for every line](#the-one-test-for-every-line)
- [What goes in](#what-goes-in)
- [What stays out](#what-stays-out)
- [README.md and CLAUDE.md are different documents](#readmemd-and-claudemd-are-different-documents)
- [How to write a line an agent can follow](#how-to-write-a-line-an-agent-can-follow)
- [When to add a line, and when to cut one](#when-to-add-a-line-and-when-to-cut-one)
- [Where the files live](#where-the-files-live)
- [Example: a small project CLAUDE.md](#example-a-small-project-claudemd)
- [Sources](#sources)

This doc says what earns a place in `CLAUDE.md`, what goes somewhere else, and how to write a line so an agent can follow it.

## The one test for every line

Ask two questions, in this order.

1. "Would removing this line make Claude do something wrong?" If the answer is no, cut the line. Anthropic's own guidance gives the same test and the reason behind it: a bloated file makes Claude ignore the rules that matter.
2. "Does every task need this line?" If not, the line goes to a topic file, such as the file for git work, for running commands, or for writing code, and `CLAUDE.md` keeps one pointer to that file (next section).

One exception to question 2: a hard rule stays in `CLAUDE.md`, whatever its topic, when review will not stop a miss. Either the harm happens at the act itself (a push, a call to a live service), or it hides easily in a diff (a key in a config file). A pointer works only when Claude decides to open the file, and for these rules one skipped read is already the harm.

The official target is under 200 lines per file. Shorter works better.

## What goes in

Two places, sorted by how many tasks need a line.

In `CLAUDE.md` itself go the lines that every task needs, and the hard rules the exception keeps:

- The language of code, comments, commit messages, and docs. "English everywhere" is one line; without it an agent answers in the language of the chat.
- Style that differs from the default, for the text Claude writes on any task: its answers, docs, and commit messages. Not "write clean code"; Claude does that anyway. A rule like "B2-level English, no filler words" is worth a line because Claude would not guess it. Code style, such as "no default exports", goes to the conventions file, because only code work needs it.
- Hard rules that fall under the exception, each with its reason in the same line. "Never commit `.env` files; a pushed secret cannot be taken back." "No customer names in test data; the repo is public." A hard rule gets one `IMPORTANT` at most. If every line shouts, none stands out.
- One pointer per topic file, and each pointer names the moment to read its file: "Before you branch, commit, or merge, read `docs/git.md`."

In a topic file go the lines that not every task needs. The file stays out of context until the pointer's moment comes:

| Topic file | What it holds | The pointer's moment |
|---|---|---|
| `docs/git.md` | Branch names, the commit message format, what to run before a commit, how a change goes to review | Before you branch, commit, or merge |
| `docs/commands.md` | Commands Claude cannot guess and when to run them; what a command needs that the code does not show, such as a required environment variable or a local database | Before you build, run, or test anything |
| `docs/conventions.md` | Where new things go, one line per kind ("API handlers go in `src/api/handlers/`"); code style that differs from the default; project rules no linter checks | Before you write, plan, or review code |

Why split: every line in `CLAUDE.md` is in context on every task, and a line the task does not need still competes with the lines it does need. A question opens none of the topic files, a code review opens only `docs/conventions.md`, and a code change opens each one at the step that needs it. So every task that is not a code change loads less, and `CLAUDE.md` stays short while the topic files grow. Claude Code's own auto memory works the same way: the `MEMORY.md` index loads every session, and Claude reads the topic files when it needs them.

This departs from Anthropic's advice for `CLAUDE.md`. Its memory page keeps "build commands, conventions, project layout" in the file, and its best-practices include table lists bash commands, testing instructions, branch naming, and environment quirks. Both pages agree on the aim, which the best-practices page puts as "only include things that apply broadly". For the rest, that page sends what is "only relevant sometimes" to skills, and the memory page sends a procedure or a rule for one part of the codebase to a skill or a path-scoped rule. Neither sends it to plain files. This guide uses plain topic files behind a pointer, as HumanLayer's guide does: they hold reference lines that people read too, not procedures, and each pointer names the step that needs its file. A procedure, such as a release, is still a skill, and a rule for one folder is still a path-scoped rule (next section).

What the split costs: Claude sees a topic file only when it decides to open it. So each pointer names a moment Claude can recognise (see "How to write a line an agent can follow"), and a hard rule that review would not catch stays in `CLAUDE.md` (the exception in "The one test for every line").

Write each pointer's path in backticks, never as an `@` import. An import loads the file at every launch, which undoes the split (see "Where the files live").

## What stays out

- The layout of the repo. What `ls` shows, `CLAUDE.md` should not repeat. A folder list or a "what lives where" section belongs in `README.md`, where a person reads it once. The rule about where new files go stays, in the conventions file (above). The tree itself is what Claude Code's own `/doctor` command proposes to cut from a checked-in `CLAUDE.md`, along with dependency lists and architecture overviews. A one-line pointer with its moment ("Before you look for where something lives, read the project structure in `README.md`") is enough.
- Multi-step procedures. A release checklist, a review flow, a ticket template. These are skills: they load when they are needed, not on every task.
- Rules for one part of the codebase. "All handlers validate input" matters only under `src/api/`. Put it in `.claude/rules/api.md` with a `paths:` field, and it loads only when Claude touches those files.
- Long explanations. API docs and tutorials. Link them.
- Facts that change often. A version number, the name of the person on call. They go stale in the file before anyone notices.
- What Claude already knows. Standard language conventions, how git works, what a README is.
- What a tool enforces better. A formatter, a linter, a pre-commit hook, or a Claude Code hook runs every time; `CLAUDE.md` is advice the model may miss. Anthropic's docs call the file "context, not enforced configuration", and point to hooks for anything that must happen with no exceptions.
- Personal preferences. Your sandbox URL, your test data. Those go in `~/.claude/CLAUDE.md` (all your projects) or `CLAUDE.local.md` (this project only, git-ignored).

## README.md and CLAUDE.md are different documents

| | `README.md` | `CLAUDE.md` |
|---|---|---|
| Reader | A person, once, when they arrive | An agent, on every task |
| Loaded by Claude Code | Only when asked to read it | At every session start |
| Holds | What the project is, why, how to start, the layout, who maintains it | The rules every task needs, and pointers to the rest |
| Grows when | You add a new part to the project | Claude makes the same mistake twice |

The two do not repeat each other. If a line seems to belong in both, split it. The layout goes to `README.md`, and `CLAUDE.md` points at it. The hard rule goes to `CLAUDE.md`, and `README.md` may mention it in one sentence for the human reader.

## How to write a line an agent can follow

A rule is one act, at one moment. Before you save a line, check that it answers two questions, and decide whether it needs a third:

- When does it fire? A moment in the working loop the agent can recognize: "before staging", "when you create a doc", "when a file passes 500 lines". "Always" and "be careful" are not moments.
- What does the agent do? One concrete act. Someone who disagrees with the rule could still carry it out.
- How does anyone tell? Ask this only where a miss matters. For most rules the act shows in the diff or the transcript, and review is enough.

When to name a check. Anthropic's docs call `CLAUDE.md` "context, not enforced configuration": an agent follows a line most of the time, not every time, and its own "done" is not evidence. Name a check when a miss would be costly or silent (hard to undo, seen by others, a leaked secret, lost data), or when the rule tells the agent to stop, ask, refuse, or do what it would not do on its own. Then pick the cheapest check that fits: a tool that already runs and rarely cries wolf (a linter, a test, a CI step), or one specific question at a named moment ("before you stage, re-read the diff for a home path"), never "check carefully". Keep a gate the agent cannot switch off (CI, a required review) for the rare rule that must hold with no exceptions; a hook on the agent's own machine can be skipped or worked around. Two costs cap the number of checks: a check that fires often and gets ignored teaches everyone to ignore the next one, and an agent optimises for the check it can see, so a check confirms the outcome and never replaces it.

Before: "Keep the docs current."
After: "When you rename a flag, update its `--help` line in the same commit." The diff shows both files; no check is needed.

Before: "Be careful with secrets."
After: "Before you commit, read `git diff --cached` for a key or a token; a pushed secret cannot be taken back." A miss is costly and easy to overlook in review, so the rule names the check.

Anthropic's memory page says the same thing in fewer words: "Use 2-space indentation" beats "Format code properly"; "Run `npm test` before committing" beats "Test your changes".

## When to add a line, and when to cut one

Add a line when one of the cases below happens. The second question of the one test decides where it goes: in `CLAUDE.md`, or in a topic file.

- Claude makes the same mistake a second time;
- a review catches something Claude should have known about this repo;
- you type the same correction you typed last session;
- a new teammate would need the same fact to be productive.

Cut a line when Claude already does the right thing without it.

When Claude keeps ignoring a rule, do not delete the rule. The usual cause is a file that is too long, so shorten the file first. If that one rule still gets skipped, add `IMPORTANT` to that line alone.

Treat the file like code: review it when something goes wrong, cut what is dead, and test that an edit really changes what Claude does.

## Where the files live

Claude Code loads several `CLAUDE.md` files and joins them, broadest scope first:

| Scope | File | Shared with |
|---|---|---|
| Organization | Managed policy file, set by IT | Everyone on the machine |
| You, all projects | `~/.claude/CLAUDE.md` | Only you |
| The project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | The team, through git |
| You, this project | `./CLAUDE.local.md` (add it to `.gitignore`) | Only you |

Three details that change what you write:

- A `CLAUDE.md` in a subdirectory loads only when Claude reads files there. Use it for a subsystem with its own rules.
- `@path/to/file` inside `CLAUDE.md` imports that file at launch. The import organizes text; it does not save context, because the imported file still loads every session. To mention a path without importing it, wrap it in backticks.
- Block-level HTML comments (`<!-- like this -->`) are stripped before the file reaches Claude, so notes to human maintainers cost no tokens. Comments inside code blocks stay.

A repo that already has `AGENTS.md` for other agents does not need a copy: a `CLAUDE.md` with the single line `@AGENTS.md` imports it.

## Example: a small project CLAUDE.md

A fictional Python service at Acme Corp. The file holds what every task needs, and the hard rules the exception keeps. Git, commands, and conventions live in three topic files, and the file points to each one at its moment.

```markdown
# Project instructions — acme-billing

## Language and style
- English in code, comments, commit messages, and docs.
- Short, plain sentences in answers, docs, and commit messages; no filler words.

## Read before you act
- Before you look for where something lives, read the project structure in `README.md`.
- Before you branch, commit, or merge, read `docs/git.md`.
- Before you build, run, or test anything, read `docs/commands.md`.
- Before you write, plan, or review code, read `docs/conventions.md`.

## Never
- Never commit `.env` or anything under `secrets/`; before you commit, read `git diff --cached` for a key or a token. A secret hides easily in a diff, and a pushed one cannot be taken back.
- Never push, and never run a command that pushes for you, such as `gh pr create`; a push skips review. Say which branch is ready; the maintainer pushes.
- Never call the payment provider from a test; a real call moves real money. Use the fake in `tests/fakes/provider.py`.
```

The three "Never" lines fall under the exception, although each belongs to a topic: a secret hides easily in a diff, a push skips review, and a test that calls the real provider moves real money before anyone reads the diff. "Never edit a migration after it is merged" stays in `docs/conventions.md`: the edit shows in the diff, and review stops it before it runs anywhere. The other two lines carry no check of their own, because their checks live outside the file: permission deny rules for `git push` and `gh pr create` in `.claude/settings.json`, and test settings that hold only the provider's sandbox key.

What the topic files hold in this project:

| Topic file | Lines |
|---|---|
| `docs/git.md` | Branch `<type>/PROJ-123-short-name`. Commit title `type [PROJ-123]: what changed, in business terms`. Run `make check` before every commit, and `make test-integration` too when the change touches `src/billing/ledger/`. |
| `docs/commands.md` | `make check` runs lint, types, and the fast tests. `make test-integration` runs the ledger's integration tests and needs a local Postgres (`make db-up`). |
| `docs/conventions.md` | Type hints on every public function; `ruff` and `mypy` are the style guide. New HTTP handlers go in `src/billing/api/handlers/`, one file per resource. Money is `Decimal`, never `float`; a `float` in a money field fails review. Database changes go through `alembic revision --autogenerate`; never edit a migration after it is merged. |

A question about how invoice numbers are built loads none of the three. A docs fix loads `docs/git.md` at the commit, then `docs/commands.md` when it runs `make check`. A ledger bug fix loads all three, each at the step that needs it. The two "run before a commit" lines sit in `docs/git.md`, not in `docs/commands.md`, because their moment is the commit, and that is the file Claude opens before a commit. `docs/commands.md` says what each command does and what it needs.

What is in none of the four files: the folder tree, the list of dependencies, how Alembic works, the release procedure (a skill), the API reference (a link in `README.md`).

## Sources

- Anthropic, "How Claude remembers your project": https://code.claude.com/docs/en/memory (file locations and load order, the 200-line target, "build commands, conventions, project layout", the four "add a line when" triggers, the specificity examples, imports load at launch, `.claude/rules/`, the `/doctor` trim, "context, not enforced configuration", a file named in words is seen "only if it decides to open the file", the auto memory index and its on-demand topic files)
- Anthropic, "Best practices for Claude Code": https://code.claude.com/docs/en/best-practices (the include/exclude table; "only include things that apply broadly"; what is "only relevant sometimes" goes to skills; "would removing this cause Claude to make mistakes?"; one `IMPORTANT` on a single line)
- HumanLayer, "Writing a good CLAUDE.md", 2025-11: https://www.humanlayer.dev/blog/writing-a-good-claude-md (keep it short; progressive disclosure: task-specific files such as `running_tests.md` and `code_conventions.md`, listed in `CLAUDE.md` with a short description, and Claude decides which to read before it starts working; do not auto-generate it)
- agents.md: https://agents.md/ ("README.md files are for humans"; the agent file holds what would clutter a README)
