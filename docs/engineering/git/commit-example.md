# Commit examples

Three messages that follow [git.md](git.md) section 3, and two that do not.

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
```

Why it works: the title names the change in business terms and reads on its own. The paragraph
gives the reason, the bullets give what and why, and none of them names a file.

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
docs: explain the upload size limit in the README
```

Why it works: nothing is left to say. A body that repeats the title is noise, so the message
stops at one line.

## Bad: the title says nothing and the bullets list files

```
update files

- rename parser.py to pdf_parser.py
- rename tests/test_parser.py to tests/test_pdf_parser.py
- update imports in loader.py
```

Why it fails: "update files" describes every commit ever made, and the bullets repeat the file
list that `git show` already prints. What changed for a user, and why, is missing.

## Bad: bullets that need a second document

```
fix [PROJ-520]: fix the thing

- fixed as discussed
- see the ticket
```

Why it fails: nothing here stands on its own. Six months later the ticket is closed and the
discussion is gone, and the message still has to answer what changed.
