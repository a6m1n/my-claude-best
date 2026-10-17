# React security practices

What the browser side of a React application must and must not do: keep outside data from
running as script, keep tokens and secrets out of the browser, send the headers that limit an
injected script, install packages under a cooldown and a script block, keep the dev server to
the developer's machine, and leave every access decision to the server. It also says what the
backend that holds the session must do for that browser side: the session cookie, the session's
life from login to logout, CSRF and CORS.

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)

## What is here

- [security.md](security.md) — the rules, one topic per section: XSS and its sinks, sanitising
  and Trusted Types, the Content-Security-Policy and the other headers, sessions and tokens (the
  session cookie and the session's life from login to logout), CSRF and CORS, server-side React,
  secrets, the supply chain, the dev server, third-party code, data the browser exposes, and the
  lint rules and scanners; then the common mistakes as bad and good pairs, where the rules stop
  holding, a review checklist,
  [what the OWASP Top 10 is and how to work with it](security.md#what-the-owasp-top-10-is-and-how-to-work-with-it),
  with its 2025 categories mapped to the sections, and the sources.
  Read it at the moments its section 1 lists.
- [security-example.md](security-example.md) — the security-relevant parts of one billing
  application, each with the threat it stops and what it does not stop: the API client, the
  public settings, the link, the one HTML sink, the web-vitals report, the headers file, the lint
  rules and the package manager settings. Read it when you set these parts up in an application.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/react/security/`. Where the BFF or
   the API that holds the session lives in a repository of its own, copy the folder there too,
   since most of sections 6 and 7 are the server's rules.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you put data from outside a React
   application on its page, spread an object from outside as props, handle a session or a token
   in one, keep or send a credential, set its session cookie, change how its session starts, times
   out or ends, change its API's CORS or CSRF checks, add an environment variable, a dependency, a
   third-party script, a response header or a CI step to one, change the dev server's settings,
   add a route, a WebSocket or a file download to its API or to the server that holds its
   session, set up its query client, add polling, or build the shell its screens share, read
   `docs/engineering/react/security/security.md`." Without it an agent never opens the file. In
   the BFF's own repository, add this line instead: "Before you handle a session or a token, set
   the session cookie, change how the session starts, times out or ends, change the CORS or CSRF
   checks, add a route, a WebSocket, a file download or a response header to the API, store a file
   users upload, or add or update a dependency, read sections 5, 6, 7, 10 and 17 of
   `docs/engineering/react/security/security.md`."
3. In the same change, turn on the lint rules of section 14 and the package manager settings of
   section 10, so the rules are checked from the first commit on. On an application that already
   has users, roll out section 7's server checks as its log-only rule says.
4. Use section 17's checklist as the security part of your review template.
5. The practice links the other React practices (architecture, components, design, performance),
   [file-structure.md](../../any-language/file-structure/file-structure.md),
   [readability.md](../../any-language/readability/readability.md),
   [refactoring.md](../../any-language/refactoring/refactoring.md),
   [roles-and-decisions.md](../../any-language/project-management/roles-and-decisions.md) for the
   decision log, and two Python practices for rules they own: the form of a lint suppression in
   [static-checks.md](../../python/static-checks/static-checks.md) and what never goes into a log
   in [logging.md](../../python/logging/logging.md). Copy those folders too, or replace each link
   with your own rule for that topic.
6. Re-check what moves when you adopt the practice, and again six months after each line's read
   date: distrust every dated line from then until it is read again, the earliest on 2027-04-01.

   Dated lines: when you adopt the practice, add a task dated 2027-04-01 to the team's tracker, so
   the re-check does not rest on anyone's memory. At that task, re-read the source of each dated
   line, update its date, and add the next task for six months after the oldest date left. List
   every dated line with
   `grep -rnE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' docs/engineering/react/security/`; the lines whose
   date is a read date are the ones to re-check, and each line in security.md that names a moving
   target carries the date it was read. At the same task, check whether OWASP has published a new
   Top 10 edition, or a newer ASVS, Proactive Controls or WSTG version (security.md section 17).

   Advisories: for the advisories of React's server packages, your framework, your router, Vite
   and DOMPurify, do not wait for a re-check. Turn on the host's dependency alerts (Dependabot
   alerts on GitHub) and watch the advisory sources security.md cites, as
   [security.md](security.md) section 10 says, since a critical one is patched within the day.
7. When you adopt the practice, do four things that security.md asks for at moments when nobody
   has it open: pick the ASVS level and write it into the decision log (security.md section 17);
   add a line "threats modelled (security.md section 17)" to the template the team uses to design
   or ticket a feature, for a feature that touches authentication, access control, business logic
   or a key flow; add a line "tested against the OWASP Web Security Testing Guide" to the team's
   release checklist, for a release that changes those parts; and write the person or channel
   that receives security advisories and alerts into the decision log (security.md sections 6, 7
   and 8).

## The points to adapt

- **The session pattern.** This practice picks the Backend for Frontend, which RFC 10017
  recommends for business, sensitive and personal-data applications. A lower-risk application may
  run a browser-only OAuth client; section 6's storage and refresh-token rules then apply in full.
  When your own server signs the user in with no identity provider, section 6's opening paragraph
  says which rules drop.
- **Where the session's state lives.** On the server, with only an id in the cookie, or in the
  cookie itself, signed and encrypted; section 6 says which rules change with the choice.
- **The cooldown length.** One day covered the short-lived package hijacks of 2025 and 2026, and
  seven days is CISA's advice; a longer wait delays every normal update by as much. Whatever the
  length, the cooldown has a named emergency path.
- **The linter.** ESLint, Oxlint and Biome name the same rules differently (section 14); which one
  to use is [libraries.md](../architecture/libraries.md) section 4.
- **The host.** The format of the headers file depends on where the application is served.
- **One origin or two.** The example serves the page and the API from two origins of one site,
  so the API needs CORS. An API served on the page's own origin needs none: the rules under "CORS"
  in section 7 then do not apply, while its CSRF rules still do.
- **The session timeouts.** The idle and absolute timeouts come from your risk level; section 6
  gives OWASP's ranges and NIST's values for each assurance level.

What does not change is the one rule: anything the browser holds, a script on the page can read,
and anything the browser decides, the user can change.
