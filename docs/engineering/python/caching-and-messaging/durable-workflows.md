# Durable workflows

Rules for Python code that runs work of several steps on a durable-workflow engine, Temporal or
DBOS, so that the work goes on after a crash and stays correct when a step runs twice.

**Navigation**

- [1. Purpose and scope](#1-purpose-and-scope)
- [2. When an engine is too much, and the simpler way](#2-when-an-engine-is-too-much-and-the-simpler-way)
- [3. Which engine](#3-which-engine)
- [4. Workflow code is deterministic](#4-workflow-code-is-deterministic)
- [5. Steps run more than once: make them idempotent](#5-steps-run-more-than-once-make-them-idempotent)
- [6. Retries: decide them where you call the step](#6-retries-decide-them-where-you-call-the-step)
- [7. Changing workflow code that is running](#7-changing-workflow-code-that-is-running)
- [8. Schedules inside the engine](#8-schedules-inside-the-engine)
- [9. Rules that hold only under a condition](#9-rules-that-hold-only-under-a-condition)
- [10. Common mistakes](#10-common-mistakes)
- [11. Where the rules stop holding](#11-where-the-rules-stop-holding)
- [12. Alternatives considered](#12-alternatives-considered)
- [13. Security and personal data](#13-security-and-personal-data)
- [14. Checks](#14-checks)
- [15. Sources](#15-sources)

## 1. Purpose and scope

Some work has several steps that depend on each other, each with an effect in another system:
charge a card, then book a shipment, then send a receipt, or wait a day for an answer. When the
process that runs it crashes half-way, the work must go on from where it stopped, not start again
and not stop. A durable-workflow engine does this. Temporal calls itself "a scalable and reliable
runtime for durable function executions called Temporal Workflow Executions" [1]. DBOS is a
library that keeps the same state in PostgreSQL: "There's no separate orchestration server and no
infrastructure required besides Postgres" [2]. Both record the result of each step and rebuild a
workflow's state by running its code again [3]: "A Workflow Definition must be deterministic
because the Temporal Server may replay your Workflow to reconstruct its state" [4].

This file is for a programmer who writes workflows and their steps in Python. Two words carry it:

- **Workflow**: the code that decides which step runs next. It does no work of its own in other
  systems.
- **Step**: a unit that does the work, such as a database write or an HTTP call. Temporal calls
  it an Activity; DBOS calls it a step.

**The one rule:** workflow code decides only from its inputs and from the step results the engine
recorded, and every step that changes another system is written so that a second run changes
nothing more. Section 4 holds the first half, section 5 the second.

The rules every job shares (delivery at least once, idempotent consumers, retries, dead letters,
security of messages) are in [delivery.md](delivery.md); this file keeps what is specific to the
two engines. Out of scope on purpose: running the engine's servers (clustering, upgrades,
capacity), and data pipeline orchestration (Airflow, Dagster, Prefect).

Not covered yet, because the research found no source for them:

- **An owner's statement of when an engine is too much.** Neither Temporal's docs nor DBOS's give
  one, so section 2 rests on a vendor's comment and on cases.
- **An independent test of Temporal or DBOS.** Jepsen's list of analyses has neither; it does hold
  Orkes Conductor, another workflow engine [5] (section 5).
- **Testing workflow code** with each engine's own test tools, and **how DBOS handles a change to
  workflow code that is still running**. The research did not cover them.
- **How Temporal treats a second start with the same workflow ID** (section 5).
- **How many teams use each engine.** The surveys do not ask, and downloads include CI runs
  (section 3).

## 2. When an engine is too much, and the simpler way

**Before you add an engine, ask whether one database transaction can hold the whole job; when it
can, put the job on a task queue with retries.** Reason: an engine adds a server or a library, the
rules of sections 4 and 7, and a second place where the state of the work lives.

Alexander Belanger, a co-founder of Hatchet, puts the test this way: "If your entire async job can
be modeled as a single database transaction, you don't need a durable execution platform, you
need a task queue with retries" [6], [7]. It is his view, and a vendor's: in the same comment he
argues for Hatchet's own design, where the task queue comes first and durable execution is a
feature for more complex work [6]. Neither Temporal nor DBOS says in its docs when its tool is too
much, so there is no owner's rule to set beside his.

The signs that a project needs an engine, from the two cases in this research that moved to one
(both tied to Temporal, as section 3 says):

- **Jobs that depend on other jobs, several levels deep, and jobs that run for days.** Vantage, a
  Rails application that runs roughly 25 million jobs a day, moved from Sidekiq to Temporal and
  names "numerous long-running processes that can take over a day to complete" [8].
- **Background jobs that grew into orchestration.** FireHydrant writes that its runbook
  automation "evolved from simple background jobs into complex, stateful orchestration" [9].

The simpler ways:

- A job of one step, or of steps that fit in one transaction, goes on a task queue:
  [task-queues.md](task-queues.md).
- A team that already runs Temporal can run a single job as a Standalone Activity, with no
  workflow around it: "Use a Standalone Activity to run one Activity" [10].

## 3. Which engine

| Tool (Python client) | Use it when | Too much, or the risk |
|---|---|---|
| Temporal (`temporalio` 1.35.0) | The work has several dependent steps with effects in other systems, long waits, or runs for days [8], [9], and the team can run a server or pay for the cloud service. | Running it yourself needs a database, its only required dependency [11], and a visibility store: Elasticsearch and OpenSearch are each "Recommended for any setup that spawns more than a few Workflow Executions" [37]. The cloud service bills per Action: "Actions are the primary billing unit" [12]. The rules of sections 4 and 7. |
| DBOS (`dbos` 3.4.0) | The same need, and the application already has PostgreSQL: DBOS runs as a library in your process, with no orchestration server [2]. It recovers workflows by itself on one node; across nodes, it needs Conductor or recovery by hand [2]. | Young: its downloads, CI runs included, went from about 15,000 a day (April 8 to 30, 2026) to about 91,000 a day in September, about six times as many [13], and one contributor account made 400 of the commits, about 5.2 times the next one (77) [14]. Its control plane, Conductor, is proprietary when you host it yourself (section 9). The rules of section 4. |

When both rows fit, the number of nodes decides: on one node DBOS recovers its workflows at
startup, while across nodes it needs Conductor, whose production use requires a paid licence key,
or recovery by hand [2], [38]; a team that wants neither runs Temporal.

Versions checked: `temporalio` 1.35.0 and `dbos` 3.4.0, both released on 2026-10-28 under the MIT
licence, for Python 3.10 or newer [15], [16]. The download count of `temporalio` may count installs
that come through another package: `openai-agents` 0.24.0 lists `temporalio==1.34.0` as its
optional `temporal` extra [17].

### Temporal's cost and its rules, against the work it saves

Teams weigh three costs against what Temporal does for them.

- **The rules.** Workflow code must be deterministic, and code that is running changes only
  through a patch or a new worker version (sections 4 and 7). DBOS asks the same of its workflows:
  "a workflow function must be deterministic" [3]. So the rules come with replay, in both engines.
  They are a reason to keep one-step work on a task queue (section 2), not a reason to pick one
  engine over the other.
- **The bill.** Temporal Cloud bills per Action: "Pricing starts at $50 per million Actions" [12].
  At Daylight, whose detection engine runs on Temporal, "Each new customer materially increased
  our Temporal Cloud bill", with schedules as the main driver, and "workflow inputs, outputs, and
  state transitions traverse external infrastructure" [18]. Daylight kept Temporal: "We decided to
  move to a self-hosted Temporal cluster", on Aurora PostgreSQL and OpenSearch, with a platform
  team that had run self-hosted Temporal before [18].
- **The fit.** Nango could never use Temporal's main feature, resuming failed workflows, largely
  because it runs untrusted user code. That left Temporal "a pretty expensive and complex queuing
  and scheduling system" for Nango, and "The dependency on Temporal has also become an increasing
  barrier to adoption by our Enterprise customers" [19]. Nango replaced it with a queue and a
  scheduler on PostgreSQL, "~300 lines of Typescript" [19].

On the other side, Vantage and FireHydrant moved work to Temporal for the reasons section 2 lists
[8], [9]. Vantage says the time it takes "to fully grasp Temporal's execution model" is paid back by
"the long-term benefits for handling stateful Workflows and easy job restarts" [8]. Both are tied
to Temporal: Vantage writes "We even recently announced an integration for ingesting Temporal
Cloud costs" [8], and FireHydrant writes "We've been huge fans of Temporal for a while" and links a
Temporal case study about itself [9].

**The answer this practice takes.** Temporal earns its cost when the work needs what only replay
gives: several dependent steps with effects in other systems, long waits, and a resume after a
crash. A team that would use it only as a queue and a scheduler, as Nango did, gets the same from
a task queue for less. When the cloud bill grows with each customer, running Temporal yourself is
the path Daylight took, and it needs a team that can run a server, its database and a visibility
store (the table above). These are four cases, two of them tied to Temporal and one written by a company
about its own replacement; they show what can happen, not how often.

### Named once, not described

- **Hatchet.** Its server is still before 1.0, at v0.114.2 [20], and two concurrency bugs were
  open on 2026-10-30: single-task workflows release their concurrency slot during retry backoff
  [21], and a round-robin group admits more runs than its limit on a cold engine [22].
- **Restate.** Its server is under the Business Source License 1.1, whose change date to the
  Apache License 2.0 is four years after release [23]. The licence's grant forbids only a "Public
  Restate Platform Service", and explicitly permits "Any type of production deployment of Restate
  that is invoking services or workflows written by the Licensee" [23], so a team can run it for
  its own workflows. It is not described because this job's two tools are taken: Temporal is the
  engine with a server, and its server is under the MIT licence [40]; DBOS is the library on
  PostgreSQL.
- **Inngest.** Its server is under the Server Side Public License, with a grant of the Apache
  License 2.0 that takes effect on the third anniversary of the date the software is made
  available [24]. Its Python SDK marks its step decorator "(experimental)" and its realtime
  feature "(beta)", and says "Some features are TypeScript-only for now" [25].

## 4. Workflow code is deterministic

**When you write workflow code, make it take the same path every time it runs with the same inputs
and the same step results: no clock, no random number, no network call and no file read inside
it.** Reason: the engine runs the code again to rebuild its state, and code that takes another path
on the second run breaks the workflow.

Temporal: "A Workflow Definition must be deterministic to support replay" [26]. Its Python docs
list what that rules out: "no threading", "no randomness", no calls to outside processes, "no
network I/O", no change to global state and "no system date or time" [4]. DBOS states the same for
its workflows [3], and says where the rest goes: "You should make a function a step if you're
using it in a DBOS workflow and it performs a nondeterministic operation" [27].

What a Temporal workflow uses instead: `workflow.now()` for the time, `workflow.random()` for a
random number and `workflow.uuid4()` for a UUID [4]. For `workflow.now()`, "The SDK returns the time
of the last Workflow Task, which is consistent across replays" [4]. Everything else that reads or
changes the world, a database query, an HTTP call, a file, is a step (section 5).

Bad: the system clock in workflow code.

```python
paid_at = datetime.now(UTC)
```

A replay reads a new time, so a workflow that compares or stores it takes another path on the
second run.

Good: the time of the workflow task.

```python
paid_at = workflow.now()
```

It fixes the clock read above: every replay gets the same value, so the path does not change.

A workflow that charges an invoice and sends a receipt, in the worker's adapter folder
([file-structure.md](../../any-language/file-structure/file-structure.md) section 5):

```python
# src/acme/worker/workflows_settle_invoice.py
# The file holds workflows only, with no other side effects.
# A departure from file-structure.md section 5, one file per module, named for the
# role and the module: a workflow file is named for the workflow it runs, which
# calls the activities of several modules. The cost: the file maps to no one module.
from datetime import timedelta
from typing import Final

from temporalio import workflow
from temporalio.common import RetryPolicy

# Passed through: the sandbox would import them again on every run (section 4).
with workflow.unsafe.imports_passed_through():
    from acme.billing.charge_invoice.schemas import SettleInvoiceRequest
    from acme.core.schemas import PaymentId, Receipt
    from acme.worker.activities_charge_invoice import ChargeInvoice
    from acme.worker.activities_send_receipt import SendReceipt

# The policy allows five attempts, then the workflow gets the error: the default
# never stops (section 6).
# The wait is written too, at Temporal's defaults (delivery.md section 5).
STEP_RETRY_POLICY: Final = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=100),
    maximum_attempts=5,
)


@workflow.defn
class SettleInvoice:
    @workflow.run
    async def run(self, request: SettleInvoiceRequest) -> PaymentId:
        payment_id = await workflow.execute_activity_method(
            ChargeInvoice.charge_invoice,
            request,
            # This bounds one attempt; the SDK requires a timeout on every activity
            # call.
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=STEP_RETRY_POLICY,
        )

        receipt = Receipt(
            invoice_id=request.invoice_id,
            payment_id=payment_id,
            # The engine recorded this time, the same on every replay (section 4).
            paid_at=workflow.now(),
        )
        await workflow.execute_activity_method(
            SendReceipt.send_receipt,
            receipt,
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=STEP_RETRY_POLICY,
        )

        return payment_id
```

It is good because the workflow only orders the steps: the charge and the receipt run in
activities, the one clock read is `workflow.now()`, and the input is a typed model that the client's
Pydantic converter carries (section 9). Every activity call states its timeout, which the SDK
requires ("At least one of `start_to_close_timeout` or `schedule_to_close_timeout` must be
provided" [28]), and its retry limit, which the default leaves open (section 6). The modules it
imports pass through the sandbox, as the next part says.

### The Python sandbox catches some of it, not all (Temporal)

The SDK runs workflow code in a sandbox that throws an error when the code makes a call known to
be non-deterministic [28]. Its README warns: "The sandbox is not foolproof and non-determinism can
still occur" [28]. The default restrictions stop "most dangerous standard library calls", and some
calls, such as reading a file with `open` or reading `os.environ`, run while a module is imported
[28]. So the rule above is yours to keep; the sandbox is a net under it.

- **Define each workflow in a file with no other side effects, and import activities and model
  types inside `workflow.unsafe.imports_passed_through()`.** Reason: the sandbox imports the
  workflow's file again on every run and reloads every module it does not pass through. The README
  asks users "to define their workflows in files with no other side effects" and to "pass through
  all third party modules whose calls will be deterministic", including the modules that hold
  activities and Pydantic models [28].
- **Never turn the sandbox off.** It can be turned off for a block (`sandbox_unrestricted()`), for
  a workflow (`sandboxed=False`) or for a worker (`UnsandboxedWorkflowRunner()`) [28], and
  "Skipping Workflow Sandboxing results in a lack of determinism checks" [29]. Reason: those checks
  are the only warning before a replay fails in production.

## 5. Steps run more than once: make them idempotent

**When you write an activity or a DBOS step that changes another system, make a second run of it
change nothing more than the first, with a key that stays the same on every attempt, such as the
invoice id.** How a consumer checks such a key, in the same transaction as its effect, is
[delivery.md](delivery.md) section 3. Reason: the engine runs a step again whenever it does not
learn that the step finished.

- **Temporal.** "Because Activities may be retried, these functions may be executed more than
  once" [30]. An activity is recorded only when it returns or fails, and "If an Activity fails to
  report to the server at all, it will be retried" [30]. The page also says "Temporal guarantees
  that the Activity will be observed as completed exactly once" [30]: that is the result the
  workflow sees, not how often the code ran. Temporal's own example of why it matters: "A payment
  processing system must charge the customer only once for a given purchase" [30].
- **DBOS.** "Steps are tried at least once but are never re-executed after they complete" [3]. A
  step that fails half-way and is retried does its first half again.
- **Neither engine tells you.** "The lack of idempotency might affect the correctness of your
  application but does not affect the Temporal Platform" [30]: a double charge shows up in your
  data, not as an error.

The activities of the workflow in section 4. Each step is one business operation, so each has a
module of its own, `billing/charge_invoice/` and `billing/send_receipt/`, whose `usecase.py` holds
its one entry point ([file-structure.md](../../any-language/file-structure/file-structure.md)
section 3). Each activity sits in a file named for its module and is a method of a class, so the
client comes in as a parameter (the README: "Activities can be methods of a class" [28]):

```python
# src/acme/worker/activities_charge_invoice.py
from temporalio import activity

from acme.billing.charge_invoice import usecase
from acme.billing.charge_invoice.schemas import SettleInvoiceRequest
from acme.core.payments_client import PaymentsClient
from acme.core.schemas import PaymentId


class ChargeInvoice:
    # main.py builds the client once and passes it in (file-structure.md section 4).
    def __init__(self, payments: PaymentsClient) -> None:
        self._payments = payments

    @activity.defn
    async def charge_invoice(self, request: SettleInvoiceRequest) -> PaymentId:
        # The use case sends the invoice id as the idempotency key: a retry after a
        # lost report finds the first charge, not a second one (section 5).
        return await usecase.charge_invoice(self._payments, request)
```

```python
# src/acme/worker/activities_send_receipt.py
from temporalio import activity

from acme.billing.send_receipt import usecase
from acme.core.mail_client import MailClient
from acme.core.schemas import Receipt


class SendReceipt:
    # main.py builds the client once and passes it in (file-structure.md section 4).
    def __init__(self, mail: MailClient) -> None:
        self._mail = mail

    @activity.defn
    async def send_receipt(self, receipt: Receipt) -> None:
        await usecase.send_receipt(self._mail, receipt)
```

It is good because each activity is a thin adapter in the file of the module it offers: it takes
the client it was given, calls that module's one entry point and holds no business rule
([file-structure.md](../../any-language/file-structure/file-structure.md) section 5). The shapes
two modules take sit in `core/schemas.py`
([file-structure.md](../../any-language/file-structure/file-structure.md) section 4): `PaymentId`
comes out of `charge_invoice` and goes into `send_receipt`, and `Receipt` goes into `send_receipt`
and into the `email_receipt` module of section 7. Only `charge_invoice` takes
`SettleInvoiceRequest`, so it stays in that module's `schemas.py`. The key that makes the charge
safe to repeat is the invoice id, which is the same on every attempt.

**Start a DBOS workflow with an ID built from the business key.** Reason: "An assigned workflow ID
acts as an idempotency key", so "if a workflow is called multiple times with the same ID, it
executes only once" [3]. How Temporal treats a second start with the same workflow ID was not
part of this research.

```python
# src/acme/worker/workflows_charge_invoice.py
from dbos import DBOS, DBOSConfiguredInstance, SetWorkflowID

from acme.core.payments_client import PaymentsClient
from acme.core.schemas import InvoiceId, PaymentId


# SettleInvoice is a class, so the client comes in as a parameter: DBOS records the
# instance's name to find it again when it recovers a workflow.
@DBOS.dbos_class()
class SettleInvoice(DBOSConfiguredInstance):
    # main.py builds the client once and passes it in, before DBOS launches
    # (file-structure.md section 4).
    def __init__(self, payments: PaymentsClient) -> None:
        super().__init__("settle-invoice")
        self._payments = payments

    # DBOS retries no step unless told to; this one calls the payment provider
    # (section 6). The wait is written too, at DBOS's defaults (delivery.md section 5).
    @DBOS.step(
        retries_allowed=True, interval_seconds=1.0, max_attempts=5, backoff_rate=2.0
    )
    def charge_invoice(self, invoice_id: InvoiceId, amount_cents: int) -> PaymentId: ...

    @DBOS.workflow()
    def settle_invoice(self, invoice_id: InvoiceId, amount_cents: int) -> PaymentId:
        return self.charge_invoice(invoice_id, amount_cents)


def start_settlement(
    settlement: SettleInvoice, invoice_id: InvoiceId, amount_cents: int
) -> PaymentId:
    # The workflow ID is the idempotency key: a second start for one invoice runs once.
    with SetWorkflowID(f"settle-invoice-{invoice_id}"):
        return settlement.settle_invoice(invoice_id, amount_cents)
```

The step's body is cut; like the Temporal activity, it calls the module's use case with the client
the class was given, and the use case sends the invoice id to the provider as the idempotency key.
It is good because both halves of the rule are visible: the step that calls another system turns
its retries on and states how many and how long it waits, and the workflow starts under an ID that
a second request for the same invoice repeats. The client comes in as a parameter, as in the
Temporal half ([readability.md](../../any-language/readability/readability.md) section 6): DBOS's
base class is for "DBOS functions that access instance state", and DBOS records the instance's
name to find the instance when it recovers a workflow [42]. `main.py` builds the instance once,
before DBOS launches, because "All configured instances should be instantiated before DBOS is
launched" [42]. The file is named for the one module it calls
([file-structure.md](../../any-language/file-structure/file-structure.md) section 5).

**An engine still delivers at least once.** Jepsen tested Orkes Conductor 5.3.2 to 5.5.0-rc2, in
work Orkes paid for ("This research was funded by Orkes Inc."), and found that "healthy Conductor
clusters occasionally executed the same task for the same workflow execution on two workers
concurrently" [31]. Orkes reports that issue fixed in 5.5.6; abandoned and missing workflows were
fixed in 5.5.0, and two issues, null workflow IDs after a Redis crash and an aborted read, were
still unresolved [31]. Jepsen adds that the concurrent runs are "not surprising, since mutual
exclusion is impossible in asynchronous networks" [31]. So a step stays idempotent whatever the
engine promises.

## 6. Retries: decide them where you call the step

The two engines start from opposite defaults, which [delivery.md](delivery.md) section 5 sets side
by side.

**When you call a Temporal activity, pass a `RetryPolicy` with `maximum_attempts` and the wait
between attempts; on every DBOS step, set `retries_allowed`, and on one that retries, also
`max_attempts` and the wait.** Reason: Temporal's default never gives up ("If 0, the default,
there is no maximum" [33]), so an activity that can never succeed keeps trying; DBOS's default
never retries, so a short network error in a step is not tried again at all. The wait is written
even at its default ([delivery.md](delivery.md) section 5).

The fields the rule sets, each written even at its default
([delivery.md](delivery.md) section 5):

| Field | What it means | Set it when | Leave it out when |
|---|---|---|---|
| `maximum_attempts` (Temporal `RetryPolicy`) | Attempts in total; `0` means no maximum [33]; default: [delivery.md](delivery.md) section 5 | Always, on every activity call | Never: the research found no case where the open default is right |
| `initial_interval`, `backoff_coefficient`, `maximum_interval` (Temporal `RetryPolicy`) | The wait: `initial_interval` before the first retry, each wait `backoff_coefficient` times the last, and at most `maximum_interval` [33] | Always, the default's value included ([delivery.md](delivery.md) section 5) | Never |
| `non_retryable_error_types` (Temporal `RetryPolicy`) | Names of error types that end the retries at once [33] | The activity can raise an error that no retry fixes | Every error the activity raises may pass on a later attempt |
| `retries_allowed` (DBOS step) | Whether the step retries at all [27]; default: [delivery.md](delivery.md) section 5 | Always, on every step, the default's value included ([delivery.md](delivery.md) section 5): `True` for a step that calls another system that can fail for a moment, `False` for one that fails only on bad input, which a retry repeats | Never |
| `max_attempts` (DBOS step) | Attempts in total once retries are allowed [27]; default: [delivery.md](delivery.md) section 5 | Always when `retries_allowed=True`, the defaults' values included ([delivery.md](delivery.md) section 5) | `retries_allowed=False` |
| `interval_seconds`, `backoff_rate` (DBOS step) | The wait: `interval_seconds` before the first retry, then exponential backoff at `backoff_rate` [27] | Always when `retries_allowed=True`, the defaults' values included ([delivery.md](delivery.md) section 5) | `retries_allowed=False` |

## 7. Changing workflow code that is running

**When you change workflow code while workflows of the old version are still running, put the
change behind `workflow.patched()` or roll it out with Worker Versioning.** Reason: a worker replays
an old workflow's history against the new code, and without one of the two "you are likely to cause
a nondeterminism error" [34].

"A Patch defines a logical branch in a Workflow for a specific change, similar to a feature flag"
[34]. Patching has three steps: add the new code under `patched()` and run it beside the old code;
once the workflows started on the old code have left retention, remove the old code and mark the
patch with `deprecate_patch()`; when no open workflow of the previous version is left, remove that
call too [34]. Worker Versioning, the other way, "allows you to tag your Workers and
programmatically roll them out in Deployment Versions" [34].

The receipt step of section 4, moved to a new `email_receipt` activity. The new activity does a
different job from `send_receipt`, so it calls the entry point of a module of its own,
`billing/email_receipt/`, and sits in `activities_email_receipt.py`; the workflow file imports its
class with the others. The fragment takes the place of the receipt call in `run`, and the rest of
`run` is unchanged:

```python
        # Runs started before this deploy replay the old branch (section 7).
        if workflow.patched("receipt-by-email"):
            await workflow.execute_activity_method(
                EmailReceipt.email_receipt,
                receipt,
                start_to_close_timeout=timedelta(minutes=1),
                retry_policy=STEP_RETRY_POLICY,
            )
        else:
            await workflow.execute_activity_method(
                SendReceipt.send_receipt,
                receipt,
                start_to_close_timeout=timedelta(minutes=1),
                retry_policy=STEP_RETRY_POLICY,
            )
```

It is good because a run that started before the change replays the branch it recorded, a new run
takes the new one, and the patch ID names the change so the later `deprecate_patch()` call can
find it.

## 8. Schedules inside the engine

Schedules, and the rules for missed, late and overlapping runs and for time zones, are in
[scheduled-jobs.md](scheduled-jobs.md), which names the engines' own schedules once and does not
describe them.

## 9. Rules that hold only under a condition

**When you use Temporal Cloud.** Count the Actions your workflows will take before you move them,
and split them into namespaces by domain when one namespace would carry them all. Reason: the
service bills per Action [12], and at Vantage, where all new workflows went into one production
namespace, "we approached rate limits in our single namespace", made worse by aggressive worker
retries; the team moved to one namespace per domain, sized by the Activities each would run [8].

**When workflow inputs are Pydantic models.** Set the SDK's Pydantic data converter on the client:
"To use Pydantic model instances, install Pydantic and set the Pydantic data converter when
creating client instances" [28]. Reason: a workflow input leaves the process in a fixed shape, so
it is a Pydantic model ([python.md](../language/python.md) section 4), and the client must know how
to carry it. Section 13 shows the client.

**When you run DBOS in production.** Decide before the first deploy whether you use Conductor, its
control plane. DBOS does not need it to run workflows: "Conductor is off your workflows
orchestration path", and if the connection to it breaks, the application "will continue to operate
normally" [2]. DBOS still writes "we strongly recommend connecting your application to Conductor"
[2]. Conductor is what recovers a workflow on another healthy executor when its own executor
crashes, and it gives the dashboards and the controls to pause workflows and start stopped ones
[2]. The library is MIT [16], but "Self-hosted Conductor is released under a proprietary license",
and "Commercial or production use of DBOS Conductor or the DBOS Console requires a paid license
key" [38]. Reason: recovery on another executor and the dashboards come from Conductor, so a
project that picked DBOS to avoid running or paying for a server must know before production
whether it needs them.

## 10. Common mistakes

Each of these is named in the owners' docs or in a case above.

- **The clock, a random number or a network call in workflow code.** It is ordinary Python, so it
  looks harmless, and a test that runs the workflow once does not show it. On replay it takes
  another path. Temporal's docs forbid each of them in workflow code [4]. The fix and its BAD and GOOD are
  in section 4.
- **A change to workflow code deployed while old workflows run.** The diff looks like any other
  change; without a patch or a new worker version it is "likely to cause a nondeterminism error"
  [34]. The fix is section 7.
- **Reading "observed as completed exactly once" as a promise that the code runs once.** The
  sentence is on Temporal's own page [30], and it describes the result the workflow sees. The code itself may run more than
  once, and a payment step that is not idempotent charges twice [30]. The fix is section 5.
- **Turning the sandbox off.** The docs name three ways to do it and say each one removes the
  determinism checks [29]. Pass the module through instead (section 4).
- **Taking DBOS step retries as on.** They are off unless `retries_allowed=True` [27]; a step that
  calls another system fails on its first short error. The fix is section 6.
- **An engine used only as a queue and a scheduler.** Nango paid for replay it could not use and
  called the result "a pretty expensive and complex queuing and scheduling system" [19]. The fix is
  section 2.
- **All workflows in one Temporal Cloud namespace.** Vantage neared the namespace's rate limits
  [8]. The fix is section 9.

## 11. Where the rules stop holding

- **Determinism binds workflow code only.** Steps may read the clock, call the network and use
  random numbers; that is what they are for [27].
- **Idempotency is not needed where a repeat does no harm.** Temporal's page gives the case: "if
  you have a monotonically incrementing counter, you might not care that retries increment the
  counter" [30].
- **A job that fits one database transaction needs no engine** (section 2).
- **The rules are written for Temporal and DBOS.** Another engine has its own replay, sandbox and
  retry rules; read its docs before you carry these over.

## 12. Alternatives considered

- **Hatchet, Restate and Inngest.** Named once in section 3, with the reason each is not
  described.
- **A queue and a scheduler of your own on PostgreSQL**, as Nango built [19]. It fits work that
  needs a queue and a schedule and none of replay; for that work this practice points to a
  PostgreSQL queue that already exists, in [task-queues.md](task-queues.md), instead of a new one.
- **A Standalone Activity instead of a workflow**, for a team already on Temporal with a job of one
  step [10]. It is the simpler way of section 2, not a third engine.

## 13. Security and personal data

This section covers six threats: an engine credential that leaks, a connection to the engine
without TLS, a self-hosted Temporal Service that lets every client in, a row in DBOS's system
database that runs code when DBOS reads it, personal data kept in the engine's store, and a
licence check that calls out at startup. Securing the engine's own servers is out of scope, as
running them is. The rules every job shares, such as TLS and authentication to a broker and
personal data in messages, are [delivery.md](delivery.md) section 10.

- **The engine's credentials come from the settings class.** The Temporal API key, the DBOS
  database password and the Conductor key are fields of the application's `Settings`, each secret
  a `SecretStr` read where its client is built ([python.md](../language/python.md) section 5). DBOS's
  own example reads `DBOS_SYSTEM_DATABASE_URL` and `DBOS_CONDUCTOR_KEY` with `os.environ.get`
  [38]; take both from `Settings` instead. The system database URL carries the password, so build
  it from the separate fields in the code that builds the DBOS config, and never log it
  ([logging.md](../logging/logging.md) section 10).
- **TLS is set, not left to the default.** `Client.connect` turns TLS on by itself when an API key
  is passed and leaves it off otherwise [39]; pass `tls=True` for any server off your machine.
- **On a self-hosted Temporal Service, connect with a client certificate, and do not count on an
  API key there.** Temporal's security page: "If you do not explicitly configure an Authorizer,
  Temporal uses the default noopAuthorizer." and "This default allows every API request, with no
  authentication or access control." [44] Its operators limit the clients through mTLS to
  "certificates issued by a specific Certificate Authority (CA)" [44]; pass the client
  certificate through `tls=TLSConfig(...)`, where the client below passes `tls=True` [39].
  Setting up the server's mTLS and its Authorizer is running the server, which stays out of
  scope.
- **Give DBOS's system database a role of its own, and grant write on it to the DBOS application
  only.** DBOS 3.4.0 stores workflow data with pickle unless its config names another serializer:
  its `DefaultSerializer` calls `pickle.dumps` and `pickle.loads`, and DBOS takes it when the
  config sets none [41], [42]. Python's docs warn that "It is possible to construct malicious
  pickle data which will execute arbitrary code during unpickling" [43], so whoever can write that
  database can run code in every DBOS process that reads the row. A JSON serializer does not close
  it: DBOS still unpickles a stored row marked `py_pickle`, whatever serializer the config names
  [41].
- **Workflow data is kept by the engine.** Temporal's database holds "An append-only log of
  Workflow Execution History Events" [11], and with Temporal Cloud "workflow inputs, outputs, and
  state transitions traverse external infrastructure" [18]. The SDK's payload codecs "convert bytes
  to bytes (e.g. for compression or encryption)" [28]. What may travel in an input is
  [delivery.md](delivery.md) section 10; Daylight's answer for sensitive data was to self-host, so
  that "no workflow data leaves our network boundary" [18].
- **A self-hosted Conductor calls out at startup.** "Conductor validates its license key against
  https://cloud.dbos.dev at startup and exits if it cannot reach it"; "For air-gapped deployments,
  contact sales" [38]. Allow that call, or plan for it, before the first production start.

The client for Temporal Cloud, which the worker's `main.py` builds once from three `Settings`
fields; on a self-hosted service it passes `tls=TLSConfig(...)` with the client certificate
instead (the bullet above):

```python
# src/acme/core/temporal_client.py
from pydantic import SecretStr
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter


async def connect_temporal(
    target_host: str, namespace: str, api_key: SecretStr
) -> Client:
    return await Client.connect(
        target_host,
        namespace=namespace,
        # The key is unwrapped only where the client is built (python.md section 5).
        api_key=api_key.get_secret_value(),
        # TLS is stated, not left to the default, which turns it off when no key is
        # passed.
        tls=True,
        # Workflow inputs are Pydantic models (section 9).
        data_converter=pydantic_data_converter,
    )
```

It is good because the key stays a `SecretStr` until the one line that hands it to the SDK, the
function takes plain values that a test can pass, it sits in the one client file for the system
([file-structure.md](../../any-language/file-structure/file-structure.md) section 4), and TLS and the
converter are stated where a reader of the call sees them.

## 14. Checks

- `grep -rnE "datetime\.(now|utcnow)|time\.time\(|random\.|uuid\.uuid4|httpx|requests" src/acme/worker/workflows_*.py`
  prints nothing: no clock, randomness or network call in workflow files (section 4).
- `grep -rnE "UnsandboxedWorkflowRunner|sandboxed=False|sandbox_unrestricted" src/` prints nothing
  (section 4).
- At review of an activity call: does its `retry_policy` set `maximum_attempts` and the wait
  (section 6)?
- At review of a DBOS step: does its decorator set `retries_allowed` (section 6)?
- At review of a DBOS step that retries: does its decorator also set `max_attempts` and the wait
  (section 6)?
- At review of the DBOS setup: is the DBOS application the only role that may write to DBOS's
  system database (section 13)?
- Before a deploy that changes workflow code: do workflows of the old version still run, and is
  the change behind `workflow.patched()` or a new worker version? (section 7)

## 15. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Temporal — What is Temporal? — https://docs.temporal.io/temporal
- [2] DBOS — DBOS Architecture — https://docs.dbos.dev/architecture
- [3] DBOS — Workflows, Python tutorial — https://docs.dbos.dev/python/tutorials/workflow-tutorial
- [4] Temporal — Workflow basics, Python SDK — https://docs.temporal.io/develop/python/workflows/basics
- [5] Jepsen — Analyses — https://jepsen.io/analyses
- [6] Alexander Belanger — comment in the thread "How to think about durable execution" (Hacker News, 2025; opinion; the author is a co-founder of Hatchet, which sells a durable task queue) — https://news.ycombinator.com/item?id=46328355
- [7] Alexander Belanger — How to think about durable execution (Hatchet blog, 2025; opinion; Hatchet's own blog) — https://hatchet.run/blog/durable-execution — checked 2026-10-30
- [8] Danielle V. and Emily D. — Why and How We Migrated from Sidekiq to Temporal (Vantage blog, 2025; case; Vantage sells an integration for Temporal Cloud costs) — https://www.vantage.sh/blog/sidekiq-vs-temporal
- [9] David Haley — Sidekiq to Temporal: a zero-downtime migration strategy (FireHydrant blog, 2026; case; FireHydrant is the subject of a Temporal case study) — https://firehydrant.com/blog/sidekiq-to-temporal-a-zero-downtime-migration-strategy/
- [10] Temporal — Job queues — https://docs.temporal.io/evaluate/features/job-queue
- [11] Temporal — Persistence — https://docs.temporal.io/temporal-service/persistence
- [12] Temporal — Temporal Cloud: Overview — https://docs.temporal.io/cloud/overview
- [13] pypistats — dbos, downloads per day (overall) — https://pypistats.org/api/packages/dbos/overall
- [14] GitHub — dbos-inc/dbos-transact-py, contributors (API) — https://api.github.com/repos/dbos-inc/dbos-transact-py/contributors
- [15] PyPI — temporalio, 1.35.0 — https://pypi.org/project/temporalio/1.35.0/ — checked 2026-10-30
- [16] PyPI — dbos, 3.4.0 — https://pypi.org/project/dbos/3.4.0/ — checked 2026-10-30
- [17] PyPI — openai-agents, 0.24.0 — https://pypi.org/project/openai-agents/0.24.0/
- [18] Alon Gluzman and Guy Grinberg — How We Migrated Off Temporal Cloud Without Downtime (Daylight blog, 2026; case) — https://daylight.ai/blog/how-we-migrated-off-temporal-cloud-without-downtime
- [19] Robin Guldener — Migrating from Temporal to a Postgres-based task orchestrator (Nango blog, 2026; case; Nango sells an integration platform, and the replacement is its own open-source code) — https://nango.dev/blog/migrating-from-temporal-to-a-postgres-based-task-orchestrator/
- [20] Hatchet — Hatchet, release v0.114.2 — https://github.com/hatchet-dev/hatchet/releases/tag/v0.114.2 — checked 2026-10-30
- [21] Scalahansolo — Single-task workflows release workflow-level concurrency during retry backoff, issue #5254 (GitHub, hatchet-dev/hatchet, 2026; case) — https://github.com/hatchet-dev/hatchet/issues/5254 — checked 2026-10-30
- [22] iblaine — RunGroupRoundRobin computes concurrency capacity positionally, admitting more than maxRuns on a cold engine, issue #4778 (GitHub, hatchet-dev/hatchet, 2026; case) — https://github.com/hatchet-dev/hatchet/issues/4778 — checked 2026-10-30
- [23] Restate — LICENSE (Business Source License 1.1) — https://github.com/restatedev/restate/blob/main/LICENSE
- [24] Inngest — LICENSE.md (Server Side Public License 1.0) — https://github.com/inngest/inngest/blob/main/LICENSE.md
- [25] Inngest — Python SDK, Inngest reference — https://www.inngest.com/docs/reference/python — checked 2026-10-30
- [26] Temporal — Temporal Workflow Definition — https://docs.temporal.io/workflow-definition
- [27] DBOS — Steps, Python tutorial — https://docs.dbos.dev/python/tutorials/step-tutorial
- [28] Temporal — Temporal Python SDK, README — https://github.com/temporalio/sdk-python/blob/main/README.md
- [29] Temporal — Temporal Python SDK sandbox environment — https://docs.temporal.io/develop/python/python-sdk-sandbox
- [30] Temporal — Activity Definition — https://docs.temporal.io/activity-definition
- [31] Kyle Kingsbury — Jepsen: Orkes Conductor 5.3.2 (Jepsen, 2026; research, sponsored by Orkes) — https://jepsen.io/analyses/orkes-conductor-5.3.2
- [33] Temporal — temporalio source, `temporalio/common.py` (`RetryPolicy`), 1.35.0 — https://github.com/temporalio/sdk-python/blob/1.35.0/temporalio/common.py — checked 2026-10-30
- [34] Temporal — Versioning, Python SDK — https://docs.temporal.io/develop/python/versioning
- [37] Temporal — Self-hosted Visibility feature setup — https://docs.temporal.io/self-hosted-guide/visibility
- [38] DBOS — Self-Hosting Guide (Conductor) — https://docs.dbos.dev/conductor/self-hosting/hosting-conductor
- [39] Temporal — temporalio source, `temporalio/client/_client.py` (`Client.connect`), 1.35.0 — https://github.com/temporalio/sdk-python/blob/1.35.0/temporalio/client/_client.py — checked 2026-10-30
- [40] Temporal — temporal (server repository), `LICENSE` (branch `main`) — https://github.com/temporalio/temporal/blob/main/LICENSE — checked 2026-10-30
- [41] DBOS — dbos source, `dbos/_serialization.py`, 3.4.0 — https://github.com/dbos-inc/dbos-transact-py/blob/3.4.0/dbos/_serialization.py
- [42] DBOS — dbos source, `dbos/_dbos.py`, 3.4.0 — https://github.com/dbos-inc/dbos-transact-py/blob/3.4.0/dbos/_dbos.py
- [43] Python — pickle: Python object serialization, Python 3.15.2 — https://docs.python.org/3/library/pickle.html
- [44] Temporal — Temporal Platform security features (self-hosted guide) — https://docs.temporal.io/self-hosted-guide/security — checked 2026-10-30
