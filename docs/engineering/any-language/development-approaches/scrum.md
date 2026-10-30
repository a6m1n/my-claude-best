# Scrum

What Scrum is and the problem it solves, when it fits and when it is too much, how a team starts
with it, and why a team keeps it whole while it adds other practices. It is for everyone who
starts Scrum or changes how a team runs it: a developer, a Product Owner, a Scrum Master, a
manager, and an AI agent asked to set up "our Scrum". The rules follow the 2020 Scrum Guide. Three
things live elsewhere and are linked here, not repeated: the pick between Scrum and a Kanban flow
is [life-cycle.md](../project-management/life-cycle.md) section 4, the events with their order and
timeboxes are [meetings.md](../project-management/meetings.md) sections 2 to 9, and the Definition
of Done is [tickets.md](../project-management/tickets.md) section 2.

**Navigation**

- [1. What Scrum is and the problem it solves](#1-what-scrum-is-and-the-problem-it-solves)
- [2. When it fits and when it is too much](#2-when-it-fits-and-when-it-is-too-much)
- [3. How a team starts](#3-how-a-team-starts)
- [4. Keeping Scrum whole, and what tailoring costs](#4-keeping-scrum-whole-and-what-tailoring-costs)
- [5. When the team's situation changes](#5-when-the-teams-situation-changes)
- [6. Common mistakes](#6-common-mistakes)
- [7. What effective Scrum teams have in common](#7-what-effective-scrum-teams-have-in-common)
- [8. The Expansion Pack](#8-the-expansion-pack)
- [9. Alternatives considered](#9-alternatives-considered)
- [10. Sources](#10-sources)

**When you do not need it.** The Scrum Guide frames Scrum for "complex problems" and names no
case where it does not fit [1]. Ken Schwaber, one of the Guide's two authors, holds on his own
blog that Scrum is designed for complex work, and that continuous flow, which Kanban formalizes,
is "another process for different types of problems" [2]. Whether a team runs Scrum or a Kanban
flow is decided by [life-cycle.md](../project-management/life-cycle.md) section 4, and a flow runs
by [kanban.md](kanban.md). In this practice's reading, a team that cannot staff three
accountabilities or give its time to the five events is better served by another approach than by
a Scrum with parts missing (sections 2 and 4).

## 1. What Scrum is and the problem it solves

Some work cannot be planned in full at the start: what to build, and how, is learned while
building it. Scrum is for that work. The Scrum Guide defines it as "a lightweight framework that
helps people, teams and organizations generate value through adaptive solutions for complex
problems" [1]. A team that follows this file delivers a usable Increment in every Sprint of fixed
length, inspects it with its stakeholders, and changes its plan and its way of working from what
it saw.

The Guide of November 2020 is the current official edition: its download page lists "English
(November 2020) - Official Current Version" [3]. Every rule in this file follows that edition.

What Scrum is made of, in the Guide's words [1]:

| Part | What the Guide says | Where this library has more |
|---|---|---|
| Theory | "Scrum is founded on empiricism and lean thinking": knowledge comes from experience and from decisions based on what is observed, and lean thinking "reduces waste and focuses on the essentials". Its three pillars are transparency, inspection and adaptation. | — |
| Values | "Commitment, Focus, Openness, Respect, and Courage" | — |
| Team | "one Scrum Master, one Product Owner, and Developers", with "no sub-teams or hierarchies", "typically 10 or fewer people" | Section 3 |
| Accountabilities | Three: the Developers, the Product Owner and the Scrum Master | Section 3 |
| Artifacts, each with its commitment | The Product Backlog and the Product Goal; the Sprint Backlog and the Sprint Goal; the Increment and the Definition of Done | The Definition of Done: [tickets.md](../project-management/tickets.md) section 2 |
| Events | The Sprint, and the four inside it: Sprint Planning, the Daily Scrum, the Sprint Review and the Sprint Retrospective | [meetings.md](../project-management/meetings.md) sections 1 to 8 |

The commitments "exist to reinforce empiricism and the Scrum values for the Scrum Team and their
stakeholders" [1].

The one rule: **run Scrum whole, as the 2020 Guide defines it. Add the practices the team needs
inside it; never remove an event, an accountability or an artifact, and never let a Sprint run
without its fixed end.**

Why it holds the rest together:

- The Guide says so itself: partial use is possible, but "the result is not Scrum", and Scrum
  "functions well as a container for other techniques, methodologies, and practices" [1].
- In the studies a 2022 review covered, teams that dropped the Sprint Review got feedback late,
  and teams whose Sprint had no time limit had unclear goals [7] (section 4).
- A team that runs the whole framework can check itself against one text. A team that removed
  parts has no text left that says what it runs. This reason is this practice's own.

What it leaves out on purpose, and where that lives:

- Whether a team uses Scrum at all, and who chooses: [choosing-an-approach.md](choosing-an-approach.md).
  The Guide's line that a Scrum Team is self-managing, "meaning they internally decide who does
  what, when, and how" [1], is about the team's own work inside Scrum, not about that choice.
- The pick between Scrum and a Kanban flow: [life-cycle.md](../project-management/life-cycle.md)
  section 4.
- The events, their order and their timeboxes, and a team without Sprints:
  [meetings.md](../project-management/meetings.md) sections 2 to 9.
- The Definition of Done and the story form: [tickets.md](../project-management/tickets.md)
  section 2.
- Kanban inside Scrum, which keeps Scrum whole: [kanban.md](kanban.md). Scrumban, which this
  practice uses only for a path that starts from Scrum and leaves it:
  [combining-approaches.md](combining-approaches.md). Engineering practices with Scrum:
  [extreme-programming.md](extreme-programming.md). Many teams on one product:
  [scaling.md](scaling.md). AI agents in a Scrum team: [ai-agents.md](ai-agents.md). Regulated
  and fixed-scope work: [regulated-work.md](regulated-work.md).
- Security: there are no known security impacts of the rules in this file. A coding agent that
  takes part in a team's work runs as [agent-containers.md](../docker/agent-containers.md)
  describes.

Not covered yet, because the research for this practice found no source it could read: a measured
result for changes that stay inside the Guide's rules (section 4); later studies that test the five
factors of section 7, which were not searched, and the journal text of that study, read only as its
preprint; and the position of Scrum.org or Ken Schwaber on the Expansion Pack (section 8).

## 2. When it fits and when it is too much

The Guide says what Scrum is for and nowhere says what it is not for. It speaks of "complex
problems", and adds: "We are humbled to see Scrum being adopted in many domains holding
essentially complex work, beyond software product development where Scrum has its roots" [1]. Its
advice to a team is "Try it as is and determine if its philosophy, theory, and structure help to
achieve goals and create value" [1]. That is a test a team runs, not a boundary.

The boundaries come from named practitioners, each on their own site:

- Ken Schwaber, one of the Guide's two authors, writes of "the complex work Scrum is designed for
  (where more things are unknown than known)" [2]. Of continuous flow, "best formalized by Kanban",
  he writes: "It is great for complicated work, such as service tickets, customer complaints, and
  some bug fixes. Kanban is a very specific set of techniques from Lean that is applicable when
  the work is inherently simple" [2]. He rejects the idea that flow is a simpler Scrum: "It is
  another process for different types of problems" [2].
- Schwaber also holds that Scrum needs a team that organises itself: "Scrum without
  self-organization and empowerment is a death march, just like waterfall, but an iterative,
  incremental death march without slack" [2]. This is his view; the post cites no study for it.
- A year later he wrote that "sometimes processes are applied to inappropriate situations", and
  of Scrum: "It is most appropriate for optimizing complex work" [4].

Schwaber co-wrote Scrum but does not own Kanban, so his simple-against-complex test is his view
and not this practice's rule. In his view, Scrum is too much when the work is simple or made simple
and comes as single requests such as service tickets, and he names a Kanban flow for it [2]; this
practice does not follow that test, because the Kanban Guide, Kanban's owner text, says Kanban "can
be used at any scale and in most contexts where value is delivered" [17], so a test that keeps
Kanban to simple work does not match Kanban's owner (section 9). What Kanban fits is
[kanban.md](kanban.md)'s, and the rule that picks between Scrum and a Kanban flow is
[life-cycle.md](../project-management/life-cycle.md) section 4.

What this means for a team, in this practice's own reading of the sources above:

- Scrum fits when much about the product is unknown, and the team learns what to build by
  building it and showing each Increment to its stakeholders [1], [2].
- In these practitioners' views it is too much when the team is not allowed to organise its own
  work [2]. For that case the sources name no simpler way.
- A small team still pays for the whole framework. It holds five events, whose time
  [meetings.md](../project-management/meetings.md) section 2 gives, and fills three
  accountabilities, one of them a Product Owner who "is accountable for maximizing the value of
  the product resulting from the work of the Scrum Team" [1]. A team that cannot fill them picks
  another approach, not a Scrum with parts missing (section 4).
- Whether Scrum should be an organisation's default is
  [choosing-an-approach.md](choosing-an-approach.md).

## 3. How a team starts

Start from the Guide as it is, and change it only after the team has seen it work: "Scrum is
simple. Try it as is and determine if its philosophy, theory, and structure help to achieve goals
and create value" [1]. In this order:

1. **Before the first Sprint, form one Scrum Team of 10 or fewer people: one Product Owner, one
   Scrum Master and the Developers, with no sub-teams.** The Guide's reason: "In general, we have
   found that smaller teams communicate better and are more productive" [1]. When more people work
   on the product, the Guide's answer is several Scrum Teams on one product, and
   [scaling.md](scaling.md) owns that case.
2. **Give the Product Owner's accountability to one person.** "The Product Owner is one person,
   not a committee" [1], so one person answers for the order of the Product Backlog and for the
   value of the product.
3. **Before the first Sprint Planning, the Product Owner writes the Product Goal and orders the
   Product Backlog.** The Product Goal is "a target for the Scrum Team to plan against" [1], and
   Sprint Planning has nothing to pick from without an ordered backlog.
4. **Agree the Definition of Done before the first Sprint**, the way
   [tickets.md](../project-management/tickets.md) section 2 says, because "Work cannot be
   considered part of an Increment unless it meets the Definition of Done" [1].
5. **Pick one Sprint length of a month or less, and keep it.** Sprints "are fixed length events of
   one month or less to create consistency", and "A new Sprint starts immediately after the
   conclusion of the previous Sprint" [1]. Hold the events in the order and with the timeboxes of
   [meetings.md](../project-management/meetings.md) section 2.
6. **Let the Developers decide who does what.** The team is self-managing, "meaning they
   internally decide who does what, when, and how" [1]. Without that, Schwaber holds, Scrum
   becomes "a death march" [2] (section 2).
7. **Change how the team runs Scrum only at the Sprint Retrospective, and only inside the rules of
   section 4.** The Retrospective's purpose "is to plan ways to increase quality and
   effectiveness" [1], so a change made there is one the whole team saw and can check at the next
   one.

The Scrum Master answers for this start: "The Scrum Master is accountable for establishing Scrum
as defined in the Scrum Guide" [1]. The Guide gives no number of Sprints to run before a team
changes anything.

Check: before the first Sprint Planning, can the team name its Product Owner, its Scrum Master,
its Sprint length, its Product Goal and the place where its Definition of Done is written?

## 4. Keeping Scrum whole, and what tailoring costs

The Guide's End Note is the rule: "The Scrum framework, as outlined herein, is immutable. While
implementing only parts of Scrum is possible, the result is not Scrum. Scrum exists only in its
entirety and functions well as a container for other techniques, methodologies, and practices"
[1]. Its opening says what removing a part does: "Changing the core design or ideas of Scrum,
leaving out elements, or not following the rules of Scrum, covers up problems and limits the
benefits of Scrum, potentially even rendering it useless" [1].

Research points the same way, with limits. Özgün Özkan and Özden Özcan-Top reviewed 23 studies
of Scrum in software organisations, published from 2001 to 2022; 8 of them hold examples of
tailored events, which the review calls practices [7]. They found that "most organizations tailor
the existing Scrum components by either not implementing a specific practice, role, or an
artifact or modifying the duration limits of the practices" [7]. In the studies they cite, teams
with no Sprint Review got feedback only when the customer started to use the product, and so made
changes late; in a Sprint with no time limit, goals were unclear and team members did not commit
to the Sprint Goals, "considering that the sprint could be extended at any time" [7]. Daily Scrums
with no fixed time and longer than 15 minutes led to fatigue, and members lost their focus [7]. Their
conclusion: "Significant tailoring choices such as removing a specific Scrum practice or role that
is defined in the Scrum guide, ended up having negative consequences for most of the teams" [7].
The same review holds that "tailoring some of the Scrum components can be a must for most
companies", and says that "there is not enough evidence about specific Scrum practice tailoring
results" [7]. Each link it draws rests on one or two of the studies it reviewed.

So the rules are narrower than a ban on all tailoring:

- **When you change how the team runs Scrum, keep every event, accountability and artifact the
  Guide defines, and keep the Sprint's fixed length.** The Guide says the result is otherwise not
  Scrum [1], and the review linked removing them to late feedback and unclear goals [7].
- **When the team needs a practice the Guide does not define, add it inside the framework.** The
  Guide: "Various processes, techniques and methods can be employed within the framework" [1].
  Two common additions have files of their own. Kanban inside Scrum: the Kanban Guide for Scrum
  Teams says "The Scrum Guide applies in its entirety" [8], and [kanban.md](kanban.md) says how.
  Engineering practices: Martin Fowler holds that "the XP practices make a good starting point"
  [9], and [extreme-programming.md](extreme-programming.md) says how.
- **Adjust inside the rules at a Sprint Retrospective, and check the effect at the next one.** The
  Guide gives each event a maximum, and "For shorter Sprints, the event is usually shorter" [1].
  Inside the rules is not the same as harmless: in studies the review cites, Retrospectives kept to
  about 15 minutes meant "not being able to run efficient discussion and identify actionable
  improvement items" [7]. The one success it reports is Fitzgerald et al.'s: two planning sessions
  and planning kept simple, without Gantt charts, after which "overall project success is
  increased" [7]. No study the review covers measures such changes across teams.

What keeping it whole costs, and where the rule stops:

- The cost is the time of every event and the people for three accountabilities, Sprint after
  Sprint. The review holds that "most companies have valid reasons to adjust the original
  definition of the Scrum practices, roles and artifacts" [7]. When the reason is that the team
  cannot pay for a part, it says so and picks another approach, by
  [choosing-an-approach.md](choosing-an-approach.md) and
  [combining-approaches.md](combining-approaches.md), because a Scrum with a part removed is "not
  Scrum" [1] and readers of the team's docs expect the whole. This is this practice's own reading.
- A regulator or a contract may set rules of its own around the team:
  [regulated-work.md](regulated-work.md).

A team that already runs a Scrum with parts removed does not stop its work to rebuild its process.
This is the first of the three answers in [refactoring.md](../refactoring/refactoring.md)
section 7, new and touched code, applied to a process: at its next Sprint Retrospective, or, when
the team dropped the Retrospective, at a session the Scrum Master holds before the next Sprint
Planning, the team names each event, accountability or artifact it dropped, and any Sprint with no
fixed end. For each part it plans either to bring it back or, when it cannot pay for the part, to
stop calling its process Scrum, because then "the result is not Scrum" [1] (the cost bullet above).

Check: at each Sprint Retrospective, or, when the team dropped the Retrospective, at a session the
Scrum Master holds before the next Sprint Planning, ask: does any event, accountability, artifact
or fixed Sprint end of the Guide no longer run?

## 5. When the team's situation changes

Each rule below holds only under its condition; a team that does not meet it can skip it.

- **When unplanned, must-do-now work keeps arriving.** The Guide's rule for the Sprint is "No
  changes are made that would endanger the Sprint Goal" [1]. Whether such work stays with this
  Scrum team, with capacity held for it, or goes to a separate flow is
  [life-cycle.md](../project-management/life-cycle.md) section 4.
- **When the team grows past about ten people:** [scaling.md](scaling.md).
- **When the team wants flow practices and keeps Scrum whole:** Kanban inside Scrum,
  [kanban.md](kanban.md).
- **When the team means to leave Scrum for a flow, step by step:** that path is what this practice
  calls Scrumban, [combining-approaches.md](combining-approaches.md). From the first part it drops,
  the team no longer runs Scrum (section 4).
- **When the code base slows the team down:** [extreme-programming.md](extreme-programming.md),
  and Flaccid Scrum in section 6.
- **When AI agents take part in the work:** [ai-agents.md](ai-agents.md). One Expansion Pack text
  departs from the Guide on this point (section 8).
- **When a regulator or a fixed-price contract sets the frame:**
  [regulated-work.md](regulated-work.md).

## 6. Common mistakes

These are the mistakes that named practitioners and one research summary describe. Each fix
points at the rule that prevents it.

| Mistake | What it looks like | What it costs | Fix |
|---|---|---|---|
| Dark Scrum, in Ron Jeffries' account | "people who know their old job, but not their new Scrum job, begin to do the Scrum activities"; the Daily Scrum "is imposed on the typical team", and a power holder uses it "to stay on top of what everyone is doing" [10] | "Too often, at least in software, Scrum seems to oppress people" [10] | The Daily Scrum is the Developers' event ([meetings.md](../project-management/meetings.md) section 5); the Developers decide who does what (section 3); Jeffries' own way out is to make progress visible with "a complete, running, tested, operable program" each Sprint [10] |
| Zombie Scrum, as its authors describe it | "something that looks like Scrum from a distance, but is anything but on closer inspection. There is no working software after a Sprint, stakeholders are not involved, teams have little autonomy and nobody is trying to improve" [11] | No Increment to inspect, so the team learns nothing from the Sprint (this practice's reading) | A Definition of Done that ends in a usable Increment ([tickets.md](../project-management/tickets.md) section 2); stakeholders at the Sprint Review ([meetings.md](../project-management/meetings.md) section 7); Retrospective actions with an owner (section 8 there) |
| Flaccid Scrum, in Martin Fowler's view | The team adopts the Scrum practices, and "After a while progress is slow because the code base is a mess"; Scrum "deliberately omits any technical practices" [9] | Slow progress, and a code base the team cannot change safely | Add engineering practices inside the framework (section 4); [extreme-programming.md](extreme-programming.md) |
| Priorities that keep changing, from Google's blog summary of the 2024 DORA report | The plan changes inside the Sprint and from one Sprint to the next | Instability in priorities "can significantly hinder progress", and the "constantly pivot" mentality "negatively impacts developer well-being" [12] | Keep the Sprint Goal for the Sprint [1]; plan for interrupts (section 5) |
| A part removed, or a Sprint with no fixed end | No Sprint Review; a Sprint that "could be extended at any time" [7] | Late feedback, unclear goals, wrong features [7] | Section 4 |

Two notes on these sources. Zombie Scrum's authors sell their book on the site cited, and the site
names The Liberators B.V. in its footer [11]; one of the authors, Christiaan Verwijs, co-wrote the
study in section 7, so the two are not independent sources. The DORA finding is not about Scrum,
and only the blog's summary was read: not the report's method, nor its effect sizes.

## 7. What effective Scrum teams have in common

Christiaan Verwijs and Daniel Russo built a model of Scrum team effectiveness from thirteen
exploratory field studies, then tested it on survey answers from 4,940 software professionals in
1,978 Scrum teams [13]. They found five high-level factors: "responsiveness, stakeholder concern,
continuous improvement, team autonomy, and management support" [13]. The study was published in
ACM TOSEM in 2023 and was read here as its arXiv preprint, version 3.

Its limits, as the authors state them:

- "Our survey consisted of self-reported items", and team effectiveness itself "is based on
  self-reported scores on team morale and the perceived satisfaction of stakeholders" [13].
- The sample is voluntary: "samples are based on voluntary (non-probabilistic) responses", and
  42% of those who started the survey completed it [13]. Teams got a detailed score profile for
  taking part [13].
- "The cross-sectional nature of the data also does not allow conclusions about the causality of
  effects" [13].
- They "can not make conclusions for teams that apply Scrum to other domains than software
  engineering" [13].
- "Christiaan Verwijs has a financial interest in The Liberators BV", the company the paper gives
  as his affiliation [13].

So use the five factors as questions for a Sprint Retrospective, never as a score to compare teams
or a target to reach. The reason is the study's own limits: self-rated answers from volunteers,
measured once, show which factors go together, not which ones cause effectiveness. This rule is
this practice's own.

## 8. The Expansion Pack

The Scrum Guide Expansion Pack is a companion text by Jeff Sutherland, one of the Guide's two
authors, with John Coleman and Ralph Jocham; Ken Schwaber is not among its authors [14], [15]. Its
core document, "Scrum Guide Expanded", is at version 2026.1, dated 2026-01-18 [14]. Its readme
says: "It's not a replacement of the Scrum Guide. It's an optional companion", and "Scrum, as
defined in the 2020 Scrum Guide, is still solid and useful" [15]. The core document says that "in
the end, it departs in some places", marks its "Notable departures from the 2020 Scrum Guide", and
adds: "This Expansion Pack will evolve regularly" [14].

One departure as an example: the Guide says "Developers are the people in the Scrum Team" [1], and
the Expansion Pack says "A Product Developer may be human or automated" [14]. What that means for
a team with AI agents is [ai-agents.md](ai-agents.md).

- **Take the rules from the 2020 Guide. When you use an Expansion Pack text, name it as its
  authors' companion, with its version, and say where it departs from the Guide.** The Guide is
  the official current version [3], the pack itself says it is no replacement [15], and a reader
  who meets a departure with no label takes it for Scrum.

A team that takes the Scrum Guide Expanded as its base instead names it and its version as its
text, and lists each departure from the 2020 Guide it takes; what such a team keeps with AI agents
is [ai-agents.md](ai-agents.md) section 4.

Not covered yet: the position of Scrum.org or Ken Schwaber on the Expansion Pack. The research for
this practice searched for one and found none it could read. That is not the same as a statement
that they do not endorse it.

## 9. Alternatives considered

- **Remove the parts of Scrum that do not fit the company.** The tailoring review holds that
  tailoring "can be a must for most companies" [7]. Not taken for removal: the same review linked
  removing an event or a role, and Sprints with no time limit, to negative results [7], and the
  Guide says the result is not Scrum [1]. Taken for additions and for adjustments inside the rules
  (section 4).
- **Schwaber's test: Scrum for complex work, a Kanban flow for simple work** [2]. Not taken: the
  Kanban Guide says Kanban "can be used at any scale and in most contexts where value is delivered"
  [17], so a test that keeps Kanban to simple work does not match Kanban's owner (section 2). The
  pick between the two is [life-cycle.md](../project-management/life-cycle.md) section 4.
- **Treat a Kanban flow as a simpler Scrum for a team that finds Scrum heavy.** Not taken:
  Schwaber holds that flow "is another process for different types of problems" [2], and the pick
  between the two is [life-cycle.md](../project-management/life-cycle.md) section 4.
- **Take the Expansion Pack as the base text.** Not taken: the Guide is the official current
  version [3], and the pack calls itself "an optional companion" [15] (section 8).
- **Follow no named method.** Ron Jeffries holds that software developers "should have no
  adherence to any 'Agile' method of any kind" [16]. Not taken in this file, which describes Scrum
  and follows the Guide on what counts as Scrum. Whether a team uses a named method at all, and who
  decides, is [choosing-an-approach.md](choosing-an-approach.md).
- **Scrumban, a path that starts from Scrum and leaves it.** Not taken in this file, which keeps
  Scrum whole; the path is [combining-approaches.md](combining-approaches.md)'s. A team that adds
  flow practices and keeps Scrum whole runs Kanban inside Scrum ([kanban.md](kanban.md)).

## 10. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Ken Schwaber and Jeff Sutherland — The Scrum Guide, November 2020 — https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf — checked 2026-10-30
- [2] Ken Schwaber — Microsoft and Scrum (Ken Schwaber's Blog, 2011; opinion, by a co-author of the Scrum Guide) — https://kenschwaber.wordpress.com/2011/07/18/microsoft-and-brian-harry/ — checked 2026-10-30
- [3] ScrumGuides.org — Download the official Scrum Guide — https://scrumguides.org/download.html — checked 2026-10-30
- [4] Ken Schwaber — What Comes After Scrum? (Ken Schwaber's Blog, 2012; opinion, by a co-author of the Scrum Guide) — https://kenschwaber.wordpress.com/2012/10/05/what-comes-after-scrum/ — checked 2026-10-30
- [7] Özgün Özkan and Özden Özcan-Top — Tailoring Choices Made in Scrum Projects: A Systematic Literature Review (IWSM-MENSURA 2022, CEUR Workshop Proceedings vol. 3272, 2022; research) — https://ceur-ws.org/Vol-3272/IWSM-MENSURA22_paper5.pdf — checked 2026-10-30
- [8] Scrum.org, Daniel Vacanti and Yuval Yeret — The Kanban Guide for Scrum Teams, January 2021 — https://scrumorg-website-prod.s3.amazonaws.com/drupal/2021-01/01-2021%20Kanban%20Guide.pdf — checked 2026-10-30
- [9] Martin Fowler — Flaccid Scrum (martinfowler.com, 2009; opinion) — https://www.martinfowler.com/bliki/FlaccidScrum.html — checked 2026-10-30
- [10] Ron Jeffries — Dark Scrum (ronjeffries.com, 2016; opinion) — https://ronjeffries.com/articles/016-09ff/defense/ — checked 2026-10-30
- [11] Christiaan Verwijs, Johannes Schartau and Barry Overeem — The Zombie Scrum Survival Guide, the book's site (zombiescrum.org, no date; opinion, on a site that sells the authors' book) — https://zombiescrum.org/ — checked 2026-10-30
- [12] Nathen Harvey and Derek DeBellis — Announcing the 2024 DORA report (Google Cloud Blog, 2024; research, sponsored by Google, read as the blog's summary of the report) — https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report — checked 2026-10-30
- [13] Christiaan Verwijs and Daniel Russo — A Theory of Scrum Team Effectiveness (ACM Transactions on Software Engineering and Methodology 32(3), 2023; research, by an author with a declared financial interest in The Liberators BV; read as arXiv v3, https://arxiv.org/html/2105.12439v3) — https://doi.org/10.1145/3571849 — checked 2026-10-30
- [14] Ralph Jocham, John Coleman and Jeff Sutherland — Scrum Guide Expanded, version 2026.1 (Scrum Guide Expansion Pack, 2026; opinion) — https://raw.githubusercontent.com/ScrumGuides/ScrumGuide-ExpansionPack/88eb64c2458da5021cb3c160ff4cc38dbb93e1ed/site/content/scrum-guide-expanded/2026.1/index.md
- [15] Scrum Guide Expansion Pack — repository readme — https://raw.githubusercontent.com/ScrumGuides/ScrumGuide-ExpansionPack/88eb64c2458da5021cb3c160ff4cc38dbb93e1ed/readme.md — checked 2026-10-30
- [16] Ron Jeffries — Developers Should Abandon Agile (ronjeffries.com, 2018; opinion) — https://ronjeffries.com/articles/018-01ff/abandon-1/ — checked 2026-10-30
- [17] Orderly Disruption Limited and Daniel S. Vacanti, Inc. — The Kanban Guide, v2025.5 (May 2025) — https://kanbanguides.org/the-kanban-guide/2025.5/ — checked 2026-10-30
