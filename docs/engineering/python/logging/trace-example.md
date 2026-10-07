# Example: one request, one trace

A worked example for [logging.md](logging.md) section 8, "One request, one trace". It continues the
application of [agent-example.md](agent-example.md): the same `core/langfuse_client.py`, the same
Langfuse handler built once at start-up. A support module, `support/answer_ticket/`, answers a
customer's ticket in three steps, and each step is one LangChain call: it finds help articles (a
retriever), lets an agent answer with them, and has a model write a one-line note for the support
team. Every name is a placeholder.

What each part does for the trace:

- the HTTP adapter opens the request's root span with `request_trace`, so the three steps land in
  one trace, and puts the ticket text, the reply, the request id, the dialogue and the customer on
  it;
- the use case gives each step a stable name through `run_name`, so the steps under the root read
  like a list of what the request did;
- a route that streams its reply opens the root span inside the generator that yields the body.

## `support/answer_ticket/consts.py` and `support/answer_ticket/schemas.py`: the names

```python
# support/answer_ticket/consts.py
from typing import Final

# Evaluators and dashboards find the request's trace by this name, so keep it stable
# (logging.md section 8).
SUPPORT_TICKET_TRACE_NAME: Final = "answer-ticket"
```

```python
# support/answer_ticket/schemas.py, next to Ticket and TicketAnswer
from enum import StrEnum, unique


# The names of the steps under the root span. Like the trace name, they are an API
# for evaluators and dashboards, so the set is declared once and the checker rejects
# any other name. The use case names each step, so a StrEnum (python.md section 2).
@unique
class TicketStep(StrEnum):
    FIND_ARTICLES = "find-articles"
    ANSWER_CUSTOMER = "answer-customer"
    WRITE_TICKET_NOTE = "write-ticket-note"
```

The module's model constants sit in `consts.py` too, as in [agent-example.md](agent-example.md);
they are not shown. The step names are a closed set, so they are a type, not bare strings
([python.md](../language/python.md) section 3), and the use case writes each one by name, so the
type is a `StrEnum` ([python.md](../language/python.md) section 2). A member is a `str` whose value
is the step's name, so `run_name` and the span name Langfuse shows are the plain value.

## `support/answer_ticket/usecase.py`: three steps, one handler

The use case leaves out two parts that [agent-example.md](agent-example.md) shows or names for
`answer`: the run's summary line ([logging.md](logging.md) section 9) and the check of the parsed
values ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md)
section 11), such as rejecting an empty reply or note.

```python
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from acme.core.logging import thread_id
from acme.support.answer_ticket.graph import TicketFlow
from acme.support.answer_ticket.schemas import Ticket, TicketAnswer, TicketStep


async def answer_ticket(
    ticket: Ticket, flow: TicketFlow, tracing: BaseCallbackHandler
) -> TicketAnswer:
    # Every line of this run carries it, in nodes and tools too (logging.md section 8).
    thread_id.set(ticket.thread_id)

    # The adapter's root span is the current span, so all three calls nest under it
    # (logging.md section 8).
    articles = await flow.find_articles.ainvoke(
        ticket.text, _traced(tracing, TicketStep.FIND_ARTICLES)
    )

    # version="v2": the output is typed, so .value["structured_response"] is the
    # schema's model.
    output = await flow.agent.ainvoke(
        {"messages": [HumanMessage(ticket.text)], "articles": articles},
        _traced(tracing, TicketStep.ANSWER_CUSTOMER),
        version="v2",
    )
    reply = output.value["structured_response"]

    # An agent, so its call gets the cache switch (prompt-engineering.md section 17).
    note_output = await flow.write_note.ainvoke(
        {"messages": [HumanMessage(ticket.text)], "reply": reply.text},
        _traced(tracing, TicketStep.WRITE_TICKET_NOTE),
        version="v2",
    )
    note = note_output.value["structured_response"]

    return TicketAnswer(reply=reply.text, note=note.text)


def _traced(tracing: BaseCallbackHandler, step: TicketStep) -> RunnableConfig:
    # The handler names the step's span after run_name.
    return {"callbacks": [tracing], "run_name": step}
```

Each call passes the same handler, and none of them opens a trace of its own: the handler nests its
spans under the current span, which is the adapter's root span. The calls pass no `langfuse_*`
metadata keys, because the root span already carries the trace's attributes (logging.md section 8).

`graph.py` builds `TicketFlow` once, at start-up: the retriever, the agent made by `create_agent`
with an `articles` field in its state, and the note writer, made by `create_agent` too, with no
tools and a `reply` field in its state. Each model call in it follows
[prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) sections 11,
15 and 17. The note writer is an agent, not a plain chain, so `graph.py` gives both agents the
middlewares `provider_middlewares(...)` of `core/openai_client.py` returns, as the agent of
[agent-example.md](agent-example.md) gets them: the cache switch and the two error middlewares are
agent middlewares, and a chain's call would skip them. The rest
of `schemas.py` holds `Ticket` (`customer_id`, `thread_id`, `text`) and `TicketAnswer` (`reply`,
`note`). `graph.py` and the rest of `schemas.py` are left out.

## `api/routes_answer_ticket.py`: the root span around the use case

```python
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from acme.api.auth import current_customer_id
from acme.api.schemas import TicketRequest, TicketResponse
from acme.core.langfuse_client import request_trace
from acme.core.logging import request_id
from acme.support.answer_ticket.consts import SUPPORT_TICKET_TRACE_NAME
from acme.support.answer_ticket.schemas import Ticket
from acme.support.answer_ticket.usecase import answer_ticket

router = APIRouter()


@router.post("/tickets/answer")
async def ticket_answer(
    body: TicketRequest,
    request: Request,
    customer_id: Annotated[str, Depends(current_customer_id)],
) -> TicketResponse:
    ticket = Ticket(customer_id=customer_id, thread_id=body.thread_id, text=body.text)
    # The request's root span: the retrieval, the agent and the note nest under it as
    # one trace (logging.md section 8).
    with request_trace(
        SUPPORT_TICKET_TRACE_NAME,
        request_input=ticket.text,
        request_id=request_id.get(),
        session_id=ticket.thread_id,
        user_id=ticket.customer_id,
    ) as trace:
        result = await answer_ticket(
            ticket, request.app.state.ticket_flow, tracing=request.app.state.tracing
        )
        trace.record_output(result.reply)

    return TicketResponse(reply=result.reply, note=result.note)
```

The root span's input is the ticket text and its output the reply the customer reads: what a
reviewer needs at a glance in the trace list, not the request body or the route's arguments. The
note keeps its own output on the step that wrote it. The customer id comes from the caller's
authentication (`api/auth.py`, not shown), never from the body, and it is the shop's own id, not an
email. `TicketRequest` (`api/schemas.py`, not shown) bounds `thread_id` with a pattern: the
customer controls it, and Langfuse drops a session id over 200 characters
([python.md](../language/python.md) section 4). `build_app` keeps the flow on `app.state` as
`ticket_flow`, next to the handler of [agent-example.md](agent-example.md).

## What the trace shows

One trace per request. The trace's name comes from `consts.py` and the steps' names from
`TicketStep`; the agent's own model and tool calls are named by LangGraph:

```
answer-ticket            span        input: the ticket text, output: the reply
├── find-articles        retriever   the query and the articles it found
├── answer-customer                  the agent's run
│   ├── …                generation  each model call, with its tokens and cost
│   └── …                tool        each tool call
└── write-ticket-note                the agent that wrote the note
    └── …                generation  the model call, with the note as its output
```

Every span in it carries the trace name, the session (the dialogue's `thread_id`) and the user,
because `request_trace` passes them with `propagate_attributes` before the first step starts. The
trace id on every log line of the run opens the trace, and the request id in the root span's
metadata leads from the trace back to the log lines. With the release that `start_tracing` sets
on the client as the prompts' version, the trace carries what
[production.md](../evals/production.md) section 2 asks a production trace to carry.

Without the root span, the same request leaves three traces, `find-articles`, `answer-customer`
and `write-ticket-note`, each with only its own input and output, and nothing that shows they
answered one ticket.

## `api/routes_answer_ticket.py`, streaming: the root span inside the generator

The generator that yields the body opens the root span; [logging.md](logging.md) section 8 says
why the route cannot.

```python
import asyncio
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from langchain_core.callbacks import BaseCallbackHandler

from acme.api.auth import current_customer_id
from acme.api.schemas import TicketRequest
from acme.core.langfuse_client import request_trace
from acme.core.logging import request_id
from acme.support.answer_ticket.consts import SUPPORT_TICKET_TRACE_NAME
from acme.support.answer_ticket.graph import TicketFlow
from acme.support.answer_ticket.schemas import Ticket
from acme.support.answer_ticket.usecase import stream_ticket_reply

...


@router.post("/tickets/answer/stream")
async def ticket_answer_stream(
    body: TicketRequest,
    request: Request,
    customer_id: Annotated[str, Depends(current_customer_id)],
) -> StreamingResponse:
    ticket = Ticket(customer_id=customer_id, thread_id=body.thread_id, text=body.text)
    chunks = _traced_reply(
        ticket, request.app.state.ticket_flow, request.app.state.tracing
    )

    return StreamingResponse(chunks, media_type="text/plain")


async def _traced_reply(
    ticket: Ticket, flow: TicketFlow, tracing: BaseCallbackHandler
) -> AsyncIterator[str]:
    # Opened here, not in the route: Starlette sends the body after the route has
    # returned (logging.md section 8).
    with request_trace(
        SUPPORT_TICKET_TRACE_NAME,
        request_input=ticket.text,
        request_id=request_id.get(),
        session_id=ticket.thread_id,
        user_id=ticket.customer_id,
    ) as trace:
        yielded: list[str] = []
        try:
            async for chunk in stream_ticket_reply(ticket, flow, tracing=tracing):
                yielded.append(chunk)
                yield chunk
        except (GeneratorExit, asyncio.CancelledError):
            # The stream stopped early: the root is marked, so a judge's rule and a
            # reviewer can tell a cut reply.
            trace.mark_cut()
            raise
        finally:
            # Runs on every exit: the end, a client that disconnects, a failure.
            # The root records what the customer received.
            trace.record_output("".join(yielded))
```

`stream_ticket_reply` is the use case's streaming entry in `usecase.py`: the same three steps,
with the agent's answer yielded in chunks; it is not shown. The generator runs inside the same
request, so it reads the request id the way the route does.

When the client disconnects, the stream stops early, and the generator is closed either at once or
later, when Python collects it. `finally` records the part that was yielded in both cases; a line
placed after the loop would never run, and the trace would show no output at all. A generator
closed later is closed in another task: by the source of Langfuse SDK 4.16.0 and OpenTelemetry, the
root then ends late and OpenTelemetry logs `Failed to detach context` at `ERROR` (langfuse issue
#13590, no released fix as of 1 October 2026).

The root of a cut stream is at level `WARNING`, and the steps under it are at `ERROR`: LangChain
reports a cancelled step as failed, and the handler maps that to `ERROR`. The root's level is what
tells a cut reply from a short answer. A judge on the root span
([production.md](../evals/production.md) section 5) skips these replies when its rule leaves out a
root at level `WARNING`. A count of observations at `ERROR` still counts their steps, and no filter
on the root removes them, because each observation is filtered on its own level; count root spans
at `ERROR` when a client that left should not count as a failure.
