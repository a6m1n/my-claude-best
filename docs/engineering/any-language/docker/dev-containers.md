# Dev containers

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. What a dev container is](#2-what-a-dev-container-is)
- [3. When it pays off, and when it is over-engineering](#3-when-it-pays-off-and-when-it-is-over-engineering)
- [4. The alternatives](#4-the-alternatives)
- [5. Writing one](#5-writing-one)
- [6. The fields of devcontainer.json](#6-the-fields-of-devcontainerjson)
- [7. Where these rules stop holding](#7-where-these-rules-stop-holding)
- [8. Sources](#8-sources)

## 1. Purpose and the one rule

This file is for everyone who decides whether a repository gets a dev container, or writes one:
people and AI agents alike. A container an AI agent works in, and the security of dev containers,
are [agent-containers.md](agent-containers.md); the image a person works in is
[images.md](images.md) section 12. One topic is covered only in part: a check that shows a
`devcontainer.json` follows these rules. Some rules route to checks in other files, such as
`--frozen-lockfile` in CI and the merged-configuration read
([agent-containers.md](agent-containers.md) section 9); for the rest, a check is not covered yet.

The one rule: **add a dev container when the part of the environment a lock file does not record
differs between the team's machines and matters to the code; leave it out when the lock files and
Compose already make the machines alike.**

Why it matters:

- A lock file and a pinned interpreter already make the packages the same everywhere. uv's lock
  file covers every operating system, architecture and Python version, "allowing for consistent and
  reproducible installations across machines" [1], and `.python-version` sets the interpreter [2].
- They do not record the rest. "The linkage between the Python package and its system dependency
  is not recorded by the packaging system" [3]; the interpreter uv installs still needs the host's
  glibc or musl [4]; and a package with no wheel for a teammate's platform is built with that
  machine's compiler and headers [5]. A dev container fixes this layer.
- It costs upkeep, slower files on macOS and Windows, and editor support that varies (section 3),
  and this practice's search found no controlled or independent measurement of its payoff; the
  reports that exist are vendor-run or self-reported. DORA's 2024 report, for one, has no finding
  on development environments or containers [6].

## 2. What a dev container is

The specification calls it "a container in which a user can develop an application" [7]. It is
described in `.devcontainer/devcontainer.json` (or `.devcontainer.json`, or one folder deeper for
several configurations) [7], and it is not the build or the deployment: it is where you develop
"before you are ready to build" [8]. Its tools differ from the service image's on purpose: "you may
not want to include tools in a deployment image that you use during development" [7].

The specification promises a "repeatable development environment" [7] and "consistency to avoid
environment specific problems across developers and centralized build and test automation
services" [9]. That is not the same bytes on every rebuild: nothing guarantees that a rebuild next
month gives the same image unless its inputs are pinned ([images.md](images.md) section 4); that
limit is this practice's own reading.

VS Code, Visual Studio, IntelliJ IDEA, the `devcontainer` command-line tool, GitHub Codespaces,
DevPod and others read the file [10], but not all of them read every field (section 7).

## 3. When it pays off, and when it is over-engineering

| The situation | Dev container? | Why |
|---|---|---|
| The code needs system libraries or compilers, and their versions differ between the team's machines | Yes | That is the layer a lock file does not record [3]. For example, `psycopg` without its `binary` extra needs libpq from the operating system, while `psycopg[binary]` brings its own [11]. |
| Only the versions of command-line tools differ between the machines | No (this practice's own call): a tool-version manager pins them without a container (section 4) | mise records the exact versions in a `mise.lock` committed beside `mise.toml` [49]. |
| A dependency has no wheel for a teammate's operating system or CPU | Yes | uv then builds it from source with that machine's compiler and headers [5]. |
| The shared parts are services: a database, a cache | No | Compose runs the same type and version of each service on every machine, as 12-factor asks [12]; see [compose.md](compose.md). |
| The wheels are self-contained and the services run in Compose | No | A lock file, a pinned interpreter and Compose already make the machines alike (section 4). |
| Only one person uses the dev container | No | No one else gains from it, and an unused configuration drifts from CI. In 2025-2026 graphprotocol/contracts removed one whose author believed they were the only user [13]; at yapms, a contributor who did not use it asked whether anyone did, and removed it [16]; powertools-lambda-python removed its cloud environments for low and unknown usage [15]; Bencher removed one that had drifted from CI (pull request merged 2026-10-17) [14]. Each is one project, not a measure. |
| A small project on GitHub Codespaces, in the languages it provides | No custom one | GitHub's default configuration "is a good option" there [17]. |
| The team uses editors without dev container support | Keep it optional (this practice's own call): the setup of section 4 must still work without it | Support differs by tool [10], and the `devcontainer` command-line tool does not forward ports [18]. |
| The code talks to USB or Bluetooth hardware | No, on Windows and macOS | The device cannot be passed into the container there [19]. |
| An AI agent works in it without approvals, or the repository is not trusted | Not this file | [agent-containers.md](agent-containers.md) sections 3 and 9. |

What a dev container costs:

- **Files on macOS and Windows.** Bind mounts are slower "since macOS and Windows run containers
  in a VM" [20]. One measurement of `npm install` found a plain bind mount 2.5 to 2.8 times slower
  than the host on Docker Desktop, and about as fast as the host with a named volume for the
  dependency folder [21]; it is one author's test on one machine. On Windows, keep the code in the
  WSL file system: "Performance is much higher when files are bind-mounted from the Linux
  filesystem" [22].
- **The licence.** Docker Desktop is free for companies under 250 employees and under $10 million
  in annual revenue, for personal use, education and non-commercial open source; other
  professional use needs a paid subscription [23]. Docker Engine on Linux stays open source [23].
- **Upkeep.** The image, its tools and the editor extensions need updates, or they drift from
  what CI runs [14], [15].

## 4. The alternatives

| Alternative | What it makes the same | When it wins |
|---|---|---|
| A lock file and a pinned interpreter (`uv.lock`, `.python-version`) | Package versions and the interpreter build [1], [2]; `--locked` makes a stale lock fail instead of drift [24] | A project whose lock file and Compose already make the machines alike (row 5 of section 3). Apache Airflow runs its unit tests in a local virtualenv, which it recommends managing with uv [44], and keeps containers for integration tests with services and for reproducing CI [25]. Airflow's own page rates this route as difficult for team synchronization [25], which is the gap a dev container fills (section 3, first row). |
| A tool-version manager (`mise.toml` with a committed `mise.lock`) | The versions of command-line tools [49], not system libraries, which mise installs only machine-wide, with the host's package manager [50] | Only a tool's version differs between the machines (this practice's own call). |
| Compose for the services | The type and version of each backing service [12] | Every project with a database or a cache, with or without a dev container (this practice's own call: one Compose file the team keeps anyway runs the same services on every machine, and 12-factor asks every deploy to use "the same type and version of each of the backing services" [12]). |
| A Nix-based shell | System packages as well, but only once its package set is pinned: a shell is "not reproducible" until then [26] | The team must pin system packages without a container, and pins nixpkgs to one commit, since a shell is not reproducible until then [26]. |
| A cloud environment such as Codespaces | The same image for everyone, built on the provider's machines | The team wants no local setup (this practice's own call: the container is built and runs on the provider's machines, so nothing is installed locally). GitHub: if creating one takes over 2 minutes, prebuilds are likely to pay off [27]. |

## 5. Writing one

- **Put tools in the image, not in `postCreateCommand`.** A Dockerfile uses the build cache and
  rebuilds faster [28]. Steps that need the workspace, which a Dockerfile cannot see [28], go in
  `updateContentCommand`: it runs at least once, and cloud services run it again to refresh cached
  or prebuilt containers [33].
- **When you build on a base image, pin it in the Dockerfile, not in `devcontainer.json`.**
  Renovate's `docker:pinDigests` preset turns digest pinning off for the `devcontainer`
  manager [29], so the bot adds no digest to `devcontainer.json`; in the Dockerfile the preset
  applies and the bot keeps the pin current ([images.md](images.md) section 4).
- **Pin what a Feature installs.** Commit `devcontainer-lock.json`, and set the tool's own
  `version` option: the lock records the Feature's version and checksum, not the tool it
  installs [36], and official Features install `lts` or `latest` by default [37], [35]
  ([agent-containers.md](agent-containers.md) section 9: `--frozen-lockfile` in CI).
- **Prebuild the image when creating the container is slow.** VS Code recommends pre-building with
  the `devcontainer` command-line tool for a faster start and pinned tools [30]; GitHub's threshold
  for Codespaces prebuilds is 2 minutes [27].
- **Put in what everyone needs, not personal preferences.** GitHub: "You should only include things
  that everyone working on your codebase needs as standard elements of the development environment,
  not things that are personal preferences" [17]. Themes and shell setup go in dotfiles [17].
- **Set up the user as [images.md](images.md) section 12 asks for a development container**;
  `updateRemoteUserUID` does the UID part (section 6).
- **Keep the virtual environment out of the mounted code, on every OS.** uv's guide says "it is
  important _not_ to include the project virtual environment (`.venv`) in the mount, because the
  virtual environment is platform specific" [47]. Set `UV_PROJECT_ENVIRONMENT` to a directory the
  image gives the user, outside the workspace [48]; on macOS and Windows that also keeps the
  busiest folder off the slow shared files.
- **Put another busy folder, such as `node_modules`, on a named volume on macOS and Windows**, as
  VS Code shows [20]. A new volume belongs to root: VS Code hands it to its non-root user with
  `sudo chown` [20], so the image needs `sudo` for that user, and the step must run before
  anything installs into the folder, in `onCreateCommand` [33].
- **Know what the editor brings in from your machine**: [agent-containers.md](agent-containers.md)
  section 9 lists it, and says why an agent's container gets none of it.

The smallest `devcontainer.json` for a Python service. One part is left out here: the
`Dockerfile` it names, which pins its frontend and turns its build checks into errors
([images.md](images.md) section 7), starts from a pinned Python image and copies uv from a pinned
uv image ([images.md](images.md) section 4), installs the system libraries the code needs, and
creates the user `dev` with a home directory ([images.md](images.md) section 12).

```jsonc
// .devcontainer/devcontainer.json
{
  "name": "acme",
  // The tools come from a Dockerfile, so a rebuild reuses its cached layers
  // (dev-containers.md section 5).
  "build": { "dockerfile": "Dockerfile" },
  // A non-root user; on Linux its UID is changed to yours for the mounted code
  // (dev-containers.md section 5).
  "remoteUser": "dev",
  // The virtual environment lives outside the mounted code, since it is platform
  // specific (dev-containers.md section 5).
  "containerEnv": { "UV_PROJECT_ENVIRONMENT": "/home/dev/.venv" },
  // Needs the code, which the Dockerfile cannot see; a prebuild runs it, so a new container
  // starts synced (dev-containers.md section 6). --locked stops on a stale lock (images.md
  // section 11).
  "updateContentCommand": "uv sync --locked"
}
```

It is good because it holds only what everyone needs: the tools live in the image, the one step
that needs the code runs after the code is mounted, and nothing in it is a personal setting.

## 6. The fields of devcontainer.json

A configuration needs one of `image`, `build.dockerfile` or `dockerComposeFile` with `service`;
every other field is optional [33]. The table leaves out these fields of the reference:
`build.options`, `otherPortsAttributes`, `overrideFeatureInstallOrder`, `userEnvProbe` and
`waitFor` [33].

| Field | What it does | Use it when | Leave it out when |
|---|---|---|---|
| `name` | The name the tool shows for the dev container [33]. | Any configuration; it changes only what the UI shows. | No case found. |
| `image` | Runs a ready image [33]. | A prebuilt image that already holds the tools [30]; pin its digest by hand, since Renovate's preset adds no digest here (section 5), or a one-line Dockerfile `FROM <image>@sha256:...`, so Renovate keeps the pin current (section 5). | You add system packages: use `build`, and pin the base image in the Dockerfile (section 5). |
| `build` (`dockerfile`, `context`, `args`, `target`, `cacheFrom`) | Builds the image from a Dockerfile; `cacheFrom` names images to use as a cache [33]. | The code needs tools or system libraries (section 3). `target` when a development stage of the service's own Dockerfile can keep the system libraries the same as the image CI tests (this practice's own call) [33], [38]. | A prebuilt image already has them. |
| `dockerComposeFile`, `service`, `runServices` | Uses Compose: the files, the service you work in (required with Compose), and which services to start (all by default) [33]. | The code needs its services running beside it. VS Code suggests extending the project's Compose file with a second file rather than copying it [28]. | One container is enough. |
| `features` | Adds Features: install scripts that run as root while the image builds [34]. | A development-only tool with install code you do not want to write, such as Docker-in-Docker or a cloud CLI; pin it as section 5 says. | System packages, and tools the service image or CI also need: one Dockerfile line keeps them in one place. That choice is this practice's own; the owners present Features and Dockerfiles as alternatives [38]. Never a Feature from a publisher you would not trust with root in your build: publishing is, by design, "not centrally controlled" [39]. |
| `customizations` | Settings for one tool, such as VS Code's extensions [33]. | What everyone needs [17]. | Personal preferences [17]. |
| `forwardPorts`, `portsAttributes` | Forwards container ports to the local machine [33]. | A port the tool cannot forward on its own, or a service in another Compose container [33]. | You start the container with the `devcontainer` command-line tool, which does not forward ports [18]: publish the port with `appPort`, with the application listening on `0.0.0.0` [46], [33], or, with a Compose-based configuration, with Compose `ports`. |
| `appPort` | Ports "published locally when the container is running"; unlike `forwardPorts`, the application may need to listen on `0.0.0.0` [33]. | You start the container with the `devcontainer` command-line tool, which does not forward ports: a comment on the issue says `appPort` "works as a workaround" [46]. | Your editor forwards ports with `forwardPorts`, which the reference recommends in most cases [33], or Compose publishes them. |
| `initializeCommand` | Runs on the host, before the container exists [33]. | Almost never ([agent-containers.md](agent-containers.md) section 9). | Anything that can run in the container. |
| `onCreateCommand`, `updateContentCommand` | Run in the container before user secrets exist; a prebuild runs them [33], [27]. | Steps a prebuild can cache, such as installing dependencies. | Steps that need your secrets. |
| `postCreateCommand` | Runs once the container is assigned to you [33]. | Steps that need your secrets [33]. | Installing tools: they belong in the image [28]. |
| `postStartCommand`, `postAttachCommand` | Run on each start, and each time a tool attaches [33]. | Something that must run every time, such as a background process. | One-time setup. |
| `remoteUser`, `containerUser` | The user the tool works as, and the user the whole container runs as [33]. | `remoteUser` set to a non-root user. | `containerUser`, unless every process must run as that user. |
| `updateRemoteUserUID` | On Linux, changes the user's UID to yours; `true` by default [33]. | On Linux with a bind-mounted workspace: keep the default `true` [33]. | The engine maps UIDs itself, as rootless Docker does ([images.md](images.md) section 12), or the workspace is not a bind mount: the specification lets a tool skip the change there [45]. Where the image already has a user with your UID, the change does not happen ([images.md](images.md) section 12). |
| `mounts` | Extra mounts, in `docker --mount` syntax [33]. | A named volume for a dependency folder on macOS and Windows [20]. | A host folder with credentials ([agent-containers.md](agent-containers.md) section 4). |
| `containerEnv`, `remoteEnv` | Variables for the whole container, or for the tool's processes only; the specification recommends `containerEnv` "as much as possible" [33]. | `containerEnv` for a static value, since changing it needs a rebuild [33]; `remoteEnv` when the value changes without a rebuild, and always with Compose, where `devcontainer.json` supports only `remoteEnv` [40]. | No case found where a variable is too much. |
| `runArgs` | Extra `docker run` arguments [33]. | Rarely: a flag no field covers, such as `--device-cgroup-rule` [33]. | The flag has a field: write `capAdd` and `securityOpt` instead of `--cap-add` and `--security-opt` in `runArgs`, because the specification defines those fields for every orchestrator [33]. CodeSandbox does not support adding capabilities [10]. |
| `privileged` | Runs the container in privileged mode; it is "Required for things like Docker-in-Docker, but has security implications" [33]. | Docker-in-Docker [33]. | By default. A Feature can turn on this field, `capAdd`, `init` or `securityOpt` for you [34], as Docker-in-Docker sets `privileged` [35], so review the Features too ([agent-containers.md](agent-containers.md) section 9). |
| `capAdd` | Adds Linux capabilities a container does not get by default; "Most often used to add the `ptrace` capability" for debuggers [33]. | A debugger needs `ptrace`. | By default. |
| `securityOpt` | Sets container security options, such as `seccomp=unconfined` [33]. | A debugger needs `ptrace`: the reference's `runArgs` example adds `seccomp=unconfined` so that "ptrace based debuggers like C++" work [33]. | By default. |
| `init` | "Cross-orchestrator way to indicate whether the tini init process should be used to help deal with zombie processes" [33]. | Where [images.md](images.md) section 6 asks for an init. | Where images.md section 6 asks for none. |
| `workspaceFolder`, `workspaceMount` | Where the code is mounted (`workspaceMount`, with `image` or `build` only) and opened [33]; the mount should be the repository root, "so that source control operations work correctly" [7]. | A Compose-based configuration, where `workspaceFolder` defaults to `/` [33]: set it to the path the Compose file mounts the code at, as [agent-container-example.md](agent-container-example.md) does. A monorepo: open the subfolder, mount the root. | A one-project repository with `image` or `build`, where `workspaceFolder` defaults to the code's mount [33]. |
| `shutdownAction`, `overrideCommand` | Whether closing the tool stops the container, and whether a sleep loop replaces the image's command [33]. `overrideCommand` defaults to `true` with `image` or `build` and to `false` with Compose; `shutdownAction` defaults to `stopContainer`, or `stopCompose` with Compose [33]. | `overrideCommand: false` when the image's own command must run; `shutdownAction` when closing the editor should leave the container up [33]. | The default for your configuration's type already does it. |
| `hostRequirements` | The CPU, memory and storage the project needs; cloud services pick a machine from it, other tools only warn [33]. | Codespaces. | Local-only work. |

## 7. Where these rules stop holding

- **Tool support.** Codespaces ignores bind mounts other than the Docker socket, and DevPod lists
  fields it does not support, such as `waitFor` (in a page last changed in 2023) [10], [41]. Check
  the fields your team's tools read.
- **A Compose-based dev container.** The `devcontainer` command-line tool cannot push one, so
  build and push its image with `docker buildx` instead (`doBuild` in CLI 0.89.0) [42].
- **Hardware.** USB and Bluetooth devices cannot be passed in on Windows and macOS [19].
- **An untrusted repository or an agent without approvals.** A dev container is not the boundary
  there: [agent-containers.md](agent-containers.md) sections 3 and 9.

## 8. Sources

Checked 2026-10-16 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Astral — uv: Project structure and files, uv 0.13.1 — https://github.com/astral-sh/uv/blob/0.13.1/docs/concepts/projects/layout.md
- [2] Astral — uv: Working on projects, uv 0.13.1 — https://github.com/astral-sh/uv/blob/0.13.1/docs/guides/projects.md
- [3] Python Packaging Authority — Python Packaging User Guide: Supporting downstream packaging — https://github.com/pypa/packaging.python.org/blob/main/source/discussions/downstream-packaging.rst
- [4] Astral — python-build-standalone: Running distributions, release 20261013 — https://github.com/astral-sh/python-build-standalone/blob/20261013/docs/running.md
- [5] Astral — uv: Resolution, uv 0.13.1 — https://github.com/astral-sh/uv/blob/0.13.1/docs/concepts/resolution.md
- [6] Google Cloud DORA — Accelerate State of DevOps Report 2024 (DORA, 2024; research) — https://github.com/dora-team/dora.dev/blob/main/hugo/content/research/2024/dora-report/2024-dora-accelerate-state-of-devops-report.pdf
- [7] Development Containers — Specification: devcontainer reference — https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainer-reference.md
- [8] Microsoft — VS Code docs: Dev Containers FAQ — https://github.com/microsoft/vscode-docs/blob/main/docs/devcontainers/faq.md
- [9] Development Containers — Specification README — https://github.com/devcontainers/spec/blob/main/README.md
- [10] Development Containers — containers.dev: Supporting tools — https://github.com/devcontainers/devcontainers.github.io/blob/abccd5b45734af15c1710aea4603bab1a43ea77a/supporting.md
- [11] Psycopg — Psycopg 3 docs: Installation, 3.3.6 — https://github.com/psycopg/psycopg/blob/3.3.6/docs/basic/install.rst
- [12] The Twelve-Factor App — X. Dev/prod parity — https://github.com/twelve-factor/twelve-factor/blob/main/content/dev-prod-parity.md
- [13] Rembrandt Kuipers — Remove dev container config from repo (for now) (GitHub, graphprotocol/contracts pull request #1231, 2025; case) — https://github.com/graphprotocol/contracts/pull/1231
- [14] Everett Pompeii — Remove the dev container (GitHub, bencherdev/bencher pull request #1214, 2026; case) — https://github.com/bencherdev/bencher/pull/1214 — checked 2026-10-17
- [15] Leandro Damascena — Maintenance: Remove cloud development environment configurations (Gitpod, Codespaces, devcontainer) (GitHub, aws-powertools/powertools-lambda-python issue #7883, 2026; case) — https://github.com/aws-powertools/powertools-lambda-python/issues/7883
- [16] Jacob Enders — Remove Devcontainers (GitHub, yapms/yapms pull request #2501, 2026; case) — https://github.com/yapms/yapms/pull/2501
- [17] GitHub — GitHub Docs: Introduction to dev containers — https://github.com/github/docs/blob/main/content/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers.md
- [18] davidkron — forwardPorts configuration option not working (GitHub, devcontainers/cli issue #186, 2022; case) — https://github.com/devcontainers/cli/issues/186 — checked 2026-10-17
- [19] Home Assistant — Developer docs: Set up development environment — https://github.com/home-assistant/developers.home-assistant/blob/master/docs/development_environment.mdx
- [20] Microsoft — VS Code docs: Improve container disk performance — https://github.com/microsoft/vscode-docs/blob/main/remote/advancedcontainers/improve-performance.md — checked 2026-10-17
- [21] Paolo Mainardi — Docker on macOS performance, 2025 update (paolomainardi.com, 2025; research) — https://github.com/paolomainardi/paolomainardi.com/blob/main/src/content/posts/10-docker-macos-perf-update/index.md
- [22] Docker — Docker Desktop WSL 2 best practices — https://github.com/docker/docs/blob/main/content/manuals/desktop/features/wsl/best-practices.md
- [23] Docker — Docker Desktop license agreement summary — https://github.com/docker/docs/blob/main/content/manuals/subscription-billing/desktop-license.md
- [24] Astral — uv: Locking and syncing, uv 0.13.1 — https://github.com/astral-sh/uv/blob/0.13.1/docs/concepts/projects/sync.md
- [25] Apache Airflow — Contributing docs: development environments — https://github.com/apache/airflow/blob/main/contributing-docs/06_development_environments.rst
- [26] NixOS — nix.dev: Ad hoc shell environments — https://github.com/NixOS/nix.dev/blob/master/source/tutorials/first-steps/ad-hoc-shell-environments.md
- [27] GitHub — GitHub Docs: About GitHub Codespaces prebuilds — https://github.com/github/docs/blob/main/content/codespaces/prebuilding-your-codespaces/about-github-codespaces-prebuilds.md
- [28] Microsoft — VS Code docs: Create a Dev Container — https://github.com/microsoft/vscode-docs/blob/main/docs/devcontainers/create-dev-container.md
- [29] Mend — Renovate: docker presets (docker.preset.ts) — https://github.com/renovatebot/renovate/blob/main/lib/config/presets/internal/docker.preset.ts
- [30] Microsoft — VS Code docs: Developing inside a Container — https://github.com/microsoft/vscode-docs/blob/main/docs/devcontainers/containers.md
- [33] Development Containers — containers.dev: devcontainer.json reference — https://github.com/devcontainers/devcontainers.github.io/blob/abccd5b45734af15c1710aea4603bab1a43ea77a/_implementors/json_reference.md
- [34] Development Containers — Specification: Features — https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainer-features.md
- [35] Development Containers — Features: docker-in-docker devcontainer-feature.json — https://github.com/devcontainers/features/blob/main/src/docker-in-docker/devcontainer-feature.json
- [36] Development Containers — Specification: lock file — https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainer-lockfile.md
- [37] Development Containers — Features: node devcontainer-feature.json — https://github.com/devcontainers/features/blob/main/src/node/devcontainer-feature.json
- [38] Chuck Lantz — Using Images, Dockerfiles, and Docker Compose (containers.dev, 2022; opinion) — https://github.com/devcontainers/devcontainers.github.io/blob/abccd5b45734af15c1710aea4603bab1a43ea77a/_posts/2022-12-16-dockerfile.md
- [39] Development Containers — Specification: Features distribution — https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainer-features-distribution.md
- [40] Microsoft — VS Code docs: Environment variables — https://github.com/microsoft/vscode-docs/blob/main/remote/advancedcontainers/environment-variables.md
- [41] Loft Labs — DevPod docs: devcontainer.json — https://github.com/loft-sh/devpod/blob/main/docs/pages/developing-in-workspaces/devcontainer-json.mdx
- [42] Development Containers — devcontainer CLI source, src/spec-node/devContainersSpecCLI.ts, 0.89.0 — https://github.com/devcontainers/cli/blob/v0.89.0/src/spec-node/devContainersSpecCLI.ts
- [44] Apache Airflow — Contributing docs: local virtualenv — https://github.com/apache/airflow/blob/main/contributing-docs/07_local_virtualenv.rst
- [45] Development Containers — containers.dev: Development Container Specification, Container Creation — https://github.com/devcontainers/devcontainers.github.io/blob/abccd5b45734af15c1710aea4603bab1a43ea77a/_implementors/spec.md
- [46] candidtim — comment in "forwardPorts configuration option not working" (GitHub, devcontainers/cli issue #186, 2026; opinion) — https://github.com/devcontainers/cli/issues/186#issuecomment-4718235755 — checked 2026-10-17
- [47] Astral — uv: Using uv in Docker, uv 0.13.1 — https://github.com/astral-sh/uv/blob/0.13.1/docs/guides/integration/docker.md
- [48] Astral — uv: Configuring projects, uv 0.13.1 — https://github.com/astral-sh/uv/blob/0.13.1/docs/concepts/projects/config.md
- [49] mise — Lockfile (mise.lock), v2026.10.12 — https://github.com/jdx/mise/blob/v2026.10.12/docs/dev-tools/mise-lock.md
- [50] mise — Bootstrap packages, v2026.10.12 — https://github.com/jdx/mise/blob/v2026.10.12/docs/bootstrap/packages/index.md
