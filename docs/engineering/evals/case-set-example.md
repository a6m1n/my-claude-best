# Example: the case set and the eval of one model call

A worked example for [evals.md](evals.md) and [repeated-runs.md](repeated-runs.md). It continues the
triage call of [prompt-example.md](../prompt-engineering/prompt-example.md): `support/triage/` reads a
customer's ticket and returns its kind and the date its problem first occurred. Here the call gets
its case set, its eval in Langfuse and the CI job that runs it. The eval calls the house client,
`AcmeAiClient`, because that example sends every model call through the one client in `core/`; a
LangChain app keeps the same case set, graders and gate, and changes only how the task reaches the
model ([With LangChain](#with-langchain)).
Every name is a placeholder, the tickets are invented, and the rates are example values.

What each part does:

- `evals/triage/cases_triage.jsonl` holds the cases, one per line, in git;
- `evals/triage/schemas.py` turns a line into a typed case once, at the edge;
- `evals/triage/experiment_triage.py` runs every case three times against the real model, grades
  each run by code, counts every run and fails when a rate falls below its baseline;
- `.github/workflows/evals.yml` runs it on a pull request that changes the call, and every night;
- the pytest contract for single cases stays in `tests/integration/triage/`.

## `evals/triage/cases_triage.jsonl`: the cases

```json
{"case_id": "crash-on-export", "ticket_text": "Since 2 March the CSV export fails with error 500.", "kind": "bug", "problem_first_occurred_on": "2026-03-02"}
{"case_id": "dark-mode-wish", "ticket_text": "Please add a dark mode to the dashboard.", "kind": "feature_request", "problem_first_occurred_on": null}
{"case_id": "excel-called-a-bug", "ticket_text": "Bug: export does not support Excel, only CSV.", "kind": "feature_request", "problem_first_occurred_on": null}
{"case_id": "vague-date", "ticket_text": "About a week ago the totals on invoices started to be wrong.", "kind": "bug", "problem_first_occurred_on": null}
```

Why it looks like this ([evals.md](evals.md) section 4):

- **Each case has a stable id and its pass criterion**: the kind and the date the call must return.
- **The set holds the near misses the prompt defines**: a request the customer calls a bug, and a
  vague date, where the right answer is the way out, `null`
  ([prompt-engineering.md](../prompt-engineering/prompt-engineering.md) section 8).
- **The tickets are real tickets with the identifying details removed**; here they are invented.
  A ticket that failed in production gets its line in the pull request that fixes it.

## `evals/triage/schemas.py`: one case, typed once

```python
# evals/triage/schemas.py
from datetime import date
from enum import StrEnum, unique

from pydantic import BaseModel, ConfigDict

from acme.support.triage.schemas import TicketKind


@unique
class Criterion(StrEnum):
    """What the triage eval grades; each has one grader and one rate."""

    KIND_MATCHES = "kind_matches"
    DATE_MATCHES = "date_matches"


class TriageCase(BaseModel):
    """One line of cases_triage.jsonl: a ticket and the triage it must get."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    case_id: str
    ticket_text: str
    kind: TicketKind
    problem_first_occurred_on: date | None
```

A line of the file is data from outside the code, so it becomes a model once, when it is read
([python.md](../python/python.md) section 4). A misspelt kind or a key the model does not name fails
the load, not the grading. `kind` is the application's own `TicketKind`, so a case cannot expect a
kind the application does not have. The criteria are a closed set, so they are an enum, not strings
([python.md](../python/python.md) section 3).

## `evals/triage/experiment_triage.py`: the run and its gate

```python
# evals/triage/experiment_triage.py
"""The triage eval: every case three times against the real model, graded by code, gated on its baseline."""

import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import Final

from acme_ai import AcmeAiSdk
from langfuse import Evaluation, RegressionError, RunnerContext, get_client
from langfuse.experiment import ExperimentItemResult, ExperimentResult, LocalExperimentItem

from acme.core.acme_ai_client import AcmeAiClient
from acme.core.config import Settings
from acme.core.langfuse_client import start_tracing
from acme.support.triage.consts import TRIAGE_LLM_MODEL, TRIAGE_LLM_REASONING_EFFORT
from acme.support.triage.schemas import TicketTriage
from acme.support.triage.services.service_triage import triage_ticket
from evals.triage.schemas import Criterion, TriageCase

CASES_FILE: Final = Path(__file__).with_name("cases_triage.jsonl")
RUNS_PER_CASE: Final = 3
# The pass rates of the version on main. The pull request that changes them explains why.
BASELINE: Final[Mapping[Criterion, float]] = {
    Criterion.KIND_MATCHES: 0.95,
    Criterion.DATE_MATCHES: 0.88,
}
# About two standard errors of a rate near 0.9 over 40 cases x 3 runs (repeated-runs.md section 5).
MARGIN: Final = 0.05


def experiment(context: RunnerContext) -> ExperimentResult:
    cases = [TriageCase.model_validate_json(line) for line in CASES_FILE.read_text().splitlines()]
    client = _uncached_client(Settings())

    result = context.run_experiment(
        name="triage",
        data=[_item(case) for case in cases for _ in range(RUNS_PER_CASE)],
        task=lambda *, item, **kwargs: _triage(item, client),
        evaluators=[kind_matches, date_matches],
    )

    _gate(result, runs_expected=len(cases) * RUNS_PER_CASE)
    return result


def kind_matches(*, output: TicketTriage, expected_output: TriageCase, **kwargs: object) -> Evaluation:
    return Evaluation(name=Criterion.KIND_MATCHES, value=output.kind is expected_output.kind)


def date_matches(*, output: TicketTriage, expected_output: TriageCase, **kwargs: object) -> Evaluation:
    expected = expected_output.problem_first_occurred_on
    return Evaluation(name=Criterion.DATE_MATCHES, value=output.problem_first_occurred_on == expected)


def _item(case: TriageCase) -> LocalExperimentItem:
    return LocalExperimentItem(input=case.ticket_text, expected_output=case, metadata={"case_id": case.case_id})


def _triage(item: LocalExperimentItem, client: AcmeAiClient) -> TicketTriage:
    return triage_ticket(
        item["input"],
        client,
        model=TRIAGE_LLM_MODEL,
        reasoning_effort=TRIAGE_LLM_REASONING_EFFORT,
    )


def _uncached_client(settings: Settings) -> AcmeAiClient:
    """The one model client with the cache switch on, so every run reaches the model."""
    return AcmeAiClient(
        AcmeAiSdk(api_key=settings.acme_ai_api_key.get_secret_value()),
        disable_prompt_cache=True,
        new_request_uuid=uuid.uuid4,
    )


def _gate(result: ExperimentResult, *, runs_expected: int) -> None:
    # run_experiment leaves out a run whose task raised, so the count is taken against the cases.
    graded = [run for run in result.item_results if len(run.evaluations) == len(BASELINE)]
    if len(graded) != runs_expected:
        raise RegressionError(result=result, message=f"{runs_expected - len(graded)} runs have no grade")

    for criterion, baseline in BASELINE.items():
        rate = _passes(graded, criterion) / runs_expected
        if rate < baseline - MARGIN:
            raise RegressionError(result=result, metric=criterion, value=rate, threshold=baseline - MARGIN)


def _passes(runs: list[ExperimentItemResult], criterion: Criterion) -> int:
    return sum(
        evaluation.value is True
        for run in runs
        for evaluation in run.evaluations
        if evaluation.name == criterion
    )


if __name__ == "__main__":
    settings = Settings()
    start_tracing(settings.langfuse_public_key, settings.langfuse_secret_key, settings.langfuse_base_url)
    experiment(RunnerContext(client=get_client()))
    get_client().flush()
```

Why it looks like this:

- **Three runs of every case, one rate over all of them** ([repeated-runs.md](repeated-runs.md)
  sections 4 and 5): the gate compares each criterion's rate with its baseline minus a margin, and
  never requires each case to pass three times in three.
- **Graded by code** ([evals.md](evals.md) section 5): the kind and the date have one right value,
  so no judge is needed. One grader per criterion, each with its own rate.
- **Every run counted** ([evals.md](evals.md) section 6): `run_experiment` leaves a run out when its
  task raised, and a missing grade fails the gate by name instead of raising the rate. The rate is
  divided by the runs the case set asked for, never by the results that came back.
- **The version before is the baseline** ([evals.md](evals.md) section 7): `BASELINE` holds the
  rates of the version on main, so a change is judged against it, and a pull request that moves
  them has to say why.
- **Every run reaches the model**: the client's cache switch
  ([prompt-engineering.md](../prompt-engineering/prompt-engineering.md) section 17) puts a fresh
  UUID first in each prompt, so three runs are three answers, not one answer and two cache hits.
  The model runs with the settings production uses ([repeated-runs.md](repeated-runs.md) section 2).
- **Traced** ([evals.md](evals.md) section 9): `run_experiment` records a trace per run, linked from
  its result in Langfuse, with the case id in its metadata.
- **Run as a module** (`uv run python -m evals.triage.experiment_triage`): `Settings()` is read once
  at the start, as in the application's own entry points ([python.md](../python/python.md)
  section 5), and Langfuse gets its keys through `start_tracing`, the one client of Langfuse of
  [logging/agent-example.md](../logging/agent-example.md). The `langfuse/experiment-action` GitHub
  Action can call `experiment(context)` directly instead, and adds a comment to the pull request.

`AcmeAiClient`, `Settings` and `triage_ticket` are those of
[prompt-example.md](../prompt-engineering/prompt-example.md), and `start_tracing` that of
[logging/agent-example.md](../logging/agent-example.md); `acme_ai_api_key` and the Langfuse keys
stand for the settings fields those examples leave out.

## With LangChain

In a LangChain app the task hands the app's chat model, in place of the house client, to the app's
own `triage_ticket`; the case set, the graders and the gate stay as they are. `...` marks code that
stays as above:

```python
# evals/triage/experiment_triage.py in a LangChain app: in place of experiment, _triage and _uncached_client
# Drop the imports only they used: AcmeAiSdk, AcmeAiClient and TRIAGE_LLM_REASONING_EFFORT.
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI

from acme.core.langfuse_client import callback_handler
from acme.core.openai_client import chat_model


def experiment(context: RunnerContext) -> ExperimentResult:
    cases = ...
    llm = chat_model(TRIAGE_LLM_MODEL, Settings().openai_api_key)
    tracing = callback_handler()

    result = context.run_experiment(..., task=lambda *, item, **kwargs: _triage(item, llm, tracing))

    ...


def _triage(item: LocalExperimentItem, llm: ChatOpenAI, tracing: BaseCallbackHandler) -> TicketTriage:
    return triage_ticket(
        item["input"], llm, tracing=tracing, disable_prompt_cache=True, new_request_uuid=uuid.uuid4
    )
```

`chat_model`, `callback_handler` and `openai_api_key` are those of
[logging/agent-example.md](../logging/agent-example.md); `TRIAGE_LLM_MODEL` is this app's own
`ChatModel` constant. Its `triage_ticket` takes the chat model, the handler, the switch and the UUID
source, and hands the last two to the function of `core/openai_client.py` that puts the UUID line
first, as `build_agent` hands them to `PromptCacheSwitchMiddleware`; neither function is shown. The
cache switch and the effort's mapping belong where the app applies them,
in its one client or, for an agent, in `build_agent`'s middleware, which
[agent-eval-example.md](agent-eval-example.md) turns on; never in the eval
([prompt-engineering.md](../prompt-engineering/prompt-engineering.md) sections 15 and 17). The eval
turns the switch on, as `_uncached_client` and agent-eval-example.md do, so a response cache that
matches the request exactly, in a gateway or LangChain's global cache, cannot answer a run from an
earlier one.

## `.github/workflows/evals.yml`: when it runs

```yaml
# .github/workflows/evals.yml
name: evals

on:
  pull_request:
    paths:
      - "src/acme/support/triage/prompts.py"
      - "src/acme/support/triage/consts.py"
      - "evals/triage/**"
  schedule:
    - cron: "0 3 * * *"

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v6
      - run: uv sync --locked
      - run: uv run python -m evals.triage.experiment_triage
        env:
          # A key of its own, in a project with a monthly spend limit (evals.md section 8).
          ACME_ACME_AI_API_KEY: ${{ secrets.EVALS_ACME_AI_API_KEY }}
          ACME_LANGFUSE_PUBLIC_KEY: ${{ secrets.LANGFUSE_PUBLIC_KEY }}
          ACME_LANGFUSE_SECRET_KEY: ${{ secrets.LANGFUSE_SECRET_KEY }}
          ACME_LANGFUSE_BASE_URL: ${{ vars.LANGFUSE_BASE_URL }}
```

A pull request that changes the triage prompt or its model runs the eval, and so does every night:
the schedule catches a change behind the model's alias that no pull request made
([evals.md](evals.md) section 8). A `RegressionError` ends the module with an error, so the job
fails. The key belongs to a project with a spend limit, because nobody watches the nightly run.
`Settings` reads each field from `ACME_` plus the field's name in upper case
([python/settings-example.md](../python/settings-example.md)), so `acme_ai_api_key` comes from
`ACME_ACME_AI_API_KEY`. The job must also set every other required field of the application's
`Settings`, such as the database and payments fields of that example; this snippet leaves them out.

## The contract of single cases

The eval gives the rate over the set. A contract that must hold for one case is a real-model test in
`tests/integration/triage/test_service_triage.py`, as
[repeated-runs.md](repeated-runs.md) section 5 shows: "a crash report is filed as a bug in two runs
of three", a plain loop and a count. It runs by hand, as
[running-tests.md](../testing/running-tests.md) section 10 says, before a pull request that changes
the prompt.

## What this example does not claim

The baseline rates and the margin are example values. A real margin comes from your own set's size
and rates ([repeated-runs.md](repeated-runs.md) section 7), and a real case set starts from reading
real traces ([evals.md](evals.md) section 3).
