# Logging rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. Setup: one config, applied by the entry point](#2-setup-one-config-applied-by-the-entry-point)
- [3. Writing a line](#3-writing-a-line)
- [4. Levels](#4-levels)
- [5. Exceptions: once, where handled](#5-exceptions-once-where-handled)
- [6. Where logs go, and the formatters](#6-where-logs-go-and-the-formatters)
- [7. The request id](#7-the-request-id)
- [8. Agents: dialogue, trace and tool calls](#8-agents-dialogue-trace-and-tool-calls)
- [9. Summary lines](#9-summary-lines)
- [10. What never goes into a log](#10-what-never-goes-into-a-log)
- [11. Checks: reasonable, not strict](#11-checks-reasonable-not-strict)
- [12. Where it stops holding](#12-where-it-stops-holding)
- [13. Sources](#13-sources)

## 1. Purpose and the one rule

This file is for everyone who writes or changes Python code that logs: people and AI agents alike.
Read it before you add a log call, set up logging for a process, or wire logging or tracing into
a web service or an agent.

One rule holds the rest together: **the log tells a person what the application did; the trace
store keeps what it said.** A log line is an event with ids: a service started, a request
finished, a call was retried, an operation failed. The text of prompts, answers, tool results and
documents never goes into the log. An application that calls a language model keeps that text in
a trace store, which has its own access control and retention (section 8).

The code assumes Python 3.11 or newer and the standard library's `logging` module. Two cases get
their own rules: a FastAPI service served by uvicorn, and an agent built with LangChain or
LangGraph. File names follow [file-structure.md](../../any-language/file-structure/file-structure.md): `core/`
for code every module uses, one adapter folder per way in (`api/`, `cli/`), and modules in
between.

## 2. Setup: one config, applied by the entry point

When you create a process entry point (the `main()` of an HTTP service, a CLI or a worker), or
change how logging is set up:

- **Build the config in one function.** `build_logging_config(log_level, log_format)` in
  `core/logging.py` returns the one config dict of the process. It imports no web framework
  (file-structure.md section 4).
- **Apply it once, in `main()`, before anything else logs.** Never at import, never in an app
  factory such as `create_app()`, never in a lifespan hook. Lines logged before the config come
  out in another format, and a factory that tests call replaces pytest's capture handler, so
  `caplog` sees nothing: pytest asks that root configuration "only adds to the existing handlers".
- **Give uvicorn the same dict.** `uvicorn.run(..., log_config=build_logging_config(...))`.
  uvicorn applies it in every worker process, with `--workers` and `--reload` too. A second
  `dictConfig` inside the app is not needed, and with `--workers` uvicorn partly overrides it.
- **Set `disable_existing_loggers: False`.** The default `True` disables every logger that
  already exists and is not named in the config, and library loggers such as `langgraph`, `httpx`
  and `uvicorn` exist long before `main()` runs.
- **Route uvicorn's loggers through your handler.** By default `uvicorn` and `uvicorn.access`
  have handlers of their own and do not propagate. Give them no handlers and let them propagate,
  so their lines pass the same Filter and formatter as yours. `uvicorn.error` carries uvicorn's
  start, stop and error lines, not only errors.
- **Pin a noisy library logger by its real name, with the reason.** `"httpx": {"level":
  "WARNING"}  # one INFO line per outgoing request`. A name that is not a real parent, such as
  `langchain` for `langchain_core`, pins nothing.
- **Get the logger once per module:** `logger = logging.getLogger(__name__)` at module level.
  Never the root logger (`logging.info(...)`), never a logger object imported from another module,
  never `logging.Logger(...)`. The logger tree then follows the package tree, the logger name
  says where a line came from, and one module's level can change alone.
- **A library configures nothing.** A package that other code imports adds at most a
  `NullHandler` to its own logger. The Python HOWTO: "the configuration of handlers is the
  prerogative of the application developer who uses your library."

To tell: `grep -rn "dictConfig\|build_logging_config" src/` prints only `core/logging.py` and the
`main.py` files. A LangGraph Agent Server deployment has no `main()` of yours: section 12.

The whole setup, with both formatters and the Filter, is in [setup-example.md](setup-example.md).

## 3. Writing a line

At every log call:

- **The message is a constant string with `%s` placeholders; the values are arguments.** Never
  build the message yourself: no f-string, no `.format()`, no `%` and no `+`. Log stores group
  records by that constant string. Google's style guide: "Some logging implementations collect
  the unexpanded pattern-string as a queryable field." Speed is the smaller reason: for a small
  value the difference is about one percent, but for a large argument it is not. LiteLLM measured
  an f-string with a 67 kB message list at 77 µs against 0.07 µs for the lazy call, at a level
  that was switched off.
- **The message says what happened, and names the thing it happened to.** A reader understands it
  without the lines around it: `logger.info("Order %s paid", order_id)`.
- **A value someone will filter or count on goes into `extra=`,** in snake_case with its unit in
  the name: `extra={"duration_ms": 412, "rows": 1200}`. Everything else stays in the message.
  The base formatter prints no `extra=` field; the JSON formatter prints them all (section 6).
- **An `extra=` key never repeats a record attribute** (`name`, `msg`, `args`, `module` and the
  rest of the LogRecord table) **nor a key the formatter writes itself** (`ts`, `level`,
  `logger`, `message`, `template`, `exception`).
- **An argument that is expensive to build is built only when the level is on.** Passing
  `json.dumps(state)` as an argument still runs `json.dumps`. Guard it with
  `if logger.isEnabledFor(logging.DEBUG):`. Template strings (PEP 750) are evaluated eagerly
  too, so they are no way out.

```python
# good: a constant message, the value as an argument, a filterable field with its unit
logger.info("Report %s generated", report_id, extra={"sections": 6, "duration_ms": 412})

# bad: every record is a new message to the log store
logger.info(f"Report {report_id} generated")
# bad: "level" is the JSON formatter's own key
logger.info("Order %s escalated", order_id, extra={"level": escalation.tier})
```

## 4. Levels

Pick the level by what the reader has to do, not by how bad the event feels.

| Level | When |
|---|---|
| `DEBUG` | Detail for diagnosing a problem. Off in production. |
| `INFO` | A finished unit of work or a change of state, in the past tense, with an id: the service started (its version and its settings, without secrets), a request or an agent run finished, a job completed. "Starting X" is `DEBUG`. |
| `WARNING` | Something went wrong and the application recovered by itself (a retry that is still going, a fallback, a degraded mode), and someone should look at it this week. If nobody will look, it is `INFO`. |
| `ERROR` | The operation failed for good and a person has to act: the last retry failed, a request ended in a 500. Never for a step that will be retried, never for a client error (a 4xx) or an expected outcome such as a failed validation. |
| `CRITICAL` | The process cannot go on and exits: a required setting is missing, the port cannot be bound. |

- The production level is `INFO`, read from a `LOG_LEVEL` setting whose type allows only the five
  names, so a typo fails at start-up.
- `INFO` stays small because of what it means, not because of the level: one line per finished
  unit of work, never a line per step.
- An expected failure is not a warning and carries no traceback. Dave Cheney: "If you choose to
  handle the error by logging it, by definition it's not an error any more."

`ERROR` meaning "a person has to act" is the rule in OpenStack's and MediaWiki's logging
guidelines, and the Google SRE book says of alerts: "Every page should be actionable." Some
practitioners drop `WARNING` altogether (Cheney; Tietz-Sokolskaya). This practice keeps it
narrow instead: uvicorn, httpx and LangGraph write warnings whatever your code does, and a retry
that recovered deserves a line someone reads.

## 5. Exceptions: once, where handled

When you catch an exception, or decide not to:

- **The code that decides what happens next logs it, once.** That code returns an error
  response, retries, falls back or skips an item. Code that only re-raises, with or without
  wrapping, does not log. Logging and re-raising writes the same failure two or three times, and
  every alert on errors counts it that often.
- **The one client of an external system** (`core/<system>_client.py`) logs each retry at
  `WARNING` and raises after the last attempt. The final `ERROR` belongs to the caller that
  decides.
- **An unexpected failure is logged with `logger.exception(...)`** inside the `except` block, so
  the traceback goes with it. Never paste `traceback.format_exc()` into the message, and never
  log only `str(exc)`.
- **An expected failure gets no traceback:** validation, "not found", a 4xx. Log it at `INFO`, or
  not at all.
- **Never catch `BaseException`.** It swallows cancellation and `SystemExit`. An
  `except Exception` either logs with the traceback or re-raises.

In FastAPI, an exception that no handler catches is logged by uvicorn and by nothing else. In
FastAPI 0.141, Starlette 1.7 and uvicorn 0.54, Starlette's `ServerErrorMiddleware` sends the 500
and re-raises ("We always continue to raise the exception. This allows servers to log the
error"). uvicorn then writes one `ERROR` on the `uvicorn.error` logger, with the traceback. So:

- **Leave an unhandled exception to uvicorn.** An `@app.exception_handler(Exception)`, if you
  have one, only builds the response. It changes the body, not the re-raise, so a handler that
  logs writes a second `ERROR`.
- `HTTPException` and validation errors are handled responses. Nothing logs them, and the access
  line already carries their status.

```python
# core/search_client.py: retrying is this client's job, so it logs each retry and raises the last
for attempt in range(1, MAX_ATTEMPTS + 1):
    try:
        return await self._fetch(topic)
    except httpx.TimeoutException:
        if attempt == MAX_ATTEMPTS:
            raise SearchUnavailable(attempts=attempt) from None

        logger.warning(
            "Search API timed out, retry %d of %d", attempt, MAX_ATTEMPTS - 1
        )

# reports/report/usecase.py: this code decides (the report fails), so it logs, once
try:
    sections = await search.find_sections(topic)
except SearchUnavailable:
    logger.exception("Report %s failed: search unavailable", report_id)

    return ReportResult.failed(report_id)
```

## 6. Where logs go, and the formatters

- **One stream handler per process.** A service writes to stdout. "A twelve-factor app never
  concerns itself with routing or storage of its output stream"; the platform collects and ships
  it. A CLI writes its logs to stderr and keeps stdout for its output. So does a server that
  speaks a protocol on stdout, such as an MCP server over stdio: one log line on stdout breaks
  the protocol.
- **No log files, no network handlers, no `QueueHandler` by default.** In async code a file or
  network handler blocks the event loop (the logging cookbook). `QueueHandler` fixes that, but
  `dictConfig` never starts its listener, its queue has no limit, and formatting still runs on
  the calling thread. Section 12 says when it is worth that care.
- **Start with the standard `logging.Formatter` and a format string.** It is enough while a
  person reads the log: locally, in a CLI, in a small service.
- **Switch to the JSON formatter when the logs go to a store searched by field, or when the
  first `extra=` field is something someone filters on.** The base formatter prints only the
  attributes its format string names and silently drops every `extra=` field.
- **Keep both formatters, chosen by a `LOG_FORMAT` setting:** `console` for development and `json`
  for deployed environments. The console formatter stays readable for a person: time, level,
  logger, request id, message, then the `extra=` fields as `key=value`.
- **The console format string names only standard attributes and fields the Filter always
  sets.** A record that lacks a named field is not printed; logging writes "--- Logging error
  ---" to stderr instead, and the application never notices.
- **The JSON formatter writes one object per line:**
  - `ts` (UTC, ISO 8601, with milliseconds), `level`, `logger`, `message` and `template` (the
    constant string, for grouping);
  - the context ids (sections 7 and 8), then the `extra=` fields;
  - `exception`, the whole traceback as one field.

  Its own keys are written last, so no `extra=` key can overwrite them. `json.dumps` escapes
  line breaks inside values, so a value cannot split one record into two. That is OWASP's log
  injection concern, handled by the formatter.

Both formatters are in [setup-example.md](setup-example.md).

## 7. The request id

A request id lets you find every line of one request with one filter, including uvicorn's
access line and the error record uvicorn writes for a 500. Not every process has one: a CLI, a
worker or a script handles no request, and the field there is `-`.

- **A service with an HTTP way in sets the id in a pure ASGI middleware** in its `api/` adapter.
  Never with `@app.middleware("http")` or `BaseHTTPMiddleware`. Starlette's docs: "Using
  BaseHTTPMiddleware will prevent changes to contextvars.ContextVars from propagating upwards
  ... To overcome these limitations, use pure ASGI middleware."
- **Wrap the whole application with it,** outside FastAPI's own error middleware, so the
  response header reaches a 500 too.
- **Take an incoming `X-Request-ID` only if it matches `[A-Za-z0-9._-]{1,64}`;** otherwise
  make a new one. Send the id back in the response header on every status.
- **The `ContextVar` and the Filter live in `core/logging.py`,** which imports no framework. The
  Filter sits on the handler, so every record gets the field, uvicorn's included, and its
  default is `-`.

uvicorn writes its access line inside the request's own task, so the line sees the id with no
extra code. The middleware is a short example in [setup-example.md](setup-example.md), not a
library to install; the package `asgi-correlation-id` does the same job (section 12).

## 8. Agents: dialogue, trace and tool calls

An application that calls a language model has two records of a run: the log, which says what
happened, and the trace, which keeps what was said.

- **Keep the content in a trace store.** Prompts, answers, and tool arguments and results go
  there, never to the log. This practice strongly recommends Langfuse: it is open source (MIT,
  except its `ee` folders), it can be self-hosted, its Python SDK is built on OpenTelemetry, and
  it plugs into LangChain and LangGraph with `from langfuse.langchain import CallbackHandler`
  passed as `config={"callbacks": [handler]}`. LangSmith is the other common choice. What the
  trace store keeps is a data decision of its own; LangSmith's docs: "Redaction is not access
  control".
- **Mark every line of a run with the dialogue.** Set a `thread_id` `ContextVar` at the one
  place the graph is invoked; the Filter adds it to every record. LangGraph copies the context
  into its nodes and into sync tools run in a thread, so they see it too. Never use `run_id` as
  the key: LangGraph does not persist it, LangSmith ignores a custom one, and the Agent Server's
  `run_id` is the platform's id, not a trace id.
- **Link each line to its trace.** The Filter reads the trace id when the record is written:
  `opentelemetry.trace.get_current_span()` for OpenTelemetry and Langfuse, or
  `langsmith.get_current_run_tree().trace_id` for LangSmith. With no tracer running, the field
  is `-`. The request's root span (below) is open while the run works, so every line of the run
  carries the id. Never call a trace store's `get_url()` for a log line, because it may call the
  backend.
- **Put the request id into the root span's `metadata`,** so a trace leads back to its log lines
  too.
- **Do not use the OpenTelemetry `gen_ai.*` names for log fields.** Those conventions are still
  in Development and moved to a new repository in 2026. Name your own fields, with units.
- **Log a handled tool error once, at `WARNING`, where it is handled:** in the agent's
  `wrap_tool_call` middleware, or in the `on_error` function of `ToolErrorMiddleware`. Never
  also in the tool itself. Nothing in LangChain logs it for you. `ToolNode`, `ToolRetryMiddleware`
  and `ToolErrorMiddleware` turn the error into a message for the model and write no log. A tool
  error that nobody handles propagates and is logged once by the caller (section 5). An expected
  outcome, such as "no such order", is a normal tool result, not a tool error, and is not logged.
- **Never leave `set_debug(True)` or `set_verbose(True)` in code.** `set_debug` prints every
  input and output, prompts included, with `print()`, past the log levels, the Filter and the
  formatter.
- **Callback handlers do not log.** A sync handler in an async run runs in a copy of the context
  unless it sets `run_inline = True`, and whatever it writes to a `ContextVar` is lost.

**One request, one trace.** A trace is one unit of work, such as one chatbot turn that retrieves
context, calls the model and returns the answer (Langfuse, "What does a good trace look like?").
LangChain's handler does not group calls by itself: "each invocation will end up on its own
trace" (Langfuse's LangChain docs). An endpoint that retrieves documents, runs an agent and writes
a summary leaves three traces, and nothing in them shows that they answered one request.

- **The adapter opens one root span per request, around the use case call.** Every model call
  of the request then runs inside it: the handler's runs, `@observe` functions and spans you open
  by hand nest under it by themselves. With Langfuse it is
  `start_as_current_observation(as_type="span", ...)`, called in `core/langfuse_client.py`. Open
  it for a request with one model call too: the same span puts the trace id on the log lines, and
  a second call added later lands in the same trace. A CLI command or a worker's job opens its root
  the same way, at its own entry point. An eval run opens none: the experiment runner gives each
  case its own trace ([evals.md](../evals/evals.md) section 9).
- **Set the input and the output on the root span, never on the trace.** Langfuse SDK v4 marks
  `set_current_trace_io()` deprecated and takes the trace's input and output from the root span,
  and on Langfuse Cloud the LLM judges that read trace-level input stop on 16 November 2026. Set
  them to what a reviewer needs at a glance: the question the user sent and the answer the
  request returns. Never the raw request, a dependency object or the function's arguments.
  `@observe` on a route records exactly those, so the route opens the root through
  `core/langfuse_client.py` with an explicit input, never with `@observe`.
- **Right after the root span opens, pass the trace's attributes with
  `propagate_attributes(...)`.** The root, which is open when the block starts, and every span
  created inside the block get them; any other span created earlier does not, and Langfuse counts cost per
  user only over the spans that carry the user id. Pass ids, not text: a value
  over 200 characters is dropped with only a warning. Pass them in this one place, never also as
  the run's `langfuse_*` metadata keys; in async LangChain runs those reach only the run's first
  span (langfuse issue #16177).
- **The environment and the release belong to the trace client, not to a request.** Pass them
  once, where the client is built (`Langfuse(environment=..., release=...)`), from the settings
  ([python.md](../language/python.md) section 5); given nothing, the SDK reads its own variables.
  When the prompts live in the code, the commit is the release, and so the prompts' version.
- **A route that streams its answer opens the root span and passes its attributes inside the
  generator that yields the body.** Starlette sends a `StreamingResponse` body after the route has
  returned, so a span the route opened has closed before the stream makes its first model call.
- **A `BackgroundTasks` function is a trace of its own.** It runs after the request's root span
  has closed, so it opens its own root span with the request's id in its metadata and the same
  `session_id` and `user_id`: the request id ties it to the request, the session to the dialogue.
  Do not join it to the request's trace with `trace_context`: its cost and duration would land in
  a request that has already answered, and Langfuse users report the last span overwriting the
  trace's name and output (discussion #11127). A task started with `asyncio.create_task` is
  different: it copies the request's context, so its spans stay in the request's trace, even after
  the root has closed; work that must outlive the response goes through `BackgroundTasks` or a
  worker instead.
- **Run blocking work inside a request with `asyncio.to_thread`,** which copies the context. A bare
  `loop.run_in_executor` does not, and the model calls it makes start traces of their own.
- **Shut the trace client down when the service stops,** from the app's lifespan, so the spans
  still in its buffer are sent. Langfuse registers an exit hook for this, and still asks
  long-running services to call `shutdown()` when they get a shutdown signal.

What to set on the root span:

| What | Value | Where | Why |
|---|---|---|---|
| name | the operation, verb first, the same on every call: `answer-ticket`, from the module's `consts.py` ([file-structure.md](../../any-language/file-structure/file-structure.md) section 3) | the span's `name` | evaluators, dashboards and saved filters find spans by name; an id or a model name in it makes a new name on every trace |
| input | what the user sent, such as the question | the span's `input`, when it opens | the trace list shows it as the trace's input |
| output | what the request returns, such as the answer | the span's `output`, before it closes | the trace list shows it as the trace's output |
| request id | the id from section 7 | the span's `metadata` | the trace leads back to its log lines |
| trace name | the span's name | `propagate_attributes(trace_name=...)` | the SDK puts it on every span of the request; without it, only Langfuse's server falls back to the root span's name |
| session | the dialogue's `thread_id` | `propagate_attributes(session_id=...)` | the requests of one dialogue show as one session |
| user | the user's id in your own system, never an email | `propagate_attributes(user_id=...)` | cost and quality per user |
| tags | values known before the run, such as the channel | `propagate_attributes(tags=[...])` | a tag is fixed when its span is created |

A LangGraph run that stops for a person (an interrupt) and resumes in a later request gives one
trace per request; the shared `session_id` shows them as one dialogue. `request_trace`, the one
function that opens the root span and passes its attributes, is in `core/langfuse_client.py` in
[agent-example.md](agent-example.md); a request with three model calls under one root, and a
streaming route, are in [trace-example.md](trace-example.md).

**Optional: one line per model call and per tool call.** To see an agent's pace in the terminal
without opening the trace store, add one agent middleware that logs, at `INFO`:

- one line per finished model call, with its duration and its finish reason;
- one line per finished tool call, with the tool name and its duration.

Token counts stay in the trace store. The ids come from the Filter, so the middleware adds none.
A tool the agent calls very often may log at `DEBUG`. In a graph you build by hand, the one
client of the model and `ToolNode(wrap_tool_call=...)` take the middleware's place.

The wiring, the run line of section 9 and the optional middleware are in
[agent-example.md](agent-example.md).

## 9. Summary lines

A summary line is added to the normal lines of a request or a run, never used instead of them.
One wide record per request that replaces the other lines needs code that collects fields across
the request, and a request that crashes before it writes the record leaves nothing.

- **An HTTP request:** uvicorn's access line, with the request id from the Filter, is the
  summary. No request log of your own.
- **An agent run:** one `INFO` line, written by the code that invoked the graph, from the value
  the run returned: its outcome, its duration and a few counts. A failed run writes its one
  `ERROR` instead (section 5).
- **Latency is a metric.** Read its distribution from metrics, not by parsing log lines.

This is Stripe's canonical log line, as Brandur Leach described it: "a big log line ... that gets
emitted at the end of a request", in addition to the normal lines.

## 10. What never goes into a log

At every level, `DEBUG` included, a log line never carries:

- **secrets:** tokens, keys, passwords, session ids, connection strings, authorization headers,
  pre-signed URLs, or any URL with a query string;
- **content:** prompt text, model answers, tool arguments and results, documents, user text, or
  a value the code exists to hide.

Log instead what lets a reader find and size the event: ids, lengths, counts, short hashes,
durations, model names, statuses.

- **Exception text is data.** A provider's or a tool's error message can repeat the request. The
  one client of that system raises its own error with a safe message, `from None`, and puts the
  status and the model into that error, so the `logger.exception` above it leaks nothing.
- **Never build a log path or a logger name from input.** A name built from a request field is a
  path traversal waiting to happen.

OWASP's logging cheat sheet lists the secrets and adds "data of a higher security classification
than the logging system". OpenTelemetry's GenAI conventions make the same choice for traces:
"By default, no prompt content or tool arguments are captured".

```python
# good: what a reader needs to find and size the event
logger.info("Document %s indexed", doc_id, extra={"pages": 12, "sha256_8": digest[:8]})

# bad, at any level
logger.debug("Prompt: %s", prompt)  # user content
logger.info("Fetched %s", presigned_url)  # a URL that is a credential
logger.warning("Tool failed: %s", exc)  # a tool's error text can repeat its input
```

## 11. Checks: reasonable, not strict

Check a rule only where a check is cheap and a miss is costly or silent. Do not build a gate for
every rule.

- **Turn on the logging rules in the linter the project already runs.** In ruff 0.16 these are
  stable: `G` (a pre-formatted message, an `extra=` key that clashes with a record attribute,
  `exc_info` misuse), `LOG` (a root logger call, `Logger()` built directly, `.exception()`
  outside `except`), `TRY400` (`.error()` inside `except` where `.exception()` belongs),
  `TRY401`, `BLE001` (a blind `except`) and `T201` (`print`). They cost nothing and catch the
  mechanical half of sections 2, 3 and 5.
- **Review covers the rest:** who handles an exception, whether a warning will be read, which
  field someone filters on, whether a line carries content. The `grep` lines in this file help a
  reviewer. They are not gates.
- **No tests on log output.** A test that asserts a line's text breaks on every rewording, and it
  tests the words, not the behaviour.

A study of 4,550 pull requests by coding agents found that the agents ignored the logging
instructions they were given in 67% of the cases (Ouatiti et al., 2026). That is the reason the
mechanical half goes to the linter and not to more prose.

## 12. Where it stops holding

- **The LangGraph Agent Server** runs your graph, so your code owns no `main()`. Set logging only
  through its settings (`LOG_LEVEL`, and `LOG_JSON=true` in deployed environments), and never
  replace its formatter. Its formatter already adds `run_id`, `thread_id`, `request_id` and
  `langgraph_node` to each record: replace it and those fields are gone. Those fields were read
  from older releases, so check the fields on the version you run.
- **structlog** is fine for a team that already uses it, as long as its chain extends the host
  framework's formatter and never replaces it. Its `ProcessorFormatter` renders standard
  `getLogger(__name__)` records too.
- **python-json-logger** is an accepted ready-made JSON formatter: it is maintained, and it
  prints `extra=` fields by default. **asgi-correlation-id** is an accepted ready-made request-id
  middleware.
- **An own line per HTTP request:** when the service has no metrics, the request-id middleware
  can also time the call and log one line per request (method, route, status, `duration_ms`),
  written in `finally` so a 500 gets it too. Turn off uvicorn's access line then, so each request
  has one summary.
- **The node name:** when several graph nodes share one module, the logger name no longer tells
  them apart. A Filter in the agent module can add `langgraph_node` from `get_config()` (it raises
  `RuntimeError` outside a run). It reads one agent module's graph, so it lives in that module
  (file-structure.md section 4), never in `core/logging.py`, which every process imports, the CLI
  included.
- **An APM or an OpenTelemetry HTTP instrumentation in the same process,** such as
  `opentelemetry-instrumentation-fastapi`, or Sentry's SDK where it runs on OpenTelemetry (Python
  `sentry_sdk` 3 and later): its server span becomes the parent of the request's
  root span, and Langfuse's spans take that trace's id and its sampling decision. Requests can
  then merge into one trace, or none reach Langfuse when the incoming trace is not sampled. Read
  Langfuse's FAQ on an existing OpenTelemetry or Sentry setup before you add one; it shows how to
  give Langfuse a tracer provider of its own.
- **A handler that must block,** such as a file you are required to keep: put it behind a
  `QueueHandler`. Start and stop the listener yourself, give the queue a limit, put the
  formatter on the `QueueHandler`, and set logging up again in each forked worker.
- **Library code** follows section 2's last rule and nothing else in this file.
- **A command-line tool** logs to stderr and maps `-v` and `-q` to levels; its output for the
  user goes to stdout (clig.dev).

## 13. Sources

The Python docs: the Logging HOWTO, the Logging Cookbook ("Dealing with handlers that block",
the contextvars recipe), and the `logging`, `logging.config` and `logging.handlers` references
(3.14); PEP 750. uvicorn 0.54 source (`config.py`, `run_asgi`, the access logger) and discussion
#2673 on `--workers`; Starlette 1.7 middleware docs and `ServerErrorMiddleware` source; FastAPI
0.141 source; pytest's "How to manage logging". Google Python Style Guide, section 3.10;
OpenStack oslo.log guidelines; MediaWiki "Structured logging"; GitLab's development logging
guide; Microsoft's Code-With Engineering Playbook, "Logging"; The Twelve-Factor App, "Logs";
clig.dev; Google SRE book, chapter 6. Dave Cheney, "Let's talk about logging" (2015); Nicole
Tietz-Sokolskaya, "The only two log levels you need are INFO and ERROR" (2024); Brandur Leach,
"Canonical log lines" (2016); Charity Majors on structured events (2019, 2024); Jeremy Morrell,
"A practitioner's guide to wide events" (2024). OWASP Logging Cheat Sheet and Top 10:2025 A09.
OpenTelemetry Python API source (1.45) and the GenAI semantic conventions repository. LangChain
core source (1.4 to 1.6), LangChain agents middleware (1.4.2), LangGraph source (1.2) and
langgraph-prebuilt (`ToolNode`), the LangSmith SDK (0.14) and docs, Langfuse's docs and
repository. For the root span, read 2026-10-01: Langfuse's "What does a good trace look like?",
"Instrumentation", the LangChain integration page, "Upgrade path Python v3 to v4", the FAQs
"Why are the input and output of my trace empty?", "LLM-as-a-judge migration", "Existing
OpenTelemetry setup", "Existing Sentry setup" and "Dashboard changes in v4", and the Python SDK
4.16.0 source (`propagate_attributes`, `start_as_current_observation`, the LangChain
`CallbackHandler`); langfuse issues #16177 and #13590 and discussion #11127 (2025–2026);
Starlette 1.7 `StreamingResponse` and `BackgroundTask` source; CPython's `asyncio.to_thread` and
`loop.run_in_executor`. ruff's rule reference (0.16.9). LiteLLM issue #35699 (2026) for the f-string
measurement; Ouatiti, Sayagh, Li and Hassan, arXiv:2604.09409 (2026), on agents and logging
instructions.
