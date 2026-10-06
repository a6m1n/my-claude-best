# Worked example: one ideal work item of each type

The work items of one project, one of each Jira type, with the reason each is good next to it. They
come from the running project of [project-example.md](project-example.md): Acme Corp moves card
payments in its online shop's checkout to a new provider, and the Jira key is `PROJ`. Every name,
number and key is invented. Pick the type with [work-item-types.md](work-item-types.md) section 1,
and write the item by [tickets.md](tickets.md) section 2.

No certification defines an ideal ticket ([work-item-types.md](work-item-types.md) section 5), so
"ideal" here means this practice's own choice: an item that follows tickets.md and
work-item-types.md, with what each standard contributes named on its Carries line.

**Navigation**

- [1. Epic](#1-epic)
- [2. Story](#2-story)
- [3. Task](#3-task)
- [4. Bug](#4-bug)
- [5. Subtasks](#5-subtasks)
- [6. Subtasks handed out per person, and the fix](#6-subtasks-handed-out-per-person-and-the-fix)

## 1. Epic

The epic is one deliverable of the WBS ([project-example.md](project-example.md) section 4), and its
description is the WBS dictionary entry ([wbs.md](wbs.md) section 6):

```
PROJ-11  Epic    Owner: Richard Roe    Fix versions: PROJ 1.0 test payments, PROJ 1.1 1% live
Routing flag

Scope: the flag that sends each card payment to the old or the new provider, the steps that move traffic from 1% to all, and the removal of the flag after the move.
Owner: Richard Roe.
Done when: with the flag off every payment goes to the old provider, and at 100% every card payment goes to the new one.

Child work items
- PROJ-123  Story  Route card payments by flag
- PROJ-131  Bug    Saved-card payment ignores the flag
- PROJ-150  Task   Remove the routing flag once all traffic is on the new provider   # made with the flag, so the flag does not outlive the move (release.md section 6)
- ...              # the rest are cut when their version is one release away (wbs.md section 5)
```

The epic is good because its "Done when" is a state the sponsor can check, and it is too big for the
three-day limit, so it groups stories instead of being one ([work-item-types.md](work-item-types.md)
section 2). Its work shows in two versions, so the release pages show how much of it ships when.

Carries: PMI WBS dictionary (scope, owner, done-when); PRINCE2: the done-when written as measurable
quality criteria, as a Product Description asks (a secondary source, edition unknown); Jira's epic
as the group of work toward one deliverable; the Fix versions of [tickets.md](tickets.md) section 5.

## 2. Story

A story is an outcome a shopper can see ([work-item-types.md](work-item-types.md) section 1):

```
PROJ-123  Story    Epic: PROJ-11    Fix version: PROJ 1.0 test payments
Route card payments by flag

As a shopper, I want my card payment to go through the new provider
so that checkout keeps working while Acme Corp changes provider.

Acceptance criteria
- With the flag on, a test card payment is sent to the new provider.
- With the flag off, the same payment is sent to the old provider.
- The payment record stores which provider handled it.
Blocked by: PROJ-124   # the third criterion needs the column (tickets.md section 5)
```

The story is good because it names the user and the result, each criterion is a check someone else
can run, and the three criteria fit the three-working-day limit ([tickets.md](tickets.md)
sections 2 and 3).

Carries: PMI's user story ("an outcome for a specific user") and acceptance criteria; PRINCE2: the
acceptance criteria written as measurable quality criteria, as a Product Description asks (a
secondary source, edition unknown); Scrum: an item that can be Done within one Sprint; the team's
Definition of Done
([project-example.md](project-example.md) section 6).

## 3. Task

A task, because the work is not an outcome for a shopper:

```
PROJ-124  Task    Epic: PROJ-12    Fix version: PROJ 1.0 test payments
Add a nullable `provider` column to payment records.

Acceptance criteria
- The migration adds the column with no default and no NOT NULL.   # expand step, so the old release still runs (rollback-plan.md section 4)
- The old release runs against the migrated schema in staging.
```

The task is good because it has no "As a ..." line it cannot honestly fill, and its criteria prove
the one thing that matters: the old release still runs, so a rollback stays possible
([rollback-plan.md](rollback-plan.md) section 4).

Carries: PMI's task ("a specific activity ... to achieve a project goal") and acceptance criteria;
PRINCE2: the acceptance criteria written as measurable quality criteria, as a Product Description
asks (a secondary source, edition unknown); the team's Definition of Done.

## 4. Bug

A bug found in testing, in the same version. The steps, the expected result and the actual result
sit in the description, as [tickets.md](tickets.md) section 2 says:

```
PROJ-131  Bug    Epic: PROJ-11    Fix version: PROJ 1.0 test payments
Saved-card payment ignores the flag

With the flag off, a test payment on a returning shopper's saved card goes to the new provider.
Steps: turn the flag off in staging; pay with a saved test card.
Expected: the old provider handles it. Actual: the new provider handles it.
Environment: staging, flag off, saved test card of a returning shopper.   # where it was seen, as Atlassian's bug template asks
Blocks: PROJ-123
```

The bug is good because it states the symptom and leaves the diagnosis out. The reader can repeat
the steps and see the wrong provider, without opening the comments. Its branch and commit are in
[project-example.md](project-example.md) section 6.

Carries: Tatham: symptoms, steps, expected, actual; Atlassian's bug template: numbered steps in the
description and the environment; the team's Definition of Done.

## 5. Subtasks

Subtasks are optional ([work-item-types.md](work-item-types.md) section 3). The Developers of
`PROJ-123` chose to track three steps of it:

```
PROJ-141  Subtask of PROJ-123    Owner: the Developers    Estimate: none   # velocity ignores subtask points (work-item-types.md section 3)
Read the flag value in the payment router

PROJ-142  Subtask of PROJ-123    Owner: the Developers    Estimate: none
Send the payment to the provider the flag names

PROJ-143  Subtask of PROJ-123    Owner: the Developers    Estimate: none
Store the provider on the payment record
```

The subtasks are good because each is a step of a day or less, each is named by what it does and
not by who does it, and none carries points, so the story keeps the one estimate the velocity chart
reads. All three must be Done before the sprint closes, and they take the sprint of `PROJ-123`.

Carries: Scrum Guide: the Developers plan the Sprint Backlog, in items of "one day or less"; Jira:
a subtask has no children, takes its parent's sprint and is left out of velocity.

## 6. Subtasks handed out per person, and the fix

Bad: the story is split by person. The one problem is that subtasks are used to hand out work:

```
PROJ-141  Subtask of PROJ-123    Jane Doe: backend     Estimate: none
PROJ-142  Subtask of PROJ-123    John Smith: database  Estimate: none
```

The reason it is wrong: each person now owns a piece alone, and nobody owns the story. Wolpers
lists this among his Jira anti-patterns (his view, [work-item-types.md](work-item-types.md)
section 3). Agreeing what the story must deliver and leaving the way to the people is
[principles.md](principles.md) section 2.

Good: the same work, split by step and owned by the Developers. This is section 5:

```
PROJ-141  Subtask of PROJ-123    Owner: the Developers    Estimate: none   # velocity ignores subtask points (work-item-types.md section 3)
Read the flag value in the payment router

PROJ-142  Subtask of PROJ-123    Owner: the Developers    Estimate: none
Send the payment to the provider the flag names

PROJ-143  Subtask of PROJ-123    Owner: the Developers    Estimate: none
Store the provider on the payment record
```

This fixes the one problem. The names say what each step does, so any Developer can pick one up,
and the story stays the unit that is estimated, owned and finished by the team.

Carries: Scrum Guide: the Sprint Backlog is a plan by and for the Developers; Jira: subtask
estimates are left out of velocity.
