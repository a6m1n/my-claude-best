# Rules for coding agents in containers

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. What a container protects, and what it does not](#2-what-a-container-protects-and-what-it-does-not)
- [3. Choose the isolation by trust](#3-choose-the-isolation-by-trust)
- [4. Credentials: give the agent nothing it must not leak](#4-credentials-give-the-agent-nothing-it-must-not-leak)
- [5. Network: one way out, through a proxy](#5-network-one-way-out-through-a-proxy)
- [6. The container process](#6-the-container-process)
- [7. Files and git](#7-files-and-git)
- [8. Docker inside the agent's container](#8-docker-inside-the-agents-container)
- [9. Dev containers](#9-dev-containers)
- [10. The agent's own settings are not the boundary](#10-the-agents-own-settings-are-not-the-boundary)
- [11. Where it stops holding](#11-where-it-stops-holding)
- [12. Sources](#12-sources)

## 1. Purpose and the one rule

This file is for everyone who gives an AI coding agent a container to work in: a dev container,
a container that runs the agent without approvals, or a sandbox service. People and AI agents read
it before they set one up or change one. How an image is built is [images.md](images.md); the
Compose keys it uses are [compose.md](compose.md). The worked case is Claude Code; section 11
says what changes for other agents.

The one rule: **a container limits what an agent can damage; it does not stop the agent from
leaking what it can read. Give the agent nothing it must not leak and nothing it must not
change.**

Why it matters:

- Agents follow instructions hidden in what they read. In 2026 studies, coding agents set to
  accept their own actions carried out an instruction planted in a GitHub issue in 41% to 79% of
  runs, depending on the agent. For one agent, its own sandbox and network isolation rejected none
  of the attacks that stayed inside the workspace.
- The vendors say it about their own containers. Anthropic: run without approvals, a dev
  container does "not prevent a malicious project from exfiltrating anything accessible inside the
  container, including the Claude Code credentials". GitHub calls its agent firewall not "a
  comprehensive security solution". Microsoft: a dev container's "boundary depends on the container
  configuration".
- Researchers have sent data out through every kind of allowed address: the model provider's own
  API, a package registry, a model hub's download counter, GitHub, a cloud subdomain anyone can
  rent.

## 2. What a container protects, and what it does not

Name the three conditions before you choose anything. An agent that has private data, reads
untrusted content and can send data out can be made to leak that data; Simon Willison calls the
combination the "lethal trifecta". A coding agent always reads untrusted content: issues, pull
requests, web pages, dependencies, and the repository itself. So each setup decides the other two:
what the agent can read, and where it can send it.

| A container, set up as this file says, protects | It does not protect |
|---|---|
| host files outside the mounted workspace | the mounted workspace: the agent's edits land on your disk |
| host processes, the host's Docker daemon, except host services the network's gateway reaches (section 5) | anything inside the container, credentials included |
| the network beyond the allowlist | the addresses on the allowlist |
| the host kernel, as long as the container runtime holds | the host, when a runtime escape appears (runc had High-severity escapes in 2024 and in November 2025) |

The workspace is the way back to your machine. Repository files that tools run later, such as git
hooks, `.envrc`, a `Makefile`, an editor's task file, the dev container's definition
(`.devcontainer/`) or an agent's own committed settings, run on
your host the next time you or your tools open them. In June 2026 a worm spread through exactly
such files: "Cloning the repository is safe. Opening it is not." Section 7 says how to handle this.

## 3. Choose the isolation by trust

| Situation | Isolation | Why |
|---|---|---|
| A repository you trust; a person approves the agent's actions, which holds only with auto mode turned off (section 10) | a dev container (section 9) | a convenience: the same tools for everyone. Anthropic calls it "a convention rather than an enforcement boundary" |
| A repository you trust; the agent runs without approvals | a hardened container: no host credentials (section 4), egress only through an allowlisting proxy (section 5), the process rules of section 6 | the approvals were the only check; the container now carries the whole load |
| A repository you do not trust, or work on content from outside | a virtual machine or a microVM: a cloud VM, a cloud agent session, or Docker Sandboxes | a dev container runs the repository's own setup commands on your host (section 9), and every container shares your host's kernel. Anthropic's advice for untrusted repositories is "a dedicated virtual machine, or a cloud session" |

- **Decide the row before the agent first runs, and write it next to the setup**, in the
  repository's `README.md` or the dev container's comments. Anthropic's secure-deployment guide
  presents its options "so you can choose what fits your situation". A setup without a stated row
  tends to slide from "a person approves" to "runs without approvals" with no one changing the
  isolation: Johann Rehberger calls this the normalization of deviance, "temporary" shortcuts
  that "quietly become the new baseline".
- For row 2, user namespaces (`--userns-remap` in the daemon's configuration) narrow what a
  container escape reaches: Anthropic's secure-deployment guide says the option maps container
  root to an unprivileged host user. It is a setting for the whole daemon, and it moves every
  container UID into a subordinate range on the host, so the agent's UID no longer owns a
  bind-mounted clone (the shift [images.md](images.md) section 12 names for rootless Docker); give
  the clone to the remapped UID if you turn it on. For row 3, gVisor (`runsc`) is a middle step
  between a container and a virtual machine: it intercepts the container's system calls, so a
  kernel flaw is harder to reach, at the cost of slower I/O-heavy work, programs that fail on
  system calls it does not implement, and Linux hosts only. A virtual machine
  stays the first choice for an untrusted repository, because it runs its own kernel.

## 4. Credentials: give the agent nothing it must not leak

- **Mount no host credential into the container:** no `~/.ssh`, no SSH agent socket, no git
  credential helper, no `~/.aws`, `~/.config`, `~/.docker/config.json`, `~/.kube/config`, `.npmrc`
  or `.pypirc`. Anthropic's secure-deployment guide lists these, and adds that even read-only
  access to a code folder exposes the `.env` files and keys inside it.
- **Treat every credential inside the container as readable by the agent and by whatever it reads,
  and size it for that.** The agent's own API key is one of them: Claude Code keeps its
  credentials in `~/.claude`, which the agent can read. Create a workspace for agent keys in the
  Claude Console, set its spend limit, and make the agent's key there: the Default Workspace takes
  no limit. Use a key you can revoke alone, never a key shared with other work.
- **Give the agent tokens scoped to one repository and short-lived, or none.** A GitHub App
  installation token names its repositories and expires after one hour. Better still, the agent has
  no push rights at all: a person reviews the work and pushes it (section 7). GitHub's own cloud
  agent can only open pull requests, and a human must approve the CI run.
- **Keep secrets the agent needs to call a service behind a proxy outside the container**, when you
  can. Anthropic's guide recommends a proxy that adds the credential to outgoing requests, so the
  agent never holds it; Docker Sandboxes inject credentials the same way, and the raw value never
  enters the sandbox. For the agent's own API key, Anthropic's guide names a gateway set as
  `ANTHROPIC_BASE_URL`, which receives the requests in plain HTTP and can add the key.

Check: does the agent's container hold a host credential? `docker inspect` on it lists only the
mounts you meant, and inside it `git config --show-origin --get-all credential.helper` prints
nothing.

## 5. Network: one way out, through a proxy

- **Put the agent's container on an internal network with no route out, and give it one exit: an
  allowlisting proxy on a second container.** In Compose, an `internal: true` network has no route
  to the outside; the proxy is the only service on both networks. A tool that ignores the proxy
  variables then fails instead of going around the proxy. Two independent teams and GitHub's own
  agent workflows use this shape. Anthropic's guide uses `--network none`, where the container has
  no network interface at all and reaches a proxy on the host through a mounted socket; that also
  closes the path to the host described next, so it is the stronger choice where you cannot keep
  host services off the gateway. The internal network is used here because it works with Compose
  and dev containers as they are, with no socket bridge inside the container. The host stays
  reachable: on an internal network,
  Docker's documentation says, "communication with the gateway IP address (and thus appropriately
  configured host services) is possible". Bind host services the agent must not reach to
  `127.0.0.1`, or block the bridge in the host's firewall.
- **Allow only the hosts the work needs, and start from the agent's own published list.** For Claude
  Code that list is the "network access requirements" page, which ties `api.anthropic.com` to the
  API requests of every setup that calls Anthropic directly. Add the package registries the project installs from. Read each host on
  the list as a way out, too. Match the requested name only: a list that falls back to reverse DNS
  lets in any address whose owner names it after an allowed host, which Squid's `dstdomain` does
  unless you add `-n`.
- **Leave out hosts that accept writes from anyone:** GitHub, gists and other code hosts,
  paste sites, request bins, and wildcard cloud domains, unless the work cannot be done without
  them. Each one lets data leave in a form that looks like normal work.
- **Let the proxy resolve names; give the agent's container no DNS to the outside.** Anthropic's
  reference firewall script allows DNS and SSH to any host and the whole host subnet, so it leaves
  two ways out open; a report showing DNS tunnelling through it was closed by a bot without a fix.
  Do not copy it as a boundary. On an internal network, Docker's embedded DNS once sent outside
  names to an outside server (GHSA-mq39-4gv4-mvpx): fixed in 23.0.11 on the 23.0 line, in 25.0.5
  on the 25.0 line, and in 26.0.0 and later; no 24.0 release has the fix, and only a host whose
  resolver sits on a loopback address leaks. Docker Desktop is not affected: it runs its own
  internal resolver.
- **Know the proxy's limit.** A proxy that does not terminate TLS decides by the host name the client
  sends, so traffic to a shared CDN can be redirected to another site behind it (domain fronting).
  An allowed host is also a way out, and the model provider's API is always on the list: researchers
  used it to upload data with the attacker's own API key. The proxy narrows the ways out; it does not close
  them. Section 4 is what limits the damage.

Check: from the agent's container, does anything reach the outside without the proxy?
`getent hosts proxy` prints an address while `getent hosts example.com` prints nothing, a direct
connection to an outside address fails, and a request through the proxy to a host not on the
list fails with 403.

## 6. The container process

- **Run the agent as a non-root user with no `sudo` and without the `NET_ADMIN` capability.** A user
  who can run the firewall script again, or who holds `NET_ADMIN`, can change the rules that confine
  them; one widely used hardened container gives its user both.
- **Always run an init (`init: true` in Compose, `--init` with `docker run`).** An agent starts `git`,
  shells and test runners, and `git` leaves maintenance processes behind it. Without an init to reap
  them, three teams reported zombie processes piling up in 2026 (19,346 in one container) until the
  process limit stopped every new process, the agent's own included.
- **Set limits: `pids_limit`, memory and CPU.** The process limit turns a runaway fork into a failed
  command instead of a stalled host.
- **Drop every capability (`cap_drop: [ALL]`) and set `no-new-privileges`**, as Anthropic's
  secure-deployment recipe does. [compose.md](compose.md) section 7 gives the keys.

## 7. Files and git

- **Mount one workspace folder, never your home folder or the parent of several projects.** Every
  mounted file is readable, and, if writable, changeable by the agent.
- **Give an agent in a container its own clone of the repository, not a linked worktree of yours.**
  A linked worktree runs the main repository's hooks and shares its config, refs and stash, so an
  agent that can write to it can plant a hook that runs on your host at your next commit. Changing
  `core.hooksPath` does not close this: the config is shared too, and other config keys such as
  `core.fsmonitor` also run programs. Clone with `--no-local`: a clone from a local path hardlinks
  its object files to your repository's, so an agent that can write them could change your
  repository. [git.md](../git/git.md) section 8 owns how sessions get their working trees; this is
  its container case. In one measurement, a clone with no hardlinks took 1.8 s and 373 MB against
  0.8 s and 59 MB for a worktree: that is the price of the separation. `git clone --shared` costs
  about what a worktree costs, but the clone then reads your repository's objects, so the
  container would need your object store mounted, and git calls the option "a possibly dangerous
  operation"; this practice pays for `--no-local` instead. Section 11 names the one case where a
  linked worktree is fine.
- **Review the agent's work as a diff before you run anything from it on your host or push it,
  and read first the paths that run on your host or in CI.** Git hooks committed in a folder such
  as `.githooks`, `.envrc`, `Makefile` targets, editor tasks, committed agent settings
  (`.claude/`, `.mcp.json`, and other agents' folders such as `.gemini/` and `.cursor/`),
  `.gitmodules`, the dev container's files, Compose files and Dockerfiles,
  `.pre-commit-config.yaml` and its scripts, the dependency list and its lock file
  (`pyproject.toml`, `uv.lock` and `.python-version` in the Python case), `.github/workflows/` and
  `conftest.py` run with your rights when you or your tools use them, or in CI as soon as the
  branch is pushed to a repository whose workflows hold secrets.
- **Treat the clone as untrusted once the agent has run in it:** never open a shell, an editor, a
  git command or a `devcontainer` or `docker compose` command inside it on your host. Keep the
  clone outside every folder an editor, an IDE or a git tool has open: VS Code's git extension
  looks for repositories one folder down by default and runs git there, and git runs the program
  the clone's `core.fsmonitor` names. A container user with your own UID makes the clone yours,
  which turns off git's refusal to work in a repository owned by someone else. One session gets
  one clone and one Compose project name, both removed when the session ends, so nothing one
  session wrote reaches the next.
- **Bring the work back as a bundle that the container writes to standard output, into a file
  outside the clone** (`git bundle create -`), and fetch from that file in your own repository,
  so your git commands read that one file and never the agent's repository or its config. A
  bundle inside the clone is a path the agent can replace while its container runs. The agent
  commits to a branch you named, under an identity you set in its clone's config
  ([git.md](../git/git.md) section 8).
  A direct fetch from the agent's repository is the weaker way: git guards it (it ignores a
  repository's own `uploadpack.packObjectsHook` as "a safety measure against fetching from
  untrusted repositories"), but git's own security notes warn that "the surface area for attack
  against `upload-pack` is large, so this does carry some risk".
- **Mount the code read-only when it is a repository you do not trust**, inside the virtual
  machine or microVM that section 3 asks for in that row, and let the agent write only to a
  separate output folder.

## 8. Docker inside the agent's container

- **Never mount the host's Docker socket into the agent's container.** Whoever can talk to the Docker
  daemon controls the host: Docker's documentation says the `docker` group "grants root-level
  privileges", and Anthropic's sandbox documentation says allowing the socket "effectively grants
  access to the host system".
- **Run integration tests that need containers in CI, not in the agent's container**, when you can.
  Testcontainers ([python/testing/libraries.md](../../python/testing/libraries.md) section 2)
  needs a Docker daemon, and its page on running inside a container describes two ways to reach
  one: the host socket, or Docker-in-Docker, which it calls "an instrument of last resort".
  The agent writes the tests; a CI job runs them after you have reviewed them as section 7 says
  and pushed the branch.
- **When the agent must run them itself, there are two ways: a service beside it, or a daemon of
  its own. Know the cost:**

  | Option | What it costs |
  |---|---|
  | A database service beside the agent, on its internal network | no daemon and no `--privileged`; the tests read the database's address from settings instead of starting it, a departure from Testcontainers ([python/testing/libraries.md](../../python/testing/libraries.md) section 2, [compose.md](compose.md) section 6); one database shared by every test run of the session; one more image to pin |
  | Docker-in-Docker (`docker:dind`) | `--privileged`, which is "not a securely sandboxed process"; the rootless variant still needs `--privileged` |
  | Sysbox | runs Docker inside a container without `--privileged`, but needs a root-level install on a Linux host (Ubuntu or Debian packages, kernel 5.12 or newer); not for a laptop running Docker Desktop |
  | Docker Sandboxes | a private Docker daemon per agent inside a microVM, documented for builds, Compose and test suites; a proprietary tool at version 0.x, with a 10 GB disk by default; Testcontainers there is shown only in Docker's own demo |
  | A remote daemon (Testcontainers Cloud) | one more host on the allowlist, a token inside the container that the agent can read, no bind mounts of local files, and a paid plan after the trial |

## 9. Dev containers

A dev container is a container described by `.devcontainer/devcontainer.json`, which VS Code and
the `devcontainer` command-line tool build and start.

- **Never open a repository you do not trust in a dev container.** Its `devcontainer.json` can set
  `initializeCommand`, which runs on your host, with your rights, before any container exists.
- **When the agent writes without a person's approval, keep the dev container's definition
  outside every folder it can write.** The host reads `devcontainer.json`, whose
  `initializeCommand` runs on the host, and the Compose file and Dockerfiles it names each time it
  starts the container, so an agent that can edit them can run code on your host or widen its own
  network. When a person approves each action, that person also approves each change to the
  definition (section 11).

  Check: `docker compose -f <the definition's folder>/compose.yaml config` lists no volume whose
  source holds that folder.
- **Read the merged configuration before every start**, with
  `devcontainer read-configuration --include-merged-configuration`.
  A Feature or the base image's metadata can add `privileged: true`, an init, capabilities or mounts
  that `devcontainer.json` does not show: the specification turns `privileged` on if any source sets
  it, and joins the capability lists.
- **Commit `devcontainer-lock.json`, and run with `--frozen-lockfile` in CI.** The lock file records
  the digest of each Feature at its first install, so a Feature that changes later fails the build.
  It records what you first trusted; it does not check who published the Feature.
- **Do not attach an IDE to a container where the agent runs without approvals.** VS Code forwards
  your SSH agent and gpg agent into the container and installs a git credential helper that reaches
  your host's credentials; a researcher used the forwarded agents from inside a dev container to log
  in to another host as the user. A VS Code maintainer: "Docker containers are not a security
  boundary."
- **Start such a container with the `devcontainer` command-line tool or Compose**, which do not
  forward the SSH agent (a maintainer's statement of 2023). The check in section 4 does not see a
  socket an attached IDE forwards, so not attaching an IDE stays the guard.
- **When you must attach VS Code, turn off what it brings in from your host:** set
  `dev.containers.copyGitConfig` to `false` and `dev.containers.gitCredentialHelperConfigLocation`
  to `"none"` in your host user settings, and clear `SSH_AUTH_SOCK` and `GPG_AGENT_INFO` in
  `remoteEnv`. VS Code has no setting that turns off the SSH agent forwarding itself. Clearing the
  variables hides the path, not the socket an attached IDE forwards (VS Code puts it under
  `/tmp/vscode-ssh-auth-*.sock`, by practitioner reports), so where the agent runs without
  approvals, not attaching an IDE is the only guard.
- **Pin the agent's version in the image, and turn off its self-update.** The Claude Code dev
  container Feature installs the latest release and updates itself; install a fixed version with
  `npm` instead. The npm package asks for Node.js 22 or later, and an older Node gives only a
  warning at install (Claude Code's setup page). Set `DISABLE_AUTOUPDATER=1`, so the agent in the
  container is the one you chose.
- **Keep the agent's settings and login in a named volume, and count that volume as a secret.** Claude
  Code needs `CLAUDE_CONFIG_DIR` pointed at the volume to keep you signed in across rebuilds; the
  volume then holds the agent's credentials.

## 10. The agent's own settings are not the boundary

An agent's built-in sandbox and permission settings are useful inside the container. They are not
what keeps it in.

- **Do not count on the agent's built-in sandbox inside a container.** Claude Code's sandbox runs
  commands without the sandbox when it cannot start, unless `sandbox.failIfUnavailable` is set; its
  retry outside the sandbox is on by default; and inside an unprivileged container it needs a weaker
  mode that its own documentation says "considerably weakens security".
- **On machines where the agent must never act without a person's approval, turn off both modes
  that skip it, centrally**: `"permissions": {"disableBypassPermissionsMode": "disable",
  "disableAutoMode": "disable"}` in the managed settings file
  (`/etc/claude-code/managed-settings.json` on Linux). From Claude Code 2.1.283, auto mode is the
  starting mode of interactive terminal and VS Code sessions, and "in auto mode, a second model,
  the classifier, reviews actions instead of you". The first key makes Claude Code reject
  `--dangerously-skip-permissions`; the second removes auto mode. Managed settings guard against
  mistakes, not against someone who controls the machine: an administrator can edit the file, and
  Anthropic calls the form it delivers from its servers "a client-side control, not a security
  boundary".

## 11. Where it stops holding

- **A person who approves each action in a repository they trust** may mount a linked worktree into
  a dev container. This holds only with auto mode turned off (section 10). Its `.git` file holds
  an absolute host path; with git 2.48 or newer, create the worktree with `--relative-paths` (or
  set `worktree.useRelativePaths`), which git's own commit message names as the fix for
  containers. Every git that reads the repository must be 2.48 or
  newer.
- **Other agents** keep their own settings and lists of hosts: GitHub's cloud agent has its own
  firewall, and OpenAI's Codex its own internet settings, each with stated limits. Sections 2 to 9
  hold for them; section 10 names Claude Code's keys only.
- **Row 3 of section 3, a virtual machine or a microVM, has no setup in this file.** Sections 4, 5
  and 7 are the questions to ask of such a product: which credentials enter it, what its network
  allows, and how the work comes back.
- **Sandbox products change fast.** Docker Sandboxes was at version 0.x in October 2026, with
  breaking changes between releases; check its current defaults (allowed domains, permission mode)
  before you rely on them.

## 12. Sources

Read in October 2026 unless a date is given.

- Anthropic, Claude Code documentation: "Development containers", "Sandboxing", "Sandbox
  environments", "Permission modes", "Security", "Network configuration", "Settings reference",
  "Managed settings", "Server-managed settings", "Advanced setup" (install with npm); Agent SDK
  "Secure deployment"; the reference `.devcontainer` folder of the `anthropics/claude-code`
  repository (`init-firewall.sh`, last changed 2026-06-30) and its issue #36907; advisory
  GHSA-7835-87q9-rgvv (2026-06-25); Claude platform documentation, "Workspaces" (spend limits).
- Docker documentation: "Docker Engine security", "Isolate containers with a user namespace"
  (`userns-remap`), "Linux post-installation steps" (the `docker` group), `docker container run`
  (`--privileged`, `--init`), `docker network create` (internal mode), Docker Sandboxes (security,
  architecture, workflows, troubleshooting, the Claude Code agent page); Docker Hub, the `docker` image page (Docker-in-Docker and `--privileged`); Docker's
  blog on running agents in GitHub Actions with Docker Sandboxes (2026-08-21); moby advisory
  GHSA-mq39-4gv4-mvpx (embedded DNS on internal networks).
- Development Containers specification (containers.dev: the JSON reference, Features, Features
  distribution, the lock file) and devcontainers/cli issue #441 and #1195, and its
  `src/spec-node/dockerCompose.ts` (`getProjectName`, the Compose project name); VS Code
  documentation (dev containers, "Use Docker Compose", sharing git credentials, trust and safety,
  the 1.118 release notes) and microsoft/vscode-remote-release issues #9897 and #11869;
  microsoft/vscode issue #287765 and the git extension's `package.json`
  (`git.autoRepositoryDetection`, `git.repositoryScanMaxDepth`).
- GitHub documentation: the Copilot cloud agent firewall; installation access tokens for GitHub
  Apps; "Events that trigger workflows" (`push`); the GitHub blog on its agentic security
  principles (2025-11-25); GitHub Agentic Workflows architecture.
- git documentation: `git(1)` (SECURITY), `git-clone(1)` (`--local`, `--shared`), `git-bundle(1)`,
  `git-worktree(1)`, `git-config(1)` (`worktree.useRelativePaths`, `core.hooksPath`,
  `core.fsmonitor`, `uploadpack.packObjectsHook`), `gitrepository-layout(5)`; git 2.48.0 release
  notes; the git commit "worktree: link worktrees with relative paths".
- Squid documentation, the `acl` directive (`dstdomain`, `-n`); the Squid v6 source,
  `src/tools.cc` (`leave_suid()`).
- Testcontainers documentation (patterns for running inside Docker, configuration and Ryuk;
  Testcontainers Cloud); Nestybox Sysbox user guide (Docker-in-Docker, installation, limitations).
- Studies (preprints): arXiv:2607.20759 (2026, injected issue instructions); arXiv:2606.09935
  (2026, prompt injection in CI agents).
- Researchers and practitioners: Simon Willison, "The lethal trifecta" (2025-06-16); Johann
  Rehberger, embracethered.com (exfiltration through the Anthropic API, 2025-10-28; DNS, 2025-08-11;
  Auto Mode, 2026-08-26; "The Normalization of Deviance in AI", 2025-12-04); PromptArmor on
  allowlists (2026-05-13); Invariant Labs on the GitHub MCP
  server (2025-05-26); StepSecurity on the Miasma worm (2026-06-05); The Red Guild, "Leveraging
  VSCode internals to escape containers" (2025-11-16); Trail of Bits' `claude-code-devcontainer`;
  Alex Chaplinsky, fletch.sh, on worktrees and clones for agents (2026-07-30); the
  schubergphilis/claude-docker pull request #112 discussion; ftnilsson/dev-containers and Shaharia
  Azam (2026-02-21) on the proxy sidecar; issues Cloonar/coding-lab #64, lbacik/agent-forge #9 and
  rappdw/sandy #392 (zombie processes).
- runc advisories GHSA-xr7r-f8xq-vfvv (2024) and GHSA-cgrx-mc8f-2prm (2025).
