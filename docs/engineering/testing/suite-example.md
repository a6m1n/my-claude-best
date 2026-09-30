# Example: the test suite of one service

A worked example for the testing practice: the `tests/` tree of a small service, the pytest
configuration, the two files that open the tree, and one integration test file with its fixtures.
The service is the shop of [readability/module-example.md](../readability/module-example.md); its
module `remind_overdue_invoice` sends a reminder for an overdue invoice, at most once a week.
Every name is a placeholder.

The unit test of the reminder rule is the `TestNeedsReminder` file of that example, and
`tests/support/fake_mailer.py` is the `FakeMailer` of
[fakes-and-boundaries.md](fakes-and-boundaries.md) section 1; neither is repeated here.
`FakeMailer` sits in `support/` because two files use it: this module's integration test and the
test of its CLI command, not shown. The application's own code is left out: `Database` in
`shop/core/database.py` wraps a SQLAlchemy `Engine`, and `Mailer.send(to, *, subject, body)` is
the call the use case makes.

**Navigation**

- [The tree](#the-tree)
- [pyproject.toml: the pytest table](#pyprojecttoml-the-pytest-table)
- [tests/conftest.py: the suite of each test](#testsconftestpy-the-suite-of-each-test)
- [tests/README.md](#testsreadmemd)
- [tests/CLAUDE.md](#testsclaudemd)
- [tests/integration/conftest.py: one database for the run](#testsintegrationconftestpy-one-database-for-the-run)
- [The integration test of the reminder run](#the-integration-test-of-the-reminder-run)
- [Running it](#running-it)
- [What this example does not claim](#what-this-example-does-not-claim)

## The tree

```text
tests/
├── README.md
├── CLAUDE.md
├── __init__.py
├── conftest.py
├── unit/
│   ├── __init__.py
│   └── remind_overdue_invoice/
│       ├── __init__.py
│       └── test_reminder_rules.py       TestNeedsReminder
├── integration/
│   ├── __init__.py
│   ├── conftest.py                      one Postgres container per run, emptied after each test
│   ├── cli/
│   │   ├── __init__.py
│   │   └── test_commands_remind_overdue_invoice.py    the CLI command's test, not shown
│   └── remind_overdue_invoice/
│       ├── __init__.py
│       └── test_usecase.py              TestRemindOverdueInvoice
└── support/
    ├── __init__.py
    └── fake_mailer.py                   FakeMailer, also used by the CLI command's test, not shown
```

It is good because each file has the path [layout.md](layout.md) section 3 gives it: the rule in
`reminder_rules.py` is tested in `unit/remind_overdue_invoice/test_reminder_rules.py`, the use case
in `usecase.py` needs a database, so its test is `integration/remind_overdue_invoice/test_usecase.py`.
`pytest tests/*/remind_overdue_invoice tests/*/*/*_remind_overdue_invoice*` runs both, and
the CLI command's test with them: the first pattern expands to the module's folder in each suite,
the second to its adapter tests ([running-tests.md](running-tests.md) section 3).

## pyproject.toml: the pytest table

```toml
[tool.pytest]
testpaths = ["tests"]
addopts = ["-ra", "--disable-socket", "--allow-unix-socket", "-m", "not live_model"]
markers = [
    "unit: the offline suite; the collection hook sets it from the folder",
    "integration: the suite that needs a service; set from the folder too",
    "live_model: sends each call to a paid model API; select it on purpose",
]
strict_config = true
strict_markers = true
strict_parametrization_ids = true
strict_xfail = true
filterwarnings = ["error"]
required_plugins = ["pytest-randomly", "pytest-socket"]
```

It is good because it is the block of [running-tests.md](running-tests.md) section 1 without the
async keys: this service has no async code, so it installs no async plugin. The service has no
real-model test either, but it keeps the mark and its exclusion, so the first such test is safe
the day it is written.

## tests/conftest.py: the suite of each test

```python
"""Marks each test with its suite, read from its folder, and lets integration tests
reach the network."""

from enum import StrEnum, unique
from pathlib import Path

import pytest


@unique
class Suite(StrEnum):
    """The suite folders under tests/; each name is also the mark of its tests."""

    UNIT = "unit"
    INTEGRATION = "integration"


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    tests_root = config.rootpath / "tests"

    for item in items:
        suite = _suite_of(item, tests_root)
        item.add_marker(suite.value)

        # The configuration blocks the network for every test; the folder opens it.
        if suite is Suite.INTEGRATION:
            item.add_marker("enable_socket")


def _suite_of(item: pytest.Item, tests_root: Path) -> Suite:
    folder = item.path.relative_to(tests_root).parts[0]

    try:
        return Suite(folder)
    except ValueError:
        # from None: the enum's own message adds nothing to this one
        raise pytest.UsageError(
            f"{item.nodeid}: a test outside tests/unit and tests/integration"
        ) from None
```

It is good because the folder is the one place a test's suite is written: the hook reads it, so
`-m unit` selects exactly what `tests/unit` holds, and no test carries a mark by hand
([running-tests.md](running-tests.md) section 2). The suites are a closed set, so they are an
enum ([python.md](../python/python.md) section 3), and a test file outside both folders stops the
run at collection with a message that names it, instead of running unmarked. The mark is the
member's `.value`, because marks cross to pytest-xdist workers as plain strings: an enum member
there stops a `-n 2` run with an `INTERNALERROR`. Run on pytest 9.1.1 with pytest-socket 0.8.1:
a unit test that opened a socket failed with the plugin's error, an integration test whose
session fixture opened a TCP connection passed, and a stray `tests/test_stray.py` stopped the run
with exit code 4 and the message above.

## tests/README.md

```markdown
# Tests

The test suites of the shop service. `unit/` needs nothing outside Python; `integration/`
starts Postgres in Docker. CI runs `tests/unit` on every push and `tests/integration` in its
own job. The rules behind this tree are in `docs/engineering/testing/`.

**Navigation**

- [Running the tests](#running-the-tests)
- [Where a new test goes](#where-a-new-test-goes)
- [What each folder holds](#what-each-folder-holds)

## Running the tests

| Command | Runs |
|---|---|
| `uv run pytest tests/unit` | the unit suite, in seconds |
| `uv run pytest tests/integration` | the integration suite; Docker must be running |
| `uv run pytest tests/*/<module> tests/*/*/*_<module>*` | one module in every suite, its adapter tests included (leave out the second pattern while it has none): run it before you push a change to it |
| `uv run pytest -n auto` | everything in parallel; needs pytest-xdist installed |
| `uv run pytest -m live_model` | the tests that call a real model; they cost money |

## Where a new test goes

A test of `src/shop/<domain>/<module>/<file>.py` goes to `tests/<suite>/<module>/test_<file>.py`,
in the file's one `Test<Unit>` class. `unit/` if it needs nothing outside Python, `integration/`
if it needs the database or the network.

## What each folder holds

- `unit/`, `integration/`: one folder per module, one per `core` and per adapter.
- `support/`: fakes and test-data helpers that several test files import. No tests, no fixtures.
- `conftest.py` files: fixtures, placed as `docs/engineering/testing/fixtures.md` section 4 says.
```

It is good because a newcomer finds the three things they came for, how to run, where a file goes
and what the folders are, and no rule is copied: the last line of the first paragraph sends them to
the practice ([layout.md](layout.md) section 8). The folder list names kinds, never files, so it
stays true when a module is added.

## tests/CLAUDE.md

```markdown
# Tests: the rules a change must not break

For how to run the suites and where a file goes, read `tests/README.md`. Each line below points
at the section that owns the rule, in `docs/engineering/testing/`.

- A test file sits in a folder below `tests/unit/` or `tests/integration/`; only a guarantee
  file may sit directly in a suite folder, and none directly under `tests/`.
  → `layout.md` sections 1 and 5
- One `Test<Unit>` class per file. → `layout.md` section 4
- Every fixture states `scope=`; never `autouse`. → `fixtures.md` sections 1 and 2
- No bare `Mock()` and no `mock.patch`. → `fakes-and-boundaries.md` section 1, `fixtures.md` section 6
- Never write the marks `unit`, `integration` or `enable_socket`; the hook sets them.
  → `running-tests.md` section 2, `fakes-and-boundaries.md` section 4
- A test that calls a real model is marked `live_model`. → `running-tests.md` section 10
```

It is good because each line is a rule whose break shows in a diff, and each points to its owner
instead of restating it: when a rule changes, its line changes in the same commit and says nothing
the rule does not.

## tests/integration/conftest.py: one database for the run

```python
"""What the integration suite shares: one Postgres container per run, emptied after each
test."""

from collections.abc import Iterator
from typing import Final

import pytest
from sqlalchemy import Engine, create_engine
from testcontainers.community.postgres import PostgresContainer

from shop.core.database import Database

# The major version production runs, so a query that works here works there.
POSTGRES_IMAGE: Final = "postgres:17-alpine"


def apply_migrations(engine: Engine) -> None:
    """Create the application's tables with its own migrations."""
    ...  # left out: the project's migration tool, pointed at this engine


def empty_tables(db: Database) -> None:
    """Delete every row, so the next test starts from empty tables."""
    ...  # left out: one TRUNCATE of every application table


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    """One Postgres container for the run; stopped after the last test."""
    with PostgresContainer(POSTGRES_IMAGE, driver="psycopg") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture(scope="session")
def migrated_database(postgres_url: str) -> Iterator[Database]:
    """The database with the application's tables, built once for the run."""
    engine = create_engine(postgres_url)
    apply_migrations(engine)

    yield Database(engine)

    engine.dispose()


@pytest.fixture(scope="function")
def database(migrated_database: Database) -> Iterator[Database]:
    """The run's database, emptied after each test so no test sees another's rows."""
    yield migrated_database

    empty_tables(migrated_database)
```

It is good because each fixture holds one resource and states how long it lives
([fixtures.md](fixtures.md) sections 1 and 5). The two helpers serve this file alone, so they sit
in it, their bodies left out ([layout.md](layout.md) section 7); the tables come from the
migrations the application runs, so the test database cannot drift from the real one. Starting a
container and running migrations is the slowest thing in the suite, so they live for the session;
the rows are what tests change, so the function-scoped `database` puts them back after every
test, whether it passed or not
([fixtures.md](fixtures.md) section 3). Every integration module can ask for `database`, which is
why it sits in the suite's `conftest.py` ([fixtures.md](fixtures.md) section 4). Under
pytest-xdist each worker gets its own container, which keeps the workers apart
([running-tests.md](running-tests.md) section 8).

## The integration test of the reminder run

`tests/integration/remind_overdue_invoice/test_usecase.py`

```python
"""The reminder run against a real database, with the mail provider faked."""

from datetime import date
from decimal import Decimal
from typing import Final

import pytest

from shop.billing.remind_overdue_invoice.repository import get_invoice
from shop.billing.remind_overdue_invoice.schemas import Invoice, InvoiceId
from shop.billing.remind_overdue_invoice.usecase import remind_overdue_invoice
from shop.core.database import Database
from tests.support.fake_mailer import FakeMailer

DUE_ON: Final = date(2026, 9, 1)
# Nine days past due, never reminded: the rule says a reminder is due.
TODAY: Final = date(2026, 9, 10)


def an_invoice(*, last_reminded_on: date | None = None) -> Invoice:
    """An overdue invoice; a test sets only the date it is about."""
    return Invoice(
        invoice_id=InvoiceId("INV-1001"),
        customer_email="jane.doe@example.com",
        amount=Decimal("120.00"),
        due_on=DUE_ON,
        last_reminded_on=last_reminded_on,
    )


def insert_invoice(db: Database, invoice: Invoice) -> None:
    """Store an invoice the way the application's tables hold it."""
    ...  # left out: one INSERT into the invoices table


@pytest.fixture(scope="function")
def mailer() -> FakeMailer:
    """A mailer that keeps what it was asked to send, new for each test."""
    return FakeMailer()


@pytest.fixture(scope="function")
def overdue_invoice_id(database: Database) -> InvoiceId:
    """One overdue invoice, stored in this test's database."""
    invoice = an_invoice()
    insert_invoice(database, invoice)

    return invoice.invoice_id


class TestRemindOverdueInvoice:
    """An overdue invoice gets exactly one reminder email, recorded on the invoice."""

    def test_an_overdue_invoice_gets_one_reminder_email(
        self, database: Database, mailer: FakeMailer, overdue_invoice_id: InvoiceId
    ) -> None:
        remind_overdue_invoice(overdue_invoice_id, TODAY, database, mailer)

        assert [email.to for email in mailer.sent] == ["jane.doe@example.com"]

    def test_the_reminder_is_recorded_on_the_invoice(
        self, database: Database, mailer: FakeMailer, overdue_invoice_id: InvoiceId
    ) -> None:
        remind_overdue_invoice(overdue_invoice_id, TODAY, database, mailer)

        assert get_invoice(database, overdue_invoice_id) == an_invoice(
            last_reminded_on=TODAY
        )

    def test_a_second_run_on_the_same_day_sends_no_second_email(
        self, database: Database, mailer: FakeMailer, overdue_invoice_id: InvoiceId
    ) -> None:
        """A retried job must not mail the customer twice for one invoice."""
        remind_overdue_invoice(overdue_invoice_id, TODAY, database, mailer)
        sent_by_first_run = list(mailer.sent)

        remind_overdue_invoice(overdue_invoice_id, TODAY, database, mailer)

        assert mailer.sent == sent_by_first_run
```

It is good because:

- **One class for the one unit the act steps call**, `remind_overdue_invoice`, in the file named
  for its source file ([layout.md](layout.md) sections 3 and 4), and each test name is the sentence
  that breaks ([test-structure.md](test-structure.md) section 3).
- **One behavior per test** ([test-structure.md](test-structure.md) section 4): the email, the
  record and the repeat each fail on their own line.
- **Every fixture states its scope and is asked for by name** ([fixtures.md](fixtures.md) sections
  1 and 2). `mailer` and `overdue_invoice_id` serve this file alone, so they sit in it; `database`
  comes from the suite's `conftest.py`. The builder `an_invoice` and `insert_invoice`, its body
  left out, serve this file alone too, so they sit in it ([layout.md](layout.md) section 7).
- **The assertions compare exact values** ([assertions.md](assertions.md) sections 1 and 2): the
  list of recipients, and the whole stored invoice built by the same builder with the one field
  the run changed.
- **The mail provider is a fake that records data** ([fakes-and-boundaries.md](fakes-and-boundaries.md)
  sections 1 and 2); the database is real, because the queries are part of what the run does.
- **The third test's docstring gives the consequence** the name cannot
  ([test-structure.md](test-structure.md) section 5). Its first run is the arrange step and records
  what was sent; the second is the act the guarantee is about, and the assertion checks that it
  added nothing. A first run that sends no email turns the first test red, not this one.

## Running it

```text
# the module in both suites, its CLI command's test included
uv run pytest tests/*/remind_overdue_invoice tests/*/*/*_remind_overdue_invoice*
uv run pytest tests/unit                         # the unit suite, as CI runs it on every push
uv run pytest tests/integration                  # the integration suite, CI's own job for it
uv run pytest -n auto                            # everything in parallel, with pytest-xdist
```

## What this example does not claim

- **The integration test was not run here.** It needs Docker and the service's migrations, which
  the example leaves out. The hook, the configuration block and the Python files were checked
  with ruff and mypy in strict mode on stand-in modules for the service; the hook also ran on
  pytest 9.1.1 as described above.
- **One container per worker is a choice.** A suite with many workers and a slow database start
  may share one container per run with pytest-xdist's file-lock recipe
  ([running-tests.md](running-tests.md) section 8).
