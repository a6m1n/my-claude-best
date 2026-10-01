# Example: the billing screens, laid out

A worked example for [architecture.md](architecture.md): the whole tree of a small client-rendered
React application, the billing screens of `Acme Corp`, with the configuration that checks its
rules, the startup file, the routes and one module's reads and writes. Each part says which rule it
follows and why. Names are invented. The code was type-checked, linted, unit-tested and built;
nothing was run in a browser. The code is quoted from a reference application that is not in this
folder: the example files of the `react/` practices quote its code, and the checks named were run
on it on 2026-10-01 and 2026-10-02.

Other examples own the rest of this code. The bodies of the components are in
[component-example.md](../components/component-example.md). The API client's session and headers,
the sanitised HTML, the link allowlist and the response headers are in
[security-example.md](../security/security-example.md). How the application measures its web
vitals is in [performance-example.md](../performance/performance-example.md).

**Navigation**

- [1. The tree](#1-the-tree)
- [2. The first day of a new application](#2-the-first-day-of-a-new-application)
- [3. The configuration that checks the rules](#3-the-configuration-that-checks-the-rules)
- [4. The startup file](#4-the-startup-file)
- [5. The routes](#5-the-routes)
- [6. One module's reads and writes](#6-one-modules-reads-and-writes)
- [7. What the checks caught](#7-what-the-checks-caught)

## 1. The tree

```text
<repo>/
├── src/
│   ├── main.tsx                         # startup: reads the settings; builds the clients and the router once
│   ├── styles.css                       # the stylesheet the build starts from
│   ├── route-tree.gen.ts                # written by the router plugin; never edited, never linted
│   ├── core/                            # code no module owns
│   │   ├── api-client.ts                # the ApiClient class: the one way to reach the backend; parses every answer
│   │   ├── config.ts                    # reads import.meta.env once, through a schema; only main.tsx imports it
│   │   ├── query-client.ts              # the query cache and its one staleTime
│   │   ├── invoice.keys.ts              # the key root of every invoice read, for both modules
│   │   ├── invoice.schema.ts            # the invoice both modules parse
│   │   ├── iso-date.ts                  # a date as YYYY-MM-DD in the user's time zone
│   │   ├── money.format.ts              # cents as currency text
│   │   ├── report-error.ts              # createErrorReporter(reportUrl): the function React calls for every error
│   │   ├── report-web-vitals.ts         # reportWebVitals(reportUrl): sends the visit's web vitals to the URL it is given
│   │   ├── send-report.ts               # sendReport(reportUrl, report): one small report with no session cookie
│   │   └── ui/                          # design-system components with no business words
│   │       ├── button.tsx
│   │       └── screen-pending.tsx       # the router's default pending screen; needs no router
│   ├── billing/                         # the domain folder
│   │   ├── list-invoices/               # module: see the invoices and the state of each
│   │   │   ├── external-link.tsx        # the one link to an address that comes from outside
│   │   │   ├── invoice-list.tsx         # InvoiceList; takes its pay link from the route
│   │   │   ├── invoice-status-badge.tsx # InvoiceStatusBadge
│   │   │   ├── invoice-status.schema.ts # InvoiceStatus: paid, overdue or due
│   │   │   ├── invoice-status.rules.ts  # invoiceStatus: which of the three an invoice is
│   │   │   ├── invoice-status.rules.test.ts  # the rule's test, beside it
│   │   │   ├── invoices.queries.ts      # invoicesQueryOptions
│   │   │   ├── link-url.rules.ts        # hasAllowedProtocol: which addresses a link may point to
│   │   │   └── link-url.rules.test.ts   # the rule's test, beside it
│   │   └── pay-invoice/                 # module: pay one invoice
│   │       ├── invoice.queries.ts       # invoiceQueryOptions: the invoice being paid
│   │       ├── pay-invoice-form.tsx     # PayInvoiceForm; takes its navigation from the route
│   │       ├── pay-invoice.mutations.ts # payInvoiceMutationOptions
│   │       ├── payment.schema.ts        # the payment method and the receipt
│   │       └── sanitized-html.tsx
│   └── routes/                          # the adapter: one file per route
│       ├── __root.tsx                   # the shell every screen renders in
│       ├── -screen-error.tsx            # the router's default error screen; "-": not a route
│       ├── index.tsx                    # "/" redirects to the list
│       ├── invoices.index.tsx           # /invoices
│       └── invoices.$invoiceId.pay.tsx  # /invoices/$invoiceId/pay
├── public/
│   └── _headers                         # response headers for the static host
├── .env.example                         # the setting names with no real value; config.ts reads them
├── index.html
├── eslint.config.js                     # the direction, the imports and the names
├── .oxlintrc.json                       # barrels, cycles, and React, accessibility, security rules
├── vite.config.ts
├── tsconfig.json                        # references the two files below
├── tsconfig.app.json                    # the application's compiler options and the alias
├── tsconfig.node.json                   # the options for vite.config.ts
├── package.json
├── package-lock.json
└── .gitignore
```

The session server, the Backend for Frontend of [security.md](../security/security.md) section 6,
is not part of this tree and is not shown.

What to notice:

- **Each module is one thing the user does**, named for it: seeing the invoices, paying one
  ([file-structure.md](../../any-language/file-structure/file-structure.md) section 1). Both modules
  read invoices, and neither imports the other.
- **`core/` holds what both modules need**: the invoice schema, the key root, the API client class and
  the query client ([architecture.md](architecture.md) sections 3 and 6). The status badge knows about
  invoices, so it stays in its module and not in `core/ui/`. The link, its rule and the sanitised
  HTML each have one module that uses them, so each sits in that module and moves down to `core/`
  only when a second module needs it
  ([file-structure.md](../../any-language/file-structure/file-structure.md) section 4, and
  section 6, move 3).
- **Every file name is kebab-case, with its role as a suffix** where the role recurs:
  `.queries.ts`, `.mutations.ts`, `.schema.ts`, `.rules.ts`, `.format.ts`, `.keys.ts`, `.test.ts`
  ([architecture.md](architecture.md) section 4). The files in `routes/` take the router's names.
- **The test sits beside the rule it tests** ([architecture.md](architecture.md) section 3).
  `vitest run` found both test files, both in `list-invoices/`, with no test settings in
  `vite.config.ts`.
- **`routes/` holds the route files and the adapter's own error screen.** The `-` prefix keeps the
  error screen out of the route tree. The route files, the error screen and `main.tsx` are the only
  hand-written files that import the router ([architecture.md](architecture.md) section 3).
- **`main.tsx` and `route-tree.gen.ts` belong to no kind of folder.** The first wires the
  application together; the second is written by a tool.

## 2. The first day of a new application

The order below makes the first module land on a tree that already checks it. It was not run once as
a list: the create command was run on its own, and the reference application was written by hand to
the same end state.

1. **Create the base:** `npm create vite@latest <name> -- --template react-ts`. It gives a working
   React, Vite and TypeScript project with a lint script, so nothing here starts from an empty
   folder. On 2026-10-02 it produced React 19, Vite 8, TypeScript `~6.0.2` and Oxlint as
   `npm run lint`.
2. **Install what the example's `package.json` lists beyond the template**, so the libraries are
   the ones the rules assume ([libraries.md](libraries.md) section 2 for the runtime and the
   build, section 4 for the lint, section 6 for the tests). The names are below, with no
   versions; [libraries.md](libraries.md) section 8 has the versions that passed the checks:

   ```sh
   npm install @tanstack/react-query @tanstack/react-router zod
   npm install -D @tanstack/router-plugin tailwindcss @tailwindcss/vite babel-plugin-react-compiler @rolldown/plugin-babel @babel/core eslint @eslint/js typescript-eslint eslint-plugin-react-hooks eslint-plugin-boundaries eslint-import-resolver-typescript eslint-plugin-check-file eslint-plugin-oxlint vitest
   ```

   Add `dompurify` and `web-vitals` when the first screen needs them.
3. **Write the configuration files in the order section 3 shows them**: the alias and compiler flags,
   the bundler, ESLint, then Oxlint. The alias comes first because every import that follows uses
   it, and the checks come before the first module so that no module is written against a rule that
   does not run yet.
4. **Write the first module and its route, then run `npm run typecheck`, `npm run lint`,
   `npm test` and `npm run build`.** All four exit 0 before the second module is started, so a
   broken rule is found while it has one file to blame.

## 3. The configuration that checks the rules

Four files hold the configuration that [architecture.md](architecture.md) sections 4, 5 and 13 ask
for, so a broken rule fails the type check or the lint.

### The alias and the compiler flags

`tsconfig.app.json`:

```json
{
  "compilerOptions": {
    "target": "es2023",
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "module": "esnext",
    "moduleResolution": "bundler",
    "moduleDetection": "force",
    "types": ["vite/client"],
    "jsx": "react-jsx",

    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "forceConsistentCasingInFileNames": true,

    "verbatimModuleSyntax": true,
    "erasableSyntaxOnly": true,
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "skipLibCheck": true,

    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src"]
}
```

Why it is good:

- **`paths` maps `@/*` to `./src/*`, with no `baseUrl`**, the form TypeScript 6.0 asks for
  ([architecture.md](architecture.md) section 5).
- **`strict` comes with the three flags of [architecture.md](architecture.md) section 13**:
  `noUncheckedIndexedAccess`, `verbatimModuleSyntax` and `erasableSyntaxOnly`. There is no
  `exactOptionalPropertyTypes`.
- **`moduleResolution: "bundler"`, `allowImportingTsExtensions` and `noEmit`** let every import
  name its `.ts` or `.tsx` file ([architecture.md](architecture.md) section 5). Vite builds the
  code; `tsc` only checks it.
- The other flags in the second group are no rule of this practice: keep them or drop them.
  `tsconfig.json` only references this file and `tsconfig.node.json`, which covers
  `vite.config.ts`.

### The bundler reads the same alias

`vite.config.ts`:

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

Why it is good:

- **`resolve.tsconfigPaths: true` makes Vite read the alias from `tsconfig.app.json`**, so the
  alias has one declaration and cannot work in the type check and fail at run time
  ([architecture.md](architecture.md) section 5). Vite 8 leaves the option off by default, which is
  why the comment says what it is for.
- **The router plugin points at the adapter folder and gives the generated tree a kebab-case
  name** ([architecture.md](architecture.md) section 3). `autoCodeSplitting` makes each route's
  component its own chunk ([architecture.md](architecture.md) section 10), and the comment says why
  the plugin comes first.
- The React Compiler preset is [components.md](../components/components.md)'s, and the Tailwind
  plugin is [visual-design.md](../design/visual-design.md)'s.

### The direction, the imports and the names, in ESLint

`eslint.config.js`:

```js
import js from "@eslint/js";
import boundaries from "eslint-plugin-boundaries";
import checkFile from "eslint-plugin-check-file";
import oxlint from "eslint-plugin-oxlint";
import reactHooks from "eslint-plugin-react-hooks";
import { defineConfig, globalIgnores } from "eslint/config";
import tseslint from "typescript-eslint";

const RELATIVE_IMPORTS = { group: ["./*", "../*"], message: "Import by the absolute path: @/<folder>/<file>." };
const SETTINGS_FILE = {
  name: "@/core/config.ts",
  message: "Only src/main.tsx reads the settings; take the value as a parameter.",
};
const ROUTER = {
  name: "@tanstack/react-router",
  message: "The router is the framework of src/routes/; a module takes a link or a callback as a prop.",
};

export default defineConfig([
  globalIgnores(["dist", "src/route-tree.gen.ts"]),
  {
    files: ["src/**/*.{ts,tsx}"],
    extends: [js.configs.recommended, tseslint.configs.strictTypeChecked, reactHooks.configs.flat.recommended],
    plugins: { boundaries, "check-file": checkFile },
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    settings: {
      "import/resolver": { typescript: { project: "./tsconfig.app.json" } },
      // The three kinds of folder. `src/main.tsx` wires them and belongs to none.
      "boundaries/elements": [
        { type: "core", pattern: "src/core" },
        { type: "routes", pattern: "src/routes" },
        { type: "module", pattern: "src/*/*", capture: ["domain", "module"] },
      ],
    },
    rules: {
      // One direction: routes -> modules -> core. A module imports its own files and core only.
      "boundaries/dependencies": [
        "error",
        {
          default: "disallow",
          policies: [
            {
              from: { element: { type: "routes" } },
              allow: { to: { element: { types: { anyOf: ["routes", "module", "core"] } } } },
            },
            {
              from: { element: { type: "module" } },
              allow: {
                to: [
                  { element: { type: "core" } },
                  // The same module only: both captured folder names have to match.
                  {
                    element: {
                      type: "module",
                      captured: {
                        domain: "{{ from.element.captured.domain }}",
                        module: "{{ from.element.captured.module }}",
                      },
                    },
                  },
                ],
              },
            },
            { from: { element: { type: "core" } }, allow: { to: { element: { type: "core" } } } },
          ],
        },
      ],
      // Absolute imports only: the import line names the file's place in the tree. The settings
      // are read in `src/main.tsx` alone and handed on as values.
      "no-restricted-imports": ["error", { patterns: [RELATIVE_IMPORTS], paths: [SETTINGS_FILE] }],
      "check-file/filename-naming-convention": [
        "error",
        { "src/!(routes)/**/*.{ts,tsx}": "KEBAB_CASE" },
        { ignoreMiddleExtensions: true },
      ],
      "check-file/folder-naming-convention": ["error", { "src/**/": "KEBAB_CASE" }],
    },
  },
  // A later block replaces the whole option of a rule, so each block below repeats what it keeps.
  {
    files: ["src/core/**/*.{ts,tsx}", "src/*/*/**/*.{ts,tsx}"],
    ignores: ["src/routes/**"],
    rules: {
      "no-restricted-imports": ["error", { patterns: [RELATIVE_IMPORTS], paths: [SETTINGS_FILE, ROUTER] }],
    },
  },
  {
    files: ["src/main.tsx"],
    rules: { "no-restricted-imports": ["error", { patterns: [RELATIVE_IMPORTS] }] },
  },
  // Last: turns off every ESLint rule that Oxlint already checks.
  ...oxlint.buildFromOxlintConfigFile("./.oxlintrc.json"),
]);
```

Why it is good:

- **`boundaries/elements` names the three kinds of folder of
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 2 by their
  path.** `src/core/ui/` counts as `core`, not as a module: a module imports
  `@/core/ui/button.tsx`, and the lint passes. `src/main.tsx` matches none of them, as the comment
  says: the startup file sits outside every layer (file-structure section 5).
- **`boundaries/dependencies` starts from `default: "disallow"` and lists what each kind may
  import** ([architecture.md](architecture.md) section 5). A module may import a module only when
  both captured folder names match its own, so one rule keeps every module apart, with no line per
  module. A new module needs no change here.
- **The `import/resolver` setting reads `tsconfig.app.json`**, so the boundary rule resolves `@/`
  paths to their folders.
- **`no-restricted-imports` bans `./` and `../`**, and its message tells the author the form to use
  ([architecture.md](architecture.md) section 5).
- **Two more `no-restricted-imports` rules keep the router and the settings in their homes.** `core/`
  and the modules may not import `@tanstack/react-router` ([architecture.md](architecture.md)
  section 3), and every file but `src/main.tsx` may not import `core/config.ts`
  ([architecture.md](architecture.md) section 8). A later config block replaces the whole option of
  a rule, so each block repeats what it keeps, as the comment in the file says.
- **`check-file` holds every file outside `routes/` and every folder to kebab-case**
  ([architecture.md](architecture.md) section 4). `ignoreMiddleExtensions` lets the role suffix
  through, and `routes/` is left out because the router's own names win there.
- **The generated route tree is ignored**, so a rule never fails on a file nobody edits.
- The rule sets in `extends` and the Oxlint bridge are [libraries.md](libraries.md)'s; the hooks
  rules are [components.md](../components/components.md)'s.

### Barrels and cycles, in Oxlint

`.oxlintrc.json`:

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["typescript", "react", "jsx-a11y", "import", "oxc"],
  "categories": { "correctness": "error" },
  "rules": {
    "react/rules-of-hooks": "error",
    "react/exhaustive-deps": "error",
    "import/no-cycle": "error",
    "oxc/no-barrel-file": "error",
    "no-eval": "error",
    "no-implied-eval": "error",
    "no-new-func": "error",
    "no-script-url": "error",
    "react/no-danger": "error"
  },
  "ignorePatterns": ["dist", "src/route-tree.gen.ts"]
}
```

Why it is good:

- **`oxc/no-barrel-file` fails on a barrel** whose imports load more than 100 modules
  ([architecture.md](architecture.md) section 5).
- **`import/no-cycle` fails on two files that import each other.** Inside one module the boundary
  rule allows any import, so this is the rule that keeps a module's own files from going in a
  circle.
- The React rules are [components.md](../components/components.md)'s, the `jsx-a11y` plugin is
  [accessibility.md](../design/accessibility.md)'s, and `no-eval`, `no-implied-eval`,
  `no-new-func`, `no-script-url` and `react/no-danger` are [security.md](../security/security.md)'s.

## 4. The startup file

`src/main.tsx`. The imports are cut: the application's own files are imported by absolute `@/`
paths, the two default screens come from `@/core/ui/screen-pending.tsx` and
`@/routes/-screen-error.tsx`, and the error reporter comes from `@/core/report-error.ts`.

```tsx
...

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

// A deploy removed the chunks this open tab still points to. A reload fetches the new
// index.html, which points to the new chunks (Vite, "Load error handling").
window.addEventListener("vite:preloadError", () => {
  window.location.reload();
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }

  // Optional, because the root route and the redirect at "/" show no screen of their own.
  interface StaticDataRouteOption {
    title?: string;
  }
}

const rootElement = document.getElementById("root");

if (rootElement === null) {
  throw new Error("index.html has no #root element");
}

// React calls these for an error a boundary caught and for one nothing caught: one place
// sees every failure of every screen.
createRoot(rootElement, { onCaughtError: reportError, onUncaughtError: reportError }).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
);

reportWebVitals(new URL("/web-vitals", config.apiBaseUrl));
```

Why it is good:

- **The settings are read here and nowhere else.** The API client, the query client and the router
  are built once, at startup. Both clients reach every loader through the router's context, and the
  route hands the API client to a module's component as a prop
  ([architecture.md](architecture.md) sections 3 and 8; file-structure section 4;
  [readability.md](../../any-language/readability/readability.md) section 6).
- **The router leaves freshness to the cache and starts loaders on intent**:
  `defaultPreloadStaleTime: 0` and `defaultPreload: "intent"`, each with a comment that says why
  ([architecture.md](architecture.md) sections 8 and 10).
- **Every route has a pending screen and an error screen by default**
  ([architecture.md](architecture.md) section 12).
- **`Register` types the whole route tree once** ([architecture.md](architecture.md) section 10).
  The comment on `title?` says why the field is optional, so nobody makes it required and breaks
  the two routes that show no screen.
- **Every error of every screen reaches one function.** `createRoot` gets `onCaughtError` and
  `onUncaughtError`, both set to the reporter that `createErrorReporter` builds from the report URL
  ([architecture.md](architecture.md) section 12). The report holds the error's name and the path,
  never its message, because a message can carry what the user typed or what the server answered.
  `core/send-report.ts` sends it with `fetch`, `keepalive: true` and `credentials: "omit"`: no
  session cookie goes with it, so the endpoint takes anonymous reports and needs neither the
  session nor the custom header of the API client ([security-example.md](../security/security-example.md)'s).
- **A reload on `vite:preloadError`** keeps an open tab working after a deploy removed the chunks
  it points to ([performance.md](../performance/performance.md) section 5).
- **The missing root element is a guard clause**, and blank lines split the stages: build, declare,
  find the root, render, report
  ([readability.md](../../any-language/readability/readability.md) sections 3 and 5).
- `reportWebVitals` and `createErrorReporter` take the URL they report to, so they read no setting. What it measures is
  [performance-example.md](../performance/performance-example.md)'s.

## 5. The routes

`src/routes/invoices.index.tsx`, the list screen:

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

- **The loader starts the module's fetch with `queryClient.query()`** and awaits it, so the screen
  renders with its data ([architecture.md](architecture.md) section 8). Its comment says why the
  fetch belongs here and not in a component.
- **The route reads the clock once and passes `today` down as a value**, so the rule that decides
  "overdue" takes every input in its signature
  ([readability.md](../../any-language/readability/readability.md) section 6).
- **The route composes the screen and owns the URL.** It places the list module's component and
  hands it the link to the pay screen as `renderPayLink`, so the list module names no URL
  ([architecture.md](architecture.md) section 6). The route holds no business rule (file-structure
  section 5).
- **Each import names the file that holds the name, by `@/`** ([architecture.md](architecture.md)
  section 5).
- The visually hidden text in the link is [accessibility.md](../design/accessibility.md)'s.

`src/routes/invoices.$invoiceId.pay.tsx`, the payment screen:

```tsx
import { createFileRoute } from "@tanstack/react-router";

import { invoiceQueryOptions } from "@/billing/pay-invoice/invoice.queries.ts";
import { PayInvoiceForm } from "@/billing/pay-invoice/pay-invoice-form.tsx";

export const Route = createFileRoute("/invoices/$invoiceId/pay")({
  loader: ({ context, params }) =>
    context.queryClient.query(invoiceQueryOptions(context.apiClient, params.invoiceId)),
  staticData: { title: "Pay invoice" },
  component: PayInvoiceScreen,
});

function PayInvoiceScreen() {
  const { apiClient } = Route.useRouteContext();
  const { invoiceId } = Route.useParams();
  const navigate = Route.useNavigate();

  return (
    <section className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">Pay invoice</h1>
      <PayInvoiceForm
        apiClient={apiClient}
        invoiceId={invoiceId}
        onPaid={() => void navigate({ to: "/invoices" })}
      />
    </section>
  );
}
```

Why it is good:

- **The loader returns the query's promise for the invoice in the URL**, so the router waits for
  it ([architecture.md](architecture.md) section 8).
- **The navigation after a payment is the route's**: it passes `onPaid` to the form, and the form
  never learns the list's URL ([architecture.md](architecture.md) section 6).
- **`Route.useParams()` and `Route.useNavigate()` are typed by the registered router**, so a wrong
  parameter name or path fails the type check ([architecture.md](architecture.md) section 10).

The two module components take what the routes hand them as props. From
`src/billing/list-invoices/invoice-list.tsx`, with the imports and the body cut:

```tsx
type InvoiceListProps = {
  // The route hands the client in, like `today`: the component reaches nothing by itself.
  apiClient: ApiClient;
  today: string;
  // The route supplies the link, so this module needs no router and no path of another module.
  renderPayLink: (invoice: Invoice) => ReactNode;
};

export function InvoiceList({ apiClient, today, renderPayLink }: InvoiceListProps) {
  ...
}
```

Why it is good: the prop is the module's whole contact with routing, and its comment tells the next
editor why the module does not import `Link` itself ([architecture.md](architecture.md) section 6).

## 6. One module's reads and writes

The `pay-invoice` module reads one invoice and pays it. Its keys grow from a root in `core/`, which
the list module uses too.

`src/core/invoice.keys.ts`:

```ts
// The root of every cached read about invoices. It lives in core because two modules read
// invoices, and a write in one has to mark the reads of both as stale.
export const invoiceKeys = {
  all: ["invoices"] as const,
  detail: (invoiceId: string) => ["invoices", invoiceId] as const,
};
```

Why it is good: the key root is data both modules share, so it sits in `core/`, and its comment
says why ([architecture.md](architecture.md) section 6). `detail` starts with the root, so an
invalidation of `all` reaches every invoice by prefix ([architecture.md](architecture.md)
section 9).

`src/core/query-client.ts`:

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

Why it is good: one `staleTime` for the whole cache, set where the cache is made, with the reason
for the value next to it ([architecture.md](architecture.md) section 8;
[readability.md](../../any-language/readability/readability.md) section 4). The unit is in the
name. `main.tsx` calls the factory once.

`src/billing/pay-invoice/invoice.queries.ts`:

```ts
import { queryOptions } from "@tanstack/react-query";

import type { ApiClient } from "@/core/api-client.ts";
import { invoiceKeys } from "@/core/invoice.keys.ts";
import { invoiceSchema } from "@/core/invoice.schema.ts";

export function invoiceQueryOptions(apiClient: ApiClient, invoiceId: string) {
  return queryOptions({
    queryKey: invoiceKeys.detail(invoiceId),
    queryFn: ({ signal }) =>
      apiClient.request(`/invoices/${encodeURIComponent(invoiceId)}`, { schema: invoiceSchema, signal }),
  });
}
```

Why it is good: one `queryOptions` holds the key and the fetch, and the invoice id is in the key
([architecture.md](architecture.md) section 8). The route's loader and the form call the same
function. The response is parsed with the shared invoice schema from `core/`, and the query's
`signal` goes to the request, so the query cache can cancel it.

The list module's read, `src/billing/list-invoices/invoices.queries.ts`, builds on the same root:

```ts
import { queryOptions } from "@tanstack/react-query";
import { z } from "zod";

import type { ApiClient } from "@/core/api-client.ts";
import { invoiceKeys } from "@/core/invoice.keys.ts";
import { invoiceSchema } from "@/core/invoice.schema.ts";

export function invoicesQueryOptions(apiClient: ApiClient) {
  return queryOptions({
    queryKey: invoiceKeys.all,
    queryFn: ({ signal }) => apiClient.request("/invoices", { schema: z.array(invoiceSchema), signal }),
  });
}
```

Why it is good: the list's schema is built from the shared one at the call, so the file declares
no schema of its own: a file holds one kind of thing
([file-structure.md](../../any-language/file-structure/file-structure.md) section 3). The key is
the root itself, so a payment that invalidates the root refreshes the list
([architecture.md](architecture.md) section 6).

`src/billing/pay-invoice/payment.schema.ts`:

```ts
import { z } from "zod";

export const paymentMethodSchema = z.enum(["card", "bank_transfer"]);

export type PaymentMethod = z.infer<typeof paymentMethodSchema>;

export const paymentReceiptSchema = z.object({
  invoiceId: z.string(),
  paidOn: z.iso.date(),
});
```

Why it is good: the file holds the module's own schemas and nothing else (file-structure
section 3). Each schema keeps the role word in its name, so `paymentMethodSchema` and the type
`PaymentMethod` inferred from it never read alike ([architecture.md](architecture.md) section 4).

`src/billing/pay-invoice/pay-invoice.mutations.ts`:

```ts
import { mutationOptions } from "@tanstack/react-query";

import type { PaymentMethod } from "@/billing/pay-invoice/payment.schema.ts";
import { paymentReceiptSchema } from "@/billing/pay-invoice/payment.schema.ts";
import type { ApiClient } from "@/core/api-client.ts";
import { invoiceKeys } from "@/core/invoice.keys.ts";

export function payInvoiceMutationOptions(apiClient: ApiClient, invoiceId: string) {
  return mutationOptions({
    mutationKey: [...invoiceKeys.detail(invoiceId), "pay"],
    mutationFn: (method: PaymentMethod) =>
      apiClient.request(`/invoices/${encodeURIComponent(invoiceId)}/payments`, {
        method: "POST",
        body: { method },
        schema: paymentReceiptSchema,
      }),
    // The invalidation sits here, not in the form: a callback passed to `mutate` is dropped
    // when the form unmounts. The promise is returned so the mutation stays pending until
    // every invoice read on screen is fresh.
    onSuccess: (_receipt, _method, _onMutateResult, context) =>
      context.client.invalidateQueries({ queryKey: invoiceKeys.all }),
  });
}
```

Why it is good:

- **The invalidation sits in the options and returns its promise**, and the comment gives both
  reasons, so the next editor does not move it into the form ([architecture.md](architecture.md)
  section 9).
- **It invalidates the invoice root**, so the list and the invoice both refresh, and it imports no
  other module ([architecture.md](architecture.md) sections 6 and 9).
- **The receipt is parsed with its schema, and the cache is not written from it**: a receipt is not
  the full invoice ([architecture.md](architecture.md) section 9). There is no `retry` and no
  optimistic update: a payment can be declined.

From `src/billing/pay-invoice/pay-invoice-form.tsx`, the part that reads and writes; the imports and
the form's markup are cut, and the markup is
[component-example.md](../components/component-example.md)'s:

```tsx
type PayInvoiceFormProps = {
  apiClient: ApiClient;
  invoiceId: string;
  onPaid: () => void;
};

export function PayInvoiceForm({ apiClient, invoiceId, onPaid }: PayInvoiceFormProps) {
  const { data: invoice } = useSuspenseQuery(invoiceQueryOptions(apiClient, invoiceId));
  const payment = useMutation(payInvoiceMutationOptions(apiClient, invoiceId));

  function payInvoice(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    const method = paymentMethodSchema.parse(new FormData(event.currentTarget).get("method"));

    payment.mutate(method, { onSuccess: onPaid });
  }

  ...
```

Why it is good:

- **The form reads with `useSuspenseQuery` and writes with `useMutation`, each from the module's
  options** ([architecture.md](architecture.md) sections 8 and 9).
- **A simple form reads `FormData`, parses it with the module's schema and calls `mutate`**
  ([architecture.md](architecture.md) section 11). The navigation the route handed in runs in the
  call's own `onSuccess`, the place for an effect on the screen ([architecture.md](architecture.md)
  section 9).
- **`payInvoice` has three stages, split by blank lines**: stop the browser's submit, parse,
  send ([readability.md](../../any-language/readability/readability.md) section 5).

Every read and write above goes through the one `ApiClient` in `src/core/api-client.ts`. The class
takes the base URL in its constructor, so it reads no setting. Its `request` method parses the
answer; the type definitions and the options of the request, which carry the session and the
headers, are cut, and those are [security-example.md](../security/security-example.md)'s:

```ts
// The one way to reach the backend. `src/main.tsx` builds one instance at startup and hands it
// on, so no module reads a setting to find the server.
export class ApiClient {
  readonly #baseUrl: string;

  constructor(baseUrl: string) {
    this.#baseUrl = baseUrl;
  }

  async request<TSchema extends z.ZodType>(path: string, request: ApiRequest<TSchema>): Promise<z.infer<TSchema>> {
    const response = await fetch(new URL(path, this.#baseUrl), {
      ...
    });

    if (!response.ok) {
      throw new ApiError(`${path} answered ${String(response.status)}`);
    }

    // Parsed, never cast: the returned type is checked against the data that arrived.
    return request.schema.parse(await response.json());
  }
}
```

Why it is good: the answer is parsed with the schema the caller passed, so the type a component
gets is checked against the data that arrived ([architecture.md](architecture.md) section 8). The
base URL comes in through the constructor and the instance comes in as a parameter, so a test hands
a module a client of its own and patches no module path ([architecture.md](architecture.md)
section 8). A failed status ends the method in a guard clause, and the comment on the last line
keeps the next editor from replacing the parse with a cast
([readability.md](../../any-language/readability/readability.md) sections 3 and 4).

## 7. What the checks caught

Each check is one script in `package.json`; the rest of the file is cut:

```json
{
  ...
  "scripts": {
    "dev": "vite",
    "typecheck": "tsc --noEmit -p tsconfig.app.json && tsc --noEmit -p tsconfig.node.json",
    "lint": "oxlint && eslint .",
    "test": "vitest run",
    "build": "vite build"
  },
  ...
}
```

Why it is good: the type check, the lint, the tests and the build are one command each, and each
exited 0 on the clean tree: the type check covers `vite.config.ts` too, and the 7 tests in 2 files
passed. `lint` runs Oxlint first and ESLint second, in the order Oxlint's docs
give. Which version of each tool runs is [libraries.md](libraries.md)'s.

Then each of these files, which breaks one rule, was added, run through the checks, and removed:

| The file broke | The check that failed | Rule |
|---|---|---|
| a file named `ControlPascal.ts` in a module | `check-file/filename-naming-convention`: does not match the `KEBAB_CASE` pattern | [architecture.md](architecture.md) section 4 |
| a module that imports another module | `boundaries/dependencies`: no policy allows `module` `billing/list-invoices` to import `module` `billing/pay-invoice` | section 5 |
| a module that imports a route | `boundaries/dependencies`: no policy allows a `module` to import `routes` | section 5 |
| a relative import in a module | `no-restricted-imports`: the `./` pattern, with the message to import by `@/` | section 5 |
| `core/` importing a module | `boundaries/dependencies`: no policy allows `core` to import a `module` | section 5 |
| a module importing a module of the same name in another domain | `boundaries/dependencies`: `payments/list-invoices` may not import `billing/list-invoices` | section 5 |
| a module that imports `@tanstack/react-router` | `no-restricted-imports`: "The router is the framework of src/routes/; a module takes a link or a callback as a prop" | [architecture.md](architecture.md) section 3 |
| a relative import in a module, after the two new blocks were added | `no-restricted-imports`: the `./` pattern, with the message to import by `@/` (the repeated pattern still works) | section 5 |
| `core/` importing `core/config.ts` | `no-restricted-imports`: "Only src/main.tsx reads the settings; take the value as a parameter" | [architecture.md](architecture.md) section 8 |
| a route importing `core/config.ts` | `no-restricted-imports`: the same message | section 8 |
| an `index.ts` that re-exports a module | Oxlint `oxc/no-barrel-file`: 249 modules loaded, over the threshold of 100 | section 5 |

The same run showed the React, accessibility and security rules of `.oxlintrc.json` failing on a
component written to break them; those rules belong to the files section 3 names.

One rule of [architecture.md](architecture.md) has no check here: server data copied into state
(section 7). Review asks it.
