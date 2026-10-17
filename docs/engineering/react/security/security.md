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
  BFF's settings with its reason next to it (section 6, "The session's life", says more).
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
  (section 7), and on a subdomain of the site it would be the sibling subdomain that the cookie and
  CSRF rules of sections 6 and 7 defend against. web.dev's article (Dworken, 2023, read
  2026-10-16) serves active content from a domain on the Public Suffix List. The same article
  calls a `Content-Security-Policy: sandbox` header on the file's response the simplest option, and
  likely enough when Spectre-class and renderer-compromise attacks are outside the threat model, so
  a team whose threat model leaves those attacks out may send that header instead, and a team whose
  threat model includes them uses the separate site.
- **Serve an inactive file that users upload, such as an image or a download, from the API's
  origin under the response headers of section 7, for the page to show as the blob rule of
  section 7 says,** since the same article allows inactive content without a sandbox domain when
  its response carries safe headers.
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
  collector or the report intake of section 7; without one, do not start report-only, since a
  violation then shows only in the browser console of whoever visits
  ([security-example.md](security-example.md) section 6).
- **When a policy starts as report-only, write down the date by which it is enforced, and add a
  task for that date, with an owner, to the team's tracker, linked from the decision log's entry
  ("Write it down" in section 6 says where),** since a report-only policy blocks nothing, and
  without a written end it can stay that way, while the decision log reminds nobody on the date;
  the rule is this practice's choice.
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
under "Logout" below, would then be the only control that stops a copy of the cookie.

With a first-party login, skip these parts, which hold only with an identity provider:

- "The login cookie" and "Forwarding to resource servers", whole;
- in "Timeouts and refresh", the refresh rules, from the `invalid_grant` rule to the rule on a
  provider that rotates refresh tokens and has no reuse window;
- in "Logout", the rules on revoking the tokens and on RP-initiated, back-channel and
  front-channel logout;
- in "The login and logout responses", the login callback's response;
- in section 7, the rules on refreshing before a request is forwarded and on a resource server's
  `401`.

Any other rule that needs an identity provider says `with an identity provider` in its prefix.

In this section, every rule the page follows starts with `Page:` or
`Page, with an identity provider:`, or with `Browser-only client:` where the page itself holds the
tokens, so a search for those words finds them all. In section 7, the page's rules are under "What
the React code does", and in "Fixing a CORS error" they are the bullets that start with "The page"
or `Page:`. With a BFF, the page's only token rules are the two bans below: no token in
`localStorage` or `sessionStorage`, and no token in a cookie written from JavaScript. The BFF's own
rules start at "The session cookie".

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

### The session cookie

The session cookie the BFF sets:

| Attribute | Value | Why |
|---|---|---|
| name prefix | `__Host-Http-` (RFC 10017 section 6.1.3.2, which takes it from the IETF's layered-cookies draft) | a browser that enforces the prefix accepts the cookie only with `Secure`, `HttpOnly`, `Path=/` and no `Domain`, so neither a script on the page nor a sibling subdomain can set a cookie under that name (the layered-cookies draft; MDN). Chrome, Edge and Firefox enforce it; Safari 27 enforces it neither on `Set-Cookie` nor on `document.cookie`, so there a script on the cookie's own host can set a cookie under that name; it applies only the `__Host-` rules, which the name also matches (web-platform-tests results, read 2026-10-15 and 2026-10-16). Safari 27 also matches the prefix case-sensitively, so it applies no prefix rule to `__HOST-HTTP-SESSION`, and it stores a `__Host-` cookie set with no `Path` attribute (wpt.fyi, the stable aligned run of 2026-10-06, read 2026-10-16) |
| `Secure` | set | sent over HTTPS only |
| `HttpOnly` | set | `document.cookie` cannot read it, and `fetch` still sends it (MDN) |
| `Path` | `/` | the `__Host-` rules ask for it; a path is no security boundary, since other pages on the host can still reach the cookie (the cookie spec, RFC 6265bis draft, read 2026-10-15; MDN) |
| `Domain` | not set | without it the cookie goes back only to the host that set it; with it, every subdomain receives the cookie and can overwrite it (the cookie spec's "Weak Integrity" section, RFC 6265bis draft, read 2026-10-15; MDN) |
| `SameSite` | `Strict`, written out | RFC 10017 section 6.1.3.2 asks for `Strict`. Left out, the default differs by browser: `Lax` in Chromium, none in Firefox and Safari (MDN; Mozilla's bug tracker, read 2026-10-15) |
| `Max-Age` | not set: a non-persistent cookie | the server's idle and absolute timeouts end the session (section 6, "Timeouts and refresh"). A cookie with `Max-Age` is persistent, and the browser keeps it on disk through every close (OWASP's Session Management cheat sheet); one without it ends with the browser, though a browser that restores its last session brings it back (MDN), so the timeouts stay the control. Set `Max-Age`, no longer than the absolute timeout, only when the product needs the session to survive a browser close |
| `Partitioned` | not set | it keeps a cookie to the site that embeds another site's frame (CHIPS); the application's own session is no such cookie (MDN) |

- **BFF: name the cookie `__Host-Http-session` and still write `Secure`, `HttpOnly` and `Path=/`
  yourself, and leave out `Domain`,** because Safari 27 does not enforce the `Http` part, and
  stores a `__Host-` cookie set with no `Path` attribute (the table's first row, read 2026-10-15
  and 2026-10-16).
- **BFF: use `SameSite=Lax` instead only when the server reads the session on a top-level navigation
  that can arrive from another site,** such as a page the server renders, opened from a link in an
  email, or the first page after the identity provider sends the user back, since `Strict` keeps
  the cookie off those requests (OWASP's CSRF cheat sheet). OWASP's Session Management cheat sheet
  allows `Lax` for session cookies. Duende's BFF sample uses `Lax` because its first request after
  login, a navigation that starts on the identity provider's site, reads the session; Duende
  recommends `Strict` when the provider is on the same site as the BFF (Duende's docs, read
  2026-10-15).
- **BFF: keep `Strict` for a single-page application whose first page after the callback is a
  static file that reads no session,** since a `Strict` cookie set on the login callback is stored
  (RFC 6265bis draft, section 5.7, read 2026-10-15), and the page's later `fetch` calls to the API
  are same-site, so they carry it (the same draft's "site for cookies" rules).
- **BFF: keep the session cookie's name and attributes the same in every environment, never behind
  a setting, and develop on `http://localhost` or on local HTTPS,** since a setting that turns
  `Secure` off for development can ship to production. MDN's `Set-Cookie` page says the `https:`
  requirement of `Secure` is ignored when localhost sets the cookie, and its compatibility data
  says Safari does not send a `Secure` cookie to `http://localhost`, so Safari needs local HTTPS
  (read 2026-10-16). The rule is this practice's choice.

### The login cookie

For the first login, these rules are checks on the OpenID Connect library you use; write code only
for a rule it does not meet.

- **BFF: give the short-lived login cookie (the `state`, the nonce, the PKCE verifier) the session
  cookie's name prefix and attributes:** name it with `__Host-Http-`, write `Secure`, `HttpOnly`
  and `Path=/`, and leave out `Domain`. Without the prefix, a sibling subdomain could set a cookie
  under the same name with its own `state` and verifier and sign the user into the attacker's
  account (OWASP's CSRF cheat sheet).
- **BFF: name the login cookie per attempt, `__Host-Http-login-<id>`, with the id carried in
  `state`,** so a login started in another tab does not overwrite this one's cookie and fail its
  callback. ASP.NET Core names its correlation cookie per attempt in the same way (its
  `RemoteAuthenticationHandler` source, read 2026-10-16).
- **BFF: for the first login, keep what the login attempt records where the user cannot change it:
  in the login cookie's value, signed and encrypted by the framework's own cookie protection,
  under the key rules for every cookie the BFF signs or encrypts ("The session's life" below),**
  since a person at the browser can edit any cookie value that is not protected (section 1's one
  rule), and a login start has no session, so a record kept on the server for it would let anyone
  write records without limit. The rule is this practice's choice.
- **BFF: for a step-up, keep what the attempt records where the user cannot change it: in the
  login cookie's value, protected as the rule above says, or on the server, keyed by the attempt
  id that `state` carries,** since the step-up's checks compare the new ID token with that record,
  and a step-up's records are bounded by the session they belong to and by the per-session cap of
  two in the next rule. The rule is this practice's choice.
- **BFF, with an identity provider: keep at most two live step-up attempts, with their kept
  changes, per session, wherever their record lives, and end the oldest when a third is made,
  making and counting each attempt in one atomic step of the shared store that keeps the
  changes,** so a session, a stolen one included, cannot pile up kept changes, not even with
  guarded requests sent in parallel; the rule is this practice's choice.
- **BFF, with an identity provider: when that per-session cap ends an attempt, expire the ended
  attempt's login cookie on the same `403` when the request carries it,** so the cap and the
  login cookies end the same attempt; the rule is this practice's choice.
- **BFF: at the callback, read the attempt's values, such as the time it started, only from that
  protected record,** so an edited value never passes a check; the rule is this practice's choice.
- **BFF: give the login cookie a `Max-Age` long enough for the user to finish at the provider,
  such as 15 minutes, and delete it at the callback,** since it is needed only between the login
  start and the callback, and the user may enrol a second factor on the way. 15 minutes is ASP.NET
  Core's default for a remote sign-in (`RemoteAuthenticationTimeout`, Microsoft's docs, read
  2026-10-16).
- **BFF: when you set a login cookie, write the time its attempt started into the cookie's
  value,** so the next rule can tell which login cookies are newest: a `Cookie` header carries
  only each cookie's name and value, and the cookie spec tells servers not to rely on the order
  of the cookies in it (RFC 6265bis draft, section 4.2.2, read 2026-10-16). The rule is this
  practice's choice.
- **BFF: at the login start, expire every login cookie the request carries beyond the two with
  the latest start times in their values,** so login cookies cannot pile up until the `Cookie`
  header passes the server's size limit and every request to the API's host fails. ASP.NET Core,
  whose per-attempt cookie this practice follows, has that failure on record (dotnet/aspnetcore
  issue 58731, read 2026-10-16), and the cookie spec warns that many cookies can force the browser
  to evict others (RFC 6265bis draft, section 8.6, read 2026-10-16). The rule, a cap of two,
  is this practice's choice.
- **BFF: refuse a login start whose `Sec-Fetch-Dest` header is present and is not `document`, and
  let a request without the header through,** so in a browser that sends Fetch Metadata, an image
  or a frame on another site cannot start a login; only a top-level navigation can (MDN on
  `Sec-Fetch-Dest`). With `response_mode=form_post`, such a request would store the
  `SameSite=None` login cookie, while a browser that follows the cookie spec already ignores a
  `Lax` login cookie that such a request sets (RFC 6265bis draft, section 5.7), so the refusal is
  the guard for `form_post` and a second guard for `query`. web.dev's Resource Isolation Policy
  lets a request without Fetch Metadata through too, since not every browser sends these headers
  (read 2026-10-16); the rule is this practice's choice. Section 16 names what this leaves open.
- **BFF: at a callback whose login cookie is missing or does not match the `state`, log the reason
  and answer a page that offers to sign in again,** so the user has a way on instead of a dead
  end; the rule is this practice's choice.
- **BFF: give the page that a failed login callback answers with fixed text, and put no parameter
  of the request into it,** such as `error`, `error_description` or `state`, since those come from
  outside (RFC 6749 section 4.1.2.1; OpenID Connect Core 1.0 section 3.1.2.6) and the page is
  served from the API's origin, which holds the session cookie; the rule is this practice's choice.
- **BFF: at every callback that fails, delete this attempt's login cookie,** so a failed sign-in
  leaves no cookie behind to add to the pile; the rule is this practice's choice.
- **BFF: set the login cookie's `SameSite` by the callback's `response_mode`:** `Lax` when the
  identity provider returns with `response_mode=query`, a top-level `GET`; `SameSite=None; Secure`
  with `response_mode=form_post`, a cross-site `POST` on which neither `Lax` nor `Strict` cookies
  are sent (RFC 6265bis draft, section 5.8.3, read 2026-10-15; Microsoft's ASP.NET Core docs set
  these cookies to `None` for that reason, read 2026-10-15). Duende's BFF sample uses `query`,
  which keeps that cookie off cross-site requests other than the callback.

### Reading the `Cookie` header

- **BFF: when an advisory names your server framework, its session and cookie library or its
  OpenID Connect client library, update it under section 10's advisory path,** which covers the
  BFF's own repository too. The browser checks the prefix; a server that parses the
  `Cookie` header in another way can read a cookie the browser treated as a different one.
  PortSwigger's research (2025) got past the `__Host-` and `__Secure-` prefixes on several server
  frameworks through such differences.
- **BFF: read the session cookie and the login cookie only when the raw `Cookie` header holds the
  cookie's exact name once, compared byte for byte, and answer `400` when it holds the name more
  than once,** so the server never has to choose between two values for one cookie. For the login
  cookie the check runs on the raw `Cookie` header before the OAuth library reads it.
- **BFF: check each cookie name in the raw `Cookie` header in this order,** so a planted cookie
  whose name differs from the real one only by characters a token does not allow, such as
  whitespace, is never read under the real name:
  1. When the name is byte for byte the session cookie's name, or starts byte for byte with
     `__Host-Http-login-`, read the cookie under the rule above.
  2. Otherwise, remove from the name every character that a token does not allow (RFC 6265
     section 4.1.1).
  3. When the result is the session cookie's name, or starts with `__Host-Http-login-`, answer
     `400`.
  4. Otherwise, skip the name.

  A sibling subdomain can set a cookie whose name starts with a Unicode space, such as
  U+2000: the browser treats it as another cookie, outside the prefix rules, and frameworks that
  trim cookie names, such as Django and ASP.NET, read it under the real cookie's name, often
  keeping the last of two values (PortSwigger's research, 2025, read 2026-10-16). Whitespace,
  control characters, U+FEFF and every other non-ASCII character are outside the token set, so the
  check catches the name whichever trim function the framework runs.
- **BFF: in step 3 of that check, also lowercase the ASCII letters of both names before you
  compare them,** so a planted cookie whose name differs from the real one only in case is never
  read under the real name. ASP.NET Core looks up request cookies by name in any case (its
  `RequestCookieCollection` source, read 2026-10-16), and Firefox before version 127 ignored a
  cookie prefix written in another case (CVE-2024-5699), as Safari 27 still does (wpt.fyi, the
  stable aligned run of 2026-10-06, read 2026-10-16), so a sibling subdomain can plant
  `__HOST-HTTP-SESSION` and have it read as the session cookie.
- **BFF: skip, never reject, any other cookie whose name is not a token, as RFC 6265 section 4.1.1
  defines `cookie-name`,** since browsers store and send such names: RFC 6265 section 5.2 takes as
  the name everything before the first `=`, so an ordinary cookie set for the whole domain can
  carry one, and rejecting it would fail every request of the users who carry it.
- **BFF: answer `400` to a request whose `Cookie` header starts with `$Version`,** so no server
  reads one cookie string as several. The same research shows that some Java servers, such as
  Apache Tomcat and Jetty, switch to a legacy parser when the `Cookie` header starts with
  `$Version=1`, so a cookie a sibling subdomain sets can carry a forged `__Host-` pair. The
  research gives a test, not a developer rule, so this rule and the four above it are this
  practice's choice; the advisory rule above them stays as the second control.
- **BFF: give every `400` that the cookie checks above answer to a request from the API client a
  JSON body with one fixed code, such as `cookie_conflict`,** so the page can tell the user how to
  get out; the rule is this practice's choice.
- **BFF: answer that `400` on a route the page opens by navigation, such as the login start, a
  callback or the download link, with a page of fixed text that tells the user to clear this
  site's data in the browser,** since no page code runs on a navigation to read a JSON body, as
  with the failed-callback page above; the rule is this practice's choice.
- **BFF: answer a failure on a route the browser reaches by navigation, such as the login start or
  a download link, with a page of fixed text that puts no parameter of the request into it, and on
  a `401` link that page to the sign-in,** since no page code runs on a navigation to read the
  status, and a parameter of the request comes from outside, as the rule on the failed callback's
  page above says. The failed callback keeps its own page; the rule is this practice's choice.
- **Page: on a `400` whose JSON body carries that fixed code, such as `cookie_conflict`, tell the
  user to clear this site's data in the browser,** since a cookie that a sibling subdomain planted
  fails every request until it expires or the user removes it; the rule is this practice's choice.

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

**Write it down** means two things in these rules: a choice, such as where the session's state
lives, goes into the project's decision log
([roles-and-decisions.md](../../any-language/project-management/roles-and-decisions.md) section
7), and a value, such as a timeout or a token lifetime, goes into the BFF's settings with its
reason next to it ([readability.md](../../any-language/readability/readability.md) section 4), so a
later reader finds why.

- **BFF: answer the session check, the "check session" endpoint of RFC 10017 section 6.1.2.1,
  with `200`, the user's display fields and no token when the session is live, and with `401` when
  there is none,** so the page learns who is signed in without holding a token; the contract is
  this practice's choice.
- **BFF: send the session check's answer with `Cache-Control: no-store`,** so no cache keeps one
  user's answer for the next, as for every API response (section 7, "Response headers").
- **BFF: leave the session check out of the idle clock,** so a page that asks on every load, or
  before it reconnects a dropped WebSocket (section 7), does not keep an idle session alive; the
  rule is this practice's choice.
- **Page: when the session check answers `401` on a route that needs no session, show the
  signed-out state instead of running the sign-out path, and check for this case before the `401`
  rule below,** since a visitor on a public page has no session to end, and the sign-out path
  would send them to sign in; the rule is this practice's choice.
- **BFF, with an identity provider: choose where the session's state lives, and write the choice
  down:** on the server, with only a random id in the cookie, or in the cookie itself, signed and
  encrypted. With a first-party login there is no choice: the session's state stays on the server
  (the opening of this section). Where the session's state in the cookie changes a rule, the rule
  says how.
- **BFF, with an identity provider: keep the session's state on the server by default, and choose
  the cookie for a deployment that cannot keep whole sessions in a shared store but can share a
  small list of ended sessions,** since the rules below are
  written for the state on the server and back-channel logout is simpler with it ("Logout" below),
  and RFC 10017 section 6.1.2.3 recommends the session's state on the server only for small
  deployments, because it needs sticky sessions or replication. With the session's state in the
  cookie, the logout rules below say what stops a copied cookie, and the list of ended sessions
  they use still needs a store that every instance reads.
- **BFF, with an identity provider: before you choose the session's state in the cookie, read the
  provider's discovery document for `revocation_endpoint`** (RFC 8414 section 2), so you know
  whether revocation can back up the list of ended sessions.
- **BFF: with the session's state in the cookie, keep each cookie's name and value under 4096
  bytes in all,** since a browser ignores a larger cookie (RFC 6265bis draft, sections 5.6 and 5.7,
  read 2026-10-15).
- **BFF: with the session's state in the cookie, check the session cookie's size before you set
  it; when it is too large, do not set it, log the reason and answer an error page,** because the
  browser drops a cookie that is too large with no error (RFC 6265bis draft, sections 5.6 and 5.7),
  so the sign-in would look done and the next request would answer `401`.
- **BFF, with an identity provider: keep the client's credential at the identity provider in the
  server's secret store, never in code,** so the code, and every copy of it, holds no credential;
  the rule is this practice's choice.
- **BFF: for every cookie the BFF signs or encrypts, the login cookie included, keep the key in the
  server's secret store too, never in code,** so the code, and every copy of it, holds no key; the
  rule is this practice's choice.
- **BFF: for every cookie the BFF signs or encrypts, the login cookie included, give every instance
  the same key,** since an instance with a key of its own cannot read a cookie another instance
  wrote, so users are signed out, or their sign-in fails, at random (Microsoft's ASP.NET Core docs
  on a web farm, read 2026-10-16).
- **BFF: when you rotate that key, add the new key and let the old one still read cookies until
  the absolute timeout has passed,** since a key dropped at once signs every user out (Microsoft's
  ASP.NET Core docs on key management, read 2026-10-16).
- **BFF: when you suspect that the old key leaked, remove it at once, though that signs every user
  out,** since whoever holds the key can write a session cookie the BFF accepts; the rule is this
  practice's choice.
- **BFF: with the session's state in the cookie, protect the cookie with the framework's own
  cookie protection, never with code of your own,** so the encryption comes from code that others
  review and keep patched; the rule is this practice's choice.

### A new session id at login

- **BFF: issue a new session id at login and at every change of privilege, and destroy the old
  one.** An id an attacker set before login, or one that leaked earlier, then dies with the old
  session (session fixation). OWASP's Session Management cheat sheet calls the renewal mandatory,
  ASVS 5.0 requirement 7.2.4 asks for it on every authentication, re-authentication included (the
  step-up rules under "Re-authentication" below), and OWASP Top 10:2025 lists it under A07.
- **BFF, with an identity provider: when the login start request carries the session cookie,
  record that session's id with the attempt; destroy that session at the callback,** because a
  `Strict` cookie does not come with the provider's redirect. With the session's state in the
  cookie, record the old cookie's session id in the same way and add it to the list of ended
  sessions (its rules are under "Logout" below) at the callback, since the new cookie does not stop
  a copy of the old one from working; the rule is this practice's choice.
- **BFF, with an identity provider: at the login callback, when destroying the old session fails,
  log it at `ERROR` ([logging.md](../../python/logging/logging.md) section 4), issue no new
  session and answer the page of a failed callback** (the login cookie rules above), so a failed
  destroy never leaves the old session live beside a new one; ASVS 5.0 requirement 16.5.3 asks to
  prevent fail-open conditions.
- **BFF, with an identity provider: at the login callback, store the ID token's `iss`, `sub` and
  `sid` with the new session,** since the back-channel logout rules and the step-up's checks below
  match on them.
- **BFF: let the framework's session manager create the session id,** since it draws the id from
  a secure random source (ASVS 5.0 requirement 7.2.3 and OWASP's advice for ids you create
  yourself both ask for at least 128 bits).

### Timeouts and refresh

- **BFF: enforce an idle timeout and an absolute timeout on the server.** A timeout holds only
  where the session lives (OWASP). ASVS 5.0 requirements 7.3.1 and 7.3.2 ask for both timeouts.
  With the session's state in the cookie, the cookie carries its signed start and last-use times,
  and the BFF checks both on every request; the idle clock moves when the BFF re-issues the cookie
  on use (ASP.NET Core's cookie authentication is one example, with its `ExpireTimeSpan` and
  `SlidingExpiration` options; Microsoft's docs, read 2026-10-16).
- **BFF: write both timeout values down, as values with their reason ("Write it down", above,
  says where).** The values come from the risk: OWASP gives 2 to 5 minutes idle for high-value
  applications and 15 to 30 minutes for low-risk ones, and 4 to 8 hours absolute for an office
  application; NIST SP 800-63B-4 gives at most 1 hour idle and 24
  hours overall at its middle assurance level, AAL2, and 15 minutes and 12 hours at AAL3. ASVS 5.0
  requirement 7.1.1 asks for the values to be documented.
- **BFF, with an identity provider: when the application asks for step-up re-authentication,
  write down an idle timeout no shorter than the time a user needs to sign in at the provider, or
  write in the decision log why a step-up may end `expired`,** since the idle clock runs while
  the user is at the provider, and a step-up whose recorded session has idled out applies nothing
  ("Re-authentication" below), while the login cookie is sized for that leg, such as 15 minutes;
  the rule is this practice's choice.
- **BFF, with an identity provider: decide whether the idle and absolute timeouts must make the
  user sign in again at the provider, and write the choice down,** since a timeout ends only the
  BFF's session, and the provider can answer the next login from its own session without asking
  the user; the rule is this practice's choice.
- **BFF, with an identity provider: where the timeouts must make the user sign in again, send
  `max_age` on the login that follows a session the timeouts ended, and check the ID token's
  `auth_time` at its callback,** since `max_age` makes the provider re-authenticate a user whose
  last sign-in is older than it allows, and puts `auth_time` in the ID token for the client to
  check (OpenID Connect Core 1.0 sections 3.1.2.1 and 3.1.3.7).
- **BFF: when the token endpoint answers a refresh with `invalid_grant`, end the session,** so the
  session never outlives the tokens it stands for. RFC 10017 section 6.1.2.2 says it makes sense to
  end the session when a refresh token is no longer valid, and RFC 6749 section 5.2 sends
  `invalid_grant` for a refresh token that is invalid, expired or revoked. With the session's state
  in the cookie, ending the session means expiring the cookie.
- **BFF: when the token endpoint answers a refresh with any other error code that RFC 6749 section
  5.2 lists, keep the session, answer the page `502` and log it at `ERROR`
  ([logging.md](../../python/logging/logging.md) section 4),** since those codes
  (`invalid_request`, `invalid_client`, `unauthorized_client`, `unsupported_grant_type` and
  `invalid_scope`) name the client's own request or setup, not the user's grant: ending the
  session on them would sign every user out after one wrong setting, such as a client secret
  rotated at the provider but not in the BFF. The rule is this practice's choice.
- **BFF: when a refresh fails in any other way, keep the session, answer the page `502` or `503`,
  never `401`, and log it,** because the page runs the sign-out path on every `401`. Such a
  failure is a provider that cannot be reached or does not answer, a `5xx`, a `429`, any other
  `4xx`, or a body that does not parse. `502` says that an upstream server answered badly, and
  `503` that the server cannot answer for now (RFC 9110 sections 15.6.3 and 15.6.4); the status is
  this practice's choice.
- **BFF: set the provider's reuse window where it has one,** so a refresh token sent twice within
  it does not count as reuse. Auth0 calls that window the rotation overlap period, and it is off
  by default (vendors' docs, read 2026-10-16).
- **BFF: when the provider rotates the BFF's refresh tokens and has no reuse window that covers the
  requests in flight, and the session's state is on the server, refresh the tokens of a session at
  most once at a time, and let the session's other requests wait for that refresh and use its
  result,** because parallel requests would each refresh with the same refresh token, and where
  the provider rotates refresh tokens, the second use counts as reuse: Auth0 then revokes every
  refresh token issued since, with the grant, and Okta invalidates the newest refresh token and the
  access tokens issued since sign-in, unless the reuse falls in its grace period (vendors' docs,
  read 2026-10-16); the rule is this practice's choice.
- **BFF: with the session's state on the server, hold that one refresh with a lock that every
  instance shares, keyed by the session id,** since the session's requests can reach any instance;
  the rule is this practice's choice.
- **BFF: when the lock cannot be taken because the store that holds it fails, answer `503` and
  never refresh without the lock,** since a refresh without it can send the same refresh token
  twice, which the provider counts as reuse (above); the rule is this practice's choice.
- **BFF: give the lock that holds a session's refresh an expiry shorter than the access token's
  lifetime,** so a lock whose holder stopped frees itself before the session needs its next
  refresh; the rule is this practice's choice.
- **BFF: give the call to the token endpoint, together with the store of its answer, a timeout
  shorter than the lock's expiry, and treat a call that times out as a provider that does not
  answer: keep the session and answer `503` (the refresh failure rule above),** so a refresh
  never outlives the lock that guards it: a holder delayed past its lock's expiry can still write
  after another request has taken the lock (Kleppmann, 2016); the rule is this practice's choice.
- **BFF: store the new tokens before you release the lock,** so the next request that takes it
  refreshes with the newest refresh token, never with one the provider has already rotated; the
  rule is this practice's choice.
- **BFF: when the holder's refresh or its store of the new tokens fails, release the lock and
  answer `503` to the requests that waited,** so no waiting request takes the lock and refreshes
  again with a refresh token the provider may already have rotated; the rule is this practice's
  choice.
- **BFF: answer `503` to a request that waited for the refresh until the lock expired, and to the
  request whose refresh got new tokens that could not be stored, and log it at `ERROR`
  ([logging.md](../../python/logging/logging.md) section 4),** so the page sees an outage it can
  retry, not a sign-out; the rule is this practice's choice. After a failed store, the retry
  avoids a sign-out only while the provider's reuse window lasts, since the refresh token still
  stored is one the provider has already rotated.
- **BFF: with the session's state in the cookie, rely on the provider's reuse window instead of a
  lock, and set it long enough to cover the requests already in flight,** since they still carry
  the old cookie and its old refresh token; the rule is this practice's choice. A refresh whose
  answer never reaches the browser, such as one for a cancelled query or a dropped connection,
  loses its `Set-Cookie`, so the browser keeps the old refresh token until its next request; when
  that request comes after the window, it counts as reuse, and the user is signed out.
- **BFF: when the provider rotates refresh tokens and has no reuse window, keep the session's state
  on the server,** since with the state in the cookie, parallel requests would each refresh with
  the same refresh token, and the second use counts as reuse (above); the rule is this practice's
  choice.
- **BFF: when the session store or the list of ended sessions cannot be read, answer `503`, never
  `401`, never accept the cookie, and log it at `ERROR`
  ([logging.md](../../python/logging/logging.md) section 4),** so an outage neither signs every
  user out through the page's `401` path nor lets a copied cookie through after logout. ASVS 5.0
  requirements 16.5.2 and 16.5.3 ask the application to keep operating securely when an external
  resource fails, and to prevent fail-open conditions.
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
- **BFF: at logout, with the session's state on the server, destroy the session there.** A cookie
  deleted only in the browser leaves a session that still works from a copy of the cookie. OWASP's
  cheat sheet, ASVS 5.0 requirement 7.4.1 and OWASP Top 10:2025 A01 ask for the session to end on
  the server.
- **BFF: end a session on the server by marking it ended, or keep sessions in a store whose save
  fails when the record is gone,** because a request still running when the session ends saves
  the session it loaded and so writes a deleted session back. CVE-2025-32441 let parallel requests
  restore a deleted session in Rack's session middleware, and its advisory names marking sessions
  as logged out as a fix; Django ticket 37249 reports the same race for two of its session stores
  (both read 2026-10-16).
- **BFF: with the session's state in the cookie, write a random session id into the cookie at
  login,** so a later logout can name the session it ends.
- **BFF: with the session's state in the cookie, at logout add the cookie's session id to a list
  of ended sessions that every instance reads, and keep it there until its absolute timeout has
  passed,** because a copy of the cookie still leads to the tokens. ASVS 5.0 requirement 7.4.1
  names such a list for sessions held in a token, and it works without the provider. Revoking the
  tokens at logout (below) is then the second control (RFC 10017 section 6.1.2.3).
- **BFF: with the session's state in the cookie, on every request reject a cookie whose session id
  or provider `sid` is on the list of ended sessions, or whose start time is earlier than its
  user's per-user time (the back-channel logout rules below),** so a copy of the cookie stops
  working as soon as its session ends.
- **BFF: with the session's state in the cookie, keep the access token's lifetime short, and write
  it down,** because revocation on its own leaves a copy of the cookie working until the access
  token in it expires, unless the provider invalidates that token on revocation (RFC 7009 section
  5).
- **BFF: at logout, also revoke the refresh token at the identity provider, and the access token
  where the provider supports it (RFC 7009).** A refresh token that is not revoked still gets new
  access tokens. RFC 7009 names logout as a reason to revoke tokens, and RFC 10017 section 6.1.2.3
  says that, with the session's state in the cookie, revoking the tokens is enough. This practice
  still asks for the list of ended sessions with the session's state in the cookie (the rules above
  say why). With the session's state on the server, neither step replaces the other.
- **BFF: at logout, end the session and expire the cookie before you revoke the tokens, holding
  the tokens the revoke needs only within the logout request,** so a failed revoke never keeps the
  user signed in; the order is this practice's choice.
- **BFF: when destroying the session or adding its id to the list of ended sessions fails at
  logout, log it, answer `503` and keep the cookie,** so the page can try again on the same
  session; the rule is this practice's choice, after ASVS 5.0 requirement 7.4.1, which asks that
  a logout end every further use of the session.
- **BFF: answer the logout request with success also when no session exists,** so a second tab
  that signs out after the first is not told that sign-out failed; the rule is this practice's
  choice.
- **BFF: log a revoke that fails at the provider,** so the token it leaves alive until its own
  expiry shows in the log; the rule is this practice's choice, and
  [logging.md](../../python/logging/logging.md) section 10 says what stays out of the line.
- **BFF: do not retry a failed revoke later,** so the BFF keeps no token after logout; the token
  then ends at its own expiry. With the session's state in the cookie, the list of ended sessions
  already stops every copy of the cookie, so a failed revoke no longer leaves the session usable.
  RFC 7009 section 2.2.1 lets a client retry, since on a `503` the client must assume the token
  still exists, so not retrying is this practice's choice; record it with the logout choices.
- **Page: call the BFF's logout endpoint through the API client,** so the call carries the custom
  header (section 7); the rule is this practice's choice.
- **Page: show the user as signed out when the logout endpoint answers with a `2xx`, and also on a
  `401`, which means the session had already ended; then run the sign-out path,** since the
  session no longer exists on the server; the rule is this practice's choice.
- **Page: when the logout endpoint answers with any other failure, say that sign-out failed and
  offer it again,** since the page cannot remove an `HttpOnly` cookie, so the session is still in
  this browser; the rule is this practice's choice.
- **BFF: where the user should also leave the identity provider, end its session too,** for
  example on a shared device or where one sign-in covers several applications. The BFF ends the
  session as the logout rules above say, expires the cookie, and answers with the provider's
  logout URL, built from `client_id` and the registered `post_logout_redirect_uri`, with
  no `id_token_hint`, so no token reaches the page or a URL (RFC 10017 section 6.1; OpenID Connect
  RP-Initiated Logout 1.0). Without `id_token_hint`, RP-Initiated Logout 1.0 says in section 6 that
  the provider should get the user's explicit confirmation, and in section 3 that it must not send
  the user back to `post_logout_redirect_uri` unless it can confirm that target another way, so the
  redirect back may not happen; the local logout never waits for either step.
- **Page: when the logout answer carries the provider's logout URL, check it by section 3's rule
  for a URL that comes from data, and open it by a top-level navigation,** because a `fetch`
  cannot take the user to another site, and the reference policy's `form-action 'self'` (section
  5) blocks a form posted to another origin. RP-Initiated Logout 1.0 section 2 has the client
  redirect the user's browser to the provider's logout endpoint. The URL comes from the answer, so
  it is data, as the step-up's `authorizationUrl` is ("Re-authentication" below). When the check
  refuses the URL, run the sign-out path without the navigation, since the BFF has already ended
  the local session; the rule is this practice's choice.
- **BFF: accept the provider's back-channel logout,** which names the session to end (Back-Channel
  Logout 1.0). Duende's BFF accepts it only with the session's state on the server (Duende's
  docs, read 2026-10-16); that is a limit of Duende's product, and the specification leaves the
  way a session ends to the application (its section 1). Where back-channel logout is needed, the
  session's state on the server is the simpler choice; that choice is this practice's.
- **BFF: with the session's state in the cookie, end the session that a back-channel logout names
  by adding its `sid` to the list of ended sessions, and for a logout token with no `sid`, keep a
  time per user before which no cookie of that user counts,** since the cookie carries the
  provider's `sid` ("A new session id at login" above) and the every-request check above rejects
  both. ASVS 5.0 requirement 7.4.1 names both ways for sessions held in a token.
- **BFF: when a back-channel logout token carries no `sid`, end every session of the user its
  `iss` and `sub` name,** since Back-Channel Logout 1.0 section 2.4 says a token without `sid` asks
  for all of that user's sessions at the client to be logged out (read 2026-10-16).
- **BFF: answer a back-channel logout with `200` also when no session matches, and with `400` when
  the logout token fails validation,** since section 2.7 of the same specification counts a user
  who is already logged out as a logout that succeeded, and section 2.6 asks for `400` when a
  validation step fails.
- **BFF: log at `INFO` ([logging.md](../../python/logging/logging.md) section 4) a valid logout
  token that matches no session,** so a BFF whose sessions never match shows as a run of such
  lines.
- **BFF: when the session that a valid logout token names cannot be ended, such as when the session
  store cannot be written, log it at `ERROR` with the token's `iss`, `sub` and a short hash of its
  `sid` ([logging.md](../../python/logging/logging.md) sections 4 and 10), and answer `400`,**
  since section 2.8 of the same specification asks for `400` when the logout failed, not the `503`
  of the store-outage rule above. Section 16 names what this leaves open.
- **BFF: prefer back-channel to front-channel logout,** because front-channel logout runs in
  third-party frames, which browsers block (Front-Channel Logout 1.0, read 2026-10-16).
- **BFF: write these logout choices down, in the decision log ("Write it down", above, says
  where).** ASVS 5.0 requirement 7.1.3 asks how federated sessions end to be documented.
- **BFF: at logout, expire the session cookie by name,** so the browser drops it at once (MDN); the
  logout response below shows the line.
- **BFF: send `Clear-Site-Data: "cache", "storage"` only from the origin whose data it should
  clear.** OWASP's cheat sheet suggests `Clear-Site-Data: "cache", "cookies", "storage"`, but
  `"cookies"` clears the cookies of the whole registrable domain, every sibling subdomain included
  (MDN; the W3C draft). GitLab stopped sending it after a sign-out from GitLab signed users out of
  other applications on the same domain (GitLab merge request 156213, 2024). `"storage"` clears
  only the origin of the response, so the header on a response from `api.example.com` leaves what
  `app.example.com` stored. Chrome supports `"cache"` only in part (MDN's compatibility data, read
  2026-10-15). The header is defence in depth; ending the session on the server, or, with the
  session's state in the cookie, the list of ended sessions, is the control.

### Re-authentication

The step-up rules below, down to the rule on the step-up's outcome route, serve ASVS 5.0
requirement 7.5.1, a Level 2 requirement: a team at Level 1 may skip them, and so may a team whose
identity provider holds the email, the phone, the second factor and the recovery data and asks for
re-authentication itself; write the choice down ("Write it down" above says where). The rules
after them, on ending a user's other sessions (7.4.3) and every session of a disabled or deleted
account (7.4.2, a Level 1 requirement), hold for every team.

- **BFF: ask for re-authentication before a change to the email, the phone, the second factor or
  the recovery data,** and after a high-risk event such as a sign-in from a new device. ASVS 5.0
  requirement 7.5.1 asks for full re-authentication before such changes, and OWASP's cheat sheet
  asks for it after high-risk events, so a stolen session cannot take over the account. The rules
  below say how, by who logs the user in.
- **BFF, with an identity provider: re-authenticate the user at the provider, and never ask for
  the provider's password,** since RFC 9700 section 2.4 forbids the password grant, the only way
  the BFF could check it. Start a login with `max_age=0`, which OpenID Connect Core 1.0 section
  3.1.2.1 makes equal to `prompt=login` and which makes the ID token carry `auth_time`.
- **BFF, with an identity provider: when a guarded request needs a step-up, start the login attempt
  in the answer to that request, in this order:**
  1. Create the attempt with its `state`, nonce and PKCE verifier.
  2. Set its per-attempt login cookie on the `403` that asks for re-authentication (the `403` rule
     below).
  3. Keep the request's change, keyed by the session's id and the attempt's id, for as long as the
     login cookie lives. When the attempt's record or the change cannot be stored, answer `503`
     instead, with no attempt and no login cookie.
  4. Put the provider's authorization URL for that attempt, with `max_age=0`, in the `403`'s body,
     in the field `authorizationUrl`.

  The change is then bound to its attempt from the moment it arrives, each guarded request gets an
  attempt of its own, so no request replaces another's change, and only the client that sent the
  change holds the cookie that can finish its attempt; the rule is this practice's choice.

RFC 10017 section 6.1.2.1 starts the flow with a navigation to the BFF's login endpoint instead,
and says that returning the authorization URL in a response, as the rule above does, "requires a
custom implementation and makes it harder to use standard OAuth libraries". This practice takes
that cost because a navigation that carries a step-up id can come from any same-site page, a
sibling subdomain included, so a thief's id could be bound to the user's re-authentication, while
a login cookie set on the `403` reaches only the client that sent the change. The first login
keeps the navigation start, since no change waits on it.

RFC 9470 section 2 has the client repeat its request once the user has re-authenticated, so the
page could instead keep the change, re-authenticate the user in a popup and send the change again
itself. This practice keeps the navigation, because the reference policy's
`Cross-Origin-Opener-Policy: same-origin` (section 5) cuts the page's link to the popup (MDN), so
a popup flow needs that header relaxed to `same-origin-allow-popups`, which MDN names for OAuth
popups, or another way back to the page; the navigation needs neither, and the BFF's outcome code
tells the page what happened.

A simpler design marks the session as recently re-authenticated for a short window, and the page
sends the change again within it. This practice binds each change to its own attempt instead,
because a window lets any request of the session through, a page script's included; OWASP's
Transaction Authorization cheat sheet asks the same in its section 1.5: "Each transaction should
be authorized using unique authorization credentials". The cost: the BFF keeps the user's change
for as long as the login cookie lives.

- **BFF, with an identity provider: when the `403` creates the attempt, record with it the id of
  the session that the guarded request carried, with that session's `iss`, `sub` and `sid`,**
  since the step-up's callback is a cross-site navigation that carries no `Strict` session cookie,
  and the checks below need that session. With the session's state in the cookie, record the
  cookie's session id and the session's start time that the cookie carries. The rule is this
  practice's choice.
- **BFF, with an identity provider: of the login cookie's rules above, apply to this attempt these:
  the per-attempt name and the cookie's attributes, the protection of what the attempt records,
  the per-session cap of two and the expiry of the cookie it ends, the start time in its value,
  its lifetime, the cap of two on the login cookies a request carries, `SameSite` by
  `response_mode`, and the callback rules,** since the step-up's callback runs on the login
  callback's path. The per-session cap of two still holds, so a third guarded request ends the
  oldest attempt, and that attempt's change is never applied. The rule is this practice's choice.
- **BFF, with an identity provider: do not apply the login cookie's `Sec-Fetch-Dest` rule above to
  this attempt,** since that rule would refuse it: the request that creates the attempt is a
  `fetch`, which a browser sends with `Sec-Fetch-Dest: empty`, and the section 7 checks guard that
  request instead. The rule is this practice's choice.
- **BFF, with an identity provider: at the step-up's callback, accept the guarded change only when
  the new ID token's `iss` and `sub` equal those of the session recorded with the attempt and its
  `auth_time` is later than the time the step-up started,** because `iss` and `sub` together are
  the only claims a client can rely on to name the same user (OpenID Connect Core 1.0 section 5.7),
  so a thief who holds the cookie cannot pass the step-up by signing in to their own account, and a
  provider session that answers without asking the user does not count.
- **BFF, with an identity provider: when `iss` or `sub` does not match, refuse the change, end the
  session recorded with the attempt, log it and alert (the logging and alerting rules of section
  7),** since another account at the callback means the session may be in someone else's hands;
  the rule is this practice's choice.
- **BFF, with an identity provider and the session's state in the cookie: count the session
  recorded with a step-up's attempt as live only while it passes the every-request check of
  "Logout" above,** since the BFF has only what the attempt recorded: neither the recorded session
  id nor its provider `sid` may be on the list of ended sessions, and its start time may not be
  earlier than its user's per-user time. The rule is this practice's choice.
- **BFF, with an identity provider and the session's state in the cookie: count that session as no
  longer live once its absolute timeout, counted from the recorded start time, or its idle
  timeout, counted from the time the step-up started in the protected record, has passed,** since
  the BFF has only what the attempt recorded. The rule is this practice's choice.
- **BFF, with an identity provider: complete a step-up at its callback in this order,** so only
  the change the step-up was for is applied, only for a session that is still live, the page has
  nothing to send again, and the old session never stays live beside the new one; the order is
  this practice's choice:
  0. When the code exchange or the library's ID token checks fail, or the change kept with the
     attempt is gone, issue no new session, apply nothing and answer `failed`. When the session
     store or the list of ended sessions cannot be read, log it at `ERROR`
     ([logging.md](../../python/logging/logging.md) section 4), apply nothing and answer
     `failed`: the callback is a navigation, so this is its exception to the `503` of the
     store-outage rule in "Timeouts and refresh" above.
  1. Run the `iss`, `sub` and `auth_time` checks above against the attempt's protected record
     ("The login cookie" above). When a check fails, apply nothing and answer `refused`; a failed
     `iss` or `sub` also ends the recorded session, as the rule on a mismatched `iss` or `sub`
     above says. When ending it fails, log it at `ERROR`
     ([logging.md](../../python/logging/logging.md) section 4) and alert a person, saying that the
     session is still live; still apply nothing and answer `refused`.
  2. When the session recorded with the attempt is no longer live, issue no new session, apply
     nothing and answer `expired`.
  3. Otherwise issue the new session: with the session's state on the server, a new session id;
     with the session's state in the cookie, a new session cookie under a new session id. It holds
     the tokens the step-up's own code exchange returned, since RFC 9470 section 4 has a step-up
     obtain a new access token that meets the resource server's needs. It keeps the recorded
     session's start time, `iss` and `sub`, so a step-up never extends the absolute timeout. Its
     `sid` is the new ID token's `sid` when that token carries one, and the recorded `sid`
     otherwise, so back-channel logout still finds the session. Its cookie goes on the callback's
     answer, which a top-level navigation stores (RFC 6265bis draft, section 5.7). When issuing it
     fails, keep the recorded session, apply nothing and answer `failed`.
  4. End the recorded session before the change goes anywhere: with the session's state on the
     server, destroy it; with the session's state in the cookie, add its session id to the list of
     ended sessions. ASVS 5.0 requirement 7.2.4 asks for a new session token on every
     authentication, re-authentication included, and for the end of the current one. When ending
     it fails, log it at `ERROR` ([logging.md](../../python/logging/logging.md) section 4), drop
     the new session, forward nothing and answer `failed`, since ASVS 5.0 requirement 16.5.3 asks
     to prevent fail-open conditions.
  5. Forward the kept change with the new access token, then clear it. On a `2xx` from the
     resource server, answer `applied`. On any other answer, or none, keep the new session, answer
     `failed`, and log it with the resource server's status: a `4xx` at `INFO`, and a `5xx` or no
     answer at `ERROR` ([logging.md](../../python/logging/logging.md) section 4).

  A failed or abandoned step-up applies nothing: its change ends with its attempt. With the
  session's state in the cookie, the old refresh token is never used again, since only the BFF,
  with its client credential, can use it (RFC 10017 section 6.1.2.2).
- **BFF, with an identity provider: answer a step-up's callback whose login cookie matches the
  `state` with a `303` to one fixed route of the page, carrying one of four fixed outcome codes,
  never a value taken from the request,** so the page that loads after the navigation can show
  what happened to the change; the rule is this practice's choice. Each code has one meaning:
  - `applied`: the resource server answered the forwarded change with a `2xx` (step 5 above);
  - `refused`: a check failed (step 1);
  - `expired`: the recorded session was no longer live (step 2);
  - `failed`: the code exchange or the ID token checks failed, the kept change was gone, or the
    session store could not be read (step 0); issuing the new session failed (step 3); ending the
    recorded session failed (step 4); or the forwarded change got any other answer or none (step
    5).

  A provider's error response, and a callback whose login cookie is missing or does not match the
  `state`, get the page of a failed callback instead ("The login cookie" above). So does a callback
  whose login cookie matches the `state` but whose attempt has no record any more, such as a record
  on the server that the per-session cap ended, and nothing is applied.
- **BFF: let one step-up admit only the change that started it, and clear the step-up once that
  change is applied,** so a later request through the same session, such as one a script on the
  page sends, gets no guarded change through without a step-up of its own; the rule is this
  practice's choice.
- **BFF, with a first-party login: ask for the password or a second factor again with the `403`
  below, and take the answer only with the guarded request it is for,** so one answer authorises
  the one change it comes with (OWASP's Transaction Authorization cheat sheet, section 1.5), and
  the BFF keeps no change between the two requests: the page sends that request again with the
  answer. The BFF then counts a wrong answer toward the guess limit below, renews the session id
  as the completion order below says, and applies that request only; the rule is this practice's
  choice.
- **BFF, with a first-party login: check the answer against the user of the session the request
  carries,** so a thief who holds a stolen session cannot answer with the password of an account
  of their own; the rule is this practice's choice.
- **BFF, with a first-party login: count the failed answers to a step-up per session, raising the
  count with one atomic increment in the session store before each answer is compared, and when
  it reaches a small number the team writes down ("Write it down" above), end the session and log
  it,** so a thief who holds a stolen session cannot guess the password through the step-up, not
  even with answers sent in parallel, since each one raises the count before it is compared. ASVS
  5.0 requirement 6.3.1 asks for controls against password brute force; the number and the atomic
  increment are this practice's choice.
- **BFF, with a first-party login: start that count again at zero when a step-up succeeds,** so
  wrong answers in earlier step-ups do not add up and end an honest user's session; the rule is
  this practice's choice.
- **BFF, with a first-party login: answer a wrong answer with a `403` whose JSON body carries a
  fixed code such as `reauth_failed`, and with `401` once the guess limit has ended the session,**
  so the page asks again while it may, and runs the sign-out path once the session has ended; the
  rule is this practice's choice.
- **BFF, with a first-party login: once the answer passes the check, complete the step-up in this
  order,** so a valid answer never lets another change through, only a live session gets the
  change, and the old session never stays live beside the new one; the order is this practice's
  choice:
  1. When the session the request carries is no longer live, issue no new session, apply nothing
     and answer `401`, so the page runs the sign-out path.
  2. Otherwise issue a new session id and move the session into it, since ASVS 5.0 requirement
     7.2.4 asks for a new session token on re-authentication too. When issuing it fails, keep the
     old session, apply nothing, log it at `ERROR` ([logging.md](../../python/logging/logging.md)
     section 4) and answer `503`.
  3. Destroy the old session before the request is applied. When destroying it fails, log it at
     `ERROR` ([logging.md](../../python/logging/logging.md) section 4), drop the new session,
     apply nothing and answer `503`, since ASVS 5.0 requirement 16.5.3 asks to prevent fail-open
     conditions.
  4. Apply the request the answer came with, and only that request, and send its own answer with
     the new session cookie, an error answer included.

  A wrong or missing answer applies nothing, and the BFF keeps no change for a later request.
- **BFF: ask the page for re-authentication with a `403` whose JSON body carries a fixed code such
  as `reauth_required`, and never with a `401`,** because the page runs the sign-out path on every
  `401`. RFC 9470's `401` with the error `insufficient_user_authentication` is a resource server's
  challenge to its OAuth client, which here is the BFF, so RFC 9470 governs the hop from the
  resource server to the BFF (section 7 says what the BFF does with it), not the hop to the page;
  the signal to the page is this practice's choice. The `Page:` rules below say what the page does
  with it.
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
- **BFF: after a change or removal of a password or second factor, offer to end every other
  session of the user** (ASVS 5.0 requirement 7.4.3), so a session stolen before the change stops
  working. The three rules below say how, by who logs the user in and where the session's state
  lives.
- **BFF, with an identity provider and the session's state on the server: end each other session
  that the provider's back-channel logout names** (the back-channel rule above), since the
  provider owns the change, and ending the other sessions goes through its own session end.
- **BFF, with an identity provider and the session's state in the cookie: leave the end of the
  other sessions to the provider's own session end,** since the revocation that ends them is the
  provider's act: revoking the user's refresh tokens at the provider ends the other sessions only
  where the provider revokes the tokens of those grants (RFC 7009 section 2.1); the logout rules
  above say how long a copy of a cookie then works.
- **BFF, with a first-party login: when the user accepts, destroy every other session of the user
  on the server,** as the logout rules above destroy one, since the BFF owns the change and keeps
  the sessions itself.
- **BFF: when an account is disabled or deleted, end every session of the user, in the way the
  three rules above end the other sessions, and with the session's state in the cookie also set
  that user's per-user time to now ("Logout" above),** so a disabled or deleted account keeps no
  session that still works (ASVS 5.0 requirement 7.4.2).

### Forwarding to resource servers

- **BFF: forward requests only to an allowlist of resource servers,** mapping each route to a
  fixed backend, validating the path of any dynamic route, and attaching the access token only to
  those requests (RFC 10017 section 6.1.3.6). A route that takes its host or path from the request
  can send the user's access token to another server.
- **BFF: build each forwarded request from an allowlist of the inbound request's headers: drop
  `Cookie`, any `Authorization` the client sent, and the custom and CSRF headers, and attach only
  the access token,** so the session cookie never reaches a resource server or its logs, and a
  header a script on the page wrote never stands beside the BFF's token. RFC 10017 section 6.1.1:
  "The BFF removes the cookie from the request, attaches the user's access token to the request,
  and forwards it to the actual resource server".

### The login and logout responses

Good: the response of the BFF's login callback, as HTTP. The session value is cut as `…`, `<id>`
stands for the login attempt's id, and the response's `Location` header and the other headers
section 7 asks of every API response are left out. HTTP has no comment syntax, so the reason for
each line is in the table and the login-cookie rules above rather than at the line; that is this
example's one departure from [readability.md](../../any-language/readability/readability.md)
section 4; the cost: the block copied alone carries none of those reasons, so copy the table and
those rules with it.

```http
HTTP/1.1 303 See Other
Set-Cookie: __Host-Http-login-<id>=; Secure; HttpOnly; Path=/; Max-Age=0
Set-Cookie: __Host-Http-session=…; Secure; HttpOnly; Path=/; SameSite=Strict
Cache-Control: no-store
```

It is good because it deletes this attempt's login cookie, `__Host-Http-login-<id>`, at the
callback, as the login-cookie rules ask, with the attributes its prefix requires, so a browser
that enforces the prefix accepts the deletion. The session cookie carries every attribute the
table asks for, so it keeps them in a browser that does not enforce the prefix (the table's first
row), and `no-store` keeps the response out of every cache (section 13).

Good: the response of the BFF's logout endpoint, after it ended the session (destroyed it on the
server, or listed it as ended and revoked its tokens). The other headers section 7 asks of every
API response are left out. HTTP has no comment syntax, so the reason for each line is in the
table above and in the text after the block rather than at the line; that is this example's one
departure from [readability.md](../../any-language/readability/readability.md) section 4; the
cost: the block copied alone carries none of those reasons, so copy the table and that text with
it.

```http
HTTP/1.1 200 OK
Content-Type: application/json
Set-Cookie: __Host-Http-session=; Secure; HttpOnly; Path=/; SameSite=Strict; Max-Age=0
Cache-Control: no-store

{"logoutUrl":null}
```

It is good because it answers `200` with a short JSON body, not `204`: the one API client parses
every response with its schema ([architecture.md](../architecture/architecture.md) section 8), and
an empty body has nothing to parse; [security-example.md](security-example.md) section 1 shows
that client. `logoutUrl` is `null` here, and holds the provider's logout URL where the user should
also leave the identity provider, for the page to open by a top-level navigation (the rules on
leaving the identity provider, above). `Max-Age=0` removes the cookie at once, and the line
repeats every attribute the prefix requires: a browser that enforces the prefix rejects a
`Set-Cookie` without them, so the old cookie would stay. It sends no
`Clear-Site-Data: "cookies"`, which would also clear the cookies of every other application on
`example.com`. It sends no `Clear-Site-Data` at all: the response comes from
`api.example.com`, whose origin holds nothing the page stored, and the page clears what it loaded
through its sign-out path.

## 7. CSRF and CORS

As in section 6, "the server" means the component that receives the browser's session cookie: the
BFF, which in the example is also the API, so the `API:` and `BFF:` rules below name the same
server. An API route is any route of that server other than a `GET` that serves the page's own
files (the HTML and its scripts) or, with a framework that renders on the server, a `GET` that
renders one of its pages.

The page's rules in this section are under "What the React code does", and in "Fixing a CORS
error" they are the bullets that start with "The page" or `Page:`.

### CSRF

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

This practice asks for no token (item 2): the same cheat sheet names a custom request header as a
defence suited to an API that JavaScript calls, and one that needs no token. The cheat sheet also
says that "CSRF tokens are still essential for web applications that rely on cookies for
authentication", and that a browser bug that let a page send custom headers, or skipped the
preflight, "could compromise your security", against which a token adds a layer. RFC 10017
section 6.1.3.3.3 says the anti-forgery cookie, a token kept in a cookie, "is not necessarily
recommended over the CORS approach". This practice follows the RFC, because Fetch Metadata and the
custom header are two mechanisms that one preflight bug does not both break. That holds in every
browser that sends Fetch Metadata; in an old browser that does not, the custom header and the
`Origin` check below are what remain. A framework's own token, where the server already has one,
stays on (item 1).

- **BFF: keep other applications and user content off the site the BFF shares with the page where
  you can, and delete the DNS record of a subdomain when its service is retired,** since `SameSite`
  "is adequate if the BFF is never considered to be same site with any other applications", and
  "a subdomain-takeover attack" against a sibling makes CSRF against the BFF possible again
  (RFC 10017 section 6.1.3.3.1). The rules on sibling subdomains in sections 6 and 7 stay for a
  site where this cannot hold.
- **The server applies the Fetch Metadata check to every request to an API route, reads
  included,** since the custom header holds only while the CORS policy stays tight (item 3 of
  OWASP's list above). OWASP's list checks state-changing requests; Fetch Metadata runs on reads
  too, as web.dev's Resource Isolation Policy does, so another site cannot load the API's answers
  into its own page for script inclusion (XSSI), cross-origin leaks or timing attacks (web.dev,
  "Protect your resources from web attacks with Fetch Metadata").
- **As part of the Fetch Metadata check, when `Sec-Fetch-Site` is absent, the server checks
  `Origin`: it rejects a request whose `Origin` names an origin outside the one setting of allowed
  origins ("What the server does"), and sends a request with neither header on to the
  custom-header check,** since some old browsers send no `Sec-Fetch-*` headers, and OWASP's CSRF
  cheat sheet calls this fallback "a mandatory requirement" for any Fetch Metadata implementation.
- **The server requires the custom header on every request to an API route,** since Fetch
  Metadata is absent from requests that old browsers send (item 4 of OWASP's list above). RFC 10017
  section 6.1.3.3.2 says "the BFF SHOULD require that the browser-based application includes a
  custom request header", and "When this mechanism is used, the BFF MUST ensure that every
  incoming request carries this static header."
- **The server keeps the framework's own CSRF protection on where it has one** (item 1 of OWASP's
  list above), so each check covers what another misses.
- **API: when you add the Fetch Metadata check or the custom-header check to an API that already
  has users, run it in a log-only mode first,** so a tab still on the previous bundle or a client
  nobody listed is not refused from the first deploy. Then fix each legitimate caller the log
  shows, or exempt it when it is one of the endpoints the table below names, and only then enforce
  the check. web.dev gives these three steps for a Resource Isolation Policy, and section 5 uses the
  same order for a new policy.
- **API: when a check starts in log-only mode, write down the date by which it is enforced
  ("Write it down" in section 6 says where), and add a task for that date, with an owner, to the
  team's tracker, linked from the decision log's entry,** since a check that only logs refuses
  nothing, and without a written end it can stay that way, while the decision log reminds nobody
  on the date. web.dev's steps end the log-only stage by enforcing the check (the rule above); the
  written date and the task are this practice's choice.

### What the server does

#### Fetch Metadata and exemptions

- **When the page and the API are two origins of one site, let Fetch Metadata allow the page's
  exact origin, never every `same-site` request.** The page at `https://app.example.com` and the
  API at `https://api.example.com` are one site, so every request from the page arrives with
  `Sec-Fetch-Site: same-site` (the W3C Fetch Metadata draft). OWASP's cheat sheet allows
  `same-site` only when the threat model trusts every sibling subdomain, and both its sample code
  and Filippo Valsorda's algorithm (2025) reject it. So the server accepts `same-origin`, and a
  `same-site` request only when its `Origin` is exactly `https://app.example.com`. When the API is
  on the page's own origin, the server accepts `same-origin` only. Fetch Metadata is Baseline in
  every major browser since March 2023 (MDN, read 2026-10-15).
- **API: keep the allowed origins in one setting per environment, read by the Fetch Metadata
  check, the CORS headers and the WebSocket check,** so a change of domain reaches all three checks
  at once; the rule is this practice's choice. In development the setting also holds the dev
  server's origin, and all three checks then accept it: the WebSocket check needs it, since Vite's
  proxy leaves that check to the target (section 11), and behind the proxy the page's other calls
  arrive as `same-origin`, so the CORS headers go unused there. Production's value holds the one
  origin of the application, so a review of it shows that the dev server's origin is absent.
- **Reject, with `403` and never `401`, a request to an API route that carries no custom header or
  whose Fetch Metadata check fails.** MDN's `Sec-Fetch-Site` page says a request that is not
  accepted should be rejected with a `403`; a `401` tells the page its session has ended, so an
  origin set up wrong would turn into a sign-in loop.
- **Answer `401` only when the session has ended or never existed, and `403` to a request the user
  is not allowed to make** (RFC 9110 sections 15.5.2 and 15.5.4), because the page runs the
  sign-out path on every `401` (section 6). The logout endpoint is the exception: it answers
  success also when no session exists (section 6).
- **BFF: before you forward a request to a resource server, refresh an access token that has
  expired,** so the forwarded request carries a live token; RFC 10017 section 6.1.2.2 describes
  this refresh, done inline while the BFF handles the API call.
- **BFF: when a resource server answers `401` with any error other than
  `insufficient_user_authentication`, or with none, refresh once and forward the request once
  more; answer a second `401` to the page as `502` and log it, and never pass a resource server's
  `401` to the page,** since the page would read a `401` as a session that ended. The retry and the
  `502` are this practice's choice.
- **BFF: when a resource server answers `401` with the error `insufficient_user_authentication`, do
  not refresh; answer the page `403` with `reauth_required`, and start the step-up's attempt with
  the challenge's `acr_values`, and with `max_age=0` as the step-up rules of section 6 ask, which
  also meets any `max_age` the challenge names,** since RFC 9470 uses that challenge to say that the
  user's authentication does not meet the resource server's needs, which a refreshed token does
  not change (section 6, "Re-authentication").
- **Exempt from the custom header and the Fetch Metadata check only the endpoints in the table
  below, and guard each one as its row says,** since a request reaches each of them without the
  custom header. This table is this practice's departure from the MUST of RFC 10017 quoted above,
  and OWASP's CSRF Prevention cheat sheet asks for such an explicit list, each endpoint secured on
  its own. These endpoints skip the framework's own CSRF check too, since they cannot
  carry its token.

| Exempt endpoint | Matches by | Guarded by |
|---|---|---|
| the login start, a top-level `GET` | one exact path and the method `GET` | it changes neither the user's data nor the session; it starts a login attempt, which the login-cookie rules of section 6 bound |
| the login callback, which also applies a step-up's change | one exact path and its method | `state`, the nonce and the PKCE verifier bound to the login cookie (section 6); for a step-up's change, also the steps of section 6's step-up callback |
| the back-channel logout endpoint | one exact path and its method | validating the signed logout token, as OpenID Connect Back-Channel Logout 1.0 section 2.6 says |
| the report intake, a separate endpoint that takes anonymous reports | one exact path and its method | it reads no session, so a report carries no session to forge; the rule on reports below |
| the WebSocket handshake, a `GET` on its one path | one exact path and the method `GET` | the exact `Origin` check below |
| a file the page opens by navigation (a download link) | one route template (a fixed path with the record id as one encoded segment) and the method `GET`; when the request carries Fetch Metadata, also `Sec-Fetch-Mode: navigate` and a `Sec-Fetch-Dest` other than `object` or `embed`, the navigation test of web.dev's Resource Isolation Policy (read 2026-10-16) | it changes nothing, and its answer goes to the user's own window, where no other site can read it (OWASP's CSRF cheat sheet: keep `GET` free of state changes) |
| the CORS preflight | the method `OPTIONS` on any API path | it carries no cookie and no custom header, and changes nothing |

A report the application sends about itself (web vitals, errors) goes to the report intake without
a cookie, through the `report` method of the API client; an endpoint that did read the session
would need the client's `request` method. Every other request to an API route without the header
is rejected. In a client-rendered application served as static files, the routes that serve the
page's own files (the HTML and its scripts) read no session, so neither check applies to them.
The RP-initiated logout needs no exemption: the page calls the logout endpoint through the API
client, so the call carries the custom header, and the navigation that follows goes to the
identity provider, not the BFF (section 6). The download link
stays a navigation so that a large file goes to the browser's download manager, not into the
page's memory; a file the page shows goes through the API client and a blob instead ("What the
React code does").

- **Match each exemption only as its row in the table says, never by a request mode such as
  `Sec-Fetch-Mode: navigate` on its own, by a missing header or by a path prefix,** since a broader
  exemption lets a sibling subdomain's form through with the user's cookie. A request mode may
  narrow a row, as it does for the download link, but never matches on its own. The rule is this
  practice's choice. It departs from step 3.1 of OWASP's Fetch Metadata policy, which allows every
  simple top-level `GET` navigation so that other sites can link to the site: here the pages other
  sites link to are the page's own files, outside both checks, and the few API routes a page
  navigates to are listed one by one.
- **Only as a last resort, add a route that the page loads without `fetch` to the table above, on
  the same terms as the download link:** one route template, never a path prefix, for a `GET` that
  changes nothing, since a route in that table takes the cookie without the custom header; the
  rule is this practice's choice.
- **Treat each report the report intake receives as untrusted data: accept only the schema's
  fields, cap its size, and never render it as HTML,** since the intake takes anonymous reports
  from anyone; this guard is this practice's choice, after OWASP's advice to secure each exempted
  endpoint on its own.
- **Never change the user's data or session on a `GET`; the login start, which starts a login
  attempt, and the login callback, which creates the session or applies a step-up's change, are
  the only exceptions, each guarded as its row in the exemption table says.** OWASP notes that
  `SameSite=Lax` does not cover a state change made with `GET`, since the cookie still goes with a
  top-level `GET` from another site.
- **When the session cookie is `SameSite=Strict`, keep the Fetch Metadata and custom-header checks
  on every API route anyway,** since `SameSite` is defence in depth: OWASP says it does not
  replace a proper CSRF defence in most deployments. It is scoped to the registrable domain, not
  the origin, so every subdomain of the site counts as same-site: a 2021 USENIX study found
  exploitable issues through such related domains on 887 of the top 50,000 sites. Filippo Valsorda
  (2025) writes that the rollout of `Lax` by default has mostly failed and recommends
  `Sec-Fetch-Site`, which Go 1.25 ships as `CrossOriginProtection`.
- **Next.js Server Actions: when a reverse proxy does not forward the public host in
  `x-forwarded-host`, list the host the browser shows in
  `experimental.serverActions.allowedOrigins`.** The framework compares `Origin` with the host on
  every action and uses no CSRF token (Next.js data security guide, read 2026-10-01).
- **For Server Functions and the framework's route actions, guard each one with the Fetch Metadata
  check and the framework's own `Origin` check, and either have it carry the custom header or add
  it to the exemption table as a row with the reason it cannot,** since each one is a public
  endpoint that anyone can send a `POST` to (section 8), and the framework's runtime sends it, not
  the one API client; the rule is this practice's choice.

#### WebSocket

- **Check `Origin` on every WebSocket handshake against the page's exact origin (the one the Fetch
  Metadata rule allows), or the CORS allowlist when there is more than one,** and answer `403` to
  any other origin. The browser sends the session cookie with the handshake, the handshake
  cannot carry the custom header, and `SameSite` lets a sibling subdomain through, so without the
  check a page elsewhere opens a connection as the user (OWASP's WebSocket Security cheat sheet;
  RFC 6455 section 10.2).
- **Tie each WebSocket connection to its session on the server, and close it when the session
  ends:** at logout, at the idle and absolute timeouts, and when a back-channel logout or the
  refresh rule of section 6 ends the session. The cookie is checked only at the handshake, so an
  open connection would keep sending the user's data after the session ended. OWASP's WebSocket
  Security cheat sheet asks to close the connections at logout and when the session expires.
- **When the server closes a WebSocket connection because its session ended, use one close code of
  your own from 4000 to 4999,** the range RFC 6455 section 7.4.2 reserves for private use, so the
  page can tell an ended session from a dropped connection (the `Page:` rules in "What the React
  code does"); the rule is this practice's choice.
- **Check the session of each open WebSocket connection again at an interval no longer than the
  idle timeout, without counting the socket's keep-alive messages as activity on the idle clock,**
  for the reason the polling rule in section 6 gives. With the session's state in the cookie, that
  re-check is what closes the connection once the cookie's times or its tokens fail. OWASP's
  WebSocket Security cheat sheet asks to check the session again from time to time; the interval is
  this practice's choice.
- **BFF: leave the WebSocket handshake out of the idle clock, as section 6 does for the session
  check,** so a page that reconnects a dropped socket does not keep an idle session alive (the
  polling rule in section 6); the rule is this practice's choice.

#### Paths and proxies

- **Validate each dynamic path segment in the API against the format of its id, such as
  `^[A-Za-z0-9_-]{1,64}$`, and reject any other value,** because a denylist of `.`, `..`, `/` and
  `\` has to foresee every encoded form, and one it misses becomes a traversal: a URL parser turns
  `/orders/%2e%2e/x` into `/x` (checked with Node 20's URL parser). OWASP's Input Validation cheat
  sheet asks to define what the application accepts rather than recognise every malicious string,
  and RFC 10017 section 6.1.3.6 asks the BFF to validate dynamic routes strictly.
- **Forward each dynamic path segment percent-encoded, in the API and in any proxy in front of
  it,** since a proxy that decodes `%2F` and then resolves dot segments turns an encoded value back
  into a traversal; the rule is this practice's choice.
- **In nginx, write `proxy_pass` without a URI,** so the API receives the path in the form the
  client sent it: nginx matches a `location` against the URI after it decodes `%XX` and resolves
  `.` and `..`, and its `proxy_pass` with a URI passes that normalized URI on (nginx's docs, read
  2026-10-16). For the same reason a `location` cannot validate the segment, since it matches the
  decoded, resolved URI.

#### Response headers

- **API: send these headers on every API response except the preflight's:** `Cache-Control:
  no-store`, a `Content-Type` that names the exact type of the body, `X-Content-Type-Options:
  nosniff`, `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`, and the API
  host's own `Strict-Transport-Security`, since the page's header covers only `app.example.com`
  and the names under it. They keep the browser from guessing a body's type and running it, and
  keep the answer out of frames and caches (OWASP's REST Security cheat sheet). A preflight answer
  has no body, and no HTTP cache keeps it (RFC 9110 section 9.3.7); the browser's own preflight
  cache is keyed by origin and URL (the Fetch standard).
- **API: add `Sec-Fetch-Site, Origin` to `Vary` on every API response except the preflight's,
  after the values already there,** because the Fetch Metadata check decides the answer from those
  headers (the W3C Fetch Metadata draft, section 5.1; OWASP's CSRF cheat sheet). No HTTP cache keeps
  a preflight answer (RFC 9110 section 9.3.7), and the browser's own preflight cache is keyed by
  origin and URL (the Fetch standard). The header list above already keeps these responses out of
  caches with `no-store`.
- **API: on the download route, send `Content-Disposition: attachment` with any file that came
  from outside,** so the browser saves it instead of showing it (MDN on `Content-Disposition`):
  shown inline as HTML or SVG, it would run as script on the API's origin, where its requests are
  `same-origin` and carry the session cookie past every check in this section.

#### Logging

- **BFF: when you set up the alerts below, write the person or channel that receives security
  advisories and alerts into the decision log ("Write it down" in section 6 says where), send one
  test alert to it, and send every alert below to it,** so every alert has a recipient who acts on
  it, even after people change roles, also in a client-rendered application that never reads
  section 8, and an alert path is not first tried in an incident; the rule is this practice's
  choice.
- **BFF: log at `INFO` ([logging.md](../../python/logging/logging.md) section 4) each request that
  a check rejects (the custom header, Fetch Metadata, `Origin`, the cookie name, a path format, a
  WebSocket's `Origin`) and each failed sign-in or re-authentication, with the check's name, the
  route and the `Origin` and `Sec-Fetch-Site` values,** so a CSRF probe, a planted cookie or an
  origin set up wrong leaves a trace. Each is an expected client error, which logging.md section 4
  keeps out of `WARNING`; the alert on the rejection rate below is what calls a person. OWASP's
  Logging cheat sheet asks to log authentication, access-control, session and input-validation
  failures, and ASVS 5.0 requirement 16.3.3 asks to log attempts to get past a security control;
  what never goes into a log is [logging.md](../../python/logging/logging.md) section 10.
- **BFF: cut each value that a rejected request supplies (the `Origin`, a cookie name, a path) to
  a fixed length before you log it,** so a probe cannot flood the log. OWASP's Logging cheat sheet
  asks to sanitise event data against log injection and to encode it for the log's format; where
  the value goes in the log line, and how the JSON formatter escapes it, is
  [logging.md](../../python/logging/logging.md) sections 3 and 6. The same holds for each field of
  a report that the report intake writes to a log.
- **BFF: alert a person when the rejections of one check pass a rate the team writes down ("Write
  it down" in section 6 says where),** since OWASP Top 10:2025 A09 says that without alerting a
  team can hardly respond quickly and effectively to an incident; the rule is this practice's
  choice.
- **BFF, with an identity provider: alert a person on every step-up whose `iss` or `sub` does not
  match (section 6),** since another account at the callback means the session may be in someone
  else's hands; the rule is this practice's choice.
- **BFF, with an identity provider: alert a person on every back-channel logout that could not end
  its session (section 6),** since Back-Channel Logout 1.0 leaves sending the logout request again
  to the provider (section 2.5) and names nothing the provider does after the BFF's `400` (section
  2.8), so the session may stay live until its timeouts; the rule is this practice's choice.
- **BFF, with an identity provider: alert a person when valid back-channel logout tokens that
  match no session pass a rate the team writes down,** since a BFF whose stored `sid` never
  matches leaves live every session the provider ended, and section 6 logs each such token at
  `INFO`, the level for what nobody will look at ([logging.md](../../python/logging/logging.md)
  section 4); the rule is this practice's choice.

### What the React code does

- **Send the custom header on every request to an API route, from the one API client,** except
  the requests the exemption table above names that the page sends: the login start, which the
  page opens by a top-level navigation, the `report` method's calls, the WebSocket handshake and
  a download link. A header such as `X-Requested-With` makes the
  browser send a CORS preflight first, and the server allows it only for the application's origin
  (`https://app.example.com`), so another site cannot send the request from a form (OWASP, item 4;
  RFC 10017 section 6.1.3.3.2, which recommends the header and, once it is used, asks for it on
  every request; MDN on which headers start a preflight). The reference API client is in section
  15 and in [security-example.md](security-example.md).
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
  past every defence in OWASP's list (Doyensec, 2024; CVE-2023-45316 in Mattermost). The query and
  mutation options in [layout-example.md](../architecture/layout-example.md) encode the route's
  `invoiceId` this way.

Encoding stops the slash, but it leaves `.` and `..` as they are, and the URL parser then resolves
them: `` `/invoices/${encodeURIComponent("..")}/payments` `` requests `/payments` (checked with
Node 20's URL parser, 2026-10-15).

- **Check the format of any value that does not come from the route's own path, against its
  schema, before you build the path,** such as the format of an invoice id (OWASP's CSRF cheat
  sheet, client-side CSRF). A path parameter the router reads from the page's own URL has lost its
  literal `.` and `..` segments, but not a `%2F` inside one, which the server's path rule above
  rejects; a value from a search parameter, a message, storage or a response has not lost them.
- **Put no token in the WebSocket URL's query string,** where logs keep it (OWASP's WebSocket
  Security cheat sheet; section 13).
- **When the page opens a WebSocket, add the socket's `wss://` origin, such as
  `wss://api.example.com`, to `connect-src` in the page's policy (section 5),** since a source
  written with `https://` does not match a `wss://` URL, so the reference policy would block the
  socket (CSP Level 3, "scheme-part matching", read 2026-10-16).
- **Page: when the server closes a WebSocket with its session-ended code, run the sign-out path,**
  since that code is the server's word that the session ended (the WebSocket rules in "What the
  server does"); the rule is this practice's choice.
- **Page: when a WebSocket closes with any other code, reconnect with a bounded backoff, and before
  each reconnect ask the API through the API client whether the session is still live,** since a
  handshake the server refuses reaches the page only as a close with code 1006, the code for a
  connection closed with no close frame, so the `401` rule of section 6 cannot fire for a socket
  (MDN's `CloseEvent.code` page; the WHATWG WebSockets Standard). The rule is this practice's
  choice.

### CORS

- **API: serve the API on the page's own origin, through a path such as `/api` on the same host,
  when the host allows,** so there is no CORS policy to get wrong. Such an API needs no CORS at
  all: no preflight for each new URL, no allowlist, and every request is `same-origin` to Fetch
  Metadata (RFC 10017 section 6.1.3.3.2; Duende's BFF docs). The API answers CORS only because the
  page and the API are on two origins; the rules below hold when the two are split, as in the
  example.

The API's CORS response headers:

| Header | Value | Why |
|---|---|---|
| `Access-Control-Allow-Origin` | the application's one origin, `https://app.example.com`, on every response the browser can get from the API's host, including one from a gateway or proxy in front of it | with credentials the browser refuses `*` (the Fetch standard); one fixed origin needs no `Origin` in `Vary` for CORS (next list). Without it, or without the next row's header, the page sees a network error instead of the status, so a `401` from a gateway never reaches the sign-out path (MDN's CORS errors page) |
| `Access-Control-Allow-Credentials` | `true`, on the same responses as the row above, the gateway's included | without it, the browser hides from the page any answer to a request that carried the cookie (the Fetch standard), a gateway's `401` included |
| `Access-Control-Allow-Methods` | the methods the API serves, such as `GET, POST` | with credentials, `*` is a literal name, not a wildcard (the Fetch standard); listing them keeps the policy to what is used |
| `Access-Control-Allow-Headers` | `Content-Type, X-Requested-With`, and the header that carries the framework's CSRF token, where the server issues one | the JSON body and the custom header start the preflight (MDN); the same `*` rule holds |
| `Access-Control-Max-Age` | `7200` | the browser caches a preflight answer per URL, for 5 seconds without this header; with it, repeat calls to the same URL skip the preflight, but every new URL (each record id, each query string) still waits for one (the Fetch standard); Chromium caps the value at 7200, Firefox at 86400 (MDN, read 2026-10-15) |
| `Access-Control-Expose-Headers` | only the response headers the page reads, often none | each listed header becomes readable by scripts on the allowed origin (MDN) |

- **API: with more than one allowed origin, compare the request's `Origin` with the list by exact
  string, and copy it back only on a match.** Copying the origin back unchecked is the most common
  CORS flaw (James Kettle, PortSwigger, 2016; ASVS 5.0 requirement 3.4.2).
- **API: never match an origin by suffix, prefix or regular expression.** A suffix check lets
  `evil-example.com` through, and a prefix check lets `example.com.evil.net` through
  (PortSwigger's Web Security Academy, its CORS page, read 2026-10-16).
- **API: never allow every subdomain.** A subdomain on the list is as safe as its weakest page: an
  XSS there reads every answer (James Kettle, PortSwigger, 2016).
- **API: never allow `null`.** It is the origin of any sandboxed frame an attacker builds (James
  Kettle, PortSwigger, 2016; MDN).
- **API: when the allowed origin depends on the request, add `Origin` to `Vary`, and never replace
  the `Vary` values already there.** Without it, a cache can hand one origin's answer to another; a
  CORS layer that overwrote `Vary: Cookie` with `Vary: Origin` let a CDN serve one user's data to
  another (Netty, CVE-2026-59903). With one fixed origin, CORS needs no `Origin` in `Vary`, so send
  `Access-Control-Allow-Origin` on every response (the Fetch standard, section "CORS protocol and
  HTTP caches").
- **API: answer the preflight without the session and without the custom-header check; the
  preflight handler changes nothing.** A preflight `OPTIONS` request never carries the cookie, and
  it names the custom header in `Access-Control-Request-Headers` instead of sending it (the Fetch
  standard), so an `OPTIONS` route behind the session check or the header check fails every request
  it should allow.
- **API: do not count CORS as a CSRF defence, and keep it tight because of CSRF.** It loosens the
  same-origin policy for the origins it names; it does not stop a form that another site submits
  (MDN). A loose policy also lets other origins send JSON with the cookie and read the answer, which
  turns a CSRF that the preflight would have blocked into a working attack (Chen et al., USENIX
  Security 2018).

Bad: the request's `Origin` copied back with no check. The request comes from a browser that sends
no Fetch Metadata, or reaches a server where another check is missing: a page on
`evil.example.com` fetches an invoice's PDF from the download route with the user's cookie, a
`GET` with no custom header, which needs no preflight. The other headers section 7 asks of this
route's answers are left out, and the body, the PDF, is cut as `…`.

```http
GET /invoices/inv_123/pdf HTTP/1.1
Host: api.example.com
Origin: https://evil.example.com
Cookie: __Host-Http-session=…

HTTP/1.1 200 OK
Content-Type: application/pdf
Access-Control-Allow-Origin: https://evil.example.com
Access-Control-Allow-Credentials: true

…
```

The browser hands this answer to the page on `evil.example.com`. What the reflected origin opens
is reading: where no other check stops the request, as in a browser that sends no Fetch Metadata,
a page on any sibling subdomain can `fetch` a route such as the download link with the user's
cookie, and read the answer.

Good: the same request, and the API's answer with its one fixed origin. The other headers and the
body are left out as in the Bad. HTTP has no comment syntax, so each line's reason is in the table
above, and for `Content-Type` in the header rule of "What the server does"; that is this example's
one departure from [readability.md](../../any-language/readability/readability.md) section 4; the
cost: the block copied alone carries none of those reasons, so copy the table with it.

```http
GET /invoices/inv_123/pdf HTTP/1.1
Host: api.example.com
Origin: https://evil.example.com
Cookie: __Host-Http-session=…

HTTP/1.1 200 OK
Content-Type: application/pdf
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true

…
```

It fixes the one problem: the answer names `https://app.example.com` whatever origin asked, and
the API sends that one origin on every response (the header table above), so the browser lets no
page on a sibling subdomain, such as `evil.example.com`, read an answer sent with the user's
cookie, even where no other check stops the request, as in a browser that sends no Fetch
Metadata. Why the other lines hold is in the same table.

### Fixing a CORS error

- **Fix a CORS error on the server, or behind a proxy you run; never in the page.** MDN says most
  CORS errors can be fixed only on the server (read 2026-10-15).
- **The page never sets `mode: "no-cors"`:** the answer comes back opaque, with status 0 and a
  body no script can read (MDN; the Fetch standard).
- **The page never sends an `Access-Control-Allow-*` header:** it is a response header, and on a
  request it is one more header outside the safelist, which starts a preflight (the Fetch
  standard).
- **The page never sends requests through a public CORS proxy:** the proxy reads every request and
  answer, tokens and keys included. No leak through such a proxy is documented; the risk is the
  design, so the rule is this practice's choice.
- **A proxy you run forwards only to the hosts on the BFF's allowlist (section 6), never to a URL
  the request names.** A proxy that forwards anywhere is server-side request forgery, which OWASP
  Top 10:2025 counts under A01 (CVE-2020-36851 in cors-anywhere).
- **Page: when development calls a real API on another origin instead of MSW handlers
  ([libraries.md](../architecture/libraries.md) section 6), send the API calls through Vite's
  `server.proxy`, under a path prefix that no page route uses,** so the page's calls reach the API
  as `same-origin` (Vite's docs), and the proxy never catches a navigation to one of the page's
  own routes. What the development instance accepts is the rule on the one setting of allowed
  origins, in "What the server does" above. The dev server's own rules are section 11.

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
  advisories and alerts is in the decision log (section 7, the first rule under "Logging"), so the
  advisories of React, the framework and the router reach them on the day they are published.
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
- **With the session's state in the cookie, only the list of ended sessions stops a copy of the
  cookie at once;** without it, how long a copy works depends on the revocation and the timeouts
  of section 6.
- **With the session's state in the cookie, a refresh whose answer never reaches the browser,**
  such as one for a cancelled query or a dropped connection, loses its `Set-Cookie`: the browser
  keeps the old refresh token, and when its next request comes after the provider's reuse window,
  that request counts as reuse and the user is signed out (section 6, "Timeouts and refresh").
- **A back-channel logout that the BFF cannot carry out,** because its session store cannot be
  written, can leave the session live until its timeouts; only the `ERROR` line of section 6 and its
  alert (section 7, "Logging") show it.
- **A login start that arrives from another site,** such as a link in an email, carries no
  `Strict` session cookie, so the BFF cannot record the old session id, and the old session lives
  on until its own timeouts or its logout (section 6, "A new session id at login").
- **Another site can still send the user to the login start by a top-level navigation,** which the
  `Sec-Fetch-Dest` check of section 6 lets through; in a browser that sends no Fetch Metadata, the
  check does not stop an image or a frame either, whose login cookie a browser that follows the
  cookie spec stores only with `response_mode=form_post` (section 6). Each such request starts a
  login attempt; the cap on login cookies keeps their number small, but it can push out the cookie
  of an attempt the user started, whose sign-in then has to start again.
- **Where other applications or user content share the application's site (section 7, "CSRF"), a
  sibling subdomain can lock a user out:** a cookie it plants that the cookie checks of section 6
  refuse makes every request of that user answer `400` until the cookie expires or the user clears
  the site's data. This practice accepts that trade, since reading a planted value instead would
  let the attacker choose the session. GitHub (2013) took a third way: the server answers with a
  `Set-Cookie` that expires the planted cookie, once for each part of the path. This practice does
  not ask for it, since no source read for it shows which browsers delete a cookie whose name is
  not a token, such as one that starts with U+2000, and GitHub writes that a cookie overflow
  cannot be blocked that way from the server.
- **A browser that stores a cookie with an empty name whose value starts with `__Host-`** sends
  only its value in the `Cookie` header, such as `__Host-Http-session=<id>`, which the server
  cannot tell from the real cookie. The RFC 6265bis draft asks browsers to ignore such a
  cookie (section 5.7), and Firefox fixed it in Mozilla bug 1779993 (read 2026-10-16); which other
  browsers ignore it was not checked.
- **A framework that decodes or rewrites cookie names** can read a planted cookie as the session
  cookie although its name passes the check of section 6: PHP URL-decoded cookie names before
  7.2.34, 7.3.23 and 7.4.11 (CVE-2020-7070), and parsed a name that starts with `_[Host-` as
  `__Host-` before 8.1.28, 8.2.18 and 8.3.6 (CVE-2024-2756, PHP's advisory GHSA-wpj3-hf5j-x4v4).
  Keep the framework patched (section 10).
- **A BFF on another registrable domain** sets a third-party cookie, which Firefox and Safari block
  by default and Chrome lets users block (MDN's third-party cookies guide, read 2026-10-15). The
  cookie rules of section 6 assume the BFF shares the application's site, as `api.example.com` does;
  `Partitioned` does not change that, since it keeps a cookie to the site that embeds the frame.
- **Pages the server renders read the session on navigations from other sites,** such as a link
  in an email, so their session cookie takes `Lax` instead of `Strict` (section 6).
- **A first-party login's credential checks** are outside this practice: password storage,
  protection against automated attacks on the login itself, such as login throttling (section 6
  limits only the failed answers to a step-up), and one generic message for a failed sign-in.
  OWASP's Authentication and Password Storage cheat sheets are where to look.
- **A team at ASVS Level 1, or one whose identity provider holds the email, the phone, the second
  factor and the recovery data and asks for re-authentication itself,** may skip the step-up rules
  of section 6's "Re-authentication", which serve the Level 2 requirement 7.5.1, and writes the
  choice down.
- **Five Level 2 session requirements of ASVS 5.0** are left to a team that works at that level
  (section 17). The session rules of section 6 cover the Level 1 requirements of ASVS 5.0 chapter
  V7 and the Level 2 requirements they cite. They leave out 7.1.2, the number of sessions one
  account may hold; 7.4.5, an administrator ends one user's sessions or all of them; 7.5.2, users
  see and end their own sessions; 7.6.1, the application's and the provider's sessions end as
  documented, with the user signed in again where needed, beyond the choice section 6 asks to
  write down; and 7.6.2, a new session starts only with the user's consent or an explicit act.
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

A review question per section; sections 6 and 7 each get one row for the page and one for the
server. OWASP's ASVS 5.0, chapter V3 "Web Frontend Security", is the longer
checklist for the same ground. Each red flag is a way in, so one red flag is enough to stop the
merge until it is fixed or the author shows why it does not apply; that bar is the practice's
choice.

| Section | Ask | Red flag |
|---|---|---|
| 2. What the browser can protect | Does the server check this request on its own? | a permission enforced only by hiding a button or a route |
| 3. XSS | Can a value from outside reach HTML, a URL, a props object, a style or code? | a URL from data with no scheme allowlist; outside data spread as props; a renderer's `urlTransform` overridden |
| 4. Sanitising | Is the HTML sanitised in the sink's own render? | a second `dangerouslySetInnerHTML`; a sanitised string changed or joined after cleaning |
| 5. Headers | Does the built page run under a policy with no `'unsafe-inline'` in `script-src`? | `'unsafe-inline'` or `data:` in `script-src`; a policy only in `<meta>`; a nonce in a cached response; a check or a policy still log-only after its written end |
| 6a. Sessions, page | Can script read anything that grants access? | a token or session id in `localStorage`, `sessionStorage` or a cookie set by script; a cookie the page sets without `Secure`, a written `SameSite` or a `__Host-` or `__Secure-` prefix; `refetchInterval` on data that needs the session, unless the BFF leaves those requests out of its idle clock |
| 6b. Sessions, server | Does the server end the session at logout and on timeout? | a callback page that shows a parameter of the request; a session cookie or login cookie without the `__Host-Http-` prefix; a session cookie without `Secure`, `HttpOnly` or a written `SameSite`, or with `Domain`; a session or login cookie read without checking that its name appears once; a cookie whose name becomes the session or login cookie's name once non-token characters are removed and ASCII letters are lowercased, read instead of answered with `400`; a `Cookie` header that starts with `$Version` accepted; the same session id before and after login; a logout that only deletes the cookie; a session that a late request can save back after logout; a timeout kept only in the page; a session accepted when the session store or the list of ended sessions cannot be read; a step-up that does not compare `iss` and `sub`; a step-up without the `auth_time` check, or not bound to its change and to its session; a step-up check against a login-cookie value that is neither protected nor kept on the server; a WebSocket that stays open after logout; a BFF route that forwards to a host or path taken from the request |
| 7a. CSRF and CORS, page | Does each request to an API route carry the CSRF defence, and does the page fix CORS errors and build API paths as section 7 says? | `mode: "no-cors"` or a public proxy in the page; a value from outside put into an API path unchecked; a request to an API route, other than the exempt ones in section 7, made outside the one API client or without the custom header, or without `credentials: "include"` when the API is on another origin; a blob made with the response's own type, or an SVG blob |
| 7b. CSRF and CORS, server | Does the API allow only exact origins, change no user data or session on a `GET`, and exempt only the endpoints section 7 lists? | a change to the user's data or session on a `GET` other than the login start or the login callback, which creates the session or applies a step-up's change; `Access-Control-Allow-Origin` copied from the request unchecked, matched by suffix or pattern, `null`, or `*` with credentials; a Fetch Metadata check that allows every `same-site` request; a WebSocket handshake with no `Origin` check; an API route that accepts a request without the custom header; a dynamic path segment not checked against its format; a CSRF exemption by request mode, by a missing header or by path prefix; a file from outside served inline on the download route; a check or a policy still log-only after its written end; a rejected check, a failed sign-in or re-authentication, or a session that could not be ended, with no log line; no alert on the rejection rate or on a step-up from another account |
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
  write it into the decision log ("Write it down" in section 6 says where),** so reviews and tests
  know the target; writing it down is this practice's choice. OWASP's Application Security
  Verification Standard (ASVS 5.0, read 2026-10-16) has three levels: Level 1 holds "the minimum
  requirements to consider when securing an application", Level 2 is the level "most applications
  should be striving to achieve", and Level 3 is for applications that must show the highest level
  of security.
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
| A01 Broken Access Control | the server decides every access; the page hides what the user cannot use, for the user's sake. OWASP counts CSRF, CORS mistakes and server-side request forgery here | 2, 7, 8 |
| A02 Security Misconfiguration | headers, cookie attributes, the CORS policy and the dev server are configuration | 5, 6, 7, 11 |
| A03 Software Supply Chain Failures | the packages you install, the lockfile and the CI workflow | 10 |
| A04 Cryptographic Failures | mostly the server's: HTTPS, HSTS and no caching of responses with personal data; the browser side keeps secrets out of the bundle; password storage for a first-party login is outside this practice (section 16) | 5, 9, 13 |
| A05 Injection | XSS is injection into the page; the server checks the format of each path segment and of each report (section 7); injection into the server's own interpreters, such as SQL or an OS command, is outside this practice | 3, 4, 5, 7 |
| A06 Insecure Design | a check in the page helps the user and protects nothing; the design puts every control on the server, and the session in a BFF; OWASP asks to model the threats of critical flows such as sign-in and access control (the threat-modelling step above) | 2, 6 |
| A07 Authentication Failures | mostly the server's: the OAuth flow, a new session id at login, timeouts, logout and re-authentication; the browser side holds no token and runs the sign-out path on a `401`; a first-party login's password storage, throttling and sign-in error messages are outside this practice (section 16) | 6 |
| A08 Software or Data Integrity Failures | scripts from other origins, Subresource Integrity, and state the server writes into the page; an object from outside spread as props (section 3); the session's state in a signed and encrypted cookie (section 6); the arguments of a Server Function (section 8) | 3, 6, 8, 10, 12 |
| A09 Security Logging and Alerting Failures | mostly the server's: it logs security events, and alerts a person when the rejections of one check pass their written rate and on every step-up from another account; the browser side keeps credentials out of its own reports | 6, 7, 13 |
| A10 Mishandling of Exceptional Conditions | mostly the server's: it fails closed; the browser side shows a message of its own on a failed screen, never the error's text | 6, 13 |

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
| the parts of source 36 that section 7 quotes (the case for tokens and the `Origin` fallback) | as raw text | yes | 2026-10-16 |
| 134 to 136 | as raw text | no | 2026-10-16 |
| 112 to 117, 120 to 123, 128 and 129 | as raw text | no | 2026-10-16 |
| 130 to 132; the pages at the URLs of sources 103, 105 and 106; the parts of sources 93, 97 and 100 that section 6 cites for login cookies, the `$Version` header and logout | as raw text | no | 2026-10-16 |
| 9, 76 and 133; the parts of sources 6, 82, 100, 106 and 115 that sections 6 and 7 cite for the page's cookies, log fields, the logout redirect, the callback's error page and the WebSocket close codes | as raw text | no | 2026-10-16 |
| 91 to 107, apart from the parts above | through a summarising tool | no | 2026-10-15; the pages at the URLs of 96 and 107 on 2026-10-16 |
| 108 to 111, 118, 119 and 124 | through a summarising tool | no | 2026-10-16 |
| 137 to 140 | through a summarising tool | no | 2026-10-16 |
| 141 and 142; the part of source 100 that section 7 cites for a logout request sent again (2.5) | as raw text | no | 2026-10-16 |
| 143 | as raw text | yes | 2026-10-16 |
| 144 and 145; the parts of sources 35 and 93 that sections 6 and 16 cite for local development and a cookie with an empty name | as raw text | no | 2026-10-16 |
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
