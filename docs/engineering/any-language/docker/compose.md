# Compose rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. One file, and what overrides it](#2-one-file-and-what-overrides-it)
- [3. Start a service when what it needs is healthy](#3-start-a-service-when-what-it-needs-is-healthy)
- [4. Configuration and secrets](#4-configuration-and-secrets)
- [5. Profiles and file watch](#5-profiles-and-file-watch)
- [6. Integration tests](#6-integration-tests)
- [7. Hardening keys](#7-hardening-keys)
- [8. A Compose file is trusted input](#8-a-compose-file-is-trusted-input)
- [9. Production: one host at most](#9-production-one-host-at-most)
- [10. Where it stops holding](#10-where-it-stops-holding)
- [11. Sources](#11-sources)

## 1. Purpose and the one rule

This file is for everyone who writes or changes a `compose.yaml`: people and AI agents alike. A
Compose file runs an application and the services it needs, such as its database, on one
machine. How the image itself is built is [images.md](images.md).

The one rule: **Compose runs the stack on one machine, from one reviewed file, and starts each
service only when what it needs is ready.**

Why it matters:

- Compose starts a service when its dependency is running, not when it is ready [1]. An
  application that connects to a database still starting fails at its first query.
- Compose does what the file says, including mounting the host's root folder or running a
  privileged container [2]. A file nobody reviewed is code nobody reviewed (section 8).

## 2. One file, and what overrides it

- **Name the file `compose.yaml`, and leave out the top-level `version:` key.** `compose.yaml` is
  the name Compose looks for first, and `docker-compose.yml` is kept only for older projects [3].
  Compose ignores `version:` and warns that it is obsolete [4].
- **Keep what everyone needs in `compose.yaml`; put a change for one machine or one environment
  in a second file that holds only the difference.** Compose reads `compose.override.yaml` on top
  of `compose.yaml` by default, and `-f compose.yaml -f compose.production.yaml` reads both in
  that order [5]. Lists such as `ports` are combined, and `environment` merges by variable
  name [5].
- **Read the merged result with `docker compose config` before you trust it.** It prints the file
  Compose will run, with every variable filled in and every override applied [6], [2].

## 3. Start a service when what it needs is healthy

- **Give every service that others depend on a `healthcheck` in `compose.yaml`, and depend on it
  with `condition: service_healthy`.** Compose waits only until a container is running, not until
  it is ready to answer [1]. With the condition, Compose starts the dependent service only after
  the health check passes [1], [7]. The check lives here, not in the image: Compose is the runtime
  that acts on it ([images.md](images.md) section 6).
- **Write the check with the service's own readiness tool**, as Docker's startup-order example
  does for Postgres with `pg_isready` [1]:
  `test: ["CMD-SHELL", "pg_isready -h 127.0.0.1 -U acme -d acme"]`. The tool asks the service
  whether it can serve, which a running process alone does not tell you. Ask over TCP (`-h`),
  because on first start the official Postgres image runs a temporary server that listens on the
  socket only [8].
- **In scripts and CI, start the stack with `docker compose up --wait`.** It waits until the
  services are running or healthy before it returns, so the next step does not run against a
  half-started stack; `--wait-timeout` sets how long it waits [9].

## 4. Configuration and secrets

- **The Python case: the application's settings and its `.env` follow
  [python.md](../../python/language/python.md) section 5.** Compose passes them to the container
  with `env_file: .env`, and also reads that `.env` on its own, but only to fill in `${...}` in the
  file: a value reaches a container only through `environment` or `env_file` [10], [11]. Compose's
  own variables, when you need any, go in a file of their own passed with `--env-file` [11],
  because the application's `.env` accepts only the application's variables.
- **Set the values that differ inside Compose, and the values two services must share, with
  `environment:`.** The database host differs: it is the service name `db` here and `localhost` in
  a local run. A value two services share, such as the database name, reaches both through the
  same `${...}`; the last bullet of this section says why. `environment` wins over
  `env_file` [12].
- **Make a required variable fail early:
  `${ACME_DATABASE_PASSWORD:?set it in .env or in the host's environment}`.** Without the `:?`, a
  missing variable becomes an empty string, and the service starts with an empty password [13].
- **Never write a secret value into `compose.yaml`.** The file is committed; the value is not.
  Reference a variable that comes from the git-ignored `.env`, or a secret file.
- **When a secret grants access to something outside your machine and the image can read it
  from a file, pass it as a Compose secret.** Compose mounts it at `/run/secrets/<name>`, only into
  the services you grant it to; the official Postgres image, for example, reads
  `POSTGRES_PASSWORD_FILE` [14], [15]. Docker's documentation warns that environment variables "can
  also be printed in logs" [14]. A Compose secret from a file is a bind mount, not encrypted:
  protect the source file as you would the value [14], [16].
- **A password for a database that exists only in the local stack may come from `.env` by
  interpolation**, taken from the variable the application already reads. It guards nothing
  outside your machine. Give both services the value through the same `${...}`, the database and
  the application alike: a variable exported in your shell wins over `.env` in interpolation, and
  `environment` wins over `env_file` in the container, so one interpolation that both read keeps
  the two from disagreeing [11], [12]. [compose-example.md](compose-example.md) does this.

## 5. Profiles and file watch

- **Put an optional service under a profile** (`profiles: [tools]`), so `docker compose up` starts
  only what everyone needs. A service without `profiles` always starts; a profiled one starts with
  `--profile tools`, or when you start it by name [17].
- **Use `develop.watch` to sync or rebuild a service built from local source while you work.**
  `sync` copies changed files into the running container; `rebuild` builds the image again and
  replaces the container [18], [19]. It works only for a service with a `build:` section [18].
  `sync` needs a
  container that runs the source it syncs; an image that installs the project as a package, as
  [dockerfile-example.md](dockerfile-example.md) does, takes `rebuild`.

## 6. Integration tests

Integration tests start the real services they need from the test code, with Testcontainers, which
has libraries for most languages ([python/testing/libraries.md](../../python/testing/libraries.md)
section 2 names the Python one): each run gets its own containers on free ports, removed
afterwards, so runs share no state and can go in parallel [20], [21]. Compose runs the whole
application, by
hand or for a smoke check of the stack in CI: `docker compose up --wait`, a request that retries
until the server answers, and `docker compose down`.

## 7. Hardening keys

Each key below narrows what a compromised process in the container can do. Set them on every
service whose image allows it, and say next to a missing one why the service needs that power.

- **`cap_drop: [ALL]`**, then `cap_add` only for a capability the service shows it needs. Docker
  starts a container with a default set of Linux capabilities; the best practice in Docker's
  security documentation is to remove all that the process does not need [22].
- **`security_opt: [no-new-privileges:true]`.** It stops container processes "from gaining new
  privileges", in the words of Docker's reference, for example through a set-user-ID binary [23].
- **`init: true` where [images.md](images.md) section 6 asks for an init.** Compose then runs
  `docker-init` (a tini build) as PID 1, which forwards signals and reaps the children [7], [23].
- **`pids_limit`**, so a process that forks without end cannot exhaust the host. If you also set
  `deploy.resources.limits.pids`, the two must agree [7].
- **Publish a port on `127.0.0.1` only (`"127.0.0.1:8000:8000"`) for a local stack.** A port
  published on all interfaces is reachable from the network, and Docker's own firewall rules can
  bypass a host firewall such as UFW [24], [16], [25].

`read_only: true` is a point to adapt ([images.md](images.md) section 6). If you turn it on, give
each path the process writes a `tmpfs`, in the short form that sets owner and mode:
`tmpfs: ["/tmp:mode=1770,uid=10001,gid=10001"]` [7]. The long volume form of a `tmpfs` accepts only
`size` and `mode` [7], [26]. A bare `tmpfs` gets Docker's defaults, which some runc releases made
root-owned `0755`, so the non-root user could not write it [27] ([images.md](images.md) section 6
lists the other costs).

## 8. A Compose file is trusted input

Docker's documentation says it directly: "Docker Compose treats every Compose file as trusted
input" [2].

- **Before you run a Compose file you did not write, read `docker compose config`** and look for
  `privileged`, `network_mode: host`, `pid: host`, `devices`, bind mounts of host paths, and
  `provider` services [2]. Each of these gives the container power over the host [2].
- **Never let CI or a coding agent run a Compose file from a source nobody reviewed**, such as a
  pull request from a fork or a repository the agent was asked to look at [2]. The agent's own
  container rules are [agent-containers.md](agent-containers.md).
- **Pin a remote `include` or `extends` to a digest or a commit**, so the file you reviewed is
  the file that runs. Docker's trust model asks for the digest: "Digests are immutable" [2]. The
  commit, for a Git remote, is this practice's own addition.

## 9. Production: one host at most

- **Use Compose in production only on a single host.** Docker's documentation says "Compose
  supports production deployments on single hosts", with a production override file that, for
  example, removes source-code bind mounts and adds `restart: always` [28], [29]. For more than one
  host, Docker points to Swarm [29]; teams on Kubernetes write manifests for it.

A production host runs the image CI pushed, by digest ([images.md](images.md) section 8), and gets
no `.env` ([python.md](../../python/language/python.md) section 5).

## 10. Where it stops holding

- **A service whose image runs as root, or needs a capability**, such as a network tool, cannot
  take every key of section 7. Keep the ones it can, and write next to the service why it lacks
  the others.

## 11. Sources

Checked 2026-10-16 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Docker — Control startup and shutdown order in Compose — https://docs.docker.com/compose/how-tos/startup-order/
- [2] Docker — Trust model for Compose files — https://docs.docker.com/compose/trust-model/
- [3] Docker — How Compose works (Compose application model) — https://docs.docker.com/compose/intro/compose-application-model/
- [4] Docker — Version and name top-level elements — https://docs.docker.com/reference/compose-file/version-and-name/
- [5] Docker — Merge Compose files — https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/
- [6] Docker — docker compose config (CLI reference) — https://docs.docker.com/reference/cli/docker/compose/config/
- [7] Compose Specification — `spec.md`, `container_spec.md` and `schema/compose-spec.json` — https://github.com/compose-spec/compose-spec/tree/de28432802a367d650bd4ad6748b19491b6cf986
- [8] Docker Official Images — postgres `18/trixie/docker-entrypoint.sh` — https://github.com/docker-library/postgres/blob/dfc76bb299b057785026eb2eea39556b6fe52983/18/trixie/docker-entrypoint.sh
- [9] Docker — docker compose up (CLI reference) — https://docs.docker.com/reference/cli/docker/compose/up/
- [10] Docker — Set environment variables within your container's environment — https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/
- [11] Docker — Set, use, and manage variables in a Compose file with interpolation — https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
- [12] Docker — Environment variables precedence in Docker Compose — https://docs.docker.com/compose/how-tos/environment-variables/envvars-precedence/
- [13] Docker — Interpolation (Compose file reference) — https://docs.docker.com/reference/compose-file/interpolation/
- [14] Docker — Manage secrets securely in Docker Compose — https://docs.docker.com/compose/how-tos/use-secrets/
- [15] Docker Official Images — postgres (Docker Hub page) — https://hub.docker.com/_/postgres
- [16] OWASP Cheat Sheet Series — Docker Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
- [17] Docker — Using profiles with Compose — https://docs.docker.com/compose/how-tos/profiles/
- [18] Docker — Use Compose Watch — https://docs.docker.com/compose/how-tos/file-watch/
- [19] Docker — Compose Develop Specification — https://docs.docker.com/reference/compose-file/develop/
- [20] Testcontainers — Getting started, What is Testcontainers? — https://testcontainers.com/getting-started/
- [21] Testcontainers for Java — Networking and communicating with containers — https://java.testcontainers.org/features/networking/
- [22] Docker — Docker Engine security — https://docs.docker.com/engine/security/#linux-kernel-capabilities
- [23] Docker — docker container run (CLI reference) — https://docs.docker.com/reference/cli/docker/container/run/
- [24] Docker — Port publishing and mapping — https://docs.docker.com/engine/network/port-publishing/
- [25] Docker — Packet filtering and firewalls — https://docs.docker.com/engine/network/packet-filtering-firewalls/
- [26] Ricky Curtice — Add `gid` and `uid` to `tmpfs` long-form mount options a la the current `mode` support (compose-spec/compose-spec issue #278, 2022; opinion) — https://github.com/compose-spec/compose-spec/issues/278
- [27] opencontainers/runc — Recent security update changed default permissions of tmpfs (runc issue #4971, 2025; case) — https://github.com/opencontainers/runc/issues/4971
- [28] Docker — Why use Compose? — https://docs.docker.com/compose/intro/features-uses/
- [29] Docker — Use Compose in production — https://docs.docker.com/compose/how-tos/production/
