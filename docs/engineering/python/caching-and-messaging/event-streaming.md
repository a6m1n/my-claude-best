# Event streaming: Kafka from Python

How a Python service produces events to Kafka and consumes them with confluent-kafka, so that a
crash loses no event and a repeated event does no harm.

**Navigation**

- [1. Purpose and scope](#1-purpose-and-scope)
- [2. When you need an event stream](#2-when-you-need-an-event-stream)
- [3. Which tool: Kafka with confluent-kafka](#3-which-tool-kafka-with-confluent-kafka)
- [4. The producer: durable settings and delivery reports](#4-the-producer-durable-settings-and-delivery-reports)
- [5. Keys and ordering](#5-keys-and-ordering)
- [6. The consumer: store the offset after the work](#6-the-consumer-store-the-offset-after-the-work)
- [7. Rebalances and the poll interval](#7-rebalances-and-the-poll-interval)
- [8. Consumer lag](#8-consumer-lag)
- [9. Schemas](#9-schemas)
- [10. The settings you set](#10-the-settings-you-set)
- [11. Common mistakes](#11-common-mistakes)
- [12. Where the rules stop holding](#12-where-the-rules-stop-holding)
- [13. Alternatives considered](#13-alternatives-considered)
- [14. Security and personal data](#14-security-and-personal-data)
- [15. Checks](#15-checks)
- [16. Sources](#16-sources)

## 1. Purpose and scope

An event stream keeps an event after it is read. Kafka's introduction says "Events in a topic can
be read as often as needed" and that "events are not deleted after consumption" [1]. Each
partition of a topic is read by "exactly one consumer within each subscribing consumer group at
any given time", and a consumer's position in it "is just a single integer" [2]. So several
services can read the same events, each at its own pace, and one of them can go back and read
them again.

This file is for a programmer who writes the Python code that produces to Kafka or consumes from
it, and for an agent that writes such code. Kafka promises "at-least-once delivery by default"
[2], and the client's own defaults can still lose an event or deliver it twice (sections 4
and 6). A project that follows this file has producers whose writes survive the loss of a broker,
consumers that store an offset only after the work is done, handlers that take a repeated event
without harm, and an alert that sees a partition nobody reads.

The one rule: decide in code what happens to an event when a process crashes. The producer sets
its durability, and the consumer stores an offset only after its work is done. The client's
defaults do neither.

Left out on purpose:

- Running the cluster: brokers, partition counts, upgrades, capacity.
- Stream processing (joins, windows, state over events), Kafka Streams and Kafka Connect. This
  file covers Python code that produces and consumes.
- The rules every messaging job shares. They live in [delivery.md](delivery.md): delivery
  guarantees and the limits of "exactly once" (section 2), idempotent consumers (section 3), the
  outbox (section 4), retries (section 5), dead letters (section 6), ordering (section 7), message
  contracts (section 8), tracing (section 9), security and personal data (section 10).

Not covered yet. The research searched for these and found no source to rest a rule on:

- a verifiable cost of running Kafka yourself;
- when Pulsar fits better than Kafka;
- an independent test of current Kafka: Jepsen's only analysis of Kafka itself is from 2013, of
  Kafka 0.8 beta [3];
- what the Python code sees when a consumer passes `max.poll.interval.ms`. librdkafka documents
  the rebalance that follows (section 7), not the error the application receives;
- how many teams use each streaming platform: the surveys do not ask, and downloads include CI
  runs.

## 2. When you need an event stream

Kafka fits when one of these holds:

- **Several consumers read the same events, and one may need to read them again**: a new service
  that starts from the history, a replay after a bug. Kafka keeps events for a retention period
  you set per topic, whoever has read them [1].
- **The events of one key must stay in order at high throughput.** Google's comparison of its two
  services names this case for Kafka: "You require message ordering at high throughput per key"
  [4].
- **The event log is the source of truth**: "You want to use the event sourcing pattern with an
  event log as a source of truth" [4].

It is too much when:

- **Each message is a piece of work for one worker, and nobody reads it again.** A queue does that
  job with less to run: [message-brokers.md](message-brokers.md) for a broker or a managed cloud
  queue, [task-queues.md](task-queues.md) for background work.
- **Nobody on the team wants to run brokers.** Even as a managed service Kafka asks more of a team:
  Google's comparison says its managed Kafka service "Requires more operational effort" than
  Pub/Sub [4]. Google sells both services, so this is the vendor's view of its own two
  products.

The simpler way: a managed queue when nobody needs to read an event again, and a managed Kafka
service when Kafka is needed and nobody wants to run it. The code in sections 4 to 9 is the same
on both.

Kafka 4.2 added queues to the broker: "Kafka Queues (Share Groups) is now production-ready"
[5]. From Python they are not ready yet (section 3).

## 3. Which tool: Kafka with confluent-kafka

| Tool (Python client) | Use it when | Too much, or the risk |
|---|---|---|
| Apache Kafka (confluent-kafka) | A sign from section 2 holds. Confluent documents confluent-kafka as its Python client, "a binding on top of the C client, librdkafka" [6]. The asyncio producer and consumer classes are in `confluent_kafka.aio` from 2.13.0 [6], the release whose changelog removed their experimental label [7]. | Section 2's "too much" list. From Python: the share consumer is a Preview, and no release supports Kafka's newer transaction protocol (both below). The defaults can lose an event or write it twice (sections 4 and 6). |

This file was checked against confluent-kafka 2.16.1, released on 28 October 2026 with
librdkafka 2.16.0 [8], and Kafka 4.4.0, released on 22 October 2026 [9]. The
4.4.0 release post lists no change a confluent-kafka producer or consumer has to act on: the new
client setting it names, `bootstrap.resolve.timeout.ms`, keeps the old behaviour by default
[10].

**Do not use the share consumer in production code.** When the work needs a queue, use one
([message-brokers.md](message-brokers.md)). Why: confluent-kafka's 2.15.0 changelog says "The
share consumer is currently in Preview and should not be used in production environments"
[7], and Confluent's docs say "Share consumers are a Preview feature" and that Preview
features are for "evaluation and non-production testing purposes" [6]. When you upgrade
confluent-kafka, read the changelog for the share consumer's status.

**Do not build an exactly-once effect on Kafka transactions from confluent-kafka.** Make the
consumer idempotent instead ([delivery.md](delivery.md) section 3). Why: Jepsen's analysis of
Bufstream, a Kafka-compatible system, found that "The Kafka transaction protocol is fundamentally
broken and must be revised" and reported that "Kafka's engineers believe KIP-890, which was
motivated by hanging transactions in Kafka, will likely fix the problem" [11]. Buf paid
for that analysis, and it tested Bufstream, not Kafka. On the Kafka ticket for the flaw, a comment
says "This issue should be resolved by KIP-890 and its related followups" [12]. The broker
side is done: Kafka 4.0's release post says "The second phase of KIP-890 has been completed"
[13]. The client side is not released. librdkafka's request for KIP-890 is open and labelled
`status:planned` [14], and a first commit for it is dated 24 September 2026 [15].
As of 29 October 2026 neither librdkafka's changelog, its unreleased section included
[16], nor confluent-kafka's [7] has a KIP-890 line.

**Kafka from Python: worth it, or only through a managed service?** Both limits above sit in the
client, so a managed service does not lift them, and neither stops the common case: a producer and
a consumer group with idempotent handlers work today. A third limit sits in the client too:
`AIOProducer` sets no headers per message [6], so in an asyncio service the producer sends each
event, with its id header, through the synchronous `produce()` (section 4). It changes how the
producer is called, not whether Kafka works from Python. So Kafka from Python is worth it, with
confluent-kafka, when a sign from section 2 holds. Who runs the brokers is a separate question,
and this practice leaves running servers out. The research found no verifiable cost of running
Kafka yourself; the one owner source on the effort is Google's comparison in section 2 [4].
So when the team does not run Kafka already, start with a managed Kafka service. Nothing in this
file changes when you move from one to the other.

Named once, not described:

- **Redpanda** says it is "compatible with the Kafka API" [17]. Its core is under the
  Business Source License, and its enterprise features under a separate licence [18]; the
  licence's grant says "you may not use the Licensed Work for a Streaming or Queuing Service"
  [19]. The only analysis of its benchmark claims found is a 2023 post by Jack Vanlightly, who
  works at Confluent, a Kafka vendor. He found that "Redpanda's claims regarding Kafka and even
  their own performance are greatly exaggerated" [20].
- **kafka-python** started a 3.0 line on 11 June 2026 [21]. Its networking runs on "a
  bespoke event-loop supporting async/await (but no asyncio yet)" [21], and one
  contributor has 1,472 commits against 120 for the next [22]. No asyncio, and one main
  committer.
- **aiokafka** is an "asyncio client for Kafka" [23]. Version 0.15.0 came out on
  28 October 2026 [24]. Its producer sends headers, added in 0.5.1, and can be idempotent, added
  in 0.5.0 [24]. Its changelog, up to 0.15.0, has no line on KIP-848, the consumer protocol
  section 7 asks every consumer to plan for [24], which confluent-kafka has had since 2.12.0 [7].
  Its README runs the tests against Kafka 2.8.1 by default [23]. The research found no other gap
  that matters here, so the pick rests on one client for sync and async code, the one Confluent
  documents as its Python client [6].

## 4. The producer: durable settings and delivery reports

The producer decides three things: whether the cluster can lose a write it accepted, whether a
retry writes a second copy, and whether your code ever hears that a send failed.

**Ask for each topic with three replicas and `min.insync.replicas` 2, and produce with
`acks=all`.** Do it when you create a topic, or when you ask the team that runs the cluster for
one. Kafka's broker docs call this "A typical scenario": a replication factor of 3,
`min.insync.replicas` 2, and `acks` of all [25]. It "ensures that a majority of replicas
must persist a write before it's considered successful by the producer" [25]. The
broker's default `min.insync.replicas` is 1 [25], so a topic created with the defaults
accepts an `acks=all` write that only one broker holds. librdkafka's `acks` default is
already `all` (`-1`) [26]; write it out anyway, so a reader sees it and nobody lowers it.

**Set `enable.idempotence=True` in every producer.** librdkafka leaves it off by default
[26], while Kafka's Java producer turns it on when no other setting conflicts
[27], so habits carried over from Java get it wrong. Without it, a retry "may write
duplicates of the retried message in the stream" [27]. With it, librdkafka "will ensure
that messages are successfully produced exactly once and in the original produce order", and it
sets `acks=all` and retries up to `INT32_MAX` for you [26]. "Exactly once" here means one
copy of each send in the topic. It does not make a consumer's effect happen once
([delivery.md](delivery.md) section 2).

**Serve delivery reports with `poll()`, and call `flush()` before the process exits.**
`produce()` "enqueues message immediately for batching, compression and transmission to broker",
but "no delivery notification events are propagated until `poll()` is invoked" [6]. The
callback you pass as `on_delivery` "will be called from poll() when the message has been
successfully delivered or permanently fails delivery" [28]. So call `poll(0)` after each
`produce()`, and log or act on a failed report in the callback: a failed send that nobody reads
is an event lost in silence. At shutdown, "Typically, flush() should be called prior to shutting
down the producer to ensure all outstanding/queued/in-flight messages are delivered" [6].
It returns the "Number of messages still in queue" [28]; above zero, those events are lost
when the process exits.

**When the next step needs the broker's answer, take it from the delivery report.** An outbox
relay deletes its row only after the broker has accepted the event ([delivery.md](delivery.md)
section 4). It does that in the delivery callback or after `flush()`, never right after
`produce()`.

The client every publish goes through, in `src/acme/core/kafka_client.py`
([file-structure.md](../../any-language/file-structure/file-structure.md) section 4). The adapter's
`main.py` builds one producer at startup from the values in `Settings` and calls `close()` on
shutdown; that wiring is left out. `UndeliveredEventsError`, in `src/acme/core/errors.py` and
also left out, holds only the number of events not sent.

```python
"""The one way into Kafka for code that publishes events."""

import logging
from uuid import UUID

from confluent_kafka import KafkaError, Message, Producer
from pydantic import BaseModel, SecretStr

from acme.core.errors import UndeliveredEventsError

logger = logging.getLogger(__name__)


def build_producer(
    bootstrap_servers: str, username: str, password: SecretStr
) -> Producer:
    return Producer(
        {
            "bootstrap.servers": bootstrap_servers,
            # Kafka runs without security unless asked (event-streaming.md section 14).
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "SCRAM-SHA-512",  # the mechanism your cluster accepts
            "sasl.username": username,
            "sasl.password": password.get_secret_value(),
            # librdkafka leaves it off; without it a retry can write a second copy
            # (event-streaming.md section 4).
            "enable.idempotence": True,
            # Already the default; written out so nobody lowers it
            # (event-streaming.md section 4).
            "acks": "all",
            # The default, 5 minutes, written: after it the delivery report says the
            # send failed (event-streaming.md section 10).
            "message.timeout.ms": 300_000,
            # The default, written: the timeout above, not this count, ends the
            # retries (event-streaming.md section 10).
            "retries": 2_147_483_647,
        }
    )


class EventPublisher:
    """Publishes one kind of event to its topic."""

    def __init__(self, producer: Producer, topic: str) -> None:
        self._producer = producer
        self._topic = topic

    def publish(self, key: str, message_id: UUID, event: BaseModel) -> None:
        self._producer.produce(
            self._topic,
            # The key picks the partition (delivery.md section 7).
            key=key.encode(),
            value=event.model_dump_json().encode(),
            # Consumers drop a second copy by this id (delivery.md section 3).
            headers=[("id", str(message_id).encode())],
            on_delivery=_log_failed_delivery,
        )
        # Runs the delivery callbacks (event-streaming.md section 4).
        self._producer.poll(0)

    def close(self, timeout_s: float) -> None:
        undelivered = self._producer.flush(timeout_s)
        if undelivered:
            # Raised, not logged: main.py, the caller that decides, logs it once
            # (logging.md section 5).
            raise UndeliveredEventsError(undelivered)


def _log_failed_delivery(err: KafkaError | None, msg: Message) -> None:
    if err is None:
        return
    # Departs from logging.md section 5, which leaves the final ERROR to the caller:
    # librdkafka reports the final outcome in this callback, run from poll() or
    # flush(), with no caller to raise to. The cost: the caller does not learn the
    # outcome. The topic and the error only: no payload (logging.md section 10).
    logger.error("Kafka delivery to topic %s failed: %s", msg.topic(), err)
```

It is good because the durability settings sit in the one place every send goes through, so no
second producer can leave them out. The password stays a `SecretStr` until the one line that needs
the text ([python.md](../language/python.md) section 5). The event that leaves is a Pydantic model
([python.md](../language/python.md) section 4). Each event carries its id in a header, so a
consumer drops a copy without parsing the body ([delivery.md](delivery.md) section 3), and an
asyncio service calls `publish` through `run_in_executor()` (the rule below). A failed send is
logged once, without its payload ([logging.md](../logging/logging.md) section 10). That one line
departs from [logging.md](../logging/logging.md) section 5, which leaves the final `ERROR` to the
caller, and says so at the line: librdkafka reports the final outcome in a callback run from
`poll()` or `flush()`, with no caller to raise to, so the caller does not learn the outcome. A
relay that must learn it, such as the outbox relay above, passes its own `on_delivery` to
`produce()`. `close()` logs nothing: it raises `UndeliveredEventsError` with the number of events
it could not send, and `main.py`, the caller that decides, logs it once, as that section asks.

**In an asyncio service, send each event with the synchronous `produce()`, called through
`run_in_executor()`, not with `AIOProducer`.** Why: every event carries its id in a header
([delivery.md](delivery.md) section 3), and Confluent's docs send you to the synchronous client
when "You require per-message headers in produce operations (not supported in asynchronous
batched path)": "If you require headers, invoke the synchronous produce() using
run_in_executor() for that path" [6]. The same page advises the asyncio clients when "Your
application runs under an event loop" and "You must avoid blocking the event loop during Kafka
operations" [6], which is why the call goes through `run_in_executor()`. A trace context in a
header takes the same path ([delivery.md](delivery.md) section 9).

## 5. Keys and ordering

Kafka keeps order inside a partition, not across a topic: "Our topic is divided into a set of
totally ordered partitions" [2]. Which key keeps an entity's events in order is
[delivery.md](delivery.md) section 7. Kafka adds two things:

- In a group, each partition has one consumer at a time [2], so one key's events reach one
  handler in the order they were written.
- Idempotence keeps one producer's retries "in the original produce order" [26].

A retry, a retry topic or a dead-letter topic on the consumer's side can still break the order;
the shared rule is [delivery.md](delivery.md) section 7.

## 6. The consumer: store the offset after the work

librdkafka's defaults set `enable.auto.commit` and `enable.auto.offset.store` to true [26].
The client then stores the offset "of last message provided to application", and commits the
stored offsets every 5000 ms [26]. Confluent's docs call this the default "which provides no
delivery guarantee" and warn: "You can lose data or get duplicates" [6]. When the process
dies after an automatic commit and before the work is done, the next consumer starts after that
event, "effectively missing the message" [6].

**Set `enable.auto.offset.store=False`, and call `store_offsets()` after the handler has
finished.** Keep `enable.auto.commit` on: it commits what you stored. This is Confluent's recipe
for at least once [6], and librdkafka recommends `enable.auto.offset.store=false` "for
long-time processing applications" [26]. In Confluent's words: "For this guarantee option,
you should store the offset only after processing the message successfully" [6]. A crash
before the store line re-reads the event, so the handler sees it twice: "Messages might be
redelivered after a failure, so design processing to tolerate duplicates" [6]. The
handler follows [delivery.md](delivery.md) section 3.

**Never store the offset of a later event while an earlier one in the same partition has
failed.** The offset store holds "the next offset to (auto-)commit for each partition" [26],
so storing a later event's offset commits the failed one with it.

**When the handler fails, retry the event in place, then move it to a dead-letter topic, and store
its offset only after that.** Kafka's design docs describe no delayed redelivery for a consumer
group [2], and a dead-letter topic is one more topic your code writes to. So the consumer
does both:

1. Retry the event inside the loop. The partition's next event waits meanwhile, so the order
   holds, for every key on that partition and not only the failed one. No owner source gives the
   number of attempts or the wait between them, so both are your choice; pick them from two
   limits: all the attempts together, waits included, stay well under `max.poll.interval.ms`
   (section 7), and every other event on the partition waits until they end. Write both in the
   code ([delivery.md](delivery.md) section 5).
2. When the last attempt fails, produce the event with its key to a dead-letter topic, wait for its
   delivery report (section 4), and then store the offset of the original. The alarm and the
   replay are [delivery.md](delivery.md) section 6; what a moved event does to its key's order is
   section 7.

Ending the process instead stops on the event without skipping it, but the restart reads the same
event and fails again, so it only buys time.

**Close the consumer on shutdown.** `close()` "Commits offsets, unless the consumer property
'enable.auto.commit' is set to False. Leaves the consumer group" [28]. Without it, the
offsets stored since the last automatic commit are lost, and the group waits for the session
timeout before it moves the partitions (section 7).

The consumer is built beside the producer in `src/acme/core/kafka_client.py`:

```python
def build_consumer(
    bootstrap_servers: str, group_id: str, username: str, password: SecretStr
) -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "SCRAM-SHA-512",  # the mechanism your cluster accepts
            "sasl.username": username,
            "sasl.password": password.get_secret_value(),
            # Set, so a library upgrade cannot change what the rebalance callbacks
            # receive (event-streaming.md section 7).
            "group.protocol": "classic",
            # The default stores an offset before the work, and a crash then skips
            # the event (event-streaming.md section 6).
            "enable.auto.offset.store": False,
            # Commits what the loop stored, every 5 s and on close.
            "enable.auto.commit": True,
            # The default, 5 s, written: after a crash the next owner re-reads at most
            # 5 s of stored events (event-streaming.md section 7).
            "auto.commit.interval.ms": 5_000,
            # The default, 45 s, written: how long a dead consumer keeps its partitions.
            # Classic protocol only: drop it with group.protocol=consumer
            # (event-streaming.md section 7).
            "session.timeout.ms": 45_000,
            # earliest, not the default largest: a skipped order costs more than one
            # read twice (event-streaming.md section 10).
            "auto.offset.reset": "earliest",
            # The default, 5 minutes, written: well above one order's work
            # (event-streaming.md section 7).
            "max.poll.interval.ms": 300_000,
        }
    )
```

The loop is the queue consumer's adapter, `src/acme/consumer/handlers_orders.py`
([file-structure.md](../../any-language/file-structure/file-structure.md) section 5). It takes the
consumer, the topic and the use case as parameters:

```python
import logging
import threading
from collections.abc import Callable
from uuid import UUID

from confluent_kafka import (
    Consumer,
    KafkaError,
    KafkaException,
    Message,
    TopicPartition,
)
from pydantic import ValidationError

from acme.consumer.schemas import OrderPlaced

logger = logging.getLogger(__name__)


class InvalidOrderEvent(Exception):
    """An event that does not parse. It names the event's place, never its values."""

    def __init__(
        self, topic: str | None, partition: int | None, offset: int | None
    ) -> None:
        super().__init__(
            f"Order event at {topic} [{partition}] offset {offset} does not parse"
        )


def consume_orders(
    consumer: Consumer,
    topic: str,
    record_order: Callable[[UUID, OrderPlaced], None],
    stop: threading.Event,
) -> None:
    consumer.subscribe([topic], on_revoke=_commit_stored, on_lost=_log_lost)
    try:
        while not stop.is_set():
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            payload = msg.value()
            if payload is None:
                raise ValueError("An order event arrived with no value")
            # Outside data becomes a model once, here (python.md section 4).
            try:
                event = OrderPlaced.model_validate_json(payload)
            except ValidationError:
                # The error's text holds the event's values: raise one that names only
                # where the event is (logging.md section 10).
                raise InvalidOrderEvent(
                    msg.topic(), msg.partition(), msg.offset()
                ) from None
            # The producer's id: record_order drops a second copy by it
            # (delivery.md section 3).
            record_order(_event_id(msg), event)
            # After the work, never before: a crash before this line re-reads the
            # event, and record_order skips it by its id (delivery.md section 3).
            consumer.store_offsets(message=msg)
    finally:
        # Commits what was stored and leaves the group (event-streaming.md section 6).
        consumer.close()


def _event_id(msg: Message) -> UUID:
    # The id header the producer sets (event-streaming.md section 4).
    for name, value in msg.headers() or []:
        if name == "id" and value is not None:
            return UUID(value.decode())
    raise ValueError("An order event arrived with no id header")


def _commit_stored(consumer: Consumer, partitions: list[TopicPartition]) -> None:
    # The last moment to commit before these partitions move to another member
    # (event-streaming.md section 7).
    try:
        consumer.commit(asynchronous=False)
    except KafkaException as exc:
        # No offset stored since the last commit leaves nothing to commit.
        if exc.args[0].code() != KafkaError._NO_OFFSET:
            raise


def _log_lost(consumer: Consumer, partitions: list[TopicPartition]) -> None:
    # No commit here: another member may own these partitions already
    # (event-streaming.md section 7).
    logger.warning("Kafka partitions lost: %s", partitions)
```

It is good because the offset is stored only after `record_order` returns, so a crash re-reads
the event instead of skipping it. A failure raises before the store line, so no later offset
passes a failed event, and `close()` still commits what was stored before it. The event is parsed
into a model once, at the edge ([python.md](../language/python.md) section 4). A value that does
not parse raises `InvalidOrderEvent`, which names the topic, the partition and the offset,
`from None`, so the error that leaves the loop carries none of the event's values
([python.md](../language/python.md) section 4, [logging.md](../logging/logging.md) section 10).
The producer's `id` header reaches `record_order`, which drops a second copy by it
([delivery.md](delivery.md) section 3). The consumer, the
topic and the use case come in as parameters, so a unit test can call the loop with a fake
([readability.md](../../any-language/readability/readability.md) section 6,
[fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 3). Left out: the retry
and the dead-letter step above; this loop raises instead, which stops on the event without
skipping it. The API reference lists `_NO_OFFSET`, "No offset stored", among the error codes
[28]; the docs do not say when a commit returns it, so the callback treats it as nothing to
do and raises every other error.

## 7. Rebalances and the poll interval

A rebalance moves partitions between the members of a group: when a member joins, leaves, or
stops calling `poll()`. The new owner starts from the last committed offset, so it reads again
every event that was not committed.

**Keep the work for one event well under `max.poll.interval.ms`, 300000 ms (5 minutes) by
default** [26]. It is the "Maximum allowed time between calls to consume messages", and "If
this interval is exceeded the consumer is considered failed and the group will rebalance in order
to reassign the partitions to another consumer group member" [26]. The same row warns:
"Offset commits may be not possible at this point" [26]. The slow handler's events are then
processed again by another member. When one event can take longer, raise the setting (section
10), or let the consumer only put the work on a task queue ([task-queues.md](task-queues.md)) and
store the offset once the task is queued. The KIP-848 protocol keeps this check: librdkafka lists
"Enforced max poll interval" among its features [29].

On the classic protocol a crashed consumer's partitions move after the session timeout. The
consumer sends heartbeats, and when none arrives within `session.timeout.ms`, 45000 ms by default,
"the broker will remove the consumer from the group and trigger a rebalance" [26]. That is
the delay to expect before another member reads a dead consumer's events again; it is a separate
check from the poll interval [26]. Under KIP-848 the client setting does not apply:
"`session.timeout.ms` is not supported for `group.protocol=consumer`" [26], and "Session
timeout is broker-controlled" [30].

**Commit the stored offsets in `on_revoke`.** The API reference describes `on_revoke` as the
"callback to provide handling of offset commits to a customized store on the start of a rebalance
operation" [28], and Confluent's asyncio example commits there [6]. Without it, the
next owner re-reads the events stored since the last automatic commit, up to 5 seconds of them.

**Set `on_lost`, and do not count on a commit in it.** "If not specified, lost partition events
will be delivered to on_revoke, if specified" [28]. A lost partition is not a revoked one:
"Partitions that have been lost may already be owned by other members in the group and therefore
committing offsets, for example, may fail" [28]. So `on_lost` logs and lets go. The new owner
reads those events again, and the idempotent handler takes them ([delivery.md](delivery.md)
section 3). The example sets no `on_assign`: when that callback does not assign the partitions
itself, the client "assigns these partitions automatically after it returns" [6].

**Set `group.protocol` in every consumer.** The default is `classic`, and librdkafka says it
"will change to `consumer` in next releases" [26]. The two protocols hand the callbacks
different lists (below), so an upgrade that changes the default would change what your code
receives without a line in your diff.

**When you set `group.protocol=consumer` (KIP-848).** Kafka 4.0 turned the new protocol on by
default on the broker side, and "Consumers must opt-in by setting group.protocol=consumer"
[13]. confluent-kafka made it production-ready in 2.12.0, and it is "not enabled by default"
[7]. The migration guide asks for brokers 4.0.0 or later and confluent-kafka 2.12.0 or
later [30]. Under it:

- "The protocol is fully incremental in KIP-848" [30]: `on_assign` and `on_revoke`
  receive only the partitions that changed, not the full list [30]. Code that keeps
  state per partition must update it from the changes.
- "Do not use consumer.assign() or consumer.unassign() when using group.protocol='consumer'
  (KIP-848)" [30].
- `partition.assignment.strategy` is not supported, and the session timeout is set on the broker
  (above) [26].

Kafka's 4.0 post says the protocol "increases the stability and the performance of consumer groups
while simplifying clients" [13]. That is the project's own claim, and the research found no
independent measure of it, so this file does not tell you to switch, only to set the value
yourself.

## 8. Consumer lag

Lag is how far a group is behind the newest events. The consumer publishes `records-lag-max`,
"The maximum lag in terms of number of records for any partition in this window", and the metric
is "Published by the consumer, not broker" [31]. Kafka's monitoring docs list it with
the other consumer metrics and do not single it out as the signal to watch [31]. A metric
that the consumer publishes says nothing about a partition that no consumer holds.

At Socure, a Confluent Kafka consumer group that fed a webhook pipeline did not rebalance
correctly after an infrastructure scale-up, and "a subset of Kafka partitions was effectively
unassigned for consumption" [32]. For about 16 hours, from 2:06 PM ET on 25 June 2026 to
6:03 AM ET the next day, about half of the webhook events were delayed, and none was lost.
"Topic-aggregate lag remained within thresholds during the impact window" [32]. Socure's fix
was an alert on the gap between the rate events are produced and the rate they are polled, to
catch "partition-level consumption gaps that aggregate lag alone does not surface" [32].

**Alert on lag per partition, and on a partition that nobody consumes, not on the topic's total
alone.** A total can stay low while one partition stands still, as it did at Socure [32].
Comparing the rate events reach each partition with the rate the group reads them is the way
Socure chose to see the second [32].

## 9. Schemas

How to pick a compatibility mode, what a contract holds, and why a consumer's model keeps
`extra="ignore"` are shared: [delivery.md](delivery.md) section 8. A replay also reads events
written under older schemas, so it meets fields the model does not declare: one more reason for
that section's `extra="ignore"`. With confluent-kafka's `DeserializingConsumer`, `value()` returns
the deserialized object instead of bytes [28]; parse it into the same model with
`model_validate`.

The model the loop in section 6 parses, in `src/acme/consumer/schemas.py`:

```python
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class OrderPlaced(BaseModel):
    # The orders team owns this event, and an event one schema version away can
    # carry a field this model lacks (event-streaming.md section 9).
    model_config = ConfigDict(extra="ignore", frozen=True)

    order_id: str
    total_cents: Annotated[int, Field(ge=0, strict=True)]
```

It is good because every rule the event must follow is on the type: a negative total or a total
sent as a string fails at the edge, in one `ValidationError`. The one setting a reader might flip
back to `forbid` carries its reason at the line.

## 10. The settings you set

Every client sets `bootstrap.servers`, the "Initial list of brokers" [26], and every consumer
of a group sets the same `group.id`: "All clients sharing the same group.id belong to the same
group" [26]. The client requires none of the settings below; the "Set it when" column says
when this file does. Meanings and defaults are librdkafka 2.16.0's [26].

| Field | What it means | Set it when | Leave it out when |
|---|---|---|---|
| `acks` (producer) | How many in-sync replicas must hold a write before the broker answers. Default `-1`, the same as `all`. With fewer in sync than the topic's `min.insync.replicas`, the write fails [26]. With `0` the "Broker does not send any response/ack to client" [26], so never lower it for an event that must not be lost. | Always, the default's value included ([delivery.md](delivery.md) section 5): `all` (section 4). | Never. |
| `enable.idempotence` (producer) | One copy of each send, in the order sent; turns on `acks=all` and the retries for you. Default `false` [26]. | Always, as `True` (section 4). | No case found. |
| `message.timeout.ms` (producer) | The longest a produced message waits for delivery, retries included; after it the delivery report carries an error. Default 300000 ms; 0 is infinite [26]. | Always, the default's value included ([delivery.md](delivery.md) section 5), as in section 4. | Never. |
| `retries` (producer) | How many times librdkafka retries a failing send; an alias of `message.send.max.retries`. Default 2147483647; with idempotence it must stay above 0 [26]. | Always, the default's value included ([delivery.md](delivery.md) section 5), as in section 4. | Never. |
| `enable.auto.commit` (consumer) | Commits the stored offsets in the background, every `auto.commit.interval.ms` (5000 ms by default). Default `true` [26]. | Always, the default's value included ([delivery.md](delivery.md) section 5): `True`, with `enable.auto.offset.store=False` (section 6); `False` when the code commits each event itself with `commit()` (section 13). | Never. |
| `auto.commit.interval.ms` (consumer) | How often, in milliseconds, the stored offsets are committed. Default 5000 [26]. | Always while `enable.auto.commit` is `True`, the default's value included ([delivery.md](delivery.md) section 5), as in section 6. | `enable.auto.commit` is `False` (section 13). |
| `session.timeout.ms` (consumer) | On the classic protocol, how long the broker waits for a heartbeat before it removes the consumer and rebalances. Default 45000 ms [26]. | Always on the classic protocol, the default's value included ([delivery.md](delivery.md) section 5), as in section 6. | `group.protocol=consumer`, which does not support it [26]. |
| `enable.auto.offset.store` (consumer) | Stores the offset of each message as it reaches your code. Default `true` [26]. | Always, the default's value included ([delivery.md](delivery.md) section 5): `False`, with `store_offsets()` after the work (section 6); `True` only in the at-most-once case of section 12. | Never. |
| `max.poll.interval.ms` (consumer) | The longest gap between two calls that consume before the group drops the consumer. Default 300000 ms [26]. A higher value also lets a stuck consumer keep its partitions for that long. | Always, the default's value included ([delivery.md](delivery.md) section 5): well above one event's work, its retries included (sections 6 and 7). | Never. |
| `group.protocol` (consumer) | `classic`, or `consumer` for KIP-848. Default `classic`, to change in a later release [26]. | Always, the default's value included ([delivery.md](delivery.md) section 5), so an upgrade does not change it for you; `consumer` once the brokers are 4.0 or later and the callbacks follow section 7. | Never. |
| `auto.offset.reset` (consumer) | Where a group starts when it has no committed offset, or its offset is out of range. Default `largest`, the newest events [26]. | Always, the default's value included ([delivery.md](delivery.md) section 5): `earliest` when a new group must read the events already in the topic, or when an event skipped after an outage costs more than one read twice; otherwise `latest`. | Never. |

## 11. Common mistakes

| Mistake | Why people make it | What it costs | The fix |
|---|---|---|---|
| A consumer left on the default offset settings | The defaults need no line of setup. | "You can lose data or get duplicates" [6]. | Section 6. |
| A producer without `enable.idempotence=True` | Kafka's Java producer turns it on by default [27]; librdkafka leaves it off [26]. | A retry "may write duplicates of the retried message in the stream" [27]. | Section 4. |
| `produce()` with no `poll()` and no `flush()` | `produce()` returns at once, because it only queues the message [6]. | No delivery report arrives, so a failed send goes unseen, and events still queued at exit are not delivered [6]. | Section 4. |
| An alert on the topic's total lag only | Lag is the metric the consumer publishes [31]. | At Socure, partitions went unread for about 16 hours while the total stayed within thresholds [32]. | Section 8. |

## 12. Where the rules stop holding

1. **At most once.** Confluent documents the opposite recipe for at-most-once delivery:
   "Committing synchronously before processing the message, instead of after", so that "a crash
   can skip a message rather than reprocess it" [6]. Use it only where a skipped event
   costs less than one handled twice and the handler cannot be made idempotent. The sources read
   name no such case.
2. **A cluster with one broker**, for local runs and tests, cannot meet `min.insync.replicas` 2:
   "If there are less than `min.insync.replicas` (broker configuration) in the ISR set the produce
   request will fail" [26]. Create its topics with one replica and `min.insync.replicas` 1,
   and keep `acks=all` and idempotence, so the client code is the same as in production. The
   integration tests run against such a broker through testcontainers
   ([libraries.md](../testing/libraries.md) section 2).
3. **Work longer than the poll interval.** A higher `max.poll.interval.ms` (section 7) also lets a
   consumer that hangs keep its partitions for that long before the group moves them [26].
   When the work runs for many minutes, let the consumer only put it on a task queue
   ([task-queues.md](task-queues.md)), and keep the interval at its default.
4. **The three client limits end with a release.** When you upgrade confluent-kafka, read its
   changelog for the share consumer's Preview note, for KIP-890 and for per-message headers in
   `AIOProducer` [7]. When one of them changes, sections 3, 4 and 13 no longer hold as written.

## 13. Alternatives considered

- **Kafka transactions for an exactly-once effect.** Not taken while no confluent-kafka release
  has KIP-890 (section 3). An idempotent consumer ([delivery.md](delivery.md) section 3) gives the
  effect at the handler, with any broker.
- **Share groups (Kafka's queues) for work done once per event.** Not taken while the Python share
  consumer is a Preview (section 3). A queue does that job
  ([message-brokers.md](message-brokers.md)).
- **A synchronous commit after each event.** Confluent calls it "The simplest and most reliable way
  to manually commit offsets" [6]. This file keeps the stored-offset recipe as the default,
  because a synchronous commit "will block until the commit succeeds or fails" [28], on every
  event, while stored offsets are committed in the background every 5 seconds [26]. Take the
  synchronous commit when a crash may re-read only the event in flight, never the last seconds'
  worth. Then set `enable.auto.commit` to `false`: the API reference says to "Use this method to
  commit offsets if you have 'enable.auto.commit' set to False" [28].
- **Redpanda, kafka-python and aiokafka**, each named once in section 3 with its reason.
- **Pulsar** is not compared: the research found no source that settles when it fits better
  (section 1).

## 14. Security and personal data

This section covers a client that connects in plain text or without a login, a client that can
read or write topics it does not need, and personal data kept in a topic after it was read. It
leaves out the hardening of brokers and networks, which belongs to running the cluster. The part
every messaging job shares is [delivery.md](delivery.md) section 10.

**Set `security.protocol` to `SASL_SSL`, or to `SSL` with client certificates, in every client.**
Why: librdkafka's default protocol is `plaintext` [26]. librdkafka supports the SASL mechanisms
GSSAPI, PLAIN, SCRAM-SHA-256, SCRAM-SHA-512 and OAUTHBEARER [26]. Why every broker connection is
encrypted and authenticated, and where the credentials come from, are
[delivery.md](delivery.md) section 10; the example in section 4 follows it.

**Ask for ACLs that give each service its own topics and its own group, and nothing else.** The
reason, and the cluster setting to leave off, are [delivery.md](delivery.md) section 10.

**Keep personal data out of events where you can.** Kafka keeps an event until the topic's
retention ends, whoever has read it [1], so a person's data in an event outlives the work
that needed it. What to do instead is [delivery.md](delivery.md) section 10. No payload goes into
a log line ([logging.md](../logging/logging.md) section 10): the examples log the topic and the
error only, and the consumer loop turns a `ValidationError` into an error that names the event's
topic, partition and offset and none of its values (section 6).

## 15. Checks

- `grep -rn "enable.idempotence" src/` prints `True` in every producer's configuration.
- `grep -rn "enable.auto.offset.store" src/` prints `False` in every consumer's configuration, and
  `grep -rn "group.protocol" src/` prints a line in each one.
- At review, in each consumer loop: does `store_offsets()` come after the handler returns
  (section 6)?
- At review, in each consumer loop: can any path reach `store_offsets()` after a failed event
  (section 6)?
- `grep -rnE "ShareConsumer|transactional\.id" src/` prints nothing while section 3's limits hold.
- At review of the monitoring: is there an alert per partition, and one for a partition that no
  consumer reads (section 8)?
- Unit tests replace the publisher with a fake that records
  ([fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 3); integration tests
  run the consumer loop against a real broker ([libraries.md](../testing/libraries.md) section 2).

## 16. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Apache Kafka — Introduction — https://kafka.apache.org/intro
- [2] Apache Kafka — Design, 4.3 — https://kafka.apache.org/43/design/design/
- [3] Jepsen — Analyses — https://jepsen.io/analyses
- [4] Google Cloud — Choose Pub/Sub or Cloud Managed Service for Apache Kafka (Google sells both services) — https://docs.cloud.google.com/pubsub/docs/choose-pubsub-kafka
- [5] Apache Kafka — Apache Kafka 4.2.0 Release Announcement, 4.2.0 — https://kafka.apache.org/blog/2026/02/17/apache-kafka-4.2.0-release-announcement/
- [6] Confluent — Python Client for Apache Kafka (confluent-kafka-python overview) — https://docs.confluent.io/kafka-clients/python/current/overview.html
- [7] Confluent — confluent-kafka-python CHANGELOG, v2.16.1 — https://github.com/confluentinc/confluent-kafka-python/blob/v2.16.1/CHANGELOG.md
- [8] Confluent — confluent-kafka-python releases (v2.16.1, v2.16.0, v2.15.1) — https://github.com/confluentinc/confluent-kafka-python/releases
- [9] Apache Kafka — Downloads — https://kafka.apache.org/community/downloads/ — checked 2026-10-30
- [10] Apache Kafka — Apache Kafka 4.4.0 Release Announcement, 4.4.0 — https://kafka.apache.org/blog/2026/10/22/apache-kafka-4.4.0-release-announcement/ — checked 2026-10-30
- [11] Kyle Kingsbury — Bufstream 0.1.0 (Jepsen, 2024; research, sponsored by Buf Technologies) — https://jepsen.io/analyses/bufstream-0.1.0
- [12] Kyle Kingsbury — KAFKA-17754: A delayed EndTxn message can cause aborted read, lost writes, atomicity violation (Apache Kafka Jira, 2024; opinion) — https://issues.apache.org/jira/browse/KAFKA-17754
- [13] Apache Kafka — Apache Kafka 4.0.0 Release Announcement, 4.0.0 — https://kafka.apache.org/blog/2025/03/18/apache-kafka-4.0.0-release-announcement/ — checked 2026-10-30
- [14] morgando — Request for KIP-890 support (GitHub, confluentinc/librdkafka issue #5423, 2026; opinion) — https://github.com/confluentinc/librdkafka/issues/5423 — checked 2026-10-30
- [15] Confluent — librdkafka commit f846408, "txn: Initial KIP-890 Part 2 transaction protocol v2 support (#5423)" — https://github.com/confluentinc/librdkafka/commit/f8464088dc76b2c4f39d4393956d2c737d50f099
- [16] Confluent — librdkafka CHANGELOG (master branch, its unreleased section included) — https://github.com/confluentinc/librdkafka/blob/master/CHANGELOG.md
- [17] Redpanda — Introduction to Redpanda (Redpanda sells it) — https://docs.redpanda.com/current/get-started/intro-to-events/
- [18] Redpanda — licenses (folder README) — https://github.com/redpanda-data/redpanda/tree/dev/licenses
- [19] Redpanda — Business Source License (licenses/bsl.md) — https://github.com/redpanda-data/redpanda/blob/dev/licenses/bsl.md
- [20] Jack Vanlightly — Kafka vs Redpanda Performance - Do the claims add up? (jack-vanlightly.com, 2023; research; the author works at Confluent, a Kafka vendor that competes with Redpanda) — https://jack-vanlightly.com/blog/2023/5/15/kafka-vs-redpanda-performance-do-the-claims-add-up
- [21] kafka-python — CHANGES.md, 3.0.7 — https://github.com/dpkp/kafka-python/blob/master/CHANGES.md
- [22] GitHub — kafka-python contributors (REST API) — https://api.github.com/repos/dpkp/kafka-python/contributors — checked 2026-10-30
- [23] aiokafka — README — https://github.com/aio-libs/aiokafka
- [24] aiokafka — CHANGES.rst, 0.15.0 — https://github.com/aio-libs/aiokafka/blob/master/CHANGES.rst
- [25] Apache Kafka — Broker Configs, 4.4 — https://kafka.apache.org/44/configuration/broker-configs/
- [26] Confluent — librdkafka CONFIGURATION.md, v2.16.0 — https://github.com/confluentinc/librdkafka/blob/v2.16.0/CONFIGURATION.md
- [27] Apache Kafka — Producer Configs, 4.4 — https://kafka.apache.org/44/configuration/producer-configs/
- [28] Confluent — confluent_kafka API, confluent-kafka 2.16.0 — https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html
- [29] Confluent — librdkafka INTRODUCTION.md — https://github.com/confluentinc/librdkafka/blob/master/INTRODUCTION.md
- [30] Confluent — confluent-kafka-python KIP-848 migration guide — https://github.com/confluentinc/confluent-kafka-python/blob/master/docs/kip-848-migration-guide.md
- [31] Apache Kafka — Monitoring, 4.3 — https://kafka.apache.org/43/operations/monitoring/
- [32] Socure — RETROACTIVE: [Sev2] RiskOS Delayed Webhook Deliveries (Socure status page, 2026; case) — https://status.socure.com/incidents/167ly5ws2xsk
