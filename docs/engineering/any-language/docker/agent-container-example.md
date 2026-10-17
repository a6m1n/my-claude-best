# Example: a container where a coding agent runs without approvals

A worked example for [agent-containers.md](agent-containers.md). It is the second row of that
file's section 3: a repository you trust, and Claude Code running without approvals. The agent
gets no host credential, reaches the network only through an allowlisting proxy, and works in a
clone of its own. The repository is the Acme service of
[dockerfile-example.md](dockerfile-example.md). The files below sit in the `.devcontainer/agent/`
folder of your own repository, and the agent's container mounts a separate clone, never this
folder, because the host reads these files each time it starts the container. They stay out of
`.devcontainer/` itself: the default path is kept free for a person's own dev container (row 1 of
that section 3), which this file does not show. The Dev Container reference asks tools to consider
offering a choice among the configurations under `.devcontainer/` [1]. In Reopen in Container,
pick row 1's, never this one ([agent-containers.md](agent-containers.md) section 9).

Each `sha256:...` stands for the image's index digest, as in
[dockerfile-example.md](dockerfile-example.md). The paths `~/work/acme` and `~/agent-sessions`
are placeholders for your own folders.

**Navigation**

- [1. devcontainer.json](#1-devcontainerjson)
- [2. compose.yaml](#2-composeyaml)
- [3. The agent's image](#3-the-agents-image)
- [4. The proxy](#4-the-proxy)
- [5. Run it, and take the work back](#5-run-it-and-take-the-work-back)
- [6. Sources](#6-sources)

## 1. devcontainer.json

`.devcontainer/agent/devcontainer.json`

```jsonc
{
  // Row 2 of agent-containers.md section 3: a repository you trust, the agent runs
  // without approvals.
  "name": "acme-agent",
  // The containers and their network live in compose.yaml; this file only points at them.
  "dockerComposeFile": "compose.yaml",
  "service": "agent",
  "workspaceFolder": "/workspace",
  // Clears the variables an attached IDE would set; its forwarded sockets stay
  // (agent-containers.md section 9), so attach none.
  "remoteEnv": { "SSH_AUTH_SOCK": "", "GPG_AGENT_INFO": "" }
}
```

It is good because it holds nothing that runs on your host: no `initializeCommand`, no Features
that could add privileges the file does not show ([agent-containers.md](agent-containers.md)
section 9). The agent's tools come from its own image instead. The agent cannot change this file
either, because its folder is never mounted into the agent's container.

## 2. compose.yaml

`.devcontainer/agent/compose.yaml`

```yaml
services:
  agent:
    build: .
    # Keeps the container up for docker compose exec: with a Compose file the image's own
    # command runs, and python3 exits at once.
    command: ["sleep", "infinity"]
    init: true  # reaps the git processes the agent leaves behind (agent-containers.md section 6)
    # The proxy is its only way out; the host's gateway stays reachable (agent-containers.md
    # section 5).
    networks: [sandbox]
    depends_on:
      proxy:
        condition: service_healthy  # start once the proxy answers, not once it runs
    environment:
      HTTPS_PROXY: http://proxy:3128
      HTTP_PROXY: http://proxy:3128
      # A key made for this agent alone, in a workspace with a spend limit. A departure from compose.md
      # section 4 and agent-containers.md section 4: the agent could read the key from a file
      # just as well. Anthropic's secure-deployment guide recommends a gateway that adds the key
      # outside the container (set as ANTHROPIC_BASE_URL); this example leaves it out to stay at
      # two services, because a gateway is a third service that holds the key and needs its own
      # pinned image. Squid cannot do it, since it does not terminate TLS. The cost: the key
      # sits in the container's environment, where docker inspect and every process the agent
      # starts can see it.
      ANTHROPIC_API_KEY: ${AGENT_ANTHROPIC_API_KEY:?export a key made for this agent}
      # The default path, set anyway: it keeps the login in the volume across rebuilds
      # (agent-containers.md section 9).
      CLAUDE_CONFIG_DIR: /home/agent/.claude
      DISABLE_AUTOUPDATER: "1"  # the version in the image is the one you chose
      DISABLE_TELEMETRY: "1"
      DISABLE_ERROR_REPORTING: "1"
    volumes:
      # The agent's own clone, never your repository and never this folder, which the host reads
      # at every start (agent-containers.md section 9).
      - type: bind
        source: ${AGENT_WORKSPACE:?set it to the agent's clone}
        target: /workspace
        bind:
          create_host_path: false  # a wrong path fails instead of creating an empty folder (compose-keys.md section 4)
      # The agent's settings and session data; count the volume as a secret.
      - claude-config:/home/agent/.claude
    cap_drop: [ALL]  # the agent cannot change its own network rules (agent-containers.md section 6)
    security_opt: [no-new-privileges:true]  # no process gains privileges (agent-containers.md section 6)
    # A runaway process fails here instead of stalling the host (agent-containers.md section 6).
    pids_limit: 1024
    mem_limit: 4g
    cpus: 2

  proxy:
    build:
      dockerfile: proxy.Dockerfile
    networks: [sandbox, egress]  # the only service on both networks
    # Not every key of compose.md section 7 (section 10): Squid starts as root and switches
    # to its own user, which needs root powers. The cost: Docker's default capabilities stay,
    # including ones it never uses, such as NET_RAW; a build that lists what Squid uses can keep
    # only those with cap_drop: [ALL] and cap_add.
    security_opt: [no-new-privileges:true]
    pids_limit: 100  # a fork loop stops here, not on the host (compose.md section 7)
    healthcheck:
      test: ["CMD", "squid", "-k", "check"]  # asks the running Squid whether it is up
      interval: 5s
      timeout: 3s
      retries: 10

networks:
  sandbox:
    # No route to the outside; the host's gateway stays reachable (agent-containers.md section 5).
    internal: true
  egress: {}

volumes:
  claude-config:
```

| Part | Why |
|---|---|
| `networks: [sandbox]` with `internal: true` | the agent's container has no route out [2]; a tool that ignores `HTTPS_PROXY` fails instead of going around the proxy. The host's gateway stays reachable, so host services the agent must not reach listen on `127.0.0.1` only ([agent-containers.md](agent-containers.md) section 5) [3] |
| `proxy` on `sandbox` and `egress` | one way out, which reads the allowlist of section 4 |
| `command: ["sleep", "infinity"]` | keeps the container up for `docker compose exec`: with a Compose file the image's own command runs, and here that is `python3` [4], [5]. With no input, `python3` exits at once [25] |
| `depends_on` the `proxy` with `service_healthy`, and the proxy's `healthcheck` | the agent starts once Squid answers, so its first request does not fail ([compose.md](compose.md) section 3) [6] |
| no mount of `~/.ssh`, `~/.gitconfig`, `~/.aws` or the Docker socket | the container holds no host credential and cannot drive the host's Docker |
| `ANTHROPIC_API_KEY` from `AGENT_ANTHROPIC_API_KEY` | a declared departure: a key you can revoke alone, in the environment because this example leaves out the gateway Anthropic's guide recommends (`ANTHROPIC_BASE_URL`) [7], a third service that holds the key and needs its own pinned image, and Squid cannot add the key, since it does not terminate TLS; there `docker inspect` and every process the agent starts can see it |
| `init: true`, `pids_limit`, `mem_limit`, `cpus` | zombie processes are reaped, and a runaway process fails instead of stalling the host [8] |
| `cap_drop: [ALL]`, `no-new-privileges` | the agent cannot change its own network rules or gain privileges |
| `DISABLE_AUTOUPDATER`, `DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING` | the agent stays at the version in the image [10], and the two Datadog hosts are switched off [9] |
| the project name, from `COMPOSE_PROJECT_NAME` set once per session (section 5) | the `devcontainer` tool and Compose both read it, so each session gets its own containers and networks; section 5 reaches them with `docker compose -p`, never `devcontainer exec`, which picks a container by labels two sessions share [11], [12] |
| the `claude-config` volume | Compose names a volume after its project (`<session>_claude-config`), so each session gets its own, and `docker compose down --volumes` removes it with the session [13], [14] |

It is good because the agent can damage only its own clone and leak only what is inside the
container: its own key and that clone. Everything else is out of its reach, or behind a list you
wrote.

## 3. The agent's image

`.devcontainer/agent/Dockerfile`

```dockerfile
# syntax=docker/dockerfile:1.28.0@sha256:...
# check=error=true

# The check line above makes a build check fail the build instead of warning (images.md
# section 7).
# An image the agent works in: one stage, its tools included (images.md section 12).
# The project's own Python image, so the agent runs the code the way the service does.
ARG PYTHON_IMAGE=python:3.13-slim-trixie@sha256:...
FROM ${PYTHON_IMAGE}

# Debian's images delete downloaded packages; keep them for the cache mount below.
RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
# Cache mounts speed up the local builds devcontainer up runs (images.md section 3).
# Debian's Node.js 20 is below the npm package's floor of 22: npm warns (EBADENGINE) and installs
# (agent-containers.md section 9).
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
 && apt-get install --yes --no-install-recommends git nodejs npm

# After the apt step: a changed ARG rebuilds every RUN after it (images.md section 3).
# A fixed release of the agent, not the latest one; Renovate moves it, through
# dockerfile-example.md section 5.
# renovate: datasource=npm depName=@anthropic-ai/claude-code
ARG CLAUDE_CODE_VERSION=2.1.301
RUN --mount=type=cache,target=/root/.npm \
    npm install --global "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}"
COPY --from=ghcr.io/astral-sh/uv:0.13.1@sha256:... /uv /bin/uv

# UID 1000 matches the usual first user of a Linux host, so the files the agent writes in the
# bind-mounted clone belong to you (images.md section 12); set it to your own UID. That is also
# why you never run git in the agent's clone on your host (agent-containers.md section 7).
# The last line makes the folder the claude-config volume mounts on, owned by the agent, as
# Anthropic's reference dev container does.
RUN groupadd --gid 1000 agent \
 && useradd --uid 1000 --gid agent --create-home agent \
 && install --directory --owner agent --group agent /home/agent/.claude
# No sudo, no NET_ADMIN: the agent cannot change the rules that confine it.
USER agent
# docker compose exec and claude start in the clone, so git and the agent find it
# (dockerfile-instructions.md section 3).
WORKDIR /workspace
```

It is good because the agent's version is fixed in the image, the agent runs as a user who owns
nothing outside its home and the clone, and the image installs no tool that could open a way past
the proxy. Debian's Docker Official Image is built from debuerreotype's artifacts [20], and
debuerreotype writes an APT configuration, `docker-clean`, that deletes downloaded packages after
every `dpkg` run [21]. Debian trixie packages Node.js 20 [22], below the Node.js floor of the npm
package that [agent-containers.md](agent-containers.md) section 9 gives.

## 4. The proxy

`.devcontainer/agent/proxy.Dockerfile`

```dockerfile
# syntax=docker/dockerfile:1.28.0@sha256:...
# check=error=true

# The check line above makes a build check fail the build instead of warning (images.md
# section 7).
# A departure from images.md section 3: Squid comes as a Debian package, so there is no build
# output to move into a second stage, and apt's lists stay in the cache mount, out of the layer.
# The cost: apt and dpkg stay in the image.
FROM debian:trixie-slim@sha256:...
# Debian's images delete downloaded packages; keep them for the cache mount below.
RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
 && apt-get install --yes --no-install-recommends squid
COPY squid.conf /etc/squid/squid.conf
# The port the agent's HTTPS_PROXY and HTTP_PROXY point at (dockerfile-instructions.md section 3).
EXPOSE 3128
# No USER line, a departure from images.md section 6: Squid starts as root and switches to its
# own "proxy" user itself. The cost: the container starts as root, and Squid reads its
# configuration before it switches; a docker exec into this container runs as root unless it
# names a user. Squid keeps root as its saved user ID so it can switch back, so a flaw in its
# request handling can act as root in this container.
# -N keeps Squid in the foreground as the container's process; without it Squid moves to the
# background and the container exits.
CMD ["squid", "-N", "-f", "/etc/squid/squid.conf"]
```

It is good because its one base image is pinned by digest, apt updates and installs in one `RUN`
whose lists stay in a cache mount, out of the layer, and each departure from images.md is stated
at its line, with its cost. Squid gives up root with `setresuid`, keeping 0 as its saved user ID,
and takes root back when it needs it [24].

`.devcontainer/agent/.dockerignore`

```text
*
# An allow-list (images.md section 2): the proxy image copies squid.conf; the agent image copies nothing.
!squid.conf
```

It is good because both images read one context and the list lets in only the one file a build
copies, so a `.env` beside `compose.yaml` never reaches a builder. Docker reads the Dockerfiles
themselves whatever this file says [15].

`.devcontainer/agent/squid.conf`

```text
# Only the hosts this agent's work needs (agent-containers.md section 5).
# -n: no reverse lookup, so a request to a bare IP address never matches.
# The Claude API, from Claude Code's network access requirements:
acl allowed_hosts dstdomain -n api.anthropic.com
# The package index the project installs from:
acl allowed_hosts dstdomain -n pypi.org files.pythonhosted.org

# CONNECT only to port 443, even to an allowed host: no tunnel to another port.
acl SSL_ports port 443
acl CONNECT method CONNECT

http_access deny CONNECT !SSL_ports
http_access allow allowed_hosts
http_access deny all

# Squid waits 30 s after SIGTERM by default; Docker kills it after 10 s
# (compose-keys.md section 4, stop_grace_period). Its one client stops with it.
shutdown_lifetime 1 seconds
http_port 3128
cache deny all
# Allowed and denied requests go to a file the proxy user owns; Squid drops root before it
# opens the log, so it cannot write to stdout. Read it with:
# docker compose -p "$COMPOSE_PROJECT_NAME" exec proxy tail /var/log/squid/access.log
access_log stdio:/var/log/squid/access.log
```

It is good because the list is short and each host carries its reason: the agent's own API and
the one package index. GitHub, paste sites and wildcard domains are left out, so the agent cannot
push code or post data there. The proxy resolves every outside name. The agent's container uses
Docker's embedded DNS only to find `proxy`. On an internal network that resolver once forwarded
other names too [16]; [agent-containers.md](agent-containers.md) section 5 names the Docker releases
that leak. Squid waits `shutdown_lifetime`, 30 seconds by default, after SIGTERM [26], longer than
the 10 seconds Compose waits before it kills ([compose-keys.md](compose-keys.md) section 4), so the
file sets 1 second.

## 5. Run it, and take the work back

```sh
session=acme-agent-$(date +%Y%m%d-%H%M%S)   # one name for everything this session makes
branch=feat/agent-task                      # git.md section 2's form; name it after the task

# One session, one fresh clone that shares no file with your repository (agent-containers.md
# section 7). For newer commits, end the session and clone again.
# The clone sits outside every folder an editor has open (agent-containers.md section 7).
# --branch main: the agent's branch is cut from main, whatever your checkout is on (git.md
# section 2).
git clone --no-local --branch main ~/work/acme ~/agent-sessions/$session
# Its identity and branch, set by you before the agent first runs (git.md section 8).
git -C ~/agent-sessions/$session config user.name "Acme Agent"
git -C ~/agent-sessions/$session config user.email agent@example.com
git -C ~/agent-sessions/$session switch --create "$branch"

export AGENT_WORKSPACE="$HOME/agent-sessions/$session"
export COMPOSE_PROJECT_NAME="$session"   # one name per session: its own containers and volume
export AGENT_ANTHROPIC_API_KEY=...       # a key from the agent workspace, which has a spend limit
cfg=~/work/acme/.devcontainer/agent/devcontainer.json

# Prints nothing: no volume from an earlier session.
docker volume ls -q --filter label=com.docker.compose.project="$COMPOSE_PROJECT_NAME"

# Read what will start, then start it from your own repository, never from the agent's clone.
devcontainer read-configuration --workspace-folder ~/work/acme --config "$cfg" \
  --include-merged-configuration
devcontainer up --workspace-folder ~/work/acme --config "$cfg"

# Each check that must print nothing sits next to one that must print something.
# The mounts: the clone and the volume only.
docker inspect "$(docker compose -p "$COMPOSE_PROJECT_NAME" ps -q agent)" \
  --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}'
# docker compose -p picks this session's container; devcontainer exec picks one by labels
# that two sessions with the same --workspace-folder and --config share.
docker compose -p "$COMPOSE_PROJECT_NAME" exec agent \
  git config --show-origin --get-all credential.helper   # prints nothing
docker compose -p "$COMPOSE_PROJECT_NAME" exec agent \
  getent hosts proxy        # an address
docker compose -p "$COMPOSE_PROJECT_NAME" exec agent \
  getent hosts example.com  # nothing
docker compose -p "$COMPOSE_PROJECT_NAME" exec agent python3 -c \
  "import urllib.request; urllib.request.urlopen('https://example.com', timeout=5)"  # fails: 403
docker compose -p "$COMPOSE_PROJECT_NAME" exec agent python3 -c \
  "import socket; socket.create_connection(('1.1.1.1', 443), timeout=5)"  # fails: no route out

# This container is the boundary, so the agent may run without approvals here.
# Ask it to commit its work on the branch $branch.
docker compose -p "$COMPOSE_PROJECT_NAME" exec agent \
  claude --dangerously-skip-permissions

# Nothing left behind: the bundle carries only commits on $branch.
docker compose -p "$COMPOSE_PROJECT_NAME" exec agent \
  git status --porcelain --branch   # one line: ## $branch
docker compose -p "$COMPOSE_PROJECT_NAME" exec agent \
  git branch --list                 # main and $branch only
# Anything more: ask the agent to commit it on $branch, then check again.

# Take the work back as a bundle written outside the clone, so your git reads that one file.
docker compose -p "$COMPOSE_PROJECT_NAME" exec -T agent \
  git bundle create - main.."$branch" > ~/agent-sessions/$session.bundle
git -C ~/work/acme bundle verify ~/agent-sessions/$session.bundle
# transfer.fsckObjects makes git check every object in the bundle before it stores it.
git -C ~/work/acme -c transfer.fsckObjects=true fetch ~/agent-sessions/$session.bundle "$branch:$branch"
# The work is now the branch $branch in your repository; the bundle and the clone can go.
# These paths run on your host, or in CI as soon as you push: read every line of them first.
git -C ~/work/acme diff --stat main..."$branch" -- \
  .devcontainer .github .pre-commit-config.yaml Makefile .envrc .vscode .claude .mcp.json \
  .gemini .cursor .gitmodules \
  .githooks ':(glob)**/*compose*.y*ml' ':(glob)**/*Dockerfile*' ':(glob)**/conftest.py' \
  pyproject.toml uv.lock .python-version
git -C ~/work/acme diff main..."$branch"

# End the session: the clone and the agent's volume hold what the agent wrote.
# ${…:?} stops the command if the variable is empty, as in a new shell;
# each line carries its own guard.
docker compose -p "${COMPOSE_PROJECT_NAME:?}" down --volumes
rm -rf ~/agent-sessions/"${session:?}" ~/agent-sessions/"${session:?}".bundle
# Revoke the key now, unless it expires by itself (agent-containers.md section 4).
```

It is good because the work comes back as one bundle file, written outside the clone, so your git
commands read that file and never the agent's repository or its config. The paths that run on your
host or in CI are read before anything runs or is pushed. The definition the container starts from
sits in your own repository, out of the agent's reach until you merge a branch that changes it.
Each session ends with its clone and its volume removed, and the agent has no credential to push
anything itself.

What this example does not claim: it was not built or run when it was written. The host list
assumes an API key; a claude.ai login also needs the sign-in hosts on Claude Code's network access
page [9]. Claude Code 2.1.301 and uv 0.13.1 were the latest releases on 2026-10-15 [17], [18]. The
proxy does not terminate TLS, so it decides by host name and cannot stop domain fronting, and an
allowed host is still a way out ([agent-containers.md](agent-containers.md) section 5) [19].
Integration tests that start containers do not run here: they run in CI (section 8 of the same
file).

## 6. Sources

Checked 2026-10-16 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Development Containers — Dev Container reference, file locations — https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainer-reference.md
- [2] Docker — Networking in Compose — https://docs.docker.com/compose/how-tos/networking/
- [3] Docker — docker network create (CLI reference), network internal mode — https://docs.docker.com/reference/cli/docker/network/create/
- [4] Development Containers — Dev Container metadata reference (`overrideCommand`) — https://containers.dev/implementors/json_reference/
- [5] Docker Official Images — python `3.13/slim-trixie/Dockerfile` — https://github.com/docker-library/python/blob/d2a898cb88e46203577eabc62cdcf6e92aaee176/3.13/slim-trixie/Dockerfile
- [6] Docker — Control startup and shutdown order in Compose — https://docs.docker.com/compose/how-tos/startup-order/
- [7] Anthropic — Securely deploying AI agents (Claude Agent SDK docs) — https://code.claude.com/docs/en/agent-sdk/secure-deployment
- [8] Compose Specification — `container_spec.md` (`init`) — https://github.com/compose-spec/compose-spec/blob/de28432802a367d650bd4ad6748b19491b6cf986/container_spec.md
- [9] Anthropic — Enterprise network configuration, Network access requirements (Claude Code docs) — https://code.claude.com/docs/en/network-config#network-access-requirements
- [10] Anthropic — Development containers (Claude Code docs) — https://code.claude.com/docs/en/devcontainer
- [11] Development Containers — devcontainers/cli (`src/spec-node/dockerCompose.ts`, `utils.ts`, `singleContainer.ts`) — https://github.com/devcontainers/cli/tree/155f8b29e1c521bf365e2aebd74f3258a9160718/src/spec-node
- [12] Docker — Specify a project name — https://docs.docker.com/compose/how-tos/project-name/
- [13] Docker — Define and manage volumes in Docker Compose — https://docs.docker.com/reference/compose-file/volumes/
- [14] Docker — docker compose down (CLI reference) — https://docs.docker.com/reference/cli/docker/compose/down/
- [15] Docker — Build context — https://docs.docker.com/build/concepts/context/#dockerignore-files
- [16] Moby project — GHSA-mq39-4gv4-mvpx, External DNS requests from 'internal' networks could lead to data exfiltration (CVE-2024-29018) — https://github.com/moby/moby/security/advisories/GHSA-mq39-4gv4-mvpx
- [17] npm registry — `@anthropic-ai/claude-code`, its versions and their publish times — https://registry.npmjs.org/@anthropic-ai/claude-code — checked 2026-10-17
- [18] Astral — uv releases — https://github.com/astral-sh/uv/releases
- [19] Anthropic — Sandboxing (Claude Code docs) — https://code.claude.com/docs/en/sandboxing
- [20] Docker Official Images — library/debian — https://github.com/docker-library/official-images/blob/6b287dc80f463f088b8d6432ceeb633ec0c0b8a4/library/debian
- [21] Debuerreotype — debuerreotype-minimizing-config (the docker-clean APT configuration) — https://github.com/debuerreotype/debuerreotype/blob/ccebaf58b6f640746e6bb0e8046235681dc5018e/scripts/debuerreotype-minimizing-config
- [22] Debian — nodejs package in trixie — https://packages.debian.org/trixie/nodejs
- [24] Squid — src/tools.cc (leave_suid, enter_suid) — https://github.com/squid-cache/squid/blob/a433a54f0fd4a9d5b629bbfdf010097bd7581cbf/src/tools.cc
- [25] Python — The Python Tutorial: Using the Python Interpreter, 3.13 — https://docs.python.org/3.13/tutorial/interpreter.html
- [26] Squid — src/cf.data.pre (shutdown_lifetime) — https://github.com/squid-cache/squid/blob/a433a54f0fd4a9d5b629bbfdf010097bd7581cbf/src/cf.data.pre
