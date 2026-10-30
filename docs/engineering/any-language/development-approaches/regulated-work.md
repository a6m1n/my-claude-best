# Regulated, safety-critical and fixed-scope work

A team that builds software for a medical device or a safety system, or for a customer on a
fixed-price contract, often hears that it must work in a waterfall. This file says what the
regulator and standard texts read for it ask of a development approach, how a team runs an agile
loop inside the plan-driven frame that safety evidence and approvals need, and what a fixed price
or a fixed scope does to agile work. It is for the team lead, the project manager, the quality or
regulatory lead, and an agent asked to plan such work. Which deliverables run adaptive and which
run as fixed milestones is decided per deliverable in
[life-cycle.md](../project-management/life-cycle.md) section 4; this file adds what a regulator, a
safety standard or a contract changes in that choice. The rule that holds the file together:
**fix only what the regulator's text, the standard or the contract fixes, and run the rest of the
work in an agile loop inside that frame.**

**Navigation**

- [1. What regulators and standards require](#1-what-regulators-and-standards-require)
- [2. An agile loop inside a plan-driven frame](#2-an-agile-loop-inside-a-plan-driven-frame)
- [3. Fixed-price and fixed-scope contracts](#3-fixed-price-and-fixed-scope-contracts)
- [4. Common mistakes](#4-common-mistakes)
- [5. Where the rules stop holding](#5-where-the-rules-stop-holding)
- [6. Alternatives considered](#6-alternatives-considered)
- [7. Adoption in a running project](#7-adoption-in-a-running-project)
- [8. How an agent applies it](#8-how-an-agent-applies-it)
- [9. Sources](#9-sources)

**When you do not need this file.** When no regulator, no safety standard and no fixed-scope
contract governs the work, [life-cycle.md](../project-management/life-cycle.md) section 4 and
[choosing-an-approach.md](choosing-an-approach.md) cover the choice, and this file adds nothing.
Regulated software of low risk needs a lighter frame than section 2 describes, because the FDA
ties the effort to the risk: "Based on the intended use and the safety risk associated with the
software to be developed, the software developer should determine the specific approach, the
combination of techniques to be used, and the level of effort to be applied" [1]. A contract
that fixes the budget and the date but lets the scope move needs less than section 3 describes,
because Fowler holds that a fixed scope, not a fixed price, is what conflicts with agile work [2].

**What it leaves out on purpose.**

- The texts of IEC 62304, ISO 26262-6, DO-178C, IEC 61508, IEC 60880, EN 50128, AAMI TIR45 and
  ISO 13485: not covered yet, because the research did not read them (they are sold, or their
  pages were blocked); section 5 says what was read about each.
- Regulators other than the US FDA, such as the EU's rules for medical devices: not researched.
- Contract law. The clauses in section 3 are practitioners' proposals; a lawyer writes the
  contract.
- How an agile loop and a plan-driven frame combine outside regulated work, Water-Scrum-Fall
  included: [combining-approaches.md](combining-approaches.md).
- Security: there are no known security impacts of the rules in this file. A regulator may ask for
  security work across the life cycle: the FDA notes that software device manufacturers "may need
  to establish a cybersecurity risk management process that encompasses the total product
  lifecycle" [3]. That process is not covered here.

## 1. What regulators and standards require

**Before you plan the life cycle of regulated software, read the regulator's and the standard's
own text, and note the edition you read and the date.** Why: the regulator texts read for this
file prescribe no development model, so a team that believes from hearsay that the regulator
wants a waterfall pays for a process nobody asked for. Editions also move: a section of the FDA's
2002 guidance was superseded in 2025, and the US device quality regulation changed in 2026
(below).

**The FDA, for medical device software.**

- The FDA's General Principles of Software Validation (2002) says in section 5.1: "This guidance
  does not recommend the use of any specific software life cycle model. Software developers should
  establish a software life cycle model that is appropriate for their product and organization"
  [1]. The same section adds: "The software life cycle model that is selected should cover the
  software from its birth to its retirement" [1]. Section 5 opens by saying that its tasks "may
  be one time occurrences or may be iterated many times, depending on the life cycle model used"
  [1].
- Only section 6 of that guidance is superseded: FDA's note at the front of the 2002 guidance says
  that the Computer Software Assurance guidance "supersedes Section 6: Validation of Automated
  Process Equipment and Quality System Software of this guidance", and that the other sections
  still reflect FDA's current thinking [1]. The Computer Software Assurance guidance was first
  issued on 2025-09-24 and re-issued on 2026-02-03 as "Computer Software Assurance for Production
  and Quality Management System Software" [4]. It covers software used in production or in the
  quality system, and it "does not provide recommendations for the design and development
  verification or validation requirements for device software functions"; for those, it points
  back to the 2002 guidance [4].
- FDA's 2023 guidance on premarket submissions for device software functions names agile in its
  scope: "This guidance does not recommend the use of any specific software life cycle model or
  development methodology (such as waterfall model or other variations thereof, spiral model,
  Agile model, etc.)" [3]. Whatever the model, it asks sponsors to keep their design history
  file (DHF) in step with the work, in its words "synchronized with their software development,
  verification, and validation efforts" [3]. Documentation written later "could raise concerns
  regarding whether a developer has adequate control of their design process" [3].
- FDA recognises AAMI TIR45:2023, "Guidance on the use of AGILE practices in the development of
  medical device software", as a "Complete standard" [5]. Its recognition entry says the TIR
  gives "recommendations for complying with international standards and U.S. Food and Drug
  Administration (FDA) guidance documents when using AGILE practices to develop medical device
  software" [5]. FDA accepts declarations of conformity to the 2012 edition in premarket
  submissions until 2028-07-02 [5]. The TIR's own text was not read for this file.
- These guidances recommend and do not bind: the 2023 and 2026 guidances carry FDA's note "The
  use of the word should in Agency guidances means that something is suggested or recommended, but
  not required" [3], [4]. What binds is the regulation. In the US that is the Quality
  Management System Regulation, in force since 2026-02-02, which incorporates ISO 13485:2016 by
  reference [6]. The 2002 and 2023 guidances were issued before it, and FDA asks manufacturers
  to review the current QMSR [1], [3].

**IEC 62304.** Edition 1.1, the first edition of 2006 with its amendment of 2015, is the current
edition, and IEC's webstore lists Edition 2 as under development, not published [7]. The
webstore says the standard "Defines the life cycle requirements for medical device software" and
"does not cover validation and final release of the medical device, even when the medical device
consists entirely of software" [7]. What its text says about life-cycle models was not read, so
this file makes no claim about it (section 5).

**Two sources on whether safety standards assume a plan-driven model.**

| Source | What it says | Kind | Texts it covers |
|---|---|---|---|
| FDA, the 2002 and 2023 guidances [1], [3] | Recommends no life-cycle model or methodology, and names the Agile model among the examples | The regulator's own guidance | US medical device software |
| Stålhane, Myklebust and Hanssen, 2013 [8] | The standards they studied "are developed for plan driven, waterfall or V-model development processes" | The authors' claim, in the paper's introduction | IEC 61508, IEC 60880 (nuclear), EN 50128 (railway) |

The two do not cover the same texts. For software under the FDA, this file follows the FDA's
text, because the regulator owns what it asks for. For the standards the SINTEF authors studied,
the standards' own texts were not read, so their sentence stands as the authors' 2013 view, and
whether those standards favour a plan-driven model stays open (section 5).

- **Before development starts, write down the life-cycle model and the reason for it**, in the
  plan where [life-cycle.md](../project-management/life-cycle.md) section 4 records each
  deliverable's approach. Why: the FDA's 2002 guidance asks the developer to establish a model
  "appropriate for their product and organization" [1], and a model nobody wrote down cannot be
  shown to a reviewer.
- **In the same plan, name each regulator text and standard that applies, with its edition.** Why:
  a claim about what a regulator asks holds only for the edition that was read, and the FDA's
  texts above changed in 2025 and 2026.

## 2. An agile loop inside a plan-driven frame

The default for regulated and safety-critical software: **run the software work in an agile loop,
in sprints or a Kanban flow, inside a plan-driven frame that holds the safety analysis, the
planned evidence and the approvals.** This default is this practice's own reading of SafeScrum and
the V-Modell XT, both below. Its boundary: the FDA's guidance asks that a life-cycle model be
established that covers the software "from its birth to its retirement" [1], and the loop runs
inside that model, not in place of it. No source read for this file removes the frame, and the
research found no account of safety-critical work run without one.

The frame and the loop hold different things:

| Part | Where it runs | Why |
|---|---|---|
| The system-level risk and safety analysis, and the decision on the safety level | The frame, before and around the loop | SafeScrum runs it "outside the Safe Scrum process" [8] |
| Safety requirements | A safety backlog of their own | They are "quite stable" [8] |
| Functional requirements | The product backlog | They "can change considerably over time" [8] |
| Decision points (milestones), each with a progress check and a decision on how the project goes on | The frame | The V-Modell XT asks for them [9] |
| Development, verification and the design records of each increment | The loop, in each sprint | FDA asks that the design history file stay "synchronized" with the work [3] |

**SafeScrum.** Tor Stålhane (NTNU), Thor Myklebust and Geir Kjetil Hanssen (SINTEF) adapted Scrum
to three safety standards: IEC 61508, IEC 60880 for nuclear control systems and EN 50128 for
railways [8]. In the paper's introduction they hold that these standards "are developed for
plan driven, waterfall or V-model development processes", and that Scrum and other agile models
"are not well adapted to the development of safety critical software" [8]. Their answer
keeps the standard's process around Scrum: "let Scrum do what Scrum is good at", and "The rest of
the process specified by the standard is performed in the same way as when we use any other
model" [8]. What they propose:

- "All the risk and safety analyses on the system level are done outside the Safe Scrum process,
  including the analysis needed to decide the safety level" [8]. Inside the loop, the
  software is analysed again in each iteration, because "safety analysis also improves when it is
  done iteratively and for small increments" [8].
- Two backlogs, "one functional product backlog, which is typical for Scrum projects, and one
  safety product backlog, which is used to handle safety requirements", with links that show which
  safety requirements each functional item affects [8].
- The assessor from the first day. Their main conclusion: "the most important thing to do is to
  involve the assessor in the project from day one" [8], because "different assessors have
  different opinions of what should count as proof of compliance" [8]. They also warn that
  this must be done so that "we do not hold the assessor hostage to our choice of development
  process", and suggest one assessor as a sparring partner during the project and another one for
  certification [8].

SINTEF, the method's owner, reports on its own page that it discussed the approach with several
certification bodies, and that "in 2015, they informed us that they would accept such an
approach" [10]. It also reports that in some projects "the manufacturer issued the safety case
up to six months after writing the last code", and that it then made the safety case part of the
certification process in The Agile Safety Case of 2018 [10].

**The V-Modell XT Bund.** The German federal reference model for system development projects in
the federal administration, version 2.3 of 2019, is a V-model built for repeated passes [9]:

- Part A.3: "Das V-Modell ist dabei auf ein iteratives Vorgehen ausgelegt, bei dem der
  Entwicklungszyklus mehrmals durchlaufen wird", in English: the V-Modell is designed for an
  iterative approach, in which the development cycle is run through several times [9]. The same
  part sets the frame: "Es fordert an diesen Entscheidungspunkten eine Fortschrittskontrolle und
  eine Entscheidung über den weiteren Projektverlauf", in English: at these decision points
  (milestones) it requires a progress check and a decision on how the project goes on [9].
- Part A.4: "Agile Vorgehensweisen wie Scrum oder Kanban können je nach Projektkontext gut mit dem
  V-Modell kombiniert werden", in English: agile approaches such as Scrum or Kanban can, depending
  on the project context, be combined well with the V-Modell [9].
- Part B.1.3.3: with an agile method, the client steers the contractor "auf Basis von Sprints
  anstelle der Iterationen", in English on the basis of sprints instead of iterations [9].
- Its Scrum parts follow the 2017 Scrum Guide, which the document includes under that guide's
  licence [9]. The current guide is the subject of [scrum.md](scrum.md).

The rules of the default:

- **Before the first sprint, or in a Kanban flow before the first refinement
  ([meetings.md](../project-management/meetings.md) section 9), agree with the assessor or the
  regulatory lead what evidence each sprint, or each period between two regular retrospectives in
  a Kanban flow, and each milestone must leave, and put those documents
  into the backlog as items.** Why:
  assessors differ on what counts as proof, and the SINTEF authors hold that asking early lets the
  team write every document the assessor needs and none that is not needed, each one a backlog
  item like any other requirement [8].
- **Keep safety requirements in a backlog of their own, and link each functional item to the
  safety requirements it affects.** Why: the two kinds change at different rates, and the links
  show which safety requirements a change to a functional item touches [8].
- **Run the system-level hazard and safety analysis in the frame, and analyse each increment again
  in its sprint, or in a Kanban flow at the refinement when the Backlog runs low
  ([meetings.md](../project-management/meetings.md) section 9).** Why: that is how SafeScrum
  splits the work [8]. The hazard analysis is
  about harm the product can do; the project's risk register in
  [risks.md](../project-management/risks.md) holds risks to the project's objectives and does not
  replace it.
- **Write the design, verification and validation records of each sprint in that sprint, and in a
  Kanban flow those of each period between two regular retrospectives
  ([meetings.md](../project-management/meetings.md) section 9) in that period.** Why:
  FDA says that records written late could raise concerns about the developer's control of the
  design process [3], and SINTEF reports safety cases issued up to six months after the last
  code [10].
- **Date each design, verification and validation record on the day it is written. Never back-date
  a record, and never present a record written later as one made at the time.** This holds for
  people and agents alike. Why: FDA says that documentation written later "could raise concerns
  regarding whether a developer has adequate control of their design process" [3], and a
  back-dated record hides that a record was written late.
- **Put the regulatory milestones into the plan as milestones, and let the sprints, or the work of
  a Kanban flow, feed them.** How
  a fixed date becomes a milestone is [life-cycle.md](../project-management/life-cycle.md)
  section 4. Why: each decision point needs its evidence ready, and the V-Modell XT asks for a
  progress check and a decision at each one [9].

Check: at each sprint review, or at each regular retrospective in a Kanban flow
([meetings.md](../project-management/meetings.md) section 9), open the design records (the
design history file or the project's equivalent) and find the changes of that period there, dated
in that period. A change with no record of its period gets one now, dated the day it is written and
marked late; never back-date (the dating rule above). That path is this practice's own reading of
FDA's note that records written later "could raise concerns" [3].

## 3. Fixed-price and fixed-scope contracts

This section holds when a contract fixes the price, the date or the scope of the work. What matters
for agile work is the scope, as Fowler puts it: "However this doesn't mean you can't come up with a
fixed price agile contract, what it really means is that you can't come up with a fixed scope
contract" [2]. His alternative fixes the budget and the date and lets the parties choose the features:
"we have $x to spend and we need a release on 1 Dec. We'll collaborate together to come up with the
best set of features to go live with on that date" [2].

Arbogast, Larman and Vodde hold that "Fixed-price, fixed-scope—and worse, with fixed
duration—contracts and projects tend toward lose-lose situations for both the customer and
supplier", in which "customers often do not get what they really need, and suppliers can easily
lose money" [11]. They do not call it impossible: "First, it is possible; Valtech India and
other agile outsourcing suppliers have done so (because of market demand)—though this is their
least-favorite model" [11]. They hold that "Scrum can be used with a fixed-content Release
Backlog" [11], and for pricing they recommend time and materials: "Variations of time and
materials (T&M) make for good agile-project pricing models: simple, straightforward. Recommended"
[11]. Their variants that limit the customer's exposure include a cap per iteration and a cap
per project or release [11].

Sutherland posted, in 2008, clauses from an open-source agile contract that a team was working on
in the Open Plans Agile Contract Project [12]. They are a proposal on a blog, not a legal text:

- Early termination: "The Customer may terminate the contract at the end of any Sprint" [12]. The
  customer then pays "20% of the remaining contract value", and the company "commits to delivering
  80% of the project scope as high quality by the agreed upon delivery date" [12].
- Change for free: "New features may be added for free at Sprint boundaries if items of equal scope
  are removed from the contract" [12].
- Both clauses hold only while the customer takes part in the Scrum team; otherwise "the contract
  shall revert to a time and materials billing" [12]. In the same post, Jens Ostergaard adds: "I
  would however be cautious starting this with a new company, and have some kind of risk sharing"
  [12].

For Scrum work that a German federal client contracts out, the V-Modell XT Bund says that the
requirements are fixed "nicht zu Projektbeginn, sondern im Projektverlauf auf Grundlage
regelmäßiger Zwischenergebnisse", in English not at the start of the project but during it, based
on regular interim results [9]. The client writes a rough requirements concept as the basis
for the tender, and its Product Owner is an employee of the client who works in the contractor's
project (part B.2.2.6) [9].

- **Before you agree to a contract, find out which of price, date and scope it fixes.** Why: Fowler
  holds that only a fixed scope conflicts with agile work [2], so the rules for a fixed scope below
  apply only when the scope is fixed.
- **As the default, propose a contract that fixes the budget and the date and lets the scope move,
  or a capped variant of time and materials.** Why: Fowler describes the first as the fixed-price
  agile contract [2], and the Primer's authors recommend the second [11].
- **When the scope must stay fixed, run Scrum with a fixed-content release backlog, and follow the
  Primer's keys:** a detailed analysis of the requirements up front with acceptance tests, no
  change of scope except swaps of equal effort, a larger margin for the risk, and experienced
  people [11]. Why: the authors hold that "the last thing you want to do with an FPFS project is
  make matters even worse by applying a traditional sequential development approach" [11].
- **Write the flexibility into the contract's clauses:** swapping a requirement for a new one of
  equal effort, changing the order in which the fixed requirements are built, and an early exit.
  Why: the Primer lists the first two as low-risk flexibility in a fixed-price, fixed-scope project
  with Scrum, and holds that "this flexibility can and should be expressed in clauses of an FPFS
  contract" [11]; Sutherland's early termination clause is the third [12].
- **When a clause depends on the customer's participation, name the customer's Product Owner in
  the contract.** Why: Sutherland's clauses fall back to time and materials without that
  participation [12], and the V-Modell XT Bund gives the role to an employee of the client
  [9].
- **Plan the fixed parts as milestones, and change a fixed scope only through change control.** The
  first is [life-cycle.md](../project-management/life-cycle.md) section 4, the second
  [project-plan.md](../project-management/project-plan.md) section 4.

## 4. Common mistakes

| Mistake | What it costs | Fix |
|---|---|---|
| Believing that the regulator demands a waterfall | A process nobody asked for: the FDA texts read recommend no model and name the Agile model among the examples [1], [3] | Read the regulator's own text, section 1 |
| Design documentation written after the work, for the submission | FDA: it "could raise concerns regarding whether a developer has adequate control of their design process" [3]; SINTEF saw safety cases up to six months after the last code [10] | Records in each sprint, section 2 |
| The assessor first sees the process at the end | Assessors differ on what counts as proof [8], and the team learns late which documents are missing | The assessor from day one, section 2 |
| The Computer Software Assurance guidance read as FDA's word on developing device software | Its scope leaves device software out [4] | The 2002 and 2023 guidances, section 1 |
| A fixed price read as a fixed scope | Fowler notes that many people believe a fixed-price contract cannot be agile [2]; the team refuses a contract it could run, or signs a scope it cannot change | Find out what the contract fixes, section 3 |
| A fixed-price, fixed-scope project run sequentially | The Primer's authors hold that it makes matters worse [11] | Scrum with a fixed-content release backlog, section 3 |

## 5. Where the rules stop holding

- **Low risk.** The FDA ties the approach, the techniques and the effort to the intended use and
  the safety risk [1]. Size the frame of section 2 by the risk of the software; do not copy it
  whole onto a function of low risk.
- **What the frame costs.** A second backlog, records in every sprint, and an assessor's time from
  the first day. Where the assessor must stay independent, the SINTEF authors suggest two
  assessors, one as a sparring partner and one for certification [8], which costs more again.
- **A fixed scope that cannot be avoided.** The Primer's authors note that the model is often
  "imposed on them—perhaps by the Legal or Finance arms" [11]. Then the fixed-scope rules of
  section 3 hold, and its default contract does not.
- **Not covered yet.** The research for this file did not read these texts, so they carry no
  rule here:
  - What the text of IEC 62304 asks of a life-cycle model; only the webstore's description was
    read [7].
  - ISO 26262-6 for road vehicles and DO-178C for airborne software: their texts were not read.
  - IEC 61508, IEC 60880 and EN 50128, beyond what the SINTEF authors write about them.
  - The text of AAMI TIR45:2023; only FDA's recognition entry was read [5].
  - The text of ISO 13485:2016, which the QMSR incorporates [6].
  - Regulators other than the US FDA.

## 6. Alternatives considered

- **A sequential model for the whole project, because the work is regulated.** Not taken: the FDA
  texts read recommend no model [1], [3], and both SafeScrum and the V-Modell XT combine
  Scrum with a plan-driven frame [8], [9].
- **An agile loop with no plan-driven frame.** Not taken: the FDA asks for an established model
  that covers the software from birth to retirement [1] and for design records kept in step
  [3], SafeScrum keeps the system-level safety analysis outside the loop [8], and the
  research found no account of safety-critical work without such a frame.
- **The Computer Software Assurance guidance as FDA's newest word on software development.** Not
  taken: it covers production and quality-system software, and leaves device software out [4].
- **Sutherland's clauses as the default contract.** Not taken as the default: they are a 2008
  proposal from a project still at work, and the same post advises caution with a new company
  [12]. Section 3 shows them as one option.
- **Fixed-price, fixed-scope as a normal agile contract.** Not taken as the default: its authors
  call it a road to "lose-lose situations" [11]. Section 3 keeps it as possible, with its keys.

## 7. Adoption in a running project

The answer is **new and touched code** ([refactoring.md](../refactoring/refactoring.md)
section 7), read for a process: a project under way keeps the life-cycle model it established and
moves to the loop of section 2 at a point its own plan names, such as the next release or the next
project. Before the change, ask the assessor the SINTEF authors' question, "If we use approach X
here, will this be accepted?" [8], and record the changed model in the plan (section 1). A
contract already signed keeps its terms; section 3 applies to the next contract, or to a change
agreed under the change clause of the current one.

## 8. How an agent applies it

The project's `CLAUDE.md` routes an agent here with the line in [README.md](README.md), "How to
adopt". What an agent does in this work, by this practice's own rules:

- **Name the text and the edition behind every claim about what a regulator or a standard asks,**
  and say "not read" for the standards that section 5 lists. A requirement stated from memory is
  the hearsay that section 1 warns about.
- **Write design and verification records for the work of the current sprint, dated when they are
  written.** The ban on back-dating, which holds for people and agents alike, is the dating rule
  of section 2.
- **Draft contract clauses only as a draft for a lawyer,** with the source of each clause.

The research found no study of the mistakes agents make in regulated work.

## 9. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] U.S. Food and Drug Administration — General Principles of Software Validation; Final Guidance for Industry and FDA Staff, issued 2002-01-11, with FDA's later notes on the QMSR and on section 6 — https://www.fda.gov/media/73141/download
- [2] Martin Fowler — FixedPrice (martinfowler.com, 2003; opinion) — https://www.martinfowler.com/bliki/FixedPrice.html
- [3] U.S. Food and Drug Administration — Content of Premarket Submissions for Device Software Functions, issued 2023-06-14 — https://www.fda.gov/media/153781/download
- [4] U.S. Food and Drug Administration — Computer Software Assurance for Production and Quality Management System Software, issued 2026-02-03 — https://www.fda.gov/media/188844/download
- [5] U.S. Food and Drug Administration — Recognized Consensus Standards: AAMI TIR45:2023, recognition number 13-143 — https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfstandards/detail.cfm?standard__identification_no=46295
- [6] U.S. Food and Drug Administration — Quality Management System Regulation (QMSR) — https://www.fda.gov/medical-devices/postmarket-requirements-devices/quality-management-system-regulation-qmsr
- [7] IEC — IEC 62304:2006+AMD1:2015 CSV, Medical device software - Software life cycle processes, edition 1.1 (webstore page) — https://webstore.iec.ch/en/publication/22794
- [8] Tor Stålhane, Thor Myklebust and Geir Kjetil Hanssen — Safety standards and Scrum: A synopsis of three standards (SINTEF, 2013; research) — https://www.sintef.no/globalassets/_div.-opprydding-2023/safety-standards-and-scrum_may2013.pdf
- [9] Informationstechnikzentrum Bund — V-Modell XT Bund, version 2.3 (in German) — https://www.itzbund.de/static/download/Produkte/VMXT/V-Modell-XT-Bund-2.3.pdf
- [10] SINTEF — SafeScrum (sintef.no, no date; case, by the method's authors) — https://www.sintef.no/en/digital/departments/department-of-software-engineering-safety-and-security/research-group-system-safety/safescrum/
- [11] Tom Arbogast, Craig Larman and Bas Vodde — Agile Contracts Primer, version 5 (agilecontracts.org, 2012; opinion) — https://agilecontracts.org/agile_contracts_primer.pdf
- [12] Jeff Sutherland — Agile Contracts: Money for Nothing and Your Change for Free (Scrum Log, 2008; opinion) — http://jeffsutherland.com/scrum/2008/10/agile-contracts-money-for-nothing-and.html
