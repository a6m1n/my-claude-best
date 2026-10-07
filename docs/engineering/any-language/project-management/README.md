# Project management practices

How a software team that tracks its work in Jira runs a project: why it has a project manager, the
phases a project and a release pass through, and the few artifacts that keep the team and its
sponsor pointed at the same goal. The rules follow PMBOK and the PMP from PMI, PRINCE2 from
PeopleCert and the Scrum Guide, and use Atlassian's own docs for Jira.

**Navigation**

- [The one rule](#the-one-rule)
- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)

## The one rule

**Project management helps the team reach the agreed goal in the agreed time.** Every artifact in
this folder earns its place by serving that, and none exists to watch people. An artifact that no
decision uses is dropped: the team pays for it in time and gets nothing back. The reasons, and the
sources behind them, are in [principles.md](principles.md).

## What is here

A file named `jira-…` is about one Jira object, such as the work types, the fields or the board.
Every other file is a practice, and maps that practice to Jira in a section of its own.

- [principles.md](principles.md): what project management is for, what it never does (micromanage,
  track for its own sake), how to see and limit workload, which standard names which artifact, and
  why Jira is the tool, and what a project is, what limits it and what its success means. Read it
  before you open a project, and when you doubt whether an artifact or a report is worth its cost.
- [operating-system.md](operating-system.md): how the artifacts below work as one loop, the rhythm
  that keeps them current, and which conditional artifacts a project keeps. Read it when you
  start a project and choose its artifacts, and when someone asks what happens when.
- [life-cycle.md](life-cycle.md): the five phases of a project, the artifact each one ends with and
  who approves it, and the seven SDLC phases each release passes through, with their Jira homes.
  Read it when you start a project, a phase or a release, when you decide whether a phase is
  over, and when you pick the development approach.
- [charter.md](charter.md): the project charter, what it holds, who issues it, and how it differs
  from the plan. Read it when you open a project.
- [stakeholders.md](stakeholders.md): the stakeholder register, influence and interest, and
  engagement now and wanted. Read it in initiation, before the kickoff, and at each phase end.
- [roles-and-decisions.md](roles-and-decisions.md): the roles, one Accountable per deliverable in
  the RACI matrix, who decides what, DACI and the decision log. Read it when you assign the
  deliverables, and before a decision that is hard to undo.
- [project-plan.md](project-plan.md): the project plan, its schedule (the Gantt chart, the Jira Timeline), its baseline and how it
  stays current. Read it when you plan a project, or change its scope or schedule.
- [schedule.md](schedule.md): dependencies and what Jira can draw, estimates in ranges, and the
  critical path when a date is fixed. Read it when you plan the schedule, link work that waits, or
  give a date.
- [wbs.md](wbs.md): the work breakdown structure, its rules, and how it maps to epics, work items
  and subtasks in Jira. Read it when you break the scope into work.
- [risks.md](risks.md): the risk register, the scoring, the five ways to respond to a threat (mitigation is one of them),
  contingency plans and reserves, and the review. Read it when you open the register, add a risk or review the register.
- [tickets.md](tickets.md): what a work item holds, how big it is, how it links to a branch, a pull
  request and a release. Read it when you write or triage a work item.
- [jira-work-item-types.md](jira-work-item-types.md): the five Jira work types, story or epic, task or
  subtask, who creates each, and what PMI, PRINCE2 and Scrum ask of a unit of work. Read it when
  you pick a work item's type.
- [jira-work-item-example.md](jira-work-item-example.md): one ideal work item of each type, with what each
  standard contributes. Read it when you write the first work item of a type.
- [jira-workflow.md](jira-workflow.md): the board's statuses and when an item moves between them, the
  workflow diagram, Blocked, Canceled, comments, and a work item that is only partly done. Read it
  when you move a work item, comment on one, or set up a board.
- [jira-fields.md](jira-fields.md): what each Jira field holds and when to fill it, components or
  labels, and what differs in a team-managed space. Read it when you fill a work item's fields or
  set up a space.
- [meetings.md](meetings.md): the kickoff and the sprint meetings, their order, cadence and
  timebox, and who speaks in what order. Read it when you plan or run a team meeting.
- [communication.md](communication.md): the communication plan, the weekly status update and its
  three markers, the escalation path, and management by exception. Read it when you plan who hears
  what, each week when you write the update, and when a forecast leaves the tolerance.
- [sla.md](sla.md): what an SLA is, how it differs from an SLO, severity levels, and what "fixed"
  means in it. Read it when you agree or change an SLA.
- [release.md](release.md): what a release is, environments, the go or no-go decision, version
  numbers, CI/CD, and how a release reaches users. Read it when you plan a release and before you
  mark a version released.
- [rollback-plan.md](rollback-plan.md): the rollback plan of a release, its trigger, owner and
  steps, and how data changes are handled. Read it when you plan a release.
- [project-example.md](project-example.md): one small project with every artifact filled in, with
  the reason next to each. Read it when you write your first charter, plan or register.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/any-language/project-management/`,
   so the path in step 2 and the links to other practices in step 5 still work.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you open a project, write or change
   its charter, plan, scope, schedule, WBS, risk register, stakeholder register or RACI matrix, make
   or record a decision that is hard to undo, write a status update, write, triage, split or move a
   Jira work item, fill its fields or comment on one, set up a board or a space, plan a release or
   its rollback, open or run an incident or roll a release back, agree an SLA, or plan or run a team
   meeting, read `docs/engineering/any-language/project-management/README.md` and the files it
   routes to for that work."
   Without it an agent never opens the folder.
3. In Jira, use a company-managed software space, because components, Affects versions and a
   shared workflow that sets the resolution are there only, and a space that later changes type
   loses its components. What differs in a team-managed space is in [jira-fields.md](jira-fields.md)
   section 4.
4. Make sure the space has the Fix versions field that [life-cycle.md](life-cycle.md) and
   [tickets.md](tickets.md) use to tie work to a release. A company-managed space already has it;
   in a team-managed space, turn on releases and versions
   ([Atlassian: enable releases and versions](https://support.atlassian.com/jira-software-cloud/docs/enable-releases-and-versions/)).
5. The practice links [git.md](../git/git.md) for the branch, commit and pull request names, and
   [refactoring.md](../refactoring/refactoring.md) for how existing work adopts a rule. Copy those
   folders too, or replace each link with your own rule for that topic, so no link in this folder
   points at a file your repository does not have.
6. Existing projects adopt these rules the way [refactoring.md](../refactoring/refactoring.md)
   section 7 says.

## The points to adapt

- The SLA numbers and severity levels: each company sets its own ([sla.md](sla.md)).
- The space type: this practice assumes a company-managed space ([jira-fields.md](jira-fields.md) section 4).
- Levels above the epic in Jira: what a team without them does is in [wbs.md](wbs.md) section 7.
- Where the risk register lives: one place per project ([risks.md](risks.md) section 2).
- PRINCE2 terms: PID for the charter, its own six threat responses ([risks.md](risks.md) section 5).
- The board's statuses: a team with no pre-production environment drops Pre-prod
  ([jira-workflow.md](jira-workflow.md) section 2).
- The sprint length, which sets every meeting's timebox ([meetings.md](meetings.md) section 2).
- What each status marker means, in ten words or fewer ([communication.md](communication.md) section 3).
- Who is on the escalation path, and how fast each level answers ([communication.md](communication.md) section 4).
- The engagement scale of the stakeholder register ([stakeholders.md](stakeholders.md) section 4).
- Which conditional artifacts a project keeps ([operating-system.md](operating-system.md) section 3).
