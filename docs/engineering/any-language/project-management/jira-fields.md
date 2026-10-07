# Jira fields

What each field of a Jira work item holds and when to fill it, in a company-managed software space
(section 4 says why that type). A file whose name starts with `jira-` is about one Jira object; this
one covers the fields of a work item. Read it when you fill a field and are not sure what it is for,
and when you set up a space. The filled fields of each work type are in
[jira-work-item-example.md](jira-work-item-example.md).

**Navigation**

- [1. The fields](#1-the-fields)
- [2. Components or labels](#2-components-or-labels)
- [3. Jira components are not PMI components](#3-jira-components-are-not-pmi-components)
- [4. Space type](#4-space-type)
- [5. Sources](#5-sources)

## 1. The fields

In the second column, text in quotation marks is Atlassian's definition; the other rows say what
the field holds in plain words. Where the last column names another file, that file owns the rule
and the row only links it. A rule marked "this practice's own" has no Atlassian source behind it.

| Field | What it holds (Atlassian) | When to fill it | Owned by |
|---|---|---|---|
| Summary | The outcome in a few words | When you create the item | [tickets.md](tickets.md) section 2 |
| Description | The story and its acceptance criteria, or a bug's steps, expected result and actual result | When you create the item | [tickets.md](tickets.md) section 2; a default text per work type: section 4 |
| Work type | The kind of work: epic, story, task, bug or subtask | When you create the item | [jira-work-item-types.md](jira-work-item-types.md) section 1 |
| Parent | "A parent is a work item that sits above another work item"; a subtask can only be a child. It replaced Epic Link and Parent Link (an Atlassian staff post, 2021). | When you create the item | [wbs.md](wbs.md) section 7 |
| Status | Where the item is now, in one of three categories: To do, In progress, Done | Jira sets the first status on create; people move the item by the board's rules | [jira-workflow.md](jira-workflow.md) sections 1 and 2 |
| Resolution | "A work item's Resolution field describes the reason it was moved to Done". Jira treats an item as ended once the field has a value. | On the move into a status of the Done category | [jira-workflow.md](jira-workflow.md) sections 1 and 5 |
| Assignee | "the person assigned to the task" | One person: the one who works on the item now. An item in the backlog stays unassigned until someone takes it. This practice's own, so the board shows who works on what and the backlog shows what is free to take. | this file |
| Reporter | "the person who brought up the work item or task. Usually, this is the same as the person who created the work item." | Jira sets it on create. Change it only when you create the item for someone else, so questions go to the person who raised it (this practice's own). | this file |
| Priority | Jira's defaults are "Highest, High, Medium, Low, and Lowest"; a priority scheme sets a space's list and its default | On a bug or an incident: from its severity. On a story or a task: leave the default, so the backlog order, which the Product Owner owns, is the one order the team follows (this practice's own). Radigan, on an Atlassian blog in 2014: "Agile teams don't need the priority field as the order of the backlog sets the priority". | Bugs and incidents: [sla.md](sla.md) sections 2 and 7; the order: [roles-and-decisions.md](roles-and-decisions.md) section 1; stories and tasks: this file |
| Labels | "tags used to group, filter, or search for work items"; a label "cannot contain spaces" | When the item belongs to a theme that cuts across areas | this file, section 2 |
| Components | Jira components "help you group work items in your space around product features, departments, or workstreams" | When the item falls in an area that has a component | this file, section 2 |
| Fix versions | "shows the version that the work on the work item is released in", and adds the item to that release | When the item is planned into a release | [tickets.md](tickets.md) section 5; [release.md](release.md) section 1 |
| Affects versions | "details the versions of your product that a work item (a bug, for example) affects"; it does not add the item to that version | On a bug: every version where the bug shows. This practice's own, so the team sees which releases carry the bug. | this file |
| Sprint | A sprint is "a fixed time period where a team commits to a set number of work items from their backlog" | In Sprint Planning, when the Developers select the item; a subtask takes its parent's sprint | [meetings.md](meetings.md) section 4; subtasks: [jira-work-item-types.md](jira-work-item-types.md) section 3 |
| Story points | How complex an item is compared with others. Atlassian recommends points and leaves the choice to the team. In a team-managed space the field is named Story point estimate (section 4). | Only when the team uses points: in backlog refinement, on a story, task or bug, never on a subtask. Points are never converted to hours; Cohn (2024) argues against equating a point with a number of hours. | [schedule.md](schedule.md) section 2; refinement: [meetings.md](meetings.md) section 6; subtasks: [jira-work-item-types.md](jira-work-item-types.md) section 3 |
| Original estimate | A time estimate, which states "this task should take no more than x hours to complete" | Only when a named decision needs hours | [principles.md](principles.md) section 2 |
| Due date | "the agreed time and date when the work item should be resolved" | On an epic: the end of the plan's dates. On a story, task or bug: only when a date was agreed with someone outside the team, such as a customer or another team; the problem item of an incident is one case ([sla.md](sla.md) section 3). The team's own dates live on the epics and versions. This practice's own, so a due date on an item always marks a promise that someone outside waits for. | Epics and versions: [project-plan.md](project-plan.md) section 3; other items: this file |
| Start date | "when work began on an item" | On an epic, with its due date: the Timeline draws a parent work item from these two fields (Atlassian). Leave it empty on other items (this practice's own), so the plan keeps one set of dates. | Epics: [project-plan.md](project-plan.md) section 3; other items: this file |
| Environment | "the specific technical environment that relates to the task", such as a browser or an operating system | On a bug: where it was seen (this practice's own), so a reader can repeat the bug there | this file |
| Flagged | "You can flag a work item to indicate that it's important or blocked" | When the item is blocked | [jira-workflow.md](jira-workflow.md) section 4 |
| Team | Links a work item to a team, so search and filters find that team's work | Only when several teams share a space or a plan (this practice's own), because with one team per space the space already names the team | this file |

The table is good because each row names one moment to fill the field and links the file that owns
each rule, so a reader who copies a row into a board policy also copies where the rule is kept.

## 2. Components or labels

No Atlassian page compares components with labels or says when to use which. The rule below is this
practice's own, built on Atlassian's definitions of the two.

A component is a controlled area of the product, such as Checkout or Payments API. A space admin
sets it up with a lead and a default assignee, and each space has its own list (Atlassian). A label
is a free tag for a theme that cuts across areas, such as `provider-switch`. It cannot contain
spaces, and all company-managed spaces share the same labels (Atlassian).

- Use a component when someone owns the area and new items in it should reach that person, because
  the component names the owner and groups the area's work in one place.
- Use a label for a group that is temporary or cuts across areas, because it needs no admin setup
  and can be dropped when the theme ends.
- When a label keeps being used for the same area, make it a component, because only a component
  gives the area an owner and one fixed name.
- Set the component's default assignee to Unassigned, one of the four choices Atlassian gives
  (Space default, Space owner, Component lead, Unassigned). The lead finds new items under the
  component, and each one waits in the backlog until someone takes it (section 1, Assignee), so the
  component never hands work to a person who did not take it.

Compass components are a different thing. They describe "pieces of software that make up your
wider software architecture" across spaces, they work only in company-managed software spaces, and
a space uses either Jira components or Compass components, never both (Atlassian).

## 3. Jira components are not PMI components

Elsewhere in this folder "component" is PMI's word: a part of a product in [release.md](release.md),
a part of the work breakdown structure in [wbs.md](wbs.md) and
[jira-work-item-types.md](jira-work-item-types.md), and a part of the project management plan in
[communication.md](communication.md). In this file a component is the Jira field of section 2, and a
deliverable of the WBS becomes an epic ([wbs.md](wbs.md) section 7), not a Jira component.

## 4. Space type

This practice assumes a company-managed software space, because components, Affects versions and a
workflow that sets the resolution all work there. Pick the space type before the first work item:
when a space changes type its component data is lost, because a component belongs to one space
(Atlassian).

What differs in a team-managed space:

- There are no components: neither Jira components nor Compass components.
- Affects versions is not in Atlassian's list of team-managed fields.
- The story points field is named Story point estimate. Atlassian treats it as a separate field
  from Story points, and estimation is off until someone turns it on.
- A default description can be set per work type, in the space settings. In a company-managed space
  "adding default values to the system description field isn't supported", so an Automation rule
  fills the template after the item is created.
- The resolution cannot be set by hand or by the workflow; an Automation rule sets it
  ([jira-workflow.md](jira-workflow.md) section 5).
- Fields belong to one space and cannot be shared with another space.
- Atlassian's team-managed field list names Priority as an optional field, and Labels and Due date
  may have to be added to a work type before they show.

## 5. Sources

- Atlassian, ["Customize a work item's fields in team-managed
  spaces"](https://support.atlassian.com/jira-software-cloud/docs/customize-an-issues-fields-in-team-managed-projects/),
  undated, read 2026-10-06: the definitions of Labels, Assignee, Reporter, Due date, Start date and
  Environment; Priority as optional; the team-managed field list; fields kept to one space.
- Atlassian, ["What are Jira
  components"](https://support.atlassian.com/jira-software-cloud/docs/what-are-jira-components/)
  and ["Configure Jira
  components"](https://support.atlassian.com/jira-software-cloud/docs/configure-jira-components/),
  undated, read 2026-10-06: the definition, company-managed spaces only, lead and default assignee.
- Atlassian, ["Switch between Jira and Compass
  components"](https://support.atlassian.com/jira-software-cloud/docs/switch-between-jira-and-compass-components/),
  undated, read 2026-10-06.
- Atlassian, ["How to create and use labels in Jira
  Cloud"](https://support.atlassian.com/jira/kb/how-to-create-and-use-labels-in-jira-cloud/),
  2026-04-10: no spaces, shared by company-managed spaces.
- Atlassian, ["Unable to add a label to work items in a team-managed
  space"](https://support.atlassian.com/jira/kb/unable-to-add-a-label-to-issues-in-a-team-managed-project/),
  2025-09-26, and ["Add the due date field to your work
  items"](https://support.atlassian.com/jira-software-cloud/docs/add-the-due-date-field-to-your-issues/),
  undated, read 2026-10-06.
- Atlassian, ["Configure priorities for
  projects"](https://support.atlassian.com/jira-cloud-administration/docs/configure-priorities-for-projects/)
  and ["Manage priority
  schemes"](https://support.atlassian.com/jira-cloud-administration/docs/manage-priority-schemes/),
  undated, read 2026-10-06.
- Radigan, ["Organizing issues by priority to optimize
  delivery"](https://atlassian.com/blog/jira-software/organizing-issues-priority-optimize-delivery/amp),
  Atlassian blog, 2014-06-25: the backlog order sets the priority.
- Atlassian, ["Manage
  versions"](https://support.atlassian.com/jira-cloud-administration/docs/manage-versions/),
  undated, read 2026-10-06: Fix versions and Affects versions.
- Atlassian, ["Enable sprints"](https://support.atlassian.com/jira-software-cloud/docs/enable-sprints/),
  undated, read 2026-10-06.
- Atlassian, ["Estimate a work
  item"](https://support.atlassian.com/jira-software-cloud/docs/estimate-an-issue/), ["Configure
  estimation and
  tracking"](https://support.atlassian.com/jira-software-cloud/docs/configure-estimation-and-tracking/),
  ["Enable estimation"](https://support.atlassian.com/jira-software-cloud/docs/enable-estimation/)
  and ["What are time
  estimates"](https://support.atlassian.com/jira-software-cloud/docs/what-are-time-estimates-days-hours-minutes/),
  undated, read 2026-10-06.
- Atlassian, ["Story points not showing in a custom board for a team-managed
  space"](https://support.atlassian.com/jira/kb/story-points-not-showing-in-custom-board-for-a-team-managed-jira-project/),
  2026-07-03: Story points and Story point estimate are two fields.
- Cohn, ["Don't equate story points to
  hours"](https://www.mountaingoatsoftware.com/agile/dont-equate-story-points-to-hours),
  2024-12-06.
- Atlassian, ["What are work
  types"](https://support.atlassian.com/jira-cloud-administration/docs/what-are-issue-types/),
  undated, read 2026-10-06: the parent.
- Atlassian staff, ["Deprecation of the Epic Link, Parent Link and other related fields in REST
  APIs and
  webhooks"](https://community.developer.atlassian.com/t/deprecation-of-the-epic-link-parent-link-and-other-related-fields-in-rest-apis-and-webhooks/54048),
  2021-11-30: the Parent field replaces Epic Link and Parent Link.
- Atlassian, ["What is a resolution in
  Jira"](https://support.atlassian.com/jira-cloud-administration/docs/what-is-a-resolution-in-jira/),
  undated, read 2026-10-06, and ["Best practices on using the resolution field in Jira
  Cloud"](https://support.atlassian.com/jira/kb/best-practices-on-using-the-resolution-field-in-jira-cloud/),
  2026-03-11.
- Atlassian, ["Set Resolution field for Team Managed project in Jira
  Cloud"](https://support.atlassian.com/jira/kb/set-resolution-field-for-team-managed-project-jira-issues/),
  2025-09-26: an Automation rule sets the resolution in a team-managed space.
- Atlassian, ["Flag a work item"](https://support.atlassian.com/jira-software-cloud/docs/flag-an-issue/),
  undated, read 2026-10-06.
- Atlassian, ["Using Atlassian teams in Jira
  spaces"](https://support.atlassian.com/atlassian-account/docs/using-atlassian-teams-in-jira-projects/),
  undated, read 2026-10-06.
- Atlassian, ["Adding a default description in a company-managed
  space"](https://support.atlassian.com/jira/kb/adding-default-description-in-company-managed-project/),
  2025-09-26, and ["How to set a default description template for a work type in Jira
  Cloud"](https://support.atlassian.com/automation/kb/how-to-set-a-default-description-template-for-an-issue-type-in-jira-cloud/),
  2025-09-25.
- Atlassian, ["Migrate between team-managed and company-managed
  spaces"](https://support.atlassian.com/jira-software-cloud/docs/migrate-between-team-managed-and-company-managed-projects/),
  undated, read 2026-10-06: component data is lost.
- Atlassian, ["Schedule parent work items on your
  timeline"](https://support.atlassian.com/jira-software-cloud/docs/add-issues-to-epics-on-the-roadmap/),
  undated, read 2026-10-06: parent work items are scheduled by Start date and Due date.
