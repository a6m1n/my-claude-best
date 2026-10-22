# Example: the Acme service and its database in Compose

A worked example for [compose.md](compose.md). It runs the image of
[dockerfile-example.md](dockerfile-example.md) with a Postgres database on one machine, for local
work. The application reads its settings from the `.env` that
[python/language/settings-example.md](../../python/language/settings-example.md) describes: the
`ACME_DATABASE_HOST`, `ACME_DATABASE_NAME`, `ACME_DATABASE_USER` and `ACME_DATABASE_PASSWORD`
values used below come from it. The `.env` is git-ignored and never enters the image.

**Navigation**

- [1. compose.yaml](#1-composeyaml)
- [2. Run it](#2-run-it)
- [3. Sources](#3-sources)

## 1. compose.yaml

```yaml
services:
  api:
    build: .
    # The application's own ACME_ settings (python.md section 5).
    env_file: .env
    environment:
      # Inside Compose the database is the service "db"; .env says localhost for runs
      # without Compose, and environment wins over env_file.
      ACME_DATABASE_HOST: db
      # The same ${...} as the db service, so a value exported in your shell reaches both.
      ACME_DATABASE_NAME: ${ACME_DATABASE_NAME:?set it in .env or in the host's environment}
      ACME_DATABASE_USER: ${ACME_DATABASE_USER:?set it in .env or in the host's environment}
      ACME_DATABASE_PASSWORD: ${ACME_DATABASE_PASSWORD:?set it in .env or in the host's environment}
    ports:
      - "127.0.0.1:8000:8000"  # reachable from this machine only (compose.md section 7)
    depends_on:
      db:
        condition: service_healthy  # start once Postgres answers, not once it runs
    read_only: true  # the service cannot change its own files (compose.md section 7)
    tmpfs:
      # The one path the service may write, owned by the image's user (compose.md section 7).
      - /tmp:mode=1770,uid=10001,gid=10001
    cap_drop: [ALL]  # the API needs no Linux capability (compose.md section 7)
    security_opt: [no-new-privileges:true]  # no process gains privileges (compose.md section 7)
    pids_limit: 200  # a fork loop stops here, not on the host (compose.md section 7)

  db:
    image: postgres:18-trixie@sha256:...
    environment:
      POSTGRES_DB: ${ACME_DATABASE_NAME:?set it in .env or in the host's environment}
      POSTGRES_USER: ${ACME_DATABASE_USER:?set it in .env or in the host's environment}
      # A database that exists only in this stack: both services take its name, user and
      # password through the same ${...}, so the two cannot disagree (compose.md section 4).
      POSTGRES_PASSWORD: ${ACME_DATABASE_PASSWORD:?set it in .env or in the host's environment}
    volumes:
      - db-data:/var/lib/postgresql  # the data path of Postgres 18 and later
    healthcheck:
      # $$ keeps the variables for the container's shell instead of Compose. -h asks over TCP: on
      # first start the image runs a temporary server on the socket only (compose.md section 3).
      test: ["CMD-SHELL", "pg_isready -h 127.0.0.1 -U \"$${POSTGRES_USER}\" -d \"$${POSTGRES_DB}\""]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 10s
    # No cap_drop: [ALL], as compose.md section 7 says for a third-party image: the Postgres
    # entrypoint changes file owners and then switches to its own user. The cost: Docker's default
    # capabilities stay, such as NET_RAW; dropping them all, as compose.md section 7 prefers,
    # needs user: and a test that starts the service.
    security_opt: [no-new-privileges:true]
    pids_limit: 200  # a fork loop stops here, not on the host (compose.md section 7)
    # No published port: only the api service reaches the database.

volumes:
  db-data:
```

| Part | Why |
|---|---|
| no `version:` key, the name `compose.yaml` | the name Compose reads first; `version:` is obsolete [1], [2] |
| `env_file: .env` | passes the application's settings in; Compose's own reading of `.env` only fills the `${...}` below [3], [4] |
| `environment:` with `ACME_DATABASE_HOST: db` and the three `${...}` values | the host is the one value that differs inside Compose; the name, user and password come through the same `${...}` as `db`'s, so a value exported in your shell, which wins over `.env`, reaches both services [4] |
| `"127.0.0.1:8000:8000"` | a published port on every interface would be reachable from the network [5] |
| `depends_on` with `service_healthy` and the `healthcheck` on `db` | the API starts when Postgres can serve, and the check sits in the file of the runtime that acts on it [6] |
| `read_only`, `tmpfs` with `uid`, `gid` and `mode` | the service cannot change its files; the short `tmpfs` form is the one that sets an owner [7] |
| `cap_drop: [ALL]`, `no-new-privileges`, `pids_limit` | the API needs no Linux capability; no process gains privileges [8]; a fork loop stops at 200 processes |
| `${ACME_DATABASE_PASSWORD:?…}` | fails at once when neither `.env` nor the host's environment sets the value, instead of starting Postgres with an empty password [9] |
| `postgres:18-trixie@sha256:...` | names the Debian release and pins the digest, like every image ([images.md](images.md) section 4) |
| `db-data:/var/lib/postgresql` | keeps the data across restarts; `docker compose down --volumes` removes it [10]. The data volume mounts at `/var/lib/postgresql`, where the image declares it from Postgres 18 on; for 17 and below the path is `/var/lib/postgresql/data` [12] |
| no `ports:` on `db` | the database is not reachable from the host or the network |

It is good because the API never starts before its database can answer, no secret value is in
the file, and the API gets no Linux capability, while the database keeps Docker's default set, as
compose.md section 7 says for a third-party image, with its reason and its cost written next to
it.

## 2. Run it

```sh
docker compose config     # the file Compose will run, variables filled in: read it first
docker compose up --wait  # returns once db is healthy and api is running
# Retries until api answers at all: the service has no health route, so any HTTP status counts.
curl --silent --output /dev/null --retry 10 --retry-all-errors --retry-delay 1 http://127.0.0.1:8000/
docker compose logs api
docker compose down       # add --volumes to drop the database too
```

It is good because it reads the merged file before it runs it ([compose.md](compose.md) section
2), returns only once the stack is up, and checks that the API answers before anyone uses it.

What this example does not claim: it was not run when it was written; `postgres:18-trixie` was
the current major version and Debian release of the official image in October 2026 [11], and the
`sha256:...` digest is a placeholder until Renovate fills it. A stack that needs a secret for a
service outside this machine, such as a payment provider's key, passes it as a Compose secret
when the image can read files, as [compose.md](compose.md) section 4 says; the Acme settings
class reads its key from an environment variable, so it comes through `env_file`.

## 3. Sources

Checked 2026-10-16 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Docker — How Compose works (Compose application model) — https://docs.docker.com/compose/intro/compose-application-model/
- [2] Docker — Version and name top-level elements — https://docs.docker.com/reference/compose-file/version-and-name/
- [3] Docker — Set environment variables within your container's environment — https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/
- [4] Docker — Set, use, and manage variables in a Compose file with interpolation — https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
- [5] Docker — Port publishing and mapping — https://docs.docker.com/engine/network/port-publishing/
- [6] Docker — Control startup and shutdown order in Compose — https://docs.docker.com/compose/how-tos/startup-order/
- [7] Compose Specification — `container_spec.md` (`tmpfs`) and `schema/compose-spec.json` — https://github.com/compose-spec/compose-spec/tree/de28432802a367d650bd4ad6748b19491b6cf986
- [8] Docker — docker container run (CLI reference) — https://docs.docker.com/reference/cli/docker/container/run/
- [9] Docker — Interpolation (Compose file reference) — https://docs.docker.com/reference/compose-file/interpolation/
- [10] Docker — docker compose down (CLI reference) — https://docs.docker.com/reference/cli/docker/compose/down/
- [11] Docker Official Images — `library/postgres`, the tag list — https://github.com/docker-library/official-images/blob/f5a08cb993309e539ddddf5b23236d4442fb95a1/library/postgres
- [12] Docker Official Images — postgres image documentation — https://github.com/docker-library/docs/blob/a5b1248/postgres/content.md
