# Component and hook practices

How to write one React component and one custom hook: the Rules of React that are not taste,
props as the component's signature, the state a component keeps, effects only for a system
outside React, the compiler in place of hand-written memoisation, and the common mistakes with
their fixes. It is the React case of [readability](../../any-language/readability/README.md).

**Navigation**

- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)

## What is here

- [components.md](components.md) — the rules, each labelled as a Rule of React, advice or taste,
  with bad and good examples; the effect lookup table; the common mistakes with the lint rule that
  reports each; then where the rules stop holding and a review checklist. Read it before you write
  or change a component or a custom hook, and when you review one.
- [component-example.md](component-example.md) — one module of a billing screen written to every
  rule except the component tests: a pure rule and its test, a badge, a list that takes its link as
  a prop, the route that feeds it, and a form that reads with a suspense query and writes with a
  mutation, with the reason next to each part. Read it when you write the components of a new
  module.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/react/components/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you write or change a React component
   or a custom hook, and when you review one, read
   `docs/engineering/react/components/components.md`." Without it an agent never opens the file.
3. Turn on the React Compiler, and a linter that reports the Rules of React and the compiler's
   diagnostics as errors in CI. [libraries.md](../architecture/libraries.md) names the tools and
   which rule runs where; [layout-example.md](../architecture/layout-example.md) shows the
   configuration. Without the lint, section 2 of the rules lives in review alone, and the compiler
   skips a broken component without a word.
4. Use section 12's checklist as the component part of your review template, so a reviewer asks
   the same questions every time.
5. The practice links [readability.md](../../any-language/readability/readability.md),
   [file-structure.md](../../any-language/file-structure/file-structure.md),
   [refactoring.md](../../any-language/refactoring/refactoring.md),
   [architecture.md](../architecture/architecture.md),
   [libraries.md](../architecture/libraries.md), [accessibility.md](../design/accessibility.md),
   [ux.md](../design/ux.md), [security.md](../security/security.md) and
   [performance.md](../performance/performance.md) for the rules they own. Copy those folders too,
   or replace each link with your own rule for that topic.
6. Re-check the lines that name a moving target. List them with
   `grep -rnE '2026-10-0[12]' docs/engineering/react/components/`. Each was read on 2026-10-01 or 2026-10-02. Check
   them on the day you adopt the folder, and again by 2027-04-01, six months after the reading;
   after that date, distrust every dated line until it is read again.

## The points to adapt

Every rule labelled Taste is yours to change: props typed on the parameter rather than with
`React.FC`, `type` or `interface` for props, one exported component per file, named exports. Pick
once and keep the choice across the code base. The Advice rules give way where your team can name
what its case gains, such as a hand-written `useCallback` for a library that compares functions
by identity. What does not change are the Rules of React in section 2 or 9: React depends on them,
and the compiler skips a component that breaks one.

The rules for testing a component are not a practice yet. [libraries.md](../architecture/libraries.md)
section 6 gives the tools and a minimum, and the reference application's only tests are its two
rule files' tests; [component-example.md](component-example.md) shows one of them.
