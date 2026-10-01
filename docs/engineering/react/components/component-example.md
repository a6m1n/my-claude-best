# Example: one module, written to every rule

A worked example for [components.md](components.md). The billing screens of Acme Corp list the
invoices with their status, and let a user pay one. The parts below come from the modules
`billing/list-invoices` and `billing/pay-invoice`: a pure rule, its type and its test, a badge, a list that
takes its pay link as a prop, the route that hands the list the date and the link, and a form that
reads the invoice with a suspense query and pays it with a mutation. Each part says which rules it
follows and why it is good. Names are invented.

The code is quoted verbatim from a reference application on React 19.3, React Compiler 1.0,
TypeScript 6.0, Vite 8, TanStack Router 1 and TanStack Query 5 (versions read 2026-10-01). It was
type-checked, linted with Oxlint and ESLint, unit-tested and built; nothing was run in a browser.
The application is not in this folder: the example files of the `react/` practices quote its code,
and the checks named were run on it on 2026-10-01 and 2026-10-02.
The whole tree and the configuration files are
[layout-example.md](../architecture/layout-example.md); the accessibility of the markup is
[accessibility.md](../design/accessibility.md) section 3.

Not shown: `invoices.queries.ts` and `invoice.queries.ts` hold one `queryOptions` each, and
`pay-invoice.mutations.ts` holds the payment's `mutationOptions`, which refreshes every invoice
read when a payment succeeds. `payment.schema.ts` holds the Zod schemas of the payment method and
the receipt. In `core/`, `invoice.schema.ts` holds the `Invoice` type both modules read (`id`,
`customerName`, `customerUrl` or `null`, `amountCents`, `dueOn`, `paidOn` or `null`, `noteHtml` or
`null`), `money.format.ts` holds `formatCents`, and `ui/` holds `Button` (shown in
[components.md](components.md) section 3), `ExternalLink` (shown in
[components.md](components.md) section 9) and `SanitizedHtml`. How those files are written is
[architecture.md](../architecture/architecture.md) section 8 (server data), and
[security.md](../security/security.md) section 4 (sanitising HTML).

## The rule

`src/billing/list-invoices/invoice-status.rules.ts`

```ts
import type { InvoiceStatus } from "@/billing/list-invoices/invoice-status.schema.ts";
import type { Invoice } from "@/core/invoice.schema.ts";

// ISO dates (YYYY-MM-DD) sort as text in calendar order, so the rule compares the strings.
export function invoiceStatus(invoice: Invoice, today: string): InvoiceStatus {
  if (invoice.paidOn !== null) {
    return "paid";
  }

  if (invoice.dueOn < today) {
    return "overdue";
  }

  return "due";
}
```

Why it is good:

- **The business decision lives outside every component**
  ([readability.md](../../any-language/readability/readability.md) section 2). It is plain
  TypeScript with no React in it, so the list, the badge and a test all get the same answer from
  one function ([components.md](components.md) section 1).
- **`today` comes in like the invoice**
  ([readability.md](../../any-language/readability/readability.md) section 6). The rule never reads
  the clock, so its answer depends on its two arguments alone, and no component that calls it
  reads the clock during render ([components.md](components.md) section 2).
- **The answer is a union, `InvoiceStatus`** (next section), which the badge's props reuse
  ([components.md](components.md) section 3): three states that exclude each other, one value.
- **The comment gives the reason for the string comparison**
  ([readability.md](../../any-language/readability/readability.md) section 4), the line a reader
  would otherwise "fix" by parsing both dates.
- **Two guards, then the main path**, each stage split by a blank line
  ([readability.md](../../any-language/readability/readability.md) sections 3 and 5). The import
  is absolute ([file-structure.md](../../any-language/file-structure/file-structure.md) section 7).

## The type

`src/billing/list-invoices/invoice-status.schema.ts`

```ts
export type InvoiceStatus = "paid" | "overdue" | "due";
```

The type sits in its own file because a data model and the logic that uses it never share a file
([file-structure.md](../../any-language/file-structure/file-structure.md) section 3). The rule
above and the badge below both import it from here.

## The test

`src/billing/list-invoices/invoice-status.rules.test.ts`

```ts
import { describe, expect, it } from "vitest";

import { invoiceStatus } from "@/billing/list-invoices/invoice-status.rules.ts";
import type { Invoice } from "@/core/invoice.schema.ts";

const unpaidInvoice: Invoice = {
  id: "inv-1",
  customerName: "Acme Corp",
  customerUrl: null,
  amountCents: 12_000,
  dueOn: "2026-10-01",
  paidOn: null,
  noteHtml: null,
};

describe("invoiceStatus", () => {
  it("is due on the due date itself", () => {
    expect(invoiceStatus(unpaidInvoice, "2026-10-01")).toBe("due");
  });

  it("is overdue from the day after the due date", () => {
    expect(invoiceStatus(unpaidInvoice, "2026-10-02")).toBe("overdue");
  });

  it("stays paid after the due date has passed", () => {
    const paidInvoice: Invoice = { ...unpaidInvoice, paidOn: "2026-09-30" };

    expect(invoiceStatus(paidInvoice, "2026-10-02")).toBe("paid");
  });
});
```

Why it is good:

- **No render, no frozen clock, no mock.** The test passes plain values and checks the status that
  comes back. That is what keeping the rule out of the component buys
  ([readability.md](../../any-language/readability/readability.md) section 6).
- **The boundary is pinned on both sides.** The due date itself is "due" and the day after is
  "overdue", so a `<` turned into `<=` in the rule turns the first test red.
- **Each test's name says the behaviour it pins**
  ([readability.md](../../any-language/readability/readability.md) section 7), and the third test
  splits its setup from its check with a blank line (section 5 there).

The test sits beside the rule it tests; where a test file sits is
[architecture.md](../architecture/architecture.md) section 3 (the tree), and the test tools are
[libraries.md](../architecture/libraries.md) section 6. This reference application has no component test;
the rule carries the logic worth a unit test.

## The badge

`src/billing/list-invoices/invoice-status-badge.tsx`

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

Why it is good:

- **One prop typed with the rule's union, not a boolean per state**
  ([components.md](components.md) section 3). The `Record<InvoiceStatus, string>` maps make the
  type checker fail when a fourth status gets no label or colour.
- **One exported component, named for the file**; the two maps only it reads stay unexported
  ([components.md](components.md) section 9).
- **The comment says why the word stays**, so nobody replaces it with a coloured dot. Colour as a
  cue is [accessibility.md](../design/accessibility.md) section 9.

## The list

`src/billing/list-invoices/invoice-list.tsx`

```tsx
import { useSuspenseQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";

import { InvoiceStatusBadge } from "@/billing/list-invoices/invoice-status-badge.tsx";
import { invoiceStatus } from "@/billing/list-invoices/invoice-status.rules.ts";
import { invoicesQueryOptions } from "@/billing/list-invoices/invoices.queries.ts";
import type { ApiClient } from "@/core/api-client.ts";
import type { Invoice } from "@/core/invoice.schema.ts";
import { formatCents } from "@/core/money.format.ts";
import { ExternalLink } from "@/core/ui/external-link.tsx";

type InvoiceListProps = {
  // The route hands the client in, like `today`: the component reaches nothing by itself.
  apiClient: ApiClient;
  today: string;
  // The route supplies the link, so this module needs no router and no path of another module.
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
        {invoices.map((invoice) => (
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
              <InvoiceStatusBadge status={invoiceStatus(invoice, today)} />
            </td>
            <td>{invoice.paidOn === null ? renderPayLink(invoice) : null}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

Why it is good:

- **Pure render** ([components.md](components.md) section 2). The date comes in as `today`, and
  each row's status is computed during render from the rule, never stored in state or kept in step
  by an effect ([components.md](components.md) section 4).
- **The client comes in as a prop, `apiClient`**, like `today`: the component calls it, so it is an
  input in the signature ([readability.md](../../any-language/readability/readability.md) section
  6). Where the client is built and handed in is
  [architecture.md](../architecture/architecture.md) section 8.
- **The pay link is a render prop** ([components.md](components.md) section 3), with its reason at
  the line. The list decides where the link goes in a row; the route decides what the link is. The
  module imports no router and no other module, the direction
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 2 asks for.
- **No loading flag, no fetch in an effect.** `useSuspenseQuery` with the module's query options
  hands the component loaded data; the router shows the loading and the error screens
  ([architecture.md](../architecture/architecture.md) sections 8 and 12).
- **The hook comes first, then the guard** for an empty list
  ([components.md](components.md) section 2;
  [readability.md](../../any-language/readability/readability.md) section 3). The empty message
  says what will appear here, which [ux.md](../design/ux.md) section 6 asks of an empty state.
- **The customer's address is an input from outside, so `ExternalLink` shows it.** The customer
  gave the address, so it can be any text. `ExternalLink` makes a link only when its rule accepts
  the address, and a row with no address shows the name as plain text.
- **Each row is keyed by the invoice's id** ([components.md](components.md) section 4).
- **The table has a caption and header cells with `scope`**, so a screen reader names each cell;
  that markup is [accessibility.md](../design/accessibility.md) section 3.

## The route that hands the list its date and its link

`src/routes/invoices.index.tsx`

```tsx
import { createFileRoute, Link } from "@tanstack/react-router";

import { InvoiceList } from "@/billing/list-invoices/invoice-list.tsx";
import { invoicesQueryOptions } from "@/billing/list-invoices/invoices.queries.ts";
import { toIsoDate } from "@/core/iso-date.ts";

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
        renderPayLink={(invoice) => (
          <Link to="/invoices/$invoiceId/pay" params={{ invoiceId: invoice.id }} className="underline underline-offset-2">
            Pay<span className="sr-only"> the invoice of {invoice.customerName}</span>
          </Link>
        )}
      />
    </section>
  );
}
```

Why it is good:

- **The clock is read in the loader, once per visit**, and the date goes down as a prop
  ([components.md](components.md) section 2). The route is the adapter, so this is where
  [readability.md](../../any-language/readability/readability.md) section 6 puts the clock. The
  comment at the line keeps it there.
- **The route composes the screen.** It hands the module the router's `Link` through the render
  prop ([components.md](components.md) section 3), and the module stays free of the router.
  Routes and their loaders are [architecture.md](../architecture/architecture.md) sections 6, 8 and 10.
- **The file exports the route, not the screen.** `InvoicesScreen` is used only here, so it stays
  unexported; the shape of a route file is the router's ([components.md](components.md) section
  9).
- **The hidden text tells a screen reader which invoice each "Pay" link pays**; that pattern is
  [accessibility.md](../design/accessibility.md) section 3.

## The form

`src/billing/pay-invoice/pay-invoice-form.tsx`

```tsx
import { useMutation, useSuspenseQuery } from "@tanstack/react-query";
import type { SyntheticEvent } from "react";

import { invoiceQueryOptions } from "@/billing/pay-invoice/invoice.queries.ts";
import { payInvoiceMutationOptions } from "@/billing/pay-invoice/pay-invoice.mutations.ts";
import { paymentMethodSchema } from "@/billing/pay-invoice/payment.schema.ts";
import type { ApiClient } from "@/core/api-client.ts";
import { formatCents } from "@/core/money.format.ts";
import { Button } from "@/core/ui/button.tsx";
import { SanitizedHtml } from "@/core/ui/sanitized-html.tsx";

type PayInvoiceFormProps = {
  apiClient: ApiClient;
  invoiceId: string;
  onPaid: () => void;
};

export function PayInvoiceForm({ apiClient, invoiceId, onPaid }: PayInvoiceFormProps) {
  const { data: invoice } = useSuspenseQuery(invoiceQueryOptions(apiClient, invoiceId));
  const payment = useMutation(payInvoiceMutationOptions(apiClient, invoiceId));

  function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    const method = paymentMethodSchema.parse(new FormData(event.currentTarget).get("method"));

    payment.mutate(method, { onSuccess: onPaid });
  }

  if (invoice.paidOn !== null) {
    return <p>This invoice was paid on {invoice.paidOn}.</p>;
  }

  return (
    <form onSubmit={handleSubmit} className="flex max-w-md flex-col gap-4">
      <p>
        Amount due: <span className="font-medium tabular-nums">{formatCents(invoice.amountCents)}</span>
      </p>

      {invoice.noteHtml === null ? null : <SanitizedHtml html={invoice.noteHtml} />}

      <fieldset className="flex flex-col gap-2">
        <legend className="text-sm font-medium">Payment method</legend>
        <label className="flex items-center gap-2">
          <input type="radio" name="method" value="card" defaultChecked />
          Card
        </label>
        <label className="flex items-center gap-2">
          <input type="radio" name="method" value="bank_transfer" />
          Bank transfer
        </label>
      </fieldset>

      {/* The region is in the page before the error is: a screen reader announces text that
          appears inside an existing live region, and often misses a region that arrives with
          its text. */}
      <p role="alert" className="text-sm text-destructive">
        {payment.isError ? "We could not confirm the payment. Check the invoice list before you try again." : null}
      </p>

      <Button type="submit" disabled={payment.isPending}>
        {payment.isPending ? "Paying…" : "Pay invoice"}
      </Button>
    </form>
  );
}
```

Why it is good:

- **Both hooks run on every render, and the guard for a paid invoice comes after them**
  ([components.md](components.md) section 2). The guard reads `invoice.paidOn` directly; no
  `isPaid` state is kept in step with it ([components.md](components.md) section 4).
- **The submit does the work the submit causes** ([components.md](components.md) section 5): stop
  the browser's own submit, read and check the chosen method, send the payment. Three stages, split
  by blank lines ([readability.md](../../any-language/readability/readability.md) section 5). No
  effect sends the payment, and no `useCallback` wraps the handler
  ([components.md](components.md) section 7).
- **Pending and error state come from the mutation** ([components.md](components.md) section 8).
  The button is disabled while `payment.isPending`, so a second click cannot send a second payment,
  and the error text appears when `payment.isError` is true. No flag is kept by hand.
- **The component keeps no state of its own** ([components.md](components.md) section 4). The
  invoice is in the query cache, and the payment method stays in the radio buttons until the form
  is read on submit. How a form reads and checks its values is
  [architecture.md](../architecture/architecture.md) section 11.
- **What happens after a payment is the caller's choice.** `onPaid` is a prop, so the route decides
  where to go, and the module needs no router ([components.md](components.md) section 3).
- **HTML from outside reaches the page only through `SanitizedHtml`**; why, and how, is
  [security.md](../security/security.md) sections 3 and 4.
- **The live region is in the page before any error is**, and its comment says why, so nobody
  renders it only on error; that rule is [accessibility.md](../design/accessibility.md) section 7. The message says what happened, what it means and what to do next, which
  [ux.md](../design/ux.md) section 2 asks of a failed action.
