# Roles and decisions

Who does what on a project, who answers for each deliverable, and who decides what. Read this file in
initiation, when you assign the deliverables, and before any decision that is hard to undo.

**Navigation**

- [1. The roles](#1-the-roles)
- [2. Responsible and accountable](#2-responsible-and-accountable)
- [3. The RACI matrix](#3-the-raci-matrix)
- [4. Find the gaps in ownership](#4-find-the-gaps-in-ownership)
- [5. Decision rights](#5-decision-rights)
- [6. One decision: DACI](#6-one-decision-daci)
- [7. The decision log](#7-the-decision-log)
- [8. A matrix for work, a decider for each decision](#8-a-matrix-for-work-a-decider-for-each-decision)
- [9. Sources](#9-sources)

## 1. The roles

At kickoff, name one person for each role below, so each role has one person who answers for it, and
give the sponsor and the project manager to two different people, because one person in both seats
would approve their own changes beyond the tolerance (section 5).

| Role | What it is | Source |
|---|---|---|
| Sponsor | "An individual or a group that provides resources and support for the portfolio, program, or project, and is accountable for enabling success." Name one person ([charter.md](charter.md) section 1) | PMI Lexicon |
| Project manager | "The person assigned by the performing organization to lead the team that is responsible for achieving the project objectives." | PMI Lexicon |
| Product Owner | "accountable for maximizing the value of the product resulting from the work of the Scrum Team"; "one person, not a committee" | Scrum Guide |
| Scrum Master | "accountable for establishing Scrum as defined in the Scrum Guide" and "for the Scrum Team's effectiveness" | Scrum Guide |
| Developers | The people who do the work; "responsible for the sizing" and for the plan of the sprint | Scrum Guide |
| Stakeholders | Everyone the project affects or who can affect it ([stakeholders.md](stakeholders.md)) | PMI Lexicon |

PRINCE2 7 names the same seats differently. Its executive is "the single point of accountability
for the project", and "There cannot be more than one project executive and the role cannot be
combined with the project manager"; in this practice that is the sponsor. Its senior user
"Represents the user community", and its senior supplier "Represents the supplier community"
(PeopleCert, 2023). That is the reason for the two different people above.

Scrum has no project manager: the Scrum Guide names only the three accountabilities. Scrum Alliance,
which certifies Scrum Masters, contrasts the two: "In project management, accountability lies with
the project manager", while "in scrum, there is shared accountability", and an organisation may have
either or both. When a Scrum team works inside a project, the project manager works around the team:
the sponsor, the budget, the stakeholders, other teams, the release plan and the risks. The Product
Owner orders the backlog, and the Developers decide how the work is done, so each accountability keeps
one holder (this practice's split; the rule against directing how is in [principles.md](principles.md)
section 2). On a larger project keep the Scrum Master and the project manager apart: Johanna Rothman,
an independent PM author, notes that a Scrum Master who also manages risks and does technical work
has "too much work".

## 2. Responsible and accountable

The Responsible does the work; the Accountable answers for the result. PMI keeps them apart:
responsibility is "An assignment that can be delegated", while accountability is "The condition of
being answerable for the outcome of a task or project. It is an individual responsibility and is not
shared." (PMI Lexicon, 2026) So one item has one Accountable, and one or more Responsible: however
many people do the work, one person answers when it is late or wrong.

## 3. The RACI matrix

Make a RACI matrix for the deliverables of the WBS and for the few activities that cross teams, not
for every work item, so each of them names who does it and who answers for it. PMI defines the RACI
matrix as "A type of responsibility assignment matrix that uses responsible, accountable, consulted,
and informed statuses to define the involvement of stakeholders in project activities.", and the
responsibility assignment matrix as "A grid that shows the project resources assigned to each work
package." (PMI Lexicon, 2026) The reason for the limit: inside one work item the assignee is already
the Responsible, so a row per work item copies Jira and goes stale in a week.

- Each row has exactly one A. Atlassian's template: "Each task should have precisely one accountable
  person to maintain clear ownership."
- Each row has at least one R, because a row with no R is work nobody does: "Every task needs at
  least one responsible person, but you can have more than one." (Atlassian)
- The A of a deliverable's row is the owner in its WBS dictionary entry ([wbs.md](wbs.md) section 6),
  so the two never disagree.
- C and I come from the stakeholder register ([stakeholders.md](stakeholders.md) section 2) or from
  the team of section 1 (the project manager, the Product Owner, the Scrum Master and the
  Developers), because the communication plan has lines only for those groups
  ([communication.md](communication.md) section 1), and a C or I from anywhere else is never told.

Keep the matrix as a Confluence page from Atlassian's RACI chart template, linked from the charter
page, so anyone who opens the charter can find it.

Check: read each row of the matrix: exactly one A, at least one R.

## 4. Find the gaps in ownership

At kickoff, run Atlassian's "Roles and responsibilities" play, so the work each person thinks someone
else holds is found before it is dropped: each person writes what they think their role holds, the
others write what they think it holds, and the team lists the "Unassigned responsibilities". Give
every unassigned item an owner, a row in the matrix, or take it out of scope, because an item that
stays in scope with no owner is still expected, and nobody does it.
No standard read for this practice names a rule for finding ownership gaps; the play is the check.

After kickoff, three things must each have one owner: a deliverable (section 3), a risk
([risks.md](risks.md) section 4) and a kind of decision (section 5). One with none, or with two, is a
gap.

## 5. Decision rights

Before the work starts, write in the plan who decides each kind of decision, one person for each
kind. Bain's RAPID says "there should only be one decider for each decision", and Atlassian's DACI
gives each decision "The one person (yes: one!) who makes the decision." The reason: a decision with
two deciders waits for both, and a decision with none is made by whoever moves first.

The defaults, each owned by the file named:

| Decision | Decider | Where the rule lives |
|---|---|---|
| The goal, the scope boundary, the budget, the sponsor | The sponsor | [charter.md](charter.md) section 3 |
| A change inside the agreed tolerance | The project manager | [project-plan.md](project-plan.md) section 4 |
| A change beyond the tolerance | The sponsor | [project-plan.md](project-plan.md) section 4, [communication.md](communication.md) section 5 |
| The order of the Product Backlog | The Product Owner | Scrum Guide |
| How a work item is built | The Developer who takes the item | [principles.md](principles.md) section 2 |
| A technical choice that is hard to undo or crosses work items (a data store, a framework, the architecture) | One Developer the Developers name for the project, written in the plan | this section; DACI in section 6 |
| Canceling a work item | The Product Owner | [jira-workflow.md](jira-workflow.md) section 5 |
| Go or no-go for a release | The named release decider | [release.md](release.md) section 3 |
| Rolling back a release | The rollback decider | [rollback-plan.md](rollback-plan.md) section 2 |

The table is good because each row names who decides and the file that owns the rule, so nobody
has to guess who decides or where the rule is.

The Developers name the decider for a hard-to-undo technical choice themselves, so the choice stays
inside the team: Scrum Teams are self-managing, "meaning they internally decide who does what, when,
and how" (Scrum Guide). The other Developers are Contributors on the DACI page, since its Approver
is "The one person (yes: one!) who makes the decision." (section 6)

A decision outside the team's authority goes to the sponsor, or to a steering committee where the
organisation has one, because a decision the team makes beyond its authority can be reversed by
someone above it. PMI defines a steering committee as "An advisory body of senior stakeholders who
provide direction and support for the portfolio, program, or project team and make decisions outside
of the team's authority." (PMI Lexicon, 2026) In PRINCE2 7 the same place is the project board
(PeopleCert, 2023).

## 6. One decision: DACI

For a decision that is hard to undo or crosses teams, use DACI (Atlassian Team Playbook), so one
person decides and everyone else knows whether they advise or only hear the result:

- **Driver:** "The person responsible for corralling stakeholders, collating all the necessary
  information, determining the scope of the decision, and getting a decision made by the agreed
  date."
- **Approver:** "The one person (yes: one!) who makes the decision." The Approver comes from the
  table in section 5, so the page and the table never name two deciders.
- **Contributors:** "People who have subject-area knowledge and can make recommendations – i.e., they
  have a voice, but not a vote."
- **Informed:** "People whose work may be affected by the decision, and should be informed once it's
  been made."

Write the options, the date by which the decision is due, and the outcome on one page, from
Confluence's DACI decision template, so anyone who opens it later sees what was weighed, by when, and
what was chosen.

## 7. The decision log

Record every decision that changes the scope, the schedule, the budget, the development approach or
the architecture: its date, the decision, the decider, the options weighed, the reason, and links to
the epics or work items it touches. PMI's Lexicon has no decision log, only an issue log; the log is
Atlassian's: Confluence's Decisions blueprint makes "a decision log page for the space". The reason:
in three months nobody remembers why, and a decision nobody can find gets made again.

Link each new decision from the weekly status update ([communication.md](communication.md) section
2).

Check: when the plan changes, find the decision behind it in the log.

## 8. A matrix for work, a decider for each decision

Use the RACI matrix to assign work and the decider table, with DACI, to assign decisions; do not
let one stand in for the other (this practice's own). PMI's matrix shows "the project resources
assigned to each work package"; Bain and DACI give each decision one decider. The two differ: the A
of the plan's row answers for the plan, but a change to the scope boundary is still the sponsor's to
decide.

## 9. Sources

- [PMI Lexicon of Project Management Terms, v5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: sponsor, project manager, stakeholder, responsibility, accountability, responsibility assignment matrix, RACI matrix, steering committee, issue log. Read as raw text on 2026-10-06.
- [The Scrum Guide](https://scrumguides.org/scrum-guide.html), November 2020: the Product Owner, the Scrum Master, the Developers; self-managing Scrum Teams.
- PeopleCert, [PRINCE2 7 Foundation Quick Reference Guide](https://www.nilc.co.uk/wp-content/uploads/2023/10/PRINCE2-Quick-Reference-Guide.pdf), 2023, an official training PDF hosted by a training organisation: executive, senior user, senior supplier, project board.
- Scrum Alliance, ["Key Differences Between Project Managers and Scrum Masters"](https://resources.scrumalliance.org/Article/difference-project-managers-scrum-masters), Natalie Barnes, undated.
- Rothman, ["The Agile Project Manager: To Facilitate, Serve and Protect"](https://www.jrothman.com/articles/2010/01/the-agile-project-manager-to-facilitate-serve-and-protect/), 2010-01-01.
- Atlassian, [RACI chart template](https://www.atlassian.com/software/confluence/templates/raci-chart), [DACI decision template](https://www.atlassian.com/software/confluence/templates/decision), Team Playbook plays ["Roles and responsibilities"](https://www.atlassian.com/team-playbook/plays/roles-and-responsibilities) and ["DACI"](https://www.atlassian.com/team-playbook/plays/daci), and the Confluence ["Decisions blueprint"](https://confluence.atlassian.com/doc/decisions-blueprint-339739406.html) (Data Center documentation). All undated, read 2026-10-06.
- Bain & Company, ["RAPID: a tool to clarify decision accountability"](https://www.bain.com/insights/rapid-tool-to-clarify-decision-accountability/), 2023-10-13.
