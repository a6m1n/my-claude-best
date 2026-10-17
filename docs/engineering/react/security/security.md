# React security rules

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. What the browser side can and cannot protect](#2-what-the-browser-side-can-and-cannot-protect)
- [3. XSS: what JSX escapes, and the sinks it does not](#3-xss-what-jsx-escapes-and-the-sinks-it-does-not)
- [4. Sanitising HTML, and Trusted Types](#4-sanitising-html-and-trusted-types)
- [5. Content-Security-Policy and the other headers](#5-content-security-policy-and-the-other-headers)
- [6. Sessions and tokens](#6-sessions-and-tokens)
- [7. CSRF and CORS](#7-csrf-and-cors)
- [8. Server-side React](#8-server-side-react)
- [9. Secrets and public settings](#9-secrets-and-public-settings)
- [10. Supply chain: packages, lockfile, CI](#10-supply-chain-packages-lockfile-ci)
- [11. The dev server](#11-the-dev-server)
- [12. Third-party scripts, postMessage, iframes, redirects](#12-third-party-scripts-postmessage-iframes-redirects)
- [13. Data the browser exposes](#13-data-the-browser-exposes)
- [14. Automation: lint rules and header scanners](#14-automation-lint-rules-and-header-scanners)
- [15. Common mistakes](#15-common-mistakes)
- [16. Where the rules stop holding](#16-where-the-rules-stop-holding)
- [17. Review checklist and the OWASP Top 10:2025](#17-review-checklist-and-the-owasp-top-102025)
- [18. Sources](#18-sources)

## 1. Purpose and the one rule

This file is for everyone who writes or reviews the browser side of a React application and the
backend that holds its session (a Backend for Frontend, BFF for short, or the API): people and AI
agents alike. Read it before you put data from outside the application on the page, spread an
object from outside as props, handle a session or a token, keep or send a credential, set the
session cookie, change how the session starts, times out or ends, change the API's Cross-Origin
Resource Sharing (CORS) or cross-site request forgery (CSRF) checks, add an environment variable, a
dependency, a third-party script, a response header or a CI step, change the dev server's
settings, add a route, a WebSocket or a file download to its API or to the server that holds its
session, set up its query client, add polling, or build the shell its screens share. Every line
that carries a read date is to be distrusted six months after that date until it is read again,
the earliest on 2027-04-01; the README's "How to adopt" says how to list those lines.

The default case is a client-rendered application built with Vite and served as static files. A
framework that renders on the server or runs Server Functions is the second case: section 8 and
parts of section 5 add its rules. The examples use the billing screens of `Acme Corp`, and
[security-example.md](security-example.md) shows the whole set in one application. The example
assumes the page at one origin and the API at another origin of the same site
(`https://app.example.com` and `https://api.example.com`). That is why the API answers CORS
preflights for the page's origin, why the request sets `credentials: "include"`, and why a
`SameSite` cookie is still sent; an API on the page's own origin needs no CORS at all. Where files
live is [architecture.md](../architecture/architecture.md) section 3; which tool and which version
is [libraries.md](../architecture/libraries.md) section 2; how far to trust a Claude Code plugin or
skill is [designing-with-claude-code.md](../design/designing-with-claude-code.md) section 7. Many
rules here come from OWASP, the Open Worldwide Application Security Project, a non-profit
foundation; what its Top 10 and its Application Security Verification Standard (ASVS) are, and how
to work with them, is in [section 17](#what-the-owasp-top-10-is-and-how-to-work-with-it).

The rules stand on six terms, in this file's own wording. The cookie, CORS and CSRF rules use the
first four; the last two are this file's own:

- An origin is a URL's scheme, host and port, such as `https://app.example.com`; two URLs that
  differ in any of the three are two origins [1]. CORS works by origin [1].
- A site is a URL's scheme and registrable domain, such as `https://example.com`, so
  `https://app.example.com` and `https://api.example.com` are two origins of one site. `SameSite`
  cookies and the `same-site` value of Fetch Metadata work by site.
- A top-level navigation loads a new page into the whole window, as a link, a form or a change of
  `location` does; a `fetch`, an image and a frame are not top-level navigations.
- A preflight is the `OPTIONS` request a browser sends before a cross-origin request whose method
  or headers are outside the CORS safelist, to ask the server whether it allows that request
  [2], [1].
- **Write it down** means: a choice goes into the project's decision log, and a value goes into the
  BFF's settings with its reason next to it
  ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
  section 2, "The session's life", says more).
- **The sign-out path** is what the page runs when the session has ended: it clears what the
  session loaded and sends the user to sign in (section 6, "Timeouts and refresh").

The one rule: **anything the browser holds, a script on the page can read, and anything the
browser decides, the user can change.** So the browser side keeps no secret, makes no access
decision, and lets no outside text and no unchecked package run as code. Each section below is
one way that rule breaks, and what stops it.

Why it matters:

- Once an attacker's script runs on the page, it acts as the user. RFC 10017 names what such a
  script does to an OAuth client in its section 5.1: "Single-Execution Token Theft", "Persistent
  Token Theft", "Acquisition and Extraction of New Tokens" and "Proxying Requests via the User's
  Browser" [3].
- Code reaches the page by more paths than the team's own commits: a dependency, a third-party
  script, the build in CI. In 2025 and 2026 each of these paths carried an attack (section 10).

Every rule names the threat it stops. Where an incident showed a control's gap, the rule says
what it does not stop.

## 2. What the browser side can and cannot protect

The browser side can:

- keep data from outside the application from running as script (sections 3 and 4);
- limit what an injected script can load, run and frame (section 5);
- keep tokens out of reach of script, by holding a session cookie that script cannot read
  (section 6);
- keep secrets out of the bundle and its source maps (section 9);
- choose which code it installs and builds (section 10);
- keep credentials and user input out of URLs, logs and recordings (section 13).

It cannot:

- **Decide who may do what.** Hide a button for the user's sake, never as a control. OWASP's Top
  10:2025 ranks broken access control first and says access control works only in trusted
  server-side code, and its Authorization cheat sheet tells developers never to rely on a check in
  the client [4], [5]. The server checks every request again: who the user is, whether
  they may touch that record, and the shape of the data [5]. A check in a form helps the user
  fill it in; it protects nothing.
- **Stop a script that already runs on the page from acting as the user.** RFC 10017, section 8:
  "Since the attacker's code becomes indistinguishable from the legitimate application's code, the
  attacker will always be able to request tokens from the provider in exactly the same way as the
  legitimate application code" [3]. The rules here limit what such a script takes away;
  only preventing the injection stops it.
- **Protect a user whose machine is infected.** RFC 10017, section 8.6: "More and more malware is
  specifically created to crawl users' machines and look for browser profiles to obtain
  high-value tokens and session cookies, resulting in account-takeover attacks" [3]. An
  `HttpOnly` cookie stops a script on the page, not malware on the disk. OWASP's Cookie Theft
  Mitigation cheat sheet lists what a server can add, such as comparing request signals with those
  seen at login, and Device Bound Session Credentials, which tie a session cookie to a key in the
  machine's hardware in Chrome on Windows since 2026 (Google, read 2026-10-15); this practice
  treats them as extras a BFF may add, not rules [6], [7].

## 3. XSS: what JSX escapes, and the sinks it does not

React escapes every string it renders as text, so `{invoice.customerName}` shows `<script>` as
characters on the screen, and a value it sets on a named prop cannot break out of that prop
(De Ryck, 2020) [8]. That covers most of a screen. It does not decide whether the value is
safe for what the prop does, and it does not reach the places where a string becomes HTML, a URL,
a set of props, a style or code. OWASP's XSS cheat sheet asks you to know where your framework
stops protecting you, and names React's gaps: HTML set without sanitising, and URL values, since
React 19 blocks only `javascript:` URLs (read 2026-10-16) [9].

| Sink | Why escaping does not reach it | The rule |
|---|---|---|
| `dangerouslySetInnerHTML` | the string is parsed as HTML; React's docs warn that markup from a source that is not fully trusted makes XSS easy [10] | one component writes HTML into the page and sanitises at the sink (section 4) |
| a URL from data in `href` or `src` | React 19 refuses a `javascript:` URL and no other scheme; `data:` and other schemes pass, and the refusal is new in React 19, listed there as a breaking change [11], [12] | parse the URL and allow a short list of schemes |
| an object from outside spread as props | the object chooses the props, `dangerouslySetInnerHTML` and `href` among them | pass each prop by name, from a value you checked |
| a Markdown renderer | escapes HTML and checks URLs by default; unsafe once its URL check is overridden or raw HTML is turned on [13] | keep the renderer's defaults; raw HTML only through its sanitiser plugin [13] |
| MDX | MDX from outside can carry JavaScript expressions that run when it is compiled [14] | MDX only from people who may change the application's code |
| JSON written into a `<script>` tag on the server | a `</script>` inside a value ends the tag [15] | let the framework serialise; otherwise escape `<` |
| a user value inside runtime CSS-in-JS | the libraries insert the value into the stylesheet without escaping it [16] | map the user's choice to a fixed value in code, or set it through the `style` prop [16] |
| `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` through a ref | React is not involved, so nothing escapes; OWASP's DOM-based XSS cheat sheet names all but `insertAdjacentHTML`, which this practice adds [17] | set `textContent`, or build nodes with `createElement` [17] |
| `eval`, `new Function`, a string passed to `setTimeout` or `setInterval` | the text runs as code [17] | never; parse data with `JSON.parse` [17] |

OWASP's XSS cheat sheet also names the places untrusted data never goes, whatever the encoding:
inside a `<script>` element, a `<style>` element and an HTML comment [9].

- **When a URL comes from data, parse it with `URL` and allow only the schemes the link needs,**
  such as `https:` and `mailto:`. React 19's guard replaces a `javascript:` URL in `href`, `src`
  and a few other URL props with one that throws, and checks no other scheme, so a `data:` URL
  passes it [11], [12], [8]. That is why this practice checks the scheme itself. An
  allowlist also stops a scheme nobody planned for; a check for `javascript:` stops one scheme.
  Philippe De Ryck (2020) recommends an allowlist over a blocklist, and react-markdown's default
  list (`http`, `https`, `irc`, `ircs`, `mailto`, `xmpp` and relative URLs) is a maintainer's
  reference set [8], [13]. A relative path the application builds itself needs no check.
  Section 15 shows the BAD link and the GOOD one.
- **When data from outside the application describes an element, pass each prop by name from a
  checked value; never spread the object onto the element.** A spread object sets every prop it
  holds, so a response that carries a `dangerouslySetInnerHTML` key puts HTML on the page with no
  sink in sight (De Ryck, 2020) [18]. How props are passed in general is
  [components.md](../components/components.md) section 3. Section 15 shows the pair.
- **When you render Markdown from outside, keep the renderer's defaults.** react-markdown escapes
  HTML and checks URLs unless told otherwise [13]. A 2026 advisory describes an application
  that passed `urlTransform={(url) => url}` and got stored XSS with no `dangerouslySetInnerHTML`
  anywhere [19]. The source for the raw-HTML row is react-markdown's README [13].
- **Treat MDX from outside as code.** MDX from outside can carry JavaScript expressions that run
  when it is compiled [14]. A 2026 advisory in next-mdx-remote let untrusted MDX run code on
  the server; its version 6 blocks JavaScript expressions by default [14].
- **When the server writes state into a `<script>` tag, let the framework serialise it, or escape
  every `<` as `\u003c`.** Redux's server-rendering docs and Next.js's JSON-LD guide both show
  `.replace(/</g, '\\u003c')` after `JSON.stringify`, and `serialize-javascript` escapes the same
  characters [20], [21], [15]. A plain `JSON.stringify`
  does not, so a customer name that holds `</script>` ends the script and starts HTML
  [15]. Serialising helpers and framework script components have had advisories
  of exactly this kind (serialize-javascript in 2024, a Next.js script component in 2026)
  [22], [23].
- **Never put a user's value into a CSS-in-JS template.** styled-components and Emotion inserted
  the value into a stylesheet without escaping it as of 2019 (Nelson, 2019) [16]. This rests
  on one practitioner article and a styled-components issue; the maintainers' docs were not read
  (2026-10-01).
- **When code reaches the DOM through a ref, set `textContent` or build nodes; never assign
  HTML.** OWASP's DOM-based XSS cheat sheet lists `innerHTML`, `outerHTML`, `document.write`, and
  `setTimeout`, `setInterval` or `Function` called with a string as dangerous sinks, and asks for
  the safe ones instead [17].
- **Never run text as code.** The source is OWASP's DOM-based XSS cheat sheet [17]. The lint
  rules that catch these are off by default (section 14).

## 4. Sanitising HTML, and Trusted Types

Prefer no HTML at all: OWASP's DOM-based XSS cheat sheet asks for `textContent` and DOM methods
before any HTML sink [17]. When outside data must carry formatting, Markdown with the
renderer's defaults is the safer form (section 3). When it must be HTML:

- **Write HTML into the page from one component, and render text everywhere else.** The
  component takes the HTML string as its only prop, sanitises it, and is the one place that sets
  `dangerouslySetInnerHTML`. De Ryck (2020) advises wrapping the sanitiser in reusable components;
  one component gives one place to review and one lint suppression to find [18].
  Check: `react/no-danger` is on (section 14), and `grep -rn "react/no-danger" src/` prints one
  line: the suppression in that component.
- **Sanitise right at the sink, in the same render, with DOMPurify.** A string cleaned earlier can
  be joined with another string, or changed, on its way to the page. DOMPurify's 2026 advisory on
  a bypass through parsing again asks you to keep the context stable from the sanitiser to the
  sink [24].
- **Never change, join or parse again what the sanitiser returned.** DOMPurify's README warns that
  changing sanitised HTML can undo the sanitising, and MDN says that HTML serialised and parsed
  again with `innerHTML` is no longer sanitised [25], [26].
- **Start from a profile, such as `USE_PROFILES: { html: true }`, and widen the allowed tags only
  for a need you can name.** A profile allows plain HTML and leaves SVG and MathML out [25].
  DOMPurify's 2026 releases fixed bypasses that worked only when risky tags were allowed
  [27].
- **Update DOMPurify with your routine updates, never skip it.** Its 2026 releases fixed, among
  others, a bypass of the default call through a prototype-pollution bug anywhere on the page, and
  DOM clobbering [27], [28]. A sanitiser is code with advisories like
  any other.
- **On the server, run DOMPurify with the newest jsdom, never with happy-dom.** DOMPurify's README
  says older jsdom releases have known XSS bugs and does not consider happy-dom safe [25].
- **Do not move to the HTML Sanitizer API yet.** `Element.setHTML()` is not Baseline: MDN says it
  does not work in some of the most used browsers (read 2026-10-01) [26]. When it is, it
  removes scripts, frames and event handlers without a library; re-check it [26].

Trusted Types moves the check into the browser. With the policy directive
`require-trusted-types-for 'script'`, the browser throws when a plain string reaches an HTML sink
such as `innerHTML`, unless a policy named `default` exists, which the browser then runs on the
string; only a value a policy created passes, and the `trusted-types` directive lists the allowed
policy names (MDN, web.dev) [29], [30]. Trusted Types is Baseline since February
2026 (MDN, read 2026-10-01) [29]. React passes a `TrustedHTML` value given as `__html` to the
browser as it is (React's docs) [10].

- **Once the policy of section 5 is enforced, add Trusted Types in report-only mode, fix what the
  reports show, then enforce it.** web.dev gives this order [30]. No measured study of
  how many libraries break under Trusted Types was found (2026-10-01): the report-only phase is
  where you learn it for your own dependencies.
- **Make the policy sanitise.** A policy that returns its input unchanged turns the check off.
  MDN's example policy calls `DOMPurify.sanitize` in `createHTML`, DOMPurify can return a
  `TrustedHTML` value itself (`RETURN_TRUSTED_TYPE: true`), and React's docs say the policy must
  still make sure its input is trusted and sanitised [29], [25], [30],
  [10]. Inside a policy's `createHTML`, DOMPurify's README asks for the opposite setting:
  "`RETURN_TRUSTED_TYPE: false` is required, as `createHTML` expects a normal string" [25].
## 5. Content-Security-Policy and the other headers

A Content-Security-Policy (CSP) tells the browser which scripts, styles, connections and frames
the page may use. It does not prevent an injection; it limits what an injected script can do when
one gets through. Most deployed policies give that limit up: the 2025 Web Almanac (HTTP Archive
crawl) found a CSP on 21.9% of sites, and 92% of those policies carry `'unsafe-inline'`, which
lets an injected inline script run unless the policy also has a nonce or a hash [31]. A 2016
Google study found bypasses in 94.72% of all distinct policies, and 75.81% of distinct policies
used script allowlists an attacker could get around [32].

### The policy for a static single-page application

- **Send `script-src 'self'` with no `'unsafe-inline'` and no `'unsafe-eval'`, together with
  `object-src 'none'`, `base-uri` and `frame-ancestors`.** A plain Vite production build writes no
  inline script: Vite bundles inline module scripts and its preload polyfill into files (Vite's
  HTML plugin source, read on its main branch 2026-10-01) [33]. The reference
  application's built `index.html` shows it: one module script with `src`, two preload links, one
  stylesheet link. web.dev's strict CSP uses hashes on static pages to allow chosen inline
  scripts; a build with no inline script has nothing to hash, and `'self'` allows its files
  [34]. The full policy is in [security-example.md](security-example.md), and the BAD form
  follows below.
  Check: after a build that changes `index.html`, a Vite plugin or the Vite version, open
  `dist/index.html`: every `<script>` has a `src`, and there is no `<style>` element and no
  `style=` attribute.
- **Serve a file that users upload and that a browser runs or renders as a document, such as HTML
  or SVG, from another site: a domain on the Public Suffix List or a registrable domain of its
  own, never a subdomain of the application's site.**
  `'self'` allows every script file the application's origin serves, so an upload served from that
  origin could be loaded as script; on the API's origin it would run with the session cookie
  ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
  section 3), and on a subdomain of the site it would be the sibling subdomain that the cookie and
  CSRF rules of
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
  sections 2 and 3 defend against. web.dev's article (Dworken, 2023, read 2026-10-16) serves active
  content from a domain on the Public Suffix List [35]. The same article calls a
  `Content-Security-Policy: sandbox` header on the file's response the simplest option, and likely
  enough when Spectre-class and renderer-compromise attacks are outside the threat model, so a team
  whose threat model leaves those attacks out may send that header instead, and a team whose threat
  model includes them uses the separate site [35].
- **Serve an inactive file that users upload, such as an image or a download, from the API's
  origin under the response headers of
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  3, for the page to show as the blob rule of section 7 says,** since the same article allows
  inactive content without a sandbox domain when its response carries safe headers [35].
- **Allow `data:` in `img-src` only, never in `script-src`.** Vite inlines small assets as `data:`
  URIs; its docs say to allow `data:` where those assets load, or set
  `build.assetsInlineLimit: 0`, and never to allow `data:` for scripts [36].
- **Do not use a nonce on a static host.** A nonce must change with every response, and a static
  file is the same for every request. Vite's `html.cspNonce` writes a placeholder that a server
  replaces on each request; Vite's docs give no hash recipe, so a static host uses `'self'`
  (read 2026-10-01) [36]. A fixed nonce in a static file is the reuse failure of the next
  subsection.

Bad: `'unsafe-inline'` in `script-src`. This is the reference policy with that one word added.

```text
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self'; img-src 'self' data:; connect-src 'self' https://api.example.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'
```

An injected `<script>` element or an `onerror=` attribute now runs, which is the attack the
policy is there to stop. Next.js's CSP guide shows this form as its example without nonces;
web.dev's strict CSP leaves it out of its policies, and adds it only as a fallback for very old
browsers, which every browser that supports a nonce or a hash ignores [37], [34].

Good: the policy line of `public/_headers` in the reference application, as written there, with
the comment that says why. The rest of the file, the Trusted Types lines and the other headers,
is cut; the whole file is in [security-example.md](security-example.md).

```text
/*
  # No 'unsafe-inline' in script-src: the build puts no script into the page itself, so an
  # injected one stays blocked (security.md section 5).
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self' https://api.example.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'
  ...
```

It fixes the one problem: only script files from the application's own origin run, so an
injected inline script or event handler is blocked. The policy was checked only against the built
`index.html` (no inline script, no inline style); no tool and no browser evaluated it.

### The policy for a server-rendered application

- **Use a strict policy built on a nonce.** It is a new random value per response, set on every
  script tag the server renders, with `'strict-dynamic'`, `object-src 'none'` and `base-uri 'none'`.
  This is the form that OWASP's CSP cheat sheet and web.dev give; `{RANDOM}` stands for the
  per-response value [38], [34]:

  ```text
  Content-Security-Policy: script-src 'nonce-{RANDOM}' 'strict-dynamic'; object-src 'none'; base-uri 'none';
  ```

- **Create the nonce per response and never cache a response that carries one.** A study of the
  top 50,000 sites found 598 of 2,271 nonce-based sites reusing one nonce across responses, often
  because a cache stored the HTML (2023) [39]. A reused nonce is a value an attacker can read
  and copy.
- **Add the nonce to the tags your server renders, never through a step that stamps every script
  tag in the output.** OWASP: such a step stamps the attacker's injected tags too [38].
- **Keep outside data out of nonced scripts.** A nonce does not help when the injection is into
  the body or the `src` of a nonced script itself (web.dev) [34].
- **Know what `'strict-dynamic'` trusts: every script that a nonced script loads.** A nonced tag
  manager therefore runs every Custom HTML tag added in its own console (Raxis, 2026)
  [40]. Next.js's docs show that setup [37]. Treat that console as a way to deploy
  code (section 12).
- **Next.js: use its nonce setup and accept dynamic rendering, or its experimental SRI hashes for
  static pages; never its example without nonces.** Its nonce setup needs dynamic rendering, which
  turns off static generation and, by default, CDN caching for those pages [37]. Its
  experimental SRI hashes keep a page static but cannot cover scripts generated at run time
  [37]. Its example without nonces uses `'unsafe-inline'`, the BAD form above (Next.js CSP
  guide, read 2026-10-01) [37].
- **Vite behind a server: set `html.cspNonce` and have the server replace the placeholder with a
  fresh value on each request,** as Vite's docs ask [36]. The same option writes a
  `<meta property="csp-nonce">` tag, which some CSS-in-JS libraries read (next subsection)
  [36], [41].

### style-src

- **Ship styles as files built at build time, and send `style-src 'self'`.** A stylesheet built
  into a file needs nothing inline; the reference application's build has one stylesheet link and
  no inline style.
- **React's `style` prop is not blocked.** By MDN's `style-src` page, a property set through an
  element's `style` object is allowed, while a `style` attribute in HTML,
  `setAttribute("style", …)` and `style.cssText` are blocked [42]. React's own source was not
  read on how it sets the prop; this is MDN's rule applied to React, and it holds for client
  rendering only [42].
  Server-rendered HTML that carries `style="…"` needs `'unsafe-inline'` in `style-src`, or a hash
  of each value together with `'unsafe-hashes'`; a nonce covers only `<style>` elements [42].
- **Give runtime CSS-in-JS that inserts `<style>` tags the per-response nonce.** Emotion takes it
  as the `nonce` option of `createCache`; styled-components 6.4 and later read it from the
  `<meta property="csp-nonce">` tag that Vite writes when `html.cspNonce` is set (owners' docs,
  read 2026-10-01) [43], [44], [36], [41]. A
  static host has no nonce to give, so such a library there needs `'unsafe-inline'` in
  `style-src`: prefer CSS built into files.

### Rolling it out and delivering it

- **Send a new policy as `Content-Security-Policy-Report-Only` first, read the reports, then
  enforce it.** MDN's CSP guide starts this way, and web.dev offers report-only as an optional step
  before enforcing: a report-only policy blocks nothing, and its reports show what the enforced
  one would block [45], [46], [34]. Collect reports with `report-to`
  and the `Reporting-Endpoints` header, and add `report-uri` for older browsers (OWASP) [38].
  Before the first report-only deploy, name the receiver of the reports, such as a hosted
  collector or the report intake of
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  3; without one, do not start report-only, since a violation then shows only in the browser console
  of whoever visits ([security-example.md](security-example.md) section 6).
- **When a policy starts as report-only, write down the date by which it is enforced, and add a
  task for that date, with an owner, to the team's tracker, linked from the decision log's entry
  ("Write it down" in
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  2 says where),** since a report-only policy blocks nothing, and without a written end it can stay
  that way, while the decision log reminds nobody on the date; the rule is this practice's choice.
- **Send the policy as an HTTP header, not in a `<meta>` tag.** MDN says a `<meta>` policy suits a
  client-rendered single-page application with only static files, but it does not support every
  feature: `frame-ancestors` is not supported there, and a report-only policy cannot be delivered
  that way [45], [46], [47].
- **Set the headers in your host's file.** Netlify and Cloudflare Pages read a `_headers` file
  from the folder they publish; Vercel reads the `headers` array in `vercel.json` (vendors' docs,
  read 2026-10-01) [48], [49], [50]. Vite copies `public/_headers`
  into `dist/` as it is [41]. Copy the format, not a sample policy; the rule is
  this practice's choice.
- **After every deploy that changes a header, check the deployed result** with the scanners of
  section 14.

### The other headers

The values are OWASP's HTTP Headers cheat sheet's unless the row says otherwise [51].

| Header | Value | What it stops | In the example |
|---|---|---|---|
| `Content-Security-Policy` | the policy above | injected script loading or running; the page being framed by another site (`frame-ancestors 'none'`) | yes |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` [51] | a later visit going over plain HTTP, where the traffic can be read and changed | yes, without `preload` |
| `X-Content-Type-Options` | `nosniff` [51] | the browser guessing a file's type and running it as script | yes |
| `Referrer-Policy` | `strict-origin-when-cross-origin` [51] | the path and query string, which can hold sensitive values, going to other sites (MDN; it is also the browsers' default) [52] | yes |
| `Permissions-Policy` | `geolocation=(), camera=(), microphone=()`, plus any other feature the application does not use [51] | a script or a frame using a device feature the application never needs | yes, plus `payment=()` |
| `Cross-Origin-Opener-Policy` | `same-origin` [51] | a window this page opened, or that opened it, keeping a handle to it [53] | yes |
| `X-Frame-Options` | `DENY` [51] | framing, in old browsers that lack `frame-ancestors`; a browser that sees both obeys `frame-ancestors` (OWASP's Clickjacking cheat sheet) [54] | no |
| `Cross-Origin-Resource-Policy` | `same-site` [51] | another site loading this site's files into its own pages | no |
| `Cross-Origin-Embedder-Policy` | `require-corp` [51] | part of cross-origin isolation; it blocks every file from another origin that does not opt in, so test it on its own before you send it [51] | no |
| `X-XSS-Protection` | `0` [51] | turns off the XSS filter old browsers had, which OWASP says can create XSS holes in otherwise safe sites [51] | no |
| `Cache-Control` | `no-store`, on the responses section 13 names | a shared cache keeping one user's data for the next user (OWASP's Session Management cheat sheet) [55] | the API's responses, not this file |
## 6. Sessions and tokens

In this file the BFF is the server that holds the OAuth tokens and sets the session cookie. In
sections 6 and 7, "the server" means the component that receives the browser's session cookie:
the BFF, which in the example is also the API at `https://api.example.com`, so "the API" names it
too. If your own server logs the user in and there is no identity provider, that server plays the
BFF's part: the cookie, session-life and CSRF rules apply unchanged; the rules about the identity
provider (its tokens, refresh-token revocation, and RP-initiated, back-channel and front-channel
logout) do not; ending the session at logout still does. With such a first-party login, keep the
session's state on the server (this practice's choice). With the session's state in the cookie,
there would be no provider tokens to revoke at logout. The list of ended sessions, whose rules are
in [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
section 2, "Logout", would then be the only control that stops a copy of the cookie.

With a first-party login, skip these parts of
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md), which
hold only with an identity provider:

- "The login cookie" and "Forwarding to resource servers", whole;
- in "Timeouts and refresh", the refresh rules, from the `invalid_grant` rule to the rule on a
  provider that rotates refresh tokens and has no reuse window;
- in "Logout", the rules on revoking the tokens and on RP-initiated, back-channel and
  front-channel logout;
- in "The login and logout responses", the login callback's response;
- in its section 3, the rules on refreshing before a request is forwarded and on a resource server's
  `401`.

Any other rule that needs an identity provider says `with an identity provider` in its prefix.

In this section, every rule the page follows starts with `Page:` or
`Page, with an identity provider:`, or with `Browser-only client:` where the page itself holds the
tokens, so a search for those words finds them all. In section 7, the page's rules are under "What
the React code does", and in "Fixing a CORS error" they are the bullets that start with "The page"
or `Page:`. With a BFF, the page's only token rules are the two bans below: no token in
`localStorage` or `sessionStorage`, and no token in a cookie written from JavaScript. The BFF's own
rules start at
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
2, "The session cookie".

Preventing XSS comes first: when an attacker's script runs on the page, no storage choice stops
it from acting as the user (section 2). De Ryck argued in 2020 that storage hardly matters once
XSS exists [56]. The storage choice still decides what the attacker takes away: a stolen token
works from the attacker's own machine until it expires, while a session cookie that script cannot
read works only through the user's open browser. RFC 10017, which De Ryck co-wrote, ranks the
patterns "in decreasing order of security" (section 6), and this practice follows the RFC [3].
Sender-constrained tokens narrow that gap for a browser-only client, since a token bound to a key
the script cannot export cannot be used on another machine (RFC 10017 section 9.2), but the BFF
still wins: no defence in the browser stops the attacker's script from running a new flow to obtain
tokens (RFC 10017 section 6.3.4.2) [3].

RFC 10017 (BCP 212, August 2026) gives three patterns, "presented in decreasing order of
security" (section 6) [3]:

| Pattern | Who holds the tokens | What the RFC says |
|---|---|---|
| Backend for Frontend (BFF), section 6.1 | the backend, as a confidential OAuth client; the browser holds only an `HttpOnly` session cookie | "This architecture is strongly recommended for business applications, sensitive applications, and applications that handle personal data." The same section names the cost: "The architecture of a BFF is significantly more complicated than a browser-only application. It requires deploying and operating a server-side BFF component." (6.1.4.3) [3] |
| Token-mediating backend, section 6.2 | the backend gets the tokens and hands the access token to the browser | its security properties "lie somewhere between using a BFF and running" a browser-only application [3] |
| Browser-based OAuth client, section 6.3 | the browser, as a public client | last in the order; all four attack scenarios of section 5.1 apply to it [3] |

- **Choose the BFF for a business application, a sensitive one, or one that handles personal
  data,** since that is the RFC's recommendation, and a billing screen is all three [3].
- **Page: with a BFF, read, store and send no token,** so no token exists in JavaScript to steal:
  the page sends requests with `credentials: "include"`, and the browser adds the cookie (section
  7). Section 15 shows the BAD and the GOOD.
- **Page: treat the route guard as the user's convenience, never as access control,** since access
  control stays on the server (section 2 of this file) [4], [5]. Where the route guard and
  the sign-out handler live is [architecture.md](../architecture/architecture.md) section 10.
- **Know what a BFF does not stop.** A script on the page can still send requests to the BFF
  through the user's session: the RFC's fourth scenario, "Proxying Requests via the User's
  Browser" [3]. And a cookie session brings CSRF back (Auth0, 2026), so section 7 is part of
  the same choice [57].
- **Browser-only client: if you choose one for a lower-risk application, use the authorization
  code flow with PKCE, never the implicit grant** (RFC 10017 section 7.2; RFC 9700 sections 2.1.1
  and 2.1.2), so no access token travels in a redirect URL, where it can leak and be replayed
  [3], [58], [59].
- **BFF or browser-only client: use a maintained library or the provider's SDK for the OAuth
  flow, never your own code** (OWASP's Authentication cheat sheet asks to prefer well-maintained
  libraries or SDKs; writing the flow yourself is this practice's ban), so the flow's checks come
  from code that others review and keep patched [60]. The library runs the protocol: the
  authorization request, `state`, the nonce, PKCE, the token exchange and the ID token checks. The
  step-up's checks and the bookkeeping of its login cookie are the team's own code around it
  ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
  section 2, "The login cookie" and "Re-authentication").
- **Browser-only client: set the SDK's token storage option explicitly.** Vendors' defaults
  differ: Auth0's SPA SDK keeps tokens in memory, MSAL.js in `sessionStorage`, Okta's auth-js in
  `localStorage` [61], [62], [63].

What RFC 10017 section 8 says about each place a token can be kept [3]:

| Where | RFC 10017, verbatim | Section |
|---|---|---|
| a cookie set by the BFF, `HttpOnly` | the RFC keeps it apart from cookies set by script: "this practice is different from the use of cookies in a BFF (discussed in Section 6.1.3.2), where the cookie is inaccessible to JavaScript and is intended to be sent to the backend." [3] | 8.1 |
| a cookie written from JavaScript | "Because of these unintentional side effects of using cookies for JavaScript-based storage, this practice is NOT RECOMMENDED." [3] | 8.1 |
| a Service Worker | "A Service Worker [W3C.service-workers] offers a fully isolated environment to keep track of tokens. These tokens are inaccessible to the client application, effectively protecting them against exfiltration." But "the use of a Service Worker does not prevent an attacker from obtaining a new set of tokens", and "the Service Worker MUST NOT store tokens in any persistent storage API that is shared with the main window" [3]. | 8.2 |
| a Web Worker | "The security properties of using a Web Worker are identical to using Service Workers. When tokens are exposed to the application, they become vulnerable." When the worker keeps the refresh token and hands the access token to the page, "the application's own refresh token is effectively protected against exfiltration, but the access token is not." [3] | 8.3 |
| memory | "Another option is keeping tokens in memory without using any persistent storage. Doing so limits the exposure of the tokens to the current execution context only but has the downside of not being able to persist tokens between page loads." A closure that hides them does not hold: "Using prototype poisoning, an attacker can substitute these functions with malicious versions" [3]. | 8.4 |
| `localStorage` | "localStorage does not protect against unauthorized access from malicious JavaScript, as the attacker would be running code within the same origin, and as such, would be able to read the contents of the localStorage." [3] | 8.5 |
| `sessionStorage` | it "is not shared between multiple tabs open to pages on the same origin, which slightly reduces the exposure of the tokens in sessionStorage." [3] | 8.5 |
| any of the above | "Note that the main difference between these patterns is the exposure of the data, but none of these options can fully mitigate token exfiltration when the attacker can execute malicious code in the application's execution environment." [3] | 8.5 |
| the browser's files on disk | "there is no guarantee that browser storage is encrypted at rest" [3] | 8.6 |

- **Page: never keep a token, a session id or any other credential in `localStorage` or
  `sessionStorage`.** OWASP's Session Management cheat sheet says the same, and RFC 10017 section
  8.5 gives the reason [55], [3].
  Check: in review, `grep -rnE "(local|session)Storage" src/` shows no token, session id or key.
- **Page: never write a token into a cookie from JavaScript** (RFC 10017 section 8.1) [3].
- **Page: when the page sets a cookie of its own, such as a theme or a locale, name it with the
  `__Host-` prefix, write `Secure`, `Path=/` and a `SameSite` value that fits its purpose, and leave
  out `Domain`,** so the cookie goes over HTTPS only, follows one site rule in every browser, and
  no sibling subdomain can overwrite it (ASVS 5.0 requirements 3.3.1 to 3.3.3; the `__Host-` rules
  of the cookie spec) [64], [65]. A cookie that must be shared with other hosts
  takes the `__Secure-` prefix instead, as requirement 3.3.1 asks [64].
- **Browser-only client: keep the tokens in memory or in a worker, and accept the limit both
  share:** the attacker's script can still ask the provider for new tokens (RFC 10017 sections 8.2
  to 8.4) [3].
- **Browser-only client: where the provider supports DPoP (RFC 9449), bind the tokens to a
  non-exportable key made with the Web Crypto API,** so a token that a script copies out cannot be
  used without the key (RFC 10017 section 9.2) [66], [3]. It does not stop a script that
  runs a new flow (RFC 10017 section 6.3.4.2) [3].
- **Browser-only client: before it takes refresh tokens, confirm that the provider meets RFC 10017
  section 6.3.2.3 [3].** The RFC first says that authorization servers "may choose whether or
  not to issue refresh tokens to browser-based applications" [3]. If they do, they "MUST either
  rotate refresh tokens on each use OR use sender-constrained refresh tokens as described in Section
  4.14.2 of [RFC9700]"; "MUST either set a maximum lifetime on refresh tokens OR expire if the
  refresh token has not been used within some amount of time"; and "MUST NOT, upon issuing a rotated
  refresh token, extend the lifetime of the new refresh token beyond the lifetime of the initial
  refresh token if the refresh token has a preestablished expiration time" [3]. Rotation does
  not make `localStorage` safe: De Ryck (2021) concludes that sensitive single-page applications
  should use a BFF rather than rely on rotation in the browser [67].

The BFF's rules on the session cookie are in
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
section 2, "The session cookie".

The BFF's rules on the login cookie are in
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
section 2, "The login cookie".

### Reading the `Cookie` header

- **Page: on a `400` whose JSON body carries that fixed code of
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  2, such as `cookie_conflict`, tell the user to clear this site's data in the browser,** since a
  cookie that a sibling subdomain planted fails every request until it expires or the user removes
  it; the rule is this practice's choice.

### The session's life, from login to logout

The BFF holds the session, so most of these rules are the server's. Each rule below starts with
whose act it is: the BFF's or the page's.

The flow, in order, with the page's own acts in bold:

0. Session check: **the page asks the BFF, through the API client, whether a session is live**.
1. Login start: **the page opens the BFF's login endpoint by a top-level navigation**.
2. The provider: the BFF sends the user to the identity provider, where the user signs in.
3. The callback: the BFF checks the login cookie, gets the tokens and sets the session cookie.
4. The session: **the page calls the API through the one API client**; the BFF adds the token.
5. Refresh: the BFF refreshes the tokens when the access token expires.
6. Step-up: on `403 reauth_required`, **the page opens the BFF's login endpoint again, with the
   step-up flag**.
7. Logout: **the page calls the logout endpoint and runs the sign-out path**.

- **Page: when the session check answers `401` on a route that needs no session, show the
  signed-out state instead of running the sign-out path, and check for this case before the `401`
  rule below,** since a visitor on a public page has no session to end, and the sign-out path
  would send them to sign in; the rule is this practice's choice.

The BFF's rules on a new session id at login are in
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
section 2, "A new session id at login".

### Timeouts and refresh

- **Page: do not keep an idle session alive with requests sent on a timer.** OWASP measures idle
  time by activity in the session, on the server, so a request the page sends on a timer resets
  the clock as a click does [55]. In TanStack Query that means no `refetchInterval` on data that
  needs the session, unless the BFF leaves those requests out of its idle clock. Polling is off by
  default, and a hidden tab polls only with `refetchIntervalInBackground` set (TanStack Query docs,
  read 2026-10-15) [68], [69]. OWASP states the definition, not this rule; the rule
  is this practice's reading of it.
- **Page: run the sign-out path on the first `401` the API answers:** clear what the session
  loaded and send the user to sign in, so the screen shows no data from a session the server has
  ended. What the sign-out handler does is [architecture.md](../architecture/architecture.md)
  section 10. The rule is this practice's choice.
- **Page: on a `401` that answers a request sent before a sign-in or a step-up renewed the session,
  ask the session check once, and run the sign-out path only when it also answers `401`,** since
  that request carried the session id the renewal destroyed, while the session may be live under
  its new id; this is an exception to the `401` rule above, and the rule is this practice's
  choice.
- **Page: where the query client is made, tell it not to retry a `401`, nor a `403` or a `400`
  whose body carries a fixed code,** since these answers say what the page must do, and a retry
  only sends a guarded request again, while `useQuery` retries a failed query three times by
  default in the browser (TanStack Query docs, read 2026-10-16) [68], [70]. The query client is
  made as [architecture.md](../architecture/architecture.md) section 8 says. The rule is this
  practice's choice.
- **Page: on a `502` or a `503`, the session check's included, and on a `403` whose body carries
  no code, never run the sign-out path, and show the error as for any failed request
  ([architecture.md](../architecture/architecture.md) sections 9 and 12), and for the logout
  endpoint as the rule in "Logout" below on any other failure says,** since these answers say that
  the server or a check failed, not that the session ended; the rule is this practice's choice.

### Logout

- **Page: show a sign-out control on every screen that needs the session** (ASVS 5.0 requirement
  7.4.4; OWASP's Session Management cheat sheet), so a user on a shared device can always end it
  [71], [55].
- **Page: call the BFF's logout endpoint through the API client,** so the call carries the custom
  header (section 7); the rule is this practice's choice.
- **Page: show the user as signed out when the logout endpoint answers with a `2xx`, and also on a
  `401`, which means the session had already ended; then run the sign-out path,** since the
  session no longer exists on the server; the rule is this practice's choice.
- **Page: when the logout endpoint answers with any other failure, say that sign-out failed and
  offer it again,** since the page cannot remove an `HttpOnly` cookie, so the session is still in
  this browser; the rule is this practice's choice.
- **Page: when the logout answer carries the provider's logout URL, check it by section 3's rule
  for a URL that comes from data, and open it by a top-level navigation,** because a `fetch`
  cannot take the user to another site, and the reference policy's `form-action 'self'` (section
  5) blocks a form posted to another origin. RP-Initiated Logout 1.0 section 2 has the client
  redirect the user's browser to the provider's logout endpoint [72]. The URL comes
  from the answer, so it is data. When the check refuses the URL, run the sign-out path without the
  navigation, since the BFF has already ended the local session; the rule is this practice's
  choice.

### Re-authentication

- **Page: on a `403`, check its body for the code `reauth_required` before the `401` rule,** so
  the user re-authenticates, by the path of the login type that the next rules give, instead of
  seeing a plain refusal; the rule is this practice's choice.
- **Page, with an identity provider: before the step-up's navigation, keep in `sessionStorage` the
  screen of the guarded change and what the user typed into it, or start the step-up as the user
  opens that screen, before they type,** since the navigation unloads the page and everything typed
  into it. A screen that takes a password, a one-time code or another credential takes the second
  way, since the storage rule above keeps every credential out of `sessionStorage`. The rule is this
  practice's choice.
- **Page, with an identity provider: on a `403` whose body carries `reauth_required`, or as the user
  opens a guarded change's screen (the rule above), open the BFF's login endpoint by a top-level
  navigation, with the step-up flag and, when the `403` carried `acrValues`, that value as a query
  parameter encoded by `URLSearchParams`,** since the browser reaches the login endpoint by a
  navigation, so the BFF can answer with the redirect that takes the browser to the authorization
  server (RFC 10017 section 6.1.2.1) [3]. `URLSearchParams` encodes every character of a value
  except the ASCII letters and digits, `*`, `-`, `.` and `_`, so an `&`, a `=` or a `#` in
  `acrValues` cannot add a parameter or end the query (URL Standard sections 5.2 and 6.2) [75]. The
  BFF accepts only the values on the list the team wrote down
  ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
  section 2, "Re-authentication"). The step-up flag and the encoding are this practice's choice.
- **Page: with a first-party login, on a `403` whose body carries `reauth_required`, show the
  re-authentication prompt and send the guarded request again with the answer, and on a `403`
  whose body carries `reauth_failed`, show the prompt again,** so the change the BFF guards can go
  through; leave a `401` to the sign-out path. The rule is this practice's choice.
- **Page, with an identity provider: on the step-up's outcome route, read what was kept in
  `sessionStorage` and delete it, show the outcome its code names (`reauthenticated`, `refused` or
  `failed`), and after `reauthenticated` put the user back on the kept screen with what they typed,
  its data read again from the BFF, so they can send the change again,** since the BFF applied
  nothing of the change and kept nothing of the request
  ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
  section 2, "Re-authentication"); the rule is this practice's choice.

The BFF's rules on forwarding requests to resource servers are in
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
section 2, "Forwarding to resource servers".

The BFF's login and logout responses are in
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
section 2, "The login and logout responses".

## 7. CSRF and CORS

As in section 6, "the server" means the component that receives the browser's session cookie: the
BFF, which in the example is also the API, so the `API:` and `BFF:` rules of
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 3
name the same server. An API route is any route of that server other than a `GET` that serves the
page's own files (the HTML and its scripts) or, with a framework that renders on the server, a `GET`
that renders one of its pages.

The page's rules in this section are under "What the React code does", and in "Fixing a CORS
error" they are the bullets that start with "The page" or `Page:`.

What CSRF is, and the server's defence against it, are in
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
section 3, "CSRF".

What the server does is in
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
section 3, "What the server does".

### What the React code does

- **Send the custom header on every request to an API route, from the one API client,** except
  the requests the exemption table of
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  3 names that the page sends: the login start, which the page opens by a top-level navigation, the
  `report` method's calls, the WebSocket handshake and a download link. A header such as
  `X-Requested-With` makes the browser send a CORS preflight first, and the server allows it only
  for the application's origin (`https://app.example.com`), so another site cannot send the request
  from a form (OWASP, item 4 in
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  3; RFC 10017 section 6.1.3.3.2, which recommends the header and, once it is used, asks for it on
  every request; MDN on which headers start a preflight) [73], [3], [1]. The reference
  API client is in section 15 and in [security-example.md](security-example.md).
- **When the API is on another origin of the site, send every request that needs the session with
  `credentials: "include"`, from the one API client,** so the browser adds the session cookie: the
  default, `same-origin`, sends no cookie to another origin (MDN) [74]. On the page's own origin
  the default already sends it.
- **Page: when the API answers with a status that is not `2xx`, have the API client throw an error
  that carries the response's status and, when the body parses as JSON, its fixed code and the
  body's `acrValues` when it has them; a body that does not parse, such as a gateway's HTML page,
  gives no code and no `acrValues`,** so the `Page:` rules that read a status and a code, such as
  `cookie_conflict` and `reauth_required` (section 6), can read both, and the step-up with an
  identity provider can pass the `acrValues` on to the BFF's login endpoint (section 6,
  "Re-authentication"); the rule is this practice's choice.
- **Load an API resource that the page shows without `fetch`, such as an image or a PDF preview,
  through the API client, and show it from a `URL.createObjectURL` URL,** because an `<img>` and a
  frame cannot send the custom header; the reason is this practice's reading.
- **Build that blob with a type the code sets, never with the response's own type:
  `application/pdf` for a frame, and `image/png`, `image/jpeg`, `image/webp` or `image/gif` for an
  `<img>`, never `image/svg+xml`,** so a file from outside never becomes an HTML or SVG document in
  the page's origin. For a PDF that is
  `new Blob([await response.arrayBuffer()], { type: "application/pdf" })`. The guard is this
  practice's choice, after the URL Standard, which gives a blob URL the origin of the page that
  created it [75], [76].
- **Add `blob:` to `img-src` in the page's policy for these images, and to `frame-src` only for
  the PDF preview,** since a blob URL has the page's origin (URL Standard section 4.7), so a
  document loaded from it in a frame runs in that origin; the rule is this practice's choice
  [75].
- **Never loosen `object-src` for the PDF preview; where the frame shows nothing, offer the file
  through the download link instead, whose answer carries `Content-Disposition: attachment`,** since
  `object-src 'none'` belongs to the strict policy of section 5, and a blank preview is no reason
  to give it up; the rule is this practice's choice [77].
- **Read an event stream with `fetch` through the API client, not with `EventSource`,** because
  `EventSource` cannot send the custom header and takes `withCredentials` as its only option (MDN,
  read 2026-10-16) [78].
- **Send the CSRF token the server issues, where it uses one, in a header of each state-changing
  request,** since the server checks it on each of them, the login included, which needs a token
  of its own, issued before the session exists (OWASP) [73].
- **When the API is on another origin of the site, read the CSRF token from a JSON response
  through the API client, never from a cookie with a `Domain` attribute,** since the page cannot
  read the API's own cookie, and a cookie with `Domain` goes to every subdomain, any of which can
  overwrite it with a token of its own (OWASP's CSRF cheat sheet) [73].
- **Encode every value you put into an API path with `encodeURIComponent`.** A value such as
  `../../account/delete` turns the application's own request into a request to another endpoint,
  with the cookie, the custom header and any CSRF token attached: client-side path traversal gets
  past every defence in OWASP's list in
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  3 (Doyensec, 2024; CVE-2023-45316 in Mattermost) [79], [80],
  [81]. The query and mutation options in
  [layout-example.md](../architecture/layout-example.md) encode the route's `invoiceId` this way.

Encoding stops the slash, but it leaves `.` and `..` as they are, and the URL parser then resolves
them: `` `/invoices/${encodeURIComponent("..")}/payments` `` requests `/payments` (checked with
Node 20's URL parser, 2026-10-15).

- **Check the format of any value that does not come from the route's own path, against its
  schema, before you build the path,** such as the format of an invoice id (OWASP's CSRF cheat
  sheet, client-side CSRF) [73]. A path parameter the router reads from the page's own URL has
  lost its literal `.` and `..` segments, but not a `%2F` inside one, which the server's path rule
  in [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
  section 3 rejects; a value from a search parameter, a message, storage or a response has not lost
  them.
- **Put no token in the WebSocket URL's query string,** where logs keep it (OWASP's WebSocket
  Security cheat sheet; section 13) [82].
- **When the page opens a WebSocket, add the socket's `wss://` origin, such as
  `wss://api.example.com`, to `connect-src` in the page's policy (section 5),** since a source
  written with `https://` does not match a `wss://` URL, so the reference policy would block the
  socket (CSP Level 3, "scheme-part matching", read 2026-10-16) [83].
- **Page: when the server closes a WebSocket with its session-ended code, run the sign-out path,**
  since that code is the server's word that the session ended (the WebSocket rules in
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  3, "What the server does"); the rule is this practice's choice.
- **Page: when a WebSocket closes with any other code, reconnect with a bounded backoff, and before
  each reconnect ask the API through the API client whether the session is still live,** since a
  handshake the server refuses reaches the page only as a close with code 1006, the code for a
  connection closed with no close frame, so the `401` rule of section 6 cannot fire for a socket
  (MDN's `CloseEvent.code` page; the WHATWG WebSockets Standard) [84],
  [85]. The rule is this practice's choice.

The API's CORS rules are in
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
section 3, "CORS".

### Fixing a CORS error

- **The page never sets `mode: "no-cors"`:** the answer comes back opaque, with status 0 and a
  body no script can read (MDN; the Fetch standard) [86], [2].
- **The page never sends an `Access-Control-Allow-*` header:** it is a response header, and on a
  request it is one more header outside the safelist, which starts a preflight (the Fetch
  standard) [2].
- **The page never sends requests through a public CORS proxy:** the proxy reads every request and
  answer, tokens and keys included. No leak through such a proxy is documented; the risk is the
  design, so the rule is this practice's choice.
- **Page: when development calls a real API on another origin instead of MSW handlers
  ([libraries.md](../architecture/libraries.md) section 6), send the API calls through Vite's
  `server.proxy`, under a path prefix that no page route uses,** so the page's calls reach the API
  as `same-origin` (the browser sends them to the page's own origin, and Vite's proxy forwards them;
  Vite's docs), and the proxy never catches a navigation to one of the page's own routes [87].
  What the development instance accepts is the rule on the one setting of allowed origins, in
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  3, "What the server does". The dev server's own rules are section 11.
## 8. Server-side React

This section holds when a framework renders React on the server or runs Server Functions:
Next.js, React Router in framework mode, and others. A client-only application has none of these
endpoints; React's December 2025 advisory lists client-only React as not affected [88]. An
application that uses Server Components can be exposed even when it defines no Server Function of
its own (the same advisory) [88].

- **Treat every Server Function as a public HTTP endpoint.** Anyone can send it a POST directly,
  not only through your UI, and a check on the page that shows the form does not cover it (Next.js
  data security guide) [89]. Inside each one: parse the arguments with a schema; check who
  the user is and that they may touch this record; return only the fields the client needs
  [89], [90]. Why a schema is this practice's reasoning: TypeScript types do not
  exist at run time.
- **Read data through a data access layer that runs only on the server.** Next.js's guide
  describes it: it runs only on the server, checks authorisation, and returns small objects with
  only the fields the caller needs; `import "server-only"` at its top makes a client import fail
  at build time [89]. The layer lives on the server, in the framework's server-only code.
- **Never authorise in middleware or a proxy alone; check again in the data access layer and in
  each Server Function.** CVE-2025-29927 (CVSS 9.1) let one spoofed header skip Next.js middleware,
  and Vercel's post-mortem advises against middleware as the only protection of a route; the May
  2026 Next.js release fixed four more middleware and proxy bypasses [91], [92],
  [93].
- **Do not treat closure encryption or taint as a boundary.** Next.js encrypts the values a Server
  Action closes over and advises against relying on that alone; arguments passed with `.bind()`
  are not encrypted [89], [90]. React's taint APIs are experimental, and a clone
  or a spread copy of a tainted object is not tainted [94].
- **Write no secret into server code; read it from the server's environment at run time.**
  CVE-2025-55183 exposed Server Function source: any secret written in a Server Function's source
  could be exposed; values read from the environment at run time were not affected (Next.js and
  React, December 2025) [95], [96].
- **Patch a critical advisory for React's server packages, your framework or your router within
  the day, through the cooldown's emergency path (section 10).** React2Shell (CVE-2025-55182,
  CVSS 10.0) let anyone run code on the server without logging in [88]. Groups tried to
  exploit it within hours of disclosure (AWS) and went after cloud and API credentials (Microsoft)
  [97], [98]. Nothing in application code stopped it: Next.js wrote that there
  was no workaround, only the upgrade [99]. Google called its WAF rule a temporary
  measure until the patch lands, and React told users not to depend on their host's mitigations
  [100], [88]. Turn on Dependabot or Renovate security updates, which skip their
  cooldowns (section 10) [101], [102], [103].
  Check: when you set up the repository, see that the person or channel that receives security
  advisories and alerts is in the decision log
  ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
  section 3, the first rule under "Logging"), so the advisories of React, the framework and the
  router reach them on the day they are published.
- **Read the advisory again in the days after you patch.** After React2Shell, follow-up
  advisories for denial of service and source exposure moved the patched version more than once,
  so the first fix was not the last [96]. Write the advisory id in your notes,
  never a version number as "the safe version".
- **After a flaw that ran code on the server, treat the server's credentials as stolen.** Rotate
  every cloud, database and API key the server could reach; Next.js's React2Shell advisory asks
  you to "rotate any secrets it uses, starting with your most critical ones" [99].
  Keeping that set small is this practice's choice.
- **Patch the framework's XSS advisories as fast as any other critical one.** React Router had
  three XSS advisories in January 2026: `ld+json` in `meta()` and `ScrollRestoration` keys, both
  in server rendering in framework mode, and redirects from loaders and actions, which run script
  in the browser in framework and data modes [104], [105],
  [106].

## 9. Secrets and public settings

- **Treat every `VITE_` value and every `NEXT_PUBLIC_` value as public.** Vite writes them into
  the bundle at build time, and its docs say they must not hold sensitive data such as API keys;
  Next.js inlines `NEXT_PUBLIC_` values at build time the same way [107], [108]. A secret
  lives on the server, and the server makes the call that needs it. Section 15 shows the BAD and
  the GOOD.
  Check: before you add a `VITE_` or `NEXT_PUBLIC_` variable, ask whether you would print its value
  on the login page. If not, it is a secret.
- **List the public settings in one schema, so a secret has no place to land.** Where the
  settings file sits and how the application reads it is
  [architecture.md](../architecture/architecture.md) section 3.
- **Keep files with real values out of git.** Vite's docs say `*.local` env files stay out of
  git, and the Next.js template ignores `.env*`; commit an example file with every name and no
  real value ([file-structure.md](../../any-language/file-structure/file-structure.md) section 9)
  [107], [108].
- **Publish no source maps from a production build.** Vite's `build.sourcemap` is off by default,
  and `'hidden'` writes maps without the comment that points to them, which this practice keeps
  for upload to an error tracker; Next.js keeps browser source maps off by default (read
  2026-10-01) [109], [110]. A published map hands out the original
  source with its comments. Demir et al. (2026 preprint) studied 10 million rendered sites and
  found 1,748 live credentials in front ends; 62% of the exposures in JavaScript appeared only in
  compiled bundles [111].
- **Restrict at the provider any key that must ship to the browser.** A maps key gets a website
  restriction and an API restriction (Google Maps Platform) [112]. A "public" database key,
  such as a Supabase anon key, is safe only behind server-side rules such as row-level security: a
  scan by two researchers found 170 of 1,645 Lovable-built apps exposing tables to anyone holding
  that key, because their row-level security policies were missing or insufficient
  (CVE-2025-48757, which Lovable disputes) [113], [114].
- **Scan for secrets before they leave the machine and after the build.** Turn on GitHub secret
  scanning and repository-level push protection, which is off by default (GitHub's docs, read
  2026-10-01), and run a scanner such as gitleaks as a pre-commit hook [115], [116]. Run it
  over the build output too: the study above found most JavaScript exposures only in the compiled
  bundle [111]. Gitleaks takes security fixes only, and its maintainer is moving to Betterleaks
  (read 2026-10-01); re-check before you adopt it [116].
- **When a secret leaks, revoke it at the provider first.** GitHub's guide calls revocation the
  most important step: deleting the secret from the code, pushing a new commit or recreating the
  repository does not stop its use [117].

## 10. Supply chain: packages, lockfile, CI

A package you install runs with your rights in two places: on the developer's machine and in CI,
when it is installed or built; and in your users' browsers, once it is bundled. The incidents of
2025 and 2026 each found a different gap:

| Incident | How it got in | What it teaches |
|---|---|---|
| Shai-Hulud, September 2025 | compromised maintainer accounts (Unit 42 suspects phishing); an install script stole npm and GitHub tokens and published infected versions of the victims' other packages; GitHub removed more than 500 packages [118], [119] | block dependency install scripts |
| chalk and debug, September 2025 | a phished maintainer; the payload ran in end users' browsers once bundled; Vercel found 76 projects built with it [120] | blocking install scripts does not stop a payload that runs in the bundle |
| Nx, August 2025 | a `pull_request_target` workflow with write rights, and a pull request title run as part of a script [121] | CI is an entry point |
| axios, March 2026 | the maintainer's npm credentials; a malicious dependency that dropped remote-access malware; the versions were pulled after about 3 hours; CISA advised `ignore-scripts=true` and `min-release-age=7` [122], [123], [124] | a cooldown would have skipped it |
| TanStack, May 2026 | a `pull_request_target` workflow that ran fork code, a poisoned Actions cache, and an OIDC token read from runner memory; the versions carried valid provenance; Snyk wrote that a seven-day cooldown would have fully protected against it [125], [126] | provenance says where a package was built, not that its code is safe |
| AsyncAPI, July 2026 | the payload ran when the package was imported, so `--ignore-scripts` did not stop it; the versions carried valid provenance (Microsoft) [127] | no single control is enough |

A cooldown also misses what it cannot see: a git dependency names a commit, not a registry
version, and an account taken over for weeks outlasts any wait (a 2026 practitioner analysis)
[128]. Socket found destructive packages aimed at React, Vue and Vite projects
[129].

The controls, per package manager (owners' docs, read 2026-10-01; "not read" means the page read
for this table did not cover it):

| Control | npm 12 | pnpm 11 and later |
|---|---|---|
| dependency install scripts | blocked unless `allowScripts` in the root `package.json` approves them; `strict-allow-scripts=true` turns the warning into a failed install. npm 11 still runs them: set `ignore-scripts=true` there [130], [131], [132] | blocked; `strictDepBuilds` (default `true`) fails the install on an unreviewed build script; reviewed packages go in `allowBuilds`, which replaced `onlyBuiltDependencies` in pnpm 11; never `dangerouslyAllowAllBuilds` [133], [134] |
| release cooldown | `min-release-age` in days, off by default in npm 12 as well (the setting exists since npm 11.10.0, 2026-02-11; npm 10 has none); `min-release-age-exclude` (since 11.17.0) exempts packages [130], [135], [136] | `minimumReleaseAge` in minutes, default 1440 (one day) since pnpm 11; `minimumReleaseAgeExclude` exempts packages [137] |
| git and tarball sources | `allow-git` and `allow-remote` default to `none` [131] | `blockExoticSubdeps` (default `true`): only direct dependencies may come from git or a tarball URL [137] |
| provenance | `npm audit signatures` checks registry signatures and provenance attestations [138] | `trustPolicy: no-downgrade` fails when a version's trust level is lower than that of earlier versions [137] |
| install exactly the lockfile | `npm ci` fails when the lockfile and `package.json` disagree, and writes neither [139] | commit `pnpm-lock.yaml` (pnpm's supply-chain page) [134] |
| fix a transitive dependency | `overrides` in the root `package.json` [140] | `overrides` in `pnpm-workspace.yaml` [137] |

Yarn and Bun have controls of the same kind under other names; they were not compared here
[141], [142].

Update bots: Renovate's `minimumReleaseAge` does not apply to vulnerability fixes, and its
`security:minimumReleaseAgeNpm` preset waits 3 days; Dependabot's `cooldown` applies to version
updates only, never to security updates (read 2026-10-01) [101], [102],
[103].

- **Turn on the install-script block and a release cooldown in the repository's own config file,
  so every install obeys them:** a person's, CI's and an agent's. A setting on one laptop protects
  one laptop. The settings for npm 12, npm 11.10 or later, and pnpm are in
  [security-example.md](security-example.md).
- **Set the cooldown to at least one day.** One day covered axios, Nx and TanStack, whose versions
  were live for hours; CISA advised seven after the axios compromise [121], [122],
  [124], [125]. A longer wait delays every normal update by as much; that
  is the trade.
  `min-release-age` exists since npm 11.10.0 (2026-02-11); npm 10 has neither it nor
  `min-release-age-exclude` [135], [136]. On npm before 11.10.0,
  `--before=<date>` on the install command installs only versions that were available on or
  before that date (npm's config page, read 2026-10-02) [136]. It takes a fixed date
  that the person running the install has to choose each time, where `min-release-age` is a
  rolling window set once in the repository. The reference application was installed this way
  (npm 10.8, `--before=2026-09-24`); it is a command flag, not repository config.
- **Write the emergency path next to the cooldown.** A one-day pnpm cooldown blocked the
  React2Shell patch while it was under a day old, and the developer got it through with
  `minimumReleaseAgeExclude` (a practitioner's account, 2025) [143]. The path names the setting
  that exempts one package, who may add an entry, and that the entry comes out once the version is
  older than the cooldown [143]. Who may add an entry, and that it comes out once the version
  is older than the cooldown, are this practice's choice. npm has `min-release-age-exclude` since
  11.17.0; an older npm has no per-package exemption [135].
  Check: when you set a cooldown, ask: if a critical fix ships today, which line do we change? If
  no line next to the setting answers, the path is missing.
- **Allow a dependency's build script only after someone has read it,** by adding that package to
  `allowBuilds` or `allowScripts`. The script runs with your rights when the package is installed,
  which is how Shai-Hulud stole npm and GitHub tokens [119].
- **Treat provenance as one layer, never as proof.** pnpm recommends `trustPolicy: no-downgrade`
  and npm checks attestations with `npm audit signatures`, yet the TanStack and AsyncAPI versions
  carried valid ones [134], [126], [127].
- **Have every security advisory of your dependencies reach you on the day it is published:**
  turn on the host's dependency alerts for the repository, such as Dependabot alerts on GitHub,
  and watch the advisory sources section 18 lists for React's server packages, the framework, the
  router, Vite and DOMPurify [144]. Where a BFF holds the session, turn on dependency alerts in
  the BFF's own repository too, for its server framework, its session and cookie library and its
  OAuth or OpenID Connect client library. A critical fix can then go in through the emergency path
  on the day it ships, not at the next dated re-check or CI run.

Before an AI coding agent installs a package:

- **It checks on the registry that the package exists, that the name is the one the library's own
  docs give, and how old the version is; a name it cannot find in those docs is not installed.**
  Models invent package names. A 2025 USENIX study of 16 models found that on average at least
  5.2% of the packages commercial models suggested, and 21.7% of those open-source models
  suggested, did not exist; a 2026 preprint found 4.6% to 6.1% on five frontier models, which all
  invented the same 127 names, 53 of them still free to register [145], [146]. An
  attacker who registers such a name gets installed by the next agent that invents it.
- **It installs through the repository's config, and never passes a flag that turns off the
  cooldown or the script block.** The rules above hold only if every install goes through them.
  No owner states this for agents; it is the practice's choice.
- How far to trust a Claude Code plugin or skill is
  [designing-with-claude-code.md](../design/designing-with-claude-code.md) section 7. The
  packages a plugin or a registry brings are dependencies, and this section's rules apply to
  them.

The lockfile:

- **Commit the lockfile,** so every install takes the same versions and a change to them shows in
  a pull request.
- **Install in CI with the command that refuses to change the lockfile:** `npm ci`, or Yarn's
  immutable install (npm's and Yarn's docs), so CI builds exactly what the lockfile says and an
  install that would change it fails [139], [141].
- **Review a lockfile change in a pull request like code.** A pull request can point a `resolved`
  URL at another tarball; `lockfile-lint` checks that every package comes from the hosts you
  allow [147].
- **Judge an audit by what the application reaches.** `npm audit` reports issues in code an
  application never runs; Dan Abramov called it broken by design (2021), and alerts nobody reads
  train people to skip the real one [148]. Fix what is reachable. When the fix exists
  only in a transitive dependency, pin it with `overrides` [140]. OSV-Scanner
  reads npm, pnpm and Yarn lockfiles against the OSV database, as a second opinion
  [149].

CI (GitHub Actions; the rules are GitHub's own, from its secure-use reference) [150]:

- **Pin every third-party action to its full commit SHA, unless the repository uses GitHub's
  workflow dependency lockfile.** GitHub's docs call the lockfile "the strongest protection
  available" and say it "supersedes SHA pinning for repositories that adopt it"; for a repository
  without one, they list pinning actions to a full-length commit SHA [150]. Dependabot keeps the
  pinned versions current [150].
  Check: the repository uses GitHub's workflow dependency lockfile, or
  `grep -rhn "uses:" .github/workflows/ | grep -vE "@[0-9a-f]{40}|uses: \./"` prints nothing.
- **Set the default `GITHUB_TOKEN` permission to read the repository contents, and raise it per
  job only where a job needs more.** A workflow that runs an attacker's input, as the Nx one did,
  then holds a token that cannot write [121], [150].
- **Never check out pull request code from a fork in a `pull_request_target` workflow.** The
  TanStack attack used such a workflow to run fork code [125], [150].
- **Pass pull request fields to a script through an environment variable, never through `${{ }}`
  inside the script.** The Nx attack ran a pull request title as part of a script [121],
  [150].
- **Share no cache between workflows that run fork code and workflows that publish.** This rule is
  this practice's choice. TanStack's post-mortem says a pull request running in the base
  repository's cache scope "can poison entries that production workflows on main will later
  restore" [125]. GitHub says privileged workflows "share the same cache of the main branch with
  other privileged workflow triggers" [150].

## 11. The dev server

The Vite dev server serves your source tree. Between January 2025 and June 2026 Vite published
thirteen advisories against it: twelve let a request read files outside the `server.fs` limits, and
one let any website the developer visited send requests to the dev server and read the source,
through CORS and the WebSocket (Vite's advisories, read 2026-10-01) [144]. Each was closed only
by an upgrade [144].

- **Keep Vite current on every machine that runs the dev server.** The rules below shrink who can
  reach it; only the patch closes a bug.
- **Keep `server.host` at its default, `localhost`.** `--host` or `host: true` listens on every
  address, the local network and public ones included [87]. Use it only on a network you
  trust, and only while you need it.
- **Never set `server.allowedHosts: true`; list only domains you control.** Vite's docs warn that
  `true` opens the dev server to DNS rebinding, which lets any site download your source [87].
  The BAD and the GOOD follow this list.
- **Never set `server.cors: true`; list the origins you need.** The default allows only
  localhost; `true` lets any website send requests and read the answers (Vite's docs) [87].
- **Keep `server.fs.strict` on (the default), and widen `server.fs.allow` only to folders you mean
  to serve.** `server.fs.deny` blocks `.env` files and key files by default, but it does not cover
  the `public/` folder, so nothing secret goes there; the build also copies `public/` as it is
  [87].
- **Do not set `rewriteWsOrigin` in `server.proxy`.** Vite does not check the origin of a
  WebSocket request before it proxies it, so the target must, and this option removes that check
  (Vite's docs) [87].
- **Apply the same rules to `vite preview`.** The preview server takes `host`, `allowedHosts`,
  `cors` and `proxy` from `server` unless `preview` sets its own [151].

Bad: the host check turned off, to reach the dev server through a tunnel for a test on a phone.

```ts
server: {
  allowedHosts: true,
},
```

Any site can now reach the dev server through DNS rebinding and download the source [87].

Good: the same tunnel, with only its own domain allowed. This line is written from Vite's docs;
the reference application sets no `server` block, so the defaults hold there [87].

```ts
server: {
  // Only the tunnel's domain: `true` would let any site reach this server through DNS rebinding
  // (security.md section 11).
  allowedHosts: ["billing-dev.tunnel.example.com"],
},
```

It fixes the one problem: the tunnel works, and the server answers no other host name. A leading
`.` would allow every subdomain too; list the one name you need [87].

## 12. Third-party scripts, postMessage, iframes, redirects

Third-party scripts:

- **Prefer a data layer to a vendor's script on the page:** your own code collects the events and
  sends the vendor only the fields you chose, so the vendor gets nothing else [152]. A data
  layer limits what is collected; it is not a sandbox, since a tag manager's tags still run as
  code in the page (OWASP's Third Party JavaScript Management cheat sheet, read 2026-10-16)
  [152].
- **Load a fixed version of a script from another origin with Subresource Integrity:** the
  `integrity` attribute and `crossorigin="anonymous"` [153]. SRI refuses any file whose hash
  does not match, a vendor's own update included, and it covers scripts and stylesheet and preload
  links only (MDN) [153]. So it fits only a file that never changes at its URL; that reading is
  the practice's.
- **Keep analytics, session replay and any other script that listens to keystrokes off the login
  and payment screens.** Munir et al. (2025) crawled a random sample of 15,000 of the top million
  sites and found third-party keystroke listeners on 38.52% of them; at least 3.18% of the sites
  sent what users typed to a third-party server [154].
- **Give a tag manager's console the access rules of a deploy.** Under `'strict-dynamic'`, a
  nonced tag manager runs every Custom HTML tag added in its own console (section 5; Raxis, 2026)
  [40]. OWASP's Third Party JavaScript Management cheat sheet sets the access rule:
  "Restrict tag-manager publishing access and review changes as application code" [152].

postMessage:

- **Add a `message` listener only when the page expects messages from another window** (MDN),
  since any window can send the page a message and the listener is where it gets in [155].
- **In the listener, compare `event.origin` with the one exact origin you expect, then check the
  message's shape before you use it** [155]. Never check `event.source` instead, and never
  accept a whole domain with a wildcard. Microsoft's security team calls a check of
  `event.source` instead of `event.origin` a dangerous anti-pattern, and in 2025 found wildcard
  domains and messages sent to `"*"` across its own products [156].
- **Send with the exact target origin, never `"*"`.** With `"*"`, the message goes to whatever page
  is in the target window at that moment (OWASP's HTML5 Security cheat sheet; MDN)
  [157], [155].

iframes, redirects and service workers:

- **Load content you do not control in an `<iframe>` with `sandbox`, and never give it
  `allow-scripts` together with `allow-same-origin`.** With both, a same-origin document can remove
  its own sandbox (MDN) [158].
- **Redirect after login only to a target from an allowlist, or to one the server maps from a
  short id.** A `?next=` value used as it is sends the user to any site from a link that shows your
  domain (OWASP's Unvalidated Redirects cheat sheet) [159].
- **Register a service worker only from your own origin and over HTTPS** (OWASP's HTML5 Security
  cheat sheet), since the worker sits between the page and the network for every request in its
  scope [157].
- **Cache no response that carries personal data in a service worker,** since the Cache API
  ignores HTTP caching headers and its entries do not expire, so they stay until code deletes them
  (the same cheat sheet) [157]. That any script on the origin can read them is this
  practice's reasoning.
- No rule is spent on `rel="noopener"`: browsers already treat `target="_blank"` as `noopener`
  (MDN, read 2026-10-01) [160].

## 13. Data the browser exposes

- **Put no token, password or API key in a URL; send it in a header or a request body.** A URL
  lands in server logs and browser history, and goes to other sites in the `Referer` header
  (OWASP's REST Security cheat sheet for server logs; MDN for history and the `Referer` header)
  [161].
- **Send no credential, session id, token or payment data to a client log, the console or an
  error report.** OWASP's Logging cheat sheet lists what logs should not record, and an error
  report is a log that leaves the user's machine [162]. The same list for server logs is
  [logging.md](../../python/logging/logging.md) section 10.
- **On a screen that failed, show a message of your own, never the error's own message or its
  stack.** A message or a stack can carry what the server answered or how it is built. OWASP's
  Error Handling cheat sheet asks that "a generic response is returned by the application but the
  error details are logged server side for investigation, and not returned to the user" [163].
- **Send the path, not the full URL, to analytics and metrics.** The query string can hold what the
  user typed, and MDN's referrer guide names URL parameters among the sensitive data a referrer can
  leak [52].
  The reference application's web-vitals report sends the path of the URL the metric belongs to,
  `metric.navigationURL`, and never the query string ([security-example.md](security-example.md));
  what to measure is [performance.md](../performance/performance.md) section 3.
- **Keep session replay masking on.** Sentry's replay masks all text and all input values by
  default, and its docs say to turn that off only on a site with no sensitive data; PostHog masks
  inputs but not page text by default, so turn on text masking there (vendors' docs, read
  2026-10-01) [164], [165].
- **Give credential fields their `autocomplete` token: `username`, `current-password`,
  `new-password`, `one-time-code`.** `autocomplete="off"` is no control: password managers may fill
  the field anyway, and browsers may ignore it on login fields (MDN) [166]. How a form behaves in
  general is [ux.md](../design/ux.md) section 4.
- **Never block paste in the username, password or one-time-code fields.** OWASP's
  Authentication cheat sheet asks to allow paste in the username, password and MFA fields
  [60]. The UK's NCSC asks services to let users paste passwords, so people can use password
  managers [167].
- **Send `Cache-Control: no-store` on any response that carries personal data or a session id,
  HTML included,** so no shared cache keeps one user's data for the next one. OWASP's Session
  Management cheat sheet asks for it on responses that carry a session id [55]. OWASP's REST
  Security cheat sheet asks for it on API responses a browser may read [161]. Personal
  data and HTML pages are this practice's choice.

## 14. Automation: lint rules and header scanners

The lint rules that catch the sinks of section 3 are mostly off in the default presets (read
2026-10-01):

| Sink | ESLint | Oxlint |
|---|---|---|
| `eval`, `new Function`, timers given a string | core `no-eval`, `no-implied-eval`, `no-new-func`, none of them in `eslint:recommended`; typescript-eslint's `no-implied-eval` uses types and is in `recommended-type-checked` [168], [169] | `no-eval`, `no-implied-eval`, `no-new-func` |
| a `javascript:` URL written in the code | core `no-script-url`, not in `eslint:recommended`; eslint-plugin-react's `jsx-no-script-url`, not in its recommended set; @eslint-react's `dom-no-script-url` [168], [170], [171] | `no-script-url` |
| `dangerouslySetInnerHTML` | eslint-plugin-react's `no-danger`, not in its recommended set; @eslint-react's `dom-no-dangerously-set-innerhtml` [170], [171] | `react/no-danger` |
| `innerHTML`, `insertAdjacentHTML`, `document.write` | `eslint-plugin-no-unsanitized`, its `property` and `method` rules [172] | not read |
| an unsafe `iframe` sandbox | @eslint-react's `dom-no-unsafe-iframe-sandbox` [171] | not read |

Biome has rules of the same kind, and its docs mark both as recommended, which turns them on by
default [173], [174]. They were not compared here.

- **Turn these rules on by name, as errors.** The reference application's `.oxlintrc.json` names
  them, and its negative controls show `react/no-danger`, `no-script-url` and `no-eval` reporting
  a file that broke each ([security-example.md](security-example.md)). Which linter, and which
  version, is [libraries.md](../architecture/libraries.md) section 4.
- **Know what the rules miss.** `no-script-url` reports a `javascript:` string written in the
  code, not a URL that arrives as data, so the scheme allowlist of section 3 stays. `no-danger`
  reports every sink, sanitised or not, so the one allowed sink carries a suppression that names
  the rule and the reason, in the form
  [static-checks.md](../../python/static-checks/static-checks.md) section 6 gives.
- **After every deploy that changes a header, run the policy through CSP Evaluator and the site
  through MDN's HTTP Observatory.** CSP Evaluator looks for ways around a policy, and Google offers
  it for convenience, with no promise that a clean result means a safe policy; the Observatory
  checks the headers and settings the deployed site actually sends [175], [176].
- **Run the supply-chain and secret checks in CI:** `npm audit signatures`, OSV-Scanner and the
  secret scanner (sections 9 and 10) [138].
## 15. Common mistakes

Each pair shows one problem and its fix. The BAD is written by hand: the same file or lines as
its GOOD, with the one problem in place. The GOOD is quoted from the reference application as it
is, with the cut parts named before the block.

### A token in localStorage

Bad: the `request` method of `ApiClient` reads an access token from `localStorage` and sends it as
a bearer header.

```ts
async request<TSchema extends z.ZodType>(path: string, request: ApiRequest<TSchema>): Promise<z.infer<TSchema>> {
  const accessToken = localStorage.getItem("accessToken");

  const response = await fetch(new URL(path, this.#baseUrl), {
    method: request.method ?? "GET",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken ?? ""}`,
    },
    body: request.body === undefined ? undefined : JSON.stringify(request.body),
    signal: request.signal,
  });
  ...
```

Any script that runs on the page can read `localStorage` (RFC 10017 section 8.5), send the token
to its own server, and use it from there until it expires [3].

Good: `src/core/api-client.ts`, the `request` method of `ApiClient`. The imports, the error class,
the schema of its body and its type, `readErrorBody`, the request type, the constructor, the
error check and the parsing of the response are cut; the whole file is in
[security-example.md](security-example.md) section 1.

```ts
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
  ...
```

It fixes the token problem: the BFF sets an `HttpOnly` cookie and `credentials: "include"` lets
the browser send it, so no token exists in JavaScript to steal (section 6). A script on the page
can still send requests through the session and read the answers; what it cannot do is carry a
token away to use from its own machine. The custom header follows
from the fix: a cookie session brings CSRF back, and the header is the browser's half of the
defence (section 7) [57].

### A secret in a VITE_ variable

Bad: the payment provider's secret key added to the public settings.

```ts
import { z } from "zod";

const publicEnvSchema = z.object({
  // An origin with no path: request paths start at the root, and `new URL("/invoices", base)`
  // would silently drop a path such as `/v1` from the base.
  VITE_API_BASE_URL: z.url().refine((value) => new URL(value).pathname === "/", {
    error: "VITE_API_BASE_URL is an origin, such as https://api.example.com, with no path",
  }),
  VITE_PAYMENT_PROVIDER_SECRET_KEY: z.string(),
});

const publicEnv = publicEnvSchema.parse(import.meta.env);

export const config = {
  apiBaseUrl: publicEnv.VITE_API_BASE_URL,
  paymentProviderSecretKey: publicEnv.VITE_PAYMENT_PROVIDER_SECRET_KEY,
} as const;
```

Vite writes the value into the bundle, so anyone who opens the application can read the key in
the browser's developer tools and use it with the provider [107]. No type check and no lint
rule reports it.

Good: `src/core/config.ts`. The import, the origin check inside the schema and the parse line are
cut; the whole file is in [security-example.md](security-example.md)
section 2.

```ts
// Vite inlines every VITE_ value into the bundle, so this schema holds public settings only.
// A secret never goes here: anyone can read it in the browser (security.md section 9).
const publicEnvSchema = z.object({
  ...
});

...

export const config = {
  apiBaseUrl: publicEnv.VITE_API_BASE_URL,
} as const;
```

It fixes the one problem: the secret's two lines are gone, and the schema lists public names
only. The comment that says why sits where a reader would add a key, so the next one does not.
The provider's key stays on the server; the screen posts the payment to the application's own
API, which holds the key and calls the provider (section 9).

### Outside HTML put on the page unsanitised

Bad: the invoice note goes on the page as it arrived, in `pay-invoice-form.tsx`.

```tsx
      {invoice.noteHtml === null ? null : <div dangerouslySetInnerHTML={{ __html: invoice.noteHtml }} />}
```

The note is HTML typed by whoever issued the invoice. An `<img src=x onerror=…>` in it runs as
script in the session of every user who opens the invoice. `react/no-danger` reports the line.

Good: the same line in `src/billing/pay-invoice/pay-invoice-form.tsx`, and the component it calls,
`src/billing/pay-invoice/sanitized-html.tsx`, whole, since all of it is new. The whole form is in
[component-example.md](../components/component-example.md), "The form".

```tsx
      {/* The note is HTML from outside: only SanitizedHtml may put it on the page (security.md section 4). */}
      {invoice.noteHtml === null ? null : <SanitizedHtml html={invoice.noteHtml} />}
```

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

It fixes the one problem: the note passes DOMPurify at the sink, in the same render, with the
HTML profile, and the component is the one place the lint suppression sits, with its reason
(section 4). With `RETURN_TRUSTED_TYPE: true`, DOMPurify returns a `TrustedHTML` where the browser
has Trusted Types, so the sink also passes `require-trusted-types-for 'script'` (section 4, "Make
the policy sanitise"); this was type-checked, not run in a browser [25], [30]. It
does not stop a DOMPurify bypass found later: keep the library current.

### A link that takes its href from data with no scheme check

Bad: the external link puts whatever URL it is given into `href`.

```tsx
import type { ReactNode } from "react";

type ExternalLinkProps = {
  href: string;
  children: ReactNode;
};

export function ExternalLink({ href, children }: ExternalLinkProps) {
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

The link follows whatever scheme the data holds. React 19 refuses `javascript:` and nothing else,
so a `data:` URL passes, and versions before React 19 do not refuse `javascript:` either
[11], [8]. `no-script-url` does not report this line: it sees a `javascript:` string
written in the code, not a value that arrives as data.

Good: the rule in `src/billing/list-invoices/link-url.rules.ts`, the whole file, which is new, and
the changed part of the component that uses it, `src/billing/list-invoices/external-link.tsx`.
The props type and the returned link are cut. The link is the Bad's; the whole file is in
[security-example.md](security-example.md) section 3.

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

```tsx
import { hasAllowedProtocol } from "@/billing/list-invoices/link-url.rules.ts";

...

// For an address that came from outside the application. An address the rule refuses is shown
// as plain text, never as a link (security.md section 3).
export function ExternalLink({ href, children }: ExternalLinkProps) {
  if (!hasAllowedProtocol(href)) {
    return <span>{children}</span>;
  }

  ...
}
```

It fixes the one problem: the URL is parsed, and only `https:` and `mailto:` become a link;
anything else, an unparsable string included, renders as plain text (section 3). The guard sits
at the top of the component, and the comment on the set, in the rule's own file, says why an
allowlist and not a check for `javascript:`. The reference application's invoice list shows the
customer's address through this component, and its rule has four unit tests.

### An object from outside spread as props

Bad: a status badge whose props come from the billing service as one object.

```tsx
import type { ComponentProps } from "react";

type InvoiceStatusBadgeProps = {
  // The label, colour and title, as the billing service sends them.
  badge: ComponentProps<"span">;
};

export function InvoiceStatusBadge({ badge }: InvoiceStatusBadgeProps) {
  return <span {...badge} />;
}
```

The object decides every prop of the element. A response that carries
`dangerouslySetInnerHTML: { __html: "<img src=x onerror=…>" }` puts script on the page, and
nothing in this file shows a sink (De Ryck, 2020) [18].

Good: `src/billing/list-invoices/invoice-status-badge.tsx`, the whole file.

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
  // The word carries the status. The colour repeats it and is never the only signal
  // (accessibility.md section 9).
  return <span className={`text-sm font-medium ${STATUS_COLOR[status]}`}>{STATUS_LABEL[status]}</span>;
}
```

It fixes the one problem: the data supplies one value of a closed set, and the code maps it to
the label and the colour; the two maps and the new import follow from that fix. A response can
change which badge shows, never which props the element gets (section 3).

## 16. Where the rules stop holding

- **A page with no session and no user data,** such as a public marketing page, has no token to
  protect and no request to forge: sections 6 and 7 do not apply. Its headers, its dependencies and
  its build still do.
- **A lower-risk application may run a browser-only OAuth client.** RFC 10017 recommends a BFF for
  business, sensitive and personal-data applications, and describes the other two patterns
  without forbidding them [3]. Choose one knowingly, with section 6's storage rules.
- **A client-only application has no Server Functions;** section 8 applies once a framework
  renders on the server.
- **A script an attacker already runs on the page** acts as the user under every rule here. The
  rules limit what it takes away; only preventing the injection stops it (section 2).
- **Malware on the user's machine** reads cookies and storage from the browser's files, outside
  the page's reach (RFC 10017 section 8.6) [3]. Section 2 names what a server can add.
- **A screen left open after the server's timeout, or open in another tab after logout,** keeps
  showing data until its next request; OWASP's Session Management cheat sheet notes that a
  server-side timeout expires silently and that session data may stay in the browser's cache
  [55].
- **A call from a public page to the user's local network or `localhost`** passes a permission
  prompt in Chrome since version 142, not a CORS check (Chrome's developer blog, read 2026-10-15)
  [177].
- **Old code does not wait.** These rules exist because the old way is a security hole, so old
  code is fixed by a date, not when a change happens to touch it
  ([refactoring.md](../../any-language/refactoring/refactoring.md) section 6).
- **Moving targets** change under these rules: package manager defaults, the framework and Vite
  advisories, browser support for Trusted Types and the Sanitizer API, the lint presets, the OWASP
  Top 10 edition. Each line that names one carries the date it was read, and
  [README.md](README.md) lists what to re-check.

## 17. Review checklist and the OWASP Top 10:2025

A review question per section; sections 6 and 7 each get one row for the page here and one for the
server in [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
section 5. OWASP's ASVS 5.0, chapter V3 "Web Frontend Security", is the longer checklist for the
same ground [64]. Each red flag is a way in, so one red flag is enough to stop the merge until
it is fixed or the author shows why it does not apply; that bar is the practice's choice.

| Section | Ask | Red flag |
|---|---|---|
| 2. What the browser can protect | Does the server check this request on its own? | a permission enforced only by hiding a button or a route |
| 3. XSS | Can a value from outside reach HTML, a URL, a props object, a style or code? | a URL from data with no scheme allowlist; outside data spread as props; a renderer's `urlTransform` overridden [13] |
| 4. Sanitising | Is the HTML sanitised in the sink's own render? | a second `dangerouslySetInnerHTML`; a sanitised string changed or joined after cleaning |
| 5. Headers | Does the built page run under a policy with no `'unsafe-inline'` in `script-src`? | `'unsafe-inline'` or `data:` in `script-src`; a policy only in `<meta>`; a nonce in a cached response; a check or a policy still log-only after its written end |
| 6a. Sessions, page | Can script read anything that grants access? | a token or session id in `localStorage`, `sessionStorage` or a cookie set by script; a cookie the page sets without `Secure`, a written `SameSite` or a `__Host-` or `__Secure-` prefix; `refetchInterval` on data that needs the session, unless the BFF leaves those requests out of its idle clock |
| 7a. CSRF and CORS, page | Does each request to an API route carry the CSRF defence, and does the page fix CORS errors and build API paths as section 7 says? | `mode: "no-cors"` or a public proxy in the page; a value from outside put into an API path unchecked; a request to an API route, other than the exempt ones in [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 3, made outside the one API client or without the custom header, or without `credentials: "include"` when the API is on another origin; a blob made with the response's own type, or an SVG blob |
| 8. Server-side React | Does each Server Function check the user and the record itself? | authorisation only in middleware; a secret written in server code |
| 9. Secrets | Would you publish every `VITE_` value on the login page? | a key, a token or a password behind a public prefix; production source maps published |
| 10. Supply chain | Does every install obey the cooldown and the script block, with a named emergency path? | a new dependency nobody checked on the registry; an action pinned by tag; fork code in `pull_request_target` |
| 11. Dev server | Does the dev server answer only localhost? | `allowedHosts: true`; `cors: true`; `host` open on a network you do not trust |
| 12. Edges | Does each `message` listener check one exact origin? | `postMessage(…, "*")`; a sandbox with both `allow-scripts` and `allow-same-origin`; a redirect to a raw `?next=` |
| 13. Data exposure | Can a URL, a log line or a replay carry a credential, and does a failed screen show a message of its own, not the error's text? | a token in a query string; replay masking turned off; paste blocked; the error's own text on a failed screen |
| 14. Automation | Are the sink rules on, as errors? | a suppression with no reason |

### What the OWASP Top 10 is, and how to work with it

The OWASP Top 10 is a list of the ten most critical risk categories for web applications, kept by
the OWASP Foundation [178], [179]. OWASP calls it an awareness document for developers and
web application security, one that "represents a broad consensus about the most critical security
risks to web applications" [178], [179]. The current edition is the 2025 one, the eighth
(OWASP's Impact Report 2025, read 2026-10-17); 2021 and 2017 came before it [180].
Read it at [top10.owasp.org/2025](https://top10.owasp.org/2025/), where each category has its own
page with its weaknesses, attack scenarios and prevention steps; the source text is in the
OWASP/Top10 repository on GitHub (both read 2026-10-16) [178], [179].

Each category groups many weaknesses, each one an entry in CWE, the Common Weakness Enumeration:
the ten categories of 2025 hold 248 CWEs [179]. OWASP builds the list from two inputs
[179]. Testing data on over 2.8 million applications ranks the categories by how many
applications show the weakness and by the exploit and impact scores of the known vulnerabilities
behind it; eight categories come from that data [179]. A survey of practitioners picks the
other two, because a new kind of weakness reaches testing tools, and so the data, only weeks or
years after it appears [179].

Work with it this way:

- **In a review, check against the checklist above; use the Top 10 only to name a finding's
  category.** OWASP calls it "primarily an awareness document", and as a coding or testing
  standard "the bare minimum and just a starting point" [181]. Some of its
  risks, such as A06 Insecure Design, are "beyond the scope of most forms of testing", and OWASP
  discourages any claim of full coverage because it is "simply untrue" [181]. A team that
  checks only the ten categories believes it is done. The table below says which section of this
  file covers each 2025 category. The checklist above holds the red flags of the highest-risk acts;
  a review also reads the rules of every section the change touches.
- **When the project starts, pick its
  [ASVS](https://owasp.org/www-project-application-security-verification-standard/) level and
  write it into the decision log ("Write it down" in
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  2 says where),** so reviews and tests know the target; writing it down is this practice's choice.
  OWASP's Application Security Verification Standard (ASVS 5.0, read 2026-10-16) has three levels:
  Level 1 holds "the minimum requirements to consider when securing an application", Level 2 is the
  level "most applications should be striving to achieve", and Level 3 is for applications that must
  show the highest level of security [182].
- **When you write a feature's security requirements, take them from ASVS at the chosen level,**
  since ASVS is the standard the Top 10 sends teams to, because each requirement in it can be
  verified and tested [181]. Chapters V3 Web Frontend Security and V7 Session Management are
  the parts closest to this file [64], [71].
- **When you design a feature that touches authentication, access control, business logic or a key
  flow, model its threats first, with OWASP's
  [Threat Modeling cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html),**
  since OWASP's guide to an application security program puts threat modelling in the planning
  and design phase, and A06 Insecure Design asks for it for critical parts of the application,
  such as authentication, access control, business logic and key flows [183], [181],
  [184].
- **When you build a feature, first read what the
  [OWASP Top 10 Proactive Controls](https://top10proactive.owasp.org/) and the
  [Cheat Sheet Series](https://cheatsheetseries.owasp.org/) say about what it handles,** such as a
  session, input or output, since OWASP's guide to an application security program names them as
  "a good starting point" for designing security in [181]. The Proactive Controls (2024 edition,
  read 2026-10-16) are the techniques OWASP writes for developers, and the Cheat Sheet Series gives
  concise guidance on one topic at a time; this file cites both throughout [185], [186].
- **Before a release that changes authentication, access control, business logic or a key flow,
  test the application against the
  [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/),
  or give it to whoever runs the security test,** so the test follows OWASP's own method and does
  not stop at the ten categories. The WSTG (stable version 4.2, read 2026-10-16) is OWASP's
  testing guide for web applications, for a penetration test or a code review; the moment is this
  practice's choice [187].
- **When OWASP publishes a new edition, the team that adopted this practice maps its categories to
  this file again,** since categories move and merge between editions (server-side request forgery
  joined A01 in 2025); the rule is this practice's choice [179].

### The OWASP Top 10:2025, mapped to this file

The table says where each category meets a React application and which section here covers it.
Where a category is mostly the server's, the middle column says so, and the browser side's part
is named.

| Category | What it means for a React application | Sections |
|---|---|---|
| A01 Broken Access Control [4] | the server decides every access; the page hides what the user cannot use, for the user's sake. OWASP counts CSRF, CORS mistakes and server-side request forgery here [4] | 2, 7, 8; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) sections 2, 3 |
| A02 Security Misconfiguration [178] | headers, cookie attributes, the CORS policy and the dev server are configuration | 5, 6, 7, 11; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) sections 2, 3 |
| A03 Software Supply Chain Failures [178] | the packages you install, the lockfile and the CI workflow | 10 |
| A04 Cryptographic Failures [178] | mostly the server's: HTTPS, HSTS and no caching of responses with personal data; the browser side keeps secrets out of the bundle; password storage for a first-party login is outside this practice ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 5) | 5, 9, 13 |
| A05 Injection [178] | XSS is injection into the page; the server checks the format of each path segment and of each report ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 3); injection into the server's own interpreters, such as SQL or an OS command, is outside this practice | 3, 4, 5, 7; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 3 |
| A06 Insecure Design [178] | a check in the page helps the user and protects nothing; the design puts every control on the server, and the session in a BFF; OWASP asks to model the threats of critical flows such as sign-in and access control (the threat-modelling step above) [184] | 2, 6 |
| A07 Authentication Failures [178] | mostly the server's: the OAuth flow, a new session id at login, timeouts, logout and re-authentication; the browser side holds no token and runs the sign-out path on a `401`; a first-party login's password storage, throttling and sign-in error messages are outside this practice ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 5) | 6; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2 |
| A08 Software or Data Integrity Failures [178] | scripts from other origins, Subresource Integrity, and state the server writes into the page; an object from outside spread as props (section 3); the session's state in a signed and encrypted cookie ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2); the arguments of a Server Function (section 8) | 3, 6, 8, 10, 12; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2 |
| A09 Security Logging and Alerting Failures [178] | mostly the server's: it logs security events, and alerts a person when the rejections of one check pass their written rate and on every step-up from another account; the browser side keeps credentials out of its own reports [188] | 6, 7, 13; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) sections 2, 3 |
| A10 Mishandling of Exceptional Conditions [178] | mostly the server's: it fails closed; the browser side shows a message of its own on a failed screen, never the error's text | 6, 13; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2 |

Two more OWASP sources sound like they belong here, and neither is mapped (both read 2026-10-15).
The "Top 10 Client-Side Security Risks" is an Incubator project whose list is still the 2022
candidate [189]. The OWASP React Security cheat sheet sits in the drafts folder of the cheat
sheet repository and is not published on the cheat sheet site [190].

## 18. Sources

Checked 2026-10-17 unless a line ends with — checked <YYYY-MM-DD>.

- [1] MDN — Cross-Origin Resource Sharing (CORS) — https://github.com/mdn/content/blob/44a1a0348720bbd1b1085c7d92b93b4fd311a3dd/files/en-us/web/http/guides/cors/index.md
- [2] WHATWG — Fetch Standard, Living Standard, commit snapshot e9460d1 — https://fetch.spec.whatwg.org/commit-snapshots/e9460d1b22ead1c6a72eeac37fb2ec0dc01aeb1d/
- [3] IETF — RFC 10017, OAuth 2.0 for Browser-Based Applications, BCP 212, August 2026 — https://www.rfc-editor.org/rfc/rfc10017.txt
- [4] OWASP — OWASP Top 10:2025, A01:2025 Broken Access Control — https://top10.owasp.org/2025/A01_2025-Broken_Access_Control
- [5] OWASP — Authorization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- [6] OWASP Cheat Sheet Series — Cookie Theft Mitigation Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/cedcdcb3e94d1748e964e296f9f3c71d1de8da0d/cheatsheets/Cookie_Theft_Mitigation_Cheat_Sheet.md
- [7] Google — Protecting Cookies with Device Bound Session Credentials — https://blog.google/security/protecting-cookies-with-device-bound-session-credentials/
- [8] Philippe De Ryck — Preventing XSS in React (Part 1): Data binding and URLs (Pragmatic Web Security, 2020; opinion) — https://pragmaticwebsecurity.com/articles/spasecurity/react-xss-part1.html
- [9] OWASP — Cross Site Scripting Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- [10] React — Common components (e.g. <div>) — https://react.dev/reference/react-dom/components/common
- [11] React — React 19 Upgrade Guide — https://react.dev/blog/2024/04/25/react-19-upgrade-guide#other-breaking-changes
- [12] kassens — sanitize javascript: urls for <object> tags (React, GitHub pull request #29808, 2024; kind not confirmed) — https://github.com/react/react/pull/29808
- [13] remarkjs — react-markdown README — https://github.com/remarkjs/react-markdown/blob/8545ebd7416beb2af2bfef59440db231abe69f13/readme.md
- [14] HashiCorp — HCSEC-2026-01: Arbitrary code execution in React server-side rendering of untrusted MDX content — https://discuss.hashicorp.com/t/hcsec-2026-01-arbitrary-code-execution-in-react-server-side-rendering-of-untrusted-mdx-content/77155
- [15] Yahoo — serialize-javascript README, v7.1.2 — https://github.com/yahoo/serialize-javascript/blob/v7.1.2/README.md
- [16] James K. Nelson — CSS-in-JS security: the rascal's guide (Frontend Armory, 2017, updated 2019; opinion) — https://frontarm.com/james-k-nelson/how-can-i-use-css-in-js-securely/
- [17] OWASP — DOM based XSS Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html
- [18] Philippe De Ryck — Preventing XSS in React (Part 2): dangerouslySetInnerHTML (Pragmatic Web Security, 2020; opinion) — https://pragmaticwebsecurity.com/articles/spasecurity/react-xss-part2.html
- [19] Paperclip — GHSA-fpw4-p57j-hqmq: Stored XSS via javascript: URLs in MarkdownBody, urlTransform override disables react-markdown sanitization — https://github.com/advisories/GHSA-fpw4-p57j-hqmq
- [20] Redux — Server Rendering — https://redux.js.org/usage/server-rendering
- [21] Vercel — Next.js docs: How to implement JSON-LD in your Next.js application, 16.4.2 — https://nextjs.org/docs/app/guides/json-ld
- [22] NIST NVD — CVE-2024-11831 — https://nvd.nist.gov/vuln/detail/CVE-2024-11831
- [23] Vercel — GHSA-gx5p-jg67-6x7h: Next.js has cross-site scripting in beforeInteractive scripts with untrusted input (CVE-2026-44580) — https://github.com/advisories/GHSA-gx5p-jg67-6x7h
- [24] Cure53 — GHSA-h8r8-wccr-v5f2: DOMPurify is vulnerable to mutation-XSS via Re-Contextualization (CVE-2026-65914) — https://github.com/advisories/GHSA-h8r8-wccr-v5f2
- [25] Cure53 — DOMPurify README, 3.4.17 — https://github.com/cure53/DOMPurify/blob/3.4.17/README.md
- [26] MDN Web Docs (Mozilla) — Element: setHTML() method — https://developer.mozilla.org/en-US/docs/Web/API/Element/setHTML
- [27] Cure53 — DOMPurify releases 3.4.0 to 3.4.17 — https://github.com/cure53/DOMPurify/releases
- [28] Cure53 — GHSA-v9jr-rg53-9pgp: DOMPurify: Prototype Pollution to XSS Bypass via CUSTOM_ELEMENT_HANDLING Fallback (CVE-2026-41238) — https://github.com/advisories/GHSA-v9jr-rg53-9pgp
- [29] MDN Web Docs (Mozilla) — Trusted Types API — https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API
- [30] Krzysztof Kotowicz — Prevent DOM-based cross-site scripting vulnerabilities with Trusted Types (web.dev, no date; opinion) — https://web.dev/articles/trusted-types
- [31] Vik Vanderlinden and Gertjan Franken — Security, The 2025 Web Almanac, chapter 9 (HTTP Archive, 2025; research) — https://almanac.httparchive.org/en/2025/security
- [32] Lukas Weichselbaum, Michele Spagnuolo, Sebastian Lekies and Artur Janc — CSP Is Dead, Long Live CSP! On the Insecurity of Whitelists and the Future of Content Security Policy (ACM CCS 2016, 2016; research, sponsored by Google) — https://doi.org/10.1145/2976749.2978363
- [33] Vite — HTML plugin source, packages/vite/src/node/plugins/html.ts — https://github.com/vitejs/vite/blob/df7503cc499e0b49e45701e3be7546918ee9d322/packages/vite/src/node/plugins/html.ts
- [34] Lukas Weichselbaum — Mitigate cross-site scripting (XSS) with a strict Content Security Policy (CSP) (web.dev, no date; opinion) — https://web.dev/articles/strict-csp
- [35] David Dworken — Securely hosting user data in modern web applications (web.dev, 2023; case) — https://web.dev/articles/securely-hosting-user-data
- [36] Vite — Features, "Content Security Policy (CSP)" — https://github.com/vitejs/vite/blob/df7503cc499e0b49e45701e3be7546918ee9d322/docs/guide/features.md
- [37] Next.js (Vercel) — How to set a Content Security Policy (CSP) for your Next.js application, v16.4.2 — https://github.com/vercel/next.js/blob/v16.4.2/docs/01-app/02-guides/content-security-policy.mdx
- [38] OWASP Cheat Sheet Series — Content Security Policy Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/1a78ae3e443cef156e947f87e892efbcc62876ee/cheatsheets/Content_Security_Policy_Cheat_Sheet.md
- [39] Matteo Golinelli, Francesco Bonomi and Bruno Crispo — The Nonce-nce of Web Security: an Investigation of CSP Nonces Reuse (arXiv, accepted at the WASP workshop of ESORICS 2023, 2023; research) — https://arxiv.org/abs/2309.07782v1
- [40] Ryan Chaplin — Bypassing a WAF and a CSP with Google Tag Manager: An Attacker's Perspective and Remediation Advice (Raxis blog, 2026; opinion) — https://raxis.com/blog/bypassing-waf-and-csp-with-google-tag-manager/
- [41] Vite — Shared Options (`html.cspNonce`, `publicDir`) — https://github.com/vitejs/vite/blob/df7503cc499e0b49e45701e3be7546918ee9d322/docs/config/shared-options.md
- [42] MDN Web Docs (Mozilla) — Content-Security-Policy: style-src directive — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/style-src
- [43] Emotion — @emotion/cache README — https://github.com/emotion-js/emotion/blob/b882bcba85132554992e4bd49e94c95939bbf810/packages/cache/README.md
- [44] styled-components — FAQs — https://styled-components.com/docs/faqs
- [45] MDN Web Docs (Mozilla) — Content Security Policy (CSP) — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP
- [46] MDN Web Docs (Mozilla) — Content Security Policy (CSP) implementation — https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/CSP
- [47] MDN Web Docs (Mozilla) — Content-Security-Policy: frame-ancestors directive — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors
- [48] Netlify — Custom headers — https://docs.netlify.com/manage/routing/headers/
- [49] Cloudflare — Headers (Cloudflare Pages docs) — https://developers.cloudflare.com/pages/configuration/headers/
- [50] Vercel — Static Configuration with vercel.json, "headers" — https://vercel.com/docs/project-configuration/vercel-json#headers
- [51] OWASP Cheat Sheet Series — HTTP Security Response Headers Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/1a78ae3e443cef156e947f87e892efbcc62876ee/cheatsheets/HTTP_Headers_Cheat_Sheet.md
- [52] MDN Web Docs (Mozilla) — Referrer policy configuration — https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/Referrer_policy
- [53] MDN — Cross-Origin-Opener-Policy (COOP) header — https://github.com/mdn/content/blob/44a1a0348720bbd1b1085c7d92b93b4fd311a3dd/files/en-us/web/http/reference/headers/cross-origin-opener-policy/index.md
- [54] OWASP Cheat Sheet Series — Clickjacking Defense Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/1a78ae3e443cef156e947f87e892efbcc62876ee/cheatsheets/Clickjacking_Defense_Cheat_Sheet.md
- [55] OWASP Cheat Sheet Series — Session Management Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/1a78ae3e443cef156e947f87e892efbcc62876ee/cheatsheets/Session_Management_Cheat_Sheet.md
- [56] Philippe De Ryck — Why avoiding LocalStorage for tokens is the wrong solution (Pragmatic Web Security, 2020; opinion) — https://pragmaticwebsecurity.com/articles/oauthoidc/localstorage-xss.html
- [57] Andrea Chiarelli — Things Developers Get Wrong About the Backend for Frontend Pattern (Auth0 blog, 2026; sponsored by Auth0) — https://auth0.com/blog/things-developers-get-wrong-about-the-backend-for-frontend-pattern/
- [58] IETF — RFC 9700, Best Current Practice for OAuth 2.0 Security, BCP 240, January 2025 — https://www.rfc-editor.org/rfc/rfc9700.txt
- [59] oauth.net — OAuth 2.0 for Browser-Based Apps (oauth.net, no date; kind not confirmed) — https://oauth.net/2/browser-based-apps/
- [60] OWASP Cheat Sheet Series — Authentication Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/1a78ae3e443cef156e947f87e892efbcc62876ee/cheatsheets/Authentication_Cheat_Sheet.md
- [61] Auth0 — Auth0 Single Page App SDK — https://auth0.com/docs/libraries/auth0-single-page-app-sdk
- [62] Microsoft — Caching in MSAL.js — https://learn.microsoft.com/en-us/entra/msal/javascript/browser/caching
- [63] Okta — Okta Auth JavaScript SDK README, okta-auth-js-8.0.1 — https://github.com/okta/okta-auth-js/blob/okta-auth-js-8.0.1/README.md
- [64] OWASP — Application Security Verification Standard, chapter V3 Web Frontend Security, 5.0.0 — https://github.com/OWASP/ASVS/blob/v5.0.0_release/5.0/en/0x12-V3-Web-Frontend-Security.md
- [65] IETF HTTP Working Group (S. Bingler, M. West, J. Wilander, eds.) — Cookies: HTTP State Management Mechanism, draft-ietf-httpbis-rfc6265bis-22, December 2025 — https://datatracker.ietf.org/doc/html/draft-ietf-httpbis-rfc6265bis-22
- [66] IETF — RFC 9449, OAuth 2.0 Demonstrating Proof of Possession (DPoP), September 2023 — https://www.rfc-editor.org/rfc/rfc9449
- [67] Philippe De Ryck — A Critical Analysis of Refresh Token Rotation in Single-page Applications (Ping Identity blog, guest post, 2021; opinion) — https://www.pingidentity.com/en-us/docs/blogs/refresh-token-rotation-spa
- [68] TanStack — TanStack Query docs (React), Important Defaults — https://github.com/TanStack/query/blob/67b12ae1a0bca52472d0e54a38a6822458aaa858/docs/framework/react/guides/important-defaults.md
- [69] TanStack — TanStack Query docs (React), Polling — https://github.com/TanStack/query/blob/67b12ae1a0bca52472d0e54a38a6822458aaa858/docs/framework/react/guides/polling.md
- [70] TanStack — TanStack Query docs (React), Query Retries — https://github.com/TanStack/query/blob/4e8be3f46f35b9208184f95e50fa1dc61fccef1f/docs/framework/react/guides/query-retries.md
- [71] OWASP — Application Security Verification Standard, chapter V7 Session Management, 5.0.0 — https://github.com/OWASP/ASVS/blob/v5.0.0_release/5.0/en/0x16-V7-Session-Management.md
- [72] OpenID Foundation — OpenID Connect RP-Initiated Logout 1.0, final, 12 September 2022 — https://openid.net/specs/openid-connect-rpinitiated-1_0.html
- [73] OWASP Cheat Sheet Series — Cross-Site Request Forgery Prevention Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/1a78ae3e443cef156e947f87e892efbcc62876ee/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md
- [74] MDN — Request: credentials property — https://developer.mozilla.org/en-US/docs/Web/API/Request/credentials
- [75] WHATWG — URL Standard, sections 4.7 "Origin", 5.2 "application/x-www-form-urlencoded serializing" and 6.2 "URLSearchParams class", commit snapshot fde3f74 — https://url.spec.whatwg.org/commit-snapshots/fde3f74f063341a28d437216f75735b8b40128f5/
- [76] W3C — File API, Editor's Draft, 12 September 2026, sections 8.2, 8.3.1 and 8.4 — https://w3c.github.io/FileAPI/#url-model
- [77] MDN Web Docs (Mozilla) — Content-Disposition header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Disposition
- [78] MDN Web Docs (Mozilla) — EventSource() constructor — https://developer.mozilla.org/en-US/docs/Web/API/EventSource/EventSource
- [79] Maxence Schmitt — Exploiting Client-Side Path Traversal to Perform Cross-Site Request Forgery - Introducing CSPT2CSRF (Doyensec blog, 2024; research, sponsored by Doyensec) — https://blog.doyensec.com/2024/07/02/cspt2csrf.html
- [80] Maxence Schmitt — Exploiting Client-Side Path Traversal: CSRF is dead, long live CSRF (Doyensec, no date; research, sponsored by Doyensec) — https://www.doyensec.com/resources/Doyensec_CSPT2CSRF_Whitepaper.pdf
- [81] NIST NVD — CVE-2023-45316 (Mattermost) — https://nvd.nist.gov/vuln/detail/CVE-2023-45316
- [82] OWASP Cheat Sheet Series — WebSocket Security Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/fdd74a30ff147436f218df84778651cad6b8d9a4/cheatsheets/WebSocket_Security_Cheat_Sheet.md
- [83] W3C — Content Security Policy Level 3, Editor's Draft, 16 September 2026, section 6.7.2.9 "scheme-part matching" — https://w3c.github.io/webappsec-csp/#match-schemes
- [84] MDN — CloseEvent: code property — https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code
- [85] WHATWG — WebSockets Standard, Living Standard, commit snapshot 9879e5c — https://websockets.spec.whatwg.org/commit-snapshots/9879e5cf0d66c66af6990e4c75f72dda794e1b87/
- [86] MDN — Request: mode property — https://developer.mozilla.org/en-US/docs/Web/API/Request/mode
- [87] Vite — Server options (docs/config/server-options.md) — https://github.com/vitejs/vite/blob/ce4293f15cc5cd221c5ed60f5cd64e82ca5cbaf5/docs/config/server-options.md
- [88] React — Critical Security Vulnerability in React Server Components — https://github.com/reactjs/react.dev/blob/046f17d04295ba047bb5739026b4ac3110f17028/src/content/blog/2025/12/03/critical-security-vulnerability-in-react-server-components.md
- [89] Next.js — How to think about data security in Next.js — https://github.com/vercel/next.js/blob/e2e7393c1f8449759aa1ae502b64fd7e946fbf37/docs/01-app/02-guides/data-security.mdx
- [90] Next.js (Sebastian Markbåge) — How to Think About Security in Next.js — https://nextjs.org/blog/security-nextjs-server-components-actions
- [91] Next.js — GHSA-f82v-jwr5-mffw, Authorization Bypass in Next.js Middleware (CVE-2025-29927) — https://github.com/advisories/GHSA-f82v-jwr5-mffw
- [92] Ty Sbano — Postmortem on Next.js Middleware bypass (Vercel blog, 2025; case) — https://vercel.com/blog/postmortem-on-next-js-middleware-bypass
- [93] Netlify — Next.js & React security release (May 2026): what to know (Netlify changelog, 2026; kind not confirmed) — https://www.netlify.com/changelog/2026-05-08-react-nextjs-security-vulnerabilities/
- [94] React — experimental_taintObjectReference — https://github.com/reactjs/react.dev/blob/046f17d04295ba047bb5739026b4ac3110f17028/src/content/reference/react/experimental_taintObjectReference.md
- [95] Next.js — Next.js Security Update: December 11, 2025 — https://nextjs.org/blog/security-update-2025-12-11
- [96] React — Denial of Service and Source Code Exposure in React Server Components — https://github.com/reactjs/react.dev/blob/046f17d04295ba047bb5739026b4ac3110f17028/src/content/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components.md
- [97] CJ Moses — China-nexus cyber threat groups rapidly exploit React2Shell vulnerability (CVE-2025-55182) (AWS Security Blog, 2025; case) — https://aws.amazon.com/blogs/security/china-nexus-cyber-threat-groups-rapidly-exploit-react2shell-vulnerability-cve-2025-55182/
- [98] Microsoft Defender Security Research Team — Defending against the CVE-2025-55182 (React2Shell) vulnerability in React Server Components (Microsoft Security Blog, 2025; case) — https://www.microsoft.com/en-us/security/blog/2025/12/15/defending-against-the-cve-2025-55182-react2shell-vulnerability-in-react-server-components/
- [99] Next.js — Security Advisory: CVE-2025-66478 — https://nextjs.org/blog/CVE-2025-66478
- [100] Aragorn Tseng, Robert Weiner, Casey Charrier, Zander Work, Genevieve Stark, Austin Larsen — Multiple Threat Actors Exploit React2Shell (CVE-2025-55182) (Google Cloud Blog, Google Threat Intelligence Group, 2025; case) — https://cloud.google.com/blog/topics/threat-intelligence/threat-actors-exploit-react2shell-cve-2025-55182
- [101] Renovate — Configuration options — https://docs.renovatebot.com/configuration-options/#minimumreleaseage
- [102] Renovate — Security presets — https://docs.renovatebot.com/presets-security/
- [103] GitHub — Dependabot options reference — https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference
- [104] React Router — GHSA-3cgp-3xvw-98x8, XSS in meta() script:ld+json (CVE-2025-59057) — https://github.com/advisories/GHSA-3cgp-3xvw-98x8
- [105] React Router — GHSA-8v8x-cx79-35w7, SSR XSS in ScrollRestoration (CVE-2026-21884) — https://github.com/advisories/GHSA-8v8x-cx79-35w7
- [106] React Router — GHSA-2w69-qvjg-hvjx, XSS via Open Redirects (CVE-2026-22029) — https://github.com/advisories/GHSA-2w69-qvjg-hvjx
- [107] Vite — Env Variables and Modes — https://github.com/vitejs/vite/blob/df7503cc499e0b49e45701e3be7546918ee9d322/docs/guide/env-and-mode.md
- [108] Next.js — Environment Variables guide — https://github.com/vercel/next.js/blob/e2e7393c1f8449759aa1ae502b64fd7e946fbf37/docs/01-app/02-guides/environment-variables.mdx
- [109] Vite — Build Options — https://github.com/vitejs/vite/blob/df7503cc499e0b49e45701e3be7546918ee9d322/docs/config/build-options.md
- [110] Next.js — productionBrowserSourceMaps — https://github.com/vercel/next.js/blob/e2e7393c1f8449759aa1ae502b64fd7e946fbf37/docs/01-app/03-api-reference/05-config/01-next-config-js/productionBrowserSourceMaps.mdx
- [111] Nurullah Demir, Yash Vekaria, Georgios Smaragdakis, Zakir Durumeric — Keys on Doormats: Exposed API Credentials on the Web (arXiv preprint v3, 2026; research) — https://arxiv.org/abs/2603.12498v3
- [112] Google — Google Maps Platform security guidance — https://developers.google.com/maps/api-security-best-practices
- [113] Michael Bires — CVE-2025-48757: 170+ Lovable Apps With Open Supabase Tables (michaelbir.es, 2026; case, on the author's page that sells security audits) — https://www.michaelbir.es/case-studies/lovable-supabase-rls-security-audit/
- [114] Matt Palmer — CVE-2025-48757 (mattpalmer.io, 2025; case) — https://mattpalmer.io/posts/CVE-2025-48757/
- [115] GitHub — Push protection — https://github.com/github/docs/blob/dae83f7d28f3b8e10015bd6b6d8b72267cedceca/content/code-security/concepts/secret-security/push-protection.md
- [116] Gitleaks — Gitleaks README — https://github.com/gitleaks/gitleaks/blob/b58d3f102cf3a2c84cb7f923d05c25c9b1aed84b/README.md
- [117] GitHub — Remediating a leaked secret in your repository — https://github.com/github/docs/blob/dae83f7d28f3b8e10015bd6b6d8b72267cedceca/content/code-security/tutorials/remediate-leaked-secrets/remediating-a-leaked-secret.md
- [118] Xavier René-Corail — Our plan for a more secure npm supply chain (The GitHub Blog, 2025; case) — https://github.blog/security/supply-chain-security/our-plan-for-a-more-secure-npm-supply-chain/
- [119] Justin Moore — "Shai-Hulud" Worm Compromises npm Ecosystem in Supply Chain Attack (Unit 42, Palo Alto Networks, 2025; research, sponsored by Palo Alto Networks) — https://unit42.paloaltonetworks.com/npm-supply-chain-attack/
- [120] Aaron Brown — Critical npm supply chain attack response – September 8, 2025 (Vercel blog, 2025; case) — https://vercel.com/blog/critical-npm-supply-chain-attack-response-september-8-2025
- [121] Nx (nrwl) — Malicious versions of Nx and some supporting plugins were published, GHSA-cxm3-wv7p-598c — https://github.com/nrwl/nx/security/advisories/GHSA-cxm3-wv7p-598c
- [122] CISA — Supply Chain Compromise Impacts Axios Node Package Manager — https://www.cisa.gov/news-events/alerts/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager
- [123] Microsoft Threat Intelligence and Microsoft Defender Security Research Team — Mitigating the Axios npm supply chain compromise (Microsoft Security Blog, 2026; research, sponsored by Microsoft) — https://www.microsoft.com/en-us/security/blog/2026/04/01/mitigating-the-axios-npm-supply-chain-compromise/
- [124] jasonsaayman (axios lead maintainer) — Post Mortem: axios npm supply chain compromise (axios GitHub issue #10636, 2026; case) — https://github.com/axios/axios/issues/10636
- [125] Tanner Linsley — Postmortem: TanStack npm supply-chain compromise (TanStack blog, 2026; case) — https://tanstack.com/blog/npm-supply-chain-compromise-postmortem
- [126] Stephen Thoemmes — TanStack npm packages compromised: inside the Mini Shai-Hulud supply chain attack (Snyk blog, 2026; research, sponsored by Snyk) — https://snyk.io/blog/tanstack-npm-packages-compromised/
- [127] Microsoft Security Research, Ravikant Tiwari, Sagar Patil, Suriyaraj Natarajan and Arvind Gowda — Unpacking the AsyncAPI npm supply chain compromise and import-time payload delivery (Microsoft Security Blog, 2026; research, sponsored by Microsoft) — https://www.microsoft.com/en-us/security/blog/2026/07/15/unpacking-asyncapi-npm-supply-chain-compromise-import-time-payload-delivery/
- [128] lilting channel — Blocking Shai-Hulud npm waves with pnpm 11 default minimumReleaseAge, Yarn 4.10 npmMinimalAgeGate, and npm v11.10 (with ignore-scripts gotchas) (lilting channel, 2026; opinion) — https://lilting.ch/en/articles/pnpm-11-minimum-release-age-default-shai-hulud-defense
- [129] Kush Pandya — 2025 Report: Destructive Malware in Open Source Packages (Socket blog, 2025; research, sponsored by Socket) — https://socket.dev/blog/2025-report-destructive-malware-in-open-source-packages
- [130] npm — Config, v12 — https://docs.npmjs.com/cli/v12/using-npm/config
- [131] npm — Changelog, v12 — https://docs.npmjs.com/cli/v12/using-npm/changelog
- [132] npm — Config, v11 — https://docs.npmjs.com/cli/v11/using-npm/config
- [133] pnpm — Settings: build — https://pnpm.io/settings/build
- [134] pnpm — Mitigating supply chain attacks — https://pnpm.io/supply-chain-security
- [135] npm — Changelog, v11 — https://docs.npmjs.com/cli/v11/using-npm/changelog
- [136] npm — Config, v10 — https://docs.npmjs.com/cli/v10/using-npm/config
- [137] pnpm — Settings: dependency resolution — https://pnpm.io/settings/dependency-resolution
- [138] npm — npm-audit, v11 — https://docs.npmjs.com/cli/v11/commands/npm-audit
- [139] npm — npm-ci, v12 — https://docs.npmjs.com/cli/v12/commands/npm-ci
- [140] npm — package.json, v11 — https://docs.npmjs.com/cli/v11/configuring-npm/package-json#overrides
- [141] Yarn — Configuration options (.yarnrc.yml) — https://yarnpkg.com/configuration/yarnrc
- [142] Bun — bunfig.toml — https://bun.com/docs/runtime/bunfig
- [143] Tadashi Shigeoka — How pnpm's minimumReleaseAgeExclude Helped with Emergency Security Updates (CodeNote.net, 2025; case) — https://codenote.net/en/posts/pnpm-minimumreleaseageexclude-for-emergency-vulnerability-fixes/
- [144] Vite — Security advisories — https://github.com/vitejs/vite/security/advisories
- [145] Joseph Spracklen, Raveen Wijewickrama, A H M Nazmus Sakib, Anindya Maiti, Bimal Viswanath and Murtuza Jadliwala — We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs (USENIX Security 2025; research) — https://arxiv.org/abs/2406.10279v3
- [146] Aleksandr Churilov — The Range Shrinks, the Threat Remains: Re-evaluating LLM Package Hallucinations on the 2026 Frontier-Model Cohort (arXiv preprint, 2026; research) — https://arxiv.org/abs/2605.17062v3
- [147] Liran Tal — lockfile-lint README (GitHub, 2026; kind not confirmed) — https://github.com/lirantal/lockfile-lint/blob/72a368dfe5890612cc2b531251430be681f8370c/README.md
- [148] Dan Abramov — npm audit: Broken by Design (overreacted, 2021; opinion) — https://overreacted.io/npm-audit-broken-by-design/
- [149] OSV-Scanner — Supported languages and lockfiles — https://github.com/google/osv-scanner/blob/f0e28d3623dc9e451003c424dde7ac03430a1147/docs/supported_languages_and_lockfiles.md
- [150] GitHub — Secure use reference (GitHub Actions) — https://docs.github.com/en/actions/reference/security/secure-use
- [151] Vite — Preview options (docs/config/preview-options.md) — https://github.com/vitejs/vite/blob/91b5dc18e7119d0df59abfdaa6126e9f58503c65/docs/config/preview-options.md
- [152] OWASP — Third Party JavaScript Management Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/41da8e658d9163fbc77c27f89c262262a59f1f03/cheatsheets/Third_Party_Javascript_Management_Cheat_Sheet.md
- [153] Mozilla (MDN Web Docs) — Subresource Integrity — https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Subresource_Integrity
- [154] Munir, Demir, Li, Kollnig and Shafiq — Every Keystroke You Make: A Tech-Law Measurement and Analysis of Event Listeners for Wiretapping (arXiv preprint, 2025; research) — https://doi.org/10.48550/arXiv.2508.19825
- [155] Mozilla (MDN Web Docs) — Window: postMessage() method — https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage
- [156] Jhilakshi Sharma — postMessaged and Compromised (Microsoft Security Response Center blog, 2025; case) — https://www.microsoft.com/en-us/msrc/blog/2025/08/postmessaged-and-compromised
- [157] OWASP Cheat Sheet Series — HTML5 Security Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/1a78ae3e443cef156e947f87e892efbcc62876ee/cheatsheets/HTML5_Security_Cheat_Sheet.md
- [158] Mozilla (MDN Web Docs) — <iframe>: The Inline Frame element — https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe
- [159] OWASP Cheat Sheet Series — Unvalidated Redirects and Forwards Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html
- [160] Mozilla (MDN Web Docs) — rel="noopener" — https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel/noopener
- [161] OWASP Cheat Sheet Series — REST Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
- [162] OWASP Cheat Sheet Series — Logging Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- [163] OWASP Cheat Sheet Series — Error Handling Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html
- [164] Sentry — Session Replay: Privacy (Sentry for React) — https://docs.sentry.io/platforms/javascript/guides/react/session-replay/privacy/
- [165] PostHog — Session replay: Privacy controls — https://posthog.com/docs/session-replay/privacy
- [166] Mozilla (MDN Web Docs) — HTML attribute: autocomplete — https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/autocomplete
- [167] NCSC — Password policy: updating your approach, version 1.0 — https://www.ncsc.gov.uk/collection/passwords/updating-your-approach
- [168] ESLint — eslint:recommended rule set (packages/js/src/configs/eslint-recommended.js), v10.13.0 — https://github.com/eslint/eslint/blob/v10.13.0/packages/js/src/configs/eslint-recommended.js
- [169] typescript-eslint — no-implied-eval, v8.71.2 — https://typescript-eslint.io/rules/no-implied-eval/
- [170] jsx-eslint — eslint-plugin-react README, v7.37.5 — https://github.com/jsx-eslint/eslint-plugin-react/blob/v7.37.5/README.md
- [171] ESLint React — Rules overview — https://www.eslint-react.xyz/docs/rules/overview
- [172] Mozilla — eslint-plugin-no-unsanitized README, v4.1.5 — https://github.com/mozilla/eslint-plugin-no-unsanitized/blob/v4.1.5/README.md
- [173] Biome — noDangerouslySetInnerHtml — https://biomejs.dev/linter/rules/no-dangerously-set-inner-html/
- [174] Biome — noGlobalEval — https://biomejs.dev/linter/rules/no-global-eval/
- [175] Google — CSP Evaluator — https://csp-evaluator.withgoogle.com/
- [176] Mozilla (MDN) — HTTP Observatory — https://developer.mozilla.org/en-US/observatory
- [177] Google Chrome — New permission prompt for Local Network Access — https://developer.chrome.com/blog/local-network-access
- [178] OWASP Foundation — OWASP Top 10:2025 — https://top10.owasp.org/2025/
- [179] OWASP — OWASP Top 10:2025, index, Introduction, About OWASP and "What are Application Security Risks" — https://github.com/OWASP/Top10/blob/57db8ec5ddbca1dfef5aa77cbb81951e94f714cf/2025/docs/en/0x00_2025-Introduction.md, https://github.com/OWASP/Top10/blob/57db8ec5ddbca1dfef5aa77cbb81951e94f714cf/2025/docs/en/0x02_2025-What_are_Application_Security_Risks.md, https://github.com/OWASP/Top10/blob/57db8ec5ddbca1dfef5aa77cbb81951e94f714cf/2025/docs/en/index.md
- [180] OWASP Foundation — OWASP Impact Report 2025, "A word from our Executive Director" (page 4) — https://owasp.org/assets/files/OWASP_Impact_Report_2025.pdf
- [181] OWASP — OWASP Top 10:2025, "Establishing a Modern Application Security Program" — https://github.com/OWASP/Top10/blob/57db8ec5ddbca1dfef5aa77cbb81951e94f714cf/2025/docs/en/0x03_2025-Establishing_a_Modern_Application_Security_Program.md
- [182] OWASP — Application Security Verification Standard 5.0.0, "What is the ASVS?" — https://github.com/OWASP/ASVS/blob/v5.0.0_release/5.0/en/0x03-What-is-the-ASVS.md
- [183] OWASP Cheat Sheet Series — Threat Modeling Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/1a78ae3e443cef156e947f87e892efbcc62876ee/cheatsheets/Threat_Modeling_Cheat_Sheet.md
- [184] OWASP — OWASP Top 10:2025, A06:2025 Insecure Design — https://github.com/OWASP/Top10/blob/3a31f35346c3f4e90f350395124382fa53af2afe/2025/docs/en/A06_2025-Insecure_Design.md
- [185] OWASP — OWASP Top 10 Proactive Controls, 2024 — https://top10proactive.owasp.org/
- [186] OWASP — OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- [187] OWASP — Web Security Testing Guide, v4.2 — https://owasp.org/www-project-web-security-testing-guide/; https://github.com/OWASP/wstg/blob/v4.2/document/2-Introduction/README.md
- [188] OWASP — OWASP Top 10:2025, A09:2025 Security Logging & Alerting Failures — https://github.com/OWASP/Top10/blob/3a31f35346c3f4e90f350395124382fa53af2afe/2025/docs/en/A09_2025-Security_Logging_and_Alerting_Failures.md
- [189] OWASP Foundation — OWASP Top 10 Client-Side Security Risks (Incubator project) — https://owasp.org/www-project-top-10-client-side-security-risks/
- [190] OWASP Cheat Sheet Series — React Security Cheat Sheet (draft) — https://github.com/OWASP/CheatSheetSeries/blob/995524d4a18e64672c80c8e13869d29ef850bd43/cheatsheets_draft/React_Security_Cheat_Sheet.md
