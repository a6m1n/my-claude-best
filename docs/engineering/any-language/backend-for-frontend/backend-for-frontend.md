# Backend for Frontend

**Navigation**

- [1. Purpose and scope](#1-purpose-and-scope)
- [2. Sessions and tokens](#2-sessions-and-tokens)
- [3. CSRF and CORS](#3-csrf-and-cors)
- [4. Choosing a library or framework](#4-choosing-a-library-or-framework)
- [5. Where the rules stop holding](#5-where-the-rules-stop-holding)
- [6. Review checklist](#6-review-checklist)
- [7. Sources](#7-sources)

## 1. Purpose and scope

A browser application that signs users in has to keep its session somewhere. When the page holds
the OAuth tokens, a script injected into the page can read them and send them to its own server
(RFC 10017 section 5.1.1) [1]. These rules keep the tokens on a server, the Backend for
Frontend (BFF) of RFC 10017 section 6.1: the application's confidential OAuth client, which keeps
the tokens in a cookie-based session and forwards each API call to the resource server with the
user's access token, so the browser holds only a session cookie that script cannot read
[1]. A team that follows them has a BFF whose session cookie no script on the page can
read and no sibling subdomain can plant, whose sessions end on the server at logout, at their
timeouts and at the provider's back-channel logout, whose keys rotate without signing users out,
and whose API refuses the requests that other sites make the user's browser send.

The rules are for the team that builds or runs that server, whether it writes the session, cookie
and key handling itself or takes them from a library or a framework, and for the reviewer of a
change to it. A library can get a rule wrong, so section 4 turns the rules into questions to ask
a library before the team picks one. The page's own rules are in
[security.md](../../react/security/security.md), whose sections 6 and 7 open with what a BFF is
and what "the server", "the API" and "an API route" mean here.

One rule holds the rest together: the session cookie is the only thing the browser holds, and a
request that carries it may come from someone other than the user. Another site can make the
browser send it, and a script on the page sends it like the page's own code (RFC 10017 sections
5.1.4 and 6.1.3.3) [1]. A sibling subdomain can set a cookie under its name (the RFC
6265bis draft, section 8.6) [2]. So the cookie rules keep the cookie from being read
or planted, the session rules end the session on the server, and the CSRF and CORS rules check
each request before the BFF serves it.

Use a BFF when the application signs users in with OpenID Connect or OAuth, calls APIs with the
user's access token, and is a business application, a sensitive one or one that handles personal
data: RFC 10017 section 6.1.4.3 strongly recommends the BFF for these [1]. The choice
between the BFF and the RFC's two other patterns is
[security.md](../../react/security/security.md) section 6. The BFF has a cost that lasts as long
as the application runs. RFC 10017 section 6.1.4.3: "The architecture of a BFF is significantly
more complicated than a browser-only application. It requires deploying and operating a
server-side BFF component" [1]. Since every call to a resource server goes through it,
this proxy behaviour "can add a significant burden on the server-side components", as the same
section says [1].

A BFF is more than the application needs when its page calls only the API of its own server, on
the same site, and the server calls no other API with the user's token. RFC 10017 section 7.1
says that "simple applications are made needlessly complex by using OAuth to replace the concept
of session management", and that such an application "can rely on server-side cookie-based
session state" instead of access tokens [1]. That is the simpler way. Its server still
sets a session cookie, so the rules here hold for it, apart from the rules on forwarding and on
refresh tokens, which hold only where a server keeps tokens to call other APIs. A server that
signs users in itself, with no identity provider, is such a server, and the opening of
[security.md](../../react/security/security.md) section 6 says which of these rules it skips. An
application that signs nobody in has no session to keep, and none of these rules applies to it.

Some topics are outside this practice on purpose: the page's side, and the choice of a pattern,
are [security.md](../../react/security/security.md). These are not covered yet: a silent login run
in an iframe, which the login start refuses (section 2, "The login cookie"); caps on the size and
number of WebSocket messages and connections; throttling of sign-in attempts, with the rest of a
first-party login's credential checks such as password storage, which a practice on
authentication would own; and rate limiting or anomaly detection on the requests that a script on
the page sends through the BFF, for which RFC 10017 section 6.1.4.1 calls the BFF "the ideal
place" [1]. Section 5 says where the rules that are here stop holding.

## 2. Sessions and tokens

### The session cookie

The session cookie the BFF sets:

| Attribute | Value | Why |
|---|---|---|
| name prefix | `__Host-Http-` (RFC 10017 section 6.1.3.2, which takes it from the IETF's layered-cookies draft) [1] | a browser that enforces the prefix accepts the cookie only with `Secure`, `HttpOnly`, `Path=/` and no `Domain`, so neither a script on the page nor a sibling subdomain can set a cookie under that name [3], [4]. Chrome, Edge and Firefox enforce it; Safari 27 enforces it neither on `Set-Cookie` nor on `document.cookie`, so there a script on the cookie's own host can set a cookie under that name; it applies only the `__Host-` rules, which the name also matches [5], [6]. Safari 27 also matches the prefix case-sensitively (its `__HoSt-` tests fail), so it applies no prefix rule to `__HOST-HTTP-SESSION`, and it stores a `__Host-` cookie set with no `Path` attribute (wpt.fyi, the stable aligned run of 2026-10-06) [6] |
| `Secure` | set | sent over HTTPS only [2] |
| `HttpOnly` | set | `document.cookie` cannot read it, and `fetch` still sends it [4] |
| `Path` | `/` | the `__Host-` rules ask for it; a path is no security boundary, since other pages on the host can still reach the cookie (RFC 6265bis draft, section 4.1.2.4) [3], [2], [4] |
| `Domain` | not set | without it the cookie goes back only to the host that set it; with it, every subdomain receives the cookie and can overwrite it (the cookie spec's "Weak Integrity" section, RFC 6265bis draft, section 8.6) [2], [4] |
| `SameSite` | `Strict`, written out | RFC 10017 section 6.1.3.2 asks for `Strict` [1]. Left out, the default differs by browser: `Lax` in Chromium, none in Firefox and Safari [7], [8] |
| `Max-Age` | not set: a non-persistent cookie | the server's idle and absolute timeouts end the session (section 2, "Timeouts and refresh"). A cookie with `Max-Age` is persistent, and the browser keeps it on disk through every close; one without it ends with the browser, though a browser that restores its last session brings it back, so the timeouts stay the control [8], [4]. Set `Max-Age`, no longer than the absolute timeout, only when the product needs the session to survive a browser close |
| `Partitioned` | not set | it stores a cookie that content embedded from another site sets in a separate cookie jar for each top-level site (CHIPS); the application's own session cookie is no such cookie [4], [9] |

- **BFF: name the cookie `__Host-Http-session` and still write `Secure`, `HttpOnly` and `Path=/`
  yourself, and leave out `Domain`,** because Safari 27 does not enforce the `Http` part, and
  stores a `__Host-` cookie set with no `Path` attribute (the table's first row)
  [6].
- **BFF: use `SameSite=Lax` instead only when the server reads the session on a top-level navigation
  that can arrive from another site,** such as a page the server renders, opened from a link in an
  email, or the first page after the identity provider sends the user back, since `Strict` keeps
  the cookie off those requests [10]. OWASP's Session
  Management cheat sheet allows `Lax` for session cookies [8]. Duende's
  BFF sample uses `Lax`, and recommends `Strict` when the provider is on the same site as the BFF
  [11]. Duende's docs give the reason: with `Strict` and a provider on
  another site, the browser leaves out the cookie set after the sign-in until the user reloads the
  page, so the user looks signed out [12].
- **BFF: keep `Strict` for a single-page application whose first page after the callback is a
  static file that reads no session,** since a `Strict` cookie set on the login callback is stored
  (RFC 6265bis draft, section 5.7), and the page's later `fetch` calls to the API are same-site, so
  they carry it (the same draft's "site for cookies" rules) [2].
- **BFF: keep the session cookie's name and attributes the same in every environment, never behind
  a setting, and develop on `http://localhost` or on local HTTPS,** since a setting that turns
  `Secure` off for development can ship to production. MDN's `Set-Cookie` page says the `https:`
  requirement of `Secure` is ignored when localhost sets the cookie, and its compatibility data
  says Safari does not send a `Secure` cookie to `http://localhost`, so Safari needs local HTTPS
  [4], [7]. The rule is this practice's choice.

### The login cookie

For the first login, these rules are checks on the OpenID Connect library you use; write code only
for a rule it does not meet.

- **BFF: give the short-lived login cookie (the `state`, the nonce, the PKCE verifier) the session
  cookie's name prefix and attributes:** name it with `__Host-Http-`, write `Secure`, `HttpOnly`
  and `Path=/`, and leave out `Domain`. Without the prefix, a sibling subdomain could set a cookie
  under the same name with its own `state` and verifier and sign the user into the attacker's
  account. OWASP's CSRF cheat sheet names the two parts: a cookie without the `__Host-` prefix can
  be overwritten from another subdomain, and login CSRF signs a victim into the attacker's account
  [10]. Their use against `state` and the verifier is this
  practice's reading.
- **BFF: name the login cookie per attempt, `__Host-Http-login-<id>`, with the id carried in
  `state`,** so a login started in another tab does not overwrite this one's cookie and fail its
  callback. ASP.NET Core names its correlation cookie per attempt in the same way [13].
  The rule is this practice's choice.
- **BFF: where your own code, not the OpenID Connect library, creates an attempt's `state`, nonce
  or PKCE verifier, draw each from a secure random source, the verifier from 32 random bytes, and
  send its challenge with `S256`,** since RFC 7636 section 7.1 asks for a verifier "with a minimum
  of 256 bits of entropy" [14]. RFC 6749 section 10.12 says that the binding value used for
  CSRF protection "MUST contain a non-guessable value" [15]. RFC 9700 section 2.1.1 asks for
  a challenge method that does not expose the verifier: "Currently, S256 is the only such method"
  [16]. ASVS 5.0 requirement 10.1.2 asks these values to be "not guessable" and "specific
  to the transaction" [17].
- **BFF: keep what a login attempt records, a step-up's included, where the user can neither change
  nor read it: in the login cookie's value, or in `state` when the library keeps it there,
  encrypted and signed with authenticated encryption from a vetted library, the framework's own
  data protection where it has one, under the key rules for every cookie the BFF signs or encrypts
  (section 2, "Keys and secrets"), and never in a record on the server,** since a person at the
  browser can edit any value that is not protected
  ([security.md](../../react/security/security.md) section 1's one rule). RFC 9700 section 4.7.1
  asks a client to protect `state` "against tampering and swapping", by binding it to the browser
  session or by "signing/encrypting state values" [16]. RFC 7636 section 7.1 adds that the
  PKCE verifier must not be "learned or guessed by the attacker" [14]. ASP.NET Core keeps
  the record, the verifier included, in the encrypted `state`, and binds it to the browser with a
  per-attempt cookie [18], [13]. A record kept on the server
  for each login start would let a caller add one per request, with a session or without one: the
  garbage-data creation that ASVS 5.0 requirement 2.4.1 names [17].
  OWASP's CSRF cheat sheet offers the other choice, pre-sessions, "sessions before a user is
  authenticated" that hold the login's tokens [10]. The
  rule is this practice's choice.
- **BFF: at the callback, read the attempt's values, such as the time it started, only from that
  protected record,** so an edited value never passes a check; the rule is this practice's choice.
- **BFF, with more than one identity provider: record in the attempt's protected record the issuer
  the authorization request went to, and at the callback reject a response whose `iss` parameter
  differs from it; with a provider that sends no `iss`, give each provider a callback path of its
  own and check the path instead,** since RFC 9700 section 4.4.2 says that a client that talks to
  two or more authorization servers "MUST store, for each authorization request, the issuer they
  sent the authorization request to and bind this information to the user agent" [16].
  RFC 9207 section 2.4 adds that when the value "does not match the expected issuer identifier,
  clients MUST reject the authorization response" [19]. RFC 9700 section 4.4.2.2 allows a
  distinct callback path for each provider as the alternative [16]. The ID token's `iss`
  does not replace this check in the code flow: that token arrives only after the code has gone to
  the token endpoint, and RFC 9700 section 2.1 asks for an `iss` value "in the authorization
  response" [16].
- **BFF: give the login cookie a `Max-Age` long enough for the user to finish at the provider, such
  as 15 minutes, and delete it at every callback, whether the sign-in succeeds or fails, a callback
  that carries an `error` from the provider included,** since it is needed only between the login
  start and the callback, and the user may enrol a second factor on the way. RFC 9700 section 4.2.4
  asks that "The state value SHOULD be invalidated by the client after its first use at the
  redirection endpoint" [16]. A cookie left behind adds to the login cookies that every
  request carries: in the open dotnet/aspnetcore issue 53048, a team reports that ASP.NET Core
  keeps its correlation and nonce cookies after a callback with `error=login_required`, and that
  "Around 4 or 5 navigations to the site without being logged in, within a 15 minute window, will
  cause the errors to occur" [20]. 15 minutes is ASP.NET Core's default for a remote
  sign-in, its `RemoteAuthenticationTimeout` [13].
- **BFF: when you set a login cookie, write the time its attempt started into the cookie's value,**
  so the next rule can tell which login cookies are newest: a `Cookie` header carries only each
  cookie's name and value, and section 4.2.2 of the cookie spec, the RFC 6265bis draft, tells
  servers not to rely on the order of the cookies in it [2]. The rule is this practice's
  choice.
- **BFF: at the login start, expire every login cookie the request carries that none of the cookie
  keys every instance shares can read, then every other one beyond the two with the latest start
  times in their values,** so login cookies cannot pile up until the `Cookie` header passes the
  server's size limit, and a cookie no callback can use, such as one written under a key since
  removed, never fails the login start or keeps a place in the two. The prefix asks for `Path=/`,
  so every login cookie rides every request to the API's host, not only the callback. ASP.NET
  Core, whose per-attempt cookie this practice follows, has the pile on record: in
  dotnet/aspnetcore issues 58731 and 53048, users report that its correlation and nonce cookies
  built up until requests failed, in issue 58731 with nginx's `400` "Request Header Or Cookie Too
  Large" [21], [20]. The RFC 6265bis draft asks servers, in section 6.1,
  to "use as few and as small cookies as possible", and warns in section 8.6 that many cookies can
  force the browser to evict others [2]. Microsoft's ASP.NET Core docs on key
  management say that a deleted key leaves the data it protected "permanently undecipherable"
  [22]. The rule, a cap of two, is this practice's choice.
- **BFF: refuse a login start whose `Sec-Fetch-Dest` header is present and is not `document`, and
  let a request without the header through,** so in a browser that sends Fetch Metadata, an image
  or a frame on another site cannot start a login; only a top-level navigation can
  [23]. RFC 10017 section 6.1.2.1 has the browser reach the login endpoint
  "through a navigation" [1]. With `response_mode=form_post`, such a request would store
  the `SameSite=None` login cookie, while a browser that follows the cookie spec ignores a `Lax`
  login cookie that such a request sets, by section 5.7 of the RFC 6265bis draft [2].
  So the refusal is the guard for `form_post` and a second guard for `query`. web.dev's Resource
  Isolation Policy, a Google guide, lets a request without Fetch Metadata through too, since not
  every browser sends these headers [24]. What the check lets through, a
  top-level navigation from another site and any request from a browser that sends no Fetch
  Metadata, is in section 5, "Where the rules stop holding". The W3C Fetch Metadata draft asks
  servers to ignore a value it does not define, "to support forward-compatibility with
  as-yet-unknown request types"; this rule refuses such a value instead, since the same draft
  gives every top-level navigation the destination `document`, so no new value can be a login
  start [25]. The rule also refuses a silent login run in an
  iframe, which Duende BFF 4 starts by loading its login endpoint with `prompt=none`
  [26]. A team that adds silent login gives it a path of its own, which this
  practice does not cover yet (section 1). The rule is this practice's choice.
- **BFF: at a callback whose login cookie is missing, cannot be read, or does not match the
  `state`, log the reason and answer a page that offers to sign in again,** so the user has a way
  on instead of a dead end: a login cookie that expired, that another browser holds, or that was
  written under a removed key leaves the callback nothing to check. ASP.NET Core throws "An error
  was encountered while handling the remote login." on a failed callback that no handler takes
  [13]. The rule is this practice's choice.
- **BFF: give the page that a failed login callback answers with fixed text, and put no parameter
  of the request into it,** such as `error`, `error_description` or `state`, since those come from
  outside and the page is served from the API's origin, which holds the session cookie. They are
  the parameters of the provider's error response in RFC 6749 section 4.1.2.1 and OpenID Connect
  Core 1.0 section 3.1.2.6 [15], [27]. The rule is this practice's choice.
- **BFF: set the login cookie's `SameSite` by the callback's `response_mode`:** `Lax` when the
  identity provider returns with `response_mode=query`, a top-level `GET`; `SameSite=None; Secure`
  with `response_mode=form_post`, a cross-site `POST` on which neither `Lax` nor `Strict` cookies
  are sent, by section 5.8.3 of the RFC 6265bis draft [2]. Microsoft's ASP.NET Core
  docs say that "The POST based redirects trigger the SameSite browser protections, so SameSite is
  disabled for these components" [28]. Duende's BFF sample uses `query`
  [11]. A `Lax` login cookie stays off cross-site subresource requests and
  cross-site `POST`s, but still rides every cross-site top-level `GET` navigation to the API's
  host, not only the callback, by the same section [2]. RFC 9700, in sections 4.2.4 and
  4.3.1, names `form_post` as a countermeasure against a code that leaks through the `Referer`
  header or the browser history [16]. So choosing `query` for its `Lax` cookie is a trade;
  write the choice down.

### Reading the `Cookie` header

- **BFF: when an advisory names your server framework, its session and cookie library or its
  OpenID Connect client library, update it under [security.md](../../react/security/security.md)
  section 10's advisory path,** which covers the BFF's own repository too. The browser checks the
  prefix; a server that parses the `Cookie` header in another way can read a cookie the browser
  treated as a different one [29]. PortSwigger's research
  (2025) got past the `__Host-` and `__Secure-` prefixes on several server frameworks through such
  differences [29].
- **BFF: read the session cookie and the login cookie only when the raw `Cookie` header holds the
  cookie's exact name once, compared byte for byte, and answer `400` when it holds the name more
  than once,** so the server never has to choose between two values for one cookie, since the
  cookie spec tells servers not to rely on the order of two cookies with one name (RFC 6265bis
  draft, section 4.2.2) [2]. The raw header is every `Cookie` field line of the request
  joined with `; `, because HTTP/2 and HTTP/3 may split it into several (RFC 9113 section 8.2.3;
  RFC 6265bis draft, section 4.2.1) [30], [2]. For the login cookie the check
  runs on the raw header before the OAuth library reads it.
- **BFF: check each cookie name in the raw `Cookie` header in this order,** so a planted cookie
  whose name differs from the real one only by characters a token does not allow, or only in case,
  is never read under the real name:
  1. When the name is byte for byte the session cookie's name, or starts byte for byte with
     `__Host-Http-login-`, read the cookie under the rule above.
  2. Otherwise, remove from the name every character that a token does not allow (RFC 6265
     section 4.1.1), and lowercase its ASCII letters [31].
  3. When the result is `__host-http-session`, or starts with `__host-http-login-`, answer `400`.
  4. Otherwise, skip the name and never reject the request for it. Browsers store and send names
     that are not tokens: the cookie spec parses a name as everything before the first `=` "so as
     to interoperate with servers that do not follow the recommendations in Section 4" (RFC 6265
     section 5.2; RFC 6265bis draft, section 5.6) [31], [2]. Rejecting such
     a name would fail every request of the users who carry one.

  A sibling subdomain can set a cookie whose name starts with a Unicode space, such as U+2000
  [29]. The browser treats it as another cookie, outside
  the prefix rules [29]. Frameworks that trim cookie names,
  such as Django and ASP.NET, read it under the real cookie's name, often keeping the last of two
  values (PortSwigger's research, 2025) [29]. Django's
  `parse_cookie` strips each name with Python's `str.strip()` and keeps the last value
  [32]. A name in another case is a separate cookie to the browser, and the cookie
  spec warns that a server which matches names in any case can be fooled by it (RFC 6265bis draft,
  section 5.4) [2]. ASP.NET Core looks up request cookies by name in any case (its
  `RequestCookieCollection` source) [33]. Firefox before version 127
  ignored a prefix written in another case (CVE-2024-5699), and Safari 27 still does: it fails the
  `__HoSt-` tests (wpt.fyi, the stable aligned run of 2026-10-06) [34],
  [6]. So a sibling subdomain can plant
  `__HOST-HTTP-SESSION`. Whitespace, control characters, U+FEFF and every other non-ASCII character
  are outside the token set, so the check catches the name whichever trim function the framework
  runs.
- **BFF: answer `400` to a request whose `Cookie` header starts with `$Version`, and keep the
  server's cookie parser in its RFC 6265 mode,** so no server reads one cookie string as several.
  PortSwigger's research (2025) shows that Apache Tomcat and Jetty can switch to a legacy parser,
  so a cookie a sibling subdomain sets can carry a forged `__Host-` pair
  [29]. Tomcat 9 does so when the header starts with
  `$Version` (its `Cookie.java`; the 10.1 and 11.0 parsers have no legacy mode) [35].
  Jetty 12 does so only in its legacy compliance modes, where it reads `$` names anywhere in the
  header and, in its RFC 2965 modes, splits cookies at commas; its default is RFC 6265 (its
  `RFC6265CookieParser.java`, `CookieCompliance.java` and `HttpConfiguration.java`)
  [36]. The research gives a test, not a developer rule
  [29]. This rule and the name checks above are therefore
  this practice's choice, built on the cookie spec's sections 4.2.2, 5.4 and 5.6 [2].
  The advisory rule above them stays as the second control.
- **BFF: take the session cookie's value from the same parse of the raw `Cookie` header that ran
  the name checks, never from the framework's cookie collection: split the header at `;`, drop the
  one space the browser writes after it, and split each pair at its first `=`,** since that is how
  the browser writes the header (the layered-cookies draft, section 5.4.6), while a framework's
  parser can trim or fold the case of names, decode values or split cookies in its own way
  [3], [29],
  [33], [36]. The login cookie, which the
  OpenID Connect library reads, keeps the checks above as its control. The rule is this practice's
  choice.
- **BFF: check the session cookie's value against the format of the values the BFF writes, its
  length and its alphabet, before you look it up or decrypt it, and treat a value that fails as no
  session,** since the value comes from outside like any other input
  [8].
- **BFF: give every `400` that the cookie checks above answer to a request from the API client a
  JSON body with one fixed code, such as `cookie_conflict`,** so the page can tell the user how to
  get out; the rule is this practice's choice.
- **BFF: answer a failure on a route the browser reaches by navigation, such as the login start or
  a download link, with a page of fixed text that puts no parameter of the request into it,**
  since no page code runs on a navigation to read the status or a JSON body, and a parameter of the
  request comes from outside, as the rule on the failed callback's page in "The login cookie" above
  says. On a `401` the page links to the sign-in. On a `400` of the cookie checks above, the
  callback included, it tells the user to clear this site's data in the browser. The failed
  callback keeps its own page; the rule is this practice's choice.
- **BFF: where the team controls the registrable domain and accepts the cost to the other
  applications on it, send `Clear-Site-Data: "cookies"` with the `400` of the cookie checks,** so
  the browser removes the planted cookie without the user's help. The header removes every cookie
  whose domain matches the registered domain, a cookie a sibling subdomain set for `example.com`
  included [37]. Chrome 61, Firefox 63 and Safari 17 support it
  [38]. The cost: it also signs the user out of every other application on
  that domain. Write the choice down ("The session's life" below says where); the rule is this
  practice's choice.
- **BFF: where the team controls the registrable domain and every application on it can serve
  HTTPS, send `Strict-Transport-Security` with `includeSubDomains` from it and preload it,** so the
  browser reaches no host under it over plain HTTP, where a network attacker can answer and set a
  cookie for the whole domain (RFC 6265bis draft, section 8.6; RFC 6797 sections 8.3 and 12.3)
  [2], [39]. The cookie checks above stay, since a sibling subdomain can still
  plant a cookie. The cost: every host under the domain, those of other applications included, must
  then serve HTTPS (RFC 6797 section 11.4) [39]. Write the choice down; the rule is this
  practice's choice.

### The session's life, from login to logout

**Write it down** means two things in these rules: a choice, such as where the session's state
lives, goes into the project's decision log
([roles-and-decisions.md](../../any-language/project-management/roles-and-decisions.md) section
7), and a value, such as a timeout or a token lifetime, goes into the BFF's settings with its
reason next to it ([readability.md](../../any-language/readability/readability.md) section 4), so a
later reader finds why.

- **BFF: answer the session check, the "check session" endpoint of RFC 10017 section 6.1.2.1,
  with `200`, the user's display fields and no token when the session is live, and with `401` when
  there is none, and send it the headers of every API response (section 3, "Response headers"),
  `Cache-Control: no-store` among them,** so the page learns who is signed in without holding a
  token, and no cache keeps one user's answer for the next [1]. RFC 10017 section 6.1
  keeps tokens away from the page, and Duende BFF's user endpoint answers `401` with no session by
  default [1], [40]. The status codes are this practice's choice.
- **BFF: leave the session check out of the idle clock,** so a page that asks on every load, or
  before it reconnects a dropped WebSocket (section 3), does not keep an idle session alive; the
  rule is this practice's choice. NIST SP 800-63B-4 section 5.2 ends a session after a period
  "without activity from the subscriber", and a check the page sends by itself is not the user's
  activity [41]. Duende's BFF has a `slide=false` parameter so that a periodic call to
  its user endpoint does not slide the cookie [40]. OWASP's Session Management
  cheat sheet counts idle time from "the last HTTP request received by the web application"
  instead [8]. The rule follows NIST, since by OWASP's count a page
  that checks the session on a timer would never let it go idle.
- **BFF, with an identity provider: keep the session's state on the server, with only a random id
  in the cookie, unless the deployment cannot keep whole sessions in a store every instance reads;
  then keep it in the cookie, signed and encrypted, and write the choice down.** RFC 10017 section
  6.1.2.3 says that "using server-side sessions with a BFF is only recommended in small-scale
  scenarios", since they need sticky sessions or replication [1]. This practice departs
  from it because a session held in the cookie still needs a list of ended sessions in a store
  every instance reads (ASVS 5.0 requirement 7.4.1) [42]. The cookie then saves less than
  the RFC expects, and the rules below, back-channel logout among them, are simpler with the state
  on the server ("Logout" below). With a first-party login there is no choice: the state stays on
  the server (the opening of [security.md](../../react/security/security.md) section 6). Where the
  state in the cookie changes a rule, the rule says how.
- **BFF, with an identity provider: before you choose the session's state in the cookie, read the
  provider's discovery document for `revocation_endpoint`,** so you know whether revocation can
  back up the list of ended sessions; the rule is this practice's choice. RFC 8414 section 2 makes
  the field optional, so when it is missing, ask the provider [43].
- **BFF: with the session's state in the cookie, check the length of the session cookie's name and
  value before you set it; when the two together pass 4096 bytes, set no cookie, log the reason
  and answer an error page,** because a browser ignores such a cookie without an error (RFC 6265bis
  draft, sections 5.6 and 5.7), so the sign-in would look done and the next request would
  answer `401` [2].
- **BFF: with the session's state on the server, let only the BFF's own identity reach the session
  store, and encrypt the store's backups and replicas at rest,** since the store holds every
  user's tokens: server-side sessions "keep all data on the server", as RFC 10017 section 6.1.2.3
  puts it [1]. OWASP's Session Management cheat sheet asks to "restrict access to the
  session store and encrypt backups and replicas at rest" [8].
- **BFF: when someone reading the session store is in your threat model, put a lookup id and a
  separate secret in the session cookie, keep only the SHA-256 hash of the secret in the store,
  and compare hashes in constant time,** so a copy of the store gives no live session id. OWASP's
  Session Management cheat sheet says "If read-only disclosure of the store is in your threat
  model, store a one-way verifier instead", and compares the hash of the secret the request brings
  "with the stored hash using a constant-time comparison" [8]. In a
  BFF the record also holds the tokens, so this keeps only the ids from a reader of the store.
- **BFF: write down how many sessions one user may hold at once, and what happens when a new login
  passes that number ("Write it down" above),** so the team decides, before a user reaches the
  limit, whether a new login ends an older session or is refused. ASVS 5.0 requirement 7.1.2 asks
  the documentation to define both [42].

#### Keys and secrets

A key here is any key that signs or encrypts a cookie, the login cookie's included. Where a
framework protects the cookies, these rules are checks on it; write code only for a rule it does
not meet.

- **BFF: keep the client's credential at the identity provider, and every key that signs or
  encrypts a cookie, the login cookie's included, in the server's secret store, or in a shared
  store encrypted under a key that only the secret store holds, never in code or a build artifact;
  let only the BFF's own identity, and the job that rotates the keys, read or write them,** so no
  copy of the code holds a secret, and nobody else who reaches the store can add a key of their
  own and forge cookies (ASVS 5.0 requirements 13.3.1 and 13.3.2; Microsoft's ASP.NET Core Data
  Protection docs) [44], [45]. OWASP's Cryptographic Storage cheat sheet
  asks that a key which encrypts other keys be stored apart from them
  [46].
- **BFF: generate every cookie key from the operating system's CSPRNG, 32 bytes (256 bits), never
  from a password, a phrase or a value a person typed,** so nobody can guess the key, and it gives
  at least the 128 bits of security that ASVS 5.0 requirement 11.2.3 asks for [47].
  OWASP's Cryptographic Storage cheat sheet asks for keys "randomly generated using a
  cryptographically secure function" and not based "on common words or phrases", and for AES keys
  of at least 128 bits, ideally 256 [46]. Libraries differ here:
  express-session asks for a secret with at least 32 bytes of entropy [48], while
  iron-session takes a password of at least 32 characters [49]. Give a library that
  takes a password a key generated by this rule, written as hex or base64.
- **BFF: give the session cookie and the login cookie each its own key, or a subkey derived from
  the key with a fixed purpose label per cookie, and give each environment its own keys,** so a
  value from one cookie never decrypts as the other, and a key copied to a test system cannot
  forge a production cookie; the rule is this practice's choice. NIST SP 800-57 Part 1 section 5.2
  says: "In general, a single key shall be used for only one purpose" [50]. ASVS 5.0
  requirement 11.1.1 asks that keys are "not overshared" [47]. ASP.NET Core derives a
  subkey for each purpose string, so that "no other component can read its payloads"
  [51], and its docs say that apps that must stay isolated "should use
  different key repositories" [45].
- **BFF: for every cookie the BFF signs or encrypts, the login cookie included, give every instance
  the same set of keys, loaded from one store,** since an instance with keys of its own cannot read
  a cookie another instance wrote, so users are signed out, or their sign-in fails, at random
  (Microsoft's ASP.NET Core docs on a web farm) [52].
- **BFF: start every cookie you protect with a format version and the id of the key that
  protected it, and choose the key that reads it by that id,** so rotation needs no trial over
  every key, an unknown id is refused at once, and the algorithm can change later. OWASP's
  Cryptographic Storage cheat sheet names "Marking each item with the ID of the key that was used
  to encrypt it, and storing multiple keys to allow the old data to be decrypted" as a way to
  rotate keys [46]. ASVS 5.0 requirement 11.2.2 asks that keys and
  algorithms can be replaced [47]. ASP.NET Core's protected payload starts the same way,
  with "A 32-bit magic header that identifies the version" and "A 128-bit key id"
  [53].
- **BFF: with the session's state in the cookie, protect the cookie with authenticated encryption,
  such as AES-GCM, from a vetted library, the framework's own cookie protection where it has one,
  never with a scheme you build from primitives yourself,** so the encryption comes from code that
  others review and keep patched, and an edited cookie fails the check instead of being read
  (ASVS 5.0 requirements 11.2.1 and 11.3.3; OWASP's Cryptographic Storage cheat sheet)
  [47], [46].
- **BFF: rotate a cookie key in three steps,** since an instance that protects with a key the
  others do not hold yet signs users out at random, and a key removed too early signs out every
  user whose cookie it protected.
  1. Add the new key to every instance as a key that only reads.
  2. Once every instance holds it, make it the key that protects new cookies. Every instance holds
     the new key when each one logs the key ids it loaded, or when more time has passed than an
     instance keeps its key list cached.
  3. Remove the old key only when the longest lifetime of a cookie it protected, the absolute
     timeout for the session cookie, has passed since it stopped protecting new ones.

  ASP.NET Core waits 2 days before a new key protects anything, against a key list each instance
  re-reads about every 24 hours (Microsoft's docs on key management) [22].
  NIST SP 800-57 Part 1 section 5.3.5 lets a key keep reading after it stops protecting new data
  [50]. The express-session library signs with the first secret in its list and checks
  with all of them [48], so there step 1 adds the new secret at the end of the
  list, and step 2 moves it to the front.
- **BFF: write down how long each cookie key protects new cookies, and when the client's credential
  is rotated ("Write it down" above), and let a scheduled job rotate the keys by the steps above,**
  so rotation happens before anyone needs it and not by hand. ASVS 5.0 requirements 13.1.4 and
  13.3.4, both at Level 3, ask for a written schedule for rotating the critical secrets, and for
  secrets that expire and are rotated as the documentation says [44]. OWASP's Key
  Management cheat sheet asks to "Establish and document a key rotation schedule based on the
  system's threat model and risk assessment", and to prefer automated rotation
  [54]. The period has to end before the key reaches the usage limits of
  its encryption mode, counted over every instance that shares the key: OWASP's Cryptographic
  Storage cheat sheet asks to enforce "the mode's limits on message size, encryption operations,
  and initialization vector (IV) uniqueness across all instances sharing the key"
  [46]. NIST SP 800-57 Part 1 section 5.3.6 recommends that a
  symmetric key that protects integrity protect new data for no more than two years
  [50], and ASP.NET Core's default key lifetime is 90 days [22].
- **BFF: treat a session or login cookie that fails to decrypt or verify, or names a key the BFF no
  longer holds, as a request with no cookie, never as a `500`, and log the reason (unknown key,
  failed check, expired) without the cookie's value,** so a failed rotation shows in the log as a
  burst of unknown-key lines, not as random sign-outs; the rule is this practice's choice. The
  iron-session library starts a new empty session when it cannot read a cookie, since "a 500 on
  every request would be worse", and its README reads a burst of `unknown-password` reasons as a
  sign that a password rotation went wrong [49]. ASP.NET Core's docs describe the
  failure in a web farm: on a node that cannot decrypt the authentication cookie, authorization
  for the requested resource fails [52].
- **BFF: when you suspect that a cookie key leaked, replace it by the four steps below, though that
  signs out every user whose cookie the leaked key protected,** since whoever holds the key can
  write a cookie the BFF accepts and read the tokens in any copy of a cookie it encrypted, and each
  instance keeps the key list it loaded until it reloads [54],
  [22].
  1. Put a new key in the store as the key that protects new cookies.
  2. Delete the leaked key there.
  3. Restart or reload every instance.
  4. Check that no instance still reads the leaked key, for example by sending each one's session
     check a test cookie the leaked key protected, made before step 2, and expecting `401`, before
     you call it done.

  ASP.NET Core's docs say that until a refresh "a warmed instance might continue to unprotect data
  created with the revoked key", and ask to restart or reload every instance and to verify that
  all have refreshed [22]. NIST SP 800-57 Part 1 section 7.5 says "A
  compromised key shall not be used to apply cryptographic protection to information", and its
  glossary counts a key as compromised on "a suspicion or confirmation" of it [50].
  OWASP's Cryptographic Storage cheat sheet counts someone who had access to the key leaving the
  organisation as a reason to rotate it [46].
- **BFF: write down the steps for a leaked cookie key, who runs them and how to check them, and run
  them once in a test environment before you need them,** so the keys can be replaced quickly when
  a leak comes, not worked out under pressure; the test run is this practice's choice. OWASP's
  Cryptographic Storage cheat sheet asks that "the code and processes required to rotate a key are
  in place before they are required, so that keys can be quickly rotated in the event of a
  compromise" [46]. Its Key Management cheat sheet says "A
  compromise-recovery plan shall be documented and easily accessible" [54].

### A new session id at login

- **BFF: issue a new session id at login and at every change of privilege, and destroy the old
  one.** An id an attacker set before login, or one that leaked earlier, then dies with the old
  session (session fixation). OWASP's Session Management cheat sheet calls the renewal mandatory,
  ASVS 5.0 requirement 7.2.4 asks for it on every authentication, re-authentication included (the
  step-up rules under "Re-authentication" below), and OWASP Top 10:2025 lists it under A07
  [8], [42], [55].
- **BFF, with an identity provider: when the login start request carries the session cookie,
  record that session's id with the attempt; destroy that session at the callback,** because a
  `Strict` cookie does not come with the provider's redirect [2]. With the session's
  state in the cookie, record the old cookie's session id in the same way and add it to the list
  of ended sessions (its rules are under "Logout" below) at the callback, since the new cookie does
  not stop a copy of the old one from working; the rule is this practice's choice.
- **BFF, with an identity provider: at the login callback, when destroying the old session fails,
  log it at `ERROR` ([logging.md](../../python/logging/logging.md) section 4), issue no new
  session and answer the page of a failed callback** (the login cookie rules above), so a failed
  destroy never leaves the old session live beside a new one; ASVS 5.0 requirement 16.5.3 asks to
  prevent fail-open conditions [56].
- **BFF, with an identity provider: at the login callback, store the ID token's `iss` and `sub`
  with the new session, and its `sid` when the ID token carries one,** since the back-channel
  logout rules and the step-up's checks below match on them, and a provider sends `sid` only when
  it supports it (OpenID Connect Back-Channel Logout 1.0, sections 2.1 and 2.7)
  [57]. With the session's state on the server, the index rule in
  "Re-authentication" below writes them into the index of sessions by user and by `sid`.
- **BFF: create the session id from a CSPRNG with at least 128 bits of entropy: check that the
  framework's session manager does, and where you write it yourself, draw 32 bytes from the
  operating system's CSPRNG, never a UUID,** so nobody can guess a live id (ASVS 5.0 requirements
  7.2.3 and 11.5.1; OWASP's Session Management cheat sheet, which asks for at least 128 bits for an
  id you create yourself) [42], [47], [8].
- **BFF: with the session's state on the server, treat a session cookie whose id the store does not
  hold as no session, and never create or save a session under an id the request brought,** so an
  attacker cannot plant an id and wait for the user to sign in under it. OWASP's Session
  Management cheat sheet says "Web applications should never accept a session ID they have never
  generated" [8].

### Timeouts and refresh

- **BFF: enforce an idle timeout and an absolute timeout on the server.** A time the client keeps,
  such as a cookie's `Max-Age`, can be changed to extend the session, so the server checks both
  timeouts on every request [8]. ASVS 5.0 requirements 7.3.1 and 7.3.2
  ask for both timeouts [42]. With the session's state in the cookie, the cookie's
  protected value carries the session's start time and its last-use time, and the BFF checks both;
  the idle clock moves when the BFF re-issues the cookie on use. ASP.NET Core's cookie
  authentication, with `ExpireTimeSpan` and `SlidingExpiration`, gives the idle timeout only: it
  re-issues the cookie once more than half of `ExpireTimeSpan` has passed and then sets the
  ticket's issue time to now, so the absolute timeout needs the start time kept as a value of its
  own [58], [59].
- **BFF: with the session's state on the server, delete a session's record, with its tokens, when
  a timeout ends it, such as with a store expiry that moves with the idle clock and never passes
  the absolute timeout,** since a record left in the store keeps a live refresh token at rest after
  the session ended [41]. ASVS 5.0 requirement 7.4.1 asks that expiration
  invalidate the session data at the application backend [42].
- **BFF: write both timeout values down, as values with their reason ("Write it down", above, says
  where), and say why where a value is longer than NIST's for the session's assurance level.** The
  values come from the risk: OWASP gives 2 to 5 minutes idle for high-value applications and 15 to
  30 minutes for low-risk ones, and 4 to 8 hours absolute for an office application;
  NIST SP 800-63B-4 says the overall timeout should be at most 24 hours and the idle one at most 1
  hour at AAL2, and at AAL3 the overall timeout shall be at most 12 hours and the idle one should
  be at most 15 minutes [8], [41]. ASVS 5.0
  requirement 7.1.1 asks for the values to be documented, with the reason for any departure from
  NIST SP 800-63B's re-authentication requirements [42].
- **BFF, with an identity provider: write the refresh token's maximum lifetime down with the
  timeouts, and set the absolute timeout no longer than it,** since after it the first refresh
  fails with `invalid_grant` and ends the session (the `invalid_grant` rule below), so users would
  meet a shorter absolute timeout than the one written down [15]. RFC 10017 section 6.1.2.2
  says it makes sense to set the BFF's session lifetime equal to the refresh token's maximum
  lifetime [1].
- **BFF, with an identity provider: decide whether the idle and absolute timeouts must make the
  user sign in again at the provider, and write the choice down,** since a timeout ends only the
  BFF's session, and the provider can answer the next login from its own session without asking
  the user [41]. NIST SP 800-63B-4 makes the relying party, here the BFF, the
  authority on whether its re-authentication requirements have been met [41].
  ASVS 5.0 requirements 7.1.3 and 7.6.1 ask for the session lifetimes of the BFF and the provider,
  and the conditions that require re-authentication, to be documented and to behave as documented
  [42].
- **BFF, with an identity provider: where the timeouts must make the user sign in again, send
  `max_age` on the login that follows a session the timeouts ended, and check the ID token's
  `auth_time` at its callback,** since `max_age` makes the provider re-authenticate a user whose
  last sign-in is older than it allows, and puts `auth_time` in the ID token for the client to
  check (OpenID Connect Core 1.0 sections 3.1.2.1 and 3.1.3.7) [27].
- **BFF: when the token endpoint answers a refresh with `invalid_grant`, or with an error that asks
  for the user at the provider, such as `interaction_required` or `consent_required`, end the
  session,** so the session never outlives the tokens it stands for, and the page's sign-in path
  takes the user to the provider. RFC 10017 section 6.1.2.2 says it makes sense to end the session
  when a refresh token is no longer valid, and RFC 6749 section 5.2 sends `invalid_grant` for a
  refresh token that is invalid, expired or revoked [1], [15].
  Microsoft Entra ID's token endpoint also answers `interaction_required` and `consent_required`,
  and its client action for both is a new request to the authorization endpoint
  [60]. OpenID Connect Core 1.0 section 3.1.2.6 defines
  `interaction_required` as a provider that needs the user to act [27]. With the
  session's state in the cookie, ending the session means expiring the cookie.
- **BFF: when the token endpoint answers a refresh with any other error code that RFC 6749 section
  5.2 lists, keep the session, answer the page `502` and log it at `ERROR`
  ([logging.md](../../python/logging/logging.md) section 4),** since those codes
  (`invalid_request`, `invalid_client`, `unauthorized_client`, `unsupported_grant_type` and
  `invalid_scope`) mostly name the client's own request or setup, not the user's grant: ending
  the session on them would sign every user out after one wrong setting, such as a client secret
  rotated at the provider but not in the BFF [15]. `invalid_scope` can also mean a scope
  beyond the one the user granted (RFC 6749 section 5.2), which a refresh that asks for the
  granted scope does not ask for [15]. The rule is this practice's choice.
- **BFF: when a refresh fails in any other way, keep the session, answer the page `502` or `503`,
  never `401`, and log it,** because the page runs the sign-out path on every `401`. Such a
  failure is a provider that cannot be reached or does not answer, a `5xx`, a `429`, any other
  `4xx`, or a body that does not parse. `502` says that an upstream server answered badly, and
  `503` that the server cannot answer for now (RFC 9110 sections 15.6.3 and 15.6.4) [61].
  The status is this practice's choice.
- **BFF: when a refresh answer carries no `refresh_token`, keep the refresh token you have, and
  replace it only with one an answer carries,** since RFC 6749 makes the new refresh token
  optional (sections 5.1 and 6), and a BFF that stores the missing value signs the user out at the
  next refresh [15]. Okta, with rotation on, returns no new refresh token while its lifetime
  setting has not expired, and Spring Security keeps the old token in this case [62],
  [63].
- **BFF, with an identity provider: where the provider lets you choose, give the BFF refresh
  tokens that do not rotate, or rotation with a reuse window, and write the choice down,** since
  the BFF is a confidential client whose refresh token works only with its client authentication
  (RFC 10017 section 6.1.2.2), and without rotation the lock rules below are not needed
  [1]. RFC 9700 section 2.2.2 adds that RFC 6749 "already mandates that refresh tokens
  for confidential clients can only be used by the client for which they were issued" [16].
  RFC 9700 section 4.14.2 asks for rotation or sender-constrained refresh tokens only for public
  clients [16]. RFC 10017 asks the same of authorization servers in section 6.3.2.3, for
  refresh tokens issued to browser-based applications, not to a BFF [1]. The cost: the
  provider no longer detects a refresh token stolen together with the BFF's client credentials
  [16].
  Okta gives web apps non-rotating refresh tokens by default, and Duende IdentityServer has made
  reusable refresh tokens the default since version 7.0 [62], [64].
  The rule is this practice's choice.
- **BFF: set the provider's reuse window where it has one,** so a refresh token sent twice within
  it does not count as reuse. Auth0 calls that window the rotation overlap period, and it is off
  by default [65].
- **BFF: when the provider rotates the BFF's refresh tokens and has no reuse window that covers the
  requests in flight, and the session's state is on the server, refresh the tokens of a session at
  most once at a time, and let the session's other requests wait for that refresh and use its
  result,** because parallel requests would each refresh with the same refresh token, and where
  the provider rotates refresh tokens, the second use counts as reuse; the rule is this practice's
  choice. Auth0 then revokes every refresh token issued since, with the grant, and Okta
  invalidates the newest refresh token and the access tokens issued since sign-in, unless the
  reuse falls in its grace period [65], [62].
- **BFF: with the session's state on the server, hold that one refresh with a lock that every
  instance shares, keyed by the session id,** since the session's requests can reach any instance;
  the rule is this practice's choice.
- **BFF: when the lock cannot be taken because the store that holds it fails, answer `503` and
  never refresh without the lock,** since a refresh without it can send the same refresh token
  twice, which the provider counts as reuse (above); the rule is this practice's choice.
- **BFF: give the call to the token endpoint, together with the store of its answer, a timeout,
  and give the lock that holds a session's refresh an expiry a little longer than that timeout,**
  so a lock whose holder stopped frees itself while the requests that wait for it still wait, and
  a slow provider alone does not make a refresh outlive its lock; a call that times out is a
  provider that does not answer (the refresh failure rule above). Timeouts lower that chance and
  do not remove it. Kleppmann holds that a lock's holder paused past the lock's expiry can still
  write after another client has taken the lock, and that a timeout does not show that the other
  side is down, since a request can still arrive long after it was sent
  [66]. So a call that timed out may still have reached the
  provider and rotated the refresh token, and such a failure can still end in a sign-out once the
  provider's reuse window has passed. The values are this practice's choice.
- **BFF: after taking the lock, read the session's tokens again from the store, and refresh only
  when the access token read then still needs it; otherwise use that token,** since a request that
  read the session before the last holder stored its new tokens carries a refresh token the
  provider has already rotated, and sending it is the reuse the lock is there to prevent; the rule
  is this practice's choice.
- **BFF: store the new tokens before you release the lock,** so the next request that takes it
  refreshes with the newest refresh token, never with one the provider has already rotated; the
  rule is this practice's choice.
- **BFF: when the refresh that holds the lock fails, or its new tokens cannot be stored, release
  the lock, answer `503` to every request that waited for it, and to the holder's own request when
  the store failed, and log it once at `ERROR` ([logging.md](../../python/logging/logging.md)
  section 4),** so no waiting request takes the lock and refreshes again with a refresh token the
  provider may already have rotated, and the page sees an outage it can retry, not a sign-out; the
  rule is this practice's choice. A lock in a store that cannot be written ends at its expiry.
  After a failed store, the retry avoids a sign-out only while the provider's reuse window lasts,
  since the refresh token still stored is one the provider has already rotated.
- **BFF: answer `503` to a request that waited for the refresh until the lock expired, and log it
  at `ERROR` ([logging.md](../../python/logging/logging.md) section 4),** so the page sees an
  outage it can retry, not a sign-out; the rule is this practice's choice.
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
  resource fails, and to prevent fail-open conditions [56].

### Logout

- **BFF: at logout, with the session's state on the server, destroy the session there,** since a
  cookie deleted only in the browser leaves a session that still works from a copy of the cookie.
  OWASP's Session Management cheat sheet, ASVS 5.0 requirement 7.4.1 and OWASP Top 10:2025 A01
  ask for the session to end on the server [8], [42],
  [67].
- **BFF: with the session's state on the server, end a session with a write that a request still
  running cannot undo: record the end where a session's save never writes it, such as the list of
  ended sessions, which every request then checks, or delete the session in a store whose save is
  one atomic step that fails when the record is gone (an update, never a read followed by a
  write),** because a request still running when the session ends saves the copy it loaded and so
  writes the session back. CVE-2025-32441 let parallel requests restore a deleted session in
  Rack's session middleware [68]. Its advisory names a store that refuses data for a
  session ended after the request began, and the rack-session fix makes the save refuse a session
  that is gone [68], [69]. Django ticket
  37249 shows that a save which checks first and writes after still restores the session, while
  Django's database store, whose save is an update, does not [70].
- **BFF: with the session's state in the cookie, write a random session id into the cookie at
  login, and copy it unchanged into every cookie the BFF re-issues for that session,** so a later
  logout can name the session it ends, whichever copy of the cookie comes back; the rule is this
  practice's choice, after ASVS 5.0 requirement 7.4.1, which names a list of terminated tokens
  [42].
- **BFF: with the session's state in the cookie, at logout add the cookie's session id to a list
  of ended sessions that every instance reads, and keep it there until its absolute timeout has
  passed,** because a copy of the cookie still leads to the tokens. ASVS 5.0 requirement 7.4.1
  names such a list for sessions held in a token, and it works without the provider [42].
  Revoking the tokens at logout (below) is then the second control. RFC 10017 section 6.1.2.3
  counts revocation as enough on its own [1]; the list is this practice's addition.
- **BFF: with the session's state in the cookie, on every request reject a cookie whose session id
  or provider `sid` is on the list of ended sessions, or whose start time is earlier than its
  user's per-user time (the back-channel logout rules below),** so a copy of the cookie stops
  working as soon as its session ends. ASVS 5.0 requirement 7.4.1 asks to verify that, when a
  session ends, "the application disallows any further use of the session" [42].
- **BFF: with the session's state in the cookie, keep the access token's lifetime short, and write
  it down,** because revocation on its own leaves a copy of the cookie working until the access
  token in it expires: a provider without access-token revocation leaves the token valid (RFC 7009
  section 5), and a resource server that checks a self-contained token by itself accepts it even
  after the provider revokes it (RFC 7009 section 3) [71]. OWASP Top 10:2025 A01 asks for
  short-lived stateless tokens [67].
- **BFF: at logout, also revoke the refresh token at the identity provider, and the access token
  where the provider supports it,** since a refresh token that is not revoked still gets new
  access tokens. RFC 7009 names logout as a reason to revoke tokens, and RFC 10017 section 6.1.2.3
  says that, with the session's state in the cookie, revoking the tokens is enough [71],
  [1]. This practice still asks for the list of ended sessions with the session's state
  in the cookie (the rules above say why). With the session's state on the server, neither step
  replaces the other.
- **BFF: at logout, end the session and expire the cookie before you revoke the tokens, holding
  the tokens the revoke needs only within the logout request,** so a failed revoke never keeps the
  user signed in; the order is this practice's choice.
- **BFF: when destroying the session or adding its id to the list of ended sessions fails at
  logout, log it at `ERROR` ([logging.md](../../python/logging/logging.md) section 4), still revoke
  the tokens when the request could read them, answer `503` and keep the cookie,** so the page can
  try again on the same session, and until it does, the session cannot get new access tokens (RFC
  10017 section 5.2.1); the rule is this practice's choice, after ASVS 5.0 requirement 7.4.1,
  which asks that a logout end every further use of the session, and 16.5.3, which asks to prevent
  fail-open conditions [1], [42], [56].
- **BFF: answer the logout request with success also when no session exists,** so a second tab
  that signs out after the first is not told that sign-out failed; the rule is this practice's
  choice.
- **BFF: log every logout at `INFO` ([logging.md](../../python/logging/logging.md) section 4), with
  a short hash of the session id, the user's id and whether the revoke succeeded,** so an incident
  review can see when a session ended. OWASP's Session Management cheat sheet says "it is
  recommended to record session related events, such as the creation, renewal, and destruction of
  session IDs, as well as details about its usage within login and logout operations"
  [8]. [logging.md](../../python/logging/logging.md) section 10 keeps
  the raw session id out of the line.
- **BFF: log a revoke that fails at the provider,** so the token it leaves alive until its own
  expiry shows in the log. ASVS 5.0 requirement 16.3.4 asks the application to log "unexpected
  errors and security control failures" [56].
  [logging.md](../../python/logging/logging.md) section 10 says what stays out of the line.
- **BFF: do not retry a failed revoke later,** so the BFF keeps no token after logout; the token
  then ends at its own expiry. A refresh token left alive is of no use without the BFF's client
  credential, since RFC 6749 section 10.4 requires the provider to "verify the binding between the
  refresh token and client identity whenever the client identity can be authenticated"
  [15]. With the session's state in the cookie, the list of ended sessions already stops
  every copy of the cookie, so a failed revoke no longer leaves the session usable. RFC 7009
  section 2.2.1 lets a client retry, since on a `503` the client must assume the token still
  exists [71]. Not retrying is this practice's choice; record it with the logout choices.
- **BFF: where the user should also leave the identity provider, end its session too,** for
  example on a shared device or where one sign-in covers several applications. The BFF ends the
  session as the logout rules above say, expires the cookie, and answers with the provider's
  logout URL: the `end_session_endpoint` from the provider's discovery document, with `client_id`
  and the registered `post_logout_redirect_uri` [72]. It sends no `id_token_hint`,
  so no token reaches the page or a URL: RFC 10017 section 6.1 keeps the tokens away from the page,
  and keeping the ID token out of a URL too is this practice's reading [1]. Leaving out
  `id_token_hint`, which OpenID Connect RP-Initiated Logout 1.0 recommends, is this practice's
  choice: without it, section 2 says the provider must ask the user whether to log out, and
  section 3 says it must not send the user back to `post_logout_redirect_uri` unless it can
  confirm that target another way, so the redirect back may not happen [72]. The
  local logout never waits for either step, which section 2 leaves to the relying party
  [72].
- **BFF: accept the provider's back-channel logout,** which names the session to end
  (Back-Channel Logout 1.0) [57]. Duende's BFF accepts it only with the session's
  state on the server (Duende's docs); that is a limit of Duende's product, and the specification
  leaves the way a session ends to the application (its section 1)
  [73], [57]. Where back-channel logout is
  needed, the session's state on the server is the simpler choice; that choice is this practice's.
  With the session's state on the server, the BFF finds the sessions a logout token names through
  the index of sessions by user and by `sid` (the index rule in "Re-authentication" below).
- **BFF: validate every logout token by the steps of Back-Channel Logout 1.0 section 2.6 before
  you end anything, and where the provider sets the `typ` header, require `logout+jwt`,** since an
  unchecked token lets anyone who can reach the endpoint end a user's sessions
  [57]. ASVS 5.0 requirement 10.5.5 (Level 2) asks the relying party to check the
  type, the `events` claim and that no `nonce` is present [74]. Back-Channel Logout 1.0
  section 4.1 warns that requiring the type breaks providers that do not set it, so check what
  yours sends and write the choice down [57].
- **BFF: with the session's state in the cookie, end the session that a back-channel logout names
  by adding its `sid` to the list of ended sessions, and for a logout token with no `sid`, set a
  time per user before which no cookie of that user counts; keep each such entry for one absolute
  timeout after it was written,** since the cookie carries the provider's `sid`, when the ID token
  has one ("A new session id at login" above), the every-request check above rejects both, and
  every session the entry ends started before it was written. ASVS 5.0 requirement 7.4.1 names
  both ways for sessions held in a token [42].
- **BFF: when a back-channel logout token carries no `sid`, end every session of the user its
  `iss` and `sub` name,** since Back-Channel Logout 1.0 section 2.4 says a token without `sid` asks
  for all of that user's sessions at the client to be logged out [57].
- **BFF: answer a back-channel logout with `200` also when no session matches, and with `400` when
  the logout token fails validation,** since section 2.7 of the same specification counts a user
  who is already logged out as a logout that succeeded, and section 2.6 asks for `400` when a
  validation step fails [57].
- **BFF: log at `INFO` ([logging.md](../../python/logging/logging.md) section 4) a valid logout
  token that matches no session,** so a BFF whose sessions never match shows as a run of such
  lines; the rule is this practice's choice.
- **BFF: when the session that a valid logout token names cannot be ended, such as when the session
  store cannot be written, log it at `ERROR` with the token's `iss`, `sub` and a short hash of its
  `sid` ([logging.md](../../python/logging/logging.md) sections 4 and 10), and answer `400`,**
  since section 2.8 of the same specification asks for `400` when the logout failed, not the `503`
  of the store-outage rule above [57]. Section 5 names what this leaves open.
- **BFF: prefer back-channel to front-channel logout,** because front-channel logout loads the BFF
  in a frame on the provider's page, where the `SameSite=Strict` session cookie is not sent (RFC
  6265bis draft, section 4.1.2.7) and where a browser that blocks third-party content can keep the
  frame from the session's state (Front-Channel Logout 1.0 section 4.1); its request also carries no
  signature, while a back-channel logout token is signed (Back-Channel Logout 1.0 section 4)
  [2], [75], [57].
- **BFF: write these logout choices down, in the decision log ("Write it down", above, says
  where),** since ASVS 5.0 requirement 7.1.3 asks how federated sessions end to be documented
  [42].
- **BFF: at logout, expire the session cookie by name,** so the browser drops it at once: MDN's
  `Set-Cookie` page says a `Max-Age` of zero or less expires the cookie immediately
  [4]. OWASP's Session Management cheat sheet recommends the same step, an empty
  value with an `Expires` or `Max-Age` in the past [8]. The logout
  response below shows the line.
- **BFF: send `Clear-Site-Data: "cache", "storage"` only from the origin whose data it should
  clear,** since `"storage"` clears only the origin of the response, so the header on a response
  from `api.example.com` leaves what `app.example.com` stored [76]. OWASP's
  Session Management cheat sheet suggests `Clear-Site-Data: "cache", "cookies", "storage"`, but
  `"cookies"` clears the cookies of the whole registrable domain, every sibling subdomain included
  (MDN; the W3C draft) [8], [76],
  [77]. GitLab stopped sending it after a sign-out from GitLab
  signed users out of other applications on the same domain (GitLab merge request 156213, 2024)
  [78]. Chrome supports `"cache"` only in part (MDN's compatibility data)
  [38]. The header is defence in depth; ending the session on the server,
  or, with the session's state in the cookie, the list of ended sessions, is the control.

### Re-authentication

The step-up rules below, down to the `403` rule that asks the page for re-authentication, and the
`Page:` re-authentication rules in [security.md](../../react/security/security.md) section 6, serve
ASVS 5.0 requirement 7.5.1, a Level 2 requirement: a team at Level 1 may skip them, and so may a
team whose identity provider holds the email, the phone, the second factor and the recovery data
and asks for re-authentication itself; write the choice down ("Write it down" above says where)
[42]. The rules after them are outside that skip: ending a user's other sessions (7.4.3)
holds at Level 2 and above, and ending every session of a disabled or deleted account (7.4.2)
holds at every level [42].

- **BFF: ask for re-authentication before a change to the email, the phone, the second factor or
  the recovery data,** and after a high-risk event such as a sign-in from a new device. ASVS 5.0
  requirement 7.5.1 asks for full re-authentication before such changes, and OWASP's cheat sheet
  asks for it after high-risk events, so a stolen session cannot take over the account
  [42], [8], [79]. The rules below say
  how, by who logs the user in.
- **BFF, with an identity provider: re-authenticate the user at the provider, and never ask for
  the provider's password,** since RFC 9700 section 2.4 forbids the password grant, the only way
  the BFF could check it [16]. Start a login with `max_age=0`, which OpenID Connect Core
  1.0 section 3.1.2.1 makes equal to `prompt=login` and which makes the ID token carry
  `auth_time` [27].
- **BFF, with an identity provider: answer a guarded request that the session's re-authentication
  does not cover (the window rule below) with the `403` and `reauth_required` below, and keep
  nothing of the request,** since the page starts the step-up by a navigation to the BFF's login
  endpoint, the start RFC 10017 section 6.1.2.1 describes, and sends the request again once the
  user is back, as RFC 9470 section 2 has the client repeat its request [1],
  [80]. The rule is this practice's choice.
- **BFF, with an identity provider: treat a login start that carries a live session and the
  step-up flag as a step-up, and send the user to the provider with `max_age=0`, and with the
  challenge's `acr_values` when the step-up answers an RFC 9470 challenge,** so every login-cookie
  rule above holds for it unchanged; a login start without a live session is a first login,
  whatever its flag says. The rule is this practice's choice.
- **BFF: name a relayed challenge's `acr_values` in the `acrValues` field of the `403`'s body, a
  string that holds the space-separated value, and at a step-up's login start accept `acr_values`
  only from the list the team writes down,** so the page can pass the value on and cannot pick one
  the resource servers never ask for; the rule is this practice's choice. RFC 9470 section 4 has a
  client that receives the challenge use its `acr_values` in the authorization request it builds
  [80].

RFC 9470 section 2 has the client repeat its request once the user has re-authenticated; here the
page sends the request again after the navigation back [80]. The page could keep itself
loaded by re-authenticating the user in a popup, but the reference policy's
`Cross-Origin-Opener-Policy: same-origin` ([security.md](../../react/security/security.md)
section 5) cuts the page's link to the popup (MDN), so a popup flow needs that header relaxed to
`same-origin-allow-popups`, which MDN names for OAuth popups [81].
The navigation needs neither: the page keeps the user's input itself, or asks for the step-up
before the form ([security.md](../../react/security/security.md) section 6).

A design that keeps the request's change on the BFF, bound to a login attempt the `403` starts,
admits only that change after one re-authentication. OWASP's Transaction Authorization cheat
sheet favours that design: its section 2.3 asks that significant transaction data be "generated and
stored on a server, then passed to an authorization component"
[82]. This practice does not take it: it needs the start RFC
10017 section 6.1.2.1 says "requires a custom implementation and makes it harder to use standard
OAuth libraries"; it keeps state for each guarded request, so a screen with three challenged
reads makes more attempts than a per-session cap can hold, and the one the page navigates with is
gone; and it does not stop a script on the page, which can send its own change and open the
returned URL itself, while RFC 10017 section 6.1.4.1 says nothing prevents client hijacking
"apart from stopping the execution of malicious code in the first place" [1]. Neither
design meets the cheat sheet's section 1.1, which asks that the user can "identify and
acknowledge the data that is significant to a given transaction", since an identity provider's
sign-in prompt does not show the change [82]. The single use in
the rule below keeps one change per re-authentication.

- **BFF, with an identity provider: at a step-up's login start, record with the attempt, in its
  protected record ("The login cookie" above), the id of the session the request carries, with
  that session's `iss`, `sub` and `sid`, and that the attempt is a step-up,** since the callback
  is a cross-site navigation that carries no `Strict` session cookie, and its checks below need
  that session. The rule is this practice's choice.
- **BFF, with an identity provider: at a step-up's callback, accept the re-authentication only
  when the new ID token's `iss` and `sub` equal those recorded with the attempt and its
  `auth_time` is later than the time the attempt started,** because `iss` and `sub` together are
  the only claims a client can rely on to name the same user (OpenID Connect Core 1.0 section
  5.7), so a thief who holds the cookie cannot pass the step-up by signing in to their own
  account, and a provider session that answers without asking the user does not count (OpenID
  Connect Core 1.0 section 3.1.3.7; NIST SP 800-63B-4 section 5.2 makes the relying party the
  judge) [27], [41].
- **BFF, with an identity provider: when the step-up asked for `acr_values`, accept it at the
  callback only when the new ID token's `acr` is one of them, and answer `refused` otherwise,** so
  the page is not sent round a loop that the resource server answers with the same challenge.
  OpenID Connect Core 1.0 section 3.1.3.7 says that when the `acr` claim was requested, the
  client "SHOULD check that the asserted Claim Value is appropriate" [27]. RFC 9470
  section 5 names the loop: one "where the authorization server keeps returning tokens that the
  resource server already identified as not meeting its requirements" [80].
- **BFF, with an identity provider: when `iss` or `sub` does not match, issue no new session, end
  the session recorded with the attempt, log it and alert (the logging and alerting rules of
  section 3),** since another account at the step-up's callback means the session may be in
  someone else's hands; the rule is this practice's choice.
- **BFF, with an identity provider: complete a step-up at its callback in this order,** so the old
  session never stays live beside the new one, and a step-up that fails issues no new session;
  the order is this practice's choice:
  0. When the code exchange or the library's ID token checks fail, issue no new session, keep the
     recorded session and answer `failed`.
  1. Run the `iss`, `sub`, `auth_time` and `acr` checks above against the attempt's protected
     record. When one fails, issue no new session and answer `refused`; a failed `iss` or `sub`
     also ends the recorded session, as the rule on a mismatch says. When ending it fails, log it
     at `ERROR` ([logging.md](../../python/logging/logging.md) section 4) and alert a person
     (section 3, "Logging"), saying that the session is still live; still answer `refused`.
  2. End the recorded session: destroy it, or add its id to the list of ended sessions. When that
     fails, log it at `ERROR` ([logging.md](../../python/logging/logging.md) section 4), issue no
     new session and answer `failed`, since ASVS 5.0 requirement 16.5.3 asks to prevent fail-open
     conditions [56].
  3. Issue the new session as a login does ("A new session id at login" above; ASVS 5.0
     requirement 7.2.4 asks for it on re-authentication too) [42]. It holds the tokens of
     the step-up's own code exchange (RFC 9470 section 4); the new ID token's `iss`, `sub` and
     `sid`, or the recorded `sid` when the token carries none, so back-channel logout still finds
     the session; and the time of this callback as the session's re-authentication time
     [80]. Its idle and absolute timeouts start again, since NIST SP 800-63B-4 section 5.2
     says that successful reauthentication "SHALL reset both timeouts" [41]. A team
     that keeps the absolute timeout of the first sign-in writes its reason down ("Write it down"
     above says where), since ASVS 5.0 requirement 7.1.1 asks for a reason for any departure from
     NIST SP 800-63B [42]. When issuing it fails, answer `failed`.
  4. Answer `reauthenticated`.

  With the session's state in the cookie, the old refresh token is never used again, since only
  the BFF, with its client credential, can use it (RFC 10017 section 6.1.2.2) [1].
- **BFF, with an identity provider: at a step-up callback whose login cookie matches the `state`
  and that carries the provider's error, delete the login cookie, keep the recorded session and
  answer the step-up's `failed` code,** so the user keeps their session and can try again; the
  rule is this practice's choice. RFC 9470 section 5 has the authorization request fail with the
  error `unmet_authentication_requirements` when the sign-in does not meet the requested `acr`
  [80].
- **BFF, with an identity provider: answer a step-up's callback whose login cookie matches the
  `state` with a `303` to one fixed route of the page, carrying one of three fixed outcome codes,
  never a value taken from the request,** so the page that loads after the navigation can ask the
  user to send the change again, or say why it cannot; the rule is this practice's choice. Each
  code has one meaning:
  - `reauthenticated`: the new session holds a fresh re-authentication (step 4 above);
  - `refused`: a check failed (step 1);
  - `failed`: the provider answered with an error (the rule above), the code exchange or the ID
    token checks failed (step 0), ending the recorded session failed (step 2), or issuing the new
    session failed (step 3).

  A callback whose login cookie is missing, cannot be read, or does not match the `state` gets the
  page of a failed callback instead ("The login cookie" above).
- **BFF, with an identity provider: let a guarded change through only while the session's
  re-authentication time is younger than a window the team writes down, long enough for the user
  to finish the change, and clear that time once one guarded change is applied,** since ASVS 5.0
  requirement 7.5.1 asks for full re-authentication before the change, and OWASP's Transaction
  Authorization cheat sheet, section 1.5, warns that a credential asked for once lets the user
  "authorize any transaction during the entire session" [42],
  [82]. A script on the page can still use the window (RFC 10017
  section 6.1.4.1); the single use limits it to one change [1]. The window and the single
  use are this practice's choice; a team that lets several changes through one window, as
  GitHub's sudo mode does for two hours, writes that down [83].

A step-up with a first-party login works differently from the provider's step-up above, because
the user answers on the page. At an identity provider the user leaves the page and comes back
through the callback, so the BFF never gets the answer and the guarded request together. With a
first-party login the page asks the user itself, so the answer can travel with the guarded
request: the BFF checks it, applies that one request, and keeps nothing between two requests. The
design is this practice's choice.

- **BFF, with a first-party login: before a guarded change, ask again for every factor the user's
  sign-in asks, the password and the second factor where the account has one, with the `403`
  below,** since ASVS 5.0 requirement 7.5.1 asks for full re-authentication, while its Level 3
  requirement 7.5.3 asks only for at least one factor [42]. Reading "full" as every factor
  of the sign-in is this practice's choice. OWASP's Session Management cheat sheet, guidance
  rather than a standard, asks for less: "Prompt users for primary credentials (e.g., password) or
  enforce MFA" [8].
- **BFF, with a first-party login: take the answer only with the guarded request it is for, and
  keep no change between the two requests,** so an answer authorises only the change it comes
  with, never every change of the session, and the page sends that request again with the answer;
  the rule is this practice's choice, after OWASP's Transaction Authorization cheat sheet, section
  1.5, which warns that credentials asked for once let the user "authorize any transaction during
  the entire session" [82]. That section also asks for
  authorization credentials unique to each transaction, which a password typed again is not
  [82]; leaving that part out is this practice's choice.
- **BFF, with a first-party login: take the answer from a header or a body field of its own, never
  the URL, and remove it from the request once it is checked, before the request is applied,** so
  the code that applies the change never holds, stores or logs the password. ASVS 5.0 requirement
  14.2.1 asks that "the URL and query string do not contain sensitive information", and
  requirement 16.2.5 says that "it may not be allowed to log certain data, such as credentials"
  [84], [56]. Removing the answer before the request is applied is this practice's
  choice.
- **BFF, with a first-party login: check the answer against the user of the session the request
  carries,** so a thief who holds a stolen session cannot answer with the password of an account
  of their own; the rule is this practice's choice.
- **BFF, with a first-party login: check a step-up's answer with the same verifier as the sign-in,
  and count a wrong answer also toward the per-account failure count the sign-in keeps, where it
  keeps one,** so every control of the sign-in, such as a one-time code that works once, holds for
  the step-up too. ASVS 5.0 requirement 6.3.4 asks that, where an application has several
  authentication pathways, "security controls and authentication strength are enforced
  consistently", and requirement 6.5.1 that time-based one-time passwords "are only successfully
  usable once" [85]. NIST SP 800-63B-4 section 3.2.2 counts failed attempts "using a
  specific authenticator on a single subscriber account" [41]. The login throttling
  itself stays outside this practice (sections 1 and 5).
- **BFF, with a first-party login: count every answer to a step-up per session with one atomic
  increment in the session store, never in the session object the request loaded and saves back
  at its end; compare an answer only while its raised count is below a small number the team
  writes down ("Write it down" above), and when the count reaches it, end the session and log it
  without comparing the answer,** so a thief who holds a stolen session cannot guess the password
  through the step-up, not even with answers sent in parallel. ASVS 5.0 requirement 6.3.1 asks for
  controls against password brute force, and OWASP's Transaction Authorization cheat sheet,
  section 2.4, asks for a limit where such answers are checked [85],
  [82]. A framework that saves the loaded session at the end of
  a request loses an update a parallel request made (CVE-2025-32441, in Rack's session middleware)
  [86]. When ending the session fails, log it at `ERROR`
  ([logging.md](../../python/logging/logging.md) section 4) and still refuse the answer, since ASVS
  5.0 requirement 16.5.3 asks to prevent fail-open conditions [56]. The number, the atomic
  increment and the end of the session are this practice's choice.
- **BFF, with a first-party login: start that count again at zero when a step-up succeeds,** so
  wrong answers in earlier step-ups do not add up and end an honest user's session. NIST SP
  800-63B-4 section 3.2.2 says that when the subscriber authenticates successfully, "the verifier
  SHOULD disregard any previous failed attempts for the authenticators used in the successful
  authentication" [41].
- **BFF, with a first-party login: answer a wrong answer with a `403` whose JSON body carries a
  fixed code such as `reauth_failed`, and with `401` once the guess limit has ended the session,**
  so the page asks again while it may, and runs the sign-out path once the session has ended; the
  rule is this practice's choice.
- **BFF, with a first-party login: once the answer passes the check, complete the step-up in this
  order,** so a valid answer never lets another change through, only a live session gets the
  change, and the old session never stays live beside the new one; the order is this practice's
  choice:
  1. Issue a new session id and move the session into it in one atomic act of the session store
     that succeeds only while the old session is still live there, such as a transaction or a
     conditional update of the record, never from the copy of the session the request loaded.
     ASVS 5.0 requirement 7.2.4 asks for a new session token on re-authentication too
     [42]. A logout in another tab can end the session while the answer is checked, and a
     move from the loaded copy would bring that session back, as CVE-2025-32441 describes for
     Rack's session middleware [86]. The moved session's idle and absolute
     timeouts start again, since NIST SP 800-63B-4 section 5.2 says that successful
     reauthentication "SHALL reset both timeouts" [41]. When the old session is no
     longer live, issue no new session, apply nothing and answer `401`, so the page runs the
     sign-out path. When the move fails for another reason, keep the old session, apply nothing,
     log it at `ERROR` ([logging.md](../../python/logging/logging.md) section 4) and answer `503`.
  2. Where the move left the old session in the store, destroy it before the request is applied.
     When destroying it fails, log it at `ERROR` ([logging.md](../../python/logging/logging.md)
     section 4), drop the new session, apply nothing and answer `503`, since ASVS 5.0 requirement
     16.5.3 asks to prevent fail-open conditions [56].
  3. Apply the request the answer came with, and only that request, and send its own answer with
     the new session cookie, an error answer included.

  A wrong or missing answer applies nothing, and the BFF keeps no change for a later request.

OWASP's Transaction Authorization cheat sheet, section 1.4, points the other way from the rule
that asks again for every factor of the sign-in: "applications should not require a user to
perform the same actions for authentication and transaction authorization", since malware can show
a false error and use the repeated sign-in to authorize a change of its own
[82]. That rule follows ASVS 5.0 requirement 7.5.1 instead,
because ASVS is the standard and the cheat sheet is guidance below it.

- **BFF: ask the page for re-authentication with a `403` whose JSON body carries a fixed code such
  as `reauth_required`, and never with a `401`,** because the page runs the sign-out path on every
  `401`. RFC 9470's `401` with the error `insufficient_user_authentication` is a resource server's
  challenge to its OAuth client, which here is the BFF [80]. So RFC 9470 governs the hop from
  the resource server to the BFF (section 3, "Forwarding tokens", says what the BFF does with it),
  not the hop to the page, and the signal to the page is this practice's choice. The `Page:` rules
  in [security.md](../../react/security/security.md) section 6 say what the page does with it.
- **BFF: after a change or removal of any authentication factor, a password changed by a reset or
  a recovery included, offer to end every other session of the user** (ASVS 5.0 requirement
  7.4.3), so a session stolen before the change stops working [42]. The rules below say
  how, by who logs the user in.
- **BFF, with the session's state on the server: index each session by its user, the ID token's
  `iss` and `sub` or the first-party user id, and by the provider's `sid`; write the index with
  the session, and fail the login, or the step-up's move to a new session id, when the index
  cannot be written,** so a back-channel logout, the end of a user's other sessions and the end of
  a disabled account find every session they name in one lookup, not a scan of every session.
  Back-Channel Logout 1.0 section 2.4 asks, for a logout token with no `sid`, that "all sessions
  at the RP for the End-User identified by the "iss" and "sub" Claims be logged out"
  [57]. A store read only by session id cannot find them: Spring Session's docs
  say that only some of its session stores can look up the sessions of one user, and that the
  application must fill the attribute that lookup reads, since "It is your responsibility to
  ensure that the attribute is populated" [87]. Failing the login follows ASVS 5.0
  requirement 16.5.3, which asks to prevent fail-open conditions [56]; the index is this
  practice's choice.
- **BFF, with an identity provider: leave the offer, and the end of the other sessions, to the
  provider, which owns the change of the factor, and end each session its back-channel logout
  names (the back-channel rules under "Logout" above),** since the BFF does not see a change made
  at the provider. ASVS 5.0's section on session termination, V7.4, lets the provider own it:
  "Session termination may be handled either by the application itself or by the SSO provider if
  the SSO provider is handling session management instead of the application" [42].
  Revoking refresh tokens does not stand in for it, since whether revoking one token ends the
  user's other grants depends on the provider's revocation policy, as RFC 7009 section 2.1 says
  [71].
- **BFF, with a first-party login: when the user accepts, destroy every other session of the user
  on the server, as the logout rules above destroy one, and when destroying one fails, log it at
  `ERROR` ([logging.md](../../python/logging/logging.md) section 4) and answer `503`,** since the
  BFF owns the change and keeps the sessions itself; the failure path is this practice's choice.
  A reply that says the other sessions ended while one still works is the fail-open condition
  ASVS 5.0 requirement 16.5.3 asks to prevent [56].
- **BFF: when an account is disabled or deleted, end every session of the user yourself: with the
  session's state on the server, destroy each session of the user, as the logout rules above
  destroy one; with the session's state in the cookie, set that user's per-user time to now
  ("Logout" above),** so a disabled or deleted account keeps no session that still works (ASVS 5.0
  requirement 7.4.2) [42]. Where the provider disables the account, its back-channel logout
  ends the sessions as the back-channel rules above say.

### Forwarding to resource servers

These rules say where the BFF forwards and what the forwarded request carries. Refreshing a token
before forwarding, and the answers to a resource server's `401`, are in section 3,
["Forwarding tokens"](#forwarding-tokens).

- **BFF: forward requests only to an allowlist of resource servers,** mapping each route to a
  fixed backend, validating the path of any dynamic route, and attaching the access token only to
  those requests (RFC 10017 section 6.1.3.6) [1]. A route that takes its host or path
  from the request can send the user's access token to another server.
- **BFF: forward each route only with the methods its resource server serves on it, and answer
  any other method with `405` and an `Allow` header that lists the methods it serves,** so a
  route mapped for reading cannot carry a write. RFC 10017 section 6.1.3.6 says that "restricting
  the allowed HTTP methods on a per-endpoint basis can further reduce attack vectors" [1].
  RFC 9110 section 15.5.6 says that the origin server "MUST generate an Allow header field in a
  405 response" [61]. Restricting the methods is this practice's choice.
- **BFF: build each forwarded request from an allowlist of the inbound request's headers: drop
  `Cookie`, any `Authorization` the client sent, and the custom and CSRF headers, and attach only
  the access token,** so the session cookie never reaches a resource server or its logs, and a
  header a script on the page wrote never stands beside the BFF's token. RFC 10017 section 6.1.1:
  "The BFF removes the cookie from the request, attaches the user's access token to the request,
  and forwards it to the actual resource server" [1].
- **BFF: when it forwards to more than one resource server, attach to each the access token issued
  for that server, asked for with a resource indicator where the provider supports one,** since
  RFC 9700 section 2.3 asks that access tokens be restricted to one resource server, or to a small
  set where that is not feasible, and ASVS 5.0 requirement 10.3.1 has a resource server refuse a
  token meant for another [16], [74]. RFC 9700 section 4.10.2 names resource
  indicators, specified in RFC 8707, as a way to get one token per resource server [16].
  With the session's state in the cookie, each extra token counts toward the cookie's 4096 bytes
  (the cookie-size rule in "The session's life, from login to logout" above).

### The login and logout responses

Good: the response of the BFF's login callback, as HTTP. The session value is cut as `…`, `<id>`
stands for the login attempt's id, and the response's `Location` header and the other headers
section 3 asks of every API response are left out. HTTP has no comment syntax, so the reason for
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
that enforces the prefix accepts the deletion [4]. The session cookie carries every
attribute the table asks for, so it keeps them in a browser that does not enforce the prefix (the
table's first row), and `no-store` keeps the response out of every cache
([security.md](../../react/security/security.md) section 13).

Good: the response of the BFF's logout endpoint, after it ended the session and revoked its
tokens, as the logout rules above say. The other headers section 3 asks of every API response are
left out. HTTP has no comment syntax, so the reason for each line is in the table above and in the
text after the block rather than at the line; that is this example's one departure from
[readability.md](../../any-language/readability/readability.md) section 4; the cost: the block
copied alone carries none of those reasons, so copy the table and that text with it.

```http
HTTP/1.1 200 OK
Content-Type: application/json
Set-Cookie: __Host-Http-session=; Secure; HttpOnly; Path=/; SameSite=Strict; Max-Age=0
Cache-Control: no-store

{"logoutUrl":null}
```

It is good because it answers `200` with a short JSON body, not `204`: the one API client parses
every response with its schema ([architecture.md](../../react/architecture/architecture.md) section
8), and an empty body has nothing to parse;
[security-example.md](../../react/security/security-example.md) section 1 shows that client.
`logoutUrl` is `null` here, and holds the provider's logout URL where the user should also leave
the identity provider, for the page to open by a top-level navigation (the rule on leaving the
identity provider, in "Logout" above). `Max-Age=0` removes the cookie at once, and the line
repeats every attribute the prefix requires: a browser that enforces the prefix rejects a
`Set-Cookie` without them, so the old cookie would stay [4]. It sends no
`Clear-Site-Data: "cookies"`, which would also clear the cookies of every other application on
`example.com` [76]. It sends no `Clear-Site-Data` at all: the response comes
from `api.example.com`, whose origin holds nothing the page stored, and the page clears what it
loaded through its sign-out path.

## 3. CSRF and CORS

### CSRF

A session cookie goes with every request to its site, including requests that another site makes
the browser send. Cross-site request forgery (CSRF) uses that: a page elsewhere submits a form to
your API, and the browser adds the user's cookie. RFC 10017 section 6.1.3.3 says "The BFF MUST
implement a proper CSRF defense", so every application with a cookie session needs one
[1]. Auth0, a vendor, describes the BFF as trading XSS-based token theft for this "more
constrained" risk (2026) [88]. The defence is the
server's; the browser side keeps its half.

OWASP's CSRF Prevention cheat sheet lists the defences in this order
[10]:

1. the framework's built-in CSRF protection, where it has one;
2. a token: a synchronizer token, or a signed double-submit cookie bound to the session with an
   HMAC (a plain double-submit cookie is open to cookie injection);
3. Fetch Metadata: the server rejects a state-changing request whose `Sec-Fetch-Site` header is
   `cross-site`, and checks `Origin` where the header is missing;
4. a custom request header on API calls;
5. `SameSite` cookies and origin checks, as defence in depth.

This practice asks for no token (item 2): the same cheat sheet names a custom request header as a
defence suited to an API that JavaScript calls, and one that needs no token
[10]. The cheat sheet also says that "CSRF tokens are
still essential for web applications that rely on cookies for authentication", and that a browser
bug that let a page send custom headers, or skipped the preflight, "could compromise your
security", against which a token adds a layer [10].
RFC 10017 section 6.1.3.3.3 says the anti-forgery cookie, a token kept in a cookie, "is not
necessarily recommended over the CORS approach" [1]. This practice follows the RFC,
because Fetch Metadata and the custom header are two mechanisms that one preflight bug does not
both break. That holds in every browser that sends Fetch Metadata; in an old browser that does
not, the custom header and the `Origin` check below are what remain. A framework's own token,
where the server already has one, stays on (item 1).

- **BFF: keep other applications and user content off the site the BFF shares with the page where
  you can, and when a subdomain's service is retired, remove its DNS record before you delete the
  resource it points to,** since `SameSite` "is adequate if the BFF is never considered to be same
  site with any other applications", and "a subdomain-takeover attack" against a sibling makes
  CSRF against the BFF possible again (RFC 10017 section 6.1.3.3.1); deleting the resource first
  leaves "an immediate window for takeover" (OWASP's Subdomain Takeover Prevention cheat sheet)
  [1], [89]. The rules on sibling subdomains in
  sections 2 and 3 stay for a site where this cannot hold.
- **The server applies the Fetch Metadata check to every request to an API route, reads
  included,** since the custom header holds only while the CORS policy stays tight (item 3 of
  OWASP's list above) [10]. OWASP's list checks
  state-changing requests; Fetch Metadata runs on reads too, as web.dev's Resource Isolation
  Policy does, so another site cannot load the API's answers into its own page for script
  inclusion (XSSI), cross-origin leaks or timing attacks (web.dev, "Protect your resources from
  web attacks with Fetch Metadata") [10],
  [24].
- **As part of the Fetch Metadata check, when `Sec-Fetch-Site` is absent, the server checks
  `Origin`: it rejects a request whose `Origin` names an origin outside the one setting of allowed
  origins ("What the server does"), and sends a request with neither header on to the
  custom-header check,** since some old browsers send no `Sec-Fetch-*` headers, and OWASP's CSRF
  cheat sheet calls this fallback "a mandatory requirement" for any Fetch Metadata implementation
  [10].
- **The server requires the custom header on every request to an API route,** since Fetch
  Metadata is absent from requests that old browsers send (item 4 of OWASP's list above)
  [10]. RFC 10017 section 6.1.3.3.2 says "the BFF SHOULD
  require that the browser-based application includes a custom request header", and "When this
  mechanism is used, the BFF MUST ensure that every incoming request carries this static header"
  [1].
- **The server keeps the framework's own CSRF protection on where it has one** (item 1 of OWASP's
  list above), so each check covers what another misses
  [10].
- **The server runs the custom-header and Fetch Metadata checks first, before the session lookup
  or any other work on the request,** so a forged request costs no session-store read, and its
  timing tells the other site nothing about the user's session. web.dev's Resource Isolation
  Policy says to "reject invalid requests before running authentication checks or any other
  processing of the request to prevent revealing sensitive timing information"
  [24].
- **API: when you add the Fetch Metadata check or the custom-header check to an API that already
  has users, run it in a log-only mode first, until a date you write down ("Write it down" in
  section 2 says where); fix each legitimate caller the log shows, or exempt it when it is one of
  the endpoints the table below names, and enforce the check on that date,** so a tab still on
  the previous bundle or a client nobody listed is not refused from the first deploy, and the
  check does not stay log-only, where it refuses nothing. web.dev gives these three steps for a
  Resource Isolation Policy, OWASP's CSRF cheat sheet says "Start in 'log only' mode", and
  [security.md](../../react/security/security.md) section 5 uses the same order for a new policy
  [24], [10]. The written date is this
  practice's choice.
- **API: in the log-only stage, also log the `User-Agent` of each request that arrives without
  `Sec-Fetch-Site`, and before you enforce, fix whatever strips the header when a current browser
  shows up in that log,** since a proxy, gateway or load balancer that removes `Origin` or the
  `Sec-Fetch-*` headers switches the Fetch Metadata check off silently, because a request with
  neither header goes on to the custom-header check. OWASP's CSRF cheat sheet says that
  intermediaries "may remove or modify `Origin` and `Sec-*` headers", calls such header stripping
  "problematic, but common", and asks to "Track which user agents include `Sec-Fetch-*`"
  [10].

### What the server does

#### Fetch Metadata and exemptions

- **When the page and the API are two origins of one site, let Fetch Metadata allow the page's
  exact origin, never every `same-site` request.** The page at `https://app.example.com` and the
  API at `https://api.example.com` are one site, so every request from the page arrives with
  `Sec-Fetch-Site: same-site` (the W3C Fetch Metadata draft) [25].
  OWASP's cheat sheet allows `same-site` only when the threat model trusts every sibling
  subdomain, and its sample code rejects it on state-changing methods; Filippo Valsorda's
  algorithm (2025) rejects it on those methods too, unless `Origin` equals a trusted origin,
  "compared by simple equality" [10], [90].
  So the server accepts `same-origin`, and a `same-site` request only when its `Origin` is exactly
  `https://app.example.com`, reads included (the rule above). When the API is on the page's own
  origin, the server accepts `same-origin` only. Fetch Metadata is Baseline in every major browser
  since March 2023 (MDN) [91].
- **API: keep the allowed origins in one setting per environment, read by the Fetch Metadata
  check, the CORS headers and the WebSocket check,** so a change of domain reaches all three checks
  at once; the rule is this practice's choice. In development the setting also holds the dev
  server's origin, and all three checks then accept it: the WebSocket check needs it, since Vite's
  proxy leaves that check to the target ([security.md](../../react/security/security.md) section
  11), and behind the proxy the page's other calls arrive as `same-origin`, so the CORS headers go
  unused there. Production's value holds the one origin of the application, so a review of it shows
  that the dev server's origin is absent.
- **Reject, with `403` and never `401`, a request to an API route that carries no custom header or
  whose Fetch Metadata check fails.** MDN's `Sec-Fetch-Site` page says a request that is not
  accepted should be rejected with a `403` [91]. A `401` tells the page its
  session has ended, so an origin set up wrong would turn into a sign-in loop.
- **Answer `401` only when the session has ended or never existed, and `403` to a request the user
  is not allowed to make** (RFC 9110 sections 15.5.2 and 15.5.4), because the page runs the
  sign-out path on every `401` ([security.md](../../react/security/security.md) section 6)
  [61]. The `401` carries no `WWW-Authenticate`: no registered authentication scheme
  describes a cookie session, and the page reads the status, not a challenge; this departs from
  the MUST of RFC 9110 section 15.5.2 and is this practice's choice [92],
  [61]. The logout endpoint is the exception: it answers success also when no session
  exists (section 2).
- **Exempt only the endpoints in the table below, each from the custom header, and from the Fetch
  Metadata check unless its row keeps that check, and guard each one as its row says,** since a
  request reaches each of them without the custom header. This table is this practice's departure
  from the MUST of RFC 10017 quoted above, and OWASP's CSRF Prevention cheat sheet asks for such
  an explicit list, each endpoint secured on its own [1],
  [10]. These endpoints skip the framework's own CSRF
  check too, since they cannot carry its token.

| Exempt endpoint | Matches by | Guarded by |
|---|---|---|
| the login start, a top-level `GET` | one exact path and the method `GET` | it changes neither the user's data nor the session; it starts a login attempt, which the login-cookie rules of section 2 bound |
| the login callback, which also completes a step-up | one exact path and its method | `state`, the nonce and the PKCE verifier bound to the login cookie (section 2) [16]; for a step-up, also the checks of section 2's step-up callback |
| the back-channel logout endpoint | one exact path and its method | validating the signed logout token, as the logout-token rule of section 2, "Logout", says |
| the report intake, a separate endpoint that takes anonymous reports | one exact path and its method | it reads no session, so a report carries no session to forge; the rule on reports below |
| the WebSocket handshake, a `GET` on its one path | one exact path and the method `GET` | the exact `Origin` check below |
| a file the page opens by navigation (a download link) | one route template (a fixed path with the record id as one encoded segment) and the method `GET`; when the request carries Fetch Metadata, also `Sec-Fetch-Mode: navigate` and a `Sec-Fetch-Dest` other than `object` or `embed`, the navigation test of web.dev's Resource Isolation Policy [24] | it changes nothing, and its answer goes to the user's own window, where no other site can read it (OWASP's CSRF cheat sheet: keep `GET` free of state changes) [10] |
| the CORS preflight | the method `OPTIONS` on any API path | it carries no cookie and no custom header, and changes nothing [93] |

A report the application sends about itself (web vitals, errors) goes to the report intake without
a cookie, through the `report` method of the API client; an endpoint that did read the session
would need the client's `request` method. Every other request to an API route without the header
is rejected. In a client-rendered application served as static files, the routes that serve the
page's own files (the HTML and its scripts) read no session, so neither check applies to them.
The RP-initiated logout needs no exemption: the page calls the logout endpoint through the API
client, so the call carries the custom header, and the navigation that follows goes to the
identity provider, not the BFF ([security.md](../../react/security/security.md) section 6). The
download link stays a navigation so that a large file goes to the browser's download manager, not
into the page's memory; a file the page shows goes through the API client and a blob instead
([security.md](../../react/security/security.md) section 7, "What the React code does").

- **Match each exemption only as its row in the table says, never by a request mode such as
  `Sec-Fetch-Mode: navigate` on its own, by a missing header or by a path prefix; add a route the
  page loads without `fetch` only as a last resort, as a row like the download link's: one route
  template, for a `GET` that changes nothing,** since a broader exemption lets a sibling
  subdomain's form through with the user's cookie, and every route in the table takes the cookie
  without the custom header. A request mode may narrow a row, as it does for the download link,
  but never matches on its own. The rule is this practice's choice. It departs from step 3.1 of
  OWASP's Fetch Metadata policy, which allows every simple top-level `GET` navigation so that
  other sites can link to the site: here the pages other sites link to are the page's own files,
  outside both checks, and the few API routes a page navigates to are listed one by one
  [10].
- **Treat each report the report intake receives as untrusted data: accept only the schema's
  fields, cap its size, limit how many reports one client sends in a time window, and never
  render it as HTML,** since the intake takes anonymous reports from anyone. OWASP's API Security
  Top 10 (2023, API4) asks for a maximum size on every payload and "a limit on how often a client
  can interact with the API within a defined timeframe"
  [94]. The rest of the guard is this practice's choice,
  after OWASP's advice to secure each exempted endpoint on its own
  [10].
- **Never change the user's data or session on a `GET`; the login start, which starts a login
  attempt, and the login callback, which creates the session or, after a step-up, replaces it,
  are the only exceptions, each guarded as its row in the exemption table says.** OWASP notes that
  `SameSite=Lax` does not cover a state change made with `GET`, since the cookie still goes with a
  top-level `GET` from another site [10].
- **When the session cookie is `SameSite=Strict`, keep the Fetch Metadata and custom-header checks
  on every API route anyway,** since `SameSite` is defence in depth: OWASP says it does not
  replace a proper CSRF defence in most deployments [10].
  It is scoped to the registrable domain, not the origin, so every subdomain of the site counts as
  same-site: Squarcina et al. (USENIX Security 2021) found vulnerabilities open to such a
  related-domain attacker on 887 of the top 50,000 sites of the Tranco list
  [10], [95]. Filippo Valsorda (2025)
  writes that the rollout of `Lax` by default has mostly failed and recommends `Sec-Fetch-Site`,
  which Go 1.25 ships as `CrossOriginProtection` [90], [96].
- **Next.js Server Actions: when a reverse proxy does not forward the public host in
  `x-forwarded-host`, list the host the browser shows in
  `experimental.serverActions.allowedOrigins`, written out exactly, never as a `*` or `**`
  pattern,** since a pattern accepts the sibling subdomains that the Fetch Metadata rule above
  refuses [97]. The framework compares the host of `Origin` with the host from
  `x-forwarded-host` or `host` on every action (Next.js's `serverActions` config page and its data
  security guide) [97], [98]. A post on the Next.js blog
  (2023) adds that Server Actions use no CSRF token [99].
- **For Server Functions and the framework's route actions, keep the Fetch Metadata check, keep
  the framework's own `Origin` check on where it has one, at a version that runs it on every
  unsafe method, and either have each call carry the custom header or add it to the exemption
  table as a row that skips the custom header only, whose guard also rejects a request with
  neither `Sec-Fetch-Site` nor `Origin`,** since each one is a public endpoint that anyone can send
  a `POST` to ([security.md](../../react/security/security.md) section 8), and the framework's
  runtime sends it, not the one API client. A framework's own check can be missing or partial:
  Next.js lets a request with no `Origin` through with a warning, and React Router's Framework
  Mode had no such check before 7.12.0 (CVE-2026-22030) and skipped `PUT`, `PATCH` and `DELETE`
  until 7.15.1 (CVE-2026-53663) [97], [100],
  [101], [102]. OWASP's CSRF cheat sheet says to reject a
  state-changing request when neither header establishes its origin, unless another CSRF defence
  succeeds [10]. The rule is this practice's choice.

#### Forwarding tokens

Where the BFF may forward a request, with which methods and headers, is section 2,
["Forwarding to resource servers"](#forwarding-to-resource-servers).

- **BFF: before you forward a request to a resource server, refresh an access token that has
  expired,** so the forwarded request carries a live token; RFC 10017 section 6.1.2.2 describes
  this refresh, done inline while the BFF handles the API call [1].
- **BFF: when a resource server answers `401` with any error other than
  `insufficient_user_authentication`, or with none, refresh once and forward the request once
  more; answer a second `401` to the page as `502` and log it, and never pass a resource server's
  `401` to the page,** since the page would read a `401` as a session that ended. RFC 6750
  section 3.1 lets the client "request a new access token and retry" after `invalid_token`, and a
  `401` means the request "has not been applied" (RFC 9110 section 15.5.2), so the retry does not
  apply a `POST` twice [103], [61]. The single retry and the `502` are this
  practice's choice.
- **BFF: when a resource server answers `401` with the error `insufficient_user_authentication`, do
  not refresh; answer the page `403` with `reauth_required`, and name the challenge's `acr_values`,
  when it carries them, in the `403`'s field that the `acr_values` rule of section 2,
  "Re-authentication", names, so that the step-up the page then starts asks for them, with the
  `max_age=0` the step-up rules of section 2 ask for, which also meets any `max_age` the challenge
  names,** since RFC 9470 uses that challenge to say that the user's authentication does not meet
  the resource server's needs, which a refreshed token does not change (section 2,
  "Re-authentication") [80].

#### WebSocket

- **API: check `Origin` on every WebSocket handshake against the page's exact origin (the one the
  Fetch Metadata rule allows), or the CORS allowlist when there is more than one,** and answer
  `403` to any other origin. The browser sends the session cookie with the handshake, the
  handshake cannot carry the custom header, and `SameSite` lets a sibling subdomain through, so
  without the check a page elsewhere opens a connection as the user (OWASP's WebSocket Security
  cheat sheet; the WebSockets standard; RFC 6455 section 10.2) [104],
  [105], [106].
- **BFF: tie each WebSocket connection to its session on the server, and close it when the
  session ends or gets a new id:** at logout, at the idle and absolute timeouts, when a
  back-channel logout or one of the refresh rules ends the session (section 2, "Logout" and
  "Timeouts and refresh"), and when a step-up issues a new session id (section 2,
  "Re-authentication"). The cookie is checked only at the handshake, so an open connection would
  keep sending the user's data after the session ended. A socket opened under the old id, perhaps
  by whoever planted or stole it, would outlive the renewal meant to end that id. OWASP's
  WebSocket Security cheat sheet asks to close the connections at logout and when the session
  expires, through a map of sessions to their connections [104]. OWASP's
  Session Management cheat sheet asks for a new session id at every change of privilege
  [8].
- **BFF: when you close a WebSocket connection because its session ended, use one close code of
  your own from 4000 to 4999, the range RFC 6455 section 7.4.2 reserves for private use, and use
  that code for nothing else,** so the page can tell an ended session from a dropped connection
  (1006) and from the server's other closes [106]. The page cannot learn it from a refused
  reconnect either, since the browser reports every failed handshake as 1006
  [105]. OWASP's WebSocket Security cheat sheet closes an expired
  session with 1008, the code its examples also use for a bad message, and Spring Session closes
  an expired session's sockets with 1008 too [104],
  [107]. IANA registers code 3000 as "Unauthorized", a name wider than an
  ended session [108]. Close a socket for any other reason, a new session id
  included, with another code, so the page checks the session and reconnects (the `Page:` rules
  in [security.md](../../react/security/security.md) section 7, "What the React code does"). The
  rule is this practice's choice.
- **BFF: check the session of each open WebSocket connection again at an interval no longer than
  the idle timeout,** so a socket still closes when its session ended and no event reached the
  instance that holds it. OWASP's WebSocket Security cheat sheet asks to re-validate the session
  periodically [104]. With the session's state in the cookie, the
  socket holds only its handshake's copy of the cookie, whose last-use time and tokens stay as
  they were while the user works through HTTP requests. Close it with the session-ended code only
  when the every-request check of section 2, "Logout", rejects that copy or its absolute timeout
  has passed. Close it with another code when only the copy's idle time or its tokens ran out, so
  the page checks the session and reconnects with the current cookie. The interval is this
  practice's choice.
- **BFF: with more than one instance, send each session end and each new session id to every
  instance, through the session store's events or a channel all instances read,** so the
  instance that holds a socket closes it at once, as the rules above say; the re-check above is
  only the backstop for an event that comes late. OWASP's WebSocket Security cheat sheet asks to
  close a user's connections "immediately" at logout, through "a mapping of sessions to active
  connections" [104]. Spring Session's guide says that the notice of an
  expired session from Redis "is not guaranteed to happen within 60 seconds", so Spring Session
  also runs "a background task every minute" that cleans up expired sessions
  [109]. The channel is this practice's choice.
- **BFF: count neither the WebSocket handshake nor the socket's keep-alive messages as activity
  on the idle clock, as section 2 does for the session check; count only the messages the user's
  actions send,** so a page that reconnects a dropped socket, or a socket that pings on a timer,
  does not keep an idle session alive (the polling rule in
  [security.md](../../react/security/security.md) section 6). OWASP's Session Management cheat
  sheet measures idle time from the last HTTP request, which a handshake is
  [8]. This practice reads it as the user's last action, as Spring
  Session does for messages ("Only messages sent from a user keep the session alive")
  [109]. With the session's state in the cookie, a socket message
  cannot move the cookie's idle clock, since no cookie comes back over a socket; the rule is this
  practice's choice.
- **BFF: authorise each WebSocket message that asks for an action as you would the same request
  over HTTP, and take a change that needs a step-up only over HTTP,** since a message inside an
  open socket skips the checks that run on each HTTP request, the CSRF checks and the step-up's
  `403` with `reauth_required` (section 2, "Re-authentication") among them. OWASP's WebSocket
  Security cheat sheet says: "Don't assume WebSocket connection equals unlimited access. Check
  authorization for each action" [104]. Taking a step-up's change only
  over HTTP is this practice's choice.

#### Paths and proxies

- **API: validate each dynamic path segment against the format of its id, such as
  `^[A-Za-z0-9_-]{1,64}$`, and reject any other value, and a segment that is `.` or `..` even
  when the format allows dots,** because a denylist of `.`, `..`, `/` and `\` has to foresee every
  encoded form, and one it misses becomes a traversal. The URL standard counts `%2e%2e` as a `..`
  segment, so a URL parser turns `/orders/%2e%2e/x` into `/x` (checked with Node 20's URL
  parser), and percent-encoding leaves `.` and `..` as they are (MDN on `encodeURIComponent`)
  [110], [111]. OWASP's Input Validation cheat
  sheet asks to define what the application accepts rather than recognise every malicious string,
  and RFC 10017 section 6.1.3.6 asks the BFF to validate dynamic routes strictly
  [112], [1].
- **BFF: when you build the URL you forward, percent-encode each validated path segment once, and
  have every proxy in front of the API pass the path on as the client sent it, never decoded,**
  since a segment decoded before the path is split turns an encoded `/` back into a separator,
  and a second decoding turns `%252F` into `/`. RFC 3986 section 2.4 asks to split a URI's path
  before decoding its parts and never to decode the same string twice [113]. OWASP's Input
  Validation cheat sheet asks to validate the decoded value and not decode it again downstream
  [112]. Encoding leaves `.` and `..` as they are, so the format check
  above is what stops them [111].
- **API: when nginx stands in front of the API, write its `proxy_pass` without a URI, and use no
  `rewrite` in the `location` that holds it,** so the API receives the path in the form the
  client sent it. nginx matches a `location` against the URI after it decodes `%XX` and resolves
  `.` and `..` [114]. Its `proxy_pass` with a URI passes that normalized
  URI on, and one without a URI passes "the full normalized request URI" once a `rewrite` has
  changed it (nginx's docs) [115]. For the same reason
  a `location` cannot validate the segment, since it matches the decoded, resolved URI.

#### Response headers

- **API: send these headers on every API response except the preflight's:**
  `Cache-Control: no-store`, a `Content-Type` that names the exact type of the body,
  `X-Content-Type-Options: nosniff`,
  `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`, and the API host's own
  `Strict-Transport-Security`. An HSTS header covers its own host and, with `includeSubDomains`,
  the names under that host (RFC 6797 section 6.1.2), so the page's header on `app.example.com`
  does not cover `api.example.com` [39]. The rule on HSTS for the whole registrable domain
  is in section 2, "Reading the `Cookie` header". The other headers keep the browser from guessing
  a body's type and running it, and keep the answer out of frames and caches (OWASP's REST
  Security cheat sheet) [116]. No HTTP cache keeps a preflight answer (RFC
  9110 section 9.3.7), and the preflight handler sends no body, so these headers have nothing to
  protect there; the browser's own preflight cache is keyed by origin and URL (the Fetch standard)
  [61], [93]. OWASP's REST Security cheat sheet also lists
  `X-Frame-Options: DENY`, "for compatibility with older browsers that do not support CSP Level
  2" [116]. This rule leaves it out and follows OWASP's HTTP Headers cheat
  sheet, which says that for "an API returning JSON data, X-Frame-Options does not provide any
  security" [117].
- **API: add `Sec-Fetch-Site, Origin` to `Vary` on every API response except the preflight's,
  after the values already there,** because the Fetch Metadata check decides the answer from
  those headers (the W3C Fetch Metadata draft, section 5.1; OWASP's CSRF cheat sheet)
  [25], [10]. No HTTP
  cache keeps a preflight answer (RFC 9110 section 9.3.7), and the browser's own preflight cache
  is keyed by origin and URL (the Fetch standard) [61], [93].
  The header list above already keeps these responses out of caches with `no-store`.
- **API: on the download route, send `Content-Disposition: attachment` with any file that came
  from outside,** so the browser saves it instead of showing it (MDN on `Content-Disposition`)
  [118]. Shown inline, an HTML or SVG file becomes a page on the API's
  origin. The policy above stops its script, but `default-src` does not cover `form-action` (CSP
  Level 3), so a form in it can still send what the user types to another site from the API's
  address [119]. Without the policy, its script would run where its requests
  are `same-origin` and carry the session cookie past every check in this section.

#### Logging

- **BFF: when you set up the alerts below, write the person or channel that receives security
  advisories and alerts into the decision log ("Write it down" in section 2 says where), send one
  test alert to it, and send every alert below to it,** so every alert has a recipient who acts
  on it, even after people change roles, also in a client-rendered application that never reads
  [security.md](../../react/security/security.md) section 8, and an alert path is not first tried
  in an incident; the rule is this practice's choice.
- **BFF: log at `INFO` ([logging.md](../../python/logging/logging.md) section 4) each request that
  a check rejects (the custom header, Fetch Metadata, `Origin`, the cookie name, a path format, a
  WebSocket's `Origin`) and each failed sign-in or re-authentication, with the check's name, the
  route and the `Origin` and `Sec-Fetch-Site` values,** so a CSRF probe, a planted cookie or an
  origin set up wrong leaves a trace. Each is an expected client error, which logging.md section
  4 keeps out of `WARNING`; the alert on the rejection rate below is what calls a person. OWASP's
  Logging cheat sheet asks to log authentication, access-control, session and input-validation
  failures, and ASVS 5.0 requirement 16.3.3 asks to log attempts to get past a security control
  [120], [56]. What never goes into a log is
  [logging.md](../../python/logging/logging.md) section 10.
- **BFF: cut each value that a rejected request supplies (the `Origin`, a cookie name, a path) to
  a fixed length before you log it,** so a probe cannot flood the log. OWASP's Logging cheat
  sheet asks to record a validation failure on data from another trust zone "with bounded, safe
  context", and to make sure logging cannot "deplete system resources" [120].
  Where the value goes in the log line, and how the JSON formatter escapes it against log
  injection, is [logging.md](../../python/logging/logging.md) sections 3 and 6. The same holds
  for each field of a report that the report intake writes to a log.
- **BFF: log at `INFO` each sign-in, re-authentication and logout that succeeds, and each new
  session id, with the user's id and the method, never the session id itself,** so an
  investigation can rebuild who held a session and when. OWASP's Logging cheat sheet asks to log
  "Authentication successes and failures", and its Session Management cheat sheet asks to
  "record session related events, such as the creation, renewal, and destruction of session IDs"
  [120], [8]. ASVS 5.0 requirement 16.3.1 asks that
  "all authentication operations are logged, including successful and unsuccessful attempts",
  with "the type of authentication or factors used", and requirement 16.2.5 says that session
  tokens "may only be logged by being hashed or masked" [56].
- **BFF: log at `INFO` each WebSocket connection the BFF opens and closes, with the user's id,
  the `Origin` and the close code,** since the HTTP access log shows only the handshake, and a
  burst of session-ended closes then shows in the log. OWASP's WebSocket Security cheat sheet
  says that "Traditional HTTP access logs only capture the initial WebSocket upgrade request",
  and asks to log "connection establishment and termination (with user identity, IP, and
  origin)" [104].
- **BFF: alert a person when the rejections of one check pass a rate the team writes down
  ("Write it down" in section 2 says where),** since OWASP Top 10:2025 A09 says that without
  alerting a team can hardly respond quickly and effectively to an incident [121].
  The rule is this practice's choice.
- **BFF, with an identity provider: alert a person on every step-up whose `iss` or `sub` does not
  match,** for the reason the rule on such a mismatch in section 2, "Re-authentication", gives;
  the rule is this practice's choice.
- **BFF, with an identity provider: alert a person on every back-channel logout that could not
  end its session (section 2, "Logout"),** since Back-Channel Logout 1.0 leaves sending the
  logout request again to the provider (section 2.5) and names nothing the provider does after
  the BFF's `400` (section 2.8), so the session may stay live until its timeouts
  [57]. The rule is this practice's choice.
- **BFF, with an identity provider: alert a person when valid back-channel logout tokens that
  match no session pass a rate the team writes down,** since a BFF whose stored `sid` never
  matches leaves live every session the provider ended, and section 2, "Logout", logs each such
  token at `INFO`, the level for what nobody will look at
  ([logging.md](../../python/logging/logging.md) section 4); the rule is this practice's choice.

### CORS

- **API: serve the API on the page's own origin, through a path such as `/api` on the same host,
  when the host allows,** so there is no CORS policy to get wrong. Such an API needs no allowlist,
  its requests "do not require any preflights" (RFC 10017 section 6.1.3.3.2), so no new URL waits
  for one, and Fetch Metadata marks each of them `same-origin` [1],
  [25]. OWASP Top 10:2025 A01 asks for "minimizing Cross-Origin
  Resource Sharing (CORS) usage" [67], and Duende's docs for its own BFF say the
  same-origin setup "eliminates CORS" [122]. The API answers CORS only
  because the page and the API are on two origins; the rules below hold when the two are split,
  as in the example.

The API's CORS response headers:

| Header | Value | Why |
|---|---|---|
| `Access-Control-Allow-Origin` | the application's one origin, `https://app.example.com`, on every response the browser can get from the API's host, including one from a gateway or proxy in front of it | with credentials the browser refuses `*`, and one fixed origin needs no `Origin` in `Vary` for CORS (the Fetch standard; the `Vary` rule below) [93]. Without it, or without the next row's header, the page sees a network error instead of the status, so a `401` from a gateway never reaches the sign-out path (MDN's CORS errors page) [123] |
| `Access-Control-Allow-Credentials` | `true`, on the same responses as the row above, the gateway's included | without it, the browser hides from the page any answer to a request that carried the cookie, a gateway's `401` included (the Fetch standard) [93] |
| `Access-Control-Allow-Methods` | the methods the API serves other than `GET`, `HEAD` and `POST`, such as `PUT`, `PATCH`, `DELETE`; leave the header out when it serves none | the browser lets `GET`, `HEAD` and `POST` past the preflight without the header, and with credentials `*` is a literal name, not a wildcard (the Fetch standard) [93]. Listing the rest keeps the policy to what is used |
| `Access-Control-Allow-Headers` | `Content-Type, X-Requested-With`, and the header that carries the framework's CSRF token, where the server issues one | the JSON body and the custom header start the preflight (MDN) [124]. The same `*` rule holds (the Fetch standard) [93] |
| `Access-Control-Max-Age` | `7200` | the browser caches a preflight answer per URL, for 5 seconds without this header; with it, repeat calls to the same URL skip the preflight, but every new URL (each record id, each query string) still waits for one (the Fetch standard) [93]. Chromium caps the value at 7200, Firefox at 86400 (MDN) [125] |
| `Access-Control-Expose-Headers` | only the response headers the page reads, often none | each listed header becomes readable by scripts on the allowed origin (MDN) [126] |

- **API: with more than one allowed origin, compare the request's `Origin` byte for byte with each
  entry of the list, written as the browser sends it (scheme, host and port, no trailing slash),
  and copy it back only on a match; never match by suffix, prefix, substring or regular
  expression.** ASVS 5.0 requirement 3.4.2 asks that `Access-Control-Allow-Origin` be "a fixed
  value by the application, or if the Origin HTTP request header field value is used, it is
  validated against an allowlist of trusted origins" [127]. The browser sends an origin
  with no trailing slash, so a list entry written with one never matches (the Fetch standard)
  [93]. A pattern goes wrong easily: a suffix check lets
  `evil-example.com` through and a prefix check lets `example.com.evil.net` through
  (PortSwigger's Web Security Academy, its CORS page) [128]. Chen et al. (USENIX
  Security 2018) found such validation mistakes on 10.4% of 481,589 CORS-configured sites, and an
  origin copied back unchecked on 3.3%, the flaw James Kettle (PortSwigger, 2016) calls "the
  single most common CORS vulnerability" [129],
  [130].
- **API: never allow every subdomain.** A subdomain on the list is as safe as its weakest page: an
  XSS there reads every answer (James Kettle, PortSwigger, 2016)
  [130]. OWASP's CSRF cheat sheet adds that an attacker
  who takes over such a subdomain can "forge a request with your custom header"
  [10].
- **API: never allow `null`.** It is the origin of any sandboxed frame an attacker builds (James
  Kettle, PortSwigger, 2016; MDN) [130],
  [131].
- **API: when the allowed origin depends on the request, add `Origin` to `Vary`, and never replace
  the `Vary` values already there.** Without it, a cache can hand one origin's answer to another
  (the Fetch standard, section "CORS protocol and HTTP caches") [93].
  A CORS layer that overwrote `Vary: Cookie` with `Vary: Origin` could let a CDN serve one user's
  data to another (Netty, CVE-2026-59903, fixed in 4.1.137.Final and 4.2.17.Final)
  [132]. With one fixed origin, CORS needs no `Origin` in `Vary`, so send
  `Access-Control-Allow-Origin` on every response (the Fetch standard, section "CORS protocol and
  HTTP caches") [93]. MDN's `Access-Control-Allow-Origin` page asks
  for `Vary: Origin` with any explicit origin, a fixed one included; this rule follows the
  standard [131]. The `Vary` rule of "Response headers" adds
  `Origin` to every API response anyway, for the Fetch Metadata check.
- **API: answer the preflight with `204` and the CORS headers, without the session and without the
  custom-header check; the preflight handler changes nothing.** A preflight `OPTIONS` request
  never carries the cookie, and it names the custom header in `Access-Control-Request-Headers`
  instead of sending it (the Fetch standard), so an `OPTIONS` route behind the session check or
  the header check fails every request it should allow [93]. The
  browser accepts a preflight answer only with a `2xx` status (the Fetch standard), so a `401`,
  `404` or `405` fails it too [93]. Spring Security's docs name the
  same failure: "the pre-flight request does not contain any cookies" [133].
- **API: count CORS as a CSRF defence only together with the custom-header check, and keep its
  policy tight, because that defence rests on it.** A request the browser may send without a
  preflight, such as a form's `POST`, reaches the API whatever the policy says; the browser only
  hides the answer (RFC 10017 section 6.1.3.3.2; MDN) [1], [134]. Chen et al.
  (USENIX Security 2018) found that the requests a script may send to another origin without a
  preflight let an attacker exploit CSRF flaws that were not exploitable before, such as one in a
  file upload [129]. The custom header forces a preflight, which "makes CORS
  an effective CSRF defense" (RFC 10017 section 6.1.3.3.2), but only against origins the policy
  refuses [1]. MDN's CSRF page says a site "will be vulnerable to a CSRF attack from a
  particular origin" when its answer lists that origin in `Access-Control-Allow-Origin` and sends
  `Access-Control-Allow-Credentials` [134], and OWASP's CSRF cheat sheet asks the server
  to allow only "a few select origins that you definitively control"
  [10].

Bad: the request's `Origin` copied back with no check. The request comes from a browser that sends
no Fetch Metadata, or reaches a server where another check is missing: a page on
`evil.example.com` fetches an invoice's PDF from the download route with the user's cookie, a
`GET` with no custom header, which needs no preflight. The other headers section 3 asks of this
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

The browser hands this answer to the page on `evil.example.com` [93].
What the reflected origin opens is reading: where no other check stops the request, as in a
browser that sends no Fetch Metadata, a page on any sibling subdomain can `fetch` a route such as
the download link with the user's cookie, and read the answer [2],
[93].

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
Metadata [93]. Why the other lines hold is in the same table.

### Fixing a CORS error

- **Fix a CORS error on the server, or behind a proxy you run; never in the page.** MDN says "Most
  CORS errors can only be resolved on the server", and the two page-side moves
  it lists break this API: a request rebuilt as a simple one drops the custom header that every
  API request must carry (section 3, "CSRF"), and `mode: "no-cors"` returns an answer whose
  "status is `0`, its headers are empty, and its body is not readable by JavaScript" (MDN)
  [123].
- **Fix a CORS error by adding the exact origin to the environment's allowed-origins setting
  (section 3, "What the server does"), never by allowing every origin or turning on a framework's
  option that copies the origin back,** since with credentials such an option lets any site read
  the answers. Chen et al. (USENIX Security 2018) found that 8 of the 11 CORS middleware they
  analysed turned `*` with credentials into a reflected origin, and Starlette's `CORSMiddleware`
  still does (its source at commit b7901fb) [129], [135]. The `cors`
  package for Express copies the origin back when its `origin` option is `true`, while ASP.NET
  Core "returns an invalid CORS response" when an application allows any origin together with
  credentials, so check what your framework does [136],
  [137].
- **A proxy you run forwards only to the hosts on the BFF's allowlist (section 2, "Forwarding to
  resource servers"), never to a URL the request names.** A proxy that forwards anywhere is
  server-side request forgery, which OWASP Top 10:2025 counts under A01 (CVE-2020-36851 in
  cors-anywhere) [67], [138].

## 4. Choosing a library or framework

The rules in sections 2 and 3 are what a team checks a library or a framework against before it
builds the BFF on one, since using a library does not make the BFF follow them: a library can get
a rule wrong or leave it out. Rack's session middleware let a request that was still running
bring back a session that a logout had deleted (CVE-2025-32441) [68]. A team
reports in dotnet/aspnetcore issue 53048 that ASP.NET Core keeps its login cookies after a
callback that carries an error [20]. RFC 10017 section 6.1.4.1 notes that "security
vulnerabilities in the BFF can have a significant impact on the application" [1]. Each
row below turns one problem into a question with a yes or no answer, and links the rule that says
what a yes must do.

| Problem | Ask of the library or framework | The rule it checks |
|---|---|---|
| a script or a sibling subdomain reads or plants the session cookie | Can you name the session cookie `__Host-Http-session`, and does the library write `Secure`, `HttpOnly`, `Path=/` and `SameSite` itself, with no `Domain`? | [section 2, "The session cookie"](#the-session-cookie) |
| the browser's default `SameSite` applies | Does it always write `SameSite`, and let you choose `Strict` or `Lax` for each cookie? | [section 2, "The session cookie"](#the-session-cookie) |
| `Secure` is off in production | Does it keep `Secure` on in every environment, with no setting that turns it off? | [section 2, "The session cookie"](#the-session-cookie) |
| the session outlives the browser | Is the session cookie non-persistent by default? | [section 2, "The session cookie"](#the-session-cookie) |
| a sibling subdomain plants the login cookie | Can its login cookie, the `state`, correlation or nonce cookie, take the `__Host-Http-` prefix with `Secure`, `HttpOnly`, `Path=/` and no `Domain`? | [section 2, "The login cookie"](#the-login-cookie) |
| a login in a second tab breaks the first one's callback | Does it keep each login attempt in a cookie of its own? | [section 2, "The login cookie"](#the-login-cookie) |
| the user edits or reads what a login attempt records | Does it keep the `state`, nonce and PKCE verifier encrypted and signed, in the login cookie or in `state`, and never in a record on the server? | [section 2, "The login cookie"](#the-login-cookie) |
| guessable login values | Does it draw the `state`, nonce and verifier from a secure random source for every attempt, with a 256-bit verifier and `S256`? | [section 2, "The login cookie"](#the-login-cookie) |
| login cookies left behind | Does it delete the login cookie at every callback, a callback that carries an error included? | [section 2, "The login cookie"](#the-login-cookie) |
| login cookies pile up until requests fail | Does it cap the login cookies a browser holds, or give you a hook at the login start to expire the extra ones? | [section 2, "The login cookie"](#the-login-cookie) |
| a login cookie lives on | Is the login cookie's lifetime bounded by default, and can you set it? | [section 2, "The login cookie"](#the-login-cookie) |
| an unreadable login cookie ends in an error | Does it treat a login cookie it cannot read as missing, and log the reason, instead of throwing? | [section 2, "The login cookie"](#the-login-cookie) |
| the failure page shows a request value | Can you replace its answer to a failed callback with a fixed page of your own? | [section 2, "The login cookie"](#the-login-cookie) |
| a `form_post` callback arrives without its cookie | Does it set the login cookie's `SameSite` to fit `response_mode`, and let you change it? | [section 2, "The login cookie"](#the-login-cookie) |
| an image or a frame on another site starts a login | Can your own check, such as the `Sec-Fetch-Dest` refusal, run before its login endpoint sets the login cookie? | [section 2, "The login cookie"](#the-login-cookie) |
| a mix-up between identity providers | With more than one provider, does it record the issuer of each attempt and check the `iss` of RFC 9207, or give each provider a callback path of its own? | [section 2, "The login cookie"](#the-login-cookie) |
| a `Cookie` header split into several lines | Does the server join every `Cookie` field line with `; ` before it parses them? | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| two cookies with one name | Does the parser give you every value of a repeated name, or the raw header, instead of keeping one of them without telling you? | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| a planted cookie read under the real name | Does the parser match cookie names byte for byte, with no trimming, case folding or URL-decoding? | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| one cookie string read as several | Is the server's legacy cookie parser, the RFC 2109 or RFC 2965 mode with `$Version` or commas, off by default, and can you keep it off? | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| the session cookie's value read through the framework's parser | Can your code read the session cookie's value from the raw `Cookie` header? | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| a planted cookie locks the user out | Can you add a header, such as `Clear-Site-Data`, to the library's own error answers? | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| known bugs in cookie parsing | Does the project publish advisories, and fix cookie-parsing bugs in the versions it supports? | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| the session check leaks a token or keeps a session alive | Does its user endpoint answer `401` with no session, return no token, send `Cache-Control: no-store`, and leave the idle clock alone? | [section 2, "The session's life, from login to logout"](#the-sessions-life-from-login-to-logout) |
| one instance cannot read another's sessions | Does it keep server-side sessions in a store that every instance reads? | [section 2, "The session's life, from login to logout"](#the-sessions-life-from-login-to-logout) |
| a cookie too large for the browser to store | With the session's state in the cookie, does it refuse to set a cookie over 4096 bytes, and tell you? | [section 2, "The session's life, from login to logout"](#the-sessions-life-from-login-to-logout) |
| a copy of the session store | Can access to the session store be limited to the BFF's own identity, with its backups encrypted? | [section 2, "The session's life, from login to logout"](#the-sessions-life-from-login-to-logout) |
| a key in the code | Does it load the client's credential and the cookie keys from a secret store, never from the code or a config file? | [section 2, "Keys and secrets"](#keys-and-secrets) |
| a guessable key | Does it generate keys from a CSPRNG, never from a password a person types? | [section 2, "Keys and secrets"](#keys-and-secrets) |
| a homemade cipher, or one key for every cookie | Does it protect cookies with authenticated encryption from a vetted library, with a separate key or subkey for each cookie? | [section 2, "Keys and secrets"](#keys-and-secrets) |
| instances that hold different keys | Does every instance load the same set of keys from one store? | [section 2, "Keys and secrets"](#keys-and-secrets) |
| rotation by trial over every key | Does each protected cookie carry a format version and the id of its key? | [section 2, "Keys and secrets"](#keys-and-secrets) |
| a rotation signs users out | Does a new key wait until every instance holds it before it protects cookies, and does an old key keep reading until the cookies it protected expire? | [section 2, "Keys and secrets"](#keys-and-secrets) |
| a leaked key keeps working | Can you revoke a key, and does the revocation reach running instances at once, not at their next refresh? | [section 2, "Keys and secrets"](#keys-and-secrets) |
| an unreadable cookie answers `500` | Does it treat a cookie it cannot read as no session, and give the reason for the log? | [section 2, "Keys and secrets"](#keys-and-secrets) |
| session fixation | Does it issue a new session id at login and at every re-authentication, and destroy the old session? | [section 2, "A new session id at login"](#a-new-session-id-at-login) |
| a failed destroy of the old session passes in silence | Does a failed destroy of the old session stop the login? | [section 2, "A new session id at login"](#a-new-session-id-at-login) |
| a session id the attacker chose | Does it refuse a session id it never created? | [section 2, "A new session id at login"](#a-new-session-id-at-login) |
| a guessable session id | Does it draw session ids from a CSPRNG, with at least 128 bits? | [section 2, "A new session id at login"](#a-new-session-id-at-login) |
| a session that never times out | Does it enforce an idle and an absolute timeout on the server, and does the absolute one survive a sliding renewal? | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| timeout values nobody can find | Are both timeout values settings, not constants in the code? | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| the provider signs the user in again without asking | Can it send `max_age` on a chosen login, and check `auth_time` at the callback? | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| one wrong setting signs every user out | Does it give you the token endpoint's error code, so you can end the session on `invalid_grant` and keep it on a setup error or an outage? | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| a refresh answer without a refresh token | Does it keep the old refresh token when a refresh answer carries none? | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| parallel refreshes count as reuse | Can it run one refresh per session at a time across instances, with a timeout on the token call and an expiry on its lock? | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| an outage lets a copied cookie through | When the session store or the list of ended sessions cannot be read, does it fail with an error, rather than sign the user out or accept the cookie? | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| a timed-out session keeps its tokens at rest | Does its server-side store delete a session's record when a timeout ends the session? | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| a logout that only deletes the cookie | Does logout delete the session on the server? | [section 2, "Logout"](#logout) |
| a request still running restores the session | Does the store refuse to save a session that ended after the request loaded it? Test it: start a slow request, log out while it runs, then let it finish. | [section 2, "Logout"](#logout) |
| a copied cookie works after logout | With the session's state in the cookie, does it keep one session id across re-issued cookies, and check a list of ended sessions and a per-user time on every request? | [section 2, "Logout"](#logout) |
| tokens outlive the logout | Does logout revoke the refresh token, and still end the session when the revoke fails? | [section 2, "Logout"](#logout) |
| a token in the provider's logout URL | Does it build the provider's logout URL from `end_session_endpoint`, and let you leave out `id_token_hint`? | [section 2, "Logout"](#logout) |
| a forged logout token | Does its back-channel logout run every check of Back-Channel Logout 1.0 section 2.6, offer the `logout+jwt` type check, and end every session of the user for a token with no `sid`? | [section 2, "Logout"](#logout) |
| a back-channel logout that fails in silence | Does it answer `400` when it cannot end the session, `200` when no session matches, and give you a hook to log and alert? | [section 2, "Logout"](#logout) |
| the provider's logout never reaches the BFF | Is back-channel logout its default, not front-channel logout? | [section 2, "Logout"](#logout) |
| the old cookie stays in the browser | Does logout send `Max-Age=0` with every attribute the prefix needs? | [section 2, "Logout"](#logout) |
| a logout signs the user out of other applications | Does it leave `Clear-Site-Data: "cookies"` off by default, or let you turn it off? | [section 2, "Logout"](#logout) |
| a scan of every session to find one user's | Can its session store find every session of one user, and of one `sid`, in one lookup? | [section 2, "Re-authentication"](#re-authentication) |
| an old sign-in passes a step-up | Can its login start take `max_age=0` and `acr_values` for each request, and does its callback give you the new ID token's `auth_time` and `acr`? | [section 2, "Re-authentication"](#re-authentication) |
| a thief steps up as another user | Can the callback compare the new ID token's `iss` and `sub` with the session's, and refuse, before it issues a session? | [section 2, "Re-authentication"](#re-authentication) |
| one step-up lets every change through | Can a route ask for a re-authentication younger than a window you set, kept on the server, and clear it after one change? | [section 2, "Re-authentication"](#re-authentication) |
| a step-up keeps the old timeouts | Does a successful step-up start the idle and absolute timeouts again? | [section 2, "Re-authentication"](#re-authentication) |
| a step-up's callback sends the user to any URL | Does a step-up's callback send the user back only to a fixed route of the page, never to a URL taken from the request? | [section 2, "Re-authentication"](#re-authentication) |
| a first-party step-up asks for less than the sign-in | Does its step-up ask for every factor the account signs in with, a passkey included? | [section 2, "Re-authentication"](#re-authentication) |
| one answer covers more than one change | Does it check the answer inside the guarded request itself, not only through a "recently signed in" window? | [section 2, "Re-authentication"](#re-authentication) |
| a thief answers with their own password | Does it check the answer against the session's own user? | [section 2, "Re-authentication"](#re-authentication) |
| password guessing through the step-up | Does it count step-up answers with an atomic operation of the store, and add a wrong one to the account's own failure count? | [section 2, "Re-authentication"](#re-authentication) |
| an honest user loses the session after old mistakes | Does it clear that count after a successful step-up? | [section 2, "Re-authentication"](#re-authentication) |
| the page signs out when a step-up is due | Can its re-authentication challenge come back as a `403` with a fixed code, not as a redirect or a `401`? | [section 2, "Re-authentication"](#re-authentication) |
| a step-up brings back a session that just ended | At a re-authentication, does it move the session to a new id, and refuse to move a session that ended during the request? | [section 2, "Re-authentication"](#re-authentication) |
| other sessions live on after a factor change | Can it end every other session of a user, and report a failed end? | [section 2, "Re-authentication"](#re-authentication) |
| a disabled account keeps its sessions | Can it end every session of a user and, with the session's state in the cookie, reject cookies issued before a per-user time? | [section 2, "Re-authentication"](#re-authentication) |
| the access token goes to any host | Does its proxy forward only to configured routes, with each route's methods and path checks? | [section 2, "Forwarding to resource servers"](#forwarding-to-resource-servers) |
| the session cookie reaches a resource server | Does it drop `Cookie` and the inbound `Authorization` header by default? | [section 2, "Forwarding to resource servers"](#forwarding-to-resource-servers) |
| one token for every resource server | Can it hold a separate access token for each resource server, and attach the right one? | [section 2, "Forwarding to resource servers"](#forwarding-to-resource-servers) |
| an expired or rejected access token | Does it refresh an expired access token before it forwards, and retry once after a resource server's `401`? | [section 3, "Forwarding tokens"](#forwarding-tokens) |
| a step-up challenge read as an expired token | Does it treat a resource server's `insufficient_user_authentication` as a step-up, not a refresh, and read the challenge's `acr_values`? | [section 3, "Forwarding tokens"](#forwarding-tokens) |
| a sibling subdomain passes the CSRF check | Does it treat a `same-site` request as untrusted unless its `Origin` equals a configured full origin, on reads too? | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| a request with no Fetch Metadata | When `Sec-Fetch-Site` is absent, does it compare `Origin` exactly, and let you reject a request with neither header on the routes you choose? | [section 3, "CSRF"](#csrf) |
| an exemption wider than one route | Can it require one fixed header on every API route, and exempt routes only by exact path and method? | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| a refused request read as an ended session | Does a failed check answer `403`, and an API call without a session `401`, not a `302` to the login page? | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| a new check refuses real users from the first deploy | Does it have a log-only mode that logs `Origin`, `Sec-Fetch-Site` and `User-Agent`? | [section 3, "CSRF"](#csrf) |
| framework actions open to CSRF | Does the framework's own `Origin` check run on every unsafe method, reject a request with no `Origin`, and match exact hosts? | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| three lists of allowed origins drift apart | Can the CSRF, CORS and WebSocket checks read one setting of allowed origins? | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| an anonymous route floods | Can it limit the size and the rate of one anonymous route on its own? | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| CORS lets any origin read the answers | Does its CORS layer compare origins against an exact list, refuse, not copy back, any origin with credentials, and offer no switch that allows every subdomain? | [section 3, "CORS"](#cors) |
| a CORS layer overwrites `Vary` or reflects headers | Does it add `Origin` to `Vary` instead of replacing the header, and take a fixed list of allowed headers instead of copying `Access-Control-Request-Headers`? | [section 3, "CORS"](#cors) |
| the preflight fails | Does it answer the preflight with a `2xx` before authentication runs? | [section 3, "CORS"](#cors) |
| cross-site WebSocket hijacking | Does its WebSocket server check `Origin` against an exact list by default, and refuse other origins with `403`? | [section 3, "WebSocket"](#websocket) |
| a socket outlives its session | Does it close a session's sockets when the session ends or gets a new id, on every instance? | [section 3, "WebSocket"](#websocket) |
| the page cannot tell an ended session from a dropped socket | Can you choose the close code it uses when the session ends? | [section 3, "WebSocket"](#websocket) |
| sockets keep an idle session alive | Can you leave the handshake and keep-alive messages off the idle clock? | [section 3, "WebSocket"](#websocket) |
| a socket checks an old copy of the cookie | With the session's state in the cookie, does its periodic check read the list of ended sessions, not only the cookie the handshake carried? | [section 3, "WebSocket"](#websocket) |
| path traversal through an encoded segment | Does the router route on the path as sent, without resolving `%2e%2e` or decoding `%2F` first? | [section 3, "Paths and proxies"](#paths-and-proxies) |
| a path decoded twice | Does its HTTP client encode each segment it inserts exactly once, and pass the inbound path on without decoding it? | [section 3, "Paths and proxies"](#paths-and-proxies) |
| a body run as a page, or kept in a cache | Does it set `Cache-Control: no-store`, `nosniff` and the policy on every API response, error answers included? | [section 3, "Response headers"](#response-headers) |
| a file shown on the API's origin | Does its file helper send `Content-Disposition: attachment` by default? | [section 3, "Response headers"](#response-headers) |
| a probe floods the log | Does the logger cap the length of values taken from requests, and escape line breaks in them? | [section 3, "Logging"](#logging) |
| security events missing from the log | Can it log each rejected check and each failed sign-in without the cookie's value or a token? | [section 3, "Logging"](#logging) |
| an alert reaches nobody | Does the alerting platform send each alert to a named recipient, and can you send a test alert? | [section 3, "Logging"](#logging) |

When a library answers no, write that rule's code yourself, or wrap the library so that the rule
holds around it, as the rule says: the login-cookie and key rules of section 2 are checks on the
library, with code of your own only for a rule it does not meet. Run a row's test, such as the one
for the logout race, against the version you pick, and again when you update it.

## 5. Where the rules stop holding

- **A script that runs on the page still acts as the user through the BFF,** since its requests
  carry the session cookie and the custom header like the page's own, and RFC 10017 section 5.1.4
  says they "are indistinguishable from requests sent by the legitimate application"; the BFF
  keeps the tokens from it, not its requests [1]. RFC 10017 section 6.1.4.1 says "nothing
  will be able to prevent such attacks apart from stopping the execution of malicious code in the
  first place", and names the BFF as "the ideal place" for anomaly detection or rate limiting
  [1]. The page's side is [security.md](../../react/security/security.md) section 6.
- **A copy of the session cookie works until its session ends,** by logout, a timeout or a
  back-channel logout, whether the session's state is on the server or in the cookie: the BFF
  cannot tell the copy from the original. RFC 10017 section 6.1.3.2 notes that an encrypted cookie
  "still allows the attacker to use the encrypted cookie in a session hijacking attack"
  [1]. With the state in the cookie, the list of ended sessions is what stops the copy at
  that end (section 2, "Logout").
- **With the session's state in the cookie and a provider that rotates refresh tokens, a refresh
  whose answer never reaches the browser,** such as one for a cancelled query or a dropped
  connection, loses its `Set-Cookie`: the browser keeps the old refresh token, and when its next
  request comes after the provider's reuse window, the provider counts it as reuse, revokes the
  active refresh token and the user is signed out (section 2, "Timeouts and refresh"; RFC 9700
  section 4.14.2) [16].
- **A back-channel logout that the BFF cannot carry out,** because its session store cannot be
  written, can leave the session live until its timeouts; only the `ERROR` line of section 2 and
  its alert (section 3, "Logging") show it.
- **A BFF that the provider cannot reach,** such as one behind a firewall or NAT with a public
  provider, gets no back-channel logout, so a session ended at the provider lives on in the BFF
  until its timeouts. Back-Channel Logout 1.0 section 1 says the RP's back-channel logout URI
  "must be reachable from all the OPs used", so "the RP cannot be behind a firewall or NAT when
  used with public OPs" [57].
- **A login start that arrives from another site,** such as a link in an email, carries no
  `Strict` session cookie, so the BFF cannot record the old session id, and the old session lives
  on until its own timeouts or its logout (section 2, "A new session id at login")
  [2].
- **Another site can still send the user to the login start by a top-level navigation,** which the
  `Sec-Fetch-Dest` check of section 2 lets through; in a browser that sends no Fetch Metadata, the
  check does not stop an image or a frame either, whose login cookie a browser that follows the
  cookie spec stores only with `response_mode=form_post` (section 2) [2]. Each such
  request starts a login attempt; the cap on login cookies keeps their number small, but it can
  push out the cookie of an attempt the user started, whose sign-in then has to start again.
- **Where other applications or user content share the application's site (section 3, "CSRF"), a
  sibling subdomain can lock a user out:** a cookie it plants that the cookie checks of section 2
  refuse makes every request of that user answer `400` until the cookie expires or the user clears
  the site's data. A team that controls the registrable domain can send `Clear-Site-Data: "cookies"`
  with that `400`, at the cost the rule in section 2, "Reading the `Cookie` header", names; the
  browser then removes the cookie at the first such answer. This practice accepts that trade, since
  reading a planted value instead would let the attacker choose the session. GitHub (2013) took a
  third way: the server answers with a `Set-Cookie` that expires the planted cookie, once for each
  part of the path [139]. This practice does not ask for it, since
  no source read for it shows which browsers delete a cookie whose name is not a token, such as one
  that starts with U+2000, and GitHub writes that a cookie overflow cannot be blocked that way from
  the server [139].
- **A browser that stores a cookie with an empty name whose value starts with `__Host-`** sends
  only its value in the `Cookie` header, such as `__Host-Http-session=<id>`, which the server
  cannot tell from the real cookie. The RFC 6265bis draft asks browsers to ignore such a cookie
  (section 5.7), and Firefox fixed it in Mozilla bug 1779993 [2],
  [140]. Which other browsers ignore it was not checked.
- **A framework that decodes or rewrites cookie names** can read a planted cookie as the session
  cookie although its name passes the check of section 2: PHP URL-decoded cookie names before
  7.2.34, 7.3.23 and 7.4.11 (CVE-2020-7070), and parsed a name that starts with `_[Host-` as
  `__Host-` before 8.1.28, 8.2.18 and 8.3.6 (CVE-2024-2756, PHP's advisory GHSA-wpj3-hf5j-x4v4)
  [141], [142]. The session cookie's value comes from the BFF's own parse
  of the raw header (section 2, "Reading the `Cookie` header"), so the gap stays open only for the
  login cookie, which the OpenID Connect library reads. Keep the framework patched
  ([security.md](../../react/security/security.md) section 10).
- **A BFF on another registrable domain gets no session cookie from the page's requests:** the
  cookie rules of section 2 set `SameSite=Strict`, as RFC 10017 section 6.1.3.2 asks, and a
  browser never sends such a cookie on a cross-site request (RFC 6265bis draft, section 5.8)
  [1], [2]. A cookie used across sites needs `SameSite=None` (MDN), which
  gives up that CSRF defence and makes it a third-party cookie: Safari's tracking prevention
  restricts it by default, Firefox keeps it in a separate jar per site, and Chrome blocks it only
  in Incognito mode or when the user asks (MDN's third-party cookies guide)
  [143]. `Partitioned` does not change that, since it applies to cross-site
  cookies, which still need `SameSite=None` [143]. The cookie rules of
  section 2 assume the BFF shares the application's site, as `api.example.com` does.
- **Pages the server renders read the session on navigations from other sites,** such as a link
  in an email, so their session cookie takes `Lax` instead of `Strict` (section 2) [134].
- **A first-party login's credential checks** are outside this practice: password storage,
  protection against automated attacks on the login itself, such as login throttling (section 2
  limits only the answers to a step-up, and feeds a wrong one into the sign-in's own failure count
  where it keeps one), and one generic message for a failed sign-in.
  OWASP's Authentication and Password Storage cheat sheets are where to look.
- **A team at ASVS Level 1, or one whose identity provider holds the email, the phone, the second
  factor and the recovery data and asks for re-authentication itself,** may skip the step-up rules
  of section 2's "Re-authentication", which serve the Level 2 requirement 7.5.1, and writes the
  choice down [42].
- **Four Level 2 session requirements of ASVS 5.0** are left to a team that works at that level
  ([security.md](../../react/security/security.md) section 17). The session rules of section 2
  cover the Level 1 requirements of ASVS 5.0 chapter V7 and the Level 2 requirements they cite
  [42]. They leave out 7.4.5, an administrator ends one user's sessions or all of them;
  7.5.2, users see and end their own sessions; 7.6.1, the application's and the provider's
  sessions end as documented, with the user signed in again where needed, beyond the choice
  section 2 asks to write down; and 7.6.2, a new session starts only with the user's consent or
  an explicit act [42].

## 6. Review checklist

| Section | Ask | Red flag |
|---|---|---|
| 2. Sessions, server | Does the server end the session at logout and on timeout? | a callback page that shows a parameter of the request; a session cookie or login cookie without the `__Host-Http-` prefix; a session cookie without `Secure`, `HttpOnly` or a written `SameSite`, or with `Domain`; a session or login cookie read without checking that its name appears once, or with a duplicate check that reads only the first `Cookie` field line; a cookie whose name becomes the session or login cookie's name once non-token characters are removed and ASCII letters are lowercased, read instead of answered with `400`; a `Cookie` header that starts with `$Version` accepted, or a cookie parser set to a legacy RFC 2109 or RFC 2965 mode; a session cookie value read from the framework's cookie collection, or looked up or decrypted before its format is checked; a login attempt's record kept on the server, or in a cookie or `state` that is not encrypted and signed; a BFF with more than one identity provider that checks neither `iss` nor a callback path for each provider; a login cookie left behind after a failed callback; a cookie key kept in the code, or shared between environments; a new key that protects cookies before every instance holds it; an unreadable cookie answered with `500`; the same session id before and after login; a session kept after `invalid_grant` or `interaction_required`; a stored refresh token emptied by an answer that carries none; a timed-out session's record left in the store; a logout that only deletes the cookie; a session that a late request can save back after logout; a logout token accepted without the checks of Back-Channel Logout 1.0 section 2.6; a timeout kept only in the page; a session accepted when the session store or the list of ended sessions cannot be read; a step-up that does not compare `iss` and `sub`; a step-up without the `auth_time` or `acr` check, or not bound to its session; a guarded change let through outside the re-authentication window, or twice in one window; a step-up guess count kept in the session object the request loaded; a step-up answer in the URL; a step-up that moves the session from the copy the request loaded; a disabled account whose sessions wait for the provider; a WebSocket that stays open after logout; a BFF route that forwards to a host or path taken from the request, or with a method its resource server does not serve; one access token sent to several resource servers |
| 3. CSRF and CORS, server | Does the API allow only exact origins, change no user data or session on a `GET`, and exempt only the endpoints section 3 lists? | a change to the user's data or session on a `GET` other than the login start or the login callback, which creates the session or, after a step-up, replaces it; `Access-Control-Allow-Origin` copied from the request unchecked, matched by suffix or pattern, `null`, or `*` with credentials; a framework's any-origin option turned on with credentials; a preflight answered with a status other than `2xx`, or placed behind the session check; a Fetch Metadata check that allows every `same-site` request; a custom-header or Fetch Metadata check that runs after the session lookup; a WebSocket handshake with no `Origin` check; an API route that accepts a request without the custom header; a dynamic path segment not checked against its format; a CSRF exemption by request mode, by a missing header or by path prefix; a report intake with no rate limit; an `allowedOrigins` entry written as `*` or `**`; a framework's action check on a version that skips `PUT`, `PATCH` or `DELETE`; a resource server's `401` passed to the page; a file from outside served inline on the download route; a check or a policy still log-only after its written end; a rejected check, a failed sign-in or re-authentication, or a session that could not be ended, with no log line; no alert on the rejection rate or on a step-up from another account |

## 7. Sources

Checked 2026-10-17 unless a line ends with — checked <YYYY-MM-DD>.

- [1] IETF — RFC 10017, OAuth 2.0 for Browser-Based Applications, BCP 212, August 2026 — https://www.rfc-editor.org/rfc/rfc10017.txt
- [2] IETF — Cookies: HTTP State Management Mechanism, draft-ietf-httpbis-rfc6265bis-22 — https://www.ietf.org/archive/id/draft-ietf-httpbis-rfc6265bis-22.txt
- [3] IETF HTTP Working Group — Cookies: HTTP State Management Mechanism, draft-ietf-httpbis-layered-cookies-02 — https://www.ietf.org/archive/id/draft-ietf-httpbis-layered-cookies-02.txt
- [4] MDN — Set-Cookie header — https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/http/reference/headers/set-cookie/index.md
- [5] web-platform-tests — wpt.fyi results for `cookies/prefix` and `cookies/samesite`, stable aligned runs of 2026-10-06 (Chrome 154, Edge 154, Firefox 157, Safari 27.0) — https://wpt.fyi/api/search?run_ids=6218298311311360,4877098740350976,5164107446878208,5139408432136192&q=cookies%2Fprefix
- [6] web-platform-tests — Safari 27.0 subtest results for `cookies/prefix` and `cookies/samesite`, stable aligned run of 2026-10-06 — https://storage.googleapis.com/wptd/cc74d2669f5de548e808779877d1d33339ec5115/safari-27.0__22625.1.29.11.27_-mac-27.0-434012013c/cookies/prefix/__host.header.https.html
- [7] MDN — browser-compat-data, `http/headers/Set-Cookie.json` — https://raw.githubusercontent.com/mdn/browser-compat-data/main/http/headers/Set-Cookie.json
- [8] OWASP — Session Management Cheat Sheet — https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Session_Management_Cheat_Sheet.md
- [9] MDN — Cookies Having Independent Partitioned State (CHIPS) — https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies/Partitioned_cookies
- [10] OWASP — Cross-Site Request Forgery Prevention Cheat Sheet — https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md
- [11] Duende Software — BFF documentation, "Getting Started - Single Frontend" — https://docs.duendesoftware.com/bff/getting-started/single-frontend/
- [12] Duende Software — BFF documentation, "ASP.NET Core Authentication System" (the session handlers page) — https://docs.duendesoftware.com/bff/fundamentals/session/handlers/
- [13] Microsoft — ASP.NET Core source, `RemoteAuthenticationHandler.cs` and `RemoteAuthenticationOptions.cs` — https://github.com/dotnet/aspnetcore/tree/main/src/Security/Authentication/Core/src
- [14] IETF — RFC 7636, Proof Key for Code Exchange by OAuth Public Clients, September 2015 — https://www.rfc-editor.org/rfc/rfc7636.txt
- [15] IETF — RFC 6749, The OAuth 2.0 Authorization Framework, October 2012 — https://www.rfc-editor.org/rfc/rfc6749.txt
- [16] IETF — RFC 9700, Best Current Practice for OAuth 2.0 Security, BCP 240, January 2025 — https://www.rfc-editor.org/rfc/rfc9700.txt
- [17] OWASP — Application Security Verification Standard, 5.0.0 — https://github.com/OWASP/ASVS/tree/v5.0.0_release/5.0/en
- [18] Microsoft — ASP.NET Core source, `OpenIdConnectHandler.cs` — https://github.com/dotnet/aspnetcore/blob/main/src/Security/Authentication/OpenIdConnect/src/OpenIdConnectHandler.cs
- [19] IETF — RFC 9207, OAuth 2.0 Authorization Server Issuer Identification, March 2022 — https://www.rfc-editor.org/rfc/rfc9207.txt
- [20] JeroMiya — /signin-oidc does not unset nonce and correlation cookies with param error=login_required from failed identity server prompt=none request (GitHub, dotnet/aspnetcore issue 53048, 2023; case) — https://github.com/dotnet/aspnetcore/issues/53048
- [21] AndyWangMSFT — Correlation/Nonce cookies accummulated causing Nginx Request Header Or Cookie Too Large (GitHub, dotnet/aspnetcore issue 58731, 2024; case) — https://github.com/dotnet/aspnetcore/issues/58731
- [22] Microsoft — Key management in ASP.NET Core — https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/implementation/key-management
- [23] MDN — `Sec-Fetch-Dest` — https://github.com/mdn/content/blob/main/files/en-us/web/http/reference/headers/sec-fetch-dest/index.md
- [24] Lukas Weichselbaum — Protect your resources from web attacks with Fetch Metadata (web.dev, Google, 2020; opinion) — https://web.dev/articles/fetch-metadata
- [25] W3C — Fetch Metadata Request Headers, Working Draft, 21 September 2026 — https://www.w3.org/TR/2026/WD-fetch-metadata-20260921/
- [26] Duende Software — BFF documentation, "BFF Silent Login Endpoint" — https://github.com/DuendeSoftware/docs.duendesoftware.com/blob/main/astro/src/content/docs/bff/fundamentals/session/management/silent-login.md
- [27] OpenID Foundation — OpenID Connect Core 1.0, incorporating errata set 2 — https://openid.net/specs/openid-connect-core-1_0.html
- [28] Microsoft — Work with SameSite cookies in ASP.NET Core — https://learn.microsoft.com/en-us/aspnet/core/security/samesite
- [29] Zakhar Fedotkin — Cookie Chaos: How to bypass `__Host` and `__Secure` cookie prefixes (PortSwigger Research, 2025; research, sponsored by PortSwigger) — https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes
- [30] IETF — RFC 9113, HTTP/2 — https://www.rfc-editor.org/rfc/rfc9113.txt
- [31] IETF — RFC 6265, HTTP State Management Mechanism — https://www.rfc-editor.org/rfc/rfc6265.txt
- [32] Django — `django/http/cookie.py` — https://raw.githubusercontent.com/django/django/main/django/http/cookie.py
- [33] Microsoft — ASP.NET Core source, `RequestCookieCollection.cs` and `CookieHeaderParserShared.cs` — https://raw.githubusercontent.com/dotnet/aspnetcore/main/src/Http/Http/src/Internal/RequestCookieCollection.cs
- [34] Mozilla — Security Vulnerabilities fixed in Firefox 127, MFSA 2024-25 (CVE-2024-5699) — https://www.mozilla.org/en-US/security/advisories/mfsa2024-25/
- [35] Apache Tomcat — `java/org/apache/tomcat/util/http/parser/Cookie.java`, branches 9.0.x, 10.1.x, 11.0.x and main — https://raw.githubusercontent.com/apache/tomcat/9.0.x/java/org/apache/tomcat/util/http/parser/Cookie.java
- [36] Eclipse Jetty — `RFC6265CookieParser.java`, `CookieCompliance.java` and `HttpConfiguration.java`, 12.1.x — https://raw.githubusercontent.com/jetty/jetty.project/jetty-12.1.x/jetty-core/jetty-http/src/main/java/org/eclipse/jetty/http/RFC6265CookieParser.java
- [37] W3C Web Application Security Working Group — Clear Site Data, Editor's Draft (Bikeshed source) — https://raw.githubusercontent.com/w3c/webappsec-clear-site-data/main/index.src.html
- [38] MDN — browser-compat-data, `http/headers/Clear-Site-Data.json` — https://raw.githubusercontent.com/mdn/browser-compat-data/main/http/headers/Clear-Site-Data.json
- [39] IETF — RFC 6797, HTTP Strict Transport Security (HSTS) — https://www.rfc-editor.org/rfc/rfc6797.txt
- [40] Duende Software — BFF User Endpoint — https://docs.duendesoftware.com/bff/fundamentals/session/management/user/
- [41] NIST — SP 800-63B-4, Digital Identity Guidelines: Authentication and Authenticator Management — https://pages.nist.gov/800-63-4/sp800-63b.html
- [42] OWASP — Application Security Verification Standard, V7 Session Management, 5.0.0 — https://github.com/OWASP/ASVS/blob/v5.0.0_release/5.0/en/0x16-V7-Session-Management.md
- [43] IETF — RFC 8414, OAuth 2.0 Authorization Server Metadata — https://www.rfc-editor.org/rfc/rfc8414.txt
- [44] OWASP — Application Security Verification Standard, V13 Configuration, 5.0.0 — https://github.com/OWASP/ASVS/blob/v5.0.0_release/5.0/en/0x22-V13-Configuration.md
- [45] Microsoft — Configure ASP.NET Core Data Protection — https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/configuration/overview
- [46] OWASP — Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- [47] OWASP — Application Security Verification Standard, V11 Cryptography, 5.0.0 — https://github.com/OWASP/ASVS/blob/v5.0.0_release/5.0/en/0x20-V11-Cryptography.md
- [48] expressjs — express-session README — https://github.com/expressjs/session
- [49] vvo — iron-session README — https://github.com/vvo/iron-session
- [50] NIST — SP 800-57 Part 1, Recommendation for Key Management: Part 1 – General, Revision 5 — https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r5.pdf
- [51] Microsoft — Purpose strings in ASP.NET Core — https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/consumer-apis/purpose-strings
- [52] Microsoft — Host ASP.NET Core in a web farm — https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/web-farm
- [53] Microsoft — Authenticated encryption details in ASP.NET Core — https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/implementation/authenticated-encryption-details
- [54] OWASP — Key Management Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html
- [55] OWASP — Top 10:2025, A07 Authentication Failures — https://owasp.org/Top10/2025/A07_2025-Authentication_Failures/
- [56] OWASP — Application Security Verification Standard, V16 Security Logging and Error Handling, 5.0.0 — https://github.com/OWASP/ASVS/blob/v5.0.0_release/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md
- [57] OpenID Foundation — OpenID Connect Back-Channel Logout 1.0, incorporating errata set 1 — https://openid.net/specs/openid-connect-backchannel-1_0.html
- [58] Microsoft — CookieAuthenticationOptions.SlidingExpiration Property — https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.authentication.cookies.cookieauthenticationoptions.slidingexpiration
- [59] Microsoft — ASP.NET Core source, `CookieAuthenticationHandler.cs` — https://github.com/dotnet/aspnetcore/blob/main/src/Security/Authentication/Cookies/src/CookieAuthenticationHandler.cs
- [60] Microsoft — Microsoft identity platform and OAuth 2.0 authorization code flow — https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow
- [61] IETF — RFC 9110, HTTP Semantics, June 2022 — https://www.rfc-editor.org/rfc/rfc9110.txt
- [62] Okta — Refresh access tokens and rotate refresh tokens — https://developer.okta.com/docs/guides/refresh-tokens/main/
- [63] Spring (Broadcom) — Spring Security source,`RestClientRefreshTokenTokenResponseClient.java` — https://github.com/spring-projects/spring-security/blob/main/oauth2/oauth2-client/src/main/java/org/springframework/security/oauth2/client/endpoint/RestClientRefreshTokenTokenResponseClient.java
- [64] Duende Software — IdentityServer, Refreshing a Token — https://docs.duendesoftware.com/identityserver/tokens/refresh/
- [65] Auth0 — Configure Refresh Token Rotation — https://auth0.com/docs/secure/tokens/refresh-tokens/configure-refresh-token-rotation
- [66] Martin Kleppmann — How to do distributed locking (Martin Kleppmann's blog, 2016; opinion) — https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html
- [67] OWASP — Top 10:2025, A01 Broken Access Control — https://raw.githubusercontent.com/OWASP/Top10/master/2025/docs/en/A01_2025-Broken_Access_Control.md
- [68] GitHub Advisory Database — GHSA-vpfw-47h7-xj4g, CVE-2025-32441, "Rack session gets restored after deletion" — https://github.com/advisories/GHSA-vpfw-47h7-xj4g
- [69] Rack — rack-session commit c28c4a8, the fix for GHSA-9j94-67jr-4cqj (CVE-2025-46336) — https://github.com/rack/rack-session/commit/c28c4a8c1861d814e09f2ae48264ac4c40be2d3b
- [70] Shai Berger — Race condition can undo logout with cache/file session backends (Django Trac, ticket 37249, 2026; case) — https://code.djangoproject.com/ticket/37249
- [71] IETF — RFC 7009, OAuth 2.0 Token Revocation — https://www.rfc-editor.org/rfc/rfc7009.txt
- [72] OpenID Foundation — OpenID Connect RP-Initiated Logout 1.0 — https://openid.net/specs/openid-connect-rpinitiated-1_0.html
- [73] Duende Software — BFF Back-Channel Logout Endpoint — https://docs.duendesoftware.com/bff/fundamentals/session/management/back-channel-logout/
- [74] OWASP — Application Security Verification Standard, V10 OAuth and OIDC, 5.0.0 — https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0_release/5.0/en/0x19-V10-OAuth-and-OIDC.md
- [75] OpenID Foundation — OpenID Connect Front-Channel Logout 1.0 — https://openid.net/specs/openid-connect-frontchannel-1_0.html
- [76] MDN — Clear-Site-Data header — https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/http/reference/headers/clear-site-data/index.md
- [77] W3C — Clear Site Data, Editor's Draft, 10 November 2023 — https://w3c.github.io/webappsec-clear-site-data/
- [78] Andrew Evans — Sign-out deletes only GitLab site data, not all subdomains (GitLab merge request 156213, 2024; case) — https://gitlab.com/gitlab-org/gitlab/-/merge_requests/156213
- [79] OWASP — Authentication Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Authentication_Cheat_Sheet.md
- [80] IETF — RFC 9470, OAuth 2.0 Step Up Authentication Challenge Protocol — https://www.rfc-editor.org/rfc/rfc9470.txt
- [81] MDN — Cross-Origin-Opener-Policy (COOP) header — https://github.com/mdn/content/blob/main/files/en-us/web/http/reference/headers/cross-origin-opener-policy/index.md
- [82] OWASP — Transaction Authorization Cheat Sheet — https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Transaction_Authorization_Cheat_Sheet.md
- [83] GitHub — Sudo mode — https://github.com/github/docs/blob/main/content/authentication/keeping-your-account-and-data-secure/sudo-mode.md
- [84] OWASP — Application Security Verification Standard, V14 Data Protection, 5.0.0 — https://github.com/OWASP/ASVS/blob/v5.0.0_release/5.0/en/0x23-V14-Data-Protection.md
- [85] OWASP — Application Security Verification Standard, V6 Authentication, 5.0.0 — https://github.com/OWASP/ASVS/blob/v5.0.0_release/5.0/en/0x15-V6-Authentication.md
- [86] NIST National Vulnerability Database — CVE-2025-32441 (Rack session middleware) — https://nvd.nist.gov/vuln/detail/CVE-2025-32441
- [87] Spring (Broadcom) —Spring Session reference, API, "Using FindByIndexNameSessionRepository", 4.1.1 — https://docs.spring.io/spring-session/reference/api.html
- [88] Andrea Chiarelli — Things Developers Get Wrong About the Backend for Frontend Pattern (Auth0 Blog, 2026; sponsored by Auth0) — https://auth0.com/blog/things-developers-get-wrong-about-the-backend-for-frontend-pattern/
- [89] OWASP — Subdomain Takeover Prevention Cheat Sheet — https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Subdomain_Takeover_Prevention_Cheat_Sheet.md
- [90] Filippo Valsorda — Cross-Site Request Forgery (words.filippo.io, 2025; opinion) — https://words.filippo.io/csrf/
- [91] MDN — Sec-Fetch-Site — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Sec-Fetch-Site
- [92] IANA — HTTP Authentication Scheme Registry — https://www.iana.org/assignments/http-authschemes/authschemes.csv
- [93] WHATWG — Fetch Standard, Living Standard — https://fetch.spec.whatwg.org/
- [94] OWASP — API Security Top 10, API4:2023 Unrestricted Resource Consumption, 2023 edition — https://raw.githubusercontent.com/OWASP/API-Security/master/editions/2023/en/0xa4-unrestricted-resource-consumption.md
- [95] Marco Squarcina, Mauro Tempesta, Lorenzo Veronese, Stefano Calzavara, Matteo Maffei — Can I Take Your Subdomain? Exploring Same-Site Attacks in the Modern Web (30th USENIX Security Symposium, 2021; research) — https://www.usenix.org/conference/usenixsecurity21/presentation/squarcina (abstract page; the full paper was not read)
- [96] The Go Authors — net/http `csrf.go` (`CrossOriginProtection`), go1.25.0 — https://raw.githubusercontent.com/golang/go/go1.25.0/src/net/http/csrf.go
- [97] Vercel — Next.js docs, `serverActions` configuration, canary docs — https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/serverActions.mdx
- [98] Vercel — Next.js docs, How to think about data security, canary docs (next 16.5.0-canary.16) — https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/02-guides/data-security.mdx
- [99] Sebastian Markbåge — How to Think About Security in Next.js (Next.js blog, 2023; opinion) — https://nextjs.org/blog/security-nextjs-server-components-actions
- [100] GitHub Advisory Database — GHSA-h5cw-625j-3rxh, CVE-2026-22030, React Router has CSRF issue in Action/Server Action Request Processing — https://github.com/advisories/GHSA-h5cw-625j-3rxh
- [101] Remix — React Router, `packages/react-router/CHANGELOG.md`, 7.12.0 entry — https://raw.githubusercontent.com/remix-run/react-router/main/packages/react-router/CHANGELOG.md
- [102] GitHub Advisory Database — GHSA-84g9-w2xq-vcv6, CVE-2026-53663, React Router: Potential CSRF via PUT/PATCH/DELETE document requests — https://github.com/advisories/GHSA-84g9-w2xq-vcv6
- [103] IETF — RFC 6750, The OAuth 2.0 Authorization Framework: Bearer Token Usage — https://www.rfc-editor.org/rfc/rfc6750.txt
- [104] OWASP — WebSocket Security Cheat Sheet — https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/WebSocket_Security_Cheat_Sheet.md
- [105] WHATWG — WebSockets Standard — https://websockets.spec.whatwg.org/
- [106] IETF — RFC 6455, The WebSocket Protocol — https://www.rfc-editor.org/rfc/rfc6455.txt
- [107] Spring (Broadcom) — Spring Session source, `WebSocketRegistryListener.java` — https://raw.githubusercontent.com/spring-projects/spring-session/main/spring-session-core/src/main/java/org/springframework/session/web/socket/handler/WebSocketRegistryListener.java
- [108] IANA — WebSocket Close Code Number Registry — https://www.iana.org/assignments/websocket/websocket.xml
- [109] Spring (Broadcom) — Spring Session, "Spring Session - WebSocket" guide — https://raw.githubusercontent.com/spring-projects/spring-session/main/spring-session-docs/modules/ROOT/pages/guides/boot-websocket.adoc
- [110] WHATWG — URL Standard — https://url.spec.whatwg.org/
- [111] MDN — encodeURIComponent() — https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/javascript/reference/global_objects/encodeuricomponent/index.md
- [112] OWASP — Input Validation Cheat Sheet — https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Input_Validation_Cheat_Sheet.md
- [113] IETF — RFC 3986, Uniform Resource Identifier (URI): Generic Syntax — https://www.rfc-editor.org/rfc/rfc3986.txt
- [114] nginx — Module ngx_http_core_module — https://nginx.org/en/docs/http/ngx_http_core_module.html
- [115] nginx — Module ngx_http_proxy_module — https://nginx.org/en/docs/http/ngx_http_proxy_module.html
- [116] OWASP — REST Security Cheat Sheet — https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/REST_Security_Cheat_Sheet.md
- [117] OWASP — HTTP Headers Cheat Sheet — https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/HTTP_Headers_Cheat_Sheet.md
- [118] MDN — Content-Disposition — https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/http/reference/headers/content-disposition/index.md
- [119] W3C — Content Security Policy Level 3, Editor's Draft — https://w3c.github.io/webappsec-csp/
- [120] OWASP — Logging Cheat Sheet — https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Logging_Cheat_Sheet.md
- [121] OWASP — Top 10:2025, A09 Security Logging and Alerting Failures — https://raw.githubusercontent.com/OWASP/Top10/master/2025/docs/en/A09_2025-Security_Logging_and_Alerting_Failures.md
- [122] Duende Software — BFF documentation, Architecture — https://docs.duendesoftware.com/bff/architecture/
- [123] MDN — CORS errors — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS/Errors
- [124] MDN — Cross-Origin Resource Sharing (CORS) — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
- [125] MDN — Access-Control-Max-Age — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Max-Age
- [126] MDN — Access-Control-Expose-Headers — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Expose-Headers
- [127] OWASP — Application Security Verification Standard, V3 Web Frontend Security, 5.0.0 — https://github.com/OWASP/ASVS/blob/v5.0.0_release/5.0/en/0x12-V3-Web-Frontend-Security.md
- [128] PortSwigger — Cross-origin resource sharing (CORS) (Web Security Academy, no date; sponsored by PortSwigger) — https://portswigger.net/web-security/cors
- [129] Jianjun Chen, Jian Jiang, Haixin Duan, Tao Wan, Shuo Chen, Vern Paxson, Min Yang — We Still Don't Have Secure Cross-Domain Requests: an Empirical Study of CORS (27th USENIX Security Symposium, 2018; research) — https://www.usenix.org/system/files/conference/usenixsecurity18/sec18-chen.pdf
- [130] James Kettle — Exploiting CORS misconfigurations for Bitcoins and bounties (PortSwigger Research, 2016; sponsored by PortSwigger) — https://portswigger.net/research/exploiting-cors-misconfigurations-for-bitcoins-and-bounties
- [131] MDN — Access-Control-Allow-Origin — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Origin
- [132] GitHub Advisory Database — GHSA-8c42-7qj2-3j46, CVE-2026-59903, Netty Vulnerable to Cache Poisoning and Information Disclosure via CORS Vary Header Overwrite — https://github.com/advisories/GHSA-8c42-7qj2-3j46
- [133] Spring — Spring Security reference, CORS, 7.1.1 — https://docs.spring.io/spring-security/reference/servlet/integrations/cors.html
- [134] MDN — Cross-site request forgery (CSRF) — https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF
- [135] Encode — Starlette, `starlette/middleware/cors.py`, commit b7901fb — https://github.com/encode/starlette/blob/b7901fb908f0c6c3b8b6e495517cea6b2e77e66b/starlette/middleware/cors.py
- [136] expressjs — cors, README — https://github.com/expressjs/cors
- [137] Microsoft — Enable Cross-Origin Requests (CORS) in ASP.NET Core, ASP.NET Core 10.0 — https://learn.microsoft.com/en-us/aspnet/core/security/cors?view=aspnetcore-10.0
- [138] NIST NVD — CVE-2020-36851, cors-anywhere — https://nvd.nist.gov/vuln/detail/CVE-2020-36851
- [139] Vicent Martí — Yummy cookies across domains (The GitHub Blog, 2013; case) — https://github.blog/engineering/yummy-cookies-across-domains/
- [140] Mozilla — Bug 1779993, '=' prepended to set-cookie header can result in __Secure- and __Host- prefix bypasses — https://bugzilla.mozilla.org/show_bug.cgi?id=1779993
- [141] NIST NVD — CVE-2020-7070, PHP — https://nvd.nist.gov/vuln/detail/CVE-2020-7070
- [142] PHP — Security advisory GHSA-wpj3-hf5j-x4v4, CVE-2024-2756 — https://github.com/php/php-src/security/advisories/GHSA-wpj3-hf5j-x4v4
- [143] MDN — Third-party cookies — https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies
