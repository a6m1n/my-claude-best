# CI/CD practices

How a team checks every change and ships it: what a CI job is and what goes into it, which event
starts which work, the stages and when they run, the one required check that guards `main`, how
an artifact is built once and promoted to production, how a deploy reaches the cloud without a
stored key, and how the pipeline itself is kept safe, secrets included. The rules hold for any
language and any CI system; the examples are GitHub Actions workflows for a monorepo with a
Python API (uv) and a React application (Vite, pnpm), deployed to AWS.

**When you do not need all of it.** Martin Fowler holds that integrating everyone's work into the
mainline "isn't plausible" in "a classical open-source project, where there is one or two
maintainers and many contributors", and that "Instituting Continuous Integration without
self-testing code won't work" [1]: write the tests before the pipeline. At 37signals, where the
checks of one application ran in less than half the time on a developer's machine, the company
moved CI to developer machines, because "Installing, operating, and caring for a remote CI setup
is a substantial complication" [2]; its `gh-signoff` tool posts a commit status that a ruleset can
require [3]. That is one company's case, with a fast local test suite and a small team that trusts
each other. Even there, keep the deploy in the pipeline, with OIDC and no cloud key on a laptop
([delivery.md](delivery.md) section 5); that is this practice's view.
[pipeline.md](pipeline.md) section 12 says when parts of CI are too much.

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)
- [Sources](#sources)

A plain arrow reads "then"; the dashed arrow is a person's decision.

```mermaid
flowchart LR
  PR["pull request<br/>ci.yml: checks, tests, build, scans<br/>ci-ok required"] --> M["merge to main"]
  M --> B["deploy.yml: CI again,<br/>image and bundle published once"]
  B --> S["staging<br/>migrate, deploy, smoke test"]
  S -.-> T["version tag v1.4.2<br/>by the go or no-go decider"]
  T --> P["production<br/>the same artifacts"]
```

It is good because each box is the subject of one rules file and one example, and the only
dashed arrow is the decision that [release.md](../project-management/release.md) section 3 gives
to one named person.

## What is here

- [pipeline.md](pipeline.md) — the CI rules: workflow, job, step and runner; CI and CD and how they
  differ; what a job holds and
  what it does not; the triggers and when to use each, automatic or manual; the stages and when
  they run, the checks other practices ask for among them; the gate job as the one required check;
  a monorepo that runs only what a change touches; speed and what CI costs, reproducible runs, a
  red build, a flaky test and who is told; and when parts of it are too much, a one-person
  repository included. Read it before you write or change a CI workflow or the required checks of
  `main`.
- [delivery.md](delivery.md) — the CD rules: continuous delivery as the default pipeline, and
  continuous deployment as a job that creates the version tag after staging, building once and
  promoting the same artifact, environments and the production gate, OIDC instead of stored keys,
  what a deploy job holds, migrations, version skew between the bundle and the API, smoke tests,
  the way back, blue/green, linear and canary deploys on ECS, and the deploy targets to choose
  from; then the infrastructure a deploy needs, measuring delivery, and preview environments per
  pull request. Read it before you write or change a deploy workflow, a cloud role it uses, or the
  infrastructure code a deploy needs.
- [pipeline-security.md](pipeline-security.md) — token permissions, actions pinned by commit,
  untrusted input from pull requests, why a secret never goes into a repository (private ones
  included) and where each secret lives, the security jobs and where they gate a merge and a
  deploy, review of workflow files, personal data in logs, artifacts and test data, an AI agent as
  a job, third-party apps and tokens, and audit logs and visibility. Read it before you add a
  trigger, a permission, an action, a secret or an agent to a workflow.
- [ci-example.md](ci-example.md) — `ci.yml` for the monorepo: change detection, the static-checks
  job, backend and frontend jobs with the migration check and the bundle budget, the image job,
  the call of the security jobs and the `ci-ok` gate, plus the root hook file. Read it when you
  write or change a CI workflow.
- [deploy-example.md](deploy-example.md) — `deploy.yml` and the reusable `deploy-to.yml`: CI on
  `main`, the image and the bundle published once, staging on every merge, production on a version
  tag, the migration, the smoke test, the passive scan and the header scans after the staging
  deploy, the notice to the team when a run fails, the GitHub environments, and the AWS trust
  policy and task definition. Read it when you write or change a deploy workflow.
- [security-example.md](security-example.md) — `security.yml`, the security jobs that `ci.yml`
  and `deploy.yml` call: workflow linters, a dependency scan of both lockfiles, a secret scan of a
  pull request's commits and CodeQL, plus `CODEOWNERS`, the waiver file and the secret-scanning
  hook. Read it when you set up the security checks.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/any-language/ci-cd/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you write or change a workflow under
   `.github/workflows/`, a required status check, a deploy job, a cloud role a pipeline uses, or a
   secret a pipeline reads, read `docs/engineering/any-language/ci-cd/README.md` and the file it
   routes to for that work." Without it an agent never opens the folder. An agent that writes a
   workflow checks, before it pins an action, that the action exists and belongs to its vendor,
   and reads the SHA itself ([pipeline-security.md](pipeline-security.md) section 4).
3. The rules and examples link the practices that own a neighbouring rule:
   [release.md](../project-management/release.md) and
   [rollback-plan.md](../project-management/rollback-plan.md) (the release decision, the
   environments, the way back), [images.md](../docker/images.md) (the image job, tags, provenance),
   [static-checks.md](../../python/static-checks/static-checks.md) section 5 (the static-checks job),
   [python/testing](../../python/testing/README.md) (the test suites),
   [security.md](../../react/security/security.md) sections 9, 10 and 14 (the frontend's public
   values, its installs, the header scans and the registry signatures),
   [performance.md](../../react/performance/performance.md) (the bundle budget the build checks),
   [accessibility.md](../../react/design/accessibility.md) (the automated checks in the
   end-to-end tests), [evals.md](../../python/evals/evals.md) section 8 (the eval run before a
   model change merges, and the key it uses),
   [libraries.md](../../react/architecture/libraries.md) (the frontend's tools),
   [python.md](../../python/language/python.md) section 5 (how the application reads settings),
   [file-structure.md](../file-structure/file-structure.md) section 9 (`.env.example` and the files
   at the root), and [git.md](../git/git.md) with [ruleset-example.md](../git/ruleset-example.md)
   (pull requests, leaked secrets, the required check, release tags). Copy those practices too, or
   point each link at the rule your project follows instead.
4. Check what your GitHub plan offers before you copy a setting. The plan limits are stated where
   each setting is explained: [delivery.md](delivery.md) sections 4 and 13 (environments, required
   reviewers), [pipeline.md](pipeline.md) section 6 (merge queue) and section 8 (the Actions minutes
   and the storage a plan includes, and what more costs), and
   [pipeline-security.md](pipeline-security.md) sections 6 and 7 (push protection, secret
   scanning, CodeQL) and section 12 (the audit log). On a plan without environments, do not use
   this deploy.
5. In a repository that already has workflows, apply the rules to new and changed workflows first,
   as [refactoring.md](../refactoring/refactoring.md) section 2 describes. Set a date by which old
   workflows follow three rules: every action pinned by commit, a `permissions:` block on every
   workflow, and no `pull_request_target` workflow that runs a pull request's code. They fix
   security holes, so they do not wait for a change to touch the file
   ([refactoring.md](../refactoring/refactoring.md) section 6).
6. Re-check the lines that name a moving target. Each file's Sources section opens with its
   `Checked <date>` line; the action releases and tool checksums in the examples are dated
   2026-10-18, and so are the plan limits and the preview status of GitHub's workflow lockfiles
   ([pipeline-security.md](pipeline-security.md) section 4). The ZAP image digest, the CSP
   Evaluator checksum and the Terraform release in [deploy-example.md](deploy-example.md) and
   [delivery.md](delivery.md) section 9 are dated 2026-10-19.

## The points to adapt

The shape stays: one required gate, every input pinned, the artifact built once, short-lived
credentials, production behind a person's decision (for each release, or once for the pipeline
under continuous deployment), no secret in a repository. Within that shape,
these are your choices; each rules file names the options and their costs.

- Whether pull requests run part of the monorepo or all of it ([pipeline.md](pipeline.md) section 7).
- The deploy target and whether to use GitOps ([delivery.md](delivery.md) section 8).
- The form of the production gate your plan allows: a protected tag, a required reviewer, or both
  (under continuous deployment, the tag only) ([delivery.md](delivery.md) section 4).
- Whether every change goes to production by itself (continuous deployment) or waits for the go or
  no-go decider's tag ([delivery.md](delivery.md) section 2,
  [release.md](../project-management/release.md) section 3).
- Whether the frontend bundle can be built once, or must be built per environment
  ([delivery.md](delivery.md) section 3).
- The scanners and the written policy of what fails ([pipeline-security.md](pipeline-security.md)
  section 7).
- The CI system itself: the rules hold on GitLab CI, Jenkins, CircleCI or Buildkite, and the
  examples need rewriting ([pipeline.md](pipeline.md) section 13).
- The tool for the infrastructure a deploy needs, or none for a small setup
  ([delivery.md](delivery.md) sections 9 and 14).
- Whether pull requests get preview environments ([delivery.md](delivery.md) section 11).
- How a release reaches users on ECS: the rolling update, or blue/green, linear or canary
  ([delivery.md](delivery.md) section 7, [release.md](../project-management/release.md) section 6).

## Sources

Checked 2026-10-19 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Martin Fowler — Continuous Integration (martinfowler.com, 2024; opinion) — https://martinfowler.com/articles/continuousIntegration.html
- [2] David Heinemeier Hansson — We're moving continuous integration back to developer machines (world.hey.com, 2024; case) — https://world.hey.com/dhh/we-re-moving-continuous-integration-back-to-developer-machines-3ac6c611
- [3] Basecamp — gh-signoff, README — https://github.com/basecamp/gh-signoff
