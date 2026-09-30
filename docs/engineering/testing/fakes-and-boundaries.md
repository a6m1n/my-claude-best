# Fakes and boundaries

How a test stands in for the world outside the code under test: which stand-in to build, where
each outside system is cut off, and what a test may reach past. That a unit takes its
collaborators as parameters, so a test can pass a stand-in at all, is
[readability.md](../readability/readability.md) section 6.

**Navigation**

- [1. Which stand-in to use](#1-which-stand-in-to-use)
- [2. Assert what came out, not how it was called](#2-assert-what-came-out-not-how-it-was-called)
- [3. Where each boundary is cut](#3-where-each-boundary-is-cut)
- [4. The unit suite is offline by configuration](#4-the-unit-suite-is-offline-by-configuration)
- [5. Drive the public interface](#5-drive-the-public-interface)
- [6. Sources](#6-sources)

## 1. Which stand-in to use

[readability.md](../readability/readability.md) section 6 names the three stand-ins a type checker
accepts for a parameter annotated with a concrete class: the real class with a fake inside it,
`create_autospec(<Class>, instance=True)`, and a subclass that overrides the methods the unit
calls. **When you need one, take the first that fits, in this order:**

1. **The real class with a fake inside**, when a cheap fake of what it wraps exists: an
   `httpx.Client` with an `httpx.MockTransport` for a client class, `tmp_path` for a file store.
   The test then covers the class's own code too: its headers, its parsing, its error mapping.
2. **A hand-written fake**, a subclass that overrides the methods the unit calls and keeps what it
   received in a public attribute, when the class's own code is not the subject. It is ordinary
   code: `@override` on each method makes the type checker fail the day the parent renames it
   ([python.md](../python/python.md) section 3).
3. **`create_autospec(<Class>, instance=True)`**, when the class is wide and the test needs one or
   two of its methods. It raises `AttributeError` for an attribute the class does not have and
   checks the arguments of each call; it does not check what a method returns.

**Never a bare `Mock()` or `MagicMock()`.** typeshed declares `NonCallableMock` a subclass of
`Any`, so the type checker accepts a bare mock for any parameter, and the mock accepts any
attribute: rename `send` to `deliver` on the real class, and the test still passes.

```python
# Good: tests/support/fake_mailer.py — the fake keeps each email as data a test
# compares.
@dataclass(frozen=True)
class SentEmail:
    to: str
    subject: str
    body: str


class FakeMailer(Mailer):
    """A Mailer that keeps every email instead of sending it."""

    def __init__(self) -> None:
        # No super().__init__(): the fake sends nothing, so it needs no provider client.
        self.sent: list[SentEmail] = []

    @override
    def send(self, to: str, *, subject: str, body: str) -> None:
        self.sent.append(SentEmail(to, subject, body))
```

A fake one test file uses stays in that file; a fake a second file needs moves to
`tests/support/fake_<system>.py` ([layout.md](layout.md) section 7).

Check: `grep -rnE "\b(Magic)?Mock\(\)" --include='*.py' tests/` prints nothing.

## 2. Assert what came out, not how it was called

**Assert what the unit returned, the state it left, or the data a fake received, never the shape
of a call when the result already shows it.** `mailer.send.assert_called_once_with(...)` pins how
the call was spelled: adding a `reply_to=` argument to the call, or sending through a batch call,
turns the test red while the customer gets the same email. Harry Percival and Bob Gregory: "Tests
that use mocks *tend* to be more coupled to the implementation details of the codebase. That's
because mock tests verify the interactions between things", which "*tends* to make tests more
brittle" (*Architecture Patterns with Python*, chapter 3).

When the call itself is the behavior, as when the guarantee is that one email goes out, assert on
what the fake recorded, as data:

```python
# Bad: pins the spelling of the call. Adding a reply_to= argument to it breaks the test.
mailer.send.assert_called_once_with(
    "jane.doe@example.com", subject="Your invoice is overdue", body=ANY
)

# Good: pins who got an email, which is the guarantee.
assert [email.to for email in mailer.sent] == ["jane.doe@example.com"]
```

## 3. Where each boundary is cut

**When the code under test reaches outside the process, cut it at the seam this table names.**

| Outside system | In a unit test | In an integration test |
|---|---|---|
| an HTTP API behind a `core/` client class | the client class built on an `httpx.Client` with an `httpx.MockTransport` | the provider's sandbox, where one exists |
| the database | not reached: a rule takes plain values, and a flow that queries goes to `integration/` | a real database in a container, one per run, emptied after each test ([suite-example.md](suite-example.md)) |
| email, a queue, another sender | a fake subclass that records (section 1) | the same fake, unless the sender is the subject |
| a language model | a fake of the one model client, returning a prepared answer | the real model, only under the `live_model` mark ([running-tests.md](running-tests.md) section 10) |
| the clock | a `today` or `now` the test passes ([readability.md](../readability/readability.md) section 6) | the same; time-machine only when a library reads the clock itself |
| files | `tmp_path` | `tmp_path` |
| settings and the environment | the plain values the unit takes ([python.md](../python/python.md) section 5) | the plain values the unit takes, or the `Settings` a whole-app test passes to the function that builds the app ([python.md](../python/python.md) section 5) |

The client is a parameter of whatever uses it, never something the unit builds for itself; that
is what makes the transport replaceable.

```python
# Good: the gateway's own code runs, and the answer is the one the provider gives for a
# declined card. base_url never resolves: the transport answers before any network.
def _card_declined(request: httpx.Request) -> httpx.Response:
    """Answer every call the way the payments provider answers a declined card."""
    return httpx.Response(402, json={"error": {"code": "card_declined"}})


@pytest.fixture(scope="function")
def declining_gateway() -> Iterator[PaymentGateway]:
    """The real gateway, talking to a provider that declines every card."""
    with httpx.Client(
        transport=httpx.MockTransport(_card_declined),
        base_url="https://payments.example.com",
    ) as http:
        yield PaymentGateway(http, api_key=SecretStr("key-for-tests"))
```

`PaymentGateway` is the client of
[python/settings-example.md](../python/settings-example.md); httpx's own documentation names
`MockTransport` for this: it "accepts a handler function, which can be used to map requests onto
pre-determined responses."

## 4. The unit suite is offline by configuration

A unit test that dials out is slow, fails when the network does, and at a model's seam it costs
money. **Block the network for every test with pytest-socket's `--disable-socket` in the
configuration, and let the folder, not each test, open it for `integration/`**: the hook in
`tests/conftest.py` that marks each test with its suite also adds the plugin's own
`enable_socket` mark to every test under `integration/` ([suite-example.md](suite-example.md)
shows it). `--allow-unix-socket` keeps asyncio's internal socket pair and a local Docker socket
working. Check: `grep -n "disable-socket" pyproject.toml` prints the line.

- A unit test that opens a socket fails with the plugin's error, wherever it sits, so the rule
  needs no review.
- A test never writes `enable_socket` itself. A unit test that needs the network belongs in
  `integration/` ([layout.md](layout.md) section 2). Check: `grep -rn "mark.enable_socket" tests/`
  prints nothing.

## 5. Drive the public interface

**Call the unit's public function, never a private helper under it**: the use case, the rule, the
client method. A private helper is tested through the function that calls it; a test that calls it
directly keeps the helper alive after a refactor has made it pointless, and misses the wiring
between the steps.

**Never assert on a private attribute of a fake or of the code under test.** A fake publishes what
a test reads (`mailer.sent`); a test that reaches into `mailer._sent` breaks on a rename that
changes nothing a user sees.

Check: `grep -rnE "import _[a-z]|\._[a-z][a-z_]*\b" tests/` prints only names the test module
defines for itself.

## 6. Sources

Harry Percival and Bob Gregory, *Architecture Patterns with Python* (O'Reilly, 2020), chapter 3,
"A Brief Interlude: On Coupling and Abstractions", free at cosmicpython.com. Python documentation,
`unittest.mock`, "Autospeccing" (`create_autospec`, `instance=True`). typeshed,
`stdlib/unittest/mock.pyi` (`NonCallableMock` subclasses `Any`). httpx documentation, "Transports"
(`MockTransport`). pytest-socket README (`--disable-socket`, `--allow-unix-socket`,
`enable_socket`).
