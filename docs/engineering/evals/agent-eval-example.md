# Example: the unit tests and the eval of one LangGraph agent

A worked example for [agents.md](agents.md). The agent is the support agent of
[logging/agent-example.md](../logging/agent-example.md): LangChain's `create_agent` with one tool,
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

from acme.core.order_store_client import Order, OrderStore


class FakeOrderStore(OrderStore):
    """An OrderStore that answers from a dict of statuses, and keeps the ids it was asked for."""

    def __init__(self, statuses: Mapping[str, str]) -> None:
        # No super().__init__(): the fake reaches no store.
        self._statuses = statuses
        self.asked: list[str] = []

    @override
    def get(self, order_id: str) -> Order | None:
        self.asked.append(order_id)
        status = self._statuses.get(order_id)
        return None if status is None else Order(order_id=order_id, status=status)
```

The real store's client and its `Order` record are not shown in the logging example; the fake
overrides the one method the tool calls ([testing/fakes-and-boundaries.md](../testing/fakes-and-boundaries.md)
section 1). An unknown id returns `None`, as the real store does, so the agent's "no such order" path
runs against the fake too ([agents.md](agents.md) section 6). The unit tests and the eval use the
same fake, so both agree on how the store behaves; each builds a new one per run.

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

from acme.support.chat.consts import SUPPORT_CHAT_LLM_MODEL
from acme.support.chat.graph import ChatAgent, build_agent
from acme.support.chat.schemas import ChatReply
from tests.support.fake_order_store import FakeOrderStore

ASK_FOR_A_1042: Final = {
    "role": "assistant",
    "content": None,
    "tool_calls": [
        {
            "id": "call_1",
            "type": "function",
            "function": {"name": "find_order", "arguments": json.dumps({"order_id": "A-1042"})},
        }
    ],
}
SHIPPED_REPLY: Final = {
    "role": "assistant",
    "content": json.dumps({"text": "Order A-1042 has shipped."}),
}


class ScriptedProvider:
    """Answers each chat completion with the next scripted message, and keeps every request body."""

    def __init__(self, messages: Iterator[dict[str, object]]) -> None:
        self._messages = messages
        self.requests: list[dict[str, object]] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(json.loads(request.content))
        message = next(self._messages)
        finish_reason = "tool_calls" if message.get("tool_calls") else "stop"
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 0,
                "model": SUPPORT_CHAT_LLM_MODEL,
                "choices": [{"index": 0, "message": message, "finish_reason": finish_reason}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            },
        )


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
    """The support agent finds an order, answers in its reply shape, and stops at its step limit."""

    async def test_an_order_question_is_answered_from_the_store(self) -> None:
        orders = FakeOrderStore({"A-1042": "shipped"})
        agent = agent_on(ScriptedProvider(iter([ASK_FOR_A_1042, SHIPPED_REPLY])), orders)

        result = await agent.ainvoke({"messages": [HumanMessage("Where is order A-1042?")]})

        assert (orders.asked, result["structured_response"]) == (
            ["A-1042"],
            ChatReply(text="Order A-1042 has shipped."),
        )

    async def test_the_model_is_offered_find_order_with_one_string_argument(self) -> None:
        provider = ScriptedProvider(iter([SHIPPED_REPLY]))

        await agent_on(provider, FakeOrderStore({})).ainvoke({"messages": [HumanMessage("Hello")]})

        tools = provider.requests[0]["tools"]
        offered = [(tool["function"]["name"], tool["function"]["parameters"]) for tool in tools]
        assert offered == [
            (
                "find_order",
                {
                    "type": "object",
                    "properties": {"order_id": {"type": "string"}},
                    "required": ["order_id"],
                    "additionalProperties": False,
                },
            )
        ]

    async def test_a_model_that_keeps_calling_tools_stops_at_the_step_limit(self) -> None:
        endless = ScriptedProvider(repeat(ASK_FOR_A_1042))
        agent = agent_on(endless, FakeOrderStore({"A-1042": "shipped"}))

        with pytest.raises(GraphRecursionError):
            await agent.ainvoke(
                {"messages": [HumanMessage("Where is order A-1042?")]},
                {"recursion_limit": 8},
            )
```

Why it looks like this:

- **The real chat model class with a scripted transport** ([agents.md](agents.md) section 5): the
  `ChatOpenAI` of the application sends its real request, tools and response format included, and
  `httpx.MockTransport` answers it from the script. The calls are async, `await agent.ainvoke(...)`
  through `http_async_client`: `build_agent`'s middlewares define only async hooks, so a sync
  `invoke` raises `NotImplementedError`. LangChain's `GenericFakeChatModel` would fail
  here: it has no `bind_tools`. This is the first stand-in of
  [testing/fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 1, and the logging
  example's text already names it for this agent.
- **What the test can say, and what it cannot.** The script decides what the "model" answers, so the
  tests check the agent's code: that a tool call reaches the store with the model's argument, that
  the reply is parsed into `ChatReply`, that the definition the model is offered has not changed,
  and that a model that never stops is stopped. Whether the real model calls `find_order` for this
  question is the eval's job.
- **The tool definition is locked** ([agents.md](agents.md) section 5): the test reads the request
  body the provider received. A change to the tool's name or argument turns it red, and a change to
  a tool definition runs the eval
  ([prompt-engineering.md](../prompt-engineering/prompt-engineering.md) section 14).
- **The step limit is asserted by its error**, not by a count of calls, which is LangGraph's own
  detail.
- **One class for the unit, names that state the guarantee, a fresh agent and a fresh store in each
  test** ([testing/test-structure.md](../testing/test-structure.md) sections 1 to 4): the agent is
  built inside the test, so nothing carries from one test to the next. The scripted provider is used
  by this file alone, so it stays here
  ([testing/fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 1).

`build_agent`, `ChatReply` and `SUPPORT_CHAT_LLM_MODEL` are those of the logging example; its
`build_agent` asks for `ChatOpenAI`, which is what the test passes.

## `evals/chat/cases_chat.jsonl`: the cases

```json
{"case_id": "shipped-order", "question": "Where is my order A-1042?", "order_statuses": {"A-1042": "shipped"}, "required_tools": ["find_order"], "allowed_tools": ["find_order"], "status_in_reply": "shipped"}
{"case_id": "unknown-order", "question": "What happened to order B-9?", "order_statuses": {}, "required_tools": ["find_order"], "allowed_tools": ["find_order"], "status_in_reply": null}
{"case_id": "no-order-id", "question": "Can I change my delivery address?", "order_statuses": {}, "required_tools": [], "allowed_tools": [], "status_in_reply": null}
```

Each case names the tools the agent must call and the tools it may call, and the store it runs
against ([agents.md](agents.md) section 2). The last case has no order id: the right action is to ask
for one, so no tool may run.

```python
# evals/chat/schemas.py, next to Verdict, Split, PromiseVerdict and LabelledReply
@unique
class ToolName(StrEnum):
    FIND_ORDER = "find_order"


@unique
class Criterion(StrEnum):
    """What the agent's eval grades; each has one grader and one rate."""

    REQUIRED_TOOLS_CALLED = "required_tools_called"
    ONLY_ALLOWED_TOOLS_CALLED = "only_allowed_tools_called"
    REPLY_STATES_THE_STATUS = "reply_states_the_status"
    REPLY_KEEPS_TO_THE_STATUS = "reply_keeps_to_the_status"


class ChatCase(BaseModel):
    """One line of cases_chat.jsonl: a question, the store it runs against, and what the agent must do."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    case_id: str
    question: str
    order_statuses: dict[str, str]
    required_tools: frozenset[ToolName]
    allowed_tools: frozenset[ToolName]
    status_in_reply: str | None  # the status word the reply must state, when the order exists


class ChatRun(BaseModel):
    """What one run of the agent did: its reply and the tools it called."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    reply: str
    # The names the model asked for, which can include a tool that does not exist: not ToolName.
    tools_called: frozenset[str]
    order_status_seen: str | None
```

## `evals/chat/experiment_chat.py`: the agent's eval

```python
# evals/chat/experiment_chat.py
"""The support agent's eval: each case three times against the real model, graded on what the agent did."""

import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import Final

from acme_ai import AcmeAiSdk
from langchain_core.messages import AIMessage, HumanMessage
from langfuse import Evaluation, RunnerContext, get_client
from langfuse.experiment import ExperimentResult, LocalExperimentItem

from acme.core.acme_ai_client import AcmeAiClient
from acme.core.config import Settings
from acme.core.langfuse_client import start_tracing
from acme.core.openai_client import chat_model
from acme.support.chat.consts import SUPPORT_CHAT_LLM_MODEL
from acme.support.chat.graph import build_agent
from evals.chat.consts import (
    UNSUPPORTED_PROMISE_JUDGE_LLM_MODEL,
    UNSUPPORTED_PROMISE_JUDGE_LLM_REASONING_EFFORT,
)
from evals.chat.judge_unsupported_promise import judge_unsupported_promise
from evals.chat.schemas import ChatCase, ChatRun, Criterion, Verdict
from tests.support.fake_order_store import FakeOrderStore

CASES_FILE: Final = Path(__file__).with_name("cases_chat.jsonl")
RUNS_PER_CASE: Final = 3


def experiment(context: RunnerContext) -> ExperimentResult:
    settings = Settings()
    cases = [ChatCase.model_validate_json(line) for line in CASES_FILE.read_text().splitlines()]
    judge_client = AcmeAiClient(
        AcmeAiSdk(api_key=settings.acme_ai_api_key.get_secret_value()),
        disable_prompt_cache=True,
        new_request_uuid=uuid.uuid4,
    )

    result = context.run_experiment(
        name="support-chat",
        data=[_item(case) for case in cases for _ in range(RUNS_PER_CASE)],
        task=lambda *, item, **kwargs: _run_agent(item["expected_output"], settings),
        evaluators=[
            required_tools_called,
            only_allowed_tools_called,
            reply_states_the_status,
            lambda **kwargs: reply_keeps_to_the_status(judge_client=judge_client, **kwargs),
        ],
    )

    _gate(result, runs_expected=len(cases) * RUNS_PER_CASE)
    return result


async def _run_agent(case: ChatCase, settings: Settings) -> ChatRun:
    # A new store and a new agent for every run: nothing carries over (agents.md section 6).
    orders = FakeOrderStore(case.order_statuses)
    agent = build_agent(
        chat_model(SUPPORT_CHAT_LLM_MODEL, settings.openai_api_key),
        orders,
        model=SUPPORT_CHAT_LLM_MODEL,
        disable_prompt_cache=True,
        new_request_uuid=uuid.uuid4,
    )

    result = await agent.ainvoke({"messages": [HumanMessage(case.question)]})

    tools_called = frozenset(
        call["name"]
        for message in result["messages"]
        if isinstance(message, AIMessage)
        for call in message.tool_calls
    )
    return ChatRun(
        reply=result["structured_response"].text,
        tools_called=tools_called,
        order_status_seen=_first_status_seen(orders.asked, case.order_statuses),
    )


def _first_status_seen(asked: list[str], statuses: Mapping[str, str]) -> str | None:
    """The status of the first order the agent asked for that exists, or None."""
    found = [statuses[order_id] for order_id in asked if order_id in statuses]
    return found[0] if found else None


def required_tools_called(*, output: ChatRun, expected_output: ChatCase, **kwargs: object) -> Evaluation:
    called_all = expected_output.required_tools <= output.tools_called
    return Evaluation(name=Criterion.REQUIRED_TOOLS_CALLED, value=called_all)


def only_allowed_tools_called(*, output: ChatRun, expected_output: ChatCase, **kwargs: object) -> Evaluation:
    called_only_allowed = output.tools_called <= expected_output.allowed_tools
    return Evaluation(name=Criterion.ONLY_ALLOWED_TOOLS_CALLED, value=called_only_allowed)


def reply_states_the_status(*, output: ChatRun, expected_output: ChatCase, **kwargs: object) -> Evaluation:
    expected = expected_output.status_in_reply
    states_it = expected is None or expected in output.reply.lower()
    return Evaluation(name=Criterion.REPLY_STATES_THE_STATUS, value=states_it)


def reply_keeps_to_the_status(
    *, output: ChatRun, judge_client: AcmeAiClient, **kwargs: object
) -> Evaluation:
    judged = judge_unsupported_promise(
        output.reply,
        output.order_status_seen or "no order found",
        judge_client,
        model=UNSUPPORTED_PROMISE_JUDGE_LLM_MODEL,
        reasoning_effort=UNSUPPORTED_PROMISE_JUDGE_LLM_REASONING_EFFORT,
    )
    return Evaluation(
        name=Criterion.REPLY_KEEPS_TO_THE_STATUS,
        value=judged.verdict is Verdict.PASS,
        comment=judged.evidence,
    )


def _item(case: ChatCase) -> LocalExperimentItem:
    return LocalExperimentItem(input=case.question, expected_output=case, metadata={"case_id": case.case_id})


if __name__ == "__main__":
    settings = Settings()
    start_tracing(settings.langfuse_public_key, settings.langfuse_secret_key, settings.langfuse_base_url)
    experiment(RunnerContext(client=get_client()))
    get_client().flush()
```

`_gate`, `BASELINE`, `MARGIN` and the rest of the gate are those of
[case-set-example.md](case-set-example.md), with this eval's four criteria; a second eval that needs
the same gate moves it into a file of its own under `evals/`, named for what it holds.

Why it looks like this:

- **The task returns what the agent did**, not only its reply ([agents.md](agents.md) section 9): an
  item evaluator in Langfuse sees the task's output and never the trace, so the tool calls travel in
  `ChatRun`.
- **Tool calls checked as sets** ([agents.md](agents.md) section 3): the required tools are among
  the calls, and nothing outside the allowed set ran. No order is asserted, because none is the
  guarantee here. The case with no order id makes "no tool" a case of its own
  ([agents.md](agents.md) section 2).
- **Code first, then the judge** ([evals.md](evals.md) section 5): whether the status word is in the
  reply is a string check; whether the reply promises more than the status supports is the
  validated judge of [judge-example.md](judge-example.md), given the status the agent actually saw as
  its reference, and gating here because this is an offline run on the team's own cases
  ([judges.md](judges.md) section 9). Its quoted evidence goes into the score's comment, so a failure
  shows the words that failed it.
- **A clean environment per run** ([agents.md](agents.md) section 6): each of the three runs of a case
  builds a new store and a new agent; the agent's model is the real one, through the application's
  one client with the cache switch on.
- **Every run counted** ([evals.md](evals.md) section 6): the gate of the triage example fails a run
  that has fewer grades than criteria, which also catches a judge call that raised.

`chat_model` and `openai_api_key` are those of the logging example's `core/openai_client.py` and
settings.

## What this example does not claim

Three cases and three runs show the shape, not a set: a real one starts from 20 to 50 cases drawn
from the agent's real failures ([evals.md](evals.md) section 4), and pass^k for the critical flow runs
on the schedule ([repeated-runs.md](repeated-runs.md) section 6). The eval imports the fake store from
`tests/support/`, so the store the eval runs against is the one the unit tests trust; a team that
keeps `evals/` and `tests/` apart copies it instead.
