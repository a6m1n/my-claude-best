# The skill test result: a personal opinion

**Personal opinion, not a rule.** This page records one test of design skills, run by the
author of this library and judged by the same person. The scores say how much one person liked each page, not how good a skill is in
general. Nothing in the other files of this practice rests on this page, and no rule here comes
from it.

**Navigation**

- [How far to trust it](#how-far-to-trust-it)
- [What ran](#what-ran)
- [How it was run](#how-it-was-run)
- [Results](#results)
- [Notes per skill](#notes-per-skill)
- [taste-skill and taste-skill-classics are two skills](#taste-skill-and-taste-skill-classics-are-two-skills)
- [What I want from a design after this test](#what-i-want-from-a-design-after-this-test)
- [Sources](#sources)

## How far to trust it

This test answered the question it was run for: which design skill to use. It is one person's
taste on one brief, with one run per skill (the next two sections), so read the scores as that
person's ranking. A reader with a different product or a different taste may rank the same pages
in another order.

## What ran

Eight arms got the same brief: seven design skills and one run with no skill, as the baseline. The
brief was the landing page of a small software company, with its copy given in full. Each arm then
had the same three follow-up sessions with my feedback: a second screen (an AI app that answers
questions over documents and shows its sources and its reasoning), a round to simplify, and a
theme change. Each arm ran on Claude Opus 5.5 at medium effort, with its skill copied from the
skill's own repository at one pinned commit: taste-skill [1], taste-skill-classics [2], hallmark
[4], huashu-design [5], ui-ux-pro-max [6], frontend-design [7] and impeccable [8]. The scores and
the notes below are from my look at the pages after those four sessions, the same for every arm.
An earlier, quicker look, mostly at the landing pages, gave the "First look" column.

## How it was run

- **Names visible, skills new.** I saw which skill made each page, but I had not used or read
  any of these skills before, so a name told me nothing about what to expect.
- **One judge, no designer,** one brief, one run per skill.
- **The brief fixed the copy and the section titles,** word for word. That alone explains much
  of what the first look showed: many pages had the same sections with the same titles.
- **No photos.** The brief had none, so every arm worked without them.
- **The runs used my own Claude Code login, not a token**.
- **Requests between sessions.** Every arm had three follow-up sessions on my requests before
  the scores, so the pages are not what a skill builds alone from the brief.
- **Only the two winners went on, after the scores.** hallmark and taste-skill-classics then got
  seven more sessions (eleven in all, the last one not finished), the later ones at high effort
  with subagents and web tools. Every skill of the test, and other skills not about design, were
  copied into those two runs, and both called the `impeccable` skill. Those later pages are not
  the work of one skill, and they were not scored.

## Results

Sorted by score.

| Skill | First look | Score | In one line |
|---|---|---|---|
| taste-skill-classics | Top | 9/10 | Beautiful motion and transitions; the dark theme hurts readability |
| hallmark | Top | 8/10 | Clean and calm; the best at showing which claims are weakly supported |
| taste-skill | Good | 7/10 | A good app with a nice way to move between sources; the landing page is overloaded |
| huashu-design | Top | 6/10 | The best landing page and hover animation; a weak app screen |
| ui-ux-pro-max | Boring | 5/10 | Too simple, looks like 2010 |
| frontend-design | So-so | 5/10 | Boring, odd colours, looks dated |
| no skill (baseline) | Good | 5/10 | Fine at first look; on a closer look too many colours and too much detail |
| impeccable | not looked at | 4/10 | Not a modern style, and it does not fit the topic |

My two clear favourites: taste-skill-classics and hallmark.

The scores hide how the field looked. Many skills in the middle gave almost the same design,
and the differences between them were small: a colour here, a section order there. The real gap
was at the edges: the winners stood clearly above everyone else, and the losers clearly below.
Even the baseline with no skill landed in the middle group. So in this test the choice of skill
mattered when it picked a winner or avoided a loser; inside the middle group it changed little.

## Notes per skill

### taste-skill-classics — 9/10

My top pick in both looks. The animations are the best of the set: smooth, and every move from
one state to the next looks good. The panel that shows the steps of answer generation is well
built. Weak spots: the italic type is beautiful but hard to read, and it may not fit a 2026 AI
product. Text on the black background is hard to read, and a light theme would help. The
reasoning view shows too many details.

### hallmark — 8/10

A good font and a simple, clean design. The hover animation is nice but could go further. The
app screen is clean and readable, and the interface is not overloaded. It is the best at
marking grounding: it highlights only the sentences that need attention, while fully supported
text stays plain. Weak spot: hiding and showing the steps and the reasoning is not clear and not
easy to use.

### taste-skill — 7/10

The app is good and easy to use. I liked how it moves between sources: click a citation at the
end of the answer, and the sources show at the top. The landing page feels overloaded and needs
work, and I am not sure about the colours.

### huashu-design — 6/10

The best landing page of the set, with the best first animation and the best hover effects. One
landing section felt useless. The app screen pulls the score down: a long bar of scores is an awkward choice, and the sentence highlights are too bright. A plus: the
reasoning is short.

### ui-ux-pro-max — 5/10

Very simple, even boring: it looks like 2010, not like a modern product. I wanted more animation
and something more interesting. Its colours are better than hallmark's, though.

### frontend-design — 5/10

At first it looked fun, but something was off: the colours, or the layout of the content. On the
closer look it read as boring and dated, with odd colours that all look the same.

### No skill (baseline) — 5/10

A good result at first look. On the closer look it dropped to the middle: too much detail in the
reasoning and too many colours in the interface.

### impeccable — 4/10

Not a modern style, and the design does not fit the topic.

## taste-skill and taste-skill-classics are two skills

The names are close, but these are two skills by the same author, from two repositories.

**taste-skill** is `design-taste-frontend`, version 2. Its README says it "is built from a study
of 247 curated sites" and runs in six steps: a script deals three of 20 researched directions,
the agent picks one, builds with real pictures from open collections, checks the page in a real
browser, then "Looks at its own screenshots and fixes the top three problems, up to three
rounds" [1]. It needs Node 22 or newer and Chrome, Edge or Chromium [1]. The arm ran the skill at the commit in Sources.

**taste-skill-classics** holds the skills taste-skill shipped before version 2; its README says
they "moved here in October 2026" [2]. This arm ran one of them, `high-end-visual-design` (the
folder `soft-skill`), which the README sums up as "Calm, polished UI: soft contrast, whitespace,
spring motion" [2]. It is one `SKILL.md` of 99 lines and no scripts: a list of banned fonts, icons, shadows, layouts and motion, then one look and one layout to pick, all inside an
"Apple-esque / Linear-tier" design language [3]. It is opt-in: "an agent never picks one by
itself, it runs only when you call it by name" [2].

So taste-skill is a heavy process with research, real pictures and a browser check, and the
classic skill is a short style guide with strict bans and a focus on motion. In this test the
short one scored higher.

## What I want from a design after this test

These are my preferences, not rules; the rules on how a screen looks and behaves are in
[visual-design.md](visual-design.md) and [ux.md](ux.md).

- A modern, intuitive interface. I like Apple's style: clean and clear.
- A hover animation on the landing page catches the visitor best; huashu-design did it best.
- Smooth moves from one state to the next make a product feel finished (taste-skill-classics).
- In an AI answer, mark at once the sentences that are not supported or only partly supported,
  and leave the rest plain (hallmark did this best).
- When a source opens, show whether it supports the sentence at the top, before the text.
- Keep the reasoning short. Several pages showed too many details.
- Readability before style: no hard-to-read italics, no low-contrast text on black, and a light
  theme on offer.

## Sources

Checked 2026-11-08 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Leonxlnx — taste-skill, README.md, at commit 12af471 — https://github.com/Leonxlnx/taste-skill/blob/12af471f627f866411b4bd785b19646d3672784c/README.md
- [2] Leonxlnx — taste-skill-classics, README.md, at commit 5e08c93 — https://github.com/Leonxlnx/taste-skill-classics/blob/5e08c9383dc4ad7fc0df70e1ac8cfa09ec356305/README.md
- [3] Leonxlnx — taste-skill-classics, skills/soft-skill/SKILL.md (`high-end-visual-design`), at commit 5e08c93 — https://github.com/Leonxlnx/taste-skill-classics/blob/5e08c9383dc4ad7fc0df70e1ac8cfa09ec356305/skills/soft-skill/SKILL.md
- [4] Nutlope — hallmark, skills/hallmark, at commit 8f6969f — https://github.com/Nutlope/hallmark/tree/8f6969f8922caabde9de1784959eae11ddf68073/skills/hallmark
- [5] alchaincyf — huashu-design, at commit 4fc7bfd — https://github.com/alchaincyf/huashu-design/tree/4fc7bfdbd5ec3fa2d43ce7a6433de60976a5e4b1
- [6] nextlevelbuilder — ui-ux-pro-max-skill, .claude/skills/ui-ux-pro-max, at commit 28b3b8d — https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/28b3b8dee8c976df4fa3e94aed4e092ad43fcb03/.claude/skills/ui-ux-pro-max
- [7] Anthropic — anthropics/skills, skills/frontend-design, at commit 41bbe19 — https://github.com/anthropics/skills/tree/41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f/skills/frontend-design
- [8] Paul Bakaus — impeccable, .claude/skills/impeccable, at commit 5e745ac — https://github.com/pbakaus/impeccable/tree/5e745ace7e151feb2a93d360d0281fe39448b857/.claude/skills/impeccable
