# Example: the direction file for a brand page

A worked example for [brand-pages.md](brand-pages.md). Acme Corp, an invented bicycle repair
workshop, needs a one-page site: a cyclist opens it on a phone, sees what a repair costs, and books
one. The example shows what a person writes before Claude Code builds anything: the direction file,
the theme file that holds every value, and the brief that points to both, with the reason next to
each part. The site is a small React application with Tailwind CSS 4, the stack
[libraries.md](../architecture/libraries.md) section 2 picks. All names, values and photos are
invented.

The files the example touches:

```text
docs/
├── brand-direction.md   the direction: its sentence, the roles and where each is used, type, motion, do-nots, the log
└── page-copy.md         every word on the page and every photo's alt text (not shown)
public/photos/           the owner's photos (not shown)
src/
└── styles.css           the theme: every colour, face, radius and motion value, as roles
```

Why it is good: the look, the values and the words each live in one file, so the brief points to
each of them and no value is written twice. The theme file sits where
[architecture.md](../architecture/architecture.md) section 3 puts the stylesheet the build starts
from, and the two documents sit in `docs/`, as
[file-structure.md](../../any-language/file-structure/file-structure.md) section 9 lays out a
repository's root. The copy file and the photos are left out of the example; the brief names them.

## How the direction was picked

Before these files existed, a session made three directions from the workshop's own material, each
one sentence and one tile with its colours, faces, a button and a photo
([brand-pages.md](brand-pages.md) section 3):

1. The sign: a painted yellow board on a grey wall, lettered in a narrow sans.
2. The job card: a carbon-copy repair ticket, blue-black ink on white, with the total written by
   hand.
3. The tool wall: the outlines of tools on a brown pegboard, one bright colour for each kind of
   tool.

The owner picked the first, because the sign is what a cyclist already sees from the street.

Why it is good: the three directions differ in colour, in type and in texture at once, so the owner
chose between three worlds, not three shades of one. Each comes from something the workshop owns,
and none is one of the defaults in [brand-pages.md](brand-pages.md) section 4.

## The direction file: `docs/brand-direction.md`

```markdown
# Brand direction: Acme Corp bicycle repairs

The sign: a painted yellow board on a grey wall, lettered in a narrow sans.
Picked by the owner from three directions: the sign, the job card, the tool wall.

## Values that already exist
- The sign's yellow, matched by the owner to the paint the sign was painted with. It is the
  `signal` role in `src/styles.css`.
- The photos in `public/photos/`, taken by the owner. Their alt text is in `docs/page-copy.md`.

## Colour roles, and where each is used
| Role | Used for | Never for |
|---|---|---|
| `background` | the page behind every section but the hero | — |
| `foreground` | all text on `background`; links, which are also underlined | — |
| `muted-foreground` | photo captions and the note under a price, on `background` | — |
| `signal` | the hero band, and nothing else | a second band, a button, a link, an icon |
| `signal-foreground` | all text on the hero band | — |
| `primary`, `primary-foreground` | the one button, "Book a repair", in the hero and at the end of the page | any other control |
| `border` | the hairline between the rows of the price list | the only edge of a control |
| `ring` | the focus outline of every link and of the button | — |

## Type roles
| Role | Face and weight | Steps | Used for |
|---|---|---|---|
| display | Barlow Condensed 600 (`font-display`) | `text-5xl md:text-7xl` for the headline, `text-3xl md:text-4xl` for section headings | the headline and the section headings, in sentence case |
| body | Barlow 400 (`font-sans`) | `text-lg`, never wider than `max-w-prose` | running text |
| strong | Barlow 500 (`font-sans`) | `text-lg`, with `tabular-nums` on prices | prices and the button's label |

Faces: Barlow and Barlow Condensed, two widths of one family by one designer, under the SIL Open
Font License 1.1. Self-hosted as WOFF2 files, loaded as `performance.md` section 5 says.

## Motion
One motion: the button settles on press (`--motion-duration-press`, `--motion-ease-enter`).
Nothing moves on its own or on scroll. With reduced motion on, nothing moves at all.

## Do-nots, each with what the page does instead
- A cream or beige page with a serif display face -> the `background` grey and Barlow Condensed.
- A small capital label or a number such as "01" above a heading -> the heading alone, in
  sentence case.
- One word of the headline in another colour or in italics -> the whole headline in
  `signal-foreground` on the hero band.
- A grid of cards with an icon for each repair -> the price list: one row per repair, its price on
  the right, `border` between the rows.
- A stock photo -> one of the owner's photos; a section with no photo of its own gets none.

## Log
One line per build: the date, the faces, the roles used, the order of the sections, and the
default the page fell into, which also goes into the do-nots above.
- No build yet.
```

Why it is good:

- **The direction is one sentence about something the workshop owns,** so a reviewer can hold the
  page against it ([brand-pages.md](brand-pages.md) section 3).
- **Only the values the brand already had are pinned here as facts:** the sign's yellow and the
  owner's photos. Every other value came from the pick and lives in the theme file, so this file
  names roles and never repeats a value
  ([designing-with-claude-code.md](designing-with-claude-code.md) section 3).
- **Every colour role says where it is used, and the risky ones say where they are not.** `signal`
  stays on the hero band, so the page spends its boldness in one place
  ([visual-design.md](visual-design.md) section 12), and `border` is never a field's only edge
  ([visual-design.md](visual-design.md) section 7). The column of "never" is the line a copier
  would most likely drop, and it is what keeps the second yellow band out of the page.
- **The type roles use the stack's steps,** not sizes in brackets, and running text has a maximum
  width ([visual-design.md](visual-design.md) section 5). The faces are one family in two widths by
  one designer, Butterick's method ([brand-pages.md](brand-pages.md) section 5): Barlow and Barlow
  Condensed are both by Jeremy Tribby and both under the SIL Open Font License 1.1. The licence
  counts a change of format as a modified version and bars only a Reserved Font Name from one;
  neither family's copyright line names one, so a WOFF2 file converted from them may keep the
  name [1], [2]. These faces are this brand's choice, from its sign; copy the method, not the
  faces, or they become the next default ([brand-pages.md](brand-pages.md) section 4).
- **Five do-nots, each with its replacement on the same line.** The first four are defaults from
  [brand-pages.md](brand-pages.md) section 4's table; the fifth is section 5's rule on photos. Each replacement names a role or a part
  of this page, so the reviewer can check it.
- **The motion is one sentence, named by its tokens,** with the reduced-motion case stated, so
  nobody adds a scroll effect the direction did not choose.
- **The log has its form before the first build,** so the first build writes into it and the next
  brief can name what this one used ([brand-pages.md](brand-pages.md) section 4).

## The theme file: `src/styles.css`

The whole file, apart from the `@font-face` rules that load the two faces; those follow
[performance.md](../performance/performance.md) section 5 and are left out here.

```css
@import "tailwindcss";

/* Roles, not colours: a component names a role and this file supplies the value. Every surface
   role has a -foreground role that keeps text readable on it (visual-design.md section 3). */
:root {
  /* One theme. visual-design.md section 12 does not count two themes among the rules that still
     hold on a brand page; this line makes the browser draw its own parts in the light scheme. */
  color-scheme: light;

  --background: oklch(0.97 0.005 250);
  --foreground: oklch(0.23 0.012 250);
  --muted-foreground: oklch(0.46 0.012 250);
  /* Decorative: the hairline between price rows, never the only edge of a control
     (visual-design.md section 7). */
  --border: oklch(0.86 0.008 250);
  /* The sign's yellow, the one colour the brand already had (brand-pages.md section 3). Keep it:
     the page is meant to look like the sign. */
  --signal: oklch(0.86 0.165 92);
  --signal-foreground: oklch(0.23 0.012 250);
  --primary: oklch(0.23 0.012 250);
  --primary-foreground: oklch(0.97 0.005 250);
  --ring: oklch(0.23 0.012 250);

  /* Durations and curves are tokens (visual-design.md section 8): 100 ms is in the range for a
     press, and the curve decelerates into place. */
  --motion-duration-press: 100ms;
  --motion-ease-enter: cubic-bezier(0, 0, 0, 1);
}

@theme inline {
  /* Clearing the default palette leaves the roles below as the only colours, so a class such as
     bg-yellow-300 gives no style at all (visual-design.md section 3). */
  --color-*: initial;
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-muted-foreground: var(--muted-foreground);
  --color-border: var(--border);
  --color-signal: var(--signal);
  --color-signal-foreground: var(--signal-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-ring: var(--ring);

  /* Two widths of one family by one designer, so the page needs no second family
     (brand-pages.md section 5). */
  --font-display: "Barlow Condensed", ui-sans-serif, system-ui, sans-serif;
  --font-sans: "Barlow", ui-sans-serif, system-ui, sans-serif;

  /* The sign's square corners: one small radius, for the button. */
  --radius-control: 0.125rem;
}

@layer base {
  body {
    background-color: var(--background);
    color: var(--foreground);
  }
}

.press {
  /* The page's one motion. Only `transform`, listed, never `all` (visual-design.md section 8). */
  transition: transform var(--motion-duration-press) var(--motion-ease-enter);
}

.press:active {
  transform: scale(0.98);
}

@media (prefers-reduced-motion: reduce) {
  /* Drop the movement; there is no fade to keep (visual-design.md section 8). */
  .press {
    transition: none;
  }

  .press:active {
    transform: none;
  }
}
```

Why it is good:

- **A component sees only roles,** and `--color-*: initial` removes Tailwind's palette, so a raw
  colour gives no style and shows at once ([visual-design.md](visual-design.md) section 3). The
  comment keeps that reason at the line, because the line looks removable.
- **The one value the brand already had carries its origin at the line,** so the next editor does
  not "improve" the yellow; every other value came from the pick.
- **`primary` and `ring` hold the same graphite as `foreground`, under their own names,** because a
  role is picked by what it means ([visual-design.md](visual-design.md) section 3). A rebrand that
  changes the button changes one line.
- **The motion is two tokens and one listed property,** inside the duration range for a press, and
  the reduced-motion rule removes it ([visual-design.md](visual-design.md) section 8). The comment
  on `color-scheme` keeps the reason the page has one theme, which a copier would otherwise
  question.

## The contrast of each pair

Every pair the direction file allows, computed from the OKLCH values above with the WCAG 2 formula,
against the floors of [visual-design.md](visual-design.md) section 4:

```text
foreground on background             15.48  floor 4.5:1  ok
muted-foreground on background        6.52  floor 4.5:1  ok
signal-foreground on signal          11.00  floor 4.5:1  ok
primary-foreground on primary        15.48  floor 4.5:1  ok
primary on signal                    11.00  floor 3:1    ok   the button's edge on the hero band
primary on background                15.48  floor 3:1    ok   the button's edge at the end of the page
ring on background                   15.48  floor 3:1    ok
ring on signal                       11.00  floor 3:1    ok
border on background                  1.40  decorative, no floor
```

Why it is good: every text pair is held to 4.5:1, so it holds for body text as well as for the
headline. The button's edge and the focus ring are checked on both surfaces they sit on, the hero
band and the page, because a yellow band is where a dark ring could have vanished. `border` is
marked decorative, which matches its "never" in the direction file.

## The brief

The brief is one message: the steps below, then the checklist of the next section in its tag.

```text
Build the one-page site of Acme Corp, a bicycle repair workshop, at the route /. A cyclist opens
it on a phone to see what a repair costs and to book one. The steps are in the order the work
happens, and each ends with how anyone can tell it was done.

1. Before you write code, read docs/brand-direction.md, src/styles.css and docs/page-copy.md. The
   direction file is the look, the theme file holds every value, and the copy file holds every
   word and every photo's alt text. Check: your first message quotes the direction's sentence and
   lists its five do-nots.
2. When you pick a colour, a face or a radius, use a role from src/styles.css, in the place the
   direction file gives it. Check: every colour, font and radius class in the diff names one of
   these roles, or is one of the two exceptions of visual-design.md section 3.
3. Build the navigation and the hero first, nothing below them, with the photo
   public/photos/workshop-front.jpg at its own width and height (performance.md section 5). Then
   run step 5 for the hero. Check: the diff of this step adds no section below the hero.
4. When the hero has passed, build the sections in the order of docs/page-copy.md, one at a time,
   and run step 5 after each. Where your first idea is one of the do-nots in the direction file,
   do what its arrow says instead. Check: each section has its own round of screenshots.
5. Take screenshots with Playwright, with animations disabled (a moving frame differs on every
   shot), after the fonts and images have loaded: the first screen at 390, 768 and 1280 pixels
   wide, and the full page at 390 and 1280. Name each for its round, part and width, such as
   round-1-hero-390.png. Then start a reviewer subagent with a fresh context. Give it steps 1 to 6
   of this brief in <brief>, docs/brand-direction.md in <direction>, the diff in <diff>, the
   screenshot file names in <screenshots> and the checklist in <review_checklist>. Act on its
   first word. Check: after the second review of the same part, stop and send me the screenshots
   and every item still open.
6. When the page is done, add a line to the log of docs/brand-direction.md: the date, the faces,
   the roles used, the order of the sections, and any default the page fell into, with that
   default added to the do-nots. Check: the log has one new line.
```

Why it is good:

- **The goal comes first, then the steps in the order the work happens,** each with its moment,
  its act and how anyone can tell it was done
  ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 2;
  [designing-with-claude-code.md](designing-with-claude-code.md) section 4).
- **It points to the direction file, the theme file and the copy file instead of repeating
  them,** so each requirement is written once
  ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 9),
  and a pointer is what gets a file read ([brand-pages.md](brand-pages.md) section 8). Step 1's
  check shows that the model read the direction before it wrote code.
- **The hero comes first and is reviewed before any section,** and each section gets its own
  round ([brand-pages.md](brand-pages.md) section 6).
- **The screenshots are taken with animations disabled, after loading, at a phone, a tablet and a
  desktop width** ([brand-pages.md](brand-pages.md) section 7). The reason sits in brackets at the
  step, since "animations disabled" is the part a reader would drop.
- **The reviewer has a fresh context, the direction, the diff, the screenshots and a checklist,
  answers with one word first, and the loop stops after two reviews of a part**
  ([designing-with-claude-code.md](designing-with-claude-code.md) section 6;
  [brand-pages.md](brand-pages.md) section 7). Each piece it gets sits in a named tag
  ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 5).
- **The last step writes the log,** so the next page's brief can name this page's faces and
  layout as defaults ([brand-pages.md](brand-pages.md) section 4).

## The reviewer's checklist

The brief ends with this block:

```text
<review_checklist>
Read the diff first, then the screenshots. Your first line is one word: rebuild, fix or ship.
Then report only the items the page fails, each with a file and line or a screenshot name.

In the code:
1. Roles: every colour, font and radius class names a role from src/styles.css, in the place
   <direction> gives it. Fails on a palette class, a value in brackets, or signal outside the
   hero band.
2. Words: every visible word and every alt text is from docs/page-copy.md. Fails on any other,
   such as an invented quote or a customer logo.
3. Motion: only the button moves, on press, and nothing moves under reduced motion. Fails on any
   other transition or animation.

In the screenshots:
4. Do-nots: none of the do-nots in <direction> shows. Fails when one does.
5. Its own page: the page could not pass for another business's site, and would not fit any
   bicycle workshop as it is. Fails when it could.
6. Coverage: every width that step 5 of <brief> names, for the part under review. Fails when one
   is missing.
</review_checklist>
```

Outside the checklist, and not for the subagent: before the page ships, a person scrolls it on a
phone and runs the manual pass of [accessibility.md](accessibility.md) section 11.

Why it is good:

- **The code comes first, then the screenshots,** as
  [designing-with-claude-code.md](designing-with-claude-code.md) section 6 orders a model reviewer.
- **Each item says when it fails, and the checklist holds no praise words,** so the reviewer
  reports facts a person can check and is not pulled toward one look
  ([brand-pages.md](brand-pages.md) section 7).
- **Item 5 asks [brand-pages.md](brand-pages.md) section 7's two questions:** could the page pass
  for another site, and would it fit any business of its kind.
- **The checks a subagent cannot make stay with a person:** scroll feel on a real phone and the
  manual accessibility pass.

## What was verified, and what was not

- The contrast ratios were computed with a short python3 script from the OKLCH values, with the
  WCAG 2 formula. The same script gives 17.59, 7.30 and 1.39 for three pairs whose ratios
  [visual-design.md](visual-design.md) section 4 publishes, so its conversion matches that file's.
  Every value above is inside the sRGB gamut.
- The designer and the licence of Barlow and Barlow Condensed were read in the Google Fonts
  repository on 2026-10-29 [1], [2].
- Not run: the brief, the build, Tailwind's build of this theme, and the page in a browser.

## Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Google — google/fonts, `ofl/barlow`: METADATA.pb and OFL.txt — https://github.com/google/fonts/tree/main/ofl/barlow
- [2] Google — google/fonts, `ofl/barlowcondensed`: METADATA.pb and OFL.txt — https://github.com/google/fonts/tree/main/ofl/barlowcondensed
