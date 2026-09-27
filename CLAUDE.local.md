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
repo is what gets fixed, the way `docs/engineering/refactoring/refactoring.md` says.

- Before you change anything in an area that has a folder under `docs/engineering/`, read that
  folder's rules file first and work by it. The check: the closing summary names the practice
  file you read.
- Before any git operation (branch, commit, merge, push, pull request, conflict), read
  `docs/engineering/git/git.md`. Write the commit message by
  `docs/engineering/git/commit-example.md`, the pull request by
  `docs/engineering/git/pr-example.md`, a project README by
  `docs/engineering/git/readme-example.md`. The check: the branch name, the commit title and
  the pull request sections match the forms `git.md` gives for branches, commits and pull
  requests.
- Before you write or change Python — a module, a type, a check on data coming in — read
  `docs/engineering/python/python.md`, and
  `docs/engineering/python/explicit-constraints-example.md` when you place a constraint. The
  check: every constraint the change introduces is stated on the type or signature that carries
  it, and what enforces it is a runtime mechanism or a checker the CI runs and fails on.
- Before a change edits code that already exists (a feature, a fix, a move to a practice, a
  restructure), or turns on a new rule, read `docs/engineering/refactoring/refactoring.md`, and
  `docs/engineering/refactoring/adoption-example.md` when a practice change has to reach old
  code. The check: every hunk in the diff is new code or code the change had to edit, and no
  `refactor` commit changes an expected value in a test.
- Before you create a file, a folder or a module in an application, or move code from one folder
  to another, read `docs/engineering/file-structure/file-structure.md`, and
  `docs/engineering/file-structure/layout-example.md` when you lay out a repository or add a
  module, `docs/engineering/file-structure/package-map-example.md` when you write a package map.
  The check: every file the diff adds sits where the practice's role table puts its kind, its name
  says what it holds (no `utils.py`), and every import in it is absolute.
- Before you add a log call, set up logging for a process, or wire logging into a service or an
  agent, read `docs/engineering/logging/logging.md`, and
  `docs/engineering/logging/setup-example.md` when you set up logging for a process,
  `docs/engineering/logging/agent-example.md` when an agent's runs should appear in the log. The
  check: the ruff rules in `logging.md` section 11 pass on the change, and no line it adds logs a
  prompt, an answer or a secret.
- Before you create or edit any file under `docs/engineering/`, read `docs/engineering/CLAUDE.md`
  first. The check: the closing summary names it.
- When you write or change an example under `docs/engineering/` (as `docs/engineering/CLAUDE.md`
  defines one), read the rules on examples in `docs/engineering/CLAUDE.md` and work by them. The
  check: the closing summary has the lines that file's GOOD-example bullet asks for.
- Every practice under `docs/engineering/` is a folder named by the topic, never a bare file.
  Before you stage a change that adds or removes one, run `ls -d docs/engineering/*/` and
  `ls docs/engineering/*.md`: every folder the first prints has a bullet that names it in this
  section, in the shape above (the moment, the file, the check), and the second prints nothing
  but `CLAUDE.md`.
```
