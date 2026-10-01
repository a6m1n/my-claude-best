# Example: logging an agent built with LangChain

A worked example for [logging.md](logging.md), sections 8, 9 and 10. It continues the application of
[setup-example.md](setup-example.md): the same `core/logging.py`, the same Filter. A support
module, `support/chat/`, answers a customer's question with an agent made by LangChain's
`create_agent`, traced in Langfuse. Every name is a placeholder.

What each part does for the log:

- the use case marks the run with its dialogue (`thread_id`) and writes the one summary line;
- the HTTP adapter opens the request's root span around the use case, with the question, the
  answer, the request id and the dialogue on it, so every line the run writes carries the trace
  id, and `core/langfuse_client.py` is the one place that knows Langfuse;
- `core/openai_client.py`, the one client of the model provider, replaces a provider's error and
  an answer that does not parse with a safe error that names the model, so neither the provider's
  text nor the answer's text reaches the log;
- the optional middleware writes one line per model call and per tool call, and can be removed
  without changing what the agent does;
- the tool-failure handler, required when the model should recover from a tool failure, logs that
  failure once, where it turns it into a message for the model. An expected outcome, such as an
  unknown order, is a normal tool result and is not logged.

The prompts, the answers and the tool results go to Langfuse and to no log line.

The model call itself follows [prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md):
the model is a constant of the module, the reply comes back as JSON through a response schema, the
one client carries the cache switch, and the tool's description says when to call it.

## `support/chat/usecase.py`: the run, its ids and its summary line

```python
import logging
import time
from collections.abc import Sequence

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from acme.core.logging import thread_id
from acme.support.chat.graph import ChatAgent
from acme.support.chat.schemas import Answer, Question

logger = logging.getLogger(__name__)


async def answer(
    question: Question, agent: ChatAgent, tracing: BaseCallbackHandler
) -> Answer:
    # Every line of this run carries it, in nodes and tools too.
    thread_id.set(question.thread_id)

    config: RunnableConfig = {
        "configurable": {"thread_id": question.thread_id},
        # The prompt, the answer and the tool results go to Langfuse.
        "callbacks": [tracing],
    }

    started = time.perf_counter()
    output = await agent.ainvoke(
        {"messages": [HumanMessage(question.text)]}, config, version="v2"
    )
    messages = output.value["messages"]
    reply = output.value["structured_response"]

    duration_ms = round((time.perf_counter() - started) * 1000)
    logger.info("Chat run finished", extra=_run_summary(messages, duration_ms))

    return Answer(thread_id=question.thread_id, text=reply.text)


def _run_summary(
    messages: Sequence[BaseMessage], duration_ms: int
) -> dict[str, object]:
    return {
        # A run that returns ended on its reply, so this is normally "stop"; a reply cut at the
        # model's output limit raised ModelOutputCutOff before this line (core/openai_client.py).
        "outcome": messages[-1].response_metadata.get("finish_reason", "-"),
        "duration_ms": duration_ms,
        "messages": len(messages),
        "tool_calls": sum(
            len(message.tool_calls)
            for message in messages
            if isinstance(message, AIMessage)
        ),
    }
```

The use case catches nothing. A failure it cannot handle, a tool that crashed or a provider that
is down, propagates to the HTTP adapter, and uvicorn logs it once with the traceback
(logging.md section 5). Neither the provider's text nor the answer's text reaches that traceback:
`ProviderErrorMiddleware` and `AnswerErrorMiddleware` in `core/openai_client.py` replace the errors
that carry them with the errors in `core/errors.py`, which name only the model and, for
`ModelUnavailable`, the status (logging.md section 10). The `ERROR` record and the summary line of
a good run both carry the same `request_id` and `thread_id`, so one filter finds a dialogue's
whole history. `answer` leaves out the value check
[prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 11 asks for after the
parse, such as rejecting an empty `reply.text`.

`thread_id`, not the run's `run_id`, is the key: the dialogue keeps its `thread_id` across runs,
and LangGraph does not persist `run_id`. The `trace_id` field needs no code here: the HTTP
adapter opens the request's root span around this call (next section). Every line inside that
span, the use case's summary line included, carries its trace id. Langfuse's handler nests its
spans under the current span, and its trace id is the OpenTelemetry one, so the id on a line opens
the request's trace.

`answer` times the run with `time.perf_counter()` in place: the duration feeds only the log line
([readability.md](../../any-language/readability/readability.md) section 6).

## `api/routes_chat.py`: the request's root span around the use case

```python
from fastapi import APIRouter, Request

from acme.api.schemas import ChatRequest, ChatResponse
from acme.core.langfuse_client import request_trace
from acme.core.logging import request_id
from acme.support.chat.consts import SUPPORT_CHAT_TRACE_NAME
from acme.support.chat.schemas import Question
from acme.support.chat.usecase import answer

router = APIRouter()


@router.post("/chat")
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    question = Question(thread_id=body.thread_id, text=body.text)
    # The request's root span: the run's model and tool calls nest under it, and every line
    # inside it, the use case's summary line included, carries its trace id.
    with request_trace(
        SUPPORT_CHAT_TRACE_NAME,
        request_input=question.text,
        request_id=request_id.get(),
        session_id=question.thread_id,
    ) as trace:
        reply = await answer(
            question, request.app.state.chat_agent, tracing=request.app.state.tracing
        )
        trace.record_output(reply.text)

    return ChatResponse(thread_id=reply.thread_id, text=reply.text)
```

The root span carries what logging.md section 8 asks for: a stable name from the module's
`consts.py`, the customer's question as its input and the reply as its output, the request id in
its metadata, and the dialogue's `thread_id` as the session. `ChatRequest` (`api/schemas.py`, not
shown) bounds `thread_id` as `TicketRequest` does in [trace-example.md](trace-example.md). The
chat has no signed-in user, so it passes no `user_id`. A failure inside the block leaves the output
unset and propagates as before; OpenTelemetry records the exception on the root span and sets its
status to error, which Langfuse shows as level `ERROR`. A test builds the app from its own `Settings` with
`langfuse_tracing_enabled=False`: the client then records nothing, and the route runs the same.

`create_app()` passes `Settings()` to `build_app(settings)`, as in
[setup-example.md](setup-example.md), and `build_app` builds the chat model once with
`llm = chat_model(SUPPORT_CHAT_LLM_MODEL, api_key=settings.openai_api_key)` and the agent once with
`build_agent(llm, orders, model=SUPPORT_CHAT_LLM_MODEL, disable_prompt_cache=settings.disable_prompt_cache, new_request_uuid=uuid.uuid4)`,
where `orders` is the order store's client and `settings` is the `Settings` of
[setup-example.md](setup-example.md), which gains `openai_api_key: SecretStr`, the Langfuse keys
and URL, `langfuse_environment: TracingEnvironment`, `langfuse_tracing_enabled: bool = True` and
`git_commit` (not shown; the secret key is a `SecretStr` with no default) and
`disable_prompt_cache: bool = False`
([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 17). The adapter
reads the model constant and the setting in this one place and hands them on, so a test can pass a
`ChatOpenAI` with an `httpx.MockTransport` inside and a fixed UUID
([readability.md](../../any-language/readability/readability.md) section 6). `build_app` also calls
`start_tracing` with the Langfuse keys and URL from `settings`, the environment, the tracing switch,
and the commit as the release (the prompts are in git, so the commit is their version), then
builds the Langfuse handler once with `callback_handler()`, and keeps the agent and the handler on
`app.state` as `chat_agent` and `tracing`; the app's lifespan calls `stop_tracing()` when the
service stops. That wiring is not shown.

## `core/langfuse_client.py`: the one client of Langfuse

```python
"""The one client of Langfuse: every other file reaches the trace store through these functions."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Literal, TypeAlias

from langchain_core.callbacks import BaseCallbackHandler
from langfuse import Langfuse, LangfuseSpan, get_client, propagate_attributes
from langfuse.langchain import CallbackHandler
from pydantic import SecretStr

# This application's deployments; Langfuse keeps test traces out of production's views by it.
TracingEnvironment: TypeAlias = Literal["development", "staging", "production"]


def start_tracing(
    public_key: str,
    secret_key: SecretStr,
    base_url: str,
    *,
    environment: TracingEnvironment,
    release: str,
    enabled: bool,
) -> None:
    # get_client() and CallbackHandler() reuse this client and the values passed here.
    Langfuse(
        public_key=public_key,
        secret_key=secret_key.get_secret_value(),
        base_url=base_url,
        environment=environment,
        release=release,
        tracing_enabled=enabled,
    )


def stop_tracing() -> None:
    # Sends the spans still in the buffer; Langfuse asks services to call it when they stop.
    get_client().shutdown()


class RequestTrace:
    """The root span of one request, as the adapter sees it: the place its answer is recorded."""

    def __init__(self, root: LangfuseSpan) -> None:
        self._root = root

    def record_output(self, output: str) -> None:
        # Langfuse takes the trace's output from its root span.
        self._root.update(output=output)

    def mark_cut(self) -> None:
        # The client left before the end: the output is partial, and the root's level says so.
        self._root.update(
            level="WARNING", status_message="client disconnected before the end"
        )


@contextmanager
def request_trace(
    name: str,
    *,
    request_input: str,
    request_id: str,
    session_id: str | None = None,
    user_id: str | None = None,
) -> Iterator[RequestTrace]:
    with get_client().start_as_current_observation(
        as_type="span", name=name, input=request_input, metadata={"request_id": request_id}
    ) as root:
        # The root and every span created inside this block get the attributes; any other span
        # created earlier does not, so the block opens before any model call.
        with propagate_attributes(trace_name=name, session_id=session_id, user_id=user_id):
            yield RequestTrace(root)


def callback_handler() -> BaseCallbackHandler:
    return CallbackHandler()
```

`request_trace` is the one place that opens a request's root span: the adapter passes the values
and gets back only `record_output` and `mark_cut`, so no adapter calls Langfuse itself. The root is
a plain `span`, because it holds steps of several kinds; the handler gives each step under it its
own type. The example passes no tags. A service that sets them adds `tags=[...]` to the same
`propagate_attributes` call; [logging.md](logging.md) section 8 says which values qualify.

`request_trace` and `stop_tracing` reach the client through `get_client()` instead of taking it as
a parameter, which departs from
[file-structure.md](../../any-language/file-structure/file-structure.md) section 4: Langfuse's
handler and `@observe` read the client from `get_client()` by themselves, and `get_client()` builds
it from the one configuration `start_tracing` registered, so a handle passed in would add nothing.
`start_tracing` is also where a `mask_otel_spans` function goes when a service keeps some values
out of the trace store ([logging.md](logging.md) section 8); this example masks nothing.

## `core/openai_client.py`: the one client of the model provider

```python
# core/openai_client.py
"""The one client of the model provider: every model call passes through these middlewares."""

import uuid
from collections.abc import Awaitable, Callable

import openai
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.agents.structured_output import StructuredOutputValidationError
from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from openai.types import ChatModel
from pydantic import SecretStr

from acme.core.errors import (
    ModelAnswerInvalid,
    ModelOutputCutOff,
    ModelRefused,
    ModelUnavailable,
)


def chat_model(model: ChatModel, api_key: SecretStr) -> ChatOpenAI:
    return ChatOpenAI(model=model, api_key=api_key)


class PromptCacheSwitchMiddleware(AgentMiddleware):
    """disable_prompt_cache: a fresh first line of the system prompt on every call, so nothing from there on hits a cache."""

    def __init__(
        self, *, disable_prompt_cache: bool, new_request_uuid: Callable[[], uuid.UUID]
    ) -> None:
        super().__init__()
        self._disable_prompt_cache = disable_prompt_cache
        self._new_request_uuid = new_request_uuid

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        if not self._disable_prompt_cache:
            return await handler(request)

        system = (
            request.system_message.text if request.system_message is not None else ""
        )
        # First in the system prompt: a cache matches from the request's start, so
        # nothing from here on hits.
        system_message = SystemMessage(
            f"Request UUID: {self._new_request_uuid()}\n{system}"
        )

        return await handler(request.override(system_message=system_message))


class ProviderErrorMiddleware(AgentMiddleware):
    """Replaces a provider error with ModelUnavailable, which names only the model and the status."""

    def __init__(self, model: ChatModel) -> None:
        super().__init__()
        self._model = model

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        try:
            return await handler(request)
        except openai.APIStatusError as exc:
            # from None: the provider's message can quote the prompt; the model and the status say enough
            raise ModelUnavailable(self._model, exc.status_code) from None
        except openai.APIError:
            # every other provider error (connection, timeout, context overflow) has no status we need,
            # only text we must not log
            raise ModelUnavailable(self._model, None) from None


class AnswerErrorMiddleware(AgentMiddleware):
    """Replaces an answer the agent cannot use with an error that names only the model."""

    def __init__(self, model: ChatModel) -> None:
        super().__init__()
        self._model = model

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        # from None in every raise: the SDK's error and the parse error can carry the answer's text
        try:
            return await handler(request)
        except openai.LengthFinishReasonError:
            raise ModelOutputCutOff(self._model) from None
        except openai.ContentFilterFinishReasonError:
            # To the caller, a stop by the provider's content filter is a refusal.
            raise ModelRefused(self._model) from None
        except StructuredOutputValidationError as exc:
            if _is_refusal(exc.ai_message):
                raise ModelRefused(self._model) from None

            raise ModelAnswerInvalid(self._model) from None


def _is_refusal(reply: AIMessage) -> bool:
    # A refusal has no JSON, so it fails the parse; langchain-openai keeps its text under this key.
    return bool(reply.additional_kwargs.get("refusal"))
```

```python
# core/errors.py
from openai.types import ChatModel


class ModelUnavailable(Exception):
    """The model provider failed; the message names the model and the status, never the provider's text."""

    def __init__(self, model: ChatModel, status: int | None) -> None:
        super().__init__(f"model {model} unavailable (status {status})")
        self.model = model
        self.status = status


class ModelRefused(Exception):
    """The model refused; the message names the model, never the answer's text."""

    def __init__(self, model: ChatModel) -> None:
        super().__init__(f"model {model} refused")
        self.model = model


class ModelOutputCutOff(Exception):
    """The answer hit the model's limit; the message names the model, never the answer's text."""

    def __init__(self, model: ChatModel) -> None:
        super().__init__(f"model {model} stopped at its output limit")
        self.model = model


class ModelAnswerInvalid(Exception):
    """The answer did not match the schema; the message names the model, never the answer's text."""

    def __init__(self, model: ChatModel) -> None:
        super().__init__(f"model {model} gave an answer that does not match the schema")
        self.model = model
```

## `support/chat/consts.py` and `support/chat/schemas.py`: the model, the trace name and the reply's shape

```python
# support/chat/consts.py
from typing import Final

from openai.types import ChatModel

# A dated version, not a moving alias (python/evals/production.md section 6).
# gpt-4.1-mini has no reasoning effort to set (prompt-engineering.md section 15).
SUPPORT_CHAT_LLM_MODEL: Final[ChatModel] = "gpt-4.1-mini-2025-04-14"
# One LangGraph step per model call and one per round of tool calls, so 12 allows
# several tool rounds.
SUPPORT_CHAT_MAX_STEPS: Final = 12
# Evaluators and dashboards find the request's trace by this name, so keep it stable
# (logging.md section 8).
SUPPORT_CHAT_TRACE_NAME: Final = "answer-chat"
```

```python
# support/chat/schemas.py, next to Answer and Question
from pydantic import BaseModel, ConfigDict


class ChatReply(BaseModel):
    """The agent's final reply, the text the customer reads; the provider returns it as JSON in this shape."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    text: str
```

`SUPPORT_CHAT_LLM_MODEL` follows `<purpose>_llm_model`
([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 15), and `ChatModel`,
the OpenAI SDK's own `Literal`, makes a misspelt model fail the type checker
([python.md](../language/python.md) section 3). Its value is a dated version, not the alias
`gpt-4.1-mini`, which the vendor can point at a new build
([production.md](../evals/production.md) section 6). `ChatReply` is the response schema the provider
fills ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 11).

## `support/chat/graph.py` and `support/chat/services/service_orders.py`: the agent and a tool

```python
# support/chat/graph.py
import uuid
from collections.abc import Callable
from typing import TypeAlias

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import ToolErrorMiddleware
from langchain.agents.middleware.types import InputAgentState, OutputAgentState
from langchain.agents.structured_output import ProviderStrategy
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from openai.types import ChatModel

from acme.core.openai_client import (
    AnswerErrorMiddleware,
    PromptCacheSwitchMiddleware,
    ProviderErrorMiddleware,
)
from acme.core.order_store_client import OrderStore
from acme.support.chat.call_logging import CallLoggingMiddleware
from acme.support.chat.consts import SUPPORT_CHAT_MAX_STEPS
from acme.support.chat.prompts import SYSTEM
from acme.support.chat.schemas import ChatReply
from acme.support.chat.services.service_orders import order_tools
from acme.support.chat.tool_errors import report_tool_failure

ChatAgent: TypeAlias = CompiledStateGraph[
    AgentState[ChatReply], None, InputAgentState, OutputAgentState[ChatReply]
]


def build_agent(
    llm: ChatOpenAI,
    orders: OrderStore,
    *,
    model: ChatModel,
    disable_prompt_cache: bool,
    new_request_uuid: Callable[[], uuid.UUID],
) -> ChatAgent:
    # The run stops at the application's own step limit, never LangGraph's default.
    return create_agent(
        llm,
        tools=order_tools(orders),
        system_prompt=SYSTEM,
        # The provider's own strict structured output: the provider enforces the schema,
        # and the reply is the last AI message, with its finish reason.
        response_format=ProviderStrategy(ChatReply, strict=True),
        middleware=[
            ToolErrorMiddleware(on_error=report_tool_failure),
            CallLoggingMiddleware(),
            # Required: disable_prompt_cache reaches the model only through this entry.
            PromptCacheSwitchMiddleware(
                disable_prompt_cache=disable_prompt_cache,
                new_request_uuid=new_request_uuid,
            ),
            # Required, and last: the last entries are the innermost, next to the model, so
            # every other middleware sees this client's errors, never the provider's error
            # or the answer's text.
            AnswerErrorMiddleware(model),
            ProviderErrorMiddleware(model),
        ],
    ).with_config(recursion_limit=SUPPORT_CHAT_MAX_STEPS)
```

`ProviderStrategy(ChatReply, strict=True)` asks for the provider's own strict structured output:
the provider enforces the schema, and the final reply is the last AI message. LangChain's other
strategy, a tool call, would end the run on a tool message instead.

The two error middlewares split the ways a call fails by what failed. `ProviderErrorMiddleware`
handles the provider: a status error or any other API error becomes `ModelUnavailable`.
`AnswerErrorMiddleware` handles the answer, which is parsed inside the agent, in the call both
middlewares wrap:

- When a reply stops at the model's output limit, the OpenAI SDK raises
  `openai.LengthFinishReasonError` before LangChain parses the reply, and `AnswerErrorMiddleware`
  replaces it with `ModelOutputCutOff`.
- A stop by the provider's content filter raises `openai.ContentFilterFinishReasonError` at the
  same point, and `AnswerErrorMiddleware` replaces it with `ModelRefused`.
- A refusal or a reply that does not match the schema reaches LangChain's parse, whose
  `StructuredOutputValidationError` can quote the answer, so `AnswerErrorMiddleware` replaces it
  before any other code sees it: with `ModelRefused` when `_is_refusal` finds the refusal, and
  `ModelAnswerInvalid` otherwise.

The SDK's two errors are `OpenAIError`s but not `APIError`s, so `ProviderErrorMiddleware` lets them
through. Each error names only the model, and each propagates like any failure the use case cannot
handle.

The refusal and cut-off mapping holds on LangChain's Chat Completions path, which this model uses;
a model or setting that moves the call to the Responses API changes it.

`OrderStore`, the one client of the order store in `core/`, is not shown. The tool gets the store
from `order_tools`, which `build_agent` calls with the client `create_app()` builds once, so it
reads no module-level client, and the model, which fills only `order_id`, never sees the store
([readability.md](../../any-language/readability/readability.md) section 6).

```python
# support/chat/services/service_orders.py
from langchain_core.tools import BaseTool, tool

from acme.core.order_store_client import OrderStore
from acme.support.chat.errors import ToolFailure, ToolFailureReason


def order_tools(orders: OrderStore) -> list[BaseTool]:
    @tool
    def find_order(order_id: str) -> str:
        """Look up one order by its id, such as A-1042, and return its status.

        Call it when the customer asks where an order is or what happened to it.
        Reads only; changes nothing.
        """
        try:
            order = orders.get(order_id)
        except ConnectionError:
            # from None: the store's error text could quote the order; the fixed code says enough
            raise ToolFailure(ToolFailureReason.ORDER_STORE_UNAVAILABLE) from None

        if order is None:
            # An expected outcome is a normal result, so no log line.
            return "No order with this id. Ask the customer to check the id on their receipt."

        return order.status

    return [find_order]
```

```python
# support/chat/errors.py
from enum import StrEnum, unique


@unique
class ToolFailureReason(StrEnum):
    """The fixed codes a tool failure can carry, so no free text reaches the log."""

    ORDER_STORE_UNAVAILABLE = "order_store_unavailable"


class ToolFailure(Exception):
    """A tool failure the model can read and work around."""

    def __init__(self, reason: ToolFailureReason) -> None:
        super().__init__(reason)
        self.reason = reason
```

The tool raises and does not log. Whoever handles the failure logs it, and that is the
tool-failure handler below.

## `support/chat/tool_errors.py`: required when the model should recover

```python
"""The one place a tool failure the model can work around is handled, so the one place it is logged."""

import logging

from langchain.agents.middleware import ToolCallRequest

from acme.support.chat.errors import ToolFailure

logger = logging.getLogger(__name__)


def report_tool_failure(exc: Exception, request: ToolCallRequest) -> str | None:
    if not isinstance(exc, ToolFailure):
        return None  # not ours: it propagates, and the caller that decides logs it once

    logger.warning("Tool %s failed: %s", request.tool_call["name"], exc.reason)

    return f"The tool failed: {exc.reason}"
```

`create_agent`'s tool node handles only a model's invalid tool arguments and re-raises everything
else. So an agent whose model should recover from a `ToolFailure` needs this handler, passed to
`ToolErrorMiddleware` in `graph.py`: it turns the failure into an error message the model reads,
and it logs the one `WARNING`.

## `support/chat/call_logging.py`: optional, one line per call

```python
"""Optional: one terminal line per model call and per tool call; the content stays in Langfuse."""

import logging
import time
from collections.abc import Awaitable, Callable

from langchain.agents.middleware import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
    ToolCallRequest,
)
from langchain_core.messages import ToolMessage
from langgraph.types import Command

logger = logging.getLogger(__name__)


def _ms_since(started: float) -> int:
    return round((time.perf_counter() - started) * 1000)


class CallLoggingMiddleware(AgentMiddleware):
    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        started = time.perf_counter()
        response = await handler(request)

        # The key name differs by provider; a model that names it otherwise logs "-".
        finish_reason = response.result[-1].response_metadata.get("finish_reason", "-")
        logger.info(
            "Model call finished",
            extra={"duration_ms": _ms_since(started), "finish_reason": finish_reason},
        )

        return response

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command[object]]],
    ) -> ToolMessage | Command[object]:
        name = request.tool_call["name"]
        started = time.perf_counter()
        result = await handler(request)

        logger.info("Tool %s finished", name, extra={"duration_ms": _ms_since(started)})

        return result
```

Leave this middleware out and the agent behaves the same and still logs correctly: the
tool-failure handler, the summary line and any error stay. Add it when you want to watch an
agent's pace in the terminal. It adds no token counts, because Langfuse keeps them, and no ids,
because the Filter adds them to every line. A tool the agent calls many times per run can log at
`DEBUG` instead.

In a graph built by hand, the same two jobs sit in the one client of the model and in
`ToolNode(tools, wrap_tool_call=...)`.

## What a run prints

With `ACME_LOG_FORMAT=console`, one question that needed one tool call, which failed because the order
store was down (the ids are cut to eight characters here; the console line shows only the request
id, and the JSON record carries all three):

```
2026-09-27 15:21:04,310 INFO     acme.support.chat.call_logging [7f3c9a1e] Model call finished duration_ms=812 finish_reason=tool_calls
2026-09-27 15:21:04,322 WARNING  acme.support.chat.tool_errors [7f3c9a1e] Tool find_order failed: order_store_unavailable
2026-09-27 15:21:05,104 INFO     acme.support.chat.call_logging [7f3c9a1e] Model call finished duration_ms=779 finish_reason=stop
2026-09-27 15:21:05,106 INFO     acme.support.chat.usecase [7f3c9a1e] Chat run finished outcome=stop duration_ms=1631 messages=4 tool_calls=1
2026-09-27 15:21:05,107 INFO     uvicorn.access [7f3c9a1e] 192.0.2.10:53211 - "POST /chat HTTP/1.1" 200
```

The same summary line with `ACME_LOG_FORMAT=json`:

```json
{"request_id": "7f3c9a1e0b2d4c6e8f1a3b5c7d9e0f12", "thread_id": "thread-42", "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736", "outcome": "stop", "duration_ms": 1631, "messages": 4, "tool_calls": 1, "ts": "2026-09-27T15:21:05.106+00:00", "level": "INFO", "logger": "acme.support.chat.usecase", "message": "Chat run finished", "template": "Chat run finished"}
```

To see what the model was asked and what it answered, open the trace: its id is on every line the run writes.
