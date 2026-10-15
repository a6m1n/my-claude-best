Every value in this file is invented: the repository, the branches, the tickets, the commits, the
people, the logins and the numbers. It shows the shape of what the skill prints in each mode,
never real content, and not the only allowed answer: a real draft has the sections its change
needs.

# Worked example — what the skill prints, one case per mode

The lines in italics set the scene and are not part of the output. Everything else is what the
skill prints: the draft in one code block, then one line on what your yes will do, and, after the
yes, the result. Every case runs in a project with a binding (README, What to fill in) that names
the ticket key `PROJ-123`, the section `## Jira Ticket`, the URL template
`https://tracker.example.com/browse/<KEY>`, and the checks `make test`, `make lint` and
`npm run test`.

**Navigation**

- [CREATE — a branch with no pull request yet](#create--a-branch-with-no-pull-request-yet)
- [UPDATE — new commits on an open pull request](#update--new-commits-on-an-open-pull-request)
- [Stacked — two layers, created together](#stacked--two-layers-created-together)

## CREATE — a branch with no pull request yet

*Branch `feat/PROJ-482-partial-refunds`, three commits ahead of `main`, all by Jane Doe
<jane.doe@example.com>, the repository's local identity. No pull request exists. Every check the
draft lists under "Checked in this session" ran earlier in this session. The user types `/pr`.*

```markdown
feat [PROJ-482]: Let support agents refund part of an order

## Summary

Support could refund only a **whole order**, so a customer who sent back one item of five got a
manual bank transfer. This PR adds **partial refunds**: an agent picks the items and quantities,
and the money goes back to the original card through the payment provider. A refund **never
exceeds what is left to refund** on the order, and every refund is written to a new **refund
ledger**.

| | Before | After |
| --- | --- | --- |
| What can be refunded | the whole order | any items and quantities |
| Refunds per order | 1 | until the paid amount is used up |
| Where a refund is recorded | `orders.refunded_at` | `refunds` table, one row per refund |

## Jira Ticket

[PROJ-482](https://tracker.example.com/browse/PROJ-482)

## What's Changed

- **Partial refund endpoint.** `POST /orders/{id}/refunds` takes item ids and quantities,
  computes the amount from the prices the customer paid, and sends one refund to the payment
  provider. A request that would refund more than is left gets HTTP 409 with the remaining
  amount in the body, so the support screen can show it.
- **Refund ledger.** A new `refunds` table holds one row per refund: order, items, amount,
  provider reference and agent. The refundable amount of an order is now the paid amount minus
  the ledger's sum, in place of the single `refunded_at` flag. A migration turns each existing
  full refund into one ledger row.
- **Support screen.** The order page gets a "Refund items" dialog with a quantity per item and
  the remaining amount on top. The old "Refund order" button stays and now writes one ledger row
  for the whole remaining amount.

## Verification

*Checked in this session*

- `make test`: 412 passed, 0 failed, 18 of them new for the endpoint and the ledger.
- `make lint`: no findings.
- `npm run test` in `web/`: 96 passed.
- The migration on a copy of the staging data: 1,204 full refunds moved; the ledger sums match
  the old `refunded_at` totals.

*For the reviewer*

- Refund 2 of 5 items on a test order. Expected: one ledger row, and the remaining amount drops
  by the price of those 2 items.
- Try to refund more than is left. Expected: HTTP 409 with the remaining amount, and no call to
  the provider.
- Call the endpoint as a user without the support role. Expected: HTTP 403.
- Not run: the end-to-end suite against the provider's sandbox, which needs the sandbox key.

## Notes

- `orders.refunded_at` stays for one release and is no longer written. A follow-up removes it.

  > ⚠️ **Contract change:** the order response gains `refundable_amount` and `refunds[]`.
  > Nothing is removed, so existing callers keep working.

- Added `money` 2.3.0, which keeps amounts in minor units, so a refund of three items never
  rounds differently from the sum of their prices.

## Risks

- A provider timeout after the provider accepted a refund leaves no ledger row, and the agent
  could refund again. The provider's idempotency key is set, but no test covers the retry path.
- The migration assumes one currency per order. That holds for all current data and is not
  enforced.
```

Your yes pushes `feat/PROJ-482-partial-refunds` (3 commits) and runs `gh pr create --base main
--assignee "@me"`.

*The user answers "yes".*

Pushed `feat/PROJ-482-partial-refunds`. Pull request #57:
https://github.com/acme-corp/shop/pull/57 — assignees: `jane-doe`.

## UPDATE — new commits on an open pull request

*Branch `fix/PROJ-517-duplicate-emails` has open pull request #61, opened by `john-smith`, with
an empty Assignees field. Two commits by John Smith <john.smith@example.com>, the repository's
local identity, are not pushed yet. A teammate added a "Deploy checklist" section to the
description. Every check the draft lists under "Checked in this session" ran earlier in this
session. The user says "update the PR".*

What changed against the current description: What's Changed gains the retry fix and the renamed
setting from the two new commits, Summary now covers both causes, Verification lists the new
tests, the new ⚠️ Breaking Changes section names the renamed setting, and the teammate's "Deploy
checklist" section stays word for word. The title stays: the scope is the same.

```markdown
fix [PROJ-517]: Send each order confirmation email once

## Summary

About **1 in 200 customers got two confirmation emails** for one order. There were two causes:
the checkout called the mail job twice when the payment page reloaded, and the mail worker
retried a send that had already **reached the mail provider** but timed out on the way back.
This PR makes the mail job **idempotent per order** and lets the worker retry only sends the
provider never accepted.

## Jira Ticket

[PROJ-517](https://tracker.example.com/browse/PROJ-517)

## What's Changed

- **One mail job per order.** The checkout now creates the confirmation job with the order id as
  its key, so a second call for the same order finds the existing job and stops. This removes
  the duplicates that came from a reloaded payment page.
- **Retry only what the provider did not accept.** The mail worker now sends a message id with
  each email and, after a timeout, asks the provider whether that id arrived before it retries.
  A send the provider already has is marked done, not sent again.
- **Retry setting renamed.** The mail worker's `MAIL_RETRIES` setting is now `MAIL_MAX_RETRIES`,
  because it is an upper limit on retries, not a fixed count. The default stays 3.

## Verification

*Checked in this session*

- `make test`: 398 passed, 0 failed, 9 of them new for the job key and the retry check.
- A replay of 2,000 checkout logs from last week against a local mail stub: 0 duplicate sends,
  against 11 before the change.

*For the reviewer*

- Reload the payment page twice during checkout on staging. Expected: one confirmation email.
- Stop the mail stub after it accepts a message and before it answers. Expected: the worker asks
  for the message id, finds it, and does not send again.

## ⚠️ Breaking Changes

- **`MAIL_RETRIES` is now `MAIL_MAX_RETRIES`.** What breaks: a deploy that still sets
  `MAIL_RETRIES` gets the default of 3 retries, without an error. Blast radius: the mail worker
  in every environment. Migration: rename the variable in each environment's settings before
  this deploy.

## Risks

- The provider's "does this id exist" call has a rate limit of 10 per second. A burst of
  timeouts above that rate waits instead of retrying, and the tests do not cover it.

## Deploy checklist

- [ ] Rename `MAIL_RETRIES` to `MAIL_MAX_RETRIES` in staging and production.
- [ ] Watch the mail queue for 30 minutes after the deploy.
```

Your yes pushes the 2 new commits and runs `gh pr edit 61` with the new description. The
Assignees field is empty: your yes also adds `john-smith`, who opened the pull request, in the
same call.

*The user answers "yes".*

Pushed 2 commits to `fix/PROJ-517-duplicate-emails`. Pull request #61 updated:
https://github.com/acme-corp/shop/pull/61 — assignees: `john-smith`.

## Stacked — two layers, created together

*Branch `feat/PROJ-530-export-api` is cut from `main`, and branch `feat/PROJ-531-export-screen`
is cut from it. Neither has a pull request. All commits are by Jane Doe <jane.doe@example.com>,
the repository's local identity. Every check the draft lists under "Checked in this session" ran
earlier in this session. The user says "stack these: the API first, the screen on top".
`gh extension list` shows `gh-stack`.*

Layer 1 of 2 — branch `feat/PROJ-530-export-api`, base `main`:

```markdown
feat [PROJ-530]: Export the order list as a CSV file

## Summary

Finance copies the order list into a spreadsheet by hand every month. This PR adds a **CSV
export endpoint** for the order list, with the **same filters** as the list itself, so finance
can download exactly what they see.

## Jira Ticket

[PROJ-530](https://tracker.example.com/browse/PROJ-530)

## What's Changed

- **CSV export endpoint.** `GET /orders/export.csv` takes the list's filters (date range,
  status, country) and streams one row per order, so a year of orders does not load into memory
  at once. Amounts use a dot as the decimal mark and carry the currency in its own column.

## Verification

*Checked in this session*

- `make test`: 405 passed, 0 failed, 7 of them new for the endpoint.
- An export of 50,000 test orders: 50,000 rows, memory flat at about 60 MB.

*For the reviewer*

- Export one month with the status filter "paid". Expected: the same orders as the list shows
  with that filter.
- Call the endpoint without the finance role. Expected: HTTP 403.
```

Layer 2 of 2 — branch `feat/PROJ-531-export-screen`, base `feat/PROJ-530-export-api`:

```markdown
feat [PROJ-531]: Add an Export button to the order list

## Summary

The order list gets an **Export** button that downloads the CSV file of the endpoint in the
layer below, with the filters the user has set. This PR holds **the screen only**; the endpoint
is reviewed in its own layer.

## Jira Ticket

[PROJ-531](https://tracker.example.com/browse/PROJ-531)

## What's Changed

- **Export button.** The button sits next to the filters and calls `GET /orders/export.csv` with
  the current filters. While the file downloads, the button shows a spinner and cannot be
  pressed again.

## Verification

*Checked in this session*

- `npm run test` in `web/`: 101 passed, 0 failed, 5 of them new for the button.

*For the reviewer*

- Set a date range and press Export. Expected: a CSV file with the orders the list shows.
- Open the list as a user without the finance role. Expected: no Export button.
```

Your yes pushes both branches, runs `gh pr create --base main --assignee "@me"` for
`feat/PROJ-530-export-api`, then `gh pr create --base feat/PROJ-530-export-api --assignee
"@me"` for `feat/PROJ-531-export-screen`, and links the two new pull requests with
`gh stack link`, bottom first.

*The user answers "yes".*

Pushed both branches. Pull request #64 (base `main`) and pull request #65 (base
`feat/PROJ-530-export-api`), linked as one stack:
https://github.com/acme-corp/shop/pull/64 and https://github.com/acme-corp/shop/pull/65 —
assignees: `jane-doe` on both.
