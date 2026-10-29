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
Which way to run a design job (a canvas, a Figma file, code in the repository or a polish pass),
and which design skill fits which case, is
[choosing-tools-and-skills.md](choosing-tools-and-skills.md). A brand or marketing page, where the
look itself carries the message, is
[brand-pages.md](brand-pages.md). To learn which design skill does best on your own brief before you
adopt one, [skill-blind-test.md](skill-blind-test.md) runs each skill on the same brief and has a
person pick the best page without knowing which skill made it. Whether people can use the screen is
[evaluation.md](../../any-language/ux-evaluation/evaluation.md); its section 11 says what a model can
and cannot judge when it reviews a screen for usability.
Distrust a line that carries a read date six months after that date, until it is read again; the
README's "How to adopt" says how to list those lines.

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

| Claim | Evidence (read 2026-10-01 unless the row gives another date) | Kind |
|---|---|---|
| A design skill or plugin makes generated screens better | Not established. Anthropic's launch post for its `frontend-design` skill shows before-and-after pictures, with no ratings, no sample size and no win rate. The one test of web-design skills against no skill used a model judge and found them about equal to no skill on average ([choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 3 has its figures). No test with human raters was found. The one large study of skills (SkillsBench, 87 tasks, 18 model and harness setups) has no visual design task: curated skills raised the pass rate on average, software engineering gained least, skills made 13 tasks worse, and skills a model wrote for itself scored below no skill at all. The rest of what is known about skills is [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 3 | vendor's claim; one model-judged test; one study, not on design |
| Design principles written into a prompt get built | Mostly not. Five generative UI tools recognised about half of the UX principles in their prompts, and more than a quarter of the design reasons they gave were not in the interface they built ("Design Theater", 120 interfaces) | measured, one study |
| Generated UI converges on one look | Yes. Anthropic's post calls it distributional convergence, and the guides for Sonnet 5, Opus 4.8 and Opus 5.5 each describe a default look the model falls back on (below, and section 4). A benchmark of ten text-to-app tools found generic templates and repeated card grids in the weaker ones | owner's statement; one benchmark |
| A model judges a screen, its own included, as well as a person does | No. The best model judge agreed with human preference 66% of the time, against 85% between human experts, and reading the code mattered more than reading the screenshot (WebDevJudge, 654 pairs). In Anthropic's long runs, scores rose over 5 to 15 rounds, then flattened, and a middle round was often better than the last | measured, one study; owner's practice report |
| A separate critic helps | Yes, with limits. Refining with no critic gained 1.5%; a structured critic gained 10.8 to 17.8%. The gain shrank with each of three rounds, and the critic cost about six times the tokens (600 tasks, scored by a model judge). For Claude Sonnet 4.5, which was its own critic in a separate call that saw only the rendered page, 10.8% is the best round picked per task; after the third round the gain was 6.1%, and the no-critic control was run only with a smaller open model (read 2026-10-29) | measured, one study |
| An edit keeps the earlier screens working | No. The best model passed 74.9% of single edits but finished only 37.3% of five-edit sessions (EvoGenUI-Bench, 150 tasks, 8 models) | measured, one study |
| One current model is best at design | Not established. No model owner or arena page gave a ranking that could be read | unknown |

What the model owner's prompting guides say about design, per model (read 2026-10-29; each new
model gets a new guide, and the advice has changed each time):

| Guide | Design section | What it says to do |
|---|---|---|
| Claude Sonnet 5 | "Design and frontend defaults" | The model may settle into one default style, and "make it clean and minimal" only moves it to another fixed palette. Give a concrete spec (palette, radius, type, motion timing), or ask it to "propose 4 distinct visual directions" and pick one before it builds. `temperature` returns an error on this model, so the four directions are the way to get variety |
| Claude Opus 4.8 | "Design and frontend defaults" | Names the default house style: warm cream backgrounds (about `#F4F1EA`), serif display type, italic word accents and a terracotta accent, which "will feel off for dashboards, dev tools, fintech, healthcare, or enterprise apps". The same two fixes: a concrete alternative, or four directions and then only the one picked |
| Claude Opus 5.5 | "Frontend design defaults" | A general instruction "mostly swaps one default for another". Name the specific patterns to avoid, then "check which styles the first result used instead, and extend the list if needed" |
| Claude Opus 5 | none | Lists "UI and frontend visual replication" as a strength; vision works best when the model has tools to analyse, crop and check its work |
| Claude Sonnet 5.5, Haiku 5.5, Fable 5, Fable 5.1 | none | Fable 5: "Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality" |

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

- **Put the design tokens in the theme file as roles, and let a component name only roles, apart
  from the two exceptions of [visual-design.md](visual-design.md) section 3.**
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
- **Write the component rule as an act: use a native element, a component from the shared folder or
  one of the module's own; a new shared one goes in the shared folder.** Where that folder sits is
  [architecture.md](../architecture/architecture.md) section 3.
  Practitioners report that a fixed component set with CSS tokens stopped off-brand variants, and
  that a component library to anchor on gave better screens than free generation (anecdotes from two
  Hacker News threads and a forum thread, which agree).
- **Keep one screen in the repository that follows the spec, and name it in each brief.** Claude
  Code's best-practices page gives this pattern for any code: "follow the pattern in HotDogWidget.php
  and build a calendar widget". The pointer goes in the prompt for the task, not as a list in
  `CLAUDE.md`.
- **Put an "instead" next to each thing to avoid.** In one practitioner's test, adding an "INSTEAD"
  line next to each "NEVER" line of the `frontend-design` skill won 21 of 28 decided comparisons;
  the judge was a model, the sample was small, and other changes went in at the same time. The
  Opus 5.5 guide asks for named patterns to avoid, and
  [prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 9
  asks for what to do rather than what not to do, where you can.
- **Treat a design skill as an option you test on your own screens, never as the spec.** No design
  skill has a gain that people rated, the one model-judged test found a gain in roughly half of the
  web-design settings ([choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 3), a
  skill written for an earlier model can make a newer one
  worse (the Fable 5 guide), and a skill a model wrote for itself scored below none. Tokens and
  components come first; a skill comes after, if a test on your screens keeps it. What the spec
  holds before a skill joins it is [choosing-tools-and-skills.md](choosing-tools-and-skills.md)
  section 4; the test itself is [skill-blind-test.md](skill-blind-test.md).

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
  Claude Design and the `/design` canvas (section 5) are other places to explore before code;
  which way fits the job is [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 2.
- **Name the looks to avoid, each with what to do instead, and extend the list after the first
  result.** Naming the patterns and extending the list is the Opus 5.5 guide's method; the
  "instead" for each is section 3's, with
  [prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 9.
  The table below lists the defaults sources reported; they move with each model, so use it as a
  first list, not a complete one.
- **Say how the model will see its work**: how to start the app, the route, the widths, both
  themes, and how to produce each state. Claude Code's best-practices page: "Give Claude something it
  can run that comes back pass or fail", and one of its examples is "A browser screenshot next to
  the mockup". Section 6 says who judges what it sees.

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
required, and none has a measured effect on how good a screen looks. Each row was read from the
owner's pages, and its status cell ends with the date of that reading; a part read on another day
carries its own date. Statuses, plans and versions change within months: re-read a row's source
before you rely on it ([README.md](README.md), "How to adopt", says when). "Preview" and "beta"
are the owner's words for a tool that may still change.

Which way to run a design job, and the gates to check before you pick one, is
[choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 2.

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

| Tool | What it does | Status and gates | Trust |
|---|---|---|---|
| The official plugin marketplace, `claude-plugins-official` | Lists the plugins Anthropic maintains, and more from partners and other authors. `/plugin install <name>@claude-plugins-official` first shows what the plugin will install (its skills, hooks and MCP servers among them) with an estimate of its context cost, then asks for a scope: user (all your projects), project (`.claude/settings.json`, committed, so the team shares it; each teammate still runs the install once) or local | Added by Claude Code in the first interactive session. Anthropic also runs `claude-community`, which you add yourself. The old `claude-code-plugins` marketplace in `anthropics/claude-code` is deprecated: skip a tutorial step that adds `anthropics/claude-code`. Topic marketplaces such as `anthropics/knowledge-work-plugins` are added by hand (read 2026-10-29) | Most listings come from partners and other authors, not Anthropic. Auto-update is on by default here, so a plugin can change after you reviewed it (section 7) |

### Design knowledge

Design skills and plugins, such as Anthropic's `frontend-design` skill and `design` plugin,
Impeccable and Vercel's Web Interface Guidelines, are in
[choosing-tools-and-skills.md](choosing-tools-and-skills.md): what each runs on your machine is its
section 6, which fits an application screen its section 7, and which fits a brand page its section
8. Their rows, with the status and the trust note of each, are in that file, so this one does not
repeat them.

### Designs outside the code

| Tool | What it does | Status and gates | Trust |
|---|---|---|---|
| Claude Design (inside Claude; the standalone site claude.ai/design until 2026-12-14) | Designs and clickable prototypes on a canvas. It now runs inside Claude: in any conversation, in Claude Code and in the Artifacts tab. It uses the organisation's design system, and in Claude Code `/design` creates, edits and syncs design projects (next row) | On by default on Free, Pro, Max, Team and Enterprise; on Enterprise since 2026-10-15, except in organisations with HIPAA, and design systems there are off by default (Organization settings > Artifacts). Zero data retention turns artifacts off, so Claude Design is not available under it. No allowance of its own: it counts toward the plan's shared usage limits. No version history yet. The standalone site stays open until 2026-12-14 and is read-only after it; design systems move to Claude's Artifacts page, and chats and comments do not move. The current pages no longer call it a research preview (read 2026-10-29); it launched as one on 2026-04-17 (read 2026-10-01) | Anthropic's own product |
| The `/design` canvas in Claude Code | `/design <brief>` drafts artboards on one canvas and publishes it as a Claude Design artifact; artboards export as PNG or PDF | Claude Code v2.1.265 or later, signed in to a claude.ai account with `/login`: a session on an API key, a gateway token or a cloud-provider credential cannot publish. On the Anthropic API, not Amazon Bedrock, Google Cloud's Agent Platform or Microsoft Foundry. Pro, Max, Team and Enterprise; Free is not listed, although Claude Design in a chat is on Free. Not in an organisation with customer-managed keys (CMEK), HIPAA or zero data retention. Off by default with `-p`, in the Agent SDK, in the GitHub Action and when `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set. The Design template is in beta and on by default on Pro, Max and Team; with it off, `/design` drafts nothing. On Enterprise, Claude Code's page says an Owner turns each template on, while Claude's own pages say Design is on by default since 2026-10-15: check Organization settings > Artifacts (read 2026-10-29) | Anthropic's own |
| Figma's remote MCP server (`https://mcp.figma.com/mcp`) | Reads a design: its context, its variables and a screenshot (`get_design_context`, `get_variable_defs`, `get_screenshot`). Writing to the canvas (`use_figma`) writes to a Figma file. Code to canvas (`generate_figma_design`) turns a running page into Figma frames, as flat layers with no link to your libraries. Code Connect maps Figma components to the components in your code. Figma also ships skills for the server, such as `figma-use`, and example skills such as `figma-generate-design`; `claude plugin install figma@claude-plugins-official` adds the server and the skills together | Figma recommends the remote server over its desktop one. It works on every seat, but View and Collab seats get up to 20 read calls a month, so real use needs a Full or Dev seat: up to 200 calls a day on Professional and Organization plans, 600 on Enterprise. Writing to the canvas needs a Professional, Education, Organization or Enterprise plan, edit access to the file, and a Full seat outside your drafts; it is free during its beta and will then be usage-based, with no price or date published. Code to canvas is open on Starter plans too, its pages carry no beta or price note, and tools that write to a file, code to canvas among them, are exempt from the call limits. Code to canvas was announced on 2026-02-17 (read 2026-10-29) | Use Figma's own server: a community Figma MCP server had a command-injection flaw reachable through prompt injection (CVE-2025-53967, fixed in 0.6.3; read 2026-10-01). Code Connect's gain comes from Figma's own test: median code quality rose from 2 to 3 out of 4, with 29.5% fewer tokens, over 27 tasks (read 2026-10-01) |

### Seeing the result

| Tool | What it does | Status and gates | Trust |
|---|---|---|---|
| The Playwright agent CLI (`@playwright/cli`) with its skill | Opens a page, types and clicks; after each command it returns a snapshot, the page's accessibility tree with a reference for each control; `screenshot` captures what is on screen. `playwright-cli install --skills` writes its skill to `.claude/skills/playwright-cli`, and the skill covers request mocking too | The docs install it with `npm install -g @playwright/cli@latest`, a global install. The pages carry no dates (read 2026-10-01) | Microsoft's own. Preferred over the Playwright MCP server for a coding agent: Playwright's docs point coding agents such as Claude Code to the CLI, rate the MCP server's token cost higher because its tool schemas and snapshots stay in the context, and keep MCP for long exploratory loops. Use the snapshot to check structure and the screenshot to check the look; the docs call the snapshot the more reliable default |
| Chrome DevTools MCP (`npx -y chrome-devtools-mcp@latest`) | Screenshots, snapshots, the console, performance traces and Lighthouse. It also ships a CLI that works without MCP | Needs a current LTS Node and a current stable Chrome (read 2026-10-01) | The Chrome DevTools team's own. It collects usage statistics by default, and the agent can read any data in the browser it drives; [performance.md](../performance/performance.md) section 3 gives the note in full |
| Claude in Chrome | Claude Code drives your Chrome: `claude --chrome`, or `/chrome`. Its docs name design verification as a use: build a screen from a Figma mock, then open it in the browser and check that it matches | Chrome extension v1.0.36 or later; a direct Anthropic plan (Pro, Max, Team, Enterprise) signed in with `/login`. An API key or a long-lived token from `claude setup-token` keeps it off, even with `--chrome`. Not through Amazon Bedrock, Google Cloud's Agent Platform or Microsoft Foundry, and not in WSL. Off by default in Enterprise organisations with HIPAA, where an Owner can turn it on. Since v2.1.290 a project's settings file cannot turn it on: use `--chrome`, `/chrome` or your user settings. Turning it on by default adds context cost, since its tools and instructions then load in every session (read 2026-10-29) | Anthropic's own |
| `/run` and `/verify` | Skills bundled with Claude Code. `/run` starts the app and drives it to show a change working. `/verify` builds and runs the app to confirm that a change does what it should, rather than relying on tests or type checks. Both work out how to start the app from the project type, the README or `package.json`; `/verify` saves its recipe in `.claude/skills/verify/SKILL.md` | `/verify` runs only when you invoke it (since v2.1.215). Once `/verify` records its recipe at the repo root, that skill replaces the bundled one, and from v2.1.286 Claude runs it before each commit except docs-only or test-only changes (skills page and changelog, read 2026-10-29) | Anthropic's own. Its best-practices page: once Claude says it is done, `/verify` "has Claude build and run the app and look at the result. That catches the kind of problem that tests and typechecks miss." |
| A baseline screenshot test | Playwright Test's `toHaveScreenshot()` saves reference images on the first run and compares every later run with them; `npx playwright test --update-snapshots` replaces them. Vitest's browser mode has `toMatchScreenshot` for the same job. Which test runner a project uses is [libraries.md](../architecture/libraries.md) section 6 | Playwright's page carries no date; Vitest's page (v5.0.3) calls the feature stable (read 2026-10-01) | A comparison of pixels, not a model's opinion, so it gives the same answer every time. Rendering differs by operating system, browser version, settings and hardware, so make and compare the images on one setup, such as the CI image. The first run records whatever the screen shows: review the reference images like code |

### The component inventory

| Tool | What it does | Status and gates | Trust |
|---|---|---|---|
| Storybook's MCP server and components manifest | `npx storybook add @storybook/addon-mcp` serves an MCP server from the Storybook dev server; its tools find and show stories and docs, and run tests and accessibility checks. With `features.componentsManifest: true`, Storybook builds a JSON manifest of every component with its description, props and usage examples, at `/manifests/components.json` | Preview: Storybook says its AI features and their API may change (the pages refer to version 10.6). The manifest supports React frameworks. Since Storybook v10.6.0 the addon lives in the main `storybookjs/storybook` repository; its own repository, `storybookjs/mcp`, was archived on 2026-10-14 and is read-only, so take its docs and issues from the main one (read 2026-10-29) | Storybook's own advice: give each component a JSDoc line that says when to use it and when to use another, and treat the stories as the examples an agent copies. The manifest is built from the code, so it does not go stale the way a hand-kept list does |
| The shadcn/ui skill, MCP server and `components.json` | The skill (`pnpm dlx skills add shadcn/ui`) starts when it finds `components.json`. As it loads, it runs `npx shadcn@latest info --json` to read the project: the framework, the Tailwind version, the aliases, the base library and the installed components. It knows the CLI, theming and registries, and its `allowed-tools` let Claude run `npx shadcn@latest` commands without asking during the turn it loads. The MCP server (`npx shadcn@latest mcp`, added to `.mcp.json`) browses, searches and installs from registries. `components.json`'s `aliases` tell the CLI and the skill where components live and how to rewrite their imports | The pages carry no dates. Since July 2026, new projects start on Base UI; which base to choose is [libraries.md](../architecture/libraries.md) section 2. The skill's page and its file read 2026-10-29; the MCP, `components.json` and Base UI pages read 2026-10-01 | A component copied from a registry becomes your code, defects included: one accessibility issue in its mobile Sidebar was closed as not planned. Review a copied component as [accessibility.md](accessibility.md) sections 3 and 11 say. Code from a registry is a dependency ([security.md](../security/security.md) section 10). The skill's load-time command runs whatever CLI version npm serves that day, before the model reads the skill; `disableSkillShellExecution` stops it, and the skill then loses that project context (section 7) |

## 6. The verify loop

The model builds the screen; something else has to judge it. The steps below are what the evidence
in section 2 supports.

- **Give the model a way to see each state the brief names**: start the app, open the route, and
  take a snapshot and a screenshot at each width and in each theme. For a screen copied from a
  mockup, Claude Code's best-practices page lists "A browser screenshot next to the mockup" as a
  check Claude can run, and tells you to ask Claude for evidence: "the command it ran and its
  output, or the screenshot". The comparison finds the defects; who decides that the screen is done
  is the next bullet.
- **When the screen is done, a reviewer other than the author judges it: a person, or a subagent
  with a fresh context.** The author praises its own work: Anthropic's long runs showed it, and two
  Hacker News commenters report Claude Code calling a visibly broken screen "working". Claude
  Code's best-practices page names this check "By someone who didn't write the code": `/code-review`
  "reviews the diff in a fresh subagent that never saw your conversation. It isn't swayed by the
  reasoning that produced the code." The bundled `/code-review` skill (v2.1.218 or
  later, read 2026-10-16) is a fresh-context reviewer for correctness bugs, not for the design; the design reviewer
  is the subagent the brief starts, with the checklist and the screenshots.
- **Give the reviewer a written checklist, and tell it to report only what fails the checklist or
  the brief.** The best-practices page warns that "A reviewer that's asked to find problems will
  always find something", and that fixing every finding adds layers and tests for cases that cannot
  happen. The gain in section 2's study came from a structured critic; refining with no critic
  gained 1.5%.
- **Ask for the reviewer in the brief, not in a standing line of `CLAUDE.md`.** The Opus 5 guide
  (read 2026-10-29) says to remove standing instructions such as "use a subagent to verify",
  because that model verifies its own work without being told to; that is a vendor's statement
  about its model. The Sonnet 5.5 guide (read 2026-10-29) gives its line, not to start reviewer
  subagents unless the user asked for a review, for the `xhigh` and `max` effort levels, to save
  cost.
  Claude Code's best-practices page and the Fable 5 guide recommend a fresh-context reviewer. This
  practice reads them together: the Opus 5 and Sonnet 5.5 guides remove a review baked into every
  prompt, one for a model that checks itself and one to save cost at two effort levels; Claude
  Code's docs ask for a reviewer when the work needs one. A review the brief asks for fits both
  sides.
- **The reviewer reads the code first, then the screenshots.** A model judge did better on the code
  than on the screenshot (WebDevJudge). On usability, against the problems human experts found, a
  model reading screenshots found 21% of them, with false findings of its own (GPT-4o, an older
  model). Zhong et al.'s GPT-4 also reported 95 of 147 items that the researchers rated as no
  usability problem at all (a preprint). So a model reviewer is a first pass that finds real
  problems and false ones, and a person looks at a new screen before it ships. A model does not
  stand in for the people either: when Kuric et al. asked GPT-4.1 to predict first clicks, a
  prediction and not a review, its clicks differed significantly from those of 3,431 people in 53%
  of the tasks (a preprint). What a model can and cannot judge as a usability reviewer is
  [evaluation.md](../../any-language/ux-evaluation/evaluation.md) section 11. The automated
  accessibility checks and the manual pass the person runs are [accessibility.md](accessibility.md) sections 10 and 11.
- **After each edit, check again the screens and the states that passed before.** Edits break
  earlier work (EvoGenUI-Bench). A baseline screenshot test (section 5) turns that check into a
  command.
- **Stop after two or three review rounds.** The critic's gain shrank with each round, at about six
  times the tokens, and in Anthropic's runs a middle round was often the best: keep each round's
  screenshots and choose among them, rather than taking the last. One practitioner reports that two
  or three rounds get most of the way (an anecdote). Anthropic's evaluator ran 5 to 15 rounds per
  generation, in runs of up to four hours; the lower cap here follows the shrinking gain and the
  token cost above. When the same problem survives two
  corrections, run `/clear` and write a better first brief; this is Claude Code's general rule for
  any task, not a result of a design study.

Check: before a screen is merged, ask who answered the checklist. If only the session that built
the screen did, it has not been reviewed.

## 7. Trust: a plugin or a skill runs code

- **It runs with your rights.** Claude Code's docs: "A Claude Code plugin you install can execute
  arbitrary code on your machine with your user privileges." A plugin can carry hooks (shell
  commands), monitors (background shell commands that Claude Code starts on its own), a mod
  (JavaScript that runs inside Claude Code with your permissions), MCP and LSP servers, a `bin/`
  folder added to the shell's path, and skills that enter the context as instructions. Hooks,
  monitors, MCP and LSP servers, and the processes a mod starts run outside the sandbox, and
  permission rules cover only Claude's own tool calls.
- **A skill's inline commands run before the model reads it; turn them off where nobody reviews
  them.** A `` !`command` `` line in a skill runs a shell command before the skill's text is sent
  to Claude, and its output takes the line's place, so the model never gets a chance to refuse it.
  Datadog Security Labs, a security vendor's research team, showed this with a modified skill: the
  model refused its request in words, but the commands had already run. Since Claude Code v2.1.91,
  `"disableSkillShellExecution": true` replaces each such command with
  `[shell command execution disabled by policy]` in skills and custom commands from user, project,
  plugin and additional-directory sources; bundled skills and skills deployed through managed
  settings are not affected. From v2.1.228, Claude Code never runs these commands in skills synced
  from a claude.ai account, whatever the setting. Claude Code's docs advise managed settings for
  it, where a user cannot override it. It does not stop hooks, which a plugin or a skill's installer can add:
  `disableAllHooks` turns those off. Some skills need their inline commands, such as the shadcn/ui
  skill reading the project as it loads (section 5), so the setting costs them that context (read
  2026-10-29). What each design skill runs on your machine is
  [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 6.
- **It can change after you read it.** Auto-update is on by default for Anthropic's official
  marketplaces (except `knowledge-work-plugins` and `first-party-plugins`) and for marketplaces added
  from claude.ai, and off for community and third-party ones (read 2026-10-29). An update can change
  files you already reviewed. A skill can also fetch its rules each time it runs: Vercel's
  `web-design-guidelines` skill fetches them from the main branch of another repository before each
  review, so what the model reads can change while the skill stays the same (read 2026-10-29).
- **Malicious skills exist in numbers.** A study of 98,380 skills from two public registries
  confirmed 157 malicious ones, more than half of them from one author (accepted to USENIX Security
  2026).
- **An install count is not a trust signal.** Zenity Labs, a security vendor, found a family of
  skills on look-alike domains and GitHub organisations that were clean copies when they appeared,
  turned hostile about a week later and told agents to fetch and run a remote payload that collected
  credentials, while the family's displayed install counter passed 1.7 million. The post notes that
  the counter shows installs, not people (read 2026-10-29).
- **For a design tool, prefer the owner's own version** when one exists, such as Figma's own MCP
  server, so a flaw in a community copy does not reach your machine (section 5 names one).

To review a plugin before you accept it, read the install screen for what the plugin adds, then
read the files that run code in its source (`hooks/hooks.json`, `.mcp.json`, `bin/`, monitors, any
mod), and clone it and run `claude --plugin-dir <dir> plugin details <name>` to list what it
contains; the install screen shows that a hook exists, not what it runs (read 2026-10-16). Install
it at project scope, so the team enables the same plugins. Each teammate's install still fetches
the marketplace's current version, so read the plugin again when someone installs it later. To
turn auto-update off for the team, set `autoUpdate: false` on the marketplace's
`extraKnownMarketplaces` entry in `.claude/settings.json`. Without that entry the `/plugin` toggle
changes only your own machine; with it, the toggle also writes `autoUpdate` into that entry, so
review that change like any edit to the file (read 2026-10-29). Packages that a plugin or a registry brings are dependencies, and their rules are
[security.md](../security/security.md) section 10.

## 8. Common mistakes

Each pair shows one problem, then the same example with that problem fixed. All four are about the
invoices screen of [design-brief-example.md](design-brief-example.md). Each Good shows only the
part of the brief or of `CLAUDE.md` its problem is about; the whole brief and the design lines of
`CLAUDE.md` are in that file.

### A prompt made of adjectives

Bad — the spec is three adjectives:

```text
Build the invoices screen at /invoices, in src/routes/invoices.index.tsx. An accounts clerk
opens it to see which invoices are due or overdue and to start paying one. The screen is
effective, the default for a product screen (visual-design.md section 2): dense and quiet, with
motion only to show what changed. Make it clean, modern and professional.
```

"Clean, modern and professional" names nothing a reviewer can check, and the model guides say such
words move the model from one default palette to another.

Good — the same goal, with the spec as things the diff shows:

```text
Build the invoices screen at /invoices, in src/routes/invoices.index.tsx. An accounts clerk
opens it to see which invoices are due or overdue and to start paying one. The screen is
effective, the default for a product screen (visual-design.md section 2): dense and quiet, with
motion only to show what changed. Take every colour and radius from the roles in src/styles.css,
except rounded-full on a circle or a pill and transparent on a part that shows no colour
(visual-design.md section 3), build from native elements, the components in src/core/ui/ and the
module's own, and give the screen the same frame as src/routes/invoices.$invoiceId.pay.tsx.
```

The three adjectives became three things a reviewer can check in the diff: the roles, the
components and the screen to follow (section 4). The case sentence is the same in both: its words
are the case's definition in visual-design.md section 2, not free adjectives.

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
with a fresh context; give it the brief in <brief>, the diff in <diff>, the screenshot file names
in <screenshots> and the checklist in <review_checklist>, and tell it to report only the items
the screen fails. Fix what it reports.
```

The same checklist and screenshots, now judged by a reviewer that did not write the screen and
reports only failures (section 6). A fresh context holds only what it is given, so the brief the
checklist points at goes with them.

### A component list pasted into the instruction file

Bad — `CLAUDE.md` lists the components:

```markdown
## UI components
- Button (`src/core/ui/button.tsx`): the primary action.
- ScreenPending (`src/core/ui/screen-pending.tsx`): a screen that is loading.
```

The list loads in every session and is wrong the day someone adds a component. Claude Code's
best-practices page leaves file-by-file descriptions out of `CLAUDE.md`, and
[claude-md.md](../../../claude-code/claude-md.md) keeps what `ls` shows out of it.

Good — one rule in place of the list:

```markdown
## UI
- Before you add a control to a screen, use a native element, a component from `src/core/ui/` or
  one of the module's own; a new shared one goes in `src/core/ui/`. The diff adds no second
  button, link or dialog.
```

The folder is the list, `ls` shows it, and a Storybook manifest serves it to the agent where the
project has one (section 5); the brief names the one screen to copy (section 4).

## 9. Where it stops holding

- **A prototype you will throw away.** The separate reviewer and the round cap are ceremony there.
  The spec and a screenshot still save rounds.
- **A brand or marketing page.** The distinctive look that the `frontend-design` skill and the
  cookbook aim at belongs there ([visual-design.md](visual-design.md) section 2 has the modes, and
  [brand-pages.md](brand-pages.md) the rules for building one). The spec, the screenshot and the
  separate reviewer still hold.
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
| 3. The spec | Do the components name roles only, apart from the two exceptions of [visual-design.md](visual-design.md) section 3, and do the design lines in `CLAUDE.md` route rather than list? | A raw colour (a hex value) or a default palette class in a component; a component list in `CLAUDE.md` |
| 4. The brief | Does the brief give values, components, states, words and a screen to follow, with an "instead" for each thing to avoid? | Adjectives as the spec; a prohibition with no "instead" |
| 5. The tools | Is each design tool the owner's own version, and was its status re-read since the date in its row? | A community server where the owner ships one; work that depends on a preview tool with no way back |
| 6. The verify loop | Did someone other than the author answer the checklist, from the code and from screenshots of each state? | The only review is the author's; more than three rounds; the earlier screens not checked again |
| 7. Trust | Was every plugin, skill and MCP server reviewed as this section says before it was installed? | An auto-updating plugin nobody has looked at since it was installed; a skill trusted for its install count |

## 11. Sources

Read on 2026-10-01 unless a line gives another date. A source read only as a summary is given as
the place to look.

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
   flatten; a middle round often best; a separate evaluator; 5 to 15 rounds per generation, in runs
   of up to four hours, read 2026-10-29)
6. Sansford et al., critic-in-the-loop study, arXiv:2604.05839, 2026-04:
   https://arxiv.org/html/2604.05839 (gains with and without a structured critic, per round, and the
   token cost; the best-round and third-round figures, and Sonnet 4.5 as its own critic, read
   2026-10-29)
7. WebDevJudge, arXiv:2510.18560, 2025-10-21: https://arxiv.org/html/2510.18560v1 (model judges
   against human agreement; code over screenshots)
8. Heuristic evaluation by GPT-4o, arXiv:2506.16345, 2025-06-19: https://arxiv.org/abs/2506.16345
   (21.2% of the issues experts found)
9. EvoGenUI-Bench, arXiv:2608.29387, 2026-08-29: https://arxiv.org/abs/2608.29387 (edits that
   break earlier work)
10. Practitioner reports on the `frontend-design` skill (anecdotes): wmedia.es, 2026-05-20,
    https://wmedia.es/en/tips/claude-code-frontend-design-skill; Hacker News,
    https://news.ycombinator.com/item?id=49330250 and https://news.ycombinator.com/item?id=49058547
11. Ying et al., "OpenSkillEval: Automatically Auditing the Open Skill Ecosystem for LLM Agents",
    arXiv:2605.23657, v2 2026-05-28: https://arxiv.org/abs/2605.23657 (eight web-design skills
    against no skill, scored by a model judge; higher visual-design scores in roughly half of the
    web-design settings; 3 to 5 times the tokens, averaged over five task kinds; read 2026-10-29)

The model guides and the default looks (sections 2 and 4):

12. Anthropic, prompting best practices, "Frontend design":
    https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
13. Anthropic, the guides per model:
    https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5,
    .../prompting-claude-opus-4-8, .../prompting-claude-opus-5-5, .../prompting-claude-opus-5,
    .../prompting-claude-sonnet-5-5, .../prompting-claude-haiku-5-5, .../prompting-claude-fable-5
    and .../prompting-claude-fable-5-1 (each guide's design section, or its absence; the advice on
    reviewer subagents; read 2026-10-29)
14. Anthropic's cookbook, prompting for frontend aesthetics, the place to look:
    https://raw.githubusercontent.com/anthropics/claude-cookbooks/main/coding/prompting_for_frontend_aesthetics.ipynb
15. The `frontend-design` skill text:
    https://raw.githubusercontent.com/anthropics/claude-code/main/plugins/frontend-design/skills/frontend-design/SKILL.md
    (the looks it now warns against)
16. Skillselion on the skill's failure-mode descriptions, 2026-08-28, a secondary reading:
    https://dev.to/skillselion/anthropics-frontend-design-skill-names-the-three-cliche-ai-looks-hex-codes-included-f29
17. Impeccable's list of overused looks: https://impeccable.style

The spec and the brief (sections 3 and 4):

18. Claude Code, "Artifacts": https://code.claude.com/docs/en/artifacts (tokens in `CLAUDE.md` or a
    theme file, and the order of precedence; the `/design` canvas, with its gates read 2026-10-29)
19. Claude Code, "Best practices": https://code.claude.com/docs/en/best-practices (a short
    `CLAUDE.md`; skills and path-scoped rules that load when the task needs them; "follow the
    pattern in HotDogWidget.php"; a check Claude can run, a browser screenshot next to the mockup
    among them; two failed corrections, then `/clear`; read 2026-10-29)
20. Justin Wetch, an eval of "INSTEAD" lines, 2026-01-05:
    https://www.justinwetch.com/blog/improvingclaudefrontend/
21. Hacker News, "Tells of a Slop UI": https://news.ycombinator.com/item?id=49867038, and
    "Slightly reducing the sloppiness of AI generated front end":
    https://news.ycombinator.com/item?id=48504912 (tells; copy before styling; a fixed component
    set with tokens)
22. Elixir Forum, "Developing great frontends with LLM assistance":
    https://elixirforum.com/t/developing-great-frontends-with-llm-assistance/74417 (a component
    library to anchor on)

The tools (section 5):

23. Claude Code plugins: https://code.claude.com/docs/en/plugins/install and
    https://code.claude.com/docs/en/plugins/anthropic-marketplaces (marketplaces, scopes, the
    deprecated `claude-code-plugins`); https://code.claude.com/docs/en/plugins/loading, for the
    refresh before a later install, the auto-update defaults and the settings entry's `autoUpdate`
    over the toggle (all read 2026-10-29)
24. Claude Design: https://claude.com/product/design (inside Claude; the standalone site until
    2026-12-14); https://support.claude.com/en/articles/14604416-get-started-with-claude-design
    (plans, on by default, shared limits, no version history);
    https://support.claude.com/en/articles/17440474-migrate-from-standalone-claude-design-to-claude
    (what moves and what does not; read-only after 2026-12-14);
    https://support.claude.com/en/articles/16994751-artifacts-admin-guide-for-team-and-enterprise-plans
    and https://claude.com/features/artifacts (the Enterprise default from 2026-10-15, and HIPAA);
    Claude Code's zero data retention page, https://code.claude.com/docs/en/zero-data-retention
    (artifacts off) (all read 2026-10-29); the launch post, 2026-04-17:
    https://www.anthropic.com/news/claude-design-anthropic-labs
25. Figma's MCP server: https://developers.figma.com/docs/figma-mcp-server/ (the remote server
    recommended; a Full seat to write outside your drafts),
    https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/,
    https://developers.figma.com/docs/figma-mcp-server/write-to-canvas/ and
    https://developers.figma.com/docs/figma-mcp-server/code-to-canvas/; Figma's skills:
    https://help.figma.com/hc/en-us/articles/39166810751895-Figma-skills-for-MCP; the code-to-canvas
    announcement, 2026-02-17: https://www.figma.com/blog/introducing-claude-code-to-figma/ (all read
    2026-10-29); the tools: https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/
    and https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server; Code
    Connect's test, 2026-08-05: https://www.figma.com/blog/the-benefits-of-code-connect-in-mcp/
26. Playwright's agent CLI, the place to look: https://playwright.dev/agent-cli/introduction and
    its installation, skills, quick-start and vision-mode pages; the Playwright MCP README:
    https://github.com/microsoft/playwright-mcp
27. Chrome DevTools MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp; Claude in Chrome:
    https://code.claude.com/docs/en/chrome (read 2026-10-29)
28. Claude Code skills, `/run` and `/verify`: https://code.claude.com/docs/en/skills; the version of
    each change, Claude Code's changelog, which also gives 2.1.290 for Claude in Chrome:
    https://code.claude.com/docs/en/changelog (read 2026-10-29)
29. Baseline screenshots, the place to look: https://playwright.dev/docs/test-snapshots and
    https://vitest.dev/guide/browser/visual-regression-testing
30. Storybook's AI pages, the place to look: https://storybook.js.org/docs/ai/mcp/overview,
    https://storybook.js.org/docs/ai/manifests and https://storybook.js.org/docs/ai/best-practices
    (their preview notice at version 10.6, read 2026-10-29); the addon's old repository:
    https://github.com/storybookjs/mcp (moved into `storybookjs/storybook` at v10.6.0, archived on
    2026-10-14; read 2026-10-29)
31. shadcn/ui: https://ui.shadcn.com/docs/skills and the skill file,
    https://raw.githubusercontent.com/shadcn-ui/ui/main/skills/shadcn/SKILL.md (the skill starts
    on `components.json`; the `npx shadcn@latest info --json` line and `allowed-tools`; both read
    2026-10-29); https://ui.shadcn.com/docs/mcp and https://ui.shadcn.com/docs/components-json (the
    place to look); the Base UI default, July 2026:
    https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default; the Sidebar issue:
    https://github.com/shadcn-ui/ui/issues/6761

The verify loop (section 6):

32. Claude Code, "Best practices", as in source 19 (a browser screenshot next to the mockup; ask
    for evidence; `/code-review` as a reviewer that did not write the code; a reviewer that always
    finds something; `/verify` once Claude says it is done; read 2026-10-29)
33. Hacker News, Claude Code calling a broken screen "working":
    https://news.ycombinator.com/item?id=46594200 (two commenters)
34. "Two or three rounds", an anecdote, 2026-06-22:
    https://youcanbuildthings.com/articles/claude-code-screenshot-loop-fix-ui/
35. Zhong, McDonald and Hsieh, "Synthetic Heuristic Evaluation: A Comparison between AI- and
    Human-Powered Usability Evaluation", arXiv:2507.02306, v1 2025-07-03:
    https://arxiv.org/abs/2507.02306 (GPT-4 on screenshots of two mobile apps against five
    experts, on a reference list that pooled the findings of both; severity rated by the
    researchers; read 2026-10-29)
36. Kuric, Demcak and Krajcovic, "What Would GPT Click: Practical Effects of Human-AI Behavioral
    Misalignment and the Cost of Synthetic Participants in User Experience", arXiv:2605.18302, v1
    2026-05-18: https://arxiv.org/abs/2605.18302 (first clicks predicted by GPT-4.1 and GPT-5.2,
    against twelve first-click tests with 3,431 people; read 2026-10-29)

Trust (section 7):

37. Claude Code, plugin security: https://code.claude.com/docs/en/plugins/security
38. A study of 98,380 skills, arXiv:2602.06547, 2026-02-06: https://arxiv.org/abs/2602.06547
39. CVE-2025-53967 in a community Figma MCP server:
    https://github.com/advisories/GHSA-gxw4-4fc5-9gr5
40. Claude Code, inline shell commands in skills and the settings that stop them:
    https://code.claude.com/docs/en/skills (`!` commands, `disableSkillShellExecution`, and skills
    synced from a claude.ai account, from v2.1.228) and
    https://code.claude.com/docs/en/settings-reference (`disableSkillShellExecution` and
    `disableAllHooks`); the version, 2.1.91, in Claude Code's changelog, as in source 28 (read
    2026-10-29)
41. Datadog Security Labs, a security vendor's research team, "Malicious Coding Agent Skills and
    the Risk of Dynamic Context", 2026-05-11:
    https://securitylabs.datadoghq.com/articles/malicious-skills-supply-chain-risks-in-coding-agents-with-dynamic-context/
    (inline commands run before the model sees the skill; read 2026-10-29)
42. Bargury, Zenity Labs, a security vendor, "Attackers target agents via the skill supply chain",
    2026-08-06: https://labs.zenity.io/post/attackers-target-agents-via-the-skill-supply-chain
    (skills that turned hostile; displayed installs, not people; read 2026-10-29)
43. Vercel's `web-design-guidelines` skill:
    https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines (it fetches
    its rules before each review; read 2026-10-29)
