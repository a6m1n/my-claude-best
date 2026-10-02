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
- [17. Review checklist](#17-review-checklist)
- [18. Sources](#18-sources)

## 1. Purpose and the one rule

This file is for everyone who writes or reviews the browser side of a React application: people
and AI agents alike. Read it before you put data from outside the application on the page, handle
a session or a token, add a setting or a dependency, add a third-party script, or change the
headers, the dev server or the CI workflow. Every line that carries a read date is to be
distrusted after 2027-04-01 until it is read again; the README's "How to adopt" says how to list
those lines.

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
skill is [designing-with-claude-code.md](../design/designing-with-claude-code.md) section 7.

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
  cookie stops a script on the page, not malware on the disk.

## 3. XSS: what JSX escapes, and the sinks it does not

React escapes every string it renders as text, so `{invoice.customerName}` shows `<script>` as
characters on the screen, and a value it sets on a named prop cannot break out of that prop
(De Ryck, 2020). That covers most of a screen. It does not decide whether the value is safe for
what the prop does, and it does not reach the places where a string becomes HTML, a URL, a set of
props, a style or code. OWASP's XSS cheat sheet asks you to know where your framework stops
protecting you, and names React's gaps: HTML set without sanitising, and `javascript:` or `data:`
URLs.

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
  (its upgrade guide, read 2026-10-01), and OWASP still lists `data:` URLs as a gap React does not
  handle. An allowlist also stops a scheme nobody planned for; a check for `javascript:` stops one
  scheme. Philippe De Ryck (2020) recommends an allowlist over a blocklist, and react-markdown's
  default list (`http`, `https`, `irc`, `ircs`, `mailto`, `xmpp` and relative URLs) is a
  maintainer's reference set. A relative path the application builds itself needs no check.
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
- **Serve files that users upload from another origin.** `'self'` allows every script file the
  application's origin serves, so an upload served from that origin could be loaded as script. No
  owner states this for this case; it is the practice's choice, drawn from the allowlist bypasses
  the 2016 study measured.
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
  (OWASP).
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
| `Cache-Control` | `no-store` on any response that carries personal data or a session id, HTML included | a shared cache keeping one user's data for the next user (OWASP's Session Management cheat sheet) | the API's responses, not this file |

## 6. Sessions and tokens

Preventing XSS comes first: when an attacker's script runs on the page, no storage choice stops
it from acting as the user (section 2). De Ryck argued in 2020 that storage hardly matters once
XSS exists. The storage choice still decides what the attacker takes away: a stolen token works
from the attacker's own machine until it expires, while a session cookie that script cannot read
works only through the user's open browser. RFC 10017, which De Ryck co-wrote, ranks the patterns
by that exposure, and this practice follows the RFC.

RFC 10017 (BCP 212, August 2026) gives three patterns, "presented in decreasing order of
security" (section 6):

| Pattern | Who holds the tokens | What the RFC says |
|---|---|---|
| Backend for Frontend (BFF), section 6.1 | the backend, as a confidential OAuth client; the browser holds only an `HttpOnly` session cookie | "This architecture is strongly recommended for business applications, sensitive applications, and applications that handle personal data." The same section names the cost: "The architecture of a BFF is significantly more complicated than a browser-only application. It requires deploying and operating a server-side BFF component." (6.1.4.3) |
| Token-mediating backend, section 6.2 | the backend gets the tokens and hands the access token to the browser | its security properties "lie somewhere between using a BFF and running" a browser-only application |
| Browser-based OAuth client, section 6.3 | the browser, as a public client | last in the order; all four attack scenarios of section 5.1 apply to it |

- **Choose the BFF for a business application, a sensitive one, or one that handles personal
  data.** That is the RFC's recommendation, and a billing screen is all three. With a BFF the
  frontend reads, stores and sends no token: it sends requests with `credentials: "include"`, and
  the browser adds the cookie. Section 15 shows the BAD and the GOOD. Where the route guard and
  the sign-out handler live is [architecture.md](../architecture/architecture.md) section 10; the
  guard is for the user's convenience, and access control stays on the server (section 2 of this
  file).
- **Know what a BFF does not stop.** A script on the page can still send requests to the BFF
  through the user's session: the RFC's fourth scenario, "Proxying Requests via the User's
  Browser". And a cookie session brings CSRF back (Auth0, 2026), so section 7 is part of the same
  choice.
- **If you choose a browser-only client for a lower-risk application, use the authorization code
  flow with PKCE, never the implicit grant** (RFC 9700; oauth.net), so no access token travels in
  a redirect URL, where it can leak and be replayed.
- **Use a maintained library or the provider's SDK for the OAuth flow, never your own code**
  (OWASP's Authentication cheat sheet), so the flow's checks come from code that others review and
  keep patched.
- **Set the SDK's token storage option explicitly.** Vendors' defaults differ: Auth0's SPA SDK
  keeps tokens in memory, MSAL.js in `sessionStorage`, Okta's auth-js in `localStorage` (vendors'
  docs read through search summaries, 2026-10-01; re-check them).

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

- **Never keep a token, a session id or any other credential in `localStorage` or
  `sessionStorage`.** OWASP's Session Management cheat sheet says the same, and RFC 10017 section
  8.5 gives the reason.
  Check: in review, `grep -rnE "(local|session)Storage" src/` shows no token, session id or key.
- **Never write a token into a cookie from JavaScript** (RFC 10017 section 8.1).
- **A browser-only client keeps its tokens in memory or in a worker, and accepts the limit both
  share:** the attacker's script can still ask the provider for new tokens (RFC 10017 sections 8.2
  to 8.4).
- **Before a browser-only client takes refresh tokens, confirm that the provider meets RFC 10017
  section 6.3.2.3.** The RFC first says that authorization servers "may choose whether or not to
  issue refresh tokens to browser-based applications". If they do, they "MUST either rotate refresh
  tokens on each use OR use sender-constrained refresh tokens as described in Section 4.14.2 of
  [RFC9700]"; "MUST either set a maximum lifetime on refresh tokens OR expire if the refresh token
  has not been used within some amount of time"; and "MUST NOT, upon issuing a rotated refresh
  token, extend the lifetime of the new refresh token beyond the lifetime of the initial refresh
  token if the refresh token has a preestablished expiration time". Rotation does not make
  `localStorage` safe: De Ryck (2021) concludes that sensitive single-page applications should
  use a BFF rather than rely on rotation in the browser.

The session cookie the BFF sets:

| Attribute | Value | Why |
|---|---|---|
| name prefix | `__Host-Http-` (RFC 10017 section 6.1.3.2) | it keeps every `__Host-` rule: the browser accepts the cookie only with `Secure`, no `Domain` and `Path=/`, so it stays bound to this one host (MDN; OWASP); `Http` marks it as set over HTTP (RFC 10017) |
| `Secure` | set | sent over HTTPS only |
| `HttpOnly` | set | `document.cookie` cannot read it, and `fetch` still sends it (MDN) |
| `SameSite` | `Strict` (RFC 10017 section 6.1.3.2; OWASP's preference) or `Lax`, always written out | left out, it means `Lax` only in Chromium, and even there a cross-site POST within two minutes of setting still carries the cookie (MDN) |

The server's part of the session, such as a new session id after login, and idle and absolute
timeouts, is in OWASP's Session Management cheat sheet.

## 7. CSRF and CORS

A session cookie goes with every request to its site, including requests that another site makes
the browser send. Cross-site request forgery (CSRF) uses that: a page elsewhere submits a form to
your API, and the browser adds the user's cookie. A BFF trades token theft for this risk (Auth0,
2026), so every application with a cookie session needs a CSRF defence. The defence is the
server's; the browser side keeps its half.

OWASP's CSRF Prevention cheat sheet lists the defences in this order:

1. the framework's built-in CSRF protection, where it has one;
2. a token: a synchronizer token, or a signed double-submit cookie bound to the session with an
   HMAC (a plain double-submit cookie is open to cookie injection);
3. Fetch Metadata: the server rejects a state-changing request whose `Sec-Fetch-Site` header is
   `cross-site`, and checks `Origin` where the header is missing;
4. a custom request header on API calls;
5. `SameSite` cookies and origin checks, as defence in depth.

The browser side:

- **Send the custom header on every API request, from the one API client.** A header such as
  `X-Requested-With` makes the browser send a CORS preflight first, and the server allows it only
  for the application's origin (`https://app.example.com`), so another site cannot send the
  request from a form (OWASP, item 4; MDN on which headers start a preflight). The server rejects
  a request without the header. The reference API client is in section 15 and in
  [security-example.md](security-example.md).
  The one boundary: a report the application sends about itself (web vitals, errors) goes without
  a cookie, through the `report` method of the API client, to the report intake, a separate
  endpoint that takes anonymous reports. It carries no session to forge, so it needs no header. An
  endpoint that did read the session would need the client's `request` method.
- **Never change state on a `GET`.** OWASP notes that `SameSite=Lax` does not cover a state change
  made with `GET`, since the cookie still goes with a top-level `GET` from another site.
- **Send the CSRF token the server issues, where it uses one,** in a header of each
  state-changing request. Login needs a token of its own, issued before the session exists
  (OWASP).
- **Treat `SameSite` as defence in depth, never as the defence.** OWASP says it does not replace a
  proper CSRF defence in most deployments. It is scoped to the registrable domain, not the origin,
  so every subdomain of the site counts as same-site: a 2021 USENIX study found exploitable issues
  through such related domains on 887 of the top 50,000 sites. Filippo Valsorda (2025) writes that
  the rollout of `Lax` by default has mostly failed and recommends `Sec-Fetch-Site`, which Go 1.25
  ships as `CrossOriginProtection`.
- **Next.js Server Actions: when a reverse proxy does not forward the public host in
  `x-forwarded-host`, list the host the browser shows in
  `experimental.serverActions.allowedOrigins`.** The framework compares `Origin` with the host on
  every action and uses no CSRF token (Next.js data security guide, read 2026-10-01).

CORS:

- **With credentials, the server names one exact origin in `Access-Control-Allow-Origin`, never
  `*` and never the request's `Origin` copied back, and sends `Vary: Origin`** (MDN; OWASP's HTML5
  Security cheat sheet). An origin copied back hands every site the user's session.
- **Do not count CORS as a CSRF defence.** It loosens the same-origin policy for the origins it
  names; it does not stop a form that another site submits (MDN).

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
  host's mitigations.
  Check: when you set up the repository, name the person or the channel that receives the security
  advisories of React, the framework and the router on the day they are published, and turn on
  Dependabot or Renovate security updates, which skip their cooldowns (section 10).
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
  router, Vite and DOMPurify. A critical fix can then go in through the emergency path on the day
  it ships, not at the next dated re-check or CI run.

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

- **Prefer a data layer to a vendor's script on the page.** Your own code collects the events and
  sends the vendor only the fields you chose, so only your JavaScript runs in your users' browsers
  (OWASP's Third Party JavaScript Management cheat sheet).
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

Good: `src/core/api-client.ts`, the `request` method of `ApiClient`. The imports, the error
class, the request type, the constructor, the error check and the parsing of the response are
cut; the whole file is in [security-example.md](security-example.md) section 1.

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
can still send requests through the session, but it takes nothing away. The custom header follows
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
OWASP still lists `data:` URLs as a React gap, and versions before React 19 do not refuse
`javascript:` either. `no-script-url` does not report this line: it sees a `javascript:` string
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
  the page's reach (RFC 10017 section 8.6).
- **Old code does not wait.** These rules exist because the old way is a security hole, so old
  code is fixed by a date, not when a change happens to touch it
  ([refactoring.md](../../any-language/refactoring/refactoring.md) section 6).
- **Moving targets** change under these rules: package manager defaults, the framework and Vite
  advisories, browser support for Trusted Types and the Sanitizer API, the lint presets. Each line
  that names one carries the date it was read, and [README.md](README.md) lists what to re-check.

## 17. Review checklist

A review question per section. OWASP's ASVS 5.0, chapter V3 "Web Frontend Security", is the longer
checklist for the same ground. Each red flag is a way in, so one red flag is enough to stop the
merge until it is fixed or the author shows why it does not apply; that bar is the practice's
choice.

| Section | Ask | Red flag |
|---|---|---|
| 2. What the browser can protect | Does the server check this request on its own? | a permission enforced only by hiding a button or a route |
| 3. XSS | Can a value from outside reach HTML, a URL, a props object, a style or code? | a URL from data with no scheme allowlist; outside data spread as props; a renderer's `urlTransform` overridden |
| 4. Sanitising | Is the HTML sanitised in the sink's own render? | a second `dangerouslySetInnerHTML`; a sanitised string changed or joined after cleaning |
| 5. Headers | Does the built page run under a policy with no `'unsafe-inline'` in `script-src`? | `'unsafe-inline'` or `data:` in `script-src`; a policy only in `<meta>`; a nonce in a cached response |
| 6. Sessions | Can script read anything that grants access? | a token or session id in `localStorage`, `sessionStorage` or a cookie set by script |
| 7. CSRF and CORS | Does each state-changing request carry the CSRF defence? | a state change on `GET`; `Access-Control-Allow-Origin` copied from the request, or `*` with credentials |
| 8. Server-side React | Does each Server Function check the user and the record itself? | authorisation only in middleware; a secret written in server code |
| 9. Secrets | Would you publish every `VITE_` value on the login page? | a key, a token or a password behind a public prefix; production source maps published |
| 10. Supply chain | Does every install obey the cooldown and the script block, with a named emergency path? | a new dependency nobody checked on the registry; an action pinned by tag; fork code in `pull_request_target` |
| 11. Dev server | Does the dev server answer only localhost? | `allowedHosts: true`; `cors: true`; `host` open on a network you do not trust |
| 12. Edges | Does each `message` listener check one exact origin? | `postMessage(…, "*")`; a sandbox with both `allow-scripts` and `allow-same-origin`; a redirect to a raw `?next=` |
| 13. Data exposure | Can a URL, a log line or a replay carry a credential, and does a failed screen show a message of its own, not the error's text? | a token in a query string; replay masking turned off; paste blocked; the error's own text on a failed screen |
| 14. Automation | Are the sink rules on, as errors? | a suppression with no reason |

## 18. Sources

Every source below except RFC 10017 and OWASP's Error Handling cheat sheet was read through a
summarising tool, so this file quotes none of them; each is the place to look for the rule it
backs. Those two were read as raw text, and their quotes are verbatim. Read 2026-10-01 unless a
date is given.

Standards and access control

1. RFC 10017, "OAuth 2.0 for Browser-Based Applications", BCP 212, August 2026 (A. Parecki,
   P. De Ryck, D. Waite): https://www.rfc-editor.org/rfc/rfc10017.txt — the attack scenarios
   (5.1), the three patterns and their order (6), the BFF recommendation and its cost (6.1.4.3),
   refresh tokens (6.3.2.3), token storage (8.1 to 8.6).
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
   checklist.

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
