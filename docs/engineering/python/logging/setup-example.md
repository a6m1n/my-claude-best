# Example: logging set up for a service and a CLI

A worked example for [logging.md](logging.md), sections 2, 3, 5, 6 and 7. It shows one
application, `acme`, with an HTTP adapter (FastAPI, served by uvicorn) and a command-line
adapter, laid out as in [file-structure.md](../../any-language/file-structure/file-structure.md). The application
traces with Langfuse, whose SDK brings `opentelemetry-api`; an application with no tracer drops
the `trace_id` part. Every name is a placeholder.

The files, in the order a record travels: a module writes a line, the Filter adds the ids, a
formatter renders it, and one handler writes it to the stream the entry point chose.

## `core/logging.py`: the config, the Filter and two formatters

```python
"""Logging for every process: one config, one context Filter, two formatters."""

import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Final, Literal, TypeAlias

from opentelemetry import trace

LogFormat: TypeAlias = Literal["console", "json"]
LogLevel: TypeAlias = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Set per request or per run: request_id by the request-id middleware, thread_id where
# the agent is invoked (logging.md section 8).
request_id: ContextVar[str] = ContextVar("request_id", default="-")
thread_id: ContextVar[str] = ContextVar("thread_id", default="-")

# Every record has these attributes; anything else on a record came from extra= or
# the Filter.
_STANDARD_ATTRIBUTES: Final = frozenset(
    vars(logging.LogRecord("", 0, "", 0, "", None, None))
) | {"message", "asctime"}
_CONTEXT_IDS: Final = ("request_id", "thread_id", "trace_id")
# uvicorn's coloured copy of its own message
_DROPPED_ATTRIBUTES: Final = frozenset({"color_message"})


class ContextFilter(logging.Filter):
    """Copies the ids of the current request, dialogue and trace onto every record.

    Each id defaults to "-": a CLI or a worker has no request, and a format string
    that names a field the record lacks would drop the whole line.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id.get()
        record.thread_id = thread_id.get()
        record.trace_id = _current_trace_id()

        return True


def _current_trace_id() -> str:
    span_context = trace.get_current_span().get_span_context()
    return format(span_context.trace_id, "032x") if span_context.is_valid else "-"


def _extra_fields(record: logging.LogRecord) -> dict[str, object]:
    return {
        key: value
        for key, value in vars(record).items()
        if key not in _STANDARD_ATTRIBUTES
        and key not in _CONTEXT_IDS
        and key not in _DROPPED_ATTRIBUTES
    }


class ConsoleFormatter(logging.Formatter):
    """For a person at a terminal: the usual line, then the extra= fields as key=value."""

    def __init__(self) -> None:
        super().__init__(
            "%(asctime)s %(levelname)-8s %(name)s [%(request_id)s] %(message)s"
        )

    def formatMessage(self, record: logging.LogRecord) -> str:
        # formatMessage, not format: a traceback still comes after the fields.
        line = super().formatMessage(record)

        extra_fields = _extra_fields(record)
        rendered_fields = " ".join(
            f"{key}={value}" for key, value in extra_fields.items()
        )
        return f"{line} {rendered_fields}" if rendered_fields else line


class JsonFormatter(logging.Formatter):
    """One JSON object per line, for a log store searched by field."""

    def format(self, record: logging.LogRecord) -> str:
        context = {key: getattr(record, key, "-") for key in _CONTEXT_IDS}
        fields = context | _extra_fields(record)
        timestamp = datetime.fromtimestamp(record.created, UTC)
        # The formatter's own keys go last, so no extra= key can overwrite them.
        fields |= {
            "ts": timestamp.isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "template": record.msg,
        }

        if record.exc_info:
            fields["exception"] = self.formatException(record.exc_info)

        if record.stack_info:
            fields["stack"] = self.formatStack(record.stack_info)

        # json.dumps escapes line breaks inside values, so a value cannot split the record.
        return json.dumps(fields, default=str)


def build_logging_config(
    log_level: LogLevel,
    log_format: LogFormat,
    stream: Literal["stdout", "stderr"] = "stdout",
) -> dict[str, object]:
    """The one logging config of a process; main() applies it, directly or through uvicorn."""
    return {
        "version": 1,
        # The default True silences loggers created before this call.
        "disable_existing_loggers": False,
        "filters": {"context": {"()": ContextFilter}},
        "formatters": {
            "console": {"()": ConsoleFormatter},
            "json": {"()": JsonFormatter},
        },
        "handlers": {
            "stream": {
                "class": "logging.StreamHandler",
                "stream": f"ext://sys.{stream}",
                "formatter": log_format,
                "filters": ["context"],
            },
        },
        "loggers": {
            # Start, stop and error lines.
            "uvicorn": {"handlers": [], "propagate": True},
            # One line per request.
            "uvicorn.access": {"handlers": [], "propagate": True},
            # httpx logs every outgoing request at INFO.
            "httpx": {"level": "WARNING"},
            # openai>=3 sends through httpx2, which also logs every request at INFO.
            "httpx2": {"level": "WARNING"},
        },
        "root": {"level": log_level, "handlers": ["stream"]},
    }
```

The console formatter is the default, because a person reads the log while the code is written.
`JsonFormatter` is switched on by `ACME_LOG_FORMAT=json` once the logs go to a store searched by
field (logging.md section 6). Both read the same Filter, so a line has the same ids in either
format.

## `core/config.py`: the two settings

The two logging fields of the application's settings class. Its `model_config` and its other
fields are left out; they are [python/language/settings-example.md](../language/settings-example.md)'s.

```python
from pydantic_settings import BaseSettings

from acme.core.logging import LogFormat, LogLevel


class Settings(BaseSettings):
    log_level: LogLevel = "INFO"
    log_format: LogFormat = "console"  # ACME_LOG_FORMAT=json in deployed environments
```

The types reject a misspelt level or format when the process starts, not at the first log call.

## `api/main.py` and `cli/main.py`: the only places that apply the config

```python
# api/main.py: uvicorn applies the dict in every worker process
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

```python
# cli/main.py: the CLI keeps stdout for its output, so its log goes to stderr
import logging.config
import sys

from acme.cli.commands import run
from acme.core.config import Settings
from acme.core.logging import build_logging_config


def main() -> None:
    settings = Settings()
    logging.config.dictConfig(
        build_logging_config(settings.log_level, settings.log_format, stream="stderr")
    )

    sys.exit(run(sys.argv[1:]))
```

`run` gets only the arguments because this CLI's commands call no client; a command that does gets
it from `main()`, built from `settings`, as `build_app` does for routes.

No other file calls `dictConfig`, and no test does: pytest's `caplog` keeps working.

## `api/middleware_request_id.py` and `api/app.py`: the request id

```python
# api/middleware_request_id.py
"""Pure ASGI middleware: every line of a request, uvicorn's included, carries one id."""

import re
from typing import Final
from uuid import uuid4

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from acme.core.logging import request_id

REQUEST_ID_HEADER: Final = "x-request-id"
_VALID_ID_PATTERN: Final = re.compile(r"[A-Za-z0-9._-]{1,64}")


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)

            return

        incoming_id = Headers(scope=scope).get(REQUEST_ID_HEADER, "")
        # A client's id only if it is safe to write into a log line.
        is_safe = _VALID_ID_PATTERN.fullmatch(incoming_id) is not None
        current_request_id = incoming_id if is_safe else uuid4().hex

        request_id.set(current_request_id)

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message).append(
                    REQUEST_ID_HEADER, current_request_id
                )

            await send(message)

        await self.app(scope, receive, send_with_id)
```

`create_app()` below passes `Settings()` to `build_app()`, so a test builds the app from its own,
as in [python/language/settings-example.md](../language/settings-example.md). `build_app()` also builds the
search client once from `settings` and keeps it on `app.state`, and registers the handlers for
`RequestValidationError` and `ResponseValidationError` that [python.md](../language/python.md)
section 4 asks for; that wiring is not shown.

```python
# api/app.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from acme.api.middleware_request_id import RequestIdMiddleware
from acme.api.routes_report import router as report_router
from acme.core.config import Settings


async def internal_error(request: Request, exc: Exception) -> JSONResponse:
    # uvicorn logs this exception once, with its traceback; a log call here would write a second ERROR.
    return JSONResponse({"detail": "Internal server error"}, status_code=500)


def create_app() -> RequestIdMiddleware:
    # Outside FastAPI's own error middleware, so the id is set first and its header reaches a 500 too.
    return RequestIdMiddleware(build_app(Settings()))


def build_app(settings: Settings) -> FastAPI:
    app = FastAPI()

    app.add_exception_handler(Exception, internal_error)
    app.include_router(report_router)

    return app
```

`app.add_middleware(RequestIdMiddleware)` would put it inside that error middleware: the id would
still reach every log line, but the 500 response would leave without its header.

## A module and a client: lines at work

Imports are left out of the two files below; only the log lines matter here.

```python
# core/search_client.py: the one client of the search API; retrying is its job
logger = logging.getLogger(__name__)

# The search API answers in well under a second, so three tries of five seconds
# end a call that is stuck instead of waiting on it.
MAX_ATTEMPTS: Final = 3
TIMEOUT_SECONDS: Final = 5.0


class SearchClient:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def find_sections(self, topic: str) -> list[Section]:
        attempt = 1

        while True:
            try:
                response = await self._http.post(
                    "/sections", json={"topic": topic}, timeout=TIMEOUT_SECONDS
                )
                return parse_sections(response.content)
            except httpx.TimeoutException:
                if attempt == MAX_ATTEMPTS:
                    # from None: the error text could repeat the request; the attempts say enough
                    raise SearchUnavailable(attempts=attempt) from None

                logger.warning(
                    "Search API timed out, retry %d of %d", attempt, MAX_ATTEMPTS - 1
                )

                attempt += 1
```

`parse_sections`, not shown, validates the bytes once with a module-level `TypeAdapter`'s
`validate_json` and replaces a `ValidationError` with the client's own error, from None
([python.md](../language/python.md) section 4).

```python
# reports/report/usecase.py: this code decides what a failed search means, so it logs it, once
logger = logging.getLogger(__name__)


async def generate_report(request: ReportRequest, search: SearchClient) -> ReportResult:
    try:
        sections = await search.find_sections(request.topic)
    except SearchUnavailable:
        logger.exception("Report %s failed: search unavailable", request.report_id)

        return ReportResult.failed(request.report_id)

    logger.info(
        "Report %s generated", request.report_id, extra={"sections": len(sections)}
    )

    return ReportResult.done(request.report_id, sections)
```

The client logs a retry at `WARNING`, because it recovered by itself. It never logs the final
failure, because it does not decide what that failure means. The use case decides, and writes
the one `ERROR` with the traceback. The topic, which is user text, appears in no line.

## What it prints

With `ACME_LOG_FORMAT=console`, one request that needed a retry:

```
2026-09-27 14:03:11,482 INFO     uvicorn.error [-] Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
2026-09-27 14:03:15,107 WARNING  acme.core.search_client [7f3c9a1e0b2d4c6e8f1a3b5c7d9e0f12] Search API timed out, retry 1 of 2
2026-09-27 14:03:16,020 INFO     acme.reports.report.usecase [7f3c9a1e0b2d4c6e8f1a3b5c7d9e0f12] Report 81 generated sections=6
2026-09-27 14:03:16,021 INFO     uvicorn.access [7f3c9a1e0b2d4c6e8f1a3b5c7d9e0f12] 192.0.2.10:53211 - "POST /reports HTTP/1.1" 200
```

The same `Report 81 generated` line with `ACME_LOG_FORMAT=json`:

```json
{"request_id": "7f3c9a1e0b2d4c6e8f1a3b5c7d9e0f12", "thread_id": "-", "trace_id": "-", "sections": 6, "ts": "2026-09-27T14:03:16.020+00:00", "level": "INFO", "logger": "acme.reports.report.usecase", "message": "Report 81 generated", "template": "Report %s generated"}
```

This request calls no model, so it opens no root span ([logging.md](logging.md) section 8), and
`trace_id` is `-`. An OpenTelemetry HTTP instrumentation fills the field on every route, but read
[logging.md](logging.md) section 12 before you add one to a process that traces with Langfuse.

The start line carries `-`: uvicorn wrote it before any request existed. The access line carries
the request's id because uvicorn writes it inside the request's own task.
