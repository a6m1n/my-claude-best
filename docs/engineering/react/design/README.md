# Design practices

How a screen of a React application should look and behave, the accessibility floor it has to
meet, and how to design it with Claude Code: the product and brand modes with the tokens and scales
behind them, how much expression a screen carries, the feedback and states a user sees, native
elements and focus, and, for every screen an agent builds, a concrete spec, a way to see the result
and a reviewer other than the author. It also covers how to pick the tool and the skill for a design
job, how to get a brand page from Claude Code that does not look like the model's default, and how
to test design skills blind on your own briefs.

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)

**When you do not need all of it.** Each file says where its rules are too much, in its section on
where it stops holding: [visual-design.md](visual-design.md) section 12, [ux.md](ux.md) section 10,
[accessibility.md](accessibility.md) section 13,
[designing-with-claude-code.md](designing-with-claude-code.md) section 9,
[choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 10,
[brand-pages.md](brand-pages.md) section 10 and [skill-blind-test.md](skill-blind-test.md)
section 10.

## What is here

- [visual-design.md](visual-design.md) — how a screen looks: the product and brand modes, how much
  expression a product screen carries (effective, polished or a balance), the tokens, the scales,
  and tables of visual styles and of what the owners say by use case. Read it before you choose or
  change how a screen looks, or add a token.
- [ux.md](ux.md) — how a screen behaves: feedback, loading, forms, errors and empty states. Read
  it before you design what a screen does while it waits, when it fails, or when it takes input.
- [accessibility.md](accessibility.md) — the standard, native elements, ARIA patterns, focus,
  announcements, the automated checks and the manual pass. Read it before you build or review a
  control or a screen.
- [designing-with-claude-code.md](designing-with-claude-code.md) — what is known and what is not
  about designing with a model, the spec the model reads, the brief for one screen, the tools with
  their status and a trust note each, the verify loop with its cap, and the common mistakes. Read
  it before you ask Claude Code for a screen, before you add a design tool or plugin, and when you
  review a screen Claude Code built.
- [choosing-tools-and-skills.md](choosing-tools-and-skills.md) — how to pick the way to run a
  design job by what it must leave (a Figma file, a canvas, code in the repository, a polish pass)
  and the gates your account has to pass; what is known about design skills, how to call one and
  check that it ran, what each runs on your machine, and which to choose for application screens and
  for brand pages. Read it before you set up a canvas, Figma or a browser tool for a design job, and
  before you install or call a design skill.
- [brand-pages.md](brand-pages.md) — how to get a landing or marketing page from Claude Code that
  does not look like the model's default: the direction before the code, the defaults to avoid with
  a replacement each, real copy, photos and fonts with their licences, the build order and the
  render check. Read it before you ask Claude Code for a brand page.
- [skill-blind-test.md](skill-blind-test.md) — how to test design skills against no skill on your
  own briefs, with the pages judged blind by people: the arms, the bench, the headless runs, the
  screenshots, the pick, and when the result justifies a skill of your own. Read it before you adopt
  a design skill for a team, or when you want to know whether one helps.
- [design-brief-example.md](design-brief-example.md) — one worked case, the invoices screen: the
  design lines of `CLAUDE.md`, the brief, the reviewer's checklist, and the code that meets them,
  with the reason next to each part. Read it when you write a brief or a checklist for a new
  screen.
- [brand-direction-example.md](brand-direction-example.md) — one direction file for a brand page and
  the brief that points to it. Read it when you fix the direction of a new brand page.
- [blind-test-example.md](blind-test-example.md) — the files of one test bench: the briefs, the
  runner, the screenshot and contrast script, the blind key and the judging sheet. Read it when you
  set up the blind test.

How to tell whether a screen works for the people who use it, and what to measure once it is live,
is the [ux-evaluation](../../any-language/ux-evaluation/README.md) practice.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/react/design/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you design or restyle a screen of a
   React application, add a control, a form or a route to one, ask an agent to build a screen or a
   brand page, pick, install or call a design skill or a design tool, or review such a change, read
   `docs/engineering/react/design/README.md` and the file it routes to for that work, and
   `docs/engineering/react/design/design-brief-example.md` when you write the brief for a screen,
   `docs/engineering/react/design/brand-direction-example.md` when you fix the direction of a brand
   page, `docs/engineering/react/design/blind-test-example.md` when you set up a blind test of
   design skills. The check: every colour, radius and space the change adds is a token role, a step
   of the scale or one of the two exceptions (`visual-design.md` sections 3 and 6), the closing
   summary says which steps of the manual accessibility pass were run (`accessibility.md` section
   11), someone other than the author of the screen answered its review checklist
   (`designing-with-claude-code.md` section 6), and every design skill a run uses is called by name
   and shown loaded in that run (`choosing-tools-and-skills.md` section 5)." Without it an agent
   never opens the folder. How to write such a line is
   [claude-md.md](../../../claude-code/claude-md.md#how-to-write-a-line-an-agent-can-follow).
3. Use the review checklist that closes each rules file as the design part of your review
   template, so a reviewer asks the same questions every time.
4. The files link other practices for the rules those own. Run
   `grep -rhoE '\]\(\.\./[^)#]+' docs/engineering/react/design/ | sort -u` to print every link
   that leaves this folder. Copy each folder or file it names, or replace each link with your own
   rule for that topic.
5. Re-check the lines that name a moving target. Tools and model guides change within months: in
   the six months before these files were read, a design tool went from research preview to beta,
   a new canvas command shipped, and a component library changed its default base. So:
   - before you install or rely on a tool, re-read the source of its row in
     designing-with-claude-code.md section 5; before you install or call a design skill, re-read the
     source of its row in choosing-tools-and-skills.md sections 6 to 8;
   - when the project moves to a new Claude model, read that model's prompting guide for a design
     section and update the per-model table in designing-with-claude-code.md section 2;
   - six months after the date a line was read, re-read it. Each such line, or the header of its
     table, carries the date it was read;
     `grep -rnE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' docs/engineering/react/design/` lists them, and the
     date alone is the pattern, so a date wrapped onto the next line after the word "read" is still
     found. It also lists other dates, such as a release or a closing date, which you skip. The six
     months is this practice's choice, from how fast the tools above changed. Distrust each such
     line six months after the date on the line until you have read it again. The rules files with
     a Sources section that opens `Checked <date>` date their sources there.

## The points to adapt

- **The look.** The token values, the brand and the component base are yours; the rules on modes
  and token roles are in [visual-design.md](visual-design.md) sections 2 and 3.
- **The tools.** Which browser tool, which canvas, and whether Figma is in the loop depend on your
  plans and seats; [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 2 picks the
  way, and section 5 of designing-with-claude-code.md names the gate on each tool.
- **The expression.** Effective, polished or a balance for your product and its users;
  [visual-design.md](visual-design.md) section 2 gives the default and section 10 what the owners
  say for your field.
- **The reviewer and the cap.** A person, a fresh-context subagent, or both; two review rounds or
  three.
- **Charts.** [visual-design.md](visual-design.md) sections 10 and 12 set the number of colours
  (four categories), a word on every status, and the 3:1 contrast of marks. Not covered yet: the
  values of a categorical palette, a chart library, and a chart palette for a dark theme. The line
  in section 12 points here.

What does not change is the one rule behind the folder's Claude Code file: the model gets a
concrete spec and a way to see the result, and a reviewer other than the author judges it.
