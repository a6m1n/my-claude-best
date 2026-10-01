# Readability practices

How to write a function or a class that a reader follows from the unit itself: one job and a name
that says it, the main path flat under its guard clauses, comments that give reasons, blank lines
between stages, every input and every object it calls in the signature, and names taken from the
business.

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The point to adapt](#the-point-to-adapt)

## What is here

- [readability.md](readability.md) — the principles, one per section, each with a bad and a good
  example, then where they stop holding and a review checklist. Read it before you write or
  change a function or a class, and when you review one.
- [module-example.md](module-example.md) — one small module, an overdue-invoice reminder,
  written to every principle at once, with the reason next to each part. Read it when you write a
  new module's use case, its rule and its test.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/any-language/readability/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you write or change a function or a
   class, and when you review one, read `docs/engineering/any-language/readability/readability.md`." Without
   it an agent never opens the file.
3. Use section 9's checklist as the readability part of your review template, so a reviewer
   asks the same questions every time.
4. The practice links [git.md](../git/git.md), [python.md](../../python/language/python.md),
   [file-structure.md](../file-structure/file-structure.md) and
   [refactoring.md](../refactoring/refactoring.md) for the rules they own. Copy those folders too,
   or replace each link with your own rule for that topic.
5. Re-check the lines that name a moving target: the ruff version and rule codes (`RET505`,
   `RET506`, `ERA001`) and the formatter behaviour in section 5.

## The point to adapt

How many blank lines a body gets is yours to tune. This practice puts one at every stage
boundary, more than PEP 8's "sparingly" asks for; a team that prefers denser bodies may
keep blank lines for the larger stages only. What does not change is the test behind every
section: a reader who opens one unit can tell what it does and what it depends on without opening
anything else.
