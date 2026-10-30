# Delivery rules

The rules every job in this practice shares: what can happen to a message on its way, and how the
code that sends it and the code that receives it stay correct when it does.

**Navigation**

- [1. Purpose and scope](#1-purpose-and-scope)
- [2. Every message can arrive twice, late or out of order](#2-every-message-can-arrive-twice-late-or-out-of-order)
- [3. Idempotent consumers](#3-idempotent-consumers)
- [4. The outbox: send only what the database committed](#4-the-outbox-send-only-what-the-database-committed)
- [5. Retries and delayed retries](#5-retries-and-delayed-retries)
- [6. Dead-letter queues](#6-dead-letter-queues)
- [7. Ordering](#7-ordering)
- [8. Message contracts](#8-message-contracts)
- [9. Tracing and ids across a message](#9-tracing-and-ids-across-a-message)
- [10. Security and personal data in messages](#10-security-and-personal-data-in-messages)
- [11. Common mistakes](#11-common-mistakes)
- [12. Where the rules stop holding](#12-where-the-rules-stop-holding)
- [13. Alternatives considered](#13-alternatives-considered)
- [14. Sources](#14-sources)

## 1. Purpose and scope

This file is for everyone, people and AI agents alike, who writes or changes Python code that
sends or receives a message: a task for a task queue, a message for a broker, an event for a
stream, a step of a durable workflow, a scheduled job. Each job file of this practice keeps what
is specific to its tools and links the sections here; [README.md](README.md) says which job file
is yours.

The problem: on its way, a message can arrive twice, late or out of order, and the code that
sends it can send it twice. A consumer crashes after its work but before its acknowledgement, and
the broker delivers the message again. A producer commits a change and crashes before it sends
the event, or sends the event for a change that then rolls back. Section 2 shows that every tool
in this practice works this way by default.

A project that follows these rules loses no committed change and applies none twice, whatever the
broker delivers again.

The one rule: **assume every message arrives at least once, maybe more than once and out of
order. The consumer records each message it processed in the same database transaction as its
work, and the producer sends only what its database committed.**

What this file leaves out on purpose:

- Running the servers: clustering, upgrades, capacity and the broker's own hardening.
- The general retry rule for calls between services: which layer retries, how many retries a
  call may spend, and the shape of the backoff. Section 5 keeps only what a consumer needs: each
  tool's defaults, how to make a retry wait, and the choice between the broker's delay and
  backoff in code.
- The outbox's write side beyond what the relay needs. For the relay's sake, section 4 states the
  write side's rule with its BAD and GOOD, the table the relay reads, the insert order the relay's
  ordering rests on, and the check on use cases.

Not covered yet, because the research found no source that settles it:

- how long to keep the ids of processed messages (section 3 gives the practice's own reasoning,
  not a rule);
- a measured comparison of a broker's delayed retry with backoff in code (section 5);
- the point where one outbox relay at a time stops keeping up (section 12);
- whether a Procrastinate job deferred inside Django's `transaction.atomic()` joins that
  transaction (section 4);
- a consumer-side check that drops a message older than the state it would change, such as a
  version number on each message (section 7).

The snippets assume Python 3.11 or newer and psycopg 3 on an autocommit connection. File names
follow [file-structure.md](../../any-language/file-structure/file-structure.md): a module's
`schemas.py`, `usecase.py` and `repository.py`.

## 2. Every message can arrive twice, late or out of order

This holds for every project that sends or receives a message. The research found no tool
where it does not hold, so there is no case where this section is too much. Read it before you
trust a tool's promise of "exactly once".

At least once is the default, and it is what you get:

- SQS: "Standard queues ensure at-least-once message delivery, but due to the highly distributed
  architecture, more than one copy of a message might be delivered, and messages may occasionally
  arrive out of order." [1]
- Kafka: "Kafka guarantees at-least-once delivery by default" [2].
- Dramatiq acknowledges a message only after the actor succeeds. When a worker goes down, the
  messages it pulled "will eventually be re-delivered to it (assuming it recovers) or another
  worker." [3]
- Celery, by default, acknowledges a message just before the task runs. With `acks_late=True` it
  acknowledges after, and then "the task may be executed multiple times should the worker crash in
  the middle of execution" [4]. Under the default, a crash in the middle loses the
  task instead, because the broker removed the message before the work began.
- Temporal retries activities, so "these functions may be executed more than once"
  [5]. DBOS: "Steps are tried at least once but are never re-executed after they
  complete." [6]

Why it cannot be otherwise: the acknowledgement travels after the work. When a consumer crashes
between the two, the broker cannot tell that crash from a crash before the work, so it delivers
the message again. Microsoft's guide gives this case: when a consumer fails while processing,
Service Bus returns the message to the queue and a consumer gets it again [7].

A message also comes late, or twice, when its consumer does not settle it in time. SQS hides a
received message for the visibility timeout, 30 seconds by default, and shows it again when nobody
deletes it; "Amazon SQS doesn't guarantee that a message won’t be delivered more than once within
the visibility timeout period." [8] Retries and delays (section 5) make a message
later still. Order is section 7.

"Exactly once" exists in a few places, each with a narrow edge:

| Tool | What it promises | Where it stops |
|---|---|---|
| Google Pub/Sub | exactly-once delivery, when you turn it on | "Only the pull subscription type supports exactly-once delivery", and "The exactly-once delivery guarantee only applies when subscribers connect to the service in the same region." A failed acknowledgement still means a redelivery [9]. |
| Azure Service Bus | it removes the duplicates a producer sends | "Service Bus might still deliver a message twice." [7] |
| Kafka | exactly once when a consumer reads, processes and writes Kafka topics, through transactions | "Exactly-once delivery for other destination systems generally requires cooperation with such systems" [2]. Your database is such a system. Whether to build on them from Python is [event-streaming.md](event-streaming.md) section 3. |
| Temporal | "Temporal guarantees that the Activity will be observed as completed exactly once." [5] | The activity's function may still run more than once [5]. |
| DBOS | a step that completed never runs again [6] | A step is "tried at least once", so one that fails midway can run again [6]. |

**Write every consumer for at-least-once delivery, whatever exactly-once setting its tool has.**
Why: each promise above stops at the edge of its tool, and the work your consumer does in its own
database is outside that edge.

## 3. Idempotent consumers

Applies when a consumer changes state: it writes a row, moves money, sends an email or calls
another service. Chris Richardson's example is a consumer of an `AccountDebited` message: if it
subtracts the amount from the balance twice, the balance is wrong [10].

Too much when the effect is already the same however often it runs. The Enterprise Integration
Patterns name two ways to idempotency: explicit "de-duping", and "Defining the message semantics
to support idempotency" [11]. When a message carries a whole new state that the consumer
writes over the old one, the second way is the simpler one, and it needs no id table. A consumer
that only reads needs neither.

How to build it:

1. **The producer gives every message an id and sends it in a header.** Why: the consumer can
   find a copy without parsing the body. Debezium's outbox router stores the event id "in the
   emitted event’s headers under the id key" [12], and Gunnar Morling of the Debezium project
   says this "allows for efficient duplicate detection by consumers, without having to examine the actual
   message contents." [13] In AMQP the header is the `message_id` property; in Kafka
   it is a record header, which Confluent's asyncio producer does not set per message
   ([event-streaming.md](event-streaming.md) section 4). A Kafka consumer can instead store its
   offset with its output, which Kafka's design page suggests ("letting the consumer store its offset in the same place as its
   output") [2]. That catches a record read twice. A producer or a relay that
   publishes twice writes two records with two offsets, though, and only an id the producer set
   catches the second one.
2. **In one transaction, insert the id, then do the work.** Richardson's Idempotent Consumer
   records "the IDs of processed messages in the database", in a table whose primary key is the
   subscriber and the message id; the INSERT fails for a message already processed, and the
   handler rolls back and ignores it [10]. Use `ON CONFLICT DO NOTHING` and test the
   row count instead of catching the error. Why: after a failed statement, PostgreSQL ignores every
   command "until end of transaction block", as psycopg's docs put it [16], so a caught error
   leaves nothing to commit the work with. Why one transaction:
   the id row and the work commit together or not at all, so a crash cannot leave an id without
   its work (a lost message) or work without its id (a duplicate next time).
3. **Acknowledge after the commit, never before.** A crash between the commit and the
   acknowledgement makes the broker deliver again, and the id row then skips the copy. How each
   tool does it: [task-queues.md](task-queues.md) section 5;
   [message-brokers.md](message-brokers.md) sections 5 and 9 for RabbitMQ and section 10 for SQS;
   [event-streaming.md](event-streaming.md) section 6 for Kafka. Section 12 names the one case
   where the order may be the other way.
4. **Key the table by the consumer and the message id.** Why: two consumers of one message each
   keep their own row, as Richardson's primary key does [10].
5. **Delete old ids on a schedule.** No source we read gives a rule for how long to keep them.
   The practice's own reasoning: keep an id for as long as a copy of its message can still
   arrive, that is while the message can sit in its queue, in its dead-letter queue (section 6), or
   in a topic a consumer may read again. Then delete older rows in batches.

The use case, its result type and its query; the payment query and the `OrderPaid` model are left
out:

```python
# src/acme/billing/payments/schemas.py
# What one run did with one message: a closed set, so the caller can tell a copy
# from a payment (python.md section 2).
@unique
class PaymentOutcome(StrEnum):
    RECORDED = "recorded"
    ALREADY_PROCESSED = "already_processed"
```

```python
# src/acme/billing/payments/repository.py
# One row per consumer and message (delivery.md section 3).
CONSUMER: Final = "billing.payments"


async def claim_message(conn: AsyncConnection[TupleRow], message_id: UUID) -> bool:
    """Record the message id; False when this consumer has processed it already."""
    cursor = await conn.execute(
        "INSERT INTO processed_message (consumer, message_id) VALUES (%s, %s)"
        # A copy inserts no row and leaves the transaction usable.
        " ON CONFLICT DO NOTHING",
        (CONSUMER, message_id),
    )
    return cursor.rowcount == 1
```

```python
# src/acme/billing/payments/usecase.py
async def record_payment(
    conn: AsyncConnection[TupleRow], message_id: UUID, paid: OrderPaid
) -> PaymentOutcome:
    # One transaction: the id row and the payment commit together, or neither does.
    async with conn.transaction():
        if not await repository.claim_message(conn, message_id):
            # A copy of a message this consumer has already processed.
            return PaymentOutcome.ALREADY_PROCESSED
        await repository.insert_payment(conn, paid)
    return PaymentOutcome.RECORDED
```

The adapter acknowledges only after the use case returns:
[message-brokers.md](message-brokers.md) section 9 shows it for aio-pika and section 10 for SQS,
[event-streaming.md](event-streaming.md) section 6 for Kafka, and
[consumer-example.md](consumer-example.md) in full.

Why this is good: the id insert and the payment run in one `transaction()` block, which commits
when the block ends [16]. The acknowledgement comes after that block, so every crash
leads to a redelivery that the id row absorbs. The connection must be in autocommit mode: on a
connection that already has a transaction open, the same block is only a savepoint and commits
nothing [16], and the acknowledgement would then come before the commit. Both paths return a
`PaymentOutcome`, so a skipped copy reads differently from a recorded payment
([python.md](../language/python.md) section 2). The query lives in `repository.py`, the `if` in
`usecase.py` and the result type in `schemas.py`, as
[file-structure.md](../../any-language/file-structure/file-structure.md) section 3 puts them.

When you judge a library that says it removes duplicates for you, ask four questions. Each comes
from a problem above:

- Does it write the id on your connection, inside your transaction? If it commits on its own
  connection, a crash between its commit and yours loses the work or repeats it.
- Does it acknowledge only after your transaction commits?
- Is the key the consumer and an id the producer set?
- Does it say how and when old ids are removed?

Check: in each consumer, does the id insert sit inside the block that commits?

Check: in each consumer, does the acknowledgement come after that block?

## 4. The outbox: send only what the database committed

Applies when code changes its database and must tell another service about the change through a
broker, and both of Richardson's conditions hold: "If the database transaction commits then the
messages must be sent", and if it rolls back they must not [18]. Too much in two
cases. The first: the worker reads its jobs from the same PostgreSQL. Then deferring the job
inside the transaction does the outbox's work with no relay (the end of this section). The second:
a lost message, or one sent for a change that rolled back, does no harm.

Why not send it directly: Richardson notes that "sending a message in the middle of a transaction
is not reliable", and that a service that sends after the commit has "no guarantee that it won’t
crash before sending the message" [18]. Brandur Leach, introducing River, a job
queue for Go and PostgreSQL that he co-wrote, names the same two failures for jobs: "A job is
emitted from a transaction which then rolls back.", and "a brief moment between the commit and job
emit where if the process crashes or there's a bug, the job is gone" [19].

### The write side

**Store the message in an outbox table in the same transaction as the change.** Richardson: "The
solution is for the service that sends the message to first store the message in the database as
part of the transaction that updates the business entities." [18] A separate
process, the relay, then sends it.

```python
# Bad: the dual write. A crash between the commit and the publish loses the event.
async def mark_paid(
    conn: AsyncConnection[TupleRow], broker: BrokerClient, order_id: int
) -> None:
    async with conn.transaction():
        await repository.set_status(conn, order_id, OrderStatus.PAID)
    await broker.publish("order.paid", OrderPaidEvent(order_id=order_id))
```

The event goes out only if the process lives past the commit, which is the failure Richardson's
page describes [18].

```python
# Good: the event is a row in the same transaction; the relay sends it after the commit.
async def mark_paid(conn: AsyncConnection[TupleRow], order_id: int) -> None:
    async with conn.transaction():
        await repository.set_status(conn, order_id, OrderStatus.PAID)
        # After the status: the row lock orders this entity's outbox rows
        # (delivery.md section 4).
        await repository.add_outbox_message(
            conn, order_id, OrderPaidEvent(order_id=order_id)
        )
```

Why this is good: it fixes the dual write. The change and its event commit together or not at
all, and the `broker` parameter is gone because the use case no longer sends anything. The outbox
row comes after the update of the entity. The practice's own reasoning for that order: the update
locks the entity's row, so a second transaction on the same entity waits for this one to commit
before it adds its own outbox row, and its row then gets the later position.

The table. Its column names (`id`, `aggregatetype`, `aggregateid`, `type`, `payload`) are the
ones Debezium's outbox router reads by default; a table with other names works with log tailing
when the router's `table.field.event.*` and `route.by.field` options name them [12]:

```sql
CREATE TABLE outbox (
    -- The polling relay sends in this order.
    position      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- The message id consumers dedup on (section 3).
    id            uuid NOT NULL UNIQUE,
    -- Where the relay sends it: a topic or an exchange.
    aggregatetype text NOT NULL,
    -- The key that keeps one entity in order (section 7).
    aggregateid   text NOT NULL,
    -- The event's name.
    type          text NOT NULL,
    payload       jsonb NOT NULL
);
```

Why this is good: every column a relay needs is there, and nothing more. The `id` is the id
consumers use against duplicates, and it is unique, so one message never gets two rows.
`aggregateid` is the key for order, and `position`, the primary key, gives a polling relay an
order to read in.

Check: does any use case that changes the database also call the broker client itself? If so, the
message needs an outbox row.

### The relay: polling

Applies when the outbox lives in PostgreSQL and no change-data-capture pipeline runs. It is the
simpler of the two ways: one more process, and no server you do not already run.

1. **Claim a batch in order with `FOR UPDATE SKIP LOCKED`.** PostgreSQL's docs say skipping locked
   rows "is not suitable for general purpose work, but can be used to avoid lock contention with
   multiple consumers accessing a queue-like table." [20] Why: a second relay, during a
   deploy or as a second replica, skips the rows the first one holds instead of sending them too.
2. **Send each row and wait until the broker accepts it:** a publisher confirm in RabbitMQ, for
   a message published as mandatory ([message-brokers.md](message-brokers.md) section 8), a
   delivery report in Kafka ([event-streaming.md](event-streaming.md) section 4), a successful
   response from SQS. AWS's version of the pattern sends
   the events and deletes them "if Amazon SQS responds successfully" [21].
3. **Delete the rows, or mark them sent, in the same transaction, and commit.** Brandur Leach's job
   drain removes jobs only after they were sent to the queue [22]. Why: a row deleted
   before the broker took it is a lost message.
4. **Keep the order the service wrote in.** AWS: "Send messages or events in the same order in
   which the service updates the database." [21] Richardson asks that this order hold
   across service instances that update the same aggregate [18]. One relay at a
   time keeps it: Leach's relay takes a lock so that only one runs [22]. In PostgreSQL, take
   `pg_try_advisory_xact_lock` first in each batch's transaction: it takes the lock at once or
   returns false without waiting [80], and the lock is released when the transaction ends, with
   no unlock to forget [81]. Several relays
   with `SKIP LOCKED` do not block each other, but two rows of one entity can then leave through
   two relays in either order. Run several only where consumers do not need that order.
5. **Expect duplicates.** "The Message relay might publish a message more than once."
   [18] A crash after the sends and before the commit sends the batch again, so
   every consumer must be idempotent (section 3); AWS gives the same advice [21].

The claim query and one pass of the relay; the broker client, the row type, the `BATCH_SIZE`
constant, the `take_relay_lock` query (`SELECT pg_try_advisory_xact_lock(%s)` with the relay's
key) and the loop that calls `relay_batch` are left out:

```sql
SELECT id, aggregatetype, aggregateid, type, payload
FROM outbox
ORDER BY position        -- The order the service wrote in (delivery.md section 4).
LIMIT %(limit)s
FOR UPDATE SKIP LOCKED   -- A second relay skips these rows instead of sending them too.
```

```python
async def relay_batch(conn: AsyncConnection[TupleRow], broker: BrokerClient) -> int:
    async with conn.transaction():
        # One relay at a time keeps the order (step 4); the lock ends with the block.
        if not await repository.take_relay_lock(conn):
            return 0
        rows = await repository.claim_batch(conn, limit=BATCH_SIZE)
        for row in rows:
            # Returns only after the broker accepted it.
            await broker.publish_confirmed(row)
        # Delete after the sends: a crash before the commit sends the batch again,
        # never loses it.
        await repository.delete_rows(conn, [row.id for row in rows])
    return len(rows)
```

Why this is good: the rows stay locked and in the table until the broker has taken every one, so
any failure leaves them to be sent again, and the duplicate this can cause is the one section 3
handles. A second relay finds the advisory lock taken and sends nothing, so the rows leave in the
order step 4 asks for. The cost is a transaction that stays open while the batch is sent, so keep `BATCH_SIZE`
small. A full relay is in [outbox-relay-example.md](outbox-relay-example.md).

### The relay: log tailing with Debezium

Applies when Kafka Connect and Debezium already run next to the database. Too much for a service
that would have to add them only for this, because they are servers to run. Debezium reads the
database's log and its outbox router turns each new row into a message. Capture only the outbox
table: set the connector's `table.include.list` to it, as Morling's set-up does "by means of a
table whitelist" [13], and with the pgoutput plug-in give it a publication for that table alone,
because the default `publication.autocreate.mode`, `all_tables`, creates one "for all tables in
the database" [82]. The router uses `aggregateid` as the message key, which "is important for
maintaining correct order in Kafka partitions" [12]. Morling adds that a consumer then gets the
events of one aggregate
"in the exact order as they were produced" [13]. The router "automatically filters out
`DELETE` operations on an outbox table" [12], so cleaning the table sends nothing.
Richardson lists two drawbacks of log tailing: it "Requires database specific solutions", and it is
"Tricky to avoid duplicate publishing" [23]. Consumers stay idempotent either way.

### Choosing a library

No mature Python outbox library exists yet. On 2026-10-29, faststream-outbox was at 0.20.2,
marked Beta, with 50 releases in all, the first in May 2026 [24]; pactix was at 0.2.0
after two releases [25], and pgrelay at 0.1.2 after three [26]. So the relay
is code you write, or a library you judge against the problems above:

- it writes the outbox row on your connection, inside your transaction;
- it claims rows so that two relays never send the same row at once;
- it deletes or marks a row only after the broker accepted it;
- it says which order it keeps, and what happens to that order with two relays;
- it sets a message id in a header for consumers to check copies against;
- it says that a crash between the send and the delete sends the message again, not that it loses
  it.

### When the worker reads its jobs from the same PostgreSQL

Applies when the job queue is a table in the same PostgreSQL as the data, as with Procrastinate
([task-queues.md](task-queues.md)). The job row is then the outbox and the worker is the relay, so
write the job inside the app's own transaction.

- Procrastinate (3.10.0 [27]) lets you "insert the job within the same transaction as your
  own database operations, enabling patterns like the transactional outbox." Pass your connection
  to `configure(connection=...)`: "The job INSERT will execute on your connection, inside your
  transaction." and "You are responsible for committing." [28]
- Only three connectors take a connection: `SyncPsycopgConnector`, `PsycopgConnector` and
  `SQLAlchemyPsycopg2Connector`. "Other connectors will raise a ConnectorException if connection
  is provided." [28], [29]
- Workers wake only when you commit, and an error on the job's INSERT "may abort your
  transaction"; the docs say to "Use savepoints if you need to isolate the defer from the rest of
  your transaction." [28]
- The docs do not say what happens to a job deferred in a transaction that rolls back. The
  practice's own reasoning: its INSERT never committed, so no worker can see it, and the job never
  runs.
- In Django, Procrastinate's worker "connects using the `DATABASES` settings", and the Django page
  does not say that a defer joins Django's `transaction.atomic()` [30]. Do not rely on
  deferring atomically there; it is not covered yet.

The call, through the one jobs client in `core/`: [task-queues.md](task-queues.md) section 4.

## 5. Retries and delayed retries

Applies when a consumer's work can fail for a while and then succeed: a remote service is down, a
lock is held. Too much when a retry cannot fix the failure, such as a body that does not parse or
a message that breaks a business rule. Send it to the dead-letter queue at once (section 6).
Dramatiq has a setting for that case, `throws`: "An exception or a tuple of exceptions that must
not get retried" [14].

Which layer of a call retries, how many retries a call may spend, and the shape of the backoff
are outside this file. A consumer needs two things from this section: what each tool does by
default, because they differ, and how to make a retry wait.

**Write every setting the code relies on for what happens to work that fails, is late or runs
twice, in the code or in a queue policy the change ships, even when its value is the default.**
That covers retries (whether they run, how many, and the wait between them), delivery limits,
time limits, acknowledgement and offset modes (`auto.offset.reset` among them), start deadlines,
time zones, and the overlap and coalescing of scheduled runs. The settings tables of the job files
list these settings: every row whose "Leave it out when" reads Never is one of them. Look up the
default for the tool and the version you use; the table below gives the retry defaults. Why: the
reader then sees at the line what the code depends on
([python.md](../language/python.md) section 2), and these defaults change between versions. The
quorum-queue delivery limit has defaulted to 20 only since RabbitMQ 4.0, with no limit before
[37], and librdkafka says its `group.protocol` default will change
([event-streaming.md](event-streaming.md) section 7).

| Tool | Retries by default | How many | Wait between attempts |
|---|---|---|---|
| Celery 5.6.3 | No: "By default, no exceptions will be autoretried." A task retries when it calls `self.retry()` or lists exceptions in `autoretry_for` [4]. | `max_retries` 3 [4] | `default_retry_delay` three minutes; `retry_backoff` off, and when on, capped at 600 s with jitter on [4] |
| Dramatiq 2.2.0 | Yes, through the Retries middleware [31] | `max_retries` 20 [14] | exponential, from 15 seconds up to 7 days [31] |
| Procrastinate 3.10.0 | No: `retry` defaults to `False` [29] | an int, `True` for no limit, or a `RetryStrategy` [32] | set by the strategy; "a job waiting to be retried lives in the database" [32] |
| Temporal | Activities yes, Workflows no [33] | no limit [33] | 1 second, doubling, capped at 100 times the first interval [33] |
| DBOS | No: `retries_allowed` defaults to `False` [34] | `max_attempts` 3 when on [34] | 1 second, doubling (`backoff_rate` 2.0) [34] |
| SQS | A message nobody deleted shows again after the visibility timeout, 30 seconds by default [8]. | `maxReceiveCount` in a redrive policy caps it [35] | the visibility timeout |
| RabbitMQ quorum queue | A returned message is not delayed: `delayed-retry-type` defaults to `disabled` in 4.3 and later [36] | a delivery limit of 20 since 4.0 [37] | none, unless delayed retry is on |
| Kafka | No: a failed event is read again only after a restart or a rebalance, when its offset was not stored ([event-streaming.md](event-streaming.md) section 6) | the team's choice, in the consumer loop ([event-streaming.md](event-streaming.md) section 6) | the team's choice; all the attempts together stay well under `max.poll.interval.ms` ([event-streaming.md](event-streaming.md) section 6) |

### Delayed retry per tool

Applies when the tool you use has no wait of its own, such as a plain SQS or RabbitMQ consumer,
or when its wait does not fit. Task queues and workflow engines have their own wait (the table
above).

- **SQS.** To make a retry wait, set the visibility timeout of the message you hold to that wait
  with `ChangeMessageVisibility`, and do not delete the message. The change is not remembered:
  "the visibility timeout for the message reverts to the original timeout value (not to the value
  you set using the `ChangeMessageVisibility` action) the next time the message is received."
  [38] The visibility timeout is capped at 12 hours from the
  first receive, and extending it does not reset that cap [8]. `DelaySeconds` delays a
  new message by up to 15 minutes, and a delay queue hides a message "when it is first added to
  queue" [39]. For longer waits, AWS says "EventBridge Scheduler is the recommended solution
  for advanced message scheduling use cases." [39]
- **RabbitMQ 4.3 and later, quorum queues.** Delayed retry is set per queue, with a queue argument
  or a policy: `delayed-retry-type`, `delayed-retry-min` and `delayed-retry-max`. "The delay is
  calculated using linear backoff", as `min(delayed-retry-min * delivery-count,
  delayed-retry-max)` [36], [37]. The type decides which returns wait: `failed` delays a message
  whose delivery count went up, as after a `basic.reject`; `returned` delays only one whose count
  did not, as after a `basic.nack`; `all` delays both; and the default, `disabled`, delays none
  [37]. A consumer can set an exact delay for one message
  only over AMQP 1.0 [36], while pika [40] and aio-pika [41] speak AMQP 0-9-1.
- **RabbitMQ 4.4 and later, delayed messages on quorum queues.** A message on a quorum queue whose
  `x-opt-delivery-time` is set to a future time, in milliseconds since the Unix epoch, is
  enqueued at once and delivered only when that time comes; AMQP 0-9-1 clients set it as a long
  header [42]. Delaying the redelivery of a message you return is AMQP 1.0 only [42]. From pika or aio-pika, a delayed retry is
  therefore a new message: publish a copy with the header and the same message id, then
  acknowledge the original. A crash between the two leaves two copies with one id, which section 3
  absorbs. The copy starts with a new delivery count, so the delivery limit (section 6) no longer
  counts its attempts; carry the attempt number in a header of your own.
- **RabbitMQ before 4.3, or a classic queue.** Dead lettering with a TTL; the delayed-message
  plugin's own README calls this combination "widely used for basic delays and task retries across
  the RabbitMQ community." [43]
- **Not the delayed-message exchange plugin.** "Team RabbitMQ no longer maintains this project."
  [43] Its README also warns that disabling it loses every delayed message not yet
  delivered [43].
- **Kafka.** The 4.3 design page describes no delayed retry [2]. Spring for Apache
  Kafka builds one from retry topics, and its docs warn: "By using this strategy you lose Kafka's
  ordering guarantees for that topic." [44] The Kafka side is in
  [event-streaming.md](event-streaming.md) section 6.

### The broker's delay, or backoff in code

No owner source compares the two, so this choice is the practice's own reasoning. It covers only
the choice between the two; the shape of a backoff in general is outside this file (section 1).

- **From pika or aio-pika on a quorum queue of RabbitMQ 4.3 or later, use the queue's delayed
  retry with `delayed-retry-type: failed`, and write its minimum and its maximum.** `failed`
  delays a `basic.reject`, which [message-brokers.md](message-brokers.md) section 9 asks for, and
  not a `basic.nack` [37]. Without delayed
  retry, a requeued message is not delayed [37]. The cost: the delay is linear and has no jitter,
  so when one outage fails many messages at the same moment, they come back in step, each wait
  bounded by the maximum. Marc Brooker of AWS simulated many clients competing for one resource
  and found that "The no-jitter exponential backoff approach is the clear loser" [45]. In
  return, the delay keeps the delivery count of section 6 and needs no copy of the message.
- **Republish with a delivery time only when the wait must differ per message and is too long to
  hold in the handler.** From pika or aio-pika that wait is a new message ("RabbitMQ 4.4 and
  later" above), with three costs: it needs RabbitMQ 4.4, the copy starts with a new delivery
  count, so the delivery limit no longer counts its attempts, and a crash between the publish and
  the acknowledgement leaves two copies with one id.
- **Wait inside the handler, then retry the work, only for a short wait that fits well inside the
  consumer timeout** ([message-brokers.md](message-brokers.md) section 9). After the last
  attempt, return the message with `reject(requeue=True)`, so the delivery limit counts it
  (section 6). The costs: the message holds its prefetch slot while it waits, a consumer that
  handles one message at a time stalls, the consumer timeout bounds the wait, and a crash returns
  the message at once, with no wait.

## 6. Dead-letter queues

Applies when a consumer can fail for good on a message: a body that does not parse, a bug, a
broken rule, a service that stays down past the last retry. The research found no case where such
a queue does better without one. Kafka has no dead-letter queue of its own:
[event-streaming.md](event-streaming.md) section 6.

1. **Give every queue a delivery limit and a place for the messages that reach it.** Why: without
   them, a message that always fails comes back for ever, and on a RabbitMQ quorum queue with no
   dead-letter exchange it is dropped at the limit [37]. Per tool:
   - RabbitMQ: the quorum-queue delivery limit defaults to 20 since 4.0 [37]. RabbitMQ
     also dead-letters a message a consumer rejects without requeue (`basic.reject`, or
     `basic.nack` with `requeue` false), a message that expires, and one a length limit drops
     [46].
   - RabbitMQ 4.3 and later count toward the limit a `basic.reject`, a client crash and a lost
     connection; a `basic.nack` and a consumer timeout do not [36], [37]. So a consumer that
     requeues a failing message with `nack` never reaches the limit. How a RabbitMQ consumer
     returns a failure so the limit counts it: [message-brokers.md](message-brokers.md) section 9;
     `delayed-retry-type: failed` spaces the attempts (section 5).
   - SQS: a redrive policy's `maxReceiveCount` is the number of receives before the move to the
     dead-letter queue. Set it high enough to allow the retries you want [35].
   - Dramatiq: a message past its retry or age limits moves to the dead-letter queue, which keeps
     it up to 7 days and then drops it [14].
2. **Make RabbitMQ's dead-lettering at-least-once when the messages matter.** "`at-most-once`
   remains the default dead-letter-strategy for quorum queues" [37], so a message can be
   lost on its way to the dead-letter queue. RabbitMQ keeps the default for messages "more of an
   informational nature" [37]. The cost of at least once: "at-least-once dead-lettering will
   require more system resources such as memory and CPU" [37].
3. **Keep messages in the dead-letter queue longer than in the source queue.** On a standard SQS
   queue, a message keeps its first enqueue time when it moves, so a dead-letter queue with the same
   retention deletes it early. AWS: "it is a best practice to always set the retention period of a
   dead-letter queue to be longer than the retention period of the original queue." [35]
4. **Put an alarm on every dead-letter queue.** This is the practice's own rule. Why: a message in
   a dead-letter queue is work that did not happen, and nobody sees it unless something tells them.
   On SQS, alarm on the dead-letter queue's `ApproximateNumberOfMessagesVisible` [47].
5. **Send a message back only through an idempotent consumer.** A message moved back from the
   dead-letter queue is one more delivery, and section 3 makes it safe.

The settings, for the two brokers this practice covers:

| Setting | What it means | Set it when | Leave it out when |
|---|---|---|---|
| RabbitMQ `delivery-limit` (quorum queue) | returns before the message is dead-lettered or dropped; 20 by default since 4.0 [37] | always, the default's value included (section 5); never `-1`, which turns the limit off and which RabbitMQ advises against, "as repeated requeues can threaten the stability of a queue or RabbitMQ cluster" [37] | never |
| RabbitMQ `delayed-retry-type`, `delayed-retry-min`, `delayed-retry-max` (quorum queue, 4.3 and later) | which returned messages wait before their redelivery, and for how long: the minimum times the delivery count, at most the maximum, in milliseconds; the type is `disabled` by default [37] | always, the default's value included (section 5): `failed`, with its minimum and its maximum, or `disabled` when the code backs off itself (section 5) | never |
| RabbitMQ dead-letter exchange | where rejected, expired and over-limit messages go [46] | always | never: without it, an over-limit message is dropped [37] |
| RabbitMQ `dead-letter-strategy` | `at-most-once` (the default) or `at-least-once` [37] | always, the default's value included (section 5): `at-least-once` whenever a dead-lettered message matters, `at-most-once` for informational messages [37] | never |
| RabbitMQ `overflow` | at-least-once dead-lettering needs it set to `reject-publish`; the default is `drop-head` [37] | with `at-least-once` | otherwise |
| SQS `maxReceiveCount` (redrive policy) | receives before the move to the dead-letter queue [35] | always | never |
| SQS dead-letter queue retention | how long the dead-letter queue keeps a message | always: longer than the source queue's [35] | never |

Check: does every queue the change declares have a dead-letter target and a written delivery
limit, in its arguments or in a policy the change ships?

Check: does every dead-letter queue the change adds have its alarm?

A FIFO queue's dead-letter queue breaks its order: section 7.

## 7. Ordering

Applies when a consumer's result depends on the order of the messages about one thing: a status
that only moves forward, a balance. Too much when each message stands alone. Then several
consumers in parallel are simpler and faster, and no ordering is needed.

Order holds only inside a narrow unit:

| Tool | Order holds within | So |
|---|---|---|
| Kafka | one partition. The key picks it: "if the key chosen was a user id then all data for a given user would be sent to the same partition" [2] | key each message by the entity whose order matters |
| SQS FIFO | one message group. "Messages with different message group IDs may arrive or be processed out of order relative to one another", and a group waits while its first message is in flight [48] | use the entity's id as the group id |
| SQS standard | nothing: messages "may occasionally arrive out of order" [1] | use FIFO when order matters |
| RabbitMQ | a queue with one active consumer: "Enable Single Active Consumer so only one consumer receives messages at a time." With several consumers, "any redelivery can change order" [49] | turn on Single Active Consumer for a queue that needs order |
| An outbox | the relay's order (section 4); with Debezium, the aggregate id as the key [12], [13] | write `aggregateid` as the entity's id |

**Pick the entity whose order matters, and make its id the message's key or group.** Why: order
then holds for each entity, while different entities still run in parallel.

What breaks order even then:

- a retry topic: "By using this strategy you lose Kafka's ordering guarantees for that topic."
  [44];
- a dead-letter queue on a FIFO queue: "Don't use a dead-letter queue with a FIFO queue if you
  don't want to break the exact order of messages or operations." [35];
- a delayed retry, because the next message with the same key passes the one that waits;
- several outbox relays (section 4).

When order must survive a retry, the consumer must hold back the key's later messages until the
first succeeds. SQS FIFO does that for a group while the message is in flight [48]; for
Kafka it is in [event-streaming.md](event-streaming.md) section 6. A check in the consumer that
drops a message older than the state it would change, such as a version number on each message, is
not covered yet: the research found no owner source for it.

## 8. Message contracts

Applies when a message outlives one deploy of its producer or its consumer. That is nearly every
queue: a message waiting in the queue is read by the code deployed next. A written AsyncAPI
document pays off when another team or another service reads the messages; for one producer and
one consumer in one repository, the model in the code is the contract.

Parse every message into a model at the edge, as [python.md](../language/python.md) section 4
says.

**Give a consumer's message model `extra="ignore"`, with a comment that names the producer as
the owner of the format.** Why: a `BACKWARD` change may remove a field [50], so the messages still
in the queue carry a field the new model lacks, and a model with `extra="forbid"` would reject
them all into the dead-letter queue. [python.md](../language/python.md) section 4 keeps `ignore`
for a format another party owns, and asks for that comment.

**Change a message's schema only in compatible steps, and deploy the two sides in the order its
mode asks.** Why: during a deploy, old and new code read the same messages. Confluent's Schema
Registry names the modes; without a registry, the same modes apply to the models in your code:

| Mode | What it means | Set it when | Leave it out when |
|---|---|---|---|
| `BACKWARD` | the default: a "consumer using schema `X` can process data produced with schema `X` or `X-1`"; "upgrade all consumers before you start producing new events." [50] | consumers deploy before producers | producers must deploy first |
| `FORWARD` | "data produced using schema `X` can be read by consumers with schema `X` or `X-1`"; "first upgrade all producers to using the new schema" [50] | producers deploy first | consumers deploy first |
| `FULL` | both: "backward and forward compatible between schemas `X` and `X-1`" [50] | the two sides deploy in no fixed order | one side always deploys first and `BACKWARD` or `FORWARD` fits |
| `NONE` | "compatibility checks are disabled." [50] | the research found no case | always |

AsyncAPI is "a project used to describe message-driven APIs in a machine-readable format", now at
3.1.0 [51]. The Linux Foundation hosts it and calls it "The open specification for defining
asynchronous APIs" [52]. Write one when another team reads your messages.

FastStream generates AsyncAPI documents from code [53]. Its README warns: "Prior
to FastStream's 1.0 release, each minor update is considered a major and can introduce breaking
changes" [53]. On 2026-10-29 it was at 0.7.8, though PyPI marks it Production/Stable
[54]. Pin its minor version if you use it.

## 9. Tracing and ids across a message

Applies when one piece of work crosses a queue and someone must follow it from end to end, in a
trace or in the logs. With no tracing backend, the message id on each log line is enough (the last
rule below).

OpenTelemetry's messaging conventions have the status "Development" (semantic conventions 1.44.0)
[55], so their names may still change. "A producer SHOULD attach a message creation
context to each message.", and the consumer's "Process" or "Receive" span "SHOULD link to the
message's creation context." [56] The conventions say they do not specify how the context
is attached [56].

**Let the instrumentation carry the trace context; do not write your own header.** Why: the
instrumentations read the headers they write, and no standard says what else a tool reads. The
OpenTelemetry instrumentations for Celery, aio-pika and confluent-kafka put the context into the
message headers when they send and take it out when they receive [57], [58], [59], [60], [61].
All three are Beta, at 0.66b2 [62], [63], [64]. They do not join the two sides the same way.
On their main branch, Celery starts the consumer's span with the producer's context as its
parent, and links to it instead only when `use_span_links` is set [57]. aio-pika makes the
extracted context the current one before it starts the span [59], [65], and a new span's parent
"Defaults to the global context" [66], so the span is a child there too. confluent-kafka adds a link to the
producer's context instead [61]. So expect one trace across a Celery or RabbitMQ
hop, and two linked traces across Kafka. Confluent's asyncio producer does not set headers per
message ([event-streaming.md](event-streaming.md) section 4).

When the consumer's job calls a model and opens its root span
([logging.md](../logging/logging.md) section 8), read logging.md section 12's bullet on an
OpenTelemetry instrumentation in the same process before you add these instrumentations: it says
what such a span does to that root, and where its exporter sends the prompts under it.

The default propagators are `tracecontext,baggage` [67], and the trace-context
propagator writes the `traceparent` and `tracestate` headers [68]. These are the
header names on the wire. No messaging standard for them exists: W3C Trace Context is written for
HTTP and says only that "messaging middleware MAY decide not to modify the traceparent headers"
[69], and the W3C draft for AMQP says "This document was abandoned." [70]

**Put the message id on every log line the consumer writes about a message.** Why: a worker has
no request id ([logging.md](../logging/logging.md) section 7), and the message id takes its place,
so one filter finds every line of one message. OpenTelemetry calls it `messaging.message.id`, "A
value used by the messaging system as an identifier for the message, represented as a string."
[56] Its `messaging.message.conversation_id` is the id it says is sometimes called the
correlation id [56].

```python
# One line for a finished unit of work, with the id that finds the message
# (logging.md section 4).
logger.info(
    "Payment for order %s recorded", paid.order_id, extra={"message_id": message_id}
)
```

Why this is good: the line carries ids and no payload, so it helps a reader find the message and
leaks nothing ([logging.md](../logging/logging.md) section 10).

## 10. Security and personal data in messages

This section covers four threats: someone who reads or changes messages on the network; a leaked
or shared credential that lets one service read or write every queue; someone with access to the
broker's storage, its management tools or a dead-letter queue who reads personal data; and
personal data copied to every consumer and every log. It leaves out the hardening of the broker
servers, because running them is out of scope, and the cache's own threats, which are in
[caching.md](caching.md). It applies to every project that sends messages; the research found no
case where a broker without encryption or authentication is fine in production.

1. **Encrypt the connection to the broker.** RabbitMQ: "We recommend using TLS connections when
   possible, at least to encrypt traffic." [71] SQS: allow only HTTPS, with the
   `aws:SecureTransport` condition in the queue policy [72]. Kafka encrypts with SSL and
   authenticates with SSL or SASL, but "security is optional - non-secured clusters are
   supported." [73] Turn it on. A task queue's broker on Redis or Valkey counts here too: its
   client settings are [task-queues.md](task-queues.md) section 12.
2. **Give each application its own credential, with only the rights it needs.** RabbitMQ: delete
   the default `guest` user, and "use a separate user per application" [71]; its
   permissions are three patterns per virtual host, one each for configure, write and read
   [74]. SQS: grant least privilege, with separate access for producers and consumers,
   and IAM roles instead of stored keys [72]. Kafka: ACLs per principal; with
   `allow.everyone.if.no.acl.found` set, "if a resource does not have any ACLs defined, Kafka will
   allow access to everyone." [75] Leave that setting off. The credentials come from the
   settings class ([python.md](../language/python.md) section 5).
3. **Know what encryption at rest leaves out.** SQS server-side encryption "encrypts the body of a
   message"; queue and message metadata stay unencrypted, and "Amazon SQS doesn't encrypt backlogged
   messages." [76] Keep personal data out of message attributes and headers.
4. **Keep personal data out of the payload, and send a reference.** The UK regulator's data
   minimisation rule: "identify the minimum amount of personal data you need to fulfil your
   purpose." [77] A message is copied to every consumer and to retry and dead-letter queues,
   and kept until its retention ends, so put the id of a record in the message, not the record.
   Microsoft's Claim Check pattern is for the case where payloads "contain sensitive information
   that shouldn't be visible to the messaging system or to intermediary components such as
   queue-monitoring tools." [78] Mathias Verraes, for event-sourced systems: "In the event,
   store a reference or URL that points to the payload’s location in the database." [79] The
   data can then be erased in one place.
5. **Never log a payload.** A message body is content in the sense of
   [logging.md](../logging/logging.md) section 10; log its id.

## 11. Common mistakes

Each of these is one a source names; the fix is in the section given.

| Mistake | What it costs | Fix |
|---|---|---|
| Sending the event after the commit, or in the middle of the transaction | an event lost in a crash, or sent for a change that rolled back [18], [19] | the outbox, section 4 |
| Trusting a tool's exactly-once setting | duplicates the tools' own docs warn about [7], [9] | section 2 |
| Acknowledging before the work commits, as Celery does by default [4] | a crash loses the message | section 3 |
| Leaving RabbitMQ's dead-lettering at its default `at-most-once` for messages that matter | a message lost between the queue and its dead-letter queue [37] | section 6 |
| Requeueing a failing message with `basic.nack` on RabbitMQ 4.3 and later | the message never reaches the delivery limit [37] | section 6 |
| A dead-letter queue on a FIFO queue whose order matters | broken order [35] | section 7 |
| Starting with the delayed-message exchange plugin | an unmaintained plugin; delayed messages lost when it is disabled [43] | section 5 |

## 12. Where the rules stop holding

- **The consumer's work is outside its database:** an email, a call to a payment service. The id
  row and the call cannot share a transaction, so a crash between the call and the commit repeats
  the call. Pass the message id to the other system as its idempotency key where it takes one.
  DBOS uses a workflow id that way: "An assigned workflow ID acts as an idempotency key"
  [6]. Work that spans several such calls is a job for
  [durable-workflows.md](durable-workflows.md).
- **The other system takes no idempotency key, and the work cannot be made idempotent.** Then
  the consumer chooses between two failures: an acknowledgement after the call turns a crash into
  a second call, and one before it, as Celery gives by default, turns a crash into a lost call
  [4]. Choose the failure that costs less, and write the choice in a comment at the consumer, so
  the next reader does not "fix" it. This is the one case where section 3's order may be the
  other way.
- **The database is not PostgreSQL.** The claim query and the relay here are written for
  PostgreSQL; other databases are not covered.
- **The relay cannot keep up.** One relay at a time is the simple way to keep order (section 4),
  and no measured point where it stops being enough was found.
- **The cost.** The id table is one more write per message and grows until it is cleaned. The
  polling relay holds a transaction open while it sends a batch.

## 13. Alternatives considered

- **A two-phase commit across the database and the broker.** Richardson: "2PC is not an option.
  The database and/or the message broker might not support 2PC." [18] Kafka's
  design page calls a two-phase commit the classic way, and prefers storing the offset with the
  output [2].
- **The broker's own deduplication or exactly-once setting.** Each stops at its tool's edge
  (section 2) [7], [9].
- **Log tailing for every outbox.** It fits where Kafka Connect already runs; elsewhere it adds
  servers, and it is database specific [23] (section 4).
- **A young outbox library as the default.** None is mature yet [24], [25],
  [26]; section 4 gives the questions to judge one.
- **The delayed-message exchange plugin.** No longer maintained [43].
- **A trace header of your own, or the W3C AMQP draft.** The draft was abandoned [70], and
  the instrumentations read only the headers they write (section 9).

## 14. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] AWS — Amazon SQS standard queues — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html
- [2] Apache Software Foundation — Apache Kafka documentation: Design, 4.3 — https://kafka.apache.org/43/design/design/
- [3] Dramatiq — Advanced Topics, 2.2.0 — https://dramatiq.io/advanced.html
- [4] Celery — User Guide: Tasks, 5.6.3 — https://docs.celeryq.dev/en/stable/userguide/tasks.html
- [5] Temporal — Activity Definition — https://docs.temporal.io/activity-definition
- [6] DBOS — Python tutorials: Workflows — https://docs.dbos.dev/python/tutorials/workflow-tutorial
- [7] Microsoft — Azure Architecture Center: Asynchronous messaging options — https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/messaging
- [8] AWS — Amazon SQS visibility timeout — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html
- [9] Google Cloud — Pub/Sub: Exactly-once delivery — https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery
- [10] Chris Richardson — Pattern: Idempotent Consumer (microservices.io, no date; opinion) — https://microservices.io/patterns/communication-style/idempotent-consumer.html
- [11] Bobby Woolf — Idempotent Receiver (Enterprise Integration Patterns, 2003; opinion) — https://www.enterpriseintegrationpatterns.com/patterns/messaging/IdempotentReceiver.html
- [12] Debezium — Outbox Event Router, 3.7 — https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html
- [13] Gunnar Morling — Reliable Microservices Data Exchange With the Outbox Pattern (Debezium blog, 2019; opinion, written by the Debezium project about its own tool) — https://debezium.io/blog/2019/02/19/reliable-microservices-data-exchange-with-the-outbox-pattern/
- [14] Dramatiq — User Guide, 2.2.0 — https://dramatiq.io/guide.html
- [16] Psycopg — Transactions management, documentation 3.3.7.dev1 — https://www.psycopg.org/psycopg3/docs/basic/transactions.html
- [18] Chris Richardson — Pattern: Transactional outbox (microservices.io, no date; opinion) — https://microservices.io/patterns/data/transactional-outbox.html
- [19] Brandur Leach — River: a Fast, Robust Job Queue for Go + Postgres (brandur.org, 2023; opinion, by a co-author of River) — https://brandur.org/river
- [20] PostgreSQL Global Development Group — SQL Commands: SELECT, PostgreSQL 18 — https://www.postgresql.org/docs/current/sql-select.html
- [21] AWS — AWS Prescriptive Guidance: Transactional outbox pattern — https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
- [22] Brandur Leach — Transactionally Staged Job Drains in Postgres (brandur.org, 2017; opinion) — https://brandur.org/job-drain
- [23] Chris Richardson — Pattern: Transaction log tailing (microservices.io, no date; opinion) — https://microservices.io/patterns/data/transaction-log-tailing.html
- [24] PyPI — faststream-outbox, 0.20.2 (package metadata and release history) — https://pypi.org/pypi/faststream-outbox/json
- [25] PyPI — pactix, 0.2.0 (package metadata and release history) — https://pypi.org/pypi/pactix/json
- [26] PyPI — pgrelay, 0.1.2 (package metadata and release history) — https://pypi.org/pypi/pgrelay/json
- [27] PyPI — procrastinate, 3.10.0 (package metadata) — https://pypi.org/pypi/procrastinate/json
- [28] Procrastinate — Using an external database connection — https://procrastinate.readthedocs.io/en/stable/howto/production/external_connection.html
- [29] Procrastinate — API Reference — https://procrastinate.readthedocs.io/en/stable/reference.html
- [30] Procrastinate — Use Procrastinate in a Django application — https://procrastinate.readthedocs.io/en/stable/howto/django/basic_usage.html
- [31] Dramatiq — API Reference, 2.2.0 — https://dramatiq.io/reference.html
- [32] Procrastinate — Define a retry strategy on a task — https://procrastinate.readthedocs.io/en/stable/howto/advanced/retry.html
- [33] Temporal — What is a Temporal Retry Policy? — https://docs.temporal.io/encyclopedia/retry-policies
- [34] DBOS — Python tutorials: Steps — https://docs.dbos.dev/python/tutorials/step-tutorial
- [35] AWS — Using dead-letter queues in Amazon SQS — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html
- [36] RabbitMQ — RabbitMQ 4.3 Highlights (RabbitMQ blog, 23 April 2026), 4.3 — https://www.rabbitmq.com/blog/2026/04/23/rabbitmq-4.3-release
- [37] RabbitMQ — Quorum Queues, documentation 4.4 — https://www.rabbitmq.com/docs/quorum-queues
- [38] AWS — Amazon SQS API Reference: ChangeMessageVisibility — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ChangeMessageVisibility.html
- [39] AWS — Amazon SQS delay queues — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-delay-queues.html
- [40] Pika — FAQ, in the documentation titled "Pika Python AMQP 0-9-1 Client Library" — https://pika.github.io/pika/latest/faq/
- [41] PyPI — aio-pika, 10.2.1 (package metadata, keyword "amqp 0.9.1") — https://pypi.org/pypi/aio-pika/json
- [42] RabbitMQ — RabbitMQ 4.4.0 release notes, v4.4.0 — https://github.com/rabbitmq/rabbitmq-server/releases/tag/v4.4.0
- [43] RabbitMQ — rabbitmq-delayed-message-exchange, README (archived repository) — https://github.com/rabbitmq/rabbitmq-delayed-message-exchange
- [44] Spring — Spring for Apache Kafka: Non-Blocking Retries, How the Pattern Works, 4.1.2 — https://docs.spring.io/spring-kafka/reference/retrytopic/how-the-pattern-works.html
- [45] Marc Brooker — Exponential Backoff And Jitter (AWS Architecture Blog, 2015; research, sponsored by Amazon Web Services) — https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- [46] RabbitMQ — Dead Letter Exchanges, documentation 4.4 — https://www.rabbitmq.com/docs/dlx
- [47] AWS — Creating alarms for dead-letter queues using Amazon CloudWatch — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/dead-letter-queues-alarms-cloudwatch.html
- [48] AWS — FIFO queue delivery logic in Amazon SQS — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-understanding-logic.html
- [49] RabbitMQ — Queues, documentation 4.4 — https://www.rabbitmq.com/docs/queues
- [50] Confluent — Schema Evolution and Compatibility for Schema Registry on Confluent Platform — https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
- [51] AsyncAPI Initiative — AsyncAPI Specification, 3.1.0 — https://www.asyncapi.com/docs/reference/specification/latest
- [52] Linux Foundation — Linux Foundation Will Host AsyncAPI to Support Growth and Collaboration for Industry’s Fastest-Growing API Spec (press release), 30 March 2021 — https://www.linuxfoundation.org/press/press-release/linux-foundation-will-host-asyncapi-to-support-growth-and-collaboration-for-industrys-fastest-growing-api-spec
- [53] FastStream — README — https://github.com/ag2ai/faststream
- [54] PyPI — faststream, 0.7.8 (package metadata) — https://pypi.org/pypi/faststream/json
- [55] OpenTelemetry — Semantic conventions for messaging systems, 1.44.0 — https://opentelemetry.io/docs/specs/semconv/messaging/
- [56] OpenTelemetry — Semantic conventions for messaging spans, 1.44.0 — https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/
- [57] OpenTelemetry — opentelemetry-instrumentation-celery, `celery/__init__.py`, main branch (0.67b0.dev) — https://raw.githubusercontent.com/open-telemetry/opentelemetry-python-contrib/main/instrumentation/opentelemetry-instrumentation-celery/src/opentelemetry/instrumentation/celery/__init__.py
- [58] OpenTelemetry — opentelemetry-instrumentation-aio-pika, `publish_decorator.py`, main branch (0.67b0.dev) — https://raw.githubusercontent.com/open-telemetry/opentelemetry-python-contrib/main/instrumentation/opentelemetry-instrumentation-aio-pika/src/opentelemetry/instrumentation/aio_pika/publish_decorator.py
- [59] OpenTelemetry — opentelemetry-instrumentation-aio-pika, `callback_decorator.py`, main branch (0.67b0.dev) — https://raw.githubusercontent.com/open-telemetry/opentelemetry-python-contrib/main/instrumentation/opentelemetry-instrumentation-aio-pika/src/opentelemetry/instrumentation/aio_pika/callback_decorator.py
- [60] OpenTelemetry — opentelemetry-instrumentation-confluent-kafka, `confluent_kafka/__init__.py`, main branch (0.67b0.dev) — https://raw.githubusercontent.com/open-telemetry/opentelemetry-python-contrib/main/instrumentation/opentelemetry-instrumentation-confluent-kafka/src/opentelemetry/instrumentation/confluent_kafka/__init__.py
- [61] OpenTelemetry — opentelemetry-instrumentation-confluent-kafka, `confluent_kafka/utils.py`, main branch (0.67b0.dev) — https://raw.githubusercontent.com/open-telemetry/opentelemetry-python-contrib/main/instrumentation/opentelemetry-instrumentation-confluent-kafka/src/opentelemetry/instrumentation/confluent_kafka/utils.py
- [62] PyPI — opentelemetry-instrumentation-celery, 0.66b2 (package metadata) — https://pypi.org/pypi/opentelemetry-instrumentation-celery/json
- [63] PyPI — opentelemetry-instrumentation-aio-pika, 0.66b2 (package metadata) — https://pypi.org/pypi/opentelemetry-instrumentation-aio-pika/json
- [64] PyPI — opentelemetry-instrumentation-confluent-kafka, 0.66b2 (package metadata) — https://pypi.org/pypi/opentelemetry-instrumentation-confluent-kafka/json
- [65] OpenTelemetry — opentelemetry-instrumentation-aio-pika, `span_builder.py`, main branch (0.67b0.dev) — https://raw.githubusercontent.com/open-telemetry/opentelemetry-python-contrib/main/instrumentation/opentelemetry-instrumentation-aio-pika/src/opentelemetry/instrumentation/aio_pika/span_builder.py
- [66] OpenTelemetry — opentelemetry-python, `opentelemetry/trace/__init__.py` (`Tracer.start_span`), v1.45.2 — https://raw.githubusercontent.com/open-telemetry/opentelemetry-python/v1.45.2/opentelemetry-api/src/opentelemetry/trace/__init__.py
- [67] OpenTelemetry — opentelemetry-python, `opentelemetry/propagate/__init__.py`, v1.45.2 — https://raw.githubusercontent.com/open-telemetry/opentelemetry-python/v1.45.2/opentelemetry-api/src/opentelemetry/propagate/__init__.py
- [68] OpenTelemetry — opentelemetry-python, `opentelemetry/trace/propagation/tracecontext.py`, v1.45.2 — https://raw.githubusercontent.com/open-telemetry/opentelemetry-python/v1.45.2/opentelemetry-api/src/opentelemetry/trace/propagation/tracecontext.py
- [69] W3C — Trace Context, W3C Recommendation 23 November 2021 — https://www.w3.org/TR/trace-context/
- [70] W3C Distributed Tracing Working Group — Trace Context: AMQP protocol, status of this document (`spec/02-sotd.md`, archived repository) — https://raw.githubusercontent.com/w3c/trace-context-amqp/main/spec/02-sotd.md
- [71] RabbitMQ — Production Deployment Guidelines, documentation 4.4 — https://www.rabbitmq.com/docs/production-checklist
- [72] AWS — Amazon SQS security best practices — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-security-best-practices.html
- [73] Apache Software Foundation — Apache Kafka documentation: Security Overview, 4.3 — https://kafka.apache.org/43/security/security-overview/
- [74] RabbitMQ — Authentication, Authorisation, Access Control, documentation 4.4 — https://www.rabbitmq.com/docs/access-control
- [75] Apache Software Foundation — Apache Kafka documentation: Authorization and ACLs, 4.3 — https://kafka.apache.org/43/security/authorization-and-acls/
- [76] AWS — Encryption at rest in Amazon SQS — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-server-side-encryption.html
- [77] Information Commissioner's Office — UK GDPR guidance: Principle (c), Data minimisation — https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/
- [78] Microsoft — Azure Architecture Center: Claim Check pattern — https://learn.microsoft.com/azure/architecture/patterns/claim-check
- [79] Mathias Verraes — Eventsourcing Patterns: Forgettable Payloads (verraes.net, 2019; opinion) — https://verraes.net/2019/05/eventsourcing-patterns-forgettable-payloads/
- [80] PostgreSQL Global Development Group — System Administration Functions: Advisory Lock Functions, PostgreSQL 18 — https://www.postgresql.org/docs/18/functions-admin.html — checked 2026-10-30
- [81] PostgreSQL Global Development Group — Explicit Locking: Advisory Locks, PostgreSQL 18 — https://www.postgresql.org/docs/18/explicit-locking.html — checked 2026-10-30
- [82] Debezium — Debezium connector for PostgreSQL: connector properties, 3.7 — https://debezium.io/documentation/reference/stable/connectors/postgresql.html — checked 2026-10-30
