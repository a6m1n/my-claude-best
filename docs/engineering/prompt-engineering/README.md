# Prompt engineering practices

How to write the prompts that application code sends to a language model, and the call that
carries them: the goal and the steps first, defined terms, marked inserted material, a way out
when the input lacks the answer, a JSON answer with the reasoning first, tools written as prompt
text, the reasoning effort set on every call, and every change tested old against new.

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The point to adapt](#the-point-to-adapt)

## What is here

- [prompt-engineering.md](prompt-engineering.md) — the rules, one per section, each opening with
  its level (Must or Should) and its reasons, most with a bad and a good example; then where they
  stop holding, a review checklist with each rule's level, and the sources. Read it before you
  write or change a prompt, a chat message sequence, a tool definition, or a setting that changes
  what the model receives, and when you review one.
- [prompt-example.md](prompt-example.md) — one call site, a ticket triage, from the model and
  effort constants to the parsed answer: the one client of the vendor, the answer's schema, and a
  base prompt with a thin layer per model, used as the template for changing models. Read it when
  you add a call to a model or change the model a call site uses.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/prompt-engineering/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you write or change a prompt, a tool
   definition, or a setting that changes what the model receives, read
   `docs/engineering/prompt-engineering/prompt-engineering.md`." Without it an agent never opens
   the file.
3. Use section 20's checklist as the prompt part of your review template, so a reviewer asks the
   same questions every time.
4. The practice links [file-structure.md](../file-structure/file-structure.md),
   [python.md](../python/python.md), [readability.md](../readability/readability.md),
   [logging.md](../logging/logging.md) and [refactoring.md](../refactoring/refactoring.md) for the
   rules they own. Copy those folders too, or replace each link with your own rule for that topic.
5. Re-check the lines that name a moving target: the vendor table in section 15 of the rules
   (dated September 2026), the Claude model versions named in section 13, and the vendor
   mechanics in sections 11, 16 and 17. Vendors change these with each model release.

## The point to adapt

Where each reasoning effort starts is yours to tune. Section 15's table is what is usually used,
and your case set decides, per model. The same holds for every rule marked Should: your tests
keep it or drop it. What does not change is the test behind the Must rules: a prompt states what
the task needs once, the answer comes back in a shape code checks, and no change to the prompt or
the model ships without a run of old against new on the same cases.
