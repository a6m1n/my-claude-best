# Scaling past one team: when to scale, LeSS and SAFe

A product grows, and the team that builds it grows past the size at which Scrum works. This file
says when a second team is needed, the smallest structure the teams then share, how LeSS and SAFe
work by their owners' own texts, what research has measured about scaling frameworks, and the
mistakes the sources report. It is for whoever decides how several teams work on one product: a
Product Owner, a manager, a Scrum Master, a team that has grown too large, and an agent asked
"should we adopt SAFe?". Picking predictive, adaptive or hybrid work, and Scrum or Kanban, is
[life-cycle.md](../project-management/life-cycle.md) section 4. The rule that holds the file
together: **add a team only when one team cannot hold the product, and then add only the
structure the work needs, starting from the one Product Goal, Product Backlog and Product Owner
that the Scrum Guide gives a product.**

**Navigation**

- [1. When scaling starts](#1-when-scaling-starts)
- [2. LeSS](#2-less)
- [3. SAFe](#3-safe)
- [4. What the evidence says](#4-what-the-evidence-says)
- [5. Common mistakes](#5-common-mistakes)
- [6. Where the rules stop holding](#6-where-the-rules-stop-holding)
- [7. Alternatives considered](#7-alternatives-considered)
- [8. Adoption in a group that already has teams](#8-adoption-in-a-group-that-already-has-teams)
- [9. How an agent applies it](#9-how-an-agent-applies-it)
- [10. Sources](#10-sources)

**When you do not need this file.** A product that one team builds needs none of it: the Scrum
Guide's team of "typically 10 or fewer people" is the whole structure [1], and
[scrum.md](scrum.md) says how such a team starts. The frameworks are too much for a group below
their own ranges: Basic LeSS starts at two teams [2], and an Agile Release Train in SAFe has 5 to
15 teams [7]. A group that already runs a framework without problems needs only section 4, which
gives no measured reason to switch, and section 6.

**What it leaves out on purpose.**

- Who chooses the approach, and the evidence on agile outcomes in general:
  [choosing-an-approach.md](choosing-an-approach.md).
- How one team combines Scrum and Kanban: [combining-approaches.md](combining-approaches.md).
  Teams of one product that combine them in different ways still share what section 1 names
  (this practice's reading).
- What a team keeps when AI agents take part, in AI-Native SAFe too: [ai-agents.md](ai-agents.md).
- Scaling in regulated or fixed-scope work: [regulated-work.md](regulated-work.md).
- Nexus, Scrum@Scale and other scaling frameworks: section 7.
- Security: there are no known security impacts of the practices in this file.

Not covered yet, because the research found no source it could read or did not read one (section
6 gives the detail): a measured point at which a second team pays off, what adopting LeSS or SAFe costs, the steps of
moving to feature teams, the steps of a SAFe roll-out past Essential SAFe, and the size of a team
or a train in AI-Native SAFe.

## 1. When scaling starts

The Scrum Guide gives a Scrum Team a size and one rule for growth. The team is "small enough to
remain nimble and large enough to complete significant work within a Sprint, typically 10 or fewer
people" [1]. The rule follows in the same paragraph: "If Scrum Teams become too large, they should
consider reorganizing into multiple cohesive Scrum Teams, each focused on the same product.
Therefore, they should share the same Product Goal, Product Backlog, and Product Owner" [1].

The rules, in the order the work meets them:

- **Stay one team while one team can hold the product.** Add a team when the work of one product
  needs more people than one team of about ten. Why: every team you add has to coordinate with the
  others, and one team has nobody to coordinate with. This rule is this practice's own reading of
  the Scrum Guide's growth rule; the Guide frames scaling as a team that became too large and names
  no other trigger [1].
- **When a team splits, keep one Product Goal, one Product Backlog and one Product Owner for the
  product** [1], and one Definition of Done: "If there are multiple Scrum Teams working together on
  a product, they must mutually define and comply with the same Definition of Done" [1]. Why: with
  one backlog in one order and one person who orders it, every team pulls the work that matters
  most for the product, not for its own part (this practice's reading). LeSS makes the same choice
  its first product rule (section 2). What a Definition of Done holds is
  [tickets.md](../project-management/tickets.md) section 2.
  Check: when a team splits, list the teams that work on the product and ask whether they share one
  Product Backlog, one Product Owner and one Definition of Done.
- **Run one-team Scrum well before you scale it.** LeSS opens its framework with "Scaling Scrum
  starts with understanding standard one-team Scrum" [3]. Why: a framework built on Scrum copies
  the team's way of working into every new team (this practice's reading), and Verwijs and Russo
  found that teams' experience with Agile explains far more of their effectiveness than the scaling
  approach does [19]. How one team starts is [scrum.md](scrum.md).
- **Add as little structure as the work needs.** A new role, meeting or planning layer comes in
  only when a problem the teams have names it. This is this practice's default. It rests on the
  Scrum Guide's rule above and on LeSS's principle "more with less": "We don't want more roles
  because more roles leads to less responsibility to Teams." and "We want more with less" [4]. That
  principle is about fewer roles, artifacts and processes. LeSS does not use it as a reason to
  scale, and it does not mean adopting LeSS in part (section 2).

After the split, a product group can go on with the Scrum Guide's rule alone, or adopt a
framework. This file covers two. LeSS calls itself "Scrum applied to many teams working together on
one product" [4] (section 2). SAFe, Scaled Agile's framework, groups its teams in Agile Release
Trains [7] (section 3). No study read shows that one framework, or none, gives teams better results
than another (section 4), so the choice rests on fit with the group. No source read for this file
names who decides on a scaling framework. LeSS names whose support its adoption needs: the person
or people with "the organizational authority to make structural changes in your group—usually the
head of your product group" [24]. The two layers of the choice, the project's and the team's, are
in [choosing-an-approach.md](choosing-an-approach.md) section 3.

## 2. LeSS

This section holds when two or more teams build one product and the group runs LeSS or weighs it.
LeSS (Large-Scale Scrum) [4] comes in two sizes: "Basic LeSS applies to products with 2-“8”
teams." and "LeSS Huge applies to products with “8+” teams" [2]. The table below is a selection
from the LeSS Rules of November 2024, which LeSS calls "things we consider a must" [2]; the whole
set is in [2].

LeSS is too much for one team, which runs plain Scrum [1]. It does not fit a group that cannot
change its structure, since LeSS calls that structure vital [2] and its adoption changes it [5]
(this practice's reading).

| Rule | LeSS's text [2] |
|---|---|
| One owner, one backlog | "There is one Product Owner and one Product Backlog for the complete shippable product." |
| One Sprint for all teams | "There is one product-level Sprint, not a different Sprint for each Team." "Each Sprint results in an integrated whole product." |
| Feature teams | "The teams are customer-focused feature teams." |
| Real teams | "Each team is (1) self-managing, (2) cross-functional, (3) co-located, and (4) long-lived." |
| One Definition of Done | "One Definition of Done for the whole product, common for all teams." |
| Scrum Masters | "A Scrum Master is a dedicated full-time role." "One Scrum Master can serve 1-3 teams." |
| Overall Retrospective | After the team retrospectives, for "cross-team and system-wide issues". |

Adopting LeSS, in the order the work meets it:

- **Plan the adoption as a change of structure.** LeSS says "Successful adoption requires breaking
  assumptions and changing structure, with all the explosive politics and “loss of face” that
  entails across a big group" [5]. It runs no separate change programme: "In LeSS adoptions, there
  is no change initiative, no change group, no change managers" [5]. Why: the rules above change who
  sits on which team and who orders the work, so a group that only adds new meetings has not adopted
  LeSS (this practice's reading).
- **Set up the whole LeSS structure for the product group at once.** "For the product group,
  establish the complete LeSS structure “at the start”; this is vital for a LeSS adoption" [2].
  LeSS's adoption principles also say "use volunteering", and, on top-down or bottom-up adoption,
  "Either one or the other by itself is likely to fail. Do both" [24]. What they reject is the
  purely top-down case: "The manager-driven, “thou shalt do LeSS”-adoption causes resistance and
  sets the organization up for failure" [24].
  Around the product group, LeSS asks for a different pace: "For the larger organization beyond the
  product group, adopt LeSS evolutionarily" [2]. Why: LeSS calls the complete structure vital, so a
  product group that takes some of the rules and leaves others runs something other than LeSS by
  its owner's definition.
- **Stay on Basic LeSS up to eight teams.** "Avoid applying LeSS Huge for smaller product groups as
  it will result in more overhead and local optimizations" [2]. LeSS names the signs that a group
  has outgrown Basic LeSS: the single Product Owner "can no longer grasp an overview of the entire
  product", cannot balance an external and an internal focus, and the Product Backlog "is so large
  that it becomes difficult for one person to work with" [4]. Even then LeSS adds: "On the other
  hand, we suggest first trying to get better, smaller, and simpler, before getting huger" [4]. That
  line compares LeSS with LeSS Huge; it is not advice on whether to scale at all.
- **Move to LeSS Huge step by step.** In LeSS Huge, related customer requirements form Requirement
  Areas. "Each Requirement Area has one Area Product Owner." and has "between “4-8” teams", and one
  Product Owner still orders one Product Backlog for the product [2]. Unlike Basic LeSS, "LeSS Huge
  adoptions, including the structural changes, are done with an evolutionary incremental approach"
  [2].

## 3. SAFe

This section holds when an organisation runs SAFe or weighs it. It describes how SAFe works from
the texts of its owner, Scaled Agile, and says nothing about whether SAFe works better than another
way, because no study read shows that (section 4).

The version: the owner's configurations page opens with "Welcome to the Scaled Agile Framework 6.0
configurations." and lists four: Full SAFe, Essential SAFe, Large Solution SAFe and Portfolio SAFe
[6]. The owner's pages read for this file state no newer version number.

Scaled Agile names no case where SAFe does not fit. Its "What is SAFe?" page says "It's proven,
scalable, and configurable, no matter your organization's size, industry, or complexity" [10].

- **Start with Essential SAFe.** Scaled Agile describes it as "the minimal elements necessary for
  Agile Release Trains to deliver solutions" and "the simplest starting point for implementation",
  and says it "excludes Enterprise Solution Delivery and Portfolio concerns" [7]. Why: it is the
  owner's own smallest configuration, so it adds the least structure (section 1); the larger
  configurations come in when a problem the group has names them.
- **Form a train only when there are enough teams for one.** An Agile Release Train (ART) is "a
  long-lived team of Agile teams", "Each ART comprises 5 – 15 Agile teams", and each team is "a
  cross-functional group of ten or fewer individuals" [7]. Why: below five teams the owner's own
  range for a train is not met, and section 1 or Basic LeSS covers the group (this practice's
  reading).

**Core SAFe and AI-Native SAFe.** Since June 2026 Scaled Agile has supported "two co-existing
versions of the Framework, Core SAFe and AI-Native SAFe" [8], [9]. Its release post of 2026-06-23
says "This release does not replace Core SAFe" [8]. In AI-Native SAFe, "Standardized Agile roles
are replaced by flexible capabilities", named Product, Builder and Domain Expert, PI Planning
becomes PI Outcome Planning, and "Teams define their own cadence around three core activities":
Align, Sense and Respond [9]. These are the owner's descriptions of its product. The posts read
name no case for picking one version over the other; the release post says only "For many
organizations, Core SAFe continues to provide the right operating model for their current needs"
[8]. What a team keeps when AI agents take part is [ai-agents.md](ai-agents.md).

**What the owner claims.** The "What is SAFe?" page lists "Typical results reported by enterprises
using SAFe", among them 50% faster time-to-market and a 35% increase in productivity, with no
method or sample given [10]. These are a vendor's claims about its own product. No rule in this
file rests on them.

**What its critics hold.** Two of the Agile Manifesto's authors [14] criticise SAFe. Both posts are
more than ten years old, and both are opinions, not measurements:

- Ken Schwaber co-wrote the Scrum Guide [1], built Scrum.org [12], and develops Nexus, a scaling
  framework of his own, with Scrum.org [13], so he speaks as the owner of a rival framework. He holds
  that SAFe's authors push it "as a simple, one-size fits all approach to the agile organization",
  and that "Values and principles scale, but practices are context sensitive" [11]. In a 2018 reply
  under the same post he wrote "I still feel the same about SAFe" [11].
- Ron Jeffries holds that "The structure and teaching of SAFe is relentlessly top down." and that
  "SAFe is more likely to result in management imposing structure and teams being unable to move in
  better directions" [15]. He grants that "it will help, to a degree" [15].

## 4. What the evidence says

The reviews read found no comparison of scaling frameworks based on evidence, and the one large
survey since then that compares team results across them finds almost no difference. The rules in sections 1
to 3 therefore rest on the owners' texts and on this practice's reasoning, never on a claim that
one framework works better.

- **Most of the literature is experience reports.** Dikert, Paasivaara and Lassenius reviewed 52
  publications describing 42 industrial cases of large-scale agile transformations and found that
  "Almost 90% of the included papers were experience reports, indicating a lack of sound academic
  research on the topic" [16]. The papers they reviewed "very seldom mention any frameworks" [16].
- **The evidence on frameworks is young.** Conboy and Carroll, drawing on 13 agile transformation
  cases over 15 years, found the empirical evidence on the frameworks' adoption, use, effectiveness
  and challenges "still very much in its infancy" [17].
- **No comparison across methods.** The abstract of Edison, Wang and Conboy's systematic review of
  SAFe, LeSS, Scrum-at-Scale, DAD and the Spotify model reports "a disparate set of studies across
  each individual method, with no cross-method comparison based on empirical evidence" [18]. The
  review itself compares the methods' "principles, practices, tools, and metrics" [18]: their texts,
  not their outcomes.
- **The scaling approach explains about 1 to 2% of the variance in team effectiveness.** Verwijs and Russo ran a
  public online survey from September 2021 to September 2023 of 15,078 members of 4,013 teams, with
  stakeholder ratings for 529 of those teams, comparing SAFe, LeSS, Scrum of Scrums, custom
  approaches and no scaling [19]. Models that took only the scaling approach into account "tended
  to explain about 1-2% of the variance", while the teams' experience with Agile weighed far more
  [19]. They conclude that "the choice of Agile scaling strategy does not markedly influence team
  effectiveness" [19]. Read it within its limits: the sample chose itself, as the authors note:
  "Public surveys are susceptible to response bias due to the self-selection of participants" [19].
  They also write "We do not know how well our sample reflects the total population" [19]. The first
  author declares a financial interest in The Liberators BV [19]. And the survey measured team
  effectiveness and stakeholder satisfaction, not portfolio results or time to market (this
  practice's reading of its measures).

What follows for a rule: pick a framework, or none, by fit with the group, since the measured
difference between frameworks is negligible. Verwijs and Russo advise organisations "to choose a
method that best aligns with their previous experiences with Agile, organizational culture, and
management style" [19]. The evidence on agile outcomes in general is
[choosing-an-approach.md](choosing-an-approach.md).

## 5. Common mistakes

| Mistake | What it costs | Fix |
|---|---|---|
| Adding teams and a framework before one team runs Scrum well | The new structure carries one team's problems into every team (this practice's reading); teams' experience with Agile explains far more of their effectiveness than the scaling approach [19] | Run one-team Scrum first [3], section 1 |
| A backlog and a Product Owner for each new team | The teams no longer share one order of work; it breaks the Scrum Guide's growth rule [1] and LeSS's first product rule [2] | One Product Goal, one Product Backlog, one Product Owner, section 1 |
| Copying the Spotify model as a framework | Henrik Kniberg, who published the material that came to be called the Spotify model, holds that it "wasn't actually intended to be a generic framework or “model” at all" and is "just an example of how one company works" [22]. At Spotify, by the account of Jeremiah Lee, who joined after the company had grown to 3,000 people, the model was "only ever aspirational and never fully implemented" [23]; that is one insider's account | Take single ideas and adapt them; Kniberg holds that copying "can sometimes be helpful", as long as a company adapts it to its local context [22] |
| Choosing a framework because someone read a book or saw a talk | Conboy and Carroll found that "Framework selection was often ad hoc where one or two read a book, attended a talk and the decision was made" [17]. | Write down why the framework fits the group, by sections 1 to 3 and [choosing-an-approach.md](choosing-an-approach.md) |
| Driving the framework only from the top | Conboy and Carroll found many implementations "driven completely from either the bottom-up or from the top-down, rather than a mix". The top-down ones felt like "yet another framework imposed by those who didn't understand the implications or problems to be solved", and bottom-up SAFe ones ended in "mass confusion" [17]. Jeffries holds that SAFe itself is "relentlessly top down" [15] | Management sponsors the change and takes part, and the teams shape the practices; Conboy and Carroll: "Strike a clear balance between enabling top-down and bottom-up transformation" [17]. |
| Measuring the change by how closely teams follow the framework | Conboy and Carroll found "a tendency to measure agile transformation by adherence to that framework, rather than the value it provides" [17] | Measure what the product delivers, not how many teams follow the framework (this practice's reading) |
| Adopting LeSS part by part | LeSS calls its complete structure "at the start" "vital for a LeSS adoption" [2] | The whole structure for the product group at once, section 2 |
| LeSS Huge for eight teams or fewer | "more overhead and local optimizations" [2] | Basic LeSS, section 2 |
| SAFe's 50% and 35% read as evidence | A vendor's figures with no method [10] | Section 4 |

## 6. Where the rules stop holding

When a rule does not fit, and what following it costs:

- **One team.** Nothing in this file applies: the Scrum Guide's one team is the structure [1], and
  [scrum.md](scrum.md) is the file to read.
- **A group that cannot change its structure.** LeSS does not fit, because its rules make the
  complete structure vital [2] and its adoption changes structure [5]. Section 1 still holds.
- **Fewer than five teams.** An Agile Release Train has 5 to 15 teams [7]; such a group follows
  section 1 or Basic LeSS.
- **A group that already runs a framework.** Keep it until a problem the teams have names a reason
  to change. Why: no measured difference between frameworks favours a switch (section 4), and
  Conboy and Carroll saw teams that went through several frameworks become "frustrated" or "just
  take a passive approach and not do things any differently" [17].
- **Regulated or fixed-scope work.** [regulated-work.md](regulated-work.md) says what a regulator or
  a contract adds.
- **What following the rules costs.** A LeSS adoption changes structure, with "explosive politics"
  [5], and "LeSS Huge adoptions take months or years" [2]. One backlog and one Product Owner put the
  ordering of the whole product on one person, and LeSS moves to LeSS Huge at the point where one
  person can no longer do that [4]. The cost of a SAFe adoption: no source the research could read
  gives one.

Not covered yet. The research for this file found no source it could read on these, or did not
read one:

- A measured point at which a second team pays off. The owners give sizes, a team of "typically 10
  or fewer people" [1], Basic LeSS for 2 to 8 teams [2] and a train of 5 to 15 teams [7], and no
  study read measures where a split starts to pay.
- What adopting LeSS or SAFe costs, in time or money, from a study.
- How a group moves from component teams to feature teams step by step: the LeSS pages read give
  the rule, not the steps.
- How an organisation rolls out SAFe past Essential SAFe: the owner pages read give the
  configurations, not the steps.
- The size of a team or a train in AI-Native SAFe: the two posts read give none [8], [9].

## 7. Alternatives considered

- **Starting LeSS small, with a pilot of a few teams.** Not taken: LeSS's rules ask for the complete
  structure for the product group "at the start" [2]. Its "better, smaller, and simpler" line is
  about LeSS against LeSS Huge, and "more with less" is about roles, artifacts and processes [4].
  This practice's default, "add as little structure as the work needs" (section 1), decides whether
  to adopt a framework and which one, not how much of LeSS to adopt.
- **"Scale only when one team cannot hold the product" as an owner's rule.** No owner text read says
  it in these words. It is this practice's reading of the Scrum Guide's growth rule [1], and it
  stays, marked as this practice's own.
- **Picking the framework that most organisations use.** Not taken: a share measures use, not
  results ([choosing-an-approach.md](choosing-an-approach.md) section 3).
- **The Spotify model as a scaling framework.** Not taken: Kniberg calls it an example of one
  company, not a framework [22] (section 5).
- **Nexus, Scrum@Scale, Disciplined Agile and other frameworks.** Not covered. Nexus is the scaling
  framework Ken Schwaber and Scrum.org develop [13]. No study read shows any of them ahead of LeSS,
  SAFe or no framework (section 4). Nexus is not described here because, for "approximately three
  to nine Scrum Teams", it states that "A Nexus works off a single Product Backlog" and that "a
  Product Backlog has a single Product Owner" [13], which section 1 already holds, and this file
  does not describe Nexus's own events. A reader who weighs another framework reads its owner's
  text against section 1.

## 8. Adoption in a group that already has teams

The answer is **new and touched code** ([refactoring.md](../refactoring/refactoring.md)
section 7), read here as new and changed team structures: the rules apply the next time a group
adds a team, splits one or picks a framework. A structure nobody changes waits, and a group that
runs a framework keeps it until a problem names a reason to change (section 6).

## 9. How an agent applies it

The project's `CLAUDE.md` routes an agent here with the line in [README.md](README.md), "How to
adopt". What an agent does in this work:

- **Give each claim its kind.** An owner's text settles how LeSS or SAFe works. A vendor's figure, a
  critic's view and a survey share are labelled as what they are (section 3).
- **Never say that one framework works better.** No study read shows it (section 4). An agent asked
  "should we adopt SAFe?" answers with the tests of sections 1 to 3.
- **Do not propose a second team or a framework for a product that one team holds** (section 1).

The research found no source on the mistakes agents make in this work.

## 10. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Ken Schwaber and Jeff Sutherland — The Scrum Guide, November 2020 — https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf — checked 2026-10-30
- [2] LeSS — LeSS Rules, November 2024 — https://less.works/less/rules
- [3] LeSS — What is LeSS? — https://less.works/less/framework/index
- [4] LeSS — Introduction to LeSS (chapter 2 of the book Large-Scale Scrum: More with LeSS) — https://less.works/less/framework/introduction
- [5] LeSS — Adopting LeSS — https://less.works/less/adoption/index
- [6] Scaled Agile — SAFe 6.0 Configurations — https://framework.scaledagile.com/safe-6-0-configurations
- [7] Scaled Agile — Essential SAFe — https://framework.scaledagile.com/essential-safe/
- [8] Andrew Sales — New Release: AI-Native SAFe is the Operating Model for the AI-Native Organization (Scaled Agile Framework blog, 2026; opinion) — https://framework.scaledagile.com/blog/ai-native-safe-is-the-operating-model-for-the-ai-native-organization
- [9] Andrew Sales — SAFe Summit Keynote Recap: Launching The Operating Model for the Age of AI (Scaled Agile Framework blog, 2026; opinion) — https://framework.scaledagile.com/blog/safe-summit-keynote-recap-launching-the-operating-model-for-the-age-of-ai
- [10] Scaled Agile — What is SAFe? — https://scaledagile.com/what-is-safe/
- [11] Ken Schwaber — unSAFe at any speed (Ken Schwaber's Blog, 2013; opinion) — https://kenschwaber.wordpress.com/2013/08/06/unsafe-at-any-speed/
- [12] Ken Schwaber — My Approach to Scrum at Scrum.org (Ken Schwaber's Blog, 2025; opinion) — https://kenschwaber.wordpress.com/2025/02/07/my-approach-to-scrum-at-scrum-org/
- [13] Ken Schwaber and Scrum.org — Nexus Guide, January 2018 — https://scrumorg-website-prod.s3.amazonaws.com/drupal/2018-01/2018-Nexus-Guide-English.pdf — checked 2026-10-30
- [14] The Agile Manifesto's authors — Manifesto for Agile Software Development, 2001 — https://agilemanifesto.org/
- [15] Ron Jeffries — Issues with SAFe (ronjeffries.com, 2014; opinion) — https://ronjeffries.com/xprog/articles/issues-with-safe/
- [16] Kim Dikert, Maria Paasivaara and Casper Lassenius — Challenges and success factors for large-scale agile transformations: A systematic literature review (Journal of Systems and Software, 2016; research) — https://doi.org/10.1016/j.jss.2016.06.013, read in the Aalto University copy of the version of record, https://acris.aalto.fi/ws/portalfiles/portal/11744469/1_s2.0_S0164121216300826_main.pdf
- [17] Kieran Conboy and Noel Carroll — Implementing Large-Scale Agile Frameworks: Challenges and Recommendations (IEEE Software, 2019; research) — https://doi.org/10.1109/MS.2018.2884865, read in the authors' preprint, https://arxiv.org/abs/1901.08130v1
- [18] Henry Edison, Xiaofeng Wang and Kieran Conboy — Comparing Methods for Large-Scale Agile Software Development: A Systematic Literature Review (IEEE Transactions on Software Engineering, 2022; kind not confirmed) — https://doi.org/10.1109/TSE.2021.3069039, abstract read in the University of Galway record, https://research.universityofgalway.ie/en/publications/comparing-methods-for-large-scale-agile-software-development-a-sy-4/
- [19] Christiaan Verwijs and Daniel Russo — Do Agile scaling approaches make a difference? An empirical comparison of team effectiveness across popular scaling approaches (Empirical Software Engineering, 2024; research; the first author declares a financial interest in The Liberators BV) — https://doi.org/10.1007/s10664-024-10481-5, text read in the preprint, https://arxiv.org/abs/2310.06599v1, and the journal's abstract in its Crossref record
- [22] Henrik Kniberg — No, I didn't invent the Spotify model (Crisp's Blog, 2015; opinion) — https://blog.crisp.se/2015/06/07/henrikkniberg/no-i-didnt-invent-the-spotify-model
- [23] Jeremiah Lee — Spotify's Failed #SquadGoals (jeremiahlee.com, 2020; case) — https://www.jeremiahlee.com/posts/failed-squad-goals/
- [24] LeSS — Three Principles (Adopting LeSS) — https://less.works/less/adoption/three-principles — checked 2026-10-30
