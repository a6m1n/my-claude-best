# React application architecture rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. The application format](#2-the-application-format)
- [3. The tree: by what the user does](#3-the-tree-by-what-the-user-does)
- [4. File names](#4-file-names)
- [5. Imports: absolute, direct, one way](#5-imports-absolute-direct-one-way)
- [6. A screen is composed in its route](#6-a-screen-is-composed-in-its-route)
- [7. Where state lives](#7-where-state-lives)
- [8. Server data: reads](#8-server-data-reads)
- [9. Server data: writes](#9-server-data-writes)
- [10. Routing and URL state](#10-routing-and-url-state)
- [11. Forms](#11-forms)
- [12. Errors and loading](#12-errors-and-loading)
- [13. TypeScript settings](#13-typescript-settings)
- [14. The server-rendered case](#14-the-server-rendered-case)
- [15. Common mistakes](#15-common-mistakes)
- [16. Where the rules stop holding](#16-where-the-rules-stop-holding)
- [17. Review checklist](#17-review-checklist)
- [18. Sources](#18-sources)

## 1. Purpose and the one rule

This file is for everyone who starts or grows a React application: people and AI agents alike.
Read it before you choose the format of an application, add a folder, a module or a route, or
write a query, a mutation, a form or an error screen. Every line that carries a read date is to be distrusted after 2027-04-01 until it is read again; [README.md](README.md), under how to adopt, says how to list those lines.

Its tree has the shape of [file-structure.md](../../any-language/file-structure/file-structure.md):
three kinds of folder, one import direction, one role per file and absolute imports. This file
links that practice for those rules and argues the tree from React's own reasons (section 3). It
adds the folders, where shared UI goes, the file names, the import alias, the tool that checks the
direction, and where a test file sits. It also covers what file-structure leaves open: the format
of the application, where state lives, how server data is read and written, routing, forms and
errors. Other questions have their own owners:

| Question | Owner |
|---|---|
| How one component or one hook is written | [components.md](../components/components.md) |
| How props, state, events and refs are typed | [components.md](../components/components.md) section 3 |
| Which library does which job, and its version | [libraries.md](libraries.md) |
| What the browser side must and must not do | [security.md](../security/security.md) |
| What fast means, and how to measure it | [performance.md](../performance/performance.md) |
| How a screen looks, and how it behaves | [visual-design.md](../design/visual-design.md), [ux.md](../design/ux.md) |
| Focus, announcements and the other accessibility rules | [accessibility.md](../design/accessibility.md) |
| How a function reads | [readability.md](../../any-language/readability/readability.md) |

Every example comes from one invented application: the billing screens of `Acme Corp`, with the
modules `billing/list-invoices` and `billing/pay-invoice`. [layout-example.md](layout-example.md)
shows it whole. Its code was type-checked, linted, unit-tested and built; nothing was run in a
browser.

The one rule: **every kind of thing has one home, and its kind decides where.** A screen lives in
its route file. One thing the user does lives in its module. Code no module or route owns lives in
`core/` ([file-structure.md](../../any-language/file-structure/file-structure.md) section 4 says
when code moves there). Data the server owns lives in the query cache. State a link should carry lives in the
URL. A reader who knows what kind of thing they want knows where to find it, and no value has a second copy that
drifts away from the first.

Why it matters:

- React leaves the structure to you. Next.js calls itself "unopinionated" about how a project is
  organised, and no React owner states a convention for file names. Without a rule, each author
  picks a place, and the next author copies the place they saw.
- The common mistakes of a React application are second homes: fetched data copied into component
  state, an `index.ts` that gives a module a second import path, a module that reaches into another
  module's files. Section 15 shows each one with its fix.

## 2. The application format

Choose the format before the first route, from what the pages must do. A later change moves every
route and the way each one loads its data.

react.dev's advice is to start with a framework: "If you want to build a new app or website with
React, we recommend starting with a framework." The same team says a framework does not mean a
server: "All the frameworks we recommend support client-side rendering (CSR) and single-page apps
(SPA), and can be deployed to a CDN or static hosting service without a server." A build from
scratch with Vite is, in react.dev's words, "often the same as building your own adhoc framework":
routing, data loading and code splitting become your work (read 2026-10-01).

| The application | Format | What you get | What it costs |
|---|---|---|---|
| A product behind a login, with no page a crawler must read | A client-rendered app: Vite and a router | The bundle is static files on static hosting, with no server that renders pages. One team left Next.js for a Vite app because it was "paying for Next.js's server runtime ... while opting out of every feature that justified that cost" (one team's account) | The session needs a server, though: a product that handles personal or payment data gets a Backend for Frontend, a server component to run and patch ([security.md](../security/security.md) section 6). You set up routing, data loading and code splitting yourself; the rest of this file does that with a router and a query cache. The first screen waits for the script and then for its data: "at least 3 serial requests on the first page load", in one trainer's count |
| Pages that must be indexed, shown as a link preview or cited, or whose first paint on a slow device matters | A framework that prerenders those routes at build time, or renders them on the server | HTML a crawler reads without running a script, and a first paint that does not wait for the bundle | Server rendering adds a server runtime that you run and patch: on 2025-12-03 react.dev published a critical flaw in Server Components that let anyone run code on the server. The rules are in [security.md](../security/security.md) |
| Not sure yet, or a mix of both | A framework in single-page mode: React Router's framework mode with `ssr: false`, or TanStack Start's SPA mode | File-based routes and code splitting by route now; prerendering or server rendering for some routes later, in the same tool | The framework's conventions and release pace. TanStack Start's status is in [libraries.md](libraries.md) |

No source read compares row 1 with row 3 for a product behind a login. Row 1 is the case this
practice's examples use, because it has the fewest parts in the frontend. Pick row 3 when you cannot yet say
whether a crawler will ever need a page, since a later change of format moves every route.

Leaving a public page client-rendered has its own cost. One team with about 280 routes had to add
prerendering to a plain single-page app, because "a raw SPA serves the same index.html for every
route" (one team's account). Brad Westfall, a React trainer, adds that "Server Rendering is not
just for SEO": the first paint matters too.

The choice is argued in public. Andrew Clark of the React team: "If you use React, you should be
using a React framework." Mark Erikson answers with npm download counts that put single-page apps
at "at least half of the React ecosystem"; a download count is a proxy, not a count of teams. The
table does not settle the argument. It says which need decides.

This practice's examples are the first row: billing screens behind a login.

## 3. The tree: by what the user does

The tree groups code by what the user does, and each screen is composed in its route. The reasons
are React's. Files that change together sit together, so a change to one user flow stays in one
folder (colocation, quoted in the module rule below). react.dev asks for a screen's data
dependencies "at the route level", so the route is where a screen's data and parts meet (section
6). A screen loads what it imports, and Vite fetches every file a barrel lists, so a module is
imported file by file (section 5). And a team can change or delete one module alone:
bulletproof-react, Robin Wieruch, Nadia Makarevich (2022) and Feature-Sliced Design all keep
features from importing each other, none of the four argues from a backend, and Makarevich names
independence and cheap refactoring as her reasons.

The shape is the one these React sources prescribe. bulletproof-react composes features "at the
application level", Robin Wieruch's features do not import each other, and Angular's style guide, a
frontend owner, says to organise by feature and to "avoid creating directories like `components`,
`directives`, and `services`". React's own word is short: the old React FAQ, no longer updated,
says "don't spend more than five minutes on choosing a file structure", and that larger projects
"often use a mix" of grouping by feature and by file type. Josh Comeau groups by type instead: in
his experience "real life isn't nicely segmented", and feature boundaries become arbitrary. This
practice stays by feature, because a flow kept in one folder is changed and deleted in one place,
which is what the sources above argue for. TanStack Router's own examples keep code that is not a
route by type (`components/`, `utils/`) or as loose files beside `routes/`; they are demos of the
router, not models of a growing application. The shape is the same as
[file-structure.md](../../any-language/file-structure/file-structure.md) section 2's, three kinds
of folder and one import direction, and in a React application the folders are these:

```text
src/
├── main.tsx              # startup: reads the settings, builds the API client, the query client and the router once, then renders
├── styles.css            # the stylesheet the build starts from
├── route-tree.gen.ts     # written by the router plugin; never edited by hand
├── core/                 # code no module owns; imports no module and no route
│   ├── ui/               # design-system components with no business words: button, dialog
│   ├── api-client.ts     # the ApiClient class: the one way to reach the API
│   ├── config.ts         # reads import.meta.env once; only main.tsx imports it
│   ├── query-client.ts   # the query cache and its defaults
│   ├── invoice.keys.ts   # the query-key root of data two modules read
│   └── invoice.schema.ts # data two modules share
├── billing/              # a domain folder, named for what the application does
│   ├── list-invoices/    # a module: one thing the user does
│   └── pay-invoice/
└── routes/               # the adapter: turns a URL into a screen composed from modules
```

| React folder | Holds | Imports | Same kind in file-structure.md |
|---|---|---|---|
| `src/main.tsx` | reads the settings, builds the API client, the query client and the router once, gives the router its default screens, renders | anything; it sits outside every layer | the file that starts the process (section 5) |
| `src/core/` | the API client, the settings, the query client, the schemas and query-key roots that two modules share, formats | libraries and `core/`; never the router | `core/` (section 4) |
| `src/core/ui/` | design-system components with no business words | the same as `core/` | part of `core/` |
| `src/<domain>/<module>/` | one thing the user does: its components, hooks, queries, mutations, schemas, rules, and their tests | its own files, `core/` and libraries; never another module, a route or the router | a module (section 3) |
| `src/routes/` | one file per route, with its loader and its screen; the router's own error screen; and code one route uses, in `-` folders, in a code base that keeps one-route flows there (section 3, Scalability) | modules, `core/` and the router | an adapter (section 5) |

- **`routes/` composes each screen, and only it and `main.tsx` import the router.** A route file
  turns a URL into a screen: its loader starts the fetches of the modules, and its component places
  their components. It holds no business rule
  ([file-structure.md](../../any-language/file-structure/file-structure.md) section 5). No owner
  says that only `routes/` imports the router; it is this practice's choice, because a module's
  component then renders and is tested without a router, and section 6 says how a module gets a
  link without it. The router's default error screen calls the router to retry, so it sits in
  `routes/`, named with the `-` prefix that tells TanStack Router the file is not a route:
  `routes/-screen-error.tsx`. A pending screen that needs no router stays in `core/ui/`. The
  boundary rule of section 5 checks imports between folders, not imports of a library, so a second
  rule catches a router import in the wrong place.

  Check: ESLint's `no-restricted-imports` fails on an import of `@tanstack/react-router` in `core/`
  or in a module; only `routes/` and `main.tsx` are left free of it
  ([layout-example.md](layout-example.md) section 3).
- **Shared UI goes to `core/ui/`, and only UI with no business word in it**: a button, a dialog, a
  field. A component that knows about invoices stays in its module, even when a second module could
  use it; [file-structure.md](../../any-language/file-structure/file-structure.md) section 6,
  move 3, decides whether it moves down or is copied. Robin
  Wieruch promotes code that two features use to a shared folder. Here that folder is `core/`, by
  this library's naming rule, which bans the name `shared`
  ([file-structure.md](../../any-language/file-structure/file-structure.md) section 7). React
  sources usually call this folder `shared` (Feature-Sliced Design), `lib` or `components/ui`
  (shadcn/ui), and no React source bans the name.
- **A module keeps its components next to its data code.** Its components, queries, mutations,
  schemas and rules sit in one folder, so a change to paying an invoice stays in `pay-invoice/`.
  Kent C. Dodds' rule: "Place code as close to where it's relevant as possible"; he credits Dan
  Abramov with "Things that change together should be located as close as reasonable."
- **A test sits beside the file it tests**, as `<file>.test.ts` or `<file>.test.tsx`. This is the
  React case, and it departs from
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 8, which takes the
  `tests/` tree of
  [python/testing/layout.md](../../python/testing/layout.md). The colocation reason above holds: a
  test changes with its file, and a reader who opens the folder sees both. The test imports by the
  same `@/` path as every other file. Angular's style guide puts unit tests in the same directory
  as the code they test, Robin Wieruch colocates them, and Kent C. Dodds gives the reason. Inside
  `routes/`, the router plugin treats every file as a route candidate, so a test beside a route
  file needs `routeFileIgnorePattern: "\\.test\\.tsx?$"` in the plugin's options: without it the
  plugin warns about every test file on each build, and in development it writes a route template
  into a new empty file there. None of the eight TanStack examples read on 2026-10-03 sets this
  pattern or keeps a test in `routes/`. A TanStack maintainer pointed to this option for tests
  beside routes in a 2024 discussion; none of those eight examples uses it, so the pattern
  `\\.test\\.tsx?$` is this practice's own setting. TanStack's testing guide puts route tests in a
  parallel `src/test/routes/` tree instead. [layout-example.md](layout-example.md) section 3 shows
  the pattern.
- **A generated file is never edited.** The router plugin writes `route-tree.gen.ts` on every dev
  run and every build, and both linters skip it. The plugin's default name is `routeTree.gen.ts`;
  the example sets a kebab-case name, so section 4 holds for this file too.
- **Scalability: the tree grows in steps.** By default a user flow is a module from its first
  route, as section 1, the table above and [layout-example.md](layout-example.md) do. That is
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 6, move 1, a new
  feature is a new module, with its tests beside its files rather than in `tests/` (the test bullet
  above). Moves 3 and 4 there carry over as written. Moves 2 and 6 take this file's forms: a file
  that becomes a folder gets no index file (section 5), and a new module or a second domain folder
  needs no change to the lint config, since its patterns capture the domain and the module
  ([layout-example.md](layout-example.md) section 3). Feature-Sliced Design v2.1
  names the cost: a module that serves one route spreads one user flow over a route file and a
  module. The allowed alternative: a code base may keep a flow that one route uses in that route's
  `-` folder (`routes/invoices/-components/`), which the router leaves out of the route tree, an
  option its docs give and none of the eight TanStack examples read on 2026-10-03 uses, and make
  it a module when a second route reuses it, the line v2.1 draws. A code base picks one of the two
  and keeps it, so each kind of thing still has one home; the alternative departs from move 1 for
  a flow that one route uses. A `-` folder holds what v2.1 keeps in a page: UI, forms and data
  logic, such as the route's queries and mutations, that no other route reuses. It belongs to the
  route files in the folder that holds it: `routes/invoices/-components/` belongs to the routes
  under `routes/invoices/`. Only those files import it, it imports what a route may import, and a
  business rule, a pure decision with its test, still goes to a module, as the first bullet of this
  section says. When `routes/` grows, `(group)` folders sort its files without changing a URL.

  Check: in review, does any import of a `-` folder come from outside its folder?

## 4. File names

- **Every file and folder name is kebab-case**: lower case, words joined by `-`
  (`pay-invoice-form.tsx`, `list-invoices/`). No React owner states a convention for file names, so
  this is this practice's choice. It gives one rule for every kind of file, so nobody decides the
  case per file, and a name that behaves the same on a case-sensitive and a case-insensitive file
  system. A developer of several React applications, Codemzy, moved them all to kebab-case in 2025
  for these two reasons, and bulletproof-react enforces it. The cost: a component file no longer
  matches the PascalCase name of its component. A team that wants the match takes PascalCase for
  component files ([README.md](README.md), the points to adapt).
- **A file whose role recurs from module to module carries the role as a suffix before the
  extension**: `invoices.queries.ts`, `pay-invoice.mutations.ts`, `payment.schema.ts`,
  `invoice-status.rules.ts`, `money.format.ts`, `invoice.keys.ts`, and
  `invoice-status.rules.test.ts` for a test. This is the TypeScript form of the role in the file
  name, [file-structure.md](../../any-language/file-structure/file-structure.md) section 7; its
  NestJS example in section 12 there, `<name>.controller.ts`, has the same shape.
- **A component file is named for its component, and a hook file for its hook**:
  `pay-invoice-form.tsx` holds `PayInvoiceForm`, and `use-invoice-filters.ts` would hold
  `useInvoiceFilters`. A file that is the only one of its kind is named for what it holds:
  `api-client.ts`, `config.ts`, `query-client.ts`. What else goes in a component's file is
  [components.md](../components/components.md)'s.
- **Query options, mutation options, schemas and key factories keep their role word in the
  exported name**: `invoicesQueryOptions`, `payInvoiceMutationOptions`, `paymentMethodSchema`,
  `invoiceKeys`. This departs from
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 7, which keeps
  the role out of the names inside a file. Section 12 there lets a language keep its own file
  names; keeping the role word in the exported name is this practice's own choice. A named import
  drops the file name at the line that uses it,
  `useSuspenseQuery(invoicesQueryOptions(apiClient))`, and a schema shares its subject with the type inferred
  from it, `paymentMethodSchema` and `PaymentMethod`: the role word tells them apart. The ecosystem
  names them the same way: TanStack Router's guide calls a query's options `postsQueryOptions`, and a
  TanStack Query maintainer calls a key factory `todoKeys`. Everything else follows section 7 as it
  stands: a function is named for what it answers (`invoiceStatus` in `invoice-status.rules.ts`), and
  a type for its subject (`InvoiceStatus`, `PaymentMethod`).
- **Only route files take the router's own names**: `__root.tsx`, `invoices.index.tsx`,
  `invoices.$invoiceId.pay.tsx`. The router plugin reads meaning from them: `$` makes a parameter,
  `.` nests a route, and a `-` prefix leaves a file out of the route tree. Kebab-case does not apply
  to route files. A `-`-prefixed file and the files in a `-` folder are no routes, so kebab-case
  and the role suffixes hold for them, and a file keeps its name when a second route reuses it and
  it moves to a module. Both name checks skip `src/routes/`, so review checks those names.
- **Never a name that [file-structure.md](../../any-language/file-structure/file-structure.md)
  section 7 bans**, such as `utils` or `shared`, as a file or a folder. This is this library's
  naming rule; section 3 says what React sources call such a folder.

With `ignoreMiddleExtensions`, the name check below reads the name before the role suffix, so
`invoice-status.rules.test.ts` passes it.

Check: `eslint-plugin-check-file` fails the lint on a file or folder name outside `src/routes/` that
is not kebab-case ([layout-example.md](layout-example.md) section 3).

## 5. Imports: absolute, direct, one way

[file-structure.md](../../any-language/file-structure/file-structure.md) owns the import rules:
absolute imports in section 7 there, one direction in section 2 there, and a tool that checks the
direction in section 11 there. This section gives each its React form.

- **Import a name from the file that holds it. Never write an `index.ts` that only re-exports.** A
  barrel file makes the tools load every file it lists when one name is imported. Vite's guide says
  that importing one API from a barrel makes every file in it get fetched and transformed, and tells
  you to import directly. Atlassian removed barrels from its Jira frontend and reported type
  highlighting more than 30% faster, local unit tests about 50% faster and 75% fewer build minutes;
  those are the vendor's own numbers from one very large repository, and Atlassian names the cost
  too, less encapsulation. Marvin Hagemeister measured the cost on a synthetic project, not a real
  application. On current Vite, an issue shows a barrel imported by several entry points putting a
  heavy dependency that only one of them needs into a shared chunk. bulletproof-react notes that
  barrels used to be recommended, and now says to import files directly. The cost: a module has no
  single file that lists what it offers. Robin Wieruch's layout keeps index files as that list; this
  practice takes the other side, and the boundary rule below does the job such an index does. The
  check below has a threshold, so a barrel that loads few modules passes it, and review catches
  those.

  Check: Oxlint's `oxc/no-barrel-file` fails on a barrel of `export *` lines whose imports load
  more than 100 modules, its default threshold.
- **Import every file by its absolute path through `@/`**, the alias for `src/`:
  `import { invoiceKeys } from "@/core/invoice.keys.ts"`. Declare the alias once, as `paths` in
  `tsconfig.app.json` with no `baseUrl` (TypeScript 6.0 deprecates `baseUrl`), and let the bundler
  read the same map with Vite 8's `resolve.tsconfigPaths: true`. Both halves are needed: the
  TypeScript docs warn that `paths` alone makes "path aliases that appear to work in TypeScript but
  will crash at runtime". `@/` is the alias in shadcn/ui's Vite guide, in create-next-app and in
  bulletproof-react. Copy the `paths` line from such a guide, not its `baseUrl`.
- **Write the file extension**, `.ts` or `.tsx`. Vite's guide says an import without one costs up
  to six file system checks; `allowImportingTsExtensions` lets TypeScript accept the extension.
- **`#/` is the standards-based alternative**: a subpath import, `"imports": { "#/*": "./src/*" }`
  in `package.json`. TypeScript 6.0 reads it under `moduleResolution: "bundler"`, and Node accepts
  `#/` from 24.14 and 25.4 (read 2026-10-01). It is a Node standard declared in `package.json`,
  where `@/` is a convention each tool is told about. The cost is that Node floor, and that
  generators and guides show `@/`. The example does not use it, so it was not tested there.

  Check: ESLint's `no-restricted-imports`, with the patterns `./*` and `../*`, fails on every
  relative import ([layout-example.md](layout-example.md) section 3).
- **Imports point one way: routes, then modules, then `core/`.** The direction is
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 2; its React
  check is `eslint-plugin-boundaries` and its rule
  `boundaries/dependencies`. The config names three kinds of element by folder, `core`, `routes`
  and `module`, and captures each module's domain and module folder names, so a module may import
  another module only when both names match its own, which means only itself. In the example
  application the rule failed on each of four broken imports, added on purpose and then removed: a
  module importing another module, a module importing a route, `core/` importing a module, and a
  module importing a module of the same name in another domain.

  Its version notes and config keys are [libraries.md](libraries.md) section 4's. What the rule
  cannot see: it reads imports through `eslint-import-resolver-typescript`, and only those that
  resolver can resolve. A file in none of the three kinds of folder, such as one directly in a
  domain folder, is no element, and the rule skips an import of it unless `checkUnknownLocals` is
  on; the example turns it on, so two modules cannot share such a file. How it treats
  `import type` and a dynamic `import()` was not verified.

  Check: `boundaries/dependencies` fails the lint ([layout-example.md](layout-example.md)
  section 3).

## 6. A screen is composed in its route

- **When a screen needs two modules, its route file imports both and places them.** When one needs
  a value from the other, the route passes it as a prop. bulletproof-react: "It might not be a good
  idea to import across the features. Instead, compose different features at the application
  level." Robin Wieruch gives the second reason: composition at the parent level lets the data
  fetches run in parallel. The route's loader starts the fetches of both modules at once, where a
  component that rendered another module's component would start that fetch only once it rendered.
  Each module stays deletable on its own, and the rule of
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 2 that modules do
  not import each other holds.
- **A module gets a link or a navigation from the route.** A link comes in as a render prop
  (`renderPayLink`), a navigation as a callback (`onPaid`). The module then names no URL and imports
  no router. No owner states this; it is this practice's design, and it follows from the router
  rule of section 3. The reason is coupling that nothing shows. A module that writes
  `<Link to="/invoices/$invoiceId/pay">` depends on the pay screen through the router's registered
  types, with no import between the two modules for the boundary rule to see. The cost is one prop
  per link or navigation a module offers. [layout-example.md](layout-example.md) section 5 shows
  both.
- **When a write in one module must refresh what another module reads, the root of their query
  keys lives in `core/`** (`core/invoice.keys.ts`), and each module builds its own `queryOptions` on
  it. Paying an invoice changes the list too, and the payment module may not import the list
  module's options. [file-structure.md](../../any-language/file-structure/file-structure.md)
  section 4 puts data two modules share in `core/`, and a key root
  is such data. The rest of each key stays with its query in the module, where a TanStack Query
  maintainer keeps keys. This is this practice's own design, tested in the example application: it
  type-checks, lints and builds, but nobody watched a payment refresh the list in a browser. A
  common form, a write that invalidates with the reading module's own options, is fine inside one
  module and is a cross-module import here (section 15, mistake 3).
- **A schema that two modules parse lives in `core/`** (`core/invoice.schema.ts`), by the same rule
  of [file-structure.md](../../any-language/file-structure/file-structure.md) section 4. A schema
  one module uses stays in that module.

## 7. Where state lives

When you add a piece of state, put it on the lowest rung of this ladder that serves every component
that reads it.

| The state | Where it lives | Source |
|---|---|---|
| used by one component | `useState` or `useReducer` in that component | Kent C. Dodds, state colocation |
| used by a few components of one screen | their closest common parent, passed down as props; pass JSX as `children` before you reach for Context | Kent C. Dodds; react.dev on Context |
| used deep inside one module | a reducer and a Context, provided by the module | react.dev, "Scaling Up with Reducer and Context" |
| kept by a reload, a shared link or the back button: a filter, a sort, a page, a tab | the URL's search params, checked with a schema (section 10) | TanStack Router; the author of nuqs |
| owned by the server | the query cache (sections 8 and 9) | Kent C. Dodds; TkDodo |
| client state the whole application shares that no rung above fits | a store, last ([libraries.md](libraries.md) names one) | Nadia Makarevich |

- **Server data is read from the cache where it is shown, never copied into component state or a
  store.** A copy is taken once and does not follow the cache: when the cache refetches, the copy
  still shows the old values. TkDodo, a TanStack Query maintainer: "If we can leverage the cache to
  display data that we do not own, there isn't really much left that is real client state." Kent C.
  Dodds draws the same line between server cache and UI state. Section 15, mistake 1, shows the
  copy and its fix.

  Check: in review, does a `useState` or a store take its first value from a query's `data`?
- **A value you can compute from state or props is computed, not stored.**
  [components.md](../components/components.md) owns that rule.
- **Many applications need no state library.** Nadia Makarevich (2025): "Most of the time ... you
  don't need a 'state management library' at all." In the State of React 2025 survey, 1,271
  respondents used none; the survey counts people who chose to answer, not teams.

## 8. Server data: reads

- **Build the API client once, in `src/main.tsx`, and hand it on.** `main.tsx` builds each shared
  object once, at startup: the API client, the query client and the router. The router's context
  carries both clients to every loader, so every loader reads the same cache, as TanStack Router's
  guide to external data loading does. The route's component reads the API client with
  `Route.useRouteContext()` and gives it to a
  module's component as a prop, and the module's `queryOptions` and `mutationOptions` take it as
  their first parameter (`invoicesQueryOptions(apiClient)`). The rule itself is
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 4's for a
  client and [readability.md](../../any-language/readability/readability.md) section 6's for a
  setting; this file adds only how React carries the object. The reason: a module that imports a
  ready-made client has an input no caller can see, and its test has to patch a module path. React
  context is another way to hand the client down, and no owner states which to use; the prop is
  this practice's choice, because a component's props then show everything it depends on.

  Check: ESLint's `no-restricted-imports` fails on an import of `core/config.ts` in any file but
  `src/main.tsx` ([layout-example.md](layout-example.md) section 3). In review, does any file
  import a ready-made client instead of taking one?
- **Write one `queryOptions` per query, in a `<name>.queries.ts` file of its module, or of its
  route's `-` folder while one route reads it, in a code base that keeps one-route flows there
  (section 3)**, with the key and the fetch function together. The route's loader, the component and an invalidation all call the same
  function. TkDodo: "Separating QueryKey from QueryFunction was a mistake." TanStack Query's guide
  says `queryOptions` exists to "share queryKey and queryFn between multiple places, yet keep them
  co-located". Export the options, not a hook that wraps them: TkDodo wrote in February 2026 that
  "The best abstractions are not configurable", and options work in a loader and an event handler,
  where a hook cannot run. A call site that needs more spreads its own options over them.
- **Every value the fetch depends on is part of the key**: `invoiceKeys.detail(invoiceId)`. Each
  value then has its own cache entry. TkDodo advises this over calling `refetch()` with new
  parameters.
- **Set one `staleTime` for the whole cache**, on the query client in `core/query-client.ts`. The
  default is 0: cached data is stale at once and is refetched on every mount, window focus and
  reconnect (TanStack Query's important defaults, read 2026-10-01). TkDodo sets a default globally
  and prefers at least 20 seconds. The example's 60 seconds is this practice's choice; a query whose
  data changes faster or slower sets its own.
- **The route's loader starts the fetch with `queryClient.query(options)`**, and awaits the data
  the screen needs first. Data the screen can show later starts with
  `void queryClient.query(options).catch(noop)`, not awaited. The fetch then starts as soon as the
  URL matches, in parallel with the download of the route's code: under automatic code splitting the
  loader stays in the main bundle. A fetch started in a component waits until that component
  renders, the network waterfall react.dev warns about. The older loader methods `ensureQueryData`
  and `prefetchQuery` are deprecated, and TanStack Query says each "will be removed in the next
  major version"; TanStack Router's own guide still shows `ensureQueryData` (both read 2026-10-01).
  `query()` does not retry by default, so a failed loader shows the error screen at once, and that
  screen's button is the retry (section 12).
- **The component reads with `useSuspenseQuery(options)`.** Its `data` is always defined: the
  router's pending screen shows while the loader runs, and an error goes to the error screen. It
  cannot be turned on and off by a condition (TanStack Query's suspense guide).
- **The router leaves freshness to the cache.** Set `defaultPreloadStaleTime: 0` on the router, so
  a preload always asks the query cache and the router keeps no second copy of loader data (TanStack
  Router's preloading guide).
- **Every response is parsed with its schema, in the one API client.** `core/api-client.ts` takes
  the schema with the request and returns `schema.parse(...)` of the body, never a cast, and the
  type of the result is inferred from the schema (section 13). No owner in
  the sources read states this; it is this practice's choice. A TypeScript type is a claim the
  compiler cannot check against data that arrives at run time. A cast lets a changed response
  through to a component that fails far from the cause; a parse fails at the boundary and names the
  field. The API client is the one client per external system of
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 4; what it
  must do for the session and its headers is [security.md](../security/security.md)'s.

## 9. Server data: writes

- **Write one `mutationOptions` per write, in a `<name>.mutations.ts` file of its module, or of its
  route's `-` folder while one route uses it, in a code base that keeps one-route flows there
  (section 3)**, beside the queries. `mutationOptions`
  is the twin of `queryOptions` in TanStack Query 5, and a file per role keeps the reads and the
  writes apart ([file-structure.md](../../any-language/file-structure/file-structure.md) section 3).
- **Call `mutate`, and react in its callbacks.** Use `mutateAsync` only when a second write waits
  for the result of the first: `mutate` returns nothing, and `mutateAsync` throws on an error that
  the caller then has to catch (TkDodo; TanStack Query's mutations guide).
- **Invalidate in the mutation's own options, and return the promise.** The `onSuccess` in
  `mutationOptions` returns `invalidateQueries(...)`. The effects on the screen, such as a
  navigation, a closed dialog or a notice, go in the callbacks passed to `mutate`. TanStack Query's
  guide gives the reason: callbacks passed to `mutate` "won't run if your component unmounts
  *before* the mutation finishes", so an invalidation placed there is lost when the user leaves the
  screen. A returned promise is awaited, so "isPending is true until onSuccess is fulfilled": the
  submit button stays disabled until the screen shows fresh data.
- **Invalidate by the narrowest key prefix that covers every read the write changed.** Matching is
  by prefix: `invalidateQueries({ queryKey: invoiceKeys.all })` marks the list and every invoice
  stale. TanStack Query's invalidation guide "prescribes **targeted invalidation,
  background-refetching and ultimately atomic updates**".
- **Write a response into the cache with `setQueryData` only when it is the full updated item**,
  and write it immutably, so the cache never holds a partial item, and every reader sees a new
  reference and renders again. Otherwise invalidate. A payment returns a receipt, not the
  invoice, so the example invalidates.
- **Update optimistically only where the server's answer is predictable.** TkDodo: optimistic
  updates come "with the drawback of having to know exactly what will happen on the server". A
  payment can be declined, so its screen waits for the answer.
- **Leave `retry` off on a mutation.** TanStack Query does not retry a write by default. Keep it so:
  a write that reached the server and lost its answer would run a second time.
- **A mutation's error stays on its form**: `isError` shows a message next to the button. Set
  `throwOnError` only for errors the form cannot show, so that they reach an error boundary
  (TanStack Query's `useMutation` options).
- **Under React Router with actions, writes go through actions.** An action revalidates every
  loader on the page when it completes, and `useFetcher` sends a write that does not navigate. TkDodo
  agrees: "There likely isn't much need to use mutations unless you have more complex scenarios that
  the router actions cannot handle." Add TanStack Query when the screens need what loader
  revalidation lacks: a refetch on window focus, on reconnect or on an interval (one community
  writer's list), or a cache shared across routes with mutations and optimistic updates, which
  TanStack Router's docs name as the case for Query.

## 10. Routing and URL state

- **Each route is one file in `src/routes/`**, and the router plugin turns the folder into a typed
  route tree on every dev run and build. Keep a route file thin: its loader, its title and the
  screen it composes from modules (section 6).
- **Split the code by route** with the plugin's `autoCodeSplitting`: each route's component becomes
  its own chunk, and its loader stays in the main bundle. A route file that exports its `component`
  or its `loader` "will not be code-split" (TanStack Router's docs). What to measure and how far to
  split is [performance.md](../performance/performance.md)'s.
- **Register the router's type once**, in `main.tsx`: `interface Register { router: typeof router }`.
  Every `to`, parameter and search value in a route is then checked by the compiler.
- **Start a route's loader on intent**: `defaultPreload: "intent"` starts it before the click
  (TanStack Router's preloading guide).
- **State that a reload, a shared link or the back button should keep goes in the search params**: a
  filter, a sort, a page number, the open tab. Check it with a schema through the route's
  `validateSearch`; Zod 4 works there without an adapter. TanStack Router calls search params "the
  most powerful state manager in your entire application", and the author of nuqs says to "Treat the
  URL as part of design" (read as a search snippet). Which state a user expects the URL to keep is
  [ux.md](../design/ux.md)'s. The example has no such state.
- **React Router 8 is the point to adapt.** It has three modes, declarative, data and framework,
  and its docs say the question is "how much you want to do yourself". In framework mode
  `app/routes.ts` maps each URL to a route file, and the route types are generated: run
  `react-router typegen && tsc` in CI, as its docs say. Its writes follow the last rule of section 9.

The reference application has no sign-in screen, so the three rules below are not shown in the
example.

- **Guard a route in its `beforeLoad`, and redirect by throwing `redirect()`.** TanStack Router's
  "Authenticated Routes" guide says "The `route.beforeLoad` option allows you to specify a function
  that will be called before a route is loaded", that it "is called before any of its child routes'
  `beforeLoad` functions", and "you can throw a `redirect()` from `beforeLoad`" (read 2026-10-02).
  So one guard on a parent route covers every screen under it. The guard is for the user's
  convenience; access control stays on the server
  ([security.md](../security/security.md) section 2).
- **Hand the session state to the router through its context**, next to the API client and the
  query client, so a guard reads the session it is given and has no input a caller cannot see
  (section 8): the same guide says to pass authentication state "using `router.context` option"
  (read 2026-10-02). How the application learns who is signed in when the cookie is `HttpOnly`: no
  source read says; this practice's choice is one query to the server for the current session,
  read in that guard.
- **On sign-out, call `queryClient.clear()`.** In TanStack Query 5.103 it empties the query cache
  and the mutation cache (read in the installed source, 2026-10-02), so the next person at the same
  browser sees none of the last user's data. That it belongs in the sign-out handler is this
  practice's choice.

## 11. Forms

- **A simple form submits through its mutation.** A simple form has a few fields, one submit and no
  check while the user types. Its `onSubmit` reads `FormData`, parses the values with the module's
  schema and calls `mutate`, and the submit button is disabled while the mutation is pending, so a
  second click sends nothing. react.dev: "Reading form data with `onSubmit` works in every version
  of React"; bulletproof-react's form calls `mutate` and disables its button on `isPending` in the
  same way.
- **React 19's form Actions fit a simple form whose write no query cache and no router action
  owns**: `<form action={fn}>`, `useActionState` for the result, and `useFormStatus` for the pending
  state, called from a component inside the form. Know the caveat first: React 19 resets an
  uncontrolled form after its action, so a "save draft" button empties the fields (React issue
  #29034), and controlled checkboxes are reset too (issue #31695). Under React Router, a form posts
  to its route's action instead (section 9).
- **A complex form uses a form library**: many fields, checks while the user types, fields that
  depend on each other, lists of fields. Use React Hook Form 7 or TanStack Form
  ([libraries.md](libraries.md)), with the same Zod schema as its validator. A server error that
  belongs to no one field goes to `setError('root.serverError', ...)` (React Hook Form's docs). How a
  form reads its values under the React Compiler is [components.md](../components/components.md)'s.
- What a form says, where its errors appear and where the focus goes is
  [ux.md](../design/ux.md)'s and [accessibility.md](../design/accessibility.md)'s.

## 12. Errors and loading

- **Give the router a default pending screen and a default error screen at startup**
  (`defaultPendingComponent`, `defaultErrorComponent`), so a route that defines neither still shows a
  state, never a blank page. React Router's docs set the floor in one line: "All applications should
  export a root error boundary as a minimum."
- **A retry resets the failed query and runs the loader again.** The error screen calls
  `useQueryErrorResetBoundary().reset()`, and its button calls `router.invalidate()`. A failed query
  stays failed until it is reset, so a retry that only renders again shows the same cached error
  (TanStack Query's suspense guide). `router.invalidate()` reloads the route's loader and resets the
  router's error boundaries (TanStack Router's guide to data mutations).
- **A boundary below the route uses `react-error-boundary`.** React has no way to write an error
  boundary as a function component, and react.dev points to this package. It does not catch an error
  thrown in an event handler or in async code; its `useErrorBoundary` hook passes such an error to
  it.
- **When a background refetch fails while data is on screen, keep the data and show one notice.**
  A global `onError` on the `QueryCache` that acts only when `query.state.data !== undefined` shows
  one notice per query (TkDodo, on error handling). The example does not show it.
- **Report errors from the `onCaughtError` and `onUncaughtError` options of `createRoot`.** react.dev
  says the first is called for every error a boundary caught and the second for every error no
  boundary caught; using them as the one place to report is this practice's choice. The reporting
  service is in [libraries.md](libraries.md); [layout-example.md](layout-example.md) section 4 shows
  the options in `main.tsx`.
- What an error screen and a pending screen say, and how a screen reader learns of them, is
  [ux.md](../design/ux.md)'s and [accessibility.md](../design/accessibility.md)'s.

## 13. TypeScript settings

This section owns the compiler settings and the typing rules for the whole project; component
typing is [components.md](../components/components.md) section 3, and the version is
[libraries.md](libraries.md) section 3.

- **Turn on three flags beyond `strict`**, which TypeScript 6.0 turns on by default.
  `noUncheckedIndexedAccess`: a read by index or by key may be `undefined`, so the code has to check
  it. `verbatimModuleSyntax` and `erasableSyntaxOnly` are the next two rules. All three are off by
  default (TypeScript's TSConfig reference, read 2026-10-01), and create-vite's React template
  already sets the last two. The TypeScript team declined to fold `noUncheckedIndexedAccess` into
  `strict`, so you set it by hand.
- **`verbatimModuleSyntax`: a type-only import says `import type`.** Imports are emitted as
  written, so a bundler that strips types never keeps a runtime import by mistake. Add no
  `consistent-type-imports`: the flag already enforces `import type`, and the two can report
  conflicting fixes.
- **`erasableSyntaxOnly`: a file holds only syntax that a tool which strips types can remove.**
  Node runs a `.ts` file by stripping its types, file by file, and cannot run syntax that emits
  code; with the flag the same code runs there and in Vite's build. So `enum`, `namespace` with
  code and constructor parameter properties are compile errors. Write a closed set as a union of
  string literals; when its values are needed at run time, use an `as const` object (TypeScript
  handbook, Enums). The flag is the check: add no lint rule against `enum`.
- **Turn on `switch-exhaustiveness-check` by name in `eslint.config.js` when the code switches over
  a union with no `default`**: it reports a member with no `case`, so a value added to the union
  later cannot pass unhandled; no recommended, strict or stylistic preset turns it on (the `all`
  config does).
- **Write each data type once, as `z.infer<typeof schema>` beside its schema**, so the type cannot
  drift from the schema the API client parses with (section 8). The API client's `request` returns
  `z.infer<TSchema>`, so `queryOptions`, `mutationOptions` and `useSuspenseQuery` infer their types:
  give them no type arguments, because one type argument forces all of them (TkDodo).
- **Leave `exactOptionalPropertyTypes` off.** It breaks the types of libraries not written for it:
  Radix's issue to support it was open with no maintainer reply (read 2026-10-01).
- **Declare `paths` with no `baseUrl`**, as section 5 says.
- The TypeScript version is pinned until typescript-eslint supports TypeScript 7:
  [libraries.md](libraries.md) section 3.

## 14. The server-rendered case

When section 2 sends some routes to a framework that renders on the server, or the whole
application to a framework in single-page mode, the tree keeps its shape, and the adapter moves to
the framework's routes folder. In single-page mode the tree (section 3), state (section 7), server
data (sections 8 and 9) and the components still hold. The framework's own conventions replace the
routes folder and the loaders. No source read states this split; it is this practice's reading of
section 3: the routes folder is where a screen is composed, so the framework's routes folder takes
that place, and the modules and `core/` stay as they are.

- **The framework's routes folder is the adapter.** In Next.js that folder is `app/`. A folder in it
  becomes a public route only when it holds a `page` or a `route` file, and the Next.js docs allow
  keeping `app/` "purely for routing purposes". Keep it so, and put the modules and `core/` beside
  it. In React Router's framework mode, `app/routes.ts` maps each URL to a file under `app/`, so the
  route files stay thin and the modules sit in their own folders under `app/`.
- **Server Functions are public endpoints, and a server runtime is code you patch.** The rules are
  [security.md](../security/security.md) section 8's.
- **`'use client'` marks a boundary in the import graph, not in the render tree**: every file that
  a `'use client'` file imports becomes client code too (react.dev). A module's component that needs
  the browser marks its own file, and what it imports goes to the client with it.
- **A framework with loaders and actions may need no query cache.** TkDodo: with "a mature framework
  like Next.js or Remix that has a good story around data fetching and mutations, you probably don't
  need React Query". The last rule of section 9 says when to add it.

## 15. Common mistakes

Each mistake breaks one rule above. Every good form is the example application's code, and `...`
marks a cut.

### Mistake 1. Server data copied into state (section 7)

**Bad**: the list copies the cached invoices into its own state. From
`src/billing/list-invoices/invoice-list.tsx`, with the imports, the props type and the table cut:

```tsx
export function InvoiceList({ apiClient, today, renderPayLink }: InvoiceListProps) {
  const { data } = useSuspenseQuery(invoicesQueryOptions(apiClient));
  const [invoices] = useState(data);

  if (invoices.length === 0) {
    return <p className="text-muted-foreground">No invoices yet. A new invoice appears here when it is issued.</p>;
  }

  ...
}
```

`useState` reads its argument on the first render only. When the user comes back to the tab after
the stale time, the cache refetches the list and `data` changes, but `invoices` keeps the first
copy: an invoice that someone paid in the meantime still shows "Due" and a pay link. No linter
reports it.

**Good**: the same component reads the cache where it shows the list. The same file, with the same
cuts:

```tsx
export function InvoiceList({ apiClient, today, renderPayLink }: InvoiceListProps) {
  const { data: invoices } = useSuspenseQuery(invoicesQueryOptions(apiClient));

  if (invoices.length === 0) {
    return <p className="text-muted-foreground">No invoices yet. A new invoice appears here when it is issued.</p>;
  }

  ...
}
```

Why it is good: the list has one home, the cache, so every refetch reaches the screen. The fix
removes one line and one import.

### Mistake 2. A barrel file (section 5)

**Bad**: the module gets an `index.ts` that re-exports its files, and the route imports from it.

`src/billing/list-invoices/index.ts`:

```ts
export * from "@/billing/list-invoices/invoice-list.tsx";
export * from "@/billing/list-invoices/invoices.queries.ts";
```

The imports of `src/routes/invoices.index.tsx`:

```tsx
import { createFileRoute, Link } from "@tanstack/react-router";

import { InvoiceList, invoicesQueryOptions } from "@/billing/list-invoices/index.ts";
```

Each name now has two import paths, and an import of one name loads every file the barrel lists, in
the dev server, in the test run and in the build. In the example application Oxlint's
`oxc/no-barrel-file` failed on a barrel in this module: its imports loaded 249 modules, over the
threshold of 100.

**Good**: no `index.ts`, and the route imports each name from the file that holds it. The imports of
`src/routes/invoices.index.tsx`:

```tsx
import { createFileRoute, Link } from "@tanstack/react-router";

import { InvoiceList } from "@/billing/list-invoices/invoice-list.tsx";
import { invoicesQueryOptions } from "@/billing/list-invoices/invoices.queries.ts";
```

Why it is good: each import line names the file, so a reader and a search find the code from it,
and the tools load only the files the route uses.

### Mistake 3. A module that imports another module (sections 5 and 6)

**Bad**: the payment module refreshes the list with the list module's own query options.
`src/billing/pay-invoice/pay-invoice.mutations.ts`:

```ts
import { mutationOptions } from "@tanstack/react-query";

import { invoicesQueryOptions } from "@/billing/list-invoices/invoices.queries.ts";
import { invoiceQueryOptions } from "@/billing/pay-invoice/invoice.queries.ts";
import type { PaymentMethod } from "@/billing/pay-invoice/payment.schema.ts";
import { paymentReceiptSchema } from "@/billing/pay-invoice/payment.schema.ts";
import type { ApiClient } from "@/core/api-client.ts";

export function payInvoiceMutationOptions(apiClient: ApiClient, invoiceId: string) {
  return mutationOptions({
    mutationKey: [...invoiceQueryOptions(apiClient, invoiceId).queryKey, "pay"],
    mutationFn: (method: PaymentMethod) =>
      apiClient.request(`/invoices/${encodeURIComponent(invoiceId)}/payments`, {
        method: "POST",
        body: { method },
        schema: paymentReceiptSchema,
      }),
    // The invalidation sits here, not in the form: a callback passed to `mutate` is dropped
    // when the form unmounts. The promise is returned so the mutation stays pending until
    // every invoice read on screen is fresh (architecture.md section 9).
    onSuccess: (_receipt, _method, _onMutateResult, context) =>
      context.client.invalidateQueries({ queryKey: invoicesQueryOptions(apiClient).queryKey }),
  });
}
```

`pay-invoice` now imports `list-invoices`: a rename in the list breaks the payment, and neither
module can be deleted on its own
([file-structure.md](../../any-language/file-structure/file-structure.md) section 2).
`boundaries/dependencies` fails on such an import; in the example application its message named
the captured folders of both modules.

**Good**: both modules build their keys on a root in `core/` (section 6), so the payment module
imports no other module. The key root moves to `core/invoice.keys.ts`, and the mutation key changes
with it. `src/billing/pay-invoice/pay-invoice.mutations.ts`:

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
    // every invoice read on screen is fresh (architecture.md section 9).
    onSuccess: (_receipt, _method, _onMutateResult, context) =>
      context.client.invalidateQueries({ queryKey: invoiceKeys.all }),
  });
}
```

Why it is good: the payment refreshes every invoice read, the list included, without knowing that
the list exists. The invalidation sits in the options and returns its promise (section 9), and the
comment keeps the next editor from moving it into the form.

### Mistake 4. A relative import (section 5)

**Bad**: the first line of `src/billing/list-invoices/invoice-status-badge.tsx`, written relative to
the file:

```tsx
import type { InvoiceStatus } from "./invoice-status.schema.ts";
```

The line no longer names the module the type comes from, the problem
[file-structure.md](../../any-language/file-structure/file-structure.md) section 7
describes. `no-restricted-imports` fails on it with the message the config gives: "Import by the
absolute path: @/<folder>/<file>."

**Good**: the same line, by its absolute path:

```tsx
import type { InvoiceStatus } from "@/billing/list-invoices/invoice-status.schema.ts";
```

Why it is good: the import line alone names the module and the role the type comes from.

### Mistake 5. A tree named for kinds of code (section 3)

**Bad**: the top of `src/` names kinds of code.

```text
src/
├── main.tsx
├── components/
├── hooks/
├── utils/
├── shared/
├── features/
│   ├── list-invoices/
│   └── pay-invoice/
└── routes/
```

The top of the tree says nothing about what the application does. A change to paying an invoice
spreads over `features/`, `components/` and `hooks/`, and `utils/` and `shared/` collect whatever
nobody placed. Angular's style guide, a frontend owner, says to organise by feature and to "avoid
creating directories like `components`, `directives`, and `services`" (section 3), and `utils` and
`shared` are banned by this library's naming rule
([file-structure.md](../../any-language/file-structure/file-structure.md) section 7). Many React
guides start here: bulletproof-react's top level has `components/`, `hooks/` and `utils/` beside
`features/`. No linter in the example reports it.

**Good**: the top of the example application's tree.

```text
src/
├── main.tsx
├── core/
│   └── ui/
├── billing/
│   ├── list-invoices/
│   └── pay-invoice/
└── routes/
```

Why it is good: the top says the application does billing. Components, hooks and helpers live in
the module that uses them, what no module owns is in `core/`, and shared UI is in `core/ui/`.

## 16. Where the rules stop holding

- **A prototype or a one-screen tool.** Start flat and grow by the steps of section 3.
- **A component library published as a package.** Its entry file is its public API, and its users
  import from it by name. This practice is for applications, as
  [file-structure.md](../../any-language/file-structure/file-structure.md) section 12 says of
  libraries.
- **A framework that owns its layout.** Keep the framework's names for what it owns (section 14).
- **React Router with actions.** Section 9's rules for TanStack Query mutations give way to actions
  until the screens need a query cache.
- **A monorepo of several packages** is outside this practice.
- **Code no change touches** stays as it is until a change edits it
  ([refactoring.md](../../any-language/refactoring/refactoring.md) section 2).

## 17. Review checklist

A question for each of sections 2 to 13, and the red flag that answers it with a no. Section 14
has no row: its rules are security's and the framework's, and a reviewer finds them in
[security.md](../security/security.md). Use this table as the architecture part of your review
template.

| Section | Ask | Red flag |
|---|---|---|
| 2. Format | Does any page need a crawler, a link preview or a fast first paint on a slow device? | Public pages that must be indexed, served as a plain client-rendered app; a server runtime behind a login that uses none of its features |
| 3. The tree | Can I tell each file's kind from its folder? | A business word in `core/ui/`; a router import outside `routes/` and `main.tsx`; a test away from the file it tests; a test in `routes/` with no `routeFileIgnorePattern` for it; a route that imports a `-` folder outside its own folder |
| 4. File names | Does each name say what the file holds and its role? | A name outside `routes/` that is not kebab-case; a role file without its suffix; a name that file-structure.md section 7 bans |
| 5. Imports | Does each import name the file that holds the name, by `@/`? | An `index.ts` that only re-exports; `./` or `../`; a boundary rule turned off for a line |
| 6. Composition | Is every screen that uses two modules composed in its route? | A module that imports another module, names a URL or imports the router |
| 7. State | Is each piece of state on the lowest rung that serves its readers? | Server data in `useState` or a store; a filter a link should carry, held in component state |
| 8. Reads | Does each query have one `queryOptions`, started by the route's loader, and does the client come in as a parameter? | A fetch in an effect; `ensureQueryData` or `prefetchQuery` in new code; a cast where a parse belongs; a module that imports a ready-made client or `core/config.ts` |
| 9. Writes | Does the invalidation sit in the mutation's options and return its promise? | An invalidation in a `mutate` callback; `retry` on a mutation; an optimistic update of a result the server decides |
| 10. Routing | Does a route file only load and compose? | A business rule in a route file; search params read without a schema |
| 11. Forms | Does the form's tool fit its size? | A complex form built by hand with a `useState` per field; an Actions form that must keep its values after a submit |
| 12. Errors | Can every route fail and load without a blank screen? | No default error screen; a retry that does not reset the failed query |
| 13. TypeScript | Are the three flags on, and is TypeScript at the version libraries.md section 3 names? | `exactOptionalPropertyTypes` on; `baseUrl` set; a type argument on a query hook; a hand-written type beside its schema; a `switch` over a union with no `default` and `switch-exhaustiveness-check` off |

## 18. Sources

The owner of the tree, the import direction, one role per file and absolute imports is
[file-structure.md](../../any-language/file-structure/file-structure.md); the sources below are those
of the React rules.

**The application format (section 2)**

1. react.dev, "Creating a React App": https://react.dev/learn/creating-a-react-app (start with a
   framework; Server Components need one).
2. react.dev, "Build a React app from Scratch": https://react.dev/learn/build-a-react-app-from-scratch
   (a build from scratch is "your own adhoc framework").
3. react.dev, "Sunsetting Create React App", 2025-02-14:
   https://react.dev/blog/2025/02/14/sunsetting-create-react-app (frameworks run as SPAs on static
   hosting; fetching in effects causes waterfalls; data dependencies "at the route level").
4. React Router, its pages on modes and on SPA mode: https://reactrouter.com/start/modes ,
   https://reactrouter.com/how-to/spa ; TanStack Start, "SPA mode":
   https://tanstack.com/start/latest/docs/framework/react/guide/spa-mode (the single-page mode of
   each framework).
5. Brad Westfall, React Training, 2025-03-31:
   https://reacttraining.com/blog/react-architecture-spa-ssr-rsc (three serial requests; server
   rendering is not just for SEO).
6. Mark Erikson, on the React community in 2025, 2025-06-13:
   https://blog.isquaredsoftware.com/2025/06/react-community-2025/ (Andrew Clark's quote; SPA share
   by downloads).
7. PBX.IM, on leaving Next.js for Vite, 2026-04-08: https://www.pbx.im/blog/next-js-to-vite (one
   team's move away from a server runtime it did not use).
8. A dev.to post on prerendering 280 pages of a React SPA, 2026-07-22:
   https://dev.to/virdix/prerendering-280-pages-of-a-react-spa-for-seo-what-actually-worked-1inf
   (one team's account).
9. react.dev, "Critical Security Vulnerability in React Server Components", 2025-12-03:
   https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components ;
   Rapid7 on React2Shell:
   https://www.rapid7.com/blog/post/etr-react2shell-cve-2025-55182-critical-unauthenticated-rce-affecting-react-server-components/
   (CVSS 10, CISA's list on 2025-12-05).

**The tree, the names and the imports (sections 3 to 6)**

10. bulletproof-react, "Project Structure":
    https://github.com/alan2207/bulletproof-react/blob/master/docs/project-structure.md (compose
    features at the application level; import files directly, no barrels; its top-level layer
    folders).
11. bulletproof-react, "Project Standards":
    https://raw.githubusercontent.com/alan2207/bulletproof-react/master/docs/project-standards.md
    (the `@/*` alias; kebab-case enforced by `check-file`).
12. Robin Wieruch, "React Folder Structure", updated 2026-05-05:
    https://www.robinwieruch.de/react-folder-structure/ (features do not import each other; code two
    features use is promoted; index files as a public API; tests beside their components).
13. Robin Wieruch, "React Feature Architecture", 2024-11-25:
    https://www.robinwieruch.de/react-feature-architecture/ (composition at the parent level keeps
    fetches parallel).
14. Kent C. Dodds, "Colocation", 2019: https://kentcdodds.com/blog/colocation (code as close to
    where it is relevant as possible; the reason for tests beside their file).
15. Next.js docs, "Project structure", 2026-07-21:
    https://nextjs.org/docs/app/getting-started/project-structure ("unopinionated"; `app/` purely
    for routing; no convention for component file names).
16. Codemzy, on React file structure, 2025-10-02: https://www.codemzy.com/blog/react-file-structure
    (a switch to kebab-case, and why).
17. Vite, "Performance": https://vite.dev/guide/performance (barrels make every file load;
    explicit extensions).
18. Atlassian Engineering, on faster builds after removing barrel files, 2025-06-26:
    https://www.atlassian.com/blog/atlassian-engineering/faster-builds-when-removing-barrel-files
    (the vendor's own numbers).
19. Marvin Hagemeister, on speeding up the JavaScript ecosystem (part 7), 2023:
    https://marvinh.dev/blog/speeding-up-javascript-ecosystem-part-7/ (a synthetic measurement).
20. Vite issue 21966, 2026-03-19: https://github.com/vitejs/vite/issues/21966 (a barrel pulls a
    heavy dependency into a shared chunk).
21. Oxlint, rule `no-barrel-file`: https://oxc.rs/docs/guide/usage/linter/rules/oxc/no-barrel-file.html
    (the place to look for the threshold).
22. TypeScript 6.0 release notes:
    https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html (`#/` subpath
    imports; `baseUrl` deprecated).
23. TypeScript, "Modules reference": https://www.typescriptlang.org/docs/handbook/modules/reference.html
    (`paths` alone crashes at runtime).
24. Node.js, "Packages", subpath imports: https://nodejs.org/api/packages.html (`#/` from 24.14 and
    25.4).
25. Vite 8 announcement and shared options: https://vite.dev/blog/announcing-vite8 ,
    https://vite.dev/config/shared-options.html (`resolve.tsconfigPaths`).
26. shadcn/ui, "Vite": https://ui.shadcn.com/docs/installation/vite ; Next.js, "Installation":
    https://nextjs.org/docs/app/getting-started/installation (the `@/*` alias).
27. ESLint, `no-restricted-imports`: https://eslint.org/docs/latest/rules/no-restricted-imports
    (the patterns that ban relative imports).
28. eslint-plugin-boundaries: https://github.com/javierbrea/eslint-plugin-boundaries ; releases,
    https://github.com/javierbrea/eslint-plugin-boundaries/releases ; the `dependencies` rule,
    https://www.jsboundaries.dev/docs/rules/dependencies/ ; TypeScript support,
    https://www.jsboundaries.dev/docs/guides/typescript-support/ (elements, captured names, the
    rename from `element-types`, the resolver).
29. eslint-plugin-check-file: https://raw.githubusercontent.com/dukeluo/eslint-plugin-check-file/main/README.md
    (file and folder name rules).
30. TanStack Router, "File naming conventions" and "File-based routing" API:
    https://tanstack.com/router/latest/docs/framework/react/routing/file-naming-conventions ,
    https://tanstack.com/router/latest/docs/framework/react/api/file-based-routing (route file names;
    the `-` prefix; the generated tree).
31. TkDodo, "Effective React Query Keys": https://tkdodo.eu/blog/effective-react-query-keys (key
    factories such as `todoKeys`, kept beside their queries; values in the key).

**State (section 7)**

32. Kent C. Dodds, "State Colocation will make your React app faster", 2019:
    https://kentcdodds.com/blog/state-colocation-will-make-your-react-app-faster ; "Application
    State Management with React", 2020:
    https://kentcdodds.com/blog/application-state-management-with-react (the ladder; server cache
    and UI state).
33. TkDodo, "Practical React Query": https://tkdodo.eu/blog/practical-react-query (fetched data is
    not client state).
34. react.dev, "Scaling Up with Reducer and Context":
    https://react.dev/learn/scaling-up-with-reducer-and-context ; "Passing Data Deeply with Context":
    https://react.dev/learn/passing-data-deeply-with-context .
35. Nadia Makarevich, on React state management in 2025, 2025-09-25:
    https://www.developerway.com/posts/react-state-management-2025 (most apps need no state
    library).
36. nuqs, "About": https://nuqs.dev/docs/about (the URL as part of design; read as a search
    snippet).
37. State of React 2025, state management:
    https://2025.stateofreact.com/en-US/libraries/state-management/ (respondents who use no state
    library).

**Server data (sections 8 and 9)**

38. TkDodo, "The Query Options API", 2024-01-17: https://tkdodo.eu/blog/the-query-options-api ;
    "Creating Query Abstractions", 2026-02-23: https://tkdodo.eu/blog/creating-query-abstractions
    (`queryOptions`, not configurable hooks).
39. TkDodo, "React Query as a State Manager", 2021: https://tkdodo.eu/blog/react-query-as-a-state-manager
    (a global `staleTime`).
40. TanStack Query, "Important Defaults", "Query Options", "Suspense", "Prefetching":
    https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults ,
    https://tanstack.com/query/latest/docs/framework/react/guides/query-options ,
    https://tanstack.com/query/latest/docs/framework/react/guides/suspense ,
    https://tanstack.com/query/latest/docs/framework/react/guides/prefetching .
41. TanStack Query, `QueryClient` reference:
    https://raw.githubusercontent.com/TanStack/query/main/docs/framework/react/reference/classes/QueryClient.md
    (`query()`; `ensureQueryData` and `prefetchQuery` deprecated).
42. TanStack Router, "External Data Loading" and "Preloading":
    https://tanstack.com/router/latest/docs/framework/react/guide/external-data-loading ,
    https://tanstack.com/router/latest/docs/framework/react/guide/preloading (the client in the
    router's context; `defaultPreloadStaleTime: 0`).
43. TanStack Query, "Mutations", "Invalidations from Mutations", "Query Invalidation", "Updates from
    Mutation Responses":
    https://tanstack.com/query/latest/docs/framework/react/guides/mutations ,
    https://raw.githubusercontent.com/TanStack/query/main/docs/framework/react/guides/invalidations-from-mutations.md ,
    https://raw.githubusercontent.com/TanStack/query/main/docs/framework/react/guides/query-invalidation.md ,
    https://raw.githubusercontent.com/TanStack/query/main/docs/framework/react/guides/updates-from-mutation-responses.md .
44. TanStack Query, `mutationOptions` and `UseMutationOptions` references:
    https://raw.githubusercontent.com/TanStack/query/main/docs/framework/react/reference/functions/mutationOptions.md ,
    https://raw.githubusercontent.com/TanStack/query/main/docs/framework/react/reference/interfaces/UseMutationOptions.md
    (no retry by default; `throwOnError`).
45. TkDodo, "Mastering Mutations in React Query", 2021:
    https://tkdodo.eu/blog/mastering-mutations-in-react-query ; "Concurrent Optimistic Updates in
    React Query", 2025-04-28: https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query .
46. bulletproof-react, `get-discussions.ts` and `create-discussion.tsx`:
    https://raw.githubusercontent.com/alan2207/bulletproof-react/master/apps/react-vite/src/features/discussions/api/get-discussions.ts ,
    https://raw.githubusercontent.com/alan2207/bulletproof-react/master/apps/react-vite/src/features/discussions/components/create-discussion.tsx
    (invalidation with the options factory inside one feature; a button disabled while pending).
47. TanStack Query discussion 4560: https://github.com/TanStack/query/discussions/4560 (mutations
    under router actions).
48. React Router, "Actions" and "Fetchers": https://reactrouter.com/start/framework/actions ,
    https://reactrouter.com/how-to/fetchers ; Sergio Xavier, on automatic revalidation in Remix:
    https://sergiodxa.com/articles/automatic-revalidation-in-remix (what loader revalidation lacks).
49. TanStack Router, "Data Loading" and "Data Mutations":
    https://tanstack.com/router/latest/docs/framework/react/guide/data-loading ,
    https://tanstack.com/router/latest/docs/framework/react/guide/data-mutations (the router cache's
    limits; `router.invalidate()`).

**Routing, forms and errors (sections 10 to 12)**

50. TanStack Router, "Overview", "Type Safety", "Search Params", "Automatic Code Splitting":
    https://tanstack.com/router/latest/docs/framework/react/overview ,
    https://tanstack.com/router/latest/docs/framework/react/guide/type-safety ,
    https://tanstack.com/router/latest/docs/framework/react/guide/search-params ,
    https://tanstack.com/router/latest/docs/framework/react/guide/automatic-code-splitting .
51. React Router, "Type Safety" and "Routing": https://reactrouter.com/explanation/type-safety ,
    https://reactrouter.com/start/framework/routing (`typegen`; `app/routes.ts`).
52. react.dev, `<form>`, `useActionState`, `useFormStatus`:
    https://react.dev/reference/react-dom/components/form ,
    https://react.dev/reference/react/useActionState ,
    https://react.dev/reference/react-dom/hooks/useFormStatus .
53. React issues 29034 and 31695: https://github.com/facebook/react/issues/29034 ,
    https://github.com/facebook/react/issues/31695 (forms reset after an action).
54. React Hook Form, `setError`:
    https://raw.githubusercontent.com/react-hook-form/documentation/master/src/content/docs/useform/seterror.mdx .
55. React Router, "Error Boundaries": https://reactrouter.com/how-to/error-boundary (a root error
    boundary as a minimum).
56. react.dev, `Component` (error boundaries) and `createRoot`:
    https://react.dev/reference/react/Component , https://react.dev/reference/react-dom/client/createRoot .
57. react-error-boundary README:
    https://raw.githubusercontent.com/bvaughn/react-error-boundary/main/README.md .
58. TkDodo, "React Query Error Handling": https://tkdodo.eu/blog/react-query-error-handling (one
    notice for a background refetch failure).

**TypeScript and the server-rendered case (sections 13 and 14)**

59. TypeScript, TSConfig reference: https://www.typescriptlang.org/tsconfig/ ; create-vite's
    `template-react-ts`:
    https://raw.githubusercontent.com/vitejs/vite/main/packages/create-vite/template-react-ts/tsconfig.app.json .
60. Radix Primitives issue 3535: https://github.com/radix-ui/primitives/issues/3535
    (`exactOptionalPropertyTypes`).
61. Microsoft, "Announcing TypeScript 7.0", 2026-07-08:
    https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/ (no programmatic API yet).
62. react.dev, Server Components, `'use client'`, `'use server'`:
    https://react.dev/reference/rsc/server-components , https://react.dev/reference/rsc/use-client ,
    https://react.dev/reference/rsc/use-server .
63. TkDodo, "You Might Not Need React Query": https://tkdodo.eu/blog/you-might-not-need-react-query .

**Authenticated routes (section 10)**

64. TanStack Router, "Authenticated Routes":
    https://tanstack.com/router/latest/docs/framework/react/guide/authenticated-routes .

**Added on review, 2026-10-03 (sections 3 and 13)**

65. Angular, "Style guide": https://angular.dev/style-guide , read 2026-10-03 (organise by feature;
    "avoid creating directories like `components`, `directives`, and `services`"; unit tests in the
    same directory as the code they test).
66. Nadia Makarevich, on React project structure, 2022:
    https://www.developerway.com/posts/react-project-structure (independent features; independence
    and cheap refactoring as the reasons).
67. Feature-Sliced Design, "Overview": https://feature-sliced.design/docs/get-started/overview (the
    bottom layer is `shared`; no imports within a layer); its v2.1 release, 2024-11-13:
    https://github.com/feature-sliced/documentation/discussions/756 (code no other page reuses stays
    in the page's slice; one user flow spread over several folders is the cost).
68. React's legacy FAQ, "File Structure": https://legacy.reactjs.org/docs/faq-structure.html (no
    longer updated; "don't spend more than five minutes"; a mix of both as projects grow).
69. Josh Comeau, on React file structure, updated 2025-12-03:
    https://www.joshwcomeau.com/react/file-structure/ (folders by type; "real life isn't nicely
    segmented"; one person's experience).
70. TanStack Router's examples, the `src/` listings under
    https://api.github.com/repos/TanStack/router/contents/examples/react/ (start-basic,
    basic-react-query-file-based, large-file-based and others), read 2026-10-03 (code that is not a
    route kept by type or loose; no `-` folder; none of the eight read sets `routeFileIgnorePattern`
    or keeps a test in `routes/`).
71. TanStack Router, "How to test file-based routing":
    https://tanstack.com/router/latest/docs/how-to/test-file-based-routing (route tests in a parallel
    `src/test/routes/` tree); its generator's config:
    https://raw.githubusercontent.com/TanStack/router/main/packages/router-generator/src/config.ts
    (`routeFileIgnorePattern` has no default); discussion 6697, 2026-02-18:
    https://github.com/TanStack/router/discussions/6697 (the plugin writes a route template into a new
    file in `routes/`). Read 2026-10-03.
72. TypeScript 5.8 release notes:
    https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-8.html (what
    `erasableSyntaxOnly` rejects); TypeScript handbook, "Enums":
    https://www.typescriptlang.org/docs/handbook/enums.html (`as const` objects); "Announcing
    TypeScript 6.0", 2026-03-23: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/
    (`strict` on by default).
73. typescript-eslint, `consistent-type-imports` and `switch-exhaustiveness-check`:
    https://typescript-eslint.io/rules/consistent-type-imports/ ,
    https://typescript-eslint.io/rules/switch-exhaustiveness-check/ (reports that conflict with
    `verbatimModuleSyntax`; a missing `case` over a union).
74. TkDodo, "React Query and TypeScript": https://tkdodo.eu/blog/react-query-and-type-script (type
    the fetcher, let the hooks infer; no partial type-argument inference); Zod's API docs:
    https://zod.dev/api (`z.infer`).
75. TanStack Router discussion 3046, 2024-12-19:
    https://github.com/TanStack/router/discussions/3046 (a maintainer points to
    `routeFileIgnorePattern` for tests kept beside routes). Read 2026-10-03.
