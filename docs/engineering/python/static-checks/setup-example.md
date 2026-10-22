# Example: the checks of a service, from the lock file to CI

A worked example for [static-checks.md](static-checks.md). It shows the three files that set up the
checks of a Python service laid out as in
[file-structure.md](../../any-language/file-structure/file-structure.md): `pyproject.toml`, `.pre-commit-config.yaml`
and the CI workflow. The package is `shop`, and `acme_sdk` stands for a third-party library that
ships no types. The rest of `pyproject.toml` (the project table's other keys, the
`[build-system]` table, which uv needs to install `shop` so that `lint-imports` can import it, and
the import-linter contracts of
[layout-example.md](../../any-language/file-structure/layout-example.md) section 3) is cut with `...`. The
service's `.python-version` holds `3.13`, the minor its `requires-python` allows
([ci-cd/pipeline.md](../../any-language/ci-cd/pipeline.md) section 9). This example's
`[tool.ruff.lint]` and `[tool.ruff.lint.flake8-tidy-imports]` tables replace the two in
[layout-example.md](../../any-language/file-structure/layout-example.md) section 3: `TID252` is listed here with
the other rules.

**Navigation**

- [1. pyproject.toml: tools, versions, rules](#1-pyprojecttoml-tools-versions-rules)
- [2. .pre-commit-config.yaml: the hooks](#2-pre-commit-configyaml-the-hooks)
- [3. The CI workflow](#3-the-ci-workflow)
- [4. What a developer runs](#4-what-a-developer-runs)

## 1. pyproject.toml: tools, versions, rules

```toml
[project]
...
# One minor, the one .python-version pins: uv refuses any other Python, and ruff targets this
# one (ci-cd pipeline section 9, static-checks section 3).
requires-python = "==3.13.*"

[dependency-groups]
dev = [
    "import-linter>=2.15",
    "mypy>=2.3",
    "pre-commit>=4.4",
    "ruff>=0.16",
]

[tool.uv]
required-version = ">=0.11"

[tool.ruff.lint]
extend-select = [
    "E4", "F403", "I001",                              # readability section 8
    "E7", "SIM115",                                    # python section 6; readability 3, 7 and 8
    "RET502", "RET503",                                # python section 6
    "N", "PYI042",                                     # readability section 7
    "D", "W505",                                       # readability sections 4 and 8
    "TID252",                                          # file-structure section 7
    "G", "LOG", "TRY400", "TRY401", "BLE001", "T201",  # logging section 11
    "RET505", "RET506", "ERA001",                      # readability sections 3 and 4
    "PGH003", "PGH004", "RUF100",                      # static-checks section 6
    "PT",                                              # testing: running-tests section 11
]
ignore = [
    "D1",            # readability section 4: a docstring only where the name leaves a gap
    "D206", "D300",  # the formatter already writes what these check (readability section 8)
    "PT003",  # testing: fixtures section 1 asks for scope="function", which PT003 reports
]

[tool.ruff.lint.per-file-ignores]
# readability section 4: a test's first sentence may run over two lines
"tests/**" = ["D205"]

[tool.ruff.lint.pycodestyle]
max-doc-length = 88  # readability section 8: comments and docstrings at the code's width

[tool.ruff.lint.pydocstyle]
convention = "pep257"  # readability section 4
property-decorators = ["pytest.fixture", "pytest_asyncio.fixture"]  # readability section 4: a fixture's summary names what it gives

[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "all"  # file-structure section 7

[tool.mypy]
# No python_version: mypy checks against the interpreter it runs on, and uv runs it on the
# pinned one, so a copy here could only fall behind (static-checks section 3).
strict = true
enable_error_code = ["ignore-without-code", "exhaustive-match"]  # static-checks section 6, python section 2
plugins = ["pydantic.mypy"]  # python section 5
files = ["src", "tests"]  # add "evals" when the repository has an evals/ folder (evals section 4)
mypy_path = "src"
explicit_package_bases = true

[[tool.mypy.overrides]]
# acme_sdk ships no types and no stub package, and our few calls do not pay for local stubs.
module = ["acme_sdk", "acme_sdk.*"]
ignore_missing_imports = true

[tool.pydantic-mypy]
init_typed = true
```

| Part | What it does |
|---|---|
| `requires-python = "==3.13.*"` | the one minor the service runs, the same as `.python-version` ([ci-cd/pipeline.md](../../any-language/ci-cd/pipeline.md) section 9; a library keeps a floor, section 12). ruff takes its target version from it, so no `target-version` is set ([static-checks.md](static-checks.md) section 3) |
| `[dependency-groups] dev` | every checking tool is a dev dependency; `uv lock` pins the exact versions in `uv.lock`, the one pin (section 3) |
| `[tool.uv] required-version` | the lowest uv the project accepts: an older local uv stops with a clear error, and `setup-uv` reads it and installs the newest uv that matches. It is a floor, not a pin, so CI's uv moves with each uv release |
| `extend-select` | turns on each rule a practice relies on, with the section it serves. ruff's default set leaves out most PEP 8 checks; `extend-select` adds to that set and keeps it. A rule the default set holds is listed too, `I001` and `SIM115` included, for the reason [static-checks.md](static-checks.md) section 2 gives |
| `ignore` | the rules of a selected group that a practice contradicts, or that the formatter makes redundant, each with the section that says why |
| `per-file-ignores` | the one docstring rule that gives way under `tests/`: `D205` ([readability.md](../../any-language/readability/readability.md) section 4 says why) |
| `max-doc-length = 88` | the width `W505` checks for comments and docstrings, the formatter's line length; without the setting `W505` checks nothing |
| `convention = "pep257"` | the `D` rules PEP 257 asks for, and none of the rules of the other conventions that contradict it |
| `property-decorators = ["pytest.fixture", "pytest_asyncio.fixture"]` | `D401` skips the summary of a function under either decorator, as it does for a `@property`, so a fixture's summary may name what it gives; every other `D` rule still checks its docstring. [readability.md](../../any-language/readability/readability.md) section 4 says why |
| `ban-relative-imports` | the setting `TID252` needs to fail on every relative import |
| no `python_version` | mypy checks against the interpreter that runs it, and `uv run --locked` runs it on the pinned 3.13, so the hook and CI, the gate, check against the Python the service runs; an editor checks against the interpreter it is pointed at, so point it at the project's `.venv`. A copy of the version here would be one more line a version bump could miss ([static-checks.md](static-checks.md) section 3); a library sets it to the oldest version it supports |
| `strict = true` | the strict mode [static-checks.md](static-checks.md) section 2 asks for; it includes `warn_unused_ignores` |
| `enable_error_code` | two checks outside `--strict`: a bare `# type: ignore`, and a `match` that misses a member |
| `plugins = ["pydantic.mypy"]` | lets mypy read pydantic models the way pydantic builds them, so a settings class whose fields have no default type-checks when `main()` builds it with no arguments ([python.md](../language/python.md) section 5); only in a repository that depends on pydantic, since mypy imports the plugin from it |
| `files`, `mypy_path`, `explicit_package_bases` | what to check, and how to name the modules: the package under `src/`, and test files that share a name in different folders ([python/testing/layout.md](../testing/layout.md) section 6) without a clash; `tests/` must hold at least one `.py` file, or mypy stops with an error; `evals/` joins the list only in a repository that has one ([python/evals/evals.md](../evals/evals.md) section 4), for the same reason |
| `[[tool.mypy.overrides]]` | the one untyped library, silenced by name; every other missing import still fails |
| `[tool.pydantic-mypy]` | `init_typed` types the arguments of the `__init__` the plugin writes, so a wrong type passed to a model fails the check; `init_forbid_extra` stays off, because it rejects the aliases third-party models accept, such as `ChatOpenAI(model=...)` |

It is good because the checkers read the Python version from the project instead of holding a copy
of it: ruff from `requires-python`, mypy from the interpreter uv runs it on, so a version bump
cannot leave a checker behind; and every rule a practice relies on is selected by name, next to the
section it serves.

## 2. .pre-commit-config.yaml: the hooks

```yaml
minimum_pre_commit_version: "4.4.0"

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
        args: [--enforce-all]  # every file, not only staged ones, so CI checks the whole tree
      - id: check-merge-conflict
        # Without it the check fires only during a merge, so CI would pass a committed
        # marker; a seven-= underline also fails: lengthen it.
        args: [--assume-in-merge]
      - id: detect-private-key

  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        entry: uv run --locked ruff check --fix --force-exclude
        language: unsupported
        types_or: [python, pyi]
        require_serial: true

      - id: ruff-format
        name: ruff format
        entry: uv run --locked ruff format --force-exclude
        language: unsupported
        types_or: [python, pyi]
        require_serial: true

      - id: mypy
        name: mypy
        entry: uv run --locked mypy
        language: unsupported
        # The whole project at every commit, so a caller broken in another file is
        # caught (static-checks.md section 4).
        always_run: true
        pass_filenames: false

      - id: lint-imports
        name: import contracts
        entry: uv run --locked lint-imports
        language: unsupported
        pass_filenames: false
        always_run: true
```

| Part | What it does |
|---|---|
| `minimum_pre_commit_version` | `language: unsupported` exists from 4.4.0; an older pre-commit stops with a clear message instead of a parse error |
| `pre-commit-hooks`, `rev: v6.0.0` | the file hygiene checks; the project runs them nowhere else, so this `rev:` is their one pin |
| `--enforce-all`, `--assume-in-merge` | without them `check-added-large-files` looks only at staged files and `check-merge-conflict` only at a merge in progress, so in CI they would pass whatever the tree holds. With `--assume-in-merge`, a line of exactly seven `=` also fails, such as the underline of a seven-letter Markdown or reStructuredText title: make that underline longer, or use a `#` heading |
| `repo: local`, `entry: uv run --locked …` | ruff, mypy and lint-imports run from `uv.lock`, the same versions as CI and the editor |
| `ruff check --fix` | applies the linter's safe fixes; the commit stops, and the developer stages the fixed file |
| `ruff-check` before `ruff-format` | the linter's fixes can leave code the formatter must reflow, so the formatter runs last, as ruff's own pre-commit hooks advise |
| `--force-exclude`, `require_serial: true` | the two settings ruff's own hooks carry: ruff skips the files your `exclude` lists even when pre-commit passes them by name, and one ruff process sees all the files |
| `mypy`, `pass_filenames: false`, `always_run: true` | the whole project from `files`, at every commit, a commit that changes only `pyproject.toml` included, so a broken caller in another file is caught |
| `lint-imports`, `pass_filenames: false`, `always_run: true` | the import contracts of [file-structure.md](../../any-language/file-structure/file-structure.md) section 11, checked on the whole project at every commit |
| no `stages:` | every hook runs at commit; when the timed run shows mypy or lint-imports too slow, that hook moves to the push with the lines [static-checks.md](static-checks.md) section 4 gives |

## 3. The CI workflow

`.github/workflows/checks.yml`

```yaml
name: checks

on:
  pull_request:
  push:
    branches: [main]

permissions: {}  # nothing by default; the job asks for what it uses

concurrency:
  # A new push to a pull request cancels its older run; a run on main is never cancelled
  # (ci-cd/pipeline.md section 8).
  group: checks-${{ github.event.pull_request.number || github.run_id }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  checks:
    runs-on: ubuntu-24.04  # a version label: the OS changes only when this line does (ci-cd/pipeline.md section 9)
    timeout-minutes: 15  # a hung hook stops here, not after the default 360 minutes
    permissions:
      contents: read
    steps:
      # Pinned to the release's commit, the release in the comment (ci-cd/pipeline-security.md section 4).
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false  # the token is not left on the runner for the later steps

      - uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884  # v10.3.0
        with:
          # No python-version input: uv reads .python-version, and the input would override it (ci-cd/pipeline.md section 9).
          enable-cache: true

      - run: uv sync --locked

      - run: uv run --locked pre-commit run --all-files --show-diff-on-failure
```

| Step | What it does |
|---|---|
| `permissions: {}`, the job's `contents: read`, `persist-credentials: false` | the job reads the code and nothing more, and the token is not left on the runner for the later steps ([ci-cd/pipeline-security.md](../../any-language/ci-cd/pipeline-security.md) section 3) |
| each `uses:` pinned to a commit SHA, the release in a comment | a moved tag cannot change what runs; Renovate or Dependabot moves the pin and the comment together ([ci-cd/pipeline-security.md](../../any-language/ci-cd/pipeline-security.md) section 4) |
| `ubuntu-24.04`, `timeout-minutes: 15` | the runner's OS changes only in a pull request, and a hung job stops in minutes ([ci-cd/pipeline.md](../../any-language/ci-cd/pipeline.md) sections 8 and 9) |
| `concurrency` | a new push to a pull request cancels its older run; a run on `main` gets its own group and is never cancelled ([ci-cd/pipeline.md](../../any-language/ci-cd/pipeline.md) section 8) |
| setup-uv with no `python-version` input | `uv sync` takes the Python from `.python-version`, so the job runs the service's 3.13; the input would be a second copy of the minor: it sets `UV_PYTHON` over the pin, so on another minor `requires-python` fails the job, and the next minor move has one more file to change ([ci-cd/pipeline.md](../../any-language/ci-cd/pipeline.md) section 9) |
| `uv sync --locked` | installs the locked dev tools; fails when `uv.lock` does not match `pyproject.toml` |
| `pre-commit run --all-files` | runs every hook of section 2 on the whole tree: hygiene, lint, format, types, import contracts |
| `--show-diff-on-failure` | when a hook would change a file, the log shows the change, so the author sees what to fix |

It is good because the job runs the same hook file as a developer's commit, with the locked tools on
the pinned Python, reads the code and nothing more, and pins every action by commit, so its result
is the result a developer gets.

In the repository settings, the `checks` job is a required status check for `main`, so a red job
blocks the merge.

## 4. What a developer runs

```sh
uv sync                      # installs the locked tools
uv run pre-commit install    # the hooks now run on every commit
uv run pre-commit run --all-files
```

A clone without the second command has no hooks. That is why CI runs the same file: the hook saves
time, CI decides.

What this example does not claim: the action releases are the latest on 2026-10-18, each pinned to
the commit `git ls-remote` printed for it then. In a monorepo, the hook file sits at the root and
its Python hooks name the project's folder, as
[ci-cd/ci-example.md](../../any-language/ci-cd/ci-example.md) section 3 shows.
