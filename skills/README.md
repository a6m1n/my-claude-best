# Skills

Claude Code skills to read and copy.

**Navigation**

- [What is here](#what-is-here)
- [Keep a copied practice in step with its source](#keep-a-copied-practice-in-step-with-its-source)

Nothing here runs in this repository, because Claude Code does not load skills from this
folder. To use a skill, copy it into `.claude/skills/` of your own repository, or into
`~/.claude/skills/` when its README says so. Installing a skill is your decision. The `pr`
skill goes into `~/.claude/skills/` instead, and [its README](pr/README.md#install) says why.

## What is here

- [sync-best-practice/SKILL.md](sync-best-practice/SKILL.md): copies a practice in from a
  source repository, reports whether the copy is behind its source or has changes with no
  reason, and merges new source commits into it. Read it when you copy a practice or want its
  updates.
- [update-best-practice/SKILL.md](update-best-practice/SKILL.md): writes down why your copy of
  a practice differs from its source. Read it when you change a copied practice.

The two work as a pair and share three files in `sync-best-practice/`:

- [record-format.md](sync-best-practice/record-format.md): the format of the record. Read it
  when you read or change a record by hand.
- [shared-steps.md](sync-best-practice/shared-steps.md): the steps both skills run, and the
  commands that ask for your permission. Read it when you want to know which commands of a
  run ask for your permission.
- [design.md](sync-best-practice/design.md): the options turned down, with their reasons. Read it
  before you change either skill.

These skills stand alone:

- [meta-thinking/README.md](meta-thinking/README.md): before a large task starts, one
  independent agent reads the task and the repository, asks you at most three questions and
  proposes one route, step by step. Read the README for the problem it solves and when to use
  it. It also needs its agent file copied into an agents folder; the README's Install says how.
- [pr/SKILL.md](pr/SKILL.md): writes the pull request for the current branch from one fixed
  template, shows you the draft, and opens or updates the pull request after your yes. Read
  [pr/README.md](pr/README.md) first: it says how to install the skill, what to fill in, and
  where it departs from git.md.
- [create-jira-ticket/README.md](create-jira-ticket/README.md): turns short notes into one Jira
  story, bug or task, shows every field before it writes, and creates the issue after your yes.
  Read the README for how to connect Jira; the skill needs the Atlassian MCP server.
- [commit/SKILL.md](commit/SKILL.md): writes the commit message for your changes, shows you the
  draft, and stages and commits the files it names after your yes. Its message format differs
  from git.md. Read [commit/README.md](commit/README.md) first: it says how to install the
  skill, what to fill in, and where the format differs.

Each skill has an `output_example.md` that shows what it prints, on invented values.

The `pr` skill came before git.md and is published as it is:
[its README](pr/README.md#where-it-departs-from-gitmd) lists where it departs from git.md.

## Keep a copied practice in step with its source

You copy a practice, then change it for your repository. Later the source gets better, and you
want those changes too. A plain copy loses one or the other: you overwrite your changes, or you
never take the new ones. The two skills keep both. For each copied practice they keep one
record, `docs/adopted-practices/<name>.md`, in your repository. The record holds the source
commit your copy matches, and one decision per change you made: what the source says, what you
do instead, and why.

To install them and adopt your first practice, follow
[Keep your changes when the source changes](../README.md#keep-your-changes-when-the-source-changes)
in the main README. They need git 2.39 or newer, and work in any git repository.

| You run | What it does |
| --- | --- |
| `/sync-best-practice adopt <path> source=<address>` | Clones the source into a temp folder, copies the practice at `<path>` into the same path here, and writes its record. If a copy is already at `<path>`, adopt keeps it: it finds the source commits closest to the copy, shows the best three, and asks you which one is the base. Commit such a copy before you run adopt. It also offers a line for your `CLAUDE.md` or `AGENTS.md` that tells Claude to record each later change. That line does not replace the practice's own trigger line, which the practice's `README.md` gives. |
| `/update-best-practice` | Run after you change a copy and before you commit. It asks why, and writes the answer into the record as a decision. When Claude edits a copy, it can run the skill by itself. When you edit a copy, run it yourself. |
| `/sync-best-practice status [<name>]` | Says whether the source has new commits for the practice, and whether the copy has a change that no decision explains. Changes no file in your repository. |
| `/sync-best-practice sync <name>` | Shows you the new source text, merges it on your yes, keeps every change a decision explains, and asks you about each conflict. |
| `/update-best-practice backfill <name>` | For a copy you made by hand and then changed: finds the changes with no decision and asks for their reasons. Run it after `adopt` on that copy. |

`<address>` is the source repository's `https://`, `ssh://` or `git@` address, such as the one
the green Code button copies. An `https://` address with a user name or token in it is refused,
because the record that stores the address is committed.
`<name>` is the last part of the practice's path, such as `git` for
`docs/engineering/any-language/git`.

The skills never commit, push or switch branches; you make the commits. Commit a new copy
together with its record, before you change the copy. After that, commit each change together
with the decision that explains it, and a sync together with its record.

The skills read the source only through a fresh clone in a temp folder. They
grant the clone into the temp folder and a few other commands in their `allowed-tools`, so in
the turn a skill starts, those run with no prompt. Claude Code runs plain git reads such as
`git diff` and `git log` with no prompt in any case. Every other command follows your own
permission settings. With the default settings, Claude Code asks before each command that
copies, moves or deletes a file, so a run asks several times. In acceptEdits or auto mode many
of these prompts do not appear, and a sync still shows you the new source text and asks before
it merges. The top of [shared-steps.md](sync-best-practice/shared-steps.md) lists the commands
that prompt. `sync-best-practice` runs only when you call it, because adopt and sync change
your copy.
