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

- Compose starts a service when its dependency is running, not when it is ready. An application
  that connects to a database still starting fails at its first query.
- Compose does what the file says, including mounting the host's root folder or running a
  privileged container. A file nobody reviewed is code nobody reviewed (section 8).

## 2. One file, and what overrides it

- **Name the file `compose.yaml`, and leave out the top-level `version:` key.** `compose.yaml` is
  the name Compose looks for first, and `docker-compose.yml` is kept only for older projects.
  Compose ignores `version:` and warns that it is obsolete.
- **Keep what everyone needs in `compose.yaml`; put a change for one machine or one environment
  in a second file that holds only the difference.** Compose reads `compose.override.yaml` on top
  of `compose.yaml` by default, and `-f compose.yaml -f compose.production.yaml` reads both in
  that order. Lists such as `ports` are combined, and `environment` merges by variable name.
- **Read the merged result with `docker compose config` before you trust it.** It prints the file
  Compose will run, with every variable filled in and every override applied.

## 3. Start a service when what it needs is healthy

- **Give every service that others depend on a `healthcheck` in `compose.yaml`, and depend on it
  with `condition: service_healthy`.** Compose waits only until a container is running, not until
  it is ready to answer. With the condition, Compose starts the dependent service only after the
  health check passes. The check lives here, not in the image: Compose is the runtime that acts on
  it ([images.md](images.md) section 6).
- **Write the check with the service's own readiness tool**, as Docker's startup-order example
  does for Postgres with `pg_isready`:
  `test: ["CMD-SHELL", "pg_isready -h 127.0.0.1 -U acme -d acme"]`. The tool asks the service
  whether it can serve, which a running process alone does not tell you. Ask over TCP (`-h`),
  because on first start the official Postgres image runs a temporary server that listens on the
  socket only.
- **In scripts and CI, start the stack with `docker compose up --wait`.** It waits until the
  services are running or healthy before it returns, so the next step does not run against a
  half-started stack; `--wait-timeout` sets how long it waits.

## 4. Configuration and secrets

- **The Python case: the application's settings and its `.env` follow
  [python.md](../../python/language/python.md) section 5.** Compose passes them to the container
  with `env_file: .env`, and also reads that `.env` on its own, but only to fill in `${...}` in the
  file: a value reaches a container only through `environment` or `env_file`. Compose's own variables, when you need any, go in a file of
  their own passed with `--env-file`, because the application's `.env` accepts only the
  application's variables.
- **Set the values that differ inside Compose, and the values two services must share, with
  `environment:`.** The database host differs: it is the service name `db` here and `localhost` in
  a local run. A value two services share, such as the database name, reaches both through the
  same `${...}`; the last bullet of this section says why. `environment` wins over `env_file`.
- **Make a required variable fail early:
  `${ACME_DATABASE_PASSWORD:?set it in .env or in the host's environment}`.** Without the `:?`, a
  missing variable becomes an empty string, and the service starts with an empty password.
- **Never write a secret value into `compose.yaml`.** The file is committed; the value is not.
  Reference a variable that comes from the git-ignored `.env`, or a secret file.
- **When a secret grants access to something outside your machine and the image can read it
  from a file, pass it as a Compose secret.** Compose mounts it at `/run/secrets/<name>`, only into
  the services you grant it to; the official Postgres image, for example, reads
  `POSTGRES_PASSWORD_FILE`. Docker's documentation warns that environment variables "can also be
  printed in logs". A Compose secret from a file is a bind mount, not encrypted: protect the source
  file as you would the value.
- **A password for a database that exists only in the local stack may come from `.env` by
  interpolation**, taken from the variable the application already reads. It guards nothing
  outside your machine. Give both services the value through the same `${...}`, the database and
  the application alike: a variable exported in your shell wins over `.env` in interpolation, and
  `environment` wins over `env_file` in the container, so one interpolation that both read keeps
  the two from disagreeing. [compose-example.md](compose-example.md) does this.

## 5. Profiles and file watch

- **Put an optional service under a profile** (`profiles: [tools]`), so `docker compose up` starts
  only what everyone needs. A service without `profiles` always starts; a profiled one starts with
  `--profile tools`, or when you start it by name.
- **Use `develop.watch` to sync or rebuild a service built from local source while you work.**
  `sync` copies changed files into the running container; `rebuild` builds the image again and
  replaces the container. It works only for a service with a `build:` section. `sync` needs a
  container that runs the source it syncs; an image that installs the project as a package, as
  [dockerfile-example.md](dockerfile-example.md) does, takes `rebuild`.

## 6. Integration tests

Integration tests start the real services they need from the test code, with Testcontainers, which
has libraries for most languages ([python/testing/libraries.md](../../python/testing/libraries.md)
section 2 names the Python one): each run gets its own containers on free ports, removed
afterwards, so runs share no state and can go in parallel. Compose runs the whole application, by
hand or for a smoke check of the stack in CI: `docker compose up --wait`, a request that retries
until the server answers, and `docker compose down`.

## 7. Hardening keys

Each key below narrows what a compromised process in the container can do. Set them on every
service whose image allows it, and say next to a missing one why the service needs that power.

- **`cap_drop: [ALL]`**, then `cap_add` only for a capability the service shows it needs. Docker
  starts a container with a default set of Linux capabilities; the best practice in Docker's
  security documentation is to remove all that the process does not need.
- **`security_opt: [no-new-privileges:true]`.** It stops container processes "from gaining new
  privileges", in the words of Docker's reference, for example through a set-user-ID binary.
- **`init: true` where [images.md](images.md) section 6 asks for an init.** Compose then runs
  `docker-init` (a tini build) as PID 1, which forwards signals and reaps the children.
- **`pids_limit`**, so a process that forks without end cannot exhaust the host. If you also set
  `deploy.resources.limits.pids`, the two must agree.
- **Publish a port on `127.0.0.1` only (`"127.0.0.1:8000:8000"`) for a local stack.** A port
  published on all interfaces is reachable from the network, and Docker's own firewall rules can
  bypass a host firewall such as UFW (OWASP Docker Security Cheat Sheet).

`read_only: true` is a point to adapt ([images.md](images.md) section 6). If you turn it on, give
each path the process writes a `tmpfs`, in the short form that sets owner and mode:
`tmpfs: ["/tmp:mode=1770,uid=10001,gid=10001"]`. The long volume form of a `tmpfs` accepts only
`size` and `mode`. A bare `tmpfs` gets Docker's defaults, which some runc releases made
root-owned, so the non-root user could not write it ([images.md](images.md) section 6 lists the
other costs).

## 8. A Compose file is trusted input

Docker's documentation says it directly: "Docker Compose treats every Compose file as trusted
input."

- **Before you run a Compose file you did not write, read `docker compose config`** and look for
  `privileged`, `network_mode: host`, `pid: host`, `devices`, bind mounts of host paths, and
  `provider` services. Each of these gives the container power over the host.
- **Never let CI or a coding agent run a Compose file from a source nobody reviewed**, such as a
  pull request from a fork or a repository the agent was asked to look at. The agent's own
  container rules are [agent-containers.md](agent-containers.md).
- **Pin a remote `include` or `extends` to a digest or a commit**, so the file you reviewed is the
  file that runs.

## 9. Production: one host at most

- **Use Compose in production only on a single host.** Docker's documentation says "Compose
  supports production deployments on single hosts", with a production override file that, for
  example, removes source-code bind mounts and adds `restart: always`. For more than one host,
  Docker points to Swarm; teams on Kubernetes write manifests for it.

A production host runs the image CI pushed, by digest ([images.md](images.md) section 8), and gets
no `.env` ([python.md](../../python/language/python.md) section 5).

## 10. Where it stops holding

- **A service whose image runs as root, or needs a capability**, such as a network tool, cannot
  take every key of section 7. Keep the ones it can, and write next to the service why it lacks
  the others.

## 11. Sources

Read in October 2026.

- Docker documentation: "Compose application model" (file names); "Version and name top-level
  elements"; "Merge Compose files", the merge reference and `include`; "Control
  startup and shutdown order";
  `docker compose up --wait`; "Use profiles"; "Use Compose Watch" and the `develop` reference;
  "Ways to set environment variables", "Environment variables precedence", "Interpolation", and the
  best practices for environment variables; "Use secrets in Compose"; the services reference
  (`init`, `pids_limit`, `read_only`, `cap_drop`, `security_opt`, `tmpfs`); "Use Compose in
  production"; "Why use Compose?"; "Compose trust model"; "Docker Engine security" (capabilities).
- The Compose Specification (`spec.md`, `container_spec.md`, `13-merge.md`, the JSON schema) and
  its issue #278 (tmpfs `uid` and `gid` in the long form).
- The official Postgres image on Docker Hub (`POSTGRES_PASSWORD_FILE`, the data volume of
  version 18) and its `docker-entrypoint.sh` (the temporary server of the first start); Docker's
  startup-order page (`pg_isready`).
- Testcontainers documentation (the libraries for each language, containers on free ports,
  cleanup after the run).
- OWASP Docker Security Cheat Sheet (secrets in Compose, publishing ports and UFW).
- moby/moby `Dockerfile` (`docker-init` is built from tini); runc issue #4971 (tmpfs mode).
