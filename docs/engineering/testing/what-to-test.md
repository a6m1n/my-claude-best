# What to test

Which code a test is written for, which code gets no test, and what a test that earns its place
asserts. Where the test file goes and how it is built are [layout.md](layout.md) and
[test-structure.md](test-structure.md); how it stands in for the outside world is
[fakes-and-boundaries.md](fakes-and-boundaries.md).

**Navigation**

- [1. A test is written for a break you can name](#1-a-test-is-written-for-a-break-you-can-name)
- [2. What earns a test](#2-what-earns-a-test)
- [3. What gets no test](#3-what-gets-no-test)
- [4. What a test asserts](#4-what-a-test-asserts)
- [5. Where it stops holding](#5-where-it-stops-holding)
- [6. Sources](#6-sources)

## 1. A test is written for a break you can name

**Before you write a test, name the edit to the team's own code that would turn it red, and check
that the edit would be a bug.** If you cannot name one, or the only edits that turn it red are a
change inside a library, a rename, or a decision the next author would copy into the test, do not
write it. Such a test is a change detector, and Google's verdict on those is plain: "Change
detectors provide negative value, since the tests do not catch any defects, and the added
maintenance cost slows down development. These tests should be re-written or deleted."

Vladimir Khorikov names the trap: "It's easy to fall into the trap of writing unit tests for the
sake of unit testing without a clear picture of whether it helps the project." A bigger suite is
not a safer one either. In one 2026 study of LLM-written Java suites, the number of tests and the
share of injected bugs they caught were unrelated (r≈0.03), and a coverage figure only says which
lines ran, not what a test checked.

The same question decides a test already in the suite: when the only edits that turn it red are a
library change or a deliberate one, rewrite it around the behavior it meant to pin, or delete it.

Check: for each test the diff adds, say in one sentence which edit to the team's code turns it
red. When unsure, make that edit, run the test, see it fail on its assertion, and undo the edit.

## 2. What earns a test

**When you decide whether code gets a test, find its row and write what the last column says.**

| Code | Example | What it earns |
|---|---|---|
| A rule the team wrote: a branch, a calculation, a parse, a validator | `needs_reminder`; a settings validator that rejects a placeholder secret | a unit test per behavior ([test-structure.md](test-structure.md) section 4) |
| A flow that reaches outside the process: a use case, a route, a client class | `remind_overdue_invoice`; `PaymentGateway` | a few tests through its public entry, with the outside cut where [fakes-and-boundaries.md](fakes-and-boundaries.md) section 3 says |
| A decision an edit can undo without a sound: a flag that stops a bad start or keeps a secret out of an error | `env_ignore_empty=True`, `hide_input_in_errors=True` on a settings class | one test of the consequence (the start stops, the error text holds no secret), never of the flag's value |
| An error the code catches and survives: a fallback, a retry that gives up | a client that returns "unavailable" after a timeout | one test of that path |

- **Rules** are where a test finds bugs. HackSoft's Django Styleguide puts the line for a model:
  "Models need to be tested only if there's something additional to them - like validation,
  properties or methods."
- **Flows** get few tests, at their entry. Harry Percival and Bob Gregory: "Write the bulk of your
  tests against the service layer."
- **Decisions like these** fail silently when someone deletes the line, and nothing else notices:
  without `hide_input_in_errors=True`, a failed pydantic-settings start prints every value it
  read, secrets included. A 2026 open-source project leaked a database password this way and fixed
  it with the flag and a test.
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
| A library's own mechanics: pydantic-settings reading a variable into a field or JSON into a list, an ORM mapping a column | the library's own suite tests it: pydantic-settings' `tests/test_settings.py` covers reading, empty values and JSON parsing. A red test means the library changed or a field was renamed on purpose | the team's code that uses the value; nothing when there is none |
| Trivial code: a field, a property that returns a field, a dataclass, a call that only forwards | "You won't gain anything from testing simple getters or setters or other trivial implementations (e.g. without any conditional logic)" (Ham Vocke, *The Practical Test Pyramid*) | the code that uses it. It earns a test the day it gains a branch |
| A constant or a configured value: `MAX_RETRIES = 5`, a model name, a default | the test copies the value: a change detector | the behavior that depends on it: a failing call is retried five times, and the sixth never happens |
| A log line | Google's mutation testing leaves logging out: "Mutants in logging statements are usually unproductive and would not lead to tests that improve software quality" | the message a person or an alert reads, when one does |
| A private helper, or a value the unit asks a collaborator for | what the public function returns already shows it ([fakes-and-boundaries.md](fakes-and-boundaries.md) section 5) | the public function |
| What the type checker already rejects | the checker runs on every change ([static-checks.md](../static-checks/static-checks.md)) | nothing |

Mark Seemann once argued for testing trivial code, because it may not stay trivial; in 2018 he
asked of code with one path through it: "Should you test code that has a cyclomatic complexity of
1? What would be the point of that?"

The settings test in [python/settings-example.md](../python/settings-example.md) shows both
tables at work: it tests the placeholder validator and the two flags, and nothing that
pydantic-settings reads or parses.

## 4. What a test asserts

**When you write the assertion, pick it by what the unit does**, the way Sandi Metz sorts the
messages an object handles:

| The unit | Assert |
|---|---|
| returns a value | the value |
| changes state, or sends something out | the state it left, or what the fake received ([fakes-and-boundaries.md](fakes-and-boundaries.md) section 2) |
| asks a collaborator for a value | nothing about the asking: the answer shows in what the unit returns |
| calls its own private helper | nothing: the test of the public call covers it |

Each test drives the unit the way its callers do, through its public entry: "make calls against its
public API rather than its implementation details" (*Software Engineering at Google*, ch. 12).

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
Ham Vocke, "The Practical Test Pyramid", martinfowler.com (2018). Goran Petrović et al., "Practical
Mutation Testing at Scale" (arXiv 2102.11378, 2021). Mark Seemann, "Test trivial code" (2013) and
"What to test and not to test" (2018). Sandi Metz, "The Magic Tricks of Testing" (RailsConf 2013).
Titus Winters, Tom Manshreck and Hyrum Wright, *Software Engineering at Google* (2020), ch. 12.
Robert C. Martin, *Clean Code* (2008), ch. 8, "Learning Tests Are Better Than Free". Joseph
Hejderup and Georgios Gousios, "Can We Trust Tests To Automate Dependency Updates?" (JSS 2022).
