# Example: a project CLAUDE.md that adopts these practices

Claude Code loads `CLAUDE.local.md` alongside `CLAUDE.md`, and by convention it is a personal,
git-ignored file (`docs/claude-code/claude-md.md` § "Where the files live"). This library
commits one on purpose. It is not this repository's rules, which live in a local `CLAUDE.md`
that is not committed; it is an example of the practices section of a project `CLAUDE.md`, for
a repository that copied `docs/engineering/` in. Copy the block, keep the shape, and add one
bullet per practice folder you took.

```markdown
## Engineering practices — read before you act

`docs/engineering/` holds the practices: how a kind of work should be done, in any repository.
A practice describes the practice, never this repo. Where the repo and a practice disagree, the
repo is what gets fixed, the way `docs/engineering/any-language/refactoring/refactoring.md` says.

- Before you change anything in an area that has a practice folder under `docs/engineering/`,
  read that practice's rules file first and work by it. The check: the closing summary names the
  practice file you read.
- Before any git operation (branch, commit, merge, push, pull request, conflict), read
  `docs/engineering/any-language/git/git.md`. Write the commit message by
  `docs/engineering/any-language/git/commit-example.md`, the pull request by
  `docs/engineering/any-language/git/pr-example.md`, a project README by
  `docs/engineering/any-language/git/readme-example.md`. The check: the branch name, the commit title and
  the pull request sections match the forms `git.md` gives for branches, commits and pull
  requests.
- Before you write or change Python — a module, a type, a check on data coming in — read
  `docs/engineering/python/language/python.md`, and
  `docs/engineering/python/language/explicit-constraints-example.md` when you place a constraint,
  `docs/engineering/python/language/settings-example.md` when you add or change the application's
  settings. The check: every constraint the change introduces is stated on the type or signature
  that carries it, what enforces it is a runtime mechanism or a checker the CI runs and fails on,
  no parameter or field the change adds that carries a value of a closed set is a bare `str`
  (`python.md` section 3), and nothing the change adds reads the environment outside the
  settings class (`python.md` section 5).
- Before a change edits code that already exists (a feature, a fix, a move to a practice, a
  restructure), or turns on a new rule, read `docs/engineering/any-language/refactoring/refactoring.md`, and
  `docs/engineering/any-language/refactoring/adoption-example.md` when a practice change has to reach old
  code. The check: every hunk in the diff is new code or code the change had to edit, and no
  `refactor` commit changes an expected value in a test.
- Before you create a file, a folder or a module in an application, or move code from one folder
  to another, read `docs/engineering/any-language/file-structure/file-structure.md`, and
  `docs/engineering/any-language/file-structure/layout-example.md` when you lay out a repository or add a
  module, `docs/engineering/any-language/file-structure/package-map-example.md` when you write a package map.
  The check: every file the diff adds sits where the practice's role table puts its kind, its name
  says what it holds (no `utils.py`), and every import in it is absolute.
- Before you add a log call, set up logging for a process, or wire logging into a service or an
  agent, read `docs/engineering/python/logging/logging.md`, and
  `docs/engineering/python/logging/setup-example.md` when you set up logging for a process,
  `docs/engineering/python/logging/agent-example.md` when an agent's runs should appear in the log. The
  check: the ruff rules in `logging.md` section 11 pass on the change, and no line it adds logs a
  prompt, an answer or a secret.
- Before you write or change a function or a class, or review one, read
  `docs/engineering/any-language/readability/readability.md`, and
  `docs/engineering/any-language/readability/module-example.md` when you write a new module's use case, its
  rule and its test. The check: no function or class the change writes or edits shows two or more
  red flags from `readability.md` section 9's table, and the closing summary names each single red
  flag left in place and why.
- Before you add or change a static check (the formatter, the linter, the type checker or an import
  contract), a pre-commit hook, the CI job that runs them, or a comment that silences one, read
  `docs/engineering/python/static-checks/static-checks.md`, and
  `docs/engineering/python/static-checks/setup-example.md` when you set the checks up in a repository.
  The check: every check the change adds is one command, run from the one pinned version of its
  tool in the hook file and in the required CI job, and every suppression it adds names its rule
  and says why.
- Before you write or change a prompt, a tool definition the model reads, or a setting that
  changes what the model receives (the model, its reasoning effort, the cache switch), read
  `docs/engineering/any-language/prompt-engineering/prompt-engineering.md`, and
  `docs/engineering/any-language/prompt-engineering/prompt-example.md` when you add a call to a model or change
  the model a call site uses. The check: every model call the change adds or edits takes its model
  and its reasoning effort from `<purpose>_llm_model` and `<purpose>_llm_reasoning_effort`
  constants (the effort where the model has one) and gets its answer through a response schema.
- Before you write or change a test, a fixture, a `conftest.py` or the pytest configuration, read
  `docs/engineering/python/testing/README.md` and the file it routes to for that work, and
  `docs/engineering/python/testing/suite-example.md` when you set up a suite or add a module's first
  tests. The check: every test file the change adds sits at the path `layout.md` section 3 gives
  it and holds one `Test<Unit>` class, every fixture it adds states `scope=`, and
  `grep -rn autouse --include='*.py' tests/` prints nothing.
- Before you change a prompt, a tool definition, the model or its settings, the retrieval or an
  agent's graph, or add a check on what a model answers, read `docs/engineering/python/evals/README.md`
  and the file it routes to for that work, and `docs/engineering/python/evals/case-set-example.md` when
  you write a module's first eval, `docs/engineering/python/evals/judge-example.md` when you write a judge,
  `docs/engineering/python/evals/agent-eval-example.md` when you test an agent. The check: the pull
  request's Verification holds the eval's result next to its baseline, every rate the eval reports
  is divided by the cases it asked for, and every judge that gates has its TPR and TNR on held-back
  labels.
- Before you create or edit any file under `docs/engineering/`, read `docs/engineering/CLAUDE.md`
  first. The check: the closing summary names it.
- When you write or change an example under `docs/engineering/` (as `docs/engineering/CLAUDE.md`
  defines one), read the rules on examples in `docs/engineering/CLAUDE.md` and work by them. The
  check: the closing summary has the lines that file's GOOD-example bullet asks for.
- Every practice under `docs/engineering/` is a folder named by the topic, never a bare file,
  inside a group folder: `any-language/`, or a language's own folder such as `python/`
  (`docs/engineering/CLAUDE.md` says which). Before you stage a change that adds or removes one,
  run `ls -d docs/engineering/*/*/` and `find docs/engineering -maxdepth 2 -name '*.md'`: every
  folder the first prints has a bullet that names it in this section, in the shape above (the
  moment, the file, the check), and the second prints nothing but `docs/engineering/CLAUDE.md`.
```
