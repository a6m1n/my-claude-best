# Skill designs

Nine Claude Code skills, and how each one works inside: the problem it solves,
when it is worth running, and its run drawn as a diagram with numbered arrows.

**Navigation**

- [What is here](#what-is-here)
- [How they fit together](#how-they-fit-together)
- [How each page is built](#how-each-page-is-built)
- [The demo pages](#the-demo-pages)

These pages describe a design, not a skill to install. One of the skills, meta-thinking, is
published in [skills/](../skills/); its page links it in the last section. Read a page when you want to build a similar skill, or to judge whether
such a process would help on your own work before you build anything.

## What is here

Each line says what the skill is for, then in one sentence how it works.

- [meta-thinking/](meta-thinking/README.md): thinks a large task through before any work starts.
  One fresh agent that can only read studies the task and the code, then you answer at most three
  questions and pick one route. Read it when large tasks go wrong halfway through. The skill is in
  [skills/meta-thinking/](../skills/meta-thinking/).
- [grill-me-v2/](grill-me-v2/README.md): pins down the requirements before anything is planned. It
  asks one question per message, in the order the decisions depend on each other, each with options
  and a recommendation, and looks up every fact instead of asking. Read it when a task is still
  vague and a wrong guess would be expensive.
- [create-ticket-v3/](create-ticket-v3/README.md): turns short notes into a Jira ticket, most
  often one user story. It shows the draft and every field with its source, offers a split when the
  notes hold several separate items, and creates the issues after your yes. Read it when writing
  tickets takes longer than the work they describe.
- [decompose-and-delegate/](decompose-and-delegate/README.md): answers a big question about the
  code. It splits the question into small ones, sends each to its own agent, and keeps only their
  answers with `file:line`. Read it when one session fills its context reading files.
- [settle/](settle/README.md): goes through an existing plan, ticket or doc with you, one open point
  at a time. Each point comes with options, pros and cons and a recommendation; your answers are
  recorded and applied at the end. Read it when a draft has open questions only you can answer.
- [debate-loop/](debate-loop/README.md): reviews a document, plan or prompt in rounds. Reviewers
  with different focus find problems, one agent fixes them, another checks the fixes, until the
  text does what you asked for. Read it when one review pass is not enough.
- [test-driven-development/](test-driven-development/README.md): builds a change test first. It
  picks which units earn a test, watches each new test fail for the right reason, then writes the
  smallest code that makes the whole fast suite pass. Read it when tests keep passing while the
  code is wrong.
- [delegate-task/](delegate-task/README.md): hands one decided task to a background agent with its
  own helpers and branch. Its report is checked against git before it counts. Read it when a long
  task should run beside your other work.
- [pr-review-with-auto-fix/](pr-review-with-auto-fix/README.md): reviews your own pull request with a planned team of
  reviewers. Every finding is checked at its line, and the fixes are proven by running the tests.
  Read it when AI review comments on your pull requests are hard to trust.

## How they fit together

One large piece of work can use the skills in turn. This is one way to combine them, not a rule;
each also works alone.

1. meta-thinking picks the route and settles the decisions that are yours.
2. grill-me-v2 pins down the requirements, one question at a time.
3. create-ticket-v3 writes the ticket from those notes.
4. decompose-and-delegate shows how the code works today.
5. settle walks through the open points of your draft plan with you.
6. debate-loop reviews the plan or draft, within a round limit.
7. test-driven-development builds each change test first.
8. delegate-task runs such a build in the background and checks the result against git.
9. pr-review-with-auto-fix reviews the pull request. You decide the merge.

## How each page is built

Every page uses these parts, in this order, and skips a part its skill does not need. A page adds
a section only when its skill needs one (such as which reviewers run, or what the report holds),
so you can compare two skills part by part:

| Part | What it answers |
| --- | --- |
| The problem it solves | What goes wrong without the skill |
| When to use it, when not to use it | The signs it helps, and the cases where something simpler does the job |
| How it works | A Mermaid diagram of the run, then the steps in order |
| What you are asked | When the skill stops for you, with an example question |
| Who does what | Each agent's role, what it sees and what it may not do |
| What makes it different | Each design choice with its reason |
| Where the skill is | Whether the skill is published here, and where |

A diagram shows the main path and the ways a run stops, in plain words with one example. A page
keeps the numbers that shape the design, such as how many reviewers run or how many rounds a run
allows. Thresholds and internal file names are left out, so a page stays true when the skill gets
a small fix.

## The demo pages

Each folder also has an `index.html` that shows the same design as one page, with the run drawn
as a coloured diagram with numbered arrows, easier to read than the Mermaid chart. [index.html](index.html) in this folder links
all of them. To see one as a page, clone the repository and open the file in a browser; it needs
no internet and loads no scripts. When you change a README here, change its
`index.html` in the same edit.
