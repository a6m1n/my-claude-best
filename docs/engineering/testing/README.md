# Testing practices

How a pytest suite is laid out and written: which code earns a test, where a test file goes, how
its class and names are built, where its setup comes from, how it stands in for the outside world,
what it asserts, how the suite runs, and which libraries help.

**Navigation**

- [The one rule](#the-one-rule)
- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)

## The one rule

**A failing test tells its reader, from its id alone, which guarantee broke, and nothing but that
guarantee turns it red.** The id,
`tests/unit/remind_overdue_invoice/test_reminder_rules.py::TestNeedsReminder::test_a_second_reminder_waits_for_the_interval`,
names the module, the source file, the unit and the promise. The test fails when that promise
breaks, and not because of the order it ran in, the network, a renamed argument or a setting it
never asked for. The guarantee is one someone relies on: a test that no bug in the team's own code
can turn red is not written ([what-to-test.md](what-to-test.md) section 1). Each file below keeps
one part of that true.

## What is here

- [what-to-test.md](what-to-test.md): which code earns a test, which gets none, how to write one
  test, step by step, and what to do when your change turns a test red. Read it before you write a
  test, before you edit a test your change turned red, and when you review one.
- [layout.md](layout.md): the `tests/` tree, which suite a test belongs to, the path and the name
  of a test file, one class per file, packages and imports, the shared `support/` harness, and the
  tree's own `README.md` and `CLAUDE.md`. Read it when you create a test file or decide where one
  goes.
- [test-structure.md](test-structure.md): the `Test<Unit>` class, names that state the guarantee,
  one behavior per test, docstrings, and `parametrize` tables and when not to use them. Read it
  when you write the inside of a test file.
- [fixtures.md](fixtures.md): a scope on every fixture, no `autouse`, choosing the scope, where a
  fixture lives, teardown, patching and undoing, factories and parametrized fixtures. Read it when
  a test needs setup.
- [fakes-and-boundaries.md](fakes-and-boundaries.md): which stand-in to build, asserting results
  rather than calls, where each outside system is cut, and the offline unit suite. Read it when the
  code under test reaches outside the process.
- [assertions.md](assertions.md): exact values, whole records, named failures, floats, assert
  messages, and what must not leak. Read it when you write the line that decides pass or fail.
- [running-tests.md](running-tests.md): the configuration block, markers, running one module,
  warnings, order, time, async tests, parallel runs, flaky tests, tests that ask a real model, and
  static checks on tests. Read it when you run the suite, select part of it, or change its
  configuration.
- [libraries.md](libraries.md): what each common pytest library solves, when to add it, and the
  ones left out of the default set with the reason. Read it before you add a test dependency.
- [suite-example.md](suite-example.md): the test suite of one small service, written to every rule
  here, with the reason next to each file. Read it when you set up a suite or add a module's first
  tests.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/testing/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you write or change a test, a fixture
   or the pytest configuration, read `docs/engineering/testing/README.md` and the file it points
   to for that work." Without it an agent never opens the folder.
3. Copy `tests/README.md`, `tests/CLAUDE.md` and `tests/conftest.py` from
   [suite-example.md](suite-example.md), and the configuration block of
   [running-tests.md](running-tests.md) section 1, and adjust the names. Give every folder under
   `tests/` an empty `__init__.py` ([layout.md](layout.md) section 6). Add pytest 9.0 or newer and
   each plugin in `required_plugins` as development dependencies, locked with the rest
   ([running-tests.md](running-tests.md) section 1). Select ruff's `PT` rules and turn off `PT003`
   ([running-tests.md](running-tests.md) section 11).
4. Set up two CI jobs ([layout.md](layout.md) section 2): `pytest tests/unit` on every push and
   before a merge, and `pytest tests/integration --timeout=120` in a job of its own
   ([running-tests.md](running-tests.md) section 9).
5. The practice links [readability.md](../readability/readability.md),
   [python.md](../python/python.md), [file-structure.md](../file-structure/file-structure.md),
   [static-checks.md](../static-checks/static-checks.md),
   [prompt-engineering.md](../prompt-engineering/prompt-engineering.md),
   [logging.md](../logging/logging.md), [refactoring.md](../refactoring/refactoring.md) and
   [git.md](../git/git.md) for the rules they own. Copy those folders too, or replace each link
   with your own rule for that topic.
6. Existing tests follow the rules when a change touches them, the way
   [refactoring.md](../refactoring/refactoring.md) sections 2 and 7 say for new and touched code.
   A file moved to the new layout moves in a commit of its own ([layout.md](layout.md) section 4).
7. Re-check the lines that name a moving target: the pytest 9 configuration keys, the async
   plugins' keys, and the libraries of [libraries.md](libraries.md), which were read in
   September 2026.

When you review a test change, run the `Check:` lines of the files above that cover that work, and
hold the change to the example `tests/CLAUDE.md` in [suite-example.md](suite-example.md).

## The points to adapt

- **Which stand-in comes first.** This practice prefers the real class with a fake inside, then a
  hand-written fake, then `create_autospec`, for the reasons in
  [fakes-and-boundaries.md](fakes-and-boundaries.md) section 1, "Why this order", which also names
  the one measurement that points the other way. A team that prefers `create_autospec` for every
  collaborator keeps section 2 of [fakes-and-boundaries.md](fakes-and-boundaries.md), which is
  about what a test asserts, whatever the stand-in.
- **The async plugin** is pytest-asyncio or anyio's own, by what the code runs on
  ([running-tests.md](running-tests.md) section 7).

What does not change is the one rule above: a red test names one broken guarantee, and nothing else
turns it red.
