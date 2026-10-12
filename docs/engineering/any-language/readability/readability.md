# Readability rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. One job per unit](#2-one-job-per-unit)
- [3. Guard clauses: the main path stays flat](#3-guard-clauses-the-main-path-stays-flat)
- [4. Comments say why](#4-comments-say-why)
- [5. Blank lines between stages](#5-blank-lines-between-stages)
- [6. Every input in the signature](#6-every-input-in-the-signature)
- [7. Names from the business](#7-names-from-the-business)
- [8. Layout: one formatter decides it](#8-layout-one-formatter-decides-it)
- [9. Where it stops holding](#9-where-it-stops-holding)
- [10. Review checklist](#10-review-checklist)
- [11. Sources](#11-sources)

## 1. Purpose and the one rule

This file is for everyone who writes or reviews code: people and AI agents alike. Read it before
you write or change a function or a class, and when you review one.

It is about how code reads inside a file: what one unit does, how its body flows, how its lines
are laid out, and what its names and comments say. Where a file sits and what it is called is
[file-structure.md](../file-structure/file-structure.md). Where a business decision and its rule
live, and how a type carries a constraint, is [python.md](../../python/language/python.md) section 2. The
examples are Python; the principles hold in any language. The parts marked **Python case** are
Python's own: PEP 8's form for a condition written as one test (section 3), the form PEP 8 and
PEP 257 give comments and docstrings (section 4), PEP 8's naming conventions (section 7), and the
formatter with its settings, the import rules and whitespace inside a string (section 8). Another
language puts its own style guide and formatter in their place. Each example shows the smallest
piece that makes its point, a line, a function, or a function and its test, and leaves out its
imports and the types and functions it calls. [module-example.md](module-example.md) shows a whole
module.

The one rule: **a reader tells what a unit does, and what it depends on, from the unit itself:
its name, its signature and its body.** The reader should not have to open the functions it calls
to follow it, or run it to learn what it touches. Each section below is one way that rule breaks,
and the fix.

Why it matters:

- Code is read many more times than it is written. Robert C. Martin puts the ratio of reading to
  writing at "well over 10 to 1" (*Clean Code*, ch. 1), so a minute saved for the writer and lost
  for every reader is a bad trade.
- A reader who has to hold several things in mind at once makes mistakes. Each principle here
  removes one of them: a second job, a nested condition, a hidden input, a name that has to be
  translated.

Any code a change writes or edits has to meet this file.

## 2. One job per unit

When you write a function or a class, give it one job and a name that says the whole job.

- **The one-sentence test.** Say what the unit does in one sentence. If the sentence needs "and"
  between two jobs, or the name is too general to finish it (`process`, `handle`, `manage`), it
  is two units. Martin's version: functions "should do one thing. They should do it well. They
  should do it only."
- **One level of detail per body.** A function that calls named steps does not also do the
  arithmetic of one of them. When "save the invoice" sits next to the loop that sums its lines,
  the reader switches between the story and its details at every line. Kent Beck calls the shape
  that avoids it the Composed Method: a body made of calls at one level of detail.
- **A class keeps state its methods share.** When a group of fields is used only by a group of
  methods, that group is a second class inside the first: split it out.
- **Length is a hint, never a cap.** A long body most often holds more than one job. Split it
  where one job ends and the next begins; how many lines it has does not decide where the cut
  goes. Where a split stops paying is [python.md](../../python/language/python.md) section 2, condition 5.

How jobs split into files is [file-structure.md](../file-structure/file-structure.md) section 3;
which function holds a business decision and which only acts is
[python.md](../../python/language/python.md) section 2.

```python
# Bad: one body does three jobs at two levels of detail. It builds the
# invoice lines, formats the email body, and runs the flow. A change to the
# email body edits the same function as the change to how lines are priced.
def issue_invoice(
    order: PaidOrder,
    db: Database,
    mailer: Mailer,
) -> Invoice:
    lines = [
        InvoiceLine(
            order_line.product_name, order_line.unit_price * order_line.quantity
        )
        for order_line in order.lines
    ]
    invoice = Invoice(order.order_id, lines)

    save_invoice(db, invoice)

    body = "\n".join(f"{line.name}: {line.amount}" for line in lines)
    mailer.send(order.email, subject="Your invoice", body=body)

    return invoice
```

```python
# Good: the same flow puts each detail in a function named for it. The body
# reads as three steps at one level: build, save, send. The email body now
# changes in render_invoice_email alone, and build_invoice is tested with
# plain values.
def issue_invoice(
    order: PaidOrder,
    db: Database,
    mailer: Mailer,
) -> Invoice:
    invoice = build_invoice(order)

    save_invoice(db, invoice)

    mailer.send(order.email, subject="Your invoice", body=render_invoice_email(invoice))

    return invoice
```

## 3. Guard clauses: the main path stays flat

When a function has cases that end it early, test them at the top and end the function there.
What is left runs top to bottom at the first indentation level, so no line asks the reader to
remember which `if` it still sits inside.

- **A guard ends the function in one of two ways:** it raises for a state the function refuses,
  or it returns a value the signature declares. In a use case, a top-level `if` that returns a
  value is the business decision [python.md](../../python/language/python.md) section 2 describes, not a
  guard.
- **No `else` after a branch that returned or raised.** The code after the `if` already is the
  else, and the extra level only moves the main path to the right. ruff's `RET505` and `RET506`
  flag it.
- **Turn nesting into guards when the main path sits inside two or more nested `if`s,** or when
  the real work waits in the last `else`, far from the conditions it depends on.

Kent Beck named the shape the guard clause (*Smalltalk Best Practice Patterns*, 1997). Martin
Fowler's refactoring catalog has the move from the nested form: Replace Nested Conditional with
Guard Clauses.

```python
# Bad: the main path sits inside three nested `if`s, and each error sits at
# the bottom, far from the check that raises it. The reader holds three open
# conditions to see when a code is returned.
def parse_discount_code(raw: str) -> DiscountCode:
    code = raw.strip().upper()

    if code:
        if len(code) == CODE_LENGTH:
            if code.isalnum():
                return DiscountCode(code)
            else:
                raise InvalidDiscountCodeError("only letters and digits")
        else:
            raise InvalidDiscountCodeError(f"must have {CODE_LENGTH} characters")
    else:
        raise InvalidDiscountCodeError("empty")
```

```python
# Good: the same checks become guards. Each error sits next to its condition, and
# what is left at the end is the main path, at the first level.
def parse_discount_code(raw: str) -> DiscountCode:
    code = raw.strip().upper()

    if not code:
        raise InvalidDiscountCodeError("empty")

    if len(code) != CODE_LENGTH:
        raise InvalidDiscountCodeError(f"must have {CODE_LENGTH} characters")

    if not code.isalnum():
        raise InvalidDiscountCodeError("only letters and digits")

    return DiscountCode(code)
```

**Python case: a condition is written as the test it makes.**

| Write | Not | Why | Check |
|---|---|---|---|
| `if is_paid:` | `if is_paid == True:` | the comparison adds nothing the `if` does not already do | `E712` |
| `if key not in prices:`, `if a is not b:` | `if not key in prices:`, `if not a is b:` | the same behaviour, read as one test | `E713`, `E714` |
| `if code.startswith("PROJ-"):` | `if code[:5] == "PROJ-":` | PEP 8 calls it "cleaner and less error prone": the call names the test, and a slice length can be miscounted | review |
| `if not order_lines:` | `if len(order_lines) == 0:` | an empty sequence is false, so the length adds nothing the `if` does not already do | review |

PEP 8 gives the reason for `is not` over `not ... is`: "the former is more readable and preferred".
ruff marks its `E712` fix unsafe: NumPy, pandas and SQLAlchemy redefine `==`, and there the
rewrite changes what the code does, so `ruff check --fix` leaves those lines to a person.

## 4. Comments say why

When you write a comment, write what the code cannot say: why this value, why this order, which
outside constraint forces the line. Names and structure say what the code does.

What a comment holds:

- **The reason for a value that is not obvious**: a limit, a timeout, a start index, a regular
  expression.
- **A decision the code does not show**, such as a known bug in an outside system or a line that
  exists for security. The missing comment is as common as the useless one. To decide whether a
  comment earns its place, imagine the line without it: if the next editor would then likely
  make the mistake it warns about, keep it.
- **In code that others copy, the reason for each line a copier would otherwise change or
  delete**: an example in a doc, a template, a snippet in a README. The prose around such code
  stays behind when it is copied, so the reason has to sit at the line. MDN's code style guide
  says why: "Readers will copy and paste examples into their own code and may put it into
  production." The test above still decides which lines get one; Microsoft's style guide sets the
  same limit: "Help developers determine what to modify. Add comments to explain details, but
  don't overdo it. Don't state the obvious."
- **The code as it is now.** Change a comment in the same edit as the line it describes. A
  comment that describes old behavior is worse than none, because the reader believes it.

What to delete:

- **A comment that repeats the line below it.** Delete it, or rename until it is not needed. It
  adds nothing, and it goes stale at the next change.
- **Commented-out code.** Git keeps the old version, and ruff's `ERA001` flags the lines.

Where other text goes:

- **The story of a change goes in the commit message**, not in the code. A note such as "moved
  to X, since Y took too long" helps whoever reviews that diff ([git.md](../git/git.md) section
  3). The next reader of the code needs the constraint, not the story of the diff. A test that
  holds down a fixed bug is the one exception: its docstring tells that story
  ([python/testing/test-structure.md](../../python/testing/test-structure.md) section 5).
- **What the caller needs goes in the docstring.** A docstring is for the caller and says what
  the function does, returns and raises (PEP 257); a `#` comment is for the maintainer and says
  why the body is the way it is.

PEP 8 draws the same line with one pair of examples: `x = x + 1  # Compensate for border`, not
`# Increment x`.

```python
# Bad: the comment repeats what the line already says. It adds nothing, and it
# goes stale when the value changes.

# Timeout for the provider, in seconds.
PROVIDER_TIMEOUT_SECONDS: Final = 25
```

```python
# Good: the same line, and the comment now carries the one fact the line cannot
# show: why 25. Without it, the next editor may raise it to "give the provider
# more time".

# The provider's gateway drops a connection after 30 seconds; stopping at 25
# lets us return our own error instead of a dropped connection.
PROVIDER_TIMEOUT_SECONDS: Final = 25
```

**Python case: the form PEP 8 and PEP 257 give comments and docstrings.**

- **A comment follows PEP 8's form.** It starts with a capital, unless its first word is an
  identifier, a file name, or a fixed marker a tool or another practice searches for, such as
  `legacy` in `# noqa: CODE  # legacy`, whose spelling stays; each line of a block comment starts
  with `#` and a single space, unless it holds indented text; a block comment is complete
  sentences, each ending with a period; an inline comment sits at least two spaces after the code,
  starts with `#` and a single space, is rare, and may be a short phrase, as PEP 8's own
  `x = x + 1  # Compensate for border` is. A comment that only names a file, such as the path at
  the top of a snippet, is a label: it keeps the file's spelling and needs no period. English,
  unless the code will never be read by anyone who does not speak your language, as PEP 8 puts it:
  the next reader may be anyone.
- **A docstring takes PEP 257's form:** triple double quotes; a summary that fits on one line and
  ends with a period; in a longer docstring, one blank line after the summary, then the rest, and
  the closing quotes on a line of their own. The summary of a function or a method gives its
  effect as a command, "Return the share of runs that …", not "Returns …" and not a noun phrase.
  One form across the code base lets a reader scan the summaries the same way everywhere. Google's
  Python guide accepts the descriptive form too, if a file keeps one; this practice takes PEP 257's
  command.
- **A docstring only where the name and the signature leave out what the caller needs.** PEP 8
  asks for one on every public module, function, class and method; this practice departs from
  that ([python.md](../../python/language/python.md) section 6), because a docstring that repeats
  the name goes stale like a comment that repeats the line. The comment PEP 8 asks for after the
  `def` line of a non-public method follows the same rule: it is written only where the name
  leaves out what the method does. A library's public modules, functions, classes and methods keep
  PEP 8's docstring, because its users read the API through `help()`, `pydoc` and generated docs
  rather than the source, the same reason the `__all__` bullet in section 7 gives; a library takes
  `"D1"` out of the `ignore` list and adds it to the `"tests/**"` entry of `per-file-ignores`
  ([setup-example.md](../../python/static-checks/setup-example.md) section 1), since a test follows
  the testing practice's docstring rule.
- **Under `tests/`, two parts of the form give way: the one-line summary and the command.** A
  test's docstring follows the testing practice
  ([python/testing/test-structure.md](../../python/testing/test-structure.md) section 5): its
  forms, such as `Regression (PROJ-123): …` or a test class's one sentence, open with a statement
  and may run over more than one line. A fixture's summary may name what it gives, "A mailer that
  keeps what it was asked to send", the way `pytest --fixtures` lists it. Every other docstring
  there, a helper's or a factory's, keeps the whole form.
- **The checks.** ruff's `D` rules with `convention = "pep257"` check the docstring form. `D1`,
  the rules that ask for a docstring everywhere, stay off for the reason above, and `D205` (the
  blank line after a one-line summary) stays off under `tests/`, where a test's first sentence may
  run over two lines. `D401` (the command) skips a function named `test…` by itself, and ruff's
  `property-decorators` setting makes `D401` skip a fixture too, as it does for a `@property`,
  while every other `D` rule still checks the fixture's docstring
  ([setup-example.md](../../python/static-checks/setup-example.md) section 1). A helper's or a
  factory's docstring is still checked by the `D` rules, apart from `D205` under `tests/`. The
  width of comments and docstrings is section 8. Complete sentences, the `# ` that opens each line
  of a block comment, and English are review.

## 5. Blank lines between stages

When a function body has several stages, such as get the data, compute a value, check it, decide,
act and return, put one blank line between two stages and none inside a stage.

- **A stage is one step of the body at the level section 2 asks for:** load, compute, check, decide,
  act or return. Two acts are two stages. A line that changes nothing and whose result only the next
  line uses belongs to that line's stage.
- **A reader sees the stages before reading a line.** Martin calls this "vertical openness
  between concepts" (*Clean Code*, ch. 5): a blank line tells the reader that a new thought
  starts.
- **This practice uses more blank lines than PEP 8 asks for.** PEP 8 says to use them in
  functions "sparingly, to indicate logical sections". This practice puts one at every stage
  boundary, a guard included, so that every stage shows before a line is read (the bullet above).
  It keeps PEP 8's other half: never a blank line inside a stage, where it splits what belongs
  together.
- **An `if` that ends the function early is a stage of its own, and so is the final `return`**
  of a body with more than one stage.
- **Inside a branch that acts and then returns, the return is a stage of its own**, one blank
  line after the act. A branch that only returns or raises is one stage.
- **A test has the same stages: arrange, act and assert.** When the act only returns the value the
  assert checks, as in a test of a rule, the act sits inside the assert line, and the test has two
  stages (section 6 shows one). An act that changes state, such as a call to a use case, is a
  stage of its own.
- **Once the stages show, each one is a candidate for a named function** (section 2). Extracting a
  stage does not remove its blank lines: the function's name tells the reader what the step is
  for, and the empty line shows where the step stops.
- **A formatter keeps these lines but does not choose where they go.** Black and ruff format keep
  a single blank line inside a function, collapse several into one, and add one before and after a
  nested function that does not open the body. ruff format also removes a blank line at the start
  of a block, such as an `if`, `for`, `with` or `class` body, but keeps one at the start of a
  function body unless a docstring follows. So the rule lives in review, not in a tool. The rest
  of the layout, and what the formatter leaves to the writer, is section 8.

```python
# Bad: five stages with no blank line between them. The reader has to find
# where loading ends and the decision starts.
def renew_subscription(
    subscription_id: SubscriptionId,
    today: date,
    db: Database,
    billing: BillingGateway,
) -> RenewalResult:
    subscription = get_subscription(db, subscription_id)
    if needs_card_update(subscription.card_expires_on, today):
        mark_card_update_needed(db, subscription_id)
        return RenewalResult.CARD_UPDATE_NEEDED
    charge_id = billing.charge(subscription.customer_id, subscription.plan.price)
    extend_subscription(db, subscription_id, subscription.plan.period, charge_id)
    return RenewalResult.RENEWED
```

```python
# Good: the same lines are split at each stage: load, decide (act, then return),
# charge, extend, return. The shape of the flow shows before a word is read.
def renew_subscription(
    subscription_id: SubscriptionId,
    today: date,
    db: Database,
    billing: BillingGateway,
) -> RenewalResult:
    subscription = get_subscription(db, subscription_id)

    if needs_card_update(subscription.card_expires_on, today):
        mark_card_update_needed(db, subscription_id)

        return RenewalResult.CARD_UPDATE_NEEDED

    charge_id = billing.charge(subscription.customer_id, subscription.plan.price)

    extend_subscription(db, subscription_id, subscription.plan.period, charge_id)

    return RenewalResult.RENEWED
```

## 6. Every input in the signature

When a unit reads the clock, a random number, an environment variable or a setting, take the
value as a parameter instead. Then its result depends only on what its signature shows, and a
test calls it with plain values.

- **Time.** The adapter reads the clock once per call and passes the value, `today` or `now`, to
  the use case, which passes it to the rule. A rule always takes the value, never a clock
  ([python.md](../../python/language/python.md) section 2). A use case or a doer that reads the time again
  during its work and acts on it or stores it, such as a deadline, a retry schedule, an expiry or
  a finish time it saves, takes a clock: a function the adapter passes in and a test replaces, such
  as `time.monotonic` for a deadline or a retry schedule, or one that returns `datetime.now(UTC)`
  for a time it saves. A duration measured only for a log line or a metric is not an input: read
  `time.perf_counter()` in place, before and after the work. Nothing the unit returns or saves
  depends on it, and no test checks it ([logging.md](../../python/logging/logging.md) section 11).
- **Randomness.** Take the value, or a `random.Random` the caller seeds, so a test can fix it.
- **Settings.** Read them once at startup, the way [python.md](../../python/language/python.md) section 5
  says, from the file [file-structure.md](../file-structure/file-structure.md) section 4 names, and
  pass the values in. A function that reads `os.environ` has an input no caller can see.
- **Computation apart from input and output.** A function that computes a value and then saves
  it cannot be tested without the save. Which function computes and which acts is
  [python.md](../../python/language/python.md) section 2.
- **Objects the unit calls come in the same way.** A store or a sender is passed in like a
  client ([python.md](../../python/language/python.md) section 2): the unit never builds one, and the adapter
  builds each once ([file-structure.md](../file-structure/file-structure.md) section 5).
- **A test passes a stand-in for the concrete class.** Annotate the parameter with the concrete
  class. A test still passes a stand-in: the real class with a fake inside it
  (`httpx.MockTransport`, a test database), `create_autospec(Mailer, instance=True)`, or a
  subclass that overrides the methods the unit calls. The type checker accepts all three, so a
  test alone is no reason for a new type.
- **Open-closed and dependency inversion: a second production class gets a protocol.** When a
  second class must fill the parameter in production, such as a disk store next to the cloud one,
  change the annotation to a `typing.Protocol` with only the methods the unit calls; where its
  file sits is [file-structure.md](../file-structure/file-structure.md) section 3. A new variant
  is then one new class and one line in the adapter, and the unit does not change: the
  open-closed principle (Bertrand Meyer named it; this form is Robert C. Martin's) and Martin's
  dependency inversion, at the size a Python service needs.

The signal comes from the test. When a test of a function that does no input or output itself,
such as a rule or a computation, needs `unittest.mock.patch` on a module path, a frozen clock or a
real database, the unit hides an input. Fix the unit, not the test. Gary Bernhardt calls the
target shape "functional core, imperative shell"; Brandon Rhodes' version is "hoist your I/O".

```python
# Bad: the rule reads the clock itself. Its answer changes from day to day
# with nothing in the signature to say so, and a test has to freeze time.
def needs_card_update(card_expires_on: date) -> bool:
    return card_expires_on <= date.today() + CARD_NOTICE_PERIOD
```

```python
# Good: today comes in as a value, like the expiry date. The answer depends
# only on the two arguments, and a test passes two dates.
def needs_card_update(card_expires_on: date, today: date) -> bool:
    return card_expires_on <= today + CARD_NOTICE_PERIOD


class TestNeedsCardUpdate:
    """A card needs an update when it expires within the notice period."""

    def test_card_expiring_within_notice_needs_update(self) -> None:
        today = date(2026, 10, 1)

        assert needs_card_update(today + CARD_NOTICE_PERIOD, today=today)
```

## 7. Names from the business

When you name a type, a function or a variable, use the word the business uses for that thing,
and one word for one thing across the codebase.

- **The words of the people who know the domain.** If they say "shipment", the code has
  `Shipment`, not `DeliveryObject` or `TransportRecord`. Eric Evans calls the shared vocabulary the
  ubiquitous language (*Domain-Driven Design*, 2003, chapter 2): the same words in the
  conversation, the code and the tests, so nothing is translated on the way.
- **One concept, one name.** Before you name a new thing, search the code for the name it already
  has. Two names for one thing (`customer`, `client`) make a reader ask whether they are two
  things. One name for two things hides a difference the business cares about.
- **A function name says the intent, not the mechanism**: `cancel_booking`, not
  `update_status_and_notify`.
- **A test's name says the behavior it pins**: `test_card_expiring_within_notice_needs_update`, not
  `test_needs_card_update_2`. How a test is named and grouped is
  [python/testing/test-structure.md](../../python/testing/test-structure.md) section 3.
- **Generic words say nothing on their own**: `data`, `info`, `item`, `record`, `obj`, `value`,
  `manager`, `processor`, `handler`. File names follow the same rule in
  [file-structure.md](../file-structure/file-structure.md) section 7.
- **A boolean reads as a yes-or-no question**: `is_paid`, `has_items`, `needs_manual_review`.
- **A number whose type does not carry its unit carries it in the name**: `timeout_seconds`,
  `amount_cents`.
- **No abbreviation a newcomer has to decode**: `customer_address`, not `cust_addr`. In one study,
  72 professional developers found a bug about 19% faster when the names were whole words than
  when they were single letters or abbreviations (Hofmeister, Siegmund and Holt, 2017). Short forms
  everyone knows, such as `id`, `url` and `html`, stay: an earlier study found abbreviations often
  understood as well as whole words (Lawrie et al., 2006).

```python
# Bad: generic names. `compute_value`, `entry` and `days` say nothing about
# the business: the reader has to read the body, and know the business, to
# learn that this is a late fee.
def compute_value(entry: Entry, days: int) -> Decimal:
    if days <= GRACE_DAYS:
        return Decimal(0)

    return entry.amount * DAILY_RATE * (days - GRACE_DAYS)
```

```python
# Good: the same body uses the business's words. The signature alone says what
# the function answers, and a finance colleague can check the formula.
def late_fee(invoice: Invoice, days_overdue: int) -> Decimal:
    if days_overdue <= GRACE_DAYS:
        return Decimal(0)

    return invoice.amount * DAILY_LATE_FEE_RATE * (days_overdue - GRACE_DAYS)
```

**Python case: PEP 8's naming conventions.** The case of a name tells the reader what kind of
thing it is before they read on: `PaidOrder` is a class, `paid_order` a value, `REMINDER_INTERVAL`
a constant. Every Python reader knows the convention, and that is its value; PEP 8's own principle
is that public names "should follow conventions that reflect usage rather than implementation".

| The name is | Form | Example |
|---|---|---|
| a class, a type alias, a type variable | `CapWords`, an acronym in capitals | `PaidOrder`, `LLMModel`, `T` |
| an exception that is an error | `CapWords` ending in `Error` | `InvalidDiscountCodeError` |
| a function, a method, a variable, a parameter | `lower_case_with_underscores` | `needs_reminder`, `days_overdue` |
| a constant | `UPPER_CASE_WITH_UNDERSCORES`, at module level | `REMINDER_INTERVAL` |
| for use inside its module or class only | one leading underscore | `_extra_fields` |
| a name that clashes with a keyword | one trailing underscore, never a corrupted spelling | `class_`, not `klass` |
| the first parameter of a method, of a class method | `self`, `cls` | |
| a module or a package | lower case; the file and folder names are [file-structure.md](../file-structure/file-structure.md) section 7 | `reminder_rules` |

PEP 8 names no form for a type alias; `CapWords` for one is PEP 484's advice.

- **Never `l`, `O` or `I` as a one-letter name.** PEP 8's reason: "In some fonts, these
  characters are indistinguishable from the numerals one and zero."
- **When you write a context manager that does more than acquire and release a resource, give it a
  method that names the act, and enter it through that method**:
  `with connection.begin_transaction():`, not `with connection:`. PEP 8's reason: the bare form
  gives no sign that its `__enter__` and `__exit__` do more than close the connection, and "Being
  explicit is important in this case". Review checks it.
- **No `__all__`.** PEP 8 asks each module to declare its public names in `__all__` "to better
  support introspection"; this practice does not. An application's modules are read through their
  imports, not through `help()` or `pydoc`: an import names the file that holds the name
  ([file-structure.md](../file-structure/file-structure.md) section 7), and the leading underscore
  in the table above already marks an internal name. `F403` (section 8) bans the star import that
  `__all__` also controls, so `__all__` would be a second list to keep in step with the code. A
  library's public modules declare `__all__`, since its users and `pydoc` read the public API
  from it.
- **A name the standard library or a framework gives keeps its spelling**: `setUp` in `unittest`,
  `do_GET` in `http.server`, `formatMessage` in `logging`.
  [python.md](../../python/language/python.md) section 3 says when such a method takes
  `@override`. `setUp` and `tearDown` need no mark: ruff's default `ignore-names` lists them. Any
  other name a framework gives that the parent class does not define, such as `do_EOF` on a
  `cmd.Cmd` shell, goes in `lint.pep8-naming.extend-ignore-names` with a comment that says why.
  List each name the code defines, such as `"do_EOF"`. Do not use a glob such as `"do_*"`: it would
  exempt every `do_` name in the repository.
- **The checks.** ruff's `N` rules check the case of a class, a function, a method, a variable and
  a parameter, `self` and `cls`, and a module's name. No rule this practice selects checks an
  acronym in capitals, a type variable, a module-level constant, the leading underscore or a name
  that clashes with a keyword: review checks those rows. `PYI042` flags a type alias, written with
  `TypeAlias` or as a `type` statement, whose name starts with a lower-case letter after at most one
  leading underscore, such as `money`, `orderLines` or `_money`. Any other alias name that is not
  `CapWords`, such as `MONEY`, `Order_Lines` or `__money`, and an alias written as a plain
  assignment are review. `E741`, `E742` and `E743` flag `l`, `O` and `I`. `N806` also flags a name a
  domain writes in capitals inside a function, such as a matrix `X`: list such names in
  `lint.pep8-naming.extend-ignore-names`, with a comment that says why. `N818` asks for the `Error`
  suffix; an exception that is not an error, such as one that only ends a loop, gets `# noqa: N818`
  with that reason ([static-checks.md](../../python/static-checks/static-checks.md) section 6).
  Whether a name says what the business means, the rest of this section, is review.

## 8. Layout: one formatter decides it

When you write or change code, let the project's formatter lay it out: run it before every
commit, and in review never argue about a choice the formatter makes. When the formatter has a
line length, it is the width of every line, comments and docstrings included; only a line that holds
a long string, or a comment or docstring line that ends with a URL, may run past it (below).

- **Why one tool decides.** A layout that changes from file to file makes a reader work out the
  shape before the meaning, and a review that argues about spaces has less time for what the code
  does. Google's Python guide notes that teams use a formatter "to avoid arguing over formatting".
- **What the formatter leaves to you:** the blank lines between the stages of a body (section 5),
  the width of comments and docstrings, since a formatter does not rewrap prose, and long strings,
  which it never splits.
- **One width for every line.** A comment or a docstring wraps at the formatter's line length, like
  the code, so one number is the width of every line and one ruler in the editor shows it.
- **A string stays whole.** Do not split a log message or an error text in code, or a URL in code
  or in a comment, to fit the width: the split text no longer turns up when someone searches for
  it. The Linux kernel's coding style never breaks a user-visible string for the same reason. A
  message built from several fields may break between two fields, as long as each fixed phrase
  stays whole. The formatter leaves a long string as it is.

**Python case.** The formatter is `ruff format`, which writes Black's style. Black "follows PEP 8
in spirit and enforces a consistent subset of its formatting recommendations", in its own words,
such as two blank lines around a top-level function or class and one between methods. The line
length stays at the formatter's default, 88, and the width departs from PEP 8 in two ways, which
[python.md](../../python/language/python.md) section 6 lists. The first is one width, 88, for code
and for comments and docstrings. PEP 8 asks for 79, and allows up to 99 for a team that agrees on
it only while comments and docstrings stay at 72, which this practice does not keep. Black chose
88 because it "was found to produce significantly shorter files than sticking with 80 (the most
popular), or even 79 (used by the standard library)". Prose takes the same width so that one
number holds every line: the formatter's line length for code, and `W505` at the same length for
comments and docstrings on lines of their own. PEP 8 limits the width so that several files, or
the two columns of a review tool, fit side by side. PEP 8 itself accepts a code window up to 99
for a team; 88 needs a narrower one, and prose at 88 asks for no wider window than the code
already sets. What it gives up is the shorter line PEP 8 keeps for "flowing long blocks of text".
The alternative that stays inside PEP 8, code at 88 and prose at 72, puts two widths in one file,
and since `W505` counts the indentation, a docstring inside a method would keep about 64 columns
of text. The second is that a line that holds a long string, or a comment or docstring line that
ends with a URL, may run past the width, where PEP 8 makes no such exception. The reason is the
"A string stays whole" bullet above: a split string no longer turns up in a search. Against
PEP 8's reason, such a line overflows the side-by-side window on that one line only.
ruff checks what the formatter leaves:

- **Imports are laid out by tools too.** One module per import line, every import at the top of
  the file after the module docstring, in three groups with a blank line between them: the
  standard library, third-party packages, then the application's own modules. The reader then
  finds every dependency of the file in one place and sees which ones are the application's.
  ruff's `I001` sorts them into the groups, and `E401` and `E402` flag two modules on one line and
  an import below code. No wildcard import, `from module import *`: PEP 8 says it makes "it
  unclear which names are present in the namespace, confusing both readers and many automated
  tools", and ruff's `F403` flags it. Imports are absolute
  ([file-structure.md](../file-structure/file-structure.md) section 7).
- **`W505`, with `lint.pycodestyle.max-doc-length = 88`,** checks every comment on a line of its own
  and every docstring line. It skips a line that ends with a URL, as long as the URL starts within
  the width. ruff counts `W505` among the rules a formatter makes redundant, but its formatter never
  wraps prose, so here it is the only check on that width.
- **`E501`, the line-length rule, stays off.** The formatter "only makes a best-effort attempt to
  wrap lines", ruff's documentation says, so `E501` fires on the lines this section keeps whole,
  such as a long string. A long comment after code, on the same line, is checked by neither
  `W505` nor the formatter; review catches it.
- **No line inside a multi-line string ends in whitespace the program needs.** PEP 8's reason:
  "Such trailing whitespace is visually indistinguishable and some editors (or more recently,
  reindent.py) will trim them." Where the program needs it, write it as an escape, such as `\x20` or
  `\t`. The `trailing-whitespace` hook in
  [setup-example.md](../../python/static-checks/setup-example.md) section 2 is the check: it strips
  such whitespace, inside a string too, and fails the commit that had it.
- **The pycodestyle rules on whitespace, indentation and blank lines (`E1`, `E2`, `E3`) stay
  off.** All but `E101` are still in preview in ruff 0.16, and the formatter already writes what
  they check, apart from a comment that opens with `##`, `#!`, `#:`, `#'` or `#|`: the formatter
  keeps it as written, where `E262`, `E265` or `E266` would flag it, so review checks it
  (section 4).
- **`D206` and `D300` stay off,** and `E701`–`E703` stay quiet: they check a docstring's
  indentation and quotes and one statement per line, which the formatter already writes. ruff's
  formatter documentation lists `D206` and `D300` among the rules to avoid beside it.

How the formatter and the checks run is [static-checks.md](../../python/static-checks/static-checks.md)
sections 2 and 4.

## 9. Where it stops holding

- **Code no change touches.** It stays as it is until a change edits it
  ([refactoring.md](../refactoring/refactoring.md) section 2).
- **A script run once, a notebook, a spike.** Section 6 is ceremony there. Sections 2 to 5, 7
  and 8 still pay for themselves, since someone will read it again.
- **A shape a framework requires**, such as the signature of a pytest fixture or a view the
  framework calls, keeps the framework's names and form.
- **A name another practice fixes**, such as the boolean setting `disable_prompt_cache` of
  [prompt-engineering.md](../prompt-engineering/prompt-engineering.md) section 17, keeps that name,
  though section 7 asks a boolean to read as a question: every code base that follows that
  practice then calls the switch by one name.

## 10. Review checklist

A review question per section. A single red flag is something to raise with the author, not a
demand to rewrite; when a unit the change wrote or edited shows two or more, that unit is not ready.

| Section | Ask | Red flag |
|---|---|---|
| 2. One job per unit | Can I say what it does in one sentence, without "and"? | The name needs "and", or is too general to finish the sentence; the body mixes steps with the details of one step |
| 3. Guard clauses | Does the main path run at the first indentation level? | The real work sits inside two or more nested `if`s, or in the last `else` |
| 4. Comments say why | Does each comment give a reason the code cannot? | A comment repeats the line below; a tricky line has none |
| 5. Blank lines | Can I see the stages before reading a line? | A multi-stage body with no blank line; a blank line inside a stage |
| 6. Every input in the signature | Can a test call it with plain values? | Below the adapter, the unit reads the clock for anything but a duration it only logs or reports as a metric; it reads `os.environ` or a module-level client, or builds an object it calls |
| 7. Names from the business | Would someone who knows the business understand each name? | `data`, `record`, `manager`; two names for one concept |
| 8. Layout | Did the formatter make every choice it can, and do the lines it leaves meet section 8? | A hand-made layout the formatter would undo; a comment or docstring line over the line length that does not end with a URL; a fixed phrase split to fit the width |

## 11. Sources

Robert C. Martin, *Clean Code* (2008): chapter 1 on the ratio of reading to writing, chapter 3
("Functions", do one thing, one level of abstraction), chapter 5 ("Formatting", vertical openness
between concepts); "The Open-Closed Principle" (1996) and "The Dependency Inversion Principle"
(1996). Kent Beck, *Smalltalk Best Practice Patterns* (1997): Composed Method and Guard Clause.
Martin Fowler, the refactoring catalog: Replace Nested Conditional with Guard Clauses. Bertrand
Meyer, *Object-Oriented Software Construction* (1988), the open-closed principle. Eric Evans,
*Domain-Driven Design* (2003), chapter 2, "Communication and the Use of Language". Gary
Bernhardt, "Functional Core, Imperative Shell" (2012). Brandon Rhodes, "Hoist Your I/O" (PyWaw
2015). PEP 8 (blank lines, comments, imports, naming conventions, maximum line length,
programming recommendations), PEP 257 (docstrings), PEP 484, "Type Hints" (its "Type aliases"
section), and PEP 544 (protocols); the mypy documentation on protocols and structural subtyping.
Black's code style
([black.readthedocs.io](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html#line-length):
"follows PEP 8 in spirit", "Line length", "Empty lines") and ruff's formatter
documentation: its deviations from Black and its "Conflicting lint rules"; ruff's rules `RET505`,
`RET506`, `ERA001`, `E101`, `E401`, `E402`, `E501`, `E701`–`E703`, `E712`–`E714`, `E741`–`E743`,
`F403`, `I001`, `PYI042`, `W505`, the pycodestyle `E1`, `E2` and `E3` groups, the `D` rules with
the `pep257` convention, `D205`, `D206`, `D300` and `D401` among them, and the `N` rules, `N806` and
`N818` among them, with `N802`'s exemption for `@override` (ruff 0.16.10). The Google Python Style
Guide, on formatters and on docstring style (section 3.8.3). The Linux kernel coding style
(`Documentation/process/coding-style.rst`), on user-visible strings. Hofmeister, Siegmund and
Holt, "Shorter identifier names take longer to comprehend" (SANER 2017); Lawrie, Morrell, Feild
and Binkley, "What's in a name? A study of identifiers" (ICPC 2006). MDN Web Docs, "Code style
guide" (last modified 2026-09-14), and the Microsoft Writing Style Guide, "Code examples", on
comments in code that readers copy.
