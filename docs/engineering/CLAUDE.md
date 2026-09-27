# docs/engineering — writing and editing a practice

Each practice here is a folder named by the topic, never a bare file: the way one kind of work
should be done, in any repository. Every folder `ls -d docs/engineering/*/` prints is one. This
file is the contract for writing them, and a folder's `README.md` is its map; the practice docs
are a folder's rules file and its example files.

## The contract

- **A practice is the source; the code is the consumer.** A doc here says how the work should
  be done, never how this repository does it today. This repository may be behind a practice,
  or plain wrong. That is a gap in the code, never a reason to soften the doc: leave the doc as
  it is. What the code does about the gap, and when, is in `refactoring/refactoring.md`.
- **Reading a practice is mandatory before working in its area.** This file loads only when a
  file under this folder is read, so the mandate cannot fire from here: the project `CLAUDE.md`
  carries it, one routing line per practice — the moment it fires, the file to read, the check
  — and owns the rule that a new practice folder gets its line in the same change. Copying a
  practice folder into another repository does not carry the mandate; that repository adds the
  line to its own `CLAUDE.md` (`git/README.md` § "How to adopt", step 2). In this library that
  file is local and not committed; `CLAUDE.local.md` is the committed example of the section.

## Writing or editing a practice

- Take every rule from public practice, never from what the code in this repository does. The
  check: no rule in a practice doc is justified by what this repository's code does today, and
  no sentence in one names this repository, its owner, a decision made in it, or a person who
  works on it. A link to another doc is not a hit.
- Before you create a doc, run `grep -ril "<topic>" docs/`. If a doc on that topic exists,
  extend it; the diff then shows an edited file, not a second file on the same topic. A practice
  is one folder named by the topic, with a `README.md` map, a rules file and one ideal example
  per artifact type; never a bare file, even before the examples exist.
- When you change a rule in a practice, write in the commit body how existing code responds,
  using one of the answers `refactoring/refactoring.md` section 7 lists. The check: the commit
  body names one of them.
- Write a rule as one act, at one moment, with one way to tell that it happened.
  `docs/claude-code/claude-md.md` § "How to write a line an agent can follow" is the test, and
  it holds for a practice doc as much as for an instruction file.
- Every name in an example is a placeholder (`Acme Corp`, `Jane Doe`, `PROJ-123`,
  `example.com`) or a well-known name of the same kind standing in for a real client — a
  well-known bank for a bank; it marks the role and claims nothing about that company. A real
  company appears under its own name only as a cited source, as the tool described, or as its
  own public product.
- Before you stage, re-read the diff for two things: a rule justified by this repository's
  code, and a real name. Either one means the doc is not ready.
