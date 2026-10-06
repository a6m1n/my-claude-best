# Worked example: one ideal work item of each type

The work items of one project, of each Jira type, with the reason each is good next to it. They
come from the running project of [project-example.md](project-example.md): Acme Corp moves card
payments in its online shop's checkout to a new provider, and the Jira key is `PROJ`. Every name,
number and key is invented. Pick the type with [jira-work-item-types.md](jira-work-item-types.md) section 1,
write the item by [tickets.md](tickets.md) section 2, and fill its fields by
[jira-fields.md](jira-fields.md).

**Navigation**

- [1. Epic](#1-epic)
- [2. Story](#2-story)
- [3. Task](#3-task)
- [4. Bug](#4-bug)
- [5. Subtasks](#5-subtasks)
- [6. Subtasks handed out per person, and the fix](#6-subtasks-handed-out-per-person-and-the-fix)

No certification defines an ideal ticket ([jira-work-item-types.md](jira-work-item-types.md) section 5), so
"ideal" here means this practice's own choice: an item that follows tickets.md and
jira-work-item-types.md, with what each standard contributes named on its Carries line.

Each item shows the fields that [jira-fields.md](jira-fields.md) section 1 says to fill for its
type; a field shown as none or Unassigned carries its reason at the line. The space has two
components, Checkout and Payments API, each with a lead and Unassigned as its default assignee, so
a new item waits in the backlog until someone takes it ([jira-fields.md](jira-fields.md)
section 2). No story, task or bug below has a Due date, because
none of them carries a date promised to someone outside the team.

## 1. Epic

The epic is one deliverable of the WBS ([project-example.md](project-example.md) section 4), and its
description is the WBS dictionary entry ([wbs.md](wbs.md) section 6):

```
PROJ-11  Epic
Routing flag
Assignee: Richard Roe    Components: Payments API
Labels: provider-switch   # the switch cuts across Checkout and Payments API, so it is a label, not a component (jira-fields.md section 2)
Start date: 2026-12-21    Due date: 2027-03-26   # the plan's dates: 2.1 starts, PROJ 2.0 ships; the Timeline draws the epic from them (jira-fields.md section 1)
Fix versions: none   # each child carries the version that ships it (tickets.md section 5)

Scope: the flag that sends each card payment to the old or the new provider, the steps that move traffic from 1% to all, and the removal of the flag after the move.
Owner: Richard Roe.
Done when: with the flag off every payment goes to the old provider, and at 100% every card payment goes to the new one.

Child work items
- PROJ-123  Task   Route card payments by flag
- PROJ-131  Bug    Saved-card payment ignores the flag
- PROJ-150  Task   Remove the routing flag once all traffic is on the new provider   # made with the flag, so the flag does not outlive the move (release.md section 6)
- ...              # the rest are cut when their version is one release away (wbs.md section 5)
```

The epic is good because its "Done when" is a state the sponsor can check, and it is too big for the
three-day limit, so it groups work items instead of being one
([jira-work-item-types.md](jira-work-item-types.md) section 2). It has no Fix version of its own: its
work ships across several releases, and each child carries the version that ships it, so the
release pages show how much of the epic ships in each one ([tickets.md](tickets.md) section 5). Its
Start date and Due date are the plan's, so the Timeline draws it where the plan puts it.

Carries: PMI WBS dictionary (scope, owner, done-when); PRINCE2: the done-when written as measurable
quality criteria, as a Product Description asks (a secondary source, edition unknown); Jira's epic
as the group of work toward one deliverable, drawn on the Timeline from its Start date and Due date
([jira-fields.md](jira-fields.md) section 1).

## 2. Story

A story is an outcome a shopper can see ([jira-work-item-types.md](jira-work-item-types.md) section 1):

```
PROJ-136  Story    Parent: PROJ-10    Status: Backlog   # Parent replaced Epic Link (jira-fields.md section 1)
Show the shopper what to do after a declined card
Fix versions: PROJ 1.0 test payments    Components: Checkout    Labels: provider-switch
Assignee: Unassigned   # stays empty until someone takes it from the backlog (jira-fields.md section 1)
Reporter: the customer support lead   # John Smith created it for them, so questions go to the person who raised it (jira-fields.md section 1)
Priority: Medium   # the default: the backlog order ranks stories and tasks (jira-fields.md section 1)
Story points: 3   # sized by the Developers in refinement (jira-fields.md section 1)

As a shopper whose card is declined, I want to see what I can do next,
so that I can pay another way.

Acceptance criteria
- When the provider declines a card for lack of funds, the line "Try another card or another
  payment method." appears under the declined message, with the shop's other payment methods.
- When the provider declines an expired card, the line "Check the expiry date or use another
  card." appears under the declined message, and the expiry date field is marked.
- Both lines are shown in the shop's three languages.
```

The story is good because it names the user and the result, each criterion is a check someone else
can run on the checkout page, and the three criteria fit the three-working-day limit
([tickets.md](tickets.md) sections 2 and 3). It holds work that no other item of WBS 1.5 holds:
`PROJ-135` shows why a payment failed, `PROJ-139` translates those two messages
([jira-workflow.md](jira-workflow.md) section 7), and `PROJ-136` adds what to do next, so the work
package has no gap and no duplicate ([wbs.md](wbs.md) section 2).

Carries: PMI's user story ("an outcome for a specific user") and acceptance criteria; PRINCE2: the
acceptance criteria written as measurable quality criteria, as a Product Description asks (a
secondary source, edition unknown); Scrum: an item that can be Done within one Sprint; the team's
Definition of Done
([project-example.md](project-example.md) section 6).

## 3. Task

A task is work with no outcome a shopper can see
([jira-work-item-types.md](jira-work-item-types.md) section 1). Three tasks follow, each under the
epic of its WBS work package ([project-example.md](project-example.md) section 4): `PROJ-123` (2.1),
`PROJ-124` (3.1) and `PROJ-125` (3.2). Work package 3.2 takes up to seven working days in the
schedule, more than one work item may take, so it is split into work items that each name it in
their summary ([wbs.md](wbs.md) section 7); `PROJ-125` is the first of them.

```
PROJ-123  Task    Parent: PROJ-11
Route card payments by flag
Fix versions: PROJ 1.0 test payments    Sprint: PROJ Sprint 3    Story points: 3
Components: Payments API    Labels: provider-switch    Assignee: Richard Roe

Acceptance criteria
- With the flag on, a test card payment is sent to the new provider.
- With the flag off, the same payment is sent to the old provider.
```

```
PROJ-124  Task    Parent: PROJ-12
Add a nullable `provider` column to payment records
Fix versions: PROJ 1.0 test payments    Sprint: PROJ Sprint 2    Story points: 2
Components: Payments API    Labels: provider-switch    Assignee: Mary Major

Acceptance criteria
- The migration adds the column with no default and no NOT NULL.   # expand step, so the old release still runs (rollback-plan.md section 4)
- The old release runs against the migrated schema in staging.
```

```
PROJ-125  Task    Parent: PROJ-12
Write the provider on each payment: new card payments   # names its work package, because 3.2 is split into several items (wbs.md section 7)
Fix versions: PROJ 1.0 test payments    Sprint: PROJ Sprint 3    Story points: 3
Components: Payments API    Labels: provider-switch    Assignee: Mary Major

Acceptance criteria
- The payment record of a new card payment stores which provider handled it.
- Payment records written before this change keep an empty provider; the backfill (WBS 3.3) fills them.
Blocked by: PROJ-124   # the criteria need the column that PROJ-124 adds (tickets.md section 5)
```

The tasks are good because none has an "As a ..." line it cannot honestly fill, and the criteria of
each prove the one thing its work must show: `PROJ-123` that the flag picks the provider,
`PROJ-124` that the old release still runs, so a rollback stays possible
([rollback-plan.md](rollback-plan.md) section 4), and `PROJ-125` that each new card payment records
its provider while the old records wait for the backfill. Each sits under the epic of its work
package, so Jira and the WBS agree on who owns the work ([wbs.md](wbs.md) section 7).

Carries: PMI's task ("a specific activity ... to achieve a project goal") and acceptance criteria;
PRINCE2: the acceptance criteria written as measurable quality criteria, as a Product Description
asks (a secondary source, edition unknown); the team's Definition of Done.

## 4. Bug

A bug found in testing, in the same version. The steps, the expected result and the actual result
sit in the description, as [tickets.md](tickets.md) section 2 says:

```
PROJ-131  Bug    Parent: PROJ-11
Saved-card payment ignores the flag
Fix versions: PROJ 1.0 test payments    Sprint: PROJ Sprint 4    Story points: 1
Affects versions: PROJ 1.0 test payments   # the version where the bug shows (jira-fields.md section 1)
Priority: High   # from its severity, SEV 2: after a rollback, saved-card shoppers would stay on the new provider (sla.md sections 2 and 7)
Components: Payments API    Labels: provider-switch    Assignee: Mary Major
Environment: staging, flag off, saved test card of a returning shopper   # where it was seen, so a reader can repeat it there (jira-fields.md section 1)

With the flag off, a test payment on a returning shopper's saved card goes to the new provider.
Steps: 1. Turn the flag off in staging. 2. Pay with a saved test card.
Expected: the old provider handles it. Actual: the new provider handles it.
Blocks: PROJ-123   # PROJ-123's flag-off criterion cannot pass until this is fixed (tickets.md section 5)
```

The bug is good because it states the symptom and leaves the diagnosis out. The reader can repeat
the steps and see the wrong provider, without opening the comments. Its priority comes from its
severity, and its Affects versions and Environment say where it shows, so a reader knows how urgent
it is and where to repeat it ([jira-fields.md](jira-fields.md) section 1). Its branch and commit
are in [project-example.md](project-example.md) section 6.

Carries: Tatham: symptoms, steps, expected, actual; Atlassian's bug template: numbered steps in the
description and the environment; the team's Definition of Done.

## 5. Subtasks

Subtasks are optional ([jira-work-item-types.md](jira-work-item-types.md) section 3). The Developers of
`PROJ-123` chose to track two steps of it. The Components, Labels and Fix versions of the
subtasks, the same as those of `PROJ-123`, are left out here:

```
PROJ-141  Subtask    Parent: PROJ-123
Read the flag value in the payment router
Assignee: Unassigned   # the Developer who starts the step takes it (jira-fields.md section 1)
Story points: none     # never on a subtask: velocity ignores subtask points (jira-work-item-types.md section 3)

PROJ-142  Subtask    Parent: PROJ-123
Send the payment to the provider the flag names
Assignee: Unassigned
Story points: none
```

The subtasks are good because each is a step of a day or less, each is named by what it does and
not by who does it, and none carries points, so the task keeps the one estimate the velocity chart
reads. Each waits unassigned until the Developer who starts the step takes it. Both must be Done
before the sprint closes, and they take the sprint of `PROJ-123`.

Carries: Scrum Guide: the Developers plan the Sprint Backlog, in items of "one day or less"; Jira:
a subtask has no children, takes its parent's sprint and is left out of velocity.

## 6. Subtasks handed out per person, and the fix

Bad: the task is split by person. The one problem is that subtasks are used to hand out work:

```
PROJ-141  Subtask    Parent: PROJ-123
Richard Roe: router
Assignee: Richard Roe
Story points: none     # never on a subtask: velocity ignores subtask points (jira-work-item-types.md section 3)

PROJ-142  Subtask    Parent: PROJ-123
Mary Major: flag
Assignee: Mary Major
Story points: none
```

The reason it is wrong: each person now owns a piece alone, and nobody owns the task. Wolpers
lists this among his Jira anti-patterns (his view, [jira-work-item-types.md](jira-work-item-types.md)
section 3). Agreeing what the task must deliver and leaving the way to the people is
[principles.md](principles.md) section 2.

Good: the same work, split by step and owned by the Developers. This is section 5:

```
PROJ-141  Subtask    Parent: PROJ-123
Read the flag value in the payment router
Assignee: Unassigned   # the Developer who starts the step takes it (jira-fields.md section 1)
Story points: none     # never on a subtask: velocity ignores subtask points (jira-work-item-types.md section 3)

PROJ-142  Subtask    Parent: PROJ-123
Send the payment to the provider the flag names
Assignee: Unassigned
Story points: none
```

This fixes the one problem. The names say what each step does, and nobody is assigned before the
step starts, so any Developer can pick one up, and the task stays the unit that is estimated, owned
and finished by the team.

Carries: Scrum Guide: the Sprint Backlog is a plan by and for the Developers; Jira: subtask
estimates are left out of velocity.
