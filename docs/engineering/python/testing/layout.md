# Test layout

Where a test file lives, what it is called, and how the tree stays easy to navigate at a few
hundred files. The other files of this practice are in [README.md](README.md).

**Navigation**

- [1. The tree](#1-the-tree)
- [2. Which suite a test belongs to](#2-which-suite-a-test-belongs-to)
- [3. Where a test file goes](#3-where-a-test-file-goes)
- [4. One test class per file, and when a file becomes a folder](#4-one-test-class-per-file-and-when-a-file-becomes-a-folder)
- [5. A test of several files together](#5-a-test-of-several-files-together)
- [6. Packages and imports](#6-packages-and-imports)
- [7. The shared harness in support](#7-the-shared-harness-in-support)
- [8. The README and the CLAUDE.md of the tree](#8-the-readme-and-the-claudemd-of-the-tree)
- [9. Where it stops holding](#9-where-it-stops-holding)
- [10. Sources](#10-sources)

## 1. The tree

```text
tests/
├── README.md            for people: how to run the suites, where a new test goes (section 8)
├── CLAUDE.md            for agents: the rules a change must not break, and where to read more
├── __init__.py          empty; every folder below has one too (section 6)
├── conftest.py          the hook that marks each test with its suite; fixtures used across modules
├── unit/                needs nothing outside the process; runs on every push
│   ├── conftest.py      fixtures every unit test may use; only when there are some
│   ├── <module>/        one folder per module of the application
│   │   ├── test_<source file>.py        one Test<Unit> class (section 4)
│   │   └── <source file>/               from the second test class for that file
│   │       └── test_<subject>.py
│   ├── core/            the tests of core/, the same way
│   └── <adapter>/       the tests of an adapter such as api/, the same way
├── integration/         needs a real database, a container, the network or a real model
│   ├── conftest.py      the resources the whole suite shares, such as one database
│   ├── <module>/
│   │   └── test_<source file>.py
│   └── <adapter>/
└── support/             fakes and builders the tests import; no test files, no fixtures
    └── fake_<system>.py
```

The words mean what [file-structure.md](../../any-language/file-structure/file-structure.md) section 2 says: a
module is a feature folder, `src/<app>/<domain>/<module>/`, and a source file is one `.py` file
inside it. pytest's `module` scope and the words "test module" mean something else: one test file.
Each module has one folder in each suite that tests it, and its adapter tests carry its name, so
one command runs every test of one module, `pytest tests/*/<module> tests/*/*/*_<module>*`
([running-tests.md](running-tests.md) section 3). Home Assistant's developer docs make a folder per
module their rule: "Tests for each integration are stored inside a directory named after the
integration domain", where an integration is a plugin, and its repository keeps about 5,800 test
files that way. PyPI's Warehouse mirrors its packages the same way in a `tests/unit/` of about two
hundred files. Neither splits its suites by what a test needs, as section 2 does: they back the
folder per module, not the split.

- **Tests live in `tests/` at the repository root, outside the application package**, grouped by
  suite and not placed inside the modules, so CI picks a suite by its folder and a module folder
  holds only code that ships. Keeping tests next to the code is a respected alternative (the
  HackSoft Django Styleguide puts `tests/` in each app); a framework that starts it there, as
  Django's `startapp` does, keeps it (section 9).
- **A test file never sits directly under `tests/`**, and never directly in a suite folder,
  except the guarantee files of section 5. The hook in `tests/conftest.py` stops the run on a test
  outside a suite folder ([suite-example.md](suite-example.md) shows it).
- **Stop at the module.** The test tree mirrors `<module>/`, not the folders inside it:
  `src/<app>/<domain>/<module>/services/service_invoice_total.py` is tested in
  `tests/unit/<module>/test_service_invoice_total.py`. File names inside one module do not repeat,
  since a file in a role folder starts with its role and each of the module's other files is named
  for its role ([file-structure.md](../../any-language/file-structure/file-structure.md) sections 3 and 7); the
  next bullet names the one exception. Module names are unique across the application (the same
  practice, section 6, move 6). A deeper mirror adds two levels and a second move on every move
  inside the module.
- **A module subfolder that is not a role folder, such as a pipeline's folder, is always mirrored
  in the test tree**, whatever its file names: `src/<app>/<domain>/<module>/<pipeline>/schemas.py`
  is tested in `tests/unit/<module>/<pipeline>/test_schemas.py`, next to the module's own
  `test_schemas.py`.

Check: `find tests -name 'test_*.py' | awk -F/ 'NF < 4'` prints only the guarantee files of
section 5: every other test file sits at least one folder below its suite.

## 2. Which suite a test belongs to

The line between the suites is what a test needs to run; speed follows from that. Martin Fowler
calls the words "unit" and "integration" "rather murky" (*On the Diverse And Fantastical Shapes of
Testing*, 2021), so this practice does not define them; it defines the folders. Google draws the
same line with its test sizes: size is "the resources that are required to run a test case", kept
apart from the code a test checks, and a small test runs in one process with no network or disk
(*Software Engineering at Google*, ch. 11). The `unit/` suite here is close to Google's small
tests, not the same: it may use the disk through `tmp_path`.

| Suite | What its tests need | When it runs |
|---|---|---|
| `unit/` | nothing outside the Python process: no network, no database, no container, no real model | on every push and in the pre-merge CI job |
| `integration/` | at least one of: a real database, a container, the network, a real model | in its own CI job, and on demand |

- **When you create a test file, ask what its act step needs.** The act step is the one line
  that calls the code under test ([test-structure.md](test-structure.md) section 1). If that call
  needs anything from the second column beyond `unit/`, the file goes to `integration/`.
- **A unit test that reaches the network fails, wherever it sits.** The suite is offline by
  configuration, not by habit ([fakes-and-boundaries.md](fakes-and-boundaries.md) section 4).
- **A test that calls a real model is an integration test with a mark of its own**, which no
  default run selects ([running-tests.md](running-tests.md) section 10).

## 3. Where a test file goes

When you create a test file, say in one sentence what it holds, then give it a path from this
table before you write its body. The path is decided by the source file the act step calls; code
the test only imports to arrange state, to read a result or to build a stand-in does not decide
it.

| The act step calls | The test file |
|---|---|
| a unit in `src/<app>/<domain>/<module>/<file>.py`, at any depth inside the module but for the one case of section 1 | `tests/<suite>/<module>/test_<file>.py` |
| a unit in `src/<app>/core/<file>.py` | `tests/<suite>/core/test_<file>.py` |
| a unit in an adapter, `src/<app>/<adapter>/<file>.py` | `tests/<suite>/<adapter>/test_<file>.py` |
| several source files, and no one of them is the subject | a guarantee file (section 5) |

- **The file is named for the source file, the class for the unit.** `reminder_rules.py` holds
  `needs_reminder`, so its test is `test_reminder_rules.py` with the class
  `TestNeedsReminder` ([test-structure.md](test-structure.md) section 1). A reader who has the
  source file open knows the test file's name, and a failing test id names both.
- **Integration tests follow the same rule.** An integration test of a module's flow calls its
  `usecase.py`, so it is `tests/integration/<module>/test_usecase.py`; a test that drives the HTTP
  app through its routes is `tests/integration/api/test_routes_<module>.py`. `usecase.py` has the
  same name in every module, and so does its test: the folder says which module it is, as it does
  for the source file.
- **The unit of an adapter test is the route or command function** the test reaches through the
  app or the command line.

Check: for each test file, `ls` the source folder of its module and find the file its name
comes from. A test file whose stem names no source file is either a promoted file (section 4) or a
guarantee file (section 5); anything else is misnamed. A test folder inside a module's test folder
is named for a source file (promoted, section 4) or for a source subfolder (mirrored, section 1);
anything else is misplaced.

```text
# Good: the path names the module, the file name names the source file.
src/shop/billing/remind_overdue_invoice/reminder_rules.py
tests/unit/remind_overdue_invoice/test_reminder_rules.py

# Bad: named for the domain. A red test says "billing", and the reader opens every module in it.
tests/unit/test_billing.py
```

## 4. One test class per file, and when a file becomes a folder

**When you write a test file, give it exactly one `Test<Unit>` class**, for the one unit its act
steps call ([test-structure.md](test-structure.md) section 1). The file holds that class, its
module-level fixtures and constants, and the builders and fakes only it uses (section 7), and
nothing else. A reader who opens the file reads one
subject from top to bottom, and the file name, the class name and the test name together say
what failed.

The class docstring is the file's one sentence ([readability.md](../../any-language/readability/readability.md)
section 2). When it needs "and", the file splits by subject into the folder below.

Check: `grep -c '^class Test' <file>` prints `1` for every test file.

**When a source file needs a second test class**, because it holds a second unit or because one
unit's tests split by subject, the test file becomes a folder named for the source file, and each
class gets a file inside it named for its unit or its subject:

```text
# Before: one class for reminder_rules.py.
tests/unit/remind_overdue_invoice/test_reminder_rules.py

# After: reminder_rules.py gained a second rule. The folder is named for the source file,
# without the test_ prefix, and each file inside holds one class.
tests/unit/remind_overdue_invoice/reminder_rules/test_needs_reminder.py
tests/unit/remind_overdue_invoice/reminder_rules/test_next_reminder_date.py
```

One unit's tests split by subject when its class docstring needs "and"
([readability.md](../../any-language/readability/readability.md) section 2). Each file then keeps the class
`Test<Unit>` and is named `test_<subject>.py`.

- **Move the first file in a commit of its own, before the commit that adds the second**:
  [refactoring.md](../../any-language/refactoring/refactoring.md) section 3, rule 3, owns the
  separate move commit.
- **A promoted folder is the deepest level**; when the source file becomes a folder itself, its
  tests take the paths section 3 gives the new files, in the same move commit.

## 5. A test of several files together

Some guarantees belong to no single source file: "every route requires a login", "no module
imports another module's `models.py`". **When the act steps of a test call several source files
and none of them is the subject, name the file for the guarantee**, as a sentence:
`test_every_route_requires_a_login.py`. Its one class is named for the guarantee too:
`TestEveryRouteRequiresALogin`.

- **Put it in the module folder when all the files it calls are in one module**, and directly in
  the suite folder when they are not. These are the only test files that may sit directly in
  `unit/` or `integration/`.
- **Its class docstring opens with the source files it covers**, since the file name no longer
  names one.
- **Before you write one about imports, check whether an import contract can state it.** A rule
  about which package may import which belongs to the contracts of
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 11, not to a test.

## 6. Packages and imports

**Give every folder under `tests/` an empty `__init__.py`, `tests/` itself included, and run pytest
in its default import mode, `prepend`.** Every test module then has a full package name, such as
`tests.unit.remind_overdue_invoice.test_reminder_rules`, so two modules can each have a
`test_usecase.py`.

Check:
`find tests -type d -not -name __pycache__ -not -path '*/__snapshots__*' '!' -exec test -e '{}/__init__.py' ';' -print`
prints nothing.

A test imports the harness by its package path:

```python
# Good: the import line says which package the fake comes from.
from tests.support.fake_mailer import FakeMailer
```

Why `prepend` and not `importlib`: pytest keeps `prepend` the default, and under `importlib` its
reference says helper modules in the test folders "are not importable", where a test that
annotates a fixture with a fake's type has to import that type from `tests.support`.

Rules that follow from it:

- **Never put `tests` on `pythonpath`.** Then `support` imports under two names, `support` and
  `tests.support`, and a fake imported both ways is two different classes. The repository root
  needs no entry: with the packages in place, pytest adds it itself. Check:
  `grep -rnE '^\s*(from|import) support\b' tests/` prints nothing.
- **The application is imported as installed**, the way the src layout of
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 9 installs it: `uv sync`
  installs the package in editable mode, so no `pythonpath = ["src"]` is needed.
- **One `tests/` tree per repository root.** Every test run registers the package name `tests`; a
  second tree with its own `tests` package, such as in a monorepo, clashes with the first. A
  monorepo gives each project its own test run from its own root.
- **Imports are absolute**, as everywhere else ([file-structure.md](../../any-language/file-structure/file-structure.md)
  section 7); a test never imports another test module.

## 7. The shared harness in support

`tests/support/` holds the code tests import: fakes, builders of test data, and helpers that
start or empty a test resource. It follows the naming rules of a module
([file-structure.md](../../any-language/file-structure/file-structure.md) section 7): one file per system it
stands in for or per kind of data, named with its role first, `fake_mailer.py` holding
`FakeMailer`, never `helpers.py` or `utils.py`.

- **Code moves to `support/` when a second test file needs it**, not before. A fake or a builder
  one file uses stays in that file.
- **No fixtures in `support/`.** It is imported, so an import line says where a name came from; a
  fixture is requested by name, so fixtures live in a test file or a `conftest.py`
  ([fixtures.md](fixtures.md) section 4). Check: `grep -rn "@pytest.fixture" tests/support/`
  prints nothing.
- **A file a test reads is built in the test when its bytes do not matter**, with `tmp_path`, and
  checked in only when the bytes are the subject, such as a sample of a partner's real export
  format. A checked-in file goes under `tests/support/data/<system>/`, with an `__init__.py` in
  each folder, and a test reaches it with
  `importlib.resources.files("tests.support.data.<system>")`, never with a path built from
  `__file__`, which breaks when the test file moves.

## 8. The README and the CLAUDE.md of the tree

Two short files open the tree, one per reader.

| File | Reader | Holds | Never holds |
|---|---|---|---|
| `tests/README.md` | a person new to the project | how to run each suite and one module; where a new test file goes; where fakes live; a link to this practice | the rules themselves |
| `tests/CLAUDE.md` | an agent about to change a test | the few rules whose break is visible in a diff, one line each, each with a pointer to the section that owns it; one line that routes to `tests/README.md` | a copy of a rule's reasons or its check |

- **The README follows [git.md](../../any-language/git/git.md) section 9** in miniature: what the tree is, the
  commands, the structure. Its structure section names the kinds of folder, never every file.
- **`CLAUDE.md` loads when an agent reads a file under `tests/`**, so it carries only what the
  agent must not miss: the rules whose break shows in a diff, such as no `autouse` or one class
  per file. Each line states the rule in a few words and points to the section that owns it; it
  never copies the rule's reasons or its check ([claude-md.md](../../../claude-code/claude-md.md)).
- **When a rule that a line points to changes, change the line in the same commit.**

[suite-example.md](suite-example.md) shows both files.

## 9. Where it stops holding

- **A framework that puts tests inside the app**, as Django does, keeps its own layout; the rules
  inside a test file still hold.
- **A library with no modules** mirrors its public packages instead, one folder per package, and
  keeps the rest of this file.

## 10. Sources

pytest documentation: "pytest import mechanisms and sys.path/PYTHONPATH" (`prepend`, `importlib`,
and the drawbacks of each) and "Good Integration Practices" (test layout, `importlib` for new
projects, "Choosing an import mode"), both for pytest 9.1; pytest source at 9.1.1,
`src/_pytest/pathlib.py`, a maintainer's comment in pytest discussion #12714 on the `tests` package
name clashing across trees, and the closing comment of pytest issue #7245 (2022) on why the
default stays. Martin Fowler, *On the Diverse And Fantastical Shapes of Testing* (2021). Titus
Winters, Tom Manshreck and Hyrum Wright, *Software Engineering at Google* (2020), ch. 11, "Test
Size". The HackSoft Django Styleguide on tests inside each app. Home Assistant developer docs,
"Integration tests file structure", and its repository's `tests/components/` (5,842 test files in
1,198 folders, September 2026); the `tests/unit/` tree of PyPI's Warehouse (212 test files).
Measured on pytest 9.1.1 (September 2026): with an `__init__.py` in every test folder,
`from tests.support... import` worked from the `pytest` command, from `python -m pytest`, from a
subfolder and under `pytest -n 2`, under `prepend` on Python 3.13 and under both modes on Python
3.12; with `tests/__init__.py` removed, collection failed.
