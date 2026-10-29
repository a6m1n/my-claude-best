# Evaluating an interface: reviews, tests with users and measures in production

This file is for everyone who has to say whether an interface works for the people who use it: a
developer, a designer, a product owner, a researcher, and an AI agent asked to "check the
usability". It says which level of evaluation to run now, with how many people, what to measure,
and what each method cannot tell you. What users do in the product, as events, page views,
heatmaps and replays, is [behaviour-analytics.md](behaviour-analytics.md). The rules were written
for the screens of web applications (lists, forms, dashboards, settings, editors); native apps are
out of scope.

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. Three levels, and which fits when](#2-three-levels-and-which-fits-when)
- [3. Expert review: heuristics and the cognitive walkthrough](#3-expert-review-heuristics-and-the-cognitive-walkthrough)
- [4. Tests with users: rounds, people, tasks and measures](#4-tests-with-users-rounds-people-tasks-and-measures)
- [5. Questionnaires: SEQ, SUS and UMUX-LITE](#5-questionnaires-seq-sus-and-umux-lite)
- [6. Benchmarks and sample sizes](#6-benchmarks-and-sample-sizes)
- [7. People with disabilities among the participants](#7-people-with-disabilities-among-the-participants)
- [8. Metrics in production: goals, signals, metrics](#8-metrics-in-production-goals-signals-metrics)
- [9. Surveys inside the product](#9-surveys-inside-the-product)
- [10. A/B tests](#10-ab-tests)
- [11. Synthetic users and a model as a reviewer](#11-synthetic-users-and-a-model-as-a-reviewer)
- [12. Judging an effective, a polished and a balanced interface](#12-judging-an-effective-a-polished-and-a-balanced-interface)
- [13. Participants' personal data](#13-participants-personal-data)
- [14. Common mistakes](#14-common-mistakes)
- [15. Where the rules stop holding](#15-where-the-rules-stop-holding)
- [16. Alternatives considered](#16-alternatives-considered)
- [17. Adoption in existing work](#17-adoption-in-existing-work)
- [18. How an agent applies it](#18-how-an-agent-applies-it)
- [19. Review checklist](#19-review-checklist)
- [20. Sources](#20-sources)

## 1. Purpose and the one rule

A team can build a screen and still not know whether people can use it. A screenshot, a rating,
an expert's opinion or a model's review each look like evidence, and none of them shows what a
person does with the screen on a real task. A project that follows this file runs the level of
evaluation each screen's stage needs, names in every finding who did what, and claims that a
change helped only when a measure shows it.

The one rule: **say that an interface works only when people did real tasks with it, watched in a
test or measured in production. An expert review, a model or a rating finds problems to look at;
it never settles them.**

Why it holds the rest together:

- The standard for human-centred design puts evaluation with users at the centre: "Evaluating
  designs with users and improving them based on their feedback provides an effective means of
  minimizing the risk of a system not meeting user or organizational needs" (ISO 9241-210, read
  in the free preview of the paid standard) [1].
- NN/g, which teaches both review methods, says so about each. Kim Flaherty: "a
  cognitive walkthrough should not be the only evaluative technique applied to a new interface"
  [2]. Kate Moran and Kelley Gordon of NN/g: "heuristic evaluations cannot replace user research"
  [3].
- Ratings follow looks more than performance, and a model's review reports problems that are not
  there (sections 11 and 12).

What it leaves out on purpose, and where that lives:

- The heuristics as a reviewer's lens: [ux.md](../../react/design/ux.md) section 9.
- The automated accessibility checks and the manual pass:
  [accessibility.md](../../react/design/accessibility.md) sections 10 and 11.
- The loop in which a coding agent's screen is reviewed before merge:
  [designing-with-claude-code.md](../../react/design/designing-with-claude-code.md) section 6.
- Events, page views, consent for tracking, heatmaps and replays:
  [behaviour-analytics.md](behaviour-analytics.md).
- Security: there are no known security impacts of the methods in this file beyond two that other
  rules own. A survey or an A/B testing tool loaded into the product is a third-party script
  ([security.md](../../react/security/security.md) section 12), and participants' recordings and
  notes are personal data (section 13).

Not covered yet, because the research found no source it could read (section 15 gives the detail):
numbers on response bias in surveys inside a product, a sample size for unmoderated tests, pass or
fail criteria and a stopping rule for a round, the full texts of ISO 9241-210 and 9241-11,
UMUX-LITE on its own, ISO/IEC 25062, the five-user paper and Faulkner's full text, the rest of
WAI's notes on testing with disabled participants, and how long to keep recordings.

## 2. Three levels, and which fits when

ISO 9241-210 names three kinds of user-centred evaluation in its table of contents:
inspection-based evaluation, user-based testing and long-term monitoring [1]. Only the headings
could be read, since the text of that clause is not in the free preview; this file uses the same
three levels and takes their rules from the sources below.

| Level | What it answers | Use it when | It is too much when | Who, and how many |
|---|---|---|---|---|
| Expert review (section 3) | Which glaring problems does the screen have? | every new or changed screen, before it ships | never as the only level for a new interface [2], [3] | 3 to 5 evaluators who work alone [3] |
| Tests with users (sections 4 to 7) | What goes wrong when real people do real tasks, and why? A benchmark: is it easier than before, and by how much? | while the interface changes; a benchmark when you must show progress | a benchmark, when you only need to know what is wrong (section 6) | 4 to 8 people a round [4]; 30 to 60 for a benchmark [19] |
| Measures in production (sections 8 to 10) | Does it work at scale: who finishes, who drops out, what changed after a release? | once the interface is live and has users | before launch, when there is nothing to measure [21] | everyone who uses it; "hundreds" for surveys and A/B tests [4] |

- **Before you pick a method, write the question the evaluation must answer and the decision it
  feeds.** GOV.UK asks each round's objectives to say "what you need to know now to be able to
  make an informed decision about what to do next" [12]. A method picked first answers a question
  nobody asked.
- **Pick the level by the question.** "What is wrong, and why?" is a review, then a round of
  tests. "Is it better than last release, and by how much?" is a benchmark. "Which of two built
  versions moves the metric?" is an A/B test. Kate Moran of NN/g: "Qualitative usability testing
  is best for discovering problems in the user experience" and "Quantitative usability testing is
  best for collecting benchmarks" [10].
- **Start with this default, and change it only for a reason section 15 names:** an expert review
  on every new or changed screen, a round of tests with 4 to 8 people while the interface changes,
  and measures in production once it is live. GOV.UK's Service Manual asks a service team to "Aim
  to do at least one round of research every 2 weeks" [4]. The three levels find different
  things, so each one covers what the one before cannot see.

## 3. Expert review: heuristics and the cognitive walkthrough

An expert review is a person, or several, who inspects the screen without users. It is cheap and
fast, and it finds the obvious problems so that the test with users can find the rest.

The heuristic review:

- **Run a heuristic review on every new or changed screen before it ships, with the questions of
  [ux.md](../../react/design/ux.md) section 9.** Moran and Gordon hold that "Heuristic evaluations
  are useful for identifying glaring problems in an interface", and that they are "particularly
  helpful early in the design process" [3].
- **Set a narrow scope and a timebox of about one to two hours.** "The narrower the scope, the
  easier and more detailed the evaluation will be", and "We recommend reserving about 1–2 hours"
  [3].
- **Use three to five evaluators, each working alone, and let nobody see another's notes until
  all are done; then merge the lists.** "Ideally, three to five people should independently
  evaluate the same interface" [3]. Each evaluator misses problems that another finds, and Moran
  and Gordon keep the notes apart until every evaluator is done [3]. A team with one reviewer
  still runs the review; it knows the list is shorter than it would be.
- **Then have three evaluators rate the severity of each problem on the merged list, each on their
  own, on the 0 to 4 scale of section 4, and use the mean.** Jakob Nielsen, writing on severity
  ratings in heuristic evaluation, holds that "severity ratings from a single evaluator are too
  unreliable to be trusted", and that "using the mean of a set of ratings from three evaluators is
  satisfactory for many practical purposes" [40]. Each evaluator, he adds, "should provide
  individual severity ratings independently of the other evaluators" [40].

The cognitive walkthrough:

- **Run a cognitive walkthrough when new users must learn a workflow that is new, complex or
  unfamiliar.** Flaherty describes it as "a technique used to evaluate the learnability of a
  system from the perspective of a new user", and holds that "they’re most effective for systems
  with complex, new, or unfamiliar workflows and functionalities" [2].
- **Skip it on a screen built from standard patterns.** For a site for the general public "that
  correctly employs standard design patterns", Flaherty calls it "overkill" [2]. An invoices table
  with a pay link gets the heuristic review; a new reconciliation flow gets the walkthrough.
- **Run it as a workshop: define the tasks and the correct steps first, then ask four questions
  at each step.** The team has a facilitator, evaluators and a recorder. At each step it asks:
  "Will users try to achieve the right result?", "Will users notice that the correct action is
  available?", "Will users associate the correct action with the result they’re trying to
  achieve?" and "After the action is performed, will users see that progress is made toward the
  goal?" One "No" marks the step as failed [2]. The page gives no number of evaluators.

Neither review replaces a test with users [2], [3]. A model as the reviewer is section 11.

## 4. Tests with users: rounds, people, tasks and measures

A usability test gives representative people representative tasks and watches what they do.
Jakob Nielsen sums up a basic think-aloud test: "Recruit representative users. Give them
representative tasks to perform. Shut up and let the users do the talking" [9]. The rules below
follow the order of the work. A plan that follows them is
[test-plan-example.md](test-plan-example.md).

Plan and recruit:

- **Write the plan of each round before you recruit.** It holds the objectives, the participants,
  the tasks, the measures, the session times, recording and note-taking, and time for analysis:
  the parts GOV.UK's "Plan a round of user research" and "Using moderated usability testing" list
  [12], [11], and Digital.gov's research plan, which adds roles, a timeline and "any legal,
  ethical, accessibility, bias, or power concerns raised by the research plan and how the team will
  mitigate them" [13].
- **Test with 4 to 8 people a round, and run more rounds rather than one big round.** GOV.UK:
  "You’ll usually need between 4 and 8 participants for each round using methods like experience
  mapping, contextual research, in-depth interviews or usability testing", and "If you need more
  participants to get clear findings, do more rounds rather than one big round" [4]. Why not one
  round of five: Nielsen's model has five users find about 85% of the problems, with "The typical
  value of L is 31%", the share of users who meet a given problem, "averaged across a large number
  of projects we studied" [5]; those projects date from the early 1990s [7]. Laura Faulkner
  tested 60 users and drew random sets from them: "Some of the randomly selected sets of 5
  participants found 99% of the problems; other sets found only 55%" (abstract only) [6]. One
  round of five can miss almost half of the problems; the next round, after the fixes, finds what
  the first one missed.
- **When the interface is mature or the problems are rare, add people by adding rounds.** Raluca
  Budiu of NN/g: with L at 10%, the model needs 18 users to find 85% of the problems, and "If your
  interface has already gone through many rounds of testing, you may need to include more people
  even in a qualitative test" [7]. Spread those people over more rounds of 4 to 8, as GOV.UK asks
  [4].
- **When the users fall into distinct groups, test each group.** "The formula only holds for
  comparable users who will be using the site in fairly similar ways"; Nielsen suggests "3–4 users
  from each category if testing two groups" and "3 users from each category if testing three or
  more groups" [5].
- **Recruit actual or likely users, and start at least a week before the sessions.** GOV.UK:
  "Start recruiting participants at least a week before a research session" [12].

Tasks and sessions:

- **Write each task as a goal the participant wants, never as the steps or the words on the
  screen.** GOV.UK: "Good test tasks: set a clear goal for participants to try and achieve; are
  relevant and believable to participants; are challenging enough to uncover usability issues; do
  not give away ‘the answer’ or hint at how a participant might complete them" [11]. Moran: "Small
  errors in the phrasing of a task can cause the participant to misunderstand what they’re asked to
  do or can influence how participants perform the task" [10]. A task that says "click Pay" tests
  reading, not the screen.
- **Write down, for each task, what counts as success before the first session.** Success is the
  measure of effectiveness below, and a definition written after watching bends to what people
  did. No source read gives a form for it; the form in the example is this practice's choice.
- **Moderate the sessions by default, with the participant thinking aloud.** GOV.UK: "Moderated
  usability testing is most useful in the alpha, beta and live phases to test prototypes or the
  service you’ve built" [11]. Train the facilitator, or pair a new one with someone who has run
  sessions: "from an untrained facilitator, such interruptions can very easily change user
  behavior" [9]. In an unmoderated test a tool gives written tasks and the participant works alone
  [10]; nobody can ask why. Use it for a few focused tasks, to find problems from the recordings or
  to measure (section 6), and moderate when you need to ask why or to review a whole flow. Amy
  Schade of NN/g holds that "it is preferable to use unmoderated remote usability tests when the
  main focus of the study is a few specific elements, rather than an overall review" [42]. Kathryn
  Whitenton of NN/g writes tasks differently "depending on whether you’re doing a qualitative or
  quantitative study", and for qualitative data "you’ll need to review each session recording"
  [41].
- **Make the prototype work end to end, and run the tasks yourself the day before.** GOV.UK: "Your
  prototype or beta service needs to work from end-to-end and be usable and accessible from the
  research venue. Run through the test tasks on the day before the research" [12]. Its plan also
  has a practice session with a member of the team [12].
- **Keep sessions to 30 to 60 minutes, and plan no more than six one-hour sessions a day.**
  GOV.UK: "Plan for no more than 6 one-hour sessions a day and allow at least 15 minutes between
  sessions, plus additional time for lunch" [11].
- **Get the whole team to watch.** GOV.UK: "everyone should observe at least 2 hours of research
  every 6 weeks" [4]. A team that saw a participant fail argues less about the fix.

Measures:

- **Measure each task for effectiveness, efficiency and satisfaction, the three parts of ISO's
  definition of usability.** ISO 9241-11 defines usability as the "extent to which a system,
  product or service can be used by specified users to achieve specified goals with effectiveness,
  efficiency and satisfaction in a specified context of use" (read in the free preview of the
  paid standard, which holds the definitions only) [14]. Effectiveness is "accuracy and
  completeness with which users achieve specified goals": task success and errors. Efficiency is
  "resources used in relation to the results achieved", and the standard names time as a typical
  resource: time on task. Satisfaction is the participant's response: the question after each task
  in section 5 [14].
- **Name the users, the goals and the context with every result.** ISO: "Usability, as defined in
  this document, is not an attribute of a product" [14]. "Clerks found the overdue invoices" is a
  result for clerks on that task, not a property of the screen.
- **In a round of 4 to 8, report the measures as counts, not as scores.** Write "3 of 5 found the
  overdue invoices", never "60% success". Nielsen on thinking aloud: "the method doesn't lend
  itself to detailed statistics, unless you run a huge, expensive study" [9], and Jeff Sauro and
  Joseph Dumas found that "below 10 participants, none of the question types have high detection
  rates nor do the common post-test questionnaires" [16]. Numbers to compare need a benchmark
  (section 6).
- **Plan the analysis before the sessions, at twice their time.** Digital.gov: "a safe estimate is
  twice as long as you give to data collection" [13]. Findings written the week after the sessions
  lose what nobody noted.
- **Rate each finding's severity on Nielsen's scale of 0 to 4 the way section 3 rates a heuristic
  review's list: three people, each on their own, and the mean. Fix the most severe first.** Jakob
  Nielsen holds that "The severity of a usability problem is a combination of three factors": how
  often it occurs, how hard it is to overcome, and whether it keeps bothering users [40]. His scale
  runs from "0 = I don't agree that this is a usability problem at all" to "4 = Usability
  catastrophe: imperative to fix this before product can be released" [40]. He wrote the advice on
  three raters for heuristic evaluation (section 3); rating a test's findings the same way is this
  practice's choice.

## 5. Questionnaires: SEQ, SUS and UMUX-LITE

A questionnaire turns what a participant felt into a number. Each one below has a moment, and a
sample below which its number means little.

The Single Ease Question (SEQ), after each task:

- **Ask it right after each task, then ask why.** NN/g's glossary gives the wording: "Overall, how
  difficult or easy did you find this task", answered "on a scale from 1 (very difficult) to 7
  (very easy)" [15]. The low answer points at the task to talk about.
- **Know what it rests on.** The SEQ is a later, widely used form of the seven-point Likert
  question that Sauro and Dumas compared with two other one-question ratings, with 26 participants
  who did the same five tasks in two applications; they found it "was easy for participants to
  use, was highly correlated with other measures" [16]. The name SEQ comes from later practice,
  not from that paper [15].
- **Do not read it as satisfaction with the product, and do not compare it under ten people.**
  The authors: "It does not measure overall satisfaction with a product", and below ten
  participants none of the ratings they tested detected differences well [16].

The System Usability Scale (SUS), after all tasks:

- **Give it after the participant has used the system and before any debrief, and ask for a
  quick answer to every item.** John Brooke, who wrote it: it "is generally used after the
  respondent has had an opportunity to use the system being evaluated, but before any debriefing or
  discussion takes place", and "All items should be checked. If a respondent feels that they
  cannot respond to a particular item, they should mark the centre point of the scale" [17].
- **Score it as Brooke says, and report only the total.** "For items 1,3,5,7,and 9 the score
  contribution is the scale position minus 1. For items 2,4,6,8 and 10, the contribution is 5
  minus the scale position. Multiply the sum of the scores by 2.5 to obtain the overall value of
  SU" [17]. "Note that scores for individual items are not meaningful on their own" [17].
- **Compare a SUS score only with the same product or a product for the same purpose, measured the
  same way.** Brooke calls it "quick and dirty": there are no absolute measures of usability, and
  he advises against comparing systems built for different purposes [17]. Keep one version of the
  items across rounds: the paper on UMUX-LITE names two, the standard one with mixed tone and an
  all-positive one [18].
- **Use it in a benchmark (section 6), not in a round of 4 to 8.** With fewer than ten people the
  common post-test questionnaires do not detect differences well [16].

UMUX-LITE, only beside the SUS:

- **Never give UMUX-LITE in place of the SUS.** It has two items, "This system’s capabilities meet
  my requirements" and "This system is easy to use", on seven-point scales, and a regression maps
  it onto the SUS: "UMUX-LITE = .65(UMUX(1,3)) + 22.9" [18]. James Lewis, Brian Utesch and Deborah
  Maher found reliability of ".82 and .83" and a correlation with the SUS of ".81, .81", in two
  surveys of IBM employees [18]. Their own conclusion: "Until researchers have validated the
  UMUX-LITE across a wider variety of systems, we do not recommend its use independent of the SUS"
  [18]. Whether later work lifted that limit was not checked (section 15).

## 6. Benchmarks and sample sizes

A benchmark repeats the same tasks and questions with enough people to give numbers you can
compare: this release against the last one, or your product against another.

- **Run a benchmark when you must show whether the interface got easier, and by how much.** A
  round of 4 to 8 shows what is wrong; it cannot show that a change helped (section 4).
- **Report each benchmark number with its confidence interval, and size a comparison before it
  runs.** Jeff Sauro and Jim Lewis's tables put the margin of error of a completion rate, at 90%
  confidence, at 14% with 32 people and 11% with 54 [39]. Use 90% confidence, the level of those
  tables. For a completion rate, use the adjusted Wald interval: Sauro's page for MeasuringU's
  completion-rate calculator holds that "The Adjusted Wald method should be used almost all the
  time" [43]. For time on task, report the geometric mean with an interval worked out on the log of
  the times: Sauro computes task-time intervals with "t-statistics instead of the normal deviate",
  and graphs the times "in log-transformed seconds", with "the geometric mean" and its interval
  [44]. To compare a design with an earlier one or a competitor's with different people in each
  study, Sauro and Lewis advise "a sample size of 213 in each group for a between-subjects study or
  93 total for a within-subjects study" to detect differences of 12% or more; a difference of 20%
  needs 75 in each group [39]. So two benchmarks of 30 to 60 different people show only large
  changes, and the same people on both versions need fewer than two separate groups: 93 in all for
  a difference of 12% [39].
- **Keep the tasks and the questions the same in every round.** GOV.UK: "maintain consistency -
  it’s easier to compare results if you keep the tasks and questions the same for each round"
  [19].
- **Give each participant no more than five tasks of up to ten minutes each.** "A good rule of
  thumb is no more than 5 tasks per participant, with up to 10 minutes per task" [19].
- **Measure per task whether it was completed, how long it took, and whether the participant gave
  up or wrongly believed it was done; after each task, ask for a rating.** GOV.UK lists these
  measures, with ratings from 1 to 5 of how easy the task was, how confident the participant is,
  and whether it took more or less time than expected [19]. Add the SUS after the tasks
  (section 5).
- **Run it remotely.** GOV.UK: "It’s usually best to run usability benchmarking remotely" [19].
- **Recruit 30 to 60 actual or likely users.** GOV.UK's page on usability benchmarking: "Aim to
  recruit 30 to 60 actual or likely users of your service" [19]. The sources disagree; of those
  cited here, Sauro and Lewis give the method behind their figures: margins of error at 90%
  confidence for a completion rate of 50% [39]. GOV.UK's planning page puts benchmarking with surveys and A/B
  tests under "hundreds of participants" [4]. NN/g recommends "usually more than 30" (2021) [7];
  in 2012 Nielsen wrote "Test at least 20 users to get statistically significant numbers; tight
  confidence intervals require even more users" [8]. This file takes 30 to 60, the figure of
  GOV.UK's page on usability benchmarking [19], and the newer NN/g figure agrees with its lower
  end. At 90% confidence, Sauro and Lewis's table gives a completion rate a margin of error of
  about 15% at 30 people and 11% at 54, and they plan 65 people for a margin under 10% [39]. The
  "hundreds" figure is recorded in section 16.

How many people each method needs, from the sources this file rests on:

| Method | People | Source |
|---|---|---|
| Heuristic review | 3 to 5 evaluators, each working alone | [3] |
| Cognitive walkthrough | a team: facilitator, evaluators, recorder; no number given | [2] |
| Round of tests with users | 4 to 8 a round; more rounds, not a bigger round | [4] |
| Two or more distinct user groups | 3 to 4 per group for two groups; 3 per group for three or more | [5] |
| Benchmark | 30 to 60 | [19] |
| Survey in the product, A/B test | "hundreds"; for an A/B test, compute it (section 10) | [4], [28] |
| People with disabilities | a few, in every round when the audience is broad | [20], [4] |
| Very low-overhead project | "as few as 2 users per study" | [8] |

## 7. People with disabilities among the participants

- **Include people with disabilities among the participants, as W3C WAI advises.** WAI does not
  require it; it advises it, because "Evaluating with users with disabilities and with older users
  identifies usability issues that are not discovered by conformance evaluation alone" [20].
- **When the audience is broad, include them in every round; when it is small or specialist, plan
  rounds of their own.** GOV.UK: "If your service has a broad audience, you should include
  disabled users and people who may need support to use your service in every round of research.
  This may not be possible for smaller or more specialist user groups. In this case, plan specific
  rounds of research" [4].
- **Remove the obvious barriers first, and test early and often rather than once at the end.**
  WAI advises an expert review before involving users, and "Conducting informal evaluations
  throughout development is more effective than only formal usability testing at the end of a
  project" [20]. The checks and the manual pass that remove the obvious barriers are
  [accessibility.md](../../react/design/accessibility.md) sections 10 and 11.
- **Let a participant who uses assistive technology use their own device.** GOV.UK: "it’s usually
  best if participants can use their own devices" [11]. A screen reader set up by someone else
  tests the set-up, not the screen.
- **Never generalise from one or two people.** WAI: "Avoid assuming that input from one person
  with a disability applies to all people with disabilities", and "Results from only a couple of
  people with disabilities cannot be generalized" [20]. Report the scope and the participants'
  characteristics with the findings [20].
- Combine both. WAI: user involvement "alone cannot determine if a website is accessible. Combine
  user involvement with evaluating conformance to WCAG" [20].

## 8. Metrics in production: goals, signals, metrics

Once the interface is live, its users produce data every day. A metric picked because a tool
offers it measures what the tool can count, not what the product is for.

- **Write the goal first, then the signals that would show it, then the metrics.** Kerry Rodden,
  Hilary Hutchinson and Xin Fu, from their work on Google's products, describe "a simple process
  that steps teams through articulating the goals of a product or feature, then identifying
  signals that indicate success, and finally building specific metrics to track on a dashboard"
  [21].
- **Use the HEART categories as a list to choose from, not a form to fill.** The categories are
  "Happiness, Engagement, Adoption, Retention, and Task success" [21]. "It is not always
  appropriate to employ metrics from every category, but referring to the framework helps to make
  an explicit decision about including or excluding a particular category" [21]. In work software,
  drop Engagement: it "may not be meaningful in an enterprise context, if users are expected to use
  the product as part of their work" [21].
- **Take the signals from logs and from surveys.** "Logs and surveys are the two signal sources we
  have used most often" [21]. The events and their names are
  [behaviour-analytics.md](behaviour-analytics.md) section 3; the survey is section 9 here; page
  speed as users see it is [performance.md](../../react/performance/performance.md) section 3.
- **When a metric shows where people drop out, plan research to find out why.** GOV.UK: "your
  completion rate data can help you identify the stages in your user journeys when users are
  dropping out. Work with your user researcher and plan a round of user research to try to
  understand why" [22]. Rodden et al.: metrics "should be triangulated with findings from other
  sources", and "are not a substitute for early or formative user research" [21].
- **Under a regulator's rule, the rule sets the floor.** UK government services "must" collect
  cost per transaction, user satisfaction, completion rate and digital take-up [22]. A UK firm that
  serves retail customers falls under the FCA's PRIN 2A.5.10: "Where appropriate, a firm must: (a)
  test communications before communicating them to retail customers; and (b) (as set out in PRIN
  2A.9) regularly monitor the impact of the communications once they have been communicated" [23].

## 9. Surveys inside the product

- **Ask after the user has finished a real task, and keep it to about a minute.** Anna Kaley of
  NN/g: "Wait until after users complete a real task to ask for feedback", and "A feedback survey
  should take around 1 minute to complete. In our research, we commonly saw timeframes of 2–3
  minutes, which are too long for users" [24]. She puts an optional comment field at the end [24].
- **Never let the survey be the only feedback.** Kaley: the survey "shouldn’t be the only way you
  get feedback; use the findings to direct and prioritize in-depth user research" [24].
- **Read a score that drops right after a change with care: the people who answer change too.**
  Weitao Duan and Qian Weng, describing LinkedIn's survey system: "users who respond can be quite
  different from users who do not respond", and "users who do not like changes are more likely to
  respond to surveys in the new version than in the old version" [25]. Check a drop against the
  task measures of section 8 before you act on it. How large the bias is inside a product is not
  covered yet (section 15).
- **Never use the Net Promoter Score (NPS) alone, and never on a small sample.** Therese Fessenden
  of NN/g: "NPS is a loyalty metric that correlates well with perception of usability, is easy to
  understand and administer, but has limitations for understanding and evaluating UX when used in
  isolation", and "NPS is relevant only with a large enough sample size" [26]. "While loyalty and
  usability are well correlated, they are not exactly the same" [26]. Put it beside the SUS or the
  task measures: "when combined with other UX metrics, NPS can help you track the overall
  perception of your user experience over time" [26]. Susana Jaramillo et al. found, about firms'
  results rather than interfaces, that "customer satisfaction explains slightly more variance"
  in financial performance than NPS (abstract only) [27].
- A survey tool loaded into the page is a third-party script:
  [security.md](../../react/security/security.md) section 12.

## 10. A/B tests

An A/B test shows each user one of two built versions and compares a metric between the groups.
It is the one method here that shows cause, and it needs both versions built and many users.

- **Before you start, compute how many users each version needs.** Ron Kohavi, Roger Longbotham,
  Dan Sommerfield and Randal Henne give "a calculation for the minimum sample size, assuming the
  desired confidence level is 95% and the desired power is 80%": `n = 16 × σ² / Δ²` users per
  version, where σ² is the variance of the metric and Δ the smallest change you want to detect
  [28]. The change is squared, so halving it needs four times the users; in their example,
  detecting a 20% change in conversion instead of a 5% one needs 16 times fewer users, 7,600 [28].
  For 90% power they replace 16 with 21 [28].
- **When your traffic cannot reach that number in a few weeks, do not run the test.** Test the
  versions with people instead (section 4 or 6). GOV.UK expects "hundreds of participants" for A/B
  tests [4].
- **Run it long enough for novelty to wear off, which can take weeks.** Kohavi et al. warn of
  primacy and newness effects, and that "some experiments need to be run for multiple weeks" [28].
- **Expect most ideas to fail.** Kohavi, Diane Tang and Ya Xu report, from Kohavi, Crook and
  Longbotham's 2009 paper: "Only one third of the ideas tested at Microsoft improved the metric(s)
  they were designed to improve", and in "well-optimized domains like Bing and Google" some
  measures' success rate is about 10–20% [29]. A team that tests one idea and ships it when it wins has not yet seen the
  ideas that lose.
- **Pair it with research when you need to know why.** Kohavi et al.: "Quantitative metrics, but
  no explanations. It is possible to know which variant is better, and by how much, but not
  “why.”" [28]. A round of tests with users on the winning and the losing version supplies the why.
- The testing tool's script in the page is a third-party script:
  [security.md](../../react/security/security.md) section 12.

## 11. Synthetic users and a model as a reviewer

Two different uses of a language model sit under this heading. A synthetic user is a model that
plays a participant. A model reviewer inspects a screen as an expert would. The studies below
measured different things, so each rule names the one it rests on.

What was measured:

- **A model as a heuristic reviewer.** Zhong, McDonald and Hsieh gave GPT-4 screenshots of two
  mobile apps and found that "our evaluation identified 73% and 77% of usability issues, which
  exceeded the performance of 5 experienced human evaluators (57% and 63%)" (arXiv preprint, v1)
  [32]. Their list of problems pooled what the model and the experts reported. The same study shows
  the cost: of the 147 items in its table that the authors rated at severity 0 on Nielsen's scale,
  "I don’t agree that this is a usability problem at all.", GPT-4 reported 95 and the five experts
  together 9 [32]. The authors rated the severity themselves, not the experts. The table's 147 is
  the 104 items of the authors' first analysis plus 43 that Gemini and Claude reported, which the
  authors added in section 5.1 [32].
- **A model measured against the experts' own list** is the study
  [designing-with-claude-code.md](../../react/design/designing-with-claude-code.md) section 6
  cites. Zhong et al.'s baseline was the pooled list, so the two studies answer different
  questions and their figures cannot be set against each other.
- **A model as a participant.** Eduard Kuric, Peter Demcak and Matus Krajcovic compared first
  clicks predicted by GPT models with those of real people, in "twelve diverse first click tests
  (n = 3431) obtained from real UX practice", 45 tasks in all (arXiv preprint, v1) [33]. GPT-4.1's
  clicks had a significantly different distribution from people's in 53% of the tasks; GPT-5.2 with
  medium reasoning differed in 44%, a change from GPT-4.1 that was not significant [33]. The study
  is about predicting what participants do, not about reviewing a screen.
- **What the method's practitioners hold.** Maria Rosala and Kate Moran of NN/g, who tried one
  synthetic-user product: synthetic users "often provide shallow or overly favorable feedback";
  "Do not use synthetic-user research as a replacement for real-user research"; they are "useful
  for desk research and generating hypotheses, but not for final decision-making" [30]. They report
  that Jeff Sauro and colleagues found ChatGPT "was not an acceptable replacement for real users in
  tree testing, because it vastly outperformed most real people" [30].

The rules:

- **Never count a synthetic user as a participant, and never report its answers as findings about
  users.** This rests on Kuric et al. [33] and on Rosala and Moran [30]. Use a model for desk
  research, for hypotheses, and to draft research goals, tasks and survey questions, which Moran
  and Rosala list among the uses that work [31]; a person checks each draft task against
  section 4.
- **Treat a model reviewer's list as a first pass, and let a person decide which items are real
  before any reaches the backlog.** This rests on Zhong et al., where many of the model's items
  were no problem at all and the model still missed 27% and 23% of the pooled list [32]. Like a
  heuristic review (section 3), the list holds candidates; a test with users settles them
  (section 1). The loop in which a reviewer subagent judges a screen a coding agent built is
  [designing-with-claude-code.md](../../react/design/designing-with-claude-code.md) section 6;
  this file does not repeat it.
- **Do not let an AI tool moderate a session or judge from a recording what a participant did.**
  Moran and Rosala, in a page last reviewed on 2026-01-21: "Avoid using AI tools to moderate
  usability tests; AI research tools are not (yet) capable of actually knowing what users are
  doing" [31]. The claim is dated: re-check it when that page is reviewed again, or when a study
  with people measures an AI moderator. The same page holds that these tools "do much better with
  self-reported or attitudinal data gathered through methods like interviews, diary studies, and
  surveys" [31], so a model may summarise what participants said; a person reads the notes behind
  each summary line that becomes a finding.

## 12. Judging an effective, a polished and a balanced interface

[visual-design.md](../../react/design/visual-design.md) section 2 names three cases for a screen
in product mode: an effective interface, a polished one, and a balance of the two. This section
says how each is judged. The studies behind it, with each one's sample and limits, are in that
section; in short, looks raised ratings without raising task performance [34], [35] and can hide
problems in a test [36], while a whole redesign changed task time [37].

The rules:

| Case | Judge it by | Never by |
|---|---|---|
| Effective | task success and time on task, with errors (section 4) | ratings |
| Polished | the same task measures, no worse than the effective version, plus what people say: the SEQ and its "why", comments, the SUS in a benchmark | ratings alone: looks raise ratings without raising performance [35], and hide problems in a test [36] |
| Balance | both: the task measures on every task, including those that pass through an expressive moment; what people say about those moments | ratings alone |

- **When a polished version rates higher and its task measures are no better, report both
  numbers.** The rating is a real result about how people feel; it is not a result about whether
  they can do the task [34], [35].
- **Do not assume that expression speeds work up or slows it down; measure the case you built.**
  A whole redesign changed task time [37]; looks alone did not [34]. Which of the two your change
  is, only your measures show.
- **Compare two versions with benchmark numbers (section 6), not with a round of 4 to 8, and size
  the comparison before it runs.** A round shows where people struggle with the polished version;
  it cannot show that the polish cost or saved time (section 4). Two benchmarks of different people
  detect only large differences, so plan the people for the smallest difference that matters
  [39].

## 13. Participants' personal data

A test with users collects faces, voices, screens, names and what people say about their work.

- **Get informed consent before the session, and write in the plan how.** GOV.UK's "Plan a round
  of user research" names informed consent among what to settle when you find participants [12].
- **Write the plan's legal and ethical concerns, and how the team will handle them.** Digital.gov:
  "Note any legal, ethical, accessibility, bias, or power concerns raised by the research plan and
  how the team will mitigate them" [13].
- **Decide in the plan between real data and test data, and store real data securely.** GOV.UK
  prefers real data, since participants who work with made-up data are less engaged and uncover
  fewer problems that depend on their context, and it asks for personal data to be stored securely
  [11]. A test environment with real-looking records and invented names is a middle way: the
  records look like the participant's own work, and no customer's data leaves production.
- **Decide in the plan whether to record, and who takes notes** [12].
- **Name participants by an id (P1, P2) in notes, findings and anything you give a model.** This is
  the practice's own choice, not a source's: findings travel to tickets, backlogs and tools, and
  nobody needs a name to act on one.
- How long to keep recordings, the legal basis under a given law, and whether a transcript may go
  to a model provider's API are not covered yet (section 15); ask the person who owns data
  protection in your organisation. Personal data in analytics and replays is
  [behaviour-analytics.md](behaviour-analytics.md) section 5 and
  [security.md](../../react/security/security.md) section 13.

## 14. Common mistakes

| Mistake | What it costs | Fix |
|---|---|---|
| One round of five read as "all the problems found" | sets of five found from 55% to 99% of the problems [6] | rounds, section 4 |
| "60% success" or a SUS average reported from five people | below ten people the ratings do not detect differences [16]; the number looks like a result and is noise | counts, section 4; benchmark, section 6 |
| UMUX-LITE alone, in place of the SUS | its authors do not recommend it [18] | section 5 |
| NPS as the UX score | a loyalty metric, limited alone and on small samples [26] | section 9 |
| Synthetic users counted as participants | their clicks differ from people's [33]; feedback "overly favorable" [30] | section 11 |
| A model's review list pasted into the backlog | many of its items were no problem at all [32] | section 11 |
| An AI tool moderating a session | it cannot yet tell what users do [31] | section 11 |
| A polished screen judged by ratings | looks raise ratings, not performance [35], and hide problems [36] | section 12 |
| A cognitive walkthrough on a screen of standard patterns | "overkill" [2] | heuristic review, section 3 |
| Heuristic evaluators who see each other's notes | the review is no longer independent, as the method asks [3] | section 3 |
| A task that names the button or the steps | it tests reading, and primes the participant [10], [11] | section 4 |
| An A/B test on too little traffic, or read as "why" | a result that is noise, or a cause nobody knows [28] | section 10 |
| A survey before the user did anything, or one of three minutes | answers about no real task, or a survey users find too long [24] | section 9 |
| One disabled participant's result applied to all disabled users | "cannot be generalized" [20] | section 7 |

## 15. Where the rules stop holding

When a rule does not fit, and what following it costs:

- **A tool with a handful of users.** Test with the users you have. A benchmark and an A/B test
  cannot reach their numbers, and NN/g notes that "For really low-overhead projects, it's often
  optimal to test as few as 2 users per study" [8].
- **No traffic yet.** Measures in production and A/B tests wait for launch. Rodden et al. call
  metrics "primarily useful for evaluation of launched products" [21].
- **A small or specialist audience.** People with disabilities join rounds of their own rather than
  every round [4].
- **Work software.** Drop the Engagement category of HEART [21].
- **A regulated product.** The regulator's rule comes first; the rules here sit under it [23].
- **What it costs.** A round needs recruiting, sessions and analysis at twice the session time
  [13]; NN/g puts the simplest study at about three days for planning, five users and analysis
  [10]. A benchmark needs 30 to 60 people each time [19]. A team that cannot pay for rounds every
  two weeks runs fewer rounds, and keeps the review on every screen.

Not covered yet. The research for this file looked for these and found no source it could read:

- Numbers on response bias in surveys inside a product: one preprint describes it [25], and no
  study that measures it was found.
- A sample size for an unmoderated usability test from a standards body or the method's owner.
- Pass or fail criteria for a round, or a stopping rule, in a test plan: none of the plan
  templates read gives one.
- The text of ISO 9241-210 clause 7.5 (the evaluation methods) and of ISO 9241-11 Annex B (the
  measures): the standards are paid, and only their free previews were read [1], [14].
- Whether later work validated UMUX-LITE on its own, without the SUS [18].
- ISO/IEC 25062, the report format for usability tests: not searched.
- The paper behind the five-user model (Nielsen and Landauer, 1993) and the full text of
  Faulkner's study: read only through the restatements [5], [7] and the abstract [6].
- The rest of WAI's notes on how a test with disabled participants differs from a general one
  [20].
- How long to keep recordings, and whether a transcript may go to a model provider (section 13).

## 16. Alternatives considered

- **Two practices, one for evaluation and one for analytics.** GOV.UK gives user research and
  performance analysis roles of their own: the user researcher should "plan and carry out research
  using a range of methods", and the performance analyst helps the team understand user needs "by
  providing quantitative and qualitative evidence from web analytics, financial data and user
  feedback" [38]. Not taken: the split is of roles, not of documents, and GOV.UK's own guidance
  sends the analyst's numbers back to research for the why [22]. One practice keeps the two halves
  linked in one map; its `README.md` routes each role to its file.
- **A model as the only usability reviewer.** Zhong et al.'s headline result, more problems found
  than five pooled experts [32], argues for it. Not taken: the same study reports many items that
  are no problem at all and a model that still missed about a quarter of the pooled list, and the
  study is a preprint on two mobile apps with GPT-4 on screenshots (section 11).
- **Synthetic users in place of participants.** Not taken: Kuric et al. found model clicks that
  differ from people's in about half of the tasks [33], and NN/g advises against it [30].
- **NPS as the headline UX metric.** Not taken: NN/g calls it a loyalty metric that is limited
  alone and on small samples [26], and Jaramillo et al. found that satisfaction explains slightly
  more of firms' financial results (abstract only) [27].
- **"SUS or its two-item alternative".** A short questionnaire tempts a team that has no time for
  ten items. Not taken: UMUX-LITE's authors do not recommend it independent of the SUS [18].
- **"Hundreds" of participants for a benchmark** (GOV.UK's planning page) [4], and "at least 20"
  (NN/g, 2012) [8]. Not taken: 30 to 60 is the figure of GOV.UK's page on usability benchmarking
  [19], NN/g's newer "more than 30" agrees with it, and it gives a completion rate a margin of
  error of about 15% to 11% at 90% confidence [39] (section 6).
- **One round of five users.** Nielsen's model gives about 85% of the problems [5]. Not taken as a
  stopping point: Faulkner's sets of five found from 55% to 99% [6], and GOV.UK asks for more
  rounds instead of a bigger one [4].
- **An AI moderator.** Not taken, as of NN/g's review of 2026-01-21 [31]; section 11 says when to
  look again.

## 17. Adoption in existing work

The answer is **new and touched code** ([refactoring.md](../refactoring/refactoring.md)
section 7): the practice applies to the screens a change adds or changes, and an old screen moves
to it when a change touches it.

- A new or changed screen gets the heuristic review before it ships (section 3) and joins the
  next round of tests with users (section 4).
- A screen nobody touches waits; a team that wants to know where to start picks the screens where
  production data shows people dropping out (section 8).
- Measures in production start with the next change that touches the product's analytics
  ([behaviour-analytics.md](behaviour-analytics.md) section 12).
- A rule from a regulator (section 8) keeps the regulator's dates, whatever this section says.

## 18. How an agent applies it

The project's `CLAUDE.md` routes an agent here with the line in [README.md](README.md), "How to
adopt", step 2.

What an agent does in this work:

- **Draft; do not decide.** An agent may draft the plan, the tasks and the survey questions [31];
  a person checks each task against section 4 before recruiting starts.
- **Label every finding with its source:** a participant in a round, a heuristic review, a model
  reviewer, or production data. A finding from a model never reads as a finding about users
  (section 11).
- **Never say a test ran when none did.** A report that "users found the screen easy" needs the
  round it came from; a review by the agent itself is a review, not a test.
- **Do not moderate, and do not judge recordings** (section 11).

The mistakes agents make in this work, as the research found them: a model reviewer reports items
that are no problem at all [32], and a model's predicted clicks differ from people's [33]. The
mistakes an agent makes with analytics data are [behaviour-analytics.md](behaviour-analytics.md)
section 7.

## 19. Review checklist

One question per section, for a test plan, a report of findings, or a change that adds a survey,
an A/B test or a UX metric.

| Section | Ask | Red flag |
|---|---|---|
| 2. Levels | Does the plan name the question and the decision it feeds? | a method with no question; a new screen shipped with no review |
| 3. Expert review | Did evaluators work alone, within a scope and a timebox? | merged notes from the start; a walkthrough on a standard screen |
| 4. Tests with users | 4 to 8 people, tasks as goals, success defined before the sessions? | one round of five called complete; a task that names the button; percentages from five people |
| 5. Questionnaires | Is each questionnaire used at its moment and its sample size? | a SUS score from a round of five; UMUX-LITE alone; SUS item scores reported |
| 6. Benchmarks | Same tasks and questions as last time, 30 to 60 people, each number with its confidence interval, and a comparison of two versions sized before it ran? | changed tasks between rounds; a benchmark of eight people; two versions compared with no sample-size calculation |
| 7. Disabled participants | Are they in the round, or in a round of their own? | none in a service for a broad audience; one person's result applied to all |
| 8. Production | Goal, then signal, then metric? | a dashboard of what the tool counts; Engagement on work software |
| 9. Surveys | After a real task, about a minute, not the only feedback? | a survey on page load; NPS alone |
| 10. A/B tests | Was the sample size computed before the start? | a test stopped on the first good day; a winner read as "why" |
| 11. Models | Is every model finding labelled, and was it checked by a person? | synthetic users counted as participants; an AI moderator |
| 12. The three cases | Is a polished or balanced screen judged by task measures too? | ratings as the only evidence |
| 13. Personal data | Consent, ids, storage and recording decided in the plan? | names in the findings; recordings with no owner |

## 20. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] ISO — ISO 9241-210:2019, Ergonomics of human-system interaction, Part 210: Human-centred design for interactive systems, 2nd edition (free preview: contents, introduction, clauses 1 to 5) — https://cdn.standards.iteh.ai/samples/77520/8cac787a9e1549e1a7ffa0171dfa33e0/ISO-9241-210-2019.pdf
- [2] Kim Flaherty — Evaluate Interface Learnability with Cognitive Walkthroughs (Nielsen Norman Group, 2022; opinion) — https://www.nngroup.com/articles/cognitive-walkthroughs/
- [3] Kate Moran and Kelley Gordon — How to Conduct a Heuristic Evaluation (Nielsen Norman Group, 2023; opinion) — https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/
- [4] GOV.UK Service Manual — Plan user research for your service — https://www.gov.uk/service-manual/user-research/plan-user-research-for-your-service
- [5] Jakob Nielsen — Why You Only Need to Test with 5 Users (Nielsen Norman Group, 2000; opinion) — https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/
- [6] Laura Faulkner — Beyond the five-user assumption: benefits of increased sample sizes in usability testing (Behavior Research Methods, Instruments, & Computers, 2003; kind not confirmed) — https://pubmed.ncbi.nlm.nih.gov/14587545/
- [7] Raluca Budiu — Why 5 Participants Are Okay in a Qualitative Study, but Not in a Quantitative One (Nielsen Norman Group, 2021; opinion) — https://www.nngroup.com/articles/5-test-users-qual-quant/
- [8] Jakob Nielsen — How Many Test Users in a Usability Study? (Nielsen Norman Group, 2012; opinion) — https://www.nngroup.com/articles/how-many-test-users/
- [9] Jakob Nielsen — Thinking Aloud: The #1 Usability Tool (Nielsen Norman Group, 2012; opinion) — https://www.nngroup.com/articles/thinking-aloud-the-1-usability-tool/
- [10] Kate Moran — Usability (User) Testing 101 (Nielsen Norman Group, 2019; opinion) — https://www.nngroup.com/articles/usability-testing-101/
- [11] GOV.UK Service Manual — Using moderated usability testing — https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing
- [12] GOV.UK Service Manual — Plan a round of user research — https://www.gov.uk/service-manual/user-research/plan-round-of-user-research
- [13] U.S. General Services Administration, Digital.gov — How to write a research plan — https://digital.gov/resources/how-write-research-plan/
- [14] ISO — ISO 9241-11:2018, Ergonomics of human-system interaction, Part 11: Usability: Definitions and concepts, 2nd edition (free preview: introduction, scope, clause 3) — https://cdn.standards.iteh.ai/samples/63500/33c267a5a7564f298f02bbd65721a181/ISO-9241-11-2018.pdf
- [15] Raluca Budiu — Quantitative UX: Glossary (Nielsen Norman Group, 2023; opinion) — https://www.nngroup.com/articles/quant-ux-glossary/
- [16] Jeff Sauro and Joseph S. Dumas — Comparison of Three One-Question, Post-Task Usability Questionnaires (CHI, 2009; research) — https://measuringu.com/wp-content/uploads/2017/07/Sauro_Dumas_CHI2009.pdf
- [17] John Brooke — SUS: A quick and dirty usability scale (Usability Evaluation in Industry, Taylor & Francis, 1996; opinion) — https://hell.meiert.org/core/pdf/sus.pdf
- [18] James R. Lewis, Brian S. Utesch and Deborah E. Maher — UMUX-LITE: When There's No Time for the SUS (CHI, 2013; research) — https://iihm.imag.fr/coutrix/ens/M2-MoSIG-HiL/1stAssignment/UsabilityQuestionnaire/2470654.2481287.pdf
- [19] GOV.UK Service Manual — Usability benchmarking a website or whole service — https://www.gov.uk/service-manual/measuring-success/usability-benchmarking-a-website-or-whole-service
- [20] W3C Web Accessibility Initiative — Involving Users in Evaluating Web Accessibility — https://www.w3.org/WAI/test-evaluate/involving-users/
- [21] Kerry Rodden, Hilary Hutchinson and Xin Fu — Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications (CHI, 2010; case) — https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/
- [22] GOV.UK Service Manual — Using performance data to improve your service: an introduction — https://www.gov.uk/service-manual/measuring-success/using-data-to-improve-your-service-an-introduction
- [23] Financial Conduct Authority — FCA Handbook, PRIN 2A.5 Communications — https://handbook.fca.org.uk/handbook/PRIN/2A/5.html
- [24] Anna Kaley — User-Feedback Requests: 5 Guidelines (Nielsen Norman Group, 2023; opinion) — https://www.nngroup.com/articles/user-feedback/
- [25] Weitao Duan and Qian Weng — Scalable Online Survey Framework: from Sampling to Analysis (arXiv preprint, 2019; case) — https://arxiv.org/abs/1906.10082
- [26] Therese Fessenden — Net Promoter Score: What a Customer-Relations Metric Can Tell You About Your User Experience (Nielsen Norman Group, 2024; opinion) — https://www.nngroup.com/articles/nps-ux/
- [27] Susana Jaramillo, George Deitz, John D. Hansen and Emin Babakus — Taking the measure of net promoter score: An assessment of construct and predictive validity (International Journal of Market Research, 2024; kind not confirmed) — https://digitalcommons.memphis.edu/facpub2/182
- [28] Ron Kohavi, Roger Longbotham, Dan Sommerfield and Randal M. Henne — Controlled experiments on the web: survey and practical guide (Data Mining and Knowledge Discovery, 2009; research) — https://exp-platform.com/Documents/controlledExperimentDMKD.pdf
- [29] Ron Kohavi, Diane Tang and Ya Xu — Trustworthy Online Controlled Experiments, chapter 1 (Cambridge University Press, 2020; opinion) — https://experimentguide.com/wp-content/uploads/TrustworthyOnlineControlledExperiments_PracticalGuideToABTesting_Chapter1.pdf
- [30] Maria Rosala and Kate Moran — Synthetic Users: If, When, and How to Use AI-Generated "Research" (Nielsen Norman Group, 2024; opinion) — https://www.nngroup.com/articles/synthetic-users/
- [31] Kate Moran and Maria Rosala — Accelerating Research with AI (Nielsen Norman Group, 2024; opinion) — https://www.nngroup.com/articles/research-with-ai/
- [32] Zhong, McDonald and Hsieh — Synthetic Heuristic Evaluation: A Comparison between AI- and Human-Powered Usability Evaluation (arXiv preprint, 2025; research) — https://arxiv.org/abs/2507.02306v1
- [33] Eduard Kuric, Peter Demcak and Matus Krajcovic — What Would GPT Click: Practical Effects of Human-AI Behavioral Misalignment and the Cost of Synthetic Participants in User Experience (arXiv preprint, 2026; research) — https://arxiv.org/abs/2605.18302v1
- [34] Meinald T. Thielsch, Russell Haines and Leonie Flacke — Experimental investigation on the effects of website aesthetics on user performance in different virtual tasks (PeerJ, 2019; research) — https://pmc.ncbi.nlm.nih.gov/articles/PMC6388663/
- [35] Sebastian A. C. Perrig, David Ueffing, Klaus Opwis and Florian Brühlmann — Smartphone app aesthetics influence users' experience and performance (Frontiers in Psychology, 2023; research) — https://pmc.ncbi.nlm.nih.gov/articles/PMC10306164/
- [36] Kate Moran — The Aesthetic-Usability Effect (Nielsen Norman Group, 2024; opinion) — https://www.nngroup.com/articles/aesthetic-usability-effect/
- [37] Frank Bentley, Lennard Schmidt, Alyssa Sheehan, Bianca Gallardo and Ying Wang — Usability Hasn't Peaked: Exploring How Expressive Design Overcomes the Usability Plateau (CHI, 2026; kind not confirmed; published by Google Research, and Google owns the system tested) — https://research.google/pubs/usability-hasnt-peaked-exploring-how-expressive-design-overcomes-the-usability-plateau/
- [38] GOV.UK Service Manual — What each role does in a service team — https://www.gov.uk/service-manual/the-team/what-each-role-does-in-service-team
- [39] Jeff Sauro and Jim Lewis — Sample Size Recommendations for Benchmark Studies (MeasuringU, 2020; research) — https://measuringu.com/sample-size-recommendations/
- [40] Jakob Nielsen — Severity Ratings for Usability Problems (Nielsen Norman Group, 1994; opinion) — https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/
- [41] Kathryn Whitenton — Unmoderated User Tests: How and Why to Do Them (Nielsen Norman Group, 2019; opinion) — https://www.nngroup.com/articles/unmoderated-usability-testing/
- [42] Amy Schade — Remote Usability Tests: Moderated and Unmoderated (Nielsen Norman Group, 2013; opinion) — https://www.nngroup.com/articles/remote-usability-tests/
- [43] Jeff Sauro — Confidence Interval Calculator for a Completion Rate (MeasuringU, 2005; opinion) — https://measuringu.com/calculators/wald/
- [44] Jeff Sauro — Task Times in Formative Usability Tests (MeasuringU, 2008; opinion) — https://measuringu.com/formative-time/
