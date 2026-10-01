# React security practices

What the browser side of a React application must and must not do: keep outside data from
running as script, keep tokens and secrets out of the browser, send the headers that limit an
injected script, install packages under a cooldown and a script block, keep the dev server to
the developer's machine, and leave every access decision to the server.

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)

## What is here

- [security.md](security.md) — the rules, one topic per section: XSS and its sinks, sanitising
  and Trusted Types, the Content-Security-Policy and the other headers, sessions and tokens, CSRF
  and CORS, server-side React, secrets, the supply chain, the dev server, third-party code, data
  the browser exposes, and the lint rules and scanners; then the common mistakes as bad and good
  pairs, where the rules stop holding, a review checklist and the sources. Read it before you put
  data from outside the application on the page, handle a session or a token, add a setting or a
  dependency, add a third-party script, or change the headers, the dev server or CI.
- [security-example.md](security-example.md) — the security-relevant parts of one billing
  application, each with the threat it stops and what it does not stop: the API client, the
  public settings, the link, the one HTML sink, the web-vitals report, the headers file, the lint
  rules and the package manager settings. Read it when you set these parts up in an application.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/react/security/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you put data from outside the
   application on the page, handle a session or a token, add a dependency or a `VITE_` setting,
   or change the headers, the dev server or CI, read
   `docs/engineering/react/security/security.md`." Without it an agent never opens the file.
3. In the same change, turn on the lint rules of section 14 and the package manager settings of
   section 10, so the rules are checked from the first commit on.
4. Use section 17's checklist as the security part of your review template.
5. The practice links the other React practices (architecture, components, design, performance),
   [file-structure.md](../../any-language/file-structure/file-structure.md),
   [readability.md](../../any-language/readability/readability.md),
   [refactoring.md](../../any-language/refactoring/refactoring.md), and two Python practices for
   rules they own: the form of a lint suppression in
   [static-checks.md](../../python/static-checks/static-checks.md) and what never goes into a log
   in [logging.md](../../python/logging/logging.md). Copy those folders too, or replace each link
   with your own rule for that topic.
6. Re-check what moves when you adopt the practice, and again whenever a line's date is more
   than a few months old; distrust every dated line after 2027-04-01, six months after the reading,
   until it is read again. List the lines to re-check with
   `grep -rnE '2026-10-0[12]' docs/engineering/react/security/`; each line in security.md that names
   a moving target carries the date it was read. For the advisories of React's server packages,
   your framework, your router, Vite and DOMPurify, do not wait for a re-check: subscribe, since a
   critical one is patched within the day.

## The points to adapt

- **The session pattern.** This practice picks the Backend for Frontend, which RFC 10017
  recommends for business, sensitive and personal-data applications. A lower-risk application may
  run a browser-only OAuth client; section 6's storage and refresh-token rules then apply in full.
- **The cooldown length.** One day covered the short-lived package hijacks of 2025 and 2026, and
  seven days is CISA's advice; a longer wait delays every normal update by as much. Whatever the
  length, the cooldown has a named emergency path.
- **The linter.** ESLint, Oxlint and Biome name the same rules differently (section 14); which one
  to use is [libraries.md](../architecture/libraries.md) section 4.
- **The host.** The format of the headers file depends on where the application is served.

What does not change is the one rule: anything the browser holds, a script on the page can read,
and anything the browser decides, the user can change.
