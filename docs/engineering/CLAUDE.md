# docs/engineering — writing and editing a practice

Each practice here is a folder named by the topic, never a bare file: the way one kind of work
should be done, in any repository. It sits in a group folder: `any-language/`, or the folder of
the one language its rules are for, such as `python/`. Every folder `ls -d docs/engineering/*/*/`
prints is a practice. This file is the contract for writing them, and a practice folder's
`README.md` is its map; the practice docs are a folder's rules file, or rules files, and its
example files. An example is anything a reader may copy: an `*-example.md` file, or a tree, a
diagram, a code snippet or a message inside a rules file or a `README.md`. A BAD example is one
shown as the form to avoid: labelled Bad or Before, or named by its rule as the wrong form. Every
other example is a GOOD example.

**Navigation**

- [The contract](#the-contract)
- [Researching a practice: the topics](#researching-a-practice-the-topics)
- [Writing or editing a practice](#writing-or-editing-a-practice)
- [Citing sources](#citing-sources)
- [Sources](#sources)

## The contract

- **A practice is the source; the code is the consumer.** A doc here says how the work should
  be done, never how this repository does it today. This repository may be behind a practice,
  or plain wrong. That is a gap in the code, never a reason to soften the doc: leave the doc as
  it is. What the code does about the gap, and when, is in `any-language/refactoring/refactoring.md`.
- **Reading a practice is mandatory before working in its area.** This file loads only when a
  file under this folder is read, so the mandate cannot fire from here: the project `CLAUDE.md`
  carries it, one routing line per practice — the moment it fires, the file to read, the check
  — and owns the rule that a new practice folder gets its line in the same change. Copying a
  practice folder into another repository does not carry the mandate; that repository adds the
  line to its own `CLAUDE.md` (`any-language/git/README.md` § "How to adopt", step 2). In this library that
  file is local and not committed; `CLAUDE.local.md` is the committed example of the section.

## Researching a practice: the topics

A new practice starts with research on the web, and the topic list below guides it; so does a new
rules file added to an existing practice. The rules a practice states are the practice; the list
only helps the research find them. It is not a table of contents: a topic that does not fit the
practice is dropped, and a topic the list lacks is added.

- **Research before the first rule.** Before you write the first rule of a new practice, or of a
  new rules file, research its topic on the web, and keep the record of that research outside the
  practice, with the working files of the change (in this library, the git-ignored
  `docs/artifacts/` folder). Before the research starts, run the search from § Writing or editing
  a practice, the bullet on creating a doc: when a practice on the topic exists, the work is a new
  rules file in it or an edit to it, and the research covers only what that practice does not.
  Work in this order:
  1. Go through the topics below and mark each one: it applies, and the practice covers it in
     detail; another practice, or another file of this practice, owns it, and this one links that
     file and section (§ Writing or editing a practice, the bullet on one owner); or it does not
     apply, with one sentence that says why.
  2. For each topic that applies, write the questions it raises for this practice.
  3. Read the source that owns each answer first (§ Citing sources has the order). Note each
     source you read, the date, and whether you read its own text or a tool's summary of it. A
     tool that answers a prompt about a page, such as WebFetch, returns a summary; the source's
     own text is the raw page, the raw file, or a PDF converted to text. For a rule that depends
     on a tool or a library, note the version you checked, because its behaviour changes between
     versions. A search that found nothing is a result too: write what you searched.
  4. When the research ends, mark the topics again; the final marks are the ones the pull request
     lists. A topic that applies but has no source after the search gets no rule: the practice
     names it in its purpose and scope as not covered yet.

  When subagents do the reading, quote this bullet, the bullet "Read what you cite" and the source
  table of § Citing sources in their brief, because a subagent may not load this file, and count a
  reading only when the agent says it read the source's own text; re-read any other reading
  yourself before it backs a quote, or let it back none. Why: a rule written from memory,
  or from the first search hit, can be years behind current practice. OWASP asks the author of a
  new cheat sheet "What other resources exist in this area?" [1], and Rust asks a proposal to
  "Discuss prior art, both the good and the bad" [2]. What the research found lands in the practice
  as its sources and its alternatives, not as a search log.
- **The topic list is a helper, not a gate.** When the research shows a topic the practice needs
  and the list lacks, add it to the practice; when that topic would serve other practices too, add
  its row to the table below in the same change, so the next practice does not miss it. Dropping
  or adding a topic needs nobody's approval. Security is the one topic whose "does not apply" goes
  into the practice itself and not only into the record: one line, in the form the W3C suggests,
  "There are no known security impacts of the features in this specification" [12], plus a link to
  the practice that owns a nearby rule where one exists, because a reader who copies the practice
  needs to know security was checked. Why: a part that must be filled in gets filled with nothing
  when its topic does not fit. Widely used templates mark such parts optional: MADR marks its
  optional parts "This is an optional element. Feel free to remove" [3], and Kubernetes marks the
  optional sections of its proposal template "(Optional)" [4].
- **Coverage, not headings.** When you write the practice's rules file, give each topic that
  applies a home a reader can find: its own `##` section, a part of one, or an example file, named
  in the practice's own words. Several topics can share a section. In a practice with several
  rules files, the `README.md` map says which file holds which topic. Why: an agent reads the rules
  file before it works, so a section that says nothing costs every reader and helps none; "A small
  set of fresh and accurate docs is better than a large assembly of "documentation" in various
  states of disrepair" [5]. A fixed set of headings, even optional ones, would pull a mistake away
  from the rule it breaks and an advanced rule away from its condition, because in a practice the
  topics interleave.
- **Check:** the pull request that adds the practice or the rules file lists, in its Notes, every
  topic with its final mark: applies, with the section that covers it; owned elsewhere, with the
  link; does not apply, with its sentence; or not covered yet. It also lists each topic added,
  saying whether it went into the table below. A reviewer takes each topic marked "applies" and
  asks: which lines of the practice's Sources section back the rules in that section? The record
  stays out of the repository; the sources are the trace a reviewer can see.

Covering a topic in detail means covering the cases it names completely and correctly; it does
not mean writing more. In two surveys of 323 IBM software professionals, Uddin and Robillard found
that "The three severest problems were ambiguity, incompleteness, and incorrectness of content"
[30].

| Topic | What covering it in detail means |
|---|---|
| Purpose and scope | The problem the practice solves, the outcome a project has when it follows the practice, who reads it, the one rule that holds the rest together, and what it leaves out on purpose. AWS's best-practice pages open with a "Desired outcome" [27], and Kubernetes asks every proposal "What is out of scope for this KEP?" [4]. |
| Basic use | The rules every project applies from the first day, in the order the work happens, each with a short example. Microsoft's style guide: "Start with simple examples and build up complexity after you cover common scenarios" [6]. |
| Advanced use | The rules that hold only under a named condition: a second team, a framework, a regulated product, a larger scale. Each opens with its condition, so a reader whose project does not meet it can skip it. Basic and advanced differ in when a rule applies, not in how expert the reader is. Why: a practice is read before the work starts, so a reader needs to know which rules hold for their project and can skip the rest; a split by reader skill would turn one set of rules into a tutorial and a reference. |
| Recommendations | The rules themselves, each one act at one moment with its reason (§ Writing or editing a practice), and what goes wrong when a project skips one; where several ways work, one default and the case for another. AWS's best-practice pages state the "Level of risk exposed if this best practice is not established" [27], and OWASP asks its authors to "Recommend specific approaches rather than listing every possible option" [7]. |
| Common mistakes | Each mistake readers make: what it looks like, why people make it, what it costs, and the fix. A mistake in an artifact is a BAD next to its GOOD (§ Writing or editing a practice). Catalogs of settled practice do the same: AWS's Well-Architected best-practice pages list "Common anti-patterns" [27], and Azure's pattern catalog says "An antipattern describes a practice to avoid" [28]. Google's technical-writing course holds that "it is sometimes wise to show readers what not to do" [8]. This rests on writers' advice, not on a measured effect, so list the mistakes a source or a review has seen, not every one you can imagine. |
| Good examples | The examples § Writing or editing a practice asks for, each with the sentence that says why it is good. Where advanced use changes what the artifact looks like, the research checks whether that case needs an example too. Readers copy them, as MDN warns: "Readers will copy and paste examples into their own code and may put it into production" [9]. |
| Security | What an attacker, a leaked secret, input from outside, a dependency or an unsafe default can do through this kind of work, and the rule that stops each; a rule another practice owns is linked, not repeated. Ask the question Python's proposal template asks: "How could a malicious user take advantage of this new feature?" [31]. Say which threats the practice covers and which it leaves out, and why, as the IETF asks of every specification: "which attacks are out of scope (and why!)" [10]. Examples carry the risk too: Fischer et al. found insecure snippets copied from a Q&A site in 15% of 1.3 million Android apps [11]. When nothing applies, the bullet on the topic list above says what the practice still writes. |
| Privacy and personal data | What personal data this kind of work touches (logs, examples, test data, prompts) and how the practice keeps it out. Whether a document needs this part depends on its content [13]. |
| Where the rules stop holding | When a rule does not apply, and what following it costs: the trade-offs. Rust's template asks "Why should we *not* do this?" [2], OWASP's conventions for its cheat sheets say "Say when guidance does not apply" [14], and Azure's design-pattern pages, such as Circuit Breaker, list when "This pattern might not be suitable" [29]. |
| Alternatives considered | Other ways the sources propose, and why the practice does not take them, so nobody raises the same idea again without the reason. Python's process says rejected ideas "should be recorded along with the reasoning as to why they were rejected" [15]. |
| Adoption in existing code | How code written before the practice moves to it: one of the three answers in `any-language/refactoring/refactoring.md` section 7. |
| Checks | How a reader or a tool tells that a rule was followed: a linter rule, a CI step, or one question at review (§ Writing or editing a practice, the bullet on `Check:` lines). |
| How an agent applies it | The routing line a project's `CLAUDE.md` gets for the practice (§ The contract), and the mistakes an agent makes in this kind of work, when the research found any. |

## Writing or editing a practice

- Take every rule from public practice, never from what the code in this repository does. The
  check: no rule in a practice doc is justified by what this repository's code does today, and
  no sentence in one names this repository, its owner, a decision made in it, or a person who
  works on it. A link to another doc is not a hit.
- Before you create a doc, run `grep -ril "<topic>" docs/`. If a doc on that topic exists,
  extend it; the diff then shows an edited file, not a second file on the same topic. A practice
  is one folder named by the topic, with a `README.md` map, a rules file and one ideal example
  per artifact type; never a bare file, even before the examples exist. A topic whose subjects a
  reader looks up apart, such as testing, has one rules file per subject, and its `README.md`
  says which file to read for which work.
- Before you create a practice folder, pick its group by what its rules cover, not by its
  examples. A practice goes under `any-language/` when every rule in it holds in any language,
  apart from a part it labels as one language's case (file-structure's "Python case",
  refactoring's section 10); Python examples and tool names do not change that. Every other
  practice goes under the folder of the language it is written for, such as `python/`, even when
  some of its rules would hold in any language (testing's `what-to-test.md`); those rules move
  out the way the next sentence says. Before a language adds a topic another language's folder
  already holds, move the rules that hold in any language into an `any-language/` practice, in a
  commit of its own whose body names an answer from `any-language/refactoring/refactoring.md`
  section 7; that practice then links each language's practice on the topic for that language's
  case. A language or framework with no folder yet gets one, named by it in lower case
  (`react/`). The name `any-language/` states the test a practice passes to sit there, which a
  name like `general/`, `common/` or `shared/` would not (`core/` is file-structure's word for
  shared application code). A group folder holds practice folders and nothing else. The check:
  before you stage, `find docs/engineering -maxdepth 2 -name '*.md'` prints only
  `docs/engineering/CLAUDE.md`.
- When you add or remove a practice, change the practice list in the root `README.md` in the same
  commit. When you add a group, also change the README's sentence on the groups, its tree, its
  examples badge and every line that says the examples are only in Python. The check: before you
  stage, every folder `ls -d docs/engineering/*/*/` prints has a link in the README list, and
  `grep -n -i -E 'in Python|other than Python' README.md` shows nothing the change made false.
- A rule has one owner: the practice whose topic it is, as each practice folder's `README.md` says.
  When one practice needs a rule another owns, link that practice's file and section, and never
  write the rule's conditions or its check again. Where two practices disagree, the owner's
  text stands and the other one changes. The check: before you stage, every sentence in the
  diff that uses a rule another practice owns links that practice's file and section, and none
  repeats the rule's conditions or its check.
- Before you write a practice file, or add, rename or remove one of its `##` headings, read
  `any-language/git/git.md` section 9: it says which files open with a navigation block and how the block is
  kept in step. In a file that has one, the diff shows each heading change next to its line. When
  you renumber or move a `##` section of a rules file, run
  `git grep -n -E '<file>\.md\)? (section|§) ?<old n>([^0-9]|$)' docs/` and update each hit in the
  same commit, because a comment that cites the old number now points a reader at the wrong rule.
- When you add a practice, or change a rule in one, write in the commit body how existing code
  responds, using one of the answers `any-language/refactoring/refactoring.md` section 7 lists. In the same
  commit, change every example under `docs/engineering/` that the new or changed rule governs
  and does not yet follow; an example never waits for a change to touch it.
  The check: the commit body names one of the answers, and before you stage,
  each hit of `grep -rn "<key term of the rule>" docs/engineering/`, and of a second search for
  the code the rule is about (`os.environ` for a settings rule), is in the diff, is a BAD that
  shows the old form on purpose, or already shows the new rule. An added practice gets one
  search per rule.
- Write a rule as one act, at one moment, then give its reason in one clause: the goal it serves
  or the failure it prevents. The reason lets a reader judge an exception and see when the rule
  needs another look; a rule whose reason you cannot state is a candidate to cut. Google's style
  guides aim to give each ruling its pros, cons and decision [16], so that "it should be clearer
  to everyone when a rule may be waived" [17]. A reason
  never replaces a check. `docs/claude-code/claude-md.md` § "How to write a line an agent can
  follow" is the test for the moment, the act and the check. A practice doc gives every rule its
  reason, which that section asks of an instruction file only where the act could be misapplied: a
  practice is read when its work starts, and an instruction file is in every turn's context. A
  `Check:` line is optional: most rules leave their act in the diff, and review is enough.
  Add one where a miss would be costly or easy to overlook in review, and make it one specific
  question at a named moment ("read the title alone") or a tool that already runs and rarely cries
  wolf (`lint-imports` in CI) — never "review carefully", and never a gate people will have to
  bypass. The check: each `Check:` line the diff adds is one question or one command.
- Every name in an example is a placeholder (`Acme Corp`, `Jane Doe`, `PROJ-123`,
  `example.com`) or a well-known name of the same kind standing in for a real client — a
  well-known bank for a bank; it marks the role and claims nothing about that company. A real
  company appears under its own name only as a cited source, as the tool described, or as its
  own public product.
- When you write or change a GOOD example, make it follow every practice here that governs what
  it shows, and say next to it why it is good. Why: readers, people and agents, copy the example
  and not the rules around it, so a GOOD that breaks a practice spreads that break to every copy
  and to every author who cites it as precedent (documentation teams hold their samples to the
  same bar: MDN asks that examples "follow generally accepted best practices" [9], and Microsoft's
  .NET docs "show code you should write today" [18]). A practice governs an example when its
  routing line in the project `CLAUDE.md` would fire for that code in an application. Add nothing
  only to show another practice. Code it leaves out is cut with `...`, or named as left out in the
  sentence that introduces it; never shown as if it were complete. The check: when you write the
  commit message, open the sections of each practice that governs each GOOD the diff adds or
  changes, and put a `Practices: <rules file> §n, …; every other practice governs nothing here`
  line in it as a git trailer (`Key: value`): last, with the other trailers, above
  `Co-Authored-By:` where that line exists, a long one folded onto indented lines, such as
  `Practices: testing/layout.md §3, logging/logging.md §8; every other practice governs nothing here`.
  When no practice governs the examples, the line is `Practices: none govern these examples`.
  Why a trailer: `git log` keeps it with the change, and this library has no CI to run a stricter
  check.
  A GOOD with no sentence that says why it is good fails.
- Before you stage, a GOOD that breaks a rule of a practice that governs it is not ready,
  whatever severity a review gives the break, unless the example declares the departure where it
  happens: it names the rule, says why it departs and what that costs, so a reader who copies it
  sees the trade and can choose (the Google C++ Style Guide states a rule's goal so that "it
  should be clearer to everyone when a rule may be waived" [17]). Fix every other
  break before you stage, and never park it in a backlog or let a review record it as a design
  choice, because readers copy it in the meantime. If the rule is the thing that is wrong, change
  the rule in the practice that owns it. The evidence that an example follows a practice is a
  clause in that practice's rules file, never another example.
- In an example, each line that [readability.md](any-language/readability/readability.md)
  section 4 says carries its reason (code that others copy) gets a short comment that says why,
  and names the rule's section where a practice rule owns the reason, such as
  `# One trace per label, so a wrong verdict can be opened (evals.md section 9).` The longer
  reason goes in the sentence after the block that says why the example is good. The check:
  before you stage, ask of each line the diff adds to an example whether a reader who copies it
  would likely undo it; if so, it has its reason at the line.
- When you write or change a BAD example, or the GOOD that fixes one, make the BAD show one
  problem, named in its label or by the rule that calls it wrong; the reason sits right after
  it, and in everything else it follows every practice here. Its GOOD is the same example with
  that problem fixed, and says which problem it fixes and why the fix is better. The check:
  before you stage, set the two side by side; every difference is the named problem or follows
  from its fix, and the GOOD's text names that problem, and the BAD's reason sits in the lines
  right after it.
- Before you stage, run every check the bullets above name for what your diff touches. Then
  re-read the diff for two things: a rule justified by this repository's code, and a real name.
  A failed check, or either of the two, means the doc is not ready.

<!--
FUTURE: rule levels (Must / Should) for every practice
Trigger: a second practice needs rules that help on some tasks and hurt on others, or the library
decides to give every rule a level.
Fix location: this section.
Approach: one bullet: every rule opens with its level, Must (always, when its condition holds) or
Should (keep it when a test shows it helps). Existing practices adopt it when a change touches
them (any-language/refactoring/refactoring.md section 7, "New and touched code").
any-language/prompt-engineering/prompt-engineering.md section 1 is the first practice written this way.
python/evals/evals.md section 1 adds a third level, Optional: add it when the need the rule names appears.
-->

## Citing sources

A practice doc names the outside source behind each claim it takes from one, so a reader can
check the claim and judge how far to trust it. New practices use the form below, and this file
uses it too; the bullet on practices written before these rules says when an older file moves to
it.

- **A marker after the sentence.** When you write a sentence in a practice doc that rests on an
  outside source — a rule's reason, a fact, a number, a quote — end it with `[n]` before its
  closing period, and give the source its line under the file's Sources section. When the sentence
  ends with a quote, the marker follows the closing quotation mark and the period follows the
  marker: `… in various states of disrepair" [5].` IEEE places its numbers the same way: "in square
  brackets, inside the punctuation" [19]. Mark only a sentence that rests on a source; a sentence
  of your own reasoning gets no marker. Two sources behind one sentence get a marker each, with a
  comma and a space between them: `[3], [7]`. Never write a range (`[3]–[5]`), two markers with no
  space (`[3][7]`) or a part inside the brackets (`[3, Sec. 2]`), because the check below does not
  see them; name the part in the sentence instead ("RFC 3552, section 5, asks … [10]"). Why:
  Wikipedia asks an inline citation for "quotations and any facts or claims challenged or likely
  to be challenged" [20], and a marker on every sentence would hide the ones that matter. A link
  to another doc in this library stays an ordinary Markdown link.
- **One number per source, never moved.** When you cite a source the file already cites, use its
  number again; IEEE: "There must be only one reference with each number" [19]. When you add a
  source, give it the next free number, wherever its first marker falls; a number is never moved
  or given to another source, and a source you remove leaves its number unused. Why: the Mayfield
  Handbook notes that in a numbered style "the addition or deletion of a reference will
  necessitate the renumbering of references throughout the manuscript" [21], and numbers that only
  grow keep an edit to the lines it changes.
- **The Sources section.** It is the file's last `##` section, named Sources. Its first line is
  `Checked <YYYY-MM-DD> unless a line ends with — checked <YYYY-MM-DD>.`, then one list item per
  source in number order, in one of two forms:
  - a piece (a paper, an article, a post, a talk, a book):
    `- [n] <author> — <title> (<publication>, <year>; <kind>) — <link>`. The kind is `research`
    when it reports a study with data or a formal analysis (an article that only cites studies is
    an opinion), `research, sponsored by <company>` for such a study a company paid for, `case`
    for what happened at one organisation, `opinion`, `interview`, `column`, `sponsored by
    <company>` for other paid content, or `kind not confirmed` when you read the part you cite in
    the piece's abstract or a listing but could not open the full piece, which then counts as not
    research. A piece with no named author takes its publisher as the author, and a piece with no
    date writes `no date` for the year. An issue, a pull request or a Q&A answer is a piece: its
    site and project are the publication, and its kind is `opinion`, or `case` when it reports
    what happened in that project;
  - official material (a standard, a specification, a tool's documentation, a project's own
    policy page): `- [n] <owner> — <title>[, <version or edition>] — <link>`, where the version
    or edition is one the source names for itself: a release number or tag, a numbered version,
    or the date of an edition that does not change, such as an RFC's month. A page's "last
    updated" date or a file's last-commit date is not one, since the line's checked date already
    records when you read the page.

  A line read on another day than the first line's date ends with `— checked <YYYY-MM-DD>`. A
  source that does not change, a DOI, a published book or a link pinned to a release tag or a
  commit, needs no date of its own. Prefer such a link where one exists: Hata et al., who studied
  links in source-code comments, advise "referencing permanent links", with DOIs for papers and
  tags or commit hashes for code [22]. A book with no free copy names its edition and has no link.
  Why the date: Pew Research Center found that "38% of webpages that existed in 2013 are no longer
  accessible a decade later" [23], and Jones et al. found in scholarly articles that "for over 75%
  of references the content has drifted away from what it was when referenced" [24]. The date
  tells a reader when someone last read the cited part.
- **Read what you cite.** When you are about to cite a source, open it first and find the part
  that supports your sentence; write a date only for a reading you did, because a link that opens
  is not a reading. A quote in quotation marks copies the source's own words, as you read them in
  its own text, never in a tool's summary of it. A source whose supporting part you could not read
  at all, not even in an abstract, is a lead to search further and gets no line. Why: OWASP's
  conventions for its cheat sheets put it plainly: "A plausible-looking URL that does not exist,
  or that does not contain the claimed content, is worse than no citation" [14].
- **Say what kind of claim it is.** When you write a sentence from a source, give an opinion, an
  interview or a column as its author's view ("Fowler holds that …"), a case as what happened
  there ("At Acme Corp, …"), and research as what it found ("X et al. found that …"). For a case or
  a study, name its context in the sentence (the organisation, the platform, the scale), so a
  reader can judge whether it fits their project. Call something a best practice, or generally
  accepted, only when a standard or a specification says so, or several independent sources
  agree; sources are independent when they have different authors and different origin documents.
  A vendor's guide alone never makes a practice a best practice, except for how to use the
  vendor's own product. Why: Wikipedia's rule for a source that is not authoritative is to
  "attribute the opinion to the author in the text of the article but do not represent it as
  fact" [25].
- **Start from the source that owns the claim.** When you pick a source, start from the one the
  table names for the kind of claim; which source is strongest depends on what the claim is
  about: "No source is 'always reliable' or 'always unreliable' for everything" [25]. When two
  sources disagree, the rule follows the one in the claim's "Read first" column over its "Then"
  column, and either of those over the table's last row; show the other beside it with its kind,
  and never average the two into a middle. When two sources in the same cell disagree, show both
  with their kinds, say which one the rule follows and why, and record the other under the
  practice's alternatives considered.

  | The claim is about | Read first | Then |
  |---|---|---|
  | How a tool, a format or a standard behaves | Its owner's documentation, specification or changelog, at the version the rule names | The project's issue tracker, for known problems at that version |
  | Whether a practice works, or what it costs | Research that measured it | Several independent practitioners who report the same |
  | How teams should do the work | The standard or specification of the body that owns the area, where one exists (an IETF RFC or BCP, a W3C note, an OWASP or NIST standard, a language's own PEP); then named practitioners with books or long public work, and the published style guides of engineering organisations | Cases |
  | Any of these | — | Vendor how-to guides, blog posts and Q&A answers, as pointers to a stronger source, never the only source behind a rule |

  When research that measured a practice, or a source the "Read first" cell names after the
  standard, disagrees with a standard, the rule follows the standard and shows the other beside it
  with its kind; a rule that follows the other instead says why under its alternatives considered.

  A vendor's documentation owns how its own product works, never a claim about its merits, such
  as "faster" or "safer": that claim needs a source that would be wrong if it were wrong. Name a
  vendor tie or a sponsor on the source's line; Garousi, Felderer and Mäntylä's guidelines for grey
  literature in software-engineering research ask of every source "Is there vested interest?"
  [26].
- **A practice written before these rules.** When you change a rules file written before these
  rules, cite a new sentence in the form the file already uses, so one file never mixes two forms.
  A file that cites no outside source yet takes this form with its first cited sentence, in the
  same change; that is not a move. A file whose sources section has another name, such as
  `Where these rules come from`, renames it to Sources when it moves. A file that lists its sources
  in another form, such as `Sources:` paragraphs, keeps that form until it moves; when it moves,
  they become one Sources section. A file written before these rules moves to this form in a commit
  of its own that converts its whole Sources section, never as a side part of another change. This
  departs on purpose from `any-language/refactoring/refactoring.md` section 2, where new lines
  follow the current practice at once and touched code moves in the same change: moving a file to
  markers means re-reading every source it cites, which a one-sentence fix should not carry. A new
  rules file follows these rules in full (§ Researching a practice). A rules file whose research
  started before this section reached `main` counts as written before these rules: it keeps its
  citation form, and its pull request still lists the topic marks that step 4 of § Researching a
  practice asks for. The check: in a diff that adds the first `[n]` marker to a file, that file's
  whole Sources section is in this form.
- **Check:** before you stage a practice doc, run this command in bash; it prints nothing when
  every marker in the text has its line under Sources and every line there is cited. A `<` line is
  a marker with no source line: add the line, or remove the marker. A `>` line is a source no
  sentence cites: cite it, or remove the line. The command counts markers and proves nothing about
  what a source says, which only the reading above does.

  ```bash
  f=<file>; diff <(sed '/^## .*Sources$/,$d' "$f" | grep -oE '(^|[ (])\[[0-9]+\]' | tr -d ' (' | sort -u) <(sed -n '/^## .*Sources$/,$p' "$f" | grep -oE '^- \[[0-9]+\]' | cut -c3- | sort -u)
  ```

## Sources

Checked 2026-10-16 unless a line ends with — checked <YYYY-MM-DD>.

- [1] OWASP Cheat Sheet Series — New Cheat Sheet Proposal (issue template) — https://github.com/OWASP/CheatSheetSeries/blob/master/.github/ISSUE_TEMPLATE/new_cheatsheet_proposal.md
- [2] The Rust Project — RFC template (`0000-template.md`) — https://github.com/rust-lang/rfcs/blob/master/0000-template.md
- [3] MADR — Markdown Architectural Decision Records, template 4.0.0 — https://github.com/adr/madr/blob/4.0.0/template/adr-template.md
- [4] Kubernetes — KEP template (`NNNN-kep-template/README.md`) — https://github.com/kubernetes/enhancements/blob/master/keps/NNNN-kep-template/README.md
- [5] Google — Google documentation guide: Documentation Best Practices — https://google.github.io/styleguide/docguide/best_practices.html
- [6] Microsoft — Microsoft Writing Style Guide: Code examples — https://learn.microsoft.com/en-us/style-guide/developer-content/code-examples
- [7] OWASP Cheat Sheet Series — Cheat Sheet Writing Guide (`GUIDELINE.md`) — https://github.com/OWASP/CheatSheetSeries/blob/master/GUIDELINE.md
- [8] Google — Technical Writing Two: Creating sample code — https://developers.google.com/tech-writing/two/sample-code
- [9] MDN Web Docs — Guidelines for writing code examples — https://developer.mozilla.org/en-US/docs/MDN/Writing_guidelines/Code_style_guide
- [10] IETF — RFC 3552, Guidelines for Writing RFC Text on Security Considerations (BCP 72), July 2003 — https://www.rfc-editor.org/rfc/rfc3552
- [11] Felix Fischer et al. — Stack Overflow Considered Harmful? The Impact of Copy&Paste on Android Application Security (IEEE Symposium on Security and Privacy, 2017; research) — https://arxiv.org/abs/1710.03135
- [12] W3C — Self-Review Questionnaire: Security and Privacy (Editor's Draft) — https://w3c.github.io/security-questionnaire/
- [13] IAB — RFC 6973, Privacy Considerations for Internet Protocols, July 2013 — https://www.rfc-editor.org/rfc/rfc6973
- [14] OWASP Cheat Sheet Series — Cheat sheet conventions (`cheatsheets.instructions.md`) — https://github.com/OWASP/CheatSheetSeries/blob/master/.github/instructions/cheatsheets.instructions.md
- [15] Python — PEP 1, PEP Purpose and Guidelines — https://peps.python.org/pep-0001/
- [16] Shaindel Schwartz — Style Guides and Rules, chapter 8 of Software Engineering at Google (O'Reilly, 2020; case) — https://abseil.io/resources/swe-book/html/ch08.html
- [17] Google — Google C++ Style Guide, Goals of the Style Guide — https://google.github.io/styleguide/cppguide.html
- [18] Microsoft — .NET documentation: Common C# code conventions — https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions
- [19] IEEE — IEEE Reference Guide, V 11.12.2018 — https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/IEEE-Reference-Guide.pdf
- [20] Wikipedia — Wikipedia:Verifiability — https://en.wikipedia.org/wiki/Wikipedia:Verifiability
- [21] Leslie C. Perelman, Edward Barrett and James Paradis — The Mayfield Handbook of Technical & Scientific Writing, section 10.3 (Mayfield Publishing, no date; opinion) — https://web.mit.edu/21.guide/doc-sty.htm
- [22] Hideaki Hata et al. — 9.6 Million Links in Source Code Comments: Purpose, Evolution, and Decay (ICSE, 2019; research) — https://arxiv.org/abs/1901.07440
- [23] Athena Chapekis et al. — When Online Content Disappears (Pew Research Center, 2024; research) — https://www.pewresearch.org/data-labs/2024/05/17/when-online-content-disappears/
- [24] Shawn M. Jones et al. — Scholarly Context Adrift: Three out of Four URI References Lead to Changed Content (PLOS ONE, 2016; research) — https://doi.org/10.1371/journal.pone.0167475
- [25] Wikipedia — Wikipedia:Reliable sources — https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources
- [26] Vahid Garousi, Michael Felderer and Mika V. Mäntylä — Guidelines for including grey literature and conducting multivocal literature reviews in software engineering (Information and Software Technology, 2019; opinion) — https://arxiv.org/abs/1707.02553
- [27] AWS — AWS Well-Architected Framework, Security Pillar: SEC01-BP01 Separate workloads using accounts — https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/sec_securely_operate_multi_accounts.html
- [28] Microsoft — Azure Architecture Center: Cloud Design Patterns — https://learn.microsoft.com/en-us/azure/architecture/patterns/
- [29] Microsoft — Azure Architecture Center: Circuit Breaker Pattern — https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker
- [30] Gias Uddin and Martin P. Robillard — How API Documentation Fails (IEEE Software, 2015; research) — https://doi.org/10.1109/MS.2014.80
- [31] Python — PEP 12, the PEP template (`pep-NNNN.rst`) — https://github.com/python/peps/blob/main/peps/pep-0012/pep-NNNN.rst
