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
- Before you add a log call, set up logging for a process, wire logging or tracing into a service
  or an agent, or add an HTTP route, a CLI command or a worker's job that calls a model, read
  `docs/engineering/python/logging/logging.md`, and
  `docs/engineering/python/logging/setup-example.md` when you set up logging for a process,
  `docs/engineering/python/logging/agent-example.md` when an agent's runs should appear in the log,
  `docs/engineering/python/logging/trace-example.md` when you add a route that calls a model, or
  one request makes more than one model call. The check: the ruff rules in `logging.md` section 11
  pass on the change, no line it adds logs a prompt, an answer or a secret, and every HTTP route
  the change adds that calls a model opens the request's root span (`logging.md` section 8).
- Before you write or change a function or a class, or review one, read
  `docs/engineering/any-language/readability/readability.md`, and
  `docs/engineering/any-language/readability/module-example.md` when you write a new module's use case, its
  rule and its test. The check: no function or class the change writes or edits shows two or more
  red flags from `readability.md` section 9's table, and the closing summary names each single red
  flag left in place and why.
- Before you add or change a static check (the formatter, the linter, the type checker or an import
  contract), a pre-commit hook, the CI job that runs them, or a comment that silences one, in a
  Python repository, read
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
- Before you write or change a test, a fixture, a `conftest.py` or the pytest configuration in a
  Python repository, read
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
- Before you create a React application, or add a module, a route, a query, a mutation or a
  dependency to one, read `docs/engineering/react/architecture/architecture.md`, and
  `docs/engineering/react/architecture/layout-example.md` when you lay out an application or add a
  module, `docs/engineering/react/architecture/libraries.md` when you pick a library or a tool. The
  check: every import the change adds is absolute and names the file that holds the name, with no
  barrel file (`architecture.md` section 5), no module imports another module or the router, and no
  component state holds a copy of server data (`architecture.md` section 7).
- Before you write or change a React component or a hook, or review one, read
  `docs/engineering/react/components/components.md`, and
  `docs/engineering/react/components/component-example.md` when you write a module's first
  component. The check: the hooks and compiler lint rules pass on the change (`components.md`
  section 2), and every `useEffect`, `useMemo`, `useCallback`, `memo` and `"use no memo"` the change
  adds carries a comment that names the outside system or the escape hatch it is for
  (`components.md` sections 5 and 7).
- Before you design or restyle a screen of a React application, add a control, a form or a route to
  one, or ask an agent to build a screen, read `docs/engineering/react/design/README.md` and the
  file it routes to for that work, and `docs/engineering/react/design/design-brief-example.md` when
  you write the brief for a screen. The check: every colour, radius and space the change adds is a
  token role, a step of the scale or one of the two exceptions (`visual-design.md` sections 3 and 6),
  the closing summary says which steps of the manual accessibility pass were run (`accessibility.md`
  section 11), and someone other than the author of the screen answered its review checklist
  (`designing-with-claude-code.md` section 6).
- Before you render a value from outside as HTML or as a URL in a React application, spread an
  object from outside as props, keep or send a credential in one, or add an environment variable, a
  dependency, a third-party script, a response header or a CI step to one, or change the dev
  server's settings, read `docs/engineering/react/security/security.md`, and
  `docs/engineering/react/security/security-example.md` when you set these up in an application. The
  check: `grep -rln dangerouslySetInnerHTML src/` prints one file, the one that sanitises
  (`security.md` section 4), `grep -rnE 'localStorage|sessionStorage' src/` prints no line that
  holds a credential (`security.md` section 6), and no secret sits in a variable the bundler exposes
  (`security.md` section 9).
- Before you add an image, a font, a route, a data request or a dependency to the first load of a
  screen in a React application, or act on a report that such an application is slow, read
  `docs/engineering/react/performance/performance.md`, and
  `docs/engineering/react/performance/performance-example.md` when you set up field metrics, code
  splitting or caching. The check: a change that claims a gain names the metric, its percentile, its
  source and its date in the pull request's Verification (`performance.md` section 4), and every
  image the change adds has `width` and `height` (`performance.md` section 5).
- Before you open a project, write or change its charter, plan, schedule, work breakdown structure,
  risk register, stakeholder register or RACI matrix, record a decision that is hard to undo, write
  a status update, write, split or move a Jira work item, comment on one, set up a board, plan a
  release or its rollback, agree an SLA, or plan or run a team meeting, read
  `docs/engineering/any-language/project-management/README.md` and the file it routes to for that
  work, and `docs/engineering/any-language/project-management/project-example.md` when you write a
  project's first charter, plan, stakeholder register or risk register,
  `docs/engineering/any-language/project-management/work-item-example.md` when you write the first
  work item of a type. The check: every risk the change adds has one owner and one of the five
  threat responses (`risks.md` section 5), every work item it adds has the type `work-item-types.md`
  section 1 gives its work, can be done in three working days and gets its own branch and pull
  request (`tickets.md` sections 3 and 4), every move to Blocked or Canceled it makes carries a
  comment that names the blocker or the reason (`workflow.md` sections 4 and 5), every RACI row it
  adds has exactly one Accountable (`roles-and-decisions.md` section 3), every status update it
  writes sets its marker from the forecast against the plan's tolerance (`communication.md` section
  3), every meeting it plans names the decision it makes (`meetings.md` section 1), and every
  release it plans has one go or no-go decider (`release.md` section 3) and a rollback plan with a
  trigger, one decider and a time that fits the SLA (`rollback-plan.md` section 2).
- Before you create or edit any file under `docs/engineering/`, read `docs/engineering/CLAUDE.md`
  first. The check: the closing summary names it.
- When you write or change an example under `docs/engineering/` (as `docs/engineering/CLAUDE.md`
  defines one), read the rules on examples in `docs/engineering/CLAUDE.md` and work by them. When
  you brief a subagent to write or change one, quote that file's two bullets on GOOD examples and
  its bullet on a line's reason in the brief, since a subagent may not load that file, and ask for
  the `Practices:` line in the hand-back. The check: when you write the commit message, its
  trailer block carries the `Practices:` line that file's GOOD-example bullets ask for, in the
  form they give, `Practices: none govern these examples` included.
- Every practice under `docs/engineering/` is a folder named by the topic, never a bare file,
  inside a group folder: `any-language/`, or a language's own folder such as `python/`
  (`docs/engineering/CLAUDE.md` says which). Before you stage a change that adds or removes one,
  run `ls -d docs/engineering/*/*/` and `find docs/engineering -maxdepth 2 -name '*.md'`: every
  folder the first prints has a bullet that names it in this section, in the shape above (the
  moment, the file, the check), and the second prints nothing but `docs/engineering/CLAUDE.md`.
```
