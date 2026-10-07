# UX rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. Feedback and response times](#2-feedback-and-response-times)
- [3. Loading states](#3-loading-states)
- [4. Forms](#4-forms)
- [5. Undo over confirmation](#5-undo-over-confirmation)
- [6. Empty states](#6-empty-states)
- [7. State in the URL](#7-state-in-the-url)
- [8. Pointer and touch](#8-pointer-and-touch)
- [9. The heuristics as a reviewer's lens](#9-the-heuristics-as-a-reviewers-lens)
- [10. Where it stops holding](#10-where-it-stops-holding)
- [11. Review checklist](#11-review-checklist)
- [12. Sources](#12-sources)

## 1. Purpose and the one rule

This file is for everyone who designs, builds or reviews a screen of a React application: people
and AI coding agents alike. Read it before you decide what a screen shows while it waits, when it is
empty, when an action fails or when a user fills in a form, and when you review one.

It is about how a screen behaves. How it looks is [visual-design.md](visual-design.md) sections 2 to 9. The
accessibility standard, native elements, focus and announcements are
[accessibility.md](accessibility.md) sections 2, 3, 5, 6 and 7; this file states a number where a designer needs it and links
there for the rest. Where state lives, how server data, forms and routes are wired, and how errors
are caught is [architecture.md](../architecture/architecture.md) sections 7 to 12. What fast means and how it is
measured is [performance.md](../performance/performance.md) sections 2 and 3.
Every line that carries a read date is to be distrusted after 2027-04-01 until it is read again;
the README's "How to adopt" says how to list those lines.

The one rule: **a screen never leaves the user guessing what happened, what is happening now, or
what to do next.** It is the first of Nielsen's ten usability heuristics, "visibility of system
status", together with the ninth, help users recognize, diagnose and recover from errors. Each
section below is one place where the rule breaks, and the fix.

The examples come from one invented application, the billing screens of Acme Corp, built with
React 19, TanStack Query 5 and Tailwind CSS 4 (versions read 2026-10-01). The blocks quoted from
the application were type-checked, linted, unit-tested and built. The labelled field in section 4
is not from it; the record of the reference application lists it as type-checked and linted in a
temporary file. Nothing was run in a browser, so no timing, focus or announcement in these
examples was seen working.

## 2. Feedback and response times

Jakob Nielsen's three limits (1993) set what a user feels at each wait. NN/g's later articles say
what to show.

| Wait | What the user feels | What the screen shows |
|---|---|---|
| up to 0.1 s | the system reacts at once | the result, and nothing else |
| 0.1 s to 1 s | a delay is noticed, but the flow of thought holds | the control that started the action shows it is working; no spinner and no skeleton, which NN/g says "aren't necessary" under 1 s |
| 1 s to 10 s | attention holds, but the user is waiting | a skeleton or a spinner (section 3); NN/g's 2014 article puts a looped animation at 2 to 10 s |
| over 10 s | attention is lost | a progress indicator that shows how much is done; in the study NN/g reports, users with an animated progress bar waited about three times longer |

- **When a user starts an action that waits on the server, change the control in the same moment:
  its label says what is happening, and it refuses a second press.** NN/g found that static
  indicators, and warnings that ask the user not to click twice, fail; the control itself has to
  change.

  ```tsx
  // Bad: nothing changes while the payment runs. The user sees no answer for a
  // second or more and presses again.
  <Button type="submit">Pay invoice</Button>
  ```

  The user cannot tell a slow payment from a click that did not register, and a second press can
  start a second payment. The application's submit button, with that one problem fixed:

  ```tsx
  {/* Disabled while the payment runs, so a second click cannot send a second payment
      (ux.md section 2). */}
  <Button type="submit" disabled={payment.isPending}>
    {payment.isPending ? "Paying…" : "Pay invoice"}
  </Button>
  ```

  Why it is good: the label turns into "Paying…" as soon as the mutation is pending, so the user
  sees that the click was taken, and the disabled button cannot start a second payment while the
  first one runs.
- **When an action fails, say what happened, what it means for the user, and what to do next, in
  words next to the control that failed.** These are the three verbs of the ninth heuristic:
  recognize, diagnose, recover.

  ```tsx
  {/* Bad: the message names no outcome and no next step. Was anything charged?
      Should the user try again, or call someone? */}
  {/* The region is in the page before the error is: a screen reader announces text that
      appears inside an existing live region, and often misses a region that arrives with
      its text (accessibility.md section 7). */}
  <p role="alert" className="text-sm text-destructive">
    {payment.isError ? "Something went wrong." : null}
  </p>
  ```

  The user cannot recognize what failed or decide what to do. The application's message, with that
  one problem fixed:

  ```tsx
  {/* The region is in the page before the error is: a screen reader announces text that
      appears inside an existing live region, and often misses a region that arrives with
      its text (accessibility.md section 7). */}
  <p role="alert" className="text-sm text-destructive">
    {payment.isError ? "We could not confirm the payment. Check the invoice list before you try again." : null}
  </p>
  ```

  Why it is good: two short sentences answer the three questions: what happened ("We could not
  confirm the payment"), what it means (the payment may or may not have gone through, so the
  message claims nothing about a charge) and what to do ("Check the invoice list before you try
  again"). The message sits right above the button that failed. The comment keeps the reason the empty region stays in the
  page; how the message reaches a screen reader is [accessibility.md](accessibility.md) section 7.

## 3. Loading states

- **For a wait under 1 s, show no spinner and no skeleton.** NN/g (2023, reviewed 2026-09-02)
  says they "aren't necessary" there; the control's own change from section 2 is enough.
- **Choose a skeleton or a spinner by the wait, and do not make skeletons the default for every
  request.** NN/g recommends a skeleton only for waits under 10 s. One small test points the
  other way: Viget (2017) showed 136 mobile users the same wait three ways, and the skeleton felt
  longest, 2.82 s against 2.41 s for a spinner and 2.29 s for a blank screen. NN/g's thresholds win
  here because they are the newer, reviewed guidance; the test is one reason not to assume a
  skeleton always feels faster.
- **For a wait over 10 s, show how much is done:** a percentage, or steps done out of steps
  planned (NN/g, 2014).
- **Give every screen a loading state and an error state, so no screen is ever blank.** A router
  can give every route both by default; how is [architecture.md](../architecture/architecture.md)
  section 12. How a loading message is announced is [accessibility.md](accessibility.md) sections 6
  and 7, and the page jumping when content arrives is
  [performance.md](../performance/performance.md) sections 2 and 9.
- **Keep loading and empty apart:** an empty message appears only after the data has arrived
  (section 6).

## 4. Forms

What the user sees and when is this section. How a form library holds the values and the schema
is [architecture.md](../architecture/architecture.md) section 11. How a label and an error are tied
to a field for a screen reader, and how focus moves, is [accessibility.md](accessibility.md)
sections 5 and 8.

- **Give every field a visible label outside the field. A placeholder is not a label** (NN/g).
- **Validate a field when the user leaves it, not at each keystroke and never before the input is
  complete. Remove the error as soon as the user fixes it, and confirm a field that is valid.**
  Baymard measured that 31% of the e-commerce sites it tested have no inline validation and 4% do
  it badly; it recommends validating on blur. NN/g asks for inline validation, and none before the
  input is complete.
- **Show an error in text, next to its field.** NN/g: not only in a summary at the top, never in a
  tooltip, and colour together with an icon or a word.
- **When a submit finds errors, move the focus to the first field with an error,** so the user
  lands where the work is (Vercel's interface guidelines: "Errors inline next to fields; on submit,
  focus first error").
- **Pick the input's `type` and `inputmode`,** so a phone shows the keyboard the field needs: a
  number pad for an amount, an email keyboard for an email (web.dev).

What never goes into a form:

| Never | Why | Instead | Source |
|---|---|---|---|
| a placeholder as the only label | it disappears at the first keystroke | a visible label | NN/g |
| validation while the user is still typing | the error appears before the input is complete | validate on blur | NN/g, Baymard |
| errors only in a summary, or in a tooltip | the user has to hunt for the field | the error next to the field | NN/g |
| blocked paste (an `onPaste` that cancels) | the user retypes what they copied, such as a long payment reference | let paste through | Vercel: "NEVER: Block paste in `<input>`/`<textarea>`" |
| a text input smaller than 16 px | iOS Safari zooms the page in when the field gets focus | `text-base` (16 px) on every text input | Vercel: "Mobile `<input>` font-size ≥16px to prevent iOS zoom" |
| zoom switched off in the viewport tag | a user who needs larger text cannot get it | the plain viewport tag below | Vercel: "NEVER: Disable browser zoom (`user-scalable=no`, `maximum-scale=1`)" |

A field labelled only by its placeholder:

```tsx
// Bad: the placeholder is the only label. It disappears at the first keystroke,
// so the user has to clear the field to see what it asked for.
<input
  name="reference"
  placeholder="Payment reference"
  // 16 px: a smaller input makes iOS Safari zoom the page in on focus (ux.md section 4).
  // border-input: the field's edge at 3:1 (visual-design.md section 4); min-h-9 and
  // pointer-coarse:min-h-11: the target heights of ux.md section 8.
  className="min-h-9 rounded-control border border-input px-3 text-base pointer-coarse:min-h-11"
/>
```

Once the user types, nothing on the screen says what the field is for. The same field with a
visible label (not from the reference application, which has no such field; type-checked and
linted in a temporary file). The `input` role its border uses is in the application's theme for
this field ([visual-design.md](visual-design.md) section 3):

```tsx
<label className="flex flex-col gap-1">
  <span className="text-sm font-medium">Payment reference</span>
  <input
    name="reference"
    // 16 px: a smaller input makes iOS Safari zoom the page in on focus (ux.md section 4).
    // border-input: the field's edge at 3:1 (visual-design.md section 4); min-h-9 and
    // pointer-coarse:min-h-11: the target heights of ux.md section 8.
    className="min-h-9 rounded-control border border-input px-3 text-base pointer-coarse:min-h-11"
  />
</label>
```

Why it is good: the label stays on screen above the field while the user types, and the `<label>`
around the input names it. The input keeps 16 px, with its reason at the line, because a reader
who wants the field to match the 14 px label would otherwise shrink it. Its edge is the `input`
role at 3:1, so the user can see where to type, and it is 36 px high with a mouse and 44 px with a
finger (section 8).

The billing application's payment form uses visible labels for a group of choices. It is cut to
the group:

```tsx
<fieldset className="flex flex-col gap-2">
  <legend className="text-sm font-medium">Payment method</legend>
  {/* min-h-6: the 24 px floor of a target; pointer-coarse:min-h-11: 44 px on a touch screen
      (ux.md section 8). */}
  <label className="flex min-h-6 items-center gap-2 pointer-coarse:min-h-11">
    {/* One method is always chosen, so `payInvoice` never parses an empty choice. */}
    <input type="radio" name="method" value="card" defaultChecked />
    Card
  </label>
  <label className="flex min-h-6 items-center gap-2 pointer-coarse:min-h-11">
    <input type="radio" name="method" value="bank_transfer" />
    Bank transfer
  </label>
</fieldset>
```

Why it is good: the group has a visible name, "Payment method", and each choice has visible text
the user can click as well as the small radio button. Each label is at least 24 px tall and 44 px
on a coarse pointer, the target sizes of section 8, with the reason at the line. One choice is set
at the start, so the form has no empty state to validate.

Zoom switched off:

```html
<!-- Bad: maximum-scale=1 and user-scalable=no stop the user from zooming the page. -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1, user-scalable=no" />
```

A user with low vision cannot enlarge the page. The application's viewport tag, from its built
`index.html`:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
```

Why it is good: the page fits the device and the user can still zoom. If the zoom on focus was what
the BAD line tried to stop, the 16 px input stops it without taking zoom away.

## 5. Undo over confirmation

**When an action can be reversed, do it at once and offer undo; keep a confirmation for an action
that is serious and cannot be reversed.** NN/g (2018, reviewed 2026-08-07): a confirmation dialog
used for everyday actions trains users to click through it, so it no longer protects the one action
that needed it. Vercel's guidelines give the same pair: "Confirm destructive actions or provide
Undo window".

| Action in the billing screens | Can it be reversed? | What the screen does |
|---|---|---|
| archive an invoice | yes, if the server can restore it | archives at once and shows "Invoice archived" with an Undo button |
| clear a filter | yes | clears at once; Back brings the filter back (section 7) |
| pay an invoice | no | a step that shows the amount and the method before the one button that pays |
| delete a customer with all their invoices | no | a confirmation before anything is deleted |

Bad: an "Are you sure?" dialog before every archive. The user meets it many times a day, learns to
press OK without reading, and presses it the one time it mattered. Good: the archive happens at
once and the message offers Undo. The user loses nothing by a slip, and the dialogs that remain are
rare enough to be read. Undo needs the server to keep the action reversible for as long as the offer
shows; where it cannot, the action is irreversible and gets the confirmation. How long the message
stays and how it is announced is [accessibility.md](accessibility.md) section 7.

## 6. Empty states

**When a list or a screen has nothing to show, say so in words: tell empty apart from still
loading, say what will appear here, and give a direct path to the task that fills it** (NN/g),
**where the user can do that task.**

```tsx
// Bad: an empty list renders nothing. The user sees a heading over a blank
// area and cannot tell an empty list from one that failed or is still loading.
if (invoices.length === 0) {
  return null;
}
```

A blank area says nothing. The application's invoice list, cut to its empty case:

```tsx
if (invoices.length === 0) {
  return <p className="text-muted-foreground">No invoices yet. A new invoice appears here when it is issued.</p>;
}
```

Why it is good: the message says the list is empty and what will appear in it, and when. It can
never show during loading: the list reads its data with `useSuspenseQuery`, so it renders only once
the data has arrived, and until then the route shows its loading state. A user of this screen does
not issue invoices, so it has no action.

## 7. State in the URL

**When a user changes what a screen shows, put that change in the URL: the item in view, a filter,
a sort, a tab, a page number, an open panel.** A reload, the Back button, a new tab and a link sent
to a colleague then bring back the same view. Vercel's guidelines: "URL reflects state (deep-link
filters/tabs/pagination/expanded panels)".

Bad: the status filter of the invoice list lives in component state. A reload shows all invoices
again, Back leaves the screen instead of undoing the filter, and a link to "the overdue invoices"
opens the full list. Good: the filter is in the search params (`/invoices?status=overdue`), and the
invoice being paid is in the path (`/invoices/<id>/pay`), as the billing application's routes have
it. How a route reads and validates its search params is
[architecture.md](../architecture/architecture.md) sections 7 and 10. What must never
go into a URL is [security.md](../security/security.md) section 13.

## 8. Pointer and touch

- **Never hide an action or important information behind hover.** web.dev's interaction module
  says the same, and pairs every hover style with a focus style. A touch screen has no hover, and a
  keyboard user never triggers it.

  ```tsx
  // Bad: the Pay link shows only while the pointer is over the row. A touch
  // screen has no hover, and a keyboard user tabs to a link they cannot see.
  <tr key={invoice.id} className="group border-b border-border">
    ...
    <td className="opacity-0 group-hover:opacity-100">{status === "paid" ? null : renderPayLink(invoice)}</td>
  </tr>
  ```

  The action exists only for a mouse. The application's invoice row, cut to the row and the cell
  that holds the action:

  ```tsx
  <tr key={invoice.id} className="border-b border-border">
    ...
    <td>{status === "paid" ? null : renderPayLink(invoice)}</td>
  </tr>
  ```

  Why it is good: every unpaid row shows its Pay link on every device, and a paid row shows none,
  so the action is where the user looks for it and nothing appears or disappears under the pointer.
  The link the cell renders is at least 24 px tall, the floor below, and 44 px on a coarse pointer
  (`min-h-6` and `pointer-coarse:min-h-11` in the route's `renderPayLink`, which
  [accessibility.md](accessibility.md) section 3 shows).
- **Make every target at least 24 by 24 CSS px, and larger on a touch screen.** The floor, its
  exceptions and its check are [accessibility.md](accessibility.md) sections 9 and 14, and the
  sizes a designer works with (the 24 px floor, Apple's 44 pt, Google's 48 dp) are in the table of
  accessibility.md section 9. Vercel's guidelines add a number of their own: at least 24 px, 44 px
  on mobile, and a larger hit area where the visible part is smaller.

- **Grow targets when the main pointer is coarse,** so a desktop screen keeps its density and a
  finger still hits the control. web.dev treats a finger on a touch screen as a coarse pointer and
  uses `@media (pointer: coarse)` for larger buttons. Tailwind's `pointer-coarse:` variant is that
  media query (read 2026-10-01). The application's button, cut to its class list:

  ```tsx
  className="min-h-9 rounded-control bg-primary px-4 text-sm font-medium text-primary-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring disabled:opacity-60 pointer-coarse:min-h-11"
  ```

  Why it is good: with a mouse the button is 36 px high (`min-h-9`), well over the 24 px floor; with
  a finger it is 44 px (`pointer-coarse:min-h-11`), Apple's default size and Vercel's mobile size.
  The visible focus outline is [accessibility.md](accessibility.md) section 5; the colours are roles
  ([visual-design.md](visual-design.md) section 3).

## 9. The heuristics as a reviewer's lens

Jakob Nielsen's ten usability heuristics (1994, updated 2024-01-30) are a lens for a person who
walks through a screen before it ships. Ask each question on the screen itself, with real data and
on a phone as well as a desktop.

| Heuristic | Ask on the screen | Where this practice covers it |
|---|---|---|
| 1. Visibility of system status | After each click, can I tell what the system is doing? | sections 2, 3 |
| 2. Match between the system and the real world | Are the words the ones the user uses, not the backend's? | the copy on each screen |
| 3. User control and freedom | Can I undo a slip, and does Back do what I expect? | sections 5, 7 |
| 4. Consistency and standards | Does the same thing look and act the same on every screen? | [visual-design.md](visual-design.md) section 3 |
| 5. Error prevention | Does the screen stop a mistake before it happens, such as a double payment? | sections 2, 4, 5 |
| 6. Recognition rather than recall | Is everything I need visible, with nothing to remember from another screen? | sections 4, 8 |
| 7. Flexibility and efficiency of use | Can a frequent user reach a view fast, for example from a saved link? | section 7 |
| 8. Aesthetic and minimalist design | Does every element on the screen earn its place? | [visual-design.md](visual-design.md) section 2 |
| 9. Help users recognize, diagnose and recover from errors | Does each error say what happened, what it means and what to do? | sections 2, 4 |
| 10. Help and documentation | When the screen is empty or new, does it tell me what goes here? | section 6 |

The lens is for a person, and it checks the built screen, not the brief. A study of 120 interfaces
from five generative UI tools ("Design Theater", a 2026 preprint) found that the tools recognized
about half of the UX principles written into their prompts (a mean of 0.54), and four of the five
built 6% or fewer of the functional principles. A principle written into a prompt is not a
principle built into the screen. How to review a screen a coding agent built, and why a model
should not be the only reviewer, is [designing-with-claude-code.md](designing-with-claude-code.md) section 6.

## 10. Where it stops holding

- **An action the server cannot reverse.** Undo is not available; the action gets a confirmation
  step (section 5).
- **Data that must not appear in a URL.** The URL rule of section 7 stops at anything
  [security.md](../security/security.md) section 13 keeps out of URLs.
- **A native mobile application.** Apple's and Google's platform guidelines decide its targets,
  gestures and patterns.
- **A brand or marketing page.** Most rules here still hold: a sign-up form is a form, and a slow
  page still needs feedback. The look of such a page is [visual-design.md](visual-design.md) sections 2 and 12,
  where it stops holding.
- **Code no change touches.** It keeps its behaviour until a change edits it
  ([refactoring.md](../../any-language/refactoring/refactoring.md) section 2).

## 11. Review checklist

A review question per section. A red flag that fails a WCAG 2.2 A or AA criterion means the screen
is not ready. Any other single red flag is something to raise with the author; a screen that shows
two or more is not ready.

| Section | Ask | Red flag |
|---|---|---|
| 2. Feedback | Does every action answer at once, and does every failure say what to do? | A button that keeps its label while it waits; "Something went wrong" |
| 3. Loading | Does each wait show what its length calls for? | A spinner that flashes on a fast request; a skeleton on every request; a screen that can be blank |
| 4. Forms | Does every field have a visible label, and do errors appear on blur, next to the field? | A placeholder as the label; errors only at the top; blocked paste; an input under 16 px; zoom switched off |
| 5. Undo | Is each confirmation dialog guarding an action that cannot be reversed? | "Are you sure?" before a reversible action |
| 6. Empty states | Does an empty screen say what goes here, and only after loading ends? | A blank area; an empty message during loading |
| 7. URL | Do reload, Back and a shared link bring back the same view? | A filter, tab or page number kept only in component state |
| 8. Pointer and touch | Is every action visible without hover, and big enough for a finger? | An action that appears only on hover; a target under 24 px |
| 9. Heuristics | Did a person walk through the built screen with the ten questions? | Only the prompt or a model's review was checked |

## 12. Sources

### Feedback and loading

1. NN/g, "Response Times: The 3 Important Limits" (1993):
   https://www.nngroup.com/articles/response-times-3-important-limits/ — 0.1 s, 1 s and 10 s.
2. NN/g, skeleton screens (2023, reviewed 2026-09-02): https://www.nngroup.com/articles/skeleton-screens/
   — no indicator under 1 s, skeletons only for waits under 10 s, progress bars beyond.
3. NN/g, progress indicators (2014): https://www.nngroup.com/articles/progress-indicators/ — a
   looped animation for 2 to 10 s, percent done beyond 10 s, users wait about three times longer
   with an animated bar, static indicators and warnings not to click twice fail (read as a summary;
   an older study).
4. Viget, "A Bone to Pick with Skeleton Screens" (2017):
   https://www.viget.com/articles/a-bone-to-pick-with-skeleton-screens — skeletons felt slowest;
   136 mobile users, a small blog experiment.

### Forms

5. NN/g, error messages in forms (2019, reviewed 2024-12-12):
   https://www.nngroup.com/articles/errors-forms-design-guidelines/ — inline errors next to the
   field, no validation before the input is complete, no summary-only or tooltip errors, colour
   with an icon or text.
6. NN/g, placeholders in form fields (2014, reviewed 2018):
   https://www.nngroup.com/articles/form-design-placeholders/ — a placeholder does not replace a
   label.
7. Baymard Institute, inline form validation: https://baymard.com/blog/inline-form-validation —
   31% of tested sites without inline validation; validate on blur, remove the error as the user
   corrects it.
8. Vercel, Web Interface Guidelines: https://vercel.com/design/guidelines,
   https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md and
   https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/AGENTS.md — focus
   the first error, 16 px inputs, never block paste or zoom, undo or confirm, state in the URL, hit
   targets; one design team's rules.
9. web.dev, Learn Design, Interaction: https://web.dev/learn/design/interaction — `type` and
   `inputmode`, coarse pointers, nothing behind hover, hover paired with focus (read as a summary).

### Undo, empty states, the URL

10. NN/g, confirmation dialogs (2018, reviewed 2026-08-07):
    https://www.nngroup.com/articles/confirmation-dialog/ — prefer undo; overused confirmations
    train users to click through.
11. NN/g, empty states: https://www.nngroup.com/articles/empty-state-interface-design/ — tell empty
    from loading, teach what goes here, give a path to the task.

### Pointer and touch

12. W3C, Understanding SC 2.5.8 Target Size (Minimum):
    https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html — 24 by 24 CSS px and its
    exceptions.
13. Apple, Human Interface Guidelines, Accessibility:
    https://developer.apple.com/design/human-interface-guidelines/accessibility, read through its
    data file https://developer.apple.com/tutorials/data/design/human-interface-guidelines/accessibility.json
    — 44 by 44 pt default, 28 by 28 pt minimum on iOS and iPadOS.
14. Google, Accessibility Help, touch target size:
    https://support.google.com/accessibility/android/answer/7101858 — at least 48 dp (read as a
    summary).
15. Tailwind CSS, Hover, focus, and other states: https://tailwindcss.com/docs/hover-focus-and-other-states
    — the `pointer-coarse` variant maps to `@media (pointer: coarse)` (read 2026-10-01).

### The heuristics

16. NN/g, "10 Usability Heuristics for User Interface Design" (1994, updated 2024-01-30):
    https://www.nngroup.com/articles/ten-usability-heuristics/ — the ten heuristics by name.
17. "Design Theater" (arXiv preprint, 2026-07-24): https://arxiv.org/abs/2607.22928 — tools built
    few of the UX principles written into their prompts; 120 interfaces from five tools.
