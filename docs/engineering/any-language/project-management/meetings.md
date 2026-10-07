# Meetings

Which meetings a project team holds, in what order and how often, what each one decides, and who
speaks in what order. Read it when you open a project, plan a sprint, or doubt that a meeting is
worth its time. The rule behind every meeting here is in [principles.md](principles.md) section 2.

**Navigation**

- [1. What a meeting is for](#1-what-a-meeting-is-for)
- [2. The order and the cadence](#2-the-order-and-the-cadence)
- [3. Project kickoff](#3-project-kickoff)
- [4. Sprint Planning](#4-sprint-planning)
- [5. Daily Scrum](#5-daily-scrum)
- [6. Backlog refinement](#6-backlog-refinement)
- [7. Sprint Review](#7-sprint-review)
- [8. Sprint Retrospective](#8-sprint-retrospective)
- [9. A team without sprints](#9-a-team-without-sprints)
- [10. PRINCE2 and PMBOK: reports, not meetings](#10-prince2-and-pmbok-reports-not-meetings)
- [11. Sources](#11-sources)

## 1. What a meeting is for

Hold a meeting only when it decides something, and name that decision before you put it in the
calendar. The check is the one in [principles.md](principles.md) section 2: write "We will decide
X from this." The reason: a meeting with no decision costs every attendee's time and gives nothing
back.

| Meeting | What it decides | Output in Jira |
|---|---|---|
| Project kickoff | Whether everyone shares the goal, the scope and the roles, and what happens first | The charter page linked from the project's epics; the first items in the backlog |
| Sprint Planning | What this Sprint holds and why | A sprint with its goal and its work items; subtasks if the team uses them |
| Daily Scrum | What the Developers do in the next day | Moves on the board; a blocker is set as [jira-workflow.md](jira-workflow.md) section 4 says |
| Backlog refinement | Which items are ready to be picked, and in what order | Items with a description, a rank and a size |
| Sprint Review | What is Done, and what to do next toward the goal | At Complete sprint, items not Done move to the next sprint or the backlog list, and their status does not change ([jira-workflow.md](jira-workflow.md) section 7); the backlog re-ordered |
| Sprint Retrospective | Which improvements the team takes on | Actions, each with an owner and a date |

The table is good because every row names the decision its meeting makes, as the rule above asks,
so a reader who copies a row into a calendar invite also copies what the meeting must decide.
The Jira column is this practice's own: it names where each decision is kept, so that nobody has
to remember what a meeting decided.

The Scrum Guide (2020) names five events: the Sprint and the four inside it, Sprint Planning, the
Daily Scrum, the Sprint Review and the Sprint Retrospective. "The Sprint is a container for all
other events." Backlog refinement is not one of them (section 6), and neither is the kickoff,
which PMI defines (section 3).

## 2. The order and the cadence

Hold the meetings in this order. Refinement prepares the items for the next Sprint Planning; each other meeting uses the output of the one before it:

1. Project kickoff, once, at the start (section 3).
2. Then, in every sprint: Sprint Planning on day 1, the Daily Scrum every working day, backlog
   refinement once a week, for the next Sprint Planning, the Sprint Review on the last day, and the Sprint Retrospective after
   the review and before the next Sprint Planning (Cohn, in a two-week sprint, puts planning on
   day 1, refinement mid-sprint, and the review and then the retrospective on the last day).

The reason for the order: the planning sets the goal, the daily checks progress toward it, the
review shows what was reached, and the retrospective changes how the next sprint is run.

A two-week sprint:

| Meeting | When | Timebox | Who attends |
|---|---|---|---|
| Sprint Planning | Day 1 | Up to 4 hours | The whole Scrum Team |
| Daily Scrum | Every working day, same time and place | 15 minutes | The Developers |
| Backlog refinement | Once a week, before Sprint Planning | About an hour | The Product Owner, the Scrum Master and at least one Developer |
| Sprint Review | Last day | 30 to 60 minutes | The Scrum Team and the stakeholders |
| Sprint Retrospective | Last day, after the review | 30 to 60 minutes | The Scrum Team |

The table is good because each meeting has its day, its timebox and who attends, and every value
comes from a source this section names or is marked as this practice's own, so a team can copy it
and know where each number comes from.

The timeboxes come from two places. The Scrum Guide gives the maxima for a one-month Sprint:
Planning 8 hours, Review 4 hours, Retrospective 3 hours, and the Daily Scrum 15 minutes. It adds
that shorter Sprints have shorter events. For planning, Atlassian's rule is "no more than two
hours for each week of the sprint", which makes 4 hours for two weeks. Atlassian gives 30 minutes
to an hour for the review and for the retrospective. The refinement time of an hour is this
practice's own figure, because no source gives one. The reason for a timebox: a meeting that
has no end grows to fill the day.

A table is enough here, so there is no diagram.

## 3. Project kickoff

Hold one kickoff at the start of the project, after the sponsor has issued the charter
([charter.md](charter.md)), so the meeting can walk a charter that is already agreed (step 2 below).
PMI defines it as "A gathering of team members and other key stakeholders at the beginning of a
project to formally set expectations, gain a common understanding, and commence work." Atlassian's
project kickoff play plans 90 minutes for 3 to 14 people.

Run it in this order. Steps 1 and 5 follow Atlassian's play, which opens with the sponsor and ends
with next steps; steps 2 to 4 are this practice's own, built on PMI's three aims (set
expectations, gain a common understanding, start work):

1. The sponsor opens with the goal and why the project exists. The reason: the team hears the goal
   from the person who owns it, not second hand.
2. The project manager walks the charter ([charter.md](charter.md) section 2): the scope in and
   out, the success criteria, the plan in outline, and the top risks. The reason: everyone leaves
   with the same picture of what "done" means.
3. Roles: who is the sponsor, the project manager, and who owns each deliverable. The reason: a
   person who does not know the roles does not know whom to ask.
4. Questions from everyone. The reason: a doubt raised here costs a minute, and a doubt raised
   in week six costs a change request.
5. Next steps: who does what first, with a date. The reason: the meeting ends in work, which is
   what PMI's "commence work" asks for.

The decision of this meeting is that the team commits to the goal and the first steps. This
practice's own rule: the sponsor records it as a comment on the charter page, so the start of the
work can be shown later.

## 4. Sprint Planning

Hold it on day 1 of the sprint with the whole Scrum Team, so the sprint has its goal before the
work starts. The Scrum Guide gives it three topics, and you take them in this order, because each
needs the answer of the one before:

| Topic | Question | Who brings it |
|---|---|---|
| Why | Why is this Sprint valuable? | "The Product Owner proposes how the product could increase its value and utility in the current Sprint"; the whole Scrum Team then defines the Sprint Goal |
| What | What can be Done this Sprint? | "Through discussion with the Product Owner, the Developers select items from the Product Backlog" |
| How | How will the chosen work get done? | The Developers plan the work, "often" by "decomposing Product Backlog items into smaller work items of one day or less" |

The Guide adds that the how is the Developers' alone: "No one else tells them how to turn Product
Backlog items into Increments of value." That is the same rule as [principles.md](principles.md)
section 2: agree what, leave the how to the people who do it.

This practice's own order of speaking: the Product Owner speaks first, because the why topic
starts from the Product Owner's proposal. The Developers speak next, because they select and plan,
and the Sprint Backlog is "a plan by and for the Developers". The Scrum Master makes sure the
timebox holds. The reason: the person who owns the value proposes it, and the people who do the
work decide how much of it fits.

The output in Jira: a sprint, its goal written in the sprint's goal field, the selected items in
it, and the subtasks the Developers add when they split an item
([jira-work-item-types.md](jira-work-item-types.md) section 3). Pick only items that were refined: an item
that "can be Done by the Scrum Team within one Sprint" is ready for selection (section 6).

## 5. Daily Scrum

Hold it every working day, 15 minutes, for the Developers, at the same time and place. All three
come from the Scrum Guide, which gives the reason for the fixed time and place: "To reduce
complexity". The Guide also leaves the structure to the Developers: "The
Developers can select whatever structure and techniques they want, as long as their Daily Scrum
focuses on progress toward the Sprint Goal and produces an actionable plan for the next day of
work."

The three questions are not part of the 2020 Guide. The 2017 Guide offered them as an example
("Here is an example of what might be used") and the 2020 Guide removed them. So the format
below is a default, and a team may change it.

Default format: each Developer in turn says three things:

1. What they finished since yesterday toward the Sprint Goal.
2. What they will do today.
3. What blocks them.

No source sets the speaking order. This practice's own rule: go round in one fixed order the team
agrees at its first Daily, because a fixed order saves the time spent on who is next. With the board
walk, the board sets the order: the item nearest Done first.

Atlassian's team uses these three questions, and PMI's daily coordination meeting does the same:
it "reviews progress from the previous day, declares intentions for the current day, and
highlights any obstacles encountered or anticipated". The reason to keep the Sprint Goal in
the first two: the meeting then checks the goal, not the individual.

Alternative: walk the board right to left, starting with the item nearest Done, and ask what is
needed to finish it. Hammarberg puts it as "Stop starting - start finishing", and scrum.org
posts describe the same walk. Use it when the team has many items in progress, because it turns
attention to finishing before starting.

Rules for both formats:

- Solve a problem after the meeting, by the people it concerns. This practice's own rule. The
  reason: the other Developers' 15 minutes are not spent on a discussion that is not theirs.
- A blocker from outside the team goes to Blocked as [jira-workflow.md](jira-workflow.md) section 4 says, with
  its named blocker and its link; a block the team can clear the same day is flagged and stays where
  it is.
- The Scrum Master makes sure the meeting happens. The Product Owner joins as a Developer only when
  working on items. The reason: it is the Developers' plan for the next day, and a manager in the
  circle turns it into a report (principles.md section 2 on micromanaging).

BAD: a status report instead of a plan. Each person reports a percentage to the manager, so no one
plans the next day with the others.

```
Jane Doe:   "Hello, John. For the report: PROJ-21 is at 80 percent. I will be done soon."
John Smith: "Hello. PROJ-22 is at 50 percent, no problems."
Mary Major: "PROJ-23 is at 30 percent."
Project manager: "Good, keep going."
```

The reason it is wrong: nothing here says what finishes today, what blocks whom, or how the team
reaches the Sprint Goal. A percentage is not a plan, and the manager is the only listener.

GOOD: the same three people and the same items, with the one problem fixed: they plan the next day
together toward the Sprint Goal "Card payments in the checkout call the new provider's test
environment", instead of reporting status.

```
Jane Doe:   "Yesterday I finished the provider client for PROJ-21, so the test call works.
             Today I start the retry on timeouts, also PROJ-21. No blocker."
John Smith: "Yesterday I wrote the routing flag for PROJ-22. Today I need the test client
             from Jane to try it. No blocker."
Mary Major: "Yesterday I started PROJ-23, the checkout tests. I am blocked: the provider's
             test keys have not arrived. I will mark PROJ-23 as Blocked after this."
Jane Doe:   "I will ask the provider about the keys right after this meeting."
```

Why it is good: each person says what they finished, what they do, and what blocks them, and
each speaks to the others. John's need for Jane's client is found in the meeting. Mary's blocker
leaves the meeting with a named owner, and the talk about the keys happens afterwards, between
the two people it concerns. The example follows the rules above and holds no code, so no
other practice governs it.

## 6. Backlog refinement

Refine the backlog all the time, and hold a refinement session once a week, about an hour, before
Sprint Planning, so the items are ready when the planning picks them. The Product Owner runs it,
because the session ends in the Product Owner's order of the backlog (step 5 below). The Scrum
Guide describes refinement as "an ongoing activity to add details, such as a description, order,
and size", and it is an activity, not an event. Atlassian puts the session once a week, run by the
Product Owner, with the Product Owner, the Scrum Master and at least one Developer, before each
sprint planning meeting. The hour is this practice's own figure.

Leave an item in refinement until it can be Done within one Sprint, and until it fits
[tickets.md](tickets.md) section 3's three-day limit. The Scrum Guide says items "that can be Done
by the Scrum Team within one Sprint are deemed ready for selection". The reason: an item that does
not fit cannot be picked in Sprint Planning, and one that is too big is found out late in the
sprint.

The decision of the session is which items are ready, and in what order. This practice's own
order of work in the session, where each step uses what the one before it settled:

1. The Product Owner presents the top items and why they matter.
2. The Developers ask questions and check the acceptance criteria.
3. They check each item fits three working days ([tickets.md](tickets.md) section 3) and split what
   does not.
4. The Developers who will do the work size each item. The Scrum Guide: "The Developers who will
   be doing the work are responsible for the sizing." A size set in a session with only some of
   them is confirmed at Sprint Planning, because the whole Scrum Team is there (section 4).
5. The Product Owner re-orders the backlog.

The output in Jira is the item with its description, its rank in the backlog and its size.

## 7. Sprint Review

Hold it on the last day of the sprint, so it covers all the work the sprint reached. The order:

1. The Product Owner opens with the Sprint Goal, and says what is Done and what is not Done, so
   everyone judges what follows against the goal. The Scrum Guide 2017 has this step: "The Product
   Owner explains what Product Backlog items have been 'Done' and what has not been 'Done'"; the
   2020 Guide does not.
2. The Developers demonstrate Done items only. The Scrum Guide 2020 says an item that does not meet
   the Definition of Done "cannot be released or even presented at the Sprint Review. Instead, it
   returns to the Product Backlog for future consideration."
3. Different team members demonstrate (Atlassian), not always the same one. The reason: the work
   belongs to the team, and every person who did the work can show it.
4. The stakeholders give feedback. The Scrum Guide 2020: "the Scrum Team and stakeholders review
   what was accomplished in the Sprint".
5. The group discusses what to do next and the progress toward the Product Goal (Scrum Guide 2020).

The order of the steps is this practice's own, and each step names its source. Keep it a
conversation (Scrum Guide 2020): "The Sprint Review is a working session and the Scrum Team should
avoid limiting it to a presentation." The reason: the meeting decides what to do next, and a
presentation decides nothing. The review is not a gate to releasing: the Guide says an Increment
may be delivered before the end of the Sprint, and that "the Sprint Review should never be
considered a gate to releasing value".
Its output in Jira: the backlog re-ordered by the Product Owner. Done items are already Done, from
their production deploy ([jira-workflow.md](jira-workflow.md) section 2). At Complete sprint, items
not Done move to the next sprint or the backlog list, and their status does not change
([jira-workflow.md](jira-workflow.md) section 7, which also covers a partly done item). The
timebox is in section 2.

## 8. Sprint Retrospective

Hold it after the review and before the next Sprint Planning. The Scrum Guide's retrospective
inspects "individuals, interactions, processes, tools, and their Definition of Done", with a maximum of
3 hours for a one-month Sprint (section 2), and "concludes the Sprint". The reason for the place in
the order: the team can apply what it learned in the very next planning. The Guide says what comes
out of it: "The Scrum Team identifies the most helpful changes to improve its effectiveness. The
most impactful improvements are addressed as soon as possible. They may even be added to the Sprint
Backlog for the next Sprint."

Atlassian's retrospective play has five steps, with these minutes:

| Step | Minutes |
|---|---|
| Set the tone | 5 |
| Gather feedback | 15 |
| Turn feedback into insights | 20 |
| Create action items | 15 |
| Conclusion | 5 |

The steps total 60 minutes. Atlassian says a retrospective can be as short as 45 minutes or as
long as 3 hours, so scale the minutes to the length you pick.

End with "a few actionable ideas with clear owners and due dates" (Atlassian). The reason: an
idea with no owner and no date is forgotten before the next sprint. Write each as a work item with
its owner and its date, so the action is planned and tracked with the rest of the work.

No source prescribes a speaking order for the retrospective. Atlassian's only rule on turns is
that, when one person dominates, the facilitator calls on others "to make sure everyone gets
their voice heard". So the facilitator calls on people who have not yet spoken.

The project's final retrospective, at Closure, is in [life-cycle.md](life-cycle.md) section 2.

## 9. A team without sprints

The Kanban Guide prescribes no meetings. It says: "There is no requirement, however, to wait for a
formal meeting at a regular cadence to make these changes." It also says members review active
items "continuously, at regular intervals, or through a combination of both."

This practice's own rule: a team without sprints keeps a daily board review, walking the board
right to left as in section 5, and a regular retrospective, and it refines when the Backlog runs
low. The reasons: the daily review keeps the age of items visible, the retrospective changes how
the team works, and refining on need keeps the Backlog from growing stale. Where the Kanban Guide
lists no cadence, the team picks it, and writes it down, so the cadence does not depend on anyone's
memory. When a team should work without sprints is in [life-cycle.md](life-cycle.md) section 4.

## 10. PRINCE2 and PMBOK: reports, not meetings

PRINCE2 prescribes reports and stage decisions, not team meetings. In PRINCE2 7 a Checkpoint Report
goes from the team manager to the project manager "at a frequency defined in the work package", and
the project manager issues a Highlight Report to the project board "at intervals defined by them"
(PeopleCert's PRINCE2 7 sample paper). PMI defines the kickoff meeting and the daily coordination
meeting (section 3 and section 5).

No standard read for this practice requires a weekly status meeting. The check of
[principles.md](principles.md) section 2 applies to any such meeting: write "We will decide X
from this", and if you cannot, do not hold it. The weekly written status update that takes its place
is in [communication.md](communication.md) section 2.

## 11. Sources

- [Scrum Guide (2020)](https://scrumguides.org/scrum-guide.html), 2020-11: the events and the Sprint as their container, their timeboxes and attendees, the Daily Scrum text, refinement and who sizes, Definition of Done, the Sprint Review text, the review as no gate.
- [Scrum Guide (2017)](https://scrumguides.org/scrum-guide-2017.html) and [its revisions](https://scrumguides.org/revisions.html), 2017 and 2020: the three Daily Scrum questions as an example, and their removal; the Product Owner's step in the Sprint Review on what is and is not Done.
- [PMI Lexicon of Project Management Terms, version 5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), 2026-01: the kickoff meeting and the daily coordination meeting.
- [Kanban Guide, version 2025.5](https://kanbanguides.org/english/), read 2026-10-06: no prescribed meetings; review of active items.
- [Atlassian, "Standups"](https://www.atlassian.com/agile/scrum/standups), undated, read 2026-10-06: the three questions, 15 minutes, the board.
- [Atlassian, "Sprint planning"](https://www.atlassian.com/agile/scrum/sprint-planning), undated, read 2026-10-06: two hours for each week of the sprint.
- [Atlassian, "Sprint reviews"](https://www.atlassian.com/agile/scrum/sprint-reviews), undated, read 2026-10-06: 30 minutes to an hour; different people demonstrate.
- [Atlassian, "Retrospectives"](https://www.atlassian.com/agile/scrum/retrospectives), undated, read 2026-10-06: 30 minutes to an hour; actions with owners and dates.
- [Atlassian, "Backlog refinement"](https://www.atlassian.com/agile/scrum/backlog-refinement), undated, read 2026-10-06: once a week, run by the Product Owner, who attends.
- [Atlassian Team Playbook, "Project kickoff"](https://www.atlassian.com/team-playbook/plays/project-kickoff), undated: 90 minutes, 3 to 14 people, the sponsor opens.
- [Atlassian Team Playbook, "Retrospective"](https://www.atlassian.com/team-playbook/plays/retrospective), undated, read 2026-10-06: the five steps and their minutes; no speaking order.
- [Cohn, "What happens when during a sprint"](https://www.mountaingoatsoftware.com/agile/what-happens-when-during-a-sprint), undated: the order in a two-week sprint.
- [Hammarberg, "Comments on board practices 7"](https://www.marcusoft.net/2017/03/comments-on-board-practices-7.html), 2017-03-04: walk the board right to left.
- [Scrum.org, "Daily Scrum tips and tactics"](https://www.scrum.org/resources/blog/daily-scrum-tips-tactics), undated, seen as a search snippet only: the same walk.
- [prince2.wiki, "Work Package"](https://prince2.wiki/management-products/baselines/work-package/), undated, a secondary source: reporting arrangements.
- PeopleCert, [PRINCE2 7 Foundation sample paper 1 with rationales](https://www.serview.de/fileadmin/redakteur/medien/downloads/Musterpr%C3%BCfungen_f%C3%BCr_neuen_Downloadbereich/P2-7_FND_SamplePaper1_Rationales_v1-1_EN.pdf), 2023, an official training PDF hosted by a training organisation: checkpoint and highlight reports.
