# Work item types

Which Jira work type to pick for a piece of work, where the line between two types falls, who
creates each one, and what the project management standards ask of a work item. Read it before you
create a work item, and when two types both seem to fit. How to write the item once you have picked
its type is in [tickets.md](tickets.md) section 2, and one ideal item of each type is in
[work-item-example.md](work-item-example.md).

**Navigation**

- [1. The five work types](#1-the-five-work-types)
- [2. Story or epic](#2-story-or-epic)
- [3. Task or subtask](#3-task-or-subtask)
- [4. Who creates each type](#4-who-creates-each-type)
- [5. What the standards ask of a work item](#5-what-the-standards-ask-of-a-work-item)
- [6. Sources](#6-sources)

## 1. The five work types

Pick the type from what the work is, before you write anything else, because the type decides who
reads the item and how the board and the reports count it. Jira has five types, and Atlassian
defines them in one line each:

| Type | Atlassian's definition |
|---|---|
| Epic | "A big user story that needs to be broken down" |
| Story | "the smallest unit of work that needs to be done" |
| Task | "work that needs to be done" |
| Bug | "a problem which impairs or prevents the functions of a product" |
| Subtask | "a piece of work that is required to complete a task" |

"Issue" is the old name of a work item in Jira; this folder says work item
([tickets.md](tickets.md) section 1). Atlassian's definitions are short on purpose, so the table
below is this practice's own reading of them. Take the first row that fits:

| What you have | Type | Why |
|---|---|---|
| Something is broken: the product does less than it should | Bug | A bug is a defect, and its report is a different shape from a feature ([work-item-example.md](work-item-example.md) section 4). |
| An outcome a user can see, that fits in three working days ([tickets.md](tickets.md) section 3) | Story | The story names the user and the result, so the team can check the result. |
| Work with no outcome a user can see (a migration, a setup, a contract step), that fits in three working days | Task | A task has no user to write "As a ..." for; the acceptance criteria carry the proof instead. |
| A deliverable that needs more than one work item | Epic | The epic groups the work items and answers "is the deliverable done?". |
| A step inside one work item | Subtask, and only if the team wants it | A subtask is a step, not a unit of work with its own value (section 3). |

Check: read the summary of the item. If you cannot say who sees the result and what they see, it
is a task or a bug, not a story.

## 2. Story or epic

PMI's Lexicon defines both. A user story is "A brief description of an outcome for a specific user,
which is a promise for a conversation to clarify details." An epic is "A large, related body of
work intended to hierarchically organize a set of requirements and deliver specific business
outcomes." (PMI Lexicon, 2026) So a story is one outcome for one kind of user, and an epic is a
body of work that groups requirements.

No source draws a number between them. Atlassian writes that there is "no universal definition that
draws a line between a big story and an epic". Cohn takes the Agile view: an epic is "simply 'a
large user story'", and he notes that Jira defines the epic differently, so a team should use its
tool's vocabulary (Cohn, 2025). Jira's epic groups work, so this practice follows Jira.

Draw the line by size: a story fits the three-working-day limit of [tickets.md](tickets.md)
section 3, and an epic does not. This line is this practice's own. The reason: without a number,
every author draws the line in a different place, and a "story" of three weeks hides its progress
until the last day.

An epic is one deliverable of the work breakdown structure. The mapping from WBS to Jira is in
[wbs.md](wbs.md) section 7, and the epic's description holds the WBS dictionary entry
([wbs.md](wbs.md) section 6). When a story grows past three days, split it into stories under the
same epic. Do not promote it to an epic, because an epic is a deliverable the sponsor can accept,
and half a story is not one.

Check: before you move a story to In Progress, ask whether its acceptance criteria can be met in
three working days ([tickets.md](tickets.md) section 3). If not, it is several stories under an
epic.

## 3. Task or subtask

A task is a work item of its own. It has an owner, a branch and a pull request
([tickets.md](tickets.md) section 4). A subtask is a step inside one work item, and Jira limits it
in four ways:

- It cannot have child work items, and it takes the sprint of its parent (Atlassian). It is a leaf,
  so it cannot hold a further breakdown.
- Before a sprint completes, all its subtasks must be Done (Atlassian). One forgotten subtask
  blocks the close of the sprint.
- The Velocity Chart ignores subtask estimates: "Estimates from sub-tasks are not included in the
  Velocity Chart's calculation." (Atlassian)
- Subtasks exist only where the space enables them (Atlassian), so a team's board may have none.

From these, three rules. They are this practice's own, built on the Jira facts above:

- Use a subtask only for a step of a day or less inside one work item, and only when the step helps
  the Developers keep track. A task or a story with no subtasks is normal. The hook is the Scrum
  Guide: the Sprint Backlog is "a plan by and for the Developers", and the Developers may
  decompose items "into smaller work items of one day or less". The reason: a step that small
  needs no branch and no review of its own.
- Do not estimate a subtask in points. The reason: velocity ignores the number, so it only looks
  like data. Estimate the parent.
- Do not create one subtask per person to hand out work ("Jane Doe: backend"). The reason: it turns
  a shared item into separate pieces that each person owns alone. Wolpers lists this among his
  Jira anti-patterns, and it is his view, read as a snippet, not a standard (Wolpers, undated).
  The same point in this folder is [principles.md](principles.md) section 2: agree what the item
  must deliver, and leave the way to the people. A filled bad and good case is in
  [work-item-example.md](work-item-example.md) section 6.

Check: before you add a subtask, ask whether the step takes a day or less and has no owner but the
Developers. If it takes longer, make it a task.

## 4. Who creates each type

Let each type be created by the role that knows the most about it, because a work item written by
someone who does not know the work is rewritten later. Jira's Create work items permission sets
only who may create; Atlassian names no role that should write stories or epics (Atlassian,
undated). The roles below come from the Scrum Guide and from this practice.

| Type | Who creates it | Why |
|---|---|---|
| Epic | The product owner or the project manager, in planning, from the WBS | An epic is a deliverable of the plan. This role split is this practice's own. |
| Story | The product owner is accountable; anyone may write one | The Scrum Guide: the Product Owner is accountable for "Creating and clearly communicating Product Backlog items" and "may delegate the responsibility to others". Cohn: anyone may write stories, and the product owner stays accountable. The team refines it: refinement adds "a description, order, and size" (Scrum Guide). |
| Task | Anyone on the team; the product owner orders it | This practice's own. A task is work for the team, and its place in the backlog is the product owner's call. |
| Bug | Whoever finds it | This practice's own. The finder has the steps and the symptom in mind, and waiting for a role loses them. |
| Subtask | The Developers, as part of the Sprint Backlog | The Scrum Guide: the Sprint Backlog is a plan by and for the Developers. |

Where the product owner is not the author, the product owner still decides the order and whether
the item stays in the backlog.

## 5. What the standards ask of a work item

None of PMP, PRINCE2 or CSM and PSM defines a ticket. Each defines its own unit of work, and the
table shows them. User stories are not part of Scrum either: the word does not occur in the Scrum
Guide (2020), and not in the CSM Learning Objectives (2022). So there is no "ideal ticket per
certification", and this file does not invent one. It shows what each body asks of its unit and
which Jira field can carry it. The column of Jira fields is this practice's own mapping.

| Standard | Its unit of work | What it requires | The Jira field that carries it |
|---|---|---|---|
| PMI Lexicon (PMP) | Work package, task | A task is "A specific activity or work that needs to be completed in order to achieve a project goal." Acceptance criteria are "A set of conditions that are met before deliverables are accepted." The WBS dictionary describes each component ([wbs.md](wbs.md) section 6). | Work package: a story, task or bug. Acceptance criteria: the description. WBS dictionary entry: the epic's description. |
| PRINCE2 7 (secondary source, edition unknown) | Work Package, Product Description | A Work Package holds a description, product descriptions, techniques, tolerances, the date of agreement, reporting arrangements and quality criteria. A Product Description is written before the product and has measurable quality criteria. | The description, with the quality criteria as acceptance criteria. |
| Scrum Guide (CSM, PSM) | Product Backlog item | Refinement adds "a description, order, and size". An item "that can be Done by the Scrum Team within one Sprint" is ready for selection. It must meet the Definition of Done. | Description; the item's place in the backlog (order); the estimate (size). The Definition of Done belongs to the team, not to the item ([tickets.md](tickets.md) section 2). |

PRINCE2 is a secondary source here, as in [principles.md](principles.md) section 4: the pages
read describe it, and the PeopleCert manual is paid. Read the Work Package row as a pointer to
what the method cares about (measurable criteria, a named agreement), not as a quotation of the
manual.

One ideal item of each type, with what each standard contributes to it, is in
[work-item-example.md](work-item-example.md).

## 6. Sources

- Atlassian, ["What are work types"](https://support.atlassian.com/jira-cloud-administration/docs/what-are-issue-types/), undated, read 2026-10-06: the five definitions, and the subtask rules (no children, the parent's sprint, only where enabled).
- Atlassian, ["Create a work item and a subtask"](https://support.atlassian.com/jira-software-cloud/docs/create-an-issue-and-a-sub-task/), undated, read 2026-10-06.
- Atlassian, ["Velocity chart"](https://support.atlassian.com/jira-software-cloud/docs/view-and-understand-the-velocity-chart/), undated, read 2026-10-06: subtask estimates are not counted.
- Atlassian, ["Complete a sprint"](https://support.atlassian.com/jira-software-cloud/docs/complete-a-sprint/), undated, read 2026-10-06: all subtasks must be Done.
- Atlassian, ["Work item permissions in a space"](https://support.atlassian.com/jira-cloud-administration/docs/use-manage-sprints-permission-for-advanced-cases/), undated (snippet only): the Create work items permission, who may create.
- Atlassian, ["Epics, stories, themes"](https://www.atlassian.com/agile/project-management/epics-stories-themes), undated (snippet): no universal line between a big story and an epic.
- Cohn, ["Stories, epics and themes"](https://www.mountaingoatsoftware.com/agile/stories-epics-and-themes), 2025-04-28: an epic as a large story, and use the tool's vocabulary.
- Cohn, ["Short answers to your big questions about user stories"](https://www.mountaingoatsoftware.com/agile/short-answers-to-your-big-questions-about-user-stories), undated (snippet): anyone may write stories.
- PMI, [Lexicon of Project Management Terms, version 5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: user story, epic, task, work package, acceptance criteria.
- Schwaber and Sutherland, [The Scrum Guide](https://scrumguides.org/scrum-guide.html), November 2020: the Product Owner's accountability, refinement, ready, the Sprint Backlog, the Definition of Done; the word "user story" does not occur. Verbatim checked.
- Scrum Alliance, [CSM Learning Objectives](https://assets.scrumalliance.org/media/certifications/los/csm_learning_objectives_2022.pdf), 2022 (file dated 2024-02): no user story objective.
- Wolpers, ["Jira anti-patterns"](https://age-of-product.com/jira-anti-patterns/), undated (snippet only): per-person subtasks. One practitioner's view.
- prince2.wiki, ["Work Package"](https://prince2.wiki/management-products/baselines/work-package/) and ["Product Description"](https://prince2.wiki/management-products/baselines/product-description/), undated: secondary sources on PRINCE2, edition unknown; the PeopleCert manual is paid.
