# Example: logging set up for a service and a CLI

A worked example for [logging.md](logging.md), sections 2, 3, 5, 6 and 7. It shows one
application, `acme`, with an HTTP adapter (FastAPI, served by uvicorn) and a command-line
adapter, laid out as in [file-structure.md](../file-structure/file-structure.md). The application
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
from typing import Any, Literal

from opentelemetry import trace

LogFormat = Literal["console", "json"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Set by the adapters: the request-id middleware and the code that invokes an agent.
request_id: ContextVar[str] = ContextVar("request_id", default="-")
thread_id: ContextVar[str] = ContextVar("thread_id", default="-")

# Every record has these attributes; anything else on a record came from extra= or the Filter.
_STANDARD = frozenset(vars(logging.LogRecord("", 0, "", 0, "", None, None))) | {"message", "asctime"}
_CONTEXT = ("request_id", "thread_id", "trace_id")
_DROPPED = frozenset({"color_message"})  # uvicorn's coloured copy of its own message


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


def _extra_fields(record: logging.LogRecord) -> dict[str, Any]:
    return {
        key: value
        for key, value in vars(record).items()
        if key not in _STANDARD and key not in _CONTEXT and key not in _DROPPED
    }


class ConsoleFormatter(logging.Formatter):
    """For a person at a terminal: the usual line, then the extra= fields as key=value."""

    def __init__(self) -> None:
        super().__init__("%(asctime)s %(levelname)-8s %(name)s [%(request_id)s] %(message)s")

    def formatMessage(self, record: logging.LogRecord) -> str:
        # formatMessage, not format: a traceback still comes after the fields.
        line = super().formatMessage(record)
        fields = " ".join(f"{key}={value}" for key, value in _extra_fields(record).items())
        return f"{line} {fields}" if fields else line


class JsonFormatter(logging.Formatter):
    """One JSON object per line, for a log store searched by field."""

    def format(self, record: logging.LogRecord) -> str:
        fields = {key: getattr(record, key, "-") for key in _CONTEXT} | _extra_fields(record)
        # The formatter's own keys go last, so no extra= key can overwrite them.
        fields |= {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds"),
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
    level: LogLevel, fmt: LogFormat, stream: Literal["stdout", "stderr"] = "stdout"
) -> dict[str, Any]:
    """The one logging config of a process; main() applies it, directly or through uvicorn."""
    return {
        "version": 1,
        "disable_existing_loggers": False,  # the default True silences loggers created before this call
        "filters": {"context": {"()": ContextFilter}},
        "formatters": {"console": {"()": ConsoleFormatter}, "json": {"()": JsonFormatter}},
        "handlers": {
            "stream": {
                "class": "logging.StreamHandler",
                "stream": f"ext://sys.{stream}",
                "formatter": fmt,
                "filters": ["context"],
            },
        },
        "loggers": {
            "uvicorn": {"handlers": [], "propagate": True},  # start, stop and error lines
            "uvicorn.access": {"handlers": [], "propagate": True},  # one line per request
            "httpx": {"level": "WARNING"},  # it logs every outgoing request at INFO
            "httpx2": {"level": "WARNING"},  # openai>=3 sends through httpx2, which also logs every request at INFO
        },
        "root": {"level": level, "handlers": ["stream"]},
    }
```

The console formatter is the default, because a person reads the log while the code is written.
`JsonFormatter` is switched on by `LOG_FORMAT=json` once the logs go to a store searched by field
(logging.md section 6). Both read the same Filter, so a line has the same ids in either format.

## `core/config.py`: the two settings

```python
from pydantic_settings import BaseSettings

from acme.core.logging import LogFormat, LogLevel


class Settings(BaseSettings):
    log_level: LogLevel = "INFO"
    log_format: LogFormat = "console"  # LOG_FORMAT=json in deployed environments
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
        "acme.api.app:app",
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

No other file calls `dictConfig`, and no test does: pytest's `caplog` keeps working.

## `api/middleware_request_id.py` and `api/app.py`: the request id

```python
# api/middleware_request_id.py
"""Pure ASGI middleware: every line of a request, uvicorn's included, carries one id."""

import re
from uuid import uuid4

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from acme.core.logging import request_id

_VALID_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = Headers(scope=scope).get("x-request-id", "")
        rid = incoming if _VALID_ID.fullmatch(incoming) else uuid4().hex  # a client id only if it is safe
        request_id.set(rid)

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message).append("x-request-id", rid)
            await send(message)

        await self.app(scope, receive, send_with_id)
```

```python
# api/app.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from acme.api.middleware_request_id import RequestIdMiddleware
from acme.api.routes_report import router as report_router


async def internal_error(request: Request, exc: Exception) -> JSONResponse:
    # uvicorn logs this exception once, with its traceback; a log call here would write a second ERROR.
    return JSONResponse({"detail": "Internal server error"}, status_code=500)


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_exception_handler(Exception, internal_error)
    app.include_router(report_router)
    return app


# Outside FastAPI's own error middleware, so the id is set first and its header reaches a 500 too.
app = RequestIdMiddleware(create_app())
```

`app.add_middleware(RequestIdMiddleware)` would put it inside that error middleware: the id would
still reach every log line, but the 500 response would leave without its header.

## A module and a client: lines at work

Imports are left out of the two files below; only the log lines matter here.

```python
# core/search_client.py: the one client of the search API; retrying is its job
logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
TIMEOUT_S = 5.0


class SearchClient:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def find_sections(self, topic: str) -> list[Section]:
        attempt = 1
        while True:
            try:
                response = await self._http.post("/sections", json={"topic": topic}, timeout=TIMEOUT_S)
                return parse_sections(response.json())
            except httpx.TimeoutException:
                if attempt == MAX_ATTEMPTS:
                    # from None: the error text could repeat the request; the attempts say enough
                    raise SearchUnavailable(attempts=attempt) from None
                logger.warning("Search API timed out, retry %d of %d", attempt, MAX_ATTEMPTS - 1)
                attempt += 1
```

```python
# reports/report/usecase.py: this code decides what a failed search means, so it logs it, once
logger = logging.getLogger(__name__)


async def generate_report(request: ReportRequest, search: SearchClient) -> ReportResult:
    try:
        sections = await search.find_sections(request.topic)
    except SearchUnavailable:
        logger.exception("Report %s failed: search unavailable", request.report_id)
        return ReportResult.failed(request.report_id)
    logger.info("Report %s generated", request.report_id, extra={"sections": len(sections)})
    return ReportResult.done(request.report_id, sections)
```

The client logs a retry at `WARNING`, because it recovered by itself. It never logs the final
failure, because it does not decide what that failure means. The use case decides, and writes
the one `ERROR` with the traceback. The topic, which is user text, appears in no line.

## What it prints

With `LOG_FORMAT=console`, one request that needed a retry:

```
2026-09-27 14:03:11,482 INFO     uvicorn.error [-] Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
2026-09-27 14:03:15,107 WARNING  acme.core.search_client [7f3c9a1e0b2d4c6e8f1a3b5c7d9e0f12] Search API timed out, retry 1 of 2
2026-09-27 14:03:16,020 INFO     acme.reports.report.usecase [7f3c9a1e0b2d4c6e8f1a3b5c7d9e0f12] Report 81 generated sections=6
2026-09-27 14:03:16,021 INFO     uvicorn.access [7f3c9a1e0b2d4c6e8f1a3b5c7d9e0f12] 192.0.2.10:53211 - "POST /reports HTTP/1.1" 200
```

The same `Report 81 generated` line with `LOG_FORMAT=json`:

```json
{"request_id": "7f3c9a1e0b2d4c6e8f1a3b5c7d9e0f12", "thread_id": "-", "trace_id": "-", "sections": 6, "ts": "2026-09-27T14:03:16.020+00:00", "level": "INFO", "logger": "acme.reports.report.usecase", "message": "Report 81 generated", "template": "Report %s generated"}
```

This request opens no span, so `trace_id` is `-`; an HTTP tracer, for example OpenTelemetry's
FastAPI instrumentation, fills the field.

The start line carries `-`: uvicorn wrote it before any request existed. The access line carries
the request's id because uvicorn writes it inside the request's own task.
