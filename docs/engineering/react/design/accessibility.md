# Accessibility rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. The standard and the law](#2-the-standard-and-the-law)
- [3. Native elements first, ARIA second](#3-native-elements-first-aria-second)
- [4. Widget patterns and dialogs](#4-widget-patterns-and-dialogs)
- [5. Focus](#5-focus)
- [6. Route changes in a single-page app](#6-route-changes-in-a-single-page-app)
- [7. Live regions and status messages](#7-live-regions-and-status-messages)
- [8. Forms and errors](#8-forms-and-errors)
- [9. The numbers](#9-the-numbers)
- [10. Automated checks](#10-automated-checks)
- [11. The manual pass](#11-the-manual-pass)
- [12. Common mistakes](#12-common-mistakes)
- [13. Where the rules stop holding](#13-where-the-rules-stop-holding)
- [14. Review checklist](#14-review-checklist)
- [15. Sources](#15-sources)

## 1. Purpose and the one rule

This file is for everyone who builds or reviews a screen of a React application: people and AI
agents alike. Read it before you write a control, a form, a widget, a dialog or a route, and when
you review one.

It covers the build side of accessibility: which element to use, when ARIA is needed, where focus
goes, what a screen reader hears, and how to check all of it. How a screen looks, its tokens and
scales, is [visual-design.md](visual-design.md) sections 3, 5 and 6. How a screen behaves, its
feedback, forms, states and navigation, is [ux.md](ux.md) sections 2 to 4, 6 and 7. How one component is written is
[components.md](../components/components.md). The examples come from one invented application,
the billing screens of Acme Corp. Its code was type-checked, linted, unit-tested and built;
nothing in it was run in a browser or with a screen reader.
Every line that carries a read date is to be distrusted after 2027-04-01 until it is read again;
the README's "How to adopt" says how to list those lines.

The one rule: **use the native HTML element that already has the role and the keyboard behaviour
you need, add ARIA only where HTML has no such element, and then keep every promise the ARIA role
makes.** The target is WCAG 2.2 at level AA. A screen is done when it passes the automated checks
of section 10 and the manual pass of section 11. A tool never finds everything: the measured
figures run from 29% to 57%, each on a different denominator (section 10).

Why it matters:

- In WebAIM's 2026 scan of one million home pages, 95.9% had WCAG 2 failures that a tool could
  detect. The six most common were low-contrast text (83.9% of pages), images with no text
  alternative (53.1%), form fields with no label (51%), links with no text (46.3%), buttons with
  no text (30.6%) and no page language (13.5%). Each of them is fixed in the source the team
  ships, not by a script on top of it (section 12).
- The law in the EU and in the US points at WCAG (section 2).

## 2. The standard and the law

Read 2026-10-01. Each line is a moving target: re-check it before you rely on it. This section
says which version each law points at; it is not legal advice.

| What | Status | What it means for the build |
|---|---|---|
| WCAG 2.2 | W3C Recommendation since 2023-10-05; current edition 2024-12-12. WCAG 2.0, 2.1 and 2.2 all stay valid | the target, at level AA. Content that meets 2.2 also meets 2.1, so it meets the 2.1 AA the laws below ask for |
| WCAG 3 | Working Draft (2026-09-10). It says it is inappropriate to cite it as anything but work in progress | no rule here rests on it; its contrast method is not decided |

The European Accessibility Act applies from 2025-06-28 and points at EN 301 549; the US rules point
at WCAG 2.1 AA. A build that meets WCAG 2.2 AA meets the 2.1 AA they ask for. This is not legal
advice.

The criteria a React screen meets most often in code, with the section of this file that handles
each. The levels were re-read in the WCAG 2.2 text on 2026-10-01.

| Criterion | Level | What the code does | Section |
|---|---|---|---|
| 1.1.1 Non-text Content | A | an image has a text alternative, or `alt=""` when it is decoration | 12 |
| 1.3.1 Info and Relationships | A | the structure the eye sees is in the markup: headings, tables, labels, groups | 3, 8 |
| 1.3.5 Identify Input Purpose | AA | a field about the user carries its `autoComplete` token | 8 |
| 1.4.1 Use of Color | A | colour is never the only cue | 9 |
| 1.4.3 Contrast (Minimum) | AA | 4.5:1 for text, 3:1 for large text | 9 |
| 1.4.4 Resize Text | AA | text at 200% loses nothing | 9, 11 |
| 1.4.10 Reflow | AA | no scrolling in two directions at 320 CSS px wide | 9, 11 |
| 1.4.11 Non-text Contrast | AA | 3:1 for controls, focus indicators and graphics that carry meaning | 5, 9 |
| 1.4.12 Text Spacing | AA | wider spacing set by the user loses nothing | 9, 11 |
| 2.1.1 Keyboard, 2.1.2 No Keyboard Trap | A | everything works from the keyboard, and focus can always leave | 3, 4, 5 |
| 2.4.2 Page Titled | A | each screen has its own title | 6 |
| 2.4.3 Focus Order | A | focus moves in an order that keeps the meaning | 4, 5 |
| 2.4.4 Link Purpose (In Context) | A | a link's text, with its context, says where it goes | 3 |
| 2.4.7 Focus Visible | AA | the focused element shows it | 5 |
| 2.4.11 Focus Not Obscured (Minimum) | AA, new in 2.2 | nothing sticky hides the focused element entirely | 5 |
| 2.5.8 Target Size (Minimum) | AA, new in 2.2 | 24 by 24 CSS px, or the spacing exception | 9 |
| 3.3.1 Error Identification, 3.3.2 Labels or Instructions | A | errors in text; every field labelled | 8 |
| 3.3.7 Redundant Entry | A, new in 2.2 | the same process does not ask twice for the same data | 8 |
| 3.3.8 Accessible Authentication (Minimum) | AA, new in 2.2 | no memory test or puzzle at login without an alternative | 8 |
| 4.1.2 Name, Role, Value | A | each control exposes its name, role and state | 3, 4 |
| 4.1.3 Status Messages | AA | results, waits and errors reach a screen reader without moving focus | 6, 7 |

WCAG 2.2 also added 2.5.7 Dragging Movements (AA: what works by dragging also works with a single
pointer, without the drag) and 3.2.6 Consistent Help (A). It removed 4.1.1 Parsing.

## 3. Native elements first, ARIA second

When HTML has an element with the role and the behaviour you need, use it: `<button>` for an
action, `<a href>` for a move to another place, `<table>` for data in rows and columns, `<label>`
for a field's name, `<fieldset>` and `<legend>` for a group of fields, `<dialog>` for a modal. The
native element brings its keyboard behaviour, its focus and its role; a `div` with a role brings
only the role. W3C's "Using ARIA" calls this the first rule of ARIA: "If you can use a native HTML
element or attribute with the semantics and behavior you require already built in, instead of
re-purposing an element and adding an ARIA role, state or property to make it accessible, then do
so." That document's status is now "Discontinued Draft" (2026-02-24); the ARIA Authoring Practices
Guide (APG) says the same in its own words.

When you give an element an ARIA role, implement the keyboard behaviour of that role's pattern
(section 4). A role changes what a screen reader announces and adds no behaviour: a `div` with
`role="button"` is announced as a button and still does nothing on Enter or Space. The APG's
heading for this is "No ARIA is better than bad ARIA", and its reason: "Incorrect ARIA
misrepresents visual experiences, with potentially devastating effects on their corresponding
non-visual experiences." WebAIM's 2026 scan points the same way: home pages with ARIA averaged 59.1
detected errors, pages without it 42. That is a correlation across one million pages, not proof
that ARIA causes the errors.

### Every control has a name

Give every control and every link a name a screen reader can say (4.1.2): its visible text, its
`<label>`, or the `alt` of the image inside it. When the visible text alone does not say which
item a control acts on, add the rest as visually hidden text, so a screen reader's list of links
reads "Pay the invoice of Globex" and not "Pay" five times (2.4.4). GOV.UK lists non-descriptive
link text among the things to check by hand.

The `renderPayLink` prop of the invoices screen, from `src/routes/invoices.index.tsx`, with the
rest of the screen cut:

```tsx
renderPayLink={(invoice) => (
  <Link to="/invoices/$invoiceId/pay" params={{ invoiceId: invoice.id }} className="underline underline-offset-2">
    Pay<span className="sr-only"> the invoice of {invoice.customerName}</span>
  </Link>
)}
```

Why it is good: the router's `Link` renders an `<a href>`, the native link, which the keyboard
reaches and a crawler follows (Google crawls a link only when it is an `<a>` element with an
`href`). The eye sees "Pay" in a row whose customer it can see; a screen reader that lists the
links says the customer too. Tailwind's `sr-only` class hides the text from sight and keeps it in
the accessibility tree.

### Data in a table

Put data in rows and columns in a `<table>` with `<th>` header cells, so the relationships the eye
sees are in the markup (1.3.1). The invoice table, from
`src/billing/list-invoices/invoice-list.tsx`, with the other cells of each row and the end of the
table cut:

```tsx
<table className="w-full text-left">
  <caption className="sr-only">Invoices</caption>
  <thead className="border-b border-border text-sm text-muted-foreground">
    <tr>
      <th scope="col">Customer</th>
      <th scope="col">Amount</th>
      <th scope="col">Due</th>
      <th scope="col">Status</th>
      <th scope="col">
        <span className="sr-only">Actions</span>
      </th>
    </tr>
  </thead>
  <tbody>
    {invoices.map((invoice) => (
      <tr key={invoice.id} className="border-b border-border">
        <th scope="row" className="py-2 font-medium">
          {invoice.customerUrl === null ? (
            invoice.customerName
          ) : (
            <ExternalLink href={invoice.customerUrl}>{invoice.customerName}</ExternalLink>
          )}
        </th>
        ...
```

Why it is good: the `<caption>` names the table; `scope="col"` makes each header name its column,
and `scope="row"` makes the customer name its row, so a screen reader can say which column and
which customer a cell belongs to. The last column has no visible header, so it gets a hidden one;
an empty header cell would leave that column with no name. The customer's name is a link only
when the invoice has an address, through the shared `ExternalLink`; otherwise it is plain text.

### ARIA and ids in JSX

| In HTML | In JSX | Why |
|---|---|---|
| `aria-*` | the same names, such as `aria-describedby`; not camelCase | react.dev: "In React, all ARIA attribute names are exactly the same as in HTML." |
| `for` on a `<label>` | `htmlFor` | React uses the DOM property name. A control wrapped in its `<label>` needs no `htmlFor` |
| `tabindex` | `tabIndex`, only `0` or `-1` | react.dev: "Avoid using values other than -1 and 0." A positive value makes a focus order of its own (section 5) |
| an `id` that another element points at | `const hintId = useId()`, then `aria-describedby={hintId}` on the field and `id={hintId}` on the hint | one id per rendered copy, so a component rendered twice keeps its ids unique, with no id written by hand; react.dev says never to use it for list keys |

A virtualised list keeps rows out of the page, which costs find in page, landmark navigation and a
stable reading buffer for a screen reader; the evidence and the rule on when to virtualise are
[performance.md](../performance/performance.md) section 6.

## 4. Widget patterns and dialogs

When HTML has no element for a widget, take it from a library that follows the APG pattern, or
build it to the pattern yourself. The order, native element, then such a library, then a
hand-built pattern, is this practice's own choice: no owner states it as one sequence, and the
first rule of ARIA backs only its first step.

The APG patterns a screen needs most, read 2026-10-01. The pattern page has the full contract;
the table is for finding it.

| Widget | Roles and states | Keys | Watch for |
|---|---|---|---|
| Tabs | a `tablist` of `tab`s, each with `aria-controls` pointing at its `tabpanel`; the active tab has `aria-selected="true"` | Tab moves to the active tab; Left and Right Arrow (Up and Down when vertical) move between tabs; Enter or Space activates a tab when focus alone does not; Home and End are optional | the whole list is one Tab stop |
| Menu button | a `button` with `aria-haspopup` (`menu` or `true`) and `aria-expanded`; the popup is a `menu` of `menuitem`s, `menuitemcheckbox`es or `menuitemradio`s | Enter or Space opens the menu and focuses its first item; Down Arrow moves to the next item; Enter activates an item and closes the menu; Escape closes it and returns focus to the button | the APG frames a menu as a set of actions or functions (read through a summary) |
| Combobox | `combobox` with `aria-expanded`, `aria-controls` pointing at the popup, and `aria-autocomplete` (`none`, `list` or `both`) | Down Arrow moves into the popup; Escape closes it; while an option is highlighted, DOM focus stays on the combobox and `aria-activedescendant` names the option | one 2026 audit lists shadcn/ui's Combobox among five components with gaps |
| Disclosure | a `button` with `aria-expanded`; `aria-controls` is optional | Enter or Space toggles | |
| Accordion | each header is a `button` inside a heading with `aria-level`, and has `aria-expanded` and `aria-controls`; a panel may be a `region` labelled by its header button | Enter or Space opens or closes a panel; Tab moves through every focusable element | |
| Alert | `alert`; it does not take focus | none: the APG says "Not applicable" | a brief, important message; section 7 |
| Alert dialog | `alertdialog` with `aria-modal="true"`, `aria-labelledby` or `aria-label`, and `aria-describedby` pointing at the message | as the modal dialog | the modal dialog's rules below apply |
| Listbox | a `listbox` of `option`s; selection shown by `aria-selected` or `aria-checked`; `aria-multiselectable="true"` when several can be chosen | Up and Down Arrow move; Home and End are optional; Space toggles an option in a multi-select | |
| Tooltip | `tooltip`; the trigger points at it with `aria-describedby` | focus stays on the trigger; Escape closes the tooltip | the APG says this pattern "is work in progress; it does not yet have task force consensus"; a tooltip never holds an action or anything the user must read to finish the task ([ux.md](ux.md) section 8) |
| Modal dialog | `dialog` with `aria-modal="true"` and `aria-labelledby` or `aria-label` | focus moves in on open; Tab and Shift+Tab stay inside; Escape closes; focus returns to the opener on close | use the native `<dialog>`, below |

A composite widget, such as tabs, a listbox or a menu, is one Tab stop, and the arrow keys move
inside it. There are two ways to build that. With a roving `tabIndex`, the current item has
`tabIndex={0}`, the others `-1`, and focus moves from item to item. With `aria-activedescendant`,
focus stays on the container, which names the current item. Use the roving `tabIndex` unless the
pattern keeps focus in one place: the APG gives its benefit, "the user agent will scroll the newly
focused element into view". The combobox is the case for `aria-activedescendant`, since the user
keeps typing in it.

### Libraries

Radix Primitives and React Aria both say their components follow the APG and are tested with
screen readers. Those are the vendors' own statements, and two public records show their limits.
An expert audit of Radix by Publicis Sapient (2023, with VoiceOver and Safari, NVDA and Firefox,
TalkBack and Chrome) found 35 defects, and in February 2025 its authors wrote that "the issues are
still there in 2025". shadcn/ui copies its components into your repository, so their defects
become yours: an issue in which screen-reader users could not dismiss the mobile sidebar was
closed as not planned (2025), and a 2026 audit by a firm that sells audits found 34 of 48
components passing WCAG 2.2 AA, with gaps in Combobox, Data Table, Context Menu, Chart and Input
OTP.

When you take a widget from a library, let the library manage its focus and its keys, and add no
focus code of your own on top: two pieces of code moving focus work against each other. Then put
the widget through the manual pass of section 11, like code you wrote. Which library to pick, and
its version, is [libraries.md](../architecture/libraries.md) section 2.

### The modal dialog

For a modal, use the native `<dialog>` element and open it with `showModal()`. It is Baseline
widely available since 2024-09-14: Chrome 37, Edge 79, Firefox 98, Safari 15.4 (read 2026-10-01).
Scott O'Hara's advice (2023) is the same: use it for most modal needs, since recent changes to the
specification make a hand-built dialog largely unnecessary. The APG's dialog pattern does not
mention the native element (read 2026-10-01), so build with MDN and check the result against the
APG's keyboard contract in the table above.

| A modal needs | What `showModal()` does by itself | What you still do |
|---|---|---|
| focus moves in | sets focus on the first focusable element inside, or on the one with `autofocus` | MDN recommends `autofocus` on the close button when nothing inside needs more immediate interaction |
| the rest of the page is out of reach | makes everything outside the dialog inert, puts the dialog in the top layer and adds a `::backdrop` | nothing |
| Escape closes it | closes on Escape | keep it working. MDN: "Keyboard users expect the Esc key to close modal dialogs; ensure that this behavior is implemented and maintained." |
| focus comes back | returns focus to the element that had it before the dialog opened | when that element is gone, move focus to the next logical place yourself (the APG) |
| assistive technology treats it as modal | `aria-modal="true"` is implicit | put no `tabindex` on the `<dialog>` itself (MDN) |
| a name | nothing | `aria-labelledby` pointing at the dialog's heading, or `aria-label` (the APG) |

Do not rely on the `closedby` attribute to close a dialog on a click outside it: it is Baseline
limited, in Chrome and Edge 134 and Firefox 141 and not in Safari (read 2026-10-01).
`showModal()` is a method of the DOM element, so a component calls it through a ref; how a
component reaches a DOM element is [components.md](../components/components.md) section 3.

### Popover and `inert`

The `popover` attribute also puts an element in the top layer, but a popover is always non-modal:
MDN says "for modal behavior, use the `<dialog>` element". MDN's overview names no role that it
adds (read through a summary), so a popover still needs the role and the keys of its APG pattern.
It is Baseline newly available since 2025-01-27 and not yet widely available (read 2026-10-01).
Convert every modal to the native `<dialog>` before you adopt `popover`. Adrian Roselli's reason
(updated 2025-12-05): a popover can open over a `div role="dialog"`, and Escape then closes the
dialog instead of the popover; a native `<dialog>` sits above popovers in the top layer.

For an overlay you build without `<dialog>`, set the `inert` attribute on the rest of the page
while the overlay is open, so neither the Tab key nor a screen reader reaches what lies behind it.
`inert` is Baseline widely available since 2025-10-11 (read 2026-10-01).

## 5. Focus

When you style a focusable element, keep its focus indicator visible (2.4.7, AA). The APG: "The
visual focus indicator must always be visible." Draw it with `outline` or a border, never with
`box-shadow` alone: in forced colours mode, such as Windows contrast themes, the browser sets
`box-shadow` to none and repaints outline and border colours from the system palette (MDN,
2026-04-20). Give the indicator 3:1 against the colours next to it, the floor for the parts of a
control (1.4.11, AA).

The shared button, from `src/core/ui/button.tsx`, whole:

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

Why it is good: it is a native `<button>`, so Tab, Enter and Space work with no code. The focus
indicator is an `outline`, so it survives forced colours, and it shows under `focus-visible`, when
the browser decides focus should be seen, such as on keyboard use. The `ring` token measured
4.77:1 on the light background and 10.35:1 on the dark one in the application's contrast check
([visual-design.md](visual-design.md) section 4), above the 3:1 floor. The button is 36 px high (`min-h-9` on Tailwind 4's default
spacing, read 2026-10-01), above the 24 px floor of 2.5.8. On a coarse pointer such as a finger it
is 44 px (`pointer-coarse:min-h-11`), the height of Apple's default 44 by 44 pt control. The `type`
defaults to `button`, and the comment above `className` gives the reason for the outline and for
the coarse-pointer height, so nobody swaps the outline for a shadow or drops the second height.

The other focus rules:

- **Order.** Keep the DOM order the reading order, so Tab moves through the screen the way the eye
  does (2.4.3, A). Set `tabIndex` only to `0`, to add a custom control to the order, or to `-1`,
  to let code focus an element the user does not tab to, such as a heading. A positive value puts
  the element ahead of everything else; Oxlint's `jsx-a11y/tabindex-no-positive` rule reports it
  when the rule is on (section 10).
- **Never hidden.** When a header, a banner or a toast sticks to an edge of the screen, it must
  never hide the focused element entirely (2.4.11, AA, new in 2.2). Tab to the controls under it in
  the manual pass.
- **Focus moves only when the user starts a new context:** into a dialog and back out (2.4.3), to
  the new screen after a route change (section 6), to the first error after a failed submit
  ([ux.md](ux.md) section 4). A status message never moves focus (4.1.3, section 7).
- **A skip link** when the same block of links comes before `<main>` on every screen: the first
  Tab stop is a link to the main content. W3C's Easy Checks list a skip link, and the 2019 user
  test in section 6 recommends one.

## 6. Route changes in a single-page app

A client-side route change loads no page. The browser announces no new title, and focus stays on
a link that may no longer exist. The router does not fix this (read 2026-10-01):

- React Router's ScrollRestoration page covers scroll only and says nothing on focus or
  announcements. Its maintainer said, in a discussion that ran from 2022 to 2025, that it does not
  manage focus, because moving focus also scrolls the page, and he recommended announcing the
  change instead.
- TanStack Router has no announcer. A pull request that would add one was an open draft on
  2026-09-29, not shipped.

So the application does it, in this order:

1. **Give each screen its own `<title>`**, one at a time, that names the screen (2.4.2, A). React
   puts a `<title>` it renders into the document head; react.dev says to render only one at a time.
   Two screens with the same title sound like one screen: put the item in the title when a user can
   go from one item's screen straight to another's.
2. **Then tell assistive technology about the new screen.** This practice's default is to put the
   new screen's name in a polite status region that stays in the page. WCAG and MDN send results
   and progress to a polite status region, and React Router's maintainer recommends announcing.
   The other way is to move focus to the new screen's `<h1>`, given `tabIndex={-1}`. In a 2019 test
   with five users of different assistive technology, focus on a heading was "the best
   experience", no single technique worked for everyone, and the testers recommended a skip link, a
   live region that announces the page and a visible focus outline together. Five users in one
   test is little evidence for either way; pick one and check it in the manual pass.
3. **Announce only a change of screen.** Skip the first load, which the screen reader already
   reads, and a change of the search string or the hash alone.

The application shell, from `src/routes/__root.tsx`, with the imports and the route definition cut:

```tsx
const APPLICATION_NAME = "Acme Billing";

...

function AppShell() {
  // The deepest matched route is the screen on show; it names itself in its `staticData`.
  const screenTitle = useMatches({ select: (matches) => matches.at(-1)?.staticData.title ?? APPLICATION_NAME });
  const screenStatus = useMatches({ select: (matches) => matches.at(-1)?.status });

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 p-6">
      <title>{`${screenTitle} · ${APPLICATION_NAME}`}</title>
      {/* A route change loads no page, so a screen reader says nothing by itself. <output> is
          the native element with the `status` role. It stays in the page from the first render
          and only its text changes: a region that arrives together with its text is often not
          announced, so the loading and error screens say their message here. */}
      <output className="sr-only">{screenAnnouncement(screenStatus, screenTitle)}</output>
      <header>
        <p className="text-lg font-semibold">{APPLICATION_NAME}</p>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
```

The text the region says comes from one function in the same file:

```tsx
function screenAnnouncement(screenStatus: AnyRouteMatch["status"] | undefined, screenTitle: string): string {
  if (screenStatus === "pending") {
    return "Loading";
  }

  if (screenStatus === "error") {
    return "This screen did not load";
  }

  return screenTitle;
}
```

Each route names itself, as the invoices screen does in `src/routes/invoices.index.tsx` (its
loader cut):

```tsx
export const Route = createFileRoute("/invoices/")({
  ...
  staticData: { title: "Invoices" },
  component: InvoicesScreen,
});
```

Why it is good: the `<title>` and the status region read the same name from the route on show, so
they cannot drift apart. The same region also says "Loading" while a route loads and "This screen
did not load" when it fails, so the loading and error screens need no live-region role of their
own (section 7). `<output>` is the native element with the implicit `status` role; MDN
says "many browsers" implement it as a live region, which is polite. It sits in the shell, so it is
in the page from the first render, and a later route change only changes its text, the form a
screen reader announces (section 7). On the first load it arrives with its text and is not
expected to speak; the screen reader reads the new page anyway. A change of the search string keeps
the same title, so the text stays the same and nothing is said. Each screen also has its own
`<h1>`, so the focus alternative has a target.

Not verified: this code was type-checked, linted and built; it was never run in a browser or with
a screen reader. Whether the announcement is heard is a step of the manual pass (section 11).

## 7. Live regions and status messages

A status message, such as the result of an action, a wait, progress or an error, must reach a
screen reader without taking focus (4.1.3, AA). The WCAG text also warns against making an
application "chatty": announce what the user needs, not every change. A dialog takes focus, so it
is not a status message.

Render the live region in the page before its text changes, and then change only its text. Most
screen readers announce a change inside a region they already know about, and often miss a region
that arrives with its text. WCAG technique ARIA19: "The error container must be present in the DOM
on page load for the error message to be spoken by most screen readers." MDN: "The most reliable
way to ensure that live regions are registered is to include them in the initial markup", and
"Behavior can vary across browser and assistive technology combinations." In React, render the
element every time and make only its children conditional.

The same holds for a loading or an error component that a router mounts in place of a screen: it
arrives with its text, so its message may not be announced. The application gives that message to
the shell's `<output>` region (section 6), which is in the page from the first render, and the
component carries no live-region role. A component that arrives with its text carries none, and
says why in a comment. From `src/core/ui/screen-pending.tsx`, whole:

```tsx
// No live-region role here: this component arrives in the page together with its text, and a
// screen reader often skips such a region. The shell's status region announces the loading.
export function ScreenPending() {
  return <p className="text-muted-foreground">Loading…</p>;
}
```

`src/routes/-screen-error.tsx`, the router's error screen, has no `role="alert"` for the same
reason and says so in a comment. Not verified: nothing was run with a screen reader, so whether
the shell's region is heard for these two screens is a step of the manual pass (section 11).

Pick the role by what the message is:

| Message | Role or attribute | How it is read |
|---|---|---|
| the result or progress of an action: saved, loading, 3 results | `role="status"`, or the `<output>` element | polite: after the user pauses (ARIA22) |
| an error or warning the user has to act on | `role="alert"` | interrupts, and is often read with the word "Alert" first (ARIA19, MDN) |
| a sequence of updates, such as a chat or an activity log | `role="log"` | polite; only the new entries are read (ARIA23) |
| something time-critical that is none of the above | `aria-live="assertive"` | interrupts; MDN keeps it for time-sensitive or critical notifications |

`aria-atomic` is false by default, so a screen reader reads only the part that changed; set it to
true when the region must be read whole.

Bad, the region arrives with its text:

```tsx
{payment.isError ? (
  <p role="alert" className="text-sm text-destructive">
    We could not confirm the payment. Check the invoice list before you try again.
  </p>
) : null}
```

The `<p>` is created at the moment the payment fails, text and all. Most screen readers have not
registered it as a live region yet, so the message can pass in silence while the user waits.

Good, the same message in a region that is in the form from the first render. From
`src/billing/pay-invoice/pay-invoice-form.tsx`, the rest of the form cut:

```tsx
{/* The region is in the page before the error is: a screen reader announces text that
    appears inside an existing live region, and often misses a region that arrives with
    its text. */}
<p role="alert" className="text-sm text-destructive">
  {payment.isError ? "We could not confirm the payment. Check the invoice list before you try again." : null}
</p>
```

Why it is good: it fixes the one problem of the bad version. The `<p role="alert">` is rendered
every time and stays empty until the payment fails; then only its text changes, the form ARIA19
and MDN describe. `alert` fits, since the user has to act. The comment keeps the next editor from
"tidying" the empty paragraph into a conditional one. Not verified: nothing was run with a screen
reader.

Check: in review, for each `role="alert"`, `role="status"`, `role="log"`, `<output>` or
`aria-live` the diff adds, ask whether the element is rendered while its text is empty.

## 8. Forms and errors

How a form behaves, when it validates, where an error shows and where focus goes after a failed
submit, is [ux.md](ux.md) section 4. This section is what the markup carries.

- Tie every field to a `<label>`, by wrapping the field in it or by `htmlFor` and an `id` (3.3.2,
  4.1.2). A screen reader then says the label when the field takes focus, and a click on the label
  focuses the field. WebAIM found fields with no label on 51% of home pages in 2026.
- Put a group of radio buttons or checkboxes in a `<fieldset>` whose `<legend>` names the group
  (1.3.1), so the question is in the markup next to its answers.
- Tie a hint or an error to its field with `aria-describedby` and an id from `useId` (section 3),
  so a screen reader reads it with the field.
- Write each error in text that says what went wrong and what to do (3.3.1, A); a red border alone
  says neither (1.4.1).
- Announce an error through a region that is already in the page (section 7), or by moving focus to
  the first field in error ([ux.md](ux.md) section 4).
- Give a field about the user its `autoComplete` token, such as `email` or `postal-code` (1.3.5,
  AA). Oxlint's `jsx-a11y/autocomplete-valid` rule checks the token when the rule is on
  (section 10).
- Let each login step work without a cognitive function test, "such as remembering a password or
  solving a puzzle", unless the step offers an alternative or a mechanism that does it for the user
  (3.3.8, AA).
- Do not ask, in the same process, for data the user already entered (3.3.7, A).

The payment method group, from `src/billing/pay-invoice/pay-invoice-form.tsx`, the rest of the form
cut:

```tsx
<fieldset className="flex flex-col gap-2">
  <legend className="text-sm font-medium">Payment method</legend>
  <label className="flex items-center gap-2">
    {/* One method is always chosen, so `payInvoice` never parses an empty choice. */}
    <input type="radio" name="method" value="card" defaultChecked />
    Card
  </label>
  <label className="flex items-center gap-2">
    <input type="radio" name="method" value="bank_transfer" />
    Bank transfer
  </label>
</fieldset>
```

Why it is good: the `<legend>` names the group once, and each `<label>` wraps its radio button, so
the text is the button's name, a click on the text selects it, and no `id` or `htmlFor` is needed.
The radio buttons share one `name`, so the browser gives them arrow-key movement inside the group
with no code.

## 9. The numbers

The floors of WCAG 2.2 AA and the comfortable sizes of the two platform guides. The token values
that meet them are [visual-design.md](visual-design.md) sections 3 and 4.

| What | Floor | Criterion | Note |
|---|---|---|---|
| Text contrast | 4.5:1; 3:1 for large text (18 pt, or 14 pt bold) | 1.4.3, AA | a threshold, never rounded: 4.49:1 fails |
| Contrast of control parts, focus indicators and graphics that carry meaning | 3:1 against the colours next to them | 1.4.11, AA | |
| Colour as a cue | never the only one | 1.4.1, A | the word, the icon or the shape carries the meaning; colour repeats it |
| Target size | 24 by 24 CSS px, or spacing that keeps a 24 px circle around the target clear of others | 2.5.8, AA | exceptions: a link inside a sentence, an equivalent control elsewhere, a control the browser draws, a size that is essential |
| Comfortable touch target | 44 by 44 pt on iOS and iPadOS (Apple's default size; its minimum is 28 by 28 pt); 48 by 48 dp on Android (Material, as Google's help cites it) | platform guidance, not WCAG | Apple's 44 pt is a default, not a minimum |
| Resize text | 200%, with no loss of content or function | 1.4.4, AA | captions and images of text are exempt |
| Reflow | no scrolling in two directions at 320 CSS px wide, or 256 CSS px high for content that scrolls sideways | 1.4.10, AA | 320 px is 400% zoom on a 1280 px window; content that needs two dimensions, such as a data table, is exempt |
| Text spacing | nothing is lost when the user sets line height to 1.5, paragraph spacing to 2, letter spacing to 0.12 and word spacing to 0.16 times the font size | 1.4.12, AA | |
| Motion | follow `prefers-reduced-motion` | none at A or AA; 2.3.3 is AAA | it stays in the manual pass (section 11) |

The 2.5.8 spacing wording is a summary; read the criterion before you lean on the exception.

WCAG 2's contrast formula stays the reference. WCAG 3 is a draft and its contrast method is not
decided, and APCA is normative nowhere (read 2026-10-01). APCA's author argues that the WCAG 2
formula misjudges dark themes, so look at the dark-theme pairs by eye as well; for conformance,
WCAG 2 is the test the law can use. WCAG 3.0 is a Working Draft (2026-09-10) that says it should
not be cited as other than work in progress. APCA's author is an interested party. Vercel's
interface guidelines prefer APCA; this practice does not follow them there, because no standard
includes APCA yet and, in Eric Eggert's words, organisations "cannot rely on APCA for
compliance".

The application checked the WCAG 2 ratio of each token pair in both themes. The pairs are tokens,
so the table of their ratios, each next to its floor, is
[visual-design.md](visual-design.md) section 4.

Colour as one cue among others, from `src/billing/list-invoices/invoice-status-badge.tsx`, with
the import, the two lookup tables and the props type cut:

```tsx
export function InvoiceStatusBadge({ status }: InvoiceStatusBadgeProps) {
  // The word carries the status. The colour repeats it and is never the only signal.
  return <span className={`text-sm font-medium ${STATUS_COLOR[status]}`}>{STATUS_LABEL[status]}</span>;
}
```

Why it is good: "Overdue" is a word a screen reader says and a user who cannot tell red from green
reads; the colour only repeats it (1.4.1).

## 10. Automated checks

Three checks run on every change. Each finds a different part, and none of them finds meaning.

| Check | When it runs | What it finds | What it cannot find |
|---|---|---|---|
| Oxlint with its jsx-a11y plugin | in the editor and in CI, on the source | faults visible in the JSX: an image with no `alt`, a click handler on a `div`, a bad `href`, an unknown role or ARIA attribute, a positive `tabIndex`, a field with no label | anything known only at run time: a computed name, contrast, focus order, what a screen reader says |
| a component test that finds elements by role and name | in the unit suite | a control that lost its role or its name | layout, contrast, a real screen reader |
| axe on the rendered screen, from a Playwright test | in the end-to-end suite | faults in the rendered page, such as low contrast and missing or invalid properties once the page has rendered | meaning: `alt="image"` passes, a wrong label passes; focus order; announcements |

Turn the jsx-a11y plugin on by name in the Oxlint configuration: Oxlint enables only its default
plugins, and jsx-a11y is not one of them (read 2026-10-01). Oxlint has every rule of
`eslint-plugin-jsx-a11y`'s `recommended` set; the two plugin rules it lacks, `accessible-emoji`
and `label-has-for`, are outside that set (read through a summary of the plugin's README and the
Oxlint source, 2026-10-01). Having a rule is not the same as running it: which rules a
configuration turns on is set by its categories and rule list, and the negative control below shows
only the four rules it triggered. The plugin's README states the limit of all of them: "it only
catches errors in static code". The setup, the rules to turn on and the versions are
[libraries.md](../architecture/libraries.md) section 4.

What Oxlint 1.85 with the plugin on reported, in the application's negative control: a file with
a click handler on a `div`, an `<img>` with no `alt` and a `javascript:` link, added and then
removed. From the record of those checks, the jsx-a11y lines only:

```text
src/billing/list-invoices/control-react.tsx:19:5: error jsx-a11y(click-events-have-key-events): Enforce a clickable non-interactive element has at least one keyboard event listener.
src/billing/list-invoices/control-react.tsx:19:6: error jsx-a11y(no-static-element-interactions): Static HTML elements with event handlers require a role.
src/billing/list-invoices/control-react.tsx:20:7: error jsx-a11y(alt-text): Missing `alt` attribute.
src/billing/list-invoices/control-react.tsx:22:8: error jsx-a11y(anchor-is-valid): Use of incorrect `href` for the 'a' element.
```

In a component test, find elements by role and name (`getByRole`), first in Testing Library's
priority list, so the test fails when a control loses its role or its name. On the rendered page,
run axe from a Playwright test. Playwright's own documentation draws the line: automated tests "can
detect some common accessibility problems such as missing or invalid properties. But many
accessibility problems can only be discovered through manual testing." The tools and their
versions are [libraries.md](../architecture/libraries.md) sections 6 and 8.

How much the tools find, each figure with what it counts:

| Source | What was counted | What the tools found | How far to trust it |
|---|---|---|---|
| Deque, 2021 | nearly 300,000 issues from over 2,000 first-time audits of 13,000+ pages | axe "completely covered" 57% of the issues | the vendor measuring its own tool; it counts issues by volume, not WCAG criteria |
| UK Government Digital Service, page dated 2018-04-13 | 142 barriers planted on one test page, 13 tools | the best tool found 40% of the barriers; axe found 29% | barrier types on one page, with the tools of 2018 |
| A 2026 study of 300 interfaces generated by three commercial models | 541 "semantic" violations of six kinds | automated checkers passed them all, such as `alt="image"` | the abstract only; the full text was not read |

The figures do not add up to one number: one counts issues as they occur, the other counts kinds
of barrier. A higher coverage figure circulates from vendor marketing with no published method;
this file does not use it.

## 11. The manual pass

Run it on each new or changed screen before the change ships, in this order. Each step catches
what section 10 cannot. W3C's Easy Checks page is a good first walk-through for someone new; it
says of itself that its checks "cover just a few accessibility issues".

1. **Keyboard only.** Put the mouse away and Tab through the screen. Every control is reached in
   reading order (2.4.3), shows its focus (2.4.7), is not hidden under a sticky element (2.4.11)
   and works with the keys of its pattern (2.1.1, section 4); focus can always move on (2.1.2).
   Open and close each dialog: focus goes in, stays in, and comes back. Change the route: the title
   changes, and the new screen is announced or its heading has focus (section 6).
2. **Text at 200%.** Set the browser's text size to 200%: no text is cut off or overlaps, and every
   control still works (1.4.4).
3. **Reflow at 320 px.** Make the window 320 CSS px wide, or zoom to 400% on a 1280 px window:
   nothing needs a sideways scroll except a part that is two-dimensional by nature, such as a data
   table (1.4.10).
4. **Text spacing.** Apply the four values of section 9 with a user style sheet: no text is cut off
   or hidden (1.4.12).
5. **Forced colours.** Turn on a Windows contrast theme, or the browser's forced-colours emulation:
   focus indicators, control borders and icons that carry meaning still show (section 5).
6. **Reduced motion.** Turn on the system's reduce-motion setting: animations stop, or become
   fades. No A or AA criterion asks for this; The A11Y Project's checklist does, and MDN advises
   replacing scaling and panning with opacity fades.
7. **One screen reader with one browser.** Walk the screen's main task, listening for each
   control's name and role, the route announcement, each status message and alert, and each
   dialog's name. Pick a pair users have: in WebAIM's 2026 survey (1,780 self-selected
   respondents) the most common primary pairs were JAWS with Chrome (31.2%), NVDA with Chrome
   (17.3%) and JAWS with Edge (17.0%). GOV.UK's list also has VoiceOver with Safari on iOS and
   TalkBack with Chrome. The browser's accessibility inspector, in Firefox or in Chrome DevTools,
   shows the name and role a control exposes when what you hear is unclear.

Check: the pull request that adds or changes a screen says in its Verification which steps of this
list were run, and with which screen reader and browser.

## 12. Common mistakes

Each pair shows one mistake, the reason, and the same code with only that mistake fixed.

### A click handler on a `div`

Bad, an action on an element with no role:

```tsx
<div onClick={() => void router.invalidate()}>Try again</div>
```

A `div` has no role, no place in the Tab order and no Enter or Space, so a keyboard user cannot
reach the action and a screen reader does not call it a button. Oxlint reported this form in the
negative control as `jsx-a11y(click-events-have-key-events)` and
`jsx-a11y(no-static-element-interactions)`. Adding `role="button"`, `tabIndex={0}` and a key handler
rebuilds by hand what `<button>` already does, and every piece of it is a promise to keep
(section 3).

Good, the same action on the shared button, from `src/routes/-screen-error.tsx`, the rest of the
component cut:

```tsx
<Button onClick={() => void router.invalidate()}>Try again</Button>
```

Why it is good: it fixes the one problem. `Button` renders a native `<button>` (section 5), so the
keyboard, the focus and the role come with it.

### An image with no `alt`

Bad, a logo in the header with no text alternative:

```tsx
<img src="/acme-logo.svg" width={120} height={32} />
```

A screen reader has no text alternative to say for it (1.1.1). Oxlint reported
`jsx-a11y(alt-text)`, "Missing `alt` attribute.", on this form in the negative control.

Good, the same image with the text it shows as its `alt`:

```tsx
<img src="/acme-logo.svg" alt="Acme Billing" width={120} height={32} />
```

Why it is good: the `alt` says what the image says, the name of the application. An image that is
only decoration gets `alt=""`, so a screen reader skips it. An `alt` that names the kind of thing,
such as `alt="logo"` or `alt="image"`, passes every automated check and tells the user nothing;
only the manual pass finds it (section 10).

### A live region that arrives with its text

The pair is in section 7: a `<p role="alert">` rendered only when the error happens, and the fix,
the same element rendered every time with only its text conditional.

### An overlay as the "fix"

Bad, the page with an overlay script added to it:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://overlay.example.com/widget.js" async></script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

An overlay is a script that runs on top of the page after it loads. The source the team ships
keeps every barrier it had, and the widget adds code from another origin to every screen. In 2025
the US Federal Trade Commission's final order against one overlay vendor, accessiBe, required a
payment of $1 million and barred it from claiming, without evidence, that its automated tool makes
a site WCAG-conformant.

Good, the page with the script removed, as the application ships it (`index.html`, whole):

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Why it is good: it fixes the one problem, and the barriers an overlay claims to patch are fixed
where they live, by the rules of this file. The page language, missing on 13.5% of home pages in
WebAIM's 2026 scan, is set in the markup with `lang="en"`.

## 13. Where the rules stop holding

- **A framework with its own route announcer.** Next.js announces client-side transitions by
  default; its announcer reads the document title, then the `<h1>`, then the path, so each page
  needs a unique, descriptive title (documentation page dated 2024-11-06, read 2026-10-01). Do not
  add the status region of section 6 there; the title rule still holds.
- **A widget from a library that manages its own focus.** The focus code of section 5 stays out of
  it; the manual pass of section 11 still covers it.
- **The criteria's own exceptions.** Target size exempts a link inside a sentence, an equivalent
  control and a control the browser draws; reflow exempts content that needs two dimensions; resize
  text exempts captions and images of text (section 9).
- **AAA criteria.** They are not the target: 7:1 contrast, the 80-character line (whose owner is
  [visual-design.md](visual-design.md) section 5), 2.3.3 Animation from Interactions and 2.4.13 Focus
  Appearance. Reduced motion stays in the manual pass all the same.
- **A product outside a law's scope**, such as a service of a microenterprise under the European
  Accessibility Act. The users are the same, so the target stays WCAG 2.2 AA; no owner states
  this, it is the practice's choice.

## 14. Review checklist

One question per section. A single red flag is something to raise with the author; a screen that
shows two or more is not ready.

| Section | Ask | Red flag |
|---|---|---|
| 3. Native elements | Does each control use the HTML element made for its job? | `onClick` on a `div` or a `span`; a `role` with no keyboard handling; data in rows and columns built from `div`s |
| 3. Names | Can each control's name be understood when read alone? | an icon button with no name; five links called "Pay" |
| 4. Widgets and dialogs | Does each custom widget follow its APG pattern, or come from a library that does? | tabs or a listbox with no arrow keys; a modal built from a `div` when `<dialog>` would do |
| 5. Focus | Can you see focus on every control, and does it move in reading order? | `outline: none` with nothing in its place; focus drawn only with `box-shadow`; a positive `tabIndex` |
| 6. Route changes | Does a route change set the title and announce the screen or focus its heading? | one title for every screen; an announcer mounted inside each screen |
| 7. Live regions | Is each live region in the page before its text changes? | a region inside a condition; `aria-live="assertive"` on a message that is not urgent |
| 8. Forms | Does every field have a label, and every error a text? | a field with no `<label>`; an error shown only in red |
| 9. Numbers | Do the pairs meet 4.5:1 and 3:1, and each target 24 px? | a ratio rounded up to pass; an icon button under 24 px with no spacing |
| 10, 11. Checks | Did the change pass the linter, axe and the manual pass? | "axe passed" given as the whole check |

## 15. Sources

The standard and the law

1. W3C, "WCAG 2 Overview", https://www.w3.org/WAI/standards-guidelines/wcag/ : WCAG 2.2 is the
   current Recommendation, 2.0, 2.1 and 2.2 stay valid, and WCAG 3 is an early draft.
2. W3C, "Web Content Accessibility Guidelines (WCAG) 2.2", 2024-12-12,
   https://www.w3.org/TR/WCAG22/ : the criteria and levels in sections 2 and 9 (levels re-read
   2026-10-01), the additions of 2.2 and the removal of 4.1.1.
3. W3C, "W3C Accessibility Guidelines (WCAG) 3.0", Working Draft, 2026-09-10,
   https://www.w3.org/TR/wcag-3.0/ : its draft status and its undecided contrast method.
4. W3C Understanding documents: Contrast (Minimum),
   https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html ; Target Size (Minimum),
   https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html ; Resize Text,
   https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html ; Reflow,
   https://www.w3.org/WAI/WCAG22/Understanding/reflow.html ; Text Spacing,
   https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html ; Page Titled,
   https://www.w3.org/WAI/WCAG22/Understanding/page-titled.html ; Focus Order,
   https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html ; Status Messages,
   https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html ; Accessible Authentication
   (Minimum), https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html ;
   Visual Presentation (the AAA line length),
   https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html .
5. W3C techniques ARIA19 (alert for errors; the container is present on load),
   https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA19 ; ARIA22 (status),
   https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA22 ; ARIA23 (log),
   https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA23 .
6. Directive (EU) 2019/882, https://eur-lex.europa.eu/eli/dir/2019/882/oj/eng : Articles 4(5),
   14 and 32: the date, the exemption and the link to EN 301 549.
7. ADA.gov, first steps for the ADA Title II web rule, 2026-04-20,
   https://www.ada.gov/resources/web-rule-first-steps/ : the rule points at WCAG 2.1 AA.

Native elements, ARIA and widget patterns

8. W3C, "Using ARIA", Discontinued Draft, 2026-02-24, https://www.w3.org/TR/using-aria/ : the
   first rule of ARIA.
9. W3C APG, "Read Me First", https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/ : "No ARIA
    is better than bad ARIA" and a role as a promise.
10. W3C APG patterns: tabs, https://www.w3.org/WAI/ARIA/apg/patterns/tabs/ ; menu button,
    https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/ ; menu and menubar,
    https://www.w3.org/WAI/ARIA/apg/patterns/menubar/ ; combobox,
    https://www.w3.org/WAI/ARIA/apg/patterns/combobox/ ; disclosure,
    https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/ ; accordion,
    https://www.w3.org/WAI/ARIA/apg/patterns/accordion/ ; alert,
    https://www.w3.org/WAI/ARIA/apg/patterns/alert/ ; alert dialog,
    https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog/ ; listbox,
    https://www.w3.org/WAI/ARIA/apg/patterns/listbox/ ; tooltip,
    https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/ ; modal dialog,
    https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ . The roles, states and keys of the
    section 4 table.
11. W3C APG, "Developing a Keyboard Interface",
    https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/ : roving `tabindex` and
    `aria-activedescendant`; focus always visible.
12. react.dev, "Common components",
    https://react.dev/reference/react-dom/components/common : `aria-*`, `htmlFor`, `tabIndex`.
    react.dev, "useId", https://react.dev/reference/react/useId : ids for accessibility
    attributes, never list keys. react.dev, "`<title>`",
    https://react.dev/reference/react-dom/components/title : one title at a time, placed in the
    head.
13. WebAIM, "The WebAIM Million", 2026, https://webaim.org/projects/million/ : the failure rates
    in sections 1, 8 and 12, and the error averages of pages with and without ARIA.
14. Google Search Central, crawlable links,
    https://developers.google.com/search/docs/crawling-indexing/links-crawlable : only `<a href>`.

Libraries and dialogs

15. Radix, "Accessibility", https://www.radix-ui.com/primitives/docs/overview/accessibility , and
    "Dialog", https://www.radix-ui.com/primitives/docs/components/dialog : the vendor's own
    statement. React Aria, https://react-aria.adobe.com/ : the vendor's own statement.
16. Publicis Sapient's audit of Radix, discussion #2232,
    https://github.com/radix-ui/primitives/discussions/2232 : 35 defects, still open in 2025.
17. shadcn/ui issue #6761, https://github.com/shadcn-ui/ui/issues/6761 : the mobile sidebar.
    The Frontkit, "shadcn/ui accessibility audit", 2026-04-08,
    https://thefrontkit.com/blogs/shadcn-ui-accessibility-audit-2026 : 34 of 48; the auditor sells
    audits.
18. MDN, "`<dialog>`", 2026-09-02,
    https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog : what
    `showModal()` does, `autofocus` on the close button, Escape, no `tabindex`. WHATWG HTML, "The
    dialog element",
    https://html.spec.whatwg.org/multipage/interactive-elements.html#the-dialog-element :
    `closedby` and the focusing steps.
19. webstatus.dev, read 2026-10-01: `dialog`, https://api.webstatus.dev/v1/features/dialog ;
    `dialog-closedby`, https://api.webstatus.dev/v1/features?q=dialog%20closedby ; `popover`,
    https://api.webstatus.dev/v1/features/popover ; `inert`,
    https://api.webstatus.dev/v1/features/inert .
20. MDN, "Popover API", https://developer.mozilla.org/en-US/docs/Web/API/Popover_API : always
    non-modal.
21. Scott O'Hara, "Use the dialog element (reasonably)", 2023-01-26,
    https://www.scottohara.me/blog/2023/01/26/use-the-dialog-element.html .
22. Adrian Roselli, "Brief Note on Popovers with Dialogs", updated 2025-12-05,
    http://adrianroselli.com/2023/05/brief-note-on-popovers-with-dialogs.html .

Focus, route changes and live regions

23. React Router, "ScrollRestoration", https://reactrouter.com/api/components/ScrollRestoration ,
    and discussion #9555, https://github.com/remix-run/react-router/discussions/9555 : no focus
    management; announce instead.
24. TanStack Router, "Scroll Restoration",
    https://tanstack.com/router/latest/docs/framework/react/guide/scroll-restoration , and pull
    request #8561, https://github.com/TanStack/router/pull/8561 : no announcer; a draft one.
25. Marcy Sutton, user testing of accessible client-side routing, Gatsby blog, 2019-07-11,
    https://www.gatsbyjs.com/blog/2019-07-11-user-testing-accessible-client-routing/ : five users,
    focus on a heading tested best.
26. Marcy Sutton, accessibility tips for single-page applications, Deque blog, 2018-11-07,
    https://www.deque.com/blog/accessibility-tips-in-single-page-applications/ : title, live
    region and/or focus.
27. Next.js, "Accessibility", https://nextjs.org/docs/architecture/accessibility , and its
    announcer source,
    https://github.com/vercel/next.js/blob/canary/packages/next/src/client/components/app-router-announcer.tsx :
    the built-in route announcer; no announcement on the first load.
28. MDN, "ARIA live regions", 2026-09-11,
    https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Live_regions : the
    region in the initial markup, politeness, `aria-atomic`.
29. MDN, "`<output>`", 2026-09-11,
    https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/output : the implicit
    `status` role; "many browsers" make it a live region.
30. MDN, "forced-colors", 2026-04-20,
    https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/forced-colors :
    `box-shadow` set to none, outline and border colours from the system palette.

The numbers

31. Apple, Human Interface Guidelines, "Accessibility", read through its data endpoint,
    https://developer.apple.com/tutorials/data/design/human-interface-guidelines/accessibility.json :
    44 by 44 pt default, 28 by 28 pt minimum.
32. Google, Android Accessibility Help on touch targets,
    https://support.google.com/accessibility/android/answer/7101858 : 48 dp, citing Material.
33. MDN, "prefers-reduced-motion",
    https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion :
    support since 2020 and the reason.
34. Myndex, "Why APCA",
    https://github.com/Myndex/SAPC-APCA/blob/master/documentation/WhyAPCA.md : the case against
    WCAG 2's formula in dark themes. Eric Eggert, "WCAG 3 is not ready yet",
    https://yatil.net/blog/wcag-3-is-not-ready-yet : WCAG 2 is the test the law can use.

Automated checks and the manual pass

35. Oxlint, "Built-in plugins", https://oxc.rs/docs/guide/usage/linter/plugins.html : which
    plugins are on by default. `eslint-plugin-jsx-a11y` README,
    https://github.com/jsx-eslint/eslint-plugin-jsx-a11y : the presets and "only catches errors in
    static code". Oxlint's jsx-a11y rule sources,
    https://api.github.com/repos/oxc-project/oxc/contents/crates/oxc_linter/src/rules/jsx_a11y :
    the two rules it lacks. Both read through a summary.
36. Playwright, "Accessibility testing", https://playwright.dev/docs/accessibility-testing : axe
    from Playwright; manual testing still needed.
37. Testing Library, "About Queries", https://testing-library.com/docs/queries/about/#priority :
    `getByRole` first.
38. Deque, "Automated testing study identifies 57 percent of digital accessibility issues",
    2021-03-10,
    https://www.deque.com/blog/automated-testing-study-identifies-57-percent-of-digital-accessibility-issues/ .
39. Government Digital Service, "Accessibility tool audit", 2018-04-13,
    https://alphagov.github.io/accessibility-tool-audit/index.html .
40. A study of 300 generated interfaces and their semantic faults, 2026,
    https://dl.acm.org/doi/10.1145/3772363.3799364 : the abstract only.
41. W3C WAI, "Easy Checks", https://www.w3.org/WAI/test-evaluate/easy-checks/ .
42. GOV.UK Service Manual, "Testing for accessibility",
    https://www.gov.uk/service-manual/helping-people-to-use-your-service/testing-for-accessibility ,
    and "Testing with assistive technologies", 2022,
    https://www.gov.uk/service-manual/technology/testing-with-assistive-technologies : manual
    checks, inspectors, the screen reader and browser pairs (versions dated 2022).
43. WebAIM, "Screen Reader User Survey #11", 2026,
    https://webaim.org/projects/screenreadersurvey11/ : the primary pairs; self-selected
    respondents.
44. The A11Y Project, "Checklist", https://www.a11yproject.com/checklist/ : 200% text, reduced
    motion, focus order.

Overlays

45. US Federal Trade Commission, accessiBe, Inc., final order 2025-04-22,
    https://www.ftc.gov/legal-library/browse/cases-proceedings/2223156-accessibe-inc .
