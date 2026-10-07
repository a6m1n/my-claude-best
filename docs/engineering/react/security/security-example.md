# Example: the security-relevant parts of one application

A worked example for [security.md](security.md). It shows the parts of the `Acme Corp` billing
application that carry a security rule: the API client, the public settings, the link, the one
HTML sink, the web-vitals report, the headers file, the lint rules and the package manager
settings. Each part says which threat it stops, what it does not stop, and why it is written the
way it is. Names are placeholders. The tree is the one
[architecture.md](../architecture/architecture.md) section 3 describes.

**Navigation**

- [1. The API client](#1-the-api-client)
- [2. The public settings](#2-the-public-settings)
- [3. The link](#3-the-link)
- [4. The one HTML sink](#4-the-one-html-sink)
- [5. The web-vitals report](#5-the-web-vitals-report)
- [6. The headers file](#6-the-headers-file)
- [7. The lint rules](#7-the-lint-rules)
- [8. The package manager settings](#8-the-package-manager-settings)
- [9. What the example leaves out](#9-what-the-example-leaves-out)

The code here is quoted from a reference application. The application is not in this folder: the
example files of the `react/` practices quote its code, and the checks named below were run on it
on 2026-10-01 and 2026-10-02.

What was verified, and what was not. The application in sections 1 to 7 of this file was
type-checked, linted, unit-tested and built with Vite 8.3. Nothing was run in a browser: the
web-vitals and error reports were checked by the type checker and the linters only. The
Content-Security-Policy in `public/_headers` was checked only against the built `index.html` (no
inline script, no inline style); no tool and no browser evaluated it. The npm and pnpm settings
in section 8 of this file come from the owners' docs and were not run; the application was
installed with npm 10.8.

```text
billing-app/
├── .env.example                  every setting name, with no real value
├── .gitignore                    keeps files with real settings out of git
├── .oxlintrc.json                the sink rules, turned on by name
├── public/
│   └── _headers                  the policy and the other headers, for a static host
└── src/
    ├── core/
    │   ├── api-client.ts         the one way to reach the API
    │   ├── config.ts             public settings only
    │   ├── invoice.schema.ts     marks the fields that carry outside HTML and an outside address
    │   ├── report-error.ts       an error report with the error's name and the path, no message
    │   └── report-web-vitals.ts  sends the path, never the query string
    ├── billing/
    │   ├── list-invoices/
    │   │   ├── external-link.tsx     a link for an address from outside, as text when the rule refuses it
    │   │   ├── invoice-list.tsx      the one caller of ExternalLink, for the customer's address
    │   │   └── link-url.rules.ts     the scheme allowlist for an address from outside
    │   └── pay-invoice/
    │       ├── pay-invoice-form.tsx  the one caller of SanitizedHtml
    │       └── sanitized-html.tsx    the one place HTML enters the page
    └── main.tsx                      builds the API client and the error reporter, reads the settings
```

The tree has no package manager settings file, although security.md section 10 asks for the
install-script block in the repository's own config file; section 8 of this file shows those
files. The reference application was installed on npm 10.8 with
`--ignore-scripts --before=2026-09-24` on the command line instead, because npm 10.8 has no
`min-release-age`, the install already needed `--before` on the command line, and
`--ignore-scripts` went on the same line. The cost: an install that forgets the flags runs every
install script.

The link, its rule and the HTML sink each sit in the one module that uses them, not in `core/`:
[file-structure.md](../../any-language/file-structure/file-structure.md) section 4 moves code to
`core/` only when a second module needs it. When a second module needs one of them,
file-structure.md section 6, move 3, decides where it goes. The sink then moves down to `core/ui/`
and is never copied: a copy would be a second place that sets `dangerouslySetInnerHTML`, and
security.md section 4 asks for one component and one lint suppression.

## 1. The API client

`src/core/api-client.ts`

```ts
import type { z } from "zod";

// Named, so an error report can tell a failed request from a bug in the application.
export class ApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiError";
  }
}

type ApiRequest<TSchema extends z.ZodType> = {
  schema: TSchema;
  method?: "GET" | "POST";
  body?: unknown;
  signal?: AbortSignal;
};

// The one way to reach the API: one client per external system (file-structure.md section 4).
// `src/main.tsx` builds one instance at startup and hands it on, so no module reads a setting
// to find the server.
export class ApiClient {
  readonly #baseUrl: string;

  constructor(baseUrl: string) {
    this.#baseUrl = baseUrl;
  }

  async request<TSchema extends z.ZodType>(path: string, request: ApiRequest<TSchema>): Promise<z.infer<TSchema>> {
    const response = await fetch(new URL(path, this.#baseUrl), {
      method: request.method ?? "GET",
      // The session is an HttpOnly cookie, so no token is read or stored in JavaScript
      // (security.md section 6).
      credentials: "include",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        // A custom header forces a CORS preflight, so another site cannot send this request from
        // a plain form. The server rejects a request without it (security.md section 7).
        "X-Requested-With": "billing-app",
      },
      body: request.body === undefined ? undefined : JSON.stringify(request.body),
      signal: request.signal,
    });

    if (!response.ok) {
      throw new ApiError(`${path} answered ${String(response.status)}`);
    }

    // Parsed, never cast: the returned type is checked against the data that arrived
    // (architecture.md section 8).
    return request.schema.parse(await response.json());
  }

  // Sends a small report about this visit, such as a web vital or an error, to the API's report
  // intake. No cookie and no custom header: the intake takes anonymous reports, so a forged one
  // gains nothing, and no answer is read (security.md section 7).
  report(path: string, report: Record<string, unknown>): void {
    void fetch(new URL(path, this.#baseUrl), {
      method: "POST",
      body: JSON.stringify(report),
      // The request outlives the page, so a report sent while the tab closes still arrives.
      keepalive: true,
      // No cookie: the intake takes anonymous reports, so a forged one gains nothing
      // (security.md section 7).
      credentials: "omit",
    }).catch(() => {
      // A report that fails is dropped: an error raised here would itself need a report.
    });
  }
}
```

Why it is good:

- **No token exists in JavaScript** ([security.md](security.md) section 6). The BFF sets an
  `HttpOnly` session cookie, and `credentials: "include"` lets the browser send it; nothing here
  reads, stores or forwards a token. It stops a script on the page from taking a token away. It
  does not stop that script from sending requests through the session: only preventing the
  injection does (security.md sections 3 to 5).
- **The browser's half of the CSRF defence** (security.md section 7). The custom header makes the
  browser send a preflight first, which the server allows only for the application's origin
  (`https://app.example.com`), so another site's form cannot send this request. The server's
  half, rejecting a request without the header, lives in the BFF and is not shown.
- **One client class for the API**
  ([file-structure.md](../../any-language/file-structure/file-structure.md) section 4). The cookie
  mode and the header are written once in `request`, so no screen can send a request that carries
  the session without them; `report` is the one call without either, for anonymous reports
  (section 5 of this file). `src/main.tsx` builds one `ApiClient` with the base URL and hands it
  on, so the class reads no setting
  ([readability.md](../../any-language/readability/readability.md) section 6).
- **The comments sit at the four lines a reader would likely delete**, `credentials` and the
  custom header in `request`, `keepalive` and `credentials: "omit"` in `report`, and say why
  ([readability.md](../../any-language/readability/readability.md) section 4). The failed
  response ends the method in a guard
  ([readability.md](../../any-language/readability/readability.md) section 3), and blank lines
  split the request, the check and the parsing
  ([readability.md](../../any-language/readability/readability.md) section 5).
- **A departure from [file-structure.md](../../any-language/file-structure/file-structure.md)
  sections 3 and 4:** `ApiError` and the `ApiRequest` type sit in the same file as the class,
  though a type that `core/` names and a class are different kinds of file. They exist only for
  this one client: `ApiError` is what its request throws, and `ApiRequest` is the shape of
  `request`'s argument. The cost: a second client class has no shared place for them, so they
  move to their own `core/` files first.

## 2. The public settings

`src/core/config.ts`

```ts
import { z } from "zod";

// Vite inlines every VITE_ value into the bundle, so this schema holds public settings only.
// A secret never goes here: anyone can read it in the browser (security.md section 9).
const publicEnvSchema = z.object({
  // An origin with no path: request paths start at the root, and `new URL("/invoices", base)`
  // would silently drop a path such as `/v1` from the base.
  VITE_API_BASE_URL: z.url().refine((value) => new URL(value).pathname === "/", {
    error: "VITE_API_BASE_URL is an origin, such as https://api.example.com, with no path",
  }),
});

const publicEnv = publicEnvSchema.parse(import.meta.env);

export const config = {
  apiBaseUrl: publicEnv.VITE_API_BASE_URL,
} as const;
```

`.gitignore`

```text
node_modules
dist
.env
.env.*
!.env.example
```

Why it is good:

- **The schema lists public names only, and its comment says why at the line where a reader
  would add a key** (security.md section 9). A secret has no place to land, and the one place
  that reads `import.meta.env` is this file. Only `src/main.tsx` reads these settings and passes
  the values on, as [architecture.md](../architecture/architecture.md) sections 3 and 8 and
  [readability.md](../../any-language/readability/readability.md) section 6 ask; an import rule
  in `eslint.config.js` fails the lint when any other file imports `core/config.ts`.
- **The schema refuses a base URL that has a path.** `new URL("/invoices", base)` drops a path such
  as `/v1` from the base, so the application would call the wrong address without an error; the
  refusal stops that at startup.
- **Files with real values stay out of git, and the example file stays in.** `.env` and `.env.*`
  are ignored, and `!.env.example` keeps the file that lists every name with no real value
  (`VITE_API_BASE_URL=https://api.example.com` in the reference application;
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 9).
- **No source maps are published.** The Vite config sets no `build.sourcemap`, and the default is
  off (read 2026-10-01); the build output in the verification lists no `.map` file.
- **What it does not stop:** someone adding a secret to the schema with a `VITE_` prefix. No tool
  reports it; the question in security.md section 9, asked before a variable is added, is the
  guard.

## 3. The link

The rule that decides which address may become a link, `src/billing/list-invoices/link-url.rules.ts`.

```ts
// React refuses `javascript:` URLs and nothing else. An allowlist also stops `data:` and any
// scheme added to browsers later (security.md section 3).
const ALLOWED_PROTOCOLS: ReadonlySet<string> = new Set(["https:", "mailto:"]);

export function hasAllowedProtocol(href: string): boolean {
  if (!URL.canParse(href)) {
    return false;
  }

  return ALLOWED_PROTOCOLS.has(new URL(href).protocol);
}
```

The component that uses it, `src/billing/list-invoices/external-link.tsx`.

```tsx
import type { ReactNode } from "react";

import { hasAllowedProtocol } from "@/billing/list-invoices/link-url.rules.ts";

type ExternalLinkProps = {
  href: string;
  children: ReactNode;
};

// For an address that came from outside the application. An address the rule refuses is shown
// as plain text, never as a link (security.md section 3).
export function ExternalLink({ href, children }: ExternalLinkProps) {
  if (!hasAllowedProtocol(href)) {
    return <span>{children}</span>;
  }

  return (
    // `noreferrer` keeps this page's address, which can name an invoice, from the linked site.
    // min-h-6: the 24 px floor of a target; pointer-coarse:min-h-11: 44 px on a touch screen
    // (ux.md section 8).
    <a
      href={href}
      rel="noreferrer"
      className="inline-flex min-h-6 items-center underline underline-offset-2 pointer-coarse:min-h-11"
    >
      {children}
    </a>
  );
}
```

Why it is good:

- **Only `https:` and `mailto:` become a link** (security.md section 3). The URL is parsed with
  `URL`, and anything else, an unparsable string included, renders as plain text. It stops a
  `data:` URL or a scheme nobody planned for, which React 19 lets through, and a `javascript:`
  URL in any React version.
- **The comment on the set says why an allowlist and not a check for `javascript:`**, so the next
  editor does not "simplify" it to the one scheme React already refuses. The rule sits in its own
  file, `link-url.rules.ts`, which has four unit tests in `link-url.rules.test.ts`; the component
  only draws the result.
- **The guards sit at the top of each function** (readability.md section 3), and
  `rel="noreferrer"` keeps the page's address from the linked site.
- **A screen uses it:** `src/billing/list-invoices/invoice-list.tsx` shows the customer's address
  (`customerUrl`, which the schema marks as an address from outside) through `ExternalLink`, and
  shows the customer's name alone when the address is `null`.
- **The link's `min-h-6` and `pointer-coarse:min-h-11` are the target floor of ux.md section 8**,
  the same as the Pay link's; a link in a table row is a target like any other.

## 4. The one HTML sink

The invoice schema marks the field that carries outside HTML. It marks the customer's address too,
which the link in section 3 of this file handles.

`src/core/invoice.schema.ts`

```ts
import { z } from "zod";

export const invoiceSchema = z.object({
  id: z.string(),
  customerName: z.string(),
  // An address the customer gave. It comes from outside, so only `ExternalLink` may link it
  // (security.md section 3).
  customerUrl: z.string().nullable(),
  amountCents: z.number().int().nonnegative(),
  dueOn: z.iso.date(),
  paidOn: z.iso.date().nullable(),
  // Rich text typed by the person who issued the invoice. It is HTML from outside the
  // application, so only `SanitizedHtml` may put it on the page (security.md section 4).
  noteHtml: z.string().nullable(),
});

export type Invoice = z.infer<typeof invoiceSchema>;
```

The one caller, a line of `src/billing/pay-invoice/pay-invoice-form.tsx`; the rest of the form is
cut.

```tsx
      {/* The note is HTML from outside: only SanitizedHtml may put it on the page (security.md section 4). */}
      {invoice.noteHtml === null ? null : <SanitizedHtml html={invoice.noteHtml} />}
```

`src/billing/pay-invoice/sanitized-html.tsx`

```tsx
import DOMPurify from "dompurify";

type SanitizedHtmlProps = {
  html: string;
};

// The one place in the application that writes HTML into the page. Every other component
// renders text, which React escapes (security.md section 4).
export function SanitizedHtml({ html }: SanitizedHtmlProps) {
  // Cleaned here, next to the sink, on every render: a string cleaned earlier can be changed
  // or joined with another one on its way to this line (security.md section 4).
  // RETURN_TRUSTED_TYPE: in a browser with Trusted Types the result is a TrustedHTML, so the
  // sink passes `require-trusted-types-for 'script'` (security.md section 4).
  const cleanHtml = DOMPurify.sanitize(html, { USE_PROFILES: { html: true }, RETURN_TRUSTED_TYPE: true });

  // oxlint-disable-next-line react/no-danger -- the one allowed sink; `cleanHtml` is sanitised on the line above
  return <div dangerouslySetInnerHTML={{ __html: cleanHtml }} />;
}
```

Why it is good:

- **One field, one caller, one sink** (security.md section 4). The schema's comment names the one
  field that holds outside HTML and the one component allowed to show it, and
  `grep -rn "react/no-danger" src/` prints one line in the reference application: the suppression
  above.
- **Sanitised at the sink, in the same render, with the HTML profile.** No cleaned string travels
  through the application where it could be changed or joined; the comment says so at the line.
- **The sink passes Trusted Types.** With `RETURN_TRUSTED_TYPE: true`, DOMPurify returns a
  `TrustedHTML` where the browser has Trusted Types, so the one sink passes the report-only check
  of section 6 of this file (security.md section 4, "Make the policy sanitise"), and the comment
  says so at the line. This was type-checked and not run in a browser.
- **The suppression names its rule and its reason**, in the form
  [static-checks.md](../../python/static-checks/static-checks.md) section 6 gives, so a reviewer
  sees why this one sink is allowed.
- **What it does not stop:** a DOMPurify bypass found after this was written. The library is
  updated with the routine updates (security.md section 4). Trusted Types runs in report-only
  mode in section 6 of this file: a violation shows in the browser console but is not blocked yet;
  security.md section 4 says when to enforce it.

## 5. The web-vitals report

The application reports about itself: the web vitals of a visit, and the errors React catches.
Both go through the `report` method of the API client, which sends no cookie and no custom header.
From `src/core/api-client.ts`, the `report` method alone; the rest of the class is cut, and
section 1 of this file quotes the whole file.

```ts
...

  // Sends a small report about this visit, such as a web vital or an error, to the API's report
  // intake. No cookie and no custom header: the intake takes anonymous reports, so a forged one
  // gains nothing, and no answer is read (security.md section 7).
  report(path: string, report: Record<string, unknown>): void {
    void fetch(new URL(path, this.#baseUrl), {
      method: "POST",
      body: JSON.stringify(report),
      // The request outlives the page, so a report sent while the tab closes still arrives.
      keepalive: true,
      // No cookie: the intake takes anonymous reports, so a forged one gains nothing
      // (security.md section 7).
      credentials: "omit",
    }).catch(() => {
      // A report that fails is dropped: an error raised here would itself need a report.
    });
  }
```

The web-vitals reporter, `src/core/report-web-vitals.ts`, the inner function `reportMetric` of
`reportWebVitals(apiClient)` and the three calls that follow it; the imports, the metric type, the
options and `metricTarget` are cut. `src/main.tsx` passes the API client in, so the function
reads no setting.

```ts
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

- **It sends the path of the URL the metric belongs to, never the query string** (security.md
  section 13), and its comment says why at the line a reader might change to send the full URL.
- **One client for the API, with two ways to call it**
  ([file-structure.md](../../any-language/file-structure/file-structure.md) section 4): `request`
  sends the session and the custom header, and `report` sends neither (security.md section 7).
  `credentials: "omit"` keeps the session out of a report, so the intake takes an anonymous report
  and a forged one gains nothing. `navigator.sendBeacon` is not used for the same reason: it sends
  the session cookie and cannot carry a custom header. `keepalive` gives the one thing the beacon
  gave, a report that still arrives while the tab closes. An endpoint that did read the session
  would need `request`.
- **The error report holds the error's name and the path, never its message.**
  `src/core/report-error.ts` builds the function that `src/main.tsx` passes to `createRoot` as
  `onCaughtError` and `onUncaughtError`, and sends it through the client's `report` method to
  `/client-errors` on the API's origin. A message can carry what the user typed or what the server
  answered.
- **It sends to the application's own backend,** so the policy's `connect-src` names the API's
  origin and nothing else. No third-party script collects the metrics.
- The reports were checked by the type checker and the linters only. What to measure and why is
  [performance.md](../performance/performance.md) section 3.

## 6. The headers file

`public/_headers`, read by Netlify and Cloudflare Pages from the published folder. Vite copies
`public/` into `dist/` as it is; the verification shows `_headers` in `dist/`.

```text
/*
  # No 'unsafe-inline' in script-src: the build puts no script into the page itself, so an
  # injected one stays blocked (security.md section 5).
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self' https://api.example.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'
  # Trusted Types in report-only mode: with no report endpoint, a violation shows only in the
  # browser console of whoever visits a deploy that serves this file; a live application adds a
  # report endpoint and enforces once the reports stop (security.md section 4).
  Content-Security-Policy-Report-Only: require-trusted-types-for 'script'
  Strict-Transport-Security: max-age=63072000; includeSubDomains
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Cross-Origin-Opener-Policy: same-origin

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/index.html
  # no-cache, not no-store: this HTML holds no personal data, and no-store keeps the page out
  # of the back/forward cache (performance.md section 5).
  Cache-Control: no-cache
```

The policy rests on what the build writes. The built `dist/index.html`, from the verification:

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

Why it is good, directive by directive (security.md section 5):

| Part | What it stops |
|---|---|
| `script-src 'self'` | an injected inline script or event handler, and a script from another origin; it works because the built page above has no inline script |
| `style-src 'self'` | a `<style>` element or `style` attribute an attacker injects; the build ships one stylesheet file and no inline style |
| `img-src 'self' data:` | images from other origins; `data:` is there for the small assets Vite inlines, and it never appears in `script-src` |
| `connect-src 'self' https://api.example.com` | an injected script sending data anywhere but the application and its API |
| `object-src 'none'` | plugin content |
| `base-uri 'self'` | an injected `<base>` tag that moves where relative URLs point |
| `form-action 'self'` | an injected form that posts what the user types to another site |
| `frame-ancestors 'none'` | another site framing the page to trick clicks; it works only as a header, which is why the policy is not in a `<meta>` tag |
| the other five headers | each row of the header table in security.md section 5 |

The two security comments in the file give their reason at the line:

- **No `'unsafe-inline'` in `script-src`.** It is the word a reader would most likely add when a
  script is blocked, so the comment above the policy says why it stays out (security.md
  section 5).
- **Trusted Types run in report-only mode now** (security.md section 4). A violation shows only
  in the browser console of whoever visits a deploy that serves this file, preview or production,
  because the header names no `report-to` endpoint; the team sees its own visits, on its preview
  deploys. A live application adds a report endpoint, the way the main policy's report-only phase
  below does, and enforces when the reports stop.
  DOMPurify returns a `TrustedHTML` where the browser has Trusted Types, so the one sink of
  section 4 of this file passes the report-only check (security.md section 4, "Make the policy
  sanitise"); this was type-checked and not run in a browser.

The two `Cache-Control` blocks serve caching, which [performance.md](../performance/performance.md)
section 5 owns, and the comment on `/index.html` gives its reason at the line.

What it leaves out, on purpose or for a later step:

- **The report-only phase.** A live application sends this policy as
  `Content-Security-Policy-Report-Only`, with a report endpoint, before it enforces it. The example
  shows the main policy in its enforced form; only the Trusted Types header is report-only.
- **Enforced Trusted Types.** They run in report-only mode now. A live application adds a report
  endpoint and enforces once its reports stop; until then a violation shows only in the console
  (security.md section 4).
- **`preload` in `Strict-Transport-Security`,** and the `X-Frame-Options`, CORP, COEP and
  `X-XSS-Protection` headers; the table in security.md section 5 says what each would add.

Limits: nothing was run in a browser, so no browser has enforced this policy against the running
page. After the first deploy, run it through CSP Evaluator and the site through MDN's HTTP
Observatory (security.md section 14). Vercel reads headers from `vercel.json`, not from this file.

## 7. The lint rules

`.oxlintrc.json`, the five security rule lines only. The rest of the file is cut; the whole file
is in [layout-example.md](../architecture/layout-example.md) section 3.

```json
{
  ...
  "rules": {
    ...
    "no-eval": "error",
    "no-implied-eval": "error",
    "no-new-func": "error",
    "no-script-url": "error",
    "react/no-danger": "error"
  },
  ...
}
```

The negative controls in the verification: control files that broke a rule were added, the linter
run, and the files removed. Two of them broke security rules; one line for each rule they broke:

```text
src/billing/list-invoices/control-react.tsx:21:13: error react(no-danger): Do not use `dangerouslySetInnerHTML` prop
src/billing/list-invoices/control-react.tsx:22:15: error eslint(no-script-url): Unexpected `javascript:` url
src/core/control-eslint-plugin.ts:2:24: error eslint(no-eval): eval can be harmful.
```

Why it is good:

- **The sink rules are named, as errors** (security.md section 14): `no-eval`, `no-implied-eval`,
  `no-new-func`, `no-script-url` and `react/no-danger`. A rule named in the config stays on
  whatever a preset does.
- **Three of them are shown to work:** `react/no-danger`, `no-script-url` and `no-eval` reported a
  control file. No control file tried `new Function` or a string passed to a timer, so
  `no-implied-eval` and `no-new-func` are configured but not shown reporting.
- **What they miss:** `no-script-url` sees a `javascript:` string written in the code, not a URL
  that arrives as data; the link component in section 3 of this file covers that case. Which
  linter and which version is [libraries.md](../architecture/libraries.md) section 4.

## 8. The package manager settings

The reference application was installed with
`npm install --ignore-scripts --before=2026-09-24` on npm 10.8: no dependency ran an install
script, and no version published after that date was taken, a week before the build. Type check,
lint, tests and build then passed, so the application needs no dependency build script. Two of
its dependencies carry one, `unrs-resolver`, which `eslint-import-resolver-typescript` pulls in,
and `fsevents` (optional, macOS), and the strict settings below fail the install on a script
nobody reviewed. So the two are denied, not allowed: `false` under `allowBuilds` for pnpm, and
for npm 12 a denial in `package.json`'s `allowScripts`, which `npm deny-scripts` writes. npm's
page gives no value format for that entry, so it is not shown here (pnpm's build settings page
and npm's v12 config page, read 2026-10-03).

The files below make the same controls part of the repository, one for each package manager:
`.npmrc` for npm 12, `.npmrc` for npm 11.10.0 or later, and `pnpm-workspace.yaml` for pnpm 11; a
repository takes the one it installs with, so every install obeys them (security.md section 10).
They are written from the owners' docs (npm's config page and changelog, CISA's axios alert,
pnpm's settings and supply-chain pages, read 2026-10-01) and were not run: the machine had npm
10.8.

`min-release-age` exists since npm 11.10.0 (2026-02-11) and `min-release-age-exclude` since
11.17.0; npm before 11.10.0 has neither. There `--before=<date>` on the install command installs
only versions that were available on or before that date (npm's config page, read 2026-10-02). It
takes a fixed date that the person running the install has to choose each time, where
`min-release-age` is a rolling window set once in the repository. The reference application was
installed with the flag (npm 10.8, `--before=2026-09-24`).

`.npmrc`, for npm 12:

```ini
# npm 12 blocks dependency install scripts with a warning; this makes the install fail instead
# (security.md section 10).
strict-allow-scripts=true
# The next two are npm 12's defaults, written out so the policy shows in review.
# Refuses git dependencies: a cooldown cannot see a commit (security.md section 10).
allow-git=none
# Refuses tarball URLs, which skip the registry and its checks (security.md section 10).
allow-remote=none
# A version is installed only once it is 7 days old (CISA's advice after the axios compromise).
# Emergency path, for a critical advisory only, approved by a second person in the pull request:
# list the patched package in min-release-age-exclude; remove it when the version is 7 days old
# (security.md section 10).
min-release-age=7
```

`.npmrc`, for npm 11.10.0 or later. npm 11 still runs dependency install scripts, so
`ignore-scripts=true` takes the place of `strict-allow-scripts`, and it allows git and tarball
sources, so the file turns them off. npm 11.10 to 11.16 has the cooldown but no per-package
exemption, so the emergency path works from 11.17.0 on.

```ini
# npm 11 runs dependency install scripts; this stops them (security.md section 10).
ignore-scripts=true
# Refuses git dependencies: a cooldown cannot see a commit (security.md section 10).
allow-git=none
# Refuses tarball URLs, which skip the registry and its checks (security.md section 10).
allow-remote=none
# A version is installed only once it is 7 days old (CISA's advice after the axios compromise).
# Emergency path, for a critical advisory only, approved by a second person in the pull request:
# list the patched package in min-release-age-exclude; remove it when the version is 7 days old
# (security.md section 10).
min-release-age=7
```

`allow-git` exists since npm 11.9.0. npm's 11.21.0 config page lists `allow-remote`, and the
version that added it to npm 11 was not established. An npm that does not know a setting prints a
warning and ignores it, so on an older npm 11 the `allow-remote` line has no effect.

`pnpm-workspace.yaml`, for pnpm 11 and later:

```yaml
# A version is installed only once it is 7 days old (CISA's advice after the axios compromise).
# Emergency path, for a critical advisory only, approved by a second person in the pull request:
# add the patched package to minimumReleaseAgeExclude; remove it when the version is 7 days old
# (security.md section 10).
minimumReleaseAge: 10080 # minutes
# The next two are pnpm defaults, written out so the policy shows in review.
# An unreviewed dependency build script fails the install (security.md section 10).
strictDepBuilds: true
# Only direct dependencies may come from git or a tarball URL (security.md section 10).
blockExoticSubdeps: true
# Fails when a version has weaker provenance than earlier ones (security.md section 10).
trustPolicy: no-downgrade
# Denied by name, so strictDepBuilds does not fail the install on them; the checks passed
# with every install script ignored (pnpm's build settings page; security.md section 10 for
# the review rule).
allowBuilds:
  unrs-resolver: false
  fsevents: false
```

Why it is good:

- **The controls live in the repository,** so a person, CI and an agent install under the same
  rules.
- **The emergency path is written next to the cooldown,** with who approves it and when the entry
  comes out; the React2Shell patch was blocked by a one-day cooldown that had no such line.
- **Each line says what it does,** so nobody deletes a default as noise. The defaults of npm 12
  (`allow-git`, `allow-remote`) and of pnpm 11 (`strictDepBuilds`, `blockExoticSubdeps`) are
  written out too, so the policy shows in review.
- **What they do not stop:** a payload that runs when the package is imported or bundled, and a
  version older than the cooldown. Provenance checks do not stop a package built from a hijacked
  CI with valid provenance (security.md section 10).

## 9. What the example leaves out

- **The BFF:** it sets the `__Host-Http-` session cookie, rejects a request without the custom
  header, checks CSRF and decides access. That is server code; security.md sections 6 and 7 list
  what it must do.
- **The CI workflow:** pinned actions, a read-only token, no fork code in `pull_request_target`
  (security.md section 10).
- **Server-side React:** the application renders in the browser only, so section 8 of security.md
  does not apply to it.
