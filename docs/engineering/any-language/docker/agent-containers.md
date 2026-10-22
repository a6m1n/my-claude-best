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

- Agents follow instructions hidden in what they read. In a 2026 study, Singh, Yang and Chen found
  that coding agents set to accept their own actions carried out an instruction planted in a
  GitHub issue in 41% to 79% of runs, depending on the agent [1]. For one agent, its own sandbox
  and network isolation rejected none of the attacks that stayed inside the workspace [1].
- The vendors say it about their own containers. Anthropic: run without approvals, a dev
  container does "not prevent a malicious project from exfiltrating anything accessible inside the
  container, including the Claude Code credentials" [2]. GitHub calls its agent firewall not "a
  comprehensive security solution" [3]. Microsoft: a dev container's "boundary depends on the
  container configuration" [4].
- Researchers have sent data out through addresses an allowlist lets through: the model
  provider's own API [5], a model hub's download counter [6] and GitHub [7].

## 2. What a container protects, and what it does not

Name the three conditions before you choose anything. An agent that has private data, reads
untrusted content and can send data out can be made to leak that data; Simon Willison calls the
combination the "lethal trifecta" [8]. A coding agent always reads untrusted content: issues, pull
requests, web pages, dependencies, and the repository itself. So each setup decides the other two:
what the agent can read, and where it can send it.

| A container, set up as this file says, protects | It does not protect |
|---|---|
| host files outside the mounted workspace | the mounted workspace: the agent's edits land on your disk |
| host processes, the host's Docker daemon, except host services the network's gateway reaches (section 5) | anything inside the container, credentials included |
| the network beyond the allowlist | the addresses on the allowlist |
| the host kernel, as long as the container runtime holds | the host, when a runtime escape appears (runc had High-severity escapes in 2024 and in November 2025) [9], [10] |

The workspace is the way back to your machine. Repository files that tools run later, such as git
hooks, `.envrc`, a `Makefile`, an editor's task file, the dev container's definition
(`.devcontainer/`) or an agent's own committed settings, run on
your host the next time you or your tools open them. In June 2026 a worm spread through files of
this kind in Microsoft's Azure GitHub organizations: "Cloning the repository is safe. Opening it is
not" [11]. Section 7 says how to handle
this.

## 3. Choose the isolation by trust

| Situation | Isolation | Why |
|---|---|---|
| A repository you trust; a person approves the agent's actions, which holds only with auto mode turned off (section 10) | a dev container (section 9) | a convenience: the same tools for everyone. Anthropic calls it "a convention rather than an enforcement boundary" [12] |
| A repository you trust; the agent runs without approvals | a hardened container: no host credentials (section 4), egress only through an allowlisting proxy (section 5), the process rules of section 6 | the approvals were the only check; the container now carries the whole load |
| A repository you do not trust, or work on content from outside | a virtual machine or a microVM: a cloud VM, a cloud agent session, or Docker Sandboxes [12] | a dev container runs the repository's own setup commands on your host (section 9), and every container shares your host's kernel [13]. Anthropic's advice for an untrusted repository: "A dedicated virtual machine, or a cloud session" [12] |

- **Decide the row before the agent first runs, and write it next to the setup**, in the
  repository's `README.md` or the dev container's comments. Anthropic's secure-deployment guide
  presents its options "so you can choose what fits your situation" [13]. A setup without a stated
  row tends to slide from "a person approves" to "runs without approvals" with no one changing the
  isolation: Johann Rehberger calls this the normalization of deviance, "temporary" shortcuts
  that "quietly become the new baseline" [14].
- For row 2, user namespaces (`--userns-remap` in the daemon's configuration) narrow what a
  container escape reaches: Anthropic's secure-deployment guide says the option maps container
  root to an unprivileged host user [13]. It is a setting for the whole daemon, and it moves every
  container UID into a subordinate range on the host [15], so the agent's UID no longer owns a
  bind-mounted clone (the shift [images.md](images.md) section 12 names for rootless Docker); give
  the clone to the remapped UID if you turn it on. For row 3, gVisor (`runsc`) is a middle step
  between a container and a virtual machine: it intercepts the container's system calls, so a
  kernel flaw is harder to reach, at the cost of slower I/O-heavy work, programs that fail on
  system calls it does not implement, and Linux hosts only [13], [16]. A virtual machine stays the
  first choice for an untrusted repository, because it runs its own kernel [13].

## 4. Credentials: give the agent nothing it must not leak

- **Mount no host credential into the container:** no `~/.ssh`, no SSH agent socket, no git
  credential helper, no `~/.aws`, `~/.config`, `~/.docker/config.json`, `~/.kube/config`, `.npmrc`
  or `.pypirc`. Anthropic's secure-deployment guide lists most of these, and adds that even
  read-only access to a code folder exposes the `.env` files and keys inside it [13].
- **Treat every credential inside the container as readable by the agent and by whatever it reads,
  and size it for that.** The agent's own API key is one of them: Claude Code keeps its
  credentials in `~/.claude`, which the agent can read [2]. Create a workspace for agent keys in the
  Claude Console, set its spend limit, and make the agent's key there: the Default Workspace takes
  no limit [17]. Use a key you can revoke alone, never a key shared with other work.
- **Give the agent tokens scoped to one repository and short-lived, or none.** A GitHub App
  installation token names its repositories and expires after one hour [18]. Better still, the
  agent has no push rights at all: a person reviews the work and pushes it (section 7). GitHub's
  own cloud agent can only open pull requests, and a human must approve the CI run [19].
- **Keep secrets the agent needs to call a service behind a proxy outside the container**, when you
  can. Anthropic's guide recommends a proxy that adds the credential to outgoing requests, so the
  agent never holds it; Docker Sandboxes inject credentials the same way, and the raw value never
  enters the sandbox [13], [20]. For the agent's own API key, Anthropic's guide names a gateway set
  as `ANTHROPIC_BASE_URL`, which receives the requests in plain HTTP and can add the key [13].

Check: does the agent's container hold a host credential? `docker inspect` on it lists only the
mounts you meant, and inside it `git config --show-origin --get-all credential.helper` prints
nothing.

## 5. Network: one way out, through a proxy

- **Put the agent's container on an internal network with no route out, and give it one exit: an
  allowlisting proxy on a second container.** In Compose, an `internal: true` network has no route
  to the outside; the proxy is the only service on both networks [21]. A tool that ignores the
  proxy variables then fails instead of going around the proxy. Two independent practitioners and
  GitHub's own agent workflows use this shape [22], [23], [24]. Anthropic's guide uses
  `--network none`, where the container has no network interface at all and reaches a proxy on the
  host through a mounted socket [13]; that also closes the path to the host described next, so it
  is the stronger choice where you cannot keep host services off the gateway. The internal network
  is used here because it works with Compose and dev containers as they are, with no socket bridge
  inside the container. The host stays reachable: of an internal network, Docker's documentation
  says "Communication with the gateway IP address (and thus appropriately configured host
  services) is possible" [25]. Bind host services the agent must not reach to `127.0.0.1`, or
  block the bridge in the host's firewall.
- **Allow only the hosts the work needs, and start from the agent's own published list.** For Claude
  Code that list is the "Network access requirements" section of its network configuration page,
  which ties `api.anthropic.com` to the API requests of every setup that calls Anthropic
  directly [26]. Add the package registries the project installs from. Read each host on the list
  as a way out, too. Match the requested name only: a list that falls back to reverse DNS lets in
  any address whose owner names it after an allowed host, which Squid's `dstdomain` does unless you
  add `-n` [27].
- **Leave out hosts that accept writes from anyone:** GitHub, gists and other code hosts,
  paste sites, request bins, and wildcard cloud domains, unless the work cannot be done without
  them [28], [29]. Each one lets data leave in a form that looks like normal work.
- **Let the proxy resolve names; give the agent's container no DNS to the outside.** Anthropic's
  reference firewall script allows DNS and SSH to any host and the whole host subnet, so it leaves
  two ways out open; a report showing DNS tunnelling through it was closed by a bot without a
  fix [30], [31]. Do not copy it as a boundary. On an internal network, Docker's embedded DNS once
  sent outside names to an outside server (GHSA-mq39-4gv4-mvpx): fixed in 23.0.11 on the 23.0
  line, in 25.0.5 on the 25.0 line, and in 26.0.0 and later; the advisory names no fixed 24.0
  release, and only a host whose resolver sits on a loopback address leaks [32]. Docker Desktop is
  not affected: it runs its own internal resolver [32].
- **Know the proxy's limit.** A proxy that does not terminate TLS decides by the host name the client
  sends, so traffic to a shared CDN can be redirected to another site behind it (domain
  fronting) [33], [34]. An allowed host is also a way out, and the model provider's API is always on
  the list: Johann Rehberger used it, from Claude's Code Interpreter, to upload data with the
  attacker's own API key [26], [5]. The proxy narrows the ways out; it does not close them.
  Section 4 is what limits the damage.

Check: from the agent's container, does anything reach the outside without the proxy?
`getent hosts proxy` prints an address while `getent hosts example.com` prints nothing, a direct
connection to an outside address fails, and a request through the proxy to a host not on the
list fails with 403.

## 6. The container process

- **Run the agent as a non-root user with no `sudo` and without the `NET_ADMIN` capability.** A user
  who can run the firewall script again, or who holds `NET_ADMIN`, can change the rules that confine
  them; one widely used hardened container gives its user both [35].
- **Always run an init (`init: true` in Compose, `--init` with `docker run`).** An agent starts `git`,
  shells and test runners, and `git` leaves maintenance processes behind it [36]. Without an init to
  reap them, three projects reported zombie processes piling up in 2026 (19,346 in one container)
  until the process limit stopped every new process, the agent's own included [36], [37], [38].
- **Set limits: `pids_limit`, memory and CPU.** The process limit turns a runaway fork into a failed
  command instead of a stalled host.
- **Drop every capability (`cap_drop: [ALL]`) and set `no-new-privileges`**, as Anthropic's
  secure-deployment recipe does [13]. [compose.md](compose.md) section 7 gives the keys.

## 7. Files and git

- **Mount one workspace folder, never your home folder or the parent of several projects.** Every
  mounted file is readable, and, if writable, changeable by the agent.
- **Give an agent in a container its own clone of the repository, not a linked worktree of yours.**
  A linked worktree runs the main repository's hooks and shares its config, refs and stash, so an
  agent that can write to it can plant a hook that runs on your host at your next commit [39], [40],
  [43]. Changing `core.hooksPath` does not close this: the config is shared too, and other config
  keys such as `core.fsmonitor` also run programs [40], [41]. Clone with `--no-local`: a clone from
  a local path hardlinks its object files to your repository's, so an agent that can write them
  could change your repository [42]. [git.md](../git/git.md) section 8 owns how sessions get their
  working trees; this is its container case. In Alex Chaplinsky's measurement on git's own
  repository, a clone with no hardlinks took 1.8 s and 373 MB against 0.8 s and 59 MB for a
  worktree: that is the price of the separation [43]. `git clone --shared` costs about what a
  worktree costs [43], but the clone then reads your repository's objects, so the container would
  need your object store mounted, and git calls the option "a possibly dangerous
  operation" [42]; this practice pays for `--no-local` instead. Section 11 names the one case where
  a linked worktree is fine.
- **Review the agent's work as a diff before you run anything from it on your host or push it,
  and read first the paths that run on your host or in CI.** Git hooks committed in a folder such
  as `.githooks`, `.envrc`, `Makefile` targets, editor tasks, committed agent settings
  (`.claude/`, `.mcp.json`, and other agents' folders such as `.gemini/` and `.cursor/`),
  `.gitmodules`, the dev container's files, Compose files and Dockerfiles,
  `.pre-commit-config.yaml` and its scripts, the dependency list and its lock file
  (`pyproject.toml`, `uv.lock` and `.python-version` in the Python case), `.github/workflows/` and
  `conftest.py` run with your rights when you or your tools use them, or in CI as soon as the
  branch is pushed [44]. That CI run is the risk in a repository whose workflows hold secrets.
- **Treat the clone as untrusted once the agent has run in it:** never open a shell, an editor, a
  git command or a `devcontainer` or `docker compose` command inside it on your host. Keep the
  clone outside every folder an editor, an IDE or a git tool has open: VS Code's git extension
  looks for repositories one folder down by default [45] and runs git there, and git runs the
  program the clone's `core.fsmonitor` names [41]. A container user with your own UID makes the clone
  yours, which turns off git's refusal to work in a repository owned by someone else [41]. One
  session gets
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
  untrusted repositories" [41]), but git's own security notes warn that "the surface area for
  attack against `upload-pack` is large, so this does carry some risk" [46].
- **Mount the code read-only when it is a repository you do not trust**, inside the virtual
  machine or microVM that section 3 asks for in that row, and let the agent write only to a
  separate output folder.

## 8. Docker inside the agent's container

- **Never mount the host's Docker socket into the agent's container.** Whoever can talk to the Docker
  daemon controls the host: Docker's documentation says the `docker` group "grants root-level
  privileges", and Anthropic's sandbox documentation says allowing the socket "effectively grants
  access to the host system" [47], [33].
- **Run integration tests that need containers in CI, not in the agent's container**, when you can.
  Testcontainers ([python/testing/libraries.md](../../python/testing/libraries.md) section 2)
  needs a Docker daemon, and its page on running inside a container describes two ways to reach
  one: the host socket, or Docker-in-Docker, which it says is "generally considered an instrument
  of last resort" [48].
  The agent writes the tests; a CI job runs them after you have reviewed them as section 7 says
  and pushed the branch.
- **When the agent must run them itself, there are two ways: a service beside it, or a daemon of
  its own. Know the cost:**

  | Option | What it costs |
  |---|---|
  | A database service beside the agent, on its internal network | no daemon and no `--privileged`; the tests read the database's address from settings instead of starting it, a departure from Testcontainers ([python/testing/libraries.md](../../python/testing/libraries.md) section 2, [compose.md](compose.md) section 6); one database shared by every test run of the session; one more image to pin |
  | Docker-in-Docker (`docker:dind`) | `--privileged`, which is "not a securely sandboxed process"; the rootless variant still needs `--privileged` [49], [50] |
  | Sysbox | runs Docker inside a container without `--privileged`, but needs a root-level install on a Linux host (Ubuntu or Debian packages; below kernel 5.12 also the shiftfs module) [51]; not for a laptop running Docker Desktop |
  | Docker Sandboxes | a private Docker daemon per agent inside a microVM, documented for builds, Compose and test suites [52], [53]; a proprietary tool at version 0.x [55], with a 10 GB Docker data disk (20 GB root) by default [54]; Testcontainers there is shown only in Docker's own demo [56] |
  | A remote daemon (Testcontainers Cloud) | one more host on the allowlist, a token inside the container that the agent can read, no bind mounts of local files, and a paid plan after the trial [57], [58] |

## 9. Dev containers

A dev container is a container described by `.devcontainer/devcontainer.json`, which VS Code and
the `devcontainer` command-line tool build and start. This section covers the agent's; a dev
container a person works in, and whether a team needs one at all, is
[dev-containers.md](dev-containers.md).

- **Never open a repository you do not trust in a dev container.** Its `devcontainer.json` can set
  `initializeCommand`, which runs on your host, with your rights, before any container exists [59].
- **When the agent writes without a person's approval, keep the dev container's definition
  outside every folder it can write.** The host reads `devcontainer.json`, whose
  `initializeCommand` runs on the host, and the Compose file and Dockerfiles it names each time it
  starts the container, so an agent that can edit them can run code on your host or widen its own
  network [59]. When a person approves each action, that person also approves each change to the
  definition (section 11).

  Check: `docker compose -f <the definition's folder>/compose.yaml config` lists no volume whose
  source holds that folder.
- **Read the merged configuration before every start**, with
  `devcontainer read-configuration --include-merged-configuration` [60].
  A Feature or the base image's metadata can add `privileged: true`, an init, capabilities or mounts
  that `devcontainer.json` does not show: the specification turns `privileged` on if any source sets
  it, and joins the capability lists [61].
- **Commit `devcontainer-lock.json`, and run with `--frozen-lockfile` in CI.** The lock file records
  the digest of each Feature at its first install, so a Feature that changes later fails the
  build [62], [60], [63]. It records what you first trusted; it does not check who published the
  Feature [62].
- **Do not attach an IDE to a container where the agent runs without approvals.** VS Code forwards
  your SSH agent and gpg agent into the container and installs a git credential helper that reaches
  your host's credentials; a researcher at The Red Guild used the forwarded agents from inside a
  dev container to log in to another host as the user [64], [65]. A VS Code maintainer wrote: "My
  understanding is that Docker containers are not a security boundary" [66].
- **Start such a container with the `devcontainer` command-line tool or Compose**, which do not
  forward the SSH agent; a maintainer of the command-line tool said so for it in 2023 [67]. The
  check in section 4 does not see a socket an attached IDE forwards, so not attaching an IDE stays
  the guard.
- **When you must attach VS Code, turn off what it brings in from your host:** set
  `dev.containers.copyGitConfig` to `false` and `dev.containers.gitCredentialHelperConfigLocation`
  to `"none"` in your host user settings [66], and clear `SSH_AUTH_SOCK` and `GPG_AGENT_INFO` in
  `remoteEnv` [65]. An issue reporter found that `copyGitConfig` works only in the host's user
  settings: set in `devcontainer.json`, it left the copy attempted, and the copy stopped once the
  setting moved to the host's user `settings.json` [77]. A VS Code maintainer wrote in 2024 that
  with `dev.containers.forwardWSLServices` off a local `ssh-agent` "will still be forwarded" [66].
  Clearing the variables hides the path, not the socket an attached IDE forwards (VS Code puts it
  under `/tmp/vscode-ssh-auth-*.sock`, by practitioner reports) [65], so where the agent runs without
  approvals, not attaching an IDE is the only guard.
- **Pin the agent's version in the image, and turn off its self-update.** The Claude Code dev
  container Feature installs the latest release and updates itself; install a fixed version with
  `npm` instead [2]. The npm package asks for Node.js 22 or later, and an older Node gives only a
  warning at install [68]. Set `DISABLE_AUTOUPDATER=1`, so the agent in the container is the one you
  chose [2].
- **Keep the agent's settings and login in a named volume, and count that volume as a secret.** Claude
  Code needs `CLAUDE_CONFIG_DIR` pointed at the volume to keep you signed in across rebuilds; the
  volume then holds the agent's credentials [2].

## 10. The agent's own settings are not the boundary

An agent's built-in sandbox and permission settings are useful inside the container. They are not
what keeps it in.

- **Do not count on the agent's built-in sandbox inside a container.** Claude Code's sandbox runs
  commands without the sandbox when it cannot start, unless `sandbox.failIfUnavailable` is set; its
  retry outside the sandbox is on by default; and inside an unprivileged container it needs a weaker
  mode that its own documentation says "considerably weakens security" [69], [33].
- **On machines where the agent must never act without a person's approval, turn off both modes
  that skip it, centrally**: `"permissions": {"disableBypassPermissionsMode": "disable",
  "disableAutoMode": "disable"}` in the managed settings file
  (`/etc/claude-code/managed-settings.json` on Linux) [69], [70]. From Claude Code 2.1.283, auto
  mode is the starting mode of interactive terminal and VS Code sessions, and Anthropic's page
  says: "In auto mode, a second model, the classifier, reviews actions instead of you" [71]. The
  first key makes Claude Code reject `--dangerously-skip-permissions`; the second removes auto
  mode [69]. Managed settings guard against mistakes, not against someone who controls the
  machine: an administrator can edit the file, and Anthropic calls the form it delivers from its
  servers "a client-side control, not a security boundary" [72].

## 11. Where it stops holding

- **A person who approves each action in a repository they trust** may mount a linked worktree into
  a dev container. This holds only with auto mode turned off (section 10). Its `.git` file holds
  an absolute host path; with git 2.48 or newer, create the worktree with `--relative-paths` (or
  set `worktree.useRelativePaths`), which git's own commit message names as the fix for
  containers [73], [40]. Every git that reads the repository must be 2.48 or newer [41], [74].
- **Other agents** keep their own settings and lists of hosts: GitHub's cloud agent has its own
  firewall, and OpenAI's Codex its own internet settings, each with stated limits [3], [75].
  Sections 2 to 9 hold for them; section 10 names Claude Code's keys only.
- **Row 3 of section 3, a virtual machine or a microVM, has no setup in this file.** Sections 4, 5
  and 7 are the questions to ask of such a product: which credentials enter it, what its network
  allows, and how the work comes back.
- **Sandbox products change fast.** Docker Sandboxes was at version 0.x in October 2026, with
  breaking changes between releases [55], [76]; check its current defaults (allowed domains,
  permission mode) before you rely on them.

## 12. Sources

Checked 2026-10-16 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Ankur Singh, Jinqiu Yang and Tse-Hsun Chen — IssueTrojanBench: Benchmarking AI Coding Agents Against Malicious Issue Requests (arXiv preprint, 2026; research) — https://arxiv.org/abs/2607.20759v1
- [2] Anthropic — Development containers (Claude Code docs) — https://code.claude.com/docs/en/devcontainer
- [3] GitHub — Customizing or disabling the firewall for GitHub Copilot — https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-the-firewall
- [4] Microsoft — Understand trust and safety for AI agents (VS Code docs) — https://code.visualstudio.com/docs/agents/concepts/trust-and-safety
- [5] Johann Rehberger — Claude Pirate: Abusing Anthropic's File API For Data Exfiltration (Embrace The Red, 2025; case) — https://embracethered.com/blog/posts/2025/claude-abusing-network-access-and-anthropic-api-for-data-exfiltration/
- [6] Anthropic — GHSA-fg94-h982-f3mm, Claude Code: Out-of-Band Data Exfiltration via Pre-Approved HuggingFace Domain in WebFetch — https://github.com/advisories/GHSA-fg94-h982-f3mm
- [7] Omer Mayraz — CamoLeak: Critical GitHub Copilot Vulnerability Leaks Private Source Code (Legit Security blog, 2025; case) — https://www.legitsecurity.com/blog/camoleak-critical-github-copilot-vulnerability-leaks-private-source-code
- [8] Simon Willison — The lethal trifecta for AI agents: private data, untrusted content, and external communication (simonwillison.net, 2025; opinion) — https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
- [9] opencontainers/runc — GHSA-xr7r-f8xq-vfvv, container breakout through process.cwd trickery and leaked fds (CVE-2024-21626) — https://github.com/opencontainers/runc/security/advisories/GHSA-xr7r-f8xq-vfvv
- [10] opencontainers/runc — GHSA-cgrx-mc8f-2prm, container escape and denial of service due to arbitrary write gadgets and procfs write redirects (CVE-2025-52881) — https://github.com/opencontainers/runc/security/advisories/GHSA-cgrx-mc8f-2prm
- [11] StepSecurity — Miasma Worm Hits Microsoft Again: Azure Functions Action and 72 Other Repositories Disabled After Supply Chain Attack Targeting AI Coding Agents (StepSecurity blog, 2026; case) — https://www.stepsecurity.io/blog/miasma-worm-hits-microsoft-again-azure-functions-action-and-72-other-repositories-disabled-after-supply-chain-attack-targeting-ai-coding-agents
- [12] Anthropic — Choose a sandbox environment (Claude Code docs) — https://code.claude.com/docs/en/sandbox-environments
- [13] Anthropic — Securely deploying AI agents (Claude Agent SDK docs) — https://code.claude.com/docs/en/agent-sdk/secure-deployment
- [14] Johann Rehberger — The Normalization of Deviance in AI (Embrace The Red, 2025; opinion) — https://embracethered.com/blog/posts/2025/the-normalization-of-deviance-in-ai/
- [15] Docker — Isolate containers with a user namespace — https://docs.docker.com/engine/security/userns-remap/
- [16] Google — gVisor documentation (`g3doc/README.md`, `user_guide/compatibility.md`, `user_guide/install.md`) — https://github.com/google/gvisor/tree/5b88ae5f7c64db9d323e3950a2f2386842c79d33/g3doc
- [17] Anthropic — Workspaces (Claude Platform docs) — https://platform.claude.com/docs/en/manage-claude/workspaces
- [18] GitHub — Generating an installation access token for a GitHub App — https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app
- [19] Rahul Zhade — How GitHub's agentic security principles make our AI agents as secure as possible (GitHub Blog, 2025; case) — https://github.blog/ai-and-ml/github-copilot/how-githubs-agentic-security-principles-make-our-ai-agents-as-secure-as-possible/
- [20] Docker — Docker Sandboxes: Default security posture — https://docs.docker.com/ai/sandboxes/security/defaults/
- [21] Docker — Networking in Compose — https://docs.docker.com/compose/how-tos/networking/
- [22] Fredrik Nilsson — Agent Sandbox Dev Container, `README.md` (ftnilsson/dev-containers, 2026; case) — https://github.com/ftnilsson/dev-containers/blob/dc69d3e2ad1713a94aecf8b9372db04f8a1d9859/README.md
- [23] Shaharia Azam — Claude Code in Docker Compose: Network-Isolated Setup (shaharia.com, 2026; case) — https://shaharia.com/blog/run-claude-code-docker-network-isolation/
- [24] GitHub — GitHub Agentic Workflows: Architecture — https://github.github.com/gh-aw/introduction/architecture/
- [25] Docker — docker network create (CLI reference), network internal mode — https://docs.docker.com/reference/cli/docker/network/create/
- [26] Anthropic — Enterprise network configuration, Network access requirements (Claude Code docs) — https://code.claude.com/docs/en/network-config#network-access-requirements
- [27] Squid Project — Squid configuration directive `acl` — https://www.squid-cache.org/Doc/config/acl/
- [28] PromptArmor Threat Intelligence — What domains should I add to my allowlist? (PromptArmor, 2026; opinion) — https://www.promptarmor.com/resources/what-domains-should-i-add-to-my-allowlist
- [29] Simon Willison — Google Antigravity Exfiltrates Data (simonwillison.net, 2025; opinion) — https://simonwillison.net/2025/Nov/25/google-antigravity-exfiltrates-data/
- [30] Anthropic — `.devcontainer/init-firewall.sh` (anthropics/claude-code) — https://github.com/anthropics/claude-code/blob/d945a61bc6346abce607252d5667df8a3bf0461a/.devcontainer/init-firewall.sh
- [31] Ilan Goldfeld — Devcontainer firewall allows DNS to arbitrary servers — enables data exfiltration via DNS tunneling (GitHub, anthropics/claude-code issue #36907, 2026; case) — https://github.com/anthropics/claude-code/issues/36907
- [32] Moby project — GHSA-mq39-4gv4-mvpx, External DNS requests from 'internal' networks could lead to data exfiltration (CVE-2024-29018) — https://github.com/moby/moby/security/advisories/GHSA-mq39-4gv4-mvpx
- [33] Anthropic — Sandboxing (Claude Code docs) — https://code.claude.com/docs/en/sandboxing
- [34] Wikipedia — Domain fronting — https://en.wikipedia.org/wiki/Domain_fronting
- [35] Trail of Bits — claude-code-devcontainer (`README.md`, `devcontainer.json`) — https://github.com/trailofbits/claude-code-devcontainer/tree/feea113719e50c8820ce5d0f11f2b0abb01d32a4
- [36] dpolakovics — Container runs exhaust the pids cap with zombies: the provider CLI is PID 1 and never reaps orphans (GitHub, Cloonar/coding-lab issue #64, 2026; case) — https://github.com/Cloonar/coding-lab/issues/64
- [37] Łukasz Bacik — Agent containers run without an init process; orphaned zombies exhaust pids.max and fail every attempt (GitHub, lbacik/agent-forge issue #9, 2026; case) — https://github.com/lbacik/agent-forge/issues/9
- [38] Daniel Rapp — Agent container has no init: orphaned processes become permanent zombies and exhaust --pids-limit 512, killing long-lived sessions (GitHub, rappdw/sandy issue #392, 2026; case) — https://github.com/rappdw/sandy/issues/392
- [39] Git — gitrepository-layout, v2.56.0 — https://github.com/git/git/blob/v2.56.0/Documentation/gitrepository-layout.adoc
- [40] Git — git-worktree, v2.56.0 — https://github.com/git/git/blob/v2.56.0/Documentation/git-worktree.adoc
- [41] Git — git-config (`core.fsmonitor`, `safe.directory`, `uploadpack.packObjectsHook`, `worktree.useRelativePaths`), v2.56.0 — https://github.com/git/git/tree/v2.56.0/Documentation/config
- [42] Git — git-clone, v2.56.0 — https://github.com/git/git/blob/v2.56.0/Documentation/git-clone.adoc
- [43] Alex Chaplinsky — Git worktrees are not an isolation boundary for coding agents (Fletch blog, 2026; opinion; the author builds Fletch) — https://fletch.sh/blog/git-worktrees-vs-clones-for-ai-agents/
- [44] GitHub — Events that trigger workflows, `push` — https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#push
- [45] Microsoft — VS Code git extension, `extensions/git/package.json` (`git.autoRepositoryDetection`, `git.repositoryScanMaxDepth`) — https://github.com/microsoft/vscode/blob/f3f3fc2b8c71193754d5b2a24807611d1acf3cf3/extensions/git/package.json
- [46] Git — git(1), SECURITY, v2.56.0 — https://github.com/git/git/blob/v2.56.0/Documentation/git.adoc
- [47] Docker — Linux post-installation steps for Docker Engine — https://docs.docker.com/engine/install/linux-postinstall/
- [48] Testcontainers — Patterns for running tests inside a Docker container — https://java.testcontainers.org/supported_docker_environment/continuous_integration/dind_patterns/
- [49] Docker — docker container run (CLI reference), `--privileged` — https://docs.docker.com/reference/cli/docker/container/run/
- [50] Docker Official Images — docker (Docker Hub page), the `dind-rootless` variant — https://hub.docker.com/_/docker
- [51] Nestybox — Sysbox user guide: Docker-in-Docker, installation, distro compatibility — https://github.com/nestybox/sysbox/tree/master/docs
- [52] Docker — Docker Sandboxes: Architecture — https://docs.docker.com/ai/sandboxes/architecture/
- [53] Docker — Docker Sandboxes: Develop and test locally — https://docs.docker.com/ai/sandboxes/workflows/development/
- [54] Docker — Docker Sandboxes: Troubleshooting — https://docs.docker.com/ai/sandboxes/troubleshooting/
- [55] Docker — docker/sbx-releases (license and releases) — https://github.com/docker/sbx-releases
- [56] Docker — Running AI Agents in GitHub Actions with Docker Sandboxes (Docker blog, 2026; kind not confirmed) — https://www.docker.com/blog/running-ai-agents-in-github-actions-with-docker-sandboxes/
- [57] Testcontainers — Testcontainers Cloud documentation — https://testcontainers.com/cloud/docs/
- [58] Testcontainers — Testcontainers Cloud pricing — https://testcontainers.com/cloud/pricing/
- [59] Development Containers — Dev Container metadata reference (`initializeCommand`) — https://containers.dev/implementors/json_reference/
- [60] Development Containers — devcontainers/cli, `src/spec-node/devContainersSpecCLI.ts` — https://github.com/devcontainers/cli/blob/155f8b29e1c521bf365e2aebd74f3258a9160718/src/spec-node/devContainersSpecCLI.ts
- [61] Development Containers — Dev Container metadata in images, merge logic — https://github.com/devcontainers/spec/blob/main/docs/specs/image-metadata.md
- [62] Development Containers — Lockfiles (`devcontainer-lock.json`) — https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainer-lockfile.md
- [63] Microsoft — Visual Studio Code 1.118 release notes — https://code.visualstudio.com/updates/v1_118
- [64] Microsoft — Sharing Git credentials with your container (VS Code docs) — https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials
- [65] matta — Leveraging VSCode internals to escape containers (The Red Guild blog, 2025; case) — https://blog.theredguild.org/leveraging-vscode-internals-to-escape-containers/
- [66] Christof Marti — replies in "SSH still available in container even I disable `forwardWSLServices`" (GitHub, microsoft/vscode-remote-release issue #9897, 2024; opinion) — https://github.com/microsoft/vscode-remote-release/issues/9897
- [67] Christof Marti — reply in "How to use ssh-agent from devcontainer CLI ?" (GitHub, devcontainers/cli issue #441, 2023; opinion) — https://github.com/devcontainers/cli/issues/441
- [68] Anthropic — Advanced setup, install with npm (Claude Code docs) — https://code.claude.com/docs/en/setup
- [69] Anthropic — Settings reference (Claude Code docs) — https://code.claude.com/docs/en/settings-reference
- [70] Anthropic — Managed settings (Claude Code docs) — https://code.claude.com/docs/en/managed-settings
- [71] Anthropic — Choose a permission mode (Claude Code docs) — https://code.claude.com/docs/en/permission-modes
- [72] Anthropic — Server-managed settings (Claude Code docs) — https://code.claude.com/docs/en/server-managed-settings
- [73] Caleb White — worktree: link worktrees with relative paths (git commit 717af91, 2024; case) — https://github.com/git/git/commit/717af916cd69d2565aa2a7b7d73d895aa92ff392
- [74] Git — Git 2.48 release notes, v2.56.0 tree — https://github.com/git/git/blob/v2.56.0/Documentation/RelNotes/2.48.0.adoc
- [75] OpenAI — Cloud environment (Codex docs) — https://learn.chatgpt.com/docs/environments/cloud-environment
- [76] Docker — Docker Sandboxes release notes — https://docs.docker.com/ai/sandboxes/release-notes/
- [77] cristian-popa — comment in "postStartCommand silently skipped when git-credential-sharing copy fails, and dev.containers.copyGitConfig=false doesn't suppress the attempt" (GitHub, microsoft/vscode-remote-release issue #11869, 2026; case) — https://github.com/microsoft/vscode-remote-release/issues/11869#issuecomment-5803453093
