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

- [principles.md](principles.md): what project management is for, what it never does (micromanage,
  track for its own sake), how to see and limit workload, which standard names which artifact, and
  why Jira is the tool. Read it before you open a project, and when you doubt whether an artifact
  or a report is worth its cost.
- [life-cycle.md](life-cycle.md): the five phases of a project, the artifact each one ends with and
  who approves it, and the seven SDLC phases each release passes through, with their Jira homes.
  Read it when you start a project, a phase or a release, and when you decide whether a phase is
  over.
- [charter.md](charter.md): the project charter, what it holds, who issues it, and how it differs
  from the plan. Read it when you open a project.
- [project-plan.md](project-plan.md): the project plan, its schedule (the Gantt chart, the Jira Timeline), its baseline and how it
  stays current. Read it when you plan a project, or change its scope or schedule.
- [wbs.md](wbs.md): the work breakdown structure, its rules, and how it maps to epics, work items
  and subtasks in Jira. Read it when you break the scope into work.
- [risks.md](risks.md): the risk register, the scoring, the five ways to respond to a threat (mitigation is one of them)
  and the review. Read it when you open the register, add a risk or review the register.
- [tickets.md](tickets.md): what a work item holds, how big it is, how it links to a branch, a pull
  request and a release. Read it when you write or triage a work item.
- [sla.md](sla.md): what an SLA is, how it differs from an SLO, severity levels, and what "fixed"
  means in it. Read it when you agree or change an SLA.
- [rollback-plan.md](rollback-plan.md): the rollback plan of a release, its trigger, owner and
  steps, and how data changes are handled. Read it when you plan a release.
- [project-example.md](project-example.md): one small project with every artifact filled in, with
  the reason next to each. Read it when you write your first charter, plan or register.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/any-language/project-management/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you open a project, plan or change its
   scope or schedule, write or triage a work item, plan a release or its rollback, or agree an SLA,
   read `docs/engineering/any-language/project-management/README.md` and the file it points to."
   Without it an agent never opens the folder.
3. In Jira, turn on releases and versions. This adds the Fix versions field that
   [life-cycle.md](life-cycle.md) and [tickets.md](tickets.md) use to tie work to a release
   ([Atlassian: enable releases and versions](https://support.atlassian.com/jira-software-cloud/docs/enable-releases-and-versions/)).
4. The practice links [git.md](../git/git.md) for the branch, commit and pull request names, and
   [refactoring.md](../refactoring/refactoring.md) for how existing work adopts a rule. Copy those
   folders too, or replace each link with your own rule for that topic.
5. Existing projects adopt these rules the way [refactoring.md](../refactoring/refactoring.md)
   section 7 says.

## The points to adapt

- The SLA numbers and severity levels: each company sets its own ([sla.md](sla.md)).
- Levels above the epic in Jira: what a team without them does is in [wbs.md](wbs.md) section 7.
- Where the risk register lives: one place per project ([risks.md](risks.md) section 2).
- PRINCE2 terms: PID for the charter, its own six threat responses ([risks.md](risks.md) section 5).
