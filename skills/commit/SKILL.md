---
name: commit
description: >-
  Draft a commit message for the current git changes following the project's commit convention
  (type [TICKET-ID] / type(scope) title in business terms + self-contained bullets + the model
  attribution trailer), show it for review, and only after explicit approval stage the named files
  selectively and commit. Use this skill whenever the user wants changes committed or a commit
  message written. Triggers: "commit", "commit this", "commit the changes", "make a commit",
  "write a commit message", "commit msg". NOT for pushing or pull requests — pushing and PR
  create/update belong to a separate `pr` skill, or to the user. A project can
  specialize it — ticket-key pattern, excluded paths, scope vocabulary, house examples — via a
  binding file at .claude/skills/commit/SKILL.md, read at the start of a run when present.
argument-hint: [optional feedback, e.g. "type should be fix, not feat" or "title too vague — lead with the roster fix"]
allowed-tools: Read, Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git branch *), Bash(git var *), Bash(git config --get *), Bash(git config --global --get *), Bash(git config --local --get *), Bash(git config --show-origin --get *), Bash(git add *), Bash(git commit -m *)
---

# commit — draft the message, then (after approval) commit selectively

Two strict phases. First draft the commit message and show it in chat; then — **only after the
user explicitly approves** — stage the files by explicit path and commit. Never stage or commit
in the same turn as the draft. If the user only wanted the message text, phase two simply never
runs.

## Project binding (resolve once, before Step 1)

This skill carries no project specifics. Check for a **project binding file** at
`${CLAUDE_PROJECT_DIR}/.claude/skills/commit/SKILL.md`. If it exists, Read it — it carries **repo
facts only** (the ticket-key pattern, paths excluded from staging and from the message, the scope
vocabulary for ticketless branches, house example messages) and **wins on conflict**. (User-level
skills win same-name registration over project-level ones, so a project specialization is
delivered as this binding file that you read, not as a skill that shadows this one.) Without a
binding, infer the conventions from `git log` history and the project's instruction files.

## Step 0: Apply user feedback (if arguments were given)

Arguments: $ARGUMENTS

If arguments are provided, they are the user's instructions for the commit message — WHAT to
improve and HOW. Apply them on top of all the rules below; where feedback conflicts with a rule
below, the feedback wins. Typical feedback:

- **Wrong type** — "this is a fix, not a feat" → use the type the user named in Step 4
- **Title focus** — "lead with X", "title is too vague/too implementation-heavy" → rewrite the
  title around what the user pointed at
- **Bullet content** — "drop the bullet about Y", "mention the config change", "bullet 2 is
  cryptic — explain why" → add/remove/rewrite the named bullets
- **Scope** — "only describe the adapter changes", "ignore the test files" → narrow the analysis
  to what the user named
- **Wording/tone** — "shorter", "more business terms", "in English" → adjust the style

When revising a message you already produced earlier in this conversation, change ONLY what the
feedback targets — keep everything else verbatim.

## Step 1: Gather context

1. `git status --short` — all changed, staged, unstaged, and untracked files
2. `git diff` and `git diff --cached` — actual content of changes
3. `git log -5 --format="%H%n%B%n---"` — recent commits for tone, format, and ticket reference
4. `git branch --show-current` — extract the ticket key from the branch name
5. The identity gate — run the check in § Identity gate at the end of this file. Outcome: a
   repo-local `user.name` + `user.email` pair that `git var` confirms → proceed under it without
   asking; anything else is STOP-and-escalate now — before drafting a message the user cannot
   safely commit.

## Step 2: Determine ticket / scope

Extract the ticket key from the branch name using the project's tracker pattern (the binding
names it — e.g. a branch `PROJ-123-description`; without a binding, infer the pattern from recent
commit history); if the branch has none, check recent commits for a `[PROJ-123]`-style reference.
**A ticket is used when it exists — never invented.** On ticketless branches (e.g.
`fix/frontend-public-assets`), follow the conventional-scope style recent history uses instead:
`type(scope): title` (scope = the module or area, from the binding's scope vocabulary or the
repo's top-level layout), or bare `type:` when no scope fits.

## Step 3: Exclude working-artifact paths

Paths the project marks as working documents (the binding lists them; a dated-artifacts
convention in the project's instruction files counts) must NOT be described in the commit message
nor staged. Ignore them entirely, at every depth — such trees typically nest by date and area, so
match the whole subtree, not just the first level.

## Step 4: Choose the commit type

Pick exactly one type based on the nature of the changes:

- `feat` — new feature or capability
- `fix` — bug fix
- `refactor` — code restructuring with no behavior change
- `test` — test-only changes
- `docs` — documentation-only changes
- Omit the type entirely for general/mixed changes that do not fit the above

If changes span multiple types (e.g., a feature plus a refactor), pick the dominant one. Do not
combine types.

## Step 5: Write the commit message

```
type [PROJ-123]: Title describing the change in business terms   ← use when a ticket exists
type(scope): Title describing the change in business terms      ← otherwise

- Bullet point 1
- Bullet point 2

Co-Authored-By: <current model attribution> <noreply@anthropic.com>
```

The `Co-Authored-By` trailer is the harness convention — every commit carries it, naming the
model that authored the change.

### Title rules

- Summarize the feature or change in business terms, not implementation terms
- A reader must understand what was done from the title alone
- Keep it concise but specific

### Body rules

- When the WHY needs more room than the title gives, open with a short context paragraph before
  the bullets (do this for non-obvious changes) — what was wrong or missing and why it matters.
  Skip it when the title already says enough.
- Each bullet must be a clear, self-contained statement — not cryptic shorthand
- Describe WHAT was done and WHY it matters (the business purpose)
- Include enough context to understand scope and impact without looking at the diff
- Cover ALL meaningful changes across all changed files (except excluded artifact paths)
- Do NOT list file names that are obvious from the diff (e.g., "Rename foo.py to bar.py")
- Do NOT write vague bullets like "Update schemas" or "Add new service" — explain what the
  schema change does or what the service provides

### What GOOD looks like

```
feat [PROJ-123]: Add the export scheduler for nightly report delivery

- Add a scheduler service that walks the pending-export queue every night and writes each report to the delivery bucket, so customers get reports without a manual trigger
- Register it via the existing job-runner config; no orchestration code change needed
- Add the new job name to the runner's roster assertion in the job-runner tests
```

```
fix(frontend): Serve static assets from the standalone runtime image

- Add a COPY step for the public/ folder into the standalone output stage so static assets (favicon, images) are served from the built image, not just in local dev
- The standalone build only bundles server files by default; public/ has to be copied in explicitly
```

```
fix [PROJ-123]: Reject a config entry with no description at load time

- Raise from the loader when the description field is missing or blank, instead of silently registering an undescribed entry
- A missing description previously broke request routing without any signal at load time
```

### What BAD looks like (avoid these patterns)

Too cryptic, lists file renames instead of explaining the purpose:
```
refactor [PROJ-123]: Rename middleware files and add a naming note

- Rename request_logger.py -> structured_request_logger.py
- Rename cache_layer.py -> write_through_cache_layer.py
- Update imports in the app entry points
- Add the naming note to the coding-standards rule
```

Not understandable without looking at the diff:
```
feat [PROJ-123]: Add tool grounding

- Add new tool group and script
- Wire up the tool server
- Update the agent config
```

## Step 6: Show the draft and STOP

Present the commit message inside a single code block, followed by ONE line listing the exact
files that approval will stage and commit (explicit paths). Then stop and wait. If the user
requests edits, apply them (Step 0 rules) and show the updated draft again. Read
`${CLAUDE_SKILL_DIR}/output_example.md` before you show the first draft: it shows one Step 6
output on invented values.

## Step 7: After approval — stage selectively and commit

1. Re-run `git status --short` immediately before staging — other sessions may share this
   working tree — and re-run the § Identity gate check: a concurrent session can change
   `.git/config` between the draft and the commit.
2. Stage ONLY the files that belong to this change, each by explicit path:
   `git add <file1> <file2> ...`. **Never `git add -A`, `git add .`, or `git commit -a`.**
3. If a file that must be committed also carries unrelated uncommitted changes (someone else's
   work mixed into it), STOP and surface it instead of silently including it.
4. Commit with a quoted heredoc so the message survives verbatim:

   ```bash
   git commit -m "$(cat <<'EOF'
   ...approved message...
   EOF
   )"
   ```

5. Show `git log -1 --stat` to confirm what landed. Do NOT push — pushing belongs to a separate
   `pr` skill, or to the user.

## Identity gate

The identity on a commit belongs to the user, and it lives **per repo**: the repo-local
`git config` (`.git/config`) only. A global identity is not used: never suggest `--global`, and
never expect a `~/.gitconfig` identity to exist. A project binding or the feedback in Step 0 may
make this gate, and the staging rules in Step 7, stricter, but never relax them. Read-only check,
run in Step 1 and again in Step 7:

1. `git config --local --get user.name` and `git config --local --get user.email`.
2. **Both set locally** → confirm this is the identity that will land: `git var GIT_AUTHOR_IDENT`
   and `git var GIT_COMMITTER_IDENT` must show the same name and email as that pair. Match →
   proceed under exactly this identity, without asking. Mismatch → something overrides the
   local config (a `GIT_AUTHOR_*` / `GIT_COMMITTER_*` environment variable, or an
   `author.*` / `committer.*` config entry) → STOP, show the source, and ask.
3. **Not set locally, but a global, system, or environment value exists** → never commit under
   it. Tell the user the value and where it comes from
   (`git config --show-origin --get user.email`) and STOP: the user removes it by hand and sets
   the repo-local pair.
4. **No identity anywhere** → STOP and ask the user to set the repo-local pair. Git often does not
   fail here: unless the host name is not a full domain name or `user.useConfigOnly` is set, it
   invents a name from the OS user name and host name and commits with exit 0. So the commit must
   never be attempted.

**Never set, change, or override the identity yourself.** Do not invent values, and do not copy
them from another repo, a log, or the environment. Do not set the identity with `git config`
(`user.*`, `author.*`, `committer.*`), `git -c`, `--author` / `--reset-author`, or the
`GIT_AUTHOR_*` / `GIT_COMMITTER_*` / `EMAIL` variables, and do not edit a git config file. The
user configures it; the skill only uses it. Three boundary notes:

- Setting a repo-local value the user dictated in this session, when the user asks you to set
  it, is the user configuring it through you: allowed. Anything less explicit is not.
- Undoing an identity you yourself just wrote (`git config --unset …`) is required, not
  forbidden: undo it and tell the user.
- This rule covers every repo except one that your own test creates with `git init` in a
  temporary folder. A clone, a checkout or a linked worktree of the user's repo is still the
  user's (a linked worktree shares `.git/config` with the main checkout).

On STOP, say what failed and wait for the user's answer: no second attempt, no workaround. If
something re-invokes you after a STOP (a hook, a retry, a restart), repeat the blocker and stop
again: a restart is not an answer.
