# UX evaluation and behaviour analytics

How a team finds out whether an interface works for the people who use it, and what those people
do in it once it is live. The first half is evaluation: expert reviews, tests with users,
questionnaires, benchmarks, metrics in production, surveys inside the product and A/B tests. The
second half is behaviour analytics: the tracking plan, page views in a single-page app, consent
before tracking, heatmaps, session replay and frustration signals, and how a coding agent gets that
data. The rules hold for any language and were written for the screens of web applications; the
React case of analytics is a labelled section of [behaviour-analytics.md](behaviour-analytics.md).

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)
- [Sources](#sources)

**When you do not need all of it.** A screen built from standard patterns needs a heuristic review
and a short round of tests with users, not a cognitive walkthrough, which Kim Flaherty of NN/g
calls "overkill" there [1]. A small internal tool with a handful of users cannot reach the numbers
a benchmark or an A/B test needs, and Jakob Nielsen holds that "For really low-overhead projects,
it's often optimal to test as few as 2 users per study" [2]. Before launch there is nothing to
measure: Kerry Rodden, Hilary Hutchinson and Xin Fu call metrics "primarily useful for evaluation
of launched products" [3], and an A/B test needs both versions built: "Features must be
implemented" [4]. Session replay records far more than a team watches: at PostHog, the tool's
vendor, "fewer than 1 in 600 recordings was opened" across its customers over 90 days [5]. Each
rules file says when its parts are too much: [evaluation.md](evaluation.md) section 15, and
[behaviour-analytics.md](behaviour-analytics.md) sections 1 and 10.

## What is here

The two rules files answer different questions: analytics shows where people drop out, and
research with people shows why ([evaluation.md](evaluation.md) section 8). A team that splits the
work by role, a user researcher and a performance analyst, gives each person one file; the reason
the two stay in one practice is [evaluation.md](evaluation.md) section 16.

- [evaluation.md](evaluation.md) — the three levels of evaluation and which fits when; expert
  review with heuristics and the cognitive walkthrough; tests with users: rounds, people, tasks
  and measures; the SEQ, the SUS and UMUX-LITE; benchmarks and sample sizes; people with
  disabilities among the participants; metrics in production; surveys inside the product and NPS;
  A/B tests; synthetic users and a model as a reviewer; how to judge an effective, a polished and a
  balanced interface; participants' personal data. Read it before you plan, run or report an expert
  review, a usability test, a benchmark, a survey inside the product, an A/B test or a UX metric,
  or before you say whether a screen works for its users.
- [behaviour-analytics.md](behaviour-analytics.md) — what each signal can show and what it cannot;
  the tracking plan: events, names and properties; page views in a single-page app; consent before
  tracking; heatmaps, session replay and frustration signals; giving a coding agent the data; and
  the React case. Read it before you add an analytics event, count page views, set up consent for
  tracking, turn on heatmaps or session replay, or give an agent access to analytics data.
- [test-plan-example.md](test-plan-example.md) — the plan of one round of moderated tests of an
  invoices screen with five accounts clerks: objectives and the decision they feed, participants,
  tasks with their success written first, measures, sessions, data, recording, timeline and what
  the round leaves out. Read it when you write a test plan.
- [tracking-plan-example.md](tracking-plan-example.md) — a tracking plan: the events, their names
  and their properties. Read it when you write or extend a tracking plan.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/any-language/ux-evaluation/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you plan, run or report a usability
   test, an expert review, a survey inside the product, an A/B test or a UX metric, judge whether a
   screen works for its users, add an analytics SDK, an event, a page-view source, a consent gate,
   heatmaps or session replay to a web application, or give an agent its analytics data, read
   `docs/engineering/any-language/ux-evaluation/README.md` and the file it routes to for that work,
   and `docs/engineering/any-language/ux-evaluation/test-plan-example.md` when you write a test
   plan, `docs/engineering/any-language/ux-evaluation/tracking-plan-example.md` when you write a
   tracking plan. The check: every test plan the change adds writes the decision its round feeds
   and each task's success before the first session (`evaluation.md` sections 2 and 4), every
   finding it reports from a model or a synthetic user carries that label (`evaluation.md`
   sections 11 and 18), every event it sends is in the tracking plan (`behaviour-analytics.md`
   section 3), each analytics tool gets its page views from one source (`behaviour-analytics.md`
   section 4), a new browser profile shows no request to the analytics host and no cookie or key of
   the tool before the consent banner is answered (`behaviour-analytics.md` section 5), and no rage
   click, dead click or hotspot is reported as a finding before a person watched the replay behind
   it (`behaviour-analytics.md` section 6)." Without it an agent never opens the folder.
3. The rules and examples link the practices that own a neighbouring rule:
   [ux.md](../../react/design/ux.md) section 9 (the heuristics as a reviewer's lens),
   [accessibility.md](../../react/design/accessibility.md) sections 10 and 11 (the automated checks
   and the manual pass), [designing-with-claude-code.md](../../react/design/designing-with-claude-code.md)
   section 6 (the verify loop for a screen an agent built),
   [visual-design.md](../../react/design/visual-design.md) section 2 (the effective, polished and
   balanced cases), [security.md](../../react/security/security.md) sections 12 and 13 (third-party
   scripts, analytics off login and payment screens, replay masking),
   [performance.md](../../react/performance/performance.md) section 3 (page speed as users see it),
   and [refactoring.md](../refactoring/refactoring.md) section 7 (how existing work moves). Copy
   those practices too, or point each link at the rule your project follows instead.
4. In work that exists already, apply the rules to new and changed screens first
   ([evaluation.md](evaluation.md) section 17, [behaviour-analytics.md](behaviour-analytics.md)
   section 12). A regulator's rule keeps the regulator's dates.
5. Re-check the lines that name a moving target. Each file's Sources section opens with its
   `Checked <date>` line. The studies of models as reviewers and participants are preprints from
   2025 and 2026, and NN/g's advice against AI moderators carries its review date of 2026-01-21
   ([evaluation.md](evaluation.md) section 11). The vendor pages, SDK versions and regulators'
   drafts that [behaviour-analytics.md](behaviour-analytics.md) names carry their own dates.

## The points to adapt

The shape stays: no claim that an interface works without people doing real tasks with it; a
model's or a tool's finding is a lead that a person checks; personal data of participants and
users is settled before it is collected; consent before tracking
([behaviour-analytics.md](behaviour-analytics.md) section 5). Within that shape, these are your
choices; each rules file names the options and their costs.

- How often to run rounds of tests, and how many people within 4 to 8 ([evaluation.md](evaluation.md)
  section 4).
- Whether to run a benchmark at all, and its size within 30 to 60 ([evaluation.md](evaluation.md)
  section 6).
- Whether people with disabilities join every round or rounds of their own
  ([evaluation.md](evaluation.md) section 7).
- Which HEART categories your product needs ([evaluation.md](evaluation.md) section 8).
- Whether your traffic supports A/B tests ([evaluation.md](evaluation.md) section 10).
- The analytics tool, and the case and tense of event names
  ([behaviour-analytics.md](behaviour-analytics.md) section 3).
- Whether to turn on heatmaps and session replay ([behaviour-analytics.md](behaviour-analytics.md)
  section 6).

## Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Kim Flaherty — Evaluate Interface Learnability with Cognitive Walkthroughs (Nielsen Norman Group, 2022; opinion) — https://www.nngroup.com/articles/cognitive-walkthroughs/
- [2] Jakob Nielsen — How Many Test Users in a Usability Study? (Nielsen Norman Group, 2012; opinion) — https://www.nngroup.com/articles/how-many-test-users/
- [3] Kerry Rodden, Hilary Hutchinson and Xin Fu — Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications (CHI, 2010; case) — https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/
- [4] Ron Kohavi, Roger Longbotham, Dan Sommerfield and Randal M. Henne — Controlled experiments on the web: survey and practical guide (Data Mining and Knowledge Discovery, 2009; research) — https://exp-platform.com/Documents/controlledExperimentDMKD.pdf
- [5] Natalia Amorim — Nobody watches their session replays (PostHog blog, 2026; case, by the tool's vendor) — https://posthog.com/blog/nobody-watches-session-replays
