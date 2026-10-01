# Static check rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. The checks: one tool per job](#2-the-checks-one-tool-per-job)
- [3. One pinned version per tool](#3-one-pinned-version-per-tool)
- [4. Hooks before a commit: light, fast, cheap](#4-hooks-before-a-commit-light-fast-cheap)
- [5. CI is the gate](#5-ci-is-the-gate)
- [6. A suppression names the rule and the reason](#6-a-suppression-names-the-rule-and-the-reason)
- [7. Where it stops holding](#7-where-it-stops-holding)
- [8. Sources](#8-sources)

## 1. Purpose and the one rule

This file is for everyone who sets up or changes the checks a Python repository runs without
running the code: the formatter, the linter, the type checker and the import contracts. People and
AI agents alike read it before they add or change a check, a hook, the CI job that runs them, or a
comment that silences one.

It says how the checks run. Which rules each check turns on belongs to the practice the rule serves:
the import contracts and the relative-import ban to
[file-structure.md](../../any-language/file-structure/file-structure.md) sections 7 and 11, the logging rules to
[logging.md](../logging/logging.md) section 11, the readability rules to
[readability.md](../../any-language/readability/readability.md) sections 3 and 4, and what typed code looks like to
[python.md](../language/python.md) section 3.

The one rule: **CI is the gate, and a hook is an early copy of it.** Every check is one command,
run from one pinned version of its tool. CI runs it on every pull request and blocks the merge when
it fails. A pre-commit hook runs the same command on the developer's machine, so most failures show
up before a push.

Why it matters:

- A rule that is only written down is often ignored: [logging.md](../logging/logging.md) section 11
  cites a study of agents and the logging rules they were given. A check that fails the build does
  not depend on being read.
- A type checker finds real bugs ([python.md](../language/python.md) section 3 has the figure).
- A hook that disagrees with CI teaches people to skip hooks. One command and one version remove
  the disagreement.

## 2. The checks: one tool per job

| Job | Tool | Command (hook and CI) | Rules come from |
|---|---|---|---|
| Lint | ruff | `ruff check --fix --force-exclude` | each practice's own list (section 1), plus section 6 of this file |
| Format | ruff format | `ruff format --force-exclude` | the formatter's defaults |
| Types | one checker in strict mode | `mypy` (or `pyright`) | [python.md](../language/python.md) section 3 |
| Import contracts | import-linter | `lint-imports` | [file-structure.md](../../any-language/file-structure/file-structure.md) section 11 |

CI runs these through the hook file (section 5), so each command is the same in both places.

- **One checker per job.** Two type checkers on the same code disagree, and each wants its own
  ignore comments. Pick one as the gate. mypy is the default here: it has the widest plugin support,
  Django's included. pyright in strict mode is an equal choice. pyrefly reached 1.0 in May 2026 and
  may be the checker of a new project. ty was still beta in September 2026 and is not a gate yet.
- **Turn rules on by name.** A linter's default set is small: ruff's covers only a few rule groups.
  A rule a practice relies on is selected by its code in `pyproject.toml`, next to a comment that
  names the practice section it serves.

## 3. One pinned version per tool

- **Every tool is a dev dependency of the project**, locked in `uv.lock` with the rest. The hook,
  CI and the editor all run the locked copy through `uv run --locked`, so they check with the same
  version and the same rules.
- **Never pin a tool a second time in the hook file.** A hook repository pinned by `rev:` is a second
  copy of ruff or mypy, and the two drift: the hook passes, CI fails. It happens often enough that
  people wrote tools to sync the two pins. With one pin there is nothing to sync.
- **Never run the type checker through a mirror hook** such as mirrors-mypy. Each such hook runs in
  its own virtual environment without the project's dependencies, so it starts with
  `--ignore-missing-imports`, treats every missing import as `Any`, and passes code the real
  checker fails. One project saw the hook pass while the project's own mypy reported 961 errors.
- **`--locked`, not `--frozen`.** `--locked` fails when `uv.lock` is out of date with
  `pyproject.toml`; `--frozen` uses the old lock without a word and leaves new dependencies out.
- A hygiene hook the project runs nowhere else, such as the checks in `pre-commit-hooks`, is pinned
  by `rev:` once, in the hook file. That is its one pin.

## 4. Hooks before a commit: light, fast, cheap

When you set up the hooks, use the `.pre-commit-config.yaml` format. pre-commit (4.4 or newer) and
prek both read it, and prek runs it faster; CPython, FastAPI, Airflow and ruff switched to prek.

- **The commit stage holds only checks that finish in a few seconds on a warm cache** (this
  practice's line: under five seconds for the whole run): file hygiene (trailing whitespace, a
  final newline, YAML and TOML syntax, large files, a private key, a merge conflict marker), the
  linter with its safe fixes, then the formatter, and the type checker and the import contracts
  while they stay that fast. To measure, run `uv run pre-commit run --all-files --verbose` twice:
  the second run prints each hook's duration on a warm cache. Measure again when you add a hook or
  when commits start to feel slow. A hook people wait for is a hook people skip with `--no-verify`.
- **Run ruff, the type checker and the import contracts as local hooks** (`repo: local`,
  `language: unsupported`, `entry: uv run --locked …`). pre-commit 4.4 renamed `system` to
  `unsupported` and plans to warn about the old name; prek reads both.
- **The type checker checks the whole project** (`pass_filenames: false`, `always_run: true`).
  Checked file by file, it misses the callers of the function a change broke, and a commit that
  touches only `pyproject.toml` or `uv.lock` would skip it. When the timed run shows the type
  checker or the import contracts too slow for the commit stage, move that hook to the push: give
  it `stages: [pre-push]`, put `default_install_hook_types: [pre-commit, pre-push]` and
  `default_stages: [pre-commit]` at the top of the hook file (without the second, every other hook
  runs at push too), and run `uv run pre-commit install` again on each clone. Add a CI step for
  that stage too, `uv run --locked pre-commit run <hook-id> --all-files --hook-stage pre-push`: CI
  runs only the commit-stage hooks unless told otherwise.
- **A hook never replaces CI.** Anyone can skip a hook, and a new clone has none installed until
  someone runs `pre-commit install`.

## 5. CI is the gate

- **One CI job runs every check on every pull request**, from a clean checkout: `uv sync --locked`,
  then the hook file on all files. `pre-commit run --all-files --show-diff-on-failure` fails when a
  hook finds a problem or would change a file.
- **The job is a required status check** for `main` in the branch ruleset, so a failing check blocks
  the merge ([git.md](../../any-language/git/git.md) section 5 owns how a pull request lands).
- **A check is on or off, never "warning only".** A warning nobody has to fix is noise after a
  week. A rule the team does not want to fix everywhere yet is turned on the way
  [refactoring.md](../../any-language/refactoring/refactoring.md) sections 4 and 10 say.

## 6. A suppression names the rule and the reason

When a check is wrong for one line, silence that rule on that line and say why. Here the library
ships types, but its stub for `search` lacks the `expand` argument its API accepts:

```python
rows = client.search(term, expand=True)  # type: ignore[call-arg]  # stub lacks expand
```

- **Name the rule.** `# type: ignore[code]`, `# noqa: CODE`, `# pyright: ignore[rule]`. A bare
  suppression silences every rule on the line, including the ones nobody meant to silence.
- **Give the reason** on the same line, after a second `#`
  ([readability.md](../../any-language/readability/readability.md) section 4): mypy rejects other text inside its
  own comment. A mark left on old code until a change touches it, as
  [refactoring.md](../../any-language/refactoring/refactoring.md) section 4 describes, gives `legacy` as its
  reason: `# type: ignore[arg-type]  # legacy`.
- **The tools enforce the name and catch a stale suppression; the reason is review.** ruff's
  `PGH003` and `PGH004` fail on a bare `# type: ignore` or `# noqa`, and mypy's
  `ignore-without-code` does the same for its own comments. Upstream pyright cannot require a rule
  name; basedpyright's `reportIgnoreCommentWithoutRule` can. ruff's `RUF100` and mypy's
  `warn_unused_ignores` (part of `--strict`) fail on a suppression that no longer suppresses
  anything; with pyright, turn on `reportUnnecessaryTypeIgnoreComment`, which is off in every mode.
- **Silence a module, not the world.** A setting that turns a rule off for the whole repository
  hides every future case too. Scope it to the one module in `[[tool.mypy.overrides]]` or ruff's
  `per-file-ignores`.

Check: before you merge,
`grep -rnE "# (type: ignore|pyright: ignore|noqa)(\[[^]]*\]|: [A-Z0-9, ]+)?$" src/ tests/` prints
nothing: no suppression ends without a reason.

## 7. Where it stops holding

- **A script or a notebook** run once needs the formatter and nothing else.
- **A library** follows this practice and also checks the API its users see, which this practice
  does not cover.
- **Django** stays on mypy with django-stubs. Other checkers do not run mypy plugins, so on a Django
  project they report errors that are not real. pyrefly 1.0 claims Django support; this practice has
  not tested that.
- **A repository without uv** keeps the same shape with its own lock: the tools are dev dependencies
  in the lock file, and the hooks call the locked copy.

## 8. Sources

mypy documentation (2.3): "The mypy command line" (`--strict`), "Error codes for optional checks"
(`ignore-without-code`, `exhaustive-match`), "Running mypy and managing imports". pyright
`configuration.md` (1.1.414): `typeCheckingMode`, `reportUnnecessaryTypeIgnoreComment`. ruff rule
reference (0.16): `PGH003`, `PGH004`, `RUF100`. The ruff-pre-commit README (hook order).
basedpyright documentation, new diagnostic rules (`reportIgnoreCommentWithoutRule`). pre-commit
documentation and pull request #3577 (the `unsupported` rename, 4.4.0); the pre-commit-hooks README
(`check-added-large-files`, `check-merge-conflict`); the mirrors-mypy README; prek documentation
(local hooks, stages); uv documentation on `--locked` and `--frozen`. The setup-uv release tags
(September 2026). CPython issue #143148 (moving CI to prek); Akkudoktor-EOS issue #1276 (a mirror
hook passing against 961 real errors). pyrefly 1.0 release notes (May 2026); the ty README (beta);
the typing conformance results, python/typing repository. Tim Hopper, pydevtools.com, on version
drift between pre-commit and uv (2025) and on mypy strict mode (2026).
