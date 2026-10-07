# Adopting the practice, step by step

The order in which a team brings this practice into one project: what to do at each step, why the
step is there, and what goes wrong without it. Each step says what to do and links the section that
owns its rule. Where the step and that section differ, the section is right, so read the rule there
before you do the step. Read this file when you start a project with this practice, or bring the
practice into a project that is already running.

**Navigation**

- [1. How to use this guide](#1-how-to-use-this-guide)
- [2. Once per team: the tools](#2-once-per-team-the-tools)
- [3. Initiation](#3-initiation)
- [4. Planning](#4-planning)
- [5. Execution](#5-execution)
- [6. Until closure: the loop](#6-until-closure-the-loop)
- [7. Closure](#7-closure)
- [8. A project that is already running](#8-a-project-that-is-already-running)
- [9. Bring the team along](#9-bring-the-team-along)
- [10. The adoption checklist](#10-the-adoption-checklist)
- [11. Sources](#11-sources)

## 1. How to use this guide

Take the steps in order, because each one uses what the one before it produced: the plan is checked
against the charter, the RACI matrix needs the deliverables of the WBS, and the status markers need
the tolerance. Step 15 is the one exception: it starts in the week after step 10 and runs until
closure. The tolerance is how far a date may move before the sponsor must decide; step 10 agrees
it ([project-plan.md](project-plan.md) section 4). The order follows the five project phases of
[life-cycle.md](life-cycle.md) section 2 and the loop of
[operating-system.md](operating-system.md) section 1, and it is this practice's own: the PMP exam
outline lists the tasks with no order, and PRINCE2 7 runs a similar one, which starts a project
with an explicit decision and authorizes it once the plan and its controls exist.

The Scrum Guide sets nothing that must exist before the first sprint, and says Scrum "wraps around
existing practices or renders them unnecessary". So the artifacts here sit around a Scrum team's
sprints, for the sponsor, the budget, the dates and the risks, and do not replace them.

There are two paths:

- **A new project** runs sections 2 to 7 in order.
- **A project that is already running** starts with section 8, which says what to do first and how
  to reach the same artifacts without stopping the work.

Each step has the same parts. **Do** says what to do and links the rule. **Why** says what the step
gives the team. **Scenario** shows what goes wrong without it, mostly in the project of
[project-example.md](project-example.md): Acme Corp moves its card payments to a new provider, with
Jane Doe as the sponsor and John Smith as the project manager. **Ask** lists the questions that fill
the artifact, and whom to ask. **You end with** names what exists when the step is done.

Before step 1, or R1 on a running project, copy the checklist of section 10 and fill a row as each
step ends.

Keep each artifact as short as the project allows: on a small project, one team for a few months,
each fits on one page or in a few lines ([operating-system.md](operating-system.md) section 3). A
short artifact is one people keep current, and a stale one misleads.

## 2. Once per team: the tools

### Step 1. Make each change traceable, and give the pages a home

**Do.** Before the first project, make sure anyone can follow a change from the goal to the release,
and that each artifact has a place to live. A Jira admin does most of it. In Jira terms this is:

- A company-managed software space, chosen before the first work item
  ([jira-fields.md](jira-fields.md) section 4).
- Versions, so each work item can get a Fix version ([tickets.md](tickets.md) section 5). A
  company-managed space has them; a team-managed space turns them on
  ([Atlassian: enable releases and versions](https://support.atlassian.com/jira-software-cloud/docs/enable-releases-and-versions/)).
- The repository host and the CI/CD tool connected to Jira, so branches, pull requests and
  deployments show on each work item ([principles.md](principles.md) section 5,
  [tickets.md](tickets.md) section 4, [release.md](release.md) section 7).
- The seven board statuses, with a resolution set on the move to Canceled
  ([jira-workflow.md](jira-workflow.md) sections 2 and 5).
- Time logging off, unless a named decision needs hours ([principles.md](principles.md) section 2).
- A home for the pages: the charter, the registers, the RACI matrix, the plan and the status
  updates, each where its file says ([charter.md](charter.md) section 5,
  [stakeholders.md](stakeholders.md) section 2,
  [roles-and-decisions.md](roles-and-decisions.md) section 3, [risks.md](risks.md) section 2).

**Why.** Every later step writes into one of these places. When the key of a work item is in a
branch name and the tools are connected, anyone can follow a change from the goal to the code and
to the release without asking a person ([principles.md](principles.md) section 5). Set up in a
hurry, the space costs a migration months later, and an unconnected repository lets an unreviewed
change ship, as the scenario below shows.

**Scenario.** A team starts its first sprint in a space it created in a hurry as team-managed. Three
months later it needs components to route bugs to the payments area, and finds that a team-managed
space has no components and that its fields belong to that one space
([jira-fields.md](jira-fields.md) section 4), so getting components means migrating the work to a
company-managed space and building its fields again. In the same team, nobody connected the
repository host, so the release page cannot warn that a Done item still has an open pull request
([release.md](release.md) section 7), and an unreviewed change ships.

**Ask** the Jira admin: who may change the workflow and the board? Is the repository host connected,
and does the Development panel show on a work item? Where do the team's pages live?

**You end with** a space whose work items show the Development panel, with the repository host and
the CI/CD tool connected; the first released work item later passes the check of
[principles.md](principles.md) section 5.

## 3. Initiation

### Step 2. Check it is a project, name the sponsor, open the decision log

**Do.** Ask what change the work delivers and when it ends. Work with neither is operations and
gets a board, and an SLA where users depend on it, not a charter
([principles.md](principles.md) section 6). Name one sponsor ([charter.md](charter.md) section 1).
Open the decision log page ([roles-and-decisions.md](roles-and-decisions.md) section 7) and write
in it the decisions already made.

**Why.** A charter, a baseline and a closure only mean something for work that ends. Starting a
project is a decision, and the sponsor makes it: PRINCE2 7 starts a project by asking "do we have a
viable and worthwhile project?", and says "The decision to start the project must be explicit". One
sponsor is the one person who approves a change to the goal. The decision log starts now because
the first hard decisions come before the charter does.

**Scenario.** In the example, the decision to move payment traffic in steps (1%, 10%, all) was made
on 2026-10-12, a week before the charter, and the charter names those steps. Without the log, three
months later somebody proposes moving all traffic in one night "to save time", and nobody can find
why the team said no: the flag can turn traffic back in minutes, and one night has no way back
without a new deploy.

**Ask** the person who asked for the work: what changes when this is done, and by when? Who pays for
it and can stop it? Who decides when the goal and the date cannot both be met? What did earlier
projects of this kind teach us, and where are those lessons written?

**You end with** a named sponsor, a project that ends, and a decision log with its first entries.

### Step 3. Write the charter

**Do.** The project manager drafts the charter with the sponsor, before any plan, and the sponsor
issues it in writing ([charter.md](charter.md) sections 1 and 2, which list its parts). It is one or
two pages and an hour or two of work, not a week: Johanna Rothman reports that teams write one "in
less than two hours. (Often, just one hour.)" Check each assumption by its date; one proved false
goes to the risk register as an issue ([charter.md](charter.md) section 2).

**Why.** Every later step is measured against this page. The plan is checked against the goal, the
WBS is cut from the scope line, and the fixed constraint tells the team what to give up when work
runs late: scope, not the date, or the other way round ([principles.md](principles.md) section 6).
Rothman calls the hour "a tradeoff of small up-front time to help everyone understand how to make
decisions", and asks the team to "Know What Done Means at the Start", which is why each success
criterion carries a number.

**Scenario.** The example's charter names the date as fixed, because the old provider's contract
ends on 2027-03-31, and it says the provider's test environment will be ready by the end of planning,
to be checked on 2026-11-16. The check failed that day, so the team knew ten weeks before the first
milestone that test payments would start late. It later cut the holds at 1% and 10% from three
weeks to two, instead of asking for a date that did not exist
([project-example.md](project-example.md) sections 2 and 3). Without the dated assumption, the team
would have found the late environment when the test payments were due.

**Ask** the sponsor:

- What problem does this solve, and how will we measure that it is solved?
- What is out of scope, even if someone asks for it later?
- It is three weeks before the end date, the features are not finished and there are more defects
  than you like. Do you ship on the date, wait for all the features, or wait until the defects are
  fixed? (Johanna Rothman's question; the answer is the fixed constraint.)
- What are we assuming that nobody has checked yet, and by when can we check it?
- Who else must say yes, and on what?
- How much may it cost, which dates are the big steps, what could stop it, and what may I decide
  without you? ([charter.md](charter.md) section 2 lists these parts.)

**You end with** the charter page, issued by the sponsor and approved in writing
([charter.md](charter.md) section 1).

### Step 4. List the stakeholders

**Do.** Starting from the charter's approvers and informed people, list everyone the project
affects or who can affect it, ask each of them who else the change touches, and keep them all in
one register ([stakeholders.md](stakeholders.md) sections 1 and 2). Then plan how to close the gap
between how engaged each one is and how engaged the project needs them to be
([stakeholders.md](stakeholders.md) section 4).

**Why.** An approver found late delays the project, and a user group found late finds that the
result does not fit them. One owner per row makes sure each stakeholder hears from one person.

**Scenario.** In the example, the head of security approves the provider contract's data clauses,
and the register gave that row an action: walk through the clauses by 2026-11-27, before the
contract is signed. Without the register, the team meets the head of security at signing, the
contract waits two weeks for a review nobody planned, and its December milestone slips.

**Ask** each stakeholder: what do you need from this project, and what do you fear from it? Who else
does this change touch? How and how often do you want to hear from us?

**You end with** the stakeholder register, linked from the charter page.

### Step 5. Hold the kickoff and name the roles

**Do.** After the sponsor has issued the charter, hold one kickoff, in the order of
[meetings.md](meetings.md) section 3. Use it to name a person for each role
([roles-and-decisions.md](roles-and-decisions.md) section 1). Run Atlassian's roles and
responsibilities team exercise in it (Atlassian calls it a play), to find the work everyone thinks
someone else holds ([roles-and-decisions.md](roles-and-decisions.md) section 4).

**Why.** The team hears the goal from the person who owns it, and leaves with the same picture of
what done means. A doubt raised at the kickoff costs a minute; raised in week six it costs a change
request. The exercise finds the gaps in ownership before anything is dropped.

**Scenario.** Without the exercise, the developer who writes the routing flag thinks the payments
team will remove it after the move, and the payments team thinks the flag is the developer's.
Nobody removes it, and a dead flag stays in the checkout code, the trap
[release.md](release.md) section 6 describes. In the example the flag removal has its own work
item, `PROJ-150`, made together with the flag.

**Ask** each person at the kickoff: what is your role on this project, and what are your top three
responsibilities? Which of the responsibilities others named for you do you accept? What is still
unclear about the goal or the scope?

**You end with** the roles named, every unassigned responsibility given an owner or taken out of
scope, and the sponsor's comment on the charter page that the work has started
([meetings.md](meetings.md) section 3).

## 4. Planning

### Step 6. Break the scope into deliverables

**Do.** Cut the charter's scope into deliverables, not phases or teams, then into work packages you
can estimate and own; keep far work as planning packages until it comes near
([wbs.md](wbs.md) sections 2 to 5). Give each element a dictionary entry
([wbs.md](wbs.md) section 6). Map the deliverables to epics ([wbs.md](wbs.md) section 7), created
by the person [jira-work-item-types.md](jira-work-item-types.md) section 4 names, and make the RACI
matrix ([roles-and-decisions.md](roles-and-decisions.md) section 3).

**Why.** The WBS is the list of what the project must deliver, so a gap in it is work nobody
planned, and work outside it is scope creep. One Accountable per deliverable means one person
answers when it is late or wrong, however many people work on it.

**Scenario.** Without the dictionary, the sponsor reads "payment records migration" as "every old
record shows its provider", and the team reads it as "new payments record the provider". The
difference shows at acceptance, when the backfill of old records has not been planned at all. In
the example, the epic's done-when names the backfill, so it is a planning package from the start
([project-example.md](project-example.md) section 4). Without the RACI matrix, the backfill of old
records has three people who each think another one answers for it, and it is found late at
acceptance.

**Ask** the team and the sponsor: what does the sponsor accept or reject at the end? Does each
element's work add up to all of its parent's work? Who answers for each deliverable? What is near
enough to cut into work items now? Ask each person on the team, for each deliverable: do you do
it, answer for it, need to be asked, or only need to be told
([roles-and-decisions.md](roles-and-decisions.md) section 3)?

**You end with** the WBS with its dictionary, the deliverable epics in Jira, and the RACI matrix.

### Step 7. Pick the approach and draw the schedule

**Do.** For each deliverable, pick predictive, adaptive or hybrid, and write why
([life-cycle.md](life-cycle.md) section 4). Put the milestones into Jira as versions with dates, and
show the schedule on the Timeline ([project-plan.md](project-plan.md) section 3). Link the work
that waits, let the people who do the work estimate it in ranges
([schedule.md](schedule.md) sections 1 and 2), and find the critical path where
[schedule.md](schedule.md) section 3 asks for one.

**Why.** A contract or a migration window is planned as a dated milestone, and software whose
requirements will change runs in sprints; one approach for all of it fits neither. A range tells the
sponsor how sure the team is, and the critical path tells everyone which delay moves the end date
and which does not.

**Scenario.** A team gives one date, "test payments by the end of January", and the sponsor plans
the marketing around it. The work lands in mid-February. Had the team given a range, the sponsor
would have planned around its late end. The reason is measured: a project leader who says they are
90 percent sure of a maximum is right 60 to 70 percent of the time
([schedule.md](schedule.md) section 2).

**Ask** the people who do the work (the Developers of the Scrum Guide): what is the shortest and the
longest this could take? What does this work wait for, inside and outside the team? Ask the
sponsor: which dates are fixed by a contract or by law?

**You end with** the approach per deliverable, versions with dates, linked dependencies, estimates
as ranges, and the critical path where schedule.md section 3 asks for one.

### Step 8. Find the risks

**Do.** Run a pre-mortem with the team: imagine the project has failed and write down why
([risks.md](risks.md) section 8). Record each risk in one register, give it an owner and a response
([risks.md](risks.md) sections 2, 4 and 5), and plan in advance for the threats that would do the
most damage ([risks.md](risks.md) section 6).

**Why.** The pre-mortem finds risks while the plan can still change. One owner per risk is the one
person who watches it. A contingency plan made before the trigger fires is made calmly; one made
after it is made during the damage.

**Scenario.** In the example the pre-mortem on 2026-11-02 found that the draft contract had no
uptime clause (R-2), while the contract could still change. The team asked for the clause, with a
plan for the case that the provider refused it. Found after signing, the same gap would have left a
provider outage with no response time, and the only fix would have been to keep the old provider on
standby for USD 4,000 a month ([project-example.md](project-example.md) section 5).

**Ask** the team: it is the end date and the project has failed; what happened? For each risk: who
watches it, what do we do about it now, and what tells us it is happening?

**You end with** the risk register, linked to each deliverable epic.

### Step 9. Plan who hears what

**Do.** Write one line for each stakeholder group: what they hear, how often, through which channel
and from whom ([communication.md](communication.md) section 1), and write the escalation path
([communication.md](communication.md) section 4).

**Why.** Each message then has a sender, and a line with no sender is a message nobody sends.

**Scenario.** A team member sits blocked for four days on a provider question the team cannot
answer, because nobody wrote whom to go to. In the example, a Developer goes to John Smith, who
answers the same working day. John Smith goes to Jane Doe, who answers an exception note within one
working day ([project-example.md](project-example.md) section 3). An exception note is the short
message that tells the sponsor a date is beyond the tolerance
([communication.md](communication.md) section 5).

**Ask** each stakeholder group, from the register: who needs which information, in what format, and
at what time (PRINCE2 7's question)? Ask the sponsor: who is above you when a decision is outside
your authority? Ask the people on the escalation path: how soon does each level answer
([communication.md](communication.md) section 4)?

**You end with** the communication lines in the plan, and the escalation path.

### Step 10. Write the deciders and the rhythm, and baseline the plan

**Do.** Write in the plan who decides each kind of decision, one person per kind
([roles-and-decisions.md](roles-and-decisions.md) section 5). Write the rhythm of the reviews and
the board look ([project-plan.md](project-plan.md) section 6,
[operating-system.md](operating-system.md) section 2). Choose which conditional artifacts the
project keeps ([operating-system.md](operating-system.md) section 3). If the plan cannot meet the
charter's fixed constraint, the change comes out of a constraint that is not fixed
([principles.md](principles.md) section 6). A cut to the scope boundary or the budget is a charter
change the sponsor approves ([charter.md](charter.md) section 3). Agree a tolerance with the
sponsor. Have the sponsor approve the plan as the baseline, with change control from then on
([project-plan.md](project-plan.md) section 4). Define the three status markers, On track, At risk
and Off track, against the tolerance before the first update
([communication.md](communication.md) section 3). Off track sends the exception note
([communication.md](communication.md) section 5). From the week after the sponsor approves the
baseline, run the loop of step 15. Steps 11 to 14 happen alongside it, each at its own moment.

**Why.** A decision with two deciders waits for both, and one with none is made by whoever moves
first. Without a baseline nobody can say whether the project is late. The tolerance is what PRINCE2 7
calls "limits of delegated authority": inside it the project manager decides, beyond it the sponsor
does, so the sponsor's time goes to the changes that move the goal. Markers defined in advance stop
the update from saying "on track" until the week the milestone is missed. Atlassian calls the fix
"a social contract among all teams for when and why to change your project's status". The rhythm
written in the plan makes the reviews happen without anyone having to call them.

**Scenario.** In the example, the tolerance lets a milestone move one week on the project manager's
decision. When the late environment pushed two milestones by two weeks, the move was beyond the
tolerance, so it went to the sponsor as a change request with the old and the new dates and the
reason ([project-example.md](project-example.md) section 3). Without the baseline, the dates would
have been edited quietly, and at closure nobody could have said how far the project slipped or why.

Without marker definitions, the project manager writes "green" each Friday because the team is busy
and nothing is on fire. The test environment is four weeks late, but the milestone is still two
months away, so it feels fine. The sponsor hears about the slip at the milestone, when the only
options left are expensive. Atlassian calls this a watermelon status: green outside, red inside
([communication.md](communication.md) section 3).

**Ask** the sponsor: how far may a milestone move before you want to decide? How soon will you
answer an exception note? Ask whoever will write the update: how safe do you feel choosing a status
that is not green (Atlassian's question)? Ask the team: which technical choice is hard to undo, and
which of you decides it? On which day and time do we review the plan and look at the board? And,
when you pick the conditional artifacts, Rothman's question: how little can we do to satisfy our
needs?

**You end with** the plan, approved by the sponsor as the baseline, with its tolerance, its
deciders and its rhythm, and the marker definitions.

## 5. Execution

### Step 11. Agree how the team works before the first sprint

**Do.** Agree one Definition of Done for the team ([tickets.md](tickets.md) section 2), and a limit
on work in progress per person and for the team ([principles.md](principles.md) section 3). Pick
sprints or a flow ([life-cycle.md](life-cycle.md) section 4), the sprint length, and the meetings
with their cadence ([meetings.md](meetings.md) section 2, or section 9 for a team without sprints).
Keep work items small, each with its own branch and pull request
([tickets.md](tickets.md) sections 3 and 4). Atlassian's working agreements exercise, one hour with
the whole team, agrees the meeting plan and how the team talks and escalates. Write the first work
item of each type from [jira-work-item-example.md](jira-work-item-example.md), so the team copies a
complete one.

**Why.** A shared Definition of Done means Done means the same on every work item. A
work-in-progress limit shows a person who holds too much before it shows as a missed date. A small
work item is easy to review, easy to roll back and easy to find when an SLA clock runs.

**Scenario.** In the example, a bug found in staging sent saved-card payments to the new provider
with the flag off (`PROJ-131`). The work item was small, so the fix was one commit on the day it was
found ([project-example.md](project-example.md) sections 6 and 9). In a team whose work items run
for two weeks, the same bug sits inside a large pull request with three other changes, and the
release waits for all of them.

**Ask** the team: what must be true before we call a work item Done? How many items can one person
hold at once before work slows down? Can we agree a Sprint Goal every two weeks, or does our work
arrive unplanned?

**You end with** the Definition of Done, the work-in-progress limits, the sprint length or the flow,
and the meetings in the team's calendar.

### Step 12. Agree severity levels and the SLA before users depend on the result

**Do.** Write the severity levels first, then one SLA clause for each level that has an agreed
restore target ([sla.md](sla.md) sections 1 to 4, which list what a clause names). Map each level
to one Jira priority ([sla.md](sla.md) section 7).

**Why.** Without levels, "critical" means whatever the customer says at 2 a.m. A target with no
consequence is an objective, not an agreement, and a team that calls every target an SLA promises
more than it agreed.

**Scenario.** The first outage comes on a Saturday night. Payments fail for one card brand. The
customer calls it critical, the person on call is not sure whether the 4-hour clock applies, and
the team argues on Monday about whether the clock started at the alert or when the work item was
opened. In the example, the SEV 2 clause answers both: one card brand is SEV 2, 24 hours, from the
alert or the first customer report ([project-example.md](project-example.md) section 7).

**Ask** the sponsor and the customer: what counts as down, and for whom? How fast must each level be
restored, around the clock or in working hours? What happens when we miss it? Ask the team: who
opens the incident and writes the alert time into it?

**You end with** the severity table, one SLA clause for each level that has an agreed restore
target, and each level mapped to one Jira priority.

### Step 13. Plan each release and its go or no-go

**Do.** Plan each release as one Jira version ([release.md](release.md) section 1). Name the one
person who decides go or no-go before it reaches production, and the short checklist they decide by
([release.md](release.md) section 3). Choose how the release reaches users
([release.md](release.md) section 6).

**Why.** One person owns the risk of shipping, so nobody ships because everyone assumed someone else
had checked. The checklist makes the decision a check, not a feeling.

**Scenario.** Without a go or no-go check, a release goes out with a change merged to main from a
work item that belongs to the next version. It was not tested with this release, and it breaks
checkout. The example's checklist has a line for exactly this: main holds no change of a work item
outside this version ([project-example.md](project-example.md) section 8).

**Ask** the release decider: what must be true before this version goes out? How does the release
reach users: all at once, in steps, or behind a flag?

**You end with** a version per release, a named decider, and the checklist the decider will use.

### Step 14. Write and rehearse the rollback plan

**Do.** For every release that changes production, write the rollback plan before the deploy
([rollback-plan.md](rollback-plan.md) sections 1 and 2, which list its parts). Change data in steps
that keep the old release working ([rollback-plan.md](rollback-plan.md) section 4), and rehearse the
rollback in a test environment ([rollback-plan.md](rollback-plan.md) section 5). If the measured
time does not fit the restore target, the plan fails the check of
[rollback-plan.md](rollback-plan.md) section 2, and the release decider says no-go on the rollback
line until it fits ([release.md](release.md) section 3).

**Why.** During an incident there is no time to design the way back. A plan that was never run has
an unknown time, and the time is what the SLA needs.

**Scenario.** In the example, the rehearsal on 2027-02-19 measured seven minutes from turning the
flag off until all test payments went to the old provider, and found that the on-call role could
not change the flag in staging. The permission was added the same day
([project-example.md](project-example.md) section 8). Without the rehearsal, the missing permission
is found during a real outage, at night, while the SLA clock runs and the person on call searches
for someone with admin rights.

**Ask** the release decider and the person on call: what number tells us to roll back? Who decides,
and who decides when they do not answer? Can the old release run against the new data? From the
alert to restored, how long does the way back take, and does it fit the restore target of the SLA?
How do we go back: redeploy the previous version or turn the flag off? Who must hear that we rolled
back?

**You end with** a rollback plan in each production release's version, and a rehearsal with its
measured time.

## 6. Until closure: the loop

### Step 15. Run the loop: each week and at each phase end

**Do.** From the week after step 10, run the rows of
[operating-system.md](operating-system.md) section 2 from "Every week" to "Every phase end", on the
days step 10 wrote into the plan. Each row names the rule it runs; the weekly status update comes
first ([communication.md](communication.md) sections 2 and 3). Until the sponsor decides on an
exception note, the team keeps working to the current baseline
([communication.md](communication.md) section 5), and the next update names the decision it still
needs ([communication.md](communication.md) section 2).

**Why.** This is the loop that keeps every artifact from steps 2 to 14 current. An artifact nobody
looks at goes stale, and a stale plan is ignored, so it stops helping any decision
([operating-system.md](operating-system.md) section 2). The phase end is where the sponsor decides
whether the project goes on, on the evidence of the phase that just ended.

**Scenario.** In the example, the update of 2026-12-18 was Off track: the forecast for test payments
was 8 to 12 February against a baseline of 29 January, beyond the one-week tolerance. The exception
note sent the same day gave two options with what each cost, and the sponsor chose one in a single
reply on 2026-12-21 ([project-example.md](project-example.md) section 3). Without the loop, the same
slip reaches the sponsor in February, when only the expensive option is left.

**Ask** at each update: what is the late date of the forecast, and is it inside the tolerance? What
do we need from the readers this week? At the board look: who holds too much, and which date or
scope moves because of it ([principles.md](principles.md) section 3)? At a phase end: which risks
and stakeholders changed since the last review?

**You end with** a status update on the page every week, a decision in the log for every change
beyond the tolerance, and an approval on the page at each phase end.

## 7. Closure

### Step 16. Close the project

**Do.** The sponsor accepts the result in writing against the charter's success criteria. Give each
open risk an owner after the project and a follow-on action. Hold a retrospective and record each
lesson with an owner and a date. Close the epics ([life-cycle.md](life-cycle.md) section 2). If the
sponsor stops the project instead of accepting it, the stop and its reason go into the decision log
([roles-and-decisions.md](roles-and-decisions.md) section 7).

**Why.** The result is judged by the goal, not by the schedule. A risk handed over is not dropped
when the team moves on, and a lesson with an owner turns into a change, not only a note. The next
project reads those lessons in its step 2.

**Scenario.** In the example, the provider's uptime clause stays a risk after the project. At
closure, R-2 went to Richard Roe, for the on-call team, with a monthly check against the 99.9%
clause ([project-example.md](project-example.md) section 9). Without the handover, nobody watches
the clause, and the first long provider outage after the project finds no one who knows it was
promised.

**Ask** the sponsor: is each success criterion met, measured as the charter says? Ask the team:
which open risks remain, and who owns each from now on? What will we do differently next time, who
changes it, and by when?

**You end with** the sponsor's acceptance on the charter page, or the logged decision to stop,
every open risk handed over, lessons with owners, and closed epics.

## 8. A project that is already running

A running project cannot stop for a month to write documents, and it should not change everything
at once: a team that gets ten new rules in one week cannot tell which one helped, and it starts to
see the whole practice as paperwork. Kanban University's Kanban Method starts any change with
"Start with what you do now", and says "Kanban is not a big bang transformation". Elizabeth Harrin,
writing on taking over a project, advises the same: match "what you are trying to do and the
standards to which you want to do it to the company culture", and improve step by step. PMI's PM
Network asks the question to put to every change: "before reconfiguring the work breakdown structure
or introducing a new task tracker, it's worth asking: Will this truly improve the workflow or create
better project outcomes?" So split the work in two:

- **What the project manager writes with the sponsor**: the charter, the baseline, the rollback
  plan, and the registers, plans and weekly update of step R7. These do not change how the team
  works day to day, so write them in the first weeks, in the order below.
- **How the team works**: the board, the Definition of Done, the work-in-progress limit, the
  meetings, the size of work items. Change these one at a time (step R6).

### Step R1. Learn what is there before you change it

**Do.** In the first week, before you change anything, find out:

- Your role, your authority and the escalation path.
- The goal and the date as the sponsor sees them.
- What has been promised, to whom and by when.
- The budget, and who can spend it.
- The plan and the decisions already made.
- Which artifacts of sections 2 to 7 exist, and whether each holds what its step's "You end with"
  names.

Read the board and the last two weeks of work on it: items that have not moved, two people on the
same work, items with no description. Write each gap as a fact with an example. If R1 finds no
single named sponsor or no decision log, do step 2 before R2.

**Why.** You can only fix what you understand, and a fact with an example is what moves the sponsor
in step R2. Three independent sources start a take-over the same way. Owen Gadeken, in a PMI
congress paper: "So your first job—other than to respond to crises—before you make any decisions
is to assess the current state of the project", starting with the predecessor and the documents.
Fred Wenger, quoted in PMI's PM Network, gathers what the team, the sponsor and the stakeholders
know before he reads the charter and the documents. Harrin's checklist starts with your role and
the escalation paths, then the objectives, the plan, the governance, the budget and the logs that
already exist.

**Scenario.** A new project manager joins and, in the first week, replaces the team's board with
seven new statuses. Two developers lose track of their work, and the team decides the new manager
does not understand the project. The board did have a real problem, three items that had sat in
progress for a month, but by then nobody listened. Shown to the sponsor first, those three items
would have given the change a reason everyone could see.

**Ask** the team and the previous project manager: what is the goal, in your words? What has been
promised to whom, and by when? What worries you about the next release? Which decisions are made,
and where are they written? How safe do you feel reporting a status that is not green? And
Wenger's question: "If you could change one thing about how the project has been managed to date,
what would that be?"

**You end with** a short list of gaps, each a fact with an example, and a note of which artifacts
already exist.

### Step R2. Agree the gaps with the sponsor

**Do.** Meet the sponsor alone, before you change anything the team sees. If a deploy is due before
you can meet the sponsor, do R3 first and report it in this meeting. For each gap, say what it
could cost in dates, money or risk to customers, and bring one or two options. Write what you agreed
into the decision log ([roles-and-decisions.md](roles-and-decisions.md) section 7) the same day,
and send it to the sponsor.

**Why.** The sponsor issues the charter and owns the tolerance, so nothing below holds without them.
A problem with options gets a decision; a problem alone gets a worry. The meeting comes after R1,
not before it: Gadeken advises to put off such meetings until you have "at least a preliminary
assessment of your project; otherwise, you may find yourself making promises or commitments you
can't keep." An agreement written down the same day cannot be read two ways later.

**Scenario.** The project manager tells the sponsor in passing that releases "feel risky", and the
sponsor agrees to look at it. Nothing changes. A week later the manager brings one page: two
customers wait for the next release, it has no version and no way back, and there are two options.
Name a decider and write a rollback plan this week, for half a day of the lead developer's time; or
ship as it is and accept a night of downtime if it fails. The sponsor picks the first in the
meeting.

**Ask** the sponsor: what must this project deliver, by when, and what is fixed? What worries you
most? Which gap do you want closed first?

**You end with** the sponsor's decision on each gap, in the decision log.

### Step R3. Make the next release safe

**Do.** Before the next deploy to production, name its go or no-go decider and write its rollback
plan (steps 13 and 14), even if the charter does not exist yet. If the space has no versions, or
the repository host is not connected to it, set those up first (step 1), so the release page can
warn ([release.md](release.md) section 7). If the project has no severity levels yet, write them
and a restore target for each first ([sla.md](sla.md) section 2). Then the plan's Time part (the
time from alert to restored) has a target to fit ([rollback-plan.md](rollback-plan.md) section 2).
A target with no agreed consequence if it is missed is only an objective (an SLO,
[sla.md](sla.md) section 1). The full SLA waits for R7 (step 12). When a deploy is due before you
have finished R1, do this step first.

**Why.** The next deploy comes before any plan review, and a release with no way back is the gap
that can cost the most in one night. The rule is not new for a running project:
[rollback-plan.md](rollback-plan.md) section 1 asks for a rollback plan before every release that
changes production. A running project only does it first: Gadeken lets the response to crises come
before the assessment, and this guide treats a deploy with no way back as one.

**Scenario.** A release fails on its first evening. The team has no list of what changed and no
named person to decide, so it spends an hour arguing whether to roll back while payments fail. With
a decider and a trigger written down, the rollback starts when the trigger fires.

**Ask** the lead developer and the person on call: what number tells us to roll back? Who decides,
and who decides when they do not answer? Can the old release run against the new data? From the
alert to restored, how long does the way back take, and does it fit the restore target?

**You end with** a decider and a rollback plan for the next release.

### Step R4. Write the charter and the baseline as of today

**Do.** Write the charter from today on (step 3): the goal as it stands, the scope still to deliver,
the fixed constraint and the success criteria, and have the sponsor issue it. If the milestones are
not yet Jira versions with dates, do step 7 first: versions with dates and estimates as ranges. At
the next plan review, or at one you hold for this, have the sponsor approve today's plan as the
baseline, with a tolerance (step 10). If the sponsor approved dates before, those are the first
baseline: keep them as Original, and write today's approved dates as Baseline, through a change
request that holds the old date, the new date, the sponsor's approval and the reason
([project-plan.md](project-plan.md) section 4). Original is the first approved date, and Baseline
is the current approved date ([project-plan.md](project-plan.md) section 4).

**Why.** The plan needs a goal to be measured against, and the project's history changes no open
decision, so the charter is written from today and does not record the past. Wenger's advice for an
inherited project is the same: "In a sense, you approach it as if you were starting a new project".
The baseline split is this practice's own rule, from [project-plan.md](project-plan.md) section 4:
the weekly marker needs a baseline and a tolerance to compare with
([communication.md](communication.md) section 3), and the earlier approved dates stay as Original,
so the new baseline does not hide the slip that came before it.

**Scenario.** A project promised for March is re-planned for May when the new manager arrives. If
the plan shows only May, then in July the sponsor sees "two months late against the baseline" and
has forgotten the first two. With March as Original and May as Baseline, the page shows both.

**Ask** the sponsor: which dates did you approve before, and when? How far may a milestone move
from here before you want to decide?

**You end with** the charter issued, and the plan baselined with a tolerance and its earlier dates
kept.

### Step R5. Move the open work, leave finished work as it is

**Do.** When the team has taken the statuses of step 1 into use, which R6 decides, move every open
work item into them. An item that goes to Blocked or Canceled follows
[jira-workflow.md](jira-workflow.md) sections 4 and 5. An open item gets its type
([jira-work-item-types.md](jira-work-item-types.md) section 1), its Fix version
([tickets.md](tickets.md) section 5) and its acceptance criteria
([tickets.md](tickets.md) section 2) the next time someone works on it. Leave Done items as
they are.

**Why.** Open work is what the team and the sponsor decide about now, and rewriting finished items
costs time that no decision gets back ([principles.md](principles.md) section 2). It is the same
split [refactoring.md](../refactoring/refactoring.md) section 2 makes for code: new and touched
work follows the practice, and untouched work stays as it is.

**Scenario.** A team spends two days giving three hundred closed items a type and a version, so the
reports look complete. Nobody opens those reports, and the two days came out of the sprint that had
the release in it.

**Ask** the Jira admin: how do the old statuses map to the new ones? Ask the team: which open items
are still real work? Ask the Product Owner: which can be canceled?

**You end with** every open work item on the board the team kept at R6, and finished work
unchanged.

### Step R6. Change how the team works one step at a time

**Do.** Take the changes to how the team works (step 11, the board of step 1, the meetings) one at a
time, in the order the team agrees. Try each for one sprint, or two weeks in a team without
sprints, and decide at the retrospective whether to keep, change or drop it
([meetings.md](meetings.md) section 8). Atlassian's working agreements exercise fits this moment
too: Atlassian names "when work scenarios change" among the times to run it.

**Why.** A trial with a review date lets the team judge each change by what it did, not by how it
was introduced. Johanna Rothman asks teams for "one experiment at a time", because the more
experiments come out of one retrospective, the fewer of them get finished; Scrum Alliance's guide
to change puts it as "The goal isn't to fix everything at once."

**Scenario.** A team that has never held a Daily Scrum tries it for one sprint, at 15 minutes. At
the retrospective it keeps the meeting and moves it to the afternoon. Another team gets the Daily
Scrum, the work-in-progress limit, the new board and the Definition of Done in the same week.
Within a month it drops all four, and nobody can say which one was the problem.

**Ask** at each retrospective: what did this change give us, and what did it cost? Do we keep it,
change it or drop it? What do we try next?

**You end with** each change kept, changed or dropped at a retrospective, as an action with an
owner and a date.

### Step R7. Close the other gaps

**Do.** Take each of the steps below whose artifact R1 found missing or short of its
"You end with", in the order of this guide. The project manager writes these with the sponsor and
the team. They do not change how the team works day to day, so do them in the first weeks after R4:

- The stakeholder register (step 4).
- The named roles (step 5, without the kickoff).
- The WBS and the RACI matrix (step 6).
- The risk register (step 8).
- The communication lines and the escalation path (step 9).
- The deciders, the rhythm and the markers (step 10).
- The SLA clauses (step 12).

Steps 11, 13, 14 and 15 belong to R6, R3 and the loop, and step 16 to closure. Start the weekly
loop of step 15 in the first week after R4 sets the tolerance. Before that first update, do
step 7's estimates as ranges, step 10's markers and step 9's escalation path. The risk review of
the loop starts once step 8's register exists. Changes to how the team works stay with R6.

**Why.** Every project keeps the stakeholder register, the RACI matrix, the risk register and the
weekly status update with its escalation path, each as short as the project allows
([operating-system.md](operating-system.md) section 3), and steps R1 to R6 write none of them.
R4's baseline is what the weekly update compares the forecast with
([communication.md](communication.md) sections 2 and 3); with no update, nobody reads it, and a
slip reaches the sponsor at the milestone instead of in the week it starts.

**Scenario.** Six weeks after taking over, a project manager has the charter issued and the plan
baselined, and the team is trying its first change of R6. Nobody has started the weekly update,
because the team never had one. The next milestone slips by three weeks, beyond the tolerance, and
the sponsor hears of it at the milestone, when only expensive options are left. With the update
running from the week after R4, the slip would have reached the sponsor in the week it began.

**Ask** the people each step names, with that step's own questions. Ask the sponsor: on which day
of the week do you read the status update?

**You end with** each artifact of the list above that R1 found missing or short of its
"You end with", and a status update on the page every week since the first week after R4.

## 9. Bring the team along

The steps produce artifacts; whether people use them depends on how the steps are introduced. Four
habits help, on both paths:

- Say what decision each step serves, in the listener's terms: a date, money, a risk to customers.
  The test is the sentence of [principles.md](principles.md) section 2, "We will decide X from
  this." The reason: people skip a rule whose purpose they cannot see as soon as it costs them time.
- Ask before you assign: in step 5 each person names their own responsibilities. The reason: a
  responsibility a person named is one they know they hold.
- Keep the same rules for everyone. The sponsor's urgent change and a senior engineer's side work go
  through work items too ([tickets.md](tickets.md) section 1). The reason: work outside Jira is the
  work nobody can trace when something breaks, and a rule senior people skip reads as control of
  the others.
- Show the board, never the person ([principles.md](principles.md) sections 2 and 3). The reason: a
  practice that watches people turns into micromanagement, and people work around it.

## 10. The adoption checklist

Copy this block to a page linked from the charter page, and fill one row as each step is done.
Until step 2 opens the decision log, keep it with the team's pages of step 1. After that, and until
the charter exists, link it from the decision log. A running project marks a step done, with its
link, only when what exists holds the row's text. The other rows stay open for R7. A running
project also adds a row at the top for each of steps R1 to R7. Each has that step's "You end with"
as its text and the project manager as its owner. R6's row is owned by the Scrum Master, who owns
row 11. The rows of steps 1 to 16 still open after R7 are then done in row order, except row 11,
which R6 takes one change at a time. Mark row 11 done when R6 has kept, changed or dropped each of
its changes.

```markdown
# Adoption checklist: <project name> (<space key>)

Path: new project | running since <date>
Sponsor: <name>. Project manager: <name>.
Guide: <link to adoption-guide.md in your repository>. Step N there says what to do, why, and
whom to ask.

| Step | What exists when it is done | Link | Owner | Done on |
|---|---|---|---|---|
| 1 | Space whose work items show the Development panel, with the repository host and the CI/CD tool connected; the first released work item later passes the check of principles.md section 5 | <link> | <Jira admin> | |
| 2 | Sponsor named, a project that ends, decision log with its first entries | <link> | <project manager> | |
| 3 | Charter page issued by the sponsor and approved in writing | <link> | <project manager> | |
| 4 | Stakeholder register, linked from the charter page | <link> | <project manager> | |
| 5 | Kickoff held, roles named, every responsibility owned or out of scope, sponsor's start comment on the charter page | <link> | <project manager> | |
| 6 | WBS with dictionary, deliverable epics, RACI matrix | <link> | <project manager> | |
| 7 | Approach per deliverable, versions with dates, linked dependencies, estimates as ranges, critical path where schedule.md section 3 asks for one | <link> | <project manager> | |
| 8 | Risk register after a pre-mortem, linked to each deliverable epic | <link> | <project manager> | |
| 9 | Communication lines in the plan, escalation path | <link> | <project manager> | |
| 10 | Plan approved by the sponsor as the baseline, with tolerance, deciders and rhythm, and marker definitions | <link> | <project manager> | |
| 11 | Definition of Done, work-in-progress limits, sprint length or flow, meetings in the team's calendar | <link> | <Scrum Master> | |
| 12 | Severity table, one SLA clause for each level that has an agreed restore target, each level mapped to one Jira priority | <link> | <project manager> | |
| 13 | A version, a named decider and the decider's checklist, for each release | <link> | <release decider> | from <date>, each release |
| 14 | Rollback plan in each production release's version, rehearsal with its measured time | <link> | <release decider> | from <date>, each release |
| 15 | Weekly status update, a decision in the log for each change beyond the tolerance, approval at each phase end | <link> | <project manager> | every <day> |
| 16 | Sponsor's acceptance on the charter page, or the logged decision to stop, every open risk handed over, lessons with owners, epics closed | <link> | <project manager> | |
```

The checklist is good because each row has one owner, so a step nobody did shows as a name, not a
gap, and the Link column points at the real artifact, so the checklist holds no copy of it that
could go stale. The Done on column lets the sponsor see in one look what is in place. The sponsor
reads it at each plan review to see which step is late and whose it is, and asks that owner for a
date. When every row is done no decision reads it, so archive it
([principles.md](principles.md) section 4).

## 11. Sources

- PeopleCert, [PRINCE2 7 Foundation Quick Reference Guide](https://www.nilc.co.uk/wp-content/uploads/2023/10/PRINCE2-Quick-Reference-Guide.pdf),
  2023, an official training PDF hosted by a training organisation: starting up a project as an
  explicit decision, the order of starting up and initiating, "who needs information, in what
  format, and at what time", tolerances as "limits of delegated authority".
- [PMP Examination Content Outline, July 2026 exam](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/new-pmp-examination-content-outline-2026.pdf),
  PMI, 2026: the tasks, with no order among them.
- [The Scrum Guide](https://scrumguides.org/scrum-guide.html), November 2020: "Scrum wraps around
  existing practices or renders them unnecessary."
- Kanban University, ["The Official Guide to The Kanban Method"](https://kanban.university/kanban-guide/),
  undated, read 2026-10-07: "Start with what you do now"; "Kanban is not a big bang transformation".
- Atlassian Team Playbook, ["Roles and responsibilities"](https://www.atlassian.com/team-playbook/plays/roles-and-responsibilities)
  and ["Working agreements"](https://www.atlassian.com/team-playbook/plays/working-agreements),
  undated, read 2026-10-07.
- Atlassian, ["Define your status markers"](https://www.atlassian.com/dam/jcr:d164f7ba-1fe7-4c1f-bec7-22967945c8b4/Loop-Technique_3-3_define-your-status-markers.pdf),
  2021: the social contract for status, and "how safe do you feel choosing a status that is not
  green?"
- Owen C. Gadeken, ["So you're the new project manager: tips for a good start"](https://www.pmi.org/learning/library/new-project-manager-tips-good-start-6687),
  PMI Global Congress 2009, North America: assess the current state before any decision, and the
  order of the first meetings.
- Ashley Bishel, ["Midstream Maneuver"](https://www.pmi.org/learning/library/inheriting-project-careful-research-smooth-transition-11824),
  PM Network, PMI, 2019-12-01: inheriting a project, with the advice of Fred Wenger and other
  project managers.
- Elizabeth Harrin, ["How to take over an existing project"](https://rebelsguidetopm.com/how-to-take-over-an-existing-project/),
  2024-02-02, updated 2024-09-03: the order of the first checks on a project you take over, and
  matching the standards to the company culture.
- Johanna Rothman, ["How to Create a Useful Project Charter in Less Time Than You Think: Overview"](https://www.jrothman.com/mpd/2025/09/how-to-create-a-useful-project-charter-in-less-time-than-you-think-overview/),
  2025-09-17, and the series' parts 2 (["Clarify the Project Driver"](https://www.jrothman.com/mpd/2025/10/project-charter-part-2-clarify-the-project-driver-boundaries-and-constraints-for-this-project/),
  2025-10-01) and 4 (["Define Release Criteria"](https://www.jrothman.com/mpd/2025/10/project-charter-part-4-define-release-criteria-so-you-know-what-done-means-avoid-scope-creep/),
  2025-10-21).
- Johanna Rothman, ["Agile Project Kickoffs"](https://www.jrothman.com/mpd/2019/07/agile-project-kickoffs/),
  2019-07-09: "How little can we do to satisfy our needs?"
- Johanna Rothman, ["How to Best Learn From Your Retros: Choose One Experiment at a Time"](https://www.jrothman.com/mpd/2026/08/how-to-best-learn-from-your-retros-choose-one-experiment-at-a-time/),
  2026-08-26.
- Scrum Alliance, ["Change management process guide"](https://resources.scrumalliance.org/Article/change-management-process-guide),
  undated, read 2026-10-07.
