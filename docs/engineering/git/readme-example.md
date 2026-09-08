# README example

An ideal `README.md` for a fictional command-line tool, `docparse`. The sections and their
order come from [git.md](git.md) section 9. Everything below the line is the example.

---

# docparse

Turn PDFs, Word files, and scans into structured text and tables.

## What it does

`docparse` reads a document and returns its text, its tables, and its page structure as JSON.
It takes native PDFs, `.docx` files, and scans through OCR. Page numbers survive the whole
way, so an extracted table can be traced back to the page it came from.

## Why it is useful

Most extraction tools return one long block of text, and the page a number came from is gone.
That is fine for search and useless for anything a person has to check: an invoice total, a
figure in a report, a clause in a contract. `docparse` keeps the structure, so the answer and
its page travel together.

It runs offline. Documents never leave the machine, which is what makes it usable for
material that cannot go to a hosted service.

## How to start

Requires Python 3.11 or newer.

```
pip install docparse
docparse parse invoice.pdf --out invoice.json
```

The command prints the page count and writes the JSON next to your file. From Python:

```python
from docparse import parse

doc = parse("invoice.pdf")
print(doc.pages[0].tables)
```

Scans need an OCR engine on the machine. `docs/ocr.md` has the setup for each platform.

## Layout

- `src/docparse/` — the library. `parse.py` is the entry point.
- `src/docparse/backends/` — one module per input format.
- `tests/` — the test suite, with sample documents in `tests/fixtures/`.
- `docs/` — the JSON format reference and the OCR setup guide.

## Where to get help

- Usage questions: the Discussions tab of the repository.
- Bugs and feature requests: open an issue at https://github.com/your-org/docparse/issues.
  Include the document type, the command you ran, and the version from `docparse --version`.
- Security reports: security@example.com, not a public issue.

## Who maintains it

Maintained by the document platform team at `your-org`. Jane Doe <jane.doe@example.com>
reviews and lands changes. Read `CONTRIBUTING.md` before you open a pull request.

## License

MIT. See the `LICENSE` file in the repository root.

---

The example ends here. Every name in it is a placeholder: `docparse`, `your-org`, and Jane Doe
do not exist.
