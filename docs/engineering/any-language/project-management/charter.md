# Project charter

The charter is the short document that starts a project and says who may spend the
organization's resources on it. Read this file at initiation, before you write the
[project plan](project-plan.md). The phases are in [life-cycle.md](life-cycle.md). A Gantt chart is
part of the plan, not the charter ([project-plan.md](project-plan.md) section 3).

**Navigation**

- [1. When and who](#1-when-and-who)
- [2. What it holds](#2-what-it-holds)
- [3. It stays stable](#3-it-stays-stable)
- [4. Other standards](#4-other-standards)
- [5. In Jira](#5-in-jira)
- [6. Sources](#6-sources)

## 1. When and who

Write the charter in initiation, before the plan, and have the sponsor issue it. The plan needs
the goal and the authority the charter gives; without them the project manager has no mandate
to plan with.

PMI defines the charter as "A document issued by the project initiator or sponsor that formally
authorizes the existence of a project and provides the project manager with the authority to
apply organizational resources to project activities." (PMI Lexicon, 2026)

The sponsor is "An individual or a group that provides resources and support for the portfolio,
program, or project, and is accountable for enabling success." (PMI Lexicon, 2026) Name one
person, so the project manager knows who approves a change to the charter (section 3).

Check: before you write the plan, ask whether the sponsor has approved the charter in writing.

## 2. What it holds

Keep the charter to one or two pages. Atlassian says it is "not meant to be a detailed project
plan, but rather a high-level overview" (Atlassian, project charter); detail belongs in the
plan. Each part below is a short section of the page.

| Part | What to write | Why it is there |
|---|---|---|
| Purpose and business need | The problem or opportunity the project answers, in two or three sentences | A team that knows the reason can judge a change |
| Objectives and success criteria | Measurable goals, each with the number that shows it is met | A goal nobody can measure cannot be called done |
| Scope | What is in and what is out, at high level | The WBS ([wbs.md](wbs.md)) is cut from this boundary |
| People | Sponsor, project manager and the project manager's authority | The authority is the point of the document |
| Stakeholders and approvers | Who must agree, and on what; the full list goes to the [stakeholder register](stakeholders.md) | Approvals found late delay the project |
| Key milestones | Dates of the big steps, not tasks | The plan starts its schedule from them |
| Budget summary | One total, or one range | The limit the plan must fit |
| Constraints | The limits the project works within, and which of them is fixed ([principles.md](principles.md) section 6) | A team that knows what is fixed knows what to cut when work runs late |
| Assumptions | What the plan takes as true without proof, each with a date by which it must be confirmed | An assumption that turns out false is a risk that has already happened |
| Top risks | The few that could stop the goal | They seed the [risk register](risks.md) |

PMI defines the business need as "The impetus for a change in an organization, based on an existing
problem or opportunity. The business need provides the rationale for initiating a program or
project." (PMI Lexicon, 2026)

PMI defines an assumption as "A factor in the planning process considered to be true, real, or
certain, without proof or demonstration.", and keeps both in an assumption log: "A project document
used to record all assumptions and constraints throughout the project." (PMI Lexicon, 2026)
Atlassian's project poster gives the reason to write them down: "Unidentified and unvalidated
assumptions can significantly contribute to project failures." The date on each assumption is this
practice's own: an assumption with no date to check it by stays untested until it fails. When one is
proved false, it goes to the [risk register](risks.md) as an issue.

A filled charter for one project is in [project-example.md](project-example.md) section 2.

## 3. It stays stable

Change the charter only when the goal, the scope boundary, the budget or the sponsor changes,
and only with the sponsor's approval. Day-to-day change goes into the plan
([project-plan.md](project-plan.md) section 4). The charter is the reference the plan is
measured against, so a charter that moves with every plan change measures nothing.

Atlassian lists "neglecting to update the document as project parameters change" as a charter
mistake, so do update it when one of the four things above changes. It also contrasts the
charter with the project poster: "Unlike project charters, your project poster is a living
document." (Atlassian, project charter) If the team wants a page that is updated every week, make
the poster or the plan page, not the charter.

## 4. Other standards

PRINCE2 has no charter by that name. It builds a Project Brief at the start and extends it into
the Project Initiation Documentation (PID), "the primary reference point for how the project will
be managed, by whom, and to what end." (PRINCE2 guide to the PID) The PMP exam outline does not
use the word "charter" at all (PMP exam content outline, July 2026); the term comes from the PMI
Lexicon above. Scrum has no charter.

## 5. In Jira

Keep the charter as a Confluence page and link it to each deliverable epic ([wbs.md](wbs.md) section 7),
so every work item traces up to the goal. Jira can link a Confluence page to a parent-level work item in
company-managed spaces. Atlassian's docs mention the epic case, and its scope for other work
types is not settled in the docs, so link the deliverable epics and nothing else.

## 6. Sources

- [PMI Lexicon of Project Management Terms, v5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: project charter, sponsor, business need, assumption, assumption log.
- [Atlassian Team Playbook, "Project poster"](https://www.atlassian.com/team-playbook/plays/project-poster), undated: unvalidated assumptions.
- [Atlassian, project charter](https://www.atlassian.com/work-management/project-management/project-planning/project-charter), undated, read 2026-10-05: content, mistakes, project poster.
- [PRINCE2, guide to the PID](https://www.prince2.com/usa/blog/a-beginners-guide-to-the-project-initiation-document-pid-what-is-it-and-why-does-it-matter), updated 2026-05-27, and [guide to project briefs](https://www.prince2.com/usa/blog/a-guide-to-project-briefs), 2020-10-30.
- [PMP examination content outline](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/new-pmp-examination-content-outline-2026.pdf), July 2026 exam: no use of "charter".
- [Atlassian, link a Confluence page to an epic](https://support.atlassian.com/jira-software-cloud/docs/link-a-confluence-page-to-an-epic/), undated.
