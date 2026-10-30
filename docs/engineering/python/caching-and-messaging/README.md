# Caching and messaging

How Python code works with a cache, a task queue, a message broker, an event stream, a
durable-workflow engine or a scheduler, so that it stays correct when a message arrives twice, late
or out of order; and when each of these tools is more than a service needs.

**Navigation**

- [The one rule](#the-one-rule)
- [Which job is yours](#which-job-is-yours)
- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)

## The one rule

**Every message can arrive twice, late or out of order, so write every consumer so that a second
run changes nothing, and send only what the database committed. Add a tool only when the simpler
way no longer does the job.**

[delivery.md](delivery.md) section 2 shows why the first part holds for every tool here: none of
them promises to run a consumer's work exactly once, and each exactly-once setting stops at the edge of its
tool, while the work a consumer does in its own database lies outside that edge. A cache meets the
same rule from the other side: any copy can be gone or old at any moment, so the data store keeps
the truth ([caching.md](caching.md) section 1). The second part is why each job file says what the
simpler way is before its first rule. Each file below holds the rule for one job and its tools.

## Which job is yours

Pick the file by the job the code does, not by the product: Redis, RabbitMQ and Kafka can each pass
a message from one service to another, and each fits a different job
([message-brokers.md](message-brokers.md) section 2). Read every job file except caching.md together
with [delivery.md](delivery.md), which holds the rules they share.

| Job | You have it when | Read | The simpler way |
|---|---|---|---|
| A cache | An answer costs time to get again, such as a slow query or a call to another service, and its reader may see a copy that is a little old | [caching.md](caching.md) | Section 2: memory inside the process |
| Background tasks | The application hands work to run after the response or in a worker: a receipt, a search entry, a slow API call | [task-queues.md](task-queues.md) | Section 2: the framework's background tasks, or a queue in the PostgreSQL the service already has |
| Messages between services | Another service must get each message: one consumer per message, or one copy for each subscriber | [message-brokers.md](message-brokers.md) | Section 3: a task queue when one application both sends and does the work, or the managed queue of the cloud in use |
| An event stream | Several services read the same events and may read them again, or the events of one key must stay in order at high throughput | [event-streaming.md](event-streaming.md) | Section 2: a queue when nobody reads a message again |
| A durable workflow | Work of several dependent steps, each with an effect in another system, must go on from where it stopped after a crash, or waits for days | [durable-workflows.md](durable-workflows.md) | Section 2: a task queue with retries when one database transaction can hold the whole job |
| A scheduled job | Code must run at set times, such as a nightly report or a cleanup | [scheduled-jobs.md](scheduled-jobs.md) | Section 1: APScheduler inside the service's one process |

A service may need none of these tools yet. Each job file names the simpler way, and the signs that
it no longer does the job, before its first rule: start there.

Left out on purpose: running the servers (clustering, upgrades, capacity), data pipeline
orchestration such as Airflow, Dagster or Prefect, brokers built around Java's JMS, and MQTT.

## What is here

- [delivery.md](delivery.md) — the rules every job except caching shares: why a message can arrive
  twice, late or out of order, idempotent consumers, the outbox and its relay, retries and delayed
  retries, dead-letter queues, ordering, message contracts, tracing and ids across a message, and
  security and personal data in messages. Read it together with your job file, before you write a
  producer, a consumer, a relay or a retry.
- [caching.md](caching.md) — an in-process cache first, then Valkey or Redis: cache-aside, expiry,
  many requests rebuilding one key, what goes into the cache, an instance of its own and its
  eviction policy, the client, timeouts and retries, and a cache that is down. Read it before you
  add a cache, change what it holds or for how long, or build the client of a shared cache.
- [task-queues.md](task-queues.md) — when the framework's background tasks or a PostgreSQL queue is
  enough, Celery or Dramatiq, enqueuing only what committed, acknowledging after the work, long
  tasks, arguments, results and retries, and the settings you set. Read it before you add a
  background task, a task queue or a worker.
- [message-brokers.md](message-brokers.md) — RabbitMQ through aio-pika or pika, and a managed cloud
  queue with Amazon SQS as the example: when a service needs no broker of its own, connections and
  channels, fan-out, quorum queues, publishing with confirms, consuming with manual
  acknowledgements, and the limits of SQS. Read it before you write code that publishes to a broker
  or consumes from one.
- [event-streaming.md](event-streaming.md) — Kafka through confluent-kafka: when a service needs an
  event stream, the producer's durable settings, keys and order, storing the offset after the work,
  rebalances, consumer lag and schemas. Read it before you write a Kafka producer or consumer.
- [durable-workflows.md](durable-workflows.md) — Temporal or DBOS: when an engine is too much,
  deterministic workflow code, steps that are safe to run twice, retries set where a step is called,
  and changing workflow code that is running. Read it before you add an engine, or write a workflow
  or a step.
- [scheduled-jobs.md](scheduled-jobs.md) — Celery beat, Procrastinate's periodic tasks or a
  Kubernetes CronJob: one scheduler per schedule, a job that is safe to run twice, time zones, missed
  and late runs, and a run still going when the next one is due. Read it before you add or change a
  scheduled job.
- [consumer-example.md](consumer-example.md) — one RabbitMQ consumer that charges an order once per
  event: it records the message id in the same transaction as the charge and acknowledges the
  message after the commit. Read it when you write a service's first consumer.
- [outbox-relay-example.md](outbox-relay-example.md) — an order and its outbox row written in one
  transaction, and the relay that publishes each row with publisher confirms and deletes it after
  the confirm. Read it when you write an outbox and its relay.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/python/caching-and-messaging/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you add or change a cache, a background
   task, a task queue, a message producer or consumer, a broker, queue or stream client, an outbox
   or its relay, a durable workflow or a scheduled job in a Python service, read
   `docs/engineering/python/caching-and-messaging/README.md` and the file it routes to for that
   work." Without it an agent never opens the folder.
3. The rules link the practices that own a nearby rule: [python.md](../language/python.md) sections
   2 to 5 and [settings-example.md](../language/settings-example.md) (values written in the code,
   closed sets, a message parsed into a model at the edge, credentials in the settings class),
   [logging.md](../logging/logging.md) sections 4, 5, 7, 8, 10 and 12 (the level of a retry, one
   line where an error is handled, the request id a worker does not have, the root span of a
   worker's job, what never goes into a log, an OpenTelemetry instrumentation in the same
   process),
   [fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 3 and
   [libraries.md](../testing/libraries.md) section 2 (a fake that records what was sent, a real
   broker or cache in testcontainers),
   [file-structure.md](../../any-language/file-structure/file-structure.md) sections 3 to 5 (a
   module's files, one client per outside system, one adapter folder per way in),
   [readability.md](../../any-language/readability/readability.md) section 6 (every input in the
   signature),
   [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
   section 2 (the session store, and the lock around a token refresh), and
   [ci-cd/pipeline.md](../../any-language/ci-cd/pipeline.md) section 4 (a scheduled CI workflow).
   Copy those practices too, or point each link at the rule your project follows instead.
4. Existing code takes two of the answers in
   [refactoring.md](../../any-language/refactoring/refactoring.md) section 7. Most rules reach old
   code when a change touches it, as section 2 of that file describes. Four groups exist because
   the old way loses work, repeats it, leaks data or lets someone run code, so they reach all code
   by a date, as its section 6 says: a consumer that acknowledges before its work commits
   ([delivery.md](delivery.md) section 3), unless [delivery.md](delivery.md) section 12's case
   applies; a message whose loss does harm, sent from inside a transaction or after it with no
   outbox row ([delivery.md](delivery.md) section 4,
   [task-queues.md](task-queues.md) section 4); a broker connection without TLS, a credential
   shared between applications, a Kafka cluster with `allow.everyone.if.no.acl.found` on, or a
   message body in a log line ([delivery.md](delivery.md) section 10), an SQS queue policy whose
   Principal is `*`, or a producer user with no topic permissions on a shared topic exchange
   ([message-brokers.md](message-brokers.md) section 15), or a Temporal client without TLS
   ([durable-workflows.md](durable-workflows.md) section 13); and a cached value or a task message
   decoded with pickle ([caching.md](caching.md) section 6, [task-queues.md](task-queues.md)
   section 12), an APScheduler job table that more than the scheduler may write
   ([scheduled-jobs.md](scheduled-jobs.md) section 13), a DBOS system database that more than the
   DBOS application may write ([durable-workflows.md](durable-workflows.md) section 13), or a
   cache client, or a task queue's broker client on Redis or Valkey, without TLS or an ACL user
   ([caching.md](caching.md) section 14, [task-queues.md](task-queues.md) section 12).

## The points to adapt

The shape stays: every consumer is safe to run twice, what must not be lost goes out through an
outbox row or a job written in the same transaction, and a tool comes in only when the simpler way
stops doing the job. Within that shape, these are your choices.

- **The tool for each job.** Each job file names at most two picks beside the simpler way, with
  its reasons; in scheduled-jobs.md the task queue's own scheduler is one pick, whichever queue the
  service runs: [caching.md](caching.md) section 2 (Valkey for a new shared cache and Redis where it
  already runs; against Valkey, valkey-py in new code and redis-py where the code already uses it),
  [task-queues.md](task-queues.md) section 3, [message-brokers.md](message-brokers.md) section 4,
  [event-streaming.md](event-streaming.md) section 3, [durable-workflows.md](durable-workflows.md)
  section 3 and [scheduled-jobs.md](scheduled-jobs.md) section 2. A team on another broker or
  another cloud keeps [delivery.md](delivery.md) and writes its own tool parts.
- **The versions named.** Each file names the versions it was read against next to the rules that
  rest on them, and its Sources section opens with its `Checked` date
  (`grep -rn '^Checked ' docs/engineering/python/caching-and-messaging/`). Some rules say "not yet"
  and change when a release lands: confluent-kafka's share consumer and Kafka transactions
  ([event-streaming.md](event-streaming.md) section 3); pika 1.5.0, RabbitMQ's AMQP 1.0 Python
  client and the support window of each RabbitMQ series ([message-brokers.md](message-brokers.md)
  section 4); `async def` tasks in Celery ([task-queues.md](task-queues.md) section 3); and
  APScheduler 4.0 ([scheduled-jobs.md](scheduled-jobs.md) section 2). Re-check them when you copy
  the folder.
- **The names in the examples.** The package `acme`, its paths under `src/acme/` and the event and
  exchange names are placeholders: use your own. The `outbox` table uses the column names
  Debezium's outbox router reads by default; a table with other names works with log tailing when
  the router's `table.field.event.*` and `route.by.field` options name them
  ([delivery.md](delivery.md) section 4).
- **The values the files leave to you.** How long to keep the ids of processed messages
  ([delivery.md](delivery.md) section 3 gives its reasoning, not a rule), the expiry of each cached
  value ([caching.md](caching.md) section 4), and the answer to a late or an overlapping scheduled
  run ([scheduled-jobs.md](scheduled-jobs.md) sections 6 and 7).
