# Prompt engineering rules

**Navigation**

- [1. Purpose, levels and the one rule](#1-purpose-levels-and-the-one-rule)
- [2. The goal and the required steps](#2-the-goal-and-the-required-steps)
- [3. A role only when a person reads the result](#3-a-role-only-when-a-person-reads-the-result)
- [4. Define the terms, one term per concept](#4-define-the-terms-one-term-per-concept)
- [5. Mark the inserted material](#5-mark-the-inserted-material)
- [6. Examples of the form, good and bad](#6-examples-of-the-form-good-and-bad)
- [7. Anonymised examples](#7-anonymised-examples)
- [8. A way out when the input may lack the answer](#8-a-way-out-when-the-input-may-lack-the-answer)
- [9. Lean: every requirement once](#9-lean-every-requirement-once)
- [10. The order of the parts](#10-the-order-of-the-parts)
- [11. The answer is always JSON](#11-the-answer-is-always-json)
- [12. The reasoning field comes first](#12-the-reasoning-field-comes-first)
- [13. Chat messages and their roles](#13-chat-messages-and-their-roles)
- [14. Tool definitions are prompt text](#14-tool-definitions-are-prompt-text)
- [15. Reasoning effort](#15-reasoning-effort)
- [16. One base prompt, a thin layer per model](#16-one-base-prompt-a-thin-layer-per-model)
- [17. The cache switch](#17-the-cache-switch)
- [18. Prompts in git: test and experiment](#18-prompts-in-git-test-and-experiment)
- [19. Where it stops holding](#19-where-it-stops-holding)
- [20. Review checklist](#20-review-checklist)
- [21. Sources](#21-sources)

## 1. Purpose, levels and the one rule

This file is for everyone who writes a prompt that application code sends to a language model,
or the code that builds and sends one: people and AI agents alike. Read it before you write or
change a prompt, the messages of a chat, a tool the model may call, or a setting that changes
what the model receives: the model, its reasoning effort, the cache switch.

It is about the text the model reads and the call that carries it. Where a prompt lives in the
tree is [file-structure.md](../file-structure/file-structure.md) section 3 (`prompts.py`). What a
log line may say about a model call is [logging.md](../logging/logging.md) sections 8 and 10. How
an answer is parsed into a type is [python.md](../python/python.md) section 2. The examples are
plain-text prompts, and Python where the code is the point. Each shows the smallest part that
makes its point and leaves the rest of the prompt out; a Python example leaves out its imports and
the types it calls. [prompt-example.md](prompt-example.md) shows one whole call site.

The one rule: **a prompt is code. It states what the task needs, once and plainly; the answer
comes back in a shape that code checks; and every change to the prompt or to the model is tested
before it ships.**

Every rule below opens with its level:

- **Must**: when its condition holds, always. A miss is a defect a review sends back.
- **Should**: a technique that helps on some tasks and models and hurts on others. The rule says
  when to try it; section 18 says how to decide: run the prompt with it and without it on the same
  cases, and keep it only if it wins.

A Should rule can hold a Must part, and a Must rule a Should part; the part says so. The levels
exist because the evidence differs. Some rules held on every model tested, or the API enforces
them. Others helped one model and hurt the next, such as examples, a role or a reasoning field;
written as orders, they would be applied where they hurt.

Sections 2 to 10 are about the text of the prompt, 11 and 12 about the answer, 13 to 17 about
the call, and 18 about changing any of them.

## 2. The goal and the required steps

**Must.** When you write the task part of a prompt, state the goal, then the steps the task
requires and the rules that decide between answers, in the order they apply. Do not add a
generic "think step by step". How much a model with built-in reasoning thinks is set by its
reasoning effort (section 15); a model with no built-in reasoning gets a reasoning field before
the answer (section 12).

Why: a goal alone leaves the path to the model, and a different path gives a different answer.
When the workflow steps were removed from an agent's instructions, GPT-5 fell from 75% to 28%
first-try success (arXiv:2601.08196). A generic "think step by step" is not the same thing: on
reasoning models it gained little or nothing and cost 20 to 80% more time (Meincke et al.,
2025). The steps here are the task's own, what to check and what decides, not a recipe for
thinking.

Bad — the goal alone:

```text
Decide whether the ticket in <ticket> reports a bug or asks for a feature.
```

On a ticket that mixes a complaint with a wish, the label changes from run to run: nothing tells
the model which part decides.

Good — the same goal, with the steps and the rule for the mixed case:

```text
Decide whether the ticket in <ticket> reports a bug or asks for a feature.

1. Find what the customer expected to happen, and what happened instead.
2. If both describe something the product already does, and only the
   outcome differs, the ticket reports a bug.
3. If the customer asks for something the product does not do today, the
   ticket asks for a feature.
4. If the ticket does both, label it by the first problem it describes.
```

The steps are the path a support engineer takes, and step 4 decides the mixed case that made the
label change. Nothing in it tells the model how to think; that is its effort setting.

## 3. A role only when a person reads the result

**Should.** When the main result is free-form text a person reads, such as a summary, an email,
an explanation or a chat reply, open the prompt with one sentence that names the role the model
writes as and the reader. When code reads the result, such as a label, extracted fields or code,
give no role: write plain instructions. Judge by the result, not by its container: a `summary`
field inside JSON that a person reads is text for a person. In both cases leave out any backstory,
name or personal detail the task does not use.

Why: a role changes tone, vocabulary and depth, not accuracy. Across 162 personas and nine
models, a persona gave no accuracy gain (Zheng et al., 2024); expert personas had no significant
effect on five of six models, and the authors note they may still change the tone (Wharton Prompting
Science Report 4, 2025). Persona details the task did not use cost up to about 30 points on open
models (Principled Personas, 2025). Test the role like any Should technique (section 18).

Bad — a persona with a backstory:

```text
You are Max, a senior support engineer with 15 years at Acme Corp who loves
hard problems. Summarise the ticket in <ticket> for the next shift.
```

The name, the years and the tastes change nothing the summary needs, and on some models they
change the answer.

Good — the role and the reader, nothing else:

```text
You are a support engineer writing the hand-over note for the next shift.
Summarise the ticket in <ticket>.
```

The backstory is gone. One sentence names the writer and the reader, and the reader decides what
stays in: the ticket key, the last thing tried, what is still open.

## 4. Define the terms, one term per concept

**Should.** When the prompt uses labels, categories or terms that have a meaning specific to the
task, define each once. Choose a label whose ordinary meaning matches the definition, or a new
word; never give a familiar word a private meaning. Use one term per concept across the prompt,
with no synonyms for variety. For a classification category, give its definition, what it
includes, what it excludes, and one near miss that does not belong.

Why: the model reads the label's ordinary meaning first. When the definitions contradicted their
labels, every method tested fell below 0.20 F1 (arXiv:2606.06781). A codebook with include and
exclude rules and near misses raised macro-F1 from 0.457 to 0.633 on small open models, and
removing those parts cut it (arXiv:2407.10747, arXiv:2606.06781). One term per concept is an old rule of technical
writing (ASD-STE100); for models the evidence is indirect: a paraphrased question already shifts
the answers (arXiv:2507.07188), and a synonym reads like a second concept.

Bad — a familiar word with a private meaning:

```text
Label each ticket "urgent" or "normal". "urgent" means the customer is on
the Enterprise plan.
```

"Urgent" already means "needs action soon". A free-plan ticket about lost data comes back
"urgent", whatever the definition says.

Good — a label whose ordinary meaning is the definition:

```text
Label each ticket "enterprise" or "standard". "enterprise" means the
customer is on the Enterprise plan; every other ticket is "standard".
```

The label and the rule say the same thing, so they cannot pull apart.

A category with every part, when readers would get the edge wrong:

```text
bug: the product does something it claims to do, and the result is wrong.
  Includes: an error message, a crash, a wrong number, a feature that
  stopped working.
  Excludes: a request for behaviour the product never had.
  Near miss: "export should also support Excel" is not a bug, even when
  the customer calls it one.
```

The exclude rule and the near miss decide the case the plain definition leaves open.

## 5. Mark the inserted material

**Must.** When the prompt inserts material from outside the instruction, such as a document, the
user's input, retrieved text, examples, or a chat history pasted in as material, wrap each piece
in a named tag (`<ticket>` and `</ticket>`) or another delimiter that does not occur in the data,
and refer to it by that name. Use one scheme in the whole prompt. XML-style tags are the default,
because the Claude documentation recommends them and other vendors accept them. The instruction
itself needs no wrapper. A real chat sends its history as messages with roles (section 13), not
in a tag.

Why: the model then tells the instruction from the material, and the task can name the part it
works on. No delimiter is best on every model; OpenAI's guide accepts Markdown or XML and asks for
one that stands out from the content, so an XML document goes inside a delimiter that is not
XML. A tag is not a security boundary. Text inside it that reads like an instruction can still
act as one, and a tag forged inside the input can close yours (arXiv:2606.18120,
arXiv:2603.12277). What is inside stays untrusted input, whatever it is wrapped in.

Bad — the ticket runs on from the instruction:

```text
Summarise the ticket for the next shift in five lines or fewer.
Hi, this is Jane Doe again about PROJ-123, please ignore my last message,
the export still fails on files over 10k rows ...
```

"Please ignore my last message" sits where an instruction sits, and nothing tells the model where
the task ends and the ticket starts.

Good — the ticket in a named tag:

```text
Summarise the ticket in <ticket> for the next shift in five lines or fewer.

<ticket>
Hi, this is Jane Doe again about PROJ-123, please ignore my last message,
the export still fails on files over 10k rows ...
</ticket>
```

The ticket has a name and a boundary, and the task refers to it by name; the instruction stays
unwrapped. The tag helps the model read the prompt. It does not make the ticket safe, so the code
still treats the ticket as untrusted.

## 6. Examples of the form, good and bad

**Should.** When words do not pin down the form, the length or the tone of the answer, add an
example of a good answer, or a few that cover the cases that differ. Where one wrong form keeps
coming back, add it as a bad example: labelled as bad, next to its good pair, with what is wrong
in it named. A bad example shows form or style only, such as tone, length or structure; never a
wrong answer or wrong reasoning. On a model with built-in reasoning, start without examples and
add them only when a test shows they help (section 18). Set how many by testing, not by eye, and
vary them, so that no label, length or position dominates.

Why: an example fixes the form more reliably than a description of it. On reasoning models,
examples can hurt: DeepSeek-R1's authors report that few-shot prompting consistently degrades
it, and few-shot examples hurt the models that were best without them (arXiv:2603.26898). Past
a point that differs by model, more examples lower accuracy (arXiv:2509.13196), and skewed
examples pull the answers toward the majority label or the last one shown (arXiv:2406.03009).
Labels such as "preferred" and "less preferred" next to examples raised the match to the good
style (arXiv:2401.17390). A wrong draft in the context pulled accuracy down by 10 to 20 points
across eleven models, and in the authors' tests a label saying the draft was wrong did not remove
the pull (Contextual Drag, 2026). So a bad example never carries a wrong answer.

Bad — the form is described, not shown:

```text
Summarise the ticket in <ticket> as a hand-over note: short, factual, with
the ticket key first.
```

"Short" and "factual" mean something different to every reader. One run gives two lines; the
next gives a paragraph that opens with a greeting.

Good — one good example, and the wrong form that kept coming back:

```text
Summarise the ticket in <ticket> as a hand-over note in the form of
<good_example>. Do not write like <bad_example>: it opens with a greeting
and has no facts.

<good_example>
PROJ-123: export to CSV fails with "timeout" for accounts over 10k rows.
Tried: raised the limit to 60 s, no change. Open: the customer wants an
answer by Friday.
</good_example>

<bad_example>
Hi team! Jane wrote in again, she is quite upset about the export thing,
could someone take a look when they have a moment? Thanks!
</bad_example>
```

The good example fixes the shape: the key first, then what fails, what was tried and what is
open. The bad example is wrong only in form, it is labelled, and the task says what is wrong in
it, so the model does not drift into it.

## 7. Anonymised examples

**Must.** When an example you write into a prompt comes from a real case, something the user
gave you or works with, do not copy it. Write a similar case with the names and the identifying
details removed: the people, the city, the dates, the product and system names. By default use an
invented name of the same kind, with the kind in a few words: "Acme Bank, a large retail bank".
Use a well-known real name only when every fact in the example is generic, so that nothing the
model knows about that company can contradict it. Keep the role and the numbers the lesson needs.
The rule is about the examples in a prompt; the live input the prompt works on is the task's
data, not an example.

Why: a prompt is committed, reviewed and sent to a vendor on every call, so a real name in it
leaks in three places. Renaming alone does not anonymise: agents re-identified 13 to 21 of 27
interview participants after their names were redacted, against 0 to 5 after the identifying
context was removed too (arXiv:2601.05918, arXiv:2605.30848). A famous name brings its own facts: GPT-4 kept its own
answer about the most popular entities 80% of the time when the context said otherwise (Xie et
al., 2024), and with identical specifications, models recommended the real brand over invented
ones in every trial (arXiv:2606.17443). An invented name costs no accuracy: replacing real names
with invented words did not reliably change reasoning accuracy on seven models (arXiv:2608.30413).

Bad — only the name was changed (Jane Doe, `db.example.com` and the date stand in for a real
client's values):

```text
<example>
Ticket from Acme Savings Bank, from Jane Doe in payments: the nightly export
from db.example.com to the regulator fails since 12 May.
</example>
```

The bank has a new name, but the contact, the host and the date are still the client's own.
Together they point at one real case, and they leave the project with every call.

Good — the same case, anonymised by kind:

```text
<example>
Ticket from Acme Bank, a large retail bank, from its payments team: the
nightly export to the regulator fails.
</example>
```

The contact became a role, and the host and the date are gone. The invented name carries its
kind in a few words and brings no facts of its own. The failing job stays, because the lesson
needs it.

## 8. A way out when the input may lack the answer

**Must**, when the input may not contain the answer, as in extraction, answers from retrieved
documents, or questions about a document. The prompt says what to return in that case, through a
condition the model can check in the input: "if the ticket gives no date, set `date` to null".
Never add a bare "Unknown" or "not sure" option. Define the way out against its nearest
neighbour: "not stated" is a different answer from "no", and "about a week ago" is not a date.
The form depends on the task: a nullable field, an enum value whose condition sits in the field's
description, a refusal, or a question back. Count how often the way out is taken, apart from the
right and wrong answers (section 18).

**Should**, in an interactive setting: let the model ask one clarifying question when a missing
detail would change the answer.

Why: a condition the model can check works, and a bare option does not. The instruction "If there
is no information available from the context, you should reject to answer" raised correct
refusals of unanswerable questions from 49% to 88%, with little cost on the answerable ones
(arXiv:2412.12300). A reflexive "Unknown" option cost 19.8 points in a survey-style study,
because models copy the surface pattern of abstaining (arXiv:2507.16199). In clinical
extraction, a third value, "not documented", next to "no" drew most of the disagreement between
prompt variants (arXiv:2606.05970), which is why the two need a line drawn between them. Grading
on accuracy alone rewards guessing (Kalai et al., 2025), so the way-out rate is counted on its
own. A policy of asking back raised success on underspecified GitHub issues from 22% to 37%
(arXiv:2604.14624).

Bad — a way out the model cannot check:

```text
Extract the date the export first failed. If you are not sure, answer
"Unknown".
```

"Not sure" is a feeling, not a fact in the ticket. The model says "Unknown" about a date it
could read, and guesses one when the ticket has none.

Good — the same way out, as a condition on the input:

```text
Extract the date the export first failed, as YYYY-MM-DD, into
first_failure_date. If the ticket in <ticket> gives no date for the first
failure, set first_failure_date to null. A guess such as "about a week ago"
is not a date: set it to null.
```

The model can check the condition in the ticket, and the nearest neighbour, a vague date, is
decided in advance. The field is nullable in the schema, so code reads the way out without
parsing a word.

## 9. Lean: every requirement once

**Must.** Before a prompt goes to review, read it from the top and make each requirement appear
once, in plain words, stated as what to do rather than what not to do where you can. Cut hedges
("try to", "if possible", "please be very careful"), general best-practice text that no step of
this task needs, and context the task never uses. Check that no two instructions conflict. Never
cut a requirement to make the prompt shorter: lean means no filler, not short. A requirement
given as a rule and a checkable example is not a repeat.

Why: an unstated requirement is a guess. Models inferred unstated requirements 41% of the time,
and underspecified prompts were twice as likely to regress when the model or the prompt changed
(Yang et al., 2025). Detailed contexts beat short generic prompts (Agentic Context Engineering,
2025). Conflicts cost more than length: instruction following fell from about 0.96 with one
instruction to between 0.20 and 0.60 with twenty, driven by pairs that conflict
(arXiv:2608.02639). A generic rules wrapper that conflicted with the task cut extraction from
100% to 90% (When "Better" Prompts Hurt, 2026). Hedged instructions let many times more cases
through than explicit ones (arXiv:2608.29028). Reasoning over the input also gets worse as the
input grows, long before the context limit (Levy et al., 2024), so context the task never uses is
not free. One practitioner view: the Claude Code team reports cutting its system prompt by about
80% for newer models, with fewer "do not" lines. That is a statement from a talk, not a
measurement.

Bad — three requirements said seven times:

```text
Please summarise the ticket in <ticket>. It is very important that the
summary is accurate. Be careful to include the ticket key. Make sure you
include the ticket key. The summary should be short. Remember that this is
for the next shift, so keep it short and make sure it is accurate and
includes the key. Do not make anything up. Accuracy is crucial.
```

The reader, model or person, has to find three requirements among seven sentences, and cannot
tell whether a repeat means something more.

Good — the same three requirements, once each:

```text
Summarise the ticket in <ticket> for the next shift, in five lines or fewer,
ticket key first. Use only what the ticket says.
```

Each requirement appears once, as something to do, and "short" became a number a reviewer can
check.

## 10. The order of the parts

**Should.** When you lay out a prompt, use this order by default:

1. The static part, in the system slot: the role if the result is text for a person, the goal and
   the required steps, the definitions, the way out, the examples.
2. The part that changes on every call, in the user turn: the inserted material, with long
   material before the question.
3. The question itself, last.
4. Inside a list of options, categories or definitions: one fixed order that carries no meaning,
   the same on every call.

When a result may depend on the order, test it with the order shuffled (section 18).

Why, and how sure: the order matters in two places that are measured, and in two that are not.
A fixed opening is cheaper: a prompt cache matches the request from its start, so static text
first is what gets cached. Order inside a list changes answers: models picked the last option far
more often, over 20 times as often on a small model (arXiv:2507.07188), and reordering the
definitions in a codebook changed about 20% of the labels (arXiv:2606.06781). "Long material
before the question" comes from Anthropic's own tests, not an independent study. The order inside
the static part is a convention for the reader, not measured.

Good — the default layout, as a skeleton:

```text
[system]
The goal and the required steps
The definitions
The way out
The examples

[user]
<ticket>
...
</ticket>
Which kind of ticket is this?
```

Everything that stays the same on every call comes first and is cached; the ticket changes per
call and comes after it; the question is the last thing the model reads.

## 11. The answer is always JSON

**Must.** Every model response is JSON. Nested structures are fine, and prose a person reads
lives in a string field. Pass the schema through the vendor's structured-output feature, not only
as text in the prompt. Make every closed set an enum in the schema. Parse the response into a type
where it arrives ([python.md](../python/python.md) section 2). Before you parse, check whether the
model refused or stopped at the output limit: either can break the schema. After you parse, check
the values in code. Write text fields as ordinary prose; the schema carries the structure. This
holds when the model also has tools: the tool schema shapes a call, the response schema shapes the
answer (section 14).

The cost: to stream an answer to a person word by word, the code needs a parser that reads
partial JSON and shows the text field as it grows.

Why: code reads the answer, and code cannot read prose. A named field with a closed set of values
fails at the parser when the model strays, instead of passing a wrong label on as text. Asking for
a format in words costs accuracy on open models, 3 to 9 points, while closed models paid little
or nothing (The Format Tax, 2026). The vendors' schema features enforce the shape instead of
asking for it; their docs name the refusal and the output limit as the cases where the answer may
not match, and ask you to check the values yourself.

Bad — the answer is prose:

```text
Decide whether the ticket in <ticket> reports a bug or asks for a feature,
and say why in one sentence.
```

The answer comes back as "This looks like a bug because ...", and the code that reads it has to
search the text for the label. A run that says "most likely a bug" passes as neither.

Good — the same task, with the shape passed as a schema:

```python
@unique
class TicketKind(StrEnum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"


class TicketTriage(BaseModel):
    reasoning: str  # first, so it leads to the kind: section 12
    kind: TicketKind
```

```text
Decide whether the ticket in <ticket> reports a bug or asks for a feature.
```

`TicketTriage` goes to the vendor as the response schema, and the prompt keeps only the task. The
"say why" became a field of its own, and `kind` accepts two values and nothing else, so a stray
answer fails at the edge.

## 12. The reasoning field comes first

**Should**, where the decision needs judgement or people need to see why: give the answer a
short reasoning field. **Must**, once the field exists: it comes before the answer fields.

Why, in plain words: the model writes JSON from top to bottom. A field before the answer is
reasoning that leads to the decision. A field after the answer is a justification, written once
the decision is already made. On six frontier models, moving the reasoning field before the label
raised accuracy by 14.6 to 23.8 points (Lin, 2026); reasoning first and formatting second is the
same pattern in general (The Format Tax, 2026). The field also shows a reviewer where a wrong
answer went wrong, which is what error analysis reads (Husain and Shankar). A second, short
explanation field after the answer, for the reader, is allowed, but one field placed first is
usually enough. Format rules are followed far less inside reasoning than in the final answer
(ReasonIF, 2025), so the schema, not the reasoning, carries the shape.

Bad — the reasoning after the answer:

```python
class TicketTriage(BaseModel):
    kind: TicketKind
    reasoning: str
```

The model writes `kind` first. Everything in `reasoning` can only defend a label it has already
chosen.

Good — the same fields, the reasoning first:

```python
class TicketTriage(BaseModel):
    reasoning: str  # first, so it leads to the kind
    kind: TicketKind
```

The order is the fix: the model now reasons about the ticket before it writes the kind.

## 13. Chat messages and their roles

**Should.** When you call a chat model, build the messages with the vendor SDK's types, not by
hand. Put the static instructions, and the role when there is one, in the system slot; put the
data, the inserted material and the examples in the user turn. Send a real conversation as its
messages, in order. When a task spread over many turns starts to drift, start a new conversation
with one turn that restates everything so far.

Two parts are **Must**, because the API rejects the alternative:

- **Must:** no request ends with an assistant message. Claude models from 4.6 on reject a
  prefilled assistant turn with a 400 error; the structured output of section 11 does what the
  prefill used to force.
- **Must:** in a tool loop, send the reasoning state back unchanged: the thinking blocks,
  reasoning items or thought signatures the vendor returned, exactly as received. The SDK or the
  vendor's stateful API can do it for you. All three large vendors reject or degrade a turn where
  it is missing or edited.

Roles are not a security boundary. The model follows the style of the text more than the message
it sits in (arXiv:2603.12277), so a tool result or user text stays untrusted in any role.

Why: the vendors differ, and the SDK knows how. Anthropic and Gemini take the system prompt as a
field of the request, and Anthropic sends tool results back inside a user message; OpenAI uses a
`developer` role for its reasoning models; Gemini names the assistant `model`; some open models
have no system role. Static instructions in the system slot also keep the start of the request
the same for the cache (section 10). Spreading a task over turns costs: across 15 models, the
same task given in pieces over several turns scored 39% lower on average, mostly from lower
reliability, and one turn that put the pieces together recovered about 95% of the loss (Laban et
al., 2025).

Bad — four roles in one user message:

```text
user: You are a support engineer at Acme Corp. Earlier the customer asked
      about order PROJ-123 and you said you would check it. The order lookup
      returned {"status": "shipped", "carrier": "..."}. Now the customer asks:
      where is my order? Answer them.
```

The role is user text, the earlier assistant turn is retold instead of shown, and the tool
result is a quote the model cannot tie to a call.

Good — one message per turn, each with its role:

```text
system:    You are a support engineer answering customers of Acme Corp.
user:      Where is my order? Ticket PROJ-123.
assistant: [calls lookup_order(ticket="PROJ-123")]
tool:      {"status": "shipped", "carrier": "..."}
```

Each turn has its role and its place, and the tool result follows the call it answers. The
request ends on the tool result, not on an assistant message. How each vendor names these roles
is the SDK's job, so the field names are left out.

## 14. Tool definitions are prompt text

**Must**, when the model is given tools, as functions or through an MCP server. A tool's name,
description and parameter schema are text the model reads on every call, and they are written
and tested like a prompt:

- **Must:** a change to a tool's name, description or schema is tested per model, like a prompt
  change (section 18). The test covers which tool is chosen, with other tools present and with
  requests that do not name the tool; the argument values; and "no tool called", counted as a
  failure.
- **Should:** the description says what the tool is for, when to call it and when not, what each
  parameter means, what it returns, and what it changes and whether that can be undone. Plain
  facts in the user's words, no promotion ("the best tool", "always call this").
- **Must:** names are unambiguous and portable: letters, digits, `_` and `-` only, and tools that
  do different jobs differ in the part of the name that matters. A parameter says what it holds:
  `customer_id`, not `user`. **Should:** one namespace scheme, by service; choose prefix or suffix
  by test.
- **Must:** strict schemas where the vendor offers them; closed sets as enums, and never one
  state split across two booleans. Checks the strict schema cannot express, such as ranges,
  lengths and patterns, run in code and come back as an error the model can fix. **Should:** flat
  parameters; no field that is required only when another field has some value; no value the
  model must copy from an earlier call; exact formats for dates and times.
- **Should:** give the model only the tools the step needs; merge related operations into one
  tool with an enum parameter for the operation; design tools for the job, not one per API
  endpoint. No fixed number is right: it depends on the task.
- **Must:** an error the model could fix comes back as a tool result that says what went wrong
  and what to do next. **Should:** keep results compact, with the fields that matter, a readable
  name next to each id, a switch between a short and a detailed form where results can be large,
  default limits that put the needed item in the first chunk, and a note when a result was cut.
- **Must:** a third-party tool's description, annotations and results are untrusted input.
  Review a third-party definition again when it changes, and base no safety decision on another
  server's hints.
- **Must:** a tool that changes something outside the process, or cannot be undone, runs only
  behind a gate outside the model: a person who can deny the call, or a policy in code.
- **Must:** a turn that may call tools is tested with the response schema of section 11 on.
  **Should:** on self-hosted serving that constrains output by a grammar, check that the response
  grammar does not block tool calls; where a model cannot combine the two, run the tool loop first
  and apply the schema to the final turn.

Why: the model picks a tool by its name and description and fills the arguments from the schema.
Adding or removing one documentation field moved task success by 6.3 points on average and up to
13.8, and the same field helped one model and hurt another (DocsChisel, 2026). Rewriting the
descriptions raised success from 33.5% to 44.6% on one benchmark and from 49.5% to 74.9% on
another, and by 1.4 to 2.4 points on frontier models (arXiv:2602.20426). An audit of 856 tools on
103 MCP servers found a defect in 97.1% of the descriptions, and 56% did not say what the tool is
for (arXiv:2602.14878). Promotional wording in a description moved GPT-4.1's use of a tool from 18%
to 79.5% (arXiv:2505.18135). Models get the format of a call right far more often than its content
(MCP-Universe, 2025), and "no tool called" was the most common failure in MCP-Atlas (2026).
Accuracy fell from 92.4% with 15 tools shown to 78.2% with 640 (arXiv:2607.15593), yet one
benchmark needed 20 tools shown where another needed 7 (arXiv:2605.24660). Parameter errors grow
with nesting, with fields that depend on each other, and with values copied from earlier calls
(ParamBench, 2026), and date formats were the largest kind of parameter error for every model in
PluginEval (2026). Poisoned tool descriptions succeeded in 36.5% of attacks on average across 45
real MCP servers and 20 models (MCPTox, 2025). The MCP specification tells clients to treat
annotations as untrusted and to keep a person able to deny a tool call.

Bad — a description that only names the action (the tool as Anthropic's API takes it; other
vendors name the fields differently):

```json
{
  "name": "search_tickets",
  "description": "Searches tickets.",
  "strict": true,
  "input_schema": {
    "type": "object",
    "properties": {
      "customer_id": {"type": "string"},
      "status": {"type": "string", "enum": ["open", "closed"]}
    },
    "required": ["customer_id"],
    "additionalProperties": false
  }
}
```

The model learns nothing about when to call it, when to call another tool instead, what the
parameters hold or what comes back, so it guesses each time.

Good — the same tool, described:

```json
{
  "name": "search_tickets",
  "description": "Finds a customer's support tickets. Call it when the user asks about a past or open ticket and you know their customer id. Do not call it for orders; use get_order. Returns up to 20 tickets, newest first, each with its key, title, status and last update, and says when more exist. Reads only; changes nothing.",
  "strict": true,
  "input_schema": {
    "type": "object",
    "properties": {
      "customer_id": {"type": "string", "description": "The customer's id, such as C-10492. Not their email."},
      "status": {"type": "string", "enum": ["open", "closed"], "description": "Only tickets with this status."}
    },
    "required": ["customer_id"],
    "additionalProperties": false
  }
}
```

The description now says what the tool is for, when to use another one, what it returns and that
it changes nothing, and each parameter says what it holds. The name, the parameters and their
types stayed the same.

## 15. Reasoning effort

**Must.** Set the reasoning effort explicitly on every call to a model that has one; never rely
on the default, which differs by vendor and by model. Keep the model and the effort as named
constants per call site: `<purpose>_llm_model` and `<purpose>_llm_reasoning_effort`, such as
`TEXT_GENERATOR_LLM_MODEL` and `TEXT_GENERATOR_LLM_REASONING_EFFORT` in Python, in the module's
`consts.py` ([file-structure.md](../file-structure/file-structure.md) section 3). The effort is a
closed set, so it is an enum ([python.md](../python/python.md) section 3). The one client of the
vendor maps it to the vendor's parameter. Choose the model first, then tune the effort.

Where to start. The table shows what is usually used: it is a starting point, not a rule. Raise or
lower the level freely. A higher level often buys accuracy on a hard task, at a cost, and the
experiment decides (section 18), per model. Never carry a level over to a new model.

| Task | Usual start |
|---|---|
| Objective classification, guard or injection classification, retrieval, format conversion, answers in an exact format | none, or the lowest level the model has |
| The same, when counting, dates, arithmetic, aggregation over a long document, or sarcasm and irony hide inside | low |
| Interactive coding | medium |
| Long, loosely specified, multi-step work with tools | high and above |

Why these starts: on prompt-injection classification, every model tested did better with thinking
off (arXiv:2603.25176); in Qwen3's own tables, thinking lost on retrieval; and rules about the
exact format of the output were followed less with thinking on (arXiv:2606.09662). Hidden
counting, dates and aggregation gain even when the task looks simple: hard date arithmetic rose
from 32 to 53 (arXiv:2510.07880), long-document tasks by 14 to 16 points, most of it in
aggregation (LongBench Pro, 2026), and sarcasm detection from 32 to 68 on a small model (arXiv:2603.19558). OpenAI's Codex
guide uses medium as the all-round default for interactive coding. On a benchmark of professional
tasks run by an agent with tools, every step up in effort gained on all seven current models
tested (GDPval-AA, Artificial Analysis). Start lower and raise the level when a check fails; a
level that is too low can cost more in retries than it saves.

What it costs: a fixed high level used 7 to 40 times the tokens of low (arXiv:2603.07915). In a
streamed chat, the first visible word came about ten times later at the highest level than at the
lowest (Artificial Analysis). On short, well-specified tasks, the differences between levels
often sat inside the noise between reruns (ReasonBENCH, 2026), so a level is chosen with repeats.

The mechanics, **Must**:

- Raise the output limit (`max_tokens`) with the level. At high levels the reasoning can use up
  the limit and cut the answer off.
- Choose the level per task or per conversation, never per turn: a change of level in the middle
  of a conversation breaks the vendor's prompt cache.
- Where a model has no `none`, use its lowest level. "None" may still reason: with thinking off,
  Claude writes its reasoning into the visible answer.
- Never assume the response contains a reasoning block.

Each vendor has its own parameter and its own levels, and a level's name does not mean the same
amount across vendors, or across the model generations of one vendor. As of September 2026:

| Vendor | Parameter | Levels |
|---|---|---|
| OpenAI | `reasoning_effort` (`reasoning.effort` in the Responses API) | `none` to `max`; each model accepts a subset |
| Anthropic | `output_config.effort` | `low` to `max`, no `none`; the effort covers all output tokens, tool calls included; with adaptive thinking (`thinking: {"type": "adaptive"}`) the model decides whether and how much to think, and the effort guides it; some models cannot turn thinking off |
| Google Gemini | `thinking_level` (Gemini 3); `thinking_budget` in tokens (Gemini 2.5) | `minimal` to `high`; on the Pro models `minimal` does not guarantee that thinking is off |
| xAI | `reasoning_effort` | `low` to `xhigh`; reasoning cannot be turned off |
| Qwen3 (open weights) | `enable_thinking` | on or off |

These names change from release to release; check the model's page before you set one. The enum
in your code is your own set of levels, and the vendor's client maps it to what the current model
accepts. [prompt-example.md](prompt-example.md) shows the constants and the enum.

## 16. One base prompt, a thin layer per model

**Should**, when a project uses more than one model or changes models. Keep one base prompt that
holds the task, the rules and the schema, and a thin layer per model that holds only what depends
on the model: the reasoning effort, the output limit, verbosity and sampling settings, and any
instruction one model needs and another does not. On a model change, run the base prompt
unchanged with the new model first (section 18), and only then change the layer.

Why: the vendors publish a guide per model release that lists what changed. Base prompts mostly
carry over; the settings do not, and some the new model rejects outright (newer Claude models
return an error for a non-default temperature). OpenAI's guide for GPT-5.2 asks you to keep the
prompt the same while you test the new model, so the test measures the model change and not a
prompt edit. A layer that holds only the model-specific part keeps that test clean, and shows
what to revisit on the next change. [prompt-example.md](prompt-example.md) has a template.

## 17. The cache switch

**Must.** When you set up the code that sends prompts, add a boolean setting
`DISABLE_PROMPT_CACHE`, off by default. When it is on, the line `Request UUID: <a fresh uuid4>`
goes at the very start of the system prompt, followed by a newline;
and where the vendor or a gateway in between has its own switch to skip a cache, the setting turns
that on too. Apply it in the one client every model call goes through
([file-structure.md](../file-structure/file-structure.md) section 4). A request id for tracing
goes into the request's metadata, never into the prompt.

Why: the vendors' prompt caches do not change the answer. Anthropic's and OpenAI's docs both state
that a cached request returns the same output as an uncached one; the cache saves cost and time
only. The switch is for the caches that do change what you get, and for measuring:

- a gateway or SDK response cache returns a stored answer for a request it has seen, so a fix you
  are testing never reaches the model;
- a self-hosted server's prefix cache changed agent runs at temperature 0 in 36 to 75% of the
  episodes in one study (arXiv:2609.04748);
- a cost or latency test has to measure a request the cache does not serve. Claude Code ships its
  own switch, `DISABLE_PROMPT_CACHING`, for debugging and cost testing.

Caches match the request from its start, so a first line that differs on every request matches
nothing after it; one report measured a changing UUID in a system prompt missing the whole cached
prefix. A UUID later in the request would leave the part before it cached. A request id
in the prompt would change the prompt itself on every call, which is why it goes into metadata.
The switch is also visible in the environment, off unless it says otherwise, so it cannot be left
on by a forgotten edit.

Both examples leave out what every call also passes, the model, its reasoning effort, the output
limit and the response schema (sections 11 and 15); [prompt-example.md](prompt-example.md) shows a
whole client.

Bad — a hand edit to the prompt is the cache switch:

```python
# core/<vendor>_client.py
class ProviderClient:
    def __init__(self, api: ProviderApi) -> None:
        self._api = api

    def complete(self, system: str, user: str) -> ModelResponse:
        # TODO remove before commit: forces a cache miss while I debug the empty summaries
        system = f"debug 3 {system}"

        return self._api.complete(system=system, user=user)
```

The prefix changes on every attempt, it changes the text the model reads, and one day it is
committed. Nothing tells the next reader which answers were produced with it.

Good — the same client, with the switch as a setting:

```python
# core/config.py
class Settings(BaseSettings):
    # DISABLE_PROMPT_CACHE=true only while debugging or measuring
    disable_prompt_cache: bool = False


# core/<vendor>_client.py
class ProviderClient:
    def __init__(
        self,
        api: ProviderApi,
        *,
        disable_prompt_cache: bool,
        new_request_uuid: Callable[[], UUID],
    ) -> None:
        self._api = api
        self._disable_prompt_cache = disable_prompt_cache
        self._new_request_uuid = new_request_uuid

    def complete(self, system: str, user: str) -> ModelResponse:
        if self._disable_prompt_cache:
            # First in the system prompt: a cache matches from the request's start, so
            # nothing from here on hits.
            system = f"Request UUID: {self._new_request_uuid()}\n{system}"

        return self._api.complete(system=system, user=user)
```

The hand edit became a setting on the client: the startup code reads it once and builds the
client once with it and with the UUID source, `uuid4`, so a test can fix the UUID
([readability.md](../readability/readability.md) section 6). The UUID line is the only thing it
changes, at the very start of the system prompt, and the prompt text stays as it is. The vendor's
own no-cache switch, where one exists, is left out too.

## 18. Prompts in git: test and experiment

**Must.** Keep every prompt in git, next to the code that sends it, reviewed and shipped with it.
On every change to a prompt, a tool definition, the model or its settings, run the old and the
new version on one fixed set of cases and compare them case by case:

- No case set yet: build one before the change ships, from real inputs of the task, anonymised
  the way section 7 anonymises an example, each with its expected answer. Where no real inputs
  exist yet, write inputs that cover the kinds the task expects, and replace them with real ones
  as they arrive. A new prompt runs alone against the set; a change to an existing prompt or model
  runs old against new on it.
- Grow the set from real errors you have seen, not from cases you invented to pass.
- Write the pass criterion down before you run.
- On a model change, keep the prompt fixed, so the test measures the model.
- Keep options in one fixed order, or shuffle them across runs; parse leniently before you score;
  count the way-out answers of section 8 apart from right and wrong ones.
- Do not claim a small difference from a small set.

**Should.** When you try a technique this practice marks Should, such as a role, examples, a
reasoning field, definitions, the order of the parts, a per-model layer or a reasoning level, run
it as an experiment: the prompt with it and without it, on the same cases, and keep it only if it
wins. Every "test it" in this file means this section.

How big a set: about 1,000 questions to see a 3-point difference with the usual statistical
power (Miller, 2024); 50 to 100 cases show only large shifts; below a few hundred cases the
usual error bars are too narrow (arXiv:2503.01747). There is no general rule for the number of
reruns: rerun until the result stops moving on your cases. Compare the two versions case by case
on the same set, never two averages from different sets.

Why: an edit that fixes the case in front of you changes others you do not see. Reading real
outputs and turning failures into cases is the most useful part of evaluating a model
application (Husain and Shankar), and they keep prompts "versioned, reviewed, and deployed
atomically with the application code". A generic "better" prompt can make the results worse
(When "Better" Prompts Hurt, 2026). Whether a technique helps depends on the pass criterion you
chose (Wharton Prompting Science Report 1, 2025). Parse errors alone deflated one model's score by
up to 206% (arXiv:2607.22969), and shuffling the input order cost 3 to 12 points
(arXiv:2502.04134). Grading on accuracy alone rewards guessing (Kalai et al., 2025).

<!--
FUTURE: an evals practice (docs/engineering/evals/)
Trigger: a project needs LLM judges, error bars or an eval gate in CI.
Fix location: a new practice folder, linked from this section.
Approach: case sets from error analysis, paired comparison, sample size for the effect you need,
judge validation, way-out answers scored on their own.
-->

## 19. Where it stops holding

- **A prompt you run once by hand**, in a chat window or a notebook, to explore. Sections 11, 15,
  17 and 18 are ceremony there; sections 2, 4, 5 and 9 still pay, since the next person reads the
  prompt too.
- **Code no change touches.** It stays as it is until a change edits it
  ([refactoring.md](../refactoring/refactoring.md) section 2).
- **A framework that builds the prompt or the messages for you**, such as an agent framework's
  tool format. Follow its shape, and apply these rules to the text you give it.
- **A model or API without a feature a rule relies on.** With no structured-output feature, the
  schema goes into the prompt and the parser rejects anything else (section 11). With no reasoning
  control, section 15 does not apply to that model.

## 20. Review checklist

One question per section. Ask them when you review a prompt, a tool definition, or the code that
sends one. A missed Must sends the change back; a missed Should is a question for the author:
was it tested?

| Section | Level | Ask |
|---|---|---|
| 2. Goal and steps | Must | Does the task give the goal, then the steps and the rules that decide, with no generic "think step by step"? |
| 3. Role | Should | If a person reads the result, does one sentence name the role and the reader; if code reads it, is there no role; is there no unused backstory? |
| 4. Terms | Should | Is every task-specific label defined once, with its ordinary meaning matching, one term per concept? |
| 5. Inserted material | Must | Is every piece of inserted material in a named tag, one scheme for the whole prompt? |
| 6. Examples | Should | Did a test keep the examples; does every bad example show form only, labelled, next to its good pair? |
| 7. Anonymised examples | Must | Are names and identifying details gone from every example taken from a real case? |
| 8. Way out | Must, interactive part Should | Where the input may lack the answer, is the way out a condition the model can check, with its rate counted; in an interactive setting, was a clarifying question tried and kept only if it helped? |
| 9. Lean | Must | Is each requirement stated once, with no hedge, no boilerplate, no unused context and no conflict? |
| 10. Order | Should | Is the static part first, the question last, and is every list in one fixed order? |
| 11. JSON | Must | Is the schema passed through the vendor's feature, parsed into a type, with refusal and truncation checked? |
| 12. Reasoning field | Should, order Must | If there is a reasoning field, is it before the answer fields? |
| 13. Chat roles | Should, two parts Must | Are the messages built with the SDK's types; does no request end on an assistant message; does the reasoning state go back unchanged in a tool loop? |
| 14. Tools | Must, several parts Should | Must: is each tool change tested per model; are names unambiguous, schemas strict, fixable errors returned as results, third-party definitions untrusted and side effects gated? Should: does each description say what the tool is for, when and when not, what it returns and changes, with flat parameters and only the tools the step needs? |
| 15. Reasoning effort | Must | Is the effort set on every call, from `<purpose>_llm_model` and `<purpose>_llm_reasoning_effort` constants, with the output limit raised to match? |
| 16. Base and layer | Should | Is the model-specific part in a thin layer, apart from the base prompt? |
| 17. Cache switch | Must | Does `DISABLE_PROMPT_CACHE=true` put a fresh `Request UUID:` line at the very start of the system prompt, and is it off by default? |
| 18. Test and experiment | Must, experiments Should | Did the change run old against new on the fixed case set (a new prompt: against a new set), with the pass criterion written first? |

## 21. Sources

Studies (arXiv ids where the source is a preprint): Zheng et al. on personas in system prompts
(arXiv:2311.10054, EMNLP Findings 2024); Wharton Prompting Science Reports 1
(arXiv:2503.04818) and 4 (arXiv:2512.05858); Principled Personas (arXiv:2508.19764, EMNLP 2025);
Meincke et al. on chain-of-thought prompting (arXiv:2506.07142); arXiv:2601.08196 on goal-only
instructions; arXiv:2606.06781 and arXiv:2407.10747 on codebooks and label semantics;
arXiv:2507.07188 on option order; arXiv:2606.18120 and arXiv:2603.12277 on delimiters and role
confusion; DeepSeek-R1 (arXiv:2501.12948); arXiv:2603.26898, arXiv:2509.13196 and
arXiv:2406.03009 on examples; contrastive in-context learning (arXiv:2401.17390); Contextual Drag
(arXiv:2602.04288); arXiv:2601.05918 and arXiv:2605.30848 on re-identification after name-only redaction; Xie et al.,
"Adaptive Chameleon or Stubborn Sloth" (arXiv:2305.13300, ICLR 2024); arXiv:2606.17443 on real and
invented brands; arXiv:2608.30413 on invented entity names; arXiv:2412.12300 on refusals in
retrieval; arXiv:2507.16199 on "Unknown" options; arXiv:2606.05970 on "not documented" in clinical
extraction; Kalai et al., "Why Language Models Hallucinate" (arXiv:2509.04664); arXiv:2604.14624 on
clarifying questions; Yang et al. on unstated requirements (arXiv:2505.13360); Agentic Context
Engineering (arXiv:2510.04618); arXiv:2608.02639 on conflicting instructions; When "Better" Prompts
Hurt (arXiv:2601.22025); arXiv:2608.29028 on hedged and explicit constraints; Levy et al., FLenQA
(ACL 2024); The Format Tax (arXiv:2604.03616); Lin on the order of reasoning and answer fields
(arXiv:2608.08254); ReasonIF (arXiv:2510.15211); Laban et al., "LLMs Get Lost in Multi-Turn
Conversation" (arXiv:2505.06120); DocsChisel (arXiv:2608.10037); arXiv:2602.20426 on rewriting
tool descriptions; arXiv:2602.14878, an audit of MCP tool descriptions; arXiv:2505.18135 on
promotional tool descriptions; MCP-Universe (arXiv:2508.14704); MCP-Atlas (arXiv:2602.00933);
arXiv:2607.15593 and arXiv:2605.24660 on the number of tools; ParamBench (2026); PluginEval
(arXiv:2608.08700); MCPTox (arXiv:2508.14925); arXiv:2603.25176 on injection classification with
and without thinking; the Qwen3 technical report; arXiv:2606.09662 on format rules with thinking
on; arXiv:2510.07880 on date arithmetic; LongBench Pro (arXiv:2601.02872); TextReasoningBench
(arXiv:2603.19558); arXiv:2603.07915 on the tokens of each effort level; ReasonBENCH
(arXiv:2512.07795); arXiv:2609.04748 on prefix caches in self-hosted serving; Miller, "Adding
Error Bars to Evals" (arXiv:2411.00640); arXiv:2503.01747 on error bars for small sets;
arXiv:2607.22969 on parse errors in scoring; arXiv:2502.04134 on input order.

Practitioners: Hamel Husain and Shreya Shankar, the evals FAQ (hamel.dev, 2025–2026), on error
analysis, versioning prompts, and system versus user prompts; Simon Willison on tool poisoning in
MCP (2025); Amp's documentation of its reasoning dial (2026); the Claude Code issues on
`DISABLE_PROMPT_CACHING` and on a UUID in the system prompt (2026); Artificial Analysis, the GDPval-AA results and the latency methodology (2026); a talk
by the Claude Code team on its shorter system prompt, as reported by Simon Willison (2026).

Vendor documentation, fetched September 2026, for each vendor's own mechanics: Anthropic on
prompt caching, structured outputs, XML tags, messages and prefill, tool definitions, strict tool
use, effort and extended thinking; OpenAI on prompt caching, structured outputs, reasoning, the
Codex prompting guide and the GPT-5 model guides; Google on Gemini thinking, structured output
and prompting strategies; xAI on reasoning; Qwen on thinking mode; the Model Context Protocol
specification (2026-07-28) on tools, errors and annotations.
