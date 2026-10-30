# Example: an outbox and its polling relay

A worked example for [delivery.md](delivery.md) section 4: an order and its event written in one
PostgreSQL transaction, and a relay that publishes the event to RabbitMQ and deletes it only after
the broker's confirm.

The application is Acme Corp's shop, the package `acme`. Its orders area has two modules.
`place_order` stores an order and, in the same transaction, writes its `OrderPlaced` event to the
`outbox` table. `relay_outbox` sends each outbox row to RabbitMQ on a channel with publisher
confirms and deletes the row after the confirm. A worker process runs the relay in a loop. The
consumer that charges each order once is in [consumer-example.md](consumer-example.md). Every name
is a placeholder.

**Navigation**

- [1. When you need this, and when not](#1-when-you-need-this-and-when-not)
- [2. The files](#2-the-files)
- [3. The tables](#3-the-tables)
- [4. The settings](#4-the-settings)
- [5. The clients in core](#5-the-clients-in-core)
- [6. Placing an order](#6-placing-an-order)
- [7. The relay: one batch in one transaction](#7-the-relay-one-batch-in-one-transaction)
- [8. The loop and the worker's entry point](#8-the-loop-and-the-workers-entry-point)
- [9. Why the order holds](#9-why-the-order-holds)
- [10. The tests](#10-the-tests)
- [11. Where the example stops](#11-where-the-example-stops)
- [12. Sources](#12-sources)

## 1. When you need this, and when not

You need an outbox when a use case changes its database and must tell another service about the
change through a broker, and the event must go out if, and only if, the change commits
([delivery.md](delivery.md) section 4). Placing an order is such a case: billing must charge every
order that was placed, and never one whose transaction rolled back.

Check the simpler ways first. Each of them makes this example too much:

- **The worker takes its jobs from the same PostgreSQL**, as a Procrastinate worker does. Defer the
  job inside the application's own transaction: the job row is then the outbox and the worker is
  the relay ([delivery.md](delivery.md) section 4, "When the worker reads its jobs from the same
  PostgreSQL").
- **Kafka Connect and Debezium already run next to the database.** Let Debezium tail the log, and
  keep only the write side of section 6. The table in section 3 already has the column names its
  outbox router expects ([delivery.md](delivery.md) section 4, "The relay: log tailing with
  Debezium").
- **A lost event, or one sent for a change that rolled back, does no harm.** Then the outbox costs
  more than it saves ([delivery.md](delivery.md) section 4).

The relay is code you write, because no mature Python outbox library exists yet;
[delivery.md](delivery.md) section 4, "Choosing a library", gives the questions to judge one by.

Left out of the example: the HTTP route that calls `PlaceOrder`, the function that opens the
RabbitMQ connection ([message-brokers.md](message-brokers.md) section 5 shows it), the logging
config ([setup-example.md](../logging/setup-example.md) shows it), the migration tool, and the TLS
settings of the database connection. Each block below names what it cuts.

## 2. The files

Only the files this example touches. Every folder under `src/` and `tests/` has an empty
`__init__.py`; the tree leaves them out.

```text
<repo>/
├── .env.example                    gains a line for each new setting (below)
├── migrations/
│   └── 0001_create_orders_and_outbox.sql   the two tables of section 3
├── pyproject.toml                  the layers contract gains the worker adapter
├── src/acme/
│   ├── core/
│   │   ├── config.py               Settings: the fields of section 4
│   │   ├── database.py             connect_database: the one way into PostgreSQL
│   │   ├── rabbitmq_client.py      open_event_exchange, publish_event, BROKER_ERRORS
│   │   └── schemas.py              Currency, EventId, OrderId, RoutingKey: shared types
│   ├── orders/
│   │   ├── place_order/
│   │   │   ├── schemas.py          OrderPlaced: the event billing parses
│   │   │   ├── repository.py       the order row and its outbox row
│   │   │   └── usecase.py          PlaceOrder: both rows in one transaction
│   │   └── relay_outbox/
│   │       ├── schemas.py          OutboxRow, and RelayOutcome: which path one batch took
│   │       ├── errors.py           EventNotPublishedError, EventReturnedError
│   │       ├── repository.py       the relay's lock, the claim and the delete
│   │       └── usecase.py          RelayOutbox: one batch in one transaction
│   └── worker/
│       ├── handlers_relay_outbox.py   relay_until_stopped: the poll loop
│       └── main.py                    builds each client once, runs the loop
└── tests/
    ├── integration/
    │   ├── conftest.py             one Postgres container per run
    │   ├── place_order/
    │   │   └── test_usecase.py     TestPlaceOrder
    │   └── relay_outbox/
    │       └── test_usecase.py     TestRelayOutbox, and the second connection it uses
    ├── support/
    │   └── connection_postgres.py  connect_to: the worker's own way into the test database
    └── unit/
        ├── core/
        │   └── test_config.py      gains the relay's settings (section 10)
        └── worker/
            └── test_handlers_relay_outbox.py   TestRelayUntilStopped
```

It is good because every file sits where
[file-structure.md](../../any-language/file-structure/file-structure.md) puts its kind: one client
per external system in `core/` (section 4), a module for each thing the application is asked to
do, named for it (sections 1 and 3), and one file per module in the worker adapter, named for its
role (sections 5 and 7). The SQL lives in each module's `repository.py`, so the adapter holds no
query. The worker is a new adapter, so the same change adds it to the import contracts of
[layout-example.md](../../any-language/file-structure/layout-example.md) section 3 in
`pyproject.toml`: the layers contract's top layer becomes `"acme.api | acme.worker"`, and
`lint-imports` checks the worker's imports too (file-structure.md section 11). `.env.example`,
which holds every setting with no real value (file-structure.md section 9), gains
`ACME_DATABASE_PORT`, `ACME_RABBITMQ_HOST`, `ACME_RABBITMQ_PORT`, `ACME_RABBITMQ_USER`,
`ACME_RABBITMQ_PASSWORD`, `ACME_RABBITMQ_VHOST`, `ACME_OUTBOX_BATCH_SIZE` and
`ACME_OUTBOX_POLL_INTERVAL_SECONDS`. Each test file has the path [layout.md](../testing/layout.md)
section 3 gives it: the two use cases query the database, so their tests are integration tests,
and the loop is tested in the unit suite with the relay faked. `connect_to`, which two test files use, sits in `tests/support/`
([layout.md](../testing/layout.md) section 7).

## 3. The tables

`migrations/0001_create_orders_and_outbox.sql`. The `orders` table holds only what this example
reads, and the consumer's `processed_message` table is in [consumer-example.md](consumer-example.md).

```sql
CREATE TABLE orders (
    id           uuid PRIMARY KEY,
    -- In minor units, cents for EUR and USD, so no float rounds an amount.
    amount_minor bigint NOT NULL,
    currency     text NOT NULL
);

-- One row per event to publish; Debezium's default column names, so a later move to
-- log tailing needs no rename (delivery.md section 4).
CREATE TABLE outbox (
    -- The order the relay sends in. Nothing updates it, so the claim's ORDER BY holds.
    position      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- The event's id, sent as message_id, the id the broker and the log lines carry.
    -- Consumers drop a second copy by the same id in the payload, a departure from
    -- delivery.md section 3, which finds a copy by the header without parsing the
    -- body: the payload is parsed and checked first, so its id is the checked one, and
    -- both carry the same value. The cost: a copy is found only after its body parses.
    id            uuid NOT NULL UNIQUE,
    -- With type, the routing key: orders.order_placed.
    aggregatetype text NOT NULL,
    -- The order's id: one order's events keep their order (delivery.md section 7).
    aggregateid   text NOT NULL,
    -- The event's name.
    type          text NOT NULL,
    -- The event as billing parses it.
    payload       jsonb NOT NULL
);
```

It is good because each column has one job, and its reason sits at the line. Nothing ever updates
`position`, and the claim depends on that: PostgreSQL warns that a `SELECT` with `ORDER BY` and a
locking clause can return rows out of order when the sort column is changed while the `SELECT`
waits for a lock [1]. `id` is `UNIQUE`, so one event never gets two rows, and a second insert of
the same event fails; the third test of `PlaceOrder` in section 10 relies on that. The names are
the ones Debezium's outbox router expects ([delivery.md](delivery.md) section 4), so a team that
starts running Debezium keeps the table and drops the relay.

## 4. The settings

The fields the worker reads from the application's `Settings` in `src/acme/core/config.py`. The
four `database_` fields other than the port are already in
[settings-example.md](../language/settings-example.md); the rest are new here. The class's
`model_config` and its other fields are that example's, cut with `...`; its placeholder validator
is shown, because the RabbitMQ password joins it. The file's imports gain `Annotated` from
`typing` and `Field` from `pydantic`.

```python
class Settings(BaseSettings):
    ...

    # No default: a deployment that lacks one stops at startup (python.md section 5).
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    # Its own field, not in a URL: a URL prints its password (python.md section 5).
    database_password: SecretStr
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_user: str
    rabbitmq_password: SecretStr
    rabbitmq_vhost: str
    # Small: the claim's transaction stays open while its batch is sent
    # (delivery.md section 4).
    outbox_batch_size: Annotated[int, Field(gt=0)] = 100
    # The wait after an empty claim is about the longest a new event waits to leave.
    outbox_poll_interval_seconds: Annotated[float, Field(gt=0)] = 1.0

    # The validator checks every secret field, so a RabbitMQ password left at the
    # placeholder stops the start as the others do.
    @field_validator("database_password", "payments_api_key", "rabbitmq_password")
    @classmethod
    def reject_placeholder(cls, secret: SecretStr) -> SecretStr:
        if secret.get_secret_value() == PLACEHOLDER_SECRET:
            raise ValueError("still holds the placeholder from .env.example")

        return secret
```

| Field | What it means | Set it when | Leave it out when |
|---|---|---|---|
| the `database_` and `rabbitmq_` fields | where the worker connects, and as whom | always: they have no default | never |
| `outbox_batch_size` | the most rows one claim takes and sends in one transaction | a measurement shows the relay falls behind and a bigger batch helps; where one relay stops keeping up is not covered yet ([delivery.md](delivery.md) section 12) | the default keeps up |
| `outbox_poll_interval_seconds` | how long the relay waits after an empty claim, or after the broker refused an event | events must leave sooner, or the polls load the database | the default fits |

It is good because each value a deployment must set has no default, so a missing one stops the
worker at startup, and each password is a `SecretStr` in a field of its own
([python.md](../language/python.md) section 5). The placeholder validator covers the RabbitMQ
password as it covers the others, so a deployment that kept `.env.example`'s value stops at
startup. The two tuning values are safe in every environment, so they keep a default, and `gt=0`
stops a batch of zero or a poll loop with no wait at startup. Section 10 tests both rules.

## 5. The clients in core

`src/acme/core/database.py`. libpq's default `sslmode=prefer` neither requires encryption nor
checks the server, and PostgreSQL's docs call it "not recommended in secure deployments" [15]:
deployed environments pass `sslmode="verify-full"` and `sslrootcert` from the settings class, and
the test database keeps TLS off. Those TLS settings of the connection are left out here:

```python
"""The one way into the application's PostgreSQL database."""

import psycopg
from psycopg.rows import TupleRow
from pydantic import SecretStr


async def connect_database(
    host: str, port: int, name: str, user: str, password: SecretStr
) -> psycopg.AsyncConnection[TupleRow]:
    return await psycopg.AsyncConnection.connect(
        host=host,
        port=port,
        dbname=name,
        user=user,
        password=password.get_secret_value(),
        # Every transaction() block is then a real transaction that commits when it
        # ends, never a savepoint inside one an earlier query opened
        # (delivery.md section 3).
        autocommit=True,
    )
```

It is good because every input is a parameter, so a test passes the container's values
([readability.md](../../any-language/readability/readability.md) section 6), and the password stays
a `SecretStr` until the one line that needs its text. `autocommit=True` is the line a copier would
drop. Without it, a query run outside a block leaves a transaction open, and every
`transaction()` block after it only nests a savepoint and commits nothing
([delivery.md](delivery.md) section 3).

`src/acme/core/rabbitmq_client.py`. The file's docstring, its other imports and `connect_rabbitmq`
are [message-brokers.md](message-brokers.md) section 5's, cut with `...`. This is what the outbox
adds:

```python
from typing import Final
from uuid import UUID

from aio_pika.abc import AbstractChannel, AbstractExchange
from aio_pika.exceptions import AMQPError, ChannelInvalidStateError

from acme.core.schemas import RoutingKey

...

EVENTS_EXCHANGE: Final = "acme.events"

# A publish, an ack or a reject raises these when the broker did not get it: a nack, a
# returned message, a lost connection, or a closed channel, which aiormq raises as a
# RuntimeError and not as an AMQPError. A connection the heartbeat finds stuck fails
# a pending confirm with asyncio.CancelledError instead, which this does not catch:
# the worker exits, and its restart sends the rows again.
BROKER_ERRORS: Final = (AMQPError, ChannelInvalidStateError)


async def open_event_exchange(channel: AbstractChannel) -> AbstractExchange:
    return await channel.declare_exchange(
        EVENTS_EXCHANGE,
        # Topic: each subscriber binds its queue to the keys it wants, such as
        # orders.order_placed (message-brokers.md section 6).
        aio_pika.ExchangeType.TOPIC,
        # Durable: aio-pika's default would lose the exchange when the broker restarts
        # (message-brokers.md section 8).
        durable=True,
    )


async def publish_event(
    exchange: AbstractExchange,
    *,
    routing_key: RoutingKey,
    message_id: UUID,
    body: bytes,
) -> None:
    message = aio_pika.Message(
        body,
        content_type="application/json",
        # The broker and the log lines carry this id; consumers drop a second copy by
        # the same id in the body, a departure from delivery.md section 3 that the
        # outbox table declares (outbox-relay-example.md section 3).
        message_id=str(message_id),
        # Not aio-pika's default: a dead-lettered copy survives a restart only if it
        # is persistent (message-brokers.md section 8).
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )

    # On the channel main() opens, with confirms and on_return_raises=True, this
    # returns after the broker's ack, and a nack or a returned message raises.
    # mandatory=True is aio-pika's default, written out: without it a message no
    # queue takes is dropped and still confirmed (message-brokers.md section 8).
    # The broker's errors leave here as they are: the caller wraps them, a
    # departure its use case declares (outbox-relay-example.md section 7).
    await exchange.publish(message, routing_key=routing_key, mandatory=True)
```

What `publish_event` guarantees, and why its key is a `RoutingKey`, is
[message-brokers.md](message-brokers.md) section 8's; its one caller is the relay. It is good
because `BROKER_ERRORS` names the errors that mean the broker did not get what was sent, so the
relay catches those and lets a bug through; billing's consumer catches the same errors around its
ack and reject ([consumer-example.md](consumer-example.md) section 7). aio-pika raises
`DeliveryError` when the broker answers with a nack, and `PublishError`, a `DeliveryError` too,
for a returned message on a channel opened with `on_return_raises=True` [3], [4]. aiormq defines
`ChannelInvalidStateError` as a `RuntimeError` [4], so an `except AMQPError` alone would let a
closed channel crash the worker. A lost confirm sends the event again, and the consumer drops the
copy ([message-brokers.md](message-brokers.md) section 8, [delivery.md](delivery.md) section 3).

## 6. Placing an order

`src/acme/orders/place_order/schemas.py`. `Currency`, the closed set of currencies an order
takes, and the two id types `EventId` and `OrderId` sit in `src/acme/core/schemas.py`, because
billing carries them too ([file-structure.md](../../any-language/file-structure/file-structure.md)
section 4); [consumer-example.md](consumer-example.md) section 5 shows them:

```python
"""The event a placed order publishes."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from acme.core.schemas import Currency, EventId, OrderId


class OrderPlaced(BaseModel):
    """The OrderPlaced event: billing charges the order from it."""

    # The fixed shape billing parses: a misspelt field fails here, and nothing changes
    # the event once it is built (python.md section 4).
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: EventId
    order_id: OrderId
    # Strict: an amount of money is never coerced from a string or a float
    # (python.md section 4). The upper bound is a bigint's largest value, so an amount
    # the orders table cannot store fails here, before anything is written.
    amount_minor: Annotated[int, Field(gt=0, le=9_223_372_036_854_775_807, strict=True)]
    currency: Currency
```

It is good because the event is a Pydantic model, the form python.md gives a message that leaves
the service, and its rules sit on its fields ([python.md](../language/python.md) section 4): the
currency is a closed set, never a bare `str` ([python.md](../language/python.md) section 3), and
the amount is a whole number of minor units above zero. The event carries ids and an amount and no
personal data, so nothing in it has to be erased from queues later ([delivery.md](delivery.md)
section 10).

`src/acme/orders/place_order/repository.py`:

```python
"""The queries of placing an order: the order row and its outbox row."""

from typing import Final

from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from psycopg.types.json import Jsonb

from acme.core.schemas import Currency, OrderId, RoutingKey
from acme.orders.place_order.schemas import OrderPlaced

# The relay routes on aggregatetype.type, so this event goes out as
# orders.order_placed, the key billing's queue is bound to. Both halves are taken
# from RoutingKey, the key's one declaration (python.md section 3).
AGGREGATE_TYPE: Final = RoutingKey.ORDER_PLACED.partition(".")[0]
EVENT_TYPE: Final = RoutingKey.ORDER_PLACED.partition(".")[2]


async def insert_order(
    conn: AsyncConnection[TupleRow],
    *,
    order_id: OrderId,
    amount_minor: int,
    currency: Currency,
) -> None:
    await conn.execute(
        "INSERT INTO orders (id, amount_minor, currency) VALUES (%s, %s, %s)",
        (order_id, amount_minor, currency),
    )


async def insert_order_placed(
    conn: AsyncConnection[TupleRow], event: OrderPlaced
) -> None:
    await conn.execute(
        "INSERT INTO outbox (id, aggregatetype, aggregateid, type, payload)"
        " VALUES (%s, %s, %s, %s, %s)",
        (
            event.event_id,
            AGGREGATE_TYPE,
            str(event.order_id),
            EVENT_TYPE,
            # mode="json": the ids and the currency go in as the strings billing parses.
            Jsonb(event.model_dump(mode="json")),
        ),
    )
```

It is good because each query is one function, and every value goes in as a parameter, never
formatted into the SQL. The two names that make up the routing key are constants next to the one
query that writes them ([file-structure.md](../../any-language/file-structure/file-structure.md)
section 3). The outbox keeps the key in two columns ([delivery.md](delivery.md) section 4), and
both are taken from `RoutingKey`, the key's one declaration, so the key is never spelt a second
time ([python.md](../language/python.md) section 3). psycopg dumps an enum with a mix-in type,
such as this `StrEnum`, by its mix-in type, so the currency is stored as its string, and a dict
goes into a `jsonb` column only inside the `Jsonb` wrapper [5].

`src/acme/orders/place_order/usecase.py`:

```python
"""Place an order: the order and its OrderPlaced event commit together, or neither."""

from psycopg import AsyncConnection
from psycopg.rows import TupleRow

from acme.core.schemas import Currency, EventId, OrderId
from acme.orders.place_order import repository
from acme.orders.place_order.schemas import OrderPlaced


class PlaceOrder:
    def __init__(self, conn: AsyncConnection[TupleRow]) -> None:
        self._conn = conn

    async def run(
        self,
        *,
        order_id: OrderId,
        event_id: EventId,
        amount_minor: int,
        currency: Currency,
    ) -> None:
        event = OrderPlaced(
            event_id=event_id,
            order_id=order_id,
            amount_minor=amount_minor,
            currency=currency,
        )

        # One transaction: the order and its event commit together, or neither does
        # (delivery.md section 4).
        async with self._conn.transaction():
            await repository.insert_order(
                self._conn,
                order_id=order_id,
                amount_minor=amount_minor,
                currency=currency,
            )

            await repository.insert_order_placed(self._conn, event)
```

It is good because the order row and the outbox row are written in one `transaction()` block on an
autocommit connection, so they commit together or not at all, and the use case calls no broker: it
takes only the connection ([delivery.md](delivery.md) section 4). The event is built before the
block, so an amount the model refuses fails before anything is written. The caller passes both ids:
the route, left out, makes them with `OrderId(uuid4())` and `EventId(uuid4())`, so a test passes
fixed ones ([readability.md](../../any-language/readability/readability.md) section 6), and the
two types make the checker refuse an order id passed as the event's
([python.md](../language/python.md) section 3).

## 7. The relay: one batch in one transaction

The relay follows the five steps of [delivery.md](delivery.md) section 4, "The relay: polling", the
advisory lock of step 4 included (section 9 says how it keeps the order).

`src/acme/orders/relay_outbox/schemas.py`:

```python
"""What the relay reads from an outbox row, and what one batch did."""

from dataclasses import dataclass
from enum import StrEnum, unique

from acme.core.schemas import EventId, RoutingKey


@dataclass(frozen=True)
class OutboxRow:
    position: int
    event_id: EventId
    routing_key: RoutingKey
    # The field holds the event's JSON as text, sent on as it is and never parsed here.
    payload: str


# Each member names the path one batch took. The loop and the tests write its
# members by name, so the type is a StrEnum (python.md section 2).
@unique
class RelayOutcome(StrEnum):
    SENT = "sent"
    EMPTY = "empty"
    LOCKED = "locked"
```

`src/acme/orders/relay_outbox/errors.py`:

```python
"""The errors of a batch the broker did not take."""

from acme.core.schemas import EventId


class EventNotPublishedError(Exception):
    """The broker did not take an event, so its whole batch stays in the outbox."""

    def __init__(self, event_id: EventId, broker_error: str) -> None:
        super().__init__(f"Event {event_id} was not published: {broker_error}")
        self.event_id = event_id
        self.broker_error = broker_error


class EventReturnedError(EventNotPublishedError):
    """No queue is bound to the event's key, so the broker sent the event back."""
```

`src/acme/orders/relay_outbox/repository.py`:

```python
"""The relay's queries: its lock, the claim of a batch and the delete."""

from typing import Final
from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import TupleRow, kwargs_row

from acme.core.schemas import EventId, RoutingKey
from acme.orders.relay_outbox.schemas import OutboxRow

# The key can be any bigint that no other advisory lock in this database uses.
RELAY_LOCK_KEY: Final = 7_241_001


async def take_relay_lock(conn: AsyncConnection[TupleRow]) -> bool:
    """Take the relay's lock for this transaction; False if another relay has it."""
    cursor = await conn.execute(
        "SELECT pg_try_advisory_xact_lock(%s)", (RELAY_LOCK_KEY,)
    )

    row = await cursor.fetchone()
    return row is not None and bool(row[0])


def outbox_row(
    *, position: int, event_id: UUID, routing_key: str, payload: str
) -> OutboxRow:
    """Build an OutboxRow from the claim's columns, the id and the key parsed once."""
    return OutboxRow(
        position=position,
        event_id=EventId(event_id),
        # The column's text: a key outside RoutingKey fails here, with a ValueError
        # (python.md section 3), so the worker deploys before the code that writes a
        # new key (the deploy order of outbox-relay-example.md section 11).
        routing_key=RoutingKey(routing_key),
        payload=payload,
    )


async def claim_batch(
    conn: AsyncConnection[TupleRow], *, limit: int
) -> list[OutboxRow]:
    """Lock and return the oldest rows, at most limit of them."""
    async with conn.cursor(row_factory=kwargs_row(outbox_row)) as cursor:
        await cursor.execute(
            """
            SELECT
                position,
                id AS event_id,
                -- The topic exchange routes on <aggregate type>.<event type>.
                aggregatetype || '.' || type AS routing_key,
                payload::text AS payload
            FROM outbox
            -- The order the service wrote in (delivery.md section 4).
            ORDER BY position
            LIMIT %s
            -- Another relay skips these rows instead of sending them too.
            FOR UPDATE SKIP LOCKED
            """,
            (limit,),
        )

        return await cursor.fetchall()


# A list, not a tuple: psycopg sends a list as an array for = ANY().
async def delete_rows(conn: AsyncConnection[TupleRow], positions: list[int]) -> None:
    await conn.execute("DELETE FROM outbox WHERE position = ANY(%s)", (positions,))
```

`src/acme/orders/relay_outbox/usecase.py`:

```python
"""Send the outbox to the broker, one batch at a time, in the order it was written."""

from aio_pika.abc import AbstractExchange
from aio_pika.exceptions import PublishError
from psycopg import AsyncConnection
from psycopg.rows import TupleRow

from acme.core.rabbitmq_client import BROKER_ERRORS, publish_event
from acme.orders.relay_outbox import repository
from acme.orders.relay_outbox.errors import EventNotPublishedError, EventReturnedError
from acme.orders.relay_outbox.schemas import OutboxRow, RelayOutcome


class RelayOutbox:
    def __init__(
        self,
        conn: AsyncConnection[TupleRow],
        exchange: AbstractExchange,
        *,
        batch_size: int,
    ) -> None:
        self._conn = conn
        self._exchange = exchange
        self._batch_size = batch_size

    async def run(self) -> RelayOutcome:
        """Send one batch and delete it; return which path ran.

        Raise EventNotPublishedError, with the whole batch left in the outbox, when
        the broker does not take an event; EventReturnedError, one kind of it, when no
        queue is bound to the event's key.
        """
        # One transaction for the lock, the claim and the delete: a failure anywhere
        # rolls back, and the rows wait for the next batch (delivery.md section 4).
        async with self._conn.transaction():
            # One relay at a time keeps one order's events in order
            # (delivery.md section 4).
            if not await repository.take_relay_lock(self._conn):
                return RelayOutcome.LOCKED

            rows = await repository.claim_batch(self._conn, limit=self._batch_size)

            for row in rows:
                await self._publish(row)

            # After every confirm: a crash before the commit sends the batch again,
            # never loses it (delivery.md section 4).
            await repository.delete_rows(self._conn, [row.position for row in rows])

        if not rows:
            return RelayOutcome.EMPTY

        return RelayOutcome.SENT

    async def _publish(self, row: OutboxRow) -> None:
        try:
            await publish_event(
                self._exchange,
                routing_key=row.routing_key,
                message_id=row.event_id,
                body=row.payload.encode(),
            )
        except PublishError as error:
            # Returned: no queue is bound to the event's key, and only a person can
            # bind one. The error is raised from None, for the reason below.
            raise EventReturnedError(
                row.event_id, broker_error=type(error).__name__
            ) from None
        except BROKER_ERRORS as error:
            # A departure from logging.md section 10, where the one client raises
            # its own safe error: the relay is publish_event's one caller, and its
            # error adds the event id. The cost: a second caller of publish_event
            # must wrap the broker's errors the same way. From None: the broker's
            # error can hold the message, body included; the event id is all the log
            # needs.
            raise EventNotPublishedError(
                row.event_id, broker_error=type(error).__name__
            ) from None
```

It is good because:

- **The rows stay locked and in the table until the broker has confirmed every one.** A refusal, a
  crash or a lost connection rolls the transaction back and leaves them to be sent again, and the
  cost is the duplicates the consumers drop ([delivery.md](delivery.md) section 3). While one event
  is refused, the rows ahead of it in its batch are sent again on every poll, and the consumers
  drop the copies.
- **`run` returns which path it took**: a `RelayOutcome` member
  ([python.md](../language/python.md) section 2). The loop waits on `EMPTY` and `LOCKED` alike;
  the outcome tells them apart for the tests and the reader.
- **The lock lives exactly as long as the batch.** `pg_try_advisory_xact_lock` takes the lock at
  once or returns false without waiting [6], and PostgreSQL releases a transaction-level lock when
  the transaction ends, with no unlock call to forget [7]. A second relay, during a deploy or as a
  second replica of the worker, finds the lock taken and waits for its next poll. Brandur Leach's
  enqueuer also holds a lock around its whole loop, with the comment "Only one enqueuer should be
  running at any given time" [8].
- **The claim is the one [delivery.md](delivery.md) section 4 asks for.** PostgreSQL's docs give
  `SKIP LOCKED` this use: "to avoid lock contention with multiple consumers accessing a queue-like
  table" [1]. Behind the lock no other relay holds outbox rows. The clause matters to a team whose
  consumers need no order and which drops the lock to run several relays: each relay then skips the
  rows another one holds, instead of sending them twice.
- **The SQL names are the parameters of `outbox_row`.** psycopg's `kwargs_row` passes every column
  of the result to the function by its name [9], so the aliases in the claim reach `outbox_row`,
  which parses the id and the key once. A key outside `RoutingKey` fails the claim with a
  `ValueError`, and the worker stops before anything is sent
  ([python.md](../language/python.md) section 3). The delete passes a Python list, which psycopg
  sends as an array for `= ANY()`, and which works for an empty batch too [5].
- **The broker's error becomes one module error with the event's id**, raised and not logged, so
  the loop, which decides what happens next, logs it once ([logging.md](../logging/logging.md)
  section 5). A returned event becomes `EventReturnedError`, a kind of it the loop logs with a
  line of its own (section 8). `raise ... from None` drops the broker's error: a `DeliveryError`
  keeps the message it is about in its `message` attribute [4], and aiormq's delivered message
  holds the body [10].

## 8. The loop and the worker's entry point

`src/acme/worker/handlers_relay_outbox.py`:

```python
"""The worker's way into relay_outbox: a poll loop that runs until the worker stops."""

import asyncio
import contextlib
import logging

from acme.orders.relay_outbox.errors import EventNotPublishedError, EventReturnedError
from acme.orders.relay_outbox.schemas import RelayOutcome
from acme.orders.relay_outbox.usecase import RelayOutbox

logger = logging.getLogger(__name__)


async def relay_until_stopped(
    relay: RelayOutbox, stop: asyncio.Event, *, poll_interval_seconds: float
) -> None:
    while not stop.is_set():
        try:
            outcome = await relay.run()
        except EventNotPublishedError as error:
            # Handled here, once: the batch waits in the outbox for the next poll
            # (logging.md section 5).
            _log_refused_batch(error)

            # Wait here too, so a broker that is down is asked once per poll.
            await _wait_unless_stopped(stop, poll_interval_seconds)

            continue

        # An empty outbox, or another relay's turn: wait instead of polling in a loop.
        if outcome is not RelayOutcome.SENT:
            await _wait_unless_stopped(stop, poll_interval_seconds)


def _log_refused_batch(error: EventNotPublishedError) -> None:
    # The id finds the event, and no payload is logged (logging.md section 10).
    if isinstance(error, EventReturnedError):
        # WARNING, not ERROR: every poll retries the batch, and the alarm on a stalled
        # outbox, not this line, calls a person (logging.md section 4).
        logger.warning(
            "Outbox batch left for next poll: no queue takes an event's key",
            extra={"message_id": str(error.event_id)},
        )
    else:
        # WARNING: the relay gets past a nack or a lost connection by itself
        # (logging.md section 4). A connection the heartbeat finds stuck never gets
        # here: its CancelledError ends the worker, whose restart sends the rows.
        logger.warning(
            "Outbox batch left for next poll: broker did not take an event (%s)",
            error.broker_error,
            extra={"message_id": str(error.event_id)},
        )


async def _wait_unless_stopped(stop: asyncio.Event, seconds: float) -> None:
    # A stop ends the wait at once, so a shutdown does not wait out the interval.
    with contextlib.suppress(TimeoutError):
        await asyncio.wait_for(stop.wait(), timeout=seconds)
```

It is good because:

- **The loop is where a refused batch is handled**, so it writes the one line, at `WARNING` in
  both cases ([logging.md](../logging/logging.md) sections 4 and 5). The relay gets past a nack or
  a lost connection by itself. A connection the heartbeat finds stuck is the exception: its
  `asyncio.CancelledError` passes `BROKER_ERRORS` and ends the worker, whose restart sends the
  rows (section 11). A returned event waits until a person binds a queue to its key, but
  every poll retries the batch, and [logging.md](../logging/logging.md) section 4 keeps a step that
  will be retried below `ERROR`: the alarm on a stalled outbox (section 11), not this line, calls a
  person. The line carries the event's id as `message_id`, the field a worker logs in place of a
  request id ([delivery.md](delivery.md) section 9), and names the broker's error by its class
  only.
- **It waits after an empty claim and after a refusal**, so neither an idle outbox nor a broker that
  is down turns the relay into a busy loop against the database. `asyncio.wait_for` cancels the
  wait and raises `TimeoutError` when the interval ends [11], and a set `stop` ends the wait at
  once.
- **It catches only the module's error.** A database error ends the worker; its open transaction
  rolls back, and the rows wait for the next start.

`src/acme/worker/main.py`, as the relay needs it. [consumer-example.md](consumer-example.md)
section 8 adds billing's consumer to `run_worker`: a third connection in the `async with`, and the
relay's statements inside a task group beside the consumer.

```python
"""The worker process: builds each client once, then runs until SIGTERM."""

import asyncio
import logging
import logging.config
import signal
import sys
from importlib.metadata import version

from pydantic import SecretStr

from acme.core.config import Settings
from acme.core.database import connect_database
from acme.core.logging import build_logging_config
from acme.core.rabbitmq_client import connect_rabbitmq, open_event_exchange
from acme.orders.relay_outbox.usecase import RelayOutbox
from acme.worker.handlers_relay_outbox import relay_until_stopped

logger = logging.getLogger(__name__)


def main() -> None:
    settings = Settings()

    logging.config.dictConfig(
        build_logging_config(settings.log_level, settings.log_format)
    )

    try:
        asyncio.run(run_worker(settings))
    except Exception:
        # CRITICAL, with the traceback: the worker cannot go on and exits, and this
        # line, not raw stderr, is what a restart's alert reads (logging.md section 4).
        logger.critical("Worker stopped: it cannot go on", exc_info=True)
        sys.exit(1)


async def run_worker(settings: Settings) -> None:
    stop = asyncio.Event()
    # SIGTERM is what a container stop sends: the relay ends its batch, then the
    # clients close below. A batch whose confirm a broker alarm holds ends with the
    # kill after the grace period instead (outbox-relay-example.md section 11).
    asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, stop.set)

    rabbitmq = await connect_rabbitmq(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        user=settings.rabbitmq_user,
        password=settings.rabbitmq_password,
        vhost=settings.rabbitmq_vhost,
    )

    # The relay's own connection: a transaction another task opened on a shared one
    # would turn the relay's block into a savepoint (delivery.md section 3).
    relay_database = await connect_database(
        host=settings.database_host,
        port=settings.database_port,
        name=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
    )

    async with rabbitmq, relay_database:
        # Confirms are on, and a returned message raises: publish_event returns only
        # after the broker's ack, and an event no queue takes stays in the outbox
        # (message-brokers.md section 8).
        channel = await rabbitmq.channel(publisher_confirms=True, on_return_raises=True)

        relay = RelayOutbox(
            relay_database,
            await open_event_exchange(channel),
            batch_size=settings.outbox_batch_size,
        )

        # INFO, once the clients are built: the line logs the start, with the version
        # and every setting that is not a secret (logging.md sections 4 and 10).
        logger.info(
            "Worker started",
            extra={
                # The version comes from the installed distribution, so nothing reads
                # the environment outside Settings (python.md section 5).
                "version": version("acme"),
                # The dict is built from the class, so a new field joins with no edit
                # and a SecretStr never does. It sits under one key, so no field name
                # clashes with a record attribute (logging.md section 3).
                "settings": {
                    name: value
                    for name, value in settings.model_dump().items()
                    if not isinstance(value, SecretStr)
                },
            },
        )

        await relay_until_stopped(
            relay, stop, poll_interval_seconds=settings.outbox_poll_interval_seconds
        )
```

It is good because:

- **`main()` builds `Settings` first and applies the logging config before anything logs**
  ([python.md](../language/python.md) section 5, [logging.md](../logging/logging.md) section 2).
  `run_worker` turns the settings into clients, each built once at startup and handed in
  ([file-structure.md](../../any-language/file-structure/file-structure.md) sections 4 and 5).
- **The worker logs its start and the error that ends it.** The start is one `INFO` line with the
  service's version and every setting that is not a `SecretStr`, built from the class, so a field
  added later joins the line with no edit and a secret never does
  ([logging.md](../logging/logging.md) sections 4 and 10). An error that leaves `asyncio.run` is
  one `CRITICAL` line with its traceback before the exit code 1
  ([logging.md](../logging/logging.md) section 4). Each
  designed stop of the worker then reaches the log store through the logging config, with its
  level, instead of as raw lines on stderr that an alert on the level never sees.
- **The relay has a database connection and a channel of its own**
  ([message-brokers.md](message-brokers.md) section 5), so the consumer's work never runs inside
  the relay's transaction. The channel raises on a returned message, which a channel does not do
  by default [14], [3], so an event no queue takes is not counted as sent.
- **A container stop ends the process cleanly.** The stop sends SIGTERM, and
  `loop.add_signal_handler` lets the handler set `stop` from inside the event loop [12]. The loop
  finishes the batch it is sending, and leaving the `async with` closes the broker connection and
  the database connection. A batch whose confirm the broker holds back waits with it: under a
  resource alarm RabbitMQ stops reading every connection that publishes [18], and the publish has
  no time limit, aio-pika's default [3]. A stop during an alarm then ends with the kill after the
  grace period (section 11). A process killed in the middle of a batch loses nothing either: its
  open transaction rolls back and the rows stay.

## 9. Why the order holds

The relay sends the events of every module, so it keeps the order the service wrote them in, as
[delivery.md](delivery.md) section 4 step 4 asks. Billing reads one event per order and does not
rely on that order. The claim's `ORDER BY position` and the advisory lock of section 7 are that
step's two halves; why one entity's events get increasing positions is
[delivery.md](delivery.md) section 4, "The write side".

## 10. The tests

No test here runs a real RabbitMQ, a departure from [message-brokers.md](message-brokers.md)
section 16 that section 11 declares with its reason and its cost.

Which code earns which test follows [what-to-test.md](../testing/what-to-test.md) section 2. The two
use cases are flows that reach the database, so each gets a few integration tests through `run()`
against a real PostgreSQL, with the broker cut by a fake exchange
([fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 3). The loop catches an error
and survives it, and waits after an empty claim, so it gets one test of each, in the unit suite
with the relay faked. The settings' placeholder validator and their two `gt=0` bounds each get a
test of the start they stop, in the unit suite too. The suite runs pytest-asyncio in auto mode
with both loop scopes set to `"function"`, as [running-tests.md](../testing/running-tests.md)
sections 1 and 7 give; that configuration block is not repeated here.

`tests/integration/conftest.py`:

```python
"""What the integration suite shares.

One Postgres container per run, its tables emptied after each test.
"""

from collections.abc import AsyncIterator, Iterator
from typing import Final

import pytest
from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from testcontainers.community.postgres import PostgresContainer

from tests.support.connection_postgres import connect_to

# Production runs this major version, so a query that works here works there.
POSTGRES_IMAGE: Final = "postgres:18-alpine"


def apply_migrations(postgres: PostgresContainer) -> None:
    """Create the application's tables with its own migrations."""
    ...  # Left out: the project's migration tool, pointed at this container


@pytest.fixture(scope="session")
def postgres() -> Iterator[PostgresContainer]:
    """One Postgres container for the run, with the application's tables."""
    # Every value set here: unset, the container takes POSTGRES_USER and the others
    # from the machine's environment.
    with PostgresContainer(
        POSTGRES_IMAGE, username="acme", password="password-for-tests", dbname="acme"
    ) as container:
        apply_migrations(container)

        yield container


# This is the default, written out to show the lifetime (fixtures.md section 1);
# PT003 is off.
@pytest.fixture(scope="function")
async def database(
    postgres: PostgresContainer,
) -> AsyncIterator[AsyncConnection[TupleRow]]:
    """A connection to the run's database; its tables are emptied after the test."""
    async with await connect_to(postgres) as conn:
        yield conn

        # TRUNCATE empties every table a test writes, so no test sees another's rows
        # (fixtures.md section 3).
        await conn.execute("TRUNCATE orders, outbox")
```

`tests/support/connection_postgres.py`:

```python
"""A connection to the test run's PostgreSQL, opened the way the worker opens one."""

from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from pydantic import SecretStr
from testcontainers.community.postgres import PostgresContainer

from acme.core.database import connect_database


async def connect_to(postgres: PostgresContainer) -> AsyncConnection[TupleRow]:
    """Open a connection to the run's database the way the worker does."""
    return await connect_database(
        host=postgres.get_container_host_ip(),
        port=postgres.get_exposed_port(postgres.port),
        name=postgres.dbname,
        user=postgres.username,
        password=SecretStr(postgres.password),
    )
```

It is good because the container and its tables live for the session, the slowest thing to build,
and the function-scoped `database` empties every table the suite writes after every test, so no
test sees another's rows ([fixtures.md](../testing/fixtures.md) sections 1 and 3). Each connection
comes from the application's own `connect_database`, autocommit included, so the tests run on the
kind of connection the worker runs on. `connect_to` sits in `tests/support/` because the conftest
and the relay's test file both use it, and the relay's second connection is a fixture of that one
file ([layout.md](../testing/layout.md) section 7, [fixtures.md](../testing/fixtures.md)
section 4). The fixture passes every credential, because `PostgresContainer` falls back to
`POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` from the environment when it is given
none [13], which would let the machine's own configuration into the run.

`tests/integration/place_order/test_usecase.py`:

```python
"""Placing an order against a real database."""

from typing import Final
from uuid import UUID

import pytest
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation
from psycopg.rows import TupleRow
from pydantic import ValidationError

from acme.core.schemas import Currency, EventId, OrderId
from acme.orders.place_order.usecase import PlaceOrder

ORDER_ID: Final = OrderId(UUID("6f1c2b8e-0d4a-4c1e-9b7a-3e5f2a1d0c01"))
SECOND_ORDER_ID: Final = OrderId(UUID("6f1c2b8e-0d4a-4c1e-9b7a-3e5f2a1d0c02"))
EVENT_ID: Final = EventId(UUID("a3d9e4f0-5b6c-4d7e-8f9a-0b1c2d3e4f01"))
# 1250 is 12.50 EUR in cents.
AMOUNT_MINOR: Final = 1250


async def stored_orders(conn: AsyncConnection[TupleRow]) -> list[TupleRow]:
    """Read every order as (id, amount_minor, currency)."""
    cursor = await conn.execute("SELECT id, amount_minor, currency FROM orders")
    return await cursor.fetchall()


async def outbox_rows(conn: AsyncConnection[TupleRow]) -> list[TupleRow]:
    """Read every outbox row, in the order the relay would send it."""
    cursor = await conn.execute(
        "SELECT id, aggregatetype, aggregateid, type, payload FROM outbox"
        " ORDER BY position"
    )
    return await cursor.fetchall()


class TestPlaceOrder:
    """A placed order and its OrderPlaced event commit together, or neither does."""

    async def test_a_placed_order_is_stored(
        self, database: AsyncConnection[TupleRow]
    ) -> None:
        await PlaceOrder(database).run(
            order_id=ORDER_ID,
            event_id=EVENT_ID,
            amount_minor=AMOUNT_MINOR,
            currency=Currency.EUR,
        )

        assert await stored_orders(database) == [(ORDER_ID, AMOUNT_MINOR, "EUR")]

    async def test_a_placed_order_writes_its_event_to_the_outbox(
        self, database: AsyncConnection[TupleRow]
    ) -> None:
        """Pins: the outbox row of OrderPlaced.

        The relay routes on aggregatetype and type, and billing parses the payload; a
        change here sends the event where billing does not listen, or in a shape it
        rejects.
        """
        await PlaceOrder(database).run(
            order_id=ORDER_ID,
            event_id=EVENT_ID,
            amount_minor=AMOUNT_MINOR,
            currency=Currency.EUR,
        )

        assert await outbox_rows(database) == [
            (
                EVENT_ID,
                "orders",
                str(ORDER_ID),
                "order_placed",
                {
                    "event_id": str(EVENT_ID),
                    "order_id": str(ORDER_ID),
                    "amount_minor": AMOUNT_MINOR,
                    "currency": "EUR",
                },
            )
        ]

    async def test_an_order_whose_event_cannot_be_written_is_not_stored(
        self, database: AsyncConnection[TupleRow]
    ) -> None:
        """An order stored without its event would never be charged."""
        await PlaceOrder(database).run(
            order_id=ORDER_ID,
            event_id=EVENT_ID,
            amount_minor=AMOUNT_MINOR,
            currency=Currency.EUR,
        )

        # The same event id again: the outbox's UNIQUE id refuses the second row.
        # PostgreSQL names that constraint outbox_id_key; a refused order row would
        # name orders_pkey instead.
        with pytest.raises(UniqueViolation, match="outbox_id_key"):
            await PlaceOrder(database).run(
                order_id=SECOND_ORDER_ID,
                event_id=EVENT_ID,
                amount_minor=AMOUNT_MINOR,
                currency=Currency.EUR,
            )

        assert [row[0] for row in await stored_orders(database)] == [ORDER_ID]

    async def test_an_order_with_no_amount_is_refused_before_anything_is_stored(
        self, database: AsyncConnection[TupleRow]
    ) -> None:
        """An order of 0 would be stored and published, and billing would dead-letter
        its event, so nobody would charge it.
        """
        with pytest.raises(ValidationError, match="amount_minor"):
            await PlaceOrder(database).run(
                order_id=ORDER_ID,
                event_id=EVENT_ID,
                amount_minor=0,
                currency=Currency.EUR,
            )

        assert (await stored_orders(database), await outbox_rows(database)) == ([], [])
```

It is good because each test pins one promise of the use case through its public `run`
([fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 5), and compares exact
values ([assertions.md](../testing/assertions.md) sections 1 and 2). The second test pins the whole
outbox row, which both the relay and billing read, and its docstring opens with `Pins:`
([test-structure.md](../testing/test-structure.md) section 5). The third test holds the outbox's
promise: it turns red when the two inserts leave the `transaction()` block, because on the
autocommit connection each insert would then commit alone, and the second order would stay stored
without its event. Its `pytest.raises` names the outbox's constraint, so a refused order row cannot
pass for it ([assertions.md](../testing/assertions.md) section 3). The fourth test turns red when
`gt=0` leaves the event's model: the order of 0 is then stored with its outbox row.

`tests/integration/relay_outbox/test_usecase.py`:

```python
"""The relay against a real database, with the broker faked."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Final, override
from uuid import UUID

import aiormq
import pytest
from aio_pika import DeliveryMode, Exchange
from aio_pika.abc import AbstractMessage, TimeoutType
from aio_pika.exceptions import ChannelInvalidStateError, DeliveryError
from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from testcontainers.community.postgres import PostgresContainer

from acme.core.schemas import Currency, EventId, OrderId
from acme.orders.place_order.schemas import OrderPlaced
from acme.orders.place_order.usecase import PlaceOrder
from acme.orders.relay_outbox.errors import EventNotPublishedError
from acme.orders.relay_outbox.repository import take_relay_lock
from acme.orders.relay_outbox.schemas import RelayOutcome
from acme.orders.relay_outbox.usecase import RelayOutbox
from tests.support.connection_postgres import connect_to

ORDER_ID: Final = OrderId(UUID("6f1c2b8e-0d4a-4c1e-9b7a-3e5f2a1d0c01"))
EVENT_ID: Final = EventId(UUID("a3d9e4f0-5b6c-4d7e-8f9a-0b1c2d3e4f01"))
AN_ORDER_PLACED: Final = OrderPlaced(
    event_id=EVENT_ID, order_id=ORDER_ID, amount_minor=1250, currency=Currency.EUR
)
BATCH_SIZE: Final = 10


@dataclass(frozen=True)
class PublishedMessage:
    routing_key: str
    message_id: str | None
    delivery_mode: DeliveryMode
    body: bytes


class FakeExchange(Exchange):
    """An exchange that keeps every message it is asked to publish."""

    def __init__(self) -> None:
        # No super().__init__(): the fake talks to no broker, so it needs no channel.
        self.published: list[PublishedMessage] = []

    @override
    async def publish(
        self,
        message: AbstractMessage,
        routing_key: str,
        *,
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
    ) -> aiormq.spec.Basic.Ack | None:
        self.published.append(
            PublishedMessage(
                routing_key, message.message_id, message.delivery_mode, message.body
            )
        )

        return None


class RefusingExchange(FakeExchange):
    """An exchange whose broker answers every message with a nack."""

    @override
    async def publish(
        self,
        message: AbstractMessage,
        routing_key: str,
        *,
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
    ) -> aiormq.spec.Basic.Ack | None:
        raise DeliveryError(None, aiormq.spec.Basic.Nack(delivery_tag=1))


class ClosedChannelExchange(FakeExchange):
    """An exchange whose channel is closed, as after a lost connection."""

    @override
    async def publish(
        self,
        message: AbstractMessage,
        routing_key: str,
        *,
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
    ) -> aiormq.spec.Basic.Ack | None:
        raise ChannelInvalidStateError("closed")


class LockCheckingExchange(FakeExchange):
    """An exchange that records whether another relay can take the lock mid-batch."""

    def __init__(self, other_relay: AsyncConnection[TupleRow]) -> None:
        super().__init__()
        self._other_relay = other_relay
        self.other_relay_locked: list[bool] = []

    @override
    async def publish(
        self,
        message: AbstractMessage,
        routing_key: str,
        *,
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
    ) -> aiormq.spec.Basic.Ack | None:
        # The other relay starts its own batch while this one is being sent.
        async with self._other_relay.transaction():
            self.other_relay_locked.append(await take_relay_lock(self._other_relay))

        return await super().publish(
            message,
            routing_key,
            mandatory=mandatory,
            immediate=immediate,
            timeout=timeout,
        )


async def place_an_order(conn: AsyncConnection[TupleRow]) -> None:
    """Write AN_ORDER_PLACED to the outbox the way the application does."""
    await PlaceOrder(conn).run(
        order_id=ORDER_ID,
        event_id=EVENT_ID,
        amount_minor=AN_ORDER_PLACED.amount_minor,
        currency=AN_ORDER_PLACED.currency,
    )


async def outbox_event_ids(conn: AsyncConnection[TupleRow]) -> list[UUID]:
    """Read the ids of the events still in the outbox."""
    cursor = await conn.execute("SELECT id FROM outbox ORDER BY position")
    return [row[0] for row in await cursor.fetchall()]


@pytest.fixture(scope="function")
def exchange() -> FakeExchange:
    """An exchange that keeps what it was asked to publish, new for each test."""
    return FakeExchange()


@pytest.fixture(scope="function")
async def second_connection(
    postgres: PostgresContainer,
) -> AsyncIterator[AsyncConnection[TupleRow]]:
    """A second connection, for what another relay holds at the same time."""
    async with await connect_to(postgres) as conn:
        yield conn


class TestRelayOutbox:
    """An outbox row leaves the table only after the broker has taken its event."""

    async def test_a_confirmed_event_leaves_the_outbox(
        self, database: AsyncConnection[TupleRow], exchange: FakeExchange
    ) -> None:
        await place_an_order(database)

        await RelayOutbox(database, exchange, batch_size=BATCH_SIZE).run()

        assert await outbox_event_ids(database) == []

    async def test_an_empty_outbox_is_reported_as_empty(
        self, database: AsyncConnection[TupleRow], exchange: FakeExchange
    ) -> None:
        """The loop waits on EMPTY; a relay that reported SENT would poll in a loop."""
        outcome = await RelayOutbox(database, exchange, batch_size=BATCH_SIZE).run()

        assert outcome is RelayOutcome.EMPTY

    async def test_an_event_the_broker_refuses_stays_in_the_outbox(
        self, database: AsyncConnection[TupleRow]
    ) -> None:
        """A relay that caught the broker's error and deleted the batch anyway would
        lose an order nobody charges.
        """
        await place_an_order(database)
        relay = RelayOutbox(database, RefusingExchange(), batch_size=BATCH_SIZE)

        with pytest.raises(EventNotPublishedError, match=str(EVENT_ID)):
            await relay.run()

        assert await outbox_event_ids(database) == [EVENT_ID]

    async def test_an_event_sent_on_a_closed_channel_stays_in_the_outbox(
        self, database: AsyncConnection[TupleRow]
    ) -> None:
        """A closed channel's error is not an AMQPError; a relay that missed it would
        end the worker instead of keeping the batch for the next poll.
        """
        await place_an_order(database)
        relay = RelayOutbox(database, ClosedChannelExchange(), batch_size=BATCH_SIZE)

        # ChannelInvalidStateError is listed so that the edit this test names fails on
        # match, not as an error (what-to-test.md section 4, step 5).
        with pytest.raises(
            (EventNotPublishedError, ChannelInvalidStateError), match=str(EVENT_ID)
        ):
            await relay.run()

        assert await outbox_event_ids(database) == [EVENT_ID]

    async def test_a_published_event_carries_what_billing_reads(
        self, database: AsyncConnection[TupleRow], exchange: FakeExchange
    ) -> None:
        """Pins: the routing key, the message id, the delivery mode and the body.

        Billing's queue is bound to the key, its log lines carry the id, and it drops
        copies by the same id in the body; a change here loses charges, doubles them
        or hides them from the log.
        """
        await place_an_order(database)

        await RelayOutbox(database, exchange, batch_size=BATCH_SIZE).run()

        assert [
            (
                message.routing_key,
                message.message_id,
                message.delivery_mode,
                OrderPlaced.model_validate_json(message.body),
            )
            for message in exchange.published
        ] == [
            (
                "orders.order_placed",
                str(EVENT_ID),
                DeliveryMode.PERSISTENT,
                AN_ORDER_PLACED,
            )
        ]

    async def test_a_second_relay_sends_nothing_while_another_holds_the_lock(
        self,
        database: AsyncConnection[TupleRow],
        second_connection: AsyncConnection[TupleRow],
        exchange: FakeExchange,
    ) -> None:
        """Two relays sending at once could send one order's events out of order."""
        await place_an_order(database)
        relay = RelayOutbox(database, exchange, batch_size=BATCH_SIZE)

        async with second_connection.transaction():
            # The other relay is in the middle of its batch.
            await take_relay_lock(second_connection)

            await relay.run()

        assert exchange.published == []

    async def test_another_relay_cannot_take_the_lock_while_a_batch_is_sent(
        self,
        database: AsyncConnection[TupleRow],
        second_connection: AsyncConnection[TupleRow],
    ) -> None:
        """A lock that ended before the sends would let a second relay send at once."""
        await place_an_order(database)
        exchange = LockCheckingExchange(second_connection)

        await RelayOutbox(database, exchange, batch_size=BATCH_SIZE).run()

        assert exchange.other_relay_locked == [False]
```

It is good because:

- **The database is real and the broker is a fake that records the messages as data**
  ([fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) sections 1 to 3). The lock, the
  claim and the delete are what the relay does, so they run against PostgreSQL. The fakes subclass
  aio-pika's `Exchange` and override only `publish`, the one method `publish_event` calls, with
  `@override`, so a rename in aio-pika fails the type check. `RefusingExchange` raises
  `DeliveryError`, what aio-pika raises when the broker answers with a nack [3], and
  `ClosedChannelExchange` raises `ChannelInvalidStateError`, the other half of `BROKER_ERRORS`.
  `LockCheckingExchange` asks for the lock from a second connection in the middle of a batch.
- **Each test is one promise of section 7, and one plausible edit turns it red**: a missing delete,
  an empty outbox reported as sent, a relay that catches the broker's error and deletes the batch
  anyway, a `BROKER_ERRORS` without `ChannelInvalidStateError`, a wrong routing key or a missing
  `message_id`, a removed lock check, and a lock taken outside the batch's transaction.
- **The rows come from `PlaceOrder`, the real writer**, so the relay is tested on rows as the
  application writes them. The body is compared after parsing, because `jsonb` keeps its own layout
  of the JSON, and the bytes are not the guarantee: what billing parses is.
- **`second_connection` is a fixture of this file**, the one file that asks for it
  ([fixtures.md](../testing/fixtures.md) section 4).

`tests/unit/worker/test_handlers_relay_outbox.py`:

```python
"""The relay's poll loop, with the relay faked."""

import asyncio
from typing import Final, Literal, override
from uuid import UUID

from acme.core.schemas import EventId
from acme.orders.relay_outbox.errors import EventNotPublishedError
from acme.orders.relay_outbox.schemas import RelayOutcome
from acme.orders.relay_outbox.usecase import RelayOutbox
from acme.worker.handlers_relay_outbox import relay_until_stopped

EVENT_ID: Final = EventId(UUID("a3d9e4f0-5b6c-4d7e-8f9a-0b1c2d3e4f01"))
# Above 0: asyncio.wait_for cancels a wait whose timeout is 0 before it starts. The
# test still does not sleep, because RecordingStop ends each wait at once.
POLL_INTERVAL_SECONDS: Final = 60


class FirstBatchRefusedRelay(RelayOutbox):
    """A relay whose first batch the broker refuses; its second batch stops the loop."""

    def __init__(self, stop: asyncio.Event) -> None:
        # No super().__init__(): the fake reads no database and sends nothing.
        self.batches_run = 0
        self._stop = stop

    @override
    async def run(self) -> RelayOutcome:
        self.batches_run += 1

        if self.batches_run == 1:
            raise EventNotPublishedError(EVENT_ID, broker_error="DeliveryError")

        self._stop.set()

        return RelayOutcome.EMPTY


class AlwaysEmptyRelay(RelayOutbox):
    """A relay that finds the outbox empty; its third batch stops the loop."""

    def __init__(self, stop: asyncio.Event) -> None:
        # No super().__init__(): the fake reads no database and sends nothing.
        self.batches_run = 0
        self._stop = stop

    @override
    async def run(self) -> RelayOutcome:
        self.batches_run += 1

        # The third batch sets the stop, so a loop that never waits still ends, and
        # fails on its assertion.
        if self.batches_run == 3:
            self._stop.set()

        return RelayOutcome.EMPTY


class RecordingStop(asyncio.Event):
    """A stop event that counts each wait on it and ends the wait by setting itself."""

    def __init__(self) -> None:
        super().__init__()
        self.waits = 0

    @override
    async def wait(self) -> Literal[True]:
        self.waits += 1

        self.set()

        return True


class TestRelayUntilStopped:
    """The relay keeps polling after a refused batch, and waits after an empty claim."""

    async def test_a_refused_batch_does_not_stop_the_relay(self) -> None:
        stop = asyncio.Event()
        relay = FirstBatchRefusedRelay(stop)

        # A zero interval means no wait between polls, so the test does not sleep.
        await relay_until_stopped(relay, stop, poll_interval_seconds=0)

        assert relay.batches_run == 2

    async def test_an_empty_outbox_makes_the_relay_wait_before_its_next_claim(
        self,
    ) -> None:
        """A relay that claimed again at once would poll the database in a busy loop."""
        stop = RecordingStop()
        relay = AlwaysEmptyRelay(stop)

        await relay_until_stopped(
            relay, stop, poll_interval_seconds=POLL_INTERVAL_SECONDS
        )

        assert (relay.batches_run, stop.waits) == (1, 1)
```

It is good because each fake overrides the one method the loop calls and records how many batches
ran, the behavior under test ([fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section
2). A loop that returned after the refusal would run one batch and turn the first test red. The
second turns red when the wait after an empty claim goes or its condition flips: the relay then
claims three times without a wait. Its stop event ends the wait at once, so no test sleeps
([running-tests.md](../testing/running-tests.md) section 6), and its relay stops the loop on the
third claim, so the broken loop fails on the assertion instead of running forever. The tests need
nothing outside Python, so they sit in the unit suite ([layout.md](../testing/layout.md) section 2),
and they read no log line ([logging.md](../logging/logging.md) section 11).

`tests/unit/core/test_config.py` is [settings-example.md](../language/settings-example.md)'s. Its
imports are left out, and its `environment` fixture and its other tests are cut with `...`. The
relay's required settings join `VALID_ENVIRONMENT`, so the missing-value test gets a row for each,
the RabbitMQ password joins the placeholder test's rows, and two new tests pin the two `gt=0`
bounds, one each, since two named tests read better than a table of two
([test-structure.md](../testing/test-structure.md) section 7):

```python
VALID_ENVIRONMENT: Final = {
    "ACME_DATABASE_HOST": "db.example.com",
    "ACME_DATABASE_PORT": "5432",
    "ACME_DATABASE_NAME": "shop",
    "ACME_DATABASE_USER": "shop",
    "ACME_DATABASE_PASSWORD": "db-password-for-tests",
    "ACME_PAYMENTS_API_KEY": "payments-key-for-tests",
    "ACME_RABBITMQ_HOST": "rabbitmq.example.com",
    "ACME_RABBITMQ_PORT": "5671",
    "ACME_RABBITMQ_USER": "shop",
    "ACME_RABBITMQ_PASSWORD": "rabbitmq-password-for-tests",
    "ACME_RABBITMQ_VHOST": "acme",
}

...


class TestSettings:
    ...  # The other tests of settings-example.md

    @pytest.mark.parametrize(
        "name",
        [
            pytest.param(name, id=name)
            for name in [
                "ACME_DATABASE_PASSWORD",
                "ACME_PAYMENTS_API_KEY",
                "ACME_RABBITMQ_PASSWORD",
            ]
        ],
    )
    def test_a_placeholder_secret_stops_the_start(
        self, environment: pytest.MonkeyPatch, name: str
    ) -> None:
        environment.setenv(name, PLACEHOLDER_SECRET)

        with pytest.raises(ValidationError, match="placeholder"):
            Settings(_env_file=None)

    def test_a_batch_size_of_zero_stops_the_start(
        self, environment: pytest.MonkeyPatch
    ) -> None:
        """A batch of 0 never sends an event."""
        environment.setenv("ACME_OUTBOX_BATCH_SIZE", "0")

        with pytest.raises(ValidationError) as caught:
            Settings(_env_file=None)

        errors = caught.value.errors(include_input=False)
        assert [(error["loc"], error["type"]) for error in errors] == [
            (("outbox_batch_size",), "greater_than")
        ]

    def test_a_poll_interval_of_zero_stops_the_start(
        self, environment: pytest.MonkeyPatch
    ) -> None:
        """A poll interval of 0 turns the relay into a busy loop."""
        environment.setenv("ACME_OUTBOX_POLL_INTERVAL_SECONDS", "0")

        with pytest.raises(ValidationError) as caught:
            Settings(_env_file=None)

        errors = caught.value.errors(include_input=False)
        assert [(error["loc"], error["type"]) for error in errors] == [
            (("outbox_poll_interval_seconds",), "greater_than")
        ]
```

It is good because each rule the relay adds to the settings has a test of its consequence, a start
that stops, and not of the declared value ([what-to-test.md](../testing/what-to-test.md)
section 2): delete `"rabbitmq_password"` from the validator, or one `gt=0`, and exactly its row
or its test turns red. A required field the relay adds gets its missing-value row from
`VALID_ENVIRONMENT` alone, the way settings-example.md builds that test.

## 11. Where the example stops

- **It was not run here.** The code was written against the sources of aio-pika 10.2.1, aiormq
  7.2.4, psycopg 3.3.6 and testcontainers 4.15.0 [3], [4], [9], [13], and was not run, linted or
  type-checked. The edit that each test names as turning it red was reasoned from the code, not
  run.
- **An event that no queue is bound to stops the relay.** RabbitMQ confirms a message once the
  exchange finds no queue for it, and returns it first when it was published as mandatory [2].
  On the relay's channel, opened with `on_return_raises=True`, aio-pika raises `PublishError` for
  the returned message instead of handing it back [3]. The relay then keeps the batch, and every
  event behind the returned one waits, with one `WARNING` line on each poll, until a queue is bound
  to its key. The cost meanwhile: the rows ahead of the returned one in its batch are sent again
  on every poll, and the consumers drop the copies.
  Declare each subscriber's queue, bound to its keys, before the first event with those keys is
  written, as `open_billing_queue` declares billing's queue when its worker starts
  ([message-brokers.md](message-brokers.md) section 8). The other way, a channel that hands the
  message back, lets the relay delete the row and lose the event without a word.
- **A new event key needs the worker first.** A new event key reaches the relay before its
  `RoutingKey` member does when the code that writes the key deploys first, or when the worker is
  rolled back past it. The claim then fails on every start, and the worker restarts in a loop,
  with every event behind that row waiting. Deploy the worker with the new member first, and never
  roll the worker back past a key the outbox already holds ([delivery.md](delivery.md) section 8).
- **A stuck connection ends the worker.** When no frame arrives within the heartbeat's grace
  time, aiormq cancels its reader and closes the connection with that `asyncio.CancelledError` as
  the reason [16], and the close fails every pending future with it, the confirm the relay waits
  for included [17]. `CancelledError` is a `BaseException`, so it passes `BROKER_ERRORS` and the
  `except Exception` of `main()`: the worker exits with the traceback on stderr, its transaction
  rolls back, and its restart sends the rows. In consumer-example.md's worker the task group
  cancels billing's consumer too.
- **A resource alarm holds the batch.** Under a memory or disk alarm RabbitMQ blocks every
  connection that publishes: "When a connection is blocked, no more data sent by this connection
  will be read, parsed or processed on the connection" [18]. The confirm has no time limit, so the
  batch, its transaction, the advisory lock and the claimed rows wait until the alarm clears. A
  SIGTERM in that time ends with the kill after the grace period; the transaction rolls back and
  the rows stay.
- **Every process that builds `Settings` holds every secret.** The application's one settings
  class requires the database password, the payments API key and the broker password
  ([settings-example.md](../language/settings-example.md), section 4 here), so the API holds a
  broker credential it never uses, the worker holds a payments key it never uses, and a leak of
  either environment leaks both.
- **What no test pins.** `autocommit=True`: every statement here runs inside a `transaction()`
  block, so no test of this code turns red without it; it guards the next query someone writes
  outside a block ([delivery.md](delivery.md) section 3). The send order: without `ORDER BY`,
  PostgreSQL returns rows "in whatever order the system finds fastest to produce" [1], which for a
  few rows just inserted can be the order they were written in, so a test of the order could pass
  with the clause gone ([what-to-test.md](../testing/what-to-test.md) section 4, step 5); review
  keeps it.
  That the exchange and a dead-lettered copy survive a broker restart: no test restarts a broker,
  and the `Pins:` test checks only the mode each message carries. The wait after a refusal: the
  refused-batch test polls with no interval, so a loop that went straight back to the broker
  after a refusal would pass it; review keeps the wait.
- **The broker's side is not tested**, a departure from [message-brokers.md](message-brokers.md)
  section 16, whose checks ask for an integration test against a real RabbitMQ in testcontainers.
  The tests fake the broker and start no broker container; the broker's container, and the run of
  [consumer-example.md](consumer-example.md) section 4's script against it, are left out, as in
  consumer-example.md section 10. The cost: nothing checks that `publish_event` passes
  `mandatory=True`, that the channel raises on a returned message, that a returned event stays in
  the outbox, or that the exchange is durable, because those act only on a real broker.
- **Left out: the alarm on a stalled outbox.** A relay held back by a returned event, or by a
  broker that stays down, logs a line on each poll and tells no one. An alarm that fires when the
  oldest outbox row, the one with the smallest `position`, stays in the table longer than a
  threshold calls a person. The monitoring system reads the outbox for it with a read-only
  database user, never the worker's.
- **A relay to Kafka** deletes its rows in the delivery callback or after `flush()`, never right
  after `produce()` ([event-streaming.md](event-streaming.md) section 4).
- **`loop.add_signal_handler` is Unix only** [12]; the worker runs in a Linux container.
- **Old rows need no cleaning.** The relay deletes each row it sent, so the table holds only events
  not yet confirmed. The consumer's table of processed ids does need cleaning
  ([delivery.md](delivery.md) section 3).

## 12. Sources

Checked 2026-10-30 unless a line ends with — checked <YYYY-MM-DD>.

- [1] PostgreSQL Global Development Group — SQL Commands: SELECT, PostgreSQL 18 — https://www.postgresql.org/docs/current/sql-select.html — checked 2026-10-29
- [2] RabbitMQ — Consumer Acknowledgements and Publisher Confirms, docs version 4.4 — https://www.rabbitmq.com/docs/confirms — checked 2026-10-29
- [3] aio-pika — `aio_pika/exchange.py` (`Exchange.publish`), 10.2.1 — https://github.com/mosquito/aio-pika/blob/10.2.1/aio_pika/exchange.py
- [4] aiormq — `aiormq/exceptions.py`, 7.2.4 — https://github.com/mosquito/aiormq/blob/7.2.4/aiormq/exceptions.py
- [5] Psycopg — Adapting basic Python types, documentation 3.3.7.dev1 — https://www.psycopg.org/psycopg3/docs/basic/adapt.html
- [6] PostgreSQL Global Development Group — System Administration Functions: Advisory Lock Functions, PostgreSQL 18 — https://www.postgresql.org/docs/18/functions-admin.html
- [7] PostgreSQL Global Development Group — Explicit Locking: Advisory Locks, PostgreSQL 18 — https://www.postgresql.org/docs/18/explicit-locking.html
- [8] Brandur Leach — Transactionally Staged Job Drains in Postgres (brandur.org, 2017; opinion) — https://brandur.org/job-drain — checked 2026-10-29
- [9] psycopg — `psycopg/rows.py` (`kwargs_row`), 3.3.6 — https://github.com/psycopg/psycopg/blob/3.3.6/psycopg/psycopg/rows.py
- [10] aiormq — `aiormq/abc.py` (`DeliveredMessage`), 7.2.4 — https://github.com/mosquito/aiormq/blob/7.2.4/aiormq/abc.py
- [11] Python — asyncio: Coroutines and Tasks (`asyncio.wait_for`), Python 3.15.2 — https://docs.python.org/3/library/asyncio-task.html
- [12] Python — asyncio: Event loop (`loop.add_signal_handler`), Python 3.15.2 — https://docs.python.org/3/library/asyncio-eventloop.html
- [13] testcontainers-python — `testcontainers/community/postgres/__init__.py` (`PostgresContainer`), 4.15.0 — https://github.com/testcontainers/testcontainers-python/blob/testcontainers-v4.15.0/src/testcontainers/community/postgres/__init__.py
- [14] aio-pika — `aio_pika/abc.py` (`AbstractRobustConnection.channel`), 10.2.1 — https://github.com/mosquito/aio-pika/blob/10.2.1/aio_pika/abc.py
- [15] PostgreSQL Global Development Group — libpq: SSL Support, PostgreSQL 18 — https://www.postgresql.org/docs/18/libpq-ssl.html
- [16] aiormq — `aiormq/connection.py` (`Connection.__heartbeat`, `_on_reader_done`), 7.2.4 — https://github.com/mosquito/aiormq/blob/7.2.4/aiormq/connection.py
- [17] aiormq — `aiormq/base.py` (`FutureStore.reject_all`), 7.2.4 — https://github.com/mosquito/aiormq/blob/7.2.4/aiormq/base.py
- [18] RabbitMQ — Publishers, docs version 4.4 — https://www.rabbitmq.com/docs/publishers — checked 2026-10-29
