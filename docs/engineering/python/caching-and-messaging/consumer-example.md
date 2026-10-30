# Example: an idempotent RabbitMQ consumer

A worked example for [delivery.md](delivery.md) section 3 and
[message-brokers.md](message-brokers.md) section 9: a billing worker reads `OrderPlaced` from
RabbitMQ with aio-pika, charges each order once per event, and acknowledges each message only
after the PostgreSQL transaction that holds the charge has committed. Every name is a
placeholder.

**Navigation**

- [1. What it shows, and when you need it](#1-what-it-shows-and-when-you-need-it)
- [2. The files](#2-the-files)
- [3. Settings and the clients](#3-settings-and-the-clients)
- [4. The queues and the broker's policy](#4-the-queues-and-the-brokers-policy)
- [5. The event, parsed at the edge](#5-the-event-parsed-at-the-edge)
- [6. The use case: the event's id and the charge in one transaction](#6-the-use-case-the-events-id-and-the-charge-in-one-transaction)
- [7. The handler: ack after the commit, reject on failure](#7-the-handler-ack-after-the-commit-reject-on-failure)
- [8. The entry point](#8-the-entry-point)
- [9. The tests](#9-the-tests)
- [10. What this example does not claim](#10-what-this-example-does-not-claim)
- [11. Sources](#11-sources)

## 1. What it shows, and when you need it

A broker delivers a message at least once. A worker that crashes after its charge commits, but
before its acknowledgement, receives the same message again, and a plain handler then charges the
order twice ([delivery.md](delivery.md) section 2). This worker writes the event's id in the same
transaction as the charge, so a second copy changes nothing. It acknowledges a message only after
that transaction commits, so a crash never loses a charge ([delivery.md](delivery.md) section 3).

Use this shape when a consumer changes state in its own database for each message, such as a row
in a ledger. It is too much, or the wrong tool, in three cases:

- **The effect is already the same however often it runs**, such as a message that carries a
  whole new state the consumer writes over the old one. Drop the `processed_message` table and the
  use case's `if`; keep the acknowledgement after the commit and the two reject paths of section 7
  ([delivery.md](delivery.md) section 3).
- **The code that sends the work and the code that does it are one Python application.** Use a
  task queue, whose library acknowledges and limits the prefetch for you:
  [task-queues.md](task-queues.md).
- **The charge is a call to a payment provider, not a row in your database.** The id row and the
  call cannot share a transaction, so pass the event id to the provider as its idempotency key
  ([delivery.md](delivery.md) section 12).

Before this file, the orders module writes `OrderPlaced` to its outbox in the same transaction as
the order. The relay publishes each row to the topic exchange `acme.events` with the routing key
`orders.order_placed`, and with the event's id as the message id
([outbox-relay-example.md](outbox-relay-example.md)). This file starts when the message reaches
billing's queue. The two examples share one application, so the shared files are shown once:
where a block below cuts a part with `...`, it names the file that shows it.

The code is written for Python 3.13, the version
[setup-example.md](../static-checks/setup-example.md) pins. Its library calls were checked against
aio-pika 10.2.1 and aiormq 7.2.4 [1], [2], psycopg 3.3.6 [3], pydantic 2.14.2 [4] and
testcontainers 4.15.0 [5], the newest release of each on 2026-10-30. The broker is RabbitMQ 4.3
or later, the first series with delayed retry on quorum queues [6].

## 2. The files

Only the files this consumer touches. Every folder under `src/` and `tests/` has an empty
`__init__.py`; the tree leaves them out. `charge_order` is the module of the `billing` domain, as
`place_order` and `relay_outbox` are modules of the `orders` domain in
[outbox-relay-example.md](outbox-relay-example.md).

```text
<repo>/
├── .env.example                    gains ACME_BILLING_PREFETCH_COUNT
├── migrations/
│   └── 0002_create_processed_message_and_charge.sql   the two tables of section 6
├── pyproject.toml                  the import contracts gain the billing domain
├── scripts/
│   └── set_rabbitmq_policy_and_permissions.sh   billing's policy, the worker's rights
├── src/acme/
│   ├── core/
│   │   ├── config.py               Settings: gains billing_prefetch_count
│   │   ├── schemas.py              Currency, EventId, OrderId, RoutingKey: shared types
│   │   ├── database.py             connect_database, as outbox-relay-example.md shows it
│   │   └── rabbitmq_client.py      open_event_exchange, BROKER_ERRORS, as it shows them
│   ├── billing/
│   │   └── charge_order/
│   │       ├── schemas.py          ChargeOutcome
│   │       ├── errors.py           ChargeNotRecordedError
│   │       ├── repository.py       the claim of an event, and the charge row
│   │       └── usecase.py          ChargeOrder: both in one transaction
│   └── worker/
│       ├── schemas.py              OrderPlaced, as the worker parses it
│       ├── errors.py               ConsumerStoppedError: billing's consumer cannot go on
│       ├── handlers_charge_order.py   billing's queues, the loop, the handler of a message
│       └── main.py                 gains billing's consumer next to the relay
└── tests/
    ├── integration/
    │   ├── conftest.py             outbox-relay-example.md's; it empties billing's tables too
    │   └── charge_order/
    │       └── test_usecase.py     TestChargeOrder
    ├── support/
    │   ├── fake_charge_order.py    FakeChargeOrder
    │   └── builders_order_placed.py   an OrderPlaced body, and a delivery that carries it
    └── unit/
        ├── core/
        │   └── test_config.py      gains one test (section 9)
        └── worker/
            └── handlers_charge_order/
                ├── test_on_order_placed.py        TestOnOrderPlaced
                └── test_consume_order_events.py   TestConsumeOrderEvents
```

It is good because each file sits where
[file-structure.md](../../any-language/file-structure/file-structure.md) sections 3 to 5 put its
kind: the clients in `core/`, the use case and its queries in the module, and everything that
knows a RabbitMQ message in the `worker/` adapter, whose file is named for its role and its module.
Each error sits in the `errors.py` of the folder that raises it. The SQL lives in the module's
`repository.py`, so the adapter holds no query, and the module imports no broker library. The
broker's policy and the worker's rights are a script a person runs, so it sits in `scripts/`
(file-structure.md section 9). Billing is a second domain beside `orders`, so the same change
updates the import contracts of [layout-example.md](../../any-language/file-structure/layout-example.md)
section 3 in `pyproject.toml` (file-structure.md section 6, move 6): the layers contract's middle
layer becomes `"acme.orders : acme.billing"`, and the independence contract's `modules` list
gains `"acme.billing.*"`, so `lint-imports` checks billing's imports too. Each test file has the
path [layout.md](../testing/layout.md) section 3 gives it: the use case needs a database, so its
test is in `integration/charge_order/`. The two units of `handlers_charge_order.py` need nothing outside
Python, so their tests are in `unit/worker/`, in a folder named for the file, one file per unit
([layout.md](../testing/layout.md) section 4). The fake and the builders that both of those files
use sit in `support/` (layout.md section 7), and
`pytest tests/*/charge_order tests/*/*/*_charge_order*` runs all three test files.

## 3. Settings and the clients

The one field this worker adds to the application's `Settings` in `src/acme/core/config.py`. The
connection fields, `database_` and `rabbitmq_` with each password a `SecretStr` of its own, are
[outbox-relay-example.md](outbox-relay-example.md) section 4's; the class's `model_config`, its
validator and its other fields are [settings-example.md](../language/settings-example.md)'s. The
file's imports gain `Annotated` from `typing` and `Field` from `pydantic`.

```python
class Settings(BaseSettings):
    ...  # The fields of outbox-relay-example.md section 4 and settings-example.md

    # Never 0, which means no limit; small, so no waiting message nears the ack
    # timeout (message-brokers.md section 9).
    billing_prefetch_count: Annotated[int, Field(gt=0)] = 10
```

| Field | What it means | Set it when | Leave it out when |
|---|---|---|---|
| `billing_prefetch_count` | how many unacknowledged messages billing's consumer holds ([message-brokers.md](message-brokers.md) section 9) | the worker waits on the broker between messages (raise it), or a message waits near the ack timeout (lower it) | 10 fits: the handler takes milliseconds, and the worker charges one message at a time (section 7) |

It is good because the value comes in through the one class, read once at startup, and it is safe
in every environment, so it keeps a default ([python.md](../language/python.md) section 5). A
prefetch count of 0 stops the start instead of turning the limit off, because the rule sits on the
field.

The two clients are the shared ones of `core/`, built once by the worker's `main()`
([file-structure.md](../../any-language/file-structure/file-structure.md) section 4):

- `connect_database(host, port, name, user, password)` in `src/acme/core/database.py`, shown in
  [outbox-relay-example.md](outbox-relay-example.md) section 5. It opens the connection with
  `autocommit=True`, and the use case of section 6 depends on that: on an autocommit connection a
  `transaction()` block is a real transaction that commits when it ends, never a savepoint inside
  one nobody commits ([delivery.md](delivery.md) section 3).
- `src/acme/core/rabbitmq_client.py`: `connect_rabbitmq`, which opens one robust connection over
  TLS as the application's own user ([message-brokers.md](message-brokers.md) sections 5 and 15),
  `open_event_exchange`, which declares the durable topic exchange `acme.events`, and
  `BROKER_ERRORS`, the errors that mean the broker did not get what was sent. The last two are in
  [outbox-relay-example.md](outbox-relay-example.md) section 5.

## 4. The queues and the broker's policy

`src/acme/worker/handlers_charge_order.py`, first part: the imports of the whole file, its names,
and the function that declares billing's queues.

```python
"""The worker's way into charge_order: billing's queues and its message handler."""

import logging
from typing import Final

import aio_pika
from aio_pika.abc import (
    AbstractIncomingMessage,
    AbstractQueue,
    AbstractRobustConnection,
)
from pydantic import ValidationError

from acme.billing.charge_order.usecase import ChargeOrder
from acme.core.rabbitmq_client import BROKER_ERRORS, open_event_exchange
from acme.core.schemas import RoutingKey
from acme.worker.errors import ConsumerStoppedError
from acme.worker.schemas import OrderPlaced

logger = logging.getLogger(__name__)

# scripts/set_rabbitmq_policy_and_permissions.sh writes these names too; change them
# together.
BILLING_QUEUE: Final = "billing.order_placed"
BILLING_DEAD_LETTER_EXCHANGE: Final = "billing.dead-letter"
BILLING_DEAD_LETTER_QUEUE: Final = "billing.order_placed.dead-letter"


async def open_billing_queue(
    connection: AbstractRobustConnection, prefetch_count: int
) -> AbstractQueue:
    # A channel of its own: a channel is never shared (message-brokers.md section 5).
    channel = await connection.channel()
    # Per consumer, and never 0: aio-pika's default of 0 means no limit
    # (message-brokers.md section 9).
    await channel.set_qos(prefetch_count=prefetch_count)

    # Declared before the queue takes a message: under at-most-once, a message
    # dead-lettered to an exchange that does not exist yet is dropped; under the
    # policy's at-least-once, the queue keeps it and retries until the exchange exists.
    dead_letters = await channel.declare_exchange(
        BILLING_DEAD_LETTER_EXCHANGE,
        aio_pika.ExchangeType.FANOUT,
        # aio-pika defaults to False, and a lost exchange drops every dead letter
        # (message-brokers.md section 8).
        durable=True,
    )
    # No delivery limit or dead-letter target of its own, a departure from the check
    # of delivery.md section 6: this queue ends the path. Nothing consumes it, and a
    # person sends a dead letter back by publishing it again, never by rejecting it
    # with requeue; a dead-letter target here would loop. The cost: a message rejected
    # with requeue here is dropped at the broker's default limit.
    dead_letter_queue = await channel.declare_queue(
        BILLING_DEAD_LETTER_QUEUE,
        durable=True,  # Quorum queues are always durable; aio-pika defaults to False.
        arguments={"x-queue-type": "quorum"},  # A policy cannot set the type.
    )
    await dead_letter_queue.bind(dead_letters)

    events = await open_event_exchange(channel)
    queue = await channel.declare_queue(
        BILLING_QUEUE,
        durable=True,  # Quorum queues are always durable; aio-pika defaults to False.
        arguments={"x-queue-type": "quorum"},  # A policy cannot set the type.
    )
    # Only OrderPlaced reaches this queue's parser: the exchange is a topic
    # (message-brokers.md section 6).
    await queue.bind(events, routing_key=RoutingKey.ORDER_PLACED)

    return queue
```

It is good because both queues are durable quorum queues that survive the loss of a node and of
the worker ([message-brokers.md](message-brokers.md) section 7), and the dead-letter path exists
before the first message can need it. With at-most-once dead-lettering, RabbitMQ silently drops
a message dead-lettered to an exchange that does not exist yet [7]. With the at-least-once
strategy this queue's policy sets, the queue keeps such a message and retries until the exchange
exists [6], so here the order saves a wait, not a message. The dead-letter exchange is billing's
own fanout, so its one queue gets billing's dead letters and nobody else's. The consumer timeout
is written at its default in the policy below, so a reader can check the handler's longest run
against it ([message-brokers.md](message-brokers.md) section 9). The queue binds the `RoutingKey`
member the relay publishes `OrderPlaced` with, not a bare `str`
([python.md](../language/python.md) section 3).

The exchange is a topic because it carries more than one kind of event, the case
[message-brokers.md](message-brokers.md) section 6 gives a topic exchange. With a fanout,
billing's queue would also receive every other event the exchange carries, and its parser would
reject each one into the dead-letter queue.

The dead-letter exchange, the delivery limit, the delayed retry and the consumer timeout come from
a policy, not from queue arguments. RabbitMQ strongly advises against hardcoded arguments, which
"cannot be updated without redeploying applications and deleting the queue before it can be
redeclared" [7]. The change ships the policy, with the rights of the worker's broker user, in
`scripts/set_rabbitmq_policy_and_permissions.sh`. The broker's operator runs it with an
operator's credential, never the worker's, as the release step before the worker rolls out to a
virtual host, and again whenever the script changes. It takes the virtual host and the worker's
user as its two arguments. The order of the options is the one `rabbitmqctl` gives [10],
`--apply-to quorum_queues` is the form RabbitMQ's quorum-queue guide uses [6], and
`set_permissions` takes the configure, write and read patterns in that order [21]:

`scripts/set_rabbitmq_policy_and_permissions.sh`

```sh
#!/bin/sh
# Billing's queue policy and the worker's broker rights, on one virtual host.
# Run as the broker's operator: set_rabbitmq_policy_and_permissions.sh <vhost> <user>
# When: before the worker rolls out to a virtual host, and again whenever this policy
# changes.
# Then check: rabbitmqadmin --vhost <vhost> policies list_matching_object
#   --name billing.order_placed --type queues
# billing-order-placed must be the only matching policy at priority 10 or more.
set -eu

vhost="$1"
worker_user="$2"

# Priority 10 beats a broader policy left at the default of 0. The anchors keep the
# policy off billing.order_placed.dead-letter, whose name starts the same.
rabbitmqctl set_policy --vhost "$vhost" --priority 10 --apply-to quorum_queues \
    billing-order-placed '^billing\.order_placed$' \
    '{"dead-letter-exchange": "billing.dead-letter",
      "dead-letter-strategy": "at-least-once",
      "overflow": "reject-publish",
      "delivery-limit": 20,
      "delayed-retry-type": "failed",
      "delayed-retry-min": 10000,
      "delayed-retry-max": 200000,
      "consumer-timeout": 1800000}'

# Only the names the worker uses, as configure, write and read patterns. Configure
# lets the worker declare these names, and delete them too.
rabbitmqctl set_permissions -p "$vhost" "$worker_user" \
    '^(acme\.events|billing\.dead-letter|billing\.order_placed|billing\.order_placed\.dead-letter)$' \
    '^(acme\.events|billing\.order_placed|billing\.order_placed\.dead-letter)$' \
    '^(acme\.events|billing\.dead-letter|billing\.order_placed)$'
```

RabbitMQ applies one policy to a queue. Its guide says "At most one policy matches a queue or
exchange", and of the policies that match, "the one with the highest priority will take
effect" [20]. A broader policy with a higher priority would replace this one whole, so before the
worker first starts on a virtual host, check by hand which policies match billing's queue, with
rabbitmqadmin v2 [20]:

```sh
rabbitmqadmin --vhost "<vhost>" policies list_matching_object \
    --name "billing.order_placed" \
    --type "queues"
```

`billing-order-placed` must be the only matching policy at priority 10 or more: of policies with
equal priorities, RabbitMQ chooses the one in effect "undeterministically" [20]. An empty list
means that no policy on that virtual host matches the queue [20]: the script never ran there, or
the queue's name and the pattern differ.

What each policy key means, in general, is in [delivery.md](delivery.md) sections 5 and 6, and the
consumer timeout in [message-brokers.md](message-brokers.md) section 11. The values this worker
relies on:

| Key | Value here | Why this value | Leave it out when |
|---|---|---|---|
| `dead-letter-exchange` | `billing.dead-letter` | the exchange `open_billing_queue` declares; without it, a message over the limit is dropped ([delivery.md](delivery.md) section 6) | never ([delivery.md](delivery.md) section 6) |
| `dead-letter-strategy` | `at-least-once` | an event lost on its way to the dead-letter queue is an order nobody charges | never ([delivery.md](delivery.md) section 6) |
| `overflow` | `reject-publish` | at least once works only with `reject-publish`, and RabbitMQ also asks for the `stream_queue` feature flag in case it is not on [6] | the strategy is `at-most-once` ([delivery.md](delivery.md) section 6) |
| `delivery-limit` | `20` | RabbitMQ's default since 4.0, written out because the retries below count against it ([delivery.md](delivery.md) section 5) | never: the value the code relies on stays written down |
| `delayed-retry-type` | `failed` | it delays a message returned with `reject`, as section 7 returns a failed charge. It does not delay one returned with `nack`, as the queue iterator returns its buffered messages at shutdown, so those reach another worker at once [6] | the broker runs a series before 4.3, which has no delayed retry; [delivery.md](delivery.md) section 5 gives the older way |
| `delayed-retry-min` | `10000`, ten seconds | the wait is this minimum times the message's delivery count [6], so the waits grow by ten seconds each: 10 to 200 seconds over the 20 returns the limit allows, 35 minutes in all, long enough for a database restart | never while delayed retry is on: it is the wait itself |
| `delayed-retry-max` | `200000`, 200 seconds | ten seconds times the limit, the longest wait the values above give, written so that a later change to the limit or the minimum cannot stretch one wait | never ([delivery.md](delivery.md) section 6) |
| `consumer-timeout` | `1800000`, 30 minutes | RabbitMQ's default, written: a delivery held longer goes back to the queue, and the prefetch of section 3 keeps every message far below it ([message-brokers.md](message-brokers.md) section 9) | never ([message-brokers.md](message-brokers.md) section 11) |

It is good because the queue's whole failure path sits in one file the change ships, shown here
next to the code that depends on it: a body that does not parse goes to the dead-letter queue at
once, a failed charge comes back after a growing wait, and after 21 failed deliveries the
dead-letter queue takes the message for a person to look at. A message is dead-lettered when its
delivery count "exceeds this limit" [6], so a limit of 20 allows 20 delayed returns, and the 21st
failure ends the path.
The worker's rights name only what it declares, binds, publishes to and reads, because the
configure right lets a user delete what it may declare [21]. Where other applications publish to
`acme.events` too, give each producer user topic permissions on it
([message-brokers.md](message-brokers.md) section 15). The worker's user both publishes and binds,
so its write pattern names the keys the relay publishes, and its read pattern the keys billing
binds: binding keys "are checked against the topic permissions configured, if any" [21], and
RabbitMQ checks each one against the read pattern [26]. `set_topic_permissions` takes the user,
the exchange, then the write and the read pattern [25]. For this worker:

```sh
rabbitmqctl set_topic_permissions -p "$vhost" "$worker_user" acme.events \
    '^orders\.' '^orders\.order_placed$'
```

## 5. The event, parsed at the edge

The currency and the two ids are types that the orders module and billing both carry, so they sit
in `core/schemas.py` ([file-structure.md](../../any-language/file-structure/file-structure.md)
section 4), where neither module has to import the other. `RoutingKey` sits there too, because
`core/rabbitmq_client.py` names it (the same section). The file's other types and imports, the
`LogFormat` and `LogLevel` of [setup-example.md](../logging/setup-example.md), are left out.

`src/acme/core/schemas.py`

```python
from enum import StrEnum, unique
from typing import NewType
from uuid import UUID

# Two kinds of id the code passes side by side: NewType makes the checker refuse one
# passed for the other (python.md section 3).
EventId = NewType("EventId", UUID)
OrderId = NewType("OrderId", UUID)


# The currencies an order takes. Code and tests write its members by name, so the
# type is a StrEnum (python.md section 2).
@unique
class Currency(StrEnum):
    EUR = "EUR"
    USD = "USD"


# The key each event is published with. An event name is a closed set, never a bare
# str (python.md section 3).
@unique
class RoutingKey(StrEnum):
    ORDER_PLACED = "orders.order_placed"
```

It is good because the types both modules carry are declared once, in the one place each module
may import and neither has to import the other
([file-structure.md](../../any-language/file-structure/file-structure.md) section 4). The two ids
are `NewType`s, so the checker refuses an order id where an event id belongs, and the key is a
closed set, so a key outside it fails where it is parsed instead of reaching the broker
([python.md](../language/python.md) section 3).

`src/acme/worker/schemas.py`

```python
"""The messages the worker reads, each parsed once at the edge."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from acme.core.schemas import Currency, EventId, OrderId


class OrderPlaced(BaseModel):
    """OrderPlaced as billing reads it: the fields a charge needs."""

    model_config = ConfigDict(
        # The orders module owns this event and may add a field before billing knows
        # it; ignoring the field lets orders deploy first (python.md section 4,
        # delivery.md section 8).
        extra="ignore",
        frozen=True,
    )

    event_id: EventId
    order_id: OrderId
    # Minor units, such as cents. Strict: an amount of money is never coerced from a
    # string or a float (python.md section 4). The upper bound is a bigint's largest
    # value, so an amount the table cannot store fails here and is never retried.
    amount_minor: Annotated[int, Field(gt=0, le=9_223_372_036_854_775_807, strict=True)]
    currency: Currency
```

It is good because every rule the body must follow sits on the model, so a missing field, an
amount below one or above what the `charge` table stores, and a currency the shop does not take all
fail in one `ValidationError` at the edge ([python.md](../language/python.md) section 4), and no
field is a bare `str` for a closed set ([python.md](../language/python.md) section 3). The model is
billing's own, apart from the one the orders module publishes, because modules do not import each
other, so billing keeps its own copy
([file-structure.md](../../any-language/file-structure/file-structure.md) sections 2 and 6). The
producer's model forbids an unknown field; this one, which reads a format another party owns,
ignores it and says why at the line, as [python.md](../language/python.md) section 4's check asks
and [delivery.md](delivery.md) section 8 explains. That lets the producer add a field first, the
order [delivery.md](delivery.md) section 8's `FORWARD` mode deploys in. The event carries ids, an
amount and a currency, and no personal data ([delivery.md](delivery.md) section 10).

## 6. The use case: the event's id and the charge in one transaction

`migrations/0002_create_processed_message_and_charge.sql`, the two tables the use case writes.
The migration tool is left out, and so is the job that deletes old `processed_message` rows
([delivery.md](delivery.md) section 3, step 5).

```sql
-- One row per message a consumer has finished; written in the same transaction as
-- the side effect.
CREATE TABLE processed_message (
    consumer     text NOT NULL,
    message_id   uuid NOT NULL,
    processed_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (consumer, message_id)
);

-- One row per charge.
CREATE TABLE charge (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id     uuid NOT NULL,
    amount_minor bigint NOT NULL,
    currency     text NOT NULL,
    charged_at   timestamptz NOT NULL DEFAULT now(),
    -- Money is checked where it is stored too, not only at the edge
    -- (python.md section 2, "Where it stops holding", condition 4).
    CONSTRAINT charge_amount_is_positive CHECK (amount_minor > 0)
);
```

`src/acme/billing/charge_order/schemas.py`

```python
"""The types of charging an order."""

from enum import StrEnum, unique


# What one run did with one event. The use case and the tests write its members by
# name, so the type is a StrEnum (python.md section 2).
@unique
class ChargeOutcome(StrEnum):
    CHARGED = "charged"
    ALREADY_CHARGED = "already_charged"
```

`src/acme/billing/charge_order/repository.py`

```python
"""The queries of charging an order: the claim of an event, and the charge row."""

from typing import Final

from psycopg import AsyncConnection
from psycopg.rows import TupleRow

from acme.core.schemas import Currency, EventId, OrderId

# This consumer's key in processed_message: each consumer of an event keeps its own row
# (delivery.md section 3).
CONSUMER: Final = "billing.charge_order"


async def claim_event(conn: AsyncConnection[TupleRow], event_id: EventId) -> bool:
    """Record the event as processed; return False when this consumer has it already."""
    cursor = await conn.execute(
        "INSERT INTO processed_message (consumer, message_id) VALUES (%s, %s)"
        " ON CONFLICT DO NOTHING",  # A copy adds no row; the transaction stays usable.
        (CONSUMER, event_id),
    )

    return cursor.rowcount == 1


async def insert_charge(
    conn: AsyncConnection[TupleRow],
    *,
    order_id: OrderId,
    amount_minor: int,
    currency: Currency,
) -> None:
    await conn.execute(
        "INSERT INTO charge (order_id, amount_minor, currency) VALUES (%s, %s, %s)",
        (order_id, amount_minor, currency),
    )
```

`src/acme/billing/charge_order/errors.py`

```python
"""The error of a charge the database did not record."""

from acme.core.schemas import OrderId


class ChargeNotRecordedError(Exception):
    """The database refused the charge, so the event stays unprocessed."""

    def __init__(self, order_id: OrderId, *, sqlstate: str | None) -> None:
        super().__init__(f"Charge of order {order_id} was not recorded: {sqlstate}")
        self.order_id = order_id
        self.sqlstate = sqlstate
```

`src/acme/billing/charge_order/usecase.py`

```python
"""Charging an order: once for each event that asks for it."""

import psycopg
from psycopg import AsyncConnection
from psycopg.rows import TupleRow

from acme.billing.charge_order import repository
from acme.billing.charge_order.errors import ChargeNotRecordedError
from acme.billing.charge_order.schemas import ChargeOutcome
from acme.core.schemas import Currency, EventId, OrderId


class ChargeOrder:
    def __init__(self, conn: AsyncConnection[TupleRow]) -> None:
        # From connect_database, so autocommit: the block below is then a real
        # transaction, not a savepoint (delivery.md section 3).
        self._conn = conn

    @property
    def connection_closed(self) -> bool:
        """True once the connection is closed, after which every charge fails."""
        # psycopg reports a broken connection as closed too.
        return self._conn.closed

    async def run(
        self,
        *,
        event_id: EventId,
        order_id: OrderId,
        amount_minor: int,
        currency: Currency,
    ) -> ChargeOutcome:
        """Charge the order unless this event has charged it; return which happened."""
        try:
            # One transaction: the event's id and the charge commit together, or
            # neither does (delivery.md section 3).
            async with self._conn.transaction():
                # The body's event_id, a departure from delivery.md section 3, which
                # sends the id in a header so a copy is found without parsing the body:
                # the handler parses and checks the body first, so the model's id is
                # the checked one, and the header carries the same value. The cost: a
                # copy is found only after its body parses.
                if not await repository.claim_event(self._conn, event_id):
                    return ChargeOutcome.ALREADY_CHARGED

                await repository.insert_charge(
                    self._conn,
                    order_id=order_id,
                    amount_minor=amount_minor,
                    currency=currency,
                )
        except psycopg.Error as error:
            # From None: the database's error text can repeat the row it refused, the
            # event's values included (logging.md section 10).
            raise ChargeNotRecordedError(order_id, sqlstate=error.sqlstate) from None

        return ChargeOutcome.CHARGED
```

It is good because the id row and the charge run in one `transaction()` block, so a crash cannot
leave an id without its charge, which would skip the redelivered copy, or a charge without its id,
which would charge it again ([delivery.md](delivery.md) section 3). `ON CONFLICT DO NOTHING` tells
a copy by its row count and leaves the transaction usable, where a caught unique violation would
leave it failed. The queries live in `repository.py` and the `if` in `usecase.py`
([file-structure.md](../../any-language/file-structure/file-structure.md) section 3). That `if` is
the idempotency guarantee that [python.md](../language/python.md) section 2, "Where it stops
holding", condition 3 keeps inside the function, not a business rule, so no rule file asks it.
`run` returns which path it took, as a value of a closed set, and receives its connection instead
of reaching for one ([python.md](../language/python.md) section 2). The table's check on the
amount is the point-of-use check that section's condition 4 keeps for money, and the test of
section 9 uses it to make a charge fail. A database error leaves `run` as `ChargeNotRecordedError`,
raised `from None` with the SQLSTATE only, because PostgreSQL adds the row a check refused to the
error's detail, as "Failing row contains" and the row's values [22], and the handler of section 7
logs the error's traceback ([logging.md](../logging/logging.md) section 10). `connection_closed`
lets the handler tell a closed connection from a charge that failed once, and it reads `closed`
alone because psycopg's docs say "A broken connection is always closed" [23].

## 7. The handler: ack after the commit, reject on failure

`src/acme/worker/handlers_charge_order.py`, second part: the loop the entry point runs, and the
handler of one message.

```python
async def consume_order_events(queue: AbstractQueue, charge_order: ChargeOrder) -> None:
    """Settle the queue's messages one at a time; raise if the iterator ends."""
    # Written though it is aio-pika's default: the broker keeps each message until its
    # ack or reject (message-brokers.md section 9).
    async with queue.iterator(no_ack=False) as messages:
        # One at a time, never queue.consume(callback): that runs a handler per message
        # at once, and two charges on billing's one connection would share one
        # transaction.
        async for message in messages:
            try:
                await on_order_placed(message, charge_order)
            except BROKER_ERRORS:
                # A closed channel or a lost connection: the ack or reject never reached
                # the broker, which sends the message again, and the id row skips the
                # charge (message-brokers.md section 5). WARNING: the broker recovers
                # by itself, and someone should look at it (logging.md section 4).
                logger.warning(
                    "Order event unsettled: the broker did not get its ack or reject",
                    extra={"message_id": message.message_id},
                )

    # The iterator ends by itself only when its channel has not come back after a
    # reconnect: raise, so the task group stops the relay and the worker exits with an
    # error, to be restarted.
    raise ConsumerStoppedError("billing's queue iterator ended")


async def on_order_placed(
    message: AbstractIncomingMessage, charge_order: ChargeOrder
) -> None:
    """Charge the order a message names; ack it after the commit, or reject it."""
    # Ack and reject by hand, never message.process() (message-brokers.md section 9):
    # it rejects on any exception, cancellation included, then re-raises, and the
    # error is logged with the body in its text. Each path below settles the message
    # itself, which the tests of section 9 check.
    message_id = message.message_id

    try:
        # A message is outside data, parsed into a model once (python.md section 4).
        event: OrderPlaced | None = OrderPlaced.model_validate_json(message.body)
    except ValidationError:
        event = None

    if event is None:
        # INFO, with no traceback and not the error, whose text repeats the body: a body
        # that fails its model is an expected failure (logging.md sections 4 and 10).
        logger.info(
            "Order event rejected: its body does not parse",
            extra={"message_id": message_id},
        )

        # requeue=False: no retry can fix the body, so the dead-letter exchange takes it
        # at once (delivery.md section 5). Outside the except block: a reject that
        # failed inside it would carry the ValidationError, and the body in its text, as
        # its context (logging.md section 10).
        await message.reject(requeue=False)

        return

    try:
        outcome = await charge_order.run(
            event_id=event.event_id,
            order_id=event.order_id,
            amount_minor=event.amount_minor,
            currency=event.currency,
        )
    except Exception:  # Any failure of the charge gets the same answer: a retry.
        # WARNING, not ERROR: the broker sends the message again, and the alarm on the
        # dead-letter queue, not this line, calls a person (logging.md section 4).
        logger.warning(
            "Order event returned for a retry: charging order %s failed",
            event.order_id,
            extra={"message_id": message_id},
            # The traceback, at WARNING: logger.exception would log at ERROR. It also
            # keeps ruff's BLE001 quiet on the broad except.
            exc_info=True,
        )

        # requeue=True through reject, never nack: the delivery limit counts a reject,
        # and the queue's delayed retry spaces the attempts (delivery.md sections 5, 6).
        await message.reject(requeue=True)

        # A closed connection fails every charge after this one: stop the worker, so
        # that its restart opens a new connection.
        if charge_order.connection_closed:
            raise ConsumerStoppedError("billing's database connection is closed")

        return

    # After run() has committed: a crash before this line brings a redelivery that the
    # id row skips, never a lost charge (delivery.md section 3).
    await message.ack()

    logger.info(
        "Order event acknowledged for order %s",
        event.order_id,
        extra={"message_id": message_id, "outcome": outcome},
    )
```

The adapter's own error, in `src/acme/worker/errors.py`
([file-structure.md](../../any-language/file-structure/file-structure.md) section 5):

```python
"""The errors that end the worker, so that it is restarted."""


class ConsumerStoppedError(Exception):
    """Billing's consumer cannot go on; the worker exits with an error."""
```

It is good because a message is acknowledged only after `charge_order.run` returns, and that
return comes after the commit ([delivery.md](delivery.md) section 3). Each failure is settled
where it is handled and logged once there, with the message id and never the body
([logging.md](../logging/logging.md) sections 5 and 10, [delivery.md](delivery.md) section 9).
A body that does not parse goes to the dead-letter queue at once, because no retry can fix it. Any
other failure goes back through `reject`, which counts toward the delivery limit, while a `nack`
would not since RabbitMQ 4.3 ([delivery.md](delivery.md) section 6). A delayed retry then spaces
the attempts, so a database that is down for a few minutes costs waits, not dead letters. A
failure that no wait can cure ends the worker instead: when billing's connection reports closed
after a failed charge, the handler returns the message and raises `ConsumerStoppedError`, and so
does the loop when its iterator ends by itself. Either error leaves the task group of section 8,
which stops the worker with an error. `except Exception` is broad on purpose: whatever fails the
charge, the handler decides the same thing, and `exc_info=True` keeps the traceback. It does not
catch cancellation, since `asyncio.CancelledError` is a subclass of `BaseException` and not of
`Exception` [11], so a worker stopped mid-message leaves the message to the broker
([logging.md](../logging/logging.md) section 5). The loop catches `BROKER_ERRORS` around the
settle calls for the same reason the relay catches it around a publish: aiormq raises
`ChannelInvalidStateError` for an ack or a reject on a closed channel [12], and that error is not
an `AMQPError` ([outbox-relay-example.md](outbox-relay-example.md) section 5). It logs that case at
`WARNING`, as the relay logs a refused batch: the broker recovers by itself, and someone should
look ([logging.md](../logging/logging.md) section 4).

Three facts from the libraries shape the loop. aiormq starts a new task for each delivery [12],
so a callback given to `queue.consume` runs once per unacknowledged message at the same time, up
to the prefetch count. psycopg puts every cursor of one connection in one transaction: "All the
cursors that share the same connection will also share the same transaction" [13]. Two charges
in flight on billing's one connection would therefore commit together, and the first could be
acknowledged before the second had committed. The `async for` loop takes the next message only
after the handler returns, so the prefetched messages wait in the iterator. aio-pika's iterator
for a robust connection "survives channel reconnection" [14], and when it closes it returns its
buffered messages with a `nack` and `requeue=True` [15].

The handler settles each message by hand, as [message-brokers.md](message-brokers.md) section 9
asks. `process()` rejects the message when its block raises any exception, cancellation included,
and then lets the exception go on [16]. In this loop that exception would leave
`on_order_placed` and end the consumer task, because aio-pika's iterator only puts each delivery
in its buffer and runs no handler of its own [15]. The text of a pydantic `ValidationError`
carries the input it rejected ([python.md](../language/python.md) section 4), so the body would
reach the worker's crash trace, which [logging.md](../logging/logging.md) section 10 rules out.
For the same reason the handler rejects a body that does not parse after its `except` block: a
reject that failed inside it would carry the `ValidationError` as the broker error's context, and
any traceback of that error would print the body.

## 8. The entry point

`src/acme/worker/main.py` runs billing's consumer next to the outbox relay. `main()`, the file's
docstring, its imports, the `stop` event with its SIGTERM handler, the two connections `rabbitmq`
and `relay_database`, and the relay's own lines are
[outbox-relay-example.md](outbox-relay-example.md) section 8's, cut with `...`. The imports gain
`ChargeOrder` and the two functions of `handlers_charge_order.py`. This is billing's part of
`run_worker`:

```python
async def run_worker(settings: Settings) -> None:
    ...  # stop and its SIGTERM handler, rabbitmq and relay_database

    # Billing's own connection: a charge never runs inside the relay's transaction, nor
    # the relay's batch inside a charge (delivery.md section 3).
    billing_database = await connect_database(
        host=settings.database_host,
        port=settings.database_port,
        name=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
    )

    async with rabbitmq, relay_database, billing_database:
        queue = await open_billing_queue(rabbitmq, settings.billing_prefetch_count)

        async with asyncio.TaskGroup() as tasks:
            # A consumer that cannot go on raises: the group then cancels the relay and
            # raises too, so the worker exits with an error and is restarted.
            consuming = tasks.create_task(
                consume_order_events(queue, ChargeOrder(billing_database))
            )

            ...  # The relay, until SIGTERM sets stop: outbox-relay-example.md section 8

            # The relay returns once stop is set: cancel the consumer, which hands back
            # its buffered messages. A task group takes a cancelled task as done.
            consuming.cancel()
```

It is good because billing gets a database connection and a channel of its own, so no charge
ever runs inside the relay's transaction ([message-brokers.md](message-brokers.md) section 5).
Each client is built once and handed to what calls it: the connection to the use case, the use
case to the loop ([file-structure.md](../../any-language/file-structure/file-structure.md)
sections 4 and 5). The consumer runs as a task beside the relay. On SIGTERM the relay finishes
its batch and returns, and the consumer is cancelled; a task group treats a task cancelled from
outside as done, not as an error [17]. The group then ends normally, the iterator returns its
buffered messages, and leaving the `async with` closes the three connections. A batch whose
confirm the broker holds back under a resource alarm does not finish: the stop then ends with the
kill after the grace period, and the relay's transaction rolls back with its rows still in the
outbox ([outbox-relay-example.md](outbox-relay-example.md) section 11).
[images.md](../../any-language/docker/images.md) section 6 says what happens without a SIGTERM
handler: the container is killed ten seconds later, in the middle of a message. The consumer
also ends alone in one case: the iterator stops when the channel has not come back within 60
seconds of a reconnect [14]. A worker that went on relaying without consuming would charge
nothing and say nothing, so `consume_order_events` raises `ConsumerStoppedError` instead of
returning. A task that fails makes the group cancel the code in its block, the relay here, and
raise [17], so the worker exits with an error. `main()` logs that error at `CRITICAL` with its
traceback ([outbox-relay-example.md](outbox-relay-example.md) section 8), the line a restart's
alert reads, and a restart policy that acts on failure sees the exit.

## 9. The tests

No test here runs a real RabbitMQ, a departure from [message-brokers.md](message-brokers.md)
section 16 that section 10 declares with its reason and its cost.

The pytest configuration is the block of [running-tests.md](../testing/running-tests.md) section 1
with its three `asyncio_*` keys, because this code is async. Each test below was listed from the
guarantee before its body, and each names the edit that turns it red
([what-to-test.md](../testing/what-to-test.md) sections 1 and 4).

The use case reaches a database, so its tests run against a real PostgreSQL
([fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 3).
`tests/integration/conftest.py` is [outbox-relay-example.md](outbox-relay-example.md)
section 10's: one Postgres container per run with the application's tables, and a `database`
fixture whose connection comes from `connect_to`, which opens it with the application's own
`connect_database`, autocommit included. Billing changes one line of that fixture: its `TRUNCATE`
gains billing's two tables.

```python
        # Every table a test writes, billing's two included, so no test sees another's
        # rows (fixtures.md section 3).
        await conn.execute("TRUNCATE orders, outbox, processed_message, charge")
```

It is good because the suite keeps one `database` fixture, which empties every table it writes,
instead of a second copy here: "Two copies drift on the first edit to one of them"
([fixtures.md](../testing/fixtures.md) section 4).

`tests/integration/charge_order/test_usecase.py`

```python
"""Charging an order against a real database: once per event, all or nothing."""

import traceback
from typing import Final
from uuid import UUID

import pytest
from psycopg import AsyncConnection
from psycopg.errors import CheckViolation
from psycopg.rows import TupleRow

from acme.billing.charge_order.errors import ChargeNotRecordedError
from acme.billing.charge_order.usecase import ChargeOrder
from acme.core.schemas import Currency, EventId, OrderId

EVENT_ID: Final = EventId(UUID("6f1c2b9e-4d3a-4e8f-9b7c-1a2d3e4f5a6b"))
ORDER_ID: Final = OrderId(UUID("0c9d8e7f-6a5b-4c3d-8e2f-1a0b9c8d7e6f"))
AMOUNT_MINOR: Final = 4999


async def stored_charges(conn: AsyncConnection[TupleRow]) -> list[TupleRow]:
    """Return every charge as (order_id, amount_minor, currency), oldest first."""
    cursor = await conn.execute(
        "SELECT order_id, amount_minor, currency FROM charge ORDER BY id"
    )

    return await cursor.fetchall()


async def processed_events(conn: AsyncConnection[TupleRow]) -> list[TupleRow]:
    """Return the id of every message the database records as processed."""
    cursor = await conn.execute("SELECT message_id FROM processed_message")

    return await cursor.fetchall()


class TestChargeOrder:
    """Each event charges its order once; its id commits only with its charge."""

    async def test_an_event_charges_its_order(
        self, database: AsyncConnection[TupleRow]
    ) -> None:
        await ChargeOrder(database).run(
            event_id=EVENT_ID,
            order_id=ORDER_ID,
            amount_minor=AMOUNT_MINOR,
            currency=Currency.EUR,
        )

        assert await stored_charges(database) == [(ORDER_ID, AMOUNT_MINOR, "EUR")]

    async def test_a_second_copy_of_an_event_charges_nothing(
        self, database: AsyncConnection[TupleRow]
    ) -> None:
        """The broker sends a message again when its ack is lost in a crash."""
        charge_order = ChargeOrder(database)
        await charge_order.run(
            event_id=EVENT_ID,
            order_id=ORDER_ID,
            amount_minor=AMOUNT_MINOR,
            currency=Currency.EUR,
        )
        charges_after_the_first_copy = await stored_charges(database)

        await charge_order.run(
            event_id=EVENT_ID,
            order_id=ORDER_ID,
            amount_minor=AMOUNT_MINOR,
            currency=Currency.EUR,
        )

        assert await stored_charges(database) == charges_after_the_first_copy

    async def test_a_charge_the_database_refuses_leaves_the_event_unprocessed(
        self, database: AsyncConnection[TupleRow]
    ) -> None:
        """An id committed without its charge would make the broker's next copy skip
        the order, which would then never be charged.
        """
        # 23514 is PostgreSQL's SQLSTATE for a check violation, the table's check on
        # the amount. CheckViolation is listed so that the edit this test names fails
        # on match, not as an error (what-to-test.md section 4, step 5).
        with pytest.raises(
            (ChargeNotRecordedError, CheckViolation), match="23514"
        ) as caught:
            await ChargeOrder(database).run(
                event_id=EVENT_ID,
                order_id=ORDER_ID,
                amount_minor=0,
                currency=Currency.EUR,
            )

        assert await processed_events(database) == []
        # The traceback the handler logs, its chain included: only the database's own
        # text could put "Failing row" there (assertions.md section 6).
        logged = "".join(traceback.format_exception(caught.value))
        assert "23514" in logged
        assert "Failing row" not in logged
```

It is good because each test pins one guarantee, and each turns red on one plausible edit. The
first turns red when the charge is not written, the second when the `if` on the claimed id goes,
and the third when the `transaction()` block goes, because on an autocommit connection each
statement then commits alone ([test-structure.md](../testing/test-structure.md) sections 3 and 4).
The third also turns red when the use case lets the database's error out as it is, because that
error's text carries no SQLSTATE for `match=` to find, and when `from None` goes, because the
traceback the handler logs then carries the database's error and the row it refused. The second
test's first run is its arrange step, and its assertion checks that the second run added
nothing, as in [suite-example.md](../testing/suite-example.md). The
third test makes the charge fail through the table's own check, so no stand-in is needed; its
amount of 0 cannot pass `OrderPlaced`, and the test calls the use case directly to reach that
failure. Every assertion compares the whole stored result
([assertions.md](../testing/assertions.md) sections 1 and 2), and the `pytest.raises` names its
failure (section 3).

The handler and its loop reach no database and no broker: the use case is a fake, and the message
and the queue are stand-ins ([fakes-and-boundaries.md](../testing/fakes-and-boundaries.md)
section 3). The use case gets a hand-written fake, the second stand-in in that file's section 1.
aio-pika's message interface has ten abstract members [18], and the handler calls two of them, so
the message gets the third stand-in, `create_autospec`, which fails a call that the real methods
would not take. The loop calls one method of the queue, `iterator`, so the queue gets
`create_autospec` too, and the iterator it hands back is a hand-written fake. Both test files use
the use case's fake and the message builders, so those sit in `tests/support/`
([layout.md](../testing/layout.md) section 7).

`tests/support/fake_charge_order.py`

```python
"""A ChargeOrder that reaches no database, for the tests of billing's handler."""

from typing import override

from acme.billing.charge_order.schemas import ChargeOutcome
from acme.billing.charge_order.usecase import ChargeOrder
from acme.core.schemas import Currency, EventId, OrderId


class FakeChargeOrder(ChargeOrder):
    """A ChargeOrder that keeps each event id it gets and answers as it is told."""

    def __init__(
        self,
        outcome: ChargeOutcome = ChargeOutcome.CHARGED,
        error: Exception | None = None,
        connection_closed: bool = False,
    ) -> None:
        # No super().__init__(): the fake reaches no database and needs no connection.
        self.event_ids: list[EventId] = []
        self._outcome = outcome
        self._error = error
        self._connection_closed = connection_closed

    @property
    @override
    def connection_closed(self) -> bool:
        return self._connection_closed

    @override
    async def run(
        self,
        *,
        event_id: EventId,
        order_id: OrderId,
        amount_minor: int,
        currency: Currency,
    ) -> ChargeOutcome:
        self.event_ids.append(event_id)

        if self._error is not None:
            raise self._error

        return self._outcome
```

`tests/support/builders_order_placed.py`

```python
"""Builders of an OrderPlaced message, as billing's handler receives it."""

import json
from typing import Final
from unittest.mock import NonCallableMagicMock, create_autospec
from uuid import UUID

from aio_pika import IncomingMessage

EVENT_ID: Final = UUID("6f1c2b9e-4d3a-4e8f-9b7c-1a2d3e4f5a6b")
ORDER_ID: Final = UUID("0c9d8e7f-6a5b-4c3d-8e2f-1a0b9c8d7e6f")


def an_order_placed_body(
    *, currency: str = "EUR", amount_minor: int | str = 4999
) -> bytes:
    """Build the body the outbox relay publishes; a test sets only the field it is
    about, and may pass a value OrderPlaced refuses.
    """
    return json.dumps(
        {
            "event_id": str(EVENT_ID),
            "order_id": str(ORDER_ID),
            "amount_minor": amount_minor,
            "currency": currency,
        }
    ).encode()


def a_delivery(body: bytes) -> NonCallableMagicMock:
    """Build a stand-in for one delivery that records every call made on it."""
    delivery: NonCallableMagicMock = create_autospec(
        IncomingMessage, instance=True, message_id=str(EVENT_ID), body=body
    )

    return delivery
```

It is good because one file builds the body the relay publishes and the delivery that carries it,
so each test sets only the field it is about, and a change to the body's shape is one edit here
([layout.md](../testing/layout.md) section 7).

`tests/unit/worker/handlers_charge_order/test_on_order_placed.py`

```python
"""The handler of one order event, with its use case and its message stood in for."""

import logging
from typing import Final
from unittest.mock import call

import pytest

from acme.billing.charge_order.schemas import ChargeOutcome
from acme.worker.errors import ConsumerStoppedError
from acme.worker.handlers_charge_order import on_order_placed
from tests.support.builders_order_placed import (
    EVENT_ID,
    a_delivery,
    an_order_placed_body,
)
from tests.support.fake_charge_order import FakeChargeOrder

# Only the body leaking into the log can put this text there (assertions.md section 6).
UNPARSEABLE_CURRENCY: Final = "not-a-currency"


class TestOnOrderPlaced:
    """A message is acked after its charge, and rejected, never acked, when it fails."""

    # A departure from test-structure.md section 7, which writes two rows as two
    # named tests: the table runs over every ChargeOutcome, so an outcome added later
    # is tested the day it is added. The cost: a table of two rows today.
    @pytest.mark.parametrize(
        "outcome",
        [pytest.param(outcome, id=outcome.value) for outcome in ChargeOutcome],
    )
    async def test_a_message_the_use_case_has_settled_is_acked(
        self, outcome: ChargeOutcome
    ) -> None:
        """A copy charged before is acked too, or it would come back until the
        dead-letter queue took it.
        """
        message = a_delivery(an_order_placed_body())

        await on_order_placed(message, FakeChargeOrder(outcome=outcome))

        assert message.mock_calls == [call.ack()]

    async def test_a_message_is_charged_under_the_event_id_its_body_carries(
        self,
    ) -> None:
        """A charge under any other id would charge every redelivered copy again."""
        charge_order = FakeChargeOrder()

        await on_order_placed(a_delivery(an_order_placed_body()), charge_order)

        assert charge_order.event_ids == [EVENT_ID]

    async def test_a_body_with_an_amount_of_one_is_acked(self) -> None:
        """One minor unit is the smallest amount OrderPlaced takes."""
        message = a_delivery(an_order_placed_body(amount_minor=1))

        await on_order_placed(message, FakeChargeOrder())

        assert message.mock_calls == [call.ack()]

    async def test_a_body_with_the_largest_amount_a_bigint_holds_is_acked(
        self,
    ) -> None:
        """The charge table stores the amount as a bigint, up to 2**63 - 1."""
        message = a_delivery(an_order_placed_body(amount_minor=2**63 - 1))

        await on_order_placed(message, FakeChargeOrder())

        assert message.mock_calls == [call.ack()]

    async def test_a_failed_charge_is_rejected_for_a_retry_instead_of_acked(
        self,
    ) -> None:
        message = a_delivery(an_order_placed_body())

        await on_order_placed(message, FakeChargeOrder(error=RuntimeError("db down")))

        assert message.mock_calls == [call.reject(requeue=True)]

    async def test_a_failed_charge_on_a_closed_connection_stops_the_worker(
        self,
    ) -> None:
        """Every charge after a closed connection fails, and only a restart opens a
        new one.
        """
        message = a_delivery(an_order_placed_body())
        charge_order = FakeChargeOrder(
            error=RuntimeError("db down"), connection_closed=True
        )

        with pytest.raises(ConsumerStoppedError, match="connection is closed"):
            await on_order_placed(message, charge_order)

        assert message.mock_calls == [call.reject(requeue=True)]

    @pytest.mark.parametrize(
        "body",
        [
            pytest.param(
                an_order_placed_body(currency=UNPARSEABLE_CURRENCY),
                id="unknown-currency",
            ),
            pytest.param(an_order_placed_body(amount_minor=0), id="amount-zero"),
            pytest.param(
                an_order_placed_body(amount_minor=2**63), id="amount-above-a-bigint"
            ),
            pytest.param(
                an_order_placed_body(amount_minor="4999"), id="amount-as-a-string"
            ),
        ],
    )
    async def test_a_body_that_does_not_parse_is_dead_lettered_without_a_charge(
        self, body: bytes
    ) -> None:
        message = a_delivery(body)
        charge_order = FakeChargeOrder()

        await on_order_placed(message, charge_order)

        assert (message.mock_calls, charge_order.event_ids) == (
            [call.reject(requeue=False)],
            [],
        )

    async def test_a_body_that_does_not_parse_stays_out_of_the_log(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        message = a_delivery(an_order_placed_body(currency=UNPARSEABLE_CURRENCY))

        await on_order_placed(message, FakeChargeOrder())

        assert any(record.levelno == logging.INFO for record in caplog.records)
        assert not any(
            UNPARSEABLE_CURRENCY in repr(vars(record)) for record in caplog.records
        )
```

`tests/unit/worker/handlers_charge_order/test_consume_order_events.py`

```python
"""The loop that hands billing's handler one message at a time, its queue faked."""

import logging
from types import TracebackType
from typing import Final, Self, override
from unittest.mock import NonCallableMagicMock, call, create_autospec

import pytest
from aio_pika.abc import AbstractIncomingMessage
from aio_pika.exceptions import ChannelInvalidStateError
from aio_pika.queue import Queue, QueueIterator

from acme.worker.errors import ConsumerStoppedError
from acme.worker.handlers_charge_order import consume_order_events
from tests.support.builders_order_placed import a_delivery, an_order_placed_body
from tests.support.fake_charge_order import FakeChargeOrder

# Only the body leaking into the log can put this text there (assertions.md section 6).
UNPARSEABLE_CURRENCY: Final = "not-a-currency"


class FakeMessages(QueueIterator):
    """A queue iterator that hands out the given deliveries, then ends."""

    def __init__(self, *deliveries: NonCallableMagicMock) -> None:
        # No super().__init__(): the fake reads no broker and needs no queue.
        self._deliveries = list(deliveries)

    @override
    async def __aenter__(self) -> Self:
        return self

    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        return None

    @override
    def __aiter__(self) -> Self:
        return self

    @override
    async def __anext__(self) -> AbstractIncomingMessage:
        if not self._deliveries:
            # What the robust iterator does when its channel has not come back.
            raise StopAsyncIteration

        return self._deliveries.pop(0)


def a_queue_of(*deliveries: NonCallableMagicMock) -> NonCallableMagicMock:
    """Build a stand-in queue whose iterator hands out the deliveries, then ends."""
    queue: NonCallableMagicMock = create_autospec(Queue, instance=True)
    queue.iterator.return_value = FakeMessages(*deliveries)

    return queue


class TestConsumeOrderEvents:
    """The loop settles each message it gets, then raises when its iterator ends."""

    async def test_a_settle_call_on_a_closed_channel_does_not_stop_the_loop(
        self,
    ) -> None:
        """The broker sends the unsettled message again, so the loop goes on."""
        on_a_closed_channel = a_delivery(an_order_placed_body())
        on_a_closed_channel.ack.side_effect = ChannelInvalidStateError("closed")
        next_delivery = a_delivery(an_order_placed_body())
        queue = a_queue_of(on_a_closed_channel, next_delivery)

        # ChannelInvalidStateError is listed so that the edit this test names fails on
        # match, not as an error (what-to-test.md section 4, step 5).
        with pytest.raises(
            (ConsumerStoppedError, ChannelInvalidStateError), match="iterator ended"
        ):
            await consume_order_events(queue, FakeChargeOrder())

        assert next_delivery.mock_calls == [call.ack()]

    async def test_a_failed_dead_letter_reject_keeps_the_body_out_of_the_log(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """A reject that failed inside the parse's except block would carry the body,
        as its context, into any traceback the loop's line logs.
        """
        caplog.set_level(logging.DEBUG)
        unparseable = a_delivery(an_order_placed_body(currency=UNPARSEABLE_CURRENCY))
        unparseable.reject.side_effect = ChannelInvalidStateError("closed")

        with pytest.raises(ConsumerStoppedError, match="iterator ended"):
            await consume_order_events(a_queue_of(unparseable), FakeChargeOrder())

        assert any(record.levelno == logging.WARNING for record in caplog.records)
        assert not any(
            UNPARSEABLE_CURRENCY in repr(vars(record)) for record in caplog.records
        )

    async def test_an_iterator_that_ends_stops_the_worker(self) -> None:
        """A loop that returned instead would leave the worker relaying, charging
        nothing and saying nothing.
        """
        with pytest.raises(ConsumerStoppedError, match="iterator ended"):
            await consume_order_events(a_queue_of(), FakeChargeOrder())
```

It is good because the tests pin what the broker sees: `mock_calls` is the whole list of calls the
handler made on the message, so one equality says both which call came and that no other did
([assertions.md](../testing/assertions.md) section 2). The ack test turns red when the handler
acks only the `CHARGED` outcome, the event-id test when the handler charges under any id but the
body's, the failure test when the ack moves before `run`, the closed-connection test when the
handler goes on after a closed connection, and the two parse tests when the reject asks for a
requeue or the log line takes the error's text. The parse table's rows also turn red when
`strict=True`, `le=` or `gt=0` leaves billing's model, and the two amount tests, the in-bound
neighbours of those bounds ([what-to-test.md](../testing/what-to-test.md) section 4, step 2), when
a bound moves one step inward, such as `le=` becoming `lt=`. The loop's first test turns red when
the `except BROKER_ERRORS` goes or shrinks to `AMQPError`, because the first ack's
`ChannelInvalidStateError` then ends the loop before the second message and fails the
`match=`; its second test turns red when the reject of a body that does not parse moves back
inside the `except` block and the loop's line gains a traceback, and its third when the loop
returns after its iterator ends. The fakes keep what they received in a public list or hand out
what they were given, `@override` fails the type check the day a parent method changes its
signature, and no test uses a bare `Mock()` or `mock.patch`
([fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) sections 1 and 2). Each leak check
pairs its negative line with a positive one after setting the level to `DEBUG`, and it reads every
attribute of every record ([assertions.md](../testing/assertions.md) section 6). The stand-ins
work for the async methods because `create_autospec` gives each coroutine method an `AsyncMock`
and checks each call against the real signature [19].

The settings class of section 3 gains one test in `tests/unit/core/test_config.py`, the file of
[settings-example.md](../language/settings-example.md), whose `VALID_ENVIRONMENT` holds every
required variable, as [outbox-relay-example.md](outbox-relay-example.md) section 10 shows it.
The new test sits in its `TestSettings` class:

```python
    def test_a_prefetch_count_of_zero_stops_the_start(
        self, environment: pytest.MonkeyPatch
    ) -> None:
        """RabbitMQ reads a prefetch of 0 as no limit (message-brokers.md section 9)."""
        environment.setenv("ACME_BILLING_PREFETCH_COUNT", "0")

        with pytest.raises(ValidationError) as caught:
            Settings(_env_file=None)

        errors = caught.value.errors(include_input=False)
        assert [(error["loc"], error["type"]) for error in errors] == [
            (("billing_prefetch_count",), "greater_than")
        ]
```

It is good because it tests the consequence of the declaration, a start that stops, and not the
declared value ([what-to-test.md](../testing/what-to-test.md) section 2): delete `gt=0` and this
test, and only this one, turns red.

## 10. What this example does not claim

- **It was not run.** Each Python block was parsed with Python 3.13, and each library call was
  read in the library's own source or documentation at the versions of section 1. Two
  behaviours were tried on Python 3.13 with stand-in classes: `create_autospec` on a class with
  slots and async methods, as the handler tests use it, and a task group whose task is
  cancelled from outside, as the entry point uses it. No test ran against a real broker or
  database, and no type checker or linter ran on the code. The edit that each test names as
  turning it red was reasoned from the code, not run.
- **One message at a time.** The worker charges one message at a time on one database connection.
  For more throughput, run more worker processes. A worker that must charge several messages at
  once in one process needs a connection per message in flight, such as from a pool, and that is
  not shown.
- **No reconnect to the database.** The worker opens billing's connection once. When the database
  closes it, the next charge fails, the connection reports closed, and the handler returns that
  message and raises `ConsumerStoppedError` (section 7): the worker exits with an error, and its
  restart opens a new connection. A charge that fails for another reason stays on the delayed
  retry of section 4: 20 waits, 35 minutes in all, before the dead-letter queue takes it.
- **The broker's side is not tested**, a departure from [message-brokers.md](message-brokers.md)
  section 16, whose checks ask for an integration test against a real RabbitMQ in testcontainers.
  It is left out with the broker's container and the run of the script of section 4 against it,
  because the tests here fake the broker and start no broker container; such a test would start
  the broker ([libraries.md](../testing/libraries.md) section 2), run the script, and read a
  rejected message from the dead-letter queue. The cost: nothing checks that the policy's pattern
  matches the queue's name, that a reject reaches the dead-letter queue, or that the delivery
  limit counts a reject.
- **One broker connection carries the relay's publishes and billing's acks.** Billing's queue
  opens its channel on the relay's `rabbitmq` connection (section 8), while RabbitMQ recommends
  "that, when possible, publishers and consumers use separate connections" [27]. The cost: flow
  control on the relay's publishing slows billing's acks, and under a resource alarm the broker
  stops reading every connection that publishes [28], so billing's acks stop until it clears. A
  failure of either duty also stops the other through the task group. The way out is billing's
  consumer in a worker process of its own, which gets its own connection by
  [message-brokers.md](message-brokers.md) section 5.
- **The queue is bound before the relay's first publish.** `run_worker` declares and binds
  billing's queue before it starts the relay (section 8). The risk is a relay in a process without
  billing's declaration: what an event that no queue takes does to the relay is
  [outbox-relay-example.md](outbox-relay-example.md) section 11 and
  [message-brokers.md](message-brokers.md) section 8.
- **Left out: the alarm on the dead-letter queue**, a departure from [delivery.md](delivery.md)
  section 6, rule 4. The alarm lives in the monitoring system, outside the service's code. It
  fires when `billing.order_placed.dead-letter` holds one message or more, read by the monitoring
  system with a user of its own, tagged `monitoring`, with no configure or write rights [21],
  never the worker's user. The cost: until it is set, a dead letter sits there unseen. A person
  sends a dead letter back by publishing it again, and the idempotent consumer makes that copy
  safe ([delivery.md](delivery.md) section 6, rule 5).
- **Left out:** the job that deletes old `processed_message` rows
  ([delivery.md](delivery.md) section 3, step 5), TLS to the database, and the trace context,
  which the aio-pika instrumentation carries ([delivery.md](delivery.md) section 9). libpq's
  default `sslmode=prefer` neither requires encryption nor checks the server, and PostgreSQL's
  docs call it "not recommended in secure deployments" [24]: deployed environments pass
  `sslmode="verify-full"` and `sslrootcert` from the settings class, and the test database keeps
  TLS off.

## 11. Sources

Checked 2026-10-30 unless a line ends with — checked <YYYY-MM-DD>.

- [1] PyPI — aio-pika, 10.2.1 (package metadata) — https://pypi.org/pypi/aio-pika/10.2.1/json
- [2] PyPI — aiormq, 7.2.4 (package metadata) — https://pypi.org/pypi/aiormq/json
- [3] PyPI — psycopg, 3.3.6 (package metadata) — https://pypi.org/pypi/psycopg/json
- [4] PyPI — pydantic, 2.14.2 (package metadata) — https://pypi.org/pypi/pydantic/json
- [5] PyPI — testcontainers, 4.15.0 (package metadata) — https://pypi.org/pypi/testcontainers/json
- [6] RabbitMQ — Quorum Queues, documentation 4.4 — https://www.rabbitmq.com/docs/quorum-queues — checked 2026-10-29
- [7] RabbitMQ — Dead Letter Exchanges, documentation 4.4 — https://www.rabbitmq.com/docs/dlx
- [10] RabbitMQ — rabbitmq-server, `deps/rabbitmq_cli/lib/rabbitmq/cli/ctl/commands/set_policy_command.ex`, v4.4.0 — https://github.com/rabbitmq/rabbitmq-server/blob/v4.4.0/deps/rabbitmq_cli/lib/rabbitmq/cli/ctl/commands/set_policy_command.ex
- [11] Python — asyncio: Exceptions, Python 3.13 documentation — https://docs.python.org/3.13/library/asyncio-exceptions.html
- [12] aiormq — `aiormq/channel.py`, 7.2.4 — https://github.com/mosquito/aiormq/blob/7.2.4/aiormq/channel.py
- [13] Psycopg — Concurrent operations, documentation 3.3.7.dev1 — https://www.psycopg.org/psycopg3/docs/advanced/async.html
- [14] aio-pika — `aio_pika/robust_queue.py`, 10.2.1 — https://github.com/mosquito/aio-pika/blob/10.2.1/aio_pika/robust_queue.py
- [15] aio-pika — `aio_pika/queue.py`, 10.2.1 — https://github.com/mosquito/aio-pika/blob/10.2.1/aio_pika/queue.py
- [16] aio-pika — `aio_pika/message.py`, 10.2.1 — https://github.com/mosquito/aio-pika/blob/10.2.1/aio_pika/message.py
- [17] Python — `Lib/asyncio/taskgroups.py`, branch 3.13 — https://github.com/python/cpython/blob/3.13/Lib/asyncio/taskgroups.py
- [18] aio-pika — `aio_pika/abc.py`, 10.2.1 — https://github.com/mosquito/aio-pika/blob/10.2.1/aio_pika/abc.py
- [19] Python — `Lib/unittest/mock.py` (`create_autospec`), branch 3.13 — https://github.com/python/cpython/blob/3.13/Lib/unittest/mock.py
- [20] RabbitMQ — Policies, documentation 4.4 — https://www.rabbitmq.com/docs/policies
- [21] RabbitMQ — Authentication, Authorisation, Access Control, documentation 4.4 — https://www.rabbitmq.com/docs/access-control — checked 2026-10-29
- [22] PostgreSQL Global Development Group — `src/backend/executor/execMain.c`, branch REL_18_STABLE — https://github.com/postgres/postgres/blob/REL_18_STABLE/src/backend/executor/execMain.c
- [23] Psycopg — Connection classes, documentation 3.3.7.dev1 — https://www.psycopg.org/psycopg3/docs/api/connections.html
- [24] PostgreSQL Global Development Group — libpq: SSL Support, PostgreSQL 18 — https://www.postgresql.org/docs/18/libpq-ssl.html
- [25] RabbitMQ — rabbitmq-server, `deps/rabbit/docs/rabbitmqctl.8` (`set_topic_permissions`), v4.4.0 — https://github.com/rabbitmq/rabbitmq-server/blob/v4.4.0/deps/rabbit/docs/rabbitmqctl.8
- [26] RabbitMQ — rabbitmq-server, `deps/rabbit/src/rabbit_channel.erl` (`binding_action_with_checks`), v4.4.0 — https://github.com/rabbitmq/rabbitmq-server/blob/v4.4.0/deps/rabbit/src/rabbit_channel.erl
- [27] RabbitMQ — Connections, documentation 4.4 — https://www.rabbitmq.com/docs/connections — checked 2026-10-29
- [28] RabbitMQ — Publishers, documentation 4.4 — https://www.rabbitmq.com/docs/publishers — checked 2026-10-29
