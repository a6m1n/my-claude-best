# Extreme Programming (XP) and its engineering practices

What Extreme Programming is, the problem it solves, when it fits a team and when it is too much,
how a team starts with it, how it works inside Scrum, and what research says about two of its
practices. Read it when a team wants to try XP or one of its practices, when a Scrum team asks how
to build the work, or when someone cites a study on pair programming or test-driven development.
The rules hold in any language; test-first work in Python is
[what-to-test.md](../../python/testing/what-to-test.md) section 4.

**Navigation**

- [1. What XP is and the problem it solves](#1-what-xp-is-and-the-problem-it-solves)
- [2. When it fits and when it is too much](#2-when-it-fits-and-when-it-is-too-much)
- [3. How a team starts](#3-how-a-team-starts)
- [4. XP with Scrum](#4-xp-with-scrum)
- [5. What the evidence says on single practices](#5-what-the-evidence-says-on-single-practices)
- [6. Common mistakes](#6-common-mistakes)
- [7. Alternatives considered](#7-alternatives-considered)
- [8. Sources](#8-sources)

**When you do not need this file.** XP "does not address project portfolio management, financial
justification of projects, operations, marketing, or sales" [1], so a team that needs rules for
those reads other practices. Don Wells, on his XP site, holds that "you can not use XP on a project
with a huge staff", and makes automated unit and functional tests a requirement [4]. A team that
wants one fix, such as fewer integration bugs, does not need the whole of XP: Kent Beck offers its
practices as ones "you can add to your bag of tricks" [1], and section 3 says how to start with
one. To pick an approach for a deliverable, read
[life-cycle.md](../project-management/life-cycle.md) section 4; to decide who picks, read
[choosing-an-approach.md](choosing-an-approach.md).

## 1. What XP is and the problem it solves

Kent Beck and Cynthia Andres, in the second edition of *Extreme Programming Explained* (2004),
describe XP as "a software development discipline that addresses risk at all levels of the
development process" [1]. The risks they name are a schedule that slips, a project that is
cancelled, a system that decays, too many defects, a business that is misunderstood or that
changes, features nobody needs, and staff who leave [1]. XP includes a philosophy "based on the
values of communication, feedback, simplicity, courage, and respect", a body of practices, a set
of principles and a community [1]. It is also a change in how people work together: "Extreme
Programming (XP) is about social change" [1]. Only the publisher's free sample pages of the book
were read: the contents, the Preface and chapter 1.

The Agile Alliance glossary calls XP "the most specific of the agile frameworks regarding
appropriate engineering practices for software development" [2].

The book's table of contents lists five values, 14 principles (Humanity, Economics, Mutual
Benefit, Self-Similarity, Improvement, Diversity, Reflection, Flow, Opportunity, Redundancy,
Failure, Quality, Baby Steps, Accepted Responsibility), and two kinds of practices [1]:

| Kind | The practices, as the contents list them [1] | What the kind means |
|---|---|---|
| Primary (13) | Sit Together, Whole Team, Informative Workspace, Energized Work, Pair Programming, Stories, Weekly Cycle, Quarterly Cycle, Slack, Ten-Minute Build, Continuous Integration, Test-First Programming, Incremental Design | Bill Wake, reviewing the book: "generally safe to introduce one at a time, or in any order" [3] |
| Corollary (11) | Real Customer Involvement, Incremental Deployment, Team Continuity, Shrinking Teams, Root-Cause Analysis, Shared Code, Code and Tests, Single Code Base, Daily Deployment, Negotiated Scope Contract, Pay-Per-Use | Wake: "riskier: they require the support of other practices" [3] |

The one rule: **take XP's practices as tools the team picks for the problems it has, one primary
practice at a time, and judge them by what they change. Never impose them on a team, and never
check a team against the list as if it were a contract.**

Why it holds the rest together:

- Beck writes in the Preface that critics of the first edition "complained that it tries to force
  them to program in a certain way", and that the second edition gives up that aim: "I present
  proven practices you can add to your bag of tricks" [1].
- Beck and Andres: "Every team does XP differently with varying degrees of success" [1]. A list
  checked like a contract hides that.
- The two kinds of practice differ in risk: a primary practice can start alone, a corollary one
  needs others in place first [3].

What it leaves out on purpose, and where that lives:

- Who chooses a team's approach, and the evidence on approaches as a whole:
  [choosing-an-approach.md](choosing-an-approach.md). Picking predictive, adaptive or hybrid for a
  deliverable, and Scrum or Kanban: [life-cycle.md](../project-management/life-cycle.md) section 4.
- Keeping Scrum whole and what changing it costs: [scrum.md](scrum.md).
- XP's Stories: the story form and the Definition of Done are
  [tickets.md](../project-management/tickets.md) section 2.
- XP's Continuous Integration, Incremental Deployment and Daily Deployment: the daily merge to
  main and continuous delivery are [release.md](../project-management/release.md) section 5, and
  merging each pull request within a day is [tickets.md](../project-management/tickets.md)
  section 4. XP's Ten-Minute Build, and the pipelines that build and deploy, are
  [ci-cd/README.md](../ci-cd/README.md).
- XP's Test-First Programming in Python: the order of the steps and its evidence are
  [what-to-test.md](../../python/testing/what-to-test.md) section 4.
- Restructuring code that already exists: [refactoring.md](../refactoring/refactoring.md).
- Test-first work and small steps when AI agents write the code: [ai-agents.md](ai-agents.md).
- Work past one team: [scaling.md](scaling.md). Safety-critical and regulated work:
  [regulated-work.md](regulated-work.md).
- Security: there are no known security impacts of the practices in this file. Wake reads the book
  as saying that safety- and security-critical software may need some modest changes to XP
  (section 2).

Not covered yet, because the book's pages past chapter 1 are not free and were not read: the text
of the values, principles and practices; chapter 8, "Getting Started"; chapter 15, "Scaling XP",
which says how the practices change with many people; and the section "When You Shouldn't Use XP"
in chapter 20 [1]. No meta-analysis of pair programming newer than 2009 was read (section 5).

## 2. When it fits and when it is too much

The book is XP's own text and leads here. Wells's list is older, from his site's page of 1999, and
follows with its date.

What Beck and Andres say:

- **Team size.** The first edition defined XP for "small-to-medium-sized teams"; the second says
  that definition "doesn't tell the whole story" [1]. Now: "XP can work with teams of any size",
  and "The practices need to be augmented and altered when many people are involved" [1]. How they
  change is in chapter 15, which was not read; [scaling.md](scaling.md) covers work past one team.
- **Requirements.** "XP adapts to vague or rapidly changing requirements", and "teams have also
  successfully used XP where requirements don't seem volatile, like porting projects" [1].
- **What XP assumes of the people.** "XP assumes that you want to work together. XP assumes that
  change can be made inexpensive using this method" [1]. The book also assumes that people see
  themselves as part of a team, want to grow and are willing to change [1]. A team where these do
  not hold lacks what XP is built on; that reading is this file's own.

Wells's signs that XP fits [4]:

| Sign | Wells's words |
|---|---|
| The requirements change | "dynamically changing requirements is the only constant. This is when XP will succeed while other methodologies do not." |
| A fixed date and new technology | "If your customers need a new system by a specific date the risk is high. If that system is a new challenge for your software group the risk is even greater." |
| A small team with its customers and managers | "Between 2 and 12, though larger projects of 30 have reported success", with managers and customers "all working together elbow to elbow" |
| The code can be tested automatically | "You must be able to create automated unit and functional tests." |

When it is too much, or does not fit:

- **A huge staff.** Wells: "you can not use XP on a project with a huge staff", and on projects with
  changing requirements or high risk "you may find that a small team of XP programmers will be more
  effective than a large team anyway" [4]. The book, written later, keeps XP for any size but
  with changed practices [1]; this file follows the book and keeps Wells's warning (section 7).
- **Code that cannot be tested automatically.** Wells: "some domains will be disqualified by this
  requirement", though he names none [4].
- **Safety- and security-critical software.** Wake, summing up what the book says on scaling:
  "Safety- and security-critical software may require some modest changes" [3]. What such work
  requires is [regulated-work.md](regulated-work.md).
- **The book's own list.** Chapter 20 has a section "When You Shouldn't Use XP" [1]. It was not
  read, so this file has no rule from it.

The simpler way: when one problem hurts, take the one practice that answers it (section 3) and
leave the rest. Ron Jeffries holds that developers "should detach their thinking from any
particular named 'Agile' method" and use "practices such as, but not limited to, those of Extreme
Programming" [6].

Where this file's rules stop holding:

- **One primary practice at a time** is this file's default, not the book's rule. Beck leaves the
  pace to the reader: a team can start "one toe at a time" or with "the cannonball", and "Only you
  can decide which is right for you" [1]. A team that starts many practices at once still holds the
  corollary ones back until their support is in place (section 3).
- **Pairing** costs effort; section 5 says on which tasks the trade pays.
- **Section 4** holds only for a team that runs Scrum.

## 3. How a team starts

- **Let the team choose XP, and never impose it.** Who chooses is
  [choosing-an-approach.md](choosing-an-approach.md). Beck's Preface turns away from the first
  edition's aim to make people work one way, "Relinquishing the illusion of control of other
  people's behavior" [1]. Jeffries holds that a team that may choose should start with something
  like XP: "If you do get a chance to choose, I'd recommend that you start with something like
  Extreme Programming", because it holds the planning and feedback loops and "the basic technical
  practices you need" [6].
- **When you cannot choose for the team, start with your own work.** Beck: "You can always start
  improving with yourself" [1]. Wake sums up the book's advice: "Change yourself first, then offer
  the fruit of that to others" [3].
- **Start with the problem the team feels most, and add the XP practice that answers it.** Wells:
  projects usually come to XP "only after the project is in trouble", and then the way to start is
  to "take a good long look at your current software methodology and figure out what is slowing
  you down. Add XP to this problem first" [5]. Wake: "Two types of groups find it easiest to start
  XP: those aligned with its values, and those in pain" [3]. On a new project Wells starts with
  stories and short trial solutions for the risky parts, then plans the release with customers,
  developers and managers [5].
- **Add primary practices one at a time, and hold a corollary practice until the practices it rests
  on run.** Wake: primary practices "are ones that are generally safe to introduce one at a time,
  or in any order", and corollary practices "require the support of other practices" [3]. He also
  reports that "Beck advises not changing too fast" [3].

Wells's first practice for each problem, with its name in the second edition [1], [3], [5]:

| The problem the team feels most | What Wells tries first [5] | The practice in the second edition |
|---|---|---|
| The requirements document becomes useless part way through | Write user stories with the customers | Stories (primary) [1] |
| Changing requirements make the team redo the schedule again and again | A simpler release planning meeting every few iterations, short iterations, and tasks planned just in time; user stories first | Quarterly Cycle and Weekly Cycle (primary), which Wake says cover the first edition's Planning Game [3] |
| Many bugs in production | Automated acceptance tests, kept for regression testing | Test-First Programming (primary) at the customer's level: Wake reads the book as "Use test-first, at both levels" [3] |
| Integration bugs | Automated unit tests, all passing before new code goes into the repository | Test-First Programming (primary) [3]; the daily merge is [release.md](../project-management/release.md) section 5 |
| One or two developers are a bottleneck because they own the core classes | Collective code ownership: "(You will also need unit tests.)" [5] | Shared Code, a corollary practice [1], [3] |

The table is sound because each row starts from a problem the team can name, and the last row
shows the corollary rule at work: Wells asks for unit tests before shared ownership, and the
second edition files Shared Code as a corollary practice. Wells writes in the first edition's
words; the right-hand column maps them by Wake's comparison of the two editions. The book's
contents list a chapter 8, "Getting Started" [1], which was not read.

In a project that already runs, the same order holds: start where it hurts. How to change code
that has no tests yet is [refactoring.md](../refactoring/refactoring.md) section 3.

## 4. XP with Scrum

This section holds when a team runs Scrum, or is about to.

Martin Fowler holds that Scrum "deliberately omits any technical practices, in contrast to (for
example) Extreme Programming", and reports what the "prominent Scrummers" he has listened to say
of those practices: "They don't mandate what those technical practices should be, but you do need
them" [7]. Henrik Kniberg puts the gap this way: "Scrum leaves a hole in the middle, i.e. how the
team should do their daily work, which XP fills in quite nicely" [8].

- **When a team adopts Scrum, choose its technical practices in the same step, and start from
  XP's.** Fowler: "If you're looking to introduce scrum, make sure you pay good attention to
  technical practices", and "the XP practices make a good starting point - and are certainly going
  to be much better than doing nothing at all" [7]. Without them, he writes, "After a while
  progress is slow because the code base is a mess" [7]. Kniberg adds why XP suits a Scrum team:
  "Scrum places fairly strict requirements (such as delivering working tested software every
  iteration) making XP a natural choice for many teams" [8].
- **Use XP for how the team builds the work, the part Scrum leaves open.** Kniberg sees Scrum as
  "the interface between the team and the stakeholders", and finds one small overlap with XP,
  daily meetings, "which is no problem really" [8]. How far a Scrum team may change Scrum itself
  is [scrum.md](scrum.md)'s rule; this file sets none.

Check: at a retrospective or any review of the project, name the technical practices the team
runs. Fowler: "any kind of project review should include examining what kinds of technical
practices are present" [7]. An empty answer is the first mistake in section 6.

## 5. What the evidence says on single practices

Both studies below were read in their abstracts only. The kind of each is not confirmed, so this
file reports what the abstracts say and does not treat them as settled research.

**Pair programming.** The abstract of Jo E. Hannay, Tore Dybå, Erik Arisholm and Dag I. K.
Sjøberg's 2009 meta-analysis of experiments on pair versus solo programming reports "a small
significant positive overall effect of pair programming on quality, a medium significant positive
overall effect on duration, and a medium significant negative overall effect on effort" [9]. It
adds that "between-study variance is significant, and there are signs of publication bias among
published studies on pair programming" [9]. By task, pairs were faster than one person on simple
tasks at "noticeably lower quality", and gave higher quality on complex tasks at "considerably
greater effort" [9]. The abstract does not say how many experiments it pooled, or whether the
programmers were students or professionals. The study is from 2009, and no later meta-analysis
was read.

- **Decide where to pair by the task, and do not expect pairing to save effort.** On a complex task
  the abstract reports higher quality for more effort; on a simple one, a faster result of lower
  quality [9]. That reading of the abstract is this file's own.

**Test-driven development.** Fernando Uyaguari, Silvia T. Acuña, John W. Castro, Oscar Dieste and
Natalia Juristo compared eight systematic reviews of test-driven development, in a tertiary study
published in 2025 [10]. Its abstract reports that the reviews share few studies: "Only three per
cent of the primary studies are included in all eight analysed SLRs" [10]. It finds that
"Conclusions regarding external quality and productivity may vary across the SLRs on TDD", and
that the review authors' criteria on the consistency of evidence may influence those conclusions
[10].

- **Do not cite one review of TDD as the answer on quality or productivity; name the review and
  how it picked its studies.** The reviews draw on different studies, and their conclusions may
  differ [10]. For Python, the order of test-first steps and its evidence are
  [what-to-test.md](../../python/testing/what-to-test.md) section 4.

The evidence on approaches as a whole, Scrum, XP or hybrid, is in
[choosing-an-approach.md](choosing-an-approach.md).

## 6. Common mistakes

- **Scrum without engineering practices**, which Fowler calls Flaccid Scrum [7]:
  [scrum.md](scrum.md) section 6; the fix is section 4.
- **Every practice at once.** It looks like a team that switches on all 24 practices in one go,
  the corollary ones included. People make it because the first edition read as "do all 12
  practices", which Wake contrasts with the second [3]. The cost: corollary practices start before
  the practices they rest on are in place, and they "require the support of other practices" [3].
  The fix is section 3: one primary practice at a time, for the problem the team feels most.
- **The practice list as a contract.** It looks like a manager, an auditor or the team itself
  ticking the practices off one by one to decide whether the team does XP, or a lead who imposes
  the list. People make it because, as Beck and Andres write, methodology "is often interpreted to
  mean 'a set of rules to follow that guarantee success.'" [1]. The cost is a process that does not
  fit the team: "Methodologies don't work like programs. People aren't computers" [1]. The fix is
  to judge by results:
  Jeffries would "ask for results, not a specific process" [6], and Wake quotes the book's chapter
  on purity: "The goal is successful and satisfying relationships and projects, not membership in
  the XP club" [3].

## 7. Alternatives considered

- **XP only for small teams.** Wells: "you can not use XP on a project with a huge staff" [4]. Not
  taken as the rule: the book is XP's own text, written later, and says XP works at any size with
  changed practices [1]. Wells's limit stays as the warning in section 2, because the book's
  chapter on how the practices change was not read.
- **Aim for the full set of practices.** Wells holds that, once the first fixes work, a team should
  "add the remaining practices as you can", that "at some point between having a few XP rules and
  all of the XP rules it will take some persistence to make it work", and that "There is a synergy
  between the rules that is hard to understand until you have been fully immersed" [5]. Not this
  file's default: the second edition offers its practices as ones "you can add to your bag of
  tricks" [1]. A team that does aim for all of them should expect the climb Wells describes.
- **XP as the thing that fills Scrum's gap.** Kniberg holds that XP "fills in quite nicely" what
  Scrum leaves open [8]; Fowler calls the XP practices "a good starting point" [7]. Section 4
  follows Fowler's narrower claim: the team picks its technical practices and starts from XP's,
  which keeps the choice with the team, as Beck's Preface does [1].
- **The Agile Alliance glossary's fit list.** The glossary repeats Wells's signs of fit in shorter
  words of its own [2]. Section 2 quotes Wells's page instead, because the glossary's words say
  more than his page does about where the team sits; Wells writes "elbow to elbow" [4].

## 8. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Kent Beck with Cynthia Andres — Extreme Programming Explained: Embrace Change, Second Edition, the publisher's free sample pages: contents, Preface and chapter 1 (Pearson Education, 2004; opinion) — https://ptgmedia.pearsoncmg.com/images/9780321278654/samplepages/9780321278654.pdf — checked 2026-10-30
- [2] Agile Alliance — What is Extreme Programming (XP)? (Agile Alliance glossary, no date; opinion) — https://agilealliance.org/glossary/xp/ — checked 2026-10-30
- [3] Bill Wake — Overview of "Extreme Programming Explained, 2/e" (XP123, 2005; opinion) — https://xp123.com/review-extreme-programming-explained-2e/ — checked 2026-10-30
- [4] Don Wells — When should Extreme Programming be Used? (extremeprogramming.org, 1999; opinion) — http://www.extremeprogramming.org/when.html — checked 2026-10-30
- [5] Don Wells — How do I start this XP thing? (extremeprogramming.org, 1999; opinion) — http://www.extremeprogramming.org/start.html — checked 2026-10-30
- [6] Ron Jeffries — Developers Should Abandon Agile (ronjeffries.com, 2018; opinion) — https://ronjeffries.com/articles/018-01ff/abandon-1/ — checked 2026-10-30
- [7] Martin Fowler — Flaccid Scrum (martinfowler.com, 2009; opinion) — https://www.martinfowler.com/bliki/FlaccidScrum.html — checked 2026-10-30
- [8] Henrik Kniberg — Scrum and XP fit together (Crisp's Blog, 2007; opinion) — https://blog.crisp.se/2007/10/13/henrikkniberg/1192249140000 — checked 2026-10-30
- [9] Jo E. Hannay, Tore Dybå, Erik Arisholm and Dag I. K. Sjøberg — The effectiveness of pair programming: A meta-analysis (Information and Software Technology, 2009; kind not confirmed) — https://doi.org/10.1016/j.infsof.2009.02.001 — checked 2026-10-30
- [10] Fernando Uyaguari, Silvia T. Acuña, John W. Castro, Oscar Dieste and Natalia Juristo — Reliability of systematic literature reviews on test-driven development (Information and Software Technology, 2025; kind not confirmed) — https://doi.org/10.1016/j.infsof.2025.107762 — checked 2026-10-30
