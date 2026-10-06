# Schedule

The schedule puts the work of the WBS in order, gives it durations, and shows which work sets the
end date. Read this file in planning, after the [WBS](wbs.md), and again when a dependency or an
estimate changes. Where the schedule lives in Jira, and how its baseline is kept, is in
[project-plan.md](project-plan.md) sections 3 and 4.

**Navigation**

- [1. Link the work that waits](#1-link-the-work-that-waits)
- [2. Estimate in ranges](#2-estimate-in-ranges)
- [3. Find the critical path when a date is fixed](#3-find-the-critical-path-when-a-date-is-fixed)
- [4. In Jira](#4-in-jira)
- [5. Sources](#5-sources)

## 1. Link the work that waits

Link two work items when one cannot start, or cannot finish, until the other has. PMI defines a
dependency as "A logical relationship between two or more activities where the timing, sequencing,
or completion of one activity is dependent upon another activity." and names four kinds of logical
relationship (PMI Lexicon, 2026):

| Relationship | PMI's definition | A software case |
|---|---|---|
| Finish-to-start (FS) | "A logical relationship in which a successor activity cannot start until a predecessor activity has finished." | The load test starts after the API client is done |
| Start-to-start (SS) | "...a successor activity cannot start until a predecessor activity has started." | The user guide starts once the screens are being built |
| Finish-to-finish (FF) | "...a successor activity cannot finish until a predecessor activity has finished." | Testing cannot finish before the last fix is merged |
| Start-to-finish (SF) | "...a successor activity cannot finish until a predecessor activity has started." | Support for the old service cannot end until the new one serves users |

Use finish-to-start unless the work really overlaps. Jira draws only that one kind: the Timeline
"can only show work items with the Blocks work item link type", and Jira Plans treats every link
type "as though they're of the Blocks type meaning that the first work item must end before the
second one can begin" (Atlassian). So turn an SS or FF dependency into finish-to-start between
smaller items: split the successor, so that the part that waits is a work item of its own (this
practice's own). The reason: a dependency Jira cannot draw is one nobody sees on the Timeline. Which
link type to use for what is in [tickets.md](tickets.md) section 5.

Check: before a work item enters In Progress, ask whether every item it waits on is linked to it
with "blocks".

## 2. Estimate in ranges

Let the people who will do the work estimate it, and give a range, never a single number. The Scrum
Guide says "The Developers who will be doing the work are responsible for the sizing." PMI's
multipoint estimating applies "an average or weighted average of optimistic, pessimistic, and most
likely estimates when there is uncertainty with the individual activity estimates" (PMI Lexicon,
2026). The reason for the range is measured: Jørgensen reports that when a project leader claims to
be 90 percent sure of a maximum effort, "the actual probability is typically 60 to 70 percent"
(IEEE Software, 2005).

- **Make the range wider than feels right.** A range the team is "90 percent sure" of is too narrow
  by Jørgensen's measure, so set its ends from how far the team's past estimates were off, not from
  how sure the team feels (this practice's own reading of his finding).
- **Forecast a date from a range of past throughput, not one average.** Cohn forecasts with a range
  of velocity ("this team is likely to complete between 27 and 36 points per sprint") and writes "A
  useful agile forecast does not pretend to remove uncertainty." A team without points uses the
  number of items it finished per sprint. Jira's reports forecast from an average (section 4); only
  the version report adds an optimistic and a pessimistic line. Give the early and the late date,
  and name the report and the sprints they come from, because two Jira reports can give the same
  team two different dates.
- **A team without sprints forecasts per item.** The Kanban Guide's Service Level Expectation is "A
  forecast of how long it should take a work item to flow from started to finished", with a
  probability, for example "85% of work items will be finished in eight days or less".
- **Story points are optional.** The Scrum Guide names no unit. Atlassian calls story points "a
  subjective unit of measurement that doesn't correlate to any amount of time", so never convert
  them to hours. Ron Jeffries, who may have invented them, writes "if I did, I'm sorry now", and
  calls predicting a date from them "at best a weak idea".
- **Never compare teams by their points or velocity.** Each team sizes in its own unit; Jeffries
  names the comparison as one of the misuses he regrets.

Experts disagree on how far a date forecast from points can be trusted: Cohn forecasts dates from a
velocity range, while Jeffries prefers to fix the date and deliver small slices every week until
then. Both reject a single number, and so does this practice.

Check: when anyone gives a date, ask which range it is the end of, and which past sprints set it.

## 3. Find the critical path when a date is fixed

When the project has a fixed date and work that waits on other work, draw the network of the work
packages that lead to that date and find its critical path. Without it nobody knows which delay
moves the date and which does not.

PMI's terms (PMI Lexicon, 2026):

- **Project schedule network diagram:** "A graphical representation of the logical relationships
  among the project schedule activities."
- **Critical path:** "The sequence of activities that represents the longest path through a project,
  which determines the shortest possible duration."
- **Total float:** "The amount of time that a schedule activity can be delayed or extended from its
  early start date without delaying the project finish date or violating a schedule constraint."

How, in four steps (this practice's own, on PMI's critical path method):

1. List the work packages that lead to the fixed milestone, each with the high end of its range.
2. Add the finish-to-start links from Jira (section 1).
3. Walk forward: an item starts when the last item it waits on finishes.
4. The longest chain to the milestone is the critical path. For every other item, its float is how
   long it can slip before it joins that chain.

Keep the network at the level of work packages or epics, not stories (this practice's own). A path
drawn over hundreds of stories changes every day, and a slip on it is news only at the level the
sponsor sees.

Use the result two ways. A delay on the critical path moves the end of the path by the same amount: it uses the schedule's
buffer first (below), then moves the milestone, so the project manager checks the forecast against
the tolerance that day ([project-plan.md](project-plan.md) section 4). A delay inside an item's float moves nothing, so it needs no change request.

Keep the schedule's share of the contingency reserve as one named buffer before the milestone, not
hidden in each estimate ([risks.md](risks.md) section 6 owns the reserves).

A filled network for one project is in [project-example.md](project-example.md) section 3.

Check: when a milestone is at risk, ask which items are on its critical path, and how much float the
late item had.

## 4. In Jira

| Need | Jira | Limit |
|---|---|---|
| See dependencies of one space | The Timeline, with "blocks" links | "A timeline can only show work items from one space."; finish-to-start only |
| Plan across spaces and teams | Jira Plans: dependencies across spaces, capacity, scenarios | Premium and Enterprise only |
| Past velocity, sprint by sprint | The velocity chart | Shows "the average amount of work a scrum team completes during a sprint"; read the spread yourself |
| Forecast a release date | The version report shows a "Predicted Release Date ... based on your average daily velocity", with an optimistic and a pessimistic line; the release burndown predicts sprints from the last three sprints | Scrum boards; one average, so the two reports can disagree |
| Release on track in a plan | Jira Plans marks a release off track when "the sprint ends after the release date" | Uses sprint dates, not ranges |
| Cycle time and its spread | The control chart: a rolling average, with the standard deviation shaded | No forecast; useful for a Kanban team's Service Level Expectation |
| Critical path, float, schedule baseline | Not computed | No Jira help page describes them; Atlassian's guide to the critical path method defines the critical path and float, not a schedule baseline; the request "Add in Critical Path Analysis" (`JSWCLOUD-21122`) has been open since 2021 |

Compute the critical path on the plan page, as a table, or in a spreadsheet, from the links in
Jira. Keep the schedule baseline in the plan page's baseline column, as
[project-plan.md](project-plan.md) section 4 says, because Jira keeps none.

## 5. Sources

- [PMI Lexicon of Project Management Terms, v5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: dependency, the four logical relationships, multipoint estimating, project schedule network diagram, critical path, total float. Read as raw text on 2026-10-06.
- [The Scrum Guide](https://scrumguides.org/scrum-guide.html), November 2020: sizing by the Developers; no estimation unit.
- Jørgensen, ["Practical Guidelines for Expert-Judgment-Based Software Effort Estimation"](https://cms.simula.no/sites/default/files/publications/Jorgensen.2005.3.pdf), IEEE Software, 2005: overconfident intervals and how two companies fixed them.
- Cohn, ["Agile planning and forecasting"](https://www.mountaingoatsoftware.com/agile/agile-planning-and-forecasting), Mountain Goat Software, undated: forecasting with a velocity range.
- Jeffries, ["Story Points Revisited"](https://ronjeffries.com/articles/019-01ff/story-points/Index.html), 2019-05-23.
- Atlassian, ["Critical path method"](https://www.atlassian.com/work-management/project-management/critical-path-method), undated, read 2026-10-06: the critical path and float.
- Atlassian: ["What are story points"](https://support.atlassian.com/jira-software-cloud/docs/what-are-story-points/); ["Create or remove dependencies on your timeline"](https://support.atlassian.com/jira-software-cloud/docs/create-or-remove-dependencies-on-your-timeline/); ["What are dependencies in plans"](https://support.atlassian.com/jira-software-cloud/docs/what-are-dependencies-in-advanced-roadmaps/); ["What is Plans"](https://support.atlassian.com/jira-software-cloud/docs/what-is-advanced-roadmaps/); ["Track releases from your timeline"](https://support.atlassian.com/jira-software-cloud/docs/track-releases-from-your-timeline/); ["What is the timeline"](https://support.atlassian.com/jira-software-cloud/docs/what-is-the-roadmap/); the [velocity chart](https://support.atlassian.com/jira-software-cloud/docs/view-and-understand-the-velocity-chart/), [version report](https://support.atlassian.com/jira-software-cloud/docs/view-and-understand-the-version-report/), [release burndown](https://support.atlassian.com/jira-software-cloud/docs/view-and-understand-the-release-burndown-report/) and [control chart](https://support.atlassian.com/jira-software-cloud/docs/view-and-understand-the-control-chart/). All undated, read 2026-10-06.
- [Kanban Guide](https://kanbanguides.org/english/), version 2025.5: the Service Level Expectation.
- Atlassian's public tracker, ["Add in Critical Path Analysis (via story links) in JIRA"](https://jira.atlassian.com/browse/JSWCLOUD-21122), created 2021-01-04, status "Gathering Interest" when read on 2026-10-06.