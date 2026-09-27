# Example: from `order: dict` to `order: PaidOrder`

A worked before-and-after for [python.md](python.md) section 2. The system takes an order
from a payment provider over a webhook, and several modules each do their own job with it. Names
are invented.

## Before: the rules live in people's heads

The payload arrives as a `dict` and stays a `dict` all the way down.

`payments/webhook.py`

```python
def handle(request_body: str) -> None:
    order = json.loads(request_body)
    store.save(order)
    invoice.issue(order)
    receipt.send(order)
```

`billing/invoice.py`

```python
def issue(order: dict) -> None:
    if "currency" not in order:
        raise ValueError("order has no currency")
    net = order["amount_minor"] / 100
    tax = us_tax(net) if order["currency"].upper() == "USD" else eu_tax(net)
    ledger.write(order["order_id"], net, tax)
```

`billing/refund.py`

```python
def refund(order: dict) -> None:
    if order["currency"].upper() == "USD":
        gateway.refund_usd(order["amount_minor"])
    else:
        gateway.refund_eur(order["amount_minor"])
```

`reporting/daily.py`

```python
def total(orders: list[dict]) -> float:
    return sum(o["amount_minor"] / 100 for o in orders)
```

`reporting/export.py`

```python
def rows(orders: list[dict]) -> list[str]:
    return [f'{o["order_id"]},{o["amount_minor"]}' for o in orders]
```

`notifications/receipt.py`

```python
def send(order: dict) -> None:
    if order.get("paid_at") is None:
        return
    paid_at = datetime.fromisoformat(order["paid_at"])
    mailer.send(order["email"], f"Paid on {paid_at:%d %B %Y}")
```

### Three constraints, and not one of them is written down

1. **`amount_minor` is in minor units.** The key says so, and a `dict` key is a name, not a
   rule: nothing stops `daily.total`, which divides by 100, and `export.rows`, which does not,
   from meaning different things by it. Both are right today, and whoever reads the value next
   picks a meaning.
2. **`currency` is one of the two codes the gateways handle.** Nothing in `str` says which two,
   and nothing at the door turns a third away: a payload carrying `"GBP"` reaches `refund` and
   takes the EUR branch.
3. **`paid_at` is `null` unless the order is paid.** Only `receipt.send` reads it, and guards it;
   an unpaid payload is still saved and invoiced, because nothing else knows to look. The author
   of the next module has to know to write that guard, and nothing in `dict` tells them.

Every guard is right. The rules still live in people's heads, and the next module gets them
from memory or not at all.

## After: the rule is in the type every signature past the webhook names

Eight files, the same six jobs: the two new ones hold the type and the parser. What moved is
where each rule is written.

`orders/model.py`

```python
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum, unique


@unique
class Currency(Enum):
    # Not StrEnum: that would make Currency.USD == "USD" true, so a caller could keep
    # passing the wire string around and never notice the type.
    USD = "USD"
    EUR = "EUR"


class MixedCurrency(Exception):
    """Two Money values in different currencies were combined."""


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: Currency

    @classmethod
    def from_minor_units(cls, minor: int, currency: Currency) -> "Money":
        # Every member of Currency has two decimal places; that is what licenses the / 100.
        return cls(Decimal(minor) / 100, currency)

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency is not self.currency:
            raise MixedCurrency(f"{self.currency.value} + {other.currency.value}")
        return Money(self.amount + other.amount, self.currency)


@dataclass(frozen=True, slots=True)
class PaidOrder:
    """An order the provider has confirmed as paid.

    Holding one means the payment went through. No caller has to
    handle an unpaid order. Its fields are the ones this system
    uses, not the ones the provider sends; today they happen to
    match.
    """

    order_id: str
    email: str
    total: Money
    paid_at: datetime
```

`payments/provider.py`

```python
import json
from datetime import datetime

from orders.model import Currency, Money, PaidOrder


class InvalidPayload(Exception):
    """The provider sent something this code cannot turn into a PaidOrder."""


_FIELDS = (("order_id", str), ("email", str), ("currency", str),
           ("paid_at", str), ("amount_minor", int))


def parse_paid_order(body: str) -> PaidOrder:
    """The only place a provider payload becomes a PaidOrder.

    Every way out of this function is a PaidOrder or an InvalidPayload.
    """
    try:
        payload = json.loads(body)
        if not isinstance(payload, dict):
            raise InvalidPayload("the payload is not a JSON object")
        if payload.get("status") != "paid":
            raise InvalidPayload("status is not paid")
        for field, kind in _FIELDS:
            # type(...) is, not isinstance: a bool is an int, and must not pass for one.
            if type(payload[field]) is not kind:
                raise InvalidPayload(f"{field} must be {kind.__name__}")
        if payload["amount_minor"] < 0:
            raise InvalidPayload("amount_minor is negative")
        paid_at = datetime.fromisoformat(payload["paid_at"])
        if paid_at.tzinfo is None:
            raise InvalidPayload("paid_at has no time zone")
        return PaidOrder(
            order_id=payload["order_id"],
            email=payload["email"],
            total=Money.from_minor_units(
                payload["amount_minor"], Currency(payload["currency"].upper())
            ),
            paid_at=paid_at,
        )
    except InvalidPayload:
        raise
    except (KeyError, ValueError, RecursionError) as exc:
        raise InvalidPayload(repr(exc)) from exc
```

`payments/webhook.py`

```python
from billing import invoice
from notifications import receipt
from payments.provider import InvalidPayload, parse_paid_order


def handle(request_body: str) -> None:
    try:
        order = parse_paid_order(request_body)
    except InvalidPayload as exc:
        log.warning("rejected webhook: %s", exc)
        return
    store.save(order)
    invoice.issue(order)
    receipt.send(order)
```

`billing/invoice.py`

```python
from orders.model import Currency, PaidOrder


def issue(order: PaidOrder) -> None:
    net = order.total.amount
    # A member added to Currency later stops at case _, instead of taking the EUR branch.
    match order.total.currency:
        case Currency.USD:
            tax = us_tax(net)
        case Currency.EUR:
            tax = eu_tax(net)
        case _:
            raise NotImplementedError(f"no tax rule for {order.total.currency.value}")
    ledger.write(order.order_id, net, tax)
```

`billing/refund.py`

```python
from orders.model import Currency, PaidOrder


def refund(order: PaidOrder) -> None:
    match order.total.currency:
        case Currency.USD:
            gateway.refund_usd(order.total)
        case Currency.EUR:
            gateway.refund_eur(order.total)
        case _:
            raise NotImplementedError(f"no gateway for {order.total.currency.value}")
```

`reporting/daily.py`

```python
import operator
from decimal import Decimal
from functools import reduce

from orders.model import Currency, Money, PaidOrder


def total(orders: list[PaidOrder], currency: Currency) -> Money:
    """One currency per report: the caller says which, and a mixed list raises."""
    return reduce(operator.add, (o.total for o in orders), Money(Decimal(0), currency))
```

`reporting/export.py`

```python
from orders.model import PaidOrder


def rows(orders: list[PaidOrder]) -> list[str]:
    return [f"{o.order_id},{o.total.amount},{o.total.currency.value}" for o in orders]
```

`notifications/receipt.py`

```python
from orders.model import PaidOrder


def send(order: PaidOrder) -> None:
    mailer.send(order.email, f"Paid on {order.paid_at:%d %B %Y}")
```

### What changed

- **The allowed currencies are a set a signature names.** `refund` takes a `PaidOrder` and
  compares `order.total.currency` with a `Currency` member. `Currency("GBP")` raises
  `ValueError` inside `parse_paid_order`, which leaves the function as `InvalidPayload`, so the
  webhook logs and returns before `store.save` runs.
- **No path through the parser builds an unpaid order.** `paid_at: datetime` is not optional, and
  `parse_paid_order` rejects a payload whose status is not `paid`, and a timestamp with no time
  zone. `receipt.send` has nothing left to guard against.
- **The unit and the currency travel together.** `Money` carries both, so `daily.total` cannot
  add dollars to euros: `Money.__add__` raises `MixedCurrency` instead of returning a number.
  `export.rows` writes `o.total.amount` and `o.total.currency.value` from the same object.
- **Every call site names what it needs in its own signature.** `issue`, `refund` and `send` take
  a `PaidOrder`; `total` and `rows` take a `list[PaidOrder]`. None of them re-states a rule; each
  names the type that carries it.
- **A test builds a `PaidOrder` by satisfying its fields.** There is no payload to fake and no
  validator to patch out.

### What this example does not claim

- **`datetime` does not say whether it carries a time zone.** The field type takes a naive value
  as readily as an aware one; only the check in `parse_paid_order` keeps naive ones out. Two
  payloads for the same instant print different days; ordering the two shapes raises `TypeError`,
  and `==` quietly answers `False`.
- **A boundary is only a boundary if every path out of it raises something the caller names.**
  `parse_paid_order` checks each field first, so it knows which exceptions its own body can
  raise, and turns those into `InvalidPayload`. Catching `Exception` instead would report a typo
  in this function as the provider's bad data, and the webhook would answer 2xx to an order it
  dropped. An `except` tuple in `handle` would be the same scattered rule in a new place.
- **`frozen=True` is what keeps a valid object valid.** Drop it and any module can assign
  `order.total = "5 USD"`, which ends the guarantee at construction and puts you back where the
  first version was.
- **Where the type lives is a second decision.** `Currency`, `Money` and `PaidOrder` sit in a
  module that imports no wire format; `parse_paid_order` imports them. That is why `billing` and
  `reporting` never import `payments`, and why a second way an order can arrive needs a second
  parse function and no change to the type.
- **`Money` has a price of its own.** `Money.from_minor_units` divides by 100 because every
  member of `Currency` has two decimals; a currency with a different exponent has to change that
  function. And `daily.total` takes the report's currency as a parameter, because a day's orders
  can carry two, and adding them is the one thing `Money` refuses to do. `Money` also moves the
  amount off `float`; that is a separate rule, not this one.
- **Different things enforce different fields here.** The `Currency(...)` call, the field checks
  in `parse_paid_order`, `Money.__add__`'s currency check and `frozen=True` are enforced by
  CPython when the code runs. The field types on `PaidOrder` and `Money` are enforced by whatever
  type checker your CI runs and fails on, and by nothing at all if it runs none — so nothing at
  runtime stops a caller who builds a `Money` from a `float`, or a `PaidOrder` that never went
  through `parse_paid_order`.
