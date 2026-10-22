# Dockerfile instructions

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. The baseline every service image has](#2-the-baseline-every-service-image-has)
- [3. Instructions](#3-instructions)
- [4. Parser directives](#4-parser-directives)
- [5. Common mistakes](#5-common-mistakes)
- [6. Where these rules stop holding](#6-where-these-rules-stop-holding)
- [7. Sources](#7-sources)

## 1. Purpose and the one rule

This file is for everyone who writes, changes or reviews a `Dockerfile`: people and AI agents
alike. For each instruction it says what the instruction does, when you need it, and when it is
over-engineering or does harm. The rules for the image as a whole (the build context, the base
image and its pins, build secrets, the running process) are [images.md](images.md); this file
links them and does not repeat them. [dockerfile-example.md](dockerfile-example.md) shows the
baseline in one file.

The one rule: **write an instruction only when it changes what the image holds or how its process
runs, or when a reader or a tool needs what it records (`EXPOSE`, `LABEL`). Six instructions carry
a service image; each of the others answers one need, named in its row below.**

Why it matters:

- Every instruction is a line the next reader must understand and keep correct. One added "just in
  case" costs that reading and buys nothing.
- Some instructions keep costing after you add them. `VOLUME` gives every container a volume filled
  from the image [1], `ONBUILD` runs inside the builds of other images [1], and a shell-form
  `ENTRYPOINT` keeps the process from receiving signals [1].
- Docker's own best-practices page puts no instruction in a tier [2], so this file names the
  condition for each one.

## 2. The baseline every service image has

| Instruction | Why every service image has it |
|---|---|
| `FROM` | starts the stage, pinned by tag and digest ([images.md](images.md) section 4) |
| `WORKDIR` | the directory for the later steps that use a relative path ([images.md](images.md) section 3); a stage with no such step, whose process needs no start directory, needs none (this practice's own call; section 3 shows Docker's advice against it) |
| `COPY` | brings in the lock file first, then the source ([images.md](images.md) section 3) |
| `RUN` | installs the dependencies and the project |
| `USER` | runs the process as a non-root user ([images.md](images.md) section 6) |
| `CMD` | starts the server in exec form ([images.md](images.md) section 6) |

The parser directives `# syntax=` and `# check=error=true` sit above them ([images.md](images.md)
section 7). `ARG`, `ENV`, `EXPOSE` and `LABEL` are common too, each for the need its row in
section 3 names.

## 3. Instructions

| Instruction | What it does | Use it when | Leave it out when |
|---|---|---|---|
| `FROM` | Starts a build stage from an image. "Each `FROM` instruction clears any state created by previous instructions" [1]. | Required, once per stage: "a valid Dockerfile must start with a `FROM` instruction" [1]. Add `--platform=$BUILDPLATFORM` to a builder stage that compiles for another platform [1]. | You would give `--platform` a fixed value such as `linux/amd64`: the build check `FromPlatformFlagConstDisallowed` flags it [3]. |
| `ARG` | A variable for the build, in scope from its line to the end of the stage. It is not in the container's environment, but its value stays in `docker history` and in max-level provenance [1]. | A value a build may change, such as one base-image pin that two `FROM` lines share ([images.md](images.md) section 11). | The value is a credential ([images.md](images.md) section 5), or the running process reads it: that is `ENV`. |
| `ENV` | Sets a variable in the image and in every container started from it [1]. | The process needs the value at run time, such as `PATH` or `PYTHONUNBUFFERED`. | Only the build needs it, in a stage that ships: Docker's advice is for a variable "only needed during build, and not in the final image" [1], so set it on the one `RUN` line or use `ARG`. A builder stage's `ENV` does not reach the final image. Never for a credential ([images.md](images.md) section 5). |
| `WORKDIR` | Sets the directory for the instructions after it, `CMD` and `ENTRYPOINT` included, so also the directory the container's process starts in, and creates it; without it, the directory is `/` [1]. | A later step uses a relative path: set the directory as [images.md](images.md) section 3 says. Also when the process, or a command run with `docker exec`, must start in that directory, as in the agent's image of [agent-container-example.md](agent-container-example.md) [1], [26]. | No later step uses a relative path and nothing at run time relies on the directory, as in the runtime stage of [dockerfile-example.md](dockerfile-example.md) (this practice's own call: then the line changes nothing the image does; Docker's reference advises setting `WORKDIR` explicitly "to avoid unintended operations in unknown directories" [1]). |
| `COPY` | Copies files from the build context, another stage or an image. Without `--chown`, the files belong to UID and GID 0 [1]. | Every local file the image needs, and `--from=<stage>` between stages. `--link` when you want the copy's layer reused after an earlier layer changes: the files stay on a layer of their own [1]. Not where the destination path holds a symlink the copy must follow, which `--link` cannot follow [1]. | `--chown` for the code or its virtual environment: who owns them is [images.md](images.md) section 6, and [images.md](images.md) section 12 lifts that rule for an image a person or an agent works in. A directory the service writes takes `--chown` as [images.md](images.md) section 6 says. |
| `ADD` | Like `COPY`, and also unpacks local tar archives and downloads URLs [1]. | A file you download during the build, with `--checksum` so the build checks what it got [1]; Docker calls `ADD` "best for when you need to download a remote artifact" [2]. | The file is local: [images.md](images.md) section 3 asks for `COPY`. |
| `RUN` | Runs a command and stores the result as a layer. `--mount` adds a cache, a bind, a tmpfs, a secret or an SSH agent for that one command [1]. | Installing and building. A cache mount for a package manager, which "should only be used for better performance" [1]; a secret mount for a credential ([images.md](images.md) section 5); `--mount=from=<image>` to use a tool such as uv without copying it into the image [4]. | One long chain mixes steps that change at different rates: split it, so an edit to the source reuses the install ([images.md](images.md) section 3). |
| `USER` | Sets the user for the instructions after it and for the container [1]. | Where [images.md](images.md) section 6 asks for one. Docker: "If a service can run without privileges, use `USER` to change to a non-root user" [2]. | A Docker container action on GitHub, which must not set `USER` ([images.md](images.md) section 12). |
| `EXPOSE` | Records the port the server listens on. "The `EXPOSE` instruction doesn't actually publish the port. It functions as a type of documentation" [1]. | The server's port, for readers and for tools that read it: Traefik sends traffic to the one port a container exposes [6]. | You mean to publish a port: that is `ports` in [compose-keys.md](compose-keys.md). |
| `CMD` | The default command, or the default arguments of `ENTRYPOINT`; only the last `CMD` counts [1]. | Every service image, in the form [images.md](images.md) section 6 asks for. | The shell form, `CMD acme-api` ([images.md](images.md) section 6); section 6 below says when a shell-form `CMD` is PID 1 anyway. |
| `ENTRYPOINT` | The fixed executable; `CMD` becomes its arguments, and setting it empties a `CMD` inherited from the base image [1]. | A wrapper script that prepares the container and ends with `exec "$@"`, so the server becomes PID 1 [2], or an init such as tini (section 6). | `CMD` alone starts the server. Never in shell form: it "ignores any `CMD` or `docker run` command line arguments", and the program "will not receive Unix signals" [1]. |
| `HEALTHCHECK` | A command the runtime runs to test the container: every 30 s, a 30 s timeout, 3 retries by default; `HEALTHCHECK NONE` turns off an inherited check [1]. | Where [images.md](images.md) section 6 puts the check in the image. | Where [images.md](images.md) section 6 puts the check outside the image, in `compose.yaml` or, under Kubernetes, in the probes; and an image that is not a long-running service ([images.md](images.md) section 12). |
| `STOPSIGNAL` | The signal `docker stop` sends; `SIGTERM` when left out [1]. | Where [images.md](images.md) section 6 asks for one; Kubernetes uses it too [14]. | Where it does not. |
| `LABEL` | Adds key-value metadata to the image [1]. | The OCI labels that tie the image to its repository and commit ([images.md](images.md) section 8). | The CI action already writes the label ([images.md](images.md) section 8). |
| `VOLUME` | Declares a mount point; each container gets a volume there, filled with the image's files at that path [1]. | Almost never in an image you write (this practice's own call): the runtime declares storage. | A service image: declare storage in `compose.yaml` ([compose-keys.md](compose-keys.md)). Docker's best practices encourage `VOLUME` for "mutable or user-serviceable parts of your image" [2]; this practice does not follow them, because every container then gets a volume that the stack did not declare [1]. A contributor's Moby issue argues the instruction "only causes problems"; a Moby member answered that `VOLUME` "is part of the OCI specification" [15]. |
| `SHELL` | Changes the shell that runs the shell form of `RUN`, `CMD` and `ENTRYPOINT`; `["/bin/sh", "-c"]` by default [1]. | A `RUN` pipes one command into another and hadolint checks the file ([images.md](images.md) section 3). Windows images [1]. | No `RUN` has a pipe, or hadolint is not used: the inline form of [images.md](images.md) section 3 does. |
| `ONBUILD` | Stores instructions that run in the build of each image that starts `FROM` this one [1]. | A base image that only your own team's builds extend, for a step every one of them needs (this practice's own call; Docker's reference names a base image for other builds as the use [1]). | Others build on the image and it puts `ADD` or `COPY` in `ONBUILD`: Docker warns the image "fails catastrophically if the new build's context is missing the resource being added" and advises a separate tag [2]. This practice's own call: skip it for a base image outside your team, because a trigger the downstream author did not write is hard to see. |
| `MAINTAINER` | Deprecated [1]. | Never. | Always: write `LABEL org.opencontainers.image.authors` instead [1]. |

## 4. Parser directives

| Directive | What it does | Use it when | Leave it out when |
|---|---|---|---|
| `# syntax=` | Chooses the frontend that reads the file; without it, BuildKit uses the version it bundles [1]. | Every Dockerfile the repository keeps, pinned to a version and a digest: the ones CI builds, and the image a person or an agent works in ([images.md](images.md) sections 4, 7 and 12). | A throwaway build that is never kept or pushed, such as the build that only lists the context in [images.md](images.md) section 2 (this practice's own call). |
| `# check=` | Sets the build checks: `skip=<rules>` and `error=true`. By default a failed check is a warning and the build exits 0 [1]. | `error=true`, as [images.md](images.md) section 7 asks. For one false positive, `# check=skip=<Rule>` on the line above that instruction, from frontend 1.21.0 [25], [18], with the reason on a comment line above it, as [static-checks.md](../../python/static-checks/static-checks.md) section 6 asks of every suppression; `SecretsUsedInArgOrEnv`, for example, flags names such as `KMS_KEY_ALIAS` [19]. | You would skip a rule for the whole file, which also hides its real hits. |
| `# escape=` | Sets the line-continuation character; `\` by default [1]. | A Windows image, with a backtick [1]. | Every Linux image. |

## 5. Common mistakes

Each row's "Leave it out when" cell in section 3 names the mistake for that instruction.

## 6. Where these rules stop holding

- **A shell-form `CMD` with one command.** dash, `/bin/sh` on Debian [29], runs a single
  `sh -c` command in place of the shell, without a fork [27], and BusyBox's ash on Alpine does the
  same [21], so such a `CMD` is often PID 1 after all. With more than one command, the shell stays
  PID 1 while the earlier ones run [27], and with a trap set it always forks and stays PID 1 [28].
  The exec form does not depend on the shell, so keep it.
- **Kubernetes.** KEP-495 lists "a general purpose container init solution" as a non-goal [22].
  Its shared PID namespace lets the pod's infra container reap orphaned zombies, and then the main
  process is no longer PID 1 [22]. Without it, the process is PID 1 with no init; that Kubernetes
  has no counterpart to `docker run --init` is this practice's reading. Where
  [images.md](images.md) section 6 asks for an init, put tini in `ENTRYPOINT`, as its README
  shows [23].
- **Builders other than BuildKit.** Kaniko does not support `RUN --mount` [24], so the cache, bind
  and secret mounts in section 3 need BuildKit.
- **Windows images.** `escape` and `SHELL` are most useful there [1]; this practice does not cover
  Windows containers ([images.md](images.md) section 12).

## 7. Sources

Checked 2026-10-16 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Docker (moby/buildkit) — Dockerfile reference, frontend docker/dockerfile 1.28.0 — https://github.com/moby/buildkit/blob/dockerfile/1.28.0/frontend/dockerfile/docs/reference.md
- [2] Docker — Building best practices — https://github.com/docker/docs/blob/main/content/manuals/build/building/best-practices.md
- [3] Docker (moby/buildkit) — Build checks — https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/rules/_index.md
- [4] Astral — uv: Using uv in Docker, uv 0.13.1 — https://github.com/astral-sh/uv/blob/0.13.1/docs/guides/integration/docker.md
- [6] Traefik Labs — Traefik docs: Docker provider — https://github.com/traefik/traefik/blob/master/docs/content/reference/install-configuration/providers/docker.md
- [14] Kubernetes — KEP-4960, container stop signals — https://github.com/kubernetes/enhancements/tree/master/keps/sig-node/4960-container-stop-signals
- [15] Brennan Kinney — Deprecate `VOLUME` instruction for future removal (GitHub, moby/moby issue #49482, 2025; opinion) — https://github.com/moby/moby/issues/49482 — checked 2026-10-17
- [18] Jonathan A. Sternberg — dockerfile: add syntax to skip a check (GitHub, moby/buildkit pull request #6334, 2025; case) — https://github.com/moby/buildkit/pull/6334
- [19] Nuru — Allow better tuning of SecretsUsedInArgOrEnv check (GitHub, moby/buildkit issue #5775, 2025; opinion) — https://github.com/moby/buildkit/issues/5775
- [21] Denys Vlasenko — ash: [SHELL] Optimize dash -c "command" to avoid a fork (BusyBox, commit 1e3e2ccd5d, 2017; case) — https://github.com/rsalvaterra/busybox/commit/1e3e2ccd5d
- [22] Kubernetes — KEP-495, sharing the process namespace of a pod — https://github.com/kubernetes/enhancements/blob/master/keps/sig-node/495-pod-pid-namespace/README.md
- [23] krallin — tini README — https://github.com/krallin/tini
- [24] Guillaume Déflache — Support bind Build Mounts (RUN --mount=type=bind / RUN --mount) like BuildKit and Buildah do (GitHub, GoogleContainerTools/kaniko issue #1568, 2021; opinion) — https://github.com/GoogleContainerTools/kaniko/issues/1568
- [25] Docker (moby/buildkit) — release notes, dockerfile/1.21.0 — https://github.com/moby/buildkit/releases/tag/dockerfile%2F1.21.0
- [26] Docker — docker container exec reference, v29.9.1 — https://github.com/docker/cli/blob/v29.9.1/docs/reference/commandline/container_exec.md
- [27] Herbert Xu — [SHELL] Optimize dash -c "command" to avoid a fork (dash on git.kernel.org, commit ee5cbe9, 2011; case) — https://git.kernel.org/pub/scm/utils/dash/dash.git/commit/?id=ee5cbe9fd6bc02f31b4d955606288de36c3d4eab
- [28] Jilles Tjoelker — [EVAL] Force fork if any trap is set, not just on EXIT (dash on git.kernel.org, commit 699170f, 2010; case) — https://git.kernel.org/pub/scm/utils/dash/dash.git/commit/?id=699170f4c835d8ec8e310f58c34c6d158dd37d71
- [29] Debian — Debian Wiki: Shell — https://wiki.debian.org/Shell — checked 2026-10-17
