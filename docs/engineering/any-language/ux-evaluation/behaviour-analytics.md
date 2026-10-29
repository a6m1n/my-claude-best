# Behaviour analytics rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. What each signal can show, and what it cannot](#2-what-each-signal-can-show-and-what-it-cannot)
- [3. The tracking plan: events, names and properties](#3-the-tracking-plan-events-names-and-properties)
- [4. Page views in a single-page app](#4-page-views-in-a-single-page-app)
- [5. Consent before tracking](#5-consent-before-tracking)
- [6. Heatmaps, session replay and frustration signals](#6-heatmaps-session-replay-and-frustration-signals)
- [7. Giving a coding agent the data](#7-giving-a-coding-agent-the-data)
- [8. React case](#8-react-case)
- [9. Common mistakes](#9-common-mistakes)
- [10. Where the rules stop holding](#10-where-the-rules-stop-holding)
- [11. Alternatives considered](#11-alternatives-considered)
- [12. Adoption in existing code](#12-adoption-in-existing-code)
- [13. Review checklist](#13-review-checklist)
- [14. Sources](#14-sources)

## 1. Purpose and the one rule

This file is for everyone who adds analytics events, page views, heatmaps, session replay or
frustration signals to a web application, or gives a coding agent that data: people and AI agents
alike. Read it before you add an analytics SDK or an event, turn on replay or heatmaps, build the
consent gate, or connect an analytics MCP server to an agent. How to choose the metrics and how to
test with users is [evaluation.md](evaluation.md) (sections 4 and 8). What a third-party script may
see in a React application is [security.md](../../react/security/security.md) sections 12 and 13.

A team that follows it names its events one way, counts each change of screen once, sends, stores
and reads nothing before the user agrees where consent is needed (section 5), and treats every
click pattern as a lead to check, never as a finding.

The one rule: **collect only what a written question needs, start collecting when the user agrees,
and check every pattern the data shows with people before you call it a finding.**

Why it matters:

- Click data is easy to collect, and weak evidence of what people saw or meant. Huang, White and
  Buscher tracked the eyes and the cursor of 36 people on 32 search tasks in a lab: the cursor sat
  a median of 74 px from the gaze at the moment of a click, and 233 px while the cursor was idle
  [1]. They measured search result pages only, and say "more work is also needed to generalize
  this research beyond SERPs to any Web page" [1].
- Recordings pile up unwatched. Across its customers' web recordings over 90 days, PostHog found
  that "roughly 99.8% of recorded sessions are watched by no one, ever", and that the median watch
  lasted 17 seconds [2]. That is the vendor's own data, and "ever" there means within the 90 days.
- A search on 2026-10-29 found no study that checks rage clicks or dead clicks against real
  usability problems: only vendors' blogs, with no validation data (section 6).

When you need it, and when it is too much:

- **Use it** when a product is live and has a question about what users do that only usage data
  answers at scale: how many reach a step, where they stop, which screens they open.
- **It is too much** when no question is written yet, since then nothing is worth collecting. When
  the question is why people fail at a step, a test with users answers it
  ([evaluation.md](evaluation.md) section 4). When the answer is an outcome the server already
  records, such as a payment that went through, the server's records answer it, and a browser event
  would be a second copy that misses every user who did not agree. When nobody will watch, recording
  replay costs consent and storage for nothing [2].
- **The simpler way** is the server's own records and small rounds of tests with users.

What this file leaves out, and where it lives:

- Choosing product metrics, and A/B tests: [evaluation.md](evaluation.md) sections 8 and 10.
- Core Web Vitals from real users: [performance.md](../../react/performance/performance.md)
  section 3. Whether that report needs consent is not covered yet: neither this file nor
  performance.md decides it.
- What a third-party script may see, keystroke listeners on login and payment screens, and replay
  masking: [security.md](../../react/security/security.md) sections 12 and 13.
- Native apps. Page views in a server-rendered application (section 10).
- Not covered yet, because the research found no source: a study that checks rage or dead clicks
  against real usability problems; how closely cursor and gaze agree on pages other than search
  results, measured after 2012; how many problems watching replays finds, and at what cost; the
  CNIL's final recommendation on session replay (section 5); consent law outside the EU's ePrivacy
  Directive; how a consent banner should look and word its choice; an independent source on event
  naming (section 3).

## 2. What each signal can show, and what it cannot

| Signal | What it can show | What it cannot show |
|---|---|---|
| An event, a funnel | how many people did a step, and where they stopped | why they stopped |
| A page view | which screens people open, and in which order | whether the screen worked for them |
| A click map | where clicks land on a page; in PostHog it needs autocapture [8] | where people looked: on search pages the cursor sat 74 to 233 px from the gaze [1] |
| A scroll map | how far down people scroll; in PostHog it needs page-leave events [8] | whether they read what they scrolled past |
| A rage or a dead click | clicks that match one vendor's rule (section 6) | that the person was frustrated, or that a problem exists: no study validates it |
| A session replay | what one person did, step by step | how often it happens: that takes the events |

- **Before you add a signal, write the question it answers and find its row above.** When the
  question sits in the right-hand column, the signal cannot answer it: plan a test with users
  instead ([evaluation.md](evaluation.md) section 4).

## 3. The tracking plan: events, names and properties

A tracking plan lists every event the product sends, with its properties and the question each one
answers. Amplitude and Segment each keep such a plan apart from the code: Amplitude's page is called
"Plan your taxonomy", and Segment's rules sit in its tracking-plan docs [3], [4].
[tracking-plan-example.md](tracking-plan-example.md) shows one for an invoices screen.

What a plan holds, per event:

| Field | What it means | Set it when | Leave it out when |
|---|---|---|---|
| Question | what the team wants to learn, and the metric it feeds ([evaluation.md](evaluation.md) section 8) | always | never |
| Event name | an object and a past-tense action, in the plan's case | always | never |
| Fires when | the user's action or the system's moment, and the file that sends it | always | never |
| Properties | each with its type, its allowed values and whether it is required | a question needs a breakdown | the count alone answers the question |
| Sent from | the browser or the server | always | never |
| Consent | which decision of section 5 covers the event | always | never |
| Owner | the role that answers for the event | always | never |

Rules:

- **Write the event into the plan before the code sends it, and change both in one pull request,**
  so a reviewer reads the name and its question next to the call. The rule is this practice's
  choice: a plan written after the fact drifts from what the code sends.
  Check: before you merge a change that sends an event, find its name and each of its properties in
  the plan.
- **Give every event a question from the plan.** An event no question needs is data you hold and
  must protect for nothing.
- **Name an event as an object and an action:** `Invoice Payment Started`, not `Clicked Pay`.
  Names of one form let a search for an object find every event about it. Segment uses "the
  Object ( Blog Post ) + Action ( Read ) framework" [4], Mixpanel "the (Object) (Verb) format" [5],
  and Amplitude "[Noun] + [Past-Tense Verb]" [3]. These, and the naming rules below, are the
  conventions the three vendors publish for their own tools; no independent source on event naming
  was found (section 1). Put the verb in the past tense: Amplitude says so [3], Segment and
  Mixpanel name no tense, and Mixpanel's own examples, `song_played` and `page_viewed`, take the
  same form [5].
- **Never put a value in an event's name.** Send one event with a property, not one event per date,
  status or id. Segment: "Don't create event names dynamically" [4]. Mixpanel: "don't create an
  event name like Purchase (11-01-2019)" [5]. Amplitude's page says nothing on it, and its example
  uses one event with a property in place of several events [3]. A value in the name splits one
  action into as many events as there are values, in every report.
- **Keep the detail in properties,** for the same reason: detail in the name would split one event
  into many. Segment: "events should be generic and high level, whereas properties are specific and
  detailed" [4].
- **Use one case in a plan, and write it at the top.** The default is Title Case for event names
  and snake_case for property names: Segment recommends exactly that [4], and Amplitude's default
  events use Title Case [3]. Mixpanel recommends snake_case for event and property names alike,
  above all when the data goes on to a data warehouse [5]; take snake_case for events too when a
  warehouse is the main reader. Two cases in one plan give one action two names in the reports.
- **Keep the tool's own name for its built-in events,** such as PostHog's `$pageview`, and apply the
  plan's case to your own events only, so the plan does not rename what the tool defines.
- **Give every property a type, and give a choice its closed list of values,** and say whether the
  property is required, so `overdue` cannot also arrive as `Overdue` and `late`.
- **Send no personal data in an event's name or properties:** no person's name, email, typed text
  or document number. Only the fields the plan lists leave the browser, and the plan lists the
  ones the tool adds by itself too ([security.md](../../react/security/security.md) section 12,
  the data layer; section 13 for credentials).
  Check: before release, open one real event of each name in the tool's own event view and
  compare its property list with the plan; a property no plan row names blocks the release until
  it is listed, turned off or masked.
- **Identify a person only when a question needs one person's events joined.** PostHog's React
  guide says "Identifying users is required" to connect events, replays and errors to one person
  [31]; that is the vendor's view for its own features. A plan whose questions are about a screen
  needs no identity, and its events stay further from a named user. When you do identify, PostHog
  advises "a stable ID from your auth system when possible, not an email or display name" [31].

## 4. Page views in a single-page app

A route change in a single-page app loads no page, so a tool that counts page loads sees one page
per visit. Google: "If virtual page views are not recorded for screen changes, Google Analytics
treats the SPA as a single page, leading to skewed metrics" [23].

- **Count one page view each time the screen changes, from one source per tool:** either the tool's
  own history setting or the router's event, never both. What each source counts:

  | Source | Its page view on a route change | Counts a `replaceState` |
  |---|---|---|
  | GA4, enhanced measurement | `page_view` "each time the page loads or the browser history state is changed by the active site" [22] | yes: it "listens for pushState, popState, and replaceState" [22] |
  | PostHog (posthog-js 1.442.0) | `capture_pageview: 'history_change'`, the default from `defaults: '2025-05-24'`; without `defaults`, page loads only [6] | yes, when "the pathname changes" [33]: it hooks both `pushState` and `replaceState` [32] |
  | Amplitude (Browser SDK 2) | `[Amplitude] Page Viewed` on start, and on `pushState` or `popstate` [9] | no: "history.replaceState() doesn't trigger a page view" [9] |
  | TanStack Router (1.170.46) | the `onResolved` event, which its docs call "a good default for analytics because it fires after navigation finishes" [29] | it fires after each navigation the router resolves [29] |

  Two sources count each screen twice. Google warns that turning on automatic history tracking
  next to a Tag Manager page view "can lead to double-counting page views" [23], and Amplitude warns
  that an effect on `useLocation()` that sends its own page view "produces a second, differently
  named page view per navigation" [7].
- **Count a change of the path, not a change of the search string or the hash alone.** A new filter
  or page number keeps the same screen. PostHog's history setting counts path changes [6], and
  TanStack Router's event says whether "the pathname changed" (`pathChanged`) apart from any change
  of the address (`hrefChanged`) [29]. [accessibility.md](../../react/design/accessibility.md)
  section 6 treats such a change the same way for announcements. Whether GA4 counts a router's
  search-string update made with `replaceState` was not tested: check it in the tool's live view.
- **Compare a tool's counts only with the same tool's.** The tools disagree on what a change is:
  GA4 counts `replaceState` and Amplitude does not [22], [9], so one transition can count in one
  tool and not in the other.
- **Send the path, not the full URL:** [security.md](../../react/security/security.md) section 13.
- **Keep page views apart from performance navigations.**
  [performance.md](../../react/performance/performance.md) section 3 measures each route change as
  a soft navigation for Core Web Vitals, with its own library and report; neither replaces the
  other.

Check: in a production build, accept the consent banner on the first screen, open two more screens,
then go back once. The tool's live view of incoming events shows four page views: the first screen,
counted when you agree, then one per screen shown. A development build under `<StrictMode>` can
show more (section 8).

## 5. Consent before tracking

This section settles a point the vendors and the regulator's text disagree on: when an analytics
SDK may send and store. The rule follows the regulator's guidelines and shows the vendors' view
beside it: a regulator's text decides what the law covers, while a vendor's docs decide only how
its own product behaves.

What the texts say:

- The EDPB's guidelines on the technical scope of Art. 5(3) of the ePrivacy Directive (version 2.0,
  adopted 7 October 2024) treat JavaScript that makes the browser send information as access that
  "clearly falls within the scope of Article 5(3) ePD" [11]. They add that "the applicability of
  this article does not systematically mean that consent needs to be collected": the guidelines "do
  not analyse the application of the exemptions", which are assessed case by case [11].
- The CNIL's draft recommendation on session replay says the purposes of replay tools "sont soumises
  au consentement préalable des utilisateurs" (are subject to the users' prior consent), and that
  with no configuration, masking should apply to every category by default [12]. It is a draft: its
  consultation is closed [21], the CNIL's plenary of 8 October 2026 listed the post-consultation
  version for examination [20], and no adopted text was found on 2026-10-29.
- Microsoft Clarity has enforced consent signals for visits from the EEA, the UK and Switzerland
  since 2025-10-31, and says this "does not introduce new consent requirements" [13]. Clarity sets
  no cookies there without consent [13].
- The vendors' view. PostHog: "Always load posthog-js", and control capture with its opt-in and
  opt-out calls [19]. Its reason is data quality: a gated snippet "can't count the visitors who
  ignore or dismiss the banner" [19]. Google: "Load Google tags in all cases, not only if the user
  consents. If consent is denied, Google receives cookieless pings" [25], which may include "user
  agent, screen resolution, IP address" [25].

Rules:

- **Before the SDK ships, decide for each tool and each purpose whether it needs consent, and
  write the decision, who made it and why into the tracking plan.** The default is consent first.
  An exemption is a decision of the person who answers for data protection in the project, with its
  reason, because the EDPB leaves exemptions to a case-by-case assessment [11]. A developer's guess
  is not that decision.
- **Until the user agrees, the tool sends nothing, stores nothing and reads nothing it stored on
  the device: where consent is needed, start the SDK only when the user agrees.** Art. 5(3) covers
  "the storing of information, or the gaining of access to information already stored, in the
  terminal equipment" [11]. The EDPB counts a browser's own use of what it stored as no such access
  "as long as the information does not leave the device" [11], so keeping the tool from reading
  before consent is this practice's choice. Loading the SDK's code with the page is fine; starting
  it is not. With the opt-out settings below, each tool but PostHog still sends or stores something
  once it has started. PostHog started with `opt_out_capturing_by_default`,
  `opt_out_persistence_by_default` and `advanced_disable_flags` would send and store nothing, as
  read in its source, yet it still reads its stored state at start [32], and one missed setting
  would send. So this practice starts every tool's SDK on consent, whatever its settings:

  | Tool | Its opt-out setting | What it still sends or stores, started before consent |
  |---|---|---|
  | PostHog (posthog-js 1.442.0) | `opt_out_capturing_by_default: true` holds the events until `opt_in_capturing()` [6]. Storage stops while the user is opted out only with `opt_out_persistence_by_default`, `cookieless_mode` or `disable_persistence`; with the first flag alone the SDK keeps its cookie and local storage [32] | on start it requests its remote configuration (`/array/<token>/config`) and then its feature flags, with no consent check, unless `advanced_disable_flags` is on [32], [33] |
  | Amplitude (Browser SDK 2) | `optOut: true` in `init()` [9] | "By default, init() fetches your project's remote configuration from Amplitude" [9], and it keeps the opt-out flag in its first-party `AMP_` cookie [9] |
  | GA4 | the `gtag('consent', 'default', ...)` command "on every page of your site before any commands that send measurement data" [24] | in advanced mode, "If consent is denied, Google receives cookieless pings" [25]: hold the tags back until consent (the next rule) |
  | Clarity | in Consent Mode, "consent state is denied until you update the user's current consent state" [13] | with `analytics_storage` denied, "Clarity tag loads, but only cookieless data is collected" [13] |

  Check: open the application in a new browser profile and answer nothing on the banner. The
  network panel shows no request to the analytics host, and the storage panel no cookie or key of
  the tool. The panels cannot show a read: a read is held back because the SDK starts only on
  consent, which the reviewer checks in the code (section 8).
- **Send no cookieless ping and no cookieless event to a user who has not agreed, until the person
  who answers for data protection has accepted them.** Google's advanced mode sends cookieless
  pings when consent is denied [25], and PostHog's `cookieless_mode` counts such users "with a
  privacy-preserving hash" [19]. Both make the browser send information, which the EDPB puts in
  scope of Art. 5(3) [11], and no source read says whether an exemption covers them: that is an
  open legal point. Until it is settled for your product, hold Google's tags until consent (its
  basic mode) and run PostHog without `cookieless_mode`. The cost: Google says that with the tags
  blocked "you will not get the full benefits of consent mode" [25], and PostHog warns of "sudden,
  large drops in event volume" [19].
- **Start session replay only after the user agrees, whatever the decision for events.** The CNIL's
  draft asks for prior consent for replay [12], and a replay records far more than any event.
  Replay masking is [security.md](../../react/security/security.md) section 13; the CNIL's draft
  asks the tool to mask every category by default as well [12].
- **Keep analytics and replay off the login and payment screens:**
  [security.md](../../react/security/security.md) section 12. The screens that section names send
  nothing; section 8 shows one way to hold that in a React app.
- **Prefer a data layer to a vendor's script:** [security.md](../../react/security/security.md)
  section 12. Section 8 shows the trade a team makes when it uses the vendor's SDK.

## 6. Heatmaps, session replay and frustration signals

- **Treat a rage click, a dead click or a heatmap hotspot as a lead.** Open the replays behind it,
  or put the task into the next test with users ([evaluation.md](evaluation.md) section 4), and
  report a problem only after a person has seen it happen. A search on 2026-10-29 for a study that
  checks these signals against real usability problems found only vendors' blogs, with no
  validation data. Sentry's docs say that when a user clicks an unresponsive element three or more
  times, "it indicates frustration" [10]; that is the vendor's reading of its own signal, not a
  measurement.
- **Never compare a rage-click rate across tools, or across an SDK upgrade that changes the rule.**
  Each tool counts something else:

  | Tool | A rage click is | Version read |
  |---|---|---|
  | PostHog | "three times in roughly the same spot (within 30 pixels) inside a one-second window" [8] | docs, no version |
  | Amplitude | "Four or more clicks on the same element, within 50 pixels, in one second" [9] | Browser SDK 2.24.0 or later |
  | Sentry | "3 or more times within that 7-second timeframe" on a `<button>`, `<input>` or `<a>` that changes neither the page nor its scroll; no distance [10] | JavaScript SDK 7.60.1 or later |

  Amplitude's dead click is "A click on an interactive element that changes neither the DOM nor the
  URL within three seconds" [9]. PostHog's own rule moves with its `defaults` date: from
  `'2025-11-30'` it "ignores repeat-click controls such as pagination arrows and pagers", and from
  `'2026-05-30'` it "also excludes stepper controls ... and text-selection surfaces" [33].
- **Read a click map as where clicks land, never as where people looked** [1]. How cursor and gaze
  agree on pages other than search results, measured after 2012, is not covered yet; the 2012
  paper itself notes that
  "Previous work has already shown that cursor is less aligned with gaze on non-SERP pages" [1].
- **Before you turn replay on, write the question it answers, who will watch and when it stops,**
  and record for that question only. PostHog's own figures show most recordings unwatched [2]; the
  rule is this practice's answer to that. How many problems watching replays finds, and at what
  cost, is not covered yet: the only figure found is PostHog's median watch of 17 seconds [2].
- **Count a replay finding from an AI only after a person has watched the clip.** At PostHog, "A
  text-only review of our dead-end monitor called its 'can't close this modal' findings solid.
  Watching the recordings said otherwise" [18]. In another check, nine people had opened a form,
  typed nothing and closed it, and "The model had invented their question from the pages around
  it" [18]. That is the vendor's own
  staff, reviewing sessions of its own site.

## 7. Giving a coding agent the data

Analytics vendors offer MCP servers that let a coding agent query the data. What each server
offered when read on 2026-10-29:

| Server | What the agent can read | What it can change |
|---|---|---|
| PostHog | funnels (`query-funnel`), session replays (9 tools), heatmaps (`heatmaps-list`) [14] | many tools that create, update or delete, such as `session-recording-playlist-create`, `action-create` and `alert-delete`; among them `session-recording-delete` and `session-recording-bulk-delete` [14] |
| Sentry, `sentry-mcp` (`@sentry/mcp-core` 0.42.0) | one replay's rage-click, dead-click and error counts, by its URL or id, and a search over many replays: "rage clicks, dead clicks, visited pages, errors seen, and replay users" (`search_replays`) [15] | not read |
| Microsoft Clarity | "metrics including scroll depth, engagement time, total traffic, and more", at most 10 requests per project per day, 3 days of data and 3 dimensions per request [16] | no replay or heatmap tool is listed [16] |

- **Before you connect a server, take its write tools away at the server, and deny the rest in the
  client.** PostHog's server drops the tools that create, update or delete data in read-only mode
  (`x-posthog-read-only: true`), and pins one project with `x-posthog-project-id` [39]. Its
  personal API key with the MCP Server preset is scoped to one project [39]. Where a server has no
  such mode, list its tools and deny every tool that writes or deletes: in Claude Code, a deny rule
  names one tool as `mcp__<server>__<tool>` [36]. A tool the vendor adds later is not on that
  list, so list the tools again after each update of the server.
- **Name the project, the date window and the filters in the request, and have the agent state
  them with its answer.** At Storyblok, an agent left unconfigured would "query whichever PostHog
  project was most recently mentioned, assume today's date", and early sessions needed correction:
  "wrong PostHog project, wrong date range" [17]. That is one team's report on its own workflow.
- **Treat what the agent concludes from the data as a lead**, the same as a signal (section 6): at
  PostHog a model invented what users wanted [18].
- **Keep the server's API key where the agent cannot leak it:** an agent in a container is
  [agent-containers.md](../docker/agent-containers.md) section 4.
- **Give the agent masked replays only** ([security.md](../../react/security/security.md) section
  13): what the agent reads goes into its context and to the model's provider.

## 8. React case

This is the React form of sections 4 and 5, for a client-rendered application laid out as
[architecture.md](../../react/architecture/architecture.md) says, with TanStack Router
([libraries.md](../../react/architecture/libraries.md) section 2). The tool is PostHog, because its
settings were read in its own source for this file. `libraries.md` names no analytics tool, so the
tool is a point to adapt; the rules hold for any tool.

- **Start the SDK once per page load, never in an effect: build the client at the top level of the
  startup file, and let it start the SDK behind a module-level guard when the user agrees
  (section 5).** `<StrictMode>` runs "one extra setup+cleanup cycle in development for every
  Effect", and none of these checks run in production [26]. react.dev keeps logic that runs "once
  per app load" in "your application's entry point" [27], and
  [components.md](../../react/components/components.md) section 5 lists the same case as "code at
  the top level of a module, or in the startup file". PostHog's React guide starts the SDK in
  `main.jsx`, and "Events captured before `posthog.init()` runs are dropped" [31]. Amplitude's guide
  gives the reason: "Module code runs once, before createRoot, and Strict Mode can't replay it" [7].
  [architecture.md](../../react/architecture/architecture.md) section 3 builds every client once in
  `main.tsx`, and the analytics client is one more.
- **Count page views in one place:** the router's `onResolved` event in `main.tsx` with the SDK's
  own page view off, or the SDK's history setting with no router code. Never add an effect on the
  location as well [7]. React Router's own docs send a page view from a `useEffect` on `[location]`
  [30]; that `location` holds the search string, so the effect also fires on a filter change, and
  twice per change in development [26]. If an effect stays, react.dev says not to suppress the
  second development call: "We recommend keeping this code as is", because "In production, there
  will be no duplicate visit logs" [28]. It also allows sending analytics "from the route change
  event handlers instead of Effects" [28], which the router event is.
- **How the router event behaves.** In `@tanstack/router-core` 1.171.39, the version
  `@tanstack/react-router` 1.170.46 installs, `pathChanged` compares the new path with the last
  resolved one, which is empty on the first load, so the first screen counts once. A navigation
  that redirects emits no `onResolved` for the address it leaves, so a redirect counts only where it
  lands [35]. This was read in the source, not run in a browser.
- **Call `init` only when the user agrees** (section 5): until then posthog-js drops every capture
  call [31]. The client below sets nothing that holds a capture back, so started earlier it would
  send every capture call at once, and with its opt-out settings alone posthog-js still requests
  its remote configuration and its feature flags [32].
- **Turn off in code every collector the tracking plan does not list.** posthog-js turns autocapture
  on by default [33], and when `capture_heatmaps` is unset, heatmaps follow the project's settings
  page [32]. `disable_external_dependency_loading` "will prevent PostHog from requesting any
  external scripts such as those needed for Session Replay, Surveys or Site Apps" [33]; in the
  default bundle, dead clicks, exception capture and web vitals load that way too [37].
- **Strip the query string and the hash from every URL the SDK sends.** posthog-js puts the page's
  full address, `location.href`, into `$current_url` [34], and copies it into the person's
  `$initial_` and the session's `$session_entry_` properties [34], [32]. Its config types point to
  `before_send` for rewriting `$current_url` [33]. The rule itself is
  [security.md](../../react/security/security.md) section 13.
- **Allow the ingestion host in the Content-Security-Policy.** PostHog's React guide says the SDK
  "lazy-loads extra bundles (session replay, surveys) from PostHog's CDN, and sends events to the
  ingestion host", and lists `script-src` and `connect-src` entries for its hosts, or a reverse
  proxy [31]. With external scripts off, `script-src` keeps `'self'`, and `connect-src` must allow
  the host the settings name ([security.md](../../react/security/security.md) section 5).

The `init` options the code below sets, read in posthog-js 1.442.0:

| Option | What it means | Set it when | Leave it out when |
|---|---|---|---|
| `api_host` | where the events go; the default is PostHog's US host [33] | always, from the public settings, so the code and the policy name one host | never |
| `opt_out_persistence_by_default` | no cookie or local storage while the user is opted out [32], [33] | consent is needed (section 5), so that a user who withdraws it stops the SDK's storage too | the written decision of section 5 says this tool and purpose need no consent |
| `capture_pageview` | the SDK's own page view; `false` turns it off [33] | `false` when the router counts page views, `'history_change'` when the SDK does | never: left unset, its default depends on `defaults` [6] |
| `autocapture` | the SDK records clicks and form events by itself [33] | `false`, unless the plan is built on autocaptured events | the plan lists autocaptured events; then the `ph-no-capture` class keeps a part of the page out [33] |
| `capture_heatmaps` | click positions for heatmaps; unset, the project's settings decide [32] | `false`; `true` when a question needs a heatmap (section 6) | never: left unset, the project's settings decide [32] |
| `disable_external_dependency_loading` | no script from PostHog's servers [33] | `true`, unless the plan needs replay, surveys or another collector loaded that way | the plan needs one; then `script-src` must allow PostHog's script host [31] |
| `advanced_disable_flags` | no request for the remote configuration or the feature flags [33], [32]; the flags request carries the first page's full address, which `before_send` never sees [38], [34] | the plan uses no feature flags or surveys | the plan needs them; then the plan names the flags request and what it carries, and the person who answers for data protection decides on it |
| `save_campaign_params` | the SDK copies the `utm_*` and ad click-id parameters of the page's address into each event; `false` stops that copy, but not the session's `$session_entry_` properties, which rebuild them from the address the session started on [33], [32], [34] | `false`, unless a question needs campaign attribution | a question needs it; then the plan lists each parameter, and the person who answers for data protection decides on the click ids |
| `mask_personal_data_properties` | the value of each ad click id the SDK knows, such as `gclid` and `fbclid`, becomes `<masked>` in the addresses it reads, the session's entry address included; `utm_*` values stay as they are [33], [34] | `true`, so the click ids that still leave in the `$session_entry_` properties carry no value | a question needs a click id's value; then the person who answers for data protection decides on it |
| `disable_scroll_properties` | the SDK measures how far down each screen is scrolled and sends it with the next page view; `true` turns that off, but not the previous screen's path and time [33], [32] | `true`, unless a question needs scroll depth (section 6) | a question needs scroll depth |
| `property_denylist` | properties the SDK deletes from every event before it leaves [33], [32] | always, for each property the tool adds that the plan refuses, such as the search words | the tool adds nothing the plan refuses |
| `before_send` | a function that edits or drops each event before it leaves [33] | always, to cut the query string and the hash | never |

The public settings, in `src/core/config.ts`; the API's own setting and the comments the file
already has are cut, and [security-example.md](../../react/security/security-example.md) section 2
shows the rest of the file:

```ts
const publicEnvSchema = z.object({
  ...
  // PostHog's project token ships to the browser: PostHog's React guide puts it in a VITE_ variable.
  // security.md section 9 asks for a restriction at the provider; PostHog's docs, read on
  // 2026-10-29, name none for this token. The cost: anyone who reads the bundle can send events to
  // the project.
  VITE_POSTHOG_PROJECT_TOKEN: z.string().min(1),
  // Where the events go. The Content-Security-Policy's connect-src must allow this host
  // (security.md section 5).
  VITE_POSTHOG_HOST: z.url(),
});

const publicEnv = publicEnvSchema.parse({
  ...
  VITE_POSTHOG_PROJECT_TOKEN: import.meta.env.VITE_POSTHOG_PROJECT_TOKEN,
  VITE_POSTHOG_HOST: import.meta.env.VITE_POSTHOG_HOST,
});

export const config = {
  ...
  posthogProjectToken: publicEnv.VITE_POSTHOG_PROJECT_TOKEN,
  posthogHost: publicEnv.VITE_POSTHOG_HOST,
} as const;
```

The analytics client, `src/core/analytics.ts`, whole:

```ts
// A vendor's SDK in the page: a departure from security.md section 12, which prefers a data layer.
// The team uses this SDK's session and device handling (behaviour-analytics.md section 8). The
// cost: the vendor's code runs in the page, and it adds its own device properties to each event.
import posthog from "posthog-js";
import type { CaptureResult, Properties } from "posthog-js";

type AnalyticsSettings = {
  projectToken: string;
  host: string;
};

// The application's one way to the analytics tool: nothing else imports posthog-js
// (file-structure.md section 4).
export type Analytics = {
  pageViewed: () => void;
  // One method per event of docs/tracking-plan.md, so an event or a property the plan does not
  // list does not compile (behaviour-analytics.md section 3). No "paid": a paid invoice has no
  // Pay link.
  invoicePaymentStarted: (properties: { invoiceStatus: "due" | "overdue" }) => void;
  // Starts the SDK: before the user agrees, nothing is sent and nothing is stored
  // (behaviour-analytics.md section 5).
  grantConsent: () => void;
  denyConsent: () => void;
};

// Set once the SDK has started: posthog.init runs once per page load, and a user may agree more
// than once (behaviour-analytics.md section 8).
let hasSdkStarted = false;

// `src/main.tsx` calls this once, at the top level, before the first render
// (behaviour-analytics.md section 8). The SDK starts later, in grantConsent().
export function createAnalytics(settings: AnalyticsSettings): Analytics {
  // Before grantConsent() starts the SDK, posthog-js drops every capture call, so nothing leaves
  // (behaviour-analytics.md section 8).
  return {
    pageViewed() {
      posthog.capture("$pageview");
    },
    invoicePaymentStarted({ invoiceStatus }) {
      posthog.capture("Invoice Payment Started", { invoice_status: invoiceStatus });
    },
    grantConsent() {
      startOnce(settings);

      // No `$opt_in` event: the tracking plan lists every event the product sends
      // (behaviour-analytics.md section 3). The call also replaces a "no" the SDK stored on this
      // device when the user withdrew on an earlier visit.
      posthog.opt_in_capturing({ captureEventName: false });
    },
    denyConsent() {
      // Before the start there is nothing to stop: the SDK has sent and stored nothing.
      if (hasSdkStarted) {
        posthog.opt_out_capturing();
      }
    },
  };
}

// Where consent is needed, the SDK starts only here, after the user agrees: started earlier, it
// would send every capture call at once, since none of the settings below holds one back
// (behaviour-analytics.md section 5).
function startOnce({ projectToken, host }: AnalyticsSettings): void {
  if (hasSdkStarted) {
    return;
  }

  hasSdkStarted = true;

  // The security.md section 12 departure: once started, the SDK adds its own device properties to
  // each event (behaviour-analytics.md section 8).
  posthog.init(projectToken, {
    api_host: host,
    // If the user withdraws later, denyConsent() opts out, and this flag stops the SDK's cookie
    // and local storage from then on; without it the SDK keeps them (behaviour-analytics.md
    // section 5).
    opt_out_persistence_by_default: true,
    // The router counts page views in src/main.tsx. A second source would count every screen
    // twice (behaviour-analytics.md section 4).
    capture_pageview: false,
    // Only the events the tracking plan lists. Autocapture is on by default, and heatmaps follow
    // the tool's project settings when this code leaves them unset (behaviour-analytics.md
    // section 8).
    autocapture: false,
    capture_heatmaps: false,
    // No script from the vendor's servers: replay, surveys, dead clicks and the other collectors
    // PostHog loads that way stay off, and script-src keeps only 'self' (security.md section 5).
    disable_external_dependency_loading: true,
    // The plan uses no feature flags or surveys. Without this the SDK requests its remote
    // configuration and its flags, and the flags request carries the first page's full address,
    // which before_send never sees (security.md section 13).
    advanced_disable_flags: true,
    // No question needs campaign values or ad click ids. Without this the SDK copies the utm_ and
    // click-id parameters of the address into every event, which before_send does not cut, since
    // they are not addresses (behaviour-analytics.md section 3).
    save_campaign_params: false,
    // The session's $session_entry_ properties still rebuild those parameters from the address the
    // session started on; with this, an ad click id among them arrives as "<masked>"
    // (behaviour-analytics.md section 3).
    mask_personal_data_properties: true,
    // No question needs scroll depth. Without this the SDK measures scrolling on every screen, the
    // pay screen included, and sends it with the next page view (behaviour-analytics.md section 3).
    disable_scroll_properties: true,
    // The search words a clerk typed into a search engine are typed text, which no question needs;
    // the SDK copies them from the referrer into every event (behaviour-analytics.md section 3).
    property_denylist: ["ph_keyword", "$session_entry_ph_keyword"],
    // Origin and path only: security.md section 13 asks for the path, because the query string can
    // hold typed text; the hash is cut for the same reason. The origin stays: it holds nothing the
    // user typed, and the SDK sends its host anyway, as $host for the page and $referring_domain
    // for the referrer. The cost: the host name leaves in each URL, which the tool already has.
    before_send: withQueryAndHashCut,
  });
}

// The SDK puts the page's full address into $current_url and copies it into the $initial_ and
// $session_entry_ properties; $referrer holds the address of the page before. Every URL in the
// event keeps its origin and path only.
function withQueryAndHashCut(event: CaptureResult): CaptureResult {
  return {
    ...event,
    properties: urlsWithQueryAndHashCut(event.properties),
    ...(event.$set === undefined ? {} : { $set: urlsWithQueryAndHashCut(event.$set) }),
    ...(event.$set_once === undefined ? {} : { $set_once: urlsWithQueryAndHashCut(event.$set_once) }),
  };
}

function urlsWithQueryAndHashCut(properties: Properties): Properties {
  return Object.fromEntries(
    Object.entries(properties).map(([name, value]) => [
      name,
      typeof value === "string" ? withoutQueryAndHash(value) : value,
    ]),
  );
}

function withoutQueryAndHash(value: string): string {
  // Only an absolute web address loses its tail: any other text keeps a "?" or "#" it holds.
  if (!/^https?:\/\//i.test(value)) {
    return value;
  }

  // The path ends at the first "?" (the query string) or "#" (the hash).
  return value.split(/[?#]/, 1)[0] ?? value;
}
```

From `src/main.tsx`: the lines this section adds, around the router of
[layout-example.md](../../react/architecture/layout-example.md) section 4. The imports, the
router's other options, the root element's guard and the render call are cut; `createAnalytics`
comes from `@/core/analytics.ts`, and the root route's context type gains `analytics` and
`countScreenOnShow`:

```tsx
...
const apiClient = new ApiClient(config.apiBaseUrl);
const queryClient = createQueryClient();
// Built here, once per page load: Strict Mode runs effects twice in development, never a line
// at the top of this file, so there is one client, and it starts the SDK once, when the user
// agrees (behaviour-analytics.md section 8).
const analytics = createAnalytics({ projectToken: config.posthogProjectToken, host: config.posthogHost });

// The one check before a page view: login and payment screens send nothing to analytics
// (security.md section 12). The router calls it after a navigation, and the consent banner once
// when the user agrees, for the screen on show.
function countScreenOnShow(): void {
  if (router.state.matches.at(-1)?.staticData.isPaymentOrLogin !== true) {
    analytics.pageViewed();
  }
}

const router = createRouter({
  routeTree,
  // The consent banner in the root route reaches the analytics client and the page-view check
  // here, the way a loader reaches the API client (architecture.md section 8).
  context: { apiClient, queryClient, analytics, countScreenOnShow },
  ...
});

// The one source of page views: the router, once a navigation has finished and changed the
// path. A change of the search string alone stays on the same screen, and a redirect counts
// only where it lands (behaviour-analytics.md section 4).
router.subscribe("onResolved", (event) => {
  if (event.pathChanged) {
    countScreenOnShow();
  }
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }

  interface StaticDataRouteOption {
    title?: string;
    // Set on a login or a payment screen: countScreenOnShow() sends no page view from it.
    isPaymentOrLogin?: true;
  }
}
...
```

The pay screen marks itself, in `src/routes/invoices.$invoiceId.pay.tsx` (the rest of the route
cut):

```tsx
export const Route = createFileRoute("/invoices/$invoiceId/pay")({
  ...
  // A payment screen: no page view is sent from it (security.md section 12).
  staticData: { title: "Pay invoice", isPaymentOrLogin: true },
});
```

The consent banner is left out: it sits in the root route and reads `analytics` and
`countScreenOnShow` from the route's context. Its accept button calls `analytics.grantConsent()`
and then `countScreenOnShow()`, so the screen on show counts unless it is a login or payment
screen; its other button calls `analytics.denyConsent()`. How the application stores the answer,
and calls `grantConsent()` at start, before the first render, for a user who agreed before, is left
out too.

Why it is good:

- **The SDK starts once per page load:** the client is built at the top level of the startup file,
  where Strict Mode cannot run it twice, and it starts the SDK behind a module-level guard; the
  comments say why at the lines ([components.md](../../react/components/components.md) section 5;
  [architecture.md](../../react/architecture/architecture.md) section 3).
- **Page views have one source,** the router, after each navigation that changed the path, with
  the SDK's own page view off and a comment at each end that names the other. A filter change is
  not a page view, and a redirect counts only where it lands (section 4).
- **Nothing is sent, stored or read before consent:** the SDK starts only when the user
  agrees, and the comment at `startOnce` says what it would send if it started earlier, so nobody
  moves the start back to page load (section 5).
- **Login and payment screens send nothing:** each such route says so in its `staticData`, and one
  check in `main.tsx` reads it, for the router's page views and for the one the consent banner asks
  for ([security.md](../../react/security/security.md) section 12).
- **Every URL leaves as its origin and path,** through one function the SDK calls before it sends
  ([security.md](../../react/security/security.md) section 13; the origin is a departure from its
  path-only rule, declared at the `before_send` line). The function cuts at the first `?` or `#`
  rather than parsing the address, so it needs no browser API newer than the application's floor.
- **Only the events the plan lists leave the browser:** autocapture and heatmaps are off in code,
  not on a settings page, and no script comes from the vendor's servers, so `script-src` stays
  `'self'`. The client has one method per event of the plan
  ([tracking-plan-example.md](tracking-plan-example.md)), with the plan's names and its closed
  list of values, so the compiler refuses an event or a value the plan does not list (section 3).
- **One client per external system, built once and handed down:** nothing outside
  `src/core/analytics.ts` imports posthog-js, `main.tsx` builds the client and the router's context
  hands it on, and the settings are read by name through the one schema
  ([file-structure.md](../file-structure/file-structure.md) section 4;
  [architecture.md](../../react/architecture/architecture.md) sections 3 and 8;
  [security.md](../../react/security/security.md) section 9). Imports are absolute and name the file
  that holds each name ([architecture.md](../../react/architecture/architecture.md) section 5).
- **No effect is needed,** so no effect is written: the client is built in top-level code, the SDK
  starts from the banner's click handler or, for a user who agreed before, at start, and the page
  view is the router's event ([components.md](../../react/components/components.md) section 5).

The departures:

- [security.md](../../react/security/security.md) section 12 prefers a data layer to a vendor's
  script on the page. This example runs the vendor's SDK, because the team uses its session and
  device handling, which a data layer through the application's own backend would have to rebuild.
  The cost: the vendor's code runs in the page, and the SDK adds its own properties to each event
  (browser, operating system, device type, screen size, time zone) [34]. A team that needs none of
  the SDK's features sends its events through its own backend instead, as
  [security-example.md](../../react/security/security-example.md) section 5 does for metrics.
- [security.md](../../react/security/security.md) section 13 asks for the path alone.
  `before_send` keeps the origin, since the origin holds nothing the user typed and the SDK sends
  the host anyway: as `$host` for the page's own address, and as `$referring_domain` for the
  referrer. The query string and the hash are cut. The cost: the host name leaves in each URL,
  which the tool already has.

What was checked: the lines shown above, in a scratch project with a hand-written route tree and
stubs for the cut parts, passed `tsc --noEmit` with TypeScript 6.0.3, `posthog-js` 1.442.0,
`@tanstack/react-router` 1.170.46, React 19.3.1 and Zod 4.6.7 (2026-10-29). Deliberate type
errors failed the same check: `isPaymentOrLogin: false` in the pay route and a call of
`invoicePaymentStarted` with `"paid"`, on an earlier form of these lines, and a call of
`grantConsent` with an argument, on this form. The scratch route used `createRoute`, since
`createFileRoute` needs the router plugin; the `staticData` line is the same. `withoutQueryAndHash`
was run in Node 24 on eight sample values. Not checked: the linters, a build, a run in a browser,
the network and storage panels of section 5's check, the Content-Security-Policy, the consent
banner, and the size the SDK adds to the first screen, which the budget gate of
[performance.md](../../react/performance/performance.md) section 3 measures.

## 9. Common mistakes

| Mistake | What it costs | Fix |
|---|---|---|
| Two sources of page views: the SDK's history setting plus a router hook, or an effect on the location [7], [23] | every screen counts twice | one source per tool (section 4); the BAD below |
| A value in an event's name, such as a date or an id [4], [5] | one action becomes as many events as there are values | a property (section 3) |
| Two cases or two tenses in one plan | one action has two names in the reports | one case, written at the top of the plan (section 3) |
| A rage-click rate or a heatmap hotspot reported as a problem | a fix for a problem nobody saw | a lead to a replay or a test with users (section 6) |
| A cursor heatmap read as attention [1] | a layout change built on where people did not look | read it as where clicks land (section 6) |
| Replay on for every session, with nobody watching [2] | personal data held, and consent asked, for nothing | a question, a watcher and an end date (section 6) |
| The SDK started at page load with its opt-out settings, read as "nothing leaves" [32], [9] | requests leave before the user answers, and with `opt_out_capturing_by_default` alone PostHog keeps its cookie and local storage | start the SDK when the user agrees (section 5) |
| A ref or a flag that stops the second development call of an analytics effect [28] | it hides React's development check and changes nothing in production | keep the effect as it is, or move the call to the router event (section 8) |
| An agent asked about "last week" with no project named [17] | an answer from the wrong project or the wrong dates | name the project, the window and the filters (section 7) |

The first mistake in code: the client of section 8 with the SDK's own page view turned back on.
The rest of `init` is cut:

```ts
  posthog.init(projectToken, {
    ...
    // Bad: a second source of page views. The SDK counts each change of the path, and the
    // router event in src/main.tsx counts it again, so every screen counts twice
    // (behaviour-analytics.md section 4).
    capture_pageview: "history_change",
    ...
  });
```

Why it is wrong: two sources count every screen twice, and the SDK's own count also ignores the
router's `isPaymentOrLogin` mark, so the pay screen now sends a page view. The fix is section 8's
`capture_pageview: false`, which leaves the router as the one source.

## 10. Where the rules stop holding

- **A server-rendered application.** Sections 4 and 8 hold for a client-rendered application. Page
  views in a framework's own navigation were not read;
  [architecture.md](../../react/architecture/architecture.md) section 14 is the server-rendered
  case.
- **Consent law outside the EU's ePrivacy Directive.** Section 5 rests on the EDPB's guidelines and
  the CNIL's draft. Clarity's enforcement for the UK and Switzerland [13] says nothing about the law
  there, and no text on it was read.
- **Users who are the operator's own staff,** such as the clerks of an internal tool. The consent
  rules for employees were not read.
- **Low traffic.** A funnel over a few dozen people says little; how many people a measure needs is
  [evaluation.md](evaluation.md) section 6.
- **Tools change their rules.** PostHog's defaults move with a date [6], [33], and rage-click rules
  change between SDK versions (section 6). Re-read the tool's docs at the version you install.
- **The cost of the consent rules:** counts cover only the users who agreed, and Google and PostHog
  both warn of the data the strict path loses [25], [19].

## 11. Alternatives considered

- **Load the SDK and send cookieless pings or cookieless events before consent** (Google's advanced
  consent mode, PostHog's `cookieless_mode`) [25], [19]. Not the default: the EDPB puts code that
  makes the browser send information in scope of Art. 5(3) [11], and no source read settles an
  exemption for these pings. A team whose data-protection owner accepts them may take this path; it
  keeps the counts the strict path loses.
- **Start the SDK at page load with its opt-out settings,** as PostHog advises for data quality
  [19]. Not taken: one missed setting sends before the user answers, and even PostHog with every
  setting section 5 names still reads what it stored on the device at start [32]; starting on
  consent is this practice's choice (section 5). The SDK's code may load with the page; only its
  start waits. GA4 is the same case: its advanced mode,
  which loads the tags before consent, sends cookieless pings when consent is denied [25].
- **snake_case event names** (Mixpanel) [5]. Kept as the choice for a team whose main reader is a
  warehouse (section 3).
- **The SDK's own history setting for page views** [6], [22]. Allowed as the one source; the React
  case uses the router because the router knows which route is a payment screen and where a
  redirect lands (section 8).
- **An effect for page views,** as React Router's docs show [30]. react.dev allows it [28]; the
  router event fires once a navigation has finished and says whether the path changed, so it is the
  default (section 8).
- **Rage clicks as findings.** Sentry's docs read three or more clicks on an unresponsive element
  as frustration [10]. Not taken: no study read validates the signal (section 6).
- **Watching replays as the main research method.** Not taken: tests with users are
  [evaluation.md](evaluation.md) section 4, and PostHog's own figures show how little replay gets
  watched [2].
- **A data layer through the application's own backend,** which
  [security.md](../../react/security/security.md) section 12 prefers. The default wherever the team
  needs no SDK feature; section 8 departs from it for a team that does, and names the cost.

## 12. Adoption in existing code

Which answer of [refactoring.md](../refactoring/refactoring.md) section 7 applies depends on the
rule:

- **All code by a date** for a second source of page views and for anything sent or stored before
  consent where consent is needed. The first corrupts every count now; the second sends data the
  user did not agree to.
- **New and touched code** for names and properties. An event that is live keeps its name until the
  plan retires it, because a renamed event starts a new series in every report.

The order of work:

1. List every event the code sends: search for the SDK's capture call, and for the tool's own
   automatic events (page views, autocapture, heatmaps, replay). Write each into the plan with the
   question it answers.
2. Mark the events no question needs, and stop sending them.
3. Run the check of section 4, and remove every page-view source but one.
4. Run the check of section 5 in a new browser profile, and fix what it finds.

Check: the commit that brings the code in line names the answer of refactoring.md section 7 in its
body.

## 13. Review checklist

1. Does every event the change sends appear in the tracking plan, with its question, its
   properties and its consent decision? (section 3)
2. Is each new name an object and a past-tense action, in the plan's case, with no value in it?
   (section 3)
3. Is there one source of page views per tool, counting changes of the path only? (section 4)
4. In a new browser profile, before any answer on the banner, does the application make no request
   to the analytics host and keep no cookie or key of the tool? (section 5)
5. Does every login and payment screen send no event and run no collector? (section 5;
   [security.md](../../react/security/security.md) section 12)
6. Does every URL in an event reach the tool as a path? (section 8;
   [security.md](../../react/security/security.md) section 13)
7. Does replay start only after consent, with a written question, a watcher and an end date?
   (sections 5 and 6)
8. Has a person seen each rage click, dead click or hotspot happen before it is reported as a
   problem? (section 6)
9. For an agent's MCP server: are its write and delete tools denied, and does each request name the
   project and the dates? (section 7)
10. In React: is the client built at the top level of the startup file, does it start the SDK only
    when the user agrees, and does no effect also count page views? (section 8)

## 14. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Jeff Huang, Ryen W. White and Georg Buscher — User See, User Point: Gaze and Cursor Alignment in Web Search (CHI, 2012; research) — https://www.microsoft.com/en-us/research/wp-content/uploads/2012/01/Final_GazeCursor_CHI12.pdf
- [2] Natalia Amorim — Nobody watches their session replays (PostHog blog, 2026; case, the tool's vendor on its own customers' data) — https://posthog.com/blog/nobody-watches-session-replays
- [3] Amplitude — Plan your taxonomy — https://amplitude.com/docs/data/data-planning-playbook
- [4] Twilio Segment — Data collection best practices (Protocols, tracking plan) — https://www.twilio.com/docs/segment/protocols/tracking-plan/best-practices
- [5] Mixpanel — Events and properties — https://docs.mixpanel.com/docs/data-structure/events-and-properties
- [6] PostHog — JavaScript web configuration — https://posthog.com/docs/libraries/js/config
- [7] Amplitude — How to add product analytics to a React app — https://amplitude.com/build/react-analytics
- [8] PostHog — Heatmaps — https://posthog.com/docs/toolbar/heatmaps
- [9] Amplitude — Browser SDK 2, usage guide — https://amplitude.com/docs/sdks/analytics/browser/browser-sdk-2/usage-guide
- [10] Sentry — Rage Click Issues — https://docs.sentry.io/product/issues/issue-details/replay-issues/rage-clicks/
- [11] European Data Protection Board — Guidelines 2/2023 on the technical scope of Art. 5(3) of the ePrivacy Directive, version 2.0 — https://www.edpb.europa.eu/system/files/documents/2024-10/edpb_guidelines_202302_technical_scope_art_53_eprivacydirective_v2_en_0.pdf
- [12] CNIL — Projet de recommandation concernant les outils de rejeu de session, draft of February 2026 — https://www.cnil.fr/sites/default/files/2026-02/projet_de_recommandation_rejeu_session.pdf
- [13] Microsoft — Clarity consent management — https://learn.microsoft.com/en-us/clarity/setup-and-installation/consent-management
- [14] PostHog — MCP tools — https://posthog.com/docs/model-context-protocol/tools
- [15] Sentry — sentry-mcp tool catalog (`get-replay-details.ts`, `search-replays.ts`), `@sentry/mcp-core` 0.42.0 — https://github.com/getsentry/sentry-mcp/tree/main/packages/mcp-core/src/tools/catalog
- [16] Microsoft — Clarity MCP server — https://learn.microsoft.com/en-us/clarity/third-party-integrations/clarity-mcp-server
- [17] Edoardo Dusi — How we analyze content performance with Claude Code, Storyblok and PostHog (Storyblok, 2026; case) — https://www.storyblok.com/mp/how-we-analyze-content-performance-with-claude-code-storyblok-and-posthog
- [18] Cory Slater — What we learned from our first 400k Replay Vision scans (PostHog blog, 2026; case, the tool's vendor on its own product) — https://posthog.com/blog/a-scanner-that-watches-everything-sees-nothing
- [19] PostHog — Controlling data collection — https://posthog.com/docs/privacy/data-collection
- [20] CNIL — Ordre du jour de la séance plénière du 8 octobre 2026 — https://cnil.fr/fr/ordre-du-jour-de-la-seance-pleniere-du-8-octobre-2026
- [21] CNIL — Cookies et autres traceurs (topic page) — https://www.cnil.fr/fr/thematique/cookies-et-autres-traceurs
- [22] Google — Enhanced measurement events (Analytics Help) — https://support.google.com/analytics/answer/9216061?hl=en
- [23] Google — Measure single-page applications (Google Analytics developer guide) — https://developers.google.com/analytics/devguides/collection/ga4/single-page-applications?technology=websites
- [24] Google — Set up consent mode on websites (Tag Platform developer guide) — https://developers.google.com/tag-platform/security/guides/consent?consentmode=advanced
- [25] Google — Consent mode on websites and mobile apps (Analytics Help) — https://support.google.com/analytics/answer/9976101?hl=en
- [26] React — `<StrictMode>` (react.dev reference) — https://react.dev/reference/react/StrictMode
- [27] React — You Might Not Need an Effect, "Initializing the application" (react.dev) — https://react.dev/learn/you-might-not-need-an-effect#initializing-the-application
- [28] React — Synchronizing with Effects, "Sending analytics" (react.dev) — https://react.dev/learn/synchronizing-with-effects#sending-analytics
- [29] TanStack — Router Events (`docs/router/guide/router-events.md`) — https://github.com/TanStack/router/blob/main/docs/router/guide/router-events.md
- [30] React Router — `useLocation` (`docs/api/hooks/useLocation.md`) — https://github.com/remix-run/react-router/blob/main/docs/api/hooks/useLocation.md
- [31] PostHog — React (posthog-js and `@posthog/react`) — https://posthog.com/docs/libraries/react
- [32] PostHog — posthog-js source (`lib/src/posthog-core.js`, `lib/src/posthog-persistence.js`, `lib/src/remote-config.js`, `lib/src/heatmaps.js`, `lib/src/page-view.js`, `lib/src/session-props.js`, `lib/src/extensions/history-autocapture.js`), 1.442.0 — https://unpkg.com/browse/posthog-js@1.442.0/lib/src/
- [33] PostHog — `@posthog/types`, `src/posthog-config.ts`, 1.418.0 — https://unpkg.com/@posthog/types@1.418.0/src/posthog-config.ts
- [34] PostHog — `@posthog/browser-common`, `dist/utils/event-utils.mjs`, 0.10.1 — https://unpkg.com/@posthog/browser-common@0.10.1/dist/utils/event-utils.mjs
- [35] TanStack — `@tanstack/router-core` source (`dist/esm/router.js`, `dist/esm/load-client.js`), 1.171.39 — https://unpkg.com/browse/@tanstack/router-core@1.171.39/dist/esm/
- [36] Anthropic — Configure permissions (Claude Code docs) — https://code.claude.com/docs/en/permissions
- [37] PostHog — posthog-js, `dist/module.mjs` (the default bundle), 1.442.0 — https://unpkg.com/posthog-js@1.442.0/dist/module.mjs
- [38] PostHog — `@posthog/browser-common`, `dist/feature-flags.mjs`, 0.10.1 — https://unpkg.com/@posthog/browser-common@0.10.1/dist/feature-flags.mjs
- [39] PostHog — PostHog MCP FAQ and advanced setup — https://posthog.com/docs/model-context-protocol/faq
