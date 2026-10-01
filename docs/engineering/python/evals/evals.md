# Evals: checking what a model does

**Navigation**

- [1. Purpose, levels and the one rule](#1-purpose-levels-and-the-one-rule)
- [2. Unit tests check the code, evals check the behaviour](#2-unit-tests-check-the-code-evals-check-the-behaviour)
- [3. Read real outputs before you write a check](#3-read-real-outputs-before-you-write-a-check)
- [4. The case set](#4-the-case-set)
- [5. Graders: the cheapest one that can decide](#5-graders-the-cheapest-one-that-can-decide)
- [6. Count every case](#6-count-every-case)
- [7. Compare with the version before](#7-compare-with-the-version-before)
- [8. When evals run, and what they cost](#8-when-evals-run-and-what-they-cost)
- [9. Trace every eval run](#9-trace-every-eval-run)
- [10. Where it stops holding](#10-where-it-stops-holding)
- [11. Review checklist](#11-review-checklist)
- [12. Sources](#12-sources)

## 1. Purpose, levels and the one rule

This file is for everyone who builds or changes an application that calls a language model: a
single call, a RAG pipeline or an agent. Read it before you change a prompt, a tool definition, the
model, its settings, the retrieval or an agent's graph, and before you add a check on what a model
answers.

It covers the method. The other files of this folder cover one subject each: repeated runs and
pass rules in [repeated-runs.md](repeated-runs.md), judges in [judges.md](judges.md), agents in
[agents.md](agents.md), RAG in [rag.md](rag.md), what runs after release in
[production.md](production.md), and the libraries in [tools.md](tools.md). How a pytest suite is
laid out and run is [python/testing/](../testing/README.md)'s. How a prompt is written and what changes it
triggers is [prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md)'s.

The one rule of this folder is in its [README](README.md#the-one-rule); every section below serves
it.

Every rule in this folder opens with its level:

- **Must**: when its condition holds, always. A miss is a defect a review sends back.
- **Should**: pays in most applications, not in all of them. The rule says when to start it and
  what shows that it pays; when your own data shows it does not, drop it and write the reason next
  to the eval.
- **Optional**: add it when the need the rule names appears. Before that it costs time and money
  and returns nothing.

A rule can hold parts of two levels; the part says so. The terms a reader needs before the rules,
such as case set, grader, pass@k and pass^k, are in the [README](README.md#what-to-know-first).

## 2. Unit tests check the code, evals check the behaviour

**Must.** When a change touches a prompt, a tool definition, the model or its settings, the
retrieval, or an agent's graph, check what the model now does with real model calls before the
change merges. A unit test with a stand-in for the model
([python/testing/fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 3) checks the code
around the model: the request it builds, how the answer is parsed, which tool runs, what happens on
an error. It never checks what the model decides, because the stand-in answers what the test told
it to answer.

There are two kinds of check with real calls, and they answer different questions:

| | A real-model test | An eval |
|---|---|---|
| The question | Does this case meet its contract? | How often does the system get it right over a set of cases, and did a change make it worse? |
| The result | pass or fail for one case | a pass rate per criterion, compared with a baseline |
| Where it lives | `tests/integration/<module>/`, under the `live_model` mark ([running-tests.md](../testing/running-tests.md) section 10) | `evals/<module>/` (section 4) |
| How it runs | pytest | an eval runner, such as a Langfuse experiment ([tools.md](tools.md) section 2) |

A pytest run returns pass or fail, and a rate over a hundred cases is not a pass or a fail. So a
contract for one case, such as "a crash report is filed as a bug", is a real-model test, and the
quality of the feature over the whole set is an eval.

Why: a test model "won't look pretty or relevant" (Pydantic AI's docs); it checks the wiring. In a
study of 2,572 tests in 12 agent projects, 34.4% mocked the agent or its tools and 8.7% asserted
anything about its reasoning; across 439 agent applications, prompts got about 1% of the tests. In
one production agent, a person reading real output caught about 70% of 22 incidents and the unit
tests caught none. The model's answer also changes from call to call at any temperature
([repeated-runs.md](repeated-runs.md) section 2), so one green call proves little.

## 3. Read real outputs before you write a check

**Must.** Before you write the first grader for a feature, and again when a new kind of failure
shows up, read real outputs. Read at least 30 traces, and keep reading until new traces show no new
kind of failure. For each trace, write down the first thing that went wrong. Group the notes into
failure modes. Each failure mode becomes one criterion, and each criterion gets one grader
(section 5). Before launch, when there are no users yet, use inputs written to cover the kinds you
expect, and replace them as real ones arrive.

Why: Hamel Husain and Shreya Shankar start every eval from this error analysis, and note only the
first failure in each trace, because later steps fail as a result of it. LangChain's agent
checklist (2026) spends 60 to 80% of the effort on understanding failures. Shankar et al. measured
"criteria drift": people change their idea of a good answer while they grade outputs, so criteria
written before reading outputs miss what matters. Generic ready-made metrics "measure abstract
qualities that may not matter" (Husain).

## 4. The case set

A case set is the list of inputs an eval runs, each with what counts as a pass.

**Must**, for every case set:

- **Cases come from real inputs**, with names and identifying details removed the way
  [prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 7 removes them from an
  example.
- **Each case states its pass criterion before the run**: an expected value, the tool calls that
  must and must not happen, or the criteria a grader checks. A criterion written after you saw the
  answer bends toward the answer.
- **Each case has a stable id**, so a case can be compared across runs and versions.
- **Every failure found in review or in production becomes a case** in the change that fixes it.
  Grow the set from failures you saw, not from cases you invented to pass.
- **The set holds cases where the right answer is not an answer**: the way out of
  [prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 8, a refusal, a
  question back to the user, a request for confirmation. Their results are counted apart from the
  others, as a two-by-two table: should answer or not, did answer or not. In one study a system
  scored 71.8% overall and got 19.5% of the cases right where it should have refused; in a RAG
  study, 49% of real queries could not be answered from the documents.
- **The case set lives in git** at `evals/<module>/cases_<purpose>.jsonl`, one case per line, and is
  reviewed like code. A dataset in an eval platform is a copy made for a run, not the source.

**Should.** Keep two sets: a regression set of cases the system passes today, which should stay
close to 100%, and a capability set of cases it fails today, which shows progress. Anthropic and
LangChain both split them; a regression set that falls and a capability set that rises are two
different pieces of news.

How big: 20 to 50 cases drawn from real failures is a good start (Anthropic, 2026; LangChain,
2026: "20-50 hand-reviewed examples you're confident in will outperform hundreds of synthetic
examples you haven't verified"). A claim that a change is a few points better needs hundreds of
cases ([repeated-runs.md](repeated-runs.md) section 7).

**Optional.** Generated cases, when there are no real inputs yet or to cover kinds real traffic has
not shown. A person reads each generated case before it counts, and generated cases never replace
real ones. On one university chatbot, the best retrieval setup scored a hit rate of 0.90 on
generated questions and 0.53 on real ones, and the ranking of setups flipped.

Where the files live: `evals/` sits at the repository root
([file-structure.md](../../any-language/file-structure/file-structure.md) section 9), with one folder per module,
named as the module is:

```text
evals/
├── rate_gate.py                     the gate every experiment ends with
└── <module>/
    ├── cases_<purpose>.jsonl        the case set: one JSON object per line
    ├── experiment_<purpose>.py      the run: task, graders, metadata
    ├── schemas.py                   a case, a run's output and the criteria, typed once
    ├── consts.py                    only with a judge: its model and effort
    ├── prompts.py                   only with a judge: its prompt
    ├── judge_<criterion>.py         only with a judge: the one call
    └── labels_<criterion>.jsonl     only with a judge: people's labels (judges.md section 6)
```

A grader that only evals use lives next to the experiment that uses it; a grader the application
also runs in production lives in the application. Code in `evals/` is checked like `src/` and
`tests/`: the type checker's file list names it ([python.md](../language/python.md) section 3: types
in half the code check half the code). [case-set-example.md](case-set-example.md) and
[judge-example.md](judge-example.md) show the files.

## 5. Graders: the cheapest one that can decide

**Must.** For each criterion, use the first grader in this list that can decide it:

1. **Code**: an equality, a schema, a regular expression, the set of tool calls, the state a fake
   store or a sandbox was left in.
2. **A comparison with a reference answer** written for the case.
3. **An LLM judge** ([judges.md](judges.md)).
4. **A person.**

Each grader decides one criterion, and its verdict is pass or fail. Several criteria mean several
graders, each with its own result.

Why: code is free, fast and gives the same verdict every time. Husain and Shankar use code wherever
a rule can find the failure and a judge only for what code cannot decide; OpenAI's guide to
evaluating agent skills puts deterministic checks on the trace first and a rubric second. Judges
disagree with themselves between runs and can be fooled ([judges.md](judges.md) section 5).

**Must.** Before a grader gates anything, run it on outputs you know are bad and on a system that
does nothing, such as an agent that returns an empty answer. The grader must fail them. When you
have a known-good answer, it must pass. A grader that passes everything looks exactly like a system
that works: one team found a lenient judge passed a compliant answer and a flawed one ten times out
of ten, and an audit of ten agent benchmarks found all ten could be passed without solving a task.

## 6. Count every case

**Must.** The pass rate is the number of passes divided by the number of cases times the number of
runs in the set, never by the number of results that came back. A case whose system call or grader
raised an error is reported by its id, apart from the wrong answers, and a run with such a case does
not pass its gate. An exception that carries the model's own answer (a refusal, an answer cut off or
one that does not parse, a run stopped at its step limit) is a failed case, graded like a wrong
answer; only a failure of the provider or of a grader is an error of the run. Before the run
reports a rate, it checks that it has one result per case, run and grader.

Why: eval tools drop failures quietly, and each drop makes a broken run look better. In a local run
of Langfuse's `run_experiment` (SDK 4.16.0), a case whose task raised was missing from the results,
and a pass rate averaged over the results read 1.0; an evaluator that raised left no score. Ragas
drops rows that failed from its averages (issue #3028), and several DeepEval metrics divide by the
verdicts the judge returned rather than by the items it was asked to judge (issue #3346).

## 7. Compare with the version before

**Must.** Judge a change by running the old version and the new one on the same cases, and compare
them case by case. Write the decision rule down before the run, for example: "the pass rate of each
criterion does not fall below the baseline by more than the margin, and every case that passed
before and fails now is listed in the pull request for a person to read". The gate is the rate; a
case's own pass rule is a report, not a gate ([repeated-runs.md](repeated-runs.md) section 4). Keep
each run's results, so the next change has a baseline. How many cases and runs a comparison needs is
[repeated-runs.md](repeated-runs.md) section 7; a change to a prompt or a model has its own rules in
[prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 18.

Why: an edit that fixes the case in front of you changes others you do not see, and two averages
from different sets or different days say nothing about the change. A paired comparison on the same
cases needs about a third to a half of the cases an unpaired one needs to see the same drop
([repeated-runs.md](repeated-runs.md) section 7).

## 8. When evals run, and what they cost

**Must.** Before a change to a prompt, a tool definition, the model or its settings, the retrieval
or an agent's graph merges, run its eval and put the result, with the baseline, in the pull
request's Verification section ([git.md](../../any-language/git/git.md) section 4). A person may start this run by
hand.

**Should.** Run the whole eval on the main branch on a schedule, nightly or weekly, including
repeated runs and pass^k for agents ([repeated-runs.md](repeated-runs.md) section 6). Start it when
the set has settled; it shows a change nobody made in the code. A vendor alias pointed to ten
different model builds over 19 months; one team saw a vendor model update drop a pass rate from 97%
to 11% in a day; Anthropic's own evals missed a degradation that hit up to 16% of requests.

**Must**, for any run nobody watches: the key it uses belongs to a workspace or project of its own
with a monthly spend limit (Anthropic workspaces, OpenAI projects). A loop that calls the model with
no cap is the most expensive bug in this folder.

What each run holds:

| Moment | What runs | Real model |
|---|---|---|
| every push | the unit suite, with a stand-in for the model | no |
| a pull request that changes model behaviour | the regression set, the real-model tests of the changed module, the result in the pull request | yes, started by hand or by the CI job |
| the schedule | the whole eval: every set, repeated runs, judges, pass^k for agents | yes |
| production | checks on sampled traces ([production.md](production.md)) | the production calls |

**Optional.** A vendor's batch API for the scheduled run: Anthropic's and OpenAI's cost half and
return within 24 hours.

A replayed recording of a model's answer (a cassette) checks the code that parses it, never the
model's behaviour; it is [python/testing/libraries.md](../testing/libraries.md) section 3's subject, and it
never counts as an eval.

## 9. Trace every eval run

**Must.** Every eval run records one trace per case in the trace store, and each result links to its
trace, so a failure is read, not guessed at. The run's metadata names the model and its version, the
prompt's version and, for a judge, the judge's model and prompt version. What a trace may hold and
what never goes into a log is [logging.md](../logging/logging.md) section 8's.

Why: a pass rate says that something changed; the trace says what. Reading traces is the step
section 3 asks for, and the failures a person finds there become the next cases.

## 10. Where it stops holding

- **A prompt you run once by hand**, in a notebook or a chat window, to explore. Sections 3 and 4
  still help; the rest is ceremony there.
- **Code that calls no model**, even when it sits next to one. It is tested like any other code
  ([python/testing/](../testing/README.md)).
- **An application too small for a schedule**, such as an internal tool with ten users. Sections 2
  to 7 still hold; section 8's schedule does not, and a person reads the outputs each week instead.

## 11. Review checklist

One question per rule. Ask them when you review a change that touches a prompt, a model, the
retrieval or an agent's graph, and when you review an eval.

| Section | Level | Ask |
|---|---|---|
| 2 | Must | Did the change run against the real model, and does a unit test with a stand-in claim nothing about what the model decides? |
| 3 | Must | Do the criteria come from reading real outputs? |
| 4 | Must, split Should | Do the cases come from real inputs, with a pass criterion, a stable id and cases where the right answer is not an answer, kept in git? |
| 5 | Must | Is each criterion graded by the cheapest grader that can decide it, and did each grader fail known-bad outputs? |
| 6 | Must | Is the rate divided by every case, with errors reported apart? |
| 7 | Must | Was the new version compared with the old one on the same cases, by a rule written before the run? |
| 8 | Must, schedule Should | Is the result in the pull request, and does an unattended run use a key with a spend limit? |
| 9 | Must | Does each result link to its trace, with the model and prompt versions recorded? |

## 12. Sources

- Hamel Husain and Shreya Shankar, "LLM Evals: Everything You Need to Know" (the evals FAQ),
  hamel.dev/blog/posts/evals-faq/, revised 2025-2026: error analysis first, code checks before
  judges, generic metrics.
- Shankar et al., "Who Validates the Validators?", arXiv:2404.12272, 2024: criteria drift.
- Anthropic, "Demystifying evals for AI agents", 2026-01-09: 20 to 50 tasks from real failures,
  capability and regression evals, pass@k and pass^k.
- LangChain, "Agent evaluation readiness checklist", 2026-03-27: hand-reviewed traces first, 60 to
  80% of effort on failures, code graders in CI.
- OpenAI, "Eval skills" (developers.openai.com/blog/eval-skills): deterministic trace checks first.
- Pydantic AI docs, "Testing" (pydantic.dev/docs/ai/guides/testing/): what a test model checks.
- "Testing practices in agent frameworks", arXiv:2509.19185, 2025, and arXiv:2608.08413, 2026: what
  agent projects test.
- "Silent failures in a production agent runtime", arXiv:2606.14589, 2026: who caught the incidents.
- "Calibration is the bottleneck", arXiv:2609.00949, 2026: aggregate accuracy hid refusal recall.
- Kucia and Gawlik, arXiv:2609.14579, 2026: generated vs real queries in RAG evaluation.
- BenchJack, arXiv:2605.12673, 2026: agent benchmarks passed without solving a task.
- Local run of `Langfuse.run_experiment`, SDK 4.16.0, 2026-09-30; ragas issue #3028; deepeval issue
  #3346: failures dropped from averages.
- "A vendor alias over 19 months", arXiv:2608.11803, 2026; MagicSchool production judges,
  arXiv:2609.28478, 2026; Anthropic, "A postmortem of three recent issues", 2025-09-17.
- Anthropic and OpenAI docs on workspace and project spend limits and on the batch APIs, read
  2026-09.
