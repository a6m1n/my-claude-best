# Libraries for a pytest suite

Which library solves which problem around pytest, when it is worth adding, and what to watch for.
The rules that use these libraries are in the other files of this practice; this file is the
catalogue. It names no versions, since they change monthly: it was checked against each
project's documentation and changelog in September 2026. A version floor appears only where a
configuration key needs it.

**Navigation**

- [1. The set the configuration uses](#1-the-set-the-configuration-uses)
- [2. Add when the need appears](#2-add-when-the-need-appears)
- [3. Not by default, and why](#3-not-by-default-and-why)
- [4. Sources](#4-sources)

## 1. The set the configuration uses

The configuration block of [running-tests.md](running-tests.md) section 1 relies on these three
from the first test, and lists them in `required_plugins`.

| Need | Library | What it does | Watch for |
|---|---|---|---|
| a unit suite that never reaches the network | pytest-socket | `--disable-socket` blocks every socket a test opens; the `enable_socket` mark opens it again, set here by folder ([fakes-and-boundaries.md](fakes-and-boundaries.md) section 4) | since 0.8 it blocks DNS lookups too, so the error may name `getaddrinfo` |
| tests that pass in any order | pytest-randomly | shuffles the order on every run, reseeds `random` for each test, prints the seed | 4.0 changed the seed `random` gets in each test, and 5.0 changed the order a given seed produces, so a seed noted on an older version may not repeat that run |
| async tests | pytest-asyncio, or anyio's own plugin | runs `async def` tests and fixtures in auto mode, with no mark ([running-tests.md](running-tests.md) section 7) | one plugin in auto mode, never both; anyio's key needs anyio 4.11 or newer |

## 2. Add when the need appears

Add each of these as a development dependency, locked with the rest, when the first test needs
it, not before.

| Need | Library | What it does | Add it when | Watch for |
|---|---|---|---|---|
| a faster run | pytest-xdist | runs the tests in several worker processes, `-n auto` | the whole suite takes longer than people are willing to wait before a push | a session fixture runs once per worker ([running-tests.md](running-tests.md) section 8) |
| a real database or broker in `integration/` | testcontainers | starts Postgres, Redis and others in Docker from a fixture, and removes them after | the first test that needs the real thing | needs a Docker daemon; the database driver is not included, add it yourself |
| a hung test fails instead of stalling | pytest-timeout | ends a test after a set time | the integration suite, from its first test that calls something outside | the time covers fixture setup too; the `signal` method clashes with code that uses `SIGALRM` |
| retries for a test that asks a real model | pytest-rerunfailures | reruns a failed test, `--reruns N` | the first `live_model` check whose pass rule is any of n ([running-tests.md](running-tests.md) section 10) | never on a test that does not call a real model; a rerun keeps the wider fixtures |
| code you do not own reads the clock | time-machine | moves the process clock for the length of a block | a library reads `datetime.now()` itself; your own code takes the time as a value | does not move `time.monotonic()` since 3.0 |
| a property that holds for every input | Hypothesis | generates inputs from a description of them, and shrinks a failing one to the smallest | a property holds for every input: a round trip such as parse and format, agreement with a simpler implementation | slower than a table; name the test for the property it checks |
| a large output checked by eye | syrupy | stores the output in a file next to the test and compares later runs with it | a rendered email, an API response of many fields | a snapshot passes whatever it first recorded: review each update like code. Its `__snapshots__/` folders hold no `__init__.py`, so the two `find` checks of [layout.md](layout.md) sections 4 and 6 skip them |
| test data for models with many fields | polyfactory | builds dataclasses, Pydantic models and `TypedDict`s from their type hints | a builder function ([fixtures.md](fixtures.md) section 7) grows past a handful of fields | its values are random: set every field the test is about |
| which lines the tests reach | pytest-cov | measures coverage for the run, and combines the workers of pytest-xdist | you want the report in CI | coverage says what ran, not what a test checked |

Two needs take no library at all:

- **A fake HTTP server for a client**: `httpx.MockTransport` is part of httpx
  ([fakes-and-boundaries.md](fakes-and-boundaries.md) section 3).
- **Checks over cases known only at run time**: the `subtests` fixture is part of pytest since 9.0
  ([test-structure.md](test-structure.md) section 7).

## 3. Not by default, and why

These are good libraries that this practice leaves out of the default set, each for a reason a
team may weigh differently.

| Library | What it offers | Why it is not in the default set |
|---|---|---|
| pytest-mock | a `mocker` fixture over `unittest.mock` | `monkeypatch` ships with pytest and, with the stand-ins of [fakes-and-boundaries.md](fakes-and-boundaries.md) section 1, covers it; each patcher object keeps its own undo list, so a suite keeps one patcher library ([fixtures.md](fixtures.md) section 6) |
| respx, pytest-httpx | intercept every httpx request by route, without passing a client | the interception is global and unseen by the code under test; an injected `MockTransport` does the same explicitly. pytest-httpx also pins one minor version of httpx |
| pytest-env | environment variables set from the configuration for every test | every test gets them without asking for them, the implicit setup [fixtures.md](fixtures.md) section 2 rules out; a test builds the values it needs ([python.md](../language/python.md) section 5) |
| inline-snapshot | snapshots written into the test's own source | still before 1.0 and marked beta, and it rewrites test files; syrupy covers snapshots |
| factory-boy | factories for ORM models | built around ORM models, and its last release was in early 2025; polyfactory builds typed models. A Django project that already uses it keeps it |
| vcrpy, pytest-recording | record real HTTP traffic to a file and replay it | a recording can keep request headers, keys included, and replays whatever the partner said on the day it was made; pytest-recording has not been released since May 2025 |
| dirty-equals | matchers such as `IsNow` and `IsPartialDict` for `==` | it changes how every assertion reads; a team choice, not a default. [assertions.md](assertions.md) section 1 asks for the exact value |
| mutmut, cosmic-ray | changes the code in many small ways, reruns the tests on each change, and lists every change no test caught | steps 1 and 5 of [what-to-test.md](what-to-test.md) section 4 already name one breaking edit for each new test and watch the test fail on it. mutmut starts pytest with `-p no:randomly`, which the `required_plugins` of [running-tests.md](running-tests.md) section 1 rejects with exit code 4. cosmic-ray reruns the whole test command for each change: by its own docs, a 10-second suite with 1,000 changes takes about 2.7 hours |

## 4. Sources

Each project's own documentation, changelog or README, read in September 2026: pytest-socket,
pytest-randomly, pytest-asyncio, anyio ("Testing with AnyIO" and its version history),
pytest-xdist, testcontainers-python, pytest-timeout, pytest-rerunfailures, time-machine,
Hypothesis, syrupy, polyfactory, pytest-cov and coverage.py, httpx ("Transports"), pytest's 9.0
changelog (`subtests`), pytest-mock, respx, pytest-httpx, pytest-env, inline-snapshot,
factory-boy, vcrpy, pytest-recording, dirty-equals, mutmut (README and source), cosmic-ray
(documentation).
