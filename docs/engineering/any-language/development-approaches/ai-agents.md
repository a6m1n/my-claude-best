# AI coding agents and the development approaches

This file is for a team that works in Scrum, Kanban, XP or SAFe and lets AI coding agents write
code, open pull requests or draft plans, and for an agent that works in such a team. It says what
the approaches' owners say about AI, what has been measured, and what a team keeps when agents take
part. How each approach works is in [scrum.md](scrum.md), [kanban.md](kanban.md),
[extreme-programming.md](extreme-programming.md) and [scaling.md](scaling.md); how a team picks
one is [life-cycle.md](../project-management/life-cycle.md) section 4.

**Navigation**

- [1. Purpose, the one rule, and when you do not need it](#1-purpose-the-one-rule-and-when-you-do-not-need-it)
- [2. What the approaches' owners say](#2-what-the-approaches-owners-say)
- [3. What has been measured](#3-what-has-been-measured)
- [4. What a team keeps when agents take part](#4-what-a-team-keeps-when-agents-take-part)
- [5. Common mistakes](#5-common-mistakes)
- [6. Where the rules stop holding](#6-where-the-rules-stop-holding)
- [7. Alternatives considered](#7-alternatives-considered)
- [8. Sources](#8-sources)

## 1. Purpose, the one rule, and when you do not need it

A team that adds agents can produce more code than before, while the approaches it runs were
written for people. Two things can then slip with nobody choosing it: who answers for a change an
agent made, and whether a person still reviews and tests that change before it ships. A team that
follows this file keeps both with people, keeps its batches small, watches its review step, and
reports what AI changed from its own numbers.

The one rule: **an agent may write, test and recommend; a person on the team decides, and answers
for every change the agent makes.**

Why it holds the rest together:

- Every owner text read for this file that speaks of accountability keeps it with people: the
  Scrum Guide [1], both AI texts of the Scrum Guide Expansion Pack [2], [3], and Scaled Agile's
  AI-Native SAFe [5] (section 2).
- The measurements disagree on speed, and three of them found a cost after the code is written:
  lower delivery stability [16], less human review [19], and more static-analysis warnings and
  code complexity [22] (section 3).

**When you do not need it.** If no agent writes code, opens pull requests or plans work in your
team, nothing here applies yet. If people use AI only as an assistant in their own editor, and
author and review every change themselves, the one rule is enough: the rules on batch size and
review in section 4 act on numbers that move when AI raises the count or the size of pull
requests, as both did in the one firm measured [19]. Until your own counts move, those rules have
nothing to act on, and the simpler way is the review and the Definition of Done the team already
has.

What this file leaves out, and where it lives:

- Where an agent runs, what it can read, change and send out, and which credentials it gets:
  [agent-containers.md](../docker/agent-containers.md), sections 3 to 5. This file adds no
  security rule of its own. Which personal data an agent may read during the work is not covered
  yet in this file: the approaches' owner texts read say nothing on it.
- Prompts, tool definitions and model settings:
  [prompt-engineering.md](../prompt-engineering/prompt-engineering.md).
- The size and form of a pull request: [git.md](../git/git.md) section 4. Small work items and the
  daily merge: [tickets.md](../project-management/tickets.md) sections 3 and 4. Continuous
  integration and delivery: [release.md](../project-management/release.md) section 5.
- Picking predictive, adaptive or hybrid, and Scrum or Kanban:
  [life-cycle.md](../project-management/life-cycle.md) section 4.

What the research for this file could not settle is listed in section 6.

## 2. What the approaches' owners say

The Scrum Guide and the Kanban Guide say nothing about AI. Companion texts, SAFe's owner, and
practitioners on the owners' sites have written about it.

### Scrum

- The Scrum Guide (November 2020) has no word on AI. It describes the team as people: "The
  fundamental unit of Scrum is a small team of people, a Scrum Team", and "Developers are the
  people in the Scrum Team that are committed to creating any aspect of a usable Increment each
  Sprint" [1].
- The Scrum Guide Expansion Pack is a companion text by Jeff Sutherland, one of the Guide's two
  authors [1], with Ralph Jocham and John Coleman; Ken Schwaber, the Guide's other author, is not
  among its authors [3]. It calls itself "a comprehensive companion to the 2020 Scrum Guide", and
  says that "it departs in some places" [3]. Two of its texts, both version 2026.1, speak about AI
  [2], [3]. AI and Scrum is published under CC BY-NC-ND 4.0 and the Expanded Guide under CC BY-SA
  4.0 [2], [3], so a team that copies text from them follows different licence terms for each.
- AI and Scrum, by Jocham and Sutherland: "AI may recommend, but humans decide" [2]. It says "AI
  is treated as a junior collaborator whose output is never accepted on trust", and "Every piece
  of AI-generated code must be reviewed with the same rigor as if a teammate wrote it" [2]. It
  keeps three decisions with people: "AI may assist, prepare, or recommend, but humans retain
  authority over prioritization, acceptance, and release decisions" [2]. It calls AI a tool and a
  junior collaborator, and never a team member [2].
- Scrum Guide Expanded, by Jocham, Coleman and Sutherland: "A Product Developer may be human or
  automated", and "At least one Product Developer should be human" [3]. "The Product Owner must
  be human", and "The Scrum Master must be human" [3]. It asks teams to "Maintain clear human
  accountability for all outcomes" [3].

So the two companion texts differ on whether an agent can hold a place in the team, and both keep
accountability with people. The rules in section 4 follow the 2020 Guide, which is the owner's
text; section 7 records the Expanded Guide's view.

### SAFe

Scaled Agile, SAFe's owner, released AI-Native SAFe in June 2026 and wrote: "This release does not
replace Core SAFe" [4]. Its keynote recap names what changes [5]:

- "Standardized Agile roles are replaced by flexible capabilities": Product, Builder and Domain
  Expert, working alongside AI [5].
- Experiments and Prototypes join Features and Enablers as work items [5].
- Teams set their own cadence around Align, Sense and Respond, and PI Planning becomes PI Outcome
  Planning [5].
- "People remain at the center, accountable for quality, cost, value, and customer impact" [5].

Both pages are the owner's announcements of its own product; this file uses them only for what
changed in the framework. How SAFe works is in [scaling.md](scaling.md).

### Kanban

The Kanban Guide (May 2025) and the Open Guide to Kanban (July 2025) contain no word on AI or
agents [6], [7], and neither does Kanban University's page on the principles and practices of the
Kanban Method [8]. Professional Kanban Trainers do write about AI on ProKanban.org [9], [10], and
their posts are their own views, not the Guide's. Liz Rettig holds that "AI made building fast. It
didn't make finding out you were wrong any faster" [9]. So, in her view, a big batch of up-front
requirements now gets a team "a large, polished, wrong thing" sooner [9]. In a second post she
holds that the constraint "didn't go away, it just relocated", to getting work ready and to
checking what comes back, and she asks teams to "Put WIP controls on every step where work waits"
[10].

### XP

Kent Beck, XP's author ([extreme-programming.md](extreme-programming.md)), writes about coding with
agents in his newsletter. His posts describe his own practice and small trials of his own; they
are not measurements.

- In a 2025 post, the system prompt he gave the agent says "Always follow the TDD cycle: Red →
  Green → Refactor" and "Use small, frequent commits rather than large, infrequent ones" [11]. He
  "watched the intermediate results of the genie more carefully, ready to intervene & stop
  unproductive development", and names the signs that the agent was going off track: loops,
  functionality he had not asked for, and "Any indication that the genie was cheating, for
  example by disabling or deleting tests" [11].
- In an April 2025 podcast he gave this advice: "Work in smaller steps and get more feedback"
  [12]. Asked how to pass that on to an agent, he answered: "Well, I don't know yet" [12]. The two
  answers belong together; the first is not advice he could yet give an agent.
- In a January 2026 post he ran a prompt trial on one sample project, a rope data structure, with
  four groups: a persona prompt ("Kent Beck"), explicit design constraints, both, and neither
  [13]. The persona prompt "reliably improved testing style and naming", but the design did not
  change; the constraint prompt "reliably forced the class hierarchy" [13]. In the same post he
  lists "smaller steps, larger steps" among the ways he had already tried to make the agent
  balance features and futures, and writes "I’ve been trying to encode my style" [13]. The post
  backs explicit constraints as the way to steer the design; it gives no result on step size.

### PMI and Agile Alliance

Agile Alliance's page for the Agile Practice Guide, second edition (2026), lists "AI-enabled
delivery" and "AI and GenAI" among the topics the edition updates [14]. The page names the topics
only, and the book itself was not read for this file.

## 3. What has been measured

These studies measure AI tools, not approaches. They matter here because they change what the
approaches manage: batch size, review load and stability. The research for this practice searched
arXiv for a study that compares Scrum, Kanban, XP or SAFe under AI, or that measures WIP, sprint
cadence or estimation accuracy in a live team with agents, and found none.

### Speed: no single figure holds

- METR, a randomised trial: Becker et al. found that 16 experienced open-source developers, on 246
  tasks in mature projects they already worked on, took 19% longer when AI tools of February to
  June 2025 were allowed, mainly Cursor Pro with Claude 3.5 and 3.7 Sonnet. Before the study the
  developers forecast 24% less time, and afterwards they estimated 20% less [20]. The result is
  for early-2025 tools [20].
- METR's 2026 update ran a new experiment and says its data "gives us an unreliable signal of the
  current productivity effect of AI tools", mainly because many developers declined to take part
  without AI [21]. METR believes "it is likely that developers are more sped up from AI tools now",
  and calls its data "only very weak evidence for the size of this increase" [21]. This file uses
  no figure from that experiment.
- One firm, observational: He et al. studied a mid-sized B2B software company whose CTO set a goal
  in June 2025 to double merged pull requests per engineer with AI; Cursor came first, and Claude
  Code then became the main tool [19]. Over 802 developers and 196,212 pull requests, January 2024
  to April 2026, raw pull requests per active developer rose 2.09 times, and the authors' main
  estimate of the AI effect, from a staggered difference-in-differences design without random
  assignment, is 1.46 times [19]. They say their results are "better interpreted as an upper bound
  than as a representative industry average", and that throughput "is only a proxy for
  productivity" [19].
- Open-source repositories, observational: He et al. compared 806 GitHub repositories that adopted
  Cursor with 1,380 matched repositories. Velocity rose sharply in the first month, "but gains
  dissipate after two months" [22].
- A meta-analysis: Maier et al. pooled 16 productivity effect sizes from 14 studies published from
  2019 to 2025, and found a moderate effect (Hedges' g = 0.33, 95% CI 0.09 to 0.58) with very high
  heterogeneity (I² = 99%) [23]. Laboratory experiments showed g = 0.73, while the effects in
  enterprise (g = 0.19) and open-source settings (g = 0.01) "do not differ significantly from zero"
  [23]. The authors conclude that "GenAI tools should not be treated as a one-size-fits-all
  productivity solution" [23].

These studies measure different things (task time, pull requests, repository activity) in
different populations, and they disagree. So the rules in section 4 rest on no speed-up figure.

### Stability and quality

- DORA, a program run by Google Cloud [15], surveyed nearly 5,000 technology professionals and
  collected over 100 hours of qualitative data for its 2025 report [16]. It calls AI's primary
  role "an amplifier, magnifying an organization’s existing strengths and weaknesses" [15]. It
  found "a
  positive relationship between AI adoption on both software delivery throughput and product
  performance", and that "AI adoption does continue to have a negative relationship with software
  delivery stability" [16].
- The measures behind those findings are the respondents' own answers about their primary
  application or service, such as their lead time for changes and the share of their changes that
  needed remediation [17]. They are self-reported answers from one survey year, so they show a
  relationship, not a cause. DORA's throughput finding opens with "Unlike last year" [16]: the 2024
  report did not find that positive relationship, so the two years' figures are never combined.
- DORA's explanation of the stability result: "Without robust control systems, like strong
  automated testing, mature version control practices, and fast feedback loops, an increase in
  change volume leads to instability" [16].
- In the open-source study, static-analysis warnings rose by 30.26% and code complexity by 41.64%
  after adoption, and stayed up (its Table 2) [22].

### Pull-request size depends on the agent

- Popescu et al. studied 111,969 pull requests on GitHub from five agents and from humans, June to
  August 2025. "The median human-opened PR was approximately 60 lines"; Claude Code's median was
  376 lines, "with the exception of Codex, which was used in smaller changes" [24]. The authors
  add that "the actual effect size can be moderate to fairly negligible" (Cliff's delta about 0.37
  for Claude Code against humans, about −0.03 for humans against Codex) [24].
- Pham and Ghaleb compared 31,268 closed agent pull requests with 6,135 closed human ones, from a
  dataset in which Codex made 21,799 of 33,596 agent pull requests: "The number of changed lines
  does not differ significantly (p = 0.131)", and agent pull requests had fewer commits, files
  and directories [25].
- In the one firm, the median pull request grew from 35 lines in the baseline months to 61 lines
  in April 2026 [19].

So whether agents raise batch size depends on the agent and the setting; no general claim holds.

### Review

- In the one firm, "The share of PRs receiving at least one human review fell from 89% to 68%",
  while automated AI review rose from about 19% to about 84% of pull requests, and the load per
  reviewer doubled [19].
- Agarwal et al. built a theory of code review under AI from 3,100 coded documents, sampled from
  38,709 engineering blog posts and Reddit threads, and call it "a proposed explanatory theory, not
  a validated one" [26]. Their first look at public GitHub activity found agent pull requests
  reviewed less often and merged faster, "yet the direction of these trends flips under different
  but equally defensible analysis choices" [26].

So the claim that review capacity becomes the constraint is a hypothesis. One firm measured less
human review and more load per reviewer [19]; the theory that review becomes the bottleneck has not
been tested [26].

### Planning

Caraeni et al. ran one sprint-planning condition in each of three experience-matched Scrum teams
(a Product Owner, a Scrum Master and four developers each) at a digital agency of 35 to 50 people.
Each team built the same 47-story-point deliverable over three two-week sprints. The plan made by
AI alone (Claude Sonnet 4.6) captured 36.4% of the risks, against 78.6% for the plan made by
people and 86.7% for the plan made by both [27]. The authors write that, "with N = 3 sprints per
condition", their tests "should be interpreted as preliminary evidence" [27]. By this file's own
reading of their table, the three rates are shares of different numbers of risks (about 11, 14
and 15), which makes the comparison less clean. The AI planned; it wrote no code [27].

## 4. What a team keeps when agents take part

The rules every team with agents applies, in the order the work happens:

- **Name the person who answers for the result of each work item an agent takes, and write that
  person on the work item before the agent starts: as its assignee, or in a comment on the work
  item when the agent's account is the assignee or another person answers.** That person reviews
  the agent's change as their own before it merges. Why: every owner text that speaks of
  accountability keeps it with people [1], [2], [3], [5], and AI and Scrum warns that "The attitude
  “the AI suggested it, so we implemented it” can lead to diffused responsibility" [2].
  Check: before the agent starts, the work item names a person who answers for it.
- **Count only people as the Scrum Team: the Developers, the Product Owner and the Scrum Master.**
  An agent is a tool the Developers use. Why: the 2020 Guide calls the Developers "the people in
  the Scrum Team" [1], so the team's size, its commitments and its accountabilities stay with
  people who can answer for them. Even the Expanded Guide, which allows an automated Product
  Developer, says the Product Owner and the Scrum Master "must be human" [3].
- **Keep the decisions on what to build, what counts as done and what ships with people; an agent
  may draft and recommend them.** Why: AI and Scrum keeps "authority over prioritization,
  acceptance, and release decisions" with humans [2].
- **Keep each agent pull request to one work item, within the limits that [git.md](../git/git.md)
  section 4 and [tickets.md](../project-management/tickets.md) sections 3 and 4 set, and split a
  larger one before review.** Why: DORA calls working in small batches "a critical countermeasure"
  to the delivery instability that AI adoption often brings [18], and pull-request size depends on
  the agent [24], [25], so the team's limit has to set it, not the tool's habit. Beck's own prompt
  asks for "small, frequent commits" [11].
  Check: before review, read the agent pull request's diff summary. It covers one work item, at a
  size the team would accept from a person.
- **Give every agent change a review by a person; an AI reviewer adds its findings to that review
  and never replaces it.** Why: AI and Scrum asks that AI-generated code "be reviewed with the same
  rigor as if a teammate wrote it" [2]. In the one firm measured, "Automated review thus replaced
  part of human review rather than only adding to it" [19], and the authors' checks "cannot rule
  out quality costs" [19]. Who lands a pull request is [git.md](../git/git.md) section 5: "a human
  lands the pull request, and an agent never merges its own"; where two or more people review,
  the required approvals of [ruleset-example.md](../git/ruleset-example.md) § "What to change for
  your repository" make the repository ask for that approval on every pull request.
  Check: before merge, the pull request shows an approval by a person.
- **Run every agent change through the same tests, CI and Definition of Done as a person's
  change, and change none of them for agent work.** The pipeline is
  [release.md](../project-management/release.md) section 5, the pull request's Verification is
  [git.md](../git/git.md) section 4, and the Definition of Done is
  [tickets.md](../project-management/tickets.md) section 2. Why: AI and Scrum asks for
  "strengthening—not relaxing—the Definition of Output Done" [2], and DORA ties AI's instability
  to teams without "strong automated testing, mature version control practices, and fast feedback
  loops" [16].
- **When an agent's change disables or deletes a test, ask why before you review anything else.**
  Why: Beck names "disabling or deleting tests" as a sign that the agent was cheating, next to
  loops and functionality nobody asked for [11].
- **Show review as its own step on the board, with a limit of its own that the team writes on the
  board or in its Definition of Workflow ([kanban.md](kanban.md) section 3, element 4), inside the
  team's WIP limit ([principles.md](../project-management/principles.md) section 3). Count the
  pull requests that wait for review at the board look the team already holds (the weekly board
  look of [principles.md](../project-management/principles.md) section 3, or the daily board review of
  [meetings.md](../project-management/meetings.md) section 9), not only at retrospectives, and at
  each retrospective ([meetings.md](../project-management/meetings.md) section 8) look at two
  numbers: how many pull requests wait for review, and how many merged without a review by a
  person.** A team without sprints looks at them at its regular retrospective
  ([meetings.md](../project-management/meetings.md) section 9). Name each pull request merged
  without a person's review at that retrospective, with its cause and its fix. Why: in one firm the
  share of pull requests with a human review fell from 89% to 68% while the load per reviewer
  doubled [19], and the theory that review becomes the constraint is untested [26]. The team
  treats it as a hypothesis and lets its own numbers show whether it holds.
- **When you report what AI changed for the team, report the team's own measures before and
  after, with the period they cover, and quote no published speed-up figure.** Why: the published
  figures disagree in sign and size (section 3) [20], [21], [23].

Where the agent runs and what it can reach is set up by
[agent-containers.md](../docker/agent-containers.md) before the agent works without approvals. A
team that already runs agents applies these rules to the work items it starts after it adopts
them: the answer "New and touched code" in
[refactoring.md](../refactoring/refactoring.md) section 7.

The rules that hold only under a condition:

- **When an AI drafts the sprint plan or the backlog, the team does its own pass over the risks
  in Sprint Planning ([meetings.md](../project-management/meetings.md) section 4), or, in a team
  without sprints, at the refinement when the Backlog runs low
  ([meetings.md](../project-management/meetings.md) section 9), before it commits to the plan.**
  Why: "AI may recommend, but humans decide" [2], and in the one study of
  it, preliminary and with three teams, the plan made by AI alone captured 36.4% of the risks
  against 78.6% and 86.7% for the other two [27].
- **When the count of pull requests waiting for review grows from one look to the next, start new
  agent work only while the review step is under the limit the team writes for it on the board or
  in its Definition of Workflow ([kanban.md](kanban.md) section 3, element 4), and keep the review
  by a person.** Why: the Kanban
  Guide asks members to "start work on an item (pull or select) only when there is a clear signal
  that there is capacity to do so" [6]. Rettig holds the same for AI-boosted delivery: "Put WIP
  controls on every step where work waits" [10].
- **When the team follows the Scrum Guide Expanded rather than the 2020 Guide, keep at least one
  human Product Developer, a human Product Owner and a human Scrum Master, as that text asks [3].**
  This condition replaces the rule above that counts only people as the Scrum Team; every other
  rule above still holds, because that text also keeps "clear human accountability for all
  outcomes" [3].
- **When the team runs SAFe, apply the rules above in Core SAFe and in AI-Native SAFe alike.**
  Why: AI-Native SAFe changes roles into capabilities and PI Planning into PI Outcome Planning,
  and still keeps people "accountable for quality, cost, value, and customer impact" [5]. Which
  operating model fits is [scaling.md](scaling.md)'s question.

## 5. Common mistakes

| Mistake | What it costs | Fix |
|---|---|---|
| One study's speed-up quoted as what AI does for every team | the studies disagree in sign and size, and the pooled effect has I² = 99% [23] | the team's own before-and-after measures, section 4 |
| METR's 19% read as a fact about today's tools, or its 2026 figures reused | it is for early-2025 tools [20]; METR calls its newer data "an unreliable signal" [21] | name the tools' date; use no figure from the 2026 experiment |
| Agent pull requests read as six times larger than human ones | 376 against 60 lines is Claude Code's median; Codex made smaller changes [24], and a second study found no difference in lines [25] | section 3; the team's own size limit, section 4 |
| DORA's finding read as a cause, or its 2024 and 2025 figures mixed | the measures are self-reported answers from one survey year [17], and the 2024 report did not find the 2025 throughput relationship [16] | section 3 |
| Agent pull requests merged with no review by a person, or with an AI review only | the owner text asks a teammate's rigor [2]; in one firm the human-review share fell from 89% to 68% [19] | section 4 |
| An agent treated as accountable, as in "the AI suggested it, so we implemented it" | "diffused responsibility" [2] | name the person before the agent starts, section 4 |
| An agent counted as a Scrum Team member under the 2020 Guide | the Guide's team is people [1] | section 4 |
| Tests skipped, or the Definition of Done loosened, for agent work | AI and Scrum asks to strengthen it, not relax it [2]; Beck watched for disabled or deleted tests as a sign the agent was cheating [11] | section 4 |
| A sprint plan made by AI alone, committed with no risk pass by people | fewer risks captured in the one preliminary study [27] | section 4, the rules under a condition |
| That review is the constraint, stated as a measured fact | it is a proposed, unvalidated theory [26] | watch the team's own review numbers, section 4 |

## 6. Where the rules stop holding

When a rule does not fit, and what following it costs:

- **Assistants only.** A team whose people use AI in their own editor and author every change
  themselves keeps the one rule; the rules on batch size and review have nothing to act on until
  the team's own counts move (section 1).
- **The Scrum Guide Expanded.** A team that adopts it may count an automated Product Developer;
  the condition in section 4 says what it keeps.
- **What a review by a person costs.** It limits the merge rate to what the reviewers can read. The
  firm in [19] kept pace mainly by moving review onto automation. A team that follows section 4
  accepts a slower merge rate when its review queue grows, and answers the queue by starting less
  work, not by dropping the review. That trade is this file's own reading of [19] and [2].
- **The evidence behind the rules.** The measurements come from one firm, from open-source
  repositories, from laboratory experiments and from one preliminary three-team study (section 3).
  None measured a team that runs Scrum or Kanban with agents over months. The rules therefore rest
  on the owner texts first, and the measurements say what to watch.

Not covered yet. The research for this file looked for these and found no source it could read:

- A study that compares Scrum, Kanban, XP or SAFe under AI, or that measures WIP, sprint cadence or
  estimation accuracy in a live team with agents.
- Scrum.org's or Ken Schwaber's position on AI in Scrum and on the Expansion Pack.
- What the Agile Practice Guide's second edition says about AI: only its publisher's page was read
  [14].
- The method details of DORA's 2025 report: the number of answers each model used, the response
  rate and the effect sizes. The full report was not read, only DORA's pages about it [15], [16],
  [17].
- Whether XP's own book texts change under AI: Beck's posts describe his practice and do not
  revise XP [11], [13].
- Defects and incidents that agent changes cause in a team's delivery: the firm study did not
  measure them [19].

## 7. Alternatives considered

- **Count an agent as a Product Developer, as the Scrum Guide Expanded allows [3].** Not taken: the
  rule follows the 2020 Guide, the owner's text [1]. The Expansion Pack calls itself a companion
  that "departs in some places" [3], and AI and Scrum states the difference itself: "The SGEP view
  is that Scrum is mutable (the 2020 Scrum Guide considers it immutable)" [2]. A team that adopts
  the Expanded Guide follows the condition in section 4.
- **Let an AI review replace part of the human review, as the firm in [19] did.** Not taken: the
  owner texts ask for a teammate's rigor and a human decision [2], and the one measurement of that
  change reports less human review without showing that quality held [19].
- **Plan capacity from a published speed-up figure.** Not taken: no single figure holds (section 3).
- **A step-size rule for agents.** Not taken: Beck lists smaller and larger steps among the things
  he had tried [13], and said he did not yet know how to teach small steps to an agent [12]. This
  file takes batch size from DORA [18] and from the limits the team already has (section 4).

## 8. Sources

Checked 2026-10-30 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Ken Schwaber and Jeff Sutherland — The Scrum Guide, November 2020 — https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf
- [2] Ralph Jocham and Jeff Sutherland — AI and Scrum, version 2026.1 (Scrum Guide Expansion Pack, 2026; opinion) — https://raw.githubusercontent.com/ScrumGuides/ScrumGuide-ExpansionPack/88eb64c2458da5021cb3c160ff4cc38dbb93e1ed/site/content/ai-and-scrum/2026.1/index.md
- [3] Ralph Jocham, John Coleman and Jeff Sutherland — Scrum Guide Expanded, version 2026.1 (Scrum Guide Expansion Pack, 2026; opinion) — https://raw.githubusercontent.com/ScrumGuides/ScrumGuide-ExpansionPack/88eb64c2458da5021cb3c160ff4cc38dbb93e1ed/site/content/scrum-guide-expanded/2026.1/index.md
- [4] Andrew Sales — New Release: AI-Native SAFe is the Operating Model for the AI-Native Organization (Scaled Agile Framework blog, 2026; opinion) — https://framework.scaledagile.com/blog/ai-native-safe-is-the-operating-model-for-the-ai-native-organization
- [5] Andrew Sales — SAFe Summit Keynote Recap: Launching The Operating Model for the Age of AI (Scaled Agile Framework blog, 2026; opinion) — https://framework.scaledagile.com/blog/safe-summit-keynote-recap-launching-the-operating-model-for-the-age-of-ai
- [6] Orderly Disruption Limited and Daniel S. Vacanti, Inc. — The Kanban Guide, May 2025 (v2025.5) — https://kanbanguides.org/the-kanban-guide/2025.5/
- [7] Kanban Guides — Open Guide to Kanban, July 2025 (v2025.7) — https://kanbanguides.org/open-guide-to-kanban/2025.7/
- [8] Kanban University — Principles and General Practices of the Kanban Method (Kanban University, 2014; opinion) — https://kanban.university/principles-general-practices-kanban-method/
- [9] Liz Rettig — AI doesn't bring waterfall back. It lets you be wrong faster. (ProKanban.org blog, 2026; opinion, by a trainer of an organisation that sells Kanban training) — https://prokanban.org/blog/ai-doesn-t-bring-waterfall-back-it-lets-you-be-wrong-faster
- [10] Liz Rettig — AI boosted your throughput. Your strategy didn't move. (ProKanban.org blog, 2026; opinion, by a trainer of an organisation that sells Kanban training) — https://prokanban.org/blog/ai-boosted-your-throughput-your-strategy-didn-t-move
- [11] Kent Beck — Augmented Coding: Beyond the Vibes (Software Design: Tidy First?, 2025; opinion) — https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes
- [12] Jessica Kerr, Ken Rimple and Kent Beck — Ep. #80, Augmented Coding with Kent Beck (O11ycast, Heavybit, 2025; interview) — https://www.heavybit.com/library/podcasts/o11ycast/ep-80-augmented-coding-with-kent-beck
- [13] Kent Beck — Taming the Genie: "Like Kent Beck" (Software Design: Tidy First?, 2026; opinion) — https://newsletter.kentbeck.com/p/taming-the-genie-like-kent-beck
- [14] Agile Alliance — Agile Practice Guide, Second Edition (publication page) — https://agilealliance.org/agile-practice-guide-2nd-edition/
- [15] DORA — State of AI-assisted Software Development 2025, report page (dora.dev, 2025; research, sponsored by Google) — https://dora.dev/dora-report-2025/
- [16] Nathen Harvey and Derek DeBellis — Announcing the 2025 DORA Report: State of AI-Assisted Software Development (Google Cloud blog, 2025; research, sponsored by Google) — https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report
- [17] DORA — Survey questions of the 2025 State of AI-assisted Software Development report (dora.dev, 2025; research, sponsored by Google) — https://dora.dev/research/2025/questions/
- [18] DORA — Capabilities: Working in small batches (dora.dev, 2025; opinion, by a program run by Google Cloud) — https://dora.dev/capabilities/working-in-small-batches/
- [19] Hao He et al. — AI Writes Faster Than Humans Can Review: A Longitudinal Study of an Enterprise "2×" Mandate (arXiv 2607.01904v2, 2026; research, preprint) — https://arxiv.org/abs/2607.01904v2
- [20] Joel Becker, Nate Rush, Elizabeth Barnes and David Rein — Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity (arXiv 2507.09089v2, 2025; research, preprint) — https://arxiv.org/abs/2507.09089v2
- [21] METR — We are Changing our Developer Productivity Experiment Design (METR blog, 2026; research) — https://metr.org/blog/2026-02-24-uplift-update/
- [22] Hao He et al. — Speed at the Cost of Quality: How Cursor AI Increases Short-Term Velocity and Long-Term Complexity in Open-Source Projects (arXiv 2511.04427v3, 2026, MSR '26 per its arXiv record; research, preprint) — https://arxiv.org/abs/2511.04427v3
- [23] Sebastian Maier et al. — A meta-analysis of the effect of generative AI on productivity and learning in programming (arXiv 2605.04779v1, 2026; research, preprint) — https://arxiv.org/abs/2605.04779v1
- [24] Razvan Mihai Popescu et al. — Investigating Autonomous Agent Contributions in the Wild: Activity Patterns and Code Change over Time (arXiv 2604.00917v1, 2026, MSR 2026 per its arXiv record; research, preprint) — https://arxiv.org/abs/2604.00917v1
- [25] Dung Pham and Taher A. Ghaleb — Code Change Characteristics and Description Alignment: A Comparative Study of Agentic versus Human Pull Requests (arXiv 2601.17627v1, 2026, accepted at MSR '26 per its arXiv record; research, preprint) — https://arxiv.org/abs/2601.17627v1
- [26] Shyam Agarwal et al. — 3100 Opinions on Code Review in an AI World: Building Causal Theory from Practitioner Discourse (arXiv 2607.07980v1, 2026; research, preprint) — https://arxiv.org/abs/2607.07980v1
- [27] Adriana Caraeni, Alexander Shick and Andrew Lan — Cognitive Offloading in Agile Teams: How Artificial Intelligence Reshapes Risk Assessment and Planning Quality (arXiv 2604.13814v1, 2026; research, preprint) — https://arxiv.org/abs/2604.13814v1
