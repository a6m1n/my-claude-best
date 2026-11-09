# The agile values and principles

What the Manifesto for Agile Software Development says, what it is and what it is not, when its
values fit a team and when they do not, and how a team starts from them without buying a brand.
Read it when a team wants to work in an agile way, when someone offers to make a team "agile", or
when a team that runs a named method asks whether its work still follows the values.

**Navigation**

- [1. What the Manifesto is](#1-what-the-manifesto-is)
- [2. When it fits and when not](#2-when-it-fits-and-when-not)
- [3. Agility, not a brand](#3-agility-not-a-brand)
- [4. How a team starts from the values](#4-how-a-team-starts-from-the-values)
- [5. Common mistakes](#5-common-mistakes)
- [6. Sources](#6-sources)

**When you do not need this file.** To pick a predictive, adaptive or hybrid approach for a
deliverable, or Scrum or Kanban for its adaptive part, read
[life-cycle.md](../project-management/life-cycle.md) section 4, which makes that pick. To decide
who picks, read [choosing-an-approach.md](choosing-an-approach.md). A team that does not want to
work in an agile way gets little from the rest of this file; section 2 says why.

## 1. What the Manifesto is

In February 2001, at Snowbird in Utah, "seventeen people met" and wrote the Manifesto [3]. Jim
Highsmith's history of the meeting says who came: "Representatives from Extreme Programming,
SCRUM, DSDM, Adaptive Software Development, Crystal, Feature-Driven Development, Pragmatic
Programming, and others sympathetic to the need for an alternative to documentation driven,
heavyweight software development processes convened" [3]. He calls the group "independent
thinkers about software development, and sometimes competitors to each other" [3].

The Manifesto states four values [1]:

- Individuals and interactions over processes and tools
- Working software over comprehensive documentation
- Customer collaboration over contract negotiation
- Responding to change over following a plan

Its closing line keeps the right side: "That is, while there is value in the items on the right, we
value the items on the left more" [1]. The twelve principles behind it, in short [2]:

1. Satisfy the customer through early and continuous delivery of valuable software.
2. Welcome changing requirements, even late in development.
3. Deliver working software often, every few weeks to every few months, the shorter the better.
4. Business people and developers work together daily.
5. Motivated people, the support they need, and trust: quoted and applied in
   [principles.md](../project-management/principles.md) section 1.
6. Face-to-face conversation is the best way to pass information to and within the team.
7. Working software is the primary measure of progress.
8. A pace the team can keep: quoted and applied in
   [principles.md](../project-management/principles.md) section 3.
9. Continuous attention to technical excellence and good design.
10. Simplicity, "the art of maximizing the amount of work not done" [2].
11. The best architectures, requirements and designs come from self-organizing teams.
12. At regular intervals the team reflects and adjusts how it works.

Neither page names a method, a meeting or a tool [1], [2]. So a team that takes the values still
has to pick how it works. Highsmith holds that the rise of interest in agile methods, and the
criticism of them, "is about the mushy stuff of values and culture" [3]. He also writes: "The Agile
movement is not anti-methodology, in fact, many of us want to restore credibility to the word
methodology" [3].

The one rule of this file: **the four values and the twelve principles are the test of a way of
working; a method, a label or a tool counts as agile only as far as the work it shapes shows
them.** Fowler: "It's the values and principles that count" [6]. Sections 3 and 5 show what goes
wrong when a team takes the name for the work.

What this file leaves out, and where it lives:

- Who chooses the approach and the team's process:
  [choosing-an-approach.md](choosing-an-approach.md).
- The pick of predictive, adaptive or hybrid for each deliverable, and of Scrum or Kanban:
  [life-cycle.md](../project-management/life-cycle.md) section 4.
- The named methods: [scrum.md](scrum.md), [kanban.md](kanban.md),
  [extreme-programming.md](extreme-programming.md),
  [lean-software-development.md](lean-software-development.md); how teams combine them:
  [combining-approaches.md](combining-approaches.md).
- Whether the approaches improve outcomes: [choosing-an-approach.md](choosing-an-approach.md).
- Security and privacy: there are no known security impacts of the values and principles in this
  file, and they touch no personal data.

Not covered yet: a way to measure how far a team follows the values. No source read for this file
gives one.

## 2. When it fits and when not

The Manifesto, the principles and the history page name no case where the values do not fit [1],
[2], [3]. The cases below come from the authors' later writing, and they are their views. Fowler
sets the frame: "there is no one-size-fits-all in software development. Even the agile advocates
wouldn't say that agile is necessarily the best thing to use everywhere" [6]. In 2005 he called
"where the boundary conditions lie" one of "the open questions about agile methods" [7].

- **Before a team starts to work from the values, find out whether its people want to work that
  way, and do not start when they do not.** Fowler holds that where not to use an agile method
  "primarily comes down to the people": "If the people involved aren't interested in the kind of
  intense collaboration that agile working requires, then it's going to be a big struggle to get
  them to work with it" [7]. From this he concludes that "you should never try to impose agile
  working on a team that doesn't want to try it" [7]. In 2018 he went further: "if the team
  doesn't want to work in an agile way, then agile probably isn't appropriate in that context"
  [6]. Who makes that call is in [choosing-an-approach.md](choosing-an-approach.md) section 3.
- **When the customer will not work with the team, plan for less of the gain, not for none.**
  Principle 4 asks business people and developers to work together daily [2]. Fowler holds that
  "If customers don't collaborate, then you won't see the full advantages of an adaptive process",
  and he reports customers who "changed their mind over the first few months" [7].
- **Do not use the values to decide whether a deliverable is planned up front;
  [life-cycle.md](../project-management/life-cycle.md) section 4 makes that pick** (this
  practice's own split, so the pick has one owner). Fowler, who argued for adaptive methods, still
  holds that predictable development is possible in some work, with NASA's space shuttle software
  group as his example, and that it "requires a lot of ceremony, plenty of time, a large team, and
  stable requirements" [7]. The danger he names is "to pretend that you can follow a predictable
  process when you can't" [7].

No source read for this file names a case where the four values and twelve principles are too
much for a project. A method built on them can be; each method's file says when.

## 3. Agility, not a brand

Three of the Manifesto's authors later wrote against treating "agile" as a product to buy or a
method to install.

- Dave Thomas holds that "The word 'agile' has been subverted to the point where it is effectively
  meaningless" [4]. For him "Agile is not a noun, it's an adjective, and it must qualify something
  else", so you do not "work on an agile team"; "your team exhibits agility" [4]. His warning on
  labels: "you can buy and sell labels", "But you can't buy experience—you can only earn it" [4].
- Ron Jeffries holds that developers "should detach their thinking from any particular named
  'Agile' method" and keep to "the foundational principles that support Agile Software
  Development" [5]. This is his view about named methods. What counts as Scrum is the Scrum
  Guide's call, in [scrum.md](scrum.md).
- Martin Fowler shares the diagnosis (section 5) but keeps the word: "we might as well use the
  same label, but we've got to let people know what it really stands for" [6]. Thomas instead
  holds "it is time to retire the word 'Agile'" [4]. This file follows Fowler on the word, since
  readers and teams still use it, and Thomas on the test: what a team does counts, not what it
  calls it (this practice's own choice).

**When you judge whether a team works with agility, look at what it does against the four values
and the twelve principles, never at the name of its method, its tools or its job titles.** The
reason: a name can be bought and sold, as Thomas holds [4], and Fowler finds the name used for work
that has "none of the practices and values in place" [6].

Check: before you take an offer to make a team agile, sort what it asks for (tools, documents,
meetings, plans) onto the left or the right side of the four values; an offer whose items sit
mostly on the right side sells process, not agility. This is Thomas's test: he asks where
consultants and vendors "are positioned on the left-right axis", and his guess is "you'll find them
process and tool heavy, with many suggested work products" [4].

## 4. How a team starts from the values

The Manifesto gives no first step. The steps below are its authors' advice, each one their view;
the order is this file's own. Which approach a project's deliverable takes is
[life-cycle.md](../project-management/life-cycle.md) section 4's rule, and who chooses the team's way
of working is in [choosing-an-approach.md](choosing-an-approach.md).

1. **Start with a team that wants to, on a project of manageable size that is a little more
   critical than is comfortable.** Fowler holds that "it's essential that you start with a team
   that wants to try and work in an agile way" [7]. He advises "picking something smaller to start
   with", because "Large projects are inherently more difficult anyway", and "a project that's a
   little bit more critical than you are comfortable with", because "an unimportant project often
   makes a poor test since nobody cares much about the outcome" [7]. Work across several teams is
   in [scaling.md](scaling.md).
2. **Work in small steps, and adjust after each one.** Thomas's recipe is "Find out where you
   are", "Take a small step towards your goal", "Adjust your understanding based on what you
   learned", "Repeat", with one practice: "When faced with two or more alternatives that deliver
   roughly the same value, take the path that makes future change easier" [4]. He holds that these
   lines "encompass everything there is to know about effective software development", and admits
   that the loop "involves a fair amount of thinking" [4].
3. **Find someone who has done it before.** Fowler holds that "Perhaps the most important thing you
   can do is find someone more experienced in agile methods to help you learn" [7]. He calls this
   advice "self serving", since his firm, Thoughtworks, and many of his friends do mentoring on
   agile methods [7].
4. **Reflect at regular intervals, and change how the team works from what it finds.** Principle
   12 asks that "At regular intervals, the team reflects on how to become more effective, then
   tunes and adjusts its behavior accordingly" [2]. The meeting that does it is the Sprint
   Retrospective in [meetings.md](../project-management/meetings.md) section 8, or the regular
   retrospective of a team without sprints in section 9.

Principles 5 and 8 already have their rules in this library: trust in how a person does the work
([principles.md](../project-management/principles.md) section 1), and a pace the team can keep
(section 3).

**When the organisation runs a method the team did not choose.** Jeffries would "follow those
values and principles no matter what method the larger organization used", and he offers that "as
advice" [5]. For that case he writes: "No matter what framework or method your management thinks
they are applying, learn to work this way" [5]:

- produce running, tested, integrated software every two weeks, then every week, and build the
  skill to make a new working version every day [5];
- keep the design clean by "refactoring in tiny continuous steps, all the time" [5];
- "Use the current increment of software as the foundation for all your conversations with your
  product leadership and management" [5].

When the team cannot finish what it takes on, he advises it to "take on less work in each time
period, until you've taken on a small enough batch that you can actually get it done" [5]. He is
plain about the cost: "It won't be perfect, and for a while at least, it probably won't be fun"
[5]. The engineering practices behind this advice are in
[extreme-programming.md](extreme-programming.md), and integration and delivery in
[release.md](../project-management/release.md) section 5.

## 5. Common mistakes

- **Imposing the process.** A method is rolled out to the teams from above. The reasons to let the
  team choose instead are in [choosing-an-approach.md](choosing-an-approach.md) section 3. Jeffries
  holds that "Larger-scale 'Agile' methods appear actually to recommend imposition of process" [5].
  Such methods, he writes, "are pitched to the enterprise, and the enterprise is expected to
  'install' them, or 'roll them out'" [5]. Fowler holds that "imposing agile methods on reluctant
  people is fundamentally at odds with the whole notion of agile development" [7]. In 2018 he named
  the industry of agile consulting firms and conference talks, which he counts himself part of, the
  "Agile Industrial Complex", and called its "imposing methods upon people" "an absolute travesty"
  [6]. The fix: who chooses the process is in [choosing-an-approach.md](choosing-an-approach.md), and scaled
  frameworks are in [scaling.md](scaling.md).
- **Faux-agile: the name without the work.** A team says it is agile, and its work shows none of
  the values. Fowler calls this "faux-agile: agile that's just the name, but none of the practices
  and values in place", and holds that it is "even worse than just pretending to do agile", since
  it is "actively using the name 'agile' against the basic principles" [6]. Thomas describes how
  the word lost its meaning: once the Manifesto became popular, it "became a magnet for anyone with
  points to espouse, hours to bill, or products to sell" [4]. Fowler notes Jeffries's names for it,
  "Dark Agile" and "Dark Scrum" [6]; the Scrum form is in [scrum.md](scrum.md). The fix: the rule
  and the check in section 3.
- **Reading "over" as "instead of".** The values are read as a ban on plans and documents. The
  Manifesto's closing line keeps "value in the items on the right" [1]. Highsmith answered that
  reading in 2001, against critics who called the methods' supporters "hackers": "We embrace
  documentation, but not hundreds of pages of never-maintained and
  rarely-used tomes. We plan, but recognize the limits of planning in a turbulent environment"
  [3]. The fix: keep a plan or a document where it serves the left side, and drop the parts nobody
  maintains or reads.
- **Leaving out technical excellence.** The work on process gets the attention, and the work on
  code does not. Fowler named "the lack of recognition of the importance of technical excellence"
  as the second problem of agile in 2018, and observed that "A lot of agile conferences I go to
  don't tend to talk very much about the actual techniques of writing software" [6]. Principle 9
  holds that "Continuous attention to technical excellence and good design enhances agility" [2].
  The fix: the engineering practices in [extreme-programming.md](extreme-programming.md).

## 6. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Kent Beck et al., the 17 authors — Manifesto for Agile Software Development, 2001 — https://agilemanifesto.org/
- [2] Kent Beck et al., the 17 authors — Principles behind the Agile Manifesto, 2001 — https://agilemanifesto.org/principles.html
- [3] Jim Highsmith — History: The Agile Manifesto (agilemanifesto.org, 2001; opinion) — https://agilemanifesto.org/history.html — checked 2026-10-30
- [4] Dave Thomas — Agile is Dead (Long Live Agility) (pragdave.me, 2014; opinion) — https://pragdave.me/thoughts/active/2014-03-04-time-to-kill-agile.html — checked 2026-10-30
- [5] Ron Jeffries — Developers Should Abandon Agile (ronjeffries.com, 2018; opinion) — https://ronjeffries.com/articles/018-01ff/abandon-1/ — checked 2026-10-30
- [6] Martin Fowler — The State of Agile Software in 2018, transcript of a keynote at Agile Australia (martinfowler.com, 2018; opinion) — https://martinfowler.com/articles/agile-aus-2018.html — checked 2026-10-30
- [7] Martin Fowler — The New Methodology (martinfowler.com, 2005; opinion; the author's firm, Thoughtworks, does mentoring on agile methods, as the text says) — https://martinfowler.com/articles/newMethodology.html — checked 2026-10-30
