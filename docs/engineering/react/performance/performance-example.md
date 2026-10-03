# Example: the performance setup of one application

A worked example for [performance.md](performance.md): the performance setup of the billing
screens of `Acme Corp`, a client-rendered application behind a login, built with Vite, TanStack
Router, TanStack Query and React Compiler. Each part is quoted as it stands in the reference
application, with the metric it serves and why it is good. Names are placeholders.

**Navigation**

- [The field-metrics reporter](#the-field-metrics-reporter)
- [The router: preload on intent](#the-router-preload-on-intent)
- [The loaders](#the-loaders)
- [The query client](#the-query-client)
- [Route-level splitting and the build output](#route-level-splitting-and-the-build-output)
- [The cache lines](#the-cache-lines)
- [Not in the reference application](#not-in-the-reference-application)

The reference application is not in this folder. The example files of the `react/` practices
quote its code, and the checks named here were run on it on 2026-10-01, 2026-10-02 and
2026-10-03.

What was verified, and what was not: the code was type-checked, linted, unit-tested and built.
Nothing was run in a browser, so no metric of this application was measured. The example shows
the setup, not a result: there is no LCP, INP or CLS value to report, and none is made up here.
The one number the build gives is the size of each chunk, shown below.

| Part | File | Serves |
|---|---|---|
| Field metrics to the application's own backend | `src/core/report-web-vitals.ts` | all three vitals, measured on real visits |
| Startup: the API client in the router context, and preload on intent | `src/main.tsx` | LCP of each route change |
| Loaders that start the request | `src/routes/invoices.index.tsx`, `src/routes/invoices.$invoiceId.pay.tsx` | LCP of the first screen and of each route change |
| A global `staleTime` | `src/core/query-client.ts` | LCP of a screen opened again; fewer requests |
| Route-level splitting and the compiler | `vite.config.ts` | LCP of the first screen through a smaller entry chunk; INP through fewer re-renders |
| Cache lines | `public/_headers` | LCP of a repeat visit; a deploy that reaches users at once |

## The field-metrics reporter

`src/core/report-web-vitals.ts`, quoted whole except `metricTarget`, the function at the end of
the file that reads the element from the metric's attribution. The reporter takes the API client
and calls its `report` method, which posts each report with `fetch`, `keepalive: true` and
`credentials: "omit"`; its reason is in the list below the code.

```ts
import type { CLSMetricWithAttribution, INPMetricWithAttribution, LCPMetricWithAttribution } from "web-vitals/attribution";
import { onCLS, onINP, onLCP } from "web-vitals/attribution";

import type { ApiClient } from "@/core/api-client.ts";

type CoreWebVital = CLSMetricWithAttribution | INPMetricWithAttribution | LCPMetricWithAttribution;

// This application sits behind a login, so it is in no public data set of field metrics.
// It measures its own visits and sends each value to its own backend (performance.md section 3).
export function reportWebVitals(apiClient: ApiClient): void {
  // A route change loads no page, so without this option only the first screen of a visit
  // would be measured (performance.md section 3).
  const options = { reportSoftNavs: true };

  function reportMetric(metric: CoreWebVital): void {
    apiClient.report("/web-vitals", {
      name: metric.name,
      value: metric.value,
      rating: metric.rating,
      navigationType: metric.navigationType,
      // The element the value comes from, so a failing metric can be traced to a part of the
      // screen (performance.md section 3).
      target: metricTarget(metric),
      // The URL the metric belongs to, not the current one: the INP and CLS of a screen arrive
      // after the user has moved on (web-vitals; performance.md section 3). The path only: a
      // query string can hold what the user typed (security.md section 13).
      path: new URL(metric.navigationURL ?? window.location.href).pathname,
      // The backend groups visits into device classes by this width (performance.md section 3).
      viewportWidthPx: window.innerWidth,
    });
  }

  onLCP(reportMetric, options);
  onINP(reportMetric, options);
  onCLS(reportMetric, options);
}
```

Why it is good:

- **It is the only field data this application can have** (performance.md section 3). CrUX
  holds public pages only, so without this file nobody would know how fast the screens are for
  the people who use them (performance.md section 2).
- **Soft navigations are on**, so each route change is measured as a navigation of its own, and
  the comment says what goes wrong without the option. It works in Chromium 151 and newer with
  `web-vitals` 6; other browsers report the first screen only (read 2026-10-01).
- **It loads the attribution build and sends the path with each value**, so the backend can read
  each metric at the 75th percentile per route. The path comes from the URL the metric belongs
  to, `metric.navigationURL`, so a value that arrives after a route change lands on the right
  route. The body carries `target`, the element the value comes from (performance.md section 3,
  attribution), and `viewportWidthPx`, which the backend uses to group visits into device
  classes. The full attribution object is not sent: when a metric
  fails and `target` is not enough, the fields that split it into parts are added in
  `reportMetric`, one place (performance.md section 4).
- **The report goes out as a `fetch` with `keepalive: true` and `credentials: "omit"`**
  (the `report` method of the API client). `keepalive` lets the request outlive the page, so the
  final values of a visit, known only when the page closes, still arrive. No cookie is sent, so
  the endpoint takes anonymous reports and needs neither the session nor the API client's custom
  header.
- **The client comes in as a parameter.** `reportWebVitals(apiClient: ApiClient)` reads no
  setting; the startup file reads the settings once, builds the client and passes it in
  ([readability.md](../../any-language/readability/readability.md) section 6).
- **One job per function**: `reportWebVitals` registers the three metrics, and the
  `reportMetric` function inside it builds the report of one value and hands it to the client's
  `report` method ([readability.md](../../any-language/readability/readability.md) section 2).
  The option carries its reason at the line (section 4 there). `keepalive` and
  `credentials: "omit"` carry theirs at their own lines in `ApiClient.report`, which
  [security-example.md](../security/security-example.md) section 5 quotes.
- **It leaves out the time from an interaction to its network result**, which performance.md
  section 3 asks for when an interaction waits for the network. The application's one such
  interaction is the payment, and timing it needs a mark at the submit and one when the mutation
  ends, which this file does not show. The cost: a slow payment request shows in no field metric.
  INP ends at the next paint, when the button already reads "Paying…", while the user still waits
  for the payment.

## The router: preload on intent

`src/main.tsx`. The imports, the router's type registration and the render call are cut; the
render call passes the error reporter, `reportError`, to `createRoot` as `onCaughtError` and
`onUncaughtError`, and the report holds the error's name and the path, never its message. The
router's error screen, `ScreenError`, is in `src/routes/-screen-error.tsx`: it imports the router,
so it sits with the routes, and the `-` prefix keeps it out of the route tree. The
`vite:preloadError` listener of performance.md section 5 is in this file, after the router.

```tsx
// Settings are read here, once, and handed on as values: nothing below this file reads them
// (architecture.md section 8).
const apiClient = new ApiClient(config.apiBaseUrl);
const queryClient = createQueryClient();
const reportError = createErrorReporter(apiClient);

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

// A deploy removed the chunks this open tab still points to. A reload fetches the new
// index.html, which points to the new chunks (Vite, "Load error handling"; performance.md
// section 5).
window.addEventListener("vite:preloadError", () => {
  window.location.reload();
});

...

reportWebVitals(apiClient);
```

Why it is good:

- **`defaultPreload: "intent"` serves the LCP of each route change.** The target's loader runs on
  hover or focus, so its request is often done by the time of the click (performance.md section 5,
  prefetch on intent). How much it saves for these screens was not measured.
- **One cache decides what is fresh.** With `defaultPreloadStaleTime: 0` the router always calls
  the loader and the query cache answers from its own `staleTime`, so a screen's data has one
  lifetime, not two.
- **The API client, the query client and the router are built once, at startup.** The API client
  goes into the router context next to the query client, so a loader and a route component read it
  from there and no module imports the settings. The reporter starts in the same file, with the
  API client, so every visit is measured from its first screen.
- **The `vite:preloadError` listener reloads the page** when a tab opened before a deploy asks for
  a chunk the host has deleted, so the user gets the new build and not a broken screen
  ([performance.md](performance.md) section 5).

## The loaders

`src/routes/invoices.index.tsx` and `src/routes/invoices.$invoiceId.pay.tsx`, the route
definitions only. The imports, the screen components and the list route's `toIsoDate` are cut.

```tsx
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
```

```tsx
export const Route = createFileRoute("/invoices/$invoiceId/pay")({
  loader: ({ context, params }) =>
    context.queryClient.query(invoiceQueryOptions(context.apiClient, params.invoiceId)),
  staticData: { title: "Pay invoice" },
  component: PayInvoiceScreen,
});
```

Why it is good:

- **The request starts when the URL matches, not when a component renders.** The router's code
  splitting keeps the loader in the main chunk, so the request and the download of the screen's
  chunk run side by side: one round trip less before the screen's LCP (performance.md section 5,
  data). The same route with the request moved out of the loader is in performance.md section 9.
- **The loaders use `queryClient.query()`**, the method TanStack Query's prefetching guide names
  now that `prefetchQuery` and `ensureQueryData` are deprecated (read 2026-10-01).
- **The components read the same cache.** The screen reads `apiClient` with
  `Route.useRouteContext()` and gives it to `InvoiceList`, which calls `useSuspenseQuery` with the
  same query options, finds the data the loader fetched, and starts no second request.

## The query client

`src/core/query-client.ts`

```ts
import { QueryClient } from "@tanstack/react-query";

// A screen opened again within a minute reads the cache instead of asking the server
// (architecture.md section 8).
const STALE_TIME_MS = 60_000;

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: { staleTime: STALE_TIME_MS } },
  });
}
```

Why it is good:

- **It replaces TanStack Query's default `staleTime` of 0**, which marks every result stale at
  once and asks the server again on each mount, window focus and reconnect (performance.md
  section 5). A screen opened again within a minute renders from the cache, which serves the LCP
  of that route change.
- **The value has its reason at the line**, and the unit is in the name
  ([readability.md](../../any-language/readability/readability.md) sections 4 and 7). One minute
  is a product decision about how stale an invoice list may be; the practice does not set it.

## Route-level splitting and the build output

`vite.config.ts`

```ts
import babel from "@rolldown/plugin-babel";
import tailwindcss from "@tailwindcss/vite";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import react, { reactCompilerPreset } from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [
    // The router plugin runs before the React plugin: it writes the route tree and moves each
    // route's components into a chunk of their own; the loader stays in the main chunk
    // (performance.md section 5).
    tanstackRouter({
      target: "react",
      autoCodeSplitting: true,
      routesDirectory: "./src/routes",
      generatedRouteTree: "./src/route-tree.gen.ts",
      // A test sits beside the route file it tests: without this pattern the plugin warns on
      // every build that the test file exports no route (architecture.md section 3).
      routeFileIgnorePattern: "\\.test\\.tsx?$",
    }),
    react(),
    babel({ presets: [reactCompilerPreset()] }),
    tailwindcss(),
  ],
  resolve: {
    // Reads the `@/*` alias from tsconfig, so the alias is declared in one place
    // (architecture.md section 5).
    tsconfigPaths: true,
  },
});
```

The production build of the reference application printed these files (Vite 8.3.0):

```text
dist/index.html                                    0.53 kB │ gzip:  0.30 kB
dist/assets/index-CmulJnWv.css                     9.30 kB │ gzip:  2.78 kB
dist/assets/rolldown-runtime-CbXtAM7H.js           0.58 kB │ gzip:  0.36 kB
dist/assets/invoices.index-m_HDp9I8.js             3.66 kB │ gzip:  1.47 kB
dist/assets/money.format-CUDBypya.js               8.07 kB │ gzip:  3.00 kB
dist/assets/invoices._invoiceId.pay-B_GXieUv.js   34.05 kB │ gzip: 13.51 kB
dist/assets/preload-helper-C1JRZSNY.js           123.77 kB │ gzip: 37.88 kB
dist/assets/index-jrUD5Y6A.js                    301.45 kB │ gzip: 96.88 kB
```

The built `index.html` asks for the entry chunk and preloads two shared chunks:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script type="module" crossorigin src="/assets/index-jrUD5Y6A.js"></script>
    <link rel="modulepreload" crossorigin href="/assets/rolldown-runtime-CbXtAM7H.js">
    <link rel="modulepreload" crossorigin href="/assets/preload-helper-C1JRZSNY.js">
    <link rel="stylesheet" crossorigin href="/assets/index-CmulJnWv.css">
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

Why it is good:

- **One chunk per route.** The invoice list and the payment screen each have their own file, so
  a visit to the list does not download the payment form (performance.md section 5, code
  splitting). This serves the LCP of the first screen, which waits for the entry chunk to run.
- **A dependency of one route stays in that route's chunk.** Only the payment screen imports the
  HTML sanitiser, through its form, and its chunk is the larger one: 34.05 kB against 3.66 kB.
  The build output lists sizes, not contents; a bundle analyser (performance.md section 3) is how
  to confirm what each chunk holds.
- **The first screen's JavaScript is small.** The entry and the two chunks `index.html` preloads
  come to 96.88 + 0.36 + 37.88 = 135.12 kB after gzip. The first screen, `/invoices`, also loads
  its route chunk and `money.format`: 135.12 + 1.47 + 3.00 = 139.59 kB. The budget of
  performance.md section 3 counts compressed bytes, by the practice's reading of Russell's model,
  so this is the figure to compare: 0.62 MiB, about 650 kB, is the budget for a page that is
  mostly JavaScript, and this application is well under it. That is a size from the build, not a
  measured LCP. The uncompressed sizes in the first column are not comparable. The reference
  application has no CI job, so it has no size gate, and the CI job of performance.md section 3
  is not shown. The cost: a build that grows past the budget passes unnoticed.
- **The compiler is on**, which the memoisation rule of
  [components.md](../components/components.md) section 7 relies on (performance.md section 6). The comment
  keeps the order of the plugins, which a reader might otherwise change.
- **Vite writes the `modulepreload` links itself** (performance.md section 5, resource hints), so
  no hint is written by hand.

## The cache lines

`public/_headers`, the file the static host reads. The security headers under `/*` are cut; they
are [security.md](../security/security.md) section 5's.

```text
...

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/index.html
  # no-cache, not no-store: this HTML holds no personal data, and no-store keeps the page out
  # of the back/forward cache (performance.md section 5).
  Cache-Control: no-cache
```

Why it is good:

- **Built assets are cached for a year.** Vite puts a hash of the content in every asset name
  (`index-jrUD5Y6A.js`), so a new build changes the name and a returning user downloads only what
  changed. This serves the LCP of a repeat visit (performance.md section 5, caching).
- **`index.html` is revalidated on every visit**, so a deploy reaches users at once and a new
  page load never points to chunks the host has deleted; the Vite guide recommends `no-cache` on
  HTML for that reason. A tab opened before the deploy is the `vite:preloadError` case.
- **`no-cache`, not `no-store`**: a page sent with `no-store` is kept out of the back/forward
  cache (performance.md section 5), and the comment says so at the line.

Check on the host, since nothing here was run against one: a deep link such as `/invoices` is
answered with `index.html` by the host's fallback, and a host may match a header rule on the path
asked for, not the file it serves. Before the first release, run
`curl -I https://app.example.com/invoices` and confirm the response carries `no-cache`.

## Not in the reference application

The screens hold no image, and the stylesheet declares no web font, so the LCP element of both
screens is text and the image and font rules of performance.md section 5 have nothing to act on.
A screen that adds an image follows the pairs in performance.md section 9. A screen that adds a
web font preloads the one font its first screen draws, in `index.html`. This block is written
from web.dev's guidance and was not built or run:

```html
<!-- The one font the first screen draws. Without `crossorigin` the browser fetches it a
     second time (web.dev; performance.md section 5). -->
<link rel="preload" href="/fonts/brand-sans.woff2" as="font" type="font/woff2" crossorigin>
```

Two more parts of the practice are not here: the size gate in CI (performance.md section 3), and
the server-rendered case and SEO. The server-rendered case (performance.md section 7) does not
apply because the application renders in the browser only, and SEO (performance.md section 8)
because its screens sit behind a login with nothing a crawler must read.

The time from an interaction to its network result is not reported either; the last point under
the field-metrics reporter says why, and what that costs.
