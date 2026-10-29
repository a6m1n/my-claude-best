# Visual design rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. Product mode and brand mode](#2-product-mode-and-brand-mode)
- [3. Tokens: tiers, roles and pairs](#3-tokens-tiers-roles-and-pairs)
- [4. Colour and contrast](#4-colour-and-contrast)
- [5. Type](#5-type)
- [6. Spacing, layout and density](#6-spacing-layout-and-density)
- [7. Shape, borders and elevation](#7-shape-borders-and-elevation)
- [8. Motion](#8-motion)
- [9. Themes: light and dark](#9-themes-light-and-dark)
- [10. Design styles and their fit](#10-design-styles-and-their-fit)
- [11. Common mistakes](#11-common-mistakes)
- [12. Where it stops holding](#12-where-it-stops-holding)
- [13. Review checklist](#13-review-checklist)
- [14. Sources](#14-sources)

## 1. Purpose and the one rule

This file is for everyone who designs, builds or reviews a screen of a React application: people
and AI coding agents alike. Read it before you choose a colour, a size, a font, a radius, a shadow
or an animation for a screen, and when you review one.

It is about how a screen looks. How a screen behaves (feedback, forms, empty states) is
[ux.md](ux.md) sections 2, 4 and 6. The accessibility floor, with the standard behind the numbers
quoted here, is [accessibility.md](accessibility.md) sections 2 and 9. How to get a coding agent to
follow this file is [designing-with-claude-code.md](designing-with-claude-code.md) sections 3 and 4.
Where the token file sits in the tree is [architecture.md](../architecture/architecture.md)
section 3.
Distrust a line that carries a read date six months after that date, until it is read again; the
README's "How to adopt" says how to list those lines.

The one rule: **an application screen is designed in product mode, and every visual value on it
comes from a token or a scale (section 3 names two exceptions), never from one screen's taste.**
Each section below is one part of that rule, or one way it breaks.

Why:

- The owners of four large design systems, IBM's Carbon, Atlassian's, Vercel's Geist and GitHub's
  Primer, each keep the look of a task screen apart from the look of a marketing page (section 2).
  A task screen that borrows the marketing look gets type, motion and decoration that pull the eye
  away from the task.
- A value chosen for its meaning survives a second theme and a rebrand. A value chosen because it
  looks right today does not: Atlassian warns that a token picked only because its colour looks the
  same can break the screen in another theme.
- A generated screen drifts to the model's current default look unless something concrete pins it
  down (section 11). The token file is that concrete thing: an agent reads it, and a reviewer
  checks the screen against it.

The examples come from one invented application, the billing screens of Acme Corp, built with
React 19 and Tailwind CSS 4 (versions read 2026-10-01). The blocks quoted from the application were
type-checked, linted, unit-tested and built. The blocks that are not from it say so where they
stand: the motion and reduced-motion CSS in section 8 and the theme switch in section 9; the
application has one motion, the loading spinner, and no switch yet. Nothing was run in a browser.
The contrast numbers in section 4 were computed from the token values with the WCAG 2 formula, not
measured on a screen.

What the research did not settle (layout density, fields, banking, dark themes for code, motion
between screens, a regulator's guidance, education systems, Salesforce's AppExchange, chart palettes
for a dark theme, and one thing per page for expert users) is listed in section 12, under "Not
covered yet".

## 2. Product mode and brand mode

Before you design a screen, name its mode. Product mode is for a screen where a user does a task:
a list, a form, a settings page, a dashboard. Brand mode is for a page that sells or tells a
story: a landing page, a launch page, a pricing page. A screen behind the login is in product
mode, and that is the case this file is written for.

Four owners draw the same line, each in their own words:

| Owner | Product mode | Brand mode | What the owner says |
|---|---|---|---|
| IBM Carbon | productive | expressive | The productive type set is "primarily used within product spaces, where users benefit from a more condensed treatment of content to maintain focus on tasks". The expressive set suits "editorial and marketing design… but would be distracting if used in product". Motion is split the same way. |
| Atlassian | in-app | brand | A custom brand font for marketing; Atlassian Sans and Atlassian Mono "for all in-app experiences". The larger heading sizes are for marketing. |
| Vercel Geist | the app | marketing and hero areas | One type scale with the split inside it: copy sizes 24, 20 and 18 are "primarily for marketing and hero areas"; copy-14 and label-14 are the sizes used most. |
| GitHub Primer | Primer Product | Primer Brand | Two design systems; Primer Brand is "for creating marketing websites and digital experiences". The split is stated; rules per mode were not found. |

What the mode changes:

| Part | Product mode | Brand mode |
|---|---|---|
| Type | a compact scale, most text at 14 px (Geist); the in-app face (Atlassian) | the larger steps of the scale; a brand face; more dramatic type (Carbon, Atlassian, Geist) |
| Motion | "subtle and out of the way", for when the user must focus on a task (Carbon) | "enthusiastic, vibrant, and highly visible", kept for "significant moments" (Carbon) |
| Density | dense and quiet: Linear keeps "rich density of information without letting the interface feel overwhelming" | more room around fewer things |
| Shape and depth | small radii; little or no shadow on surfaces in the page (Geist) | not stated by the owners read |

A community design skill, Impeccable, sorts surfaces the same way: "Operate" for apps, dashboards
and tools, "Persuade" for landing pages and marketing (read in part from the skill file,
2026-10-01). The advice to make a design bold and distinctive, which design skills for coding
agents give, belongs to brand mode; section 12 says where it applies.

### How much expression a product screen carries

The mode says what kind of screen it is. Inside product mode a screen can still carry more or less
expression, and this part says how much.

**What "expressive" means here.** The sources use the word in two senses. Carbon uses it for two
sets kept apart from the task: an expressive type set for editorial pages, and expressive motion
that it asks teams to "Reserve expressive motion for occasional, important moments, to better
capture the user's attention and offer a rhythmic break to the productive experience." Google
uses it for a whole design system: its research page describes Material 3 Expressive through
"color, shape, size, motion, and containment", so it also changes the size and grouping of the
parts a person works with. This file uses Carbon's sense. Expression is what a screen adds to draw
the eye or to show character, beyond what the task needs: a brand type step, a stronger colour, a
longer or springier motion, an illustration. Layout, size and grouping are not expression here;
sections 5 to 7 set them.

**The three cases.** Name one before you design the screen, so the author and the reviewer judge
the screen against the same aim.

| Case | What it is | When it fits | When it is the wrong case |
|---|---|---|---|
| Effective | Dense and quiet. Every element earns its place, and motion only shows what changed (section 8). | Every product-mode screen, by default: screens used many times a day, data-dense tables, tools for experts (section 10). | A few moments need the user's attention or a welcome, such as an alert or onboarding: then a balance. |
| Polished | The same structure as an effective screen, with more craft in type, palette, density and motion. Nothing is added. | Where what people think of the product counts as well as how fast they work: looks raised perceived usability in the studies below, and consumers cite a site's look when they judge its credibility (section 10, banking). | The polish costs the task, the state or a familiar control, or it stands in for a fix to what the screen says and in what order (the FCA's finding below). |
| Balance | An effective screen with expression at a few important moments: a transition, a confirmation, an empty state, an alert. | A product that needs some character on screens people work in. | The moments spread to most of the screen, or fall on an interaction repeated many times a day (section 8). |

The moments the owners name: Carbon's motion page holds that "System alerts and the appearance of
notification boxes are great cases for expressive motion", and adds opening a new page, clicking
the primary action button, and movement that itself carries a meaning. Carbon's type page calls
expressive moments inside a product "less common" and places them on home pages and page headers or
banners, where content "is not restricted to a container, card, or data table". Atlassian says:
"Save expressive, characterful motion for key brand moments, like onboarding experiences." The
empty state is this file's own example; no owner read names it, and what an empty state says is
[ux.md](ux.md) section 6.

**The default: start every product-mode screen as effective.** Move to a balance only for a moment
like the ones above, and add polish only where it costs nothing in the task, the state or a
familiar control. Why: the owners of four design systems put purpose before expression.

- Carbon keeps productive type "for product design" and expressive type "for editorial pages", and
  holds that "For the most part, this is still a good guideline to follow".
- Atlassian: "Motion is a clarifying layer, not decoration." and "Keep everyday UI motion efficient
  and focused, and let brand personality come through in restraint and polish rather than
  spectacle." Its motion page is marked Early Access (read 2026-10-29).
- Primer's accessibility guidance: "The first step is to consider whether motion is needed at all."
  Of motion meant "to enhance engagement and provide visual delight" it says: "Use it sparingly, if
  at all."
- Fluent 2: "Motion is applied with purpose and intent to serve the functionality of an experience."
  It names delight as an aim after that ("Delightful animation draws people in."), and that page
  does not say where delight is out of place.

At Vercel, the product-design skill given to coding agents says: "Do not add decorative novelty,
motion, or copy unless it clarifies structure, state, or brand intent." (a simplified view of the
skill, shown in a Vercel blog post, 2026).

### What the studies measured, and how each case is judged

No study read changed the looks of a screen alone and measured faster work. Each study changed
something different, so each row says what it changed.

| Study | What changed | Who took part | What it found | Limits |
|---|---|---|---|---|
| Bentley et al., "Usability Hasn't Peaked" (CHI '26) | Designs made to the Material 3 Expressive guidelines against versions made to the previous Material system, in 10 apps | 48 people | They "fixated on the correct screen element for a task 33% faster, completed tasks 20% faster, and rated experiences more positively" | Abstract only. The paper is listed by Google Research and the system is Google's; the authors' affiliation was not on the page. The abstract speaks of mobile usability throughout and ends on the "risks of added flexibility". A whole redesign: size and grouping changed with the look, so the study cannot say which part made the gain (this file's reading). |
| Google, "Expressive Design: Google's UX Research" | Material 3 Expressive against Material 3, across "46 separate research studies" with "more than 18,000 participants" | as stated | People spotted key elements "up to four times faster"; up to 87% of 18-to-24-year-olds preferred it, but "a strong minority of users preferred calmer, less intense versions". When an album-art playlist replaced a vertical list, "usability scores suffered", and removing text labels from email actions "resulted in decreased usability". | The owner's own research page, with no method or statistics, so nobody can check it. Its own advice: "No amount of emotion can compensate for a lack of clarity." |
| Thielsch, Haines and Flacke (PeerJ, 2019) | A tidy website against one made messy on purpose, "very varicolored" and with "a mixture of different fonts"; the same content on a made-up medical-information site; three tasks | 331 people, online, each saw one version | No significant effect of aesthetics on accuracy or response time in any of the three tasks | Tidy against deliberately messy, not plain against polished. People used the site for 10 to 20 minutes; the authors expect that "an office worker, who has to deal with an unaesthetic interface for eight hours every weekday, may be more strongly influenced". They still advise attention to aesthetics for its effect on how people perceive a site. |
| Perrig, Ueffing, Opwis and Brühlmann (Frontiers in Psychology, 2023) | A smartphone web app of a made-up event agency, made "as aesthetically pleasing or as unaesthetic as possible" | 281 people analysed, recruited on MTurk in the US, each saw one version | Looks raised perceived usability, a significant effect. In the paper's body, time and the number of correct answers showed no significant difference. | The abstract's claim of better performance is stronger than the body. Most people answered correctly in both versions, and use was short. |
| Moran, "The Aesthetic-Usability Effect" (NN/g, 2024, reviewed 2026) | A review of studies, no new measurement | none | "A pretty design can make users forgiving of minor usability problems, but not of large ones." In usability tests, the appeal of a site "masked its usability issues and made them harder to identify". | A practitioner's article backed by the studies it cites. |
| FCA, "Consumer understanding: good practice and areas for improvement" (2026) | A regulator's review of customer communications under the Consumer Duty, with a survey of 38 firms | 38 firms | "Some firms made surface-level changes, shorter wording, new icons or colour changes without improving clarity, sequencing or prominence of key information. Our review continued to find customers missing or misinterpreting core points." | About documents, journeys and promotions, not interface redesigns; no measurement. |
| Belton et al., FCA research note on digital design (2025) | Where product information sat in a hypothetical credit journey: behind a navigation-bar click or a link, or shown only on the quote page; against simplified information shown on time. No font or colour change was tested. | 6,045 people in the UK, online experiment | "Obscuring information generally reduces product comprehension." Simplified, timely information raised the comprehension of repayments "from 26 percent to 40 percent". Most treatments did not change acceptance, but showing the information only on the quote page lowered acceptance of the credit quote by about 4.9 percentage points, against a 54% baseline. | The authors call it "a superficial and highly stylised online setting", and the FCA says its research notes "may not necessarily represent the position of the FCA". |

What the studies add up to: the one study that changed looks alone with no stake in a design system
(Thielsch et al.) found no effect on performance, and Perrig et al.'s body agrees. The one study
that found faster work (Bentley et al.) changed a whole mobile design system, and the system's
owner lists it. Looks did raise what people said. Where the FCA moved information, comprehension moved. So
the default above rests on clarity and placement first; how each case is judged is
[evaluation.md](../../any-language/ux-evaluation/evaluation.md) section 12.

Each case is judged by the task measures of
[evaluation.md](../../any-language/ux-evaluation/evaluation.md) section 12, never by ratings alone.

### Alternatives considered on expression

- **Expressive throughout, as Google's research favours for its own system.** Not taken. The speed
  gain was measured on a whole redesign of mobile apps, in a paper the system's owner lists, and
  only its abstract could be read. Google's own page warns that what works in a media player or email app "might not
  be suitable for something like a banking interface", and Carbon, Atlassian and Primer keep
  expression for moments. Look again when an independent study separates expression from layout on
  web task screens.
- **Expression speeds up work (Bentley et al.).** Not taken as a rule. Thielsch et al., with no stake
  in a design system, changed only the looks of the same content and found no effect on
  performance, and Perrig et al.'s body agrees. Bentley et al.'s result holds for a Material redesign
  of a mobile app; a rule for such an app may rest on it, a rule here does not.
- **"Expressive" in Google's whole-system sense.** Not taken. It bundles size, shape and grouping,
  which sections 5 to 7 already set for product screens, so the word would cover changes this file
  rules on elsewhere. Carbon's sense matches the mode split in the table at the top of this section.

## 3. Tokens: tiers, roles and pairs

A token is a named value: a colour, a length, a radius, a duration. The owners name three tiers in
different words for the same shape: a raw value, then a role, then a component.

| Tier | Holds | Primer's name | Material's name | In this stack | Who uses it |
|---|---|---|---|---|---|
| Value | a raw value: a colour, a length | base (`base-color-green-5`) | reference | the OKLCH values in `:root` | the token file only |
| Role | a decision: what the value is for | functional (`bgColor-inset`) | system (`--md-sys-color-primary`) | `--primary`, `--muted-foreground`, used as `bg-primary`, `text-muted-foreground` | every component |
| Component | one part of one component | component (`button-primary-bgColor-hover`) | component | rarely needed | that component's own styles only |

- **When a component needs a colour, a radius or a shadow, use a role, never a raw value,** so a new
  theme or a rebrand is an edit to one file. Primer says base tokens are never used directly in
  code or design, and that its functional tokens are the ones used most. Carbon gives the payoff:
  with tokens, a change made in one place shows across the whole system. Two values no theme
  changes are the exceptions: `rounded-full` for a circle or a pill (section 7), and `transparent`
  for a part that shows no colour, such as the gap in a spinner ring.
- **Pick the role by what the thing means, not by how it looks.** Error text takes `destructive`
  even when another role has a similar red. Atlassian's rule is to choose a token by its meaning,
  not by its value.
- **Every surface role has a foreground role, and text on a surface uses that pair.** In shadcn/ui,
  `primary` pairs with `primary-foreground`; in Material, every colour role has an `on-` role for
  the content on it, with readable contrast. The pair is where contrast is computed, once, for
  every screen that uses it (section 4).
- **A theme swaps values, never roles.** Carbon's four themes keep each token's role and change its
  value: `$text-secondary` is Gray 70 in the White theme and Gray 30 in Gray 100. In Primer, the
  value behind `bgColor-default` changes with the colour mode on its own. A component never asks
  which theme is on.
- **A component token lives only in the styles of its own component.** Primer limits component
  tokens to component CSS; Material allows a component token to hold a raw value, and this practice
  follows Primer there.

In this stack (read 2026-10-01): Tailwind CSS 4's `@theme` defines tokens and generates a utility
for each, by namespace, such as `--color-*`, `--font-*`, `--text-*`, `--spacing-*`, `--shadow-*`,
`--animate-*` and `--breakpoint-*`. A variable in `:root` makes no utility. `@theme inline` makes
the utility use the variable's value, and `--color-*: initial;` removes the default palette.
shadcn/ui's variable names (`background`, `foreground`, `primary`, `primary-foreground`, `muted`,
`muted-foreground`, `destructive`, `border`, `input`, `ring` and more) are the roles; its default
theme holds OKLCH values in `:root` and `.dark` and maps them with `@theme inline`.

The token file of the billing application, in full:

```css
@import "tailwindcss";

/* Roles, not colours: a component names a role and the theme supplies the value.
   Every surface role has a -foreground role that keeps text readable on it
   (visual-design.md section 3). */
:root {
  color-scheme: light dark;

  --background: light-dark(oklch(0.99 0 0), oklch(0.16 0 0));
  --foreground: light-dark(oklch(0.2 0 0), oklch(0.96 0 0));
  --muted: light-dark(oklch(0.96 0 0), oklch(0.24 0 0));
  --muted-foreground: light-dark(oklch(0.45 0 0), oklch(0.74 0 0));
  --border: light-dark(oklch(0.88 0 0), oklch(0.34 0 0));
  /* The edge of a control, 3:1 on the background: `border` is decorative and may stay faint
     (visual-design.md section 4). */
  --input: light-dark(oklch(0.6 0 0), oklch(0.55 0 0));
  --primary: light-dark(oklch(0.45 0.16 255), oklch(0.74 0.13 255));
  --primary-foreground: light-dark(oklch(0.99 0 0), oklch(0.16 0 0));
  --destructive: light-dark(oklch(0.5 0.19 27), oklch(0.74 0.15 27));
  --success: light-dark(oklch(0.45 0.12 150), oklch(0.77 0.14 150));
  --ring: light-dark(oklch(0.55 0.16 255), oklch(0.8 0.11 255));
}

@theme inline {
  /* Clearing the default palette leaves the roles below as the only theme colours, apart from
     the keywords `transparent`, `current` and `inherit`: `bg-blue-500` produces no style at all
     (visual-design.md section 3). */
  --color-*: initial;
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-destructive: var(--destructive);
  --color-success: var(--success);
  --color-ring: var(--ring);

  /* One family, chosen and set once: the system face, so no font file loads (visual-design.md
     section 5; performance.md section 5). */
  --font-sans: ui-sans-serif, system-ui, sans-serif;

  --radius-control: 0.375rem;
  --radius-surface: 0.75rem;
}

@layer base {
  body {
    background-color: var(--background);
    color: var(--foreground);
  }
}
```

Why it is good:

- A component sees only roles. The values sit in one place, the light and the dark value of each
  role side by side in `light-dark()`, so both themes are designed together.
- `--color-*: initial` removes Tailwind's palette, but not the keywords `transparent`, `current`
  and `inherit`. A raw colour such as `bg-blue-500` then produces no style, so the mistake shows
  the first time anyone looks at the screen, not in a review months later. The comment keeps that
  reason at the line, because the line looks removable.
- Every text role has the surface it sits on, and each pair's contrast is computed in both themes
  (section 4).
- `input`, the edge of a control, is a role apart from `border`, so a field's edge can meet 3:1
  while the lines between table rows stay faint (section 7).
- The two radii are named by role (`control`, `surface`), not by size, and sit at the small values
  product screens use (section 7).
- The family is chosen and set once, as the `--font-sans` token: the system face, so no font file
  loads (section 5; [performance.md](../performance/performance.md) section 5).
- `color-scheme: light dark` lets the browser draw its own parts, such as scrollbars and form
  controls, in the matching theme (section 9).

`light-dark()` is a moving target: MDN marks it Baseline 2024, newly available since May 2024, and
warns that it may not work in older devices and browsers (read 2026-10-01). In a browser without
it, every colour that reads these variables falls back to the browser's default. If you support
such browsers, put the dark values in a `.dark` block, the way shadcn/ui's default theme does; the
roles stay the same.

The mistake this prevents is a raw palette value in a component:

```tsx
import type { ReactNode } from "react";

type ButtonProps = {
  children: ReactNode;
  // "button" by default: a bare <button> inside a form submits it.
  type?: "button" | "submit";
  disabled?: boolean;
  onClick?: () => void;
};

// Bad: the colours are raw palette values (`bg-blue-600`, `text-white`,
// `outline-blue-500`), not roles.
export function Button({ children, type = "button", disabled = false, onClick }: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      // focus-visible:outline-*: an outline, not a shadow, because forced-colours mode removes
      // shadows (accessibility.md section 5). pointer-coarse:min-h-11: 44 px tall on a touch
      // screen; 36 px is for a mouse (ux.md section 8).
      className="min-h-9 rounded-control bg-blue-600 px-4 text-sm font-medium text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 disabled:opacity-60 pointer-coarse:min-h-11"
    >
      {children}
    </button>
  );
}
```

The classes name a look, not a job. In the dark theme the button keeps the light theme's blue;
nobody computed the contrast of white on it; a rebrand has to edit every component that copied
the classes. In an application that keeps Tailwind's default palette this compiles and looks
right in the light theme, which is why it ships.

The same component with that one problem fixed, as the application has it:

```tsx
import type { ReactNode } from "react";

type ButtonProps = {
  children: ReactNode;
  // "button" by default: a bare <button> inside a form submits it.
  type?: "button" | "submit";
  disabled?: boolean;
  onClick?: () => void;
};

export function Button({ children, type = "button", disabled = false, onClick }: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      // focus-visible:outline-*: an outline, not a shadow, because forced-colours mode removes
      // shadows (accessibility.md section 5). pointer-coarse:min-h-11: 44 px tall on a touch
      // screen; 36 px is for a mouse (ux.md section 8).
      className="min-h-9 rounded-control bg-primary px-4 text-sm font-medium text-primary-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring disabled:opacity-60 pointer-coarse:min-h-11"
    >
      {children}
    </button>
  );
}
```

Why it is good: each colour is a role. The button's surface is `primary`, its text is the pair
`primary-foreground`, and its focus outline is `ring`, whose contrast against the background is
computed in both themes (section 4). The radius is the `control` role. The sizes are steps of the
scale (`min-h-9` is 36 px, `px-4` is 16 px), and the button grows to 44 px on a touch screen
([ux.md](ux.md) section 8). The `type` line and the `className` line keep their reasons as
comments, since a reader would otherwise drop the default, the outline or the coarse-pointer
height.

## 4. Colour and contrast

The contrast floor a design must meet, from WCAG 2.2 at level AA. The standard, its exceptions
and the checks that enforce it are [accessibility.md](accessibility.md) sections 2, 9 and 10; the numbers are here
because a designer picks colours against them.

| What | Minimum contrast | Where it comes from |
|---|---|---|
| Text | 4.5:1 | WCAG 2.2 SC 1.4.3 (AA) |
| Large text: 18 pt (24 CSS px), or 14 pt (about 18.7 CSS px) in bold | 3:1 | SC 1.4.3 (AA) |
| The parts of a control a user needs to see it (its edge, its state), a focus indicator, an icon or a graphic that carries meaning | 3:1 | SC 1.4.11 (AA) |
| Text at the enhanced level | 7:1, large text 4.5:1 | SC 1.4.6 (AAA) |

The ratio is a threshold and is not rounded: 4.49:1 fails 4.5:1.

- **When the token file changes, compute the contrast of every text-on-surface pair in both
  themes,** so one check covers every screen that uses the pair. Low contrast is the failure seen
  most: WebAIM's 2026 survey of a million home pages found low-contrast text on 83.9% of them, up
  from 79.1%. WebAIM blames this partly on AI-assisted coding; that link is a correlation, not a
  measurement.

  The billing application's pairs, computed from the OKLCH values in its token file:

  ```text
  foreground on background             light 17.59 dark 17.28 floor 4.5:1 ok
  muted-foreground on background       light 7.23 dark 8.42 floor 4.5:1 ok
  muted-foreground on muted            light 6.62 dark 7.13 floor 4.5:1 ok
  primary-foreground on primary        light 7.30 dark 8.41 floor 4.5:1 ok
  destructive on background            light 6.44 dark 7.90 floor 4.5:1 ok
  success on background                light 6.84 dark 9.88 floor 4.5:1 ok
  ring on background                   light 4.77 dark 10.35 floor 3:1 ok
  input on background                  light 3.84 dark 4.00 floor 3:1 ok
  border on background                 light 1.39 dark 1.65 decorative, no floor
  ```

  Why it is good: every pair a screen can use is listed with the floor it must meet, in both
  themes. The focus ring and the `input` role, the edge of a field, are held to 3:1, and the
  border is marked decorative, so nobody uses it as the only edge of a control (section 7).

  Check: when the token file changes, is every pair's ratio, in both themes, at or above its
  floor?
- **Use the WCAG 2 ratios as the reference, and look at the dark theme with your own eyes as
  well.** WCAG 3 and APCA are not standards yet; why, and what to do about dark pairs, is
  [accessibility.md](accessibility.md) section 9.
- **Never let colour be the only signal** (SC 1.4.1, level A). A status, an error or a required
  field also carries a word or an icon.
- **Build the palette in a perceptual colour space from a few inputs.** Tailwind 4's default
  palette and shadcn/ui's themes are OKLCH, and `oklch()` is Baseline widely available since
  2025-11-09 (webstatus.dev, read 2026-10-02). Linear rebuilt its theming in LCH and went from 98
  theme variables to 3: a base colour, an accent and a contrast level (read as a snippet only).
- **No pure black, and no grey text on a coloured surface.** Text on a coloured surface takes that
  surface's foreground role, which has its contrast computed. Two sources name both mistakes:
  Refactoring UI by Adam Wathan and Steve Schoger, read only through second-hand summaries, and
  Impeccable's list of anti-patterns.

A status shown by colour alone:

```tsx
// Bad: a dot whose colour is the only signal. A reader who cannot tell red from
// green, and every screen reader, learns nothing from it.
const STATUS_COLOR: Record<InvoiceStatus, string> = {
  paid: "bg-success",
  overdue: "bg-destructive",
  due: "bg-muted-foreground",
};

type InvoiceStatusBadgeProps = {
  status: InvoiceStatus;
};

export function InvoiceStatusBadge({ status }: InvoiceStatusBadgeProps) {
  return <span className={`inline-block size-2 rounded-full ${STATUS_COLOR[status]}`} />;
}
```

The dot fails SC 1.4.1: the status exists only as a colour. The same badge with a word, as the
application has it (the import line is left out):

```tsx
const STATUS_LABEL: Record<InvoiceStatus, string> = {
  paid: "Paid",
  overdue: "Overdue",
  due: "Due",
};

const STATUS_COLOR: Record<InvoiceStatus, string> = {
  paid: "text-success",
  overdue: "text-destructive",
  due: "text-muted-foreground",
};

type InvoiceStatusBadgeProps = {
  status: InvoiceStatus;
};

export function InvoiceStatusBadge({ status }: InvoiceStatusBadgeProps) {
  // The word carries the status. The colour repeats it and is never the only signal
  // (accessibility.md section 9).
  return <span className={`text-sm font-medium ${STATUS_COLOR[status]}`}>{STATUS_LABEL[status]}</span>;
}
```

Why it is good: the word carries the status, and the colour only repeats it, so the badge reads
the same in greyscale and to a screen reader. Each colour is a role whose contrast against the
background is in the table above. The comment says why the label must stay when someone wants a
smaller badge.

## 5. Type

- **Use the stack's type scale, not a ratio of your own.** A 2025 review of 42 empirical studies
  found "no single type size or typeface optimizes readability for everyone in every situation",
  and the research for this practice found no evidence base for modular-scale ratios. Tailwind 4's
  default steps (read 2026-10-01):

  | Utility | Size | Typical use on a product screen |
  |---|---|---|
  | `text-xs` | 12 px | a secondary label, a badge |
  | `text-sm` | 14 px | table text, labels, buttons |
  | `text-base` | 16 px | body text; every text input ([ux.md](ux.md) section 4) |
  | `text-lg` | 18 px | a section heading |
  | `text-xl` | 20 px | a section heading |
  | `text-2xl` | 24 px | a screen title |
  | `text-3xl` and up | 30 px and more | brand pages |

  The "typical use" column is this practice's reading of the owners' product sizes: Geist uses 14 px
  most for copy and labels and keeps running text of 18 px and up for marketing and hero areas;
  Atlassian's heading scale runs from 32 px down to 12 px, with its larger steps for marketing.
- **Make hierarchy with weight and colour before size.** A column heading in `text-muted-foreground`
  and a row heading in `font-medium` say what matters without a larger step. Refactoring UI gives
  this advice; it was read only through second-hand summaries, so it is paraphrased here.
- **Choose one family for the application and set it once, as a `--font-*` token.** Atlassian keeps
  its brand face for marketing and its product faces for the app. Linear's product UI uses Inter for
  body text and Inter Display for headings, so the face itself is not the problem; the mistake is
  the default nobody chose (section 11). The billing application's token file sets `--font-sans`
  to the system face (section 3).
- **Keep running text at 45 to 75 characters a line,** with about 66 as the ideal, which web.dev
  sets with `max-inline-size: 66ch`. WCAG's limit of 80 characters is SC 1.4.8, level AAA, not AA.
  Anthropic's frontend-design skill says the same in its own words: "Default to line lengths of
  less than 80 characters." Tables and forms are not running text.
- **Set numbers that line up in a column in tabular figures** (`tabular-nums`), as Vercel's
  interface guidelines ask.

Amounts in proportional figures:

```tsx
{/* Bad: proportional figures. A "1" is narrower than an "8", so the digits of
    the amounts do not line up and the eye cannot compare them down the column. */}
<td>{moneyText(invoice.amountCents)}</td>
<td>{invoice.dueOn}</td>
```

The digits shift from row to row. The same cells from the application's invoice table, cut to the
two cells that hold numbers:

```tsx
<td className="tabular-nums">{moneyText(invoice.amountCents)}</td>
<td className="tabular-nums">{invoice.dueOn}</td>
```

Why it is good: every digit takes the same width, so amounts and dates line up and a reader scans
down the column. The class goes on the cells that hold numbers, and nowhere else.

## 6. Spacing, layout and density

- **Take every space from the stack's 4 px scale, never an arbitrary value.** Tailwind 4 sets
  `--spacing: 0.25rem` (4 px), and every `p-<n>`, `m-<n>` and `gap-<n>` is n times that (read
  2026-10-01). Carbon asks teams to avoid leaving its spacing scale wherever they can, and allows a
  jump of a step or more at a page breakpoint. Atlassian uses an 8 px base, and Carbon's scale is
  built from multiples of 2, 4 and 8 px. No source measured an 8 px grid against a 4 px one, so this
  practice keeps the stack's 4 px.

  ```tsx
  // Bad: arbitrary values, so this form gets its own width and gap and the
  // next form gets others.
  <form onSubmit={payInvoice} className="flex max-w-[450px] flex-col gap-[18px]">
  ```

  Each value in square brackets is off the scale, and the next screen will pick a third value. The
  application's form, cut to its opening tag:

  ```tsx
  <form onSubmit={payInvoice} className="flex max-w-md flex-col gap-4">
  ```

  Why it is good: the width and the gap are named steps of the stack's scales (`gap-4` is 16 px), so
  every form of the application has the same rhythm, and a value in square brackets stands out in
  review as one that left the scale.
- **Lay a screen out in one column first, and add columns as the space grows,** so the screen
  already works at the narrow width that reflow asks for ([accessibility.md](accessibility.md)
  section 9). web.dev starts macro layouts single-column and builds them with Grid.
- **Use media queries for the page and container queries for a component,** so a component adapts
  to its own width wherever it is placed. web.dev's layout modules give the split and the CSS:
  `container-type: inline-size` on the parent and `@container (min-width: 25em)` on the rule.
  Container size queries are Baseline widely available since 2025-08-14 (webstatus.dev, read
  2026-10-02).
- **Keep a task screen dense: tight rows, small type, few boxes, alignment and spacing to group
  things.** Linear's 2024 redesign set out to "reduce visual noise, maintain visual alignment, and
  increase the hierarchy and density of navigation elements"; its 2026 refresh kept "that rich
  density of information without letting the interface feel overwhelming", with fewer borders,
  compact tabs and fewer icons. Density never shrinks a target below its floor ([ux.md](ux.md)
  section 8).

## 7. Shape, borders and elevation

- **Keep radii small on a product screen, and name them by role.** The owners' product radii:

  | Owner | Radii |
  |---|---|
  | Vercel Geist | 6 px (base, small, tooltip), 12 px (medium, large, menu, modal), 16 px (fullscreen) |
  | GitHub Primer | 3 px (small), 6 px (medium), 12 px (large), full (pill) |

  The billing application's token file has two: `--radius-control` (6 px) and `--radius-surface`
  (12 px).
- **A full circle or a pill, such as a status dot or a spinner ring, takes `rounded-full`,**
  because a radius role stands for the size of a corner, and a circle has no corner. `full` is not
  a role: Primer's table above lists "full (pill)" as the last step of its radius scale, and
  Tailwind 4's `rounded-full` is a fixed value, `calc(infinity * 1px)`. The gap in a spinner ring
  takes `border-t-transparent`, because a hidden edge has no colour to name; the built stylesheet
  keeps the keyword after `--color-*: initial`.
- **Draw a border only where it tells the reader something.** Anthropic's frontend-design skill:
  "Structural devices like outlines, borders, numbering, eyebrows, dividers, labels, etc., encode
  useful information about the content rather than decorate it." Linear's 2026 refresh removed
  borders that "had quietly proliferated" and softened the contrast of the rest. Refactoring UI
  (read through a summary) suggests spacing, two background colours or a shadow in place of a
  border.
- **A divider may be decorative; the edge of a control may not.** The application's `border` role
  is 1.39:1 in the light theme, which is fine for the line between table rows. When the edge is
  what shows the user where a text field is, it needs 3:1 (SC 1.4.11). Give that edge a role of its
  own, as shadcn/ui does with `input`, and compute it against 3:1. The application's theme now has
  that role, `input`, at 3.84:1 in the light theme and 4.00:1 in the dark one (section 4).
- **Keep surfaces in the page flat and give floating layers the shadow,** so a shadow means one
  thing: this layer sits above the page. Geist puts minimal shadow on surfaces in the page and
  progressively stronger shadows on layers that float above it, such as a menu or a dialog.
- **Define elevation as a pair of tokens, a surface and its shadow, and always use them together.**
  Atlassian asks that a surface token always go with its matching shadow token, so a raised layer
  looks right in both themes. Carbon steps surfaces up as layers: `$layer-01` sits on
  `$background`, and `$layer-02` on `$layer-01` (read as a summary). The owners' rules for dark
  surfaces, such as lightening a surface as it rises, were not read in full for this practice.

## 8. Motion

- **Animate to show what changed after a person's action, and almost nothing else.** Anthropic's
  frontend-design skill: "Motion that answers a person's action (opening, expanding, confirming) is
  welcome when it shows what changed", and motion nobody triggered is used "sparingly and
  deliberately, only to draw attention". In product mode, Carbon wants motion "subtle and out of
  the way".
- **The more often a person sees a motion, the less of it there is.** Atlassian: "Match motion
  expression to how often it is seen. High-frequency interactions like hover states, button
  presses, and list items should use minimal, near-instant transitions that stay out of the way."
  and "If someone will trigger this motion dozens of times a day, keep it under 150ms." This adds
  no number to the table below: it puts every frequent interaction in the table's first row, and
  keeps expressive motion for the rare moments of a balance (section 2). Atlassian's motion page is
  marked Early Access (read 2026-10-29).
- **Let the duration grow with the size of the change.** Carbon, Atlassian and Material all state
  it: the farther an element moves, or the more it grows, the longer the animation. The owners'
  numbers differ, so the table gives ranges and who states them:

  | Change | Duration | Owners |
  |---|---|---|
  | hover, press, a toggle, a fade | 50 to 150 ms | Atlassian: interactions 50 to 150 ms, small and frequent changes under 150 ms; Carbon: 70 ms (button, toggle), 110 ms (fade); Material short: 50 to 200 ms |
  | a small expansion, a short move, a toast | 150 to 250 ms | Carbon: 150 ms (small expansion), 240 ms (expansion, toast) |
  | a panel or a dialog that enters or leaves | 150 to 400 ms | Atlassian: transitions 150 to 400 ms; Carbon: 400 ms (large expansion); Material medium: 250 to 400 ms |
  | a full-screen change, a background dimming | 450 to 1000 ms | Material: 450 to 1000 ms; Carbon: 700 ms (background dimming) |

- **Make an exit faster than its entrance,** so a closing panel never holds up the next step.
  Atlassian gives that reason; it is the only owner read that states this rule. The easing follows
  the same logic: decelerate into place on entry, accelerate away on exit.

  | Curve | Carbon, productive | Material, standard |
  |---|---|---|
  | entrance (decelerate) | `cubic-bezier(0, 0, 0.38, 0.9)` | `cubic-bezier(0, 0, 0, 1)` |
  | exit (accelerate) | `cubic-bezier(0.2, 0, 1, 0.9)` | `cubic-bezier(0.3, 0, 1, 1)` |

- **Keep the durations and curves with the other tokens,** so every component moves the same way.
  No owner read states this for motion; it is this file's one rule applied to motion.
- **List the properties you animate, never `transition: all`,** so nothing moves that nobody
  meant to move. Vercel's guidelines: "NEVER: `transition: all`—list properties explicitly". Which
  properties are cheap to animate, and what animation costs at run time, is
  [performance.md](../performance/performance.md) section 6.

  The motion blocks of this section (the two below and the reduced-motion one after them) are not
  part of the reference application, which has no transition yet. The application's one motion is
  the loading spinner: Tailwind's `animate-spin` behind `motion-safe:`. Its duration and curve come
  from Tailwind's default `--animate-spin` token (`spin 1s linear infinite`), a step of the stack's
  theme the way `gap-4` is a step of its spacing scale, so the rule on tokens holds without a line
  in the application's file. It answers the person's navigation with a loop that shows a wait, not
  a change of a size, so the duration table does not reach it; when a wait gets a spinner is
  [ux.md](ux.md) section 3. The two custom properties join the application's token file with the
  first transition.

  ```css
  :root {
    --motion-duration-small: 150ms;
    --motion-ease-enter: ease-out;
  }

  /* Bad: `all` animates every property that changes, layout ones included. */
  .invoice-details {
    transition: all var(--motion-duration-small) var(--motion-ease-enter);
  }
  ```

  `all` picks up properties nobody meant to animate, such as `height` when the panel's content
  changes, and a layout property is costly to animate. The same rule with the two properties
  listed, and the two tokens defined in the block because the reference application has none:

  ```css
  :root {
    --motion-duration-small: 150ms;
    --motion-ease-enter: ease-out;
  }

  .invoice-details {
    /* Listed, never `all` (visual-design.md section 8), and only `opacity` and `transform`:
       a layout property is costly to animate (performance.md section 6). */
    transition:
      opacity var(--motion-duration-small) var(--motion-ease-enter),
      transform var(--motion-duration-small) var(--motion-ease-enter);
  }
  ```

  Why it is good: only the two cheap properties move
  ([performance.md](../performance/performance.md) section 6), and a change to the panel's size
  snaps instead of animating. The duration and the curve are tokens, as the rule above asks, so
  every component that moves takes the same two values. 150 ms is in the range for a small change,
  and `ease-out` decelerates into place, the entrance curve; a panel that also leaves gets the
  accelerating curve and a shorter time on its way out (the rules above).
- **Honour `prefers-reduced-motion`: keep the fade, drop the movement.** MDN advises replacing
  scaling and panning with opacity fades, and the media query is Baseline widely available since
  2022-07-15 (webstatus.dev, read 2026-10-02). WCAG asks for it only at level AAA (SC 2.3.3);
  Vercel's guidelines and Josh Comeau ask for it with no level attached. The block below is not
  from the reference application either; it uses the two tokens of the block above.

  ```css
  @media (prefers-reduced-motion: reduce) {
    .invoice-details {
      /* Keep the fade, drop the movement (visual-design.md section 8). */
      transition: opacity var(--motion-duration-small) var(--motion-ease-enter);
    }
  }
  ```

  Why it is good: a user who asked the system for less motion still sees that the panel changed,
  through the fade, and nothing slides or scales.
- **When a chart changes form, animate its marks from the old form to the new one, with little
  staging.** Heer and Robertson found, with 24 people in two experiments, that animated
  transitions between statistical charts lowered error: "Even in highly predictable transitions,
  such as the stacked bars to grouped bars conditions, animation had a significantly lower error
  rate." They also found that "heavily staged animation resulted in increased error". They measured
  error, not time, on changes between chart forms, not between screens; the rise with heavy staging
  showed in two chart types and was not always significant, and they call the gain from simple
  staging "not overwhelming". Their transitions ran 2 to 3 seconds and the study compared no
  durations, so it sets no number: the duration table above still sets the time, and a chart
  transition keeps the reduced-motion rule.
- **Set the amount of motion by the audience.** NN/g's tests with 125 children found that children
  liked animation and sound, where adults usually disliked them (Sherwin and Nielsen, 2019, in a
  table row "Animation and sound: Liked / Usually disliked"). W3C's guidance for older users: "Some
  older people are particularly distracted by any movement and sound on web pages." The two
  audiences pull in opposite directions, so the rules above are a default for adults at work. An
  application for children may carry more motion, and one for older adults less; both keep the
  durations above and the reduced-motion rule.

## 9. Themes: light and dark

- **Start in the light theme, follow the system when it asks for dark, and offer a switch.** NN/g:
  for people with normal vision, "light mode leads to better performance most of the time"; dark
  mode helped people with cataracts in the studies it reviews. It advises light as the default for a
  general audience, a switch to dark, and a dark option in applications people read in for a long
  time (the article is from 2020). web.dev's theming module follows the system setting with
  `color-scheme` and `prefers-color-scheme`.

  The application's token file does the first two with `color-scheme: light dark` and
  `light-dark()`: MDN says the function gives its first value when the used colour scheme is light
  or when the user has set no preference (read 2026-10-01). A switch then only has to set
  `color-scheme` on the root element, and every role follows. The block below is not from the
  reference application, which has no switch yet:

  ```css
  /* The switch sets `color-scheme` only; every role follows through `light-dark()`
     (visual-design.md section 9). */
  :root[data-theme="light"] {
    color-scheme: light;
  }

  :root[data-theme="dark"] {
    color-scheme: dark;
  }
  ```

  Why it is good: the switch touches one property and no colour; the roles and their values stay in
  the token file. Where the user's choice is stored is a question of where state lives
  ([architecture.md](../architecture/architecture.md) section 7).
- **Design both themes, and look at both before a change ships.** Every pair is computed in both
  (section 4). Linear makes text and neutral icons darker in the light theme and lighter in the dark
  one, and Primer inverts its neutral scales in dark mode, so components share one set of roles.
- **Set `color-scheme` on the root element,** so the browser draws scrollbars, form controls and the
  page canvas in the matching theme. `color-scheme` is Baseline widely available since 2024-08-03
  (webstatus.dev, read 2026-10-02); Vercel's guidelines ask for it too.
- **On a data screen, keep both themes designed and the switch in place; the studies do not pick
  one.** Three recent studies disagree:
  - Ettling et al. (ETRA '25): 15 people in a dimly lit room (114 lux) each solved dashboard tasks
    once per theme at three levels of complexity. Mann-Whitney U tests found dark dashboards more
    accurate at medium complexity only, with no difference at the easy and hard levels and none in
    time. Dark gave a lower perceived workload on the NASA-TLX at every level. The authors note that
    a larger sample would give the tests more power.
  - While and Sarvghad (IEEE VIS '24, short paper; abstract only): in a crowdsourced study of 134
    people (the abstract's own split, 69 under 60 and 66 aged 60 and over, adds up to 135), the
    better polarity for charts "varied on an individual basis, with each polarity benefiting
    comparable proportions of participants", and it did not always match the one people preferred.
  - Gazit et al. (Ergonomics, 2025; abstract only): 173 people took cognitive tests online on a
    light or a dark background, and "cognitive scores were higher in light mode compared to dark
    mode". These were cognitive tests, not work in an interface.

  Two designed themes with a switch fit all three results. None of them overturns the light default
  above, and none supports a dark-only screen.

## 10. Design styles and their fit

A style is a look with a name. Most of them were made for posters, marketing pages or a phone
platform, not for a screen of forms and tables. The table says what each one is, whether it fits an
application screen, and the caution an owner or a measurement gives. Where the fit is the
research's own inference and no source tested it, the row says so.

| Style | What it is | Fits an application screen? | Caution, and how strong it is |
|---|---|---|---|
| Minimal, Swiss | A modular grid, a sans-serif face, asymmetric layout, generous white space, a neutral tone. "Minimal design is about removing the unnecessary and emphasizing the necessary" (Smashing Magazine, 2009). | Yes, in its parts: the grid and the neutral type map onto forms and tables. That mapping is an inference; no source tested it on app screens. Linear states the same aims for its app: "a more neutral and timeless appearance". | The sources describe print design. A poster's white space does not carry over to a dense table (an inference): take the grid and the type, keep the density (section 6). |
| Flat | "Defined by the absence of glossy or three-dimensional visual effects" (NN/g). | Yes, with clear cues for what can be clicked. | NN/g: users lose the cues for what is clickable, and "long-term exposure to these flat yet clickable elements has been slowly reducing user efficiency" (NN/g's eye-tracking, 2015; the method was not checked, and the page is old). |
| Dense product UI | Small type, tight rows, few borders, neutral surfaces, one accent: Linear, Geist, Carbon's productive mode. | Yes: this is product mode (section 2). | Linear's own warning is the limit: density "without letting the interface feel overwhelming". Targets keep their floor ([ux.md](ux.md) section 8). |
| Bento grid | A grid of compartments of different sizes under one grid. | Perhaps, for a dashboard of figures and charts. Unverified. For the charts, see section 12. | Only agency blogs and a design publication on Medium describe it; no design-system owner and no NN/g article was found. Treat any number quoted for it as unmeasured. |
| Neo-brutalism | "High contrast, blocky layouts, bold colors, thick borders, and 'unpolished' elements" (NN/g, 2025), with solid single-colour shadows. | Brand pages. On a task screen, thick borders on every element fight density (an inference). | NN/g: "without balance, it can overwhelm users and hinder accessibility". It asks for contrast, plain body type and white space. |
| Glassmorphism | Translucent layers with background blur, "mimicking frosted glass" (NN/g, 2024). | At most for chrome and overlays, never under text or data (an inference). | NN/g: busy backgrounds and translucent layers hurt legibility and break contrast; overused, it "can pose significant accessibility and usability challenges". |
| Liquid Glass | Apple's translucent material for controls, navigation, icons and widgets, introduced on 2025-06-09 for its 26-series systems. | No. It is a native platform material; Apple's release gives no web guidance (read 2026-10-01). | NN/g's review of iOS 26 found text on images with low contrast, shrunk tap targets and controls that come and go, and concludes that Apple put spectacle ahead of usability. An expert review, not a measured study; read as a summary. |
| Skeuomorphism | Real-world textures, shadows and gradients that make a three-dimensional effect (NN/g, 2024). | No, as a look for whole screens. | NN/g: it "led to cluttered interfaces and slower load times", and its interactions were "clunky and unintuitive in a digital medium". |
| Neumorphism | Soft UI: an element in the colour of its background, raised by one light and one dark shadow (CSS-Tricks, 2020). | No, not for controls, forms or tables. | Users with colour blindness or poor vision "would have difficulty using it due to the poor contrast caused by the soft shadows", and contrast checkers cannot measure shadows, so a tool passes what people cannot see. One practitioner's article, read in full. |
| Editorial, typographic | Large dramatic type, broadsheet layouts, hairline rules. | Brand pages and long reading. Carbon: the same type "would be distracting if used in product". | It is also one of the default looks of generated UI (section 11). |
| Material 3 Expressive | Google's 2025 update for Android and Wear OS: "color, shape, size, motion, and containment", springy motion, dynamic colour. | Android apps. On the web, take nothing from it by default: Google's web library has it only as experimental components that it says are not for production. | Google's own research reports 46 studies, more than 18,000 participants and key elements spotted "up to four times faster", and Bentley et al. found faster tasks with it in 10 mobile apps (section 2). Both are published or listed by the system's owner, and both change the whole design, not the looks alone. Its own caveat: "Context still matters"; breaking familiar patterns reduced usability. On the web, `@material/web` v2.5.0 (July 2026) adds Expressive components only in its `labs` folder, whose README says: "This folder contains experimental features that are not recommended for production." The library's own README says it is "in maintenance mode pending new maintainers" (read 2026-10-29). |
| Dark-first | Light text on a dark background as the only or the default theme. | As one of two designed themes, yes. As the default for a general audience, no. | NN/g (2020): light mode "leads to better performance most of the time" for people with normal vision. Linear designs both themes rather than dark only. WCAG 2 math may flatter dark pairs (section 4). On data screens, three recent studies disagree on which theme works better (section 9). |

To use a style on a product screen, take the parts that keep sections 3 to 9: a grid, neutral type,
flat surfaces with clear cues. Leave the parts that break them: translucent layers under text, soft
shadows on controls, decorative motion, type at brand sizes.

### By use case

Before you design a screen for one of the fields or uses below, read its row: the owner of a design
system, a host product, a public body or a regulator has said something about how it should look.
Most rows quote the owner; the rows on complex tools, children, older adults and checkout quote
research firms and NN/g. "None found" in the third column means the research for this file found no
study, not that none exists. The last column is this file's rule for the row.

| Use case | What the owners say | What was measured | What this file takes |
|---|---|---|---|
| Product screens in general | Carbon keeps productive type "for product design" and expressive type "for editorial pages", blended by "moments", and keeps expressive motion for "occasional, important moments". | Section 2 | Effective, or a balance (section 2). |
| Onboarding and first use | Atlassian: "Save expressive, characterful motion for key brand moments, like onboarding experiences." | None found | One of the few moments a balance spends its expression on. |
| Interactions repeated many times a day | Atlassian: "If someone will trigger this motion dozens of times a day, keep it under 150ms." | None found | Minimal, near-instant motion (section 8). |
| Banking | Google's research page: "What works in a media player or email app might not be suitable for something like a banking interface. Product makers need to respect well-established UI patterns and standards." Nedbank, a South African bank that publishes its design system, asks in its motion guidelines: "Keep animations simple and unobtrusive", and "Use motion to enhance the brand story and create a sense of trust and reliability." | Figl et al. found that bank home pages that look typical of banks improved people's attitude to the bank and its appeal as an employer, with 107 people rating 16 home pages in a job-seeker scenario; attitude was measured through items on the bank's competence, not task performance. Stanford, Tauber, Fogg and Marable (2002) found that consumers cited a site's look in 54.6% of their comments on finance sites, against 16.4% for finance experts (15 experts, and 2,684 consumers in a parallel study): what people say they rely on, not proof that looks are a valid cue. | Effective, with the patterns users know from other banks; simple motion. |
| Financial services, UK | The FCA's Consumer Duty guidance asks firms to "make key information prominent and easy to identify, including by means of headings and layout"; its rule PRIN 2A.5.10 says that "Where appropriate, a firm must: (a) test communications before communicating them to retail customers", and monitor their impact after. FG22/5 recommends layering, where "key information is provided upfront with cross-references or links to further detail". Friction that keeps customers from acting in their interests, such as complaining or switching, "is not consistent with the Duty", while the FCA's 2025 review holds that "Positive friction in journeys can drive good outcomes." | The FCA's research note and its review of 38 firms (section 2) | Effective; key information first; for UK retail customers, test before release where appropriate. |
| Illustration inside the product | Atlassian: "Collage is for marketing landing pages and communications only — it's too visually busy for in-product use." and "Excessive illustrations increase cognitive load. Consider icons, copy, ambient pattern, or other affordances before using illustrations." Written for Atlassian's own brand. | None found | No decorative illustration on a task screen; an icon or a line of copy first. |
| Public government services, UK | GOV.UK's design principles: "If we have to sacrifice elegance - so be it." and "We should use the same language and the same design patterns wherever possible." A site on a GOV.UK domain "must look like GOV.UK"; a public-facing service hosted elsewhere must still use the GOV.UK Design System, apart from branding such as logos and fonts. Since 9 July 2026 a site or service that is not on GOV.UK "cannot use GOV.UK brand colours" (read 2026-10-29). | None found | The government's design system, with no look of your own. |
| Internal tools for staff | GOV.UK's service manual (2018): it makes sense for public-facing services to "look and feel like part of GOV.UK", and "This is not necessary for internal services"; it also asks to "Hold internal services to the same standard you would a public-facing service". DWP gives internal services "such as admin dashboards and agent-facing systems" a header with no GOV.UK branding or crest. The Home Office, whose system "builds on the GOV.UK design system", says: "For internal services, such as caseworking systems, use the Home Office styles (including logo, colours and internal font) in your prototypes"; its production guidance is not written yet. The NHS keeps one design system "for the public and staff", and allows smaller buttons where space is limited or where "there are several actions of a similar priority that a user can take, for example on a staff-facing system": "Use them sparingly." | None found. DWP reports a debate among government designers on whether 'one thing per page' suits "expert users who prioritise moving through a journey quickly", and does not settle it. | One design system with small variants (settled below). |
| Complex tools for expert users | Kaplan (NN/g, 2025, an opinion with no new data): complex applications "demand higher levels of cognitive load and feature density compared to typical consumer apps", and splitting their users into novices and experts is "a false dichotomy". | Liu and Sra (preprint, 2025) found, in the 3D tool Blender, that a reduced, task-scaffolded panel lowered 32 beginners' perceived task load and raised their self-rated performance; time was the same in one task and shorter in the other. The 8 experts used only the new panel, with no baseline condition. | Effective and dense (section 6). A reduced panel for new users is something to test with them, not a default. |
| US federal services | The U.S. Web Design System, on type only: "A straightforward and neutral typeface can help the user focus on using the interface as a tool." | None found | A neutral face (section 5). |
| Healthcare | The NHS: "People trust the NHS. Take care not to jeopardise that. Design things that are reliable and secure." and "Do not push complexity onto the people using what you are designing." On contrast: "The NHS meets at least level AA for contrast and we aim for AAA where possible." One design system "for the public and staff". | Stanford, Tauber, Fogg and Marable (2002): consumers cited a site's look in 41.8% of their comments on health sites, health experts in 7.6%. | Effective; text contrast at AAA where you can (section 4). |
| Data-dense tables | Carbon's data table: 40 px rows as "the default and most commonly used size", 24 px "for highly dense layouts where maximizing information within limited space is a priority". SAP's UI5 shows larger controls on touch devices and "a smaller, more compact design for devices that are operated by mouse"; its third density, condensed, is for tables and "can only be used in combination with the Compact density"; in SAP's Fiori launchpad the user can set the density on desktop. Atlassian names customisable density as a goal "in the future", keeps space tokens of 0 to 8 px "for small and compact pieces of UI", and has "a compact button for tight spaces". Shopify: "Avoid changing information density within a single page, otherwise your app can feel disjointed." | None found: no controlled study of dense against airy layouts (section 12) | Dense by default (section 6); targets keep their floor ([ux.md](ux.md) section 8); one density per page. |
| Charts on data screens | The UK Government Analysis Function: "Avoid: shaded backgrounds; unnecessary borders; boxes around legends and other content; patterns, textures and shadows; 3D shapes; unnecessary data markers on line charts; thick or dark gridlines". "The right chart will depend on the values in your data and the statistical story you're telling." "We recommend a limit of four categories as best practice for basic data visualisations." Clustered and stacked bar charts get "no more than four series". "You should only use different colours when they show helpful differences in the data." "If you have a series of charts, assign the same colour to the same variable in each chart." The ONS: "Always use five colours or fewer". Atlassian: 5 to 6 colours, the rest grouped together. Carbon: a palette of 14 colours "applied in sequence strictly", with no cap. The U.S. Web Design System: "Prefer common visualization types." and "Use color with care." | Heer and Robertson, on transitions between charts (section 8) | Four categories at most, the same colour for the same variable, a text label on every status (settled below); marks at 3:1 (section 12). |
| Dashboards | The Analysis Function: "Design your dashboard using an inverted pyramid structure, with your most important headline content up front and detailed information in other tabs", "limiting colour schemes and fonts to a few consistent choices", and consistent with other government dashboards. Carbon: "Place the most important at the top of the page", strip away "anything that could distract a user from interpreting the information", and "Always use consistent colors for each data set within a dashboard." | Ettling et al., on dark and light dashboards (section 9) | Effective; the headline first; one colour per data set. |
| An app inside Shopify's admin | Shopify: "the best apps provide merchants with a user experience that matches the appearance and behaviors of the Shopify host surface", with Polaris components for embedded apps. Its Built for Shopify review, which an app applies for, asks: "Your app's UI should mimic Shopify's core look and feel", and lists as failures primary buttons in "a completely different color than Polaris" and a background "significantly different from the Shopify admin". Rule 4.3.5 forbids an app that a merchant could mistake for Shopify itself. The base App Store review asks for "a consistent embedded experience", which is about keeping features inside the admin, not about the look; sales channel apps must "Use the required Polaris components and style guide". | None found | Polaris and the admin's look; required for sales channel apps and for the badge (read 2026-10-29). |
| An app inside Microsoft Teams | Teams: "The app uses native Teams design components or your own. There's no blend of color schemes, controls, and so on." Its store validation (rules starting July 2026) marks the styling of tabs "Good-to-fix", which does not block publishing; inside meetings, "Apps must only use a dark theme during meetings and calling" is a Must fix. The marketplace certification policy: "Apps must follow Teams tab design guidelines without impeding the customer experience within the host application." | None found | Teams components or your own, never a mix; the dark theme in meetings and calls (read 2026-10-29). |
| An Office add-in | Office: "The functionality, as well as the look and feel, of an add-in must harmoniously complement the Office experience." and "Place your add-in branding in a brand bar footer at the bottom of your UI." Marketplace policy 1120.3: "Add-ins must follow design guidelines without impeding the customer experience within the host application." | None found | Office's look; the brand in a footer bar. |
| An app inside an Atlassian product | Forge: Atlassian's design tokens "can be highly beneficial", and with them the app's colours "mirror and react to the active theme of the parent Atlassian app". The Marketplace approval guidelines: "If the UI breaks, your app will be rejected."; their trademark rule is about the app's name, not its look. | None found | Atlassian's tokens and the host's theme. |
| A Slack app | Slack: "Utilize your brand color to complement your app's avatar to more clearly brand your messages.", and for meaning, the colours users know, such as "green for confirmation, red for cancelling actions". | None found | Your brand colour on the avatar; Slack's meanings for green and red. |
| Colour as expression | Atlassian: "Don't use an accent when the color has semantic meaning." An accent is a colour with no meaning tied to it, in Atlassian's own roles. | None found | An expression colour never takes a status role (section 3). |
| Developer tools | Primer: "GitHub's UI offers two color modes, light and dark." and "Every pattern in Primer is built to work across all color modes out of the box." Vercel's Web Interface Guidelines, a general list: "Only animate when it clarifies cause & effect or when it adds deliberate delight". | None found | Both themes designed (section 9); motion for cause and effect (section 8). |
| Children | NN/g (Sherwin and Nielsen, 2019): "Kids expected some sites to play sound or have animation." | Think-aloud tests with 125 children in three rounds: in the table row "Animation and sound", children "Liked", adults "Usually disliked". | More motion may fit (section 8). |
| Older adults | W3C: "Some older people are particularly distracted by any movement and sound on web pages.", and the existing W3C accessibility standards "address most older user needs". | Nielsen (NN/g, 2013), with 75 people aged 65 and over and a group aged 21 to 55, on websites: "Users aged 65 and older are 43% slower at using websites than users aged 21–55", and they succeeded in 55.3% of tasks against 74.5%. Kane (NN/g, 2019), in three rounds with 123 people aged 65 and over: "Readability has remained an issue for seniors throughout all our studies over the years", and "text on mobile apps was often too small and lightly colored for older adults to read comfortably". | Less motion (section 8); the WCAG floor; text that is neither small nor light grey. |
| Checkout | Baymard, a research firm, in a 2026 blog post: "Enclosed design: Strip away main site navigation to prevent 'pogo-sticking' back to product pages, leaving only a logo 'escape hatch'" | None read | No main navigation in checkout; the logo as the way out. |

Three points the sources disagree on, settled:

- **Internal tools: one design system with small variants.** Give a staff screen the same tokens
  and components as the public product, with its own header and a compact control where the work
  needs it, such as the NHS's smaller button. Why: the sources that free internal tools from the
  public look still build on a shared system. The Home Office's system "builds on the GOV.UK design
  system", DWP's internal header is a component of DWP's design system, and GOV.UK expects that you
  will "sometimes need to use different patterns, for example if you're building something like an
  admin interface". One token file also keeps this file's one rule (section 1). DWP's question
  about "one thing per page" for expert users stays open (section 12).
- **Chart colours: four categories at most, as the Analysis Function sets.** It is the UK
  government's guidance for its analysts, a public body's rule rather than a vendor's, and four also
  meets the ONS's "five colours or fewer". The ONS's "Never use more than nine colours." sits in a
  warning about its Chartbuilder tool, so it is a limit of that tool, not a cap for charts in
  general. Atlassian advises 5 to 6 while it ships 8 categorical colours, and Carbon's palette page
  gives 14 colours in a fixed order and states no cap. With more categories, group the rest into
  "other", show fewer series, or change the chart type, the ways the ONS gives.
- **Status colours: a text label every time.** The sources agree on a second signal. The Analysis
  Function: "it is not possible to choose red, amber and green shades that have enough contrast
  with a white background and each other"; where a table needs a red, amber and green column, it
  lets text say what each colour means. Atlassian ships status colours for charts and says: "use
  other visual indicators or consider categorical colors as a better option". Carbon ships a
  four-colour alert palette, and its palette page gives no such advice. So a status in a chart or a
  table carries its word, and the colour repeats it (section 4).

### Alternatives considered for use cases

- **A look of their own for internal tools, as DWP and the Home Office give them.** Not taken as the
  default: a second look needs a second token file and a second review, and both departments still
  build on a shared system. It fits where a rule forbids the public brand on internal screens, as
  GOV.UK forbids the crown logo off service.gov.uk and asks for the Helvetica or Arial font stacks
  instead; then change the branding, not the system.
- **Five colours (the ONS) or five to six (Atlassian).** Not taken: four keeps within both, and
  comes from the cross-government guidance. A team that builds on Atlassian's or Carbon's chart
  palette may follow that system's own advice (section 12).
- **Status by colour alone, from a palette such as Carbon's alert colours.** Not taken: colour is
  never the only signal (WCAG SC 1.4.1, section 4), and the Analysis Function found no red, amber
  and green that all reach enough contrast on white and with each other.

## 11. Common mistakes

| Mistake | What goes wrong | The fix | Sources |
|---|---|---|---|
| A raw palette value in a component (`bg-blue-600`, `#2563eb`) | The dark theme and a rebrand miss it; nobody computed its contrast | A role token; clear the default palette (section 3) | Primer, Atlassian |
| Colour as the only signal | Users who cannot see the colour difference lose the meaning | A word or an icon, with colour as a repeat (section 4) | WCAG SC 1.4.1 |
| Grey text on a coloured surface, or pure black | Grey loses contrast on the colour; pure black is advised against by both sources, with no measurement given | The surface's foreground role; a near-black step of the palette (section 4) | Refactoring UI (second-hand), Impeccable |
| A border around everything | Visual noise that hides the structure it should show | Spacing, a second background, a divider where it carries meaning (section 7) | Linear (2026), Refactoring UI (summary), Hacker News commenters |
| A value off the scale (`gap-[18px]`) | Every screen drifts to its own rhythm | A step of the 4 px scale (section 6) | Tailwind, Carbon |
| Brand-size type or expressive motion on a task screen | The eye goes to decoration instead of the task | The product sizes and productive motion (sections 2, 5, 8) | Carbon, Geist, Atlassian |
| `transition: all`, or an animated `height` | Properties nobody meant to move, and costly frames | The properties listed, never `all` (section 8); which ones are cheap, [performance.md](../performance/performance.md) section 6 | Vercel |
| Motion that ignores `prefers-reduced-motion` | Sliding and scaling for a user who asked for less | A fade only, inside the media query (section 8) | MDN, Vercel |
| A dark-only theme | Worse reading performance for most users | Light by default, a switch, both designed (section 9) | NN/g |
| Glass, soft shadows or thin decorative type on controls | Contrast a checker cannot see, cues users cannot find | The product look; glass at most for chrome (section 10) | NN/g, CSS-Tricks |
| New icons or colours in place of a clarity fix | People still miss or misread the key points | Change what the screen says, in what order, and what stands out (sections 2 and 10) | FCA |
| Expressive or slow motion on an interaction repeated many times a day | The motion gets in the way of work the person repeats | Minimal motion, under 150 ms (section 8) | Atlassian |
| A chart with more than four colours, or a status shown by its colour | Readers cannot tell the categories apart; no red, amber and green all reach enough contrast with white and with each other | Four categories, the rest grouped; a word on every status (section 10) | Analysis Function, ONS, Atlassian |

### The looks generated UI falls into

Generated UI falls into a few default looks, and they change with each model and each version of a
design skill. The current list, with its sources, and how to steer the model away from it are in
[designing-with-claude-code.md](designing-with-claude-code.md) section 4. On an application screen
each of those looks is brand-mode type or colour on a task screen (section 2). So the lasting fix
is the mode and the token file, not a list of banned fonts.

## 12. Where it stops holding

- **Brand and marketing pages.** Expressive type, larger steps, a brand face and expressive motion
  belong there (section 2). Anthropic's frontend-design skill gives the rule for them: "Spend your
  boldness in one place." A brand page may have a token set of its own, as GitHub ships Primer
  Brand apart from Primer Product. The contrast floor, `prefers-reduced-motion` and the tokens-only
  rule still hold.
- **An application built on an established design system,** such as Material, Carbon or Primer. Its
  own tokens, scales, radii and durations replace the numbers here; the shape stays: roles in code,
  pairs for contrast, themes that swap values.
- **A native mobile application.** Apple's and Google's platform guidelines decide its look; Liquid
  Glass and Material 3 Expressive belong there (section 10).
- **Charts.** This practice asks these things of any chart: colour is never the only cue (section
  4), and a status carries a word (section 10); the marks of a chart meet the contrast that
  [accessibility.md](accessibility.md) section 9 gives for graphical objects, 3:1; a chart has a
  text or table alternative (1.1.1, [accessibility.md](accessibility.md) section 12); and the rows
  on charts and dashboards in section 10 set the rest: a plain chart chosen by the values and the
  story, four categories at most, the same colour for the same variable, the headline first on a
  dashboard. Those rows rest on government guidance (the UK Government Analysis Function, the ONS
  and the U.S. Web Design System) and on Carbon's and Atlassian's chart pages. Three things are
  still not covered. The values of a categorical palette: this file leaves them to the design system
  you build on. A chart library: no source read picks one, so check a candidate's accessibility
  before you use it. A chart palette for a dark theme: the EU Publications Office's guide notes that
  Datawrapper "changes the colours of all elements on the chart in dark mode to ensure a high enough
  contrast ratio with the dark background", and gives no palette and no ratio, and the Analysis
  Function's colour page gives no dark-theme guidance. The [README](README.md), "The points to
  adapt", names the gap.
- **Code no change touches.** It keeps its values until a change edits it
  ([refactoring.md](../../any-language/refactoring/refactoring.md) section 2).

### Not covered yet

No source read for this file settles these, as of October 2026:

- A controlled study of dense against airy layouts, for expert and for new users.
- A study that compares fields, such as finance, health and productivity, on looks or visual
  complexity against task performance. The nearest are one test on a health-information site
  (Thielsch et al.) and the FCA's credit-journey experiment (section 2).
- A controlled study from 2024-10 to 2026-10 of visual design and trust in banking web
  applications, beyond the one study of typical-looking home pages (Figl et al., section 10).
- A study from 2024-10 to 2026-10 of dark themes for reading code.
- A study from 2024-10 to 2026-10 of transition motion between screens, not in charts, against task
  time in work software.
- A bank's published design system with guidance on type, colour or density: Nedbank's covers motion
  only (section 10).
- Guidance in force from the US consumer-finance regulator, the CFPB, on interface design.
- Style principles from the design systems of education platforms.
- Whether Salesforce's AppExchange requires the Lightning look today: its official pages could not
  be read.
- A chart palette for a dark theme (the Charts bullet above).
- Whether "one thing per page" suits expert users of internal tools: DWP reports the question and
  leaves it open (section 10).

## 13. Review checklist

A review question per section. A red flag that fails a WCAG 2.2 A or AA criterion means the screen
is not ready. Any other single red flag is something to raise with the author; a screen that shows
two or more is not ready.

| Section | Ask | Red flag |
|---|---|---|
| 2. Mode | Is this a task screen, and does it look like one? | Brand-size type, a gradient hero or expressive motion on a screen behind the login |
| 2. Expression | Which case is the screen: effective, polished or a balance, and is each expressive moment one that section 2 names? | Expression spread over most of the screen |
| 3. Tokens | Does every colour, radius and shadow name a role, with `rounded-full` only on a circle or a pill and `transparent` only on a part that shows no colour? | A palette class (`bg-blue-600`), a hex value, or a role picked because its colour looked right |
| 4. Colour and contrast | Does every text-on-surface pair have its ratio in both themes? | A new pair with no ratio; colour as the only signal; grey text on a coloured surface |
| 5. Type | Are sizes steps of the scale, and does the hierarchy use weight and colour first? | A size in square brackets; running text wider than 75 characters; numbers in a column without `tabular-nums` |
| 6. Spacing and layout | Is every space a step of the 4 px scale? | A value in square brackets; a component that only adapts to the viewport |
| 7. Shape and borders | Are radii small and named by role (a circle or a pill takes `rounded-full`), and does each border carry meaning? | A border around every box; a decorative border as the only edge of a field |
| 8. Motion | Does motion answer an action, at a duration that fits its size (a loop that shows a wait keeps its utility's duration, section 8)? | `transition: all`; an animated layout property ([performance.md](../performance/performance.md) section 6); no reduced-motion rule; motion over 150 ms on an interaction repeated many times a day |
| 9. Themes | Was the dark theme looked at, not only computed? | A component that checks which theme is on; a colour set outside the token file |
| 10. Styles | Does the style keep sections 3 to 9? | Glass under text, soft shadows on controls, a style chosen because it is in fashion |
| 10. Use case | Does the screen follow its row in section 10's "By use case" table? | A chart with more than four categories; a status shown by colour alone; an app inside a host that ignores the host's rule in that table |

## 14. Sources

### Mode

1. IBM Carbon, Typography overview: https://carbondesignsystem.com/elements/typography/overview/ —
   the productive and expressive type sets, and why expressive type distracts in a product.
2. IBM Carbon, Motion overview: https://carbondesignsystem.com/elements/motion/overview/ —
   productive and expressive motion; the duration table and the curves (read as a summary);
   expressive motion kept for occasional, important moments, and the cases it names (own text,
   read 2026-10-29).
3. Atlassian Design System, Typography: https://atlassian.design/foundations/typography — the
   brand font and the in-app fonts; the heading sizes.
4. Vercel Geist, Typography and Materials: https://vercel.com/geist/typography and
   https://vercel.com/geist/materials — the sizes kept for marketing and hero areas; product radii
   and shadows.
5. GitHub Primer, Primer Brand and Primer Product: https://primer.style/brand and
   https://primer.style/product/getting-started/ — two design systems, one per mode.
6. Impeccable skill file: https://raw.githubusercontent.com/pbakaus/impeccable/main/.claude/skills/impeccable/SKILL.md
   — the "Operate" and "Persuade" modes (read in part).
7. Anthropic, frontend-design skill:
   https://raw.githubusercontent.com/anthropics/claude-code/main/plugins/frontend-design/skills/frontend-design/SKILL.md
   — motion that answers an action, structural devices that carry information, line length,
   "Spend your boldness in one place", the current list of looks to avoid (read 2026-10-01).

### Tokens

8. Primer, token names: https://primer.style/product/primitives/token-names/ — base, functional
   and component tiers (read as a summary).
9. Primer, colour usage: https://primer.style/product/getting-started/foundations/color-usage/ —
   base tokens never in code; tokens that change with the colour mode (read as a summary); two
   colour modes with every pattern built for both (own text, read 2026-10-29).
10. Material Web, theming: https://raw.githubusercontent.com/material-components/material-web/main/docs/theming/README.md
    and https://raw.githubusercontent.com/material-components/material-web/main/docs/theming/color.md
    — reference, system and component tokens; the `on-` pair rule (read through a summariser).
11. Atlassian, design tokens: https://atlassian.design/foundations/tokens/design-tokens — choose
    tokens by meaning, not value (read as a summary).
12. IBM Carbon, Themes and Colour tokens: https://carbondesignsystem.com/elements/themes/overview/
    and https://carbondesignsystem.com/elements/color/tokens/ — a role keeps its name across
    themes; layers (read as a summary).
13. shadcn/ui, Theming and Tailwind v4: https://ui.shadcn.com/docs/theming and
    https://ui.shadcn.com/docs/tailwind-v4 — the role names, the surface and foreground pairs, OKLCH
    values mapped with `@theme inline` (the theming page read as a summary).
14. Tailwind CSS, Theme variables: https://tailwindcss.com/docs/theme, and the default theme file
    https://raw.githubusercontent.com/tailwindlabs/tailwindcss/main/packages/tailwindcss/theme.css
    — `@theme`, its namespaces, `--color-*: initial`, the 4 px spacing unit, the type scale (read
    2026-10-01).

### Colour, contrast and themes

15. W3C, Understanding SC 1.4.3 Contrast (Minimum):
    https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html — the ratios of SC 1.4.3,
    1.4.6, 1.4.11 and 1.4.1; the ratio is not rounded.
16. W3C, WCAG 3.0 Working Draft: https://www.w3.org/TR/wcag-3.0/ — a draft not to be cited as a
    standard (2026-09-10). Eric Eggert, "WCAG 3 is not ready yet": https://yatil.net/blog/wcag-3-is-not-ready-yet
    — APCA cannot be relied on for compliance. Myndex, "Why APCA":
    https://github.com/Myndex/SAPC-APCA/blob/master/documentation/WhyAPCA.md — the case that WCAG 2
    overstates dark contrast, from APCA's author.
17. WebAIM, The WebAIM Million (2026): https://webaim.org/projects/million/ — low-contrast text on
    83.9% of home pages.
18. Refactoring UI, through a book review: https://updivision.com/blog/post/book-review-refactoring-ui-by-adam-wathan-steve-schoger,
    and "7 Practical Tips for Cheating at Design":
    https://medium.com/refactoring-ui/7-practical-tips-for-cheating-at-design-40c736799886 — the
    place to look for hierarchy by weight and colour, no pure black, fewer borders; read only
    through summaries, so not quoted.
19. Impeccable: https://impeccable.style — its anti-pattern list (overused fonts, grey text on
    colour, pure black).
20. Linear, "How we redesigned the Linear UI" (2024-03-28):
    https://linear.app/now/how-we-redesigned-the-linear-ui, and "Behind the latest design refresh"
    (2026-03-12): https://linear.app/now/behind-the-latest-design-refresh — LCH theming from three
    inputs, density, fewer borders, both themes designed.
21. MDN: `light-dark()` https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/light-dark,
    `color-scheme` https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme, `oklch()`
    https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/oklch — Baseline status and
    behaviour (read 2026-10-01).
22. NN/g, "Dark Mode vs. Light Mode" (2020): https://www.nngroup.com/articles/dark-mode/ — light
    mode performs better for most users; offer a switch.
23. web.dev, Learn Design, Theming: https://web.dev/learn/design/theming — follow the system
    setting with `color-scheme` (read as a summary).

### Type, spacing, layout, shape

24. "Readability" literature review, Visible Language (2025-12-23):
    https://journals.uc.edu/index.php/vl/article/view/8855 — no single size or face is best for
    everyone; 42 studies.
25. web.dev, Learn Design, Typography and layouts: https://web.dev/learn/design/typography,
    https://web.dev/learn/design/macro-layouts, https://web.dev/learn/design/micro-layouts — line
    length, single column first, container queries (read as a summary).
26. W3C, Understanding SC 1.4.8 Visual Presentation:
    https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html — the 80-character limit
    is level AAA.
27. Vercel, Web Interface Guidelines: https://vercel.com/design/guidelines,
    https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md and
    https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/AGENTS.md —
    `tabular-nums`, `color-scheme`, animation rules, reduced motion; one design team's rules;
    animate only for cause and effect or deliberate delight (own text, read 2026-10-29).
28. IBM Carbon, Spacing: https://carbondesignsystem.com/elements/spacing/overview/ — stay on the
    scale; steps may jump at breakpoints (read as a summary).
29. MDN, Container queries: https://developer.mozilla.org/en-US/docs/Web/CSS/@container — Baseline
    status (read 2026-10-01).
30. GitHub Primer, Size: https://primer.style/product/primitives/size/ — radii and border widths
    (read as a summary).
31. Atlassian, Elevation: https://atlassian.design/foundations/elevation — surface and shadow
    tokens used as pairs (read as a summary).

### Motion

32. Atlassian, Motion: https://atlassian.design/foundations/motion — durations, exits faster than
    entrances (read as a summary); motion as "a clarifying layer, not decoration", expressive motion
    for key brand moments, and motion matched to how often it is seen (own text, read 2026-10-29;
    the page is marked Early Access).
33. Material Components for Android, Motion:
    https://raw.githubusercontent.com/material-components/material-components-android/master/docs/theming/Motion.md
    — duration tokens and easing curves (read through a summariser).
34. Josh Comeau, CSS transitions: https://www.joshwcomeau.com/animation/css-transitions/ — the
    place to look for reduced motion (read as a snippet only).
35. MDN, `prefers-reduced-motion`:
    https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion — replace
    scaling and panning with fades; Baseline status (read 2026-10-01).

### Styles

36. Smashing Magazine, "Lessons from Swiss Style Graphic Design" (2009):
    https://www.smashingmagazine.com/2009/07/lessons-from-swiss-style-graphic-design/
37. NN/g, "Flat Design" (2015): https://www.nngroup.com/articles/flat-design/
38. uxdesign.cc Bootcamp, bento box: https://bootcamp.uxdesign.cc/web-design-trend-bento-box-95814d99ac62
    — a description only, anecdote class.
39. NN/g, "Neobrutalism" (2025): https://www.nngroup.com/articles/neobrutalism/
40. NN/g, "Glassmorphism" (2024): https://www.nngroup.com/articles/glassmorphism/
41. Apple Newsroom (2025-06-09):
    https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/,
    and NN/g, "Liquid Glass Is Cracked, and Usability Suffers in iOS 26" (2025-10):
    https://www.nngroup.com/articles/liquid-glass/ (read as a summary)
42. NN/g, "Skeuomorphism" (2024): https://www.nngroup.com/articles/skeuomorphism/
43. CSS-Tricks, "Neumorphism and CSS" (2020): https://css-tricks.com/neumorphism-and-css/
44. Google Design, expressive Material research:
    https://design.google/library/expressive-material-design-google-research, and the Material 3
    Expressive launch (2025-05-13):
    https://blog.google/products-and-platforms/platforms/android/material-3-expressive-android-wearos-launch/
    — the research page's studies, its definition of expressive and its caveats on banking and
    familiar patterns (own text, read 2026-10-29); the owner's own research, with no method given.

### The looks of generated UI

45. Anthropic, "Improving frontend design through Skills" (2025-11-12):
    https://www.claude.com/blog/improving-frontend-design-through-skills — the purple-gradient and
    Inter default.
46. Anthropic, Prompting Claude Opus 4.8, "Design and frontend defaults":
    https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8
    — the warm-cream, serif and terracotta house style (read 2026-10-01).
47. Skillselion, on the frontend-design skill's three looks (2026-08-28):
    https://dev.to/skillselion/anthropics-frontend-design-skill-names-the-three-cliche-ai-looks-hex-codes-included-f29
    — the broadsheet look; a secondary reading of the skill.
48. Hacker News, "Tells of a Slop UI": https://news.ycombinator.com/item?id=49867038 — heavy
    borders among the tells several commenters name; anecdote.

### Baseline dates

49. webstatus.dev: https://webstatus.dev — the "Baseline widely available since" dates of
    `oklch()`, container size queries, `prefers-reduced-motion` and `color-scheme` (read
    2026-10-02).

### Expression, and what was measured

Sources 50 to 100 were read in their own text on 2026-10-29, unless a line says otherwise.

50. IBM Carbon, Typography style strategies:
    https://carbondesignsystem.com/elements/typography/style-strategies/ — productive type for
    product design, expressive type for editorial pages, blended by "moments".
51. GitHub Primer, Motion and animation:
    https://primer.style/accessibility/design-guidance/motion-and-animation/ — consider first
    whether motion is needed at all; accessibility guidance.
52. Microsoft Fluent 2, Motion: https://fluent2.microsoft.design/motion — motion with purpose;
    delight named as an aim.
53. John Phamous, "Teaching agents product design at Vercel" (Vercel blog, 2026-06-25):
    https://vercel.com/blog/teaching-agents-product-design-at-vercel — the product-design skill's
    line on decorative novelty, in a simplified view of the skill; a case.
54. Frank Bentley, Lennard Schmidt, Alyssa Sheehan, Bianca Gallardo and Ying Wang, "Usability
    Hasn't Peaked: Exploring How Expressive Design Overcomes the Usability Plateau" (CHI '26):
    https://research.google/pubs/usability-hasnt-peaked-exploring-how-expressive-design-overcomes-the-usability-plateau/
    — research on Google's own design system, listed by Google Research; abstract only.
55. Meinald T. Thielsch, Russell Haines and Leonie Flacke, "Experimental investigation on the
    effects of website aesthetics on user performance in different virtual tasks" (PeerJ 7:e6516,
    2019): https://pmc.ncbi.nlm.nih.gov/articles/PMC6388663/ — research, 331 people.
56. Sebastian A. C. Perrig, David Ueffing, Klaus Opwis and Florian Brühlmann, "Smartphone app
    aesthetics influence users' experience and performance" (Frontiers in Psychology, 2023):
    https://pmc.ncbi.nlm.nih.gov/articles/PMC10306164/ — research, 281 people analysed.
57. Kate Moran, "The Aesthetic-Usability Effect" (NN/g, 2024, reviewed 2026-09-01):
    https://www.nngroup.com/articles/aesthetic-usability-effect/ — a practitioner's article that
    cites studies.
58. FCA, "Consumer understanding: good practice and areas for improvement" (2026-03-13):
    https://www.fca.org.uk/publications/good-and-poor-practice/consumer-understanding-good-practice-areas-improvement
    — a regulator's review, with a survey of 38 firms.
59. Cameron Belton, Daniel Bogiatzis-Gibbons, Isaac Keeley, Cherryl Ng, Gráinne Murphy and Max
    Spohn, "Digital design for financial products and services: Consumer impact of sludge,
    deceptive design, timeliness and simplification" (FCA Research Note, 2025-07-31):
    https://www.fca.org.uk/publication/research-notes/digital-design-financial-products-services.pdf
    — research by the regulator, 6,045 people.

### Motion and themes for an audience or a chart

60. Jeffrey Heer and George G. Robertson, "Animated Transitions in Statistical Data Graphics" (IEEE
    TVCG, 2007): https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf —
    research, 24 people.
61. Katie Sherwin and Jakob Nielsen, "Children's UX: Usability Issues in Designing for Young People"
    (NN/g, 2019): https://www.nngroup.com/articles/childrens-websites-usability-issues/ — research,
    125 children.
62. W3C WAI, "Developing Websites for Older People": https://www.w3.org/WAI/older-users/developing/
    — movement and sound distract some older people.
63. W3C WAI, "Older Users and Web Accessibility": https://www.w3.org/WAI/older-users/ — the existing
    standards cover most needs of older users.
64. Jakob Nielsen, "Usability for Senior Citizens: Improved, But Still Lacking" (NN/g, 2013):
    https://www.nngroup.com/articles/usability-seniors-improvements/ — research on websites; old.
65. Lexie Kane, "Usability for Older Adults: Challenges and Changes" (NN/g, 2019):
    https://www.nngroup.com/articles/usability-for-senior-citizens/ — research, 123 people.
66. Tobias Julien Ettling, Dominik Steinmann, Kenan Bektaş and Amine Abbad-Andaloussi, "An Eye
    Tracking Study on the Effects of Dark and Light Themes on User Performance and Workload" (ETRA
    '25): https://doi.org/10.1145/3715669.3725879 — research, 15 people; read in the authors'
    open-access copy.
67. Zack While and Ali Sarvghad, "Dark Mode or Light Mode? Exploring the Impact of Contrast Polarity
    on Visualization Performance Between Age Groups" (IEEE VIS '24, short paper):
    https://arxiv.org/abs/2409.10841 — research; abstract only.
68. T. Gazit, T. Tager-Shafrir, H.-X. Zhong, P. C. K. Hung and V. Cheung, "The dark side of the
    interface: examining the influence of different background modes on cognitive performance"
    (Ergonomics, 2025): https://eprints.whiterose.ac.uk/id/eprint/231852 — research, 173 people;
    abstract only.

### Use cases

69. Nedbank, Design System, Motion guidelines:
    https://design.nedbank.co.za/design-system/foundations/motion-guidelines.html — a bank's motion
    guidance.
70. Figl et al., "The danger of not being typical" (Electronic Markets, 2025):
    https://pmc.ncbi.nlm.nih.gov/articles/PMC12078413/ — research, 107 people.
71. Julianne Stanford, Ellen R. Tauber, B. J. Fogg and Leslie Marable, "Experts vs. Online
    Consumers: A Comparative Credibility Study of Health and Finance Web Sites" (Consumer WebWatch,
    2002): https://advocacy.consumerreports.org/wp-content/uploads/2013/05/expert-vs-online-consumers.pdf
    — research, sponsored by Consumer WebWatch; read in a Wayback Machine copy of that link.
72. FCA Handbook, PRIN 2A.5 Communications: https://handbook.fca.org.uk/handbook/PRIN/2A/5.html;
    FCA, FG22/5, Final non-Handbook Guidance for firms on the Consumer Duty (July 2022):
    https://www.fca.org.uk/publication/finalised-guidance/fg22-5.pdf; FCA, "Digital design in
    customers' online journeys" (2025):
    https://www.fca.org.uk/publications/good-and-poor-practice/digital-design-customers-online-journeys
    — prominence, testing, layering and friction under the Consumer Duty.
73. Atlassian, Illustrations: https://atlassian.design/foundations/illustrations — no collage or
    purely decorative illustration in product.
74. GOV.UK, Government Design Principles: https://www.gov.uk/guidance/government-design-principles;
    "Making your service look like GOV.UK":
    https://www.gov.uk/service-manual/design/making-your-service-look-like-govuk; "Use GOV.UK
    domains and the GOV.UK Design System":
    https://www.gov.uk/guidance/use-govuk-domains-and-the-govuk-design-system; "Services for
    government users" (2018):
    https://www.gov.uk/service-manual/design/services-for-government-users — public and internal
    services (read 2026-10-29).
75. DWP Design System, Internal service header:
    https://design-system.dwp.gov.uk/components/internal-service-header, and Internal systems:
    https://design-system.dwp.gov.uk/get-started/internal-systems — the header for internal
    services; the open question on "one thing per page".
76. Home Office Design System, Get started:
    https://design.homeoffice.gov.uk/design-system/get-started — Home Office styles for internal
    services, in prototypes.
77. NHS Service Manual, Design system: https://service-manual.nhs.uk/design-system; Buttons:
    https://service-manual.nhs.uk/design-system/components/buttons; Design principles:
    https://service-manual.nhs.uk/design-system/design-principles; Accessibility, design:
    https://service-manual.nhs.uk/accessibility/design — one system for the public and staff,
    smaller buttons, trust, contrast.
78. Kate Kaplan, "Supporting 'Power Users' Isn't Enough: 3 Complex-App User Types" (NN/g, 2025):
    https://www.nngroup.com/articles/complex-apps-users/ — an opinion with no new data.
79. Yimeng Liu and Misha Sra, "Designing Scaffolded Interfaces for Enhanced Learning and Performance
    in Professional Software" (arXiv:2505.12101, 2025): https://arxiv.org/html/2505.12101 — a
    preprint, 32 beginners and 8 experts.
80. U.S. Web Design System, Typography: https://designsystem.digital.gov/components/typography/ — a
    neutral face for interfaces.
81. IBM Carbon, Data table usage: https://carbondesignsystem.com/components/data-table/usage/ — row
    sizes.
82. SAP, SAPUI5 documentation, Content densities:
    https://raw.githubusercontent.com/SAP-docs/sapui5/main/docs/04_Essentials/content-densities-e54f729.md,
    and How to use densities for controls:
    https://raw.githubusercontent.com/SAP-docs/sapui5/main/docs/04_Essentials/how-to-use-densities-for-controls-13e6f3b.md
    — compact, cozy and condensed densities.
83. Atlassian, Spacing: https://atlassian.design/foundations/spacing, and Button usage:
    https://atlassian.design/components/button/usage — compact pieces of UI and the compact button.
84. Shopify, App design guidelines: https://shopify.dev/docs/apps/design, and Layout:
    https://shopify.dev/docs/apps/design/layout — match the admin; one density per page.
85. Shopify, Built for Shopify: https://shopify.dev/docs/apps/launch/built-for-shopify, its
    requirements: https://shopify.dev/docs/apps/launch/built-for-shopify/requirements, and the
    Shopify App Store requirements:
    https://shopify.dev/docs/apps/launch/shopify-app-store/app-store-requirements — what each review
    checks (read 2026-10-29).
86. Microsoft, Teams, Designing your custom app:
    https://learn.microsoft.com/en-us/microsoftteams/platform/concepts/design/design-teams-app-overview,
    and Teams Store validation guidelines:
    https://learn.microsoft.com/en-us/microsoftteams/platform/concepts/deploy-and-publish/appsource/prepare/teams-store-validation-guidelines
    — native or distinct, never a blend; what blocks publishing (read 2026-10-29).
87. Microsoft, Office Add-ins, Design the UI:
    https://learn.microsoft.com/en-us/office/dev/add-ins/design/add-in-design, and Branding patterns:
    https://learn.microsoft.com/en-us/office/dev/add-ins/design/branding-patterns — complement
    Office; the brand in a footer bar.
88. Microsoft, Commercial marketplace certification policies:
    https://learn.microsoft.com/en-us/legal/marketplace/certification-policies — add-ins and Teams
    apps must not impede the host (read 2026-10-29).
89. Atlassian, Forge design tokens and theming:
    https://developer.atlassian.com/platform/forge/design-tokens-and-theming/, and Marketplace app
    approval guidelines: https://developer.atlassian.com/platform/marketplace/app-approval-guidelines/
    — the host's tokens and theme; an app that breaks the host is rejected.
90. Slack, App design: https://docs.slack.dev/surfaces/app-design — the brand colour on the avatar.
91. Atlassian, Color: https://atlassian.design/foundations/color — no accent where colour has a
    meaning.
92. Carl MacDonald, "Checkout UX" (Baymard Institute blog, 2026-04-23):
    https://baymard.com/blog/checkout-flow-ux-optimization — enclosed checkout.

### Charts and dashboards

93. UK Government Analysis Function, Data visualisation: charts:
    https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/; Accessible
    charts, a checklist of the basics:
    https://analysisfunction.civilservice.gov.uk/policy-store/charts-a-checklist/; Data
    visualisation: colours:
    https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-colours-in-charts/;
    Testing dashboards for design and accessibility:
    https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-testing-dashboards-for-design-and-accessibility/
    — plain charts, four categories, red, amber and green with text, dashboards headline first.
94. ONS Service Manual, Using colours in charts:
    https://service-manual.ons.gov.uk/data-visualisation/colours/using-colours-in-charts — five
    colours or fewer; the nine-colour limit of its Chartbuilder tool.
95. U.S. Web Design System, Data visualizations:
    https://designsystem.digital.gov/components/data-visualizations/ — common chart types, care with
    colour.
96. IBM Carbon, Data visualization: dashboards:
    https://carbondesignsystem.com/data-visualization/dashboards/, and colour palettes:
    https://carbondesignsystem.com/data-visualization/color-palettes/ — the most important at the
    top; 14 colours in a fixed order and an alert palette (the palette page calls itself a work in
    progress).
97. Atlassian, Data visualization color:
    https://atlassian.design/foundations/color/data-visualization-color — 5 to 6 colours; status
    colours with other visual indicators.
98. Publications Office of the European Union, Data Visualisation Guide, Dark mode (2023):
    https://data.europa.eu/apps/data-visualisation-guide/dark-mode — one tool recolours charts in
    dark mode; no palette.

### Material 3 Expressive on the web

99. Google, `@material/web` release v2.5.0:
    https://github.com/material-components/material-web/releases/tag/v2.5.0 — Expressive components
    added under `labs`; the `labs/README.md` of that release marks the folder as not for production
    (read 2026-10-29).
100. Google, `@material/web` README:
     https://raw.githubusercontent.com/material-components/material-web/main/README.md — the library
     is in maintenance mode (read 2026-10-29).
