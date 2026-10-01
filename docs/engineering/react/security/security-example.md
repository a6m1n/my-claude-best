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

What was verified, and what was not. The application in sections 1 to 7 was type-checked,
linted, unit-tested and built with Vite 8.3. Nothing was run in a browser: the
Content-Security-Policy in `public/_headers` and the web-vitals and error reports were checked by the
type checker and the linters only, so the policy has not been tested against a running page. The npm 12
and pnpm settings in section 8 come from the owners' docs and were not run; the application was
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
    │   ├── api-client.ts         the one way to reach the backend
    │   ├── config.ts             public settings only
    │   ├── invoice.schema.ts     marks the fields that carry outside HTML and an outside address
    │   ├── report-error.ts       an error report with the error's name and the path, no message
    │   ├── report-web-vitals.ts  sends the path, never the query string
    │   └── send-report.ts        sends a report with no cookie
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

// The one way to reach the backend. `src/main.tsx` builds one instance at startup and hands it
// on, so no module reads a setting to find the server.
export class ApiClient {
  readonly #baseUrl: string;

  constructor(baseUrl: string) {
    this.#baseUrl = baseUrl;
  }

  async request<TSchema extends z.ZodType>(path: string, request: ApiRequest<TSchema>): Promise<z.infer<TSchema>> {
    const response = await fetch(new URL(path, this.#baseUrl), {
      method: request.method ?? "GET",
      // The session is an HttpOnly cookie, so no token is read or stored in JavaScript.
      credentials: "include",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        // A custom header forces a CORS preflight, so another site cannot send this request from
        // a plain form. The server rejects a request without it.
        "X-Requested-With": "billing-app",
      },
      body: request.body === undefined ? undefined : JSON.stringify(request.body),
      signal: request.signal,
    });

    if (!response.ok) {
      throw new ApiError(`${path} answered ${String(response.status)}`);
    }

    // Parsed, never cast: the returned type is checked against the data that arrived.
    return request.schema.parse(await response.json());
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
  browser send a preflight first, which the server allows only for its own origin, so another
  site's form cannot send this request. The server's half, rejecting a request without the
  header, lives in the BFF and is not shown.
- **One client class for the one backend**
  ([file-structure.md](../../any-language/file-structure/file-structure.md) section 4). The cookie
  mode and the header are written once in `request`, so no screen can call the API without them.
  `src/main.tsx` builds one `ApiClient` with the base URL and hands it on, so the class reads no
  setting ([readability.md](../../any-language/readability/readability.md) section 6).
- **The comments sit at the two lines a reader would likely delete**, `credentials` and the
  custom header, and say why ([readability.md](../../any-language/readability/readability.md)
  section 4). The failed response ends the method in a guard (section 3), and blank lines split
  the request, the check and the parsing (section 5).

## 2. The public settings

`src/core/config.ts`

```ts
import { z } from "zod";

// Vite inlines every VITE_ value into the bundle, so this schema holds public settings only.
// A secret never goes here: anyone can read it in the browser.
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
// scheme added to browsers later.
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
// as plain text, never as a link.
export function ExternalLink({ href, children }: ExternalLinkProps) {
  if (!hasAllowedProtocol(href)) {
    return <span>{children}</span>;
  }

  return (
    // `noreferrer` keeps this page's address, which can name an invoice, from the linked site.
    <a href={href} rel="noreferrer" className="underline underline-offset-2">
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

## 4. The one HTML sink

The invoice schema marks the field that carries outside HTML. It marks the customer's address too,
which the link of section 3 handles.

`src/core/invoice.schema.ts`

```ts
import { z } from "zod";

export const invoiceSchema = z.object({
  id: z.string(),
  customerName: z.string(),
  // An address the customer gave. It comes from outside, so only `ExternalLink` may link it.
  customerUrl: z.string().nullable(),
  amountCents: z.number().int().nonnegative(),
  dueOn: z.iso.date(),
  paidOn: z.iso.date().nullable(),
  // Rich text typed by the person who issued the invoice. It is HTML from outside the
  // application, so only `SanitizedHtml` may put it on the page.
  noteHtml: z.string().nullable(),
});

export type Invoice = z.infer<typeof invoiceSchema>;
```

The one caller, a line of `src/billing/pay-invoice/pay-invoice-form.tsx`; the rest of the form is
cut.

```tsx
      {invoice.noteHtml === null ? null : <SanitizedHtml html={invoice.noteHtml} />}
```

`src/billing/pay-invoice/sanitized-html.tsx`

```tsx
import DOMPurify from "dompurify";

type SanitizedHtmlProps = {
  html: string;
};

// The one place in the application that writes HTML into the page. Every other component
// renders text, which React escapes.
export function SanitizedHtml({ html }: SanitizedHtmlProps) {
  // Cleaned here, next to the sink, on every render: a string cleaned earlier can be changed
  // or joined with another one on its way to this line.
  const cleanHtml = DOMPurify.sanitize(html, { USE_PROFILES: { html: true } });

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
- **The suppression names its rule and its reason**, in the form
  [static-checks.md](../../python/static-checks/static-checks.md) section 6 gives, so a reviewer
  sees why this one sink is allowed.
- **What it does not stop:** a DOMPurify bypass found after this was written. The library is
  updated with the routine updates (security.md section 4). Trusted Types is not yet in the
  policy of section 6; security.md section 4 says when to add it.

## 5. The web-vitals report

The application reports about itself: the web vitals of a visit, and the errors React catches.
Both go through one function that sends no cookie, `src/core/send-report.ts`, the whole file.

```ts
// Sends a small report about this visit to the application's own backend. It goes around
// `ApiClient` on purpose: a report carries no session and expects no answer.
export function sendReport(reportUrl: URL, report: Record<string, unknown>): void {
  void fetch(reportUrl, {
    method: "POST",
    body: JSON.stringify(report),
    // The request outlives the page, so a report sent while the tab closes still arrives.
    keepalive: true,
    // No cookie is sent: the endpoint takes anonymous reports, so a forged request gains nothing
    // and the endpoint needs neither the session nor the custom header.
    credentials: "omit",
  }).catch(() => {
    // A report that fails is dropped: an error raised here would itself need a report.
  });
}
```

The web-vitals reporter, `src/core/report-web-vitals.ts`, the inner function `reportMetric` of
`reportWebVitals(reportUrl)` and the three calls that follow it; the imports, the metric type, the
options and `metricTarget` are cut. `src/main.tsx` passes the URL in as `reportUrl`, so the
function reads no setting.

```ts
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
      viewportWidthPx: window.innerWidth,
    });
  }

  onLCP(reportMetric, options);
  onINP(reportMetric, options);
  onCLS(reportMetric, options);
}
```

Why it is good:

- **It sends the path, never the query string** (security.md section 13), and its comment says
  why at the line a reader might change to `location.href`.
- **It sends no cookie.** `credentials: "omit"` keeps the session out of a report, so the endpoint
  takes an anonymous report and a forged one gains nothing. That is why `sendReport` does not use
  `ApiClient` and its custom header (security.md section 7). `navigator.sendBeacon` is not used
  for the same reason: it sends the session cookie and cannot carry a custom header. `keepalive`
  gives the one thing the beacon gave, a report that still arrives while the tab closes. An
  endpoint that did read the session would need the API client.
- **The error report holds the error's name and the path, never its message.**
  `src/core/report-error.ts` builds the function that `src/main.tsx` passes to `createRoot` as
  `onCaughtError` and `onUncaughtError`, and sends it through `sendReport` to `/client-errors`
  on the API's origin. A message can carry what the user typed or what the server answered.
- **It sends to the application's own backend,** so the policy's `connect-src` names the API's
  origin and nothing else. No third-party script collects the metrics.
- Like the policy, the reports were checked by the type checker and the linters only. What to
  measure and why is [performance.md](../performance/performance.md) section 3.

## 6. The headers file

`public/_headers`, read by Netlify and Cloudflare Pages from the published folder. Vite copies
`public/` into `dist/` as it is; the verification shows `_headers` in `dist/`.

```text
/*
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self' https://api.example.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'
  Strict-Transport-Security: max-age=63072000; includeSubDomains
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Cross-Origin-Opener-Policy: same-origin

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/index.html
  Cache-Control: no-cache
```

The policy rests on what the build writes. The built `dist/index.html`, from the verification:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script type="module" crossorigin src="/assets/index-XsSBP8Id.js"></script>
    <link rel="modulepreload" crossorigin href="/assets/rolldown-runtime-CbXtAM7H.js">
    <link rel="modulepreload" crossorigin href="/assets/preload-helper-C1JRZSNY.js">
    <link rel="stylesheet" crossorigin href="/assets/index-n5Li4O4A.css">
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

The two `Cache-Control` blocks serve caching, which [performance.md](../performance/performance.md)
section 5 owns.

What it leaves out, on purpose or for a later step:

- **The report-only phase.** A live application sends this policy as
  `Content-Security-Policy-Report-Only`, with a report endpoint, before it enforces it. The example
  shows the enforced form.
- **Trusted Types.** It is added in report-only mode once the policy's reports are quiet
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

The negative controls in the verification: a file that broke each rule was added, the linter run,
and the file removed. The two security lines of that run:

```text
src/billing/list-invoices/control-react.tsx:21:13: error react(no-danger): Do not use `dangerouslySetInnerHTML` prop
src/billing/list-invoices/control-react.tsx:22:15: error eslint(no-script-url): Unexpected `javascript:` url
```

Why it is good:

- **The sink rules are named, as errors** (security.md section 14): `no-eval`, `no-implied-eval`,
  `no-new-func`, `no-script-url` and `react/no-danger`. A rule named in the config stays on
  whatever a preset does.
- **Two of them are shown to work:** `react/no-danger` and `no-script-url` reported the control
  file. No control file tried `eval` or `new Function`, so those three rules are configured but not
  shown reporting.
- **What they miss:** `no-script-url` sees a `javascript:` string written in the code, not a URL
  that arrives as data; the link component of section 3 covers that case. Which linter and which
  version is [libraries.md](../architecture/libraries.md) section 4.

## 8. The package manager settings

The reference application was installed with
`npm install --ignore-scripts --before=2026-09-24` on npm 10.8: no dependency ran an install
script, and no version published after that date was taken, a week before the build. Type check,
lint, tests and build then passed, so the application needs no dependency build script, and
`allowScripts` or `allowBuilds` stays empty.

The two files below make the same controls part of the repository, so every install obeys them
(security.md section 10). They are written from the owners' docs (npm's config page and changelog,
CISA's axios alert, pnpm's settings and supply-chain pages, read 2026-10-01) and were not run:
the machine had npm 10.8.

`.npmrc`, for npm 11.10.0 or later. `min-release-age` exists since npm 11.10.0 (2026-02-11) and
`min-release-age-exclude` since 11.17.0; npm 10 has neither. There `--before=<date>` on the
install command installs only versions that were available on or before that date (npm's config
page, read 2026-10-02). It takes a fixed date that the person running the install has to choose
each time, where `min-release-age` is a rolling window set once in the repository. The reference
application was installed with the flag (npm 10.8, `--before=2026-09-24`).

```ini
# npm 12 blocks dependency install scripts with a warning; this makes the install fail instead.
strict-allow-scripts=true
# A version is installed only once it is 7 days old (CISA's advice after the axios compromise).
# Emergency path, for a critical advisory only, approved by a second person in the pull request:
# list the patched package in min-release-age-exclude; remove it when the version is 7 days old.
min-release-age=7
```

`pnpm-workspace.yaml`, for pnpm 11 and later:

```yaml
# A version is installed only once it is 7 days old (CISA's advice after the axios compromise).
# Emergency path, for a critical advisory only, approved by a second person in the pull request:
# add the patched package to minimumReleaseAgeExclude; remove it when the version is 7 days old.
minimumReleaseAge: 10080 # minutes
# The next two are pnpm defaults, written out so the policy shows in review.
strictDepBuilds: true # an unreviewed dependency build script fails the install
blockExoticSubdeps: true # only direct dependencies may come from git or a tarball URL
trustPolicy: no-downgrade # fails when a version has weaker provenance than earlier ones
```

Why it is good:

- **The controls live in the repository,** so a person, CI and an agent install under the same
  rules.
- **The emergency path is written next to the cooldown,** with who approves it and when the entry
  comes out; the React2Shell patch was blocked by a one-day cooldown that had no such line.
- **Each line says what it does,** so nobody deletes a default as noise. npm 12 already sets
  `allow-git` and `allow-remote` to `none`, so `.npmrc` does not repeat them; npm 11 needs
  `ignore-scripts=true` instead of `strict-allow-scripts`.
- **What they do not stop:** a payload that runs when the package is imported or bundled, and a
  version older than the cooldown. Provenance checks do not stop a package built from a hijacked
  CI with valid provenance (security.md section 10).

## 9. What the example leaves out

- **The BFF:** it sets the `__Host-` session cookie, rejects a request without the custom header,
  checks CSRF and decides access. That is server code; security.md sections 6 and 7 list what it
  must do.
- **The CI workflow:** pinned actions, a read-only token, no fork code in `pull_request_target`
  (security.md section 10).
- **Server-side React:** the application renders in the browser only, so section 8 of security.md
  does not apply to it.
