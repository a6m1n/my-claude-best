# Repeated runs: flaky results and pass rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. Why the same input gives a different answer](#2-why-the-same-input-gives-a-different-answer)
- [3. A flaky test with no model in it is a bug](#3-a-flaky-test-with-no-model-in-it-is-a-bug)
- [4. The pass rule of a check](#4-the-pass-rule-of-a-check)
- [5. "It may be wrong one time in three"](#5-it-may-be-wrong-one-time-in-three)
- [6. pass@k and pass^k for agents](#6-passk-and-passk-for-agents)
- [7. How many cases, how many runs](#7-how-many-cases-how-many-runs)
- [8. An error is not an answer](#8-an-error-is-not-an-answer)
- [9. Sources](#9-sources)

## 1. Purpose and the one rule

This file is for anyone who writes a check on what a model answers, and for anyone who meets a
check that passes one time and fails the next. Its levels are those of
[evals.md](evals.md) section 1.

The one rule: **a check on a model's answer says how many of its runs must pass before it runs, and
a test with no model in it that passes one time and fails the next is a bug to fix, not a check to
repeat.**

## 2. Why the same input gives a different answer

A hosted model does not give the same answer twice, even at temperature 0. Anthropic: "Even with
temperature set to 0, the results will not be fully deterministic and identical inputs may produce
different outputs across API calls"; newer Anthropic models accept no temperature other than the
default. OpenAI calls its `seed` parameter "best effort". Thinking Machines ran one prompt 1,000
times at temperature 0 and got 80 different completions, because the server batches requests of
different sizes. A judge model varies the same way: five judges gave different scores to identical
inputs at temperature 0.

**Must.** An eval runs the model with the settings production uses. Never set the temperature to 0
or fix a seed to make an eval repeat itself: it buys no repeatability, it tests settings production
does not use, and a newer model may reject the call.

## 3. A flaky test with no model in it is a bug

A test that calls no model and passes one run and fails the next has a cause: an order, a clock, a
shared path or port. Find it and fix it; [testing/running-tests.md](../testing/running-tests.md)
section 9 owns this rule and the tools for it. Everything below is about checks that call a real
model.

## 4. The pass rule of a check

**Must.** Before a check on a model's answer runs, name its pass rule: how many runs, and how many
of them must pass. Use one of these four:

| Rule | Passes when | Use it for |
|---|---|---|
| all of n (pass^n) | every run passes | behaviour that must not fail: money, permissions, a policy, a safety limit |
| k of n | at least k of the n runs pass | behaviour that may fail now and then |
| any of n (pass@n) | at least one run passes | "can the system do it at all": a capability, never a quality claim |
| a rate over the set | the pass rate over all cases and runs meets the threshold, or falls no more than a margin below the baseline | the quality of a feature |

A rule on repeated runs only gives the chance that a case passes, and that chance depends on how
often the case really succeeds. With three runs, for a case whose single run succeeds with
probability p:

| p | all of 3 | 2 of 3 | any of 3 |
|---|---|---|---|
| 0.95 | 0.857 | 0.993 | 1.000 |
| 0.90 | 0.729 | 0.972 | 0.999 |
| 0.80 | 0.512 | 0.896 | 0.992 |
| 0.67 | 0.296 | 0.741 | 0.963 |
| 0.50 | 0.125 | 0.500 | 0.875 |
| 0.30 | 0.027 | 0.216 | 0.657 |

The formulas are p³, 3p² − 2p³ and 1 − (1 − p)³. Rerunning a failed test twice, as
pytest-rerunfailures' `--reruns 2` does, is any of 3: [running-tests.md](../testing/running-tests.md)
section 10 owns that command and shows what it lets through.

**Must.** Gate a feature on the rate over the set, not on every case's k of n at once. A per-case
rule is a report per case. When a suite requires every one of 100 cases to pass 2 of 3, and each
case really succeeds 8 times in 10, the suite passes with a chance of 0.896¹⁰⁰, about 2 in 100,000:
it is red every day for no reason.

## 5. "It may be wrong one time in three"

A feature that may be wrong one time in three makes a claim about a rate: a single run is right at
least two times in three, p ≥ 2/3. What checks that claim:

- **The rate over the set.** Run every case three times, count the passes, and compare the rate
  with 2/3 minus a margin, or with the baseline's rate on the same cases (section 7). With 50 cases
  and 3 runs each, the rate's standard error is about 4 points if every run were independent. Runs
  of one case are not independent, so the real error is larger; gate on a margin of at least two
  standard errors, or on the paired comparison with the baseline.
- **Not "2 of 3" on each case.** A case that is right exactly two times in three passes "2 of 3" only
  74% of the time, so on every run about one good case in four turns red; and a case right only half
  the time still passes half the time.
- **"2 of 3" per case is a regression floor** for cases that normally pass almost always: at
  p = 0.9 it fails 2.8% of runs, and a case that breaks (p = 0.3) fails 78% of runs. **All of 3** is
  the rule for cases that must not fail.

How to run "2 of 3" in pytest:

**Should.** A plain loop in the test, with the count as the assertion. It needs no plugin, works
with async tests and with every other plugin, and shows every answer when it fails:

```python
# tests/integration/triage/test_service_triage.py
def kind_or_model_failure(
    ticket_text: str, client: AcmeAiClient
) -> TicketKind | ModelRefused | ModelOutputCutOff | ModelAnswerInvalid:
    """One run's kind, or the model's own failure, which counts as a wrong kind.

    ModelUnavailable, the provider's failure, is not caught: the test fails on it as
    an error of the run (evals.md section 6).
    """
    try:
        return triage_ticket(
            ticket_text,
            client,
            model=TRIAGE_LLM_MODEL,
            reasoning_effort=TRIAGE_LLM_REASONING_EFFORT,
        ).kind
    except (ModelRefused, ModelOutputCutOff, ModelAnswerInvalid) as exc:
        return exc


@pytest.mark.live_model
class TestTriageTicket:
    """The triage call files a ticket under its kind."""

    def test_a_crash_report_is_filed_as_a_bug_in_two_runs_of_three(
        self, uncached_model_client: AcmeAiClient
    ) -> None:
        kinds = [
            kind_or_model_failure(CRASH_ON_EXPORT, uncached_model_client)
            for _ in range(3)
        ]

        assert kinds.count(TicketKind.BUG) >= 2
```

The client, the fixture and the call are those of
[running-tests.md](../testing/running-tests.md) section 10, and the `acme.core.errors` classes those
of [prompt-example.md](../prompt-engineering/prompt-example.md). A refusal, an answer cut off or one
that does not parse is the model's own answer, so `kind_or_model_failure` puts it in the list in
place of a kind, and it counts as a wrong one. Only `ModelUnavailable`, the provider's failure,
raises, and the test fails on it as an error of the run ([evals.md](evals.md) section 6). pytest's
report prints the list, so a red run shows every answer, and the loop makes three calls unless the
provider fails.

**Optional.** The `flaky` plugin's decorator, `@flaky(max_runs=3, min_passes=2)`, imported with
`from flaky import flaky`. It stops as soon as the rule is decided, so a case that passes twice
costs two calls. Add it only when you accept its limits, each checked on pytest 9.1.1 with flaky
3.8.1:

- **Never the marker form**, `@pytest.mark.flaky(max_runs=3, min_passes=2)`, when
  pytest-rerunfailures is installed: both plugins claim the marker, and a case that was right once
  and wrong twice passed.
- **Never together with `--reruns`**: pytest-rerunfailures reruns the whole flaky cycle, and the
  same case passed.
- It has had no release since March 2024, it patches pytest's internals, and it breaks async tests
  (issue #166), which LangGraph tests often are.

**Optional.** In an Inspect AI eval ([tools.md](tools.md) section 3), `Task(...,
epochs=Epochs(3, "at_least_2"))`: the `at_least_k` reducer scores a sample correct when at least k
of its epochs score 1.0 or more, so partial credit does not count.

The repetition features of Langfuse, LangSmith (`num_repetitions`), DeepEval (`deepeval test run
-r`), Pydantic Evals (`repeat=`) and promptfoo (`--repeat`) repeat a case and report an average; none
of them has a per-case "k of n" rule.

## 6. pass@k and pass^k for agents

pass@k is the chance that at least one of k runs succeeds; pass^k is the chance that all k succeed.
A user who asks an agent to do a task once meets pass^k, not pass@k: on τ-bench's retail tasks one
model's pass^8 was about 25%, and the reliability metric the same authors defined falls as k grows
while pass@k rises. Anthropic's guide to agent evals uses pass^k where consistency matters.

**Should.** For an agent that acts for a user, report pass^k for its critical flows on the schedule
of [evals.md](evals.md) section 8 or before a release, not on every pull request. Measuring a
scenario's reliability takes many runs: one study needed about 100 runs per scenario to see a
10-point change, and the agreement between runs settled only after 8 to 16 of them.

## 7. How many cases, how many runs

**Must.** Do not claim a difference the set cannot show. On a set of 100 cases with a pass rate
near 80%, the standard error is about 4 points, so a 3-point change is noise.

What the evidence says:

- About 1,000 questions are needed to see a 3-point difference with the usual statistical power
  (Miller, 2024); 50 to 100 cases show only large shifts; below a few hundred cases the usual error
  bars are too narrow (Bowyer et al., 2025).
- **Pair the comparison.** Old and new on the same cases, case by case: to see a 5-point drop at a
  pass rate near 80%, a paired test (McNemar's) needs about 314 cases when the two versions disagree
  on 10% of them, and about 627 at 20%; comparing two separate rates needs about 1,000 per side.
- **For a fixed budget, more cases beat more runs per case.** In one study, 100 tasks with 4 runs
  each gave a 68% smaller standard error than 10 tasks with 40 runs. Start with 2 or 3 runs per
  case, see how much a case's result moves, and add runs only while the result keeps moving; beyond
  3 to 5 runs the gain is small unless single cases are the subject.

## 8. An error is not an answer

A timeout, a rate limit or a server error is a failure of the provider, not a flake of the answer:
the vendors' SDKs already retry these twice by default. Which failures are errors of the run and
which are failed cases is [evals.md](evals.md) section 6's rule. Where a pytest rerun is allowed,
and what it lets through, is [running-tests.md](../testing/running-tests.md) sections 9 and 10's.

## 9. Sources

- Anthropic, API glossary and Messages API reference (temperature), read 2026-09; OpenAI cookbook,
  "Reproducible outputs with the seed parameter".
- Thinking Machines, "Defeating nondeterminism in LLM inference", 2025-09-10.
- "Judge scores at temperature 0", arXiv:2603.04417, 2026.
- Local runs of flaky 3.8.1, pytest-rerunfailures 16.7, pytest 9.1.1 and pytest-xdist 3.8.0,
  2026-09-30; box/flaky README, source and issues #166, #192, #198, #211.
- Inspect AI, `inspect_ai/scorer/_reducer/reducer.py` and the options docs, version 0.3.273.
- Yao et al., "τ-bench", arXiv:2406.12045, 2024 (origin of pass^k); Anthropic, "Demystifying evals
  for AI agents", 2026-01-09.
- AgentAssay, arXiv:2603.02601, 2026; "Budget allocation for agent evaluation", arXiv:2512.06710,
  2025; "Run-to-run variance on SWE-bench", arXiv:2602.07150, 2026.
- Evan Miller, "Adding error bars to evals", arXiv:2411.00640, 2024; Bowyer et al., arXiv:2503.01747,
  2025.
- OpenAI and Anthropic Python SDK READMEs and source: default retries on 408, 409, 429 and 5xx.
