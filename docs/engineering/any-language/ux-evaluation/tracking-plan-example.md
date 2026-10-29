# Example: a tracking plan for the invoices screen

A worked example for [behaviour-analytics.md](behaviour-analytics.md). The billing application of
Acme Corp, an invented company, has the invoices screen that
[design-brief-example.md](../../react/design/design-brief-example.md) designs: an accounts clerk
opens `/invoices` to see which invoices are due or overdue, follows a Pay link, and pays on the pay
screen. This is the tracking plan the team keeps for that flow, shown part by part with the reason
next to each part. Every name, date and decision in it is invented.

The plan is `docs/tracking-plan.md` in the application's repository, in the `docs/` folder that
[file-structure.md](../file-structure/file-structure.md) section 9 gives the repository's documents,
so the pull request that adds an event changes the plan in the same diff
([behaviour-analytics.md](behaviour-analytics.md) section 3). The client that sends its events is
the one in [behaviour-analytics.md](behaviour-analytics.md) section 8.

## 1. The head of the plan

The file's title is `Tracking plan: Acme Billing`. Under it:

| Field | Value |
|---|---|
| Owner | Jane Doe, the billing team's product analyst. She and the engineer who sends an event review every change to it |
| Tool | PostHog, through `src/core/analytics.ts` only. Nothing else in the application sends analytics |
| Names | an event is an object and a past-tense action in Title Case: `Invoice Payment Started`. A property is in snake_case: `invoice_status`. The tool's own events keep its names: `$pageview` |
| Consent | every event waits for the clerk's consent, and the analytics client starts the SDK only then. Decided on 2026-10-12 by John Smith, Acme Corp's data protection officer: consent first for every event, no cookieless pings or cookieless events, no session replay. Why: the EDPB puts the SDK's sending in scope of Art. 5(3), and no exemption is claimed |
| Screens that send nothing | the pay screen, `/invoices/$invoiceId/pay`, a payment screen. Its route carries `isPaymentOrLogin: true` |
| Version | 3, of 2026-10-20 (section 6) |

Why it is good:

- **One owner, and a second reviewer for each change,** so every event has a person who answers
  for it (behaviour-analytics.md section 3, the Owner field).
- **The case is written at the top,** so the next author does not pick another one
  (behaviour-analytics.md section 3).
- **The consent decision says who made it, when, what it covers and why,** and it settles the open
  legal point of behaviour-analytics.md section 5 the strict way: no cookieless pings or events.
- **The pay screen is named as sending nothing,** the rule of
  [security.md](../../react/security/security.md) section 12 in this product's words, and the row
  names the route mark the router reads (behaviour-analytics.md section 8).

## 2. The questions

| Id | Question | Metric it feeds | Answered by |
|---|---|---|---|
| Q1 | Do clerks who open the invoices list go on to start a payment? | the share of visits with a page view of `/invoices` that also hold an `Invoice Payment Started` | `$pageview`, `Invoice Payment Started` |
| Q2 | Do clerks pay overdue invoices first? | of the visits that start a payment on both an overdue and a due invoice, the share whose first started payment was on the overdue one, against the share a random order of the same payments would give | `Invoice Payment Started` with `invoice_status`, in its order within the visit (`$session_id`) |
| Q3 | Do the payments clerks submit go through? | the share of submitted payments that succeed, by failure code | the API's payment records, not analytics |

Why it is good:

- **The questions come before the events, and every event names the questions it answers**
  (behaviour-analytics.md section 3), so an event with no question has nowhere to go.
- **Each question feeds one metric,** the goals, signals and metrics step of
  [evaluation.md](evaluation.md) section 8.
- **Q3 is answered from the API's records, not from analytics.** The server records every payment;
  a browser event would miss every clerk who did not agree, and the pay screen sends nothing
  (behaviour-analytics.md sections 1 and 5).
- **No question asks why,** because analytics cannot answer it (behaviour-analytics.md section 2).
  Why clerks stop before paying goes to the next round of tests with users
  ([evaluation.md](evaluation.md) section 4).

## 3. The events

| Event | Fires when | Sent from | Properties | Consent | Owner | Questions |
|---|---|---|---|---|---|---|
| `$pageview`, the tool's own | the router resolves a navigation that changed the path, and once when the clerk agrees, for the screen on show; never on the pay screen. Both go through one check, `countScreenOnShow()` in `src/main.tsx` | the browser | the tool's own (section 4) | consent first, the decision of 2026-10-12 | the product analyst | Q1 |
| `Invoice Payment Started` | the clerk follows a Pay link on the invoices screen: the link's click handler in `src/routes/invoices.index.tsx`, through `analytics.invoicePaymentStarted()` | the browser | `invoice_status` | consent first, the decision of 2026-10-12 | the product analyst | Q1, Q2 |

Why it is good:

- **Two questions for analytics, two events.** Nothing is sent that no question needs.
- **The name is an object and a past-tense action, with no value in it:** one `Invoice Payment
  Started` with a status property, not `Overdue Invoice Payment Started` and its twin
  (behaviour-analytics.md section 3).
- **The page view is counted through one check in `src/main.tsx`,** and the row names it, so a
  reviewer can see there is no second source and no page view from the pay screen
  (behaviour-analytics.md sections 4 and 8).
- **The started payment fires on the invoices screen, not on the pay screen,** so the payment
  screen still sends nothing ([security.md](../../react/security/security.md) section 12).
- **Each row names the file that sends the event,** so a reader goes from the plan to the code and
  back.
- **Each row names its consent decision and its owner,** the two fields behaviour-analytics.md
  section 3 asks for on every event.

## 4. The properties

| Property | On events | Type | Values | Required | Set by |
|---|---|---|---|---|---|
| `invoice_status` | `Invoice Payment Started` | text, a closed list | `due`, `overdue` | yes | the route, from `invoiceStatus` in `src/billing/list-invoices/invoice-status.rules.ts`, the rule the list's status badge reads |
| `$pathname`, `$host` | every event | text | the path, such as `/invoices`, and the host | yes | the tool |
| `$current_url`, and the address the session started on: `$session_entry_url`, `$session_entry_host`, `$session_entry_pathname` | every event | text | origin and path only: `before_send` in `src/core/analytics.ts` cuts the query string and the hash, and `advanced_disable_flags` there stops the flags request, which would carry the first page's full address past `before_send`. The `$initial_` copies go only with an identified person, and this plan identifies nobody (section 5) | yes | the tool |
| the tool's ids: `distinct_id`, `$device_id`, `$session_id`, `$window_id` | every event | text | random ids the SDK makes: one per browser (`distinct_id` and `$device_id`, kept in its cookie and local storage), one per visit and one per browser tab. The client keeps them, since Q1 and Q2 join a visit's events; no `identify` call ties them to a clerk (section 5) | yes | the tool |
| the page's title and where the clerk came from: `title`; `$referrer`, `$referring_domain` and their `$session_entry_` copies; `$search_engine` and `ph_keyword`, and their `$session_entry_` copies | `title` on `$pageview`, the rest on every event | text | each route's title names the screen, never a customer or an invoice, and is sent as it is; the referring address reaches the tool as origin and path, through `before_send`; when the clerk came from a search engine, the SDK adds its name and the search words, and the client drops the words with `property_denylist` | yes; the search ones only after a search | the tool |
| the screen before: `$pageview_id`, `$prev_pageview_id`, `$prev_pageview_pathname`, `$prev_pageview_duration` | `$pageview_id` on every event, the rest on `$pageview` | text, number | the id of the screen's page view, and the previous screen's id, path and seconds on screen. `disable_scroll_properties` turns off only the previous screen's scroll depth (section 5) | yes | the tool |
| the tool's device and library properties | every event | various | browser, operating system, device type, screen and viewport size, time zone, `$raw_user_agent`, `$browser_language`, `$lib` and its version, and the SDK's own bookkeeping, such as `token`, `$insert_id`, `$time` and `$initialization_time` | yes | the tool; the cost behaviour-analytics.md section 8 names for a vendor's SDK |
| campaign values in the session's entry properties: `$session_entry_utm_*`, `$session_entry_gad_source`, `$session_entry_mc_cid`, and an ad click id such as `$session_entry_gclid` or `$session_entry_fbclid` | every event of a visit whose first address held them | text | `save_campaign_params: false` keeps the plain `utm_*` and click-id properties off each event, but these copies still leave, rebuilt from the address the visit started on. `mask_personal_data_properties` turns each ad click id's value into `<masked>`; the `utm_*`, `gad_source` and `mc_cid` values leave as they are | no | the tool; behaviour-analytics.md section 8 |

Why it is good:

- **The status has a closed list, taken from the rule the screen already uses,** so the event and
  the status badge cannot disagree. `paid` is not on the list, since a paid invoice has no Pay link
  (design-brief-example.md, step 2 of the brief), and the client's type refuses it
  (behaviour-analytics.md section 8).
- **The plan lists what the team sends and each group the tool adds,** with what the client does
  about each; the release check in behaviour-analytics.md section 3 confirms the list on a real
  event.
- **Every URL reaches the tool as its origin and path,** and the row names the function that does it
  ([security.md](../../react/security/security.md) section 13; the origin is a departure from its
  path-only rule, declared at the `before_send` line).

## 5. Not collected, and why

| Not collected | Why |
|---|---|
| the customer's name, the amount, the invoice's id | no question needs them, and the customer's name is personal data of someone outside the application |
| who the clerk is: no `identify` call | the questions are about the screen, not about one clerk (behaviour-analytics.md section 3) |
| any event or page view from the pay screen | it is a payment screen ([security.md](../../react/security/security.md) section 12) |
| the outcome of a payment | the API's records answer Q3 (section 2) |
| autocapture, heatmaps, rage and dead clicks | no question needs them, and a click pattern would be a lead to check, not an answer (behaviour-analytics.md section 6) |
| scroll depth per screen | no question needs it; the client turns it off with `disable_scroll_properties` (behaviour-analytics.md section 8) |
| the search words a clerk typed into a search engine (`ph_keyword`) | typed text (behaviour-analytics.md section 3); the client drops them |
| session replay | no question needs it and nobody is set to watch it (behaviour-analytics.md section 6); the consent decision leaves it out |
| `Customer Link Opened` | proposed on 2026-10-15 and refused: no question needs it |

Why it is good:

- **What the plan leaves out is written down with its reason,** so nobody adds it back "while we
  are here" without the reason in front of them, and a refused event stays refused.
- **The collectors a tool turns on by default are named as off,** which the client sets in code
  (behaviour-analytics.md section 8).

## 6. How the plan changes

- A pull request that adds, renames or removes an event changes this file in the same diff, and
  Jane Doe reviews it (behaviour-analytics.md section 3).
- A new event names its question first. A question with no metric gets no event.
- A live event keeps its name. A new name is a new event, and the old one is retired in the same
  change, both in the log below (behaviour-analytics.md section 12).

| Version | Date | Change |
|---|---|---|
| 1 | 2026-10-12 | the plan, Q1, `$pageview`, and the consent decision |
| 2 | 2026-10-15 | `Customer Link Opened` refused (section 5) |
| 3 | 2026-10-20 | Q2 and Q3; `Invoice Payment Started` with `invoice_status` |

Why it is good:

- **A change to an event and a change to the plan arrive together,** so the plan cannot fall behind
  the code (behaviour-analytics.md section 3).
- **The log keeps the refused event and the reason for each version,** so a later reader sees why
  the plan is as it is.

## 7. What the example leaves out, and what was checked

The code the plan names is behaviour-analytics.md section 8's: the client with
`invoicePaymentStarted`, `countScreenOnShow` with the router subscription, and the pay route's
mark, type-checked as that section says. The Pay link's click handler in `src/routes/invoices.index.tsx` is not shown. The
plan was never run against a live tool, so no count in it has been seen, and the metrics' reports
are left out ([evaluation.md](evaluation.md) section 8). The tool's own properties in section 4
were read in the source of posthog-js 1.442.0 on 2026-10-29, not seen on a live event; the release check of
behaviour-analytics.md section 3 is where a team confirms them. The consent banner's words are
left out, since how a banner should word its choice is not covered yet (behaviour-analytics.md
section 1).
