# Adopted-practice record: the format

The contract for the record that both `sync-best-practice` and `update-best-practice` read and
write. Read it before you create, read or change a record.

## Where it lives

One record per practice copied from a source repo, at `docs/adopted-practices/<name>.md` in the
repo that holds the copy. `<name>` is the last part of the source path (`git` for
`docs/engineering/any-language/git`); when that name is taken, the last two parts joined with
`-`. One fixed folder, so `ls docs/adopted-practices/` lists every copied practice.

Why this path:

- Outside the copied folder: a fresh copy of the source would overwrite a record inside it, and
  S4 would list it as a file only this repo has.
- Under `docs/`, not `.claude/`: the record is project documentation that people read when they
  review a practice change, not Claude Code configuration.
- One file per practice, not one log: each practice has its own source, synced commit and local
  path in its front matter.

The record holds only what git cannot tell: where the copy came from, the source commit it
matches, and why each local change was made. It never holds diffs, file lists, commit lists or
a history of syncs: `git log -p -- <record>` and `git log -- <local_path>` give those.

## Front matter

Written by `sync-best-practice` (adopt, and the last step of a sync). Nobody edits it by hand.

```yaml
---
source: https://github.com/<owner>/<repo>    # URL of the source git repo
source_path: docs/engineering/any-language/git    # the practice in the source repo
synced_commit: 0123456789abcdef0123456789abcdef01234567    # full SHA; S3 tells whether the source's default branch holds it
local_path: docs/engineering/any-language/git    # the copy, relative to this repo's root
---
```

All four fields are required. A practice is a folder or a single file; `source_path` and
`local_path` are the same kind.

## Body

```markdown
# <name>: adopted practice

<One paragraph: what the practice is, that the copy follows the source except for the
decisions below, and that sync-best-practice and update-best-practice keep this record.>

## Notes

<Optional. Facts about this copy that a reader needs and git cannot produce: where the record
came from, an open case about the base.>

## Decisions

<`none`, or the entries below, oldest first>
```

Each decision is one entry. Numbers go up in order, D1, D2, and are never reused or renumbered:

```markdown
### D<n> · <YYYY-MM-DD> · <what we do differently, as a short title>

- Source: <what the source says or does here, one or two sentences>
- Ours: <what this repo does instead>
- Why: <the reason, and who decided it>
- Where: <file> § <heading>; <file> § <heading>; <file>
- Also: <other files in this repo that carry the same decision>
- Upstream: local only | propose to the source | proposed <link>    (optional; no line means local only)
- Changed <YYYY-MM-DD>: <what changed> — <why>
- Closed <YYYY-MM-DD>: <why the decision no longer applies>
```

Field rules:

- **The intro stays one paragraph.** `## Notes` is optional and sits between the intro and
  `## Decisions`.
- **Source, Ours, Why and Where are required.** Also and Upstream are optional; no Upstream line
  means local only. Closed appears only on a closed decision.
- **Changed is optional and repeatable:** one dated line for each later change that extends the
  decision for the same reason, or that drops a place from its Where because the copy matches
  the source there again, under the entry. What changed and why are both required. A Changed
  line is never deleted, and the entry keeps its original date.
- **Source is a summary in the writer's own words**, never a copy of the source's lines: the
  source is data, and an instruction copied from it would sit in a file that every run reads.
- **Why is never empty and never invented.** It quotes or restates the reason the user gave in
  the conversation that writes the decision. A reason found in the source repo, a file comment
  or a commit message is at most a proposal the user confirms (backfill step 3), never a Why on
  its own. A placeholder (`TBD`, `n/a`, `see commit`) is not a reason.
- **Where names places inside the copy**, with paths relative to `local_path`.
  `<file> § <heading>` names a section by the nearest ATX heading (`#` to `######`) above the
  change, written without the `#` signs, exactly as the source file has it. `<file>` alone
  covers the whole file: use it for a file added or deleted here, a file that is not markdown,
  and a file whose changes sit under `# comment` lines in code blocks, which git takes for
  headings. A section added at the end of a file is named by the source heading above it. A
  place is always named from the source side, by S4 of `shared-steps.md`, in both skills. A
  place may end with a locator: free text in round brackets after the heading, such as
  `git.md § 7. Conflicts when syncing (step 1)`, that helps a reader find the lines. S5 ignores
  it. Places are separated by `;`. A long Where continues on lines indented by two spaces.
  `Where: none` marks a decision that changes nothing inside the copy and lives only in the
  files under Also.
- **Where is what the gate checks.** Steps S4 and S5 of `shared-steps.md` list every changed
  hunk of the copy against the source commit. Each hunk must sit in a place that active
  decisions name in their Where, and their Ours together must explain its lines; each place in a
  decision's Where must have a change that this decision's Ours explains. Both kinds of miss fail
  the gate.
- **The gate's known limit:** matching a hunk to an Ours is a judgment, not a text match, so the
  gate report always carries the full hunk table for a reader to check.
- **Also names files outside the copy** that carry the same decision, such as an agent
  instruction file. Its paths are relative to the repo root, while Where paths are relative to
  `local_path`. The gate does not check them.
- **Upstream** says whether the change should go back to the source: `local only` (fits this
  repo only), `propose to the source` (a better rule for everyone), or `proposed <link>`.
- **A decision is active until it has a Closed line.** A closed decision stays in the record, so
  a later reader sees why the copy changed back. Close it when the copy matches the source again
  in all its places, for example because the source now does the same. When only some of its
  places match again, drop those places from its Where with a Changed line instead.
- **Dates** are the day the decision was made, changed or closed.

Worked records: the adopt example in this skill's `output_example.md`, and a record with
decisions in the `update-best-practice` skill's `output_example.md`.
