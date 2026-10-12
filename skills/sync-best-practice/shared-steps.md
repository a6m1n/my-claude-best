The shared steps S0–S8, used by both `sync-best-practice` and `update-best-practice`: each skill
names the steps it runs, in its own order.

Commands outside a skill's `allowed-tools` prompt on purpose; design.md says why. These prompt:
every `git -C <tmp>/src.git …` command, every `git -c core.attributesFile=… diff …` command,
`rm -rf <tmp>`, each file change or undo of adopt and sync (`mkdir`, `cp`, `mv`, `rm`,
`git restore`, `git clean -fd`), and each Write or Edit outside `docs/adopted-practices/`, such as
a conflict resolution in the copy or `<tmp>/attributes` in S4. A record run prompts about eight
times. The `allowed-tools` grant ends when the user answers, so after any "ask" the next commands
may prompt again.

### S0 — Check a record before you use it

Read the record, `docs/adopted-practices/<name>.md`. Stop and report the cause when:

- the file is missing;
- its front matter lacks `source`, `source_path`, `synced_commit` or `local_path`, or one of
  them is empty;
- `synced_commit` is not 40 hex characters;
- `local_path` does not exist in this repo (Glob finds nothing at it or under it);
- `local_path`, after you drop a leading `./` and a trailing `/`, is empty or `.`, starts with
  `/` or `~`, has a `..` part, holds a character other than ASCII letters, digits, `.`, `_`, `-`
  and `/`, or has a part that starts with `-`: it must name a folder or file below the repo
  root, never the root itself, and every command that uses it must read it as one plain path.

Check: the record exists, and all four fields hold usable values.

### S1 — Clone the source

1. Make a temp folder: `mktemp -d`. Call it `<tmp>`: the absolute path it printed.
2. Check the source address before you clone it: the record's `source`, or the `source=` value
   of a new adopt. It must start with `https://`, `ssh://`, `git@` or `/` (a local path), never
   with `-`, and hold only ASCII letters, digits and `.`, `_`, `-`, `/`, `:`, `@`, `~`, `%`, `+`.
   An `https://` address must hold no `@`: a user name or token there would be written into the
   record, which is committed. When the address breaks any of these, stop and report it.
3. Clone the source into it: `git clone --quiet --bare -- <source> <tmp>/src.git`. Every word
   after `--` is a path, never an option.
   - Think: why a fresh clone? Someone's working copy can hold local edits or sit on an old
     branch, so it is not the source. A bare clone holds every branch and nothing else.
   - If the clone fails (network, access), stop and report the error. Never try a URL you made up.
4. Find the default branch: `git -C <tmp>/src.git symbolic-ref --short HEAD`.

Check: the clone exists, and you know the default branch.

### S2 — Check out the source at a commit

The checkout of a commit is `<tmp>/at-<sha7>`, where `<sha7>` is the first 7 characters of its
SHA. Every step uses that one name.

1. Unless this run already checked the commit, check that it exists in the clone:
   `git -C <tmp>/src.git cat-file -e <sha>^{commit}`. If that fails, stop with "base not in the
   source; re-anchor (/sync-best-practice adopt, Re-anchor path)".
2. If `<tmp>/at-<sha7>` already exists, an earlier step made it at the same commit: reuse it and
   go to item 4. Otherwise add a worktree of the clone at that commit:
   `git -C <tmp>/src.git worktree add --detach <tmp>/at-<sha7> <sha>`.
3. Think: a real checkout gives every file exactly as the source stores it, so every comparison
   below is against the source itself, not against a copy someone made.
4. Look for `<tmp>/at-<sha7>/<source_path>`. If it is missing, the practice was not at that path
   at that commit: stop and report.
5. Before adopt or sync copies or merges files from a commit (adopt step 3, sync step 2), check
   its tree. This item needs only the clone, not the checkout.
   - `git -C <tmp>/src.git ls-tree -r <sha> -- <source_path>`: stop and report when it prints
     no line (then `<source_path>` is not in that commit's tree, or a folder above it is a link
     that the checkout would read through), when a line has mode `120000` (a symbolic link) or
     `160000` (a submodule), when it prints a path in double quotes, or when a path holds a
     character other than ASCII letters, digits, `.`, `_`, `-` and `/`, or has a part that
     starts with `-`.
   - `git -C <tmp>/src.git grep -n -E '^(<<<<<<< local|\|\|\|\|\|\|\| base|>>>>>>> source)' <sha> -- <source_path>`:
     S8's pattern without its line end, because `git grep -E` does not read `\r`. A hit stops
     too, because the copy would then hold lines that S8 takes for an unfinished sync. Exit 1
     means no hit; any exit other than 0 or 1 is an error: stop and report it.
   - Think: a link makes a copy or a merge read or write wherever it points, outside the copy;
     any other character can split a command, run one (a backtick, `$`, `|`, `&`, `;`, `<`,
     `>`), or turn into an option.

### S3 — Is a commit on the default branch?

1. Run `git -C <tmp>/src.git merge-base --is-ancestor <sha> HEAD` and read its exit code: 0 means
   the commit is on the default branch, 1 means it is off it, and any other code is an error: stop
   and report it.
2. Think: a commit that only a feature branch holds disappears for every new clone once that
   branch is squash-merged or deleted. A base like that can be lost.
3. If not, find the branches that hold it: `git -C <tmp>/src.git branch --contains <sha>`. The
   mode decides what to do next.

### S4 — List the changed places of the copy

A place is one section of one file: `<file> § <heading>`.

1. Write the file `<tmp>/attributes` with one line: `*.md diff=markdown`. This turns on git's
   built-in markdown driver, which names each change by the heading above it.
2. Compare the source checkout with the copy:
   `git -c core.attributesFile=<tmp>/attributes diff --no-index -U0 --no-renames <tmp>/at-<sha7>/<source_path> <local_path>`.
   Read its exit code: 1 means the two sides differ, which is the normal result; 0 means no
   difference; any other code is an error: stop and report it.
3. Read each hunk header, the text after the second `@@`, and turn it into a place:
   - `@@ -12,2 +12,3 @@ ## 3. Commits` in `git.md` becomes `git.md § 3. Commits`: drop the `#`
     signs, keep the heading text as it is;
   - git cuts the heading in a hunk header near 80 bytes. When a heading looks cut, find the
     full heading line in the source checkout with Grep on its first words, and use the full
     text as the place;
   - nothing after the `@@` becomes `<file> § (top)`;
   - a file that exists on one side only (`new file` or `deleted file`) becomes `<file>`;
   - a file not ending in `.md`, and any `Binary files … differ` line, becomes the whole-file
     place `<file>`.
4. Think: the heading comes from the source side, so it names the section as the source has it.
   A `# comment` line inside a code block also looks like a heading to git; a change under one
   is named by that line, which is why such a file is better recorded as a whole file.
5. Check the driver, on `.md` files only: if a header shows a plain text line where a `#`
   heading should be, this git has no markdown driver, and places cannot be named. Stop and
   report it.

Result: the list of hunks, each with its place, its `+start,count` and its first changed line.

### S5 — The gate: every hunk against the decisions

1. Read the record's active decisions: the ones with no `Closed` line. Collect the places in
   their `Where` fields, each without its locator in round brackets; `Where: none` has none.
2. Build one row per S4 hunk: its place, its `+start,count`, and its first changed line. In each
   row, name every active decision whose Where names that place AND whose Ours explains some of
   the hunk's lines; a row may name several decisions, whose Ours together explain the hunk.
   When some of the hunk's lines no named decision explains, the hunk is **UNRECORDED**.
3. A whole-file Where (`<file>`) covers a file only when the file is added or deleted, is not
   markdown, or its headings are code comments.
4. Judge NO-CHANGE per decision. For each active decision X and each place in X's Where, look
   for a row in that place that names X (for a whole-file entry, any row in that file that
   names X). A place with no such row is **NO-CHANGE** for X: X's change no longer shows there.
5. Think: an UNRECORDED hunk is a change nobody can explain, and a sync would carry it forward
   without a reason. A NO-CHANGE place is a decision that may have run out there.

Check: the gate passes only with no UNRECORDED hunk and no NO-CHANGE place. Put the whole table
(one row per hunk: place, `+start,count`, first changed line, decisions or UNRECORDED; then every
NO-CHANGE place with its decision) into the report, so a reader can check the matching.

### S6 — Clean up

Delete the temp folder with everything in it: `rm -rf <tmp>`. Run it only when `<tmp>` is the
absolute path `mktemp -d` printed in S1 and `<tmp>/src.git` exists; otherwise do not delete it,
and say so in the report. Run S6 when the mode ends, also when it ends at a stop. Never run it
at an "ask" after which the mode goes on: the later steps still need the clone and its
checkouts. Name `<tmp>` in the report and in each message that asks, so that when the user never
comes back after an ask, the user or the next run can delete it.

### S7 — Resolve NO-CHANGE places

The calling step names the source text to compare with and gives the `<why>` for the lines below.
For each NO-CHANGE place from S5, read the decision's Ours against the copy and that text:

- Ours now sits under another place: S4 prints the same lines there. Rewrite the Where to that
  place.
- The copy matches the source text there again, the calling step's `<why>` holds, and the
  decision still has other changed places: propose to drop the place from its Where, with the
  line `- Changed <YYYY-MM-DD>: <place> matches the source again — <why>`.
- The same, but the decision has no changed place left: propose
  `- Closed <YYYY-MM-DD>: <why>`. Never delete the entry.
- Any other case: S7 cannot explain the place. The calling step says what that means.

Ask about every proposed drop and close in one message. For each place, quote the decision's Ours,
the copy's lines there and the source's lines there, so the user judges the text and not only
your verdict. Never drop a place or write a Closed line without the user's yes. When the user
declines one, keep the decision as it is and list it in the report as "NO-CHANGE, kept on your
answer". A decline is never a stop, and never a reason to run the gate again.

Check: the report names each NO-CHANGE place as renamed, dropped, closed, "NO-CHANGE, kept on
your answer", or handed back to the calling step.

### S8 — Check for an unfinished sync

Grep `<local_path>` for the conflict markers that sync step 5 writes, pattern
`^(<<<<<<< local|\|\|\|\|\|\|\| base|>>>>>>> source)\r?$` (the labels it gives `git merge-file`).
A marker line counts only when `git diff HEAD -U0 -- <local_path>` shows it as an added line, or
when it sits in a file that `git status --porcelain --untracked-files=all -- <local_path>` lists
as `??` (sync's R row leaves a half-merged file under a new, untracked name): committed marker
lines are text the copy holds, not an unfinished sync. A hit that counts means an earlier sync
did not finish: the calling step stops with "an earlier sync did not finish: run the undo block
of /sync-best-practice sync step 8, or finish it".
