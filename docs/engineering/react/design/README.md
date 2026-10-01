# Design practices

How a screen of a React application should look and behave, the accessibility floor it has to
meet, and how to design it with Claude Code: the product and brand modes with the tokens and scales
behind them, the feedback and states a user sees, native elements and focus, and, for every screen
an agent builds, a concrete spec, a way to see the result and a reviewer other than the author.

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)

## What is here

- [visual-design.md](visual-design.md) — how a screen looks: the product and brand modes, the
  tokens, the scales, and a table of visual styles with their fit for an application. Read it
  before you choose or change how a screen looks, or add a token.
- [ux.md](ux.md) — how a screen behaves: feedback, loading, forms, errors and empty states. Read
  it before you design what a screen does while it waits, when it fails, or when it takes input.
- [accessibility.md](accessibility.md) — the standard, native elements, ARIA patterns, focus,
  announcements, the automated checks and the manual pass. Read it before you build or review a
  control or a screen.
- [designing-with-claude-code.md](designing-with-claude-code.md) — what is known and what is not
  about designing with a model, the spec the model reads, the brief for one screen, the tools with
  their status and a trust note each, the verify loop with its cap, and the common mistakes. Read
  it before you ask Claude Code for a screen, before you add a design tool, plugin or skill, and
  when you review a screen Claude Code built.
- [design-brief-example.md](design-brief-example.md) — one worked case, the invoices screen: the
  design lines of `CLAUDE.md`, the brief, the reviewer's checklist, and the code that meets them,
  with the reason next to each part. Read it when you write a brief or a checklist for a new
  screen.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/react/design/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you design, build or review a screen,
   read `docs/engineering/react/design/README.md` and the file it routes to for that work. The
   check: the closing summary names the files you read." Without it an agent never opens the
   folder. How to write such a line is
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
     designing-with-claude-code.md section 5;
   - when the project moves to a new Claude model, read that model's prompting guide for a design
     section and update the table in section 2 of the same file;
   - six months after the date a line was read, re-read it. Each such line, or the header of its
     table, carries the date 2026-10-01 or 2026-10-02; `grep -rnE '2026-10-0[12]' docs/engineering/react/design/`
     lists them, and the date alone is the pattern, so a date wrapped onto the next line after the
     word "read" is still found. The six months is this practice's choice, from how fast the tools
     above changed. Distrust every such line after 2027-04-01, six months after the reading, until
     you have read it again.

## The points to adapt

- **The look.** The token values, the brand and the component base are yours; the rules on modes
  and token roles are in [visual-design.md](visual-design.md) sections 2 and 3.
- **The tools.** Which browser tool, which canvas, and whether Figma is in the loop depend on your
  plans and seats; section 5 of designing-with-claude-code.md names the gate on each.
- **The reviewer and the cap.** A person, a fresh-context subagent, or both; two review rounds or
  three.
- **Charts.** A chart needs a categorical palette and its own contrast check, and this practice
  does not cover them yet. The line in [visual-design.md](visual-design.md) section 12 points here.

What does not change is the one rule behind the folder's Claude Code file: the model gets a
concrete spec and a way to see the result, and a reviewer other than the author judges it.
