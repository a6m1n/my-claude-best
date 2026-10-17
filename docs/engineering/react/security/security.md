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

The rules stand on six terms. The cookie, CORS and CSRF rules use the first four, which are MDN's
and the Fetch standard's; the last two are this file's own:

- An origin is a URL's scheme, host and port, such as `https://app.example.com`; two URLs that
  differ in any of the three are two origins. CORS works by origin.
- A site is a URL's scheme and registrable domain, such as `https://example.com`, so
  `https://app.example.com` and `https://api.example.com` are two origins of one site. `SameSite`
  cookies and the `same-site` value of Fetch Metadata work by site.
- A top-level navigation loads a new page into the whole window, as a link, a form or a change of
  `location` does; a `fetch`, an image and a frame are not top-level navigations.
- A preflight is the `OPTIONS` request a browser sends before a cross-origin request whose method
  or headers are outside the CORS safelist, to ask the server whether it allows that request.
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
  Browser".
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
  the client. The server checks every request again: who the user is, whether they may touch that
  record, and the shape of the data. A check in a form helps the user fill it in; it protects
  nothing.
- **Stop a script that already runs on the page from acting as the user.** RFC 10017, section 8:
  "Since the attacker's code becomes indistinguishable from the legitimate application's code, the
  attacker will always be able to request tokens from the provider in exactly the same way as the
  legitimate application code." The rules here limit what such a script takes away; only
  preventing the injection stops it.
- **Protect a user whose machine is infected.** RFC 10017, section 8.6: "More and more malware is
  specifically created to crawl users' machines and look for browser profiles to obtain
  high-value tokens and session cookies, resulting in account-takeover attacks." An `HttpOnly`
  cookie stops a script on the page, not malware on the disk. OWASP's Cookie Theft Mitigation
  cheat sheet lists what a server can add, such as comparing request signals with those seen at
  login, and Device Bound Session Credentials, which tie a session cookie to a key in the machine's
  hardware in Chrome on Windows since 2026 (Google, read 2026-10-15); this practice treats them as
  extras a BFF may add, not rules.

## 3. XSS: what JSX escapes, and the sinks it does not

React escapes every string it renders as text, so `{invoice.customerName}` shows `<script>` as
characters on the screen, and a value it sets on a named prop cannot break out of that prop
(De Ryck, 2020). That covers most of a screen. It does not decide whether the value is safe for
what the prop does, and it does not reach the places where a string becomes HTML, a URL, a set of
props, a style or code. OWASP's XSS cheat sheet asks you to know where your framework stops
protecting you, and names React's gaps: HTML set without sanitising, and URL values, since React 19
blocks only `javascript:` URLs (read 2026-10-16).

| Sink | Why escaping does not reach it | The rule |
|---|---|---|
| `dangerouslySetInnerHTML` | the string is parsed as HTML; React's docs warn that markup from a source that is not fully trusted makes XSS easy | one component writes HTML into the page and sanitises at the sink (section 4) |
| a URL from data in `href` or `src` | React 19 refuses a `javascript:` URL in `href` and `src` and nothing else; `data:` and other schemes pass, and the refusal is new in React 19, listed there as a breaking change | parse the URL and allow a short list of schemes |
| an object from outside spread as props | the object chooses the props, `dangerouslySetInnerHTML` and `href` among them | pass each prop by name, from a value you checked |
| a Markdown renderer | escapes HTML and checks URLs by default; unsafe once its URL check is overridden or raw HTML is turned on | keep the renderer's defaults; raw HTML only through its sanitiser plugin |
| MDX | it compiles to code, and code from outside runs | MDX only from people who may change the application's code |
| JSON written into a `<script>` tag on the server | a `</script>` inside a value ends the tag | let the framework serialise; otherwise escape `<` |
| a user value inside runtime CSS-in-JS | the libraries insert the value into the stylesheet without escaping it | map the user's choice to a fixed value in code, or set it through the `style` prop |
| `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` through a ref | React is not involved, so nothing escapes | set `textContent`, or build nodes with `createElement` |
| `eval`, `new Function`, a string passed to `setTimeout` or `setInterval` | the text runs as code | never; parse data with `JSON.parse` |

OWASP's XSS cheat sheet also names the places untrusted data never goes, whatever the encoding:
inside a `<script>` element, a `<style>` element and an HTML comment.

- **When a URL comes from data, parse it with `URL` and allow only the schemes the link needs,**
  such as `https:` and `mailto:`. React 19's guard covers `javascript:` in `href` and `src` only
  (its upgrade guide, read 2026-10-01), so a `data:` URL and every other scheme pass it; that is
  why this practice checks the scheme itself. An allowlist also stops a scheme nobody planned for;
  a check for `javascript:` stops one scheme. Philippe De Ryck (2020) recommends an allowlist over
  a blocklist, and react-markdown's default list (`http`, `https`, `irc`, `ircs`, `mailto`, `xmpp`
  and relative URLs) is a maintainer's reference set. A relative path the application builds
  itself needs no check.
  Section 15 shows the BAD link and the GOOD one.
- **When data from outside the application describes an element, pass each prop by name from a
  checked value; never spread the object onto the element.** A spread object sets every prop it
  holds, so a response that carries a `dangerouslySetInnerHTML` key puts HTML on the page with no
  sink in sight (De Ryck, 2020). How props are passed in general is
  [components.md](../components/components.md) section 3. Section 15 shows the pair.
- **When you render Markdown from outside, keep the renderer's defaults.** react-markdown escapes
  HTML and checks URLs unless told otherwise. A 2026 advisory describes an application that passed
  `urlTransform={(url) => url}` and got stored XSS with no `dangerouslySetInnerHTML` anywhere.
  The source for the raw-HTML row is react-markdown's README.
- **Treat MDX from outside as code.** It compiles to JavaScript. A 2026 advisory in
  next-mdx-remote let untrusted MDX run code on the server; its version 6 blocks JavaScript
  expressions by default.
- **When the server writes state into a `<script>` tag, let the framework serialise it, or escape
  every `<` as `\u003c`.** Redux's server-rendering docs and Next.js's JSON-LD guide both show
  `.replace(/</g, '\\u003c')` after `JSON.stringify`, and `serialize-javascript` escapes the same
  characters. A plain `JSON.stringify` does not, so a customer name that holds `</script>` ends the
  script and starts HTML. Serialising helpers and framework script components have had advisories
  of exactly this kind (serialize-javascript in 2024, a Next.js script component in 2026).
- **Never put a user's value into a CSS-in-JS template.** styled-components and Emotion insert the
  value into a stylesheet without escaping it. This rests on one practitioner article and a
  styled-components issue; the maintainers' docs were not read (2026-10-01).
- **When code reaches the DOM through a ref, set `textContent` or build nodes; never assign
  HTML.** OWASP's DOM-based XSS cheat sheet lists `innerHTML`, `outerHTML`, `document.write`, and
  `setTimeout`, `setInterval` or `Function` called with a string as dangerous sinks, and asks for
  the safe ones instead.
- **Never run text as code.** The source is OWASP's DOM-based XSS cheat sheet. The lint rules that
  catch these are off by default (section 14).

## 4. Sanitising HTML, and Trusted Types

Prefer no HTML at all: OWASP's DOM-based XSS cheat sheet asks for `textContent` and DOM methods
before any HTML sink. When outside data must carry formatting, Markdown with the renderer's
defaults is the safer form (section 3). When it must be HTML:

- **Write HTML into the page from one component, and render text everywhere else.** The
  component takes the HTML string as its only prop, sanitises it, and is the one place that sets
  `dangerouslySetInnerHTML`. De Ryck (2020) advises wrapping the sanitiser in reusable components;
  one component gives one place to review and one lint suppression to find.
  Check: `react/no-danger` is on (section 14), and `grep -rn "react/no-danger" src/` prints one
  line: the suppression in that component.
- **Sanitise right at the sink, in the same render, with DOMPurify.** A string cleaned earlier can
  be joined with another string, or changed, on its way to the page. DOMPurify's 2026 advisory on
  a bypass through parsing again asks you to keep the context stable from the sanitiser to the
  sink.
- **Never change, join or parse again what the sanitiser returned.** DOMPurify's README warns that
  changing sanitised HTML can undo the sanitising, and MDN says that HTML serialised and parsed
  again with `innerHTML` is no longer sanitised.
- **Start from a profile, such as `USE_PROFILES: { html: true }`, and widen the allowed tags only
  for a need you can name.** A profile allows plain HTML and leaves SVG and MathML out.
  DOMPurify's 2026 releases fixed bypasses that worked only when risky tags were allowed.
- **Update DOMPurify with your routine updates, never skip it.** Its 2026 releases fixed, among
  others, a bypass of the default call through a prototype-pollution bug anywhere on the page, and
  DOM clobbering. A sanitiser is code with advisories like any other.
- **On the server, run DOMPurify with the newest jsdom, never with happy-dom.** DOMPurify's README
  says older jsdom releases have known XSS bugs and does not consider happy-dom safe.
- **Do not move to the HTML Sanitizer API yet.** `Element.setHTML()` is not Baseline: MDN says it
  does not work in some of the most used browsers (read 2026-10-01). When it is, it removes
  scripts, frames and event handlers without a library; re-check it.

Trusted Types moves the check into the browser. With the policy directive
`require-trusted-types-for 'script'`, the browser throws when a plain string reaches an HTML sink
such as `innerHTML`; only a value that a named policy created passes, and the `trusted-types`
directive lists the allowed policy names (MDN, web.dev). Trusted Types is Baseline since February
2026 (MDN, read 2026-10-01). React passes a `TrustedHTML` value given as `__html` to the browser
as it is (React's docs).

- **Once the policy of section 5 is enforced, add Trusted Types in report-only mode, fix what the
  reports show, then enforce it.** web.dev gives this order. No measured study of how many
  libraries break under Trusted Types was found (2026-10-01): the report-only phase is where you
  learn it for your own dependencies.
- **Make the policy sanitise.** A policy that returns its input unchanged turns the check off.
  MDN's example policy calls `DOMPurify.sanitize` in `createHTML`, DOMPurify can return a
  `TrustedHTML` value itself (`RETURN_TRUSTED_TYPE: true`), and React's docs say the policy must
  still make sure its input is trusted and sanitised.

## 5. Content-Security-Policy and the other headers

A Content-Security-Policy (CSP) tells the browser which scripts, styles, connections and frames
the page may use. It does not prevent an injection; it limits what an injected script can do when
one gets through. Most deployed policies give that limit up: the 2025 Web Almanac (HTTP Archive
crawl) found a CSP on 21.9% of sites, and 92% of those policies allow `'unsafe-inline'`, which
lets an injected inline script run. A 2016 Google study found bypasses in 94.72% of all distinct
policies, and 75.81% of distinct policies used script allowlists an attacker could get around.

### The policy for a static single-page application

- **Send `script-src 'self'` with no `'unsafe-inline'` and no `'unsafe-eval'`, together with
  `object-src 'none'`, `base-uri` and `frame-ancestors`.** A plain Vite production build writes no
  inline script: Vite bundles inline module scripts and its preload polyfill into files (Vite's
  HTML plugin source, read on its main branch 2026-10-01). The reference application's built
  `index.html` shows it: one module script with `src`, two preload links, one stylesheet link.
  web.dev's strict CSP uses hashes on static pages to allow chosen inline scripts; a build with
  no inline script has nothing to hash, and `'self'` allows its files. The full policy is in
  [security-example.md](security-example.md), and the BAD form follows below.
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
  content from a domain on the Public Suffix List. The same article calls a
  `Content-Security-Policy: sandbox` header on the file's response the simplest option, and likely
  enough when Spectre-class and renderer-compromise attacks are outside the threat model, so a team
  whose threat model leaves those attacks out may send that header instead, and a team whose threat
  model includes them uses the separate site.
- **Serve an inactive file that users upload, such as an image or a download, from the API's
  origin under the response headers of
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  3, for the page to show as the blob rule of section 7 says,** since the same article allows
  inactive content without a sandbox domain when its response carries safe headers.
- **Allow `data:` in `img-src` only, never in `script-src`.** Vite inlines small assets as `data:`
  URIs; its docs say to allow `data:` where those assets load, or set
  `build.assetsInlineLimit: 0`, and never to allow `data:` for scripts.
- **Do not use a nonce on a static host.** A nonce must change with every response, and a static
  file is the same for every request. Vite's `html.cspNonce` writes a placeholder that a server
  replaces on each request; Vite's docs give no hash recipe, so a static host uses `'self'`
  (read 2026-10-01). A fixed nonce in a static file is the reuse failure of the next subsection.

Bad: `'unsafe-inline'` in `script-src`. This is the reference policy with that one word added.

```text
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self'; img-src 'self' data:; connect-src 'self' https://api.example.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'
```

An injected `<script>` element or an `onerror=` attribute now runs, which is the attack the
policy is there to stop. Next.js's CSP guide shows this form as its example without nonces;
web.dev's strict CSP leaves it out.

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
  per-response value:

  ```text
  Content-Security-Policy: script-src 'nonce-{RANDOM}' 'strict-dynamic'; object-src 'none'; base-uri 'none';
  ```

- **Create the nonce per response and never cache a response that carries one.** A study of the
  top 50,000 sites found 598 of 2,271 nonce-based sites reusing one nonce across responses, often
  because a cache stored the HTML (2023). A reused nonce is a value an attacker can read and copy.
- **Add the nonce to the tags your server renders, never through a step that stamps every script
  tag in the output.** OWASP: such a step stamps the attacker's injected tags too.
- **Keep outside data out of nonced scripts.** A nonce does not help when the injection is into
  the body or the `src` of a nonced script itself (web.dev).
- **Know what `'strict-dynamic'` trusts: every script that a nonced script loads.** A nonced tag
  manager therefore runs every tag added in its own console, and Next.js's docs show that setup.
  Treat that console as a way to deploy code (section 12).
- **Next.js: use its nonce setup and accept dynamic rendering, or its experimental SRI hashes for
  static pages; never its example without nonces.** Its nonce setup needs dynamic rendering, which
  turns off static generation and CDN caching for those pages. Its experimental SRI hashes keep a
  page static but cannot cover scripts generated at run time. Its example without nonces uses
  `'unsafe-inline'`, the BAD form above (Next.js CSP guide, read 2026-10-01).
- **Vite behind a server: set `html.cspNonce` and have the server replace the placeholder with a
  fresh value on each request,** as Vite's docs ask. The same option writes a
  `<meta property="csp-nonce">` tag, which some CSS-in-JS libraries read (next subsection).

### style-src

- **Ship styles as files built at build time, and send `style-src 'self'`.** A stylesheet built
  into a file needs nothing inline; the reference application's build has one stylesheet link and
  no inline style.
- **React's `style` prop is not blocked.** By MDN's `style-src` page, a property set through an
  element's `style` object is allowed, while a `style` attribute in HTML, `setAttribute("style", …)`
  and `style.cssText` are blocked. React's own source was not read on how it sets the prop; this is
  MDN's rule applied to React, and it holds for client rendering only. Server-rendered HTML that
  carries `style="…"` needs a nonce, a hash or `'unsafe-inline'` in `style-src`.
- **Give runtime CSS-in-JS that inserts `<style>` tags the per-response nonce.** Emotion takes it
  as the `nonce` option of `createCache`; styled-components 6.4 and later read it from the
  `<meta property="csp-nonce">` tag that Vite writes when `html.cspNonce` is set (owners' docs,
  read 2026-10-01). A static host has no nonce to give, so such a library there needs
  `'unsafe-inline'` in `style-src`: prefer CSS built into files.

### Rolling it out and delivering it

- **Send a new policy as `Content-Security-Policy-Report-Only` first, read the reports, then
  enforce it.** MDN's CSP guide and web.dev both start this way: a report-only policy blocks
  nothing, and its reports show what the enforced one would block. Collect reports with
  `report-to` and the `Reporting-Endpoints` header, and add `report-uri` for older browsers
  (OWASP). Before the first report-only deploy, name the receiver of the reports, such as a hosted
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
  that way.
- **Set the headers in your host's file.** Netlify and Cloudflare Pages read a `_headers` file
  from the folder they publish; Vercel reads the `headers` array in `vercel.json` (vendors' docs,
  read 2026-10-01). Vite copies `public/_headers` into `dist/` as it is. Netlify's sample policy in
  its docs carries `'unsafe-inline'`: copy the format, not the policy.
- **After every deploy that changes a header, check the deployed result** with the scanners of
  section 14.

### The other headers

The values are OWASP's HTTP Headers cheat sheet's unless the row says otherwise.

| Header | Value | What it stops | In the example |
|---|---|---|---|
| `Content-Security-Policy` | the policy above | injected script loading or running; the page being framed by another site (`frame-ancestors 'none'`) | yes |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | a later visit going over plain HTTP, where the traffic can be read and changed | yes, without `preload`, which asks browsers to build the domain into their HTTPS-only list |
| `X-Content-Type-Options` | `nosniff` | the browser guessing a file's type and running it as script | yes |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | the path and query string, which can hold sensitive values, going to other sites (MDN; it is also the browsers' default) | yes |
| `Permissions-Policy` | `geolocation=(), camera=(), microphone=()`, plus any other feature the application does not use | a script or a frame using a device feature the application never needs | yes, plus `payment=()` |
| `Cross-Origin-Opener-Policy` | `same-origin` | a window this page opened, or that opened it, keeping a handle to it | yes |
| `X-Frame-Options` | `DENY` | framing, in old browsers that lack `frame-ancestors`; a browser that sees both obeys `frame-ancestors` (OWASP's Clickjacking cheat sheet) | no |
| `Cross-Origin-Resource-Policy` | `same-site` | another site loading this site's files into its own pages | no |
| `Cross-Origin-Embedder-Policy` | `require-corp` | part of cross-origin isolation; it blocks every file from another origin that does not opt in, so test it on its own before you send it | no |
| `X-XSS-Protection` | `0` | turns off the XSS filter old browsers had, which OWASP advises against relying on | no |
| `Cache-Control` | `no-store`, on the responses section 13 names | a shared cache keeping one user's data for the next user (OWASP's Session Management cheat sheet) | the API's responses, not this file |

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
XSS exists. The storage choice still decides what the attacker takes away: a stolen token works
from the attacker's own machine until it expires, while a session cookie that script cannot read
works only through the user's open browser. RFC 10017, which De Ryck co-wrote, ranks the patterns
by that exposure, and this practice follows the RFC. Sender-constrained tokens narrow that gap for
a browser-only client, since a token bound to a key the script cannot export cannot be used on
another machine (RFC 10017 section 9.2), but the BFF still wins: no defence in the browser stops
the attacker's script from running a new flow to obtain tokens (RFC 10017 section 6.3.4.2).

RFC 10017 (BCP 212, August 2026) gives three patterns, "presented in decreasing order of
security" (section 6):

| Pattern | Who holds the tokens | What the RFC says |
|---|---|---|
| Backend for Frontend (BFF), section 6.1 | the backend, as a confidential OAuth client; the browser holds only an `HttpOnly` session cookie | "This architecture is strongly recommended for business applications, sensitive applications, and applications that handle personal data." The same section names the cost: "The architecture of a BFF is significantly more complicated than a browser-only application. It requires deploying and operating a server-side BFF component." (6.1.4.3) |
| Token-mediating backend, section 6.2 | the backend gets the tokens and hands the access token to the browser | its security properties "lie somewhere between using a BFF and running" a browser-only application |
| Browser-based OAuth client, section 6.3 | the browser, as a public client | last in the order; all four attack scenarios of section 5.1 apply to it |

- **Choose the BFF for a business application, a sensitive one, or one that handles personal
  data,** since that is the RFC's recommendation, and a billing screen is all three.
- **Page: with a BFF, read, store and send no token,** so no token exists in JavaScript to steal:
  the page sends requests with `credentials: "include"`, and the browser adds the cookie (section
  7). Section 15 shows the BAD and the GOOD.
- **Page: treat the route guard as the user's convenience, never as access control,** since access
  control stays on the server (section 2 of this file). Where the route guard and the sign-out
  handler live is [architecture.md](../architecture/architecture.md) section 10.
- **Know what a BFF does not stop.** A script on the page can still send requests to the BFF
  through the user's session: the RFC's fourth scenario, "Proxying Requests via the User's
  Browser". And a cookie session brings CSRF back (Auth0, 2026), so section 7 is part of the same
  choice.
- **Browser-only client: if you choose one for a lower-risk application, use the authorization
  code flow with PKCE, never the implicit grant** (RFC 9700; oauth.net), so no access token travels
  in a redirect URL, where it can leak and be replayed.
- **BFF or browser-only client: use a maintained library or the provider's SDK for the OAuth
  flow, never your own code** (OWASP's Authentication cheat sheet), so the flow's checks come from
  code that others review and keep patched. The library runs the protocol: the authorization
  request, `state`, the nonce, PKCE, the token exchange and the ID token checks. The step-up's
  binding and the bookkeeping of its login cookie, below, are the team's own code around it.
- **Browser-only client: set the SDK's token storage option explicitly.** Vendors' defaults
  differ: Auth0's SPA SDK keeps tokens in memory, MSAL.js in `sessionStorage`, Okta's auth-js in
  `localStorage` (vendors' docs read through search summaries, 2026-10-01; re-check them).

What RFC 10017 section 8 says about each place a token can be kept:

| Where | RFC 10017, verbatim | Section |
|---|---|---|
| a cookie set by the BFF, `HttpOnly` | the RFC keeps it apart from cookies set by script: "this practice is different from the use of cookies in a BFF (discussed in Section 6.1.3.2), where the cookie is inaccessible to JavaScript and is intended to be sent to the backend." | 8.1 |
| a cookie written from JavaScript | "Because of these unintentional side effects of using cookies for JavaScript-based storage, this practice is NOT RECOMMENDED." | 8.1 |
| a Service Worker | "A Service Worker [W3C.service-workers] offers a fully isolated environment to keep track of tokens. These tokens are inaccessible to the client application, effectively protecting them against exfiltration." But "the use of a Service Worker does not prevent an attacker from obtaining a new set of tokens", and "the Service Worker MUST NOT store tokens in any persistent storage API that is shared with the main window". | 8.2 |
| a Web Worker | "The security properties of using a Web Worker are identical to using Service Workers. When tokens are exposed to the application, they become vulnerable." When the worker keeps the refresh token and hands the access token to the page, "the application's own refresh token is effectively protected against exfiltration, but the access token is not." | 8.3 |
| memory | "Another option is keeping tokens in memory without using any persistent storage. Doing so limits the exposure of the tokens to the current execution context only but has the downside of not being able to persist tokens between page loads." A closure that hides them does not hold: "Using prototype poisoning, an attacker can substitute these functions with malicious versions". | 8.4 |
| `localStorage` | "localStorage does not protect against unauthorized access from malicious JavaScript, as the attacker would be running code within the same origin, and as such, would be able to read the contents of the localStorage." | 8.5 |
| `sessionStorage` | it "is not shared between multiple tabs open to pages on the same origin, which slightly reduces the exposure of the tokens in sessionStorage." | 8.5 |
| any of the above | "Note that the main difference between these patterns is the exposure of the data, but none of these options can fully mitigate token exfiltration when the attacker can execute malicious code in the application's execution environment." | 8.5 |
| the browser's files on disk | "there is no guarantee that browser storage is encrypted at rest" | 8.6 |

- **Page: never keep a token, a session id or any other credential in `localStorage` or
  `sessionStorage`.** OWASP's Session Management cheat sheet says the same, and RFC 10017 section
  8.5 gives the reason.
  Check: in review, `grep -rnE "(local|session)Storage" src/` shows no token, session id or key.
- **Page: never write a token into a cookie from JavaScript** (RFC 10017 section 8.1).
- **Page: when the page sets a cookie of its own, such as a theme or a locale, name it with the
  `__Host-` prefix, write `Secure`, `Path=/` and a `SameSite` value that fits its purpose, and leave
  out `Domain`,** so the cookie goes over HTTPS only, follows one site rule in every browser, and
  no sibling subdomain can overwrite it (ASVS 5.0 requirements 3.3.1 to 3.3.3). A cookie that must
  be shared with other hosts takes the `__Secure-` prefix instead, as requirement 3.3.1 asks.
- **Browser-only client: keep the tokens in memory or in a worker, and accept the limit both
  share:** the attacker's script can still ask the provider for new tokens (RFC 10017 sections 8.2
  to 8.4).
- **Browser-only client: where the provider supports DPoP (RFC 9449), bind the tokens to a
  non-exportable key made with the Web Crypto API,** so a token that a script copies out cannot be
  used without the key (RFC 10017 section 9.2). It does not stop a script that runs a new flow
  (RFC 10017 section 6.3.4.2).
- **Browser-only client: before it takes refresh tokens, confirm that the provider meets RFC 10017
  section 6.3.2.3.** The RFC first says that authorization servers "may choose whether or not to
  issue refresh tokens to browser-based applications". If they do, they "MUST either rotate refresh
  tokens on each use OR use sender-constrained refresh tokens as described in Section 4.14.2 of
  [RFC9700]"; "MUST either set a maximum lifetime on refresh tokens OR expire if the refresh token
  has not been used within some amount of time"; and "MUST NOT, upon issuing a rotated refresh
  token, extend the lifetime of the new refresh token beyond the lifetime of the initial refresh
  token if the refresh token has a preestablished expiration time". Rotation does not make
  `localStorage` safe: De Ryck (2021) concludes that sensitive single-page applications should
  use a BFF rather than rely on rotation in the browser.

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
6. Step-up: on `403 reauth_required`, **the page sends the user to re-authenticate**.
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
  the clock as a click does. In TanStack Query that means no `refetchInterval` on data that needs
  the session, unless the BFF leaves those requests out of its idle clock. Polling is off by
  default, and a hidden tab polls only with `refetchIntervalInBackground` set (TanStack Query docs,
  read 2026-10-15). OWASP states the definition, not this rule; the rule is this practice's
  reading of it.
- **Page: run the sign-out path on the first `401` the API answers:** clear what the session
  loaded and send the user to sign in, so the screen shows no data from a session the server has
  ended. What the sign-out handler does is [architecture.md](../architecture/architecture.md)
  section 10. The rule is this practice's choice.
- **Page: on a `401` that answers a request sent before a sign-in or a step-up renewed the session,
  ask the session check once, and run the sign-out path only when it also answers `401`,** since
  that request carried the session id the renewal destroyed, while the session may be live under
  its new id; this is an exception to the `401` rule above, and the rule is this practice's
  choice.
- **Page: where the query client is made, tell it not to retry a `401`,** since `useQuery` retries
  a failed query three times by default in the browser (TanStack Query docs, read 2026-10-16). The
  query client is made as [architecture.md](../architecture/architecture.md) section 8 says. The
  rule is this practice's choice.
- **Page: on a `502` or a `503`, the session check's included, and on a `403` whose body carries
  no code, never run the sign-out path, and show the error as for any failed request
  ([architecture.md](../architecture/architecture.md) sections 9 and 12), and for the logout
  endpoint as the rule in "Logout" below on any other failure says,** since these answers say that
  the server or a check failed, not that the session ended; the rule is this practice's choice.

### Logout

- **Page: show a sign-out control on every screen that needs the session** (ASVS 5.0 requirement
  7.4.4; OWASP's Session Management cheat sheet), so a user on a shared device can always end it.
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
  redirect the user's browser to the provider's logout endpoint. The URL comes from the answer, so
  it is data, as the step-up's `authorizationUrl` is ("Re-authentication" below). When the check
  refuses the URL, run the sign-out path without the navigation, since the BFF has already ended
  the local session; the rule is this practice's choice.

### Re-authentication

- **Page: on a `403`, check its body for the code `reauth_required` before the `401` rule,** so
  the user re-authenticates, by the path of the login type that the next rules give, instead of
  seeing a plain refusal; the rule is this practice's choice.
- **Page, with an identity provider: on a `403` whose body carries `reauth_required`, check the
  authorization URL in the `authorizationUrl` field of the `403`'s body by section 3's rule for a
  URL that comes from data, and open it by a top-level navigation,** since the provider's sign-in
  page is another site; the user comes back on the step-up's outcome route (the rule on that route
  below). The rule is this practice's choice.
- **Page, with an identity provider: when that `403`'s body has no `authorizationUrl` field, or
  section 3's check refuses it, show the error as for any failed request
  ([architecture.md](../architecture/architecture.md) sections 9 and 12) and do not navigate,** so
  the user sees that the change did not go through; the rule is this practice's choice.
- **Page: with a first-party login, on a `403` whose body carries `reauth_required`, show the
  re-authentication prompt and send the guarded request again with the answer, and on a `403`
  whose body carries `reauth_failed`, show the prompt again,** so the change the BFF guards can go
  through; leave a `401` to the sign-out path. The rule is this practice's choice.
- **Page, with an identity provider: on the step-up's outcome route, show the outcome its code
  names and read the changed data again,** since the navigation to the provider unloaded the page
  that sent the change; the rule is this practice's choice.

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
  every request; MDN on which headers start a preflight). The reference API client is in section 15
  and in [security-example.md](security-example.md).
- **When the API is on another origin of the site, send every request that needs the session with
  `credentials: "include"`, from the one API client,** so the browser adds the session cookie: the
  default, `same-origin`, sends no cookie to another origin (MDN). On the page's own origin the
  default already sends it.
- **Page: when the API answers with a status that is not `2xx`, have the API client throw an error
  that carries the response's status and, when the body parses as JSON, its fixed code and the
  body's `authorizationUrl` when it has one; a body that does not parse, such as a gateway's HTML
  page, gives no code and no URL,** so the `Page:` rules that read a status and a code, such as
  `cookie_conflict` and `reauth_required` (section 6), can read both, and the step-up with an
  identity provider can read the URL it opens (section 6, "Re-authentication"); the rule is this
  practice's choice.
- **Load an API resource that the page shows without `fetch`, such as an image or a PDF preview,
  through the API client, and show it from a `URL.createObjectURL` URL,** because an `<img>` and a
  frame cannot send the custom header (MDN, read 2026-10-16).
- **Build that blob with a type the code sets, never with the response's own type:
  `application/pdf` for a frame, and `image/png`, `image/jpeg`, `image/webp` or `image/gif` for an
  `<img>`, never `image/svg+xml`,** so a file from outside never becomes an HTML or SVG document in
  the page's origin. For a PDF that is
  `new Blob([await response.arrayBuffer()], { type: "application/pdf" })`. The guard is this
  practice's choice, after the URL Standard, which gives a blob URL the origin of the page that
  created it.
- **Add `blob:` to `img-src` in the page's policy for these images, and to `frame-src` only for
  the PDF preview,** since a blob in a frame is a document in the page's origin; the rule is this
  practice's choice.
- **Never loosen `object-src` for the PDF preview; where the frame shows nothing, offer the file
  through the download link instead, whose answer carries `Content-Disposition: attachment`,** since
  `object-src 'none'` belongs to the strict policy of section 5, and a blank preview is no reason
  to give it up; the rule is this practice's choice.
- **Read an event stream with `fetch` through the API client, not with `EventSource`,** because
  `EventSource` cannot send the custom header and takes `withCredentials` as its only option (MDN,
  read 2026-10-16).
- **Send the CSRF token the server issues, where it uses one, in a header of each state-changing
  request,** since the server checks it on each of them, the login included, which needs a token
  of its own, issued before the session exists (OWASP).
- **When the API is on another origin of the site, read the CSRF token from a JSON response
  through the API client, never from a cookie with a `Domain` attribute,** since the page cannot
  read the API's own cookie, and a cookie with `Domain` goes to every subdomain, any of which can
  overwrite it with a token of its own (OWASP's CSRF cheat sheet).
- **Encode every value you put into an API path with `encodeURIComponent`.** A value such as
  `../../account/delete` turns the application's own request into a request to another endpoint,
  with the cookie, the custom header and any CSRF token attached: client-side path traversal gets
  past every defence in OWASP's list in
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  3 (Doyensec, 2024; CVE-2023-45316 in Mattermost). The query and mutation options in
  [layout-example.md](../architecture/layout-example.md) encode the route's `invoiceId` this way.

Encoding stops the slash, but it leaves `.` and `..` as they are, and the URL parser then resolves
them: `` `/invoices/${encodeURIComponent("..")}/payments` `` requests `/payments` (checked with
Node 20's URL parser, 2026-10-15).

- **Check the format of any value that does not come from the route's own path, against its
  schema, before you build the path,** such as the format of an invoice id (OWASP's CSRF cheat
  sheet, client-side CSRF). A path parameter the router reads from the page's own URL has lost its
  literal `.` and `..` segments, but not a `%2F` inside one, which the server's path rule in
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  3 rejects; a value from a search parameter, a message, storage or a response has not lost them.
- **Put no token in the WebSocket URL's query string,** where logs keep it (OWASP's WebSocket
  Security cheat sheet; section 13).
- **When the page opens a WebSocket, add the socket's `wss://` origin, such as
  `wss://api.example.com`, to `connect-src` in the page's policy (section 5),** since a source
  written with `https://` does not match a `wss://` URL, so the reference policy would block the
  socket (CSP Level 3, "scheme-part matching", read 2026-10-16).
- **Page: when the server closes a WebSocket with its session-ended code, run the sign-out path,**
  since that code is the server's word that the session ended (the WebSocket rules in
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  3, "What the server does"); the rule is this practice's choice.
- **Page: when a WebSocket closes with any other code, reconnect with a bounded backoff, and before
  each reconnect ask the API through the API client whether the session is still live,** since a
  handshake the server refuses reaches the page only as a close with code 1006, the code for a
  connection closed with no close frame, so the `401` rule of section 6 cannot fire for a socket
  (MDN's `CloseEvent.code` page; the WHATWG WebSockets Standard). The rule is this practice's
  choice.

The API's CORS rules are in
[backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
section 3, "CORS".

### Fixing a CORS error

- **The page never sets `mode: "no-cors"`:** the answer comes back opaque, with status 0 and a
  body no script can read (MDN; the Fetch standard).
- **The page never sends an `Access-Control-Allow-*` header:** it is a response header, and on a
  request it is one more header outside the safelist, which starts a preflight (the Fetch
  standard).
- **The page never sends requests through a public CORS proxy:** the proxy reads every request and
  answer, tokens and keys included. No leak through such a proxy is documented; the risk is the
  design, so the rule is this practice's choice.
- **Page: when development calls a real API on another origin instead of MSW handlers
  ([libraries.md](../architecture/libraries.md) section 6), send the API calls through Vite's
  `server.proxy`, under a path prefix that no page route uses,** so the page's calls reach the API
  as `same-origin` (Vite's docs), and the proxy never catches a navigation to one of the page's
  own routes. What the development instance accepts is the rule on the one setting of allowed
  origins, in
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  3, "What the server does". The dev server's own rules are section 11.

## 8. Server-side React

This section holds when a framework renders React on the server or runs Server Functions:
Next.js, React Router in framework mode, and others. A client-only application has none of these
endpoints; React's December 2025 advisory lists client-only React as not affected. An application
that uses Server Components is exposed even when it defines no Server Function of its own
(the same advisory).

- **Treat every Server Function as a public HTTP endpoint.** Anyone can send it a POST directly,
  not only through your UI, and a check on the page that shows the form does not cover it (Next.js
  data security guide). Inside each one: parse the arguments with a schema, since TypeScript types
  do not exist at run time; check who the user is and that they may touch this record; return
  only the fields the client needs.
- **Read data through a data access layer that runs only on the server.** Next.js's guide
  describes it: it runs only on the server, checks authorisation, and returns small objects with
  only the fields the caller needs; `import "server-only"` at its top makes a client import fail
  at build time. The layer lives on the server, in the framework's server-only code.
- **Never authorise in middleware or a proxy alone; check again in the data access layer and in
  each Server Function.** CVE-2025-29927 (CVSS 9.1) let one spoofed header skip Next.js middleware,
  and Vercel's post-mortem advises against middleware as the only protection of a route; the May
  2026 Next.js release fixed four more middleware and proxy bypasses.
- **Do not treat closure encryption or taint as a boundary.** Next.js encrypts the values a Server
  Action closes over and advises against relying on that alone; arguments passed with `.bind()`
  are not encrypted. React's taint APIs are experimental, and a clone or a spread copy of a
  tainted object is not tainted.
- **Write no secret into server code; read it from the server's environment at run time.**
  CVE-2025-55183 exposed Server Function source, and with it every secret written in that source;
  values read from the environment stayed hidden (Next.js, December 2025).
- **Patch a critical advisory for React's server packages, your framework or your router within
  the day, through the cooldown's emergency path (section 10).** React2Shell (CVE-2025-55182,
  CVSS 10.0) let anyone run code on the server without logging in. Groups exploited it within
  hours of disclosure (AWS) and took cloud and API credentials (Microsoft). Nothing in application
  code stopped it: Next.js wrote that there was no workaround, only the upgrade. Google called its
  WAF rule a temporary measure until the patch lands, and React told users not to depend on their
  host's mitigations. Turn on Dependabot or Renovate security updates, which skip their cooldowns
  (section 10).
  Check: when you set up the repository, see that the person or channel that receives security
  advisories and alerts is in the decision log
  ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
  section 3, the first rule under "Logging"), so the advisories of React, the framework and the
  router reach them on the day they are published.
- **Read the advisory again in the days after you patch.** After React2Shell, follow-up
  advisories for denial of service and source exposure moved the patched version more than once,
  so the first fix was not the last. Write the advisory id in your notes, never a version number
  as "the safe version".
- **After a flaw that ran code on the server, treat the server's credentials as stolen.** Rotate
  every cloud, database and API key the server could reach, and keep that set small (Microsoft's
  React2Shell guidance).
- **Patch the framework's XSS advisories as fast as any other critical one.** React Router's
  framework mode had three XSS advisories in server rendering in 2025 and 2026: `ld+json` in
  `meta()`, `ScrollRestoration` keys, and redirects from loaders and actions.

## 9. Secrets and public settings

- **Treat every `VITE_` value and every `NEXT_PUBLIC_` value as public.** Vite writes them into
  the bundle at build time, and its docs say they must not hold sensitive data such as API keys;
  Next.js inlines `NEXT_PUBLIC_` values at build time the same way. A secret lives on the server,
  and the server makes the call that needs it. Section 15 shows the BAD and the GOOD.
  Check: before you add a `VITE_` or `NEXT_PUBLIC_` variable, ask whether you would print its value
  on the login page. If not, it is a secret.
- **List the public settings in one schema, so a secret has no place to land.** Where the
  settings file sits and how the application reads it is
  [architecture.md](../architecture/architecture.md) section 3.
- **Keep files with real values out of git.** Vite's docs say `*.local` env files stay out of
  git, and the Next.js template ignores `.env*`; commit an example file with every name and no
  real value ([file-structure.md](../../any-language/file-structure/file-structure.md) section 9).
- **Publish no source maps from a production build.** Vite's `build.sourcemap` is off by default,
  and `'hidden'` writes maps without the comment that points to them, for upload to an error
  tracker; Next.js keeps browser source maps off by default (read 2026-10-01). A published map
  hands out the original source with its comments. A 2026 study of 10 million rendered sites found
  1,748 live credentials in front ends, 62% of them only in compiled bundles.
- **Restrict at the provider any key that must ship to the browser.** A maps key gets a website
  restriction and an API restriction (Google Maps Platform). A "public" database key, such as a
  Supabase anon key, is safe only behind server-side rules such as row-level security: one
  researcher's scan found 170 of 1,645 apps exposing their tables to anyone holding that key,
  because those rules were off (CVE-2025-48757).
- **Scan for secrets before they leave the machine and after the build.** Turn on GitHub secret
  scanning and repository-level push protection, which is off by default (GitHub's docs, read
  2026-10-01), and run a scanner such as gitleaks as a pre-commit hook. Run it over the build
  output too: the study above found most front-end credentials only in the compiled bundle.
  Gitleaks takes security fixes only, and its maintainer is moving to Betterleaks (read
  2026-10-01); re-check before you adopt it.
- **When a secret leaks, revoke it at the provider first.** GitHub's guide calls revocation the
  most important step: deleting the secret from the code, pushing a new commit or recreating the
  repository does not stop its use.

## 10. Supply chain: packages, lockfile, CI

A package you install runs with your rights in two places: on the developer's machine and in CI,
when it is installed or built; and in your users' browsers, once it is bundled. The incidents of
2025 and 2026 each found a different gap:

| Incident | How it got in | What it teaches |
|---|---|---|
| Shai-Hulud, September 2025 | phished maintainer credentials; an install script stole npm and GitHub tokens and published infected versions of the victims' other packages; GitHub removed more than 500 packages | block dependency install scripts |
| chalk and debug, September 2025 | a phished maintainer; the payload had no install hook and ran in end users' browsers once bundled; Vercel found 76 projects built with it | blocking install scripts does not stop a payload that runs in the bundle |
| Nx, August 2025 | a `pull_request_target` workflow with write rights, and a pull request title run as part of a script | CI is an entry point |
| axios, March 2026 | the maintainer's npm credentials; a malicious dependency that dropped remote-access malware; the versions were pulled after about 3 hours; CISA advised `ignore-scripts=true` and `min-release-age=7` | a cooldown would have skipped it |
| TanStack, May 2026 | a `pull_request_target` workflow that ran fork code, a poisoned Actions cache, and an OIDC token read from runner memory; the versions carried valid provenance; Snyk wrote that a seven-day cooldown would have fully protected against it | provenance says where a package was built, not that its code is safe |
| AsyncAPI, July 2026 | the payload ran when the package was imported, so `--ignore-scripts` did not stop it; the versions carried valid provenance (Microsoft) | no single control is enough |

A cooldown also misses what it cannot see: a git dependency names a commit, not a registry
version, and an account taken over for weeks outlasts any wait (a 2026 practitioner analysis).
Socket found destructive packages aimed at React, Vue and Vite projects that went unnoticed for
about two years.

The controls, per package manager (owners' docs, read 2026-10-01; "not read" means the page read
for this table did not cover it):

| Control | npm 12 | pnpm 11 and later |
|---|---|---|
| dependency install scripts | blocked unless `allowScripts` in the root `package.json` approves them; `strict-allow-scripts=true` turns the warning into a failed install. npm 11 still runs them: set `ignore-scripts=true` there | blocked; `strictDepBuilds` (default `true`) fails the install on an unreviewed build script; reviewed packages go in `allowBuilds`, which replaced `onlyBuiltDependencies` in pnpm 11; never `dangerouslyAllowAllBuilds` |
| release cooldown | `min-release-age` in days, off by default in npm 12 as well (the setting exists since npm 11.10.0, 2026-02-11; npm 10 has none); `min-release-age-exclude` (since 11.17.0) exempts packages; `npm ci` ignores the setting, since it installs the lockfile as written | `minimumReleaseAge` in minutes, default 1440 (one day) since pnpm 11; `minimumReleaseAgeExclude` exempts packages |
| git and tarball sources | `allow-git` and `allow-remote` default to `none` | `blockExoticSubdeps` (default `true`): only direct dependencies may come from git or a tarball URL |
| provenance | `npm audit signatures` checks registry signatures and provenance attestations | `trustPolicy: no-downgrade` fails when a version's trust level is lower than that of earlier versions |
| install exactly the lockfile | `npm ci` fails when the lockfile and `package.json` disagree, and writes neither | commit `pnpm-lock.yaml` (pnpm's supply-chain page) |
| fix a transitive dependency | `overrides` in the root `package.json` | `overrides` in `pnpm-workspace.yaml` |

Yarn and Bun have controls of the same kind under other names; they were not compared here.

Update bots: Renovate's `minimumReleaseAge` does not apply to vulnerability fixes, and its
`security:minimumReleaseAgeNpm` preset waits 3 days; Dependabot's `cooldown` applies to version
updates only, never to security updates (read 2026-10-01).

- **Turn on the install-script block and a release cooldown in the repository's own config file,
  so every install obeys them:** a person's, CI's and an agent's. A setting on one laptop protects
  one laptop. The settings for npm 12, npm 11.10 or later, and pnpm are in
  [security-example.md](security-example.md).
- **Set the cooldown to at least one day.** One day covered the short-lived hijacks above; CISA
  advised seven after the axios compromise. A longer wait delays every normal update by as much;
  that is the trade.
  `min-release-age` exists since npm 11.10.0 (2026-02-11); npm 10 has neither it nor
  `min-release-age-exclude`. On npm before 11.10.0, `--before=<date>` on the install command
  installs only versions that were available on or before that date (npm's config page, read
  2026-10-02). It takes a fixed date that the person running the install has to choose each time,
  where `min-release-age` is a rolling window set once in the repository. The reference
  application was installed this way (npm 10.8, `--before=2026-09-24`); it is a command flag, not
  repository config.
- **Write the emergency path next to the cooldown.** A one-day pnpm cooldown blocked the
  React2Shell patch the day after disclosure, and the developer got it through with
  `minimumReleaseAgeExclude` (a practitioner's account, 2025). The path names the setting that
  exempts one package, who may add an entry, and that the entry comes out once the version is
  older than the cooldown. npm has `min-release-age-exclude` since 11.17.0; an older npm has no
  per-package exemption.
  Check: when you set a cooldown, ask: if a critical fix ships today, which line do we change? If
  no line next to the setting answers, the path is missing.
- **Allow a dependency's build script only after someone has read it,** by adding that package to
  `allowBuilds` or `allowScripts`. The script runs with your rights when the package is installed,
  which is how Shai-Hulud stole npm and GitHub tokens.
- **Treat provenance as one layer, never as proof.** pnpm recommends `trustPolicy: no-downgrade`
  and npm checks attestations with `npm audit signatures`, yet the TanStack and AsyncAPI versions
  carried valid ones.
- **Have every security advisory of your dependencies reach you on the day it is published:**
  turn on the host's dependency alerts for the repository, such as Dependabot alerts on GitHub,
  and watch the advisory sources section 18 lists for React's server packages, the framework, the
  router, Vite and DOMPurify. Where a BFF holds the session, turn on dependency alerts in the BFF's
  own repository too, for its server framework, its session and cookie library and its OAuth or
  OpenID Connect client library. A critical fix can then go in through the emergency path on the
  day it ships, not at the next dated re-check or CI run.

Before an AI coding agent installs a package:

- **It checks on the registry that the package exists, that the name is the one the library's own
  docs give, and how old the version is; a name it cannot find in those docs is not installed.**
  Models invent package names. A 2025 USENIX study of 16 models found that at least 5.2% of the
  packages commercial models suggested, and 21.7% of those open-source models suggested, did not
  exist; a 2026 preprint found 4.6% to 6.1% on five frontier models, which all invented the same
  127 names, 53 of them still free to register. An attacker who registers such a name gets
  installed by the next agent that invents it.
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
  install that would change it fails.
- **Review a lockfile change in a pull request like code.** A pull request can point a `resolved`
  URL and its integrity hash at another tarball, and `npm ci` installs it; `lockfile-lint` checks
  that every package comes from the hosts you allow.
- **Judge an audit by what the application reaches.** `npm audit` reports issues in code an
  application never runs; Dan Abramov called it broken by design (2021), and alerts nobody reads
  train people to skip the real one. Fix what is reachable. When the fix exists only in a
  transitive dependency, pin it with `overrides`. OSV-Scanner reads npm, pnpm and Yarn lockfiles
  against the OSV database, as a second opinion.

CI (GitHub Actions; the rules are GitHub's own, from its secure-use reference):

- **Pin every third-party action to its full commit SHA.** GitHub's docs call it the only way to
  use an action as an immutable release; Dependabot keeps the pinned versions current.
  Check: `grep -rhn "uses:" .github/workflows/ | grep -vE "@[0-9a-f]{40}|uses: \./"` prints
  nothing.
- **Set the default `GITHUB_TOKEN` permission to read the repository contents, and raise it per
  job only where a job needs more.** A workflow that runs an attacker's input, as the Nx one did,
  then holds a token that cannot write.
- **Never check out pull request code from a fork in a `pull_request_target` workflow.** The
  TanStack attack used such a workflow to run fork code.
- **Pass pull request fields to a script through an environment variable, never through `${{ }}`
  inside the script.** The Nx attack ran a pull request title as part of a script.
- **Share no cache between workflows that run fork code and workflows that publish** (TanStack's
  post-mortem).

## 11. The dev server

The Vite dev server serves your source tree. Between February 2025 and June 2026 Vite published
thirteen advisories against it: twelve let a request read files outside the `server.fs` limits, and
one let any website the developer visited send requests to the dev server and read the source,
through CORS and the WebSocket (Vite's advisories, read 2026-10-01). Each was closed only by an
upgrade.

- **Keep Vite current on every machine that runs the dev server.** The rules below shrink who can
  reach it; only the patch closes a bug.
- **Keep `server.host` at its default, `localhost`.** `--host` or `host: true` listens on every
  address, the local network and public ones included. Use it only on a network you trust, and
  only while you need it.
- **Never set `server.allowedHosts: true`; list only domains you control.** Vite's docs warn that
  `true` opens the dev server to DNS rebinding, which lets any site download your source. The BAD
  and the GOOD follow this list.
- **Never set `server.cors: true`; list the origins you need.** The default allows only
  localhost; `true` lets any website send requests and read the answers (Vite's docs).
- **Keep `server.fs.strict` on (the default), and widen `server.fs.allow` only to folders you mean
  to serve.** `server.fs.deny` blocks `.env` files and key files by default, but it does not cover
  the `public/` folder, so nothing secret goes there; the build also copies `public/` as it is.
- **Do not set `rewriteWsOrigin` in `server.proxy`.** Vite does not check the origin of a
  WebSocket request before it proxies it, so the target must, and this option removes that check
  (Vite's docs).
- **Apply the same rules to `vite preview`.** The preview server takes `host`, `allowedHosts`,
  `cors` and `proxy` from `server` unless `preview` sets its own.

Bad: the host check turned off, to reach the dev server through a tunnel for a test on a phone.

```ts
server: {
  allowedHosts: true,
},
```

Any site can now reach the dev server through DNS rebinding and download the source.

Good: the same tunnel, with only its own domain allowed. This line is written from Vite's docs;
the reference application sets no `server` block, so the defaults hold there.

```ts
server: {
  // Only the tunnel's domain: `true` would let any site reach this server through DNS rebinding
  // (security.md section 11).
  allowedHosts: ["billing-dev.tunnel.example.com"],
},
```

It fixes the one problem: the tunnel works, and the server answers no other host name. A leading
`.` would allow every subdomain too; list the one name you need.

## 12. Third-party scripts, postMessage, iframes, redirects

Third-party scripts:

- **Prefer a data layer to a vendor's script on the page:** your own code collects the events and
  sends the vendor only the fields you chose, so the vendor gets nothing else. A data layer limits
  what is collected; it is not a sandbox, since a tag manager's tags still run as code in the page
  (OWASP's Third Party JavaScript Management cheat sheet, read 2026-10-16).
- **Load a fixed version of a script from another origin with Subresource Integrity:** the
  `integrity` attribute and `crossorigin="anonymous"`. SRI stops a changed file from running. It
  cannot tell an attack from a vendor's update, so it fits only a file that never changes at its
  URL, and it covers scripts and stylesheet and preload links only (MDN).
- **Keep analytics, session replay and any other script that listens to keystrokes off the login
  and payment screens.** A 2025 crawl of the top million sites found keystroke listeners from
  third parties on 38.52% of them, and at least 3.18% of sites sent what users typed to a third
  party.
- **Give a tag manager's console the access rules of a deploy.** Under `'strict-dynamic'`, a
  nonced tag manager runs every tag added there (section 5). The trust is the sources'; the access
  rule is the practice's choice.

postMessage:

- **Add a `message` listener only when the page expects messages from another window** (MDN),
  since any window can send the page a message and the listener is where it gets in.
- **In the listener, compare `event.origin` with the one exact origin you expect, then check the
  message's shape before you use it.** Never check `event.source` instead, and never accept a whole
  domain with a wildcard. Microsoft's security team found both mistakes, and messages sent to
  `"*"`, across its own products in 2025 (MSRC).
- **Send with the exact target origin, never `"*"`.** With `"*"`, the message goes to whatever page
  is in the target window at that moment (OWASP's HTML5 Security cheat sheet; MDN).

iframes, redirects and service workers:

- **Load content you do not control in an `<iframe>` with `sandbox`, and never give it
  `allow-scripts` together with `allow-same-origin`.** With both, a same-origin document can remove
  its own sandbox (MDN).
- **Redirect after login only to a target from an allowlist, or to one the server maps from a
  short id.** A `?next=` value used as it is sends the user to any site from a link that shows your
  domain (OWASP's Unvalidated Redirects cheat sheet).
- **Register a service worker only from your own origin and over HTTPS** (OWASP's HTML5 Security
  cheat sheet), since the worker sits between the page and the network for every request in its
  scope.
- **Cache no response that carries personal data in a service worker** (the same cheat sheet),
  since that cache stays on the device until code deletes it, and any script on the origin can
  read it.
- No rule is spent on `rel="noopener"`: browsers already treat `target="_blank"` as `noopener`
  (MDN, read 2026-10-01).

## 13. Data the browser exposes

- **Put no token, password or API key in a URL; send it in a header or a request body.** A URL
  lands in server logs and browser history, and goes to other sites in the `Referer` header
  (OWASP's REST Security cheat sheet; MDN).
- **Send no credential, session id, token or payment data to a client log, the console or an
  error report.** OWASP's Logging cheat sheet lists what logs should not record, and an error
  report is a log that leaves the user's machine. The same list for server logs is
  [logging.md](../../python/logging/logging.md) section 10.
- **On a screen that failed, show a message of your own, never the error's own message or its
  stack.** A message or a stack can carry what the server answered or how it is built. OWASP's
  Error Handling cheat sheet asks that "a generic response is returned by the application but the
  error details are logged server side for investigation, and not returned to the user".
- **Send the path, not the full URL, to analytics and metrics.** The query string can hold what the
  user typed, and MDN's referrer guide names URL parameters as a common leak of sensitive data.
  The reference application's web-vitals report sends the path of the URL the metric belongs to,
  `metric.navigationURL`, and never the query string ([security-example.md](security-example.md));
  what to measure is [performance.md](../performance/performance.md) section 3.
- **Keep session replay masking on.** Sentry's replay masks all text and all input values by
  default, and its docs say to turn that off only on a site with no sensitive data; PostHog masks
  inputs but not page text by default, so turn on text masking there (vendors' docs, read
  2026-10-01).
- **Give credential fields their `autocomplete` token: `username`, `current-password`,
  `new-password`, `one-time-code`.** `autocomplete="off"` is no control: password managers may fill
  the field anyway, and browsers may ignore it on login fields (MDN). How a form behaves in general
  is [ux.md](../design/ux.md) section 4.
- **Never block paste in the username, password or one-time-code fields.** OWASP's
  Authentication cheat sheet and the UK's NCSC both ask services to allow it, so people can use
  password managers.
- **Send `Cache-Control: no-store` on any response that carries personal data or a session id,
  HTML included** (OWASP), so no shared cache keeps one user's data for the next one.

## 14. Automation: lint rules and header scanners

The lint rules that catch the sinks of section 3 are mostly off in the default presets (read
2026-10-01):

| Sink | ESLint | Oxlint |
|---|---|---|
| `eval`, `new Function`, timers given a string | core `no-eval`, `no-implied-eval`, `no-new-func`, none of them in `eslint:recommended`; typescript-eslint's `no-implied-eval` uses types and is in `recommended-type-checked` | `no-eval`, `no-implied-eval`, `no-new-func` |
| a `javascript:` URL written in the code | core `no-script-url`, not in `eslint:recommended`; eslint-plugin-react's `jsx-no-script-url`, not in its recommended set; @eslint-react's `dom-no-script-url` | `no-script-url` |
| `dangerouslySetInnerHTML` | eslint-plugin-react's `no-danger`, not in its recommended set; @eslint-react's `dom-no-dangerously-set-innerhtml` | `react/no-danger` |
| `innerHTML`, `insertAdjacentHTML`, `document.write` | `eslint-plugin-no-unsanitized`, its `property` and `method` rules | not read |
| an unsafe `iframe` sandbox | @eslint-react's `dom-no-unsafe-iframe-sandbox` | not read |

Biome has rules of the same kind; they were not compared here.

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
  checks the headers and settings the deployed site actually sends.
- **Run the supply-chain and secret checks in CI:** `npm audit signatures`, OSV-Scanner and the
  secret scanner (sections 9 and 10).

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
to its own server, and use it from there until it expires.

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
defence (section 7).

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
the browser's developer tools and use it with the provider. No type check and no lint rule
reports it.

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
the policy sanitise"); this was type-checked, not run in a browser. It does not stop a DOMPurify
bypass found later: keep the library current.

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
so a `data:` URL passes, and versions before React 19 do not refuse `javascript:` either.
`no-script-url` does not report this line: it sees a `javascript:` string written in the code,
not a value that arrives as data.

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
nothing in this file shows a sink (De Ryck, 2020).

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
  without forbidding them. Choose one knowingly, with section 6's storage rules.
- **A client-only application has no Server Functions;** section 8 applies once a framework
  renders on the server.
- **A script an attacker already runs on the page** acts as the user under every rule here. The
  rules limit what it takes away; only preventing the injection stops it (section 2).
- **Malware on the user's machine** reads cookies and storage from the browser's files, outside
  the page's reach (RFC 10017 section 8.6). Section 2 names what a server can add.
- **A screen left open after the server's timeout, or open in another tab after logout,** keeps
  showing data until its next request (OWASP's Session Management cheat sheet).
- **A call from a public page to the user's local network or `localhost`** passes a permission
  prompt in Chrome since version 142, not a CORS check (Chrome's developer blog, read 2026-10-15).
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
same ground. Each red flag is a way in, so one red flag is enough to stop the merge until it is
fixed or the author shows why it does not apply; that bar is the practice's choice.

| Section | Ask | Red flag |
|---|---|---|
| 2. What the browser can protect | Does the server check this request on its own? | a permission enforced only by hiding a button or a route |
| 3. XSS | Can a value from outside reach HTML, a URL, a props object, a style or code? | a URL from data with no scheme allowlist; outside data spread as props; a renderer's `urlTransform` overridden |
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
the OWASP Foundation. OWASP calls it an awareness document for developers and web application
security, one that "represents a broad consensus about the most critical security risks to web
applications". The current edition is the 2025 one, the eighth (OWASP's Impact Report 2025,
read 2026-10-17); 2021 and 2017 came before it.
Read it at [top10.owasp.org/2025](https://top10.owasp.org/2025/), where each category has its own
page with its weaknesses, attack scenarios and prevention steps; the source text is in the
OWASP/Top10 repository on GitHub (both read 2026-10-16).

Each category groups many weaknesses, each one an entry in CWE, the Common Weakness Enumeration:
the ten categories of 2025 hold 248 CWEs. OWASP builds the list from two inputs. Testing data on
over 2.8 million applications ranks the categories by how many applications show the weakness and
by the exploit and impact scores of the known vulnerabilities behind it; eight categories come
from that data. A survey of practitioners picks the other two, because a new kind of weakness
reaches testing tools, and so the data, only years after it appears.

Work with it this way:

- **In a review, check against the checklist above; use the Top 10 only to name a finding's
  category.** OWASP calls it "primarily an awareness document", and as a coding or testing
  standard "the bare minimum and just a starting point". Some of its
  risks, such as A06 Insecure Design, are "beyond the scope of most forms of testing", and OWASP
  discourages any claim of full coverage because it is "simply untrue". A team that checks only the
  ten categories believes it is done. The table below says which section of this file covers each
  2025 category. The checklist above holds the red flags of the highest-risk acts; a review also
  reads the rules of every section the change touches.
- **When the project starts, pick its
  [ASVS](https://owasp.org/www-project-application-security-verification-standard/) level and
  write it into the decision log ("Write it down" in
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section
  2 says where),** so reviews and tests know the target; writing it down is this practice's choice.
  OWASP's Application Security Verification Standard (ASVS 5.0, read 2026-10-16) has three levels:
  Level 1 holds "the minimum requirements to consider when securing an application", Level 2 is the
  level "most applications should be striving to achieve", and Level 3 is for applications that must
  show the highest level of security.
- **When you write a feature's security requirements, take them from ASVS at the chosen level,**
  since ASVS is the standard the Top 10 sends teams to, because each requirement in it can be
  verified and tested. Chapters V3 Web Frontend Security and V7 Session Management are the parts
  closest to this file.
- **When you design a feature that touches authentication, access control, business logic or a key
  flow, model its threats first, with OWASP's
  [Threat Modeling cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html),**
  since OWASP's guide to an application security program puts threat modelling in the planning
  and design phase, and A06 Insecure Design asks for it for critical parts of the application,
  such as authentication, access control, business logic and key flows.
- **When you build a feature, first read what the
  [OWASP Top 10 Proactive Controls](https://top10proactive.owasp.org/) and the
  [Cheat Sheet Series](https://cheatsheetseries.owasp.org/) say about what it handles,** such as a
  session, input or output, since OWASP's guide to an application security program names them as
  "a good starting point" for designing security in. The Proactive Controls (2024 edition, read
  2026-10-16) are the techniques OWASP writes for developers, and the Cheat Sheet Series gives one
  topic at a time in depth; this file cites both throughout.
- **Before a release that changes authentication, access control, business logic or a key flow,
  test the application against the
  [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/),
  or give it to whoever runs the security test,** so the test follows OWASP's own method and does
  not stop at the ten categories. The WSTG (stable version 4.2, read 2026-10-16) is OWASP's
  testing guide for web applications, for a penetration test or a security review; the moment is
  this practice's choice.
- **When OWASP publishes a new edition, the team that adopted this practice maps its categories to
  this file again,** since categories move and merge between editions (server-side request forgery
  joined A01 in 2025); the rule is this practice's choice.

### The OWASP Top 10:2025, mapped to this file

The table says where each category meets a React application and which section here covers it.
Where a category is mostly the server's, the middle column says so, and the browser side's part
is named.

| Category | What it means for a React application | Sections |
|---|---|---|
| A01 Broken Access Control | the server decides every access; the page hides what the user cannot use, for the user's sake. OWASP counts CSRF, CORS mistakes and server-side request forgery here | 2, 7, 8; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) sections 2, 3 |
| A02 Security Misconfiguration | headers, cookie attributes, the CORS policy and the dev server are configuration | 5, 6, 7, 11; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) sections 2, 3 |
| A03 Software Supply Chain Failures | the packages you install, the lockfile and the CI workflow | 10 |
| A04 Cryptographic Failures | mostly the server's: HTTPS, HSTS and no caching of responses with personal data; the browser side keeps secrets out of the bundle; password storage for a first-party login is outside this practice ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 4) | 5, 9, 13 |
| A05 Injection | XSS is injection into the page; the server checks the format of each path segment and of each report ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 3); injection into the server's own interpreters, such as SQL or an OS command, is outside this practice | 3, 4, 5, 7; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 3 |
| A06 Insecure Design | a check in the page helps the user and protects nothing; the design puts every control on the server, and the session in a BFF; OWASP asks to model the threats of critical flows such as sign-in and access control (the threat-modelling step above) | 2, 6 |
| A07 Authentication Failures | mostly the server's: the OAuth flow, a new session id at login, timeouts, logout and re-authentication; the browser side holds no token and runs the sign-out path on a `401`; a first-party login's password storage, throttling and sign-in error messages are outside this practice ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 4) | 6; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2 |
| A08 Software or Data Integrity Failures | scripts from other origins, Subresource Integrity, and state the server writes into the page; an object from outside spread as props (section 3); the session's state in a signed and encrypted cookie ([backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2); the arguments of a Server Function (section 8) | 3, 6, 8, 10, 12; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2 |
| A09 Security Logging and Alerting Failures | mostly the server's: it logs security events, and alerts a person when the rejections of one check pass their written rate and on every step-up from another account; the browser side keeps credentials out of its own reports | 6, 7, 13; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) sections 2, 3 |
| A10 Mishandling of Exceptional Conditions | mostly the server's: it fails closed; the browser side shows a message of its own on a failed screen, never the error's text | 6, 13; [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2 |

Two more OWASP sources sound like they belong here, and neither is mapped (both read 2026-10-15).
The "Top 10 Client-Side Security Risks" is an Incubator project whose list is still the 2022
candidate. The OWASP React Security cheat sheet sits in the drafts folder of the cheat sheet
repository and is not published on the cheat sheet site.

## 18. Sources

Each source is the place to look for the rule it backs. The table says how each was read and when;
the file quotes word for word only the sources it marks as quoted.

| Sources | How they were read | Quoted word for word | Read on |
|---|---|---|---|
| 1 (RFC 10017) and 85 (OWASP's Error Handling cheat sheet) | as raw text | yes | 2026-10-01; 85 on 2026-10-02 |
| 125 to 127 | as raw text | yes | 2026-10-16 |
| the parts of source 36 that [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 3 quotes (the case for tokens and the `Origin` fallback) | as raw text | yes | 2026-10-16 |
| 134 to 136 | as raw text | no | 2026-10-16 |
| 112 to 117, 120 to 123, 128 and 129 | as raw text | no | 2026-10-16 |
| 130 to 132; the pages at the URLs of sources 103, 105 and 106; the parts of sources 93, 97 and 100 that [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 2 cites for login cookies, the `$Version` header and logout | as raw text | no | 2026-10-16 |
| 9, 76 and 133; the parts of sources 6, 82, 100, 106 and 115 that sections 6 and 7, and [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) sections 2 and 3, cite for the page's cookies, log fields, the logout redirect, the callback's error page and the WebSocket close codes | as raw text | no | 2026-10-16 |
| 91 to 107, apart from the parts above | through a summarising tool | no | 2026-10-15; the pages at the URLs of 96 and 107 on 2026-10-16 |
| 108 to 111, 118, 119 and 124 | through a summarising tool | no | 2026-10-16 |
| 137 to 140 | through a summarising tool | no | 2026-10-16 |
| 141 and 142; the part of source 100 that [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) section 3 cites for a logout request sent again (2.5) | as raw text | no | 2026-10-16 |
| 143 | as raw text | yes | 2026-10-16 |
| 144 and 145; the parts of sources 35 and 93 that [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md) sections 2 and 4 cite for local development and a cookie with an empty name | as raw text | no | 2026-10-16 |
| 146 and 147 | as raw text | no | 2026-10-16 |
| 148 and 149 | as raw text | no | 2026-10-16 |
| 150 | as raw text, extracted from the PDF | no | 2026-10-17 |
| every other source | through a summarising tool | no | 2026-10-01, unless its entry gives a date |

Standards and access control

1. RFC 10017, "OAuth 2.0 for Browser-Based Applications", BCP 212, August 2026 (A. Parecki,
   P. De Ryck, D. Waite): https://www.rfc-editor.org/rfc/rfc10017.txt — the attack scenarios
   (5.1), the three patterns and their order (6), `SameSite` and other applications on the same
   site (6.1.3.3.1), the BFF recommendation and its cost (6.1.4.3), refresh tokens (6.3.2.3),
   token storage (8.1 to 8.6).
2. RFC 9700, OAuth 2.0 Security Best Current Practice, January 2025:
   https://datatracker.ietf.org/doc/html/rfc9700 — PKCE for public clients, no implicit grant.
3. oauth.net, Browser-Based Apps: https://oauth.net/2/browser-based-apps/ — authorization code
   with PKCE, the BFF.
4. OWASP Top 10:2025, A01 Broken Access Control:
   https://top10.owasp.org/2025/A01_2025-Broken_Access_Control — access control only in trusted
   server-side code.
5. OWASP Authorization cheat sheet:
   https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html — never rely on
   client-side checks.
6. OWASP ASVS 5.0, chapter V3 Web Frontend Security:
   https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x12-V3-Web-Frontend-Security.md — the long
   checklist; cookie attributes and prefixes (3.3.1 to 3.3.3).

XSS and sanitising

7. React, common components (`dangerouslySetInnerHTML`, `TrustedHTML`):
   https://react.dev/reference/react-dom/components/common
8. React 19 upgrade guide, the `javascript:` URL change:
   https://react.dev/blog/2024/04/25/react-19-upgrade-guide
9. OWASP Cross Site Scripting Prevention cheat sheet:
   https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
   — React's gaps, places untrusted data never goes.
10. OWASP DOM based XSS Prevention cheat sheet:
    https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html —
    dangerous and safe sinks, `JSON.parse` over `eval`.
11. Philippe De Ryck, a two-part article on XSS in React (2020):
    https://pragmaticwebsecurity.com/articles/spasecurity/react-xss-part1.html and
    https://pragmaticwebsecurity.com/articles/spasecurity/react-xss-part2.html — scheme
    allowlists, props spread from user data, reusable sanitising components.
12. React's PR on `javascript:` URL sinks: https://github.com/react/react/pull/29808
13. react-markdown README: https://github.com/remarkjs/react-markdown — the default URL
    allowlist, `rehype-raw` and `rehype-sanitize`.
14. Advisory GHSA-fpw4-p57j-hqmq (an overridden `urlTransform`, 2026):
    https://github.com/advisories/GHSA-fpw4-p57j-hqmq
15. HCSEC-2026-01, code execution through untrusted MDX in next-mdx-remote:
    https://discuss.hashicorp.com/t/hcsec-2026-01-arbitrary-code-execution-in-react-server-side-rendering-of-untrusted-mdx-content/77155
16. Redux, server rendering: https://redux.js.org/usage/server-rendering; Next.js JSON-LD guide:
    https://nextjs.org/docs/app/guides/json-ld; serialize-javascript:
    https://github.com/yahoo/serialize-javascript — escaping `<` in serialised state.
17. CVE-2024-11831 (serialize-javascript): https://www.cvedetails.com/cve/CVE-2024-11831/; Netlify
    changelog of 2026-05-08 on React and Next.js advisories:
    https://www.netlify.com/changelog/2026-05-08-react-nextjs-security-vulnerabilities/
18. Frontarm, CSS-in-JS and security (search summary only):
    https://frontarm.com/james-k-nelson/how-can-i-use-css-in-js-securely/
19. DOMPurify README and releases: https://github.com/cure53/DOMPurify and
    https://github.com/cure53/DOMPurify/releases; advisories GHSA-h8r8-wccr-v5f2 and
    GHSA-v9jr-rg53-9pgp: https://github.com/advisories/GHSA-h8r8-wccr-v5f2,
    https://github.com/advisories/GHSA-v9jr-rg53-9pgp
20. MDN, HTML Sanitizer API and `Element.setHTML()`:
    https://developer.mozilla.org/en-US/docs/Web/API/HTML_Sanitizer_API,
    https://developer.mozilla.org/en-US/docs/Web/API/Element/setHTML
21. MDN, Trusted Types API: https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API;
    web.dev, Trusted Types: https://web.dev/articles/trusted-types; web-features, newly available:
    https://web-platform-dx.github.io/web-features-explorer/newly-available/

Content-Security-Policy and headers

22. web.dev, strict CSP: https://web.dev/articles/strict-csp — nonce and hash forms, what a nonce
    does not protect.
23. OWASP Content Security Policy cheat sheet:
    https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html — the
    strict policies, no nonce-stamping step, reporting.
24. MDN, CSP guides: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP and
    https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/CSP —
    report-only first, what a `<meta>` policy cannot do.
25. MDN, `style-src` and `frame-ancestors`:
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/style-src,
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors
26. Vite, features (CSP section) and shared options (`html.cspNonce`):
    https://raw.githubusercontent.com/vitejs/vite/main/docs/guide/features.md,
    https://raw.githubusercontent.com/vitejs/vite/main/docs/config/shared-options.md; Vite's HTML
    plugin source:
    https://raw.githubusercontent.com/vitejs/vite/main/packages/vite/src/node/plugins/html.ts
27. Next.js, Content Security Policy guide (docs 16.3.8):
    https://nextjs.org/docs/app/guides/content-security-policy
28. Web Almanac 2025, Security chapter: https://almanac.httparchive.org/en/2025/security — CSP
    adoption and `'unsafe-inline'`.
29. Nonce reuse in the wild (2023): https://arxiv.org/abs/2309.07782
30. Google's CCS 2016 paper on the insecurity of allowlist policies:
    https://research.google/pubs/csp-is-dead-long-live-csp-on-the-insecurity-of-whitelists-and-the-future-of-content-security-policy/;
    Raxis on tag managers and CSP:
    https://raxis.com/blog/bypassing-waf-and-csp-with-google-tag-manager/
31. Emotion `@emotion/cache` README:
    https://raw.githubusercontent.com/emotion-js/emotion/main/packages/cache/README.md;
    styled-components FAQ: https://styled-components.com/docs/faqs — the `nonce` they read.
32. OWASP HTTP Headers cheat sheet:
    https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html; OWASP
    Clickjacking Defense cheat sheet:
    https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html; MDN,
    Referrer policy:
    https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/Referrer_policy
33. Netlify headers: https://docs.netlify.com/manage/routing/headers/; Cloudflare Pages headers:
    https://developers.cloudflare.com/pages/configuration/headers/; Vercel `vercel.json` headers:
    https://vercel.com/docs/project-configuration/vercel-json#headers

Sessions, CSRF and CORS

34. OWASP Session Management cheat sheet:
    https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html — no
    credential in web storage, cookie attributes, `no-store`.
35. MDN, `Set-Cookie`:
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie; Mozilla Hacks,
    SameSite changes (2020): https://hacks.mozilla.org/2020/08/changes-to-samesite-cookie-behavior/
36. OWASP CSRF Prevention cheat sheet:
    https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
    — the order of defences, `SameSite` as defence in depth.
37. Filippo Valsorda, CSRF (2025): https://words.filippo.io/csrf/
38. Squarcina et al., related-domain attackers (USENIX Security 2021):
    https://www.usenix.org/system/files/sec21-squarcina.pdf
39. MDN, CORS: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS; OWASP HTML5
    Security cheat sheet:
    https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html
40. Auth0, what developers get wrong about the BFF pattern (2026):
    https://auth0.com/blog/things-developers-get-wrong-about-the-backend-for-frontend-pattern/
41. De Ryck, localStorage and XSS (2020):
    https://pragmaticwebsecurity.com/articles/oauthoidc/localstorage-xss.html; refresh token
    rotation (2021):
    https://pragmaticwebsecurity.com/articles/oauthoidc/critical-analysis-refresh-token-rotation.html
42. OWASP Authentication cheat sheet:
    https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html — maintained
    libraries, paste allowed.
43. SDK storage defaults (search summaries): Auth0 SPA SDK
    https://auth0.com/docs/libraries/auth0-single-page-app-sdk; MSAL.js caching
    https://learn.microsoft.com/en-us/entra/msal/javascript/browser/caching; Okta refresh tokens
    https://developer.okta.com/docs/guides/refresh-tokens/main/

Server-side React

44. React, the December 2025 Server Components advisories:
    https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components
    and
    https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components
45. Next.js, security update of 2025-12-11: https://nextjs.org/blog/security-update-2025-12-11
46. Next.js, data security guide (docs 16.3.8): https://nextjs.org/docs/app/guides/data-security;
    Next.js blog on Server Components and Actions (2023):
    https://nextjs.org/blog/security-nextjs-server-components-actions
47. React, `experimental_taintObjectReference`:
    https://react.dev/reference/react/experimental_taintObjectReference
48. CVE-2025-29927: https://github.com/advisories/GHSA-f82v-jwr5-mffw; Vercel's post-mortem:
    https://vercel.com/blog/postmortem-on-next-js-middleware-bypass; the May 2026 bypasses, in
    the Netlify changelog of source 17.
49. React2Shell response: AWS
    https://aws.amazon.com/blogs/security/china-nexus-cyber-threat-groups-rapidly-exploit-react2shell-vulnerability-cve-2025-55182;
    Microsoft
    https://www.microsoft.com/en-us/security/blog/2025/12/15/defending-against-the-cve-2025-55182-react2shell-vulnerability-in-react-server-components/;
    Google Cloud
    https://cloud.google.com/blog/topics/threat-intelligence/threat-actors-exploit-react2shell-cve-2025-55182
50. React Router framework-mode advisories: https://github.com/advisories/GHSA-3cgp-3xvw-98x8,
    https://github.com/advisories/GHSA-8v8x-cx79-35w7,
    https://github.com/advisories/GHSA-2w69-qvjg-hvjx

Secrets

51. Vite, env variables and modes: https://vite.dev/guide/env-and-mode; build options:
    https://vite.dev/config/build-options
52. Next.js, environment variables: https://nextjs.org/docs/app/guides/environment-variables
53. Google Maps Platform, API security best practices:
    https://developers.google.com/maps/api-security-best-practices
54. Supabase row-level security audit, CVE-2025-48757 (one researcher's scan):
    https://www.michaelbir.es/case-studies/lovable-supabase-rls-security-audit/
55. Credentials in front-end code at scale (2026 preprint): https://arxiv.org/abs/2603.12498
56. GitHub, push protection and secret scanning:
    https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection,
    https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning;
    remediating a leaked secret:
    https://docs.github.com/en/code-security/tutorials/remediate-leaked-secrets/remediating-a-leaked-secret
57. Gitleaks README: https://raw.githubusercontent.com/gitleaks/gitleaks/master/README.md

Supply chain

58. GitHub, plan for a more secure npm supply chain (Shai-Hulud):
    https://github.blog/security/supply-chain-security/our-plan-for-a-more-secure-npm-supply-chain/;
    Unit 42: https://unit42.paloaltonetworks.com/npm-supply-chain-attack/
59. Vercel, response to the chalk and debug compromise:
    https://vercel.com/blog/critical-npm-supply-chain-attack-response-september-8-2025
60. Nx advisory: https://github.com/nrwl/nx/security/advisories/GHSA-cxm3-wv7p-598c
61. CISA, axios alert:
    https://www.cisa.gov/news-events/alerts/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager;
    Microsoft on axios:
    https://www.microsoft.com/en-us/security/blog/2026/04/01/mitigating-the-axios-npm-supply-chain-compromise/
62. TanStack post-mortem: https://tanstack.com/blog/npm-supply-chain-compromise-postmortem; Snyk:
    https://snyk.io/blog/tanstack-npm-packages-compromised/
63. Microsoft on AsyncAPI:
    https://www.microsoft.com/en-us/security/blog/2026/07/15/unpacking-asyncapi-npm-supply-chain-compromise-import-time-payload-delivery/
64. What cooldowns miss: https://lilting.ch/en/articles/pnpm-11-minimum-release-age-default-shai-hulud-defense;
    Socket's 2025 report:
    https://socket.dev/blog/2025-report-destructive-malware-in-open-source-packages
65. The emergency exemption in practice:
    https://codenote.net/en/posts/pnpm-minimumreleaseageexclude-for-emergency-vulnerability-fixes/;
    a cooldown comparison (2026-05-29):
    https://craigory.dev/blog/2026-05-29/package-manager-release-cooldown/
66. npm 12 changelog and config: https://docs.npmjs.com/cli/v12/using-npm/changelog,
    https://docs.npmjs.com/cli/v12/using-npm/config; npm 11 config and changelog:
    https://docs.npmjs.com/cli/v11/using-npm/config,
    https://docs.npmjs.com/cli/v11/using-npm/changelog/; npm 10 config, the `before` option (read
    2026-10-02): https://docs.npmjs.com/cli/v10/using-npm/config; Socket on npm 12:
    https://socket.dev/blog/npm-12
67. pnpm settings and supply-chain page: https://pnpm.io/settings/dependency-resolution,
    https://pnpm.io/settings/build, https://pnpm.io/supply-chain-security
68. Yarn configuration: https://yarnpkg.com/configuration/yarnrc; Bun `bunfig.toml`:
    https://bun.com/docs/runtime/bunfig and its issue 30525:
    https://github.com/oven-sh/bun/issues/30525
69. Renovate `minimumReleaseAge` and security presets:
    https://docs.renovatebot.com/configuration-options/#minimumreleaseage,
    https://docs.renovatebot.com/presets-security/; Dependabot options:
    https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference
70. Package hallucination: USENIX Security 2025 https://arxiv.org/abs/2406.10279; 2026 preprint
    https://arxiv.org/abs/2605.17062
71. lockfile-lint: https://github.com/lirantal/lockfile-lint; Dan Abramov's post on `npm audit`
    (2021): https://overreacted.io/npm-audit-broken-by-design/
72. npm `audit`, `ci` and `overrides`: https://docs.npmjs.com/cli/v11/commands/npm-audit,
    https://docs.npmjs.com/cli/v11/commands/npm-ci,
    https://docs.npmjs.com/cli/v11/configuring-npm/package-json#overrides; pnpm `overrides`:
    https://pnpm.io/settings/dependency-resolution#overrides; OSV-Scanner:
    https://google.github.io/osv-scanner/
73. GitHub Actions secure use: https://docs.github.com/en/actions/reference/security/secure-use
    — SHA pinning, `GITHUB_TOKEN`, `pull_request_target`, script injection.

The dev server

74. Vite security advisories: https://github.com/vitejs/vite/security/advisories
75. Vite server and preview options:
    https://raw.githubusercontent.com/vitejs/vite/main/docs/config/server-options.md,
    https://raw.githubusercontent.com/vitejs/vite/main/docs/config/preview-options.md

Third-party code and data exposure

76. OWASP Third Party JavaScript Management cheat sheet:
    https://cheatsheetseries.owasp.org/cheatsheets/Third_Party_Javascript_Management_Cheat_Sheet.html
    — a data layer limits what is collected and is not a sandbox.
77. MDN, Subresource Integrity:
    https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Subresource_Integrity
78. Keystroke listeners on the top million sites (2025): https://arxiv.org/abs/2508.19825
79. MDN, `postMessage`: https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage; the
    MSRC blog post on `postMessage` mistakes in Microsoft products (2025):
    https://www.microsoft.com/en-us/msrc/blog/2025/08/postmessaged-and-compromised
80. MDN, `<iframe>` and `noopener`:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe,
    https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel/noopener
81. OWASP Unvalidated Redirects and Forwards cheat sheet:
    https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html
82. OWASP Logging cheat sheet:
    https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html; OWASP REST Security
    cheat sheet: https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
83. Sentry session replay privacy:
    https://docs.sentry.io/platforms/javascript/guides/react/session-replay/privacy/; PostHog
    session replay privacy: https://posthog.com/docs/session-replay/privacy
84. MDN, `autocomplete`:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/autocomplete; NCSC,
    password guidance: https://www.ncsc.gov.uk/collection/passwords/updating-your-approach
85. OWASP Error Handling cheat sheet (read as raw text 2026-10-02):
    https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html — a generic
    response to the user, the details in the server's log.

Automation

86. ESLint's recommended set, raw:
    https://raw.githubusercontent.com/eslint/eslint/main/packages/js/src/configs/eslint-recommended.js
87. eslint-plugin-react README:
    https://github.com/jsx-eslint/eslint-plugin-react/blob/master/README.md; @eslint-react rules:
    https://www.eslint-react.xyz/docs/rules/overview; typescript-eslint `no-implied-eval`:
    https://typescript-eslint.io/rules/no-implied-eval/
88. eslint-plugin-no-unsanitized README:
    https://raw.githubusercontent.com/mozilla/eslint-plugin-no-unsanitized/master/README.md
89. Biome rules: https://biomejs.dev/linter/rules/no-dangerously-set-inner-html/ and its sibling
    pages for `noGlobalEval`
90. CSP Evaluator: https://csp-evaluator.withgoogle.com/; MDN HTTP Observatory:
    https://developer.mozilla.org/en-US/observatory

The OWASP lists

91. OWASP Top 10:2025: https://top10.owasp.org/2025/ — the ten categories, final; the project
    page: https://owasp.org/projects/top-ten
92. OWASP Top 10 Client-Side Security Risks, an Incubator project with a 2022 candidate list:
    https://owasp.org/www-project-top-10-client-side-security-risks/; the React Security cheat
    sheet draft:
    https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets_draft/React_Security_Cheat_Sheet.md

Cookies

93. The IETF layered-cookies draft, which defines `__Http-` and `__Host-Http-`:
    https://datatracker.ietf.org/doc/draft-ietf-httpbis-layered-cookies/; the RFC 6265bis draft,
    still in the RFC Editor's queue — `Domain`, `Path`, lifetime, "Weak Integrity", where
    `SameSite` cookies are stored and sent:
    https://datatracker.ietf.org/doc/draft-ietf-httpbis-rfc6265bis/
94. web-platform-tests, cookie prefixes, stable runs of 2026-10-15:
    https://wpt.fyi/results/cookies/prefix?label=stable; WebKit's expected results for the same
    tests:
    https://github.com/WebKit/WebKit/blob/main/LayoutTests/imported/w3c/web-platform-tests/cookies/prefix/__Host-Http.https-expected.txt
95. MDN, third-party cookies (the `SameSite` default by browser, third-party cookie blocking):
    https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies; MDN's cookie
    guide: https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/Cookies;
    Mozilla bug 1617609 (no `Lax` by default in Firefox):
    https://bugzilla.mozilla.org/show_bug.cgi?id=1617609
96. Microsoft, ASP.NET Core and `SameSite` (the login cookies on a `form_post` callback):
    https://learn.microsoft.com/en-us/aspnet/core/security/samesite; Duende BFF, single frontend
    (`Lax` after a cross-site login, `response_mode=query`):
    https://docs.duendesoftware.com/bff/getting-started/single-frontend/; Duende BFF architecture
    (an API on the page's origin makes cookies same-site and needs no CORS):
    https://docs.duendesoftware.com/bff/architecture/
97. PortSwigger, cookie prefixes bypassed through server parsing (2025):
    https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes

Sessions

98. OWASP Session Management cheat sheet, read again for renewal, timeouts, logout,
    `Clear-Site-Data` and re-authentication:
    https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Session_Management_Cheat_Sheet.md;
    ASVS 5.0, chapter V7 Session Management:
    https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x16-V7-Session-Management.md
99. NIST SP 800-63B-4, timeouts by assurance level: https://pages.nist.gov/800-63-4/sp800-63b/aal
100. RFC 7009, OAuth 2.0 Token Revocation: https://www.rfc-editor.org/rfc/rfc7009; OpenID Connect
     RP-Initiated Logout 1.0 (the redirect to the provider's logout endpoint, section 2; the
     redirect back, section 3; confirmation without `id_token_hint`, section 6): https://openid.net/specs/openid-connect-rpinitiated-1_0.html;
     Back-Channel Logout 1.0 (the way a session ends left to the application, 1; a token without
     `sid`, 2.4; when a logout request is sent again, 2.5; validation, 2.6; a user already logged
     out, 2.7; a failed logout, 2.8):
     https://openid.net/specs/openid-connect-backchannel-1_0.html;
     Front-Channel Logout 1.0: https://openid.net/specs/openid-connect-frontchannel-1_0.html
101. MDN, `Clear-Site-Data`:
     https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Clear-Site-Data; GitLab
     merge request 156213, sign-out without the header:
     https://gitlab.com/gitlab-org/gitlab/-/merge_requests/156213; the W3C `Clear-Site-Data`
     Editor's Draft (cookies cleared for the whole registered domain):
     https://w3c.github.io/webappsec-clear-site-data/
102. OWASP Cookie Theft Mitigation cheat sheet:
     https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Cookie_Theft_Mitigation_Cheat_Sheet.md;
     Google on Device Bound Session Credentials:
     https://blog.google/security/protecting-cookies-with-device-bound-session-credentials/; the
     W3C draft: https://w3c.github.io/webappsec-dbsc; Mozilla's position:
     https://github.com/mozilla/standards-positions/issues/912
103. TanStack Query, important defaults and polling:
     https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults,
     https://tanstack.com/query/latest/docs/framework/react/guides/polling; the retries guide, read
     in its source:
     https://raw.githubusercontent.com/TanStack/query/main/docs/framework/react/guides/query-retries.md

CORS, Fetch Metadata, WebSocket

104. The Fetch standard, the CORS protocol and "CORS protocol and HTTP caches":
     https://fetch.spec.whatwg.org/#http-cors-protocol,
     https://fetch.spec.whatwg.org/#cors-protocol-and-http-caches; MDN on
     `Access-Control-Allow-Origin`, `Access-Control-Max-Age`, CORS errors and `Request.mode`:
     https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Origin,
     https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Max-Age,
     https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS/Errors,
     https://developer.mozilla.org/en-US/docs/Web/API/Request/mode
105. James Kettle, CORS misconfigurations (2016):
     https://portswigger.net/research/exploiting-cors-misconfigurations-for-bitcoins-and-bounties;
     PortSwigger's Web Security Academy on CORS (origins matched by prefix or suffix):
     https://portswigger.net/web-security/cors; Chen et al., an empirical study of CORS (USENIX
     Security 2018): https://www.usenix.org/system/files/conference/usenixsecurity18/sec18-chen.pdf;
     Netty CVE-2026-59903, `Vary` overwritten: https://nvd.nist.gov/vuln/detail/CVE-2026-59903 and
     Netty's advisory GHSA-8c42-7qj2-3j46:
     https://github.com/netty/netty/security/advisories/GHSA-8c42-7qj2-3j46; CVE-2020-36851, an open
     proxy:
     https://osv.dev/vulnerability/CVE-2020-36851
106. The W3C Fetch Metadata draft: https://www.w3.org/TR/fetch-metadata/; MDN, `Sec-Fetch-Site`:
     https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Sec-Fetch-Site; MDN,
     `Sec-Fetch-Dest`:
     https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Sec-Fetch-Dest; OWASP
     WebSocket Security cheat sheet:
     https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/WebSocket_Security_Cheat_Sheet.md;
     RFC 6455, sections 7.4.2 (close codes 4000 to 4999 for private use) and 10.2:
     https://www.rfc-editor.org/rfc/rfc6455; MDN, `CloseEvent.code` (1006 for a connection closed
     with no close frame): https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code; the
     WHATWG WebSockets Standard (a refused handshake closes with 1006, and script cannot tell why):
     https://websockets.spec.whatwg.org/
107. Doyensec, client-side path traversal to CSRF (2024):
     https://blog.doyensec.com/2024/07/02/cspt2csrf.html; CVE-2023-45316 in Mattermost:
     https://nvd.nist.gov/vuln/detail/CVE-2023-45316; Chrome, Local Network Access:
     https://developer.chrome.com/blog/local-network-access
108. nginx, the `location` and `proxy_pass` directives:
     https://nginx.org/en/docs/http/ngx_http_core_module.html#location,
     https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass — matching on the
     decoded and resolved URI, and the normalized URI that `proxy_pass` passes on.

Session state

109. Duende BFF, the back-channel logout endpoint, which depends on server-side sessions in the BFF:
     https://docs.duendesoftware.com/bff/fundamentals/session/management/back-channel-logout/
110. Microsoft, cookie authentication without ASP.NET Core Identity (`ExpireTimeSpan`,
     `SlidingExpiration`, the ticket's issue and expiry times in the encrypted cookie):
     https://learn.microsoft.com/en-us/aspnet/core/security/authentication/cookie
111. RFC 9110, HTTP Semantics, sections 9.3.7 (`OPTIONS`, whose responses are not cacheable),
     15.5.2 (`401 Unauthorized`), 15.5.4 (`403 Forbidden`), 15.6.3 (`502 Bad Gateway`) and 15.6.4
     (`503 Service Unavailable`): https://www.rfc-editor.org/rfc/rfc9110

Credentials, step-up and input validation

112. MDN, `Request.credentials` (`same-origin` is the default):
     https://developer.mozilla.org/en-US/docs/Web/API/Request/credentials
113. RFC 9470, OAuth 2.0 Step Up Authentication Challenge Protocol (a `401` with the error
     `insufficient_user_authentication`): https://www.rfc-editor.org/rfc/rfc9470
114. OWASP Input Validation cheat sheet, "Allowlist vs Denylist":
     https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html

Re-authentication, session state and keys

115. OpenID Connect Core 1.0, `max_age` and `prompt=login` (3.1.2.1), the authentication error
     response (3.1.2.6), the `auth_time` claim and its check (3.1.3.7), `iss` and `sub` as the one
     stable identifier of the user (5.7):
     https://openid.net/specs/openid-connect-core-1_0.html
116. RFC 8414, OAuth 2.0 Authorization Server Metadata, section 2 (`revocation_endpoint`):
     https://www.rfc-editor.org/rfc/rfc8414
117. ASP.NET Core, `RemoteAuthenticationHandler` source (a correlation cookie named per attempt):
     https://github.com/dotnet/aspnetcore/blob/main/src/Security/Authentication/Core/src/RemoteAuthenticationHandler.cs;
     issue 58731, correlation and nonce cookies that pile up until nginx refuses the request:
     https://github.com/dotnet/aspnetcore/issues/58731
118. Microsoft, `RemoteAuthenticationTimeout` (15 minutes by default):
     https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.authentication.remoteauthenticationoptions.remoteauthenticationtimeout
119. Microsoft, ASP.NET Core in a web farm (one key ring for every node) and key management (older
     keys still decrypt, and a deleted key leaves its data unreadable):
     https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/web-farm,
     https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/implementation/key-management

API responses, logging and credentials

120. MDN, `Content-Disposition` (`inline` by default, `attachment` to download):
     https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Disposition
121. MDN, `EventSource()` (`withCredentials` its only option), `URL.createObjectURL()`, and the
     CSP source values (a scheme such as `blob:`):
     https://developer.mozilla.org/en-US/docs/Web/API/EventSource/EventSource,
     https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL_static,
     https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy
122. OWASP Password Storage cheat sheet:
     https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
123. OWASP ASVS 5.0, chapter V16 Security Logging and Error Handling (16.3.3, attempts to get past
     a security control; 16.5.2 and 16.5.3, working securely when a resource fails, with no
     fail-open condition):
     https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md
124. web.dev, "Protect your resources from web attacks with Fetch Metadata" (the Resource Isolation
     Policy, the attacks it stops, and its three deployment steps):
     https://web.dev/articles/fetch-metadata

The OWASP Top 10 and the projects it points to

125. OWASP Top 10:2025, Introduction and "What are Application Security Risks" (the 248 CWEs in
     its ten categories, the data on over 2.8 million applications, the survey that picks two
     categories, the ranking by incidence and by exploit and impact scores):
     https://github.com/OWASP/Top10/blob/master/2025/docs/en/0x00_2025-Introduction.md,
     https://github.com/OWASP/Top10/blob/master/2025/docs/en/0x02_2025-What_are_Application_Security_Risks.md
     and the index page, https://github.com/OWASP/Top10/blob/master/2025/docs/en/index.md
126. OWASP Top 10:2025, "Establishing a Modern Application Security Program" (an awareness
     document, the bare minimum as a standard, ASVS as the standard to adopt, the Cheat Sheets and
     Proactive Controls as a starting point):
     https://github.com/OWASP/Top10/blob/master/2025/docs/en/0x03_2025-Establishing_a_Modern_Application_Security_Program.md
127. OWASP ASVS 5.0, "What is the ASVS?" (the three levels):
     https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x03-What-is-the-ASVS.md; the project page:
     https://owasp.org/www-project-application-security-verification-standard/
128. OWASP Top 10 Proactive Controls (2024 edition): https://top10proactive.owasp.org/
129. OWASP Web Security Testing Guide (stable version 4.2):
     https://owasp.org/www-project-web-security-testing-guide/
130. OWASP Cheat Sheet Series, the index of every sheet: https://cheatsheetseries.owasp.org/

Refresh tokens and logout races

131. Auth0, refresh token rotation (a reused token revokes the tokens issued since, with the
     grant; the rotation overlap period, off by default):
     https://auth0.com/docs/secure/tokens/refresh-tokens/configure-refresh-token-rotation; Okta,
     refresh token rotation (reuse outside its grace period):
     https://developer.okta.com/docs/guides/refresh-tokens/refresh-token-rotation/
132. CVE-2025-32441, a deleted session restored by parallel requests in Rack's session
     middleware: https://osv.dev/vulnerability/CVE-2025-32441; Django ticket 37249, a race that can
     undo logout: https://code.djangoproject.com/ticket/37249

OAuth errors and cookie names

133. RFC 6749, The OAuth 2.0 Authorization Framework, sections 4.1.2.1 (the error response at the
     redirect URI: `error`, `error_description`, `state`) and 5.2 (the token endpoint's error
     codes, sent with `400`, or `401` for `invalid_client`): https://www.rfc-editor.org/rfc/rfc6749;
     RFC 6265, HTTP State Management Mechanism, sections 4.1.1 (`cookie-name` is a token) and 5.2
     (a browser takes as the name everything before the first `=`):
     https://www.rfc-editor.org/rfc/rfc6265

Threat modelling, alerting and the case of cookie names

134. OWASP Top 10:2025, A06 Insecure Design (threat modelling for critical parts of the
     application) and A09 Security Logging and Alerting Failures (alerting, so a team can respond
     to an incident):
     https://github.com/OWASP/Top10/blob/master/2025/docs/en/A06_2025-Insecure_Design.md,
     https://github.com/OWASP/Top10/blob/master/2025/docs/en/A09_2025-Security_Logging_and_Alerting_Failures.md
135. OWASP Threat Modeling cheat sheet:
     https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html
136. ASP.NET Core, `RequestCookieCollection` source (request cookies looked up by name in any
     case):
     https://github.com/dotnet/aspnetcore/blob/main/src/Http/Http/src/Internal/RequestCookieCollection.cs;
     Mozilla's advisory for Firefox 127, CVE-2024-5699 (cookie prefixes ignored when not written in
     the right case): https://www.mozilla.org/en-US/security/advisories/mfsa2024-25/#CVE-2024-5699

Sibling sites, locks, popups and browser results

137. David Dworken, web.dev, "Securely hosting user data in modern web applications" (2023; user
     content on a separate site, active content on a domain on the Public Suffix List or, as the
     simplest option, under `Content-Security-Policy: sandbox`, inactive content without one):
     https://web.dev/articles/securely-hosting-user-data
138. GitHub, "Yummy cookies across domains" (2013; cookies thrown from a subdomain, expired by the
     server once for each part of the path, and a cookie overflow it cannot block):
     https://github.blog/news-insights/company-news/yummy-cookies-across-domains/
139. Martin Kleppmann, "How to do distributed locking" (2016; a lock holder delayed past its
     lease that still writes):
     https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html
140. MDN, `Cross-Origin-Opener-Policy` (`same-origin` cuts the references between a page and a
     cross-origin window it opens):
     https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Opener-Policy
141. W3C, Content Security Policy Level 3, Editor's Draft, section 6.7.2.9 "scheme-part matching"
     (an `https` source does not match a `wss` URL): https://w3c.github.io/webappsec-csp/
142. web-platform-tests, cookie prefixes, the stable aligned run of 2026-10-06 (Safari 27.0 matches
     prefixes case-sensitively, stores a `__Host-` cookie set with no `Path` attribute, and lets a
     `__Host-Http-` cookie without `HttpOnly` be set by `Set-Cookie` and by `document.cookie`):
     https://wpt.fyi/results/cookies/prefix?label=stable&aligned and its test file
     `__Host-Http.https.html`:
     https://wpt.fyi/results/cookies/prefix/__Host-Http.https.html?label=stable&aligned

Step-up guesses, the window option and a cookie with an empty name

143. OWASP Transaction Authorization cheat sheet, section 1.5 (each transaction authorized with
     credentials of its own):
     https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html
144. OWASP ASVS 5.0, chapter V6 Authentication (6.3.1, controls against credential stuffing and
     password brute force):
     https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x15-V6-Authentication.md
145. Mozilla bug 1779993 (a `Set-Cookie` with an empty name whose value starts with `__Host-` or
     `__Secure-` got past the prefix rules; fixed):
     https://bugzilla.mozilla.org/show_bug.cgi?id=1779993

Cookie names a framework decodes

146. NVD, CVE-2020-7070 (PHP URL-decoded cookie names before 7.2.34, 7.3.23 and 7.4.11):
     https://nvd.nist.gov/vuln/detail/CVE-2020-7070
147. PHP's security advisory GHSA-wpj3-hf5j-x4v4, CVE-2024-2756 (a cookie name that starts with
     `_[Host-` parsed as `__Host-`; patched in 8.1.28, 8.2.18 and 8.3.6):
     https://github.com/php/php-src/security/advisories/GHSA-wpj3-hf5j-x4v4

Sender-constrained tokens and blob URLs

148. RFC 9449, OAuth 2.0 Demonstrating Proof of Possession (DPoP), September 2023, section 2 (a
     token bound to a key pair; a key made non-extractable with the Web Crypto API leaves a token
     that a script copies out unusable on its own): https://www.rfc-editor.org/rfc/rfc9449
149. The URL Standard, section 4.7 "Origin" (a blob URL takes the origin of its blob URL entry's
     environment): https://url.spec.whatwg.org/#origin; the File API, sections 8.2 and 8.4 (that
     environment is the settings object of the page that called `createObjectURL`):
     https://w3c.github.io/FileAPI/#url-model

The Top 10's edition

150. OWASP Foundation, OWASP Impact Report 2025, "A word from our Executive Director" (page 4;
     the 2025 list as the eighth edition of the OWASP Top 10):
     https://owasp.org/assets/files/OWASP_Impact_Report_2025.pdf
