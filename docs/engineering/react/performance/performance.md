# Performance rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. What fast means](#2-what-fast-means)
- [3. Measuring](#3-measuring)
- [4. The order of work](#4-the-order-of-work)
- [5. Loading](#5-loading)
- [6. Runtime](#6-runtime)
- [7. The server-rendered case, in brief](#7-the-server-rendered-case-in-brief)
- [8. SEO, in brief](#8-seo-in-brief)
- [9. Common mistakes](#9-common-mistakes)
- [10. Where the rules stop holding](#10-where-the-rules-stop-holding)
- [11. Review checklist](#11-review-checklist)
- [12. Sources](#12-sources)

## 1. Purpose and the one rule

This file is for everyone who builds or reviews a React application: people and AI agents alike.
Read it before you change how a screen loads its code, its data, its images or its fonts, before
you add a dependency to the first screen, and when a field metric fails.

Every line here that carries a read date is to be distrusted after 2027-04-01 until it is read
again; the README's "How to adopt" says how to list those lines.

It covers what fast means, how to measure it, the order of work, loading, runtime, the
server-rendered case and, in brief, search. Other practices own the rest. The application format,
where state lives, server data and routing are [architecture.md](../architecture/architecture.md) sections 2, 7, 8
and 10. How one component is written, the compiler and memoisation are
[components.md](../components/components.md) sections 2 to 8. Which tool, at which version, is
[libraries.md](../architecture/libraries.md) section 2. Every response header other than caching
is [security.md](../security/security.md) section 5, and accessibility is
[accessibility.md](../design/accessibility.md). The examples are TypeScript and HTML for the
billing screens of `Acme Corp`; [performance-example.md](performance-example.md) shows the whole
setup in one application.

The one rule: **measure on real users, then fix the largest part of the metric that fails.**

Why it matters:

- A laptop on office Wi-Fi is not your users' phone. "Only field measurement can accurately
  capture the complete picture" (web.dev); a lab run is one device on one network.
- No source has measured an order of work that fits every application (section 4). The metric
  that fails in your own field data is the order.
- A fix to a small part moves the metric little. In one practitioner's demo application, React's
  work was about 50 ms of a 650 ms LCP, so halving it gained little (Nadia Makarevich, 2025).

Each number below names its source, and a field number names its percentile; the dates are in
section 12. A figure that is modelled, measured by a vendor on its own product, or measured by
one practitioner says so.

## 2. What fast means

Google's three Core Web Vitals are the shared definition of fast. Each is read at the 75th
percentile of visits, mobile and desktop apart: a route passes when three visits in four are good.

| Metric | What it measures | Good | Poor | Source |
|---|---|---|---|---|
| LCP, Largest Contentful Paint | when the largest image or text block of the first screen is drawn | 2.5 s or less | over 4.0 s | web.dev, updated 2025-09-04 |
| INP, Interaction to Next Paint | from a click, a tap or a key press to the next frame drawn; roughly the slowest interaction of the visit; scroll and hover do not count | 200 ms or less | over 500 ms | web.dev, updated 2025-09-02 |
| CLS, Cumulative Layout Shift | the largest burst of layout shifts the user did not cause (gaps under 1 s, at most 5 s long) | 0.1 or less | over 0.25 | web.dev, updated 2023-04-12 |

Three more numbers explain a failing vital. They are diagnostics, not goals.

| Number | What it shows | Good | Poor | Source |
|---|---|---|---|---|
| TTFB, Time to First Byte | how long the server and the network take to start the HTML | 0.8 s or less | over 1.8 s | web.dev, 2025-11-18 |
| FCP, First Contentful Paint | when the first text or image is drawn | 1.8 s or less | over 3.0 s | web.dev, 2023-12-06 |
| TBT, Total Blocking Time | lab only: how long long tasks block the main thread during load | a lab stand-in for INP, "not a substitute" | | web.dev, 2024-10-31 |

Field data is what real users got, collected in their browsers: by your own code (real-user
monitoring, RUM) or by Chrome for its public data set, the Chrome UX Report (CrUX). Lab data is
one run on one machine: a Lighthouse report, a DevTools trace. Field data decides whether a route
passes. Lab data finds the cause and catches a regression before release; Lighthouse cannot
measure INP at all, because no one interacts with the page (web.dev).

What the public data set does not see:

- **A product behind a login.** CrUX holds only public pages, and only origins with enough
  visitors (Chrome for Developers). Such a product has no public field data and must collect its
  own (section 3).
- **Route changes inside a single-page application.** A route change loads no document, so LCP
  covers the first screen of a visit only (DebugBear, 2025). Chrome measures these "soft
  navigations" from version 151, on by default since 2026-07-28, but how CrUX will report them is
  "still to be determined" (Chrome for Developers, updated 2026-09-02; read 2026-10-01).
- **Browsers other than Chrome.** CrUX is Chrome only.
- **Users who left.** "Lost users do not show up in usage-based statistics" (Alex Russell,
  2025-11-24): a route that drove people away looks better in field data than it was.

For scale, from CrUX data of July 2025 in the Web Almanac: 48% of origins passed all three
vitals on mobile and 56% on desktop. On mobile, LCP was the vital most often missed: 62% of
origins good, against 77% for INP and 81% for CLS.

## 3. Measuring

### Field metrics from your own users

- **Report LCP, INP and CLS from every visit to your own backend, with Google's `web-vitals`
  library**, so the application has field data even where CrUX has none (section 2).
- **Import from `web-vitals/attribution`**, so each value arrives with what caused it and a
  failing value can be split into its parts (section 4). The attribution build costs about
  1.5 KB more than the plain one (web-vitals README, read 2026-10-01). The example sends one
  field of it, `target`, the element the value comes from; the full attribution object is not
  sent, so a part-by-part split of a failing metric needs more fields added to the report.
- **Pass `reportSoftNavs: true`**, so each route change is measured as a navigation of its own;
  without it only the first screen of a visit is measured. It needs `web-vitals` 6 or newer and
  works in Chromium 151 and newer; other browsers measure the first screen only (read
  2026-10-01).
- **Read each metric at the 75th percentile, per route and per device class**, the way the
  thresholds are set: an average hides the slowest quarter of visits. The example's report
  carries `viewportWidthPx`, and the backend groups visits into device classes by that width; the
  report holds no other device field.
- **When an interaction waits for the network, also report the time from the interaction to its
  result.** INP stops at the next paint, so a spinner drawn at once passes INP while the user
  still waits (web.dev).
- **When INP fails and the attribution does not name the cause, look at Long Animation Frames**:
  the API names the scripts that ran in a frame slower than 50 ms. Chrome and Edge 123 and newer
  only (read 2026-10-01).

[performance-example.md](performance-example.md) shows a reporter that does the first three.
Which version of `web-vitals` to install is [libraries.md](../architecture/libraries.md)
section 2.

### The tools

A lookup table. The versions in use are in [libraries.md](../architecture/libraries.md)
sections 2 and 8; the facts here were read on 2026-10-01.

| Tool | Use it for | Watch for |
|---|---|---|
| Chrome DevTools, Performance panel | a trace of one load or one interaction: long tasks, layout, paint. Since the October 2026 DevTools release (Chrome 153 and 154), its Insights cover soft navigations | throttling "is relative to your computer's capabilities": press Calibrate under Capture settings, CPU, to get low-tier and mid-tier presets for your machine instead of a fixed 4x |
| React Performance Tracks (React 19.2 and newer) | Scheduler and Components tracks inside that trace, so React's work sits next to the browser's | everything shows in a development build; in a profiling build only the Scheduler track and `<Profiler>` subtrees; nothing in production |
| `<Profiler>` | the render time of one tree, from code | off in the production build by default. Josh Comeau warns that its milliseconds are not "trustworthy" as absolute time: compare two runs, and confirm in a production build on slow hardware |
| Lighthouse | a lab run by hand or in CI: LCP, CLS, TBT | no INP. Version 13 replaced sixteen audits with insights and removed `offscreen-images`, `preload-fonts` and `uses-rel-preload`, so a check that read those audits no longer runs (release notes and a search snippet of the Chrome blog) |
| A bundle analyser: rollup-plugin-visualizer, vite-bundle-analyzer, Sonda | what a chunk holds and why a dependency is in it | rollup-plugin-visualizer lists Rolldown, Vite 8's bundler, as a supported peer; Sonda reads source maps |
| Chrome DevTools MCP | lets a coding agent record a trace (`performance_start_trace`) and read it, with CrUX data merged in | it collects usage statistics by default, and the agent can read any data in that browser. Run it in a browser profile that holds nothing private (this practice's choice; the owner only warns) |
| size-limit | a CI gate on the size, and the run time, of the built files; `--why` explains a growth | |
| Lighthouse CI | a CI gate on lab scores | whether it is still maintained was not confirmed |

What an analyser finds can be large. In one practitioner's Vite application, fixing one wildcard
import of a component library took the bundle from 5,322 kB to 878 kB (Nadia Makarevich, "Bundle
Size Investigation"). That study measured size only, not LCP or INP.

### Budgets and a size gate

**Set a JavaScript budget for the first screen, and fail the CI job when a build passes it**, so
a growth shows in the pull request that causes it, not weeks later in the field data.

No budget has been measured against field metrics. The one public figure is a model: Alex
Russell's budgets for 2026 assume a 75th-percentile phone (a Samsung Galaxy A24 4G), 9 Mbps down
and 100 ms round trips. For a page to load in 3 seconds on it, he allows about 0.3 MiB of
JavaScript on a page that is mostly content (2.0 MiB in all), and about 0.62 MiB on a page that is
mostly JavaScript (1.2 MiB in all). For a 5-second load the figures are 0.57 MiB and 1.15 MiB
(infrequently.org, 2025-11-24). The figures are bytes sent over the network, so compressed
(gzip or Brotli), not the size on disk; "in all" means every resource on the critical path of the
page (HTML, CSS, fonts, images and JavaScript together). For a client-rendered application, start
from the row for a page that is mostly JavaScript: 0.62 MiB at 3 seconds. Replace it once your
own field data shows your users' devices. For comparison, the median mobile page in the 2025 Web Almanac sent
646 KB of compressed JavaScript.

Vite warns when one chunk passes 500 kB before compression (`build.chunkSizeWarningLimit`). A
warning fails nothing, so it is not a gate.

Check: a pull request that pushes the first screen past its budget turns the CI job red.

## 4. The order of work

No source has measured an order of performance work that fits every application (read
2026-10-01). Vercel's "React Best Practices" (2026-01-14) puts request waterfalls and bundle size
first and re-renders fifth of eight, and cites no measurement for that order. web.dev's
performance course follows the loading path. web.dev's list of the most effective fixes ranks
them per metric, with HTTP Archive data, and is not about React. So the order comes from your own
field data:

1. Find the metric that fails at the 75th percentile, per route and device class (section 3).
2. Split it into its parts: LCP into four (section 5), INP into three (section 6), CLS into the
   shifts and the elements that moved. The attribution build gives the split in the field, once the report carries the
   fields (the example sends `target` only); a lab trace on a calibrated slow CPU gives the
   detail.
3. Fix the largest part, and only that.
4. Read the field metric again after the release, over a window as long as the first one.

Where to look first, once you know which metric fails (web.dev, October 2024):

| Fails | Look first at | The data behind it |
|---|---|---|
| LCP | whether the LCP resource is in the first HTML, so the browser finds it early; a CDN for TTFB; the back/forward cache for instant back navigations | 73% of mobile pages have an image as their LCP element, and 35% of those images are not in the first HTML |
| INP | long tasks that do not yield; JavaScript the page does not need; large rendering updates | |
| CLS | content with no explicit size; the back/forward cache; animations of layout properties | 66% of pages have at least one image with no size |

React re-renders are often the small share: developers "tend to overestimate how expensive
re-renders are" (Josh Comeau). They are not always small: in one practitioner's test, one
interaction took 130 ms, 90 ms with the compiler, and close to 0 ms after a fix by hand
(section 6). Work on React's rendering when the trace of a failing interaction shows React's
render inside the long task.

Check: a pull request that claims a performance gain names the metric it fixes, with its
percentile, its source and its date, and says when the field value after release will be read.

## 5. Loading

### The LCP element and its four parts

LCP has four parts (web.dev): the time to first byte; the resource load delay, from the first
byte until the LCP resource starts to download; the resource load duration; and the element
render delay, from the end of that download until the element is drawn. On a good page web.dev
expects about 40% in the first byte, about 40% in the download, and under 10% in each delay.

In a client-rendered application the LCP element is often text that exists only after the entry
chunk runs and the screen's data arrives, so the render delay is the large part. A smaller entry
chunk, a data request that starts in the route loader, and prerendering for public pages
(section 7) shorten it. This is this practice's reading of web.dev's four parts for a
client-rendered application; no owner states it.

### Images

- **Never put `loading="lazy"` on the LCP image, and give it `fetchpriority="high"`**, so the
  browser starts the download at once and ahead of other images (web.dev). `fetchpriority` is
  Baseline newly available since 2024-10-29: Chrome and Edge 103, Safari 17.2, Firefox 132 (read
  2026-10-01).
- **Set `width` and `height` on every image to its intrinsic size, with `max-width: 100%` and
  `height: auto` in CSS**, so the browser reserves the box from the aspect ratio before the file
  arrives and nothing below it moves (web.dev).
- **Give an image shown at several widths a `srcset` and a `sizes`**, so a phone downloads the
  small file (web.dev).
- **Serve AVIF**: smaller files than JPEG or WebP at the same perceived quality, in Chrome since
  2020, Firefox since 2021 and Safari since 2022 (web.dev, 2023).
- **Lazy-load images below the first screen only**, with `loading="lazy"`, so they do not compete
  with what the user sees first. It is Baseline widely available (read 2026-10-01).

Section 9 shows the first two as pairs of a mistake and its fix.

Check: before you merge a change to a route's first screen, name its LCP element and confirm it
carries no `loading="lazy"`.

### Fonts

- **Serve fonts as WOFF2 only**: "WOFF2 is now supported everywhere" (web.dev, 2022).
- **Choose `font-display` on purpose**: `optional` when a stable layout matters most (the browser
  waits about 100 ms, then keeps the fallback, and nothing shifts); `swap` when the text must
  show at once and the brand font must replace it, which needs the font delivered early (web.dev).
- **Preload only the font the first screen draws, with `crossorigin`.** Without `crossorigin` the
  preload is wasted and the font is fetched a second time, and every preload takes bandwidth from
  something else (web.dev).
- **Match the fallback font's metrics** with `size-adjust`, `ascent-override`, `descent-override`
  and `line-gap-override` in its `@font-face`, so the swap to the web font does not move the text
  (Chrome for Developers, 2023).

Whether to host fonts yourself or load them from a font service: web.dev finds the difference
"less clear cut" in practice than on paper, so this practice sets no rule.
[performance-example.md](performance-example.md) shows a font preload.

### Caching and compression

- **Put a hash of the content in the name of every built asset, and cache it for a year:
  `Cache-Control: max-age=31536000`.** A new build changes the name, so a returning user
  downloads only what changed. `immutable` may be added; some browsers ignore it (web.dev).
- **Serve the HTML with `Cache-Control: no-cache` and an `ETag` or `Last-Modified`**, so the
  browser asks every time, gets a short `304` when nothing changed, and sees a new deploy at once.
- **Never send `Cache-Control: no-store` on a page's HTML**: browsers then keep the page out of
  the back/forward cache (web.dev).
- **Compress text with Brotli rather than gzip**: web.dev's table shows Brotli smaller on every
  file it tested.
- **Serve from a CDN**, so the first byte comes from a server close to the user (web.dev).

How much this moves LCP, in one practitioner's synthetic demo: a CDN cut LCP from 960 ms to
640 ms for a client far from the server, and cache headers cut a repeat visit's LCP from 1.2 s
to 650 ms (Nadia Makarevich, 2025-01-21). The other headers a static host sends are
[security.md](../security/security.md) section 5.

### Resource hints

- **`preconnect` only to an origin the first screen uses at once, and to few of them**: the
  browser closes a connection it does not use within 10 seconds. A font origin needs
  `crossorigin` on the hint, or only the DNS lookup happens (web.dev).
- **`preload` only a resource the browser finds late**, such as a font named in CSS or an image
  set from script, and always set `as`. "If too many resources are prioritized, effectively none
  of them are" (web.dev).

Vite writes a `<link rel="modulepreload">` for each chunk the entry needs (`build.modulePreload`,
on by default in Vite 8), so the application's own code needs no hint by hand.

### The back/forward cache

**Never listen to the `unload` event; use `pagehide`, and on `pageshow` with `event.persisted`
refresh what may be stale.** The back/forward cache makes back and forward instant, and web.dev
calls this its most important rule: "never use the `unload` event. Ever!" Chrome is moving to
deprecate the event (web.dev, updated 2026-07-02).

### Code splitting

- **Split the code by route, through the router**, so a user downloads the code of the screens
  they open. TanStack Router's `autoCodeSplitting: true` puts each route's component, error,
  pending and not-found components in a chunk of their own and keeps the loader in the main
  chunk: "The loader is already an asynchronous boundary, so you pay double" if it is split.
  React Router splits route modules on its own in framework mode, and takes a `lazy` property per
  route in data mode (React Router 8.4 docs, read 2026-10-01). Which router to use is
  [architecture.md](../architecture/architecture.md) sections 2 and 10.
- **Use `lazy` for a heavy part of a screen that not every visit opens**, such as a chart behind
  a tab. Call `lazy` at the top level of a module, never inside a component: a call inside a
  component makes a new component type on every render, and React resets its state each time.
  Put the lazy component, or a parent, inside `<Suspense>` (react.dev). Section 9 shows the pair.
- **Do not write barrel files to shrink the bundle.** A barrel file costs time in development and
  tests, not in the production bundle; the rule and its evidence are
  [architecture.md](../architecture/architecture.md) section 5.
- **Keep Vite's default `build.target`** unless your users run older browsers. In Vite 8.3.1 it is
  Baseline Widely Available as of a date fixed for each major version: Chrome and Edge 111,
  Firefox 114, Safari 16.4 (read 2026-10-01). A lower target rewrites modern syntax into longer
  code for browsers that may never visit.
- **Reload the page on `vite:preloadError`.** After a deploy the host may delete the old chunks,
  and a tab opened before it then asks for a chunk that is gone (Vite docs). The listener goes in
  `src/main.tsx`:

  ```ts
  // A deploy removed the chunks this open tab still points to. A reload fetches the new
  // index.html, which points to the new chunks (Vite, "Load error handling").
  window.addEventListener("vite:preloadError", () => {
    window.location.reload();
  });
  ```

- **Split chunks by hand only when an analyser shows a reason**, such as a large library that
  changes less often than your code. In Vite 8 the option is
  `build.rolldownOptions.output.codeSplitting.groups`; `build.rollupOptions` is a deprecated alias
  and `advancedChunks` is the old name (read 2026-10-01).
- **Prefer libraries that ship ES modules.** Tree shaking "relies on the static structure of
  ES2015 module syntax" (webpack docs); in one practitioner's application, replacing a CommonJS
  build of a utility library cut the bundle from 878 kB to 813 kB (size only).

### Data: waterfalls and prefetch

A waterfall is a request that starts only after another one finished. A component that holds its
own request and sits in a split chunk adds one more: first the chunk, then the request (TanStack
Query, "Request waterfalls"). Where server data lives, and how the router and the query cache are
wired, is [architecture.md](../architecture/architecture.md) sections 6 and 8.

- **Start a screen's data in its route loader**, so the request runs while the route's code
  downloads and never waits for a component to render.
- **Prefetch on intent at the router level**: when a link is hovered or focused, the router runs
  the target's loader, so the data is on its way before the click (TanStack Query,
  "Prefetching").
- **Call `queryClient.query()` in a loader.** TanStack Query's guide calls `prefetchQuery` and
  `ensureQueryData` "now deprecated", to be removed in the next major version (read 2026-10-01).
- **Start a screen's queries together.** Several `useSuspenseQuery` calls in one component run
  one after the other; use `useSuspenseQueries`, or start all of them in the loader.
- **Set a global `staleTime` above zero.** The default, 0, marks every result stale at once, so
  each mount, window focus and reconnect asks the server again (TanStack Query, "Important
  defaults"). How stale a screen may be is a product decision; the example uses one minute.

## 6. Runtime

### INP and its three parts

web.dev splits an interaction into three parts, and each has its own fix:

| Part | What it is | Fix it with |
|---|---|---|
| Input delay | from the user's action until the handler starts, while other tasks still run | break up the long tasks that run while the user may act |
| Processing duration | the handlers, and the rendering work they start | less work in the handler; the non-urgent update as a transition (below) |
| Presentation delay | from the end of the handlers to the next frame: style, layout, paint | a smaller DOM; `content-visibility` for off-screen content; no layout thrashing |

INP ends at the next paint. A result that waits for the network needs the timing of section 3 as
well.

### Long tasks and yielding

**When a handler or a loop runs longer than 50 ms, yield to the main thread after the part the
user sees**, so the browser can paint and answer the next input. A long task is any task over
50 ms (web.dev). web.dev's pattern, with a fallback because `scheduler.yield()` runs in Chrome and
Edge 129 and Firefox 142 but not in Safari (read 2026-10-01):

```js
function yieldToMain() {
  if (globalThis.scheduler?.yield) {
    return scheduler.yield();
  }

  // Safari has no scheduler.yield(); a zero-delay timeout also lets the browser paint first.
  return new Promise((resolve) => {
    setTimeout(resolve, 0);
  });
}
```

For React's own rendering, a transition does the same job: React can interrupt it to answer
input (below).

### Layout and paint

- **In one handler, read layout first, then write.** A read after a style write forces a layout,
  and a loop of them is a "read-write-read-write cycle" (web.dev).
- **Give long off-screen sections `content-visibility: auto` and a `contain-intrinsic-size`**, so
  the browser skips their layout and paint until they near the viewport. web.dev's demo went from
  232 ms to 30 ms of rendering. It is Baseline newly available since 2025-09-15; webstatus lists
  Chrome and Edge 108, Firefox 130 and Safari 26, while web.dev's own page lists older versions
  (read 2026-10-01).
- **Animate only `opacity` and `transform`**, which the browser composites without layout or
  paint (web.dev).
- **Use `will-change` only to fix a problem you measured**: MDN calls it "a last resort" and warns
  against putting it on many elements.

### In React

- **Memoisation with the compiler on.** Whether to write `memo`, `useMemo` or `useCallback` by
  hand is [components.md](../components/components.md) section 7. What measuring adds: the compiler gives
  every component that follows the Rules of React the effect of `memo` (react.dev), and it does
  not fix every slow render. In one practitioner's test on a 15,000-line application with the
  beta compiler, it fixed 2 of 9 re-render cases, partly fixed 5, and did not fix 2, where a
  library made it bail out; initial load was unchanged (Nadia Makarevich, 2024-12-04, one
  application). When a trace shows a slow render the compiler did not fix, check whether the
  component uses a library the compiler skips; the list, and what to do about each, is
  [components.md](../components/components.md) section 7.
- **Keep a context provider's value the same object between renders when nothing in it
  changed.** React re-renders every component that reads the context when the provider gets a
  new value, compared with `Object.is`, and `memo` does not stop it (react.dev). For the same
  reason, a value that changes many times a second does not belong in a context that many
  components read (this follows from react.dev's rule; no owner states it). Where state lives
  is [architecture.md](../architecture/architecture.md) section 7.
- **Mark a non-urgent update, such as a navigation or a filter that redraws a long list, with
  `startTransition`**, so React renders it in the background, can interrupt it for input, and
  does not replace content already shown with a fallback (react.dev). One limit: a transition
  cannot drive a controlled text input. The limit on a state update after an `await` is
  [components.md](../components/components.md) section 8.
- **Use `useDeferredValue` for a value that feeds a slow render**, such as the text of a search
  box above a long list. Unlike a debounce it needs no fixed delay and does not block; it does
  not stop extra network requests (react.dev).
- **Costly initial state.** How to pass it to `useState` is
  [components.md](../components/components.md) section 4.
- **Read a slice of a query with `select`**, so a component re-renders only when its slice
  changes; TanStack Query's structural sharing keeps the old reference when nothing changed.
- **Keep a view the user will come back to, such as a tab, in `<Activity mode="hidden">`**
  instead of unmounting it: React hides it with `display: none`, cleans up its effects, keeps its
  state and DOM, and re-renders it at a lower priority (react.dev, React 19.2 and newer).

### Long lists

**Virtualise a list only when a trace shows its rendering or its DOM size as the largest part of
a failing metric.** No source with a method gives a row count at which virtualising starts to pay
(read 2026-10-01). The one number found shows why: in one project's table of 1,000 virtualised
rows, a scroll tick took 8.4 ms with 10 columns and 43.9 ms with 50 (tabularis.dev, one project),
so columns and the cost of a cell matter as much as rows. Before you virtualise, try
`content-visibility: auto` on the rows (layout and paint, above), which keeps them in the DOM;
this order is the practice's choice, since no source compares the two.

Virtualising has a cost. Rows that are not in the DOM cannot be reached by find in page, landmark
navigation or an anchor link (WICG virtual-scroller explainer), and a blind user reported rows
that "appear and disappear under the virtual cursor mid-read" (one user's bug report, 2026).
The cost to assistive technology is one reason to virtualise only when a trace shows the need;
[accessibility.md](../design/accessibility.md) section 3 links back here. How a component that
uses `useVirtualizer` meets the compiler is
[components.md](../components/components.md) section 7.

## 7. The server-rendered case, in brief

This section holds when a route is server-rendered or prerendered by a framework.
[architecture.md](../architecture/architecture.md) sections 2 and 14 decide which routes are.

- **Stream the HTML from `onShellReady` for users, and wait for `onAllReady` only for crawlers and
  static generation.** Waiting for everything gives up progressive loading (react.dev,
  `renderToPipeableStream`).
- **Fix a hydration mismatch like any other bug.** React does not promise to patch attribute
  differences, and "in the worst case, event handlers can get attached to the wrong elements".
  The usual causes are a `typeof window !== 'undefined'` check, a browser-only API such as
  `window.matchMedia`, and different data on the server and the client. `suppressHydrationWarning`
  works one level deep and is an escape hatch (react.dev).
- **Render static content that needs a large library in a Server Component**, so the browser
  does not download the library: react.dev's markdown example saves "an additional 75K
  (gzipped)". Do not describe this as "zero bundle size"; the owner's page does not.
- **When you move a route to server rendering, measure the time until it answers input as well as
  LCP, on that route.** In one practitioner's lab test (6x CPU slowdown, Slow 4G, one chat-style
  application), every server-rendered variant cut LCP from 4.1 s to between 1.28 s and 2.16 s,
  and left a gap of about 2.4 to 2.5 s in which the page was visible and did not answer input
  (Nadia Makarevich, 2025). LCP rewards that gap, and INP catches it only when a user acts during
  it.

## 8. SEO, in brief

A route that must be found, previewed or cited reaches readers that are not browsers. Google
renders JavaScript for a page that returns status 200, after a queue, and may skip a page that
returns another status; other crawlers and link-preview bots mostly read the HTML the server
sends.

- **Prerender or server-render every page that must rank or be previewed**, so its text, title
  and meta tags are in the HTML the server sends (Google; react.dev `prerender`).
- **Make every link an `<a>` with an `href`.** "Google can only crawl your link if it's an `<a>`
  HTML element with an `href` attribute."
- **Route with the History API, not `#` fragments** (Google).
- **Render one `<title>` per view.** React 19 moves a `<title>` rendered anywhere into the head;
  with two at once, search engines' behaviour is undefined (react.dev). What a title change does
  for a screen-reader user is [accessibility.md](../design/accessibility.md) section 6.
- **Answer a missing page with a real `404`.** A client-rendered route that shows "not found"
  with status 200 is a soft 404: redirect to a URL the server answers with 404, or add
  `<meta name="robots" content="noindex">` (Google).
- **Do not serve crawlers a separate rendering.** Google calls dynamic rendering "a workaround and
  not a recommended solution".

Core Web Vitals are not a flat ranking factor. Google says they align with "what our core ranking
systems seek to reward", next to other page-experience signals. Fix them for users. A product
behind a login needs none of this section.

## 9. Common mistakes

### A lazy-loaded LCP image

```html
<!-- Bad: this illustration is the largest element of the empty invoices screen, and
     loading="lazy" makes the browser wait for layout before it asks for the file. -->
<img src="/images/no-invoices.avif" width="480" height="320" alt="" loading="lazy">
```

`loading="lazy"` on the LCP element adds a wait to the resource load delay, the part of LCP that
should stay under 10% (section 5).

```html
<!-- Good: the same image, eager, and first in line among the images. -->
<img src="/images/no-invoices.avif" width="480" height="320" alt="" fetchpriority="high">
```

The fix removes the lazy loading and adds `fetchpriority="high"`, so the download starts as soon
as the browser sees the element and goes ahead of other images (web.dev).

### An image without dimensions

```html
<!-- Bad: no width and no height. The browser learns the size only when the file arrives,
     and the text under the logo jumps down. -->
<img src="/images/acme-logo.svg" alt="Acme Corp">
```

The jump is a layout shift, and it counts toward CLS on every visit.

```html
<!-- Good: width and height give the aspect ratio, so the box is reserved before the file
     arrives. -->
<img src="/images/acme-logo.svg" width="160" height="40" alt="Acme Corp">
```

```css
/* Keeps a sized image fluid: the width follows the container, the ratio stays. */
img {
  max-width: 100%;
  height: auto;
}
```

The fix adds the two attributes. The CSS lets the image shrink on a narrow screen without
losing the reserved ratio (web.dev).

### `lazy` declared inside a component

The imports and the props type are cut from both blocks. This pair is not from the reference
application: it was type-checked, linted and built in a temporary file of that application, and
the file was removed again.

```tsx
// Bad: `lazy` runs inside the component. Each render makes a new component type, so React
// unmounts the chart and resets its state every time.
export function InvoiceTotals({ isChartOpen }: InvoiceTotalsProps) {
  const InvoiceChart = lazy(() =>
    import("@/billing/list-invoices/invoice-chart.tsx").then((chartModule) => ({ default: chartModule.InvoiceChart })),
  );

  if (!isChartOpen) {
    return null;
  }

  return (
    <Suspense fallback={<ScreenPending />}>
      <InvoiceChart />
    </Suspense>
  );
}
```

react.dev: declaring `lazy` inside a component "will cause all state to be reset on re-renders".

```tsx
// The chart and its charting library download only when a user opens the chart.
// `lazy` renders the `default` of what the import resolves to; the map keeps the named export.
const InvoiceChart = lazy(() =>
  import("@/billing/list-invoices/invoice-chart.tsx").then((chartModule) => ({ default: chartModule.InvoiceChart })),
);

export function InvoiceTotals({ isChartOpen }: InvoiceTotalsProps) {
  if (!isChartOpen) {
    return null;
  }

  return (
    <Suspense fallback={<ScreenPending />}>
      <InvoiceChart />
    </Suspense>
  );
}
```

The fix moves the `lazy` call to the top level of the module. It runs once, the component type
stays the same across renders, and React caches the import, so the chunk downloads once.

### A request that starts after render

The imports and the screen component are cut from both blocks; they are the same as in
[performance-example.md](performance-example.md).

```tsx
// Bad: the loader does not start the invoices request. `InvoiceList` starts it when it first
// renders, and that waits for this route's code chunk: two round trips, one after the other.
export const Route = createFileRoute("/invoices/")({
  // The clock is read here, once per visit, and passed down as a value: rendering stays pure.
  loader: () => ({ today: toIsoDate(new Date()) }),
  staticData: { title: "Invoices" },
  component: InvoicesScreen,
});
```

With route-level splitting, the screen's code arrives in its own chunk, and only then can it ask
for its data (TanStack Query, "Request waterfalls"). A `fetch` in `useEffect` has the same
problem, and it never triggers `<Suspense>` either (react.dev).

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

The fix starts the request in the loader. The router does not split the loader out
(section 5), so the request leaves as soon as the URL matches, while the chunk downloads.

### Memoising everything by hand

The imports and the route definition are cut from both blocks.

```tsx
// Bad: `useCallback` by hand in new code, with the compiler on.
function InvoicesScreen() {
  const { apiClient } = Route.useRouteContext();
  const { today } = Route.useLoaderData();

  const renderPayLink = useCallback(
    (invoice: Invoice) => (
      <Link to="/invoices/$invoiceId/pay" params={{ invoiceId: invoice.id }} className="underline underline-offset-2">
        Pay<span className="sr-only"> the invoice of {invoice.customerName}</span>
      </Link>
    ),
    [],
  );

  return (
    <section className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">Invoices</h1>
      <InvoiceList apiClient={apiClient} today={today} renderPayLink={renderPayLink} />
    </section>
  );
}
```

The compiler already memoises what this component renders and passes down, so the hook only
adds a dependency list to keep right. When such a hook stays is
[components.md](../components/components.md) section 7.

```tsx
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

The fix removes the hook and leaves memoisation to the compiler. Memoisation that existing code
already has is a different case, also in [components.md](../components/components.md)
section 7.

### Optimising without a measurement

The two blocks are the Verification section of a pull request
([git.md](../../any-language/git/git.md) section 4). The values in the second are invented.

```markdown
## Verification

*Checked in this session*

- Moved the status filter's update into `startTransition`. The list feels faster on my laptop.
```

"Feels faster on my laptop" names no metric, no percentile and no device a user has. Nobody can
tell whether the change fixed a failing metric or one that already passed.

```markdown
## Verification

*Checked in this session*

- Field, before: INP on `/invoices` at the 75th percentile on mobile was 380 ms over the 28 days
  to 2026-09-28 (web-vitals, our own backend, 41,200 interactions). The attribution put most of
  it in processing, on the status filter.
- Lab: a trace of one filter change at the calibrated low-tier CPU showed a 240 ms task, most of
  it the render of `InvoiceList`. With the status filter's update moved into `startTransition`,
  the longest task in the same trace is 70 ms.

*For the reviewer*

- On 2026-10-29, read INP on `/invoices` at the 75th percentile on mobile over the 28 days after
  the release. Expected: 200 ms or less.
```

The fix is the measurement: the same change, now tied to the field metric that failed, its
largest part, a lab trace before and after, and the date the field value will be read again.

## 10. Where the rules stop holding

- **A product behind a login, with nothing a crawler must read.** Section 8 does not apply, and
  CrUX never sees it: your own field data is the only data.
- **Users on fast desktops only,** such as an internal tool. A budget modelled on a
  75th-percentile phone is then too strict; set it from the devices your field data shows.
- **A framework that owns loading,** such as Next.js or React Router in framework mode. Use its
  own way to split code, prefetch, and load images and fonts. The metrics, the thresholds and the
  one rule stay.
- **A prototype or a spike.** Skip the measuring and the budget. Keep what costs nothing: image
  dimensions, no lazy LCP image, the request started in the loader.
- **A feature with limited support.** Soft navigations and Long Animation Frames are Chromium
  only, and `scheduler.yield()` has no Safari (read 2026-10-01). Data from them covers part of
  your users; keep the fallback each rule names.

## 11. Review checklist

A review question per area. Ask each one of the change in front of you.

| Section | Ask | Red flag |
|---|---|---|
| 3. Field metrics | Does the application report LCP, INP and CLS from real visits, with attribution and soft navigations? | no field data; a Lighthouse score as the only number |
| 3. Budgets | Does CI fail when the first screen passes its JavaScript budget? | no budget; a size warning nobody reads |
| 4. The order of work | Does the change name the field metric it fixes, with percentile, source and date? | "feels faster"; work on a metric that already passes |
| 5. Images | Is the LCP image eager with `fetchpriority="high"`, and does every image have `width` and `height`? | `loading="lazy"` on the LCP image; an `<img>` with no size |
| 5. Fonts | WOFF2 only, a chosen `font-display`, and a preload only for the first screen's font, with `crossorigin`? | a preload with no `crossorigin`; a preload for every weight |
| 5. Caching | Hashed assets cached for a year, and the HTML revalidated? | `no-store` on the HTML; HTML cached for hours |
| 5. Code splitting | One chunk per route, and `lazy` only at module level? | `lazy` inside a component; the whole application in one chunk |
| 5. Data | Does every screen start its data in the route loader? | a request that starts after render; suspense queries in series |
| 6. Runtime | Is a task over 50 ms broken up, and was a slow render traced before it was changed? | a render change with no trace behind it; a layout read after a write in a loop |
| 6. Long lists | Is a virtualised list backed by a trace, with its accessibility cost handled? | virtualising by row count alone |
| 7. Server rendering | Was the time until the route answers input measured, as well as LCP? | LCP alone as the proof that server rendering helped |
| 8. SEO | Is a page that must rank prerendered, linked with `<a href>`, and answered with the right status? | a public page that is blank until JavaScript runs; a soft 404 |

## 12. Sources

All read on 2026-10-01; a page's own date is given where it has one.

### What fast means

1. web.dev, [Largest Contentful Paint](https://web.dev/articles/lcp) (2025-09-04),
   [Interaction to Next Paint](https://web.dev/articles/inp) (2025-09-02) and
   [Cumulative Layout Shift](https://web.dev/articles/cls) (2023-04-12): the metrics, their
   thresholds at the 75th percentile, and that INP stops at the next paint.
2. web.dev, [Web Vitals](https://web.dev/articles/vitals) (2024-10-31): field and lab, TBT as a
   lab stand-in for INP.
3. web.dev, [TTFB](https://web.dev/articles/ttfb) (2025-11-18) and
   [FCP](https://web.dev/articles/fcp) (2023-12-06): the diagnostics and their thresholds.
4. Chrome for Developers, [Chrome UX Report](https://developer.chrome.com/docs/crux): what CrUX
   holds.
5. DebugBear, [2025 in web performance](https://www.debugbear.com/blog/2025-in-web-performance)
   (2025-12): CrUX is Chrome only; LCP covers the first navigation only.
6. Chrome for Developers,
   [Soft navigations](https://developer.chrome.com/docs/web-platform/soft-navigations) (updated
   2026-09-02): on by default from Chrome 151; CrUX reporting not yet decided.
7. Alex Russell,
   [The Performance Inequality Gap, 2026](https://infrequently.org/2025/11/performance-inequality-gap-2026/)
   (2025-11-24): lost users missing from RUM; the modelled budgets and the 75th-percentile device.
8. HTTP Archive, Web Almanac 2025,
   [Performance](https://almanac.httparchive.org/en/2025/performance) and
   [Page weight](https://almanac.httparchive.org/en/2025/page-weight): pass rates from CrUX data
   of July 2025; the median JavaScript per page.

### Measuring

9. [web-vitals](https://github.com/GoogleChrome/web-vitals) README and its
   [registry entry](https://registry.npmjs.org/web-vitals/latest): the attribution build, its
   size, `reportSoftNavs`, the Chromium floor.
10. Chrome for Developers,
    [Long Animation Frames](https://developer.chrome.com/docs/web-platform/long-animation-frames)
    (2024-10-14): the API and its browser support.
11. react.dev,
    [React Performance Tracks](https://react.dev/reference/dev-tools/react-performance-tracks)
    and [`<Profiler>`](https://react.dev/reference/react/Profiler): what each build shows.
12. Josh Comeau, [Why React Re-Renders](https://www.joshwcomeau.com/react/why-react-re-renders/):
    re-renders are overestimated; Profiler times are not absolute; measure production builds on
    slow hardware.
13. Chrome for Developers,
    [Performance features reference](https://developer.chrome.com/docs/devtools/performance/reference)
    (2025-04-03) and
    [New in DevTools, October 2026](https://developer.chrome.com/blog/new-in-devtools-october-2026):
    CPU calibration; soft-navigation Insights.
14. [Lighthouse releases](https://github.com/GoogleChrome/lighthouse/releases); the Chrome blog
    post [Lighthouse 13](https://developer.chrome.com/blog/lighthouse-13-0) is the place to look
    for the removed audits, read here through a search snippet only.
15. The registry entries of
    [rollup-plugin-visualizer](https://registry.npmjs.org/rollup-plugin-visualizer/latest) and
    [vite-bundle-analyzer](https://registry.npmjs.org/vite-bundle-analyzer/latest), and
    [Sonda](https://sonda.dev/): the bundle analysers.
16. [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp): trace tools for
    an agent, its usage statistics and its data-access warning.
17. [size-limit](https://github.com/ai/size-limit) and
    [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci): the CI gates.
18. Nadia Makarevich,
    [Bundle Size Investigation](https://www.developerway.com/posts/bundle-size-investigation):
    the wildcard import and the CommonJS library, size only.

### The order of work

19. Vercel, [Introducing: React Best Practices](https://vercel.com/blog/introducing-react-best-practices)
    (2026-01-14): an order of work with no measurement behind it.
20. web.dev, [Learn Performance](https://web.dev/learn/performance): the course's order.
21. web.dev, [The most effective ways to improve Core Web Vitals](https://web.dev/articles/top-cwv)
    (October 2024): fixes per metric, with HTTP Archive figures.
22. Nadia Makarevich,
    [Initial load performance](https://www.developerway.com/posts/initial-load-performance)
    (2025-01-21): find the bottleneck first; React's share of LCP, the CDN and cache numbers, in a
    synthetic demo.

### Loading

23. web.dev, [Optimize LCP](https://web.dev/articles/optimize-lcp): the four parts, their target
    shares, no lazy LCP image, `fetchpriority`.
24. web.dev, Learn Images:
    [Image performance](https://web.dev/learn/images/performance-issues),
    [AVIF](https://web.dev/learn/images/avif) and
    [Responsive images](https://web.dev/learn/images/responsive-images) (2023-02-01): dimensions,
    lazy loading, formats, `srcset` and `sizes`.
25. webstatus.dev, the features
    [fetchpriority](https://api.webstatus.dev/v1/features?q=fetchpriority),
    [loading-lazy](https://api.webstatus.dev/v1/features/loading-lazy),
    [content-visibility](https://api.webstatus.dev/v1/features/content-visibility) and
    [scheduler](https://api.webstatus.dev/v1/features?q=scheduler): Baseline status and browser
    versions.
26. web.dev, [Best practices for fonts](https://web.dev/articles/font-best-practices)
    (2022-10-04) and
    [Preload web fonts](https://web.dev/articles/codelab-preload-web-fonts) (2018-04-23); Chrome
    for Developers, [Font fallbacks](https://developer.chrome.com/blog/font-fallbacks)
    (2023-02-10).
27. web.dev, [HTTP cache](https://web.dev/articles/http-cache),
    [Text compression](https://web.dev/articles/reduce-network-payloads-using-text-compression)
    and [Content delivery networks](https://web.dev/articles/content-delivery-networks).
28. web.dev, [preconnect and dns-prefetch](https://web.dev/articles/preconnect-and-dns-prefetch)
    and [Preload critical assets](https://web.dev/articles/preload-critical-assets).
29. web.dev, [Back/forward cache](https://web.dev/articles/bfcache) (updated 2026-07-02).
30. react.dev, [`lazy`](https://react.dev/reference/react/lazy) and
    [`<Suspense>`](https://react.dev/reference/react/Suspense).
31. TanStack Router,
    [Code splitting](https://tanstack.com/router/latest/docs/framework/react/guide/code-splitting);
    React Router, [Route module](https://reactrouter.com/start/framework/route-module) and
    [Route object](https://reactrouter.com/start/data/route-object) (8.4 docs).
32. Vite, [Building for production](https://vite.dev/guide/build) and
    [Build options](https://vite.dev/config/build-options) (8.3.1): the default target, chunking
    options, the chunk-size warning, `modulePreload`, `vite:preloadError`; Rolldown,
    [Advanced chunks](https://rolldown.rs/in-depth/advanced-chunks).
33. webpack, [Tree shaking](https://webpack.js.org/guides/tree-shaking/): ES module structure.
34. TanStack Query,
    [Request waterfalls](https://tanstack.com/query/latest/docs/framework/react/guides/request-waterfalls),
    [Prefetching](https://tanstack.com/query/latest/docs/framework/react/guides/prefetching),
    [Suspense](https://tanstack.com/query/latest/docs/framework/react/guides/suspense) and
    [Important defaults](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults).
### Runtime

35. web.dev, [Optimize INP](https://web.dev/articles/optimize-inp) (2025-09-02) and
    [Optimize long tasks](https://web.dev/articles/optimize-long-tasks) (2024-12-19): the three
    parts, the 50 ms long task, the yield pattern.
36. web.dev,
    [Avoid layout thrashing](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing),
    [content-visibility](https://web.dev/articles/content-visibility) and
    [Animations guide](https://web.dev/articles/animations-guide); MDN,
    [will-change](https://developer.mozilla.org/en-US/docs/Web/CSS/will-change).
37. react.dev, [`memo`](https://react.dev/reference/react/memo),
    [`useMemo`](https://react.dev/reference/react/useMemo),
    [Compiler configuration](https://react.dev/reference/react-compiler/configuration) and
    [React Compiler 1.0](https://react.dev/blog/2025/10/07/react-compiler-1) (2025-10-07).
38. Nadia Makarevich,
    [How React Compiler performs on real code](https://www.developerway.com/posts/how-react-compiler-performs-on-real-code)
    (2024-12-04): one application, the beta compiler.
39. react.dev, [`useContext`](https://react.dev/reference/react/useContext),
    [`useTransition`](https://react.dev/reference/react/useTransition),
    [`useDeferredValue`](https://react.dev/reference/react/useDeferredValue) and
    [`<Activity>`](https://react.dev/reference/react/Activity).
40. TanStack Query,
    [Render optimizations](https://tanstack.com/query/latest/docs/framework/react/guides/render-optimizations).
41. [tabularis.dev](https://tabularis.dev/blog/optimizing-virtualized-react-grid): the one
    measured virtualised table, one project.
42. WICG, [Virtual scroller explainer](https://wicg.github.io/virtual-scroller/): content outside
    the DOM is outside find in page and landmarks; a
    [bug report from a blind user](https://github.com/anthropics/claude-code/issues/83167)
    (2026-08-01): what a virtualised list does under a screen reader.

### The server-rendered case

43. react.dev,
    [`renderToPipeableStream`](https://react.dev/reference/react-dom/server/renderToPipeableStream),
    [`prerender`](https://react.dev/reference/react-dom/static/prerender),
    [`hydrateRoot`](https://react.dev/reference/react-dom/client/hydrateRoot) and
    [Server Components](https://react.dev/reference/rsc/server-components).
44. Nadia Makarevich,
    [React Server Components: do they really improve performance?](https://www.developerway.com/posts/react-server-components-performance)
    (2025): the gap between visible and interactive, one application in a lab.

### SEO

45. Google Search Central,
    [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
    (2026-03-04),
    [Dynamic rendering](https://developers.google.com/search/docs/crawling-indexing/javascript/dynamic-rendering)
    (2025-12-10),
    [Crawlable links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)
    and [Core Web Vitals](https://developers.google.com/search/docs/appearance/core-web-vitals)
    (2025-12-10).
46. react.dev, [`<title>`](https://react.dev/reference/react-dom/components/title): one title at
    a time.
