---
name: pr
description: >-
  Create or update the GitHub pull request for the current branch using this skill's fixed PR
  description template (Summary with optional table/mermaid, tracker-ticket link, feature-level
  "What's Changed", Verification, Notes, ⚠️ Breaking Changes, Risks). Use this skill whenever the
  user wants a PR created, updated, refreshed, or a commit pushed to a branch that has (or needs) a
  PR — even if they only say "PR". Also handles GitHub stacked PRs (public preview): a PR on top of
  another open PR, publishing a whole stack of layered branches, or updating one layer. English
  triggers: "create a PR", "open a PR", "make a PR", "update the PR", "refresh the PR
  description", "push and update the PR", "push the commit", "stacked PR", "stack of PRs", "PR on
  top of". Always drafts the title + description in chat first and waits for explicit
  approval before pushing or calling gh — the one exception is a bare push request, which may
  also self-assign your own open PR when its Assignees field is empty. Not for posting review comments onto a PR (that is
  a separate review skill, where present). A project can specialize it — ticket pattern and tracker
  URL, gate commands for Verification, a breaking-changes catalog, excluded paths — via a binding
  file at .claude/skills/pr/SKILL.md, read at the start of a run when present.
argument-hint: [optional extra context — motivation, "mark as draft", what to emphasize]
allowed-tools: Read, Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git branch *), Bash(git rev-parse *), Bash(git merge-base *), Bash(git var *), Bash(git config --get *), Bash(git config --global --get *), Bash(git config --local --get *), Bash(git config --show-origin --get *), Bash(git push *), Bash(gh pr *), Bash(gh repo *), Bash(gh stack *), Bash(gh extension list)
---

# pr — create or update the GitHub PR for the current branch

One skill for the whole PR lifecycle: it detects whether the current branch already has an open
PR and either **creates** one or **updates** it (description, title, new commits). The
description always follows the fixed template below.

`$ARGUMENTS` (if present) is extra context to reflect in the description (motivation, a
constraint, "mark as draft", what the user wants emphasized).

## Project binding (resolve once, before Step 0)

This skill carries no project specifics. Check for a **project binding file** at
`${CLAUDE_PROJECT_DIR}/.claude/skills/pr/SKILL.md`. If it exists, Read it — it carries **repo
facts only** (the ticket-key pattern and tracker URL template, the gate commands the Verification
section names, the repo's breaking-changes catalog, paths excluded from the reviewable change)
and **wins on conflict**. (User-level skills win same-name registration over project-level ones,
so a project specialization is delivered as this binding file that you read, not as a skill that
shadows this one.) Without a binding, infer the ticket pattern from branch/commit history and the
gates from the project's instruction files.

## Principles (why the template looks like this)

The description exists to make review fast — a clear description measurably cuts review time.
Every section must change what the reviewer does: point at a risk, explain a non-obvious
decision, or save them from reverse-engineering the diff.

- **Answer the reviewer's three questions**: what changed, why, and how it was verified.
- **Nothing for its own sake.** A required section with nothing real to say for THIS
  change is omitted, not filled with boilerplate — "no risks" is never written.
- **The description comes from the diff**, not from commit messages alone. Commit messages tell
  the story of the work; the description describes the net change.
- **Visuals only when they beat prose.** A table for short enumerable facts (renamed fields,
  moved constants, before/after values). ONE mermaid diagram only when the PR introduces or
  reroutes a multi-component flow a reviewer would otherwise reconstruct from the diff —
  `flowchart` for structure, `sequenceDiagram` for multi-step/async protocols. Never diagram a
  linear or single-layer change.
- **Surprises are flagged loudest.** Breaking changes, contract changes, and behavior changes
  outside the headline feature are what reviewers miss most — they get the ⚠️ treatment, with
  blast radius and migration, never a buried mention.
- **Claim only what happened.** The Verification section lists checks actually run in this
  session; anything not run is listed as "for the reviewer/author to run".

## Stacked PRs (GitHub public preview, 2026-07)

A stack is an ordered chain of PRs where each layer targets the branch below it. GitHub renders
a stack map at the top of every member PR, lets each layer be reviewed as its own diff, and
**auto-retargets** upper layers when a lower one merges. CLI support is the `gh-stack` extension
(`gh stack …`) — verify with `gh extension list`; if missing, ask before installing
(`gh extension install github/gh-stack`).

**Stacked mode is ON when any of:**

- the user asks for it ("stack this on top of PR #N");
- the current branch's open PR already targets a branch other than `main`
  (`baseRefName` from Step 0) — updating an existing layer;
- the branch was cut from another branch whose PR is still open (`gh pr list --state open
  --json headRefName` + `git merge-base --is-ancestor <head> HEAD`) — then ASK: stack layer on
  top of it, or wait for the lower PR to merge? Never silently create a PR against `main` whose
  diff includes another open PR's commits.

**Rules in stacked mode:**

- `<base>` = the branch of the layer directly below, not `main`. Every `git log`, `git diff`,
  and `gh pr create --base` in Steps 1–5 uses it — the PR describes ONE layer's diff only.
- Several layers needing PRs → draft ALL titles + bodies in one approval message, bottom layer
  first; after approval create them bottom-up, each against its own `<base>`.
- After creating, link the chain: `gh stack link <bottom-pr> <next-pr> … <top-pr>` (PR numbers
  bottom→top; works without local gh-stack tracking). Adding one layer to an existing stack:
  `gh stack link <stack-number-or-any-member-pr> <new-pr>`.
- Never hand-write "part N of M" or a stack diagram into the body — GitHub renders the stack
  map itself, and hand-written copies go stale on retarget.
- After a lower layer merges, do NOT retarget manually — GitHub does it. In UPDATE mode simply
  regenerate from the current `baseRefName`.
- Stack maintenance is not this skill's job: `gh stack rebase` / `sync` / `merge` / `modify` /
  `push` rewrite history or merge PRs — run them only when the user explicitly asks.
- Limits: all branches must live in the same repository (no cross-fork stacks); the feature is
  a public preview. If `gh stack` exits with code 9 (not enabled for this repo), fall back to
  plain chained PRs: same `--base <parent>`, no linking, and a "dependent PRs" line in Notes.

## Assignees

An empty Assignees field never passes unnoticed, and it is never filled behind the user's back.
The two modes differ: a PR this skill CREATES is self-assigned automatically; on a PR it EDITS
the empty field becomes a proposal in the draft and waits for the same yes as the description.

- **CREATE — automatic.** `--assignee "@me"` on every `gh pr create`, each layer of a stack
  included. The account running the skill is the one opening the PR, so nothing is asked.
- **UPDATE — propose, never act alone.** Step 0's `assignees` list came back empty → say so in
  the Step 4 draft and propose ONE login: the PR's `author.login`, the person who opened it and
  did the work. Print that login, never a placeholder.
  - Approving the draft approves the printed login with it — Step 4 named the account, so a
    plain yes is a yes to it — and `--add-assignee <login>` rides the same `gh pr edit` that
    writes the body. Only an explicit no to the assignee leaves the field empty: write the
    body and report it. Silence is not a refusal, and must never be reported as one.
  - Approved the assignee but not the text → `gh pr edit <number> --add-assignee <login>` alone.
  - `author.is_bot` is true → the login is `app/<name>` and cannot be assigned. Propose no
    substitute: report that the author is a bot and ask the user whom to assign. Proposing
    yourself here would be proposing to take over someone else's PR.
  - Stacked mode → one named proposal per layer whose field is empty; one yes covers only the
    layers the draft named.
- **A PR you did not open is never changed unasked.** The one assignment allowed there is the
  approved proposal above. The push-only path (the Step 0 item 4 exception, which skips the
  Step 4 approval) therefore self-assigns ONLY when the PR's author is you. Establish that with
  `gh pr list --author "@me" --state open --head <branch> --json number` — `allowed-tools`
  permits it and `@me` resolves to the authenticated GitHub login, while a git
  `user.name`/`user.email` is a different identity and proves nothing here. Keep `--head`: the
  bare list pages at 30, so a heavy author's own PR can fall off it and read as someone else's.
  The PR's number in that list → run
  `gh pr edit <number> --add-assignee "@me"` and report it. Not in the list → report the empty
  field and stop: no assignment, no `gh pr edit`.
- **A PR that already has assignees is left alone** — the rule fills an empty field, it never
  takes a PR over, and it never removes or replaces an assignee.
- **The check, before the run ends** — `gh pr view <number> --json assignees` for every PR this
  run created or edited; the bare form reads the current branch only, so stacked layers need
  their own numbers. An empty list is legitimate on two edited PRs only: one whose named
  proposal the user turned down, and one whose author is a bot, where whom to assign is still
  an open question to the user — say which in the closing report. Anywhere else — a PR this run
  created, or an edited one whose proposal was approved — it is a defect, and `gh` exited 0 so
  there is no error to quote: run `gh pr edit <number> --add-assignee <login>` once and re-read;
  only if it is still empty follow the refusal bullet below.
- **When `gh` refuses the login** — an assignee must have push access to the repo, so a fork
  or a read-only account is rejected. What survives the refusal differs by command (both read
  from the gh 2.97.0 sources):
  - `gh pr create` opens the PR and assigns in a *second* mutation, so the refusal exits
    non-zero with `pull request update failed` while **the PR is already live**. Never re-run
    `gh pr create` — it answers "a pull request for branch … already exists". Run
    `gh pr view --json number,url,assignees` to see what exists.
  - `gh pr edit` assigns *before* it writes the fields, so **nothing landed** — not the body,
    not the title, not the assignee. Re-run the same `gh pr edit` without `--add-assignee`
    first, so the approved description lands; only then handle the login.

  In both cases: report the PR URL together with the exact error, and ask the user which
  account to assign. Never guess a login — an account choice is the user's to give (global
  CLAUDE.md § Blocked on user input).

## Step 0: Detect mode

1. `git branch --show-current` — **abort if on `main`**. Extract the ticket from the branch name
   using the project's tracker pattern (the binding names it — e.g. `ABC-123-description`); if
   absent, look for `[ABC-123]`-style references in the branch commits. If still absent, the
   branch is ticketless — use the `type(scope): …` title form (Step 2).
2. `gh pr view --json number,url,state,isDraft,title,body,baseRefName,assignees,author` —
   - an **open** PR exists → **UPDATE mode**;
   - no PR (or only closed/merged ones) → **CREATE mode**.
   - Resolve `<base>`: the PR's `baseRefName` in UPDATE mode; in CREATE mode `main`, unless
     stacked mode applies (see the Stacked PRs section) — then the parent layer's branch.
     `<base>` drives every diff and `gh` call below.
3. `git status --short` — if there are uncommitted changes, warn that they will NOT be in the
   PR and ask whether to continue.
4. Unpushed commits (`git log origin/<branch>..HEAD` — or the whole branch if it has no
   upstream): pushing is normally bundled into the approval step. Before ANY push (here
   or at Step 5), run the outgoing-author check:
   `git log <base>..HEAD --format='%an <%ae>'` (dedup the list yourself) — an author
   that fails the global CLAUDE.md § Git identity check (guessed `OS-username@hostname`,
   or a name/email that is not this repo's local `user.name`/`user.email` pair) is
   STOP-and-ask; never amend or reset authorship yourself.
   **Exception:** the user explicitly said to push ("push the commit") —
   then, once the outgoing-author check passes, push immediately
   (`git push -u origin HEAD`), report the result, and continue.
   - If the user ONLY asked to push and the branch has no open PR: push, report, and stop —
     ask whether they want a PR opened rather than creating one unprompted.
   - If the user ONLY asked to push and the branch HAS an open PR with an empty `assignees`
     list: when the PR's author is you (§ Assignees names the check), run
     `gh pr edit <number> --add-assignee "@me"` in the same turn and report it; on someone
     else's PR, report the empty field and stop there.

## Step 1: Gather the change

1. `git log <base>..HEAD --format="%H%n%B%n---"` — every commit going into the PR.
2. `git diff <base>...HEAD --stat`, then the full `git diff <base>...HEAD` — read the actual
   changes end-to-end.
3. Ignore the project's excluded working-artifact paths entirely, at every depth (the binding
   lists them; dated-artifacts trees nest by date and area) — working documents, not part of the
   reviewable change.
4. **UPDATE mode only:** read the current PR body. Identify content the template does not own —
   sections added by teammates or reviewers, deployment notes, task checklists. That content is
   carried over verbatim; template-owned sections are regenerated from the full cumulative diff
   (never appended as "update 2: …").

## Step 2: Title

Same convention as commit messages:

```
type [ABC-123]: What the change does, in business terms   ← use when a ticket exists
type(scope): What the change does, in business terms      ← otherwise
```

`type` is one of `feat` / `fix` / `refactor` (omit for mixed changes). A reader must understand
the PR from the title alone. Never derive the title from the branch name. In UPDATE mode, keep
the existing title unless the PR's scope has genuinely changed — then propose the new one in the
draft.

## Step 3: Description — the fixed template

Sections in this exact order. "Always" sections appear in every PR; conditional sections appear
only when the diff warrants them — otherwise they are omitted entirely (no empty headers).

### Always

- **`## Summary`** — what the PR does, why, and the headline decisions or numbers
  a reviewer should know before opening files. Bold the key terms. Add a table or ONE mermaid
  diagram per the visuals rule above when it genuinely speeds up orientation.
- **The ticket section** — the tracker link, built from the binding's section title and URL
  template (e.g. `## Jira Ticket` with `[ABC-123](https://tracker.example.com/browse/ABC-123)`).
  Omit the section only if there is genuinely no ticket (no branch prefix, nothing in commits,
  nothing in `$ARGUMENTS`).
- **`## What's Changed`** — the detailed part, at **feature level**, not file level. One bolded
  entry per feature/change: what it does, why it exists, and how it fits the
  existing flow. A reviewer should be able to predict the diff from this section.

  ```markdown
  - **Retry on rate limit.** The payment client now retries a request the provider rejects
    with HTTP 429, waiting the time its `Retry-After` header names, up to three tries. This
    lets a short burst of checkouts finish instead of failing at the provider's limit.
    Implemented as `RateLimitRetry` in the HTTP client; a fourth 429 fails the request with the
    provider's error, as before.
  ```
- **`## Verification`** — two lists, honestly separated:
  - *Checked in this session* — automated gates actually run, scoped to the stacks the PR
    touched (the project's gate commands — the binding lists them per stack; else take them from
    the project's instruction files or build config) and manual checks performed, each with its
    observed result.
  - *For the reviewer* — manual steps with **expected results** (include a negative check when
    the change has a permission/scoping/error path), and any gates not run.

### Conditional — only when the diff warrants it

- **`## ⚠️ Breaking Changes`** — anything a consumer or teammate must react to: a config or
  frontmatter contract change (renaming or removing a required field), a rename that changes a
  public identifier every caller uses (an API operation, a tool name, an event), a schema or
  template field change, changed defaults, env-var or config changes — the binding carries the
  repo's own catalog of what tends to break here. For each: what breaks, the blast radius
  (who/what is affected), and the migration step. This section is never soft-pedaled into Notes.
- **`## Notes`** — important context that fits nowhere else: non-obvious decisions and their
  rationale, behavior changes OUTSIDE the headline feature (fixes bundled in, semantics changed
  in passing), dependencies added/updated (name, exact version, one-line purpose), dependent PRs
  or deployment ordering. Contract-adjacent changes that are NOT breaking still get a blockquote:

  ```markdown
  > ⚠️ **Contract change:** `export__extract_fields` → `export__extract`. The public tool
  > name changes for every caller in this PR.
  ```
- **`## Risks`** — what could actually regress and what is NOT covered by tests, so
  the reviewer knows where to look hardest. Only real risks.

## Step 4: Show the draft and STOP

Before you write the draft, read the case for your mode in `${CLAUDE_SKILL_DIR}/output_example.md`.

Present the title and the full description body in a single markdown code block (so the user
sees the raw markdown, mermaid included). In UPDATE mode, first say what changed
versus the current PR body (e.g., "added the new commits to What's Changed, rewrote Summary,
kept your reviewer checklist"). Stacked mode with several layers: one code block per layer,
bottom first, each labeled with its branch and `<base>` — a single approval covers the set.

After the block, state in one line exactly what approval will trigger:
- CREATE: push the branch (if needed) and `gh pr create` against `<base>`, assigned to `@me`;
  in stacked mode also `gh stack link` to attach the chain.
- UPDATE: push new commits (if any and not already pushed) and `gh pr edit`. When the PR has no
  assignee, the same line names the proposal: the field is empty, and approving this draft also
  adds `<login>` to it in that call. Print the login itself, never the placeholder (§ Assignees).

Then stop and wait. If the user requests edits, apply them and show the updated draft again.
Never push or call `gh pr create`/`gh pr edit` in the same turn as the draft — the one exception
is an assignee the user has just approved (§ Assignees), which may land while the revised text
waits for its own yes.

## Step 5: After approval — execute

1. If the branch isn't on the remote (or is behind locally): `git push -u origin HEAD` —
   after the Step 0 outgoing-author check.
2. **Assignees** — apply § Assignees: the CREATE command below always carries
   `--assignee "@me"`; the UPDATE command carries `--add-assignee <login>` only when the user
   approved that proposal at Step 4.
3. Apply the approved text verbatim, using a quoted heredoc so the markdown survives:

   ```bash
   # CREATE
   gh pr create --base <base> --assignee "@me" --title "..." --body "$(cat <<'EOF'
   ...approved body...
   EOF
   )"

   # UPDATE
   gh pr edit --body "$(cat <<'EOF'
   ...approved body...
   EOF
   )"
   # plus --title "..." only if the title changed
   # plus --add-assignee <login> only if the user approved the assignee proposal
   ```

4. Stacked mode only — after every layer's PR exists, link the chain (see the Stacked PRs
   section): `gh stack link <bottom-pr> … <top-pr>`, or `gh stack link <existing-member-pr>
   <new-pr>` when extending a stack. Exit code 9 → fall back per the Stacked PRs section and
   tell the user.
5. Print the PR URL(s) **and, per PR number, the assignee `gh pr view <number> --json assignees`
   reports**. An empty list on any of them → follow § Assignees, which names the two legitimate
   cases and what to run for every other one; the closing report says which case it was, never
   just that the field is empty. If `gh` fails for any other reason (no auth, no remote), report
   the exact error and stop — do not retry with workarounds.
