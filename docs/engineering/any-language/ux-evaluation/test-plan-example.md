# Example: a usability test plan for the invoices screen

A worked example for [evaluation.md](evaluation.md). The screen is the invoices screen of Acme
Corp's billing application, the same invented screen as
[design-brief-example.md](../../react/design/design-brief-example.md): an accounts clerk opens it to
see which invoices are due or overdue and to start paying one. The screen is built, has passed its
heuristic review, and runs in a test environment. This plan is its first round of tests with users.
Every name, date and number is invented.

The parts of the plan are the ones GOV.UK's "Plan a round of user research" [1] and "Using
moderated usability testing" [2] and Digital.gov's "How to write a research plan" [3] list. The
table after the plan says which source lists which part; a part none of them lists is marked there
as this practice's choice. A line a reader might change or delete carries its reason after a `#`.

## The plan

```text
Test plan: invoices screen, round 1

Title: Moderated usability test of the invoices screen with accounts clerks, round 1
Authors: Jane Doe (researcher, facilitator), John Smith (developer, note-taker)
Stakeholders: the billing team's product owner, who decides what the team builds next

Context: The invoices screen (/invoices) is new. Until now, clerks found overdue invoices in a
spreadsheet export. The screen passed its heuristic review on 2026-10-30.
Past research: none on this screen.

Objectives:
- Find out whether clerks can tell due, overdue and paid invoices apart.
- Find out whether clerks start paying the right invoice when a customer has more than one.
- Assumption to test: clerks read the Status column, not the Due date, to find late invoices.
- Decision this round feeds: whether the screen goes to all clerks in December as it is, or
  changes first.   # the decision is what the round is for (evaluation.md section 2)

Method: moderated usability test, think-aloud, one participant at a time, 45 minutes.

Participants:
- 5 accounts clerks of Acme Corp, named P1 to P5 in all notes and findings.
    # 4 to 8 a round; more rounds, not a bigger one (evaluation.md section 4)
    # ids, never names (evaluation.md section 13)
- A mix of clerks who joined this year and clerks with three or more years.
- P5 uses a screen reader and works at their own desk, on their own set-up.
    # own device; one person's result is not generalised (evaluation.md section 7)
- Recruiting: through the finance team lead, from 2026-11-03.
    # at least a week before the sessions (evaluation.md section 4)
- The invitation asks about access needs.
- Consent: a form signed before the session says what is recorded, who can see it, and how
  long it is kept.

Tasks (read aloud, then handed over on a card; success is decided before the first session):
   # a definition written after watching bends to what people did (evaluation.md section 4)
1. "It is the end of the month, and your manager wants to know which invoices are late.
   Find them."
   Success: names the three overdue invoices in the test data, and no other.
2. "Your manager wants the Globex invoice with this week's deadline settled. Get it under way."
   Success: reaches the pay screen of the invoice due this week, not of the one due next month.
3. "A colleague asks whether the September invoice for Contoso has been settled. Find out."
   Success: says it is paid.
   # each task is a goal and never names a column, a status word or the Pay link
   # (evaluation.md section 4)

Measures, per task:
- Success: yes, with help, or no, against the task's definition above.
- Errors: each action that moves away from the goal and is undone, such as opening the pay
  screen of the wrong invoice.
- Time on task: from the end of reading the task to "done". Noted to spot a task that takes
  far longer than the others; never compared.
- The Single Ease Question after each task, then "Why that number?"
- No SUS in this round.   # five people are too few for its number (evaluation.md section 5)
- Findings are reported as counts, such as "2 of 5", never as percentages.
    # counts, not scores, below ten people (evaluation.md section 4)

Discussion guide:
- Introduction script, read word for word: who we are; we test the screen, not you; please
  think aloud; you can stop at any time; the recording is on.
- The three task cards, in the order above.
- After the tasks: "What was the hardest part?" and "What would you change first?"
- Planning checklist: test environment up and test data loaded; screen recording works;
  consent forms printed; task cards printed; P5's desk and screen reader checked the day
  before.

Sessions:
- 2026-11-17: P1 09:30, P2 10:45, P3 13:30.
- 2026-11-18: P4 09:30, P5 10:45 (at P5's desk).
    # no more than 6 one-hour sessions a day, 15 minutes or more between (evaluation.md section 4)
- Practice session with a colleague from the billing team: 2026-11-13.
- All three tasks run on the test environment by Jane Doe the day before: 2026-11-16.

Test environment and data:
- The test environment of the billing application, with 24 invoices whose amounts and dates
  look like a clerk's month and whose customer names are invented: three overdue, two unpaid
  for Globex (one due this week, one due next month), one paid for Contoso in September.
    # real-looking work keeps clerks engaged; no customer's data leaves production
    # (evaluation.md section 13)

Recording and notes:
- Screen and voice recorded, with consent; no camera.
- Recordings sit in the billing team's restricted research folder; only the two authors and
  the product owner can open them. How long they are kept: Acme Corp's data protection lead
  decides before the first session.
    # the practice does not set a period (evaluation.md section 13)
- John Smith takes notes in a sheet: one row per participant and task, with success, errors,
  time, the SEQ and its why, and quotes.
- Observers: the product owner and one designer, from another room through a screen share.
    # the team watches (evaluation.md section 4)

Roles and responsibilities:
- Jane Doe: plan, facilitation, analysis, findings, and one of the three severity ratings.
- John Smith: test environment, test data, notes. He built the screen, so he does not
  facilitate.
- Product owner: observes two sessions or more, and takes the decision of the objectives.

Timeline:
- 2026-11-03: recruiting starts.
- 2026-11-13: practice session.  2026-11-16: dry run.
- 2026-11-17 and 2026-11-18: sessions (2 days).
- 2026-11-19 to 2026-11-24: analysis (4 working days).
    # twice the time of the sessions (evaluation.md section 4)
- 2026-11-25: findings to the team. Each finding names the task, the participants who met it
  by id, what they did, its severity from 0 to 4, and a proposed change, and goes into the
  backlog, the most severe first. The severity is the mean of three ratings, each made on its
  own by Jane Doe, the observing designer and the product owner. John Smith built the screen,
  so he does not rate.
    # Nielsen's severity scale; one rater's severity is too unreliable (evaluation.md sections 3
    # and 4)
- Week of 2026-12-07: round 2, with five other clerks, on the fixed screen.
    # more rounds, not a bigger round (evaluation.md section 4)

Issues for awareness:
- Legal: the recordings show clerks' screens and voices, which are personal data; the consent
  form and the storage above cover them.
- Power: the participants work for Acme Corp and the product owner is senior to them. The
  observers stay out of the room, and no finding names or quotes a clerk by name.
- Accessibility: the invitation asks about access needs; P5 works at their own desk.
- Bias: the developer who built the screen takes notes and does not facilitate.

Left out of this round, on purpose:
- No synthetic users and no AI moderator (evaluation.md section 11). A coding agent drafted
  the first version of the tasks; Jane Doe rewrote them against evaluation.md section 4.
- No pass mark for the round: no source the practice rests on gives one (evaluation.md
  section 15).

Links: the screen's design brief; the notes of the heuristic review; the consent form.
```

## Why it is good

- **The objectives end in the decision the round feeds**, so the findings are written for the
  one person who has to choose ([evaluation.md](evaluation.md) section 2).
- **Five clerks in one round, and a second round on the fixed screen**, as section 4 asks; the
  plan does not claim that five people find every problem.
- **Each task is a goal in the clerk's words, and its success is written before the first
  session.** No task says "Due", "Overdue", "Status", "Pay" or "payment", so the round tests
  whether the screen shows those things, not whether the clerk can read the card (section 4).
  Task 2 has two unpaid Globex invoices with different due dates on purpose, so the round can see
  whether a clerk picks the wrong one.
- **The measures fit five people**: success, errors and the SEQ's "why" find the problems; time is
  noted, not compared; the SUS waits for a benchmark; findings are counts (sections 4 and 5).
- **One participant uses a screen reader on their own set-up**, and the plan does not treat that
  one person as all screen-reader users (section 7).
- **Personal data is settled before the first session**: consent, ids instead of names,
  invented customer names in real-looking data, a restricted folder, and the retention period
  left to the person who owns it, since the practice does not set one (section 13).
- **The developer who built the screen takes notes and does not facilitate**, which answers the
  bias the research plan asks the team to name [3].
- **What the round does not do is written down**, so nobody adds a synthetic user or a pass mark
  later and calls it part of the plan (sections 11 and 15). The agent's draft is named, and
  a person checked it (section 18).

## Where each part comes from

| Part of the plan | Listed by |
|---|---|
| Title, authors and stakeholders, context, past research | Digital.gov [3] |
| Objectives, with the decision they feed | GOV.UK, "Plan a round" [1]; Digital.gov's goals and questions [3] |
| Method | Digital.gov [3] |
| Participants: kinds, access needs, consent, recruiting a week ahead | GOV.UK, "Plan a round" [1] and "Moderated usability testing" [2]; Digital.gov [3] |
| Tasks as goals | GOV.UK, "Moderated usability testing" [2] |
| Success written per task before the sessions | this practice's choice ([evaluation.md](evaluation.md) section 4); no plan template read lists it |
| Measures per task | this practice's choice ([evaluation.md](evaluation.md) sections 4 and 5); GOV.UK lists similar measures for benchmarking, not for a round [4] |
| Discussion guide: introduction script, tasks, planning checklist | GOV.UK, "Moderated usability testing" [2] |
| Session times, practice session, dry run the day before | GOV.UK, "Plan a round" [1] and "Moderated usability testing" [2] |
| Test environment and real or made-up data | GOV.UK, "Plan a round" [1] and "Moderated usability testing" [2] |
| Recording, notes and observers | GOV.UK, "Plan a round" [1] |
| Roles, timeline with analysis time, issues for awareness, links | Digital.gov [3] |
| What the round leaves out | this practice's choice ([evaluation.md](evaluation.md) sections 11 and 15) |

## Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] GOV.UK Service Manual — Plan a round of user research — https://www.gov.uk/service-manual/user-research/plan-round-of-user-research
- [2] GOV.UK Service Manual — Using moderated usability testing — https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing
- [3] U.S. General Services Administration, Digital.gov — How to write a research plan — https://digital.gov/resources/how-write-research-plan/
- [4] GOV.UK Service Manual — Usability benchmarking a website or whole service — https://www.gov.uk/service-manual/measuring-success/usability-benchmarking-a-website-or-whole-service
