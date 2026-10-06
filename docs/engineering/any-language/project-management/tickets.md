# Work items

How work is written down in Jira: what a good work item holds, how big it is, and how it links to
the branch, the pull request and the release. Read it before you create a work item, split one, or
open a branch. The key's form in branches, commits and pull requests is owned by
[git.md](../git/git.md); this file gives the reasons in Jira terms.

**Navigation**

- [1. Why work lives in work items](#1-why-work-lives-in-work-items)
- [2. A good work item](#2-a-good-work-item)
- [3. Small work items](#3-small-work-items)
- [4. One branch and one pull request per work item](#4-one-branch-and-one-pull-request-per-work-item)
- [5. Links in Jira](#5-links-in-jira)
- [6. The hierarchy](#6-the-hierarchy)
- [7. Sources](#7-sources)

## 1. Why work lives in work items

A ticket is a Jira work item ("issue" until 2025); this folder says work item.

Put every piece of work in a Jira work item before you start it. A work item is the one place that
links the goal to the code and to the release, so a person or an agent can follow the chain in both
directions.

- The work item key in the branch name, the commit title and the pull request links them in Jira
  (Atlassian). The forms are in [git.md](../git/git.md) sections 2, 3 and 4.
- A deployment links to a work item when a commit in it carries the key (Atlassian). From an
  incident you reach the release, the pull request and the reason for the change, which shortens the
  fix ([sla.md](sla.md) section 6).
- Descriptions that carry the bug number are searched later by people who need the reason (Google
  eng-practices).

Work items are not a way to watch people. Logging time is optional, and the purpose of project
management is to help the team reach the goal, not to track for its own sake
([principles.md](principles.md)).

## 2. A good work item

Write a story as "As a [user], I want [goal] so that [reason]" and add acceptance criteria; the
criteria are the test that the story is done, and without them nobody can tell when to stop
(Atlassian; Jeffries calls this the Confirmation of his three Cs).

| Part | Holds | Source |
|---|---|---|
| Title | The outcome in a few words | Atlassian |
| Story | As a [user], I want [goal] so that [reason] | Atlassian |
| Acceptance criteria | "A set of conditions that are met before deliverables are accepted." (PMI Lexicon, 2026) | PMI |
| Definition of Done | The team's shared checklist for any work item | Scrum Guide, PMI |

- Keep one Definition of Done for the team. The Scrum Guide says: "The Definition of Done is a
  formal description of the state of the Increment when it meets the quality measures required for
  the product." A work item that does not meet it is not done.
- Write the production deploy into the Definition of Done, so that Done on the board means the
  change is live ([workflow.md](workflow.md) section 2). The Scrum Guide leaves the Definition of
  Done to the team, and a Done that stops at "merged" shows finished work that no user has yet;
  Humble puts it as "They are done when it is working in production."
- Write a bug's steps, its expected result and its actual result in the description, not in
  comments, so the whole report is in one place. Tatham: "The aim of a bug report is to enable the
  programmer to see the program failing in front of them." Atlassian's bug template puts expected
  against actual in comments; this practice follows Tatham.
- Check the story against INVEST (Wake, 2003): small enough to finish soon, and testable, so that
  you could write a test for it.
- Definition of Ready is PMI's term; the Scrum Guide has no such term. If the team keeps a
  Definition of Ready, name PMI as its owner and keep it short.
- Pick the work type by [work-item-types.md](work-item-types.md) section 1, which owns when to
  use a story, a task, a bug, an epic or a subtask.

One ideal work item of each type is in [work-item-example.md](work-item-example.md); the story is
in its section 2.

## 3. Small work items

Split a work item that would take more than three working days. The limit is this practice's own; DORA's
outer limit is one week. Four reasons:

- DORA: "Any batch of code that takes longer than a week to complete and check is too big." Small
  batches also shorten the time to get feedback.
- A smaller release artifact is cheaper to roll back (Google SRE workbook;
  [rollback-plan.md](rollback-plan.md)).
- A small change is easy to find and undo when an SLA clock is running ([sla.md](sla.md)).
- A small change is easy to review ([git.md](../git/git.md) section 4).

Three keeps a work item well inside DORA's week, with time left for review and a fix; a team may
set its own number, below a week.

Check: before you move a work item to In Progress, ask whether its acceptance criteria can be met in
three working days. If not, split it.

## 4. One branch and one pull request per work item

Name the branch and the pull request by [git.md](../git/git.md) sections 2 and 4, which own the
one-branch and one-ticket rules. The Jira reason: each change then maps to one work item, one
review and one rollback.

Aim to merge each work item's one pull request within a day: Atlassian's trunk-based development
page asks for frequent, daily merges, and DORA says short-lived branches last hours and merge at
least daily. Three working days (section 3) is the outer limit; an item that would take longer is
split. Atlassian: "With small branches, developers can quickly see and review small changes."

The work item key is the only link Jira needs to show the branch, the commit and the deployment on
the work item. Jira makes the link itself when three things hold (Atlassian, "Reference work items
in your development work"):

- The key is in the name. A branch links by its name, a commit by its message, and a pull request
  by its title or its source branch. A build or a deployment links when one of its commits carries
  the key.
- The key is in capital letters: "'JRA-123', not 'jra-123'". A lower-case key may not link.
- The repository is connected to Jira (Bitbucket Cloud, GitHub through the GitHub for Atlassian
  app, or GitLab), and the reader has the View development tools permission. Without the
  connection no name links anything, and the first sync can take a few minutes.

Development > Create branch on the work item puts the key into the branch name for you, and each
person sets the name format once. Set it to the form in [git.md](../git/git.md) section 2, or edit
the name before you create the branch, because the tool's default is not that form. Bitbucket's own
branching model uses prefixes such as `feature/` and `bugfix/` and may suggest one from the work
type; git.md's six types differ, so change the prefix to the git.md one.

No Atlassian page states which characters may come before the key in a branch name, and none
reports that a prefix with a slash breaks the link. Atlassian's own example puts the key first
(`JRA-123-<branch-name>`), while git.md's form puts the type first. So check it once in each
repository.

Check: after the first branch of a repository is pushed, open its work item's Development panel. The
branch is listed there. If it is not, look for the three causes above; if none applies, the prefix
before the key is the likely cause, and you record it as a follow-up on the git.md branch rule
([refactoring.md](../refactoring/refactoring.md) section 8).

A filled branch and commit are in [project-example.md](project-example.md) section 6.

## 5. Links in Jira

- Release: put each work item in the Fix version of the release that ships it. A version is "a set
  of features and fixes released together as a single update to your app" (Atlassian). The release
  page then shows how much work is done.
- Dependencies: link with "blocks" and "is blocked by". Use "relates to" for any other connection. A
  reader then sees at once what waits for what.
- Smart commits: a commit message can add a comment to a work item or move it to the next status.
  Time logging through smart commits stays optional.
- Incidents: link a rollback or a bug to the incident work item with "causes / is caused by"
  ([rollback-plan.md](rollback-plan.md) section 6).

## 6. The hierarchy

Use Jira's default levels, so the team needs no admin setup and no Premium licence. The hierarchy,
and how the deliverables of the plan map to epics, is in [wbs.md](wbs.md) section 7. The life cycle
that sets the order of the work is in [life-cycle.md](life-cycle.md).

## 7. Sources

- Atlassian, ["Reference work items in your development
  work"](https://support.atlassian.com/jira-software-cloud/docs/reference-issues-in-your-development-work/),
  read 2026-10-05.
- Atlassian, ["View release information for a work
  item"](https://support.atlassian.com/jira-software-cloud/docs/view-release-information-for-an-issue/),
  read 2026-10-05.
- Google, ["CL
  descriptions"](https://google.github.io/eng-practices/review/developer/cl-descriptions.html),
  eng-practices, undated.
- Atlassian, ["User stories"](https://www.atlassian.com/agile/project-management/user-stories),
  undated.
- Jeffries, ["Essential XP: Card, Conversation,
  Confirmation"](https://ronjeffries.com/xprog/articles/expcardconversationconfirmation/),
  2001-08-30.
- PMI, [Lexicon of Project Management
  Terms](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf),
  version 5.0, January 2026.
- Schwaber and Sutherland, [The Scrum Guide](https://scrumguides.org/scrum-guide.html), November
  2020.
- Wake, ["INVEST in good stories, and SMART
  tasks"](https://xp123.com/invest-in-good-stories-and-smart-tasks/), 2003-08-17.
- Atlassian, ["What are work
  types"](https://support.atlassian.com/jira-cloud-administration/docs/what-are-issue-types/), and
  ["Configure the work type
  hierarchy"](https://support.atlassian.com/jira-cloud-administration/docs/configure-the-issue-type-hierarchy/),
  undated.
- DORA, ["Working in small batches"](https://dora.dev/capabilities/working-in-small-batches/) and
  ["Trunk-based development"](https://dora.dev/capabilities/trunk-based-development/), current
  pages.
- Google, ["Canarying releases"](https://sre.google/workbook/canarying-releases/), SRE workbook,
  2018.
- Atlassian, ["Feature branch
  workflow"](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow),
  and ["Trunk-based
  development"](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development),
  undated.
- Atlassian, ["What is a
  version"](https://support.atlassian.com/jira-software-cloud/docs/what-is-a-version/), ["Enable
  releases and
  versions"](https://support.atlassian.com/jira-software-cloud/docs/enable-releases-and-versions/),
  ["Link work items"](https://support.atlassian.com/jira-software-cloud/docs/link-issues/), and
  ["Process work items with smart
  commits"](https://support.atlassian.com/jira-software-cloud/docs/process-issues-with-smart-commits/),
  undated.
- Atlassian, ["View development information for a work
  item"](https://support.atlassian.com/jira-software-cloud/docs/view-development-information-for-an-issue/),
  ["How to alter the branch name format in the Create branch
  option"](https://support.atlassian.com/jira/kb/how-to-alter-the-branch-name-format-in-the-create-branch-option-in-development-panel/),
  and ["Link GitHub workflows and deployments to Jira work
  items"](https://support.atlassian.com/jira-cloud-administration/docs/link-github-workflows-and-deployments-to-jira-issues/),
  undated, read 2026-10-06.
- Atlassian, ["Configure a project's branching
  model"](https://support.atlassian.com/bitbucket-cloud/docs/configure-a-projects-branching-model/),
  Bitbucket Cloud, undated, read 2026-10-06.
- Humble, ["Continuous Delivery vs Continuous
  Deployment"](https://continuousdelivery.com/2010/08/continuous-delivery-vs-continuous-deployment/),
  2010-08-13.
- Tatham, ["How to Report Bugs
  Effectively"](https://www.chiark.greenend.org.uk/~sgtatham/bugs.html), 1999.
- Atlassian, ["Bug report
  template"](https://www.atlassian.com/software/jira/templates/bug-report), undated, read
  2026-10-06.
