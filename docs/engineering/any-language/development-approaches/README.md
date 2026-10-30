# Development approaches

How a software team organises its work: the agile values and principles, Scrum, Kanban, Extreme
Programming (XP) and Lean software development, how teams combine them, the models and the
evidence behind choosing one, and how the approaches work past one team, in regulated or
fixed-scope work and with AI coding agents. The files describe approaches, not the tools a team
runs them in: for each approach they say what problem it solves, how a team starts, and when it
fits or is too much. The rule that picks a predictive, adaptive or hybrid approach for each
deliverable, and Scrum or a Kanban flow for its adaptive part, is
[life-cycle.md](../project-management/life-cycle.md) section 4; this practice backs that rule and
never restates it.

**Navigation**

- [When you do not need all of it](#when-you-do-not-need-all-of-it)
- [The one rule](#the-one-rule)
- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [Security and privacy](#security-and-privacy)
- [The points to adapt](#the-points-to-adapt)
- [Sources](#sources)

## When you do not need all of it

This folder is a set of files to look things up in, one per approach or question, not a method to
install. Read the file your work needs and stop there.

- A team that runs one approach well, as its owner's text describes it, with no plan or release
  around it on another cadence, reads that approach's file and no other
  ([combining-approaches.md](combining-approaches.md), "When you do not need this file"). The
  Scrum Guide's own advice points the same way: "Try it as is and determine if its philosophy,
  theory, and structure help to achieve goals and create value" [1].
- A team with no choice to make yet needs none of it. The folder is for the moment someone
  proposes to pick, start, combine or change how a team works, or to add a second team, a
  regulator's frame or AI agents.
- Inside a file, take the part the work needs. A product one team builds needs nothing from
  [scaling.md](scaling.md), because the Scrum Guide's team is "typically 10 or fewer people" [1].
  [regulated-work.md](regulated-work.md) adds nothing when no regulator, safety standard or
  fixed-scope contract governs the work, and [ai-agents.md](ai-agents.md) has nothing to act on
  until an agent writes code, opens pull requests or plans work in the team. A team that wants one
  fix from XP takes one practice: Kent Beck offers XP's practices as ones "you can add to your bag
  of tricks" [2] ([extreme-programming.md](extreme-programming.md) section 3). Each file has its
  own "when you do not need it" part near its top.

What not to adopt from it: the folder, or any approach in it, as a method to roll out over a team.
Martin Fowler holds that "you should never try to impose agile working on a team that doesn't want
to try it" [3], and [agile-values.md](agile-values.md) section 5 names imposing the process as a
common mistake. Nor is Scrum the default for every team because most teams use it: a usage share
measures use, not results ([choosing-an-approach.md](choosing-an-approach.md) section 3). And the
approaches are not a sequence to work through: a team starts from one base and adds only the
practices its work needs ([combining-approaches.md](combining-approaches.md) section 4).

## The one rule

**Fit the approach to the work, not to a name. Name the text each part of the team's process comes
from, keep whole what that text calls its minimum, and let the team that does the work choose and
tune how it works inside the approach its project picked. No model, survey or study shows one
approach best for every team, so none is imposed as the default.**

Why it holds the files together:

- **The work decides, not a name.** Fowler holds that "there is no one-size-fits-all in software
  development" [4]. Each file says when its approach fits and when it is too much, and adds
  structure only for a problem the team has: one XP practice for the problem the team feels most
  ([extreme-programming.md](extreme-programming.md) section 3), a second team only when one team
  cannot hold the product ([scaling.md](scaling.md) section 1), a fixed frame only where a
  regulator, a standard or a contract fixes it ([regulated-work.md](regulated-work.md)).
- **A named text, with its minimum kept whole.** Of Scrum the Guide says: "While implementing only
  parts of Scrum is possible, the result is not Scrum" [1]; the rule is
  [scrum.md](scrum.md) section 4. A named text lets anyone check the work against it:
  [kanban.md](kanban.md) section 1 asks each Kanban policy to name its text and edition, and
  [combining-approaches.md](combining-approaches.md) section 1 asks the same of each part of a mix.
  XP's practices, by contrast, are tools the team picks one at a time
  ([extreme-programming.md](extreme-programming.md) section 1). Under every method, the four values
  and twelve principles are the test of the work ([agile-values.md](agile-values.md) section 1).
- **The team decides how it works.** Fowler: "the team doing work decides how to do it. That is a
  fundamental agile principle" [4]. The project weighs an approach for each deliverable, and the
  team chooses how it works inside the adaptive part; [choosing-an-approach.md](choosing-an-approach.md)
  section 3 keeps the two layers apart. With AI agents in the work, a person still decides and
  answers for every change an agent makes ([ai-agents.md](ai-agents.md) section 1).
- **No approach is proven best.** The outcome studies read for this practice compare past projects,
  not trials, and none of them settles the pick
  ([choosing-an-approach.md](choosing-an-approach.md) section 5). No study read shows one scaling
  framework, or none, ahead of another ([scaling.md](scaling.md) section 4), and the published
  figures for what AI does to a team's speed disagree in sign and size
  ([ai-agents.md](ai-agents.md) section 3). The pick rests on the criteria of
  [life-cycle.md](../project-management/life-cycle.md) section 4, never on a success rate or a
  usage share.

## What is here

Each file says near its top what it holds and what it leaves to other files. Each states the rule
that holds it together, except [lean-software-development.md](lean-software-development.md), which
works by the one rule above. A team that has not picked an approach yet starts with
[choosing-an-approach.md](choosing-an-approach.md) and
[life-cycle.md](../project-management/life-cycle.md) section 4.

Where a question could send you to two places, one file owns each rule, and the others link it;
the rows on what the team's events check have one row per event, and each lists the files whose
check falls at that event:

| The question | The file that owns it |
|---|---|
| Which approach each deliverable gets, and Scrum or a Kanban flow | [life-cycle.md](../project-management/life-cycle.md) section 4 |
| Who chooses, at the project layer and at the team layer | [choosing-an-approach.md](choosing-an-approach.md) section 3 |
| Whether a survey or a study shows that one approach works better | [choosing-an-approach.md](choosing-an-approach.md) sections 4 and 5 |
| What dropping or changing a part of Scrum costs | [scrum.md](scrum.md) section 4 |
| Which of the two Kanban texts a rule follows | [kanban.md](kanban.md) section 1 |
| Kanban practices in a Scrum team that keeps Scrum whole | [kanban.md](kanban.md) section 5 |
| What "Scrumban" means here, and Water-Scrum-Fall | [combining-approaches.md](combining-approaches.md) sections 2 and 3 |
| XP's practices in a Scrum team, and the evidence on pair programming and test-driven development | [extreme-programming.md](extreme-programming.md) sections 4 and 5; test-first work in Python: [what-to-test.md](../../python/testing/what-to-test.md) section 4 |
| The Scrum Guide Expansion Pack | [scrum.md](scrum.md) section 8; for AI agents, [ai-agents.md](ai-agents.md) section 4 |
| Fixed-price and fixed-scope contracts | [regulated-work.md](regulated-work.md) section 3 |
| Copying the Spotify model | [scaling.md](scaling.md) section 5 |
| The sprint events, their timeboxes, and a team without sprints | [meetings.md](../project-management/meetings.md) sections 2 to 9 |
| The Definition of Done and the story form | [tickets.md](../project-management/tickets.md) section 2 |
| How the two Kanban texts name and define the flow measures | [kanban.md](kanban.md) section 4; the WIP limits and the weekly board look: [principles.md](../project-management/principles.md) section 3 |
| The WIP limit per person and for the team, and the measures at the weekly board look | [principles.md](../project-management/principles.md) section 3 |
| What a Sprint Planning checks for the team's approach | [kanban.md](kanban.md) section 5, [ai-agents.md](ai-agents.md) section 4 |
| What a Sprint Review checks for the team's approach | [kanban.md](kanban.md) section 5, [regulated-work.md](regulated-work.md) section 2 |
| What a retrospective checks for the team's approach | [scrum.md](scrum.md) section 4, [kanban.md](kanban.md) section 5, [extreme-programming.md](extreme-programming.md) section 4, [ai-agents.md](ai-agents.md) section 4, [choosing-an-approach.md](choosing-an-approach.md) section 3; in a Kanban flow: [regulated-work.md](regulated-work.md) section 2 |

The files:

- [agile-values.md](agile-values.md): the Manifesto's four values and twelve principles, what they
  are and are not, when they fit, agility rather than a brand, how a team starts from them, and
  what a team does when its organisation runs a method it did not choose. Read it when a team wants
  to work in an agile way, when someone offers to make a team "agile", or when a team asks whether
  its named method still follows the values.
- [choosing-an-approach.md](choosing-an-approach.md): the models a group can use to weigh an
  approach (Boehm's home grounds, the Agile Practice Guide's suitability filters, Cynefin, Agile
  Fluency), who chooses at the project layer and at the team layer, whether Scrum is the default,
  and what research measured about choosing and about outcomes. Read it when a deliverable could
  fit more than one approach, when the team and the organisation disagree on who decides, when
  someone proposes one method for every team, or when someone says a survey or a study proves one
  approach best.
- [scrum.md](scrum.md): Scrum by the 2020 Scrum Guide, when it fits and when it is too much, how a
  team starts, keeping it whole and what tailoring costs, what to do when the team's situation
  changes, Dark, Zombie and Flaccid Scrum, what effective Scrum teams have in common, and the
  Expansion Pack. Read it when a team starts Scrum, before you change how a team runs it, and when
  someone proposes to drop an event, a role or an artifact.
- [kanban.md](kanban.md): the two texts that define Kanban, the Kanban Guide and the Kanban Method,
  and which one each rule follows; when it fits; how a team starts, with a Definition of Workflow
  or with STATIK; the four flow measures; and Kanban inside Scrum. Read it when you set up or
  change a Kanban board or a Definition of Workflow, report a flow measure, or add Kanban practices
  to a Scrum team.
- [extreme-programming.md](extreme-programming.md): what XP is, when it fits and when it is too
  much, how a team starts from the problem it feels most, XP with Scrum, and what research says on
  pair programming and test-driven development. Read it when a team wants to try XP or one of its
  practices, when a Scrum team asks how to build the work, or when someone cites a study on pair
  programming or test-driven development.
- [lean-software-development.md](lean-software-development.md): the Poppendiecks' principles in
  their three published lists, when they fit, how a team starts by following one request from the
  ask to the delivery and measuring its flow efficiency, and the common mistakes. Read it when
  requests wait longer for approvals, handovers or releases than for developers, or when someone
  adds a practice "because it is Lean".
- [combining-approaches.md](combining-approaches.md): why teams combine approaches, the two
  meanings of "Scrumban" and the one this practice uses, Water-Scrum-Fall, and where a hybrid
  starts. Read it when the team's process mixes parts from different texts, when someone calls it
  "Scrumban" or "hybrid", or when the plan and the releases around a Scrum team follow their own
  rules.
- [scaling.md](scaling.md): when a second team is needed, what the teams of one product share,
  LeSS and SAFe by their owners' texts, what research has measured about scaling frameworks, and
  the common mistakes, the Spotify model among them. Read it when one team can no longer hold a
  product, or when someone asks whether to adopt LeSS or SAFe.
- [regulated-work.md](regulated-work.md): what the regulator and standard texts read ask of a
  development approach, an agile loop inside the plan-driven frame that safety evidence and
  approvals need, and fixed-price and fixed-scope contracts. Read it before you plan the life cycle
  of software under a regulator or a safety standard, and before you agree to a contract that fixes
  the price, the date or the scope.
- [ai-agents.md](ai-agents.md): what the approaches' owners say about AI, what has been measured,
  and what a team keeps when AI coding agents write code, open pull requests or draft plans. Read
  it before agents take part in the team's work, and when someone quotes a figure for how much AI
  speeds a team up.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/any-language/development-approaches/`,
   so the path in step 2 and the links to other practices in step 3 still work.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you choose or change how a team works —
   pick its development approach, start, combine or change Scrum, Kanban, XP or Lean practices,
   scale past one team, run the work under a regulator or a fixed-price contract, or bring AI
   coding agents into the team's work — read
   `docs/engineering/any-language/development-approaches/README.md` and the file it routes to for
   that work, and `docs/engineering/any-language/project-management/life-cycle.md` section 4 when
   the choice is made for a project's deliverables. The check: the plan or the team's page names the
   approach and its reason (`life-cycle.md` section 4), no Scrum event, role or artifact is dropped
   while the team still calls its process Scrum (`scrum.md` section 4), every Definition of Workflow
   it writes names the Kanban text and edition it follows (`kanban.md` section 1), and no claim that
   one approach works better than another, or that AI agents speed a team up by one figure, appears
   without its study, the study's sample and its kind (`choosing-an-approach.md` section 5,
   `ai-agents.md` section 3)." Without it an agent never opens the folder.
3. The files link other practices for the rules those own:
   [project-management](../project-management/README.md) most of all, for the pick of an approach,
   the meetings, work items, the Definition of Done, WIP, releases, the plan and who decides;
   [git.md](../git/git.md) for the size of a pull request;
   [refactoring.md](../refactoring/refactoring.md) for how a running team takes up a rule;
   [agent-containers.md](../docker/agent-containers.md) for where an AI agent runs;
   [ci-cd](../ci-cd/README.md) for the pipelines;
   [prompt-engineering.md](../prompt-engineering/prompt-engineering.md) for prompts and model
   settings; and [what-to-test.md](../../python/testing/what-to-test.md) for test-first work in
   Python. Run
   `grep -rhoE '\]\(\.\./[^)#]+' docs/engineering/any-language/development-approaches/ | sort -u`
   to print every link that leaves this folder. Copy each folder or file it names, or replace each
   link with your own rule for that topic, so no link points at a file your repository does not
   have.
4. A team or a project that already runs an approach does not stop to rebuild it. The answer is
   new and touched code ([refactoring.md](../refactoring/refactoring.md) section 7), applied to a
   process: a rule reaches the team's work the next time the team changes that part of how it
   works. The files name that moment for their own rules: the next Sprint Retrospective for a Scrum
   with parts removed, or, when the team dropped the Retrospective, a session the Scrum Master holds
   before the next Sprint Planning, where the team plans to bring each part back or stops calling its
   process Scrum ([scrum.md](scrum.md) section 4), the next change of the plan for a mix
   ([combining-approaches.md](combining-approaches.md) section 4), the next time a group adds or
   splits a team or picks a framework ([scaling.md](scaling.md) section 8), a point the project's
   own plan names for regulated work, with a signed contract keeping its terms
   ([regulated-work.md](regulated-work.md) section 7), and the work items started after adoption
   for AI agents ([ai-agents.md](ai-agents.md) section 4). The values and Lean's principles reach a
   running team the same way, at the next point where it reflects on how it works and changes it;
   that reading is this practice's own.

## Security and privacy

There are no known security impacts of the approaches this practice describes. The nearest risk is
an AI coding agent in the team's work: where it runs, what it can read and reach, and which
credentials it gets are set up by [agent-containers.md](../docker/agent-containers.md) sections 3
to 5 before it works without approvals, and [ai-agents.md](ai-agents.md) adds no security rule of
its own. Two files name a security duty that another text owns: a regulator may ask for
cybersecurity risk management across the product's life cycle, which
[regulated-work.md](regulated-work.md) names and does not cover, and security tests that move into
the sprint with the release checks run in the pipeline of [ci-cd](../ci-cd/README.md)
([combining-approaches.md](combining-approaches.md) section 1).

The files touch no personal data: no rule in them collects, stores or sends it. Their examples use
invented names, keys and numbers, such as the Acme Corp support team and the SUP project in
[kanban.md](kanban.md) section 3. What an agent may read, personal data included, falls under the
one rule of [agent-containers.md](../docker/agent-containers.md) section 1.

## The points to adapt

The shape stays: a process the team calls Scrum keeps every event, accountability and artifact
([scrum.md](scrum.md) section 4), every policy that says "Kanban" names its text
([kanban.md](kanban.md) section 1), and a person answers for every change an agent makes
([ai-agents.md](ai-agents.md) section 1). Within that shape, these are the team's or the project's
choices; each file names the options and their costs. A row holds only for a team that runs that
part, and a team that does not skips it.

| What you set | When you set it | Where the options are |
|---|---|---|
| Who decides each deliverable's approach | In planning, before the first pick | [choosing-an-approach.md](choosing-an-approach.md) section 3, with the decider by [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5 |
| Which Agile Fluency zones the organisation needs | When the group weighs what it needs from agile work | [choosing-an-approach.md](choosing-an-approach.md) section 2 |
| The Sprint length, one month or less | Before the first Sprint, then kept | [scrum.md](scrum.md) section 3; the timeboxes that follow from it: [meetings.md](../project-management/meetings.md) section 2 |
| Which Kanban text, with its edition, and how big a change may be | When the team writes its Definition of Workflow, or, on the Method, the explicit policies of the system STATIK designs | [kanban.md](kanban.md) section 1 |
| The WIP control, the pull signal and the service level expectation (SLE) | In the Definition of Workflow; the SLE again once enough items have finished | [kanban.md](kanban.md) section 3; the limits per person and for the team: [principles.md](../project-management/principles.md) section 3 |
| Which list of Lean principles the team works from | Before it adopts any lean practice | [lean-software-development.md](lean-software-development.md) sections 1 and 3 |
| Which XP practice comes first, and how fast the next ones follow | When the team names the problem it feels most | [extreme-programming.md](extreme-programming.md) sections 2 and 3 |
| The base approach of a mix, and each practice added to it | When the plan records the approach, and at each change | [combining-approaches.md](combining-approaches.md) section 4 |
| Whether a product group adopts a scaling framework, and which | When one team can no longer hold the product | [scaling.md](scaling.md) sections 1 to 3 |
| How much plan-driven frame regulated software gets | When the life-cycle model is written, by the software's risk | [regulated-work.md](regulated-work.md) sections 2 and 5 |
| The contract model: a fixed budget and date with a moving scope, capped time and materials, or a fixed scope | Before the contract is agreed | [regulated-work.md](regulated-work.md) section 3 |
| Who answers for an agent's work item, written on the work item as its assignee, or in a comment when the agent's account is the assignee or another person answers | Before the agent starts on it | [ai-agents.md](ai-agents.md) section 4 |
| Whether the team follows the Scrum Guide Expanded instead of the 2020 Guide | Before an agent counts as a Product Developer | [scrum.md](scrum.md) section 8, [ai-agents.md](ai-agents.md) section 4 |

## Sources

Checked 2026-10-30 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Ken Schwaber and Jeff Sutherland — The Scrum Guide, November 2020 — https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf
- [2] Kent Beck with Cynthia Andres — Extreme Programming Explained: Embrace Change, Second Edition, the publisher's free sample pages: contents, Preface and chapter 1 (Pearson Education, 2004; opinion) — https://ptgmedia.pearsoncmg.com/images/9780321278654/samplepages/9780321278654.pdf
- [3] Martin Fowler — The New Methodology (martinfowler.com, 2005; opinion; the author's firm, Thoughtworks, uses an agile approach with its clients, as the text says) — https://martinfowler.com/articles/newMethodology.html
- [4] Martin Fowler — The State of Agile Software in 2018, transcript of a keynote at Agile Australia (martinfowler.com, 2018; opinion) — https://martinfowler.com/articles/agile-aus-2018.html
