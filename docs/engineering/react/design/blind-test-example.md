# Blind test bench: a worked example

**Not run yet.** These files are a template for a test nobody has run. A person copies them into a
scratch project and runs them later, from a Claude Code session started in a terminal of their
own, with Claude Code running every arm, by [skill-blind-test.md](skill-blind-test.md). Every version here was read on 2026-10-29:
Claude Code 2.1.312, Playwright 1.64.1, @axe-core/playwright 4.14.0, and each arm at the commit `arms.json`
names. A line marked *not yet tried* rests on behaviour no owner documents, and the pilot run
settles it. No script here has run, apart from a syntax check with `node --check`. The businesses,
copy and judges are invented.

**Navigation**

- [The layout](#the-layout)
- [Set it up and run it](#set-it-up-and-run-it)
- [The settings: bench.json](#the-settings-benchjson)
- [The briefs: briefs.json](#the-briefs-briefsjson)
- [The arms: arms.json](#the-arms-armsjson)
- [The runner](#the-runner)
- [The blind copies](#the-blind-copies)
- [The page server](#the-page-server)
- [Screenshots and contrast](#screenshots-and-contrast)
- [The judging sheets](#the-judging-sheets)
- [What the judges read](#what-the-judges-read)
- [The count](#the-count)
- [The results table](#the-results-table)

## The layout

```text
skill-bench/
├── bench.json                runs per arm, judges, the pilot's skill list, the server's port, the Claude Code version
├── briefs.json               the briefs: purpose, copy, photo files
├── arms.json                 each arm: repository, commit, skill folder, skill name
├── photos/<brief-id>/        the photos each brief names; you add them
├── arms-src/<arm>/           each arm's repository, cloned at its commit
├── run-arms.mjs              runs every brief, arm and run headless, in random order
├── blind-pages.mjs           copies each finished page under a random id; writes the key
├── serve-pages.mjs           serves the blind copies on 127.0.0.1
├── shoot-pages.mjs           takes the screenshots and checks contrast
├── make-sheets.mjs           writes one sheet per judge and set, and the empty picks files
├── count-wins.mjs            checks the picks and counts the wins against the key
├── judging-instructions.md   what each judge reads
├── results.md                the results record, empty until the bench runs
├── package.json              written by npm
├── package-lock.json         written by npm
│
├── runs/                     written by the runner: one folder per run; open no page there
├── pilot-runs/               the same, for the pilot
├── key/blind-key.json        which id is which arm; nobody opens it before the picks are in
├── checks/                   the contrast results and the sheet for a person's look
└── judging/                  the blind pages, the shots and the sheets: all the judges get
```

Why it is good: what the judges get (`judging/`), what only the count reads (`key/`) and what
holds every arm's name (`runs/`) are separate folders, so keeping the pick blind is a matter of
handing over one folder. Each script does one job and is named for it, with no `utils` file
([file-structure.md](../../any-language/file-structure/file-structure.md) section 7). The bench is
a tool of a few scripts, below the size where that practice's module folders pay
([file-structure.md](../../any-language/file-structure/file-structure.md) section 12), so the
scripts sit at the root. No script imports another: each stands alone, which is why two small
functions appear in two scripts.

## Set it up and run it

Each step says what it is for, then what to run. All commands run in the bench's folder, the one
step 0 makes, in a macOS or Linux shell.

Where each step runs: a Claude Code session may do steps 0 to 3 for you. Step 4 runs in a plain
terminal of your own, never through Claude Code's Bash tool or its `!` prefix: the command's output
enters the conversation, and with it the token ([skill-blind-test.md](skill-blind-test.md)
section 1). Then start `claude` in that same terminal, with the token exported there, and keep
that session open until the count. It does the steps after step 4 and reads the records for you,
and it runs steps 6 and 7 and step 9's server as background commands, which have no time limit in
a local session
([skill-blind-test.md](skill-blind-test.md) section 1). *Not yet tried*: whether those commands
get the exported token and keep running for days; the pilot settles it. If they do not, run steps
6 and 7 in a plain terminal that stays open, such as a `tmux` session, with the token exported
there, and step 9's server in a second terminal. Every arm still runs in Claude Code, as
`claude -p` on your plan.

0. **Make the folder.** Claude Code loads every `CLAUDE.md` above the folder it runs in, and project
   skills from the `.claude/` folders above it, so a file above the bench would reach every run
   ([skill-blind-test.md](skill-blind-test.md) section 3). Make the folder outside every repository
   and outside your home folder, and never under `/tmp`, which macOS empties of files untouched for
   more than three days while the bench runs for days. On macOS, `/Users/Shared/skill-bench` fits.
   Go into it, and run this check; it prints nothing when no such file or folder sits above it:

   ```sh
   d=$PWD; while [ "$d" != / ]; do ls -d "$d/CLAUDE.md" "$d/CLAUDE.local.md" "$d/.claude" 2>/dev/null; d=$(dirname "$d"); done
   ```

   An empty answer only counts once the check has found something: run it once in a folder that
   has a `CLAUDE.md`, and see it print that file.

1. **Save the files and check the tools.** Save each code block below under its file name in the
   folder of step 0: the six scripts, `bench.json`, `briefs.json`, `arms.json`,
   `judging-instructions.md` and `results.md`. Write at least three briefs with real copy into
   `briefs.json`, and set `judges` in `bench.json`: one placeholder name when one person judges
   alone. Then check the tools; success is Node 22 or later, Python 3, git, and a Claude Code
   version that you write into `bench.json` as `claudeCodeVersion`:

   ```sh
   node --version
   python3 --version
   git --version
   claude --version
   ```

   Then turn off auto-updates until the count is done, so the version stays the one you recorded
   ([skill-blind-test.md](skill-blind-test.md) section 3): set `DISABLE_AUTOUPDATER` to `"1"` in
   the `env` of `~/.claude/settings.json`. Success, on a native or npm installation:
   `claude doctor` shows the `Auto-updates` line as `disabled (set by env: DISABLE_AUTOUPDATER)`.
   A Homebrew, WinGet or Linux package installation does not update itself by default.

2. **Install the screenshot tools inside the bench.** Exact versions keep a rerun on the same code,
   and `PLAYWRIGHT_BROWSERS_PATH=0` puts Playwright's browser in `node_modules` instead of your
   user cache; the browser is a download of a few hundred megabytes. `puppeteer-core` is here
   because Hallmark's render checks ask for a global install; this keeps it in the bench (*not yet
   tried*). Record the version npm installs in `results.md`, since Hallmark's README names none.

   ```sh
   npm init -y
   npm install --save-exact playwright@1.64.1 @axe-core/playwright@4.14.0
   PLAYWRIGHT_BROWSERS_PATH=0 npx playwright install chromium
   npm install --save-exact puppeteer-core
   ```

   Success: `ls node_modules/playwright-core/.local-browsers` lists a `chromium` folder.

3. **Clone each arm at its commit.** The commit is the arm's version, and the runner refuses to
   start while a clone sits at another commit. Before the first run, read each arm's scripts at
   that commit ([skill-blind-test.md](skill-blind-test.md) section 8). huashu-design is optional:
   to leave it out, skip its two lines and remove its entry from `arms.json`.

   ```sh
   git clone https://github.com/anthropics/skills arms-src/frontend-design
   git -C arms-src/frontend-design checkout --quiet 41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f
   git clone https://github.com/Nutlope/hallmark arms-src/hallmark
   git -C arms-src/hallmark checkout --quiet 8f6969f8922caabde9de1784959eae11ddf68073
   git clone https://github.com/Leonxlnx/taste-skill arms-src/taste-skill
   git -C arms-src/taste-skill checkout --quiet 12af471f627f866411b4bd785b19646d3672784c
   git clone https://github.com/pbakaus/impeccable arms-src/impeccable
   git -C arms-src/impeccable checkout --quiet 5e745ace7e151feb2a93d360d0281fe39448b857
   git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill arms-src/ui-ux-pro-max
   git -C arms-src/ui-ux-pro-max checkout --quiet 28b3b8dee8c976df4fa3e94aed4e092ad43fcb03
   git clone https://github.com/Leonxlnx/taste-skill-classics arms-src/taste-skill-classics
   git -C arms-src/taste-skill-classics checkout --quiet 5e08c9383dc4ad7fc0df70e1ac8cfa09ec356305
   git clone https://github.com/alchaincyf/huashu-design arms-src/huashu-design
   git -C arms-src/huashu-design checkout --quiet 4fc7bfdbd5ec3fa2d43ce7a6433de60976a5e4b1
   ```

   Success: for each arm, `git -C arms-src/<arm> rev-parse HEAD` prints the commit `arms.json`
   gives it.

4. **Make the token, and hand it to this shell only.** Run this step in your own terminal, never in
   Claude Code (above). Each run gets a configuration folder of its own with no login in it, so
   your subscription reaches it as a token. `claude setup-token` opens the same browser sign-in as
   `/login` and prints the token. Run the `read` line, paste the token and press Enter: `read -rs`
   takes it without showing it and without writing it to your shell history. Then look at `/usage`
   in a normal session: usage credits must be off, so the plan's limit pauses the bench and nothing
   is billed ([skill-blind-test.md](skill-blind-test.md) section 3). Success: `/usage` shows no
   usage-credits row; if it shows one, turn usage credits off, which `/usage-credits` opens.

   ```sh
   claude setup-token
   read -rs CLAUDE_CODE_OAUTH_TOKEN && export CLAUDE_CODE_OAUTH_TOKEN
   claude
   ```

   The last line starts the Claude Code session that runs the steps below, in this terminal, with
   the token exported (above, "Where each step runs").

5. **Add the photos.** Every arm gets the same photos, so a picture never decides a pick. Put the
   files each brief names into `photos/<brief-id>/`, use only photos whose licence lets you use
   them this way, and write each one's source and licence into `results.md`. Where to find photos,
   and what each licence asks, is [brand-pages.md](brand-pages.md) section 5. Success: every file
   each brief lists in `briefs.json` is in `photos/<brief-id>/`; the runner copies the folder and
   does not check the files.

6. **Run the pilot,** from the session of step 4, as a background command. It runs every arm once
   on the first brief and settles the steps marked *not yet tried* before days of runs depend on
   them. Save a listing of your home folder first, so you can see whether an arm wrote to it:

   ```sh
   ls -a ~ > home-before.txt
   node run-arms.mjs pilot
   ls -a ~ | diff home-before.txt -
   ```

   Check each pilot run against the list in [skill-blind-test.md](skill-blind-test.md) section 4,
   and follow the "When it fails" line of each item that fails. If you will also judge, open
   nothing under `pilot-runs/` yourself, since its pages and streams carry each arm's name: let the
   session of step 4 read the records and report each item as pass or fail. If you will not judge,
   read each `pilot-runs/<run-id>/run.json` yourself: the verdict, `skills`, `permissionDenials`,
   `modelsUsed`, `durationMs` and `totalCostUsd`, and each run's `trace/prompt-expansions.jsonl`.
   The pilot records a skill nobody copied in under `isolationProblems` and goes on; write the
   no-skill run's `skills` into `bench.json` as `skillsInEveryRun`. Then send the pilot's pages
   through steps 8 to 10 with `node blind-pages.mjs pilot-runs`, to see the whole path work, and
   delete `judging/`, `key/` and `checks/` afterwards; if you will also judge, skip step 10 for the
   pilot and only check that the shots render. To run the pilot again, delete `pilot-runs/` first.

7. **Run the bench,** from the session of step 4, as a background command. It runs one run at a
   time, in the order it draws once, and picks up where it stopped when you start it again; a run
   the plan's limit stopped runs again then. If you add or remove a brief or an arm, or change
   `runsPerArm`, after the first start, the runner refuses to go on until you delete `runs/`. It
   does not see an edit inside a brief or a new commit for an arm, so change neither after the
   first run, or delete `runs/` and start a new count. Expect days, with the plan's limits in
   between. On a laptop, keep the machine awake while the bench runs: on macOS, start it as
   `caffeinate -i node run-arms.mjs`. Success: the last line gives every run asked as valid or
   failed, with none stopped at the plan's limit; if some were, start the runner again after the
   limit resets.

   ```sh
   node run-arms.mjs
   ```

8. **Make the blind copies.** Each finished page is copied under a random id, and the key goes to
   `key/`, which nobody opens before the picks are in.

   ```sh
   node blind-pages.mjs
   ```

   Success: the script prints `<N> pages copied under random ids to judging/pages.`, with N the
   valid count of step 7's last line.

9. **Serve the copies, then shoot them.** The session of step 4 runs the server as a background
   command, and it stays up through the judging, since the judges' scroll notes need it. The shoot
   script needs the same `PLAYWRIGHT_BROWSERS_PATH=0` to find the browser step 2 installed, and
   runs as a background command of the same session. By the script's own waits, a long page takes
   roughly a minute, so the 48 pages of a full bench take about an hour to shoot; this is not
   measured.

   ```sh
   node serve-pages.mjs
   ```

   ```sh
   PLAYWRIGHT_BROWSERS_PATH=0 node shoot-pages.mjs
   ```

   Success: one line `<id>: shot and checked` for each id in `judging/sets.json`, two PNG files
   per id in `judging/shots/`, and no error. The script stops first if the contrast check
   misjudges a control page. A page it could not shoot prints its error and goes to
   `checks/contrast-review.csv` for step 10.

10. **Look at the pages the contrast check could not decide.** Text over a photo is the common case.
    For each id in `checks/contrast-review.csv`, find the elements listed under that id in
    `checks/contrast.json`, and look at them in the shots and on the served page. For each
    element, take the colour of its text and the lightest and the darkest colour of the background
    right behind it with a colour picker, such as Digital Color Meter on macOS, and work out both
    ratios with a contrast checker or the WCAG 2 formula that
    [visual-design.md](visual-design.md) section 4 uses. Write `fail` in the last column when a
    ratio falls below 4.5:1, or 3:1 for large text, and `pass` when every element meets it. A page
    listed as not shot gets `fail` when its shots are missing from `judging/shots/`; otherwise
    judge its text on the served page the same way. The ids name no arm, so the look stays blind.
    The person who runs the bench may find an element by its selector with the browser's developer
    tools only when someone else judges; when that person also judges, the developer tools wait
    until the picks are in, and the elements are found by eye. Success: every row of
    `checks/contrast-review.csv` ends in `pass` or `fail`.

11. **Make the sheets.** The script leaves out every page below the contrast floor and refuses to
    run while a page from step 10 has no verdict.

    ```sh
    node make-sheets.mjs
    ```

    Success: the script prints `Sheets written for <N> judges.`, with N the number of names in
    `judges` in `bench.json`.

12. **Hand over the judging.** Give each judge the `judging/` folder and
    `judging-instructions.md`, and nothing else.

13. **Count.** The script refuses to count while a pick is missing or names a page outside its set.
    Paste its two tables into `results.md`, the one record of the result. Then follow
    [skill-blind-test.md](skill-blind-test.md) section 7 for what the result changes.

    ```sh
    node count-wins.mjs
    ```

    Success: the script prints two tables, and no error such as `Fix the picks first`.

Why it is good: every step says what it is for before it says what to run, so a reader can tell
which step to repeat when something fails. The pilot comes before the days of runs, and the
check for a `CLAUDE.md` above the bench has a positive control, so an empty answer means
something. The token is read without echo, so it reaches neither the screen nor the shell
history, and it is made in a plain terminal, so it reaches no transcript either. The steps that run
for days run as background commands of the session started in that terminal, with a plain
terminal as the fallback until the pilot shows that route works.

## The settings: bench.json

```json
{
  "runsPerArm": 2,
  "judges": ["judge-a", "judge-b", "judge-c"],
  "skillsInEveryRun": [],
  "pageServerPort": 8173,
  "claudeCodeVersion": "2.1.312"
}
```

| Field | What it means | Set it when | Leave it out when |
|---|---|---|---|
| `runsPerArm` | how many runs each arm gets per brief; run *k* of every arm forms one set | always; 2 is the floor of [skill-blind-test.md](skill-blind-test.md) section 2 | never |
| `judges` | one placeholder name per judge; each gets a folder of sheets | always, before `make-sheets.mjs` runs | never; name judges by placeholders, never by their names |
| `skillsInEveryRun` | the names the no-skill pilot run's `skills` list held | always; empty until the pilot shows otherwise | never: an empty list makes the full bench stop on any skill but the arm's own; the pilot records such a skill and goes on |
| `pageServerPort` | the port of the local page server | always; change it when 8173 is taken | never |
| `claudeCodeVersion` | the version `claude --version` printed when you set the bench up; the runner checks it before each run and stops on another | always, in step 1 | never: a Claude Code update between runs changes every run after it ([skill-blind-test.md](skill-blind-test.md) section 3) |

Why it is good: every value a person changes between benches sits in one small file, and the
values that decide fairness, such as the model and the effort, stay in the runner, next to the
call they shape.

## The briefs: briefs.json

Two briefs of different kinds show the shape. The test itself needs three to five
([skill-blind-test.md](skill-blind-test.md) section 2): add at least one more, such as a portfolio,
in the same shape. Three briefs, the eight arms and two runs make the 48 runs
[skill-blind-test.md](skill-blind-test.md) section 4 counts.

```json
{
  "briefs": [
    {
      "id": "bakery",
      "kind": "local business",
      "purpose": "A one-page site for a neighbourhood bakery. People who live nearby should see what is baked today, when the shop is open, and how to order a cake for a set date.",
      "copy": {
        "name": "Acme Corner Bakery",
        "headline": "Bread out of the oven at seven, most of it gone by noon",
        "intro": "We bake sourdough, rye and a few sweet things every morning in the back of the shop on Example Street. Come early for the seeded rye.",
        "sections": [
          {
            "title": "Baked every day",
            "items": ["Country sourdough", "Seeded rye", "Spelt rolls", "Cardamom buns"]
          },
          {
            "title": "Cakes to order",
            "text": "Birthday, wedding or just because. Tell us the date and how many people, and we call you back the same day with a price."
          },
          {
            "title": "Opening hours",
            "items": ["Tuesday to Friday, 7:00 to 15:00", "Saturday, 8:00 to 14:00", "Sunday and Monday, closed"]
          }
        ],
        "callToAction": "Order a cake",
        "contact": {
          "address": "12 Example Street",
          "phone": "555-0100",
          "email": "orders@example.com"
        }
      },
      "photos": [
        { "file": "loaves-on-rack.jpg", "alt": "Round sourdough loaves cooling on a wooden rack" },
        { "file": "buns-on-tray.jpg", "alt": "A tray of cardamom buns with pearl sugar" },
        { "file": "shop-counter.jpg", "alt": "The shop counter, with bread baskets on the wall behind it" }
      ]
    },
    {
      "id": "ledger",
      "kind": "product landing page",
      "purpose": "The landing page of an invoicing app for small design studios. A studio owner should understand in one screen what the app does, and start a free trial.",
      "copy": {
        "name": "Globex Ledger",
        "headline": "Send the invoice before the client forgets the project",
        "intro": "Globex Ledger turns your tracked hours into an invoice in two clicks, sends it, and reminds the client when it is late.",
        "sections": [
          {
            "title": "Hours become invoices",
            "text": "Pick a project, check the hours, press send. The invoice uses your studio's own layout and logo."
          },
          {
            "title": "Reminders you do not have to write",
            "text": "Seven days after the due date, the client gets a polite reminder. You choose the wording once."
          },
          {
            "title": "One view of who owes what",
            "text": "See every open invoice by client and by month, and export the list for your accountant."
          }
        ],
        "pricing": "Free for 30 days. Then €12 a month for up to three people.",
        "callToAction": "Start the free trial",
        "contact": { "email": "hello@example.com" }
      },
      "photos": [
        { "file": "studio-desk.jpg", "alt": "A studio desk with a laptop, a sketchbook and a cup of coffee" },
        { "file": "invoice-on-table.jpg", "alt": "A printed invoice next to a pen on a wooden table" }
      ]
    }
  ]
}
```

| Field | What it means | Set it when | Leave it out when |
|---|---|---|---|
| `id` | the brief's name in run ids, set names and `photos/<id>/` | always | never |
| `kind` | the kind of page, so the briefs of one bench differ | always | never |
| `purpose` | what the page is for and who it serves, in the client's words; the model infers the audience and tone from it, and the judges read it on every sheet | always | never |
| `copy` | every word the page may show; its keys follow the page, not a fixed schema | always | never: placeholder text would give every arm nothing to set |
| `photos` | the files in `photos/<id>/`, each with the alt text the page should use | always | never: every arm gets the same photos, so a picture never decides a pick |

Why it is good: the copy reads like a real client's, with real hours, a real offer and a reason to
act, so an arm has something to set and the judges have something to compare. The brief says what
the page is for and leaves the audience and tone for the model to infer, as
[skill-blind-test.md](skill-blind-test.md) section 2 asks. The businesses, the address, the phone
number and the e-mail addresses are placeholders that read as invented.

## The arms: arms.json

```json
{
  "arms": [
    { "name": "no-skill", "skill": null },
    {
      "name": "frontend-design",
      "skill": "frontend-design",
      "repo": "https://github.com/anthropics/skills",
      "commit": "41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f",
      "skillDir": "skills/frontend-design"
    },
    {
      "name": "hallmark",
      "skill": "hallmark",
      "repo": "https://github.com/Nutlope/hallmark",
      "commit": "8f6969f8922caabde9de1784959eae11ddf68073",
      "skillDir": "skills/hallmark"
    },
    {
      "name": "taste-skill",
      "skill": "design-taste-frontend",
      "repo": "https://github.com/Leonxlnx/taste-skill",
      "commit": "12af471f627f866411b4bd785b19646d3672784c",
      "skillDir": "skills/taste-skill"
    },
    {
      "name": "impeccable",
      "skill": "impeccable",
      "repo": "https://github.com/pbakaus/impeccable",
      "commit": "5e745ace7e151feb2a93d360d0281fe39448b857",
      "skillDir": ".claude/skills/impeccable"
    },
    {
      "name": "ui-ux-pro-max",
      "skill": "ui-ux-pro-max",
      "repo": "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill",
      "commit": "28b3b8dee8c976df4fa3e94aed4e092ad43fcb03",
      "skillDir": ".claude/skills/ui-ux-pro-max"
    },
    {
      "name": "taste-skill-classics",
      "skill": "high-end-visual-design",
      "repo": "https://github.com/Leonxlnx/taste-skill-classics",
      "commit": "5e08c9383dc4ad7fc0df70e1ac8cfa09ec356305",
      "skillDir": "skills/soft-skill"
    },
    {
      "name": "huashu-design",
      "skill": "huashu-design",
      "repo": "https://github.com/alchaincyf/huashu-design",
      "commit": "4fc7bfdbd5ec3fa2d43ce7a6433de60976a5e4b1",
      "skillDir": "."
    }
  ]
}
```

| Field | What it means | Set it when | Leave it out when |
|---|---|---|---|
| `name` | the arm's name in run ids, in `arms-src/<name>/` and in the results | always | never |
| `skill` | the `name` in the skill's `SKILL.md` frontmatter: the run calls `/<skill>`, and the copy goes into `.claude/skills/<skill>/` | always; `null` for the no-skill arm, which is the baseline | never |
| `repo` | where the arm comes from, for the clone and for the results record; no script reads it | for every arm with a skill | on the no-skill arm |
| `commit` | the commit the clone must sit at; the runner checks it before any run | for every arm with a skill | on the no-skill arm |
| `skillDir` | the folder in the clone that holds `SKILL.md`, copied whole into each run | for every arm with a skill | on the no-skill arm |

Why it is good: each arm is pinned by a full commit, and each `skill` and `skillDir` was read in
the arm's repository at that commit, so the copy loads under the name the run calls. The
no-skill arm sits in the same list as the others, so it runs in the same random order, under the
same flags.

## The runner

`run-arms.mjs` runs every brief, arm and run once, headless, in a random order it draws once, and
writes one `run.json` per run.

```js
// run-arms.mjs
import { execFile, spawn } from "node:child_process";
import { randomInt } from "node:crypto";
import { once } from "node:events";
import { createWriteStream } from "node:fs";
import { cp, mkdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import { basename, dirname, join, resolve } from "node:path";
import { pipeline } from "node:stream/promises";
import { promisify } from "node:util";

// The levels `claude --effort` accepts at 2.1.312, as a closed set
// (prompt-engineering.md section 15).
const ReasoningEffort = Object.freeze({
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  XHIGH: "xhigh",
  MAX: "max",
});

// One model and one effort for every arm (skill-blind-test.md section 2). The
// full model name, never an alias such as `opus`, so a new release cannot
// change the model halfway through the bench.
const PAGE_BUILDER_LLM_MODEL = "claude-opus-5-5";
// Long, loosely specified work with tools starts at high
// (prompt-engineering.md section 15).
const PAGE_BUILDER_LLM_REASONING_EFFORT = ReasoningEffort.HIGH;

// The same tools for every arm. Add one only when the pilot's
// permissionDenials show an arm needed it, and then for all arms
// (skill-blind-test.md section 4).
const ALLOWED_TOOLS = "Read,Write,Edit,Bash,Skill";

// A guard against a runaway run, far above a normal build. It caps Claude
// Code's own cost estimate, not a charge on a subscription.
const BUDGET_CAP_USD = "25";

// A 45-minute build plus a wait for the plan's session window to reset
// (CLAUDE_CODE_RETRY_WATCHDOG); a weekly limit outlasts it. A run killed here
// has no result: it fails, or counts as `limit` when the plan stopped it.
const RUN_TIMEOUT_MS = 6 * 60 * 60 * 1000;

// A failed run gets one more attempt (skill-blind-test.md section 2).
const ATTEMPTS_PER_RUN = 2;

// Three failed runs in a row point at the setup or the plan, not the arms.
const STOP_AFTER_FAILED_RUNS_IN_A_ROW = 3;

// Only these variables of your shell reach a run: no API key, no other
// vendor's key, nothing else of your setup (skill-blind-test.md section 3).
const PASSED_THROUGH_VARIABLES = [
  "PATH",
  "SHELL",
  "TERM",
  "LANG",
  "LC_ALL",
  "TMPDIR",
  "USER",
  "LOGNAME",
];

const VALID = "valid";
// The plan's limit stopped the run, not the arm
// (skill-blind-test.md section 4).
const LIMIT = "limit";
const ARMS_SOURCE_DIR = "arms-src";
const PHOTOS_DIR = "photos";

async function main(argv, environment) {
  const bench = await readJson("bench.json");
  const { arms } = await readJson("arms.json");
  const { briefs } = await readJson("briefs.json");
  const isPilot = argv[2] === "pilot";
  const oauthToken = environment.CLAUDE_CODE_OAUTH_TOKEN;

  if (!oauthToken) {
    throw new Error(
      "Export CLAUDE_CODE_OAUTH_TOKEN, the token `claude setup-token` " +
        "printed (skill-blind-test.md section 3).",
    );
  }

  await assertArmsAtTheirCommits(arms);

  // The pilot runs every arm once on the first brief, in a folder of its own
  // (skill-blind-test.md section 4).
  const runsDir = resolve(isPilot ? "pilot-runs" : "runs");
  const plannedBriefs = isPilot ? briefs.slice(0, 1) : briefs;
  const runsPerArm = isPilot ? 1 : bench.runsPerArm;
  const plan = await loadOrCreatePlan(
    join(runsDir, "plan.json"),
    listRuns(plannedBriefs, arms, runsPerArm),
    randomInt,
  );
  const context = {
    arms,
    briefs: plannedBriefs,
    runsDir,
    isPilot,
    skillsInEveryRun: bench.skillsInEveryRun,
    passedThrough: passedThroughVariables(environment),
    oauthToken,
  };

  let failedRunsInARow = [];
  for (const run of plan) {
    if (await isDone(join(runsDir, run.runId, "run.json"))) continue;

    await assertClaudeCodeVersion(bench.claudeCodeVersion, runsDir);
    const record = await runWithRetry(run, context);
    console.log(runLine(record));

    // A run the plan's limit stopped neither counts as a failure nor ends
    // a row of them (skill-blind-test.md section 4).
    if (record.status === VALID) failedRunsInARow = [];
    if (record.status === "failed") failedRunsInARow.push(record.runId);
    if (failedRunsInARow.length >= STOP_AFTER_FAILED_RUNS_IN_A_ROW) {
      // A recorded run counts as done, so a failure the setup caused runs
      // again only once its folder is gone.
      throw new Error(
        `${failedRunsInARow.length} runs in a row failed: ` +
          `${failedRunsInARow.join(", ")}. Read their stderr.txt before you ` +
          "start the runner again. Delete " +
          `${basename(runsDir)}/<run-id>/ to rerun one.`,
      );
    }
  }

  console.log(await planSummary(plan, runsDir));
}

// A run the plan's limit stopped runs again on the next start; any other
// recorded run is done (skill-blind-test.md section 4).
async function isDone(recordPath) {
  if (!(await exists(recordPath))) return false;

  const { status } = await readJson(recordPath);
  return status !== LIMIT;
}

// Claude Code updates itself when another session of yours installs a new
// version, and the next run would start it, so each run checks first
// (skill-blind-test.md section 3).
async function assertClaudeCodeVersion(recorded, runsDir) {
  const { stdout } = await promisify(execFile)("claude", ["--version"]);
  const installed = stdout.trim().split(" ")[0];
  if (installed !== recorded) {
    // Putting the recorded version back keeps every finished run countable;
    // a new count throws them away (skill-blind-test.md section 3).
    throw new Error(
      `Claude Code is ${installed}, bench.json records ${recorded}. Runs on ` +
        "two versions cannot be counted together. Put the recorded version " +
        `back, with \`claude install ${recorded}\` on a native installation, ` +
        "and start the runner again. Only to move to the new version: read " +
        "the headless and CLI pages again, write it into bench.json and " +
        `delete ${basename(runsDir)}/ (skill-blind-test.md section 3).`,
    );
  }
}

// The last line says how far the bench got, so the end and a stop read
// differently.
async function planSummary(plan, runsDir) {
  const records = await Promise.all(
    plan.map((run) => readJson(join(runsDir, run.runId, "run.json"))),
  );
  const countOf = (status) =>
    records.filter((record) => record.status === status).length;
  return (
    `${countOf(VALID)} valid, ${countOf("failed")} failed, ` +
    `${countOf(LIMIT)} stopped at the plan's limit, ` +
    `of ${plan.length} runs asked.`
  );
}

async function assertArmsAtTheirCommits(arms) {
  const problems = [];
  for (const arm of arms) {
    if (arm.skill === null) continue;

    const cloneDir = join(ARMS_SOURCE_DIR, arm.name);
    if (!(await exists(join(cloneDir, arm.skillDir, "SKILL.md")))) {
      problems.push(`${arm.name}: no SKILL.md in ${cloneDir}/${arm.skillDir}`);
      continue;
    }

    const head = await checkedOutCommit(cloneDir);
    if (!head.startsWith(arm.commit)) {
      problems.push(
        `${arm.name}: checked out ${head}, arms.json says ${arm.commit}`,
      );
    }
  }

  if (problems.length > 0) {
    throw new Error(
      `Clone each arm at its commit first:\n${problems.join("\n")}`,
    );
  }
}

async function checkedOutCommit(cloneDir) {
  const { stdout } = await promisify(execFile)("git", [
    "-C",
    cloneDir,
    "rev-parse",
    "HEAD",
  ]);
  return stdout.trim();
}

function listRuns(briefs, arms, runsPerArm) {
  return briefs.flatMap((brief) =>
    arms.flatMap((arm) =>
      Array.from({ length: runsPerArm }, (_, index) => ({
        runId: `${brief.id}-${arm.name}-${index + 1}`,
        briefId: brief.id,
        armName: arm.name,
        repeat: index + 1,
      })),
    ),
  );
}

async function loadOrCreatePlan(planPath, runs, randomIndex) {
  // A resumed bench keeps the order it drew the first time.
  if (await exists(planPath)) {
    const plan = await readJson(planPath);
    assertSameRuns(plan, runs);
    return plan;
  }

  const plan = shuffled(runs, randomIndex);

  await writeJson(planPath, plan);
  return plan;
}

// A plan drawn for other briefs, arms or runsPerArm would skip the new runs
// without a word, and the count would list them as asked.
function assertSameRuns(plan, runs) {
  const planned = plan.map((run) => run.runId).sort().join("\n");
  const listed = runs.map((run) => run.runId).sort().join("\n");
  if (planned !== listed) {
    throw new Error(
      "briefs.json, arms.json or runsPerArm changed since the plan was " +
        "drawn. Delete the runs folder to start again.",
    );
  }
}

// Fisher-Yates. Each script of the bench stands alone, so this function is
// also in make-sheets.mjs.
function shuffled(items, randomIndex) {
  const copy = [...items];
  for (let last = copy.length - 1; last > 0; last -= 1) {
    const pick = randomIndex(last + 1);
    [copy[last], copy[pick]] = [copy[pick], copy[last]];
  }
  return copy;
}

async function runWithRetry(run, context) {
  const runDir = join(context.runsDir, run.runId);
  // A run cut off by Ctrl-C has no run.json; it starts again from nothing.
  await rm(runDir, { recursive: true, force: true });

  const attempts = [];
  for (let attempt = 1; attempt <= ATTEMPTS_PER_RUN; attempt += 1) {
    const summary = await runAttempt(run, attempt, context);
    attempts.push(summary);
    // A second attempt would meet the same limit.
    if (summary.verdict === VALID || summary.planLimitHit) break;
  }

  const record = { ...run, status: runStatus(attempts.at(-1)), attempts };

  await writeJson(join(runDir, "run.json"), record);
  return record;
}

function runStatus(lastAttempt) {
  if (lastAttempt.verdict === VALID) return VALID;
  // Not the arm's failure: the runner runs it again on its next start
  // (skill-blind-test.md section 4).
  if (lastAttempt.planLimitHit) return LIMIT;
  return "failed";
}

async function runAttempt(run, attemptNumber, context) {
  const arm = context.arms.find((candidate) => candidate.name === run.armName);
  const brief = context.briefs.find(
    (candidate) => candidate.id === run.briefId,
  );
  const paths = attemptPaths(
    join(context.runsDir, run.runId, `attempt-${attemptNumber}`),
  );

  await prepareAttempt(paths, arm, brief);

  const exit = await runClaude({
    args: claudeArguments(buildPrompt(brief, arm)),
    cwd: paths.work,
    env: childEnvironment(context.passedThrough, paths, context.oauthToken),
    streamPath: paths.stream,
    stderrPath: paths.stderr,
  });

  const stream = parseJsonLines(await readFile(paths.stream, "utf8"));
  const expansions = parseJsonLines(await readTextIfPresent(paths.expansions));
  const init = stream.items.find(
    (event) => event.type === "system" && event.subtype === "init",
  );
  const result = stream.items.findLast((event) => event.type === "result");
  const problems =
    init === undefined
      ? []
      : isolationProblems(init, arm, context.skillsInEveryRun);

  // The pilot is where skillsInEveryRun is found, so it records what loaded
  // and goes on; the full bench stops (skill-blind-test.md section 3).
  if (context.isPilot && problems.length > 0) {
    console.log(`${run.runId}: ${problems.join("; ")}`);
  } else {
    assertIsolated(run.runId, problems);
  }

  const ran =
    arm.skill !== null && skillRan(arm.skill, expansions.items, stream.items);
  const pageWritten = await isNonEmptyFile(paths.page);
  const verdict = attemptVerdict({
    result,
    armSkill: arm.skill,
    ran,
    pageWritten,
  });

  return attemptSummary({
    attemptNumber,
    verdict,
    exit,
    init,
    result,
    ran,
    pageWritten,
    brokenLines: stream.brokenLines,
    isolationProblems: problems,
    // Only a run with no result: one that waited out a limit and then ended
    // with a result failed for the arm's own reason (skill-blind-test.md
    // section 4).
    planLimitHit: result === undefined && hitPlanLimit(stream.items),
  });
}

// The stream's rate_limit_event says when the plan stopped a run. Not yet
// tried: the pilot shows it only if it meets a limit.
function hitPlanLimit(events) {
  return events.some(
    (event) =>
      event.type === "rate_limit_event" &&
      event.rate_limit_info?.status === "rejected",
  );
}

function attemptPaths(root) {
  const work = join(root, "work");
  const trace = join(root, "trace");
  return {
    root,
    work,
    home: join(root, "home"),
    trace,
    // The run's trace: every event of the session. evals.md section 9 asks
    // for a trace store; a file per attempt needs nothing beyond your plan,
    // at the cost of search across runs.
    stream: join(root, "stream.jsonl"),
    stderr: join(root, "stderr.txt"),
    expansions: join(trace, "prompt-expansions.jsonl"),
    page: join(work, "site", "index.html"),
  };
}

async function prepareAttempt(paths, arm, brief) {
  await mkdir(paths.home, { recursive: true });
  await mkdir(paths.trace, { recursive: true });
  await mkdir(join(paths.work, ".claude"), { recursive: true });

  await cp(join(PHOTOS_DIR, brief.id), join(paths.work, "photos"), {
    recursive: true,
  });
  await writeJson(
    join(paths.work, ".claude", "settings.json"),
    traceSettings(paths.expansions),
  );

  if (arm.skill === null) return;

  // A project skill, so it loads with --setting-sources project; the folder
  // name is the skill's own name, which the run calls it by.
  await cp(
    join(ARMS_SOURCE_DIR, arm.name, arm.skillDir),
    join(paths.work, ".claude", "skills", arm.skill),
    { recursive: true, filter: (source) => basename(source) !== ".git" },
  );
}

// A hook in the run's project settings logs each typed /name, the record of
// whether the arm's skill ran (skill-blind-test.md section 4). Exec form, so
// no shell parses the path, and nothing goes to stdout, which Claude would
// read as context.
function traceSettings(expansionsPath) {
  return {
    hooks: {
      UserPromptExpansion: [
        {
          hooks: [
            {
              type: "command",
              command: "sh",
              args: ["-c", 'cat >> "$1"; echo >> "$1"', "sh", expansionsPath],
            },
          ],
        },
      ],
    },
  };
}

function buildPrompt(brief, arm) {
  const task = [
    "Build the web page that the brief in <brief> asks for.",
    "",
    "1. Read the brief, and look at the photos it lists in ./photos.",
    "2. Decide from the brief alone who the page is for and what tone fits.",
    "   Ask me nothing: where the brief leaves a choice open, decide it and",
    "   state your reading in one line.",
    "3. Choose the visual direction you recommend, and build it. If your",
    "   instructions offer a person several directions to pick from, pick the",
    "   one you recommend and go on.",
    "4. Write the finished page to ./site/index.html. Put every file it loads,",
    "   the photos you use included, under ./site/.",
    "",
    "Rules:",
    "- Use the copy in <brief> as it is. Add no names, numbers, quotes, logos",
    "  or claims that the brief does not give; short labels such as a menu",
    "  button are fine.",
    "- Use only the photos in ./photos as pictures. Fonts are your choice.",
    "- The page works as static files with no build step. Link every local",
    "  file by a relative path (./styles.css, never /styles.css).",
    "- Leave no server or other process running when you finish.",
    "",
    "<brief>",
    JSON.stringify(brief, null, 2),
    "</brief>",
  ].join("\n");

  // The same task for every arm; an arm's run calls its skill by name
  // (skill-blind-test.md section 4).
  return arm.skill === null ? task : `/${arm.skill} ${task}`;
}

function claudeArguments(prompt) {
  return [
    "-p",
    prompt,
    "--model",
    PAGE_BUILDER_LLM_MODEL,
    "--effort",
    PAGE_BUILDER_LLM_REASONING_EFFORT,
    // Only the run's own project settings load: the trace hook, and none of
    // your user or local settings (skill-blind-test.md section 3).
    "--setting-sources",
    "project",
    "--strict-mcp-config",
    "--permission-mode",
    "acceptEdits",
    // What would wait for a person is denied instead, the question tool
    // included. Needs Claude Code 2.1.259 or later.
    "--permission-prompts",
    "none",
    "--allowedTools",
    ALLOWED_TOOLS,
    "--max-budget-usd",
    BUDGET_CAP_USD,
    // The answer is the page on disk; code reads the run's state from these
    // events. prompt-engineering.md section 11 asks for a response schema
    // (--json-schema), which would add a failure that has nothing to do with
    // the page. The cost: no code reads the model's closing message.
    "--output-format",
    "stream-json",
    "--verbose",
  ];
}

function passedThroughVariables(environment) {
  return Object.fromEntries(
    PASSED_THROUGH_VARIABLES.filter(
      (name) => environment[name] !== undefined,
    ).map((name) => [name, environment[name]]),
  );
}

function childEnvironment(passedThrough, paths, oauthToken) {
  return {
    ...passedThrough,
    // A home and a config folder of the run's own: no skill finds history
    // from an earlier run, and no arm writes to your home folder. Not yet
    // tried; the pilot settles it (skill-blind-test.md section 3).
    HOME: paths.home,
    CLAUDE_CONFIG_DIR: join(paths.home, ".claude"),
    // Your subscription, as a token, since the run's config folder holds no
    // login. The runner writes it to no file.
    CLAUDE_CODE_OAUTH_TOKEN: oauthToken,
    CLAUDE_CODE_DISABLE_AUTO_MEMORY: "1",
    CLAUDE_CODE_DISABLE_BUNDLED_SKILLS: "1",
    // A dev server started in the background would hold the run open.
    CLAUDE_CODE_DISABLE_BACKGROUND_TASKS: "1",
    // At the plan's usage limit a run waits for the reset instead of failing.
    CLAUDE_CODE_RETRY_WATCHDOG: "1",
    // This run does not update Claude Code in the background. Your other
    // sessions still can, so main checks the version before each run.
    DISABLE_AUTOUPDATER: "1",
    // Asks Impeccable to send no usage record; its catalog request still goes.
    DO_NOT_TRACK: "1",
  };
}

async function runClaude({ args, cwd, env, streamPath, stderrPath }) {
  // stdin is closed, so a run can never wait for input.
  const child = spawn("claude", args, {
    cwd,
    env,
    stdio: ["ignore", "pipe", "pipe"],
  });
  const timer = setTimeout(() => child.kill("SIGTERM"), RUN_TIMEOUT_MS);
  const streamWritten = pipeline(child.stdout, createWriteStream(streamPath));
  const stderrWritten = pipeline(child.stderr, createWriteStream(stderrPath));

  const [exitCode, signal] = await once(child, "close");
  clearTimeout(timer);
  await Promise.all([streamWritten, stderrWritten]);

  return { exitCode, signal };
}

// A run killed in the middle of a line leaves a broken last line: it is
// counted in the record, not hidden.
function parseJsonLines(text) {
  const items = [];
  let brokenLines = 0;
  for (const line of text.split("\n")) {
    if (line.trim() === "") continue;

    try {
      items.push(JSON.parse(line));
    } catch {
      brokenLines += 1;
    }
  }
  return { items, brokenLines };
}

function isolationProblems(init, arm, skillsInEveryRun) {
  const expected = new Set(
    arm.skill === null ? skillsInEveryRun : [...skillsInEveryRun, arm.skill],
  );
  const problems = init.skills
    .filter((skill) => !expected.has(skill))
    .map((skill) => `skill ${skill} loaded, not expected`);

  if (arm.skill !== null && !init.skills.includes(arm.skill)) {
    problems.push(`skill ${arm.skill} did not load`);
  }
  if (init.plugins.length > 0) {
    const names = init.plugins.map((plugin) => plugin.name);
    problems.push(`plugins loaded: ${names.join(", ")}`);
  }
  if (init.mcp_servers.length > 0) {
    const names = init.mcp_servers.map((server) => server.name);
    problems.push(`MCP servers loaded: ${names.join(", ")}`);
  }
  return problems;
}

// A leak is a broken setup, not an arm's failure, so it stops the bench.
function assertIsolated(runId, problems) {
  if (problems.length === 0) return;

  throw new Error(
    `${runId} was not isolated: ${problems.join("; ")}. ` +
      "Fix the setup (skill-blind-test.md section 3).",
  );
}

// A typed /name shows in the hook's log; a skill the model calls shows as a
// Skill tool call. Its input fields are not documented, so the call is
// matched on the skill's name anywhere in the input.
function skillRan(skillName, expansions, events) {
  const typed = expansions.some((entry) => entry.command_name === skillName);
  const called = events
    .filter((event) => event.type === "assistant")
    .flatMap((event) => event.message?.content ?? [])
    .filter((block) => block.type === "tool_use" && block.name === "Skill")
    .some((block) => JSON.stringify(block.input).includes(skillName));
  return typed || called;
}

function attemptVerdict({ result, armSkill, ran, pageWritten }) {
  if (result === undefined) {
    return "no result event: killed, crashed or timed out";
  }
  if (result.subtype !== "success" || result.is_error) {
    return `result ${result.subtype}, is_error ${result.is_error}`;
  }
  if (armSkill !== null && !ran) return "the arm's skill did not run";
  if (!pageWritten) return "no page at site/index.html";
  return VALID;
}

function attemptSummary({
  attemptNumber,
  verdict,
  exit,
  init,
  result,
  ran,
  pageWritten,
  brokenLines,
  isolationProblems,
  planLimitHit,
}) {
  return {
    attempt: attemptNumber,
    verdict,
    planLimitHit,
    exitCode: exit.exitCode,
    signal: exit.signal,
    brokenLines,
    isolationProblems,
    claudeCodeVersion: init?.claude_code_version,
    model: init?.model,
    // The init event a script reads carries no effort, so the record keeps
    // the effort the run was given (skill-blind-test.md section 4).
    effort: PAGE_BUILDER_LLM_REASONING_EFFORT,
    apiKeySource: init?.apiKeySource,
    skills: init?.skills,
    pluginErrors: init?.plugin_errors,
    resultSubtype: result?.subtype,
    isError: result?.is_error,
    numTurns: result?.num_turns,
    durationMs: result?.duration_ms,
    totalCostUsd: result?.total_cost_usd,
    usage: result?.usage,
    // Subagents an arm starts may run on another model; this shows which.
    modelsUsed: Object.keys(result?.modelUsage ?? {}),
    permissionDenials: result?.permission_denials,
    skillRan: ran,
    pageWritten,
  };
}

function runLine(record) {
  const last = record.attempts.at(-1);
  const minutes = Math.round((last.durationMs ?? 0) / 60000);
  return `${record.runId}: ${record.status} (${last.verdict}), ${minutes} min`;
}

async function readJson(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

async function writeJson(path, value) {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, `${JSON.stringify(value, null, 2)}\n`);
}

async function readTextIfPresent(path) {
  return (await exists(path)) ? readFile(path, "utf8") : "";
}

async function exists(path) {
  return stat(path).then(
    () => true,
    () => false,
  );
}

async function isNonEmptyFile(path) {
  return stat(path).then(
    (info) => info.isFile() && info.size > 0,
    () => false,
  );
}

await main(process.argv, process.env);
```

Why it is good: every condition that makes the arms equal is a named constant with its reason at
the line, so a reader who copies the runner sees why the model is a full name, why the tools are
one list, and why only eight variables of the shell reach a run. A run counts as valid only when the
stream's `result` event says `success` with `is_error` false, the arm's skill ran, and the page
exists ([skill-blind-test.md](skill-blind-test.md) section 4); a leak of a skill, a plugin or an
MCP server stops the bench instead of passing for an arm's failure, and the pilot, which finds
`skillsInEveryRun`, records such a leak and goes on. A run the plan's limit stopped is recorded as
`limit`, not as the arm's failure, and runs again on the next start; the Claude Code version is
checked before each run, and a changed plan stops the runner. The model and the effort are
named constants, and the effort comes from a closed set
([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 15);
the prompt states the goal and the steps, marks the brief with a tag, and gives a way out the model
can check (sections 2, 5 and 8 of the same file). Two departures are declared at their lines: the run's answer is the page on disk, not
a response schema (section 11), and each run's trace is a file, not a trace store
([evals.md](../../python/evals/evals.md) section 9). Each function does one job, guard clauses end
it early, and the environment and the random source come in as parameters
([readability.md](../../any-language/readability/readability.md) sections 2, 3 and 6). Failed runs
stay in the record, with the attempt that failed, so the count can divide by what was asked for.

## The blind copies

`blind-pages.mjs` copies each valid page under a random id, removes the traces a judge could tell
an arm by without looking at the design, and writes the key apart from the judges' folder.

```js
// blind-pages.mjs
import { randomBytes } from "node:crypto";
import {
  cp,
  lstat,
  mkdir,
  readdir,
  readFile,
  stat,
  writeFile,
} from "node:fs/promises";
import { dirname, extname, join } from "node:path";

const PAGES_DIR = "judging/pages";
const SETS_FILE = "judging/sets.json";
// Outside judging/, the only folder the judges get, so nobody who judges
// opens the key by chance (skill-blind-test.md section 6).
const KEY_FILE = "key/blind-key.json";

async function main(argv) {
  const runsDir = argv[2] ?? "runs";

  // New ids on a second pass would leave two copies of every page.
  if (await exists(PAGES_DIR)) {
    throw new Error(
      `${PAGES_DIR} exists. Delete judging/, key/ and checks/ to start again.`,
    );
  }

  const runs = await validRuns(runsDir);
  const takenIds = new Set();
  const key = [];

  for (const run of runs) {
    const id = newBlindId(takenIds, randomBytes);
    takenIds.add(id);
    await copyWithoutLinks(run.siteDir, join(PAGES_DIR, id));
    await stripArmTraces(join(PAGES_DIR, id), id);
    key.push({
      id,
      runId: run.runId,
      arm: run.armName,
      briefId: run.briefId,
      repeat: run.repeat,
    });
  }

  await writeJson(KEY_FILE, key);
  await writeJson(SETS_FILE, setsWithoutArms(key));
  console.log(`${key.length} pages copied under random ids to ${PAGES_DIR}.`);
}

async function validRuns(runsDir) {
  const plan = await readJson(join(runsDir, "plan.json"));
  const records = await Promise.all(
    plan.map((run) => readJson(join(runsDir, run.runId, "run.json"))),
  );
  // A run still waiting at the plan's limit would be missing from every set,
  // and finishing it later would mean judging again.
  assertNoRunAtLimit(records);

  return records
    .filter((record) => record.status === "valid")
    .map((record) => ({
      ...record,
      siteDir: join(
        runsDir,
        record.runId,
        `attempt-${record.attempts.at(-1).attempt}`,
        "work",
        "site",
      ),
    }));
}

// A run the plan's limit stopped is neither valid nor failed: it waits for
// the runner's next start (skill-blind-test.md section 4). Each script of the
// bench stands alone, so this function is also in count-wins.mjs.
function assertNoRunAtLimit(records) {
  const waiting = records.filter((record) => record.status === "limit");
  if (waiting.length > 0) {
    const runIds = waiting.map((record) => record.runId).join(", ");
    throw new Error(
      `Start run-arms.mjs again first: ${runIds} stopped at the plan's limit.`,
    );
  }
}

function newBlindId(takenIds, randomBytesOf) {
  for (;;) {
    const id = randomBytesOf(4).toString("hex");
    if (!takenIds.has(id)) return id;
  }
}

// A link an arm left in its page could point at a file anywhere on your
// machine, which the page server would then serve (skill-blind-test.md
// section 8).
async function copyWithoutLinks(from, to) {
  await cp(from, to, {
    recursive: true,
    filter: async (source) => !(await lstat(source)).isSymbolicLink(),
  });
}

// Takes out the traces a judge could read an arm from without looking at the
// design: the tab title, comments, a generator tag, and the stamp comments
// some arms write into their CSS. Text a visitor sees stays as it is.
async function stripArmTraces(pageDir, id) {
  const files = await readdir(pageDir, { recursive: true });
  for (const file of files) {
    const path = join(pageDir, file);
    const extension = extname(file).toLowerCase();
    if (extension === ".html" || extension === ".htm") {
      await writeFile(path, blindHtml(await readFile(path, "utf8"), id));
    }
    if (extension === ".css") {
      await writeFile(path, withoutCssComments(await readFile(path, "utf8")));
    }
  }
}

function blindHtml(html, id) {
  return html
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<title\b[^>]*>[\s\S]*?<\/title>/gi, `<title>${id}</title>`)
    .replace(/<meta\b[^>]*name=["']?generator["']?[^>]*>/gi, "")
    .replace(
      /(<style\b[^>]*>)([\s\S]*?)(<\/style>)/gi,
      (_, open, css, close) => open + withoutCssComments(css) + close,
    );
}

// Only in CSS: in a script, the same pattern can match code.
function withoutCssComments(css) {
  return css.replace(/\/\*[\s\S]*?\*\//g, "");
}

// One set per brief and run number, listing ids only. Sorted ids carry no
// trace of the order in which the arms ran.
function setsWithoutArms(key) {
  const sets = new Map();
  for (const entry of key) {
    const name = `${entry.briefId}-run${entry.repeat}`;
    const set = sets.get(name) ?? {
      set: name,
      briefId: entry.briefId,
      ids: [],
    };
    set.ids.push(entry.id);
    sets.set(name, set);
  }
  return [...sets.values()].map((set) => ({ ...set, ids: set.ids.sort() }));
}

async function readJson(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

async function writeJson(path, value) {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, `${JSON.stringify(value, null, 2)}\n`);
}

async function exists(path) {
  return stat(path).then(
    () => true,
    () => false,
  );
}

await main(process.argv);
```

Why it is good: the key and the list of sets are two files, and only the one the judges may see
goes into `judging/`; the sets list sorted ids, so not even their order hints at an arm. The script
refuses a second pass that would leave two copies of every page. It strips comments only from HTML
and CSS, and says why at the line: in a script, the same pattern can match code. Symbolic links are
dropped with their reason ([skill-blind-test.md](skill-blind-test.md) section 8).

## The page server

`serve-pages.mjs` serves the blind copies to the screenshot script and to the judges' scroll notes,
on this machine only.

```js
// serve-pages.mjs
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, resolve, sep } from "node:path";

// This machine only: the pages are agent output nobody has reviewed
// (skill-blind-test.md section 8).
const HOST = "127.0.0.1";
const PAGES_DIR = resolve("judging/pages");

const CONTENT_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".avif": "image/avif",
  ".gif": "image/gif",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
  ".otf": "font/otf",
  ".mp4": "video/mp4",
  ".webm": "video/webm",
};

async function main() {
  const { pageServerPort } = JSON.parse(await readFile("bench.json", "utf8"));
  const server = createServer((request, response) =>
    answer(request, response, PAGES_DIR),
  );

  server.listen(pageServerPort, HOST, () => {
    console.log(`Serving ${PAGES_DIR} at http://${HOST}:${pageServerPort}/`);
  });
}

async function answer(request, response, root) {
  const path = fileInside(root, new URL(request.url, "http://page").pathname);
  if (path === null) {
    response.writeHead(403).end();
    return;
  }

  try {
    const body = await readFile(path);
    const type = CONTENT_TYPES[extname(path).toLowerCase()];
    response
      .writeHead(200, { "Content-Type": type ?? "application/octet-stream" })
      .end(body);
  } catch {
    response.writeHead(404).end();
  }
}

// Returns null for a path that leaves the root, as an encoded ../ would.
function fileInside(root, urlPath) {
  let decoded;
  try {
    decoded = decodeURIComponent(urlPath);
  } catch {
    return null;
  }

  const path = resolve(root, `.${decoded}`);
  if (path !== root && !path.startsWith(root + sep)) return null;
  return decoded.endsWith("/") ? join(path, "index.html") : path;
}

await main();
```

Why it is good: it answers only on `127.0.0.1`, and a path that leaves the pages folder, such as an
encoded `../`, gets a 403 before any file is read. It sets the content type for module scripts and
fonts, which a browser checks, so a page loads here as it would on a host. Every page is served the
same way, which keeps the arms equal at the shot.

## Screenshots and contrast

`shoot-pages.mjs` shoots the first screen of every blind page at two widths and checks its contrast.
It needs the page server running.

```js
// shoot-pages.mjs
import { AxeBuilder } from "@axe-core/playwright";
import { chromium, devices } from "playwright";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";

const SHOTS_DIR = "judging/shots";
const CONTRAST_FILE = "checks/contrast.json";
const CONTRAST_REVIEW_FILE = "checks/contrast-review.csv";

// Every page is shot at these two widths, the same way for every arm
// (skill-blind-test.md section 5).
const WIDTHS = {
  desktop: { viewport: { width: 1280, height: 800 } },
  phone: devices["iPhone 13"],
};

// One pause per screen of the scroll that wakes lazy images and reveals.
const SCROLL_PAUSE_MS = 250;
// Time for script-driven motion to come to rest before a shot or a contrast
// read: animations "disabled" stops only CSS and Web Animations. Playwright
// discourages fixed waits; here no signal says when a page's own scripts stop
// moving, so the bench waits a fixed time. Not yet tried at this length.
const SETTLE_MS = 1500;
// An image that never loads, such as a lazy one nobody scrolled to, must
// not hold the shot forever.
const IMAGE_WAIT_MS = 10000;
// A page that never fires load must not hold every page after it.
const NAVIGATION_TIMEOUT_MS = 60000;

// The higher answer wins when two screens judge one element: a failure on any
// screen fails the element, and "needs review" stays only if no screen decided.
const ANSWER_RANK = { incomplete: 0, pass: 1, violation: 2 };

// The contrast gate is tried on a page known to fail (2.85:1) and one known
// to pass (12.63:1) before it judges any arm's page (evals.md section 5).
const CONTROL_PAGES = {
  failing: '<p style="color: #999999; background: #ffffff">Grey on white</p>',
  passing: '<p style="color: #333333; background: #ffffff">Dark on white</p>',
};

async function main() {
  const { pageServerPort } = await readJson("bench.json");
  const sets = await readJson("judging/sets.json");
  const ids = sets.flatMap((set) => set.ids);
  const serverUrl = `http://127.0.0.1:${pageServerPort}`;

  await mkdir(SHOTS_DIR, { recursive: true });

  const browser = await chromium.launch();
  const findings = {};
  try {
    await assertContrastGateWorks(browser);
    for (const id of ids) {
      findings[id] = await shootAtEveryWidth(browser, serverUrl, id);
      // Written after each page, so a stop keeps every page done so far.
      await writeJson(CONTRAST_FILE, findings);
      await writeText(CONTRAST_REVIEW_FILE, reviewSheet(findings));
    }
  } finally {
    await browser.close();
  }
}

// A page that cannot be shot or checked goes to a person's look with its
// error, instead of stopping the pages after it (skill-blind-test.md
// section 5).
async function shootAtEveryWidth(browser, serverUrl, id) {
  const byWidth = {};
  const errors = [];
  for (const [width, contextOptions] of Object.entries(WIDTHS)) {
    try {
      byWidth[width] = await shootPage(
        browser,
        `${serverUrl}/${id}/index.html`,
        { shotPath: join(SHOTS_DIR, `${id}-${width}.png`), contextOptions },
      );
    } catch (error) {
      errors.push(`${width}: ${error.message}`);
      byWidth[width] = notShot(error);
    }
  }

  console.log(
    errors.length === 0
      ? `${id}: shot and checked`
      : `${id}: not shot (${errors.join("; ")}), ` +
          `listed in ${CONTRAST_REVIEW_FILE}`,
  );
  return byWidth;
}

function notShot(error) {
  return {
    violations: [],
    needsReview: [
      {
        target: "the page",
        answer: "incomplete",
        summary: `not shot: ${error.message}`,
      },
    ],
  };
}

async function shootPage(browser, pageUrl, { shotPath, contextOptions }) {
  const context = await browser.newContext(contextOptions);
  try {
    const page = await context.newPage();

    // "load", not "networkidle", which Playwright marks as discouraged.
    await page.goto(pageUrl, {
      waitUntil: "load",
      timeout: NAVIGATION_TIMEOUT_MS,
    });
    await scrollThrough(page);
    await waitForImagesAndFonts(page);
    await page.waitForTimeout(SETTLE_MS);

    await page.screenshot({
      path: shotPath,
      animations: "disabled",
      caret: "hide",
      scale: "css",
    });

    return await contrastFindings(page);
  } finally {
    await context.close();
  }
}

async function assertContrastGateWorks(browser) {
  const context = await browser.newContext(WIDTHS.desktop);
  const page = await context.newPage();
  const found = {};
  for (const [name, body] of Object.entries(CONTROL_PAGES)) {
    await page.setContent(`<!doctype html><html lang="en"><body>${body}`);
    found[name] = await contrastFindings(page);
  }
  await context.close();

  const failsTheFailing = found.failing.violations.length > 0;
  const passesThePassing = found.passing.violations.length === 0;
  if (!failsTheFailing || !passesThePassing) {
    throw new Error("The contrast check misjudged a control page; fix it.");
  }
}

// One slow pass down the page, as a reader's scroll would make it, then back
// to the top for the first-screen shot.
async function scrollThrough(page) {
  await page.evaluate(async (pauseMs) => {
    const height = document.documentElement.scrollHeight;
    for (let top = 0; top < height; top += window.innerHeight) {
      window.scrollTo(0, top);
      await new Promise((done) => setTimeout(done, pauseMs));
    }
    window.scrollTo(0, 0);
  }, SCROLL_PAUSE_MS);
}

// Playwright's screenshot code waits for fonts but not for images, and that
// wait is not documented, so both waits are made here.
async function waitForImagesAndFonts(page) {
  await page.evaluate(async (limitMs) => {
    const decoded = Promise.all(
      [...document.images].map((image) => image.decode().catch(() => null)),
    );
    const limit = new Promise((done) => setTimeout(done, limitMs));
    await Promise.race([decoded, limit]);
    await document.fonts.ready;
  }, IMAGE_WAIT_MS);
}

// axe decides contrast only for text inside the viewport, so it reads the page
// one screen at a time (skill-blind-test.md section 5).
async function contrastFindings(page) {
  const height = await page.evaluate(
    () => document.documentElement.scrollHeight,
  );
  const screenHeight = page.viewportSize().height;
  const answers = new Map();

  for (let top = 0; top < height; top += screenHeight) {
    await page.evaluate((y) => window.scrollTo(0, y), top);
    await page.waitForTimeout(SETTLE_MS);
    const results = await new AxeBuilder({ page })
      .withRules(["color-contrast"])
      .analyze();
    keepStrongestAnswers(answers, results);
  }

  const elements = [...answers.entries()].map(([target, found]) => ({
    target,
    ...found,
  }));
  return {
    violations: elements.filter((element) => element.answer === "violation"),
    needsReview: elements.filter((element) => element.answer === "incomplete"),
  };
}

function keepStrongestAnswers(answers, results) {
  const found = [
    ...nodesOf(results.incomplete, "incomplete"),
    ...nodesOf(results.passes, "pass"),
    ...nodesOf(results.violations, "violation"),
  ];
  for (const { target, answer, summary } of found) {
    const known = answers.get(target);
    const stronger =
      known === undefined || ANSWER_RANK[answer] > ANSWER_RANK[known.answer];
    if (stronger) {
      answers.set(target, { answer, summary });
    }
  }
}

function nodesOf(ruleResults, answer) {
  return ruleResults.flatMap((rule) =>
    rule.nodes.map((node) => ({
      target: node.target.join(" "),
      answer,
      summary: node.failureSummary ?? "",
    })),
  );
}

// One row per page whose text axe could not decide and that has no failure:
// a person looks at it and writes pass or fail before the pick.
function reviewSheet(findings) {
  const rows = Object.entries(findings)
    .filter(([, byWidth]) => needsAPersonsLook(Object.values(byWidth)))
    .map(([id, byWidth]) => {
      const count = Object.values(byWidth).reduce(
        (sum, width) => sum + width.needsReview.length,
        0,
      );
      return `${id},${count},`;
    });
  return ["id,elements_to_review,manual_verdict", ...rows, ""].join("\n");
}

function needsAPersonsLook(widths) {
  const failed = widths.some((width) => width.violations.length > 0);
  const undecided = widths.some((width) => width.needsReview.length > 0);
  return undecided && !failed;
}

async function readJson(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

async function writeJson(path, value) {
  await writeText(path, `${JSON.stringify(value, null, 2)}\n`);
}

async function writeText(path, text) {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, text);
}

await main();
```

Why it is good: every page goes through the same waits, the scroll that wakes lazy images, the
image and font waits, and the settle time, before one shot per width, so no arm gains from how it
loads ([skill-blind-test.md](skill-blind-test.md) section 5). The contrast gate is first tried on a
page known to fail and one known to pass ([evals.md](../../python/evals/evals.md) section 5), and
an element axe could not decide goes to a person, never through as a pass. A page that cannot be
shot goes to a person too, with its error, and the results are written after each page, so one bad
page stops none of the others. The fixed wait is a declared departure from Playwright's advice,
with its reason and the length still to be tried.

## The judging sheets

`make-sheets.mjs` leaves out every page below the contrast floor and writes, for each judge, one
sheet per set in an order shuffled for that judge, an empty `picks.csv` and an empty
`scroll-notes.csv`.

```js
// make-sheets.mjs
import { randomInt } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";

const SHOWN_SETS_FILE = "judging/shown-sets.json";
const VERDICTS = new Set(["pass", "fail"]);

async function main() {
  const bench = await readJson("bench.json");
  const { briefs } = await readJson("briefs.json");
  const sets = await readJson("judging/sets.json");
  const contrast = await readJson("checks/contrast.json");
  const verdicts = manualVerdicts(
    await readFile("checks/contrast-review.csv", "utf8"),
  );

  // Every page axe could not decide gets a person's look before the pick
  // (skill-blind-test.md section 5).
  const undecided = Object.keys(contrast).filter(
    (id) => needsVerdict(contrast[id]) && !VERDICTS.has(verdicts.get(id)),
  );
  if (undecided.length > 0) {
    throw new Error(
      "Write pass or fail in checks/contrast-review.csv for: " +
        undecided.join(", "),
    );
  }

  // A page below the contrast floor leaves the pick, whatever its looks
  // (visual-design.md section 4).
  const shownSets = sets.map((set) => ({
    ...set,
    ids: set.ids.filter((id) => meetsFloor(contrast[id], verdicts.get(id))),
  }));
  await writeJson(SHOWN_SETS_FILE, shownSets);

  for (const judge of bench.judges) {
    await writeJudgeFolder(judge, shownSets, briefs, randomInt);
  }
  console.log(`Sheets written for ${bench.judges.length} judges.`);
}

function manualVerdicts(csv) {
  const rows = csv.trim().split("\n").slice(1);
  return new Map(
    rows.map((row) => {
      const [id, , verdict = ""] = row.split(",");
      return [id.trim(), verdict.trim().toLowerCase()];
    }),
  );
}

function needsVerdict(byWidth) {
  const widths = Object.values(byWidth);
  const failed = widths.some((width) => width.violations.length > 0);
  const undecided = widths.some((width) => width.needsReview.length > 0);
  return undecided && !failed;
}

function meetsFloor(byWidth, verdict) {
  const widths = Object.values(byWidth);
  if (widths.some((width) => width.violations.length > 0)) return false;
  if (widths.some((width) => width.needsReview.length > 0)) {
    return verdict === "pass";
  }
  return true;
}

async function writeJudgeFolder(judge, shownSets, briefs, randomIndex) {
  const folder = join("judging", judge);
  const pickRows = [];

  for (const set of shownSets) {
    if (set.ids.length === 0) continue;

    const brief = briefs.find((candidate) => candidate.id === set.briefId);
    // A new order for every judge, so no page gains from always coming first.
    const order = shuffled(set.ids, randomIndex);
    await writeText(
      join(folder, `${set.set}.html`),
      sheetHtml(set, brief, order),
    );
    pickRows.push(`${set.set},`);
  }

  const allIds = shuffled(shownSets.flatMap((set) => set.ids), randomIndex);
  await writeText(
    join(folder, "picks.csv"),
    ["set,picked_id", ...pickRows, ""].join("\n"),
  );
  await writeText(
    join(folder, "scroll-notes.csv"),
    ["id,scroll_and_motion", ...allIds.map((id) => `${id},`), ""].join("\n"),
  );
}

// Fisher-Yates. Each script of the bench stands alone, so this function is
// also in run-arms.mjs.
function shuffled(items, randomIndex) {
  const copy = [...items];
  for (let last = copy.length - 1; last > 0; last -= 1) {
    const pick = randomIndex(last + 1);
    [copy[last], copy[pick]] = [copy[pick], copy[last]];
  }
  return copy;
}

function sheetHtml(set, brief, orderedIds) {
  const pages = orderedIds
    .map(
      (id) => `
    <figure>
      <figcaption>${id}</figcaption>
      <img src="../shots/${id}-desktop.png" width="640" alt="Page ${id}, desktop">
      <img src="../shots/${id}-phone.png" width="195" alt="Page ${id}, phone">
    </figure>`,
    )
    .join("");

  // The question names no quality to aim at: praise words in a judge's
  // criteria can pull the picks toward one look (skill-blind-test.md
  // section 6).
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>${set.set}</title>
  <style>
    body { font: 16px/1.5 system-ui, sans-serif; margin: 24px; }
    .pages { display: flex; flex-wrap: wrap; gap: 32px; }
    figure { margin: 0; display: flex; gap: 12px; align-items: flex-start; }
    figcaption { font: 600 18px/1.4 ui-monospace, monospace; }
    img { height: auto; border: 1px solid #767676; }
  </style>
</head>
<body>
  <h1>${set.set}</h1>
  <p>${escapeHtml(brief.purpose)}</p>
  <p>Which page would you put live for this brief, as it is? Write its id
  next to ${set.set} in picks.csv.</p>
  <div class="pages">${pages}
  </div>
</body>
</html>
`;
}

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function readJson(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

async function writeJson(path, value) {
  await writeText(path, `${JSON.stringify(value, null, 2)}\n`);
}

async function writeText(path, text) {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, text);
}

await main();
```

Why it is good: it stops while any page that needs a person's look has no verdict, so no page
enters the pick unchecked ([skill-blind-test.md](skill-blind-test.md) section 5). The order changes
per judge, so no page gains from always coming first. The question on the sheet names no quality
to aim at, and the brief's purpose is escaped before it goes into the page.

## What the judges read

`judging-instructions.md` goes to every judge with the `judging/` folder.

```markdown
# How to judge

You judge web pages built for a few short briefs, without knowing what built each one. Your
sheets are in `judging/<your-name>/`. Open nothing else in the bench.

1. Open each set file, such as `bakery-run1.html`. Read the brief at the top, look at every page at
   both widths, and choose the one you would put live for this brief, as it is.
2. Write that page's id next to the set's name in your `picks.csv`. One id per set. Judge each set
   on its own.
3. Do not open a page's source, the browser's developer tools, or any file outside your folder and
   `judging/shots/`.
4. When every set has its id, and not before, open each page in your `scroll-notes.csv` at
   `http://127.0.0.1:8173/<id>/index.html`. Scroll from top to bottom, and write a few words on how
   the scroll and the motion feel. Your picks stay as they are.
```

Why it is good: a judge reads one short page and knows what to open, what to write, and what not
to touch. The scroll notes come after the picks, so the motion a judge sees does not change a pick
already made on the stills, and each step leaves something in a file the count can check.

## The count

`count-wins.mjs` checks every judge's picks, joins them with the key, and prints the two tables for
`results.md`.

```js
// count-wins.mjs
import { readFile } from "node:fs/promises";
import { join } from "node:path";

const RUNS_DIR = "runs";

async function main() {
  const bench = await readJson("bench.json");
  const { arms } = await readJson("arms.json");
  const { briefs } = await readJson("briefs.json");
  const key = await readJson("key/blind-key.json");
  const shownSets = await readJson("judging/shown-sets.json");
  const plan = await readJson(join(RUNS_DIR, "plan.json"));
  const records = await Promise.all(
    plan.map((run) => readJson(join(RUNS_DIR, run.runId, "run.json"))),
  );
  const picks = await readPicks(bench.judges, shownSets);

  assertNoRunAtLimit(records);
  assertOneSetup(records);

  const rows = winsRows({
    arms,
    briefs,
    key,
    picks,
    records,
    shownSets,
    bench,
  });
  console.log(winsTable(rows));
  console.log("");
  console.log(totalsTable(rows, arms));
}

// One pick per judge and shown set, each naming a page of that set, before
// any count is made (evals.md section 6).
async function readPicks(judges, shownSets) {
  const setsWithPages = shownSets.filter((set) => set.ids.length > 0);
  const picks = [];
  const problems = [];

  for (const judge of judges) {
    const csv = await readFile(join("judging", judge, "picks.csv"), "utf8");
    const pickedBySet = new Map(
      csv
        .trim()
        .split("\n")
        .slice(1)
        .map((row) => row.split(",").map((cell) => cell.trim())),
    );

    for (const set of setsWithPages) {
      const pickedId = pickedBySet.get(set.set) ?? "";
      if (!set.ids.includes(pickedId)) {
        problems.push(`${judge}, ${set.set}: "${pickedId}" is not in the set`);
        continue;
      }
      picks.push({ judge, set: set.set, pickedId });
    }
  }

  if (problems.length > 0) {
    throw new Error(`Fix the picks first:\n${problems.join("\n")}`);
  }
  return picks;
}

// A run the plan's limit stopped is neither valid nor failed: it waits for
// the runner's next start (skill-blind-test.md section 4). Each script of the
// bench stands alone, so this function is also in blind-pages.mjs.
function assertNoRunAtLimit(records) {
  const waiting = records.filter((record) => record.status === "limit");
  if (waiting.length > 0) {
    const runIds = waiting.map((record) => record.runId).join(", ");
    throw new Error(
      `Start run-arms.mjs again first: ${runIds} stopped at the plan's limit.`,
    );
  }
}

// One model and one Claude Code version across all valid runs, or the arms
// did not run under the same conditions. The effort is the runner's own
// constant: the init event does not report it (skill-blind-test.md section 4).
function assertOneSetup(records) {
  const finals = records
    .filter((record) => record.status === "valid")
    .map((record) => record.attempts.at(-1));

  for (const field of ["model", "claudeCodeVersion"]) {
    const values = new Set(finals.map((attempt) => attempt[field]));
    if (values.size > 1) {
      throw new Error(`Runs differ in ${field}: ${[...values].join(", ")}`);
    }
  }
}

function winsRows({ arms, briefs, key, picks, records, shownSets, bench }) {
  const counts = {
    key,
    picks,
    records,
    shownIds: new Set(shownSets.flatMap((set) => set.ids)),
    pageById: new Map(key.map((page) => [page.id, page])),
    // Every judge was asked for one pick per run number of every brief.
    picksAsked: bench.judges.length * bench.runsPerArm,
    runsAsked: bench.runsPerArm,
  };
  return briefs.flatMap((brief) =>
    arms.map((arm) => rowFor(arm, brief, counts)),
  );
}

function rowFor(arm, brief, counts) {
  const isThisRun = (record) =>
    record.briefId === brief.id && record.armName === arm.name;
  const isThisPage = (page) =>
    page.briefId === brief.id && page.arm === arm.name;
  const runs = counts.records.filter(isThisRun);
  const pages = counts.key.filter(isThisPage);

  return {
    arm: arm.name,
    brief: brief.id,
    wins: counts.picks.filter((pick) =>
      isThisPage(counts.pageById.get(pick.pickedId)),
    ).length,
    picksAsked: counts.picksAsked,
    validRuns: runs.filter((record) => record.status === "valid").length,
    runsAsked: counts.runsAsked,
    contrastExits: pages.filter((page) => !counts.shownIds.has(page.id)).length,
    failedRuns: runs.filter((record) => record.status === "failed").length,
  };
}

function winsTable(rows) {
  const lines = rows.map(
    (row) =>
      `| ${row.arm} | ${row.brief} | ${row.wins} | ${row.picksAsked} | ` +
      `${row.validRuns} / ${row.runsAsked} | ${row.contrastExits} | ` +
      `${row.failedRuns} |`,
  );
  return [
    "| Arm | Brief | Wins | Picks asked | Valid runs / runs asked " +
      "| Left the pick on contrast | Failed runs |",
    "|---|---|---|---|---|---|---|",
    ...lines,
  ].join("\n");
}

// An arm beats no skill when its wins, summed over briefs and judges, are more
// than the no-skill arm's (skill-blind-test.md section 7).
function totalsTable(rows, arms) {
  const totalOf = (armName) =>
    rows
      .filter((row) => row.arm === armName)
      .reduce((sum, row) => sum + row.wins, 0);
  const baseline = arms.find((arm) => arm.skill === null);
  const baselineWins = totalOf(baseline.name);
  const picksAsked = rows
    .filter((row) => row.arm === baseline.name)
    .reduce((sum, row) => sum + row.picksAsked, 0);

  const lines = arms
    .filter((arm) => arm.skill !== null)
    .map((arm) => {
      const wins = totalOf(arm.name);
      const verdict = wins > baselineWins ? "yes" : "no";
      return (
        `| ${arm.name} | ${wins} | ${baselineWins} | ${picksAsked} ` +
        `| ${verdict} |`
      );
    });
  return [
    "| Arm | Wins, all briefs | No-skill wins | Picks asked | Beats no skill |",
    "|---|---|---|---|---|",
    ...lines,
  ].join("\n");
}

async function readJson(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

await main();
```

Why it is good: it checks for one pick per judge and set, each naming a page of that set, before it
counts anything, and divides by the picks asked for, never by the pages that came back
([evals.md](../../python/evals/evals.md) section 6). Each arm's failed runs and contrast exits sit
beside its wins, so an arm that often failed cannot look like a strong one. The decision rule of
[skill-blind-test.md](skill-blind-test.md) section 7 is code, written before the run, and the count
stops when a run still waits at the plan's limit, or when the valid runs differ in model or Claude
Code version.

## The results table

`results.md`, as it stays until the bench has run.

```markdown
# Results: blind test of design skills

**Not run yet.** No run has happened, and every table below is empty. Fill it in from the bench's
own records, never from memory.

## Setup

| Item | Value |
|---|---|
| Dates of the runs | |
| Claude Code version, from the runs' records | |
| Model and effort | claude-opus-5-5, high |
| Playwright and @axe-core/playwright | 1.64.1 and 4.14.0 |
| puppeteer-core, as npm installed it | |
| Runs per arm and brief | 2 |
| Judges: how many, and how many designers | |
| What the pilot settled, by step (skill-blind-test.md section 4) | |

## Arms

| Arm | Commit tested | What the pilot showed |
|---|---|---|
| no-skill | none | |
| frontend-design | | |
| hallmark | | |
| taste-skill | | |
| impeccable | | |
| ui-ux-pro-max | | |
| taste-skill-classics | | |
| huashu-design | | |

## Photos

| Brief | File | Source | Licence |
|---|---|---|---|
| | | | |

## Wins per arm per brief

| Arm | Brief | Wins | Picks asked | Valid runs / runs asked | Left the pick on contrast | Failed runs |
|---|---|---|---|---|---|---|
| | | | | | | |

## Against no skill

| Arm | Wins, all briefs | No-skill wins | Picks asked | Beats no skill |
|---|---|---|---|---|
| | | | | |

## What the winners share

Not run yet.

## Limits seen in this run

Not run yet.
```

Why it is good: it records what makes the result checkable later, the versions, the commits, the
photos with their licences, and what the pilot settled, beside the two tables `count-wins.mjs`
prints in the same columns. It keeps the wins next to the failed runs and the contrast exits, and
it says plainly that nothing has run.
