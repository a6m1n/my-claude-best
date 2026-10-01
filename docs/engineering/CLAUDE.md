# docs/engineering — writing and editing a practice

Each practice here is a folder named by the topic, never a bare file: the way one kind of work
should be done, in any repository. Every folder `ls -d docs/engineering/*/` prints is one. This
file is the contract for writing them, and a folder's `README.md` is its map; the practice docs
are a folder's rules file, or rules files, and its example files. An example is anything a reader
may copy: an `*-example.md` file, or a tree, a diagram, a code snippet or a message inside a rules
file or a `README.md`. A BAD example is one shown as the form to avoid: labelled Bad or Before,
or named by its rule as the wrong form. Every other example is a GOOD example.

## The contract

- **A practice is the source; the code is the consumer.** A doc here says how the work should
  be done, never how this repository does it today. This repository may be behind a practice,
  or plain wrong. That is a gap in the code, never a reason to soften the doc: leave the doc as
  it is. What the code does about the gap, and when, is in `any-language/refactoring/refactoring.md`.
- **Reading a practice is mandatory before working in its area.** This file loads only when a
  file under this folder is read, so the mandate cannot fire from here: the project `CLAUDE.md`
  carries it, one routing line per practice — the moment it fires, the file to read, the check
  — and owns the rule that a new practice folder gets its line in the same change. Copying a
  practice folder into another repository does not carry the mandate; that repository adds the
  line to its own `CLAUDE.md` (`any-language/git/README.md` § "How to adopt", step 2). In this library that
  file is local and not committed; `CLAUDE.local.md` is the committed example of the section.

## Writing or editing a practice

- Take every rule from public practice, never from what the code in this repository does. The
  check: no rule in a practice doc is justified by what this repository's code does today, and
  no sentence in one names this repository, its owner, a decision made in it, or a person who
  works on it. A link to another doc is not a hit.
- Before you create a doc, run `grep -ril "<topic>" docs/`. If a doc on that topic exists,
  extend it; the diff then shows an edited file, not a second file on the same topic. A practice
  is one folder named by the topic, with a `README.md` map, a rules file and one ideal example
  per artifact type; never a bare file, even before the examples exist. A topic whose subjects a
  reader looks up apart, such as testing, has one rules file per subject, and its `README.md`
  says which file to read for which work.
- A rule has one owner: the practice whose topic it is, as each folder's `README.md` says.
  When one practice needs a rule another owns, link that practice's file and section, and never
  write the rule's conditions or its check again. Where two practices disagree, the owner's
  text stands and the other one changes. The check: before you stage, every sentence in the
  diff that uses a rule another practice owns links that practice's file and section, and none
  repeats the rule's conditions or its check.
- Before you write a practice file, or add, rename or remove one of its `##` headings, read
  `any-language/git/git.md` section 9: it says which files open with a navigation block and how the block is
  kept in step. In a file that has one, the diff shows each heading change next to its line.
- When you add a practice, or change a rule in one, write in the commit body how existing code
  responds, using one of the answers `any-language/refactoring/refactoring.md` section 7 lists. In the same
  commit, change every example under `docs/engineering/` that the new or changed rule governs
  and does not yet follow; an example never waits for a change to touch it.
  The check: the commit body names one of the answers, and before you stage,
  each hit of `grep -rn "<key term of the rule>" docs/engineering/` is in the diff, is a BAD
  that shows the old form on purpose, or already shows the new rule. An added practice gets
  one search per rule.
- Write a rule as one act, at one moment. `docs/claude-code/claude-md.md` § "How to write a line
  an agent can follow" is the test, and it holds for a practice doc as much as for an instruction
  file. A `Check:` line is optional: most rules leave their act in the diff, and review is enough.
  Add one where a miss would be costly or easy to overlook in review, and make it one specific
  question at a named moment ("read the title alone") or a tool that already runs and rarely cries
  wolf (`lint-imports` in CI) — never "review carefully", and never a gate people will have to
  bypass. The check: each `Check:` line the diff adds is one question or one command.
- Every name in an example is a placeholder (`Acme Corp`, `Jane Doe`, `PROJ-123`,
  `example.com`) or a well-known name of the same kind standing in for a real client — a
  well-known bank for a bank; it marks the role and claims nothing about that company. A real
  company appears under its own name only as a cited source, as the tool described, or as its
  own public product.
- When you write or change a GOOD example, make it follow every practice here that governs what
  it shows, and say next to it why it is good. Add nothing only to show another practice. Code
  it leaves out is cut with `...`, or named as left out in the sentence that introduces it;
  never shown as if it were complete. The check: before you stage, read each GOOD example the
  diff adds or changes once per practice folder, with that folder's rules files open, and write
  one line per folder in the closing summary: "follows" or "governs nothing here"; a GOOD with
  no sentence that says why it is good fails.
- When you write or change a BAD example, or the GOOD that fixes one, make the BAD show one
  problem, named in its label or by the rule that calls it wrong; the reason sits right after
  it, and in everything else it follows every practice here. Its GOOD is the same example with
  that problem fixed, and says which problem it fixes and why the fix is better. The check:
  before you stage, set the two side by side; every difference is the named problem or follows
  from its fix, and the GOOD's text names that problem, and the BAD's reason sits in the lines
  right after it.
- Before you stage, run every check the bullets above name for what your diff touches. Then
  re-read the diff for two things: a rule justified by this repository's code, and a real name.
  A failed check, or either of the two, means the doc is not ready.

<!--
FUTURE: rule levels (Must / Should) for every practice
Trigger: a second practice needs rules that help on some tasks and hurt on others, or the library
decides to give every rule a level.
Fix location: this section.
Approach: one bullet: every rule opens with its level, Must (always, when its condition holds) or
Should (keep it when a test shows it helps). Existing practices adopt it when a change touches
them (any-language/refactoring/refactoring.md section 7, "New and touched code").
any-language/prompt-engineering/prompt-engineering.md section 1 is the first practice written this way.
any-language/evals/evals.md section 1 adds a third level, Optional: add it when the need the rule names appears.
-->
