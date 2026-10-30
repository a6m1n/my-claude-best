# Example: an agent's delegation for dependency updates

A worked example for [agents.md](agents.md) sections 2 to 5. The repository is the billing service
of Acme Corp's billing application, the same invented application as
[adr-example.md](adr-example.md): a Python service whose dependencies live in `pyproject.toml` and
`uv.lock`. Each Monday a scheduled job starts a coding agent, Claude Code, in a hardened container
to keep those dependencies current. The file below is the agent's delegation for that one decision
area: what it decides on its own, its limits, what it never does, when it stops and reports, and
which tool enforces each limit. After it come the managed settings file and the start command it
names, then the first exception note the agent sent under it.
Every name, date and number is invented, except the Claude Code version and the behaviour of its
settings, which were checked against its documentation on 2026-10-30.

The file sits at `docs/delegations/dependency-updates.md`. The job's start command passes it to the
agent, and the repository's `CLAUDE.md` links it. A line a reader might change or delete carries its
reason in an HTML comment.

## The delegation

````markdown
# Delegation: dependency updates in the billing service

<!-- In the repository, so every change to it is a reviewed diff, and passed in the start
     command, so it loads in every run; a file CLAUDE.md only links loads when the agent
     decides to open it (agents.md section 2). -->

- Decision area: which versions of its dependencies the billing service runs.
- Decider for the area: Jane Doe, tech lead of the billing team. Backup: John Smith.
  <!-- The decider roles-and-decisions.md section 5 names, and a backup, so a report never
       waits for one person's holiday (agents.md section 2). -->
- Agent: Claude Code 2.1.312, started each Monday at 06:00 by the scheduled job `deps-weekly`.
  <!-- The settings in `docker/managed-settings.json` and the start command were checked
       against this version's documentation on 2026-10-30.
       Check them again when the version changes (agents.md section 3). -->
- Where it runs: a hardened container for a trusted repository with no approvals, with no host
  credentials and with egress only through the allowlisting proxy (agent-containers.md
  section 3).
- Valid from: 2026-11-02. Last change: pull request #212, approved by Jane Doe on 2026-10-30.
- How this file changes: only through a pull request Jane Doe approves, and so do the files that
  enforce it (the table "What enforces each limit" names them). A request to "always allow"
  something new is such a change, never an answer given during a run.
  <!-- An "always allow" widens the delegation for good; it gets the same review as any other
       change to this file (agents.md section 2). -->

## Intent

Keep the billing service on supported, patched versions of its libraries, so that a security fix
can ship within a day and no upgrade grows into a project. What the billing team, Globex and the
mobile app see must not change.
<!-- The intent settles the choices the limits below do not name (agents.md section 2). -->

## What the agent decides on its own

- Which patch and minor updates to take, and how to group them into one pull request.
- How to fix the code in `src/` and `tests/` that an update breaks, when the fix keeps the
  behaviour the same.

## Limits (the tolerance)

- Patch and minor versions only. No major version.
- No new direct dependency, and none removed.
- Changes only in `pyproject.toml`, `uv.lock`, and the code in `src/` and `tests/` that calls
  the packages it updates.
- A test may change only where the updated package's API changed. Never skip, delete or loosen
  a test to make the suite pass.
- At most 10 packages and 300 changed lines outside `uv.lock` in one pull request.
  <!-- A small diff gets a real review; review quality falls as a diff grows (git.md
       section 4). -->
- Two attempts at a failing test, then a report.

## Never

- Push, merge, or open a pull request. The job does that from the agent's work.
- Change `.github/`, `.claude/`, the container files, `.python-version`, `requires-python`, or
  this file.
- Read or ask for a secret.

## When the agent stops and reports

It stops work on the item and reports when:

1. A security fix needs a major version.
2. Finishing the work would break a limit above.
3. A test still fails after its second attempt.
4. The intent does not settle a choice, such as two fixes for a call site that change the
   behaviour in different ways.

The only actions in its reach that the platform cannot undo are its calls out: to the model API,
through the gateway, and to the package index, for `uv lock` (agents.md section 2 counts a call to
another service as one). They are accepted, not a reason to stop: no secret sits in the container,
so nothing they carry can be a credential, and they change nothing on either service. They are
still ways out; the proxy narrows the ways out to these hosts, it does not close them
(agent-containers.md section 5). The agent holds no credential and cannot push.
<!-- agents.md section 4 makes such an action a reason to stop; the calls the run needs are
     named here and accepted. A delegation for an area where another one is in reach lists it as
     a fifth condition. -->

The report is an exception note in the form of communication.md section 5: the forecast, the
cause, two or three options with what each costs, and a recommendation. It is the agent's final
answer of the run. The job posts it in #team-backend for Jane Doe and adds the facts from its own
log: the test results, the scanner's findings, and any count an option rests on, from a search the
job runs in its own clone.
<!-- Facts about state come from the tools, not from the agent's account of them (agents.md
     section 4). -->

## Done, and who approves

- No prompt during a run. Anything the rules in `docker/managed-settings.json` do not allow is
  denied, not asked.
  <!-- Routine updates run without a prompt; the person's attention goes to the merge, where
       every change can still be undone (agents.md section 5). -->
- A pull request is done when the required check `ci-ok` passes on it, not when the agent says
  so (agents.md section 6; pipeline.md section 6).
- Jane Doe or John Smith reviews and merges. The job opens the pull request with its
  `GITHUB_TOKEN` (pipeline-security.md section 11), so the pull request's workflow runs wait "in
  an approval-required state" until a user with write access selects "Approve workflows to run"
  [13]. The reviewer reads `pyproject.toml`, `uv.lock` and any `conftest.py` first, because
  approving the runs starts that code in CI, and the dependency files run everywhere once merged
  (agent-containers.md section 7). Only then do they approve the runs and read `ci-ok`. Jane Doe
  and John Smith are there to check the limits no
  tool enforces: no new or removed direct dependency, `requires-python` unchanged, no test skipped
  or loosened, changes in `src/` and `tests/` only at call sites of the updated packages, a test
  changed only where the package's API changed, the size limit, and code fixes that keep the
  behaviour.
  <!-- The reviewer knows what to look for, instead of approving a diff that "looks fine"
       (agents.md section 5). -->

## How a run works

The workflow `deps-weekly` is built as pipeline-security.md section 10 says for an agent's job: its
token, the split between the agent's job and the job that writes, and the caps on turns, time and
parallel runs. The agent's work comes back as agent-containers.md section 7 says. What this
delegation adds:

1. The start command, in `.github/workflows/deps-weekly.yml`, runs at the root of a fresh clone
   at `<start-sha>`, the commit the run starts from. It passes this file with
   `--append-system-prompt-file`, sets the mode `dontAsk` and the turn cap `--max-turns <n>`,
   takes the model and its effort from the workflow's named constants, and asks for
   `--output-format stream-json --verbose`.
   Before it, the job checks as the agent's user that the managed settings file is readable
   (`test -r /etc/claude-code/managed-settings.json`). It stops the run and pushes nothing if that
   check fails, or on any line Claude Code writes to stderr at startup, before its first
   stream-json event.
   <!-- The delegation file goes in through the command, so it loads in every run. The mode comes
        from the command as well as the settings file. <n> is the turn cap pipeline-security.md
        section 10 asks for. stream-json gives the job the tool's own record of every denied call
        (agents.md section 4); in a -p run it needs --verbose, or the tool exits before the agent
        starts. A managed file the agent's user cannot read is skipped, and a rule Claude Code
        cannot parse is dropped; a -p run says so only on stderr (agents.md section 3). -->
2. The check on the fetched branch, in the job's own clone, before anything is pushed: if the
   branch does not descend from `<start-sha>`, if
   `git diff --no-renames --name-only <start-sha> FETCH_HEAD` lists a path outside
   `pyproject.toml`, `uv.lock`, `src/` and `tests/`, or if a package's major version in `uv.lock`
   differs from `main`'s, the job pushes nothing and posts the list in #team-backend. Otherwise it
   pushes a new branch, such as `chore/dependency-updates-week-45`, and opens the pull request in
   the form of git.md section 4.
   <!-- The checks read the fetched branch in the job's own clone, so no git command outside the
        container reads the agent's clone or its config, and nothing the agent's code planted in
        that clone can hide a path (agent-containers.md section 7). --no-renames lists both paths
        of a moved file, so a protected file moved into tests/ still shows its old path. -->
   <!-- Departs from agent-containers.md section 7, which asks for a review of the diff before a
        push: here the pull request is where the team reviews. The cost: the agent's code and
        lock file run in the pull request's CI as soon as someone approves the runs, which GitHub
        allows before the diff is read. The bound: that CI
        holds only the repository secrets any run may use, and every deploy secret sits in an
        environment limited to `main` (pipeline-security.md sections 6 and 10). -->
3. When the job reports: after every run, it posts the agent's final answer in #team-backend, with
   the denials the tool recorded (`permission_denials` in the final result). If Claude Code exits
   non-zero, or the 60-minute timeout ends the run, the job pushes nothing and posts the result
   with its log. A post that fails fails the job. If the agent's previous pull request for this
   area is still open, the job starts no new run and posts a reminder on that pull request
   instead, since two open pull requests would conflict on `uv.lock`.

## What enforces each limit

| Limit | What enforces it | Where it lives | Can the agent change it? |
|---|---|---|---|
| Never push, merge or open a pull request | The agent holds no GitHub credential, and `github.com` is not on the proxy's allowlist | The container setup and the proxy configuration (agent-containers.md sections 4 and 5) | No |
| Nothing reaches `main` without a review | The `main` ruleset: a pull request, an approving review, the required check `ci-ok`, no force push | GitHub (git.md sections 5 and 6) | No |
| Never read a secret | No secret is mounted or set in the container; the gateway outside it adds the API key | The container setup (agent-containers.md section 4) | No |
| Never ask for a secret | No tool: a `-p` run takes no reply [9], so a request can only reach the final answer the job posts in #team-backend, where Jane Doe reads it | This file | Not enforced |
| Never change `.github/`, `.claude/`, the container files, `.python-version` or this file | The managed settings, `docker/managed-settings.json`; and the job's check on the fetched branch (step 2 of the run) | `/etc/claude-code/managed-settings.json`, owned by root in the image with mode 0644, so the agent's user can read it and not write it, while the agent runs as a non-root user (images.md section 6); the job's script | No |
| This file and the files that enforce it change only with Jane Doe's approval | `.github/CODEOWNERS` names her for `.github/CODEOWNERS` itself (so nobody can drop her from it without her review), `docs/delegations/`, `docker/managed-settings.json` (copied into the image as its managed settings), `.github/workflows/deps-weekly.yml` (the start command, the checks of step 2 and the timeout), the proxy configuration `proxy/` (its allowlist included), the container setup `Dockerfile` and `compose.yaml`, and `.claude/`; the ruleset requires a code owner's review | GitHub | No |
| Changes only in the dependency files, `src/` and `tests/` | The allow rules in `docker/managed-settings.json`; and the job's check on the fetched branch (step 2 of the run) | As above | No |
| Patch and minor versions only | The job's check on the fetched branch: each package's major version in `uv.lock` against `main` (step 2 of the run) | The job's script | No |
| The agent's code runs in the branch's CI with no deploy secret | Every deploy secret sits in an environment limited to `main`; the repository secrets hold only what any run may use | GitHub (pipeline-security.md sections 6 and 10) | No |
| No new or removed direct dependency; `requires-python` unchanged; tests not loosened; changes in `src/` and `tests/` only at call sites of the updated packages; a test changed only where the package's API changed; the size limit; behaviour kept | No tool: the reviewer checks them before the merge | This file | Not enforced |
| Two attempts, then a report; the four report conditions | No tool. The job's 60-minute timeout ends a run that never stops; it and `--max-turns <n>` cap only the cost, so a third attempt that ends inside them is not caught, and its result reaches the reviewer at the merge like any other change | The job's configuration | Not enforced |

With another agent tool, the left column stays and the middle column names that tool's own
mechanisms (agent-containers.md section 11).
````

The managed settings file, kept in the repository as `docker/managed-settings.json` and copied
into the image at `/etc/claude-code/managed-settings.json`. JSON holds no comments, so the reasons
come first. `allowManagedPermissionRulesOnly` makes this file the only source of rules, so a
settings file in the repository cannot add one. `allowManagedHooksOnly` runs only the hooks this
file sets, and it sets none, so no hook from the repository can approve a call.
`disableBypassPermissionsMode` and `disableAutoMode` keep a changed start command from skipping
every check, or from handing the checks to auto mode's classifier instead of the allow list [6].
`dontAsk` denies every call that would prompt; reads inside the clone, read-only commands and
calls an allow rule approves still run, so a tool or command the allow list does not name stays
closed until this file or the job's start command changes. The deny rules hold in every mode, so
these paths stay closed even if the start command changes. None of them covers a script that
writes a file itself; the job's check on the fetched branch does (agents.md section 3).

```json
{
  "allowManagedPermissionRulesOnly": true,
  "allowManagedHooksOnly": true,
  "permissions": {
    "defaultMode": "dontAsk",
    "disableBypassPermissionsMode": "disable",
    "disableAutoMode": "disable",
    "allow": [
      "Edit(./pyproject.toml)",
      "Edit(./src/**)",
      "Edit(./tests/**)",
      "Bash(uv lock *)",
      "Bash(uv sync *)",
      "Bash(uv tree *)",
      "Bash(uv run pytest *)",
      "Bash(git diff *)",
      "Bash(git status *)"
    ],
    "deny": [
      "Edit(./.github/**)",
      "Edit(./.claude/**)",
      "Edit(./docs/delegations/**)",
      "Edit(./.python-version)",
      "Edit(./Dockerfile)",
      "Edit(./compose.yaml)"
    ]
  }
}
```

The start command, the step's `run:` script in `.github/workflows/deps-weekly.yml`. The rest of
the workflow is left out; pipeline-security.md section 10 gives its form. The workflow's `env:`
sets the two constants.

```sh
# The model and its effort are named constants in the workflow's env: a dated model id, never
# an alias that moves, and its effort, so a change to either is a reviewed diff
# (prompt-engineering.md section 15).
claude -p "<the weekly task>" \
  --append-system-prompt-file docs/delegations/dependency-updates.md \
  --model "$DEPS_AGENT_LLM_MODEL" --effort "$DEPS_AGENT_LLM_REASONING_EFFORT" \
  --permission-mode dontAsk --max-turns <n> --output-format stream-json --verbose
# Departs from prompt-engineering.md section 11, which asks for a response schema: the run's
# output is a branch the job checks (step 2 of the run) and a note a person reads, which the job
# posts with its own facts added. The cost: no code checks that a note holds the forecast, the cause, the
# options and a recommendation, so a note that misses one reaches Jane Doe that way.
```

The first exception note the agent sent under the delegation, as the job posted it in
#team-backend. The package and the advisory are invented:

```text
Exception note: dependency updates, run of 2026-11-09
To: Jane Doe, decider for the area

Forecast: the fix for advisory EXAMPLE-2026-0042, rated high, in example-pdf (the library that
renders invoice PDFs) ships only in 5.0.0. We run 4.9.3. Taking the fix breaks the limit
"patch and minor versions only"; without it, the advisory stays open in production.

Cause: the maintainers fixed it on the 5.x line only and have announced no more 4.x releases.

Options:
1. Update to 5.0.0 in a pull request of its own. Cost: 5.0.0 renames render() to
   render_pdf(), so every call site in src/ changes (the job's count is below); about half a
   day of review.
2. Stay on 4.9.3 and turn off the affected feature, custom fonts in invoice PDFs, by its
   setting. Cost: Globex's invoices lose their custom font until option 1 lands.
3. Stay on 4.9.3 and accept the advisory until the planned upgrade in December. Cost: a
   high-rated advisory stays open for about six weeks.

Recommendation: option 1, reviewed by John Smith, who knows the PDF code best.

Added by the job from its log: scanner step, EXAMPLE-2026-0042 in example-pdf 4.9.3, fixed in
5.0.0; test suite at the start of the run, 212 passed and 0 failed; call sites of render( in
src/ on main, from the job's git grep in its own clone: 14.
```

Jane Doe chose option 1 the same day and gave the update to John Smith as PROJ-131. The agent's
next runs left `example-pdf` alone, because a major version stays outside its limits.

## Why it is good

- **One decision area, one decider with a backup, and the intent first.** The agent knows what
  the work is for, so a choice the limits do not name has an answer, and a report always has a
  person to go to ([agents.md](agents.md) section 2;
  [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5).
- **The delegation loads in every run.** The start command passes it with
  `--append-system-prompt-file`, which appends the file's text to the system prompt [9]. A link
  alone leaves it to the agent: of a `CLAUDE.md` that tells Claude in words to read another file,
  Claude Code's documentation says "Claude sees `AGENTS.md` only if it decides to open the
  file" [10].
- **The limits are a tolerance, and breaking one is a report, not a judgement call.** Each limit
  is a number or a list a reviewer can check, and each of the four report conditions names a
  situation the agent can recognise (sections 2 and 4).
- **Every limit has its enforcement written next to it, and the table says which ones no tool
  enforces.** The team knows that the dependency, test and size limits rest on the review at the
  merge, and the
  reviewer knows that this is what they are there to check (sections 3 and 5).
- **The agent cannot change its own rules.** The rules sit in managed settings, which no other
  level can override [5]; the file is root-owned in the image; the deny rules hold in every mode,
  `bypassPermissions` included [6]; with `allowManagedPermissionRulesOnly`, Claude Code
  ignores rules from the repository's own settings files [7]; and with `allowManagedHooksOnly`,
  no hook from the repository runs [7]. A managed file the agent's user cannot read starts the
  run "without that source's policies", and a `-p` run reports that, and any rule it dropped as
  invalid, on stderr [11]; so the job checks the file before the start and stops on any stderr
  line at startup. Deny rules do not cover a Python script that writes a file itself [5], so the
  job checks the changed files on the fetched branch, in its own clone outside the container
  (section 3). It turns rename detection off, because `git diff` turns it on by default and
  `--name-only` shows only "the name of each changed file in the post-image tree" [8]: a
  moved file would show its new path only.
- **The agent holds no GitHub credential at all.** It cannot push or merge, and `github.com`
  stays off the allowlist, so it cannot post code to a code host. No secret sits in the
  container; the hosts left on the list, the model API and the package index, are still ways out,
  and the delegation names them ([agent-containers.md](../docker/agent-containers.md) sections 4,
  5 and 7).
- **No prompt during a run, one approval at the merge.** In `dontAsk` mode a call that would
  prompt is denied instead [6]. Every change stays on a branch until a person merges it, so the
  approval comes where a person can still refuse the merge; the pull request's CI runs the
  agent's code as soon as someone approves the runs, and GitHub allows that before the diff is
  read, which is why it holds no deploy secret. Nobody clicks through a
  hundred routine prompts ([agents.md](agents.md) section 5; [git.md](../git/git.md) section 5).
- **The note brings a decision back in the form the decider already reads.** It holds the
  forecast, the cause, two or three options with what each costs, and a recommendation, as
  [communication.md](../project-management/communication.md) section 5 gives it. The job, not
  the agent, adds the facts about state ([agents.md](agents.md) section 4).
- **"Done" is the required check, not the agent's word**
  ([agents.md](agents.md) section 6; [pipeline.md](../ci-cd/pipeline.md) section 6).

## Where each part comes from

| Part of the delegation | Listed by |
|---|---|
| One delegation per decision area | Appelo [4] |
| The decider and a backup | [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5; the backup is this practice's choice ([agents.md](agents.md) section 2) |
| The intent, kept by the person who delegates | ADP 6-0 [1] |
| What the agent decides on its own, within limits | ADP 6-0's freedom of action "equal to the level of acceptable risk" [1]; PRINCE2's tolerances [2] |
| No more autonomy than the work needs | OWASP [3] |
| The file under version control, changed through a reviewed pull request | OWASP [3]; "always allow" as such a change is this practice's inference ([agents.md](agents.md) section 2) |
| The report conditions | PRINCE2's exception on a forecast breach of a tolerance [2]; the others are this practice's rules ([agents.md](agents.md) section 4) |
| The form of the report | [communication.md](../project-management/communication.md) section 5 |
| No prompt for routine actions, one approval at the merge | this practice's rule ([agents.md](agents.md) section 5) |
| The enforcement table, with the limits no tool enforces named | this practice's rule ([agents.md](agents.md) section 3) |
| The managed settings | Claude Code's documentation [5], [6], [7] |
| The delegation passed in the start command; the check of the managed file and the stop on stderr | Claude Code's documentation [9], [10], [11] |
| The job: a read-only agent job, a separate job that checks and writes, the caps on turns, time and parallel runs | [pipeline-security.md](../ci-cd/pipeline-security.md) section 10 |
| The changed-paths check with rename detection off | git's documentation [8] |
| `.github/CODEOWNERS` owned by the decider too | GitHub's documentation: "you also need to define an owner for the CODEOWNERS file itself" [12] |
| The container, the credentials, the proxy, the bundle | [agent-containers.md](../docker/agent-containers.md) sections 3, 4, 5 and 7 |

## Sources

Checked 2026-10-30 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Headquarters, Department of the Army — ADP 6-0, Command and Control, 07 July 2026 — https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN47032-ADP_6-0-000-WEB-1.pdf — checked 2026-10-29
- [2] PeopleCert — PRINCE2 7 Practitioner Sample Paper 1, Answers and Rationales (a copy hosted by prince2.wiki, a training firm's site) — https://prince2.wiki/downloads/p2p-a1.pdf — checked 2026-10-29
- [3] OWASP GenAI Security Project — OWASP Top 10 for Agentic Applications for 2026, Version 2026 — https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ — checked 2026-10-29
- [4] Jurgen Appelo — Leading Agile Developers: The Seven Levels of Authority (Part 2) (InformIT, 2011; opinion) — https://www.informit.com/articles/article.aspx?p=1675546&seqNum=3 — checked 2026-10-29
- [5] Anthropic — Claude Code documentation: Configure permissions — https://code.claude.com/docs/en/permissions
- [6] Anthropic — Claude Code documentation: Choose a permission mode — https://code.claude.com/docs/en/permission-modes
- [7] Anthropic — Claude Code documentation: Settings reference — https://code.claude.com/docs/en/settings-reference
- [8] Git — git-diff documentation (`--name-only`, `--no-renames`, `diff.renames`) — https://git-scm.com/docs/git-diff
- [9] Anthropic — Claude Code documentation: CLI reference — https://code.claude.com/docs/en/cli-reference
- [10] Anthropic — Claude Code documentation: How Claude remembers your project — https://code.claude.com/docs/en/memory
- [11] Anthropic — Claude Code documentation: Deploy managed settings — https://code.claude.com/docs/en/managed-settings
- [12] GitHub — GitHub Docs: About code owners — https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- [13] GitHub — GitHub Docs: Triggering a workflow — https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow#triggering-a-workflow-from-a-workflow
