# React security practices

What the browser side of a React application must and must not do: keep outside data from
running as script, keep tokens and secrets out of the browser, send the headers that limit an
injected script, install packages under a cooldown and a script block, keep the dev server to
the developer's machine, and leave every access decision to the server. What the backend that
holds the session must do for that browser side, the session cookie, the session's life from
login to logout, CSRF and CORS, is the
[backend-for-frontend](../../any-language/backend-for-frontend/) practice.

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)

## What is here

- [security.md](security.md) — the rules, one topic per section: XSS and its sinks, sanitising
  and Trusted Types, the Content-Security-Policy and the other headers, sessions and tokens (the
  comparison of the session patterns, and the page's side), CSRF and CORS (the page's side),
  server-side React, secrets, the supply chain, the dev server, third-party code, data the
  browser exposes, and the lint rules and scanners; then the common mistakes as bad and good
  pairs, where the rules stop holding, a review checklist,
  [what the OWASP Top 10 is and how to work with it](security.md#what-the-owasp-top-10-is-and-how-to-work-with-it),
  with its 2025 categories mapped to the sections, and the sources.
  Read it at the moments its section 1 lists.
- [security-example.md](security-example.md) — the security-relevant parts of one billing
  application, each with the threat it stops and what it does not stop: the API client, the
  public settings, the link, the one HTML sink, the web-vitals report, the headers file, the lint
  rules and the package manager settings. Read it when you set these parts up in an application.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/react/security/`. Where the BFF or
   the API that holds the session lives in a repository of its own, copy the
   [backend-for-frontend](../../any-language/backend-for-frontend/) practice there, with this
   folder, which its rules link.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you put data from outside a React
   application on its page, spread an object from outside as props, handle a session or a token
   in one, keep or send a credential, add an environment variable, a dependency, a third-party
   script, a response header or a CI step to one, change the dev server's settings, set up its
   query client, add polling, build the shell its screens share, write or change a Server
   Function, a server-rendered route or middleware in one, or register a service worker, read
   `docs/engineering/react/security/security.md`." Without it an agent never opens the file. The
   BFF's own repository takes the line in the
   [backend-for-frontend README](../../any-language/backend-for-frontend/README.md#how-to-adopt).
3. In the same change, turn on the lint rules of section 14 and the package manager settings of
   section 10, so the rules are checked from the first commit on. On an application that already
   exists, review each build script the strict setting refuses and add it to the allow list
   (`allowBuilds` or `allowScripts`) before the setting lands, and mark the old lint violations as
   [refactoring.md](../../any-language/refactoring/refactoring.md) section 4 says, with the fix-by
   date its section 6 asks for. Run the install once under the new settings before the change
   lands. pnpm re-checks every lockfile entry against `minimumReleaseAge` and `trustPolicy`, so an
   entry younger than the cooldown, or with weaker provenance than an earlier version, fails it.
   Land the cooldown once those entries are older than it, or exempt each one as security.md
   section 10's emergency path says, which also names the exemption for an entry that fails
   `trustPolicy`, with its removal task.
4. Use section 17's first work step as the security part of your review template: read the rules
   of every section the change touches, and check the red flags of section 17's checklist.
5. The practice links the
   [backend-for-frontend](../../any-language/backend-for-frontend/) practice, which owns the
   server's rules, the other React practices (architecture, components, design, performance),
   [file-structure.md](../../any-language/file-structure/file-structure.md),
   [readability.md](../../any-language/readability/readability.md),
   [refactoring.md](../../any-language/refactoring/refactoring.md),
   [roles-and-decisions.md](../../any-language/project-management/roles-and-decisions.md) for the
   decision log, and two Python practices for rules they own: the form of a lint suppression in
   [static-checks.md](../../python/static-checks/static-checks.md) and what never goes into a log
   in [logging.md](../../python/logging/logging.md). Copy those folders too, or replace each link
   with your own rule for that topic.
6. Re-check what moves when you adopt the practice, and again six months after each source's date
   in security.md's Sources section: the date on the section's first line, or the date a source's
   own line ends with (`— checked <date>`). From six months after a source's date until it is read
   again, distrust every line that cites it; the earliest such day is 2027-04-01.

   Dated sources: when you adopt the practice, add a task dated 2027-04-01 to the team's tracker,
   with an owner, so the re-check does not rest on anyone's memory. At that task, the owner
   re-reads each source whose date is six months old or more, updates its date, and adds the next
   task, with an owner, for six months after the oldest date left. List the sources' dates with
   `grep -nE '^Checked|— checked' docs/engineering/react/security/security.md`, and the lines in
   the text that carry a read date with
   `grep -rnE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' docs/engineering/react/security/`. At the same task,
   check whether OWASP has published a new Top 10 edition, or a newer ASVS, Proactive Controls or
   WSTG version (security.md section 17).

   Advisories: for the advisories of React's server packages, your framework, your router, Vite
   and DOMPurify, do not wait for a re-check. Turn on the host's dependency alerts (Dependabot
   alerts on GitHub) and watch the advisory sources security.md cites, as
   [security.md](security.md) section 10 says, since a critical one is patched within the day.
7. When you adopt the practice, do four things that security.md asks for at moments when nobody
   has it open: pick the ASVS level and write it into the decision log (security.md section 17);
   add a line "threats modelled, and security requirements taken from ASVS level <n> (security.md
   section 17)" to the template the team uses to design or ticket a feature, for a feature that
   touches authentication, access control, business logic or a key flow; add a line "tested
   against the OWASP Web Security Testing Guide" to the team's release checklist, for a release
   that changes those parts; and write the person or channel that receives security advisories and
   alerts into the decision log (security.md section 8, and
   [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
   sections 2 and 3).

## The points to adapt

- **The session pattern.** Whether the application needs a BFF is
  [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
  section 1; where the team runs a browser-only OAuth client instead,
  [security.md](security.md) section 6's `Browser-only client:` rules apply in full. When your
  own server signs the user in with no identity provider, section 6's opening paragraph says which
  rules drop.
- **The cooldown length.** One day covered the short-lived package hijacks of 2025 and 2026, and
  seven days is CISA's advice; a longer wait delays every normal update by as much. Whatever the
  length, the cooldown has a named emergency path.
- **The linter.** ESLint, Oxlint and Biome name the same rules differently (section 14); which one
  to use is [libraries.md](../architecture/libraries.md) section 4.
- **The host.** The format of the headers file depends on where the application is served.
- **One origin or two.** The example serves the page and the API from two origins of one site,
  so the API needs CORS. An API served on the page's own origin needs none: the rules under "CORS"
  in [backend-for-frontend.md](../../any-language/backend-for-frontend/backend-for-frontend.md)
  section 3 then do not apply, while its CSRF rules still do. On the page's side, the two rules in
  security.md section 7 that start "When the API is on another origin of the site" then do not
  apply either.

What does not change is the one rule: anything the browser holds, a script on the page can read,
and anything the browser decides, the user can change.
