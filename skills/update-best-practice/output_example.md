Every value below is invented: repo names, commits, files, decisions, reasons. The examples show
the shape of the decisions and the report for each mode, never real content.

# record

The user changed the testing practice: "we run integration tests only in CI, not on every
commit". The copy is `docs/engineering/python/testing`.

The decision added to `docs/adopted-practices/testing.md`:

```markdown
### D3 · 2026-11-04 · Integration tests run only in CI

- Source: run the whole suite, integration tests included, before every commit.
- Ours: run unit tests before a commit; integration tests run only in CI.
- Why: integration tests here need the staging database, which developer machines cannot reach
  (the user, 2026-11-04).
- Where: testing.md § Running the suite; testing.md § Integration tests
- Also: CLAUDE.md
```

The report:

```markdown
**Result** — added D3; updated none; closed none

**Decisions**
- D3 · Integration tests run only in CI · added · Where: testing.md § Running the suite;
  testing.md § Integration tests

**Checks**
- `git status --porcelain --untracked-files=all -- docs/engineering/python/testing` → M
  testing.md
- `git status --porcelain -- CLAUDE.md` (a file outside the copy, tied to the practice) →
  M CLAUDE.md: part of the same change, so D3 lists it under Also
- `git diff HEAD -U0 --no-renames -- docs/engineering/python/testing` → 2 hunks in testing.md:
  +14,2 and +40,3
- S1 (`git clone --bare https://github.com/acme/practices`), S2 at 4f2a9c1, S4 → the two hunks
  overlap testing.md § Running the suite and testing.md § Integration tests
- gate (S5):

  | Place | Lines | First changed line | Decision |
  |---|---|---|---|
  | testing.md § Running the suite | +14,2 | Run the unit tests before a commit. | D3 |
  | testing.md § Integration tests | +40,3 | Integration tests run only in CI. | D3 |
  | testing.md § Fixtures | +71,1 | Build test data with the factory in `tests/factories.py`. | D1 |

  NO-CHANGE: none. Result: passes.
- temp folder `/tmp/tmp.H7c4Tb` → deleted (S6)

**Needs your answer** — none

**Next step** — commit the change to testing.md, CLAUDE.md and the record in one commit.
```

# backfill

The git practice was copied by hand a month ago and edited since; adopt found the base and
listed two unrecorded places.

The report at the end of the run, after the user answered the ask of step 3: the user confirmed
the proposed reason for git.md § 2. Branches and gave no reason for README.md § (top).

```markdown
**Result** — added D1; updated none; closed none

**Decisions**
- D1 · Branch names carry the Jira key · added · Where: git.md § 2. Branches

**Checks**
- shared steps S1, S3, S2 at `synced_commit`, S4, S5 → 2 hunks UNRECORDED: git.md § 2. Branches
  and README.md § (top)
- `git log --format='%h %cs %s' -- docs/engineering/any-language/git/git.md` → 3c9e1a2
  2026-10-01 "docs: Name branches after the Jira key"
- gate (S5), run again after D1 (step 4):

  | Place | Lines | First changed line | Decision |
  |---|---|---|---|
  | git.md § 2. Branches | +29,1 | `<type>/<JIRA-KEY>-<name>` | D1 |
  | README.md § (top) | +3,1 | The git rules of the Payments team. | UNRECORDED |

  NO-CHANGE: none. Result: fails (1 UNRECORDED).
- temp folder `/tmp/tmp.Lp3w8d` → deleted (S6)

**Needs your answer**
1. README.md § (top) — UNRECORDED: the intro line names our team, and you gave no reason. It
   needs a reason or an undo before the commit.

**Next step** — give README.md § (top) a reason or undo it; then commit the record, with the undo
if any, in one commit, and run `/sync-best-practice status git`.
```
