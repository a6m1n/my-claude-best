# Life cycle

The two life cycles of a project: the five phases the project passes through, and the seven SDLC
phases each release passes through inside the execution phase. Read it when you start a project, a
phase or a release, and when you decide whether a phase is over.

**Navigation**

- [1. Two life cycles](#1-two-life-cycles)
- [2. The five project phases](#2-the-five-project-phases)
- [3. The SDLC inside execution](#3-the-sdlc-inside-execution)
- [4. Sources](#4-sources)

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
| Execution | The team builds and releases the work, one release at a time | Releases ([tickets.md](tickets.md), [rollback-plan.md](rollback-plan.md)) | The team, when the Definition of Done is met; the rollback plan names who can stop it |
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
artifacts that fix the goal and the baseline, and the team approves the releases it runs, against its
Definition of Done ([tickets.md](tickets.md) section 2).

This practice's own Closure rule: the sponsor accepts the result in writing against the charter's
success criteria, not against the plan, so the result is judged by the goal and not by the schedule.
The team holds a retrospective and records each lesson with an owner and a date. The epics are
closed, and so are the open rows of the risk register. A filled closure is in
[project-example.md](project-example.md) section 9.

Check: before you start the next phase, find the approval of the current phase's artifact (a
comment, a status or a signature on the page). If you cannot find it, the phase is not over.

## 3. The SDLC inside execution

Run each release through the seven SDLC phases below, and give each phase one home in Jira, so the
state of a release can be read from Jira alone. The mapping to Jira is this practice's own: no
source names one. It uses Jira's documented features (epics, work items, versions).

| SDLC phase | What happens | Its home in Jira |
|---|---|---|
| Planning | The release is scoped: which epics and work items it holds | Epics and work items in the backlog, tied to a version through the Fix versions field |
| Feasibility analysis | The team decides whether the work can be done, at what cost and risk | A work item under the epic that ends with a written yes or no on the epic |
| System design | The team decides how the system will do it | A Confluence page linked to the epic |
| Implementation | The team writes the code | Work items, each with a branch and a pull request ([tickets.md](tickets.md); names by [git.md](../git/git.md) sections 2 to 4) |
| Testing | The team shows the work meets its criteria | The Definition of Done on each work item |
| Deployment | The release goes live | The Fix version marked released, with the [rollback plan](rollback-plan.md) ready |
| Maintenance | The team fixes what fails in use | Bugs as work items |

A version and the Fix versions field are explained in [tickets.md](tickets.md) section 5, and the
Definition of Done in [tickets.md](tickets.md) section 2. A Confluence page can be linked to an epic
(Atlassian, "Link a Confluence page to an epic").

The phases are concerns a release passes through, not a strict waterfall. Run them many times,
because requirements change ([project-plan.md](project-plan.md) section 5 has the evidence). Winston Royce's 1970 paper, the one people cite as the origin of the waterfall, says of the
pure sequence: "I believe in this concept, but the implementation described above is risky and
invites failure" (quoted from a web transcription of the 1970 paper, not from the print copy).

## 4. Sources

- [Atlassian, "The 5 phases of the project management life cycle"](https://www.atlassian.com/work-management/project-management/phases), undated, read 2026-10-05: the five stages, quoted from PMBOK.
- [PMBOK Guide eighth edition, table of contents](https://www.pmi.org/-/media/pmi/documents/public/pdf/publications/pmbok-guide-eighth-edition_table-of-contents.pdf), PMI, 2025: the Focus Areas (section 4.5) and project phases (section 4.1). The full text is paid, so this folder takes its definitions from the free PMI Lexicon.
- [Atlassian, "Software development life cycle (SDLC)"](https://www.atlassian.com/agile/software-development/sdlc), undated, read 2026-10-05: the seven phases.
- [PMI Lexicon of Project Management Terms, version 5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: sponsor.
- [PMP Examination Content Outline, July 2026 exam](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/new-pmp-examination-content-outline-2026.pdf?rev=b618cf45573e4276a54151e7636c97bf), PMI, 2026: change control, lessons learned.
- [Atlassian, "What is a version"](https://support.atlassian.com/jira-software-cloud/docs/what-is-a-version/) and [enable releases and versions](https://support.atlassian.com/jira-software-cloud/docs/enable-releases-and-versions/), undated: versions and the Fix versions field.
- [Atlassian, "Link a Confluence page to an epic"](https://support.atlassian.com/jira-software-cloud/docs/link-a-confluence-page-to-an-epic/), undated.
- [Royce, "Managing the Development of Large Software Systems", 1970](http://arafatm.com/programming/managing-the-development-of-large-software-systems-royce-1970), a web transcription.
