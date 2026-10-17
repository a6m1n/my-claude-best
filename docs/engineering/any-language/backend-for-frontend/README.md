# Backend for Frontend practices

What the server that holds a browser application's session must do, the Backend for Frontend
(BFF): its session and login cookies, the session's life from login to logout, re-authentication,
forwarding to resource servers, and its CSRF and CORS checks. What the page does with such a
server is the [React security practice](../../react/security/).

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)

## What is here

- [backend-for-frontend.md](backend-for-frontend.md) — the rules, one topic per section: sessions
  and tokens (the session and login cookies, reading the `Cookie` header, the session's life from
  login to logout, a new session id at login, timeouts and refresh, logout, re-authentication,
  forwarding to resource servers, and the login and logout responses), CSRF and CORS, where the
  rules stop holding, and a review checklist. Read it before you build or change the server that
  holds a browser application's session.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/any-language/backend-for-frontend/`,
   and `docs/engineering/react/security/` with it, since the rules link security.md for the
   page's side and for their sources.
2. In the BFF's own repository, add this line to your `CLAUDE.md` or `AGENTS.md`: "Before you
   handle a session or a token, set the session cookie, change how the session starts, times out
   or ends, change the CORS or CSRF checks, or add a route, a WebSocket, a file download or a
   response header to the API, read
   `docs/engineering/any-language/backend-for-frontend/backend-for-frontend.md`; before you store
   a file users upload, or add or update a dependency, read sections 5 and 10 of
   `docs/engineering/react/security/security.md`." Without it an agent never opens the file.
