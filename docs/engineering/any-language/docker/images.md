# Image rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. The build context: an allow-list](#2-the-build-context-an-allow-list)
- [3. Stages and layer order](#3-stages-and-layer-order)
- [4. The base image and its pins](#4-the-base-image-and-its-pins)
- [5. Secrets at build time](#5-secrets-at-build-time)
- [6. The process at run time](#6-the-process-at-run-time)
- [7. Lint the Dockerfile](#7-lint-the-dockerfile)
- [8. Tags, labels and the registry](#8-tags-labels-and-the-registry)
- [9. SBOM, provenance and signatures](#9-sbom-provenance-and-signatures)
- [10. The CI job that pushes the image](#10-the-ci-job-that-pushes-the-image)
- [11. The Python case](#11-the-python-case)
- [12. Where it stops holding](#12-where-it-stops-holding)
- [13. Sources](#13-sources)

## 1. Purpose and the one rule

This file is for everyone who writes or changes a `Dockerfile`, a `.dockerignore`, or the CI job
that builds and pushes an image: people and AI agents alike. It covers one application's image
from the build context to the registry. Running the image locally with Compose is
[compose.md](compose.md); running a coding agent in a container is
[agent-containers.md](agent-containers.md).

The one rule: **an image is built in CI from pinned inputs, holds no secret, and runs one
non-root process that stops cleanly.**

Why it matters:

- An image outlives the commit that built it. A secret copied into a layer stays in every copy of
  that image, in every registry and cache it reached.
- An unpinned input changes without a commit. A tag such as `python:3.13-slim` pointed to a new
  Debian release overnight and broke builds that nobody had touched (section 4).
- A process that ignores SIGTERM is killed after ten seconds, in the middle of its requests.

Docker's own documentation calls every Dockerfile practice "should" or "recommended", never
"must". This file decides which of them are rules here, and says why.

## 2. The build context: an allow-list

The build context is every file the builder receives. A `COPY . .` puts all of it into a layer.

- **Write `.dockerignore` as an allow-list: `*` on the first line, then one `!` line for each
  path the build reads.** A deny-list fails open: it misses what nobody thought of, such as a
  nested `.env`, a key file, or the `.claude/` folder a coding agent writes. In November 2025,
  10,456 images uploaded to Docker Hub leaked secrets, and files swept in by whole-directory
  copies were one of the most frequent causes. An allow-list fails closed: a new file stays out
  until someone lists it. Docker's documentation explains the syntax but does not say what to
  exclude, so the choice is yours to make on purpose.
- **Keep each `!` line a literal path at the top of the context** (`!src`, `!pyproject.toml`),
  never a glob such as `!bin/*/tool`. BuildKit and the classic builder both walk an excluded
  folder only along the literal paths that `!` lines name. A glob inside an exception works on
  BuildKit, but not on the classic builder, and the Docker CLI still falls back to the classic
  builder when the buildx plugin is missing.
- **After the `!` lines, exclude again what may sit inside the folders you let in:** `**/.env`,
  `**/__pycache__`, local test output. The last line that matches a path decides, so these lines
  win over `!src` for the files they name. That `.env` never reaches an image is a rule of
  [python.md](../../python/language/python.md) section 5; this is how an allow-list keeps it.
  Inside a folder you let in, these lines are a deny-list, so run the check below also when files
  are added under such a folder.
- **List every file the build backend reads, too**, such as a `README.md` that `pyproject.toml`
  names as its `readme`. The `pyproject.toml` specification makes `readme` "a path relative to
  `pyproject.toml` to a text file", and Docker removes an excluded file from the context before
  the builder receives it, so a missing file fails the build. That is the allow-list working, but
  plan for it.
- **When one build context serves several Dockerfiles, give each the list it needs:** its own
  `<name>.Dockerfile.dockerignore` beside it, or one `.dockerignore` at the context root that lists
  what any of them reads. A file named after the Dockerfile with `.dockerignore` added
  (`proxy.Dockerfile.dockerignore`) sits beside it and wins over the context's `.dockerignore`; or
  one `.dockerignore` at the context root lists what any of them reads.

Check: after you change `.dockerignore`, list what the builder receives. The `CopyIgnoredFile`
build check (section 7) goes silent once the file holds any `!` line (BuildKit issue #7125, open
in October 2026), so the build will not warn you:

```sh
# A throwaway build: it only lists the context and is never pushed, so it has no frontend line.
printf 'FROM busybox:1.37@sha256:...\nCOPY . /ctx\nRUN find /ctx -type f\n' |
  docker build --no-cache --progress=plain -f - .
```

The output lists every file in the context; nothing outside your `!` lines may appear. Fill the
digest from `docker buildx imagetools inspect busybox:1.37`, as for every `sha256:...` in this
practice.

## 3. Stages and layer order

- **Use a builder stage and a runtime stage, and copy into the runtime stage only what runs.**
  Compilers, package managers and their caches stay in the builder, so the shipped image is
  smaller and has fewer packages to patch. BuildKit builds only the stages the target needs.
- **Name each stage (`FROM … AS builder`) and copy from it by name.** A `COPY --from=0` breaks the
  day someone reorders the stages; a name does not.
- **Order the steps from the least to the most often changed: the dependency manifest and lock
  file, the install, then the source.** A changed layer rebuilds every layer after it. With this
  order, an edit to the source reuses the installed dependencies.
- **Give the package manager a cache mount (`RUN --mount=type=cache,target=…`), and expect it to
  help local builds only.** A cache mount lives in the builder's own storage. It is not part of
  the cache that `--cache-to` exports, so a fresh CI runner starts with it empty (BuildKit
  documentation, October 2026). In CI the exported layer cache does that work (section 10).
- **Read build-only files through a bind mount (`RUN --mount=type=bind,source=…`) when one `RUN`
  needs them**, as the dependency step does with the lock file. Nothing from a bind mount lands in
  a layer.
- **Run `apt-get update` and `apt-get install` in one `RUN`.** An `update` cached in a layer of
  its own leaves a later install with old package lists.
- **Set `pipefail` before a pipe.** `/bin/sh -c` checks only the last exit code of a pipe, so
  start such a `RUN` with `set -o pipefail &&`; Debian's `dash` may not support the option, so
  there run that step through `bash` in the exec form of `RUN`.
- **Give `WORKDIR` an absolute path.** An absolute `WORKDIR`, instead of `RUN cd`, does not depend
  on where the steps before it left off.
- **Copy local files with `COPY`, not `ADD`.** `ADD` also unpacks archives and fetches URLs, so a
  `COPY` does only what the line shows.

## 4. The base image and its pins

The base image is a choice each team makes. No source shows one option failing for everyone, and
Docker's own pages point to different ones. The options for a Python service, with what each
costs, as of October 2026:

| Option | What you get | What it costs |
|---|---|---|
| Docker Official Image, `python:<version>-slim-<debian release>` | the image most guides use; republished at least monthly | a full Debian userland, so scanners report many CVEs; the count varies several-fold with the scanner |
| Docker Hardened Images, `dhi.io/python` | a minimal image, free under Apache 2.0, with SBOM and provenance | a login to `dhi.io`; mirroring to your own registry is paid; its low CVE count relies on VEX statements that only Docker Scout applies without setup |
| Chainguard, `cgr.dev/chainguard/python` | a minimal image | the free tier serves `:latest` only, which moves across minor Python versions; a digest pin on the free tier receives no fixes |
| Google distroless, `python3-debian13` | no shell, a minimal runtime | Python is Debian's package, fixed at 3.13; four tags only; the builder stage must match its path and ABI |
| Alpine, `python:<version>-alpine` | a small image | musl instead of glibc: wheels exist for most packages but not all, so some installs compile from source |

Whatever the choice:

- **Name the distribution release in the tag: `python:3.13-slim-trixie`, not `python:3.13-slim`.**
  A tag without it moves to the next Debian release when one ships. That move from bookworm to
  trixie broke builds in August 2025, and the image's own page asks you to name the release.
- **Pin every image the build pulls by its digest: each `FROM`, each `COPY --from=<image>`, and
  the `# syntax=` frontend (section 7).** A tag can be moved to a different image at any time. A
  digest is the hash of the content: it cannot change, you can audit it, and you can roll back to
  it. Given a tag and a digest together, Kubernetes pulls by the digest alone.
- **Pin the multi-platform index digest, not the digest of one platform's manifest.** One team
  pinned the amd64 manifest and shipped an x86-64 userland inside their arm64 image. The
  `Digest:` line at the top of `docker buildx imagetools inspect <image>:<tag>` is the index
  digest.
- **Keep the pins moving with a bot that reads every `FROM` and every `COPY --from` line.** A pin
  that nobody updates "opts you out of automated security fixes" (Docker's words). Renovate
  updates every `FROM` line, `COPY --from` images, `ARG` defaults and the `# syntax=` image.
  Dependabot updates only the first `FROM` of a Dockerfile and does not support multi-stage
  builds, so it misses most of a Dockerfile written by section 3. Renovate pins no digest by
  default: turn on its `docker:pinDigests` and `helpers:pinGitHubActionDigests` presets
  ([dockerfile-example.md](dockerfile-example.md) section 5).
- **Rebuild on a schedule, not only when the code changes.** An image rebuilt from cache keeps
  the old packages; only a rebuild that pulls the base image again (`--pull`) and runs the install
  again picks up the fixes. With digest pins, the bot's pull request is that rebuild.

## 5. Secrets at build time

- **Pass a credential the build needs only through `RUN --mount=type=secret` or
  `RUN --mount=type=ssh`, never through `ARG` or `ENV`.** Build arguments and environment values
  persist in the image history and, with max-level provenance (section 9), in the attestation
  next to the image. A secret mount is present only for the one `RUN` that names it and never
  appears in provenance. The `SecretsUsedInArgOrEnv` build check catches the common names, not all
  of them.
- **Check that the tool you run does not write the credential into a file the image keeps.** A
  secret mount protects the way the value arrives, not what the tool does with it: uv once wrote
  package-index credentials into `uv.lock` and `pyproject.toml`. Read the files a step writes
  before you trust it with a credential.
- **Never let one builder, or one build cache, serve builds of different trust levels.** In
  BuildKit up to 0.33.0, a malicious image could poison a shared cache and read the secrets
  mounted into another build (CVE-2026-93318). In CI, give cache write access only to workflows
  that run your own code (section 10).

## 6. The process at run time

- **Run the process as a non-root user with a fixed UID and GID set in the image (`USER
  10001:10001`).** Without user namespaces, a root process that escapes the container is root on
  the host; NIST SP 800-190, OWASP and CIS all ask for a non-privileged user. A fixed number keeps file ownership
  the same in every build, while a user created without one may get a different ID next time.
  Section 12 names where a fixed UID stops holding.
- **Leave the application's files owned by root, readable but not writable by that user.** The
  process cannot rewrite its own code, so an attacker who controls it cannot change what the next
  request runs, and the image stays what CI built. Sysdig's Dockerfile best practices ask the
  same: "Make executables owned by root and not writable".
- **Start the process with an exec-form `CMD`: `CMD ["acme-api"]`, never `CMD acme-api`.** In
  shell form, `/bin/sh` is PID 1 and the application, as its child, never receives SIGTERM.
- **Make sure PID 1 handles SIGTERM, or run an init.** Linux delivers to PID 1 only the signals
  it has installed a handler for. CPython installs none for SIGTERM; uvicorn and gunicorn do.
  Without a handler, `docker stop` waits ten seconds and then kills the process. Run an init
  (`docker run --init`, or `init: true` in Compose, which runs tini) when PID 1 starts child
  processes it does not wait for, such as a shell script or a coding agent
  ([agent-containers.md](agent-containers.md) section 6).
- **Put the health check where the runtime that acts on it reads it.** Kubernetes ignores the
  image's `HEALTHCHECK` and uses its own probes. Plain Docker only reports "unhealthy" and
  restarts nothing. Compose reads the check to start the services that depend on it, and can
  override it. Swarm replaces an unhealthy task. Buildah drops `HEALTHCHECK` from images it writes
  in the OCI format. So: under Compose, the check goes in `compose.yaml`
  ([compose.md](compose.md) section 3); under Kubernetes, in the probes; in the image only where
  Docker or Swarm runs it.
- **A read-only root filesystem is a point to adapt.** It stops an attacker from changing files,
  and it breaks Python services in known ways: Docker mounts a `tmpfs` with `noexec,nosuid,nodev`
  by default; runc 1.2.8 and 1.3.3 brought up a bare `tmpfs` as root-owned `0755` (fixed in
  the next runc releases); libraries such as numba and the Hugging Face hub write
  caches under `$HOME` or `site-packages`; and a `tmpfs` counts against the memory limit. If you
  turn it on, give each writable path its own `tmpfs` with an owner and a mode
  ([compose.md](compose.md) section 7), and point each cache variable at one of them.

## 7. Lint the Dockerfile

- **Pin the Dockerfile frontend and turn its build checks into errors.** The first two lines of
  the Dockerfile:

  ```dockerfile
  # syntax=docker/dockerfile:1.28.0@sha256:...
  # check=error=true
  ```

  BuildKit runs its build checks on every build, but only as warnings, and a warning nobody must
  fix is noise ([static-checks.md](../../python/static-checks/static-checks.md) section 5 says the
  same of the Python checks: a check is on or off). With `error=true`, the build that CI runs is
  the lint gate, and no second tool needs a pin of its own. The pinned frontend version keeps a new
  check from failing yesterday's Dockerfile without a pull request; the update bot (section 4)
  moves it.
- **Know what the build checks do not see:** a missing `USER`, a health check the runtime needs, a
  `latest` tag, and, while a `.dockerignore` holds a `!` line, a `COPY` of an excluded path
  (section 2). Review covers these. A team that wants a linter for them adds hadolint (DL3007 flags
  `latest`), run as every other static check is; in a Python repository that is
  [static-checks.md](../../python/static-checks/static-checks.md) sections 3 and 5.

## 8. Tags, labels and the registry

- **Tag each image with its version and its commit (`1.4.2`, `sha-1a2b3c4`), and deploy by
  digest.** Tags can be moved; a digest cannot, and given both, Kubernetes pulls by the digest.
  `latest` is never a deploy target: Kubernetes' documentation says it is "harder to track which
  version of the image is running and more difficult to roll back properly".
- **Write the OCI labels `org.opencontainers.image.source` and `org.opencontainers.image.revision`
  at least.** They tie the image to the repository and the commit. On GitHub's registry, the
  `source` label links the package to its repository, so the package takes the repository's access
  rules. `docker/metadata-action` writes these labels and the tags of the first bullet.
- **Turn on immutable tags where the registry offers them** (Docker Hub, Amazon ECR, Google
  Artifact Registry). GitHub's container registry has no such setting; there, the digest is the
  only fixed reference.

## 9. SBOM, provenance and signatures

- **Attach an SBOM and max-level provenance when CI pushes the image** (`sbom: true`,
  `provenance: mode=max` in `docker/build-push-action`). The SBOM lists what is inside; the
  provenance records how and from what it was built. Docker recommends the max level. It also
  records the Dockerfile and the values of build arguments, one more reason for section 5.
- **Build release images only in CI, never push one from a laptop.** SLSA build levels 2 and 3
  need a hosted build platform that signs its provenance; a build on someone's workstation reaches
  level 1 at most, and nobody can tell what else was on that machine.
- **Sign images only where something verifies the signature before it runs them.** A signature
  that no deploy step checks proves nothing. Where you sign, sign the digest with cosign or
  Notation, and verify against the exact identity and issuer, failing closed: the cosign
  quickstart's `--certificate-identity-regexp=.*` accepts any signer. Docker Content Trust is
  retired, and its `notary.docker.io` service shuts down on 2026-12-08; do not copy advice that
  sets `DOCKER_CONTENT_TRUST=1`.

## 10. The CI job that pushes the image

[ci-example.md](ci-example.md) shows each rule in one workflow.

- **One job lints, builds, tests, scans and pushes, in that order, and a pull request never
  pushes.** Build and load the image into the runner, test it, then push it from the warm
  build cache. A pull request runs every step except the push.
- **Gate the push on one scanner with a written policy, such as "fail on fixable critical and
  high findings".** Scanners disagree: in a 2026 study of the Docker Hub images that carry 85% of
  pulls, two thirds of the distinct vulnerability-package pairs were reported by only one of three
  scanners. So pick one, write down what fails the build, and never read a pass as "no
  vulnerabilities". Which scanner is a point to adapt; in October 2026, Trivy, Grype and Docker
  Scout were all actively released.
- **Waive a finding only in the scanner's ignore file, one vulnerability per entry, with its
  reason and an expiry date, reviewed like code.** Trivy reads `.trivyignore`, where `exp:<date>`
  ends the waiver on that date. A gate with no waiver gets switched off the first time a fix is
  weeks away; [static-checks.md](../../python/static-checks/static-checks.md) section 6 asks the
  same of a suppressed check.
- **Give the job only the permissions it uses:** `contents: read` and `packages: write` to push to
  GitHub's registry; a signed attestation is a step of its own, such as GitHub's `actions/attest`,
  and that step is the one that needs `id-token: write` and `attestations: write`. Check out
  with `persist-credentials: false`, so the token does not stay in `.git/config` for later steps
  to read. Prefer OIDC to long-lived registry keys where the registry supports it.
- **In this job, pin every action to a full commit SHA, with its version in a comment.** Attackers
  moved existing tags to malicious commits in tj-actions (March 2025), reviewdog (March 2025) and
  Trivy's own `trivy-action` (March 2026, 76 of its 77 tags). This job holds write access to the
  registry, and the signing identity where the job signs, so a moved tag here publishes an
  attacker's image under your name. A release marked "Immutable" on GitHub is not enough: the
  badge showed on poisoned `trivy-action` tags. The rule covers the job that pushes images; other
  workflows follow their own practice. Renovate updates SHA pins together with the version comment.
- **Give each image its own cache scope, and keep cache writes away from untrusted code.** Two
  images that share a `scope` overwrite each other's cache. A workflow that runs code from a fork
  must not write the cache the release build reads (section 5).
- **Log in to Docker Hub before the build pulls from it.** Anonymous pulls are limited to 100 per
  six hours per IP address.
- **Build only the platforms you run.** Building several platforms under emulation on one runner
  "can significantly extend build times", in Docker's words.

## 11. The Python case

[dockerfile-example.md](dockerfile-example.md) shows each rule in one Dockerfile.

- **Build the virtual environment with uv the way uv's Docker guide does:** copy the `uv` binary
  from a pinned uv image into the builder stage only; install the dependencies first with
  `uv sync --locked --no-dev --no-install-project` under a cache mount, with `UV_LINK_MODE=copy`;
  then copy the source and install the project with `--no-dev --no-editable`, so the development
  tools stay out of the runtime environment; set `UV_PYTHON_DOWNLOADS=0`, so
  uv uses the image's Python. `--locked` stops the build when `uv.lock` does not match
  `pyproject.toml`, and `--no-editable` installs the project into the environment, so the runtime
  stage needs the environment and nothing else.
- **Use the same Python image for the builder and the runtime stage.** A virtual environment is
  not movable: its scripts hold the absolute path of the interpreter that built it. One `ARG` that
  both `FROM` lines read keeps the two equal.
- **Copy only the virtual environment into the runtime stage, put its `bin` folder first on
  `PATH`, and run the project's entry point directly.** uv stays out of the runtime image, as in
  uv's own production example. `uv run` forwards signals to its child (since uv 0.6.15), but it
  stays the parent process and adds a tool the image does not need.
- **Install in the runtime stage every system library a dependency loads**, such as libpq for
  psycopg without its `binary` extra. The builder's packages do not travel with the virtual
  environment, so a library installed only in the builder is missing when the process starts.
- **Set `PYTHONUNBUFFERED=1`.** Without it, a crash can swallow the last lines the process wrote.
  Where the logs go is [logging.md](../../python/logging/logging.md) section 6.
- **Compiling bytecode at build time (`UV_COMPILE_BYTECODE=1`) is a point to adapt.** It shortens
  the import of the application's main module: 12.3 s to 5.0 s and 22.6 s to 7.3 s in two
  measurements. Image size grew 1.8% (compressed layers) and 24% in the same two. It also costs
  build time.
- **Under an orchestrator that runs replicas, run one server process per container; use several
  workers only on a single host.** The orchestrator already restarts and scales containers; a
  process manager inside each one does the same job again, as FastAPI's and uvicorn's
  documentation say.
- **Bind the server to `0.0.0.0`.** uvicorn listens on `127.0.0.1` by default, which no one
  outside the container can reach. Behind a proxy, set the addresses whose forwarded headers
  uvicorn trusts (`forwarded-allow-ips`).

## 12. Where it stops holding

- **A bind-mounted workspace on Linux.** A bind mount keeps the host's numeric owners, so a
  container user with a fixed UID cannot write files owned by your host user, and the files it
  writes belong to a stranger. Docker Desktop on macOS hides this, so the problem shows up first
  on Linux machines and runners. For a development container, match the container user's UID to
  the host user's; VS Code dev containers do that on Linux, unless the image already has a user
  with that UID (as `ubuntu:24.04` has UID 1000).
- **OpenShift** runs every container under an arbitrary UID that the image cannot know. Make each
  path the process writes owned by group 0 and writable by the group, and leave the UID to the
  platform.
- **Rootless Docker** maps the container's users to a range of your own user's subordinate IDs, so
  a fixed UID in the image is not the UID on disk.
- **A Docker container action on GitHub** must run as root: GitHub's documentation says not to set
  `USER` in its Dockerfile, because the action then cannot write the workspace.
- **Windows containers** are built by the classic builder, which BuildKit does not replace yet.
  This file does not cover them.
- **An image that is not a long-running service** (a command-line tool, a batch job) needs no
  health check, and the rules on server processes in section 11 do not apply to it.
- **An image a person or an agent works in** (a dev container, the agent's image) is a tool, not
  the application: section 3's builder and runtime stages do not apply, because its package
  managers and tools are what it is for. Its other rules hold: pins, no secret in a layer, a
  non-root user.

## 13. Sources

Read in October 2026 unless a date is given.

- Docker documentation: "Building best practices"; "Multi-stage builds"; "Optimize cache usage";
  "Build context" (`.dockerignore`); "Build secrets"; "Build variables"; "Build checks" and the
  build checks reference (`SecretsUsedInArgOrEnv`, `JSONArgsRecommended`, `CopyIgnoredFile`); the
  Dockerfile reference (`HEALTHCHECK`, `STOPSIGNAL`, `RUN --mount`, parser directives); "Custom
  Dockerfile syntax"; attestations, SBOM and SLSA provenance; GitHub Actions guides (cache,
  attestations, test before push, multi-platform, tags and labels); "Usage and limits" for Docker
  Hub pulls; Docker Hardened Images (use, mirror, scan); "Deprecated features" (the classic
  builder); Docker Engine 28 and 29 release notes (bundled runc); `docker container run`
  (`--init`); "Docker Content Trust" and Docker's DCT retirement guidance (2026-06-16).
- BuildKit (moby/buildkit): the cache-mount note added to the Dockerfile reference on
  2026-10-05; advisory GHSA-f2v9-hprr-32q3 (CVE-2026-93318); issue #7125. tonistiigi/fsutil
  `filter.go` and `filter_test.go`, moby/patternmatcher, moby/go-archive (how exceptions in
  `.dockerignore` are walked); docker/buildx issue #850.
- Docker Hub, the `python` image page (naming the Debian release); docker-library FAQ.
- Python documentation: `venv`, the `signal` module, command-line `-u` and `PYTHONUNBUFFERED`.
  Linux man-pages 6.19: `pid_namespaces(7)`, `kill(2)`.
- uv documentation, "Using uv in Docker" (2026-10-14) and "Running commands"; the
  `astral-sh/uv-docker-example` repository; uv pull request #13017 (signal forwarding) and issues
  #8296 and #8483 (credentials in written files).
- FastAPI, "FastAPI in Containers"; uvicorn documentation (deployment, Docker, settings);
  gunicorn documentation (signals, Docker guide).
- Kubernetes documentation, "Images"; containerd discussion #7657 and Kubernetes issue #50703 (the
  image `HEALTHCHECK`); the OCI image specification (config, annotations); Buildah
  `buildah-config(1)`; Docker Swarm, "How services work".
- Renovate documentation (Dockerfile manager, Docker datasource, configuration options) and its
  preset pages (`docker:pinDigests`, `helpers:pinGitHubActionDigests`,
  `customManagers:dockerfileVersions`); GitHub's Dependabot documentation and dependabot-core
  issue #7640.
- Trivy documentation, "Filtering" (`.trivyignore`, `exp:`).
- Python Packaging User Guide, the `pyproject.toml` specification (`readme`); Psycopg 3
  documentation, "Installation" (the `binary` extra and libpq).
- Sysdig, "Dockerfile best practices" (executables owned by root and not writable).
- NIST SP 800-190, *Application Container Security Guide* (2017, section 4.1); OWASP Docker
  Security Cheat Sheet; CIS Docker Benchmark 1.9.0 (version and date only; the text is gated).
- SLSA specification v1.2, build track; Sigstore cosign documentation (signing and verifying).
- GitHub documentation: "Secure use reference" (pinning actions, `GITHUB_TOKEN` permissions),
  publishing packages with Actions, working with the container registry, OpenID Connect,
  immutable releases. Advisories GHSA-mrrh-fwg8-r2c3 (tj-actions, CVE-2025-30066) and
  GHSA-69fq-xp46-6x23 (Trivy, CVE-2026-33634); Aqua Security's incident post (updated
  2026-04-01); Wiz on reviewdog/action-setup (2025-03-17).
- Studies: Kapelinski, Machado and Kreutz, arXiv:2608.02669 (2026, preprint: scanner
  disagreement); Flare, "Docker Hub secrets exposed" (2025-12-10).
- Incidents and reports: GoogleCloudPlatform/cloud-sql-proxy issue #2651 (a platform manifest
  pinned instead of the index); a Hugging Face forum thread on the bookworm-to-trixie move
  (2025-08-14); runc issue #4971 (tmpfs mode); vLLM pull request #55422 and a second measured
  service (bytecode compilation); Itamar Turner-Trauring, pythonspeed.com (base images, Alpine,
  rebuilding without the cache, updated 2026).
- Red Hat OpenShift documentation, "Creating images" (arbitrary UIDs); GitHub documentation,
  "Dockerfile support for GitHub Actions"; VS Code documentation, "Add a non-root user to a
  container".
