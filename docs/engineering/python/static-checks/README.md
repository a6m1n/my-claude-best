# Static check practices

How a Python repository runs the checks that read the code without running it: the formatter, the
linter, one type checker in strict mode and the import contracts. Each is one command from one
pinned version; CI runs it on every pull request and blocks the merge, and a light pre-commit hook
runs the same command earlier.

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The point to adapt](#the-point-to-adapt)

A plain arrow reads "runs".

```mermaid
flowchart LR
  L["uv.lock<br/>one version of each tool"] -- "same version" --> H["pre-commit hook<br/>on the developer's machine"]
  L -- "same version" --> C["CI job<br/>required for main"]
  H --> T["ruff check · ruff format · mypy · lint-imports"]
  C --> T
```

## What is here

- [static-checks.md](static-checks.md) — the rules: which checks run, one pinned version per tool,
  the Python version the checks judge the code against, what a hook may hold, CI as the gate, and
  how a suppression is written. Read it before you add or
  change a static check, a hook, the CI job that runs them, or a comment that silences one.
- [setup-example.md](setup-example.md) — `pyproject.toml`, `.pre-commit-config.yaml` and a CI
  workflow for a service, with each part explained. Read it when you set the checks up in a
  repository or change one of those three files.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/python/static-checks/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you add or change a static check, a
   hook, the CI job that runs them, or a comment that silences one, read
   `docs/engineering/python/static-checks/static-checks.md`." Without it an agent never opens the file.
3. Copy the three files from `setup-example.md`, keep in `extend-select` only the rules of the
   practices you took, and make the CI job a required status check for `main`, directly or through
   the gate job of [ci-cd/pipeline.md](../../any-language/ci-cd/pipeline.md) section 6. When you took
   python/language but not readability or file-structure, still keep the settings whose comment
   names readability or file-structure: [python.md](../language/python.md) section 6 sends PEP 8's
   rules to those two practices, and these settings are their checks. Drop them only if you replaced
   python.md's links to those practices with your own rules
   ([python/language README](../language/README.md), step 4). A setting whose comment sits on the
   line above it, such as `"tests/**" = ["D205"]`, counts, and its table header stays with it. Keep
   the `lint-imports` hook and its dependency only if you took file-structure, and copy its
   contracts from [layout-example.md](../../any-language/file-structure/layout-example.md) section 3
   before the first commit: without contracts, import-linter fails on every run.
4. In a repository that already has code, turn the type checker and each new rule on the way
   [refactoring.md](../../any-language/refactoring/refactoring.md) sections 4 and 10 say, not by a rewrite.
   For ruff, `ruff check --fix` and `ruff format` make the sweep commit;
   `ruff check --add-noqa=' # legacy'` then writes, on every line still failing, the mark
   refactoring.md section 4 asks for, such as `# noqa: N802  # legacy`, which its counting command
   finds. No safe fix exists for the `N` rules or `D401` (`N804` and `N805` have only an unsafe
   one), so their old hits are marked, not swept.
5. Once `requires-python` names one minor, as [ci-cd/pipeline.md](../../any-language/ci-cd/pipeline.md)
   section 9 says, delete any mypy `python_version`, pyright `pythonVersion` and ruff
   `target-version` the project already has: each is a second copy of the Python version that a
   minor move can miss ([static-checks.md](static-checks.md) section 3).
6. Re-check the lines that name a moving target: the tool versions and the checker status in
   section 2 of `static-checks.md` (dated September 2026), ruff's default rule set and which rules
   it counts as formatting, pedantic or preview (changed in 0.16.0 and 0.17.0;
   `ruff check --isolated --show-settings <file>` lists the default set on the pinned version, and
   `ruff rule <code>` prints "This rule is in preview" when it is), the pre-commit `unsupported`
   rename, and the action versions in `setup-example.md`.

## The point to adapt

Which type checker is the gate is yours; [static-checks.md](static-checks.md) section 2 lists the
choices. The shape does not change: one checker, strict, its command in a hook and in a required
CI job, and one pinned version shared by both.
