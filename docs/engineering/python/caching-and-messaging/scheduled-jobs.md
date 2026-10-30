# Scheduled jobs

Rules for code that must run at set times, such as a nightly report or a cleanup, and must still
do the right thing when the scheduler restarts, falls behind or the clocks change.

**Navigation**

- [1. Purpose and scope](#1-purpose-and-scope)
- [2. Which scheduler](#2-which-scheduler)
- [3. One scheduler per schedule](#3-one-scheduler-per-schedule)
- [4. The job: a way in that is safe to run twice](#4-the-job-a-way-in-that-is-safe-to-run-twice)
- [5. Time zones and daylight saving time](#5-time-zones-and-daylight-saving-time)
- [6. Missed and late runs](#6-missed-and-late-runs)
- [7. A run still going when the next one is due](#7-a-run-still-going-when-the-next-one-is-due)
- [8. If you run Procrastinate: retry stalled jobs on a schedule](#8-if-you-run-procrastinate-retry-stalled-jobs-on-a-schedule)
- [9. Settings you set](#9-settings-you-set)
- [10. Common mistakes](#10-common-mistakes)
- [11. Where the rules stop holding](#11-where-the-rules-stop-holding)
- [12. Alternatives considered](#12-alternatives-considered)
- [13. Security and personal data](#13-security-and-personal-data)
- [14. Checks](#14-checks)
- [15. Sources](#15-sources)

## 1. Purpose and scope

A scheduled job is code that a scheduler starts at set times: every night at 02:15, every five
minutes. The function is the easy part. The hard part is what happens around it: two schedulers
send the same run, a scheduler that was down sends a missed run late or never, a slow run is still
going when the next one starts, and a schedule in a local time zone skips or doubles a run when
the clocks change. This file is for the programmer who adds such a job to a Python service.
Running the scheduler's own servers is out of scope.

A service that follows this file has one scheduler per schedule, schedules written in UTC, a
chosen answer for a late run and for an overlapping run, and jobs that do no harm when a run comes
twice.

**The one rule: run one scheduler per schedule, and write every job so that a second run for the
same period changes nothing.** No scheduler here promises exactly one run. Kubernetes says a
CronJob can create two Jobs or none [1], and Celery says a second beat process gives you
duplicate tasks [2].

**When you need a scheduler tool, and the simpler way.** A job inside one long-running process,
such as a small service that runs as one container, needs no extra service: APScheduler 3.x runs
it inside that process, and 3.11.3 is its current stable release [3]. Move to a pick in section 2,
or run APScheduler in one process of its own that enqueues the job, when the job runs in a service
with more than one process, because APScheduler's "Job stores must never be shared between
schedulers" [4].

**Out of scope:** data pipeline orchestration (Airflow, Dagster, Prefect); a scheduled CI workflow,
which [ci-cd/pipeline.md](../../any-language/ci-cd/pipeline.md) section 4 covers; a task deferred
once to run later, which is a task queue's job ([task-queues.md](task-queues.md)).

**Not covered yet:** a lock that stops two runs of one Celery beat task from overlapping (no
Celery owner text on it was found); daylight saving time guidance from Celery or Kubernetes,
whose docs say nothing on it (section 5); the time zone of a Procrastinate cron string, on which
its docs are silent; keeping Celery beat running when its one process dies; alerting when a run
fails or never starts; the late-run and overlap settings of a durable-workflow engine's own
schedules (section 2).

## 2. Which scheduler

Pick the scheduler from what the service already runs.

| Tool (Python client) | Use it when | Too much, or the risk |
|---|---|---|
| Celery beat, Celery's own scheduler | The service already runs Celery workers. | Run exactly one beat process, "otherwise you'd end up with duplicate tasks" [2]. Beat keeps the last run times in a local file [2], and a beat entry has no setting for an overlapping run (section 7). |
| Procrastinate periodic tasks (`periodic` on the App or a Blueprint) | The service already runs Procrastinate on PostgreSQL. | Any worker can defer the task, and "the database is responsible for making sure deferring only happens once per period, even with multiple workers" [5]. "If there is no worker running, then periodic tasks will not get scheduled" [5], and a worker that starts does not defer a task that is more than 10 minutes late [5]. |
| Kubernetes CronJob | The job is a separate Python command, and the service runs on Kubernetes. | "there are certain circumstances where two Jobs might be created, or no Job might be created", so the Jobs should be idempotent [1]. With no deadline set, more than 100 missed schedules stop it from starting the Job [1]. |

The first two rows are one pick, the task queue's own scheduler; which one follows from the queue
the service runs ([task-queues.md](task-queues.md)). For Dramatiq, its Cookbook says "APScheduler
is the recommended scheduler to use with Dramatiq" [25]: run APScheduler 3.x in one dedicated
process that enqueues the actor's messages, and apply sections 3 and 5 to 7 to it. The simpler
way, APScheduler 3.x in one process, is in section 1. APScheduler 4.0 is still a pre-release: its latest release is
4.0.0a6 [3], and its README says "do NOT use this release in production!" [6].

A team already on a durable-workflow engine ([durable-workflows.md](durable-workflows.md)) can use
the engine's own schedules, Temporal Schedules or DBOS scheduled workflows. This file names them
once and does not describe them: their late-run and overlap settings are not covered yet
(section 1).

## 3. One scheduler per schedule

- **Run one Celery beat process per schedule, apart from the workers,** because a second one sends
  every task again [2]. Start it as its own process (`celery -A <app> beat`) with one replica. Do
  not embed beat in a worker with `-B` when more than one worker may run: the docs call it
  "convenient if you'll never run more than one worker node", and it "isn't recommended for
  production use" [2].
- **Give beat a path it can write for its state file.** Beat stores the last run times in a local
  file, `celerybeat-schedule` by default, so it needs write access to the current directory or a
  path set with `-s` [2].
- **With APScheduler, run one scheduler per job store, in one process.** Sharing a persistent job
  store between processes "will lead to incorrect scheduler behavior like duplicate execution or
  the scheduler missing jobs" [10]. A web server with several worker processes is the usual way to
  get there: the FAQ sends readers who run more than one worker process to this answer, and its
  workaround is to run the scheduler in a dedicated process [10].
- **With Procrastinate, keep at least one worker running.** Workers defer the periodic tasks, so
  with no worker nothing is scheduled; any number of workers is safe, because the database defers
  once per period [5].
- **With Kubernetes, keep one CronJob per schedule.** The concurrency policy "only applies to the
  Jobs created by the same CronJob" [1], so two CronJobs for one job run side by side.

## 4. The job: a way in that is safe to run twice

- **Write a scheduled job as an adapter: it reads the time it was due, calls one use case and holds
  no business rule** ([file-structure.md](../../any-language/file-structure/file-structure.md)
  section 5). The scheduler is one more way into the application, so the rule stays testable and
  callable without the scheduler.
- **Make every scheduled job idempotent, by [delivery.md](delivery.md) section 3,** because every
  scheduler here can start the same run twice: a CronJob [1], Celery with a second beat [2],
  APScheduler with a shared job store [10].
- **Key a run by the period it covers, worked out from the time the run was due, never from the
  clock when it starts.** Otherwise a late run does the wrong period, and a repeated run does the
  same period twice under two keys. Procrastinate passes each periodic task the Unix timestamp it
  was scheduled for, and tells you to "use the received timestamp, not time.time() because tasks
  might be running late, but the timestamp you receive is always right" [5]. DBOS passes the
  scheduled time as the workflow's first argument [9]. From Kubernetes v1.32, a CronJob writes the
  scheduled time on each Job it creates, in the annotation
  `batch.kubernetes.io/cronjob-scheduled-timestamp` [1]. A Celery beat entry has fields for the
  task, its schedule, `args`, `kwargs`, `options` and `relative`, and none for the time the run was
  due [2]. A Celery task therefore works its period out from the clock when it runs, and the
  deadline in section 6 limits how late that clock can be.

A Procrastinate periodic task written this way, in the adapter that holds the worker's handlers.
The use case's own dependencies, such as its repository, are left out. In Procrastinate a task
reaches them through its job context: a task declared with `pass_context=True` gets a
`JobContext` as its first argument, and the worker started with
`run_worker_async(additional_context=...)` adds that dict to the context [11]. The adapter's
`main.py` builds the App with `periodic_defaults={"max_delay": 600}` (section 6) and registers the
Blueprint on it with `app.add_tasks_from(blueprint, namespace="reports")` [11].

```python
# src/acme/worker/handlers_build_daily_report.py
"""Scheduled jobs of the build_daily_report module."""

from datetime import UTC, datetime, timedelta

from procrastinate.blueprints import Blueprint

from acme.reports.build_daily_report import usecase

blueprint = Blueprint()


@blueprint.periodic(cron="15 2 * * *")
# The locks allow one run at a time and one waiting (scheduled-jobs.md section 7).
# retry=False is the default, written: a failed run is not tried again
# (delivery.md section 5).
@blueprint.task(lock="daily_report", queueing_lock="daily_report", retry=False)
async def build_daily_report(timestamp: int) -> None:
    """Build the report for the day before the scheduled run."""
    # The day comes from the time the run was due, not the clock, so a late or a
    # second run builds the same day (scheduled-jobs.md section 4).
    due_at = datetime.fromtimestamp(timestamp, tz=UTC)
    await usecase.build_daily_report(due_at.date() - timedelta(days=1))
```

It is good because the handler only turns the due time into a day and hands it to the use case,
so the rule is tested without a worker. The day comes from the time the run was due, so a run
that starts late, or runs a second time, builds the same report; the use case then writes that
report once per day, by [delivery.md](delivery.md) section 3. The two locks stop runs from piling
up in the queue or running side by side (section 7).

## 5. Time zones and daylight saving time

**Write every schedule in UTC, and wherever the tool has a zone setting, set it even where UTC is
the default,** because a schedule in a zone with daylight saving time skips or repeats runs when
the clocks change, and a default can come from somewhere else. APScheduler's docs explain the
failure: its
cron trigger works on wall-clock time, and the switch to and from daylight saving time "will cause
some time periods to either not exist at all, or be repeated" [12]. They add "This is not a bug",
and advise a zone without daylight saving time, such as UTC, or keeping the switch times out of
the schedule [12]. Temporal gives the same advice for its own schedules: "Temporal recommends
using UTC to avoid various surprising properties of time zones" [7].

- **Celery.** Periodic tasks use UTC by default [2], but in a Django project Celery takes Django's
  `TIME_ZONE` unless you set `timezone` for Celery [2], and `enable_utc = False` switches it to the
  system's local zone [13]. Set `timezone = "UTC"`. If you change the zone later, the default
  scheduler resets its schedule by itself; under the Django database scheduler, reset it by hand,
  as the docs show [2]. Celery's periodic-tasks and configuration pages say nothing about daylight
  saving time for crontab [2], [13]. A report on Celery's tracker, opened in February 2026 on
  Celery 5.6.2 and still open when this was checked, shows an hourly crontab that skips one run
  when the clocks go back [14].
- **Kubernetes.** With no `timeZone`, the controller "interprets schedules relative to its local
  time zone" [1]. Set `.spec.timeZone: "Etc/UTC"`, a field stable since Kubernetes v1.27 [1]. A
  `CRON_TZ` or `TZ` inside `.spec.schedule` fails validation, and the docs say to use the field
  instead [1]. The CronJob page says nothing about daylight saving time [1].
- **APScheduler.** Pass `timezone` to the scheduler: in 3.11.3 it otherwise takes the host's local
  zone [15]. A cron trigger's own `timezone` defaults to the scheduler's [12].
- **Procrastinate.** Its periodic-task page names no time zone setting for the cron string [5], so
  this file has no rule for it yet (section 1).

## 6. Missed and late runs

**For each job, decide how late a run may still start, and set that limit,** because the defaults
differ: Celery beat sends a past-due cron run at once when it comes back, and APScheduler drops a
run more than one second late [13], [15]. Kubernetes gives the reason with a backup that may start
up to 8 hours late "but no later, because a backup taken any later wouldn't be useful" [1].

- **Celery: `beat_cron_starting_deadline`.** It is the number of seconds beat looks back when it
  decides whether a cron schedule is due, and its default is None: "When set to None, cronjobs that
  are past due will always run immediately" [13]. It applies to crontab entries, and the docs warn
  that "Setting this higher than 3600 (1 hour) is highly discouraged" [13]. Several missed times
  still give one run, not one per missed time: at v5.6.3 a crontab schedule makes one due decision
  from the last run time [16], and after a send beat sets the last run time to now [17]. That is a
  reading of the code; the docs do not say it.
- **Kubernetes: `.spec.startingDeadlineSeconds`.** With no value, a Job has no deadline [1]. A run
  that misses the deadline is skipped and counted as a failed Job, and later runs stay
  scheduled [1]. Keep it at 10 seconds or more: the controller checks every 10 seconds, so a smaller
  value may never start the Job [1]. The deadline also bounds the catch-up count: with no deadline,
  a controller that missed more than 100 schedules does not start the Job and logs an error; with
  one, it counts only the schedules missed inside the deadline [1]. Setting `.spec.suspend` back to
  false on a CronJob with no deadline starts the missed Jobs at once [1].
- **Procrastinate: `periodic_defaults={"max_delay": ...}` on the App.** When a worker starts, it
  defers the periodic tasks not deferred yet, but not a task that is more than 10 minutes late [5].
  `max_delay` sets that limit in seconds; the limit keeps a heavy nightly task from starting after
  an outage longer than it [11].
- **APScheduler: `misfire_grace_time` and `coalesce`.** A missed run still starts when it is
  within the job's `misfire_grace_time`, set per job or for the scheduler [4]. In 3.11.3 the default
  is 1 second, and `coalesce` is on, so several missed runs become one [15], [4]. The docs suggest a
  higher `misfire_grace_time` when runs start late because the executor's pool is busy [4].

Section 4's job on a service that runs Celery instead of Procrastinate, so each service has one
scheduler: a Celery beat config written by these rules, and the task it sends. The broker's
settings, the worker settings of [task-queues.md](task-queues.md) section 8, and the `imports`
setting that makes the worker import the task's module [13] are left out. Celery calls
`configure_beat` itself: it is connected to the app's `on_after_configure` signal, as Celery's own
periodic-tasks example connects its setup function, and "on_after_configure is sent after the app
is set up" [2].

```python
# src/acme/worker/main.py
"""Build the worker's Celery app and its beat schedule."""

from celery import Celery
from celery.schedules import crontab

from acme.core.schemas import TaskName

# A departure from python.md section 5, which builds no app at import: `celery -A`
# imports this attribute and calls no factory. The cost: the module holds an app
# object at import, with no settings in it.
app = Celery("acme")


# `celery -A` only imports this module; the signal makes Celery call this
# once the app's configuration is ready.
@app.on_after_configure.connect
def configure_beat(sender: Celery, **kwargs: object) -> None:
    sender.conf.update(
        # Set although UTC is the default: in a Django project Celery
        # takes Django's TIME_ZONE instead (scheduled-jobs.md section 5).
        timezone="UTC",
        # A cron run more than 30 minutes late is skipped when beat comes
        # back, not sent at once; the docs advise 3600 at most
        # (scheduled-jobs.md section 6).
        beat_cron_starting_deadline=1800,
        beat_schedule={
            "build-daily-report": {
                # By its TaskName member: beat sends the task by name and imports no
                # task code (python.md section 3).
                "task": TaskName.BUILD_DAILY_REPORT,
                "schedule": crontab(minute=15, hour=2),
            },
        },
    )
```

The task beat sends. On this service it sits in `src/acme/worker/handlers_build_daily_report.py`,
the file that holds section 4's task on a service that runs Procrastinate. The import of the use
case and the use case's own dependencies, such as its repository, are left out. A Celery task
reaches them through a base `Task` class: a task declared with `base=` and `bind=True` reads them
through `self` ([task-queues.md](task-queues.md) section 7). That class and those two arguments
are left out as well. On this service the use case is a plain `def` too, because a coroutine that
the task calls does not run ([task-queues.md](task-queues.md) section 9):

```python
# src/acme/worker/handlers_build_daily_report.py
"""Scheduled jobs of the build_daily_report module."""

from datetime import UTC, datetime, timedelta

from celery import shared_task

from acme.core.schemas import TaskName


# name: beat's entry in main.py sends the task by this TaskName member
# (task-queues.md section 7).
@shared_task(name=TaskName.BUILD_DAILY_REPORT)
def build_daily_report() -> None:
    """Build the report for the day before the run."""
    # Beat passes no due time, so the clock is read once, here; the deadline in
    # main.py bounds how late it can be (scheduled-jobs.md sections 4 and 6).
    report_day = datetime.now(UTC).date() - timedelta(days=1)
    usecase.build_daily_report(report_day)
```

It is good because the zone is written down where a Django setting cannot move it, and the
deadline is a choice made for this job, not the default that sends every past-due run at once.
The schedule sits in the worker's entry point, read by the one beat process of section 3, and it
is this job's only scheduler. Beat names the task by its `TaskName` member, a closed set and never
a bare `str` ([python.md](../language/python.md) section 3), and the task is a plain `def`,
because Celery 5.6.3 does not run an `async def` task ([task-queues.md](task-queues.md) section 9).
The task works its day out from the clock it reads once, because a beat entry carries no due time
(section 4).

## 7. A run still going when the next one is due

**Decide what a run that falls due while the last one still runs should do, and set it where the
tool lets you: skip it, let it wait, or run it beside the old one.** Keep the job idempotent anyway
([delivery.md](delivery.md) section 3), because no setting here fully stops two runs at once.

- **Kubernetes: `.spec.concurrencyPolicy`.** `Allow` is the default; `Forbid` skips the new run;
  `Replace` replaces the running Job with the new one [1]. `Forbid` does not make a second run
  impossible: the page says that "in certain circumstances, a single CronJob can create multiple
  concurrent Jobs", and that when a run under `Forbid` ends, the deadline is still taken into
  account and may start a new run [1].
- **APScheduler: `max_instances`.** By default only one instance of a job runs at a time, and a run
  that falls due while the last one runs counts as a misfire [4]. `max_instances` raises the
  limit [4], [15].
- **Procrastinate: `lock` and `queueing_lock`.** With a `lock`, a job cannot start before the job
  before it with the same lock has ended [18]. A `queueing_lock` lets one job wait in the queue at a
  time, and the docs combine the two "To enforce that only one job runs at a time while limiting
  the queue size" [19].
- **Celery beat: no setting.** A beat entry has no field for an overlapping run [2]. No Celery
  owner text on a lock for it was found, so this file covers none yet; the task stays idempotent.

A CronJob fragment for a separate Python command; the Pod template (image, command, resources) is
cut with `...`.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: build-daily-report
spec:
  schedule: "15 2 * * *"
  # Without it the controller's local zone applies, and that zone
  # may change its clocks (scheduled-jobs.md section 5).
  timeZone: "Etc/UTC"
  # Skip a run more than 30 minutes late. Under 10 seconds a Job may
  # never start (scheduled-jobs.md section 6).
  startingDeadlineSeconds: 1800
  # Skip a run while the last one still runs. Two Jobs can still
  # happen, so the command stays idempotent (scheduled-jobs.md
  # section 7).
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      # Kubernetes' default, 6, written: each retry of a failed Pod runs the
      # command again (scheduled-jobs.md section 9).
      backoffLimit: 6
      ...
```

It is good because each choice the defaults would make for you (the controller's zone, no
deadline, runs side by side, six retries of a failed run) is written down with its reason. The comment on `Forbid` keeps a
reader from dropping the idempotency the command still needs.

## 8. If you run Procrastinate: retry stalled jobs on a schedule

A worker killed with `SIGKILL`, or stopped by a second `SIGINT` or `SIGTERM`, can leave jobs in the
`doing` status, and "these stalled jobs will remain in the queue forever" [20].

- **Add the periodic task from Procrastinate's docs that retries stalled jobs,** so a killed worker
  does not leave work undone for good [20]. Their example runs every 10 minutes with a
  `queueing_lock`, and retries the jobs of workers with no heartbeat in the last 30 seconds, the
  default of `seconds_since_heartbeat` [20]. A retried job runs again, so it must be idempotent
  ([delivery.md](delivery.md) section 3).
- **Do not pass `nb_seconds` to `get_stalled_jobs`.** It is deprecated, because it "may lead to
  wrongly retrying jobs that are still running" [20].

## 9. Settings you set

The tools require none of these; this practice requires every row whose "Leave it out when" reads
Never ([delivery.md](delivery.md) section 5). A CronJob's `.spec.schedule` and `.spec.jobTemplate`
are required [1]; the table lists the settings that decide the questions of sections 4 to 7.

| Setting | What it means | Set it when | Leave it out when |
|---|---|---|---|
| Celery `timezone` | The zone for periodic schedules; `"UTC"` by default, Django's `TIME_ZONE` in a Django project [13], [2] | Always, to `"UTC"` (section 5) | Never |
| Celery `beat_cron_starting_deadline` | Seconds beat looks back for a due crontab run; None sends every past-due cron run at once [13] | Always, the default's value included ([delivery.md](delivery.md) section 5): the seconds after which a late crontab run is useless, or `None` when every missed run should still run once when beat comes back | Never |
| Kubernetes `.spec.timeZone` | The zone of `.spec.schedule`; the controller's local zone by default [1] | Always, to `"Etc/UTC"` (section 5) | Never |
| Kubernetes `.spec.startingDeadlineSeconds` | How late a Job may start; no deadline by default [1] | Always ([delivery.md](delivery.md) section 5): the seconds after which a late run is useless. For a frequent job that must run at least once, a deadline rather than none, large but shorter than 100 runs of its schedule, because with no deadline more than 100 missed schedules stop the Job from starting [1] | Never |
| Kubernetes `.spec.jobTemplate.spec.backoffLimit` | Retries of a failed Job's Pods before the Job counts as failed; 6 by default, each after an exponential back-off delay "(10s, 20s, 40s ...) capped at ten minutes" [24] | Always, the default's value included ([delivery.md](delivery.md) section 5): each retry runs the command again, so it stays idempotent (section 4) | Never |
| Kubernetes `.spec.concurrencyPolicy` | `Allow` (default), `Forbid` or `Replace` for a run due while the last one runs [1] | Always, the default's value included ([delivery.md](delivery.md) section 5): `Forbid` when a run may last longer than the gap between runs, `Allow` when two at once do no harm | Never |
| APScheduler `timezone` | The scheduler's zone; the host's local zone by default in 3.11.3 [15] | Always, to UTC (section 5) | Never |
| APScheduler `misfire_grace_time` | Seconds after its time that a missed run may still start; None means no limit; 1 by default [15] | Always, the default's value included ([delivery.md](delivery.md) section 5): more than 1 when the scheduler can be down or busy at a due time [4], 1 when a run more than a second late should be dropped | Never |
| APScheduler `coalesce` | Runs several missed runs of a job once; on by default [15] | Always ([delivery.md](delivery.md) section 5): `coalesce=False` when each missed time must run on its own, `True` otherwise | Never |
| APScheduler `max_instances` | How many runs of one job may run at once; 1 by default [4], [15] | Always, the default's value included ([delivery.md](delivery.md) section 5): 1, or more when runs may overlap and must not be dropped | Never |
| Procrastinate `periodic_defaults` `max_delay` | Seconds a periodic task may be overdue when a worker starts and still be deferred; 10 minutes by default [11] | Always, the default's value included ([delivery.md](delivery.md) section 5): 600 when 10 minutes fits the job, more when it must still run after a longer outage, less when it must not run late | Never |

## 10. Common mistakes

- **Two Celery beat processes,** such as one per worker replica, or `-B` on workers that scale out.
  Every task is sent twice [2]. Fix: one beat process, apart from the workers (section 3).
- **One persistent APScheduler job store shared by the worker processes of a web server.** It
  gives duplicate runs or missed jobs [10]. Fix: one scheduler in a dedicated process (section 3).
- **A time zone inside the CronJob schedule** (`CRON_TZ=` or `TZ=` in `.spec.schedule`). Kubernetes
  rejects the object with a validation error [1]. Fix: `.spec.timeZone` (section 5).
- **A schedule in a zone with daylight saving time.** In APScheduler's own example, a job at 03:30
  in the Europe/Helsinki zone does not run at all on the last Sunday morning of March and runs twice
  on the last Sunday morning of October [12]; Celery has an open report of an hourly crontab that
  skips a run when the clocks go back [14]. Fix: UTC (section 5).
- **No deadline on a frequent CronJob.** In the Kubernetes docs' own example, a job due every minute
  with no deadline does not start after the controller was down from 08:29 to 10:21; with a 200
  second deadline it starts at 10:22 [1]. Fix: set `startingDeadlineSeconds` (section 6).
- **A `startingDeadlineSeconds` under 10.** The Job may never be scheduled [1].
- **APScheduler left at its 1-second grace time.** A run delayed by a busy pool or a restart is
  skipped as too late; the docs suggest a higher `misfire_grace_time` [4], [15].
- **A periodic task that reads the clock to pick its period.** A late run then picks the wrong
  period [5]. Fix: use the time the run was due (section 4).
- **Trusting `concurrencyPolicy: Forbid` to make a second run impossible.** One CronJob can still
  create concurrent Jobs [1]. Fix: keep the command idempotent (section 7).

## 11. Where the rules stop holding

- **A job that must run at a local business hour,** such as 09:00 in one office. In UTC it moves by
  an hour twice a year. Schedule it in that zone, and keep it out of the hours the clocks skip or
  repeat, as APScheduler's docs advise [12]; Temporal and DBOS take a zone name too [7], [9]. On
  Celery, an hourly crontab in such a zone has an open bug when the clocks go back [14].
- **Every missed period must run, even after a long outage.** The late-run limits of section 6 drop
  such runs. A durable-workflow engine's own schedule may do the catch-up (section 2 names them;
  this file does not describe them).
- **Users set schedules at runtime.** Procrastinate's docs suggest one periodic task, run as often
  as the most frequent schedule a user can set, that reads the stored schedules and defers what is
  due for the timestamp it received [5].
- **One beat process is one point of failure:** while it is down, no task is sent. Keeping it
  running is not covered yet (section 1).

## 12. Alternatives considered

- **APScheduler 4.0.** Still a pre-release (4.0.0a6) [3], with the README's warning against
  production use [6]. Revisit when a stable 4.0 ships.
- **Beat embedded in a worker (`-B`).** Celery's docs do not recommend it for production [2].
- **One APScheduler job store shared by several processes.** The FAQ's answer is "Short answer:
  You can't" [10].
- **A host cron or a systemd timer that defers jobs into Procrastinate,** with
  `procrastinate defer --queueing-lock=... --ignore-already-enqueued`. Procrastinate's docs call it
  "perfectly valid" [5]. This file keeps the periodic task as the default for a service that runs
  Procrastinate workers, because it needs no second scheduler and the database already defers once
  per period [5]. On Kubernetes, the CronJob of section 2 is that route.
- **Temporal Cron Jobs.** Temporal's docs present Schedules as "a more flexible and user-friendly
  approach than Temporal Cron Jobs" [7], so a team on Temporal takes Schedules.

## 13. Security and personal data

What a scheduler puts into a message, and what a job may log, follow [delivery.md](delivery.md)
section 10. This section covers one more threat: write access to a schedule kept in a database,
as Celery's database schedulers, APScheduler's SQLAlchemy job store and DBOS keep it [2], [22],
[9]. Whoever can write that table can start tasks. With APScheduler's SQLAlchemy job store it can
also run code in the scheduler's process: the store writes each job with `pickle.dumps` and reads
it back with `pickle.loads` [22], and "It is possible to construct malicious pickle data which
will execute arbitrary code during unpickling" [23]. DBOS pickles its data by default too
([durable-workflows.md](durable-workflows.md) section 13). For Celery's database schedulers, no
owner text on guarding the table was found.

- **Keep APScheduler's jobs in memory in its one process, or in a job table that only the
  scheduler may write.** Why: a job read from the table is unpickled where the scheduler runs
  [22]. For DBOS, give its system database a role of its own, as
  [durable-workflows.md](durable-workflows.md) section 13 says.

## 14. Checks

- **Before a new schedule ships, ask: which processes can send this run?** The answer names one
  beat process, one CronJob, one APScheduler process, or the Procrastinate workers (section 3).
- **At review of a scheduled job, ask: what does it do when it runs twice for the same period?**
  (section 4).
- **At review of a scheduled job, ask: what does it do when it starts at the latest time its
  deadline allows?** (section 6).

## 15. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Kubernetes — Concepts: CronJob — https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/
- [2] Celery — User Guide: Periodic Tasks, 5.6.3 — https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html
- [3] Python Package Index — APScheduler project metadata (JSON API) — https://pypi.org/pypi/apscheduler/json
- [4] APScheduler — User guide, 3.11.3.post3 — https://apscheduler.readthedocs.io/en/3.x/userguide.html
- [5] Procrastinate — Launch a task periodically — https://procrastinate.readthedocs.io/en/stable/howto/advanced/cron.html
- [6] APScheduler — README — https://github.com/agronholm/apscheduler
- [7] Temporal — Schedule — https://docs.temporal.io/schedule — checked 2026-10-30
- [9] DBOS — Python tutorials: Scheduling Workflows — https://docs.dbos.dev/python/tutorials/scheduled-workflows
- [10] APScheduler — Frequently Asked Questions, 3.11.3.post3 — https://apscheduler.readthedocs.io/en/3.x/faq.html
- [11] Procrastinate — API Reference — https://procrastinate.readthedocs.io/en/stable/reference.html
- [12] APScheduler — `apscheduler.triggers.cron`, 3.11.3.post3 — https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html
- [13] Celery — User Guide: Configuration and defaults, 5.6.3 — https://docs.celeryq.dev/en/stable/userguide/configuration.html
- [14] basavakanaparthi-alation — Hourly crontab skips execution during fall-back DST transition (GitHub, celery/celery issue #10107, 2026; case) — https://github.com/celery/celery/issues/10107
- [15] APScheduler — `src/apscheduler/schedulers/base.py`, 3.11.3 — https://raw.githubusercontent.com/agronholm/apscheduler/3.11.3/src/apscheduler/schedulers/base.py
- [16] Celery — `celery/schedules.py`, v5.6.3 — https://raw.githubusercontent.com/celery/celery/v5.6.3/celery/schedules.py
- [17] Celery — `celery/beat.py`, v5.6.3 — https://raw.githubusercontent.com/celery/celery/v5.6.3/celery/beat.py
- [18] Procrastinate — Ensure jobs run sequentially and in order — https://procrastinate.readthedocs.io/en/stable/howto/advanced/locks.html — checked 2026-10-30
- [19] Procrastinate — Ensure tasks don't accumulate in the queue — https://procrastinate.readthedocs.io/en/stable/howto/advanced/queueing_locks.html — checked 2026-10-30
- [20] Procrastinate — Retry stalled jobs — https://procrastinate.readthedocs.io/en/stable/howto/production/retry_stalled_jobs.html
- [22] APScheduler — `src/apscheduler/jobstores/sqlalchemy.py`, 3.11.3 — https://raw.githubusercontent.com/agronholm/apscheduler/3.11.3/src/apscheduler/jobstores/sqlalchemy.py
- [23] Python — pickle: Python object serialization, Python 3.15.2 — https://docs.python.org/3/library/pickle.html
- [24] Kubernetes — Concepts: Jobs, Pod backoff failure policy — https://kubernetes.io/docs/concepts/workloads/controllers/job/#pod-backoff-failure-policy — checked 2026-10-30
- [25] Dramatiq — Cookbook, 2.2.0 — https://dramatiq.io/cookbook.html — checked 2026-10-30
