# Example: the security workflow of a Python and React monorepo

A worked example for [pipeline-security.md](pipeline-security.md) section 7. The `ci.yml` of
[ci-example.md](ci-example.md) calls it, so it checks the monorepo on every pull request, in the
merge queue, on `main` before a deploy and once a week, and the `deploy.yml` of
[deploy-example.md](deploy-example.md) calls it again on a version tag. It checks the workflow
files, the dependencies of both lockfiles, the code, and the commits of a pull request for
secrets. The image scan stays in the image job of [ci-example.md](ci-example.md), as
[images.md](../docker/images.md) section 10 asks; the deploy workflow scans the pushed digest
again ([deploy-example.md](deploy-example.md) section 2) and runs ZAP's baseline scan against
staging. The infrastructure scan of [pipeline-security.md](pipeline-security.md) section 7 is not
shown, because this example holds no infrastructure folder.

Actions are pinned as in [ci-example.md](ci-example.md). The three tools that have no official
action are downloaded from their own releases and checked against the SHA-256 checksum the
release publishes, read on 2026-10-18 from each release's checksums file [11], [12], [13]; when you
move one to a newer release, copy its checksum from that release's checksums file. Renovate moves
the action pins, and nothing moves these three downloads, the gitleaks hook's `rev:` (section 3)
or zizmor's `version:` input: the pipeline owners of `CODEOWNERS` (section 3) move them by hand,
when a tool's release notes name a security fix and at each quarterly review. Before the first
run, create `osv-scanner.toml` at the root (section 3): the `dependencies` job fails when the file
is missing, and a file with no `[[IgnoredVulns]]` entry is valid [15].

**Navigation**

- [1. The workflow](#1-the-workflow)
- [2. What each part does](#2-what-each-part-does)
- [3. The files next to it](#3-the-files-next-to-it)
- [4. Sources](#4-sources)

## 1. The workflow

`.github/workflows/security.yml`

```yaml
name: security

on:
  # Only as a call: ci.yml's gate and deploy.yml's production job need these jobs (pipeline-security.md section 7).
  workflow_call:

permissions: {}  # read-only jobs and no secrets; only CodeQL writes, to upload its results

jobs:
  workflows:
    runs-on: ubuntu-24.04  # a version label, never ubuntu-latest: the OS changes only when this line does (pipeline.md section 9)
    timeout-minutes: 10  # a hung job stops here, not at GitHub's 360 minutes (pipeline.md section 8)
    permissions:
      contents: read
      actions: read  # zizmor-action's README asks for it on a private repository
    steps:
      # Every action by full commit SHA, the release in the comment: a tag can be moved (pipeline-security.md section 4).
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false  # the token is not left on the runner for the steps after this one (pipeline-security.md section 3)
      - name: actionlint
        run: |
          curl -sSfL -o actionlint.tar.gz \
            https://github.com/rhysd/actionlint/releases/download/v1.7.12/actionlint_1.7.12_linux_amd64.tar.gz
          echo "8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8  actionlint.tar.gz" | sha256sum --check
          tar -xzf actionlint.tar.gz actionlint
          ./actionlint -color
      - uses: zizmorcore/zizmor-action@85b2b9fb8e3325e7a23d7d0a9d7ba5ae0f999e3e  # v0.7.1
        with:
          # Print the findings and fail the job; uploading them needs GitHub Advanced Security on a private repository.
          advanced-security: false
          version: 1.31.1  # the zizmor release the action installs

  dependencies:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false
      - name: osv-scanner over both lockfiles
        run: |
          curl -sSfL -o osv-scanner \
            https://github.com/google/osv-scanner/releases/download/v2.7.0/osv-scanner_linux_amd64
          echo "160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b  osv-scanner" | sha256sum --check
          chmod +x osv-scanner
          # Exit code 1 means vulnerabilities were found; waivers live in osv-scanner.toml, each with a reason and an end date.
          ./osv-scanner scan source --config=osv-scanner.toml \
            --lockfile=backend/uv.lock --lockfile=frontend/pnpm-lock.yaml

  secrets:
    # The net under the pre-commit hook: every commit of the pull request, not only its last state.
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          fetch-depth: 0  # the pull request's commits, for the log range below
          persist-credentials: false
      - name: gitleaks over the pull request's commits
        env:
          BASE: ${{ github.event.pull_request.base.sha }}
          HEAD: ${{ github.event.pull_request.head.sha }}
        run: |
          curl -sSfL -o gitleaks.tar.gz \
            https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz
          echo "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb  gitleaks.tar.gz" | sha256sum --check
          tar -xzf gitleaks.tar.gz gitleaks
          # --redact keeps a found secret out of the log; --ignore-gitleaks-allow stops a comment in the pull request from hiding one.
          # On a finding, the log says what to do first (pipeline-security.md section 6).
          ./gitleaks git --log-opts="$BASE..$HEAD" --redact --ignore-gitleaks-allow --verbose . || {
            echo "::error::A secret was found. Revoke it at its provider first; deleting the line does not remove it."
            exit 1
          }

  code:
    # Drop this job on a private repository without GitHub Code Security: the upload needs it.
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    permissions:
      contents: read
      security-events: write  # uploads the results to code scanning
      actions: read  # GitHub's CodeQL starter workflow marks it as needed on a private repository
    strategy:
      fail-fast: false
      matrix:
        language: [python, javascript-typescript, actions]
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false
      - uses: github/codeql-action/init@6f2ac81f5cd81fe351a197ba0b00d91d03cd2aee  # v4.39.0
        with:
          languages: ${{ matrix.language }}
          build-mode: none  # interpreted languages need no build
      - uses: github/codeql-action/analyze@6f2ac81f5cd81fe351a197ba0b00d91d03cd2aee  # v4.39.0
        with:
          category: /language:${{ matrix.language }}
```

## 2. What each part does

| Part | Why |
|---|---|
| `workflow_call` only | `ci.yml` calls it, so its `ci-ok` gate needs these jobs: a pull request is checked before it merges, `main` before a deploy, and the weekly run catches an advisory published between changes; `deploy.yml` calls it again on a version tag ([pipeline-security.md](pipeline-security.md) section 7). There is one required check, `ci-ok`, not a second gate here. Inside a called workflow `github` is the caller's context [9], so `github.event_name` and the pull request's SHAs work as before. The weekly schedule is `ci.yml`'s; it runs on the default branch only and can start late ([pipeline.md](pipeline.md) section 4) |
| `permissions: {}`, then read-only jobs | a scanner is third-party code; it gets no write access and no secret, and `code` gets only the one write it needs ([pipeline-security.md](pipeline-security.md) section 7) |
| actionlint, downloaded and checked | syntax, expressions and the shell in `run:` [1]; the release's checksum stops a changed download |
| zizmor through `zizmorcore/zizmor-action` | the security audits of the workflows; with `advanced-security: false` it prints the findings and fails the job [2] |
| osv-scanner with two `--lockfile` | one scanner for `backend/uv.lock` and `frontend/pnpm-lock.yaml`; it exits with `1` when it finds vulnerabilities [3] |
| `--config=osv-scanner.toml` | one waiver file for the whole repository instead of one per lockfile's folder [4]; section 3 shows it. Create it before the first run: the job fails when the file is missing, and a file with no `[[IgnoredVulns]]` entry is valid [15] |
| gitleaks over `BASE..HEAD` | scans every commit of the pull request, so a secret added and removed again is still found [5]; the pre-commit hook scans only staged changes, so in CI it finds nothing to scan. On `main`, in the queue and on the weekly run the job is skipped, and a skipped job passes the gate |
| `--redact`, `--ignore-gitleaks-allow` | a found secret stays out of the log; a `gitleaks:allow` comment in the pull request under scan cannot switch the scan off [5] |
| the `::error::` line when gitleaks fails | the person who opens the red job reads the first step in the log, as an error message [14]: revoke the secret at its provider, because deleting the line leaves it in the history ([pipeline-security.md](pipeline-security.md) section 6). A rotated secret's finding is cleared by its fingerprint in `.gitleaksignore` [5] |
| `fetch-depth: 0` | the checkout keeps the history the log range needs |
| `BASE`, `HEAD` through `env:` | the SHAs reach the script as data ([pipeline-security.md](pipeline-security.md) section 5) |
| CodeQL for `python`, `javascript-typescript`, `actions`, with `actions: read` | GitHub's analyser for the backend, the frontend and the workflows; `none` as the build mode for languages that need no build [6]. GitHub's CodeQL starter workflow marks `actions: read` and `contents: read` as required for workflows in private repositories [10]. How an alert blocks a merge: [pipeline-security.md](pipeline-security.md) section 7 |

It is good because the workflows, both lockfiles, the code and every new commit are checked with
tools that each read their own kind of input; every downloaded tool is checked against its
release's checksum; and no scanner holds a credential it could leak.

What this example does not claim: it was not run when it was written. The actions are pinned to
the commit `git ls-remote` printed on 2026-10-18, and each tool's checksum is the one its
release's checksums file gives [11], [12], [13]. gitleaks takes security patches only and its maintainer works on Betterleaks
([pipeline-security.md](pipeline-security.md) section 7): check the choice before you copy it.

## 3. The files next to it

`osv-scanner.toml`, at the root:

```toml
# One waiver per finding: why it does not apply, and the day it fails the job again.
# The entry below is an example: delete it. Keep the file even with no entry, because the
# dependencies job reads it and fails when it is missing.
[[IgnoredVulns]]
id = "GHSA-0000-0000-0000"
ignoreUntil = 2026-12-31
reason = "The vulnerable function is in the CLI part of the package, which the API never imports."
```

`.github/CODEOWNERS`:

```text
# The pipeline holds the keys to production: its owners review every change to it (pipeline-security.md section 8).
/.github/ @acme-corp/platform
/backend/deploy/ @acme-corp/platform
# The infrastructure code of delivery.md section 9, where the repository holds it: a changed module
# source or lock file chooses the code the next plan runs (pipeline-security.md section 5).
/infra/ @acme-corp/platform
# The files that tell a scanner what to skip: a pull request could otherwise switch off its own scan.
# No leading /, so each matches at any depth: a scanner also reads them from the folder it runs in.
osv-scanner.toml @acme-corp/platform
.trivyignore @acme-corp/platform
.trivyignore.yaml @acme-corp/platform
trivy.yaml @acme-corp/platform
.gitleaks.toml @acme-corp/platform
.gitleaksignore @acme-corp/platform
zizmor.yml @acme-corp/platform
.zap-rules.tsv @acme-corp/platform
```

The pre-commit hook that stops a secret before it leaves a developer's machine, added to the
root hook file of [ci-example.md](ci-example.md) section 3:

```yaml
  - repo: https://github.com/gitleaks/gitleaks
    # A departure from static-checks.md section 3, one pin per tool: this hook scans the staged
    # changes at each commit, while CI scans the pull request's commits and the built bundle, two
    # scans of one tool. The cost: this rev: and the release in the CI downloads are two pins that
    # move together, by hand or with a Renovate regex manager.
    rev: v8.30.1
    hooks:
      - id: gitleaks  # scans the staged changes at every commit
```

| Part | Why |
|---|---|
| `ignoreUntil`, `reason` | a waiver with a reason and an end date, reviewed like code; after the date the finding fails the job again ([images.md](../docker/images.md) section 10 asks the same of the image scanner) [4] |
| `/.github/`, `/backend/deploy/` and the scanners' config and ignore files in `CODEOWNERS` | a change to a workflow, to a deploy file or to a file that tells a scanner what to skip asks for the pipeline owners' review [7]; where two or more people review, the ruleset's code-owner review makes that review required ([pipeline-security.md](pipeline-security.md) section 8) |
| `/infra/` | the infrastructure folder and the lock file inside it: a plan on a pull request runs the modules and providers they name, with the plan role's credentials ([pipeline-security.md](pipeline-security.md) section 5). Keep the line only where the repository holds its infrastructure code, as [delivery.md](delivery.md) section 9 lays it out |
| `.zap-rules.tsv` | the rules file of ZAP's baseline scan, which sets each rule to `IGNORE`, `WARN` or `FAIL` ([pipeline-security.md](pipeline-security.md) section 7), so a pull request could mark a finding `IGNORE`; the `dast-staging` job of [deploy-example.md](deploy-example.md) reads it from the root after the staging deploy |
| the scanners' files with no leading `/` | `CODEOWNERS` follows most gitignore rules, so a pattern with a leading `/` matches at the root only, and one without it matches at any depth [16]. gitleaks also reads `.gitleaksignore` from the folder it runs in and from the folder it scans, and `.gitleaks.toml` from the folder it scans [17]; Trivy reads `trivy.yaml` from the folder it runs in [18]. The bundle scan of [ci-example.md](ci-example.md) runs in `frontend/` and scans `dist/`, so a root-only pattern would miss a file there |
| the `gitleaks` hook | the first of the three nets of [pipeline-security.md](pipeline-security.md) section 6. Its `rev:` is a second pin of gitleaks next to the CI downloads, a departure from [static-checks.md](../../python/static-checks/static-checks.md) section 3 that the comment at the line declares |

It is good because each file closes one gap: the waiver file keeps every skipped finding visible
with its reason and its end date; `CODEOWNERS` puts the pipeline owners on every change that could
weaken the pipeline, the scanners' own ignore files and the infrastructure code a plan runs
included; and the hook stops a secret before it reaches a commit, with its second pin named where
a reader copies it.

## 4. Sources

Checked 2026-10-18 unless a line ends with — checked <YYYY-MM-DD>.

- [1] rhysd — actionlint, README, v1.7.12 — https://github.com/rhysd/actionlint/blob/v1.7.12/README.md
- [2] zizmor — zizmor-action, README, v0.7.1 — https://github.com/zizmorcore/zizmor-action/blob/v0.7.1/README.md
- [3] Google — OSV-Scanner: output and return codes — https://google.github.io/osv-scanner/output/
- [4] Google — OSV-Scanner: configuration — https://google.github.io/osv-scanner/configuration/
- [5] Zachary Rice — gitleaks, README, v8.30.1 — https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md
- [6] GitHub — github/codeql-action, README, v4.39.0 — https://github.com/github/codeql-action/blob/v4.39.0/README.md
- [7] GitHub — Secure use reference: Using CODEOWNERS to monitor changes — https://docs.github.com/en/actions/reference/security/secure-use
- [9] GitHub — Reusing workflow configurations: `github` context — https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations#github-context
- [10] GitHub — starter-workflows, `code-scanning/codeql.yml` — https://github.com/actions/starter-workflows/blob/main/code-scanning/codeql.yml
- [11] rhysd — actionlint, checksums file of release v1.7.12 — https://github.com/rhysd/actionlint/releases/download/v1.7.12/actionlint_1.7.12_checksums.txt
- [12] Google — OSV-Scanner, checksums file of release v2.7.0 — https://github.com/google/osv-scanner/releases/download/v2.7.0/osv-scanner_SHA256SUMS
- [13] Zachary Rice — gitleaks, checksums file of release v8.30.1 — https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_checksums.txt
- [14] GitHub — Workflow commands for GitHub Actions: Setting an error message — https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#setting-an-error-message
- [15] Google — osv-scanner, `pkg/osvscanner/osvscanner.go` (a `--config` file is read at start, and an error stops the scan), v2.7.0 — https://github.com/google/osv-scanner/blob/v2.7.0/pkg/osvscanner/osvscanner.go#L139-L145
- [16] GitHub — About code owners: CODEOWNERS syntax — https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- [17] Zachary Rice — gitleaks, `cmd/root.go` (where the config and `.gitleaksignore` are read), v8.30.1 — https://github.com/gitleaks/gitleaks/blob/v8.30.1/cmd/root.go
- [18] Aqua Security — Trivy CLI reference, `trivy image` (`--config`, default `trivy.yaml`), v0.76.0 — https://github.com/aquasecurity/trivy/blob/v0.76.0/docs/guide/references/configuration/cli/trivy_image.md
