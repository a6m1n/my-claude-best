# Example: an architecture decision record for a public API

A worked example for [decisions.md](decisions.md) section 8. The application is Acme Corp's
billing application, the same invented one as
[test-plan-example.md](../ux-evaluation/test-plan-example.md). Its public invoices API has two
clients: Globex, a partner that pulls invoices into its own accounting system, and Acme Corp's
mobile team. A planned change to the shape of an invoice's amount (work item PROJ-123) would break
both, so the team had to choose how the API takes breaking changes. That choice is hard to undo
and crosses teams, so the team ran DACI (Driver, Approver, Contributors, Informed) for it
([roles-and-decisions.md](../project-management/roles-and-decisions.md) section 6): the Driver
wrote the options and gathered the input on the DACI page, as the DACI play asks [9], and
recorded each objection there with the Approver's answer
([decisions.md](decisions.md) section 7); the record links the page. A coding agent drafted the record from the page and the
proposal thread, and the decider checked and accepted it. Every name, date and number is invented.

The file sits at `docs/adr/0012-version-the-public-invoices-api-in-the-url-path.md` in the billing
application's repository. The section after the record shows the parts that change for a team
that runs no DACI, and the table after that says where each part of the record comes from. A line
a reader might change or delete carries its reason in an HTML comment.

## The record

```markdown
<!-- One decision per file, numbered, under docs/adr/ in the repository the decision is
     about (decisions.md section 8). -->
# ADR-0012: Version the public invoices API in the URL path

## Status

Accepted
- Proposed: 2026-03-02
- Accepted: 2026-03-10
<!-- Opened at Proposed while the team discussed it; only the decider sets Accepted or
     Rejected (decisions.md section 8). -->

Comment window: 2026-03-02 to 2026-03-06, announced with its end date in #team-backend and
sent to Globex's integration team on 2026-03-02. Closed 2026-03-06: postponed to 2026-03-10 to
answer the mobile team's objection.
<!-- The end date is announced when the window opens, so nobody learns of the decision after
     it is made, and the window closes on a recorded disposition (decisions.md section 6). -->

## Decider

Jane Doe, tech lead of the billing team, and the Approver on the DACI page.
<!-- One person: the decider roles-and-decisions.md section 5 names for a technical choice
     that is hard to undo, and so the page's Approver (roles-and-decisions.md section 6). -->

Drafted by: Claude Code 2.1.<n> with the model <model id>, from the DACI page and the proposal
thread in #team-backend, on 2026-03-02.
Accepted by: Jane Doe, on 2026-03-10, after she checked each fact against its source and that
the status matches what was decided.
<!-- An agent may draft; a named person accepts and says what she checked. The agent is named
     by its tool, version and model, so a reader who checks a fact knows what wrote it
     (agents.md section 7). -->

## Context

The public invoices API (/invoices) has no version today. Globex and the mobile app are its
only clients: the gateway logs of the last 90 days show no other caller. PROJ-123 replaces the
invoice's `amount`, a number in major units that rounds wrong for some totals, with
`amount_minor` (an integer) and `currency`. Every client that reads `amount` breaks. Globex
releases its integration twice a year. Old versions of the mobile app stay in use for months
after a new one ships, because users update late.

## Options considered

On the DACI page "Versioning the public invoices API" (link), with the pros, the cons and the
cost of each option, and the objections with the Approver's answers.
<!-- One home for the options, so the page and the record never drift apart
     (roles-and-decisions.md section 6). -->

## Decision

We version the public invoices API by its major version in the URL path. `/v1/` keeps today's
shape and gets no new field. PROJ-123 ships the new amount in `/v2/`. The proposal ended `/v1/`
12 months after `/v2/` ships. The mobile team's objection changed that: old app versions keep
calling the API for months after a release, so `/v1/` now ends only when its calls are below 2%
of the mobile app's calls for 30 days in a row, and never earlier than 12 months after `/v2/`
ships. The end date is set on the day that share has stayed below 2% for 30 days in a row, at
least 6 months after that day, and every client gets it in writing that day.
<!-- What the proposal had and what the objection changed, in the record itself, so a reader of
     the record alone sees how the advice changed the decision (decisions.md section 4). -->

## Consequences

- Good: the gateway counts v1 and v2 calls per client, so the end of v1 rests on data.
- Good: Globex moves in one release by changing its base URL.
- Bad: two route sets to run, test and secure for at least 12 months.
- Bad: each fix to v1 needs a choice whether v2 gets it too; the billing team owns that choice.
- Bad: the public documentation gets a second set of pages, and the support team answers
  questions for both versions.
- Bad: Globex's contract needs a written notice of v1's end date.

## Confidence

Medium. Known: the two clients and how they release. Not known: how many old app versions will
still call v1 a year after v2 ships, and whether a future partner's tooling expects a header.
<!-- A later review reads what was known and what was not at the time of the decision, not
     what was learned since (decisions.md sections 8 and 9). -->

## Revisit when

- A second breaking change is needed less than 6 months after v2 ships, so that three versions
  would run at once.
- The v1 share of the mobile app's calls is still above 2% 12 months after v2 ships.
- A new client of the API asks for header versioning as a condition of its integration.
- Globex still calls `/v1/` 6 months after v2 ships.
<!-- The triggers are written before the outcome, so a review starts from a fact and not from
     a mood (decisions.md section 9). -->

## Confirmation

- Check: a contract test runs every `/v1/` response against the frozen v1 schema in the
  required CI check, so a dropped, renamed or retyped field fails the build.
- Expected if it works: no Globex support ticket about a changed v1 response; Globex on v2
  within 6 months of its release; the v1 share of mobile calls below 2% by 12 months after v2.

## Links

- DACI page: "Versioning the public invoices API" (link)
- Work item: PROJ-123. Its last step, when v2 ships, sets the due date of PROJ-125 and the
  start date of each alert below.
  <!-- The watchers below count from the day v2 ships, which had no date when the record was
       accepted; the work item that ships v2 dates them, so a trigger is watched from its first
       day (decisions.md section 9). -->
- Work item: PROJ-124, decide ADR-0012 by 2026-03-10, owner Jane Doe
  <!-- A decision postponed to a date gets a dated work item with an owner, or nobody brings it
       back on that date (decisions.md sections 6 and 9). -->
- Work item: PROJ-125, due 6 months after v2 ships, owner Jane Doe: until then, a breaking
  change to v2 comes to her first, against the first trigger in Revisit when
  <!-- A trigger tied to a date gets a dated work item with an owner, or nobody sees it fire
       (decisions.md section 9). -->
- Alert: the v1 share of the mobile app's calls on the gateway dashboard, against the 2% trigger
  in Revisit when, from 12 months after v2 ships; owner Jane Doe
  <!-- A trigger tied to a date or a number gets an alert with an owner, or nobody sees it
       fire (decisions.md section 9). -->
- Alert: Globex's v1 calls on the gateway dashboard, against the Globex trigger in Revisit when,
  from 6 months after v2 ships; owner Jane Doe
  <!-- The end condition counts the mobile app's calls only, so Globex's move to v2 has a
       trigger and an alert of its own (decisions.md section 9). -->
- Decision log entry: 2026-03-10, "Version the public invoices API in the URL path"

## Notes

<!-- Add dated notes below. Never edit the text above once it is Accepted: a changed decision
     is a new ADR that supersedes this one, and the only edit here is its Status line
     (decisions.md section 8). -->
- 2026-09-21, Jane Doe: reviewed after the first trigger fired. v2 shipped on 2026-05-04, and
  PROJ-118 asked to rename `status_code` in v2. The team made the change additive (the new field next to the old one)
  instead of opening v3, so two versions still run at once. The decision holds.
```

## Without a DACI page

A team that does not run DACI, such as an open-source project with no
[roles-and-decisions.md](../project-management/roles-and-decisions.md), keeps the options and the
objections in the record itself. These parts change:

- "Decider": the one person the team's own rule names.
- "Drafted by": the proposal thread only.
- "Links": no DACI page, and no log entry where the team keeps no log.
- "Options considered": the full list, then an "Objections and answers" section.

Every other part stays as above:

```markdown
## Options considered

1. **The major version in the URL path** (`/v1/invoices`, `/v2/invoices`).
   - Pros: the version shows in every request, log line and gateway metric, so the team can
     count who still calls v1 before turning it off. A client moves by changing one base URL.
   - Cons: the team runs and tests two sets of routes while both versions live. An invoice
     has one URL per version, so links a client stored break when v1 ends.
2. **The version in a request header** (`Accept-Version: 2`), one URL per invoice.
   - Pros: an invoice keeps one URL. No second set of routes.
   - Cons: the version is missing from the gateway's access logs, which record the path only.
     A request without the header needs a default version, and changing that default later
     breaks whoever relied on it. The mobile app's HTTP cache keys on the URL alone.
   - Why it lost: the team could not count v1 callers, which is the number the end of v1
     depends on.
3. **No versions; only additive changes.** Add `amount_minor` and `currency` next to `amount`
   and keep `amount` for good.
   - Pros: nothing to run twice, and no client has to move.
   - Cons: `amount` keeps its rounding error for every client, for good. The next breaking
     change, already proposed in PROJ-118, faces the same choice again.
   - Why it lost: it keeps a wrong field in the public contract with no way to remove it.
<!-- With no DACI page, the record is the one home for the options (decisions.md section 8,
     the Options considered field). -->

## Objections and answers

- John Smith, mobile team lead, 2026-03-04: old app versions keep calling the API for months
  after a release, and the app cannot force an update without losing users, so a fixed end
  date for v1 would break users who never chose to update.
  <!-- What the objection says, with its author's name, job title and date; nothing about the
       person (decisions.md section 10). -->
  Answer, Jane Doe, 2026-03-10: the proposal ended v1 12 months after v2 ships. This objection
  changed that: v1 now ends only when its calls are below 2% of the mobile app's calls for 30
  days in a row, and never earlier than 12 months after v2 ships. The mobile team sees the share
  on the gateway dashboard.
  <!-- The decider answers each objection in the record (decisions.md section 7). -->
```

## Why it is good

- **It was opened at Proposed and accepted by one named decider**, the one
  [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5 names for this
  kind of choice and the Approver on the DACI page, with the date of each status
  ([decisions.md](decisions.md) section 8). Nobody has to guess whether the API is versioned yet,
  or who said so.
- **The comment window has its dates and closes on a recorded disposition**: postponed on its end
  date to answer the objection, so the objection came in before the decision and not after it
  (section 6).
- **The options live in one place.** The record links the DACI page and copies none of it, so the
  two never drift apart ([roles-and-decisions.md](../project-management/roles-and-decisions.md)
  section 6). The variant without DACI holds three real options, each with its cons and why it
  lost: a reader a year from now who wants header versioning finds the reason it lost, the team
  could not count v1 callers. The record argues against its own choice too: four of its six
  consequences are bad ones (section 8).
- **The decision text says how the objection changed the decision**: the proposal's fixed 12
  months became a measured share with a 12-month floor (section 4). In the variant, the objection
  is in the record with the decider's answer, and the record says what John Smith objected to, and
  his name, job title and date, and nothing about him (sections 7 and 10).
- **Confidence and Revisit when are written before the outcome**, so a review can tell a bad
  decision from bad luck, and starts when a trigger fires instead of when someone is unhappy
  (sections 8 and 9).
- **Confirmation names a check that runs in CI and the outcome the team expects**, so "did it
  work?" has an answer that does not depend on memory (section 8).
- **The agent's draft is named, and so is the person who checked it** ([agents.md](agents.md)
  section 7).
- **The review left a dated note and did not touch the decision text**, so a reader sees what
  governed the work and that it was checked when the first trigger fired (sections 8 and 9).

## Where each part comes from

| Part of the record | Listed by |
|---|---|
| Title, Status, Context, Decision, Consequences | Nygard [1] |
| Status names | Nygard [1], MADR [2], Fowler [3], AWS [4] |
| The date of each status change | this practice's choice ([decisions.md](decisions.md) section 8); AWS adds a timestamp at acceptance [4], MADR keeps the date of the last update [2] |
| Decider | MADR's nearest field, "decision-makers", which lists "everyone involved in the decision" [2]; one person, as [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5 says |
| Comment window and its end date | this practice's rule ([decisions.md](decisions.md) section 6) |
| Drafted by, accepted by | this practice's choice ([agents.md](agents.md) section 7) |
| Options considered, with pros, cons and why each lost (the variant without DACI) | Fowler [3], MADR [2], Azure [5]; at least two options, Zimmermann [6] |
| Decision: what the proposal had and what the objection changed | this practice's rule ([decisions.md](decisions.md) section 4) |
| Bad consequences listed next to the good ones | Nygard [1] |
| Objections and answers (the variant without DACI) | this practice's rule ([decisions.md](decisions.md) section 7); the author's name, job title and date of a recorded opinion, the ICO [7] |
| Confidence | Fowler [3], Azure [5] |
| Revisit when | Fowler [3] |
| Confirmation: the check | MADR [2] |
| Confirmation: the expected outcome | this practice's own addition, after Farnam Street's decision journal [8] |
| Links | [roles-and-decisions.md](../project-management/roles-and-decisions.md) sections 6 and 7; the dated work item or alert with an owner on a postponement or a trigger tied to a date or a number, this practice's rule ([decisions.md](decisions.md) section 9) |
| Notes, dated, with the decision text never edited | Azure [5], AWS [4], Fowler [3]; the dated note is this practice's choice ([decisions.md](decisions.md) sections 8 and 9) |
| The options on the DACI page, linked from the record | the DACI play [9]; which record holds the options is [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 6's rule |

## Sources

Checked 2026-10-30 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Michael Nygard — Documenting Architecture Decisions (Cognitect blog, 2011; opinion) — https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions — checked 2026-10-29
- [2] MADR project — Markdown Architectural Decision Records template, 4.0.0 — https://raw.githubusercontent.com/adr/madr/4.0.0/template/adr-template.md
- [3] Martin Fowler — Architecture Decision Record (martinfowler.com bliki, 2026; opinion) — https://martinfowler.com/bliki/ArchitectureDecisionRecord.html — checked 2026-10-29
- [4] Amazon Web Services — AWS Prescriptive Guidance: Architectural decision record process — https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html — checked 2026-10-29
- [5] Microsoft — Azure Well-Architected Framework: Maintain an architecture decision record (ADR) — https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record — checked 2026-10-29
- [6] Olaf Zimmermann — A Definition of Done for Architectural Decision Making (ozimmer.ch, 2020; opinion) — https://ozimmer.ch/practices/2020/05/22/ADDefinitionOfDone.html — checked 2026-10-29
- [7] Information Commissioner's Office — UK GDPR guidance: Principle (c): Data minimisation — https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/ — checked 2026-10-29
- [8] Shane Parrish — How a Decision Journal Changed the Way I make Decisions (Farnam Street, no date; opinion) — https://fs.blog/decision-journal/ — checked 2026-10-29
- [9] Atlassian — Team Playbook: DACI, a decision-making framework — https://www.atlassian.com/team-playbook/plays/daci
