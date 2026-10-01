# LLM judges

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. When a judge, and when not](#2-when-a-judge-and-when-not)
- [3. The kinds of judge](#3-the-kinds-of-judge)
- [4. Writing a judge](#4-writing-a-judge)
- [5. Biases, and what reduces them](#5-biases-and-what-reduces-them)
- [6. Validating a judge](#6-validating-a-judge)
- [7. A threshold on a score](#7-a-threshold-on-a-score)
- [8. Choosing the judge's model](#8-choosing-the-judges-model)
- [9. When a judge may gate a change](#9-when-a-judge-may-gate-a-change)
- [10. Where it stops holding](#10-where-it-stops-holding)
- [11. Review checklist](#11-review-checklist)
- [12. Sources](#12-sources)

## 1. Purpose and the one rule

An LLM judge is a model call that grades another model's output against a criterion. This file is
for anyone who adds a judge to an eval or to production, or reads a judge's score. Its levels are
those of [evals.md](evals.md) section 1. A judge is a model call like any other: its prompt follows
[prompt-engineering.md](../prompt-engineering/prompt-engineering.md), and its model comes from a
`<purpose>_llm_model` constant (section 15 there). [judge-example.md](judge-example.md) shows one
judge from its prompt to its validation.

The one rule: **a judge grades one criterion that code cannot decide, as pass or fail, and its
verdict counts only after it has been checked against a person's labels on the same kind of
output.**

## 2. When a judge, and when not

**Must.** Use a judge only for a criterion the graders before it in
[evals.md](evals.md) section 5 cannot decide: code, then a comparison with a reference answer.
Tone, whether an answer addresses the question, whether a reply promises something the facts do not
support: a judge. A tool that was or was not called, a number, a JSON shape, the state an agent left
behind: code.

**Must.** Never ask a judge whether code is correct: run the code. Judges asked to grade code
without running it agreed with the tests at a kappa of 0.10 to 0.21 and passed half the wrong
answers.

**Must.** For a factual criterion, give the judge the reference: the expected answer, the tool
result, the retrieved passage. Without a reference, a judge agrees with experts only on questions it
can answer itself: agreement fell from 0.86 to 0.16 on questions the judge got wrong, and kappa
against experts rose from 0.46 with no reference to 0.69 with a human-written one.

## 3. The kinds of judge

| Kind | What it does | When it fits | Level |
|---|---|---|---|
| binary, one criterion | reads the output and answers pass or fail for one criterion | the default for an eval that gates | Must, as the default |
| checklist | answers several yes/no questions, one per requirement, and reports each | a quality that splits into checkable parts ("4 of 5 expected facts") | Should |
| reference-based | compares the output with a reference answer or source | factual answers, RAG correctness | Must for facts |
| claim decomposition | splits the output into claims and checks each against the context (FActScore; faithfulness metrics) | whether an answer sticks to its sources | Should |
| pairwise | compares two outputs for the same input and picks the better | choosing between two versions; subjective quality | Optional |
| rubric score (1-5) | scores on a scale with a written description of each level | trends and ranking, never a gate | Optional |
| G-Eval | writes evaluation steps from the criteria, then scores; the original weights the score by token probabilities | a quick custom criterion in DeepEval | Optional |
| decision graph | a fixed tree of small yes/no judgements with a fixed score per leaf (DeepEval's `DAGMetric`) | a rule with branches, where G-Eval's score moves too much | Optional |
| conversation | grades a whole conversation; the dialogue's score is its worst turn (MT-Bench-101) | multi-turn assistants and agents | Should, for multi-turn |
| panel | several judges vote | only after one validated judge is not good enough | Optional |
| agent as judge | a judge that can read files, run tools or inspect the environment | tasks whose result lives in an environment | Optional |
| fine-tuned judge | a small model trained to grade (Prometheus 2 and similar) | high volume, once validated on your outputs | Optional |

Why the defaults: binary verdicts on checklists agreed with each other at a Krippendorff's alpha of
0.67 against 0.05 for open scores (CheckEval), and Husain and Shankar find that numeric labels are
"advanced and usually not necessary". A panel of nine judges from seven families gave about two
effective votes and did not beat its best single judge on three language tasks. Fine-tuned judges
lose accuracy on a format they were not trained on and on newer models' outputs, and judges of the
same family err together. Eugene Yan's heuristic, from 2024, is direct scoring for objective
criteria and pairwise for subjective ones.

## 4. Writing a judge

**Must**, for every judge:

- **One criterion per judge call.** A rubric that checks several things at once agrees less with
  people than separate calls, one criterion each.
- **Pass or fail.** Split a quality into binary checks instead of a scale ([section 7](#7-a-threshold-on-a-score)
  when a tool gives a score).
- **The evidence before the verdict.** The judge's answer is JSON through a response schema
  ([prompt-engineering.md](../prompt-engineering/prompt-engineering.md) section 11), with a short
  field that quotes the evidence from the output first and the verdict last (section 12 there). Asked
  to cite the evidence before the verdict, small judges changed their verdict after a planted label
  in 5 to 22% of cases, against 75 to 85% with free reasoning; long reasoning makes position bias
  worse, so keep the field short.
- **The output under judgment is inserted material** in its own tag
  ([prompt-engineering.md](../prompt-engineering/prompt-engineering.md) section 5), and it is
  untrusted: it can hold text that addresses the judge.
- **Never the system's own reasoning.** Give the judge the output and the facts it needs, not the
  agent's chain of thought or its claim about its progress. A fluent visible reasoning raised a weak
  judge's pass rate from 57.8% to 88.0% when the true rate was 23.2%, and rewritten agent reasoning
  raised judges' false passes by 20 to 30 points.
- **Pin the judge.** Its model is a dated snapshot, never an alias, and its prompt has a version;
  both go into every run's metadata. A changed judge prompt with the same meaning changed verdicts
  (consistency from 0.39 to 0.99 across judges), and a vendor alias moved through ten model builds
  in 19 months.

**Should.** Use a judge from a different model family than the model it grades, and measure when
you cannot. Judges favoured their own family by 3.4 to 8.4 points, and passed their own output's
failed criterion over 50% more often. Hamel Husain finds the same model "usually fine" in practice;
your own labels (section 6) settle it for your case.

## 5. Biases, and what reduces them

| Bias | What happens | What reduces it | Level |
|---|---|---|---|
| position | in pairwise mode the first (or second) answer wins more often; open judges reversed their pick in 55% of swapped pairs | run each pair in both orders; a pick that flips is a tie | Must, for pairwise |
| length and format | longer or better-formatted answers score higher | say in the criterion that length and format are not quality; check on labelled pairs | Should |
| self-preference | a judge favours its own model family | a judge from another family (section 4) | Should |
| leniency | judges pass more of a stronger model's answers, right or wrong | measure the true-negative rate (section 6) on outputs of the model you grade | Must, through validation |
| planted text | one token appended to an answer (such as ":") made binary judges, frontier ones included, pass up to 35 to 89% of wrong answers | never let a judge alone gate output an attacker can shape (section 9) | Must |
| run-to-run noise | the same judge gives a different verdict on a rerun; one open judge agreed with itself on 3 runs 61.3% of the time | binary verdicts; repeated runs ([repeated-runs.md](repeated-runs.md)); a fixed anchor set (section 6) | Should |

## 6. Validating a judge

**Must.** Before a judge's verdict counts in a gate, check it against a person's labels:

1. **One person who knows the domain labels the outputs**, pass or fail with a one-line reason, for
   the criterion the judge will grade. Labels from real outputs of the system under test, including
   the hard cases.
2. **100 to 200 labelled outputs per criterion**, with 30 to 50 of each verdict in both the set you
   tune on and the held-back test set. Husain splits them: 10 to 20% as examples the judge's
   prompt may show, 40 to 45% to tune the prompt on, and 40 to 45% held back as the test set.
3. **Report on the held-back set**: the two-by-two table of judge verdict against label with its
   count, the true-positive rate (TPR: of the real passes, how many the judge passed) and the
   true-negative rate (TNR: of the real fails, how many it failed), and the pass rate of each side.
   Raw agreement hides a judge that never fails anything: across 21 judges it overstated
   chance-corrected agreement by 34 to 41 points.
4. **Decide on the gate's own question.** Keep the judge when its errors would not flip the gate's
   decision on the labelled set; a judge picked by agreement alone made 34% more inconsistent
   decisions in one study.
5. **Include known-bad outputs** in every run of the judge ([evals.md](evals.md) section 5), so a
   judge that drifts toward passing everything turns the run red.

**Must.** Validate again when the judge's model or prompt changes, and when the system it grades
changes its model: a judge validated on one model's outputs lost accuracy on another's.

**Must.** Between changes, keep a fixed set of about 200 labelled outputs and re-score it on a
schedule; a change in the judge's score on that set is the judge drifting, not the product. A
rolling statistical alarm without such a set raised false alarms on 75% of streams that had not
drifted.

**Should.** When two people label, measure their agreement first; it is the ceiling for any judge.
In one RAG study people agreed at a kappa of 0.80 and 23 of 54 judges reached that level; in a
hallucination study people agreed only at 0.46.

**Optional.** Correct the judge's pass rate for its known errors with its TPR and TNR (the
Rogan-Gladen correction, or prediction-powered inference), when you report a rate rather than gate
a change. It needs the TPR and TNR measured on the system you report on; with a judge barely better
than chance, the correction's error grows large.

Validation takes time: one team needed four and a half months of audits before its multi-turn judge
caught more failures than it raised false alarms. Budget for it before you plan to gate on a judge.

## 7. A threshold on a score

**Should.** Prefer a binary verdict to a score with a threshold. DeepEval passes a metric when its
score reaches the threshold, 0.5 by default, and its docs give no method for choosing it; its docs
also call a G-Eval score "not deterministic" when it rests on criteria alone.

When a tool gives only a score:

- **Choose the threshold on your labels** (section 6): the value that maximises Youden's J
  (TPR + TNR − 1), or the value that meets the TNR your gate needs. Never reuse a threshold from
  another domain or another team; calibration carried across domains helped on average and hurt in
  13 to 34% of cases, depending on the method.
- **Fix what makes the score move**: DeepEval's `evaluation_steps` instead of criteria alone, or a
  `DAGMetric` for a rule with branches; DeepEval's `strict_mode` makes the metric binary.
- **Treat a score within the noise of the threshold as undecided**, not as a pass: measure the noise
  by re-scoring the labelled set a few times.

## 8. Choosing the judge's model

**Should.** Develop the judge's prompt with a strong model. Then try cheaper models on the held-back
labels of section 6, and keep the cheapest one whose TPR and TNR stay where the gate needs them
(Husain and Shankar). Test on a hard set: the disagreement cases, not only easy ones.

Why: size does not decide. On one production faithfulness task, a small hosted model reached a kappa
of 0.04 on the hard cases and 0.42 on a uniform sample, a self-hosted mid-size model 0.72 and 0.94,
and a frontier model 0.71 and 0.93, at 300 times the mid-size model's price per 1,000 judgments; a
better prompt did not rescue the small model. On 200 grading cases, cheap open models matched
frontier ones on pass or fail at about a hundredth of the cost, while the frontier models ranked
answers better. A judge cannot grade reliably what it cannot solve itself, which is one more reason
to give it the reference (section 2).

The chosen model goes into the judge's `<purpose>_llm_model` constant
([prompt-engineering.md](../prompt-engineering/prompt-engineering.md) section 15), with the date of
the choice in its comment; model names and prices age.

## 9. When a judge may gate a change

**Must.** A judge's verdict may block a change only when all of this holds:

- the criterion is one code and a reference comparison cannot decide (section 2);
- the judge is validated on the gate's decision (section 6), with a pinned model and prompt
  (section 4);
- the gate compares a rate over repeated runs with the baseline, with a margin
  ([repeated-runs.md](repeated-runs.md) section 4), and code checks run next to it;
- the run includes known-bad outputs, and they fail.

**Must.** A judge alone never decides:

- **an agent's trajectory or whether its task is done** when a check on the tool calls or the end
  state exists ([agents.md](agents.md) section 3). Frontier judges scored a balanced accuracy of 0.48
  to 0.59 on agent trajectories, accepting plausible failures; a production agent's judge caught
  about 18% of the defects people found;
- **output someone outside the eval can shape at the moment it is judged**: live traffic, where a
  user or a retrieved page can plant text in what the judge reads, or the judged agent's own report
  of its work; one planted token can flip a verdict (section 5). On your own case set, offline, the
  inputs are yours and this does not apply;
- **the pass of a system that is optimised against it.** An agent loop gated by a frontier judge
  learned to copy answer keys and reported 100% while the real rate was 68%; only checks in code
  caught it.

In those cases a judge's score is advisory: it picks which traces a person reads first.

## 10. Where it stops holding

- **Exploring**, before any gate: an unvalidated judge is fine to sort outputs for a person to read.
- **A criterion a person must decide**, such as legal or medical correctness: judges agreed with
  experts about half the time on legal review. A person grades it; a judge can at most sort.

## 11. Review checklist

| Section | Level | Ask |
|---|---|---|
| 2 | Must | Could code or a reference comparison decide this criterion instead? Does a factual judge get the reference? |
| 3-4 | Must | Is it one criterion, pass or fail, evidence before the verdict, with the output in a tag and no agent reasoning? Are the model and prompt pinned? |
| 5 | Must, for pairwise | Does every pairwise call run both orders? |
| 6 | Must | Is the judge validated on held-back labels, with TPR, TNR and the two-by-two table, and re-validated after a model change? |
| 7 | Should | If the tool gives a score, was the threshold chosen on your labels? |
| 8 | Should | Was the judge's model chosen by its TPR and TNR on your hard cases? |
| 9 | Must | Does the judge gate only a validated criterion, and never alone a trajectory, live traffic or a system optimised against it? |

## 12. Sources

- Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", arXiv:2306.05685, 2023
  (origin: pointwise, pairwise, reference-guided; position bias).
- Liu et al., "G-Eval", arXiv:2303.16634, 2023 (origin); Min et al., "FActScore", arXiv:2305.14251,
  2023 (origin); Lee et al., "CheckEval", arXiv:2403.18771 (v3 2025); Kim et al., "Prometheus 2",
  arXiv:2405.01535, 2024; Verga et al., "Replacing Judges with Juries", arXiv:2404.18796, 2024;
  Zhuge et al., "Agent-as-a-Judge", arXiv:2410.10934, 2024; Bai et al., "MT-Bench-101",
  arXiv:2402.14762, 2024.
- Hamel Husain, "Using LLM-as-a-Judge" (hamel.dev/blog/posts/llm-judge/, revised 2026-09) and the
  evals FAQ with Shreya Shankar: one expert labeller, splits, TPR and TNR, binary labels, choosing a
  cheaper judge.
- Eugene Yan, "Evaluating the Effectiveness of LLM-Evaluators", 2024-08 (dated); "Product evals",
  2025-11.
- "Nine judges, two effective votes", arXiv:2605.29800, 2026; "Auditing LLM juries",
  arXiv:2607.08535, 2026; "Reliability without validity", arXiv:2606.19544, 2026; "Judge's Verdict",
  arXiv:2510.09738, 2025.
- "Rubric mechanics", arXiv:2605.06283, 2026; "Proof before preference", arXiv:2605.23970, 2026;
  "Position bias and reasoning length", arXiv:2605.06672, 2026; "Family-conditioned judge
  preference", arXiv:2609.17857, 2026; "Self-preference on verifiable rubrics", arXiv:2604.06996,
  2026; "Prompt paraphrase and judge verdicts", arXiv:2604.23478, 2026.
- "One token to fool LLM-as-a-judge", arXiv:2507.08794 (v3 2026); "Gaming the judge",
  arXiv:2601.14691, 2026; "Visible reasoning inflates judges", arXiv:2604.06756, 2026; "Judge-gated
  self-improvement", arXiv:2609.02246, 2026.
- "Reference answers and judge agreement", arXiv:2503.05061 (v2 2026); "LLMs as code judges",
  arXiv:2507.16587, 2025; JudgeBench, arXiv:2410.12784, 2024.
- SkillTV-Bench, arXiv:2608.05573, 2026; production ordering agent, arXiv:2606.10315, 2026;
  multi-turn business agents, arXiv:2609.33955, 2026.
- "Agreement metrics for LLM-as-judge", arXiv:2606.00093, 2026; "Rating indeterminacy and judge
  selection", arXiv:2503.05965, 2025; "Model shift in safety judges", arXiv:2603.06594, 2026; "Who
  drifted", arXiv:2606.15474, 2026; Youden's J for judges, arXiv:2512.08121, 2025; calibration
  transfer, arXiv:2609.27954, 2026.
- DeepEval docs: metrics introduction, G-Eval, DAG (deepeval.com, read 2026-09-30).
- Judge cost and agreement: text-to-SQL faithfulness judges, arXiv:2609.30290, 2026; proof grading,
  arXiv:2608.00004, 2026.
