# Message brokers and pub/sub

Rules for Python code that publishes messages to a broker or consumes them: RabbitMQ through aio-pika or pika, and a managed cloud queue, with Amazon SQS as the example.

**Navigation**

- [1. Purpose and scope](#1-purpose-and-scope)
- [2. A data store, a broker and an event log](#2-a-data-store-a-broker-and-an-event-log)
- [3. When a service needs no broker of its own](#3-when-a-service-needs-no-broker-of-its-own)
- [4. Which broker](#4-which-broker)
- [5. Connections and channels](#5-connections-and-channels)
- [6. Fan-out: one copy for each subscriber](#6-fan-out-one-copy-for-each-subscriber)
- [7. Quorum queues](#7-quorum-queues)
- [8. Publishing: confirms and persistent messages](#8-publishing-confirms-and-persistent-messages)
- [9. Consuming: manual acknowledgements and prefetch](#9-consuming-manual-acknowledgements-and-prefetch)
- [10. Amazon SQS: visibility, deletion and FIFO limits](#10-amazon-sqs-visibility-deletion-and-fifo-limits)
- [11. The settings you set](#11-the-settings-you-set)
- [12. Common mistakes](#12-common-mistakes)
- [13. Where the rules stop holding](#13-where-the-rules-stop-holding)
- [14. Alternatives considered](#14-alternatives-considered)
- [15. Security](#15-security)
- [16. Checks](#16-checks)
- [17. Sources](#17-sources)

## 1. Purpose and scope

This file is for everyone who writes Python code that sends a message to another service through a broker, or receives one: people and AI agents alike. It covers two jobs. In a work queue, each message goes to one consumer, which acknowledges it when the work is done. In fan-out, also called pub/sub, each subscriber gets its own copy of every message.

A project that follows it loses no message when a consumer crashes or a connection drops, and its consumers stay correct when the same message arrives twice.

The rule that holds the rest together: **publish with confirms, acknowledge a message only after its work is done unless [delivery.md](delivery.md) section 12's case applies, and make every consumer safe to run twice.** RabbitMQ's quorum-queue guide asks for the first two: publishers should use publisher confirms, and consumers manual acknowledgements [1]. The third is needed because every tool here can deliver a message twice ([delivery.md](delivery.md) section 2).

What this file leaves to others:

- The delivery rules every job shares are in [delivery.md](delivery.md): duplicates (section 2), the idempotent consumer (section 3), the outbox (section 4), retries and delayed retries (section 5), dead-letter queues (section 6), ordering (section 7), message contracts (section 8), tracing (section 9), and security and personal data in messages (section 10). This file keeps only what RabbitMQ and SQS add to them.
- Work that one Python application both sends and does belongs to a task queue: [task-queues.md](task-queues.md).
- Events that several readers read, and read again, belong to an event log: [event-streaming.md](event-streaming.md).
- Running the broker (clustering, upgrades, capacity), brokers built around Java's JMS, and MQTT are out of scope.

A full consumer, with its idempotency check and its log lines, is in [consumer-example.md](consumer-example.md).

Not covered yet, because the research found no source that settles it:

- a measured point at which running your own broker costs less than a managed queue;
- an independent test of RabbitMQ 4.x: the only RabbitMQ analysis on Jepsen's list is of version 3.3.0, from 2014 [2];
- how many teams use each broker: the surveys do not ask, and downloads include CI runs.

## 2. A data store, a broker and an event log

Redis, RabbitMQ and Kafka can each pass a message from one service to another, so people compare them. They are three kinds of tool, and a message lives differently in each.

| Tool | What it is | What happens to a message |
|---|---|---|
| Redis | A data store: its README calls it a "cache, data structure server, and document and vector query engine" [3] | Pub/sub delivers at most once: "If the subscriber is unable to handle the message (for example, due to an error or a network disconnect) the message is forever lost" [4]. Redis streams persist messages instead [4]. |
| RabbitMQ | A "messaging and streaming broker" [5] | A queue is a point-to-point channel, "which ensures that only one receiver will receive a particular message" [6]. A RabbitMQ stream is "an append-only log of messages that can be repeatedly read until they expire" [7]. |
| Kafka | "an event streaming platform" [8] | Events "can be read as often as needed", and "events are not deleted after consumption" [8]. |

Pick the file by the job, not by the product:

- a copy of data kept to answer faster: [caching.md](caching.md), which also covers Valkey;
- work the same application does later: [task-queues.md](task-queues.md);
- messages between services, each to one consumer, or one copy to each subscriber: this file;
- events that several readers read and read again: [event-streaming.md](event-streaming.md).

## 3. When a service needs no broker of its own

A broker of your own is one more server to run, patch and watch. Before you add one, check the two simpler ways.

- **The code that sends the work and the code that does it are one Python application.** Use a task queue, or a queue in the PostgreSQL the application already has ([task-queues.md](task-queues.md)). The application then holds no code that talks to a broker directly.
- **The application runs on one cloud, and that cloud has a queue.** A managed queue saves running a broker. AWS's decision guide, speaking for its own services, says "It's common that some organizations spend more time than they would like on maintaining open-source integrations" [9]. The SQS guide recommends SQS and SNS "for new applications that can benefit from nearly unlimited scalability and simple APIs" [10]. Both are AWS's words about its own products.

A broker of your own fits when neither holds: the consumers are other services, the code must not depend on one cloud, or the routing needs RabbitMQ's exchanges (section 6). The research found no measured point at which running a broker yourself becomes cheaper (section 1).

## 4. Which broker

| Tool (Python client) | Use it when | Too much, or the risk |
|---|---|---|
| RabbitMQ: aio-pika for async code, pika for sync code | The service runs its own broker, for work queues with an acknowledgement per message and for fan-out through exchanges (section 6). pika is the Python client the RabbitMQ team supports officially; aio-pika, "built for Python 3 and asyncio", is listed without that mark [11]. | Patches for a series out of community support go to paying users only, "with potential exception for very high severity CVEs" [12]. On 2026-10-29 two series had community support: 4.3 until 2027-01-31, and 4.4 until 2027-07-31 [13]. 4.4 came out on 20 October 2026 [14], and 4.3.0 on 23 April 2026 [13], so a series gets about nine months of free patches, and a broker you run needs a minor upgrade in each window. aio-pika rests on one main committer: one contributor has 1,020 commits against 58 for the next [51]. |
| A managed cloud queue: Amazon SQS through boto3, or the queue of the cloud in use | The application runs on that cloud and needs a queue with no broker to run (section 3). | It ties the code to one cloud. A standard queue delivers at least once and may deliver out of order [15]. A FIFO queue keeps order but takes 300 transactions per second per API action by default [16] (section 10). Delays and retries follow the service's limits ([delivery.md](delivery.md) section 5). |

The clients:

- **aio-pika** 10.2.1 is the current release, for Python 3.11 and later [17]. Its `connect_robust` gives "Transparent auto-reconnects with complete state recovery" [17] (section 5).
- **pika**: pin 1.4.4, the latest stable release; 1.5.0 is still a release candidate, 1.5.0rc2 [18]. 1.5.0 adds `pika.Connection`, and its notes say "If you are starting new code, use `pika.Connection`" [19]. The old adapters, `BlockingConnection` among them, warn that they "will be removed in Pika 2.0" [19]. When 1.5.0 is released, write new sync code against `pika.Connection`, so it needs no rewrite for 2.0.
- **boto3**: its SQS guide covers creating and using a queue, and sending and processing messages [20]. The redrive policy for a dead-letter queue is on a separate example page [21].

Named once, and not described here:

- **NATS JetStream, for work that must not be lost.** In Jepsen's test of NATS 2.12.1, NATS by default "calls `fsync` to flush data to disk only once every two minutes, but acknowledges messages immediately", and in one test run simulated power failures made it lose 131,418 of 930,005 messages [22]. NATS has since documented the risk of that default [22].
- **RabbitMQ's AMQP 1.0 Python client, not yet.** Its README says "Version 1.0 will be deprecated in the November 2026" [23]. The maintainer's plan is no new features in 1.0, and a 2.0 that "is not compatible with 1.0", with the first stable 2.0.0 aimed at November 2026 [24]. Code written against 1.0 today needs a rewrite within months.

## 5. Connections and channels

A connection to RabbitMQ carries channels, and a channel is the session the work runs on. RabbitMQ builds both to live long: channel leaks and a high rate of opening and closing channels "eventually lead to node exhaustion of resources" [25].

- **Open one connection per process, at startup, in the one client of the broker, and keep it open.** RabbitMQ's guides "assume long-lived connections (a new connection is not opened per protocol operation) for efficiency" [26], and tell publishers "Prefer long lived connections when possible" [27]. The client lives in `core/rabbitmq_client.py`, and the adapter builds it once ([file-structure.md](../../any-language/file-structure/file-structure.md) section 4). aio-pika's docs find one connection, which carries many channels over one socket, "is sufficient for most applications", and add a pool only when that connection saturates [28].
- **Give each consumer its own channel, keep the number of channels small, and never share a channel between threads.** RabbitMQ's channel guide starts from one channel per thread, process or coroutine, and finds that "most applications can use a single digit number of channels per connection" [25]. Its publishers guide calls publishing from several threads on one channel unsafe [27].
- **In async code, connect with `aio_pika.connect_robust`, and treat a message you held when the connection dropped as one that will come again.** `connect_robust` reconnects and restores the state it had, consumers included [17]. But "Reconnecting with `connect_robust()` does not make an old message valid on the replacement channel" [28]. Its `ack()` then raises `ChannelInvalidStateError`, RabbitMQ requeues the delivery, and the consumer receives it again [28], so the work must be safe to repeat ([delivery.md](delivery.md) section 3).
- **In sync code with pika, keep each connection in the thread that opened it.** pika's adapters "are not thread-safe. Each connection instance is confined to the thread that created it" [29]. The one call another thread may make is `add_callback_threadsafe`, which runs a callback on the connection's own thread [29]. A worker thread that finishes a message hands its `basic_ack` to the connection thread that way, and never calls it itself. pika 1.5's `pika.Connection` "exposes a blocking API that is safe to call from any number of threads simultaneously" [29].

The connection, in `src/acme/core/rabbitmq_client.py`. The worker's `main()` reads the values from the settings class ([python.md](../language/python.md) section 5, [settings-example.md](../language/settings-example.md)) and calls it once:

```python
"""The one way into RabbitMQ: every connection and every publish goes through here."""

import ssl

import aio_pika
from aio_pika.abc import AbstractRobustConnection
from pydantic import SecretStr


async def connect_rabbitmq(
    host: str, port: int, user: str, password: SecretStr, vhost: str
) -> AbstractRobustConnection:
    # The default context requires the broker's certificate and checks its host
    # name (message-brokers.md section 15).
    tls = ssl.create_default_context()
    tls.minimum_version = ssl.TLSVersion.TLSv1_2

    # Every value is passed: aio-pika falls back to guest/guest without TLS.
    return await aio_pika.connect_robust(
        host=host,
        port=port,
        login=user,
        password=password.get_secret_value(),
        virtualhost=vhost,
        ssl=True,
        ssl_context=tls,
    )
```

It is good because every input is a parameter, so a test can call it with plain values ([readability.md](../../any-language/readability/readability.md) section 6), and the password stays a `SecretStr` until the one line that needs its text. Nothing is left to aio-pika's defaults, which are the `guest` user, the `guest` password and no TLS [30], and the TLS context verifies the broker before any credential is sent (section 15). `connect_robust` reconnects by itself, which is why the consumers in sections 7 and 9 must take a message twice.

## 6. Fan-out: one copy for each subscriber

One event, such as an order placed, must reach billing, shipping and email, and a subscriber that is down for an hour must still get it.

- **On RabbitMQ, publish to an exchange, and give each subscriber its own named, durable queue bound to it.** "The core idea in the messaging model in RabbitMQ is that the producer never sends any messages directly to a queue" [31]. The producer publishes to an exchange, and a binding links the exchange to a queue [31]. The tutorial's subscriber uses an exclusive queue, because "once we disconnect the consumer the queue should be deleted" [32]. That suits log lines nobody needs later. A subscriber that must not miss an event declares a named queue of its own instead, which keeps the messages while the subscriber is down. The queue is a quorum queue (section 7), and the code that declares it is at the end of section 7.
- **Use a fanout exchange when every subscriber wants every message it carries, and a topic exchange when it carries several kinds of event.** A fanout exchange "just broadcasts all the messages it receives to all the queues it knows" [32], so it fits an exchange for one event type. RabbitMQ's tutorials move from a fanout, "only capable of dummy broadcasting", to exchanges that route by key, for "a possibility of selectively receiving the logs" [47]. A topic exchange delivers a message "to all the queues that are bound with a matching binding key" [47], so each subscriber binds its queue to the keys of the events it reads, such as `orders.order_placed`, and its parser never sees the others. The cost: a message whose key matches no binding "will be discarded" [47], unless it was published as mandatory (section 8).
- **On AWS, put an SNS topic in front of one SQS queue per subscriber.** The SQS guide: "To prevent message loss when subscribers are offline, integrating Amazon SNS with Amazon SQS queue messages ensures consistent delivery" [10].
- **Never use Redis pub/sub to fan out messages that must arrive.** A subscriber that is down, or fails on a message, loses it for good [4].
- **For a large fanout on RabbitMQ, look at streams first.** RabbitMQ lists large fanouts among the cases where quorum queues fit less, and finds streams "likely to be a better fit" there [1]. This file does not describe the stream clients; the log model is in [event-streaming.md](event-streaming.md).

## 7. Quorum queues

A queue that lives on one node loses its messages with that node. The old replicated type, classic mirrored queues, "were removed in RabbitMQ 4.0" [33]. A quorum queue is "a durable, replicated queue based on the Raft consensus algorithm", and RabbitMQ says it "should be considered the default choice when needing a replicated, highly available queue" [1].

- **Declare every work queue and every subscriber queue as a quorum queue, in the code that declares it.** Pass the `x-queue-type` argument with the value `quorum`. Only the declaration can set it: it "cannot be set or changed using a policy", and the default is a classic queue [1].
- **Declare it with `durable=True`.** Quorum queues "are always durable per their assumed use cases" [1], and aio-pika's `declare_queue` defaults to `durable=False` [30].
- The delivery limit, what counts toward it, the dead-letter exchange and at-least-once dead-lettering: [delivery.md](delivery.md) section 6.
- Delayed retries on quorum queues are in [delivery.md](delivery.md) section 5.

Where quorum queues fit less, RabbitMQ lists temporary queues (transient or exclusive, or a high rate of declaring and deleting), the lowest possible latency, data safety that is not a priority, very long backlogs of 5 million messages or more, and large fanouts; for the last two it points to streams [1]. Its use-case section adds that "Stock tickers, instant messaging systems and RPC reply queues benefit less or not at all from use of quorum queues" [1]. A quorum queue also refuses a channel-wide prefetch (section 9).

Billing's queue for order events, in the worker adapter's `src/acme/worker/handlers_charge_order.py` ([file-structure.md](../../any-language/file-structure/file-structure.md) section 5). The worker's `main()` passes the prefetch count from the settings class. `open_event_exchange`, which declares the durable topic exchange `acme.events`, is in section 8; billing's dead-letter exchange and its queue, and the import of `aio_pika` they need, are [consumer-example.md](consumer-example.md) section 4's, cut with `...`:

```python
"""The worker's way into charge_order: billing's queues and its message handler."""

from typing import Final

from aio_pika.abc import AbstractQueue, AbstractRobustConnection

from acme.core.rabbitmq_client import open_event_exchange
from acme.core.schemas import RoutingKey

BILLING_QUEUE: Final = "billing.order_placed"


async def open_billing_queue(
    connection: AbstractRobustConnection, prefetch_count: int
) -> AbstractQueue:
    # A channel of its own: a channel is never shared (message-brokers.md section 5).
    channel = await connection.channel()

    # Per consumer, and never 0: aio-pika's default of 0 means no limit
    # (message-brokers.md section 9).
    await channel.set_qos(prefetch_count=prefetch_count)

    ...  # Billing's dead-letter exchange and its queue: consumer-example.md section 4

    events = await open_event_exchange(channel)

    queue = await channel.declare_queue(
        BILLING_QUEUE,
        durable=True,  # Quorum queues are always durable; aio-pika defaults to False.
        arguments={
            "x-queue-type": "quorum",  # A policy cannot set the type.
            # RabbitMQ's default, 30 minutes, written: a delivery held longer goes
            # back to the queue (message-brokers.md section 9).
            "x-consumer-timeout": 1_800_000,
        },
    )

    # Only OrderPlaced reaches this queue's parser: the exchange is a topic
    # (message-brokers.md section 6).
    await queue.bind(events, routing_key=RoutingKey.ORDER_PLACED)

    return queue
```

It is good because the queue survives the loss of a node and of the subscriber: it is a named, durable quorum queue bound to the topic exchange by the key of the one event billing reads, so the events wait while billing is down. The key is the `RoutingKey` member the outbox relay publishes `OrderPlaced` with, not a bare `str` ([python.md](../language/python.md) section 3). Each line a copier might drop names its reason. The `durable` flag means the queue survives a broker restart, and `declare_queue` defaults it to `False` [30]. The consumer timeout is written at its default, so a reader can check the handler's longest run against it ([delivery.md](delivery.md) section 5). The dead-letter exchange and the delivery limit come from a policy the change ships, which [consumer-example.md](consumer-example.md) section 4 shows.

## 8. Publishing: confirms and persistent messages

Without a confirm, `publish` returns as soon as the message is written to the socket, and the broker never says it took it [30].

- **Publish on a channel with publisher confirms, and count a message as sent only when the broker confirms it.** RabbitMQ: "In order to guarantee persistence, a client should use confirms" [34]. Its publishers guide calls confirms "critically important" for reliable publishing [27]. In aio-pika, `channel(publisher_confirms=True)` is the default: `publish` then waits for the broker's ack and raises `DeliveryError` on a nack [30]. In pika, call `channel.confirm_delivery()` once on the channel, which turns confirm mode on [35].
- **Publish every message as mandatory, and write `mandatory=True` at the call.** When no queue takes a message that is not mandatory, the message "is discarded or republished to an alternate exchange, if any"; a mandatory one "will be returned to it", and "The publisher must have a returned message handler set up in order to handle the return" [27]. The broker confirms an unroutable message all the same, and for a mandatory one it sends the return before the ack [34]. aio-pika's `publish` defaults to `mandatory=True` [48].
- **Count a returned message as not sent: open the publishing channel with `on_return_raises=True`.** On a channel opened with aio-pika's default `on_return_raises=False` [39], `publish` hands back the returned message instead of raising [48], and a publisher that deletes its copy once `publish` returns, as the outbox relay does, then loses the event. With `on_return_raises=True`, `publish` raises `PublishError`, a `DeliveryError` [48], [49]. A returned message then stays with the publisher, and every message behind it in an outbox waits until a queue is bound to its key.
- **Declare each subscriber's queue, bound to its key, before the first event with that key is written.** Why: a returned message holds the outbox back (the rule above), and a queue bound in time keeps that from happening.
- **When a publish fails or its confirm is lost, publish again, and let the consumer drop the second copy.** A nack means the broker "refuses responsibility" for the message, and the client may then publish it again [34]. A connection from `connect_robust` restores the channel but does not replay a failed publish, and its reference warns: "A lost confirmation does not mean the broker rejected the message, so retrying can produce duplicates" [30]. This is why each message carries an id, and each consumer drops a copy it has seen ([delivery.md](delivery.md) section 3).
- **Give every message an id, and mark it persistent.** Set `message_id` to the event's own id. Set `delivery_mode` to `DeliveryMode.PERSISTENT`: a quorum queue stores every message, but a dead-lettered copy keeps its delivery mode, and it survives a restart in the dead-letter queue only when it was published persistent [1].
- **Publish only what the database committed**, through the outbox of [delivery.md](delivery.md) section 4.
- **Declare the exchange durable.** aio-pika's `durable` makes the exchange survive a broker restart, and its default is `False` [30].

The publisher side, in the same `src/acme/core/rabbitmq_client.py` as the connection in section 5. The file's imports gain `Final` from `typing`, `UUID` from `uuid`, `AbstractChannel` and `AbstractExchange` from `aio_pika.abc`, and `RoutingKey` from `acme.core.schemas`. The worker's `main()` opens the channel once, with `connection.channel(publisher_confirms=True, on_return_raises=True)`, and passes it in; [outbox-relay-example.md](outbox-relay-example.md) section 8 shows that line:

```python
EVENTS_EXCHANGE: Final = "acme.events"


async def open_event_exchange(channel: AbstractChannel) -> AbstractExchange:
    return await channel.declare_exchange(
        EVENTS_EXCHANGE,
        # Topic: each subscriber binds its queue to the keys it wants
        # (message-brokers.md section 6).
        aio_pika.ExchangeType.TOPIC,
        # Durable: aio-pika's default would lose the exchange when the broker restarts.
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
        # A dead-lettered copy keeps this mode; it survives a restart if persistent.
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )

    # On a channel with confirms and on_return_raises=True, this returns after the
    # broker's ack, and a nack or a returned message raises. mandatory=True is
    # aio-pika's default, written out: without it a message no queue takes is
    # dropped and still confirmed (message-brokers.md section 8). The broker's
    # errors leave here as they are: the caller wraps them, a departure its use
    # case declares (outbox-relay-example.md section 7).
    await exchange.publish(message, routing_key=routing_key, mandatory=True)
```

It is good because `publish_event` returns only when the broker has taken the message into a queue, and a refusal or a returned message is an exception the caller sees, not a silent loss. The message carries the id a consumer needs to drop a duplicate, and it is persistent. The caller passes the routing key and the body already encoded from the event's model, which lives in the module's `schemas.py` ([python.md](../language/python.md) section 4). The key is a `RoutingKey`, a closed set declared in `core/schemas.py`, because an event name is a closed set and never a bare `str` ([python.md](../language/python.md) section 3). The caller that runs it is the outbox relay of [delivery.md](delivery.md) section 4, not a request handler.

## 9. Consuming: manual acknowledgements and prefetch

With automatic acknowledgement, RabbitMQ counts a message as delivered "immediately after it is sent" [34], so a consumer that crashes during the work loses the message.

- **Acknowledge manually, after the work and its transaction have committed.** RabbitMQ: "automatic message acknowledgement should be considered unsafe and not suitable for all workloads" [34]. In aio-pika, write `no_ack=False` at the call that consumes, though it is the default [30], as [delivery.md](delivery.md) section 5 asks; call `message.ack()` after the work returns, and call `message.reject()` by hand on each failure path. Not `message.process()`: when its block raises, it rejects the message and lets the exception go on [36]; aiormq runs each delivery's callback as a task and logs one that fails as "Consumer callback failed" at `ERROR`, with the exception [50]. The text of a pydantic `ValidationError` holds the input it rejected ([python.md](../language/python.md) section 4), so the body would reach the log, which [logging.md](../logging/logging.md) section 10 rules out. In pika, write `auto_ack=False` at `basic_consume` the same way; it is the default there too [35]. The order of the commit and the ack is [delivery.md](delivery.md) section 3.
- **Reject without requeue only a message no retry can fix, such as a body that does not parse, and let the dead-letter exchange take it.** "if all consumers requeue because they cannot process a delivery due to a transient condition, they will create a requeue/redelivery loop" [34]. With `requeue=False`, aio-pika's default, the broker drops the message or routes it to the queue's dead-letter exchange [28], so the queue's dead-letter exchange must be in place before the first message ([delivery.md](delivery.md) section 6). Return any other failure with `reject(requeue=True)`, which sends a `basic.reject` [36]. Why `reject` and not `nack`, and the delivery limit that ends the loop the quote warns about, are [delivery.md](delivery.md) section 6; its `delayed-retry-type` row spaces the attempts.
- **Acknowledge on the channel that delivered the message.** "Because delivery tags are scoped per channel, deliveries must be acknowledged on the same channel they were received on" [34].
- **Acknowledge each message within 30 minutes, or expect it to come again.** The timeout is 30 minutes by default [37]. A consumer that passes it is cancelled when its client supports the `consumer_cancel_notify` capability, and otherwise its channel is closed; in both cases its messages go back to the queue [1]. "Starting with RabbitMQ 4.3, delivery acknowledgement timeouts are only supported by quorum queues" [37]. Write the timeout on the queue, the default's value included (section 11).
- **Set a prefetch count from the settings class, and never 0.** The prefetch count caps how many unacknowledged messages a consumer holds. A value of 0 "is treated as infinite" [38], and aio-pika's `set_qos` and pika's `basic_qos` both default to 0 [39], [35]. RabbitMQ finds that "Values in the 100 through 300 range usually offer optimal throughput", while 1 "is the most conservative" and "will significantly reduce throughput" [34]. The timeout above runs for each delivered message, and a prefetched message waits behind the slow ones, so a handler that takes minutes needs a small prefetch.
- **Keep the prefetch per consumer, never per channel.** RabbitMQ applies `prefetch_count` "separately to each new consumer on the channel" [38], and quorum queues "do not support global QoS prefetch": consuming with it returns a channel error [1]. aio-pika's `set_qos` is per consumer unless you pass `global_=True` [39]; pika's `basic_qos` unless you pass `global_qos=True` [35].

The handler, in the same `src/acme/worker/handlers_charge_order.py` as the queue in section 7. The file's imports gain `AbstractIncomingMessage` from `aio_pika.abc`, `ValidationError` from `pydantic`, `ChargeOrder` from `acme.billing.charge_order.usecase` and `OrderPlaced` from `acme.worker.schemas`. The loop that hands it one message at a time, which must write `no_ack=False` at its `iterator()` call (section 9), its two log lines, the check that stops the worker once billing's database connection has closed, and the `INFO` line after the ack are [consumer-example.md](consumer-example.md) section 7's, left out or cut with `...`:

```python
async def on_order_placed(
    message: AbstractIncomingMessage, charge_order: ChargeOrder
) -> None:
    # Ack and reject by hand, never message.process(): it re-raises, and aiormq's
    # error line would then hold the body (message-brokers.md section 9).
    try:
        # A message is outside data, parsed into a model once (python.md section 4).
        event: OrderPlaced | None = OrderPlaced.model_validate_json(message.body)
    except ValidationError:
        event = None

    if event is None:
        ...  # One INFO line with the message id, never the error's text

        # No retry can fix the body: the dead-letter exchange takes it at once.
        # Outside the except block: a reject that failed inside it would carry the
        # ValidationError, and the body in its text, as its context (logging.md
        # section 10).
        await message.reject(requeue=False)

        return

    try:
        await charge_order.run(
            event_id=event.event_id,
            order_id=event.order_id,
            amount_minor=event.amount_minor,
            currency=event.currency,
        )
    except Exception:
        ...  # One WARNING line with the message id

        # Through reject, never nack: the delivery limit counts a reject
        # (delivery.md section 6).
        await message.reject(requeue=True)

        return

    # After run() has committed: a crash before this line brings a redelivery that
    # the id row skips, never a lost charge (delivery.md section 3).
    await message.ack()
```

It is good because the message is acknowledged only after `charge_order.run` returns, and each failure is settled by hand on the path that handles it. A body that does not parse goes to the dead-letter exchange at once, because no retry can fix it; any other failure goes back through `reject`, which counts toward the delivery limit ([delivery.md](delivery.md) section 6). The body is parsed once, at the edge, into the adapter's `OrderPlaced` model, so the use case gets typed values. Left out here: the use case records `event_id` in the same transaction as the charge, so a second copy changes nothing ([delivery.md](delivery.md) section 3), and each failure path logs one line, with the message id and never the body ([logging.md](../logging/logging.md) sections 5 and 10). [consumer-example.md](consumer-example.md) shows both.

## 10. Amazon SQS: visibility, deletion and FIFO limits

On SQS, deleting a message does the job of the acknowledgement. A received message stays in the queue, hidden for the visibility timeout, until the consumer deletes it [40].

- **Delete a message only after its work has committed.** A message that is not deleted before its visibility timeout ends becomes visible again and is received again [40]. boto3's guide deletes each message after it has processed it, with `message.delete()` [20].
- **Set the queue's visibility timeout longer than the longest run of the handler.** SQS does not promise that a message is delivered only once within the timeout [40]; its default and its 12-hour cap are in [delivery.md](delivery.md) section 5. A handler that may run longer extends the timeout with `ChangeMessageVisibility` while it works [40]. The value it sets is not kept for the next receive ([delivery.md](delivery.md) section 5).
- **Give every queue a redrive policy.** It names the dead-letter queue (`deadLetterTargetArn`) and the number of receives a message gets before it moves there (`maxReceiveCount`). boto3 sets it with `set_queue_attributes`, and its example passes the count as a string, `'10'` [21]. Retention and the alarm on the dead-letter queue are [delivery.md](delivery.md) section 6.
- **When the order matters, use a FIFO queue, and plan for its throughput limit.** A FIFO queue keeps order per message group ([delivery.md](delivery.md) section 7). By default it takes 300 transactions per second per API action for `SendMessage`, `ReceiveMessage` and `DeleteMessage`, and requests over that fail with a throttling error even when messages are waiting. The batch actions raise the limit to 3,000 messages per second per action, and high throughput mode is the other way [16].
- A standard queue delivers at least once and may deliver out of order [15], so its consumer drops duplicates ([delivery.md](delivery.md) section 3) and does not depend on the order ([delivery.md](delivery.md) section 7).

## 11. The settings you set

The delivery limit, delayed retry, the dead-letter exchange, at-least-once dead-lettering and the SQS redrive policy are in the table of [delivery.md](delivery.md) section 6.

| Field | What it means | Set it when | Leave it out when |
|---|---|---|---|
| `x-queue-type: quorum` (queue argument) | The replicated, durable queue type. The default is classic, and a policy cannot set it [1]. | Always, on a work queue or a subscriber's queue. | The queue is temporary or exclusive, the lowest latency matters more than safety, or it holds a very long backlog or feeds a large fanout, where a stream fits better [1]. |
| `durable=True` (queue and exchange) | The queue or the exchange survives a broker restart. aio-pika's default is `False` [30]. | Always on a quorum queue, which is always durable [1], and on the exchange it is bound to. | A temporary queue that should go with its consumer, such as the tutorial's exclusive queue [32]. |
| `prefetch_count` (aio-pika `set_qos`, pika `basic_qos`) | The most unacknowledged messages one consumer holds. 0, the default of both clients, means no limit [38], [39], [35]. | Always, from the settings class (section 9). | The research found no case. |
| `no_ack=False` (aio-pika `consume()`, `iterator()`), `auto_ack=False` (pika `basic_consume`) | Manual acknowledgement: the broker keeps each message until the consumer settles it. `False` is the default of both [30], [35]. | Always, the default's value included ([delivery.md](delivery.md) section 5). | Never. |
| `x-consumer-timeout` (queue argument), `consumer-timeout` (policy key) | How long, in milliseconds, a consumer may hold a delivery before RabbitMQ takes it back; 30 minutes by default, and from RabbitMQ 4.3 only quorum queues support it [37], [1]. | Always, the default's value included ([delivery.md](delivery.md) section 5): above the longest run of the handler (section 9). | Never. |
| `publisher_confirms=True` (aio-pika `channel()`), `confirm_delivery()` (pika) | The broker confirms each message it took. aio-pika turns it on by default; pika needs the call [30], [35]. | Always, the default's value included ([delivery.md](delivery.md) section 5): `True` for a message that must arrive; `publisher_confirms=False` on a channel that runs AMQP transactions [28]; in pika, `confirm_delivery()` on every channel without transactions. | Never. |
| `mandatory=True` (aio-pika `publish`), `on_return_raises=True` (aio-pika `channel()`) | A message no queue takes comes back to the publisher, and `publish` raises `PublishError` for it. `mandatory` defaults to `True`, `on_return_raises` to `False` [48], [39]. | Always, for a message the publisher deletes or forgets once it is sent (section 8). | The research found no case for a message that must arrive. |
| `delivery_mode=DeliveryMode.PERSISTENT` (message) | The message is persistent, and a dead-lettered copy keeps that mode [1]. | Every message that must survive a restart, in its queue or its dead-letter queue. | The research found no case for a message that must arrive. |
| `message_id` (message) | The id a consumer drops a second copy by ([delivery.md](delivery.md) section 3). | Always. | The research found no case. |
| `VisibilityTimeout` (SQS queue attribute) | How long a received message stays hidden [40]; its default and cap are in [delivery.md](delivery.md) section 5. | Always, the default's value included ([delivery.md](delivery.md) section 5): longer than the longest run of the handler. | Never. |

Required on RabbitMQ: the queue type, `durable`, the prefetch count, manual acknowledgement, the consumer timeout, publisher confirms, mandatory publishing with returns raised, the persistent delivery mode and the message id; the dead-letter exchange and the delivery limit are required by [delivery.md](delivery.md) section 6. Required on SQS: the visibility timeout; the redrive policy is required by [delivery.md](delivery.md) section 6.

## 12. Common mistakes

Each of these is a mistake a source names:

- **Automatic acknowledgement**, `no_ack=True` in aio-pika or `auto_ack=True` in pika. RabbitMQ calls it unsafe, because the message counts as delivered once it is sent [34]. A consumer that crashes loses the message. Fix: section 9.
- **No prefetch, or a prefetch of 0.** It is what a consumer gets when it never calls `set_qos` or `basic_qos` with a count [39], [35]. RabbitMQ says manual acknowledgement "with unlimited prefetch should be used with care" [34]. Fix: section 9.
- **Requeueing every message that fails.** All consumers requeueing a message they cannot process "will create a requeue/redelivery loop", and such loops "can be costly in terms of network bandwidth and CPU resources" [34]. Fix: reject without requeue what no retry can fix, and let the delivery limit end the retries of the rest (section 9).
- **Rejecting without a dead-letter exchange.** The message is dropped [1], [28]. Fix: [delivery.md](delivery.md) section 6.
- **A connection, or a channel, per publish.** RabbitMQ assumes connections that live long [26], and each channel takes memory and a few Erlang processes on the broker's node, so channel leaks and high channel churn wear out the broker, not the client [25]. Fix: section 5.
- **A pika connection or channel used from several threads.** pika's old adapters are not thread-safe [29], and RabbitMQ calls a channel shared by publishing threads unsafe [27]. Fix: `add_callback_threadsafe`, or pika 1.5's `pika.Connection` (section 5).
- **Acknowledging a message after a reconnect.** The message belongs to the closed channel, and its `ack()` raises [28]. Fix: let the redelivered copy do the work, and make it safe to repeat (section 5).
- **Connecting with the client's defaults.** aio-pika falls back to `guest`/`guest` without TLS [30]. By default `guest` can connect only from localhost [41], and "Production environments should not use the default user" [41]. Fix: section 15.
- **Redis pub/sub for messages that must arrive.** A subscriber that is down loses them for good [4]. Fix: section 6.
- **An SQS visibility timeout shorter than the handler.** The message becomes visible again while the first consumer still works on it, and a second one takes it [40]. Fix: section 10.

## 13. Where the rules stop holding

- **The sender and the worker are one Python application.** A task queue fits, and its library sets the acknowledgement and the prefetch: [task-queues.md](task-queues.md). Celery or Dramatiq on top of RabbitMQ follow that file, not this one.
- **Several readers read the same events and read them again, or the backlog runs to millions.** A log fits: RabbitMQ's streams [7] or Kafka ([event-streaming.md](event-streaming.md)). RabbitMQ names very long backlogs and large fanouts as cases for streams [1].
- **The lowest latency matters more than safety.** A quorum queue has "an inherently higher latency due to its data safety features" [1]. That is the price of section 7, and a queue whose messages may be lost can stay classic.
- **Request and reply.** RPC reply queues gain little from quorum queues [1], and this file does not describe request and reply over a broker.
- **Long handlers.** The prefetch range of 100 to 300 is RabbitMQ's guide for throughput [34]. A handler that runs for minutes holds each prefetched message against the 30-minute timeout (section 9), so it takes a small prefetch.

## 14. Alternatives considered

- **NATS JetStream**, for its default fsync, under which Jepsen's test lost acknowledged writes (section 4).
- **RabbitMQ's AMQP 1.0 Python client**, until its 2.0 is stable (section 4).
- **Redis pub/sub** for fan-out, because it delivers at most once (section 6). Redis streams persist messages [4], but each job here describes at most two tools, and this practice covers Redis as a cache ([caching.md](caching.md)) and as a task-queue broker ([task-queues.md](task-queues.md)), not as a broker between services.
- **Classic mirrored queues**, removed in RabbitMQ 4.0 [33]; quorum queues replace them (section 7).
- **Kafka as a work queue**: [event-streaming.md](event-streaming.md) says why its queues are not ready from Python yet.
- **The delayed-message exchange plugin**, for delayed retries: [delivery.md](delivery.md) section 5.

## 15. Security

This section covers four threats: someone who reads or changes the traffic between the service and the broker, a default or shared broker account, a leaked credential that can do more than its service needs, and message bodies stored in SQS. It leaves out hardening the broker server, since running the broker is out of scope. Personal data and secrets inside messages are [delivery.md](delivery.md) section 10.

- **Connect over TLS 1.2 or later, and verify the broker's certificate.** RabbitMQ's TLS guide says to "limit supported TLS versions to 1.2 and later versions only, if possible", and "Peer verification is highly recommended in production environments" [43]. In Python, `ssl.create_default_context()` builds a client context that requires the server's certificate and checks its host name [44], and aio-pika takes it as `ssl_context` with `ssl=True` [30]. The connection in section 5 does both. Why every broker connection uses TLS is [delivery.md](delivery.md) section 10.
- **Pass the user and the password on every connect.** aio-pika uses `guest` when the code passes no login [30], so pass both from the settings class, the password as a `SecretStr` ([python.md](../language/python.md) section 5). A user of its own for each application, and no `guest`, is [delivery.md](delivery.md) section 10.
- **Grant each user only its virtual host, and only the names it uses.** RabbitMQ's table names what each operation needs: publishing needs write on the exchange, consuming needs read on the queue, and declaring needs configure [41].
- **On a topic exchange that several producers share, give each producer user topic permissions whose write pattern matches only its own routing keys,** such as `^orders\.` for the orders service. Why: with RabbitMQ's default authorisation backend, "publishing to a topic exchange or consuming from a topic is always authorised if no topic permissions are defined (which is the case on a fresh RabbitMQ installation)" [41]. A leaked producer credential with write on `acme.events` could then publish any event the other services act on. With topic permissions, the routing key "is matched against a regular expression" before the message is routed [41].
- **On SQS, never write a queue policy whose Principal is `*`; name the principal that may send.** AWS: "Avoid using a wildcard (`*`). Instead, name a specific user or users" [45]. Least privilege for producers and consumers, IAM roles and the TLS condition are [delivery.md](delivery.md) section 10.
- SQS encryption at rest, and what it leaves unencrypted, are [delivery.md](delivery.md) section 10.
- A message body never goes into a log line ([logging.md](../logging/logging.md) section 10).

## 16. Checks

- `grep -rnE "no_ack=True|auto_ack=True" src/` prints nothing (section 9).
- `grep -rnE "set_qos|basic_qos" src/` shows one line for each consumer's channel, and none of them passes `prefetch_count=0` or a global flag (section 9).
- `grep -rnE "[\"']guest[\"']" src/` prints nothing: no `guest` login in the code (section 15).
- At review, for each queue the code declares: does it pass `"x-queue-type": "quorum"` and `durable=True` (section 7)?
- At review, for each queue the code declares: does it have a dead-letter target and a written delivery limit, in its arguments or in a policy the change ships ([delivery.md](delivery.md) section 6)?
- At review, for each producer user on a shared topic exchange: do its topic permissions let it write only its own routing keys (section 15)?
- Tests: a unit test hands the code a fake publisher that records what it was given ([fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 3); an integration test runs a real RabbitMQ in testcontainers ([libraries.md](../testing/libraries.md) section 2).

## 17. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] RabbitMQ — Quorum Queues, docs version 4.4 — https://www.rabbitmq.com/docs/quorum-queues
- [2] Jepsen — Analyses — https://jepsen.io/analyses
- [3] Redis — redis (repository README, branch `unstable`) — https://github.com/redis/redis
- [4] Redis — Redis Pub/sub — https://redis.io/docs/latest/develop/pubsub/
- [5] RabbitMQ — RabbitMQ: One broker to queue them all (home page) — https://www.rabbitmq.com/
- [6] Bobby Woolf — Point-to-Point Channel (Enterprise Integration Patterns, 2003; opinion) — https://www.enterpriseintegrationpatterns.com/patterns/messaging/PointToPointChannel.html
- [7] RabbitMQ — Streams and Superstreams (Partitioned Streams), docs version 4.4 — https://www.rabbitmq.com/docs/streams
- [8] Apache Kafka — Introduction — https://kafka.apache.org/intro
- [9] AWS — Choosing an AWS application integration service (AWS Decision Guides) — https://docs.aws.amazon.com/decision-guides/latest/application-integration-on-aws-how-to-choose/application-integration-on-aws-how-to-choose.html
- [10] AWS — What is Amazon Simple Queue Service? (Amazon SQS Developer Guide) — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html
- [11] RabbitMQ — Clients Libraries and Developer Tools — https://www.rabbitmq.com/client-libraries/devtools
- [12] RabbitMQ — `COMMUNITY_SUPPORT.md` (rabbitmq-server, branch `main`) — https://github.com/rabbitmq/rabbitmq-server/blob/main/COMMUNITY_SUPPORT.md
- [13] RabbitMQ — Release Information — https://www.rabbitmq.com/docs/versions
- [14] RabbitMQ — RabbitMQ 4.4 Highlights (blog), 4.4 — https://www.rabbitmq.com/blog/2026/10/20/rabbitmq-4.4-release
- [15] AWS — Amazon SQS standard queues (Amazon SQS Developer Guide) — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html
- [16] AWS — Troubleshoot FIFO throttling issues in Amazon SQS (Amazon SQS Developer Guide) — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/troubleshooting-fifo-throttling-issues.html
- [17] aio-pika — aio-pika (PyPI JSON metadata), 10.2.1 — https://pypi.org/pypi/aio-pika/json
- [18] pika — Releases (GitHub) — https://github.com/pika/pika/releases
- [19] pika — Release notes, 1.5.0rc1 — https://github.com/pika/pika/releases/tag/1.5.0rc1
- [20] AWS — Boto3 documentation: A Sample Tutorial (Amazon SQS), 1.43.122 — https://docs.aws.amazon.com/boto3/latest/guide/sqs.html
- [21] AWS — Boto3 documentation: Using dead-letter queues in Amazon SQS, 1.43.122 — https://docs.aws.amazon.com/boto3/latest/guide/sqs-example-dead-letter-queue.html
- [22] Kyle Kingsbury — Jepsen: NATS 2.12.1 (Jepsen, 2025; research) — https://jepsen.io/analyses/nats-2.12.1
- [23] RabbitMQ — rabbitmq-amqp-python-client (repository README) — https://github.com/rabbitmq/rabbitmq-amqp-python-client
- [24] Gsantomaggio — RabbitMQ AMQP 1.0 client Version 2.0 (GitHub Discussions, rabbitmq-amqp-python-client, 2026; opinion) — https://github.com/rabbitmq/rabbitmq-amqp-python-client/discussions/123
- [25] RabbitMQ — Channels, docs version 4.4 — https://www.rabbitmq.com/docs/channels
- [26] RabbitMQ — Connections, docs version 4.4 — https://www.rabbitmq.com/docs/connections
- [27] RabbitMQ — Publishers, docs version 4.4 — https://www.rabbitmq.com/docs/publishers
- [28] aio-pika — Quick start — https://docs.aio-pika.com/quick-start.html
- [29] pika — FAQ — https://pika.github.io/pika/latest/faq/
- [30] aio-pika — API Reference — https://docs.aio-pika.com/apidoc.html — checked 2026-10-30
- [31] RabbitMQ — RabbitMQ tutorial: Publish/Subscribe (Python) — https://www.rabbitmq.com/tutorials/tutorial-three-python
- [32] aio-pika — RabbitMQ tutorial: Publish/Subscribe — https://docs.aio-pika.com/rabbitmq-tutorial/3-publish-subscribe.html — checked 2026-10-30
- [33] RabbitMQ — Migrating from Classic Mirrored Queues to Quorum Queues in 2025 (blog) — https://www.rabbitmq.com/blog/2025/07/29/latest-benefits-of-rmq-and-migrating-to-qq-along-the-way
- [34] RabbitMQ — Consumer Acknowledgements and Publisher Confirms, docs version 4.4 — https://www.rabbitmq.com/docs/confirms
- [35] pika — Connection adapters: Blocking (API reference) — https://pika.github.io/pika/latest/modules/adapters/blocking/ — checked 2026-10-30
- [36] aio-pika — `aio_pika/message.py`, 10.2.1 — https://github.com/mosquito/aio-pika/blob/10.2.1/aio_pika/message.py
- [37] RabbitMQ — Consumers, docs version 4.4 — https://www.rabbitmq.com/docs/consumers
- [38] RabbitMQ — Consumer Prefetch, docs version 4.4 — https://www.rabbitmq.com/docs/consumer-prefetch
- [39] aio-pika — `aio_pika/channel.py`, 10.2.1 — https://github.com/mosquito/aio-pika/blob/10.2.1/aio_pika/channel.py
- [40] AWS — Amazon SQS visibility timeout (Amazon SQS Developer Guide) — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html
- [41] RabbitMQ — Authentication, Authorisation, Access Control, docs version 4.4 — https://www.rabbitmq.com/docs/access-control
- [43] RabbitMQ — TLS Support, docs version 4.4 — https://www.rabbitmq.com/docs/ssl
- [44] Python — `ssl`: TLS/SSL wrapper for socket objects, Python 3.15.2 — https://docs.python.org/3/library/ssl.html — checked 2026-10-30
- [45] AWS — Amazon SQS security best practices (Amazon SQS Developer Guide) — https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-security-best-practices.html
- [47] RabbitMQ — RabbitMQ tutorial: Topics (Python) — https://www.rabbitmq.com/tutorials/tutorial-five-python — checked 2026-10-30
- [48] aio-pika — `aio_pika/exchange.py` (`Exchange.publish`), 10.2.1 — https://github.com/mosquito/aio-pika/blob/10.2.1/aio_pika/exchange.py
- [49] aiormq — `aiormq/exceptions.py`, 7.2.4 — https://github.com/mosquito/aiormq/blob/7.2.4/aiormq/exceptions.py
- [50] aiormq — `aiormq/channel.py`, 7.2.4 — https://github.com/mosquito/aiormq/blob/7.2.4/aiormq/channel.py
- [51] GitHub — aio-pika contributors (REST API) — https://api.github.com/repos/mosquito/aio-pika/contributors — checked 2026-10-30
