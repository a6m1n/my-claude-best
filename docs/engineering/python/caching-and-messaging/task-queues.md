# Task queues

How Python code hands work to a background worker so that the work runs once in effect, and when a
service needs no task queue yet.

**Navigation**

- [1. Purpose and scope](#1-purpose-and-scope)
- [2. When you need no task queue yet](#2-when-you-need-no-task-queue-yet)
- [3. Which tool](#3-which-tool)
- [4. Enqueue only what committed](#4-enqueue-only-what-committed)
- [5. Acknowledge after the work, and plan for a dead worker](#5-acknowledge-after-the-work-and-plan-for-a-dead-worker)
- [6. Long tasks: prefetch, time limits and the Redis visibility timeout](#6-long-tasks-prefetch-time-limits-and-the-redis-visibility-timeout)
- [7. Arguments, results and retries](#7-arguments-results-and-retries)
- [8. Settings you set](#8-settings-you-set)
- [9. Common mistakes](#9-common-mistakes)
- [10. Where the rules stop holding](#10-where-the-rules-stop-holding)
- [11. Alternatives considered](#11-alternatives-considered)
- [12. Security and personal data](#12-security-and-personal-data)
- [13. Checks](#13-checks)
- [14. Sources](#14-sources)

## 1. Purpose and scope

This file is for anyone, a person or an agent, who writes code that hands work to a background
worker: rebuild a search entry, send a receipt, call a slow API after the response has gone out.
It covers how to pick a task queue, how to enqueue a task, how the worker takes it, and the
settings a programmer writes. Running the broker is [message-brokers.md](message-brokers.md). A
schedule that starts a task is [scheduled-jobs.md](scheduled-jobs.md). Work of many dependent
steps that must resume where it stopped is [durable-workflows.md](durable-workflows.md). The rules
every message shares, such as duplicates, idempotent consumers, the outbox, retries and dead
letters, are in [delivery.md](delivery.md), and this file links them.

The one rule: **enqueue a task only for data that committed, acknowledge it only after the work is
done unless [delivery.md](delivery.md) section 12's case applies, and write it so that a second
run changes nothing.**

Why it matters:

- A worker can start a task before the transaction that asked for it commits, and then it finds no
  data. A task sent from a transaction that later rolls back fails on every retry [1].
- Celery acknowledges a task just before it runs, by default, so a worker that dies in the middle
  loses the task. With late acknowledgement the task runs again, and then it must be
  idempotent [2].

Versions checked: Celery 5.6.3 [3], Dramatiq 2.2.1 with its 2.2.0 docs [4], and
Procrastinate 3.10.0 [5].

Not covered yet, because the research found no source that settles it:

- a neutral throughput at which a PostgreSQL queue stops being enough (section 2 gives the
  measured cases, each from one author or a vendor);
- whether PostgreSQL 19 removes the database-wide lock that `NOTIFY` takes at commit (section 2);
- how Dramatiq's time limit reaches an `async def` actor (section 6);
- how a Dramatiq actor reaches the clients its worker builds (section 7);
- how many teams use each tool: the surveys do not ask, and downloads include CI runs
  (section 3).

## 2. When you need no task queue yet

A task queue brings a broker or a queue table, a worker process to deploy and watch, and the
delivery rules of [delivery.md](delivery.md). Start with the simplest way that keeps the work
safe enough for what a lost task costs.

| What you need | The simpler way | Move on when |
|---|---|---|
| A short job after the response, such as one email | The web framework's background tasks | The work is heavy, must run in another process or server, or must survive a restart |
| Jobs that survive a restart, in a service that already has PostgreSQL | A queue in that PostgreSQL | The signs at the end of this section appear |

**The framework's background tasks.** FastAPI runs a background task "after returning a
response" [6]. Its page says that for heavy work you do not need "to be run by the same
process", "you might benefit from using other bigger tools like Celery", which run tasks "in
multiple processes, and especially, in multiple servers", and that for small tasks you "can
simply just use BackgroundTasks" [6]. Use them only where a lost task is cheap: the task lives in
the web process, so nothing runs it again if that process stops first.

**Django's `django.tasks`.** Django 6.0 adds a standard interface for tasks, not a queue: "It does
not provide a worker mechanism to run Tasks", and "Django comes with built-in backends, but these
are for development and testing only" [7]. Django says that "Production systems should rely
on backends that supply a worker process and a durable queue implementation" [7]. Write the
tasks against `django.tasks`, pick a backend that has a worker, and apply the rules below to that
backend.

**A queue in the PostgreSQL you already have.** When jobs must survive a restart and the service
already runs PostgreSQL, a queue table there needs no second system. Brandur Leach, who wrote the
PostgreSQL job queue River, lists what goes wrong when the queue sits outside the database: a job
sent from a transaction that rolls back fails on every retry, and a job sent after the commit is
lost if the process dies in "a brief moment between the commit and job emit" [1]. A job row
written in the same transaction as the data avoids both (section 4). Richard Yen holds that "At
small scale, using Postgres as a job queue is totally fine" [8].

Procrastinate is the PostgreSQL queue this practice describes. Version 3.10.0 uses "PostgreSQL 13+
to store task definitions, manage locks and dispatch tasks", and "It can be used within both sync
and async code" [5]. It had 1.9 million downloads in the month to 29 October 2026,
against 34,000 for pgmq [9], [10]. Its README says "Procrastinate is looking for
additional maintainers!" [11], so check the project's recent releases before you depend
on it.

**Where a PostgreSQL queue stops being enough.** No neutral threshold was found. Watch the
database for these signs:

- **Dead rows pile up.** A queue table updates and deletes rows all the time. Richard Yen
  describes the pattern: "Dead tuples accumulate faster than autovacuum can clean them" [8].
  His post first appeared on Microsoft's blog, and Microsoft sells a managed PostgreSQL.
- **Long queries share the database.** In PlanetScale's benchmark, "3 concurrent analytics workers
  running 120-second queries, staggered so they overlap continuously" kept vacuum from cleaning
  the queue table, and the queue fell into "a quietly degraded equilibrium where lock times creep
  up, jobs slow down, and no alert fires" [12]. PlanetScale sells PostgreSQL, and the
  post presents its own product as the fix.
- **Throughput grows.** The numbers found come from one author or a vendor. Stanislav Kozlovski
  measured 2,885 messages a second on 4 vCPUs (two 15-minute runs) and 20,144 on 96 vCPUs
  (three 2-minute runs, with a bottleneck he did not trace); he calls himself "biased towards
  Kafka" [13].
  A co-founder of Hatchet, which sells a platform built on PostgreSQL, writes that at bursts "to
  over 5k tasks/second", "a simple Postgres queue utilizing FOR UPDATE SKIP LOCKED doesn't cut it
  at this scale" [14].
- **Commits wait on `NOTIFY`.** Recall.ai found in production that "When a NOTIFY query is issued
  during a transaction, it acquires a global lock on the entire database" [15]. Its post now
  says that a PostgreSQL commit "has eliminated the bottleneck in the postgres core" [15]. The
  commit itself describes waking only the backends that listen for a notification, and does not
  mention the lock at commit [16], so this practice treats the fix as unconfirmed.
  Procrastinate's workers listen for notifications by default and poll the database in any case;
  `listen_notify=False` makes them rely on polling alone [17], [18]. Its docs do not
  say whether a defer still sends `NOTIFY` when no worker listens.

**When the signs appear, tune the database and stay on PostgreSQL first.** At Hatchet, the
co-founder quoted above writes, the team "doubled down on Postgres, and spent about 6 months
learning how to operate Postgres databases at scale" instead of moving off it, and then announced
"a full rewrite of the Hatchet engine — still built on Postgres" [14]. Its reasons are tied to its
product: to make Hatchet "as portable and easy to administer as possible", and because PostgreSQL
"is also what allows us to offer a general-purpose orchestration platform" [14]. Why first for
an application team: a job row written in the same transaction as its data does the outbox's work
with no relay ([delivery.md](delivery.md) section 4). A move to a tool of section 3 loses that, so
every job that must not be lost then needs an outbox row and a relay. Move to section 3 when
tuning no longer keeps the signs away, or when tuning needs database skills the team does not
have, because the move costs one outbox table and one relay ([delivery.md](delivery.md) section
4); add the outbox in the same change.

## 3. Which tool

Two task queues are described here, beside the PostgreSQL queue of section 2.

| Tool (Python client) | Use it when | Too much, or the risk |
|---|---|---|
| Celery, with RabbitMQ as the broker | The tasks are plain functions (`def`). It has the most downloads: 43.2 million in the month to 29 October 2026, CI runs included [19]. FastAPI's page names it as the bigger tool [6], and Celery calls RabbitMQ "an excellent choice for a production environment" [20]. | No native `async def` tasks: the request has been open since 2020 and is marked "Design Decision Needed" [21], and an asyncio pool is a draft pull request aimed at 5.8.0 [22]. "Celery 5.x is not an LTS release" [23]. 5.7.0rc1 is a release candidate; PyPI's current release is 5.6.3 [3]. |
| Dramatiq, with RabbitMQ as the broker | The tasks are `async def`: Dramatiq runs them through its AsyncIO middleware [24]. It acknowledges a message only after the actor succeeds [25], and it had four releases from November 2025 to June 2026 [26]. | Far fewer downloads: 1.6 million in the same month [27]. A report of duplicated delayed messages, filed in 2021 on the Redis broker, is still open [28], which is one reason to run it on RabbitMQ. An `async def` actor still holds a worker thread while it runs, so a worker process handles at most as many messages at a time as it has threads, 8 by default [24]. |

**Celery: the default, and the signs that it is time to leave.** Keep Celery for task code
written as plain functions. Its lead there is the ecosystem: Celery beat, its own scheduler
([scheduled-jobs.md](scheduled-jobs.md) section 2), and `delay_on_commit()` in Django (section
4), where Dramatiq's Cookbook sends its users to APScheduler for schedules and to the
django_dramatiq project for Django [24]; and the downloads above, CI runs included, and FastAPI's
pointer to it. Dramatiq runs plain `def` actors too [48], so a service with both `def` and
`async def` tasks runs them all on Dramatiq, since one task queue is less to run than two. A
service that moves to Dramatiq adds APScheduler for its schedules.

Do not start with Celery when the tasks are `async def`: Celery 5.6.3 does not run them
(section 9), and Dramatiq does.

If you already run Celery, plan to move when one of these is true:

- **`async def` tasks arrive.** Celery 5.6.3 does not run them (section 9); move the tasks to
  Dramatiq. The workaround, `asyncio.run()` inside a `def` task, has to manage its own event
  loop: comments on Celery's request report thread errors with it, and say it "does NOT work with
  `gevent` workers" [21], while Dramatiq starts "1 thread per worker process to run an event
  loop" for its async actors [24].
- **The work is many dependent steps that must resume where they stopped.** Two teams moved such
  pipelines off Celery. Dosu moved to DBOS when it was ingesting "hundreds of thousands of
  documents per day", in a post written as a case study with DBOS [29]. AmpUp moved to
  Inngest; its co-founder writes that "Celery has no concept of durable execution: if a worker
  process dies mid-task, that unit of work is gone unless you built your own idempotency
  layer" [30], and AmpUp runs on Inngest Cloud [30]. Both posts come from teams tied to
  the tool they moved to, so read them as cases. When one transaction cannot hold the job,
  [durable-workflows.md](durable-workflows.md) section 2 applies.
- **A long-open bug hits you.** "Long tasks are executed multiple times", on RabbitMQ, has been
  open since 2016, and its first reply asks whether `acks_late` was on [31]. "Continuous
  memory leak" has been open since 2018 [32]. Both now carry the 5.8.0 milestone [31],
  [32]. When one of them hits your tasks and 5.8.0 has not fixed it, move those tasks to
  Dramatiq.

Celery's README mentions "minimal funding" in the sentence that explains why it does not support
Windows [33]; it says nothing there about the project's health in general.

**When Redis or Valkey is enough as the broker.** Celery says Redis is "more susceptible to data
loss in the event of abrupt termination or power failures" [20]. With Redis snapshots alone
"you should be prepared to lose the latest minutes of data", and with the append-only file at its
default fsync every second "you can only lose one second worth of writes" [34]. Use
Redis as the broker only when a few tasks lost in a Redis crash cost little and no countdown or
ETA runs past the visibility timeout (section 6). Otherwise use RabbitMQ.

**Named, not described:**

- **RQ.** 9.2 million downloads in the same month [35], but "RQ requires Redis >= 5 or
  Valkey >= 7.2" [36], so it carries the Redis limits above.
- **Taskiq.** A "Distributed task queue with full async support" [37], with more downloads
  than Dramatiq: 2.1 million against 1.6 million in the same month [38], [27].
  Counted without mirrors, it grew from 1.2 million in May 2026 to 2.1 million in
  September [39]. It is at 0.13.0 with the PyPI status "3 - Alpha", and PyPI names one
  person as its author and maintainer [37]. Not described while it is before 1.0 with one
  maintainer.
- **pgmq.** A "Python client for the PGMQ Postgres extension" [40], with no worker
  framework: you would write the worker yourself.
- **arq.** In maintenance-only mode; its author writes "don't expect work on new fixes" [41].

## 4. Enqueue only what committed

- **On a queue outside the database, enqueue a task after the transaction that wrote its data
  commits, never inside it.** A worker can take the task before the commit and find no data, and
  a task from a transaction that rolls back fails on every retry [1]. Celery's docs show the same race in a Django view: "There is
  a race condition because transactions are atomic" [2].
- **With Django, call `delay_on_commit()` instead of `delay()`.** Celery added it in 5.4, and it
  uses Django's `on_commit` callback to send the task once the transaction has committed
  [2]. With `django.tasks`, wrap the call in `transaction.on_commit()` and bind its
  arguments with `functools.partial()` [7].
- **Outside Django, send after `commit()` returns, and decide whether the gap matters.** Sending
  after the commit leaves "a brief moment between the commit and job emit where if the process
  crashes or there's a bug, the job is gone" [1]. When a lost task is cheap, such as a cache
  warm-up or a report someone can run again, stop here. When it is not, write the job in the same
  transaction: a PostgreSQL queue (next rule) or an outbox row that a relay sends
  ([delivery.md](delivery.md) section 4).
- **With Procrastinate, defer on the transaction's own connection** ([delivery.md](delivery.md)
  section 4); the client below does it.

A client in `core/` that defers a job inside the caller's transaction,
`src/acme/core/jobs_client.py`. `TaskName`, the closed set of task names, is in
`src/acme/core/schemas.py`. The worker's task and the use case that calls the client are left
out:

```python
from procrastinate import App
from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from pydantic import BaseModel

from acme.core.schemas import TaskName


class JobsClient:
    def __init__(self, app: App) -> None:
        self._app = app

    async def defer(
        self, conn: AsyncConnection[TupleRow], task: TaskName, arguments: BaseModel
    ) -> None:
        # By task name, so core/ imports no worker code (file-structure.md section 2).
        deferrer = self._app.configure_task(task, connection=conn)
        # On the caller's connection: the job row commits or rolls back with its data.
        await deferrer.defer_async(**arguments.model_dump(mode="json"))
```

It is good because the job row is written in the transaction that writes the order: the use case
writes the order on `conn`, calls
`jobs.defer(conn, TaskName.REINDEX_ORDER, ReindexOrder(order_id=order.order_id))` and commits
once, so neither row exists without the other. `configure_task` takes a task by its name and
passes on the options of `Task.configure`, `connection` among them [17]. The queue has one client
in `core/`, built at startup and passed in
([file-structure.md](../../any-language/file-structure/file-structure.md) section 4). It holds no
method and no constant of one module: the task comes from `TaskName`, which sits in
`core/schemas.py` because a `core/` file names it, and the arguments come as `ReindexOrder`, which
sits there too because two modules use it, the one that sends the task and `reindex_order`, which
runs it ([file-structure.md](../../any-language/file-structure/file-structure.md) section 4).
`TupleRow` is psycopg's type for its default rows [43].

## 5. Acknowledge after the work, and plan for a dead worker

- **Celery: set `task_acks_late=True` for a task that is idempotent.** By default Celery
  acknowledges a message "just before it's executed, so that a task invocation that already
  started is never executed again" [2]. A worker killed in the middle then loses the task:
  the workers guide warns that on `KILL` "currently executing tasks will be lost" unless they set
  `acks_late` [44]. With late acknowledgement, "the task may be executed multiple times
  should the worker crash in the middle of execution. Make sure your tasks are idempotent" [2].
  What makes a task idempotent is [delivery.md](delivery.md) section 3.
- **Know the case late acknowledgement does not cover.** "Even if task_acks_late is enabled, the
  worker will acknowledge tasks when the worker process executing them abruptly exits or is
  signaled (e.g., KILL/INT, etc)" [45]. `task_reject_on_worker_lost=True` puts such a task
  back on the queue instead, and Celery warns: "Enabling this can cause message loops; make sure
  you know what you're doing" [45]. A task that kills its worker process every time, for
  example by running out of memory, would then run forever. Leave the setting off unless the
  queue moves a message to a dead-letter queue after a set number of deliveries
  ([delivery.md](delivery.md) section 6).
- **A failure or a timeout is acknowledged too.** With `task_acks_on_failure_or_timeout` at its
  default, "messages for all tasks will be acknowledged even if they fail or time out" [45].
  Late acknowledgement does not retry a task that failed; the task's retry options do (section 7).
- **Stop a Celery worker with `TERM`, and give it time.** "When shutdown is initiated the worker
  will finish all currently executing tasks before it actually terminates" [44]. Let the
  deploy wait at least as long as the longest task before it sends `KILL`.
- **Dramatiq acknowledges after success, always.** "Messages are only ever acknowledged to
  (removed from) the broker after they have been successfully processed" [25]. There is
  no switch for it. A message that fails for good is negatively acknowledged into the dead-letter
  queue [46], [47]. Dramatiq "assumes all actors are idempotent" [48], so every
  actor follows [delivery.md](delivery.md) section 3.
- **With Dramatiq, the broker decides when a dead worker's messages come back.** The docs say that
  messages in flight when a worker is terminated "are going to be redelivered later" [25].
  On RabbitMQ the broker puts a consumer's unacknowledged messages back when its connection
  drops [47]. On Redis a maintenance pass, run on a share of broker calls, moves them back
  once the worker has sent no heartbeat for 60 seconds [49], [50]. How long a dead letter is kept
  is [delivery.md](delivery.md) section 6. On a graceful shutdown, messages that were "pulled by
  workers but not processed are returned to the broker" [25].
- **With Procrastinate, add the task that retries stalled jobs in the same change as the worker.**
  A worker killed with `SIGKILL`, or stopped by a second `SIGTERM`, can leave jobs in the `doing`
  state, and "these stalled jobs will remain in the queue forever" [51]. The rule and
  its settings are [scheduled-jobs.md](scheduled-jobs.md) section 8.

## 6. Long tasks: prefetch, time limits and the Redis visibility timeout

- **With long Celery tasks, set `worker_prefetch_multiplier=1` together with
  `task_acks_late=True`.** The default multiplier is 4, and with long tasks "the first worker to
  start will receive four times the number of messages initially. Thus the tasks may not be
  fairly distributed to the workers" [45]. Celery's optimizing guide pairs the two settings
  for many long tasks, and warns that "this also means the task must be idempotent" [52].
  For many short tasks where throughput matters the guide wants a larger value, and for a mix of
  long and short tasks it advises "two worker nodes that are configured separately" [52].
- **Set a time limit on every Celery task.** There is none by default [45], and "A single
  task can potentially run forever"; Celery calls time limits "The best way to defend against
  this scenario" [44]. Write `task_soft_time_limit` too, its value or `None` (section 8): set
  below `task_time_limit`, the soft limit raises `SoftTimeLimitExceeded` so the task can clean
  up, and the hard limit kills the worker process and replaces it [45], [44].
- **On the gevent pool, put a timeout on each call the task makes.** "The gevent pool does not
  implement soft time limits", and "it will not enforce the hard time limit if the task is
  blocking" [44].
- **With Dramatiq, write `time_limit` on every actor, even at its default of 10 minutes
  ([delivery.md](delivery.md) section 5).** The default is 10 minutes, after which the actor "is
  killed with a TimeLimitExceeded error", and the value is in milliseconds [48]. "Time limits are best-effort. They cannot cancel system
  calls or any function that doesn't currently hold the GIL under CPython" [48]. So give each
  network call its own timeout as well, as Dramatiq's guide advises [48]. For an `async def`
  actor the docs do not say how the limit reaches the coroutine, so bound the work inside it with
  `asyncio.timeout()` (section 7) [53].
- **On Celery's Redis broker, keep every countdown, ETA and retry delay below the visibility
  timeout.** The timeout is "the number of seconds to wait for the worker to acknowledge the task
  before the message is redelivered to another worker", and its default is 1 hour [54]. A
  task whose delay runs past it "will be executed again, and again in a loop" [54]. Raising
  the timeout to the longest delay "is not recommended as it may have negative impact on the
  reliability", because it also delays the redelivery of tasks lost in a crash [54]. For work
  due later, Celery says "Broker is not a database" and points to a database-backed periodic
  task [54]: store the due time in a table, and let a scheduled job enqueue the task when it
  is due ([scheduled-jobs.md](scheduled-jobs.md)).
- **On Celery's Redis broker with late acknowledgement, keep the visibility timeout above the
  longest task.** A task that is not acknowledged within the timeout goes to another worker
  [54], and a late-acknowledged task is acknowledged only when it ends, so a longer task runs
  twice at the same time. When you change the timeout, set it in `broker_transport_options`,
  `result_backend_transport_options` and `visibility_timeout`: Celery says it is "required to set
  all of them", and when several applications share the broker "the shortest value will be
  used" [54].

Celery settings for long tasks. Celery calls `configure_long_tasks` itself: it is connected to
the app's `on_after_configure` signal, as Celery's own periodic-tasks example connects its setup
function, and "on_after_configure is sent after the app is set up" [61]. The app itself is a bare
`Celery(...)` built at import in this module, a departure from
[python.md](../language/python.md) section 5, which builds no app at import: `celery -A` imports
that attribute and calls no factory. The cost: the module holds an app object at import, with no
settings in it. Building the app and its broker connection is left out:

```python
from celery import Celery


# `celery -A` only imports this module; the signal makes Celery call this
# once the app's configuration is ready.
@app.on_after_configure.connect
def configure_long_tasks(sender: Celery, **kwargs: object) -> None:
    sender.conf.update(
        # Ack after the task returns, so a dead worker means a rerun, not a lost task.
        task_acks_late=True,
        # Off, the default: on, a task that kills its worker comes back for ever,
        # unless the queue dead-letters it after a set number of deliveries
        # (task-queues.md section 5).
        task_reject_on_worker_lost=False,
        # On, the default, written: a task that fails or times out is acknowledged,
        # not redelivered; its own retry options retry it (task-queues.md section 5).
        task_acks_on_failure_or_timeout=True,
        # Reserve one message per process, so no message waits behind a long task.
        worker_prefetch_multiplier=1,
        # At 9 minutes the task gets SoftTimeLimitExceeded, so it can clean up in time.
        task_soft_time_limit=540,
        # At 10 minutes the worker process is killed and replaced.
        task_time_limit=600,
        # No caller reads these results; a task whose caller does
        # sets ignore_result=False.
        task_ignore_result=True,
        # JSON only, the default: pickle would run code for anyone who can write to
        # the broker (task-queues.md section 12).
        accept_content=["json"],
    )
```

It is good because each setting that changes a default says why at its line, so nobody resets it
to tidy up: late acknowledgement with a prefetch of one is the pair Celery gives for long
tasks [52], both limits are set with the soft one first [44], and results are off
where nobody reads them (section 7). The tasks it runs must be idempotent
([delivery.md](delivery.md) section 3).

## 7. Arguments, results and retries

- **Pass an id, and read the row inside the task.** Celery's docs say model objects "shouldn't be
  passed on as arguments to tasks. It's almost always better to re-fetch the object from the
  database when the task is running instead, as using old data may lead to race
  conditions" [2]. An id also keeps personal data out of the message (section 12).
- **Parse the arguments into a model once, where the task starts.** A task message is outside
  data ([python.md](../language/python.md) section 4). From Celery 5.5, a task with
  `pydantic=True` validates each argument typed as a Pydantic model; the caller still serializes
  the arguments itself, and strict validation, `pydantic_strict`, is off by default [2].
  Celery validates the decoded message, as FastAPI does a request body, so keep `pydantic_strict`
  off and mark strict fields on the model, as [python.md](../language/python.md) section 4 says.
- **Write the task function as the worker's adapter.** It parses the message, calls one use case,
  and holds no business rule; it lives in the worker's adapter folder
  ([file-structure.md](../../any-language/file-structure/file-structure.md) section 5).

The worker's Celery task for the `reindex_order` module, in
`src/acme/worker/handlers_reindex_order.py`. The call to the use case is left out:

```python
from celery import shared_task

from acme.core.schemas import ReindexOrder, TaskName


# name: the client in core/ sends the task by name, so it never imports this module.
# pydantic=True: Celery parses the message into ReindexOrder here, once
# (python.md section 4).
@shared_task(name=TaskName.REINDEX_ORDER, pydantic=True)
def reindex_order(command: ReindexOrder) -> None:
    ...  # call the reindex_order use case with its clients (see below)
```

It is good because the message becomes a typed model at the edge, so no code past this line sees
raw input; `ReindexOrder`, in `core/schemas.py` (section 4), sets `extra="ignore"`, with a
comment that names the module that sends it, as [delivery.md](delivery.md) section 8 asks of
every message model, and it holds only the
order id, so the use case reads the order itself. A module sends the task by name through its
client in `core/`: "If the task isn't registered in the current process you can use send_task()
to call the task by name instead" [55]. Where the clients come from: Celery builds a task once
per process, so its Tasks guide keeps a client on a base `Task` class that opens it on first use,
and a task declared with `base=` and `bind=True` reads it through `self` [2].

The same task as a Dramatiq actor written with `async def`. Setting up the broker and the AsyncIO
middleware is left out:

```python
import asyncio

import dramatiq
from pydantic import ValidationError

from acme.core.schemas import ReindexOrder


# Five retries, not the default 20: after that a person should look, so the message
# goes to the dead-letter queue and its alarm (delivery.md section 6).
# The wait in milliseconds, at Dramatiq's defaults: 15 s, growing to 7 days at most
# (delivery.md section 5).
# The time limit at Dramatiq's default, 10 minutes (delivery.md section 5).
@dramatiq.actor(
    max_retries=5,
    min_backoff=15_000,
    max_backoff=604_800_000,
    time_limit=600_000,
    # No retry can fix a body that does not parse, so it goes to the dead-letter
    # queue at once (delivery.md section 5).
    throws=(ValidationError,),
)
async def reindex_order(payload: str) -> None:
    # A message is outside data: parse it once, here (python.md section 4).
    command = ReindexOrder.model_validate_json(payload)
    # The docs do not say how time_limit reaches a coroutine, so bound the work here.
    async with asyncio.timeout(60):
        ...  # call the reindex_order use case with its clients (see below)
```

It is good because Dramatiq runs an `async def` actor once the worker adds the AsyncIO
middleware [24], the message is parsed once at the edge, and the work has a bound that a
coroutine is known to respect: `asyncio.timeout()` limits "the amount of time spent waiting on
something" [53]. The changed retry count and the wait carry their reasons at their lines, and
Dramatiq's guide lists `min_backoff` and `max_backoff` among the options set per actor [48]. A
body that does not parse is not retried: `throws` names `ValidationError`, so the message goes
to the dead-letter queue on its first failure ([delivery.md](delivery.md) section 5).
Where the clients come from: Dramatiq's
reference documents a middleware hook, `after_process_boot`, "Called immediately after subprocess
start up" [56], but its docs show no way to hand what it builds to an actor, so this file has no
rule for that yet (section 1).

- **Store a result only when a caller reads it.** Celery stores no result until `result_backend`
  is set [45]. Once it is set, a stored result expires after 1 day by default
  (`result_expires`), through a built-in periodic task that runs "assuming that celery beat is
  enabled", and with the database or filesystem backend beat must run for results to expire at
  all [45]. Set `task_ignore_result=True` on the tasks whose result nobody reads, and know
  that "Certain features will not work if task results are disabled" [2]. Dramatiq stores
  results only through its Results middleware, whose `backend` argument is required since
  2.0.0 [26]; it stores nothing unless `store_results` is set, and keeps a result for
  10 minutes by default [56], [24].
- **Retries: write the per-task options, and take the rule from [delivery.md](delivery.md)
  section 5.** That section owns each tool's defaults and how to make a retry wait. What a
  programmer writes on a task:
  - Celery: `autoretry_for=(...)` names the exceptions to retry, `max_retries` caps the count, and
    `retry_backoff=True` turns on exponential backoff [2]. On a task that retries, `max_retries`
    and its wait are each written even at its default (section 8).
  - Dramatiq: `max_retries` on the actor, where "None means the message should be retried
    indefinitely", and `throws` for exceptions that "must not get retried" [48].
  - Procrastinate: `retry=` on the task, as a count, `True` for no limit, or a `RetryStrategy`
    [57].

## 8. Settings you set

Defaults are those of Celery 5.6.3 and of the Dramatiq 2.2.0 docs. The tools require none of
these; this practice requires every row whose "Leave it out when" reads Never
([delivery.md](delivery.md) section 5).

| Field | What it means | Set it when | Leave it out when |
|---|---|---|---|
| Celery `task_acks_late` | Acknowledge a task after it returns. Default: disabled [45]. | Always, the default's value included ([delivery.md](delivery.md) section 5): `True` for a task that is idempotent ([delivery.md](delivery.md) section 3), `False` for one that cannot be made idempotent and whose lost run costs less than a second run (section 10). | Never. |
| Celery `task_reject_on_worker_lost` | Put a late-acknowledged task back on the queue when its worker process dies. Default: disabled; it "can cause message loops" [45]. | Always, the default's value included ([delivery.md](delivery.md) section 5): `True` when the queue dead-letters a message after a set number of deliveries ([delivery.md](delivery.md) section 6), `False` otherwise. | Never. |
| Celery `task_acks_on_failure_or_timeout` | With late acknowledgement, acknowledge a task that fails or times out instead of returning it to the queue. Default: enabled [45]. | Always, the default's value included ([delivery.md](delivery.md) section 5): `True`, so the task's own retry options decide its retries (section 7). | Never. |
| Celery `worker_prefetch_multiplier` | Messages each worker process reserves ahead. Default: 4 [45]. | Always: 1 for long tasks, with `task_acks_late=True`; a larger value for short tasks where throughput matters [52]. | Never. |
| Celery `task_time_limit` | Hard limit in seconds; the worker process is killed and replaced. Default: no limit [45]. | Always. | Never. |
| Celery `task_soft_time_limit` | Soft limit in seconds; raises `SoftTimeLimitExceeded` in the task. Default: no soft limit [45]. | Always, the default's value included ([delivery.md](delivery.md) section 5): below the hard limit when the task has something to clean up, `None` when it has nothing. | The pool is gevent, which does not implement it [44]. |
| Celery `result_backend`, `task_ignore_result` | Where results are stored, and whether a task stores its return value. Defaults: no backend; results not ignored [45]. | A caller reads results: set the backend, and `task_ignore_result=True` on every task whose result nobody reads. | No caller reads any result: set no backend. |
| Celery `result_expires` | When stored results are deleted. Default: 1 day [45]. | Results must live a shorter or a longer time. `None` or 0 keeps them for ever [45]. | No result backend is set. |
| Celery `visibility_timeout`, Redis broker | Seconds before an unacknowledged task goes to another worker. Default: 1 hour [54]. | Always on the Redis broker, the default's value included ([delivery.md](delivery.md) section 5): above the longest late-acknowledged task and every countdown (section 6). | The broker is RabbitMQ. |
| Celery `accept_content` | The serializers a worker accepts. Default: JSON only [45]. | Always, as `["json"]`, so the safe value shows at the line. | Never; never add pickle or yaml (section 12). |
| Celery `worker_enable_remote_control` | Whether workers obey remote-control commands, such as a broadcast `shutdown`. Default: enabled [45]. | Always: `False` unless a tool you run sends control commands (section 12). | Never. |
| Celery `max_retries`, with `default_retry_delay`, or with `retry_backoff`, `retry_backoff_max` and `retry_jitter` | The count and the wait of a task that retries [2]. The defaults are in [delivery.md](delivery.md) section 5. | Always on a task that lists `autoretry_for` or calls `self.retry()`, the defaults' values included ([delivery.md](delivery.md) section 5). | A task with neither, which does not retry: that shows at its decorator. |
| Dramatiq `time_limit` | Milliseconds an actor may run before it is killed. Default: 600,000, which is 10 minutes [56]. | Always, the default's value included ([delivery.md](delivery.md) section 5): 600,000 when 10 minutes fits the actor's normal run, another value when it does not. | Never. |
| Dramatiq `max_retries` | Retries before the message is dead-lettered; `None` retries forever [48]. The default is in [delivery.md](delivery.md) section 5. | Always, with its wait (`min_backoff`, `max_backoff`), the default's value included ([delivery.md](delivery.md) section 5). | Never. |
| Procrastinate `listen_notify` | The worker listens for new-job notifications; it polls in any case. Default: True [17]. | You must save the one connection the worker keeps open for listening [18]. | You need no fewer connections; polling alone is slower to start a job [17]. |

## 9. Common mistakes

- **An `async def` function as a Celery task.** It looks natural to someone who writes async web
  code. Celery 5.6.3 has no native support for coroutine tasks [21], and in Python "simply
  calling a coroutine will not schedule it to be executed" [53], so the body does not run
  the way the code reads. The fix: write the task as a plain `def`, or use Dramatiq with its
  AsyncIO middleware (section 7).
- **`delay()` inside the transaction.** It reads like the natural place to send the task, next to
  the write. The worker can run before the commit and find nothing [2]. The fix: section 4.
- **A model object as an argument.** It saves a query in the caller. The task then runs on old
  data: Celery's own example shows another author's edit reverted by a task that ran later
  [2]. The fix: pass the id (section 7).
- **Late acknowledgement on a task that is not idempotent.** It looks like the whole fix for lost
  tasks. The task then repeats its side effect after a crash, which is why Celery's
  guide says "this also means the task must be idempotent" [52]. The fix:
  [delivery.md](delivery.md) section 3 first, then the setting.
- **A countdown longer than the Redis visibility timeout.** It works in tests with short delays.
  In production the task runs "again, and again in a loop" [54]. The fix: section 6.

## 10. Where the rules stop holding

- **A task that cannot be made idempotent**, such as a call to an outside API that takes no
  idempotency key: [delivery.md](delivery.md) section 12 says how to choose between a second call
  and a lost one.
- **Work that one transaction cannot hold**, with steps that depend on each other: a chain of
  tasks keeps no record of where it stopped. [durable-workflows.md](durable-workflows.md)
  section 2 gives the test.
- **Long and short tasks on one worker.** No prefetch value suits both; run two workers, as
  section 6 says [52].
- **The PostgreSQL queue** stops being the simpler way under the signs at the end of section 2.

## 11. Alternatives considered

- **RQ, Taskiq, pgmq and arq.** Named once in section 3, with the reason each is not described.
- **Leaving PostgreSQL at the first sign of section 2.** Not taken as the first step: a move to a
  tool of section 3 trades the job written in its data's transaction for an outbox and a relay
  ([delivery.md](delivery.md) section 4), and the one team found that met the throughput sign
  stayed on PostgreSQL, for reasons tied to its product, after about six months of work and a
  rewrite of its engine [14]. It is the next step when tuning no longer keeps the
  signs away (section 2).
- **Redis as the default Celery broker.** Not taken, for the data-loss and visibility-timeout
  limits of sections 3 and 6.
- **A longer Redis visibility timeout to fit long ETAs.** Celery advises against it, because it
  delays the redelivery of lost tasks [54]; a database row and a scheduled job hold work due
  later (section 6).
- **A durable-workflow engine for every background job.** The two teams that left Celery for one
  ran multi-step pipelines, and both posts are tied to the tool they moved to (section 3). For a
  job that one transaction can hold, this practice keeps a task queue, as
  [durable-workflows.md](durable-workflows.md) section 2 also says.
- **The framework's background tasks for work that must not be lost.** FastAPI itself points to a
  bigger tool for that (section 2).

## 12. Security and personal data

This section covers four threats: a message that runs code when the worker decodes it, a leaked
broker credential, a broker connection read on the network, and personal data kept in task
messages and results. Securing the broker itself (TLS, users, permissions) and the shared rules
for personal data in messages are [delivery.md](delivery.md) section 10.

- **Keep Celery's serializer at JSON, and never add pickle to `accept_content`.** Celery's docs
  say that by default "only json is enabled but any content type can be added, including pickle
  and yaml; when this is the case make sure untrusted parties don't have access to your
  broker" [45]. Python's docs give the reason: "It is possible to construct malicious pickle
  data which will execute arbitrary code during unpickling" [58]. So a worker that accepts
  pickle runs code for anyone who can write to the broker.
- **Keep Dramatiq's encoder at its default, `JSONEncoder`, and never set `PickleEncoder`.**
  Dramatiq's reference says `JSONEncoder` "is the default encoder", and of `PickleEncoder`: "This
  encoder is not secure against maliciously-constructed data" [56].
- **Give write on the task queue only to the applications that enqueue.** JSON does not make a
  broker writer harmless. Celery's security guide: "By default, workers trust that the data they
  get from the broker hasn't been tampered with" [59]. So whoever can write to the broker can run
  any registered task with the arguments it picks. Remote control is "Enabled by default"
  (`worker_enable_remote_control`) [45], and `app.control.broadcast('shutdown')` shuts the workers
  down [44]. Its commands do not travel through the task queue: they go to the control command
  exchange, `control_exchange`, "celery" by default [45]. So set
  `worker_enable_remote_control=False` unless a tool you run sends control commands, such as
  `celery inspect` or `celery control` [44]; where it stays on, give write on the control
  exchange only to the operators' user. The rights per application are
  [delivery.md](delivery.md) section 10. Where parties you do not trust can reach the broker,
  Celery's guide points to message signing [59]; this file does not describe it.
- **Turn on TLS to the broker, with `broker_use_ssl` or a `rediss://` URL, and on Redis set
  `ssl_cert_reqs` to required, never to none.** Celery's `broker_use_ssl` is "Disabled" by
  default, and its Redis form accepts `ssl.CERT_NONE` among the values of `ssl_cert_reqs`; in a
  `rediss://` URL the value is `ssl_cert_reqs=required` [45]. A Redis or Valkey broker also
  follows [caching.md](caching.md) section 14's rules for the network, the ACL user and TLS.
- Broker credentials from the settings class, and ids instead of personal data in task
  arguments: [delivery.md](delivery.md) section 10.
- **Never log a task's arguments or its result** ([logging.md](../logging/logging.md) section 10).
  Celery logs them itself, in two records: the one for a failed task holds the exception's text,
  and the one for a task that succeeded prints its return value, `%(return_value)s`, at `INFO`;
  each puts the task's arguments in its `data` field [60]. So pass only ids, return an id or
  nothing, never a record that holds personal data, and where an argument must still stay out of
  the logs, set `argsrepr` or `kwargsrepr` on the call, which set how the arguments "are
  represented in logs and monitoring events" [2].

## 13. Checks

At review, ask of each change that adds or edits a task:

- Is every enqueue after the commit, or on the transaction's own connection (section 4)?
- Does every task with late acknowledgement show why a second run changes nothing
  ([delivery.md](delivery.md) section 3)?
- Does every task write its hard time limit (section 6)?
- Does every `async def` actor also bound its work inside (section 6)?
- On the Redis broker, is every countdown, ETA and retry delay below the visibility timeout, and
  the timeout above the longest late-acknowledged task (section 6)?
- With Procrastinate, does the change that adds a worker also add the stalled-jobs task
  ([scheduled-jobs.md](scheduled-jobs.md) section 8)?
- Is any function under a Celery task decorator written with `async def` (section 9)?
- Does `grep -rnE "PickleEncoder|accept_content.*pickle" src/` print nothing (section 12)?
- Does every Celery worker set `worker_enable_remote_control=False`, or, where a tool needs it,
  may only the operators' user write on the control exchange (section 12)?

In tests, a unit test replaces the jobs client with a fake that records what was sent
([fakes-and-boundaries.md](../testing/fakes-and-boundaries.md) section 3), and an integration test
runs the real broker or PostgreSQL in a container ([libraries.md](../testing/libraries.md)
section 2).

## 14. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Brandur Leach — River: a Fast, Robust Job Queue for Go + Postgres (brandur.org, 2023; opinion; the author wrote River) — https://brandur.org/river
- [2] Celery — Tasks, 5.6.3 — https://docs.celeryq.dev/en/stable/userguide/tasks.html
- [3] Celery — PyPI project metadata (JSON API), 5.6.3 — https://pypi.org/pypi/celery/json — checked 2026-10-30
- [4] Dramatiq — PyPI project metadata (JSON API), 2.2.1 — https://pypi.org/pypi/dramatiq/json — checked 2026-10-30
- [5] Procrastinate — PyPI project metadata (JSON API), 3.10.0 — https://pypi.org/pypi/procrastinate/json
- [6] FastAPI — Background Tasks — https://fastapi.tiangolo.com/tutorial/background-tasks/
- [7] Django — Django's Tasks framework, Django 6.0 — https://docs.djangoproject.com/en/6.0/topics/tasks/
- [8] Richard Yen — Potential Consequences of Using Postgres as a Job Queue (richyen.com, 2026; opinion; first published on Microsoft's Tech Community blog, and Microsoft sells a managed PostgreSQL) — https://richyen.com/postgres/2026/05/04/postgres_job_queue.html
- [9] pypistats — Recent downloads of procrastinate — https://pypistats.org/api/packages/procrastinate/recent
- [10] pypistats — Recent downloads of pgmq — https://pypistats.org/api/packages/pgmq/recent
- [11] Procrastinate — README — https://github.com/procrastinate-org/procrastinate
- [12] Simeon Griggs — Keeping a Postgres queue healthy (PlanetScale blog, 2026; research, sponsored by PlanetScale, which sells PostgreSQL) — https://planetscale.com/blog/keeping-a-postgres-queue-healthy
- [13] Stanislav Kozlovski — Kafka is fast -- I'll use Postgres (topicpartition.io, 2025; research) — https://topicpartition.io/blog/postgres-pubsub-queue-benchmarks
- [14] abelanger — Show HN: Hatchet v1 – A task orchestration platform built on Postgres (Hacker News, 2025; case; the author is a co-founder of Hatchet, which sells the platform) — https://news.ycombinator.com/item?id=43572733
- [15] Elliot Levin — Postgres LISTEN/NOTIFY does not scale (Recall.ai blog, 2025; case) — https://recall.ai/blog/postgres-listen-notify-does-not-scale
- [16] PostgreSQL — commit 282b1cd, Optimize LISTEN/NOTIFY via shared channel map and direct advancement — https://github.com/postgres/postgres/commit/282b1cde9dedf456ecf02eb27caf086023a7bb71
- [17] Procrastinate — API Reference, 3.10.0 — https://procrastinate.readthedocs.io/en/stable/reference.html
- [18] Procrastinate — Discussions, 3.10.0 — https://procrastinate.readthedocs.io/en/stable/discussions.html
- [19] pypistats — Recent downloads of celery — https://pypistats.org/api/packages/celery/recent
- [20] Celery — First Steps with Celery, 5.6.3 — https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html
- [21] SeyyedKomeil — Support async function (GitHub, celery/celery issue #6552, 2020; opinion) — https://github.com/celery/celery/issues/6552
- [22] ghirailghiro — asyncio pool: run coroutine task bodies on a shared event loop (GitHub, celery/celery pull request #10634, 2026; opinion) — https://github.com/celery/celery/pull/10634
- [23] Celery — What's new in Celery 5.6 (Recovery) — https://docs.celeryq.dev/en/main/history/whatsnew-5.6.html
- [24] Dramatiq — Cookbook, 2.2.0 — https://dramatiq.io/cookbook.html
- [25] Dramatiq — Advanced Topics, 2.2.0 — https://dramatiq.io/advanced.html
- [26] Dramatiq — Changelog, 2.2.0 — https://dramatiq.io/changelog.html
- [27] pypistats — Recent downloads of dramatiq — https://pypistats.org/api/packages/dramatiq/recent
- [28] somnam — Delayed messages are being duplicated on work queue which leads to one message being consumed and processed by many WorkerThreads (GitHub, Bogdanp/dramatiq issue #431, 2021; case) — https://github.com/Bogdanp/dramatiq/issues/431
- [29] Marcos Placona — From Celery to DBOS: Scaling Dosu's Pipelines to 20k Workflows per Hour (Dosu blog, 2025; case; written as a case study with DBOS) — https://dosu.dev/blog/migrate-celery-to-dbos-dosu
- [30] Rahul Balakavi — From Celery to Inngest: Why We Migrated Our Task Execution Layer (AmpUp blog, no date; case; AmpUp runs on Inngest Cloud) — https://www.ampup.ai/blog/eng-stack-inngest
- [31] MarcSalvat — Long tasks are executed multiple times (GitHub, celery/celery issue #3430, 2016; case) — https://github.com/celery/celery/issues/3430
- [32] marvelph — Continuous memory leak (GitHub, celery/celery issue #4843, 2018; case) — https://github.com/celery/celery/issues/4843
- [33] Celery — README — https://github.com/celery/celery
- [34] Redis — Redis persistence — https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/
- [35] pypistats — Recent downloads of rq — https://pypistats.org/api/packages/rq/recent
- [36] RQ — README — https://github.com/rq/rq
- [37] Taskiq — PyPI project metadata (JSON API), 0.13.0 — https://pypi.org/pypi/taskiq/json — checked 2026-10-30
- [38] pypistats — Recent downloads of taskiq — https://pypistats.org/api/packages/taskiq/recent
- [39] pypistats — Daily downloads of taskiq, without mirrors — https://pypistats.org/api/packages/taskiq/overall?mirrors=false
- [40] pgmq — PyPI project metadata (JSON API), 1.1.4 — https://pypi.org/pypi/pgmq/json
- [41] samuelcolvin — Maintenance only mode (GitHub, python-arq/arq issue #510, 2025; case) — https://github.com/python-arq/arq/issues/510
- [43] psycopg — rows: row factory implementations, 3.3.7.dev1 — https://www.psycopg.org/psycopg3/docs/api/rows.html — checked 2026-10-30
- [44] Celery — Workers Guide, 5.6.3 — https://docs.celeryq.dev/en/stable/userguide/workers.html
- [45] Celery — Configuration and defaults, 5.6.3 — https://docs.celeryq.dev/en/stable/userguide/configuration.html
- [46] Dramatiq — `dramatiq/worker.py`, v2.2.0 — https://github.com/Bogdanp/dramatiq/blob/v2.2.0/dramatiq/worker.py
- [47] Dramatiq — `dramatiq/brokers/rabbitmq.py`, v2.2.0 — https://github.com/Bogdanp/dramatiq/blob/v2.2.0/dramatiq/brokers/rabbitmq.py
- [48] Dramatiq — User Guide, 2.2.0 — https://dramatiq.io/guide.html
- [49] Dramatiq — `dramatiq/brokers/redis.py`, v2.2.0 — https://github.com/Bogdanp/dramatiq/blob/v2.2.0/dramatiq/brokers/redis.py
- [50] Dramatiq — `dramatiq/brokers/redis/dispatch.lua`, v2.2.0 — https://github.com/Bogdanp/dramatiq/blob/v2.2.0/dramatiq/brokers/redis/dispatch.lua
- [51] Procrastinate — Retry stalled jobs, 3.10.0 — https://procrastinate.readthedocs.io/en/stable/howto/production/retry_stalled_jobs.html
- [52] Celery — Optimizing, 5.6.3 — https://docs.celeryq.dev/en/stable/userguide/optimizing.html
- [53] Python — Coroutines and tasks, Python 3.15.2 — https://docs.python.org/3/library/asyncio-task.html — checked 2026-10-30
- [54] Celery — Using Redis, 5.6.3 — https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html
- [55] Celery — Calling Tasks, 5.6.3 — https://docs.celeryq.dev/en/stable/userguide/calling.html — checked 2026-10-30
- [56] Dramatiq — API Reference, 2.2.0 — https://dramatiq.io/reference.html
- [57] Procrastinate — Define a retry strategy on a task, 3.10.0 — https://procrastinate.readthedocs.io/en/stable/howto/advanced/retry.html
- [58] Python — pickle: Python object serialization, Python 3.15.2 — https://docs.python.org/3/library/pickle.html
- [59] Celery — Security, 5.6.3 — https://docs.celeryq.dev/en/stable/userguide/security.html — checked 2026-10-30
- [60] Celery — `celery/app/trace.py`, v5.6.3 — https://raw.githubusercontent.com/celery/celery/v5.6.3/celery/app/trace.py
- [61] Celery — User Guide: Periodic Tasks, 5.6.3 — https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html — checked 2026-10-30
