# CI rules: jobs, triggers, stages and the required check

This file is for everyone who writes or changes a CI workflow, people and AI agents alike. It
says what a job is and what goes into it, which event should start which work, in what order
the stages run, how one check guards `main`, and how a monorepo runs only what a change touches.
Deploys are in [delivery.md](delivery.md); token permissions, pinned actions, untrusted input and
secrets are in [pipeline-security.md](pipeline-security.md). The examples use GitHub Actions; the
rules hold on any CI system unless a line names a GitHub feature.

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. The words: workflow, job, step, runner, CI and CD](#2-the-words-workflow-job-step-runner-ci-and-cd)
- [3. What a job holds, and what it does not](#3-what-a-job-holds-and-what-it-does-not)
- [4. Triggers: what starts a workflow](#4-triggers-what-starts-a-workflow)
- [5. Stages and when they run](#5-stages-and-when-they-run)
- [6. One required check: the gate job](#6-one-required-check-the-gate-job)
- [7. A monorepo: run what a change touches](#7-a-monorepo-run-what-a-change-touches)
- [8. Speed: a feedback budget, caches, concurrency, timeouts](#8-speed-a-feedback-budget-caches-concurrency-timeouts)
- [9. Reproducible runs: lockfiles and pinned tools](#9-reproducible-runs-lockfiles-and-pinned-tools)
- [10. A red build and a flaky test](#10-a-red-build-and-a-flaky-test)
- [11. Common mistakes](#11-common-mistakes)
- [12. Where the rules stop holding](#12-where-the-rules-stop-holding)
- [13. Alternatives considered](#13-alternatives-considered)
- [14. Sources](#14-sources)

## 1. Purpose and the one rule

CI exists so that every change is checked the same way before it joins the work of everyone
else, and a broken change is found in minutes, not on release day. It pays off in how often a
team can ship: in a study of 34,544 open-source projects on GitHub, Hilton et al. found that
projects that use CI "release twice as often as those that" do not [1].

One rule holds the rest together: **every change reaches `main` only through checks that run
from a clean runner, the same way every time, and one red check stops it.** The sections below
say which checks, on which event, in which order, and how to keep them fast enough that people
wait for them and honest enough that people trust them. When the project has no tests yet, the
team is one person, or a few maintainers take changes from people they do not know, read
section 12 first: it says which parts then do not fit.

What this file leaves to other practices: what each check checks (Python's static checks are
[static-checks.md](../../python/static-checks/static-checks.md), Python's test suites are
[python/testing/layout.md](../../python/testing/layout.md), React's tools are
[libraries.md](../../react/architecture/libraries.md)), the job that builds and pushes an image
([images.md](../docker/images.md) section 10), and the definitions of continuous integration,
continuous delivery and continuous deployment ([release.md](../project-management/release.md)
section 5).

## 2. The words: workflow, job, step, runner, CI and CD

GitHub's terms, which other CI systems name differently (section 13) [2], and the other words this
folder uses:

| Word | What it is |
|---|---|
| workflow | a YAML file in `.github/workflows/` that runs one or more jobs when an event happens |
| job | a list of steps that run on one runner, from top to bottom. Each job gets its own fresh runner, and jobs run at the same time unless one names another in `needs` |
| step | one command (`run:`) or one action (`uses:`) inside a job. The steps of one job share its files |
| runner | the machine that runs a job: a virtual machine GitHub hosts, or a machine of your own |
| action | a packaged step from a repository, called with `uses:` |
| event | what starts a workflow: a pull request, a push, a schedule, a person who presses "Run workflow" |
| stage | a kind of check or step, in the order of cost, such as static checks or integration tests; here a stage is one or more jobs, and stages 1 to 5 start together (section 5) |
| artifact | what a job builds for a later job or a deploy: here the API image and the frontend bundle |
| digest | the hash of an image's content, such as `sha256:…`; it names exact bytes, while a tag can be moved ([images.md](../docker/images.md) section 8) |
| SHA pin | an action named by the full 40-character commit SHA of a release, which nobody can move ([pipeline-security.md](pipeline-security.md) section 4) |
| OIDC | OpenID Connect: GitHub signs a short-lived token that says which repository and environment run the job, and the cloud trusts that token instead of a stored key ([delivery.md](delivery.md) section 5) |
| environment | a GitHub setting named after a deploy target, such as `staging`, that holds its variables and secrets and the rules a job passes before it gets them ([delivery.md](delivery.md) section 4) |
| SBOM | a software bill of materials: the list of packages inside an artifact ([images.md](../docker/images.md) section 9) |
| required status check | a check that must pass before GitHub lets a change into a protected branch, so a pull request cannot merge while it is red or missing [17]; here `ci-ok` is the only one (section 6) |
| branch ruleset | the repository setting that protects a branch: it makes a check required and blocks force pushes and deletion ([ruleset-example.md](../git/ruleset-example.md)) |
| gate job | the one job that needs every check job and fails unless each passed or was skipped, so one required check covers them all: `ci-ok` (section 6) |
| smoke test | a short request to the new version right after a deploy, to see that it answers ([delivery.md](delivery.md) section 7) |

In a pipeline, **CI** is the workflow that checks a change. It runs on every pull request and
again on `main`, and it publishes nothing. **CD** is the workflow that publishes the artifacts of
a commit on `main` and deploys them to an environment ([delivery.md](delivery.md)). They differ in what they may touch: a
CI job reads the code and needs no credential that can change a running system; a CD job holds
exactly such credentials. That is why they are separate jobs with separate permissions.

## 3. What a job holds, and what it does not

- **Give each job one purpose, and name it by that purpose**: `backend-unit`, `frontend`,
  `deploy-staging`. When a job turns red, its name tells the reader what broke before anyone
  opens the log.
- **Split work into two jobs when the parts need different permissions, secrets, runners or
  environments, or can run at the same time; keep it as steps of one job when the steps share one
  checkout and one install and fail together.** Each job starts on a fresh runner [2], so a split
  costs one more checkout and install. A split by permissions is worth it: OWASP's risk
  CICD-SEC-5 asks that secrets be "scoped in a manner that allows each pipeline and step to have
  access to only the secrets it requires" [3].
- **A job starts from nothing and states what it needs.** It checks out the code, installs the
  pinned tools and the locked dependencies (section 9), and runs its commands. It reads what an
  earlier job made only as an output passed through `needs` [4] or an artifact it downloads [5].
  A job that relies on what happened to be on a runner passes on one run and fails on the next.

| In a job | Not in a job |
|---|---|
| the checkout, with `persist-credentials: false` ([pipeline-security.md](pipeline-security.md) section 3) | a secret the job's commands do not use |
| the pinned tools and an install from the lockfile (section 9) | a deploy step in a job that runs tests |
| the commands of its one purpose | a step that a person has to do by hand |
| a `permissions:` block that lists only what it uses ([pipeline-security.md](pipeline-security.md) section 3) | `continue-on-error: true` on a check that guards `main` (section 10) |
| `timeout-minutes:`, on a job that runs on a runner (section 8) | a loop that reruns a failing test or check until it passes (section 10) |
| an upload of what a later job or a person needs: an artifact, a report, a line in the job summary, within the personal-data and retention rules of [pipeline-security.md](pipeline-security.md) section 9 | a file another job left behind on "its" runner |

## 4. Triggers: what starts a workflow

**Start every check automatically on the event that needs it, and keep manual runs for decisions
a person makes.** A check that someone has to remember to start is the check that is skipped on
the day it matters, and a deploy to production that starts by itself takes the decision away from
the person [release.md](../project-management/release.md) section 3 gives it to, unless that person
made the standing decision of continuous deployment ([delivery.md](delivery.md) section 2).

| Event | Fires when | Use it for | Watch for |
|---|---|---|---|
| a local commit, not a GitHub event | a developer runs `git commit` | the pre-commit hook on the developer's machine ([static-checks.md](../../python/static-checks/static-checks.md) section 5, [pipeline-security.md](pipeline-security.md) section 6): the first check, before CI | no workflow starts |
| `pull_request` | a pull request is opened, gets a new push, or is reopened; the run checks the merge of the branch into its base [6] | every check that guards `main` | a pull request from a fork, and one from Dependabot, gets no secrets and a read-only token [6]: a check that needs a secret, such as an eval that calls a paid model, cannot run there, so keep secrets out of the checks that guard `main`. The one exception is a read-only token that only lifts a rate limit, such as Docker Hub's, whose step is skipped when the secret is absent ([ci-example.md](ci-example.md)) |
| `merge_group` | a pull request enters a merge queue [6] | the same checks, on the queued merge (section 6) | without it, a required check is never reported to the queue and the merge fails [6] |
| `push` to `main` | a commit lands on `main` | the checks again on the merged code, then the build of the release artifact ([delivery.md](delivery.md) section 3) | a workflow that only runs here finds a problem after the merge, not before it |
| `push` of a tag such as `v1.4.2` | a person, or under continuous deployment the tag job, creates a tag that matches the pattern | the deploy of that version to production ([delivery.md](delivery.md) section 4) | `paths` filters are not evaluated for tag pushes [4] |
| `workflow_dispatch` | a person with write access presses "Run workflow" or calls the API [7]; the file must be on the default branch [6] | a decision: redeploy a released version, roll back ([delivery.md](delivery.md) section 7) | its inputs are text a person typed: pass them to a script through `env`, never with `${{ }}` inside it ([pipeline-security.md](pipeline-security.md) section 5) |
| `schedule` | a cron time, in UTC, on the default branch only [6] | a rescan with a fresh vulnerability database ([pipeline-security.md](pipeline-security.md) section 7), a full run of a monorepo whose pull requests run only part of it | a scheduled run can start late or be dropped under load, and in a public repository it turns itself off after 60 days without activity [6]: name the person who watches it (section 10) |
| `workflow_call` | another workflow calls this one | reuse: the deploy workflow calls CI first, so no deploy skips a check | a called workflow can keep or lower the caller's permissions, never raise them [8] |
| `pull_request_target`, `workflow_run` | they run with the base repository's token and its secrets [9] | jobs that never run the pull request's code, such as adding a label | checking out or running the pull request's code there ([pipeline-security.md](pipeline-security.md) section 5) |

A push to a branch that has no pull request starts no workflow in this practice, so the pull
request is the first CI run.

**Run a job that needs a paid key, such as an eval that calls a model, outside the gate: started
by hand with `workflow_dispatch`, or by a maintainer, with its key in a GitHub environment of its
own.** On a pull request from a fork, "With the exception of `GITHUB_TOKEN`, secrets are not
passed to the runner" [40], so such a job inside the gate would be red for every outside
contributor. An environment secret reaches a job only after the environment's rules pass
([delivery.md](delivery.md) section 4), so the key stays away from the checks that run a pull
request's code, and the person who starts the run reads the diff first. Never move the job to
`pull_request_target` to reach the key ([pipeline-security.md](pipeline-security.md) section 5),
and in a private repository leave "Send secrets to workflows from pull requests" off: it "Makes
all secrets available to the pull request" from a fork [41]. When and how an eval runs before a
merge, and the spend limit on its key, are [evals.md](../../python/evals/evals.md) section 8's
rules. This practice found no case where this is too much.

## 5. Stages and when they run

- **Order the stages from fast and cheap to slow, and let the first red one stop the release.**
  Fowler: in a deployment pipeline, "Early stages can find most problems yielding faster feedback,
  while later stages provide slower and more thorough probing", and "Deploying into production is
  usually the final stage" [11]. Humble describes the first step as "optimized so that it takes
  only a few minutes to run" [12]. Inside CI, the check jobs of stages 1 to 5 run side by side and
  the gate job collects them (section 6): a red job fails the gate however far the others got, and
  the run takes as long as its slowest job, not the sum (section 8). `needs` orders only the work
  that uses an earlier result or must not start on red: publish needs CI, and staging needs
  publish; production comes after staging through the release decision
  ([delivery.md](delivery.md) section 4). The table's order is the order of cost, the order in
  which a failure is read, not the order in which the jobs start.
- **A pull request runs every check the release runs and publishes nothing; `main` runs the same
  checks again on the merged code before anything is built for release.** A reviewer then sees on
  the pull request what the release will see, and an artifact exists only for code that passed.
  Fowler makes the same point about the build on the mainline: "Only once this integration build
  is green can the developer consider the integration to be complete" [10].
- **When another practice asks CI to run its check, put the check in the stage of its cost and link
  the owner's rule.** This file decides where and when a check runs; what it checks, and the value
  it fails on, stay with the practice that owns them, so a change to the rule is made in one place.
  The table names each owner. This practice found no case where this is too much.
- **Before a merge, apply every migration to an empty scratch database, then compare the result
  with the code's models.** A migration that fails, or a model change with no migration, then shows
  on the pull request and not in the staging deploy. With Alembic the two steps are
  `alembic upgrade head` and `alembic check`, which "returns an error code plus a message if it is
  detected that new operations would be rendered into a new revision" and "can be worked into CI
  systems" [43]. `upgrade head` also fails when two branches each added a migration on the same
  parent, because then "Multiple head revisions are present for given argument 'head'" [44]. With
  another tool, use its own commands for the same two steps. Know what the check misses:
  `alembic check` compares the way autogenerate does, so "limitations in autogenerate detection are
  the same" [43]; a renamed table or column shows as a drop and an add, and an unnamed constraint
  is not seen [43]. An empty database also says nothing about the rows a migration changes: DORA
  asks you to "test every schema change against a production-like data set (with any personal or
  confidential information scrubbed, of course)" [42]. Staging is where that happens, since its
  deploy runs the migration first ([delivery.md](delivery.md) section 6), on synthetic data
  ([pipeline-security.md](pipeline-security.md) section 9). An application with no database, or
  none whose schema migrations manage, has nothing to check; this practice found no other case
  where the check is too much.

| Stage | What runs | Whose rules decide what it checks | Job in the example | Pull request, merge queue | `main` | Version tag | Schedule |
|---|---|---|---|---|---|---|---|
| 1. Static checks | format, lint, types, import contracts, file hygiene, the workflow linters | [static-checks.md](../../python/static-checks/static-checks.md) section 5 (Python); [libraries.md](../../react/architecture/libraries.md) sections 3 and 4 (React); [pipeline-security.md](pipeline-security.md) section 7 (workflows) | `checks`, `frontend`, and the `workflows` job of `security.yml` | yes | yes | the workflow linters only, with stage 5 | yes, weekly |
| 2. Unit tests | the tests that need nothing outside the process | [layout.md](../../python/testing/layout.md) section 2 (Python); [libraries.md](../../react/architecture/libraries.md) section 6 (React) | `backend-unit`, `frontend` | yes | yes | no | yes, weekly |
| 3. Build | the image, built, tested and scanned; the frontend bundle and its size budget | [images.md](../docker/images.md) section 10 (image); [performance.md](../../react/performance/performance.md) section 3 (the budget and its value) | `image`, `frontend` | yes, nothing pushed | yes | no | yes, weekly, nothing pushed |
| 4. Integration tests | the tests that need a database, a container or the network, in a job of their own; the migration check | [running-tests.md](../../python/testing/running-tests.md) section 9; the migration bullet above | `backend-integration` | yes | yes | no | yes, weekly |
| 5. Security checks | dependencies, code, infrastructure code; secrets: pull request only | [pipeline-security.md](pipeline-security.md) section 7; the frontend's supply-chain checks, [security.md](../../react/security/security.md) section 14 | `security`, which calls `security.yml` | yes | yes | yes, before production | yes, weekly |
| 6. Publish | the image pushed by digest, the bundle stored | [delivery.md](delivery.md) section 3 | `publish-api`, `publish-web` | no | yes | no | no |
| 7. Staging | migrate, deploy, smoke test; after the deploy, the passive scan of the running site and the header scans; end-to-end tests with axe, which the example does not show | [delivery.md](delivery.md) sections 5, 6 and 7; [pipeline-security.md](pipeline-security.md) section 7 (the passive scan); [security.md](../../react/security/security.md) section 14 (headers); [accessibility.md](../../react/design/accessibility.md) section 10 (axe) | `staging`, `dast-staging`, `headers-staging` | no | yes | no | no |
| 8. Production | the same artifact deployed, smoke test | [delivery.md](delivery.md) section 4 | `tag-is-on-main`, `production` | no | no | yes | no |
| Outside the gate | a job that needs a paid key, such as an eval that calls a model | [evals.md](../../python/evals/evals.md) section 8; section 4 above (the key) | not shown | started by hand or by a maintainer | no | no | as [evals.md](../../python/evals/evals.md) section 8 asks |

## 6. One required check: the gate job

- **Make one job, such as `ci-ok`, the only required status check for `main`. Let it name every
  check job in `needs`, run with `if: always()`, and fail unless each job it needs succeeded or
  was skipped by its own `if:`.** GitHub's troubleshooting page gives the two facts behind the
  shape: a job that depends on a failed job "is skipped and may not block merging", and the fix is
  to "Use `always()` with `needs` for required checks that depend on other jobs" [13]. The pattern
  is in wide use: the `alls-green` action exists for it [14], and Wharton describes the same trap
  and the same fix [15]. One required name also means a new job joins the gate in the workflow
  file, with no change to the ruleset.
- **Never put `paths:`, `paths-ignore:` or `branches:` filters on the `pull_request` or
  `merge_group` trigger of a workflow whose check is required.** A `branches:` filter on `push` is
  fine, because the required check comes from the pull request. A workflow skipped by such a
  filter leaves its checks "Pending", which blocks the merge; GitHub's advice is to "Avoid requiring workflows that can be skipped" [13]. Skip jobs
  inside the workflow with `if:` instead (section 7): a job skipped by its condition reports
  "Success" [13]. GitHub has acknowledged the gap and given no date for a fix [16], so the gate
  job is the way to do it, not a stopgap.
- **Require the gate in the branch ruleset, with "Require branches to be up to date before
  merging" on.** The branch "**must** be up to date with the base branch before merging", so the
  check ran on the code that lands; this is the default, and its cost is that "More builds may be
  required" [17]. The ruleset itself is the git practice's
  ([ruleset-example.md](../git/ruleset-example.md)).
- **Advanced: a merge queue.** Condition: GitHub offers merge queues in public repositories owned
  by an organization and in private repositories of organizations on Enterprise Cloud [18]. A
  queue gives the same up-to-date guarantee without each author updating the branch by hand [18].
  Every workflow whose check is required then also runs on `merge_group`, or the queue waits for a
  check that never comes [6].

Bad, a required workflow with a path filter:

```yaml
on:
  pull_request:
    paths: ["backend/**"]  # a frontend-only pull request leaves this check Pending forever
```

The problem is the filter on the workflow: GitHub never starts the run, so the required check
never reports [13]. The fixed form keeps the workflow unfiltered and moves the decision into a
job. Here it is cut to the trigger and three jobs; [ci-example.md](ci-example.md) section 1 has
the whole workflow:

```yaml
on:
  pull_request:  # no paths: the run always starts, so the gate always reports

jobs:
  changes:
    if: github.event_name == 'pull_request'  # on main and on the queue every job runs (section 7)
    # ... sets one output per project from the changed files
  backend-unit:
    needs: changes
    # A job skipped by its if reports success; !cancelled() lets it run when changes was skipped.
    if: ${{ !cancelled() && (github.event_name != 'pull_request' || needs.changes.outputs.backend == 'true') }}
    # ... runs-on, timeout-minutes, steps
  ci-ok:
    if: always()  # runs even when a job it needs failed, so a red job fails the gate
    needs: [changes, backend-unit]
    # ... fails unless each job it needs ended success or skipped
```

It is good because it fixes the one problem: a frontend-only pull request still starts the run,
the backend job reports skipped, and the `ci-ok` gate reports green, so the merge is open. With
the decision in a job, the job also has to keep `main` and the queue unscoped, so `changes` runs
on pull requests only and the backend job runs whenever `changes` was skipped (section 7).

Check: open a pull request that changes only the frontend. The backend jobs show "skipped",
`ci-ok` is green, and the merge button is open.

## 7. A monorepo: run what a change touches

- **Start by running every check on every pull request; scope the jobs by path only when a full
  run no longer fits the feedback budget (section 8).** A path rule must list every file a side
  (a project, here the backend or the frontend) depends on, and one missing line lets a change
  break that side with a green check.
- **When you scope, decide in the first job of the same workflow and skip with `if:`.** A
  change-detection step sets one output per side, and each side's jobs run when their output is
  `true`; `dorny/paths-filter` does this on pull requests, pushes and the merge queue [19]. Skipped
  jobs report success, so the gate stays one check (section 6).
- **Put the files every side depends on into every side's filter**: the workflow files, the hook
  file, a shared API schema. A change to one of them runs everything.
- **On `main`, run every job whatever changed.** The scoped run on a pull request is a shortcut;
  the full run on `main` catches what a filter missed.
- **Give each project its own jobs, which run in the project's folder**:
  `defaults.run.working-directory` for the commands [4], and the setup actions' own inputs for the
  folder ([ci-example.md](ci-example.md) section 2).
- **Pin the change-detection action like every action, and prefer a three-line
  `git diff --name-only` step where that is enough**
  ([pipeline-security.md](pipeline-security.md) section 4 for the pins and fewer actions, section 2
  for the incident). Semgrep's advice after the `tj-actions/changed-files` incident was to "inline
  your file-change detection logic" [21].

Larger monorepos, where projects depend on each other, need a tool that knows the dependency
graph and runs only what a change can break: Turborepo's `--affected` [22], Nx's `affected` [23],
Bazel or Pants. They compare against the git history, so the checkout fetches all of it. Choose
one when the projects import each other, not for two folders that share nothing but a repository.

## 8. Speed: a feedback budget, caches, concurrency, timeouts

- **Write down how long the pull request checks may take, and look at the slowest runs when they
  go over.** Ten minutes is the common figure: Fowler calls it "the XP guideline of a ten minute
  build" [10], DORA's page on CI names "an upper limit of about 10 minutes" for the tests that run
  on each commit [24], and it was the most common answer when Hilton et al. asked developers for the
  longest acceptable build [25]. In the same study, a survey of 51 developers at one company chose
  "varies by project" most often, and the authors leave open whether a threshold matters more
  [25]. Treat ten minutes as a guideline that practitioners share, not as a measured limit.
- **Run independent jobs at the same time.** Jobs run in parallel unless `needs` orders them [2];
  a job that waits for another without using its output wastes the wall-clock time.
- **Cache dependency downloads, keyed by the lockfile.** setup-uv caches with
  `enable-cache: true` [26], [27], and setup-node caches the package manager's store with
  `cache:` [28]. A run restores caches made on its own branch or on the default branch, and a
  pull request's cache serves only that pull request [29], so a pull request cannot fill the cache
  `main` reads.
- **Cancel a pull request's older run when a new push arrives; never cancel a run on `main` or a
  deploy.** `concurrency` with `cancel-in-progress` does the first [4]. On `main` a cancelled run
  leaves a commit with no result, and a deploy cut off halfway leaves an environment half updated
  ([delivery.md](delivery.md) section 4).
- **Set `timeout-minutes` on every job that runs on a runner (`runs-on`), a little above its
  slowest normal run.** A job that calls a reusable workflow gets its timeouts from the jobs it
  calls. The default is 360 minutes [4], so a hung job holds a runner for six hours. In a sample of 382 workflows from
  public repositories, Abrokwah and Ghaleb found that "96.3% of workflows define no
  timeout-minutes bound on their jobs" (a preprint) [30].
- **Know what the runs cost in a private repository, and set a budget with alerts.** GitHub
  Actions is free for public repositories on standard GitHub-hosted runners and for self-hosted
  runners; a private repository gets 2,000 minutes a month on GitHub Free and 3,000 on Pro or
  Team, then pays per minute, USD 0.006 for a Linux 2-core runner [45]. Artifacts share one storage
  allowance with GitHub Packages, 500 MB on Free, 1 GB on Pro and 2 GB on Team, then USD 0.25 per
  GB a month, and the cache has its own 10 GB per repository [45]; short retention keeps the
  artifacts small ([pipeline-security.md](pipeline-security.md) section 9). A budget alerts at 75%,
  90% and 100%, and with "Stop usage when budget limit is reached" on, "additional usage is
  blocked" [46], CI included, so turn that on only where a stopped pipeline costs less than the
  bill. The images the pipeline pushes cost storage too, USD 0.10 per GB a month on Amazon ECR in
  AWS's own pricing example [47]. An ECR lifecycle policy expires old images "within 24 hours"
  after they meet its rule, so write it to keep every image a rollback may redeploy
  ([rollback-plan.md](../project-management/rollback-plan.md) section 2), and run its preview
  first, as AWS asks [48]. A public repository on standard GitHub-hosted runners pays GitHub
  nothing for Actions [45], so there only the registry's part of this bullet applies.

## 9. Reproducible runs: lockfiles and pinned tools

- **Install exactly what the lockfile says, with the command that fails when the lockfile is
  stale.** For Python, `uv sync --locked` raises an error "instead of updating the lockfile" [31];
  for pnpm, `pnpm install --frozen-lockfile`, which pnpm turns on in CI by default and which fails
  when the lockfile is out of sync with `package.json` [39]. A CI that resolves versions itself
  tests a set of packages nobody pinned, and a stale lockfile then shows as a red check, not as a
  surprise in production.
- **Pin the toolchain in files the repository holds, and let CI read them:** the Python version
  (setup-uv reads it from the project [26], [27]), Node's version through setup-node's
  `node-version-file` [28], and the package manager through `packageManager` in `package.json`.
  The developer's machine, CI and the image then run the same Python, Node and package manager.
  uv itself gets a floor, not a pin: `[tool.uv] required-version`, as
  [setup-example.md](../../python/static-checks/setup-example.md) section 1 sets it, while the
  checking tools stay locked in `uv.lock` ([static-checks.md](../../python/static-checks/static-checks.md)
  section 3). setup-uv reads the floor from the project [26], [27] and installs the newest uv that
  meets it, so CI's uv can be newer than a developer's or the image's.
- **Name the runner image by its version, such as `ubuntu-24.04`, not by `ubuntu-latest`.**
  GitHub moves the `-latest` label to a new OS version over one to two months, and during that
  time "any workflow using the `-latest` label, may see changes in the OS version" [32]. A version
  label changes only when someone changes it, in a pull request where the effect shows. The cost:
  you move it yourself before GitHub retires the image.
- **Pin every action to a full commit SHA**, as [pipeline-security.md](pipeline-security.md)
  section 4 says.

## 10. A red build and a flaky test

- **When the build on `main` turns red, fixing it comes before other work, usually by reverting
  the change that broke it.** Fowler: the build "needs to be fixed right away", and "Usually the
  best way to fix the build is to revert the latest commit from the mainline" [10]. DORA's page on
  CI asks for an agreement that fixing a broken build will "take priority over any other work" [24].
- **Never rerun a failed job until it passes.** A check that fails and then passes on the same
  code is flaky, and a flaky check teaches people to ignore red. DORA: "don't tolerate flaky
  tests" [33]. In 52,610 rerun builds of 1,960 open-source Java projects on GitHub Actions, Ge and
  Zhang found 67.73% flaky, and that reruns "often serve only as a temporary workaround rather than
  resolving the underlying root causes" (a preprint) [34]. How a flaky Python test is fixed is
  [running-tests.md](../../python/testing/running-tests.md) section 9.
- **Never set `continue-on-error: true` on a job the gate needs.** It "Prevents a workflow run from
  failing when a job fails" [4], so the failure stops guarding `main`.
- **Make sure each failure reaches a person.** Each person who answers for the pipeline turns on
  GitHub's notifications for workflow runs, with "Only notify for failed workflows", on GitHub or by
  email [49]. These notifications reach only the person who started the run: GitHub sends one
  "when any workflow runs that you've triggered have completed" [56]. A run that the tag job's
  GitHub App starts by pushing a tag was triggered by no person, as this practice reads it, so under
  continuous deployment the failure notice job below is required ([delivery.md](delivery.md)
  section 2). "Notifications for scheduled workflows are sent to the user who last modified the
  cron syntax in the workflow file" [6], so the person named for a schedule (section 4) is the one
  whose notifications must be on, whoever edited the line last. When a team channel should hear
  about a failure on `main` or in a deploy, add a last job to the same workflow that needs the
  others and runs when one of them failed or was cancelled:
  `if: ${{ always() && (contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled')) }}`.
  `failure()` alone is true when "any ancestor job fails" [50], but a job that reaches its
  `timeout-minutes` is one GitHub "automatically cancels" [4], and a job's result is one of
  `success`, `failure`, `cancelled` or `skipped` [57], so `failure()` misses a job that timed out.
  Do not use a second workflow on `workflow_run`: it starts "regardless of the conclusion of the
  previous workflow", and it "is able to access secrets and write tokens, even if the previous
  workflow was not" [6]. For one person under continuous delivery, GitHub's own notification is
  enough, and the notify job is the part that is too much (this practice's reasoning).

## 11. Common mistakes

| Mistake | What it costs | Fix |
|---|---|---|
| A `paths:` or `branches:` filter on the `pull_request` or `merge_group` trigger of a required workflow | a pull request that does not match the filter waits on a Pending check forever | section 6 |
| A gate job without `if: always()` | a failed check skips the gate, and a skipped job counts as passing | section 6 |
| Checks that run only on `push` to `main` | the problem is found after the merge | section 4 |
| No `timeout-minutes` on a job that runs on a runner | a hung job holds a runner for six hours | section 8 |
| `ubuntu-latest` | the operating system changes under a green build | section 9 |
| An install that may change the lockfile | CI tests versions that nobody pinned | section 9 |
| Rerun until green | flaky tests stay, and a real failure hides among them | section 10 |
| A deploy step in the job that runs the tests | the test job holds production credentials | section 3 and [delivery.md](delivery.md) |

## 12. Where the rules stop holding

- **A repository with nothing to deploy**, such as a library: sections 2 to 10 hold, and the
  publish step pushes a package instead of deploying it.
- **A small repository whose full run takes three minutes**: skip change detection (section 7);
  the gate job still pays, because it keeps the required checks to one name.
- **A monorepo whose projects import each other**: path filters stop being safe, and a graph-aware
  build tool takes over (section 7).
- **Self-hosted runners**: a job may find files from an earlier run, so section 3's "starts from
  nothing" needs runners that are wiped after each job
  ([pipeline-security.md](pipeline-security.md) section 5).
- **Another CI system**: the rules hold; the names of events, jobs and the required check differ
  (section 13).
- **A project where continuous integration does not fit.** Fowler holds that in "a classical
  open-source project, where there is one or two maintainers and many contributors", "Continuous
  Integration isn't plausible", though raising how often work is integrated still helps; that
  setting is where the pull-request workflow came from [10]. The checks of this file on each pull
  request still hold there; integrating into the mainline every day is the part that does not.
  CI also needs tests first: "Instituting Continuous Integration without self-testing code won't
  work" [10], so a project with no tests writes them before it builds a pipeline.
- **A small team whose whole suite runs fast on its own machines.** At 37signals, the checks for
  HEY took "about 5m30s" on remote runners and less than half that on a developer's machine, so the
  company moved CI back to developer machines; David Heinemeier Hansson calls a remote CI setup "a
  substantial complication" [51]. Its `gh-signoff` tool posts the local run's result as a commit status that a
  ruleset can require [52]. That is one company's case, with a fast suite and a trusted team. The
  deploy still runs from the pipeline, with short-lived credentials and no cloud key on a laptop
  ([delivery.md](delivery.md) section 5); that part is this practice's reasoning.
- **One person.** "Pull request authors cannot approve their own pull requests" [53], and OpenSSF
  Scorecard's code-review check says that requiring reviews "is infeasible for some projects, such
  as those with only one active participant", and counts no review by a bot, AI included [54]. So
  one person keeps the pull request and the `ci-ok` gate and requires no approval, as
  [ruleset-example.md](../git/ruleset-example.md) sets it; that file also owns which plans have
  rulesets. When a second reviewer is there only some of the time, keep the approval rule and give
  the owner a bypass "For pull requests only": the owner still opens a pull request, "creating a
  clear trail of their changes in the pull request and audit log", and may then merge it [55]. A
  personal account keeps a security log, not an organization's audit log
  ([pipeline-security.md](pipeline-security.md) section 12).

## 13. Alternatives considered

- **Other CI systems.** They name events, jobs and the required check differently; the rules hold
  in intent, and the examples use GitHub Actions because one system has to be shown.
- **Path filters on the workflow instead of a gate job.** Rejected: a skipped required workflow
  blocks the merge (section 6).
- **Running everything on every change.** The default, until it no longer fits the budget
  (section 7).
- **Rerunning failed tests automatically.** Rejected for a test that does not call a real model:
  it hides the cause ([running-tests.md](../../python/testing/running-tests.md) section 9).

## 14. Sources

Checked 2026-10-18 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Michael Hilton et al. — Usage, Costs, and Benefits of Continuous Integration in Open-Source Projects (ASE, 2016; research) — https://mir.cs.illinois.edu/marinov/publications/HiltonETAL16ContinuousIntegration.pdf
- [2] GitHub — Understanding GitHub Actions — https://docs.github.com/en/actions/get-started/understand-github-actions
- [3] OWASP — Top 10 CI/CD Security Risks, CICD-SEC-5: Insufficient PBAC, v1.0 — https://owasp.org/www-project-top-10-ci-cd-security-risks/CICD-SEC-05-Insufficient-PBAC
- [4] GitHub — Workflow syntax for GitHub Actions — https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax — checked 2026-10-19
- [5] GitHub — Workflow artifacts — https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts
- [6] GitHub — Events that trigger workflows — https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- [7] GitHub — Manually running a workflow — https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow
- [8] GitHub — Reuse workflows — https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
- [9] GitHub — Secure use reference — https://docs.github.com/en/actions/reference/security/secure-use
- [10] Martin Fowler — Continuous Integration (martinfowler.com, 2024; opinion) — https://martinfowler.com/articles/continuousIntegration.html
- [11] Martin Fowler — DeploymentPipeline (martinfowler.com, 2013; opinion) — https://martinfowler.com/bliki/DeploymentPipeline.html
- [12] Jez Humble — Patterns (continuousdelivery.com, no date; opinion) — https://continuousdelivery.com/implementing/patterns/
- [13] GitHub — Troubleshooting required status checks — https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- [14] re-actors — alls-green, README — https://github.com/re-actors/alls-green
- [15] Jake Wharton — Fan-in to a single required GitHub Action (jakewharton.com, 2025; opinion) — https://jakewharton.com/fan-in-to-a-single-required-github-action/
- [16] GitHub Community — discussion 44490 on required checks skipped by path filters (github.com/orgs/community, 2023; opinion) — https://github.com/orgs/community/discussions/44490
- [17] GitHub — Available rules for rulesets — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- [18] GitHub — Managing a merge queue — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
- [19] dorny — paths-filter, README, v4.0.3 — https://github.com/dorny/paths-filter/blob/v4.0.3/README.md
- [21] Semgrep — Popular GitHub Action tj-actions/changed-files is compromised (semgrep.dev, 2025; case) — https://semgrep.dev/blog/2025/popular-github-action-tj-actionschanged-files-is-compromised
- [22] Vercel — Turborepo: Constructing CI — https://turborepo.dev/docs/crafting-your-repository/constructing-ci
- [23] Nx — Run only tasks affected by a PR — https://nx.dev/ci/features/affected
- [24] DORA — Capabilities: Continuous integration — https://dora.dev/capabilities/continuous-integration/
- [25] Michael Hilton et al. — Trade-offs in Continuous Integration: Assurance, Security, and Flexibility (ESEC/FSE, 2017; research) — https://mir.cs.illinois.edu/marinov/publications/HiltonETAL17TradeOffsInCI.pdf
- [26] Astral — uv: Using uv in GitHub Actions, uv 0.13.1 — https://docs.astral.sh/uv/guides/integration/github/
- [27] Astral — setup-uv, README, v10.3.0 — https://github.com/astral-sh/setup-uv/blob/v10.3.0/README.md
- [28] GitHub — actions/setup-node, README, v7.1.0 — https://github.com/actions/setup-node/blob/v7.1.0/README.md
- [29] GitHub — Dependency caching reference, Restrictions for accessing a cache — https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching#restrictions-for-accessing-a-cache
- [30] Edward Abrokwah and Taher A. Ghaleb — An Empirical Study of Complexity, Heterogeneity, and Compliance of GitHub Actions Workflows (arXiv, 2025; research) — https://arxiv.org/abs/2507.18062
- [31] Astral — uv: Locking and syncing, uv 0.13.1 — https://docs.astral.sh/uv/concepts/projects/sync/
- [32] GitHub — actions/runner-images, README — https://github.com/actions/runner-images
- [33] DORA — Capabilities: Test automation — https://dora.dev/capabilities/test-automation/
- [34] Wenhao Ge and Chen Zhang — Understanding and Detecting Flaky Builds in GitHub Actions (arXiv, 2026; research) — https://arxiv.org/abs/2602.02307
- [39] pnpm — pnpm install (`--frozen-lockfile`) — https://pnpm.io/cli/install
- [40] GitHub — Using secrets in GitHub Actions — https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
- [41] GitHub — Managing GitHub Actions settings for a repository — https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- [42] DORA — Capabilities: Database change management — https://dora.dev/capabilities/database-change-management/
- [43] SQLAlchemy — Alembic: Auto Generating Migrations (`alembic check`, what autogenerate cannot detect), 1.20.0 — https://github.com/sqlalchemy/alembic/blob/rel_1_20_0/docs/build/autogenerate.rst
- [44] SQLAlchemy — Alembic: Working with Branches, 1.20.0 — https://github.com/sqlalchemy/alembic/blob/rel_1_20_0/docs/build/branches.rst
- [45] GitHub — GitHub Actions billing — https://docs.github.com/en/billing/concepts/product-billing/github-actions
- [46] GitHub — Setting up budgets to control spending on metered products — https://docs.github.com/en/billing/how-tos/set-up-budgets
- [47] AWS — Amazon ECR pricing — https://aws.amazon.com/ecr/pricing/
- [48] AWS — Amazon ECR User Guide: Automate the cleanup of images by using lifecycle policies — https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html
- [49] GitHub — Managing GitHub Actions notifications — https://docs.github.com/en/subscriptions-and-notifications/how-tos/managing-github-actions-notifications
- [50] GitHub — Evaluate expressions in workflows and actions (`failure`) — https://docs.github.com/en/actions/reference/workflows-and-actions/expressions
- [51] David Heinemeier Hansson — We're moving continuous integration back to developer machines (world.hey.com, 2024; case) — https://world.hey.com/dhh/we-re-moving-continuous-integration-back-to-developer-machines-3ac6c611
- [52] Basecamp — gh-signoff, README, v0.4.1 — https://github.com/basecamp/gh-signoff/blob/v0.4.1/README.md
- [53] GitHub — Approving a pull request with required reviews — https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews
- [54] OpenSSF — Scorecard checks: Code-Review, v5.6.0 — https://github.com/ossf/scorecard/blob/v5.6.0/docs/checks.md#code-review
- [55] GitHub — Creating rulesets for a repository — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository
- [56] GitHub — Notifications for workflow runs (`notifications-for-workflow-runs.md`) — https://github.com/github/docs/blob/dae83f7d28f3b8e10015bd6b6d8b72267cedceca/content/actions/concepts/workflows-and-actions/notifications-for-workflow-runs.md — checked 2026-10-19
- [57] GitHub — Contexts reference: the `needs` context (`contexts.md`) — https://github.com/github/docs/blob/dae83f7d28f3b8e10015bd6b6d8b72267cedceca/content/actions/reference/workflows-and-actions/contexts.md — checked 2026-10-19
