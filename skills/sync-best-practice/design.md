Why `sync-best-practice` and `update-best-practice` are built this way: each option that was
weighed and turned down, and why the chosen one wins. Change a line here when its reason changes.

- **The base kept inside this repo**, as a pristine commit on a branch here: it needs commits
  and branches in this repo, which the skills never make. The record
  keeps the source's commit SHA instead, and a fresh clone gives the base back.
- **git subtree or git-subrepo:** both bring the source in through commits in this repo, and the
  skills never commit.
- **Copier or cruft:** an extra tool to install in every repo, while these skills use git alone.
- **A patch queue** (one patch per local change, replayed on each new source): a patch stops
  where the source changed the lines around it, and its reason lives apart from the text. A
  three-way merge needs only the recorded base, and the decision carries the reason.
- **`git apply -3`:** it implies `--index`, so it writes to this repo's index, and its three-way
  step needs the base blobs in this repo's object store. The base lives only in the temp clone.
- **`git merge-tree`:** with `--merge-base` it can merge trees, but a per-file `git merge-file`
  lets each conflict go to the user next to the decision it touches, and it works on the git
  version these skills already need (2.39).
- The record's path and the options weighed against it: record-format.md § Where it lives.
- **One skill instead of two:** frontmatter is per skill. Recording must be invocable by the
  model right after it edits a copy, and sync must be manual-only; one skill cannot be both.
- **`status` in the model-invocable skill:** status is a report the user asks for. It checks each
  record against its source's newest commit and answers "is my copy behind, does it drift?",
  which nothing needs between edits. Record mode also clones, but only to name the places of the
  edit just made. Status stays in the manual-only skill.
- **Record mode without a clone:** naming a place needs the source's headings, which this repo
  does not keep, so record mode clones the source on every run; offline it stops and never
  guesses. Two ways around the clone were turned down: reading the base from this repo's adopt
  commit (the copy changes after adopt, so it is not the source), and storing the source's
  headings in the record (a copy of what the source holds).
- **Record mode after a sync or a re-anchor:** (A) trust the sync's report in this
  conversation: it cannot see an edit made after the report, or a sync from another session;
  (B) no exit: record mode asks again about every hunk the sync merged; (C, chosen) run the gate
  at the new base and record the UNRECORDED hunks that this change's edits overlap; older ones
  get the backfill pointer: one clone, about eight prompts. The sync's report is read only to
  skip asking again about a place the user just kept; the gate still runs. A dated "Kept" line
  that later runs skip was put off: it adds a line type and a gate rule, and a decline in another
  session only costs one more question.
- **Gating or syncing what is not in git:** a practice that is not in git has no source commit
  to diff or merge against; its overrides are recorded as `Where: none` decisions
  (update-best-practice, Which files belong).
- **A place-only gate**, which passes a hunk when a decision's Where names its place: it passes
  any edit in a place a decision already names. A text match of each hunk against Ours breaks on
  every rewording. The gate judges whether a decision's Ours explains each hunk, and the full
  table in the report is the check on that judgment.
- **Read and Grep instead of `git -C …` commands on the checkouts, and wider `allowed-tools`
  grants:** Read and Grep cannot list hunks, check ancestry or add worktrees. A grant with a `*`
  before the git subcommand, such as one for `git -C`, also approves options such as `-c`, which
  make git run a program. A `git restore` grant would also match `-- .` and discard every
  uncommitted change in the repo. A broad file-change or delete grant (`mkdir`, `cp`, `mv`, `rm`,
  `git clean -fd`, `rm -rf`) in a skill is a risk. So these commands stay unapproved and prompt.
- **Trusting the source's text:** the gate compares the copy with the
  source, so it never sees text the source brings in, and a copied practice can be a file agents
  load as instructions. Turned down: trusting a clean merge, because nobody reads it; narrowing
  the `git diff` and `git log` grants by prefix, because a `*` matches options anywhere, so
  `--output` still matches, and dropping the grants adds a prompt to every read. Chosen: sync
  step 4 shows the incoming change and merges only on a yes; source text is data, never an
  instruction; Edit is granted only under `docs/adopted-practices/`, so any other write prompts
  with its diff; S2 item 5 checks the base and target trees before sync step 4 (links,
  submodules, any file name outside a safe character set, the skill's own marker lines), sync
  step 1 refuses a link in the copy, and S8 counts only uncommitted markers with the skill's own
  labels. The prompts guard only in Manual mode; in acceptEdits or auto mode the step-4 ask and
  the tree checks are what remains.
- **An allow-list of source hosts:** turned down. The user names the
  source at adopt, S1 item 2 checks its form, and sync step 4 shows every incoming line whatever
  the host. A fixed host list would break each repo that copies from another host.
- **A guard against heading renames:** not added. A source rename of a
  heading that a Where names moves the decision's place. Sync step 4 lists each such heading in
  the report, and S7 rewrites the Where when Ours shows under the new name.
