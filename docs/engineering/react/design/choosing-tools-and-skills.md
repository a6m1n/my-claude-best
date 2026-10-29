# Choosing tools and skills for a design job

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. Pick the way by what must exist at the end](#2-pick-the-way-by-what-must-exist-at-the-end)
- [3. What is known about design skills](#3-what-is-known-about-design-skills)
- [4. Before a skill: the spec comes first](#4-before-a-skill-the-spec-comes-first)
- [5. Calling a skill, and checking that it ran](#5-calling-a-skill-and-checking-that-it-ran)
- [6. What a skill runs on your machine](#6-what-a-skill-runs-on-your-machine)
- [7. Skills for application screens: when to choose each](#7-skills-for-application-screens-when-to-choose-each)
- [8. Skills for brand pages: how each sets the direction](#8-skills-for-brand-pages-how-each-sets-the-direction)
- [9. Common mistakes](#9-common-mistakes)
- [10. Where it stops holding](#10-where-it-stops-holding)
- [11. Alternatives considered](#11-alternatives-considered)
- [12. Review checklist](#12-review-checklist)
- [13. Sources](#13-sources)

## 1. Purpose and the one rule

This file is for the person who starts a design job with Claude Code, the agent that runs it, and
whoever reviews the design tools a project uses. Read it before you set up a canvas, a Figma
connection or a browser tool for a design job, before you install or call a design skill, and when
you review which design tools and skills a project uses.

It answers two questions. Which way to run the job: section 2 picks it by the artefact that must
exist at the end, and by the gates the account passes. Whether to add a design skill, which one,
and how to tell that it ran: sections 3 to 8. A design skill here is a folder of instructions,
sometimes with scripts, that Claude Code loads to steer how a screen or a page looks; a plugin can
carry one.

Other files own the parts this one builds on, and it links them rather than repeat them. The spec
the model reads is [designing-with-claude-code.md](designing-with-claude-code.md) section 3; each
tool's row, with its status, is section 5 there; the verify loop is section 6, and trust in plugins
in general is section 7. Product mode and brand mode are [visual-design.md](visual-design.md)
section 2. The page techniques that work with or without a skill are
[brand-pages.md](brand-pages.md). How to test a skill against no skill on your own briefs is
[skill-blind-test.md](skill-blind-test.md) section 2.

**When you need this file, and when not.** You need it when the job is more than one more screen
inside an existing theme: the look is still open, a designer wants a Figma file, the team wants a
canvas to compare screens, or someone proposes a design skill. You do not need it for a screen
inside an existing theme. There the way is code in the repository with a browser tool to see it,
[designing-with-claude-code.md](designing-with-claude-code.md) sections 3 to 6 are enough, and no
skill is needed.

The one rule: **choose the way by the artefact that must exist at the end, and a skill by what it
does and what it runs, never by its install count; a skill comes after the spec, is called by
name, and stays only when a test on your own screens keeps it.**

Why:

- In the one scored test of design skills against no skill, a model judge rated them about the
  same as no skill on average, and no test with human raters was found (section 3) [1].
- Install counts say nothing about quality or safety. The skill with the most GitHub stars in that
  test scored like no skill [1]; safety is
  [designing-with-claude-code.md](designing-with-claude-code.md) section 7.
- A way the account cannot run fails late. A session signed in with an API key "cannot publish" a
  `/design` canvas [3], and the setup work is lost.

How sure the evidence is. The gates, and what each skill runs, come from the owners' own pages and
files, read on 2026-10-29 with Claude Code 2.1.312; they settle how a product or a skill works.
Whether a skill helps rests on two preprints, one with a model judge and one that measured working
code, and on single runs judged by their authors. Skill facts change within weeks, so re-read a
row's source before you rely on it; the design [README.md](README.md), "How to adopt", step 5,
says when.

Not covered yet:

- A test with human raters of any design skill against no skill. None was found;
  [skill-blind-test.md](skill-blind-test.md) describes how to run one on your own briefs.
- Whether the rules in a design skill's reference files reach the page on current Opus and Sonnet
  models. The one measurement is of one small skill that is not a design skill [5].
- What writing to a Figma canvas will cost after its beta. Figma says only that it "will eventually
  become a usage-based paid feature" [4].

## 2. Pick the way by what must exist at the end

Name the artefact first, then the way that makes it, then check the way's gate against the account
that will run it. Each tool's detail is its row in
[designing-with-claude-code.md](designing-with-claude-code.md) section 5; this table adds the
choice and names the gate that decides it, whose values that row holds. Read 2026-10-29.

| What must exist at the end | The way | The gate that decides it | Choose it when | Not when |
|---|---|---|---|---|
| A Figma file a designer keeps working on | Figma's remote MCP server. Code to canvas (`generate_figma_design`) "captures your running UI as flat layers, without a connection to your libraries" [6]; writing to the canvas (`use_figma`) builds inside the file [4]. Figma ships skills for its server, such as `figma-use`, inside its plugin [7] | The Figma plan, the seat and the call limits [4], [6], [8]: the Figma row of [designing-with-claude-code.md](designing-with-claude-code.md) section 5 | A designer, or a review, takes the next step in Figma | Nobody will edit the file. A file that must use the team's library components needs writing to the canvas, because code to canvas gives flat layers [6] |
| An editable canvas of screens to compare before any code | Claude Design, now inside Claude: "You can now use Claude Design in any conversation with Claude, including in Claude Code and the Artifacts tab" [9]. In Claude Code, `/design` drafts artboards on one canvas | The plan, the organisation's settings (HIPAA, zero data retention, customer-managed keys), the Claude Code version and how the session signs in [3], [9], [10], [11], [12], [13]: the Claude Design and `/design` rows of [designing-with-claude-code.md](designing-with-claude-code.md) section 5 | The look is still open, and a person wants to compare screens side by side | The screen sits inside an existing theme: the theme decides. The account fails a gate in this row |
| Interface code shipped in the repository | Claude Code builds the screen from the spec, with a browser tool to see it: the Playwright agent CLI, Chrome DevTools MCP or Claude in Chrome (section 5's rows under "Seeing the result") | The browser tool's: Node and a browser, or for Claude in Chrome the plan, the extension version and how the session signs in [14], [15]: the rows under "Seeing the result" of [designing-with-claude-code.md](designing-with-claude-code.md) section 5 | The default for an application screen, once the spec exists | A person first wants to compare looks: use the canvas, or ask for four directions before code ([designing-with-claude-code.md](designing-with-claude-code.md) section 4), then come back to this way |
| A polish pass on an interface that already works | A review or polish skill on the current code (section 7), with the browser tool of the row above to see the screen before and after | What the skill runs on your machine (section 6); some run the project's own preview and test commands | The screens work and look rough; one screen or one diff at a time | The tokens or the components are wrong: fix the spec first (section 4), or every screen needs the same polish again |

- **Before you name a way in a plan or a brief, check each of its gates against the account that
  will run it**: the plan, the Claude Code version (`claude --version`), how the session signs in
  (`/login` or a key), the organisation's settings and the Figma seat. A failed gate shows late and
  quietly: when the Design template is off, "`/design` doesn't draft designs" [3], and Claude in
  Chrome stays off with a key even when you pass `--chrome` [14].

  Check: before the first call, can you name the plan, the CLI version, the sign-in and the seat
  that the way in the brief needs?

- **Hand the result to the verify loop of
  [designing-with-claude-code.md](designing-with-claude-code.md) section 6, and add no second
  loop.** A canvas and a Figma file are inputs to the screen, not a replacement for its review: the
  screen is built in the repository, and a reviewer other than the author judges it there.
- **When a designer drew the screen first, the design file is the spec.** The brief points at the
  frame, Figma's server carries it, and the designer reviews, as section 9 of
  [designing-with-claude-code.md](designing-with-claude-code.md) says. A skill that sets a look has
  nothing to decide there.

## 3. What is known about design skills

Read this before you trust a claim about a design skill, the rows in sections 7 and 8 included. The
older evidence, SkillsBench and the vendor's before-and-after pictures, is
[designing-with-claude-code.md](designing-with-claude-code.md) section 2.

| Claim | What the sources found (read 2026-10-29) | Kind, and who judged |
|---|---|---|
| A design skill makes generated pages look better | Ying et al. audited community skills against a run with no skill over five task kinds, front-end web design among them, with eight skills there [1]. Averaged over the models, the eight web-design skills scored 4.54 to 4.67, against 4.65 with no skill; `ui-ux-pro-max` scored 4.67 [1]. Setting by setting, skills gave a higher visual-design score "in all 6 presentation-generation settings, and in roughly half of the poster-generation and front-end web design settings" [1]. Over all five task kinds, skill runs used "around 3-5× more tokens" [1] | Research, a preprint (arXiv v2, May 2026). The judge was a model: an agent that browses the page and a vision model that reads screenshots. Four NLP researchers checked the judge's scores, not the pages against no skill |
| A skill helps an agent build working web code | Yang and Ding added 31 stack and framework skills to web-development tasks across four models: the skill "reduces mean Pass@2 by 1.3% to 4.2%", raised the token cost by 72% to 394%, and helped in 17% to 36% of skill-project pairs; within the skills that helped, "anti-pattern rules outperform example-heavy content" [16] | Research, a preprint. Judged by automated browser tests: whether the code works, not how it looks |
| A demo shows that a skill works | None of the demos found rates its pages against no skill. At Muzli each brief went to Opus 5.5 with "Anthropic's frontend-design skill", a browser for screenshots and "one standing instruction to check its work in that browser and fix what it saw, at least twice"; the post has no run without the skill [17]. Impeccable's gallery shows five runs without the skill next to three with it, as "First-pass results, before manual polish", with no ratings [18]. interface-design's examples page shows "Default Claude" next to "With Skill", with no ratings [19]. Hallmark's home page counts 26 issues without the skill and 0 with it, and says "The issue counts come from Hallmark's linter" [20]. tasteskill.dev shows no eval [21] | Cases, judged by the skill's own author or publisher |
| A skill and one prompt give a finished interface | interface-design's examples were "Built in a single prompt with the skill enabled" [19]. Of the builders who said how the polish came, two name many rounds: a product designer who designed an audio app in Figma and built it with Claude Code says "it took LOTS of iterations" [22]; the builder of a dashboard made in Claude Artifacts in 14 prompts says "The last 30% ... took just as long as the first 70%" [23] | Cases, each judged by its own author; neither of the last two used a design skill |
| Reviews that ran several skills | Paralect gave "the 8 most popular design packs (by GitHub stars, October 2026)" one brief in fresh sessions and judged the pages itself: `frontend-design` "reliably moves Claude off its default look", and `ui-ux-pro-max` made "the most generic page" [24]. Superdesign ran four skills and a run with no skill on a pricing page: "The honest result: they all do fine", and "a pricing page proves nothing" [25]. On Hacker News one user wrote that impeccable, ui-ux-max "and many, many others ... all seem to converge on the same thing", and one agreed [26]. Two users of `ui-ux-pro-max` report that it made an existing interface worse [27] | Cases and opinions, one brief each, judged by their authors; Superdesign sells a competing design agent |
| Install counts or stars show that a skill is good or safe | No. `ui-ux-pro-max` has the most GitHub stars of the eight skills Ying et al. tested, 142,264 on 2026-10-29 [28], and scored like no skill [1]. Hostile skills with install counts above a million are [designing-with-claude-code.md](designing-with-claude-code.md) section 7. On 2026-10-29 skills.sh listed a mobile-app design skill at 1.1 million installs whose repository had 20 stars [29] | Research; listings |

Interfaces to look at, beside the ones in the table: each was built with Claude or Claude Code and
shown by its builder, with no rating against a run without a skill.

- Lumara, a live sun-and-moon dashboard: its builder says "Claude (Opus 4.7) was used almost
  exclusively for building the site" [88].
- Cuelight, a dashboard with light, dark and auto themes and a command palette, whose commits name
  Claude as a co-author. A test holds its design system: it "reads the real tokens out of style.css
  and holds every text pair to 4.5:1 and every non-text mark to 3:1" [89].
- claude-dashboard, a local dashboard for Claude Code with five themes, "pair-programmed with
  Claude Code" [90].

Whether a design skill helps at all. A test with a run that has no skill weighs more than a demo,
because only that run shows what the skill added. The one such test that scored the pages used a
model judge: the skills scored about the same as no skill on average, and higher in about half of
the web-design settings, at several times the tokens [1]. It did not find that skills never help,
and it did not find that they help in general. No test with human raters was found. So this
practice treats every design skill as an option, kept only when a test on your own briefs, with an
arm that has no skill, keeps it; [skill-blind-test.md](skill-blind-test.md) section 2 describes
that test. The case for a skill as the default is under section 11.

## 4. Before a skill: the spec comes first

- **Put the spec in place before you add a design skill**: the token roles in the theme file, the
  component rule and one screen to follow, as
  [designing-with-claude-code.md](designing-with-claude-code.md) section 3 says. Without a spec the
  skill's own choices become the look, and those choices have no measured gain (section 3). A skill
  written with a spec in mind steps aside for it: `frontend-design` says "the brief's own words
  always win, including when it asks for one of these looks" [30]. At Vercel, the product-design
  skill the company wrote for its own agents says "Do not add decorative novelty, motion, or copy
  unless it clarifies structure, state, or brand intent", and sends the agent to the company's own
  components and accessibility rules [31].
- **Add a skill only when a test on your own screens keeps it**, with an arm that has no skill next
  to it ([skill-blind-test.md](skill-blind-test.md) section 2). Run the test again when the project
  moves to a new model: the Fable 5 guide says skills written for earlier models can make that
  model's output worse ([designing-with-claude-code.md](designing-with-claude-code.md) section 2).
- **Run one skill that sets the look at a time.** With two, a test cannot tell which one helped.
  MindStudio holds that "Running two design skills on the same page tends to create conflicting
  guidance", and pairs one design skill with a skill that tests [32]. A library's own skill, such as
  shadcn/ui's, can run next to it (section 7), since it teaches the project's components rather
  than a look.
- **Keep the design values in the theme file, and treat a skill's own file of choices as a
  draft.** Some skills save their choices: `interface-design` offers to save
  `.interface-design/system.md` [33], and Impeccable writes the look to `DESIGN.md` [34]. The theme
  file is the one the build reads, so the values the model is told and the values the build ships
  stay in one place ([designing-with-claude-code.md](designing-with-claude-code.md) section 3).
  Move a value you keep into the theme file.
- **In a project that already uses a design skill**, keep it, and test it against no skill on the
  next new screen that uses it; read what it runs (section 6) before its next update or the next
  teammate's install. This is the "new and touched code" answer of
  [refactoring.md](../../any-language/refactoring/refactoring.md) section 7.

## 5. Calling a skill, and checking that it ran

- **Call the skill by name in the prompt**: type `/<skill-name>`, or name the skill in the first
  line. Ying et al. found that agents opened the skill file in about 48% of runs on average over
  the five task kinds, in about 20% for Claude Opus 4.6, and in 94% when told to use the skill [1].
  Spence saw a skill called in 12 of 22 headless prompts on Sonnet 4.5 with nothing to push it [36].
  Hallmark's own eval notes "skills do not auto-trigger in `claude -p`, so we invoke by name" [37],
  and ktlesr saw Hallmark start in 0 of 12 requests that did not name it, on Haiku 4.5 [38]. A run
  where the skill never loaded tests no skill.
- **Call it by the name it installs under.** A skill from a plugin is called
  `/plugin-name:skill-name` [39]. taste-skill installs a skill named `design-taste-frontend` [40],
  and Hallmark, installed as the plugin `hallmark`, is called `/hallmark:hallmark` [39], [41]. Some skills run only when called by name,
  because they set `disable-model-invocation: true`: Jakub Krehel's `interface-review` and
  `variant` [42], and both `taste-skill-classics` skills [43].
- **Before you judge the output, check that the skill loaded.** In a headless run with
  `--output-format stream-json --verbose`, the `system/init` event lists the `skills`,
  `plugins`, `tools` and `mcp_servers` the run has [44], [45], and a plugin that failed to load
  shows in `plugin_errors` [45]. A skill the model calls itself shows as a `Skill` tool call in the
  stream; Spence counted those events to measure how often skills started [36]. In a session, look
  for the same call, or for the `/name` you typed, in the transcript.
- **Check that the reference files the step needs were read.** A skill keeps detail in other files,
  and the model opens one only when `SKILL.md` points to it. rulestack found that a reference file
  reached the model in 16 of 16 runs when `SKILL.md` pointed to it, in every pointer style tried,
  from a plain Markdown link to "you must read", and in 0 of 4 runs with no pointer; it tested one
  small skill that is not a design skill, on Opus 5.5 and Sonnet 5.5, with two runs per style [5].
  On Haiku 4.5 only, ktlesr counted "0 attempts to open `anti-patterns.md` or `slop-test.md`, where
  12 of the 14 checked tells are defined", and the rules defined only there made no difference to
  the output [38]. Anthropic's skill guide names the failure "Missed connections" and says "Your
  links might need to be more explicit or prominent" [46].

  Check: does the transcript show the skill's call, and a read of each file its `SKILL.md` names
  for that step? If not, the run tested no skill.

- **After a compaction, call the skill again before the next screen.** Claude Code adds a skill's
  text once and "doesn't re-read the file on later turns"; after a compaction it keeps the first
  5,000 tokens of each skill's latest call, 25,000 in all, and can drop older skills [39]. The end
  of a long skill is the part a long session loses.

## 6. What a skill runs on your machine

[designing-with-claude-code.md](designing-with-claude-code.md) section 7 owns trust in plugins in
general: a plugin runs with your rights, it can change after you read it, malicious skills exist in
numbers, and that section says how to review a plugin before you accept it. This section adds what
is particular to a skill: the ways it runs code, several of them before or outside the model's
turn, and what each skill in sections 7 and 8 runs. A skill that holds instructions only, such as
`frontend-design`, needs nothing below beyond a reading; the risks come with scripts, installers
and hooks.

| How a skill runs code | When it runs | What stops or limits it (read 2026-10-29) | Example |
|---|---|---|---|
| A `!` command in `SKILL.md` | When the skill loads, before the model reads the text; the command's output takes its place | [designing-with-claude-code.md](designing-with-claude-code.md) section 7 | The shadcn/ui skill runs `npx shadcn@latest info --json` this way on every call, so the code that runs is whatever npm serves that day [47]. Datadog Security Labs: "dynamic context commands run before the model sees the skill at all. When that happens, model-level prompt injection defenses never get a chance to intervene" [48] |
| Tools the skill allows in advance (`allowed-tools`) | During the skill's turn, with no prompt | The setting above covers only `!` commands; read the `allowed-tools` line before you install | shadcn/ui allows `Bash(npx shadcn@latest *)` [47] |
| Scripts the skill tells the model to run | During the run, as the model's own commands | Your permission rules and prompts, as for any command the model runs; Datadog notes that "not all prompt injections need to invoke dynamic context" [48] | taste-skill runs Node 22 scripts and a throwaway Chrome [40]; Hallmark runs `theme.mjs` and `sloplint.mjs` [41]; Jakub Krehel's `better-interface` runs the reviewed project's own preview and test commands [49] |
| Hooks the skill's installer adds | After file edits, or at the end of a turn, outside the model's approval | [designing-with-claude-code.md](designing-with-claude-code.md) section 7 | Impeccable's hooks run its engine after edits to design files and on Stop [50]. Its README: "Hooks run outside model approval. In Claude Code, installed command hooks run even when you deny the model's own commands, so the first edit can download the engine" [34] |
| A prebuilt binary | When a script or a hook calls it | Read where it comes from and what checks it | Impeccable downloads its engine 0.1.18 from the project's own GitHub release on first use, and checks it against `engine-checksums.txt`, a file shipped inside the skill folder, "never against anything published beside the binary" [51], [52]. The hash and the binary have the same owner, so the check shows that the file matches the repository, not that the repository is safe. The engine's source is in the repository [51] |
| Content fetched at each run | Every run | Copy the content at a fixed version, and point the skill at the copy | Vercel's `web-design-guidelines` ([designing-with-claude-code.md](designing-with-claude-code.md) section 7). The `ui-skills-root` router has the agent run `npx ui-skills` [54]. Impeccable fetches a set of visual directions from impeccable.style for each new design [34] |
| Data sent out | Every run, or once you connect an account | The skill's telemetry switch, where it has one, and the accounts you connect | Impeccable records which directions were shown and which one you picked unless telemetry is off, and "Turning telemetry off doesn't stop that request" for the directions [34]. The `design` plugin registers remote MCP connectors to Slack, Figma, Linear, Asana, Atlassian, Notion and Intercom [55]. gstack makes its mock-ups and reads them with OpenAI models, on your OpenAI key [56] |
| Files written outside the project | During the run | Read the skill's paths before you install it | taste-skill keeps `~/.taste-skill/history.json` [57]; huashu-design writes `~/.huashu-design/` [58]; Impeccable caches its engine in `~/.impeccable/bin/` [34] |

- **Before you install a design skill, read its `SKILL.md`, its scripts and its installer, and name
  each row of the table above that applies.** A `!` command and a hook run before or outside the
  model's turn, where neither a defence against prompt injection nor a permission prompt sees them
  [48], [34]. Where the instructions are the part you want, copy those files rather than install a
  runner: in `ibelick/ui-skills`, `baseline-ui` and `improve-ui` are instructions only, and the
  router is the part that runs a package from npm [54].

  Check: can you name every command the skill runs, when it runs, and what it fetches or sends? If
  not, it is not ready to install.

- **After the install, read the `hooks` entries in `.claude/settings.json`,
  `.claude/settings.local.json` and `~/.claude/settings.json`.** Impeccable's installer writes its
  hooks to a project or a user settings file [50], and the install screen shows that a hook exists,
  not what it runs ([designing-with-claude-code.md](designing-with-claude-code.md) section 7).
- **The rules on turning off inline commands and hooks, and on install counts as a trust signal,
  are [designing-with-claude-code.md](designing-with-claude-code.md) section 7.** An automated audit on
  a listing site is a pointer, not a review: the skills.sh audit rated `better-interface` "SAFE"
  while it noted that the skill runs the reviewed project's commands [49].

What each skill in sections 7 and 8 runs, read 2026-10-29:

| Skill | Source and licence | What runs, and when | Network and data sent | Outside the project | Paid part |
|---|---|---|---|---|---|
| `frontend-design` | `anthropics/skills`, also a plugin in Anthropic's official marketplace; Apache-2.0 | Nothing: instructions only [30] | None | None | None |
| `interface-design` | `Dammyjay93/interface-design`, MIT; last commit 2026-06-20 | Nothing: instructions; saves `.interface-design/system.md` in the project when you agree [33] | None | None | None |
| `ibelick/ui-skills` | MIT | `baseline-ui` and `improve-ui`: nothing; `improve-ui` writes plans under `design-plans/`. The `ui-skills-root` router: `npx ui-skills …` at run time [54] | npm, through the router | None seen | None seen |
| Jakub Krehel's skills | `jakubkrehel/skills`, MIT | Instructions; `better-interface` runs the project's own preview and test commands [42], [49] | None | None | None seen |
| Emil Kowalski's skills | `emilkowalski/skills`, MIT | Nothing: Markdown only [59] | None | None | None |
| shadcn/ui skill | `shadcn-ui/ui`, MIT | A `!` command, `npx shadcn@latest info --json`, on every call; `allowed-tools` for `npx shadcn@latest *` [47] | npm, the latest version | None | None |
| Magic UI skill | `magicuidesign/magicui`, MIT | Nothing on load; tells the agent to run `npx shadcn@latest add @magicui/<slug>` [60] | npm and the Magic UI registry | None | None in the skill |
| Motion AI Kit | motion.dev; the installer and the skill are MIT | `npx motion-ai` installs the skill and Motion's hosted MCP server, which searches the docs [61] | Motion's MCP server | Not read | Motion+: "CSS spring generation, MotionScore performance audits, plus example and Motion UI source in the editor" [62] |
| GSAP skills | `greensock/gsap-skills`, MIT | Nothing: instructions and examples [63] | None | None | None: "GSAP is 100% free — including every plugin" [63] |
| Vercel `web-design-guidelines` | `vercel-labs/agent-skills`, version 1.0.0; that repository has no licence file, and the rules repository is MIT | Fetches 104 rules from `vercel-labs/web-interface-guidelines` before each review [53] | GitHub, the `main` branch | None | None |
| Anthropic's `design` plugin | `anthropics/knowledge-work-plugins`, Apache-2.0 | Registers remote MCP connectors [55] | Slack, Figma, Linear, Asana, Atlassian, Notion and Intercom, once you sign in | None | None; the connectors use your accounts with those vendors |
| Impeccable | `pbakaus/impeccable`, Apache-2.0; skill 4.8.0, engine 0.1.18 | A `sh` launcher once a session; the engine binary; optional hooks after edits and on Stop; `live` mode runs a script from your `package.json` [51], [50], [34] | The GitHub release on first use; directions from impeccable.style; telemetry unless turned off [34] | `~/.impeccable/bin/` | None seen |
| taste-skill (`design-taste-frontend`) | `Leonxlnx/taste-skill`, MIT; 2.1.5 | Node 22 scripts and a throwaway Chrome profile; "It installs nothing and needs no API keys" [40] | Picture archives; the pages it builds load GSAP and Lenis from a CDN [40] | `~/.taste-skill/history.json` [57] | None |
| `ui-ux-pro-max` | `nextlevelbuilder/ui-ux-pro-max-skill`, MIT | A local Python script over CSV files: "Requires Python 3.x, no external dependencies"; its CLI route is a global npm install [28] | None | The global CLI, if you take that route | A "Premium Version" sold apart, not needed [28] |
| Hallmark | `Nutlope/hallmark`, MIT; 2.0.0 | The model runs `node scripts/theme.mjs` and `sloplint.mjs`; the browser checks "also need `npm i -g puppeteer-core` and Chrome"; an optional hook at edit time [41] | Photos from Wikimedia [64]; its pages load Google Fonts [65] | The global `puppeteer-core`, if you take the browser checks | None |
| `taste-skill-classics` | `Leonxlnx/taste-skill-classics`, MIT | Nothing: instructions, run only when called by name [43] | None | None | None |
| huashu-design | `alchaincyf/huashu-design`, MIT; v3.0.0 | Python 3 scripts at the start and the end of each design task [58] | Optional keys, only for voice and video review [58] | `~/.huashu-design/` | None for pages |
| `website-redesign-skill` | `AbdulHadi404/website-redesign-skill`, MIT | Needs `npm install` in its `scripts/` folder, and a Chromium [66] | npm | None seen | None seen |
| gstack `/design-shotgun` | `garrytan/gstack`, MIT; v1.91.242.0 | Installed by `git clone` into `~/.claude/skills/gstack` and `./setup`, which needs Bun, builds local binaries and registers hooks [56] | OpenAI: `gpt-5.5` and `gpt-image-2`, on your OpenAI key [56] | `~/.claude/skills/gstack` | Your OpenAI usage |
| `awesome-design-md` | `VoltAgent/awesome-design-md`, MIT | Nothing: Markdown files [67] | None | None | The README sells a starter kit and private requests [67] |

## 7. Skills for application screens: when to choose each

An application screen is in product mode ([visual-design.md](visual-design.md) section 2): the
theme decides the look, so a skill here reviews, polishes, adds motion or teaches the component
library more often than it sets a look. No skill below has a gain rated by people (section 3), and
what each one runs is in section 6. Read 2026-10-29; skill facts change within weeks.

| Skill | What it is for | Choose it when | Not when |
|---|---|---|---|
| `interface-design` | Interfaces only: "Not for: Landing pages, marketing sites, campaigns, brand-only work" [33]. Its README offers a base such as "Precision & Density" for developer tools and admin dashboards, or "Warmth & Approachability" for collaborative tools and consumer apps, and the skill keeps its choices in a file in the project [33]. Its examples are app screens "Built in a single prompt with the skill enabled", with no ratings [19] | A new product with no theme yet, to set a base before the theme file exists | The project has a theme file: keep that file as the spec (section 4). A marketing page. You need a skill that is maintained: no commit since 2026-06-20 [33] |
| Impeccable, Operate mode | One skill with modes. Operate is for "app UIs, admin dashboards, settings panels, data tables, tools, authenticated surfaces, anything where the user is in a task" [68]. In it a theme "lends four things and only these: type, palette, density, and one signature move. It never supplies the layout, the navigation model, or the controls" [69], which fits the balance between an effective and a polished screen ([visual-design.md](visual-design.md) section 2) | You want a skill that keeps the layout, the navigation and the controls conventional while the look varies, and you accept its trust note: a prebuilt engine, and hooks if you turn them on (section 6) | You cannot run a binary you did not build. A run nobody watches: new work asks you questions and ends on a decision page where you lock one direction [70]. You want to see app screens first: its gallery holds seven web-site briefs and no app screen [18] |
| Jakub Krehel's skills (`better-interface`, `interface-review`, `better-ui`, `variant`) | `better-interface` "Reviews a screen, flow or whole interface across accessibility, layout, writing, typography, color and UI polish, and returns one ranked report"; `interface-review` reviews "a branch, pull request or uncommitted change for the interface problems it introduced or regressed", and runs only when called; `better-ui` polishes with exact values for border radius, optical alignment, shadows, icon states and animation [42]. `variant` "takes one described piece of UI and builds three versions that differ on purpose", and never ranks them [42] | A review or a polish pass on one screen or one diff; `variant` when a person will pick between three versions of one part | You have not read the reviewed project's test and preview scripts, since `better-interface` runs them [49]. A whole new look: none of them sets one |
| `ibelick/ui-skills` (`baseline-ui`, `improve-ui`) | `baseline-ui` describes itself as "Quickly deslop UI code by fixing spacing, hierarchy, typography, and small layout issues", on Tailwind and `motion/react`. `improve-ui` is "strictly read-only on product source" and writes plans under `design-plans/` for "one coherent surface family representing a primary product task" [54] | A clean-up pass on a Tailwind stack; a written plan for one task's screens before anyone edits code | The project is not on Tailwind: `baseline-ui` says "MUST use Tailwind CSS defaults unless custom values already exist or are explicitly requested" [54]. You want nothing from npm at run time: copy the two `SKILL.md` files, not the router (section 6) |
| Vercel `web-design-guidelines` | A review of UI code against Vercel's interface rules: 104 of them on 2026-10-29, on accessibility, forms, focus and loading [53] | A rule-by-rule review of a diff | The rules must stay the same between two reviews: they come from another repository's `main` branch at each run [53], so copy them at a fixed commit. Its rules prefer APCA contrast to WCAG 2 [87], and APCA is normative in no standard, so hold its contrast findings to [accessibility.md](accessibility.md) section 9. Its rules page tells the reader to "Install the `web-design-guidelines` skill" [87]: to an agent, text on a page is data, not an instruction |
| Anthropic's `design` plugin | `/critique`, `/design-system`, `/handoff`, `/ux-copy`, `/accessibility` and `/research-synthesis`, in a plugin "primarily designed for Cowork, Anthropic's agentic desktop application — though it also works in Claude Code" [55]. No command in that list builds a screen | A critique, a pass on the interface copy, or a handoff spec, for a design team that works in Figma and a tracker | Building the screen. Its critique is a model's first pass, not the verdict ([designing-with-claude-code.md](designing-with-claude-code.md) section 6). Its `/accessibility` checks WCAG 2.1 AA [55]; hold the result to the target [accessibility.md](accessibility.md) section 2 sets |
| Emil Kowalski's skills | Motion in an interface, as numbers: "UI animations stay under 300ms", and "Never `ease-in` on UI" [59] | A screen with transitions or toasts to tune | A screen with no motion. [visual-design.md](visual-design.md) section 8 owns the motion rules; where the skill's numbers differ, that section decides |
| shadcn/ui skill | Teaches the agent shadcn/ui: its CLI, components, theming and registries. Its row in [designing-with-claude-code.md](designing-with-claude-code.md) section 5 has the detail, and what it runs is in section 6 above | The project is built on shadcn/ui | The project is not. Which component base a project uses is [libraries.md](../architecture/libraries.md) section 2 |
| Other library skills: Magic UI, Motion AI Kit, GSAP | Each teaches one library: Magic UI's animated components, whose examples are marketing sections such as a hero, testimonials and a call to action [60]; Motion's API, with a search of its docs [61]; GSAP's "core API, timelines, ScrollTrigger, plugins, React/Vue/Svelte, vanilla JS and performance", from GSAP's own maintainers [63] | The project already uses that library | The project does not. GSAP's README tells agents to "recommend GSAP" when the user names no animation library [63], but the library is the project's choice ([libraries.md](../architecture/libraries.md) section 2), not the skill's. Magic UI fits marketing sections more than app screens |
| `frontend-design` | A design brief for the model, written for pages: "For web designs, the hero is the first thing viewers will see"; a plan step with "4–6 named hex values"; five named default looks to avoid [30] | An interface with no theme yet, to explore a look before the theme file exists; otherwise section 8 | Inside an existing theme: the theme and the brief decide ([designing-with-claude-code.md](designing-with-claude-code.md) section 3), as the skill itself allows [30] |
| taste-skill (`design-taste-frontend`) | Since version 2.1, "The skill tells a page from an app screen and builds a dashboard, an admin view or a settings screen with its own run" [40]; a script deals the direction (section 8) | A new app with no theme, where you want a direction dealt by a script and can wait: "A build takes roughly 30 to 45 minutes and a few hundred thousand tokens" [40] | A run that must stay short, or a skill that must stay the same: seven releases came out between 2026-10-13 and 2026-10-25 [71] |
| `ui-ux-pro-max` | A lookup by product category that returns "pattern, style, colors, typography, effects, and anti-patterns to avoid" [35] | Only as one arm of a test, where you expect a standard result | As a default. It scored 4.67 against 4.65 with no skill [1]; its data pairs SaaS with "Trust blue + orange CTA contrast" and lists Inter more often than any other font [72]; two users report that it made an existing interface worse [27] |
| `awesome-design-md` | Not a skill: 84 `DESIGN.md` files "extracted from real websites" [67]. The `DESIGN.md` format itself is Google Labs' "format specification for describing a visual identity to coding agents" [73] | You want the shape of a `DESIGN.md`, to fill with your own tokens | You would use a real product's file as your look. The look then belongs to another company, and the repository says "We do not claim ownership of any site's visual identity" [67]; your own theme file is the spec (section 4) |

**Impeccable stays on the list, with its trust note.** It is the one skill read here that states
what a theme may change on a task screen and what it may not [69]. Its engine's source is in its
repository, the hash file ships inside the skill rather than beside the binary, and its hooks are
offered at install, not forced [51], [52], [34]. What a reader trades for it is a binary built by
the project rather than by you, checked by a hash from the same owner, and hooks that run outside
the model's approval once turned on (section 6). The case for leaving it out is under section 11.

**A real brand's `DESIGN.md` is never the look.** Take the format, fill it with your own tokens,
and keep the theme file as the spec; the case for copying is under section 11.

## 8. Skills for brand pages: how each sets the direction

A brand page, such as a landing page or a marketing page, is in brand mode
([visual-design.md](visual-design.md) section 2). The techniques that work with or without a skill
are [brand-pages.md](brand-pages.md) sections 3 to 7: fix the direction before the code, name the
defaults to avoid with a replacement, use real content, build the hero first and check the render.
Where a skill keeps its rules so that they reach the page is section 8 of that file. The table
below says how each skill sets the direction and checks the page, so you can pick the ones to test.
None has a gain rated by people; expect a standard result from every arm, and let a test with an
arm that has no skill show which, if any, does better. Read 2026-10-29.

| Skill | How it sets the direction | How it checks the page | Choose it when, and when not | What to expect |
|---|---|---|---|---|
| `frontend-design` | A plan before code: "First, brainstorm a short design plan based on the client's design brief: create a compact token system with color, type, layout, and principles"; five named looks to avoid unless the brief asks for one [30] | "Critique your own work as you build, taking screenshots to review if your environment supports it": the builder checks itself [30] | The first skill to test after no skill: instructions only, nothing runs. Not for a page whose brief already fixes the look: "the brief's own words always win" [30] | Paralect, one brief judged by its own authors: it "reliably moves Claude off its default look" [24]. A Hacker News thread on it holds critical comments, such as "It's placebo at best", and none that says it helps [74]. Ying et al. did not test it [1] |
| Hallmark | A script deals three themes from "a catalog of fifty materials" [41], and skips the themes of the last three builds and the last build's colour, type and accent [64]. A theme file holds tokens, type, surfaces, motion, voice and three to five do-nots, such as "Never a gradient button, a third signal colour or a red debit" [65] | "`scripts/sloplint.mjs --render` checks the page at eight widths, then a subagent reviews it with fresh eyes" [41]. The finish reviewer gets the screenshots, the page source and the theme file, and its answer starts with one word, `recapture`, `rebuild`, `fix` or `ship`, then up to eight findings [75] | Plain HTML and CSS pages, where you run its lint yourself. Not where a global install of `puppeteer-core` is not allowed: the browser checks need it, and only the static checks run without it [41] | A pull request of 2026-08-12, written before version 2.0.0 and still open, found "61 hard gate failures across 11 of the 18 example pages, all of whose CSS stamps claim `gates: all-pass`" [76]. Paralect's run used a version with 21 themes: "cream, a serif and one accented word is close to the default frontend-design bans" [24]. An issue reports that pages "can still converge on similar layouts even when each output passes the existing checks" [77] |
| taste-skill (`design-taste-frontend`) | "The script chooses, not the model: a model asked to pick a direction returns the category default every time" [57]. It deals three of twenty written directions, draws on 247 gallery sites, and avoids its own recent picks [78], [57] | "Screenshots at three widths, a juror's rubric, fix, look again": 1440, 768 and 390 pixels, a lint, and a critique of fourteen passes that the builder runs on its own screenshots [78], [79] | You want a script, not the model, to pick the direction, and can give a build 30 to 45 minutes [40]. Not when the run must be short | Its author holds that "you can't get there with prompting alone" [80]. Paralect tested an older set of 13 skills, so its result does not carry over [24]. Seven releases in October 2026 [71] |
| Impeccable | It notes "the page this category always ships and its predictable opposite", asks you to "list seven concrete visual systems, artifacts, places, or rituals the audience knows by heart", and deals challenger directions from a catalogue [70]. It keeps the product brief, `PRODUCT.md`, apart from the look, `DESIGN.md` [34] | A detector of "62 deterministic rules", with "No LLM, no API key" [34]; a critique by "two isolated sub-agents", one a design review that scores Nielsen's heuristics from 0 to 4, the other the detector with evidence from a browser [81]; a `live` mode that shows variants on "three different primary axes" in the running page [82] | You will answer its questions and pick on its decision page [70], and you accept its trust note (sections 6 and 7). Not for a run nobody watches | One Hacker News user wrote that it and other skills "all seem to converge on the same thing", and one agreed [26]. In Paralect's test, its `/audit` and `/polish` on a page built without a skill left fake logos and a testimonial, "flagged as 'needs your input'" [24] |
| huashu-design | "Three logics, two candidates each — six in total": the approach of a leading designer, two award-winning works in the same medium, and a style rolled from an 84-style library by the current second; three are built and a person picks. Its third round "switched to more options instead of more bans" [58] | A lint of template tells that "only measures checkable facts", and a ledger of what each delivered look was, so the next one differs [58] | A prototype or an HTML landing page, where you pick one of three. Not for a production web app or an SEO site: its Chinese `SKILL.md` keeps those, and back-end systems, out of scope (paraphrased from the Chinese text) [58] | It stops for your pick even in a run nobody watches, unless told to skip [58]. In Paralect's run, "Direction B fell back into the cream-serif default", at about $4.20 of API usage against about $1 for the others [24] |
| `ui-ux-pro-max` | A lookup by product category returns a pattern and tokens; `landing.csv` gives a section order and where the call to action goes, per landing pattern; three dials, `--variance`, `--motion` and `--density` [35], [72] | Nothing renders the page; a pre-delivery checklist covers native app UI only [35] | Only as an arm of a test, to confirm the standard result | A standard page: its data leans to common defaults [72]; Paralect called its page "the most generic page" [24]; it scored like no skill [1] |
| `taste-skill-classics` (`high-end-visual-design`, `minimalist-ui`) | A prompt only: "Before writing code, silently 'roll the dice' and select ONE combination" from three looks and three layouts; the model picks, not a script. `minimalist-ui` has one fixed look [43] | A checklist the model runs on itself; nothing automated [43] | Only when called by name, as an arm of a test | One of a fixed set of looks: three by three, or one [43] |
| `variant` (Jakub Krehel) | Three versions of one piece of UI that differ on purpose, in the real page; one piece per run; it never ranks them [42] | One look in a browser you already have open [42] | You compare one section of a page and a person picks. Not a direction for a whole page | It sets no direction for the page; the pick is yours |
| `website-redesign-skill` | It names "the five things a stranger notices first on the current site (typeface, palette, hero composition, section rhythm, imagery)" and changes each [66] | Scripts, and "A fresh-context reviewer, given only the brief, the direction and the captures" [66] | A redesign of a site that exists. Not a new page | No rated test found |
| gstack `/design-shotgun` | Image mock-ups of several directions from OpenAI models; a person picks one on a board, and a model reads a spec from it [56] | It ends at the chosen mock-up; screenshots at three widths and a lint belong to the separate `/design-html` step [56] | You have an OpenAI key, and the mock-ups may go to OpenAI. Not on Claude Code alone: without its design binary it falls back to HTML wireframes [56] | No independent eval found |

Motion skills, Emil Kowalski's, GSAP's and the Motion AI Kit, shape motion, not the look: section
7. Google Labs' `taste-design`, in stitch-skills, needs access to Google Stitch, another vendor's
tool, and its repository says "This is not an officially supported Google product" [83]. Chrome's
`modern-web-guidance` and Addy Osmani's `web-quality-skills` review a finished page for web
platform practice and quality, and set no look [84], [85]. `avoid-ai-design` is a catalogue of "67
tells, each with a detection signal, why it reads as AI, a fix" [86]; how to name the defaults to
avoid is [brand-pages.md](brand-pages.md) section 4.

## 9. Common mistakes

| Mistake | What it looks like | Why it happens | What it costs | Fix |
|---|---|---|---|---|
| Choosing a skill by its install count | The brief names the top skill on a leaderboard | Skill lists rank by installs | The skill with the most stars in the one scored test scored like no skill [1], and hostile skills showed counts of over a million [2] | Section 3, then a test on your own briefs (section 4) |
| Expecting an installed skill to load | The prompt describes the page and never names the skill | The skill's description seems to match the task | Agents opened the skill in about half of the runs [1], [36]; the result then says nothing about the skill | Call it by name, and check the run (section 5) |
| A skill in place of the spec | No theme file; the skill's choices are the look | One install promises a look | The look moves with the skill's version: taste-skill shipped seven releases in under two weeks [71] | Section 4 |
| Two skills that set the look in one run | Two design skills called in the same session | Each one seems to add something | Conflicting guidance [32], and no test can say which one helped | One at a time (section 4) |
| Taking a skill's own demo as proof | A gallery, a before-and-after pair or the skill's linter count | The pictures look better | Hallmark's own example pages failed its gates while stamped as passing [76] | A test with an arm that has no skill (section 3) |
| Installing without reading what runs | The offered `npx … install` accepted as it is | A skill looks like text | Hooks run "even when you deny the model's own commands" [34], and `!` commands run before the model sees the text [48] | Section 6 |
| A way the account cannot run | A plan built on `/design` for a team that signs in with API keys | The tool page names the feature, not its gate | The canvas "cannot publish" [3]; Claude in Chrome stays off [14] | Check the gates (section 2) |
| A reference file no step points to | The ban list sits in a file `SKILL.md` does not name | The author expects the model to read the folder | The rules in it never reach the page [38], [5] | Section 5 |

## 10. Where it stops holding

- **A prototype you will throw away.** The test against no skill is ceremony there: try a skill and
  look. Section 6 still holds, because a skill runs on your machine whatever the page is for.
- **A screen a designer drew first.** The design file is the spec, and the way is to read it
  through Figma's server ([designing-with-claude-code.md](designing-with-claude-code.md) section
  9). A skill that sets a direction has nothing to decide.
- **An organisation with zero data retention, HIPAA or customer-managed keys.** The canvas ways fail
  their gates there (the Claude Design and `/design` rows of
  [designing-with-claude-code.md](designing-with-claude-code.md) section 5); code in the repository
  stays available (section 2).
- **A run nobody watches.** A skill that asks questions stops or guesses: Impeccable's new work
  asks you to lock a direction [70], and huashu-design waits for a pick unless told to skip [58].
  `/design` is off by default in `-p` runs, the Agent SDK and the GitHub Action [3]. How a test run
  avoids waiting is [skill-blind-test.md](skill-blind-test.md) section 4.
- **A new model.** The results in section 3 come from the models of their day, Claude Opus 4.6
  among them [1], and the Fable 5 guide warns that skills written for earlier models can make
  output worse ([designing-with-claude-code.md](designing-with-claude-code.md) section 2). Test
  the skill again when the project moves to a new model.
- **Skill facts that age within weeks.** taste-skill shipped seven releases between 2026-10-13 and
  2026-10-25 [71], and Hallmark went from 21 themes in Paralect's test to fifty [24], [41]. Re-read
  a row's source before you rely on it.

## 11. Alternatives considered

- **A design skill as the default for every screen.** A demo credits a setup that includes
  `frontend-design` [17], and skill pages show pages made with and without the skill [18], [19],
  [20]. Not taken: none of them rated the pages against no skill, and the one test that scored them
  found the skills about equal to no skill on average [1]. When a test on your own briefs keeps a
  skill, it becomes your default from then on.
- **Choosing skills from a leaderboard of installs.** Not taken: install counts track neither
  quality [1], [28] nor safety [2].
- **Leaving Impeccable off the list.** Its cost is real: an engine binary you do not build, checked
  by a hash its own project ships, and hooks that run outside the model's approval once turned on
  [51], [52], [34]. Not taken: it is the one skill read here that states what a theme may and may
  not change on a task screen [69], and its row carries the trade so a reader can choose.
- **A real product's `DESIGN.md` as the look to follow.** awesome-design-md offers 84 such files
  [67]. Not taken: the look belongs to another company, whose visual identity the repository itself
  does not claim to own [67]. The format is kept [73].

## 12. Review checklist

Ask these when you review a plan or a brief for a design job, or a change to a project's design
skills, and raise each red flag with the author before the change is merged.

| Section | Ask | Red flag |
|---|---|---|
| 2. The way | Does the plan name the artefact that must exist at the end, and was each gate of its way checked against the account that runs it? | A way chosen by the tool's name; `/design` on an API key; Claude in Chrome on a `setup-token` login |
| 3. What is known | Does every claim that a skill helps rest on a test with an arm that has no skill? | A demo, a gallery or an install count as the evidence |
| 4. The spec first | Was the spec in place before the skill, and does only one skill set the look? | No theme file; two skills that set a look in one run; values kept only in a skill's own file |
| 5. Calling a skill | Does the run show the skill's call, and a read of each reference file it names for the step? | The prompt never names the skill; no trace of it in the transcript |
| 6. What it runs | Can the author name every command the skill runs, when it runs, and what it fetches or sends? | An installer nobody read; a new `hooks` entry nobody looked at |
| 7 and 8. The skill | Does the skill fit the screen's mode, and was its row's source re-read since 2026-10-29? | A brand-page skill on an application screen inside a theme; a real brand's `DESIGN.md` as the look |

## 13. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Jiahao Ying, Boxian Ai, Wei Tang, Siyuan Liu and Yixin Cao — OpenSkillEval: Automatically Auditing the Open Skill Ecosystem for LLM Agents (arXiv preprint 2605.23657 v2, 2026; research) — https://arxiv.org/abs/2605.23657
- [2] Michael Bargury — Attackers target agents via the skill supply chain (Zenity Labs, 2026; research, sponsored by Zenity) — https://labs.zenity.io/post/attackers-target-agents-via-the-skill-supply-chain
- [3] Anthropic — Claude Code docs: Artifacts — https://code.claude.com/docs/en/artifacts
- [4] Figma — Figma MCP server: Write to canvas — https://developers.figma.com/docs/figma-mcp-server/write-to-canvas/
- [5] rulestack — 13 of 16 Claude Code runs loaded the skill script (DEV Community, 2026; research) — https://dev.to/rulestack/13-of-16-claude-code-runs-loaded-the-skill-script-the-docs-call-executed-not-loaded-5cic
- [6] Figma — Figma MCP server: Code to canvas — https://developers.figma.com/docs/figma-mcp-server/code-to-canvas/
- [7] Figma — Figma Help Center: Figma skills for MCP — https://help.figma.com/hc/en-us/articles/39166810751895-Figma-skills-for-MCP
- [8] Figma — Figma MCP server: Rate limits & access — https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/
- [9] Anthropic — Claude Design, product page — https://claude.com/product/design
- [10] Anthropic — Claude Help Center: Get started with Claude Design — https://support.claude.com/en/articles/14604416-get-started-with-claude-design
- [11] Anthropic — Claude: Artifacts, feature page — https://claude.com/features/artifacts
- [12] Anthropic — Claude Help Center: Move from standalone Claude Design to Claude — https://support.claude.com/en/articles/17440474-migrate-from-standalone-claude-design-to-claude
- [13] Anthropic — Claude Code docs: Zero data retention — https://code.claude.com/docs/en/zero-data-retention
- [14] Anthropic — Claude Code docs: Use Claude Code with Chrome, extension 1.0.36 — https://code.claude.com/docs/en/chrome
- [15] Anthropic — Claude Code changelog, entries 2.1.91 and 2.1.290 — https://code.claude.com/docs/en/changelog
- [16] Ziyue Yang and Fan Ding — Signal or Noise? A Benchmark Study of Agent Skills in Web Development (arXiv preprint 2608.23067, 2026; research) — https://arxiv.org/html/2608.23067
- [17] Petras Baukys — Opus 5.5 builds Muzli Picks-level websites (Muzli blog, 2026; case) — https://muz.li/blog/claude-opus-5-5-for-designers/
- [18] Impeccable — Gallery — https://impeccable.style/gallery
- [19] interface-design — Examples — https://interface-design.dev/examples.html
- [20] Hallmark — Home page — https://usehallmark.com/
- [21] taste-skill — Home page — https://www.tasteskill.dev/
- [22] madebymagnolia — Show HN thread on Yamanote.fun, with the author's replies (Hacker News, 2026; case) — https://news.ycombinator.com/item?id=48816987
- [23] Kunal Ganglani — Claude Artifacts UI design challenge (personal blog, 2026; case) — https://www.kunalganglani.com/blog/claude-artifacts-ui-design-challenge.md
- [24] Paralect — Top design skills for Claude Code in 2026, tested side by side (Paralect, 2026; case) — https://www.paralect.com/skills/top-design-skills
- [25] Superdesign — Design skills reviewed (Superdesign blog, 2026; case, by the vendor of a competing design agent) — https://superdesign.dev/blog/design-skills-reviewed
- [26] Hacker News commenters — discussion of the Hallmark launch (Hacker News, 2026; opinion) — https://news.ycombinator.com/item?id=49058547
- [27] Users of ui-ux-pro-max — issues #263 and #446 (GitHub, 2026; case) — https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/issues/446
- [28] nextlevelbuilder — ui-ux-pro-max-skill, README and repository — https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- [29] skills.sh — design-mobile-apps (designed-by-ai/skills), listing — https://skills.sh/designed-by-ai/skills/design-mobile-apps
- [30] Anthropic — anthropics/skills, `frontend-design` `SKILL.md` — https://github.com/anthropics/skills/tree/main/skills/frontend-design
- [31] Vercel — Teaching agents product design at Vercel (Vercel blog, 2026; case) — https://vercel.com/blog/teaching-agents-product-design-at-vercel
- [32] MindStudio — How to Build a Website Front End With Claude Opus 5.5 (MindStudio blog, 2026; opinion, by the vendor of an AI agent builder) — https://www.mindstudio.ai/blog/opus-5-5-frontend-coding-workflow
- [33] Dammyjay93 — interface-design, README and `SKILL.md` — https://github.com/Dammyjay93/interface-design
- [34] Paul Bakaus — Impeccable, README, skill 4.8.0 — https://raw.githubusercontent.com/pbakaus/impeccable/main/README.md
- [35] nextlevelbuilder — ui-ux-pro-max, `SKILL.md` — https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main/.claude/skills/ui-ux-pro-max/SKILL.md
- [36] Scott Spence — Measuring Claude Code Skill Activation With Sandboxed Evals (personal blog, 2026; research) — https://scottspence.com/posts/measuring-claude-code-skill-activation-with-sandboxed-evals
- [37] Nutlope — hallmark, `eval/README.md` — https://raw.githubusercontent.com/Nutlope/hallmark/main/eval/README.md
- [38] ktlesr — skill-trigger-measurements, Hallmark ablation (GitHub, 2026; research) — https://github.com/ktlesr/skill-trigger-measurements
- [39] Anthropic — Claude Code docs: Skills — https://code.claude.com/docs/en/skills
- [40] Leonxlnx — taste-skill, README, 2.1.5 — https://github.com/Leonxlnx/taste-skill
- [41] Nutlope — hallmark, README, 2.0.0 — https://raw.githubusercontent.com/Nutlope/hallmark/main/README.md
- [42] Jakub Krehel — jakubkrehel/skills, README and `SKILL.md` files — https://github.com/jakubkrehel/skills
- [43] Leonxlnx — taste-skill-classics, README and `SKILL.md` files — https://github.com/Leonxlnx/taste-skill-classics
- [44] Anthropic — Claude Code docs: Agent SDK TypeScript reference, `SDKSystemMessage` — https://code.claude.com/docs/en/agent-sdk/typescript
- [45] Anthropic — Claude Code docs: Run Claude Code programmatically — https://code.claude.com/docs/en/headless
- [46] Anthropic — Claude Platform docs: Agent Skills best practices — https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- [47] shadcn/ui — `skills/shadcn/SKILL.md` — https://raw.githubusercontent.com/shadcn-ui/ui/main/skills/shadcn/SKILL.md
- [48] Datadog Security Labs — Malicious Coding Agent Skills and the Risk of Dynamic Context (Datadog Security Labs, 2026; research, sponsored by Datadog) — https://securitylabs.datadoghq.com/articles/malicious-skills-supply-chain-risks-in-coding-agents-with-dynamic-context/
- [49] skills.sh — jakubkrehel/skills `better-interface`, Agent Trust Hub audit — https://skills.sh/jakubkrehel/skills/better-interface/security/agent-trust-hub
- [50] Paul Bakaus — Impeccable, `reference/hooks.md` — https://raw.githubusercontent.com/pbakaus/impeccable/main/.claude/skills/impeccable/reference/hooks.md
- [51] Paul Bakaus — Impeccable, launcher script `scripts/impeccable`, engine 0.1.18 — https://raw.githubusercontent.com/pbakaus/impeccable/main/.claude/skills/impeccable/scripts/impeccable
- [52] Paul Bakaus — Impeccable, `scripts/engine-checksums.txt`, engine 0.1.18 — https://raw.githubusercontent.com/pbakaus/impeccable/main/.claude/skills/impeccable/scripts/engine-checksums.txt
- [53] Vercel — vercel-labs/agent-skills, `web-design-guidelines`, version 1.0.0 — https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines
- [54] ibelick — ui-skills, README and `SKILL.md` files — https://github.com/ibelick/ui-skills
- [55] Anthropic — knowledge-work-plugins, `design` plugin — https://github.com/anthropics/knowledge-work-plugins/tree/main/design
- [56] garrytan — gstack, v1.91.242.0 — https://github.com/garrytan/gstack
- [57] Leonxlnx — taste-skill, `scripts/draw.mjs` — https://raw.githubusercontent.com/Leonxlnx/taste-skill/main/skills/taste-skill/scripts/draw.mjs
- [58] alchaincyf — huashu-design, `README.en.md` and `SKILL.md`, v3.0.0 — https://github.com/alchaincyf/huashu-design
- [59] Emil Kowalski — emilkowalski/skills — https://github.com/emilkowalski/skills
- [60] Magic UI — magicuidesign/magicui, `skills/magic-ui` — https://github.com/magicuidesign/magicui/tree/main/skills
- [61] Motion — Install the Motion AI Kit — https://motion.dev/docs/ai-kit-install
- [62] Motion — AI Kit — https://motion.dev/docs/ai-kit
- [63] GreenSock — greensock/gsap-skills — https://github.com/greensock/gsap-skills
- [64] Nutlope — hallmark, `scripts/theme.mjs`, 2.0.0 — https://raw.githubusercontent.com/Nutlope/hallmark/main/skills/hallmark/scripts/theme.mjs
- [65] Nutlope — hallmark, theme file `references/themes/dusk.md` — https://raw.githubusercontent.com/Nutlope/hallmark/main/skills/hallmark/references/themes/dusk.md
- [66] AbdulHadi404 — website-redesign-skill — https://github.com/AbdulHadi404/website-redesign-skill
- [67] VoltAgent — awesome-design-md — https://github.com/VoltAgent/awesome-design-md
- [68] Paul Bakaus — Impeccable, `reference/operate.md` — https://raw.githubusercontent.com/pbakaus/impeccable/main/.claude/skills/impeccable/reference/operate.md
- [69] Paul Bakaus — Impeccable, `reference/mode-operate.md` — https://raw.githubusercontent.com/pbakaus/impeccable/main/.claude/skills/impeccable/reference/mode-operate.md
- [70] Paul Bakaus — Impeccable, `reference/new-work.md` — https://raw.githubusercontent.com/pbakaus/impeccable/main/.claude/skills/impeccable/reference/new-work.md
- [71] Leonxlnx — taste-skill, CHANGELOG, 2.1.5 — https://raw.githubusercontent.com/Leonxlnx/taste-skill/main/CHANGELOG.md
- [72] nextlevelbuilder — ui-ux-pro-max, data files `colors.csv`, `typography.csv` and `landing.csv` — https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/main/.claude/skills/ui-ux-pro-max/data
- [73] Google Labs — design.md — https://github.com/google-labs-code/design.md
- [74] Hacker News commenters — discussion of the frontend-design skill (Hacker News, 2026; opinion) — https://news.ycombinator.com/item?id=49330250
- [75] Nutlope — hallmark, `references/review-finish.md` — https://raw.githubusercontent.com/Nutlope/hallmark/main/skills/hallmark/references/review-finish.md
- [76] A contributor to Nutlope/hallmark — Examples pass their own hard gates: 61 failures → 0 (GitHub pull request #60, 2026; case) — https://github.com/Nutlope/hallmark/pull/60
- [77] A user of Nutlope/hallmark — Cross-Generation Design Similarity Detection (GitHub issue #28, 2026; opinion) — https://github.com/Nutlope/hallmark/issues/28
- [78] Leonxlnx — taste-skill, `SKILL.md` (`design-taste-frontend`) — https://raw.githubusercontent.com/Leonxlnx/taste-skill/main/skills/taste-skill/SKILL.md
- [79] Leonxlnx — taste-skill, `references/critique.md` — https://raw.githubusercontent.com/Leonxlnx/taste-skill/main/skills/taste-skill/references/critique.md
- [80] Leonxlnx — reply in taste-skill issue #106 (GitHub, 2026; opinion) — https://github.com/Leonxlnx/taste-skill/issues/106
- [81] Paul Bakaus — Impeccable, `reference/critique.md` — https://raw.githubusercontent.com/pbakaus/impeccable/main/.claude/skills/impeccable/reference/critique.md
- [82] Paul Bakaus — Impeccable, `reference/live.md` — https://raw.githubusercontent.com/pbakaus/impeccable/main/.claude/skills/impeccable/reference/live.md
- [83] Google Labs — stitch-skills — https://github.com/google-labs-code/stitch-skills
- [84] Google Chrome — modern-web-guidance — https://github.com/GoogleChrome/modern-web-guidance
- [85] Addy Osmani — web-quality-skills — https://github.com/addyosmani/web-quality-skills
- [86] funboy322 — avoid-ai-design — https://github.com/funboy322/avoid-ai-design
- [87] Vercel — vercel-labs/web-interface-guidelines, README — https://github.com/vercel-labs/web-interface-guidelines
- [88] beeswaxpat — Show HN thread on Lumara, with the author's reply (Hacker News, 2026; case) — https://news.ycombinator.com/item?id=47934261
- [89] chandan12ar — cuelight, README and `tests/test_contrast.py` — https://github.com/chandan12ar/cuelight
- [90] Jon Imms — claude-dashboard, README — https://github.com/JonImmsWordpressDev/claude-dashboard
