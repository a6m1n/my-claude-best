# Compose keys

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. The baseline every local stack has](#2-the-baseline-every-local-stack-has)
- [3. Top-level elements](#3-top-level-elements)
- [4. Service keys](#4-service-keys)
- [5. Development and one production host](#5-development-and-one-production-host)
- [6. Common mistakes](#6-common-mistakes)
- [7. Where these rules stop holding](#7-where-these-rules-stop-holding)
- [8. Sources](#8-sources)

## 1. Purpose and the one rule

This file is for everyone who writes, changes or reviews a `compose.yaml`: people and AI agents
alike. For each key it says what the key does, when you need it, and when it is over-engineering
or does harm. The rules for a Compose file as a whole (one reviewed file, a health-gated start,
configuration and secrets, hardening, the trust model) are [compose.md](compose.md); this file
links them and does not repeat them. [compose-example.md](compose-example.md) shows the baseline
in one file. The keys below are as Docker Compose v5.6.0 reads them [1]. This file covers the keys
a local stack and one production host meet. It leaves out the rest of the Compose Specification
[3], [4], among them `labels`, `working_dir`, `platform`, `extends`, `provider`, and the top-level
`models` and `jobs` [46], [47].

The one rule: **write a key only when it changes what runs; a key that restates a default stays
out.** Whether a key goes into `compose.yaml` or into an override file is [compose.md](compose.md)
section 2.

Why it matters:

- Compose's defaults already cover most of what a local stack needs. Services reach each other by
  name on a default network, and "For most development setups, the default network is sufficient"
  [2]; `restart` is `no` unless you set it [3]. A key that restates a default adds a line to read
  and nothing else.
- Some keys keep costing after you add them: a fixed `container_name` stops a service from running
  twice [3], and a short-syntax bind mount creates a missing folder on the host without a word [4].

## 2. The baseline every local stack has

| Key | Why every local stack has it |
|---|---|
| `services` with `build` or `image` | what runs: your own service built from source, the others from a pinned image ([images.md](images.md) section 4) |
| `env_file` and `environment` | the application's settings, and the values that differ inside Compose ([compose.md](compose.md) section 4) |
| `ports` on `127.0.0.1` | the one service you open from the host, reachable from this machine only ([compose.md](compose.md) section 7) |
| `volumes` with a named volume | the data the stack keeps, such as the database's ([section 4](#4-service-keys), storage) |
| `healthcheck` and `depends_on` with `service_healthy` | a service starts when what it needs can answer ([compose.md](compose.md) section 3) |

A stack with one service and no data needs only `services`; section 4 says when each other row applies.

[compose.md](compose.md) section 7 adds the hardening keys and says which services take them;
section 4 below adds the other leave-out cases it found.

## 3. Top-level elements

| Element | What it does | Use it when | Leave it out when |
|---|---|---|---|
| `services` | The containers of the application. | Always. | Never. |
| `volumes` | Declares named volumes; an empty entry uses the engine's defaults, and each service must be granted the volume by name [5]. | The stack keeps data, such as a database. `external: true` or `name:` only when the volume's life is managed outside this project. | `external` and `name` by default: `name` is used as is, not scoped to the project, and `external` fails when the volume is missing [5]. |
| `networks` | Declares networks. Without it, every service joins one default network [2]. | You need more than one network, such as the agent's internal network ([agent-containers.md](agent-containers.md) section 5), or you change the default network's settings under `networks: default` [2]. | One network serves the stack: "the default network is sufficient" [2]. |
| `secrets` | Declares secrets that services mount as files ([compose.md](compose.md) section 4). | Where [compose.md](compose.md) section 4 asks for a Compose secret. | A password for a database that exists only in this stack ([compose.md](compose.md) section 4). |
| `configs` | Declares data that a service mounts as a file once it is granted by name; by default the file is readable by all (mode 0444) [43]. | A service needs a configuration file that is not a secret, and you do not want a bind mount (this practice's own call: a config can also take its content inline or from a variable, with no file on the host [43]). | A bind mount with `:ro` does the job ([section 4](#4-service-keys), storage); this practice's own call, because the mount is one line, where a config also needs a top-level entry and a grant in each service [43]. |
| `include` | Loads another Compose file as its own application model with its own project folder; it "solves the relative path problem that `extends` and merge present" [6]. | A part of the stack that another team or folder owns [6]. | One file serves the whole stack. |
| `x-` fields and YAML anchors | "Compose ignores any fields that start with `x-`" [7]; an anchor reuses a block, and anchors resolve before variables are filled in [8]. | Two or more services share the same block. | One service would use it. |
| `name` | The project name, used when neither `-p` nor `COMPOSE_PROJECT_NAME` is set [44]. | The folder name is not a valid project name, or two different projects have folders with the same name [44]. | The folder name fits. For separate copies of one project, set `-p` or `COMPOSE_PROJECT_NAME` instead [44]. |
| `version` | Obsolete: "you'll receive a warning message that it is obsolete if used" [9]. | Never. | Always ([compose.md](compose.md) section 2). |

## 4. Service keys

### What runs

Required: every service that Compose runs as a container needs `image`, `build`, or both; `image`
"may be omitted from a Compose file as long as a `build` section is declared" [4]. A `provider`
service, which Compose "won't manage directly", needs neither [3].

| Key | What it does | Use it when | Leave it out when |
|---|---|---|---|
| `image` | The image the service runs; with `build` too and no `pull_policy`, Compose pulls first and builds only when the image is missing [10]. | A service you do not build, pinned by tag and digest ([images.md](images.md) section 4). | Your own service in development: use `build`, or set `pull_policy: build` if you keep both. |
| `build` | Builds the image from a folder; the context is `.` by default [10]. | Your own service, in development. | A production host, which runs the image CI pushed ([compose.md](compose.md) section 9). |
| `command` | Replaces the image's `CMD`; the string form does not run in a shell [4]. | The same image plays another role, such as a worker. | The image's `CMD` is right. |
| `entrypoint` | Replaces the image's `ENTRYPOINT`; a non-null value makes Compose ignore the image's `CMD` [4]. | You debug an image by hand (this practice's own call: an `entrypoint` left in the file replaces how the image starts, its `CMD` included [4]). | Almost always, for the reason in the "Use it when" cell. |
| `profiles` | Starts the service only when its profile is named ([compose.md](compose.md) section 5). | An optional tool. | A core service: "The core services of your application shouldn't be assigned `profiles`" [11]. |

### Configuration

| Key | What it does | Use it when | Leave it out when |
|---|---|---|---|
| `env_file` | Passes the variables of a file to the container ([compose.md](compose.md) section 4). | The application's settings file in development. | A production host, which gets no `.env` ([compose.md](compose.md) section 9). |
| `environment` | Sets variables; it wins over `env_file` [4]. | The values [compose.md](compose.md) section 4 sets with it. | A value [compose.md](compose.md) section 4 does not set with it: the other settings reach the container through `env_file`. |
| `secrets` (service) | Mounts a granted secret at `/run/secrets/<name>` ([compose.md](compose.md) section 4). Docker Compose ignores `uid`, `gid` and `mode` for a secret read from a file [12], so do not rely on them: give the host file permissions the service's user can read. | The secrets [compose.md](compose.md) section 4 passes as Compose secrets. | Any other secret ([compose.md](compose.md) section 4). |

### Network

| Key | What it does | Use it when | Leave it out when |
|---|---|---|---|
| `ports` | Publishes a container port on the host. "If you do not specify a host IP (such as `127.0.0.1`), Docker binds to all interfaces (`0.0.0.0`), bypassing host firewall rules" [12]. | A port you open from the host, bound as [compose.md](compose.md) section 7 says. | Only other services call the port, as with the database. |
| `expose` | Lists ports for other services without publishing them; a port the image already exposes is visible to other containers anyway [12]. | Almost never. | Other services already reach the port on the default network. |
| `networks` (service) | Attaches the service to declared networks [4]. | You declared more than one network. | The default network serves. |
| `extra_hosts` | Adds host names to the container's `/etc/hosts` [4]. | A container must reach a service on a Linux Docker Engine host: `host.docker.internal:host-gateway`, where `host-gateway` "resolves to the internal IP address of the host" [13]. | Every machine and runner that starts this file runs Docker Desktop, which resolves `host.docker.internal` itself [13], [14]. With a Linux Docker Engine among them, keep the line: on Desktop, `host-gateway` resolves to the same address [2]. |
| `network_mode: host` | Shares the host's network; on Docker Desktop it must be turned on first, and published ports are ignored [15]. | Docker names two uses: "To optimize performance", and when "a container needs to handle a large range of ports" [15]. This practice's own call adds a tool that must see the host's network interfaces, since the container shares the host's networking namespace [15]. | You only need to reach one host service: `extra_hosts` does that with less. |
| `links` | A legacy link between services. "Links are not required to enable services to communicate" [3], and a link also adds a dependency that restarts the service [16]. | Never. | Always. |

### Storage

| Key | What it does | Use it when | Leave it out when |
|---|---|---|---|
| `volumes`, a named volume | Mounts a volume Docker manages: "Volumes are the preferred mechanism for persisting data generated by and used by Docker containers" [17]. | Data the stack keeps, such as a database's. Docker's Postgres guide: "For most development and production scenarios, named volumes are simpler and less error-prone" [18]. | The host needs the files: "Volumes are not a good choice if you need to access the files from the host" [17]. |
| `volumes`, a bind mount | Mounts a host path; it has "write access to files on the host by default" [19]. | Source code and configuration shared with the host [19]; add `:ro` to a configuration file. Use the long syntax with `create_host_path: false`, so a mistyped path fails instead of creating a folder [4]. | A database's data: "Permission errors are the most frequent problem with bind mounts" [18]. |
| `tmpfs` | A memory-backed folder. | The paths a `read_only` service writes ([compose.md](compose.md) section 7). | The service writes nothing outside its volumes. |

### Order and restart

| Key | What it does | Use it when | Leave it out when |
|---|---|---|---|
| `depends_on` | Starts services in order. "On startup, Compose does not wait until a container is "ready", only until it's running" [20], so the short form does not stand in for readiness; `required: false` only warns when the service is missing [21]. | Where [compose.md](compose.md) section 3 asks for it. | A service that needs nothing at start ([compose.md](compose.md) section 3). |
| `healthcheck` | Tests the container, with the same defaults as the Dockerfile's `HEALTHCHECK`; `disable: true` turns off the image's check [21]. | The services [compose.md](compose.md) section 3 gives one. | The services [compose.md](compose.md) section 3 does not give one; development may turn off a noisy web check [22]. |
| `restart` | Restarts the container when it stops; `no` by default [3]. Docker's documentation says a policy takes effect only after the container has run 10 seconds, which "prevents a container which doesn't start at all from going into a restart loop" [23]. The Engine's source code restarts a container that exits sooner too, after a delay that starts at 100 ms and doubles up to one minute; 10 seconds of running resets the delay [49]. This file follows the code, because the code is what the Engine runs: under `always` or `unless-stopped`, a process that exits in its first seconds keeps restarting, with a growing delay [49]. | A production host, in the override file: Docker lists "a restart policy like `restart: always`" among the production changes [24]. In development only when the stack should come back after a Docker restart (this practice's reading); prefer `unless-stopped` to `always`, so a container you stopped by hand stays stopped after the Docker daemon restarts too [23], the change Supabase's local CLI made [25]. After a Docker restart the Engine, not Compose, starts these containers again, with no `depends_on` order and no health-check gate (this practice's reading of the Engine's code), so the service must retry its first connection [48]. | A stack you start by hand in development: `no` is the default, so write nothing (DDEV writes `restart: "no"` out, which adds a line and no behaviour [26]). |

### The process

| Key | What it does | Use it when | Leave it out when |
|---|---|---|---|
| `init` | Runs an init as PID 1 "that forwards signals and reaps processes" [4]. | Where [images.md](images.md) section 6 asks for an init ([compose.md](compose.md) section 7). | Where images.md section 6 asks for none. |
| `user` | The user the container runs as; by default the image's `USER`, else root [4]. | A third-party image that should take the hardening keys ([compose.md](compose.md) section 7 says on what terms). | Your own image already sets `USER` ([images.md](images.md) section 6). |
| `stop_grace_period` | How long Compose waits after the stop signal before it kills; 10 seconds by default [4]. | A server needs longer to finish its requests. | The default fits. |
| `stop_signal` | The signal Compose sends to stop; `SIGTERM` by default [4]. | The image's server stops on another signal and its image does not set `STOPSIGNAL` ([dockerfile-instructions.md](dockerfile-instructions.md) section 3). | The image sets it, or `SIGTERM` works. |

### Hardening

[compose.md](compose.md) section 7 owns these keys and says which services take them; the table
links those tiers and adds other leave-out cases for some of them.

| Key | What it does | Use it when | Leave it out when |
|---|---|---|---|
| `security_opt: [no-new-privileges:true]` | Stops processes from gaining privileges through a set-user-ID file ([compose.md](compose.md) section 7). | The services the tiers of [compose.md](compose.md) section 7 give it. | The entrypoint calls `sudo` or another setuid program ([compose.md](compose.md) section 7); the kernel's docs add that it "may interfere with LSM-based sandboxing" [27]. |
| `cap_drop: [ALL]` | Removes the Linux capabilities Docker grants by default. | The services the tiers of [compose.md](compose.md) section 7 give it. | The services those tiers leave without it. |
| `read_only` with `tmpfs` | Makes the container's filesystem read-only. | The services the tiers of [compose.md](compose.md) section 7 give it. | The services those tiers leave without it; [images.md](images.md) section 6 lists what it breaks. |
| `pids_limit` | Caps the number of processes [4]. | The services the tiers of [compose.md](compose.md) section 7 give it, sized to its work: a limit of 256 failed a parallel Rust build on a 16-core machine [32]. | No case found ([compose.md](compose.md) section 7). |

### Production on one host

| Key | What it does | Use it when | Leave it out when |
|---|---|---|---|
| `deploy.resources.limits` | Caps CPU, memory and processes; `mem_limit` and `cpus` set the same limits per service, and where a service sets both, the values must agree [4] ([compose.md](compose.md) section 7 says so for `pids_limit`). An implementation may ignore `deploy` [12]. | A production host, in the override file. The container a coding agent runs in ([agent-containers.md](agent-containers.md) section 6). In development, a memory limit sized to the host for a service known to grow, as Elastic's test setup does with `mem_limit` [45], [34]: Docker warns an unlimited container can "bring the entire system down" [35]. Write the limit as `mem_limit` and `cpus` as the examples do ([agent-container-example.md](agent-container-example.md)), or as `deploy.resources.limits`; v5.6.0 applies both [33]. Section 7 of this file says what Docker Compose v5.6.0 applies. | Blanket limits in development. On Docker Desktop the VM already caps memory, at half the host's by default [36]. |
| `logging` | Sets the log driver and its options [4]. Docker's default driver, `json-file`, keeps every line: "By default, no log-rotation is performed", which "can lead to disk space exhaustion" [37]. | A host that runs the stack for weeks: switch the daemon to the `local` driver, which Docker recommends and which rotates by default [37], then re-create the containers, since existing ones keep the driver they were created with [37], or set `max-size` for `json-file`, since `max-file` alone does nothing [38]. Per service, `logging.options` takes the driver's own options as key-value pairs [4]. | Development, where containers live for hours. |

### Keys to avoid

| Key | Why |
|---|---|
| `container_name` | "Compose does not scale a service beyond one container if the Compose file specifies a `container_name`" [3]. A Compose maintainer says the key is "mostly used for backward compatibility when user migrate from hand-managed stack to compose" [39], and a fixed name breaks a second copy of the project, such as one in another git worktree. The exception is a tool that addresses its containers by name and puts the project's name inside it, as DDEV does with `ddev-${DDEV_SITENAME}-db` [26]. |
| `links` | Not needed for services to talk (the network table above). |
| `version` | Obsolete (section 3). |
| `privileged` | Gives the container power over the host ([compose.md](compose.md) section 8). |

[compose.md](compose.md) section 5 says when to use `develop.watch`.

## 5. Development and one production host

Docker's advice for production is a second file, such as `compose.production.yaml`, that "only
needs to include the changes" [24]. On one production host, that file changes these keys:

| Key | Development (`compose.yaml`) | Production host (the override file) |
|---|---|---|
| `build` / `image` | `build: .` | the image CI pushed, by digest ([compose.md](compose.md) section 9) |
| code bind mounts | allowed | removed [24] |
| `env_file` | `.env` | none ([compose.md](compose.md) section 9) |
| `restart` | none by default; [section 4](#4-service-keys) says when development takes `unless-stopped` | `always` or `unless-stopped` [24] |
| `deploy.resources.limits` | none, or memory for a service known to grow | set per service |
| log rotation | not needed | the `local` driver, or `max-size`; re-create the containers after a switch [37] |

The override drops `build`, `env_file` and the code bind mounts with the tags
[compose.md](compose.md) section 2 names; without them `build` and the bind mount stay, and
`env_file` stops the start on a host with no `.env`, since its `required` defaults to `true` [4].

## 6. Common mistakes

- **`docker compose down -v` on a stack with a database.** `-v` "permanently deletes the stored
  data" [42]; plain `down` keeps named volumes [41].

Each key's "Leave it out when" cell in section 4 names its mistake; readiness and published ports
are [compose.md](compose.md) sections 3 and 7.

## 7. Where these rules stop holding

- **Another Compose tool or release.** The keys above are as Docker Compose v5.6.0 reads them [1].
  The specification lets a tool ignore the whole `deploy` section [12], and v5.6.0 applies, among
  others, `resources.limits`, memory and device reservations, and `restart_policy`'s `condition`
  and `max_attempts` [33]. Check what
  your tool applies before you rely on the rest of `deploy`.
- **More than one host.** Compose runs the stack on one host; [compose.md](compose.md) section 9
  says where Docker points for more.
- **A service that cannot take every hardening key**, such as one whose image runs as root, is
  [compose.md](compose.md) section 10.

## 8. Sources

Checked 2026-10-16 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Docker — Docker Compose releases, v5.6.0 — https://github.com/docker/compose/releases/tag/v5.6.0
- [2] Docker — Networking in Compose — https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/networking.md — checked 2026-10-17
- [3] Compose Specification — Services top-level element (05-services.md) — https://github.com/compose-spec/compose-spec/blob/main/05-services.md
- [4] Compose Specification — container attributes (container_spec.md) — https://github.com/compose-spec/compose-spec/blob/main/container_spec.md — checked 2026-10-17
- [5] Docker — Compose file reference: volumes top-level element — https://github.com/docker/docs/blob/main/content/reference/compose-file/volumes.md
- [6] Docker — Compose: include — https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/multiple-compose-files/include.md
- [7] Docker — Compose extensions — https://github.com/docker/docs/blob/main/content/includes/compose/extension.md
- [8] Docker — Compose file reference: fragments — https://github.com/docker/docs/blob/main/content/reference/compose-file/fragments.md
- [9] Docker — Compose file reference: version and name — https://github.com/docker/docs/blob/main/content/reference/compose-file/version-and-name.md
- [10] Compose Specification — build (build.md) — https://github.com/compose-spec/compose-spec/blob/main/build.md
- [11] Docker — Using profiles with Compose — https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/profiles.md
- [12] Docker — Compose file reference: services — https://github.com/docker/docs/blob/main/content/reference/compose-file/services.md
- [13] Docker — docker container run reference, --add-host — https://github.com/docker/docs/blob/main/data/cli/engine/docker_container_run.yaml
- [14] Docker — Collect Docker metrics with Prometheus — https://github.com/docker/docs/blob/main/content/manuals/engine/daemon/prometheus.md
- [15] Docker — Host network driver — https://github.com/docker/docs/blob/main/content/manuals/engine/network/drivers/host.md
- [16] Christian Lück — [BUG] compose watch stops services using `links` and `depends_on` with `restart: true` (GitHub, docker/compose issue #12814, 2025; case) — https://github.com/docker/compose/issues/12814
- [17] Docker — Volumes — https://github.com/docker/docs/blob/main/content/manuals/engine/storage/volumes.md
- [18] Docker — PostgreSQL guide — https://github.com/docker/docs/blob/main/content/guides/postgresql.md
- [19] Docker — Bind mounts — https://github.com/docker/docs/blob/main/content/manuals/engine/storage/bind-mounts.md
- [20] Docker — Control startup and shutdown order in Compose — https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/startup-order.md
- [21] Compose Specification — workload attributes (workload_spec.md) — https://github.com/compose-spec/compose-spec/blob/main/workload_spec.md
- [22] Nick Janetakis — docker-flask-example, .env.example (GitHub, nickjj/docker-flask-example, no date; case) — https://github.com/nickjj/docker-flask-example/blob/main/.env.example
- [23] Docker — Start containers automatically — https://github.com/docker/docs/blob/main/content/manuals/engine/containers/start-containers-automatically.md
- [24] Docker — Use Compose in production — https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/production.md
- [25] Han Qiao — fix: change restart policy to unless stopped (GitHub, supabase/cli pull request #4603, 2025; case) — https://github.com/supabase/cli/pull/4603
- [26] DDEV — app_compose_template.yaml (GitHub, ddev/ddev, no date; case) — https://github.com/ddev/ddev/blob/main/pkg/ddevapp/app_compose_template.yaml
- [27] Linux kernel — no_new_privs — https://github.com/torvalds/linux/blob/master/Documentation/userspace-api/no_new_privs.rst
- [32] Truffle — compose: pids_limit=256 too tight for default-parallelism Rust linking on 16-core container (GitHub, ghostwright/phantom issue #135, 2026; case) — https://github.com/ghostwright/phantom/issues/135
- [33] Docker — Docker Compose source, pkg/compose/create.go, v5.6.0 — https://github.com/docker/compose/blob/v5.6.0/pkg/compose/create.go
- [34] Elastic — Elasticsearch Docker Compose test environment, .env (GitHub, elastic/elasticsearch, no date; case) — https://github.com/elastic/elasticsearch/blob/main/docs/reference/setup/install/docker/.env
- [35] Docker — Resource constraints — https://github.com/docker/docs/blob/main/content/manuals/engine/containers/resource_constraints.md
- [36] Docker — Docker Desktop settings — https://github.com/docker/docs/blob/main/content/manuals/desktop/settings-and-maintenance/settings.md
- [37] Docker — Configure logging drivers — https://github.com/docker/docs/blob/main/content/manuals/engine/logging/configure.md — checked 2026-10-17
- [38] Docker — JSON File logging driver — https://github.com/docker/docs/blob/main/content/manuals/engine/logging/drivers/json-file.md
- [39] Nicolas De loof — comment in "`-p` project name does not isolate container names when `container_name` is specified" (GitHub, docker/compose issue #13553, 2026; opinion) — https://github.com/docker/compose/issues/13553#issuecomment-3794259030 — checked 2026-10-17
- [41] Docker — docker compose down reference — https://github.com/docker/compose/blob/main/docs/reference/compose_down.md
- [42] Docker — Docker Compose Quickstart — https://github.com/docker/docs/blob/main/content/manuals/compose/gettingstarted.md
- [43] Compose Specification — Configs top-level element (08-configs.md) — https://github.com/compose-spec/compose-spec/blob/main/08-configs.md
- [44] Docker — Specify a project name — https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/project-name.md
- [45] Elastic — Elasticsearch Docker Compose test environment, docker-compose.yml (GitHub, elastic/elasticsearch, no date; case) — https://github.com/elastic/elasticsearch/blob/main/docs/reference/setup/install/docker/docker-compose.yml
- [46] Compose Specification — Models top-level element (models.md) — https://github.com/compose-spec/compose-spec/blob/de28432802a367d650bd4ad6748b19491b6cf986/models.md
- [47] Compose Specification — Jobs top-level element (jobs.md) — https://github.com/compose-spec/compose-spec/blob/de28432802a367d650bd4ad6748b19491b6cf986/jobs.md
- [48] Moby project — `daemon/daemon.go`, the `restore` function that starts containers with a restart policy when the daemon starts — https://github.com/moby/moby/blob/3f38b15147b14ce0ce7b11558a1aa9e9f14db103/daemon/daemon.go
- [49] Moby project — `daemon/internal/restartmanager/restartmanager.go`, the delay between restarts — https://github.com/moby/moby/blob/3f38b15147b14ce0ce7b11558a1aa9e9f14db103/daemon/internal/restartmanager/restartmanager.go
