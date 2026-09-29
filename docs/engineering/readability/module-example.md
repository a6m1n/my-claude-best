# Example: one module, written to every principle

A worked example for [readability.md](readability.md). A billing service sends a reminder for an
overdue invoice, at most once a week. The module is small on purpose: every principle shows in a
few lines, and each part says which principles it follows and why. Names are invented. The module
sits in the tree of [file-structure.md](../file-structure/file-structure.md), and the business
`if` sits where [python.md](../python/python.md) section 2 puts it.

```text
src/shop/
├── core/
│   ├── database.py                 Database: the one way to reach the database
│   └── mail_client.py              Mailer: every call to the email provider
├── billing/
│   └── remind_overdue_invoice/
│       ├── schemas.py              Invoice, InvoiceId, ReminderResult: types only
│       ├── reminder_rules.py       needs_reminder, and the interval it reads
│       ├── reminder_format.py      render_reminder: the email body
│       ├── repository.py           get_invoice, mark_invoice_reminded: one function per query
│       └── usecase.py              remind_overdue_invoice: the flow
└── cli/
    ├── main.py                     builds Database and Mailer once
    └── commands_remind_overdue_invoice.py
tests/
├── unit/remind_overdue_invoice/
│   └── test_reminder_rules.py
└── integration/remind_overdue_invoice/
    └── test_usecase.py
```

`schemas.py`, `reminder_format.py`, `repository.py`, `core/database.py`, `core/mail_client.py`,
the adapter and the integration test are not shown. `schemas.py` holds a frozen `Invoice` with
`invoice_id`, `customer_email`, `amount`, `due_on` and `last_reminded_on: date | None`, the id
type `InvoiceId = NewType("InvoiceId", str)`, and a `ReminderResult` enum with `SENT` and
`NOT_NEEDED`. The adapter reads the clock once, `today = date.today()`, and passes it in with the
two objects `cli/main.py` built at startup.

## The rule

`src/shop/billing/remind_overdue_invoice/reminder_rules.py`

```python
from datetime import date, timedelta
from typing import Final

# One reminder a week: a daily email for the same invoice made customers
# unsubscribe instead of paying.
REMINDER_INTERVAL: Final = timedelta(days=7)


def needs_reminder(due_on: date, last_reminded_on: date | None, today: date) -> bool:
    if today <= due_on:
        return False

    if last_reminded_on is None:
        return True

    return today - last_reminded_on >= REMINDER_INTERVAL
```

Why it is good:

- **Every input is in the signature** (section 6). `today` comes in like the two dates, so the
  answer depends on the three arguments alone, and a test passes three dates.
- **The comment gives the reason for the value** (section 4), the one thing the line cannot say.
  Without it, the next editor may shorten the interval to "remind more".
- **The name is the business question** (section 7), and the two guards end the function at the
  top (section 3), each followed by a blank line (section 5).

## The flow

`src/shop/billing/remind_overdue_invoice/usecase.py`

```python
from datetime import date

from shop.billing.remind_overdue_invoice.reminder_format import render_reminder
from shop.billing.remind_overdue_invoice.reminder_rules import needs_reminder
from shop.billing.remind_overdue_invoice.repository import (
    get_invoice,
    mark_invoice_reminded,
)
from shop.billing.remind_overdue_invoice.schemas import InvoiceId, ReminderResult
from shop.core.database import Database
from shop.core.mail_client import Mailer


def remind_overdue_invoice(
    invoice_id: InvoiceId,
    today: date,
    db: Database,
    mailer: Mailer,
) -> ReminderResult:
    invoice = get_invoice(db, invoice_id)

    if not needs_reminder(invoice.due_on, invoice.last_reminded_on, today):
        return ReminderResult.NOT_NEEDED

    mailer.send(
        invoice.customer_email,
        subject="Your invoice is overdue",
        body=render_reminder(invoice),
    )

    mark_invoice_reminded(db, invoice_id, today)

    return ReminderResult.SENT
```

Why it is good:

- **One job, one level of detail** (section 2). The body is four steps: load, decide, send,
  record. The email body lives in `render_reminder`, and the rule in `needs_reminder`.
- **The `NOT_NEEDED` branch is the business decision** ([python.md](../python/python.md) section 2).
  It asks a named rule and returns the value that names the path. It has the flat shape of a
  guard, but it is not one.
- **The stages show before a word is read** (section 5).
- **Everything it touches is in the signature** (section 6): the clock's value and two objects it
  receives and never builds.

## The test

`tests/unit/remind_overdue_invoice/test_reminder_rules.py`

```python
from datetime import date

from shop.billing.remind_overdue_invoice.reminder_rules import (
    REMINDER_INTERVAL,
    needs_reminder,
)


def test_invoice_not_past_its_due_date_needs_no_reminder() -> None:
    due_on = date(2026, 9, 1)

    assert not needs_reminder(due_on, last_reminded_on=None, today=due_on)


def test_reminder_repeats_once_the_interval_has_passed() -> None:
    due_on = date(2026, 9, 1)
    last_reminded_on = date(2026, 9, 10)
    today = last_reminded_on + REMINDER_INTERVAL

    assert needs_reminder(due_on, last_reminded_on, today)
```

The flow, the use case run with a test database and `create_autospec(Mailer, instance=True)`, is
covered by `tests/integration/remind_overdue_invoice/test_usecase.py`, not shown: many fast unit
tests for the rule and a few integration tests for the flow, which is Gary Bernhardt's split that
section 6 cites.

Why it is good:

- **No patch, no clock, no network for the rule** (section 6). The tests pass plain dates, and the
  rule answers from them alone.
- **Each test's name says the behavior it pins** (section 7).
- **Arrange is one stage, and the assert holds the act** (section 5): the rule only returns the
  value the assert checks, so one blank line splits the setup from the check.
