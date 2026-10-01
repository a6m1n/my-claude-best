# After release: monitoring, review and security testing

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. Trace every run](#2-trace-every-run)
- [3. A person reads a sample every week](#3-a-person-reads-a-sample-every-week)
- [4. Signals from users](#4-signals-from-users)
- [5. Checks on live traffic](#5-checks-on-live-traffic)
- [6. The model underneath](#6-the-model-underneath)
- [7. Security: the design is the control](#7-security-the-design-is-the-control)
- [8. Guardrails and evals](#8-guardrails-and-evals)
- [9. Where it stops holding](#9-where-it-stops-holding)
- [10. Review checklist](#10-review-checklist)
- [11. Sources](#11-sources)

## 1. Purpose and the one rule

This file is for whoever runs an LLM application after its release: what to watch, who reads what,
and how security is tested. Its levels are those of [evals.md](evals.md) section 1.

The one rule: **after release, a person reads a sample of real sessions every week, and every
failure found becomes a case in the eval; automated scores choose what to read first, they never
replace the reading.**

## 2. Trace every run

**Must.** Every production run of a model call or an agent is traced in the trace store, with the
model's version, the prompt's version and the user's session. What goes into a trace, and what never
goes into a log, is [logging.md](../logging/logging.md) section 8's, which also wires Langfuse into
LangChain and LangGraph. Without traces there is nothing to read and nothing to turn into cases.

## 3. A person reads a sample every week

**Must.** Each week, a person reads a fixed number of production traces: some at random and some
chosen by the signals of sections 4 and 5. They note the first failure in each, as in
[evals.md](evals.md) section 3. In Langfuse, an annotation queue holds the traces to read and records
each verdict as a score.

**Must.** Every failure found becomes a case in the case set, with the fix
([evals.md](evals.md) section 4).

Why: in a production ordering agent, the built-in judge caught about 18% of the defect patterns that
people found by reading the conversations, and none in one batch. Eugene Yan samples and annotates
production data because automated evaluators do not remove the need for a person; Husain and
Shankar run cheap checks on every trace and read a sample.

## 4. Signals from users

**Should.** Record what users tell you, and use it to choose which traces a person reads, not as a
quality score:

- **Explicit feedback**, such as a thumbs up or down, is rare and skewed: in one study of a coding
  assistant it covered 0.6% of turns and 2% of conversations. Who clicks, and on what, differs from
  product to product, so measure your own split before you read the rate. A satisfied user is not a
  solved task either: across 25 agents, satisfaction did not correlate with verified task success,
  and 57.5% of the conversations users were satisfied with had failed the task.
- **What users do**: asking the same question again in other words, asking for a person, leaving
  mid-task, editing a draft before sending it. These are more frequent than clicks and need reading
  to interpret.

In Langfuse, feedback is a score on the trace: from the browser with the SDK's `score` call and an
id that stops a double click from counting twice, or from the backend with
`create_score(trace_id=..., name=..., value=...)`. Filter the traces by a low score and add them to a
dataset or an annotation queue; the traces where a judge and the user disagree are the first to read.

**Optional, when the agent pauses for a person's approval** ([agents.md](agents.md) section 5).
Record each decision as a score on the trace: approve, edit, reject or respond, the decisions
LangChain's `HumanInTheLoopMiddleware` takes. Edits and rejections choose traces to read, like a low
user score. Read an approval rate near 100% as a question about the checkpoint's design, never as
proof that it can go: people approve without reading. Anthropic reports that users approve 93% of
Claude Code's permission prompts, and in its own test people refused a dangerous command placed
into a real prompt only 13.6% of the time. Both numbers come from one vendor and from a coding
agent, where a permission prompt is not a business approval step. OpenAI also tracks approval and
rejection rates for Codex, and names no threshold that acts on them.

## 5. Checks on live traffic

**Should.** Run the cheap code checks of your eval on live traces: the answer's shape, the tool-call
rules of [agents.md](agents.md) section 3, the share of tool calls that returned an error, the share
of retrievals that found nothing ([rag.md](rag.md) section 2), the refusal rate, the cost and the
latency of a run. They are free, fast and have no false alarms of their own. A rise in tool errors
points at a tool that broke or at a model that now calls it wrong.

**Should.** Run an LLM judge on a sample of live traces only when it is validated and pinned
([judges.md](judges.md) sections 4 and 6), and read its score as a trend over days, never as an alert
on one trace. In one production system with 21 judges, 0.6% of the failures they flagged at first
were real; unanimous panels and softer rubrics raised that to 48.9%. A vendor's model update dropped
one judge's pass rate from 97% to 11% in a day.

For an agent whose end state cannot be checked on live traffic, a judge of whether the task was done
sees the tool calls and their results, not only the final answer, and it picks traces to read; it
never counts a task as done ([agents.md](agents.md) section 1). On injected faults, a judge that saw
the trajectory caught 77% of the silent ones with no false alarms, against 45% with 33% false alarms
for one that saw only the outcome.

**Must.** Alert when an online evaluator stops writing scores: a check that silently stops running
looks like a system with no failures. Langfuse raises alerts on a score, on cost and on latency
(monitors, since June 2026), and it has had bugs where an evaluator never triggered on live data.

Langfuse bills each trace, observation and score as a unit, so a judge on every trace with several
criteria adds up; its guide puts a judged assessment at 1 to 10 cents.

## 6. The model underneath

**Must.** Call a dated model version, not a moving alias, and record it in every trace. When the
vendor ships a new version, or an alias you rely on moves, run the eval before you switch
([evals.md](evals.md) section 7). One alias pointed to ten model builds over 19 months, and
Anthropic's own evals missed a degradation that ran for weeks with no change of model id.

When an online judge runs (section 5), its fixed set of labelled outputs, re-scored on a schedule,
follows [judges.md](judges.md) section 6.

## 7. Security: the design is the control

**Must.** Design so that no session combines all three of Meta's "Agents Rule of Two": the agent
"can process untrustworthy inputs", "can have access to sensitive systems or private data", and "can
change state or communicate externally". Meta: agents "must satisfy no more than two of the
following three properties within a session to avoid the highest impact consequences of prompt
injection". When a session needs all three, a person approves each action that changes state or
leaves the system. In LangGraph that is `HumanInTheLoopMiddleware` on those tools, and a unit test
shows the pause ([agents.md](agents.md) section 5).

Why: tests cannot make an injection defence safe. Twelve published defences held at 0 to 2% attack
success against fixed attacks, and most of them let through over 90% of adaptive ones; people
red-teaming them broke all twelve. Simon Willison: in web security a filter that stops 95% of attacks is a failing grade.
The design patterns of Beurer-Kellner et al. (2025), such as plan-then-execute and a quarantined
model that reads untrusted text with no tools, each state a property a test can check.

**Should.** Keep a set of injection cases as a regression floor, run with the eval:

- planted instructions in each place outside text enters: a user message, a tool result
  ([agents.md](agents.md) section 7), a retrieved document ([rag.md](rag.md)), with hidden carriers
  (invisible text, markup attributes) and Unicode or emoji variants, which bypassed several
  guardrails completely;
- graded by code: no forbidden call, the run's marker string nowhere in the output or the tool
  arguments; a judge only where code cannot decide;
- each with a clean twin that must still succeed.

A green run shows that known attacks fail. It does not show that the system is safe, and fixed
attack cases go stale as models change.

**Optional.** A red-team scanner on a schedule, such as promptfoo's red team (with its `owasp:llm`
and `owasp:agentic` presets), NVIDIA's garak, Microsoft's PyRIT or Confident AI's DeepTeam. Read
their results as a floor: in one comparison against an agent with six planted weaknesses they found
14 to 56% of them (run by a competing tool's authors), and one scan's attack success moved by up to
54 points with the grader's temperature, so repeat a scan before you trust it. promptfoo's RAG
poisoning plugin sends your documents to its remote service; for a private corpus keep it off
(`PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION=true`).

Map the cases to OWASP's lists so gaps show: the Top 10 for LLM Applications 2026 (LLM01 is prompt
injection; excessive agency is LLM03) and the Top 10 for Agentic Applications 2026 (ASI01 is agent
goal hijack, ASI02 tool misuse and exploitation).

## 8. Guardrails and evals

A guardrail runs inside the request and blocks or changes it: LangChain's `PIIMiddleware` redacts
personal data, `HumanInTheLoopMiddleware` waits for a person. An eval runs after, on traces, and
measures. Langfuse records what a guardrail did; it does not block anything itself.

**Should.** Before you switch a model-based guardrail on, measure it on your own traffic: how many
attacks it stops, how many good requests it blocks, and the time it adds. In one tutoring system,
NeMo Guardrails stopped every attack and blocked 16.2% of students' normal questions, adding 1.4
seconds; injection detectors that scored 0.98 on their own data blocked 22 to 42% of harmless
prompts from elsewhere. A rule-based guardrail is tested like any code
([python/testing/](../testing/README.md)).

## 9. Where it stops holding

- **An internal tool with a handful of users**: section 3's weekly reading can be every session,
  and section 5's online judges are not worth their cost.
- **A system that sees no untrusted input and changes nothing** outside itself: section 7's design
  rule holds trivially; its injection cases can wait until either changes.

## 10. Review checklist

| Section | Level | Ask |
|---|---|---|
| 2 | Must | Is every production run traced with the model and prompt versions? |
| 3 | Must | Does a person read a sample every week, and do the failures become cases? |
| 4 | Should, approvals Optional | Do feedback and user actions choose what gets read? Are approval decisions recorded, and is a near-100% approval rate read as a design question? |
| 5 | Must, judges Should | Do code checks run on live traces, is an online judge validated and read as a trend, and does an evaluator that stops scoring raise an alert? |
| 6 | Must | Is the model a dated version, and does a new version run the eval first? |
| 7 | Must, tests Should | Does no session combine untrusted input, sensitive access and outside effects without a person's approval? Is there an injection regression set? |
| 8 | Should | Were a guardrail's blocked good requests and its delay measured before it went on? |

## 11. Sources

- Production judges: MagicSchool, arXiv:2609.28478, 2026; a production ordering agent,
  arXiv:2606.10315, 2026; "Who drifted", arXiv:2606.15474, 2026; a vendor alias over 19 months,
  arXiv:2608.11803, 2026; Anthropic, "A postmortem of three recent issues", 2025-09-17.
- Eugene Yan, "An LLM eval process", 2025-04; Hamel Husain and Shreya Shankar, evals FAQ, "How often
  should I run my evals".
- User feedback: Nam et al., arXiv:2509.18361, 2025; Langfuse docs, "User feedback", "Alerts",
  changelog "Monitors" (2026-06-19) and "Boolean scores in monitors" (2026-07-21); Langfuse guide,
  "From user feedback to evaluation datasets", 2026-09; Langfuse blog, "Evals", 2025-11-12 (updated
  2026-07); Langfuse pricing, read 2026-09-30; langfuse issues #12958, #15681.
- Satisfaction and completion judges: GAUGE, arXiv:2609.12191, 2026; trajectory vs outcome judges on
  injected faults, arXiv:2609.00038, 2026.
- Live agent checks: Langfuse, "AI agent evaluation"
  (langfuse.com/resources/engineering/ai-agent-evaluation, read 2026-09-30), tool error rate;
  Microsoft Foundry, "Agent evaluators", 2026-09-25, Tool Call Success.
- Approval decisions: LangChain docs, "Human in the loop" (read 2026-09-30); Anthropic, "Claude Code
  auto mode", 2026-03-25 (93% of permission prompts approved); Simon Willison, "Auto mode",
  2026-08-08, on Anthropic's test (13.6%); OpenAI, "Auto-review" for Codex, 2026-04-30.
- Meta, "Practical AI agent security" (Agents Rule of Two), 2025-10-31; Beurer-Kellner et al.,
  "Design patterns for securing LLM agents against prompt injections", arXiv:2506.08837, 2025;
  Simon Willison, "The lethal trifecta", 2025-06-16, and "New prompt injection papers", 2025-11-02;
  Nasr et al., "The attacker moves second", arXiv:2510.09023, 2025.
- Hidden-in-Plain-Text, arXiv:2601.10923, 2026; emoji and Unicode smuggling, arXiv:2504.11168,
  2025; red-team tool comparison (github.com/rbrus/agent-redteam-benchmark, 2026-09); attack success
  and grader temperature, arXiv:2605.14418, 2026.
- promptfoo docs: red team configuration, plugins `indirect-prompt-injection` and `rag-poisoning`;
  garak, PyRIT and DeepTeam docs, read 2026-09.
- OWASP GenAI Security Project: Top 10 for LLM Applications 2026 (released 2026-08-03; item names
  read in vendor copies of the list) and Top 10 for Agentic Applications 2026 (released 2025-12-09).
- LangChain docs, "Guardrails"; NeMo Guardrails on a tutoring system, arXiv:2605.06669, 2026;
  PIDS-Bench, arXiv:2609.15017, 2026; "When benchmarks lie", arXiv:2602.14161, 2026.
