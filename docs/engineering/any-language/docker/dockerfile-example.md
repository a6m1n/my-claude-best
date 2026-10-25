# Example: the image of a Python service

A worked example for [images.md](images.md). It builds the image of the Acme service from
[python/language/settings-example.md](../../python/language/settings-example.md): the package
`acme` under `src/`, built with uv, whose `main()` in `src/acme/api/main.py` reads the settings
and starts uvicorn on `0.0.0.0:8000`. The files sit at the repository root, as
[file-structure.md](../file-structure/file-structure.md) section 9 places container files.

Each `sha256:...` stands for the image's multi-platform index digest: the value Renovate's pin
pull request writes (section 5 turns that on), and updates after that ([images.md](images.md)
section 4) [1]. To build before that pull request merges, fill each digest from the `Digest:` line
of `docker buildx imagetools inspect <image>:<tag>` [2].

**Navigation**

- [1. pyproject.toml: the entry point](#1-pyprojecttoml-the-entry-point)
- [2. .dockerignore: an allow-list](#2-dockerignore-an-allow-list)
- [3. Dockerfile](#3-dockerfile)
- [4. Build it and check it](#4-build-it-and-check-it)
- [5. renovate.json](#5-renovatejson)
- [6. Sources](#6-sources)

## 1. pyproject.toml: the entry point

```toml
[project.scripts]
# The image's CMD runs this command; main() reads the settings before uvicorn starts
# (python.md section 5).
acme-api = "acme.api.main:main"
```

The rest of `pyproject.toml` is left out: the project table and its `[build-system]`, which uv
needs to install the package, and the tool tables of
[static-checks/setup-example.md](../../python/static-checks/setup-example.md) [3]. Its
`requires-python` is `"==3.13.*"` and `.python-version` holds `3.13`, the minor the image tag in
section 3 names ([ci-cd/pipeline.md](../ci-cd/pipeline.md) section 9). The project
depends on `psycopg[binary]`, which bundles libpq, so the runtime stage installs no system library
([images.md](images.md) section 11) [4]. This `pyproject.toml` names no `readme`. If yours does,
add `!README.md` to `.dockerignore`, because the build reads it [5].

It is good because the image starts the process the same way a person does: through `main()`,
which builds `Settings` first, so a container with a missing setting stops at once with one error.

## 2. .dockerignore: an allow-list

```text
*
# An allow-list: the builder receives only what the build reads (images.md section 2).
!src
!pyproject.toml
!uv.lock
# Excluded again inside src/: the last matching line wins over !src.
**/.env
**/__pycache__
```

| Line | What it does |
|---|---|
| `*` | leaves the whole folder out: `.git`, `.venv`, `.env`, tests, notes, an agent's `.claude/` |
| `!src`, `!pyproject.toml`, `!uv.lock` | lets in the three things the build reads; each is a literal path at the top, so BuildKit and the classic builder both include them [6], [7] |
| `**/.env` | keeps a settings file someone left under `src/` out of the image; [python.md](../../python/language/python.md) section 5 requires `.dockerignore` to list `.env` |
| `**/__pycache__` | keeps local bytecode out; the build compiles its own |

It is good because it fails closed at the top of the context: a new file at the root, a stray key
or a test fixture, stays out of every image until someone adds a line for it. Inside `src/`, the
`**` lines guard against the files they name.

## 3. Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.28.0@sha256:...
# check=error=true

# The two lines above pin the frontend by its version and digest, so a new release cannot change
# this build without a pull request, and make a build check fail the build instead of warning, so
# the build CI runs is the lint gate (images.md section 7).
# One Python image for both stages: a venv only works where its interpreter sits at the same
# path (images.md section 11). Renovate updates the tag and the digest together.
# The Docker Official Image, slim, which its maintainers strive to republish at least monthly;
# images.md section 4 weighs the others.
# 3.13 is the one minor requires-python allows: on another minor the first uv sync stops the
# build (images.md section 11), so it moves only with .python-version, requires-python and
# uv.lock (ci-cd/pipeline.md section 9).
ARG PYTHON_IMAGE=python:3.13-slim-trixie@sha256:...

FROM ${PYTHON_IMAGE} AS builder
# uv runs in this stage only; the runtime stage never needs it.
COPY --from=ghcr.io/astral-sh/uv:0.13.1@sha256:... /uv /bin/uv
# Bytecode at build time: a faster start for a larger image (images.md section 11).
# UV_LINK_MODE=copy copies files out of the cache mount instead of warning that it cannot link
# them; UV_PYTHON_DOWNLOADS=0 makes uv use the image's Python, never a downloaded one.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0
WORKDIR /app

# Dependencies before the source, so an edit under src/ reuses this layer. --locked stops the
# build when uv.lock does not match pyproject.toml (images.md section 11).
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project

# The second uv sync reads both files from /app, not from a bind mount.
COPY pyproject.toml uv.lock ./
COPY src ./src
# --no-editable installs the package into the venv, so the runtime stage needs only .venv
# (images.md section 11).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM ${PYTHON_IMAGE} AS runtime
# A fixed UID and GID, so file ownership is the same in every build (images.md section 6).
RUN groupadd --gid 10001 app \
 && useradd --uid 10001 --gid app --create-home app
# Owned by root: the process can read its code but cannot change it (images.md section 6).
COPY --from=builder /app/.venv /app/.venv
# The venv's Python comes first on PATH; PYTHONUNBUFFERED=1 means a crash cannot swallow the last
# log lines (images.md section 11).
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
USER 10001:10001
EXPOSE 8000
# No HEALTHCHECK (images.md section 6): Compose and Kubernetes read their own checks, and this
# image is not published for others to run with plain Docker; add one if you publish it.
# Exec form, so the server is PID 1 and receives SIGTERM; uvicorn handles it, so no init is
# needed (images.md section 6).
CMD ["acme-api"]
```

| Part | Why |
|---|---|
| `# syntax=docker/dockerfile:1.28.0@sha256:...` | a fixed frontend, by its version and its digest, so neither a new release nor a moved tag can change this build without a pull request [8] |
| `# check=error=true` | the build checks fail the build instead of printing warnings; the build CI runs is the lint gate [9] |
| `ARG PYTHON_IMAGE=…` and both `FROM ${PYTHON_IMAGE}` | one pin for the two stages; Renovate reads an `ARG` default, Dependabot would not [10], [11] |
| `python:3.13-slim-trixie` | the Docker Official Image, which its maintainers strive to republish at least monthly ([images.md](images.md) section 4) [12]; names the Debian release, so the tag cannot move to the next one [13]; names the one minor `requires-python` allows, so an image on another minor fails the first `uv sync`, which uses an interpreter only when it fits that range ([images.md](images.md) section 11) [28] |
| `COPY --from=ghcr.io/astral-sh/uv:0.13.1@…` | a pinned uv, copied into the builder only [14] |
| `UV_LINK_MODE=copy`, `UV_PYTHON_DOWNLOADS=0` | uv copies files out of the cache mount instead of warning that it cannot link them, and uses the image's Python instead of downloading one [14] |
| first `uv sync … --no-install-project` | the dependency layer, from the lock file through bind mounts; `--locked` stops the build when `uv.lock` does not match `pyproject.toml`; `--no-dev`, in both `uv sync` lines, keeps the development tools out of the runtime environment [15] |
| second `uv sync … --no-editable` | installs `acme` itself, from `src/`, as a normal package [14] |
| `useradd --uid 10001`, `USER 10001:10001` | a non-root process with a known number |
| `COPY --from=builder /app/.venv` without `--chown` | the code stays owned by root [16], so the process cannot change it (images.md section 6) |
| `PATH` | `acme-api` and `python` resolve to the venv |
| `PYTHONUNBUFFERED=1` | a crash cannot swallow the last log lines [17], [18]; where the logs go is [logging.md](../../python/logging/logging.md) section 6 |
| `CMD ["acme-api"]` | the entry point of section 1, in exec form |

It is good because the shipped image holds Python, the venv and nothing else: no uv, no compiler,
no source tree, no file from the build context that the allow-list did not name. Every image it
pulls is pinned, it runs as a non-root user that cannot change its own code, and `docker stop`
reaches uvicorn's own SIGTERM handler [19].

## 4. Build it and check it

```sh
docker build --tag acme-api:dev .

# What the builder received: only src/, pyproject.toml and uv.lock (images.md section 2).
# A throwaway build: it only lists the context and is never pushed, so it has no frontend line.
printf 'FROM busybox:1.37@sha256:...\nCOPY . /ctx\nRUN find /ctx -type f\n' |
  docker build --no-cache --progress=plain -f - .

# On an image of another Python minor the build stops at the first uv sync, because
# requires-python allows 3.13 only (images.md section 11). A throwaway tag, never pushed.
docker build --build-arg PYTHON_IMAGE=python:3.14-slim-trixie@sha256:... --tag acme-api:other-python .  # fails: no interpreter for ==3.13.*

docker run --rm acme-api:dev id -u  # prints 10001
docker run --rm acme-api:dev stat -c '%u' /app/.venv  # prints 0: root owns the venv (images.md section 6)
# The package imports from the venv, and the entry point is on PATH.
docker run --rm acme-api:dev python -c "import acme.api.main, acme.api.app"
docker run --rm acme-api:dev sh -c 'command -v acme-api'

# It stops cleanly: dummy values are enough, because the app connects to nothing at start; it
# does load the database driver, which this check therefore covers.
docker run --detach --name acme-stop-check \
  --env ACME_DATABASE_HOST=db --env ACME_DATABASE_NAME=acme --env ACME_DATABASE_USER=acme \
  --env ACME_DATABASE_PASSWORD=dummy --env ACME_PAYMENTS_API_KEY=dummy acme-api:dev
# Still running a few seconds later: it started and did not crash.
sleep 5
docker inspect --format '{{.State.Running}}' acme-stop-check  # prints true
docker stop acme-stop-check
# 0 is a clean shutdown on SIGTERM; 137 means it was killed, 1 means it crashed
# (images.md section 6).
docker inspect --format '{{.State.ExitCode}}' acme-stop-check  # prints 0
docker rm acme-stop-check
```

It is good because each line checks the image itself, not the Dockerfile: what the builder
received, that an image of another Python cannot be built, the user the process runs as, that the
package and its entry point are installed, and that the process stops on SIGTERM.

What this example does not claim: it was not built when it was written, so the build itself, the
context listing, the build on another Python minor and the `docker run`, `docker stop` and
`docker inspect` lines are untested here; that last build's failure rests on how uv picks an
interpreter [28], not on a run of this Dockerfile;
the `sha256:...` digests are placeholders until Renovate or the command above fills them; uv
0.13.1 and frontend 1.28.0 were the latest releases in October 2026 [20], [21].

## 5. renovate.json

`renovate.json`, at the repository root

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:recommended",
    "docker:pinDigests",
    "helpers:pinGitHubActionDigests",
    "customManagers:dockerfileVersions"
  ],
  "packageRules": [
    {
      "description": "One pull request for the Python minor: the image tags and .python-version; requires-python and uv.lock by hand when Renovate leaves them",
      "matchDatasources": ["docker", "python-version"],
      "matchPackageNames": ["/(?:^|/)python$/"],
      "matchUpdateTypes": ["major", "minor"],
      "groupName": "Python minor",
      "prBodyNotes": [
        "If uv sync fails here, set requires-python to the new minor and run uv lock in this branch. uv's hint to run uv python pin would undo this update. See ci-cd/pipeline.md section 9."
      ]
    }
  ]
}
```

| Preset | What it adds |
|---|---|
| `config:recommended` | Renovate's recommended base; on its own it pins no digest [22], [23] |
| `docker:pinDigests` | pins every image Renovate reads in a Dockerfile to its digest [24] |
| `helpers:pinGitHubActionDigests` | pins each action in a workflow to a commit SHA, as [ci-example.md](ci-example.md) shows [25] |
| `customManagers:dockerfileVersions` | updates an `ARG` or `ENV` whose name ends in `_VERSION` when a `# renovate: datasource=… depName=…` comment sits on the line above it, as for Claude Code in [agent-container-example.md](agent-container-example.md) section 3 [26] |
| the `packageRules` group | moves the Python minor in one pull request, as [ci-cd/pipeline.md](../ci-cd/pipeline.md) section 9 asks: the `python` image tags, the agent image's in [agent-container-example.md](agent-container-example.md) too; `.python-version`, which the pyenv manager updates from the same Docker Hub tags [29]; and `requires-python`, which the pep621 manager reads as `python` from the `python-version` datasource [31], though whether it raises `"==3.13.*"` was not run (see below). `matchUpdateTypes` keeps digest refreshes out of the group, so a pending minor move never holds back the image rebuild [images.md](images.md) section 4 asks for [32]. The regular-expression name also catches the image behind a registry prefix, the way Renovate's own `group:nodeJs` does for Node [30] |
| `prBodyNotes` | writes the next step into the pull request's description [32], so whoever finds the pull request red knows what to do. uv's own error asks for `uv python pin` [33], which would set `.python-version` back to the old minor and undo the update |

It is good because each preset keeps one kind of pin moving with a pull request: image digests in
the Dockerfile, action SHAs in the workflows, and `_VERSION` values under a `# renovate:`
comment, and the group keeps the files of the Python minor in one change. Whether Renovate also
raises `requires-python` and relocks `uv.lock` in that pull request was not run here; when it
does not, the pull request fails `uv sync` until someone does both in that branch
([ci-cd/pipeline.md](../ci-cd/pipeline.md) section 9).
A pin of another kind, such as a scanner's `version:` input in a workflow or a tool a step
downloads, gets no pull request and is moved by hand. Renovate pins no
digest by default [23], and Docker warns that a digest pin means you update by hand, and that
"you're opting out of automated security fixes" ([images.md](images.md) section 4) [27].

The file does nothing until the Renovate app or a Renovate runner is enabled for the repository;
the Dependency Dashboard issue, which `config:recommended` turns on, shows that it runs [22]. The
`packageRules` group was not run against Renovate; it follows the idea of `group:nodeJs` [30].

## 6. Sources

Checked 2026-10-16 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Renovate — Docker datasource, `lib/modules/datasource/docker/index.ts` (`getDigest`), 44.164.10 — https://github.com/renovatebot/renovate/blob/44.164.10/lib/modules/datasource/docker/index.ts
- [2] Docker — docker buildx imagetools inspect (CLI reference) — https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/
- [3] Astral — Configuring projects, Build systems, uv 0.13.1 — https://github.com/astral-sh/uv/blob/0.13.1/docs/concepts/projects/config.md
- [4] Psycopg — Installation — https://www.psycopg.org/psycopg3/docs/basic/install.html
- [5] Python Packaging Authority — pyproject.toml specification, `readme` — https://packaging.python.org/en/latest/specifications/pyproject-toml/#readme
- [6] Tõnis Tiigi — fsutil `filter.go`, the build-context filter BuildKit uses — https://github.com/tonistiigi/fsutil/blob/468ba298314d055d18a6887781b2517dfc6ec9e0/filter.go
- [7] Moby project — go-archive `archive.go`, which the Docker CLI's classic build path uses to pack the context — https://github.com/moby/go-archive/blob/66cf06fd9d1f416faec05a3ed241b702e8941a85/archive.go
- [8] Docker — Custom Dockerfile syntax (BuildKit frontend) — https://docs.docker.com/build/buildkit/frontend/
- [9] Docker — Checking your build configuration (build checks) — https://docs.docker.com/build/checks/
- [10] Renovate — Dockerfile manager, 44.164.10 — https://github.com/renovatebot/renovate/blob/44.164.10/lib/modules/manager/dockerfile/readme.md
- [11] GitHub — Guidance for the configuration of private registries for Dependabot — https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/configure-private-registries
- [12] Docker Official Images — FAQ — https://github.com/docker-library/faq
- [13] Docker Official Images — python (Docker Hub page) — https://hub.docker.com/_/python
- [14] Astral — Using uv in Docker, uv 0.13.1 — https://github.com/astral-sh/uv/blob/0.13.1/docs/guides/integration/docker.md
- [15] Astral — uv CLI reference, `uv sync` — https://docs.astral.sh/uv/reference/cli/#uv-sync
- [16] Docker — Dockerfile reference (BuildKit `frontend/dockerfile/docs/reference.md`) — https://github.com/moby/buildkit/blob/f74a37c4c978e3d01a04540b39039442456d9c4c/frontend/dockerfile/docs/reference.md
- [17] Astral — uv-docker-example (`multistage.Dockerfile`, `Dockerfile`) — https://github.com/astral-sh/uv-docker-example/tree/3c23b2cd3a2baf090d52ba2a5699249ab9499808
- [18] Python Software Foundation — Command line and environment, Python 3.14 — https://docs.python.org/3.14/using/cmdline.html#envvar-PYTHONUNBUFFERED
- [19] Uvicorn — `uvicorn/server.py`, the signal handlers — https://github.com/Kludex/uvicorn/blob/528a3ac5031bf777ccd966d74db3034fe99fd69c/uvicorn/server.py
- [20] Astral — uv releases — https://github.com/astral-sh/uv/releases
- [21] Moby BuildKit — releases (`dockerfile/1.28.0`) — https://github.com/moby/buildkit/releases/tag/dockerfile%2F1.28.0
- [22] Renovate — Full config presets: `config:recommended` — https://docs.renovatebot.com/presets-config/#configrecommended
- [23] Renovate — Configuration options: `pinDigests` — https://docs.renovatebot.com/configuration-options/#pindigests
- [24] Renovate — Docker presets: `docker:pinDigests` — https://docs.renovatebot.com/presets-docker/#dockerpindigests
- [25] Renovate — Helper presets: `helpers:pinGitHubActionDigests` — https://docs.renovatebot.com/presets-helpers/#helperspingithubactiondigests
- [26] Renovate — Custom managers presets: `customManagers:dockerfileVersions` — https://docs.renovatebot.com/presets-customManagers/#custommanagersdockerfileversions
- [27] Docker — Building best practices — https://docs.docker.com/build/building/best-practices/
- [28] Astral — uv: Python versions (`docs/concepts/python-versions.md`), commit 4954c25 — https://github.com/astral-sh/uv/blob/4954c25a16b246c1b88aef6c3798a76d675c5cd0/docs/concepts/python-versions.md
- [29] Renovate — pyenv manager (`lib/modules/manager/pyenv/index.ts`), commit bd8f755 — https://github.com/renovatebot/renovate/blob/bd8f755bc1dd6f5f8ae8ff5ebd661835fcc15aa5/lib/modules/manager/pyenv/index.ts
- [30] Renovate — Group presets (`lib/config/presets/internal/group.preset.ts`, `nodeJs`), commit bd8f755 — https://github.com/renovatebot/renovate/blob/bd8f755bc1dd6f5f8ae8ff5ebd661835fcc15aa5/lib/config/presets/internal/group.preset.ts
- [31] Renovate — pep621 manager (`lib/modules/manager/pep621/extract.ts`), commit bd8f755 — https://github.com/renovatebot/renovate/blob/bd8f755bc1dd6f5f8ae8ff5ebd661835fcc15aa5/lib/modules/manager/pep621/extract.ts
- [32] Renovate — Configuration options (`docs/usage/configuration-options.md`: `prBodyNotes`, `packageRules.matchUpdateTypes` and the update types), commit bd8f755 — https://github.com/renovatebot/renovate/blob/bd8f755bc1dd6f5f8ae8ff5ebd661835fcc15aa5/docs/usage/configuration-options.md
- [33] Astral — uv: the `uv sync` tests (`crates/uv/tests/sync/sync.rs`, `sync_python_version`), commit 4954c25 — https://github.com/astral-sh/uv/blob/4954c25a16b246c1b88aef6c3798a76d675c5cd0/crates/uv/tests/sync/sync.rs
