# Service level agreements

How to write an SLA that a team can meet and a reviewer can check, and how Jira, small work items
and rollback help meet it. Read it before you agree to a fix-time target, set up SLA goals in Jira,
or plan the response to an incident. A filled severity table and clause are in
[project-example.md](project-example.md) section 7.

**Navigation**

- [1. SLA, SLO, SLI](#1-sla-slo-sli)
- [2. Define severity before the SLA](#2-define-severity-before-the-sla)
- [3. Open the incident](#3-open-the-incident)
- [4. What the clock measures](#4-what-the-clock-measures)
- [5. Restore first, by rollback when a change caused it](#5-restore-first-by-rollback-when-a-change-caused-it)
- [6. Why small work items make the SLA easier](#6-why-small-work-items-make-the-sla-easier)
- [7. In Jira](#7-in-jira)
- [8. Sources](#8-sources)

## 1. SLA, SLO, SLI

Use the three terms as Google SRE defines them, and call a target an SLA only when a consequence is
attached. The reason is that a team that calls every target an SLA promises more than it has agreed.

| Term | Meaning |
|---|---|
| SLI | A service level indicator: a carefully defined quantitative measure of some aspect of the level of service. |
| SLO | A service level objective: a target value or range of values for a service level, measured by an SLI. |
| SLA | "an explicit or implicit contract with your users that includes consequences of meeting (or missing) the SLOs they contain" (Google SRE book). |

Atlassian says the same in its own words: an SLO is an internal target, and an SLA is an agreement
with measurable metrics and consequences.

Check: ask "what happens if we miss it?". With no explicit consequence, it is an SLO (Google SRE
book).

## 2. Define severity before the SLA

Write the severity levels first, and give each SLA target one severity. Without them "critical"
means whatever the customer says at 2 a.m. Atlassian's levels:

| Level | Meaning | Example (Atlassian) |
|---|---|---|
| SEV 1 | A critical incident with very high impact | A client-facing service is down for all customers |
| SEV 2 | A major incident with significant impact | A service is down for a subset of customers |
| SEV 3 | A minor incident with low impact | A system bug is creating a minor inconvenience to customers |

Each company sets its own targets. A filled severity table, with an invented target for each level,
is in [project-example.md](project-example.md) section 7.

## 3. Open the incident

When the alert fires, the person on call opens one incident work item. In Jira Service Management
it is an Incident; without it, use a Bug. The person on call sets the severity from section 2, and
may raise or lower it while the incident runs. A change of severity keeps the clock's start time;
whoever lowers it writes why in the incident work item. The SLA clock starts at the alert or the
first customer report, whichever comes first; the person on call writes that time into the incident
work item, even when the item is opened later. When service is restored, the person on call opens one problem work item (a Task or a Bug) linked to the
incident, with its own due date, for the root cause ([tickets.md](tickets.md) section 5 for the
link).

The split between an incident (restore the service) and a problem (find the cause) is ITIL's and
Atlassian's, cited in section 4. The roles and the item types here are this practice's own. The
reason: one item per incident gives the clock one start, and the problem item keeps the lasting fix
from being forgotten once the service is back.

## 4. What the clock measures

Write in the SLA what "fixed" means and which clock runs. The SLA clock measures the time to restore
the service, not the time to find and fix the root cause. ITIL separates incident management
(restore normal service quickly) from problem management (find the cause), and Atlassian says to run
both, separately. Google: "first stop the impact of an incident, and then find the root cause".

No standard says what "fix within 24 hours" means in a contract. This section is this practice's
advice. A clause such as "fix within 24 hours" names five things:

- the severity it covers;
- the clock: 24/7 or business hours, and who is on call outside working hours (or that nobody is,
  and the clock still runs);
- what counts as restored (for example, checkout success rate is back to its normal level for 30
  minutes);
- how the lasting fix follows: a problem work item with its own target (section 3);
- the consequence of a miss, without which it is an SLO (section 1).

Why: a vague clause ends in a dispute over whether a workaround counted. The lasting fix still gets
done, under its own work item.

## 5. Restore first, by rollback when a change caused it

When an outage correlates with a recent release, roll the release back before you look for the
cause. The reason and the SRE quote are in [rollback-plan.md](rollback-plan.md) section 3, which
also holds the plan.

This practice's own rule for the case with no correlated change: when no release, flag or setting
change came before the symptoms, there is nothing to roll back. The person on call works the restore
under the same clock, and a workaround counts once it meets the clause's "restored" (section 4).

Measure it with DORA's failed deployment recovery time: the time to recover from a deployment that
fails and needs immediate intervention. Compare it with the restore target in the SLA.

## 6. Why small work items make the SLA easier

A small change is quick to find and quick to roll back (Google SRE workbook). The work item key
leads from the incident to the deployment, the pull request and the reason, because a deployment
links to a work item when a commit in it carries the key (Atlassian). Rules for the size and the
links are in [tickets.md](tickets.md) sections 3 and 4.

## 7. In Jira

SLAs are a Jira Service Management feature, not part of Jira Software alone. A goal is set per
priority and uses a calendar, and the clock has start, pause and stop conditions. By default the
clocks run 24/7; set a calendar to limit them to working hours. Atlassian's own example of a goal is
that blockers are resolved within 24 hours (legacy page). Jira priorities run from Highest to
Lowest; map each SEV level of section 2 to one priority.

Without Jira Service Management, a daily Automation rule on the due date can flag overdue work.
Atlassian says there is no built-in trigger for a passed due date, and gives a scheduled trigger
with this JQL:

```
duedate = startOfDay() AND resolution is empty
```

The rule flags work, and it does not time an SLA. The query is good because it flags only
unresolved items due today, so it never pages anyone about finished work, and it needs no app
beyond Jira Automation.

## 8. Sources

- Google, ["Service Level Objectives"](https://sre.google/sre-book/service-level-objectives/), SRE
  book, 2016.
- Atlassian, ["SLA vs. SLO vs.
  SLI"](https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli), undated.
- Atlassian, ["Severity
  levels"](https://www.atlassian.com/incident-management/kpis/severity-levels), undated.
- PeopleCert, [ITIL 4 incident
  management](https://www.peoplecert.org/browse-certifications/it-governance-and-service-management/ITIL-1/itil4-practices-incident-management-3684),
  undated.
- Atlassian, ["Incident management vs problem
  management"](https://www.atlassian.com/incident-management/devops/incident-vs-problem-management),
  undated.
- Google, ["Incident response"](https://sre.google/workbook/incident-response/), SRE workbook, 2018.
- DORA, ["DORA's software delivery metrics"](https://dora.dev/guides/dora-metrics/), 2026-01-05.
- Google, ["Canarying releases"](https://sre.google/workbook/canarying-releases/), SRE workbook,
  2018.
- Atlassian, ["SLAs"](https://confluence.atlassian.com/servicedeskcloud/slas-732528967.html) (legacy
  page) and ["What are
  SLAs"](https://support.atlassian.com/jira-service-management-cloud/docs/what-are-slas/), undated.
- Atlassian, ["Configure priorities for
  projects"](https://support.atlassian.com/jira-cloud-administration/docs/configure-priorities-for-projects/),
  undated.
- Atlassian, ["Trigger an automation rule based on the due date
  field"](https://support.atlassian.com/automation/kb/trigger-an-automation-rule-based-on-due-date-field/),
  undated.
