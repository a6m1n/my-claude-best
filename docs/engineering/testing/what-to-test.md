# What to test

Which code a test is written for, which code gets no test, and where the rules for writing one
live. Where the test file goes and how it is built are [layout.md](layout.md) and
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
nothing outside the code reads, the variable name a setting is read under, a change inside a
library), do not write it; section 5 names where this stops holding. Such a test is a change
detector, and Google's verdict on those is plain: "Change detectors provide negative value, since
the tests do not catch any defects, and the added maintenance cost slows down development. These
tests should be re-written or deleted." A rename that something outside reads, such as a field
another service parses, breaks that reader: its test is the last row of section 2.

Vladimir Khorikov names the trap: "It's easy to fall into the trap of writing unit tests for the
sake of unit testing without a clear picture of whether it helps the project." A bigger suite is
not a safer one either. In one 2026 study of LLM-written Java suites, the number of tests and their
mutation score, the share of injected faults they caught, correlated weakly to negligibly (Pearson
r 0.03 for the raw score), and a coverage figure only says which lines ran, not what a test
checked.

**A test that reproduces a bug that reached users is always written**, whatever row of section 3
the code falls in. Mark Seemann, who leaves code with one path untested, makes the same exceptions:
"if you're in doubt of how it works, then write a test", and "If you have a defect in production,
then reproduce that defect with one or more tests, even if the code in question is 'trivial'".
**When you cannot tell whether an edit would be a bug, write the test**; when this section names a
bug edit in code a section 3 row lists, this section wins.

**When your change touches a test already in the suite**
([refactoring.md](../refactoring/refactoring.md) section 2) and the only edits that turn it red
change nothing anyone relies on, rewrite it around the behavior it meant to pin. Delete it only in
a commit of its own whose body names those edits; never delete a test in the change that turns it
red. A test your change does not touch is a follow-up
([refactoring.md](../refactoring/refactoring.md) section 8).

When you are unsure whether a test can fail, make the edit it names, run the test, see it fail on
its assertion, and undo the edit.

Check: before you stage, name, for each test the diff adds, the edit to the team's code that turns
it red.

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
  the error text, each input cut to 50 characters, so a secret can show whole
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
| A library's own mechanics: pydantic-settings reading a variable into a field or JSON into a list, an ORM mapping a column | the library's own suite tests it: pydantic-settings' `tests/test_settings.py` covers reading a variable, what `env_ignore_empty` does once it is on, and JSON parsing. A red test means the library changed. A setting's variable name gets no test either: a required one already stops the start (the missing-value table), and review keeps a defaulted one ([python/settings-example.md](../python/settings-example.md), "What this example does not claim") | the team's code that uses the value; whether your class turns such a switch on is section 2's third row |
| Trivial code: a field, a property that returns a field, a dataclass, a call that only forwards | "You won't gain anything from testing simple getters or setters or other trivial implementations (e.g. without any conditional logic)" (Ham Vocke, *The Practical Test Pyramid*) | the code that uses it. It earns a test the day it gains a branch |
| A value that is a choice: `MAX_RETRIES = 5`, a model name, a timeout | changing it is a decision, not a bug, so a test that asserts it turns red only on a deliberate change: a change detector | the behavior around it, never the number: a failing call is retried, and the retries stop |
| A log line | [logging.md](../logging/logging.md) section 11 owns it and rules out tests of log output | nothing; a check that a secret stays out of the log is [assertions.md](assertions.md) section 6 |
| A private helper, or a value the unit asks a collaborator for | what the public function returns already shows it ([fakes-and-boundaries.md](fakes-and-boundaries.md) sections 2 and 5) | the public function |
| What the type checker already rejects | the checker runs on every change ([static-checks.md](../static-checks/static-checks.md) section 5) | nothing |

The line between this table's third row and section 2's third row: deleting a guard is a bug
nobody chose, so it earns a test; changing a number is a choice, so it does not.

Mark Seemann once argued for testing trivial code, because it may not stay trivial; in 2018 he
asked of code with one path through it: "Should you test code that has a cyclomatic complexity of
1? What would be the point of that?"

The settings tests in [python/settings-example.md](../python/settings-example.md) show both
tables at work: they test that the required values have no default, the placeholder validator and
the two flags, and nothing that pydantic-settings reads or parses.

## 4. How to test what earns a test

**When you write the test, take each part from the file that owns it.** Drive the unit by
[fakes-and-boundaries.md](fakes-and-boundaries.md) section 5, pick what to assert by its section 2
and the stand-in by its section 1, write the line that decides pass or fail by
[assertions.md](assertions.md), and keep one behavior per test
([test-structure.md](test-structure.md) section 4).

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
(2015). Vladimir Khorikov, *Unit Testing Principles, Practices, and Patterns* (Manning, 2020), ch. 1
excerpt, and "Unit tests value proposition" (2016). Zhao et al., arXiv 2607.22880 (2026, a
preprint): suite size and mutation score in LLM-written Java suites. Laura Inozemtseva and Reid
Holmes, "Coverage Is Not Strongly Correlated with Test Suite Effectiveness" (ICSE 2014). HackSoft
Django Styleguide, "Testing". Harry Percival and Bob Gregory, *Architecture Patterns with Python*,
ch. 5. langflow pull request #15147 (September 2026), on a password leaked through a settings
`ValidationError`. Ding Yuan et al., "Simple Testing Can Prevent Most Critical Failures" (OSDI
2014). Martin Fowler, "HumbleObject" (bliki). pydantic-settings `tests/test_settings.py` at 2.15.0.
Ham Vocke, "The Practical Test Pyramid", martinfowler.com (2018). Mark Seemann, "Test trivial code"
(2013) and "What to test and not to test" (2018). Robert C. Martin, *Clean Code* (2008), ch. 8,
"Learning Tests Are Better Than Free". Joseph Hejderup and Georgios Gousios, "Can We Trust Tests To
Automate Dependency Updates?" (JSS 2022).
