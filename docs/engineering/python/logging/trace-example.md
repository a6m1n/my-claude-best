# Example: one request, one trace

A worked example for [logging.md](logging.md) section 8, "One request, one trace". It continues the
application of [agent-example.md](agent-example.md): the same `core/langfuse_client.py`, the same
Langfuse handler built once at start-up. A support module, `support/ticket/`, answers a customer's
ticket in three steps, and each step is one LangChain call: it finds help articles (a retriever),
lets an agent answer with them, and has a model write a one-line note for the support team. Every
name is a placeholder.

What each part does for the trace:

- the HTTP adapter opens the request's root span with `request_trace`, so the three steps land in
  one trace, and puts the ticket text, the reply, the request id, the dialogue and the customer on
  it;
- the use case gives each step a stable name through `run_name`, so the steps under the root read
  like a list of what the request did;
- a route that streams its reply opens the root span inside the generator that yields the body.

## `support/ticket/consts.py` and `support/ticket/schemas.py`: the names

```python
# support/ticket/consts.py
from typing import Final

# The request's trace name; logging.md section 8 says how to pick one.
SUPPORT_TICKET_TRACE_NAME: Final = "answer-ticket"
```

```python
# support/ticket/schemas.py, next to Ticket and TicketAnswer
from typing import Literal, TypeAlias

# The names of the steps under the root span. Like the trace name, they are an API for
# evaluators and dashboards, so the set is declared once and the checker rejects any other name.
TicketStep: TypeAlias = Literal["find-articles", "answer-customer", "write-ticket-note"]
```

The module's model constants sit in `consts.py` too, as in [agent-example.md](agent-example.md);
they are not shown. The step names are a closed set, so they are a `Literal` alias, not bare
strings ([python.md](../language/python.md) section 3).

## `support/ticket/usecase.py`: three steps, one handler

```python
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from acme.core.logging import thread_id
from acme.support.ticket.graph import TicketFlow
from acme.support.ticket.schemas import Ticket, TicketAnswer, TicketStep


async def answer_ticket(
    ticket: Ticket, flow: TicketFlow, tracing: BaseCallbackHandler
) -> TicketAnswer:
    # Every line of this run carries it, in nodes and tools too.
    thread_id.set(ticket.thread_id)

    # The adapter's root span is the current span, so all three calls nest under it.
    articles = await flow.find_articles.ainvoke(
        ticket.text, _traced(tracing, "find-articles")
    )

    output = await flow.agent.ainvoke(
        {"messages": [HumanMessage(ticket.text)], "articles": articles},
        _traced(tracing, "answer-customer"),
        version="v2",
    )
    reply = output.value["structured_response"]

    note = await flow.write_note.ainvoke(
        {"question": ticket.text, "reply": reply.text},
        _traced(tracing, "write-ticket-note"),
    )

    return TicketAnswer(reply=reply.text, note=note.text)


def _traced(tracing: BaseCallbackHandler, step: TicketStep) -> RunnableConfig:
    # The handler names the step's span after run_name.
    return {"callbacks": [tracing], "run_name": step}
```

Each call passes the same handler, and none of them opens a trace of its own: the handler nests its
spans under the current span, which is the adapter's root span. The calls pass no `langfuse_*`
metadata keys, because the root span already carries the trace's attributes (logging.md section 8).

`graph.py` builds `TicketFlow` once, at start-up: the retriever, the agent made by `create_agent`
with an `articles` field in its state, and the chain that writes the note. Each model call in it
takes its model from a `<purpose>_llm_model` constant and returns its answer through a response
schema ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md)
sections 11 and 15). The rest of `schemas.py` holds `Ticket` (`customer_id`, `thread_id`,
`text`) and `TicketAnswer` (`reply`, `note`). The run's summary line ([logging.md](logging.md) section 9) is the
same as in [agent-example.md](agent-example.md) and is left out here; so are `graph.py` and
the rest of `schemas.py`.

## `api/routes_ticket.py`: the root span around the use case

```python
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from acme.api.auth import current_customer_id
from acme.api.schemas import TicketRequest, TicketResponse
from acme.core.langfuse_client import request_trace
from acme.core.logging import request_id
from acme.support.ticket.consts import SUPPORT_TICKET_TRACE_NAME
from acme.support.ticket.schemas import Ticket
from acme.support.ticket.usecase import answer_ticket

router = APIRouter()


@router.post("/tickets/answer")
async def ticket_answer(
    body: TicketRequest,
    request: Request,
    customer_id: Annotated[str, Depends(current_customer_id)],
) -> TicketResponse:
    ticket = Ticket(customer_id=customer_id, thread_id=body.thread_id, text=body.text)
    # The request's root span: the retrieval, the agent and the note nest under it as one trace.
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
email. `build_app` keeps the flow on `app.state` as `ticket_flow`, next to the handler of
[agent-example.md](agent-example.md).

## What the trace shows

One trace per request. The trace's name comes from `consts.py` and the steps' names from
`TicketStep`; the agent's own model and tool calls are named by LangGraph:

```
answer-ticket            span        input: the ticket text, output: the reply
├── find-articles        retriever   the query and the articles it found
├── answer-customer                  the agent's run
│   ├── …                generation  each model call, with its tokens and cost
│   └── …                tool        each tool call
└── write-ticket-note                the chain that wrote the note
    └── …                generation  the model call, with the note as its output
```

Every span in it carries the trace name, the session (the dialogue's `thread_id`) and the user,
because `request_trace` passes them with `propagate_attributes` before the first step starts. The
trace id on every log line of the run opens the trace, and the request id in the root span's
metadata leads from the trace back to the log lines. With the release that `start_tracing` sets
on the client as the prompts' version, the trace carries all three things
[production.md](../evals/production.md) section 2 asks for: the model's version on each
generation, the prompts' version and the user's session.

Without the root span, the same request leaves three traces, `find-articles`, `answer-customer`
and `write-ticket-note`, each with only its own input and output, and nothing that shows they
answered one ticket.

## `api/routes_ticket.py`, streaming: the root span inside the generator

The generator that yields the body opens the root span; [logging.md](logging.md) section 8 says
why the route cannot.

```python
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from langchain_core.callbacks import BaseCallbackHandler

from acme.api.auth import current_customer_id
from acme.api.schemas import TicketRequest
from acme.core.langfuse_client import request_trace
from acme.core.logging import request_id
from acme.support.ticket.consts import SUPPORT_TICKET_TRACE_NAME
from acme.support.ticket.graph import TicketFlow
from acme.support.ticket.schemas import Ticket
from acme.support.ticket.usecase import stream_ticket_reply

...


@router.post("/tickets/answer/stream")
async def ticket_answer_stream(
    body: TicketRequest,
    request: Request,
    customer_id: Annotated[str, Depends(current_customer_id)],
) -> StreamingResponse:
    ticket = Ticket(customer_id=customer_id, thread_id=body.thread_id, text=body.text)
    chunks = _traced_reply(ticket, request.app.state.ticket_flow, request.app.state.tracing)

    return StreamingResponse(chunks, media_type="text/plain")


async def _traced_reply(
    ticket: Ticket, flow: TicketFlow, tracing: BaseCallbackHandler
) -> AsyncIterator[str]:
    # Opened here, not in the route: Starlette sends the body after the route has returned.
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
        finally:
            # A client that disconnects stops the stream early; the root still records what was yielded.
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
