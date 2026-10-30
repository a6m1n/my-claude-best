# Kanban: two definitions, how a team starts, and Kanban inside Scrum

This file is for anyone who sets up or changes a Kanban system: a team, a project manager, a Scrum
Master, and an AI agent asked to "set up a Kanban board". Two texts define Kanban. They differ in
their practices, their measures and how big a change may be, so a team that says "we do Kanban"
can mean either. The file says which text each rule follows, when Kanban fits and when it is too
much, how a team starts, which flow measures to keep, and how a Scrum team adds Kanban and stays a
Scrum team. A team that follows it has a written Definition of Workflow that names its text, a WIP
control it acts on, and flow measures that mean the same thing in every report.

**Navigation**

- [1. Two definitions, and which one each rule follows](#1-two-definitions-and-which-one-each-rule-follows)
- [2. When it fits and when it is too much](#2-when-it-fits-and-when-it-is-too-much)
- [3. How a team starts](#3-how-a-team-starts)
- [4. Flow measures](#4-flow-measures)
- [5. Kanban inside Scrum](#5-kanban-inside-scrum)
- [6. Common mistakes](#6-common-mistakes)
- [7. Sources](#7-sources)

**When you do not need this file.** The pick between Scrum and a Kanban flow for a deliverable is
[life-cycle.md](../project-management/life-cycle.md) section 4, not this file. A team on the
project-management practice that needs only the board's statuses or a WIP limit reads
[jira-workflow.md](../project-management/jira-workflow.md) section 2 or
[principles.md](../project-management/principles.md) section 3. A Scrum team that adds no flow
practice needs none of this file.

**What this file leaves out.** Each of these has its own owner:

- Whether a deliverable runs in Scrum or in a Kanban flow:
  [life-cycle.md](../project-management/life-cycle.md) section 4.
- The board's statuses with their entry and exit conditions, and the Blocked status:
  [jira-workflow.md](../project-management/jira-workflow.md) sections 2 and 4.
- The work-in-process limit per person and for the team, and the weekly board look:
  [principles.md](../project-management/principles.md) section 3.
- The meetings of a team without sprints: [meetings.md](../project-management/meetings.md)
  section 9; the Scrum events are sections 2 to 8 there.
- Who chooses the approach and the team's process:
  [choosing-an-approach.md](choosing-an-approach.md).
- What keeping Scrum whole means, and what tailoring it costs: [scrum.md](scrum.md).
- Scrumban, which in this practice means only Corey Ladas's path that starts from Scrum and leaves
  it: [combining-approaches.md](combining-approaches.md).
- AI agents. None of the three Kanban texts this file cites says anything about AI: a search of
  each for "AI", "agent" and "artificial intelligence" on 2026-10-30 found no hit [1], [2], [4].
  Trainers certified by ProKanban.org write about AI on its blog as their own view; Liz Rettig, for
  one, holds that small work items are how a team controls the risk of building the wrong thing
  fast [8]. What a team keeps when agents take part is in [ai-agents.md](ai-agents.md).
- Security and privacy: [README.md](README.md).

## 1. Two definitions, and which one each rule follows

"Kanban" names two texts with two owners. The Kanban Guide answers a workflow that does not deliver
"what stakeholders want when they want it": "As most workflows exist to optimize value, the
strategy of Kanban is to optimize value by optimizing flow" [1]. The Kanban Method is "widely known
for usage within teams, to relieve overburdening and to (re-)gain control over the work done by
the team" [2]. The two side by side:

| | The Kanban Guide | The Kanban Method |
|---|---|---|
| Text and edition | The Kanban Guide, v2025.5, May 2025, created by John Coleman and Daniel Vacanti [1] | The Official Guide to the Kanban Method, Kanban University, © 2022 [2] |
| What Kanban is | "a strategy for optimizing the flow of value through a process" [1] | "not a methodology nor a process framework", but "a management method or approach that should be applied to an existing process or way of working" [2] |
| Practices | Three: defining and visualizing a workflow; actively managing items in a workflow; improving a workflow [1] | Six general practices: visualize; limit work in progress; manage flow; make policies explicit; implement feedback loops; improve collaboratively, evolve experimentally [2] |
| Principles | None of its own; it "draws on established flow theory" [1] | Six, in two groups: three change management principles: start with what you do now; agree to pursue improvement through evolutionary change; encourage acts of leadership at all levels; and three service delivery principles: understand and focus on customer needs and expectations; manage the work, let people self-organize around it; regularly review the network of services and its policies in order to improve outcomes [2] |
| Measures | Four mandatory flow metrics: WIP, throughput, work item age, cycle time [1] | Three core metrics: lead time, delivery rate, WIP [2] |
| How a team starts | A Definition of Workflow with six elements [1] | STATIK, the Systems Thinking Approach To Introducing Kanban [2] |

Neither text names the other [1], [2]. The Guide does not claim to own the word: its conventions
"are not meant to replace any other existing definitions but to clarify how they are intended to
be applied here" [1]. The Method "is based on" David J. Anderson's 2010 book on Kanban [2]. A page
on Kanban University's site names no author, but it says "In my book, Kanban – Successful
Evolutionary Change for your Technology Business" [3], the title of that book, so this file reads
the page as Anderson's. It lists four principles: the guide's three change management principles,
in slightly different words, and a fourth, "Respect the current process, roles, responsibilities &
titles" [3]. The 2022 guide has no such fourth principle, and the page has none of the guide's three
service delivery principles [2], [3]. This file takes the Method's principles, all six, from the
2022 Official Guide, because it is the body's own guide to the Method and the page is one author's
article.

**The one rule.** When you write a board policy or a Definition of Workflow for a Kanban system,
or any other rule that says "Kanban", name the text it follows and its edition, in the rule or in
the sources list of the file that holds it. The reason: the two texts differ in
practices, measures and the size of a change, so a policy that names no text cannot be checked
against either.

**Which text this file follows.** The rules on the Kanban system itself (the Definition of
Workflow, WIP control, the service level expectation and the flow measures, sections 3 and 4)
follow the Kanban Guide. It calls itself "the minimal guidance for Kanban" [1], so a team can check
all of it on one page, and the project-management practice already uses its terms
([principles.md](../project-management/principles.md) section 3). The Method is followed on one
route: a team that changes the way it works now, step by step, starts with STATIK (section 3). The
Open Guide to Kanban on kanbanguides.org is not followed: the site calls it "a fork of the Kanban
Guide (May 2025)" [6], and a fork is not an edition of the Guide.

**The one disagreement: how big a change may be.** The two owners disagree here. This file shows
both and does not split the difference.

- The Guide: "There is also nothing that prescribes improvements to workflow to be small or
  incremental. If the Kanban system members feel that a significant change is needed, then that is
  what they should implement" [1].
- The Method: its second principle is to agree to pursue improvement through evolutionary change,
  and "Kanban is not a big bang transformation going from a current state to some future state"
  [2]. Its glossary defines that change as "the intentional design of small incremental changes,
  tested via experiments using the scientific method" [2]. Anderson holds the same on his page:
  "The organization (or team) must agree that their current circumstances warrant a gentle,
  evolutionary approach to improvement" [3].

Write the team's position next to the name of its text and its edition: a team on the Guide in its
Definition of Workflow, and a team on the Method among the explicit policies of the Kanban system
that STATIK's last step designs (section 3), since the Definition of Workflow is the Guide's term
and the Official Guide does not use it [1], [2].
A team on the Guide may make a big change in one step when its members judge one is needed. A team on the
Method has agreed to evolutionary change, so it makes each change as a safe-to-fail experiment that
it can "easily roll back to the prior state" [2]. The reason: a proposal for a big change is then
judged against the text the team chose, not against the text each person happens to know.

## 2. When it fits and when it is too much

**When it fits.** The Guide says "Kanban can be used at any scale and in most contexts where value
is delivered" [1]. "Most" is its only limit: the whole text, read on 2026-10-30, names no context
where Kanban does not fit [1]. The Method is meant to be added to what a team does, not chosen
against it: "There is never a question of using Kanban versus a given methodology or framework.
Rather, it is always adding Kanban using an existing methodology, framework, or way of working"
[2]. It names no team or kind of work it does not fit either, and speaks only of "more or less
appropriate adoption of practices given the business context and cultural environment" [2].

Whether a deliverable runs in Scrum or in a Kanban flow is the rule of
[life-cycle.md](../project-management/life-cycle.md) section 4; this file does not restate it.

**When the Method does not fit.** The Method's precondition is its "when not": a team that adopts
it agrees first to evolutionary change, its second principle [2]. Anderson holds that without that
agreement the support is missing: "Without agreement that a slow, gentle, evolutionary,
incremental approach is the right way forward then there won’t be the right environment or
management support for a Kanban initiative" [3]. The word "slow" is Anderson's; the 2022 guide's
principle does not use it [2], [3].

Before a team adopts the Method, ask the people who own the change, the team and the managers who
would back it, whether they agree to evolutionary change. When they want a sweeping change now,
the Method is the wrong text; the Guide allows a big change (section 1). The reason: an adoption
that starts without the agreement starts without the support the Method says it needs.

**When it is too much.** Neither text names a team, a size or a kind of work for which Kanban is
too much [1], [2]. What can be too much is the part beyond the minimum. The Guide says members
often add elements to their Definition of Workflow, "such as values, principles, and working
agreements", as their circumstances require [1]. This file's own rule: start with the six elements
of section 3, and add another only when a problem the board shows calls for it, because an element
added before its need is one more policy nobody checks.

**What following it costs.** WIP control means people sometimes wait. DORA's page on the
capability says "WIP limits can result in teams sitting idle, waiting for other tasks to be
completed", and asks a team not to raise the limit then but to improve the process that causes the
wait [5]. STATIK costs a workshop: the Official Guide says it "usually takes between 4 hours and 4
days" [2]. The service level expectation starts as a guess and stays one until the team has
finished enough items (section 3).

## 3. How a team starts

There are two routes, one for each text. The team picks its route when it picks its text
(section 1).

**The Guide's route: write the Definition of Workflow first.** Before the first item moves on the
board, write the team's Definition of Workflow (DoW) with all six elements. The Guide: "At a
minimum, Kanban system members must create their DoW using all of the following elements", and
"The order in which these are implemented is not important as long as they are all adopted" [1].
The reason: "The visualization of a DoW is a Kanban board" [1], so a board with no written DoW has
columns whose meaning each person guesses. The six elements, in the Guide's terms [1]:

1. The work items: the units of value that move through the workflow.
2. When a work item starts and when it finishes.
3. The states it flows through from started to finished.
4. How WIP is controlled from started to finished.
5. Explicit policies on how work items flow through each state.
6. A service level expectation (SLE): "a forecast of how long it should take a work item to flow
   from started to finished", in two parts, "a period of elapsed time and a probability associated
   with that period" [1].

A team that also follows the project-management practice takes elements 3 to 5 from it instead of
writing them again: the states and their entry and exit conditions are the board of
[jira-workflow.md](../project-management/jira-workflow.md) section 2, the limit per person and for
the team is [principles.md](../project-management/principles.md) section 3, and a Blocked item
counts toward that limit ([jira-workflow.md](../project-management/jira-workflow.md) section 4).
The reason: each of those rules has one owner, so the DoW and the board cannot drift apart. Any
other team writes its own states with their entry and exit conditions, and its own limits.

Write the signal to pull new work into the DoW. The Guide: "Kanban system members must explicitly
control the number of work items in a workflow from started to finished", and they "should start
work on an item (pull or select) only when there is a clear signal that there is capacity to do
so" [1]. An exception to the control is written too: "Any acceptable exceptions to controlling WIP
should be made explicit as part of the DoW" [1]. The reason: a limit with no pull signal is a
number nobody acts on, and an exception nobody wrote down becomes the rule.

Set the SLE from the team's own cycle times. With no history yet, write a best guess and say that
it is one, as the Guide allows: "If historical cycle time data does not exist, a best guess will do
until there is enough historical data for a proper SLE calculation" [1]. The reason: a guess that
is marked as one gets replaced when the data arrives; an unmarked one is read as a measured
promise.

A Definition of Workflow for one team that works without sprints and follows the Guide and the
project-management practice, so its elements 3 to 5 come from that practice. It names the entry
and exit condition of each state and does not copy them: they are in the table of
[jira-workflow.md](../project-management/jira-workflow.md) section 2. The team, the project key and
the numbers are invented; a team sets its own. A Scrum team changes the four parts of section 5.

```markdown
# Definition of Workflow: Acme Corp support team

Follows: the Kanban Guide, v2025.5, May 2025. Named, so each rule can be checked against
its text (kanban.md section 1).
Size of a change: the team may make a big change in one step when it judges one is
needed, as the Guide allows (kanban.md section 1).
Owner: the team, the Guide's Kanban system members. It reviews this definition at its
retrospective, every second Thursday (meetings.md section 9), and changes it on any day a
change cannot wait.
Product Owner: Jane Doe, who orders the Backlog and decides a cancel (roles-and-decisions.md
section 5).

1. Work items: the stories, tasks and bugs of the SUP project.
   Epics and subtasks are not counted: they have three statuses of their own
   (jira-workflow.md section 2).
2. Started: the item moves from the Backlog to In Progress, after the three-working-day
   check (tickets.md section 3). A later move into In Progress from Blocked, Code Review or
   Pre-prod does not restart the clock.
   The clock starts here, not when the item is created, so cycle time measures the work
   and not the wait in the Backlog.
   Finished: the item enters Done or Canceled, with the entry conditions of
   jira-workflow.md section 2. The four flow metrics of kanban.md section 4 use both
   finished points: an item is in WIP, and has an age, from its start until it enters Done
   or Canceled; it counts once in throughput, with its cycle time, when it enters either.
   Items that enter Done are also counted per week as Delivered, from the same start, so
   a canceled item never shows as delivered work.
   An item canceled while it waits in the Backlog, whether it never entered In Progress
   or was returned there, has no start, so it counts in no flow metric. An item returned
   to the Backlog loses its start: this is the team's own policy, because the Guide counts
   as WIP every item between a started and a finished point and says nothing on returns.
   The item leaves WIP and starts again when it next moves from the Backlog to In
   Progress, so its cycle time and its age count from that start.
3. States: Backlog, In Progress, Blocked, Code Review, Pre-prod, Done, Canceled, with the
   entry and exit conditions of jira-workflow.md section 2.
   Work in progress: every item in In Progress, Blocked, Code Review or Pre-prod.
4. WIP control: at most 2 items per person, and 8 for the team of five; 8, not 10, so the
   team limit binds before every person is full. Two limits, one per person and one for
   the team (principles.md section 3).
   A Blocked item counts toward both limits (jira-workflow.md section 4).
   Pull the top item of the Backlog only when your own count and the team's count are
   both under their limits: that is the pull signal the Guide asks for.
   Exception: the fix for a production incident, its problem work item (sla.md section 3),
   is pulled at once, ahead of the Backlog's order, as Jane Doe agreed as Product Owner,
   and may take the team's count over its limit, one such fix at a time. The restore
   itself is the person on call's (sla.md section 5). The per-person limit still holds: a
   person under 2 items takes the fix. With 8 for a team of five, at least one person is
   always under 2. There is no other exception; the Guide asks for every exception to be
   written here.
5. Policies: the entry and exit condition of each state (jira-workflow.md section 2),
   and the pull rule in item 4.
6. SLE: 85% of work items will be finished in seven days or less.
   Days are elapsed days, weekends included, because the Guide's cycle time is elapsed
   time.
   This is a best guess: the team has no cycle times yet. When 20 items have finished, a
   number the team chose, it replaces the guess with the number of days within which 85%
   of those items finished.

Shown on the board: the age of each item in work in progress, both counts against their
limits, and the SLE, so the minimum elements are visible where the team works.
```

This definition is good because it holds all six elements the Guide asks for, each in a form a
team member can check against the board; it names the text it follows and that text's position on
the size of a change, so a proposal for a big change has a known rule; its four flow metrics count
both finished points, because "started and finished refer to how the Kanban system members have
established those points in their DoW" [1], and delivered work has a count and a name of its own,
so its throughput is the Guide's; an item canceled while it waits in the Backlog counts in no
metric, so a clean-up of the Backlog adds nothing to throughput, and an item returned to the
Backlog loses its start, by the team's own written policy, and starts again when it next moves
from the Backlog to In Progress, so an item that waits in the Backlog is never work in progress
and its cycle time and its age count from that start;
and it takes its states, its limits and its Blocked rule from
[jira-workflow.md](../project-management/jira-workflow.md) and
[principles.md](../project-management/principles.md) by name, so the definition, the board and the
weekly board look cannot drift apart.

Check: before the board goes live, find in the written DoW the name of its text and each of the
six elements. A DoW that lacks one is not ready.

**The Method's route: STATIK, with the people who do the work.** The Method starts from the
current way of working: "Start with what you do now" is its first principle [2]. Its way to start
is STATIK, which the Official Guide calls "a repeatable and humane way to get started with Kanban"
[2]. Its six steps are: identify sources of dissatisfaction; analyze demand; analyze system
capabilities; model the workflow; identify classes of service; design the Kanban system [2]. They
are not one pass: "STATIK is not intended as a one-pass, sequential process", and "The STATIK
approach should be applied to each service" [2]. The last step designs the system, which
"naturally consists of a board and tickets, plus other important elements such as metrics,
cadences, and policies" [2].

Run STATIK with a representative group of the people who do the work, never alone. The Official
Guide says it "should be done with at least a representative group of the people involved" and
"should not be done in isolation e.g., by the Project Manager, Team Lead, or a Coach or
Consultant", because each person's picture of how the work is done "rarely maps between people"
[2]. The meetings that follow, for a team without sprints, are in
[meetings.md](../project-management/meetings.md) section 9.

Check: before the board of a system that STATIK designed goes live, ask: do its explicit policies
name the Method's text, its edition and the team's position on the size of a change?

**When more than one group shares the work.** This holds when several teams, or several levels of
an organisation, work on one flow. The Guide: "Kanban system members also often require more than
one DoW. Those multiple DoWs could be for multiple groups of Kanban system members, different
levels of the organization, etc" [1]. Write a DoW for each group that needs to connect its flow to
the value it delivers, which is where the Guide "encourages establishing a DoW" [1]. On the
Method's route, run STATIK for each service, as quoted above [2]. Scaling frameworks for many teams
are in [scaling.md](scaling.md).

## 4. Flow measures

The WIP limits and the weekly board look are
[principles.md](../project-management/principles.md) section 3's; this section holds how the two
Kanban texts name and define the measures, and how a team shows them.

The Guide names four mandatory flow metrics, and defines each [1]:

| Measure | The Guide's definition |
|---|---|
| WIP | "The number of work items started but not finished" |
| Throughput | "The number of work items finished per unit of time" |
| Work Item Age | "The elapsed time between when a work item started and the current date" |
| Cycle Time | "The elapsed time between when a work item started and when a work item finished" |

The Method's core metrics are three: lead time, "the time it takes for a single work item to pass
through the system from the start (commitment point) to completion"; delivery rate, "the number of
completed work items per unit of time"; and WIP [2]. It names no work item age [2]. The names
differ more than the spans do. When a team's started point is its commitment point, the Method's
lead time and the Guide's cycle time measure the same span, and the Method's glossary says
"Throughput is often referred to as delivery rate" [2]. The Guide allows other names too: "Cycle
Time could be Flow Time, Throughput could be Delivery Rate" [1].

- Use the Guide's four names on the board and in reports. When a report uses another name, say
  which span it measures, from which started point to which finished point. The reason: the same
  word can name different spans; the Method's own glossary has a customer lead time, from the
  customer's request to delivery, and a system lead time, from the commitment point to the first
  column with no WIP limit [2].
- Count throughput in work items, never in points. The Guide: "Note the measurement of throughput
  is the exact count of work items" [1]. The reason: a count needs no estimate, so it means the
  same thing every week.
- Show a measure next to the decision it feeds. The Guide: "In and of themselves, these metrics
  are meaningless unless they can inform one or more of the three Kanban practices" [1]. At the
  daily board review ([meetings.md](../project-management/meetings.md) section 9), look first at
  the items whose age is near or past the SLE. The Guide lists "Ensuring work items do not age
  unnecessarily, using the SLE as a reference" as part of active management [1], and the Kanban
  Guide for Scrum Teams asks which items "have violated or are about to violate their SLE" [4].

## 5. Kanban inside Scrum

This section holds when a Scrum team adds Kanban practices and keeps its sprints. The text for that
case is the Kanban Guide for Scrum Teams, January 2021, "Developed and sustained by Scrum.org,
Daniel Vacanti, and Yuval Yeret", read in its English edition on Scrum.org's own file host [4].
This practice calls Kanban added this way, with Scrum kept whole, Kanban inside Scrum. It is not
Scrumban: here "Scrumban" means only Corey Ladas's path that starts from Scrum and leaves it,
which [combining-approaches.md](combining-approaches.md) owns, and the Kanban Guide for Scrum Teams
does not use the word [4].

It keeps Scrum whole: "This guide does not replace or discount any part of The Scrum Guide", and
"Therefore, The Scrum Guide applies in its entirety" [4]. What dropping or changing a part of Scrum
costs is in [scrum.md](scrum.md). It names four practices: visualization of the workflow; limiting
work in progress; active management of work items in progress; inspecting and adapting the team's
Definition of Workflow [4].

**Add no event.** "Kanban in a Scrum context does not require any additional events to those
outlined in The Scrum Guide", and "The Kanban complementary practices don’t invalidate the need for
Scrum’s Sprint" [4]. The reason: the Sprint and its events are already the team's loops for
inspection, and the guide uses them as the feedback loop for the Definition of Workflow too [4].
Bring flow into the events the team already holds; the events themselves are
[meetings.md](../project-management/meetings.md) sections 2 to 8. What flow adds to each, by the
Kanban Guide for Scrum Teams [4]:

| Event | What flow adds |
|---|---|
| Sprint Planning | Historical throughput, to understand the team's capacity for the next Sprint |
| Daily Scrum | Held at the board: which items are blocked, each item's work item age, which items have broken or are about to break the SLE, and whether the WIP limit is broken |
| Sprint Review | Throughput, when the Product Owner discusses likely delivery dates |
| Sprint Retrospective | Flow metrics, and changes to the Definition of Workflow for the next Sprint |

**The Scrum Team owns its Definition of Workflow.** "No one outside of the Scrum Team should tell
the Scrum Team how to define their Workflow" [4]. A project manager or another manager proposes a
change and the team decides it. The limit of [principles.md](../project-management/principles.md)
section 3 is agreed with the team, so it fits this rule. The reason: the guide makes creating and
adapting the DoW "the accountability of the relevant roles on the Scrum Team" [4].

**Change the Definition of Workflow at the Sprint Retrospective by default.** The guide allows a
change "at any time", but says changes made in the Retrospective's cadence "will reduce complexity
and improve focus, commitment and transparency" [4]. The reason, in the guide's words: such changes
"will have a material impact on how the Scrum Team performs" [4].

**Name the 2021 guide, not the 2025 Guide, in a Scrum team's Definition of Workflow.** The two
differ. The 2021 definition adds that Kanban "uses a visual, work-in-progress limited pull system",
and it says "Scrum Teams using Kanban must explicitly limit the number of these work items in
progress" [4]. The 2025 Guide asks only that WIP be controlled, and its own list of changes calls
the new text "Less explicit (and hence more flexible) how WIP is controlled" [1]. A Scrum team's
DoW keeps the shape of the example in section 3 and changes four parts: it names the 2021 guide;
its owner is the Scrum Team, and it changes at the Sprint Retrospective by default; its work items
are most likely Product Backlog items, as that guide says [4]; and its scope "may encompass flow
inside and/or outside of the Sprint" [4]. The 2021 guide says nothing on the size of a change [4],
so the team writes its own position in that line.

## 6. Common mistakes

**A board with no WIP control.** It looks like a Kanban board, with columns, cards and perhaps the
seven statuses of [jira-workflow.md](../project-management/jira-workflow.md) section 2, but anyone
starts whatever arrives. Teams fall into it because a board is easy to draw and a pull system is
not: the Official Guide calls the move to one "often a cultural change" [2]. DORA's page on the
capability is plain about what is missing: "Only by imposing WIP limits and following this
pull-based process do you actually create a Kanban board" [5]. The Guide makes WIP control one of
the six elements a DoW must have [1]. The cost is the one
[principles.md](../project-management/principles.md) section 3 names from DORA: tasks take longer,
and the team burns out. The fix: write element 4 of the DoW and pull only under the limit
(section 3).

**Mixing the two definitions.** It looks like a policy that cites "the Kanban Guide" for words
that are the Method's, such as policies that are "sparse", "simple" and "readily changeable by
those providing the service", a list from the Official Guide to the Kanban Method [2] that the
Kanban Guide does not contain [1]. It also looks like a report that puts the Method's lead time
next to the Guide's work item age with no word on which span each covers, or a team that agreed to
evolutionary change and then makes a big change citing the Guide. Teams fall into it because both
texts are called a Kanban guide; Kanban University's PDF of its Official Guide is named
"The-Official-Kanban-Guide" [2]. The cost: a reader checks a rule against the wrong text and finds
nothing, and a team argues about a change with each side reading a different owner. The fix: the
one rule of section 1.

**Reading the site badges instead of the edition lines.** kanbanguides.org hosts the Kanban Guide
and the Open Guide to Kanban, a fork of it. On the site's history page the fork carries the badges
"Current Open Guide" and "Active", and the May 2025 Kanban Guide carries "Current Fork" and "Active
Fork" [6]. On the Guide's own history page, the May 2025 Guide carries "Current Open Guide" [7]. A
reader who goes by the badges can cite the fork as the current Kanban Guide, or the Guide as a
fork. The fix: read the version line on the Guide's own page, which gives v2025.5 and marks it
Latest [1], and cite the edition by that line.

**Delivering only at the end of the Sprint.** A team that runs Kanban inside Scrum holds finished
work until the Sprint Review. The Kanban Guide for Scrum Teams names it: "It’s a common
misconception that teams can only deliver value once per Sprint. In fact, they must deliver value
at least once per Sprint" [4]. The cost is slower feedback: the guide says Scrum's empiricism
"encourages the creation of multiple valuable increments during the Sprint to enable fast inspect
and adapt feedback loops" [4]. The fix: deliver each item when it meets the Definition of Done,
and use the Sprint as the loop for inspecting the work, not as the one moment to deliver it.

## 7. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Orderly Disruption Limited and Daniel S. Vacanti, Inc. — The Kanban Guide, v2025.5 (May 2025) — https://kanbanguides.org/the-kanban-guide/2025.5/ — checked 2026-10-30
- [2] Kanban University — The Official Guide to the Kanban Method, © Mauvius Group Inc. 2022 — https://kanban.university/wp-content/uploads/2023/04/The-Official-Kanban-Guide_A4.pdf — checked 2026-10-30
- [3] Kanban University — Principles and General Practices of the Kanban Method (Kanban University, 2014; opinion) — https://kanban.university/principles-general-practices-kanban-method/ — checked 2026-10-30
- [4] Scrum.org, Daniel Vacanti and Yuval Yeret — The Kanban Guide for Scrum Teams, January 2021 — https://scrumorg-website-prod.s3.amazonaws.com/drupal/2021-01/01-2021%20Kanban%20Guide.pdf — checked 2026-10-30
- [5] DORA — Capabilities: Work in process limits (dora.dev, no date; opinion, by a program run by Google Cloud) — https://dora.dev/capabilities/wip-limits/ — checked 2026-10-30
- [6] kanbanguides.org — History — https://kanbanguides.org/history — checked 2026-10-30
- [7] kanbanguides.org — The Kanban Guide: History — https://kanbanguides.org/the-kanban-guide/history/ — checked 2026-10-30
- [8] Liz Rettig — AI doesn't bring waterfall back. It lets you be wrong faster (ProKanban.org blog, 2026; opinion, by a trainer of an organisation that sells Kanban training) — https://prokanban.org/blog/ai-doesn-t-bring-waterfall-back-it-lets-you-be-wrong-faster — checked 2026-10-30
