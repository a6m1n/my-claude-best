# Worked example: one project from charter to rollback

One small project, walked through the five project phases, with every artifact of this practice
filled in and the reason it is good next to it. Every name, date and number is invented, and the
SLA target is Acme Corp's own choice. Each section names the rules file it follows, so read the
rule there and copy the shape here.

**Navigation**

- [1. The project in one paragraph](#1-the-project-in-one-paragraph)
- [2. Charter](#2-charter)
- [3. Plan](#3-plan)
- [4. WBS](#4-wbs)
- [5. Risk register](#5-risk-register)
- [6. Work items](#6-work-items)
- [7. SLA](#7-sla)
- [8. Release and rollback plan](#8-release-and-rollback-plan)
- [9. Closure](#9-closure)

## 1. The project in one paragraph

Acme Corp moves card payments in its online shop's checkout to a new payment provider. The goal is
that every card payment runs through the new provider by 2027-03-31, with the checkout success
rate no lower than before the move. Jane Doe, head of payments, is the sponsor, and John Smith is
the project manager. The Jira project key is `PROJ`. The change has data (a new `provider` column
on payment records), a feature flag that routes each payment to the old or the new provider, and an
SLA (a SEV 1 checkout outage is restored within 4 hours).

The sections below follow the five phases of [life-cycle.md](life-cycle.md) section 2: initiation
(section 2), planning (sections 3 to 5), execution (sections 6 to 8) with monitoring alongside it
(sections 3 and 5), and closure (section 9).

## 2. Charter

Issued by Jane Doe on 2026-10-19, in initiation, before any plan exists.

```
# Charter: Payment provider integration (PROJ)

Purpose: move card payments in the Acme Corp online shop's checkout to a new provider, so
Acme Corp is no longer tied to one provider for its main revenue path.
Success criteria:
- Every card payment runs through the new provider by 2027-03-31.
- Checkout success rate is no lower than 96.5% (the September 2026 level), measured over
  the first 14 days with all traffic on the new provider.   # a number and a window, so "no lower" can be checked (charter.md section 2)
- Total cost stays within the budget below.
Scope in: checkout card payments, payment records, the routing flag.
Scope out: refunds, invoices, other payment methods.   # the WBS is cut from this line (charter.md section 2)
Sponsor: Jane Doe, head of payments. Project manager: John Smith, with authority to
assign the payments team and spend the approved budget.   # the authority is the point of the charter (charter.md section 2)
Approvers: Jane Doe (scope, budget); head of security (provider contract).
Informed: customer support lead, finance.
Milestones: provider contract signed (Dec 2026); test payments pass (Jan-Feb 2027);
1% of traffic live (Feb 2027); 10% live (Mar 2027); all traffic moved (by 2027-03-31).
Exact dates are in the plan.   # month windows keep the charter stable when the plan moves (charter.md section 3)
Budget: USD 180,000 in total.
Top risks: provider outage in cut-over; success rate drops after the move.
Assumption: the provider's test environment is available by the end of planning.
```

Where it lives ([charter.md](charter.md) section 5): a Confluence page named "PROJ charter", linked
to the epics `PROJ-10 Payment provider integration`, `PROJ-11` and `PROJ-12`. Jane Doe's written approval is a comment on
that page, dated 2026-10-19, and the plan does not start before it exists.

The charter is good because every line is a fact someone can check later and none is a task
([charter.md](charter.md) section 2).

## 3. Plan

Written in planning, after the charter, and baselined by Jane Doe on 2026-11-16.

| Part | In this project |
|---|---|
| Scope | Three deliverables, listed in section 4 |
| Schedule | Four milestones as Jira versions (below), shown on the Timeline of `PROJ` |
| Roles and resources | `PROJ-10` John Smith, `PROJ-11` Richard Roe, `PROJ-12` Mary Major; the payments team of four |
| Risks | The register in section 5, a Confluence page linked to `PROJ-10`, `PROJ-11` and `PROJ-12` |
| Communication | The team uses the `PROJ` board daily |
| Change control | A change request is a work item; a milestone may move up to one week from its baseline date on John Smith's decision, a larger move goes to Jane Doe (below) |

Milestones, each a version with a planned release date:

| Version (Fix version) | Baseline date | Now |
|---|---|---|
| `PROJ 1.0 test payments` | 2027-01-29 | 2027-02-12 |
| `PROJ 1.1 1% live` | 2027-02-12 | 2027-02-26 |
| `PROJ 1.2 10% live` | 2027-03-05 | 2027-03-12 |
| `PROJ 2.0 all traffic` | 2027-03-26 | 2027-03-26 |

The "Baseline date" column never changes after 2026-11-16; "Now" changes only through a change
request. One change request has been recorded since the baseline:

```
PROJ-127  Change request (Task), linked to epic PROJ-10
Request: move PROJ 1.0 and PROJ 1.1 two weeks later, and PROJ 1.2 one week later;
keep PROJ 2.0 on 2027-03-26 by shortening the hold at 10% from three weeks to two.
Beyond tolerance: PROJ 1.0 moves two weeks, more than the one-week tolerance (project-plan.md section 4).
Approver: Jane Doe, 2026-12-21.
Reason: the provider's test environment opened on 2026-12-14, four weeks after the
charter's assumption, so test payments cannot start earlier.   # the request, the approver and the reason are the three things to record (project-plan.md section 4)
```

Review rhythm: every second Monday, 30 minutes, the team reviews the plan to decide which change
requests to raise and which planning packages to split. Every Thursday, 15 minutes, the team looks
at the board to decide which top risk needs an action and whether anyone is over the WIP limit
([project-plan.md](project-plan.md) section 6).

WIP limit: two work items in progress per person, set by the team at planning. On 2027-01-14 Mary
Major held three items; `PROJ-126` moved to Richard Roe the same day
([principles.md](principles.md) section 3).

Rolling wave: on 2026-11-16 the work for `PROJ 1.0` and `PROJ 1.1` is cut into work items with
owners. The work for `PROJ 1.2` and `PROJ 2.0` stays at the level of a planning package in section
4, and is cut into work items when its version is one release away.

The plan is good because the baseline date stays next to the current one, so every slip is visible
([project-plan.md](project-plan.md) section 4).

## 4. WBS

Made in planning from the charter's scope. The top level is deliverables, not phases or teams.
The Jira mapping of each part is in [wbs.md](wbs.md) section 7.

```
Payment provider integration
1  PROJ-10  Payment provider integration (epic)
   1.1  Provider API client                      (work package)
   1.2  Provider settings and secrets            (work package)
   1.3  Test payments in staging                 (work package)
   1.4  Load test at 2x peak                     (work package)
2  PROJ-11  Routing flag (epic)
   2.1  Flag and routing code                    (work package)   # story PROJ-123
   2.2  1% live trial                            (work package)
   2.3  Ramp to 10%                              (planning package)   # far work, split when near (wbs.md section 5)
   2.4  Ramp to all traffic                      (planning package)   # same reason
3  PROJ-12  Payment records migration (epic)
   3.1  Nullable provider column                 (work package)   # task PROJ-124
   3.2  Write the provider on each payment       (work package)
   3.3  Backfill old records with the old provider (planning package) # same reason
```

The 100% rule check: the charter's scope in is checkout card payments (epic 1 and 2, with the
ramp to all traffic in 2.4), payment records (epic 3) and the routing flag (epic 2). Nothing in
the tree is in the charter's scope out.

The dictionary, one entry in the epic's description, three lines each:

```
PROJ-10 Payment provider integration (epic)
Scope: the API client and the settings the shop needs to take card payments through the provider.
Owner: John Smith. Done when: test payments pass in staging and a 1% live trial matches
the old success rate.

PROJ-11 Routing flag (epic)
Scope: the flag that sends each card payment to the old or the new provider, and the steps that move traffic from 1% to all.
Owner: Richard Roe. Done when: with the flag off every payment goes to the old provider, and at 100% every card payment goes to the new one.

PROJ-12 Payment records migration (epic)
Scope: the nullable provider column on payment records and the code that writes it.
Owner: Mary Major. Done when: every payment record written after the release holds its provider, and the old release runs against the new schema.
```

The WBS is good because each epic is a thing the sponsor can accept or reject ([wbs.md](wbs.md)
section 3).

## 5. Risk register

Created in planning, kept as a Confluence page linked to `PROJ-10`, `PROJ-11` and `PROJ-12` ([plan](#3-plan) names the
place). Dated 2026-11-16.

| ID | Risk | P | I | Score | Response | Actions | Owner | Trigger | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-1 | Because the new provider is untested at our volume, its API may time out during cut-over, so checkout payments fail | 3 | 5 | 15 | Mitigation | Load test at 2x peak by 2027-01-15; route 1% first | John Smith | Timeouts above 1% in the load test | Open |
| R-2 | Because the draft contract has no uptime clause, a provider outage after cut-over may leave checkout down for hours, so SEV 1 targets are missed | 2 | 4 | 8 | Transference | Put a 99.9% uptime clause and a 1-hour incident response time into the contract by 2026-12-04 | John Smith | The provider refuses the clause | Open |
| R-3 | Because one engineer knows the old payment code, a long absence may delay the routing flag, so `PROJ 1.1` is late | 2 | 2 | 4 | Acceptance | None unless it happens; one week of schedule reserve exists | John Smith | Absence announced | Open |
| R-4 | Because the provider's fee tier is fixed at signing, a volume fee above the quote may exceed the budget, so the project overspends | 3 | 3 | 9 | Escalation | Send the fee quote and the budget gap to Jane Doe by 2026-12-04 | Jane Doe | A quote above USD 0.30 per payment | Open |

Four different responses are in use: mitigation, transference (the contract moves the outage
impact and the response to the provider), acceptance, and escalation (the budget belongs to the
sponsor, so the owner is Jane Doe). The top risks are reviewed every Thursday, and the whole
register at each phase end. R-3 has the lowest score and is still read aloud, because the score
only ranks attention. R-1 and R-2 grew from the charter's top risks. R-2, R-3 and R-4 came out of
the pre-mortem on 2026-11-02, where the team wrote down why the project had failed.

The register is good because every risk is specific enough to watch: cause, event and effect
([risks.md](risks.md) section 2).

## 6. Work items

The story from [tickets.md](tickets.md) section 2, in `PROJ 1.0 test payments`:

```
PROJ-123  Story    Epic: PROJ-11    Fix version: PROJ 1.0 test payments
As a shopper, I want my card payment to go through the new provider
so that checkout keeps working while Acme Corp changes provider.

Acceptance criteria
- With the flag on, a test card payment is sent to the new provider.
- With the flag off, the same payment is sent to the old provider.
- The payment record stores which provider handled it.
Blocked by: PROJ-124   # the third criterion needs the column (tickets.md section 5)
```

A task, because the work is not an outcome for a shopper:

```
PROJ-124  Task    Epic: PROJ-12    Fix version: PROJ 1.0 test payments
Add a nullable `provider` column to payment records.

Acceptance criteria
- The migration adds the column with no default and no NOT NULL.   # expand step, so the old release still runs (rollback-plan.md section 4)
- The old release runs against the migrated schema in staging.
```

A bug found in testing, in the same version:

```
PROJ-131  Bug    Epic: PROJ-11    Fix version: PROJ 1.0 test payments
With the flag off, a test payment on a returning shopper's saved card goes to the new provider.
Steps: turn the flag off in staging; pay with a saved test card.
Expected: the old provider handles it. Actual: the new provider handles it.
Blocks: PROJ-123
```

The bug's branch and commit, named by [git.md](../git/git.md) sections 2 and 3. The pull request
takes the commit's title (git.md section 4) and links `PROJ-131`:

```
branch: fix/PROJ-131-flag-off-saved-card
commit: fix [PROJ-131]: route saved-card payments by flag

- The saved-card path took the provider from a default and ignored the flag, so
  payments went to the new provider with the flag off.
```

Fix version on `PROJ-131`: `PROJ 1.0 test payments`, so the release page shows the bug fixed
before the release ([tickets.md](tickets.md) section 5). The team's Definition of Done:

```
- Every acceptance criterion is met and checked by someone other than the author.   # a second reader finds what the author missed (tickets.md section 2)
- The pull request is reviewed and merged to main.
- Tests for the change pass.
- The work item is in its Fix version.   # the release page is only true if every item is in it (tickets.md section 5)
- If the change touches routing, turning the flag off still sends payments to the old provider.   # keeps the rollback step true (rollback-plan.md section 2)
```

The items are good because each story has criteria a stranger can check ([tickets.md](tickets.md)
section 2).

## 7. SLA

Severity is written first, and each level maps to one Jira priority
([sla.md](sla.md) sections 2 and 7):

| Level | Acme Corp example | Jira priority | Restore target |
|---|---|---|---|
| SEV 1 | Card payments fail for all shoppers | Highest | 4 hours |
| SEV 2 | Card payments fail for one card brand or country | High | 24 hours |
| SEV 3 | Checkout is slow, or a receipt line is wrong | Medium | none agreed |

The SEV 1 clause, with the five parts of [sla.md](sla.md) section 4 (the on-call line belongs to
the clock part):

```
SEV 1 checkout outage: restore within 4 hours.   # Acme Corp's invented number
Severity: SEV 1 only.
Clock: 24/7, from the alert or the first customer report.   # the person on call writes that time into the item, even if it is opened later (sla.md sections 3 and 4)
On call: Richard Roe's team, weekly rota, 24/7.   # who is on call outside working hours (sla.md section 4)
Restored: checkout success rate back at its normal level for 30 minutes.   # what "restored" means, so a workaround is not a dispute (sla.md section 4)
Lasting fix: a problem work item with its own target, opened when service is restored.   # the clock measures restore, not the root cause (sla.md section 4)
Consequence: a miss goes to Jane Doe in a written review within 2 working days.   # without a consequence it is an SLO (sla.md section 1)
```

The SEV 2 clause, with the same five parts:

```
SEV 2 payment failure for one card brand or country: restore within 24 hours.   # Acme Corp's invented number
Severity: SEV 2 only.
Clock: 24/7, from the alert or the first customer report.   # one calendar is picked and named, so nobody argues about nights (sla.md section 4)
On call: Richard Roe's team, weekly rota, 24/7.   # who acts at night (sla.md section 4)
Restored: the failing card brand or country back at its normal success rate for 30 minutes.
Lasting fix: a problem work item with a due date, opened when service is restored.
Consequence: a miss goes to Jane Doe in a written review within 2 working days.   # without a consequence it is an SLO (sla.md section 1)
```

In Jira Service Management ([sla.md](sla.md) section 7): one goal, "Time to restore", for priority
Highest at 4 hours, on a 24/7 calendar. The goal may start at creation; the on-call person backdates nothing and records the alert time
in the item. It has no pause condition. It stops when the status becomes Restored, which the on-call engineer sets only
after the 30 minutes in the definition, so the 4 hours include them. When the outage follows a
release, the first step is the rollback in section 8, before any search for the cause
([sla.md](sla.md) section 5).

The SLA is good because "restored" is defined by a number and a window, so a workaround cannot
count as a fix ([sla.md](sla.md) section 4).

## 8. Release and rollback plan

For `PROJ 1.1 1% live`, planned for 2027-02-26, written before the deploy. The release is the one
that routes 1% of card payments to the new provider through the flag.

```
Rollback plan: PROJ 1.1 1% live
Trigger: success rate of payments sent to the new provider is below the pre-move level
(96.5%) for 15 minutes, or a SEV 1 or SEV 2 is tied to this release.   # a number with a time window, so nobody argues (rollback-plan.md section 2)
Decider: Richard Roe, on call for the release week; backup Mary Major, who decides after 15 minutes
without an answer to the page. One name at a time; nobody waits for a group.   # (rollback-plan.md section 2)
Steps: 1. Turn the routing flag off. All payments go to the old provider; no new code.
       2. Watch the success rate until it is normal for 30 minutes (SLA "restored").
       3. Open a work item for the cause, linked to the incident with "causes / is caused by".
       4. Keep the flag off in every environment until the fix for the cause is merged.
Data: payments written during the release keep provider = new; the old release ignores
the column. Changes that cannot be undone: none.   # "none" is stated, so the decider knows (rollback-plan.md section 4)
Time: 15 minutes trigger window + up to 15 minutes for the backup + 7 minutes to turn the flag off
(rehearsal) + 30 minutes until restored = 67 minutes, inside the 4-hour SEV 1 target.
Who is told: John Smith, Jane Doe, the customer support lead.
```

The data change was expanded first. `PROJ-124` added the `provider` column as nullable in
`PROJ 1.0 test payments`, two weeks before this release, so the old release runs against the new
schema. No contract step is planned in this project, so the column stays nullable.

Rehearsal, 2027-02-19 in staging under test load: the flag was turned off at the decision, all
test payments went to the old provider after 7 minutes, and the old release was started against
the migrated schema. The rehearsal also showed that the on-call role could not change the flag in
staging; the permission was added the same day.

Where it lives ([rollback-plan.md](rollback-plan.md) section 6): in the description of the version
`PROJ 1.1 1% live`, with a link to the Confluence page that holds the long form. Its work items
(`PROJ-123`, `PROJ-124`, `PROJ-131`) sit in the same version. A rollback, if one happens, is a work
item linked to the incident with "causes / is caused by".

The plan is good because every part can be checked before the deploy ([rollback-plan.md](rollback-plan.md)
section 2).

## 9. Closure

All traffic moved on 2027-03-26. The sponsor accepts the result against the charter's success
criteria, not against the plan.

| Success criterion (section 2) | Result | Accepted |
|---|---|---|
| Every card payment through the new provider by 2027-03-31 | Done on 2027-03-26 | Jane Doe, 2027-04-09 |
| Success rate no lower than 96.5%, first 14 days at 100% | 96.7% | Jane Doe, 2027-04-09 |
| Cost within USD 180,000 | USD 171,500 | Jane Doe, 2027-04-09 |

Jane Doe's acceptance is a comment on the charter page, dated 2027-04-09, so the phase can be
shown to have ended ([life-cycle.md](life-cycle.md) section 2). The risk register is reviewed one
last time and its open rows are closed.

Lessons learned, from a 60-minute retrospective on 2027-04-14, each with an owner and a date:

- The provider's test environment arrived four weeks late (`PROJ-127`). Next project: write the
  environment date into the contract and track it as a dependency. Owner: John Smith, by 2027-05-14.
- The rehearsal found a missing permission that would have cost minutes in a real rollback.
  Rehearse every rollback in the release week. Owner: Richard Roe, by 2027-05-14.
- The saved-card bug (`PROJ-131`) was fixed in one commit the day it was found, because the work
  item was small. Keep one pull request per work item. Owner: Mary Major, by 2027-05-14.

The closure is good because the sponsor accepts against measured criteria ([life-cycle.md](life-cycle.md)
section 2).
