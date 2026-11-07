# Git rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. Branches](#2-branches)
- [3. Commits](#3-commits)
- [4. Pull requests](#4-pull-requests)
- [5. Merge, not rebase](#5-merge-not-rebase)
- [6. Never force push](#6-never-force-push)
- [7. Conflicts when syncing](#7-conflicts-when-syncing)
- [8. Several agents or people in one repository](#8-several-agents-or-people-in-one-repository)
- [9. Project README, and what goes where](#9-project-readme-and-what-goes-where)
- [Sources](#sources)

## 1. Purpose and the one rule

This file is for everyone who changes the repository: people and AI agents alike. Read it
before you branch, commit, merge, or push.

One rule holds the rest together: **history that has left your machine is never rewritten.**
Local commits are yours to reshape. Pushed commits are someone else's base.

The commands below assume git 2.35 or newer (`git --version`). `merge.conflictStyle=zdiff3`
in section 7 is the newest feature used here, and everything else works on older versions.

## 2. Branches

Name a branch `<type>/<KEY-123>-<short-name>`, or `<type>/<short-name>` when there is no
ticket.

- The type is one of six: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`. `chore` is the
  catch-all, and the list does not grow.
- The key is uppercase letters, a hyphen, and digits (`PROJ-520`), copied from the tracker.
  It is what links the branch to the ticket. Use a ticket when one exists, and never invent
  a key. Anything that is not a key in that shape uses the ticketless form.
- The short name is two to five lowercase ASCII words from the ticket title, joined with
  hyphens: `feat/PROJ-520-native-pdf-input`.
- One branch per change, cut from `main`.

Check: `git branch --show-current` prints a name that matches one of the two forms.

## 3. Commits

One logical change per commit. If you need the word "and" to describe two unrelated things,
it is two commits.

The message shape:

```
type [KEY-123]: what changed, in business terms

- What changed and why, in one self-contained sentence.
- A second one, if the change has a second thing worth saying.
```

Without a ticket, the title is `type(scope): what changed`.

- Title about 50 characters, imperative ("add", not "added"), no trailing period.
- Blank line, then the body: up to five bullets, each standing on its own, so a reader who has
  not seen the diff understands it. Put a short paragraph before the bullets when the change
  needs its reason told. No body at all when the title says everything.
- Wrap the body at about 72 characters.
- No file lists. `git show` already prints them.

The style is Conventional-Commits-like, not the specification. The `[KEY-123]` part is not in
that grammar, so a repository that lints commits with a Conventional Commits tool rejects it.
In such a repository, use the `type(scope):` form everywhere, and keep the ticket key in the
branch name and in the pull request.

Until the first push, the history is yours: amend, squash, reorder, and rebase as you like, so
what you push reads as a clean series. The rebase ban starts at the push, not before it. After
the first push, fixes from review are new commits. That is expected, not a violation.

Check: read the title alone. It tells a reader what changed, without the body.

Good and bad messages are in [commit-example.md](commit-example.md).

## 4. Pull requests

One ticket per pull request, and the base is `main`.

- The title uses the commit title form, without the 50-character limit.
- Sections, in this order: Summary, the ticket link, What's Changed, Verification. Add
  ⚠️ Breaking Changes, Notes, and Risks only when the change gives them something real to say.
- Summary says what, why, and the decisions or numbers a reviewer needs before opening a
  file, with the key terms in bold. It may carry a table for short facts that
  list well (renamed fields, before/after values), or one mermaid diagram when the change adds
  or reroutes a flow through several components. Never diagram a one-file change, and never
  add a second diagram.
- What's Changed is at feature level: one bold entry per feature on what it does, why it
  exists, and how it fits the existing flow. A reviewer should be able to
  predict the diff from it. Not a walk through the files.
- Verification has two lists: *Checked in this session*, the commands you ran and the result
  you saw, and *For the reviewer*, the steps left with their expected result, a negative check
  when the change has an error or permission path, and any gate you did not run. Only list a
  check you actually ran. An unrun check in the first list is a false claim.
- ⚠️ Breaking Changes names, for each item, what breaks, the blast radius, and the migration
  step. Notes holds decisions a reader would not guess, behavior changes outside the headline
  feature, and dependencies added, with their version; a contract change that breaks nothing
  gets a `> ⚠️ **Contract change:** …` blockquote there. Risks says what could regress and
  what tests do not cover.
- One ticket per pull request is also the size rule: unrelated cleanup goes in its own pull
  request, because review quality falls as the diff grows.
- Leave a section out when the change has nothing real to put in it. Verification is the
  exception: an empty one means the change is not ready for review.
- A pull request that shows conflicts is synced first (section 7), then reviewed.

Check: every section above is present, or absent because the change has nothing real to put
in it.

A complete pull request is in [pr-example.md](pr-example.md).

## 5. Merge, not rebase

The invariant: `main` changes only through a merged pull request. Nobody pushes to `main`
directly, a human lands the pull request, and an agent never merges its own.

**Sync.** Bring `main` into your branch with two commands:

1. `git fetch origin`
2. `git merge origin/main`

Not `git pull`. With `pull.rebase=true` or `branch.<name>.rebase=true` set, `git pull`
rebases your branch and does the opposite of this rule. The two commands do the same work and
cannot be turned into a rebase behind your back.

**Land.** Merge through the pull request, which creates a merge commit. Never fast-forward
`main` locally: if you merge `main` into your branch and then land it by hand, `main` becomes
the second parent of its own history and `--first-parent` stops meaning anything.

Why merge:

- One rule for all history. Nothing is rewritten, so nothing downstream breaks.
- Every commit keeps its SHA, so a link to it from a ticket or a review still resolves next
  year.
- Each conflict is resolved once, in the branch.
- A linear view is still available when you want one: `git log --first-parent`.

The cost, said plainly: the log holds more commits, and reverting a merge has a trap.
`git revert -m 1 <merge-sha>` on `main` undoes the change but leaves the branch recorded as
merged, so merging it again brings back nothing. To land that work later, revert the revert
first, then merge again.

Repository configuration:

- Merge method: merge commit only. Squash merging and rebase merging off.
- "Require linear history": off. It forbids merge commits.
- Require a pull request for `main`, and block direct pushes. Use a ruleset in a new
  repository, or branch protection where that is already set up.

A GitHub ruleset for `main` and the default branch, with the reason for each part, is in
[ruleset-example.md](ruleset-example.md).

Check: `git log --first-parent --no-merges main` lists only the commits made before the first
pull request was merged, usually just the initial commit. Anything else landed on `main`
outside a pull request.

## 6. Never force push

The rule is about effect, not about a flag: **any push that is not a fast-forward of the
remote branch is forbidden.** That covers `--force`, `--force-with-lease`, a `+` in the
refspec, deleting a branch and pushing it again, and GitHub's "Update with rebase" button,
which rewrites the branch it updates.

Why: pushed history is other people's base. Replace it and everyone who fetched it repairs
their own history by hand, while every link into the old commits goes dead.

You may hear that a force push loses the review comments. It does not: GitHub and GitLab keep
them and mark them outdated, so it is not an argument either way.

Enforcement: block force pushes on `main` and on every shared branch. On GitHub this is on by
default in branch protection and in rulesets. Leave it on. For `main` and the default branch,
[ruleset-example.md](ruleset-example.md) blocks force pushes. Other shared branches need a rule of
their own.

There is one exception path, and it is a human path:

1. A leaked secret is fixed by revoking and rotating it. Do that first and treat the leak as
   handled. A rewrite is cleanup, never removal: the old commits stay reachable on the hosting
   platform and in every clone that fetched them.
2. Stop. Describe the rewrite, what it touches and who is affected, then get explicit
   approval from a person.
3. A person does the rewrite and pushes with `--force-with-lease --force-if-includes`. If
   `main` is involved, they lift the protection and put it back afterwards.
4. Everyone else recovers with `git fetch`, then `git reset --hard origin/<branch>`. Not
   `git pull`, which would merge the old history back in. `git reset --hard` throws away every
   uncommitted change in that working tree, so run it only in a tree you own alone.

An agent never force-pushes, in any of those steps.

A wrong author on pushed history is left as it is and recorded in the ticket. `main` is never
rewritten for it. If the branch is not merged yet, it goes through the exception path above
like anything else.

Out of scope: stacked pull requests, and rebasing a fork branch before a project takes it.
Both rewrite pushed branches by design. Follow that project's policy there, and an agent
stops and asks instead of guessing.

Check: every push you make is accepted without a force flag. A push git rejects as
non-fast-forward means sync first (section 5, and section 7 if it conflicts). It never means
add a flag.

## 7. Conflicts when syncing

Merge `origin/main` into your branch early and often. A conflict is then fixed inside your
branch, by that merge. `main` is never touched.

1. Set the conflict style once, so you see the base and not only the two sides:
   `git config --global merge.conflictStyle zdiff3`. This is per-developer local config;
   nothing in the repository turns it on for you. It applies to conflicts that start after
   it. For a conflict already in the tree, `git checkout --conflict=zdiff3 -- <file>` rewrites
   that file's markers with the base, and it discards the edits you already made to it.
2. Read both sides and the base before you edit anything.
3. Resolve the file, then `git add <file>`.
4. Confirm that `git status` shows nothing unmerged.
5. Re-read the merged result as a diff, not only the hunks you touched.
6. Run the project's checks.
7. Commit the merge.

Tools for checking your own resolution:

- `git diff` during a merge shows the combined three-way diff.
- `git log --merge -p <path>` shows the commits from both sides that touched the file.
- `git show :1:<file>`, `:2:<file>`, `:3:<file>` print the base, our, and their version. A
  stage is missing when one side added or deleted the file.

Unsure? `git merge --abort` puts the tree back as it was before the merge, and that includes
throwing away uncommitted work that is not yours, so run it only in a working tree you own
alone. A conflict during `git revert` or `git cherry-pick` aborts with that command's own
`--abort`.

A clean merge is not a verified merge. Git finishing without a conflict marker means the two
sides did not overlap in text, not that the result is correct. The same holds for a
resolution an agent produced: a person reads it before it lands.

What an agent resolves, and what it hands back:

- Resolves: code and configuration, where both sides are mechanical.
- Hands back: prose, policy, and anything that records a decision, because someone chose
  those words. Generated files go back too: regenerate a lockfile instead of merging it.
- Handing back means a report naming which files conflicted and why the choice is not
  mechanical. In a working tree you own alone, `git merge --abort` first, so the tree is clean
  for whoever picks it up. In a shared working tree, leave the conflict in place: the abort
  throws away every uncommitted change in the tree, not only yours.

Check: before the merge commit, `git status` reports no unmerged paths, and the project's
checks have been run on the resolved tree.

## 8. Several agents or people in one repository

Agent work usually runs beside other work in the same repository, so treat concurrent changes
as the normal case.

- One branch per task.
- One working tree per active session. For a new branch, which is the usual case here:
  `git worktree add -b <branch> ../<name> origin/main`. For a branch that already exists:
  `git worktree add ../<name> <branch>`. Git refuses a branch that is already checked out in
  another tree, which is the guard you want. A working tree placed inside the repository
  directory goes into `.gitignore`. An agent that runs in a container gets its own clone
  instead, except in the one case [agent-containers.md](../docker/agent-containers.md) section 11
  names, because a linked worktree shares the repository's hooks and config with your host
  (section 7 there).
- In a shared working tree the index is shared too. Stage by explicit path, and never
  `git add -A` or `git add .`: they sweep up whatever anyone else left in the tree.
- Before committing, `git diff --cached --name-only` should list only your files. It reads the
  index, so it proves what is staged right now and nothing about the working tree.
- Commit your own work with explicit paths: `git commit -- <paths>`. That commits the
  working-tree content of those paths, so nothing may touch them between the check above and
  the commit. A merge commit is the exception, because git refuses pathnames during a merge:
  finish a merge with a plain `git commit`, after `git status` shows only what you expect.
- A staged file you did not stage means stop and say so. Never unstage someone else's work to
  clear your way.
- Author and committer come from the repository's configuration. An agent never sets or
  overrides them, through `user.*`, `--author`, or the `GIT_AUTHOR_*` variables.
- Landing is section 5: a human merges the pull request and owns the change.

Check: `git show --stat HEAD` after your commit lists only files you changed.

### Closing a working tree after its pull request

These steps are for a session that worked in a linked working tree and opened a pull request
from it. Work done in the main checkout needs none of them, and neither does an agent in a
container with its own clone, which goes away with the container.

The order matters because of one fact: `git worktree remove` refuses a tree with untracked or
changed files, but git-ignored files do not stop it, and it deletes them with the tree [1], [2].
Notes, plans and reports an agent keeps in an ignored folder are often their only copy, and
tools can remove the tree at merge time without asking: `gh pr merge --delete-branch` removes a
linked tree that has the merged branch checked out [3], and the Claude Code desktop app deletes
a session's untracked files when the session's pull request merges [4]. Anthropic's changelog
records fixes for lost gitignored output in its own worktree cleanup [5].

1. The agent in the tree commits and pushes its work and opens the pull request. Then it lists
   the ignored files worth keeping, with `git ls-files --others --ignored --exclude-standard`,
   and hands the list back instead of moving the files, because most agent sandboxes do not let
   a session write outside its own tree. Claude Code blocks writes to the main checkout from an
   isolated worktree session [6], Codex limits writes to its workspace by default [7], and
   Cursor's terminal sandbox does the same [8].
2. Before the merge, a person or a session in the main checkout copies the listed files to the
   place the project keeps such records. First list every file that already exists there with
   different content (`diff -rq <tree>/<folder> <folder>`), and stop and ask on any hit: a copy
   that skips existing files, such as `cp -n` or `rsync --ignore-existing`, drops the newer
   version without a word. Then copy without overwriting, and check that every listed file
   arrived.
3. A person merges the pull request (section 5).
4. In the main checkout, run `git fetch --prune origin`, then
   `git merge-base --is-ancestor <branch> origin/main`. Exit status 0 means the branch is in
   `main`. The check holds because section 5 lands with merge commits; after a squash or rebase
   merge it fails, since the branch's own commits never reach `main` [9].
5. Run `git worktree remove <path>`, never with `--force`. A refusal means the tree still holds
   untracked or changed files, and a locked tree means a session may still run in it [1]. Stop,
   show `git status` from the tree, and let its owner choose: commit the files, move them, or
   delete them. Jesse Vincent's skill for finishing a branch takes the same stance, because such
   files "exist nowhere else" [10]. If a tree was deleted by hand instead, `git worktree prune`
   removes what git still records about it [1].
6. Run `git branch -d <branch>` from the main checkout, on a `main` that has caught up with
   `origin/main` (`git merge --ff-only origin/main`; this only catches up with the remote and
   lands nothing). Git refuses to delete a branch that a tree has checked out, which is why the
   tree goes first. `-d` checks the branch against its upstream [11], and when the prune in step 4
   has removed that upstream it checks against `HEAD` instead [17], which is the up-to-date `main`.
7. Delete the remote branch. Turn on the platform's automatic deletion of the source branch:
   GitHub, GitLab and Bitbucket Cloud all leave it off until an admin turns it on [12], [13],
   [14]. Without it, the person who merged runs `git push origin --delete <branch>` [15]. This
   is not the "deleting a branch and pushing it again" that section 6 forbids: the branch is
   merged, and nobody pushes it again.
8. Move the work item on, as
   [jira-workflow.md](../project-management/jira-workflow.md) section 2 says.

Where the records live while the work runs is a choice, and no source settles it: git, GitHub and
the agent vendors say nothing about it, and no practitioner pattern has two independent sources.
The steps above take the first way below, because it works with every agent.

| Way | Gains | Costs |
|---|---|---|
| Inside the tree, rescued in step 2 (default) | Every agent can write there, the tree stays isolated, and the records sit next to the branch they describe. | Step 2 can be forgotten, or come after a tool already removed the tree; two copies of a file can drift apart. |
| Outside the tree from the start | Nothing to rescue, and no cleanup can reach the records. | Most sandboxes block it until a folder is added on purpose, which weakens the isolation; parallel sessions write into one folder. |

Take the second way only where the agent may write there by design: Aider sets no path limit on
its edits [16], and Codex takes an extra writable folder with `--add-dir` [7].

Check: before `git worktree remove`, every file on the list from step 1 has a copy in the main
checkout, or its owner said to drop it.

## 9. Project README, and what goes where

`README.md` is for people. It answers, in this order:

1. The name, then one line under 120 characters saying what the thing is.
2. What it does, and what it deliberately does not do.
3. Why it is useful.
4. Getting started: prerequisites, install, the first command, and the output it prints.
5. How the parts fit together, when a reader must know that before anything runs.
6. Project structure.
7. Where to get help.
8. Who maintains it, and whether pull requests are accepted.
9. License, last, by its full name.

Sections 5 and 6 are the two that rot. Add a diagram only when a reader has to know how the
parts talk before running anything, and let it show what runs, not what a change reroutes.
Generate the structure tree with `tree`, then cut it to the folders a newcomer opens: a tree
that lists every file is wrong at the next rename. The tree names folders, and a file only where
a newcomer opens that file itself; it is not the package map. When the repository has one
([file-structure.md](../file-structure/file-structure.md) section 10), the section links it for
what each kind of folder and file is for, and does not repeat it. Badges go under the title, and
only for a fact a reader acts on, such as build status or the supported version.

A navigation block opens the README, so a reader clicks a line and lands on that section: a
bold `**Navigation**` line, a blank line, then a plain list with one link per `##` heading, in
the order the headings appear, with the heading text as the link text. `###` headings get no
line. The block sits right after the first paragraph under the title, after the badges when
there are any, or right under the title when a `##` heading follows it directly. The link is the
anchor GitHub builds from the heading: lower case, each space becomes a hyphen, and every other
punctuation mark is dropped, so `## Getting started` links as `#getting-started` and
`## Why use it?` as `#why-use-it`. A heading with an emoji in it keeps characters that rule does
not predict, so copy its anchor from the link icon GitHub shows beside the heading. GitHub also
draws an outline from the headings, but only behind its Outline button. The block is in the
text, where every reader sees it at once, in a plain editor as much as on GitHub.

The block goes where it saves a reader the scroll, and nowhere else. Every `README.md` with two
or more `##` headings gets one, however short, a folder's `README.md` map as much as the project
README: a reader opens a README to find one thing. So does a long rules file or guide that a
reader opens to look up one section, such as this file, and a set of worked examples a reader
picks one case from. An example or a template gets none when its `##` headings are the sections
of the one document it shows, such as a pull request description; an example of a README is the
exception and keeps that README's own block. Neither does a doc read straight through as one
story, such as a before-and-after example, nor a short file a reader takes in at once, such as a
page of good and bad commit messages, nor a file whose `##` headings are too few to save a
scroll, however long. When unsure, ask whether a reader jumps to one section or reads from the
top: only the first gets a block. Add the block when you write such a file or when an edit makes
a file one, such as a rules file that gains its third section, and when you add, rename or
remove a `##` heading in a file that has one, change its line in the same edit.

Check: someone who has not seen the project clones it, follows only the README, and gets the
output the README promises. For the block: every `##` heading has exactly one line in it, and
every link lands on a heading. markdownlint's rule MD051 (`link-fragments`) fails on a link
whose heading is gone, so run it in CI wherever the repository lints Markdown. A heading added
without its line is caught only by a re-read of the diff.

A full example is in [readme-example.md](readme-example.md), with the reason behind each choice.

The agent-facing file (`CLAUDE.md` or `AGENTS.md`) is a different document for a different
reader. Read [claude-md.md](../../../claude-code/claude-md.md) when you write or edit one.

## Sources

Checked 2026-11-06 unless a line ends with — checked <YYYY-MM-DD>.

- [1] git — git-worktree, 2.56.0 — https://git-scm.com/docs/git-worktree
- [2] git — builtin/worktree.c, `check_clean_worktree` — https://github.com/git/git/blob/master/builtin/worktree.c
- [3] GitHub — GitHub CLI, `pkg/cmd/pr/merge/merge.go`, v2.103.3 — https://github.com/cli/cli/blob/v2.103.3/pkg/cmd/pr/merge/merge.go
- [4] Anthropic — Claude Code docs: Desktop — https://code.claude.com/docs/en/desktop
- [5] Anthropic — Claude Code changelog, entries 2.1.143 and 2.1.153 — https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
- [6] Anthropic — Claude Code docs: Worktrees — https://code.claude.com/docs/en/worktrees
- [7] OpenAI — Codex docs: Agent approvals and security — https://learn.chatgpt.com/docs/agent-approvals-security
- [8] Cursor — Cursor docs: Run modes — https://cursor.com/docs/agent/security/run-modes
- [9] GitHub — About pull request merges — https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges
- [10] Jesse Vincent — finishing-a-development-branch (superpowers v6.3.0, 2026; opinion) — https://github.com/obra/superpowers/blob/v6.3.0/skills/finishing-a-development-branch/SKILL.md
- [11] git — git-branch, 2.56.0 — https://git-scm.com/docs/git-branch
- [12] GitHub — Managing the automatic deletion of branches — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-the-automatic-deletion-of-branches
- [13] GitLab — Project settings: delete the source branch on merge by default, 19.5 — https://gitlab.com/gitlab-org/gitlab/-/blob/19-5-stable-ee/doc/user/project/settings/_index.md
- [14] Atlassian — Bitbucket Cloud: Branch a repository — https://support.atlassian.com/bitbucket-cloud/docs/branch-a-repository/
- [15] git — git-push, 2.55.0 — https://git-scm.com/docs/git-push
- [16] Aider — `aider/coders/base_coder.py`, `allowed_to_edit` — https://github.com/Aider-AI/aider/blob/main/aider/coders/base_coder.py
- [17] git — builtin/branch.c, `branch_merged` — https://github.com/git/git/blob/master/builtin/branch.c
