Every value in this file is invented — the app, the files, the line numbers, the user's words,
the skill names and the skills' outcomes. It shows the shape of the output contract in `SKILL.md`, not a real run,
and not the only allowed answers: a real assessment has as many gaps, questions and steps as
the task has, within the contract's bounds.

# Worked example — one run, the default case (one recommended route)

The ask (invented): "Accounting wants the monthly reports as CSV and PDF files. Can we add
export? They need it by the 30th." · repo `ledgerly` · the conversation also settled that
reports must never leave our own servers · the main session offered meta-thinking, and the user
then typed `/meta-thinking`.

What the conversation showed before the assessment:

    [meta-thinking] gate: run — signals a (who receives the files is unclear), c (a new public URL shape)

---

## 1. Frame

- Goal: an accountant can get any monthly report as a CSV file and as a PDF file.
- Decide now: how the files reach accounting (download or email); the CSV column format.
- Not deciding: other report types; scheduling beyond the monthly run.
- Given:
  - MUST keep report data on our own servers — user, this conversation.
  - MUST be live by the 30th — user, first message.
  - NEVER change the report numbers themselves; export only — user, this conversation.

## 2. Known and assumed

- Known: reports are built in `src/reports/build.py:41` (`build_monthly()`), returned as
  rows of dicts — read.
- Known: the reports page has no download route yet; routes live in `src/web/routes.py` — read.
- Known: no PDF library is installed (`pyproject.toml`, dependencies) — read.
- Assumed: accounting opens CSV in Excel · wrong if: they import it into another tool that
  needs a fixed column order.
- Assumed: one PDF per report, A4, no charts · wrong if: the reports page charts must appear.
- Gaps: goal and done — clear · scope edge — clear · inputs and interfaces — gap (delivery
  channel) · constraints — clear · how it is verified — gap (no sample file from
  accounting) · who decides — clear (the user).

## 3. Questions for the user

1. How should the files reach accounting?
   - A. A download button on the reports page (Recommended) — no new moving parts; works
     by the 30th.
   - B. Email from the monthly job — fits "send it to us", but needs mail setup and
     retries.
2. Must the CSV match a column format accounting already uses?
   - A. No, our report columns as they are (Recommended) — fastest.
   - B. Yes, their template — send a sample file first.

## 4. Research

1. What are the maintained ways to render tables with page breaks to PDF in 2026? · why: no
   PDF library is installed, and the choice decides the effort for step 2 · would change the
   route: if only an HTML-to-PDF renderer handles long tables well, step 2 uses one instead.

## 5. Recommended route

1. do add a CSV writer over `build_monthly()` rows — why the rows already exist
   (`src/reports/build.py:41`) — check a test writes one known report and compares the file
   byte for byte — skill /ship-change
2. do add the PDF writer with the library section 4 settles — why accounting asked for PDF
   (user) and nothing is installed (`pyproject.toml`) — check a test renders a 3-page report
   with page breaks — skill /ship-change
3. do add the download route `/reports/<id>/export.<fmt>` — why the reports page has no
   route yet (`src/web/routes.py`) — check a request returns the file with the right
   content type — skill /ship-change
4. do send accounting one real exported report of each format — why there is no sample file
   from them (gap in section 2) — check they confirm it opens and the numbers match the
   page — skill none

- One-way doors: the URL shape `/reports/<id>/export.<fmt>` — bookmarks and scripts will
  depend on it.
- Verified by: the tests in steps 1–3, then step 4.
- wrong if: accounting needs the files pushed to them (question 1 → B); then step 3 becomes
  a mail step and the date is at risk.
- I am not sure, but the monthly report may be longer than one PDF page in most months; step
  2's test uses 3 pages for that reason.

## 6. Alternatives

- Print-to-PDF from the browser · rejected: accounting wants files, not a page to print
  (user's words).
- An external export service · rejected: NEVER send report data outside our servers.
- One combined export job that emails both formats · rejected for now: depends on question 1;
  it returns as the route if the answer is B.
- HTML-to-PDF renderer · rejected for now: depends on the research item 1 answer.

## 7. Stop triggers

- The chosen PDF library cannot render page breaks in a table → stop, re-run meta-thinking.
- Accounting's sample file shows a fixed column order we do not produce → stop, ask again.
- Step 1's test shows `build_monthly()` changes numbers between runs → stop; that is a bug,
  not export work.

---

Decided:
- answer 1 → A: a download button on the reports page — user, call 1.
- answer 2 → A: our report columns as they are — user, call 1.
- research item 1: `tablepdf` 3.2 renders tables with page breaks — web research, `Research first`.

## Backbrief (written after the user chose)

- Goal: CSV and PDF export of monthly reports, live by the 30th.
- Route: the recommended route; delivery by download button (answer 1 → A); our columns
  (answer 2 → A); `Research first` ran section 4: `tablepdf` 3.2 renders tables with page breaks.
- MUST keep report data on our servers · MUST be live by the 30th · NEVER change the numbers.
- First steps: the CSV writer with its byte-for-byte test; then the PDF writer on `tablepdf`.
- Stop triggers: as in section 7.
- Open: none
- Next skill: /ship-change, one run per step 1–3.

---

**Aside — what changes in other cases.**

- **Gate skip.** For "add a CSV button to this one report" the gate test finds no signal, so
  the main session offers nothing and does it directly; had the user typed `/meta-thinking`
  anyway, the gate line would read
  `[meta-thinking] gate: run (would skip: one sentence, one obvious route)`.
- **A second full route.** Had two PDF approaches both been viable — a pure-Python library and
  an HTML-to-PDF renderer — and could one afternoon's spike decide between them, section 6
  would carry the second route in the section 5 format, its first step the spike ("render
  report 2026-05 both ways, compare page breaks"). Without a one-way door, a deciding test or
  a user request for the routes, alternatives stay one line each.
- **More than three decisions.** Section 3 keeps three questions and lists the rest under
  `N more — open decisions`; call 1 then adds the `Grill first` question.
