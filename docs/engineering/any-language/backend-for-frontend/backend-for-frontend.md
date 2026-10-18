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
read, and whose server accepts no planted cookie (section 5 lists the exceptions). Its sessions
end on the server at logout, at their timeouts and at the provider's back-channel logout. Its keys
rotate without signing users out, and its API refuses the requests that other sites make the
user's browser send.

The rules are for the team that builds or runs that server, whether it writes the session, cookie
and key handling itself or takes them from a library or a framework, and for the reviewer of a
change to it. A library can get a rule wrong, so section 4 turns the rules into questions to ask
a library before the team picks one. The page's own rules are in
[security.md](../../react/security/security.md); what "the server", "the API" and "an API route"
mean here is at the end of this section.

One rule holds the rest together: the session cookie is the only thing the browser holds, and a
request that carries it may come from someone other than the user. Another site can make the
browser send it, and a script on the page sends it like the page's own code (RFC 10017 sections
5.1.4 and 6.1.3.3) [1]. A sibling subdomain can set a cookie under its name (the RFC
6265bis draft, section 8.6) [2]. Whoever holds a leaked cookie key can write a cookie the BFF
accepts. So the cookie rules keep the cookie from being read or planted, the key rules replace a
leaked key, the session rules end the session on the server, and the CSRF and CORS rules check
each request before the BFF serves it.

Use a BFF when the application signs users in with OpenID Connect or OAuth, calls APIs with the
user's access token, and is a business application, a sensitive one or one that handles personal
data: RFC 10017 section 6.1.4.3 strongly recommends the BFF for these [1].
[security.md](../../react/security/security.md) section 6 compares the BFF with the RFC's two
other patterns. The BFF has a cost that lasts as long as the application runs. RFC 10017
section 6.1.4.3: "The architecture of a BFF is significantly more complicated than a
browser-only application. It requires deploying and operating a server-side BFF component" [1].
Since every call to a resource server goes through it, this proxy behaviour "can add a
significant burden on the server-side components", as the same section says [1].

A BFF is more than the application needs when its page calls only the API of its own server, on
the same site, and the server calls no other API with the user's token. RFC 10017 section 7.1
says that "simple applications are made needlessly complex by using OAuth to replace the concept
of session management", and that such an application "can rely on server-side cookie-based
session state" instead of access tokens [1]. That is the simpler way. Its server still
sets a session cookie, so the rules here hold for it, apart from the rules the next paragraph
lists for a server that signs users in itself, with no identity provider. Where such a server
signs users in through an identity provider and keeps no token after the login, the rules marked
`with an identity provider` hold for the login, logout and re-authentication, and the rules on
refreshing, revoking and forwarding tokens do not apply; that reading is this practice's. An
application that
signs nobody in has no session to keep, and none of these rules applies to it.

A server that signs users in itself, with no identity provider, plays the BFF's part: the cookie,
session-life and CSRF rules hold for it unchanged, and so does ending the session at logout. It
keeps the session's state on the server (this practice's choice), since with the state in the
cookie there would be no provider tokens to revoke at logout, and the list of ended sessions
(section 2, "Logout") would be the only control that stops a copy of the cookie. It skips the
rules that hold only with an identity provider:

- "The login cookie" and "Forwarding to resource servers", whole;
- in "Timeouts and refresh", the rules on refreshing the tokens: the token endpoint's answers to
  a refresh, the refresh token's rotation and reuse window, and the lock that holds one refresh
  at a time;
- in "Logout", the rules on revoking the tokens and on RP-initiated, back-channel and
  front-channel logout;
- in "The login and logout responses", the login callback's response;
- in section 3, the rules on refreshing before a request is forwarded and on a resource server's
  `401`;
- "Keys and secrets", whole, unless its framework signs or encrypts the session cookie, as
  express-session signs the session id [48].

Any other rule that needs an identity provider says `with an identity provider` in its prefix.
A BFF whose identity provider sends no back-channel logout skips, in the same way, in "Logout",
the rules on back-channel logout, and in section 3, the rules on the back-channel logout endpoint
and the alerts on back-channel logout. With the session's state in the cookie, such a BFF still
keeps the per-user time, which the every-request check in "Logout" reads and the rule on a
disabled or deleted account, in "Re-authentication", sets.

The words below have one meaning in this file. "The server" is the component that receives the
browser's session cookie: the BFF, which in the examples is also the API at
`https://api.example.com`, so "the API" names it too. An API route is any route of that server
other than a `GET` that serves the page's own files (the HTML and its scripts) or, with a
framework that renders on the server, a `GET` that renders one of its pages. A rule that starts
with `BFF:` or `API:` is that server's act, and so is a rule of section 3 with no prefix; the two
prefixes name the same server. A prefix that adds a condition after a comma, such as
`BFF, with an identity provider:` or `BFF, with a first-party login:`, limits the rule to that
case. "The page" is the browser application, the code that runs in the user's browser and calls
the API. The page's terms that this file uses are those of
[security.md](../../react/security/security.md): its section 1 defines the sign-out path, and its
section 7, "What the React code does", the one API client that sends every request to an API route.
Most links to [logging.md](../../python/logging/logging.md) use its level table (section 4) and its
list of what never goes in a log (section 10), which hold in any language; a team on another
language maps the level names to its own logger's.

Some topics are outside this practice on purpose: the page's side, and the comparison of the
patterns, are [security.md](../../react/security/security.md). These are not covered yet:

- a silent login run in an iframe, which the login start refuses (section 2, "The login cookie");
- caps on the size and number of WebSocket messages and connections;
- throttling of sign-in attempts, with the rest of a first-party login's credential checks such as
  password storage, which a practice on authentication would own; the cap on guesses at a step-up
  is covered (section 2, "Re-authentication");
- rate limiting or anomaly detection on the requests that a script on the page sends through the
  BFF, for which RFC 10017 section 6.1.4.1 calls the BFF "the ideal place" [1];
- re-authentication on a risk signal, such as a sign-in from a new device;
- key-based client authentication, which RFC 10017 section 6.1.3.7 names among the practices a
  BFF, as a confidential client, can adopt more easily [1];
- how a resource server that limits requests by IP address learns the user's address through the
  BFF, since otherwise, as RFC 10017 section 6.1.3.5 warns, "the server might start blocking
  requests as many users' browsers will appear to be coming from the single IP address of the
  BFF" [1].

A BFF that already has users moves to these rules as
[refactoring.md](../../any-language/refactoring/refactoring.md) section 7 says; the rule on
changing a live session cookie (section 2, "The session cookie") covers the changes that would
sign every user out. Section 5 says where the rules that are here stop holding.

## 2. Sessions and tokens

### The session cookie

The session cookie the BFF sets:

| Attribute | Value | Why |
|---|---|---|
| name prefix | `__Host-Http-` (RFC 10017 section 6.1.3.2, which takes it from the IETF's layered-cookies draft) [1] | a browser that enforces the prefix accepts the cookie only with `Secure`, `HttpOnly`, `Path=/` and no `Domain`, so neither a script on the page nor a sibling subdomain can set a cookie under that name [3], [4]. Chrome, Edge and Firefox enforce it; Safari 27 enforces it neither on `Set-Cookie` nor on `document.cookie`, so there a script on the cookie's own host can set a cookie under that name; it applies only the `__Host-` rules, which the name also matches [5], [6]. Safari 27 also matches the prefix case-sensitively (its `__HoSt-` tests fail), so it applies no prefix rule to `__HOST-HTTP-SESSION` [6]. It also stores a `__Host-` cookie set with no `Path` attribute (wpt.fyi, the stable aligned run of 2026-10-06) [6] |
| `Secure` | set | sent over HTTPS only [2] |
| `HttpOnly` | set | `document.cookie` cannot read it, and `fetch` still sends it [4] |
| `Path` | `/` | the `__Host-` rules ask for it; a path is no security boundary, since other pages on the host can still reach the cookie (RFC 6265bis draft, section 4.1.2.4) [3], [2], [4] |
| `Domain` | not set | without it the cookie goes back only to the host that set it; with it, every subdomain receives the cookie and can overwrite it (the cookie spec's "Weak Integrity" section, RFC 6265bis draft, section 8.6) [2], [4] |
| `SameSite` | `Strict`, written out | RFC 10017 section 6.1.3.2 asks for `Strict` [1]. Left out, the default differs by browser: `Lax` in Chromium, none in Firefox and Safari [7], [8] |
| `Max-Age` | not set: a non-persistent cookie | the server's idle and absolute timeouts end the session (section 2, "Timeouts and refresh"). A cookie with `Max-Age` is persistent, and the browser keeps it on disk through every close; one without it ends with the browser, though a browser that restores its last session brings it back, so the timeouts stay the control [8], [4]. Set `Max-Age`, no longer than the absolute timeout, only when the product needs the session to survive a browser close. NIST SP 800-63B-4 section 5.1.1 says a session cookie "SHOULD be tagged to expire at or soon after the session's validity period", a requirement "intended to limit the accumulation of cookies" that "SHALL NOT be relied upon to enforce session timeouts" [41]; leaving `Max-Age` out, so the cookie ends with the browser and the server's timeouts end the session, is this practice's choice |
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
- **BFF: when a BFF that already has users renames its session cookie, changes how the cookie is
  protected, or moves the session's state between the cookie and the server, either accept that
  every user is signed out once at that deploy, or for one absolute timeout also read the old
  cookie and re-issue it under the new name and format.** Without the re-issue, that deploy ends
  every live session. The name checks skip a
  cookie under the old name without a word ("Reading the `Cookie` header" below), and a cookie in
  the old format names no key the BFF holds ("Keys and secrets" below). When you accept the
  sign-out, write it down ("Write it down" in "The session's life, from login to logout" below
  says where). For the re-issue, ship the code that reads the new format first, wait until no
  instance runs the old code, then switch the code that writes it. An instance that still runs the
  old code cannot read a cookie in the new format. Re-issue only an old cookie that passes the
  checks a new cookie gets, run on the old cookie's session id and start time: the list of ended
  sessions, the per-user time and both timeouts. Carry the start time over unchanged, and expire
  the old cookie by its name in the same response, unless the new cookie keeps that name: a
  response carries only one `Set-Cookie` per cookie name, and the new cookie replaces the old one
  (RFC 6265bis draft, sections 4.1.1 and 4.1.2) [2]. Where the session's state stays where it is,
  as at a rename or a change of how the cookie is protected, keep the session id, so a later
  logout, which lists or destroys that id, also stops any copy of the old cookie. Where the state
  moves between the cookie and the server, give the session a new id from a CSPRNG, never create
  it under an id the request brought, and end the old session at the re-issue. When the state
  leaves the cookie, list the old id as ended, and keep checking old cookies against that list for
  as long as the BFF still reads them; when the state leaves the server, destroy the old record.
  Where the old format carries no session id or start time, take the sign-out instead. The rule is
  this practice's choice.

### The login cookie

- **BFF: use a maintained OpenID Connect library, or the provider's SDK, for the OAuth flow, never
  your own code,** so the flow's checks come from code that others review and keep patched.
  OWASP's Authentication cheat sheet asks to prefer well-maintained libraries or SDKs [79];
  writing the flow yourself is this practice's ban. The library runs the protocol: the
  authorization request, `state`, the nonce, PKCE, the token exchange and the ID token checks. The
  rules below are checks on it, for the first login and for a step-up; write code only for a rule
  it does not meet. The step-up's checks and the bookkeeping of its login cookie
  ("Re-authentication" below) are the team's own code around the library.
- **BFF: register the BFF at the identity provider as a confidential client with its client
  authentication, and with the values below,** so the provider sends a code only to the BFF's own
  callback, and the logout rules below get the values they match on. Register one exact `https`
  callback URI and no wildcard, the authorization code grant and the refresh token grant only,
  only the scopes the BFF uses, the post-logout redirect URI, and the back-channel logout URI with
  `sid` required. RFC 9700
  section 2.1 asks authorization servers to compare a redirect URI with the registered ones by
  "exact string matching" [16]. The
  rest of the registration is this practice's choice.
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
  The rival is one login cookie for the latest attempt: a login started in a second tab then
  overwrites it, and the first tab's callback fails, which the error page that offers to sign in
  again covers (the rule on a callback whose login cookie is missing, below). This practice keeps a
  cookie per attempt, so that a sign-in started in each tab completes, as in ASP.NET Core; its cost
  is the rules below that expire and cap the login cookies. The rule is this practice's choice.
- **BFF: where the library leaves it to your own code to create an attempt's `state`, nonce or
  PKCE verifier, draw each from a secure random source, the verifier from 32 random bytes, and
  send its challenge with `S256`,** since RFC 7636 section 7.1 asks for a verifier "with a minimum
  of 256 bits of entropy" [14]. RFC 6749 section 10.12 says that the binding value used for
  CSRF protection "MUST contain a non-guessable value" [15]. RFC 9700 section 2.1.1 asks for
  a challenge method that does not expose the verifier: "Currently, S256 is the only such method"
  [16]. ASVS 5.0 requirement 10.1.2 asks these values to be "not guessable" and "specific
  to the transaction" [17].
- **BFF: keep what a login attempt records, a step-up's included, where the user can neither change
  nor read it, and never in a record on the server,** since a person at the browser can edit any
  value that is not protected ([security.md](../../react/security/security.md) section 1's one
  rule). Keep it in the login cookie's value, or in `state` when the library keeps it there,
  encrypted and signed with authenticated encryption from a vetted library, the framework's own
  data protection where it has one, under the key rules for every cookie the BFF signs or encrypts
  (section 2, "Keys and secrets"). RFC 9700 section 4.7.1
  asks a client to protect `state` "against tampering and swapping", by binding it to the browser
  session or by "signing/encrypting state values" [16]. RFC 7636 section 7.1 adds that the
  PKCE verifier must not be "learned or guessed by the attacker" [14]. ASP.NET Core keeps
  the record, the verifier included, in the encrypted `state`, and binds it to the browser with a
  per-attempt cookie [18], [13]. Kept out of the store, the record means an anonymous login start
  writes nothing to the store, so a login starts while the store is down, and an anonymous caller
  cannot fill the store. The rival is a record on the server for each attempt, with a short
  expiry, and a rate limit on the login start: the pre-sessions of OWASP's CSRF cheat sheet,
  "sessions before a user is authenticated" that hold the login's tokens [10]. Its cost is a store
  write on every login start, anonymous ones included, and the rate limit that keeps those writes
  bounded, the anti-automation control that ASVS 5.0 requirement 2.4.1 asks for against
  "garbage-data creation" [17]. Its saving: with the session's state on the server, a record on
  the server for each attempt leaves no login cookie that the BFF protects with a key, so "Keys
  and secrets" applies only where the BFF encrypts the tokens in session records or its framework
  signs or encrypts the session cookie, as its first line says. The rule is this practice's choice.
- **BFF: at the callback, read the attempt's values, such as the time it started, only from that
  protected record,** so an edited value never passes a check; the rule is this practice's choice.
- **BFF, with more than one identity provider: record in the attempt's protected record the issuer
  the authorization request went to, and at the callback reject a response whose `iss` parameter
  differs from it.** With a provider that sends no `iss`, give each provider a callback path of its
  own and check the path instead. RFC 9700 section 4.4.2 says that a client that talks to two or
  more authorization servers "MUST store, for each authorization request, the issuer they sent
  the authorization request to and bind this information to the user agent" [16].
  RFC 9207 section 2.4 adds that when the value "does not match the expected issuer identifier,
  clients MUST reject the authorization response" [19]. RFC 9700 section 4.4.2.2 allows a
  distinct callback path for each provider as the alternative [16]. The ID token's `iss`
  does not replace this check in the code flow: that token arrives only after the code has gone to
  the token endpoint, and RFC 9700 section 2.1 asks for an `iss` value "in the authorization
  response" [16].
- **BFF: give the login cookie a `Max-Age` long enough for the user to finish at the provider, such
  as 15 minutes, and delete it at every callback, whether the sign-in succeeds or fails, a callback
  that carries an `error` from the provider included,** since it is needed only between the login
  start and the callback. The user may enrol a second factor on the way. RFC 9700 section 4.2.4
  asks that "The state value SHOULD be invalidated by the client after its first use at the
  redirection endpoint" [16]. A cookie left behind adds to the login cookies that every
  request carries. In the open dotnet/aspnetcore issue 53048, a team reports that ASP.NET Core
  keeps its correlation and nonce cookies after a callback with `error=login_required`, and that
  "Around 4 or 5 navigations to the site without being logged in, within a 15 minute window, will
  cause the errors to occur" [20]. 15 minutes is ASP.NET Core's default for a remote
  sign-in, its `RemoteAuthenticationTimeout` [13].
- **BFF: when you set a login cookie, write the time its attempt started, in whole seconds since
  1970-01-01T00:00:00Z, into the cookie's value,** so the rules below can tell which login cookies
  are newest. A `Cookie` header carries only each cookie's name and value, and section 4.2.2 of
  the cookie spec, the RFC 6265bis draft, tells servers not to rely on the order of the cookies in
  it [2]. The step-up's check compares the same time with the ID token's `auth_time`, which counts
  in the same unit ("Re-authentication" below). The rule is this practice's choice.
- **BFF: at the login start, expire every login cookie the request carries that none of the cookie
  keys every instance shares can read,** so a cookie no callback can use, such as one written under
  a key since removed, never fails the login start or keeps a place among the two the next rule
  keeps. Microsoft's ASP.NET Core docs on key management say that a deleted key leaves the data it
  protected "permanently undecipherable" [22]. The rule is this practice's choice.
- **BFF: then expire every other login cookie the request carries beyond the two with the latest
  start times in their values,** so login cookies cannot pile up until the `Cookie` header passes
  the server's size limit. The prefix asks for `Path=/`, so every login cookie rides every request
  to the API's host, not only the callback. ASP.NET Core, whose per-attempt cookie this practice
  follows, has the pile on record: in dotnet/aspnetcore issues 58731 and 53048, users report that
  its correlation and nonce cookies built up until requests failed, in issue 58731 with nginx's
  `400` "Request Header Or Cookie Too Large" [21], [20]. The RFC 6265bis draft asks servers, in
  section 6.1, to "use as few and as small cookies as possible", and warns in section 8.6 that many
  cookies can force the browser to evict others [2]. The rule, a cap of two, is this practice's
  choice.
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
- **BFF: at the login start, take the page to return to only as a local path that the framework's
  helper accepts, or as a short id the BFF maps to a path, and at the callback redirect only there
  or to the application's root.** Keep that page in the attempt's protected record. The login
  start and its callback skip every CSRF check (the exemption table of section 3), and a target
  taken from the request as it is sends the user, from a link that shows your domain, to any site.
  RFC 10017 section 6.1.2.1 has the callback answer "with a redirect that triggers the browser to
  load the application" [1]. OWASP's Unvalidated Redirects cheat sheet says: "For local return
  URLs, use a framework helper that rejects non-local destinations", and that "A server-side
  mapping from an approved destination ID remains preferable to accepting arbitrary URLs" [144].
- **BFF: at a callback whose login cookie is missing, cannot be read, or does not match the
  `state`, log the reason and answer an error page that offers to sign in again,** so the user has
  a way on instead of a dead end. A login cookie that expired, that another browser holds, or that
  was written under a removed key leaves the callback nothing to check. ASP.NET Core throws "An
  error was encountered while handling the remote login." on a failed callback that no handler
  takes [13]. The rule is this practice's choice.
- **BFF: give the error page that a failed login callback answers with fixed text, and put no
  parameter of the request into it,** such as `error`, `error_description` or `state`, since those
  come from outside and the error page is served from the API's origin, which holds the session
  cookie. They are the parameters of the provider's error response in RFC 6749 section 4.1.2.1 and
  OpenID Connect
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

- **BFF: turn on the host's dependency alerts in the BFF's own repository, and when an advisory
  names your server framework, its session and cookie library or its OpenID Connect client
  library, update it under [security.md](../../react/security/security.md) section 10's advisory
  path.** The browser checks the prefix. A server that parses the `Cookie` header in another way
  can read a cookie the browser treated as a different one [29]. PortSwigger's research
  (2025) got past the `__Host-` and `__Secure-` prefixes on several server frameworks through such
  differences [29].
- **BFF: read the session cookie and the login cookie only when the raw `Cookie` header holds the
  cookie's exact name once, compared byte for byte, and answer `400` when it holds the name more
  than once,** so the server never has to choose between two values for one cookie. The cookie
  spec tells servers not to rely on the order of two cookies with one name (RFC 6265bis draft,
  section 4.2.2) [2]. The raw header is every `Cookie` field line of the request
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
- **BFF: answer `400` to a request whose `Cookie` header starts with `$Version`,** so no server
  reads one cookie string as several. PortSwigger's research (2025) shows that Apache Tomcat and
  Jetty can switch to a legacy parser, so a cookie a sibling subdomain sets can carry a forged
  `__Host-` pair [29]. Tomcat 9 does so when the header starts with `$Version` (its `Cookie.java`;
  the 10.1 and 11.0 parsers have no legacy mode) [35].
- **BFF: keep the server's cookie parser in its RFC 6265 mode,** for the same reason: Jetty 12
  switches to a legacy parser only in its legacy compliance modes, where it reads `$` names
  anywhere in the header and, in its RFC 2965 modes, splits cookies at commas; its default is RFC
  6265 (its `RFC6265CookieParser.java`, `CookieCompliance.java` and `HttpConfiguration.java`)
  [36]. The research gives a test, not a developer rule [29]. These two rules and the name checks
  above are therefore this practice's choice, built on the cookie spec's sections 4.2.2, 5.4 and
  5.6 [2]. The advisory rule above them stays as the second control.
- **BFF: take the session cookie's value from the same parse of the raw `Cookie` header that ran
  the name checks, never from the framework's cookie collection,** since a framework's parser can
  trim or fold the case of names, decode values or split cookies in its own way [29], [33], [36].
  Split the header at `;`, drop the one space the browser writes after it, and split each pair at
  its first `=`, since that is how the browser writes the header (the layered-cookies draft,
  section 5.4.6) [3]. The login cookie, which the
  OpenID Connect library reads, keeps the checks above as its control. The rule is this practice's
  choice.
- **BFF: check the session cookie's value against the format of the values the BFF writes, its
  length and its alphabet, before you look it up or decrypt it, and treat a value that fails as no
  session,** since the value comes from outside like any other input
  [8].
- **BFF: give every `400` that the cookie checks above answer to a request from the API client a
  JSON body with the fixed code `cookie_conflict` in its field `code`,** so the page can
  tell the user how to get out. Every fixed code this file names goes in that field. The rule and
  the field's name are this practice's choice.
- **BFF: answer a failure on a route the browser reaches by navigation, such as the login start or
  a download link, with a page of fixed text that puts no parameter of the request into it,**
  since no page code runs on a navigation to read the status or a JSON body. A parameter of the
  request comes from outside, as the rule on the failed callback's error page in "The login cookie"
  above says. On a `401` the error page links to the sign-in. On a `400` of the cookie checks
  above, the callback included, it tells the user to clear this site's data in the browser. The
  failed callback keeps its own error page; the rule is this practice's choice.
- **BFF: where the team controls the registrable domain and accepts the cost to the other
  applications on it, send `Clear-Site-Data: "cookies"` with the `400` of the cookie checks,** so
  the browser removes the planted cookie without the user's help. The header removes every cookie
  whose domain matches the registered domain, a cookie a sibling subdomain set for `example.com`
  included [37]. Chrome 61, Firefox 63 and Safari 17 support it
  [38]. The cost: it also signs the user out of every other application on
  that domain. Write the choice down ("The session's life" below says where); the rule is this
  practice's choice.
- **BFF: where the team controls the registrable domain and every application on it can serve
  HTTPS, send `Strict-Transport-Security` with `includeSubDomains` from it,** so a browser that
  holds the policy reaches no host under it over plain HTTP, where a network attacker can answer
  and set a cookie for the whole domain (RFC 6265bis draft, section 8.6; RFC 6797 section 8.3)
  [2], [39]. A browser that never visits the domain itself does not get the policy (RFC 6797
  section 11.4.2) [39]. The cookie checks above stay, since a sibling subdomain can still
  plant a cookie. The cost: every host under the domain, those of other applications included, must
  then serve HTTPS (RFC 6797 section 11.4) [39]. Write the choice down; the rule is this
  practice's choice. Preloading the domain, so that the browser holds the policy before its first
  visit (RFC 6797 section 12.3) [39], is a separate choice; write it down too. Before you preload,
  raise `max-age` in stages, as hstspreload.org asks: 5 minutes, 1 week, then 1 month, each with
  `includeSubDomains`, and wait out each stage while you check for broken pages [147]. The preload
  list then requires a `max-age` of at least 31536000 seconds (1 year), with `includeSubDomains`
  and `preload` [147]. The cost: inclusion "cannot easily be undone", since removal "takes months
  for a change to reach users with a Chrome update", and "HSTS preloading applies to all
  subdomains, including internal subdomains that are not publicly accessible" [147]. The same
  page holds that "The benefits provided by HSTS preloading are minimal compared to the benefits
  provided by HSTS. While HSTS is recommended, HSTS preloading is not recommended" [147].

### The session's life, from login to logout

**Write it down** means two things in these rules: a choice, such as where the session's state
lives, goes into the project's decision log
([roles-and-decisions.md](../../any-language/project-management/roles-and-decisions.md) section
7), and a value, such as a timeout or a token lifetime, goes into the BFF's settings with its
reason next to it ([readability.md](../../any-language/readability/readability.md) section 4), so a
later reader finds why.

- **BFF: answer the session check, the "check session" endpoint of RFC 10017 section 6.1.2.1,
  with `200`, the user's display fields and no token when the session is live, and with `401` when
  there is none,** so the page learns who is signed in without holding a token [1]. Send it the
  headers of every API response (section 3, "Response headers"), `Cache-Control: no-store` among
  them, so no cache keeps one user's answer for the next. RFC 10017 section 6.1
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
  that checks the session on a timer would never let it go idle. The BFF cannot tell any other
  request the page sends on a timer from one a user's action sends, so the page must not send such
  requests on data that needs the session ([security.md](../../react/security/security.md) section
  6, "Timeouts and refresh").
- **BFF, with an identity provider: keep the session's state on the server by default, with only a
  random id in the cookie; keep it in the cookie, signed and encrypted, only when two conditions
  hold, and write the choice down.** The two conditions: every instance can read a store that
  takes a read on every request and a write at each logout, and that store cannot take a write on
  every request or hold every user's tokens. RFC 10017 section 6.1.2.3 says that "using
  server-side sessions with a BFF is only recommended in small-scale scenarios", since they need
  sticky sessions or replication [1]. This practice departs
  from it because a session held in the cookie still needs a list of ended sessions in a store
  every instance reads (ASVS 5.0 requirement 7.4.1) [42]. The two choices cost the store different
  work: with the state on the server, the store holds every user's tokens and takes a write each
  time the idle clock moves; with the state in the cookie, it holds the list of ended sessions,
  read on every request and written at each logout. The cookie then saves less than
  the RFC expects, and the rules below, back-channel logout among them, are simpler with the state
  on the server ("Logout" below). With a first-party login there is no choice: the state stays on
  the server (section 1). Where the state in the cookie changes a rule, the rule says how.
- **BFF, with an identity provider: before you choose the session's state in the cookie, read the
  provider's discovery document for `revocation_endpoint`,** so you know whether revocation can
  back up the list of ended sessions; the rule is this practice's choice. RFC 8414 section 2 makes
  the field optional, so when it is missing, ask the provider [43]. Without a revocation endpoint,
  keep the session's state on the server, or write down that the list of ended sessions is then
  the only control.
- **BFF: with the session's state in the cookie, check the length of the session cookie's name and
  value before you set it; when the two together pass 4096 bytes, set no cookie, log the reason
  at `ERROR` ([logging.md](../../python/logging/logging.md) section 4) and answer an error page.**
  A browser ignores such a cookie without an error (RFC 6265bis draft, sections 5.6 and 5.7) [2].
  The sign-in would then look done, and the next request would answer `401`. When re-issuing the
  cookie after a refresh would pass 4096 bytes, end the session and log it at `ERROR`
  ([logging.md](../../python/logging/logging.md) section 4), since a provider that rotates refresh
  tokens has already rotated the one in the cookie the browser
  keeps; the sign-in case stays as above, and the rule for a re-issue is this practice's choice.
- **BFF: with the session's state on the server, let only the BFF's own identity, and the identity
  of step 3 of the leaked-key plan ("Keys and secrets" below) only while that run lasts, reach the
  session store, over TLS, and encrypt the store's backups and replicas at rest,** since the store
  holds every user's tokens. Server-side sessions "keep all data on the server", as RFC 10017
  section 6.1.2.3 puts it [1]. OWASP's Session Management cheat sheet asks to "restrict access to
  the session store and encrypt backups and replicas at rest" [8]. Reaching the store over TLS, and
  the leaked-key run's identity as the one other identity that reaches it, are this practice's
  choice.
- **BFF: when someone reading the session store is in your threat model, put a lookup id and a
  separate secret in the session cookie, keep only the SHA-256 hash of the secret in the store,
  and compare hashes in constant time,** so a copy of the store gives no live session id. OWASP's
  Session Management cheat sheet says "If read-only disclosure of the store is in your threat
  model, store a one-way verifier instead", and compares the hash of the secret the request brings
  "with the stored hash using a constant-time comparison" [8]. In a
  BFF the record also holds the tokens, which the next rule keeps from a reader of the store.
- **BFF: in the same threat model, encrypt the tokens in each session record with authenticated
  encryption from a vetted library, under a key kept as "Keys and secrets" below says,** since the
  record holds every user's access and refresh tokens, which the hashed secret does not protect.
  OWASP's Session Management cheat sheet says that when the session objects hold sensitive
  information, "it is required to duly encrypt and protect the session management repository"
  [8]. Section 5 says what a reader who also gets that key still holds.
- **BFF: write down how many sessions one user may hold at once, and what happens when a new login
  passes that number ("Write it down" above),** so the team decides, before a user reaches the
  limit, whether a new login ends an older session or is refused. ASVS 5.0 requirement 7.1.2 asks
  the documentation to define both [42].

#### Keys and secrets

These rules apply only when the BFF protects a cookie or a token with a key.

A key here is any key that signs or encrypts a cookie, the login cookie's included, and the key
that encrypts the tokens in session records ("The session's life, from login to logout" above);
for that key, read "cookie" in the rules below as "session record". Where a framework protects the
cookies, these rules are checks on it; write code only for a rule it does not meet.

- **BFF: keep the client credential and every key that signs or encrypts a cookie, the login
  cookie's included, in the server's secret store, or in a shared store encrypted under a key that
  only the secret store holds, never in code or a build artifact,** so no copy of the code holds a
  secret (ASVS 5.0 requirement 13.3.1) [44]. The client credential is what the BFF authenticates
  with to the identity provider that registered it. OWASP's Cryptographic Storage cheat sheet asks
  that a key which encrypts other keys be stored apart from them [46]. In these rules, the key
  store is the store that holds the cookie keys: the secret store, or that shared store.
- **BFF: let the BFF's own identity only read the client credential in the secret store and the
  keys in the key store, and only the job that rotates the keys write them,** so nobody else, the
  BFF's own instances included, can add a key of their own and forge cookies (ASVS 5.0
  requirement 13.3.2; Microsoft's ASP.NET Core Data Protection docs) [44], [45]. Requirement
  13.3.2 asks that "access to secret assets adheres to the principle of least
  privilege" [44]. The read-only identity is this practice's choice. An emergency run during an
  incident, which the leaked-key plan below names who starts, is a run of the job that writes a
  new key for each purpose where keys have one, with a start time of now, then deletes each leaked
  key id. When the client credential leaked, on its own or where a key leaked, the emergency run
  also removes the leaked credential at the provider, adds the new one there and writes it into
  the secret store as "current"; that is this practice's choice. Step 3 of the leaked-key plan
  below names the one other identity that may read the keys and the client credential, only while
  that run lasts.
- **BFF, with an identity provider: let only the rotation job and one person or role the team
  writes down ("Write it down" above) reach the two other entries that the client-credential rule
  below keeps in the secret store,** since one of them, the credential for the provider's
  management API, can add client credentials at the provider. The other is the test account's
  refresh token. The rotation job reads the management credential, and reads and writes the test
  account's refresh token, since it stores the answer of each test refresh; the BFF's own identity
  reads neither. The person or role puts both entries into the store and replaces them: the test
  account's token at each sign-in again (step 3 of that rule), and the management credential when
  it leaks, or when it sat where a cookie key leaked (step 6 of the leaked-key plan below). Who
  reads and writes these two entries, and who replaces them, are this practice's choice.
- **BFF: where the key store or the secret store keeps a log of writes, alert a person (section 3,
  "Logging") on a write to it by any identity other than the rotation job,** since such a write may
  be a planted key, which every instance accepts at its next reload; the alert is this practice's
  choice. Leave out a write of the management credential or the test account's refresh token by
  the person or role the rule above names; every other write by an identity other than the
  rotation job still alerts.
- **BFF: have each run of the rotation job log at `INFO` the key ids it added and removed, at
  `WARNING` a step that failed and that the next run tries again, and at `ERROR` a step that failed
  past the limit its rule names,** so a run that stopped, or a removal that did not happen, shows
  in the log. Such a limit is the window of the check in step 1 of the rotation below, or the test
  refresh and the limit on step 5 of the client-credential rule below. The logs are this
  practice's choice.
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
  forge a production cookie. The rule is this practice's choice. NIST SP 800-57 Part 1 section 5.2
  says: "In general, a single key shall be used for only one purpose" [50]. ASVS 5.0
  requirement 11.1.1 asks that keys are "not overshared" [47]. ASP.NET Core derives a
  subkey for each purpose string, so that "no other component can read its payloads"
  [51], and its docs say that apps that must stay isolated "should use
  different key repositories" [45].
- **BFF: for every cookie the BFF signs or encrypts, the login cookie included, give every instance
  the same set of keys, loaded from one store,** since an instance with keys of its own cannot read
  a cookie another instance wrote, so users are signed out, or their sign-in fails, at random
  (Microsoft's ASP.NET Core docs on a web farm) [52].
- **BFF: start every cookie you protect, and every session record whose tokens you encrypt, with a
  format version and the id of the key that protected it, and choose the key that reads it by that
  id,** so rotation needs no trial over
  every key, an unknown id is refused at once, and the algorithm can change later. OWASP's
  Cryptographic Storage cheat sheet names "Marking each item with the ID of the key that was used
  to encrypt it, and storing multiple keys to allow the old data to be decrypted" as a way to
  rotate keys [46]. ASVS 5.0 requirement 11.2.2 asks that keys and
  algorithms can be replaced [47]. ASP.NET Core's protected payload starts the same way,
  with "A 32-bit magic header that identifies the version" and "A 128-bit key id"
  [53]. A format version and a key id written in front of what a vetted authenticated encryption
  returns, and passed to it as associated data, only frame the library's own scheme; they are not
  a scheme built from primitives (the rule below). That reading is this practice's.
- **BFF: with the session's state in the cookie, protect the cookie with authenticated encryption,
  such as AES-GCM, from a vetted library, the framework's own cookie protection where it has one,
  never with a scheme you build from primitives yourself,** so the encryption comes from code that
  others review and keep patched [47], [46]. An edited cookie then fails the check instead of
  being read (ASVS 5.0 requirements 11.2.1 and 11.3.3; OWASP's Cryptographic Storage cheat sheet)
  [47], [46].
- **BFF: before you build the key list and the rotation below, weigh a managed key service (KMS)
  that holds the keys and runs the encryption itself:** it wins where a KMS is available, the call
  volume is low and the keys never need to leave it. The hand-built key list is needed where every
  request decrypts a cookie, as with the session's state in the cookie, or where no KMS is
  available. OWASP's Key Management cheat sheet asks that cryptographic operations "be performed
  inside the isolated cryptographic security module boundary so that plaintext key material is
  never exposed outside the module" [54], and ASVS 5.0 requirement 13.3.3, at Level 3, asks that
  "all cryptographic operations are performed using an isolated security module (such as a vault
  or hardware security module)" [44]. When each one fits is this practice's choice.
- **BFF: store each cookie key with its id, its format version, its material, the time it starts
  protecting new cookies and the time the job wrote it.** Where the cookies use separate keys rather
  than subkeys of one key, also
  store its purpose, the cookie it protects. Have an instance protect new cookies with the newest
  key whose start time has passed, of that cookie's purpose where keys have one. A key added to the
  store then reaches every running instance before any of them protects with it, and the job and
  the instances can tell from the store which cookie a key protects. The purpose is this
  practice's choice. The start time is this practice's choice, after ASP.NET
  Core, which gives a new key "an activation date of { now + 2 days }" so that other
  applications can "observe the key at their next auto-refresh period" (Microsoft's docs on key
  management) [22]. The job rewrites the written time at each move of the start time (step 1 of the
  rotation below), so the check of step 1 has a time to count from; the written time is this
  practice's choice.
- **BFF: have an instance re-read the key list at an interval the team writes down ("Write it
  down" above), and also on a reload signal where the platform has one, and log the key ids it
  loaded with the id under which the load balancer lists the instance,** so a key added to the
  store reaches it within one interval. The log shows which keys each listed instance holds.
  The same line names the format versions the instance reads and, with an identity provider, the
  id of each client-credential entry it loaded and which one is "current", never the secret. The
  reload is this practice's choice, after ASP.NET Core, which checks the store for changes
  "approximately every 24 hours" [22].
- **BFF: write the reload interval down long enough that the rotation job's gap between runs, plus
  the log store's ingestion delay, plus the scheduler's start delay, is at most half of it,** so a
  run of the job falls inside the check window of step 1 below. The alert on a rotation job that
  logged no run (section 3, "Logging") then stays quiet while the job runs on schedule. That length
  is this practice's choice.
- **BFF: when the key list holds an entry the instance cannot parse, or one whose format version it
  does not know, have the instance skip that entry, log it at `ERROR`
  ([logging.md](../../python/logging/logging.md) section 4) with the key id, and count that load as
  failed for the stale-list limit below,** so one bad entry never blocks the others. A load that
  yields no key whose start time has passed counts as failed too: the instance keeps the list it
  holds and logs the load as the rule on an instance that cannot read the key store, below, logs a
  failed reload. Skipping such an entry and counting such a load
  as failed are this practice's choice.
- **BFF: have the rotation job write a key in a new format version only after every instance has
  logged that it reads that version,** which the job reads from the log store as it reads the key
  ids in step 1 below, since an instance that does not know the version skips the key (the rule
  above). The order for a new format version is this practice's choice.
- **BFF: when an instance cannot read the key store, have it keep the list it loaded and log each
  failed reload at `WARNING` ([logging.md](../../python/logging/logging.md) section 4) with the key
  ids it still holds,** so an outage of the store alone signs nobody out. An instance whose last
  successful load of the key list is older than a limit the team writes down reports not ready, so
  the load balancer takes it out, as step 7 of the leaked-key plan below does, and logs that it
  passed the limit at `ERROR` ([logging.md](../../python/logging/logging.md) section 4). Set the
  limit to the longest key-store outage the BFF must ride out plus one reload interval, since
  instances pass the limit up to one reload interval apart, and write the value down with that
  reason. The limit on a stale list is this practice's choice.
- **BFF: where the load balancer sends requests to instances that report not ready, have the
  instance itself refuse the routes that read or set a cookie once its list is older than the
  limit,** as it does when it starts without a key. Reporting not ready takes an instance out only
  where the load balancer sends nothing to an instance that reports not ready, even when every
  instance does. An AWS ALB, and Envoy past its panic threshold in its mode that sends to
  every host, send to such instances anyway. AWS's docs say that when a target group holds only
  unhealthy targets, the load balancer "routes requests to all those targets, regardless of their
  health status" [150]. Envoy's docs say that when too few hosts are healthy, Envoy "will
  disregard health status and balance either amongst all hosts or no hosts", as its cluster
  configuration chooses, and that "The default panic threshold is 50%" [151]. The rule is this
  practice's choice.
- **BFF: when an instance starts and finds no key whose start time has passed, or cannot read the
  key store, have it serve none of the routes that read or set a cookie and report not ready,**
  since it holds no key to read or protect a cookie with. When it finds no key whose start time
  has passed, it logs that at `ERROR` ([logging.md](../../python/logging/logging.md) section 4).
  When it cannot read the key store, it logs each failed read at `WARNING`
  ([logging.md](../../python/logging/logging.md) section 4), since it reads again at each reload,
  and logs at `ERROR` once the stale-list limit has passed since it started. An instance never
  generates a key itself, since every instance must hold the same set of keys (the rule above).
  The start without a key is this practice's choice.
- **BFF: rotate a cookie key in three steps,** since an instance that protects with a key the
  others do not hold yet signs users out at random, and a key removed too early signs out every
  user whose cookie it protected.
  1. The rotation job adds the new key to the store with a start time ahead by the longest
     key-store outage the BFF must ride out (the rule on an instance that cannot read the key
     store, above), plus three reload intervals, plus the clock skew between instances. So an
     outage the team planned to ride out ends before the start time. It checks on its first run
     after one reload interval plus the log store's ingestion delay has passed since the written
     time in the key's record, and before two reload intervals have passed, so a start time moved
     by that check still reaches every instance, each within one reload interval, before the old
     start time passes.
     The check reads the key ids logged by the instances the load balancer lists at that moment:
     each must have logged a key list that holds the new key id. It counts the instances the load
     balancer lists as registered and in use, and leaves out one it lists as deregistering or not
     in use, since such an instance may log no new reload: for an AWS Application Load Balancer,
     the states `draining` and `unused`, where `unused` includes a target "in the stopped or
     terminated state" [150]. The job reads the load balancer's list of instances from its API,
     and the log lines from the log store, with a read-only identity of its own, and matches each
     listed instance to its lines by the id the instance logs with its key ids (the reload rule
     above); a line it cannot find counts as not loaded. When an instance has not logged the new
     key id, or when a run finds that the check's window passed with no check logged, the job
     moves the start time later by the same margin at once, only while the start time has not
     passed, and checks again the same way. It logs the move at `WARNING`
     ([logging.md](../../python/logging/logging.md) section 4) with the key id and the ids of the
     instances that had not logged it. A run that needs to move
     the start time but cannot write the store logs it at `WARNING`
     ([logging.md](../../python/logging/logging.md) section 4) and tries again on its next run; a
     run that finds the check's window passed with the move still unwritten logs it at `ERROR`
     ([logging.md](../../python/logging/logging.md) section 4).
  2. The start time passes, and every instance protects new cookies with the new key; this step
     needs no act.
  3. The job removes the old key only when the new key's start time, plus one reload interval,
     plus the clock skew, plus the longest lifetime of a cookie the old key protects has passed.
     That lifetime is the session cookie's absolute timeout where the key protects the session
     cookie, the login cookie's `Max-Age` where it protects only login cookies, and the session's
     absolute timeout where it encrypts the tokens in session records. It removes it only when, in
     addition, every instance the load balancer lists at that moment as registered and in use,
     counted as in step 1, has logged a key list that holds the new key id, and the most recent
     reload of each of them succeeded; the job reads both from the log store as in step 1.

  NIST SP 800-57 Part 1 section 5.3.5 lets a key keep reading after it stops protecting new data
  [50]. The express-session library has no start time: it signs with the first secret in its list
  and checks with all of them [48]. So there each instance builds that list at each reload, the
  newest key whose start time has passed first and every other key after it, which needs no
  separate move at step 2. The library keeps the array it was given and reads it on each request,
  so at each reload an instance replaces the contents of that same array in one synchronous step,
  and never leaves it empty; a new array, or a single secret,
  which the library wraps in an array of its own, takes effect only at a restart [153]. Since it
  verifies a cookie by trying each secret in turn, express-session answers no to the section 4 row
  "rotation by trial over every key" [153]. The rival to the start time
  is to promote the new key by an explicit act once the check in step 1 passes. The two differ
  when the job stops after the write for longer than the margin: the start time then passes
  unchecked, while a key that waits for the act never starts protecting cookies, so the act fails
  safe, at the cost of a second write. This practice keeps the start time, as ASP.NET Core does
  (the rule above), since the job then writes each new key's material once, and its only later act
  on the key is to move the start time when the check in step 1 fails. It relies on the alert on a
  rotation job that logged no run (section 3, "Logging") for a job that stops. Where the platform
  gives no list of instances, or no log line per instance, the job cannot run the check of step 1.
  It then logs at `INFO` ([logging.md](../../python/logging/logging.md) section 4) on each run that
  no check ran. The start margin of step 1 and the stale-list limit are then the only controls,
  and the team writes that down ("Write it down" above). On such a platform the job never moves the
  start time: its line that no check ran stands for the check of step 1, so the rule on a check's
  window that passed with no check logged does not apply. On such a platform, step 3 removes the
  old key on its time condition alone, and step 5 of the client-credential rule below removes the
  old credential once the stale-list limit plus one reload interval has passed since its step 4.
  By then every instance has reloaded or reports not ready (the rule on an instance that cannot
  read the key store, above). The checks in steps 1 and 3, the job as their actor, the instances
  the load balancer lists as registered and in use as their set, and the log store as their
  channel are this practice's choice. So are the margin with the key-store outage in it, the
  check's window, the retry of a move the store refused, the `WARNING` line of a move, and what a
  run does where the platform gives no list of instances or no log line per instance.
- **BFF: before the BFF's first release to users, write down how long each cookie key protects new
  cookies and after what period the client credential is rotated ("Write it down" above),** so the
  job rotates
  by a period chosen for the threat model and the key's limits, not by a default. ASVS 5.0
  requirements 13.1.4 and 13.3.4, both at Level 3, ask for a written schedule for rotating the
  critical secrets, and for secrets that expire and are rotated as the documentation says [44].
  OWASP's Key Management cheat sheet asks to "Establish and document a key rotation schedule based
  on the system's threat model and risk assessment" [54]. The period has to end before the key
  reaches the usage limits of
  its encryption mode, counted over every instance that shares the key: OWASP's Cryptographic
  Storage cheat sheet asks to enforce "the mode's limits on message size, encryption operations,
  and initialization vector (IV) uniqueness across all instances sharing the key"
  [46]. For AES-GCM with random 96-bit IVs, OWASP's Key Management cheat sheet gives the number:
  "at most `2^32` (4,294,967,296) encryption operations across all devices sharing that key"
  [54]. Derive the period from the peak rate at which all instances together encrypt with one key,
  or count the encryptions per key id, and write the period down. NIST SP 800-57 Part 1 section
  5.3.6 recommends that a
  symmetric key that protects integrity protect new data for no more than two years
  [50], and ASP.NET Core's default key lifetime is 90 days [22].
- **BFF: before the BFF's first release to users, set up a scheduled job that rotates the keys by
  the steps above,** so rotation happens before anyone needs it and not by hand. OWASP's Key
  Management cheat sheet says: "Prefer automated key rotation using Key Management Services (KMS)
  or automated certificate management protocols (such as Automated Certificate Management
  Environment (ACME)) to reduce operational error and ensure timely updates" [54]. The job runs
  at least twice per reload interval, at a gap between runs that the rule on the reload
  interval's length above allows, and
  keeps no state of its own outside the key store and the secret store. On each
  run it reads the key list and does only the step that is due: it adds a key when the newest key
  is older than the period, counted per purpose where keys have one, runs the check of step 1 when
  its window has come, and runs step 3 when its condition holds. A run adds a key only when no key
  younger than the period exists, for that purpose where keys have one; two runs at once may still
  both add one, which is harmless, since every instance loads both keys and step 1 checks each.
  With an identity provider, the job reads on each run which client-credential step (the rule
  below) is due from the entries in the secret store, by their names and stored times, and from
  the instances' log lines, as it does for the key steps. Only "current", older than the written
  rotation period by its stored time, means step 1, which step 2 follows in the same run; "next"
  means steps 3 and 4; "previous" means step 5. Each run logs at `INFO`
  ([logging.md](../../python/logging/logging.md) section 4) what it decided. With the key id, it
  also logs whether the check of step 1 passed, failed or moved the start time, so a later run can
  tell whether a check was logged; a move goes at `WARNING`, as step 1 says. These run rules are
  this practice's choice.
- **BFF: before the first instance of an environment starts, run the rotation job once by hand,
  and give its first key a start time of now,** so the first instance finds a key it can protect
  cookies with; no instance runs yet that would have to load the key first. The rule is this
  practice's choice.
- **BFF: before the BFF's first release to users, run one cookie-key rotation and, with an
  identity provider, one client-credential rotation (the rule below) in a test environment,** so a
  rotation step that does not work shows before the first rotation in production. Check that no
  test session is signed out, that step 1 holds back while one instance is kept on its old key
  list, and that the alerts on the key's age and on an old key still in the store (section 3,
  "Logging") fire. The rule is this practice's choice. Run the test with a reload interval the
  rule on the reload interval's length allows, a few minutes where the scheduler runs at most once
  a minute, a period no shorter than the start margin of step 1 plus one lifetime of a cookie the
  old key protects, and timeouts of minutes. Where the platform fixes the reload interval, run the
  test with that interval, or with a reload of your own on a timer. ASP.NET Core Data Protection
  fixes it: its source says the refresh period "is currently fixed at 24 hours" and "is not
  settable" [154], and its docs say that "The default key lifetime cannot be shorter than 7 days"
  [22].
- **BFF, with an identity provider: rotate the client credential so that one credential works at
  every moment.** Where the provider allows two credentials at once, keep the credentials as named
  entries in the secret store, each with the time it was written: "current", which every instance
  uses, and during a rotation "next" or "previous":
  1. Have the rotation job add the new credential at the provider, through the provider's
     management API, with a credential for that API kept in the secret store under the rule above
     on the two other entries there.
  2. Have the rotation job write it into the secret store as "next", and let every instance
     reload, so each holds both entries.
  3. Have the job make a test refresh with "next" itself: one made with the refresh token of a
     test account the team keeps for this in the secret store, outside any session and its
     timeouts, whose answer the job stores there as any refresh's is. When the provider gives that
     refresh token a lifetime shorter than the period, a person signs the test account in again
     before each rotation. When the test answers `invalid_grant`, keep "next" and log that the
     test account must sign in again. Remove "next" only when the test answers `invalid_client` or
     `unauthorized_client`: then remove it at the provider and from the store, keep "current", and
     log it. Log the first failed test of a rotation at `ERROR`
     ([logging.md](../../python/logging/logging.md) section 4), since a person must act: sign the
     test account in again on `invalid_grant`, or fix the refused credential on `invalid_client`
     or `unauthorized_client`. A later run that finds the same failure in the job's earlier lines
     in the log store, read as the check in step 1 of the cookie-key rotation reads them, logs it
     at `WARNING`.
  4. Have the job mark "next" as "current" and the old "current" as "previous", writing both
     entries under their new names, and let every instance reload.
  5. When every instance the load balancer lists at that moment as registered and in use, counted
     as in step 1 of the cookie-key rotation, has logged an entry list whose "current" is the new
     credential, have the job remove "previous" at the provider, through its management API with
     the credential of step 1, and then from the secret store. Then have it list the client
     credentials at the provider and remove any that no entry names. Do that clean-up here, not
     before step 1: "current" was just written, so no other run starts step 1 now, while before
     step 1 a second run at once could remove the credential the first run had just added. The
     rotation is done when the store holds "current" only. Each instance logs that list in the
     line of the reload rule above, which names each entry by an id, never by the secret. When
     step 5 has still not run once the stale-list limit plus one reload interval has passed since
     step 4, by the time stored with "previous", the job logs it at `ERROR`
     ([logging.md](../../python/logging/logging.md) section 4), which alerts a person (section 3,
     "Logging").

  To switch back before step 5, mark "previous" as "current" again, and remove the new credential
  at the provider and from the store, as step 3's failure path does. Where the provider allows only
  one, write down the outage the switch causes ("Write it down" above). A credential the BFF does
  not hold makes every refresh fail (the rule on a refresh error that names the client's setup, in
  "Timeouts and refresh" below). OWASP's Secrets Management cheat sheet lists "Introducing new
  keys for Write operations" and "Leaving old keys for Read operations" among the ways to rotate,
  and describes a rotation in steps: "create new secret, set new secret, test new secret, finish
  rotation" [146]. The named entries and their stored times, the order, the job as the actor at
  the provider with its credential for the management API, the test account and its refresh token
  in the secret store, and the sign-in again are this practice's choice. So are what a failed test
  does, the clean-up at step 5, the switch back, and the check before step 5 with its limit.
- **BFF: treat a session or login cookie that fails to decrypt or verify, or names a key the BFF no
  longer holds, as a request with no cookie, never as a `500`, and log the reason (unknown key,
  failed check, expired) at `INFO` ([logging.md](../../python/logging/logging.md) section 4)
  without the cookie's value.** A failed rotation then shows in the log as a burst of unknown-key
  lines, and in the rate alert of section 3, "Logging", not as random sign-outs. The rule is this
  practice's choice. The iron-session library starts a new empty session when it cannot read a
  cookie, since "a 500 on every request would be worse", and its README reads a burst of
  `unknown-password` reasons as a sign that a password rotation went wrong [49]. ASP.NET Core's
  docs describe the failure in a web farm: on a node that cannot decrypt the authentication
  cookie, authorization for the requested resource fails [52].
- **BFF: when you suspect that a cookie key leaked, replace it by the seven steps below, though that
  signs out every user whose cookie a leaked key protected,** since whoever holds the key can
  write a cookie the BFF accepts and read the tokens in any copy of a cookie it encrypted [54].
  Each instance keeps the key list it loaded until it reloads [22]. Count as leaked every key that
  sat where the leaked key sat, in the same store or in the same instance's memory: the key that
  protects new cookies, a previous key still in its read period, a key whose start time has not
  passed, and each other purpose's key. The steps below call each of them a leaked key; that scope
  is this practice's choice.
  1. Sign a test user in, and keep its session cookie and, where the BFF uses login cookies, one
     login cookie with its `state`, both protected by a leaked key; step 7 uses them.
  2. Start the emergency run of the rotation job: it writes to the store a new key for each purpose
     where keys have one, with a start time of now, as the key that protects new cookies.
  3. Where a leaked key encrypts the tokens in session records, first restart or reload every
     instance and check each by its own address that it logged a key list that holds the new key
     ids, so no instance encrypts a new record under a leaked key. Then have the run end every
     session whose record a leaked key encrypted, and revoke that session's refresh token as the
     logout rules revoke it, since once the key is gone those records cannot be read. For this
     step the run uses an identity of its own, only while the run lasts, which the rule on the
     session store's access and the rule on the key store's readers above name as the one other
     identity they allow. It has read and write access to the session store, and reads the leaked
     key to read the records and the client credential to revoke. The run reuses the BFF's own
     logout and revoke code, and finds the records by the key id each record starts with. A
     session store that cannot list records by that key id must be able to before the team
     encrypts the tokens in session records, so write that down with the choice to encrypt them
     ("Write it down" above). The run logs a
     session that fails to end at `ERROR` ([logging.md](../../python/logging/logging.md) section
     4) with the count of such failures. Only a session that fails to end counts: a refresh token
     whose revoke fails is logged as the logout rules say and does not hold the key back. The run
     can be repeated, and keeps the leaked key until that count is zero. When the count stays above
     zero, the person who runs the incident decides when to delete the key anyway: deleting it
     ends those sessions too, since their records can no longer be read, but leaves their refresh
     tokens valid at the provider until they expire, so write that decision down. The step's
     own identity, the search by key id and the decision to delete the key anyway are this
     practice's choice.
  4. Have the emergency run delete each leaked key id from the store: at once for a key that
     encrypts no session record, and for a key that does, once step 3 has ended the sessions it
     encrypted or the person who runs the incident decides to delete it anyway.
  5. Restart or reload every instance. Restart them all at once, or expect failed sign-ins until
     the last one restarts, since a login cookie that a restarted instance wrote under the new key
     fails at a callback that reaches an instance not restarted yet.
  6. When the client credential sat where the key leaked, in the same secret store, replace the
     credential too, since RFC 6749 section 10.4 binds a refresh token to the client it was issued
     to [15]. Have the emergency run replace it in the order the next rule gives for a client
     credential leaked on its own: remove the leaked credential at the provider first, accepting
     the outage, then add the new one, write it into the secret store as "current" and let every
     instance load it. Never replace it by the steps of the client-credential rule above, which
     keep the leaked credential working until their last step. When the credential for the
     provider's management API sat there too, replace it as well, since it can add client
     credentials at the provider; the person or role that the rule on the two other entries in the
     secret store names replaces it.
     Replace it first, so the client credential's replacement runs with the new one.
  7. Check each instance by its own address, not through the load balancer. For a key that
     protects login cookies, send each instance's login callback the login cookie that step 1
     kept, with its `state`, and expect the error page of a failed callback. For the session
     cookie with the session's state in the cookie, or a session cookie that the framework signs
     with the session's state on the server, use the test session's cookie that step 1 kept: at
     the session check it answers `200` before step 4 and `401` after step 5, which shows the check
     can fail. In every case, also check that every instance logged a key list without
     any leaked key id, and that zero failures to end a session were logged in step 3. An instance
     that fails leaves the load balancer, restarts and is checked again; the replacement is done
     only when every instance passes.

  ASP.NET Core's docs say that until a refresh "a warmed instance might continue to unprotect data
  created with the revoked key", and ask to restart or reload every instance, to "Verify that all
  instances have refreshed before considering revocation complete", and to "Plan for the
  availability impact of coordinated restarts" [22]. Section 5 says what a leaked key still gives
  its holder after these steps. NIST SP 800-57 Part 1 section 7.5 says "A
  compromised key shall not be used to apply cryptographic protection to information", and its
  glossary counts a key as compromised on "a suspicion or confirmation" of it [50].
  OWASP's Cryptographic Storage cheat sheet counts someone who had access to the key leaving the
  organisation as a reason to rotate it [46].
- **BFF: before the BFF's first release to users, write down the steps for a leaked cookie key, who
  runs them, who starts the emergency run of the rotation job that writes the store, who to notify
  and how to check them,** so the keys can be replaced quickly when a leak comes, not worked out
  under pressure. Write the list of keys in each environment down with them. The steps count as
  leaked every key that sat where the leaked key sat, as the rule above says. OWASP's
  Cryptographic Storage cheat sheet asks that "the code and processes required to rotate a key are
  in place before they are required, so that keys can be quickly rotated in the event of a
  compromise" [46]. Its Key Management cheat sheet says "A
  compromise-recovery plan shall be documented and easily accessible", and lists in it "The
  identification and contact info of the personnel to notify" and "An inventory of all
  cryptographic keys and their use" [54]. With an identity provider, the plan also covers a client
  credential leaked on its own: the emergency run removes the leaked credential at the provider
  first, accepting the outage, then adds the new one, writes it into the secret store as "current"
  and lets every instance load it. The order of the client-credential rule above keeps the old
  credential working until its last step; this order, with the emergency run as its actor, is this
  practice's choice.
- **BFF: keep the leaked-key plan with the team's incident runbooks, where an incident opens as
  [sla.md](../../any-language/project-management/sla.md) section 3 says,** so whoever opens the
  incident finds the plan there; the plan's home is this practice's choice.
- **BFF: before the BFF's first release to users, run the leaked-key plan once in a test
  environment,** so a step that does not work shows before a leak, not during one; the test run is
  this practice's choice. In that run, also check that the alert on the unknown-key reason
  (section 3, "Logging") fires.

### A new session id at login

- **BFF: issue a new session id at login and at every change of privilege, and destroy the old
  one.** An id an attacker set before login, or one that leaked earlier, then dies with the old
  session (session fixation). OWASP's Session Management cheat sheet calls the renewal mandatory,
  ASVS 5.0 requirement 7.2.4 asks for it on every authentication, re-authentication included (the
  step-up rules under "Re-authentication" below), and OWASP Top 10:2025 lists it under A07
  [8], [42], [55].
- **BFF, with an identity provider: when the login start request carries a session cookie whose id
  the store holds as a live session, record that session's id with the attempt; destroy that
  session at the callback,** because a
  `Strict` cookie does not come with the provider's redirect [2]. With the session's
  state in the cookie, record the old cookie's session id in the same way and add it to the list
  of ended sessions (its rules are under "Logout" below) at the callback, since the new cookie does
  not stop a copy of the old one from working; the rule is this practice's choice.
- **BFF, with an identity provider: at the login callback, when destroying the old session fails,
  log it at `ERROR` ([logging.md](../../python/logging/logging.md) section 4), issue no new
  session and answer the error page of a failed callback** (the login cookie rules above), so a
  failed destroy never leaves the old session live beside a new one. ASVS 5.0 requirement 16.5.3
  asks to prevent fail-open conditions [56]. A session the store no longer holds counts as
  destroyed; only a store error is a failed destroy.
- **BFF, with an identity provider: at the login callback, store the ID token's `iss` and `sub`
  with the new session, and its `sid` when the ID token carries one,** since the back-channel
  logout rules and the step-up's checks below match on them. A provider sends `sid` only when it
  supports it (OpenID Connect Back-Channel Logout 1.0, sections 2.1 and 2.7) [57]. With the
  session's state on the server, the index rule in "Re-authentication" below writes them into the
  index of sessions by user and by `sid`.
- **BFF: create the session id from a CSPRNG with at least 128 bits of entropy: check that the
  framework's session manager does, and where you write it yourself, draw 32 bytes from the
  operating system's CSPRNG, never a UUID,** so nobody can guess a live id (ASVS 5.0 requirements
  7.2.3 and 11.5.1) [42], [47]. OWASP's Session Management cheat sheet asks for at least 128 bits
  for an id you create yourself [8].
- **BFF: with the session's state on the server, treat a session cookie whose id the store does not
  hold as no session, and never create or save a session under an id the request brought,** so an
  attacker cannot plant an id and wait for the user to sign in under it. OWASP's Session
  Management cheat sheet says "Web applications should never accept a session ID they have never
  generated" [8].
- **BFF, with an identity provider: complete a login at its callback in this order,** so each
  check runs before the new session exists, and every failure has one outcome; the order is this
  practice's choice. Each step names its rule, which holds the conditions:
  1. Check the login cookie and `state` (the rule on a callback whose login cookie is missing, in
     "The login cookie" above), and the issuer where there is more than one identity provider (the
     rule on more than one identity provider, there).
  2. Let the library exchange the code and run the ID token checks (the rule on a maintained
     OpenID Connect library, in "The login cookie" above). Log at `ERROR`
     ([logging.md](../../python/logging/logging.md) section 4) a failure the client's setup or the
     provider causes, such as `invalid_client` or a failed fetch of the provider's keys, and at
     `INFO` one the request causes, as section 3, "Logging", logs a failed sign-in.
  3. Destroy the old session the attempt recorded (the two rules on the old session above).
  4. Create the new session, with an id from a CSPRNG and the ID token's `iss`, `sub` and `sid`
     (the rules above on those values). When writing it fails, issue no session, log it at `ERROR`
     ([logging.md](../../python/logging/logging.md) section 4) and answer the error page of a
     failed callback (the login cookie rules above).
  5. Delete the login cookie, set the session cookie and redirect to the page the attempt recorded
     (the rules on the login cookie's `Max-Age` and on the page to return to, in "The login cookie"
     above).

### Timeouts and refresh

- **BFF: enforce an idle timeout and an absolute timeout on the server.** A time the client keeps,
  such as a cookie's `Max-Age`, can be changed to extend the session, so the server checks both
  timeouts on every request [8]. ASVS 5.0 requirements 7.3.1 and 7.3.2
  ask for both timeouts [42]. With the session's state in the cookie, the cookie's
  protected value carries the session's start time and its last-use time, and the BFF checks both.
  The idle clock moves when the BFF re-issues the cookie on use. The BFF re-issues it only when its
  content changed: new tokens, or a last-use time that moved past a step the team writes down.
  Otherwise a request still in flight with the old cookie can overwrite a newer one (section 5).
  That is this practice's choice. ASP.NET Core's cookie
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
  values come from the risk. OWASP gives 2 to 5 minutes idle for high-value applications and 15 to
  30 minutes for low-risk ones, and 4 to 8 hours absolute for an office application [8].
  NIST SP 800-63B-4 says the overall timeout should be at most 24 hours and the idle one at most 1
  hour at AAL2, and at AAL3 the overall timeout shall be at most 12 hours and the idle one should
  be at most 15 minutes [41]. ASVS 5.0
  requirement 7.1.1 asks for the values to be documented, with the reason for any departure from
  NIST SP 800-63B's re-authentication requirements [42]. OWASP's Session Management cheat sheet
  offers a third timeout as the alternative, a renewal timeout "after which the session ID is
  automatically renewed, in the middle of the user session", which shortens how long a stolen id
  works when the absolute timeout is long [8]. This practice does not take it: after each renewal
  the old id "would still be valid for some time", and the cheat sheet names a race in which an
  attacker who still holds it "obtains first the value for the renewed session ID" [8]. A short
  absolute timeout, written down with its reason, bounds a stolen id without that window; the
  choice is this practice's.
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
  `max_age` on every login start that has no live session, and at its callback refuse an ID token
  whose `auth_time` is older than that, or that has no `auth_time`.** Set its value, the absolute
  timeout or shorter, and write it down. `max_age` makes the provider re-authenticate a user whose
  last sign-in is older than it allows, and puts `auth_time` in the ID token for the client to
  check (OpenID Connect Core 1.0 sections 3.1.2.1 and 3.1.3.7) [27].
  Section 3.1.2.1 makes the claim required when `max_age` is sent: "When max_age is used, the ID
  Token returned MUST include an auth_time Claim Value" [27]. The BFF needs no memory of the
  session that ended; the value is this practice's choice.
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
  `invalid_scope`) mostly name the client's own request or setup, not the user's grant [15].
  Ending the session on them would sign every user out after one wrong setting, such as a client
  secret rotated at the provider but not in the BFF. `invalid_scope` can also mean a scope
  beyond the one the user granted (RFC 6749 section 5.2), which a refresh that asks for the
  granted scope does not ask for [15]. The rule is this practice's choice.
- **BFF: when a refresh fails in any other way, keep the session, answer the page `502` or `503`,
  never `401`, and log it,** because on a `401` from the API the page runs the sign-out path,
  apart from the two exceptions [security.md](../../react/security/security.md) section 6 lists.
  Such a failure is a provider that cannot be reached or does not answer, a `5xx`, a `429`, any
  other `4xx`, or a body that does not parse. `502` says that an upstream server answered badly, and
  `503` that the server cannot answer for now (RFC 9110 sections 15.6.3 and 15.6.4) [61].
  The status is this practice's choice.
- **BFF: when a refresh answer carries no `refresh_token`, keep the refresh token you have, and
  replace it only with one an answer carries,** since RFC 6749 makes the new refresh token
  optional (sections 5.1 and 6), and a BFF that stores the missing value signs the user out at the
  next refresh [15]. Okta, with rotation on, returns no new refresh token while its lifetime
  setting has not expired, and Spring Security keeps the old token in this case [62],
  [63].
- **BFF, with an identity provider: request what your provider needs to issue a refresh token, and
  when a login's answer carries none, end the session when its access token expires, and write
  that shorter session down ("Write it down" above),** since every refresh rule here needs a
  refresh token. Without one the session would outlive the access token it stands for. OpenID
  Connect Core 1.0 section 11 defines the scope `offline_access` to request a refresh token, and
  lets a provider grant refresh tokens "in other contexts that are beyond the scope of this
  specification" [27], so the provider's docs say which request it needs. The rule is this
  practice's choice.
- **BFF, with an identity provider: where the provider lets you choose, give the BFF refresh
  tokens that do not rotate, or rotation with a reuse window, and write the choice down,** since
  the BFF is a confidential client whose refresh token works only with its client authentication
  (RFC 10017 section 6.1.2.2) [1]. Without rotation the lock rules below are not needed. RFC 9700
  section 2.2.2 adds that RFC 6749 "already mandates that refresh tokens for confidential clients
  can only be used by the client for which they were issued" [16].
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

The rules from here to the rule on a request that waited until the lock expired hold only when
the provider rotates the BFF's refresh tokens, has no reuse window that covers the requests in
flight, and the session's state is on the server. They run in the order given, except that a
request that takes the lock first reads the refresh's outcome, as the rule on that outcome below
says.

- **BFF: refresh the tokens of a session at most once at a time, and let the session's other
  requests wait for that refresh and use its result,** because parallel requests would each refresh
  with the same refresh token. This rule holds when the provider rotates the BFF's refresh tokens
  and has no reuse window that covers the requests in flight, and the session's state is on the
  server. Where the provider rotates refresh tokens, the second use counts as reuse. The rule is
  this practice's choice. Auth0 then revokes every refresh token issued since, with the grant, and
  Okta invalidates the newest refresh token and the access tokens issued since sign-in, unless the
  reuse falls in its grace period [65], [62].
- **BFF: with the session's state on the server, hold that one refresh with a lock that every
  instance shares, keyed by the session id,** since the session's requests can reach any instance;
  the rule is this practice's choice.
- **BFF: when the lock cannot be taken because the store that holds it fails, answer `503` and
  never refresh without the lock,** since a refresh without it can send the same refresh token
  twice, which the provider counts as reuse (above); the rule is this practice's choice.
- **BFF: give the call to the token endpoint, together with the store of its answer, a timeout,
  and give the lock that holds a session's refresh an expiry a little longer than that timeout,**
  so a lock whose holder stopped frees itself while the requests that wait for it still wait. A
  slow provider alone also does not make a refresh outlive its lock. A call that times out is a
  provider that does not answer (the refresh failure rule above). Timeouts lower that chance and
  do not remove it. Kleppmann holds that a lock's holder paused past the lock's expiry can still
  write after another client has taken the lock, and that a timeout does not show that the other
  side is down, since a request can still arrive long after it was sent
  [66]. So a call that timed out may still have reached the
  provider and rotated the refresh token, and such a failure can still end in a sign-out once the
  provider's reuse window has passed. Since a lock can expire while its holder still runs, have
  each holder set a random value of its own when it takes the lock, and release the lock only
  while the stored value still matches, in one atomic compare-and-delete, so a holder whose lock
  expired never frees the next holder's lock. Redis's docs on locks set a value that "must be
  unique across all clients and all lock requests", and remove the key "only if it exists and the
  value stored at the key is exactly the one I expect to be", since "Using just `DEL` is not safe
  as a client may remove another client's lock" [152]. The values are this practice's choice.
- **BFF: after taking the lock, read the session's tokens again from the store, and refresh only
  when the access token read then still needs it; otherwise use that token,** since a request that
  read the session before the last holder stored its new tokens carries a refresh token the
  provider has already rotated. Sending it is the reuse the lock is there to prevent. The access
  token still needs a refresh when it has expired, or when it is the token a resource server has
  just rejected with a `401` (section 3, "Forwarding tokens"). The rule is this practice's choice.
- **BFF: store the new tokens before you release the lock,** so the next request that takes it
  refreshes with the newest refresh token, never with one the provider has already rotated; the
  rule is this practice's choice. A session the store no longer holds when the new tokens are
  stored has ended, such as at a logout in another tab: store nothing for it and answer `401`;
  only a store error is a failed store. Run the token call and that store write to completion,
  detached from the request's cancellation, and stop them only by their timeout, since a refresh
  the browser abandons, such as one for a cancelled query, would otherwise leave stored a refresh
  token the provider has already rotated.
- **BFF: before the holder releases the lock, write the refresh's outcome, done or failed with its
  time, under the session's key in the store that holds the lock, with the lock's expiry.** A
  request that takes the lock reads that outcome first. When it finds a failure written after it
  began to wait, it answers `503` without refreshing. The lock is shared across instances, so a
  waiting request learns only that the lock was released, not whether the refresh behind it
  failed. The rule is this practice's choice.
- **BFF: when the refresh that holds the lock fails, or its new tokens cannot be stored, release
  the lock and log it once at `ERROR` ([logging.md](../../python/logging/logging.md) section 4);
  each request that waited answers `503` when it reads the failed outcome,** so no waiting request
  takes the lock and refreshes again with a refresh token the provider may already have rotated.
  When the store
  failed, answer `503` to the holder's own request too. The page sees an outage it can retry, not a
  sign-out. The rule is this practice's choice. A lock in a store that cannot be written ends at
  its expiry. After a failed store, the retry avoids a sign-out only while the provider's reuse
  window lasts, since the refresh token still stored is one the provider has already rotated.
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
- **BFF: keep the list of ended sessions, the per-user times, the single-use marks of the
  re-authentication window, the step-up guess counts and the refresh locks in stores that never
  evict them before their own expiry and keep them through a restart,** since a store that evicted
  them, restarted empty or failed over answers "not on the list". So a logged-out cookie works
  again with no error and no log line. Count a read or a write that passes a timeout the team
  writes down as one that cannot be read (the rule above). The rule is this practice's choice.
  Keep every entry of the list of ended sessions, whoever writes it, for one absolute timeout after
  it was written, and every per-user time for one absolute timeout after its latest write, since
  every cookie such an entry stops started before it was written, so by then the cookie has passed
  its absolute timeout. The two lifetimes are this practice's choice. Read the store's eviction
  policy when you deploy, and alert a person (section 3, "Logging") when the store reports an
  eviction or a restart of the store that holds those entries. With the session's state in the
  cookie, the entries the store lost cannot be rebuilt. So the person decides either to replace
  the cookie key by the leaked-key plan ("Keys and secrets" above), which signs every user out, or
  to accept that a logged-out cookie may work until its absolute timeout, and writes the decision
  down ("Write it down" above). The decision is this practice's choice.

### Logout

- **BFF: at logout, with the session's state on the server, destroy the session there,** since a
  cookie deleted only in the browser leaves a session that still works from a copy of the cookie.
  OWASP's Session Management cheat sheet, ASVS 5.0 requirement 7.4.1 and OWASP Top 10:2025 A01
  ask for the session to end on the server [8], [42],
  [67].
- **BFF: with the session's state on the server, end a session with a write that a request still
  running cannot undo,** because a request still running when the session ends saves the copy it
  loaded and so writes the session back. Record the end where a session's save never writes it,
  such as the list of ended sessions, which every request then checks, or delete the session in a
  store whose save is one atomic step that fails when the record is gone (an update, never a read
  followed by a write). CVE-2025-32441 let parallel requests restore a deleted session in
  Rack's session middleware [68]. Its advisory names a store that refuses data for a
  session ended after the request began, and the rack-session fix makes the save refuse a session
  that is gone [68], [69]. Django ticket
  37249 shows that a save which checks first and writes after still restores the session, while
  Django's database store, whose save is an update, does not [70].
- **BFF: with the session's state in the cookie, write a random session id into the cookie at
  login, and copy it unchanged into every cookie the BFF re-issues for that session,** so a later
  logout can name the session it ends, whichever copy of the cookie comes back. The rule is this
  practice's choice, after ASVS 5.0 requirement 7.4.1, which names a list of terminated tokens
  [42].
- **BFF: with the session's state in the cookie, at logout add the cookie's session id to a list
  of ended sessions that every instance reads, and keep it there as long as the rule on stores
  that never evict these entries, in "Timeouts and refresh" above, says,** because a copy of the
  cookie still leads to the tokens. ASVS 5.0 requirement 7.4.1 names such a list for sessions
  held in a token, and it works without the provider [42].
  Revoking the tokens at logout (below) is then the second control. RFC 10017 section 6.1.2.3
  counts revocation as enough on its own [1]; the list is this practice's addition.
- **BFF: with the session's state in the cookie, on every request reject a cookie whose session id
  or provider `sid` is on the list of ended sessions, or whose start time is earlier than its
  user's per-user time,** so a copy of the cookie stops working as soon as its session ends. The
  back-channel logout rules below set the per-user time, and so does the rule on a disabled or
  deleted account, in "Re-authentication" below. ASVS 5.0 requirement 7.4.1 asks to verify that,
  when a session ends, "the application disallows any further use of the session" [42].
- **BFF: with the session's state in the cookie, keep the access token's lifetime short, and write
  it down,** because revocation on its own leaves a copy of the cookie working until the access
  token in it expires. A provider without access-token revocation leaves the token valid (RFC 7009
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
  try again on the same session. Until it does, the session cannot get new access tokens (RFC
  10017 section 5.2.1) [1]. The rule is this practice's choice, after ASVS 5.0 requirement 7.4.1,
  which asks that a logout end every further use of the session, and 16.5.3, which asks to prevent
  fail-open conditions [42], [56].
- **BFF: answer the logout request with success also when no session exists,** so a second tab
  that signs out after the first is not told that sign-out failed; the rule is this practice's
  choice.
- **BFF: log every logout at `INFO` ([logging.md](../../python/logging/logging.md) section 4), with
  a short hash of the session id, the user's id and whether the revoke succeeded,** so an incident
  review can see when a session ended. OWASP's Session Management cheat sheet says "it is
  recommended to record session related events, such as the creation, renewal, and destruction of
  session IDs, as well as details about its usage within login and logout operations"
  [8]. A revoke that failed leaves its token alive until its own expiry, so the line shows it. A
  line of its own logs it at `WARNING` ([logging.md](../../python/logging/logging.md) section 4)
  with the provider's error code, as ASVS 5.0 requirement 16.3.4 asks the application to log
  "unexpected errors and security control failures" [56].
  [logging.md](../../python/logging/logging.md) section 10 keeps the raw session id out of the line.
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
- **BFF, with an identity provider that sends back-channel logout: accept the provider's
  back-channel logout,** so a session the provider ends is ended at the BFF too; its logout request
  names the session to end (Back-Channel Logout 1.0) [57]. Duende's BFF accepts it only with the
  session's state on the server (Duende's docs); that is a limit of Duende's product, and the
  specification leaves the way a session ends to the application (its section 1)
  [73], [57]. Where back-channel logout is
  needed, the session's state on the server is the simpler choice; that choice is this practice's.
  With the session's state on the server, the BFF finds the sessions a logout token names through
  the index of sessions by user and by `sid` (the index rule in "Re-authentication" below). The
  rival to back-channel logout is to rely on the absolute timeout and on the end of the session at
  `invalid_grant` (section 2, "Timeouts and refresh"). Its cost: a session outlives the provider's
  logout until the next refresh fails, and longer when the refresh token was issued with
  `offline_access`.
- **BFF: validate every logout token by the steps of Back-Channel Logout 1.0 section 2.6 before
  you end anything, and where the provider sets the `typ` header, require `logout+jwt`,** since an
  unchecked token lets anyone who can reach the endpoint end a user's sessions
  [57]. ASVS 5.0 requirement 10.5.5 (Level 2) asks the relying party to check the
  type, the `events` claim and that no `nonce` is present [74]. Back-Channel Logout 1.0
  section 4.1 warns that requiring the type breaks providers that do not set it, so check what
  yours sends and write the choice down [57].
- **BFF: with the session's state in the cookie, end the session that a back-channel logout names
  by adding its `sid` to the list of ended sessions.** For a logout token with no `sid`, set a time
  per user, the latest `iat` of such a token, before which no cookie of that user counts. Never
  replace it with an earlier time: write it with one atomic act of the store that keeps the
  greater of the stored and the new time, never a read and then a write. Keep each such entry as
  long as the rule on stores that never evict these entries, in "Timeouts and refresh" above,
  says. The cookie carries the provider's `sid`, when the ID token has one ("A new session id at
  login" above), and the every-request check above rejects both. Every session the entry ends
  started before the token was issued.
  Back-Channel Logout 1.0 makes the check that no token with the same `jti` was received recently
  optional (section 2.6), and lets the provider send a logout request again after a failure
  (section 2.5), so a per-user time set at the write would also end the sessions a user opened
  after the first logout [57]. ASVS 5.0 requirement 7.4.1 names both ways for sessions held in a
  token [42].
- **BFF: when a back-channel logout token carries no `sid`, end every session of the user its
  `iss` and `sub` name, but only the sessions that started before the token's `iat`,** since
  Back-Channel Logout 1.0 section 2.4 says a token without `sid` asks for all of that user's
  sessions at the client to be logged out [57]. The limit holds for the reason the rule above
  gives for the state in the cookie: a provider may send the token again after a failure and the
  `jti` check is optional, so without the limit a re-sent token would also end the sessions the
  user opened after the first logout [57].
- **BFF: with the session's state on the server, after a back-channel logout ends a session, revoke
  its refresh token at the provider, unless the token was issued with `offline_access`,** since
  Back-Channel Logout 1.0 section 2.7 says that "Refresh tokens issued without the
  "offline_access" property to a session being logged out SHOULD be revoked" [57]. Log a revoke
  that fails at `WARNING` ([logging.md](../../python/logging/logging.md) section 4) with the
  provider's error code, and do not retry it. Not retrying follows the logout rule above. With the
  session's state in the cookie, the BFF cannot revoke it (section 5).
- **BFF: answer a back-channel logout with `200` also when no session matches, and with `400` when
  the logout token fails validation,** since section 2.7 of the same specification counts a user
  who is already logged out as a logout that succeeded, and section 2.6 asks for `400` when a
  validation step fails [57].
- **BFF: log at `INFO` ([logging.md](../../python/logging/logging.md) section 4) a valid logout
  token that matches no session,** so a BFF whose sessions never match shows as a run of such
  lines; the rule is this practice's choice.
- **BFF: before the BFF's first release to users, sign in, end that session at the provider, and
  check that the BFF's session ends; repeat it when the BFF's host name, its firewall or its
  registration at the provider changes,** since a wrong registered URI or a firewall leaves the
  BFF with no logout token at all. So no log line and no alert shows it (section 5). The rule is
  this practice's choice.
- **BFF: when the session that a valid logout token names cannot be ended, log it at `ERROR` with
  the token's `iss`, `sub` and a short hash of its `sid`
  ([logging.md](../../python/logging/logging.md) sections 4 and 10), and answer `400`,** since
  section 2.8 of the same specification asks for `400` when the logout failed, not the `503` of the
  store-outage rule above [57]. A session store that cannot be written is one such case. A session
  the store no longer holds counts as ended; only a store error leaves a session that cannot be
  ended. Section 5 names what this leaves open.
- **BFF: prefer back-channel to front-channel logout,** because front-channel logout loads the BFF
  in a frame on the provider's page, where the `SameSite=Strict` session cookie is not sent (RFC
  6265bis draft, section 4.1.2.7) and where a browser that blocks third-party content can keep the
  frame from the session's state (Front-Channel Logout 1.0 section 4.1) [2], [75]. Its request also
  carries no signature, while a back-channel logout token is signed (Back-Channel Logout 1.0
  section 4) [75], [57].
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
ASVS 5.0 requirement 7.5.1, a Level 2 requirement [42]. A team at Level 1 may skip them, and so
may a team whose identity provider holds the email, the phone, the second factor and the recovery
data and asks for re-authentication itself. Write the choice down ("Write it down" above says
where). The rules after them are outside that skip: ending a user's other sessions (7.4.3)
holds at Level 2 and above, and ending every session of a disabled or deleted account (7.4.2)
holds at every level [42].

- **BFF: ask for re-authentication before a guarded request: a request that changes something the
  team lists as needing re-authentication, such as the email address, the phone number, the second
  factor or the recovery data,** so a stolen session cannot take over the account. ASVS 5.0
  requirement 7.5.1 asks for full re-authentication before a change to "sensitive account
  attributes which may affect authentication such as email address, phone number, MFA
  configuration, or other information used in account recovery" [42]. The rules below say how, by
  who logs the user in.
- **BFF, with an identity provider: re-authenticate the user at the provider, and never ask for
  the provider's password,** since RFC 9700 section 2.4 forbids the password grant, the only way
  the BFF could check it [16]. Start a login with `max_age=0`, which OpenID Connect Core
  1.0 section 3.1.2.1 makes equal to `prompt=login` and which makes the ID token carry
  `auth_time` [27].
- **BFF, with an identity provider: answer a guarded request that the session's re-authentication
  does not cover (the window rule below) with the `403` and `reauth_required` below, and keep
  nothing of the request,** since the page starts the step-up by a navigation to the BFF's login
  endpoint, the start RFC 10017 section 6.1.2.1 describes [1]. The page sends the request again
  once the user is back, as RFC 9470 section 2 has the client repeat its request [80]. The rule is
  this practice's choice.
- **BFF, with an identity provider: treat a login start that carries a live session and the
  step-up flag, the query parameter `step_up=1`, as a step-up, and send the user to the provider
  with `max_age=0`, and with the challenge's `acr_values` when the step-up answers an RFC 9470
  challenge,** so every login-cookie rule above holds for it unchanged. A login start without a
  live session is a first login, whatever its flag says. The rule and the parameter's name are this
  practice's choice.
- **BFF, with an identity provider: name in the `acrValues` field of the `403`'s body only those of
  a relayed challenge's `acr_values` that are on the list the team writes down, as a string that
  holds the space-separated values.** At a step-up's login start, accept the query parameter
  `acr_values` only when each of its space-separated values is on that list. The page can then
  pass the value on and cannot pick one the resource servers never ask for. The rule and the
  parameter's name are this practice's choice. RFC 9470 section 4 has a client that receives the
  challenge use its `acr_values` in the authorization request it builds [80]. A challenge none of
  whose values is on the list gets the answer of the relay rule in section 3, "Forwarding tokens".
  A login start whose `acr_values` holds a value that is not on the list gets the page of fixed
  text that a failure on a navigation gets (section 2, "Reading the `Cookie` header"), and a log
  line.

RFC 9470 section 2 has the client repeat its request once the user has re-authenticated; here the
page sends the request again after the navigation back [80]. The page could keep itself
loaded by re-authenticating the user in a popup, but the reference policy's
`Cross-Origin-Opener-Policy: same-origin` ([security.md](../../react/security/security.md)
section 5) cuts the page's link to the popup (MDN), so a popup flow needs that header relaxed to
`same-origin-allow-popups`, which MDN names for OAuth popups [81].
The navigation needs neither. Its cost falls on the page and the user: the page keeps what the user
typed in `sessionStorage` across the navigation, or asks for the step-up before the form, and the
user sends the change again once back ([security.md](../../react/security/security.md) section 6).

In another design, the BFF holds the change and starts a login attempt for it, so one
re-authentication admits only that change. OWASP's Transaction Authorization cheat sheet favours
that design: its section 2.3 asks that significant transaction data be "generated and stored on a
server, then passed to an authorization component" [82]. This practice does not take it, for
three reasons. First, it needs a start in which the BFF answers with the provider's URL for the
page to open, and RFC 10017 section 6.1.2.1 says that start "requires a custom implementation and
makes it harder to use standard OAuth libraries" [1]. Second, it keeps state for each guarded
request. Third, it does not stop a script on the page, which can send its own change and open the
returned URL itself; RFC 10017 section 6.1.4.1 says nothing prevents client hijacking "apart from
stopping the execution of malicious code in the first place" [1]. A variant holds the change only
for a request that changes state, one per session, and starts the same navigation. It escapes the
first two reasons. It still needs a held change with a size bound, a delete at each end of the
session, more outcomes that tell the page what became of the held change, and a check that the
held change's session is still live. It gives nothing against a script on the page that the
single-use window below does not. Neither
design meets the cheat sheet's section 1.1, which asks that the user can "identify and
acknowledge the data that is significant to a given transaction", since an identity provider's
sign-in prompt does not show the change [82]. The single use in
the rule below keeps one change per re-authentication.

- **BFF, with an identity provider: at a step-up's login start, record with the attempt, in its
  protected record ("The login cookie" above), the id of the session the request carries, with
  that session's `iss`, `sub` and `sid`, and that the attempt is a step-up,** since the callback
  is a cross-site navigation that carries no `Strict` session cookie. Its checks below need that
  session. With the session's state in the cookie, also record that session's start time and
  last-use time. The rule, the two recorded times included, is this practice's choice.
- **BFF, with an identity provider: at a step-up's callback, accept the re-authentication only
  when the new ID token's `iss` and `sub` equal those recorded with the attempt and its
  `auth_time` is later than the attempt's start time minus a skew allowance in seconds that the
  team writes down.** `iss` and `sub` together are the only claims a client can rely on to name the
  same user (OpenID Connect Core 1.0 section 5.7) [27]. So a thief who holds the cookie cannot pass
  the step-up by signing in to their own account. A provider session that answers without asking
  the user does not count (OpenID Connect Core 1.0 section 3.1.3.7; NIST SP 800-63B-4 section 5.2
  makes the relying party the judge) [27], [41]. OpenID Connect Core 1.0 section 2 gives
  `auth_time` as "the number of seconds from 1970-01-01T00:00:00Z as measured in UTC", on the
  provider's clock, and for the ID token's
  `exp` lets implementers "provide for some small leeway, usually no more than a few minutes, to
  account for clock skew" [27]. Keep the BFF's clock synchronised, keep the allowance to seconds,
  since minutes would let a provider session that answered without asking the user pass the
  check, and on a refusal log both values. An ID token with no `auth_time`, or with no `acr` when
  the step-up asked for `acr_values` (the rule below), fails the check: answer `refused`. The
  allowance is this practice's choice.
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
  2. Take the recorded session's start and last-use times from the attempt's record with the
     session's state in the cookie, and from the store with the state on the server. When the
     recorded session is no longer live, because the store no longer holds it, its id is
     on the list of ended sessions, it started before its user's per-user time, or its timeouts
     have passed, issue no new session and answer `failed`. So a step-up never brings back a
     session that a logout, a back-channel logout or a disabled account ended while the user was
     at the provider. Otherwise end it: destroy it, or add its id to the list of ended sessions.
     When that fails, log it at `ERROR` ([logging.md](../../python/logging/logging.md) section 4),
     issue no new session and answer `failed`, since ASVS 5.0 requirement 16.5.3 asks to prevent
     fail-open conditions [56].
  3. Issue the new session as a login does ("A new session id at login" above; ASVS 5.0
     requirement 7.2.4 asks for it on re-authentication too) [42]. It holds the tokens of
     the step-up's own code exchange (RFC 9470 section 4); the new ID token's `iss`, `sub` and
     `sid`, or the recorded `sid` when the token carries none, so back-channel logout still finds
     the session; and the time of this callback as the session's re-authentication time
     [80]. Its idle and absolute timeouts start again, since NIST SP 800-63B-4 section 5.2
     says that successful reauthentication "SHALL reset both timeouts" [41]. A team
     that keeps the absolute timeout of the first sign-in writes its reason down ("Write it down"
     above says where), since ASVS 5.0 requirement 7.1.1 asks for a reason for any departure from
     NIST SP 800-63B [42]. When issuing it fails, log it at `ERROR`
     ([logging.md](../../python/logging/logging.md) section 4) and answer `failed`; the user then
     has no session, since step 2 ended the old one.
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
  `state` with a `303` to one fixed route of the page, carrying in its query parameter `outcome`
  one of three fixed codes, never a value taken from the request,** so the page that loads after
  the navigation can ask the user to send the change again. It can also say why it cannot. The
  rule and the parameter's name are this practice's choice. Each code has one meaning:
  - `reauthenticated`: the new session holds a fresh re-authentication (step 4 above);
  - `refused`: a check failed (step 1);
  - `failed`: the provider answered with an error (the rule above), the code exchange or the ID
    token checks failed (step 0), the recorded session was no longer live or ending it failed
    (step 2), or issuing the new session failed (step 3).

  A callback whose login cookie is missing, cannot be read, or does not match the `state` gets the
  error page of a failed callback instead ("The login cookie" above).
- **BFF, with an identity provider: let a guarded change through only while the session's
  re-authentication time is younger than a window the team writes down, long enough for the user
  to finish the change, and consume that time before you apply the change,** since ASVS 5.0
  requirement 7.5.1 asks for full re-authentication before the change [42]. OWASP's Transaction
  Authorization cheat sheet, section 1.5, warns that a credential asked for once lets the user
  "authorize any transaction during the entire session" [82]. A first login sets no
  re-authentication time, and a session without one is outside the window, so the first guarded
  change after sign-in asks for a step-up. The first login sends no `max_age=0`, so the provider
  may answer it from its own session without asking the user, and such an answer does not count
  (the rule on accepting a step-up at its callback, above). Consume it in one atomic act: with the
  session's state on the server, a compare-and-clear of the re-authentication time in the session
  store, never on the session object the request loaded. With the session's state in the cookie,
  the act is a set-if-absent of the pair of the session id and the re-authentication time in the
  store that holds the list of ended sessions, kept there until the window ends. Apply the change
  only when that write succeeds; when it cannot be written, answer `503` and apply nothing. Two
  parallel requests that read the time first and clear it after would both pass, and with the
  state in the cookie every copy of the cookie still in flight carries the time. ASVS 5.0
  requirement 15.4.2 (Level 3) asks that a check on a resource's state and "the actions that depend
  on them are performed as a single atomic operation to prevent time-of-check to time-of-use
  (TOCTOU) race conditions" [145]. A script on the page can still use the window (RFC 10017 section
  6.1.4.1); the single use limits it to one change [1].
  The window, the single use and the atomic consume are this practice's choice; a team that lets
  several changes through one window, as GitHub's sudo mode does for two hours, writes that down
  [83].

A step-up with a first-party login works differently from the provider's step-up above, because
the user answers on the page. At an identity provider the user leaves the page and comes back
through the callback, so the BFF never gets the answer and the guarded request together. With a
first-party login the page asks the user itself, so the answer can travel with the guarded
request: the BFF checks it, applies that one request, and keeps nothing between two requests. The
design is this practice's choice. The rival is a re-authentication endpoint that takes the answer
and sets the session's re-authentication time, under the single-use window of the provider's
step-up above. This practice keeps the answer with the guarded request, since such an answer
authorises only the change it comes with, as the rule on taking the answer below asks after
OWASP's Transaction Authorization cheat sheet, section 1.5 [82], while the window binds no change:
it lets through whichever guarded change comes first.

- **BFF, with a first-party login: before a guarded change, ask again for every factor the user's
  sign-in asks, the password and the second factor where the account has one, with the `403`
  below,** since ASVS 5.0 requirement 7.5.1 asks for full re-authentication, while its Level 3
  requirement 7.5.3 asks only for at least one factor [42]. Reading "full" as every factor
  of the sign-in is this practice's choice. OWASP's Session Management cheat sheet, guidance
  rather than a standard, asks for less: "Prompt users for primary credentials (e.g., password) or
  enforce MFA" [8].
- **BFF, with a first-party login: take the answer only with the guarded request it is for, and
  keep no change between the two requests,** so an answer authorises only the change it comes
  with, never every change of the session. The page sends that request again with the answer.
  The rule is this practice's choice, after OWASP's Transaction Authorization cheat sheet, section
  1.5, which warns that credentials asked for once let the user "authorize any transaction during
  the entire session" [82]. That section also asks for
  authorization credentials unique to each transaction, which a password typed again is not
  [82]; leaving that part out is this practice's choice.
- **BFF, with a first-party login: take the answer from the JSON body field `reauthAnswer` of the
  guarded request, never the URL, and remove the field from the request once it is checked, before
  the request is applied,** so the code that applies the change never holds, stores or logs the
  password. ASVS 5.0 requirement 14.2.1 asks that "the URL and query string do not contain
  sensitive information", and requirement 16.2.5 says that "it may not be allowed to log certain
  data, such as credentials" [84], [56]. Removing the answer before the request is applied, and
  the field's name, are this practice's choice.
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
  at its end,** so a thief who holds a stolen session cannot guess the password through the
  step-up, not even with answers sent in parallel. Keep the count in the session's record, or under
  a key that expires with it, and delete it when the session ends or moves to a new id. Keep it in
  a store that never evicts it before its session ends (the rule on stores that never evict these
  entries, in "Timeouts and refresh" above), since an evicted count starts again at zero and gives
  more guesses than the number below allows. Compare an answer only while its raised count is
  below a small number the team writes down ("Write it down" above). When the count reaches it,
  end the session and log it without comparing the answer. ASVS 5.0 requirement 6.3.1 asks for
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
- **BFF, with a first-party login: answer a wrong answer with a `403` whose JSON body carries the
  fixed code `reauth_failed`, and with `401` once the guess limit has ended the session,**
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

- **BFF: ask the page for re-authentication with a `403` whose JSON body carries the fixed code
  `reauth_required`, and never with a `401`,** because on a `401` from the API the page runs the
  sign-out path, apart from the two exceptions [security.md](../../react/security/security.md)
  section 6 lists. RFC 9470's `401` with the error `insufficient_user_authentication` is a
  resource server's challenge to its OAuth client, which here is the BFF [80]. So RFC 9470 governs
  the hop from the resource server to the BFF (section 3, "Forwarding tokens", says what the BFF
  does with it), not the hop to the page, and the signal to the page is this practice's choice.
  The `Page:` rules in [security.md](../../react/security/security.md) section 6 say what the page
  does with it.
- **BFF: after a change or removal of any authentication factor, a password changed by a reset or
  a recovery included, offer to end every other session of the user** (ASVS 5.0 requirement
  7.4.3), so a session stolen before the change stops working [42]. The rules below say
  how, by who logs the user in.
- **BFF, with the session's state on the server: index each session by its user and by the
  provider's `sid`,** so a back-channel logout, the end of a user's other sessions and the end of
  a disabled account find every session they name in one lookup, not a scan of every session. Its
  user is the ID token's `iss` and `sub`, or the first-party user id. Write the index with the
  session, and fail the login, or the step-up's move to a new session id, when the index cannot be
  written.
  Back-Channel Logout 1.0 section 2.4 asks, for a logout token with no `sid`, that "all sessions
  at the RP for the End-User identified by the "iss" and "sub" Claims be logged out"
  [57]. A store read only by session id cannot find them: Spring Session's docs
  say that only some of its session stores can look up the sessions of one user, and that the
  application must fill the attribute that lookup reads, since "It is your responsibility to
  ensure that the attribute is populated" [87]. Failing the login follows ASVS 5.0
  requirement 16.5.3, which asks to prevent fail-open conditions [56]; the index is this
  practice's choice. Remove a session's entries from the index when the session ends, or give them
  the expiry of its record, and let a lookup skip and remove an entry whose session the store no
  longer holds. So the index does not grow without bound, and a back-channel logout or the end of
  other sessions does not fail on a session that already ended. The clean-up is this practice's
  choice.
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
  ASVS 5.0 requirement 16.5.3 asks to prevent [56]. A session the store no longer holds counts as
  destroyed; only a store error is a failed destroy.
- **BFF: when an account is disabled or deleted, end every session of the user yourself,** so a
  disabled or deleted account keeps no session that still works (ASVS 5.0 requirement 7.4.2) [42].
  With the session's state on the server, destroy each session of the user, as the logout rules
  above destroy one. With the session's state in the cookie, set that user's per-user time to now,
  unless it is already later, with one atomic act of the store that keeps the greater of the
  stored and the new time, never a read and then a write ("Logout" above). Where the provider
  disables the account, its back-channel logout ends the sessions as the back-channel rules above
  say. When ending them fails, log it at `ERROR` ([logging.md](../../python/logging/logging.md)
  section 4), return the error to the caller that disabled the account, and alert a person
  (section 3, "Logging"); the failure path is this practice's choice.

### Forwarding to resource servers

These rules say where the BFF forwards and what the forwarded request carries. Refreshing a token
before forwarding, and the answers to a resource server's `401`, are in section 3,
["Forwarding tokens"](#forwarding-tokens).

- **BFF: forward requests only to an allowlist of resource servers,** mapping each route to a
  fixed backend, validating the path of any dynamic route, and attaching the access token only to
  those requests (RFC 10017 section 6.1.3.6) [1]. A route that takes its host or path
  from the request can send the user's access token to another server. Write each entry of the
  allowlist as an `https://` origin, since RFC 6750 section 5.3 says that clients "MUST always use
  TLS [RFC5246] (https) or equivalent transport security when making requests with bearer tokens"
  [103].
- **BFF: do not follow a resource server's `3xx`; answer the page `502` and log it,** since a
  redirect sends the request, and an HTTP client may send the access token with it, to a host the
  allowlist never checked. RFC 10017 section 6.1.3.6 warns that attackers "may attempt to
  manipulate the BFF into forwarding requests to unintended hosts", "potentially exposing the
  user's access token" [1]. OWASP's Server Side Request Forgery Prevention cheat sheet says:
  "Disable the support for the following of the redirection in your web client" [148]. The `502`
  is this practice's choice.
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
- **BFF: build the answer to the page from an allowlist of the resource server's response headers:
  drop `Set-Cookie` and every `Access-Control-*` header, and set section 3's response headers and
  the CORS headers yourself.** A resource server, one another party runs or one an attacker
  controls, then cannot plant a cookie under the session or login cookie's name. It also cannot
  push the `Cookie` header past the server's size limit, or send CORS headers that contradict the
  API's own policy.
  A relayed `Set-Cookie` meets every condition of the `__Host-Http-` prefix, which tells the
  server only that "the cookie was set using a Set-Cookie header" with `Secure`, `HttpOnly`,
  `Path=/` and no `Domain` (the layered-cookies draft, section 4.1.3.4) [3]. The rule is this
  practice's choice.
- **BFF: when it forwards to more than one resource server, attach to each the access token issued
  for that server, asked for with a resource indicator where the provider supports one,** since
  RFC 9700 section 2.3 asks that access tokens be restricted to one resource server, or to a small
  set where that is not feasible [16]. ASVS 5.0 requirement 10.3.1 has a resource server refuse a
  token meant for another [74]. RFC 9700 section 4.10.2 names resource
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
table's first row), and `no-store` keeps the response out of every cache (section 3, "Response
headers").

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
where the server already has one, stays on (item 1). NIST SP 800-63B-4 section 5.1 says "POST/PUT
content SHALL contain a session identifier that the RP SHALL verify to protect against cross-site
request forgery (CSRF)" [41]. This practice follows RFC 10017 sections 6.1.3.3.2 and 6.1.3.3.3
instead, which make the custom header together with CORS a CSRF defence and rank the anti-forgery
cookie no higher than it, as quoted above [1]. A token would cost the BFF a key that joins the
rotation set of section 2, "Keys and secrets", for a signed token, or state kept for each session,
for a synchronizer token; a token in a cookie the page reads cannot carry the `__Host-Http-` name,
since that name requires `HttpOnly`. That cost is this practice's reading.

- **BFF: keep other applications and user content off the site the BFF shares with the page where
  you can, and when a subdomain's service is retired, remove its DNS record before you delete the
  resource it points to,** since `SameSite` "is adequate if the BFF is never considered to be same
  site with any other applications" (RFC 10017 section 6.1.3.3.1) [1]. The same section names "a
  subdomain-takeover attack" against a sibling, which makes CSRF against the BFF possible again
  [1]. Deleting the resource first leaves "an immediate window for takeover" (OWASP's Subdomain
  Takeover Prevention cheat sheet) [89]. The rules on sibling subdomains in sections 2 and 3 stay
  for a site where this cannot hold.
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
  custom-header check,** since some old browsers send no `Sec-Fetch-*` headers. OWASP's CSRF
  cheat sheet calls this fallback "a mandatory requirement" for any Fetch Metadata implementation
  [10].
- **The server requires the custom header, `X-Requested-With` with any value that is not empty, on
  every request to an API route,** since Fetch Metadata is absent from requests that old browsers
  send (item 4 of OWASP's list above) [10]. RFC 10017 section 6.1.3.3.2 says "the BFF SHOULD
  require that the browser-based application includes a custom request header", and "When this
  mechanism is used, the BFF MUST ensure that every incoming request carries this static header"
  [1]. The header's name is this practice's choice; the examples send `billing-app`.
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
  section 2 says where),** so a tab still on the previous bundle or a client nobody listed is not
  refused from the first deploy. Fix each legitimate caller the log shows, or exempt it when it is
  one of the endpoints the table below names. Enforce the check on that date, so it does not stay
  log-only, where it refuses nothing. web.dev gives these three steps for a
  Resource Isolation Policy, OWASP's CSRF cheat sheet says "Start in 'log only' mode", and
  [security.md](../../react/security/security.md) section 5 uses the same order for a new policy
  [24], [10]. The written date is this
  practice's choice.
- **API: in the log-only stage, also log the `User-Agent` of each request that arrives without
  `Sec-Fetch-Site`, and before you enforce, fix whatever strips the header when a current browser
  shows up in that log,** since a proxy, gateway or load balancer that removes `Origin` or the
  `Sec-Fetch-*` headers switches the Fetch Metadata check off silently. A request with neither
  header goes on to the custom-header check. OWASP's CSRF cheat sheet says that
  intermediaries "may remove or modify `Origin` and `Sec-*` headers", calls such header stripping
  "problematic, but common", and asks to "Track which user agents include `Sec-Fetch-*`"
  [10].

### What the server does

The server's CSRF checks run on each request to an API route in this order, before the session
lookup; the rules above and below say why:

1. When the request matches a row of the exemption table below, it skips the checks that row
   exempts it from, and the row's guard runs instead.
2. The Fetch Metadata check (the rule on two origins of one site, in "Fetch Metadata and
   exemptions" below).
3. When `Sec-Fetch-Site` is absent, the `Origin` check (the rule on an absent `Sec-Fetch-Site`, in
   "CSRF" above).
4. The custom-header check (the rule on the custom header, in "CSRF" above).

A request that fails a check gets the answer of the rule on refusals with `403` below.

Where the server has the framework's own CSRF check, that check runs too, with its own refusal.

#### Fetch Metadata and exemptions

- **When the page and the API are two origins of one site, let Fetch Metadata allow only the exact
  origins in the setting of allowed origins, never every `same-site` request.** The page at
  `https://app.example.com` and the
  API at `https://api.example.com` are one site, so every request from the page arrives with
  `Sec-Fetch-Site: same-site` (the W3C Fetch Metadata draft) [25].
  OWASP's cheat sheet allows `same-site` only when the threat model trusts every sibling
  subdomain, and its sample code rejects it on state-changing methods; Filippo Valsorda's
  algorithm (2025) rejects it on those methods too, unless `Origin` equals a trusted origin,
  "compared by simple equality" [10], [90].
  So the server accepts `same-origin`, and a `same-site` request only when its `Origin` is exactly
  an origin in the setting of allowed origins (the rule below), such as `https://app.example.com`,
  reads included (the rule above), and refuses `cross-site`, `none` and every other `same-site`
  request. When the API is on the page's own
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
  is not allowed to make** (RFC 9110 sections 15.5.2 and 15.5.4), because on a `401` from the API
  the page runs the sign-out path, apart from the two exceptions
  [security.md](../../react/security/security.md) section 6 lists [61]. The `401` carries no
  `WWW-Authenticate`: no registered authentication scheme describes a cookie session, and the page
  reads the status, not a challenge; this departs from
  the MUST of RFC 9110 section 15.5.2 and is this practice's choice [92],
  [61]. The logout endpoint is the exception: it answers success also when no session
  exists (section 2).
- **Exempt only the endpoints in the table below, each from the custom header, and from the Fetch
  Metadata check unless its row keeps that check, as a row for Server Functions does (the rules on
  Server Functions below), and guard each one as its row says,** since a
  request reaches each of them without the custom header. This table is this practice's departure
  from the MUST of RFC 10017 quoted above, and OWASP's CSRF Prevention cheat sheet asks for such
  an explicit list, each endpoint secured on its own [1],
  [10]. These endpoints skip the framework's own CSRF
  check too, since they cannot carry its token.

| Exempt endpoint | Matches by | Guarded by |
|---|---|---|
| the login start, a top-level `GET` | one exact path and the method `GET` | it changes neither the user's data nor the session; it starts a login attempt, which the login-cookie rules of section 2 bound |
| the login callback, which also completes a step-up | one exact path and its method | `state`, the nonce and the PKCE verifier bound to the login cookie (section 2) [16]; for a step-up, also the checks of section 2's step-up callback |
| the back-channel logout endpoint | one exact path and its method | validating the signed logout token, as the logout-token rule of section 2, "Logout", says; a cap on its size and its rate, and on refetching the provider's keys (the rules on the back-channel logout endpoint below) |
| the report intake, a separate endpoint that takes anonymous reports | one exact path and its method | it reads no session, so a report carries no session to forge; the rule on reports below |
| the WebSocket handshake, a `GET` on its one path | one exact path and the method `GET` | the exact `Origin` check below |
| a file the page opens by navigation (a download link) | one route template (a fixed path with the record id as one encoded segment) and the method `GET`; when the request carries Fetch Metadata, also `Sec-Fetch-Mode: navigate` and a `Sec-Fetch-Dest` other than `object` or `embed`, the navigation test of web.dev's Resource Isolation Policy [24] | it changes nothing, and its answer goes to the user's own window, where no other site can read it (OWASP's CSRF cheat sheet: keep `GET` free of state changes) [10] |
| the CORS preflight | the method `OPTIONS` on any API path | it carries no cookie and no custom header, and changes nothing [93] |
| the readiness check the load balancer calls | one exact path and the method `GET` | it reads no session, and answers only ready or not ready, with no key id; serve it on an internal listener where you can |

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
  `Sec-Fetch-Mode: navigate` on its own, by a missing header or by a path prefix,** since a broader
  exemption lets a sibling subdomain's form through with the user's cookie. Every route in the
  table takes the cookie without the custom header. Add a route the page loads without `fetch`
  only as a last resort, as a row like the download link's: one route template, for a `GET` that
  changes nothing. A request mode may narrow a row, as it does for the download link,
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
- **BFF, with an identity provider: cap the size of each request body the back-channel logout
  endpoint takes, and limit how many requests one source sends it in a time window the team
  writes down,** since the endpoint takes a signed token from anyone, with no session and no CSRF
  check. OWASP's API Security Top 10 (2023, API4) asks for a maximum size on every payload and "a
  limit on how often a client can interact with the API within a defined timeframe" [94]. ASVS 5.0
  requirement 10.5.5 asks a relying party that uses back-channel logout to mitigate "denial of
  service through forced logout" [74]. The values are this practice's choice.
- **BFF, with an identity provider: when a logout token names a key id the BFF does not hold,
  refetch the provider's keys at most once per interval the team writes down,** so a flood of
  tokens with made-up key ids cannot make the BFF call the provider on each one; the rule is this
  practice's choice. When the interval refuses a refetch, answer `400` and log it at `WARNING`
  ([logging.md](../../python/logging/logging.md) section 4) with the token's `iss` and the key id.
  Such a refusal comes from a flood of made-up key ids, or, during one, from a genuine logout token
  signed with a key the provider began to use after the last refetch. OpenID Connect Core 1.0
  section 10.1.1 allows that: "The signer can begin using a new key at its discretion" [27]. Such
  a logout is then dropped. When a refetch fails, answer
  `400`, log it at `ERROR` with the token's `iss` and the key id, and count it in the alert on a
  back-channel logout that could not end its session ("Logging" below).
- **Never change the user's data or session on a `GET`.** The login start, which starts a login
  attempt, and the login callback, which creates the session or, after a step-up, replaces it,
  are the only exceptions, each guarded as its row in the exemption table says. OWASP notes that
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
- **For Server Functions and the framework's route actions, keep the Fetch Metadata check,** since
  each one is a public endpoint that anyone can send a `POST` to
  ([security.md](../../react/security/security.md) section 8), and the framework's runtime sends
  it, not the one API client.
- **For them, keep the framework's own `Origin` check on where it has one, at a version that runs
  it on every unsafe method,** since a framework's own check can be missing or partial. Next.js
  lets a request with no `Origin` through with a warning, and React Router's Framework Mode had no
  such check before 7.12.0 (CVE-2026-22030) and skipped `PUT`, `PATCH` and `DELETE` until 7.15.1
  (CVE-2026-53663) [97], [100], [101], [102].
- **For them, either have each call carry the custom header, or add them to the exemption table as
  a row that skips the custom header only, whose guard also rejects a request with neither
  `Sec-Fetch-Site` nor `Origin`,** since OWASP's CSRF cheat sheet says to reject a state-changing
  request when neither header establishes its origin, unless another CSRF defence succeeds [10].
  The three rules are this practice's choice.

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
  not refresh; answer the page `403` with `reauth_required`,** since RFC 9470 uses that challenge
  to say that the user's authentication does not meet the resource server's needs, which a
  refreshed token does not change (section 2, "Re-authentication") [80]. When the challenge
  carries `acr_values`, name only those of its values that are on the list the `acr_values` rule
  of section 2, "Re-authentication", asks the team to write down, in the `403`'s field that rule
  names. So the step-up the page then starts asks for them and passes the login start's check on
  each value, with the `max_age=0` the step-up rules of section 2 ask for, which also meets any
  `max_age` the challenge names. One listed value is enough, since the resource
  server "requires one of these values" (RFC 9470 section 3) [80]. When the challenge's
  `acr_values` names no value on that list, answer the page `502`, log it at `ERROR`
  ([logging.md](../../python/logging/logging.md) section 4) and alert a person ("Logging" below),
  since the step-up the page would start cannot meet the challenge; the rule is this practice's
  choice.

#### WebSocket

These rules hold only when the server accepts WebSocket connections; a BFF without them skips this
subsection and its section 4 rows.

- **API: check on every WebSocket handshake that `Origin` is exactly an origin in the setting of
  allowed origins (the one the Fetch Metadata rule reads),** and answer `403` to any other origin.
  The browser sends the session cookie with the handshake, the
  handshake cannot carry the custom header, and `SameSite` lets a sibling subdomain through, so
  without the check a page elsewhere opens a connection as the user (OWASP's WebSocket Security
  cheat sheet; the WebSockets standard; RFC 6455 section 10.2) [104],
  [105], [106].
- **BFF: tie each WebSocket connection to its session on the server, and close it when the
  session ends or gets a new id:** at logout, at the idle and absolute timeouts, and when a
  back-channel logout or one of the refresh rules ends the session (section 2, "Logout" and
  "Timeouts and refresh"). Close it too when a step-up issues a new session id (section 2,
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
  the page checks the session and reconnects with the current cookie. When the re-check cannot read
  the session store or the list of ended sessions, close the socket with a code other than the
  session-ended one, so the page checks the session and meets the `503` of the store-outage rule
  (section 2, "Timeouts and refresh") instead of signing the user out. Log it at `ERROR`
  ([logging.md](../../python/logging/logging.md) section 4) once per interval. The interval and
  the outage close are this practice's choice.
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
  on the idle clock; count only the messages the user's actions send,** so a page that reconnects
  a dropped socket, or a socket that pings on a timer, does not keep an idle session alive (the
  polling rule in [security.md](../../react/security/security.md) section 6). Section 2 does the
  same for the session check. OWASP's Session Management cheat
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
- **BFF: take every absolute URL the BFF builds, such as the login callback's, the return after
  logout and every redirect, from a setting, and read the `X-Forwarded-*` headers only from the
  proxies a setting names,** since a client sets `Host` and `X-Forwarded-Host`. OWASP's Web
  Security Testing Guide says that, without proper validation of the `Host` value, an attacker can
  make the server "Perform a redirect to an attacker-controlled domain" or "Perform web cache
  poisoning", or put the attacker's host into a password-reset link, and that the same value can
  come through `X-Forwarded-Host` (WSTG-INJT-17) [149]. To check it, send a request with a forged
  `Host`: the URLs stay the same. The rule is this practice's choice.

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
  The header list above already keeps these responses out of caches with `no-store`. A CORS layer
  that overwrote `Vary: Cookie` with `Vary: Origin` could let a CDN serve one user's data to
  another (Netty, CVE-2026-59903, fixed in 4.1.137.Final and 4.2.17.Final) [132].
- **API: on the download route, send `Content-Disposition: attachment` with any file that came
  from outside,** so the browser saves it instead of showing it (MDN on `Content-Disposition`)
  [118]. Shown inline, an HTML or SVG file becomes a page on the API's
  origin. The policy above stops its script, but `default-src` does not cover `form-action` (CSP
  Level 3), so a form in it can still send what the user types to another site from the API's
  address [119]. Without the policy, its script would run where its requests
  are `same-origin` and carry the session cookie past every check in this section.

#### Logging

- **BFF: before the BFF's first release to users, when you set up every alert this file asks for,
  those in section 2 included, write the person or channel that receives security advisories and
  alerts into the decision log ("Write it down" in section 2 says where),** so the recipient is
  known even after people change roles. The rule is this practice's choice. How the recipient
  handles an alert is [sla.md](../../any-language/project-management/sla.md) section 3.
- **BFF: send every alert this file asks for, those in section 2 included, to that recipient,** so
  every alert has a recipient who acts on it, also in a client-rendered application that never
  reads [security.md](../../react/security/security.md) section 8; the rule is this practice's
  choice.
- **BFF: send one test alert to the recipient when you set up the alerts, and another each time the
  recipient changes,** so an alert path is not first tried in an incident; the rule is this
  practice's choice.
- **BFF: make each alert rule this file asks for, those in section 2 included, fire once in a test
  environment by forcing its condition, and again when a log line the rule reads changes,** so an
  alert is not first tried in an incident; the rule is this practice's choice.
- **BFF: on an alert that names a user's `iss` and `sub`, have the recipient also end every session
  of that user through an operator command the team writes down ("Write it down" in section 2 says
  where),** so a session that may be in someone else's hands ends at once. The command calls the
  BFF, which runs the code path of the rule on a disabled account in section 2,
  "Re-authentication", for that one user under its own identity; only a role the team names may run
  it, and it logs who ran it. ASVS 5.0 requirement 7.4.5
  asks that "application administrators are able to terminate active sessions for an individual
  user or for all users" [42]. The command, its role and its log line are this practice's choice.
- **BFF: log at `INFO` ([logging.md](../../python/logging/logging.md) section 4) each request that
  a check rejects and each failed sign-in or re-authentication, with the check's name, the route
  and the `Origin` and `Sec-Fetch-Site` values,** so a CSRF probe, a planted cookie or an origin
  set up wrong leaves a trace. The checks are the custom header, Fetch Metadata, `Origin`, the
  cookie name, a path format and a WebSocket's `Origin`. Each is an expected client error, which
  logging.md section 4 keeps out of `WARNING`; the alert on the rejection rate below is what calls
  a person. OWASP's Logging cheat sheet asks to log authentication, access-control, session and
  input-validation failures, and ASVS 5.0 requirement 16.3.3 asks to log attempts to get past a
  security control [120], [56]. What never goes into a log is
  [logging.md](../../python/logging/logging.md) section 10.
- **BFF: cut each value that a rejected request supplies (the `Origin`, a cookie name, a path) to
  a fixed length before you log it,** so a probe cannot flood the log. OWASP's Logging cheat
  sheet asks to record a validation failure on data from another trust zone "with bounded, safe
  context", and to make sure logging cannot "deplete system resources" [120].
  Where the value goes in the log line, and how the JSON formatter escapes it against log
  injection, is [logging.md](../../python/logging/logging.md) sections 3 and 6. The same holds
  for each field of a report that the report intake writes to a log.
- **BFF: log at `INFO` each sign-in and re-authentication that succeeds, and each new session id,
  with the user's id and the method, never the session id itself,** so an
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
  alerting a team can hardly respond quickly and effectively to an incident [121]. The unknown-key
  reason of a cookie that cannot be read (section 2, "Keys and secrets") counts among those
  rejections.
  The rule is this practice's choice. On an alert for the unknown-key reason, the first check is to
  compare each instance's logged key ids with the store's list: reload an instance that lacks an
  id, and read a burst of ids the store never held as a probe.
- **BFF: alert a person when the key that protects new cookies is older than its written rotation
  period plus a margin the team writes down,** so a rotation job that stopped shows before the key
  reaches the limits of its mode (section 2, "Keys and secrets"). With an identity provider, also
  alert when the "current" client credential, by the time stored with it, is older than its written
  rotation period plus a margin the team writes down, or comes within that margin of its expiry at
  the provider, so a credential is replaced before every refresh fails.
  OWASP's Key Management cheat sheet lists "The monitoring of the re-keying operations" in its
  compromise-recovery plan [54]; the alerts on an old key and on the credential's age and expiry
  are this practice's choice.
- **BFF: alert a person when an old key is still in the store after the time step 3 of the
  rotation (section 2, "Keys and secrets") removes it,** since that shows a job that stopped
  before its clean-up; the rule is this practice's choice.
- **BFF: alert a person when the rotation job has logged no run for longer than one reload
  interval,** since a job that stopped between the write and the check of step 1 (section 2, "Keys
  and secrets") lets a start time pass unchecked; the rule is this practice's choice.
- **BFF: alert a person on every `ERROR` line of the rotation job, and when the job moves the same
  key's start time a second time (section 2, "Keys and secrets"),** since the rate alert on
  `ERROR` lines below can let one such line through, and a key whose start time keeps moving never
  protects a cookie. The rule is this practice's choice.
- **BFF, with an identity provider: alert a person on every step-up whose `iss` or `sub` does not
  match,** for the reason the rule on such a mismatch in section 2, "Re-authentication", gives;
  the rule is this practice's choice.
- **BFF, with an identity provider: alert a person on every back-channel logout that could not
  end its session (section 2, "Logout"), or whose logout token named a key the BFF could not
  refetch because the refetch failed (section 3, "Fetch Metadata and exemptions"),** since
  Back-Channel Logout 1.0 leaves sending the logout request again to the provider (section 2.5)
  [57]. It names nothing the provider does after the BFF's `400` (section 2.8), so the session may
  stay live until its timeouts [57].
  The rule is this practice's choice.
- **BFF, with an identity provider: alert a person when valid back-channel logout tokens that
  match no session pass a rate the team writes down,** since a BFF whose stored `sid` never
  matches leaves live every session the provider ended. Section 2, "Logout", logs each such token
  at `INFO`, the level for what nobody will look at ([logging.md](../../python/logging/logging.md)
  section 4). The rule is this practice's choice.
- **BFF, with an identity provider: alert a person when the share of token revokes that fail at
  logout passes a rate the team writes down ("Write it down" in section 2 says where),** since a
  failed revoke is not retried (section 2, "Logout"), so a wrong revocation endpoint would leave
  every refresh token alive with no other sign. The rule is this practice's choice.
- **BFF, with an identity provider: alert a person each time a resource server's step-up challenge
  names no `acr_values` value on the team's list (section 3, "Forwarding tokens"),** since the
  step-up the page would start cannot meet the challenge, so the user cannot make the change; the
  rule is this practice's choice.
- **BFF: alert a person when the `ERROR` lines this file asks for pass a rate the team writes down
  ("Write it down" in section 2 says where),** since [logging.md](../../python/logging/logging.md)
  section 4 keeps `ERROR` for an operation that failed for good and needs a person to act. Only an
  alert calls that person. The alert covers at least the lines for a session store or a list of
  ended sessions that cannot be read, for refreshes that fail with `502`, for a refresh lock that
  fails, for an instance that passes its stale-list limit, for a failed code exchange and for a
  session cookie refused for its size. The rule is this practice's choice.

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
| `Access-Control-Allow-Origin` | the application's one origin, `https://app.example.com`, on every response the browser can get from the API's host, including one from a gateway or proxy in front of it | with credentials the browser refuses `*`, and one fixed origin needs no `Origin` in `Vary` for CORS (the Fetch standard; the `Vary` rule of "Response headers") [93]. Without it, or without the next row's header, the page sees a network error instead of the status, so a `401` from a gateway never reaches the sign-out path (MDN's CORS errors page) [123] |
| `Access-Control-Allow-Credentials` | `true`, on the same responses as the row above, the gateway's included | without it, the browser hides from the page any answer to a request that carried the cookie, a gateway's `401` included (the Fetch standard) [93] |
| `Access-Control-Allow-Methods` | the methods the API serves other than `GET`, `HEAD` and `POST`, such as `PUT`, `PATCH`, `DELETE`; leave the header out when it serves none | the browser lets `GET`, `HEAD` and `POST` past the preflight without the header, and with credentials `*` is a literal name, not a wildcard (the Fetch standard) [93]. Listing the rest keeps the policy to what is used |
| `Access-Control-Allow-Headers` | `Content-Type, X-Requested-With`, and the header that carries the framework's CSRF token, where the server issues one | the JSON body and the custom header start the preflight (MDN) [124]. The same `*` rule holds (the Fetch standard) [93] |
| `Access-Control-Max-Age` | `7200` | the browser caches a preflight answer per URL, for 5 seconds without this header; with it, repeat calls to the same URL skip the preflight, but every new URL (each record id, each query string) still waits for one (the Fetch standard) [93]. Chromium caps the value at 7200, Firefox at 86400 (MDN) [125] |
| `Access-Control-Expose-Headers` | only the response headers the page reads, often none | each listed header becomes readable by scripts on the allowed origin (MDN) [126] |

- **API: with more than one allowed origin, compare the request's `Origin` byte for byte with each
  entry of the list, and copy it back only on a match; never match by suffix, prefix, substring or
  regular expression.** Write each entry as the browser sends it (scheme, host and port, no
  trailing slash). ASVS 5.0 requirement 3.4.2 asks that `Access-Control-Allow-Origin` be "a fixed
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
- **API: answer the preflight with `204` and the CORS headers, without the session and without the
  custom-header check; the preflight handler changes nothing.** A preflight `OPTIONS` request
  never carries the cookie, and it names the custom header in `Access-Control-Request-Headers`
  instead of sending it (the Fetch standard) [93]. So an `OPTIONS` route behind the session check
  or the header check fails every request it should allow. The
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
the API sends that one origin on every response (the header table above). So the browser lets no
page on a sibling subdomain, such as `evil.example.com`, read an answer sent with the user's
cookie, even where no other check stops the request, as in a browser that sends no Fetch
Metadata [93]. Why the other lines hold is in the same table.

### Fixing a CORS error

- **Fix a CORS error on the server, or behind a proxy you run; never in the page.** MDN says "Most
  CORS errors can only be resolved on the server" [123]. What the page must not do is
  [security.md](../../react/security/security.md) section 7, "Fixing a CORS error".
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
what a yes must do. It also names the part of the BFF the question is about, and what a no means.
A no means `wrap` when a hook or a check outside that part can hold the rule, and `replace` when
the rule sits in the part's core, such as cookie protection and its key format, the store's atomic
save, the cookie parser or the router's path handling.

| Problem | Part | Ask of the library or framework | A no means | The rule it checks |
|---|---|---|---|---|
| a script or a sibling subdomain reads or plants the session cookie | HTTP server | Can you name the session cookie `__Host-Http-session`, and does the library write `Secure`, `HttpOnly`, `Path=/` and `SameSite` itself, with no `Domain`? Test it: sign in and read the raw `Set-Cookie` line of the session cookie. | replace | [section 2, "The session cookie"](#the-session-cookie) |
| the browser's default `SameSite` applies | HTTP server | Does it always write `SameSite`, and let you choose `Strict` or `Lax` for each cookie? | wrap | [section 2, "The session cookie"](#the-session-cookie) |
| `Secure` is off in production | HTTP server | Does it keep `Secure` on in every environment, with no setting that turns it off? | wrap | [section 2, "The session cookie"](#the-session-cookie) |
| the session outlives the browser | HTTP server | Is the session cookie non-persistent by default? | wrap | [section 2, "The session cookie"](#the-session-cookie) |
| a sibling subdomain plants the login cookie | OpenID Connect client | With an identity provider, can its login cookie, the `state`, correlation or nonce cookie, take the `__Host-Http-` prefix with `Secure`, `HttpOnly`, `Path=/` and no `Domain`? Test it: start a login and read the raw `Set-Cookie` line of the login cookie. | replace | [section 2, "The login cookie"](#the-login-cookie), rule "give the short-lived login cookie" |
| a login in a second tab breaks the first one's callback | OpenID Connect client | With an identity provider, does it keep each login attempt in a cookie of its own? | wrap | [section 2, "The login cookie"](#the-login-cookie), rule "name the login cookie per attempt" |
| the user edits or reads what a login attempt records | OpenID Connect client | With an identity provider, does it keep the `state`, nonce and PKCE verifier encrypted and signed, in the login cookie or in `state`, and never in a record on the server? | wrap | [section 2, "The login cookie"](#the-login-cookie), rule "keep what a login attempt records" |
| guessable login values | OpenID Connect client | With an identity provider, does it draw the `state`, nonce and verifier from a secure random source for every attempt, with a 256-bit verifier and `S256`? | replace | [section 2, "The login cookie"](#the-login-cookie), rule "where the library leaves it to your own code" |
| login cookies left behind | OpenID Connect client | With an identity provider, does it delete the login cookie at every callback, a callback that carries an error included? | wrap | [section 2, "The login cookie"](#the-login-cookie), rule "give the login cookie a `Max-Age`" |
| login cookies pile up until requests fail | OpenID Connect client | With an identity provider, does it cap the login cookies a browser holds, or give you a hook at the login start to expire the extra ones? | wrap | [section 2, "The login cookie"](#the-login-cookie), rule "then expire every other login cookie" |
| a login cookie lives on | OpenID Connect client | With an identity provider, is the login cookie's lifetime bounded by default, and can you set it? | wrap | [section 2, "The login cookie"](#the-login-cookie), rule "give the login cookie a `Max-Age`" |
| an unreadable login cookie ends in an error | OpenID Connect client | With an identity provider, does it treat a login cookie it cannot read as missing, and log the reason, instead of throwing? | wrap | [section 2, "The login cookie"](#the-login-cookie), rule "at a callback whose login cookie is missing" |
| the error page shows a request value | OpenID Connect client | With an identity provider, can you replace its answer to a failed callback with a fixed error page of your own? | wrap | [section 2, "The login cookie"](#the-login-cookie), rule "give the error page that a failed login callback answers" |
| a `form_post` callback arrives without its cookie | OpenID Connect client | With an identity provider, does it set the login cookie's `SameSite` to fit `response_mode`, and let you change it? | wrap | [section 2, "The login cookie"](#the-login-cookie), rule "set the login cookie's `SameSite`" |
| an image or a frame on another site starts a login | OpenID Connect client | With an identity provider, can your own check, such as the `Sec-Fetch-Dest` refusal, run before its login endpoint sets the login cookie? | wrap | [section 2, "The login cookie"](#the-login-cookie), rule "refuse a login start whose `Sec-Fetch-Dest`" |
| a link through the real sign-in lands the user on another site | OpenID Connect client | With an identity provider, does it take the page to return to only as a local path or as an id it maps on the server, and send the callback's redirect only there? | wrap | [section 2, "The login cookie"](#the-login-cookie), rule "at the login start, take the page to return to" |
| a mix-up between identity providers | OpenID Connect client | With more than one identity provider, does it record the issuer of each attempt and check the `iss` of RFC 9207, or give each provider a callback path of its own? | wrap | [section 2, "The login cookie"](#the-login-cookie), rule "record in the attempt's protected record the issuer" |
| a `Cookie` header split into several lines | HTTP server | Does the server join every `Cookie` field line with `; ` before it parses them? Test it: over HTTP/2, send the session cookie in a second `Cookie` field line, and expect the session to be found. | replace | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| two cookies with one name | HTTP server | Does the parser give you every value of a repeated name, or the raw header, instead of keeping one of them without telling you? Test it: send the session cookie's name twice with two values, and check that your code gets both values or the raw header. | replace | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| a planted cookie read under the real name | HTTP server | Does the parser match cookie names byte for byte, with no trimming, case folding or URL-decoding? Test it: send a live session's value under `__HOST-HTTP-SESSION`, under the name with a leading U+2000, and under `__Host%2DHttp-session`, and expect none of them read as the session. | replace | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| one cookie string read as several | HTTP server | Is the server's legacy cookie parser, the RFC 2109 or RFC 2965 mode with `$Version` or commas, off by default, and can you keep it off? | replace | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| the session cookie's value read through the framework's parser | HTTP server | Can your code read the session cookie's value from the raw `Cookie` header? | replace | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| a planted cookie locks the user out | HTTP server | Can you add a header, such as `Clear-Site-Data`, to the library's own error answers? | wrap | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| known bugs in cookie parsing | HTTP server | Does the project publish advisories, and fix cookie-parsing bugs in the versions it supports? | replace | [section 2, "Reading the `Cookie` header"](#reading-the-cookie-header) |
| the session check leaks a token or keeps a session alive | HTTP server | Does its user endpoint answer `401` with no session, return no token, send `Cache-Control: no-store`, and leave the idle clock alone? | wrap | [section 2, "The session's life, from login to logout"](#the-sessions-life-from-login-to-logout) |
| one instance cannot read another's sessions | session store | With the session's state on the server, does it keep the sessions in a store that every instance reads? Test it: sign in through one instance, send the session check to another by its own address, and expect `200`. | replace | [section 2, "The session's life, from login to logout"](#the-sessions-life-from-login-to-logout) |
| a cookie too large for the browser to store | cookie protection | With the session's state in the cookie, does it refuse to set a cookie over 4096 bytes, and tell you? | wrap | [section 2, "The session's life, from login to logout"](#the-sessions-life-from-login-to-logout) |
| a copy of the session store | session store | With the session's state on the server, can access to the session store be limited to the BFF's own identity, with its backups encrypted? | replace | [section 2, "The session's life, from login to logout"](#the-sessions-life-from-login-to-logout) |
| a reader of the session store gets every user's tokens | session store | With the session's state on the server and a reader of the store in your threat model, does it encrypt the tokens in each session record with authenticated encryption, under a key it loads from the secret store? | wrap | [section 2, "The session's life, from login to logout"](#the-sessions-life-from-login-to-logout), rule "in the same threat model, encrypt the tokens" |
| a key in the code | cookie protection | Does it load the client credential and the cookie keys from a secret store, never from the code or a config file? | wrap | [section 2, "Keys and secrets"](#keys-and-secrets) |
| a guessable key | cookie protection | Does it generate keys from a CSPRNG, never from a password a person types? | wrap | [section 2, "Keys and secrets"](#keys-and-secrets) |
| a homemade cipher | cookie protection | With the session's state in the cookie, does it protect cookies with authenticated encryption from a vetted library? | replace | [section 2, "Keys and secrets"](#keys-and-secrets) |
| one key for every cookie | cookie protection | Does it use a separate key, or a subkey derived with a fixed purpose label, for each cookie and each session record it protects, and separate keys in each environment? | replace | [section 2, "Keys and secrets"](#keys-and-secrets) |
| instances that hold different keys | cookie protection | Does every instance load the same set of keys from one store? | wrap | [section 2, "Keys and secrets"](#keys-and-secrets) |
| an outage of the key store signs users out | cookie protection | When the key store cannot be read, does it keep the key list it loaded, and let the instance report not ready once that list is older than a limit you set? | wrap | [section 2, "Keys and secrets"](#keys-and-secrets), rule "when an instance cannot read the key store" |
| rotation by trial over every key | cookie protection | Does each protected cookie carry a format version and the id of its key? | replace | [section 2, "Keys and secrets"](#keys-and-secrets) |
| a rotation signs users out | cookie protection | Does it protect with a new key only from a start time, or from an explicit step, that you control, and keep reading with an old key until the cookies it protected expire? | wrap | [section 2, "Keys and secrets"](#keys-and-secrets) |
| a leaked key keeps working | cookie protection | Can you remove a key from the store and make every instance reload its key list? | wrap | [section 2, "Keys and secrets"](#keys-and-secrets) |
| an unreadable cookie answers `500` | cookie protection | Does it treat a cookie it cannot read as no session, and give the reason for the log? | wrap | [section 2, "Keys and secrets"](#keys-and-secrets) |
| an instance writes a key of its own | cookie protection | Can you keep every instance from generating or writing a key, so it only reads the keys the rotation job writes? | wrap | [section 2, "Keys and secrets"](#keys-and-secrets), rules "let the BFF's own identity only read" and "when an instance starts and finds no key" |
| the rotation check has nothing to read | cookie protection | Does it tell your code, at each reload of the key list, which key ids the instance loaded, so the instance can log them? | wrap | [section 2, "Keys and secrets"](#keys-and-secrets), rule "have an instance re-read the key list" |
| a client-credential rotation needs a restart | OpenID Connect client | With an identity provider, can it switch its client credential between "current" and "next" while it runs, with no restart? | wrap | [section 2, "Keys and secrets"](#keys-and-secrets), rule "rotate the client credential so that one credential works" |
| a cookie name or format change signs every user out | cookie protection | Can it read a cookie under its old name and format, and re-issue it under the new ones, for a time you set? | wrap | [section 2, "The session cookie"](#the-session-cookie), rule "when a BFF that already has users renames its session cookie" |
| session fixation | session store | Does it issue a new session id at login and at every re-authentication, and destroy the old session? | wrap | [section 2, "A new session id at login"](#a-new-session-id-at-login) |
| a failed destroy of the old session passes in silence | session store | With an identity provider, does a failed destroy of the old session stop the login? | wrap | [section 2, "A new session id at login"](#a-new-session-id-at-login) |
| a session id the attacker chose | session store | With the session's state on the server, does it refuse a session id it never created? Test it: send a session cookie with an id the store never held, and expect no session and no record under that id. | replace | [section 2, "A new session id at login"](#a-new-session-id-at-login) |
| a guessable session id | session store | Does it draw session ids from a CSPRNG, with at least 128 bits? | replace | [section 2, "A new session id at login"](#a-new-session-id-at-login) |
| a session that never times out | session store | Does it enforce an idle and an absolute timeout on the server, and does the absolute one survive a sliding renewal? | wrap | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| timeout values nobody can find | session store | Are both timeout values settings, not constants in the code? | wrap | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| the provider signs the user in again without asking | OpenID Connect client | With an identity provider, where the timeouts must make the user sign in again, can it send `max_age` on a chosen login, and check `auth_time` at the callback? | replace | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| one wrong setting signs every user out | OpenID Connect client | With an identity provider, does it give you the token endpoint's error code, so you can end the session on `invalid_grant` and keep it on a setup error or an outage? | replace | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| a refresh answer without a refresh token | OpenID Connect client | With an identity provider, does it keep the old refresh token when a refresh answer carries none? | wrap | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| parallel refreshes count as reuse | OpenID Connect client | When the provider rotates the BFF's refresh tokens, has no reuse window that covers the requests in flight, and the session's state is on the server, can it run one refresh per session at a time across instances, with a timeout on the token call and an expiry on its lock, and let only the lock's holder release it? Test it: send parallel requests with an expired access token, against a stub token endpoint that rotates refresh tokens and counts the calls, and expect one refresh call and every request served. | wrap | [section 2, "Timeouts and refresh"](#timeouts-and-refresh), rules "hold that one refresh with a lock" and "give the call to the token endpoint" |
| a waiting request refreshes with a rotated refresh token | OpenID Connect client | When the provider rotates the BFF's refresh tokens, has no reuse window that covers the requests in flight, and the session's state is on the server, does it read the session again after it takes the lock, and store the new tokens before it releases the lock? Test it: send parallel requests with an expired access token, against a stub token endpoint that rotates refresh tokens and counts the calls, and expect every request that waited to make no token call and to use the access token the holder stored; then have the stub return an access token that has already expired, and expect the next refresh to send the newest refresh token, never a rotated one. | wrap | [section 2, "Timeouts and refresh"](#timeouts-and-refresh), rules "after taking the lock, read the session's tokens again" and "store the new tokens before you release the lock" |
| an abandoned request leaves a rotated refresh token stored | OpenID Connect client | When the provider rotates the BFF's refresh tokens, has no reuse window that covers the requests in flight, and the session's state is on the server, does it run the token call and the store of its answer to their timeout when the browser abandons the request? Test it: send parallel requests with an expired access token, against a stub token endpoint that rotates refresh tokens and counts the calls, abandon the request whose refresh runs, and expect the stored refresh token to stay usable. | wrap | [section 2, "Timeouts and refresh"](#timeouts-and-refresh), rule "store the new tokens before you release the lock" |
| an outage lets a copied cookie through | session store | When the session store or the list of ended sessions cannot be read, does it fail with an error, rather than sign the user out or accept the cookie? Test it: make the store unreachable, send a request with a live cookie, and expect `503`. | replace | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| a timed-out session keeps its tokens at rest | session store | With the session's state on the server, does its store delete a session's record when a timeout ends the session? | wrap | [section 2, "Timeouts and refresh"](#timeouts-and-refresh) |
| an evicted or lost entry lets a logged-out cookie work again | session store | Can it keep the list of ended sessions, the per-user times, the single-use marks, the step-up guess counts and the refresh locks until their own expiry, never evicting them, and keep them through a restart? A yes may come from a setting: name the setting. Test it: write an entry, restart the store, read it; and read the store's eviction setting. | replace | [section 2, "Timeouts and refresh"](#timeouts-and-refresh), rule "keep the list of ended sessions" |
| the session records a leaked key encrypted cannot be found | session store | With the tokens encrypted in session records, can it list the records that start with a given key id? | replace | [section 2, "Keys and secrets"](#keys-and-secrets), rule "when you suspect that a cookie key leaked" |
| a logout that only deletes the cookie | session store | With the session's state on the server, does logout delete the session on the server? | wrap | [section 2, "Logout"](#logout) |
| a second tab is told that its sign-out failed | HTTP server | Does logout answer with success also when no session exists? | wrap | [section 2, "Logout"](#logout), rule "answer the logout request with success" |
| a request still running restores the session | session store | With the session's state on the server, does the store refuse to save a session that ended after the request loaded it? Test it: start a slow request, log out while it runs, then let it finish; this shows only the failure of a save at the end of the request. For a store whose save checks first and writes after, read its save code and accept only one atomic update that fails when the record is gone, or a test that holds the logout between the check and the write: Django ticket 37249 says the slow-request flow "was tested and is not sufficient" to restore a session in its cache and file stores, which a logout between the check and the write does restore [70]. | replace | [section 2, "Logout"](#logout) |
| a copied cookie works after logout | cookie protection | With the session's state in the cookie, does it keep one session id across re-issued cookies, and check a list of ended sessions and a per-user time on every request? | wrap | [section 2, "Logout"](#logout) |
| tokens outlive the logout | OpenID Connect client | With an identity provider, does logout revoke the refresh token, and still end the session when the revoke fails? | wrap | [section 2, "Logout"](#logout) |
| a token in the provider's logout URL | OpenID Connect client | Where the user should also leave the identity provider, does it build the provider's logout URL from `end_session_endpoint`, and let you leave out `id_token_hint`? | wrap | [section 2, "Logout"](#logout) |
| a forged logout token | OpenID Connect client | With an identity provider, does its back-channel logout run every check of Back-Channel Logout 1.0 section 2.6, offer the `logout+jwt` type check, and end every session of the user that started before the token's `iat` for a token with no `sid`? | wrap | [section 2, "Logout"](#logout) |
| a back-channel logout that fails in silence | OpenID Connect client | With an identity provider, does it answer `400` when it cannot end the session, `200` when no session matches, and give you a hook to log and alert? | wrap | [section 2, "Logout"](#logout) |
| the provider's logout never reaches the BFF | OpenID Connect client | With an identity provider, is back-channel logout its default, not front-channel logout? | wrap | [section 2, "Logout"](#logout) |
| the old cookie stays in the browser | HTTP server | Does logout send `Max-Age=0` with every attribute the prefix needs? | wrap | [section 2, "Logout"](#logout) |
| a logout signs the user out of other applications | HTTP server | Does it leave `Clear-Site-Data: "cookies"` off by default, or let you turn it off? | wrap | [section 2, "Logout"](#logout) |
| a scan of every session to find one user's | session store | With the session's state on the server, can its session store find every session of one user, and of one `sid`, in one lookup? | replace | [section 2, "Re-authentication"](#re-authentication), rule "index each session by its user" |
| an old sign-in passes a step-up | OpenID Connect client | With an identity provider, can its login start take `max_age=0` and `acr_values` for each request, and does its callback give you the new ID token's `auth_time` and `acr`? | replace | [section 2, "Re-authentication"](#re-authentication), rules "treat a login start that carries a live session" and "at a step-up's callback, accept the re-authentication" |
| a thief steps up as another user | OpenID Connect client | With an identity provider, can the callback compare the new ID token's `iss` and `sub` with the session's, and refuse, before it issues a session? | wrap | [section 2, "Re-authentication"](#re-authentication), rule "at a step-up's callback, accept the re-authentication" |
| one step-up lets every change through | session store | With an identity provider, can a route ask for a re-authentication younger than a window you set, and consume it in one atomic store write before the change, with the session's state on the server or in the cookie? Test it: after one step-up, send two guarded changes at once, and expect only one to pass. | replace | [section 2, "Re-authentication"](#re-authentication), rule "let a guarded change through only while" |
| a step-up keeps the old timeouts | session store | Does a successful step-up start the idle and absolute timeouts again? | wrap | [section 2, "Re-authentication"](#re-authentication), rules "complete a step-up at its callback in this order" and "once the answer passes the check" |
| a step-up's callback sends the user to any URL | OpenID Connect client | With an identity provider, does a step-up's callback send the user back only to a fixed route of the page, never to a URL taken from the request? | wrap | [section 2, "Re-authentication"](#re-authentication), rule "answer a step-up's callback whose login cookie matches" |
| a first-party step-up asks for less than the sign-in | HTTP server | With a first-party login, does its step-up ask for every factor the account signs in with, the password and the second factor where the account has one? | wrap | [section 2, "Re-authentication"](#re-authentication), rule "before a guarded change, ask again for every factor" |
| one answer covers more than one change | HTTP server | With a first-party login, does it check the answer inside the guarded request itself, not only through a "recently signed in" window? | wrap | [section 2, "Re-authentication"](#re-authentication), rule "take the answer only with the guarded request" |
| a thief answers with their own password | HTTP server | With a first-party login, does it check the answer against the session's own user? | wrap | [section 2, "Re-authentication"](#re-authentication), rule "check the answer against the user of the session" |
| password guessing through the step-up | session store | With a first-party login, does it count step-up answers with an atomic operation of the store, and add a wrong one to the account's own failure count? Test it: send as many wrong answers at once as the limit allows, and expect the session to end. | replace | [section 2, "Re-authentication"](#re-authentication), rules "count every answer to a step-up per session" and "check a step-up's answer with the same verifier" |
| an honest user loses the session after old mistakes | session store | With a first-party login, does it clear that count after a successful step-up? | wrap | [section 2, "Re-authentication"](#re-authentication), rule "start that count again at zero" |
| the page signs out when a step-up is due | HTTP server | Can its re-authentication challenge come back as a `403` with a fixed code, not as a redirect or a `401`? | wrap | [section 2, "Re-authentication"](#re-authentication), rule "ask the page for re-authentication with a `403`" |
| a step-up brings back a session that just ended | session store | With a first-party login, at a re-authentication, does it move the session to a new id, and refuse to move a session that ended during the request? | replace | [section 2, "Re-authentication"](#re-authentication), rule "once the answer passes the check" |
| other sessions live on after a factor change | session store | With a first-party login, can it end every other session of a user, and report a failed end? | wrap | [section 2, "Re-authentication"](#re-authentication), rule "when the user accepts, destroy every other session" |
| a disabled account keeps its sessions | session store | Can it end every session of a user and, with the session's state in the cookie, reject cookies issued before a per-user time? | wrap | [section 2, "Re-authentication"](#re-authentication), rule "when an account is disabled or deleted" |
| the access token goes to any host | router or HTTP client | With an identity provider, does its proxy forward only to configured routes, with each route's methods and path checks? | wrap | [section 2, "Forwarding to resource servers"](#forwarding-to-resource-servers) |
| the session cookie reaches a resource server | router or HTTP client | With an identity provider, does it drop `Cookie` and the inbound `Authorization` header by default? | wrap | [section 2, "Forwarding to resource servers"](#forwarding-to-resource-servers) |
| a resource server plants a cookie through the BFF | router or HTTP client | With an identity provider, does its proxy pass on only the response headers you allow, and drop `Set-Cookie` and every `Access-Control-*` header by default? | wrap | [section 2, "Forwarding to resource servers"](#forwarding-to-resource-servers) |
| one token for every resource server | OpenID Connect client | With an identity provider, when it forwards to more than one resource server, can it hold a separate access token for each, and attach the right one? | wrap | [section 2, "Forwarding to resource servers"](#forwarding-to-resource-servers) |
| a resource server's redirect takes the token to another host | router or HTTP client | With an identity provider, does its HTTP client leave a resource server's `3xx` unfollowed, or let you turn following off? | wrap | [section 2, "Forwarding to resource servers"](#forwarding-to-resource-servers) |
| an expired or rejected access token | router or HTTP client | With an identity provider, does it refresh an expired access token before it forwards, and retry once after a resource server's `401`? | wrap | [section 3, "Forwarding tokens"](#forwarding-tokens) |
| a step-up challenge read as an expired token | router or HTTP client | With an identity provider, does it treat a resource server's `insufficient_user_authentication` as a step-up, not a refresh, and read the challenge's `acr_values`? | wrap | [section 3, "Forwarding tokens"](#forwarding-tokens) |
| a sibling subdomain passes the CSRF check | HTTP server | Does it treat a `same-site` request as untrusted unless its `Origin` equals a configured full origin, on reads too? | wrap | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| a request with no Fetch Metadata | HTTP server | When `Sec-Fetch-Site` is absent, does it compare `Origin` exactly, and let you reject a request with neither header on the routes you choose? | wrap | [section 3, "CSRF"](#csrf) |
| an exemption wider than one route | HTTP server | Can it require one fixed header on every API route, and exempt routes only by exact path and method? | wrap | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| a refused request read as an ended session | HTTP server | Does a failed check answer `403`, and an API call without a session `401`? | wrap | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| a new check refuses real users from the first deploy | HTTP server | Does it have a log-only mode that logs `Origin`, `Sec-Fetch-Site` and `User-Agent`? | wrap | [section 3, "CSRF"](#csrf) |
| a forged request reaches the session lookup | HTTP server | Can the custom-header and Fetch Metadata checks run before its session lookup and any other work on the request? | wrap | [section 3, "CSRF"](#csrf), rule "runs the custom-header and Fetch Metadata checks first" |
| framework actions open to CSRF | HTTP server | With Server Functions or route actions, does the framework's own `Origin` check run on every unsafe method, and can each call carry the custom header, or your own guard reject a request with neither `Sec-Fetch-Site` nor `Origin`? | wrap | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| three lists of allowed origins drift apart | HTTP server | Can the CSRF, CORS and WebSocket checks read one setting of allowed origins? | wrap | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| an anonymous route floods | HTTP server | Can it limit the size and the rate of one anonymous route on its own? | wrap | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| logout tokens with made-up key ids make the BFF call the provider each time | OpenID Connect client | With an identity provider, does its back-channel logout refetch the provider's keys at most once per interval you set when a token names a key id it does not hold? | wrap | [section 3, "Fetch Metadata and exemptions"](#fetch-metadata-and-exemptions) |
| CORS lets any origin read the answers | CORS layer | Does its CORS layer compare origins against an exact list, refuse, not copy back, any origin with credentials, and offer no switch that allows every subdomain? | wrap | [section 3, "CORS"](#cors) |
| a CORS layer overwrites `Vary` or reflects headers | CORS layer | Does it add `Origin` to `Vary` instead of replacing the header, and take a fixed list of allowed headers instead of copying `Access-Control-Request-Headers`? | wrap | [section 3, "Response headers"](#response-headers) |
| the preflight fails | CORS layer | Does it answer the preflight with a `2xx` before authentication runs? | wrap | [section 3, "CORS"](#cors) |
| cross-site WebSocket hijacking | WebSocket server | Does its WebSocket server check `Origin` against an exact list by default, and refuse other origins with `403`? | wrap | [section 3, "WebSocket"](#websocket) |
| a socket outlives its session | WebSocket server | Does it close a session's sockets when the session ends or gets a new id, on every instance? | wrap | [section 3, "WebSocket"](#websocket) |
| the page cannot tell an ended session from a dropped socket | WebSocket server | Can you choose the close code it uses when the session ends? | replace | [section 3, "WebSocket"](#websocket) |
| sockets keep an idle session alive | WebSocket server | Can you leave the handshake and keep-alive messages off the idle clock? | wrap | [section 3, "WebSocket"](#websocket) |
| a socket checks an old copy of the cookie | WebSocket server | With the session's state in the cookie, does its periodic check read the list of ended sessions, not only the cookie the handshake carried? | wrap | [section 3, "WebSocket"](#websocket) |
| a WebSocket message skips the checks of an HTTP request | WebSocket server | Does it let you authorise each message that asks for an action, as you would the same request over HTTP? | wrap | [section 3, "WebSocket"](#websocket), rule "authorise each WebSocket message" |
| path traversal through an encoded segment | router or HTTP client | Does the router route on the path as sent, without resolving `%2e%2e` or decoding `%2F` first? Test it: send `/orders/%2e%2e/x`, and expect the orders route's refusal, never the answer of `/x`. | replace | [section 3, "Paths and proxies"](#paths-and-proxies) |
| a path decoded twice | router or HTTP client | Does its HTTP client encode each segment it inserts exactly once, and pass the inbound path on without decoding it? Test it: forward a segment that holds `a/b`, and expect the resource server to receive `a%2Fb`. | replace | [section 3, "Paths and proxies"](#paths-and-proxies) |
| a callback or redirect URL built from a forged `Host` | HTTP server | Can you set every absolute URL it builds, such as the login callback's and the return after logout, from a setting, and have it read the `X-Forwarded-*` headers only from the proxies you name? Test it: send a request with a forged `Host`, and expect the same callback and redirect URLs. | wrap | [section 3, "Paths and proxies"](#paths-and-proxies), rule "take every absolute URL the BFF builds" |
| a body run as a page, or kept in a cache | HTTP server | Does it set `Cache-Control: no-store`, `nosniff` and the policy on every API response, error answers included? | wrap | [section 3, "Response headers"](#response-headers) |
| a file shown on the API's origin | HTTP server | Does its file helper send `Content-Disposition: attachment` by default? | wrap | [section 3, "Response headers"](#response-headers) |
| a probe floods the log | logger | Does the logger cap the length of values taken from requests, and escape line breaks in them? | wrap | [section 3, "Logging"](#logging) |
| security events missing from the log | logger | Can it log each rejected check and each failed sign-in without the cookie's value or a token? | wrap | [section 3, "Logging"](#logging) |

Compare candidates on the `replace` rows first: a no there means the team replaces that part of
the library, or picks another one. For the OpenID Connect client, replacing the part means
picking another library or SDK, since the rule on a maintained OpenID Connect library (section 2,
"The login cookie") bans writing the flow yourself; your own code there is only the bookkeeping
that rule leaves to it. Count each `wrap` answer as code the team will own: a hook or a
check of its own around the part, as the rule says. The login-cookie and key rules of section 2 are
checks on the library, with code of your own only for a rule it does not meet. A row whose
condition your BFF does not meet does not apply. Answer each row from the library's code or from a
test against the version you pick, never from its docs. A row with several parts is a yes only
when every part is, and a no names the part that failed; a row you could not check counts as a
no. Rerun every row that has a test against the version you pick, and again each time the library
is updated: keep those tests in the BFF's own test suite, so CI runs them on each library update.
A row answered from the library's code is read again at each library update, and its answer notes
the file and the function it was read from. That reading again, and the tests on the three rows
on a refresh race, are this practice's choice. The logout race's test shows only a save at the
end of the request, so its row also asks for the store's save code.

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
  that end (section 2, "Logout"). A renewal timeout would end a copy sooner; section 2, "Timeouts
  and refresh", says why this practice does not take it. OWASP's Session Management cheat sheet
  calls it "highly recommended to bind the session ID to other user or client properties, such as
  the client IP address, User-Agent, or client-based digital certificate" [8]. But its same section
  says these properties "cannot be used by web applications to trustingly defend against session
  attacks", since an attacker on the same network or behind the same proxy shares the IP address
  and can copy the User-Agent [8]. This practice does not take the binding as a control for that
  reason.
- **With the session's state in the cookie and a provider that rotates refresh tokens, a refresh
  whose answer never reaches the browser,** such as one for a cancelled query or a dropped
  connection, loses its `Set-Cookie`. The browser keeps the old refresh token. When its next
  request comes after the provider's reuse window, the provider counts it as reuse, revokes the
  active refresh token and the user is signed out (section 2, "Timeouts and refresh"; RFC 9700
  section 4.14.2) [16]. A request still in flight with the old cookie has the same effect when it
  re-issues that cookie, because its last-use time moved past the written step, and its answer
  arrives after the refresh's: the browser keeps the old refresh token.
- **A cookie key that leaked gives its holder what the cookies it protected hold, after the key is
  replaced.** The leaked-key plan counts as leaked every key that sat where the leaked key sat
  (section 2, "Keys and secrets"), so what follows holds for each of them. With the session's
  state in the cookie, whoever held the leaked key and a copy of a
  cookie keeps the access token in it, valid at its resource servers until it expires, which the
  short access-token lifetime bounds (section 2, "Logout"). They keep the refresh token only while
  the client credential is unchanged, since RFC 6749 section 10.4 binds a refresh token to its
  client [15]. With the session's state on the server, the key protects only login cookies, which
  hold no OAuth token, and a session cookie that the framework signs, which holds only the session
  id. The record of a login or a step-up started from a live session holds that
  session's id, and with the state on the server that id is the session: whoever holds the key and
  a copy of such a cookie, or of a `state` that carries the record, can use that session until it
  ends. The callback ends it, so only an attempt that never reached its callback leaves it live,
  and the seven steps of the leaked-key plan (section 2, "Keys and secrets") do not end it.
- **Whoever reads the session store and also holds the key that encrypts its tokens** reads every
  user's tokens: the access tokens work at their resource servers until they expire, and the
  refresh tokens only with the client credential, and only until the leaked-key plan revokes them
  (section 2, "The session's life, from login to logout" and "Keys and secrets").
- **Whoever can write the key store can plant a key that every instance accepts within one reload
  interval;** the limit on who writes the store and the alert on a write by another identity are
  the controls (section 2, "Keys and secrets").
- **Where the platform gives no list of instances, or no log line per instance, the rotation job
  cannot check that every instance loaded a new key before its start time passes;** the start
  margin of the rotation's step 1 and the stale-list limit are then the only controls (section 2,
  "Keys and secrets"). There, step 3 of the rotation removes the old key on its time condition
  alone, and step 5 of the client-credential rotation removes the old credential once the
  stale-list limit plus one reload interval has passed since its step 4. By then every instance
  has reloaded or reports not ready; both removals on time are this practice's choice.
- **A back-channel logout that the BFF cannot carry out,** because its session store cannot be
  written, can leave the session live until its timeouts; only the `ERROR` line of section 2 and
  its alert (section 3, "Logging") show it. A genuine logout token that the BFF refuses during a
  flood, because the interval refused the refetch of the provider's keys (section 3, "Fetch
  Metadata and exemptions"), is dropped too. Back-Channel Logout 1.0 section 2.5 has the
  provider send a logout request again only after an error it may recover from, such as a network
  outage: "In all other cases, the OP SHOULD NOT retransmit" [57]. Only its `WARNING` line shows
  it, and the session lives until its timeouts.
- **With the session's state in the cookie, a back-channel logout cannot revoke the session's
  refresh token,** since the token sits only in the user's cookie, which the provider's logout
  request does not carry; the token lives on until it expires, of no use without the BFF's client
  credential (section 2, "Logout").
- **A step-up from another account whose recorded session cannot be ended,** because the session
  store cannot be written, leaves that session live, perhaps in someone else's hands, until the
  person the alert reaches ends it or its timeouts do (section 2, "Re-authentication").
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
- **A forged cross-site request acts as the user where it gets past the checks that remain:** in a
  browser that sends no Fetch Metadata, only the custom header and the `Origin` check stop it
  (section 3, "CSRF"), and an allowed origin is as safe as its weakest page (section 3, "CORS").
  A request that gets past them changes the user's data with the user's cookie, and one sent from
  an allowed origin also reads the answers.
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
  cannot tell from the real cookie, so a sibling host can sign the victim in as the attacker, or
  plant a login record. The RFC 6265bis draft, in step 22 of section 5.7, asks browsers to ignore
  a cookie whose name is empty and whose value begins with `__Host-`, and Firefox fixed it in
  Mozilla bug 1779993 [2], [140]. Which other browsers ignore it was not checked; test each browser
  the team supports: from a sibling host, set
  `=__Host-Http-x=1; Domain=<registrable domain>; Secure; Path=/`, then read the `Cookie` header
  the API receives. Where a browser fails the test, HSTS and control of every subdomain are the
  only controls.
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
- **Pages the server renders take a `Lax` session cookie, not `Strict`** (section 2, "The session
  cookie").
- **A first-party login's credential checks, such as password storage and login throttling, are
  outside this practice** (section 1).
- **A team at ASVS Level 1, or one whose identity provider asks for re-authentication itself, may
  skip the step-up rules** (section 2, "Re-authentication", says which).
- **Four Level 2 session requirements of ASVS 5.0** are left to a team that works at that level
  ([security.md](../../react/security/security.md) section 17). The session rules of section 2
  cover the Level 1 requirements of ASVS 5.0 chapter V7 and the Level 2 requirements they cite
  [42]. They leave out the part of 7.4.5 in which an administrator ends the sessions of all users,
  and 7.5.2, users see and end their own sessions [42]. They also leave out 7.6.1, the
  application's and the provider's sessions end as documented, with the user signed in again
  where needed, beyond the choice section 2 asks to write down; and 7.6.2, a new session starts
  only with the user's consent or an explicit act [42].

## 6. Review checklist

| Section | Ask | Red flag |
|---|---|---|
| 2, "The session cookie" | Does the session cookie carry the `__Host-Http-` name and every attribute the table asks for, in every environment? | a session cookie without the `__Host-Http-` prefix; a session cookie without `Secure`, `HttpOnly` or a written `SameSite`, or with `Domain` |
| 2, "The login cookie" | Is each login attempt's record protected, bound to its own cookie and cleared at every callback? | a callback page that shows a parameter of the request; a login cookie without the `__Host-Http-` prefix; a login attempt's record kept on the server, or in a cookie or `state` that is not encrypted and signed; a BFF with more than one identity provider that checks neither `iss` nor a callback path for each provider; a login cookie left behind after a failed callback; a login's return target taken from the request and redirected to unchecked |
| 2, "Reading the `Cookie` header" | Does the server read the session cookie only from its own parse of the raw `Cookie` header, after the name checks? | a session or login cookie read without checking that its name appears once, or with a duplicate check that reads only the first `Cookie` field line; a cookie whose name becomes the session or login cookie's name once non-token characters are removed and ASCII letters are lowercased, read instead of answered with `400`; a `Cookie` header that starts with `$Version` accepted, or a cookie parser set to a legacy RFC 2109 or RFC 2965 mode; a session cookie value read from the framework's cookie collection, or looked up or decrypted before its format is checked |
| 2, "The session's life, from login to logout" | Is the session's state where the rules put it, and does the session check hand out no token? | a session check that returns a token, or answers without `Cache-Control: no-store`; a session store that an identity other than the BFF's can reach, except the identity of step 3 of the leaked-key plan while that run lasts |
| 2, "Keys and secrets" | Do the keys come from the secret store, rotate on a written schedule, and have a routine rotation that was tried and a leaked-key plan that was tried? | a cookie key kept in the code, or shared between environments; a new key that protects cookies before every instance holds it; an unreadable cookie answered with `500`; no rotation job, or no rotation period written down; no leaked-key plan, or one never run in a test environment; a routine rotation never tried in a test environment; an old key removed before step 3's time; a key store an instance can write; no alert on a rotation job that logs no run |
| 2, "A new session id at login" | Does every login and re-authentication issue a new session id and destroy the old one? | the same session id before and after login |
| 2, "Timeouts and refresh" | Does the server end the session on timeout, and keep it through a refresh that fails for a reason other than the grant? | a session kept after `invalid_grant` or `interaction_required`; a stored refresh token emptied by an answer that carries none; a timed-out session's record left in the store; a timeout kept only in the page; a session accepted when the session store or the list of ended sessions cannot be read |
| 2, "Logout" | Does the server end the session at logout, so that no copy of the cookie works after it? | a logout that only deletes the cookie; a session that a late request can save back after logout; a logout token accepted without the checks of Back-Channel Logout 1.0 section 2.6 |
| 2, "Re-authentication" | Does each guarded change pass a re-authentication of the session's own user, used once? | a step-up that does not compare `iss` and `sub`; a step-up without the `auth_time` or `acr` check, or not bound to its session; a guarded change let through outside the re-authentication window, or twice in one window; a re-authentication time cleared after the change, or on the session object the request loaded, instead of consumed in one atomic store write before it; a step-up guess count kept in the session object the request loaded; a step-up answer in the URL; a step-up that moves the session from the copy the request loaded; a disabled account whose sessions wait for the provider |
| 2, "Forwarding to resource servers" | Does the BFF forward only to its allowlist, with one token per resource server? | a BFF route that forwards to a host or path taken from the request, or with a method its resource server does not serve; one access token sent to several resource servers |
| 3, "CSRF" | Does every request to an API route pass the custom-header and Fetch Metadata checks before the session lookup? | a custom-header or Fetch Metadata check that runs after the session lookup; an API route that accepts a request without the custom header; a check or a policy still log-only after its written end |
| 3, "Fetch Metadata and exemptions" | Does Fetch Metadata allow only the exact origins in the setting of allowed origins, does the API change no user data or session on a `GET`, and does it exempt only the endpoints its table lists? | a change to the user's data or session on a `GET` other than the login start or the login callback, which creates the session or, after a step-up, replaces it; a Fetch Metadata check that allows every `same-site` request; a CSRF exemption by request mode, by a missing header or by path prefix; a report intake with no rate limit; an `allowedOrigins` entry written as `*` or `**`; a framework's action check on a version that skips `PUT`, `PATCH` or `DELETE` |
| 3, "Forwarding tokens" | Does the BFF keep a resource server's `401` from reaching the page? | a resource server's `401` passed to the page |
| 3, "WebSocket" | Is each WebSocket checked by `Origin` at the handshake and closed when its session ends? | a WebSocket handshake with no `Origin` check; a WebSocket that stays open after logout |
| 3, "Paths and proxies" | Is each dynamic path segment checked against its format? | a dynamic path segment not checked against its format |
| 3, "Response headers" | Does every API response carry the header set, and every file from outside `Content-Disposition: attachment`? | a file from outside served inline on the download route |
| 3, "Logging" | Does every rejected check leave a log line, was each alert rule made to fire once, and does every alert reach a recipient who was tested? | a rejected check, a failed sign-in or re-authentication, or a session that could not be ended, with no log line; no alert on the rejection rate or on a step-up from another account; an alert recipient never sent a test alert; an alerting platform that cannot send each alert to a named recipient, or cannot send a test alert; an alert rule never made to fire in a test environment |
| 3, "CORS" | Does the API allow only exact origins, with credentials? | `Access-Control-Allow-Origin` copied from the request unchecked, matched by suffix or pattern, `null`, or `*` with credentials; a preflight answered with a status other than `2xx`, or placed behind the session check |
| 3, "Fixing a CORS error" | Was the CORS error fixed on the server, by adding the exact origin? | a framework's any-origin option turned on with credentials |
| 4, "Choosing a library or framework" | Was each row of section 4 that applies answered from the library's code or from a test at the version picked, with those tests in the BFF's own test suite? | a row answered from the library's docs; a library update with no rerun of the tests |

## 7. Sources

Checked 2026-10-17 unless a line ends with — checked <YYYY-MM-DD>.

- [1] IETF — RFC 10017, OAuth 2.0 for Browser-Based Applications, BCP 212, August 2026 — https://www.rfc-editor.org/rfc/rfc10017.txt
- [2] IETF — Cookies: HTTP State Management Mechanism, draft-ietf-httpbis-rfc6265bis-22 — https://www.ietf.org/archive/id/draft-ietf-httpbis-rfc6265bis-22.txt
- [3] IETF HTTP Working Group — Cookies: HTTP State Management Mechanism, draft-ietf-httpbis-layered-cookies-02 — https://www.ietf.org/archive/id/draft-ietf-httpbis-layered-cookies-02.txt
- [4] MDN — Set-Cookie header — https://raw.githubusercontent.com/mdn/content/main/files/en-us/web/http/reference/headers/set-cookie/index.md
- [5] web-platform-tests — wpt.fyi results for `cookies/prefix` and `cookies/samesite`, stable aligned runs of 2026-10-06 (Chrome 154, Edge 154, Firefox 157, Safari 27.0) — https://wpt.fyi/api/search?run_ids=6218298311311360,4877098740350976,5164107446878208,5139408432136192&q=cookies%2Fprefix
- [6] web-platform-tests — Safari 27.0 subtest results for `cookies/prefix` and `cookies/samesite`, stable aligned run of 2026-10-06 — https://storage.googleapis.com/wptd/cc74d2669f5de548e808779877d1d33339ec5115/safari-27.0__22625.1.29.11.27_-mac-27.0-434012013c/cookies/prefix/__host.header.https.html, https://storage.googleapis.com/wptd/cc74d2669f5de548e808779877d1d33339ec5115/safari-27.0__22625.1.29.11.27_-mac-27.0-434012013c/cookies/prefix/__Host-Http.https.html, https://storage.googleapis.com/wptd/cc74d2669f5de548e808779877d1d33339ec5115/safari-27.0__22625.1.29.11.27_-mac-27.0-434012013c/cookies/prefix/__host.explicit-path.https.window.html
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
- [144] OWASP — Unvalidated Redirects and Forwards Cheat Sheet — https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.md
- [145] OWASP — Application Security Verification Standard, V15 Secure Coding and Architecture, 5.0.0 — https://github.com/OWASP/ASVS/blob/v5.0.0_release/5.0/en/0x24-V15-Secure-Coding-and-Architecture.md
- [146] OWASP — Secrets Management Cheat Sheet — https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Secrets_Management_Cheat_Sheet.md
- [147] Chromium — HSTS Preload List Submission — https://hstspreload.org/
- [148] OWASP — Server Side Request Forgery Prevention Cheat Sheet — https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.md
- [149] OWASP — Web Security Testing Guide, Host Header Injection (WSTG-INJT-17) — https://raw.githubusercontent.com/OWASP/wstg/master/document/4-Web_Application_Security_Testing/07-Injection/17-Host_Header_Injection.md
- [150] Amazon Web Services — Elastic Load Balancing, Health checks for Application Load Balancer target groups — https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html
- [151] Envoy Project — Envoy documentation, Panic threshold — https://raw.githubusercontent.com/envoyproxy/envoy/main/docs/root/intro/arch_overview/upstream/load_balancing/panic_threshold.rst
- [152] Redis — Distributed Locks with Redis — https://raw.githubusercontent.com/redis/docs/main/content/develop/clients/patterns/distributed-locks.md
- [153] expressjs — express-session source, `index.js`, v1.19.0 — https://raw.githubusercontent.com/expressjs/session/v1.19.0/index.js
- [154] Microsoft — ASP.NET Core source, `KeyManagementOptions.cs` — https://raw.githubusercontent.com/dotnet/aspnetcore/main/src/DataProtection/DataProtection/src/KeyManagement/KeyManagementOptions.cs — checked 2026-10-18
