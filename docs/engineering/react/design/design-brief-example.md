# Example: designing the invoices screen with Claude Code

A worked example for [designing-with-claude-code.md](designing-with-claude-code.md). The billing
application of Acme Corp, an invented company, needs a screen that lists its invoices: an accounts
clerk opens it to see which invoices are due or overdue and to start paying one. The example
follows that screen from the lines the project's instruction file holds for design, through the
brief and the reviewer's checklist, to code that meets the brief, with the reason next to each
part. All names are placeholders. The theme and the pay screen already exist, so the look is not
open, and the brief asks for no visual directions
([designing-with-claude-code.md](designing-with-claude-code.md) section 4).

The files the example touches, in the tree of
[file-structure.md](../../any-language/file-structure/file-structure.md), whose React case is
[architecture.md](../architecture/architecture.md) section 3:

```text
src/
├── main.tsx                          the router, with a loading and a failed state for every route
├── styles.css                        the theme: colour and radius roles, both colour schemes
├── core/ui/
│   ├── button.tsx                    Button: the one button every screen uses
│   └── screen-pending.tsx            ScreenPending: the loading state
├── billing/list-invoices/
│   ├── external-link.tsx             ExternalLink: a link that leaves the application
│   ├── invoice-list.tsx              InvoiceList: the table and its empty state
│   └── invoice-status-badge.tsx      InvoiceStatusBadge: a status as a word in its role colour
└── routes/
    ├── -screen-error.tsx             ScreenError: the failed state, with a retry (the router's error screen)
    ├── invoices.index.tsx            the invoices screen
    └── invoices.$invoiceId.pay.tsx   the pay screen, which the brief points at
```

Why it is good: each file sits where architecture.md section 3 puts its kind (the route files and
the router's error screen in `routes/`, the module's own files in `billing/list-invoices/`, the
shared UI in `core/ui/`), so a reader finds a file by its kind.

`screen-pending.tsx` and `-screen-error.tsx` exist before the brief and are not in its diff: step 6
takes the loading and the failed state from the router's defaults in `main.tsx`.

Not shown: the rule that decides a status (`invoice-status.rules.ts`) and the type it returns
(`invoice-status.schema.ts`), the query
(`invoices.queries.ts`), the money helper in `core/`, the rule that decides which
customer addresses `ExternalLink` may link (`link-url.rules.ts`), the error reporter that
`main.tsx` hands to `createRoot`, and the pay screen's form.

## The design lines in `CLAUDE.md`

The project's instruction file holds three lines for design, under a heading of their own:

```markdown
## Design
- When you style a screen, take every colour and radius from the roles in `src/styles.css`, except
  `rounded-full` on a circle or a pill and `transparent` on a part that shows no colour
  (visual-design.md section 3); when one is missing, add the role there first, with a value for
  each colour scheme. The diff shows the new role next to the first screen that uses it.
- Before you add a control to a screen, use a native element, a component from `src/core/ui/` or
  one of the module's own; a new shared one goes in `src/core/ui/`. The diff adds no second
  button, link or dialog.
- Before you design, build or review a screen, read `docs/engineering/react/design/README.md` and
  the file it routes to for that work. The closing summary names the files you read.
```

Why it is good:

- **Each line has a moment, an act and something in the diff or the summary that shows it was
  done**, the test that
  [claude-md.md](../../../claude-code/claude-md.md#how-to-write-a-line-an-agent-can-follow) gives
  for a line an agent can follow.
- **The first line puts the spec where the build reads it.** The theme in the result holds the roles and
  clears Tailwind's default palette, so a palette colour outside the roles gives no style at all,
  while the keywords `transparent`, `current` and `inherit` stay. Putting the project's design
  system above the model's own choices is this practice's choice for a screen in the repository
  (designing-with-claude-code.md section 3).
- **The second line is the component rule as an act.** The folder is the list of components, so no
  list goes stale here (designing-with-claude-code.md section 8).
- **The third line routes to this practice** instead of copying it into a file every session
  loads.

What is not in it, and why: no component list (designing-with-claude-code.md section 8); no list
of looks to avoid, since those change with each model and belong in the brief; and no standing
request for a reviewer subagent, which the brief asks for instead
(designing-with-claude-code.md section 6).

## The brief

The brief is one message: the steps below, then the checklist of the next section in its tag. It
is a prompt a person types, so the rules that
[prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 19
keeps for one apply to it.

```text
Build the invoices screen at the route /invoices. An accounts clerk at Acme Corp opens it to see
which invoices are due or overdue and to start paying one. The module is
src/billing/list-invoices/ and the route file is src/routes/invoices.index.tsx. The steps are in
the order the work happens, and each ends with how anyone can tell it was done.

1. Before you write code, read src/routes/invoices.$invoiceId.pay.tsx and the components in
   src/core/ui/, and take screenshots of the pay screen the way step 8 describes, with before- in
   place of the round at the front of each name. Give the new screen the pay screen's frame: a
   section, the h1, then the module.
   Check: the section and the h1 carry the same classes as the pay screen's.
2. When you lay out the data, show one table row per invoice, with the columns Customer, Amount,
   Due and Status, and a last column with a Pay link for each unpaid invoice. Show the customer's
   name as a link to the customer's address, through the module's ExternalLink, when the address
   is known. Give amounts and dates tabular-nums, so the digits line up. Check: a paid invoice's
   row has no Pay link.
3. When you pick a colour or a radius, use a role from src/styles.css: background, foreground,
   muted-foreground, border, primary, success, destructive or ring, and rounded-control for a
   control. The theme clears Tailwind's own palette, so a class such as bg-blue-500 gives no
   style. Check: every colour and radius class in the diff names one of these roles, or is one of
   the two exceptions of visual-design.md section 3.
4. When you show a status, write its word in its role colour: Paid in success, Due in
   muted-foreground, Overdue in destructive. Check: the status reads the same in a greyscale
   screenshot.
5. When you write the screen's words, use these: the heading "Invoices"; for the empty state, "No
   invoices yet. A new invoice appears here when it is issued."; the link "Pay", followed for
   screen readers by "the invoice of" and the customer's name. Check: the diff adds no visible
   text beyond these, the column names of step 2 and the status words of step 4.
6. Design four states: loading, failed, empty, and the list. Loading and failed come from the
   router's defaults in src/main.tsx (ScreenPending and ScreenError, the latter in
   src/routes/-screen-error.tsx); write the empty state in
   the list itself. Check: each state has its screenshots in step 8.
7. Where your first idea is one of these, do what follows the arrow instead:
   - a card for each invoice -> the table row of step 2;
   - a gradient or a tinted panel behind the heading -> the background role of step 3;
   - a coloured pill for each status -> the status word of step 4;
   - an icon-only Pay button -> the Pay link of step 5.
   Check: the reviewer in step 9 finds none of the four.
8. When the screen builds, start the app with /run and open /invoices with playwright-cli. Take
   a screenshot of each state of step 6, and of the pay screen, at 1280 and 390 pixels wide, in
   the light and the dark colour scheme. Produce the loading state with a response held back
   until its screenshots are taken, then the empty and the failed states with the CLI's request
   mocking. Check: 16 screenshots of the invoices screen and 4 of the pay screen, each named for
   its round, screen, state, width and colour scheme, such as round-1-invoices-empty-390-dark.png.
9. Then start a reviewer subagent with a fresh context. Give it steps 1 to 8 of this brief in
   <brief>, the diff in <diff>, the screenshot file names in <screenshots> and the checklist in
   <review_checklist>. Fix what it
   reports, take the screenshots of step 8 again under the next round's name, then start a new
   reviewer the same way. Check: after the second review, stop and send me the screenshots and
   every item still open.
```

Why it is good:

- **The goal comes first, then the steps in the order the work happens**, each with the rule that
  decides it ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md)
  section 2). Nothing in it tells the model how to think.
- **The spec is values, not adjectives**: the roles one by one, the components, the screen to
  follow, the four states and every word the screen shows
  (designing-with-claude-code.md section 4).
- **Each thing to avoid has its "instead"** in step 7. Naming the patterns to avoid is the Opus 5.5
  guide's method; the "instead" for each is the rule of designing-with-claude-code.md section 3,
  with prompt-engineering.md section 9. The first three echo looks that sources reported for
  generated screens (repeated cards, gradients, pill shapes;
  designing-with-claude-code.md section 4); the fourth is particular to this screen.
- **Each step names its moment, its act and how anyone can tell it was done**, so a missed step
  shows in the diff or in the screenshots, not only in the model's own report.
- **Each requirement appears once** (prompt-engineering.md section 9): the roles in step 3, the
  words in step 5, the sizes in step 8, and each arrow of step 7 points at the step that holds the
  requirement instead of stating it again. What step 9 hands the reviewer is pasted in, so each
  piece sits in a named tag and the step refers to it by that name: steps 1 to 8 in `<brief>`, the
  diff in `<diff>`, the screenshot file names in `<screenshots>` and the checklist in
  `<review_checklist>`
  ([prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 5).
- **The reviewer is asked for in the brief, with a stop after two reviews**
  (designing-with-claude-code.md section 6). It gets steps 1 to 8, so it can answer the checklist
  items that point at them. Each round takes its screenshots again under its own name, so no set
  overwrites another and the second reviewer judges the fixed screen. The pay screen's `before-`
  screenshots from step 1 let the reviewer see whether the change broke a screen it did not mean
  to touch.

## The reviewer's checklist

The brief ends with this block:

```text
<review_checklist>
Read the code first, then the screenshots. Report only the items the screen fails, each with a
file and line or a screenshot name; a wish that no item covers is not a finding.

In the code:
1. Colours and radii: every class names a role from src/styles.css, or is rounded-full on a
   circle or a pill, or transparent on a part that shows no colour. Fails when a class names a
   palette colour such as bg-blue-500, or a value in brackets such as text-[#333].
2. Controls: each one is a component from src/core/ui/, one of the module's own, or a native
   element. Fails when the diff adds a second button component, or a div with an onClick.
3. Status: each status is a word. Fails when a status shows only as a colour or an icon.
4. States: loading, failed, empty and the list each have a code path. Fails when the empty
   state renders an empty table.
5. Accessibility, as the code shows it (docs/engineering/react/design/accessibility.md, sections 3,
   5 and 8): native elements, a name or a label for each control, a visible focus style. Fails
   when a control is a div or a span with an onClick, a control or a field has no name or label,
   or focus is removed with nothing in its place.
6. The brief: the section and h1 classes of step 1, the columns and the Pay link of step 2, and
   the words of step 5. Fails on any difference.

In the screenshots:
7. Coverage: one for each screen, state, width and colour scheme in step 8 of the brief. Fails
   when one is missing.
8. The looks to avoid: none of the four in step 7 of the brief. Fails when any one shows.
9. The pay screen: each before- screenshot matches the latest round's screenshot of the same name
   after the prefix. Fails on any difference.
</review_checklist>
```

Outside the checklist, and not for the subagent: a person runs the manual pass of
[accessibility.md](accessibility.md) section 11 on the screen before the merge.

Why it is good:

- **The code comes first, then the screenshots.** A model judge did better on the code than on the
  screenshot (designing-with-claude-code.md section 6).
- **Each item says when it fails**, so the reviewer reports a fact a person can check. The opening
  line limits the report to failures, which answers Claude Code's warning that a reviewer asked to
  find gaps usually reports some.
- **Item 5 asks only what the code shows and routes to [accessibility.md](accessibility.md)
  sections 3, 5 and 8 instead of copying them**, so the checklist stays true when that file
  changes. The manual pass of section 11 needs a keyboard, a screen reader and changed browser
  settings, so the reviewer cannot answer it from a diff and screenshots: a person runs it
  before the merge, outside the checklist.
- **Item 9 looks at the screen the change did not mean to touch**: edits break earlier work
  (designing-with-claude-code.md section 6).

## The result

The code below is the reference application's, quoted as it is. The application is not in this
folder; the example files of the `react/` practices quote its code, and the checks named in the last
section were run on it on 2026-10-01 and 2026-10-02. The code meets the brief, but it was not
produced by running the brief, and the brief's steps 8 and 9 were not run on it (see the last
section).

### The theme: `src/styles.css`

The theme is the file [visual-design.md](visual-design.md) section 3 shows in full.

Why it is good:

- **Roles, not colours** (designing-with-claude-code.md section 3). The names follow shadcn/ui's
  roles (`background`, `foreground`, `muted-foreground`, `primary`, `destructive`, `border`,
  `input`, `ring`), so a component taken from its registry finds the roles this theme has. Before
  you add one, add the roles it uses that the theme lacks: the registry's Radix-based
  `new-york-v4` Button, for one, uses `secondary` and `accent` (`input` is in the theme already),
  and its `text-white` needs a foreground role in its place, because the theme clears the default
  palette; the Base UI styles' Button uses `secondary` and `muted` (the registry's source, read
  2026-10-02:
  https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/registry/new-york-v4/ui/button.tsx
  and https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/registry/styles/style-vega.css).
  `success` is the
  one role the invoices screen adds, for paid invoices. Which roles a theme holds is
  [visual-design.md](visual-design.md) section 3.
- **The surface roles have their `-foreground` pair**, shadcn/ui's naming rule, so text on a
  `primary` surface has a role of its own, and the comment says so at the top.
- **Each role holds both colour schemes on one line**, with `light-dark()` under
  `color-scheme: light dark`. shadcn/ui's own theme puts the dark values under a `.dark` class
  instead; how a theme switches is [visual-design.md](visual-design.md) section 9.
- **The build enforces step 3 of the brief.** `@theme inline` turns each role into utilities such
  as `bg-primary` and `text-muted-foreground`, and `--color-*: initial` clears Tailwind's default
  palette (Tailwind CSS 4.3, read 2026-10-01). The comment on that line keeps the next editor from
  deleting it to "get the colours back".
- **Type sizes come from Tailwind's default scale** (`text-sm`, `text-2xl` in the files below),
  so the theme holds only the values this application changes.

The contrast of each pair was computed for both colour schemes when the reference application was
verified. The pairs are tokens, so their table is [visual-design.md](visual-design.md) section 4,
and the floors are in [accessibility.md](accessibility.md) section 9.

### The shared button: `src/core/ui/button.tsx`

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

Why it is good:

- **It is the one button every screen uses** (the second line of `CLAUDE.md`); on the invoices
  screen it is the "Try again" of the failed state below.
- **Its classes name roles only**: `bg-primary`, `text-primary-foreground`, `rounded-control`,
  `outline-ring`.
- **The comment on `type` gives the reason for the default** (readability.md section 4), so a
  reader does not drop it as noise.
- **The focus outline is visible, in the `ring` role, and the target grows on a coarse pointer**
  (`pointer-coarse:min-h-11`); the comment above `className` gives the reason for both. Focus and
  target size are in [accessibility.md](accessibility.md) sections 5 and 9.

### The screen: `src/routes/invoices.index.tsx`

The file with its last function cut: `toIsoDate`, which only this route uses, so it stays here and
not in `core/` ([file-structure.md](../../any-language/file-structure/file-structure.md) section 4):

```tsx
import { createFileRoute, Link } from "@tanstack/react-router";

import { InvoiceList } from "@/billing/list-invoices/invoice-list.tsx";
import { invoicesQueryOptions } from "@/billing/list-invoices/invoices.queries.ts";

export const Route = createFileRoute("/invoices/")({
  // The loader runs as soon as the URL matches, in parallel with the download of this route's
  // code, so the request never waits for a component to render first (architecture.md section 8).
  loader: async ({ context }) => {
    await context.queryClient.query(invoicesQueryOptions(context.apiClient));

    // The clock is read here, once per visit, and passed down as a value: rendering stays pure
    // (components.md section 2).
    return { today: toIsoDate(new Date()) };
  },
  staticData: { title: "Invoices" },
  component: InvoicesScreen,
});

function InvoicesScreen() {
  const { apiClient } = Route.useRouteContext();
  const { today } = Route.useLoaderData();

  return (
    <section className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">Invoices</h1>
      <InvoiceList
        apiClient={apiClient}
        today={today}
        renderPayLink={(invoice) => (
          // min-h-6: the 24 px floor of a target; pointer-coarse:min-h-11: 44 px on a touch screen
          // (ux.md section 8).
          <Link
            to="/invoices/$invoiceId/pay"
            params={{ invoiceId: invoice.id }}
            className="inline-flex min-h-6 items-center underline underline-offset-2 pointer-coarse:min-h-11"
          >
            Pay<span className="sr-only"> the invoice of {invoice.customerName}</span>
          </Link>
        )}
      />
    </section>
  );
}
```

Why it is good:

- **It has the pay screen's frame**: the same `section` and the same `h1` classes (step 1 of the
  brief), so the two screens line up without a new layout component.
- **The route builds the screen and supplies the Pay link**, so the module imports no router and
  no other module's path ([file-structure.md](../../any-language/file-structure/file-structure.md)
  section 2: a module never imports an adapter).
- **The clock is read once, in the loader, and passed down as a value**
  ([readability.md](../../any-language/readability/readability.md) section 6), and the comment
  says why at the line.
- **The link's words are the brief's** (step 5): "Pay" on screen, with the customer's name for a
  screen reader, so ten Pay links in a row are not ten identical names.
- **The link is at least 24 px tall, and 44 px on a coarse pointer** (`min-h-6`,
  `pointer-coarse:min-h-11`), and the comment above it gives the reason ([ux.md](ux.md) section 8).
- **The imports are absolute, through `@/`** (file-structure.md section 7).

### The list and its empty state: `src/billing/list-invoices/invoice-list.tsx`

```tsx
import { useSuspenseQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";

import { ExternalLink } from "@/billing/list-invoices/external-link.tsx";
import { InvoiceStatusBadge } from "@/billing/list-invoices/invoice-status-badge.tsx";
import { invoiceStatus } from "@/billing/list-invoices/invoice-status.rules.ts";
import { invoicesQueryOptions } from "@/billing/list-invoices/invoices.queries.ts";
import type { ApiClient } from "@/core/api-client.ts";
import type { Invoice } from "@/core/invoice.schema.ts";
import { formatCents } from "@/core/money.format.ts";

type InvoiceListProps = {
  // The route hands the client in, like `today`: the component reaches nothing by itself
  // (architecture.md section 8).
  apiClient: ApiClient;
  today: string;
  // The route supplies the link, so this module needs no router and no path of another module
  // (architecture.md section 6).
  renderPayLink: (invoice: Invoice) => ReactNode;
};

export function InvoiceList({ apiClient, today, renderPayLink }: InvoiceListProps) {
  const { data: invoices } = useSuspenseQuery(invoicesQueryOptions(apiClient));

  if (invoices.length === 0) {
    return <p className="text-muted-foreground">No invoices yet. A new invoice appears here when it is issued.</p>;
  }

  return (
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
        {invoices.map((invoice) => {
          // One source for "paid": the badge and the link read the same rule
          // (components.md section 1).
          const status = invoiceStatus(invoice, today);

          return (
            <tr key={invoice.id} className="border-b border-border">
              <th scope="row" className="py-2 font-medium">
                {invoice.customerUrl === null ? (
                  invoice.customerName
                ) : (
                  <ExternalLink href={invoice.customerUrl}>{invoice.customerName}</ExternalLink>
                )}
              </th>
              <td className="tabular-nums">{formatCents(invoice.amountCents)}</td>
              <td className="tabular-nums">{invoice.dueOn}</td>
              <td>
                <InvoiceStatusBadge status={status} />
              </td>
              <td>{status === "paid" ? null : renderPayLink(invoice)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
```

Why it is good:

- **The empty state is a guard at the top, and its sentence says what will appear here** (step 6
  of the brief; readability.md section 3). What an empty state should say is [ux.md](ux.md) section 6.
- **One row per invoice, the brief's columns, and `tabular-nums` on amounts and dates** (step 2),
  so the digits line up down the column.
- **The Pay link appears only while the invoice is not paid** (step 2). The row reads its status
  once, and the badge and the link both use it, so the two never disagree; the comment says so at
  the line.
- **The customer's name is a link only when the invoice has an address, and then it is the
  module's own `ExternalLink`** (step 2), which stays in `billing/list-invoices/` because one module
  uses it ([file-structure.md](../../any-language/file-structure/file-structure.md) section 4), so
  the screen adds no second link component.
- **Every input comes in as a prop**, `apiClient`, `today` and `renderPayLink` (readability.md
  section 6), and the comments on `apiClient` and `renderPayLink` say why each is a prop and not
  an import.
- **The stages show at a glance**: load, guard, render, with a blank line between them
  (readability.md section 5).
- **The table has a caption and header cells with their scope** for a screen reader; the rules for
  tables are in [accessibility.md](accessibility.md) section 3.

### The status: `src/billing/list-invoices/invoice-status-badge.tsx`

```tsx
import type { InvoiceStatus } from "@/billing/list-invoices/invoice-status.schema.ts";

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

Why it is good:

- **The word carries the status and the role colour repeats it** (step 4 of the brief), and the
  comment says so at the line, so nobody trims the word to a coloured dot.
- **Both maps are typed `Record<InvoiceStatus, string>`**: a new status with no word or no colour
  fails the type check.
- **The colours are roles**: `text-success`, `text-destructive`, `text-muted-foreground`.

### Loading and failed: `main.tsx`, `screen-pending.tsx` and `-screen-error.tsx`

From `src/main.tsx`, the router only; the imports, the query client, the type registration and the
render call are cut:

```tsx
const router = createRouter({
  routeTree,
  context: { apiClient, queryClient },
  // Hovering or focusing a link starts its loader, so the data is on its way before the click
  // (performance.md section 5).
  defaultPreload: "intent",
  // TanStack Query decides what is fresh; the router keeps no second copy of loader data
  // (architecture.md section 8).
  defaultPreloadStaleTime: 0,
  // Every route gets a loading state and an error state, so no screen can be blank
  // (architecture.md section 12).
  defaultPendingComponent: ScreenPending,
  defaultErrorComponent: ScreenError,
});
```

`src/core/ui/screen-pending.tsx`:

```tsx
// No live-region role here: this component arrives in the page together with its text, and a
// screen reader often skips such a region. The shell's status region announces the loading
// (accessibility.md section 7).
export function ScreenPending() {
  return (
    <p className="flex items-center gap-2 text-muted-foreground">
      {/* The router shows this screen after its pending delay, so the wait is already about a
          second: a wait of that length gets a spinner (ux.md section 3). motion-safe: keeps it
          still for a user who asked for less motion (visual-design.md section 8). rounded-full
          draws the circle, which has no corner for a radius role (visual-design.md section 7);
          border-t-transparent is the gap: a part that shows no colour takes transparent
          (visual-design.md section 3). */}
      <span
        aria-hidden="true"
        className="size-4 rounded-full border-2 border-muted-foreground border-t-transparent motion-safe:animate-spin"
      />
      Loading…
    </p>
  );
}
```

`src/routes/-screen-error.tsx`, the router's error screen (it imports the router, so it sits with
the routes and not in `core/ui/`; the `-` keeps it out of the route tree):

```tsx
import { useQueryErrorResetBoundary } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { useEffect } from "react";

import { Button } from "@/core/ui/button.tsx";

export function ScreenError() {
  const router = useRouter();
  const queryErrorResetBoundary = useQueryErrorResetBoundary();

  // TanStack Query keeps a failed query failed until it is reset; without this the retry
  // below would show the same cached error again (architecture.md section 12).
  useEffect(() => {
    queryErrorResetBoundary.reset();
  }, [queryErrorResetBoundary]);

  // No `role="alert"` here: this component arrives in the page together with its text. The
  // shell's status region, which is already in the page, announces the failure
  // (accessibility.md section 7).
  return (
    <div className="flex flex-col items-start gap-3">
      {/* The message says what to do (ux.md section 2). The error's own text stays out of the
          page: it can carry details of the server (security.md section 13). */}
      <p>This screen did not load. Check your connection and try again.</p>
      <Button onClick={() => void router.invalidate()}>Try again</Button>
    </div>
  );
}
```

Why it is good:

- **Every route gets the loading and the failed state by default**, so a new screen cannot ship
  without them (step 6 of the brief), and the comment in `main.tsx` says so.
- **The loading state shows a spinner next to its word.** The router shows it after its pending
  delay, a wait of about a second, so it gets a spinner ([ux.md](ux.md) section 3). The spinner
  is `aria-hidden` because the word "Loading…" already says it, and `motion-safe:` keeps it still
  for a user who asked for less motion ([visual-design.md](visual-design.md) section 8).
- **Neither state carries a live-region role**, and each comment says why: a component that arrives
  with its text is often not announced. The shell's `<output>` region, in the page from the first
  render, says "Loading" or "This screen did not load". How a change is announced is
  [accessibility.md](accessibility.md) sections 6 and 7.
- **The failed state tells the clerk what to do and offers the retry** with the shared `Button`.
  The error's own text stays out of the page, and the comment gives the reason at the line. What an
  error message says is [ux.md](ux.md) section 2.
- **Each comment carries a reason a reader would otherwise miss**: why the query is reset, why the
  server's text is hidden (readability.md section 4).

## What was verified, and what was not

The record kept with the application says: the code was type-checked, linted, unit-tested and
built, and the contrast table above was computed from the theme's values. Nothing was run in a
browser. So the screenshots of steps 1 and 8 were never taken, no reviewer ran the checklist on
this code, and the screen-reader text and the focus outline were checked by the type checker and
the linters only.

What the example leaves out: the reference application has no Storybook and no shadcn/ui
`components.json`, so no manifest serves its components; and it has no baseline screenshot test
yet. Once a person has approved the pay screen's screenshots, a `toHaveScreenshot()` test
(designing-with-claude-code.md section 5) turns item 9 of the checklist into a command.
