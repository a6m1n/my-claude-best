# Evals: testing LLM applications

How to check what a language model does in an application — a single call, a RAG pipeline or an
agent: with real model calls on cases from real use, graded by code first and by a validated judge
where code cannot decide, repeated because the answers vary, compared with the version before, and
watched after release.

**Navigation**

- [The one rule](#the-one-rule)
- [Levels](#levels)
- [What to know first](#what-to-know-first)
- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)

## The one rule

**Behaviour that comes from a model is checked by running the model on cases taken from real use,
graded by code wherever code can decide, and a change ships only after it is compared with the
version before on the same cases.** A unit test with a stand-in for the model checks the code
around it and nothing the model decides. Each file below holds one part of that rule for one kind of
work.

## Levels

Every rule opens with its level, defined in [evals.md](evals.md) section 1:

- **Must**: what every application that calls a model needs, when the rule's condition holds.
- **Should**: what pays in most applications; the rule says when to start it and what shows it pays.
- **Optional**: add it when the need the rule names appears.

The terms of the next section are what a reader needs to know before the rules.

## What to know first

- **Eval**: a scored run of the system over a set of cases, reported as a pass rate per criterion and
  compared with a baseline. A test answers pass or fail for one case; an eval answers "how often, and
  is it worse than before".
- **Case set**: the inputs an eval runs, each with its pass criterion, kept in git.
- **Grader**: what decides whether one case passed one criterion: code, a comparison with a reference
  answer, an LLM judge, or a person.
- **LLM judge**: a model call that grades another model's output ([judges.md](judges.md)).
- **Trace**: the record of one run: every model call, tool call and result, kept in a trace store
  such as Langfuse.
- **Offline and online**: an offline eval runs on the case set before a change ships; an online check
  runs on live traffic after it ships.
- **k of n**: a case passes when at least k of its n runs pass. **pass@k**: the chance that at least
  one of k runs succeeds. **pass^k**: the chance that all k succeed; for an agent that acts for a
  user, this is what the user meets ([repeated-runs.md](repeated-runs.md)).
- **Error analysis**: reading real outputs, noting the first failure in each, and grouping the notes
  into failure modes; the source of every criterion ([evals.md](evals.md) section 3).

## What is here

- [evals.md](evals.md): the method: why unit tests are not enough, reading real outputs, the case
  set, graders from cheapest to dearest, counting every case, comparing versions, when evals run and
  what they cost. Read it first, and before you change a prompt, a model, the retrieval or an
  agent's graph.
- [repeated-runs.md](repeated-runs.md): why answers vary, pass rules over repeated runs, "it may be
  wrong one time in three", pass@k and pass^k, how many cases and runs a comparison needs. Read it
  when a check on a model's answer is flaky, or before you choose how many runs must pass.
- [judges.md](judges.md): the kinds of LLM judge, writing one, its biases, validating it against
  people's labels, choosing its threshold and its model, and when it may gate. Read it before you add
  a judge or read a judge's score.
- [agents.md](agents.md): what to test in an agent, checks on tool calls, unit tests of a LangGraph
  agent, clean environments, graders an agent cannot game, injection through tool results, evals in
  Langfuse and LangSmith. Read it when you build or change an agent.
- [rag.md](rag.md): retrieval measured apart, the answer against a reference, citations, questions
  the documents cannot answer, the test set, library metrics that share a name. Read it when you
  build or change a RAG pipeline.
- [production.md](production.md): traces, weekly reading, user signals, checks on live traffic, the
  model underneath, security by design with injection tests as a floor, guardrails. Read it before a
  release and when you set up monitoring.
- [tools.md](tools.md): Langfuse or LangSmith, the eval libraries with when to add each and what to
  watch for, DeepEval in pytest, what stays out, and the settings that keep data in. Read it before
  you add an eval library or platform.
- [case-set-example.md](case-set-example.md): the case set and the eval of one model call, with the
  pytest contract "right in two runs of three". Read it when you write a module's first eval.
- [judge-example.md](judge-example.md): one judge from its prompt to its validation on labelled
  outputs. Read it when you write a judge.
- [agent-eval-example.md](agent-eval-example.md): the unit tests and the eval of one LangGraph agent.
  Read it when you test an agent.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/evals/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you change a prompt, a tool definition,
   the model, the retrieval or an agent's graph, or add a check on what a model answers, read
   `docs/engineering/evals/README.md` and the file it points to." Without it an agent never opens the
   folder.
3. Create `evals/` at the repository root, as
   [file-structure.md](../file-structure/file-structure.md) section 9 places it, and start each
   module's case set from its real traces ([evals.md](evals.md) sections 3 and 4).
4. The practice links [testing/](../testing/README.md),
   [prompt-engineering.md](../prompt-engineering/prompt-engineering.md),
   [logging.md](../logging/logging.md), [file-structure.md](../file-structure/file-structure.md) and
   [git.md](../git/git.md) for the rules they own. Copy those folders too, or replace each link with
   your own rule for that topic.
5. Re-check the lines that name a moving target: the library versions and behaviours in
   [tools.md](tools.md) and the examples, the vendor facts in [production.md](production.md), and the
   OWASP lists. They were read in September 2026.

## The points to adapt

- **The platform.** The examples use Langfuse; [tools.md](tools.md) section 2 says when LangSmith fits
  better. The method does not change with the platform.
- **A LangChain app.** It keeps the same case set, graders and gate; its task hands the app's chat
  model, in place of the house client, to the app's own triage function
  ([case-set-example.md](case-set-example.md#with-langchain)).
- **The margins and the schedule.** How far a rate may fall before a gate turns red, and how often
  the whole eval runs, depend on your traffic and your budget.
- **Should rules.** Your data keeps or drops them, as [evals.md](evals.md) section 1 says.

What does not change is the one rule above: real calls on real cases, code before judges, and the
version before as the baseline.
