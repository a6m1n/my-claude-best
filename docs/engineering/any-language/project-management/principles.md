# Project management principles

Why a team has project management at all, what it must never turn into, and which standards and
tools the rest of this folder rests on. Read it before you open a project, and when you doubt
whether an artifact, a report or a meeting is worth its cost.

**Navigation**

- [1. What project management is for](#1-what-project-management-is-for)
- [2. What it never does](#2-what-it-never-does)
- [3. Workload: see it and adapt it](#3-workload-see-it-and-adapt-it)
- [4. The standards behind this practice](#4-the-standards-behind-this-practice)
- [5. Jira as the tool](#5-jira-as-the-tool)
- [6. A project, its limits and its success](#6-a-project-its-limits-and-its-success)
- [7. Sources](#7-sources)

## 1. What project management is for

When you decide whether a task, a report or a meeting belongs to project management, ask whether it
helps the people reach the agreed goal in the agreed time. If it does not, drop it. A project is
"a temporary initiative in a unique context undertaken to create value" (PMI Lexicon, 2026), so the
goal and the time are what the project is made of, and everything else is a means.

The project manager serves the team toward that goal. PMI defines servant leadership as "The
practice of leading the team by focusing on understanding and addressing the needs and development
of team members in order to enable the highest possible team performance." (PMI Lexicon, 2026).
The reason: a manager who works for the team removes what blocks it, and a manager who works for a
report adds work to it.

At kickoff, write the goal on the charter page and give each person the deliverable where they help
it most (the WBS owner of [wbs.md](wbs.md) section 6). Netflix puts the same idea as "we model
ourselves on a professional sports team, not a family" (Netflix culture page, undated), and
explains it: professional sports teams "focus on
performance and picking the right person for every position". The point for this practice is one
shared goal and a clear place for each person, not the company's staffing policy.

When you assign a work item, trust the person with how it is done (section 2).
Principle 5 of the Agile Manifesto
says: "Build projects around motivated individuals. Give them the environment and support they
need, and trust them to get the job done."

## 2. What it never does

Never direct how a person does a task. Agree what the task must deliver and by when, then leave the
way to the person. Two sources point the same way:

- Google's Project Oxygen, an internal study of what makes its managers effective, lists "Empower
  the team without micromanaging" among its behaviours. It is Google's own research on its own
  managers, and describes what correlated with good management there.
- Atlassian's guide to project ownership says "Trust wins; control backfires".

The reason: a manager who checks every step makes people wait for the check, and a team that waits
does not decide.

Collect a number only when a decision uses it, and name that decision before you start collecting.
Martin Fowler argues that productivity cannot be measured reasonably, and that "false measures only
make things worse". A report that no decision reads is tracking for its own sake.

When the team sets up Jira, leave time logging off unless a named decision needs hours. Jira's smart commits can log time, add a comment and move a
work item, and the practice uses the transition and the comment. No rule in this folder needs hours
per person, so logging them would be tracking for its own sake.

Check: before you add a field, a report or a recurring status meeting, write one sentence: "We
will decide X from this." If you cannot, do not add it. The meetings this practice keeps, and what
each one decides, are in [meetings.md](meetings.md) section 1.

## 3. Workload: see it and adapt it

Show the work in progress on the board, and agree a limit on it with the team: a limit per person
and for the team. The Kanban Guide defines work in process as the number of work items started but
not finished, and names four flow measures: work in process, throughput, work item age and cycle time (the
elapsed time between when a work item started and when it finished). PMI describes a kanban board as
a tool that shows work in progress "to help identify bottlenecks and overcommitments" (PMI Lexicon,
2026).

How a Blocked item counts against the limit is in [workflow.md](workflow.md) section 4.

When a person or the team holds more work in process than the agreed limit, the project manager
delays or moves work. The project manager does not ask for more hours. The reason, from DORA's
research on work-in-process limits: when people are given more at once, "the result is that tasks
take longer to get done, and the team burns out in the process." The Agile Manifesto asks for the
same from the other side (principle 8): "The sponsors, developers, and users should be able to
maintain a constant pace indefinitely."

The project manager then tells the sponsor what the delay costs: which date moves, or which scope
leaves. This is the "adapt" half of the rule: the plan changes through the change control of
[project-plan.md](project-plan.md), and the team does not absorb the difference.

Check: at the weekly board look (the team sets its day), count the work items in progress for each person against
the limit. A person over it has one item moved or delayed that same day.

## 4. The standards behind this practice

Take the practice from the standards, and attribute each artifact to the body that names it. The
bodies do not name the same artifacts, so never write "all the certifications recommend X".

| Body and edition | What it is | What this folder takes from it |
|---|---|---|
| PMI Lexicon of Project Management Terms v5.0 (PMI, 2026), the definitions behind the PMBOK Guide and the PMP | The PMI standard behind the PMP | Charter, plan, baseline, change control, WBS, work package, risk register, the five threat responses |
| PMP exam content outline (PMI, July 2026 exam) | What the exam tests | "Create an integrated project management plan", "Break down scope", "Baseline a project schedule", "Maintain a risk register", "Execute the change control process" |
| PRINCE2 7 (PeopleCert, 2023) | A project management method | The project initiation document (PID) as its charter-like document; manage by stages and by exception; six threat responses (PeopleCert's PRINCE2 7 Quick Reference Guide) |
| Scrum Guide (2020), behind CSM and PSM | The Scrum framework | The Definition of Done and a refined backlog; sprints if the team works in them; no charter, WBS or risk register |

The PMBOK Guide 8th edition (2025) was read only through its table of contents.

Tailor the process to "just enough". PMI defines tailoring as "The deliberate adaptation of
approach, governance, and processes to make them more suitable for the given environment and the
work at hand." (PMI Lexicon, 2026), and PMBOK 7 lists tailoring among its principles. Add an
artifact to a project only when a risk or a decision needs it. The reason: every artifact has to be
kept current, and one that is not kept current misleads.

## 5. Jira as the tool

Keep the goal, the work and the code in one place, and make the work item key the link between
them. Jira connects a branch, a commit and a pull request to a work item when the key is in their
names, and it links a deployment to a work item when a commit of the deploy has the key in its
message (Atlassian, "Reference issues in your development work" and "View release information for
an issue"). The branch, commit and pull request names are owned by [git.md](../git/git.md)
sections 2 to 4. Read the rule there, and do not copy it.

The reason: with the key in every name, anyone can go from the goal to an epic, to a work item, to
the code and to the release, and back, without asking a person.

Use Jira's own names. "Work item" replaced "issue" in 2025 (Atlassian announcement of 2025-02-06),
though APIs still say "issue". The hierarchy is in [wbs.md](wbs.md) section 7. A version is defined
in [tickets.md](tickets.md) section 5, and Timeline is the view of epics and work items over time,
inside one space.

Check: pick one released work item and follow it from the epic to its pull request and its
deployment. A missing link means a key was left out of a name.

This practice uses Jira because the reader's team does, and takes its rules from the standards of
section 4.

## 6. A project, its limits and its success

Before you write a charter, check that the work is a project. A project ends, and it makes a change:
PRINCE2 7 calls it "a temporary organization that is created for the purpose of delivering one or
more business products according to an agreed business case", and says that once the change is in
place "business as usual resumes (in its new form), and the need for the project is removed"
(PeopleCert, 2023). The PMP exam outline adds that "The temporary nature of a project indicates a
beginning and an end". Work with no end, such as running a service or answering support requests,
is operations: run it on the team's board, with an SLA where users depend on it
([sla.md](sla.md)), and give it no charter. The reason: a charter, a baseline and a closure only
mean something for work that ends. The PMI Lexicon defines no "operations", so the line between the
two is drawn here from PRINCE2.

Write the project's limits into the charter as constraints, and say which of them is fixed. PMI
defines a constraint as "A limiting factor that affects the execution of a portfolio, program,
project, or process." (PMI Lexicon, 2026) The PMP exam outline calls "schedule, budget, and scope"
the "traditional metrics" of project success, and PRINCE2 7 sets tolerances for seven performance
targets: benefits, cost, time, quality, scope, sustainability and risk (PeopleCert, 2023). Neither
PMI's Lexicon nor any other standard read for this practice defines a "triple constraint". When one
of them is fixed, a change must come out of another, so the charter names the fixed one (this
practice's own). The reason: a team that knows the date is fixed cuts scope when work runs late,
and a team that does not know asks for more time, or quietly cuts quality. PRINCE2 7 states the quality target as "What is delivered by the project
must be fit for purpose." (PeopleCert, 2023) PMI's Lexicon has no entry for quality itself. This
practice measures quality by the acceptance criteria and the Definition of Done of each work item
([tickets.md](tickets.md) section 2), and by the charter's success criteria (this practice's own).

Judge success by the value of the result, against the charter's success criteria, not by the
schedule alone. PMI defines project success as "The consensus view across intended beneficiaries,
other stakeholders, and project participants that a project was perceived to have delivered value
that was worth the effort and expense." (PMI Lexicon, 2026), and PMBOK 7 says "Value is the ultimate
indicator of project success." Schedule, budget and scope stay in the picture as the traditional
metrics above, but they are not the whole of it. The success criteria are written in the
charter ([charter.md](charter.md) section 2), and the sponsor accepts the result against them at
closure ([life-cycle.md](life-cycle.md) section 2).

Check: before you write a charter, ask what change the work delivers and when it ends. If it has
neither, it is operations.

## 7. Sources

- [PMI Lexicon of Project Management Terms, version 5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: project, servant leadership, kanban board, tailoring, sponsor, constraint, project success; no entry for operations or quality. Read as raw text on 2026-10-05 and 2026-10-06.
- [PMP Examination Content Outline, July 2026 exam](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/new-pmp-examination-content-outline-2026.pdf?rev=b618cf45573e4276a54151e7636c97bf), PMI, 2026: a beginning and an end; schedule, budget and scope as traditional metrics.
- PeopleCert, [PRINCE2 7 Foundation Quick Reference Guide](https://www.nilc.co.uk/wp-content/uploads/2023/10/PRINCE2-Quick-Reference-Guide.pdf), 2023, and [PRINCE2 7 Foundation sample paper 1 with rationales](https://www.serview.de/fileadmin/redakteur/medien/downloads/Musterpr%C3%BCfungen_f%C3%BCr_neuen_Downloadbereich/P2-7_FND_SamplePaper1_Rationales_v1-1_EN.pdf), official training PDFs hosted by training organisations: the project definition, business as usual, the seven performance targets, the quality target.
- [PMBOK Guide eighth edition, table of contents](https://www.pmi.org/-/media/pmi/documents/public/pdf/publications/pmbok-guide-eighth-edition_table-of-contents.pdf), PMI, 2025: six principles and seven performance domains. The full text is paid, so this folder takes its definitions from the free PMI Lexicon.
- [PMBOK 7 "12 project management principles"](https://www.pmi.org/-/media/pmi/documents/public/pdf/pmbok-standards/12-project-management-principles.pdf?rev=03749f118ff84aca97a64af1d49bb1ac), PMI, 2021: tailoring principle ("just enough" process); value as the indicator of success. Edition 7, not 8.
- [PRINCE2 7 Foundation](https://www.peoplecert.org/browse-certifications/project-programme-and-portfolio-management/PRINCE2-2/PRINCE2-7-foundation-3579), PeopleCert, current: syllabus areas. PRINCE2 7 launched in September 2023 ([PRINCE2 blog](https://www.prince2.com/usa/blog/what-is-prince2-version-7-and-what-changed-from-6th-edition), 2026-09-16); the PID is described in [its beginner's guide](https://www.prince2.com/usa/blog/a-beginners-guide-to-the-project-initiation-document-pid-what-is-it-and-why-does-it-matter) (2025-08-19). These are secondary pages, not the paid PeopleCert text. The six threat responses come from PeopleCert's own Quick Reference Guide, listed below.
- [The Scrum Guide](https://scrumguides.org/scrum-guide.html), Schwaber and Sutherland, November 2020: Definition of Done, and the absence of the other artifacts. [CSM](https://www.scrumalliance.org/get-certified/scrum-master-track/certified-scrummaster) teaches the Scrum framework.
- [Netflix culture page](https://jobs.netflix.com/culture), undated, and [the culture memo post](http://about.netflix.com/en/news/sharing-our-latest-culture-memo), 2024-06-24.
- [Agile Manifesto principles](https://agilemanifesto.org/principles.html), 2001: principles 5 and 8.
- [Google re:Work, "Following the data: the research behind great managers"](https://rework.withgoogle.com/intl/en/guides/following-the-data-the-research-behind-great-managers), 2008 to 2016. Google's internal study of its own managers.
- [Atlassian, "Project ownership (without micromanaging)"](https://www.atlassian.com/blog/teamwork/guide-to-project-ownership-without-micromanaging), 2024-11-18.
- [Martin Fowler, "CannotMeasureProductivity"](https://martinfowler.com/bliki/CannotMeasureProductivity.html), 2003-08-29.
- [Atlassian, "Process issues with smart commits"](https://support.atlassian.com/jira-software-cloud/docs/process-issues-with-smart-commits/): comment, time and transition commands. Read 2026-10-05.
- [DORA, work in process limits](https://dora.dev/capabilities/wip-limits/), undated. A survey-based measure.
- [Kanban Guide](https://kanbanguides.org/english/), version 2025.5: work in process, throughput, work item age, cycle time.
- Atlassian: [Reference issues in your development work](https://support.atlassian.com/jira-software-cloud/docs/reference-issues-in-your-development-work/) and [View release information for an issue](https://support.atlassian.com/jira-software-cloud/docs/view-release-information-for-an-issue/), read 2026-10-05; [What is a version](https://support.atlassian.com/jira-software-cloud/docs/what-is-a-version/); [Work is the new collective term for items tracked in Jira](https://community.developer.atlassian.com/t/work-is-the-new-collective-term-for-items-tracked-in-jira/88552), 2025-02-06; [Jira work item hierarchy](https://www.atlassian.com/software/jira/guides/issues/overview); [What is the Timeline](https://support.atlassian.com/jira-software-cloud/docs/what-is-the-roadmap/); [Configure the issue type hierarchy](https://support.atlassian.com/jira-cloud-administration/docs/configure-the-issue-type-hierarchy/).
