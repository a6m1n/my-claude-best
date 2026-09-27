# Readability rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. One job per unit](#2-one-job-per-unit)
- [3. Guard clauses: the main path stays flat](#3-guard-clauses-the-main-path-stays-flat)
- [4. Comments say why](#4-comments-say-why)
- [5. Blank lines between stages](#5-blank-lines-between-stages)
- [6. Every input in the signature](#6-every-input-in-the-signature)
- [7. Names from the business](#7-names-from-the-business)
- [8. Where it stops holding](#8-where-it-stops-holding)
- [9. Review checklist](#9-review-checklist)
- [10. Sources](#10-sources)

## 1. Purpose and the one rule

This file is for everyone who writes or reviews code: people and AI agents alike. Read it before
you write or change a function or a class, and when you review one.

It is about how code reads inside a file: what one unit does, how its body flows, and what its
names and comments say. Where a file sits and what it is called is
[file-structure.md](../file-structure/file-structure.md). Where a business decision and its rule
live, and how a type carries a constraint, is [python.md](../python/python.md) section 2. The
examples are Python; the principles hold in any language. Each example shows the smallest piece
that makes its point, a line, a function, or a function and its test, and leaves out its imports
and the types and functions it calls. [module-example.md](module-example.md) shows a whole module.

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
  goes. Where a split stops paying is [python.md](../python/python.md) section 2, condition 5.

How jobs split into files is [file-structure.md](../file-structure/file-structure.md) section 3;
which function holds a business decision and which only acts is
[python.md](../python/python.md) section 2.

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
# Good: the same flow, with each detail in a function named for it. The body
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
  value is the business decision [python.md](../python/python.md) section 2 describes, not a
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
                raise InvalidDiscountCode("only letters and digits")
        else:
            raise InvalidDiscountCode(f"must have {CODE_LENGTH} characters")
    else:
        raise InvalidDiscountCode("empty")
```

```python
# Good: the same checks as guards. Each error sits next to its condition, and
# what is left at the end is the main path, at the first level.
def parse_discount_code(raw: str) -> DiscountCode:
    code = raw.strip().upper()

    if not code:
        raise InvalidDiscountCode("empty")

    if len(code) != CODE_LENGTH:
        raise InvalidDiscountCode(f"must have {CODE_LENGTH} characters")

    if not code.isalnum():
        raise InvalidDiscountCode("only letters and digits")

    return DiscountCode(code)
```

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
- **The code as it is now.** Change a comment in the same edit as the line it describes. A
  comment that describes old behavior is worse than none, because the reader believes it.

What to delete:

- **A comment that repeats the line below it.** Delete it, or rename until it is not needed. It
  adds nothing, and it goes stale at the next change.
- **Commented-out code.** Git keeps the old version, and ruff's `ERA001` flags the lines.

Where other text goes:

- **The story of a change goes in the commit message**, not in the code. A note such as "moved
  to X, since Y took too long" helps whoever reviews that diff ([git.md](../git/git.md) section
  3). The next reader of the code needs the constraint, not the story of the diff.
- **What the caller needs goes in the docstring.** A docstring is for the caller and says what
  the function does, returns and raises (PEP 257); a `#` comment is for the maintainer and says
  why the body is the way it is.

PEP 8 draws the same line with one pair of examples: `x = x + 1  # Compensate for border`, not
`# Increment x`.

```python
# Bad: the comment repeats what the line already says. It adds nothing, and it
# goes stale when the value changes.

# Timeout for the provider, in seconds.
PROVIDER_TIMEOUT_SECONDS = 25
```

```python
# Good: the same line, and the comment now carries the one fact the line cannot
# show: why 25. Without it, the next editor may raise it to "give the provider
# more time".

# The provider's gateway drops a connection after 30 seconds; stopping at 25
# lets us return our own error instead of a dropped connection.
PROVIDER_TIMEOUT_SECONDS = 25
```

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
  boundary, a guard included; that is this practice's own choice. It keeps PEP 8's other half:
  never a blank line inside a stage, where it splits what belongs together.
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
- **A formatter keeps these lines but never adds them.** Black and ruff format keep a single blank
  line inside a function and collapse several into one; ruff format also removes a blank line at
  the very start of a block. So the rule lives in review, not in a tool.

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
# Good: the same lines, split at each stage: load, decide (act, then return),
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

- **Time.** The adapter reads the clock once per request and passes `today` to the use case,
  which passes it to the rule. A rule always takes the value, never a clock
  ([python.md](../python/python.md) section 2). A use case or a doer that needs the time more than
  once in one call takes a clock, built once by the adapter and passed in like a client.
- **Randomness.** Take the value, or a `random.Random` the caller seeds, so a test can fix it.
- **Settings.** Read them once at startup
  ([file-structure.md](../file-structure/file-structure.md) section 4) and pass the values in.
  A function that reads `os.environ` has an input no caller can see.
- **Computation apart from input and output.** A function that computes a value and then saves
  it cannot be tested without the save. Which function computes and which acts is
  [python.md](../python/python.md) section 2.
- **Objects the unit calls come in the same way.** A store or a sender is passed in like a
  client ([python.md](../python/python.md) section 2): the unit never builds one, and the adapter
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


def test_card_expiring_within_notice_needs_update() -> None:
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
  `test_needs_card_update_2`.
- **Generic words say nothing on their own**: `data`, `info`, `item`, `record`, `obj`, `value`,
  `manager`, `processor`, `handler`. File names follow the same rule in
  [file-structure.md](../file-structure/file-structure.md) section 7.
- **A boolean reads as a yes-or-no question**: `is_paid`, `has_items`, `needs_manual_review`.
- **A number whose type does not carry its unit carries it in the name**: `timeout_seconds`,
  `amount_cents`.
- **No abbreviation a newcomer has to decode**: `customer_address`, not `cust_addr`. Short forms
  everyone knows, such as `id`, `url` and `html`, stay.

```python
# Bad: generic names. `compute_value`, `entry` and `days` say nothing about
# the business: the reader has to read the body, and know the business, to
# learn that this is a late fee.
def compute_value(entry: Entry, days: int) -> Decimal:
    if days <= GRACE_DAYS:
        return Decimal("0")

    return entry.amount * DAILY_RATE * (days - GRACE_DAYS)
```

```python
# Good: the same body in the business's words. The signature alone says what
# the function answers, and a finance colleague can check the formula.
def late_fee(invoice: Invoice, days_overdue: int) -> Decimal:
    if days_overdue <= GRACE_DAYS:
        return Decimal("0")

    return invoice.amount * DAILY_LATE_FEE_RATE * (days_overdue - GRACE_DAYS)
```

## 8. Where it stops holding

- **Code no change touches.** It stays as it is until a change edits it
  ([refactoring.md](../refactoring/refactoring.md) section 2).
- **A script run once, a notebook, a spike.** Section 6 is ceremony there. Sections 2 to 5
  and 7 still pay for themselves, since someone will read it again.
- **A shape a framework requires**, such as the signature of a pytest fixture or a view the
  framework calls, keeps the framework's names and form.

## 9. Review checklist

A review question per section. A single red flag is something to raise with the author, not a
demand to rewrite; when a unit the change wrote or edited shows two or more, that unit is not ready.

| Section | Ask | Red flag |
|---|---|---|
| 2. One job per unit | Can I say what it does in one sentence, without "and"? | The name needs "and", or is too general to finish the sentence; the body mixes steps with the details of one step |
| 3. Guard clauses | Does the main path run at the first indentation level? | The real work sits inside two or more nested `if`s, or in the last `else` |
| 4. Comments say why | Does each comment give a reason the code cannot? | A comment repeats the line below; a tricky line has none |
| 5. Blank lines | Can I see the stages before reading a line? | A multi-stage body with no blank line; a blank line inside a stage |
| 6. Every input in the signature | Can a test call it with plain values? | The unit reads the clock, `os.environ` or a module-level client, or builds an object it calls |
| 7. Names from the business | Would someone who knows the business understand each name? | `data`, `record`, `manager`; two names for one concept |

## 10. Sources

Robert C. Martin, *Clean Code* (2008): chapter 1 on the ratio of reading to writing, chapter 3
("Functions", do one thing, one level of abstraction), chapter 5 ("Formatting", vertical openness
between concepts); "The Open-Closed Principle" (1996) and "The Dependency Inversion Principle"
(1996). Kent Beck, *Smalltalk Best Practice Patterns* (1997): Composed Method and Guard Clause.
Martin Fowler, the refactoring catalog: Replace Nested Conditional with Guard Clauses. Bertrand
Meyer, *Object-Oriented Software Construction* (1988), the open-closed principle. Eric Evans,
*Domain-Driven Design* (2003), chapter 2, "Communication and the Use of Language". Gary
Bernhardt, "Functional Core, Imperative Shell" (2012). Brandon Rhodes, "Hoist Your I/O" (PyWaw
2015). PEP 8 (blank lines, comments), PEP 257 (docstrings) and PEP 544 (protocols); the mypy
documentation on protocols and structural subtyping. Black's code style ("Empty lines") and ruff's
formatter notes on its deviations from Black; ruff's rules `RET505`, `RET506` and `ERA001` (ruff
0.16).
