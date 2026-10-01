# Libraries for a React application

Which library does which job in a new React application in 2025-2026, and which tools type-check,
lint, format and test it. The rules that use these libraries are in
[architecture.md](architecture.md) and the other practices under `react/`; this file is the
catalogue. Versions move every month, so each version here is a dated reading of the npm
registry's `latest` tag (read 2026-10-01), not a pin: your lockfile pins, and section 12 says what
to re-check and when. Every line that carries a read date is to be distrusted after 2027-04-01 until it is read again; [README.md](README.md), under how to adopt, says how to list those lines.

**Navigation**

- [1. How to read this file](#1-how-to-read-this-file)
- [2. The default stack, one row per job](#2-the-default-stack-one-row-per-job)
- [3. TypeScript](#3-typescript)
- [4. Lint](#4-lint)
- [5. Format](#5-format)
- [6. Tests](#6-tests)
- [7. Package manager and Node](#7-package-manager-and-node)
- [8. What the example was checked with](#8-what-the-example-was-checked-with)
- [9. Usage signals: downloads and surveys](#9-usage-signals-downloads-and-surveys)
- [10. Not by default, and why](#10-not-by-default-and-why)
- [11. What could not be established](#11-what-could-not-be-established)
- [12. When to re-check this file](#12-when-to-re-check-this-file)
- [13. Sources](#13-sources)

## 1. How to read this file

Each row names a job, the default for it, the version read, the alternative and when to switch,
and what to watch for. "When to switch" is filled in only where a source says when the
alternative wins. Where no source says so, the row says that, and section 11 collects those gaps.
A default with no public source behind it is marked as this practice's own choice.

The version column is the registry's `latest` on 2026-10-01. The example application in
[layout-example.md](layout-example.md) was installed a week behind that date and checked with the
versions in section 8. In places it trails this column by a patch, and its Vitest is a major
behind.

Section 9 gives two kinds of usage evidence. Neither one picks a library:

- A weekly download count from npm measures installs. It counts CI runs, mirrors and packages
  that other packages pull in, so it does not count teams or what they chose. `react-scripts`,
  the package of the deprecated Create React App, still had 3.12 million downloads in the week
  read.
- A rank in State of React or State of JS shows what a self-selected group of respondents said.
  The survey calls itself "a snapshot of a specific subset of developers", and libraries were free
  to ask their own users to take part. Read a rank as a hint of direction, never as a market
  share.

The rules for testing and for static checks of a React project are not written yet as practices
of their own. Until they are, this file lists the tools only: what each is for, its version and
what to watch for. It does not say how to write a test or which rules to add beyond the setup
named here.

## 2. The default stack, one row per job

Versions are the registry's `latest`, read 2026-10-01, unless the cell says otherwise.

| Job | Default | Version read | Alternative, and when to switch | Watch for |
|---|---|---|---|---|
| UI library | React (`react`, `react-dom`) | 19.3.0, released 2026-09-09 | none | Server Components need a framework ([architecture.md](architecture.md) section 2). How a component and a hook are written: [components.md](../components/components.md) sections 3 and 6 |
| Compiler | React Compiler (`babel-plugin-react-compiler`), run through `reactCompilerPreset()` from `@vitejs/plugin-react` and `@rolldown/plugin-babel` | 1.0.0, stable since 2025-10-07; `@vitejs/plugin-react` 6.1.1 | the plugin-react README also offers `oxc-transform-react`, a Rust port; react.dev's install page shows only the Babel route, so that route is the default | react.dev says to pin the exact compiler version when test coverage is weak. The compiler skips a component that uses an incompatible library, and the hooks lint names those libraries (see the table and list rows). The memoisation rule: [components.md](../components/components.md) section 7 |
| Build tool | Vite | 8.3.2 | react.dev also names Parcel and Rsbuild; no source read says when either beats Vite | Vite 8 bundles with Rolldown and Oxc and needs Node 20.19+ or 22.12+. `resolve.tsconfigPaths: true` reads the `@/` alias from tsconfig; it is off by default |
| Router, client-rendered app | TanStack Router (`@tanstack/react-router`), with `@tanstack/router-plugin` for file-based routes and code splitting | 1.170.41 | React Router 8 (`react-router` 8.4.0), the point to adapt ([architecture.md](architecture.md) section 10). Its docs say the data mode is for those who want "data features but also want control over bundling, data, and server abstractions", and that the question is "how much you want to do yourself" (the owner's words). No source read says when it beats TanStack Router for a client-rendered app. Its type safety differs between its declarative, data and framework modes | React Router 8 needs Node 22.22+, React 19.2.7+, and Vite 7+ in framework mode; it drops `react-router-dom` and ships as ESM only |
| Framework, for routes a crawler must read | chosen by the format decision in [architecture.md](architecture.md) section 2; react.dev names Next.js and React Router's framework mode | `next` 16.3.8 | TanStack Start (`@tanstack/react-start` 1.168.60); no source read says when it is the better choice. The registry has no `rc` tag, its docs still say "Release Candidate", and its blog has no 1.0 announcement | Next.js 16 made Turbopack its default bundler. A server runtime is one more thing to secure ([security.md](../security/security.md) section 8) |
| Server data | TanStack Query (`@tanstack/react-query`) | 5.104.0 | under React Router, its loaders and actions first, and Query once its features are needed ([architecture.md](architecture.md) sections 8 and 9); RTK Query when the app already runs Redux Toolkit | `ensureQueryData`, `prefetchQuery` and `fetchQuery` are deprecated for `queryClient.query()`, and the reference says they go in the next major. No React v6 exists yet |
| Client state | no library: local state, lifted state, a reducer with context inside a module ([architecture.md](architecture.md) section 7) | none | Zustand 5.0.15 when that ladder reaches a store; Redux Toolkit 2.13.0 when the app already runs it, or when shared state is large, changes often through complex logic, is worked on by many developers and needs its changes traced (the Redux maintainer's criteria) | Zustand under server rendering: never a module-level store, since one store would serve every request. In Zustand 5 a selector that returns a new object fails with "Maximum update depth exceeded" unless wrapped in `useShallow`. A TanStack Query maintainer's advice (2022): export hooks, not the store |
| URL state | the router's typed search params (TanStack Router) | none | nuqs 2.10.1; no source read says when it beats the router's own search params | none noted |
| Forms | simple forms: no library, as [architecture.md](architecture.md) section 11 says; complex forms: React Hook Form 7. The reason for it: its use (68.20 million weekly downloads against 3.95 million for TanStack Form, section 9) and its resolvers, which cover Yup, Zod, AJV, Superstruct and Joi | `react-hook-form` 7.89.0 | TanStack Form 1.33.5; its docs argue for controlled state and for wrapping it in your own components, and no source read compares it with React Hook Form | under the compiler, read a field with `useWatch`, not `watch` (react.dev's lint page). The compiler skips a component that uses it: [components.md](../components/components.md) section 7. Version 8 is in beta (8.0.0-beta.4) |
| Validation | Zod 4 | 4.6.5 | Zod Mini, Valibot 1.5.0 or ArkType 2.2.6. Zod's docs advise regular Zod "unless you have uncommonly strict constraints around bundle size", and offer Zod Mini for that case. Valibot's own comparison claims a much smaller bundle (a vendor's claim about itself). The two statements above were read by a reviewer on 2026-10-02 from the owners' pages (sources 61 and 62). TanStack Router's docs say `validateSearch` accepts Standard Schema libraries without adapters and name Zod v4, Valibot and ArkType, so a later swap among them is cheap (source 63, read 2026-10-01) | Zod 4 moved string formats to the top level (`z.email()`, `z.iso.date()`) and replaced `message`, `invalid_type_error` and `errorMap` with one `error` parameter; the old method forms are deprecated |
| Styling | Tailwind CSS 4, with design tokens in `@theme` ([visual-design.md](../design/visual-design.md) section 3) | 4.3.3 | CSS Modules, built into Vite; no source read says when they beat Tailwind. Tailwind 3.4 when the app must run on browsers below Tailwind 4's floor (Tailwind's upgrade guide) | Tailwind 4 needs Safari 16.4+, Chrome 111+ and Firefox 128+ |
| Components | shadcn/ui on Base UI: the `shadcn` CLI copies component code into the app, built on `@base-ui/react` | `shadcn` 4.21.1, `@base-ui/react` 1.8.0 | React Aria Components 1.21.1 when you want a library whose vendor states and tests its accessibility support, at the cost of not using the shadcn tooling; Radix (`radix-ui` 1.6.7) for code already on it, since it still ships releases; MUI when the team would rather depend on a full styled kit than own copied code | The reason for this default: shadcn/ui's CLI, skill and MCP server are what [designing-with-claude-code.md](../design/designing-with-claude-code.md) section 5 builds on, and Base UI is what that CLI installs for a new project (since July 2026). No accessibility audit of Base UI was found in the sources read. Copied components are your code: an upgrade, or a move off Radix, goes one component at a time (comments on Hacker News, anecdotes). shadcn's standalone `cn` package replaces the copied `lib/utils.ts`. Check copied components for native elements ([accessibility.md](../design/accessibility.md) section 3) |
| Icons | `lucide-react` | 1.49.0 | none compared | none noted |
| Data tables | TanStack Table | 9.2.4 | none compared | the compiler skips a component that uses it: [components.md](../components/components.md) section 7 |
| Long lists | TanStack Virtual | 3.14.13 | none compared | The compiler skips a component that uses it: [components.md](../components/components.md) section 7. No source gives a row count at which virtualising pays, and virtualised rows break find-in-page and screen-reader reading ([performance.md](../performance/performance.md) section 6) |
| Animation | Motion (`motion`, formerly Framer Motion) | 13.5.0 | none compared | import from `motion/react` |
| Dates | date-fns | 4.4.0 | the built-in `Temporal`, once MDN marks it Baseline; on 2026-10-01 MDN says it is "not yet Baseline" | version 5 is in alpha |
| HTTP | the built-in `fetch`, wrapped once in the `ApiClient` class in `core/`, built once in `main.tsx` and handed in ([architecture.md](architecture.md) sections 3 and 8) | none | axios 1.20.0 or ky 2.1.0; no source read argues for either over `fetch`. The default is this practice's choice | none noted |
| Typed API client | an addition to the HTTP row's `ApiClient`, not a second default: openapi-typescript generates TypeScript types from an OpenAPI 3.0 or 3.1 schema, and those types describe the requests and the parameters. Each response is still parsed with its schema in the API client ([architecture.md](architecture.md) section 8) | 7.x (the exact `latest` was not read) | Orval 8 when you also want generated TanStack Query hooks and MSW mocks. No source read compares the two; starting with the one that writes only types is this practice's choice | both need an OpenAPI schema from the backend |
| Error boundaries | `react-error-boundary` | not read | none | React has no way to write an error boundary as a function component, and react.dev points to this package. It does not catch errors in event handlers or async code; its `useErrorBoundary` hook passes those on. The router already gives every route an error screen through `defaultErrorComponent`; use this package for a boundary below a route or outside a router ([architecture.md](architecture.md) section 12) |
| Error reporting | Sentry (`@sentry/react`) | 11.2.0, released 2026-10-01 | no other service compared; Sentry is the one the research read | 11.0 was a major release with breaking changes, which were not read here |
| Dead code | knip | 6.39.0 | none | finds unused files, exports and dependencies; it does not check import direction (section 4). Needs Node 20.19+ or 22.12+ |

Two more libraries belong to other practices, which say when to add them: `web-vitals` 6.2.2
measures the Core Web Vitals of real users ([performance.md](../performance/performance.md) section 3), and
DOMPurify 3.4.16 cleans HTML that has to be rendered as HTML
([security.md](../security/security.md) section 4). Both versions were read 2026-10-01.

## 3. TypeScript

Install TypeScript 6.0 (`"typescript": "~6.0"`), not the registry's `latest`, so that type-aware
linting keeps working: typescript-eslint, which runs those rules, supports TypeScript
`>=4.8.4 <6.1.0`, and TypeScript 7 has no programmatic API for it to call.

| Fact, read 2026-10-01 | Value | What it means here |
|---|---|---|
| Registry `latest` | 7.0.2: the native compiler; 7.0 was released 2026-07-08 | `npm install -D typescript@latest` installs 7, which typescript-eslint does not support |
| Last 6.0 patch | 6.0.3 | the version the example was checked with |
| TypeScript 7's API | "TypeScript 7.0 does not ship with an API. We expect TypeScript 7.1 to ship with a new (and different) API." | tools that call the compiler stay on 6.0 until that API arrives and they adopt it |
| typescript-eslint 8.71.0 | supports `>=4.8.4 <6.1.0`; since 8.65.0 it warns when it finds TypeScript 7 | the reason for the pin |
| create-vite's `react-ts` template | pins `"typescript": "~6.0.2"` | the template makes the same choice |
| Running 6 and 7 side by side | the TypeScript team publishes `@typescript/typescript6` for tools that still need the 6.0 API | allowed: 7 for `tsc` and the editor, 6.0 for typescript-eslint. The simple default is 6.0 for everything, as create-vite does |
| Editors | TypeScript 7 works through the language server protocol; Vue, MDX, Astro and Svelte projects stay on 6.0, and a plain React project is not in that list | an editor on 7 is fine |
| Oxlint's type-aware mode | needs TypeScript 7 | stays off while the pin is 6.0 (section 4) |

The compiler flags beyond `strict` are a rule of [architecture.md](architecture.md) section 13, with the
reason for each. Re-check the pin when TypeScript 7.1 ships its API and typescript-eslint's
supported range includes 7; typescript-eslint's tracking issue #10940 was open on 2026-10-01.

## 4. Lint

Two linters run, in the order Oxlint's docs give: `oxlint && eslint`. Oxlint is the default linter
of create-vite's React template, and here it runs most rules: hooks, the compiler's diagnostics,
accessibility in JSX, import cycles and barrel files. ESLint 10 runs only what Oxlint cannot run on
this stack: the type-aware rules of typescript-eslint, which need TypeScript 6.0 (section 3), and
the import-boundary rule. `eslint-plugin-oxlint`, spread last in the ESLint config, turns off every
ESLint rule that Oxlint already checks, so each problem is reported once. ESLint 9 reached end of
life on 2026-08-06, so the ESLint half is ESLint 10. Both config files are in
[layout-example.md](layout-example.md) section 3.

When you write `.oxlintrc.json`, name the `react`, `jsx-a11y` and `import` plugins in `plugins`,
and turn on `import/no-cycle` and `oxc/no-barrel-file` by name: by default Oxlint loads only its
`eslint`, `typescript`, `unicorn` and `oxc` plugins and the `correctness` category, so a rule that
exists in Oxlint is not yet a rule that runs. Upgrade `oxlint` and `eslint-plugin-oxlint` together,
because the plugin's version tracks Oxlint's and its peer range is `oxlint ~1.86.0`.

Which tool checks what (versions read 2026-10-01; Oxlint 1.86.0, ESLint 10.11.0):

| Check | Tool and rule | Note |
|---|---|---|
| Rules of Hooks, effect dependencies | Oxlint `react/rules-of-hooks`, `react/exhaustive-deps` | the hooks rules sit under `react/`; there is no separate hooks plugin. Set `rules-of-hooks` to `error` by name, as create-vite's config does |
| React Compiler diagnostics | Oxlint: 22 compiler rules in `correctness` (announced 2026-08-18) | Oxlint lacks the compiler's `config` and `gating` checks. `eslint-plugin-react-hooks` 7.1.1 has them and runs on ESLint 10; the example keeps its `recommended` preset in ESLint and lets `eslint-plugin-oxlint` turn off what Oxlint repeats |
| Accessibility in JSX | Oxlint `jsx-a11y` | implements every rule of `eslint-plugin-jsx-a11y`'s `recommended` set. It checks static code only; a rendered page gets axe (section 6) |
| Import cycles, barrel files | Oxlint `import/no-cycle`, `oxc/no-barrel-file` | `no-barrel-file` fires when a file re-exports more modules than its threshold, 100 by default |
| Relative imports | `no-restricted-imports` with patterns; ESLint core has it, and so does Oxlint | the rule that asks for absolute imports belongs to [file-structure.md](../../any-language/file-structure/file-structure.md) section 7 |
| Import direction between folders | `eslint-plugin-boundaries` 7.2.0, rule `boundaries/dependencies` | stays in ESLint: nothing read names it as working under Oxlint's JS plugins, which are in alpha, and an open issue on the plugin asks for docs on it. It reads the `@/` alias through `eslint-import-resolver-typescript`. The plugin's 7.x README writes the rule's entries under `policies`; the older `rules` key and `mode: "folder"` still work in 7.2.0 and print a deprecation warning |
| File and folder names | `eslint-plugin-check-file` 3.3.2 | flat config only from 3.x |
| Type-aware rules | typescript-eslint 8.71.0, the `strictTypeChecked` preset with `projectService: true`, the one the example uses | its docs advise `strictTypeChecked` only when "a nontrivial percentage of its developers are highly proficient in TypeScript"; step down to `recommendedTypeChecked` when that is not true of your team |
| Fast Refresh | Oxlint `react/only-export-components` | create-vite's config sets it to `warn` with `allowConstantExport: true` |
| `eval`, `javascript:` URLs, `dangerouslySetInnerHTML` | Oxlint core rules and `react/no-danger` | which rules and why: [security.md](../security/security.md) sections 3 and 14 |

Oxlint's limits on 2026-10-01:

- It does not type-check and does not format; its docs say "it is not a TypeScript type checker".
- Its type-aware mode needs TypeScript 7 and the `oxlint-tsgolint` package. Oxc called it stable
  on 2026-07-22, and it covers 59 of typescript-eslint's 61 type-aware rules. It stays off while
  TypeScript is pinned to 6.0.
- Its JS plugins, which run ESLint plugins inside Oxlint, are "currently in alpha" and do not run
  type-aware ESLint rules.

ESLint plugins and ESLint 10, by the peer ranges on the registry (read 2026-10-01); the plugins that do not declare ESLint 10 are in section 10:

| Plugin | Version | Declares ESLint 10 | Use here |
|---|---|---|---|
| `typescript-eslint` | 8.71.0 | yes | type-aware rules |
| `eslint-plugin-react-hooks` | 7.1.1 | yes, since 7.1.0 | the compiler checks Oxlint lacks |
| `eslint-plugin-boundaries` | 7.2.0 | yes, by its release notes | import direction |
| `eslint-plugin-check-file` | 3.3.2 | yes (`eslint>=9.0.0`) | file and folder names |
| `eslint-plugin-oxlint` | 1.86.0 | no ESLint peer; its peer is `oxlint ~1.86.0` | turns off what Oxlint already checks |
| `@tanstack/eslint-plugin-query` | 5.104.0 | yes | rules for TanStack Query code, `flat/recommended` preset |
| `eslint-plugin-testing-library` | 7.16.2 | yes | rules for component test files |
| `@vitest/eslint-plugin` | 1.6.27 | yes (open-ended peer) | rules for Vitest test files |
| `eslint-plugin-playwright` | 2.12.0 | yes (open-ended peer) | rules for end-to-end test files |
| `eslint-plugin-import-x` | 4.17.1 | yes | when an import rule is needed that Oxlint lacks |
| `eslint-plugin-react-refresh` | 0.5.7 | yes | only where Oxlint does not check Fast Refresh |
| `eslint-config-prettier` | 10.1.8 | yes (open-ended peer) | optional here: once `eslint-plugin-oxlint` has turned off the duplicates, the ESLint half runs type-aware, import, naming and compiler rules, not style rules. That is an inference from this setup, not an owner statement |

## 5. Format

| Tool | Version, read 2026-10-01 | Status | Use |
|---|---|---|---|
| Prettier | 3.9.9 | stable | the default formatter |
| oxfmt | 0.71.0 | beta since 2026-02-24. Oxc says it passes 100% of Prettier's JavaScript and TypeScript conformance tests (the vendor's own test); Prettier plugins are not supported yet | re-check when it leaves beta |
| Biome | 2.5.15 | stable; one tool that lints and formats | not by default: section 10 |

## 6. Tests

What earns a test is the rule of [what-to-test.md](../../python/testing/what-to-test.md), whose
rules hold in any language; this file does not restate it. Until React has a testing practice of
its own, this practice's minimum is its own choice, built on the rows below: every rule file has a
unit test, as the example's two rule files do; a component with behaviour of its own gets one test
in Vitest Browser Mode, found by role and driven with `user-event`; the network is replaced with
MSW handlers; and each flow the business cannot lose gets one end-to-end path in Playwright. The
reference application holds only the first kind: no component test was written for it.

One line per kind of test. Versions are the registry's `latest`, read 2026-10-01.

| Kind of test | Tool | Version read | What it is for | Watch for |
|---|---|---|---|---|
| Unit | Vitest, in Node | 5.0.3 (5.0.0 released 2026-09-03) | a rule, a schema or a function with no DOM | the example ran Vitest 4.1.11, and this file has not read what 5.0 changed: read its migration notes before you move a config to it. Several test projects in one config use `projects`; `workspace` was deprecated in 3.2 |
| Component | Vitest Browser Mode with a provider package (`@vitest/browser-playwright`), plus Testing Library (`@testing-library/react`) and `@testing-library/user-event` | Testing Library 16.3.3, user-event 14.6.7 | one component in a real browser, found by its role and driven the way a user drives it | Browser Mode is stable since Vitest 4.0. jsdom and happy-dom "only simulate a browser", so their results can be wrong in both directions. Query by role first. `user-event` simulates whole interactions, while `fireEvent` only dispatches events. Running units in Node and components in Browser Mode is one practitioner's split, not a measured result |
| Network, in tests and in development | MSW | 3.0.1 (the docs page read describes 2.x) | intercepts requests at the network level, so the same handlers serve development, tests and demos | none noted |
| End to end | Playwright (`@playwright/test`) | 1.63.0 | a few paths through the whole application, in real browsers | keep them few: in Google's 2017 data, 14% of large tests were flaky against 0.5% of small ones. Use locators and web-first assertions. Playwright's component testing is still experimental |
| Automated accessibility | axe-core through `@axe-core/playwright` | 4.13.0 | finds some common problems on a rendered page | the rest needs a manual pass; what counts as done is in [accessibility.md](../design/accessibility.md) sections 10 and 11. `vitest-axe` is at 0.1.0 and looks unmaintained |
| Async Server Components (framework case) | Playwright | as above | Vitest does not support async Server Components, and Next.js's docs send them to end-to-end tests | synchronous Server and Client Components can still be unit-tested |

## 7. Package manager and Node

| Item | Default | Version read 2026-10-01 | Watch for |
|---|---|---|---|
| Node | 24, the Active LTS line | not a package | 24 moves to maintenance on 2026-10-20, and 26 becomes Active LTS on 2026-10-28. 22 is in maintenance until 2027-04-30. Floors in this stack: ESLint 10 needs `^20.19.0 \|\| ^22.13.0 \|\| >=24`, Vite 8 needs 20.19+ or 22.12+, React Router 8 needs 22.22+ |
| Package manager | pnpm 12, because its install-time protections are on by default; npm 12 is the alternative, and it needs those settings switched on | pnpm 12.8.1; npm 12.2.0, released 2026-09-30 | the two differ in which install-time protections are on by default: build scripts of dependencies, a minimum release age, git and tarball sources. [security.md](../security/security.md) section 10 names each setting and the value to set; this file does not repeat them. The example was installed with npm 10.8 and `--before` (section 8), so neither set of settings was run |

## 8. What the example was checked with

The example application in [layout-example.md](layout-example.md) was type-checked, linted,
unit-tested and built on 2026-10-01; nothing was run in a browser. It was installed with npm's
`--before=2026-09-24`, a one-week release-age cutoff, on Node 20.19 with npm 10.8, so the npm 12
and pnpm 12 settings were not run. The table is a set of versions known to pass those checks
together, not a reason to stay on them.

| Package | Registry `latest`, read 2026-10-01 | Installed and checked |
|---|---|---|
| `react`, `react-dom` | 19.3.0 | 19.3.0 |
| `babel-plugin-react-compiler` | 1.0.0 | 1.0.0 |
| `@vitejs/plugin-react` | 6.1.1 | 6.1.1 |
| `@rolldown/plugin-babel` | not read | 0.2.4 |
| `vite` | 8.3.2 | 8.3.0 |
| `@tanstack/react-router` | 1.170.41 | 1.170.39 |
| `@tanstack/router-plugin` | not read | 1.168.40 |
| `@tanstack/react-query` | 5.104.0 | 5.103.2 |
| `zod` | 4.6.5 | 4.6.5 |
| `tailwindcss`, `@tailwindcss/vite` | 4.3.3 | 4.3.3 |
| `typescript` | 7.0.2 (pinned to `~6.0`, section 3) | 6.0.3 |
| `typescript-eslint` | 8.71.0 | 8.70.1 |
| `eslint` | 10.11.0 | 10.11.0 |
| `eslint-plugin-react-hooks` | 7.1.1 | 7.1.1 |
| `eslint-plugin-boundaries` | 7.2.0 | 7.2.0 |
| `eslint-import-resolver-typescript` | not read | 4.4.5 |
| `eslint-plugin-check-file` | 3.3.2 | 3.3.2 |
| `oxlint`, `eslint-plugin-oxlint` | 1.86.0 | 1.85.0 |
| `vitest` | 5.0.3 | 4.1.11: the example's range `^4.1.11` stops below 5 |
| `web-vitals` | 6.2.2 | 6.2.2 |
| `dompurify` | 3.4.16 (from its release page) | 3.4.16 |

## 9. Usage signals: downloads and surveys

Weekly downloads from npm for 2026-09-23 to 2026-09-29, read 2026-10-01. Section 1 says what they
measure; a package that others pull in, such as `@radix-ui/react-dialog` under shadcn/ui and
`radix-ui`, counts every one of those installs.

| Job | Weekly downloads, in millions |
|---|---|
| Server data | `@tanstack/react-query` 79.64, `swr` 20.77, `@apollo/client` 7.43 |
| Client state | `zustand` 67.15, `redux` 52.54, `@reduxjs/toolkit` 36.48, `jotai` 7.46, `xstate` 5.82, `mobx` 4.66, `valtio` 2.34 |
| Forms | `react-hook-form` 68.20, `formik` 5.42, `@tanstack/react-form` 3.95 |
| Validation | `zod` 359.98, `valibot` 24.33, `yup` 14.31, `arktype` 2.34 |
| Routing | `react-router` 66.82, `@tanstack/react-router` 27.95 |
| Frameworks and build | `vite` 218.56, `next` 71.80, `@tanstack/react-start` 19.98, `react-scripts` 3.12, `@remix-run/react` 0.65 |
| Tests | `vitest` 130.20, `@playwright/test` 78.52, `@testing-library/react` 72.94, `jest` 54.75, `msw` 25.21, `cypress` 7.17 |
| Lint and format | `eslint` 188.02, `prettier` 160.46, `oxlint` 27.30, `@biomejs/biome` 19.62 |
| UI | `tailwindcss` 154.44, `@radix-ui/react-dialog` 87.53, `@emotion/react` 24.12, `@base-ui/react` 18.02, `radix-ui` 17.49, `styled-components` 12.97, `@mui/material` 12.03, `@headlessui/react` 8.27, `react-aria-components` 5.58 |

What the 2025 surveys say. State of React 2025 had 3,760 responses between 2025-11-19 and
2026-01-13; State of JS 2025 had 13,002. The per-library percentages sit in charts the research
tools could not read, so only the text and the response counts are given:

- TanStack Query is not yet the most used data-loading tool but has the highest satisfaction
  (State of React, read as a summary).
- MUI leads use of component libraries, and shadcn/ui is growing and close behind; many
  respondents use no component library (State of React).
- React Hook Form drew 1,964 responses and Formik 1,095. Tailwind drew 2,142, CSS Modules 1,794
  and Sass 1,607, and the same page says CSS-in-JS has declined (State of React).
- 1,271 respondents use no state-management library (State of React).
- Jest is the most used test tool with falling satisfaction, and Vitest is growing fast (State of
  JS).

## 10. Not by default, and why

Each of these is a real option that this practice leaves out of the default set, for a reason a
team may weigh differently.

| Library or tool | What it offers | Why it is not the default |
|---|---|---|
| Create React App (`react-scripts`) | a React setup with no configuration | deprecated for new apps on 2025-02-14 and in maintenance mode with no active maintainers; new installs print "create-react-app is deprecated". react.dev names frameworks first, and Vite, Parcel and Rsbuild for a build from scratch |
| Jest, for a new project | the most used test runner | its ESM support is still "experimental" in Jest 30.5 and needs `--experimental-vm-modules`. In State of JS 2025 its satisfaction is falling while Vitest's use grows fast |
| Runtime CSS-in-JS for new code (styled-components, Emotion) | styles written in JavaScript and injected at run time | styled-components' maintainer put it in maintenance mode on 2025-03-17, naming React's move away from the APIs it relies on as one reason; State of React 2025 says CSS-in-JS has declined. No status was found for Emotion. Existing code keeps working: styled-components 6.5.3 was released 2026-08-15 |
| `eslint-plugin-import` | import rules for ESLint | 2.32.0's peer range stops at ESLint 9; `eslint-plugin-import-x` 4.17.1 is the maintained fork that declares ESLint 10 |
| `eslint-plugin-react`, `eslint-plugin-jsx-a11y` | React rules and JSX accessibility rules for ESLint | neither declares ESLint 10 (7.37.5 and 6.10.2), and ESLint 9 is past end of life; Oxlint's `react` and `jsx-a11y` plugins cover them (section 4) |
| A second boundary tool: dependency-cruiser 18.5.0, Nx's `enforce-module-boundaries`, Sheriff | import rules checked outside ESLint, or across a workspace | `eslint-plugin-boundaries` already runs inside the ESLint this stack has. Nx's rule needs an Nx workspace. Sheriff treats an `index.ts` as a module's public API, which the no-barrel rule of [architecture.md](architecture.md) section 5 rules out |
| Biome as the only linter and formatter | one tool for both jobs, with React rules in its `react` domain | its React Compiler rule is still a nursery (experimental) rule. Its plugins only match code snippets, and the pages read show no rule for import direction, so the boundary check of section 4 has no Biome equivalent in what was read. Its type-aware rules use its own type inference, not the TypeScript compiler, and Biome's own posts put their coverage below typescript-eslint's |
| `@eslint-react/eslint-plugin` | its own React rules, which also run under Oxlint | `eslint-plugin-react-hooks` already carries the compiler rules, and its metadata makes no ESLint 10 statement |
| SWR | data fetching with a cache, in one hook | TanStack Query covers the job, and no source read says when SWR is the better choice |
| Storybook 10.6.1 | stories, and component tests through its Vitest addon | not needed to start: component tests run in Vitest Browser Mode (section 6) |
| Cypress | end-to-end and component tests | Playwright covers end-to-end tests; Cypress's current version came from one summary only |
| `vitest-axe` | axe inside Vitest | at 0.1.0 it looks unmaintained; this stack runs axe through Playwright |
| `@hey-api/openapi-ts` | typed clients from an OpenAPI schema | still 0.x, and 0.99.0 (2026-06-22) carried four breaking changes |
| tRPC | types shared between a TypeScript server and the client | it needs the server to be written with tRPC; this file assumes nothing about the backend |
| `vite-tsconfig-paths` | the `@/` alias in Vite | Vite 8 reads tsconfig `paths` itself with `resolve.tsconfigPaths` |
| Yarn, Bun | package managers | npm and pnpm cover the job, and no source read says when either is the better choice; their install-time settings are compared in [security.md](../security/security.md) section 10 |

## 11. What could not be established

- Survey percentages per library. They sit in charts the research tools could not read, so
  section 9 gives the surveys' text and response counts only.
- When an alternative beats the default. No source read says when Jotai or Valtio beats Zustand,
  when TanStack Form beats React Hook Form, when Ark UI or Headless UI beats Base UI or React Aria,
  when Parcel or Rsbuild beats Vite, when axios or ky beats `fetch`, when React Router beats
  TanStack Router for a client-rendered app, when TanStack Start is the better choice, when CSS
  Modules beat Tailwind, when nuqs beats the router's own search params, or whether Orval or
  openapi-typescript is the better start. Each default rests on its own evidence, not on the
  alternative being worse. For Zod against Valibot, ArkType and Zod Mini, the owners' statements
  are in the validation row of section 2.
- An accessibility audit of Base UI. None was found in the sources read.
- A default for charts or for translations. Recharts, Lingui and next-intl were read for versions
  only, and no comparison was found, so this file names none.
- TanStack Start's status. On 2026-10-01 the registry shows 1.x with no release-candidate tag,
  while the docs still say "Release Candidate" and no 1.0 announcement exists.
- A row count at which virtualising a list pays.
- The exact `latest` of `react-error-boundary` and openapi-typescript.

## 12. When to re-check this file

Read every version again on the day you adopt this file. Beyond that, each line below changes a
row when it happens:

- TypeScript 7.1 ships its API and typescript-eslint's range includes 7 (issue #10940): the pin of
  section 3 moves, and Oxlint's type-aware mode can replace the ESLint half's type-aware rules.
- `eslint-plugin-jsx-a11y` or `eslint-plugin-react` declares ESLint 10.
- oxfmt leaves beta.
- 2026-10-28: Node 26 becomes Active LTS.
- MDN marks `Temporal` as Baseline.
- React Hook Form 8 leaves beta.
- TanStack Start announces 1.0.
- TanStack Query ships its next major, which removes the deprecated loader methods.
- The example moves to Vitest 5.

## 13. Sources

Every version, peer range and download count was read on 2026-10-01. A source marked "read as a
summary" was read through a tool's summary of the page: it is the place to look, not a quote.

### Registry and usage

1. npm registry, `https://registry.npmjs.org/<package>/latest`: every version and peer range in
   the tables unless a row names a release page. pnpm's dist-tags,
   https://registry.npmjs.org/-/package/pnpm/dist-tags: 12 is `latest`, 11 a maintenance line.
2. npm downloads API, `https://api.npmjs.org/downloads/point/last-week/<package>`: the weekly
   counts of section 9.
3. State of React 2025, https://2025.stateofreact.com/en-US/about/: sample size, dates and
   self-selection. Libraries, data loading, component libraries and state management pages under
   https://2025.stateofreact.com/en-US/libraries/: the statements in section 9.
4. State of JS 2025, testing, https://2025.stateofjs.com/en-US/libraries/testing/: Jest and Vitest.

### React, compiler, build and routing

5. React 19.3, https://react.dev/blog/2026/09/09/react-19-3: the version and its date.
6. React Compiler 1.0, https://react.dev/blog/2025/10/07/react-compiler-1: stable date; pin the
   exact version when coverage is weak.
7. React Compiler installation, https://react.dev/learn/react-compiler/installation, and the
   plugin-react README,
   https://raw.githubusercontent.com/vitejs/vite-plugin-react/main/packages/plugin-react/README.md
   (read as a summary): the Babel route and the Rust port.
8. `incompatible-library` lint,
   https://react.dev/reference/eslint-plugin-react-hooks/lints/incompatible-library; Oxc's version of the rule,
   https://oxc.rs/docs/guide/usage/linter/rules/react/incompatible-library.html; TanStack Virtual
   issue #1119, https://github.com/TanStack/virtual/issues/1119: libraries the compiler skips.
9. Build a React app from scratch, https://react.dev/learn/build-a-react-app-from-scratch, and
   Sunsetting Create React App, https://react.dev/blog/2025/02/14/sunsetting-create-react-app.
10. Vite blog, https://vite.dev/blog, and the Vite 8 announcement,
    https://vite.dev/blog/announcing-vite8: Rolldown and Oxc, the Node floor,
    `resolve.tsconfigPaths`.
11. React Router changelog, https://reactrouter.com/changelog; upgrading from v7,
    https://reactrouter.com/upgrading/v7 (read as a summary); modes,
    https://reactrouter.com/start/modes: v8's floors and its three modes.
12. TanStack Router overview, https://tanstack.com/router/latest/docs/framework/react/overview
    (read as a summary), and releases, https://github.com/TanStack/router/releases.
13. Next.js blog, https://nextjs.org/blog: 16.0 with Turbopack as the default.
14. TanStack Start: dist-tags,
    https://registry.npmjs.org/-/package/@tanstack%2Freact-start/dist-tags; docs overview, https://tanstack.com/start/latest/docs/framework/react/overview; blog,
    https://tanstack.com/blog.

### Data, state, forms and validation

15. TanStack Query releases, https://github.com/TanStack/query/releases, and the `QueryClient`
    reference,
    https://raw.githubusercontent.com/TanStack/query/main/docs/framework/react/reference/classes/QueryClient.md
    (read as a summary): no React v6; the deprecated loader methods.
16. RTK Query overview, https://redux.js.org/toolkit/rtk-query/overview, and the Redux FAQ,
    https://redux.js.org/faq/general: when Redux fits.
17. Zustand docs, https://zustand.docs.pmnd.rs/learn/guides/nextjs and
    https://zustand.docs.pmnd.rs/reference/migrations/migrating-to-v5; "Working with Zustand",
    https://tkdodo.eu/blog/working-with-zustand (2022).
18. nuqs, https://nuqs.dev/docs/about (read as a search snippet).
19. React Hook Form releases, https://github.com/react-hook-form/react-hook-form/releases, and
    its compiler discussion, https://github.com/orgs/react-hook-form/discussions/12524 (read as a
    summary): v8 beta; the patterns that still break.
20. TanStack Form, https://tanstack.com/form/latest/docs/overview and
    https://tanstack.com/form/latest/docs/philosophy (read as a summary).
21. Zod 4, https://zod.dev/v4: the API changes.

### UI

22. Tailwind CSS blog, https://tailwindcss.com/blog, and upgrade guide,
    https://tailwindcss.com/docs/upgrade-guide: v4 dates, `@theme`, the browser floor.
23. shadcn/ui changelog, https://ui.shadcn.com/docs/changelog: Base UI as the default, the `cn`
    package.
24. Base UI releases, https://base-ui.com/react/overview/releases; Radix releases,
    https://www.radix-ui.com/primitives/docs/overview/releases; React Aria,
    https://react-aria.adobe.com/.
25. Hacker News thread on shadcn's switch, https://news.ycombinator.com/item?id=48791328: the cost
    of owning copied components (anecdotes).
26. styled-components, https://opencollective.com/styled-components/updates/thank-you:
    maintenance mode and its reasons.
27. Motion for React, https://motion.dev/docs/react: the package and import path.
28. TanStack blog, https://tanstack.com/blog: Table v9.

### Utilities

29. date-fns releases, https://github.com/date-fns/date-fns/releases, and MDN on `Temporal`,
    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Temporal.
30. openapi-typescript, https://openapi-ts.dev; Orval, https://orval.dev; hey-api releases,
    https://github.com/hey-api/openapi-ts/releases.
31. React `Component` reference, https://react.dev/reference/react/Component, and the
    react-error-boundary README,
    https://raw.githubusercontent.com/bvaughn/react-error-boundary/main/README.md (read as a
    summary).
32. Sentry JavaScript releases, https://github.com/getsentry/sentry-javascript/releases.
33. knip, https://knip.dev/.
34. `web-vitals`, https://github.com/GoogleChrome/web-vitals; DOMPurify releases,
    https://github.com/cure53/DOMPurify/releases.

### TypeScript

35. Announcing TypeScript 7.0,
    https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/: no API in 7.0, the
    side-by-side 6.0 package, editor support.
36. typescript-eslint, https://typescript-eslint.io/users/dependency-versions and
    https://typescript-eslint.io/users/configs; issue #10940,
    https://github.com/typescript-eslint/typescript-eslint/issues/10940.
37. create-vite's `react-ts` template,
    https://raw.githubusercontent.com/vitejs/vite/main/packages/create-vite/template-react-ts/package.json
    and its `_oxlintrc.json`: the TypeScript pin and the default linter config.

### Lint

38. ESLint version support, https://eslint.org/version-support/ (read as a summary), and ESLint
    v10.0.0, https://eslint.org/blog/2026/02/eslint-v10.0.0-released/.
39. Oxlint: overview, https://oxc.rs/docs/guide/usage/linter.html; config,
    https://oxc.rs/docs/guide/usage/linter/config.html; plugins,
    https://oxc.rs/docs/guide/usage/linter/plugins.html; type-aware linting,
    https://oxc.rs/docs/guide/usage/linter/type-aware.html and
    https://oxc.rs/blog/2026-07-22-type-aware-linting-stable; JS plugins,
    https://oxc.rs/docs/guide/usage/linter/js-plugins.html; React Compiler support,
    https://oxc.rs/blog/2026-08-18-react-compiler-support.html; migrating from ESLint,
    https://oxc.rs/docs/guide/usage/linter/migrate-from-eslint.html; the rules `no-barrel-file`,
    `no-cycle` and `no-restricted-imports` under https://oxc.rs/docs/guide/usage/linter/rules/.
    Several pages were read as summaries.
40. eslint-plugin-oxlint README,
    https://raw.githubusercontent.com/oxc-project/eslint-plugin-oxlint/main/README.md (read as a
    summary): the `oxlint && eslint` order and `buildFromOxlintConfigFile`.
41. eslint-plugin-jsx-a11y README,
    https://raw.githubusercontent.com/jsx-eslint/eslint-plugin-jsx-a11y/main/README.md, and Oxc's
    jsx-a11y rule folder,
    https://api.github.com/repos/oxc-project/oxc/contents/crates/oxc_linter/src/rules/jsx_a11y
    (both read as summaries): Oxlint's coverage of `recommended`.
42. eslint-plugin-react-hooks changelog,
    https://github.com/facebook/react/blob/main/packages/eslint-plugin-react-hooks/CHANGELOG.md:
    ESLint 10 support from 7.1.0.
43. eslint-plugin-boundaries releases,
    https://github.com/javierbrea/eslint-plugin-boundaries/releases; its TypeScript guide,
    https://www.jsboundaries.dev/docs/guides/typescript-support/; issue #431,
    https://github.com/javierbrea/eslint-plugin-boundaries/issues/431.
44. eslint-plugin-check-file README,
    https://raw.githubusercontent.com/dukeluo/eslint-plugin-check-file/main/README.md.
45. eslint-plugin-import releases, https://github.com/import-js/eslint-plugin-import/releases, and
    the import-x README,
    https://raw.githubusercontent.com/un-ts/eslint-plugin-import-x/master/README.md.
46. dependency-cruiser releases, https://github.com/sverweij/dependency-cruiser/releases; Nx,
    https://nx.dev/docs/features/enforce-module-boundaries; Sheriff,
    https://github.com/softarc-consulting/sheriff.
47. TanStack Query ESLint plugin,
    https://tanstack.com/query/latest/docs/eslint/eslint-plugin-query.

### Format

48. Oxfmt beta, https://oxc.rs/blog/2026-02-24-oxfmt-beta.html.
49. Biome linter, https://biomejs.dev/linter/; domains, https://biomejs.dev/linter/domains/; Biome
    v2, https://biomejs.dev/blog/biome-v2/.

### Tests

50. Vitest 5, https://vitest.dev/blog/vitest-5; Vitest 4, https://vitest.dev/blog/vitest-4;
    Browser Mode, https://vitest.dev/guide/browser/why; projects,
    https://vitest.dev/guide/projects.
51. Testing Library query priority, https://testing-library.com/docs/queries/about/#priority;
    React Testing Library, https://testing-library.com/docs/react-testing-library/intro/;
    user-event, https://testing-library.com/docs/user-event/intro/.
52. MSW, https://mswjs.io/docs/.
53. Playwright release notes, https://playwright.dev/docs/release-notes; best practices,
    https://playwright.dev/docs/best-practices; accessibility testing,
    https://playwright.dev/docs/accessibility-testing.
54. "Where do our flaky tests come from?",
    https://testing.googleblog.com/2017/04/where-do-our-flaky-tests-come-from.html: flakiness by
    test size.
55. "Vitest Browser Mode vs Playwright", https://www.epicweb.dev/vitest-browser-mode-vs-playwright:
    one practitioner's split of unit, component and end-to-end tests.
56. Jest and ECMAScript modules, https://jestjs.io/docs/ecmascript-modules.
57. Next.js testing with Vitest, https://nextjs.org/docs/app/guides/testing/vitest: async Server
    Components go to end-to-end tests.
58. Storybook Vitest addon,
    https://storybook.js.org/docs/writing-tests/integrations/vitest-addon, and Cypress component
    testing, https://docs.cypress.io/app/component-testing/get-started.

### Package manager and Node

59. Node.js release schedule, https://github.com/nodejs/release: the LTS dates.
60. npm 12 changelog, https://docs.npmjs.com/cli/v12/using-npm/changelog, and npm releases,
    https://github.com/npm/cli/releases (read as a summary): 12.0 GA and 12.2.0.

### Added on review, 2026-10-02

61. Zod, "Zod Mini", https://zod.dev/packages/mini: regular Zod unless the bundle-size limit is
    uncommonly strict; Zod Mini for that case. Read by a reviewer on 2026-10-02.
62. Valibot, "Comparison", https://valibot.dev/guides/comparison/: Valibot's own claim of a much
    smaller bundle (a vendor's claim). Read by a reviewer on 2026-10-02.
63. TanStack Router, "Type Safety" and "Search Params", https://tanstack.com/router/latest/docs/framework/react/guide/type-safety and https://tanstack.com/router/latest/docs/framework/react/guide/search-params: `validateSearch` accepts Standard Schema libraries; Zod v4, Valibot, ArkType and Effect Schema work without adapters (read 2026-10-01 in the research run).
