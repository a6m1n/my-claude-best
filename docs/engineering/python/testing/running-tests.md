# Running tests

The configuration a pytest suite carries and what a test owes it: the keys, the marks, how to run
one part of the suite, warnings, order, time, async code, parallel runs, flaky tests, the tests
that ask a real model, and the static checks on the tests themselves. Which libraries provide the
plugins named here, and when each is worth adding, is [libraries.md](libraries.md).

**Navigation**

- [1. The configuration block](#1-the-configuration-block)
- [2. Markers](#2-markers)
- [3. Running one part of the suite](#3-running-one-part-of-the-suite)
- [4. Warnings are errors](#4-warnings-are-errors)
- [5. Order independence](#5-order-independence)
- [6. Clocks and waiting](#6-clocks-and-waiting)
- [7. Async tests](#7-async-tests)
- [8. Parallel runs](#8-parallel-runs)
- [9. Flaky tests and timeouts](#9-flaky-tests-and-timeouts)
- [10. Tests that ask a real model](#10-tests-that-ask-a-real-model)
- [11. Static checks on the tests](#11-static-checks-on-the-tests)
- [12. Where it stops holding](#12-where-it-stops-holding)
- [13. Sources](#13-sources)

## 1. The configuration block

**Keep the whole pytest configuration in `pyproject.toml`, in the `[tool.pytest]` table**, which
pytest reads since 9.0 with TOML's own types: a list is a list, a flag is `true`. Never keep it
next to the older `[tool.pytest.ini_options]` table in the same file: pytest stops with an error.
When you add a key to the block, add its row to the table of reasons below it in the same edit.
`[tool.pytest]` needs pytest 9.0 or newer as a development dependency, locked with the rest:
pytest 8 does not read `[tool.pytest]` at all and would run with no configuration, so a version
floor inside it could never fire.

```toml
[tool.pytest]
testpaths = ["tests"]
# --allow-unix-socket keeps asyncio's internal socket pair and a local Docker socket
# working (fakes-and-boundaries.md section 4).
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
required_plugins = ["pytest-asyncio", "pytest-randomly", "pytest-socket"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
asyncio_default_test_loop_scope = "function"
```

With no async code, drop the three `asyncio_*` keys and `pytest-asyncio`; on anyio, write
`anyio_mode = "auto"` and put `anyio` in `required_plugins` instead (section 7).

| Key | Why |
|---|---|
| `testpaths` | a bare `pytest` collects `tests/` and nothing else; a path on the command line still wins |
| `-ra` | the summary lists every test that did not pass, so a skip or an xfail is on the last screen, not hidden in a count |
| `--disable-socket`, `--allow-unix-socket` | the network is blocked for every test; `tests/conftest.py` opens it for `integration/` ([fakes-and-boundaries.md](fakes-and-boundaries.md) section 4) |
| `-m "not live_model"` | no default run calls a real model (section 10); a `-m` on the command line replaces it |
| `markers` | every mark this project uses, with what it means or costs (section 2) |
| `strict_config` | a key pytest does not know, such as a plugin's key whose plugin is missing, is an error |
| `strict_markers` | a mark not in `markers` is an error, so a typo in a mark does not silently select nothing |
| `strict_parametrization_ids` | two rows with one id are an error, not a silent number suffix ([test-structure.md](test-structure.md) section 6) |
| `strict_xfail` | an `xfail` test that passes fails the run, so a fixed bug does not hide behind an old mark |
| `filterwarnings` | a warning fails the test that raised it (section 4) |
| `required_plugins` | the run stops at startup when a plugin that a key or a rule here depends on is missing, so the order check of section 5 cannot quietly stop running |
| `asyncio_*` | one async plugin, and each loop scope written down (section 7) |

The four `strict_*` keys are written one by one rather than as `strict = true`. `strict` turns on
the same four today, but pytest's reference warns that later versions may add checks under it, so
a pytest upgrade could fail a suite for a reason nobody chose. The pytest version is pinned in the
lock file, so the upgrade that adds a check is the moment to decide on it.

`-n` for parallel runs is not in `addopts` (section 8).

## 2. Markers

A marker is pytest's tag: a name on a test that `-m` selects by. Two kinds exist here.

- **The suite marks, `unit` and `integration`, are set by the hook in `tests/conftest.py`**, from
  the folder the test sits in, never written by hand. `-m unit` then selects exactly what
  `tests/unit` holds, and a moved file cannot keep a stale mark. Check:
  `grep -rnE "mark\.(unit|integration)\b" tests/` prints nothing.
- **A `-m` on the command line replaces the one in `addopts`, so a selection by suite mark repeats
  the exclusion**, `-m "integration and not live_model"`; `-m integration` alone also runs the
  paid tests of section 10.
- **A mark of your own, such as `live_model`, is declared in `markers` with what it costs.**

## 3. Running one part of the suite

The layout of [layout.md](layout.md) gives each module one folder per suite, so a path selects
exactly one part:

```text
pytest tests/unit                                        # the unit suite
pytest tests/unit/remind_overdue_invoice                 # one module in one suite
pytest tests/*/remind_overdue_invoice                    # one module's folder in every suite
pytest tests/unit/remind_overdue_invoice/test_reminder_rules.py::TestNeedsReminder
pytest -k "overdue and not interval"                     # by substrings of the names
pytest -m "not integration"                              # by mark
pytest --collect-only -q                                 # the ids, nothing is run
pytest --lf                                              # only the tests that failed last time
```

- **When you work on one module, run its tests in every suite before you push**:
  `pytest tests/*/<module> tests/*/*/*_<module>*`. The shell expands the first pattern to the
  module's folder in each suite and the second to its adapter tests, such as
  `tests/integration/api/test_routes_<module>.py`, or `tests/integration/api/routes_<module>/`
  once that file is a folder ([layout.md](layout.md) section 4). The second pattern also matches
  any other name that holds `_<module>`, such as the adapter tests of a module named
  `overdue_<module>`, so it may run a few tests more. While the module has no adapter test, leave
  the second pattern out: a pattern that matches no file is an error. CI still runs the whole
  suite before a merge.
- **Select by path first.** A path is exact: it runs one folder and nothing else.
- **`-k` matches substrings, case-insensitively, in the names of the test, its class, its file and
  its folders.** Folder names match too, in pytest 9.1's source and in a run, though the
  documentation names only the file and the class. `-k invoice` therefore also picks up every test
  in any other module with "invoice" in a name. A `-k` that matches nothing exits with code 5, "no
  tests ran": that is a selector that found nothing, not a broken suite.

## 4. Warnings are errors

**Keep `"error"` first in `filterwarnings`, and add at most one narrow ignore per warning**, each
with a comment that says why it cannot be fixed in this code and what event removes the line.
pytest applies the last filter that matches, so `"error"` first with narrow ignores after it means
each ignore covers exactly the warning it names.

```toml
# Bad: a whole category disappears, including the warning nobody has seen yet.
filterwarnings = ["error", "ignore::DeprecationWarning"]

# Good: one message, one category, one module, and the two facts that let a reader delete it.
filterwarnings = [
    "error",
    # acme_sdk calls a deprecated datetime API at import; not ours to fix.
    # Remove when acme_sdk ships the release its issue names.
    "ignore:datetime.datetime.utcnow:DeprecationWarning:acme_sdk",
]
```

Turning warnings into errors in a suite that already emits some makes them failures the same day:
fix what is yours first, then write the narrow ignores for the rest.

## 5. Order independence

**Write every test so that it passes in any order and leaves nothing behind**: no module-level
object a test changes, no file written outside `tmp_path`, no state on the class
([test-structure.md](test-structure.md) section 2).

The check is pytest-randomly: it shuffles the order of modules, classes and tests on every run and
reseeds `random` for each test, and it prints the seed it used in the run's header. To repeat a
failed order, run with `--randomly-seed=<n>`. To see whether the order matters at all, run
with `--randomly-dont-reorganize`, which keeps the plugin and runs the tests in file order;
`-p no:randomly` does not work here, because `required_plugins` refuses a run without the plugin.
Under pytest-xdist every worker gets the same seed.

## 6. Clocks and waiting

- How a test controls the time is [readability.md](../../any-language/readability/readability.md) section 6 (a
  value the unit takes) and [fakes-and-boundaries.md](fakes-and-boundaries.md) section 3
  (time-machine, when a library reads the clock itself).
- **Never sleep to reach a point in time.** Wait on the event the other side sets, with a timeout:
  `assert worker_started.wait(timeout=WORKER_START_TIMEOUT_SECONDS)`. A sleep that stays names its
  window as a constant whose comment says what it waits for.

## 7. Async tests

**Run async tests through one plugin in auto mode, never two.** In auto mode an `async def test_`
needs no mark, and neither does an async fixture.

| Plugin | Use it when | Key |
|---|---|---|
| pytest-asyncio | the code runs on asyncio | `asyncio_mode = "auto"` |
| anyio's pytest plugin | the code uses anyio, or must run on trio too | `anyio_mode = "auto"`, anyio 4.11 or newer |

anyio's documentation: "This does not work if `pytest-asyncio` is installed and configured to use
its own `auto` mode, as it will conflict with the AnyIO plugin." With anyio, define your own
`anyio_backend` fixture that returns one backend; the default one runs every test once per
backend it finds.

- **Write both loop scopes in the configuration**, `asyncio_default_fixture_loop_scope` and
  `asyncio_default_test_loop_scope`, as `"function"`: pytest-asyncio's documentation says the
  default for fixtures will change, and a written value does not. It is the same reason every
  fixture states its scope ([fixtures.md](fixtures.md) section 1).
- **An async fixture wider than a function states its loop scope too, at least as wide as its
  scope**: "the event loop scope must be larger or the same as the fixture's caching scope."

  ```python
  @pytest_asyncio.fixture(scope="session", loop_scope="session")
  async def search_client() -> AsyncIterator[httpx.AsyncClient]:
      """One HTTP client for the run, closed after the last test."""
      async with httpx.AsyncClient(base_url=SEARCH_BASE_URL) as client:
          yield client
  ```

  A test that uses an object bound to that loop, such as this client, runs in the same loop:
  `@pytest.mark.asyncio(loop_scope="session")` on its class. Mixing loops is a likely source of
  errors that pytest-asyncio's documentation does not spell out, so keep a session-loop fixture
  and its tests together.
- **With anyio, an async fixture wider than a function needs an `anyio_backend` fixture of the
  same scope**, "because the default `anyio_backend` fixture is function scoped."

## 8. Parallel runs

pytest-xdist splits the tests over worker processes. Each worker is a full pytest run: it reads
the same configuration and collects the whole tree.

- **Pass `-n` only where the whole suite runs**, such as the CI job or the one command that runs the
  full suite, never in `addopts`. Otherwise a run of one test pays for several worker startups and
  full collections.
- **A session fixture runs once per worker, not once per run**: "tests in different processes
  requesting a high-level scoped fixture (for example `session`) will execute the fixture code more
  than once." One database container per worker is usually fine. When something must happen once
  per run, use the recipe in pytest-xdist's how-to: `tmp_path_factory.getbasetemp().parent`, a
  file lock from the `filelock` package, and the `worker_id` fixture. `testrun_uid` is one value
  for the whole run.
- **Never bind a fixed port and never write outside `tmp_path`.** Each worker has its own
  `tmp_path` root; a port number and a path in the repository are shared. A test server binds
  port `0` and lets the system choose.
- **When a test fails only under `-n`, run its id again with `-n0` before you change the test.**
  Red under `-n0` is a real defect; green under `-n0` means two tests share something, section 5's
  rule is broken, and a retry would hide it.

## 9. Flaky tests and timeouts

**When a test that does not call a real model fails once and passes on the next run, find the
cause and fix the test; never give it a retry.** Without a real model in the loop a flaky test
has a cause: an order (section 5), a clock (section 6), or a path or a port two tests share
(section 8). Repeat the failed run with its seed, and read a retry mark on a test that does not
call a real model as the defect itself.

- **pytest-rerunfailures is only for a test that asks a real model and whose pass rule is any of
  n** (section 10), and only on the command line of that run,
  `pytest -m live_model --reruns 2 -raR tests/integration/<module>`: never
  `reruns` in the configuration and never `@pytest.mark.flaky` on a test, which would give the
  tests that do not call a real model retries too. `-raR` prints a `RERUN` line for each retry,
  which `-ra` does not; section 10 reads each one as a wrong answer. A rerun repeats the test
  alone: "fixtures that have already completed setup remain cached at their scope."
- **Give the integration job a timeout with pytest-timeout**, `pytest tests/integration
  --timeout=120`, so a hung call fails the job instead of stalling it. The default `signal` method
  "may interfere with the code under test" if that code uses `SIGALRM`; the `thread` method "will
  terminate the whole process". The timeout also covers fixture setup, such as starting a container,
  unless `timeout_func_only` is set, so size it for the slowest setup.

## 10. Tests that ask a real model

A test whose subject is what a real model answers is the one kind of test that costs money on
every run and does not give the same result twice. Evaluating a prompt, a model or a setting
against a case set is [prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md)
section 18; this section is how such a test runs under pytest.

- **Mark it `live_model` and put it in `integration/`.** The exclusion in `addopts` keeps it out of
  every default run; a person runs it on purpose: `pytest -m live_model tests/integration/triage`.
- **Turn the cache switch on in the fixture that builds the client.** The switch belongs to
  [prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 17: with it on, the
  one model client puts a fresh request UUID at the start of every system prompt, so no cache
  answers instead of the model. A test that repeats a call, or reruns after a wrong answer, needs
  each answer to come from the model. The client makes a new UUID on every call, so the client
  itself can live for the session.
- **The fixture reads the real key from the environment of the person who runs it**, by building
  `Settings()` as the application does. That is the exception [python.md](../language/python.md)
  section 5 makes, under "Where it stops holding", for a test marked to call a real model.
- **Run a check with `--reruns` only when its pass rule is any of n.** The test below names its
  pass rule, as [repeated-runs.md](../evals/repeated-runs.md) section 4 asks: all of 1, one call
  per ticket that must be right. A retry changes the rule: `--reruns 2` on the command line makes
  every check in the run any of 3, so a prompt right one time in two still passes nearly nine runs
  in ten. Each `RERUN` line under `-raR` is a wrong answer; `-ra` prints none. To run a case more
  than once, count its passes in a loop ([repeated-runs.md](../evals/repeated-runs.md) section 5).

```python
# tests/integration/triage/test_service_triage.py
CRASH_ON_EXPORT: Final = "Since yesterday the CSV export crashes with error 500."
DARK_MODE_WISH: Final = "Please add a dark mode to the dashboard."


@pytest.fixture(scope="session")
def uncached_model_client() -> AcmeAiClient:
    """The one model client with the cache switch on: every call reaches the model."""
    # The run is by hand with the key of the person who runs it; only live_model tests
    # ask for this fixture, so no default run reads the environment.
    settings = Settings()
    return AcmeAiClient(
        AcmeAiSdk(api_key=settings.acme_ai_api_key.get_secret_value()),
        disable_prompt_cache=True,
        new_request_uuid=uuid.uuid4,
    )


@pytest.mark.live_model
class TestTriageTicket:
    """The triage call files a ticket under its kind."""

    @pytest.mark.parametrize(
        ("ticket_text", "kind"),
        [
            pytest.param(CRASH_ON_EXPORT, TicketKind.BUG, id="crash-on-export"),
            pytest.param(
                DARK_MODE_WISH, TicketKind.FEATURE_REQUEST, id="dark-mode-wish"
            ),
        ],
    )
    def test_a_ticket_is_filed_under_its_kind(
        self, ticket_text: str, kind: TicketKind, uncached_model_client: AcmeAiClient
    ) -> None:
        triage = triage_ticket(
            ticket_text,
            uncached_model_client,
            model=TRIAGE_LLM_MODEL,
            reasoning_effort=TRIAGE_LLM_REASONING_EFFORT,
        )

        # Pass rule: all of 1, so run it without --reruns (repeated-runs.md section 4).
        assert triage.kind is kind
```

It is good because the fixture sits in the test file, the one file that asks for it
([fixtures.md](fixtures.md) section 4), and the pass rule is named at the assertion, where a reader
who reaches for `--reruns` sees it. The client, the settings field and the triage call are those of
[prompt-example.md](../../any-language/prompt-engineering/prompt-example.md); `acme_ai_api_key` stands for the
vendor key field its settings class leaves out. The two tickets are invented; a real case set is
built from real tickets, the way [evals.md](../evals/evals.md) section 4 says.

## 11. Static checks on the tests

Tests are code, and the checks of [static-checks.md](../static-checks/static-checks.md) run on
them: the type checker in strict mode reads `tests/` as it reads `src/`.

- **Select ruff's pytest rules, `PT`, and turn off `PT003`**, which reports the
  `scope="function"` this practice asks for ([fixtures.md](fixtures.md) section 1). The comment
  next to the setting names that section, as static-checks section 2 asks.
  [python/static-checks/setup-example.md](../static-checks/setup-example.md) shows the lines.
- **The rules no linter checks have a hand-run check**, on the `Check:` line next to each rule in
  this practice. Run them over the diff before you stage.

## 12. Where it stops holding

- **A project on pytest 8 or older** keeps `[tool.pytest.ini_options]`, where values are strings
  (`addopts = "-ra --disable-socket"`), and spells `strict_xfail` as `xfail_strict`. The
  `strict_config` and `strict_markers` keys arrived in 9.0, so it puts `--strict-config` and
  `--strict-markers` in `addopts` instead; it has no `strict_parametrization_ids`.
- **A script run once** needs none of this; its test, if it has one, is a file next to it.

## 13. Sources

pytest documentation: "Configuration" and the configuration reference (the `[tool.pytest]` table,
`strict` and the four `strict_*` options, `required_plugins`, `filterwarnings`), "How to capture
warnings", "Working with custom markers", "Usage and Invocations" (`-k`, `-m`, node ids, exit
code 5), the 9.0 and 9.1 changelogs; pytest source at 9.1.1, `src/_pytest/config/findpaths.py`
(the two tables) and `src/_pytest/mark/__init__.py` (`-k` and folder names). pytest-asyncio
documentation: configuration (`asyncio_mode`, the two loop-scope defaults), the fixture
decorator's `loop_scope`, the markers reference. anyio documentation, "Testing with AnyIO".
pytest-xdist documentation, "How-to" (session fixtures per worker, the file-lock recipe,
`worker_id`, `testrun_uid`). pytest-randomly README and source (the seed handed to xdist
workers). pytest-rerunfailures README. pytest-timeout README. pytest-socket README.
