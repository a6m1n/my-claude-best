# Assertions

The line that decides pass from fail: what it compares, how a raise is named, how a computed
number is compared, when an assertion carries a message, and what a test asserts is absent. The
class around these lines and the name that states the guarantee are
[test-structure.md](test-structure.md); the snippets below are the assertion lines alone, and use
the reminder module of [readability/module-example.md](../readability/module-example.md).

**Navigation**

- [1. The guarantee, not a proxy](#1-the-guarantee-not-a-proxy)
- [2. A record is compared whole](#2-a-record-is-compared-whole)
- [3. Name the failure you expect](#3-name-the-failure-you-expect)
- [4. Numbers that came out of arithmetic](#4-numbers-that-came-out-of-arithmetic)
- [5. Assert messages](#5-assert-messages)
- [6. What must not leak](#6-what-must-not-leak)
- [7. Sources](#7-sources)

## 1. The guarantee, not a proxy

**Compare with the exact value the guarantee promises**, never with a check a wrong answer would
also pass: `is not None`, `len(...) > 0`, a bare truth test on a value that is not a `bool`, or `in`
where the whole value is known. A proxy passes for the right reason once and for the wrong reason
ever after.

```python
# Bad: any email to anyone passes, and so does a result of NOT_NEEDED that still sent
# one.
assert result
assert mailer.sent

# Good: the value the name promises, and the one email it promises.
assert result is ReminderResult.SENT
assert [email.to for email in mailer.sent] == ["jane.doe@example.com"]
```

A member of a set you own is compared with `is` ([python.md](../python/python.md) section 3).
A function annotated `-> bool` is asserted bare, `assert needs_reminder(...)` or
`assert not needs_reminder(...)`: the type checker lets only `True` or `False` out of it, so the
bare test is the exact value, and PEP 8 advises against comparing a boolean to `True`.

One exception covers printed output. Output a person reads (`capsys`) carries a layout the test
does not own, so a substring is the exact form of that guarantee. It still names the subject and
the outcome, never only that something was written:
`assert "1 reminder sent" in capsys.readouterr().out`, not `assert capsys.readouterr().out`. A log
line is not a guarantee ([logging.md](../logging/logging.md) section 11); a test reads `caplog`
only to check that a secret stays out of it (section 6).

## 2. A record is compared whole

**When the guarantee is a record, what a function returned or what it stored, compare it as one
equality over the whole value**, not one field at a time. A test that checks three fields of four
promises more than it checks, and a field added later is never checked at all. A frozen dataclass
or a Pydantic model compares by value, and pytest prints both sides with the fields that differ.

```python
# Bad: two fields of the stored invoice. A wrong amount, or an email changed by the run,
# passes.
stored = get_invoice(database, invoice_id)
assert stored.last_reminded_on == TODAY
assert stored.due_on == DUE_ON

# Good: the whole invoice the run should have left, built by the file's builder.
assert get_invoice(database, invoice_id) == an_invoice(last_reminded_on=TODAY)
```

`an_invoice` is the builder of [fixtures.md](fixtures.md) section 7. A test that checks what a unit
stored or returned compares the whole record; a test whose guarantee is one derived value (a list
of recipients, a count, a flag) compares that value.

**Give each record another system reads one test that pins its whole field set**, its docstring
opening with `Pins:` ([test-structure.md](test-structure.md) section 5): a JSON payload a partner
parses, a row another service reads. A renamed or added field then fails there, and someone
decides what the other side should receive.

## 3. Name the failure you expect

**When you assert that something raises, name the failure**: `match=` on its message, or an
assertion on `excinfo.value`. A bare `pytest.raises(ValueError)` also passes when the code raises
the same type for another reason, including the reason the test was not written for.

```python
# Bad: any validation error passes, such as a missing host instead of the placeholder
# key.
with pytest.raises(ValidationError):
    Settings(_env_file=None)

# Good: the message is part of the guarantee.
with pytest.raises(ValidationError, match="placeholder"):
    Settings(_env_file=None)
```

- `match` is a regular expression searched in the string of the exception. A fragment that
  separates this failure from the others of its type is enough. Pass literal text through
  `re.escape()` when it holds `.`, `(`, `[` or `|`.
- ruff's `PT011` reports a `pytest.raises` of a broad exception, such as `ValueError`, without
  `match`; `PT012` reports a `with` block that holds more than the one call expected to raise.

## 4. Numbers that came out of arithmetic

**When a float came out of arithmetic, compare it with `pytest.approx` and state the tolerance the
domain has**, not the default one. `approx` with no tolerance allows a relative `1e-6`, which is
not what a two-decimal share means.

```python
# Bad: the value came out of a division, so its last bits are not the number written
# here.
assert share_overdue == 0.33

# Good: two decimals, the precision the report shows.
assert share_overdue == pytest.approx(0.33, abs=0.005)
```

- **Money is a `Decimal`, and a `Decimal` is compared exactly.** A rounding rule is part of the
  guarantee, so the test writes the rounded value.

## 5. Assert messages

pytest rewrites every `assert` statement: when a comparison fails, the report shows both sides,
the repr of each name and attribute the failed expression reads, and for a list, a dict or a
dataclass, the items that differ. So `assert invoice.due_on < TODAY` inside a loop already shows
the whole invoice. A message on a plain comparison adds a sentence and no information.

**Add a message when the failed line reads a value by key or index**, such as
`row["reminded_on"]` inside a loop: the report shows only that value, not the row it came from.
**Make the message the data a reader needs to find the failure**: the whole row, or the input that
produced it; the id of the item when the row holds a secret or a customer's text.

```python
reminded_rows = [row for row in exported_rows if row["reminded_on"] is not None]
assert [row["invoice_id"] for row in reminded_rows] == ["inv-1001", "inv-1002"]

# Bad: the message is a sentence with no data, so the report cannot say which row failed.
for row in reminded_rows:
    assert row["reminded_on"] > row["due_on"], "reminded too early"

# Good: the message is the row, so the report shows which row was reminded too early.
for row in reminded_rows:
    assert row["reminded_on"] > row["due_on"], (
        f"reminded on or before the due date: {row}"
    )
```

With the Bad message the report reads "reminded too early" over
`assert datetime.date(2026, 9, 10) > datetime.date(2026, 9, 12)`, and no line names the row.

- **A message never holds a secret or a customer's text** (section 6): it is printed in the
  report, and CI keeps the report.
- **A loop of asserts passes when it runs zero times.** When the list comes out of a filter, as
  `reminded_rows` does, pin it first, as the line above the two loops does.
- **Prefer a comparison that shows everything over a loop with a message.** A loop whose check is
  an equality can often be one equality over a dict,
  `{i.invoice_id: i.last_reminded_on for i in ...} == {...}`, which needs no message at all.

## 6. What must not leak

**When a test drives code that handles a secret, a prompt or a customer's own text, assert next to
the positive assertion that it is absent from the output or the log.** The positive assertion
alone cannot see a leak: a run that sends the right email and logs the API key on the way passes
it. What must never be logged is [logging.md](../logging/logging.md) section 10; this section is
how a test holds the code to it.

**Pair every negative `caplog` assertion with a positive one in the same test**, after
`caplog.set_level(logging.DEBUG)`, so the negative check reads every level
[logging.md](../logging/logging.md) section 10 covers. With nothing captured, the negative check is
true for the wrong reason. The positive line checks that a record was captured at the level the code
logs at, not its text. The negative check reads every attribute of every record, not `caplog.text`:
the text holds only what its log format prints (the level, the logger, the file, the line and the
message), and a value the code passes in `extra=` ([logging.md](../logging/logging.md) section 3)
never reaches it.

```python
# Bad: nothing positive is asserted, so a run that logged nothing passes the check.
caplog.set_level(logging.DEBUG)

with pytest.raises(PaymentUnavailable, match="status 503"):
    unavailable_gateway.charge(PaymentId("pay-1001"), Decimal("120.00"))

assert not any("key-for-tests" in repr(vars(record)) for record in caplog.records)

# Good: the level is set, a WARNING record is found first, and then the key is not.
caplog.set_level(logging.DEBUG)

with pytest.raises(PaymentUnavailable, match="status 503"):
    unavailable_gateway.charge(PaymentId("pay-1001"), Decimal("120.00"))

assert any(record.levelno == logging.WARNING for record in caplog.records)
assert not any("key-for-tests" in repr(vars(record)) for record in caplog.records)
```

`unavailable_gateway` is the gateway of [fakes-and-boundaries.md](fakes-and-boundaries.md)
section 3 with a transport that answers 503. Left out are `charge`, its retries and
`PaymentUnavailable`, which belong to the client. It logs
`Payments API answered 503, retry %d of %d` at `WARNING` before each retry, and after the last it
raises `PaymentUnavailable`, which names the status, as [logging.md](../logging/logging.md)
section 5 asks of the one client of an external system.

- **A check that a value is absent needs a check that the output could have held it**, as the
  positive `caplog` line does for a log. pydantic's error text shows an input whose repr is over 50
  bytes as its first 25 and last 24 bytes, so a long key is never there whole, and a `not in`
  check on it passes whether the key leaked or not.
- **Match a secret by a value only a leak could produce**: the test's own fake key, or the fixed
  prefix every key of that vendor has.
- **No test, fixture or example holds a real key or a real customer's data.** A test's key is
  written as a placeholder, `SecretStr("key-for-tests")`.

## 7. Sources

pytest documentation: "How to write and report assertions in tests" (assertion rewriting,
`pytest.raises` and `match`), `pytest.approx` in the API reference, "How to manage logging"
(`caplog`, `set_level`). ruff rules `PT011` and
`PT012` (flake8-pytest-style). pydantic-core `src/tools.rs` at v2.41.5: how an error's text cuts
an input's repr over 50 bytes.
