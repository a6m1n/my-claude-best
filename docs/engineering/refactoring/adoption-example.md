# Example: four practice changes in one repository

A worked example for [refactoring.md](refactoring.md). Acme Corp runs `billing`, a Python service
of about 40,000 lines with a test suite and mypy in CI. In one quarter its team takes on four
practice changes, and each one reaches the old code a different way. Names, tickets, dates and
numbers are invented.

**Navigation**

- [1. A formatter: one sweep](#1-a-formatter-one-sweep)
- [2. Named types instead of `dict`: step by step](#2-named-types-instead-of-dict-step-by-step)
- [3. A new HTTP client: a migration](#3-a-new-http-client-a-migration)
- [4. A module layout: split a file when a change touches it](#4-a-module-layout-split-a-file-when-a-change-touches-it)
- [What the four have in common](#what-the-four-have-in-common)

| Practice change | Kind (section 7) | How old code gets there |
|---|---|---|
| Format all code with `ruff format` | New and touched code, swept by a tool | One sweep commit, then a CI check |
| Pass named types instead of `dict` | New and touched code | Step by step, as changes touch it |
| Replace `requests` with `httpx` | Migration | Owner, count, end date |
| Lay code out by [file-structure.md](../file-structure/file-structure.md) | New and touched code | Step by step: a file splits when a change touches it |

## 1. A formatter: one sweep

**The change.** The team adopts `ruff format` for all Python code.

**Why a sweep.** All four conditions of section 4 hold. A tool makes every edit. The formatter
does not change behavior, and the tests and mypy pass on the result. The edit can land as one
commit with nothing else in it. A CI check can stop the old layout from coming back. Formatting
only on touch would put layout noise into every feature diff for years.

**What lands.** One pull request with three commits. The first holds only the formatter's output:

```
chore(billing): format all Python code with ruff

- Every file now has the layout ruff format gives it, so review
  diffs show real changes instead of layout noise.
- The commit holds formatter output only, so .git-blame-ignore-revs
  can list it and git blame can skip it.
```

The second hides the sweep from `git blame`:

```
chore(git): skip the format commit in git blame

- .git-blame-ignore-revs lists the format commit, so git blame shows
  the last real change to each line.
```

The third turns the check on:

```
chore(ci): check formatting with ruff

- CI runs ruff format --check and fails on unformatted code, so the
  old layout cannot come back.
```

`.git-blame-ignore-revs` at the repository root:

```
# chore(billing): format all Python code with ruff
3f9c2a7d1e5b8a0c4f6e2d9b7a1c3e5f7a9b0c2d
```

Each developer runs `git config blame.ignoreRevsFile .git-blame-ignore-revs` once.

## 2. Named types instead of `dict`: step by step

**The change.** The team adopts [python.md](../python/python.md) section 2, "A rule about a value
is written in the type, where the value enters": an order that has been paid is a `PaidOrder`,
built once where the webhook's data arrives, instead of a `dict` that every function checks again.

**Why step by step.** Each fix needs judgment: which fields the type has, where the edge is, which
checks become redundant. No tool can make these edits, so section 4's first condition fails.

**The setup.** New code uses the types from day one. No tool flags a `dict` where a named type
belongs, so there are no marks to count; review reads new code for an `order: dict`, and the team
counts the old form with a search:

```
grep -rn "order: dict" src/ | wc -l
```

It prints 12 today. The team writes the command and the number in the issue that tracks the
rule. Each author runs the command before staging a change in that area, and the number may only
go down.

**A change that touches old code.** Ticket PROJ-123 adds partial refunds. It has to edit
`refund()` in `src/billing/refund.py`, which takes an order as a `dict` and has no tests. Before
the first edit, the developer lists the functions the change will edit: `refund()` and the
webhook line that calls it. The pull request carries three commits, in this order:

```
test [PROJ-123]: pin current refund behavior

- Characterization tests call refund() with the three order shapes
  seen in production and assert today's gateway calls, so the
  refactoring that follows cannot change them unnoticed.
```

```
refactor [PROJ-123]: take a PaidOrder in refund()

- refund() takes the PaidOrder built at the webhook instead of a
  dict, so mypy checks every field refund() reads.
- The count of order: dict drops by one, to 11; the characterization
  tests for refund() pass with the same expected gateway calls.
```

```
feat [PROJ-123]: refund part of an order

- A support agent can refund an amount below the order total; the
  rest of the payment stays captured.
```

The `refactor` commit changes how the tests build their input, from a `dict` to a `PaidOrder`, but
no expected value. That is what makes it a refactoring (section 3, rule 4).

**What stays.** `src/billing/reporting/daily.py` also reads orders as a `dict`, and PROJ-123
does not touch it. It stays as it is. The pull request names it as a follow-up and links
PROJ-130, which has an owner. The `order: dict` count drops from 12 to 11.

## 3. A new HTTP client: a migration

**The change.** The team replaces `requests` with `httpx`, to get one client for sync and async
code and one place to set timeouts.

**Why a migration.** This change replaces one way with another. Two clients side by side mean two
ways to set timeouts and retries, and new code would copy whichever one it saw first. Moving code
only on touch would never finish. Jane Doe changed the practice, so she owns the migration.

**The practice change** is one commit, and its body says how existing code responds (section 7):

```
docs [PROJ-140]: use httpx for outgoing HTTP calls

- New code calls external services through httpx, which gives sync
  and async code one client and one place to set timeouts.
- Migration: owner Jane Doe, end 2026-12-18, tracked in PROJ-140.
  Count: grep -rn "import requests" src/ | wc -l, 31 today.
```

**The tracking issue**, PROJ-140, records the count before each step:

```
Migrate from requests to httpx

Owner: Jane Doe
End date: 2026-12-18
Count: grep -rn "import requests" src/ | wc -l

| Date       | Count | What happened                               |
|------------|-------|---------------------------------------------|
| 2026-10-05 | 31    | practice changed; new code uses httpx only  |
| 2026-10-26 | 18    | codemod moved plain get and post calls      |
| 2026-11-30 | 4     | retry and session code moved by hand        |
| 2026-12-14 | 0     | requests removed from pyproject.toml        |
```

**How it went.**

1. **Stop the bleeding.** From the first day, each author ran the count before staging, and
   review rejected any change that raised it.
2. **The easy majority.** A LibCST codemod rewrote plain `requests.get` and `requests.post`
   calls. mypy and the tests covered every file it edited, and a grep for `requests.` found no use
   left in the files it changed, so it landed as one commit, listed in `.git-blame-ignore-revs`.
3. **The tail.** Retries and sessions needed a decision at each place, so Jane moved them by hand,
   one module per pull request, with characterization tests first where they were missing.
4. **The contract step.** The last pull request removed `requests` from `pyproject.toml` and the
   lockfile, and deleted the wrapper file that had held both clients. The count is zero, and
   PROJ-140 is closed.

**Why not a sweep on day one.** Retry and session code needed a decision at each place, so a tool
could not make every edit. **Why not on touch alone.** Eleven of the 31 imports sat in code nobody
had changed for a year. On touch alone they would still be there.

## 4. A module layout: split a file when a change touches it

**The change.** The team adopts [file-structure.md](../file-structure/file-structure.md):
adapters, then modules, then `core/`, one file per role. New code follows it from day one.

**Why step by step.** Each split needs judgment: which role each part plays, and where each
constant goes. So section 4's first condition fails, and a move is checked three ways (section 10).

**The setup.** The team counts the files outside the HTTP adapter that import the web framework
([file-structure.md](../file-structure/file-structure.md) section 2):

```bash
grep -rlE "^(from|import) fastapi" src/billing --include="*.py" | grep -v "^src/billing/api/" | wc -l
```

It prints 9. The command and the number go in the issue that tracks the rule, and the number only
goes down. There are no marks to count: the old top-level files sit in no layer of the import
contracts ([file-structure.md](../file-structure/file-structure.md) section 11), so no tool checks
them, and a search counts the ones that import the web framework instead
([refactoring.md](refactoring.md) section 4).

**A change that touches old code.** Ticket PROJ-160 asks to show up to 100 open invoices instead
of 50. The limit sits in `src/billing/invoices.py`.

**Before: a constant, a query, a route and its handler in one file**

```python
from fastapi import APIRouter, Request

from billing.core.database import Database
from billing.core.schemas import InvoiceRow

MAX_OPEN_INVOICES = 50
OPEN_INVOICES_SQL = """
    SELECT id, number, total, due_date FROM invoices
    WHERE customer_id = :customer_id AND paid_at IS NULL
    ORDER BY due_date LIMIT :limit
"""

router = APIRouter()


@router.get("/customers/{customer_id}/invoices/open")
def get_open_invoices(customer_id: str, request: Request) -> list[InvoiceRow]:
    db: Database = request.app.state.database
    rows = db.fetch_all(
        OPEN_INVOICES_SQL, customer_id=customer_id, limit=MAX_OPEN_INVOICES
    )

    return [InvoiceRow(**row) for row in rows]
```

- To change the limit, a reader loads the query, the route and the handler with it
  ([file-structure.md](../file-structure/file-structure.md) section 3).
- The query and the limit sit in the route's file, so a CLI that imports them to list open
  invoices imports FastAPI too ([file-structure.md](../file-structure/file-structure.md)
  section 2).
- The name does not say which of the four things the file holds
  ([file-structure.md](../file-structure/file-structure.md) sections 3 and 7).

**What lands.** Two pull requests, both for PROJ-160. The split is a larger refactoring, so it is
its own pull request and merges first (section 3, rule 7). It starts with a `test` commit that
pins today's rows and the limit of 50, as in case 2, then splits the file:

```text
refactor [PROJ-160]: split open-invoice code by role

- The route and its handler move to the HTTP adapter, the query to
  the repository and the limit to the constants, both in a new
  list_open_invoices module, and its use case hands the limit to the
  query, so each part changes alone.
- The characterization tests pass with the same expected values, mypy
  passes, and a search for billing.invoices finds no use left.
```

The second pull request is the feature, and the test's expected limit changes in it:

```text
feat [PROJ-160]: show up to 100 open invoices

- A customer's open-invoices list shows up to 100 invoices instead of
  50, so the collections team sees more of a large customer's unpaid
  invoices at once.
```

**After.** Each file shown under `invoicing/` and `api/` names the part of the Before it now
holds.

```text
src/billing/
├── core/
│   ├── database.py                   Database, the class only: unchanged
│   ├── schemas.py                    InvoiceRow: unchanged; the old invoice files use it too
│   └── ...                           files not shown
├── invoicing/
│   └── list_open_invoices/
│       ├── consts.py                 MAX_OPEN_INVOICES: how many rows the module returns
│       ├── repository.py             fetch_open_invoices() and the SQL it runs
│       └── usecase.py                list_open_invoices(): reads the limit and calls the query
├── api/
│   ├── routes_list_open_invoices.py  the route and its handler: one call to list_open_invoices
│   └── ...                           files not shown
└── ...                               the old top-level files that stay
```

`src/billing/invoicing/list_open_invoices/usecase.py`

```python
from billing.core.database import Database
from billing.core.schemas import InvoiceRow
from billing.invoicing.list_open_invoices.consts import MAX_OPEN_INVOICES
from billing.invoicing.list_open_invoices.repository import fetch_open_invoices


def list_open_invoices(customer_id: str, db: Database) -> list[InvoiceRow]:
    return fetch_open_invoices(customer_id, db, limit=MAX_OPEN_INVOICES)
```

`src/billing/api/routes_list_open_invoices.py`

```python
from fastapi import APIRouter, Request

# ...
from billing.invoicing.list_open_invoices.usecase import list_open_invoices

router = APIRouter()


@router.get("/customers/{customer_id}/invoices/open")
def get_open_invoices(customer_id: str, request: Request) -> list[InvoiceRow]:
    db: Database = request.app.state.database

    return list_open_invoices(customer_id, db)
```

**What changed.**

- **The limit is one line in a file of named values**, which answers the first reason. The
  feature commit changes `MAX_OPEN_INVOICES` and no other line of application code. It sits in
  the module's `consts.py`, not next to the query, because it is how many rows the module
  returns, and the use case hands it to the query
  ([file-structure.md](../file-structure/file-structure.md) section 3).
- **The query and the limit left the route's file**, which answers the second. The use case
  imports no web framework, so a CLI calls `list_open_invoices` as it is
  ([file-structure.md](../file-structure/file-structure.md) section 2).
- **Each file holds one kind of thing, and its name says which**, which answers the third: a
  reader opens only the file a change needs
  ([file-structure.md](../file-structure/file-structure.md) sections 3 and 7).

**What stays.** The other eight files stay until a change touches them, and the count drops from
9 to 8.

## What the four have in common

Each change says which of the three answers in section 7 it takes. Each has a check anyone can
run: the formatter check in CI, the `order: dict` count, the count in the tracking issue, and the
count of files outside the HTTP adapter that import the web framework. None of them rewrote code
that no change had a reason to touch, except by a tool and a command that proved it.
