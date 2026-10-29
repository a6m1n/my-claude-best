# Blind test of design skills

**Not run yet.** This file describes a test that nobody has run. Every step was read in its
owner's documentation or source on 2026-10-29, at Claude Code 2.1.312, Playwright 1.64.1 and
@axe-core/playwright 4.14.0, and none of it was tried. A step that rests on behaviour no owner
documents is marked *not yet tried*; the pilot of section 4 settles each one before the full
test. A person runs the test later, from a Claude Code session started in a terminal of their
own, with the bench files in [blind-test-example.md](blind-test-example.md): the session prepares
the files, runs the bench and reads the results, and every arm runs in Claude Code, as `claude -p`
on the person's own plan. Only the token step runs outside Claude Code (section 1).

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. The design of the test](#2-the-design-of-the-test)
- [3. The bench: a scratch project and what it isolates](#3-the-bench-a-scratch-project-and-what-it-isolates)
- [4. Running each arm headless](#4-running-each-arm-headless)
- [5. Screenshots and the contrast floor](#5-screenshots-and-the-contrast-floor)
- [6. The blind pick](#6-the-blind-pick)
- [7. Reading the result, and building a skill of your own](#7-reading-the-result-and-building-a-skill-of-your-own)
- [8. Security: every arm runs third-party code](#8-security-every-arm-runs-third-party-code)
- [9. Common mistakes](#9-common-mistakes)
- [10. Where it stops holding](#10-where-it-stops-holding)
- [11. Alternatives considered](#11-alternatives-considered)
- [12. Review checklist](#12-review-checklist)
- [13. Sources](#13-sources)

## 1. Purpose and the one rule

This file is for anyone who wants to know whether a design skill makes Claude Code build
better-looking pages than no skill, on their own briefs: people, and AI agents that prepare the
test for a person. Read it before you recommend a design skill for brand pages, before you build
a skill of your own, and before you set up any comparison of skills. Brand pages are the pages
[visual-design.md](visual-design.md) section 2 puts in brand mode, such as a landing page, a
marketing site or a portfolio. How each skill sets its direction, and what to expect from it, is
[choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 8; the techniques that make
a generated page look good are [brand-pages.md](brand-pages.md).

The test answers a question no published test has answered: no published test has had
independent people judge, blind, the pages made with a design skill and without one [1], [2].
What the one model-judged comparison found is in
[choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 3. A review by Superdesign, a vendor of a competing tool,
ran several skills on one pricing page and was judged by its author [2].

The one rule: **every arm gets the same brief, model, effort, tools and clean start; people pick
the best page without knowing which arm made it; and every win is counted against the picks that
were asked for, not against the pages that came back.**

When to use it, and when it is too much:

- Use it when a choice of skill will be copied by others: a team default, a recommendation in a
  library, or the decision to build a skill of your own (section 7).
- It is too much for one page for one client. A full bench runs every arm on three to five
  briefs, twice each; one arm, `taste-skill`, takes "roughly 30 to 45 minutes" a build by its own
  README [3], and every run counts against your plan's usage limits [4]. For one page, pick a
  skill by [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 8 and check the
  page with the verify loop of [designing-with-claude-code.md](designing-with-claude-code.md)
  section 6.
- It does not fit application screens built on a design system: the system's tokens fix the look
  ([visual-design.md](visual-design.md) section 12), so the arms have no direction to compete on.
  Skills for app screens are [choosing-tools-and-skills.md](choosing-tools-and-skills.md)
  section 7.

What it leaves out on purpose: native apps; page speed; any paid tier; and any skill that needs
another vendor's key or account. gstack's `/design-shotgun` is out for that reason: on Claude
Code its design binary uses OpenAI's models, and only on Codex "it needs no `OPENAI_API_KEY`"
[5]. Every arm and every tool in this file runs from Claude Code on your own Claude plan.

How an agent applies it: an agent in a Claude Code session prepares the bench, from the clone of
each arm to the scripts, runs it, and reads the records and the count. Only the token step runs
outside Claude Code, in a plain terminal, never through the Bash tool or the `!` prefix: a command
run through the `!` prefix adds "the command and its output to the conversation context" [48], and
`claude setup-token` prints the token to the terminal [12], so run there it puts the token into the
transcript. The person exports the token in that terminal and starts `claude` there. That session
runs the pilot, the bench and the page server as background commands: since 2.1.288, a local
session you work in from a terminal "has no time limit on background commands" [49]. It stays open
until the count. *Not yet tried*: whether those commands get the exported token and keep running
for the days the bench takes; the pilot settles it. When they do not, the person runs them in a
plain terminal that stays open, such as a `tmux` session. The agent never judges, never shows a
person a page next to its arm's name, and never opens the key before the picks are in.

Not covered yet:

- a test with human raters of any design skill against no skill: this bench fills the gap once it
  has run;
- how many judges and sets a pick among seven or eight arms needs before a lead in wins means
  more than chance: no source read for this file sizes such a pick (section 7);
- whether the rules in a design skill's reference files reach the page on Opus or Sonnet: the one
  measurement used a small skill that is not a design skill [6].

## 2. The design of the test

- **The arms.** No skill (a plain prompt, the baseline), `frontend-design`, Hallmark,
  `taste-skill`, Impeccable, `ui-ux-pro-max` and `taste-skill-classics`
  (`high-end-visual-design`); huashu-design is optional. `ui-ux-pro-max` and
  `taste-skill-classics` stay in although the research expects a standard result from them,
  because the test is how to check that.
- **Everything else is equal.** One model and one effort, set by name on every run
  ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md)
  section 15); one prompt; the same copy and photos; the same tools; a fresh folder, home folder
  and Claude Code configuration for every run (section 3); and one skill per run, called by name,
  at a pinned commit (section 4). Fonts are the arm's choice, because choosing type is part of
  most arms' direction step: `frontend-design`'s plan, for one, starts with "a compact token system
  with color, type, layout, and principles" [7].
- **The briefs.** Three to five real briefs of different kinds, such as a product landing page, a
  portfolio, a local business and a pricing page, with real copy and no placeholder text. One
  brief of a common pattern shows little: in Superdesign's review "they all do fine", and its
  author adds "That is exactly why a pricing page proves nothing" [2].
- **The runs.** At least two runs per arm and brief, because the same prompt gives a different
  page each time; why, and what that does to a comparison, is
  [repeated-runs.md](../../python/evals/repeated-runs.md) section 2. For one brief, run number *k*
  of every arm forms one set.
- **Nobody answers a run.** The prompt asks the model to infer the audience and the tone from the
  brief, ask nothing, and build the direction it recommends. A run that stops with a question,
  leaves no page, or ends in an error fails; it gets one more attempt; failed runs are reported
  per arm next to the wins. They stay in the count as picks asked for, the rule
  [evals.md](../../python/evals/evals.md) section 6 owns, so an arm that often fails does not look
  better than it is.
- **The pick is blind.** Each page is shot at the first screen, at a desktop and a phone width,
  the same way for every arm, under a random id with every name removed. For each set, each judge
  sees one page per arm, in an order shuffled for that judge, and picks the best. In Li et al.'s
  human study of generated web pages, 50 annotators judged pairs of pages blind, in a shuffled
  order [8]. The person who runs the bench sees no page next to its arm's name before the judging
  ends.
- **More than one judge, a designer among them, where possible.** Judges disagree most on looks:
  in RefCraft, Wang et al. found that "More subjective criteria, such as overall visual character,
  exhibit greater human-human and evaluator-human disagreement" [9].
- **Scroll notes after the still picks.** Each judge then scrolls every page, still without names,
  and writes a few words on scroll feel and motion. The notes do not change the count; they show
  what a still cannot (section 7).
- **The contrast floor first.** A page whose text falls below the floor of
  [visual-design.md](visual-design.md) section 4 leaves the pick, whatever its looks; brand pages
  keep that floor ([visual-design.md](visual-design.md) section 12). Section 5 says how it is
  checked.
- **Recorded, not judged.** The time and tokens of each run come from the run's own record; they
  are reported and play no part in the pick.
- **The result.** Wins per arm per brief, counted against the picks asked for; each arm's failed
  runs and contrast exits beside them; and the mechanisms the winners share (section 7).

Check: does every set a judge saw hold one page for each arm whose run finished and met the floor,
and nothing that names an arm?

## 3. The bench: a scratch project and what it isolates

Build the bench in a scratch folder of its own, made before any file is saved into it.
[blind-test-example.md](blind-test-example.md) holds its files and the commands in order.

- **Put it outside every repository and outside your home folder,** so that no `CLAUDE.md`,
  `CLAUDE.local.md` or `.claude/` folder sits above it, your own `~/.claude/` included. Claude Code
  "loads `CLAUDE.md` and `CLAUDE.local.md` from your current working directory and every directory
  above it" [10], and project skills from `.claude/skills/` "in every parent directory up to the
  repository root" [15], so a file above the bench would reach every run. The example gives a
  one-line check.
- **Never under `/tmp`.** macOS deletes what sits in `/tmp` untouched for more than three days
  [52], and the bench runs for days. On macOS, `/Users/Shared/skill-bench` meets all three
  conditions.
- **What it needs, read on 2026-10-29.** Claude Code 2.1.312 (`--permission-prompts` needs 2.1.259
  or later [11]); a Claude Pro, Max, Team or Enterprise plan, which the token below requires [12];
  Node 22 or later and an installed Chrome, Edge or Chromium, which `taste-skill`'s scripts ask for
  [3]; git; and Python 3 for the scripts of `ui-ux-pro-max` and huashu-design. Hallmark's render
  checks also use Chrome [13]. The bench installs none of these.
- **Every install happens inside the bench.** Playwright 1.64.1 and @axe-core/playwright 4.14.0 go
  into the bench's `node_modules`, and `PLAYWRIGHT_BROWSERS_PATH=0` keeps Playwright's browser there
  too, instead of in the user cache (`~/Library/Caches/ms-playwright` on macOS) [14]. Hallmark's
  README asks for `npm i -g puppeteer-core` for its render checks [13]; the bench installs
  `puppeteer-core` locally instead, since Node looks for a package in every folder above a script
  and the runs sit under the bench. *Not yet tried*: the pilot checks that Hallmark's render step
  finds it. Install exact versions and keep `package-lock.json`, so a rerun gets the same code;
  [security.md](../security/security.md) section 10 owns the rules for dependencies.
- **Each arm is a pinned copy of its skill folder.** Clone each arm's repository into the bench at
  the commit you test; the runner copies the skill's folder into the run's
  `.claude/skills/<name>/`, where it loads as a project skill [15]. One way of installing for every
  arm keeps the arms equal; a commit is an exact version, while installed plugins "update
  automatically when the marketplace they came from has auto-update turned on" [16]; nothing runs at
  install; and nothing lands in your home folder. The cost: the bench tests the skill folder, not
  what a plugin or an installer adds around it, such as Impeccable's optional hooks [17].

The arms, read on 2026-10-29. What each skill runs on your machine is
[choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 6.

| Arm | Repository, commit read | Skill name; folder copied | Written outside the run's work folder, and where the bench puts it | Not yet tried |
|---|---|---|---|---|
| No skill | none | none | nothing | nothing |
| `frontend-design` | anthropics/skills `41bbe19` | `frontend-design`; `skills/frontend-design` | nothing: instructions only [7] | nothing |
| Hallmark | Nutlope/hallmark `8f6969f` | `hallmark`; `skills/hallmark` | `npm i -g puppeteer-core` for render checks [13]: installed in the bench instead | whether its scripts find the bench's `puppeteer-core` and your Chrome |
| `taste-skill` | Leonxlnx/taste-skill `12af471` | `design-taste-frontend`; `skills/taste-skill` | a history of its picks in `~/.taste-skill/history.json` [18]: in the run's own home folder | whether it finds your Chrome when the home folder is the run's |
| Impeccable | pbakaus/impeccable `5e745ac` | `impeccable`; `.claude/skills/impeccable` | an engine binary it downloads into `~/.impeccable/bin/` [17]: into the run's own home folder, once per run | whether it builds without a person: for new work it asks through the question tool and has the user lock a direction on a decision page [19] |
| `ui-ux-pro-max` | nextlevelbuilder/ui-ux-pro-max-skill `28b3b8d` | `ui-ux-pro-max`; `.claude/skills/ui-ux-pro-max` | nothing found: a Python script reads the skill's own data files [20] | nothing |
| `taste-skill-classics` | Leonxlnx/taste-skill-classics `5e08c93` | `high-end-visual-design`; `skills/soft-skill` | nothing: instructions only, and "it runs only when you call it by name" [21] | nothing |
| huashu-design, optional | alchaincyf/huashu-design `4fc7bfd` | `huashu-design`; the repository root | `~/.huashu-design/` [22]: in the run's own home folder | whether it builds without a person's pick: its `SKILL.md`, in Chinese, says it stops after three directions, unattended or not, unless told to skip (read in translation) [22] |

By their own text, read on 2026-10-29, none of these arms needs an API key or a paid tier.
`taste-skill` "needs no API keys" [3]; Impeccable's checks use "No LLM, no API key" [17];
`ui-ux-pro-max` sells a premium version that the free skill does not need [20].

**What a run must not inherit, and what keeps each thing out.** `--bare` is the documented clean
mode for scripts, but "bare mode doesn't use your subscription login" [23], so the bench does not
use it. It keeps your login and drops the rest:

| What would reach a run | What keeps it out | Not yet tried |
|---|---|---|
| An API key in your shell, which a `-p` run uses whenever it is present [12], and every other variable of your shell | the runner passes on a short list of variables (`PATH`, `SHELL`, `TERM`, `LANG`, `LC_ALL`, `TMPDIR`, `USER`, `LOGNAME`) and nothing else | whether an arm misses a variable: the pilot shows it |
| Your user settings, hooks, skills, plugins, `~/.claude.json` and auto memory | `HOME` and `CLAUDE_CONFIG_DIR` point into the run's own folder. With `CLAUDE_CONFIG_DIR` set, every `~/.claude` path lives there, and "The same applies to `.claude.json`" [24], which `--setting-sources` alone cannot keep out [25] | yes: the pilot checks that a run works there and that nothing new appears in your home folder |
| A skill's history from an earlier run | the same home folder per run, where `taste-skill` [18] and huashu-design [22] keep their history | as above |
| Your login, which now sits outside the run's configuration | `claude setup-token` makes a one-year token that "authenticates with your Claude subscription"; it "can only make model requests" [12]. The runner passes it as `CLAUDE_CODE_OAUTH_TOKEN` | as above |
| Any settings but the run's own project settings | `--setting-sources project` [11] | nothing |
| MCP servers from any configuration, claude.ai connectors among them | `--strict-mcp-config` [11]; the token cannot fetch connectors either [12] | nothing |
| Bundled skills, most of which are in every session [15], and auto memory | `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS=1` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` [26] | nothing |
| A newer Claude Code halfway through the bench | Claude Code "checks for updates on startup and periodically while running", and an update takes effect "the next time you start Claude Code" [50]. `DISABLE_AUTOUPDATER=1` stops only the background update of the process that has it [26], so the docs put it in the `env` of your `settings.json` [50]: set it there for as long as the bench runs. The runner checks `claude --version` against the version `bench.json` records before each run and stops on a mismatch; the count also stops when valid runs differ in version (section 6). On a mismatch, put the recorded version back with `claude install <version>` on a native installation, which `DISABLE_AUTOUPDATER` leaves working [50], and start the runner again; deleting the runs and starting a new count is the last resort | nothing |

What it cannot keep out: managed policy settings, which are read whatever the setting sources
[25]; your plan's allowance, which the bench shares with your own work [4]; and the fact that
every arm's code runs as you, on your machine (section 8). A skill that loads in the no-skill run
although none was copied in comes from what the bench cannot keep out: the pilot records such
skills in each run's record instead of stopping, and `skillsInEveryRun` in `bench.json` then names
them (section 4).

- **Keep usage credits off while the bench runs.** Usage credits are extra usage you buy with
  `/usage-credits`; without them, Claude Code "blocks further requests until the reset time" [4],
  so the plan's limit pauses the bench and nothing is billed. Look at `/usage` in a session signed
  in with `/login` before the first run: it "shows a usage-credits row while usage credits are on"
  [51], so no such row means they are off.

Check: after the pilot, does `ls -a ~` show a folder an arm writes, such as `.taste-skill`,
`.impeccable` or `.huashu-design`, that was not there before?

## 4. Running each arm headless

**The call.** Every run is one `claude -p` call in a fresh folder, with the same flags and
variables, read at 2.1.312. All of them are set on every run; none is optional.

| Flag or variable | What it does | Why the bench sets it |
|---|---|---|
| `-p "<prompt>"` | runs one prompt with no interactive session [23] | the bench runs unattended |
| `--model claude-opus-5-5`, `--effort high` | the model by its full name, and the effort [11] | one model and one effort for every arm ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 15); an alias such as `opus` can move to a new model halfway through the bench |
| `--setting-sources project` | loads only the run's project settings [11] | the trace hook below lives there, and nothing else should load |
| `--strict-mcp-config` | uses only the MCP servers given with `--mcp-config`, here none [11] | no MCP server reaches a run |
| `--permission-mode acceptEdits`, `--allowedTools "Read,Write,Edit,Bash,Skill"` | file edits and the listed tools run without asking [11] | the same tools for every arm; add a tool only when the pilot shows an arm was denied one, and then for every arm |
| `--permission-prompts none` | denies what would wait for a person, the question tool included; needs 2.1.259 or later [11] | nobody answers a run |
| `--max-budget-usd 25` | stops a run at Claude Code's "client-side cost estimate" [11] | a guard against a runaway run; it is not a charge on a subscription |
| `--output-format stream-json --verbose` | one JSON event per line [23] | the runner reads the init and result events from it |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` | removes background runs from the Bash tool [26] | a `-p` run waits for a background command, such as a dev server, "until the command exits or reaches its time limit" [23] |
| `CLAUDE_CODE_RETRY_WATCHDOG=1` | a session "that hits a usage limit waits out the remaining window" [26] | an unattended bench pauses at the plan's session limit instead of failing; the time of a run then includes the wait. A weekly limit outlasts the run's timeout (below) |

`--max-turns` is in the CLI reference [11] but not in `claude --help` at 2.1.312, so the bench caps
a run by its budget and by a wall-clock timeout of its own. A run the timeout stops with SIGTERM
exits with code 143 and "records no result" [23], so it fails, unless the plan's limit stopped it
(below).

**The prompt.** One text for every arm. It states the goal and the steps, carries the brief inside
a `<brief>` tag, and gives the model a way out it can check: where the brief leaves a choice open,
decide it and state the reading in one line
([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) sections 2,
5 and 8). An arm's run starts with `/<skill-name>`; the no-skill run is the same text without it.

- **Call the skill by name;** [choosing-tools-and-skills.md](choosing-tools-and-skills.md)
  section 5 owns the rule. Headless runs are where the sources disagree: Hallmark's author states
  that skills "do not auto-trigger in `claude -p`, so we invoke by name", with no numbers [27],
  while Scott Spence saw a skill called in 55% of 22 headless prompts on Sonnet 4.5 [29]. The two
  differ by model and method; naming the skill makes "the arm's skill ran" part of the setup
  instead of a choice the model makes.
- **Tell an arm that asks a person to choose.** The prompt says: "If your instructions offer a
  person several directions to pick from, pick the one you recommend and go on." Impeccable asks
  through the question tool for new work [19], and huashu-design waits for a pick unless told to
  skip [22]. *Not yet tried*: whether both go on after that sentence.

**Finished or failed.** A run is valid when all three hold:

1. the stream's `result` event has `subtype` `success` and `is_error` false [30], [31]; a run with
   no result event, killed or crashed, fails;
2. the arm's skill ran (below);
3. the page exists at `site/index.html`.

Exit code 0 means success and a non-zero code a failure [23], but the result event says more: its
error subtypes, such as `error_max_budget_usd` and `error_during_execution`, name the kind of
failure, and it carries the run's time, turns, cost estimate, tokens and `permission_denials` [30],
which the runner keeps.

**Stopped by the plan's limit.** A run that did not finish and whose stream holds a
`rate_limit_event` with `status` `rejected` [30] is recorded as `limit`, not as a failure: the plan
stopped it, not the arm. It gets no second attempt, it does not count toward the stop after three
failed runs in a row, and the runner runs it again when you start it after the limit resets.

**Exactly one skill.** The stream's `system/init` event lists the run's `skills`, `plugins` and
`mcp_servers`, with its `model` and `claude_code_version` [30]. It omits the effort from the init
message a script reads [30], so the runner records the effort it passed. The runner stops the
whole bench, not only the run, when `skills` holds anything but the arm's skill and the names the
pilot found in the no-skill run, or when a plugin or an MCP server loaded: that is a broken setup,
not a failure of the arm. `--disable-slash-commands` is no way to keep other skills out: it disables
"all skills and commands for this session" [11], the arm's skill included.

**Whether the skill ran.** A typed `/name` does not go through the `Skill` tool;
`UserPromptExpansion` "fires on that direct path" [32]. The runner puts a hook on that event into
each run's project settings, which a `-p` run loads with no trust dialog [32]. The hook is written
in exec form, which runs "with no shell involved" [32], so its file path needs no quoting, and it
prints nothing, since Claude reads what such a hook prints as context [32]. A skill the model calls
itself shows as a `Skill` tool call in the stream. How the stream shows a typed `/name` is not
documented; the pilot shows it.

**The order.** The runner draws a random order once and writes it to `plan.json`, so a bench that
stops picks up where it stopped. Runs go one at a time, since they share one plan allowance.

**The pilot.** Before the full bench, run every arm once on the first brief. It settles, for your
machine and your version, the items below, and each says what to do when it fails:

1. that a run works on the token, in its own home and configuration folder. **When it fails:** if
   the runner stops at once and asks for the token, the session of section 1 did not hand it on:
   run the pilot and the bench in a plain terminal that stays open instead. If the runs fail on the
   token, take the fallback of section 11, your own login with the flags only. The runner has no
   switch for it: change `main` and `childEnvironment` in `run-arms.mjs` by hand, and record the
   change in `results.md`.
2. what the no-skill run's `skills` list holds: write it into `bench.json` as `skillsInEveryRun`.
   **When it holds a skill:** nothing fails; the skill comes from what the bench cannot keep out
   (section 3), and the list lets the full bench accept it.
3. that each arm's run loads its skill, and that the hook logs the typed `/name` with the whole
   prompt in `command_args`. **When it fails:** do not start the full bench, since every skill arm
   would fail as "the arm's skill did not run". Read how the run's stream shows the typed `/name`,
   match `skillRan` in `run-arms.mjs` to it, and run the pilot again.
4. that Impeccable and huashu-design build a page with nobody answering. **When it fails:**
   huashu-design, which is optional, leaves `arms.json` before the full bench; Impeccable stays,
   and its runs that end without a page count as failed runs (section 2), with the limit section
   10 names.
5. which tools an arm was denied (`permissionDenials` in its record). **When one was:** add it to
   `ALLOWED_TOOLS` for every arm, or for none, and run the pilot again.
6. that no arm wrote to your home folder, that Hallmark found `puppeteer-core`, and that
   `taste-skill` found your Chrome. **When it fails:** an arm that wrote to your home folder leaves
   the bench, or the whole bench moves into a container (section 8); a missing browser or
   `puppeteer-core` is a setup problem: fix it (section 3) and run the pilot again.
7. how long a run of each arm takes and what it costs by the estimate, against the timeout and the
   budget cap. **When a run goes past either:** raise `RUN_TIMEOUT_MS` or `BUDGET_CAP_USD` in
   `run-arms.mjs`, the same for every arm, and run the pilot again.

If you will also judge, open nothing under `pilot-runs/` yourself: its pages and streams carry
each arm's name, and a page seen next to its arm's name before the pick is no longer blind. Let a
Claude Code session read the pilot's records and report each item of the list above as pass or
fail. Then take the pilot's pages through the blind copy, the screenshots and the contrast check
(sections 5 and 6), to see the whole path work, and delete `judging/`, `key/` and `checks/` before
the full bench; if you will also judge, only check that the shots render.

How long the full bench takes. The runs asked are arms × the briefs you wrote × `runsPerArm`:
eight arms, three briefs and two runs make 48. Sum the pilot's time for each arm, times the runs
asked of that arm, and you have the bench's time before any wait at a limit. Add a person's time
for the contrast look of [blind-test-example.md](blind-test-example.md) step 10: one look for each
element the check could not decide, on every page it lists. The slowest arm takes
"roughly 30 to 45 minutes and a few hundred thousand tokens" a build [3]. Read `/usage` in a
session signed in with `/login` before and after the pilot: the share of the plan's limits the
pilot used, times the runs asked over the pilot's runs, says how many limit windows the bench
needs. Every run is on Opus, and the plan has
an Opus limit beside its session and weekly limits [4]. Plan for days, or weeks on a smaller plan.

## 5. Screenshots and the contrast floor

A plain Node script does both, with Playwright 1.64.1 and @axe-core/playwright 4.14.0; no test
runner is needed [33], [34].

- **Serve every page the same way:** from one local server that answers only on `127.0.0.1`, and
  from the blind copies the judges will see (section 6).
- **Wait for `load`, not `networkidle`,** which Playwright marks "DISCOURAGED" [35].
- **Scroll once down the page and back to the top,** to wake lazy images and scroll reveals.
- **Wait for images and fonts yourself.** In Playwright's code at 1.64.1, a screenshot waits for
  `document.fonts.ready` [36], which its docs do not promise, and nothing waits for images. The
  script waits for both, with a cap for an image that never loads.
- **Stop CSS motion, and wait out the rest.** `animations: "disabled"` "stops CSS animations, CSS
  transitions and Web Animations" [35]; motion a page drives from its own scripts goes on. The
  script waits a fixed time before each shot. Playwright discourages fixed waits [37], but no
  signal says when a page's own scripts stop moving. *Not yet tried*: whether 1.5 seconds is
  enough.
- **Two widths, the first screen only.** A 1280 × 800 desktop, and Playwright's iPhone 13
  descriptor, which brings the viewport, the scale, touch and the mobile mode [38]. The pick is on
  the first screen, so `fullPage` stays off; `scale: "css"` keeps one image pixel per CSS pixel
  [35].
- **File names carry the random id only.** Hallmark's own screenshot script names its files by
  brief and arm [27], which suits its author and breaks a blind pick.
- **No `reducedMotion: "reduce"` for the shots.** It would show every page's reduced-motion path,
  not the page most visitors see, and favour the arms that use no motion.

**The contrast floor.** axe's `color-contrast` check holds text to 4.5:1 and large text to 3:1
[39], the text rows of [visual-design.md](visual-design.md) section 4.

- Run axe with that rule only, `withRules(["color-contrast"])` [34], at both widths, before the
  pick.
- axe decides only text inside the viewport: text outside it, and text over an image, comes back
  as `incomplete` [39], which axe calls "needs review" [40]. So the script reads the page one screen
  at a time and keeps, for each element, the strongest answer any screen gave: a failure on any
  screen fails the element. *Not yet tried*: this is the bench's own method.
- A page with a failure at either width leaves the pick. A page with an element no screen decided
  gets a person's look at its blind shots, `pass` or `fail`, before the sheets are made: automated
  tests find some problems, and "many accessibility problems can only be discovered through manual
  testing" [33]. [accessibility.md](accessibility.md) sections 10 and 11 own those checks for an
  application; here only the contrast floor is checked, because only it decides whether a page
  enters the pick.
- Before it judges any arm's page, the script runs the check on a control page known to fail and
  one known to pass, and stops when it gets either wrong: a gate that passes everything looks like
  one that works ([evals.md](../../python/evals/evals.md) section 5).

Check: in the script's run, did the contrast check fail its failing control page?

## 6. The blind pick

- **Copy each valid page under a random id,** and take out what a judge could tell an arm by
  without looking at the design: the tab title, HTML comments, a generator tag, and comments in
  CSS, where an arm may stamp itself: a contributor to Hallmark reported gate failures on 11 of
  its 18 example pages, "all of whose CSS stamps claim `gates: all-pass`" [41]. Text a visitor sees
  stays as it is. Symbolic links are dropped (section 8).
- **Keep the key apart.** The file that maps ids to arms sits outside the folder the judges get,
  and the file that lists each set's pages names ids only.
- **One sheet per judge per set,** with the pages in an order shuffled for that judge, the brief's
  purpose at the top, and a plain question: "Which page would you put live for this brief, as it
  is?" No praise words. At Anthropic, criteria for a model evaluator that said "the best designs
  are museum quality" "pushed designs toward a particular visual convergence" [42]; that was a
  model, and no source read for this file tested wording on people.
- **People judge, not the builder and not a model.** In the same case, agents "reliably skew
  positive when grading their own work" [42], and the one test of skills against no skill had a
  model as its only judge [1].
- **The person who ran the bench** may judge, as long as they opened nothing under `runs/` or
  `pilot-runs/`, and not the key: a page seen next to its arm's name before the pick is
  no longer blind. When that person is the only judge, set `judges` in `bench.json` to their one
  placeholder name.
- **Picks first, then scroll notes.** Each judge writes one id per set. Then each judge opens every
  page from the local server, scrolls it, and writes a note on scroll and motion; the picks do not
  change after that.
- **Count against what was asked.** Before any count, check that every judge has one pick per set,
  each naming a page of that set; the rule is [evals.md](../../python/evals/evals.md) section 6's.
  Then count wins per arm per brief against judges × runs per arm, with each arm's valid runs,
  contrast exits and failed runs beside them. The count also stops when valid runs differ in
  model or Claude Code version.

Check: was the key opened before every judge's picks were in? If so, whoever opened it does not
judge.

## 7. Reading the result, and building a skill of your own

**The decision rule, written down before the first run:** an arm beats no skill when its wins,
summed over briefs and judges, are more than the no-skill arm's. Writing it before the run keeps the
result from bending it, as [evals.md](../../python/evals/evals.md) section 7 asks of any comparison.

- **When no arm beats no skill,** no skill is built. Record the result in the bench's `results.md`
  (below), and [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 4 stays as it
  is: the spec first, and no skill as a default.
- **When an arm beats no skill,** install it or build from what the winners share, as the bullets
  below say, and record the result in the bench's `results.md`.
- **One judge gives a lead.** With one judge, one pick can turn "beats no skill" from no to yes, so
  a second judge's picks settle the result before a skill is installed or built.
- **The numbers are small.** With three judges, three briefs and two runs, the bench asks for 18
  picks, shared among seven or eight arms, and a lead of one or two wins can be chance. No source
  read for this file sizes a pick of this kind; [repeated-runs.md](../../python/evals/repeated-runs.md)
  section 7 sizes comparisons of pass rates, which is a different count. Report the counts, and no
  verdict stronger than they carry.
- **A win shows a bundle.** The arms differ in several mechanisms at once, so one arm's win does
  not show which part made it. Build from the mechanisms that several winners share.
- **What the pick can show:** the direction step, the direction file, the list of defaults to
  avoid, the checks, and the choice of fonts; the scroll notes add motion and the build order.
  **What it cannot show:** the image sources, since every arm gets the same photos; the font
  licence, a legal floor kept whatever the test shows; and where the rules sit in `SKILL.md`, since
  no arm varies it.

The parts a skill of your own is built from, each kept only when the test supports it.
[brand-pages.md](brand-pages.md) owns how each part is done:

- a direction step that deals or builds several directions and lets a person pick one
  ([brand-pages.md](brand-pages.md) section 3);
- the defaults to avoid, each with its replacement (section 4);
- real copy, photos and fonts, with their sources and licences (section 5);
- the hero first, then one section at a time (section 6);
- render checks by a reviewer in a fresh context, with a cap on rounds (section 7).

**Where the skill keeps its rules** follows [brand-pages.md](brand-pages.md) section 8: the rules
that must always hold at the top of `SKILL.md`, and every other file behind a pointer from it.

- **The new skill is one more arm** in a rerun of the whole bench, with new runs of every arm. It
  ships when it beats no skill and wins or ties the best skill arm. When it loses, revise it once
  and rerun; when it loses again, nothing ships, and that bench's `results.md` records it.
- **Install the winner, or build:** the test decides. When the best arm beats the new skill,
  recommend that arm instead ([choosing-tools-and-skills.md](choosing-tools-and-skills.md)
  section 8).
- **The skill's home:** your project's `.claude/skills/<name>/` (section 3), with a `README.md`
  that says when to use the skill and when not.

**Your result.** Once the count is done, paste the two tables `count-wins.mjs` prints into the
bench's `results.md` ([blind-test-example.md](blind-test-example.md), "The results table"), with
the date of the count and the number of judges. `results.md` is the one record of the result; this
file holds none. Not run yet.

Then update the lines in your copies that say no test with human raters exists;
`grep -rn -i -E 'human raters|rated by people|people rated|no published test' docs/engineering/react/design/`
lists them. It also prints its own two lines in this section, which stay as they are. Add the
result to the "What to expect" cell of each tested arm in
[choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 8.

## 8. Security: every arm runs third-party code

Every run gets the `Bash` tool for any command, so an arm's instructions can run anything you can,
on your machine, with your files in reach. What each skill runs is
[choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 6.

- **Read each arm's scripts at the commit you pin, before its first run,** the way
  [designing-with-claude-code.md](designing-with-claude-code.md) section 7 reviews a plugin or a
  skill. A later commit is new code: read it again before you move the pin.
- **Hooks arrive with skills too.** A project skill's frontmatter hooks register when the skill is
  invoked, "including in a `-p` run in a folder you haven't trusted" [32], and hooks in a project's
  `.claude/settings.json` run in `-p` with no trust dialog [32]. The runner writes each run's
  project settings itself and copies only the skill folder; a hook an arm writes into
  `.claude/settings.local.json` during a run does not load, since the runs load project settings
  only [11].
- **`disableSkillShellExecution` stays off.** Since 2.1.91 it replaces a skill's inline `!`
  commands with a note instead of running them, and "Bundled and managed skills are not affected"
  [15], [43]. It would change how an arm works, and it does not cover what the model runs itself,
  or a hook: Datadog's researchers note that "not all prompt injections need to invoke dynamic
  context" [44]. The bench tests each arm as its owner ships it; isolation comes from the next
  point.
- **For code you do not trust, run the bench in a container.**
  [agent-containers.md](../../any-language/docker/agent-containers.md) sections 3 to 5 say how to
  choose the isolation, which credentials go in, and how the network is limited. The login goes in
  as the token, and the container mounts no `~/.claude`. *Not yet tried* with this bench.
- **Every arm's code can read the token** from its environment. The token "can only make model
  requests" [12]. The runner passes it to each run and writes it to no file; keep it out of every
  file and log, and remove it from your shell when the bench ends.
- **Treat every run folder as untrusted.** Never open one in an interactive Claude Code session,
  an editor or a git tool: an arm may have left settings or hooks there, as
  [agent-containers.md](../../any-language/docker/agent-containers.md) section 7 says of a clone
  an agent ran in.
- **The page server answers only on `127.0.0.1`,** and the blind copies drop symbolic links, so a
  page cannot reach a file elsewhere on your machine through the server.
- **Copy and personal data.** Use invented or published copy only. A client's unpublished copy would
  go to every arm's code and to the services those scripts call, such as the catalog Impeccable
  fetches its directions from [17]. Name the judges by placeholders, such as `judge-a`; their notes
  need no personal data.

## 9. Common mistakes

| Mistake | What it costs | The fix |
|---|---|---|
| A plain request for a page, with the skill expected to load by itself | the arm runs as no skill: Hallmark activated in 0 of 12 such requests on Haiku 4.5 [28] | call the skill by name, and check the trace (section 4) |
| `--bare` for a clean run | "bare mode doesn't use your subscription login" [23], so it needs an API key | the switches of section 3 |
| An `ANTHROPIC_API_KEY` left in the shell | in `-p` "the key is always used when present" [12]: the bench runs on API billing | pass on only the listed variables |
| `--disable-slash-commands` to keep other skills out | it disables every skill, the arm's own included [11] | the bundled-skills switch and the init check |
| Waiting for `networkidle` before a shot | Playwright marks it "DISCOURAGED" [35] | `load`, then the waits of section 5 |
| Reading axe's `incomplete` as a pass | text over a photo is never checked [39] | a person's look before the pick |
| Screenshots named by arm, as in Hallmark's own eval [27] | every judge who sees a file name knows the arm | random ids, and the key outside the judges' folder |
| A skill's history carried from run to run | the runs of one arm are not independent: `taste-skill`'s script steers away from its own recent picks [18] | a home folder per run |
| A run the plan's limit stopped, counted as the arm's failure | the arm looks worse for the plan's limit, and three such runs stop the bench | record it as `limit`, and run it again after the reset (section 4) |
| Wins divided by the pages that came back | an arm that often fails looks better than it is ([evals.md](../../python/evals/evals.md) section 6) | divide by the picks asked for |
| One brief, of a pattern every skill handles | it shows nothing: "a pricing page proves nothing" [2] | three to five briefs of different kinds |
| A model as the judge | the question is what people prefer, and the one test of skills against no skill had only a model judge [1] | people, blind |

## 10. Where it stops holding

- **A house look gives an arm away.** A judge who knows `taste-skill-classics` or `ui-ux-pro-max`
  may recognise its page. The bench cannot remove that; report it as a limit of the result.
- **Visible text stays.** A credit line or a footer an arm writes can name it during the scroll
  notes; the stills show only the first screen.
- **Arms built around a person's choice,** Impeccable and huashu-design, run here in a mode their
  owners did not design for, so their result says less about how they work with a person.
- **Motion is judged only from notes,** and motion a page drives from its scripts is not frozen in
  the stills.
- **A result holds for the commits tested.** `taste-skill` shipped seven releases between 13 and
  25 October 2026 [45]; a new commit is a new arm.
- **The result is about your briefs and your judges:** which arm these judges preferred, on these
  briefs.
- **How alike AI-built sites are** has no measurement read for this file; Ying et al. show a
  figure on the style diversity of web-design skills whose values were not read [1].

## 11. Alternatives considered

- **`--bare`.** The headless docs call it "the recommended mode for scripted and SDK calls", and
  say it "will become the default for `-p` in a future release" [23]. It needs an API key, so it is
  out. Because it may become the default, the runner names every flag, and the bench reads the
  headless page again when Claude Code changes.
- **`--safe-mode`.** Since 2.1.169 it keeps the login and starts Claude Code "with all
  customizations (CLAUDE.md, plugins, skills, hooks, MCP servers) disabled" [43]: the arm's skill
  too. A clean baseline, but no arm can run under it.
- **Your own login, with the flags only** and no home or configuration folder of the run's own.
  Documented and simpler, but `~/.claude.json` is read whatever the setting sources [25], and an
  arm's history in your home folder carries from run to run. It is the fallback if the pilot fails
  on the token: then drop huashu-design, whose history has no other place, and set
  `TASTE_SKILL_HISTORY` to a file in each run's folder [18].
- **A separate `CLAUDE_CONFIG_DIR` with its own `/login`.** On macOS, a login made there is a
  keychain entry for that folder [12], so a configuration folder per run would need a login per
  run. The token avoids that.
- **Each arm's own installer** (`/plugin install`, `npx skills add -g`, `./install.sh`). Closer to
  each owner's method, but the arms then differ in how they install, some write to your home
  folder, and a plugin can update itself [16]. `--plugin-dir` loads a plugin "for that session
  only" [46], with its hooks and servers; it is the way to test a whole plugin, not tried here.
- **`claude plugin eval`.** It runs isolated, scored `claude -p` runs in which "Nothing personal or
  project-level loads", with a run without the plugin as a baseline [47]. Its graders read text,
  files and tool calls, or ask a model [47]; none takes a screenshot or runs a blind pick. At most a
  cross-check that a skill loaded.
- **Hallmark's `eval/` as it is.** Its Claude Code runner sets a sound base, which the bench keeps:
  project-only settings, strict MCP, stream-json and caps. It is not blind: its screenshot script
  names files by brief and arm, and its judge is a model; its other tier calls model APIs with
  other vendors' keys [27].
- **A model as the judge,** as Ying et al. [1] and Hallmark's eval [27] use. Cheaper and
  repeatable, but the question is what people prefer, and no model judge here was checked against
  people's picks.
- **A tall viewport for the contrast check,** instead of one screen at a time: simpler, but a hero
  sized by the viewport's height grows with it and pushes the rest of the page out again.
- **`reducedMotion: "reduce"` for still pages:** stable shots, of a path most visitors never see,
  which favours the arms that use no motion.
- **A strict pointer such as "you must read" in `SKILL.md`.** Not required: the one test found that
  any pointer works [6], so the rule asks for a pointer of any style.
- **Copying the winners' parts into a skill before the test.** Then taste chooses the parts, not
  the pick.
- **`--max-turns`.** It is in the CLI reference [11] but not in `claude --help` at 2.1.312; the
  budget cap and the timeout do the same job without that doubt.
- **No retry watchdog.** A run would end with an error at the limit and wait as `limit` for a
  rerun after the reset (section 4). The watchdog waits out the
  window instead [26], at the cost of runs whose time includes the wait.
- **`--json-schema` for a closing answer.** It would give a typed final message, but the bench's
  answer is the page on disk, and a schema adds a failure, `error_max_structured_output_retries`
  [30], that has nothing to do with the page.

## 12. Review checklist

- Do the runs' own records show one model, one effort and one Claude Code version?
- Is every arm pinned to a commit, copied the same way, and its code read at that commit?
- Does no run's `system/init` list a skill, a plugin or an MCP server beyond what section 4 allows?
- Did the pilot settle each *not yet tried* step of sections 3 to 5, and does the results file say
  how?
- Did the contrast check fail its failing control page, and did a person look at every page it
  could not decide?
- Did the judges see only random ids, in an order shuffled per judge, with the key closed until the
  picks were in?
- Are the wins divided by the picks asked for, with failed runs and contrast exits beside them?
- Was the decision rule of section 7 written down before the first run?

## 13. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Jiahao Ying, Boxian Ai, Wei Tang, Siyuan Liu, Yixin Cao — OpenSkillEval: Automatically Auditing the Open Skill Ecosystem for LLM Agents (arXiv:2605.23657, 2026; research) — https://arxiv.org/abs/2605.23657
- [2] Superdesign — Design skills reviewed (Superdesign blog, 2026; case, by a vendor of a competing design agent) — https://superdesign.dev/blog/design-skills-reviewed
- [3] Leonxlnx — taste-skill, README.md, commit 12af471 — https://github.com/Leonxlnx/taste-skill/blob/12af471f627f866411b4bd785b19646d3672784c/README.md
- [4] Anthropic — Claude Code docs: Errors, usage limits — https://code.claude.com/docs/en/errors
- [5] garrytan — gstack, docs/hosts.md, commit 81a8272 — https://github.com/garrytan/gstack/blob/81a82727b38590c90b34f4c326af021f31d9774f/docs/hosts.md
- [6] rulestack — 13 of 16 Claude Code runs loaded the skill script (DEV Community, 2026; research) — https://dev.to/rulestack/13-of-16-claude-code-runs-loaded-the-skill-script-the-docs-call-executed-not-loaded-5cic
- [7] Anthropic — anthropics/skills, skills/frontend-design/SKILL.md, commit 41bbe19 — https://github.com/anthropics/skills/blob/41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f/skills/frontend-design/SKILL.md
- [8] Yan Li et al. — MM-WebAgent: A Hierarchical Multimodal Web Agent for Webpage Generation (arXiv:2604.15309, 2026; research) — https://arxiv.org/abs/2604.15309
- [9] Yuchi Wang et al. — RefCraft: Benchmarking Visual-Reference-Conditioned Agentic Generation through Web Development (arXiv:2610.26826, 2026; research) — https://arxiv.org/abs/2610.26826
- [10] Anthropic — Claude Code docs: Memory — https://code.claude.com/docs/en/memory
- [11] Anthropic — Claude Code docs: CLI reference — https://code.claude.com/docs/en/cli-reference
- [12] Anthropic — Claude Code docs: Authentication — https://code.claude.com/docs/en/authentication
- [13] Nutlope — hallmark, README.md, commit 8f6969f — https://github.com/Nutlope/hallmark/blob/8f6969f8922caabde9de1784959eae11ddf68073/README.md
- [14] Microsoft — Playwright docs: Browsers, v1.64.1 — https://github.com/microsoft/playwright/blob/v1.64.1/docs/src/browsers.md
- [15] Anthropic — Claude Code docs: Skills — https://code.claude.com/docs/en/skills
- [16] Anthropic — Claude Code docs: Install and manage plugins — https://code.claude.com/docs/en/plugins/install
- [17] Paul Bakaus — Impeccable, README.md, commit 5e745ac — https://github.com/pbakaus/impeccable/blob/5e745ace7e151feb2a93d360d0281fe39448b857/README.md
- [18] Leonxlnx — taste-skill, skills/taste-skill/scripts/draw.mjs, commit 12af471 — https://github.com/Leonxlnx/taste-skill/blob/12af471f627f866411b4bd785b19646d3672784c/skills/taste-skill/scripts/draw.mjs
- [19] Paul Bakaus — Impeccable, reference/new-work.md, commit 5e745ac — https://github.com/pbakaus/impeccable/blob/5e745ace7e151feb2a93d360d0281fe39448b857/.claude/skills/impeccable/reference/new-work.md
- [20] nextlevelbuilder — ui-ux-pro-max-skill, README.md and .claude/skills/ui-ux-pro-max/SKILL.md, commit 28b3b8d — https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/28b3b8dee8c976df4fa3e94aed4e092ad43fcb03
- [21] Leonxlnx — taste-skill-classics, README.md, commit 5e08c93 — https://github.com/Leonxlnx/taste-skill-classics/blob/5e08c9383dc4ad7fc0df70e1ac8cfa09ec356305/README.md
- [22] alchaincyf — huashu-design, SKILL.md and README.en.md, commit 4fc7bfd — https://github.com/alchaincyf/huashu-design/tree/4fc7bfdbd5ec3fa2d43ce7a6433de60976a5e4b1
- [23] Anthropic — Claude Code docs: Run Claude Code programmatically — https://code.claude.com/docs/en/headless
- [24] Anthropic — Claude Code docs: The .claude directory — https://code.claude.com/docs/en/claude-directory
- [25] Anthropic — Claude Code docs: Agent SDK, Use Claude Code features — https://code.claude.com/docs/en/agent-sdk/claude-code-features
- [26] Anthropic — Claude Code docs: Environment variables — https://code.claude.com/docs/en/env-vars
- [27] Nutlope — hallmark, eval/ (README.md, gen-cli.mjs, screenshot.mjs, judge.py), commit 8f6969f — https://github.com/Nutlope/hallmark/tree/8f6969f8922caabde9de1784959eae11ddf68073/eval
- [28] ktlesr — skill-trigger-measurements: hallmark ablation (GitHub, 2026; research) — https://github.com/ktlesr/skill-trigger-measurements
- [29] Scott Spence — Measuring Claude Code Skill Activation With Sandboxed Evals (scottspence.com, 2026; research) — https://scottspence.com/posts/measuring-claude-code-skill-activation-with-sandboxed-evals
- [30] Anthropic — Claude Code docs: Agent SDK reference, TypeScript — https://code.claude.com/docs/en/agent-sdk/typescript
- [31] Anthropic — Claude Code docs: Agent SDK, How the agent loop works — https://code.claude.com/docs/en/agent-sdk/agent-loop
- [32] Anthropic — Claude Code docs: Hooks reference — https://code.claude.com/docs/en/hooks
- [33] Microsoft — Playwright docs: Accessibility testing, v1.64.1 — https://github.com/microsoft/playwright/blob/v1.64.1/docs/src/accessibility-testing-js.md
- [34] Deque — @axe-core/playwright, README.md, 4.14.0 — https://github.com/dequelabs/axe-core-npm/blob/develop/packages/playwright/README.md
- [35] Microsoft — Playwright API docs: parameters (params.md), v1.64.1 — https://github.com/microsoft/playwright/blob/v1.64.1/docs/src/api/params.md
- [36] Microsoft — Playwright source: screenshotter.ts, v1.64.1 — https://github.com/microsoft/playwright/blob/v1.64.1/packages/playwright-core/src/server/screenshotter.ts
- [37] Microsoft — Playwright API docs: class Page (class-page.md), v1.64.1 — https://github.com/microsoft/playwright/blob/v1.64.1/docs/src/api/class-page.md
- [38] Microsoft — Playwright docs: Emulation, v1.64.1 — https://github.com/microsoft/playwright/blob/v1.64.1/docs/src/emulation.md
- [39] Deque — axe-core, lib/checks/color/color-contrast.json, 4.14.0 — https://github.com/dequelabs/axe-core/blob/develop/lib/checks/color/color-contrast.json
- [40] Deque — axe-core, doc/API.md, 4.14.0 — https://github.com/dequelabs/axe-core/blob/develop/doc/API.md
- [41] A contributor to Nutlope/hallmark — Pull request #60 (GitHub, 2026; case) — https://github.com/Nutlope/hallmark/pull/60
- [42] Prithvi Rajasekaran — Harness design for long-running apps (Anthropic Engineering, 2026; case, by the model's vendor) — https://www.anthropic.com/engineering/harness-design-long-running-apps
- [43] Anthropic — Claude Code docs: Changelog, to 2.1.312 — https://code.claude.com/docs/en/changelog
- [44] Datadog Security Labs — Malicious Coding Agent Skills and the Risk of Dynamic Context (Datadog Security Labs, 2026; research, sponsored by Datadog) — https://securitylabs.datadoghq.com/articles/malicious-skills-supply-chain-risks-in-coding-agents-with-dynamic-context/
- [45] Leonxlnx — taste-skill, CHANGELOG.md, commit 12af471 — https://github.com/Leonxlnx/taste-skill/blob/12af471f627f866411b4bd785b19646d3672784c/CHANGELOG.md
- [46] Anthropic — Claude Code docs: Plugin loading reference — https://code.claude.com/docs/en/plugins/loading
- [47] Anthropic — Claude Code docs: Test plugins with evals — https://code.claude.com/docs/en/plugin-evals
- [48] Anthropic — Claude Code docs: Interactive mode — https://code.claude.com/docs/en/interactive-mode
- [49] Anthropic — Claude Code docs: Tools reference — https://code.claude.com/docs/en/tools-reference
- [50] Anthropic — Claude Code docs: Advanced setup — https://code.claude.com/docs/en/setup
- [51] Anthropic — Claude Code docs: Manage costs effectively — https://code.claude.com/docs/en/costs
- [52] Apple — tmp_cleaner(8) and the script it describes, `/usr/libexec/tmp_cleaner` (`daily_clean_tmps_days="3"`), macOS 15.7.7; read on the system, with no web copy
