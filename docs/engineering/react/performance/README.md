# Performance practices

How to make a React application fast for the people who use it: the three Core Web Vitals and
their thresholds, measuring them on real users, finding the part of a failing metric that is
largest, and the rules for loading, runtime, the server-rendered case and, in brief, search.

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The point to adapt](#the-point-to-adapt)

## What is here

- [performance.md](performance.md) — what fast means, how to measure it, the order of work,
  loading, runtime, the server-rendered case, SEO in brief, the common mistakes as pairs, then
  where the rules stop holding and a review checklist. Read it before you change how a screen
  loads its code, its data, its images or its fonts, before you add a dependency to the first
  screen, and when a field metric fails.
- [performance-example.md](performance-example.md) — the performance setup of one
  client-rendered application: the field-metrics reporter, preload on intent, the loaders, the
  query cache, route-level splitting with its build output, and the cache headers, each with the
  metric it serves. Read it when you set up measuring and loading in a new application.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/react/performance/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you add an image, a font, a route, a
   data request or a dependency to the first load of a screen in a React application, or act on a
   report that such an application is slow, read
   `docs/engineering/react/performance/performance.md`." Without it an agent never opens the file.
3. Use section 11's checklist as the performance part of your review template, so a reviewer
   asks the same questions every time.
4. The practice links [architecture.md](../architecture/architecture.md),
   [libraries.md](../architecture/libraries.md), [components.md](../components/components.md),
   [security.md](../security/security.md), [accessibility.md](../design/accessibility.md),
   [readability.md](../../any-language/readability/readability.md) and
   [git.md](../../any-language/git/git.md) for the rules they own. Copy those folders too, or
   replace each link with your own rule for that topic.
5. Re-check the lines that name a moving target. Each was read on 2026-10-01 or 2026-10-02. List them with
   `grep -rnE '2026-10-0[12]' docs/engineering/react/performance/`. Re-check them on the day you
   adopt the folder, when a browser ships or drops one of the features the rules name, and again
   by 2027-04-01, six months after the reading. After that date, distrust every dated line until
   it is read again.

## The point to adapt

The JavaScript budget, and the device it assumes, are yours to set. This practice starts from
one practitioner's model of a 75th-percentile phone, because no budget has been measured against
field metrics; an internal tool used on fast desktops, or a product whose field data shows its
own devices, sets its own number. What does not change is the one rule: measure on real users,
then fix the largest part of the metric that fails.
