# Test structure

How the inside of a test file is built: the class, the names, the docstrings and the tables of
inputs. Where the file goes is [layout.md](layout.md); where its setup comes from is
[fixtures.md](fixtures.md). A test is code, so [readability.md](../readability/readability.md) holds
for it unchanged: blank lines between arrange, act and assert are its section 5.

The examples test `needs_reminder` from
[readability/module-example.md](../readability/module-example.md): an overdue invoice gets a
reminder after its due date, at most once a week. Their imports are left out.

**Navigation**

- [1. A class per unit under test](#1-a-class-per-unit-under-test)
- [2. No state on the class](#2-no-state-on-the-class)
- [3. The name is the guarantee](#3-the-name-is-the-guarantee)
- [4. One behavior per test](#4-one-behavior-per-test)
- [5. Docstrings](#5-docstrings)
- [6. One guarantee, a table of inputs](#6-one-guarantee-a-table-of-inputs)
- [7. When a table is the wrong tool](#7-when-a-table-is-the-wrong-tool)
- [8. Where it stops holding](#8-where-it-stops-holding)
- [9. Sources](#9-sources)

## 1. A class per unit under test

**When you add a test, put it in the `Test<Unit>` class of its file**, where `<Unit>` is the
function or class the test's act step calls, in CamelCase: `needs_reminder` is tested in
`TestNeedsReminder`, and a guarantee file's class is named for its guarantee instead
([layout.md](layout.md) section 5). The act step is the one line that calls the unit; it sits
between the arrange and the assert, or inside the assert when the unit only returns a value. Each
file holds one class ([layout.md](layout.md) section 4).

pytest names three reasons to group tests in a class: "Test organization, Sharing fixtures for
tests only in that particular class, Applying marks at the class level and having them implicitly
apply to all tests". This practice adds a fourth: the class name is a selector, so
`pytest tests/unit/remind_overdue_invoice/test_reminder_rules.py::TestNeedsReminder` runs one
unit's tests, and `-k NeedsReminder` finds them anywhere.

```python
# Good: the class names the unit, each test names a guarantee.
class TestNeedsReminder:
    """An overdue invoice gets a reminder after its due date, at most once a week."""

    def test_an_invoice_not_past_its_due_date_needs_no_reminder(self) -> None:
        due_on = date(2026, 9, 1)

        assert not needs_reminder(due_on, last_reminded_on=None, today=due_on)
```

A class that holds one test is normal: it still gives the unit its docstring, its selector and
one place for its marks.

Check: `grep -nE "^(async )?def test_" <file>` prints nothing: no test sits outside the class.

## 2. No state on the class

pytest's reason: "Each test has a unique instance of the class. Having each test share the same
class instance would be very detrimental to test isolation and would promote poor test practices."
A value one test writes on `self` is not there for the next, and a test that seems to read it
passes for a reason nobody wrote down.

**Never write an attribute of `self` in a test, and never use `setup_method`, `setup_class` or
`teardown_method`.** Build what a test needs inside it, or take it from a fixture
([fixtures.md](fixtures.md)); a value every test in the file reads and nobody changes is a
module-level constant.

```python
# Bad: the second test reads what the first one set. Each test gets its own instance,
# so the attribute is not there, and pytest never promised the order anyway.
class TestNeedsReminder:
    """An overdue invoice gets a reminder after its due date, at most once a week."""

    def test_an_overdue_invoice_needs_a_reminder(self) -> None:
        self.due_on = date(2026, 9, 1)

        assert needs_reminder(
            self.due_on, last_reminded_on=None, today=date(2026, 9, 2)
        )

    def test_an_invoice_on_its_due_date_needs_no_reminder(self) -> None:
        assert not needs_reminder(self.due_on, last_reminded_on=None, today=self.due_on)
```

```python
# Good: the date every test reads is a constant, and each test builds the rest itself.
DUE_ON: Final = date(2026, 9, 1)


class TestNeedsReminder:
    """An overdue invoice gets a reminder after its due date, at most once a week."""

    def test_an_overdue_invoice_needs_a_reminder(self) -> None:
        assert needs_reminder(DUE_ON, last_reminded_on=None, today=date(2026, 9, 2))

    def test_an_invoice_on_its_due_date_needs_no_reminder(self) -> None:
        assert not needs_reminder(DUE_ON, last_reminded_on=None, today=DUE_ON)
```

Check: `grep -nE "self\.[a-z_]+ *=|def (setup|teardown)_(method|class)" <file>` prints nothing.

## 3. The name is the guarantee

**Name a test as the sentence that stops being true when the code breaks**, never as the function
it calls or a number. Write the name before the body, and read it aloud: if it does not say what
breaks, rename it. A test name is read twice, once here and once in a CI log by someone who has
not opened the file, so a long name is fine: pytest prints it in full, and `-k` matches substrings
of it (`-k remind` also picks up `reminder`).

```python
class TestNeedsReminder:
    """An overdue invoice gets a reminder after its due date, at most once a week."""

    # Bad: the name says which function ran. A red line in CI says nothing until
    # someone opens the file, and a second test of the same function needs a number
    # to tell it apart.
    def test_needs_reminder(self) -> None:
        assert not needs_reminder(DUE_ON, last_reminded_on=None, today=DUE_ON)

    # Good: the name is the sentence that breaks. The CI line is the bug report.
    def test_an_invoice_on_its_due_date_needs_no_reminder(self) -> None:
        assert not needs_reminder(DUE_ON, last_reminded_on=None, today=DUE_ON)
```

The name uses the business's words, as every name does
([readability.md](../readability/readability.md) section 7): "invoice", "reminder", "due date",
not "obj", "flag" or "case 2".

## 4. One behavior per test

**When a test's name needs "and", split it into two tests.** Write the name first, and let it
tell you how many tests you are writing. Two behaviors in one test hide each other: a failure on
the first assertion stops the test before the second runs, and the report names one thing where
two are at stake. Setup is a fixture away ([fixtures.md](fixtures.md)); a guarantee is not.

Several assertions about one behavior are one test. Checking a record as one equality over its
whole value is also one assertion ([assertions.md](assertions.md) section 2).

The methods below sit in `TestNeedsReminder`; its class line is left out.

```python
# Bad: two guarantees under one name. When the first assertion fails, nobody
# learns whether the weekly limit still holds.
def test_a_first_reminder_goes_out_and_a_second_waits_a_week(self) -> None:
    assert needs_reminder(DUE_ON, last_reminded_on=None, today=date(2026, 9, 2))
    assert not needs_reminder(DUE_ON, date(2026, 9, 2), today=date(2026, 9, 5))


# Good: the split the name asked for. Each guarantee fails on its own line in the
# report.
def test_an_invoice_never_reminded_gets_its_first_reminder_after_the_due_date(
    self,
) -> None:
    assert needs_reminder(DUE_ON, last_reminded_on=None, today=date(2026, 9, 2))


def test_a_second_reminder_waits_for_the_interval(self) -> None:
    assert not needs_reminder(DUE_ON, date(2026, 9, 2), today=date(2026, 9, 5))
```

## 5. Docstrings

**Give every test class a docstring**: one sentence that says what its unit guarantees. It is
what `--collect-only` and a reader of the file see first.

**Give a test a docstring only when it says what the name cannot**: the consequence of the
guarantee, the invariant it pins, or the bug it holds down. A docstring that repeats the name or
narrates the steps is deleted: it goes stale on the first edit.

Two first lines are always written, whatever the name says, so a search finds them:

- **`Regression (PROJ-123): <what used to happen, past tense>.`** opens the docstring of a test
  that holds down a fixed bug; the next paragraph says what holds now. The test lands in the
  commit that fixes the bug.
- **`Pins: <the invariant>.`** opens the docstring of a test whose failure means the change is
  wrong until someone proves otherwise, such as the fields of a record another system reads. The
  second line says what breaks if it moves.

```python
class TestNeedsReminder:
    """An overdue invoice gets a reminder after its due date, at most once a week."""

    # Good: the docstring gives the consequence, which the name cannot.
    def test_a_second_reminder_waits_for_the_interval(self) -> None:
        """Daily reminders made customers unsubscribe instead of paying."""
        assert not needs_reminder(DUE_ON, date(2026, 9, 2), today=date(2026, 9, 5))

    # Good: the bug in the past tense, then what holds now.
    def test_a_reminder_goes_out_on_the_day_the_interval_ends(self) -> None:
        """Regression (PROJ-123): the check used > where it meant >=, so each repeat
        reminder went out one day late.

        A reminder is due again on the day the interval ends.
        """
        last_reminded_on = date(2026, 9, 2)

        assert needs_reminder(
            DUE_ON, last_reminded_on, today=last_reminded_on + REMINDER_INTERVAL
        )

    # Bad: the docstring narrates the body and names the function. It adds nothing to
    # the name. The fix deletes the docstring; the test stays as it is.
    def test_an_invoice_on_its_due_date_needs_no_reminder(self) -> None:
        """Calls needs_reminder with today set to the due date; checks it is False."""
        assert not needs_reminder(DUE_ON, last_reminded_on=None, today=DUE_ON)
```

## 6. One guarantee, a table of inputs

`@pytest.mark.parametrize` runs one test body over rows of inputs. It is for one guarantee that
holds over many inputs. Five near-copies of a test hide how many inputs are covered, and one of
them drifts from the others at the next edit; a table shows every input at once.

**When one guarantee has several inputs, write one parametrized test and name every row** with
`pytest.param(..., id="...")`. The id is a few words that say what the row is, so a failing row
reads as `test_an_overdue_invoice_needs_a_reminder[reminded-one-interval-ago]`, not
`[last_reminded_on1-today1]`. Argument names are a tuple (a single name is a string) and rows
a list, the forms ruff's `PT006` and `PT007` check.

```python
class TestNeedsReminder:
    """An overdue invoice gets a reminder after its due date, at most once a week."""

    # Good: one guarantee, three named rows. Adding a fourth case is one line.
    @pytest.mark.parametrize(
        ("last_reminded_on", "today"),
        [
            pytest.param(None, date(2026, 9, 2), id="never-reminded-a-day-after-due"),
            pytest.param(
                date(2026, 9, 2),
                date(2026, 9, 2) + REMINDER_INTERVAL,
                id="reminded-one-interval-ago",
            ),
            pytest.param(date(2026, 9, 2), date(2026, 9, 30), id="reminded-weeks-ago"),
        ],
    )
    def test_an_overdue_invoice_needs_a_reminder(
        self, last_reminded_on: date | None, today: date
    ) -> None:
        assert needs_reminder(DUE_ON, last_reminded_on, today)
```

Check: `pytest --collect-only -q <file>` prints ids made of words, never an id that ends in a
number pytest invented.

## 7. When a table is the wrong tool

A table pays when the rows share one guarantee and one body. Leave it out when:

- **The outcome differs in kind between rows.** Rows that expect `True` and rows that expect
  `False` are two guarantees, "needs a reminder" and "needs no reminder": write two tests with a
  table each. An `expected` column is right only when the guarantee is a mapping and the name says
  so, as in `test_each_status_maps_to_its_http_code`.
- **The body branches on a parameter.** An `if` on a row value is two tests sharing a name.
- **The expected value is computed in the test** with the same formula as the code. The test then
  agrees with any bug in the formula; write the expected values out. An input built from the
  unit's own constant, as `REMINDER_INTERVAL` above, is not such a formula: the interval is a
  value someone chose, and a test that pinned seven days would turn red on that choice
  ([what-to-test.md](what-to-test.md) section 3).
- **A row needs setup the others do not.** Give it its own test.
- **There are one or two rows.** Two named tests read better than a table of two.

When one guarantee holds over two independent inputs, **stack two `parametrize` decorators**
instead of writing out the combinations: pytest runs every pair. Check that
`pytest --collect-only -q <file>::<Class>::<test>` prints as many lines as the product of the two
tables.

When a table should feed a fixture rather than the test, such as a database in two states, that
is indirect parametrization, [fixtures.md](fixtures.md) section 8.

## 8. Where it stops holding

- **A characterization test**, which pins what old code does today before a change
  ([refactoring.md](../refactoring/refactoring.md) section 3), is named for the behavior it
  records, which may be a bug; its docstring says so.
- **A property-based test** (Hypothesis, [libraries.md](libraries.md)) has no table: its name
  states the property, `test_a_reminder_is_never_needed_before_the_due_date`, and the library
  picks the inputs.

## 9. Sources

pytest documentation: "Get Started" (grouping tests in a class, and one instance per test) and
"How to parametrize fixtures and test functions". ruff rules `PT006` and `PT007`
(flake8-pytest-style).
