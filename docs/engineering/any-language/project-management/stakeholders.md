# Stakeholders

Who has a stake in the project, how much each of them can change it, how involved each one should
be, and where the team keeps that. Read this file in initiation, before the kickoff, and again at
each phase end. What each stakeholder hears, and how often, is in
[communication.md](communication.md).

**Navigation**

- [1. List them in initiation](#1-list-them-in-initiation)
- [2. The stakeholder register](#2-the-stakeholder-register)
- [3. Influence and interest](#3-influence-and-interest)
- [4. Engagement: where they are and where they need to be](#4-engagement-where-they-are-and-where-they-need-to-be)
- [5. Stakeholders in Scrum](#5-stakeholders-in-scrum)
- [6. Review](#6-review)
- [7. Sources](#7-sources)

## 1. List them in initiation

Before the kickoff, list everyone the project affects or who can affect it. PMI defines a
stakeholder as "An individual, group, or organization that may affect, be affected by, or perceive
itself to be affected by a decision, activity, or outcome of a portfolio, program, or project."
(PMI Lexicon, 2026) Start from the approvers and the people the charter says are informed
([charter.md](charter.md) section 2), then ask each of them who else the change touches. The
reason: an approver found late delays the project, and a user group found late finds the result
does not fit them.

## 2. The stakeholder register

Keep one register per project, as a Confluence page from Atlassian's stakeholder register template,
linked from the charter page. PMI defines the register as "A project document that contains
information about project stakeholders including an assessment and classification of project
stakeholders." (PMI Lexicon, 2026) Atlassian calls it "a living document". Its template holds name and role, contact and preferred
communication, influence and interest, concerns and expectations, and an engagement strategy with a
frequency, and tells you to assign one team member to liaise with each stakeholder. The columns below
follow it, except "Engagement now and wanted", which comes from PMI's engagement assessment matrix
(section 4):

| Column | What it holds |
|---|---|
| Name and role | The person, or the group and the one person who speaks for it |
| Concerns and expectations | What they need from the project, or fear from it |
| Influence | High or low: can they change the scope, the budget or the date? |
| Interest | High or low: how much does the result change their work? |
| Engagement now and wanted | Section 4 |
| How and how often | The channel and the rhythm, from the communication plan ([communication.md](communication.md) section 1) |
| Owner | The one team member who liaises with the stakeholder (Atlassian's template step) |

The reason for one owner: a stakeholder everyone talks to is a
stakeholder nobody is sure was told.

Jira needs no field for this. A field no decision reads is tracking for its own sake
([principles.md](principles.md) section 2).

## 3. Influence and interest

Place each stakeholder in one of four boxes by influence and interest, as Atlassian's stakeholder
mapping template does, and let the box set how much of the team's time they get. PMI's Lexicon
names no model for the classification it asks for, so the boxes and their names below are this
practice's own:

|  | Low interest | High interest |
|---|---|---|
| **High influence** | Keep satisfied: short updates at milestones, asked before a decision touches them | Work closely: in the decisions that touch them, at every Sprint Review |
| **Low influence** | Watch: the weekly update is enough | Keep informed: the weekly update and the Sprint Review |

Atlassian's stakeholder communications plan sorts the same people another way, and both views fit
in the register. Contributors are those whose "time, decisions, or expertise are critical to doing
the work", and they need frequent, detailed information. Beneficiaries need less frequent,
high-level information.

The box ranks attention; it does not decide for you, in the same way the risk score does not
([risks.md](risks.md) section 3). Someone in "Watch" who blocks a release is a high-influence
stakeholder from that day on.

## 4. Engagement: where they are and where they need to be

For each stakeholder, write how engaged they are now and how engaged the project needs them to be,
and give every gap an action with an owner and a date. PMI's stakeholder engagement assessment
matrix is "A matrix that compares current and desired stakeholder engagement levels." (PMI Lexicon,
2026) The reason: a gap with no action stays a gap until the review where it shows up as a
surprise.

PMI's free texts define no levels. Agree a short scale in the team and write it at the top of the
register, for example "does not know, against, neutral, supports, leads" (this practice's own
example).

Check: at each phase end, find every stakeholder whose engagement now is below the engagement
wanted, and the action next to them.

## 5. Stakeholders in Scrum

In a Scrum team, the Product Owner carries the stakeholders' needs into the Product Backlog, and
the Sprint Review is where they see the result: "The Scrum Team presents the results of their work
to key stakeholders and progress toward the Product Goal is discussed." (Scrum Guide, 2020) Invite
the "Work closely" and "Keep informed" stakeholders to it (this practice's own). How the review is
run is in [meetings.md](meetings.md) section 7.

## 6. Review

Review the register and the boxes at each phase end, and when a stakeholder changes role or a new
one appears. A box that is not reviewed describes the project as it was at kickoff.

## 7. Sources

- [PMI Lexicon of Project Management Terms, v5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: stakeholder, stakeholder register, stakeholder engagement assessment matrix; no classification model and no engagement levels. Read as raw text on 2026-10-06.
- [PMP Examination Content Outline, July 2026 exam](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/new-pmp-examination-content-outline-2026.pdf), PMI, 2026: "Analyze stakeholders", "Categorize stakeholders".
- Atlassian, [stakeholder register template](https://www.atlassian.com/software/confluence/templates/stakeholder-register) and [stakeholder mapping template](https://www.atlassian.com/software/confluence/templates/stakeholder-mapping), undated, read 2026-10-06.
- [Atlassian Team Playbook, "Stakeholder communications plan"](https://www.atlassian.com/team-playbook/plays/stakeholder-communications-plan), undated: Contributors and Beneficiaries.
- [The Scrum Guide](https://scrumguides.org/scrum-guide.html), November 2020: the Sprint Review.
