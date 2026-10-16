# Example: the image of a Python service

A worked example for [images.md](images.md). It builds the image of the Acme service from
[python/language/settings-example.md](../../python/language/settings-example.md): the package
`acme` under `src/`, built with uv, whose `main()` in `src/acme/api/main.py` reads the settings
and starts uvicorn on `0.0.0.0:8000`. The files sit at the repository root, as
[file-structure.md](../file-structure/file-structure.md) section 9 places container files.

Each `sha256:...` stands for the image's multi-platform index digest: the value Renovate's pin
pull request writes (section 5 turns that on), and updates after that ([images.md](images.md)
section 4). To build before that pull request merges, fill each digest from the `Digest:` line of
`docker buildx imagetools inspect <image>:<tag>`.

**Navigation**

- [1. pyproject.toml: the entry point](#1-pyprojecttoml-the-entry-point)
- [2. .dockerignore: an allow-list](#2-dockerignore-an-allow-list)
- [3. Dockerfile](#3-dockerfile)
- [4. Build it and check it](#4-build-it-and-check-it)
- [5. renovate.json](#5-renovatejson)

## 1. pyproject.toml: the entry point

```toml
[project.scripts]
# The image's CMD runs this command; main() reads the settings before uvicorn starts
# (python.md section 5).
acme-api = "acme.api.main:main"
```

The rest of `pyproject.toml` is left out: the project table and its `[build-system]`, which uv
needs to install the package, and the tool tables of
[static-checks/setup-example.md](../../python/static-checks/setup-example.md). The project
depends on `psycopg[binary]`, which bundles libpq, so the runtime stage installs no system library
([images.md](images.md) section 11). This `pyproject.toml` names no `readme`. If yours does, add
`!README.md` to `.dockerignore`, because the build reads it.

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
| `!src`, `!pyproject.toml`, `!uv.lock` | lets in the three things the build reads; each is a literal path at the top, so BuildKit and the classic builder both include them |
| `**/.env` | keeps a settings file someone left under `src/` out of the image; [python.md](../../python/language/python.md) section 5 requires `.dockerignore` to list `.env` |
| `**/__pycache__` | keeps local bytecode out; the build compiles its own |

It is good because it fails closed at the top of the context: a new file at the root, a stray key
or a test fixture, stays out of every image until someone adds a line for it. Inside `src/`, the
`**` lines guard against the files they name.

## 3. Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.28.0@sha256:...
# check=error=true

# One Python image for both stages: a venv only works where its interpreter sits at the same
# path (images.md section 11). Renovate updates the tag and the digest together.
# The Docker Official Image, slim: most guides use it, and it is republished at least monthly;
# images.md section 4 weighs the others.
ARG PYTHON_IMAGE=python:3.13-slim-trixie@sha256:...

FROM ${PYTHON_IMAGE} AS builder
# uv runs in this stage only; the runtime stage never needs it.
COPY --from=ghcr.io/astral-sh/uv:0.13.1@sha256:... /uv /bin/uv
# Bytecode at build time: a faster start for a larger image (images.md section 11).
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0
WORKDIR /app

# Dependencies before the source, so an edit under src/ reuses this layer.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project

# The second uv sync reads both files from /app, not from a bind mount.
COPY pyproject.toml uv.lock ./
COPY src ./src
# --no-editable installs the package into the venv, so the runtime stage needs only .venv.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM ${PYTHON_IMAGE} AS runtime
# A fixed UID and GID, so file ownership is the same in every build (images.md section 6).
RUN groupadd --gid 10001 app \
 && useradd --uid 10001 --gid app --create-home app
# Owned by root: the process can read its code but cannot change it.
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
USER 10001:10001
EXPOSE 8000
# No HEALTHCHECK: the runtime that acts on a check reads its own (compose.yaml, Kubernetes probes).
# Exec form, so the server is PID 1 and receives SIGTERM; uvicorn handles it, so no init is needed.
CMD ["acme-api"]
```

| Part | Why |
|---|---|
| `# syntax=docker/dockerfile:1.28.0@sha256:...` | a fixed frontend, by its version and its digest, so neither a new release nor a moved tag can change this build without a pull request |
| `# check=error=true` | the build checks fail the build instead of printing warnings; the build CI runs is the lint gate |
| `ARG PYTHON_IMAGE=…` and both `FROM ${PYTHON_IMAGE}` | one pin for the two stages; Renovate reads an `ARG` default, Dependabot would not |
| `python:3.13-slim-trixie` | the Docker Official Image most guides use, republished at least monthly ([images.md](images.md) section 4); names the Debian release, so the tag cannot move to the next one |
| `COPY --from=ghcr.io/astral-sh/uv:0.13.1@…` | a pinned uv, copied into the builder only |
| `UV_LINK_MODE=copy`, `UV_PYTHON_DOWNLOADS=0` | uv copies files out of the cache mount instead of warning that it cannot link them, and uses the image's Python instead of downloading one |
| first `uv sync … --no-install-project` | the dependency layer, from the lock file through bind mounts; `--locked` stops the build when `uv.lock` does not match `pyproject.toml`; `--no-dev`, in both `uv sync` lines, keeps the development tools out of the runtime environment |
| second `uv sync … --no-editable` | installs `acme` itself, from `src/`, as a normal package |
| `useradd --uid 10001`, `USER 10001:10001` | a non-root process with a known number |
| `COPY --from=builder /app/.venv` without `--chown` | the code stays owned by root |
| `PATH` | `acme-api` and `python` resolve to the venv |
| `PYTHONUNBUFFERED=1` | a crash cannot swallow the last log lines; where the logs go is [logging.md](../../python/logging/logging.md) section 6 |
| `CMD ["acme-api"]` | the entry point of section 1, in exec form |

It is good because the shipped image holds Python, the venv and nothing else: no uv, no compiler,
no source tree, no file from the build context that the allow-list did not name. Every image it
pulls is pinned, it runs as a non-root user that cannot change its own code, and `docker stop`
reaches uvicorn's own SIGTERM handler.

## 4. Build it and check it

```sh
docker build --tag acme-api:dev .

# What the builder received: only src/, pyproject.toml and uv.lock (images.md section 2).
# A throwaway build: it only lists the context and is never pushed, so it has no frontend line.
printf 'FROM busybox:1.37@sha256:...\nCOPY . /ctx\nRUN find /ctx -type f\n' |
  docker build --no-cache --progress=plain -f - .

docker run --rm acme-api:dev id -u  # prints 10001
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
received, the user the process runs as, that the package and its entry point are installed, and
that the process stops on SIGTERM.

What this example does not claim: it was not built when it was written, so the build itself, the
context listing and the `docker run`, `docker stop` and `docker inspect` lines are untested here;
the `sha256:...` digests are placeholders until Renovate or the command above fills them; uv
0.13.1 and frontend 1.28.0 were the latest releases in October 2026.

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
  ]
}
```

| Preset | What it adds |
|---|---|
| `config:recommended` | Renovate's recommended base; on its own it pins no digest |
| `docker:pinDigests` | pins every image Renovate reads in a Dockerfile to its digest |
| `helpers:pinGitHubActionDigests` | pins each action in a workflow to a commit SHA, as [ci-example.md](ci-example.md) shows |
| `customManagers:dockerfileVersions` | updates an `ARG` or `ENV` whose name ends in `_VERSION` when a `# renovate: datasource=… depName=…` comment sits on the line above it, as for Claude Code in [agent-container-example.md](agent-container-example.md) section 3 |

It is good because every pin in these examples gets a pull request that moves it. Renovate pins no
digest by default, and a pin nobody moves "opts you out of automated security fixes"
([images.md](images.md) section 4).

The file does nothing until the Renovate app or a Renovate runner is enabled for the repository;
the Dependency Dashboard issue, which `config:recommended` turns on, shows that it runs.
