# The project's operating system

How the artifacts of this folder work as one loop, the rhythm that keeps them current, and how much
of it a project of a given size keeps. Read this file when you start a project and choose its
artifacts, and when someone asks what happens when.

**Navigation**

- [1. One loop](#1-one-loop)
- [2. The rhythm](#2-the-rhythm)
- [3. Tailor it to the project's size](#3-tailor-it-to-the-projects-size)
- [4. Sources](#4-sources)

## 1. One loop

Run the project as one loop: plan, deliver, inspect what happened, decide, adapt the plan. No
standard read for this practice draws the artifacts of this folder into one loop, so the loop below
is this practice's own; its two halves come from the owners.

- **The stage half, from PRINCE2 7.** "A PRINCE2 project is planned, monitored, and controlled on a
  stage-by-stage basis." At each stage boundary the board reviews "the success of the current stage",
  the next stage plan and the updated project plan, and confirms "continued business justification
  and acceptability of the risks"; it "authorizes a stage by reviewing the performance of the current
  stage and approving the stage plan for the next stage", and may close the project early "if the
  business case is no longer valid" (PeopleCert, 2023). In this practice a stage is a project phase
  ([life-cycle.md](life-cycle.md) section 2), and the board is the sponsor.
- **The sprint half, from Scrum.** The Scrum Guide founds Scrum on empiricism, "knowledge comes from
  experience and making decisions based on what is observed", and "combines four formal events for
  inspection and adaptation within a containing event, the Sprint."

```
 charter ──> roles, stakeholders ──> scope (WBS) ──> plan, schedule, risks
    ^                                                       │
    │                                                       v
 decisions <── status update <── releases <── work in Jira (sprints or flow)
    │
    └──> retrospective ──> the plan and the way of working change
```

The diagram is good because it shows that the status update and the decisions feed back into the
plan, which is the point of a loop, and that the charter changes only through a decision.

| Step | Artifact | Owning file | It feeds |
|---|---|---|---|
| Authorize | Charter | [charter.md](charter.md) | Everything below; changes only through the sponsor |
| Organise | Roles, RACI, decider table; stakeholder register | [roles-and-decisions.md](roles-and-decisions.md), [stakeholders.md](stakeholders.md) | Who does, decides and hears what |
| Scope | WBS and its dictionary | [wbs.md](wbs.md) | The epics in Jira |
| Plan | Plan, development approach, schedule, risk register | [project-plan.md](project-plan.md), [life-cycle.md](life-cycle.md) section 4, [schedule.md](schedule.md), [risks.md](risks.md) | The baseline and the tolerance |
| Deliver | Work items on the board, sprints or a flow | [tickets.md](tickets.md), [jira-work-item-types.md](jira-work-item-types.md), [jira-fields.md](jira-fields.md), [jira-workflow.md](jira-workflow.md), [meetings.md](meetings.md) | Done work in production |
| Release | Version, go or no-go, rollback plan | [release.md](release.md), [rollback-plan.md](rollback-plan.md) | What users have |
| Report | Weekly status update; an exception note | [communication.md](communication.md) | The sponsor's decisions |
| Decide | Decision log; change requests | [roles-and-decisions.md](roles-and-decisions.md) section 7, [project-plan.md](project-plan.md) section 4 | A changed plan |
| Learn | Retrospective; lessons at closure | [meetings.md](meetings.md) section 8, [life-cycle.md](life-cycle.md) section 2 | How the next sprint, stage or project runs |

PRINCE2 7's principle for the last step: "A PRINCE2 project team actively seeks, records, and
implements improvements as a result of relevant lessons learned from prior projects and throughout
the life of the project." (PeopleCert, 2023)

## 2. The rhythm

Hold each step of the loop at a fixed rhythm, and write the rhythm into the plan. PRINCE2 7 splits
its controls in two: time-driven controls run "at predefined periodic intervals", such as the
highlight report, and event-driven controls run "when a specific event occurs", such as "the end of a
stage" or "the creation of an exception report" (PeopleCert, 2023). The table keeps that split:

| When | What happens | What it inspects or changes | Owning rule |
|---|---|---|---|
| Every working day | Daily Scrum, or a walk of the board | "to inspect progress toward the Sprint Goal and adapt the Sprint Backlog" (Scrum Guide) | [meetings.md](meetings.md) section 5 |
| Every week | The status update; a look at the top risks and the work in progress | The forecast against the baseline; the top risks; each person's work in progress | [communication.md](communication.md) section 2, [risks.md](risks.md) section 7, [principles.md](principles.md) section 3 |
| Every plan review | The plan review, at the rhythm the plan names | Change requests; planning packages to split | [project-plan.md](project-plan.md) section 6 |
| Every sprint | Planning, refinement, review, retrospective | The Sprint Review "to inspect the outcome of the Sprint and determine future adaptations"; the retrospective "to plan ways to increase quality and effectiveness" (Scrum Guide) | [meetings.md](meetings.md) section 2 |
| Every release | Go or no-go; the rollback plan rehearsed | The release criteria | [release.md](release.md) section 3 |
| When the forecast breaks tolerance | The exception note; the sponsor's decision | The plan, through a change request | [communication.md](communication.md) section 5 |
| Every phase end | The approval of the phase's artifact; the whole risk register; the stakeholder register | Whether to go on | [life-cycle.md](life-cycle.md) section 2, [risks.md](risks.md) section 7, [stakeholders.md](stakeholders.md) section 6 |
| Closure | Acceptance against the success criteria; lessons with owners | The result against the charter | [life-cycle.md](life-cycle.md) section 2 |

A team without sprints keeps the daily and the weekly rows and replaces the sprint row by the
cadence of [meetings.md](meetings.md) section 9; the Kanban Guide asks for no fixed cadence, so the
team writes its own.

## 3. Tailor it to the project's size

Every project keeps the artifacts the rule files ask for without a condition, each as short as
the project allows: the charter, the stakeholder register, the named roles with the decider table
and the decision log, the RACI matrix for the deliverables, the plan with its baseline, the risk
register, the weekly status update with the escalation path, and, for each release, the go or
no-go decision and the rollback plan. On a small project, one team for a few months, each of them
fits on one page or in a few lines. Anything beyond them and the conditional artifacts below
follows the "just enough" rule of [principles.md](principles.md) section 4.

Keep the conditional artifacts when their condition holds; each condition is owned by the file
named. A larger project, with several teams or a date set outside the team, meets more of them:

| Artifact | Kept when | Owning rule |
|---|---|---|
| The critical path | A date is fixed and work waits on other work | [schedule.md](schedule.md) section 3 |
| A contingency plan | An open threat has an impact of 4 or 5 | [risks.md](risks.md) section 6 |
| A DACI page | A decision is hard to undo or crosses teams | [roles-and-decisions.md](roles-and-decisions.md) section 6 |
| An exception note | The status marker turns Off track | [communication.md](communication.md) section 5 |
| Jira Plans | The work spans several spaces or teams | [schedule.md](schedule.md) section 4 |

PMI's tailoring steps include "Adjust based on size, criticality, and other factors", PRINCE2 7
tailors "to suit the project environment, size, complexity, importance, delivery method, team
capability, and level of risk" (PeopleCert, 2023), and the PMP exam outline asks the project
manager to "Identify and tailor needed artifacts." The table is this practice's own. It is good
because each condition is one a reader can check against the project, not a size label.

Check: in the plan, find each conditional artifact the project keeps and the condition that holds
for it.

## 4. Sources

- PeopleCert, [PRINCE2 7 Foundation Quick Reference Guide](https://www.nilc.co.uk/wp-content/uploads/2023/10/PRINCE2-Quick-Reference-Guide.pdf), 2023, and [Practitioner sample paper 1 with rationales](https://prince2.wiki/downloads/p2p-a1.pdf), official training PDFs hosted by training organisations: manage by stages, the stage boundary, time-driven and event-driven controls, learn from experience, tailoring.
- [The Scrum Guide](https://scrumguides.org/scrum-guide.html), November 2020: empiricism, the events and what each inspects.
- [Kanban Guide](https://kanbanguides.org/english/), version 2025.5: no fixed cadence.
- PMI, ["Tailoring"](https://www.pmi.org/-/media/pmi/documents/public/pdf/pmbok-standards/pmi-tailoring.pdf), PMBOK 7 material, 2021: the tailoring steps.
- [PMP Examination Content Outline, July 2026 exam](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/new-pmp-examination-content-outline-2026.pdf), PMI, 2026: "Identify and tailor needed artifacts."
