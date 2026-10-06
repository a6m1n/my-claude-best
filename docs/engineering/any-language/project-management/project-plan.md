# Project plan

The plan says how the project reaches the goal in the charter: what is built, when, by whom, and
how a change is handled. Read this file in the planning phase, after the [charter](charter.md)
is approved, and again each time the plan is reviewed. The phases are in
[life-cycle.md](life-cycle.md).

**Navigation**

- [1. What the plan is and when to write it](#1-what-the-plan-is-and-when-to-write-it)
- [2. What it holds](#2-what-it-holds)
- [3. The schedule](#3-the-schedule)
- [4. Baseline and change control](#4-baseline-and-change-control)
- [5. Plan near work in detail](#5-plan-near-work-in-detail)
- [6. Keep it current](#6-keep-it-current)
- [7. Sources](#7-sources)

## 1. What the plan is and when to write it

Write the plan in planning, after the charter. The charter gives the goal and the limits; the
plan can only be checked against them.

PMI defines the plan as "The document that describes how the project will be executed,
monitored and controlled, and closed." (PMI Lexicon, 2026) The PMP exam outline asks the project
manager to "Create an integrated project management plan" and to "Maintain the integrated project
management plan" (PMP exam content outline, July 2026).

## 2. What it holds

Keep the plan short: one page per part is enough for most projects, and a part with nothing to
say gets one line. A long plan is not kept current, and a stale plan misleads.

| Part | What it says | Where the detail lives |
|---|---|---|
| Scope | The deliverables and the work to make them | [wbs.md](wbs.md) |
| Development approach | Predictive, adaptive or hybrid, for each deliverable, and why | [life-cycle.md](life-cycle.md) section 4 |
| Schedule | Milestones, and dates for the work near now | Section 3; dependencies, estimates and the critical path in [schedule.md](schedule.md) |
| Roles and resources | Who owns which deliverable, who is on the team, who decides what | The WBS dictionary entries; [roles-and-decisions.md](roles-and-decisions.md) |
| Risks | The top risks and who owns them | [risks.md](risks.md) |
| Communication | Who hears what, how often, in which channel; the escalation path | [communication.md](communication.md) |
| Change control | How a change to scope, schedule or budget is approved | Section 4 |

As a cross-check, PRINCE2 7 defines the project plan as "a high-level plan showing the major
products of the project and when, how, and at what cost they will be delivered." (PeopleCert, 2023)
The table above covers the products, the when and the how; the cost is the budget the plan must
fit, which the charter holds ([charter.md](charter.md) section 2).

## 3. The schedule

A project schedule is "An output of a schedule model that presents linked activities with planned
dates, durations, milestones, and resources." (PMI Lexicon, 2026) A Gantt chart is "A bar chart of
schedule information where activities are listed on the vertical axis, dates are shown on the
horizontal axis, and activity durations are shown as horizontal bars placed according to start and
finish dates." (PMI Lexicon, 2026)

In Jira, keep the schedule in the Timeline, so the plan and the work are one thing, not two:

- Epics carry the dates. Their child work items, sprints, releases and dependency lines show on
  the same view. A Timeline shows work items from one space only.
- A milestone is a version (the Fix version field) with a planned release date. The Releases
  feature shows how much work in a version is done.
- A plan across several spaces needs Jira Plans ([wbs.md](wbs.md) section 7).

How to link the work that waits, estimate it and find the critical path is in
[schedule.md](schedule.md).

## 4. Baseline and change control

When the plan is approved, baseline the schedule; after that, change it only through change
control. Without a baseline nobody can say whether the project is late, and without change
control the baseline is rewritten to match the slip.

PMI defines the baseline as "The approved version of a work product that can be changed using
formal change control procedures and is used as the basis for comparison to actual results." Change
control is "A process whereby modifications to documents, deliverables, or baselines associated
with the project are identified, documented, approved, or rejected." (PMI Lexicon, 2026) The PMP
exam outline lists the task "Baseline a project schedule."

On the plan page, give each milestone (a version in Jira) three dates side by side:

- Original: the date approved at the first baseline. Nobody edits it.
- Baseline: the current approved date. It changes only when the sponsor approves a change request
  beyond the tolerance, and only for the milestones the request names and the ones linked to them.
- Now: the current forecast, or the version's release date in Jira. The project manager moves it
  inside the tolerance.

The three columns are this practice's own layout; the status against the baseline is that table
plus the open change requests (a filled table is in [project-example.md](project-example.md)
section 3). Measure the tolerance and the status markers ([communication.md](communication.md)
section 3) from Baseline, because an approved change is the plan the team now works to. PRINCE2 7
says "A project baseline is the current approved versions of the management products and project
products that are subject to change control." (PeopleCert, 2023), and PMI's Practice Standard for
Scheduling (2nd edition, 2011) rebaselines only the activities a change adds or changes and the ones
linked to them (section 3.3.5).

Keep Original, because a comparison with the latest baseline alone hides the slip before it. PMI's
2011 standard compares the schedule with "the original plan—the baseline—to see the slippage
compared to the original plan" (section 3.3.3), and GAO warns that comparing only with the most
recent approved baseline "provides an incomplete perspective" (GAO-20-195G, 2020).

Record each change after the baseline as a change request (a formal proposal to modify a document,
deliverable or baseline, in PMI's words) that holds the old date, the new date, who approved it and
why. Together the change requests are the revision log, so the history of each date needs no second
list. NASA's WBS Handbook asks for the same on a revised WBS baseline: the "change rationale and
project manager approval" ([wbs.md](wbs.md) section 7).

Never move Baseline to match progress, because then no marker can show a slip; GAO calls a baseline
that keeps moving to hide variances a "rubber baseline" (GAO-20-195G, 2020). A re-baseline is rare:
"A rebaselined schedule should be rare." (GAO-16-89G, 2015) At closure, compare the actual dates
with both Original and Baseline, so the sponsor sees the whole slip and the part each approved change
explains.

When you baseline the plan, agree a tolerance with the sponsor (for example, a milestone may move up
to one week from its Baseline date, so the sponsor's time goes to changes that move the goal, not
to routine slips). Inside it the project manager decides and records the change; only a change beyond it
goes to the sponsor. While a request waits, the team keeps working to the current baseline. Tolerance
comes from PRINCE2 7's principle "manage by exception" (PeopleCert, 2023;
[principles.md](principles.md) section 4); the one-week number is an example.

In Jira, one way is a work item per change request, with the old date, the new date, the approver
and the reason in its description and a link to the epic it changes. A change to the charter's goal,
scope boundary, budget or sponsor goes to the sponsor ([charter.md](charter.md) section 3).

Check: when Baseline changes, ask for the change request that holds the old date, the new date, the
approver and the reason.

## 5. Plan near work in detail

Plan the work of the next weeks in detail and the work further away at a higher level; fill in
the detail when that work comes near. Requirements change, so far-off detail is rewritten before
anyone uses it. Martin Fowler notes that in practice "the vast majority of software projects find
they need to change their requirements significantly within a few months."

PMI calls this "An iterative planning technique in which the work to be accomplished in the near
term is planned in detail, while the work in the future is planned at a higher level." (PMI
Lexicon, 2026, rolling wave planning) NASA does the same inside the WBS with work packages for
near-term work and planning packages for far-term work ([wbs.md](wbs.md) section 5). PRINCE2 7's
principle "manage by stages" plans a project "on a stage-by-stage basis", and the next stage plan
is prepared at the stage boundary, "at, or close to, the end of each stage" (PeopleCert, 2023).

## 6. Keep it current

Review the plan with the team at a fixed rhythm and adjust it. The plan is a tool for the next
decision; an out-of-date plan gets ignored, and then it has no use. Atlassian's six steps for a
plan end with "Share, Gather Feedback, And Adjust The Project Plan As Necessary", and the PMP
outline asks the project manager to maintain the plan.

Pick the rhythm when you approve the plan and write it into the plan, for example "every second
Monday, 30 minutes". No standard sets the number; choose one short enough that a review finds few
changes, and change it if reviews find many.

## 7. Sources

- [PMI Lexicon of Project Management Terms, v5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: project management plan, project schedule, Gantt chart, baseline, change control, change request, rolling wave planning.
- [PMP examination content outline](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/new-pmp-examination-content-outline-2026.pdf), July 2026 exam: create, maintain the plan; baseline a project schedule.
- PeopleCert, [PRINCE2 7 Foundation Quick Reference Guide](https://www.nilc.co.uk/wp-content/uploads/2023/10/PRINCE2-Quick-Reference-Guide.pdf), 2023, a PeopleCert document hosted by a training organisation: the project plan, the project baseline, the principles "manage by stages" and "manage by exception", managing a stage boundary.
- PMI, [Practice Standard for Scheduling, 2nd edition](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/practice-standard-scheduling.pdf), 2011, sections 3.3.3 and 3.3.5: comparing with the original plan; rebaselining only new or changed activities and the ones linked to them. The 3rd edition (2019) was not read.
- GAO, [Schedule Assessment Guide, GAO-16-89G](https://www.gao.gov/assets/gao-16-89g.pdf), December 2015, p. 140: a rebaselined schedule should be rare.
- GAO, [Cost Estimating and Assessment Guide, GAO-20-195G](https://www.gao.gov/assets/gao-20-195g.pdf), March 2020, pp. 15-16 and 236: comparing only with the latest baseline; the "rubber baseline".
- [NASA WBS Handbook, Rev E](https://www.nasa.gov/wp-content/uploads/2025/06/nasa-wbs-handbook.pdf), June 2025, section 3.3.6: revision rationale and approval.
- [Martin Fowler, Waterfall process](https://martinfowler.com/bliki/WaterfallProcess.html), 2019-11-13.
- [Atlassian, write an effective project plan](https://www.atlassian.com/blog/project-management/write-an-effective-project-plan), 2023-07-20.
- Jira Timeline: [what is the timeline](https://support.atlassian.com/jira-software-cloud/docs/what-is-the-roadmap/); versions and releases: [enable releases and versions](https://support.atlassian.com/jira-software-cloud/docs/enable-releases-and-versions/). Both undated.
