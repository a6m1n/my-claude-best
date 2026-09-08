# Pull request example

One complete pull request for the branch `feat/PROJ-520-native-pdf-input`, written to
[git.md](git.md) section 4. It carries the same change as the first message in
[commit-example.md](commit-example.md).

## Title

```
feat [PROJ-520]: accept native PDF input for document ingestion
```

Without a ticket the same title is `feat(ingest): accept native PDF input`.

## Description

Everything below is the pull request body.

---

### Summary

`docparse` accepts PDF files directly. Until now a user had to convert a PDF to text before
uploading, which lost the page structure and made scanned documents unusable. The conversion
step is gone from the flow, and the extracted tables now carry the page they came from.

### Ticket

PROJ-520 — https://tracker.example.com/browse/PROJ-520

### What changed

- PDF is an input format everywhere a user meets ingestion: the upload form, the command
  line, and the API.
- Page breaks and reading order survive ingestion, so an extracted table reports the page a
  reader can open.
- A file above the upload limit is rejected at upload, with the limit in the message. It used
  to fail several minutes later, after the pipeline had already written partial output.

### Verification

Checked here:

- The full test suite passes locally, including the new ingestion cases.
- A 12-page text PDF: 12 pages ingested, numbered 1 to 12, the tables on pages 4 and 9
  extracted with the right page number.
- A scanned PDF with no text layer: ingested with empty page bodies, page count intact, no
  error.
- Negative check: a file above the limit is rejected at upload with the limit named in the
  message, and nothing is written to storage.

For the reviewer:

- The limit is read from configuration. Please confirm the staging value is the one support
  tells customers.
- The upload form was checked in one browser only. In a second browser, the same 12-page PDF
  should upload and report 12 pages.

### Breaking changes

The configuration key `ingest.max_upload_mb` replaces `ingest.max_text_mb`.

- Blast radius: any deployment that sets the old key. The old key is now ignored, so the
  limit silently falls back to the default instead of failing loudly.
- Migration: rename the key in your configuration before you deploy this. The value carries
  over unchanged.
- The startup log warns once when the old key is still present.

---

Which sections may be left out is the rule in [git.md](git.md) section 4. Most changes break
nothing, which is why most pull requests carry no Breaking changes section.
