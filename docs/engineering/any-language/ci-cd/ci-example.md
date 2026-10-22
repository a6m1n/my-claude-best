# Example: the CI workflow of a Python and React monorepo

A worked example for [pipeline.md](pipeline.md). One workflow checks every pull request of a
repository that holds a Python API in `backend/` and a React application in `frontend/`, and the
deploy workflow of [deploy-example.md](deploy-example.md) calls the same workflow on `main`
before it builds anything. It calls the security jobs of [security-example.md](security-example.md),
so its one gate needs them. This example scopes pull requests by path, the case of
[pipeline.md](pipeline.md) section 7 where a full run no longer fits the feedback budget; for a
repository whose full run fits, delete the `changes` job, the `if:` lines that read it and each
`needs: changes`, and keep `ci-ok` with `changes` taken out of its `needs`.

The repository, cut to the files this example touches:

```text
<repo>/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # this example
│   │   ├── deploy.yml          # deploy-example.md
│   │   ├── deploy-to.yml       # deploy-example.md
│   │   └── security.yml        # security-example.md, called by ci.yml and deploy.yml
│   └── CODEOWNERS              # security-example.md
├── .pre-commit-config.yaml     # the hook file, at the root because pre-commit runs from there
├── backend/                    # one Python application, laid out as file-structure.md section 9 says
│   ├── pyproject.toml          # requires-python "==3.13.*", dev tools, [tool.uv] required-version (static-checks setup-example.md section 1), [tool.alembic]
│   ├── uv.lock
│   ├── .python-version         # 3.13: every job and the image run this minor (pipeline.md section 9)
│   ├── Dockerfile              # dockerfile-example.md, with backend/ as the build context
│   ├── .dockerignore
│   ├── migrations/             # Alembic's env.py, which builds the application's Settings, and one file per schema change
│   ├── src/acme/api/
│   └── tests/{unit,integration}/
└── frontend/                   # one React application, laid out as layout-example.md says
    ├── package.json            # "packageManager" names pnpm; scripts typecheck, lint, test, build; size-limit as a dev dependency
    ├── .size-limit.json        # the budget's paths and value, as react/performance/performance.md section 3 sets them
    ├── pnpm-lock.yaml
    ├── pnpm-workspace.yaml     # the install settings of react/security/security-example.md
    └── .node-version
```

It is good because each project keeps its own lockfile and toolchain files in its folder, and only
what every project shares, `.github/` and the hook file, sits at the root.

Every action is pinned to the full commit SHA of the release in the comment beside it, read with
`git ls-remote https://github.com/<owner>/<repo> 'refs/tags/<release>*'` on 2026-10-18 (for an
annotated tag, the SHA on the line that ends in `^{}`). Renovate moves the SHA and the comment
together ([pipeline-security.md](pipeline-security.md) section 4). The Postgres service image of
`backend-integration` is pinned to the index digest that Docker Hub's registry returned for
`postgres:18-trixie` on 2026-10-18, and Renovate moves that digest too, because its GitHub Actions
manager reads the images under `services:` [11]. Nothing moves two other pins:
the gitleaks release the `frontend` job downloads, with its checksum from that release's checksums
file [10], and Trivy's `version:` in the `image` job. The pipeline owners of `CODEOWNERS` move
them by hand, with the same pins in [security-example.md](security-example.md) and
[deploy-example.md](deploy-example.md), when the tool's release notes name a security fix and at
each quarterly review. Before the first run, set the
repository variable `DOCKERHUB_USERNAME` and the secret `DOCKERHUB_TOKEN` (a Docker Hub token that
can only read), as [docker/ci-example.md](../docker/ci-example.md) says.

**Navigation**

- [1. The workflow](#1-the-workflow)
- [2. What each part does](#2-what-each-part-does)
- [3. The hook file at the root](#3-the-hook-file-at-the-root)
- [4. Sources](#4-sources)

## 1. The workflow

`.github/workflows/ci.yml`

```yaml
name: ci

on:
  pull_request:
  # Keep only where a merge queue is on (pipeline.md section 6).
  merge_group:
  # deploy.yml calls this workflow on main, so every check runs again before a build.
  workflow_call:
    secrets:
      DOCKERHUB_TOKEN:
        required: false  # the caller passes it by name; without it the Docker Hub logins are skipped
  # Weekly as well: fresh vulnerability databases turn an unchanged lockfile or image red.
  # Name who reads the result (pipeline-security.md section 7).
  schedule:
    - cron: "0 5 * * 1"

permissions: {}  # nothing by default; each job asks for what it uses

concurrency:
  # A new push to a pull request cancels its older run; a call from deploy.yml has a group of its own.
  group: ci-${{ github.event.pull_request.number || github.run_id }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  changes:
    # The scoped form, for a monorepo whose full run no longer fits the feedback budget (pipeline.md
    # section 7): pull requests run only the projects they change; the queue, main and the weekly
    # run run all of it. While a full run fits, delete this job, the if: lines that read it and
    # each needs: changes, and take changes out of ci-ok's needs.
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    permissions:
      pull-requests: read  # paths-filter reads the pull request's changed files through the API
    outputs:
      backend: ${{ steps.filter.outputs.backend }}
      frontend: ${{ steps.filter.outputs.frontend }}
    steps:
      - id: filter
        uses: dorny/paths-filter@ceb8a2b8f2d89434be7ff52d3de7ec3738c5cc9d  # v4.0.3
        with:
          # A file both sides depend on runs both sides.
          filters: |
            shared: &shared
              - .github/workflows/**
              - .pre-commit-config.yaml
            backend:
              - *shared
              - backend/**
              - .trivyignore  # the image job's waivers, at the root
            frontend:
              - *shared
              - frontend/**

  checks:
    # The hook file on every file, on every run (static-checks.md section 5).
    runs-on: ubuntu-24.04  # a version label, never ubuntu-latest: the OS changes only when this line does (pipeline.md section 9)
    timeout-minutes: 15  # a hung job stops here, not at GitHub's 360 minutes (pipeline.md section 8)
    permissions:
      contents: read
    steps:
      # Every action by full commit SHA, the release in the comment: a tag can be moved (pipeline-security.md section 4).
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false  # the token is not left on the runner for the steps after this one
      - uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884  # v10.3.0
        with:
          working-directory: backend  # reads required-version from the backend; uv reads .python-version there
          enable-cache: true
      - run: uv sync --locked --project backend
      - run: uv run --locked --project backend pre-commit run --all-files --show-diff-on-failure

  backend-unit:
    needs: changes
    # !cancelled() lets the job run when changes was skipped, on the queue and on main.
    if: ${{ !cancelled() && (github.event_name != 'pull_request' || needs.changes.outputs.backend == 'true') }}
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    permissions:
      contents: read
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884  # v10.3.0
        with:
          working-directory: backend
          enable-cache: true
      - run: uv sync --locked  # fails when uv.lock does not match pyproject.toml
      - run: uv run --locked pytest tests/unit

  backend-integration:
    needs: changes
    if: ${{ !cancelled() && (github.event_name != 'pull_request' || needs.changes.outputs.backend == 'true') }}
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    permissions:
      contents: read
    env:
      # Forks and Dependabot get no secrets; the login below is then skipped (pipeline.md section 4).
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
    services:
      # The empty scratch database of the migration check (pipeline.md section 5).
      postgres:
        # By digest, like every image the pipeline pulls (images.md section 4).
        image: postgres:18-trixie@sha256:74935e72241653ca55e0414067e6d8763aceb8a810eb51b452253ec3dcfc4336
        credentials:
          # With no token, as on a fork, the runner skips the login and pulls anonymously.
          username: ${{ vars.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
        env:
          POSTGRES_DB: acme
          POSTGRES_USER: acme
          # Not a secret: the database lives for this job only and holds no data.
          POSTGRES_PASSWORD: scratch
        # -h asks over TCP: on first start the image runs a temporary server on the socket only (compose.md section 3).
        options: >-
          --health-cmd "pg_isready -h 127.0.0.1 -U acme -d acme"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
        ports:
          - 5432:5432
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false
      # The tests start containers; logged-in pulls have their own Docker Hub limit.
      - uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f  # v4.6.0
        if: env.DOCKERHUB_TOKEN != ''  # if: may read env, never secrets; without the token the pulls are anonymous
        with:
          username: ${{ vars.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884  # v10.3.0
        with:
          working-directory: backend
          enable-cache: true
      - run: uv sync --locked
      - name: Migrations apply to an empty database and match the models
        env:
          # The application's own settings: env.py builds Settings, which reads them (python.md section 5).
          ACME_DATABASE_HOST: localhost
          ACME_DATABASE_NAME: acme
          ACME_DATABASE_USER: acme
          ACME_DATABASE_PASSWORD: scratch
          ACME_PAYMENTS_API_KEY: unused  # Settings has no default for it; no migration calls the provider
        run: |
          # Fails on a broken migration, and on a second head when two branches each added one (pipeline.md section 5).
          uv run --locked alembic upgrade head
          # Fails when a model changed and no migration says so; a rename or an unnamed constraint escapes it.
          uv run --locked alembic check
      # A hung test fails after two minutes, not at the job's timeout (running-tests.md section 9).
      - run: uv run --locked pytest tests/integration --timeout=120

  frontend:
    needs: changes
    if: ${{ !cancelled() && (github.event_name != 'pull_request' || needs.changes.outputs.frontend == 'true') }}
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    permissions:
      contents: read
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false
      - uses: pnpm/setup@a0881977cd8ea73b1ed212236c99ca10dcc80cf4  # v3.1.1
        with:
          working-directory: frontend  # pnpm from packageManager, Node from .node-version
          cache: true
          install: false  # the next step installs, so the command is in the workflow
      - run: pnpm install --frozen-lockfile  # fails when pnpm-lock.yaml does not match package.json
      - run: pnpm run typecheck
      - run: pnpm run lint
      - run: pnpm run test
      - run: pnpm run build
      # Fails the job when the bundle passes its budget; the rule and the value are
      # react/performance/performance.md section 3's, in .size-limit.json.
      - run: pnpm exec size-limit
      # Most front-end credentials show only in the built bundle (react/security/security.md section 9).
      - name: gitleaks over the built bundle
        run: |
          curl -sSfL -o gitleaks.tar.gz \
            https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz
          echo "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb  gitleaks.tar.gz" | sha256sum --check
          tar -xzf gitleaks.tar.gz gitleaks
          # --redact keeps a found secret out of the log; --ignore-gitleaks-allow stops a comment from hiding one.
          ./gitleaks dir dist --redact --ignore-gitleaks-allow --verbose
      # The bundle is built once; deploy.yml promotes these bytes (delivery.md section 3).
      - uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9  # v7.0.2
        if: github.event_name == 'push'  # in a call from deploy.yml, github.event_name is the caller's: push on main
        with:
          name: web-dist
          path: frontend/dist
          retention-days: 7  # deploy.yml copies it to the release store in the same run

  image:
    needs: changes
    if: ${{ !cancelled() && (github.event_name != 'pull_request' || needs.changes.outputs.backend == 'true') }}
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    permissions:
      contents: read
    env:
      # Forks and Dependabot get no secrets; the login below is then skipped (pipeline.md section 4).
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false
      - uses: docker/setup-buildx-action@f87e5991a6d7451dcb8d9637bfbc97413f497069  # v4.4.1
      - uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f  # v4.6.0
        if: env.DOCKERHUB_TOKEN != ''  # if: may read env, never secrets; without the token the pulls are anonymous
        with:
          username: ${{ vars.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      # Build checks run here and fail the build (# check=error=true in the Dockerfile).
      - uses: docker/build-push-action@c3c9e263c25d99ce0380d002d59b67737d91b0dc  # v7.4.0
        with:
          context: backend
          load: true
          tags: acme-api:test
          cache-from: type=gha,scope=acme-api
          cache-to: type=gha,scope=acme-api,mode=max
      - name: Test the image
        run: |
          test "$(docker run --rm acme-api:test id -u)" = 10001
          docker run --rm acme-api:test python -c "import acme.api.main"
          docker run --rm acme-api:test sh -c 'command -v acme-api'
          # The one path the service writes, read-only everywhere else, as compose.yaml runs it (images.md section 6).
          docker run --rm --read-only --tmpfs /tmp:mode=1770,uid=10001,gid=10001 acme-api:test python -c "import tempfile; tempfile.TemporaryFile().write(b'x')"
      # One scanner, one written policy: fail on critical and high findings that have a fix.
      - uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25  # v0.36.0
        with:
          image-ref: acme-api:test
          version: v0.76.0  # pins the Trivy release the action installs, so a new release cannot change the scan unseen
          severity: CRITICAL,HIGH
          ignore-unfixed: true
          exit-code: "1"

  security:
    # The security jobs of security.yml, called so the gate needs them: a job that fails on a finding
    # blocks the merge and, on main, the deploy. CodeQL's job stays green on an alert; the ruleset's
    # code scanning rule blocks the pull request (pipeline-security.md section 7).
    uses: ./.github/workflows/security.yml
    permissions:
      contents: read
      security-events: write  # CodeQL uploads its results
      actions: read  # the workflows job of security.yml asks for it

  ci-ok:
    # The one required check (pipeline.md section 6): green only when every job passed or skipped by its own if.
    if: always()
    needs: [changes, checks, backend-unit, backend-integration, frontend, image, security]
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    permissions: {}
    steps:
      - env:
          RESULTS: ${{ join(needs.*.result, ' ') }}
        run: |
          for result in $RESULTS; do
            case "$result" in
              success|skipped) ;;
              *) echo "a job this gate needs ended as: $result"; exit 1 ;;
            esac
          done
```

## 2. What each part does

| Part | Why |
|---|---|
| `pull_request`, `merge_group`, `workflow_call`, `schedule` | every pull request, the queue where one is on, the call from `deploy.yml` on `main`, and a weekly full run with fresh vulnerability databases ([pipeline.md](pipeline.md) section 4). No `paths:` on the workflow: a skipped required workflow stays Pending ([pipeline.md](pipeline.md) section 6) |
| `workflow_call` with `secrets: DOCKERHUB_TOKEN` | a called workflow gets only the secrets its caller passes [8]; `deploy.yml` passes this one by name, never `inherit`, so CI holds no other secret |
| `DOCKERHUB_TOKEN` in the job's `env`, and the login's `if: env.DOCKERHUB_TOKEN != ''` | a pull request from a fork or from Dependabot gets no secrets, so the login is skipped, the pulls are anonymous and the check still runs ([pipeline.md](pipeline.md) section 4). A step's `if:` may read `env` but never `secrets` [9] |
| `permissions: {}`, then one block per job | each job gets only what its steps use ([pipeline-security.md](pipeline-security.md) section 3) |
| `concurrency` | a new push cancels the pull request's older run; a call from `deploy.yml` gets its own group (`github.run_id`) and is never cancelled ([pipeline.md](pipeline.md) section 8) |
| `changes` on pull requests only | the scoped form, for a monorepo whose full run no longer fits the feedback budget ([pipeline.md](pipeline.md) section 7); while a full run fits, delete it, the `if:` lines that read it and each `needs: changes`, and take `changes` out of `ci-ok`'s `needs`. One output per side; `dorny/paths-filter` reads the changed files through the API, so the job needs no checkout and only `pull-requests: read` [1]. A change to a workflow or to the hook file runs both sides, and a change to the root `.trivyignore` runs the backend, whose `image` job reads it ([pipeline.md](pipeline.md) section 7) |
| `checks` with no condition | the hook file on every file of every run, as [static-checks.md](../../python/static-checks/static-checks.md) section 5 asks; section 3 below shows the root hook file |
| `!cancelled() && (… != 'pull_request' \|\| …)` | on the queue, on `main` and on the weekly run, `changes` is skipped and every side runs; on a pull request a side runs only when its files changed. `!cancelled()` is what lets a job run after a skipped `needs` [2] |
| `working-directory: backend` and `--project backend` | setup-uv reads the uv version from the folder it is given [3], and `uv sync` there takes the Python from `.python-version`; `--project` runs uv on the backend from the repository root, where pre-commit works |
| no `python-version` input on setup-uv | the input is a second copy of the minor: it sets `UV_PYTHON` over `.python-version` [3], so on another minor `requires-python` fails the job, and the next minor move has one more file to change; every job runs the pinned minor ([pipeline.md](pipeline.md) section 9) |
| `uv sync --locked` | installs exactly `uv.lock`, and fails when it is stale ([pipeline.md](pipeline.md) section 9) |
| `pytest tests/unit`, then `pytest tests/integration --timeout=120` in a job of its own | the two suites of [python/testing/README.md](../../python/testing/README.md), step 4 of "How to adopt" |
| `services: postgres`, pinned by digest, with `credentials` | the empty scratch database of the migration check, which the steps reach at `localhost` through the mapped port [12]; pinned by digest like every image ([images.md](../docker/images.md) section 4). The runner logs in to the registry only when both the username and the password are set, and otherwise pulls without a login [13], so the run of a fork's pull request still starts. The health check asks over TCP, for the reason [compose.md](../docker/compose.md) section 3 gives for this image |
| `POSTGRES_PASSWORD: scratch` and the `ACME_` variables of the migration step | the database lives for one job and holds no data, so its password protects nothing; real secrets follow [pipeline-security.md](pipeline-security.md) section 6. The step sets only the variables the application's settings class reads, and `env.py` builds that class ([python.md](../../python/language/python.md) section 5). The class has no default for `ACME_PAYMENTS_API_KEY`, so the step gives it a value no migration uses |
| `alembic upgrade head`, then `alembic check` | the migration check of [pipeline.md](pipeline.md) section 5: the first fails on a broken migration and on two heads [14], the second when a model changed and no migration covers it [15]. With another migration tool, use its own commands for the same two steps |
| `pnpm exec size-limit`, after the build | the size gate of [performance.md](../../react/performance/performance.md) section 3: size-limit "throws an error if the cost exceeds the limit" [16]. The budget's paths and value live in `.size-limit.json`, which this example leaves out because that practice sets them. `size-limit` and its `@size-limit/file` plugin, 14.2.0 on 2026-10-18, are dev dependencies installed from the lockfile, so they follow the install rules of [security.md](../../react/security/security.md) section 10 |
| `pnpm/setup` with `install: false`, then `pnpm install --frozen-lockfile` | pnpm's own action installs pnpm from `packageManager` and Node from `.node-version`, and caches the store [4]; the install is a step of its own so the lockfile flag is in the workflow. pnpm turns `--frozen-lockfile` on in CI by default, and with it an install fails when the lockfile needs an update [7] |
| `typecheck`, `lint`, `test`, `build` | the four scripts of [layout-example.md](../../react/architecture/layout-example.md). A departure from stage 1 of [pipeline.md](pipeline.md) section 5, which checks the format too: those scripts hold no formatter, the departure [layout-example.md](../../react/architecture/layout-example.md) section 1 declares. The cost: the frontend's code is not checked for format; where the application has Prettier ([libraries.md](../../react/architecture/libraries.md) section 5), add its check as a fifth script and step |
| gitleaks over `dist`, after the build | a bundle can hold a secret the source never showed, so the scan reads the build output ([security.md](../../react/security/security.md) section 9); the download is checked against the release's checksum, as in [security-example.md](security-example.md) |
| `upload-artifact` on `push` only | on `main` the bundle is kept for `deploy.yml`, which promotes those bytes ([delivery.md](delivery.md) section 3); a pull request builds it to prove it builds |
| `image` | the image job of [images.md](../docker/images.md) section 10 with `backend` as the context; it never pushes here; `deploy.yml` pushes and scans the pushed digest ([deploy-example.md](deploy-example.md) section 2). Its test runs the four checks of [docker/ci-example.md](../docker/ci-example.md): the user, the import, the entry point on `PATH` and the one path the service writes |
| `security` with `uses: ./.github/workflows/security.yml` | the security jobs of [security-example.md](security-example.md); `ci-ok` needs them, so a finding of the workflow linters, osv-scanner or gitleaks blocks the merge and, through `deploy.yml`'s call, the deploy. CodeQL's job stays green on an alert, and an alert blocks a pull request only through the ruleset's code scanning rule ([pipeline-security.md](pipeline-security.md) section 7). The call grants what those jobs ask for, and passes them no secret |
| `ci-ok` with `if: always()` | the gate: it runs even when a job it needs failed, and fails unless every needed job ended `success` or `skipped` ([pipeline.md](pipeline.md) section 6). It is the only required status check for `main` |
| `timeout-minutes` on every job that runs on a runner | a hung job stops after a few minutes, not after the default 360; the `security` call gets its timeouts from the jobs it calls ([pipeline.md](pipeline.md) section 8) |
| `ubuntu-24.04` | the runner's operating system changes only when this line does ([pipeline.md](pipeline.md) section 9) |

The check jobs of stages 1 to 5 of [pipeline.md](pipeline.md) section 5 run side by side, and
`ci-ok` collects them: a red job fails the gate, and the run takes as long as its slowest job.

It is good because a pull request runs every check the release runs and publishes nothing; a
change to one side runs that side's jobs and still reports one green check; and `main` runs all
of it again before [deploy-example.md](deploy-example.md) builds anything. The migration check and
the size gate fail the pull request that causes their problem, a model change with no migration or
a bundle over its budget, while each rule and its value stay with the practice that owns them; the
scratch database is pinned like every other image, and its password says at the line why it is no
secret.

In the repository settings, `ci-ok` is the required status check for `main`, with "Require
branches to be up to date before merging" on ([ruleset-example.md](../git/ruleset-example.md)).

The gate is written as a shell loop over `needs.*.result`, with no action. The `re-actors/alls-green`
action does the same job and adds lists of jobs that may fail or be skipped [5]; this example keeps
one third-party action fewer ([pipeline-security.md](pipeline-security.md) section 4).

What this example does not claim: it was not run when it was written. The actions are pinned to
the commit `git ls-remote` printed on 2026-10-18.

## 3. The hook file at the root

pre-commit runs every hook from the root of the repository, so in a monorepo the Python hooks of
[static-checks setup-example.md](../../python/static-checks/setup-example.md) section 2 tell uv
where the backend is. The hygiene hooks of that section stay as they are and are left out here;
the `local` hooks become:

`.pre-commit-config.yaml` (the `local` repo)

```yaml
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        # --project finds the backend's uv.lock; the file names stay relative to the root,
        # and ruff reads its settings from backend/pyproject.toml.
        entry: uv run --locked --project backend ruff check --fix --force-exclude
        language: unsupported
        types_or: [python, pyi]
        files: ^backend/
        require_serial: true

      - id: ruff-format
        name: ruff format
        entry: uv run --locked --project backend ruff format --force-exclude
        language: unsupported
        types_or: [python, pyi]
        files: ^backend/
        require_serial: true

      - id: mypy
        name: mypy
        # --directory runs mypy inside backend/, where its files and settings are.
        entry: uv run --locked --directory backend mypy
        language: unsupported
        always_run: true
        pass_filenames: false

      - id: lint-imports
        name: import contracts
        entry: uv run --locked --directory backend lint-imports
        language: unsupported
        always_run: true
        pass_filenames: false
```

| Part | Why |
|---|---|
| `--project backend` | uv uses the backend's project and lock while the file names pre-commit passes stay relative to the root [6] |
| `--directory backend` | mypy and lint-imports take no file names, so they run inside `backend/`, where `[tool.mypy] files` and the import contracts point [6] |
| `files: ^backend/` | the ruff hooks see only the backend's files |

It is good because CI and a developer's commit run the same hook file, as
[static-checks.md](../../python/static-checks/static-checks.md) section 5 asks, and nothing in it
assumes the Python project sits at the root.

## 4. Sources

Checked 2026-10-18 unless a line ends with — checked <YYYY-MM-DD>.

- [1] dorny — paths-filter, README, v4.0.3 — https://github.com/dorny/paths-filter/blob/v4.0.3/README.md
- [2] GitHub — Workflow syntax for GitHub Actions: `jobs.<job_id>.needs` — https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idneeds
- [3] Astral — setup-uv, README, v10.3.0 — https://github.com/astral-sh/setup-uv/blob/v10.3.0/README.md
- [4] pnpm — setup, action.yml, v3.1.1 — https://github.com/pnpm/setup/blob/v3.1.1/action.yml
- [5] re-actors — alls-green, README, v1.3.0 — https://github.com/re-actors/alls-green/blob/v1.3.0/README.md
- [6] Astral — uv: Commands reference (`--project`, `--directory`), uv 0.13.1 — https://docs.astral.sh/uv/reference/cli/
- [7] pnpm — pnpm install (`--frozen-lockfile`) — https://pnpm.io/cli/install
- [8] GitHub — Reuse workflows: passing inputs and secrets — https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
- [9] GitHub — Contexts reference: Context availability — https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#context-availability
- [10] Zachary Rice — gitleaks, checksums file of release v8.30.1 — https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_checksums.txt
- [11] Renovate — `github-actions` manager, `extract.ts` (images under `container:` and `services:`), 44.167.5 — https://github.com/renovatebot/renovate/blob/44.167.5/lib/modules/manager/github-actions/extract.ts
- [12] GitHub — Creating PostgreSQL service containers: running jobs directly on the runner machine — https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers
- [13] GitHub — actions/runner, `src/Runner.Worker/ContainerOperationProvider.cs` (`ContainerRegistryLogin`), v2.338.0 — https://github.com/actions/runner/blob/v2.338.0/src/Runner.Worker/ContainerOperationProvider.cs
- [14] SQLAlchemy — Alembic: Working with Branches, 1.20.0 — https://github.com/sqlalchemy/alembic/blob/rel_1_20_0/docs/build/branches.rst
- [15] SQLAlchemy — Alembic: Auto Generating Migrations (`alembic check`), 1.20.0 — https://github.com/sqlalchemy/alembic/blob/rel_1_20_0/docs/build/autogenerate.rst
- [16] Andrey Sitnik — size-limit, README, 14.2.0 — https://github.com/ai/size-limit/blob/14.2.0/README.md
