# Rules for brand pages built with Claude Code

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. What is known](#2-what-is-known)
- [3. Fix the direction before the code](#3-fix-the-direction-before-the-code)
- [4. Name the defaults to avoid, each with a replacement](#4-name-the-defaults-to-avoid-each-with-a-replacement)
- [5. Real content: copy, photos and fonts](#5-real-content-copy-photos-and-fonts)
- [6. Build the hero first, then one section at a time](#6-build-the-hero-first-then-one-section-at-a-time)
- [7. Check the render](#7-check-the-render)
- [8. Where a skill keeps its rules](#8-where-a-skill-keeps-its-rules)
- [9. Common mistakes](#9-common-mistakes)
- [10. Where it stops holding](#10-where-it-stops-holding)
- [11. Alternatives considered](#11-alternatives-considered)
- [12. Review checklist](#12-review-checklist)
- [13. Sources](#13-sources)

## 1. Purpose and the one rule

This file is for everyone who builds a brand page with Claude Code: a landing page, a launch page,
a pricing page, a portfolio or the site of a local business, written mostly in HTML and CSS,
sometimes in React. People and agents read it before they ask Claude Code for such a page, before
they add a design skill for one, and when they review one. The outcome it aims at is a page that
does not look like the model's default and still meets the floors every page meets.

Brand pages are in brand mode: what that mode changes, and which floors still hold on it, are
[visual-design.md](visual-design.md) sections 2 and 12. The spec, the brief and the verify loop
for any screen are [designing-with-claude-code.md](designing-with-claude-code.md) sections 3, 4
and 6; this file adds what a brand page needs on top of them. How each design skill sets a
direction is [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 8, and whether
any skill beats no skill on your own briefs is [skill-blind-test.md](skill-blind-test.md). Images
and fonts on the first screen are [performance.md](../performance/performance.md) section 5.
[brand-direction-example.md](brand-direction-example.md) shows a direction file, its theme file
and the brief that points to both.
Distrust a line that carries a read date six months after that date, until it is read again; the
README's "How to adopt" says how to list those lines.

The one rule: **a person fixes the page's direction from the brand's own material before the
model writes code, and someone other than the author judges the page from its render.**

Why:

- The model has a default look, and adjectives do not move it off. Anthropic's `frontend-design`
  skill lists five such looks and calls them "defaults rather than choices, and they appear
  regardless of subject" [1]. Becker holds that "Your adjectives select a region of the
  distribution. The prior fills in everything you did not say, and the unsaid is most of the
  design" [2].
- The author is a poor judge of its own page. In Anthropic's long runs, "agents reliably skew
  positive when grading their own work" [3], and a Claude Code user reports Claude taking a
  screenshot, looking "at it at thumbnail size", and saying "all looks good" when the page was
  broken [4].

When you do not need all of it:

- **The brand already has a style guide and a theme.** They are the direction: skip the direction
  step of section 3, point the brief at them, and keep sections 4 to 7.
- **A designer drew the page.** The design file is the direction and the designer is the reviewer
  ([designing-with-claude-code.md](designing-with-claude-code.md) section 9).
- **A prototype you will throw away.** The separate reviewer is ceremony there (the same section
  9); the direction and the screenshots still save rounds.

How sure the evidence is: no study with human raters has tested any method in this file on brand
pages. Most studies below used a model as the judge, and most practitioners' reports are one
person's runs, judged by that person. Section 2 says who judged each result, and section 10 lists
what the research did not find.

## 2. What is known

Read this before you trust a claim about a design skill or a method for brand pages. Each row says
who judged the result: people, a model, a script, or the author of the report.

| Claim | What was found (read 2026-10-29) | Who judged | Kind |
|---|---|---|---|
| A design skill makes the page better | No test with human raters was found. The one model-judged test and the reviews that ran several skills are [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 3 | a model; the authors of each review | research; cases |
| The model falls back on a few default looks | `frontend-design` names five: cream with a serif display face and a terracotta accent; near-black with one acid-green or vermilion accent; a broadsheet layout; a kit of SaaS cards; template chrome such as tracked capital labels, middle-dot strings, monospace labels and arrows [1]. funboy322's catalogue adds what comes after a ban: "warm cream with a terracotta accent, or near-black with one acid-green signal, all-caps monospace labels, one colored word in the headline, features numbered 01 / 02 / 03" [8]. A Hacker News post names a "Cream canvas", "Cobalt or Terracotta ink" and a "Mono font" [9] | nobody measured it | the skill's own text; opinions |
| A ban with no replacement moves the model to the next default | Wiegold reports that "once you tell it to avoid Inter, it converges on Space Grotesk across every generation" [10]. Becker holds that "Negative constraints work better than positive ones" [2]. Neither tested it. In WebDev-Skills-Bench, rules that name anti-patterns were the one part of a skill with a reliable effect, but on code conventions, in five skill-project pairs [11] | the authors; tests of function, not of looks | opinions; research |
| Reference screenshots steer the page | In RefCraft, the best model scored 52.1 of 100 with its reference screenshots and 17.3 without; the score measures how closely the page follows the references, not how good it looks [12] | a model judge, checked against ten web developers on 100 pages | research |
| A plan does more than a review | MM-WebAgent's full system won 78.99% of human comparisons, against other systems, not against its own parts. In its ablation, planning raised the score from 0.42 to 0.66 and reflection then to 0.75, but the planning gain came from generated images and video, while the layout and style scores fell [13] | 50 people for the win rate; a model for the ablation | research |
| A critic that sees the render helps | Sansford et al.'s figures are the critic row of [designing-with-claude-code.md](designing-with-claude-code.md) section 2. Xiong et al., on copying a target screenshot, found that a model refining its own page with no rubric fell below its first attempt, and that one repair target per round reduced this for three frontier models but not for Qwen models [15] | a model, in both | research |
| About three render-and-fix rounds are enough | Guo et al. found that three rounds gave 95.3% of the gain, on a score that mixes correct interaction with visual similarity to a site being copied [16]. Anthropic's evaluator ran 5 to 15 rounds, and its author often preferred "a middle iteration over the last one" [3] | a model; the author | research; case |
| A skill's rules in other files reach the page | The counts, for one small skill not about design and for Hallmark on Haiku 4.5, are [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 5 | file reads counted; a script of regular expressions | research |
| The hero first, then one section at a time | No measurement. Hallmark builds and reviews the hero first [19]; two builders report the same order [20], [21] | nobody | skill text; cases |

Claude Code's best-practices page names "A browser screenshot next to the mockup" as a check Claude
can run [22]. Read on 2026-10-29, the page no longer gives a prompt that lists the differences
and fixes them.

## 3. Fix the direction before the code

- **Before any code, have three or more directions made, and let a person pick one.** A model
  asked to pick goes to its default: taste-skill's own script says "a model asked to pick a
  direction returns the category default every time" [23]. Warren's team offered a client
  "three different stylistic options" as style tiles [24]; Becker asks for five and drops the
  most conventional one [2]. [designing-with-claude-code.md](designing-with-claude-code.md)
  section 4 gives the same step for a screen whose look is open; a new brand page with no style
  guide is open.
- **Make each direction one concrete world from the brand's own material, in one sentence, and
  make the directions differ on purpose,** so the person chooses between worlds, not between
  shades of one. Impeccable asks for "seven concrete visual systems, artifacts, places, or rituals
  the audience knows by heart" before it builds [25], and its live mode calls three variants
  on one axis a failure [26]. Wiegold builds a prompt from "purpose, tone, font category,
  colour family, motion philosophy" [10]: those five describe a direction before any value
  is fixed.
- **Show each direction small: a tile with the colours, the faces, one button and one photo.**
  Warren holds that "presenting multiple, fully visualized comps hurts the process more than it
  helps it", because a client mixes them into a "Frankencomp" [24]. When the tiles do not
  settle it, build only the hero in each direction: Lukyanenko reports, from his own redesign, that
  "It is faster to compare three concrete implementations than to describe an abstract preference
  in words" [27].
- **Write the picked direction into a direction file, and its values into the theme file.** The
  direction file holds the direction in one sentence, the brand values it starts from, each
  colour role with where it is used, the type roles, the motion, where photos and fonts come
  from, 3 to 5 do-nots each with its replacement (section 4), and a log of each build. Hallmark's
  theme files, such as `dusk.md`, hold tokens, type, surfaces, motion, voice and do-nots, and the
  seven of them that were read carry 3 to 5 do-nots each [28].
  The values go in the theme file the build reads, so the model and the build see one set
  ([designing-with-claude-code.md](designing-with-claude-code.md) section 3); as roles
  ([visual-design.md](visual-design.md) section 3), with each pair's contrast computed
  ([visual-design.md](visual-design.md) section 4). The brief names both files.
- **Pin exact values only where the brand already has them; every other value becomes exact when a
  person picks the direction.** A brand's real values (its logo colour, its licensed face, its
  photos) go into the theme file as they are. Mejba Ahmed keeps them in a folder for Claude Code,
  because without that "you'd be correcting branding inconsistencies in every single prompt" [21],
  and `frontend-design`'s own plan step asks for "4–6 named hex values" [1]. Values made up for a
  prompt before anyone chose a direction are what Wiegold calls "technically correct and visually
  dead" [10], so the direction comes first. A pinned value is only as good as the choice behind it:
  Mejba Ahmed's sample instruction file pins Space Grotesk and Inter [21], and other sources name
  both as defaults (Space Grotesk [10], [29]; Inter in
  [designing-with-claude-code.md](designing-with-claude-code.md) section 4).
- **Name no other product as the look to follow. When a reference helps, give screenshots and name
  the one thing to take from them,** so the page borrows a quality and stays the brand's own. At
  Banani, a prompt built on Airbnb's design file gave screens "so spot on one can mistake it as
  Airbnb UI altogether", with Airbnb's own tokens in the generated config [30]. In Kilo's test, a
  landing-page prompt that said "The page should feel like Linear, or Stripe tier polish" got a
  headline with one word, "compound", set as "an italicized serif accent", one of the default tells,
  so the named products did not keep the page off the defaults either [31]. References do steer:
  RefCraft's models followed them closely [12], and Becker asks to "Replace adjectives with
  artifacts" [2]. Take the one thing (the rhythm of the sections, the density of a price list) from
  more than one site, and let the reviewer ask whether the page could pass for any of them (section
  7). The tokens still come from the brand.

  Copying a site's own HTML, CSS and JavaScript, Chase Hannegan's clone method, is a study
  exercise, not a way to build the page you ship. He writes "The goal isn't to plagiarize", calls
  the clone "just the training exercise", and says "You can't republish someone else's site as your
  own, obviously" [32]. Code pasted in from another site is text from outside the project, and
  an agent can follow instructions hidden in what it reads
  ([agent-containers.md](../../any-language/docker/agent-containers.md) section 1).

Check: before the first build, does the direction file give each colour role a place where it is
used, and does every do-not have its replacement?

## 4. Name the defaults to avoid, each with a replacement

The general list of looks that generated UI falls into is the table in
[designing-with-claude-code.md](designing-with-claude-code.md) section 4, and section 3 of that
file asks for an "instead" next to each thing to avoid. The defaults that sources named for pages
(read 2026-10-29):

| Default | Named by |
|---|---|
| A cream page, a serif display face and a terracotta accent | `frontend-design` [1]; funboy322 [8]; a Hacker News post, with cobalt as the other ink [9] |
| A near-black page with one acid-green or vermilion accent | `frontend-design` [1]; funboy322 [8] |
| A broadsheet layout; a kit of SaaS cards | `frontend-design` [1] |
| Template chrome: a tracked capital label above each heading, middle-dot strings, monospace labels, arrows | `frontend-design` [1]; the Hacker News post, for the monospace font [9] |
| One word of the headline in another colour or in italics | `frontend-design` [1]; funboy322 [8] |
| Features numbered 01 / 02 / 03 | funboy322 [8] |
| Space Grotesk, once Inter is banned | Wiegold [10] |
| Fraunces, Inter as a display face, Space Grotesk, Playfair Display; Instrument Serif with Geist | huashu-design's list of overused faces [29] |

- **Before the build, write 3 to 5 do-nots into the direction file, each naming a default exactly
  and what the page does instead.** Pick the defaults this direction is closest to; a warm,
  editorial direction is one step from the cream-and-serif look. The Hallmark theme files that were
  read carry 3 to 5 do-nots each [28], and funboy322's 67 tells are a catalogue for review, not a
  list for one brief [8]. The replacement matters because a ban alone sends the model to the next
  default: Wiegold's Inter became Space Grotesk [10], and funboy322 describes "the *next* same page"
  [8].
- **Use options at the direction step and named bans at the build step.** Becker holds both: ask
  for several directions, and use negative constraints, because "they carve away the
  highest-probability region" [2]. huashu-design went the other way, and in its third round
  "switched to more options instead of more bans" [33]; section 11 says why this file keeps
  the bans.
- **After each build, add the default the page fell into to the do-nots, with its replacement,**
  the method the Opus 5.5 guide gives for screens
  ([designing-with-claude-code.md](designing-with-claude-code.md) section 4).
- **Log the faces, the palette and the layout each build used, and name them as defaults in the
  next page's brief.** A list of replacement faces becomes the next default once every page uses
  it. huashu-design keeps such a log, so that "every delivery logs what it looked like" and the
  next one differs [33]; Hallmark's script skips the themes of its last three builds
  [34]. The log is a short part of the direction file.

## 5. Real content: copy, photos and fonts

- **Give the model the page's real words before it builds.** Writing the words first is
  [designing-with-claude-code.md](designing-with-claude-code.md) section 4's rule for any screen. On
  a brand page the missing words are claims, logos and quotes: in one review, the page built with
  no skill carried fake customer logos and a testimonial, and they stayed after Impeccable's audit
  and polish [6].
- **Use the client's own photos first.** Hallmark asks for them, and until they come, "without
  photos I place stand-ins from Hallmark's photo library that your own replace later"
  [19].
- **A person picks and clears every photo the page uses; the agent never fetches photos from a
  stock site by script,** because the limits of the licences need a person's eye:
  - Unsplash's licence allows commercial use "without permission from or attributing the
    photographer or Unsplash" [35], but it "does not include the right to use:
    Trademarks, logos, or brands visible in an image / Recognizable people in an image / Works of
    art or other copyrighted material depicted in an image" [36]. Its API terms ask
    more: "The API is to be used for non-automated, high-quality, and authentic experiences", the
    page must use the "hotlinked image URLs returned by the API", each download is reported, and
    Unsplash and the photographer get a credit with a link [37].
  - Pexels' licence and API page were read only through a fetch tool's summary: the licence asks
    no credit, and the API asks for a prominent link to Pexels and a credit to the photographer
    where possible [38], [39]. Check both on the live pages before you rely on them.
  - On Wikimedia Commons, what you owe depends on each file's licence, and "commercial use of
    images of people may require the explicit agreement of the subject" [40].
  - Hallmark avoids stock sites, saying their terms "bar AI tools from picking their images"
    [41]. That is Hallmark's claim; the Unsplash terms read here say
    "non-automated", not "AI".
- **Before the page ships, check that every image and video URL loads.** CodeVertex55's skill does
  it as a rule: "Every link is fetched and seen to load before it is used" [42]. Image
  sizes and loading on the first screen are [performance.md](../performance/performance.md)
  section 5, and the text alternative is [accessibility.md](accessibility.md) section 12.
- **Choose the type by content, language and tone first, then the face; use one family, or two
  faces by one designer.** huashu-design decides the content type, the language mix and the tone,
  and names the face last [29]. Butterick holds that "Mixing fonts is never a
  requirement—it’s an option", and that one method "works reliably: combine fonts by the same font
  designer" [43]; he is a type designer who sells fonts, and writes about documents. For
  running text, Shoaf looks for "a body face with a large x-height, low contrast and included
  italics" [44]. A serif display face over a sans body is not a default: it is the first look
  `frontend-design` names [1], and huashu-design lists it as one of three sources of contrast,
  not as its default, with a note in its CSS template not to fill in a serif by default
  [29].
- **Before a face ships, read its licence for four things: web use, hosting the files yourself,
  changing the files, and credit.** Google Fonts' own README says "It is important to always read
  the license for every font that you use" [45].

  | Licence | Web use and your own hosting | Changing the files | Credit |
  |---|---|---|---|
  | SIL Open Font License, used by most Google Fonts families [45] | Yes: "The referenced fonts can be hosted on the same server as other site assets and content" [46] | Allowed; a changed font stays under the OFL and may not use a Reserved Font Name [46], [45] | Not required [46] |
  | Fontshare's ITF Free Font License, version 2.0 of 17 August 2026 | Yes, for personal or commercial use, self-hosting included [47] | Not allowed, including "subsetting, format conversion"; no redistribution, which covers a public repository [47] | Optional [47] |
  | Collletttivo, all under the OFL | As the OFL | As the OFL | Asked: "remember to credit the original designer and the foundry" [48] |
  | Velvetyne, all libre | Yes, "for all personal and commercial works" [49] | Allowed [49] | Required: "you must credit the name of the type designer and of our foundry" [49] |
  | A paid web licence, such as Klim's | Only for "the Domain specified on Your Sales Receipt", under a page-view cap, with Klim's own WOFF2 files [50] | Only as the licence allows | As the licence says |

  The OFL FAQ answers "Can I make webpages using these fonts? Yes!" and allows the fonts "for any
  kind of design work"; it never uses the word "commercial" for websites [46]. Some Fontshare
  faces are under the OFL instead, so the licence goes by face [47]. Velvetyne was read in
  an archived copy of 2026-09-24, because the live site showed a strike notice [49].
  [performance.md](../performance/performance.md) section 5 serves fonts as WOFF2 only; under a
  licence that forbids format conversion, take the WOFF2 files the foundry ships.

  Check: before you commit a font file to a public repository, find the line of its licence that
  allows redistribution.

## 6. Build the hero first, then one section at a time

- **Build the navigation and the hero first, have them reviewed, then build the sections one at a
  time, each checked before the next.** The hero sets the faces, the colours and the rhythm the
  sections repeat, so a mistake caught there is fixed once. Hallmark writes "the nav and the hero,
  nothing below them yet" and reviews the hero in a fresh context before any section
  [19]. Stuart advises "Create the hero, then tackle the rest section by section"
  [20], and Mejba Ahmed builds "referencing one section at a time", with a screenshot after
  every major section [21]. No source measured the order.
- **One skill that sets the look at a time:**
  [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 4. Which skill to choose is
  section 8 of the same file.

When the page moves on its own or on scroll:

- **Take the durations, the curves, the properties to animate and the reduced-motion path from
  [visual-design.md](visual-design.md) section 8;** brand mode lets motion be more visible
  ([visual-design.md](visual-design.md) section 2).
- **Keep every section's content visible when its animation does not run.** A reveal that starts
  from a hidden state leaves the text hidden when the reduced-motion path is broken; MengTo's
  motion playbook asks to "Test with prefers-reduced-motion: reduce turned on before calling any
  animation done" for that reason [52].

  Check: with `prefers-reduced-motion: reduce` on, does every section's text show?

## 7. Check the render

The loop, the reviewer other than the author, the written checklist and the round cap are
[designing-with-claude-code.md](designing-with-claude-code.md) section 6. A brand page adds these:

- **Screenshot the first screen and the full page at a phone, a tablet and a desktop width, after
  the fonts and images have loaded.** Hallmark's final reviewer gets the first screen at three
  desktop sizes and the full page at 1440 and 375 pixels [53], and taste-skill shoots
  "three widths" [54]. A screenshot seen at thumbnail size hides what is broken [4].
- **Stop CSS animations for the screenshots, and leave the motion they cannot stop to a person.**
  Playwright's `animations: "disabled"` "stops CSS animations, CSS transitions and Web Animations"
  [55]. A canvas, a video or motion driven by a script is not on that list. Mejba Ahmed's
  loop spent "twenty minutes trying to 'fix' the particles because every screenshot looked
  different", and his answer was to "Disable the screenshot loop for animated component
  integration. Review those manually" [21]. A person scrolls the finished page on a phone for
  scroll feel and motion, and runs the manual pass of [accessibility.md](accessibility.md) section
  11.
- **Give the reviewer the direction file, the do-nots and the screenshots, in a fresh context, and
  ask for one verdict first.** Hallmark's final reviewer sees the screenshots, the page source and
  the theme file, and its first line is one word: recapture, rebuild, fix or ship
  [53]. The reviewer is not the author: Anthropic's author found that "agents reliably
  skew positive when grading their own work" [3], and Claude Code's `/code-review` "reviews
  the diff in a fresh subagent that never saw your conversation" [22]. The gain Sansford et
  al. measured came from a critic call that saw only the render, with the same model as the
  builder [14].
- **Put two questions on the reviewer's checklist: could this page pass for another product's
  site, and would it fit any business in its category as it is?** The first keeps a reference
  from turning into a copy (section 3). The second is funboy322's test of a template, whether you
  would have made the page for any similar one [8], and Impeccable's "the page this category
  always ships" [25].
- **Write the checklist as what fails, with no praise words in it.** In Anthropic's case,
  "Including phrases like "the best designs are museum quality" pushed designs toward a particular
  visual convergence" [3].
- **When a round of fixes leaves the page worse, go back to the better round and fix one checklist
  item at a time.** Xiong et al. found that refining with no rubric fell below the first attempt,
  and that one repair target per round reduced the fall for three frontier models, though not for
  Qwen models; the task was copying a screenshot, judged by a model [15]. Keeping each round's
  screenshots is [designing-with-claude-code.md](designing-with-claude-code.md) section 6's rule.
- **Keep the round cap of [designing-with-claude-code.md](designing-with-claude-code.md) section 6
  as a cost limit.** Guo et al.'s three rounds were measured on copying a site, with a score that
  mixes interaction and looks [16], and Anthropic's evaluator ran 5 to 15 rounds [3], so
  the cap is not a measured best for brand pages.

## 8. Where a skill keeps its rules

Read this when you write or adapt a skill for brand pages, or a brief that points to a direction
file.

- **Put the rules that must hold, such as the do-nots and the order of the steps, near the top of
  `SKILL.md`,** because after a compaction Claude Code can keep only the start of an invoked skill
  [56]; the token budget is [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 5.
- **Point to every other file from `SKILL.md`, one level deep, and say when to read it.** In the
  one count, a file `SKILL.md` pointed to was read and a file it did not point to was not
  ([choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 5). Anthropic's skill guide asks to "Keep references one level deep from SKILL.md"
  [57]. A brief that names the direction file is the same kind of pointer; that it works
  the same way in a brief is this file's reading, not a test.
- **Choose a skill by how it sets the direction and checks the page,** as
  [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 8 compares them; what it runs
  on your machine is section 6 of the same file. Whether to install a skill or copy its parts into
  one of your own is decided by the blind test ([skill-blind-test.md](skill-blind-test.md) section
  7).

## 9. Common mistakes

| Mistake | What goes wrong | The fix | Sources |
|---|---|---|---|
| A brief of adjectives: "premium", "modern", "bold" | The model's default for the category | A direction picked by a person, in a direction file (section 3) | [2], [10] |
| A ban with no replacement | The next default (Inter became Space Grotesk) | Each do-not with what the page does instead (section 4) | [10], [8] |
| Another product named as the look | A page that passes for that product, or the defaults anyway | The brand's own tokens; a reference for one named thing (section 3) | [30], [31] |
| The author judging its own screenshots | "all looks good" on a broken page | A reviewer in a fresh context (section 7) | [4], [3] |
| A screenshot loop on an animated section | The loop chases a frame that changes on every shot | Animations stopped for screenshots; a person checks motion (section 7) | [21], [55] |
| Content hidden until an animation runs | Text that never shows under reduced motion | Content visible by default (section 6) | [52] |
| Photos fetched from a stock site by the agent | Logos, recognisable people or artworks the licence does not cover; API terms that ask for use that is not automated | Photos a person chose and cleared (section 5) | [36], [37] |
| A font file committed to a public repository, or subset, under a licence that forbids it | A licence breach anyone can see | The licence read for the four things (section 5) | [47] |
| The whole page asked for in one go | Every section needs fixing at once | The hero first, then one section at a time (section 6) | [20], [19] |
| A ban file that `SKILL.md` never points to | The rules never reach the page | A pointer to each file (section 8) | [18], [17] |
| Praise words in the reviewer's checklist | Pages pulled toward one look | A checklist of failures (section 7) | [3] |

The mistake this file adds for a brief, shown with its fix (the pair for a brief made of
adjectives is in [designing-with-claude-code.md](designing-with-claude-code.md) section 8). Bad —
the brief names another product as the look:

```text
Build the one-page site of Acme Corp, a bicycle repair workshop. Make it look like the Globex
site: the same clean style and the same polish.
```

The model either copies Globex's look, as at Banani, or falls back on its own defaults, as in
Kilo's test [30], [31]; in both cases the page is not the workshop's own (section 3).

Good — the part of the brief that sets the look, taken from the brand, with one named thing from
the references (the steps and the screenshots in `<references>` are cut):

```text
Build the one-page site of Acme Corp, a bicycle repair workshop. Follow docs/brand-direction.md
and take every colour, face and radius from the roles in src/styles.css. The screenshots in
<references> come from three sites; take one thing from them, the rhythm of a long page where each
section holds one idea and one photo, and nothing else.
...
```

Why it is good: the look comes from the direction file and the theme file, which hold the
brand's own values (section 3), so no product is named as the look. The references are named for
one quality and come from three sites, so the page is less likely to copy any one of them; the
reviewer's question in section 7 checks it. They are pasted in
a named tag, as [prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md)
section 5 asks for material put into a prompt. A whole brief of this kind, without references, is
in [brand-direction-example.md](brand-direction-example.md).

## 10. Where it stops holding

- **A page inside an established brand system.** Its tokens, faces and rules are the direction;
  section 3's direction step is done, and sections 4 to 7 still hold.
- **An application screen.** It is in product mode ([visual-design.md](visual-design.md) section
  2), and [designing-with-claude-code.md](designing-with-claude-code.md) owns its loop. Naming the
  defaults with their replacements and checking the render help there too.
- **A page built before this file.** It keeps its look until a change restyles it; that change
  writes the direction file first ([refactoring.md](../../any-language/refactoring/refactoring.md)
  section 2).
- **Security.** What a skill runs on your machine is
  [choosing-tools-and-skills.md](choosing-tools-and-skills.md) section 6 and
  [designing-with-claude-code.md](designing-with-claude-code.md) section 7; a third-party script
  on the page is [security.md](../security/security.md) section 12; another site's code pasted into
  the agent is text from outside the project (section 3).
- **Moving targets.** Model defaults, skills and licence pages change within months: the defaults
  table in section 4 and the licence table in section 5 carry their read date, and Fontshare's
  licence changed to version 2.0 in August 2026 [47].

Not covered yet, because the research found no source:

- A test with human raters of any design skill, or any method here, against none on brand pages;
  [skill-blind-test.md](skill-blind-test.md) describes one to run.
- Whether the rules in a design skill's reference files reach the page on Opus or Sonnet: the one
  measurement used a small skill not about design [17], and the design skill was measured
  on Haiku only [18].
- How alike AI-built sites are. OpenSkillEval plots how varied the styles of skills are against no
  skill [5]; its values for web design were not read.
- The page speed of AI-built pages with scroll effects or a video hero: no Core Web Vitals study
  was found.
- Whether references or templates raise expert-rated quality: RefCraft measures how closely a page
  follows its references, not how good it is [12].
- Whether the build order changes the result: no measurement was found.
- Whether a page that follows another site's look closely breaks that site's rights: no legal
  source was read.
- The consent of people in the client's own photos: no source on it was read.
- Pexels' licence and API terms in their own text: read only through a summary.

## 11. Alternatives considered

- **Bans only.** taste-skill's v2 adds "scripts that check the page in a real browser and fail it
  until the rules pass" [58]. Not taken alone: a ban with no replacement moves the model
  to the next default [10], so each ban here carries its replacement, and the direction step
  gives options.
- **Options only, no bans.** huashu-design "switched to more options instead of more bans" [33]. Not
  taken: Becker holds that negative constraints "work better" [2], and WebDev-Skills-Bench found
  anti-pattern rules the one reliable part of a skill, on code [11]. The options stay, at the
  direction step.
- **Principles only, never exact values.** Wiegold holds that rigid specs are "technically correct
  and visually dead" [10]. Kept at the direction step; after the pick, the values are exact,
  because the model owner's guides ask for concrete values
  ([designing-with-claude-code.md](designing-with-claude-code.md) section 4) and Becker asks for
  tokens [2].
- **Brand values in every prompt.** Mejba Ahmed pins them in the instruction file [21]. The
  values stay, in the theme file the build reads, so they are never typed twice
  ([designing-with-claude-code.md](designing-with-claude-code.md) section 3).
- **The builder reviews its own screenshots.** taste-skill does, on the reasoning "Use it on the
  screenshots, never on the code: you wrote the code, so you will read your intentions into it"
  [59]; Stuart's builder scores itself until it reaches 9 [20]. Not taken: the
  author skews positive [3], and a thumbnail check missed a broken page [4].
- **Several full built versions to pick from.** Lukyanenko built three [27]. Not the
  default: Warren warns that full comps get mixed into a "Frankencomp" [24], so tiles come
  first and built heroes only when the tiles do not decide.
- **A serif display face over a sans body as the default pairing.** Not taken: it is the first
  default `frontend-design` names [1], and huashu-design itself treats it as one choice among
  three [29].
- **A fixed list of replacement faces.** Not taken: a list every page follows becomes the next
  default [10], [8]; the log of faces used (section 4) takes its place.
- **Keeping the screenshot loop on animated sections.** Not taken: the loop stuck for twenty
  minutes on a moving frame [21].
- **Naming a real product, or cloning its site.** Banani's and Kilo's tests [30], [31],
  and DESIGN.md files "extracted from real websites" [60], show the pull of a named
  look. Not taken for a page you ship; the clone stays a study exercise in a scratch project, as
  its author frames it [32].
- **More review rounds.** Anthropic's evaluator ran 5 to 15 [3]. The cap of
  [designing-with-claude-code.md](designing-with-claude-code.md) section 6 stays, as a cost limit.
- **Generated images and video as the page's assets.** MM-WebAgent's planning gain came from them
  [13]. Not the default here: a page about a real business shows its own photos (section 5);
  whether generated assets help a brand page was not researched.
- **A structured `DESIGN.md` in Google Labs' format,** "A format specification for describing a
  visual identity to coding agents" [61]. Not required: a direction file in plain Markdown
  that names the roles, with the values in the theme file, gives the model the same facts; a team
  that already uses the format may keep it.

## 12. Review checklist

One question per section. A red flag that fails a floor of [visual-design.md](visual-design.md)
section 12 means the page is not ready; raise any other with the author before the page ships.

| Section | Ask | Red flag |
|---|---|---|
| 3. The direction | Did a person pick the direction from several, and do its values come from the brand or from that pick? | Another product named as the look; tokens nobody chose; no direction file |
| 4. The defaults | Does every do-not have its replacement, and does the page show none of them? | A ban with no "instead"; a default from section 4's table on the page; no log line for the build |
| 5. Real content | Are the words, photos and faces real, cleared, and credited where the licence asks? | Placeholder copy or invented logos; a stock photo with a logo or a recognisable person and no release; a font file in a public repository under a licence that forbids it |
| 6. The build | Was the hero reviewed before the sections, and does every section show with reduced motion on? | Text that appears only after an animation |
| 7. The render | Did someone other than the author give the verdict, from screenshots at every width with animations stopped? | The author's review only; one width; a loop left running on an animated section |
| 8. The skill | Does `SKILL.md` keep the rules that must hold at its top and point to every file it needs? | A ban file nothing points to |

## 13. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Anthropic — anthropics/skills, `frontend-design` SKILL.md — https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md
- [2] Sascha Becker — Same same but different (personal blog, 2026; opinion) — https://saschb2b.com/blog/same-same-but-different
- [3] Prithvi Rajasekaran — Harness design for long-running apps (Anthropic Engineering, 2026; case, by the model's vendor) — https://www.anthropic.com/engineering/harness-design-long-running-apps
- [4] A Claude Code user — Claude repeatedly fails to verify visual output and iterates through broken states instead of matching references (GitHub, anthropics/claude-code issue 46009, 2026; case) — https://github.com/anthropics/claude-code/issues/46009
- [5] Jiahao Ying et al. — OpenSkillEval: Automatically Auditing the Open Skill Ecosystem for LLM Agents (arXiv:2605.23657 v2, 2026; research) — https://arxiv.org/abs/2605.23657
- [6] Paralect — Top design skills for Claude Code in 2026, tested side by side (Paralect site, 2026; case) — https://www.paralect.com/skills/top-design-skills
- [8] funboy322 — avoid-ai-design, README and references/ai-tells-catalog.md (GitHub, 2026; opinion) — https://github.com/funboy322/avoid-ai-design
- [9] Hacker News commenters — Color palette gives away AI slop (Hacker News item 48269907, 2026; opinion) — https://news.ycombinator.com/item?id=48269907
- [10] Thomas Wiegold — How to Use the Claude Code Frontend-Design Plugin to Stop Shipping AI Slop (personal blog, 2026; opinion) — https://thomas-wiegold.com/blog/claude-code-frontend-design-plugin/
- [11] Ziyue Yang and Fan Ding — Signal or Noise? A Benchmark Study of Agent Skills in Web Development (arXiv:2608.23067 v1, 2026; research) — https://arxiv.org/abs/2608.23067
- [12] Yuchi Wang et al. — RefCraft: Benchmarking Visual-Reference-Conditioned Agentic Generation through Web Development (arXiv:2610.26826 v1, 2026; research) — https://arxiv.org/abs/2610.26826
- [13] Yan Li et al. — MM-WebAgent: A Hierarchical Multimodal Web Agent for Webpage Generation (arXiv:2604.15309 v1, 2026; research) — https://arxiv.org/abs/2604.15309
- [14] Hannah Sansford et al. — Vision-Guided Iterative Refinement for Frontend Code Generation (arXiv:2604.05839 v1, 2026; research) — https://arxiv.org/abs/2604.05839
- [15] Tianyi Xiong et al. — Rubrics as Visual-Repair Context for Self-Evolving UI-to-Code Generation (arXiv:2608.24138 v1, 2026; research) — https://arxiv.org/abs/2608.24138
- [16] Yilong Guo et al. — Rendering-in-the-Loop: An Execution-Driven Agent for Interactive Web Development (arXiv:2609.02088 v1, 2026; research) — https://arxiv.org/abs/2609.02088
- [17] rulestack — 13 of 16 Claude Code runs loaded the skill script (DEV Community, 2026; research) — https://dev.to/rulestack/13-of-16-claude-code-runs-loaded-the-skill-script-the-docs-call-executed-not-loaded-5cic
- [18] ktlesr — skill-trigger-measurements, reports/hallmark.ablation.md (GitHub, 2026; research) — https://github.com/ktlesr/skill-trigger-measurements
- [19] Nutlope — hallmark, skills/hallmark/SKILL.md — https://github.com/Nutlope/hallmark/blob/main/skills/hallmark/SKILL.md
- [20] Danny Stuart — Workflow: Build immersive websites with Midjourney + Claude (Substack, 2026; case) — https://dannystuart.substack.com/p/workflow-build-immersive-websites
- [21] Mejba Ahmed — Claude Code professional website hacks (personal blog, 2026; case) — https://www.mejba.me/blog/claude-code-professional-website-hacks
- [22] Anthropic — Claude Code docs: Best practices for Claude Code — https://code.claude.com/docs/en/best-practices
- [23] Leonxlnx — taste-skill, skills/taste-skill/scripts/draw.mjs, v2.1.5 — https://github.com/Leonxlnx/taste-skill/blob/main/skills/taste-skill/scripts/draw.mjs
- [24] Samantha Warren — Style Tiles and How They Work (A List Apart, 2012; opinion) — https://alistapart.com/article/style-tiles-and-how-they-work
- [25] Paul Bakaus — Impeccable, reference/new-work.md, version 4.8.0 — https://github.com/pbakaus/impeccable/blob/main/.claude/skills/impeccable/reference/new-work.md
- [26] Paul Bakaus — Impeccable, reference/live.md, version 4.8.0 — https://github.com/pbakaus/impeccable/blob/main/.claude/skills/impeccable/reference/live.md
- [27] Andrey Lukyanenko — Redesigning my personal website (personal blog, 2026; case) — https://andlukyane.com/blog/redesigning-my-personal-website
- [28] Nutlope — hallmark, skills/hallmark/references/themes/dusk.md — https://github.com/Nutlope/hallmark/blob/main/skills/hallmark/references/themes/dusk.md
- [29] alchaincyf — huashu-design, references/typography.md — https://github.com/alchaincyf/huashu-design/blob/master/references/typography.md
- [30] Vlad Solomakha — Fable 5 for UI & Frontend is the Final Boss of AI for UI (Banani blog, 2026; case, by the vendor of a competing design tool) — https://www.banani.co/blog/fable-5-ui-and-frontend-design
- [31] Darko Gjorgjievski — We Asked GPT-5.5 and Claude Opus 4.7 to Design 5 UIs (Kilo blog, 2026; case, by the vendor of the harness used) — https://blog.kilo.ai/p/we-asked-gpt-55-and-claude-opus-47
- [32] Chase Hannegan — How to Clone a $100K Website in 15 Minutes With Claude Code (Chase AI blog, 2026; case) — https://chaseai.io/blog/clone-100k-website-15-minutes-claude-code
- [33] alchaincyf — huashu-design, README.en.md, v3.0.0 — https://github.com/alchaincyf/huashu-design/blob/master/README.en.md
- [34] Nutlope — hallmark, skills/hallmark/scripts/theme.mjs, v2.0.0 — https://github.com/Nutlope/hallmark/blob/main/skills/hallmark/scripts/theme.mjs
- [35] Unsplash — License (read in a Wayback copy of 2026-10-23) — https://unsplash.com/license
- [36] Unsplash Help Center — What if there is a brand/logo in an image on Unsplash? — https://help.unsplash.com/en/articles/14224409-what-if-there-is-a-brand-logo-in-an-image-on-unsplash
- [37] Unsplash Help Center — Unsplash API Guidelines — https://help.unsplash.com/en/articles/2511245-unsplash-api-guidelines
- [38] Pexels — License — https://www.pexels.com/license/
- [39] Pexels — API documentation — https://www.pexels.com/api/documentation/
- [40] Wikimedia Commons — Commons:Reusing content outside Wikimedia — https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia
- [41] Nutlope — hallmark, README, v2.0.0 — https://github.com/Nutlope/hallmark/blob/main/README.md
- [42] CodeVertex55 — ui-design-skill, README — https://github.com/CodeVertex55/ui-design-skill
- [43] Matthew Butterick — Mixing fonts, Practical Typography (personal site, no date; opinion) — https://practicaltypography.com/mixing-fonts.html
- [44] Jeremiah Shoaf — Five Fresh Headline & Body Text Pairings on Google Fonts (Typewolf, 2016; opinion) — https://www.typewolf.com/blog/google-fonts-combinations
- [45] Google — google/fonts, README — https://github.com/google/fonts/blob/main/README.md
- [46] SIL International — OFL FAQ, OFL-FAQ 1.1-update7 — https://openfontlicense.org/ofl-faq/
- [47] Indian Type Foundry — Fontshare: ITF Free Font License, Version 2.0 of 17 August 2026 — https://www.fontshare.com/licenses/itf-ffl
- [48] Collletttivo — Licensing — https://www.collletttivo.it/licensing
- [49] Velvetyne — FAQ and About (read in a Wayback copy of 2026-09-24) — https://velvetyne.fr/about/faq/
- [50] Klim Type Foundry — Web Font Licence Agreement — https://klim.co.nz/licences/web-fonts/
- [52] MengTo — Cinematic GSAP + Lenis Motion System (Claude Code HQ, 2026; opinion) — https://www.claudecodehq.com/playbooks/cinematic-gsap-lenis-motion-system
- [53] Nutlope — hallmark, skills/hallmark/references/review-finish.md — https://github.com/Nutlope/hallmark/blob/main/skills/hallmark/references/review-finish.md
- [54] Leonxlnx — taste-skill, skills/taste-skill/SKILL.md (`design-taste-frontend`), v2.1.5 — https://github.com/Leonxlnx/taste-skill/blob/main/skills/taste-skill/SKILL.md
- [55] Microsoft — Playwright docs: Page.screenshot — https://playwright.dev/docs/api/class-page#page-screenshot
- [56] Anthropic — Claude Code docs: Skills — https://code.claude.com/docs/en/skills
- [57] Anthropic — Claude Platform docs: Agent Skills best practices — https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- [58] Leonxlnx — reply in taste-skill issue 106 (GitHub, 2026; opinion) — https://github.com/Leonxlnx/taste-skill/issues/106
- [59] Leonxlnx — taste-skill, skills/taste-skill/references/critique.md, v2.1.5 — https://github.com/Leonxlnx/taste-skill/blob/main/skills/taste-skill/references/critique.md
- [60] VoltAgent — awesome-design-md, README — https://github.com/VoltAgent/awesome-design-md
- [61] Google Labs — design.md, README — https://github.com/google-labs-code/design.md
