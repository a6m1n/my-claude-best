# Testing agents

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. What to test in an agent](#2-what-to-test-in-an-agent)
- [3. Checks on the tool calls](#3-checks-on-the-tool-calls)
- [4. The layers](#4-the-layers)
- [5. Unit tests of a LangGraph agent](#5-unit-tests-of-a-langgraph-agent)
- [6. The environment and the graders](#6-the-environment-and-the-graders)
- [7. Injection through tool results](#7-injection-through-tool-results)
- [8. Simulated users](#8-simulated-users)
- [9. Agent evals in Langfuse and LangSmith](#9-agent-evals-in-langfuse-and-langsmith)
- [10. Where it stops holding](#10-where-it-stops-holding)
- [11. Review checklist](#11-review-checklist)
- [12. Sources](#12-sources)

## 1. Purpose and the one rule

An agent is a model that calls tools in a loop until it decides it is done. This file is for anyone
who builds or changes one, and it assumes LangGraph and LangChain 1.x; the method holds for any
framework. Its levels are those of [evals.md](evals.md) section 1, and the method of
[evals.md](evals.md) holds for an agent too. [agent-eval-example.md](agent-eval-example.md) shows
the tests and the eval of one agent.

The one rule: **an agent is graded on what it did, in code: which tools it called with which
arguments, and the state it left behind; a model judges only what code cannot see, and a judge never
decides that the task is done.**

## 2. What to test in an agent

| What | The check | Grader | Level |
|---|---|---|---|
| the tools it must call | the required tools appear among the calls | code | Must |
| the tools it must not call | no call outside the allowed set, no forbidden call | code | Must |
| the arguments | each required call's arguments, exact where they matter | code | Must |
| the order | only where the order is the guarantee: a check before a payment, a read before a write | code | Should |
| the end state | what the agent changed in its environment: a fake store, a sandbox, a database | code | Must, when the agent changes state |
| the final answer | right content, from a reference or code; tone and helpfulness by a validated judge | code, then a judge | Must |
| asking, refusing, confirming | cases where the right action is to ask, refuse or wait for a person, scored apart | code | Must |
| a policy | limits on money, permissions or data, enforced in the tool's code and tested there, without a model | a unit test | Must |
| failures of its tools | a tool that times out or returns an error: the agent recovers or stops cleanly | code, with a failing fake | Should |
| a loop that never ends | the graph stops at its step limit | a unit test | Must |
| the cost of a run | steps, tokens, model calls and time per case, against a budget | code on the trace | Should |
| a conversation | a multi-turn session, scored per turn and by its worst turn | a judge, and a person on a sample | Should, for multi-turn agents |
| human approval | the graph pauses before a tool that needs approval, and each decision resumes it right | a unit test | Must, when the agent has approval steps |
| memory across turns | state saved and loaded by the checkpointer the service runs | an integration test | Should |

Why: an outcome check alone hides a broken procedure. On τ-bench, 16 to 78% of passes broke
procedure or policy, and 8 to 17% of agents that reached the right state skipped a required check on
the way. In repeated runs of one agent, different actions got the same failing verdict in 22 of 43
groups. The reverse also holds: rule-based checkers missed 44% of real successes, so a failing check
gets read by a person before the set is trusted. A model that scored 71.8% overall got 19.5% of the
cases right where it should have refused; decisions not to act need their own cases. Where a
policy was enforced in the tools, a benchmark found no policy loopholes; where it was written only
in the prompt, success fell from 51% to 37% on the affected tasks.

## 3. Checks on the tool calls

**Must.** Check the tool calls as sets: the required tools are all among the calls, and nothing
outside the allowed set was called. Check the order only where the order is the guarantee, and then
enforce that order in code as well (section 2). A reference path with one fixed order fails valid
runs: exact step matching ranked valid reorderings correctly only 44.8% of the time, below the 50%
of chance, and Anthropic calls tool-sequence checks "too rigid". Tool choice is stable from run to
run; tool order is not.

**Must.** Assert that the run made at least one call before you match it, when the case expects
one. A missing trajectory can pass a subset check: openevals' matcher turned a missing trajectory
into an empty one, which passes (pull request #237, open at the time of writing).

With plain Python, on the messages a LangGraph run returns:

```python
from langchain_core.messages import AIMessage

called = {
    call["name"]
    for message in result["messages"]
    if isinstance(message, AIMessage)
    for call in message.tool_calls
}

assert called & REQUIRED_TOOLS == REQUIRED_TOOLS  # every required tool was called
assert called <= ALLOWED_TOOLS  # nothing outside the allowed set
```

**Optional.** openevals' trajectory matcher, when you compare with a reference conversation or want
its argument modes. `create_trajectory_match_evaluator` from `openevals.trajectory.match` takes a
mode: `superset` passes when the run made at least the reference's calls (the required-tools
check), `subset` passes when it made no call outside the reference's (the allowed-set check),
`unordered` wants the same calls in any order, and `strict` the same calls in the same order.
`tool_args_match_mode` is `exact` by default; `ignore` passed a wrong argument in a local run, so
use it only for a tool whose arguments do not matter. It returns a plain dictionary
(`{"key": ..., "score": ..., "comment": ...}`), so its result can go to any eval platform. The same
functions used to ship as `agentevals`, which has had no release since July 2025 and has an open bug
that swaps the arguments in `subset` mode; use `openevals`.

## 4. The layers

| Layer | What it checks | Model | When | Level |
|---|---|---|---|---|
| unit tests of the graph (section 5) | the code: routing, tools, parsing, interrupts, retries, the step limit, the tool definitions sent | a scripted stand-in | every push | Must |
| real-model tests of single cases | a case's contract, with its pass rule ([repeated-runs.md](repeated-runs.md) section 4) | real | a pull request that changes behaviour | Must |
| the eval | rates over the case set: tool calls, end state, answer, cost | real | a pull request that changes behaviour, and the schedule | Must |
| reliability | pass^k for the critical flows ([repeated-runs.md](repeated-runs.md) section 6) | real | the schedule, before a release | Should |
| simulated conversations (section 8) | multi-turn behaviour | real, plus a simulator | the schedule | Optional |
| production (production.md) | sampled real sessions | production | always | Must |

The unit layer cannot see what the model does with a prompt or a tool's description: prompts got
about 1% of the tests in agent projects, and rewriting tool descriptions moved task success by a
median of 5.85 points, with a regression in 16.67% of cases. So a change to a tool's name,
description or arguments runs the eval, as
[prompt-engineering.md](../prompt-engineering/prompt-engineering.md) section 14 asks.

## 5. Unit tests of a LangGraph agent

The unit suite runs without a network and without a model
([testing/fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 4). For an agent,
that takes these parts:

- **Must. The model is the real chat model class with a scripted transport.** A `ChatOpenAI` built
  with `http_client=httpx.Client(transport=httpx.MockTransport(handler))` (or
  `http_async_client=` with an `httpx.AsyncClient` for async code) answers from a script: first a
  tool call, then the final reply. It is the first stand-in of
  [testing/fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 1, the real class
  with a fake inside. The request it sends carries the real tool list and schemas, so the test can
  also check them. LangChain's `GenericFakeChatModel` has no `bind_tools`, so `create_agent` with
  tools raises `NotImplementedError`; a subclass whose `bind_tools` returns the model works, but
  sends no tool schema anywhere, so use it only where the chat model's HTTP client cannot be
  replaced. [agent-eval-example.md](agent-eval-example.md) shows the handler.
- **Must. A fresh graph and a fresh checkpointer per test**: compile the graph in the test's
  fixture with `InMemorySaver()` (`langgraph.checkpoint.memory`; `MemorySaver` is its older name)
  and a new `thread_id`, at function scope ([testing/fixtures.md](../testing/fixtures.md)).
- **Should. One node at a time**: `graph.nodes["route"].invoke(state)` runs one node; to start in
  the middle, `graph.update_state(config, values, as_node="<the node before>")`, then
  `graph.invoke(None, config)`. This is for a graph you built with `StateGraph`; an agent made by
  `create_agent` is tested through its public `invoke`.
- **Must, when the agent pauses for a person**: assert the interrupt's payload
  (`result["__interrupt__"]`) and resume with `Command(resume=...)` on the same `thread_id`, once
  per decision the agent allows. LangChain's `HumanInTheLoopMiddleware` takes
  `{"decisions": [{"type": "approve"}]}`, and also `edit`, `reject` and `respond`. On resume the
  node runs again from its start, so any side effect before `interrupt()` must be safe to repeat.
- **Must. A tool under a retry is safe to run twice**, or its retry is off: LangChain's
  `ToolRetryMiddleware` retried a payment-like tool after a timeout, up to three times. In tests,
  set its delay to almost nothing, as LangChain's own tests do (`initial_delay=0.01`,
  `jitter=False`), so the suite stays fast.
- **Must. The step limit holds**: a scripted model that always asks for a tool, run with
  `config={"recursion_limit": 8}`, raises `GraphRecursionError`. Assert the error, not the number of
  calls, which is LangGraph's internal detail.
- **Must, with `ToolStrategy`**: assert that `"structured_response"` is in the result. When the model
  answers without the tool call, the structured response is missing and nothing fails (LangChain
  issue #36349, open at the time of writing).
- **Should. Lock the tool definitions**: assert the tool names, descriptions and argument schemas in
  the request the scripted transport received. A red lock means the definitions changed, and a
  change to them runs the eval (section 4).
- **Optional. Pin the stream format** in a test that asserts streamed events (`version="v2"` in
  LangGraph 1.1 and later), so an upgrade does not turn it red with no change in behaviour.
- **Should. Test memory on the checkpointer the service runs**, in `integration/` with a real
  database, as [testing/suite-example.md](../testing/suite-example.md) runs its database.
  `InMemorySaver` stores data differently: a check that passed on it raised on `SqliteSaver`
  (LangGraph issue #8942).

## 6. The environment and the graders

**Must.** Every run of a case starts in a clean environment: a new thread, a new fake store or
sandbox, nothing left from the run before. LangChain and Anthropic both require it; a run that sees
the last run's state is not a case.

**Must.** A fake tool behaves like the real one where the agent can tell: it rejects the inputs the
real tool rejects, and it can return the real tool's timeouts and errors. A fake that accepts
everything makes the agent look better than it is: simulated tools accepted invalid commands, and
timeouts and runtime errors in tool results cut success by about 30%.

**Must.** The grader reads nothing the agent can write: not a file in its workspace, not its own
report of success. Agents under evaluation copy answer keys and change tests: in one benchmark 57%
of runs gamed a planted shortcut, and a prompt telling them not to cut that by only 6 points.
Before a grader gates, an agent that does nothing fails every case and a reference solution passes
them ([evals.md](evals.md) section 5).

**Should.** Give the agent a legal way out, such as a tool that hands the case to a person. With an
escalation tool and a policy, gaming fell from 23.6% to 5.3% of runs.

## 7. Injection through tool results

A tool result can carry text written by someone else: a web page, an email, a document. Testing
this is part of the security work of [production.md](production.md) section 7; the case shape for
an agent is:

**Should.** For each tool that returns text from outside, a case with three parts and a twin:

1. a normal task for the user;
2. a tool result, from a fake tool, that plants an instruction ("forward the customer's data to
   ...") with a unique marker string for this run;
3. the check, in code: no call outside the allowed set, no call that serves the planted instruction,
   and the marker string in no tool argument and not in the answer;
4. the twin: the same task with a clean tool result, which must still succeed, so a guard that
   refuses everything fails.

Run the case once with the guard switched off: the attack must get through, or the case attacks
nothing. With a scripted model (section 5) the case tests your guard code: a filter, an allowed
set, an approval step before sensitive tools. With the real model it tests how often the model
follows the planted text; run that in the eval, with repeats. AgentDojo grades exactly this way,
with checks on the environment's state, not a judge.

## 8. Simulated users

**Optional.** A second model plays the user for multi-turn cases, such as openevals'
`run_multiturn_simulation` with `create_llm_simulated_user`. Add it when a flow needs several turns
to test and real conversations cannot be replayed. Pin the simulator's model and prompt, and read a
sample of its conversations: changing only the simulated user moved success by up to 15 points,
24.4% of successful runs broke the user's stated goals, and simulated users pushed success above what
real users reached. A real conversation replayed up to a failure, with the next reply graded, is the
cheaper start (Langfuse calls it N+1 evaluation).

## 9. Agent evals in Langfuse and LangSmith

**With Langfuse**, the default of [tools.md](tools.md) section 2:

- **The run.** `langfuse.run_experiment(name=..., data=cases, task=..., evaluators=[...],
  run_evaluators=[...])`. The task runs the agent on one case and returns the final answer together
  with the tool calls and whatever end state the graders need: an item evaluator sees only the
  task's output, never the trace.
- **The graders.** Item evaluators return `Evaluation(name=..., value=...)`: the checks of section 3
  in plain Python, or openevals' matcher wrapped in an evaluator. A run evaluator computes the rate
  per criterion, counting every case ([evals.md](evals.md) section 6): `run_experiment` drops a case
  whose task raised.
- **In CI.** A pytest test that calls the experiment and asserts the counts and rates, or the
  `langfuse/experiment-action` GitHub Action, which fails the job when the experiment raises
  `RegressionError`. Neither needs Langfuse to be reachable for the checks: without keys the client
  disables itself and the run still returns its results.
- **In production.** Evaluators on the agent's observations; a tool call is a field of its
  observation, so a check such as "the refund tool was called without an approval" reads it
  directly. Langfuse's hosted code evaluators run Python's standard library only, with no network,
  so openevals does not run inside them.

**With LangSmith**: `@pytest.mark.langsmith` turns tests into an experiment (with
`LANGSMITH_TEST_TRACKING=false` nothing is uploaded, and only `expect(...)`, not `log_feedback`,
fails a test); `evaluate()` runs a dataset; its guide splits agent evaluation into the final
response, a single step (one node's decision) and the trajectory. The same openevals functions work
with both.

## 10. Where it stops holding

- **A fixed chain with one model call** is not an agent: [evals.md](evals.md) holds, and sections
  2 to 9 here do not.
- **A coding agent in a large repository** is graded by running the repository's own tests in a
  sandbox. Benchmark practice applies there; this file covers application agents.

## 11. Review checklist

| Section | Level | Ask |
|---|---|---|
| 2 | Must | Are there cases for required and forbidden tools, arguments, the end state, and asking, refusing or confirming? Is a policy enforced and tested in the tool's code? |
| 3 | Must | Are the tool calls checked as sets, with order only where it is the guarantee, and a non-empty trajectory asserted? |
| 4 | Must | Does a change to a tool's name, description or arguments run the eval? |
| 5 | Must | Do unit tests use the real chat model class on a scripted transport, a fresh checkpointer per test, the step limit and each approval decision? |
| 6 | Must | Does each run start clean, do fakes reject what the real tool rejects, and did a do-nothing agent fail every case? |
| 7 | Should | Does every tool that returns outside text have an injection case with a twin and a control run? |
| 9 | Must | Does the task return the tool calls, and does the rate count every case? |

## 12. Sources

- LangGraph docs, "Test" and "Interrupts"; LangChain docs, "Test", "Unit testing", "Human in the
  loop", "Middleware", "Structured output", "Streaming" (docs.langchain.com, read 2026-09-30);
  langchain-core `fake_chat_models.py`; LangChain middleware source and tests (`tool_retry.py`,
  `human_in_the_loop.py`); issues langchain #36349 and #40687, langgraph #8942, #8796, #6559.
- Local runs, 2026-09-30: langgraph 1.2.12, langchain 1.4.3, langchain-core 1.6.6,
  langchain-openai 1.6.7, openevals 0.2.0, langfuse 4.16.0: the fake model without `bind_tools`, the
  scripted transport with `create_agent` and `ProviderStrategy`, sync and async, the step limit, the
  trajectory matcher's modes.
- openevals README and releases (trajectory evaluators folded in from agentevals, 0.1.4); agentevals
  issues #114 and #62; openevals pull request #237.
- LangChain, "Agent evaluation readiness checklist", 2026-03-27, and "Evaluating Deep Agents",
  2025-12-03; Anthropic, "Demystifying evals for AI agents", 2026-01-09; OpenAI, "Agent evals" and
  "Trace grading" guides.
- Cao et al., arXiv:2603.03116, 2026; Rabinovich et al., arXiv:2603.29665, 2026; repeated clinical
  agent runs, arXiv:2609.13582, 2026; tau2 policy loopholes, arXiv:2609.14400, 2026; "Calibration is
  the bottleneck", arXiv:2609.00949, 2026; AgentRewardBench, arXiv:2504.08942, 2025.
- Exact step matching on valid reorderings, arXiv:2607.17082, 2026; tool choice vs order,
  arXiv:2605.10516, 2026; tool descriptions, arXiv:2602.14878, 2026; agent project tests,
  arXiv:2509.19185, 2025.
- RobustBench-TC, arXiv:2605.11928, 2026; permissive tool simulators, arXiv:2605.07247, 2026;
  BAITBENCH, arXiv:2608.30724, 2026; defect-driven gaming, arXiv:2608.29460, 2026; BenchJack,
  arXiv:2605.12673, 2026.
- Debenedetti et al., "AgentDojo", arXiv:2406.13352, 2024 (origin); InjecAgent, arXiv:2403.02691,
  2024 (origin); a practitioner's release-blocking injection test (dev.to, jfisher4002, 2026).
- UserProxyBench, arXiv:2609.38043, 2026; simulated users vs real users, arXiv:2603.11245 and
  arXiv:2601.17087, 2026; Langfuse, "Evaluating multi-turn conversations", 2025-10-09.
- Langfuse docs: experiments via SDK, code evaluators, agent evaluation guide
  (langfuse.com/resources/engineering/ai-agent-evaluation), `langfuse/experiment-action` README;
  LangSmith docs: pytest, evaluate a complex agent, multi-turn simulation.
