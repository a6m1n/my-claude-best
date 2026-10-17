# Backend for Frontend

**Navigation**

- [1. Purpose and scope](#1-purpose-and-scope)
- [2. Sessions and tokens](#2-sessions-and-tokens)
- [3. CSRF and CORS](#3-csrf-and-cors)
- [4. Where the rules stop holding](#4-where-the-rules-stop-holding)
- [5. Review checklist](#5-review-checklist)
- [6. Sources](#6-sources)

## 1. Purpose and scope

A browser application that signs users in has to keep its session somewhere. These rules keep it
on a server, the Backend for Frontend (BFF) that RFC 10017 describes, so the page holds no token:
the server keeps the tokens and gives the browser only a session cookie that script cannot read.
They are for the team that builds or runs that server, and cover its session and login cookies,
the session's life from login to logout, re-authentication, and its CSRF and CORS checks. The
page's own rules are in [security.md](../../react/security/security.md), whose sections 6 and 7
open with what a BFF is and what "the server", "the API" and "an API route" mean here. A server
that signs users in itself, with no identity provider, plays the BFF's part, and the opening of
[security.md](../../react/security/security.md) section 6 says which of these rules it skips.

## 2. Sessions and tokens

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
| `Max-Age` | not set: a non-persistent cookie | the server's idle and absolute timeouts end the session (section 2, "Timeouts and refresh"). A cookie with `Max-Age` is persistent, and the browser keeps it on disk through every close (OWASP's Session Management cheat sheet); one without it ends with the browser, though a browser that restores its last session brings it back (MDN), so the timeouts stay the control. Set `Max-Age`, no longer than the absolute timeout, only when the product needs the session to survive a browser close |
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
  since a person at the browser can edit any cookie value that is not protected
  ([security.md](../../react/security/security.md) section 1's one rule), and a login start has no
  session, so a record kept on the server for it would let anyone write records without limit. The
  rule is this practice's choice.
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
  (read 2026-10-16); the rule is this practice's choice. Section 4 names what this leaves open.
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
  OpenID Connect client library, update it under [security.md](../../react/security/security.md)
  section 10's advisory path,** which covers the BFF's own repository too. The browser checks the
  prefix; a server that parses the `Cookie` header in another way can read a cookie the browser
  treated as a different one. PortSwigger's research (2025) got past the `__Host-` and `__Secure-`
  prefixes on several server frameworks through such differences.
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

### The session's life, from login to logout

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
  user's answer for the next, as for every API response (section 3, "Response headers").
- **BFF: leave the session check out of the idle clock,** so a page that asks on every load, or
  before it reconnects a dropped WebSocket (section 3), does not keep an idle session alive; the
  rule is this practice's choice.
- **BFF, with an identity provider: choose where the session's state lives, and write the choice
  down:** on the server, with only a random id in the cookie, or in the cookie itself, signed and
  encrypted. With a first-party login there is no choice: the session's state stays on the server
  (the opening of [security.md](../../react/security/security.md) section 6). Where the session's
  state in the cookie changes a rule, the rule says how.
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

### Logout

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
- **BFF: where the user should also leave the identity provider, end its session too,** for
  example on a shared device or where one sign-in covers several applications. The BFF ends the
  session as the logout rules above say, expires the cookie, and answers with the provider's
  logout URL, built from `client_id` and the registered `post_logout_redirect_uri`, with
  no `id_token_hint`, so no token reaches the page or a URL (RFC 10017 section 6.1; OpenID Connect
  RP-Initiated Logout 1.0). Without `id_token_hint`, RP-Initiated Logout 1.0 says in section 6 that
  the provider should get the user's explicit confirmation, and in section 3 that it must not send
  the user back to `post_logout_redirect_uri` unless it can confirm that target another way, so the
  redirect back may not happen; the local logout never waits for either step.
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
  of the store-outage rule above. Section 4 names what this leaves open.
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

The step-up rules below, down to the rule on the step-up's outcome route in
[security.md](../../react/security/security.md) section 6, serve ASVS 5.0 requirement 7.5.1, a Level
2 requirement: a team at Level 1 may skip them, and so may a team whose identity provider holds the
email, the phone, the second factor and the recovery data and asks for re-authentication itself;
write the choice down ("Write it down" above says where). The rules after them, on ending a user's
other sessions (7.4.3) and every session of a disabled or deleted account (7.4.2, a Level 1
requirement), hold for every team.

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
`Cross-Origin-Opener-Policy: same-origin` ([security.md](../../react/security/security.md)
section 5) cuts the page's link to the popup (MDN), so a popup flow needs that header relaxed to
`same-origin-allow-popups`, which MDN names for OAuth popups, or another way back to the page; the
navigation needs neither, and the BFF's outcome code tells the page what happened.

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
  `fetch`, which a browser sends with `Sec-Fetch-Dest: empty`, and the section 3 checks guard that
  request instead. The rule is this practice's choice.
- **BFF, with an identity provider: at the step-up's callback, accept the guarded change only when
  the new ID token's `iss` and `sub` equal those of the session recorded with the attempt and its
  `auth_time` is later than the time the step-up started,** because `iss` and `sub` together are
  the only claims a client can rely on to name the same user (OpenID Connect Core 1.0 section 5.7),
  so a thief who holds the cookie cannot pass the step-up by signing in to their own account, and a
  provider session that answers without asking the user does not count.
- **BFF, with an identity provider: when `iss` or `sub` does not match, refuse the change, end the
  session recorded with the attempt, log it and alert (the logging and alerting rules of section
  3),** since another account at the callback means the session may be in someone else's hands;
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
  resource server to the BFF (section 3 says what the BFF does with it), not the hop to the page;
  the signal to the page is this practice's choice. The `Page:` rules in
  [security.md](../../react/security/security.md) section 6 say what the page does with it.
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
that enforces the prefix accepts the deletion. The session cookie carries every attribute the
table asks for, so it keeps them in a browser that does not enforce the prefix (the table's first
row), and `no-store` keeps the response out of every cache
([security.md](../../react/security/security.md) section 13).

Good: the response of the BFF's logout endpoint, after it ended the session (destroyed it on the
server, or listed it as ended and revoked its tokens). The other headers section 3 asks of every
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
every response with its schema ([architecture.md](../../react/architecture/architecture.md) section
8), and an empty body has nothing to parse;
[security-example.md](../../react/security/security-example.md) section 1 shows that client.
`logoutUrl` is `null` here, and holds the provider's logout URL where the user should also leave the
identity provider, for the page to open by a top-level navigation (the rules on leaving the identity
provider, above). `Max-Age=0` removes the cookie at once, and the line repeats every attribute the
prefix requires: a browser that enforces the prefix rejects a `Set-Cookie` without them, so the old
cookie would stay. It sends no `Clear-Site-Data: "cookies"`, which would also clear the cookies of
every other application on `example.com`. It sends no `Clear-Site-Data` at all: the response comes
from `api.example.com`, whose origin holds nothing the page stored, and the page clears what it
loaded through its sign-out path.

## 3. CSRF and CORS

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
  (RFC 10017 section 6.1.3.3.1). The rules on sibling subdomains in sections 2 and 3 stay for a
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
  the check. web.dev gives these three steps for a Resource Isolation Policy, and
  [security.md](../../react/security/security.md) section 5 uses the same order for a new policy.
- **API: when a check starts in log-only mode, write down the date by which it is enforced
  ("Write it down" in section 2 says where), and add a task for that date, with an owner, to the
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
  proxy leaves that check to the target ([security.md](../../react/security/security.md) section
  11), and behind the proxy the page's other calls arrive as `same-origin`, so the CORS headers go
  unused there. Production's value holds the one origin of the application, so a review of it shows
  that the dev server's origin is absent.
- **Reject, with `403` and never `401`, a request to an API route that carries no custom header or
  whose Fetch Metadata check fails.** MDN's `Sec-Fetch-Site` page says a request that is not
  accepted should be rejected with a `403`; a `401` tells the page its session has ended, so an
  origin set up wrong would turn into a sign-in loop.
- **Answer `401` only when the session has ended or never existed, and `403` to a request the user
  is not allowed to make** (RFC 9110 sections 15.5.2 and 15.5.4), because the page runs the
  sign-out path on every `401` ([security.md](../../react/security/security.md) section 6). The
  logout endpoint is the exception: it answers success also when no session exists (section 2).
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
  the challenge's `acr_values`, and with `max_age=0` as the step-up rules of section 2 ask, which
  also meets any `max_age` the challenge names,** since RFC 9470 uses that challenge to say that the
  user's authentication does not meet the resource server's needs, which a refreshed token does
  not change (section 2, "Re-authentication").
- **Exempt from the custom header and the Fetch Metadata check only the endpoints in the table
  below, and guard each one as its row says,** since a request reaches each of them without the
  custom header. This table is this practice's departure from the MUST of RFC 10017 quoted above,
  and OWASP's CSRF Prevention cheat sheet asks for such an explicit list, each endpoint secured on
  its own. These endpoints skip the framework's own CSRF check too, since they cannot
  carry its token.

| Exempt endpoint | Matches by | Guarded by |
|---|---|---|
| the login start, a top-level `GET` | one exact path and the method `GET` | it changes neither the user's data nor the session; it starts a login attempt, which the login-cookie rules of section 2 bound |
| the login callback, which also applies a step-up's change | one exact path and its method | `state`, the nonce and the PKCE verifier bound to the login cookie (section 2); for a step-up's change, also the steps of section 2's step-up callback |
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
identity provider, not the BFF ([security.md](../../react/security/security.md) section 6). The
download link stays a navigation so that a large file goes to the browser's download manager, not
into the page's memory; a file the page shows goes through the API client and a blob instead
([security.md](../../react/security/security.md) section 7, "What the React code does").

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
  endpoint that anyone can send a `POST` to ([security.md](../../react/security/security.md) section
  8), and the framework's runtime sends it, not the one API client; the rule is this practice's
  choice.

#### WebSocket

- **Check `Origin` on every WebSocket handshake against the page's exact origin (the one the Fetch
  Metadata rule allows), or the CORS allowlist when there is more than one,** and answer `403` to
  any other origin. The browser sends the session cookie with the handshake, the handshake
  cannot carry the custom header, and `SameSite` lets a sibling subdomain through, so without the
  check a page elsewhere opens a connection as the user (OWASP's WebSocket Security cheat sheet;
  RFC 6455 section 10.2).
- **Tie each WebSocket connection to its session on the server, and close it when the session
  ends:** at logout, at the idle and absolute timeouts, and when a back-channel logout or the
  refresh rule of section 2 ends the session. The cookie is checked only at the handshake, so an
  open connection would keep sending the user's data after the session ended. OWASP's WebSocket
  Security cheat sheet asks to close the connections at logout and when the session expires.
- **When the server closes a WebSocket connection because its session ended, use one close code of
  your own from 4000 to 4999,** the range RFC 6455 section 7.4.2 reserves for private use, so the
  page can tell an ended session from a dropped connection (the `Page:` rules in
  [security.md](../../react/security/security.md) section 7, "What the React code does"); the rule
  is this practice's choice.
- **Check the session of each open WebSocket connection again at an interval no longer than the
  idle timeout, without counting the socket's keep-alive messages as activity on the idle clock,**
  for the reason the polling rule in [security.md](../../react/security/security.md) section 6
  gives. With the session's state in the cookie, that re-check is what closes the connection once
  the cookie's times or its tokens fail. OWASP's WebSocket Security cheat sheet asks to check the
  session again from time to time; the interval is this practice's choice.
- **BFF: leave the WebSocket handshake out of the idle clock, as section 2 does for the session
  check,** so a page that reconnects a dropped socket does not keep an idle session alive (the
  polling rule in [security.md](../../react/security/security.md) section 6); the rule is this
  practice's choice.

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
  advisories and alerts into the decision log ("Write it down" in section 2 says where), send one
  test alert to it, and send every alert below to it,** so every alert has a recipient who acts on
  it, even after people change roles, also in a client-rendered application that never reads
  [security.md](../../react/security/security.md) section 8, and an alert path is not first tried in
  an incident; the rule is this practice's choice.
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
  it down" in section 2 says where),** since OWASP Top 10:2025 A09 says that without alerting a
  team can hardly respond quickly and effectively to an incident; the rule is this practice's
  choice.
- **BFF, with an identity provider: alert a person on every step-up whose `iss` or `sub` does not
  match (section 2),** since another account at the callback means the session may be in someone
  else's hands; the rule is this practice's choice.
- **BFF, with an identity provider: alert a person on every back-channel logout that could not end
  its session (section 2),** since Back-Channel Logout 1.0 leaves sending the logout request again
  to the provider (section 2.5) and names nothing the provider does after the BFF's `400` (section
  2.8), so the session may stay live until its timeouts; the rule is this practice's choice.
- **BFF, with an identity provider: alert a person when valid back-channel logout tokens that
  match no session pass a rate the team writes down,** since a BFF whose stored `sid` never
  matches leaves live every session the provider ended, and section 2 logs each such token at
  `INFO`, the level for what nobody will look at ([logging.md](../../python/logging/logging.md)
  section 4); the rule is this practice's choice.

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
- **A proxy you run forwards only to the hosts on the BFF's allowlist (section 2), never to a URL
  the request names.** A proxy that forwards anywhere is server-side request forgery, which OWASP
  Top 10:2025 counts under A01 (CVE-2020-36851 in cors-anywhere).

## 4. Where the rules stop holding

- **With the session's state in the cookie, only the list of ended sessions stops a copy of the
  cookie at once;** without it, how long a copy works depends on the revocation and the timeouts
  of section 2.
- **With the session's state in the cookie, a refresh whose answer never reaches the browser,**
  such as one for a cancelled query or a dropped connection, loses its `Set-Cookie`: the browser
  keeps the old refresh token, and when its next request comes after the provider's reuse window,
  that request counts as reuse and the user is signed out (section 2, "Timeouts and refresh").
- **A back-channel logout that the BFF cannot carry out,** because its session store cannot be
  written, can leave the session live until its timeouts; only the `ERROR` line of section 2 and its
  alert (section 3, "Logging") show it.
- **A login start that arrives from another site,** such as a link in an email, carries no
  `Strict` session cookie, so the BFF cannot record the old session id, and the old session lives
  on until its own timeouts or its logout (section 2, "A new session id at login").
- **Another site can still send the user to the login start by a top-level navigation,** which the
  `Sec-Fetch-Dest` check of section 2 lets through; in a browser that sends no Fetch Metadata, the
  check does not stop an image or a frame either, whose login cookie a browser that follows the
  cookie spec stores only with `response_mode=form_post` (section 2). Each such request starts a
  login attempt; the cap on login cookies keeps their number small, but it can push out the cookie
  of an attempt the user started, whose sign-in then has to start again.
- **Where other applications or user content share the application's site (section 3, "CSRF"), a
  sibling subdomain can lock a user out:** a cookie it plants that the cookie checks of section 2
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
  cookie although its name passes the check of section 2: PHP URL-decoded cookie names before
  7.2.34, 7.3.23 and 7.4.11 (CVE-2020-7070), and parsed a name that starts with `_[Host-` as
  `__Host-` before 8.1.28, 8.2.18 and 8.3.6 (CVE-2024-2756, PHP's advisory GHSA-wpj3-hf5j-x4v4).
  Keep the framework patched ([security.md](../../react/security/security.md) section 10).
- **A BFF on another registrable domain** sets a third-party cookie, which Firefox and Safari block
  by default and Chrome lets users block (MDN's third-party cookies guide, read 2026-10-15). The
  cookie rules of section 2 assume the BFF shares the application's site, as `api.example.com` does;
  `Partitioned` does not change that, since it keeps a cookie to the site that embeds the frame.
- **Pages the server renders read the session on navigations from other sites,** such as a link
  in an email, so their session cookie takes `Lax` instead of `Strict` (section 2).
- **A first-party login's credential checks** are outside this practice: password storage,
  protection against automated attacks on the login itself, such as login throttling (section 2
  limits only the failed answers to a step-up), and one generic message for a failed sign-in.
  OWASP's Authentication and Password Storage cheat sheets are where to look.
- **A team at ASVS Level 1, or one whose identity provider holds the email, the phone, the second
  factor and the recovery data and asks for re-authentication itself,** may skip the step-up rules
  of section 2's "Re-authentication", which serve the Level 2 requirement 7.5.1, and writes the
  choice down.
- **Five Level 2 session requirements of ASVS 5.0** are left to a team that works at that level
  ([security.md](../../react/security/security.md) section 17). The session rules of section 2 cover
  the Level 1 requirements of ASVS 5.0 chapter V7 and the Level 2 requirements they cite. They leave
  out 7.1.2, the number of sessions one account may hold; 7.4.5, an administrator ends one user's
  sessions or all of them; 7.5.2, users see and end their own sessions; 7.6.1, the application's and
  the provider's sessions end as documented, with the user signed in again where needed, beyond the
  choice section 2 asks to write down; and 7.6.2, a new session starts only with the user's consent
  or an explicit act.

## 5. Review checklist

| Section | Ask | Red flag |
|---|---|---|
| 2. Sessions, server | Does the server end the session at logout and on timeout? | a callback page that shows a parameter of the request; a session cookie or login cookie without the `__Host-Http-` prefix; a session cookie without `Secure`, `HttpOnly` or a written `SameSite`, or with `Domain`; a session or login cookie read without checking that its name appears once; a cookie whose name becomes the session or login cookie's name once non-token characters are removed and ASCII letters are lowercased, read instead of answered with `400`; a `Cookie` header that starts with `$Version` accepted; the same session id before and after login; a logout that only deletes the cookie; a session that a late request can save back after logout; a timeout kept only in the page; a session accepted when the session store or the list of ended sessions cannot be read; a step-up that does not compare `iss` and `sub`; a step-up without the `auth_time` check, or not bound to its change and to its session; a step-up check against a login-cookie value that is neither protected nor kept on the server; a WebSocket that stays open after logout; a BFF route that forwards to a host or path taken from the request |
| 3. CSRF and CORS, server | Does the API allow only exact origins, change no user data or session on a `GET`, and exempt only the endpoints section 3 lists? | a change to the user's data or session on a `GET` other than the login start or the login callback, which creates the session or applies a step-up's change; `Access-Control-Allow-Origin` copied from the request unchecked, matched by suffix or pattern, `null`, or `*` with credentials; a Fetch Metadata check that allows every `same-site` request; a WebSocket handshake with no `Origin` check; an API route that accepts a request without the custom header; a dynamic path segment not checked against its format; a CSRF exemption by request mode, by a missing header or by path prefix; a file from outside served inline on the download route; a check or a policy still log-only after its written end; a rejected check, a failed sign-in or re-authentication, or a session that could not be ended, with no log line; no alert on the rejection rate or on a step-up from another account |

## 6. Sources

The sources these rules name, and how each was read, are listed in
[security.md](../../react/security/security.md) section 18 until this file gets its own Sources
section.
