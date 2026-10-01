# Component and hook rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. The Rules of React: what is not taste](#2-the-rules-of-react-what-is-not-taste)
- [3. Props: the component's signature](#3-props-the-components-signature)
- [4. State inside a component](#4-state-inside-a-component)
- [5. Effects: only to keep an outside system in step](#5-effects-only-to-keep-an-outside-system-in-step)
- [6. Custom hooks](#6-custom-hooks)
- [7. The compiler and memoisation](#7-the-compiler-and-memoisation)
- [8. Events and async work](#8-events-and-async-work)
- [9. Names and files](#9-names-and-files)
- [10. Common mistakes](#10-common-mistakes)
- [11. Where the rules stop holding](#11-where-the-rules-stop-holding)
- [12. Review checklist](#12-review-checklist)
- [13. Sources](#13-sources)

## 1. Purpose and the one rule

This file is for everyone who writes or reviews a React component or a custom hook: people and AI
agents alike. Read it before you write or change one, and when you review one.

Every line that carries a read date is to be distrusted after 2027-04-01 until it is read again;
the README's "How to adopt" says how to list those lines.

It is the React case of [readability.md](../../any-language/readability/readability.md). A
component is a function, and what that file says about a function holds for a component
unchanged: one job, guard clauses, comments that say why, blank lines between stages, every input
in the signature, names from the business. This file adds only what React changes. Where a
component's file sits and what it is called is [architecture.md](../architecture/architecture.md) sections 3 and 4;
how its markup works for every user is [accessibility.md](../design/accessibility.md) section 3; what it may
put into the page from outside is [security.md](../security/security.md) sections 3 and 4.

The one rule: **rendering is a pure function of props, state and context. Everything else happens
in an event handler, or, when it keeps a system outside React in step with the screen, in an
effect.**

Why it matters:

- React decides when a component renders, and may render it more than once: "React can render
  components multiple times to create the best possible user experience" (react.dev). A component
  that reads the clock, or changes a value while it renders, shows a different screen for the same
  inputs.
- A pure component can be followed, and tested, from its props alone, which is readability's one
  rule in React's terms. React can also plan around it: "When render is kept pure, React can
  understand how to prioritize which updates are most important for the user to see first." The
  React Compiler compiles only code that keeps the rules (section 7).

What React changes in readability:

| [readability.md](../../any-language/readability/readability.md) | What React adds |
|---|---|
| Section 2, one job per unit | A component draws one part of the screen. A business decision is a plain function in a `.rules.ts` file that the component calls; a server read is the module's query ([architecture.md](../architecture/architecture.md) section 8). |
| Section 3, guard clauses | An early `return` of JSX is a guard clause, and it comes after every hook call (section 2). |
| Section 6, every input in the signature | The props are the signature. The clock and random numbers are read outside render, in a route's loader or an event handler; a value render needs comes in as a prop (section 2). Context is an input the props do not show (section 3). |
| Section 7, names from the business | A component's name starts with a capital letter, and a hook's name with `use` (sections 6 and 9). |

Each rule below carries one of three labels, so a reader can tell a bug from a choice:

| Label | What it means | What breaking it costs |
|---|---|---|
| Rule of React | React itself depends on it: one of react.dev's Rules of React, or behaviour React needs to work | a bug, even when the screen looks right today. The linter reports most of them (section 2) |
| Advice | react.dev, a library's docs or a named practitioner recommends it; React does not enforce it | extra renders, a stale value, or code that is harder to change. The text names the source |
| Taste | one good way among several; this practice picks one so every component reads the same | nothing but consistency. A team may pick the other ([README.md](README.md), "The points to adapt") |

The examples are TypeScript from one invented application, the billing screens of Acme Corp. The
GOOD code is quoted from a reference application that was type-checked, linted with Oxlint and
ESLint, unit-tested and built; nothing was run in a browser. The BAD code is written by hand and
was not linted: where a lint rule is named next to a BAD, it is the rule that reported the same
problem in that application's negative controls. [component-example.md](component-example.md)
shows a whole module.

Any component or hook a change writes or edits has to meet this file.

## 2. The Rules of React: what is not taste

react.dev publishes the Rules of React in three groups. They are not style: code that breaks one
has a bug, even when the screen looks right today.

**Components and hooks are pure.**

- *Rule of React.* **Give the same output for the same props, state and context.** Never read the
  clock, a random number or anything else that changes between two calls while a component
  renders: React may render it again at any time, and the second render must match the first.
- *Rule of React.* **Run side effects in an event handler or an effect, never during render.**
  Changing a value the component created during this render is fine, such as an array it fills
  for the JSX. Changing anything that existed before render is not: a module variable, a prop, a
  piece of state.
- *Rule of React.* **Treat props, state, the arguments and return values of hooks, and any value
  passed to JSX as read-only.** To change state, pass a new value to its setter, such as
  `setDraft({ ...draft, method })`, never `draft.method = method`. React keeps "immutable
  snapshots"; "mutating values after they've been passed to JSX can lead to outdated UIs, as React
  won't know to update the component's output."

**React calls components and hooks.**

- *Rule of React.* **Render a component with JSX, never call it as a function**:
  `<InvoiceStatusBadge status={status} />`, not `InvoiceStatusBadge({ status })`. "React must
  decide when your component function is called during rendering."
- *Rule of React.* **Call a hook by its own name, inside a component or a hook. Never pass a hook
  around as a value or build one from another**, such as `withLogging(useData)` or
  `<Button useData={useDataWithLogging} />`. Every hook a component uses then shows in its source.

**The Rules of Hooks.**

- *Rule of React.* **Call hooks at the top level of a component or a custom hook, before any early
  return.** Never call one inside a condition, a loop, an event handler, a `try` block, or a
  function passed to another hook.
- *Rule of React.* **Call hooks only from components and custom hooks**, never from a plain
  function, so that "all stateful logic in a component is clearly visible from its source code".
- `use` is the one exception: it reads a promise or a context, and it may sit inside a condition or
  a loop. It may not sit inside `try`/`catch`, and the promise it reads is never created during
  render ([architecture.md](../architecture/architecture.md) section 8).

What happens when a rule breaks:

| Who | What it does |
|---|---|
| The linter | `eslint-plugin-react-hooks` 7 in its `recommended` preset and Oxlint's `react` plugin report a hook called conditionally, a missing effect dependency, and the compiler's diagnostics: an impure call in render, a synchronous `setState` in an effect, a changed prop or state, and more. In the reference application, Oxlint 1.85.0 reported its controls as `react-hooks(rules-of-hooks)`, `react(purity)` and `react(set-state-in-effect)` (read 2026-10-01). Which linter runs which rule is [libraries.md](../architecture/libraries.md) section 4. |
| The compiler | It "skips code that breaks the Rules of React": the component still runs, without the compiler's memoisation. With the lint off, nothing tells you. One practitioner found such a skip only "by way of a re-render regression no profiler was looking for". |
| React, in development | Strict Mode runs each effect's setup, cleanup and setup again, and calls a state initializer twice, so a missing cleanup or an impure initializer shows up while you work. |

Check: CI runs the linter with the hooks rules and the compiler's rules as errors, and fails the
build on one.

A hook after an early return is an easy break to make, because readability's guard clauses pull
the early return to the top.

```tsx
// Bad: the mutation hook sits after the early return. It runs for an unpaid
// invoice and not for a paid one, so the set of hooks changes from one render
// to the next: after a payment, the refetched invoice has `paidOn` set and the
// next render calls one hook fewer.
export function PayInvoiceForm({ apiClient, invoiceId, onPaid }: PayInvoiceFormProps) {
  const { data: invoice } = useSuspenseQuery(invoiceQueryOptions(apiClient, invoiceId));

  if (invoice.paidOn !== null) {
    return <p>This invoice was paid on {invoice.paidOn}.</p>;
  }

  const payment = useMutation(payInvoiceMutationOptions(apiClient, invoiceId));

  ...
}
```

The rule that reports it is `react-hooks(rules-of-hooks)`: in the reference application's control
file, Oxlint reported a conditional `useState` with it.

The GOOD is the form as the application has it, from
`src/billing/pay-invoice/pay-invoice-form.tsx`. The submit handler and the form's markup are cut.

```tsx
export function PayInvoiceForm({ apiClient, invoiceId, onPaid }: PayInvoiceFormProps) {
  const { data: invoice } = useSuspenseQuery(invoiceQueryOptions(apiClient, invoiceId));
  const payment = useMutation(payInvoiceMutationOptions(apiClient, invoiceId));

  ...

  if (invoice.paidOn !== null) {
    return <p>This invoice was paid on {invoice.paidOn}.</p>;
  }

  ...
}
```

Why it is good: both hooks run on every render, paid or not, and the guard clause still ends the
function early ([readability.md](../../any-language/readability/readability.md) section 3). It
only moves below the hooks, which is the one thing React changes about a guard.

Another break is the clock read during render.

```tsx
// Bad: the list reads the clock while it renders. Two renders with the same
// props can show different statuses around midnight, and a test of the list
// has to freeze time.
type InvoiceListProps = {
  // The route supplies the link, so this module needs no router and no path of another module.
  renderPayLink: (invoice: Invoice) => ReactNode;
};

export function InvoiceList({ apiClient, renderPayLink }: InvoiceListProps) {
  const { data: invoices } = useSuspenseQuery(invoicesQueryOptions(apiClient));
  const today = toIsoDate(new Date());

  ...
}
```

The rule that reports it is `react(purity)`: react.dev's page for the rule names `new Date()`
among the calls it rejects, and Oxlint reported the impure call in the reference application's
control file with it.

The GOOD reads the clock in the route's loader, `src/routes/invoices.index.tsx`, and passes the
date down. The pay link the screen passes to the list is cut.

```tsx
export const Route = createFileRoute("/invoices/")({
  // The loader runs as soon as the URL matches, in parallel with the download of this route's
  // code, so the request never waits for a component to render first.
  loader: async ({ context }) => {
    await context.queryClient.query(invoicesQueryOptions(context.apiClient));

    // The clock is read here, once per visit, and passed down as a value: rendering stays pure.
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
        ...
      />
    </section>
  );
}
```

The list takes the date as a prop, in `src/billing/list-invoices/invoice-list.tsx`; its table is
cut.

```tsx
type InvoiceListProps = {
  // The route hands the client in, like `today`: the component reaches nothing by itself.
  apiClient: ApiClient;
  today: string;
  // The route supplies the link, so this module needs no router and no path of another module.
  renderPayLink: (invoice: Invoice) => ReactNode;
};

export function InvoiceList({ apiClient, today, renderPayLink }: InvoiceListProps) {
  const { data: invoices } = useSuspenseQuery(invoicesQueryOptions(apiClient));

  ...
}
```

Why it is good: the route is the adapter, and it reads the clock once and passes the value, as
[readability.md](../../any-language/readability/readability.md) section 6 asks. The list's output
now depends on its props and the cached data alone. The comment at the clock line says why the
call sits in the loader, so nobody moves it back. An event handler may read the clock too: it runs
after render, when the user acts.

## 3. Props: the component's signature

The props are a component's signature, and
[readability.md](../../any-language/readability/readability.md) section 6 applies to them as it
stands. This section adds how to type them and how to shape them. The `apiClient` that
`InvoiceList` takes is one such input: the component calls the client, so the client is a prop and
not an import ([architecture.md](../architecture/architecture.md) section 8 owns where it is built).

- *Taste.* **Type the props on the function's parameter, `function Button({ ... }: ButtonProps)`,
  not with `React.FC`.** Matt Pocock: since React 18 and TypeScript 5.1, `React.FC` "is fine to use
  again", but he still prefers annotating props directly, which is simpler and easier to turn into
  a generic component. So the choice is style, not safety. react.dev's TypeScript page types props
  on plain functions, with a `type` or an `interface`; keep one of the two across the code base.
- *Advice.* **Type `children` as `ReactNode`, an event as the element's event type
  (`SyntheticEvent<HTMLFormElement>`), and a state that holds one of several values with its union
  (`useState<PaymentMethod | null>(null)`)** (react.dev, "Using TypeScript").
- *Advice.* **A wrapper that passes native props through takes them as
  `ComponentProps<"input">`, or `ComponentProps<typeof DatePicker>` for a component you do not
  control, instead of a copied list of attributes** (Matt Pocock). Every attribute the element
  accepts then works through the wrapper. His page names `ComponentPropsWithRef<"input">` for a
  wrapper that also takes a `ref`. A design-system component that offers a closed set of props
  lists them instead, as `Button` below does.
- *Advice.* **In React 19, take `ref` as an ordinary prop, and render a context as
  `<CurrentAccountContext value={account}>`.** Do not write `forwardRef` or `<Context.Provider>` in
  new code. react.dev: "In future versions we will deprecate and remove `forwardRef`"; it
  plans the same for `<Context.Provider>` (read 2026-10-01).
- *Advice.* **Give states that exclude each other one prop with a union type, never one boolean
  per state.** Two booleans for three states allow a fourth that means nothing. When each state
  needs different props, use a discriminated union of
  `{ mode: "single"; onChange: (id: string) => void }` and
  `{ mode: "multi"; onChange: (ids: string[]) => void }`, so TypeScript narrows the callback with
  the mode (Nadia Makarevich).
- *Advice.* **When a component grows one configuration prop per caller (`showPayLink`,
  `payLinkLabel`, `payLinkPath`), let the caller pass the part instead**: `children`, a render
  prop, or compound components that share their state through context, such as `<Tabs>` with
  `<Tabs.List>` and `<Tabs.Panel>`. Kent C. Dodds calls such configuration options "a nightmare to
  use and maintain", and adds a warning: do not build the abstraction before there are several
  real callers. `InvoiceList` takes its pay link as a render prop
  ([component-example.md](component-example.md)).
- *Advice.* **Pass data as props, through a few layers if needed, before you reach for Context.**
  Props show which component reads which data. Context is an input the props do not show; Josh
  Comeau calls it "invisible props", the hidden input
  [readability.md](../../any-language/readability/readability.md) section 6 warns about. react.dev
  lists two steps before Context: pass props, then extract components and pass JSX as `children`.
  Context fits a value many distant components read, such as the theme or the signed-in account.
  Kent C. Dodds: prop drilling in moderation keeps the data flow explicit.

```tsx
// Bad: two booleans for three states that exclude each other. A caller can pass
// isPaid and isOverdue together, and the badge has to guess which one wins.
type InvoiceStatusBadgeProps = {
  isPaid: boolean;
  isOverdue: boolean;
};
```

The GOOD is the badge as the application has it,
`src/billing/list-invoices/invoice-status-badge.tsx`:

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
  // The word carries the status. The colour repeats it and is never the only signal.
  return <span className={`text-sm font-medium ${STATUS_COLOR[status]}`}>{STATUS_LABEL[status]}</span>;
}
```

Why it is good: one prop, typed with the union the business rule returns, so an impossible
combination cannot be written. The two `Record<InvoiceStatus, string>` maps make the type checker
fail when a fourth status is added and its label or colour is missing. The props are typed on the
parameter, and the comment gives the reason the word stays: colour as a cue is
[accessibility.md](../design/accessibility.md) section 9.

A design-system component in `core/ui/` lists the few props it supports,
`src/core/ui/button.tsx`:

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

Why it is good: `type` is a union of the two values the design system allows, not any string, and
its default carries its reason at the line, the one a reader would otherwise "fix"
([readability.md](../../any-language/readability/readability.md) section 4). `children` is a
`ReactNode`. The props are a closed set, so every button in the application looks and behaves the
same; a wrapper that must pass every native attribute through would take `ComponentProps<"button">`
instead.

## 4. State inside a component

Where state that several components or screens share lives, and why server data never goes into
component state, is [architecture.md](../architecture/architecture.md) sections 7 and 8, where state lives and
server data. This section is about the state one component keeps.

- *Advice.* **Keep the smallest state that describes the screen.** react.dev: "If you can calculate
  some information ... during rendering, you should not put that information into ... state."
  Group values that always change together, never keep two values that can contradict each other,
  and prefer flat state to nested state, so state is "easy to update without introducing mistakes".
- *Advice.* **Derive, do not sync: compute a value during render instead of copying it into state
  and keeping the copy in step with an effect.** Kent C. Dodds and TkDodo say the same; TkDodo:
  "Whenever a state setter function is only used synchronously in an effect, get rid of the
  state!" The effect form costs a second render, and the first render shows the old value. A
  costly computation is memoised by the compiler (section 7).
- *Advice.* **Keep state in the lowest component that uses it. When two components need it, lift
  it to their closest common parent, which then owns it alone** (react.dev, "Sharing State Between
  Components"; Kent C. Dodds on colocation).
- *Advice.* **To start a component fresh when what it shows changes, give it a `key`**, such as
  `<InvoiceNoteEditor key={invoice.id} invoice={invoice} />`, instead of an effect that clears its
  fields. A different key at the same place in the tree resets the component's state (react.dev).
- *Advice.* **Key each list item by the id from the data, `key={invoice.id}`.** Never key a list
  that can change order by the item's index, and never by a value made during render such as
  `Math.random()`: the state of one row then lands on another (react.dev, "Rendering Lists").
- *Advice.* **Define every component at the top level of its file, never inside another
  component.** A definition inside a component is a new component type on every render, so its
  state resets each time; react.dev: "very slow and causes bugs".
- *Advice.* **When the first value of a state is costly to build, pass the function, not its
  result**: `useState(() => buildDraft(invoice))`, not `useState(buildDraft(invoice))`. React calls
  the function "only ... during initialization"; the second form runs on every render and throws
  the result away. The function must be pure, since Strict Mode calls it twice in development
  (react.dev, `useState`).
- *Advice.* **Move the update logic into `useReducer` when updates to several values keep going
  wrong together.** Each action names one thing the user did, and the reducer is a pure function
  (react.dev).

```tsx
// Bad: whether the invoice is paid is copied into state and kept in step by an
// effect. The first render shows the payment form for a paid invoice, and the
// effect's second render replaces it.
export function PayInvoiceForm({ apiClient, invoiceId, onPaid }: PayInvoiceFormProps) {
  const { data: invoice } = useSuspenseQuery(invoiceQueryOptions(apiClient, invoiceId));
  const payment = useMutation(payInvoiceMutationOptions(apiClient, invoiceId));
  const [isPaid, setIsPaid] = useState(false);

  useEffect(() => {
    setIsPaid(invoice.paidOn !== null);
  }, [invoice.paidOn]);

  ...

  if (isPaid) {
    return <p>This invoice was paid on {invoice.paidOn}.</p>;
  }

  ...
}
```

The rule that reports it is `react(set-state-in-effect)`, which reported the same pattern in the
reference application's control file; react.dev's page for the rule lists "deriving state from
props" among its wrong examples.

The GOOD reads the value where it is needed, `src/billing/pay-invoice/pay-invoice-form.tsx`, with
the submit handler and the form's markup cut:

```tsx
export function PayInvoiceForm({ apiClient, invoiceId, onPaid }: PayInvoiceFormProps) {
  const { data: invoice } = useSuspenseQuery(invoiceQueryOptions(apiClient, invoiceId));
  const payment = useMutation(payInvoiceMutationOptions(apiClient, invoiceId));

  ...

  if (invoice.paidOn !== null) {
    return <p>This invoice was paid on {invoice.paidOn}.</p>;
  }

  ...
}
```

Why it is good: the guard asks the invoice itself, so there is no copy to fall behind, no second
render, and no frame that shows the wrong screen. The component holds no state at all: the server
data is in the query cache, and the chosen payment method is in the form until submit.

## 5. Effects: only to keep an outside system in step

An effect is for work "caused by rendering itself, rather than by a particular event" (react.dev):
keeping a connection, a subscription, a timer, an animation, a browser API or a widget that is not
React in step with what is on screen. If no system outside React is involved, there is no effect
to write.

*Advice* for the whole table. **Before you write an effect, find your case below; write one only
when no row fits.** The cases are react.dev's "You Might Not Need an Effect".

| You want to | Write instead |
|---|---|
| show a value computed from props or state, such as a filtered list or a label | compute it during render (section 4) |
| compute something slow | compute it during render; the compiler memoises it (section 7) |
| reset all of a component's state when a prop changes | a `key` on the component (section 4) |
| adjust part of the state when a prop changes | compute the value during render. Rarely: keep the previous prop in state and adjust during render |
| run the same logic from two event handlers | a plain function both handlers call |
| send a request because the user did something | send it in that event handler, or through the mutation ([architecture.md](../architecture/architecture.md) section 9) |
| update several pieces of state in a chain | compute the next state in the one event handler |
| run something once when the application starts | code at the top level of a module, or in the startup file |
| tell the parent that the state changed | update both in the same event handler, or lift the state (section 4) |
| pass data up to the parent | let the parent fetch it and pass it down |
| read a value from a store outside React | `useSyncExternalStore` |
| fetch server data | the query cache ([architecture.md](../architecture/architecture.md) section 8). By hand, react.dev still allows an effect with an `ignore` flag in its cleanup, and names the costs: effects "don't run on the server", they make "network waterfalls" easy, and they do not preload or cache |

When an effect is the right tool:

- *Advice.* **Give each effect one concern, list every reactive value it reads as a dependency,
  and never silence `exhaustive-deps`.** react.dev says to "always follow" the lint. When it asks
  for a dependency you do not want, change the code: move the value out of the component, move it
  into the effect, or split the effect in two. Oxlint's `react/exhaustive-deps` reports the missing
  dependency ([libraries.md](../architecture/libraries.md) section 4).
- *Advice.* **Return a cleanup that undoes what the setup started**: close the connection, remove
  the listener, clear the timer, ignore a response that arrives late. In development, Strict Mode
  runs setup, cleanup and setup again, so a missing cleanup shows at once.
- *Advice.* **Move logic that must read the latest props, but must not restart the effect, into
  `useEffectEvent`** (stable since React 19.2; read 2026-10-01). Call the effect event only from
  inside effects, keep it out of the dependency list, and never pass it to another component or
  hook. react.dev: "Do not use `useEffectEvent` to avoid specifying dependencies." The linter
  checks these limits.
- *Advice.* **When `set-state-in-effect` reports an effect that sets state from a value it read
  from a ref, such as a measured height, keep the effect.** react.dev's page for the rule allows
  that case, and the rule has known false positives on it: facebook/react issue #34858 (closed as
  stale) and #34743 (open) (read 2026-10-01). Silence that one line for that one rule, with the
  reason in the comment ([readability.md](../../any-language/readability/readability.md) section
  4).

The only effect in the reference application is in the screen shown when a route fails to load,
`src/routes/-screen-error.tsx`:

```tsx
import { useQueryErrorResetBoundary } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { useEffect } from "react";

import { Button } from "@/core/ui/button.tsx";

export function ScreenError() {
  const router = useRouter();
  const queryErrorResetBoundary = useQueryErrorResetBoundary();

  // A failed query stays failed until it is reset; without this the retry below would show
  // the same cached error again.
  useEffect(() => {
    queryErrorResetBoundary.reset();
  }, [queryErrorResetBoundary]);

  // No `role="alert"` here: this component arrives in the page together with its text. The
  // shell's status region, which is already in the page, announces the failure.
  return (
    <div className="flex flex-col items-start gap-3">
      {/* The message says what to do. The error's own text stays out of the page: it can
          carry details of the server. */}
      <p>This screen did not load. Check your connection and try again.</p>
      <Button onClick={() => void router.invalidate()}>Try again</Button>
    </div>
  );
}
```

Why it is good: the effect keeps an outside system, TanStack Query's error state, in step with the
screen being shown. No user event causes it; the error screen appearing does, which is react.dev's
definition of an effect. TanStack Query's Suspense guide says a suspense query needs "a mechanism
to retry after errors occur", and offers `useQueryErrorResetBoundary` for it. The effect has one
concern, lists its one dependency, and starts nothing that needs a cleanup. The comment says why
it exists, so nobody deletes it as an effect "you might not need". The retry itself runs in the
click handler.

One misuse react.dev names is an effect that does what an event handler should do.

```tsx
// Bad: the payment is sent by an effect that watches a state value, not by the
// submit that causes it. An effect runs when its dependencies change: here it
// runs again whenever `payment` or `onPaid` is a new value while `method` is
// set, and each run sends the payment again.
const [method, setMethod] = useState<PaymentMethod | null>(null);

useEffect(() => {
  if (method !== null) {
    payment.mutate(method, { onSuccess: onPaid });
  }
}, [method, payment, onPaid]);

function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
  event.preventDefault();

  setMethod(paymentMethodSchema.parse(new FormData(event.currentTarget).get("method")));
}
```

The GOOD sends the payment from the submit handler, `src/billing/pay-invoice/pay-invoice-form.tsx`:

```tsx
  function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    const method = paymentMethodSchema.parse(new FormData(event.currentTarget).get("method"));

    payment.mutate(method, { onSuccess: onPaid });
  }
```

Why it is good: the request runs once, when the user submits, and nowhere else. The handler reads
in three stages, each split by a blank line
([readability.md](../../any-language/readability/readability.md) section 5): stop the browser's
own submit, read and check the chosen method, send it. The method never becomes state, because
nothing renders it.

## 6. Custom hooks

A custom hook is a function, and readability holds for it as for a component. React adds these
rules (react.dev, "Reusing Logic with Custom Hooks"):

- *Advice.* **Start a hook's name with `use` and a capital letter (`useInvoiceFilters`), and give
  that name only to a function that calls a hook.** The convention lets a reader "always look at a
  component and know where its state, Effects, and other React features might 'hide'". A function
  that calls no hook is a plain function with a plain name: `getSorted`, not `useSorted`.
- *Advice.* **Write a hook for one concrete purpose and name it for that purpose, never a wrapper
  around the lifecycle** such as `useMount`, `useEffectOnce` or `useUpdateEffect`. react.dev:
  such hooks "don't fit well into the React paradigm", and a missing dependency inside one goes
  unreported, because "the linter only checks direct `useEffect` calls". Do not extract every
  repeated line either: "Some duplication is fine."
- *Advice.* **Share logic through a hook, never state.** Two components that call the same hook
  get two separate copies of its state: "Custom Hooks let you share stateful logic but not state
  itself." State two components share is lifted (section 4) or lives where
  [architecture.md](../architecture/architecture.md) section 7 puts shared state.
- Whether a server read gets a hook of its own is
  [architecture.md](../architecture/architecture.md) section 8.
  `PayInvoiceForm` follows it.

A hook's file is named for the hook; the names are
[architecture.md](../architecture/architecture.md) sections 3 and 4.

## 7. The compiler and memoisation

- *Advice.* **Turn the React Compiler on for the whole application.** Version 1.0 has been stable
  since 2025-10-07 (read 2026-10-01). It memoises components and hooks at build time, which is the
  work `useMemo`, `useCallback` and `memo` did by hand. Meta reports that in the Quest Store
  "initial loads and cross-page navigations improve by up to 12%" and "certain interactions are
  more than 2.5× faster": the vendor's own numbers, with the method only in a linked talk. On Vite,
  the compiler runs through the React plugin's preset, as in the reference application's
  `vite.config.ts` below.
- *Advice.* **Write no new `useMemo`, `useCallback` or `memo`.** react.dev: "For new code, we
  recommend relying on the compiler for memoization and using `useMemo`/`useCallback` where needed
  to achieve precise control." Two cases keep them as an escape hatch, and the hook then carries a
  comment that says which one:
  - a memoised value an effect depends on, where a new value on each render would restart the
    effect (react.dev);
  - a function handed to code outside React that compares functions by identity, such as a chart
    library's click handler. One author who removed such a `useCallback` got stale data and kept
    the hook: an anecdote, not a measurement.
- *Advice.* **Leave the memoisation that existing code already has.** react.dev: removing it "can
  change compilation output"; remove it only with tests that cover the component. How old code
  meets a new rule is [refactoring.md](../../any-language/refactoring/refactoring.md) section 7.
- *Advice.* **Treat `"use no memo"` as temporary.** Put it at the top of the one function that
  needs it, with a comment that names the library or the bug that forces it and what would let it
  go. react.dev says to treat opt-outs as temporary and to use directives sparingly; one
  practitioner found that they otherwise become "permanent technical debt".
- *Advice.* **Know the libraries the compiler skips.** React's `incompatible-library` lint flags
  them, and the compiler "automatically skips over components using these incompatible APIs". The
  list, read 2026-10-01:

  | Library API | What to do |
  |---|---|
  | React Hook Form's `watch` | use `useWatch({ control, name })`; react.dev's lint page names it as the fix. A community thread (discussion #12524, no maintainer statement) reports three patterns that still break under the compiler: `watch()` read through `useFormContext`, `formState` read through context in child components, and `register` together with `reset()` or `useForm({values})` |
  | TanStack Table's `useReactTable` | the compiler skips the component that calls it; know that it runs unmemoised |
  | TanStack Virtual's `useVirtualizer` | flagged by Oxlint's `incompatible-library`: memoisation "by the compiler or by hand" makes the list stop "reflecting new data" (Oxc's docs). Add `"use no memo"` to the component that calls it, with its reason; the library's issue #1119 was open with no maintainer reply |
  | MobX's `observer` | "not yet detected by linter"; add `"use no memo"` with its reason |

- *Advice.* **Measure where speed matters; do not assume the compiler did its part.** It skips a
  component that breaks a Rule of React or uses syntax it does not support, and nothing at run time
  says so (section 2). Keep its lint rules on, and measure re-renders where a screen must be fast:
  [performance.md](../performance/performance.md) section 3.

Check: before you stage, read the diff for `useMemo`, `useCallback` and `memo(`; each one the diff
adds carries the comment that names its escape hatch.

The compiler on Vite, from the reference application's `vite.config.ts`, with the router plugin,
the styles plugin and the import alias cut:

```ts
import babel from "@rolldown/plugin-babel";
...
import react, { reactCompilerPreset } from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [
    ...
    react(),
    babel({ presets: [reactCompilerPreset()] }),
    ...
  ],
  ...
});
```

Why it is good: it is the setup react.dev's installation page gives for Vite with
`@vitejs/plugin-react` 6 or later, the preset run through the Babel plugin (read 2026-10-01). The
compiler then covers every component, so no file needs a directive to opt in. The whole file, and
the versions, are [layout-example.md](../architecture/layout-example.md) and
[libraries.md](../architecture/libraries.md) section 2.

```tsx
// Bad: a hand-written useCallback in new code under the compiler. The compiler
// memoises the handler by itself, so the hook only adds a dependency list to
// keep right.
const handleSubmit = useCallback(
  (event: SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();

    const method = paymentMethodSchema.parse(new FormData(event.currentTarget).get("method"));

    payment.mutate(method, { onSuccess: onPaid });
  },
  [payment, onPaid],
);
```

The GOOD is the plain function in section 5's GOOD: the same body, with no hook and no dependency
list. It is good because the compiler already gives it the stable identity the hook was for, and
there is one thing less to keep right.

## 8. Events and async work

- *Advice.* **Run what a user action causes in that action's handler**: the request, the
  navigation, the notice. react.dev allows side effects in event handlers, and section 5 shows the
  effect that tries to do it instead.
- *Advice.* **Take pending and error state from the mutation (`isPending`, `isError`) or from the
  transition or action (`isPending` from `useTransition`, the state of `useActionState`), never
  from a boolean you set yourself.** A hand-kept flag is a second copy of what the mutation already
  knows, the redundant state section 4 rules out; react.dev's `set-state-in-effect` page lists a
  hand-set loading flag among its wrong examples. A form that disables its submit button on the
  mutation's `isPending` is the practitioner pattern (bulletproof-react). How a mutation is built,
  and what it refreshes, is [architecture.md](../architecture/architecture.md) section 9 (server data) and
  section 11 (forms).
- *Advice.* **Inside a transition, wrap every state update that comes after an `await` in its own
  `startTransition`.** react.dev: awaited calls are part of the transition, "but currently require
  wrapping any `set` functions after the `await` in an additional `startTransition`", which it
  calls a known limitation (read 2026-10-01). Without the wrap, that update is not part of the
  transition. The transition's `isPending` stays true "until all Actions complete".
- *Advice.* **Let an error thrown inside a transition reach the nearest error boundary**, which
  react.dev names as the way to show it. A mutation's error stays in the mutation's state unless
  the mutation is set to throw; where errors are shown is
  [architecture.md](../architecture/architecture.md) section 12.

```tsx
// Bad: a second copy of the mutation's pending state, kept by hand. It repeats
// payment.isPending, and it is right only while every path that starts a
// payment sets it and every path that ends one clears it.
const payment = useMutation(payInvoiceMutationOptions(apiClient, invoiceId));
const [isPaying, setIsPaying] = useState(false);

function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
  event.preventDefault();

  const method = paymentMethodSchema.parse(new FormData(event.currentTarget).get("method"));

  setIsPaying(true);

  payment.mutate(method, { onSuccess: onPaid, onSettled: () => setIsPaying(false) });
}

...

<Button type="submit" disabled={isPaying}>
  {isPaying ? "Paying…" : "Pay invoice"}
</Button>
```

The GOOD reads the mutation's own state, `src/billing/pay-invoice/pay-invoice-form.tsx`, with the
lines between the handler and the button cut:

```tsx
  function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    const method = paymentMethodSchema.parse(new FormData(event.currentTarget).get("method"));

    payment.mutate(method, { onSuccess: onPaid });
  }

  ...

      <Button type="submit" disabled={payment.isPending}>
        {payment.isPending ? "Paying…" : "Pay invoice"}
      </Button>
```

Why it is good: there is one source for "a payment is on its way", the mutation, so the button
cannot disagree with it. The mutation stays pending until the invoices it refreshes have loaded
again, because its options return that promise ([architecture.md](../architecture/architecture.md) section 9),
and the button follows without a line of its own. A disabled button also stops a
second submit while the first is on its way.

## 9. Names and files

- *Rule of React.* **Start a component's name with a capital letter**: "React component names must
  start with a capital letter", because JSX reads `<section>` as an HTML tag and `<Profile />` as a
  component (react.dev). Name it for what it shows, in the business's words
  ([readability.md](../../any-language/readability/readability.md) section 7):
  `PayInvoiceForm`, `InvoiceStatusBadge`.
- *Taste.* **Export one component from a file, and name the file for it**: `pay-invoice-form.tsx`
  holds `PayInvoiceForm`. A component or a function that only this file uses stays in the file,
  not exported. No owner states this; it is the practice's choice, so a reader finds a component by
  its file name. The form of the names, and where the file sits, are
  [architecture.md](../architecture/architecture.md) sections 3 and 4.
- *Taste.* **Export by name, and use a default export only where an API needs one.** `lazy` needs
  the component "exported as the `default` export", and Next.js pages and React Router route modules
  are default exports (read 2026-10-01). Everywhere else a named export makes every file import the
  component under the same name, so a search finds every use; that reason is the practice's choice.
- *Advice.* **Export no plain function or hook from a file that exports a component**, so Fast
  Refresh can update the component in place while you work. Oxlint's `react/only-export-components`
  reports a file that mixes them ([libraries.md](../architecture/libraries.md) section 4 for its setting).
  The rule a component reads goes to its own role file, such as `invoice-status.rules.ts`.

The badge in [component-example.md](component-example.md) shows a file with one exported component.
The file that shows one exported component beside a rule in its own role file is in
[security-example.md](../security/security-example.md) section 3.

## 10. Common mistakes

Each row is one problem. "Reported by" names the lint rule that reported the problem in the
reference application's negative controls (Oxlint 1.85.0, read 2026-10-01), a rule that exists but
was not run as a control, or "review" when no linter catches it and a reviewer has to.

| Mistake | Fix | Kind | Reported by |
|---|---|---|---|
| a hook after an early return, or inside a condition or a loop | move it to the top, above every return (section 2) | Rule of React | `react-hooks(rules-of-hooks)` |
| the clock or a random number read during render | read it in the loader or the event handler, pass the value as a prop (section 2) | Rule of React | `react(purity)` |
| a prop, a piece of state or a module variable changed during render | build a new value, and pass new state to its setter (section 2) | Rule of React | the compiler's `immutability` lint; not run as a control |
| a component called as a function | render it with JSX (section 2) | Rule of React | review |
| a component name in lower case | a capital first letter (section 9) | Rule of React | review |
| a value copied into state and kept in step by an effect | compute it during render (section 4) | Advice | `react(set-state-in-effect)` |
| a component defined inside another | define it at the top level of the file (section 4) | Advice | review |
| a list keyed by index or by a random value | key by the item's id (section 4) | Advice | review |
| an effect that clears fields when an id changes | a `key` on the component (section 4) | Advice | review |
| work a click causes, run by an effect | run it in the event handler (section 5) | Advice | review |
| a silenced `exhaustive-deps` | change the code: move the value, or split the effect (section 5) | Advice | `react/exhaustive-deps` once the silencing comment is gone; not run as a control |
| an effect that starts something and returns no cleanup | return the cleanup (section 5) | Advice | review; Strict Mode shows it in development |
| server data fetched in an effect | the query cache ([architecture.md](../architecture/architecture.md) section 8) | Advice | review |
| a lifecycle wrapper hook such as `useMount` | a hook named for its purpose, or the effect itself (section 6) | Advice | review |
| boolean props for states that exclude each other | one prop with a union type (section 3) | Advice | review |
| one configuration prop per caller | let the caller pass the part: `children`, a render prop, compound components (section 3) | Advice | review |
| Context for data two layers down | props (section 3) | Advice | review |
| `forwardRef` or `<Context.Provider>` in new code | `ref` as a prop; `<Context value>` (section 3) | Advice | review |
| a new `useMemo`, `useCallback` or `memo` | delete it; the compiler memoises (section 7) | Advice | review |
| React Hook Form's `watch` under the compiler | `useWatch` (section 7) | Advice | the `incompatible-library` lint; not run as a control |
| a hand-kept loading or error flag | the mutation's or the transition's state (section 8) | Advice | review |
| a state update after `await` in a transition, not wrapped | wrap it in `startTransition` (section 8) | Advice | review |
| a click handler on a `div` | a native `<button>`: [accessibility.md](../design/accessibility.md) section 3 | owned there | `jsx-a11y(click-events-have-key-events)`, `jsx-a11y(no-static-element-interactions)` |
| an `img` without `alt` | [accessibility.md](../design/accessibility.md) section 3 | owned there | `jsx-a11y(alt-text)` |
| a copied kit component that draws a native control, such as a radio, from buttons with ARIA roles | check what it renders before you keep it: [accessibility.md](../design/accessibility.md) section 3 | Advice (Paul Hebert) | review |
| `dangerouslySetInnerHTML` | [security.md](../security/security.md) sections 3 and 4 | owned there | `react(no-danger)` |
| a `javascript:` URL in `href` | [security.md](../security/security.md) section 3 | owned there | `jsx-a11y(anchor-is-valid)`, `eslint(no-script-url)` |

## 11. Where the rules stop holding

- **Code no change touches.** It stays as it is until a change edits it
  ([refactoring.md](../../any-language/refactoring/refactoring.md) section 2). Existing
  memoisation stays even then (section 7).
- **A shape a library requires.** An error boundary is a class: react.dev says "there is
  currently no way to write an Error Boundary as a function component", so use
  `react-error-boundary` ([architecture.md](../architecture/architecture.md) section 12). A route
  component takes the router's shape.
- **A Server Component.** In a framework that renders on the server, a Server Component runs on the
  server and may `await` its data; state, effects and event handlers do not exist there. This file
  is written for client components. Which format an application uses is
  [architecture.md](../architecture/architecture.md) section 2.
- **A component the compiler skips** (section 7). The compiler adds no memoisation to it, and a
  hand-written `useMemo` is no fix for a library from the table in section 7: react.dev's
  `incompatible-library` page says those libraries break under memoisation, "manual or automatic".
  Measure before you add any ([performance.md](../performance/performance.md) section 3).
- **The labels.** The Rules of React hold everywhere React runs. A Taste rule is the team's to
  change ([README.md](README.md), "The points to adapt"); an Advice rule gives way only where the
  team can name what its case gains.

## 12. Review checklist

A review question per section. A break of a Rule of React (section 2 or 9) means the component is
not ready. Any other single red flag is something to raise with the author, not a demand to rewrite;
when a component or a hook the change wrote or edited shows two or more, it is not ready.

| Section | Ask | Red flag |
|---|---|---|
| 2. The Rules of React | Does it render the same output for the same props, state and context, with every hook above every return? | A hook after an early return or in a condition; the clock, a random number or a changed variable in render; a component called as a function |
| 3. Props | Do the props say what the component needs, and nothing it does not? | `React.FC` where the code base types props directly; booleans for states that exclude each other; a configuration prop per caller; Context for data a prop could carry |
| 4. State | Is every piece of state something that cannot be computed during render? | A value kept in step by an effect; a component defined inside another; an index key on a list that changes |
| 5. Effects | Does each effect keep an outside system in step, and does it clean up? | An effect that runs a click's work, copies state or fetches server data; a silenced `exhaustive-deps`; a subscription with no cleanup |
| 6. Custom hooks | Does the hook have one concrete purpose in its name? | `useMount` and other lifecycle wrappers; a `use` name on a function that calls no hook |
| 7. Compiler | Is every `useMemo`, `useCallback`, `memo` and `"use no memo"` in new code there for a named reason? | A new one without its comment; existing memoisation removed with no test |
| 8. Events and async | Does pending and error state come from the mutation or the transition? | A hand-kept loading flag; a `set` call after `await` in a transition, not wrapped |
| 9. Names and files | Does the file export one component, named for the file, with a capital first letter? | Two exported components in one file; a default export no API asks for; a function exported beside a component; a component name in lower case |

## 13. Sources

**The Rules of React and the linter**

1. react.dev, "Rules of React", https://react.dev/reference/rules: the three groups of rules.
2. react.dev, "Components and Hooks must be pure",
   https://react.dev/reference/rules/components-and-hooks-must-be-pure: the five purity rules, each
   with its reason; which side effects are allowed, and where; local mutation.
3. react.dev, "React calls Components and Hooks",
   https://react.dev/reference/rules/react-calls-components-and-hooks: never call a component
   directly; never pass a hook around as a value.
4. react.dev, "Rules of Hooks", https://react.dev/reference/rules/rules-of-hooks: top level only,
   React functions only, and the places a hook may not be called.
5. react.dev, `use`, https://react.dev/reference/react/use: the one API allowed in conditions and
   loops; no promise created in render; no `try`/`catch`.
6. react.dev, the lint pages for `purity`, `set-state-in-effect` and `incompatible-library`,
   https://react.dev/reference/eslint-plugin-react-hooks/lints/purity and the pages beside it, read
   2026-10-01: what each rule flags, and what `set-state-in-effect` allows.
7. `eslint-plugin-react-hooks` README and CHANGELOG,
   https://github.com/facebook/react/tree/main/packages/eslint-plugin-react-hooks, read 2026-10-01
   (7.1.1): the `recommended` preset and the compiler rules it carries.
8. Oxc, "React Compiler support" in Oxlint, 2026-08-18,
   https://oxc.rs/blog/2026-08-18-react-compiler-support.html: Oxlint's compiler-backed rules,
   `purity` and `set-state-in-effect` among them.
9. facebook/react issues #34858 and #34743, https://github.com/facebook/react/issues/34858 and
   https://github.com/facebook/react/issues/34743: false positives of `set-state-in-effect`.
10. react.dev, "Your First Component", https://react.dev/learn/your-first-component, read
    2026-10-01: component names start with a capital letter; never nest component definitions.

**Props**

11. Matt Pocock, "You Can Stop Hating React.FC",
    https://www.totaltypescript.com/you-can-stop-hating-react-fc (2023): `React.FC` is fine since
    TypeScript 5.1; he still types props directly.
12. Matt Pocock, "ComponentProps: React's Most Useful Type Helper",
    https://www.totaltypescript.com/react-component-props-type-helper, read 2026-10-01:
    `ComponentProps` for native elements and for components you do not control;
    `ComponentPropsWithRef`.
13. react.dev, "Using TypeScript", https://react.dev/learn/typescript: props typed on plain
    functions, `ReactNode` for children, event types, union state.
14. react.dev blog, "React 19", 2024-12-05, https://react.dev/blog/2024/12/05/react-19: `ref` as a
    prop and the plan to remove `forwardRef`; `<Context>` as a provider.
15. Nadia Makarevich, "Advanced TypeScript for React developers: discriminated unions", 2021,
    https://www.developerway.com/posts/advanced-typescript-for-react-developers-discriminated-unions:
    unions instead of boolean props.
16. Kent C. Dodds, "Inversion of Control", 2019, https://kentcdodds.com/blog/inversion-of-control:
    configuration props against compound components; no abstraction before real callers.
17. Kent C. Dodds, "Prop Drilling", 2018, https://kentcdodds.com/blog/prop-drilling: props before
    Context.
18. react.dev, "Passing Data Deeply with Context",
    https://react.dev/learn/passing-data-deeply-with-context, read 2026-10-01: the steps before
    Context, and the cases it fits.
19. Josh Comeau, "Why React Re-Renders", updated 2025-12-03,
    https://www.joshwcomeau.com/react/why-react-re-renders/: context as invisible props.

**State**

20. react.dev, "Choosing the State Structure", https://react.dev/learn/choosing-the-state-structure:
    the five principles; no redundant state.
21. react.dev, "Sharing State Between Components",
    https://react.dev/learn/sharing-state-between-components: lift to the closest common parent; one
    owner.
22. react.dev, "Preserving and Resetting State",
    https://react.dev/learn/preserving-and-resetting-state: a `key` resets state; a nested
    definition resets it on every render.
23. react.dev, "Rendering Lists", https://react.dev/learn/rendering-lists: stable keys.
24. react.dev, "Updating Objects in State", https://react.dev/learn/updating-objects-in-state:
    replace, never change.
25. react.dev, "Extracting State Logic into a Reducer",
    https://react.dev/learn/extracting-state-logic-into-a-reducer: when a reducer pays; pure
    reducers.
26. react.dev, `useState`, https://react.dev/reference/react/useState: the initializer function, and
    Strict Mode calling it twice.
27. Kent C. Dodds, "Don't Sync State. Derive It!", 2019,
    https://kentcdodds.com/blog/dont-sync-state-derive-it, and TkDodo, "Don't over useState", 2020,
    https://tkdodo.eu/blog/dont-over-use-state: derive instead of syncing.
28. Kent C. Dodds, "Colocation", 2019, https://kentcdodds.com/blog/colocation: keep state where it
    is used.

**Effects and custom hooks**

29. react.dev, "You Might Not Need an Effect", https://react.dev/learn/you-might-not-need-an-effect:
    the cases and what to write instead; the effect fetch with an `ignore` flag.
30. react.dev, "Synchronizing with Effects", https://react.dev/learn/synchronizing-with-effects:
    what an effect is for; cleanup; Strict Mode's second setup.
31. react.dev, "Lifecycle of Reactive Effects",
    https://react.dev/learn/lifecycle-of-reactive-effects: always follow `exhaustive-deps`; one
    concern per effect.
32. react.dev, "Separating Events from Effects",
    https://react.dev/learn/separating-events-from-effects, and `useEffectEvent`,
    https://react.dev/reference/react/useEffectEvent: logic that reads the latest values without
    restarting the effect, and its limits.
33. react.dev blog, "React 19.2", 2025-10-01, https://react.dev/blog/2025/10/01/react-19-2:
    `useEffectEvent` ships.
34. react.dev, `useEffect`, https://react.dev/reference/react/useEffect: the costs of fetching in
    effects.
35. TanStack Query, "Suspense" guide,
    https://tanstack.com/query/latest/docs/framework/react/guides/suspense: retrying after a failed
    suspense query, and `useQueryErrorResetBoundary`.
36. react.dev, "Reusing Logic with Custom Hooks",
    https://react.dev/learn/reusing-logic-with-custom-hooks: hook names; logic, not state; no
    lifecycle wrappers.

**The compiler**

37. react.dev, "React Compiler" introduction, https://react.dev/learn/react-compiler/introduction:
    memoisation in new and in existing code; what the compiler skips.
38. react.dev blog, "React Compiler v1.0", 2025-10-07,
    https://react.dev/blog/2025/10/07/react-compiler-1: the stable release; Meta's numbers.
39. react.dev, compiler directives, https://react.dev/reference/react-compiler/directives: `"use
    memo"` and `"use no memo"`; opt-outs are temporary.
40. react.dev, compiler installation, https://react.dev/learn/react-compiler/installation, read
    2026-10-01: `reactCompilerPreset` on Vite.
41. Oxc, the `react/incompatible-library` rule,
    https://oxc.rs/docs/guide/usage/linter/rules/react/incompatible-library.html; TanStack Virtual
    issue #1119, https://github.com/TanStack/virtual/issues/1119; React Hook Form discussion
    #12524, https://github.com/orgs/react-hook-form/discussions/12524: libraries under the
    compiler; `useVirtualizer`; `useWatch`.
42. Sascha Becker, an 18-month retrospective on the React Compiler, 2026-04-22,
    https://saschb2b.com/blog/react-compiler-year-in-review: silent skips, opt-outs that stay (one
    practitioner).
43. LogRocket blog, on what broke when memoisation was removed, 2026-06-29,
    https://blog.logrocket.com/react-compiler-memoization-what-actually-broke/: a `useCallback` kept
    for a chart library (an anecdote).

**Events, async work, names and files**

44. react.dev, `useTransition`, https://react.dev/reference/react/useTransition: `startTransition`
    after `await`; pending state; errors to a boundary.
45. bulletproof-react, `create-discussion.tsx`,
    https://github.com/alan2207/bulletproof-react/blob/master/apps/react-vite/src/features/discussions/components/create-discussion.tsx:
    a form that disables its submit on the mutation's `isPending`.
46. react.dev, `lazy`, https://react.dev/reference/react/lazy; Next.js, `page`,
    https://nextjs.org/docs/app/api-reference/file-conventions/page; React Router, "Route Module",
    https://reactrouter.com/start/framework/route-module: where a default export is required.
47. `eslint-plugin-react-refresh` README,
    https://github.com/ArnaudBarre/eslint-plugin-react-refresh: `only-export-components` and Fast
    Refresh.
48. Paul Hebert, on the shadcn/ui radio button, 2026-01-20,
    https://paulmakeswebsites.com/writing/shadcn-radio-button/: a copied component that draws a
    radio from buttons with ARIA roles.
49. react.dev, `Component`, https://react.dev/reference/react/Component: no error boundary as a
    function component.
