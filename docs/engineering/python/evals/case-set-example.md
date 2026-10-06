# Example: the case set and the eval of one model call

A worked example for [evals.md](evals.md) and [repeated-runs.md](repeated-runs.md). It continues the
triage call of [prompt-example.md](../../any-language/prompt-engineering/prompt-example.md): `support/triage/` reads a
customer's ticket and returns its kind and the date its problem first occurred. Here the call gets
its case set, its eval in Langfuse and the CI job that runs it. The eval calls the house client,
`AcmeAiClient`, because that example sends every model call through the one client in `core/`; a
LangChain app keeps the same case set, graders and gate, and changes only how the task reaches the
model ([With LangChain](#with-langchain)).
Every name is a placeholder, the tickets are invented, and the rates are example values.

What each part does:

- `evals/triage/cases_triage.jsonl` holds the cases, one per line, in git;
- `evals/triage/schemas.py` turns a line into a typed case once, at the edge;
- `evals/triage/experiment_triage.py` runs every case three times against the real model and grades
  each run by code;
- `evals/rate_gate.py` counts every run, fails when a rate falls below its baseline, and reports
  the rates;
- `.github/workflows/evals.yml` runs it on a pull request that changes the call, and every night;
- the pytest contract for single cases stays in `tests/integration/triage/`.

## `evals/triage/cases_triage.jsonl`: the cases

```json
{"case_id": "crash-on-export", "ticket_text": "Since 2 March 2026 the CSV export fails with error 500.", "kind": "bug", "problem_first_occurred_on": "2026-03-02"}
{"case_id": "dark-mode-wish", "ticket_text": "Please add a dark mode to the dashboard.", "kind": "feature_request", "problem_first_occurred_on": null}
{"case_id": "excel-called-a-bug", "ticket_text": "Bug: export does not support Excel, only CSV.", "kind": "feature_request", "problem_first_occurred_on": null}
{"case_id": "vague-date", "ticket_text": "About a week ago the totals on invoices started to be wrong.", "kind": "bug", "problem_first_occurred_on": null}
```

Why it looks like this ([evals.md](evals.md) section 4):

- **Each case has a stable id and its pass criterion**: the kind and the date the call must return.
- **The set holds the near misses the prompt defines**: a request the customer calls a bug, and a
  vague date, where the right answer is the way out, `null`
  ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 8).
- **The tickets are real tickets with the identifying details removed**; here they are invented.
  A ticket that failed in production gets its line in the pull request that fixes it.

## `evals/triage/schemas.py`: one case, typed once

```python
# evals/triage/schemas.py
from dataclasses import dataclass
from datetime import date
from enum import StrEnum, unique

from pydantic import BaseModel, ConfigDict

from acme.support.triage.schemas import TicketKind, TicketTriage


@unique
class Criterion(StrEnum):
    """What the triage eval grades; each has one grader and one rate."""

    KIND_MATCHES = "kind_matches"
    DATE_MATCHES = "date_matches"


@unique
class RunMeasure(StrEnum):
    """What the eval reports over the whole run, next to the rates; never gated."""

    DATE_WAY_OUT = "date_way_out"


@unique
class TriageEnd(StrEnum):
    """How one run of the triage call ended; only a run that answered can pass."""

    ANSWERED = "answered"
    REFUSED = "refused"
    CUT_OFF = "cut_off"
    INVALID_ANSWER = "invalid_answer"


class TriageCase(BaseModel):
    """One line of cases_triage.jsonl: a ticket and the triage it must get."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    case_id: str
    ticket_text: str
    kind: TicketKind
    problem_first_occurred_on: date | None


@dataclass(frozen=True)
class TriageRun:
    """What one run of the triage call did: how it ended, and its triage."""

    ended: TriageEnd
    triage: TicketTriage | None

    def __post_init__(self) -> None:
        # Checked on the type, never only in a comment: a refused run that held a
        # triage would pass both graders (python.md section 2).
        if (self.triage is None) != (self.ended is not TriageEnd.ANSWERED):
            raise ValueError("a run holds a triage exactly when it answered")
```

A line of the file is data from outside the code, so it becomes a model once, when it is read
([python.md](../language/python.md) section 4). A misspelt kind or a key the model does not name fails
the load, not the grading. `kind` is the application's own `TicketKind`, that of
[prompt-example.md](../../any-language/prompt-engineering/prompt-example.md), so a case cannot expect a kind the
application does not have. The criteria, the run measures and how a run ended are closed sets, so
they are enums, not strings ([python.md](../language/python.md) section 3). `TriageRun` is built by
the eval's own code from values it already holds, so it is a frozen dataclass
([python.md](../language/python.md) section 4). A run that did not answer is still a `TriageRun`
with its `TriageEnd` and no triage: an untagged union of an answer and a failure would make every
caller write an `isinstance` check, and `TicketTriage | None` is the documented form for no result
([python.md](../language/python.md) section 3). `__post_init__` raises when the triage and the
ending disagree, so the rule between the two fields is on the type, not in a comment
([python.md](../language/python.md) section 2).

## `evals/triage/experiment_triage.py`: the run and its gate

```python
# evals/triage/experiment_triage.py
"""The triage eval: every case three times against the real model, graded by code, gated on its baseline."""

import logging.config
import uuid
from collections import Counter
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Final

from acme_ai import AcmeAiSdk
from langfuse import Evaluation, RunnerContext, get_client
from langfuse.experiment import (
    ExperimentItemResult,
    ExperimentResult,
    LocalExperimentItem,
)

from acme.core.acme_ai_client import AcmeAiClient
from acme.core.config import Settings
from acme.core.errors import ModelAnswerInvalid, ModelOutputCutOff, ModelRefused
from acme.core.langfuse_client import start_tracing
from acme.core.logging import build_logging_config
from acme.support.triage.consts import TRIAGE_LLM_MODEL, TRIAGE_LLM_REASONING_EFFORT
from acme.support.triage.schemas import TicketTriage
from acme.support.triage.services.service_triage import triage_ticket
from evals.rate_gate import CASE_ID_METADATA_KEY, check_rates, rate_report
from evals.triage.schemas import (
    Criterion,
    RunMeasure,
    TriageCase,
    TriageEnd,
    TriageRun,
)

CASES_FILE: Final = Path(__file__).with_name("cases_triage.jsonl")
# Three runs of each case, one rate over all: one run shows no rate
# (repeated-runs.md sections 5 and 7).
RUNS_PER_CASE: Final = 3
# The pass rates of the version on main. The pull request that changes them explains why.
BASELINE: Final[Mapping[Criterion, float]] = {
    Criterion.KIND_MATCHES: 0.95,
    Criterion.DATE_MATCHES: 0.88,
}
# Two standard errors of the lowest baseline, 0.88, over 40 cases x 3 runs if the runs
# were independent; they are not, so the real error is larger (repeated-runs.md
# section 5).
MARGIN: Final = 0.06


def experiment(context: RunnerContext) -> ExperimentResult:
    """The entry the langfuse/experiment-action calls; `python -m` starts at main()."""
    return run_triage_eval(context, Settings())


def run_triage_eval(context: RunnerContext, settings: Settings) -> ExperimentResult:
    cases = _cases()

    client = _uncached_client(settings)

    # One trace per run, so a failed case can be opened; a plain loop leaves none
    # (evals.md section 9).
    result = context.run_experiment(
        name="triage",
        data=[_item(case) for case in cases for _ in range(RUNS_PER_CASE)],
        task=lambda *, item, **kwargs: _triage(item, client),
        evaluators=[kind_matches, date_matches],
        # The way out, a null date, counted apart from the rates (evals.md section 4).
        run_evaluators=[date_way_out],
        # The prompt is in git, so the commit is its version (evals.md section 9).
        metadata={
            "model": TRIAGE_LLM_MODEL,
            "reasoning_effort": TRIAGE_LLM_REASONING_EFFORT,
            "commit": settings.git_commit,
        },
    )

    rates, breach = check_rates(
        result, runs_asked=_runs_asked(cases), baseline=BASELINE, margin=MARGIN
    )

    report = rate_report(result, rates, baseline=BASELINE, margin=MARGIN)
    print(report)  # noqa: T201  # the report is this command's output

    # Raised after the report, so a red run's log holds every rate too.
    if breach is not None:
        raise breach

    return result


def kind_matches(
    *, output: TriageRun, expected_output: TriageCase, **kwargs: object
) -> Evaluation:
    if output.triage is None:
        return _failed_run(Criterion.KIND_MATCHES, output.ended)

    matches = output.triage.kind is expected_output.kind
    return Evaluation(name=Criterion.KIND_MATCHES, value=matches)


def date_matches(
    *, output: TriageRun, expected_output: TriageCase, **kwargs: object
) -> Evaluation:
    if output.triage is None:
        return _failed_run(Criterion.DATE_MATCHES, output.ended)

    matches = (
        output.triage.problem_first_occurred_on
        == expected_output.problem_first_occurred_on
    )
    return Evaluation(name=Criterion.DATE_MATCHES, value=matches)


def date_way_out(
    *, item_results: list[ExperimentItemResult], **kwargs: object
) -> Evaluation:
    """The share of answered runs that took the way out, a null date.

    The comment counts the answered runs, then gives the two-by-two table of evals.md
    section 4: expected null or a date, returned null or a date. A run that did not
    answer fails both rates already.
    """
    table = Counter(
        (
            case.problem_first_occurred_on is None,
            triage.problem_first_occurred_on is None,
        )
        for case, triage in _answered(item_results)
    )
    took_way_out = table[True, True] + table[False, True]

    return Evaluation(
        name=RunMeasure.DATE_WAY_OUT,
        value=took_way_out / table.total() if table else 0.0,
        comment=(
            f"of {table.total()} answered runs: "
            f"expected null: {table[True, True]} null, {table[True, False]} a date; "
            f"expected a date: {table[False, True]} null, {table[False, False]} a date"
        ),
    )


def _answered(
    item_results: Iterable[ExperimentItemResult],
) -> Iterator[tuple[TriageCase, TicketTriage]]:
    """Each run that answered, with its case; this eval's items are local dicts."""
    for run in item_results:
        case = run.item["expected_output"] if isinstance(run.item, dict) else None
        if (
            isinstance(case, TriageCase)
            and isinstance(run.output, TriageRun)
            and run.output.triage is not None
        ):
            yield case, run.output.triage


def _failed_run(criterion: Criterion, ended: TriageEnd) -> Evaluation:
    """A run with no triage fails every criterion; the comment says how it ended."""
    return Evaluation(name=criterion, value=False, comment=f"run ended: {ended}")


def _cases() -> list[TriageCase]:
    return [
        TriageCase.model_validate_json(line)
        for line in CASES_FILE.read_text().splitlines()
    ]


def _runs_asked(cases: Iterable[TriageCase]) -> Counter[str]:
    return Counter(case.case_id for case in cases for _ in range(RUNS_PER_CASE))


def _item(case: TriageCase) -> LocalExperimentItem:
    return LocalExperimentItem(
        input=case.ticket_text,
        expected_output=case,
        metadata={CASE_ID_METADATA_KEY: case.case_id},
    )


def _triage(item: LocalExperimentItem, client: AcmeAiClient) -> TriageRun:
    # The model's own failure is a failed case. ModelUnavailable, the provider's, is not
    # caught: it is an error of the run (evals.md section 6).
    try:
        triage = triage_ticket(
            item["input"],
            client,
            model=TRIAGE_LLM_MODEL,
            reasoning_effort=TRIAGE_LLM_REASONING_EFFORT,
        )
    except ModelRefused:
        return TriageRun(ended=TriageEnd.REFUSED, triage=None)
    except ModelOutputCutOff:
        return TriageRun(ended=TriageEnd.CUT_OFF, triage=None)
    except ModelAnswerInvalid:
        return TriageRun(ended=TriageEnd.INVALID_ANSWER, triage=None)

    return TriageRun(ended=TriageEnd.ANSWERED, triage=triage)


def _uncached_client(settings: Settings) -> AcmeAiClient:
    """The one model client with the cache switch on, so every run reaches the model."""
    return AcmeAiClient(
        AcmeAiSdk(api_key=settings.acme_ai_api_key.get_secret_value()),
        disable_prompt_cache=True,
        new_request_uuid=uuid.uuid4,
    )


def main() -> None:
    settings = Settings()

    # The log goes to stderr, so stdout holds only the report (logging.md section 6).
    logging.config.dictConfig(
        build_logging_config(settings.log_level, settings.log_format, stream="stderr")
    )

    start_tracing(
        settings.langfuse_public_key,
        settings.langfuse_secret_key,
        settings.langfuse_base_url,
        environment=settings.langfuse_environment,
        release=settings.git_commit,
        enabled=settings.langfuse_tracing_enabled,
    )

    langfuse = get_client()

    run_triage_eval(RunnerContext(client=langfuse), settings)

    langfuse.flush()


if __name__ == "__main__":
    main()
```

## `evals/rate_gate.py`: the gate every experiment ends with

```python
# evals/rate_gate.py
"""The gate of every eval run: each run graded, and each rate within its margin of the baseline."""

from collections import Counter
from collections.abc import Iterable, Mapping
from enum import StrEnum
from typing import Final, TypeVar

from langfuse import RegressionError
from langfuse.experiment import ExperimentItemResult, ExperimentResult

# Every experiment writes the case id under this key and the gate reads it, so the key
# is one name: a typo in one file would leave every run ungraded (python.md section 3).
CASE_ID_METADATA_KEY: Final = "case_id"

CriterionT = TypeVar("CriterionT", bound=StrEnum)


def check_rates(
    result: ExperimentResult,
    *,
    runs_asked: Counter[str],
    baseline: Mapping[CriterionT, float],
    margin: float,
) -> tuple[dict[CriterionT, float], RegressionError | None]:
    """Each criterion's rate over the runs the cases asked for, and an error for the
    first rate below its baseline, left for the caller to raise once the report is out.

    Raises RegressionError when a run has no grade: no rate can be told then.
    """
    # A grader that raised leaves no score: such a run counts as missing below, never
    # as a fail (evals.md section 6).
    graded = [
        run for run in result.item_results if len(run.evaluations) == len(baseline)
    ]

    # run_experiment leaves out a run whose task raised, so the runs are checked against the cases.
    missing = runs_asked - Counter(_case_id(run) for run in graded)
    if missing:
        raise RegressionError(
            result=result, message=f"runs with no grade: {dict(missing)}"
        )

    rates = {
        criterion: _passes(graded, criterion) / runs_asked.total()
        for criterion in baseline
    }

    for criterion, rate in rates.items():
        if rate < baseline[criterion] - margin:
            return rates, RegressionError(
                result=result,
                metric=criterion,
                value=rate,
                threshold=baseline[criterion] - margin,
            )

    return rates, None


def rate_report(
    result: ExperimentResult,
    rates: Mapping[CriterionT, float],
    *,
    baseline: Mapping[CriterionT, float],
    margin: float,
) -> str:
    """Each rate with its baseline and the margin, then each run measure."""
    lines = [
        f"{criterion}: {rate:.3f} over the runs asked; "
        f"baseline {baseline[criterion]:.2f}, margin {margin:.2f}"
        for criterion, rate in rates.items()
    ]
    lines += [
        f"{measure.name}: {measure.value}; {measure.comment}"
        for measure in result.run_evaluations
    ]

    return "\n".join(lines)


def _case_id(run: ExperimentItemResult) -> str:
    """The case id an experiment put into the item's metadata."""
    metadata = run.item["metadata"] if isinstance(run.item, dict) else run.item.metadata
    return str((metadata or {})[CASE_ID_METADATA_KEY])


def _passes(runs: Iterable[ExperimentItemResult], criterion: StrEnum) -> int:
    return sum(
        evaluation.value is True
        for run in runs
        for evaluation in run.evaluations
        if evaluation.name == criterion
    )
```

The gate knows no module: an experiment passes its cases' ids, its baseline and its margin. So it
sits at the root of `evals/`, where every experiment imports it
([file-structure.md](../../any-language/file-structure/file-structure.md) section 6: code that belongs to no module
moves down).

Why it looks like this:

- **Three runs of every case, one rate over all of them** ([repeated-runs.md](repeated-runs.md)
  sections 4 and 5): the gate compares each criterion's rate with its baseline minus a margin, and
  never requires each case to pass three times in three.
- **Graded by code** ([evals.md](evals.md) section 5): the kind and the date have one right value,
  so no judge is needed. One grader per criterion, each with its own rate. The same section asks
  each grader to fail known-bad output and a system that does nothing before it gates; this example
  leaves that check out ([What this example does not claim](#what-this-example-does-not-claim)).
- **The way out counted apart** ([evals.md](evals.md) section 4,
  [prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 8): a
  null date is the call's way out, and three of the four cases expect it, so a call that never
  reads a date would still pass `DATE_MATCHES` on those three. `date_way_out`, a run evaluator
  that Langfuse runs once over all the results, reports the share of answered runs that took the
  way out, with the count of answered runs and the two-by-two table of expected null or a date
  against returned null or a date as its comment.
  It sits next to the rates and does not gate; `DATE_MATCHES` stays as it is.
- **Every run counted** ([evals.md](evals.md) section 6): a refusal, an answer cut off or one that
  does not parse is the model's own answer, so `_triage` returns it as a `TriageRun` with no
  triage and its `TriageEnd`, and each grader fails the run with that ending as its comment. Only
  `ModelUnavailable`, the provider's failure, raises. `run_experiment` leaves a run out when its
  task raised, so the gate compares the graded runs with the runs each case asked for, and a
  missing grade fails the gate with the case ids instead of raising the rate. The rate is divided
  by the runs the case set asked for, never by the results that came back.
- **The baseline is main's last run**, which departs from [evals.md](evals.md) section 7: `BASELINE`
  holds the rates from the last run of the version on main on the same cases, not from the old
  version run again in this job. Why, and what it costs, is under
  [What this example does not claim](#what-this-example-does-not-claim). A change is judged against
  these rates, and a pull request that moves them has to say why.
- **The rates in the output** ([evals.md](evals.md) section 8): `check_rates` returns each
  criterion's rate over the runs asked, with an error for a rate below its baseline, and
  `rate_report` turns the rates into one line per criterion, with its baseline and the margin,
  followed by each run measure. `run_triage_eval` prints the report before it raises that error, so
  on either entry point, red run or green, the job's log holds the result the pull request's
  Verification quotes next to its baseline.
- **Every run reaches the model**: the client's cache switch
  ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 17) puts a fresh
  UUID first in each prompt, so a response cache in front of the model cannot answer a run from an
  earlier one. The model runs with the settings production uses
  ([repeated-runs.md](repeated-runs.md) section 2).
- **Traced, with what produced it** ([evals.md](evals.md) section 9): `run_experiment` records a
  trace per run, linked from its result in Langfuse, with the case id in its metadata; the run's
  metadata names the model, its effort and the commit, which versions the prompt.
- **Run as a module** (`uv run --locked python -m evals.triage.experiment_triage`): `main()` reads
  `Settings()` once, as the application's own entry points do ([python.md](../language/python.md)
  section 5), sets up logging as the CLI of [python/logging/setup-example.md](../logging/setup-example.md)
  does, and gives Langfuse its keys through `start_tracing`, the one client of Langfuse of
  [python/logging/agent-example.md](../logging/agent-example.md). The `langfuse/experiment-action` GitHub
  Action calls `experiment(context)` instead, and adds a comment to the pull request.

`AcmeAiClient`, `AcmeAiSdk`, `Settings`, `triage_ticket`, `TicketTriage`, `TRIAGE_LLM_MODEL`,
`TRIAGE_LLM_REASONING_EFFORT` and the `acme.core.errors` classes are those of
[prompt-example.md](../../any-language/prompt-engineering/prompt-example.md), `build_logging_config` and the
settings fields `log_level` and `log_format` those of
[python/logging/setup-example.md](../logging/setup-example.md), and `start_tracing` that of
[python/logging/agent-example.md](../logging/agent-example.md); `acme_ai_api_key`, `git_commit`,
`langfuse_environment`, `langfuse_tracing_enabled` and the Langfuse keys and URL stand for the
settings fields those examples leave out.

## With LangChain

In a LangChain app only the task changes; the case set, the graders, the three runs and the gate
stay as they are. The task runs the app's own code, built the way the app builds it, with three
things the eval adds:

- **the cache switch on**, passed where the app applies it, as `build_agent` passes it to
  `PromptCacheSwitchMiddleware` ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md)
  section 17), so a response cache in a gateway or LangChain's global cache cannot answer a run from
  an earlier one;
- **the Langfuse handler** in the call's `callbacks`, so the run's trace holds the model and tool
  calls ([evals.md](evals.md) section 9);
- **the model and its effort from the call site's own constants**, the ones the app uses
  ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 15): the eval never
  picks them.

[agent-eval-example.md](agent-eval-example.md) shows such a task end to end, for the LangChain agent
of [python/logging/agent-example.md](../logging/agent-example.md), with the graders and the gate of this
example.

## `.github/workflows/evals.yml`: when it runs

```yaml
# .github/workflows/evals.yml
name: evals

on:
  pull_request:
    paths:
      - "src/acme/support/triage/**"
      - "src/acme/core/acme_ai_client.py"
      - "evals/rate_gate.py"
      - "evals/triage/**"
  # Nightly too: catches a change on the vendor's side that no pull request made
  # (evals.md section 8).
  schedule:
    - cron: "0 3 * * *"

permissions:
  contents: read

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          persist-credentials: false  # the job holds a paid key: the token does not stay in .git/config
      - uses: astral-sh/setup-uv@v10.2.0
      - run: uv sync --locked
      - run: uv run --locked python -m evals.triage.experiment_triage
        env:
          # A key of its own, in a project with a monthly spend limit (evals.md section 8).
          ACME_ACME_AI_API_KEY: ${{ secrets.EVALS_ACME_AI_API_KEY }}
          # An evals-only Langfuse project: its keys read every trace in it, and this
          # job runs the pull request's code.
          ACME_LANGFUSE_PUBLIC_KEY: ${{ secrets.EVALS_LANGFUSE_PUBLIC_KEY }}
          ACME_LANGFUSE_SECRET_KEY: ${{ secrets.EVALS_LANGFUSE_SECRET_KEY }}
          ACME_LANGFUSE_BASE_URL: ${{ vars.LANGFUSE_BASE_URL }}
          # Required: the settings give it no default. The experiment runner files each case's
          # trace under sdk-experiment whatever this says (langfuse-python 4.16.0).
          ACME_LANGFUSE_ENVIRONMENT: development
          ACME_GIT_COMMIT: ${{ github.sha }}
```

A pull request that changes what the triage call sends or how its run is graded runs the eval: the
triage module (its prompt, its response schema, its model), the one client, the rate gate or the
case set. So does every night: the schedule catches a change on the vendor's side that no pull
request made ([evals.md](evals.md) section 8). A `RegressionError` ends the module with an error,
so the job fails; a run that passes prints its report in the job's log. The key belongs to a
project with a spend limit, because nobody watches the nightly run. The Langfuse keys belong to a
project of their own, because a project's keys read every trace in it, and this job runs the pull
request's code.
`Settings` reads each field from `ACME_` plus the field's name in upper case
([python/language/settings-example.md](../language/settings-example.md)), so `acme_ai_api_key` comes from
`ACME_ACME_AI_API_KEY`. The job must also set every other required field of the application's
`Settings`, such as the database and payments fields of that example, with throwaway values, never
the real secrets; this snippet leaves them out.
The checkout, the uv setup and the read-only token are those of
[python/static-checks/setup-example.md](../static-checks/setup-example.md): the job holds a paid key, so
the token does not stay in `.git/config`.

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

Before a grader gates anything, it runs on outputs known to be bad and on a system that does
nothing, and must fail them ([evals.md](evals.md) section 5): here, a `TriageRun` that ended with no
triage, and a fixed answer with a null date on a case that states one. This example leaves that
check out.

[evals.md](evals.md) section 7 asks to run the old version and the new one on the same cases and to
list every case that passed before and fails now; this example compares with stored rates
instead, which saves the second set of calls. Between refreshes of `BASELINE`, a change on the
vendor's side moves the rates with no change in the code; the scheduled run on main shows it
([evals.md](evals.md) section 8).
