# Example: the CI job that builds, tests, scans and pushes the image

A worked example for [images.md](images.md) section 10. It builds the image of
[dockerfile-example.md](dockerfile-example.md) on GitHub Actions and pushes it to GitHub's
container registry, `ghcr.io`. The Python checks run in
[static-checks/setup-example.md](../../python/static-checks/setup-example.md) section 3, and the
test suites in the two CI jobs that step 4 of "How to adopt" in
[python/testing/README.md](../../python/testing/README.md) sets up; this job is about the image.

Each `@...` after an action stands for the full 40-character commit SHA of the release named in
the comment beside it. Renovate cannot read `@...`, so fill each one before the first run and keep
the comment: `git ls-remote https://github.com/<owner>/<repo> 'refs/tags/<release>*'` prints it
(for an annotated tag, take the SHA on the line that ends in `^{}`) [1]. From then on Renovate
(`helpers:pinGitHubActionDigests`, turned on in [dockerfile-example.md](dockerfile-example.md)
section 5) moves the SHA and its comment together [2], [29].

Before the first run, create a Docker Hub access token that can only read, store it as the
repository secret `DOCKERHUB_TOKEN`, and set the repository variable `DOCKERHUB_USERNAME`; without
them the Docker Hub login step fails.

**Navigation**

- [1. The workflow](#1-the-workflow)
- [2. What each part does](#2-what-each-part-does)
- [3. Sources](#3-sources)

## 1. The workflow

`.github/workflows/image.yml`

```yaml
name: image

on:
  pull_request:
  push:
    branches: [main]
    tags: ["v*"]
  # Weekly as well: the scan reads a fresh vulnerability database, so a new finding in an
  # unchanged image fails the job.
  schedule:
    - cron: "0 5 * * 1"

permissions: {}  # nothing by default; the job asks for what it uses

jobs:
  image:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
      packages: write      # push to ghcr.io
    env:
      IMAGE: ghcr.io/${{ github.repository }}
    steps:
      # Every action is pinned to a full commit SHA, its release in the comment (images.md
      # section 10). Docker's own examples use tags such as @v7; this job can push images under
      # our name, so a moved tag here would publish someone else's image.
      - uses: actions/checkout@...  # v7
        with:
          persist-credentials: false  # the token does not stay in .git/config for later steps

      - uses: docker/setup-buildx-action@...  # v4.4.1

      # Pull the base images as a logged-in user: anonymous pulls share a small rate limit.
      # A pull request from a fork has no secrets, so it pulls anonymously.
      - uses: docker/login-action@...  # v4.6.0
        if: ${{ !github.event.pull_request.head.repo.fork }}
        with:
          username: ${{ vars.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@...  # v6.2.0
        with:
          images: ${{ env.IMAGE }}
          tags: |
            type=semver,pattern={{version}}
            type=sha

      # Build and load the image into the runner; the build checks run here and fail it
      # (# check=error=true in the Dockerfile).
      - uses: docker/build-push-action@...  # v7.4.0
        with:
          context: .
          load: true
          tags: acme-api:test
          cache-from: type=gha,scope=acme-api
          cache-to: type=gha,scope=acme-api,mode=max

      - name: Test the image
        run: |
          test "$(docker run --rm acme-api:test id -u)" = 10001
          docker run --rm acme-api:test python -c "import acme.api.main, acme.api.app"
          docker run --rm acme-api:test sh -c 'command -v acme-api'
          # The one path the service writes, read-only everywhere else, as compose.yaml runs it (images.md section 6).
          docker run --rm --read-only --tmpfs /tmp:mode=1770,uid=10001,gid=10001 acme-api:test python -c "import tempfile; tempfile.TemporaryFile().write(b'x')"

      # One scanner, one written policy: fail on critical and high findings that have a fix.
      - uses: aquasecurity/trivy-action@...  # v0.36.0
        with:
          image-ref: acme-api:test
          version: v0.76.0
          severity: CRITICAL,HIGH
          ignore-unfixed: true
          exit-code: "1"

      # Only a push to main or a tag publishes; a pull request or a scheduled run does not.
      - uses: docker/login-action@...  # v4.6.0
        if: github.event_name == 'push'
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # Push from the warm cache, with an SBOM and max-level provenance (images.md section 9).
      - id: push
        uses: docker/build-push-action@...  # v7.4.0
        if: github.event_name == 'push'
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          sbom: true
          provenance: mode=max
          cache-from: type=gha,scope=acme-api

      # The reference a deploy uses, on the run's summary page (images.md section 8).
      - name: Record the digest
        if: github.event_name == 'push'
        run: echo "image=${IMAGE}@${{ steps.push.outputs.digest }}" >> "$GITHUB_STEP_SUMMARY"
```

`.trivyignore`, at the repository root, where Trivy looks for it [3]:

```text
# Fixed upstream, not yet in the base image; drop when the base is republished.
CVE-2026-0000 exp:2026-12-31
```

## 2. What each part does

| Part | Why |
|---|---|
| `schedule:` once a week | scans the current image with a fresh vulnerability database; a scheduled run, like a pull request, pushes nothing |
| `permissions: {}` at the top, then the job's own block | the token gets only what this job uses: read the code, push the package [4] |
| every `uses:` pinned to a SHA with its release in a comment | tags of `tj-actions`, `reviewdog` and `trivy-action` were moved to malicious commits [5], [6], [7]; a SHA cannot be moved. This departs from Docker's own examples, which use major tags, because this job holds the registry write access [8] |
| `persist-credentials: false` | an action or test that runs later finds no token in the git configuration [9] |
| the Docker Hub login, skipped for forks | logged-in pulls have their own limit [10]; a fork's pull request runs without secrets [11] |
| `metadata-action` with `type=semver` and `type=sha` | the tags `1.4.2` and `sha-1a2b3c4`, and the OCI labels `source` and `revision`; `latest` appears only on a release tag, and nobody deploys it [12] |
| the first `build-push-action` with `load: true` | builds and puts the image in the runner, so the test and the scan check the image that will be pushed from the same cache [8] |
| `cache-to: type=gha,scope=acme-api,mode=max` | this image's own cache scope; GitHub keeps a pull request's cache apart from `main`'s, so a pull request cannot write the cache a release build reads [13], [14] |
| `Test the image` | the process runs as the non-root user, the package imports from the venv, the entry point `acme-api` is on `PATH`, and the one path the service writes, `/tmp`, works with the rest of the filesystem read-only, as compose-example.md runs it (images.md section 6) |
| `trivy-action` with `severity`, `ignore-unfixed`, `exit-code: "1"` | the written policy of [images.md](images.md) section 10; `version` pins the Trivy release the action installs [15] |
| `.trivyignore` | one waiver per entry, with its reason and an expiry date; after the `exp:` date the finding fails the job again ([images.md](images.md) section 10) [16] |
| the second `build-push-action` (`id: push`), only on a push | pushes the tags with an SBOM and provenance, and gives the pushed image's digest as its `digest` output (`steps.push.outputs.digest`) [17]. A pull request or a scheduled run builds, tests and scans, and publishes nothing |
| `Record the digest`, only on a push | writes `image=<name>@<digest>` to the run's summary page [18]; that line is the reference a deploy uses ([images.md](images.md) section 8) |

The weekly schedule notifies only the person who last edited its cron line, and GitHub turns it
off after 60 days without activity in a public repository, so name who watches it [11]. The weekly run
scans the image built from `main`; where production runs an older digest, scan that digest too on
the same schedule.

It is good because a pull request runs every check the release runs and publishes nothing; the
job can do only what its permissions name; and no tag that someone else controls decides what
code runs with the right to push the image.

In the repository settings, the `image` job is a required status check for `main`, so a red job
blocks the merge ([static-checks.md](../../python/static-checks/static-checks.md) section 5) [19].

What this example does not claim: it was not run when it was written. The action releases are the
latest in October 2026 [20], [21], [22], [23], [24], [25], [26]. The scanned image and the pushed
image are two builds from one cache, not one artifact: the classic image store on the runner cannot
load an image with attestations, so the push build adds them [27]. A runner with the containerd
image store (`docker/setup-docker-action` with the `containerd-snapshotter` feature on in its
`daemon-config`) can load an image with its attestations, so the job could scan and push one
artifact; this example keeps the default store, which saves a setup step [27], [28]. Trivy is one
choice of scanner ([images.md](images.md) section 10); its `trivy-action` is the one whose tags were
moved in March 2026, which is why the pin is a SHA [7].

## 3. Sources

Checked 2026-10-16 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Git — git-ls-remote, v2.56.0 — https://github.com/git/git/blob/v2.56.0/Documentation/git-ls-remote.adoc
- [2] Renovate — github-actions manager, digest pinning and updating, 44.164.10 — https://github.com/renovatebot/renovate/blob/44.164.10/lib/modules/manager/github-actions/readme.md
- [3] Aqua Security — Trivy CLI reference, `trivy image` (`--ignorefile`), v0.76.0 — https://github.com/aquasecurity/trivy/blob/v0.76.0/docs/guide/references/configuration/cli/trivy_image.md
- [4] GitHub — Publishing and installing a package with GitHub Actions — https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions
- [5] GitHub Advisory Database — GHSA-mrrh-fwg8-r2c3, tj-actions/changed-files (CVE-2025-30066) — https://github.com/advisories/GHSA-mrrh-fwg8-r2c3
- [6] Rami McCarthy — New GitHub Action supply chain attack: reviewdog/action-setup (Wiz blog, 2025; case) — https://www.wiz.io/blog/new-github-action-supply-chain-attack-reviewdog-action-setup
- [7] Aqua Security — GHSA-69fq-xp46-6x23, Trivy supply chain compromise (CVE-2026-33634) — https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23
- [8] Docker — Test before push with GitHub Actions — https://docs.docker.com/build/ci/github-actions/test-before-push/
- [9] GitHub — actions/checkout README, v7.0.1 — https://github.com/actions/checkout/blob/v7.0.1/README.md
- [10] Docker — Docker Hub usage and limits: pulls — https://docs.docker.com/docker-hub/usage/pulls/
- [11] GitHub — Events that trigger workflows — https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- [12] Docker — docker/metadata-action README, v6.2.0 — https://github.com/docker/metadata-action/blob/v6.2.0/README.md
- [13] GitHub — Dependency caching reference, Restrictions for accessing a cache — https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching#restrictions-for-accessing-a-cache
- [14] Docker — GitHub Actions cache backend — https://docs.docker.com/build/cache/backends/gha/
- [15] Aqua Security — trivy-action README, v0.36.0 — https://github.com/aquasecurity/trivy-action/blob/v0.36.0/README.md
- [16] Aqua Security — Trivy documentation, Filtering (`.trivyignore`), v0.76.0 — https://github.com/aquasecurity/trivy/blob/v0.76.0/docs/guide/configuration/filtering.md
- [17] Docker — docker/build-push-action README, v7.4.0 — https://github.com/docker/build-push-action/blob/v7.4.0/README.md
- [18] GitHub — Workflow commands for GitHub Actions, Adding a job summary — https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#adding-a-job-summary
- [19] GitHub — About protected branches, Require status checks before merging — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging
- [20] GitHub — actions/checkout releases — https://github.com/actions/checkout/releases
- [21] Docker — docker/setup-buildx-action releases — https://github.com/docker/setup-buildx-action/releases
- [22] Docker — docker/login-action releases — https://github.com/docker/login-action/releases
- [23] Docker — docker/metadata-action releases — https://github.com/docker/metadata-action/releases
- [24] Docker — docker/build-push-action releases — https://github.com/docker/build-push-action/releases
- [25] Aqua Security — trivy-action releases — https://github.com/aquasecurity/trivy-action/releases
- [26] Aqua Security — Trivy releases — https://github.com/aquasecurity/trivy/releases
- [27] Docker — Build attestations — https://docs.docker.com/build/metadata/attestations/
- [28] Docker — docker/setup-docker-action README, v5.5.0 — https://github.com/docker/setup-docker-action/blob/v5.5.0/README.md
- [29] Renovate — github-actions manager, extract.ts (the replacement template), 44.164.10 — https://github.com/renovatebot/renovate/blob/44.164.10/lib/modules/manager/github-actions/extract.ts
