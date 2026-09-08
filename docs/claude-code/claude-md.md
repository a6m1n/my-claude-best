# CLAUDE.md: what to put in it, and what to keep out

Claude Code reads `CLAUDE.md` at the start of every session, and reads the project-root file again after every `/compact`. Every line in it sits in the context window during every task, whether the task needs it or not. That is the design constraint: the file is a rule sheet the agent always has in front of it, not a project description.

This doc says what earns a place in `CLAUDE.md`, what goes somewhere else, and how to write a line so an agent can follow it.

## The one test for every line

Ask: "Would removing this line make Claude do something wrong on an ordinary change?" If the answer is no, the line does not belong in `CLAUDE.md`. Anthropic's own guidance gives the same test and the reason behind it: a bloated file makes Claude ignore the rules that matter.

The official target is under 200 lines per file. Shorter works better.

## What goes in

Things Claude must know on every change and cannot find out by reading the code:

- The language of code, comments, commit messages, and docs. "English everywhere" is one line; without it an agent answers in the language of the chat.
- Style that differs from the default. Not "write clean code"; Claude does that anyway. Rules like "B2-level English, no filler words" or "no default exports" are worth a line because Claude would not guess them.
- Commands Claude cannot guess, and when to run them: `make check` before a commit, `uv run pytest -x tests/ledger` for one module.
- House rules for the repo: branch names, the commit message format, what never happens (pushing to the remote, editing generated files).
- Where new things go, one line per kind: "working files go under `docs/artifacts/<date>/`", "API handlers live in `src/api/handlers/`". Each line says where a new kind of file goes; it does not describe the tree.
- Hard rules with a reason. "Never commit `.env` files; secrets do not go in git." "No customer names in test data; the repo is public." A hard rule gets one `IMPORTANT` at most. If every line shouts, none stands out.
- Behavior that is not obvious from the code: a required environment variable, a test suite that needs a local database.
- Pointers to detail that loads on demand. "Before any git operation, read `docs/git.md`." The detail stays out of context until the moment it is needed.

## What stays out

- The layout of the repo. What `ls` shows, `CLAUDE.md` should not repeat. A folder list or a "what lives where" section belongs in `README.md`, where a person reads it once. The rule about where new files go (above) stays. The tree itself is what Claude Code's own `/doctor` command proposes to cut from a checked-in `CLAUDE.md`, along with dependency lists and architecture overviews. A one-line pointer ("Layout: see `README.md`") is enough.
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
| Holds | What the project is, why, how to start, the layout, who maintains it | The rules that apply to every change |
| Grows when | You add a new part to the project | Claude makes the same mistake twice |

The two do not repeat each other. If a line seems to belong in both, split it. The layout goes to `README.md`, and `CLAUDE.md` points at it. The hard rule goes to `CLAUDE.md`, and `README.md` may mention it in one sentence for the human reader.

## How to write a line an agent can follow

A rule is one act, at one moment, with one way to tell that it happened. Before you save a line, check that it answers three questions:

- When does it fire? A moment in the working loop the agent can recognize: "before staging", "when you create a doc", "when a file passes 500 lines". "Always" and "be careful" are not moments.
- What does the agent do? One concrete act. Someone who disagrees with the rule could still carry it out.
- How does anyone tell? The act leaves a trace (a diff, a command in the transcript), or the rule names a check ("re-read the diff before you stage"; "`/context` shows the file loaded").

Before: "Keep the docs current."
After: "When you rename a flag, update its `--help` line in the same commit; the diff shows both files or it did not happen."

Anthropic's page says the same thing in fewer words: "Use 2-space indentation" beats "Format code properly"; "Run `npm test` before committing" beats "Test your changes".

## When to add a line, and when to cut one

Add a line when:

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

A fictional Python service at Acme Corp. About thirty lines, and nothing in it that Claude could find by itself.

```markdown
# Project instructions — acme-billing

Python 3.12 service that issues invoices. Layout: see `README.md`.

## Language and style
- English in code, comments, commit messages, and docs.
- Type hints on every public function. `ruff` and `mypy` are the style guide; do not restate their rules here.

## Commands
- `make check` runs lint, types, and the fast tests. Run it before every commit.
- `make test-integration` needs a local Postgres (`make db-up`). Run it only when you touch `src/billing/ledger/`.

## Conventions
- New HTTP handlers go in `src/billing/api/handlers/`, one file per resource.
- Money is `Decimal`, never `float`. A `float` in a money field fails review.
- Database changes go through `alembic revision --autogenerate`. Never edit a migration after it is merged.

## Git
- Branch `<type>/PROJ-123-short-name`; commit title `type [PROJ-123]: what changed, in business terms`.
- Never push. Say which branch is ready; the maintainer pushes.
- Before any git operation, read `docs/git.md`.

## Never
- Never commit `.env` or anything under `secrets/`.
- Never call the payment provider from a test. Use the fake in `tests/fakes/provider.py`.
```

What is not in it: the folder tree, the list of dependencies, how Alembic works, the release procedure (a skill), the API reference (a link in `README.md`).

## Sources

- Anthropic, "How Claude remembers your project": https://code.claude.com/docs/en/memory (file locations and load order, the 200-line target, the four "add a line when" triggers, imports, `.claude/rules/`, the `/doctor` trim, "context, not enforced configuration")
- Anthropic, "Best practices for Claude Code": https://code.claude.com/docs/en/best-practices (the include/exclude table; "would removing this cause Claude to make mistakes?"; the specificity examples; one `IMPORTANT` on a single line)
- HumanLayer, "Writing a good CLAUDE.md", 2025-11: https://www.humanlayer.dev/blog/writing-a-good-claude-md (keep it short, link detail on demand, do not auto-generate it)
- agents.md: https://agents.md/ ("README.md files are for humans"; the agent file holds what would clutter a README)
