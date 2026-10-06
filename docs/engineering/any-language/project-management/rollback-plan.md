# Rollback plan

What a rollback plan holds, how data changes keep it possible, and how to rehearse it. Read it
before you plan a release that changes production, and when a release goes wrong. The restore target
the plan must meet is in [sla.md](sla.md).

**Navigation**

- [1. When](#1-when)
- [2. What it holds](#2-what-it-holds)
- [3. Roll back first, fix after](#3-roll-back-first-fix-after)
- [4. Data and schema changes](#4-data-and-schema-changes)
- [5. Rehearse it](#5-rehearse-it)
- [6. In Jira](#6-in-jira)
- [7. Sources](#7-sources)

## 1. When

Write a rollback plan for every release that changes production, before you deploy it. Atlassian's
change request carries "ways to roll back the change" in the planning step. The reason: during an
incident there is no time to design the way back.

## 2. What it holds

| Part | What to write | Source |
|---|---|---|
| Trigger | A measured deviation, such as the canary's error rate too far from the control, or an alert or a SEV 1 or 2 tied to the release | Google SRE |
| Decider | One named person on call for the release, and one named backup, who decides when the decider does not answer within 15 minutes of being paged | This practice |
| Steps | Redeploy the previous version, or turn the feature flag off; the way back of each way to release is in [release.md](release.md) section 6 | Fowler (ops toggles) |
| Data | What happens to data written since the release (section 4) | Fowler, Sadalage |
| Time | The time from the alert to "restored" ([sla.md](sla.md) section 4), which holds the trigger window, the wait for the decider, the rollback itself and the restored window, fits inside the restore target | [sla.md](sla.md) |
| Who is told | The people the plan names | This practice |

No standard names the decider's role. This practice asks for one name, and one backup, so that
nobody waits for a group to agree, or for an absent decider, while the outage runs. The decider is
the person on call for the release; when the incident's person on call ([sla.md](sla.md) section 3)
is someone else, that person pages the decider as soon as the trigger fires.

A filled plan for one release is in [project-example.md](project-example.md) section 8.

Check: before the deploy, ask whether the plan names a trigger, one decider and a time that fits the
SLA.

## 3. Roll back first, fix after

When the outage correlates with the release, roll back before you look for the cause (Google SRE
workbook). Rolling back a configuration mitigates an outage much more quickly than a patch, because
"there is inherently lower confidence that a patch will improve things". After service is back,
record the root cause as a work item and analyse it (PMI: root cause analysis is "an analytical
method used to determine the basic underlying reason that causes a variance, defect, or risk"). The
restore comes first and the cause second, as in [sla.md](sla.md) section 4.

This practice's own rule: if service is not restored after the rollback, the decider tells the
sponsor and the incident continues with its SLA clock running; the next step is a fix rolled forward
under the same incident.

Also this practice's own: after a rollback the change is still on main, so keep its feature flag off
in every environment, or revert it on main, before the next deploy (the revert trap is in
[git.md](../git/git.md) section 5). The fix is an ordinary work item linked to the incident, with its
own branch and pull request ([tickets.md](tickets.md) section 4), the team's Definition of Done, and
a new Fix version (section 6).

## 4. Data and schema changes

Change data in three steps so the code can roll back while the data stays: expand, migrate, contract
(Fowler). Add the new column or table first, move the readers and the data, and remove the old one
last.

- Keep a transition phase, "a period of time when the database supports both the old access pattern
  and the new ones simultaneously" (Sadalage and Fowler). The old release still works with the new
  schema.
- Keep each database change small: "Our usual rule is to make each database change as small as
  possible" (Sadalage and Fowler).
- Before a destructive change such as a delete, test the restore. Atlassian's review of its 2022
  outage says to test restoring deleted data before running the action in production.
- Name in the plan every change that cannot be undone, so the decider knows that rolling back will
  not bring it back. For each, the plan names who approves a roll-forward fix instead.

A filled data step is in [work-item-example.md](work-item-example.md) section 3 and
[project-example.md](project-example.md) section 8.

## 5. Rehearse it

Run the rollback in a test environment before the release. Google: "you only know that you can
recover your recent state if you actually do so". Atlassian's own 2022 outage review says:
"Soft-delete actions must have a tested rollback plan". A plan that was never run has an unknown
time, and the time is what the SLA needs.

## 6. In Jira

- Keep the plan in the release's version description, or in a Confluence page linked to the version
  or to the epic.
- When a release is rolled back, record it as a work item linked to the incident with "causes / is
  caused by" ([tickets.md](tickets.md) section 5).
- To tie an incident to a release (this practice's own), open the version that was released last
  before the alert and read its work items and deployments; the work item key links the deployment
  ([tickets.md](tickets.md) section 1). If nothing was released and no flag or setting was changed
  since the symptoms began, there is nothing to roll back: restore by other means and keep the SLA
  clock running ([sla.md](sla.md) section 5).
- After a rollback (this practice's own), keep the version, add a comment on it naming the rollback
  work item, and ship the fix in a new version. Before you move any item, list in that comment every
  work item that is no longer live; then move each to the new version, so the release page shows
  only what runs. Do not change the released version's state or description.

## 7. Sources

- Atlassian, ["Managing changes with your IT service
  desk"](https://confluence.atlassian.com/servicedeskcloud/managing-changes-with-your-it-service-desk-817562147.html),
  undated.
- Google, ["Canarying releases"](https://sre.google/workbook/canarying-releases/), SRE workbook,
  2018; and ["Testing for reliability"](https://sre.google/sre-book/testing-reliability/), SRE book,
  2016.
- Google, ["Configuration design"](https://sre.google/workbook/configuration-design/), SRE workbook,
  2018; and ["Incident response"](https://sre.google/workbook/incident-response/), SRE workbook,
  2018.
- Fowler, ["Feature toggles"](https://martinfowler.com/articles/feature-toggles.html), 2017-10-09;
  and ["Parallel change"](https://martinfowler.com/bliki/ParallelChange.html), 2014-05-13.
- Sadalage and Fowler, ["Evolutionary database
  design"](https://martinfowler.com/articles/evodb.html), 2003, revised 2016-05.
- PMI, [Lexicon of Project Management
  Terms](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf),
  version 5.0, January 2026.
- Google, ["Data integrity"](https://sre.google/sre-book/data-integrity/), SRE book, 2016.
- Atlassian, ["Post-incident review: April 2022
  outage"](https://www.atlassian.com/blog/atlassian-engineering/post-incident-review-april-2022-outage),
  2022-04-29.
- Atlassian, ["Enable releases and
  versions"](https://support.atlassian.com/jira-software-cloud/docs/enable-releases-and-versions/),
  ["Link work items"](https://support.atlassian.com/jira-software-cloud/docs/link-issues/), and
  ["Link a Confluence page to an
  epic"](https://support.atlassian.com/jira-software-cloud/docs/link-a-confluence-page-to-an-epic/),
  undated.
