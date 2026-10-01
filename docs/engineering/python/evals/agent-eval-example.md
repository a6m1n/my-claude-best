# Example: the unit tests and the eval of one LangGraph agent

A worked example for [agents.md](agents.md). The agent is the support agent of
[python/logging/agent-example.md](../logging/agent-example.md): LangChain's `create_agent` with one tool,
`find_order`, and a reply in the shape `ChatReply`, built by `build_agent(llm, orders, *, model,
disable_prompt_cache, new_request_uuid)`. Here it gets unit tests that need no model and an eval
that runs the real one. Every name is a placeholder; the orders and rates are example values.

What each part does:

- `tests/support/fake_order_store.py` is the order store the tests and the eval run against;
- `tests/unit/chat/test_graph.py` checks the agent's code with a scripted model: the tool it calls,
  the reply it returns, the tool definition the model is offered, the step limit;
- `evals/chat/cases_chat.jsonl` and `evals/chat/experiment_chat.py` run the real model on the cases
  and grade what the agent did: the tools it called, by code, and its reply, by code and by the
  validated judge of [judge-example.md](judge-example.md).

## `tests/support/fake_order_store.py`: the environment

```python
# tests/support/fake_order_store.py
from collections.abc import Mapping

from typing_extensions import override

from acme.core.order_store_client import Order, OrderStatus, OrderStore


class FakeOrderStore(OrderStore):
    """An OrderStore that answers from a dict of statuses, and keeps the ids it was asked for."""

    def __init__(
        self,
        statuses: Mapping[str, OrderStatus],
        *,
        unavailable: frozenset[str] = frozenset(),
    ) -> None:
        # No super().__init__(): the fake reaches no store.
        self._statuses = statuses
        self._unavailable = unavailable
        self.asked: list[str] = []

    @override
    def get(self, order_id: str) -> Order | None:
        self.asked.append(order_id)

        if order_id in self._unavailable:
            # The error the real tool catches when the store is down.
            raise ConnectionError("order store unavailable")

        status = self._statuses.get(order_id)
        return None if status is None else Order(order_id=order_id, status=status)
```

The real store's client, its `Order` record and its `OrderStatus` are not shown in the logging
example; the fake overrides the one method the tool calls
([python/testing/fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 1).
An unknown id returns `None`, as the real store does, so the agent's "no such order" path
runs against the fake too. An id listed as unavailable raises `ConnectionError`, the error
`find_order` catches when the store is down, so the tool's failure path runs too:
[agents.md](agents.md) section 6 asks a fake tool to "return the real tool's timeouts and errors".
The unit tests and the eval use the same fake, so both agree on how the store behaves; each builds
a new one per run.

## `tests/unit/chat/test_graph.py`: the agent's code, with no model

```python
# tests/unit/chat/test_graph.py
import json
import uuid
from collections.abc import Iterator
from itertools import repeat
from typing import Final

import httpx
import pytest
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError
from pydantic import SecretStr

from acme.core.order_store_client import OrderStatus
from acme.support.chat.consts import SUPPORT_CHAT_LLM_MODEL, SUPPORT_CHAT_MAX_STEPS
from acme.support.chat.graph import ChatAgent, build_agent
from acme.support.chat.schemas import ChatReply
from tests.support.fake_order_store import FakeOrderStore

ASK_FOR_A_1042: Final[dict[str, object]] = {
    "role": "assistant",
    "content": None,
    "tool_calls": [
        {
            "id": "call_1",
            "type": "function",
            "function": {
                "name": "find_order",
                "arguments": json.dumps({"order_id": "A-1042"}),
            },
        }
    ],
}
SHIPPED_REPLY: Final[dict[str, object]] = {
    "role": "assistant",
    "content": json.dumps({"text": "Order A-1042 has shipped."}),
}


class ScriptedProvider:
    """Answers each chat completion with the next scripted message, and keeps every request body."""

    def __init__(self, messages: Iterator[dict[str, object]]) -> None:
        self._messages = messages
        self.request_bodies: list[bytes] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.request_bodies.append(request.content)

        message = next(self._messages)
        finish_reason = "tool_calls" if message.get("tool_calls") else "stop"

        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 0,
                "model": SUPPORT_CHAT_LLM_MODEL,
                "choices": [
                    {"index": 0, "message": message, "finish_reason": finish_reason}
                ],
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2,
                },
            },
        )


def offered_tools(request_body: bytes) -> list[object]:
    """The function definitions one request offered the model."""
    request = json.loads(request_body)
    return [tool["function"] for tool in request["tools"]]


def agent_on(provider: ScriptedProvider, orders: FakeOrderStore) -> ChatAgent:
    """The real agent, with the real chat model class answering from the script."""
    llm = ChatOpenAI(
        model=SUPPORT_CHAT_LLM_MODEL,
        api_key=SecretStr("key-for-tests"),
        http_async_client=httpx.AsyncClient(transport=httpx.MockTransport(provider)),
        max_retries=0,
    )
    return build_agent(
        llm,
        orders,
        model=SUPPORT_CHAT_LLM_MODEL,
        disable_prompt_cache=False,
        new_request_uuid=uuid.uuid4,
    )


class TestBuildAgent:
    """The support agent does what the model asks, through the pinned tools, within a step limit."""

    async def test_an_order_question_is_answered_from_the_store(self) -> None:
        orders = FakeOrderStore({"A-1042": OrderStatus.SHIPPED})
        agent = agent_on(
            ScriptedProvider(iter([ASK_FOR_A_1042, SHIPPED_REPLY])), orders
        )

        output = await agent.ainvoke(
            {"messages": [HumanMessage("Where is order A-1042?")]}, version="v2"
        )

        assert (orders.asked, output.value["structured_response"]) == (
            ["A-1042"],
            ChatReply(text="Order A-1042 has shipped."),
        )

    async def test_the_model_is_offered_find_order_as_pinned(self) -> None:
        """Pins: the name, description and argument schema of every tool the model is offered.

        A change to any of them changes how the model picks and fills the tool, so the agent's
        eval runs before this test is updated (prompt-engineering.md section 14).
        """
        provider = ScriptedProvider(iter([SHIPPED_REPLY]))

        await agent_on(provider, FakeOrderStore({})).ainvoke(
            {"messages": [HumanMessage("Hello")]}, version="v2"
        )

        assert offered_tools(provider.request_bodies[0]) == [
            {
                "name": "find_order",
                "description": (
                    "Look up one order by its id, such as A-1042, and return its status.\n\n"
                    "        Call it when the customer asks where an order is or what happened"
                    " to it.\n"
                    "        Reads only; changes nothing."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {"order_id": {"type": "string"}},
                    "required": ["order_id"],
                    "additionalProperties": False,
                },
                "strict": True,
            }
        ]

    async def test_a_model_that_keeps_calling_tools_stops_at_the_step_limit(
        self,
    ) -> None:
        endless = ScriptedProvider(repeat(ASK_FOR_A_1042))
        agent = agent_on(endless, FakeOrderStore({"A-1042": OrderStatus.SHIPPED}))

        with pytest.raises(
            GraphRecursionError,
            match=f"Recursion limit of {SUPPORT_CHAT_MAX_STEPS} reached",
        ):
            await agent.ainvoke(
                {"messages": [HumanMessage("Where is order A-1042?")]}, version="v2"
            )
```

Why it looks like this:

- **The real chat model class with a scripted transport** ([agents.md](agents.md) section 5): the
  `ChatOpenAI` of the application sends its real request, tools and response format included, and
  `httpx.MockTransport` answers it from the script. The calls are async, `await agent.ainvoke(...)`
  through `http_async_client`: `build_agent`'s middlewares define only async hooks, so a sync
  `invoke` raises `NotImplementedError`. LangChain's `GenericFakeChatModel` would fail
  here: it has no `bind_tools`. This is the first stand-in of
  [python/testing/fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 1, and the logging
  example's text already names it for this agent.
- **What the test can say, and what it cannot.** The script decides what the "model" answers, so the
  tests check the agent's code: that a tool call reaches the store with the model's argument, that
  the reply is parsed into `ChatReply`, that the definition the model is offered has not changed,
  and that a model that never stops is stopped. Whether the real model calls `find_order` for this
  question is the eval's job.
- **The tool definition is pinned** ([agents.md](agents.md) section 5): the test parses the request
  body the provider received and compares the whole definition, the name, the description (as the
  docstring gives it, indentation included) and the argument schema. A change to any of them turns
  it red, and a change to a tool definition runs the eval
  ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 14). The raw bodies
  are kept as bytes and parsed in `offered_tools`, so the `Any` that `json.loads` returns stays
  inside the parser ([python.md](../language/python.md) section 3).
- **The step limit is the application's**: `build_agent` sets it from `SUPPORT_CHAT_MAX_STEPS`, and
  the test passes no limit of its own, so it turns red when someone removes the limit or sets it
  to a value other than the constant's; raising the constant is a decision, not a bug, and stays
  green ([python/testing/what-to-test.md](../testing/what-to-test.md) section 3). The test asserts the
  error and its message, not a count of calls, which is LangGraph's own detail.
- **`version="v2"`**, as the logging example's use case calls the agent, so the output is typed
  and `structured_response` is a `ChatReply`.
- **One class for the unit, names that state the guarantee, a fresh agent and a fresh store in each
  test** ([python/testing/test-structure.md](../testing/test-structure.md) sections 1 to 4): the agent is
  built inside the test, so nothing carries from one test to the next. The scripted provider is used
  by this file alone, so it stays here
  ([python/testing/fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 1).

`build_agent`, `ChatAgent`, `ChatReply`, `SUPPORT_CHAT_LLM_MODEL` and `SUPPORT_CHAT_MAX_STEPS` are
those of the logging example; its `build_agent` asks for `ChatOpenAI`, which is what the test
passes.

## `evals/chat/cases_chat.jsonl`: the cases

```json
{"case_id": "shipped-order", "question": "Where is my order A-1042?", "order_statuses": {"A-1042": "shipped"}, "required_tools": ["find_order"], "allowed_tools": ["find_order"], "status_in_reply": "shipped", "budget": {"model_calls": 2, "tool_calls": 1, "seconds": 8}}
{"case_id": "unknown-order", "question": "What happened to order B-9?", "order_statuses": {}, "required_tools": ["find_order"], "allowed_tools": ["find_order"], "status_in_reply": null, "budget": {"model_calls": 2, "tool_calls": 1, "seconds": 8}}
{"case_id": "store-down", "question": "Where is my order C-3071?", "order_statuses": {}, "unavailable_order_ids": ["C-3071"], "required_tools": ["find_order"], "allowed_tools": ["find_order"], "status_in_reply": null, "budget": {"model_calls": 2, "tool_calls": 1, "seconds": 8}}
{"case_id": "no-order-id", "question": "Can I change my delivery address?", "order_statuses": {}, "required_tools": [], "allowed_tools": [], "status_in_reply": null, "budget": {"model_calls": 1, "tool_calls": 0, "seconds": 4}}
```

Each case names the tools the agent must call and the tools it may call, the store it runs
against, and its budget ([agents.md](agents.md) section 2). In `store-down` the store fails on the
order's id. The last case has no order id: the right action is to ask for one, so no tool may run.
The budget's counts are those of the shortest successful run known for the case: one model call
that asks for the tool, one tool call, and one model call that writes the reply; a shorter
successful run lowers them in the pull request that shows it. Its seconds are the 90th percentile
of the case's successful runs at the eval's `MAX_CONCURRENCY`, never the fastest run.

```python
# evals/chat/schemas.py, next to Verdict, Split, NoVerdict, PromiseVerdict and
# LabelledReply of judge-example.md, with PositiveInt, NonNegativeInt,
# PositiveFloat and model_validator imported from pydantic, OrderStatus from
# acme.core.order_store_client, Self from typing, and dataclass from dataclasses
@unique
class ToolName(StrEnum):
    FIND_ORDER = "find_order"


@unique
class RunEnd(StrEnum):
    """How one run of the agent ended; only a run that ended on its reply can pass."""

    REPLY = "reply"
    STEP_LIMIT = "step_limit"
    REFUSED = "refused"
    CUT_OFF = "cut_off"
    INVALID_ANSWER = "invalid_answer"


@unique
class Criterion(StrEnum):
    """What the agent's eval grades; each has one grader and one rate."""

    # The headline: the run passed every other criterion.
    TASK_SUCCEEDED = "task_succeeded"
    REQUIRED_TOOLS_CALLED = "required_tools_called"
    ONLY_ALLOWED_TOOLS_CALLED = "only_allowed_tools_called"
    REPLY_STATES_THE_STATUS = "reply_states_the_status"
    REPLY_KEEPS_TO_THE_STATUS = "reply_keeps_to_the_status"


@unique
class RunMeasure(StrEnum):
    """What the eval reports over the whole run, next to the rates, without gating on it."""

    WITHIN_BUDGET = "within_budget"
    TOKENS_PER_SUCCESS = "tokens_per_success"


class Budget(BaseModel):
    """The most a successful run of one case may use (agents.md section 2).

    The counts are those of its shortest successful run; the seconds are the 90th
    percentile of its successful runs.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    model_calls: PositiveInt
    tool_calls: NonNegativeInt
    seconds: PositiveFloat


class ChatCase(BaseModel):
    """One line of cases_chat.jsonl: a question, the store it runs against, and what the agent must do."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    case_id: str
    question: str
    order_statuses: dict[str, OrderStatus]
    # The ids the fake store fails on, as the real one does when it is down.
    unavailable_order_ids: frozenset[str] = frozenset()
    required_tools: frozenset[ToolName]
    allowed_tools: frozenset[ToolName]
    # The status word the reply must state, when the order exists.
    status_in_reply: OrderStatus | None
    budget: Budget

    @model_validator(mode="after")
    def required_tools_are_allowed(self) -> Self:
        """A case allows every tool it requires."""
        if self.required_tools - self.allowed_tools:
            raise ValueError("a required tool is not in allowed_tools")

        return self

    @model_validator(mode="after")
    def unavailable_orders_have_no_status(self) -> Self:
        """A case gives no status to an order the store fails on."""
        if self.unavailable_order_ids & self.order_statuses.keys():
            raise ValueError("an id in unavailable_order_ids also has a status")

        return self


@dataclass(frozen=True)
class RunUsage:
    """What one run of the agent used."""

    model_calls: int
    tool_calls: int
    tokens: int
    seconds: float


@dataclass(frozen=True)
class ChatRun:
    """What one run of the agent did: how it ended, its reply, its tools, what it used."""

    ended: RunEnd
    reply: str
    # The names the model asked for, which can include a tool that does not exist: not ToolName.
    tools_called: frozenset[str]
    order_status_seen: OrderStatus | None
    usage: RunUsage
    within_budget: bool
```

`Budget` and `ChatCase` come from the case file through `model_validate_json`, so they are strict
models, as the triage case is. `RunUsage` and `ChatRun` are built by the eval's own code from values
it already holds, so they are frozen dataclasses, like `JudgeScores`
([python.md](../language/python.md) section 4). Two rules are validators on `ChatCase`, so a case
that breaks one fails the load: a case allows every tool it requires, and it gives no status to an
order the store fails on. The fake records that id too, so `_first_status_seen` would hand the
judge a status the agent never saw. How a run ended is a closed set, so `RunEnd` is an enum
([python.md](../language/python.md) section 3), and a run that did not end on its reply is still a
`ChatRun`, so it is graded, never dropped ([evals.md](evals.md) section 6).

## `evals/chat/experiment_chat.py`: the agent's eval

```python
# evals/chat/experiment_chat.py
"""The support agent's eval: each case three times against the real model, graded on what the agent did."""

import asyncio
import logging.config
import time
import uuid
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Final

from acme_ai import AcmeAiSdk
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langfuse import Evaluation, RunnerContext, get_client
from langfuse.experiment import (
    ExperimentItemResult,
    ExperimentResult,
    LocalExperimentItem,
)
from langgraph.errors import GraphRecursionError

from acme.core.acme_ai_client import AcmeAiClient
from acme.core.config import Settings
from acme.core.errors import ModelAnswerInvalid, ModelOutputCutOff, ModelRefused
from acme.core.langfuse_client import callback_handler, start_tracing
from acme.core.logging import build_logging_config
from acme.core.openai_client import chat_model
from acme.core.order_store_client import OrderStatus
from acme.support.chat.consts import SUPPORT_CHAT_LLM_MODEL
from acme.support.chat.graph import build_agent
from evals.chat.consts import (
    UNSUPPORTED_PROMISE_JUDGE_LLM_MODEL,
    UNSUPPORTED_PROMISE_JUDGE_LLM_REASONING_EFFORT,
)
from evals.chat.judge_unsupported_promise import judge_unsupported_promise
from evals.chat.schemas import (
    Budget,
    ChatCase,
    ChatRun,
    Criterion,
    RunEnd,
    RunMeasure,
    RunUsage,
    Verdict,
)
from evals.rate_gate import check_rates
from tests.support.fake_order_store import FakeOrderStore

CASES_FILE: Final = Path(__file__).with_name("cases_chat.jsonl")
RUNS_PER_CASE: Final = 3
# How many runs are in flight at once in the one event loop. A run's seconds are
# wall-clock at this concurrency, so a time budget is compared only with runs at the same
# concurrency.
MAX_CONCURRENCY: Final = 5
# The pass rates of the version on main, the headline first. The pull request that changes them
# explains why.
BASELINE: Final[Mapping[Criterion, float]] = {
    Criterion.TASK_SUCCEEDED: 0.85,
    Criterion.REQUIRED_TOOLS_CALLED: 0.97,
    Criterion.ONLY_ALLOWED_TOOLS_CALLED: 0.98,
    Criterion.REPLY_STATES_THE_STATUS: 0.93,
    Criterion.REPLY_KEEPS_TO_THE_STATUS: 0.90,
}
MARGIN: Final = 0.05
# Tokens per successful run of the version on main, read next to the pass rate, not gated.
TOKENS_PER_SUCCESS_BEFORE: Final = 1_900


def experiment(context: RunnerContext) -> ExperimentResult:
    """The entry the langfuse/experiment-action calls; `python -m` starts at main()."""
    return run_chat_eval(context, Settings())


def run_chat_eval(context: RunnerContext, settings: Settings) -> ExperimentResult:
    cases = [
        ChatCase.model_validate_json(line)
        for line in CASES_FILE.read_text().splitlines()
    ]
    llm = chat_model(SUPPORT_CHAT_LLM_MODEL, settings.openai_api_key)
    tracing = callback_handler()
    judge_client = AcmeAiClient(
        AcmeAiSdk(api_key=settings.acme_ai_api_key.get_secret_value()),
        disable_prompt_cache=True,
        new_request_uuid=uuid.uuid4,
    )

    result = context.run_experiment(
        name="support-chat",
        data=[_item(case) for case in cases for _ in range(RUNS_PER_CASE)],
        task=lambda *, item, **kwargs: _run_agent(
            item["expected_output"], llm, tracing, clock=time.perf_counter
        ),
        evaluators=[
            required_tools_called,
            only_allowed_tools_called,
            reply_states_the_status,
            lambda **kwargs: reply_keeps_to_the_status(
                judge_client=judge_client, **kwargs
            ),
        ],
        composite_evaluator=task_succeeded,
        run_evaluators=[within_budget, tokens_per_success],
        max_concurrency=MAX_CONCURRENCY,
        # The prompts are in git, so the commit is their version (evals.md section 9).
        metadata={
            "model": SUPPORT_CHAT_LLM_MODEL,
            "judge_model": UNSUPPORTED_PROMISE_JUDGE_LLM_MODEL,
            "judge_reasoning_effort": UNSUPPORTED_PROMISE_JUDGE_LLM_REASONING_EFFORT,
            "commit": settings.git_commit,
        },
    )

    check_rates(
        result,
        runs_asked=Counter(
            case.case_id for case in cases for _ in range(RUNS_PER_CASE)
        ),
        baseline=BASELINE,
        margin=MARGIN,
    )

    return result


async def _run_agent(
    case: ChatCase,
    llm: ChatOpenAI,
    tracing: BaseCallbackHandler,
    *,
    clock: Callable[[], float],
) -> ChatRun:
    # A new store and a new agent for every run: nothing carries over (agents.md section 6).
    orders = FakeOrderStore(case.order_statuses, unavailable=case.unavailable_order_ids)
    agent = build_agent(
        llm,
        orders,
        model=SUPPORT_CHAT_LLM_MODEL,
        disable_prompt_cache=True,
        new_request_uuid=uuid.uuid4,
    )

    started = clock()
    # The model's own failure ends the run as a failed case. ModelUnavailable, the
    # provider's, is not caught: it is an error of the run (evals.md section 6).
    try:
        output = await agent.ainvoke(
            {"messages": [HumanMessage(case.question)]},
            {"callbacks": [tracing]},
            version="v2",
        )
    except GraphRecursionError:
        return _ended_early(RunEnd.STEP_LIMIT, seconds=clock() - started)
    except ModelRefused:
        return _ended_early(RunEnd.REFUSED, seconds=clock() - started)
    except ModelOutputCutOff:
        return _ended_early(RunEnd.CUT_OFF, seconds=clock() - started)
    except ModelAnswerInvalid:
        return _ended_early(RunEnd.INVALID_ANSWER, seconds=clock() - started)

    usage = _usage(output.value["messages"], seconds=clock() - started)

    return ChatRun(
        ended=RunEnd.REPLY,
        reply=output.value["structured_response"].text,
        tools_called=_tools_called(output.value["messages"]),
        order_status_seen=_first_status_seen(orders.asked, case.order_statuses),
        usage=usage,
        within_budget=_within(usage, case.budget),
    )


def _ended_early(ended: RunEnd, *, seconds: float) -> ChatRun:
    """A run the model ended without its reply: every grader fails it."""
    # The exception carries no messages, so the run's calls and tokens are not counted.
    return ChatRun(
        ended=ended,
        reply="",
        tools_called=frozenset(),
        order_status_seen=None,
        usage=RunUsage(model_calls=0, tool_calls=0, tokens=0, seconds=seconds),
        within_budget=False,
    )


def _usage(messages: Iterable[AnyMessage], *, seconds: float) -> RunUsage:
    replies = [message for message in messages if isinstance(message, AIMessage)]
    return RunUsage(
        model_calls=len(replies),
        tool_calls=sum(len(reply.tool_calls) for reply in replies),
        tokens=sum(
            reply.usage_metadata["total_tokens"]
            for reply in replies
            if reply.usage_metadata
        ),
        seconds=seconds,
    )


def _within(usage: RunUsage, budget: Budget) -> bool:
    return (
        usage.model_calls <= budget.model_calls
        and usage.tool_calls <= budget.tool_calls
        and usage.seconds <= budget.seconds
    )


def _tools_called(messages: Iterable[AnyMessage]) -> frozenset[str]:
    return frozenset(
        call["name"]
        for message in messages
        if isinstance(message, AIMessage)
        for call in message.tool_calls
    )


def _first_status_seen(
    asked: Iterable[str], statuses: Mapping[str, OrderStatus]
) -> OrderStatus | None:
    """The status of the first order the agent asked for that exists, or None."""
    found = [statuses[order_id] for order_id in asked if order_id in statuses]
    return found[0] if found else None


def required_tools_called(
    *, output: ChatRun, expected_output: ChatCase, **kwargs: object
) -> Evaluation:
    if output.ended is not RunEnd.REPLY:
        return _failed_run(Criterion.REQUIRED_TOOLS_CALLED, output.ended)

    called_all = expected_output.required_tools <= output.tools_called
    return Evaluation(name=Criterion.REQUIRED_TOOLS_CALLED, value=called_all)


def only_allowed_tools_called(
    *, output: ChatRun, expected_output: ChatCase, **kwargs: object
) -> Evaluation:
    if output.ended is not RunEnd.REPLY:
        return _failed_run(Criterion.ONLY_ALLOWED_TOOLS_CALLED, output.ended)

    called_only_allowed = output.tools_called <= expected_output.allowed_tools
    return Evaluation(
        name=Criterion.ONLY_ALLOWED_TOOLS_CALLED, value=called_only_allowed
    )


def reply_states_the_status(
    *, output: ChatRun, expected_output: ChatCase, **kwargs: object
) -> Evaluation:
    if output.ended is not RunEnd.REPLY:
        return _failed_run(Criterion.REPLY_STATES_THE_STATUS, output.ended)

    expected = expected_output.status_in_reply
    states_it = expected is None or expected in output.reply.lower()
    return Evaluation(name=Criterion.REPLY_STATES_THE_STATUS, value=states_it)


async def reply_keeps_to_the_status(
    *, output: ChatRun, judge_client: AcmeAiClient, **kwargs: object
) -> Evaluation:
    if output.ended is not RunEnd.REPLY:
        return _failed_run(Criterion.REPLY_KEEPS_TO_THE_STATUS, output.ended)

    # The judge's client is sync: in a thread, its wait does not stop the other runs.
    judged = await asyncio.to_thread(
        judge_unsupported_promise,
        output.reply,
        output.order_status_seen,
        judge_client,
        model=UNSUPPORTED_PROMISE_JUDGE_LLM_MODEL,
        reasoning_effort=UNSUPPORTED_PROMISE_JUDGE_LLM_REASONING_EFFORT,
    )
    return Evaluation(
        name=Criterion.REPLY_KEEPS_TO_THE_STATUS,
        value=judged.verdict is Verdict.PASS,
        comment=judged.evidence,
    )


def _failed_run(criterion: Criterion, ended: RunEnd) -> Evaluation:
    """A run that ended without its reply fails every criterion; the comment says how."""
    return Evaluation(name=criterion, value=False, comment=f"run ended: {ended}")


def task_succeeded(*, evaluations: list[Evaluation], **kwargs: object) -> Evaluation:
    """The headline of the run: every criterion graded, and every one passed."""
    graded_all = len(evaluations) == len(Criterion) - 1
    succeeded = graded_all and all(
        evaluation.value is True for evaluation in evaluations
    )
    return Evaluation(name=Criterion.TASK_SUCCEEDED, value=succeeded)


def within_budget(
    *, item_results: list[ExperimentItemResult], **kwargs: object
) -> Evaluation:
    """Of the runs that succeeded, the share that stayed inside its case's budget."""
    succeeded = _successful_runs(item_results)
    within = sum(run.within_budget for run in succeeded)
    share = within / len(succeeded) if succeeded else 0.0

    return Evaluation(
        name=RunMeasure.WITHIN_BUDGET,
        value=share,
        comment=f"{within} of {len(succeeded)}",
    )


def tokens_per_success(
    *, item_results: list[ExperimentItemResult], **kwargs: object
) -> Evaluation:
    """Tokens of the runs that replied, divided by the runs that succeeded.

    A run the model ended early carries no token count, so the figure is a floor.
    """
    runs = [run.output for run in item_results if isinstance(run.output, ChatRun)]
    tokens = sum(run.usage.tokens for run in runs)
    successes = len(_successful_runs(item_results))

    if not successes:
        return Evaluation(
            name=RunMeasure.TOKENS_PER_SUCCESS,
            value=float(tokens),
            comment=f"no run succeeded: all {tokens} tokens bought nothing",
        )

    return Evaluation(
        name=RunMeasure.TOKENS_PER_SUCCESS,
        value=tokens / successes,
        comment=f"{successes} successful runs; {TOKENS_PER_SUCCESS_BEFORE} on main",
    )


def _successful_runs(item_results: Iterable[ExperimentItemResult]) -> list[ChatRun]:
    return [
        run.output
        for run in item_results
        if isinstance(run.output, ChatRun)
        and any(
            evaluation.name == Criterion.TASK_SUCCEEDED and evaluation.value is True
            for evaluation in run.evaluations
        )
    ]


def _item(case: ChatCase) -> LocalExperimentItem:
    return LocalExperimentItem(
        input=case.question, expected_output=case, metadata={"case_id": case.case_id}
    )


def main() -> None:
    settings = Settings()
    # A command, like the CLI of python/logging/setup-example.md: its log goes to stderr.
    logging.config.dictConfig(
        build_logging_config(settings.log_level, settings.log_format, stream="stderr")
    )
    start_tracing(
        settings.langfuse_public_key,
        settings.langfuse_secret_key,
        settings.langfuse_base_url,
    )
    langfuse = get_client()

    run_chat_eval(RunnerContext(client=langfuse), settings)

    langfuse.flush()


if __name__ == "__main__":
    main()
```

`check_rates` is the gate of [case-set-example.md](case-set-example.md), in `evals/rate_gate.py`.

Why it looks like this:

- **Task success first** ([agents.md](agents.md) section 2): `task_succeeded` is a composite
  evaluator, which Langfuse runs after the item evaluators with their results. A run succeeds when
  every criterion was graded and passed, and its rate leads the baseline. The other rates show where
  a failed run went wrong. `BASELINE` holds the rates of main's last run, not of the old version run
  again in this job, which departs from [evals.md](evals.md) section 7; why is under
  [What this example does not claim](#what-this-example-does-not-claim).
- **Budget and cost, read under the headline** ([agents.md](agents.md) section 2): each case carries
  a budget, the counts of its shortest successful run and the 90th percentile of its successful
  runs' seconds, and `_run_agent` counts the model calls, tool calls, tokens and seconds from the
  run's messages and the clock it is given; the duration is part of what it returns, so the clock
  is a parameter ([readability.md](../../any-language/readability/readability.md) section 6). Two run evaluators,
  which Langfuse runs once over all the results, report the share of successful runs inside their
  budget and the tokens per successful run against main's figure.
  They are reported, not gated, and they stay out of `Criterion`, so they never enter the headline
  or the count `check_rates` makes. Tokens stand in for money: multiply by the model's price for
  the cost per successful case. A run the model ended early raises before its messages come back,
  so it adds no tokens, and the cost per success is a floor; a usage callback on the run would
  count the calls that came back, but not a call the SDK stopped at the output limit or the
  content filter.
- **The task returns what the agent did**, not only its reply ([agents.md](agents.md) section 9): an
  item evaluator in Langfuse sees the task's output and never the trace, so the tool calls travel in
  `ChatRun`.
- **Traced, with what produced it** ([evals.md](evals.md) section 9): the Langfuse handler in the
  call's `callbacks` puts the model and tool calls into each run's trace, and the run's metadata
  names the agent's model, the judge's model and effort, and the commit. The agent's model has no
  effort to set, as the logging example's constant says.
- **Tool calls checked as sets** ([agents.md](agents.md) section 3): the required tools are among
  the calls, and nothing outside the allowed set ran; their arguments are not checked, a Must of
  [agents.md](agents.md) section 2 that this example leaves out
  ([What this example does not claim](#what-this-example-does-not-claim)). No order is asserted,
  because none is the guarantee here. The case with no order id makes "no tool" a case of its own
  ([agents.md](agents.md) section 2).
- **Code first, then the judge** ([evals.md](evals.md) section 5): whether the status word is in the
  reply is a string check; whether the reply promises more than the status supports is the
  validated judge of [judge-example.md](judge-example.md), given the status the agent actually saw
  as its reference, and gating here because this is an offline run on the team's own cases
  ([judges.md](judges.md) section 9). That section also asks for known-bad replies that must fail,
  and [evals.md](evals.md) section 5 for an agent that does nothing; this example leaves both out
  ([What this example does not claim](#what-this-example-does-not-claim)). Its quoted evidence goes
  into the score's comment, so a failure shows the words that failed it. Together the two check that
  the reply names the status the tool returned and promises nothing beyond it
  ([agents.md](agents.md) section 2). The string check does not catch a reply that names the status
  and denies it, such as "has not shipped yet"; a stricter eval gives `ChatReply` a status field and
  compares it by code.
- **The judge in a thread, the runs at a set concurrency**: Langfuse runs the experiment's runs in
  one event loop, 50 at once by default, and calls each evaluator inside that loop, so a sync judge
  call would block the loop, and the seconds of every other run would grow by its wait.
  `reply_keeps_to_the_status` is async and hands the sync judge to `asyncio.to_thread`; the lambda
  that binds the client returns its coroutine, which Langfuse awaits. `max_concurrency` caps how
  many runs are in flight at once, from `MAX_CONCURRENCY`: a run's seconds are wall-clock at that
  concurrency, so a time budget is compared only with runs at the same concurrency.
- **A clean environment per run** ([agents.md](agents.md) section 6): each of the three runs of a case
  builds a new store and a new agent around the one chat model, which keeps no state; the model is
  the real one, through the application's one client with the cache switch on.
- **Every run counted** ([evals.md](evals.md) section 6): a run the model ended without its reply,
  at the step limit, on a refusal, or on an answer cut off or one that does not parse, comes back
  as a `ChatRun` with its `RunEnd`. Every grader fails it with that ending as its comment, and the
  judge is not called for it. Only `ModelUnavailable`, the provider's failure, raises:
  `run_experiment` leaves that run out, and `check_rates` fails a run that has fewer grades than
  criteria, which also catches a judge call that raised, and names its case.

`build_agent`, `SUPPORT_CHAT_LLM_MODEL`, `chat_model`, `callback_handler`, `start_tracing` and the
`acme.core.errors` classes the agent's middlewares raise are those of
[python/logging/agent-example.md](../logging/agent-example.md), `build_logging_config` that of
[python/logging/setup-example.md](../logging/setup-example.md), `AcmeAiClient`, `AcmeAiSdk` and `Settings`
those of [prompt-example.md](../../any-language/prompt-engineering/prompt-example.md), and
`judge_unsupported_promise`, its model constants and `Verdict` those of
[judge-example.md](judge-example.md). Of the settings fields, `openai_api_key` is the logging
example's, `log_level` and `log_format` are those of
[python/logging/setup-example.md](../logging/setup-example.md), and `acme_ai_api_key`, `git_commit` and the
Langfuse keys and URL stand for the fields the examples leave out, as in
[case-set-example.md](case-set-example.md).

## What this example does not claim

The baseline rates and the margin are example values. Four cases and three runs show the shape,
not a set: a real one starts from 20 to 50 cases drawn
from the agent's real failures ([evals.md](evals.md) section 4), and pass^k for the critical flow runs
on the schedule ([repeated-runs.md](repeated-runs.md) section 6). The eval imports the fake store from
`tests/support/`, so the store the eval runs against is the one the unit tests trust; a team that
keeps `evals/` and `tests/` apart copies it instead.

A run that gates on a judge also judges a fixed set of known-bad replies, which must fail
([judges.md](judges.md) section 9), and every grader first fails an agent that does nothing
([evals.md](evals.md) section 5); this example leaves both out.

The eval checks which tools ran, not their arguments, which [agents.md](agents.md) section 2 lists
as a Must ("each required call's arguments, exact where they matter"): a case would carry the order
ids it expects, and a criterion would compare them with the ids the run asked for.

[evals.md](evals.md) section 7 asks to run the old version and the new one on the same cases and to
list every case that passed before and fails now; this example compares with stored rates
instead, `BASELINE` and `TOKENS_PER_SUCCESS_BEFORE`, which saves the second set of calls. Between
refreshes of those two, a change on the vendor's side moves the rates with no change in the code;
the scheduled run on main shows it ([evals.md](evals.md) section 8).
