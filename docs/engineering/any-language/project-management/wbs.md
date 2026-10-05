# Work breakdown structure

The work breakdown structure (WBS) cuts the project's scope into deliverables and then into
work you can estimate and own. Read this file in the planning phase, when you turn the
[charter](charter.md)'s scope into the scope part of the [plan](project-plan.md). The work
items it leads to are in [tickets.md](tickets.md).

**Navigation**

- [1. What it is and when to make it](#1-what-it-is-and-when-to-make-it)
- [2. The 100% rule](#2-the-100-rule)
- [3. Deliverables, not phases or teams](#3-deliverables-not-phases-or-teams)
- [4. How deep](#4-how-deep)
- [5. Near work now, far work later](#5-near-work-now-far-work-later)
- [6. The WBS dictionary](#6-the-wbs-dictionary)
- [7. In Jira](#7-in-jira)
- [8. Sources](#8-sources)

## 1. What it is and when to make it

Make the WBS in planning, from the scope in the charter. Without it the plan has no list of
what the project must deliver, and gaps show up in execution.

PMI defines it as "A hierarchical decomposition of the total scope of work to be carried out by
the project team to accomplish the project objectives and create the required deliverables."
(PMI Lexicon, 2026) The PMP exam outline names the same step "Break down scope." Scrum has no WBS.

## 2. The 100% rule

For every element, make its children add up to all of its work, and keep work out of the WBS
that is not in the project scope. A gap in the WBS is work nobody planned; extra work is scope
creep. Both show up as a mismatch between the WBS and the scope.

NASA's WBS Handbook states the two halves: "Work scope not contained in the project WBS should
not be considered part of the project." (section 2.1) and "The WBS should never contain
unauthorized work scope." (section 3.3.5) PMI's definition says "total scope". The name "100%
rule" is common usage; NASA does not use it, and this file quotes no PMI sentence for it.

Check: when you finish the WBS, read each element and ask whether its children cover all of it
and nothing outside the charter's scope.

## 3. Deliverables, not phases or teams

Name each top-level element after a thing the project delivers, not after a phase, a function
or a team. A phase or a team is not something the sponsor can accept, so a WBS built from
them cannot show what is missing.

NASA: "Design, Engineering, Manufacturing, Phase A, Pipe Fitters, and Direct Labor are not
products and typically should not be used for WBS element sub-divisions." (section 3.5.2)
Atlassian describes the same as a deliverable-based WBS, which "breaks the project into major
deliverables instead of phases."

| Avoid (phases and teams) | Use (deliverables) |
|---|---|
| Design, Build, Test | Payment provider integration, Routing flag, Payment records migration |
| Backend team, QA team | Checkout payments, Payment records |

The table is good because every right-hand item can be accepted or rejected by the sponsor. The
first row names the epics of [project-example.md](project-example.md) section 4.

## 4. How deep

Stop splitting when each lowest element can be estimated, owned and managed. That element is a
work package: "The work defined at the lowest level of the work breakdown structure for which
cost, effort, duration, and resources are estimated and managed." (PMI Lexicon, 2026) NASA says
a branch "only needs to be subdivided as far as needed to allow for adequate management, insight,
and control." (section 3.3.4) Going deeper than that is tracking for its own sake.

The "8/80 rule" (a work package takes 8 to 80 hours) is a rule of thumb. NASA's handbook has no
such limit, and no standard owns it; do not cite it as one.

## 5. Near work now, far work later

Detail near-term work as work packages, and keep far-term work as planning packages that you
split when they come near. Requirements change, so detail made too early is rewritten.

NASA: "A WP provides further detail on work content that is considered near-term, while a PP
[planning package] defines far-term work at a summary level." (section 3.3.4) This is rolling wave
planning, as in [project-plan.md](project-plan.md) section 5.

## 6. The WBS dictionary

Write one entry per element: its scope, its owner and its done criteria. Without the entry two
people read the element two ways. PMI calls it "A document that provides detailed deliverable,
activity, scheduling, cost, and resource information about each component in the work breakdown
structure." (PMI Lexicon, 2026) NASA adds that it is a controlled document the project manager
maintains (sections 3.2, 3.4.4).

Keep it simple: the epic's description can be the entry. Three lines are enough. A filled
dictionary is in [project-example.md](project-example.md) section 4.

## 7. In Jira

This mapping is this practice's own. Atlassian publishes no mapping from WBS to Jira, so it is
built from Jira's work item hierarchy: epics, then work items (story, task, bug), then
subtasks. Atlassian's user-story guide says epics break into stories and several epics form an
initiative.

| WBS part | Jira |
|---|---|
| The project goal | The Jira project, or an initiative level in Jira Plans (Premium) |
| A deliverable | An epic |
| A work package | A work item: story, task or bug |
| A work package split into several work items | Work items under the same epic, each naming the work package in its summary |
| A step inside one work item | A subtask, and only then |

A work package too big for one work item becomes several work items;
[tickets.md](tickets.md) section 3 says how to size them and section 2 how to write them. Levels above the epic need Jira Plans on a Premium or Enterprise
licence, so a team without it stays with project, epic and work item.

After the baseline, a change to the WBS records its rationale and the approval, as NASA asks:
"formal documentation of the revision ... to include the associated change rationale and project
manager approval." (section 3.3.6) Use the change request of [project-plan.md](project-plan.md)
section 4.

## 8. Sources

- [PMI Lexicon of Project Management Terms, v5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: WBS, work package, WBS dictionary.
- [NASA WBS Handbook, Rev E](https://www.nasa.gov/wp-content/uploads/2025/06/nasa-wbs-handbook.pdf), June 2025: sections 2.1, 3.2, 3.3.4, 3.3.5, 3.3.6, 3.4.4, 3.5.2.
- [PMP examination content outline](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/new-pmp-examination-content-outline-2026.pdf), July 2026 exam: "Break down scope."
- [Atlassian, work breakdown structure](https://www.atlassian.com/work-management/project-management/work-breakdown-structure), undated, read 2026-10-05.
- [Atlassian, user stories](https://www.atlassian.com/agile/project-management/user-stories), undated.
- Jira hierarchy: [work types](https://support.atlassian.com/jira-cloud-administration/docs/what-are-issue-types/) and [issue type hierarchy](https://support.atlassian.com/jira-cloud-administration/docs/configure-the-issue-type-hierarchy/), both undated.
