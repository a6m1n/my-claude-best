# Example: the performance setup of one application

A worked example for [performance.md](performance.md): the performance setup of the billing
screens of `Acme Corp`, a client-rendered application behind a login, built with Vite, TanStack
Router, TanStack Query and React Compiler. Each part is quoted as it stands in the reference
application, with the metric it serves and why it is good. Names are placeholders.

The reference application is not in this folder. The example files of the `react/` practices
quote its code, and the checks named here were run on it on 2026-10-01 and 2026-10-02.

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
the file that reads the element from the metric's attribution. `sendReport`, from
`src/core/send-report.ts`, posts each report with `fetch`, `keepalive: true` and
`credentials: "omit"`; its reason is in the list below the code.

```ts
import type { CLSMetricWithAttribution, INPMetricWithAttribution, LCPMetricWithAttribution } from "web-vitals/attribution";
import { onCLS, onINP, onLCP } from "web-vitals/attribution";

import { sendReport } from "@/core/send-report.ts";

type CoreWebVital = CLSMetricWithAttribution | INPMetricWithAttribution | LCPMetricWithAttribution;

// This application sits behind a login, so it is in no public data set of field metrics.
// It measures its own visits and sends each value to its own backend.
export function reportWebVitals(reportUrl: URL): void {
  // A route change loads no page, so without this option only the first screen of a visit
  // would be measured.
  const options = { reportSoftNavs: true };

  function reportMetric(metric: CoreWebVital): void {
    sendReport(reportUrl, {
      name: metric.name,
      value: metric.value,
      rating: metric.rating,
      navigationType: metric.navigationType,
      // The element the value comes from, so a failing metric can be traced to a part of the screen.
      target: metricTarget(metric),
      // The path only: a query string can hold what the user typed.
      path: window.location.pathname,
      // The backend groups visits into device classes by this width.
      viewportWidth: window.innerWidth,
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
  the people who use them (section 2).
- **Soft navigations are on**, so each route change is measured as a navigation of its own, and
  the comment says what goes wrong without the option. It works in Chromium 151 and newer with
  `web-vitals` 6; other browsers report the first screen only (read 2026-10-01).
- **It loads the attribution build and sends the path with each value**, so the backend can read
  each metric at the 75th percentile per route. The body carries `target`, the element the value
  comes from (performance.md section 3, attribution), and `viewportWidth`, which the backend uses
  to group visits into device classes. The full attribution object is not sent: when a metric
  fails and `target` is not enough, the fields that split it into parts are added in
  `reportMetric`, one place (section 4).
- **The report goes out as a `fetch` with `keepalive: true` and `credentials: "omit"`**
  (`send-report.ts`). `keepalive` lets the request outlive the page, so the final values of a
  visit, known only when the page closes, still arrive. No cookie is sent, so the endpoint takes
  anonymous reports and needs neither the session nor the API client's custom header.
- **The URL comes in as a parameter.** `reportWebVitals(reportUrl: URL)` reads no setting; the
  startup file reads the settings once and passes the URL in
  ([readability.md](../../any-language/readability/readability.md) section 6).
- **One job per function**: `reportWebVitals` registers the three metrics, and the
  `reportMetric` function inside it builds the report of one value and hands it to `sendReport`
  ([readability.md](../../any-language/readability/readability.md) section 2). The lines a
  reader might "simplify", the option, `keepalive` and `credentials: "omit"`, carry their reason
  at the line (section 4 there).

## The router: preload on intent

`src/main.tsx`. The imports, the router's type registration and the render call are cut; the
render call passes the error reporter, `reportError`, to `createRoot` as `onCaughtError` and
`onUncaughtError`, and the report holds the error's name and the path, never its message. The
router's error screen, `ScreenError`, is in `src/routes/-screen-error.tsx`: it imports the router,
so it sits with the routes, and the `-` prefix keeps it out of the route tree. The reference
application has no `vite:preloadError` listener; performance.md section 5 shows the one that
belongs in this file, next to the router.

```tsx
// Settings are read here, once, and handed on as values: nothing below this file reads them.
const apiClient = new ApiClient(config.apiBaseUrl);
const queryClient = createQueryClient();
const reportError = createErrorReporter(new URL("/client-errors", config.apiBaseUrl));

const router = createRouter({
  routeTree,
  context: { apiClient, queryClient },
  // Hovering or focusing a link starts its loader, so the data is on its way before the click.
  defaultPreload: "intent",
  // TanStack Query decides what is fresh; the router keeps no second copy of loader data.
  defaultPreloadStaleTime: 0,
  // Every route gets a loading state and an error state, so no screen can be blank.
  defaultPendingComponent: ScreenPending,
  defaultErrorComponent: ScreenError,
});

...

reportWebVitals(new URL("/web-vitals", config.apiBaseUrl));
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
  from there and no module imports the settings. The reporter starts in the same file, with its
  URL, so every visit is measured from its first screen.

## The loaders

`src/routes/invoices.index.tsx` and `src/routes/invoices.$invoiceId.pay.tsx`, the route
definitions only. The imports and the screen components are cut.

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
  data). Section 9 there shows the same route with the request moved out of the loader.
- **The loaders use `queryClient.query()`**, the method TanStack Query's prefetching guide names
  now that `prefetchQuery` and `ensureQueryData` are deprecated (read 2026-10-01).
- **The components read the same cache.** The screen reads `apiClient` with
  `Route.useRouteContext()` and gives it to `InvoiceList`, which calls `useSuspenseQuery` with the
  same query options, finds the data the loader fetched, and starts no second request.

## The query client

`src/core/query-client.ts`

```ts
import { QueryClient } from "@tanstack/react-query";

// A screen opened again within a minute reads the cache instead of asking the server.
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
    // The router plugin runs before the React plugin: it writes the route tree and splits each
    // route file into its own chunk.
    tanstackRouter({
      target: "react",
      autoCodeSplitting: true,
      routesDirectory: "./src/routes",
      generatedRouteTree: "./src/route-tree.gen.ts",
    }),
    react(),
    babel({ presets: [reactCompilerPreset()] }),
    tailwindcss(),
  ],
  resolve: {
    // Reads the `@/*` alias from tsconfig, so the alias is declared in one place.
    tsconfigPaths: true,
  },
});
```

The production build of the reference application printed these files (Vite 8.3.0):

```text
dist/index.html                                    0.53 kB │ gzip:  0.30 kB
dist/assets/index-n5Li4O4A.css                     8.83 kB │ gzip:  2.60 kB
dist/assets/rolldown-runtime-CbXtAM7H.js           0.58 kB │ gzip:  0.36 kB
dist/assets/invoices.index-B8_TIIWC.js             3.53 kB │ gzip:  1.43 kB
dist/assets/money.format-CUDBypya.js               8.07 kB │ gzip:  3.00 kB
dist/assets/invoices._invoiceId.pay-DMnWst0W.js   33.96 kB │ gzip: 13.49 kB
dist/assets/preload-helper-C1JRZSNY.js           123.77 kB │ gzip: 37.88 kB
dist/assets/index-BnXHXF34.js                    301.18 kB │ gzip: 96.77 kB
```

The built `index.html` asks for the entry chunk and preloads two shared chunks:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script type="module" crossorigin src="/assets/index-BnXHXF34.js"></script>
    <link rel="modulepreload" crossorigin href="/assets/rolldown-runtime-CbXtAM7H.js">
    <link rel="modulepreload" crossorigin href="/assets/preload-helper-C1JRZSNY.js">
    <link rel="stylesheet" crossorigin href="/assets/index-n5Li4O4A.css">
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
  HTML sanitiser, through its form, and its chunk is the larger one: 33.96 kB against 3.53 kB.
  The build output lists sizes, not contents; a bundle analyser (section 3) is how to confirm
  what each chunk holds.
- **The first screen's JavaScript is small.** The entry and the two chunks `index.html` preloads
  come to 135.01 kB after gzip. The budget of section 3 counts compressed bytes, so this is the
  figure to compare: 0.62 MiB, about 650 kB, is the budget for a page that is mostly JavaScript,
  and this application is well under it. The uncompressed sizes in the first column are not
  comparable. That is a size from the build, not a measured LCP. The reference application has no size gate, so the CI job of
  section 3 is not shown.
- **The compiler is on**, which the memoisation rule of
  [components.md](../components/components.md) section 7 relies on (performance.md section 6). The comment
  keeps the order of the plugins, which a reader might otherwise change.
- **Vite writes the `modulepreload` links itself** (section 5, resource hints), so no hint is
  written by hand.

## The cache lines

`public/_headers`, the file the static host reads. The security headers under `/*` are cut; they
are [security.md](../security/security.md) section 5's.

```text
...

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/index.html
  Cache-Control: no-cache
```

Why it is good:

- **Built assets are cached for a year.** Vite puts a hash of the content in every asset name
  (`index-BnXHXF34.js`), so a new build changes the name and a returning user downloads only what
  changed. This serves the LCP of a repeat visit (performance.md section 5, caching).
- **`index.html` is revalidated on every visit**, so a deploy reaches users at once and a new
  page load never points to chunks the host has deleted; the Vite guide recommends `no-cache` on
  HTML for that reason. A tab opened before the deploy is the `vite:preloadError` case.
- **`no-cache`, not `no-store`**: a page sent with `no-store` is kept out of the back/forward
  cache (section 5).

Check on the host, since nothing here was run against one: a deep link such as `/invoices` is
answered with `index.html` by the host's fallback, and a host may match a header rule on the path
asked for, not the file it serves. Before the first release, run
`curl -I https://app.example.com/invoices` and confirm the response carries `no-cache`.

## Not in the reference application

The screens hold no image, and the stylesheet declares no web font, so the LCP element of both
screens is text and section 5's image and font rules have nothing to act on. A screen that adds an
image follows the pairs in performance.md section 9. A screen that adds a web font preloads the
one font its first screen draws, in `index.html`. This block is written from web.dev's guidance
and was not built or run:

```html
<!-- The one font the first screen draws. Without `crossorigin` the browser fetches it a
     second time (web.dev). -->
<link rel="preload" href="/fonts/brand-sans.woff2" as="font" type="font/woff2" crossorigin>
```

Three more parts of the practice are not here: the `vite:preloadError` listener (section 5), the
size gate in CI (section 3), and sections 7 and 8, which do not apply to screens behind a login
with nothing a crawler must read.
