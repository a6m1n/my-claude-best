# Fixtures

Where the setup of a test comes from: how long each object lives, who asks for it, where it is
written, and how a fixture puts back what it changed. The one rule here is the Zen of Python's
"Explicit is better than implicit": a reader of a test sees every fixture it uses and how long
each one lives, without opening pytest's documentation.

**Navigation**

- [1. Every fixture states its scope](#1-every-fixture-states-its-scope)
- [2. No autouse: a test names what it uses](#2-no-autouse-a-test-names-what-it-uses)
- [3. Choosing the scope](#3-choosing-the-scope)
- [4. Where a fixture lives](#4-where-a-fixture-lives)
- [5. Setup and teardown with yield](#5-setup-and-teardown-with-yield)
- [6. Patch and undo](#6-patch-and-undo)
- [7. Factories](#7-factories)
- [8. Parametrized fixtures](#8-parametrized-fixtures)
- [9. Types](#9-types)
- [10. Where it stops holding](#10-where-it-stops-holding)
- [11. Sources](#11-sources)

## 1. Every fixture states its scope

**When you write a fixture, write its scope, `scope="function"` included**:
`@pytest.fixture(scope="function")`. pytest's default is `function`, but a default is something
the reader has to know. With the scope on every decorator, two fixtures side by side show at once
which one is rebuilt for each test and which one lives for the whole run, and a wider scope stands
out in review.

```python
# Bad: the reader has to know pytest's default to learn how long the fake lives.
@pytest.fixture
def mailer() -> FakeMailer:
    """A mailer that keeps what it was asked to send instead of sending it."""
    return FakeMailer()


# Good: the lifetime is on the line. A new fake for each test, so no test sees another's
# mail.
@pytest.fixture(scope="function")
def mailer() -> FakeMailer:
    """A mailer that keeps what it was asked to send instead of sending it."""
    return FakeMailer()
```

ruff's `PT003` reports exactly this `scope="function"` as unneeded, and no ruff rule asks for a
scope, so a project that selects the `PT` rules turns `PT003` off and the check below is a grep
([running-tests.md](running-tests.md) section 11).

Check: `grep -rnE '@pytest(_asyncio)?\.fixture\b' --include='*.py' tests/ | grep -v 'scope='`
prints nothing but the first line of a decorator split over several lines, whose `scope=` you
read in the diff.

## 2. No autouse: a test names what it uses

An `autouse` fixture runs for tests that never asked for it. Its setup is invisible from the test:
a reader cannot find why the environment differs, and a fixture placed in the root `conftest.py`
reaches every suite, including one that must not have it.

**Never write `autouse=True`.** A test gets a fixture in one of two visible ways:

- **As an argument, when the test uses the value.** `def test_...(self, mailer: FakeMailer)`.
- **Through `@pytest.mark.usefixtures("<name>")` on the class, when the tests need the effect but
  not the value**, such as a fixture that patches a library (section 6). One line above the class
  names it for every test in the file.

**A guard that must hold for every test is configuration, not a fixture.** Keeping the unit suite
offline is `--disable-socket` in the configuration ([fakes-and-boundaries.md](fakes-and-boundaries.md)
section 4); failing on a warning is `filterwarnings = ["error"]`
([running-tests.md](running-tests.md) section 4). Configuration holds for every test with nothing
to forget, and it is written down in one place.

`usefixtures` never goes on a fixture function: pytest 9 fails on a mark applied to a fixture, and
ruff's `PT025`, on by default, reports it. A fixture that needs another asks for it as an argument.

Check: `grep -rn "autouse" --include='*.py' tests/` prints nothing.

## 3. Choosing the scope

pytest tears a fixture down at the end of its scope: after the test, or after the last test of
the module, the package or the session. A wider scope shares one object across tests in an order
nobody chose.

**Leave a fixture at `function` scope unless the object is expensive to build and no test can
change it.**

| Scope | Use it for | Example |
|---|---|---|
| `function` | anything a test can change: a fake that records calls, a list, an object with state | `FakeMailer` |
| `module` (one test file) | an expensive object the tests of one file share and never change | a large parsed sample file |
| `session` | an expensive resource the whole run shares, whose object never changes | a database container and its URL |

- **Never `class` scope.** A file holds one class ([layout.md](layout.md) section 4), so `class`
  and `module` scopes last exactly as long; `module` says it plainly.
- **A shared resource whose contents tests change gets a function-scoped fixture that puts it
  back.** The database container lives for the session; a function-scoped fixture empties its
  tables after each test ([suite-example.md](suite-example.md) shows the pair).
- **A wider fixture cannot ask for a narrower one**: pytest stops with a `ScopeMismatch`. A session
  fixture that needs a folder takes `tmp_path_factory`, "a session-scoped fixture which can be used
  to create arbitrary temporary directories from any other fixture or test"; one that patches uses
  `pytest.MonkeyPatch.context()` (section 6).
- **Session means once per worker under pytest-xdist**, not once per run
  ([running-tests.md](running-tests.md) section 8).

Check: every fixture wider than `function` returns an object no test changes, or is paired with a
function-scoped fixture that resets what the tests change.

## 4. Where a fixture lives

A fixture climbs a ladder, and only as far as it must:

| Level | File | Who can ask for it |
|---|---|---|
| the test file | a module-level function above the class | the one class in the file |
| the module's folder | `tests/<suite>/<module>/conftest.py` | every test file of that module in that suite |
| the suite | `tests/<suite>/conftest.py` | every test of the suite |
| the tree | `tests/conftest.py` | every test |

- **Start in the test file.** When a second file needs the fixture, move it to the lowest
  `conftest.py` both files can see, and delete the first copy in the same edit. Two copies drift
  on the first edit to one of them. Check: `grep -rn "def <name>(" tests/` prints one line, or one
  line per suite for a fixture whose body only calls a `tests/support/` builder.
- **A fixture for a resource the whole suite shares, such as a database container, starts in the
  suite's `conftest.py`**, not in the first test file that asks for it.
- **A fixture both suites of one module need never climbs to `tests/conftest.py`.** The builder
  goes in `tests/support/`, and each suite's `<module>/conftest.py` holds a one-line fixture that
  calls it.
- **A fixture is never a method of the test class.** With one class per file, a module-level
  fixture is already private to that class. A class-scoped fixture written as a method without
  `@classmethod` is deprecated since pytest 9.1.
- **A fixture never lives in `tests/support/`**: that package is imported, not requested
  ([layout.md](layout.md) section 7). A fake lives there; the fixture that builds it lives in a
  `conftest.py`.
- **A fixture with the name of one flow stays near that flow.** `mailer` means one kind of fake
  and may climb; `overdue_invoice` means one module's data and stays in that module's folder.

## 5. Setup and teardown with yield

**When a fixture opens something that must be closed, write it as a generator: set up, `yield`
the object, then clean up.** pytest runs the code after `yield` when the scope ends, also when the
test failed.

```python
POSTGRES_IMAGE: Final = "postgres:17-alpine"


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    """One Postgres container for the whole run; stopped after the last test."""
    with PostgresContainer(POSTGRES_IMAGE, driver="psycopg") as postgres:
        yield postgres.get_connection_url()
```

- **Use the resource's own context manager** inside the fixture when it has one, as above: its
  exit path is the tested one.
- **One resource per fixture.** When one fixture opens two things and the first cleanup fails, the
  second never runs; two fixtures clean up independently. pytest's docs call this the safest
  structure: "limiting fixtures to only making one state-changing action each, and then bundling
  them together with their teardown code".
- **A generator fixture is annotated `Iterator[<the type it yields>]`** (section 9).

## 6. Patch and undo

A test often needs something replaced for its duration and put back after: "mock and unmock".
There are two ways, and the first is better whenever it is open.

**Pass the stand-in in.** When the code under test takes the object as a parameter, as
[readability.md](../readability/readability.md) section 6 asks, the fixture builds the stand-in
and the test passes it. Nothing global changes, so there is nothing to undo. pytest's own page on
patching puts this first: "For code that you control, a safer long-term pattern is to make
dependencies explicit so they can be passed into the code under test instead of patched
globally." Which stand-in to build is [fakes-and-boundaries.md](fakes-and-boundaries.md)
section 1.

**Patch in a fixture, with `monkeypatch`, when the code reads a name you cannot pass**: an
environment variable, or an attribute of a library you do not own. `monkeypatch` records each
change and reverts it: "All modifications will be undone after the requesting test function or
fixture has finished." The tests of the settings class do this
([python/settings-example.md](../python/settings-example.md)): their fixture removes the
machine's own `ACME_` variables and sets the valid ones, and each test removes or changes the
variables its case needs.

A patch more than one test needs goes in a fixture; a test that needs one change once may call
`monkeypatch` itself. Check: every `monkeypatch` or `MonkeyPatch.context` line sits inside a
fixture or a test, never at module level.

- **`monkeypatch` is function-scoped**, and so is a fixture that asks for it:

  ```python
  @pytest.fixture(scope="function")
  def sdk_without_retries(monkeypatch: pytest.MonkeyPatch) -> None:
      """acme_sdk retries a failed call five times; these tests want the first error."""
      # acme_sdk takes no retry argument, so the module default is the only way in.
      monkeypatch.setattr("acme_sdk.DEFAULT_RETRIES", 0)


  @pytest.mark.usefixtures("sdk_without_retries")
  class TestSearchClient:
      """A failed search raises the first error the SDK returns."""

      ...
  ```

- **A patch that must last for a module or the session is a `yield` fixture around
  `pytest.MonkeyPatch.context()`.** pytest's reference gives this form for a place with no
  `monkeypatch` fixture: "use with MonkeyPatch.context() as mp: or remember to call undo()
  explicitly". The `with` block puts the value back when the scope ends, and also when a line
  between the patch and `yield` raises:

  ```python
  @pytest.fixture(scope="module")
  def sdk_without_retries_for_module() -> Iterator[None]:
      """No retries for the module's shared client; monkeypatch cannot reach this scope."""
      with pytest.MonkeyPatch.context() as patch:
          patch.setattr("acme_sdk.DEFAULT_RETRIES", 0)
          yield
  ```

- **`with mock.patch(...): yield` and `with mock.patch.dict(os.environ, ...): yield` are the same
  form with `unittest.mock`**, the one Adam Johnson shows in "How to Mock Environment Variables in
  pytest" (2020). Its undo is as safe as the `MonkeyPatch.context()` form, because the `with`
  block's exit runs either way. It is out here only for the reasons of the bullet "Never
  `unittest.mock.patch` or pytest-mock's `mocker`" below.
- **Never undo by hand after `yield`**: no saved value put back, and no `undo()` or `stop()` on
  the line after it. pytest skips that line when the fixture fails before it: "if a yield fixture
  raises an exception before yielding, pytest won't try to run the teardown code after that yield
  fixture's yield statement." A plain assignment has one more gap: with the name misspelt it
  creates a new attribute, where `setattr` raises `AttributeError`.
- **Patch the name where the code looks it up.** `from acme_sdk import DEFAULT_RETRIES` copies
  the value into the importing module, so patching `acme_sdk` does not reach it; patch each module
  that holds its own reference, and say in one comment why the lines differ.
- **Set a stand-in, never a bare `MagicMock()`.** What `setattr` puts in is one of the stand-ins
  of [fakes-and-boundaries.md](fakes-and-boundaries.md) section 1: a fake, or
  `create_autospec(...)`. A rule against `unittest.mock.patch` followed by
  `monkeypatch.setattr(target, "name", MagicMock())` keeps the mock and loses its spec.
- **Never patch the application's settings.** A test takes what
  [python.md](../python/python.md) section 5 names: the plain values the unit takes, or the
  `Settings` a whole-app test passes to the function that builds the app.
- **Never `unittest.mock.patch` or pytest-mock's `mocker`, in a test or in a fixture.** `patch`
  with no replacement puts in a `MagicMock` (an `AsyncMock` for an async function), where
  `setattr` always names its value. `setenv`, `delenv` and `setitem` cover the environment and
  dicts without `patch.dict`. Every patcher object also keeps its own list of what to undo: the
  `monkeypatch` fixture, each `MonkeyPatch.context()`, `mocker`, each `mock.patch`. A name patched
  through two of them can be put back in the wrong order and leak into later tests. pytest-mock's
  maintainer, on such a leak: "`mocker` is provided by `pytest-mock`, and they don't talk to each
  other". So a suite uses one patcher library, and in one test one patcher object per name: never
  the `monkeypatch` fixture and a `MonkeyPatch.context()` block on the same name. Against
  pytest-mock there is one more reason: `monkeypatch` ships with pytest, and `mocker` is one more
  dependency. pytest itself takes no side: Anthony Sottile, a maintainer, answered that "there's
  no official recommendation because it's really about opinions and trade offs". He prefers the
  `with` form of `unittest.mock` because of what he calls the "unknown scope duration" of
  `monkeypatch`; here the fixture that asks for `monkeypatch` states its scope (section 1), so how
  long a patch lasts is written down. A project that takes `unittest.mock` instead uses it alone:
  one patcher library per suite. Check:
  `grep -rnE "unittest\.mock import .*\bpatch\b|from mock import|mock\.patch|mocker\b" --include='*.py' tests/`
  prints nothing.

## 7. Factories

**Build a domain value with a module-level builder function that takes keyword overrides**, so a
test names only the field it is about. When a second test file needs it, it moves to
`tests/support/` ([layout.md](layout.md) section 7).

```python
DUE_ON: Final = date(2026, 9, 1)


def an_invoice(
    *, due_on: date = DUE_ON, last_reminded_on: date | None = None
) -> Invoice:
    """An invoice with safe defaults; a test sets only the dates it is about."""
    return Invoice(
        invoice_id=InvoiceId("INV-1001"),
        customer_email="jane.doe@example.com",
        amount=Decimal("120.00"),
        due_on=due_on,
        last_reminded_on=last_reminded_on,
    )
```

**Make it a factory fixture, one that returns a function, when building needs something only a
running test has**, such as `tmp_path` or a database. The test calls the function as often as it
needs, and the fixture's scope still governs the cleanup.

```python
@pytest.fixture(scope="function")
def add_invoice(database: Database) -> Callable[[Invoice], InvoiceId]:
    """Store an invoice in this test's database and return its id."""

    def add(invoice: Invoice) -> InvoiceId:
        insert_invoice(database, invoice)
        return invoice.invoice_id

    return add
```

For a model with many fields, polyfactory builds one from its type hints
([libraries.md](libraries.md)); a test still names the fields it is about.

## 8. Parametrized fixtures

**When every test of a file must run against several variants of one object, parametrize the
fixture, not each test.** Each test that asks for the fixture then runs once per variant, and each
variant has an id. The usual case is a contract test: the same tests over every production class
that fills one `Protocol` ([readability.md](../readability/readability.md) section 6).

```python
@pytest.fixture(
    scope="function",
    params=[
        pytest.param(DiskStore, id="disk"),
        pytest.param(SqliteStore, id="sqlite"),
    ],
)
def store(request: pytest.FixtureRequest, tmp_path: Path) -> DocumentStore:
    """Each production store in turn, so every test here runs once per store."""
    # pytest types request.param as Any; naming it once gives the rest of the body a
    # type.
    build_store: Callable[[Path], DocumentStore] = request.param
    return build_store(tmp_path)
```

**When a test's table should reach a fixture instead of the test**, such as a database prepared
in a different state per row, pass `indirect=["<fixture name>"]` to `parametrize`: pytest hands
each row to the fixture as `request.param`. Use it when the arrange step per row is heavy; a
light one stays in the test.

## 9. Types

A fixture is code, so [python.md](../python/python.md) section 3 annotates it like any function:

- **The return type is the type the test receives.** A generator fixture returns
  `Iterator[<type>]`, and one that yields nothing `Iterator[None]`.
- **pytest's own objects have public names**: `pytest.FixtureRequest`, `pytest.MonkeyPatch`,
  `pytest.TempPathFactory`, `pytest.LogCaptureFixture`, `pytest.CaptureFixture[str]`. Import
  nothing from `_pytest`.
- **`request.param` is `Any`**, because pytest's own typing of it "is still in flux". Assign it to
  a name with a type in the first line of the fixture, as in section 8. Nothing checks that the
  rows of `params` fit that annotation: the type checker takes it on trust.

## 10. Where it stops holding

- **A fixture a plugin defines**, such as pytest-asyncio's loop settings or anyio's
  `anyio_backend`, keeps the form the plugin documents ([running-tests.md](running-tests.md)
  section 7).
- **A plugin that needs `autouse` for its own mechanism**, such as a tracing plugin that wraps
  every test, is configured in its plugin, never written as an `autouse` fixture in this tree.

## 11. Sources

The Zen of Python (PEP 20). pytest documentation: "How to use fixtures" (scopes, teardown with
`yield`, `usefixtures`, "Fixtures can be parametrized", safe teardowns), "How to monkeypatch/mock
modules and environments" ("a safer long-term pattern") and the `MonkeyPatch` reference (undo
semantics, `MonkeyPatch.context()` outside the fixture since 6.2), "How to use temporary directories
and files in tests" (`tmp_path_factory`), "How to parametrize fixtures and test functions"
(`indirect`), the 9.0 and 9.1 changelogs (marks on fixtures fail; class-scoped instance-method
fixtures deprecated); pytest source at 9.1.1, `src/_pytest/fixtures.py` (the type of
`request.param`). ruff rules `PT003` and `PT025`. pytest issue #4576 (Anthony Sottile, 2020, on
`monkeypatch` and `unittest.mock`); pytest-mock issue #289 (2022, a patch leaked between the two).
Adam Johnson, "How to Mock Environment Variables in pytest" (adamj.eu, 2020). testcontainers-python
documentation (`PostgresContainer`).
