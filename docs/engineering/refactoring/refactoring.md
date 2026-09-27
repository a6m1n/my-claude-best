# Refactoring rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. New, touched and untouched code](#2-new-touched-and-untouched-code)
- [3. How to change old code safely](#3-how-to-change-old-code-safely)
- [4. Sweep the repository, or move step by step](#4-sweep-the-repository-or-move-step-by-step)
- [5. When a practice replaces one way with another: migrations](#5-when-a-practice-replaces-one-way-with-another-migrations)
- [6. Rules about correctness and security](#6-rules-about-correctness-and-security)
- [7. When a practice itself changes](#7-when-a-practice-itself-changes)
- [8. Follow-ups: what you see but do not fix](#8-follow-ups-what-you-see-but-do-not-fix)
- [9. Rules for AI agents](#9-rules-for-ai-agents)
- [10. Python](#10-python)
- [11. Where these rules come from](#11-where-these-rules-come-from)

## 1. Purpose and the one rule

This file is for everyone who changes code that already exists: people and AI agents alike.
Read it before a change edits code that already exists (a feature, a fix, a move to a practice, a
restructure), or turns on a new rule in a repository that already has code.

The practices in `docs/engineering/` say how code should be written. They do not describe the
code that is already there, and they change over time. So most of a repository is always older
than some rule it now follows. This file says what to do with that gap: which code moves to a
practice, when, and how. It is written against two failures. One is rewriting the repository
every time a rule changes. The other is never moving old code at all, until the repository holds
several ways of doing the same thing and nobody can tell which one is current.

Refactoring is a change to the structure of code that keeps its behavior; the definition is
Martin Fowler's. Moving old code to a practice is refactoring when the practice is about
structure: names, types, layout, where a check lives. When the practice is about correctness,
moving old code to it changes behavior, and section 6 applies.

The one rule: **new code follows the current practice; old code moves to it when a change
already touches it, with tests, in its own commit.** Two kinds of practice change break this
default. A change that replaces one way of doing a job with another is a migration, and a
migration has an owner and an end (section 5). A rule about correctness or security reaches all
code by a date (section 6).

Why this default:

- Rewriting everything for each rule costs review time, merge conflicts and new bugs. In one
  long study about 15% of refactorings were followed by a bug-inducing change (Bavota et al.,
  2012). Vulnerabilities cluster in new and recently changed code; code that has run for years
  without change holds the fewest (Google's Android security team, 2024).
- Never moving old code fails the other way. People copy the code they see: "Engineers tend to
  use existing code as examples when writing new code" (*Software Engineering at Google*,
  ch. 22), and AI agents do the same. A repository with an old and a new way side by side
  teaches both.
- Most refactoring already happens inside ordinary changes, not in cleanup projects: at
  Microsoft only 1.27% of the Windows 7 changes went through the dedicated refactoring branches
  (Kim, Zimmermann and Nagappan, 2014). The rules here make that habit explicit and safe.

Google's Go style guide gives the default in one sentence: its documents "may change over time,
and that is no reason to cause extra churn in existing codebases". New code uses the latest
practice, and nearby issues are fixed over time.

## 2. New, touched and untouched code

When you plan a change, sort the code it affects into three kinds. Each kind has its own rule.

| Code | What you do |
|---|---|
| **New**: a file, function, class or lines you add | Follow the current practice fully. Old code nearby is not a template. |
| **Touched**: a function your change already edits | Move it to the practice in this change, if tests cover it (section 3). |
| **Untouched**: everything else | Leave it as it is, even where it breaks the practice. |

- **Untouched old code is not a defect to fix now.** PEP 8 lists it as a valid reason to depart
  from a guideline: the code "predates the introduction of the guideline and there is no other
  reason to be modifying that code". Kent Beck's name for the choice is "tidy never": code you
  will not change again stays as it is.
- **One function does not read in two styles.** If your new lines would leave a function half in
  the old practice and half in the new one, move that function to the practice first, in its own
  commit before your change. Google's Python style guide asks for the same outcome: code you add
  should not look drastically different from the code around it. The way to get there is to bring
  the function up, not to write the new lines in the old style.
- **Do not spread an old style.** "Match the code around it" stops being a reason once your
  change would copy a deviation into more files or more public API, or make it worse (Google's Go
  style guide). Then the new code follows the practice, and the deviation stays where it was.
- **A gap outside the touched code is a follow-up, not an edit.** A whole module that breaks a
  practice is not part of your change. Record it (section 8).

Check: read the diff. Each hunk is new code that follows the practice, or old code the change
itself had to edit. A hunk that edits old code only to meet a practice, in a function the change
does not otherwise edit, belongs in its own change or in a follow-up.

## 3. How to change old code safely

This section fires when your change has to edit old code: to add behavior to it, or to move it
to a practice. The order is fixed: pin what the code does, change its structure, then change its
behavior.

1. **Tests first.** Old code without tests gets characterization tests before its structure
   changes. A characterization test pins what the code does today, right or wrong, so a
   refactoring that changes it fails a test (Michael Feathers, *Working Effectively with Legacy
   Code*). These tests land in their own `test` commit.
2. **When a test costs too much, do not refactor the old code.** Put the new behavior in a new
   function or class, written to the practice, and call it from one place in the old code
   (sprout). Or rename the old function and wrap it in a new one that adds the behavior (wrap).
   The old code stays as it was until it can be tested. Both techniques are Feathers'.
3. **Make the change easy, then make the easy change** (Kent Beck). The refactoring that prepares
   the code for your change is its own commit, before the change. A commit changes structure or
   behavior, never both; Fowler calls these the two hats.
4. **A `refactor` commit keeps behavior.** The tests that existed before it pass after it, and no
   expected value in them changes. A rename may change the names a test calls. If an expected
   value had to change, the commit changed behavior, and it is not a refactoring.
5. **Take small steps.** Run the tests after each one. Moving methods between a class and its
   parent, or extracting a subclass, breaks code more often than other refactorings (Bavota et
   al.). Keep such a step in a commit of its own, so one revert undoes it.
6. **Stop when the refactoring keeps growing.** If each fix uncovers another, revert the
   refactoring, write down what blocked you, and do that first as its own change. Then try again.
   This is the Mikado Method (Ola Ellnestam and Daniel Brolund). Never land a half-done
   refactoring inside a feature.
7. **Put each part where it can be reviewed and reverted.** A small cleanup in the lines you
   change, such as a local rename or an extracted variable, may go in the same pull request, as
   its own commit. A larger refactoring is its own pull request, merged before the change. A mixed
   pull request cannot be reverted in parts. Review quality also falls as the diff grows
   ([git.md](../git/git.md) section 4). Google's code review guide draws the same line:
   refactorings go in a separate change, and a small cleanup "such as fixing a local variable
   name" may stay inside.

Check: every commit in the pull request is one of three kinds: `test` (characterization tests),
`refactor` (the tests pass, with the same expected values), or the behavior change. `git show`
on a `refactor` commit shows no changed expected value in any test.

## 4. Sweep the repository, or move step by step

This section fires when a repository turns on a practice or a rule, or a practice changes, and
old code breaks it in many places.

**Sweep**, changing all the code in one go, only when all four hold:

1. A tool makes every edit: a formatter, a linter's safe automatic fix, a codemod.
2. A command proves every edit: the tests, the type checker and the linter pass on the result.
3. The edit lands as one commit with nothing else in it, made by the person who changed the rule.
4. The check that enforces the rule is turned on in the same pull request, so the old form
   cannot come back. Google turns on a new compiler check only after an automatic fix has cleaned
   every instance (*Software Engineering at Google*, ch. 20).

After a sweep, add the commit's full hash to `.git-blame-ignore-revs` at the repository root, so
`git blame` skips it. GitHub reads the file. Locally, `git config blame.ignoreRevsFile
.git-blame-ignore-revs` turns it on once per clone. Large automated changes and large deletions
are the accepted exceptions to "keep changes small" in Google's code review data
(Sadowski et al., 2018).

**Move step by step** in every other case: whenever a fix needs a person's judgment at each
place, such as types, names, structure, or where a check belongs. Then:

- turn the rule on for new code now;
- mark each old violation where it sits, with the tool's own suppression comment or setting
  (`# type: ignore[code]`, `# noqa: CODE`, a per-module override), not in a separate baseline
  file that nobody reads;
- make the marks shrink: remove a mark when a change touches the function that carries it
  (section 2), and a per-module override when the module passes the check without it; make the
  tool fail on a mark that no longer suppresses anything;
- count what is left with one command, for example `grep -rn "# noqa: CODE" src/ | wc -l`.
  Write the command and its number where the team tracks the rule. Before you stage a change in
  that area, run the command. The number only goes down.

When no tool checks the rule, there are no marks. Review checks new code against the practice's
own check, and a search for the old form counts the old uses, in the same way.

Two more cases:

- **Change everything at once when step by step would make every developer work in two
  languages at once.** Stripe moved its code from Flow to TypeScript in one change for that
  reason. This is a migration (section 5) done in one step, and it still needs condition 2: a
  command that proves the result. Any other replacement of one way with another, a new library
  included, is a migration done step by step, as section 5 says.
- **Never sweep by hand.** A manual reformat or rename across the repository, with no other work
  behind it, costs review time and blame history and gives a reader nothing. The LLVM coding
  standards reject "large-scale reformatting of existing code", and the Linux networking
  maintainers reject standalone style clean-ups for the same reason.

An AI agent is not a tool under condition 1: edits it writes itself need judgment. When an agent
runs a tool that meets the four conditions, the result is a sweep like any other. A repository-wide
change whose edits the agent writes itself is a migration (section 5), done in batches. Each batch
is its own pull request that meets condition 2 and is reviewed by a person. Agent-made migrations
worked at Google and at Airbnb (2025) behind automatic checks on every change and review by
people. In independent studies without that setup, most agent-made migrations failed their
checks. Agents make such a migration much cheaper to finish than it used to be (Will Larson,
2026), which is a reason to choose a migration with an end, never a reason to skip the checks.

Check: a sweep commit holds only the tool's edits, its hash is in `.git-blame-ignore-revs`, and
the pull request that carries it also turns the check on. For a step-by-step rule, the counting
command recorded with it, such as `grep -rn "# noqa: CODE" src/ | wc -l`, prints the recorded
number or a lower one.

## 5. When a practice replaces one way with another: migrations

Most practice changes improve code: a clearer name, a type instead of a `dict`, a smaller
function. Old code in the old form still works, and moving it when a change touches it is
enough. A different kind of change replaces one way of doing a job with another: a new HTTP
client, a new test library, a new error type, a new pattern for a shared task. Then two ways live
side by side, and that costs something every day: two sets of knowledge, two sets of bugs, and
new code that copies the wrong one. Moving old code only when a change touches it does not
finish this. Google found that deprecation with no deadline "rarely leads to teams actively
migrating away" (*Software Engineering at Google*, ch. 15), and Mike Hadlow named the result the
lava layer: generation after generation of half-finished moves.

So a practice change of this kind starts a migration, and a migration has an end:

1. **Stop the bleeding.** From the day the practice changes, new code uses only the new way
   (Will Larson, "Migrations").
2. **Count the old uses.** Choose one search that finds every use of the old way, for example
   `grep -rn "import requests" src/ | wc -l`. Write the command and its result in the
   migration's tracking issue. Before you stage a change in that area, run the command. The
   number may only go down: when it drops, write the new number; a change that raises it is not
   merged unless its commit body says why. This is a ratchet (qntm, 2021); Notion and Imbue keep
   the same kind of count in a checked-in file that may only go down. A plain search can match
   comments and strings, so read what it matches once and narrow it before you trust the number.
3. **Name an owner and an end date.** The person who changed the practice owns the migration.
   Google calls this the churn rule: whoever changes the ground moves the people standing on it.
   The owner moves the easy majority with a tool where one exists, then finishes the rest by
   hand.
4. **Finish, or go back to one way.** A migration ends when the count is zero and the old way is
   gone: its dependency, any wrapper written around it, and the practice text that allowed it. If
   it cannot finish, roll it back. Never start a third way while the first one is still in the
   code (Jimmy Bogard's "rule of 2").

The shape is expand, migrate, contract: add the new way next to the old one, move every caller,
then remove the old one. The last step is part of the job. Danilo Sato's warning about it, on
martinfowler.com: "If the contract phase is not executed you might end up in a worse state than
you started".

Check: the tracking issue shows the owner, the end date, the search command and its result over
time. At the end the result is zero, and the old dependency is gone from the lockfile.

## 6. Rules about correctness and security

A rule that exists because the old way is wrong, such as a security hole, lost data or a race,
does not wait for a change to touch the code. Old code is fixed too, by a date, with the same
care as any other change: tests first, one commit per kind of fix. Google shows both halves.
Writing only new code in memory-safe languages cut Android's memory-safety bugs sharply, because
bugs cluster in new code. For its large C++ codebase that was too slow, so Google hardened all
existing C++ at once and found more than 1,000 bugs (2024).

Check: the change that adds the rule, or its tracking issue, names the date. After that date the
search for the unsafe form returns nothing.

## 7. When a practice itself changes

A practice is edited like code, and an edit to a practice is not a reason to rewrite the
repository. The person who edits a rule decides, at that moment, how existing code responds, and
writes it in the body of the commit that changes the practice. There are three answers:

- **New and touched code.** The change improves code; old code moves when a change touches it
  (section 2). This is the default.
- **Migration.** The change replaces one way with another (section 5). The commit names the
  owner, the end date and the search that counts old uses.
- **All code by a date.** The change fixes something wrong (section 6).

Google's Go style guide splits its own documents the same way: "canonical" ones are "a standard
that all code (old and new) should follow", and the others guide new code and review.

Check: the commit that changes a practice names one of the three answers in its body.

## 8. Follow-ups: what you see but do not fix

Old code outside your change that breaks a practice is not fixed in passing (section 2). Record
it where someone will act on it: an issue with an owner, or the tracking issue of a migration. A
sentence in a commit body or a chat summary says that you recorded it; it is not the record.
Findings filed against old code in bulk are mostly never fixed, while the same kind of finding
shown on the lines a person is changing mostly is (Sadowski et al., 2018, on static analysis at
Google; O'Hearn, 2019, on Infer at Facebook).

Check: each follow-up a pull request mentions links an issue, or says why it needs none.

## 9. Rules for AI agents

Everything above holds for an agent as written. Agents fail in two opposite directions, and
studies from 2025 and 2026 measure both. They edit beyond the task: going past the request was
the most common kind of overreach in a study of 20,574 real agent sessions. And when they only
patch and never clean, the structure of the code gets worse run after run. Two more findings
shape the rules below: agents follow a rule that adds a step far more often than a rule that only
says what not to do, and a concrete target curbs overreach far better than a warning about
consequences. So the rules for an agent are steps, each with a named target:

1. **Before you edit, list the functions your change will edit.** That list is the touched code
   (section 2), and the only old code you move to a practice.
2. **Check new code against the practice, not against the code next to it.** When the two
   differ, new code follows the practice.
3. **Before you finish, review your own diff.** Move each function on the list to the practice
   in a separate `refactor` commit, where tests cover it (section 3). Then check that no hunk
   edits a function outside the list.
4. **Report what you left.** Every gap you noticed outside the list goes into your report as a
   follow-up (section 8), with the file and the practice it breaks.
5. **Run a repository-wide change only as section 4 says:** a sweep when a tool makes every edit;
   otherwise a migration in batches, each batch its own pull request that a command proves and a
   person reviews. Each one lands the way [git.md](../git/git.md) section 5 says.

Check: the agent's diff edits only new code and the functions on its list, and its report names
the follow-ups it did not fix.

## 10. Python

What the sections above mean in a Python codebase.

**What a tool can prove.** Python has no compiler to catch a broken reference, and refactoring
tools miss dynamic use: `getattr`, names inside strings, `__all__`, star imports. In one study,
480 of 1,152 automatic refactorings made with rope introduced new type errors, and some of the
same bugs showed up in PyCharm (Oliveira et al., 2025). LibCST's scope analysis does not follow
attribute names, and pyright's rename can stop at the files that are open or included. So:

- only formatting (`ruff format`, Black) and the linter's safe fixes (`ruff check --fix`, never
  `--unsafe-fixes`) meet the sweep conditions of section 4 by themselves;
- a rename or a move, made by an IDE, rope or a LibCST codemod, goes step by step, and each one
  is checked three ways: the type checker passes, the tests pass, and `grep -rn "old_name"` finds
  no use left in code or in strings;
- a LibCST codemod may sweep the repository only where the type checker and the tests cover every
  file it edits. Bowler, an older codemod tool, is archived; use LibCST.

**Adding a type checker to old code.** [python.md](../python/python.md) asks for a type checker
in CI. To get there without a rewrite:

- run it on every module, with strict settings as the default;
- give each legacy module that does not pass yet a per-module override in the checker's config
  (`[[tool.mypy.overrides]]` in `pyproject.toml`), or a `# type: ignore[code]` on the line;
- turn on `warn_unused_ignores`, so a suppression that no longer suppresses anything fails the
  build;
- give each function a change touches full annotations in that change (section 2), and remove a
  module's override when the type checker passes on that module without it. The number of
  overrides is the count that only goes down.

Ramp took both paths in one project: a single sweep commit for `ruff format` and the linter, and
the step-by-step path for mypy, with strict settings on new code (2024).

Check: the sweep commits in the history are formatter or safe-fix output only, and the list of
per-module overrides never gets longer.

## 11. Where these rules come from

Every rule above comes from public practice:

- Martin Fowler, *Refactoring* (2nd ed., 2018), and martinfowler.com: the definition, the two
  hats, preparatory and opportunistic refactoring, parallel change (expand, migrate, contract).
- Kent Beck, *Tidy First?* (2023): make the change easy first; tidy first, after, later or never;
  structure and behavior in separate changes.
- Michael Feathers, *Working Effectively with Legacy Code* (2004): characterization tests,
  sprout and wrap.
- Ola Ellnestam and Daniel Brolund, *The Mikado Method* (2014).
- PEP 8, section "A Foolish Consistency is the Hobgoblin of Little Minds"; Google's style guides
  for Python, C++ and Go.
- *Software Engineering at Google* (2020), chapters 1, 8, 15, 20 and 22: the churn rule,
  changing style rules, deprecation, static analysis, large-scale changes. Google's code review
  guide, "Small CLs".
- Will Larson, "Migrations" (2018); Mike Hadlow, "The Lava Layer Anti-Pattern" (2014); Jimmy
  Bogard on the rule of 2 (2015); qntm, "Ratchets in software development" (2021).
- Measured studies: Kim, Zimmermann and Nagappan on refactoring at Microsoft (2014); Bavota et
  al. on refactorings followed by bugs (2012, replicated on 103 systems in 2020); Herzig and
  Zeller on tangled changes (2013); Sadowski et al. on static analysis at Google (2015 and 2018)
  and on code review at Google (2018); Oliveira et al. on faulty Python refactorings (2025); the
  studies of coding agents' scope and rule-following from 2025 and 2026 behind section 9.
