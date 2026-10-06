# Life cycle

The two life cycles of a project: the five phases the project passes through, and the seven SDLC
phases each release passes through inside the execution phase. Read it when you start a project, a
phase or a release, and when you decide whether a phase is over.

**Navigation**

- [1. Two life cycles](#1-two-life-cycles)
- [2. The five project phases](#2-the-five-project-phases)
- [3. The SDLC inside execution](#3-the-sdlc-inside-execution)
- [4. Pick the development approach](#4-pick-the-development-approach)
- [5. Sources](#5-sources)

## 1. Two life cycles

Plan a project as five phases, and plan each release as seven SDLC phases. Keep the two terms
apart: the five phases belong to the project, and the seven belong to one release of software. The
reason: a project has many releases, so the two cycles run at different speeds, and mixing them
makes a release look like a phase.

- Atlassian, quoting PMBOK, gives the project life cycle five stages: "Initiation, Planning,
  Execution, Monitoring, Closure".
- Atlassian gives the software development life cycle seven phases: "planning, feasibility
  analysis, system design, implementation, testing, deployment, and maintenance".

When someone says a project has five phases, they most likely mean the five stages Atlassian quotes
from PMBOK (initiation, planning, execution, monitoring, closure). PMBOK 8 calls them its five Focus
Areas, Initiating, Planning, Executing, Monitoring and Controlling, and Closing (table of contents,
section 4.5), and covers project phases in a section of their own (4.1). This practice keeps those
five for the project and Atlassian's seven for each release, so feasibility analysis, system design
and maintenance keep their own Jira homes (section 3).

```
Project   Initiation -> Planning -> Execution ------------------------> Closure
                                    |  release 1 | release 2 | ...  |
                                    |  7 SDLC    | 7 SDLC    |      |
          Monitoring runs alongside, from the baseline to Closure
```

The diagram is good because it shows the seven SDLC phases repeating inside one project phase,
which is the point of this section.

## 2. The five project phases

End a phase when its artifact is approved, not on a date. The reason: the next phase builds on that
artifact, and a date can pass with the artifact unfinished. A phase that runs past its date is a
schedule change for [project-plan.md](project-plan.md), and a phase that ends on its date without
its artifact is not ended.

| Phase | What happens | It ends with | Who approves |
|---|---|---|---|
| Initiation | The goal, the scope in outline, the sponsor and the project manager's authority are written down | The charter ([charter.md](charter.md)) | The sponsor, who issues it |
| Planning | The work is broken down, scheduled and risk-assessed, and the plan is baselined | The plan, the WBS and the risk register ([project-plan.md](project-plan.md), [wbs.md](wbs.md), [risks.md](risks.md)) | The sponsor approves the baseline |
| Execution | The team builds and releases the work, one release at a time | Releases ([tickets.md](tickets.md), [rollback-plan.md](rollback-plan.md)) | One named person decides go or no-go for each release ([release.md](release.md) section 3) |
| Monitoring | Status is compared with the baseline, changes go through change control, the register is reviewed, the SLA is met | The status against the baseline ([project-plan.md](project-plan.md) section 4), and the decisions on change requests ([sla.md](sla.md) for the SLA) | The sponsor decides a change beyond the agreed tolerance ([project-plan.md](project-plan.md) section 4) |
| Closure | The sponsor accepts the result, and the team looks back at how the work went | Acceptance and the lessons learned | The sponsor accepts |

Monitoring is not a step after execution. It starts when the plan is baselined and runs alongside
execution until closure; the table shows it in its own row because it has its own artifact.
Execution ends when the last release the plan names is live, and Monitoring ends with Closure, so
the check below applies at the end of initiation, planning and execution.

What the phases and their artifacts rest on:

- After planning, a change to scope or schedule is a change request. The baseline and change
  control are defined in [project-plan.md](project-plan.md) section 4.
- The PMP exam outline names the change control process ("Execute the change control process.")
  and ends a project with "final lessons learned, retrospectives". Closure therefore holds a
  retrospective.

The assignment of who approves each phase is this practice's own, built on the PMI definitions: the
sponsor is "accountable for enabling success" (PMI Lexicon, 2026), so the sponsor approves the
artifacts that fix the goal and the baseline. A release has its go or no-go decider instead
([release.md](release.md) section 3), because the Definition of Done ends with the production
deploy ([tickets.md](tickets.md) section 2), so it cannot be the gate before the deploy.

This practice's own Closure rule: the sponsor accepts the result in writing against the charter's
success criteria, not against the plan, so the result is judged by the goal and not by the schedule.
The team holds a retrospective ([meetings.md](meetings.md) section 8) and records each lesson with
an owner and a date. The epics are closed.

Give each open risk a named owner for after the project and a follow-on action, then mark its row
handed over, so no risk is dropped when the team moves on. PRINCE2 7 asks the same of closing a
project: "ensure provision has been made to address all open issues and risks, with follow-on
action recommendations" (PeopleCert, 2023). A filled closure is in
[project-example.md](project-example.md) section 9.

Check: before you start the next phase, find the approval of the current phase's artifact (a
comment, a status or a signature on the page). If you cannot find it, the phase is not over.

## 3. The SDLC inside execution

Run each release through the seven SDLC phases below, and give each phase one home in Jira, so the
state of a release can be read from Jira alone. The mapping to Jira is this practice's own: no
source names one. It uses Jira's documented features (epics, work items, versions).

| SDLC phase | What happens | Its home in Jira |
|---|---|---|
| Planning | The release is scoped and its requirements are gathered: which epics and work items it holds, and what each must do | Epics and work items in the backlog, tied to a version through the Fix versions field; each work item's requirements are its description and acceptance criteria ([tickets.md](tickets.md) section 2) |
| Feasibility analysis | The team decides whether the work can be done, at what cost and risk | A work item under the epic that ends with a written yes or no on the epic |
| System design | The team decides how the system will do it | A Confluence page linked to the epic |
| Implementation | The team writes the code | Work items, each with a branch and a pull request ([tickets.md](tickets.md); names by [git.md](../git/git.md) sections 2 to 4) |
| Testing | The team shows the work meets its criteria | The Definition of Done on each work item |
| Deployment | The release goes live | The Fix version marked released after the go or no-go decision of [release.md](release.md) section 3, with the [rollback plan](rollback-plan.md) ready |
| Maintenance | The team fixes what fails in use | Bugs as work items |

Atlassian puts requirements in planning: "Project goals, objectives, and requirements are gathered
and documented during this phase." PMI defines a requirement as "A condition or capability that is
necessary to be present in a product, service, or result to satisfy a business need." (PMI Lexicon,
2026)

A version and the Fix versions field are explained in [tickets.md](tickets.md) section 5, and the
Definition of Done in [tickets.md](tickets.md) section 2. A Confluence page can be linked to an epic
(Atlassian, "Link a Confluence page to an epic").

The phases are concerns a release passes through, not a strict waterfall. Run them many times,
because requirements change ([project-plan.md](project-plan.md) section 5 has the evidence). Winston Royce's 1970 paper, the one people cite as the origin of the waterfall, says of the
pure sequence: "I believe in this concept, but the implementation described above is risky and
invites failure" (quoted from a web transcription of the 1970 paper, not from the print copy).

## 4. Pick the development approach

In planning, pick the development approach for each deliverable of the WBS, and write it, with the
reason, in the plan ([project-plan.md](project-plan.md) section 2). PMI names three approaches (PMI
Lexicon, 2026):

| Approach | PMI's definition | It fits when |
|---|---|---|
| Predictive | "A development approach in which the project scope, time, and cost are determined in the early phases of the life cycle." | The requirements are firm, the team is stable and the risk is low |
| Adaptive | "A development approach in which the requirements are subject to a high level of uncertainty and volatility and are likely to change throughout the project." | The work is complex, it changes often, or stakeholders see the scope differently |
| Hybrid | "A combination of elements from both adaptive and predictive approaches that is useful when there is uncertainty or risk around the requirements." | Some deliverables are fixed and others are not |

The Predictive cell of the "It fits when" column is the Agile Practice Guide's, the Adaptive cell
comes from its text on iterative life cycles (section 3.1.2), and the Hybrid cell is this practice's
own: "Predictive life cycles expect to take
advantage of high certainty around firm requirements, a stable team, and low risk", and an iterative
life cycle suits "when complexity is high, when the project incurs frequent changes, or when the
scope is subject to differing stakeholders' views" (PMI and Agile Alliance, first edition, 2017; a
second edition came out in 2026 and was not read for this practice).

Decide per deliverable, not once for the whole project. The Agile Practice Guide says "It is not
necessary to use a single approach for an entire project." The PMP exam outline asks the project
manager to "Assess project needs, complexity, and magnitude" and then recommend the approach. In a
software project this usually means that the software runs adaptive, in sprints or a Kanban flow,
and the parts fixed by a contract or a date, such as a provider contract or a migration window, are
planned predictively, as milestones ([project-plan.md](project-plan.md) section 3). That reading is
this practice's own.

Inside the adaptive part, pick Scrum when the team can agree a Sprint Goal for each sprint, and a
Kanban flow when it cannot because the work arrives unplanned, as support and operations work does
(this practice's own rule). The Scrum Guide gives every sprint one Sprint Goal, and the Kanban Guide
has no sprints. The meetings of each are in [meetings.md](meetings.md), sections 2 and 9.

Pick by the criteria above, not by a success rate: no reviewed study found for this practice
compares the approaches' success head to head. A hybrid approach is also what many teams already
run: in the HELENA survey of 69 practitioners, "Most combinations follow a pattern in which a
traditional process model serves as framework in which several fine-grained (agile) practices are
plugged in" (2017). The survey measured what teams use, not what works better.

Check: open the plan and find, for each deliverable, its approach and the reason.

## 5. Sources

- [Atlassian, "The 5 phases of the project management life cycle"](https://www.atlassian.com/work-management/project-management/phases), undated, read 2026-10-05: the five stages, quoted from PMBOK.
- [PMBOK Guide eighth edition, table of contents](https://www.pmi.org/-/media/pmi/documents/public/pdf/publications/pmbok-guide-eighth-edition_table-of-contents.pdf), PMI, 2025: the Focus Areas (section 4.5) and project phases (section 4.1). The full text is paid, so this folder takes its definitions from the free PMI Lexicon.
- [Atlassian, "Software development life cycle (SDLC)"](https://www.atlassian.com/agile/software-development/sdlc), undated, read 2026-10-05: the seven phases; requirements in planning.
- [PMI Lexicon of Project Management Terms, version 5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: sponsor; requirement; predictive, adaptive and hybrid approach.
- [PMP Examination Content Outline, July 2026 exam](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/new-pmp-examination-content-outline-2026.pdf?rev=b618cf45573e4276a54151e7636c97bf), PMI, 2026: change control, lessons learned, recommending a development approach.
- PeopleCert, [PRINCE2 7 Foundation Quick Reference Guide](https://www.nilc.co.uk/wp-content/uploads/2023/10/PRINCE2-Quick-Reference-Guide.pdf), 2023, a PeopleCert document on a third-party host: closing a project, open issues and risks with follow-on action recommendations.
- PMI and Agile Alliance, [Agile Practice Guide](https://www.agilealliance.org/wp-content/uploads/2021/02/AgilePracticeGuide.pdf), first edition, 2017: when predictive and iterative life cycles fit; one project may mix approaches.
- Kuhrmann et al., ["Hybrid software and system development in practice: waterfall, scrum, and beyond"](https://dl.acm.org/doi/pdf/10.1145/3084100.3084104) (the HELENA study), ICSSP 2017: hybrid use, not success.
- [The Scrum Guide](https://scrumguides.org/scrum-guide.html), 2020, and the [Kanban Guide](https://kanbanguides.org/english/), version 2025.5: the Sprint Goal; no sprints in Kanban.
- [Atlassian, "What is a version"](https://support.atlassian.com/jira-software-cloud/docs/what-is-a-version/) and [enable releases and versions](https://support.atlassian.com/jira-software-cloud/docs/enable-releases-and-versions/), undated: versions and the Fix versions field.
- [Atlassian, "Link a Confluence page to an epic"](https://support.atlassian.com/jira-software-cloud/docs/link-a-confluence-page-to-an-epic/), undated.
- [Royce, "Managing the Development of Large Software Systems", 1970](http://arafatm.com/programming/managing-the-development-of-large-software-systems-royce-1970), a web transcription.
