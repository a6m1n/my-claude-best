# CD rules: build once, promote, deploy

This file is for everyone who writes or changes a deploy workflow, people and AI agents alike.
It says how an artifact is built once and promoted through the environments, how a deploy job
reaches the cloud without a stored key, what a deploy job holds, how production is gated, and
which technologies a deploy can target. Who decides that a release goes to production, which
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
- [9. Common mistakes](#9-common-mistakes)
- [10. Where the rules stop holding](#10-where-the-rules-stop-holding)
- [11. Alternatives considered](#11-alternatives-considered)
- [12. Sources](#12-sources)

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
| Continuous deployment | the same, then the deploy to production | the green checks in staging, with no person in between |

**Run continuous delivery by default: staging deploys on every merge, production deploys when the
go or no-go decider of [release.md](../project-management/release.md) section 3 says go.** That
section asks every production release for a named decider, so a pipeline that deploys to
production by itself would skip the decision the release practice requires. Continuous
deployment is a team's choice under release.md section 5; this file does not cover the gates that
would let it replace the named decision, and it marks that as not covered yet.

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
  start is the other way practitioners use (section 11).

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
  practice's ([ruleset-example.md](../git/ruleset-example.md)). The tag is also the version number
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
- **Let one deploy run at a time per environment, and never cancel one halfway.** Use
  `concurrency` with the environment's name and `cancel-in-progress: false`: GitHub says
  concurrency gives an environment "a maximum of one deployment in progress at a time" [14], and a
  cancelled deploy can leave half the service on the new version.
- **While a rollback waits, start no other run for that environment.** By default a group keeps
  one pending run and a newer request cancels it [40], so a new run would cancel the rollback
  before it starts.
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
  apart, give each one an environment of its own and let each role trust only
  `environment:<name>`.
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
  five minutes by default [39], so the deploy job's wait has to cover it (section 6).
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

## 9. Common mistakes

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

## 10. Where the rules stop holding

- **A library or a CLI tool**: nothing is deployed; the artifact is published once to a registry,
  and section 3's build-once rule is the only one that applies.
- **Continuous deployment to production**: not covered yet (section 2).
- **A plan without deployment branch rules for private repositories (GitHub Free)**: environments
  are not available there [11], and neither are rulesets
  ([ruleset-example.md](../git/ruleset-example.md)), so every person with write access
  can deploy to production: a workflow-level check on the ref sits in a file that same person can
  change. Deploy from a public repository, or move to a paid plan; do not use this deploy on such
  a plan.
- **A framework that renders on the server**: the bundle is part of a server image, so it follows
  the image's rules, and section 3's static-hosting advice does not apply.

## 11. Alternatives considered

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
- **Chaining the deploy with `workflow_run`.** Rejected: it starts "regardless of the conclusion"
  of the run it follows unless the job checks it, and it runs with the default branch's privileges
  ([pipeline-security.md](pipeline-security.md) section 5). Calling CI with `workflow_call` and
  `needs` keeps the order in one run.
- **`queue: max` on the deploy's concurrency group.** GitHub's `queue: max` keeps up to 100 runs
  waiting [40]; not set here, because actionlint 1.7.12, which the security jobs run, rejects the
  key [42]; add it when an actionlint release accepts it.

## 12. Sources

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
- [12] GitHub — Available rules for rulesets — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- [13] DORA — Capabilities: Streamlining change approval — https://dora.dev/capabilities/streamlining-change-approval/
- [14] GitHub — Control deployments — https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments
- [15] GitHub — OpenID Connect reference — https://docs.github.com/en/actions/reference/security/oidc
- [16] AWS — IAM User Guide: Create a role for OpenID Connect federation — https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html
- [17] Christophe Tafani-Dereeper — Exploring GitHub-to-AWS keyless authentication flaws (Datadog Security Labs, 2023; research) — https://securitylabs.datadoghq.com/articles/exploring-github-to-aws-keyless-authentication-flaws/
- [18] GitHub — Immutable subject claims for GitHub Actions OIDC tokens (changelog, 2026-04-23) — https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens/
- [19] Seth Larson — Supply-chain attack analysis: Ultralytics (PyPI blog, 2024; case) — https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/
- [20] AWS — Amazon ECS Developer Guide: Pass Secrets Manager secrets through environment variables — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/secrets-envvar-secrets-manager.html
- [21] GitLab — Migration style guide — https://docs.gitlab.com/development/migration_style_guide/
- [22] AWS — amazon-ecs-deploy-task-definition, README, v2.6.4 — https://github.com/aws-actions/amazon-ecs-deploy-task-definition/blob/v2.6.4/README.md
- [23] AWS — Amazon CloudFront Developer Guide: Invalidate files to remove content — https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html
- [24] AWS — Amazon ECS Developer Guide: How the Amazon ECS deployment circuit breaker detects failures — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-circuit-breaker.html
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
- [36] GitHub — Events that trigger workflows: `create` and `push` — https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- [37] GitHub — Managing environments for deployment — https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments
- [38] GitHub — Workflows: triggering a workflow — https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows
- [39] AWS — Amazon ECS Developer Guide: How CloudWatch alarms detect Amazon ECS deployment failures — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-alarm-failure.html
- [40] GitHub — Workflow syntax for GitHub Actions: `concurrency` — https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- [41] GitHub — Viewing deployment history — https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/view-deployment-history
- [42] rhysd — actionlint, `parse.go` (the keys `concurrency` accepts), v1.7.12 — https://github.com/rhysd/actionlint/blob/v1.7.12/parse.go#L817-L825
