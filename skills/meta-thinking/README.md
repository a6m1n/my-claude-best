# meta-thinking

A Claude Code skill that thinks a large task through before any work starts, and asks you only
what the code cannot answer.

**Navigation**

- [The problem it solves](#the-problem-it-solves)
- [What it was made for](#what-it-was-made-for)
- [When to use it](#when-to-use-it)
- [What a run does](#what-a-run-does)
- [Why it is built this way](#why-it-is-built-this-way)
- [Install](#install)
- [Files](#files)

## The problem it solves

You give an agent a large task, and it starts editing at once. The work rarely goes wrong
because the code is bad. It goes wrong because of something nobody said out loud: a
requirement that is missing, a scope edge that reads two ways, a name or a format that later
work cannot cheaply change, two approaches where the agent silently picked one. You find out
halfway through, when the fix costs a rewrite.

Research on coding agents points the same way. GPT-5 solved 25.9% of SWE-Bench Pro tasks when
it got the requirements and the interface, and 8.4% with the problem statement alone (F20). In
another study, 46.7% of runs failed mainly at clarification or planning (F21). When the agent
could ask the user about an underspecified task, it reached about 54–89% of what it scored with
the full specification (F15).

A plan step alone does not fix this. In one single-run study, larger models scored 0.4 to 2.6
points lower with planning, and a weak model 11.6 points higher (F1). So the step has to be
short, it has to skip small tasks, and its output has to be the decisions only you can make, put
in front of you before the work starts.

## What it was made for

The skill is built on one idea: before a large task, an independent agent with a fresh
context looks at everything known about it, decides what to ask you and what to look up on the
web, and proposes a route whose every step says why it is there. The research run behind it
([research-basis.md](research-basis.md)) asked what current studies and practice say about such
a step, and the answers shaped every rule.

## When to use it

Use it when the task is large and at least one signal holds. Large means the task spans several
parts, layers or deliverables, or cannot be said as one change in one sentence.

| Signal | Example |
| --- | --- |
| a. A requirement, a scope edge or what "done" means is missing or reads two ways | "Add export" — export to where, for whom, in which format? |
| b. Two or more approaches are viable and differ in something you care about | A PDF library or an HTML-to-PDF renderer, with different costs to run |
| c. A one-way door is on the path: a name, a format, a public contract, stored data, an outside side effect | A new public URL that scripts and bookmarks will depend on |
| d. The area is new to the project, with no pattern to follow | The first background job in an app that has none |
| e. The result cannot be checked quickly: no tests, slow or no feedback | A change whose effect shows only in next month's report |

Use something else when:

| The task is | Do instead |
| --- | --- |
| Small or clear, one obvious route | Just do it. The skill's gate skips it anyway. |
| One scoped change ("fix X and add a test") | Make the change. |
| A ticket you want run end to end | Your ticket workflow. |
| Clear on the route, unclear on the requirements | A requirements interview. |
| A route already chosen, now you need a plan by file | An implementation plan. |
| A question about how existing code works | Read or map the code. |

You can start it yourself with `/meta-thinking <the task in one or two lines>`, or with
`/meta-thinking` alone to use the conversation so far. With the line from [Install](#install) in
your `CLAUDE.md`, Claude also offers it at the start of a large task and waits for your yes.

## What a run does

| Step | Who | What happens |
| --- | --- | --- |
| 0. Gate | main session | Checks the task is large and a signal holds, and prints `[meta-thinking] gate: run — signals a, c`. When you named the skill but the gate would skip, it says so and runs anyway, so you can stop it. |
| 1. Facts | main session | Collects your words verbatim, the decisions already made, each constraint as one `MUST` or `NEVER` line, the instruction files, and the skills in the session. It leaves out its own opinion of the answer. |
| 2. Assessment | `meta-thinker` agent | One agent with an empty context reads the brief and the repository and writes the assessment. It can read files and nothing else: no edits, no web, no subagents. |
| 3. Check | main session | Checks the assessment against its contract: all seven sections, every cited path exists, every named skill exists, the caps hold, no forecasts. A defect it cannot fix with a marked correction stops the run. |
| 4. Review | you | You answer at most three questions and pick the route, in one round. |
| 5. Act on answers | main session | Runs research, a requirements interview or a second assessment with full alternatives, only when you ask, and at most once each. |
| 6. Hand-off | main session | Writes an 8-line backbrief (goal, route, constraints, first steps, stop triggers, open questions, next skill), puts the route's steps in the task list, and hands the first step to its skill. The skill ends there. |

The assessment has seven sections and fits in 200 non-blank lines:

| Section | What it holds |
| --- | --- |
| 1. Frame | The goal, what to decide now, what is out of scope, the constraints as `MUST` / `NEVER` lines |
| 2. Known and assumed | Facts with their source (`file:line`, a doc, your words); each guess with `wrong if: …`; a gap checklist |
| 3. Questions | At most 3, each a decision with 2–3 options and a recommendation |
| 4. Research | At most 3 web questions, only where the answer could change the route |
| 5. Recommended route | At most 7 steps, each `do … — why … — check … — skill …`; the one-way doors; `wrong if:` |
| 6. Alternatives | One line per rejected option. A full second route only at a one-way door, at a fork a cheap test can decide, or when you ask. |
| 7. Stop triggers | 2–3 signs during the work that mean "stop and think again" |

[output_example.md](output_example.md) shows one whole run on invented values. Read it first to
see what you get.

The skill never writes code, a plan by file or a ticket. It gives no success chance, time or
token estimate. It never picks the route for you: a question you leave unanswered goes to the
next step as open, never as decided.

## Why it is built this way

Each rule in `SKILL.md` names the findings it rests on. [research-basis.md](research-basis.md)
holds all 111 findings with their links.

| Choice | Why |
| --- | --- |
| A gate that skips small or clear tasks | Planning costs a little on tasks the agent would solve anyway (F1, F43). Practitioners and the PMI and PRINCE2 standards fit the process to the task's size (F54, F76). |
| The gate uses signals you can point at | Agents judge their own chances badly: one predicted 61% success and reached 27% (F31). |
| A separate assessor with a fresh context | A separate intent agent scored 69.4%, against 61.2% for the same check inside the main agent (F16). Its brief carries your words and never the main session's preferred answer. |
| Constraints written as `MUST` / `NEVER` lines | Hand-offs keep facts and drop vague constraints: an explicit imperative leaked 2 times in 48, a hedge 35 times (F37). |
| At most 3 questions, each a real decision | Answerable, targeted questions help, and more questions add nothing (F17, F19). A question the repository can answer is looked up, not asked. |
| One recommended route, alternatives in one line | A model choosing among its own designs on paper adds a few points at most (F93, F99), and each shown route costs reading time (F55). |
| Full alternative routes only at a one-way door or a testable fork | Comparing options pays off on new, hard-to-undo choices (F69, F80). Where a cheap test can decide, the route starts with the test (F101, F110). |
| `wrong if:` lines and plain "I am not sure, but…" | A shown default tends to get followed (F82, F83). First-person hedges reduce overreliance on wrong answers (F88). |
| No success, time or token figures | Agents are overconfident about success, and their time estimates are off by 3.6–6.1 times (F31, F33). |
| A backbrief and the steps in the task list | Agents follow a given plan only in part (F104), and constraints get lost between agents (F36). A backbrief, where the doer restates the intent before starting, comes from military practice (F79). |

Most sources are 2025–2026 arXiv preprints, many run once and not repeated. Treat the numbers as
direction, not as settled fact, and distrust the file after 2027-04-11.

## Install

The skill needs Claude Code. The procedure is in `SKILL.md`; the assessor is a separate agent
type, `meta-thinker`, which the skill cannot run without.

1. Clone this repository and copy two things: the skill folder, and the agent file into an
   agents folder. Claude Code loads agent types from agents folders, not from a skill folder, so
   the copy inside the skill folder is not enough.

   For all your projects, at the user level:

   ```bash
   mkdir -p ~/.claude/skills ~/.claude/agents
   cp -R skills/meta-thinking ~/.claude/skills/
   cp skills/meta-thinking/agents/meta-thinker.md ~/.claude/agents/
   ```

   Or for one project, shared with everyone who works in it:

   ```bash
   mkdir -p ../your-project/.claude/skills ../your-project/.claude/agents
   cp -R skills/meta-thinking ../your-project/.claude/skills/
   cp skills/meta-thinking/agents/meta-thinker.md ../your-project/.claude/agents/
   ```

2. Start a new Claude Code session, so it loads the new agent and skill.

3. Add the offer line to your `CLAUDE.md`, if you want Claude to suggest the skill reliably.
   Without it, Claude may still offer the skill from its listing text, but Claude Code drops the
   descriptions of the least-used skills first when the skill listing outgrows its budget. The
   skill always runs when you type `/meta-thinking`. The line, the `when_to_use` field in the
   `SKILL.md` front matter and the gate in `SKILL.md` Step 0 carry the same test: when you change
   one, change all three in the same edit.

   ```markdown
   - At the start of a task that spans several parts or cannot be said as one change in one
     sentence, when my message names no skill by `/name` and at least one holds — a requirement
     is missing or reads two ways, two viable approaches differ in something I care about, a
     one-way door is on the path, the area is new to this project, or the result cannot be
     checked quickly: offer `/meta-thinking` in your first line and wait for my reply before any
     tool call that does the work, because a wrong route found late costs a rewrite. Never offer
     it for one scoped change, a ticket I want run end to end, unclear requirements on an
     otherwise obvious route, a route already chosen that needs a plan by file, or a question
     about how code works. A reply that does not accept the offer is a no. Offer it once per
     task, and never in an unattended run, where nobody would answer its questions.
   ```

4. Try it on a real task: `/meta-thinking add CSV and PDF export of the monthly reports`. The
   first line is the gate verdict, such as `[meta-thinking] gate: run — signals a, c`, then the
   assessment and the questions. The assessment is saved as `meta-thinking.md` in the task's
   folder when your instruction files name an artifacts folder, and in the session's scratchpad
   otherwise, which lasts only for that session.

The agent file sets `model: opus` and `effort: high`, because a weak planner hurts the result
more than a weak executor (F41). `SKILL.md` passes no model and no effort on the spawn, so the
agent file decides both; the `CLAUDE_CODE_EFFORT_LEVEL` environment variable, when set, still
wins for effort. If that model is not available to you, change `model:` in the copy in your
agents folder: the copy inside the skill folder is not loaded.
The trigger phrases sit in `when_to_use` in the `SKILL.md` front matter, in English. To start the
skill with phrases in your own language, add them there. Keep the addition short: `description`
and `when_to_use` together run to about 1,340 characters, under the 1,536-character limit
Claude Code puts on a skill's listing text, and a longer text loses its end.

`SKILL.md` routes some work away and hands the chosen route to other skills, which it names by
the kind of work: one that builds a single scoped change, runs a ticket end to end, maps how
code works, writes a file-level plan, runs a requirements interview, or does web research. None
of them is in this repository. Your own skills for these jobs show up in the session's skills
listing; without one, the main session does that part itself (`SKILL.md`, § Adjacent skills).

## Files

- [SKILL.md](SKILL.md): the procedure, from the gate to the hand-off, with the brief template
  and the output contract. Read it when you want to know exactly what a run does, or before you
  change a rule.
- [agents/meta-thinker.md](agents/meta-thinker.md): the assessor's agent definition. Copy it
  into an agents folder (step 1 of [Install](#install)); read it when you change what the
  assessor may do.
- [output_example.md](output_example.md): one whole run on invented values. Read it first.
- [research-basis.md](research-basis.md): the 111 findings, 12 contradictions and the expert
  verdict behind the rules. Read it when a rule looks wrong to you.
