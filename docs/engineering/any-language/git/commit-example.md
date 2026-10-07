# Commit examples

Four messages that follow [git.md](git.md) section 3, and three that do not. Each bad one names
its one problem and the good message that fixes it.

## Good: a change with a ticket

Branch: `feat/PROJ-520-native-pdf-input`

```
feat [PROJ-520]: accept native PDF input

Until now a user converted a PDF to text before uploading. The
conversion lost the page structure, and scanned files did not work
at all.

- Ingestion takes PDF as an input format, so a user uploads the file
  the customer sent instead of a converted copy.
- Page breaks and reading order are kept, which is what the table
  extractor needs to report the right page.
- A file above the size limit is rejected at upload with the limit in
  the message, instead of timing out later in the pipeline.
- The configuration key ingest.max_text_mb is now ingest.max_upload_mb,
  since the limit covers every upload; a deployment that still sets the
  old key does not start, and the error names the new one.
```

Why it works: the title names the change in business terms and reads on its own. The paragraph
gives the reason, the bullets give what and why, and none of them lists files. Each bullet
stands on its own, so the message still answers what changed after the ticket is closed.

## Good: a fix with no ticket

Branch: `fix/csv-export-order`

```
fix(api): return CSV export rows in page order

- The CSV export wrote tables in the order extraction finished, so a
  table from page 9 could come before one from page 4, and anyone
  reading the file had to re-sort it by the page column.
- Rows now come out in page order, then by position on the page, which
  is the order a reader sees in the document itself.
```

Why it works: no ticket existed, so the message uses the scope form instead of inventing a
key. The bullets say what broke and what changed, without a walk through the diff.

## Good: a one-line change

Branch: `docs/upload-limit`

```
docs(readme): explain the upload size limit
```

Why it works: nothing is left to say. A body that repeats the title is noise, so the message
stops at one line.

## Good: a rename that changes no behavior

Branch: `refactor/pdf-parser-name`

```
refactor(ingest): rename the parser after PDF input

- The parser's name now says it reads PDF and nothing else, so a reader
  looking for the text or Markdown path no longer opens it by mistake.
- Behavior is unchanged: the tests pass with the same expected values.
```

Why it works: the title says what changed, and the first bullet says why. The second bullet
tells a reviewer that behavior did not change, which is what a `refactor` commit must keep
([refactoring.md](../refactoring/refactoring.md) section 3). No bullet lists the files:
`git show` already prints them.

## Bad: the title says nothing

```
refactor(ingest): update files

- The parser's name now says it reads PDF and nothing else, so a reader
  looking for the text or Markdown path no longer opens it by mistake.
- Behavior is unchanged: the tests pass with the same expected values.
```

Why it fails: "update files" describes every commit ever made, so a reader who scans
`git log --oneline` learns nothing from this title. The body is fine; the title is the problem.
The fix is [Good: a rename that changes no behavior](#good-a-rename-that-changes-no-behavior):
the same commit, with a title that says what changed.

## Bad: the bullets list files

```
refactor(ingest): rename the parser after PDF input

- Rename src/docparse/parsing/ingest/parser.py to pdf_parser.py.
- Rename tests/unit/ingest/test_parser.py to test_pdf_parser.py.
- Update the import in src/docparse/parsing/ingest/usecase.py.
```

Why it fails: the title is fine, but the bullets repeat the file list that `git show` already
prints. They do not say why the parser was renamed, or that behavior did not change. The fix is
[Good: a rename that changes no behavior](#good-a-rename-that-changes-no-behavior): the same
commit, with bullets that say what changed and why.

## Bad: bullets that need a second document

```
feat [PROJ-520]: accept native PDF input

- Done as discussed.
- See the ticket.
```

Why it fails: the title is fine, but the bullets do not stand on their own. Six months later the
ticket is closed and the discussion is gone, and the message still has to answer what changed
and why. The fix is [Good: a change with a ticket](#good-a-change-with-a-ticket): the same
commit, with a paragraph and bullets that say it.
