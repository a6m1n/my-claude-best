# Choosing an approach: the models, who chooses, and the evidence

The models a group can use to weigh a development approach, who chooses at the level of the
project and at the level of the team, and what research has measured about the choice and its
outcomes. Read it when a deliverable could fit more than one approach, when someone proposes one
method for every team, or when someone says a survey or a study proves one approach best.

**Navigation**

- [1. What this file holds, and what life-cycle.md section 4 owns](#1-what-this-file-holds-and-what-life-cyclemd-section-4-owns)
- [2. The models behind the choice](#2-the-models-behind-the-choice)
- [3. Who chooses](#3-who-chooses)
- [4. What measured practice says about choosing](#4-what-measured-practice-says-about-choosing)
- [5. What the evidence says about outcomes](#5-what-the-evidence-says-about-outcomes)
- [6. Common mistakes](#6-common-mistakes)
- [7. Where the rules stop holding, and what is not covered yet](#7-where-the-rules-stop-holding-and-what-is-not-covered-yet)
- [8. Alternatives considered](#8-alternatives-considered)
- [9. Sources](#9-sources)

**When you do not need this file.** The pick itself is made in
[life-cycle.md](../project-management/life-cycle.md) section 4: predictive, adaptive or hybrid for
each deliverable, and Scrum or a Kanban flow for the adaptive part. When the people who plan the
project agree on that pick and nobody disputes who decides how the team works, that section is
enough, and this file adds only background. Read on when the pick is argued: a deliverable sits
between two approaches, the team and the organisation disagree on who decides, or someone cites a
survey share or a success rate as proof.

## 1. What this file holds, and what life-cycle.md section 4 owns

[life-cycle.md](../project-management/life-cycle.md) section 4 owns two rules: the pick of a
predictive, adaptive or hybrid approach for each deliverable of the WBS, and the pick of Scrum or a
Kanban flow inside the adaptive part, together with its quotes of the Agile Practice Guide and the
PMP exam outline. This file holds what lies behind those rules: the models a group can use to weigh
the pick (section 2), who chooses at each layer (section 3), what research measured about how
teams choose (section 4), and what it measured about outcomes (section 5). It links section 4
wherever it needs one of those rules and never restates them. It is for everyone who takes part in
the pick: a project manager, a sponsor, a team, and an agent asked which approach to use.

The one rule: **keep the two layers apart. The project weighs an approach for each deliverable by
the work, with the people involved; the team chooses how it works inside the adaptive part. No
model, survey or study settles either pick on its own.**

Why it holds the rest together:

- PMI's seventh PMBOK edition ties the approach to the work, not to a person: "The project
  deliverables determine the most appropriate development approach such as a predictive, adaptive,
  or hybrid approach" [1]. The PMI texts read since then name no decider either (section 3).
- The owners of the team frameworks give the way of working to the team. Scrum Teams "internally
  decide who does what, when, and how" [2], and "No one outside of the Scrum Team should tell
  the Scrum Team how to define their Workflow" [3].
- The Agile Practice Guide says its own suitability filters "should not be used as definitive
  inclusion or exclusion gates" [4], and the outcome comparisons found for this file are
  surveys of past projects that do not agree on a winner on cost and time (section 5).

What it leaves out on purpose, and where that lives:

- Where the approach is written in the plan:
  [project-plan.md](../project-management/project-plan.md) section 2. A filled entry is in
  [project-example.md](../project-management/project-example.md) section 3.
- One decider for each kind of decision, and the decision log:
  [roles-and-decisions.md](../project-management/roles-and-decisions.md) sections 5 and 7.
- How one team combines approaches: [combining-approaches.md](combining-approaches.md). Many teams
  on one product: [scaling.md](scaling.md). A regulator, a safety standard or a fixed-scope
  contract: [regulated-work.md](regulated-work.md).
- The evidence on single practices, such as pair programming and test-first work:
  [extreme-programming.md](extreme-programming.md). What has been measured about AI agents:
  [ai-agents.md](ai-agents.md).
- Security: there are no known security impacts of the models and rules in this file. The
  practice's note on security is in [README.md](README.md).

Section 7 lists what the research for this file looked for and could not read.

## 2. The models behind the choice

When you weigh the pick for a deliverable, use a model as the agenda of a conversation among the
people involved, never as a score that decides, because each model shows one view of the work.
The Agile Practice Guide says the same of its own filter: "no single person" should assess the
suitability of an approach, "since any one person will also have a limited view with a bias"
[4]. It asks a group to fill in its
questionnaire: "For small projects, this group may simply be the sponsor, technical lead, and a
customer" [4]. None of the models below makes the pick; section 4 of
[life-cycle.md](../project-management/life-cycle.md) does, by its criteria.

### Boehm's home grounds, balanced by risk

Barry Boehm's 2002 conference slides set agile and plan-driven methods side by side, on a slide
titled "Agile and Plan-Driven Home Grounds" [5]. The agile home ground has "Largely emergent
requirements, rapid change", "Refactoring inexpensive", "Smaller teams, products" and a "Premium on
rapid value" [5]. The plan-driven home ground has "Requirements knowable early; largely
stable", "Refactoring expensive", "Larger teams, products" and a "Premium on high-assurance"
[5]. The slides then
weigh the risk of planning too little ("oversights, delays, rework") against the risk of planning
too much ("value capture delays"), and look for the "Sweet Spot" between the two [5].

- **What it is for:** placing a deliverable between the two home grounds, and asking how much
  planning its risks call for.
- **What it is not:** a finding. "No one-size-fits-all solution" is a heading in the slides'
  outline, under "Using Risk to Balance Discipline and Agility", not a result the slides measure
  [5]. The slides are one author's view, from 2002.
- **Use it when** the group disagrees on how much to plan up front: each column names what one
  side assumes.
- **Leave it out when:** the research for this file found no case where it is too much.

Boehm and Turner later named five factors for the same choice. Mark Paulk, a researcher at
Carnegie Mellon, sums them up: "Boehm and Turner identified five critical factors in determining
whether agile methods or a plan-driven method was likely to be more suitable for a project: size,
criticality, dynamism, personnel, and culture" [6]. The 2017 Agile Practice Guide says that
Boehm and Turner "adopted some of the elements from DSDM and Crystal to develop a popular
assessment model", and builds its own model on such earlier ones [4]. Their book, Balancing
Agility and Discipline (2004) [6], was not read for this file, so the five factors are named
here and not explained (section 7).

### The Agile Practice Guide's suitability filters

The first edition of the Agile Practice Guide (PMI and Agile Alliance, 2017) says that "Various
assessment models exist to help determine the likely fit or gaps for using agile approaches", and
gives its own synthesis in Annex X3 [4]. The model asks questions in three categories [4]:

| Category | The guide's question |
|---|---|
| Culture | "Is there a supportive environment with buy-in for the approach and trust in the team?" |
| Team | "Is the team of a suitable size to be successful in adopting agile, do its members have the necessary experience and access to business representatives to be successful?" |
| Project | "Are there high rates of change? Is incremental delivery possible? How critical is the project?" |

The model uses all three. The answers are plotted on a radar chart: "Clusters of values around the
center of the chart indicate a good fit for agile approaches", "Results around the outside indicate
a predictive approach may be more suitable", and values in the middle "indicate a hybrid approach
could work well" [4].

- **What it is for:** in the guide's words, "the value of the tool is the conversation it
  encourages with the invested parties of the project" [4].
- **What it is not:** a gate. "They should not be used as definitive inclusion or exclusion gates,
  but instead as topics for objective discussion with all interested parties" [4]. When the
  stakeholders want another approach than the chart shows, the guide says to "follow the stakeholder
  consensus", and calls the tool "a high-level diagnostic only" [4].
- **Use it when** a deliverable's fit is argued and the group needs one shared list of questions.
- **Leave it out when:** the guide names no case.

The second edition came out in 2026. Agile Alliance says it covers "fit-for-purpose approach
selection, and tailoring guidance", and that it "is only available for download to active members
of Agile Alliance" [7]. It was not read for this file, so this section follows the first
edition, and whether the second keeps the filters and the gate sentence is not known (section 7).

### Cynefin

The Cynefin wiki says: "Cynefin® is at its heart a decision support framework, not a method or
model" [8]. The framework is "a way of determining what method or approach you should adopt
and, critically, when you should change it" [8], and its full version "has five domains"
[8]. The wiki defines them, and ties a type of practice to each [9]:

| Domain | What the wiki says it is | The practice the wiki ties to it |
|---|---|---|
| Clear | "the relationship between cause and effect is self-evident and clear to any reasonable person" | "the only legitimate application of best practice" |
| Complicated | the relationship exists, but "discovering it requires expertise or analysis" | "good practice" |
| Complex | "Complex has enabling constraints"; the only way to understand the system "is to interact" [8] | "exaptive", the "radical re-purposing of existing capability" |
| Chaos | "the absence of effective constraint" | "generally novel" |
| Confusion | "the central domain of confusion" | in its liminal area, "aporetic" |

- **What it is for:** asking what kind of problem a deliverable is, and noticing when it moves to
  another domain, so the approach can change with it.
- **What it is not:** a method, and not a table that maps named methods to domains. The two wiki
  pages read name no software method for any domain; a claim that Scrum belongs to the complex
  domain is the writer's own mapping.
- **Leave it out when:** the pages read name no case.

### The Agile Fluency model

James Shore and Diana Larsen describe four zones of fluency, each named by the benefit a team
delivers [10]. The zones are choices, not steps: "Unlike maturity models, where more mature
is always better, the fluency model describes a collection of choices. Each zone represents a
fully-mature choice" [10]. In The Art of Agile Development, Shore and Warden add that "each
zone may be chosen independently" and advise: "choose only the zones your company both needs and is
willing to pay for" [11].

| Zone | What it means | Choose it when | Leave it out when |
|---|---|---|---|
| Focusing | "The team thinks and plans in terms of the benefits their sponsors, customers, and users will see from their software" [10] | Always, for an agile team: "Every Agile team needs Focusing fluency" [11] | The company cannot invest in it; then "Agile probably isn't a good fit" [11] |
| Delivering | "The team can release their latest work, at minimal risk and cost, whenever the business desires" [10] | The team must "modify and enhance their software for more than a few months" [10] | The team does not maintain its software long-term; Focusing is "a good fit" for such teams [10] |
| Optimizing | "The team understands what their market wants, what your business needs, and how to meet those needs" [10] | The organisation wants "to set the pace of change in their market" [10] | The organisation will not change its structure: the zone "requires disruptive changes to organizational structure" [10] |
| Strengthening | "The team understands its role in the larger organizational system and actively works to make that system more successful" [10] | Leaders "want to innovate management theory and practice" [10]; Shore and Warden call the zone "largely speculative: a possible future for Agile" [11] | The organisation is not "on the bleeding edge of management theory and practice" [11] |

- **What it is for:** deciding how far a team's way of working should go, by the benefit the
  organisation needs and the price it will pay.
- **What it is not:** a ladder or a maturity model. Shore and Larsen call that reading "a mistake"
  [10]. It does not choose between predictive and adaptive work either; it starts once the work
  is agile.

## 3. Who chooses

Two sets of sources answer two different questions. PMI's texts are about which approach a
deliverable gets. The Scrum Guide, the Kanban Guide for Scrum Teams and named practitioners are
about who decides how a team works inside the adaptive part. The two sets do not contradict each
other, so this file keeps both as layers and never averages them into one decider.

### The project layer

In planning, give the approach of each deliverable its decider by
[roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5, because none of
the PMI texts read says who decides it. The pick follows
[life-cycle.md](../project-management/life-cycle.md) section 4, and a change to it goes into the
decision log of [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 7.

What PMI's texts say:

- The PMI Lexicon (version 5.0) defines a development approach as "A method used to create and
  evolve the product, service, or result during the project life cycle such as an adaptive,
  predictive, or hybrid method", and no entry in it says who selects one [12].
- PMBOK 8 (2025) holds the topic in at least three places, by the headings of its free table of
  contents: section 4.3 of The Standard for Project Management, "Considerations for a Development
  Approach Selection", with parts named "Deliverables", "Project" and "Organization"; section 3.3.1
  of the Guide, "Life Cycle and Development Approach Selection", under "What to Tailor"; and
  section 3.4.1 of the Guide, "Select Initial Development Approach" [13]. The headings sort the
  topic by what is weighed, not by who decides. The bodies are paid and were not read.
- PMBOK 7 (2021, now superseded): "The project deliverables determine the most appropriate
  development approach such as a predictive, adaptive, or hybrid approach" [1].
- PMI's FAQ on PMBOK 7, from 2020 and also superseded, names practitioners:
  "Practitioners are now tasked with identifying the right delivery approach (predictive, adaptive,
  or hybrid) to get the job done and deliver value" [14].
- The PMP exam outline for July 2026 lists "Recommend a project management development approach
  (i.e., predictive, adaptive/agile, or hybrid management)" under the project manager's Task 1,
  "Develop an integrated project management plan and plan delivery" [15]. It is an enabler, which
  the outline defines as "Illustrative examples of the work associated with the task" [15]. The
  verb is recommend: the outline gives the project manager the recommendation and does not say who
  decides.
- The 2017 Agile Practice Guide, now superseded, says of its questionnaire that "the final decision
  should rest and be supported by the people involved" [4].

So at this layer the project manager recommends, a group weighs the fit, and the project names its
decider itself.

### The team layer

From the first day of the adaptive part, let the team choose how it works and keep tuning it: its
practices, its workflow and its working agreements, inside the adaptive approach the project picked.
Never impose a method on a team that does not want it. The reason: the owners of the team
frameworks put the way of working with the team [2], [3], and Fowler holds that an
imposed process is "often resisted" [16].

What the sources say:

- The Scrum Guide (2020): Scrum Teams are "self-managing, meaning they internally decide who does
  what, when, and how" [2].
- The Kanban Guide for Scrum Teams (2021): "Creating and adapting the Definition of Workflow is the
  accountability of the relevant roles on the Scrum Team as described in the Scrum Guide. No one
  outside of the Scrum Team should tell the Scrum Team how to define their Workflow" [3].
- Martin Fowler holds that "Often software processes are imposed by management figures. As such
  they are often resisted", that "only the developers themselves can choose to follow an adaptive
  process", and that "each team should not just choose their own process, but should also actively
  tune their process as they proceed with the project" [16]. From this he concludes that "you
  should never try to impose agile working on a team that doesn't want to try it" [16]. In
  2018 he put it as "the team doing work decides how to do it. That is a fundamental agile
  principle" [17].
- Ron Jeffries holds that "Too commonly, the 'Agile' approach a team uses has been imposed", and
  writes: "If I were starting a company, I'd let the teams choose any process they wish" [18].
- Ken Schwaber, a co-author of the Scrum Guide, answered a reader on his blog in 2018, in a thread
  about standardising practices: "I believe that each organization, team, and project will select
  the best approach and processes" [19]. He names the organisation and the project as
  choosers too, which fits two layers better than one.

[life-cycle.md](../project-management/life-cycle.md) section 4 gives the criterion for Scrum or a
Kanban flow inside the adaptive part; by the sources above, the team applies it to its own work.

**When the team does not want to work in an agile way at all, take the case back to the
deliverable's decider** ([roles-and-decisions.md](../project-management/roles-and-decisions.md)
section 5), who weighs the deliverable's approach again with the team's answer as an input and
records the result in the decision log (section 7 there). Why: Fowler holds that "you should never
try to impose agile working on a team that doesn't want to try it" [16], so the adaptive pick is
weighed again, not imposed. This routing is this practice's own reading.

Check: in a retrospective ([meetings.md](../project-management/meetings.md) section 8), ask who set
the team's current way of working. An answer that names someone outside the team means the team
layer was imposed.

### Is Scrum the default?

Of the 845 HELENA participants who answered the question on methods (1,467 data points in all,
collected in 2017 "following a convenience sampling strategy"), 674 selected Scrum, "the most
frequently selected method" [21]. The survey counts use in a sample that is not random, and does
not measure whether Scrum works better. A usage share is therefore no reason to make Scrum the
default for every team: at the team layer the team decides how it works, and the pick between
Scrum and a Kanban flow follows the criterion in
[life-cycle.md](../project-management/life-cycle.md) section 4, not a share.

## 4. What measured practice says about choosing

Three studies looked at how a method gets chosen. They agree that the choice depends on the
context of each project, and none gives a checklist that settles it.

- Kalus and Kuhrmann's 2013 systematic literature review presents "a collection of 49 tailoring
  criteria" and finds that "the consequences of the criteria remain abstract and need to be
  interpreted on a project-per-project basis" [22]. Its introduction notes that "in the field of
  agile methods no common guideline is available to support the selection of concrete agile
  practices", and its conclusion says: "Our results do, so far, not allow for explaining how
  concrete actions affect a software project" [22].
- The abstract of Klünder et al. (ICSSP 2020), the only part read, reports an analysis of 829 data
  points from the HELENA dataset. It calls "Selecting a suitable development method for a specific
  project context" "one of the most challenging activities in process design", and reports that
  the trained models reveal "only a few context factors, e.g., project/product size and target
  application domain, that seem to significantly influence the selection of methods" [23].
- Gren, Wong and Kristoffersson, in a 2019 preprint, studied 21 ERP implementations from 20
  companies; the 10 agile ones were "close to the only ones existing in the world within SAP"
  [24]. Project managers filled in a survey on projects the decision-makers had judged
  "successful, but borderline" [24]. The assessments "did not differ on any aspects except higher
  executive buy-in for process change, and the prioritization of low cost in the agile projects",
  and the data show that the decision-makers "could not make such a decision at an early point in
  time without contextual knowledge" [24].

The first is a catalogue of criteria, the second measures what teams were seen to pick, and the
third is a small study of ERP projects around one vendor's product, so they do not contradict each
other. The third adds that an early pick can lack the knowledge it needs. That is one reason to
write each pick down with its reason, as [life-cycle.md](../project-management/life-cycle.md)
section 4 asks.

## 5. What the evidence says about outcomes

The comparisons of approaches found for this file are surveys of past projects, not trials, and
they do not agree on a winner on cost and time. They differ in their groups, their measures and
their samples, so each one is shown here with its kind and its context, and none is averaged with
another into one verdict, such as that agile wins or that there is no difference. The pick does
not rest on them: [life-cycle.md](../project-management/life-cycle.md) section 4 picks by its
criteria.

### Agile, hybrid and traditional projects as groups

- Gemino, Reich and Serrador (Project Management Journal, 2021) were read only in their abstract.
  It reports "an international study, including 477 cross-industry projects", in which "52% of
  projects could be categorized as hybrid approaches" [25]. Its analysis "suggested that hybrid
  and agile approaches significantly increase stakeholder success over traditional approaches while
  achieving the same budget, time, scope, and quality outcomes" [25]. The abstract does not say who
  rated the outcomes, how each project's approach was classed, or whether project size was
  controlled, so the design cannot be judged from what was read.
- Jørgensen (IEEE Software, 2019) was read in the author's accepted manuscript. The projects came
  from "Norwegian software professionals visiting three different seminars on project management in
  2016 and 2017", each describing their last completed project, 196 in all [26]. Whether a
  project was agile was "the respondents' own perception", and each respondent rated the project's
  performance "as he/she perceived it" [26]. Size is the budget: under 1 million euro, 1 to 10
  million, and over 10 million [26]. He found that "the difference in proportion acceptable
  projects is statistically significant, with agile being more successful, for small (p<0.01) and
  medium (p=0.03) sized projects, but not for large sized projects (p=0.12)" [26]. The abstract
  says agile projects did better "for all examined project size categories" [26]. That holds
  for the point estimates; the test is significant only for small and medium projects, and the large
  band holds 22 projects [26]. The author limits the result himself: most respondents came from
  "large organizations with mainly administrative software applications", so "the results may mainly
  be valid within this context" [26].

### Does the advantage grow with size?

The data do not show it. Jørgensen counts a project as acceptable when it is "Acceptable or better
on all five success dimensions": client benefits, cost control, time control, productivity and
technical quality [26]. In his 2019 table, that share is 65% for agile and 19% for non-agile
among small projects, 58% and 31% among medium ones, and 50% and
25% among large ones [26]. The gap narrows from 46 to 25 points as budgets grow. His 2018
conference paper, on an earlier sample of people visiting a seminar on software project management
("a convenience sample", 122 projects in the abstract and 101 valid responses in the body), read the
other way on small projects: agile projects "performed on average much better than those using
non-agile methods for medium and large software projects, but not so much for smaller projects"
[27]. Dybå and Dingsøyr's 2008 systematic review of 36 empirical studies, up to and including
2005, found that "agile methods not necessarily are the best choice for large projects", and graded
the strength of the evidence on the benefits and limitations of agile methods "very low" [28]. The
size question is open, and no rule in this practice rests on it.

### Does agile cost efficiency?

Three sources point three ways, and their designs differ:

- Gemino, Reich and Serrador's abstract reports "the same budget, time, scope, and quality outcomes"
  for hybrid, agile and traditional projects [25].
- Serrador and Pinto (International Journal of Project Management, 2015) were read only in APM's
  summary of their paper. The data came from an online questionnaire "which members of the Project
  Management Institute (PMI) and certain LinkedIn groups were invited to complete", on "over 1,000
  projects"; each respondent described "one more successful and one less successful project"
  [29]. The summary reports "a correlation between using agile methods and the success of
  projects", says that agile methods "are more likely to make the project successful in meeting cost
  and time targets", and adds that "more investigation is needed" [29]. The respondents chose
  themselves and the design is correlational, so it shows a link, not a cause.
- Kakar and Kakar (HICSS, 2023) were read only in their abstract: "a survey with team members of 58
  software development project in one of the largest global IT firms" [30]. The abstract reports
  that the agile principles "were negative correlated with project efficiency", while they were
  positively correlated with team motivation, project effectiveness and innovation [30]. It is
  one firm, and the abstract does not say how efficiency was measured.

### What was not found, and what this file does not cite

- The research for this file found no peer-reviewed study from 2024 to 2026 that compares the
  outcomes of Scrum, Kanban, XP, plan-driven and hybrid work head to head. Several candidates sat
  behind publishers' access blocks and were not read, so this is a finding about what could be
  read. Older comparisons exist, the two journal studies above among them.
- This file cites no Standish CHAOS figure. Eveleens and Verhoef applied the Standish definitions to
  "5,457 forecasts of 1,211 real-world projects" and found that "the Standish definitions of
  successful and challenged projects have four major problems: they're misleading, one-sided,
  pervert the estimation practice, and result in meaningless figures" [31]. Hanslo and
  Tanner, in a 2026 preprint, note that "the Standish Group's full investigation is not made
  available for researchers to review" [32]. A success rate nobody can check cannot back a
  rule.

## 6. Common mistakes

| Mistake | Why people make it | What it costs | Fix |
|---|---|---|---|
| Picking an approach because a survey says most teams use it | A large share reads like a verdict | The survey counts use in a sample that is not random [21], and says nothing about the deliverable at hand | Weigh the deliverable by [life-cycle.md](../project-management/life-cycle.md) section 4; section 3 here |
| Treating a suitability filter's score as a gate | A radar chart looks like a measurement | The guide says the filters "should not be used as definitive inclusion or exclusion gates" [4], and one person's score carries "a limited view with a bias" [4] | Fill it in as a group and use it as an agenda (section 2) |
| Claiming that one approach is proven best | Single studies report agile or hybrid ahead | The comparisons are surveys of past projects, they disagree on efficiency and on size, and the 2008 review graded the evidence "very low" [28] | Show the evidence with its kinds (section 5), and pick by [life-cycle.md](../project-management/life-cycle.md) section 4 |
| Reading the Agile Fluency zones as a ladder every team must climb | The book's figure shows "a straightforward path from one zone to the next" [11] | The organisation pays for zones it does not need; Shore and Larsen call the maturity-model reading "a mistake" [10] | Choose the zones the organisation needs and will pay for (section 2) |
| Citing a CHAOS success rate | It is the best-known number on project success | The definitions "result in meaningless figures" [31], and the data are closed to researchers [32] | Cite a study whose method can be read (section 5) |

## 7. Where the rules stop holding, and what is not covered yet

- **A regulator, a safety standard or a fixed-scope contract** can fix parts of the project layer
  before any model is weighed: [regulated-work.md](regulated-work.md).
- **Many teams on one product.** The scaling frameworks and their evidence are in
  [scaling.md](scaling.md).
- **A team that does not want to work in an agile way.** What that means for the pick is in
  section 3, "The team layer".
- **What the team layer costs.** A team that chooses its own way of working needs the skill to do
  it. Boehm's agile home ground assumes "Agile, knowledgeable, collocated, collaborative developers"
  [5]. In Shore and Larsen's experience of coaching teams, "it takes a team two to six months to
  become fluent in the Focusing zone", and the Delivering zone "takes another 3-24 months" [10].
  Until then, the team's choice rests on less knowledge, and the group conversation of section 2
  matters more.
- **What the group conversation costs.** Even on a small project it takes the time of "the
  sponsor, technical lead, and a customer" [4].

Not covered yet. The research for this file looked for these and found no source it could read:

- Boehm and Turner's own text. The five factors are known here only through Paulk [6] and the
  2017 Agile Practice Guide [4].
- The 2026 Agile Practice Guide, which only members can download [7]: whether it keeps the
  suitability filters and the gate sentence.
- The bodies of PMBOK 8's sections 4.3, 3.3.1 and 3.4.1 [13]: whether PMBOK 8 names who decides
  the approach.
- Who tailors the method in PRINCE2 7: no PeopleCert text read says so.
- SWEBOK, version 4: the page that offers it refused the request, so its text was not read.
- A study that compares methods a team chose with methods imposed on it: none was found.
- A peer-reviewed comparison of the approaches' outcomes from 2024 to 2026 (section 5).
- The full texts of Gemino, Reich and Serrador [25], Klünder et al. [23], Serrador and
  Pinto [29] and Kakar and Kakar [30], and the print version of Jørgensen's 2019 paper
  [26], whose wording or numbers may differ from the manuscript.

## 8. Alternatives considered

- **Pick by the most used method.** Not taken: the survey counts use in a sample that is not
  random, not results (section 3).
- **Pick by an outcome comparison.** Not taken: the comparisons are surveys of past projects with
  different designs, and they disagree (section 5).
- **Pick by a CHAOS success rate.** Not taken: the figures cannot be checked (section 5).
- **Let the suitability filter's score decide.** Not taken: the guide that defines the filters says
  they are not gates [4].
- **One decider for the approach and for the team's way of working.** Not taken: the project-layer
  and team-layer sources answer different questions. One decider for both would either let the
  project set the team's practices or let the team override the approach a deliverable needs
  (section 3).
- **Kalus and Kuhrmann's 49 criteria as a checklist.** Not taken: the review itself says the
  consequences of the criteria "remain abstract" [22].
- **Boehm and Turner's five factors as the model of this file.** Not taken: their book was not read.
  The 2017 guide's filter, which builds on their model and others [4], was read instead.

## 9. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] PMI — Project Performance Domains, from the PMBOK Guide, seventh edition — https://www.pmi.org/-/media/pmi/documents/public/pdf/pmbok-standards/pmi-project-performance-domains.pdf — checked 2026-10-30
- [2] Ken Schwaber and Jeff Sutherland — The Scrum Guide, November 2020 — https://scrumguides.org/scrum-guide.html — checked 2026-10-30
- [3] Scrum.org, Daniel Vacanti and Yuval Yeret — The Kanban Guide for Scrum Teams, January 2021 — https://scrumorg-website-prod.s3.amazonaws.com/drupal/2021-01/01-2021%20Kanban%20Guide.pdf — checked 2026-10-30
- [4] PMI and Agile Alliance — Agile Practice Guide, first edition, 2017; each page carries a watermark for Agile Alliance members, and the co-publisher serves the file — https://www.agilealliance.org/wp-content/uploads/2021/02/AgilePracticeGuide.pdf — checked 2026-10-30
- [5] Barry Boehm — CMMI and the Balance of Discipline and Agility, slides for the CMMI Technology Conference '02 (USC Center for Software Engineering, 2002; opinion) — https://ndia.dtic.mil/wp-content/uploads/2002/cmmi/boehm.pdf — checked 2026-10-30
- [6] Mark C. Paulk — On Empirical Research Into Scrum Adoption (Carnegie Mellon University, no date; opinion) — https://www.cs.cmu.edu/~mcp/agile/oersa.pdf — checked 2026-10-30
- [7] Agile Alliance — Agile Practice Guide, Second Edition (publication page) — https://agilealliance.org/agile-practice-guide-2nd-edition/ — checked 2026-10-30
- [8] Cynefin.io — Cynefin, revision 5860 — https://cynefin.io/index.php?title=Cynefin&oldid=5860 — checked 2026-10-30
- [9] Cynefin.io — Cynefin Domains, revision 5763 — https://cynefin.io/index.php?title=Cynefin_Domains&oldid=5763 — checked 2026-10-30
- [10] James Shore and Diana Larsen — The Agile Fluency Model: A Brief Guide to Success with Agile (martinfowler.com, 2018; opinion; the authors hold the Agile Fluency trademark and coach teams, as the text says) — https://www.martinfowler.com/articles/agileFluency.html — checked 2026-10-30
- [11] James Shore and Shane Warden — Choose Your Agility, a chapter of The Art of Agile Development, second edition (jamesshore.com, 2021; opinion) — https://www.jamesshore.com/v2/books/aoad2/choose_your_agility — checked 2026-10-30
- [12] PMI — PMI Lexicon of Project Management Terms, version 5.0 — https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf — checked 2026-10-30
- [13] PMI — PMBOK Guide and The Standard for Project Management (ANSI/PMI 99-001-2025), table of contents, eighth edition — https://www.pmi.org/-/media/pmi/documents/public/pdf/publications/pmbok-guide-eighth-edition_table-of-contents.pdf — checked 2026-10-30
- [14] PMI — PMBOK Guide – Seventh Edition FAQs — https://www.pmi.org/-/media/pmi/documents/public/pdf/pmbok-standards/pmbok-guide-external-faq.pdf — checked 2026-10-30
- [15] PMI — PMP Examination Content Outline, July 2026 exam — https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/new-pmp-examination-content-outline-2026.pdf — checked 2026-10-30
- [16] Martin Fowler — The New Methodology (martinfowler.com, 2005; opinion; the author's firm, Thoughtworks, uses an agile approach with its clients, as the text says) — https://martinfowler.com/articles/newMethodology.html — checked 2026-10-30
- [17] Martin Fowler — The State of Agile Software in 2018, transcript of a keynote at Agile Australia (martinfowler.com, 2018; opinion) — https://martinfowler.com/articles/agile-aus-2018.html — checked 2026-10-30
- [18] Ron Jeffries — Developers Should Abandon Agile (ronjeffries.com, 2018; opinion) — https://ronjeffries.com/articles/018-01ff/abandon-1/ — checked 2026-10-30
- [19] Ken Schwaber — reply of 17 May 2018 in the comments on "Scrum is simple, just use it as is!!" (Ken Schwaber's Blog, 2018; opinion, by a co-author of the Scrum Guide) — https://kenschwaber.wordpress.com/2017/11/11/scrum-is-simple-just-use-it-as-is/ — checked 2026-10-30
- [21] Paolo Tell et al. — What are Hybrid Development Methods Made Of? An Evidence-based Characterization (ICSSP, 2019; research) — https://arxiv.org/abs/2101.08016v1 — checked 2026-10-30
- [22] Georg Kalus and Marco Kuhrmann — Criteria for Software Process Tailoring: A Systematic Review (the authors' version of an ACM paper, 2013; research) — https://wwwbroy.in.tum.de/publ/papers/kk2013a.pdf — checked 2026-10-30
- [23] Jil Klünder et al. — Determining Context Factors for Hybrid Development Methods with Trained Models (ICSSP, 2020; kind not confirmed) — https://research.chalmers.se/en/publication/521731 — checked 2026-10-30
- [24] Lucas Gren, Alexander Wong and Erik Kristoffersson — Choosing agile or plan-driven enterprise resource planning (ERP) implementations: A study on 21 implementations from 20 companies (arXiv 1906.05220v1, 2019; research, preprint) — https://arxiv.org/abs/1906.05220v1 — checked 2026-10-30
- [25] Andrew Gemino, Blaize Horner Reich and Pedro M. Serrador — Agile, Traditional, and Hybrid Approaches to Project Success: Is Hybrid a Poor Second Choice? (Project Management Journal, 2021; kind not confirmed) — https://doi.org/10.1177/8756972820973082 — checked 2026-10-30
- [26] Magne Jørgensen — Relationships Between Project Size, Agile Practices, and Successful Software Development: Results and Analysis (IEEE Software, 2019, doi:10.1109/MS.2018.2884863; research; read in the author's accepted manuscript, titled "Relations between Project Size, Agile Practices and Successful Software Development") — https://cms.simula.no/sites/default/files/publications/files/swsi-2018-07-0123.r1_jorgensen.pdf — checked 2026-10-30
- [27] Magne Jørgensen — Do Agile Methods Work for Large Software Projects? (International Conference on Agile Software Development, 2018; research) — https://cms.simula.no/sites/default/files/publications/files/jorgensen-xp-research-paper-jan19-2018.pdf — checked 2026-10-30
- [28] Tore Dybå and Torgeir Dingsøyr — Empirical studies of agile software development: A systematic review (Information and Software Technology, 2008; research) — https://doi.org/10.1016/j.infsof.2008.01.006 — checked 2026-10-30
- [29] Pedro Serrador and Jeffrey K. Pinto — Does Agile work? A quantitative analysis of agile project success (International Journal of Project Management, 2015; kind not confirmed; read in APM's research summary of the paper) — https://apm.org.uk/media/r01fph3t/does-agile-work-a-quantitative-analysis-of-agile-project-success.pdf — checked 2026-10-30
- [30] Adarsh Kumar Kakar and Ashish Kakar — Have the Agile Principles Endured? An Empirical Investigation Post 20th Anniversary of the Agile Manifesto (2001) (HICSS-56, 2023; kind not confirmed) — https://aisel.aisnet.org/hicss-56/st/agile_development/3/ — checked 2026-10-30
- [31] J. Laurenz Eveleens and Chris Verhoef — The Rise and Fall of the Chaos Report Figures (IEEE Software, 2010; research) — https://www.cs.vu.nl/~x/chaos/chaos.pdf — checked 2026-10-30
- [32] Ridewaan Hanslo and Maureen Tanner — Predicting Agile Success: The Critical Few Factors (arXiv 2608.06228v1, 2026; research, preprint) — https://arxiv.org/abs/2608.06228v1 — checked 2026-10-30
