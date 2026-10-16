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
  Debian release overnight and broke builds that nobody had touched (section 4) [1].
- A process that ignores SIGTERM is killed after ten seconds, in the middle of its requests [2].

Docker's own documentation calls every Dockerfile practice "should" or "recommended", never
"must" [3]. This file decides which of them are rules here, and says why.

## 2. The build context: an allow-list

The build context is every file the builder receives. A `COPY . .` puts all of it into a layer.

- **Write `.dockerignore` as an allow-list: `*` on the first line, then one `!` line for each
  path the build reads.** A deny-list fails open: it misses what nobody thought of, such as a
  nested `.env`, a key file, or the `.claude/` folder a coding agent writes. In a scan of the
  images uploaded to Docker Hub in November 2025, Flare found 10,456 that leaked secrets, and
  files swept in by whole-directory copies were one of the most frequent causes [4]. An
  allow-list fails closed: a new file stays out until someone lists it. Docker's documentation
  explains the syntax but does not say what to exclude [5]. The choice is yours to make on
  purpose.
- **Keep each `!` line a literal path at the top of the context** (`!src`, `!pyproject.toml`),
  never a glob such as `!bin/*/tool`. BuildKit and the classic builder both walk an excluded
  folder only along the literal paths that `!` lines name [6], [7]. A glob inside an exception
  works on BuildKit, but not on the classic builder, and the Docker CLI still falls back to the
  classic builder when the buildx plugin is missing [6], [7], [8].
- **After the `!` lines, exclude again what may sit inside the folders you let in:** `**/.env`,
  `**/__pycache__`, local test output. The last line that matches a path decides, so these lines
  win over `!src` for the files they name [5]. That `.env` never reaches an image is a rule of
  [python.md](../../python/language/python.md) section 5; this is how an allow-list keeps it.
  Inside a folder you let in, these lines are a deny-list, so run the check below also when files
  are added under such a folder.
- **List every file the build backend reads, too**, such as a `README.md` that `pyproject.toml`
  names as its `readme`. The `pyproject.toml` specification makes `readme` "a path relative to
  `pyproject.toml` to a text file", and Docker removes an excluded file from the context before
  the builder receives it, so a missing file fails the build [9], [5]. That is the allow-list
  working, but plan for it.
- **When one build context serves several Dockerfiles, give each the list it needs:** its own
  `<name>.Dockerfile.dockerignore` beside it, or one `.dockerignore` at the context root that lists
  what any of them reads. A file named after the Dockerfile with `.dockerignore` added
  (`proxy.Dockerfile.dockerignore`) sits beside it and wins over the context's `.dockerignore` [5].

Check: after you change `.dockerignore`, list what the builder receives. The `CopyIgnoredFile`
build check (section 7) goes silent once the file holds any `!` line, a BuildKit bug still open in
October 2026 [10], so the build will not warn you:

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
  smaller and has fewer packages to patch [11]. BuildKit builds only the stages the target
  needs [11].
- **Name each stage (`FROM … AS builder`) and copy from it by name.** A `COPY --from=0` breaks the
  day someone reorders the stages; a name does not [11].
- **Order the steps from the least to the most often changed: the dependency manifest and lock
  file, the install, then the source.** A changed layer rebuilds every layer after it [12]. With
  this order, an edit to the source reuses the installed dependencies.
- **Give the package manager a cache mount (`RUN --mount=type=cache,target=…`), and expect it to
  help local builds only.** A cache mount lives in the builder's own storage [13]. It is not part
  of the cache that `--cache-to` exports, so a fresh CI runner starts with it empty [13]. In CI
  the exported layer cache does that work (section 10).
- **Read build-only files through a bind mount (`RUN --mount=type=bind,source=…`) when one `RUN`
  needs them**, as the dependency step does with the lock file. Nothing from a bind mount lands in
  a layer [12].
- **Run `apt-get update` and `apt-get install` in one `RUN`.** An `update` cached in a layer of
  its own leaves a later install with old package lists [3].
- **Set `pipefail` before a pipe.** `/bin/sh -c` checks only the last exit code of a pipe, so
  start such a `RUN` with `set -o pipefail &&`; Debian's `dash` may not support the option, so
  there run that step through `bash` in the exec form of `RUN` [3].
- **Give `WORKDIR` an absolute path.** An absolute `WORKDIR`, instead of `RUN cd`, does not depend
  on where the steps before it left off [3].
- **Copy local files with `COPY`, not `ADD`.** `ADD` also unpacks archives and fetches URLs, so a
  `COPY` does only what the line shows [3].

## 4. The base image and its pins

The base image is a choice each team makes. No source shows one option failing for everyone, and
Docker's own pages point to different ones [14], [3]. The options for a Python service, with what
each costs, as of October 2026:

| Option | What you get | What it costs |
|---|---|---|
| Docker Official Image, `python:<version>-slim-<debian release>` | the image most guides use; the maintainers strive to republish it at least monthly [15] | a full Debian userland, so scanners report many CVEs [16]; the count varies several-fold with the scanner |
| Docker Hardened Images, `dhi.io/python` | a minimal image, free under Apache 2.0, with SBOM and provenance [17] | a login to `dhi.io` [18]; mirroring to your own registry is paid [19]; its low CVE count relies on VEX statements that only Docker Scout applies without setup [20] |
| Chainguard, `cgr.dev/chainguard/python` | a minimal image | the free tier serves `:latest` only [21]; a 2023 Chainguard announcement says it moves across minor Python versions and a digest pin on the free tier receives no updates or fixes [22] |
| Google distroless, `python3-debian13` | no shell, a minimal runtime [23] | Python is Debian's package, fixed at 3.13 [23], [24]; four tags only [25]; the builder stage must match its path and ABI [23] |
| Alpine, `python:<version>-alpine` | a small image | musl instead of glibc: Itamar Turner-Trauring notes that wheels exist for most packages but not all, so some installs compile from source [26] |

Whatever the choice:

- **Name the distribution release in the tag: `python:3.13-slim-trixie`, not `python:3.13-slim`.**
  A tag without it moves to the next Debian release when one ships [27]. That move from bookworm
  to trixie broke builds of Hugging Face Spaces in August 2025, and the image's own page asks you
  to name the release [1], [27].
- **Pin every image the build pulls by its digest: each `FROM`, each `COPY --from=<image>`, and
  the `# syntax=` frontend (section 7).** A tag can be moved to a different image at any time [3].
  A digest is the hash of the content: it cannot change, you can audit it, and you can roll back to
  it [3], [28]. Given a tag and a digest together, Kubernetes pulls by the digest alone [28].
- **Pin the multi-platform index digest, not the digest of one platform's manifest.** The Cloud
  SQL Proxy project pinned an amd64 manifest and shipped an x86-64 userland inside its arm64
  image [29]. The `Digest:` line at the top of `docker buildx imagetools inspect <image>:<tag>` is
  the index digest [30].
- **Keep the pins moving with a bot that reads every `FROM` and every `COPY --from` line.** Docker
  warns that a digest pin means you update by hand, and that "you're opting out of automated
  security fixes" [3]. Renovate updates every `FROM` line, `COPY --from` images, `ARG` defaults and the
  `# syntax=` image [31]. Dependabot updates only the first `FROM` of a Dockerfile and does not
  support multi-stage builds, so it misses most of a Dockerfile written by section 3 [32].
  Renovate pins no digest by default: turn on its `docker:pinDigests` and
  `helpers:pinGitHubActionDigests` presets ([dockerfile-example.md](dockerfile-example.md)
  section 5) [33], [34], [35].
- **Rebuild on a schedule, not only when the code changes.** An image rebuilt from cache keeps
  the old packages; only a rebuild that pulls the base image again (`--pull`) and runs the install
  again picks up the fixes [3], [36]. With digest pins, the bot's pull request is that rebuild.

## 5. Secrets at build time

- **Pass a credential the build needs only through `RUN --mount=type=secret` or
  `RUN --mount=type=ssh`, never through `ARG` or `ENV`.** Build arguments and environment values
  persist in the image history and, with max-level provenance (section 9), in the attestation
  next to the image [37]. A secret mount is present only for the one `RUN` that names it and never
  appears in provenance [38], [39]. The `SecretsUsedInArgOrEnv` build check catches the common
  names, not all of them [40].
- **Check that the tool you run does not write the credential into a file the image keeps.** A
  secret mount protects the way the value arrives, not what the tool does with it: in 2024, uv
  wrote package-index credentials into `uv.lock` and `pyproject.toml` [41], [42]. Read the files a
  step writes before you trust it with a credential.
- **Never let one builder, or one build cache, serve builds of different trust levels.** In
  BuildKit up to 0.33.0, a malicious image could poison a shared cache and read the secrets
  mounted into another build (CVE-2026-93318) [43]. In CI, give cache write access only to
  workflows that run your own code (section 10).

## 6. The process at run time

- **Run the process as a non-root user with a fixed UID and GID set in the image (`USER
  10001:10001`).** Without user namespaces, a root process that escapes the container is root on
  the host [44]; NIST SP 800-190, OWASP and CIS all ask for a non-privileged user [45], [46], [47].
  A fixed number keeps file ownership the same in every build, while a user created without one may
  get a different ID next time [3]. Section 12 names where a fixed UID stops holding.
- **Leave the application's files owned by root, readable but not writable by that user.** The
  process cannot rewrite its own code, so an attacker who controls it cannot change what the next
  request runs, and the image stays what CI built. Sysdig's Dockerfile guide asks the
  same: "Make executables owned by root and not writable" [48].
- **Start the process with an exec-form `CMD`: `CMD ["acme-api"]`, never `CMD acme-api`.** In
  shell form, `/bin/sh` is PID 1 and the application, as its child, never receives SIGTERM [49],
  [13].
- **Make sure PID 1 handles SIGTERM, or run an init.** Linux delivers to PID 1 only the signals
  it has installed a handler for [50]. CPython installs none for SIGTERM; uvicorn and gunicorn
  do [51], [52], [53]. Without a handler, `docker stop` waits ten seconds and then kills the
  process [2]. Run an init (`docker run --init`, or `init: true` in Compose, which runs tini) when
  PID 1 starts child processes it does not wait for, such as a shell script or a coding agent
  ([agent-containers.md](agent-containers.md) section 6) [54], [55].
- **Put the health check where the runtime that acts on it reads it.** Akihiro Suda, a
  containerd maintainer, notes that Kubernetes does not use the image's `HEALTHCHECK` [56], and a
  2017 Kubernetes issue reports the conflict with its own probes [57]. Plain Docker only reports "unhealthy"
  and restarts nothing [13], [58]. Compose reads the check to start the services that depend on
  it, and can override it [55]. Swarm replaces an unhealthy task [59]. Buildah drops `HEALTHCHECK`
  from images it writes in the OCI format [60]. So: under Compose, the check goes in
  `compose.yaml` ([compose.md](compose.md) section 3); under Kubernetes, in the probes; in the
  image only where Docker or Swarm runs it.
- **A read-only root filesystem is a point to adapt.** It stops an attacker from changing files,
  and it breaks Python services in known ways: Docker mounts a `tmpfs` with `noexec,nosuid,nodev`
  by default [61]; runc 1.2.8 and 1.3.3 brought up a bare `tmpfs` as root-owned `0755` (fixed in
  the next runc releases) [62], [63], [64]; libraries such as numba and the Hugging Face hub write
  caches under `$HOME` or `site-packages` [65], [66]; and a `tmpfs` counts against the memory
  limit [67]. If you turn it on, give each writable path its own `tmpfs` with an owner and a mode
  ([compose.md](compose.md) section 7), and point each cache variable at one of them.

## 7. Lint the Dockerfile

- **Pin the Dockerfile frontend and turn its build checks into errors.** The first two lines of
  the Dockerfile:

  ```dockerfile
  # syntax=docker/dockerfile:1.28.0@sha256:...
  # check=error=true
  ```

  BuildKit runs its build checks on every build, but only as warnings [68]. A warning nobody must
  fix is noise ([static-checks.md](../../python/static-checks/static-checks.md) section 5 says the
  same of the Python checks: a check is on or off). With `error=true`, the build that CI runs is
  the lint gate, and no second tool needs a pin of its own [68]. The pinned frontend version keeps
  a new check from failing yesterday's Dockerfile without a pull request; the update bot
  (section 4) moves it [69].
- **Know what the build checks do not see:** a missing `USER`, a health check the runtime needs, a
  `latest` tag, and, while a `.dockerignore` holds a `!` line, a `COPY` of an excluded path
  (section 2) [70], [10]. Review covers these. A team that wants a linter for them adds hadolint
  (DL3007 flags `latest`), run as every other static check is; in a Python repository that is
  [static-checks.md](../../python/static-checks/static-checks.md) sections 3 and 5 [71].

## 8. Tags, labels and the registry

- **Tag each image with its version and its commit (`1.4.2`, `sha-1a2b3c4`), and deploy by
  digest.** Tags can be moved; a digest cannot, and given both, Kubernetes pulls by the
  digest [28]. `latest` is never a deploy target: Kubernetes' documentation says it is "harder to
  track which version of the image is running and more difficult to roll back properly" [28].
- **Write the OCI labels `org.opencontainers.image.source` and `org.opencontainers.image.revision`
  at least.** They tie the image to the repository and the commit [72]. On GitHub's registry, the
  `source` label links the package to its repository, so the package takes the repository's access
  rules [73], [74]. `docker/metadata-action` writes these labels and the tags of the first
  bullet [75].
- **Turn on immutable tags where the registry offers them** (Docker Hub, Amazon ECR, Google
  Artifact Registry) [76], [77], [78]. GitHub's documentation names no such setting for its
  container registry, and a commenter on the feature request says a pushed tag "can always be
  retargeted" [79]. There, the digest is the only fixed reference.

## 9. SBOM, provenance and signatures

- **Attach an SBOM and max-level provenance when CI pushes the image** (`sbom: true`,
  `provenance: mode=max` in `docker/build-push-action`). The SBOM lists what is inside; the
  provenance records how and from what it was built [80]. Docker recommends the max level [81]. It
  also records the Dockerfile and the values of build arguments, one more reason for
  section 5 [39].
- **Build release images only in CI, never push one from a laptop.** SLSA build levels 2 and 3
  need a hosted build platform that signs its provenance; a build on someone's workstation reaches
  level 1 at most, and nobody can tell what else was on that machine [82], [83].
- **Sign images only where something verifies the signature before it runs them.** A signature
  that no deploy step checks proves nothing. Where you sign, sign the digest with cosign or
  Notation [84], [85], and verify against the exact identity and issuer [86], failing closed: the
  cosign quickstart's `--certificate-identity-regexp=.*` accepts any signer [87].
  Docker Content Trust is being retired, and its `notary.docker.io` service shuts down on
  2026-12-08 [88]; do not copy advice that sets `DOCKER_CONTENT_TRUST=1`.

## 10. The CI job that pushes the image

[ci-example.md](ci-example.md) shows each rule in one workflow.

- **One job lints, builds, tests, scans and pushes, in that order, and a pull request never
  pushes.** Build and load the image into the runner, test it, then push it from the warm
  build cache [89]. A pull request runs every step except the push.
- **Gate the push on one scanner with a written policy, such as "fail on fixable critical and
  high findings".** Scanners disagree: in a 2026 study of the Docker Hub images that carry 85% of
  pulls, Kapelinski, Machado and Kreutz found that two thirds of the distinct
  vulnerability-package pairs were reported by only one of the three vulnerability scanners [90].
  So pick one, write down what fails the build, and never read a pass as "no vulnerabilities".
  Which scanner is a point to adapt; in October 2026, Trivy, Grype and Docker Scout were all
  actively released [91], [92], [93].
- **Waive a finding only in the scanner's ignore file, one vulnerability per entry, with its
  reason and an expiry date, reviewed like code.** Trivy reads `.trivyignore`, where `exp:<date>`
  ends the waiver on that date [94]. A gate with no waiver gets switched off the first time a fix
  is weeks away; [static-checks.md](../../python/static-checks/static-checks.md) section 6 asks
  the same of a suppressed check.
- **Give the job only the permissions it uses [126]:** `contents: read` and `packages: write` to push to
  GitHub's registry [95]; a signed attestation is a step of its own, such as GitHub's
  `actions/attest`, and that step is the one that needs `id-token: write` and
  `attestations: write` [96]. Check out with `persist-credentials: false`, so the checkout leaves
  no token for later steps to read [97]. Prefer OIDC to long-lived registry keys where the registry
  supports it [98].
- **In this job, pin every action to a full commit SHA [126], with its version in a comment.** Attackers
  moved existing tags to malicious commits in tj-actions (March 2025), reviewdog (March 2025) and
  Trivy's own `trivy-action` (March 2026, 76 of its 77 tags) [99], [100], [101]. This job holds
  write access to the registry, and the signing identity where the job signs, so a moved tag here
  publishes an attacker's image under your name. A release marked "Immutable" on GitHub is not
  enough: the badge showed on poisoned `trivy-action` tags [102], [101]. The rule covers the job
  that pushes images; other workflows follow their own practice. Renovate updates SHA pins
  together with the version comment [103], [127].
- **Give each image its own cache scope, and keep cache writes away from untrusted code.** Two
  images that share a `scope` overwrite each other's cache [104]. A workflow that runs code from a
  fork must not write the cache the release build reads (section 5) [105].
- **Log in to Docker Hub before the build pulls from it.** Anonymous pulls are limited to 100 per
  six hours per IP address [106].
- **Build only the platforms you run.** Building several platforms under emulation on one runner
  "can significantly extend build times", in Docker's words [107].

## 11. The Python case

[dockerfile-example.md](dockerfile-example.md) shows each rule in one Dockerfile.

- **Build the virtual environment with uv the way uv's Docker guide and its example repository
  do:** copy the `uv` binary from a pinned uv image into the builder stage only; install the
  dependencies first with `uv sync --locked --no-dev --no-install-project` under a cache mount,
  with `UV_LINK_MODE=copy`; then copy the source and install the project with
  `--no-dev --no-editable`, so the development tools stay out of the runtime environment; set
  `UV_PYTHON_DOWNLOADS=0`, so uv uses the image's Python [108], [109]. `--locked` stops the build
  when `uv.lock` does not match `pyproject.toml`, and `--no-editable` installs the project into the
  environment, so the runtime stage needs the environment and nothing else [110], [108].
- **Use the same Python image for the builder and the runtime stage.** A virtual environment is
  not movable: its scripts hold the absolute path of the interpreter that built it [111], [109].
  One `ARG` that both `FROM` lines read keeps the two equal.
- **Copy only the virtual environment into the runtime stage, put its `bin` folder first on
  `PATH`, and run the project's entry point directly.** uv stays out of the runtime image, as in
  uv's own production example [109]. `uv run` forwards signals to its child (since uv 0.6.15), but
  it stays the parent process and adds a tool the image does not need [112], [113].
- **Install in the runtime stage every system library a dependency loads**, such as libpq for
  psycopg without its `binary` extra [114]. The builder's packages do not travel with the virtual
  environment, so a library installed only in the builder is missing when the process starts.
- **Set `PYTHONUNBUFFERED=1`.** Without it, a crash can swallow the last lines the process
  wrote [109], [115]. Where the logs go is [logging.md](../../python/logging/logging.md) section 6.
- **Compiling bytecode at build time (`UV_COMPILE_BYTECODE=1`) is a point to adapt.** It shortens
  the import of the application's main module: 12.3 s to 5.0 s in vLLM and 22.6 s to 7.3 s in
  Navi, two measured projects [116], [117]. Image size grew 1.8% (compressed layers) and 24% in
  the same two [116], [117]. It also costs build time [108].
- **Under an orchestrator that runs replicas, run one server process per container; use several
  workers only on a single host.** The orchestrator already restarts and scales containers; a
  process manager inside each one does the same job again, as FastAPI's and uvicorn's
  documentation say [118], [119].
- **Bind the server to `0.0.0.0`.** uvicorn listens on `127.0.0.1` by default, which no one
  outside the container can reach [120]. Behind a proxy, set the addresses whose forwarded headers
  uvicorn trusts (`forwarded-allow-ips`) [120].

## 12. Where it stops holding

- **A bind-mounted workspace on Linux.** A bind mount keeps the host's numeric owners, so a
  container user with a fixed UID cannot write files owned by your host user, and the files it
  writes belong to a stranger [121]. Docker Desktop on macOS hides this, so the problem shows up
  first on Linux machines and runners [121]. For a development container, match the container
  user's UID to the host user's; VS Code dev containers do that on Linux, unless the image already
  has a user with that UID (as `ubuntu:24.04` has UID 1000) [121], [122].
- **OpenShift** runs containers under an arbitrary UID by default, which the image cannot
  know [123]. Make each path the process writes owned by group 0 and writable by the group, and
  leave the UID to the platform [123].
- **Rootless Docker** maps container UID 0 to your own UID and other container UIDs into your
  subordinate range, so a fixed UID in the image is not the UID on disk [124].
- **A Docker container action on GitHub** must run as root: GitHub's documentation says not to set
  `USER` in its Dockerfile, because the action then cannot write the workspace [125].
- **Windows containers** are built by the classic builder, which BuildKit does not replace
  yet [8]. This file does not cover them.
- **An image that is not a long-running service** (a command-line tool, a batch job) needs no
  health check, and the rules on server processes in section 11 do not apply to it.
- **An image a person or an agent works in** (a dev container, the agent's image) is a tool, not
  the application: section 3's builder and runtime stages do not apply, because its package
  managers and tools are what it is for. Its other rules hold: pins, no secret in a layer, a
  non-root user.

## 13. Sources

Checked 2026-10-16 unless a line ends with — checked <YYYY-MM-DD>.

- [1] hysts — reply 7 in "Build Error: Job failed with exit code: 1 (while creating a space at hugging Face)" (Hugging Face Forums, 2025; case) — https://discuss.huggingface.co/t/build-error-job-failed-with-exit-code-1-while-creating-a-space-at-hugging-face/166760/7
- [2] Docker — docker container stop (CLI reference) — https://docs.docker.com/reference/cli/docker/container/stop/
- [3] Docker — Building best practices — https://docs.docker.com/build/building/best-practices/
- [4] Assaf Morag — Thousands of Exposed Secrets Found on Docker Hub, Putting Organizations at Risk (Flare, 2025; research, sponsored by Flare) — https://flare.io/learn/resources/docker-hub-secrets-exposed
- [5] Docker — Build context — https://docs.docker.com/build/concepts/context/#dockerignore-files
- [6] Tõnis Tiigi — fsutil `filter.go`, the build-context filter BuildKit uses — https://github.com/tonistiigi/fsutil/blob/468ba298314d055d18a6887781b2517dfc6ec9e0/filter.go
- [7] Moby project — go-archive `archive.go`, which the Docker CLI's classic build path uses to pack the context — https://github.com/moby/go-archive/blob/66cf06fd9d1f416faec05a3ed241b702e8941a85/archive.go
- [8] Docker — Deprecated Docker Engine features — https://docs.docker.com/engine/deprecated/#legacy-builder-for-linux-images
- [9] Python Packaging Authority — pyproject.toml specification, `readme` — https://packaging.python.org/en/latest/specifications/pyproject-toml/#readme
- [10] Saeed ur Rehman Turk — CopyIgnoredFile goes silent for all files when the .dockerignore contains any negated pattern (moby/buildkit issue #7125, 2026; case) — https://github.com/moby/buildkit/issues/7125
- [11] Docker — Multi-stage builds — https://docs.docker.com/build/building/multi-stage/
- [12] Docker — Optimize cache usage in builds — https://docs.docker.com/build/cache/optimize/
- [13] Docker — Dockerfile reference (BuildKit `frontend/dockerfile/docs/reference.md`) — https://github.com/moby/buildkit/blob/f74a37c4c978e3d01a04540b39039442456d9c4c/frontend/dockerfile/docs/reference.md
- [14] Docker — Python language-specific guide — https://docs.docker.com/guides/python/
- [15] Docker Official Images — FAQ — https://github.com/docker-library/faq
- [16] Javier Cañete — Wolfi vs Alpine vs distroless, medido con la misma app en Docker (jacar.es, 2026; research) — https://jacar.es/wolfi-vs-alpine-vs-distroless/
- [17] Docker — Docker Hardened Images — https://docs.docker.com/dhi/
- [18] Docker — Use a Docker Hardened Image — https://docs.docker.com/dhi/how-to/use/
- [19] Docker — Mirror a Docker Hardened Image repository — https://docs.docker.com/dhi/how-to/mirror/
- [20] Docker — Scan Docker Hardened Images — https://docs.docker.com/dhi/how-to/scan/
- [21] Chainguard — Chainguard Containers versions (Versions available by tier) — https://edu.chainguard.dev/chainguard/containers/concepts/lifecycle-and-eol/versions/
- [22] Chainguard — Important updates for Chainguard Images public catalog users, 16 August 2023 — https://www.chainguard.dev/unchained/important-updates-for-chainguard-images-public-catalog-users
- [23] Google — distroless `python3/README.md` — https://github.com/GoogleContainerTools/distroless/blob/22b97d104cef7422b48190d0902fedf58ccc84fe/python3/README.md
- [24] Appu — reply in "[Feature request] Add support for Python 3.14" (GoogleContainerTools/distroless issue #2080, 2026; opinion) — https://github.com/GoogleContainerTools/distroless/issues/2080
- [25] Google — distroless `README.md`, the image and tag table — https://github.com/GoogleContainerTools/distroless/blob/22b97d104cef7422b48190d0902fedf58ccc84fe/README.md
- [26] Itamar Turner-Trauring — Using Alpine can make Python Docker builds 50× slower (pythonspeed.com, 2026; opinion) — https://pythonspeed.com/articles/alpine-docker-python/
- [27] Docker Official Images — python (Docker Hub page) — https://hub.docker.com/_/python
- [28] Kubernetes — Images — https://kubernetes.io/docs/concepts/containers/images/
- [29] Shun Yanaura — Alpine image: linux/arm64 variant ships an x86-64 userland because Dockerfile.alpine pins an amd64-specific base digest (GoogleCloudPlatform/cloud-sql-proxy issue #2651, 2026; case) — https://github.com/GoogleCloudPlatform/cloud-sql-proxy/issues/2651
- [30] Docker — docker buildx imagetools inspect (CLI reference) — https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/
- [31] Renovate — Dockerfile manager, 44.164.10 — https://github.com/renovatebot/renovate/blob/44.164.10/lib/modules/manager/dockerfile/readme.md
- [32] GitHub — Guidance for the configuration of private registries for Dependabot — https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/configure-private-registries
- [33] Renovate — Configuration options: `pinDigests` — https://docs.renovatebot.com/configuration-options/#pindigests
- [34] Renovate — Docker presets: `docker:pinDigests` — https://docs.renovatebot.com/presets-docker/#dockerpindigests
- [35] Renovate — Helper presets: `helpers:pinGitHubActionDigests` — https://docs.renovatebot.com/presets-helpers/#helperspingithubactiondigests
- [36] Itamar Turner-Trauring — Avoiding insecure images from Docker build caching (pythonspeed.com, 2026; opinion) — https://pythonspeed.com/articles/docker-cache-insecure-images/
- [37] Docker — Build variables — https://docs.docker.com/build/building/variables/
- [38] Docker — Build secrets — https://docs.docker.com/build/building/secrets/
- [39] Docker — Provenance attestations — https://docs.docker.com/build/metadata/attestations/slsa-provenance/
- [40] Docker — Build checks: SecretsUsedInArgOrEnv — https://docs.docker.com/reference/build-checks/secrets-used-in-arg-or-env/
- [41] João Bernardo Oliveira — uv index feature will leak credentials to uv.lock (astral-sh/uv issue #8296, 2024; case) — https://github.com/astral-sh/uv/issues/8296
- [42] Ky Waegel — `uv add` leaks credentials to `tool.uv.index` when `UV_DEFAULT_INDEX` is set (astral-sh/uv issue #8483, 2024; case) — https://github.com/astral-sh/uv/issues/8483
- [43] Moby BuildKit — GHSA-f2v9-hprr-32q3, Cache poisoning via unvalidated image layer DiffIDs (CVE-2026-93318) — https://github.com/moby/buildkit/security/advisories/GHSA-f2v9-hprr-32q3
- [44] Docker — Docker Engine security — https://docs.docker.com/engine/security/
- [45] NIST — SP 800-190, Application Container Security Guide, September 2017 — https://doi.org/10.6028/NIST.SP.800-190
- [46] OWASP Cheat Sheet Series — Docker Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
- [47] Docker — Docker Bench for Security, `tests/4_container_images.sh` (checks of the CIS Docker Benchmark v1.6.0) — https://github.com/docker/docker-bench-security/blob/68c8e53dac03e4762a7d4da826700a75ac1c9ada/tests/4_container_images.sh
- [48] Sysdig — Top 21 Dockerfile best practices for container security (Sysdig, 2026; opinion) — https://www.sysdig.com/learn-cloud-native/dockerfile-best-practices
- [49] Docker — Build checks: JSONArgsRecommended — https://docs.docker.com/reference/build-checks/json-args-recommended/
- [50] Linux man-pages project — pid_namespaces(7), man-pages 6.19 — https://man7.org/linux/man-pages/man7/pid_namespaces.7.html
- [51] Python Software Foundation — signal, Set handlers for asynchronous events — https://docs.python.org/3/library/signal.html#general-rules
- [52] Uvicorn — `uvicorn/server.py`, the signal handlers — https://github.com/Kludex/uvicorn/blob/528a3ac5031bf777ccd966d74db3034fe99fd69c/uvicorn/server.py
- [53] Gunicorn — Signal Handling, 26.2.2 — https://github.com/benoitc/gunicorn/blob/26.2.2/docs/content/signals.md
- [54] Docker — docker container run (CLI reference) — https://docs.docker.com/reference/cli/docker/container/run/#init
- [55] Compose Specification — `spec.md` (`healthcheck`, `depends_on`) and `container_spec.md` (`init`) — https://github.com/compose-spec/compose-spec/tree/de28432802a367d650bd4ad6748b19491b6cf986
- [56] Akihiro Suda — reply in "HEALTHCHECK Dockerfile instruction" (containerd discussion #7657, 2022; opinion) — https://github.com/containerd/containerd/discussions/7657
- [57] Otto Yiu — Disable Health Checks from Docker daemon to prevent conflict with liveliness probes (kubernetes/kubernetes issue #50703, 2017; case) — https://github.com/kubernetes/kubernetes/issues/50703
- [58] Docker — Start containers automatically (restart policies) — https://docs.docker.com/engine/containers/start-containers-automatically/
- [59] Docker — How services work (Swarm mode) — https://docs.docker.com/engine/swarm/how-swarm-mode-works/services/
- [60] Buildah — buildah-config(1), v1.45.2 — https://github.com/containers/buildah/blob/v1.45.2/docs/buildah-config.1.md
- [61] Moby project — `daemon/oci_linux.go`, the default options of a `tmpfs` mount — https://github.com/moby/moby/blob/9ebf533c56ea2e6836649354f6c0589fd1c2df23/daemon/oci_linux.go
- [62] opencontainers/runc — Recent security update changed default permissions of tmpfs (runc issue #4971, 2025; case) — https://github.com/opencontainers/runc/issues/4971
- [63] opencontainers/runc — runc v1.2.9 release notes — https://github.com/opencontainers/runc/releases/tag/v1.2.9
- [64] opencontainers/runc — runc v1.3.4 release notes — https://github.com/opencontainers/runc/releases/tag/v1.3.4
- [65] nos-tromo — Kimi-K3 warmup imports Kimi code for every model; startup crashes as non-root / read-only (numba "no locator available") (vllm-project/vllm issue #59250, 2026; case) — https://github.com/vllm-project/vllm/issues/59250
- [66] Hugging Face — huggingface_hub environment variables, `HF_HOME`, v2.2.0 — https://github.com/huggingface/huggingface_hub/blob/v2.2.0/docs/source/en/package_reference/environment_variables.md
- [67] Docker — tmpfs mounts — https://docs.docker.com/engine/storage/tmpfs/
- [68] Docker — Checking your build configuration (build checks) — https://docs.docker.com/build/checks/
- [69] Docker — Custom Dockerfile syntax (BuildKit frontend) — https://docs.docker.com/build/buildkit/frontend/
- [70] Docker — Build checks reference, the rules of `docker/dockerfile` 1.28.0 — https://github.com/moby/buildkit/tree/dockerfile/1.28.0/frontend/dockerfile/docs/rules
- [71] hadolint — README, the rules table (DL3007), v2.15.1 — https://github.com/hadolint/hadolint/blob/v2.15.1/README.md
- [72] Open Container Initiative — Image Format Specification: Annotations, v1.1.1 — https://github.com/opencontainers/image-spec/blob/v1.1.1/annotations.md
- [73] GitHub — Working with the Container registry — https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- [74] GitHub — Configuring a package's access control and visibility — https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility
- [75] Docker — docker/metadata-action README, v6.2.0 — https://github.com/docker/metadata-action/blob/v6.2.0/README.md
- [76] Docker — Immutable tags on Docker Hub — https://docs.docker.com/docker-hub/repos/manage/hub-images/immutable-tags/
- [77] Amazon Web Services — Preventing image tags from being overwritten in Amazon ECR — https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-tag-mutability.html
- [78] Google Cloud — Artifact Registry: Create repositories (Immutable image tags) — https://cloud.google.com/artifact-registry/docs/repositories/create-repos
- [79] Ivan Pinatti — comment in "Immutable image tags in container registry" (GitHub Community discussion #181783, 2026; opinion) — https://github.com/orgs/community/discussions/181783
- [80] Docker — Build attestations — https://docs.docker.com/build/metadata/attestations/
- [81] Docker — Add SBOM and provenance attestations with GitHub Actions — https://docs.docker.com/build/ci/github-actions/attestations/
- [82] OpenSSF SLSA — Build: Requirements for producing artifacts, v1.2 — https://slsa.dev/spec/v1.2/build-requirements
- [83] OpenSSF SLSA — Build track: Basics, v1.2 — https://slsa.dev/spec/v1.2/build-track-basics
- [84] Sigstore — cosign README, v3.1.3 — https://github.com/sigstore/cosign/blob/v3.1.3/README.md
- [85] Notary Project — Quickstart: sign and verify an image with Notation — https://notaryproject.dev/docs/quickstart-guides/quickstart-sign-image-artifact/
- [86] Sigstore — Verifying signatures (cosign) — https://docs.sigstore.dev/cosign/verifying/verify/
- [87] Sigstore — Cosign Quickstart — https://docs.sigstore.dev/quickstart/quickstart-cosign/
- [88] Docker — Content trust in Docker — https://docs.docker.com/engine/security/trust/
- [89] Docker — Test before push with GitHub Actions — https://docs.docker.com/build/ci/github-actions/test-before-push/
- [90] Cristhian Kapelinski, Beatriz Machado and Diego Kreutz — Vulnerabilities, Secrets and Misconfiguration in the Highest-Exposure Docker Hub Images (arXiv preprint, 2026; research) — https://arxiv.org/abs/2608.02669v1
- [91] Aqua Security — Trivy releases — https://github.com/aquasecurity/trivy/releases
- [92] Anchore — Grype releases — https://github.com/anchore/grype/releases
- [93] Docker — Docker Scout CLI releases — https://github.com/docker/scout-cli/releases
- [94] Aqua Security — Trivy documentation, Filtering (`.trivyignore`), v0.76.0 — https://github.com/aquasecurity/trivy/blob/v0.76.0/docs/guide/configuration/filtering.md
- [95] GitHub — Publishing and installing a package with GitHub Actions — https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions
- [96] GitHub — actions/attest README, v4.2.2 — https://github.com/actions/attest/blob/v4.2.2/README.md
- [97] GitHub — actions/checkout README, v7.0.1 — https://github.com/actions/checkout/blob/v7.0.1/README.md
- [98] GitHub — OpenID Connect (security hardening for GitHub Actions) — https://docs.github.com/en/actions/concepts/security/openid-connect
- [99] GitHub Advisory Database — GHSA-mrrh-fwg8-r2c3, tj-actions/changed-files (CVE-2025-30066) — https://github.com/advisories/GHSA-mrrh-fwg8-r2c3
- [100] Rami McCarthy — New GitHub Action supply chain attack: reviewdog/action-setup (Wiz blog, 2025; case) — https://www.wiz.io/blog/new-github-action-supply-chain-attack-reviewdog-action-setup
- [101] Aqua Security — GHSA-69fq-xp46-6x23, Trivy supply chain compromise (CVE-2026-33634) — https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23
- [102] Aqua Security — Trivy Supply Chain Attack: What You Need to Know (Aqua blog, 2026; case) — https://www.aquasec.com/blog/trivy-supply-chain-attack-what-you-need-to-know/
- [103] Renovate — github-actions manager, digest pinning and updating, 44.164.10 — https://github.com/renovatebot/renovate/blob/44.164.10/lib/modules/manager/github-actions/readme.md
- [104] Docker — GitHub Actions cache backend — https://docs.docker.com/build/cache/backends/gha/
- [105] Docker — Cache management with GitHub Actions — https://docs.docker.com/build/ci/github-actions/cache/
- [106] Docker — Docker Hub usage and limits: pulls — https://docs.docker.com/docker-hub/usage/pulls/
- [107] Docker — Multi-platform image with GitHub Actions — https://docs.docker.com/build/ci/github-actions/multi-platform/
- [108] Astral — Using uv in Docker, uv 0.13.1 — https://github.com/astral-sh/uv/blob/0.13.1/docs/guides/integration/docker.md
- [109] Astral — uv-docker-example (`multistage.Dockerfile`, `Dockerfile`) — https://github.com/astral-sh/uv-docker-example/tree/3c23b2cd3a2baf090d52ba2a5699249ab9499808
- [110] Astral — uv CLI reference, `uv sync` — https://docs.astral.sh/uv/reference/cli/#uv-sync
- [111] Python Software Foundation — venv, Creation of virtual environments (Python 3.14) — https://docs.python.org/3.14/library/venv.html
- [112] Astral — Running commands, Signal handling, uv 0.13.1 — https://github.com/astral-sh/uv/blob/0.13.1/docs/concepts/projects/run.md
- [113] Astral — uv changelog, 0.6.15 (`changelogs/0.6.x.md`), uv 0.13.1 — https://github.com/astral-sh/uv/blob/0.13.1/changelogs/0.6.x.md
- [114] Psycopg — Installation — https://www.psycopg.org/psycopg3/docs/basic/install.html
- [115] Python Software Foundation — Command line and environment, Python 3.14 — https://docs.python.org/3.14/using/cmdline.html#envvar-PYTHONUNBUFFERED
- [116] Nils Matteson — [Docker] Compile Python bytecode at image build time (vllm-project/vllm pull request #55422, 2026; case) — https://github.com/vllm-project/vllm/pull/55422
- [117] Chiyang Huang — fix(docker): precompile bytecode so cold starts stop recompiling 11k files (dddenrose/Navi pull request #8, 2026; case) — https://github.com/dddenrose/Navi/pull/8
- [118] FastAPI — FastAPI in Containers, Docker — https://fastapi.tiangolo.com/deployment/docker/
- [119] Uvicorn — Dockerfile deployment — https://uvicorn.dev/deployment/docker/
- [120] Uvicorn — Settings — https://uvicorn.dev/settings/
- [121] Microsoft — Add a non-root user to a container (VS Code docs) — https://code.visualstudio.com/remote/advancedcontainers/add-nonroot-user
- [122] Christof Marti — reply in "updateRemoteUserUID does not update UID" (microsoft/vscode-remote-release issue #10030, 2024; opinion) — https://github.com/microsoft/vscode-remote-release/issues/10030
- [123] Red Hat — Creating images, OpenShift Container Platform 4.19 — https://docs.redhat.com/en/documentation/openshift_container_platform/4.19/html/images/creating-images
- [124] Docker — Rootless mode: UID/GID mapping — https://docs.docker.com/engine/security/rootless/uid-gid-mapping/
- [125] GitHub — Dockerfile support for GitHub Actions, `USER` — https://docs.github.com/en/actions/reference/workflows-and-actions/dockerfile-support#user
- [126] GitHub — Secure use reference (GitHub Docs) — https://docs.github.com/en/actions/reference/security/secure-use
- [127] Renovate — github-actions manager, extract.ts (the replacement template), 44.164.10 — https://github.com/renovatebot/renovate/blob/44.164.10/lib/modules/manager/github-actions/extract.ts
