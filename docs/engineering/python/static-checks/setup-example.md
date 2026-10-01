# Example: the checks of a service, from the lock file to CI

A worked example for [static-checks.md](static-checks.md). It shows the three files that set up the
checks of a Python service laid out as in
[file-structure.md](../../any-language/file-structure/file-structure.md): `pyproject.toml`, `.pre-commit-config.yaml`
and the CI workflow. The package is `shop`, and `acme_sdk` stands for a third-party library that
ships no types. The rest of `pyproject.toml` (the project table with its `[build-system]`, which uv
needs to install `shop` so that `lint-imports` can import it, and the import-linter contracts of
[layout-example.md](../../any-language/file-structure/layout-example.md) section 3) is left out. This example's
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
    "TID252",                                          # file-structure section 7
    "G", "LOG", "TRY400", "TRY401", "BLE001", "T201",  # logging section 11
    "RET505", "RET506", "ERA001",                      # readability sections 3 and 4
    "PGH003", "PGH004", "RUF100",                      # static-checks section 6
    "PT",                                              # testing: running-tests section 11
]
# testing: fixtures section 1 asks for scope="function" in writing, which PT003 reports
ignore = ["PT003"]

[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "all"

[tool.mypy]
python_version = "3.11"
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
| `[dependency-groups] dev` | every checking tool is a dev dependency; `uv lock` pins the exact versions in `uv.lock`, the one pin (section 3) |
| `[tool.uv] required-version` | the lowest uv the project accepts: an older local uv stops with a clear error, and `setup-uv` reads it and installs the newest uv that matches. It is a floor, not a pin, so CI's uv moves with each uv release |
| `extend-select` | turns on each rule a practice relies on, with the section it serves; ruff's default set covers few of them |
| `ignore` | the one rule of a selected group that a practice contradicts, with the section that says why |
| `ban-relative-imports` | the setting `TID252` needs to fail on every relative import |
| `python_version = "3.11"` | checks against the oldest Python the project supports ([python.md](../language/python.md) section 1), whatever interpreter runs mypy |
| `strict = true` | the strict mode [static-checks.md](static-checks.md) section 2 asks for; it includes `warn_unused_ignores` |
| `enable_error_code` | two checks outside `--strict`: a bare `# type: ignore`, and a `match` that misses a member |
| `plugins = ["pydantic.mypy"]` | lets mypy read pydantic models the way pydantic builds them, so a settings class whose fields have no default type-checks when `main()` builds it with no arguments ([python.md](../language/python.md) section 5); only in a repository that depends on pydantic, since mypy imports the plugin from it |
| `files`, `mypy_path`, `explicit_package_bases` | what to check, and how to name the modules: the package under `src/`, and test files that share a name in different folders ([python/testing/layout.md](../testing/layout.md) section 6) without a clash; `tests/` must hold at least one `.py` file, or mypy stops with an error; `evals/` joins the list only in a repository that has one ([python/evals/evals.md](../evals/evals.md) section 4), for the same reason |
| `[[tool.mypy.overrides]]` | the one untyped library, silenced by name; every other missing import still fails |
| `[tool.pydantic-mypy]` | `init_typed` types the arguments of the `__init__` the plugin writes, so a wrong type passed to a model fails the check; `init_forbid_extra` stays off, because it rejects the aliases third-party models accept, such as `ChatOpenAI(model=...)` |

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
        args: [--enforce-all]
      - id: check-merge-conflict
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

permissions:
  contents: read

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          persist-credentials: false

      - uses: astral-sh/setup-uv@v10.2.0
        with:
          enable-cache: true

      - run: uv sync --locked

      - run: uv run --locked pre-commit run --all-files --show-diff-on-failure
```

| Step | What it does |
|---|---|
| `permissions: contents: read`, `persist-credentials: false` | the job reads the code and nothing more, and the token does not stay in `.git/config` for the later steps |
| `uv sync --locked` | installs the locked dev tools; fails when `uv.lock` does not match `pyproject.toml` |
| `pre-commit run --all-files` | runs every hook of section 2 on the whole tree: hygiene, lint, format, types, import contracts |
| `--show-diff-on-failure` | when a hook would change a file, the log shows the change, so the author sees what to fix |

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

What this example does not claim: the action versions are the latest in September 2026.
`actions/checkout@v7` follows a major tag that moves; `setup-uv` publishes no major tag, so the
example pins a release. A team that pins actions by commit hash trades updates for a fixed tree.
