# Release

What a release is, the environments it passes through, the go or no-go decision before it reaches
production, how it is numbered, and how it reaches users. Read this file when you plan a release,
and before you mark a Jira version released. The way back is in [rollback-plan.md](rollback-plan.md),
and the SDLC phase a release closes is in [life-cycle.md](life-cycle.md) section 3.

**Navigation**

- [1. A release is a version](#1-a-release-is-a-version)
- [2. Environments](#2-environments)
- [3. Release criteria and the go or no-go decision](#3-release-criteria-and-the-go-or-no-go-decision)
- [4. Version numbers](#4-version-numbers)
- [5. Continuous integration and delivery](#5-continuous-integration-and-delivery)
- [6. How the release reaches users](#6-how-the-release-reaches-users)
- [7. In Jira](#7-in-jira)
- [8. Sources](#8-sources)

## 1. A release is a version

Plan each release as one Jira version, and mark the version released only after the change runs in
production. PMI defines a release as "One or more components of one or more products, which are
intended to be put into production at the same time." (PMI Lexicon, 2026) A version, and the Fix
version field that puts a work item into it, are defined in [tickets.md](tickets.md) section 5.

Releasing a version in Jira deploys nothing. Jira links a deployment to a work item when "a commit
associated with the deploy contains the work item key in its commit message" (Atlassian). The reason
for the order (this practice's own): the Released state is what the release page and the team trust,
so it must follow the deploy, not announce it.

## 2. Environments

Move every change through the same environments, in the same order: development, testing, staging
and production. These are the four environment types Jira's Deployments feature knows (Atlassian),
so name the team's environments to match them, and Jira groups the deployments. A team may run
development and testing as one. What staging is for, and the Pre-prod status that shows a change
there, are in [jira-workflow.md](jira-workflow.md) section 2.

## 3. Release criteria and the go or no-go decision

Before a release goes to production, one named person decides go or no-go against a short written
checklist. Write the decider's name, the decision and its date in the version's description. The
rule is this practice's own, built on two sources:

- Google SRE gives launch decisions to one role: Launch Coordination Engineers act as "gatekeepers
  and signing off on launches determined to be 'safe'", using a checklist that gives "action items
  and pointers to more information". It also warns that "it's hard to design a process that is
  simultaneously lightweight and thorough", so keep the checklist short.
- Jira has no such gate: the release dialog asks only to "Choose what to do with any unresolved work
  items, and enter a release date", and the release page warns about done work items with open pull
  requests or unreviewed code (Atlassian).

PMI's Lexicon has a "go/no-go decision", but it is about the whole initiative: "The process of
determining if an initiative should continue or be stopped." A release decision is a smaller one,
so do not cite PMI for it.

The checklist:

| Criterion | Where the rule lives |
|---|---|
| Every work item in the version is in Pre-prod and meets every line of the Definition of Done except the production deploy | [jira-workflow.md](jira-workflow.md) section 2 (Pre-prod); [tickets.md](tickets.md) section 2 (the Definition of Done, which ends with the deploy). The Scrum Guide ties release to it: "If a Product Backlog item does not meet the Definition of Done, it cannot be released" |
| No work item outside Pre-prod is left unresolved in the version, and the release page shows no warning | Jira (section 7); a Pre-prod item has no resolution until it is Done ([jira-workflow.md](jira-workflow.md) section 1) |
| main holds no change of a work item outside this version, unless its feature flag is off or it is reverted | [jira-workflow.md](jira-workflow.md) section 2 |
| The change ran in staging | [jira-workflow.md](jira-workflow.md) section 2 |
| The rollback plan is written and was rehearsed | [rollback-plan.md](rollback-plan.md) sections 2 and 5 |
| The way the release reaches users is chosen | Section 6 |

The checklist is good because each line is one question the decider can answer yes or no, and points
to the rule that owns it, the "pointers to more information" of the SRE checklist. The line on main
is there because a change stays on main after its merge: when its work item moved back or was
canceled, the change would otherwise ship with this release.

The go or no-go decider and the rollback decider of [rollback-plan.md](rollback-plan.md) section 2
may be the same person; who may decide what is in [roles-and-decisions.md](roles-and-decisions.md)
section 5. A no-go keeps the version unreleased and names the criterion that failed.

An emergency release takes a shorter path through the same checklist (this practice's own rule).
Use it only for a fix rolled forward under an open incident ([rollback-plan.md](rollback-plan.md)
section 3) or for a security patch, because in those two cases a delay costs more than the skipped
checks. The same go or no-go decider decides, as for any release, so one person still owns the risk.
The decider may skip the lines "The change ran in staging" and "The rollback plan is written and was
rehearsed" when their time does not fit the SLA target ([sla.md](sla.md) section 4), or, for a
security patch, the date it must be live by; the go line in the version's description names each
skipped line and why, so a reader sees what was not checked. When the staging line is skipped, the
item skips Pre-prod too and moves from Code Review to Done after the production deploy, as on a
board with no staging ([jira-workflow.md](jira-workflow.md) section 2), so the first line of the
checklist then asks only for the Definition of Done. Do the skipped checks afterwards in a work item
linked to the incident ([tickets.md](tickets.md) section 5), or, for a security patch with no
incident, to the patch's own work item, so they are not dropped once the pressure is off. The fix
gets its own patch version (section 4), because a released version never changes.

Atlassian describes the same trade. Emergency changes are "Those changes that must be implemented as
soon as possible; to resolve an incident, roll back a deployment or implement a security patch", and
"Emergency changes should be subject to the same testing, assessment, and authorization as normal
changes, but sometimes it will be necessary to implement the change with less testing due to time
constraints." A rollback, Atlassian's third case, is not a release here: it follows the rollback plan
([rollback-plan.md](rollback-plan.md) section 2).

Check: before you press Release in Jira, find the go or no-go line in the version's description.

## 4. Version numbers

Name each version so a reader can tell what it holds. When other software depends on yours, through
a library or a public API, number it by Semantic Versioning: MAJOR "when you make incompatible API
changes", MINOR "when you add functionality in a backward compatible manner", PATCH "when you make
backward compatible bug fixes". Semantic Versioning starts with a condition: "Software using Semantic
Versioning MUST declare a public API." An application that nobody calls through an API may use a
name and a number of the team's own; Jira checks neither, since "Versions are points-in-time for a
space" (Atlassian).

Never change a released version. Semantic Versioning says "Once a versioned package has been
released, the contents of that version MUST NOT be modified." A fix goes out in a new version, as
[rollback-plan.md](rollback-plan.md) section 6 does after a rollback.

## 5. Continuous integration and delivery

Merge to the main branch at least daily, and keep main ready to release. Fowler defines continuous
integration as merging "into a codebase together with their colleagues changes at least daily", and
continuous delivery as building software "in such a way that the software can be released to
production at any time". DORA says the same of delivery, and adds that it "is commonly conflated with
continuous deployment, but they are separate practices": continuous deployment puts every change
into production automatically (Fowler). Whether every change also deploys by itself is the team's
choice; a release that waits for a date still needs main ready to ship.

PMI's Lexicon defines continuous delivery as "The practice of delivering feature increments
immediately to customers", which is closer to continuous deployment. This practice uses Fowler's and
DORA's terms. How branches and pull requests work is in [git.md](../git/git.md), and why work items
stay small is in [tickets.md](tickets.md) section 3.

## 6. How the release reaches users

Choose how each release reaches users, and write the choice in its rollback plan, because it decides
the way back.

| Way | What it is | Choose it when | Its cost | The way back |
|---|---|---|---|---|
| Rolling update | Kubernetes, as one example: "incrementally replacing the current Pods with new ones" | The old and the new version can serve users side by side | Both versions run during the rollout | Roll back to the previous state (`kubectl rollout undo` in Kubernetes) |
| Blue-green | Two production environments; when the new one works, "you switch the router so that all incoming requests go to the green environment" (Fowler) | You need a switch back in seconds | Two environments, and "Databases can often be a challenge with this technique, particularly when you need to change the schema" | Switch the router back |
| Canary | "slowly rolling out the change to a small subset of users before rolling it out to the entire infrastructure" (Fowler); "A partial and time-limited deployment of a change in a service and its evaluation" (Google SRE) | The risk is in how the change behaves under real traffic | A metric that compares the canary with the rest; one canary at a time, since "Running simultaneous canaries also increases the risk of signal contamination" | Send the canary's traffic back to the old version |
| Feature flag | The code ships switched off and is turned on for more users step by step, "gradually from 0% to 100% of users" (Google SRE) | The release must be separate from the deploy | Each flag is "inventory which comes with a carrying cost" (Hodgson, on Fowler's site) | Turn the flag off ([rollback-plan.md](rollback-plan.md) section 2) |

A schema change under any of these follows expand, migrate, contract
([rollback-plan.md](rollback-plan.md) section 4).

Give every release flag a work item that removes it, in the same epic, when you create the flag
(this practice's own rule). The reason is on record: the SEC's 2013 order on Knight Capital says the
new code of 2012 "repurposed a flag that was formerly used to activate the Power Peg code", that one
of eight servers did not get the new code, and that orders with the flag reached the old code on that
server (SEC Release No. 34-70694, paragraphs 13, 15 and 16); the company's 10-Q reports the loss.

Check: before the release, find the chosen way in the rollback plan, and for a flag, its removal
work item.

## 7. In Jira

- **Release warnings.** With a development tool connected, the release page warns about done work
  items that still have open pull requests or unreviewed code. Read them before the go or no-go
  decision.
- **Deployments.** Connect the CI/CD tool, and keep the work item key in commit messages, so each
  work item shows where it is deployed.
- **Feature flags.** Jira's flag integrations show a flag's state and rollout percentage on the work
  item and on the release page, once the flag is linked to a work item key.
- **Released state.** Set it after the production deploy is checked (section 1). After a rollback,
  [rollback-plan.md](rollback-plan.md) section 6 says what happens to the version.

## 8. Sources

- [PMI Lexicon of Project Management Terms, v5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: release, go/no-go decision, continuous delivery. Read as raw text on 2026-10-06.
- [The Scrum Guide](https://scrumguides.org/scrum-guide.html), November 2020: an item that does not meet the Definition of Done cannot be released.
- Google, ["Reliable Product Launches at Scale"](https://sre.google/sre-book/reliable-product-launches/), SRE book, 2017: Launch Coordination Engineers, the launch checklist, gradual rollouts; and ["Canarying releases"](https://sre.google/workbook/canarying-releases/), SRE workbook, 2018.
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html), undated.
- Fowler, ["Continuous Integration"](https://martinfowler.com/articles/continuousIntegration.html), 2024-01-18; ["ContinuousDelivery"](https://martinfowler.com/bliki/ContinuousDelivery.html), 2013-05-30; ["BlueGreenDeployment"](https://martinfowler.com/bliki/BlueGreenDeployment.html), 2010, updated 2015; ["CanaryRelease"](https://martinfowler.com/bliki/CanaryRelease.html), 2014-06-25.
- Hodgson, ["Feature Toggles (aka Feature Flags)"](https://martinfowler.com/articles/feature-toggles.html), on martinfowler.com, 2017-10-09.
- DORA, ["Continuous delivery"](https://dora.dev/capabilities/continuous-delivery/), undated.
- Kubernetes, ["Performing a Rolling Update"](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/), undated, live.
- Knight Capital Group, [Form 10-Q for the quarter ended 2012-06-30](https://www.sec.gov/Archives/edgar/data/0001060749/000119312512346917/d361681d10q.htm), filed with the SEC, 2012: the loss.
- Securities and Exchange Commission, [In the Matter of Knight Capital Americas LLC, Release No. 34-70694](https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf), 2013-10-16: the repurposed flag and the eight servers.
- Atlassian: ["Set up your deployment integration"](https://support.atlassian.com/jira-cloud-administration/docs/set-up-your-deployment-integration/); ["Link GitHub workflows and deployments to Jira"](https://support.atlassian.com/jira-cloud-administration/docs/link-github-workflows-and-deployments-to-jira-issues/) (environment types); ["Release a version"](https://support.atlassian.com/jira-software-cloud/docs/release-a-version-in-your-classic-project/); ["Check the release status of a version"](https://support.atlassian.com/jira-software-cloud/docs/check-the-release-status-of-a-version/); ["Manage versions"](https://support.atlassian.com/jira-cloud-administration/docs/manage-versions/); ["Integrate with feature flags"](https://support.atlassian.com/jira-cloud-administration/docs/integrate-with-feature-flags/); ["What are changes?"](https://support.atlassian.com/jira-service-management-cloud/docs/what-are-changes/) (emergency changes). All undated, read 2026-10-06.
