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
Every line that carries a read date is to be distrusted after 2027-04-01 until it is read again;
the README's "How to adopt" says how to list those lines.

The one rule: **an application screen is designed in product mode, and every visual value on it
comes from a token or a scale, never from one screen's taste.** Each section below is one part of
that rule, or one way it breaks.

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
application has no motion and no switch yet. Nothing was run in a browser. The contrast numbers in
section 4 were computed from the token values with the WCAG 2 formula, not measured on a screen.

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
  with tokens, a change made in one place shows across the whole system.
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
   Every surface role has a -foreground role that keeps text readable on it. */
:root {
  color-scheme: light dark;

  --background: light-dark(oklch(0.99 0 0), oklch(0.16 0 0));
  --foreground: light-dark(oklch(0.2 0 0), oklch(0.96 0 0));
  --muted: light-dark(oklch(0.96 0 0), oklch(0.24 0 0));
  --muted-foreground: light-dark(oklch(0.45 0 0), oklch(0.74 0 0));
  --border: light-dark(oklch(0.88 0 0), oklch(0.34 0 0));
  --primary: light-dark(oklch(0.45 0.16 255), oklch(0.74 0.13 255));
  --primary-foreground: light-dark(oklch(0.99 0 0), oklch(0.16 0 0));
  --destructive: light-dark(oklch(0.5 0.19 27), oklch(0.74 0.15 27));
  --success: light-dark(oklch(0.45 0.12 150), oklch(0.77 0.14 150));
  --ring: light-dark(oklch(0.55 0.16 255), oklch(0.8 0.11 255));
}

@theme inline {
  /* Clearing the default palette leaves the roles below as the only colours: `bg-blue-500`
     produces no style at all. */
  --color-*: initial;
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-border: var(--border);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-destructive: var(--destructive);
  --color-success: var(--success);
  --color-ring: var(--ring);

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
- `--color-*: initial` removes Tailwind's palette. A raw colour such as `bg-blue-500` then produces
  no style, so the mistake shows the first time anyone looks at the screen, not in a review months
  later. The comment keeps that reason at the line, because the line looks removable.
- Every text role has the surface it sits on, and each pair's contrast is computed in both themes
  (section 4).
- The two radii are named by role (`control`, `surface`), not by size, and sit at the small values
  product screens use (section 7).
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
      // shadows. pointer-coarse:min-h-11: 44 px tall on a touch screen; 36 px is for a mouse.
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
      // shadows. pointer-coarse:min-h-11: 44 px tall on a touch screen; 36 px is for a mouse.
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
  border on background                 light 1.39 dark 1.65 decorative, no floor
  ```

  Why it is good: every pair a screen can use is listed with the floor it must meet, in both
  themes. The focus ring is held to 3:1, and the border is marked decorative, so nobody uses it
  as the only edge of a control (section 7).

  Check: when the token file changes, is every pair's ratio, in both themes, at or above its
  floor?
- **Use the WCAG 2 ratios as the reference, and look at the dark theme with your own eyes as
  well.** WCAG 3 and APCA are not standards yet; why, and what to do about dark pairs, is
  [accessibility.md](accessibility.md) section 9.
- **Never let colour be the only signal** (SC 1.4.1, level A). A status, an error or a required
  field also carries a word or an icon.
- **Build the palette in a perceptual colour space from a few inputs.** Tailwind 4's default
  palette and shadcn/ui's themes are OKLCH, and `oklch()` is Baseline widely available since May
  2023 (read 2026-10-01). Linear rebuilt its theming in LCH and went from 98 theme variables to 3:
  a base colour, an accent and a contrast level (read as a snippet only).
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
  // The word carries the status. The colour repeats it and is never the only signal.
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
  the default nobody chose (section 11).
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
<td>{formatCents(invoice.amountCents)}</td>
<td>{invoice.dueOn}</td>
```

The digits shift from row to row. The same cells from the application's invoice table, cut to the
two cells that hold numbers:

```tsx
<td className="tabular-nums">{formatCents(invoice.amountCents)}</td>
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
- **Lay a screen out in one column first, and add columns as the space grows.** web.dev starts
  macro layouts single-column and builds them with Grid.
- **Use media queries for the page and container queries for a component,** so a component adapts
  to its own width wherever it is placed. web.dev's layout modules give the split and the CSS:
  `container-type: inline-size` on the parent and `@container (min-width: 25em)` on the rule.
  Container size queries are Baseline widely available since February 2023 (read 2026-10-01).
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
- **Draw a border only where it tells the reader something.** Anthropic's frontend-design skill:
  "Structural devices like outlines, borders, numbering, eyebrows, dividers, labels, etc., encode
  useful information about the content rather than decorate it." Linear's 2026 refresh removed
  borders that "had quietly proliferated" and softened the contrast of the rest. Refactoring UI
  (read through a summary) suggests spacing, two background colours or a shadow in place of a
  border.
- **A divider may be decorative; the edge of a control may not.** The application's `border` role
  is 1.39:1 in the light theme, which is fine for the line between table rows. When the edge is
  what shows the user where a text field is, it needs 3:1 (SC 1.4.11). Give that edge a role of its
  own, as shadcn/ui does with `input`, and compute it against 3:1.
- **Keep surfaces in the page flat and give floating layers the shadow.** Geist puts minimal shadow
  on surfaces in the page and progressively stronger shadows on layers that float above it, such as
  a menu or a dialog.
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
- **Animate only `transform` and `opacity`, and list the properties you animate.** Vercel's
  guidelines: "NEVER: Animate layout props (`top`, `left`, `width`, `height`)" and "NEVER:
  `transition: all`—list properties explicitly". Josh Comeau calls `transform` and `opacity` cheap
  to animate and scales with `transform` instead of animating `width` or `height` (read as a snippet
  only). What animation costs at run time is [performance.md](../performance/performance.md) section 6.

  The motion blocks of this section (the two below and the reduced-motion one after them) are not
  part of the reference application, which has no motion yet; the two custom properties join its
  token file with the first component that moves.

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
    transition:
      opacity var(--motion-duration-small) var(--motion-ease-enter),
      transform var(--motion-duration-small) var(--motion-ease-enter);
  }
  ```

  Why it is good: only the two cheap properties move, and a change to the panel's size snaps
  instead of animating. The duration and the curve are tokens, as the rule above asks, so every
  component that moves takes the same two values. 150 ms is in the range for a small change, and
  `ease-out` decelerates into place, the entrance curve; a panel that also leaves gets the
  accelerating curve and a shorter time on its way out (the rules above).
- **Honour `prefers-reduced-motion`: keep the fade, drop the movement.** MDN advises replacing
  scaling and panning with opacity fades, and the media query is Baseline widely available since
  January 2020 (read 2026-10-01). WCAG asks for it only at level AAA (SC 2.3.3); Vercel's guidelines
  and Josh Comeau ask for it with no level attached. The block below is not from the reference
  application either; it uses the two tokens of the block above.

  ```css
  @media (prefers-reduced-motion: reduce) {
    .invoice-details {
      transition: opacity var(--motion-duration-small) var(--motion-ease-enter);
    }
  }
  ```

  Why it is good: a user who asked the system for less motion still sees that the panel changed,
  through the fade, and nothing slides or scales.

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
  page canvas in the matching theme. `color-scheme` is Baseline widely available since January 2022
  (read 2026-10-01); Vercel's guidelines ask for it too.

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
| Material 3 Expressive | Google's 2025 update for Android and Wear OS: "color, shape, size, motion, and containment", springy motion, dynamic colour. | Android apps. On the web, take nothing from it by default. | Google's own research reports 46 studies, more than 18,000 participants and key elements spotted "up to four times faster". It is the vendor's research on its own Android components, not replicated, methods not seen. Its own caveat: "Context still matters"; breaking familiar patterns reduced usability. |
| Dark-first | Light text on a dark background as the only or the default theme. | As one of two designed themes, yes. As the default for a general audience, no. | NN/g (2020): light mode "leads to better performance most of the time" for people with normal vision. Linear designs both themes rather than dark only. WCAG 2 math may flatter dark pairs (section 4). |

To use a style on a product screen, take the parts that keep sections 3 to 9: a grid, neutral type,
flat surfaces with clear cues. Leave the parts that break them: translucent layers under text, soft
shadows on controls, decorative motion, type at brand sizes.

## 11. Common mistakes

| Mistake | What goes wrong | The fix | Sources |
|---|---|---|---|
| A raw palette value in a component (`bg-blue-600`, `#2563eb`) | The dark theme and a rebrand miss it; nobody computed its contrast | A role token; clear the default palette (section 3) | Primer, Atlassian |
| Colour as the only signal | Users who cannot see the colour difference lose the meaning | A word or an icon, with colour as a repeat (section 4) | WCAG SC 1.4.1 |
| Grey text on a coloured surface, or pure black | Grey loses contrast on the colour; pure black is advised against by both sources, with no measurement given | The surface's foreground role; a near-black step of the palette (section 4) | Refactoring UI (second-hand), Impeccable |
| A border around everything | Visual noise that hides the structure it should show | Spacing, a second background, a divider where it carries meaning (section 7) | Linear (2026), Refactoring UI (summary), Hacker News commenters |
| A value off the scale (`gap-[18px]`) | Every screen drifts to its own rhythm | A step of the 4 px scale (section 6) | Tailwind, Carbon |
| Brand-size type or expressive motion on a task screen | The eye goes to decoration instead of the task | The product sizes and productive motion (sections 2, 5, 8) | Carbon, Geist, Atlassian |
| `transition: all`, or an animated `height` | Properties nobody meant to move, and costly frames | `transform` and `opacity`, listed (section 8) | Vercel, Josh Comeau |
| Motion that ignores `prefers-reduced-motion` | Sliding and scaling for a user who asked for less | A fade only, inside the media query (section 8) | MDN, Vercel |
| A dark-only theme | Worse reading performance for most users | Light by default, a switch, both designed (section 9) | NN/g |
| Glass, soft shadows or thin decorative type on controls | Contrast a checker cannot see, cues users cannot find | The product look; glass at most for chrome (section 10) | NN/g, CSS-Tricks |

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
- **Charts.** This practice already asks three things of any graphic: colour is never the only cue
  (section 4); the marks of a chart meet the contrast that
  [accessibility.md](accessibility.md) section 9 gives for graphical objects, 3:1; and a chart has a
  text or table alternative (1.1.1, [accessibility.md](accessibility.md) section 12). No source
  read picks a chart library or a categorical palette, so check a candidate's accessibility before
  you use it. The [README](README.md), "The points to adapt", names the gap.
- **Code no change touches.** It keeps its values until a change edits it
  ([refactoring.md](../../any-language/refactoring/refactoring.md) section 2).

## 13. Review checklist

A review question per section. A single red flag is something to raise with the author; a screen
that shows two or more is not ready.

| Section | Ask | Red flag |
|---|---|---|
| 2. Mode | Is this a task screen, and does it look like one? | Brand-size type, a gradient hero or expressive motion on a screen behind the login |
| 3. Tokens | Does every colour, radius and shadow name a role? | A palette class (`bg-blue-600`), a hex value, or a role picked because its colour looked right |
| 4. Colour and contrast | Does every text-on-surface pair have its ratio in both themes? | A new pair with no ratio; colour as the only signal; grey text on a coloured surface |
| 5. Type | Are sizes steps of the scale, and does the hierarchy use weight and colour first? | A size in square brackets; running text wider than 75 characters; numbers in a column without `tabular-nums` |
| 6. Spacing and layout | Is every space a step of the 4 px scale? | A value in square brackets; a component that only adapts to the viewport |
| 7. Shape and borders | Are radii small and named by role, and does each border carry meaning? | A border around every box; a decorative border as the only edge of a field |
| 8. Motion | Does motion answer an action, at a duration that fits its size? | `transition: all`; an animated `width` or `height`; no reduced-motion rule |
| 9. Themes | Was the dark theme looked at, not only computed? | A component that checks which theme is on; a colour set outside the token file |
| 10. Styles | Does the style keep sections 3 to 9? | Glass under text, soft shadows on controls, a style chosen because it is in fashion |

## 14. Sources

### Mode

1. IBM Carbon, Typography overview: https://carbondesignsystem.com/elements/typography/overview/ —
   the productive and expressive type sets, and why expressive type distracts in a product.
2. IBM Carbon, Motion overview: https://carbondesignsystem.com/elements/motion/overview/ —
   productive and expressive motion; the duration table and the curves (read as a summary).
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
   base tokens never in code; tokens that change with the colour mode (read as a summary).
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
    `tabular-nums`, `color-scheme`, animation rules, reduced motion; one design team's rules.
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
    entrances (read as a summary).
33. Material Components for Android, Motion:
    https://raw.githubusercontent.com/material-components/material-components-android/master/docs/theming/Motion.md
    — duration tokens and easing curves (read through a summariser).
34. Josh Comeau, CSS transitions: https://www.joshwcomeau.com/animation/css-transitions/ — the
    place to look for cheap properties and reduced motion (read as a snippet only).
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
