# What to test

Which code a test is written for, which code gets no test, and how to write one. Where the test
file goes and how it is built are [layout.md](layout.md) and
[test-structure.md](test-structure.md); how it stands in for the outside world is
[fakes-and-boundaries.md](fakes-and-boundaries.md).

**Navigation**

- [1. A test is written for a break you can name](#1-a-test-is-written-for-a-break-you-can-name)
- [2. What earns a test](#2-what-earns-a-test)
- [3. What gets no test](#3-what-gets-no-test)
- [4. How to test what earns a test](#4-how-to-test-what-earns-a-test)
- [5. Where it stops holding](#5-where-it-stops-holding)
- [6. Sources](#6-sources)

## 1. A test is written for a break you can name

**Before you write a test, name the edit to the team's own code that would turn it red, and check
that the edit would break something a caller, a user or another system relies on.** If you cannot
name one, or the only edits that turn it red change nothing anyone relies on (a refactor, a rename
nothing outside the code reads, a change inside a library), do not write it; section 5 names where
this stops holding. Such a test is a change detector, and Google's verdict on those is plain:
"Change detectors provide negative value, since the tests do not catch any defects, and the added
maintenance cost slows down development. These tests should be re-written or deleted." A rename
that something outside reads, such as a field another service parses, breaks that reader: its test
is the last row of section 2.

Check: before you stage, name, for each test the diff adds, the edit to the team's code that turns
it red and the `FAILED` line it printed in section 4, step 5. Both go in the pull request's
Verification section.

**A test that reproduces a bug that reached users is always written**, whatever row of section 3
the code falls in. Mark Seemann, who leaves code with one path untested, makes the same exceptions:
"if you're in doubt of how it works, then write a test", and "If you have a defect in production,
then reproduce that defect with one or more tests, even if the code in question is 'trivial'".
**When you cannot tell whether an edit would be a bug, write the test**; when this section names a
bug edit in code a section 3 row lists, this section wins.

**When your change touches a test already in the suite, or turns it red**
([refactoring.md](../refactoring/refactoring.md) section 2), and the only edits that turn it red
change nothing anyone relies on, rewrite it around the behavior it meant to pin. Delete it only in
a commit of its own whose body names those edits; never delete a test in the change that turns it
red. A test your change neither edits nor turns red is a follow-up
([refactoring.md](../refactoring/refactoring.md) section 8).

**When your change turns a test red, the code is wrong until shown otherwise.** Change the test's
expected value only when the change's stated purpose is to change the behavior that test pins, and
name that value in the commit body. Its setup and its call may follow a changed signature or name;
its expected value and what it compares may not. A test that pins structure is the paragraph
above's case. Never add `skip` or `xfail`, or loosen an assertion, to turn it green. A `skip` is
for a test that can run only under a condition, such as a platform or a service; an `xfail` is for
a bug not fixed yet, named with `raises=` and its issue. Neither mark fails the suite while the
test is still broken. A test red only in some orders is [running-tests.md](running-tests.md)
section 9's case. When tests conflicted with the task, coding agents often edited the tests instead
of the code (ImpossibleBench).

Check: before you commit, the diff adds no `skip` or `xfail` mark to a test the change turned red,
and the commit body names every expected value the change edits.

## 2. What earns a test

**When you decide whether code gets a test, find its row and write what the last column says.**

| Code | Example | What it earns |
|---|---|---|
| A rule the team wrote: a branch, a calculation, a parse, a validator | `needs_reminder`; a settings validator that rejects a placeholder secret | a unit test per behavior ([test-structure.md](test-structure.md) section 4) |
| A flow that reaches outside the process: a use case, a route, a client class | `remind_overdue_invoice`; `PaymentGateway` | a few tests through its public entry, with the outside cut where [fakes-and-boundaries.md](fakes-and-boundaries.md) section 3 says |
| A declaration whose deletion changes behavior and that nothing else notices: a flag that stops a bad start or keeps a secret out of an error, a required setting's missing default, an access check on a route | `env_ignore_empty=True` and `hide_input_in_errors=True` on a settings class; a required field with no default | one test of the consequence (the start stops, the error text holds no secret), never of the declared value |
| An error the code catches and survives: a fallback, a retry that gives up | a client that returns "unavailable" after a timeout | one test of that path |
| A name or a shape another system reads: a field of a payload another service parses, the schema of an event | the fields of an export a partner imports | one test that pins it, its docstring opening with `Pins:` ([test-structure.md](test-structure.md) section 5, [assertions.md](assertions.md) section 2) |

- **Rules** are where a test finds bugs. HackSoft's Django Styleguide puts the line for a model:
  "Models need to be tested only if there's something additional to them - like validation,
  properties or methods."
- **Flows** get few tests, at their entry. Harry Percival and Bob Gregory: "Write the bulk of your
  tests against the service layer."
- **Decisions like these** fail silently when someone deletes the line, and nothing else notices:
  without `hide_input_in_errors=True`, a failed pydantic-settings start writes what it read into
  the error text. An input whose repr is over 50 bytes shows as its first 25 and last 24 bytes, so
  a short secret shows whole and a long one shows both ends
  ([python.md](../python/python.md) section 5 owns the flag). A 2026 open-source project leaked a
  database password this way and fixed it with the flag, a sanitizer change and tests.
- **Error paths** are where the worst failures start. Yuan et al. studied 198 failures in five
  distributed systems: "almost all (92%) of the catastrophic system failures are the result of
  incorrect handling of non-fatal errors", and in 58% of them "the underlying faults could easily
  have been detected through simple testing of error handling code".

Code that holds a rule and also reaches outside is split before it is tested, by moving "as much
as logic as possible out of the hard-to-test element" (Martin Fowler, *Humble Object*); the rule
then takes the first row and the rest the second.

## 3. What gets no test

**When the code is one of these, write no test for it; test what the last column names.**

| What | Why it earns none | Test this instead |
|---|---|---|
| A library's own mechanics: pydantic-settings reading a variable into a field or JSON into a list, an ORM mapping a column | the library's own suite tests it: pydantic-settings' `tests/test_settings.py` covers reading a variable, what `env_ignore_empty` does once it is on, and JSON parsing. A red test means the library changed. A setting's variable name gets no test either: [python.md](../python/python.md) section 5 gives a default only to a value safe in every environment, so a wrong name leaves a safe value in place, and on a required value it stops the start | the team's code that uses the value; whether your class turns such a switch on is section 2's third row |
| Trivial code: a field, a property that returns a field, a dataclass, a call that only forwards | "You won't gain anything from testing simple getters or setters or other trivial implementations (e.g. without any conditional logic)" (Ham Vocke, *The Practical Test Pyramid*) | the code that uses it. It earns a test the day it gains a branch |
| A value that is a choice: `MAX_RETRIES = 5`, a model name, a timeout | changing it is a decision, not a bug, so a test that asserts it turns red only on a deliberate change: a change detector | the behavior around it, never the number: a failing call is retried, and the retries stop |
| A log line | [logging.md](../logging/logging.md) section 11 owns it and rules out tests of log output | nothing; a check that a secret stays out of the log is [assertions.md](assertions.md) section 6 |
| A private helper, or a value the unit asks a collaborator for | what the public function returns already shows it ([fakes-and-boundaries.md](fakes-and-boundaries.md) sections 2 and 5) | the public function |
| What the type checker already rejects | the checker runs on every change ([static-checks.md](../static-checks/static-checks.md) section 5) | nothing |

The line between this table's third row and section 2's third row: deleting a guard is a bug
nobody chose, so it earns a test; changing a number is a choice, so it does not.

The settings tests in [python/settings-example.md](../python/settings-example.md) show both
tables at work: they test that the required values have no default, the placeholder validator and
the two flags, and nothing that pydantic-settings reads or parses.

## 4. How to test what earns a test

**When you write a test for code that earns one, take these steps in order.**

1. **Before you write the test**, name the guarantee in one sentence and the edit to the code that
   breaks it (section 1): a plausible bug, such as a flipped comparison or a dropped branch, not the
   removal of the whole body.
2. **Before the first test body, list the cases from the guarantee**, not from the code's branches:
   one case per outcome the guarantee names and one per error the unit catches, and for each
   boundary the guarantee draws, the boundary value and its closest neighbor on the other side
   (2-value boundary analysis). Each case is one test, or one row of a table
   ([test-structure.md](test-structure.md) sections 4 and 6). Where one property holds for every
   input, such as a round trip or agreement with a simpler implementation, add a Hypothesis
   property to the list ([libraries.md](libraries.md)); the boundary and error cases stay on it.
3. **In the act step, drive the public entry the caller uses**
   ([fakes-and-boundaries.md](fakes-and-boundaries.md) section 5). The test sits in the
   `Test<Unit>` class of the file [layout.md](layout.md) section 3 names; which collaborator is cut
   and the stand-in that replaces it follow [fakes-and-boundaries.md](fakes-and-boundaries.md)
   sections 3 and 1.
4. **When you write the assertion, take the expected value from the guarantee**, never from what
   the code returned; a characterization test ([test-structure.md](test-structure.md) section 8) is
   the one exception. LLM-written assertions tend to capture what the code did, not what it should
   do (Konstantinou et al.). The line that decides pass or fail follows
   [assertions.md](assertions.md), and [fakes-and-boundaries.md](fakes-and-boundaries.md) section 2
   when a fake records the result.
5. **Before you trust the test, run it and see it fail once, on its own assertion**: for new code,
   while the code does not yet do what the guarantee says (write only enough of it for the test to
   run); for existing code, with the step-1 edit applied, then undo the edit. Red is exit code 1
   and, under `pytest -vv`, a `FAILED` line whose message is your assertion (`- assert …` or the
   assertion's own message). For a `pytest.raises` block, red is `- Failed: DID NOT RAISE <type>`
   when nothing is raised, or `- AssertionError: Regex pattern did not match.` when the message
   does not match. An `ERROR` line, a message that starts with the type of an exception the code
   raised, such as `TypeError:`, or exit code 2 (a collection error), 4 (no such test) or 5
   (nothing selected) is not red: fix the test until it fails on its assertion.
6. **Once it is red for the right reason, make it pass**, then run the module's tests
   ([running-tests.md](running-tests.md) section 3).

A test nobody saw fail may be unable to fail: in 21 Java projects, 9% of the methods the study
analyzed could lose their whole body with no test turning red (Vera-Pérez et al., pooled; 1-46% per
project). The guard is seeing the test fail (Freeman and Pryce; Seemann); Fucci et al. found that
test-first order itself had no important effect.

## 5. Where it stops holding

- **A library you maintain.** Its mechanics are your code: they earn tests.
- **A library that changed behavior under you.** When an upgrade broke behavior your code relies
  on without a word, pin that one behavior with a test that calls the library the way your code
  does, and keep it until the next upgrade shows it holds. Robert C. Martin's *Clean Code* (ch. 8)
  calls these learning tests. Ordinary tests are a weak net here: in 262 Java projects they caught
  on average 47% of faults injected into the libraries they call directly.
- **Code with no tests that you are about to change.** Characterization tests pin what it does
  today, right or wrong ([refactoring.md](../refactoring/refactoring.md) section 3); this file
  decides which tests the changed code keeps.

## 6. Sources

Alex Eagle, "Testing on the Toilet: Change-Detector Tests Considered Harmful", Google Testing Blog
(2015). HackSoft Django Styleguide, "Testing". Harry Percival and Bob Gregory, *Architecture
Patterns with Python*, ch. 5. langflow pull request #15147 (September 2026), on a password leaked
through a settings `ValidationError`. pydantic-core `src/tools.rs` at v2.41.5: how an error's text
cuts an input's repr over 50 bytes. Ding Yuan et al., "Simple Testing Can Prevent Most Critical
Failures" (OSDI 2014). Martin Fowler, "HumbleObject" (bliki). pydantic-settings
`tests/test_settings.py` at 2.15.0. Ham Vocke, "The Practical Test Pyramid", martinfowler.com
(2018). Mark Seemann, "What to test and not to test" (2018). Robert C. Martin, *Clean Code*
(2008), ch. 8, "Learning Tests Are Better Than Free". Joseph Hejderup and Georgios Gousios, "Can We
Trust Tests To Automate Dependency Updates?" (JSS 2022).

The red-test rule of section 1: Titus Winters, Tom Manshreck and Hyrum Wright (eds.), *Software
Engineering at Google* (2020), ch. 12, "Strive for Unchanging Tests". Google Testing on the Toilet,
"Test Behavior, Not Implementation" (2013). pytest documentation, "How to use skip and xfail to
deal with tests that cannot succeed". Zhong et al., ImpossibleBench, arXiv 2510.20270 (2025, a
preprint): coding agents editing tests that conflict with the task.

The steps of section 4: Steve Freeman and Nat Pryce, *Growing Object-Oriented Software, Guided by
Tests* (2009), ch. 5, "Watch the Test Fail". Mark Seemann, "A red-green-refactor checklist" (2019).
ISTQB Certified Tester Foundation Level syllabus v4.0.1 (2024), section 4.2.2, boundary value
analysis. Hypothesis 6.168.3 documentation, the tutorial's introduction: property-based testing is
an addition to unit testing, "not always a replacement". Brian Marick, "Faults of Omission" (2000).
Kent Beck, "Canon TDD" (2023). Arquimedes Canedo, "Oracles That Cannot Fail", arXiv 2608.17214
(2026, a preprint): an expected value taken from the code under test cannot fail. Konstantinou, Degiovanni and Papadakis, arXiv 2410.21136 (2024, a
preprint): LLM-generated test oracles tend to capture what the code did rather than what it should
do.
Vera-Pérez et al., arXiv 1807.05030 (2018): pseudo-tested methods in 21 Java projects.
Fucci et al., arXiv 1611.05994 (2016): test-first against test-after order. pytest 9.1.1
documentation, "Managing pytest's output" and the exit codes reference, and its source,
`src/_pytest/runner.py` and `src/_pytest/main.py`: which outcome reads `FAILED` or `ERROR`, and
each exit code.
