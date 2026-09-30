# Tools for evals

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. Langfuse or LangSmith](#2-langfuse-or-langsmith)
- [3. The libraries](#3-the-libraries)
- [4. DeepEval in pytest](#4-deepeval-in-pytest)
- [5. Not by default, and why](#5-not-by-default-and-why)
- [6. Settings that keep data in and failures visible](#6-settings-that-keep-data-in-and-failures-visible)
- [7. Sources](#7-sources)

## 1. Purpose and the one rule

This file says which tool does which job of the method in [evals.md](evals.md), when to add it, and
what to watch for. Read it before you add an eval library or platform. The pytest plugins of the
unit and integration suites are [testing/libraries.md](../testing/libraries.md)'s. Everything here
was read in September 2026; these tools change every month, so check the watch-for column against
the current release when you adopt one.

The one rule: **a tool is added for a job the method already needs, with its version pinned, its
telemetry off where data must not leave, and a check that it does not drop failures.**

Every eval library in this file can drop a failure quietly ([evals.md](evals.md) section 6): count
the cases yourself.

## 2. Langfuse or LangSmith

Both trace LangChain and LangGraph runs, keep datasets, run experiments, host LLM judges on live
traffic and give people queues to label traces.

**Should.** Use one platform that traces eval runs, stores case sets and runs experiments. The
default here is Langfuse, which [logging.md](../logging/logging.md) section 8 already uses as the
trace store; LangSmith where the conditions below say it fits better. Tracing every eval run is a
Must of [evals.md](evals.md) section 9.

| | Langfuse | LangSmith |
|---|---|---|
| licence and hosting | MIT; self-hosting is free and has every evaluation feature (judges, annotation queues, datasets, experiments); an enterprise key adds only access control, audit logs, retention policies and similar | proprietary; cloud, or self-hosting on the Enterprise plan only |
| LangChain and LangGraph tracing | `langfuse.langchain.CallbackHandler`, passed in the run's config; built on OpenTelemetry, so other frameworks trace the same way | automatic once `LANGSMITH_TRACING=true` and the key are set; `@traceable` for your own code |
| evals from code | `run_experiment(...)` with item and run evaluators; runs with no keys on local data | `evaluate()` over a dataset; `@pytest.mark.langsmith` turns tests into an experiment |
| CI | a pytest test you write around `run_experiment`, or the `langfuse/experiment-action` GitHub Action, which fails on `RegressionError` | the pytest plugin, which needs an API key; `LANGSMITH_TEST_TRACKING=false` runs it without uploading |
| human review | annotation queues over traces, observations and sessions | annotation queues, including pairwise and whole-thread review |
| agent debugging | agent graphs drawn from the trace | LangSmith Studio: step through a graph, go back in time, rerun from a step |
| cost model | cloud billed per unit: every trace, observation and score | per seat plus traces; base traces kept 14 days, extended at most 180 days on the cloud |

**Langfuse fits better** when data must stay in your own infrastructure or region, when the team
does not want a per-seat bill, when not everything is LangChain, and when evals should run from
plain Python and pytest with no platform account in CI.

**LangSmith fits better** when the team lives in LangChain and wants tracing with no wiring, when
LangSmith Studio's step-through debugging of a graph matters, when reviewers need pairwise or
whole-conversation queues out of the box, and when the LangSmith pytest plugin's reports are wanted
more than self-hosting.

Watch for, on Langfuse: self-hosting runs PostgreSQL, ClickHouse, Redis and object storage, and
its maintainers put the need at about 4 CPUs and 16 GB of memory; three independent reports found
LangGraph's async and streaming runs attached user and session attributes only to the root span or
nested spans wrongly (the documented fix is `propagate_attributes(...)`); there is no pytest plugin;
the SDK moved to version 4 in March 2026 with breaking changes; ClickHouse bought Langfuse in
January 2026 and states no licence change is planned. On LangSmith: tracking of the pytest plugin
stops only when `LANGSMITH_TEST_TRACKING` is exactly `false`; `log_feedback` records a score and
never fails a test; on the cloud, trace retention was capped at 180 days from 14 September 2026.

## 3. The libraries

| Need | Library | What it does | Add it when | Watch for | Level |
|---|---|---|---|---|---|
| graders as plain functions | openevals | LLM-judge helpers, exact and JSON match, and trajectory matching for agents; each returns a dictionary any platform can store | a reference conversation to match, or judge helpers you do not want to write ([agents.md](agents.md) section 3) | assert a trajectory is not empty before matching (open bug); its ready-made judge prompts are generic: validate them ([judges.md](judges.md) section 6) | Optional |
| ready-made metrics in pytest | DeepEval | `assert_test` with judged metrics: G-Eval, decision graphs, RAG, agent and conversation metrics | a team wants ready metrics and accepts validating each one (section 4) | open bugs where a metric passes without judging everything; 4.2.0 turned four metrics' direction around; telemetry on by default | Optional |
| RAG metrics | Ragas | faithfulness, context precision and recall, test set generation | only with its maintenance risk accepted | no release since January 2026; 0.4.3 fails to import next to current LangChain packages; drops failed rows from averages ([rag.md](rag.md) section 7) | Optional |
| benchmark-style evals with repeats and sandboxes | Inspect AI (UK AI Security Institute) | tasks, solvers and scorers; `epochs` with reducers such as `at_least_2`; sandboxed agents | an eval needs many repeats per case, a sandbox, or "k of n" per case ([repeated-runs.md](repeated-runs.md) section 5) | its own runner, not pytest; exit status covers errors, not scores, so a gate reads the log; testing a LangGraph agent needs its model routed through Inspect | Optional |
| prompt comparisons and red teaming from YAML | promptfoo | test cases and assertions in YAML, `promptfoo eval`, a red-team module with OWASP presets | comparing prompts or models side by side, or scheduled red teaming ([production.md](production.md) section 7) | needs Node.js 22; the pip wrapper runs `npx promptfoo@latest` unless `PROMPTFOO_VERSION` pins it; OpenAI announced it was buying promptfoo in March 2026 | Optional |
| evals for a Pydantic AI app | Pydantic Evals | `Dataset`, `Case`, evaluators, `LLMJudge`, `evaluate_sync(task, repeat=n)` | the application is built on Pydantic AI | no gate of its own; `repeat` reports averages | Optional |
| "k of n" in pytest | flaky | `@flaky(max_runs=n, min_passes=k)` | you accept the limits in [repeated-runs.md](repeated-runs.md) section 5 | no release since 2024; false greens with pytest-rerunfailures; breaks async tests | Optional |

Platforms, one line each: **Arize Phoenix** (Elastic License 2.0, not an open-source licence;
Dynatrace announced it was buying Arize in August 2026); **Opik** by Comet (Apache 2.0); **Braintrust**
(hosted); **MLflow** (`mlflow.genai.evaluate`, and `@mlflow.test` for pytest); **TruLens** (MIT,
Snowflake). Each traces, stores datasets and runs judges; none changes the method.

## 4. DeepEval in pytest

DeepEval grades a test case with a judged metric: `measure` scores it, and `is_successful` says
whether the score reached the metric's threshold. Here the metric grades three runs of one case, and
the test counts the passes:

```python
# tests/integration/chat/test_graph.py
from typing import Final

import pytest
from deepeval.metrics import GEval
from deepeval.models import OpenAIModel
from deepeval.test_case import LLMTestCase, SingleTurnParams
from langchain_core.messages import HumanMessage

from acme.core.config import Settings
from acme.support.chat.graph import ChatAgent

QUESTION: Final = "Where is order A-1042?"
RUNS_PER_CASE: Final = 3


@pytest.fixture(scope="function")
def keeps_to_order_status() -> GEval:
    """The reply's judge; only live_model tests ask for it, so no default run reads a key."""
    settings = Settings()
    return GEval(
        name="Keeps to the order status",
        evaluation_steps=[
            "Read the order status in the context.",
            "Fail the reply if it promises anything the status does not support.",
        ],
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.CONTEXT],
        model=OpenAIModel(
            model=REPLY_JUDGE_LLM_MODEL,
            api_key=settings.openai_api_key.get_secret_value(),
        ),
        strict_mode=True,
    )


@pytest.mark.live_model
class TestBuildAgent:
    """The support agent's replies keep to what the order store says."""

    async def test_a_processing_order_gets_no_promise_of_a_date_in_two_runs_of_three(
        self, chat_agent: ChatAgent, keeps_to_order_status: GEval
    ) -> None:
        verdicts: list[bool | None] = []
        for _ in range(RUNS_PER_CASE):
            output = await chat_agent.ainvoke(
                {"messages": [HumanMessage(QUESTION)]}, version="v2"
            )
            test_case = LLMTestCase(
                input=QUESTION,
                actual_output=output.value["structured_response"].text,
                context=["order A-1042: processing"],
            )
            await keeps_to_order_status.a_measure(test_case)
            verdicts.append(keeps_to_order_status.is_successful())

        assert verdicts.count(True) >= 2
```

The names are those of DeepEval 4.2.7; the agent, its fixture and `REPLY_JUDGE_LLM_MODEL` are cut
here, [agent-eval-example.md](agent-eval-example.md) builds the agent, and `openai_api_key` is the
settings field of [logging/agent-example.md](../logging/agent-example.md). The test is async
because the agent is ([agent-eval-example.md](agent-eval-example.md) says why), so it awaits the
agent and DeepEval's `a_measure`. The judge's model here has no reasoning effort to set; one that
has one gets it from its `<purpose>_llm_reasoning_effort` constant through `OpenAIModel`'s
`generation_kwargs` ([prompt-engineering.md](../prompt-engineering/prompt-engineering.md)
section 15). What makes this snippet
follow the method:

- **Should. `evaluation_steps` instead of `criteria`** ([judges.md](judges.md) section 7): DeepEval's
  docs call a G-Eval score from criteria alone "not deterministic"; fixed steps repeat the same way
  each run.
- **Must. `strict_mode=True`** makes the verdict pass or fail ([judges.md](judges.md) section 4);
  without it the metric passes at a score of 0.5 by default, a threshold nobody chose
  ([judges.md](judges.md) section 7).
- **Must. `model=`** takes the judge's model from its constant
  ([prompt-engineering.md](../prompt-engineering/prompt-engineering.md) section 15), never
  DeepEval's default.
- **Must. The metric is built in a function-scoped fixture**, a fresh metric per test: `measure`
  writes its score, result and error onto the metric, and a metric that keeps an error reads as
  failed in every later test ([testing/fixtures.md](../testing/fixtures.md) section 3). Not at module
  level: a `GEval` given a model builds its client when it is created, so a module-level metric fails
  collection without a key, even in a default run that leaves the test out. Only `live_model` tests
  ask for the fixture, which reads the key through `Settings()`
  ([running-tests.md](../testing/running-tests.md) section 10).
- **Should. Three runs, and the passes counted** ([repeated-runs.md](repeated-runs.md) section 5):
  one run of one case decides nothing, and `assert_test` decides one case on one run. The metric
  stays advisory, never alone in a gate, until [judges.md](judges.md) sections 6 and 9 hold.
- **Should. Run it with `deepeval test run <file>`**, the documented entry point, and pin a release
  after April 2026, when a fix made it pass pytest's failing exit codes through to CI.
- **Must. Validate the metric** on your labels before it gates ([judges.md](judges.md) section 6):
  it is a judge like any other, and open issues report metrics that passed cases they never judged.
- **Must. Never `LLMTestCase(flaky=True)` in a gate**: it turns a failure into a warning.
- **Should. Keep one tracer**: DeepEval's `@observe` tracing duplicates what Langfuse already
  traces.

## 5. Not by default, and why

| Tool | Why it is not in the default set |
|---|---|
| agentevals | its trajectory evaluators moved to openevals in 2025; no release since July 2025, and an open bug swaps the arguments in `subset` mode |
| pytest-rerunfailures, for a claim about quality | a rerun passes a case that is right once in three runs ([repeated-runs.md](repeated-runs.md) section 4); where it belongs is [running-tests.md](../testing/running-tests.md) section 9 |
| small "k of n" plugins (flakelens, lcb-gate, pytest-stochastics, pytest-llm) | single authors, few users; a plain loop does the same ([repeated-runs.md](repeated-runs.md) section 5) |
| generic ready-made metrics used as a gate | they measure what the library's authors chose, not your failure modes ([evals.md](evals.md) section 3); validate first |
| recorded model answers as an eval | a replay checks parsing, not behaviour; recordings are [testing/libraries.md](../testing/libraries.md) section 3's subject |

## 6. Settings that keep data in and failures visible

**Must**, in CI and on any machine that handles real data:

- turn usage telemetry off: `DEEPEVAL_TELEMETRY_OPT_OUT=1`, `RAGAS_DO_NOT_TRACK=true`,
  `PROMPTFOO_DISABLE_TELEMETRY=1` (promptfoo still sends one notice that telemetry is off; its
  maintainers keep it on purpose);
- never set DeepEval's `IGNORE_DEEPEVAL_ERRORS` or `SKIP_DEEPEVAL_MISSING_PARAMS` in a gate: both let
  a run pass with cases that were not graded;
- set `CONFIDENT_API_KEY` only where DeepEval's results may be uploaded to Confident AI;
- set `LANGSMITH_TEST_TRACKING=false`, exactly, where LangSmith tests must not upload;
- pin every eval library in the lockfile, and read its changelog before an upgrade.

## 7. Sources

- Langfuse docs: self-hosting, pricing and self-hosted pricing, licence key, experiments via SDK,
  experiments in CI, code evaluators, LangChain and LangGraph integrations, Python SDK v3 to v4
  upgrade; the `langfuse/experiment-action` README; the Langfuse repository `LICENSE` and `ee/`
  folders; "Langfuse joins ClickHouse", 2026-01-16; GitHub discussion #5785 and issues #10721,
  #16177, discussion #12523. Read 2026-09-30.
- LangSmith docs: tracing with LangChain, evaluate, pytest, annotation queues, Studio, self-hosted,
  pricing and changelog; the langsmith SDK source (`utils.py`). Read 2026-09-30.
- openevals README and releases; agentevals README, PyPI history and issue #114; openevals pull
  request #237.
- DeepEval docs (getting started, CI/CD, flags, metrics, G-Eval, data privacy, environment
  variables) and 2026 changelog; issues #3346, #3283, #3356; local API check of deepeval 4.2.7.
- Ragas docs and PyPI history; issues #2995, #3004, #3028.
- Inspect AI docs (options, scorers, eval logs, agent bridge) and changelog, version 0.3.273.
- promptfoo docs (command line, CI/CD, assertions, telemetry, red team); "Promptfoo is joining
  OpenAI", 2026-03-09; issue #9968.
- Pydantic Evals docs (multi-run); box/flaky README and issues; the pytest-rerunfailures README.
- Arize, "A new chapter with Dynatrace", 2026-08-13.
- Practitioners: Hamel Husain's evals FAQ (hamel.dev), on generic library metrics that "measure
  abstract qualities that may not matter"; Rhesis pull request #2759, which removed Ragas as
  unmaintained, 2026-09-17; the Gentoo Python guide to pytest
  (projects.gentoo.org/python/guide/pytest.html), on flaky and pytest-rerunfailures both claiming
  `@pytest.mark.flaky`.
- No independent practitioner comparison of Langfuse and LangSmith was found in the research;
  section 2's conditions rest on each vendor's docs and the GitHub issues listed.
