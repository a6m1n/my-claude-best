# Rules for designing with Claude Code

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. What is known, and what is not](#2-what-is-known-and-what-is-not)
- [3. The spec: what the model reads on every screen](#3-the-spec-what-the-model-reads-on-every-screen)
- [4. The brief for one screen](#4-the-brief-for-one-screen)
- [5. The tools](#5-the-tools)
- [6. The verify loop](#6-the-verify-loop)
- [7. Trust: a plugin or a skill runs code](#7-trust-a-plugin-or-a-skill-runs-code)
- [8. Common mistakes](#8-common-mistakes)
- [9. Where it stops holding](#9-where-it-stops-holding)
- [10. Review checklist](#10-review-checklist)
- [11. Sources](#11-sources)

## 1. Purpose and the one rule

This file is for everyone who designs an application screen with Claude Code: the person who asks
for the screen, the agent that builds it, and the person or agent who reviews it. Read it before
you ask Claude Code for a new screen or a visual change, before you add a design tool, a plugin or
a skill to a project, and when you review a screen Claude Code built.

It is about the working loop: what the model reads, the brief for one screen, the tools that let
the model see its work, and who judges the result. How a screen should look is
[visual-design.md](visual-design.md) sections 2 to 9, how it behaves is [ux.md](ux.md) sections 2 to
7, and the accessibility floor it must meet is [accessibility.md](accessibility.md) sections 2 and
9. A prompt that application code sends to a
model is [prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md). The
brief here is a prompt a person types into a coding agent, and section 19 of that file says which
of its rules still hold for one: sections 2, 4, 5 and 9. How a line in `CLAUDE.md` is written is
[claude-md.md](../../../claude-code/claude-md.md#how-to-write-a-line-an-agent-can-follow).
[design-brief-example.md](design-brief-example.md) shows one screen, from the instruction file to
the code.
Every line that carries a read date is to be distrusted after 2027-04-01 until it is read again;
the README's "How to adopt" says how to list those lines.

The one rule: **the model gets a concrete spec and a way to see the result, and a reviewer other
than the author judges it.**

Why:

- Without a spec, the model draws its own default look. The model owner's guides for three recent
  models say so, and say that a concrete spec, or a named list of looks to avoid, is what moves it
  (section 2).
- A model praises its own work. Anthropic's engineering team saw agents "confidently praising the
  work—even when, to a human observer, the quality is obviously mediocre", and in a measured test a
  model judge agreed with people far less often than people agreed with each other (section 6).

How sure the evidence is: the tool docs and the model guides are the owners' own pages, so they
settle what a tool does and what the owner advises. What a guide says about model behaviour is the
vendor's advice, not a measurement. The studies are few, small, and mostly on older models; the
rest is practitioners' reports. Each rule below says which kind it rests on.

## 2. What is known, and what is not

Read this before you trust a claim about a design tool, the ones in section 5 included.

| Claim | Evidence (read 2026-10-01) | Kind |
|---|---|---|
| A design skill or plugin makes generated screens better | Not measured. Anthropic's launch post for its `frontend-design` skill shows before-and-after pictures, with no ratings, no sample size and no win rate. The one large study of skills (SkillsBench, 87 tasks, 18 model and harness setups) has no visual design task: curated skills raised the pass rate on average, software engineering gained least, skills made 13 tasks worse, and skills a model wrote for itself scored below no skill at all | vendor's claim; one study, not on design |
| Design principles written into a prompt get built | Mostly not. Five generative UI tools recognised about half of the UX principles in their prompts, and more than a quarter of the design reasons they gave were not in the interface they built ("Design Theater", 120 interfaces) | measured, one study |
| Generated UI converges on one look | Yes. Anthropic's post calls it distributional convergence, and the guides for Sonnet 5, Opus 4.8 and Opus 5.5 each describe a default look the model falls back on (below, and section 4). A benchmark of ten text-to-app tools found generic templates and repeated card grids in the weaker ones | owner's statement; one benchmark |
| A model judges a screen, its own included, as well as a person does | No. The best model judge agreed with human preference 66% of the time, against 85% between human experts, and reading the code mattered more than reading the screenshot (WebDevJudge, 654 pairs). In Anthropic's long runs, scores rose over 5 to 15 rounds, then flattened, and a middle round was often better than the last | measured, one study; owner's practice report |
| A separate critic helps | Yes, with limits. Refining with no critic gained 1.5%; a structured critic gained 10.8 to 17.8%. The gain shrank with each of three rounds, and the critic cost about six times the tokens (600 tasks, scored by a model judge) | measured, one study |
| An edit keeps the earlier screens working | No. The best model passed 74.9% of single edits but finished only 37.3% of five-edit sessions (EvoGenUI-Bench, 150 tasks, 8 models) | measured, one study |
| One current model is best at design | Not established. No model owner or arena page gave a ranking that could be read | unknown |

What the model owner's prompting guides say about design, per model (read 2026-10-01; each new
model gets a new guide, and the advice has changed each time):

| Guide | Design section | What it says to do |
|---|---|---|
| Claude Sonnet 5 | "Design and frontend defaults" | The model may settle into one default style, and "make it clean and minimal" only moves it to another fixed palette. Give a concrete spec (palette, radius, type, motion timing), or ask it to "propose 4 distinct visual directions" and pick one before it builds. `temperature` returns an error on this model, so the four directions are the way to get variety |
| Claude Opus 4.8 | "Design and frontend defaults" | Names the default house style: warm cream backgrounds (about `#F4F1EA`), serif display type, italic word accents and a terracotta accent, which "will feel off for dashboards, dev tools, fintech, healthcare, or enterprise apps". The same two fixes: a concrete alternative, or four directions and then only the one picked |
| Claude Opus 5.5 | "Frontend design defaults" | A general instruction "mostly swaps one default for another". Name the specific patterns to avoid, then "check which styles the first result used instead, and extend the list if needed" |
| Claude Opus 5 | none | Lists "UI and frontend visual replication" as a strength; vision works best when the model has tools to analyse, crop and check its work |
| Claude Sonnet 5.5, Fable 5, Fable 5.1 | none | Fable 5: "Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality" |

The general prompting page has a "Frontend design" section with a `<frontend_aesthetics>` snippet,
and Anthropic's cookbook has a notebook on frontend aesthetics. Both push toward a distinctive,
surprising look. That fits a brand page, not an application screen; which mode a screen is in is
[visual-design.md](visual-design.md) section 2.

Why the look converges: the model has a default, and an instruction that only says what to avoid
moves it to the next default. The `frontend-design` skill shows the cycle. Anthropic's post on it
warned against Inter and purple gradients on white; the current skill text warns against a cream
background with a serif display and a terracotta accent, which practitioners describe as the look
the skill produced after the first ban. A list of banned fonts goes stale when the next default
appears; a description of the failure, with what to do instead, lasts longer (one practitioner's
reading of the skill, not a test).

## 3. The spec: what the model reads on every screen

The spec is what Claude Code reads for every screen: the theme file, a few lines in the instruction
file, and the code it is told to follow. A brief (section 4) adds what is particular to one screen.

- **Put the design tokens in the theme file as roles, and let a component name only roles.**
  Claude Code's own docs, on the pages Claude publishes as artifacts, tell you to record colours,
  fonts and spacing in `CLAUDE.md` or a theme file, and state the order: "Claude treats your design
  system as higher precedence than its own choices, and your prompt as higher precedence than
  both." That sentence is about artifact pages. For a screen in the repository the same order, the
  project's design system over the model's own choices and the prompt over both, is this
  practice's choice. The theme file is the one the build
  reads, so the values the model is told and the values the build ships sit in one file. Which
  roles and scales a theme holds is [visual-design.md](visual-design.md) sections 3, 5 and 6.
- **Keep the design lines in `CLAUDE.md` few: where the tokens live, the component rule, and the
  route to this folder.** `CLAUDE.md` loads in every session, and a long one gets ignored; knowledge
  needed only for some tasks goes in a skill or a doc that loads when the task needs it (Claude
  Code's best-practices page). Write each line with its moment, its act and its check, as
  [claude-md.md](../../../claude-code/claude-md.md#how-to-write-a-line-an-agent-can-follow) says.
- **Write the component rule as an act: build from the shared components, and put a new shared one
  in the shared folder.** Where that folder sits is
  [architecture.md](../architecture/architecture.md) section 3.
  Practitioners report that a fixed component set with CSS tokens stopped off-brand variants, and
  that a component library to anchor on gave better screens than free generation (anecdotes from two
  Hacker News threads and a forum thread, which agree).
- **Keep one screen in the repository that follows the spec, and name it in each brief.** Claude
  Code's best-practices page gives this pattern for any code: "HotDogWidget.php is a good example.
  follow the pattern". The pointer goes in the prompt for the task, not as a list in `CLAUDE.md`.
- **Put an "instead" next to each thing to avoid.** In one practitioner's test, adding an "INSTEAD"
  line next to each "NEVER" line of the `frontend-design` skill won 21 of 28 decided comparisons;
  the judge was a model, the sample was small, and other changes went in at the same time. The
  Opus 5.5 guide asks for named patterns to avoid, and
  [prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 9
  asks for what to do rather than what not to do, where you can.
- **Treat a design skill as an option you test on your own screens, never as the spec.** No design
  skill has a measured effect (section 2), a skill written for an earlier model can make a newer one
  worse (the Fable 5 guide), and a skill a model wrote for itself scored below none. Tokens and
  components come first; a skill comes after, if a test on your screens keeps it.

## 4. The brief for one screen

The brief is the prompt for one task. A person writes it once and others may read it later, so
[prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) sections 2, 4, 5
and 9 hold for it: the goal first, then the steps in the order they apply; material pasted in goes
in a named tag; each requirement once, as what to do.

- **State the goal, then the spec as concrete values**: the route and the user's task, the token
  roles, the components, the screen to follow, and the states the screen must show (which states a
  screen needs is [ux.md](ux.md) sections 3 and 6). The Opus 4.8 guide says the model "follows explicit specs
  precisely", and both it and the Sonnet 5 guide say that a general word such as "clean" or
  "minimal" only swaps one default palette for another.
- **Write the words the screen shows into the brief**: the heading, the column names, the status
  words, the empty-state sentence. Practitioners report that writing the copy before styling cut
  prose problems, and that generated screens leak the prompt's own words and backend terms into the
  interface (anecdotes, several commenters in one Hacker News thread).
- **When the look is still open, ask for four directions before any code, and pick one.** The Sonnet
  5 and Opus 4.8 guides both give this step. In the Opus 4.8 version, each direction is a
  background colour, an accent colour and a typeface with a one-line reason; you pick one, and the
  model builds only that one. A screen inside an existing theme has no open look: the theme
  decides, and the brief does not ask.
  Claude Design and the `/design` canvas (section 5) are other places to explore before code.
- **Name the looks to avoid, each with what to do instead, and extend the list after the first
  result.** This is the Opus 5.5 guide's method. The table below lists the defaults sources
  reported; they move with each model, so use it as a first list, not a complete one.
- **Say how the model will see its work**: how to start the app, the route, the widths, both
  themes, and how to produce each state. Claude Code's best-practices page: "Give Claude a check it
  can run: tests, a build, a screenshot to compare." Section 6 says who judges what it sees.

The looks generated UI fell back on, as sources reported them (read 2026-10-01):

| Look | Reported by | When |
|---|---|---|
| Inter or system fonts, purple gradients on white | Anthropic's post on the `frontend-design` skill (both); Impeccable's list (overused fonts such as Inter and system defaults only) | 2025-11 |
| A warm cream background (about `#F4F1EA`), serif display type, italic accent words, a terracotta or clay accent | the Opus 4.8 guide; the current `frontend-design` skill | 2026 |
| A near-black background with one acid-green or vermilion accent | the current `frontend-design` skill | 2026 |
| Numbered "01/02/03" section labels, monospace labels, pill-shaped buttons | the Opus 5.5 guide | 2026 |
| Generic templates, a grid of repeated cards | UI-Bench, ten text-to-app tools | 2025-09 |
| All-caps labels, large corner radii, glass with gradients and thin type, heavy borders and shadows, middle-dot dividers, prompt words or backend terms in the copy | a Hacker News thread, "Tells of a Slop UI" (anecdotes, several commenters) | 2026-09 |

A whole brief for one screen, with its reviewer's checklist, is in
[design-brief-example.md](design-brief-example.md).

## 5. The tools

Each tool below gives the model either part of the spec or a way to see the result. None is
required, and none has a measured effect on how good a screen looks. Every row was read from the
owner's pages on 2026-10-01. Statuses, plans and versions change within months: re-read a row's
source before you rely on it ([README.md](README.md), "How to adopt", says when). "Preview" and
"beta" are the owner's words for a tool that may still change.

Start with:

- the spec: the theme file and the design lines of `CLAUDE.md` (section 3); nothing to install;
- components: shadcn/ui's `components.json` and its skill, when the project uses shadcn/ui (the
  row under "The component inventory");
- seeing the result: the Playwright agent CLI with its skill, and the bundled `/run` and `/verify`
  (the rows under "Seeing the result");
- the review: a reviewer subagent with a fresh context and a written checklist (section 6);
  nothing to install;
- regressions: a baseline screenshot test (a row under "Seeing the result");
- a designer's files, only when a designer supplies them: Figma's own remote MCP server (the row
  under "Designs outside the code").

Everything else in the tables is optional, and no tool here has a measured effect on how good a
screen looks.

### Getting plugins and skills

| Tool | What it does | Status and gates (read 2026-10-01) | Trust |
|---|---|---|---|
| The official plugin marketplace, `claude-plugins-official` | Lists plugins from Anthropic and its partners. `/plugin install <name>@claude-plugins-official` first shows the plugin's skills, hooks and MCP servers with an estimate of their context cost, then asks for a scope: user (all your projects), project (`.claude/settings.json`, committed, so the team shares it; each teammate still runs the install once) or local | Added by Claude Code in the first interactive session. Anthropic also runs `claude-community` and a demo marketplace, `claude-code-plugins`; an old tutorial that adds `anthropics/claude-code` gets only the demo one. Topic marketplaces such as `anthropics/knowledge-work-plugins` are added by hand | Most listings come from partners, not Anthropic. Auto-update is on by default here, so a plugin can change after you reviewed it (section 7) |

### Design knowledge

| Tool | What it does | Status and gates (read 2026-10-01) | Trust |
|---|---|---|---|
| The `frontend-design` skill (a plugin in `claude-plugins-official`; a copy is in `anthropics/skills`) | A design brief for the model: plan a token system, review it against the brief, build, critique; one bold element and the rest quiet; the brief's own words win over the skill's | Its README says Claude uses it "automatically ... for frontend work". The current text is a revision of the first one | No measured effect (section 2). It aims at a distinctive look, which fits a brand page; on an application screen the theme and the brief decide, as the skill itself allows. Practitioners report that it trades old clichés for new ones, and that its advice on animation and unusual fonts works against usability on application screens (anecdotes) |
| The `design` plugin (`design@knowledge-work-plugins`) | Commands `/critique`, `/design-system`, `/handoff`, `/ux-copy`, `/accessibility` and `/research-synthesis`; connectors to Figma, Linear, Jira, Notion and others; works from a description or a screenshot | Add the `anthropics/knowledge-work-plugins` marketplace first. Auto-update is off there by default | Its critique is a model reading a screen: a first pass, not the verdict (section 6). Its `/accessibility` checks WCAG 2.1 AA; hold the result against the standard [accessibility.md](accessibility.md) section 2 sets |

### Designs outside the code

| Tool | What it does | Status and gates (read 2026-10-01) | Trust |
|---|---|---|---|
| Claude Design (claude.ai/design) | Designs and clickable prototypes on a canvas. It uses the organisation's design system, can attach a codebase with `/design-sync`, and hands the result to Claude Code ("Send to local coding agent") | Beta; launched on 2026-04-17 as a research preview. Pro, Max, Team and Enterprise plans; on Enterprise an admin turns it on. Counts against normal usage limits; no version history yet | Anthropic's own product |
| The `/design` canvas in Claude Code | `/design <brief>` drafts artboards on one canvas and publishes it as a Claude Design artifact; artboards export as PNG or PDF | Claude Code v2.1.265 or later, signed in with `/login`, on the Anthropic API (not Bedrock, Vertex or Foundry). Pro, Max, Team and Enterprise; on Enterprise an Owner turns on the Design template | Anthropic's own |
| Figma's remote MCP server (`https://mcp.figma.com/mcp`) | Reads a design: its context, its variables and a screenshot (`get_design_context`, `get_variable_defs`, `get_screenshot`). Code to canvas (`generate_figma_design`) turns a running page into editable Figma frames. Code Connect maps Figma components to the components in your code | Figma recommends the remote server over its desktop one. It works on every seat, but View and Collab seats get single-digit calls a month, so real use needs a Dev or Full seat. Writing to the canvas is free during its beta and will become a paid, usage-based feature. Code to canvas was announced on 2026-02-17 | Use Figma's own server: a community Figma MCP server had a command-injection flaw reachable through prompt injection (CVE-2025-53967, fixed in 0.6.3). Code Connect's gain comes from Figma's own test: median code quality rose from 2 to 3 out of 4, with 29.5% fewer tokens, over 27 tasks |

### Seeing the result

| Tool | What it does | Status and gates (read 2026-10-01) | Trust |
|---|---|---|---|
| The Playwright agent CLI (`@playwright/cli`) with its skill | Opens a page, types and clicks; after each command it returns a snapshot, the page's accessibility tree with a reference for each control; `screenshot` captures what is on screen. `playwright-cli install --skills` writes its skill to `.claude/skills/playwright-cli`, and the skill covers request mocking too | The docs install it with `npm install -g @playwright/cli@latest`, a global install. The pages carry no dates | Microsoft's own. Preferred over the Playwright MCP server for a coding agent: Playwright's docs point coding agents such as Claude Code to the CLI, rate the MCP server's token cost higher because its tool schemas and snapshots stay in the context, and keep MCP for long exploratory loops. Use the snapshot to check structure and the screenshot to check the look; the docs call the snapshot the more reliable default |
| Chrome DevTools MCP (`npx -y chrome-devtools-mcp@latest`) | Screenshots, snapshots, the console, performance traces and Lighthouse. It also ships a CLI that works without MCP | Needs a current LTS Node and a current stable Chrome | The Chrome DevTools team's own. It collects usage statistics by default, and the agent can read any data in the browser it drives; [performance.md](../performance/performance.md) section 3 gives the note in full |
| Claude in Chrome | Claude Code drives your Chrome: `claude --chrome`, or `/chrome`. Its docs name design verification as a use: build a screen from a Figma mock, then open it in the browser and check that it matches | Chrome extension v1.0.36 or later; a direct Anthropic plan (Pro, Max, Team, Enterprise) signed in with `/login`. Not with API keys, Bedrock, Vertex or Foundry, and not in WSL. Turning it on by default adds context cost | Anthropic's own |
| `/run` and `/verify` | Skills bundled with Claude Code. `/run` starts the app and drives it to show a change working. `/verify` builds and runs the app to confirm that a change does what it should, rather than relying on tests or type checks. Both work out how to start the app from the project type, the README or `package.json`; `/verify` saves its recipe in `.claude/skills/verify/SKILL.md` | `/verify` needs Claude Code v2.1.200 or later. A search result says Claude stopped running `/verify` on its own after v2.1.215, so you invoke it; re-check on the skills page | Anthropic's own. Its best-practices page: "Run /verify yourself after Claude's check passes." |
| A baseline screenshot test | Playwright Test's `toHaveScreenshot()` saves reference images on the first run and compares every later run with them; `npx playwright test --update-snapshots` replaces them. Vitest's browser mode has `toMatchScreenshot` for the same job. Which test runner a project uses is [libraries.md](../architecture/libraries.md) section 6 | Playwright's page carries no date; Vitest's page (v5.0.3) calls the feature stable | A comparison of pixels, not a model's opinion, so it gives the same answer every time. Rendering differs by operating system, browser version, settings and hardware, so make and compare the images on one setup, such as the CI image. The first run records whatever the screen shows: review the reference images like code |

### The component inventory

| Tool | What it does | Status and gates (read 2026-10-01) | Trust |
|---|---|---|---|
| Storybook's MCP server and components manifest | `npx storybook add @storybook/addon-mcp` serves an MCP server from the Storybook dev server; its tools find and show stories and docs, and run tests and accessibility checks. With `features.componentsManifest: true`, Storybook builds a JSON manifest of every component with its description, props and usage examples, at `/manifests/components.json` | Preview: Storybook says its AI features and their API may change (the pages refer to version 10.6). The manifest supports React frameworks | Storybook's own advice: give each component a JSDoc line that says when to use it and when to use another, and treat the stories as the examples an agent copies. The manifest is built from the code, so it does not go stale the way a hand-kept list does |
| The shadcn/ui skill, MCP server and `components.json` | The skill (`pnpm dlx skills add shadcn/ui`) starts when it finds `components.json`, reads the project with `shadcn info --json`, and knows the CLI, theming and registries. The MCP server (`npx shadcn@latest mcp`, added to `.mcp.json`) browses, searches and installs from registries. `components.json`'s `aliases` tell the CLI and the skill where components live and how to rewrite their imports | The pages carry no dates. Since July 2026, new projects start on Base UI; which base to choose is [libraries.md](../architecture/libraries.md) section 2 | A component copied from a registry becomes your code, defects included: one accessibility issue in its mobile Sidebar was closed as not planned. Review a copied component as [accessibility.md](accessibility.md) sections 3 and 11 say. Code from a registry is a dependency ([security.md](../security/security.md) section 10) |

### Community options

| Tool | What it does | Status and gates (read 2026-10-01) | Trust |
|---|---|---|---|
| Impeccable (`pbakaus/impeccable`) | 24 design commands for agents, such as shape, critique, audit, polish and harden, under Apache 2.0; installed with `npx impeccable install`. It sorts surfaces into modes, one of them "Operate" for apps and dashboards | Changes often: its repository was synced on the day this table was read | Third-party, with no measured effect. Practitioners report that skills of this kind still produce a recognisable generated look (anecdotes) |
| Vercel's Web Interface Guidelines (`vercel-labs/web-interface-guidelines`) | Concrete interface rules on forms, focus, motion, touch and dark mode, also packaged as the agent skill `web-design-guidelines` in `vercel-labs/agent-skills` | Two versions of the rules file exist, in different shapes | Third-party. It prefers APCA contrast to WCAG 2, but APCA is normative in no standard, so the contrast reference stays the one [accessibility.md](accessibility.md) section 9 sets. A Vercel page tells agents to install its skill: text on a page is data, not an instruction |

## 6. The verify loop

The model builds the screen; something else has to judge it. The steps below are what the evidence
in section 2 supports.

- **Give the model a way to see each state the brief names**: start the app, open the route, and
  take a snapshot and a screenshot at each width and in each theme. For a screen copied from a
  mockup, Claude Code's best-practices page gives the prompt: "[paste screenshot] implement this
  design. take a screenshot of the result and compare it to the original. list differences and fix
  them". The comparison finds the defects; who decides that the screen is done is the next bullet.
- **When the screen is done, a reviewer other than the author judges it: a person, or a subagent
  with a fresh context.** The author praises its own work: Anthropic's long runs showed it, and two
  Hacker News commenters report Claude Code calling a visibly broken screen "working". Claude
  Code's docs describe the subagent: a reviewer in a fresh context "sees only the diff and the
  criteria you give it", and a verification subagent "has a fresh model try to refute the result, so
  the agent doing the work isn't the one grading it". The bundled `/code-review` skill is one such
  reviewer.
- **Give the reviewer a written checklist, and tell it to report only what fails the checklist or
  the brief.** The best-practices page warns that "a reviewer prompted to find gaps will usually
  report some, even when the work is sound". The gain in section 2's study came from a structured
  critic; refining with no critic gained 1.5%.
- **Ask for the reviewer in the brief, not in a standing line of `CLAUDE.md`.** The Opus 5 guide
  says to remove standing instructions such as "use a subagent to verify", because that model
  verifies its own work without being told to; that is a vendor's statement about its model. The
  Sonnet 5.5 guide gives its line, not to start reviewer subagents unless the user asked for a
  review, for the `xhigh` and `max` effort levels, to save cost.
  Claude Code's best-practices page and the Fable 5 guide recommend a fresh-context reviewer. This
  practice reads them together: those two prompt guides remove a review baked into every prompt,
  one for a model that checks itself and one to save cost at two effort levels, Claude Code's docs
  ask for a reviewer when the work needs one, and a review the brief asks for fits both.
- **The reviewer reads the code first, then the screenshots.** A model judge did better on the code
  than on the screenshot (WebDevJudge), and a model reading screenshots for usability problems found
  21% of what human experts found, with false findings of its own (GPT-4o, an older model). So a
  model reviewer is a first pass, and a person looks at a new screen before it ships. The automated
  accessibility checks and the manual pass the person runs are [accessibility.md](accessibility.md) sections 10 and 11.
- **After each edit, check again the screens and the states that passed before.** Edits break
  earlier work (EvoGenUI-Bench). A baseline screenshot test (section 5) turns that check into a
  command.
- **Stop after two or three review rounds.** The critic's gain shrank with each round, at about six
  times the tokens, and in Anthropic's runs a middle round was often the best: keep each round's
  screenshots and choose among them, rather than taking the last. One practitioner reports that two
  or three rounds get most of the way (an anecdote). When the same problem survives two
  corrections, run `/clear` and write a better first brief; this is Claude Code's general rule for
  any task, not a result of a design study.

Check: before a screen is merged, ask who answered the checklist. If only the session that built
the screen did, it has not been reviewed.

## 7. Trust: a plugin or a skill runs code

- **It runs with your rights.** Claude Code's docs: "A Claude Code plugin you install can execute
  arbitrary code on your machine with your user privileges." A plugin can carry hooks (shell
  commands), MCP servers, a `bin/` folder added to the shell's path, and skills that enter the
  context as instructions. Hooks and MCP servers run outside the sandbox, and permission rules cover
  only Claude's own tool calls.
- **It can change after you read it.** Auto-update is on by default for Anthropic's official
  marketplaces (except `knowledge-work-plugins` and `first-party-plugins`) and off for community and
  third-party ones (read 2026-10-01). An update can change files you already reviewed.
- **Malicious skills exist in numbers.** A study of 98,380 skills from two public registries
  confirmed 157 malicious ones, more than half of them from one author (accepted to USENIX Security
  2026).
- **For a design tool, prefer the owner's own version** when one exists, such as Figma's own MCP
  server (section 5).

To review a plugin before you accept it, read its hooks, MCP servers and skills on the install
screen. Install it at project scope, so the team shares one reviewed set. Where auto-update is on,
turn it off, or read the plugin again after each update. Packages that a plugin or a registry
brings are dependencies, and their rules are [security.md](../security/security.md) section 10.

## 8. Common mistakes

Each pair shows one problem, then the same example with that problem fixed. All four are about the
invoices screen of [design-brief-example.md](design-brief-example.md).

### A prompt made of adjectives

Bad — the spec is three adjectives:

```text
Build the invoices screen at /invoices, in src/routes/invoices.index.tsx. An accounts clerk
opens it to see which invoices are due or overdue and to start paying one. Make it clean, modern
and professional.
```

"Clean, modern and professional" names nothing a reviewer can check, and the model guides say such
words move the model from one default palette to another.

Good — the same goal, with the spec as things the diff shows:

```text
Build the invoices screen at /invoices, in src/routes/invoices.index.tsx. An accounts clerk
opens it to see which invoices are due or overdue and to start paying one. Take every colour and
radius from the roles in src/styles.css, build from the components in src/core/ui/, and give the
screen the same frame as src/routes/invoices.$invoiceId.pay.tsx.
```

The three adjectives became three things a reviewer can check in the diff: the roles, the
components and the screen to follow (section 4).

### "Make it pop"

Bad — feedback on the first result that names no pattern:

```text
The screen looks generic. Make it pop.
```

A general instruction "mostly swaps one default for another" (the Opus 5.5 guide), and the model
cannot tell which parts of the screen made it look generic.

Good — the same complaint, with the patterns named:

```text
The screen looks generic. The first version used a card for each invoice, a gradient behind the
heading and a coloured pill for each status. Instead, show each invoice as one table row, keep
the screen's background role behind the heading, and show each status as its word in its role
colour.
```

It names the patterns the first result used, each with what to do instead: the Opus 5.5 guide's
method and the "instead" of section 3.

### The author judging its own screenshots

Bad — the author checks its own screenshots:

```text
When the screen builds, take screenshots of the four states and check them against the
checklist in <review_checklist>. Fix what fails.
```

The session that built the screen grades it, and the author praises its own work (section 6).

Good — the same check, by a reviewer with a fresh context:

```text
When the screen builds, take screenshots of the four states. Then start a reviewer subagent
with a fresh context; give it the diff, the screenshots and the checklist in <review_checklist>,
and tell it to report only the items the screen fails. Fix what it reports.
```

The same checklist and screenshots, now judged by a reviewer that did not write the screen and
reports only failures (section 6).

### A component list pasted into the instruction file

Bad — `CLAUDE.md` lists the components:

```markdown
## UI components
- Button (`src/core/ui/button.tsx`): the primary action.
- ExternalLink (`src/billing/list-invoices/external-link.tsx`): a link that leaves the application.
- SanitizedHtml (`src/billing/pay-invoice/sanitized-html.tsx`): HTML that came from the server.
- ScreenPending (`src/core/ui/screen-pending.tsx`): a screen that is loading.
```

The list loads in every session and is wrong the day someone adds a component. Claude Code's
best-practices page leaves file-by-file descriptions out of `CLAUDE.md`, and
[claude-md.md](../../../claude-code/claude-md.md) keeps what `ls` shows out of it.

Good — one rule in place of the list:

```markdown
## UI
- Before you add a control to a screen, use a component from `src/core/ui/`; a new shared one
  goes there too. The diff adds no second button, link or dialog.
```

The folder is the list, `ls` shows it, and a Storybook manifest serves it to the agent where the
project has one (section 5); the brief names the one screen to copy (section 4).

## 9. Where it stops holding

- **A prototype you will throw away.** The separate reviewer and the round cap are ceremony there.
  The spec and a screenshot still save rounds.
- **A brand or marketing page.** The distinctive look that the `frontend-design` skill and the
  cookbook aim at belongs there ([visual-design.md](visual-design.md) section 2 has the modes). The spec, the
  screenshot and the separate reviewer still hold.
- **A screen a designer drew first.** The design file is the spec: the brief points at the frame,
  Figma's server and Code Connect carry it, and the verify loop compares the screenshot with the
  frame. The designer is the reviewer.
- **A model whose guide says otherwise.** Section 2's table holds for the models it names. When a
  project moves to a new model, read that model's guide first; where its design advice differs from
  a rule here, follow the guide for that model and update the table. No owner states this order;
  it is this practice's choice, since the guide is the owner's word on its own model.

## 10. Review checklist

One question per section. Ask them when you review a screen Claude Code built, a brief, or a
change to a project's design tools, and raise each red flag with the author before the change is
merged.

| Section | Ask | Red flag |
|---|---|---|
| 3. The spec | Do the components name roles only, and do the design lines in `CLAUDE.md` route rather than list? | A colour value or a default palette class in a component; a component list in `CLAUDE.md` |
| 4. The brief | Does the brief give values, components, states, words and a screen to follow, with an "instead" for each thing to avoid? | Adjectives as the spec; a prohibition with no "instead" |
| 5. The tools | Is each design tool the owner's own version, and was its status re-read since the table's date? | A community server where the owner ships one; work that depends on a preview tool with no way back |
| 6. The verify loop | Did someone other than the author answer the checklist, from the code and from screenshots of each state? | The only review is the author's; more than three rounds; the earlier screens not checked again |
| 7. Trust | Was every plugin, skill and MCP server reviewed as this section says before it was installed? | An auto-updating plugin nobody has looked at since it was installed |

## 11. Sources

All read on 2026-10-01. A source read only as a summary is given as the place to look.

What is known and what is not (section 2):

1. Anthropic, "Improving frontend design through Skills", 2025-11-12:
   https://www.claude.com/blog/improving-frontend-design-through-skills (distributional
   convergence; the Inter and purple-gradient default; before-and-after pictures with no
   measurement)
2. Li et al., SkillsBench, arXiv:2602.12670, v4 2026-06-14: https://arxiv.org/abs/2602.12670
   (skills' effect over 87 tasks, none visual; self-written skills below the baseline)
3. "Design Theater", arXiv:2607.22928, 2026-07-24: https://arxiv.org/abs/2607.22928 (UX principles
   in prompts mostly not built)
4. UI-Bench, arXiv:2508.20410, 2025-09-03: https://arxiv.org/html/2508.20410v3 (generic templates
   and repeated card grids)
5. Rajasekaran, Anthropic Engineering, "Harness design for long-running apps", 2026-03-24:
   https://anthropic.com/engineering/harness-design-long-running-apps (self-praise; scores that
   flatten; a middle round often best; a separate evaluator)
6. Critic-in-the-loop study, arXiv:2604.05839, 2026-04: https://arxiv.org/html/2604.05839 (gains
   with and without a structured critic, per round, and the token cost)
7. WebDevJudge, arXiv:2510.18560, 2025-10-21: https://arxiv.org/html/2510.18560v1 (model judges
   against human agreement; code over screenshots)
8. Heuristic evaluation by GPT-4o, arXiv:2506.16345, 2025-06-19: https://arxiv.org/abs/2506.16345
   (21.2% of the issues experts found)
9. EvoGenUI-Bench, arXiv:2608.29387, 2026-08-29: https://arxiv.org/abs/2608.29387 (edits that
   break earlier work)
10. Practitioner reports on the `frontend-design` skill (anecdotes): wmedia.es, 2026-05-20,
    https://wmedia.es/en/tips/claude-code-frontend-design-skill; Hacker News,
    https://news.ycombinator.com/item?id=49330250 and https://news.ycombinator.com/item?id=49058547

The model guides and the default looks (sections 2 and 4):

11. Anthropic, prompting best practices, "Frontend design":
    https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
12. Anthropic, the guides per model:
    https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5,
    .../prompting-claude-opus-4-8, .../prompting-claude-opus-5-5, .../prompting-claude-opus-5,
    .../prompting-claude-sonnet-5-5, .../prompting-claude-fable-5 and .../prompting-claude-fable-5-1
    (each guide's design section, or its absence; the advice on reviewer subagents)
13. Anthropic's cookbook, prompting for frontend aesthetics, the place to look:
    https://raw.githubusercontent.com/anthropics/claude-cookbooks/main/coding/prompting_for_frontend_aesthetics.ipynb
14. The `frontend-design` skill text:
    https://raw.githubusercontent.com/anthropics/claude-code/main/plugins/frontend-design/skills/frontend-design/SKILL.md
    (the looks it now warns against)
15. Skillselion on the skill's failure-mode descriptions, 2026-08-28, a secondary reading:
    https://dev.to/skillselion/anthropics-frontend-design-skill-names-the-three-cliche-ai-looks-hex-codes-included-f29
16. Impeccable's list of overused looks: https://impeccable.style

The spec and the brief (sections 3 and 4):

17. Claude Code, "Artifacts": https://code.claude.com/docs/en/artifacts (tokens in `CLAUDE.md` or a
    theme file, and the order of precedence; the `/design` canvas)
18. Claude Code, "Best practices": https://code.claude.com/docs/en/best-practices (a short
    `CLAUDE.md`; skills that load on demand; "Reference existing patterns"; give Claude a way to
    verify; the adversarial review step; two failed corrections, then `/clear`)
19. Justin Wetch, an eval of "INSTEAD" lines, 2026-01-05:
    https://www.justinwetch.com/blog/improvingclaudefrontend/
20. Hacker News, "Tells of a Slop UI": https://news.ycombinator.com/item?id=49867038, and
    "Slightly reducing the sloppiness of AI generated front end":
    https://news.ycombinator.com/item?id=48504912 (tells; copy before styling; a fixed component
    set with tokens)
21. Elixir Forum, "Developing great frontends with LLM assistance":
    https://elixirforum.com/t/developing-great-frontends-with-llm-assistance/74417 (a component
    library to anchor on)

The tools (section 5):

22. Claude Code plugins: https://code.claude.com/docs/en/plugins/install and
    https://code.claude.com/docs/en/plugins/anthropic-marketplaces (marketplaces, scopes,
    auto-update)
23. The `frontend-design` plugin:
    https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design; the
    `design` plugin: https://github.com/anthropics/knowledge-work-plugins/tree/main/design
24. Claude Design: https://www.anthropic.com/news/claude-design-anthropic-labs (2026-04-17) and
    https://support.claude.com/en/articles/14604416-get-started-with-claude-design (beta, plans)
25. Figma's MCP server: https://developers.figma.com/docs/figma-mcp-server/,
    https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server,
    https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/,
    https://developers.figma.com/docs/figma-mcp-server/code-to-canvas/ and
    https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/; Code Connect's test,
    2026-08-05: https://www.figma.com/blog/the-benefits-of-code-connect-in-mcp/
26. Playwright's agent CLI, the place to look: https://playwright.dev/agent-cli/introduction and
    its installation, skills, quick-start and vision-mode pages; the Playwright MCP README:
    https://github.com/microsoft/playwright-mcp
27. Chrome DevTools MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp; Claude in Chrome:
    https://code.claude.com/docs/en/chrome
28. Claude Code skills, `/run` and `/verify`, the place to look:
    https://code.claude.com/docs/en/skills
29. Baseline screenshots, the place to look: https://playwright.dev/docs/test-snapshots and
    https://vitest.dev/guide/browser/visual-regression-testing
30. Storybook's AI pages, the place to look: https://storybook.js.org/docs/ai/mcp/overview,
    https://storybook.js.org/docs/ai/manifests and https://storybook.js.org/docs/ai/best-practices
31. shadcn/ui: https://ui.shadcn.com/docs/skills, https://ui.shadcn.com/docs/mcp and
    https://ui.shadcn.com/docs/components-json (the place to look); the Base UI default, July 2026:
    https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default; the Sidebar issue:
    https://github.com/shadcn-ui/ui/issues/6761
32. Impeccable: https://github.com/pbakaus/impeccable; Vercel's guidelines:
    https://github.com/vercel-labs/web-interface-guidelines; WCAG 3, a working draft whose contrast
    method is not decided: https://www.w3.org/TR/wcag-3.0/

The verify loop (section 6):

33. Claude Code, "Best practices", as in source 18 (the verification subagent; "Add an adversarial
    review step"; run `/verify` yourself)
34. Hacker News, Claude Code calling a broken screen "working":
    https://news.ycombinator.com/item?id=46594200 (two commenters)
35. "Two or three rounds", an anecdote, 2026-06-22:
    https://youcanbuildthings.com/articles/claude-code-screenshot-loop-fix-ui/

Trust (section 7):

36. Claude Code, plugin security: https://code.claude.com/docs/en/plugins/security
37. A study of 98,380 skills, arXiv:2602.06547, 2026-02-06: https://arxiv.org/abs/2602.06547
38. CVE-2025-53967 in a community Figma MCP server:
    https://github.com/advisories/GHSA-gxw4-4fc5-9gr5
