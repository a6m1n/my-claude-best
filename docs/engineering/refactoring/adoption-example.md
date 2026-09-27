# Example: three practice changes in one repository

A worked example for [refactoring.md](refactoring.md). Acme Corp runs `billing`, a Python service
of about 40,000 lines with a test suite and mypy in CI. In one quarter its team takes on three
practice changes, and each one reaches the old code a different way. Names, tickets, dates and
numbers are invented.

| Practice change | Kind (section 7) | How old code gets there |
|---|---|---|
| Format all code with `ruff format` | New and touched code, swept by a tool | One sweep commit, then a CI check |
| Pass named types instead of `dict` | New and touched code | Step by step, as changes touch it |
| Replace `requests` with `httpx` | Migration | Owner, count, end date |

## 1. A formatter: one sweep

**The change.** The team adopts `ruff format` for all Python code.

**Why a sweep.** All four conditions of section 4 hold. A tool makes every edit. The formatter
does not change behavior, and the tests and mypy pass on the result. The edit can land as one
commit with nothing else in it. A CI check can stop the old layout from coming back. Formatting
only on touch would put layout noise into every feature diff for years.

**What lands.** One pull request with two commits. The first holds only the formatter's output:

```
chore: format all Python code with ruff

- Every file now has the layout ruff format gives it, so review
  diffs show real changes instead of layout noise.
- The commit holds formatter output only; the next commit lists it
  in .git-blame-ignore-revs.
```

The second turns the check on and hides the sweep from `git blame`:

```
chore: check formatting in CI

- CI runs ruff format --check and fails on unformatted code, so the
  old layout cannot come back.
- .git-blame-ignore-revs lists the format commit, so git blame shows
  the last real change to each line.
```

`.git-blame-ignore-revs` at the repository root:

```
# chore: format all Python code with ruff
3f9c2a7d1e5b8a0c4f6e2d9b7a1c3e5f7a9b0c2d
```

Each developer runs `git config blame.ignoreRevsFile .git-blame-ignore-revs` once.

## 2. Named types instead of `dict`: step by step

**The change.** The team adopts [python.md](../python/python.md) section 2: a value that crosses
modules is a named type, such as `PaidOrder` or `Money`, built once at the edge. It is no longer a
`dict` that every module checks again.

**Why step by step.** Each fix needs judgment: which fields the type has, where the edge is, which
checks become redundant. No tool can make these edits, so section 4's first condition fails.

**The setup.** New modules use the types from day one, and review checks new code against the
check in python.md section 2. No tool flags a `dict` where a named type belongs, so there are no
marks to count. The team counts the old form with a search instead:

```
grep -rn "order: dict" src/ | wc -l
```

It prints 12 today. The team writes the command and the number in the issue that tracks the
rule. Each author runs the command before staging a change in that area, and the number may only
go down.

**A change that touches old code.** Ticket PROJ-123 adds partial refunds. It has to edit
`refund()` in `billing/refund.py`, which takes an order as a `dict` and has no tests. Before the
first edit, the developer lists the functions the change will edit: `refund()` and the webhook
line that calls it. The pull request carries three commits, in this order:

```
test(billing): pin current refund behavior

- Characterization tests call refund() with the three order shapes
  seen in production and assert today's gateway calls, so the
  refactoring that follows cannot change them unnoticed.
```

```
refactor(billing): take a PaidOrder in refund()

- refund() takes the PaidOrder built at the webhook instead of a
  dict, so the currency check it repeated is gone.
- The count of order: dict drops by one, to 11; the tests from the
  previous commit pass with the same expected gateway calls.
```

```
feat [PROJ-123]: refund part of an order

- A support agent can refund an amount below the order total; the
  rest of the payment stays captured.
```

The `refactor` commit changes how the tests build their input, from a `dict` to a `PaidOrder`, but
no expected value. That is what makes it a refactoring (section 3, rule 4).

**What stays.** `reporting/daily.py` also reads orders as a `dict`, and PROJ-123 does not touch
it. It stays as it is. The pull request names it as a follow-up and links PROJ-130, which has an
owner. The `order: dict` count drops from 12 to 11.

## 3. A new HTTP client: a migration

**The change.** The team replaces `requests` with `httpx`, to get one client for sync and async
code and one place to set timeouts.

**Why a migration.** This change replaces one way with another. Two clients side by side mean two
ways to set timeouts and retries, and new code would copy whichever one it saw first. Moving code
only on touch would never finish. Jane Doe changed the practice, so she owns the migration.

**The practice change** is one commit, and its body says how existing code responds (section 7):

```
docs(engineering): use httpx for outgoing HTTP calls

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
   lockfile, and deleted the adapter module that had wrapped both clients. The count is zero, and
   PROJ-140 is closed.

**Why not a sweep on day one.** Retry and session code needed a decision at each place, so a tool
could not make every edit. **Why not on touch alone.** Eleven of the 31 imports sat in code nobody
had changed for a year. On touch alone they would still be there.

## What the three have in common

Each change says which of the three answers in section 7 it takes. Each has a check anyone can
run: the formatter check in CI, the `order: dict` count, and the count in the tracking issue.
None of them rewrote code that no change had a reason to touch, except by a tool and a command
that proved it.
