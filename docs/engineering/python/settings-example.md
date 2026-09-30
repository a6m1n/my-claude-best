# Example: application settings read once, at startup

A worked before-and-after for [python.md](python.md) section 5. A shop's HTTP API talks to its
database and to a card-payments provider, so it needs a database host, a user, a password and an
API key, plus a few values with safe defaults. Names are invented. Each client is shown with its
constructor only: its other methods are left out. The logging config is the one in
[logging/setup-example.md](../logging/setup-example.md).

What moves is where the configuration is read: from inside each client, with a default each
client picked, to one class that the code starting the process builds before anything else runs.

## Before: each client reads the environment itself

`src/acme/core/database.py`

```python
"""The one way into the shop's database."""

import os

from sqlalchemy import Engine, create_engine


def build_engine() -> Engine:
    # A developer's laptop runs Postgres with these credentials.
    url = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg://acme:acme@localhost/acme"
    )
    return create_engine(url)
```

`src/acme/core/payments_client.py`

```python
"""The one client of the card-payments provider: every call to it goes through here."""

import os
from typing import Final

import httpx

# Card payments answer within a few seconds; ten seconds ends a stuck call
# before the customer's own request gives up.
TIMEOUT_SECONDS: Final = 10.0


class PaymentGateway:
    def __init__(self, http: httpx.Client) -> None:
        api_key = os.environ.get("PAYMENTS_API_KEY", "")
        self._http = http
        self._headers = {"Authorization": f"Bearer {api_key}"}
```

### What goes wrong

One fault, seen from three sides: each client reads its own configuration, where it is used, with
the default it picked.

1. **A missing value does not stop the start.** A deployment without `PAYMENTS_API_KEY` starts,
   passes its health check and fails at the first charge, when the provider rejects an empty key.
   Without `DATABASE_URL` it connects to a database on `localhost`, or waits for one.
2. **A typo looks like a missing value.** `PAYMENT_API_KEY` set in place of `PAYMENTS_API_KEY`
   gives the same empty key, and nothing says which name was expected.
3. **The inputs are hidden.** `build_engine()` takes no parameter and `PaymentGateway` takes only
   its HTTP client, so a reader cannot see what they depend on, and a test has to set environment variables to reach
   them ([readability.md](../readability/readability.md) section 6). A second reader of
   `DATABASE_URL` elsewhere can pick a second default.

Run on CPython 3.12 with no variable set, both calls succeed: `build_engine()` returns an engine
for `localhost`, and `PaymentGateway(http)` a client whose header is `Bearer ` with nothing after
it.

## After: one class, built where the process starts

```text
src/acme/
├── core/
│   ├── config.py            Settings: every value the application reads from outside
│   ├── database.py          build_engine: the one way into the database
│   ├── payments_client.py   PaymentGateway: every call to card payments
│   ├── logging.py           the logging config
│   └── ...                  files not shown
└── api/
    ├── main.py              main(): builds Settings, then starts uvicorn with the app factory
    ├── app.py               create_app(): builds Settings and each client once, wires the routes
    └── ...                  files not shown
tests/unit/core/
└── test_config.py           the test of the settings class
```

Where each file sits is [file-structure.md](../file-structure/file-structure.md) sections 4
and 5. [testing/layout.md](../testing/layout.md) section 3 gives each module its own test folder;
the test of `core/` mirrors its folder the same way.

`src/acme/core/config.py`

```python
"""Every value the application reads from outside, read once at startup."""

from typing import Final

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from acme.core.logging import LogFormat, LogLevel

# The value .env.example ships with: a deployment that still has it was never set up.
PLACEHOLDER_SECRET: Final = "changethis"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ACME_",
        env_file=".env",  # local runs only; a deployment sets real variables
        env_ignore_empty=True,  # Compose and CI pass an unset secret as ""
        frozen=True,
        # A failed start lists every value it read; this keeps them out of the error text.
        hide_input_in_errors=True,
    )

    database_host: str
    database_name: str
    database_user: str
    database_password: SecretStr
    payments_api_key: SecretStr
    allowed_origins: tuple[str, ...] = ()
    log_level: LogLevel = "INFO"
    log_format: LogFormat = "console"  # ACME_LOG_FORMAT=json in deployed environments

    @field_validator("database_password", "payments_api_key")
    @classmethod
    def reject_placeholder(cls, secret: SecretStr) -> SecretStr:
        if secret.get_secret_value() == PLACEHOLDER_SECRET:
            raise ValueError("still holds the placeholder from .env.example")

        return secret
```

It is good because the class is the whole list of what the application reads, each rule on the
field it governs. The five values a deployment must set have no default, so a missing or misspelt
one stops the start. The two secrets are `SecretStr`, and the placeholder check is a validator on
the class, not an `if` somewhere later. The three defaults are safe in every environment.

`src/acme/core/database.py`

```python
"""The one way into the shop's database."""

from pydantic import SecretStr
from sqlalchemy import URL, Engine, create_engine


def build_engine(host: str, name: str, user: str, password: SecretStr) -> Engine:
    url = URL.create(
        "postgresql+psycopg",
        username=user,
        password=password.get_secret_value(),
        host=host,
        database=name,
    )
    return create_engine(url)
```

It is good because the password stays a `SecretStr` until the one line that needs the text, and
the URL is built here, not held in the settings: SQLAlchemy prints a `URL` with `***` in place of
the password.

`src/acme/core/payments_client.py`

```python
"""The one client of the card-payments provider: every call to it goes through here."""

from typing import Final

import httpx
from pydantic import SecretStr

# Card payments answer within a few seconds; ten seconds ends a stuck call
# before the customer's own request gives up.
TIMEOUT_SECONDS: Final = 10.0


class PaymentGateway:
    def __init__(self, http: httpx.Client, api_key: SecretStr) -> None:
        self._http = http
        self._headers = {"Authorization": f"Bearer {api_key.get_secret_value()}"}
```

It is good because both inputs are parameters: the adapter builds the `httpx.Client` once, and a
test passes one with an `httpx.MockTransport` inside and a `SecretStr` of its own. The timeout has
a name and a reason; the methods, left out, pass it on each call, as the search client in
[logging/setup-example.md](../logging/setup-example.md) does.

`src/acme/api/app.py`

```python
"""Builds the HTTP app: the settings, one instance of each client, and the routes that use them."""

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from acme.api.routes_checkout import build_checkout_router
from acme.core.config import Settings
from acme.core.database import build_engine
from acme.core.payments_client import PaymentGateway


def create_app() -> FastAPI:
    """The factory uvicorn calls once in each worker, at startup."""
    return build_app(Settings())


def build_app(settings: Settings) -> FastAPI:
    engine = build_engine(
        host=settings.database_host,
        name=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
    )
    payments = PaymentGateway(
        httpx.Client(base_url="https://payments.example.com"),
        api_key=settings.payments_api_key,
    )

    app = FastAPI()
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins))
    app.include_router(build_checkout_router(engine, payments))

    return app
```

It is good because the adapter is the one place that turns settings into clients, each built once
per worker. `create_app` is the factory uvicorn calls by name; `build_app` takes the `Settings`, so
a test builds the app from its own. `routes_checkout.py`, not shown, hands the two clients to the
use case as parameters.

`src/acme/api/main.py`

```python
"""The HTTP process: reads the settings first, then starts uvicorn with the app factory."""

import uvicorn

from acme.core.config import Settings
from acme.core.logging import build_logging_config


def main() -> None:
    settings = Settings()
    uvicorn.run(
        "acme.api.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        log_config=build_logging_config(settings.log_level, settings.log_format),
    )
```

It is good because `Settings()` is the first line of the process: if a value is missing or wrong,
the process stops here with one error that names every bad field, before uvicorn starts. uvicorn
applies the logging config, then calls `create_app` in each worker, so the app and its clients are
built after logging is set up ([logging.md](../logging/logging.md) section 2) and `--workers`
works. How each type checker handles the call is [python.md](python.md) section 5, "The type
checker sees missing arguments".

`tests/unit/core/test_config.py`

```python
import os

import pytest
from pydantic import ValidationError

from acme.core.config import Settings

VALID_ENVIRONMENT = {
    "ACME_DATABASE_HOST": "db.example.com",
    "ACME_DATABASE_NAME": "shop",
    "ACME_DATABASE_USER": "shop",
    "ACME_DATABASE_PASSWORD": "db-password-for-tests",
    "ACME_PAYMENTS_API_KEY": "payments-key-for-tests",
}


@pytest.fixture(scope="function")
def environment(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """The valid environment and nothing else: the machine's own ACME_ variables go."""
    for name in list(os.environ):
        # names match in any case, so acme_database_host is one of them too
        if name.upper().startswith("ACME_"):
            monkeypatch.delenv(name)

    for name, value in VALID_ENVIRONMENT.items():
        monkeypatch.setenv(name, value)

    return monkeypatch


class TestSettings:
    """An empty or placeholder secret stops the start, and the error shows no secret."""

    def test_an_empty_value_stops_the_start(
        self, environment: pytest.MonkeyPatch
    ) -> None:
        environment.setenv("ACME_PAYMENTS_API_KEY", "")

        with pytest.raises(ValidationError) as caught:
            Settings(_env_file=None)

        errors = caught.value.errors(include_input=False)
        assert [error["loc"] for error in errors] == [("payments_api_key",)]

    def test_a_failed_start_prints_no_secret(
        self, environment: pytest.MonkeyPatch
    ) -> None:
        environment.delenv("ACME_DATABASE_HOST")

        with pytest.raises(ValidationError, match="database_host") as caught:
            Settings(_env_file=None)

        # A missing-field error carries every value the class read as its input.
        assert "payments-key-for-tests" not in str(caught.value)

    def test_a_placeholder_secret_stops_the_start(
        self, environment: pytest.MonkeyPatch
    ) -> None:
        environment.setenv("ACME_PAYMENTS_API_KEY", "changethis")

        with pytest.raises(ValidationError, match="placeholder"):
            Settings(_env_file=None)
```

It is good because each test pins one thing this class decides and an edit could undo without a
sound: `env_ignore_empty=True`, which pydantic-settings leaves off, `hide_input_in_errors=True`,
and the placeholder validator. Delete any one of them and exactly its test turns red. No test
checks that pydantic-settings reads a variable into its field or a JSON list into a tuple: the
library's own tests cover that, and such a test here would turn red only when the library changes
or a field is renamed on purpose ([testing/what-to-test.md](../testing/what-to-test.md) section 3).
A missing value is shown once, in the test that removes `ACME_DATABASE_HOST`; that no required
field gains a default is [python.md](python.md) section 5's rule, kept in review.

The fixture closes both sources the class reads: `_env_file=None` keeps a developer's `.env` out,
and the fixture removes every `ACME_` variable of the machine before it sets the valid ones. It
states its scope ([testing/fixtures.md](../testing/fixtures.md) section 1): a fresh environment
for every test. Which tests build `Settings` at all is [python.md](python.md) section 5.

### What changed

Each thing that went wrong in Before now fails, or shows, where the reader looks.

- **A missing value stops the start**, which answers point 1. The five values without a default
  are required, so a deployment that lacks one exits at `Settings()` with the field's name, and so
  does one set to an empty string, and the error text carries no value it read.
- **A typo stops the start too**, which answers point 2, for the five required values:
  `ACME_PAYMENT_API_KEY` matches no field and is ignored, and the missing `payments_api_key` is
  reported. A typo in one of the three values with a default still leaves the default in place;
  that is why only safe values get one.
- **The inputs are in the signatures**, which answers point 3. `build_engine` and
  `PaymentGateway` take what they use; `build_app` is the one function that turns `Settings` into
  clients and hands the values on.

Run with the test file above on CPython 3.12 (pydantic 2.12.5, pydantic-settings 2.14.2) and
CPython 3.13 (pydantic 2.13.4, pydantic-settings 2.14.2): the three tests pass; with the machine's
own `ACME_DATABASE_HOST` exported, they still pass, because the fixture removes it; with
`hide_input_in_errors=True`, `env_ignore_empty=True` or the placeholder check deleted, exactly the
test that pins it fails; `repr(Settings(...))` prints both secrets as `**********`.

### What this example does not claim

- **Two builds in one process.** `main()` builds `Settings` for the log config, and `create_app`
  builds it again in each worker; with one worker both run in the same process. Both run at
  startup, and a missing value stops the first.
- **What is left out.** The settings read no secrets directory and no secret manager: a deployment
  that keeps its secrets there adds that source to the class, and nothing else changes. The
  `.env.example` file that holds the placeholder is not shown. The `.gitignore` and `.dockerignore`
  that list `.env` are not shown either.
- **That the error never carries a secret.** `hide_input_in_errors=True` keeps the values out of
  the error's text only; `errors()` and `json()` still carry them, which is why the test reads
  `errors(include_input=False)` and why [python.md](python.md) section 5 lets the error end the
  process and logs neither.
