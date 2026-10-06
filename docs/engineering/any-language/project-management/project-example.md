# Worked example: one project from charter to rollback

One small project, walked through the five project phases, with every artifact of this practice
filled in and the reason it is good next to it. Every name, date and number is invented, and the
SLA target is Acme Corp's own choice. Each section names the rules file it follows, so read the
rule there and copy the shape here.

**Navigation**

- [1. The project in one paragraph](#1-the-project-in-one-paragraph)
- [2. Charter and stakeholders](#2-charter-and-stakeholders)
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

## 2. Charter and stakeholders

Issued by Jane Doe on 2026-10-19, in initiation, before any plan exists.

```
# Charter: Payment provider integration (PROJ)

Purpose and business need: move card payments in the Acme Corp online shop's checkout to a new provider, so
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
Approvers: Jane Doe (scope, budget; provider contract, sign); head of security (provider contract,
data clauses acceptable).   # two decisions, so each has one decider (roles-and-decisions.md section 5)
Informed: customer support lead, finance.
Milestones: provider contract signed (Dec 2026); test payments pass (Jan-Feb 2027);
1% of traffic live (Feb 2027); 10% live (Mar 2027); all traffic moved (by 2027-03-31).
Exact dates are in the plan.   # month windows keep the charter stable when the plan moves (charter.md section 3)
Budget: USD 180,000 in total.
Constraints: all traffic moved by 2027-03-31 is fixed, because the old provider's contract
ends then; the budget is the limit above; scope may move.   # the fixed one is named, so the team knows what gives (principles.md section 6)
Assumption: the provider's test environment is available by the end of planning.
Check by: 2026-11-16.   # an assumption with a date is tested before it fails (charter.md section 2)
Top risks: provider outage in cut-over; success rate drops after the move.
```

Where it lives ([charter.md](charter.md) section 5): a Confluence page named "PROJ charter", linked
to the epics `PROJ-10 Payment provider integration`, `PROJ-11` and `PROJ-12`. Jane Doe's written approval is a comment on
that page, dated 2026-10-19, and the plan does not start before it exists.

The charter is good because every line is a fact someone can check later and none is a task
([charter.md](charter.md) section 2).

### Stakeholder register

Made in initiation from the charter's approvers and informed people, kept as a Confluence page
linked from the charter page ([stakeholders.md](stakeholders.md) section 2). Scale: does not know,
against, neutral, supports, leads.

| Name and role | Concerns and expectations | Influence | Interest | Engagement now → wanted | How and how often | Owner |
|---|---|---|---|---|---|---|
| Jane Doe, sponsor | Checkout not tied to one provider; cost inside the budget | High | High | supports → leads | Weekly update, exception notes, every Sprint Review | John Smith |
| Head of security, approver: provider contract, data clauses acceptable | Card data handled as the contract and the law require | High | Low | neutral → supports | A briefing before the contract is signed; milestone updates | John Smith |
| Customer support lead | Fewer failed-payment tickets; the cut-over dates in advance | Low | High | does not know → supports | Weekly update, Sprint Review | Mary Major |
| Finance; the finance controller speaks for it | Provider fees inside the quote | Low | Low | neutral → neutral | Weekly update | John Smith |
| Account manager at Globex, the new provider | The go-live date and the volume | High | High | supports → supports | A shared channel; each milestone; every Sprint Review | Richard Roe |

Actions for the gaps, each with an owner and a date ([stakeholders.md](stakeholders.md) section 4):

- Jane Doe: agree to open the kickoff and to answer each exception note within one working day, by
  2026-10-26. Owner: John Smith.
- Head of security: walk through the data and uptime clauses by 2026-11-27. Owner: John Smith.
- Customer support lead: send the cut-over dates by 2026-12-04, and invite them to the Sprint Review
  from sprint 2. Owner: Mary Major.

In the four boxes of [stakeholders.md](stakeholders.md) section 3, Jane Doe and Globex are "Work
closely", the head of security is "Keep satisfied", the support lead is "Keep informed", and finance
is "Watch".

The register is good because every gap between engagement now and wanted has an action with an
owner and a date, and every row has one owner ([stakeholders.md](stakeholders.md) sections 2 and 4).

## 3. Plan

Written in planning, after the charter, and baselined by Jane Doe on 2026-11-16.

| Part | In this project |
|---|---|
| Scope | Three deliverables, listed in section 4 |
| Development approach | Chosen per deliverable ([life-cycle.md](life-cycle.md) section 4). Adaptive, in two-week sprints, for `PROJ-10`, `PROJ-12` and the flag code of `PROJ-11` (2.1), because the provider's API and the old payment records will show the team things the charter could not know. Predictive, as dated milestones, for the traffic steps of `PROJ-11` (2.2 to 2.4) and the provider contract, because their order and dates are agreed with the provider in advance |
| Schedule | Four milestones as Jira versions (below), shown on the Timeline of `PROJ` |
| Roles and resources | `PROJ-10` John Smith, `PROJ-11` Richard Roe, `PROJ-12` Mary Major; the payments team of four, with John Smith also the Product Owner and Mary Major the Scrum Master; the RACI matrix and deciders below |
| Risks | The register in section 5, a Confluence page linked to `PROJ-10`, `PROJ-11` and `PROJ-12` |
| Communication | The team uses the `PROJ` board daily; a status update every Friday (below); escalation from a Developer to John Smith, who answers the same working day, and from him to Jane Doe, who answers an exception note within one working day |
| Change control | A change request is a work item; a milestone may move up to one week from its Baseline date on John Smith's decision, a larger move goes to Jane Doe (below) |

Milestones, each a version with a planned release date:

| Version (Fix version) | Original | Baseline | Now |
|---|---|---|---|
| `PROJ 1.0 test payments` | 2027-01-29 | 2027-02-12 | 2027-02-12 |
| `PROJ 1.1 1% live` | 2027-02-12 | 2027-02-26 | 2027-02-26 |
| `PROJ 1.2 10% live` | 2027-03-05 | 2027-03-12 | 2027-03-12 |
| `PROJ 2.0 all traffic` | 2027-03-26 | 2027-03-26 | 2027-03-26 |

Original holds the dates Jane Doe baselined on 2026-11-16 and never changes. Baseline changes only
when Jane Doe approves a change request beyond the tolerance, and only for the milestones it names:
it moved once, on 2026-12-21, for the three that `PROJ-127` moves. Now is the forecast, which John
Smith moves inside the tolerance. The tolerance and the status markers measure from Baseline. The
change request:

```
PROJ-127  Change request (Task), linked to epic PROJ-10
Request: move three milestones later and keep PROJ 2.0 on 2027-03-26.
Reason for all three: the provider's test environment opened on 2026-12-14, four weeks
after the charter's assumption, so test payments cannot start earlier.
- PROJ 1.0 test payments: 2027-01-29 -> 2027-02-12. Its test payments wait on the late environment.
- PROJ 1.1 1% live: 2027-02-12 -> 2027-02-26. It follows PROJ 1.0, and the hold at 1%
  drops from three weeks to two.
- PROJ 1.2 10% live: 2027-03-05 -> 2027-03-12, one week. It follows the hold at 1%,
  and the hold at 10% before PROJ 2.0 drops from three weeks to two.
- PROJ 2.0 all traffic: stays 2027-03-26, because the old provider's contract ends on 2027-03-31.
Beyond tolerance: PROJ 1.0 and PROJ 1.1 move two weeks, more than the one-week tolerance (project-plan.md section 4).
Approver: Jane Doe, 2026-12-21, for each move above.   # old date, new date, approver and reason for each milestone (project-plan.md section 4)
```

The change request is good because it holds, for each milestone, the old date, the new date, the
reason and the approver, so it is the history of those dates and needs no second list
([project-plan.md](project-plan.md) section 4).

Review rhythm: every second Monday, 30 minutes, the team reviews the plan to decide which change
requests to raise and which planning packages to split. Every Thursday, 15 minutes, the team looks
at the board to decide which top risk needs an action and whether anyone is over the WIP limit
([project-plan.md](project-plan.md) section 6).

WIP limit: two work items in progress per person, set by the team at planning. At the Thursday
board look on 2027-01-14, John Smith showed that Mary Major held three items, one over the limit.
The Developers decided that Richard Roe, who held one, would take `PROJ-126`, and Mary Major's
comment on it said where the work stood ([jira-workflow.md](jira-workflow.md) section 6). John Smith
recorded the cost on the plan page: none, because no date moved and no scope left
([principles.md](principles.md) section 3).

The WIP note is good because the project manager only showed the overload, the Developers chose
who took the item, and the cost was checked and written down, so the team did not absorb the extra
work in silence ([principles.md](principles.md) section 3).

Rolling wave: on 2026-11-16 the work for `PROJ 1.0` and `PROJ 1.1` is cut into work items with
owners. The work for `PROJ 1.2` and `PROJ 2.0` stays at the level of a planning package in section
4, and is cut into work items when its version is one release away.

The rolling wave is good because only the next two versions are cut into work items, so the far
work is detailed when the team knows enough to detail it, and is not written twice
([project-plan.md](project-plan.md) section 5, [wbs.md](wbs.md) section 5).

The plan is good because the Original date stays next to Baseline and Now, so the sponsor sees the
whole slip and the part each approved change explains ([project-plan.md](project-plan.md)
section 4).

Artifacts kept ([operating-system.md](operating-system.md) section 3): every artifact the rule files
ask for, each kept short, plus the conditional ones whose condition holds here: the critical path
(`PROJ 1.0` has a fixed date, 2027-02-12, set by the change request `PROJ-127`, and its test payments wait on two other work packages),
contingency plans for R-1 and R-2 (impact 5 and 4), a DACI page for D-3 (moving payment traffic is
hard to undo), and an exception note when the marker turned Off track.

The list is good because each conditional artifact names the condition that holds for it, so a reader can check the choice against the project ([operating-system.md](operating-system.md) section 3).

### Roles and decisions

The RACI matrix, a Confluence page linked from the charter page
([roles-and-decisions.md](roles-and-decisions.md) section 3):

| Deliverable or activity | Jane Doe | John Smith | Richard Roe | Mary Major | Head of security |
|---|---|---|---|---|---|
| `PROJ-10` Payment provider integration | I | A | R | R | C |
| `PROJ-11` Routing flag | I | C | A, R | R | |
| `PROJ-12` Payment records migration | I | C | R | A | C |
| The provider contract: data clauses acceptable | I | R | C | | A |
| The provider contract: sign | A | R | C | | I |

The matrix is good because each row has exactly one A, and the A of each epic is the owner in its
WBS dictionary entry in section 4, so the two never disagree.

Deciders ([roles-and-decisions.md](roles-and-decisions.md) section 5): a milestone move of up to one
week, John Smith; a larger move, Jane Doe; the provider contract, data clauses acceptable: head of
security; the provider contract, sign: Jane Doe, after the head of security's yes; a technical
choice that is hard to undo, Richard Roe, whom the Developers named; go or no-go for each release,
Richard Roe; a rollback, the decider of section 8; the order of the Product Backlog and canceling a
work item, John Smith as Product Owner. The other kinds follow the defaults of
[roles-and-decisions.md](roles-and-decisions.md) section 5.

The list is good because each kind of decision has one name, and the provider contract is split
into two decisions with one decider each, so nobody waits for a second decider
([roles-and-decisions.md](roles-and-decisions.md) section 5).

One entry of the decision log, a Confluence page from the DACI template
([roles-and-decisions.md](roles-and-decisions.md) sections 6 and 7):

```
D-3  2026-11-09  Move traffic by the routing flag in steps (1%, 10%, all), not in one night
Driver: John Smith. Approver: Jane Doe. Contributors: Richard Roe, head of security.
Informed: customer support lead.
Due: 2026-11-13, before the plan is baselined on 2026-11-16.
Options: one night for all traffic; steps by flag; split by card brand.
Reason: the flag turns traffic back in minutes, and one night has no way back without
a new deploy (rollback-plan.md section 2).   # the reason is what a later reader cannot rebuild
Links: PROJ-11.
```

The entry is good because the reason names what the chosen option protects, and the links lead to
the epic that carries it out.

### Schedule and critical path

Drawn on 2026-12-21 with the change request `PROJ-127`, after the provider's test environment opened
late. It runs to `PROJ 1.0`, the fixed date the work below leads to; the later milestones keep their planning packages (section 4) until their work is cut. Days are working days from 2026-12-21, with the team off from 2026-12-24 to 2027-01-01, and each
duration is the high end of its range; float is counted to the end of the path, day 32
([schedule.md](schedule.md) sections 2 and 3):

| Work package | Waits on | Days | Finishes on day | Float (days) |
|---|---|---|---|---|
| 2.1 Flag and routing code | nothing | 3 | 3 (2026-12-23) | 4 |
| 3.2 Write the provider on each payment | nothing | 7 | 7 (2027-01-07) | 0 |
| 1.3 Test payments in staging | 2.1, 3.2 | 12 | 19 (2027-01-25) | 0 |
| 1.4 Load test at 2x peak | 1.3 | 8 | 27 (2027-02-04) | 0 |
| The week of reserve named in R-3 (section 5) | 1.4 | 5 | 32 (2027-02-11) | 0 |

The critical path is 3.2, 1.3, 1.4 and the reserve; it ends on 2027-02-11, one day before the new
date of `PROJ 1.0 test payments`, 2027-02-12. A slip of up to four days in 2.1 moves nothing on the
path. A slip in 3.2, 1.3 or 1.4 first uses the week of reserve and the one spare day; only a slip of
more than six working days moves the milestone. The load test date in R-1 moved with `PROJ-127`,
to 2027-02-04 (section 5).

The table is good because each item shows what it waits on and its float, so a late item can be read
at once as either harmless or a milestone move.

### Weekly status update

Posted on Friday 2026-12-18, on the page linked from the epics ([communication.md](communication.md)
section 2). The team's marker definitions, in ten words or fewer: On track, within a week of baseline as
planned; At risk, within a week only if a named action lands; Off track, beyond a week even with the
planned actions.

```
PROJ status, week of 2026-12-14
Marker: Off track.   # the late date is beyond the one-week tolerance, so the marker follows from it (communication.md section 3)
Forecast: PROJ 1.0 test payments between 2027-02-08 and 2027-02-12, baseline 2027-01-29,
from the velocity chart of PROJ Sprint 1 and PROJ Sprint 2 (2026-11-16 to 2026-12-11):
the early date at the pace of Sprint 2, the faster, and the late date at that of Sprint 1.   # the fastest and slowest named sprints set the range, not the version report's fixed 10% lines (schedule.md section 2)
Changed: the provider's test environment opened on 2026-12-14, four weeks after the
charter's assumption; the work of 1.1, 1.2 and 3.1 is finished and waits in Pre-prod for PROJ 1.0.
Decisions: none this week.
Risks: R-1 unchanged; a new issue: the assumption in the charter failed.
Needed: Jane Doe's decision on the exception note sent today.   # the ask, so the sponsor knows what to give back (communication.md section 2)
```

The exception note sent the same day held the forecast, the cause, two options with what each
costs, and John Smith's recommendation. Option 1: move `PROJ 1.0` and `PROJ 1.1` by two weeks and
`PROJ 1.2` by one, and keep `PROJ 2.0`. It costs two weeks on the first two milestones, one week on
the third, and one week off each hold, at 1% and at 10%, so R-1's trial at 1% runs two weeks, not
three. Option 2: load test at 1x peak instead of 2x. It costs no time, but leaves the timeouts of
R-1 untested at peak. John Smith recommended the first, because it keeps the load test at 2x peak
that R-1 relies on and still gives the 1% trial two weeks. Jane Doe chose it on 2026-12-21, and it
became the change request `PROJ-127` above ([communication.md](communication.md) section 5).

The note is good because each option says what it costs, so the sponsor can decide in one reply ([communication.md](communication.md) section 5).

The update is good because the marker can be checked against the forecast and the tolerance, and
the last line tells the sponsor what is needed from them.

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
   1.5  Payment error messages to the shopper    (work package)   # stories PROJ-135 and PROJ-139 (jira-workflow.md section 7), PROJ-136
2  PROJ-11  Routing flag (epic)
   2.1  Flag and routing code                    (work package)   # task PROJ-123
   2.2  1% live trial                            (work package)
   2.3  Ramp to 10%                              (planning package)   # far work, split when near (wbs.md section 5)
   2.4  Ramp to all traffic                      (planning package)   # same reason
   2.5  Remove the routing flag                  (work package)   # task PROJ-150, made with the flag (release.md section 6)
3  PROJ-12  Payment records migration (epic)
   3.1  Nullable provider column                 (work package)   # task PROJ-124
   3.2  Write the provider on each payment       (work package)   # task PROJ-125, the first of its work items (wbs.md section 7)
   3.3  Backfill old records with the old provider (planning package) # same reason
```

The 100% rule check: the charter's scope in is checkout card payments (epic 1 and 2, with the
ramp to all traffic in 2.4), payment records (epic 3) and the routing flag (epic 2). Nothing in
the tree is in the charter's scope out.

The dictionary, one entry in the epic's description, three lines each:

```
PROJ-10 Payment provider integration (epic)
Scope: the API client and the settings the shop needs to take card payments through the provider, and the messages a shopper sees when the provider declines a card or times out.
Owner: John Smith. Done when: test payments pass in staging and the load test at 2x peak
passes.

PROJ-11 Routing flag (epic)
Scope: the flag that sends each card payment to the old or the new provider, the steps that move traffic from 1% to all, and the removal of the flag after the move.
Owner: Richard Roe. Done when: with the flag off every payment goes to the old provider, and at 100% every card payment goes to the new one.

PROJ-12 Payment records migration (epic)
Scope: the nullable provider column on payment records, the code that writes it, and the backfill of old records.
Owner: Mary Major. Done when: every payment record holds its provider, old ones through the backfill, and the old release runs against the new schema.
```

The WBS is good because each epic is a thing the sponsor can accept or reject ([wbs.md](wbs.md)
section 3). The dictionary is good because each entry gives the scope, one owner, the same person
as the A of the epic's RACI row, and a done-when the sponsor can check, so two people cannot read
one epic two ways ([wbs.md](wbs.md) section 6).

## 5. Risk register

Created in planning, kept as a Confluence page linked to `PROJ-10`, `PROJ-11` and `PROJ-12` ([plan](#3-plan) names the
place). Dated 2026-11-16; R-1 updated on 2026-12-21 for the change request `PROJ-127`.

| ID | Risk | P | I | Score | Response | Actions | Owner | Trigger | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-1 | Because the new provider is untested at our volume, its API may time out during cut-over, so checkout payments fail | 3 | 5 | 15 | Mitigation | Load test at 2x peak by 2027-02-04 (2027-01-15 before `PROJ-127`); route 1% first in `PROJ 1.1` on 2027-02-26, and hold there two weeks before 10%. Contingency plan: on the trigger, John Smith asks Globex to raise the rate limit, and `PROJ 1.0` waits for a second load test to pass, since only the reserve week is left after the load test; it costs up to two weeks on `PROJ 1.0` and each later milestone, which takes `PROJ 2.0` past the fixed 2027-03-31 unless the holds at 1% and 10% shrink again, so John Smith sends Jane Doe an exception note the same day | John Smith | Timeouts above 1% in the load test | Open |
| R-2 | Because the draft contract has no uptime clause, a provider outage after cut-over may leave checkout down for hours, so SEV 1 targets are missed | 2 | 4 | 8 | Transference | Put a 99.9% uptime clause and a 1-hour incident response time into the contract by 2026-12-04. Contingency plan: on the trigger, John Smith takes the contract to Jane Doe with one option, keeping the old provider on standby for a SEV 1 until 2027-03-31; the standby costs USD 4,000 a month | John Smith | The provider refuses the clause | Open |
| R-3 | Because one engineer knows the old payment code, a long absence may delay the routing flag, so `PROJ 1.1` is late | 2 | 2 | 4 | Acceptance | None unless it happens; one week of schedule reserve exists | John Smith | Absence announced | Open |
| R-4 | Because the provider's fee tier is fixed at signing, a volume fee above the quote may exceed the budget, so the project overspends | 3 | 3 | 9 | Escalation | Send the fee quote and the budget gap to Jane Doe by 2026-12-04 | Jane Doe | A quote above USD 0.30 per payment | Open |

R-1 and R-2, the two threats with an impact of 4 or more, carry a contingency plan for their
trigger, and the week of schedule reserve in R-3 is the one named contingency reserve, kept out of the
estimates ([risks.md](risks.md) section 6). Four different responses are in use: mitigation, transference (the contract moves the outage
impact and the response to the provider), acceptance, and escalation (the budget belongs to the
sponsor, so the owner is Jane Doe). The top risks are reviewed every Thursday, and the whole
register at each phase end. R-3 has the lowest score and is still read aloud, because the score
only ranks attention. R-1 and R-2 grew from the charter's top risks. R-2, R-3 and R-4 came out of
the pre-mortem on 2026-11-02, where the team wrote down why the project had failed.

The register is good because every risk is specific enough to watch: cause, event and effect
([risks.md](risks.md) section 2), each threat with an impact of 4 or more has a contingency plan with
its trigger and its cost, and the one reserve is named in the register, not hidden in the estimates,
so anyone can see when it is used up ([risks.md](risks.md) section 6).

## 6. Work items

The project's work items, at least one of each type (epic, story, task, bug and subtasks), are in
[jira-work-item-example.md](jira-work-item-example.md). The bug `PROJ-131` is the one used below.

The bug's branch and commit, named by [git.md](../git/git.md) sections 2 and 3. The pull request
takes the commit's title (git.md section 4) and links `PROJ-131`:

```
branch: fix/PROJ-131-saved-card-ignores-flag
commit: fix [PROJ-131]: route saved-card payments by flag

- The saved-card path took the provider from a default and ignored the
  flag, so payments went to the new provider with the flag off.
```

The branch and commit are good because the key ties them and the pull request to `PROJ-131`, so
the fix is found from the work item ([git.md](../git/git.md) sections 2 and 3).

Fix version on `PROJ-131`: `PROJ 1.0 test payments`, so the release page shows the bug fixed
before the release ([tickets.md](tickets.md) section 5). The team's Definition of Done:

```
- Every acceptance criterion is met and checked by someone other than the author.   # a second reader finds what the author missed (tickets.md section 2)
- The pull request is reviewed and merged to main.
- Tests for the change pass.
- The change is deployed to production.   # the team's Done status means in production (jira-workflow.md section 2; tickets.md section 2 owns the DoD)
- The work item is in its Fix version.   # the release page is only true if every item is in it (tickets.md section 5)
- If the change touches routing, turning the flag off still sends payments to the old provider.   # keeps the rollback step true (rollback-plan.md section 2)
```

The list is good because each line is a check a reviewer can tick, and the flag line keeps the
rollback step true ([tickets.md](tickets.md) section 2, [rollback-plan.md](rollback-plan.md)
section 2).

## 7. SLA

Severity is written first, and each level maps to one Jira priority
([sla.md](sla.md) sections 2 and 7):

| Level | Acme Corp example | Jira priority | Restore target |
|---|---|---|---|
| SEV 1 | Card payments fail for all shoppers | Highest | 4 hours |
| SEV 2 | Card payments fail for one card brand or country | High | 24 hours |
| SEV 3 | Checkout is slow, or a receipt line is wrong | Medium | none agreed |

The table is good because each level maps to one Jira priority and one restore target, so the
person on call picks the clock from the level ([sla.md](sla.md) sections 2 and 7).

The SEV 1 clause, with the five parts of [sla.md](sla.md) section 4 (the on-call line belongs to
the clock part):

```
SEV 1 checkout outage: restore within 4 hours.   # Acme Corp's invented number
Severity: SEV 1 only.
Clock: 24/7, from the alert or the first customer report.   # the person on call writes that time into the item, even if it is opened later (sla.md sections 3 and 4)
On call: Richard Roe's team, weekly rota, 24/7.   # who is on call outside working hours (sla.md section 4)
Restored: checkout success rate at or above 96.5% for 30 minutes.   # a number and a window, so a workaround is not a dispute (sla.md section 4)
Lasting fix: a problem work item with its own target, opened when service is restored.   # the clock measures restore, not the root cause (sla.md section 4)
Consequence: a miss goes to Jane Doe in a written review within 2 working days.   # without a consequence it is an SLO (sla.md section 1)
```

The SEV 2 clause, with the same five parts:

```
SEV 2 payment failure for one card brand or country: restore within 24 hours.   # Acme Corp's invented number
Severity: SEV 2 only.
Clock: 24/7, from the alert or the first customer report.   # one calendar is picked and named, so nobody argues about nights (sla.md section 4)
On call: Richard Roe's team, weekly rota, 24/7.   # who acts at night (sla.md section 4)
Restored: checkout success rate of the failing card brand or country at or above 96.5% for 30 minutes.
Lasting fix: a problem work item with a due date, opened when service is restored.
Consequence: a miss goes to Jane Doe in a written review within 2 working days.   # without a consequence it is an SLO (sla.md section 1)
```

In Jira Service Management ([sla.md](sla.md) section 7): one goal, "Time to restore", for priority
Highest at 4 hours, on a 24/7 calendar. The goal starts when the item is created, so it can read shorter than the contract clock; the
person on call records the alert time in the item, and that time decides a miss
([sla.md](sla.md) section 3). It has no pause condition. It stops when the status becomes Restored, which the on-call engineer sets only
after the checkout success rate has held at or above 96.5% for 30 minutes, so the 4 hours include
that window. When the outage follows a
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
without an answer to the page. One name at a time; nobody waits for a group.   # a named backup, so an absent decider does not stall the outage (rollback-plan.md section 2)
Steps: 1. Turn the routing flag off. All payments go to the old provider; no new code.
       2. Watch the checkout success rate until it holds at or above 96.5% for 30 minutes (SLA "restored", section 7).
       3. Once restored, open the rollback work item and the problem work item for the cause,
          both linked to the incident with "causes / is caused by" (Where it lives, below).
       4. Keep the flag off in every environment until the fix for the cause is merged.   # main still holds the change, so the next deploy would ship it again (rollback-plan.md section 3)
Data: payments written during the release keep provider = new; the old release ignores
the column. Changes that cannot be undone: none.   # "none" is stated, so the decider knows (rollback-plan.md section 4)
Time: 15 minutes trigger window + up to 15 minutes for the backup + 7 minutes to turn the flag off
(rehearsal) + 30 minutes until restored = 67 minutes, inside the 4-hour SEV 1 target.   # counted from the alert, as the SLA clock is (rollback-plan.md section 2)
Who is told: John Smith, Jane Doe, the customer support lead.
Way to users: the routing flag at 1% of card payments (release.md section 6).   # it decides the way back, so the plan holds it
Flag removal: PROJ-150, in epic PROJ-11.   # a flag left in the code is the trap of release.md section 6
```

The data change was expanded first. `PROJ-124` added the `provider` column as nullable in
`PROJ 1.0 test payments`, two weeks before this release, so the old release runs against the new
schema. No contract step is planned in this project, so the column stays nullable.

Rehearsal, 2027-02-19 in staging under test load: the flag was turned off at the decision, all
test payments went to the old provider after 7 minutes, and the old release was started against
the migrated schema. The rehearsal also showed that the on-call role could not change the flag in
staging; the permission was added the same day.

The rehearsal record is good because it measured the 7 minutes that the plan's Time line uses, and
the gap it found was closed before the release, not during an outage
([rollback-plan.md](rollback-plan.md) section 5).

Where it lives ([rollback-plan.md](rollback-plan.md) section 6): in the description of the version
`PROJ 1.1 1% live`, with a link to the Confluence page that holds the long form. The version
holds the work items that ship in it, such as the change that sets the flag to 1%; `PROJ-123`,
`PROJ-124`, `PROJ-125` and `PROJ-131` shipped earlier, in `PROJ 1.0 test payments`. A rollback, if
one happens, is recorded in the rollback work item, not on the version, whose state and description
stay as they are. That work item is linked to the incident with "causes / is caused by", lists
every work item that is no longer live, and is added to the Related work of `PROJ 1.1`, so a reader
of the version finds it. The rolled-back items stay Done in `PROJ 1.1`, and each gets one Bug,
linked to it and to the incident, in a new version that ships the fix.

The plan is good because every part can be checked before the deploy ([rollback-plan.md](rollback-plan.md)
section 2).

### Go or no-go

Decided by Richard Roe, the release decider of section 3, on the morning of the release, and written
into the description of the version `PROJ 1.1 1% live` ([release.md](release.md) section 3):

```
Go: Richard Roe, 2027-02-26 09:10.
- Every work item in the version in Pre-prod, with every Definition of Done line met except the
  production deploy.
- No unresolved work item in the version outside Pre-prod; the release page shows no warning.
- main holds no change of a work item outside this version: every change merged since
  PROJ 1.0 belongs to a work item in PROJ 1.1.   # else that change would ship with this release (release.md section 3)
- Ran in staging since 2027-02-19.
- Rollback plan written and rehearsed on 2027-02-19 (above).
- Way to users chosen: the routing flag at 1%.   # a no-go would name the line that failed (release.md section 3)
```

The record is good because each line is a criterion of [release.md](release.md) section 3 that
someone can check, and the decider and the time are on the version itself.

## 9. Closure

All traffic moved on 2027-03-26. The sponsor accepts the result against the charter's success
criteria, not against the plan.

| Success criterion (section 2) | Result | Accepted |
|---|---|---|
| Every card payment through the new provider by 2027-03-31 | Done on 2027-03-26 | Jane Doe, 2027-04-09 |
| Success rate no lower than 96.5%, first 14 days at 100% | 96.7% | Jane Doe, 2027-04-09 |
| Cost within USD 180,000 | USD 171,500 | Jane Doe, 2027-04-09 |

Jane Doe's acceptance is a comment on the charter page, dated 2027-04-09, so the phase can be
shown to have ended ([life-cycle.md](life-cycle.md) section 2).

The actual dates, next to both dates of the plan ([project-plan.md](project-plan.md) section 4):

| Version | Original | Baseline | Actual |
|---|---|---|---|
| `PROJ 1.0 test payments` | 2027-01-29 | 2027-02-12 | 2027-02-12 |
| `PROJ 1.1 1% live` | 2027-02-12 | 2027-02-26 | 2027-02-26 |
| `PROJ 1.2 10% live` | 2027-03-05 | 2027-03-12 | 2027-03-12 |
| `PROJ 2.0 all traffic` | 2027-03-26 | 2027-03-26 | 2027-03-26 |

The whole slip against Original, two weeks on the first two milestones and one week on the third,
is the part `PROJ-127` explains; nothing slipped against Baseline.

The risk register is reviewed one last time. Each risk still open gets a named owner for after the
project and a follow-on action, and its row is marked handed over
([life-cycle.md](life-cycle.md) section 2):

| ID | Status at closure | Owner after the project | Follow-on action |
|---|---|---|---|
| R-1 | Closed: did not happen; the cut-over is over | none | none |
| R-2 | Handed over | Richard Roe, for the on-call team | Each month, check the provider's uptime against the contract's 99.9% clause, and take a miss to Globex |
| R-3 | Closed: did not happen | none | none |
| R-4 | Handed over | Jane Doe, who owns the payments budget | Each month, compare the provider's fees with the quote of USD 0.30 per payment |

Then the epics `PROJ-10`, `PROJ-11` and `PROJ-12` are closed.

Lessons learned, from a 60-minute retrospective on 2027-04-14, each with an owner and a date:

- The provider's test environment arrived four weeks late (`PROJ-127`). Next project: write the
  environment date into the contract and track it as a dependency. Owner: John Smith, by 2027-05-14.
- The rehearsal found a missing permission that would have cost minutes in a real rollback.
  Rehearse every rollback in the release week. Owner: Richard Roe, by 2027-05-14.
- The saved-card bug (`PROJ-131`) was fixed in one commit the day it was found, because the work
  item was small. Keep every work item within three working days ([tickets.md](tickets.md)
  section 3). Owner: Mary Major, by 2027-05-14.

The lessons are good because each names what to change next time, one owner and a date, so the
retrospective changes how the next project runs ([life-cycle.md](life-cycle.md) section 2).

The closure is good because the sponsor accepts against measured criteria, the actual dates are
compared with both Original and Baseline, and no open risk is dropped: each one left open has an
owner after the project and a follow-on action ([life-cycle.md](life-cycle.md) section 2,
[project-plan.md](project-plan.md) section 4).
