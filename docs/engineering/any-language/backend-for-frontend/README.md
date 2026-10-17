# Backend for Frontend practices

What the server that holds a browser application's session must do, the Backend for Frontend
(BFF): its session and login cookies and their keys, the session's life from login to logout,
re-authentication, forwarding to resource servers, and its CSRF and CORS checks. What the page does
with such a server is the [React security practice](../../react/security/).

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)

## What is here

- [backend-for-frontend.md](backend-for-frontend.md) — the rules. Section 1 says what a BFF
  solves, when an application needs one and when the simpler way does; section 2 holds sessions
  and tokens (the session and login cookies, reading the `Cookie` header, the session's life with
  its keys and secrets, a new session id at login, timeouts and refresh, logout,
  re-authentication, forwarding to resource servers, and the login and logout responses);
  section 3 holds CSRF and CORS (what the server does, forwarding tokens, WebSocket, paths,
  response headers, logging, and fixing a CORS error); section 4 is the questions to ask a
  library or a framework before you build on it; section 5 says where the rules stop holding;
  section 6 is the review checklist; section 7 lists the sources. Read it before you build or
  change the server that holds a browser application's session, or pick a library for it.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/any-language/backend-for-frontend/`,
   and `docs/engineering/react/security/` with it, since the rules link security.md for the
   page's side. The rules also link the logging, readability and project-management practices
   and the React architecture practice; copy those folders too, or those links break.
2. In the BFF's own repository, add this line to your `CLAUDE.md` or `AGENTS.md`: "Before you
   handle a session or a token, set the session cookie, rotate a cookie key, change how the
   session starts, times out or ends, change the CORS or CSRF checks, add a route, a WebSocket, a
   file download or a response header to the API, or pick a library or a framework for the
   server, read `docs/engineering/any-language/backend-for-frontend/backend-for-frontend.md`;
   before you store a file users upload, or add or update a dependency, read sections 5 and 10 of
   `docs/engineering/react/security/security.md`." Without it an agent never opens the file.
