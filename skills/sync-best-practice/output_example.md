Every value below is invented: repo names, commits, files, decisions. The examples show the
shape of the report for each mode and of a new record, never real content.

# adopt

The report:

```markdown
**Result** — adopt · testing · adopted from acme/practices at 4f2a9c1

**Source** — https://github.com/acme/practices · docs/engineering/python/testing · base 4f2a9c1,
on the default branch `main`

**Checks**
- `git symbolic-ref -q HEAD` → refs/heads/feat/adopt-testing
- `git status --porcelain -- docs/engineering/python/testing docs/adopted-practices/` → empty
- `git clone --bare https://github.com/acme/practices` → default branch `main`
- `git merge-base --is-ancestor 4f2a9c1 HEAD` → exit 0, on the default branch
- tree check (S2 item 5) on 4f2a9c1: `ls-tree` → 4 regular files, every name safe; `git grep`
  for the marker lines → exit 1, none
- copied 4 files from the checkout at 4f2a9c1; S4 diff against it → no place changed
- gate (S5): no changed place, no decision → passes
- temp folder `/tmp/tmp.Q4mZ7r` → deleted (S6)

**Changes** — copied 4 files into docs/engineering/python/testing/; created
docs/adopted-practices/testing.md

**Decisions** — none

**Needs your answer**
- Add the trigger line to CLAUDE.md? Options: yes (recommended: without it nothing reminds the
  agent to record a decision when it edits the copy) · no.

**Next step** — commit the copy and the record together, before any local change, for example
`docs(adopt-testing): Adopt the testing practice from acme/practices 4f2a9c1`.
```

The record it created, `docs/adopted-practices/testing.md`:

```markdown
---
source: https://github.com/acme/practices
source_path: docs/engineering/python/testing
synced_commit: 4f2a9c1e7b3d5a6f8c9e0d1b2a3c4e5f6a7b8c9d
local_path: docs/engineering/python/testing
---

# testing: adopted practice

The testing practice from acme/practices: which code earns a test and how a pytest suite is laid
out. The copy follows the source except for the decisions below. sync-best-practice and
update-best-practice keep this record.

## Decisions

none
```

# status

```markdown
**Result** — status · git · behind 3 commits; 1 change has no decision

**Source** — https://github.com/acme/practices · docs/engineering/any-language/git · base
9d81e07, NOT on the default branch: only `docs/new-examples` holds it. If that branch is
squash-merged and deleted, the base is lost; re-anchor it after the branch merges.

**Checks**
- `git cat-file -e 9d81e07^{commit}` → exists
- `git merge-base --is-ancestor 9d81e07 HEAD` → exit 1; `git branch --contains 9d81e07` →
  docs/new-examples
- `git log --oneline 9d81e07..HEAD -- docs/engineering/any-language/git` → 3 commits:
  b71c2e0 explain the merge-commit trap · 0e5d9a4 add a section on tags · 6c3f118 fix a link
- S4 diff against the checkout at 9d81e07 → 7 hunks in 6 places
- gate (S5):

  | Place | Lines | First changed line | Decision |
  |---|---|---|---|
  | git.md § 2. Branches | +31,2 | `<type>/<feature>`, for example `docs/add-tags` | D1 |
  | git.md § 3. Commits | +48,1 | `type(<feature>): <title>` | D1 |
  | git.md § 3. Commits | +55,3 | Keep the whole title under 72 characters. | D4 |
  | git.md § 5. Merge, not rebase | +102,4 | Merge `main` into your branch; never rebase it. | D3 |
  | git.md § 7. Conflicts when syncing | +140,2 | Ask the team lead before you resolve a conflict. | UNRECORDED |
  | README.md § Git practices | +9,1 | Name the feature, not a ticket. | D1 |
  | merging.md | whole file, added here | — | D5 |

  NO-CHANGE: none. Result: fails (1 UNRECORDED).
- temp folder `/tmp/tmp.Xk2v9a` → deleted (S6)

**Changes** — none (status changes no file)

**Decisions** — D1, D3, D4, D5 matched; git.md § 7 has a change with no decision

**Needs your answer**
- The change in git.md § 7 has no decision. Options: record it with `/update-best-practice`
  (recommended: a sync cannot keep a change it cannot explain) · undo it.

**Next step** — record the § 7 change, then run `/sync-best-practice sync git`.
```

# sync

```markdown
**Result** — sync · git · synced 9d81e07..b71c2e0

**Source** — https://github.com/acme/practices · docs/engineering/any-language/git · base
9d81e07 on `main` · target b71c2e0 on `main`

**Checks**
- `git symbolic-ref -q HEAD` → refs/heads/docs/sync-git-practice (not the default branch)
- `git status --porcelain --untracked-files=all -- <copy> <record>` → empty
- `git ls-files -s -- <copy>` → 4 files, no link
- `git merge-base --is-ancestor 9d81e07 b71c2e0` → exit 0, the target is newer
- tree check (S2 item 5) on 9d81e07 and b71c2e0: `ls-tree` → regular files only, every name
  safe; `git grep` for the marker lines → exit 1, none
- gate before the merge (S4 against 9d81e07, S5):

  | Place | Lines | First changed line | Decision |
  |---|---|---|---|
  | git.md § 2. Branches | +31,2 | `<type>/<feature>`, for example `docs/add-tags` | D1 |
  | git.md § 3. Commits | +48,1 | `type(<feature>): <title>` | D1 |
  | git.md § 3. Commits | +55,3 | Keep the whole title under 72 characters. | D4 |
  | git.md § 5. Merge, not rebase | +102,4 | Merge `main` into your branch; never rebase it. | D3 |
  | git.md § 6. Tags | +130,1 | Tag only from `main`. | D2 |
  | README.md § Git practices | +9,1 | Name the feature, not a ticket. | D1 |

  NO-CHANGE: none. Result: passes.
- source diff 9d81e07..b71c2e0 read in full: 3 commits, 3 files; a 4-line paragraph left
  git.md § 5 and reappears in merging.md (found with Grep); D3 names git.md § 5 → asked
- source change shown before the merge: 31 added or changed lines, 4 removed lines and
  merging.md in full; one passage tells an agent what to do (git.md § 6, "rebase before you open
  a pull request"); merge approved
- `git diff --name-status -M 9d81e07 b71c2e0` → M git.md, M README.md, A merging.md
- `git merge-file` git.md → exit 2, conflicts in § 3 and § 5; README.md → exit 0; merging.md
  copied
- Grep for conflict markers after resolving → none
- gate with the new base (S4 against b71c2e0, S5):

  | Place | Lines | First changed line | Decision |
  |---|---|---|---|
  | git.md § 2. Branches | +31,2 | `<type>/<feature>`, for example `docs/add-tags` | D1 |
  | git.md § 3. Commits | +48,1 | `type(<feature>): <title>` | D1 |
  | git.md § 3. Commits | +57,3 | Keep the whole title under 72 characters. | D4 |
  | merging.md § Merge, not rebase | +12,4 | Merge `main` into your branch; never rebase it. | D3 |
  | README.md § Git practices | +9,1 | Name the feature, not a ticket. | D1 |

  NO-CHANGE: D2 at git.md § 6. Tags, closed on your yes. Result: passes.
- temp folder `/tmp/tmp.Rw5n2c` → deleted (S6)

**Changes**
- git.md — merged; 2 conflicts, in § 3. Commits and § 5. Merge, not rebase, resolved (see
  Decisions)
- README.md — merged
- merging.md — added by the source

**Decisions**
- D1 kept: the source's change in § 2 sits outside D1's lines
- D2 closed on your yes: the target's text equals its Ours, so the Closed line says "the source
  does the same since b71c2e0"
- D3 conflict in git.md § 5 resolved: the paragraph left git.md as the source moved it, and on
  your answer our wording replaced the source's in merging.md, so D3's Where now names
  merging.md § Merge, not rebase
- D4 conflict in git.md § 3 resolved: kept our 72-character title limit, took the source's new
  example around it; Source line updated ("titles of about 50 characters" → "titles of about 50
  characters, with one example per type")

**Needs your answer** — none

**Next step** — commit the merged copy and the record in one commit:
`docs(sync-git-practice): Sync the git practice with acme/practices 9d81e07..b71c2e0`.
```
