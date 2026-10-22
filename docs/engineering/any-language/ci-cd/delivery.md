# CD rules: build once, promote, deploy

This file is for everyone who writes or changes a deploy workflow, people and AI agents alike.
It says how an artifact is built once and promoted through the environments, how a deploy job
reaches the cloud without a stored key, what a deploy job holds, how production is gated, which
technologies a deploy can target, how the infrastructure a deploy needs is kept as code, how
delivery is measured, and when a pull request gets an environment of its own. Who decides that a
release goes to production, which
environments exist and how a release reaches users belong to
[release.md](../project-management/release.md); the way back is
[rollback-plan.md](../project-management/rollback-plan.md). The CI side is
[pipeline.md](pipeline.md), and workflow security and secrets are
[pipeline-security.md](pipeline-security.md).

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. Continuous delivery and continuous deployment, as pipelines](#2-continuous-delivery-and-continuous-deployment-as-pipelines)
- [3. Build once, promote the same artifact](#3-build-once-promote-the-same-artifact)
- [4. Environments and the production gate](#4-environments-and-the-production-gate)
- [5. Credentials: OIDC, not stored keys](#5-credentials-oidc-not-stored-keys)
- [6. The deploy job](#6-the-deploy-job)
- [7. After the deploy: smoke test, watch, the way back](#7-after-the-deploy-smoke-test-watch-the-way-back)
- [8. Technologies: where a deploy goes](#8-technologies-where-a-deploy-goes)
- [9. The infrastructure a deploy needs](#9-the-infrastructure-a-deploy-needs)
- [10. Measuring delivery](#10-measuring-delivery)
- [11. Preview environments per pull request](#11-preview-environments-per-pull-request)
- [12. Common mistakes](#12-common-mistakes)
- [13. Where the rules stop holding](#13-where-the-rules-stop-holding)
- [14. Alternatives considered](#14-alternatives-considered)
- [15. Sources](#15-sources)

## 1. Purpose and the one rule

A deploy should be a routine event that anyone with the right access can run at any time, not a
night of manual steps. Humble's patterns state the aim: deploy the same way to every environment,
so that "we test the deployment process many, many times before it gets to production" [1].

One rule holds the rest together: **build each artifact once, promote that same artifact through
every environment with the same deploy steps, and let only the pipeline, holding short-lived
credentials, change a running environment.** The sections below say how, for an API image and a
frontend bundle.

## 2. Continuous delivery and continuous deployment, as pipelines

[release.md](../project-management/release.md) section 5 defines both terms; DORA calls them
"separate practices" [2]. As a pipeline they differ in one place:

| | What runs on a merge to `main` | What starts the production deploy |
|---|---|---|
| Continuous delivery | CI, the build of the artifact, the deploy to staging and its checks | a person's decision, recorded as a version tag (section 4) |
| Continuous deployment | the same, then a job that creates the version tag | the tag that job creates once the approved merge has passed the staging deploy and its checks, with no person in between |

**Run continuous delivery by default: staging deploys on every merge, production deploys when the
go or no-go decider of [release.md](../project-management/release.md) section 3 says go.**
[deploy-example.md](deploy-example.md) shows it, and continuous deployment leaves that example as
it is. Continuous deployment is a team's choice under release.md section 5; release.md section 3
says when to use it, the one standing decision the decider makes for it, and the decisions that
stay with people.

**Under continuous deployment, a job creates the version tag, and the rest of the way to
production stays as it is.** The rules for that pipeline:

- **Let one job, after the green staging deploy and its checks on a commit of `main`, create the
  next protected `v*` tag; the tag starts the existing production deploy.** Section 4's tag-only
  `production` environment and section 7's rollback on an earlier tag do not change, and there is
  still one way to deploy, which Atlassian holds a continuous deployment pipeline must be: "the only
  method of deployment" [114]. The tag ruleset still lets only bypass actors create the tag [12] and
  stops anyone moving or deleting it (section 4), so the tag stays the lasting record of what
  shipped, while GitHub "retains records of previous deployment statuses for 90 days" [113]. Put
  the job in a concurrency group of its own, so two tag jobs never run at once. Let it tag a commit
  only when `git tag --list 'v*' --no-merged "$GITHUB_SHA"` prints nothing, and stop otherwise.
  The command lists the tags "whose commits are not reachable from" the commit it names [142], so
  it prints nothing only when this commit holds every `v*` tag, whatever order the runs came in.
  GitHub does not guarantee the order of runs in one concurrency group [40], so an older run could
  otherwise tag an older commit after a newer one and move production back (this practice's
  reasoning). On the push of a tag only, never on `workflow_dispatch`, let every job of the tag's
  run that changes production run the same test on its own commit as its first step: the
  production deploy and, with section 9's infrastructure code, the `infra-production` apply. Each
  fails before any change when the test prints a tag, so an older tag never lands over a newer one.
  It fails rather than skips, so no
  success record exists for a version that never ran. The way back on `workflow_dispatch` deploys
  an earlier tag on purpose, and the test would stop it (section 7). Run every copy of the test
  on a checkout that holds every tag and the full history, for example `actions/checkout` with
  `fetch-depth: 0`: by default the action fetches only "a single commit", while `fetch-depth: 0`
  fetches "all history for all branches and tags" [143], and without the other tags in the clone
  the test prints nothing and passes every time. The number the job gives the
  tag can follow the team's own
  scheme, as [release.md](../project-management/release.md) section 4 allows for an application
  nobody calls through an API.
- **Let that job sign in as a GitHub App, with an installation token.** A tag pushed with the
  workflow's `GITHUB_TOKEN` starts nothing: "events triggered by the `GITHUB_TOKEN` will not create
  a new workflow run" [115]. To start a workflow from a workflow run, GitHub names "a GitHub App
  installation access token or a personal access token" [116], and for an App it points to its own
  action, `actions/create-github-app-token` [117]. A ruleset's bypass list takes GitHub Apps [118],
  so list the App there. Its token "expires after 1 hour", and the action recommends to "explicitly
  list the permissions that are required for a use case" [119]: creating a tag needs only "Contents"
  write [120]. Keep the App's private key in a secret of an environment that admits only `main`, so
  no other branch can sign in as the App (this practice's choice); where secrets live is
  [pipeline-security.md](pipeline-security.md) section 6.
- **Merge nothing to `main` without the approval of someone other than its author, recorded in the
  platform.** DORA meets segregation of duties with peer review, "with reviews, comments, and
  approvals captured in the team's development platform" [13]; under continuous deployment that
  approval is the last person's look before production.
- **Treat a change to the gates as a change to production, and let the go or no-go decider approve
  it.** The workflow files, the rulesets, the required checks and the environments now approve each
  release ([release.md](../project-management/release.md) section 3). Kishan Sathyanarayanan, an
  auditor writing in the ISACA Journal, names "allowing engineers to modify the branch rule settings
  at will" as a common flaw [121], and Evan Bass and W. Noel Haskins-Hafer hold that once automation
  replaces such checkpoints, "pipeline integrity becomes a proxy for SoD" [122]. Give the workflow
  files that gate production (the deploy workflow, the workflows it calls, and the tag job's file)
  a `CODEOWNERS` line of their own, below the general line for `/.github/`, whose only owner is the
  decider with a named backup. GitHub takes the last line that matches, "the last matching pattern
  takes the most precedence", and "an approval from any of the owners is sufficient" [138], so a
  line the decider shares with others lets any of them approve. The review of workflow files stays
  [pipeline-security.md](pipeline-security.md) section 8. Rulesets, required checks and
  environments change in the settings, with no pull request: give the role that changes them only
  to the decider and the backup, and check each change in the audit log of
  [pipeline-security.md](pipeline-security.md) section 12. Anyone with write access can set a
  repository variable, the freeze switch included: to create one, GitHub writes, "for an
  organization repository, you must have `write` access", and "For a personal account repository,
  you must be a repository collaborator" [139]. So the audit log is its only check.
- **Let the deploy roll back by itself on a measured trigger, and bake before it ends.** At Google,
  a change that does not pass its validation period is "automatically rolled back" [123]; at
  Amazon, during each stage's bake time "the deployment is automatically rolled back if the team's
  high-severity aggregate alarm goes into the alarm state" [124]; and Atlassian holds that "A
  continuous deployment pipeline must be able to undo a deployment" [114]. On ECS these are section
  7's circuit breaker and alarm rollback, with its bake time [24], [39]. Keep the rollback plan's
  on-call decider for what the checks miss
  ([rollback-plan.md](../project-management/rollback-plan.md) section 2): Google's SRE workbook
  warns that "you won't be able to detect all release-related defects until real traffic is
  hitting the service" [125].
- **Stop the tag job before a rollback run by hand, and after an automatic rollback or a failed
  production run of a tag, and keep it stopped until the revert or the flag change is merged and
  green in staging.** Use the switch of the freeze bullet below. The rolled-back tag is still the
  latest `v*` tag, so the next merge would tag the bad change and deploy it again
  ([rollback-plan.md](../project-management/rollback-plan.md) section 3). After you stop the job,
  and before the rollback starts, cancel every unfinished run of a tag it pushed: such a run would
  still deploy its tag over the rollback.
- **Make the deploy workflow's failure notice job required.** GitHub notifies only the person who
  triggered a run, and, as this practice reads it, no person triggered a run the tag job's App
  starts ([pipeline.md](pipeline.md) section 10). List the tag job, the production deploy and, with
  section 9's infrastructure code, the `infra-staging` and `infra-production` applies in the notice
  job's `needs`. A failed apply leaves the deploy that needs it skipped [40], and the notice job
  runs only on a `failure` or `cancelled` result of a job it needs, so an apply it does not list
  fails in silence. Let a missing webhook secret fail the job instead of only warning, because
  a warning on a run nobody started reaches nobody. Let the notice say to stop the tag job, and
  name its switch (the freeze bullet below).
- **Keep every change safe to roll back: the previous version must still run on the data the new
  one writes.** At Amazon, "We plan and verify that our software is backwards compatible at every
  revision" [126]. The data side is expand, migrate and contract [45]
  ([rollback-plan.md](../project-management/rollback-plan.md) section 4).
- **Send a change the rollback cannot undo, or a high-risk one, down release.md section 3's path:
  it merges only with the decider's approval on its pull request.** Schema tools treat a drop the
  same way: Atlas's lint "fails the build and blocks the merge" on a destructive change, and with
  its review policy set to error "a detected drop requires manual approval at apply time" [127].
  Take the pattern, not the tool: this practice adds no schema linter.
- **For a freeze, stop the tag job, or stop merges, by hand for the length of the freeze.** The
  protection rules of a GitHub environment are required reviewers, a wait timer, custom rules from
  a GitHub App, and limits on branches and tags [37]; none of them is a time window. A job's `if:`
  can read a repository variable [137], so a variable the tag job checks is one way to stop it (this
  practice's suggestion). While the tag job is stopped, the decider can still push a tag by hand,
  which is continuous delivery again. Who calls a freeze is
  [release.md](../project-management/release.md) section 3's.

## 3. Build once, promote the same artifact

- **Build each artifact once, from the commit on `main`, and deploy those same bytes to staging
  and then to production.** Humble: "Only build packages once. We want to be sure the thing we're
  deploying is the same thing we've tested throughout the deployment pipeline" [1]; DORA: "Use the
  same packages for every environment" [3]; the Twelve-Factor App keeps build, release and run as
  separate stages, and "a release cannot be mutated once it is created" [4]. A rebuild for
  production is a new, untested artifact, however few lines changed.
- **Treat the image CI's image job builds to test and scan as a check, and the pushed image as the
  artifact.** Staging and production run the pushed image, by its digest.
- **Where the push is a second build from the same cache, as in
  [deploy-example.md](deploy-example.md), let the publish job scan the pushed digest again before
  any deploy.** The CI scan covered the first build, so this scan makes the bytes that ship the
  bytes scanned; [docker/ci-example.md](../docker/ci-example.md) says why the two builds differ.
- **Push that image by digest with no tag, and give the digest the tag a deploy looks it up by only
  after the scan passes.** The tag then means "scanned", a deploy can find only a scanned image,
  and a re-run after a failed scan pushes again without meeting an immutable tag.
- **Promote an image by its digest, never by a tag.** The tag and digest rules are
  [images.md](../docker/images.md) section 8's; here the deploy job looks up the digest of the
  `sha-<commit>` tag in the registry and writes the digest into the task definition (section 6).
- **Store the frontend bundle under its commit in an object store you keep, not only as a CI
  artifact.** GitHub keeps workflow artifacts for 90 days by default [5], so a rollback to an
  older version would find nothing to deploy. A prefix per commit, such as
  `s3://acme-web-releases/<sha>/`, is a store that keeps every released version. The bundle's
  publish role may write any key in that store, so a workflow change merged to `main` can rewrite
  a stored release; the review of workflow changes
  ([pipeline-security.md](pipeline-security.md) section 8) is what guards it.
- **Keep environment-specific values out of the frontend bundle, so one bundle fits every
  environment.** Vite writes environment values into the code at build time: "The values of these
  variables are bundled into your source code at build time" [6], and React's settings file reads
  them once ([architecture.md](../../react/architecture/architecture.md) section 3). The usual
  value that differs, the API's address, disappears when the API is served on the same origin:
  the CDN (content delivery network: servers near the users that keep copies of the files and
  serve them, here CloudFront) sends `/api/*` to the API and the rest to the bundle, because "The first match
  determines which cache behavior is applied to that request" [7]. When a value must still differ,
  build the bundle once per environment from the same commit and lockfile, with Vite's
  `--mode staging` and an `.env.staging` file [6], and write that departure down next to the build
  job: its cost is that production runs a bundle staging never ran. A config file the app loads at
  start is the other way practitioners use (section 14).

## 4. Environments and the production gate

- **Give every deploy job a GitHub environment named after its target, `staging` or
  `production`.** The environment holds that target's variables and secrets, and "Environment
  secrets" reach a job only after the environment's rules pass [10]. Naming the environment also
  creates the deployment record that [release.md](../project-management/release.md) section 7
  connects to Jira.
- **Restrict which refs may deploy to each environment: `staging` to `main` and version tags,
  `production` to version tags such as `v*`.** Staging takes a version tag only for a rehearsal of
  the way back (section 7). Deployment branch and tag rules work in private repositories on
  GitHub Pro and Team as well as in public ones [11]. A branch that is not `main` then cannot
  deploy, whoever runs it.
- **Gate production on the release decision: the go or no-go decider creates the version tag,
  and the tag starts the production deploy.** Protect release tags with a tag ruleset whose
  "Restrict creations" rule lets "only users with bypass permissions" create them [12], and whose
  update and deletion rules stop anyone moving a released tag; the ruleset's form is the git
  practice's ([ruleset-example.md](../git/ruleset-example.md)). Under continuous deployment the tag
  job of section 2 creates the tag, and the ruleset lists its GitHub App as a bypass actor [118].
  The tag is also the version number
  of [release.md](../project-management/release.md) section 4, so the record of what shipped is in
  git. The decider creates the tag on the commit whose staging deploy is green and pushes that one
  tag, such as `git push origin v1.4.2`, never `--tags`: GitHub creates no event when more than
  three tags are pushed at once [36], so the production deploy would not start. Runs in one
  concurrency group start in the order they began waiting, and GitHub does not guarantee even that
  [40], so an older commit's staging deploy can run after a newer one. Check: before you push the
  version tag, open the `staging` environment's deployments page and confirm it runs that commit
  [41].
- **Where the plan allows it, also require reviewers on the `production` environment, with
  "Prevent self-review" on.** On GitHub Free, Pro and Team, "other deployment protection rules,
  such as a wait timer or required reviewers, are only available for public repositories" [11];
  with the setting on, "users who initiate a deployment cannot approve the deployment job" [10].
  List two or three people; one approval is enough [37], and the decider must never be the only
  name, because the decider starts the run and so cannot approve it. Keep the reviewers peers, not
  an outside body: DORA found that approval by an external body "negative[ly] impact[s] software
  delivery performance" and that approval works best as peer review during development [13].
  Under continuous deployment, keep required reviewers off `production`: a reviewer would hold every
  deploy until a person approves it [37], and the go or no-go decider's standing decision of
  [release.md](../project-management/release.md) section 3 replaces that approval (this practice's
  choice). The way back then follows section 7's case for an environment without reviewers, run by
  the rollback plan's decider.
- **Let one deploy run at a time per environment, and never cancel one halfway.** Use
  `concurrency` with the environment's name and `cancel-in-progress: false`: GitHub says
  concurrency gives an environment "a maximum of one deployment in progress at a time" [14], and a
  cancelled deploy can leave half the service on the new version.
- **While a rollback waits, start no other run for that environment.** By default a group keeps
  one pending run and a newer request cancels it [40], so a new run would cancel the rollback
  before it starts. Under continuous deployment, that means stopping the tag job, and then
  cancelling the unfinished runs of the tags it pushed before the rollback starts (section 2).
- **When the run of a version tag fails, go forward with a new tag; never move the failed one.**
  The failed tag stays, because the ruleset forbids moving or deleting it, so write in the
  version's description that it was never deployed
  ([release.md](../project-management/release.md) section 3).
- **Take "Re-run failed jobs" on the failed run when the failure is not about the code**, such as
  an AWS call that timed out: on `main` the image is pushed with no tag, so its publish job repeats
  safely (section 3), and a deploy job is re-run only after a migration task it started has
  stopped ([deploy-example.md](deploy-example.md) section 4).
- **Fix a finding of the tag's security jobs on `main`: a fix or a waiver there, a green staging
  deploy and the next version tag.** An emergency release does not skip the tag's security jobs
  either: a waiver it needs goes through `main`, which costs one CI run and one publish on `main`
  before the next tag can deploy.

## 5. Credentials: OIDC, not stored keys

- **Let the deploy job get short-lived cloud credentials through OIDC, and store no cloud key in
  GitHub.** The job asks GitHub for a token with `permissions: id-token: write`, and the cloud
  trades it for credentials that last for the job [15]. A stored access key lasts until someone
  rotates it, and a leaked one keeps working.
- **Write the cloud's trust condition on the token's `sub` claim, naming the repository and the
  environment, never a wildcard.** GitHub: "you **must** define at least one condition, so that
  untrusted repositories can't request access tokens for your cloud resources" [15]. AWS rejects a
  trust policy whose `sub` is missing or only a wildcard, and warns that without a limit to your
  repository "GitHub Actions from organizations or repositories outside of your control are able
  to assume roles" in your account [16]. Datadog's researchers found such roles in real accounts,
  among them a government's [17]. A job that names an environment gets the `sub`
  `repo:<owner>/<repo>:environment:<name>` [15], so the production role trusts only the production
  environment. A publish job that names no environment gets the `sub`
  `repo:<owner>/<repo>:ref:refs/heads/main` on `main` [15]; trust that exact value, never a `*`.
- **Create each environment, with its rules, before any workflow names it and before a role trusts
  it.** A run that references an environment that does not exist creates one with that name, and
  the new environment has no protection rules [37]; a role that trusts `environment:production`
  then trusts whatever that empty environment admits. Never delete an environment a trust policy
  names.
- **Use the immutable `sub` form where your repository has it.** Repositories created after
  2026-07-15 get a `sub` that carries the owner's and the repository's numeric IDs, and older ones
  can opt in [18]; it stops a new owner of a recycled name from matching your trust policy. A
  rename or a transfer of the repository after that date also switches it to that form [18], [15]:
  update every trust policy when you rename or transfer the repository, or every role refuses the
  next token, the role the way back needs included.
- **Give each environment its own role, with only the permissions its deploy uses, and each publish
  job a role of its own, one per artifact, that can store that artifact and deploy nothing.** A
  mistake in a job's steps then reaches only what its own role may do. The split does not keep a
  compromised action out: publish jobs that name no environment all get the same `sub` (above),
  and an action in a job that holds `id-token: write` can request the job's token through
  environment variables on the runner [15], so a compromised action in either publish job can get
  a token that either publish role accepts. The SHA pins are what guard against that
  ([pipeline-security.md](pipeline-security.md) section 4). Where the publish jobs must be kept
  apart, give each one an environment of its own, limited to `main` by a deployment branch rule
  (section 4), and let each role trust only `environment:<name>`. Without the rule, a workflow on
  any branch could name that environment and get the role.
- **When you move a job to OIDC, delete the old stored key at the provider the same day.** In the
  Ultralytics compromise, an API token left in the workflow after the move to trusted publishing
  let the attackers publish a second time [19].
- **Keep runtime secrets in the cloud's secret store and reference them from the deployment, not
  from the workflow.** On ECS, the task definition's `secrets` names a Secrets Manager or Parameter
  Store entry, and "Sensitive data is injected into your container when the container is initially
  started" [20]; the workflow never sees the value. How the application reads its settings is
  [python.md](../../python/language/python.md) section 5.

## 6. The deploy job

**A deploy job takes an artifact that already exists and puts it into one environment. It holds:**

1. the cloud login through OIDC (section 5);
2. the artifact's reference: the image digest and the bundle's commit prefix;
3. the database migration, run once before the new code, which fails the job when it fails;
4. the deploy itself, waiting until the new version is healthy;
5. a smoke test against the environment (section 7);
6. a line in the job summary that records what was deployed where.

**It does not hold** a build, the test suites (they ran in CI), or the secrets of another
environment.

The security jobs sit before the deploy: the call of CI on `main` runs them before anything is
published, and a version tag runs them again on the tagged commit before production
([pipeline-security.md](pipeline-security.md) section 7).

- **Write the deploy steps once, as a reusable workflow, and call it for staging and for
  production with different inputs.** DORA: "Use the same deployment process for every
  environment, including production" [3]. A second copy of the steps drifts from the first, and
  the copy that drifts is the one that runs least: production's.
- **Run the migration as its own step before the service update, and stop the deploy when it
  fails.** The order and the expand, migrate and contract pattern are
  [rollback-plan.md](../project-management/rollback-plan.md) section 4's. GitLab's style guide runs
  regular migrations "before new application code is deployed" and the ones that remove things
  after it [21]. Where every migration runs before the new code, as in
  [deploy-example.md](deploy-example.md), a migration that removes something ships in a release
  after the one whose code stopped using it, and the rollback plan names it as a change that
  cannot be undone ([rollback-plan.md](../project-management/rollback-plan.md) section 4). On ECS, run the migration as a one-off task of the new task definition with
  `aws ecs run-task`, wait for it with `aws ecs wait tasks-stopped`, then read the container's
  `exitCode` with `aws ecs describe-tasks` and fail the job unless it is `0` [32], [33], [34]. The
  wait alone is not enough: it succeeds when the task has stopped, whatever its exit code [33], so
  a failed migration would pass in silence. The wait also gives up after about ten minutes [33], so
  a longer migration needs a wait of its own.
- **Wait for the new version to be healthy before the job ends.** A job that returns when the
  deploy starts reports green for a version that never came up.
- **Deploy a static frontend with long cache times for hashed files and none for `index.html`,
  and invalidate only `index.html`.** AWS advises versioned file names over invalidation when files
  change often [23]; Vite already gives every built asset a hash in its name. A CDN with a minimum
  TTL (time to live: how long the CDN keeps a copy before it asks the origin again) above zero
  caches even a response marked `no-cache` [7], so set the minimum to zero for the paths that must
  stay fresh.

A tab opened before a deploy keeps running the old bundle until it reloads, so for a while the new
API serves old clients. Vercel names the problem: "Version skew occurs when different versions of
your application run on client and server" [43]. The rules below keep both sides working through
that window. This practice found no case where they are too much.

- **Add no required field to the API until every open client is updated.** Malte Ubl holds that
  "Servers must never introduce new required fields in APIs until they know all clients are
  updated" [44]: add the field as optional, and make it required only in a later release, once no
  open tab can still run a bundle that does not send it. This is parallel change, "also known as
  expand and contract" [45], applied to the API; the database side of it is
  [rollback-plan.md](../project-management/rollback-plan.md) section 4.
- **Keep the hashed files of earlier versions in the site bucket for a window, and delete them on
  a schedule, never in the deploy.** Vite warns that when a host deletes "the assets from previous
  deployments", a user who loaded the site before "might encounter an import error" [46]. The
  sources choose different windows: AWS Amplify Hosting serves "one week of deployments" for a static
  application [47]; the Next.js docs say that if you "keep adding them to your existing static file
  folder (or CDN bucket), there will be no version skew" [48]; and Otto Kruse, writing on AWS's
  blog, warns that without a clean-up "old versions would pile up indefinitely" [49]. Pick a window
  longer than a tab usually stays open, such as a week, and let a job of its own delete the files no
  release in that window uses. An expiry rule by age alone is the wrong tool here: when no deploy
  has run for longer than the window, it would delete the files of the version that runs; that is
  this practice's reasoning from how such a rule works.
- **Copy the hashed files first and `index.html` last.** Amazon S3 says "There is no way to make
  atomic updates across keys" [50], and Netlify notes that with uploads to S3 "a new HTML page is
  live before the supporting assets (images, scripts, CSS) have been uploaded" when the files go up
  one by one [51]. With the assets first, a page that is already live never names a file that is
  not there yet. The order is this practice's reasoning from those two facts; no owner states it.
- **Let the application reload when it cannot load a chunk.** Vite fires `vite:preloadError` when
  a dynamic import fails, its docs show a handler that reloads the page, and the handler helps only
  when `index.html` is served with `Cache-Control: no-cache` [46], as the bullet on cache times
  above asks.

## 7. After the deploy: smoke test, watch, the way back

- **Run a smoke test against every environment right after its deploy.** Humble: "Smoke test your
  deployments. Have a script that validates all your application's dependencies are available"
  [1]. A request to the health endpoint through the CDN, and one to the page, find a broken
  deploy before a user does.
- **Turn on the platform's automatic rollback where it has one.** On ECS, the deployment circuit
  breaker "will automatically roll back a failed deployment to the deployment that is in the
  `COMPLETED` state" [24]. It catches a version that never becomes healthy; a version that is
  healthy but wrong needs the rollback plan.
- **Let the platform also roll back on an alarm, and use the same alarm as the rollback plan's
  trigger.** ECS can set a deployment to failed when a CloudWatch alarm it names goes into the
  `ALARM` state, and roll it back to the last completed deployment; for a service behind an
  Application Load Balancer, AWS recommends alarms on its `HTTPCode_ELB_5XX_Count` and
  `HTTPCode_ELB_4XX_Count` [39]. That catches part of a version that is healthy but wrong, and the
  trigger of [rollback-plan.md](../project-management/rollback-plan.md) section 2 then has a
  source in the pipeline. With rollback on, a deployment completes only after a bake time, under
  five minutes by default [39], so the deploy job's wait has to cover it (section 6). For the
  rolling update, the wait of [deploy-example.md](deploy-example.md) does: ECS keeps the old
  deployment until the bake time is over [39], the action's wait ends only when the service has one
  deployment left [54], and the action then fails the job when the new deployment has failed [53].
  That the wait therefore lasts through the bake is this practice's reading of those sources; AWS
  does not write it.
- **Make the way back a redeploy of an earlier artifact, run by the same workflow.** DORA asks that
  anyone with the right credentials can "deploy any version of the artifact to any environment on
  demand" [3]. With version tags, that is "Run workflow" on the earlier version's tag; the
  decision to roll back, who takes it and when, is
  [rollback-plan.md](../project-management/rollback-plan.md) section 2's. Such a redeploy skips
  the migration: the database already holds the newer schema, which expand, migrate and contract
  keep readable by the older code ([rollback-plan.md](../project-management/rollback-plan.md)
  section 4), while the older version's migration scripts do not know the newer revision and would
  fail. A manual run that retries the newest release, or deploys `main` to staging, runs the
  migration, because its code may need a schema the database does not have yet; in
  [deploy-example.md](deploy-example.md) the person turns the `migrate` input on for it. A
  contract migration, one that removed something, is not undone by a redeploy. The run
  uses the workflow files as they were at that tag: GitHub runs "the version of the workflow that
  is present in the associated commit SHA or Git ref of the event" [38]. A fix to the deploy steps
  therefore never reaches an older tag, so change those steps only in ways every earlier tag can
  still deploy with, and keep every variable, role name and file name an earlier tag reads until
  no rollback goes back to that tag. To rename one, add the new name beside the old one, and delete
  the old one only after the last release that reads it has left the rollback window: the earlier
  versions the rollback plan's Steps row may redeploy, such as the previous version
  ([rollback-plan.md](../project-management/rollback-plan.md) section 2).
- **Know who may start the way back, and how long it waits.** Without required reviewers on
  `production`, as for a private repository on Pro or Team, anyone with write access can redeploy
  any earlier version, so the rollback plan names who may. With required reviewers and "Prevent
  self-review" on, the person who starts the run cannot approve it [10], so the rollback waits for
  a second person: list the rollback decider's backup among the reviewers, and count that wait in
  the plan's Time row ([rollback-plan.md](../project-management/rollback-plan.md) section 2). A
  rollback also waits for the deploy that is running in that environment (section 4). When that
  deploy is the bad one, cancel it in the Actions tab first: the rollback redeploys everything the
  cancelled run touched, so section 4's "never cancel" covers a deploy nobody replaces. Count this
  wait in the Time row too.
- **Write the exact run into the rollback plan's Steps row**: the workflow's name, the previous
  version's tag under "Use workflow from", `production` as the environment, `migrate` off, and the
  link to the workflow's page in the Actions tab
  ([rollback-plan.md](../project-management/rollback-plan.md) section 2). During an incident the
  person who rolls back works from the plan, and a wrong choice costs a failed run or, with
  `migrate` on, an older tag's migration running against a schema it does not know. The rehearsal
  below runs those words with `staging` as the environment, so the plan is tested as written.
- **Rehearse the way back in staging before the release**: run the previous version's tag to
  staging and time the run for the plan's Time row, the rehearsal
  [rollback-plan.md](../project-management/rollback-plan.md) section 5 asks for.
- **Run the end-to-end tests against staging, after its deploy.** React's practice keeps a few
  Playwright paths for the flows the business cannot lose
  ([libraries.md](../../react/architecture/libraries.md) section 6); staging is the first place
  where the whole system runs together. [deploy-example.md](deploy-example.md) does not show this
  job.
- **Run the scans that need a running site against staging after its deploy, each in a job of its
  own:** the passive scan of [pipeline-security.md](pipeline-security.md) section 7 and the header
  scans of [security.md](../../react/security/security.md) section 14. After the deploy, they scan
  the version that runs; in jobs of their own, a scanner never runs next to the deploy role, which
  [pipeline-security.md](pipeline-security.md) section 7 keeps out of the deploy jobs.
- **Make a failed deploy end its run red, and let the team hear of it.** The deploy job fails when
  the deploy does, because it waits for a healthy version (section 6), so a broken release never
  shows green. Who is told, and the last job that tells the team's channel, are
  [pipeline.md](pipeline.md) section 10's; [deploy-example.md](deploy-example.md) shows that job at
  the end of the deploy workflow.
- **Advanced: hear about deployments that run outside the pipeline.** Condition: people or tools
  also change a service outside the workflow. An EventBridge rule on the ECS event
  `SERVICE_DEPLOYMENT_FAILED` reports those too, but ECS sends that event only "for services with
  deployment circuit breaker logic turned on" [55].

**Advanced: blue/green, linear and canary on ECS.** Condition: the release's way to reach users is
blue-green or canary ([release.md](../project-management/release.md) section 6). Otherwise keep the
rolling update, the default of this file and of [deploy-example.md](deploy-example.md): AWS fits it
to a team that wants "to avoid the additional resource costs of running two complete environments
simultaneously", to a service that "can tolerate a rollback process that takes minutes rather than
seconds", and to a service with no load balancer [56]. ECS runs all three strategies itself: the
service's `deploymentConfiguration` names the strategy, `BLUE_GREEN`, `LINEAR` or `CANARY` [58],
[61], [62].

- **Blue/green** "may double your resource usage during deployments", and keeps the old version
  running "until the bake time expires", which is what makes its rollback fast [57]. With an
  Application Load Balancer, the service names an alternate target group, the production listener
  rule and a role that lets ECS change the load balancer [58].
- **Canary** shifts a share of the traffic, waits, then shifts the rest; by default 5.0 percent and
  a 10-minute wait [61]. AWS asks that "database schema changes and data migrations are backward
  compatible", which [rollback-plan.md](../project-management/rollback-plan.md) section 4 already
  asks, and that the canary's share "generates sufficient traffic for meaningful validation" [59]:
  a service with little traffic learns little from a 5 percent canary.
- **Linear** shifts the traffic in equal steps of 3 to 100 percent, with a wait of 0 to 1440
  minutes between steps [60]; by default 10.0 percent steps and a 6-minute wait [62].
- **Set `bakeTimeInMinutes` yourself, and count it in the rollback plan's Time row.** CloudFormation
  sets 15 minutes for these strategies when the value is left out [63], while the API reference
  says "You must provide this parameter when you use the BLUE_GREEN deployment strategy" [64]. A
  value written down ends the doubt, and the bake is time the deploy job waits
  ([rollback-plan.md](../project-management/rollback-plan.md) section 2).
- **Roll back on CloudWatch alarms in every strategy.** AWS's command-line example for a blue/green
  service sets `alarms` with `"rollback": true` [58], and its canary and linear pages say "A
  rollback operation is initiated when issues are detected" during the bake [59], [60]. AWS's
  pages do not agree on the circuit breaker: its guide says the breaker "is only supported for
  Amazon ECS services that use the rolling update (ECS) deployment controller" [24], while the
  console steps for a blue/green service offer it [58]. So the alarms carry the rollback here.
- **After the deploy action's wait, read the service deployment's status, and fail the job unless
  it is `SUCCESSFUL`.** For these strategies no source shows that the action's wait lasts through
  the bake. A service deployment has a `status` whose values include `SUCCESSFUL`,
  `ROLLBACK_IN_PROGRESS`, `ROLLBACK_SUCCESSFUL` and `ROLLBACK_FAILED` [65], so poll
  `aws ecs describe-service-deployments` [67] until it reaches `SUCCESSFUL` or a rollback state.
  Service deployments came with AWS CLI 2.18.18; blue/green needs 2.27.51, and linear and canary
  need 2.31.24 [66].

## 8. Technologies: where a deploy goes

Pick the target by what the team can run, then let the pipeline follow it; the pipeline rules
above hold for each.

| Target | Examples | Choose it when | Its cost |
|---|---|---|---|
| Managed container service | Amazon ECS on Fargate [25], Google Cloud Run [26], Azure Container Apps [27] | one or a few services in containers, and no team to run a cluster | each vendor's own deploy model; check that its deploy action supports OIDC: Azure's Container Apps guide still stores a service principal secret [27] |
| Kubernetes with GitOps | Argo CD [28], Flux [29] | many services, a platform team, and a wish to keep cluster credentials out of CI | a cluster to run; write access to the config repository becomes production access |
| Static hosting with a CDN | S3 and CloudFront [7], Azure Static Web Apps, Netlify, Cloudflare Pages | a frontend bundle | the bundle must hold no value that differs per environment, or be built per environment (section 3) |
| Platform as a service | Heroku and the like | a small team that wants the platform to own the runtime | less control; a platform's release step, such as Heroku's, stops the release when a migration fails [30] |

**Push or pull.** Every target above takes a push from CI. With GitOps, CI only writes the new
version into a configuration repository, and an agent in the cluster pulls it: "Software agents
automatically pull the desired state declarations from the source" [31]. Argo CD highly
recommends a separate repository for that configuration [28], while Flux's guide notes that one
repository for code and manifests is common [29]. Choose GitOps when you already run Kubernetes;
for a managed service, a push with OIDC (section 5) keeps the pipeline smaller.

## 9. The infrastructure a deploy needs

A deploy needs resources that exist before it runs: the registry, the cluster and its services, the
buckets, the CDN and the OIDC roles of section 5. [deploy-example.md](deploy-example.md) assumes
they exist. Kept as code in the repository, they change through a reviewed pull request like the
workflows, staging and production are built from the same files, and a role's trust policy, which
decides who may deploy (section 5), changes only after a review. The rules use Terraform; section
14 names other tools.

**When it is too much.** Tom Elliott, working alone, created one storage bucket by hand: "a couple
of minutes", against "a few hours" to set it up in Terraform, and overwriting manual changes "isn't
a huge concern since I'm a team of one"; he expects Terraform to make sense "as I grow a team"
[75]. That is one person's case, not a measured limit. For one service on ECS, Express Mode is a
simpler start: "just provide your container image, and ECS Express Mode handles the rest" [85]
(section 14). Even without infrastructure code, keep the OIDC trust policies in a reviewed file
and apply them from it, because they decide which repositories may deploy (section 5); that is
this practice's view.

- **Keep the resources in one folder of code, with the values that differ per environment in a
  file per environment.** AWS's guidance says "Place common values at the root of the repository,
  and environment-specific values within the envs/ folder", and gives a variable whose value
  differs per environment no default [74]. A missing value then stops the plan instead of quietly
  taking another environment's.
- **Give each environment its own state backend, and let only the pipeline and a break-glass role
  change production.** AWS: "Use distinct Terraform backends for each application environment",
  and "Limit who can modify the production infrastructure to the CI/CD pipeline and break glass
  roles" [73]. A mistake in staging's state then never touches production's. On S3, use S3's own
  state locking, which AWS recommends over the deprecated DynamoDB locking [73].
- **Plan on every pull request that changes the infrastructure, with a role that can only read,
  and apply on `main` with a role that can write.** HashiCorp's workflow says "Generate a plan for
  every commit to a pull request branch" and "Apply the configuration when you update the main
  branch" [68]. AWS's role vending machine gives each role "a readonly version" for use "such as a
  terraform plan pipeline workflow", and its roles with write permissions "can only be used by
  workflows scoped to the main branch" [76]; HashiCorp says that when plan and apply need different
  access, "two separate roles and trust policies must be created" [77]. GitHub gives a pull request
  job that names no environment the `sub` `repo:<owner>/<repo>:pull_request` [15], so the plan
  role trusts that value and the apply role trusts an environment of its own; that split is this
  practice's reading of the `sub` formats, not a sentence of GitHub's. The plan on the pull request
  is what the reviewer approves: HashiCorp asks you to "Have a human operator review that plan", and
  to "Use automatic approval only with non-critical infrastructure" [69]. So staging's apply runs
  on `main`, and production's runs behind the production gate of section 4.
- **Run plan and apply in one job on `main`, and apply the plan file that job saved.** A plan made
  earlier, such as the pull request's, can differ, because "other changes made to the target system
  in the meantime might cause the final effect of a configuration change to be different" [70].
  With a saved plan, "Terraform performs the operations in the saved plan without prompting you for
  confirmation" [71], so what runs is what the job's log shows. One job also keeps the plan file on
  its runner: a plan file holds sensitive values and never goes into an upload
  ([pipeline-security.md](pipeline-security.md) section 5).
- **Treat the pull request's plan as code from outside, the way
  [pipeline-security.md](pipeline-security.md) section 5 says:** a plan role that only reads, no
  secret in the state that role reads, the infrastructure folder and its lock file under
  `CODEOWNERS`, and, where a malicious pull request from someone with write access is in your threat
  model, the further counters listed there. A role that only reads cannot write the S3 backend's
  lock file, which needs `s3:PutObject` and `s3:DeleteObject` [81], so the pull request's plan
  runs with `-lock=false`. Terraform calls that "dangerous if others might concurrently run
  commands against the same workspace" [70]; for a plan that writes nothing, the worst case is a
  plan read while an apply changes the state, which this practice accepts.
- **Create the service and its first task definition in the infrastructure code, then leave the
  revision to the deploy job.** The deploy job registers a new revision on every deploy (section
  6). Terraform says a setting "modified by processes outside of Terraform" is one "which Terraform
  attempts to resolve on the next run" [78], so without a boundary the next apply sets the first
  revision back and the old image runs again. `ignore_changes` lets "Terraform share management
  responsibilities of a single object with a separate process" [78]. The AWS provider shows it on a
  service only for `desired_count` under autoscaling [79], so using it for `task_definition` is
  this practice's use of the general mechanism; ignore `desired_count` as well when the service
  scales itself. Ignored arguments "are ignored when planning an `update` operation" [78], and a
  Terraform user reports that `ignore_changes` also quiets the drift check below for the arguments
  it names [112]; so a deploy does not set the check off. No owner text says the second part.
- **Check for drift on a schedule with
  `terraform plan -refresh-only -detailed-exitcode -lock=false -input=false`, and name who reads
  the result.** With `-detailed-exitcode` the plan exits with 2 when it finds changes
  [70]; in refresh-only mode those are changes made outside Terraform, and the same user reports
  that the command returns 2 "only when there's drift (an unapplied config change doesn't trigger
  it)" [112]. HashiCorp asks for drift checks "after deployments and during regular maintenance
  windows" and offers HCP Terraform's health assessments for them [72]; it gives no recipe for a
  scheduled command-line run, so this step is this practice's own, built from the plan command's
  exit codes. Run it with the plan role. Like the pull request's plan, it runs with `-lock=false`:
  that role cannot write the lock file [81], and this plan changes nothing. The role then also
  trusts the `sub` of a scheduled run on `main`, `repo:<owner>/<repo>:ref:refs/heads/main` [15].
  The publish jobs carry the same `sub` (section 5) and can then get this role too; it reads nothing
  secret, which is why the bullet
  above matters. Who watches a schedule is [pipeline.md](pipeline.md) section 4. Check: change one
  tag of a staging resource by hand and run the job: it exits with 2. Set the tag back, deploy, and
  run it again: it exits with 0, so a deploy alone does not set it off.

The plan job, a job of `ci.yml`, cut to the parts this section is about. The deploy workflow's `ci`
job, which calls `ci.yml` on `main`, must then grant `id-token: write` on that call too, because
"The `GITHUB_TOKEN` permissions passed from the caller workflow can be only downgraded (not
elevated) by the called workflow" [140]. The workflow around the plan job starts with
`permissions: {}`, as in [ci-example.md](ci-example.md); the `changes` job gets an `infra` output
for `infra/**` and the shared files of [ci-example.md](ci-example.md)'s filter (`*shared`), as
[pipeline.md](pipeline.md) section 7 asks, and `ci-ok` needs this job
([pipeline.md](pipeline.md) section 6):

```yaml
  infra-plan:
    needs: changes
    if: github.event_name == 'pull_request' && needs.changes.outputs.infra == 'true'
    runs-on: ubuntu-24.04  # a version label, never ubuntu-latest: the OS changes only when this line does (pipeline.md section 9)
    timeout-minutes: 15  # a hung job stops here, not at GitHub's 360 minutes (pipeline.md section 8)
    permissions:
      contents: read
      id-token: write  # the read-only plan role (table below)
    defaults:
      run:
        working-directory: infra/envs/staging  # production's plan: the same steps, its own folder and plan role
    steps:
      # Every action by full commit SHA, the release in the comment: a tag can be moved (pipeline-security.md section 4).
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false  # the token is not left on the runner for the steps after this one
      # A fork's code never runs with a cloud role: such a pull request gets no plan, so it cannot merge.
      - name: Refuse a pull request from a fork
        if: github.event.pull_request.head.repo.full_name != github.repository
        run: |
          echo "::error::A pull request from a fork gets no plan. Push its branch to this repository to plan it."
          exit 1
      - uses: aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd  # v6.3.0
        with:
          role-to-assume: ${{ vars.AWS_INFRA_PLAN_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      # Checked against the release's SHA256SUMS: a replaced or broken download fails here, before it runs with the plan role.
      - name: Install Terraform 1.16.6
        run: |
          curl -sSfL -o "$RUNNER_TEMP/terraform.zip" \
            https://releases.hashicorp.com/terraform/1.16.6/terraform_1.16.6_linux_amd64.zip
          echo "38034b38d03096399a7a1264a14561a8029b2b496fd1f169452656e53968f1b7  $RUNNER_TEMP/terraform.zip" | sha256sum --check
          unzip -q "$RUNNER_TEMP/terraform.zip" terraform -d "$RUNNER_TEMP/bin"
          echo "$RUNNER_TEMP/bin" >> "$GITHUB_PATH"
      # -lockfile=readonly: a provider the lock file does not record fails init here, before the
      # plan runs it (pipeline.md section 9).
      - run: terraform init -input=false -lockfile=readonly
      # -lock=false: the read-only role cannot write the lock file, and this plan changes nothing.
      - run: terraform plan -input=false -lock=false
```

The apply to staging, a job of `deploy.yml`, cut the same way:

```yaml
  infra-staging:
    needs: ci
    runs-on: ubuntu-24.04  # a version label, never ubuntu-latest: the OS changes only when this line does (pipeline.md section 9)
    timeout-minutes: 30  # a hung job stops here, not at GitHub's 360 minutes (pipeline.md section 8)
    # An environment only this job names, limited to main: the deploy job's sub cannot get this role.
    environment: infra-staging
    concurrency:
      group: infra-staging
      cancel-in-progress: false  # an apply cut off halfway leaves resources half changed
    permissions:
      contents: read
      id-token: write  # the staging apply role (table below)
    defaults:
      run:
        working-directory: infra/envs/staging
    steps:
      # ... the checkout, the login with vars.AWS_INFRA_APPLY_ROLE_ARN, and the Terraform install of infra-plan
      # -lockfile=readonly: a provider the lock file does not record fails init here, before the
      # plan runs it (pipeline.md section 9).
      - run: terraform init -input=false -lockfile=readonly
      # Plan and apply in one job: the plan file holds sensitive values, so it never leaves this runner.
      - run: terraform plan -input=false -out=tfplan
      - run: terraform apply -input=false tfplan  # the saved plan, as the log above shows it, with no prompt
  # staging then needs [publish-api, publish-web, infra-staging], and its if: adds
  # needs.infra-staging.result == 'success' on its push branch, since !cancelled() drops the
  # default success check. infra-production is the same job with the infra-production environment,
  # if: github.event_name == 'push' && github.ref_type == 'tag' and needs [tag-is-on-main, security]:
  # never on workflow_dispatch, so a way back on an earlier tag never applies its older
  # infrastructure. Under continuous deployment, its first step runs section 2's test,
  # git tag --list 'v*' --no-merged "$GITHUB_SHA", on a checkout with fetch-depth: 0, and fails
  # before the apply when the test prints a tag: runs of one concurrency group come in any order,
  # so an older tag could otherwise apply its infrastructure over a newer one's (section 2).
  # production needs it, and its if: adds
  # needs.infra-production.result == 'success' on its push branch (section 4).
  # The notice job needs infra-staging and infra-production too: a failed apply leaves staging or
  # production skipped, which the notice's condition does not see (section 2).
```

A deploy job names each result it depends on, because "A default status check of `success()` is
applied unless you include one of these functions" [141], and "If a job fails or is skipped, all
jobs that need it are skipped unless the jobs use a conditional expression that causes the job to
continue" [40].

The roles, in the short `sub` form; write the form your repository's tokens carry (section 5):

| Role | The `sub` it trusts | What it may do |
|---|---|---|
| infra plan, one per environment | `repo:acme-corp/shop:pull_request`, and `repo:acme-corp/shop:ref:refs/heads/main` for the drift check | read that environment's state and describe its resources; read no secret value; write nothing, the lock file included |
| infra apply, staging | `repo:acme-corp/shop:environment:infra-staging` | change staging's resources and write staging's state and lock file |
| infra apply, production | `repo:acme-corp/shop:environment:infra-production` | the same for production; its environment admits only `v*` tags (section 4) |

The line between the infrastructure code and the deploy, in `infra/modules/api/main.tf`:

```hcl
resource "aws_ecs_service" "api" {
  # ... cluster, launch type, network and load balancer
  # The first revision only; the deploy job registers every later one (section 6).
  task_definition = aws_ecs_task_definition.bootstrap.arn

  lifecycle {
    # Without it, the next apply sets the first revision back and the old image runs again.
    # Add desired_count when the service scales itself.
    ignore_changes = [task_definition]
  }
}
```

It is good because the code a pull request brings runs only with a role that reads and holds no
secret, a fork's pull request cannot merge a change nobody planned, the job that writes runs only
from an environment that admits `main`, the plan that is applied is the one in that job's log and
never leaves its runner, and the infrastructure code leaves the task definition revisions to the
deploy job that owns them. The Terraform download is checked against the checksum in the release's
`SHA256SUMS` file [82], read on 2026-10-19; the pipeline owners move the version and the checksum
by hand, as for gitleaks in [ci-example.md](ci-example.md).

The `infra/` folder at the root is a departure from
[file-structure.md](../file-structure/file-structure.md) section 9, whose root lists no folder for
infrastructure code: it holds code the pipeline runs for every environment, outside any one
application, so `CODEOWNERS` can give it one owner. The cost: a reader who knows file-structure.md
does not expect the folder.

## 10. Measuring delivery

DORA measures delivery with five metrics: three of throughput and two of instability [97]. They
tell a team whether its delivery gets faster and steadier over time; DORA's 2025 report adds that
"They tell you what is happening, but they don't explain why" [99].

**When it is too much.** DORA warns that "Building integrations to multiple systems to get precise
data about your software delivery performance might not be worth the initial investment", and that
"it might be better to start with having conversations, taking the DORA Quick Check" [97]. Its own
code for collecting the metrics, `fourkeys`, is archived and tracks the earlier four [100]. Start
with the Quick Check and the records in the table below, and build a dashboard only when someone
acts on what it shows.

- **Measure the five metrics per application, from records the pipeline already keeps.** DORA:
  the metrics "are best suited for measuring one application or service at a time" [97]. The
  definitions below are DORA's [97]; the record that answers each one is this practice's mapping,
  not DORA's.

| Metric | DORA's definition | The record that answers it |
|---|---|---|
| Change lead time | "The amount of time it takes for a change to go from committed to version control to deployed in production" | the commit's time in git, and the time of the production deployment of the first version tag that holds the commit (section 4) |
| Deployment frequency | "The number of deployments over a given period or the time between deployments" | the version tags deployed to `production` |
| Failed deployment recovery time | "The time it takes to recover from a deployment that fails and requires immediate intervention" | the incident's start and its "restored" time, from the incident the rollback work item is linked to ([rollback-plan.md](../project-management/rollback-plan.md) section 6) |
| Change fail rate | "The ratio of deployments that require immediate intervention following a deployment" | the rollback work items linked to an incident, over the production deployments ([rollback-plan.md](../project-management/rollback-plan.md) section 6) |
| Deployment rework rate | "The ratio of deployments that are unplanned but happen as a result of an incident in production" | the emergency releases ([release.md](../project-management/release.md) section 3) and the redeploys of section 7 started for an incident, over the production deployments |

- **Keep the deploy record where it outlives the workflow runs.** Since 2026-10-01, "checks,
  workflow runs, and statuses" follow the retention setting of artifacts and logs, and "the
  maximum retention for public repositories is 90 days" [101]. A metric over a year reads the
  version tags in git and the deployments that [release.md](../project-management/release.md)
  section 7 connects to Jira, not the runs.
- **Never make a metric a target, and never compare teams with it.** DORA: setting metrics as a
  goal "increases the likelihood that teams will try to game the metrics" [97]; its 2024 report
  says to use them "not to compare teams — and certainly not to compare individuals" [98]. Use
  them to see whether one application improves over time.
- **Read DORA's published numbers as survey answers, not as a bar for one team.** DORA "collects
  data through an annual, worldwide survey" [98], and its rework rate entered the 2024 report as a
  survey question [98]; the same report says the metrics "should also not be used as a maturity
  model" [98]. So this practice quotes no tier values.

## 11. Preview environments per pull request

Advanced use. Condition: two or more people change the frontend at the same time and wait for each
other on shared staging. A preview gives each pull request its own copy of the site, so a reviewer
sees the change run before the merge.

**When it is too much.** Upsun, which sells preview environments, writes that "A shared staging
server makes sense for a solo developer or a very small team with a slow release cadence", and that
the problems start with "two developers working on separate features" [103]. Kahoot moved to
previews when "a single shared experimental environment could no longer fit everyone's needs", with
eleven React applications in one repository [102]. A team of one or two keeps shared staging
(section 4); a hosted preview service is the simpler way when one is wanted (section 14).

- **Start with the frontend only: build the bundle per pull request, and serve every preview from
  one bucket and one distribution, a prefix per pull request.** At Kahoot, one S3 bucket behind
  CloudFront holds every preview under its own prefix, a CloudFront Function maps each preview's
  host name to its prefix, and the result is "almost 30 times cheaper" than a container per
  preview, a figure the post gives with no method [102]. Point the preview at the staging API: a
  cache behaviour sends `/api/*` to staging's load balancer, as the distributions of section 3 do.
  That last part is this practice's design; Kahoot's previews reached their services through
  proxies.
- **Give the preview's upload role write access to the previews bucket and nothing else.** A
  preview carries code nobody has reviewed yet, so its role never writes the staging site or the
  release store. Build the bundle in a job with no cloud role, and upload it in a second job that
  reads the built files as data ([pipeline.md](pipeline.md) section 3 splits jobs by permissions).
- **Run previews only for pull requests from branches of the repository, on `pull_request`, never
  for forks and never through `pull_request_target` or `workflow_run`.** A fork's run gets no
  secrets and a read-only token [36], and `pull_request_target` runs with the base repository's
  secrets ([pipeline-security.md](pipeline-security.md) section 5). Preview workflows have been the
  way in: at Ant Design Web3, a `workflow_run` preview deploy pasted text from a pull request's
  artifact into a shell command, which could expose its deploy token [105]; at the Eclipse Theia
  website, a `preview.yml` on `pull_request_target` ran a pull request's code with the repository's
  secrets and a token with wide write access [106]. Hosted services guard forks the same way:
  Vercel asks a member to authorize a fork's deploy, which "protects you from leaking sensitive
  project information such as environment variables and the OIDC Token" [108].
- **Protect the preview's address.** Netlify notes that preview URLs "can be shared with anyone
  with the link" unless they are protected, and that its `noindex` header "is not a guarantee"
  [51]; on Vercel, the protection setting decides whether preview URLs are public [107]. How to put
  a login in front of a CloudFront preview is not covered yet.
- **Delete a preview when its pull request closes, and keep a backstop.** A job on the `closed`
  event removes the prefix. At Kahoot that clean-up "would occasionally fail, resulting in zombie
  previews being left behind" [102], so also give the previews bucket an expiry rule: S3 "deletes
  expired objects on your behalf" [109]. A preview left idle for longer than the rule's window comes
  back with the next push.
- **Give the API an environment per pull request only when frontend previews no longer show what
  a reviewer needs.** At Nirvana Tech, sending a pull request's traffic to its own services by a
  request header failed, because "Cron jobs start themselves. Queue consumers wake on messages, not
  requests. Webhooks arrive from vendors who have never heard of our header"; they ended with
  separate Terraform stacks and a database clone per pull request [104].

## 12. Common mistakes

| Mistake | What it costs | Fix |
|---|---|---|
| A rebuild for production | production runs an artifact no test saw | section 3 |
| Deploying an image by tag | a moved tag changes what runs, and a rollback cannot name the old version | section 3 |
| A stored cloud access key | a leaked key works until someone rotates it | section 5 |
| A trust policy with a wildcard `sub` | any repository on GitHub may assume the role | section 5 |
| The API address baked into the bundle | one bundle per environment, and staging no longer tests the production bytes | section 3 |
| A deploy job that returns before the service is healthy | a green deploy of a version that never started | section 6 |
| Copies of the deploy steps per environment | the production copy drifts from the one that is tested | section 6 |
| Cancelling a running deploy for a newer one | half the service runs each version | section 4 |
| `aws s3 sync --delete` into the site bucket | it deletes "Files that exist in the destination but not in the source" [52], the old hashed files that open tabs still load | section 6 |
| Infrastructure code that also sets the task definition the deploy job registers | the next apply sets the old revision back, and the old image runs again [78] | section 9 |
| A plan file or a state file uploaded as a workflow artifact | every reader of the repository can read the sensitive values in it [80] | section 9 and [pipeline-security.md](pipeline-security.md) section 5 |

## 13. Where the rules stop holding

- **A library, a CLI tool, or an image published by a workflow that deploys nothing**
  ([docker/ci-example.md](../docker/ci-example.md)): nothing is deployed; the artifact is published
  once to a registry, an image's version tag goes on the digest `main` already pushed
  ([images.md](../docker/images.md) section 8), and section 3's build-once rule is the only one
  that applies.
- **Continuous deployment in a scope that asks for an independent approver.** The EU's ICT risk
  rules for financial entities ask, for all changes to software, for "mechanisms to ensure the
  independence of the functions that approve changes and the functions responsible for requesting
  and implementing those changes" [128], and the European Supervisory Authorities kept that clause
  when respondents asked them to re-evaluate the segregation of duties [129]. Singapore's MAS
  expects financial institutions "to apply security measures and segregation of duties principles
  at critical junctures in the DevOps processes, where relevant, even when these processes are
  automated" [130]. PCI DSS v4.0, requirement 6.2.3.1, asks that where custom software gets a
  manual code review before release, someone other than the author reviews each change and
  management approves it before release; a person formally given release control who is neither
  the author nor the reviewer counts as management [131]. In such a scope keep continuous delivery
  with the named decider (section 2), or agree the pipeline's controls with the auditor.
- **A plan without deployment branch rules for private repositories (GitHub Free)**: environments
  are not available there [11], and neither are rulesets
  ([ruleset-example.md](../git/ruleset-example.md)), so every person with write access
  can deploy to production: a workflow-level check on the ref sits in a file that same person can
  change. Deploy from a public repository, or move to a paid plan; do not use this deploy on such
  a plan.
- **A framework that renders on the server**: the bundle is part of a server image, so it follows
  the image's rules, and section 3's static-hosting advice does not apply.
- **Regulated change control.** DORA names segregation of duties, "which states that changes must
  be approved by someone other than the author", as a common regulatory requirement, and asks teams
  to meet it with peer review, "with reviews, comments, and approvals captured in the team's
  development platform" [13]. NIST SP 800-53's control CM-3 asks to "Review proposed
  configuration-controlled changes to the system and approve or disapprove such changes", to
  document the decisions, to "Retain records of configuration-controlled changes", and to have a
  change control element the organisation names oversee the work; its guidance gives change boards
  as examples of such processes [110]. CM-3 is in NIST's Moderate and High baselines and not in
  Low, and its enhancement that asks to "Prohibit changes to the system until designated approvals
  are received" is in High only [111]. In this pipeline the review of the pull request, the version
  tag the go or no-go decider creates (section 4) and the deployment records give the review, the
  approval and the record; who oversees them is the organisation's to name. Under continuous
  deployment the decider's approval of the gates and the reviewer's approval of each pull request
  give the approval, and the version tags the job creates with the deployment records give the
  record (section 2). What SOC 2, ISO 27001 and ITIL's change enablement practice ask is not
  covered yet: their texts were not readable for this practice, so ask your auditor. A repository with one person cannot show segregation of duties, because the author
  cannot approve their own pull request ([pipeline.md](pipeline.md) section 12).

## 14. Alternatives considered

- **One build per environment.** Rejected as the default, because the bytes in production were
  never tested in staging; kept as the declared exception when the bundle must hold a value that
  differs (section 3).
- **One frontend build with a config file loaded at start.** Practitioners ship one bundle to
  many environments by serving a `config.json` or `config.js` per environment that the app reads
  when it starts [8], [9], [35]. It costs a request before the app can run; the file has no hash in
  its name, so it is served uncached, as Sanetra advises for every such file [8]; and anyone can
  read it, so, in Erez's words, "If you're concerned about leaking sensitive information, then
  perhaps the front-end isn't the right place for that information" [35]. Not the default here,
  because it changes where the React app reads its settings, which
  [architecture.md](../../react/architecture/architecture.md) section 3 owns.
- **The deploy action's own one-off task.** `amazon-ecs-deploy-task-definition` can run a task
  before it updates the service, and its README says "the service would not be updated until the
  ad-hoc task exits successfully" [22]; it does not say that the step fails, so section 6 checks
  the exit code itself.
- **A manual "Run workflow" on `main` as the production gate.** It works on every plan, but
  anyone with write access can run it, and it records no version. A protected tag does both
  (section 4).
- **Required reviewers as the only gate.** Unavailable for private repositories below Enterprise
  [11]; used in addition where it is available.
- **Jira Service Management deployment gating, for a team that already runs its change management
  there.** It lets a team "allow or prevent deployments at specific points in the change management
  process" [132]: on GitHub, Jira becomes a custom deployment protection rule, and "GitHub will halt
  deployments for the environments selected until it receives approval from Jira Service
  Management" [133], so each deploy waits for its change request to be approved. Its cost: change
  management moved to the Premium and Enterprise plans on 2024-10-16 [134], and on GitHub custom
  protection rules are "currently in public preview and subject to change" and need GitHub
  Enterprise in private repositories [135]. Not the default, because it puts a person's approval
  back on every deploy, which section 2 replaces with gates the decider approved once.
- **A personal access token as the tag job's credential.** It would also start the production run
  [116], but such tokens "are tied to the user who generated them and will become inactive if the
  user loses access to the resource" [136], so the release path breaks when that person leaves.
  Section 2 uses a GitHub App.
- **A production deploy straight from `main`, with no tag, under continuous deployment.** Rejected:
  GitHub keeps deployment statuses for 90 days [113], so the tag is the lasting record of what
  shipped and the handle the way back uses (section 7), and a second path to production would break
  "the only method of deployment" that Atlassian asks of such a pipeline [114].
- **Chaining the deploy with `workflow_run`.** Rejected: it starts "regardless of the conclusion"
  of the run it follows unless the job checks it, and it runs with the default branch's privileges
  ([pipeline-security.md](pipeline-security.md) section 5). Calling CI with `workflow_call` and
  `needs` keeps the order in one run.
- **`queue: max` on the deploy's concurrency group.** GitHub's `queue: max` keeps up to 100 runs
  waiting [40]; not set here, because actionlint 1.7.12, which the security jobs run, rejects the
  key [42]; add it when an actionlint release accepts it.
- **ECS Express Mode, for one service with no infrastructure code.** AWS: "just provide your
  container image, and ECS Express Mode handles the rest", "at no additional charge" [85]. It is the
  simpler start that section 9 names; take section 9 when the resources must be reviewed as code.
  AWS Copilot CLI is no longer a choice: AWS announced that it "will reach end of support on June
  12, 2026" [86], a date that has passed.
- **CloudFormation or the AWS CDK instead of Terraform, for a team that runs only on AWS.** A change
  set lets you "preview how proposed changes to a stack might impact your running resources", though
  change sets "don't guarantee that CloudFormation will successfully update a stack" [87];
  drift-aware change sets show whether a deploy "will revert critical out-of-band changes made
  during incident response" [88]; and drift detection only checks "property values that are
  explicitly set" [89]. In the CDK, `cdk diff --fail` exits with 1 when it finds a difference [90],
  which serves as the plan check on a pull request. Either fits a team that runs only on AWS;
  section 9 shows Terraform because one tool had to be shown.
- **OpenTofu instead of Terraform.** Terraform 1.6.0 and later are under the Business Source
  License, whose grant reads "You may make production use of the Licensed Work", unless you offer
  it to others "on a hosted or embedded basis in order to compete with" IBM's paid versions [91];
  running it in your own pipeline is production use under that grant, as this practice reads it.
  OpenTofu is under the Mozilla Public License 2.0 [92] and "aims to maintain compatibility with
  Terraform configurations" [93]. Its state encryption does not change section 9's rules: OpenTofu
  "does not and cannot protect the sensitive values in the state file from the person running the
  `tofu` command" [94], and a pull request's plan is such a person.
- **`track_latest` on the task definition resource.** Where the infrastructure code owns the task
  definition resource, the AWS provider's `track_latest` follows the latest `ACTIVE` revision; the
  provider calls it "Useful in the event the task definition is modified outside of this resource"
  [84]. Not the default, because section 9 leaves the revisions to the deploy job.
- **HCP Terraform's health assessments for drift.** They "run periodic refresh-only Terraform
  plans" [72], and drift detection there "is available in HCP Terraform Standard Edition", with the
  pricing page for details [83]. Section 9's scheduled plan does the same inside the pipeline.
- **A plain plan of `main` as the drift check.** Answering the user of section 9, a member of the
  HashiCorp organization holds that from Terraform's view drift "is what's encountered when running
  a plan with the most recently applied configuration", which "avoids all the inherent noise caused
  by unused computed values" [112]. On `main`, where every merge applies, that check is
  `terraform plan -detailed-exitcode`. Section 9 keeps `-refresh-only`, which HashiCorp's own drift
  guidance uses [72], [83], because it reports only changes made outside Terraform. Take the plain
  plan where the refresh-only check turns out noisy for your provider.
- **ECS blue/green through CodeDeploy.** For a new service AWS writes "We recommend that you use the
  Amazon ECS blue/green deployment" [95], and its blog keeps CodeDeploy as "a valid option for
  existing customers" [96]. Section 7 uses the strategies ECS runs itself.
- **A hosted preview service instead of section 11's own previews.** Vercel holds back a fork's
  deploy until a member authorizes it [108], and Netlify holds back deploys by authors outside the
  team until an owner approves them [51]. It is the simpler way for a frontend a team can host
  there; their preview URLs are open to anyone with the link unless protection is set up [51],
  [107].

## 15. Sources

Checked 2026-10-18 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Jez Humble — Patterns (continuousdelivery.com, no date; opinion) — https://continuousdelivery.com/implementing/patterns/
- [2] DORA — Capabilities: Continuous delivery — https://dora.dev/capabilities/continuous-delivery/
- [3] DORA — Capabilities: Deployment automation — https://dora.dev/capabilities/deployment-automation/
- [4] Adam Wiggins — The Twelve-Factor App: V. Build, release, run (12factor.net, 2017; opinion) — https://12factor.net/build-release-run
- [5] GitHub — Managing GitHub Actions settings for a repository: artifact and log retention — https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- [6] Vite — Env Variables and Modes, Vite 8 — https://vite.dev/guide/env-and-mode
- [7] AWS — Amazon CloudFront Developer Guide: Cache behavior settings — https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistValuesCacheBehavior.html
- [8] Philip Sanetra — Deployment of configurable Single Page Applications (codecentric, 2021; opinion) — https://www.codecentric.de/wissens-hub/blog/deployment-configurable-single-page-application
- [9] Arron Atchison — feat(frontend): runtime SPA config via /config.js, pull request 1748 (github.com/thunderbird/appointment, 2026; case) — https://github.com/thunderbird/appointment/pull/1748
- [10] GitHub — Deployments and environments — https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- [11] GitHub — Environments: availability by plan (`gated-features/environments`) — https://github.com/github/docs/blob/main/data/reusables/gated-features/environments.md
- [12] GitHub — Available rules for rulesets — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets — checked 2026-10-19
- [13] DORA — Capabilities: Streamlining change approval — https://dora.dev/capabilities/streamlining-change-approval/ — checked 2026-10-19
- [14] GitHub — Control deployments — https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments
- [15] GitHub — OpenID Connect reference — https://docs.github.com/en/actions/reference/security/oidc — checked 2026-10-19
- [16] AWS — IAM User Guide: Create a role for OpenID Connect federation — https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html
- [17] Christophe Tafani-Dereeper — Exploring GitHub-to-AWS keyless authentication flaws (Datadog Security Labs, 2023; research) — https://securitylabs.datadoghq.com/articles/exploring-github-to-aws-keyless-authentication-flaws/
- [18] GitHub — Immutable subject claims for GitHub Actions OIDC tokens (changelog, 2026-04-23) — https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens/
- [19] Seth Larson — Supply-chain attack analysis: Ultralytics (PyPI blog, 2024; case) — https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/
- [20] AWS — Amazon ECS Developer Guide: Pass Secrets Manager secrets through environment variables — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/secrets-envvar-secrets-manager.html
- [21] GitLab — Migration style guide — https://docs.gitlab.com/development/migration_style_guide/
- [22] AWS — amazon-ecs-deploy-task-definition, README, v2.6.4 — https://github.com/aws-actions/amazon-ecs-deploy-task-definition/blob/v2.6.4/README.md
- [23] AWS — Amazon CloudFront Developer Guide: Invalidate files to remove content — https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html
- [24] AWS — Amazon ECS Developer Guide: How the Amazon ECS deployment circuit breaker detects failures — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-circuit-breaker.html — checked 2026-10-19
- [25] AWS — amazon-ecs-render-task-definition, README, v1.9.1 — https://github.com/aws-actions/amazon-ecs-render-task-definition/blob/v1.9.1/README.md
- [26] Google Cloud — Deploying container images to Cloud Run — https://docs.cloud.google.com/run/docs/deploying
- [27] Microsoft — Azure Container Apps: Deploy with GitHub Actions — https://learn.microsoft.com/en-us/azure/container-apps/github-actions
- [28] Argo CD — Best practices — https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/
- [29] Flux — Ways of structuring your repositories — https://fluxcd.io/flux/guides/repository-structure/
- [30] Heroku — Release phase — https://devcenter.heroku.com/articles/release-phase
- [31] OpenGitOps — GitOps Principles, v1.0.0 — https://opengitops.dev/
- [32] AWS — AWS CLI Command Reference: ecs run-task, version 2 — https://docs.aws.amazon.com/cli/latest/reference/ecs/run-task.html
- [33] AWS — AWS CLI Command Reference: ecs wait tasks-stopped, version 2 — https://docs.aws.amazon.com/cli/latest/reference/ecs/wait/tasks-stopped.html
- [34] AWS — AWS CLI Command Reference: ecs describe-tasks, version 2 — https://docs.aws.amazon.com/cli/latest/reference/ecs/describe-tasks.html
- [35] Robert Erez — Providing Environment Specific Configuration For JavaScript Projects (Octopus blog, 2019; opinion) — https://octopus.com/blog/javascript-configuration
- [36] GitHub — Events that trigger workflows: `create`, `push` and `pull_request` — https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- [37] GitHub — Managing environments for deployment — https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments — checked 2026-10-19
- [38] GitHub — Workflows: triggering a workflow — https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows
- [39] AWS — Amazon ECS Developer Guide: How CloudWatch alarms detect Amazon ECS deployment failures — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-alarm-failure.html — checked 2026-10-19
- [40] GitHub — Workflow syntax for GitHub Actions: `concurrency` and `jobs.<job_id>.needs` — https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax — checked 2026-10-19
- [41] GitHub — Viewing deployment history — https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/view-deployment-history
- [42] rhysd — actionlint, `parse.go` (the keys `concurrency` accepts), v1.7.12 — https://github.com/rhysd/actionlint/blob/v1.7.12/parse.go#L817-L825
- [43] Vercel — Skew Protection — https://vercel.com/docs/skew-protection — checked 2026-10-19
- [44] Malte Ubl — Version Skew (Industrial Empathy, 2023; opinion) — https://industrialempathy.com/posts/version-skew/ — checked 2026-10-19
- [45] Danilo Sato — Parallel Change (martinfowler.com, 2014; opinion) — https://martinfowler.com/bliki/ParallelChange.html — checked 2026-10-19
- [46] Vite — Building for Production: Load Error Handling, Vite 8 — https://vite.dev/guide/build.html#load-error-handling — checked 2026-10-19
- [47] AWS — AWS Amplify Hosting User Guide: Skew protection for Amplify deployments — https://docs.aws.amazon.com/amplify/latest/userguide/skew-protection.html — checked 2026-10-19
- [48] Vercel — Next.js docs: How to self-host your Next.js application (Immutable Assets) — https://nextjs.org/docs/app/guides/self-hosting — checked 2026-10-19
- [49] Otto Kruse — Host single page applications (SPA) with tiered TTLs on CloudFront and S3 (AWS Networking & Content Delivery Blog, 2023; opinion) — https://aws.amazon.com/blogs/networking-and-content-delivery/host-single-page-applications-spa-with-tiered-ttls-on-cloudfront-and-s3/ — checked 2026-10-19
- [50] AWS — Amazon S3 User Guide: What is Amazon S3? (data consistency) — https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html — checked 2026-10-19
- [51] Netlify — Deploy overview (atomic deploys, deploy previews, deploy request policy) — https://docs.netlify.com/site-deploys/overview/ — checked 2026-10-19
- [52] AWS — AWS CLI Command Reference: s3 sync (`--delete`), version 2 — https://docs.aws.amazon.com/cli/latest/reference/s3/sync.html — checked 2026-10-19
- [53] AWS — amazon-ecs-deploy-task-definition, `index.js` (the check after the wait), v2.6.4 — https://github.com/aws-actions/amazon-ecs-deploy-task-definition/blob/v2.6.4/index.js#L260-L290 — checked 2026-10-19
- [54] AWS — AWS SDK for JavaScript v3, client-ecs `waitForServicesStable`, v3.1086.0 — https://github.com/aws/aws-sdk-js-v3/blob/v3.1086.0/clients/client-ecs/src/waiters/waitForServicesStable.ts — checked 2026-10-19
- [55] AWS — Amazon ECS Developer Guide: Amazon ECS service deployment state change events — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_service_deployment_events.html — checked 2026-10-19
- [56] AWS — Amazon ECS Developer Guide: Amazon ECS service deployment controllers and strategies — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_service-options.html — checked 2026-10-19
- [57] AWS — Amazon ECS Developer Guide: Amazon ECS blue/green deployments — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-blue-green.html — checked 2026-10-19
- [58] AWS — Amazon ECS Developer Guide: Creating an Amazon ECS blue/green deployment — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deploy-blue-green-service.html — checked 2026-10-19
- [59] AWS — Amazon ECS Developer Guide: Amazon ECS canary deployments — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/canary-deployment.html — checked 2026-10-19
- [60] AWS — Amazon ECS Developer Guide: Amazon ECS linear deployments — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-linear.html — checked 2026-10-19
- [61] AWS — Amazon ECS API Reference: CanaryConfiguration — https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_CanaryConfiguration.html — checked 2026-10-19
- [62] AWS — Amazon ECS API Reference: LinearConfiguration — https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_LinearConfiguration.html — checked 2026-10-19
- [63] AWS — AWS CloudFormation Template Reference: AWS::ECS::Service DeploymentConfiguration — https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-ecs-service-deploymentconfiguration.html — checked 2026-10-19
- [64] AWS — Amazon ECS API Reference: DeploymentConfiguration — https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_DeploymentConfiguration.html — checked 2026-10-19
- [65] AWS — Amazon ECS API Reference: ServiceDeployment — https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_ServiceDeployment.html — checked 2026-10-19
- [66] AWS — AWS CLI version 2, `CHANGELOG.rst` (releases 2.18.18, 2.27.51 and 2.31.24) — https://github.com/aws/aws-cli/blob/v2/CHANGELOG.rst — checked 2026-10-19
- [67] AWS — AWS CLI Command Reference: ecs describe-service-deployments, version 2 — https://docs.aws.amazon.com/cli/latest/reference/ecs/describe-service-deployments.html — checked 2026-10-19
- [68] HashiCorp — Terraform tutorial: Automate Terraform with GitHub Actions — https://developer.hashicorp.com/terraform/tutorials/automation/github-actions
- [69] HashiCorp — Terraform tutorial: Running Terraform in automation — https://developer.hashicorp.com/terraform/tutorials/automation/automate-terraform
- [70] HashiCorp — Terraform CLI: terraform plan command reference — https://developer.hashicorp.com/terraform/cli/commands/plan
- [71] HashiCorp — Terraform CLI: terraform apply command reference (Saved Plan Mode), v1.16.x — https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.16.x/docs/cli/commands/apply.mdx — checked 2026-10-19
- [72] HashiCorp — Well-Architected Framework: Automatically detect resource drift and health — https://developer.hashicorp.com/well-architected-framework/optimize-systems/monitor-system-health/detect-configuration-drift
- [73] AWS — AWS Prescriptive Guidance, Terraform AWS Provider best practices: Backend best practices — https://docs.aws.amazon.com/prescriptive-guidance/latest/terraform-aws-provider-best-practices/backend.html
- [74] AWS — AWS Prescriptive Guidance, Terraform AWS Provider best practices: Best practices for code base structure and organization — https://docs.aws.amazon.com/prescriptive-guidance/latest/terraform-aws-provider-best-practices/structure.html
- [75] Tom Elliott — "Best practices" aren't always best for you (The Friday Deploy, 2025; case) — https://thefridaydeploy.substack.com/p/best-practices-arent-always-best
- [76] AWS — AWS Prescriptive Guidance: Provision least-privilege IAM roles by deploying a role vending machine solution — https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/provision-least-privilege-iam-roles-by-deploying-a-role-vending-machine-solution.html
- [77] HashiCorp — Terraform Enterprise: Use dynamic credentials with the AWS provider — https://developer.hashicorp.com/terraform/enterprise/dynamic-provider-credentials/aws-configuration
- [78] HashiCorp — Terraform language: The lifecycle meta-argument (`ignore_changes`), v1.16.x — https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.16.x/docs/language/meta-arguments/lifecycle.mdx
- [79] HashiCorp — Terraform AWS provider: `aws_ecs_service` resource (Ignoring Changes to Desired Count) — https://github.com/hashicorp/terraform-provider-aws/blob/main/website/docs/r/ecs_service.html.markdown
- [80] HashiCorp — Terraform language: Manage sensitive data, v1.16.x — https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.16.x/docs/language/manage-sensitive-data/index.mdx
- [81] HashiCorp — Terraform: Backend Type s3 (the permissions the lock file needs) — https://developer.hashicorp.com/terraform/language/backend/s3
- [82] HashiCorp — Terraform 1.16.6, `terraform_1.16.6_SHA256SUMS` — https://releases.hashicorp.com/terraform/1.16.6/terraform_1.16.6_SHA256SUMS — checked 2026-10-19
- [83] HashiCorp — Terraform tutorial: Manage resource drift — https://developer.hashicorp.com/terraform/tutorials/state/resource-drift
- [84] HashiCorp — Terraform AWS provider: `aws_ecs_task_definition` resource (`track_latest`) — https://github.com/hashicorp/terraform-provider-aws/blob/main/website/docs/r/ecs_task_definition.html.markdown
- [85] AWS — Announcing Amazon ECS Express Mode (What's New, 2025-11-21) — https://aws.amazon.com/about-aws/whats-new/2025/11/announcing-amazon-ecs-express-mode/ — checked 2026-10-19
- [86] AWS — Announcing the end-of-support for the AWS Copilot CLI (AWS Containers blog, 2026-03-06) — https://aws.amazon.com/blogs/containers/announcing-the-end-of-support-for-the-aws-copilot-cli
- [87] AWS — AWS CloudFormation User Guide: Update CloudFormation stacks using change sets — https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html — checked 2026-10-19
- [88] AWS — AWS CloudFormation User Guide: Using drift-aware change sets — https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/drift-aware-change-sets.html — checked 2026-10-19
- [89] AWS — AWS CloudFormation User Guide: Detect unmanaged configuration changes to stacks and resources with drift detection — https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html — checked 2026-10-19
- [90] AWS — AWS CDK v2 Developer Guide: cdk diff — https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd-diff.html — checked 2026-10-19
- [91] IBM — Terraform, `LICENSE` (Business Source License 1.1, Additional Use Grant) — https://github.com/hashicorp/terraform/blob/main/LICENSE — checked 2026-10-19
- [92] OpenTofu — `LICENSE` (Mozilla Public License 2.0), v1.13.1 — https://github.com/opentofu/opentofu/blob/v1.13.1/LICENSE — checked 2026-10-19
- [93] OpenTofu — Migrating to OpenTofu from Terraform — https://opentofu.org/docs/intro/migration/ — checked 2026-10-19
- [94] OpenTofu — State and plan encryption (`encryption.mdx`) — https://github.com/opentofu/opentofu/blob/main/website/docs/language/state/encryption.mdx
- [95] AWS — Amazon ECS Developer Guide: CodeDeploy blue/green deployments for Amazon ECS — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-bluegreen.html — checked 2026-10-19
- [96] Franco Abregu and Chris Renzo — Choosing between Amazon ECS Blue/Green Native or AWS CodeDeploy in AWS CDK (AWS DevOps & Developer Productivity Blog, 2026; opinion) — https://aws.amazon.com/blogs/devops/choosing-between-amazon-ecs-blue-green-native-or-aws-codedeploy-in-aws-cdk/ — checked 2026-10-19
- [97] DORA — DORA's software delivery performance metrics (guide) — https://dora.dev/guides/dora-metrics/
- [98] DORA — Accelerate State of DevOps Report 2024, v2024.3 — https://services.google.com/fh/files/misc/2024_final_dora_report.pdf
- [99] DORA — State of AI-assisted Software Development 2025, v2025.2 — https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf
- [100] DORA — `dora-team/fourkeys` repository (archived; its description and last push) — https://github.com/dora-team/fourkeys
- [101] GitHub — Actions retention now covers checks, runs, and statuses (changelog, 2026-10-01) — https://github.blog/changelog/2026-10-01-actions-retention-now-covers-checks-runs-and-statuses/
- [102] Nikolaos Gkarlis — Handling thousands of pull-request development environments at Kahoot! (Kahoot! Tech Blog, 2023; case) — https://kahoot.com/tech-blog/handling-thousands-of-pull-request-development-environments-at-kahoot/
- [103] Upsun — Why your team keeps waiting for staging (and what to do about it) (Upsun blog, 2026; opinion, from a vendor of preview environments) — https://upsun.com/blog/staging-bottleneck-preview-environments/
- [104] Katam Bala — Every Pull Request Gets Its Own Environment. Here's the System We Built to Do It (Nirvana Tech blog, 2026; case) — https://www.nirvanatech.com/blog/every-pull-request-gets-its-own-environment-heres-the-system-we-built-to-do-it
- [105] Jaroslav Lobačevski — GHSL-2024-281: Actions expression injection in Ant-design-web3 (GitHub Security Lab, 2025; case) — https://securitylab.github.com/advisories/GHSL-2024-281_Ant-design-web3
- [106] Eclipse Foundation — CVE-2026-1699, Eclipse Theia Website `preview.yml` (CVE record, 2026-01-30) — https://www.cve.org/CVERecord?id=CVE-2026-1699
- [107] Vercel — Deployment Protection on Vercel — https://vercel.com/docs/deployment-protection
- [108] Vercel — Deploying GitHub Projects with Vercel: Deployment Authorizations for Forks — https://vercel.com/docs/git/vercel-for-github
- [109] AWS — Amazon S3 User Guide: Managing the lifecycle of objects (expiration actions) — https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html — checked 2026-10-19
- [110] NIST — SP 800-53 Rev. 5.2.0, CM-3 Configuration Change Control (OSCAL catalog) — https://github.com/usnistgov/oscal-content/blob/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json — checked 2026-10-19
- [111] NIST — SP 800-53 Rev. 5.2.0 baselines, LOW, MODERATE and HIGH profiles (OSCAL) — https://github.com/usnistgov/oscal-content/tree/main/nist.gov/SP800-53/rev5/json — checked 2026-10-19
- [112] ajoshi01ai, with a reply by jbardin, a HashiCorp organization member — A first-class `terraform drift` command for detecting infrastructure changed outside of Terraform, issue 39172 (github.com/hashicorp/terraform, 2026; opinion) — https://github.com/hashicorp/terraform/issues/39172 — checked 2026-10-19
- [113] GitHub — REST API endpoints for deployment statuses — https://docs.github.com/en/rest/deployments/statuses — checked 2026-10-19
- [114] Sten Pittet — What Is Continuous Deployment? (Atlassian, no date; opinion) — https://www.atlassian.com/continuous-delivery/software-testing/continuous-deployment — checked 2026-10-19
- [115] GitHub — `actions-do-not-trigger-workflows` (the text the `GITHUB_TOKEN` pages share) — https://github.com/github/docs/blob/24a7a1dca982b66ffe56e2c51faad1f83a12b3bf/data/reusables/actions/actions-do-not-trigger-workflows.md
- [116] GitHub — Triggering a workflow (`trigger-a-workflow.md`) — https://github.com/github/docs/blob/1484a08c7c5658e8f2c336d7422eba111f48f564/content/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow.md
- [117] GitHub — Making authenticated API requests with a GitHub App in a GitHub Actions workflow — https://github.com/github/docs/blob/0b762b0ae89dddf9a12b1bcf216a6eb2f9fb46c7/content/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow.md
- [118] GitHub — Rulesets: who can be granted bypass (`rulesets-bypass-step.md`) — https://github.com/github/docs/blob/4780141748da1eac03fa8ac65c96e2bb550bec96/data/reusables/repositories/rulesets-bypass-step.md
- [119] GitHub — create-github-app-token, README, v3.3.0 — https://github.com/actions/create-github-app-token/blob/v3.3.0/README.md
- [120] GitHub — REST API endpoints for Git references: Create a reference — https://docs.github.com/en/rest/git/refs — checked 2026-10-19
- [121] Kishan Sathyanarayanan — A Candid Look at the Shifting Landscape of Change Management for Audit (ISACA Journal, 2023; opinion) — https://www.isaca.org/resources/isaca-journal/issues/2023/volume-4/a-candid-look-at-the-shifting-landscape-of-change-management-for-audit — checked 2026-10-19
- [122] Evan Bass and W. Noel Haskins-Hafer — Speeding Up Software Delivery With Effective Change Management (ISACA Journal, 2018; opinion) — https://www.isaca.org/resources/isaca-journal/issues/2018/volume-5/speeding-up-software-delivery-with-effective-change-management — checked 2026-10-19
- [123] Rhandeev Singh and Sebastian Kirsch with Vivek Rau — Reliable Product Launches at Scale, chapter 27 of Site Reliability Engineering (O'Reilly, 2016; case) — https://sre.google/sre-book/reliable-product-launches/ — checked 2026-10-19
- [124] Clare Liguori — Automating safe, hands-off deployments (Amazon Builders' Library, 2020; case) — https://builder.aws.com/content/3ErTKQOTKc5NIw031UePBPxTQ6I/automating-safe-hands-off-deployments — checked 2026-10-19
- [125] Alec Warner and Štěpán Davidovič — Canarying Releases, chapter 16 of The Site Reliability Workbook (O'Reilly, 2018; case) — https://sre.google/workbook/canarying-releases/ — checked 2026-10-19
- [126] Sandeep Pokkunuri — Ensuring rollback safety during deployments (Amazon Builders' Library, 2019; case) — https://builder.aws.com/content/3F04j2yRAAMBuPSPs50xwXZqg01/ensuring-rollback-safety-during-deployments — checked 2026-10-19
- [127] Ariga — Atlas Guides: Destructive Change Policy — https://atlasgo.io/guides/destructive-change-policy — checked 2026-10-19
- [128] European Commission — Commission Delegated Regulation (EU) 2024/1774 of 13 March 2024, Article 17 (ICT change management) — https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32024R1774 — checked 2026-10-19
- [129] European Supervisory Authorities — Final report on draft RTS on ICT risk management framework (JC 2023 86), 17 January 2024 — https://www.esma.europa.eu/sites/default/files/2024-01/JC_2023_86_-_Final_report_on_draft_RTS_on_ICT_Risk_Management_Framework_and_on_simplified_ICT_Risk_Management_Framework.pdf — checked 2026-10-19
- [130] Monetary Authority of Singapore — Response to feedback received on proposed revisions to Technology Risk Management Guidelines, January 2021 (paragraph 6.23) — https://www.mas.gov.sg/-/media/MAS/News-and-Publications/Consultation-Papers/Response-to-Consultation-Paper_TRM-Guidelines-2021.pdf — checked 2026-10-19
- [131] PCI Security Standards Council — PCI DSS v4.0, requirement 6.2.3.1, official German translation, March 2022 — https://listings.pcisecuritystandards.org/documents/PCI-DSS-v4_0-DE.pdf — checked 2026-10-19
- [132] Atlassian — Jira Service Management Cloud: What is deployment gating? — https://support.atlassian.com/jira-service-management-cloud/docs/what-is-deployment-gating/ — checked 2026-10-19
- [133] Atlassian — Jira Service Management Cloud: Use deployment gating with GitHub — https://support.atlassian.com/jira-service-management-cloud/docs/use-deployment-gating-with-github/ — checked 2026-10-19
- [134] Atlassian — Jira Service Management pricing and packaging updates (announcement, 2024-10-29) — https://www.atlassian.com/blog/announcements/jsm-cloud-pricing-packaging-update — checked 2026-10-19
- [135] GitHub — Creating custom deployment protection rules — https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/create-custom-protection-rules — checked 2026-10-19
- [136] GitHub — Managing your personal access tokens — https://github.com/github/docs/blob/3363b628fcf4ff0bb946e782a1f2ae9294bb0ddd/content/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens.md
- [137] GitHub — Contexts reference: context availability — https://docs.github.com/en/actions/reference/workflows-and-actions/contexts — checked 2026-10-19
- [138] GitHub — About code owners (`about-code-owners.md`) — https://github.com/github/docs/blob/0b183d589a7f22b5ed23a4b4b7f40eb4cc0dbe0a/content/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners.md — checked 2026-10-19
- [139] GitHub — Store information in variables: creating configuration variables for a repository — https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-variables — checked 2026-10-19
- [140] GitHub — Reusing workflow configurations (`reusing-workflow-configurations.md`) — https://github.com/github/docs/blob/be60fe44225664211ee6d410a17b06eb259f3bab/content/actions/reference/workflows-and-actions/reusing-workflow-configurations.md — checked 2026-10-19
- [141] GitHub — Evaluate expressions in workflows and actions: status check functions (`expressions.md`) — https://github.com/github/docs/blob/b32e08ff7345b996e5bb059bfd5bfc11d08bcc36/content/actions/reference/workflows-and-actions/expressions.md — checked 2026-10-19
- [142] Git — git-tag documentation (`--no-merged`), 2.55.0 — https://git-scm.com/docs/git-tag/2.55.0 — checked 2026-10-19
- [143] GitHub — actions/checkout, README, v7.0.1 — https://github.com/actions/checkout/blob/v7.0.1/README.md — checked 2026-10-19
