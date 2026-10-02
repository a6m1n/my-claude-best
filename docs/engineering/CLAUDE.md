# docs/engineering — writing and editing a practice

Each practice here is a folder named by the topic, never a bare file: the way one kind of work
should be done, in any repository. It sits in a group folder: `any-language/`, or the folder of
the one language its rules are for, such as `python/`. Every folder `ls -d docs/engineering/*/*/`
prints is a practice. This file is the contract for writing them, and a practice folder's
`README.md` is its map; the practice docs are a folder's rules file, or rules files, and its
example files. An example is anything a reader may copy: an `*-example.md` file, or a tree, a
diagram, a code snippet or a message inside a rules file or a `README.md`. A BAD example is one
shown as the form to avoid: labelled Bad or Before, or named by its rule as the wrong form. Every
other example is a GOOD example.

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
- Before you create a practice folder, pick its group by what its rules cover, not by its
  examples. A practice goes under `any-language/` when every rule in it holds in any language,
  apart from a part it labels as one language's case (file-structure's "Python case",
  refactoring's section 10); Python examples and tool names do not change that. Every other
  practice goes under the folder of the language it is written for, such as `python/`, even when
  some of its rules would hold in any language (testing's `what-to-test.md`); those rules move
  out the way the next sentence says. Before a language adds a topic another language's folder
  already holds, move the rules that hold in any language into an `any-language/` practice, in a
  commit of its own whose body names an answer from `any-language/refactoring/refactoring.md`
  section 7; that practice then links each language's practice on the topic for that language's
  case. A language or framework with no folder yet gets one, named by it in lower case
  (`react/`). The name `any-language/` states the test a practice passes to sit there, which a
  name like `general/`, `common/` or `shared/` would not (`core/` is file-structure's word for
  shared application code). A group folder holds practice folders and nothing else. The check:
  before you stage, `find docs/engineering -maxdepth 2 -name '*.md'` prints only
  `docs/engineering/CLAUDE.md`.
- When you add or remove a practice, change the practice list in the root `README.md` in the same
  commit. When you add a group, also change the README's sentence on the groups, its tree, its
  examples badge and every line that says the examples are only in Python. The check: before you
  stage, every folder `ls -d docs/engineering/*/*/` prints has a link in the README list, and
  `grep -n -i -E 'in Python|other than Python' README.md` shows nothing the change made false.
- A rule has one owner: the practice whose topic it is, as each practice folder's `README.md` says.
  When one practice needs a rule another owns, link that practice's file and section, and never
  write the rule's conditions or its check again. Where two practices disagree, the owner's
  text stands and the other one changes. The check: before you stage, every sentence in the
  diff that uses a rule another practice owns links that practice's file and section, and none
  repeats the rule's conditions or its check.
- Before you write a practice file, or add, rename or remove one of its `##` headings, read
  `any-language/git/git.md` section 9: it says which files open with a navigation block and how the block is
  kept in step. In a file that has one, the diff shows each heading change next to its line. When
  you renumber or move a `##` section of a rules file, run
  `git grep -n -E '<file>\.md\)? (section|§) ?<old n>([^0-9]|$)' docs/` and update each hit in the
  same commit, because a comment that cites the old number now points a reader at the wrong rule.
- When you add a practice, or change a rule in one, write in the commit body how existing code
  responds, using one of the answers `any-language/refactoring/refactoring.md` section 7 lists. In the same
  commit, change every example under `docs/engineering/` that the new or changed rule governs
  and does not yet follow; an example never waits for a change to touch it.
  The check: the commit body names one of the answers, and before you stage,
  each hit of `grep -rn "<key term of the rule>" docs/engineering/`, and of a second search for
  the code the rule is about (`os.environ` for a settings rule), is in the diff, is a BAD that
  shows the old form on purpose, or already shows the new rule. An added practice gets one
  search per rule.
- Write a rule as one act, at one moment, then give its reason in one clause: the goal it serves
  or the failure it prevents. The reason lets a reader judge an exception and see when the rule
  needs another look; a rule whose reason you cannot state is a candidate to cut. Google's style
  guides aim to give each ruling its pros, cons and decision
  ([Software Engineering at Google](https://abseil.io/resources/swe-book/html/ch08.html), ch. 8),
  so that "it should be clearer to everyone when a rule may be waived"
  ([Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html), Goals). A reason
  never replaces a check. `docs/claude-code/claude-md.md` § "How to write a line an agent can
  follow" is the test for the moment, the act and the check. A practice doc gives every rule its
  reason, which that section asks of an instruction file only where the act could be misapplied: a
  practice is read when its work starts, and an instruction file is in every turn's context. A
  `Check:` line is optional: most rules leave their act in the diff, and review is enough.
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
  it shows, and say next to it why it is good. Why: readers, people and agents, copy the example
  and not the rules around it, so a GOOD that breaks a practice spreads that break to every copy
  and to every author who cites it as precedent (documentation teams hold their samples to the
  same bar:
  [MDN](https://developer.mozilla.org/en-US/docs/MDN/Writing_guidelines/Writing_style_guide/Code_style_guide)
  asks that examples "follow generally accepted best practices", and
  [Microsoft's .NET docs](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
  "show code you should write today"). A practice governs an example when its routing line in the
  project `CLAUDE.md` would fire for that code in an application. Add nothing only to show another
  practice. Code it leaves out is cut with `...`, or named as left out in the sentence that
  introduces it; never shown as if it were complete. The check: when you write the commit message,
  open the sections of each practice that governs each GOOD the diff adds or changes, and put a
  `Practices: <rules file> §n, …; every other practice governs nothing here` line in it as a git
  trailer (`Key: value`): last, with the other trailers, above `Co-Authored-By:` where that line
  exists, a long one folded onto indented lines, such as
  `Practices: testing/layout.md §3, logging/logging.md §8; every other practice governs nothing here`.
  When no practice governs the examples, the line is `Practices: none govern these examples`.
  Why a trailer: `git log` keeps it with the change, and this library has no CI to run a stricter
  check.
  A GOOD with no sentence that says why it is good fails.
- Before you stage, a GOOD that breaks a rule of a practice that governs it is not ready,
  whatever severity a review gives the break, unless the example declares the departure where it
  happens: it names the rule, says why it departs and what that costs, so a reader who copies it
  sees the trade and can choose (the
  [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) states a rule's
  goal so that "it should be clearer to everyone when a rule may be waived"). Fix every other
  break before you stage, and never park it in a backlog or let a review record it as a design
  choice, because readers copy it in the meantime. If the rule is the thing that is wrong, change
  the rule in the practice that owns it. The evidence that an example follows a practice is a
  clause in that practice's rules file, never another example.
- In an example, each line that [readability.md](any-language/readability/readability.md)
  section 4 says carries its reason (code that others copy) gets a short comment that says why,
  and names the rule's section where a practice rule owns the reason, such as
  `# One trace per label, so a wrong verdict can be opened (evals.md section 9).` The longer
  reason goes in the sentence after the block that says why the example is good. The check:
  before you stage, ask of each line the diff adds to an example whether a reader who copies it
  would likely undo it; if so, it has its reason at the line.
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
python/evals/evals.md section 1 adds a third level, Optional: add it when the need the rule names appears.
-->
