# Combining approaches: Scrumban, Water-Scrum-Fall and hybrids

This file is for anyone who writes down, changes or reviews how a team works when its process takes
parts from more than one approach: a developer, a Scrum Master, a project manager, and an AI agent
asked to describe "our process". It says why teams combine, what the two meanings of "Scrumban"
are and which one this practice uses, what to do when a Scrum team works inside a plan-driven
frame, and where a team starts. Which approach each deliverable gets is
[life-cycle.md](../project-management/life-cycle.md) section 4, and who chooses is
[choosing-an-approach.md](choosing-an-approach.md).

**Navigation**

- [1. Why teams combine](#1-why-teams-combine)
- [2. Scrum with Kanban: the two meanings of Scrumban](#2-scrum-with-kanban-the-two-meanings-of-scrumban)
- [3. Water-Scrum-Fall](#3-water-scrum-fall)
- [4. How hybrids form, and where to start](#4-how-hybrids-form-and-where-to-start)
- [5. Common mistakes](#5-common-mistakes)
- [6. Where the rules stop holding](#6-where-the-rules-stop-holding)
- [7. Sources](#7-sources)

**When you do not need this file.** A team that runs one approach as its owner's text describes
it, with no plan or release around it on another cadence, has no mix to name. The Scrum Guide asks
a team to "Try it as is and determine if its philosophy, theory, and structure help to achieve
goals and create value" [1], and [scrum.md](scrum.md) or [kanban.md](kanban.md) is all that team
needs. Read on when the process mixes parts from different texts, when someone calls it
"Scrumban" or "hybrid", or when a plan and a release step around the team follow their own rules.

## 1. Why teams combine

A team rarely runs one named approach exactly as its owner's text describes it. It runs Scrum with
a Kanban board, or Scrum inside a plan that was fixed before the team started. Each part comes from
a different text with different rules. Trouble starts when nobody says which part comes from
where: the team calls the mix "Scrumban" or "hybrid", and each reader fills in a different set of
rules. A project that follows this file names every part of its mix by the text it comes from,
keeps the rules of each part it says it runs, and never reads how common a mix is as evidence that
it works.

The one rule: **name each part of your mix by the text it comes from, and judge the mix by what it
does in your work, never by how many teams run one like it.**

Why teams combine, as the sources describe it:

- Kuhrmann et al., in the first stage of the HELENA survey (69 participants from about 15
  countries, most of them in Europe, a convenience sample, May to June 2016), concluded that hybrid
  approaches "are the results of a natural process evolution, which is mainly driven by
  experience, learning, and pragmatism" [2]. Section 4 says what that means for where a team
  starts.
- The same authors argue that a hybrid is also a way to balance what managers and developers
  expect from the process, or to stay flexible while the team follows a standard [2].
- Dave West holds that agile adoption has been "practitioner-led, leading teams to focus on
  domains they can influence, mainly the team itself", while project planning and release
  management around the team stay traditional [3].
- Scrum leaves room for additions. The Scrum Guide says Scrum "functions well as a container for
  other techniques, methodologies, and practices", and sets the limit in the sentence before it:
  "While implementing only parts of Scrum is possible, the result is not Scrum" [1].

How common combining is. The figures below come from the second stage of HELENA, an online survey
from May to November 2017, with a convenience sample promoted through the personal contacts of its
75 researchers, conference posters, mailing lists and social media [4], [5]:

- Klünder et al. found: "Of the 732 participants, 562 (76.8%) stated that they combine different
  development approaches into a hybrid method" [4]. The unit of analysis was "a specific project or
  product" [4], so the share counts projects and products, not companies, and the sample was not
  random.
- Kuhrmann et al. found that 83 of 556 data points, about 15%, ran every project discipline the
  same way: fully or mainly agile, fully or mainly traditional, or balanced [5]. The balanced cases
  are inside the 15%, so it is not a count of purely agile or purely traditional projects alone.
- Tell et al. found in the full set of 1,467 responses that "only eight methods and few practices
  build the core of modern software development" [6]. Among the 845 participants who answered the
  question on methods, 309 selected Scrum, Kanban and DevOps together, and 380 selected Scrum and
  Waterfall, the pair the authors call "Water-Scrum-Fall" [6].

These three papers share one dataset, so they count as one source that found this, not as several
studies that agree; the first-stage paper is an earlier, smaller round by the same group. The
shares count what participants said they use; a share does not show that a
mix works. The outcome evidence the research found is in
[choosing-an-approach.md](choosing-an-approach.md).

Check: before you share a plan or a process doc that cites a survey share, ask: does each share
name its sample, its unit (a team, a project, a company) and the year of its data?

What this file leaves out on purpose, and where it lives:

- Which approach each deliverable gets (predictive, adaptive or hybrid), and the pattern HELENA
  found most often, a traditional frame with agile practices plugged in:
  [life-cycle.md](../project-management/life-cycle.md) section 4.
- Who chooses the approach and the team's way of working:
  [choosing-an-approach.md](choosing-an-approach.md).
- What changing or dropping a part of Scrum costs: [scrum.md](scrum.md).
- The two definitions of Kanban, and how a Scrum team applies Kanban: [kanban.md](kanban.md).
- XP's engineering practices inside Scrum: [extreme-programming.md](extreme-programming.md).
- A mix shared by many teams: [scaling.md](scaling.md). A plan-driven frame that a regulator or a
  contract requires: [regulated-work.md](regulated-work.md).
- DevOps as a way of working of its own. Its delivery practices are
  [release.md](../project-management/release.md) section 5 and [ci-cd](../ci-cd/README.md).
- Security: there are no known security impacts of the combinations in this file. Moving release
  checks into the sprint (section 3) moves security tests with them, and how a pipeline runs them
  is [ci-cd](../ci-cd/README.md).

Not covered yet: four topics the research found no readable source for; section 6 lists them.

## 2. Scrum with Kanban: the two meanings of Scrumban

"Scrumban" names two different things. They give different answers to the question a reader needs
answered first: do Scrum's events, accountabilities and artifacts still hold? Ajay Reddy, who wrote
a book on Scrumban, notes that "several 'authoritative' sources disagree about what Scrumban
actually represents" [7]. His book names both meanings [7].

**Ladas's Scrumban: a path that starts from Scrum and leaves it.** Corey Ladas, whom Reddy calls
the "creator of Scrumban" [7], describes it in a 2008 essay that Agile Alliance republished in
2021. He holds that "it is possible to incrementally enhance Scrum with more and more pull-like
features until all that remains of the original process is vestigial scaffolding" [8]. The path
starts with Scrum's iterations and planning, adds limits on work in process and a ready queue, and
then goes past Scrum: "The first step beyond Scrum is to decouple the planning and release
periods" [8]. In remarks he added in 2021, Ladas says that "Scrumban is not a set of practices.
Scrumban is not a prescribed process" [9]. A team on the path "will eventually abandon one or more
Scrum practices" [9], and once it reaches reliable continuous delivery, "you have escaped from
Scrumban and are now practicing Lean production" [9]. Reddy reads him the same way: Ladas "defined
Scrumban as a transition method for moving software development teams from Scrum to a more evolved
development framework" [7]. The words "replaces most of Scrum" are not Ladas's. They are Chris
Sims's summary of the essay in InfoQ, with a condition attached: "which if taken far enough,
replaces most of Scrum" [10].

**Kanban inside Scrum: Scrum kept whole.** The Kanban Guide for Scrum Teams, by Scrum.org with
Daniel Vacanti and Yuval Yeret, adds Kanban practices to a team that already runs Scrum and takes
nothing away: "This guide does not replace or discount any part of The Scrum Guide", and "The Scrum
Guide applies in its entirety" [11]. The guide does not use the word "Scrumban" [11]. Reddy's own
Scrumban sits near this meaning, since it "prescribes an underlying software development process
framework (Scrum) as its core" [7]. The guide's practices, and how a Scrum team applies them, are
[kanban.md](kanban.md).

**The meaning this practice uses.** In this practice, "Scrumban" means Ladas's path out of Scrum,
and the layer inside Scrum is called Kanban inside Scrum. "Kanban inside Scrum" is this practice's
own name for the layer: the guide that owns the layer does not use it, and writes "Kanban in a
Scrum context" and "Teams using Scrum with Kanban", under a section headed "Kanban with Scrum
Theory" [11]. Why: "Scrumban" follows the text of Ladas, who made the word [7], and the guide does
not use that word [11]. For the layer, the guide has several phrases and no single name, so this
practice gives it one, which a plan writes in place of a "Scrumban" that means the layer (the check
below); that reason is this practice's own reading. Reddy's
sense, a framework with Scrum at its core [7], is not taken: one word for both meanings would bring
back the confusion this section is there to remove.

- **When you write "Scrumban" in a plan, a process doc, a ticket or a status update, say that you
  mean Ladas's path and list the practices the team runs today, or write "Kanban inside Scrum" if
  the team keeps Scrum whole.** Why: the two meanings disagree on whether Scrum's rules still hold,
  and Ladas's Scrumban has no fixed set of practices [9], so the word alone tells a reader neither
  what the team does nor which rules apply.
- **On Ladas's path, at the step where the team stops keeping the minimum of
  [scrum.md](scrum.md) section 4, write in the plan that the team no longer runs Scrum, and name
  what it runs instead.** Why: by the Scrum Guide, when only parts are implemented "the result is
  not Scrum" [1], and a reader who believes the team runs Scrum expects every event and
  accountability. What dropping a part costs is [scrum.md](scrum.md). The flow a team arrives at is [kanban.md](kanban.md) or
  [lean-software-development.md](lean-software-development.md).

Check: when you write or edit a plan or a process doc, search it for "Scrumban". Every hit says it
means Ladas's path and lists the practices run today, or it becomes "Kanban inside Scrum".

## 3. Water-Scrum-Fall

This section holds when a Scrum team works inside a frame it does not run: requirements and a plan
are fixed before the team starts, and the release to production keeps its own, slower cadence. Dave
West, then a vice president and research director at Forrester, described the pattern in a 2011
column [3]:

- Water: "Governance rules require many organizations to define requirements and plans before
  starting work" [3].
- Scrum: the team "is presented with a detailed project plan and a set of requirements that it then
  works through" [3].
- Fall: most organizations "do infrequent releases backed by heavy processes and governance" [3].

The pattern is common in the survey data: 380 of the 845 HELENA participants who answered on
methods selected Scrum and Waterfall together [6], and Kuhrmann et al. read their first-stage data
as support for "West's claim that the 'Water-Scrum-Fall' has become reality" [2].

West holds that the pattern "is not inherently bad", but that professionals "need to carefully
consider and make the right decisions about where the lines fall between water-Scrum and
Scrum-fall" [3]. The rules below follow his advice on both ends.

- **When the plan of such a project is written, write where the lines fall: what the up-front part
  fixes for governance, what the Scrum team decides on its own, and how its work reaches
  production.** Why: West holds that without that decision teams are "unlikely to realize agile's
  business benefits" [3]. The plan is where [life-cycle.md](../project-management/life-cycle.md)
  section 4 records the approach, and who decides is
  [choosing-an-approach.md](choosing-an-approach.md).
- **Push back on up-front work beyond what governance needs.** West asks professionals to "push
  back on the water-Scrum side of the model", because "Spending too much time upfront will not
  increase the quality of the release; on the contrary, it is wasteful" [3]. Documents written up
  front "should be just enough to introduce the problem area and allow high-level planning and
  development work to commence" [3].
- **Challenge infrequent releases: move release work into the sprint, step by step.** West holds
  that professionals should "challenge the status quo of infrequent releases and push to better
  integrate release processes into the development team", and add to sprints "such release process
  activities as preproduction testing, data migration, and security and performance testing" [3].
  Why: in his words, doing this in each sprint "gathers more rapid feedback for the team" and
  "encourages the team to automate these processes" [3]. How the team integrates and delivers is
  [release.md](../project-management/release.md) section 5.

When a regulator or a contract fixes the up-front part or the release gate, those lines are not the
team's to move, and [regulated-work.md](regulated-work.md) applies first. When the fixed parts are
separate deliverables with their own dates, [life-cycle.md](../project-management/life-cycle.md)
section 4 plans them as milestones.

## 4. How hybrids form, and where to start

Hybrids are rarely designed in one step; they grow. In HELENA's first stage, 47 of the 56
participants who combine approaches said their combination "Evolved from past projects over time",
and 11 said it was "Planned in a process improvement program"; a participant could give more than
one answer [2]. Kuhrmann et al. argue that "individual practices, rather than large methods, have
become the building blocks for process customization" [2]. Tell et al. raise a related point only
as a question for later work: what follows "if, regardless of the 'showroom method' providing the
umbrella, the practices are the stable key components of organizing and conducting the actual
project work?" [6]. The paper does not state it as a finding.

The rules below are this practice's own reading of these sources.

- **Start from one base approach whose owner's text you can name, and add only the practices your
  work needs.** The base is Scrum by the Scrum Guide, a Kanban flow by the Kanban Guide
  ([kanban.md](kanban.md)), or the plan-driven frame the organisation requires. A team adds XP's
  practices to the base that
  [life-cycle.md](../project-management/life-cycle.md) section 4 picks
  ([extreme-programming.md](extreme-programming.md) section 4). Why: a named base
  tells everyone which rules hold without a long list. The Scrum Guide calls Scrum "a container for
  other techniques, methodologies, and practices" [1], and Ladas starts from a base too: "for
  Scrumban, that starting point is Scrum" [9]. Which base each deliverable gets is
  [life-cycle.md](../project-management/life-cycle.md) section 4.
- **Add or change one practice at a time, for a problem the team has seen, and write the reason
  next to it.** Why: hybrids grow out of experience with past work [2], and a written reason lets
  the team see later whether the practice still earns its place. Ladas's own step has the same
  shape: "Change one practice in the direction of continuous delivery" [9]. For a Scrum team, the
  Sprint Retrospective is where the team identifies such a change
  ([meetings.md](../project-management/meetings.md) section 8).
- **Name the source text of each part, with its edition, where the plan records the approach**
  ([project-plan.md](../project-management/project-plan.md) section 2). Why: the source text tells a
  reader which rules hold, and the edition tells them which version of those rules.

A split of deliverables between predictive and adaptive work by
[life-cycle.md](../project-management/life-cycle.md) section 4 is a hybrid project, not a mix of
methods inside one team's way of working; the naming rule above applies to the second.

Changing or dropping a part of Scrum is tailoring Scrum, and what that costs is
[scrum.md](scrum.md). Who may change the team's way of working is
[choosing-an-approach.md](choosing-an-approach.md).

**A team that already runs a mix** does not start over. It names its base and the parts it added
the next time the plan changes, and gives each "Scrumban" in its docs one meaning when it next
edits that doc. This follows the default answer of [refactoring.md](../refactoring/refactoring.md)
section 7, new and touched code, applied here to process docs.

## 5. Common mistakes

| Mistake | Why it happens | What it costs | Fix |
|---|---|---|---|
| The process called Scrumban, with no meaning given | the word has two senses, and the sources disagree on it [7] | readers disagree on whether the Scrum events and accountabilities still hold | name the meaning, or write "Kanban inside Scrum" (section 2) |
| "Replaces most of Scrum" quoted as Ladas's words | a short news summary stands in for the essay | the words are Chris Sims's [10], so the quote puts words in Ladas's mouth | quote the essay [8] or the remarks [9] |
| A survey share used as proof that a mix works | a large share reads like a verdict | HELENA counted what participants use, in a convenience sample, in 2017 [4]; a share says nothing about results | name the sample, the unit and the year (section 1); for outcomes, [choosing-an-approach.md](choosing-an-approach.md) |
| The HELENA papers counted as several studies that agree | they have different first authors and venues | one 2017 dataset reads as independent agreement | count them as one source (section 1) |
| Klünder et al.'s 76.8% reported as a share of companies | the paper's abstract says "76.8% of the companies" [4] | the unit was a project or a product [4] | report it as a share of projects or products |
| Tell et al. cited as concluding that practices are "the stable key components" | the phrase reads like a result | it sits inside a question the paper asks [6] | cite its finding, "only eight methods and few practices build the core of modern software development" [6] |
| Scrum for the developers only, inside a plan-driven frame | teams adopt Scrum where they have influence [3] | West holds that "applying Scrum to only developers is a recipe for disaster" [3] | a Scrum team "must comprise all the people necessary to deliver working software" [3]; [scrum.md](scrum.md) |
| Parts of Scrum dropped, and the process still called Scrum | the team changed one thing at a time and kept the name | "the result is not Scrum" [1], and readers expect what Scrum includes | section 2; [scrum.md](scrum.md) |

## 6. Where the rules stop holding

- **One approach run as written.** A team with nothing around it on another cadence has no mix,
  and this file adds nothing for it. In HELENA, about 15% of the cases ran every discipline one
  way [5].
- **A frame fixed by a regulator or a contract.** West's advice to push back and to challenge
  reaches only as far as that frame lets the team move the lines
  ([regulated-work.md](regulated-work.md)).
- **Many teams on one product.** A mix shared across teams is [scaling.md](scaling.md).
- **After Ladas's path ends.** A team that has left Scrum follows the text of what it runs now, and
  the Scrum rules in this file stop holding for it.
- **What following the rules costs.** A line per part in the plan, and some care with one word. The
  research found no source that names a case where this costs more than it saves.

Not covered yet. The research for this file looked for these and found no source it could read:

- A study that compares one mix with another. How hybrid projects compare with agile and
  traditional ones as groups is in [choosing-an-approach.md](choosing-an-approach.md).
- Ladas's 2008 book beyond the essay Agile Alliance reprinted from it [8].
- The Forrester report behind West's column, which needs a login.
- The mistakes an agent makes when it describes or changes a team's mix.

## 7. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Ken Schwaber and Jeff Sutherland — The Scrum Guide, November 2020 — https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf — checked 2026-10-30
- [2] Marco Kuhrmann et al. — Hybrid Software and System Development in Practice: Waterfall, Scrum, and Beyond (ICSSP, 2017; research) — https://pure.itu.dk/en/publications/hybrid-software-and-system-development-in-practice-waterfall-scru/
- [3] Dave West — Analyst Watch: Water-Scrum-fall is the reality of agile (SD Times, 2011; column) — https://sdtimes.com/agile/analyst-watch-water-scrum-fall-is-the-reality-of-agile/
- [4] Jil Klünder et al. — Catching up with Method and Process Practice: An Industry-Informed Baseline for Researchers (ICSE-SEIP, 2019; research) — https://arxiv.org/abs/2101.12383v1
- [5] Marco Kuhrmann et al. — What Makes Agile Software Development Agile? (IEEE Transactions on Software Engineering, 2021; research) — https://arxiv.org/abs/2109.11435v1
- [6] Paolo Tell et al. — What are Hybrid Development Methods Made Of? An Evidence-based Characterization (ICSSP, 2019; research) — https://arxiv.org/abs/2101.08016v1
- [7] Ajay Reddy — The Scrumban [R]Evolution, the publisher's sample pages (Pearson Education, 2016; opinion) — https://ptgmedia.pearsoncmg.com/images/9780134086217/samplepages/9780134086217.pdf
- [8] Corey Ladas — What is Scrumban?, reprinted from his book Scrumban, 2008 (Agile Alliance, 2021; opinion) — https://agilealliance.org/scrumban/
- [9] Corey Ladas — Remarks on the Original Scrumban Essay (Agile Alliance, 2021; opinion) — https://agilealliance.org/remarks-on-the-original-scrumban-essay/
- [10] Chris Sims — Scrum-ban Paper Adds Kanban to Scrum (InfoQ, 2008; opinion) — https://www.infoq.com/news/2008/08/Scrum-kanban
- [11] Scrum.org, Daniel Vacanti and Yuval Yeret — The Kanban Guide for Scrum Teams, January 2021 — https://scrumorg-website-prod.s3.amazonaws.com/drupal/2021-01/01-2021%20Kanban%20Guide.pdf — checked 2026-10-30
