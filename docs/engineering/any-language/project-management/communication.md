# Communication and status

How information moves on a project: the communication plan, the weekly written status update and
its three markers, the escalation path, and how the sponsor hears about exceptions and not about
routine. Read this file when you plan the project's communication, each week when you write the
update, and when a forecast goes beyond the plan's tolerance.

**Navigation**

- [1. The communication plan](#1-the-communication-plan)
- [2. The weekly status update](#2-the-weekly-status-update)
- [3. Status markers](#3-status-markers)
- [4. The escalation path](#4-the-escalation-path)
- [5. Management by exception](#5-management-by-exception)
- [6. Sources](#6-sources)

## 1. The communication plan

In planning, write one line for each stakeholder group: what they hear, how often, through which
channel, and from whom. PMI defines the communications management plan as "A component of the
portfolio, program, or project management plan that describes how, when, and by whom information
will be administered and disseminated." (PMI Lexicon, 2026) The groups come from the stakeholder
register ([stakeholders.md](stakeholders.md) section 2), and the plan holds the lines in its
Communication part ([project-plan.md](project-plan.md) section 2). The PMP exam outline lists the
same act: "Analyze and tailor communication to stakeholder needs."

Atlassian's stakeholder communications plan, run "at the beginning of every project", splits the
audience in two: Contributors, whose "time, decisions, or expertise are critical to doing the work",
get frequent, detailed information; Beneficiaries get less frequent, high-level information.

| Group | What they hear | How often | Channel | From |
|---|---|---|---|---|
| The team | The board, the sprint goal | Daily | The board, the Daily Scrum | The team itself |
| The sponsor | The status update; an exception note when it happens | Weekly; at once on an exception | The update page; a direct message for the exception | The project manager |
| Other stakeholders | The status update; the Sprint Review | Weekly; each sprint | The update page; the review | The project manager; the Product Owner |

The table is an example, so each team writes its own; it is good because each line names who sends,
and a line with no sender is a message nobody sends.

## 2. The weekly status update

Write one status update a week, in writing, and do not hold a status meeting for it; a meeting must
decide something ([meetings.md](meetings.md) sections 1 and 10). Atlassian's "Weekly project updates"
play has four steps: reflect on the week; note the decisions, risks and learnings; "Accurately mark
your project's status (e.g., 'On Track,' 'At Risk,' or 'Off Track')" and the due date; then add
comments. Its aim is to "Share a clear, accountable record of project progress".

The update holds, in this order:

1. The status marker (section 3).
2. The forecast of the next milestone as an early and a late date, next to its baseline date
   ([project-plan.md](project-plan.md) section 4), with the report and the sprints it comes from
   ([schedule.md](schedule.md) section 2).
3. What changed this week, and the decisions made, linked to the decision log
   ([roles-and-decisions.md](roles-and-decisions.md) section 7).
4. New or changed top risks ([risks.md](risks.md) section 7).
5. What the project needs from its readers: a decision, a person, a date.

Items 2 and 5 are this practice's own; the rest is the play's. Post it where the sponsor and the
stakeholders read, and link it from the project's epics. PRINCE2 7 calls the same document the
highlight report, which the project manager sends "to provide the project board (and possibly other
stakeholders) with a summary of the stage status at intervals defined by them" (PeopleCert, 2023).

## 3. Status markers

Use three markers, On track, At risk and Off track, and define each against the plan's tolerance
before the first update. Atlassian's guide to status markers says "Define each status in 10 or less
words", and to record and share the definitions so every report uses the same ones. This practice's
default definitions:

| Marker | Means |
|---|---|
| On track | Forecast inside tolerance with no extra action |
| At risk | Inside tolerance only if a named action lands |
| Off track | Outside tolerance even with the planned actions |

Compare the late date of the forecast with the tolerance, since the late end is the one that breaks
it (this practice's own).

Off track is the marker that sends the exception note of section 5.

Set the marker from the forecast, not from how the week felt. Snow and Keil found that "project
managers are overly optimistic in their perceptions, and executives receive status reports very
different from reality" (IEEE Transactions on Engineering Management, 2002, read from the abstract),
and Park, Im and Keil found that the "mum effect", a reluctance to report bad news, contributes to
project failure (Journal of the AIS, 2008, a laboratory experiment, read from the abstract).
Atlassian's guide names the result: "watermelon" status, green outside and red inside. Johanna
Rothman, an independent PM author, makes the same point: status lights work "as long as they are
binary and prompt people to action".

Answer an At risk with help, not blame. Atlassian's play warns: "If teams are penalized for setbacks,
they'll either set less ambitious goals or hide when projects veer off course".

Check: before you post the update, put the late date of the forecast next to the baseline date and the tolerance,
and see that the marker follows from them.

## 4. The escalation path

Write the escalation path in the plan: for each level, the one person it goes to, and how soon they
answer. The PMP exam outline asks the project manager to "Outline governance escalation paths and
thresholds." PRINCE2 7 sets the levels by tolerance: the business sets the project's tolerances, the
project board sets each stage's, the project manager sets each work package's, and each level goes to
the one above when its tolerance is forecast to break (PeopleCert, 2023).

A software project's path is usually four steps (this practice's own mapping):

1. A Developer to the Scrum Master or the project manager, for a blocker the team cannot remove
   ([workflow.md](workflow.md) section 4).
2. The project manager to the sponsor, when a forecast leaves the tolerance (section 5).
3. The sponsor to a steering committee, where the organisation has one, for a decision "outside of
   the team's authority" (PMI Lexicon, 2026).
4. A risk outside the team's authority goes up as a risk response, escalation ([risks.md](risks.md)
   section 5).

Who decides at each level is in [roles-and-decisions.md](roles-and-decisions.md) section 5.

## 5. Management by exception

The sponsor hears about a change only when its forecast, with the planned actions, breaks the tolerance. PRINCE2 7 states the
principle: "A PRINCE2 project establishes limits of delegated authority by defining tolerances for
performance against its plans." An exception is "a situation where it can be forecast that there will
be a deviation beyond the tolerance levels agreed", and the exception report goes to the board "to
inform the project board when a stage plan or project plan is forecast to exceed tolerance levels
set, and to offer options and recommendations for the way to proceed." (PeopleCert, 2023) The
tolerance itself is set in [project-plan.md](project-plan.md) section 4.

When the marker turns Off track, the project manager sends the sponsor an exception note the same
day: the forecast, the cause, two or three options with what each costs, and a recommendation. The
sponsor decides, and the decision goes into the decision log ([roles-and-decisions.md](roles-and-decisions.md)
section 7). The note and the split, project manager writes and sponsor decides, are this practice's
own short form of PRINCE2's exception report. The reason: the sponsor's time goes to the changes that
move the goal, and the team keeps working to the current baseline while the request waits
([project-plan.md](project-plan.md) section 4).

## 6. Sources

- [PMI Lexicon of Project Management Terms, v5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: communications management plan, steering committee. Read as raw text on 2026-10-06.
- [PMP Examination Content Outline, July 2026 exam](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/new-pmp-examination-content-outline-2026.pdf), PMI, 2026: tailoring communication; escalation paths and thresholds.
- PeopleCert, [PRINCE2 7 Foundation Quick Reference Guide](https://www.nilc.co.uk/wp-content/uploads/2023/10/PRINCE2-Quick-Reference-Guide.pdf), 2023, and the PRINCE2 7 sample papers with rationales ([Foundation 1](https://www.serview.de/fileadmin/redakteur/medien/downloads/Musterpr%C3%BCfungen_f%C3%BCr_neuen_Downloadbereich/P2-7_FND_SamplePaper1_Rationales_v1-1_EN.pdf), [Practitioner 1](https://prince2.wiki/downloads/p2p-a1.pdf)), official training PDFs hosted by training organisations: manage by exception, tolerances, the exception and highlight reports.
- Atlassian Team Playbook, ["Weekly project updates"](https://www.atlassian.com/team-playbook/plays/weekly-project-updates) and ["Stakeholder communications plan"](https://www.atlassian.com/team-playbook/plays/stakeholder-communications-plan), undated; and Atlassian, ["Define your status markers"](https://www.atlassian.com/dam/jcr:d164f7ba-1fe7-4c1f-bec7-22967945c8b4/Loop-Technique_3-3_define-your-status-markers.pdf), 2021.
- Snow and Keil, ["The challenge of accurate software project status reporting"](https://www.researchgate.net/publication/3076745_The_challenge_of_accurate_software_project_status_reporting_A_two-stage_model_incorporating_status_errors_and_reporting_bias), IEEE Transactions on Engineering Management, 2002, abstract.
- Park, Im and Keil, ["Overcoming the Mum Effect in IT Project Reporting"](https://aisel.aisnet.org/jais/vol9/iss7/17/), Journal of the AIS 9(7), 2008, abstract.
- Rothman, ["Traffic Lights and Project Status"](https://www.jrothman.com/mpd/project-management/2011/03/traffic-lights-and-project-status/), 2011-03-02.
