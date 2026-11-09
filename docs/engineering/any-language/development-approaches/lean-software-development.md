# Lean software development

Lean software development is a set of principles for building software, written by Mary and Tom
Poppendieck and taken from lean thinking, which grew out of the Toyota Production System [1], [4].
The problem it answers: a team tunes each part of its work on its own, keeps every person busy and
measures each step apart, and a request still waits in one queue after another, for approval,
design, development, testing and deployment, before it reaches the customer [1]. Lean looks at the
whole flow of a request instead. This file says what the principles are, when they fit, how a team
starts from them, and the mistakes teams make with them. A team that needs a ready process, with
roles and events, does not need this file first: Lean gives principles, not a process (section 2).

**Navigation**

- [1. What it is](#1-what-it-is)
- [2. When it fits and when not](#2-when-it-fits-and-when-not)
- [3. How a team starts](#3-how-a-team-starts)
- [4. Common mistakes](#4-common-mistakes)
- [5. Sources](#5-sources)

## 1. What it is

Mary Poppendieck calls it "the application of Lean Thinking to the software development process"
[2]. In her 2002 essay she traces the name to the 1990 book The Machine That Changed the World,
and writes that the Toyota Production System has become known as lean production [3]. The
Poppendiecks' 2006 book says the same: that book "gave a new name to what had previously been
called Just-in-Time or the Toyota Production System" [4].

Three lists name the principles, an essay and two books, and the names change from one list to the
next, so cite the list your team uses by its source:

| Source | The principles |
|---|---|
| Mary Poppendieck, "Principles of Lean Thinking" (essay, 2002): the four principles of lean thinking she calls "most relevant to software development" [3] | Add Nothing But Value (Eliminate Waste); Center On The People Who Add Value; Flow Value From Demand (Delay Commitment); Optimize across Organizations |
| Mary and Tom Poppendieck, Lean Software Development: An Agile Toolkit (book, 2003), the chapter titles in the publisher's table of contents [5] | Eliminate Waste; Amplify Learning; Decide as Late as Possible; Deliver as Fast as Possible; Empower the Team; Build Integrity In; See the Whole |
| Mary and Tom Poppendieck, Implementing Lean Software Development: From Concept to Cash (book, 2006), its table of contents [4] | Eliminate Waste; Build Quality In; Create Knowledge; Defer Commitment; Deliver Fast; Respect People; Optimize the Whole |

The two lists of seven are one set of principles under two sets of names: the 2006 book's preface
says its second chapter "reviews the seven principles of lean software development presented in
Lean Software Development" [4]. Mary Poppendieck's essays restate the set in other words. Her
2003 essay uses Delay Commitment and Deliver Fast for the book's third and fourth principles [1],
her 2015 essay retells the 2003 list with "Build quality in" in place of Build Integrity In [6],
and her 2019 essay names three characteristics she would consider first principles: customer
focus, rapid flow and systematic learning [7].

Lean gives principles and leaves the practices to the team. Her 2003 essay: "These principles are
not cook-book recipes for software development, but guideposts for devising appropriate practices
for your environment" [1]. Her 2015 essay presents them as "a set of principles that form a
theoretical framework for developing and evolving agile practices" [6].

Kanban grew in the same tradition: Mary Poppendieck counts David Anderson's book Kanban (2010) among
the "two significant books about lean software development" of that year [6]. Kanban, its two
definitions and its practices are in [kanban.md](kanban.md).

What this file leaves out, and where it lives:

- Which approach a deliverable or a team uses (predictive, adaptive or hybrid; Scrum or Kanban):
  [life-cycle.md](../project-management/life-cycle.md) section 4.
- Who chooses the approach, the models behind the choice, and what the evidence says about
  outcomes: [choosing-an-approach.md](choosing-an-approach.md).
- A limit on work in process in a project: [principles.md](../project-management/principles.md)
  section 3. The Kanban Guide's flow measures: [kanban.md](kanban.md) section 4.
- Fixed-price and fixed-scope contracts: [regulated-work.md](regulated-work.md).
- Lean Startup, which uses the word "lean" for product discovery: out of scope.
- Security and privacy: there are no known security impacts of the principles in this file, and
  they touch no personal data. The practice's note on both is in [README.md](README.md).

Not covered yet: a rule that holds only under a named condition, such as a larger scale or a
regulated product, because the owner texts read state none; a study that measured the outcomes of
Lean software development, since none was read for this file; the full text of both books, read
only through the 2003 table of contents and the 2006 sample pages; and Niklas Modig and Pär
Åhlström's This is Lean, the source Mary Poppendieck gives for the idea of flow efficiency, which
was not read.

## 2. When it fits and when not

It fits a team that wants principles to build its own practices from [1]. It also fits where a
request waits longest outside the coding. Mary Poppendieck holds that the
expected benefits of agile "often failed to materialize because agile focused on optimizing
software development, which frequently was not the system constraint", and that Lean differs by
optimising flow efficiency across the whole value stream, "from concept to cash" [6]. This file
reads that as: when a request waits for approval, a handover or a release more than it waits for
developers, Lean's principles point the team at those waits.

In this file's own reading, it does not fit a team that needs a ready set of roles, events and
rules to start from, because Lean gives principles and no process (section 1) [1]. The pick between
Scrum and Kanban is [life-cycle.md](../project-management/life-cycle.md) section 4.

Beyond that reading, the owner texts read name no case where Lean does not fit. In her 2002 essay
Mary Poppendieck calls the principles of lean thinking "universal" [3]. She does name limits on
adopting it:

- IT departments found it hard to adopt the four areas she says lean software development came to
  focus on (build the right thing, build it fast, build the thing right, learn through feedback),
  because the changes lay "beyond span of control of most IT organizations" [6]. A team whose
  longest waits sit in departments it cannot change will see the waste, but cannot remove it
  alone; that reading is this file's own.
- Where an IT department contracts with its business colleagues "to deliver a pre-specified set of
  features", she holds that this way of working is "incompatible with full stack teams responsible
  for business metrics" [6].
- Between companies, her 2002 essay calls the typical software development contract "the ultimate
  sub-optimizing mechanism" [3]. The rules on contracts are in
  [regulated-work.md](regulated-work.md).
- Practices do not carry over from manufacturing: "transferring lean practices from manufacturing
  to development has led to some disastrous results" [6], and a practice "will not apply
  universally across all software development environments" [2]. These limits are on practices.
  On the principles, she holds in 2019 that lean's first principles apply to software too, though
  in a different way [7]. Section 4 has the mistake this leads to.

When it is too much: no owner text read names such a case. Lean adds no roles, events or artifacts
of its own, so its cost is the changes the flow shows; that reading is this file's own.

## 3. How a team starts

1. **Start from the principles, not from a practice.** Before the team adopts any lean practice,
   pick one list from section 1 and agree what each principle means for its work. The 2006 book:
   "The first step in implementing lean software development is to understand these underlying
   principles" [4]. Why: a practice taken over without its principle loses what made it work; Mary
   Poppendieck says that too often practices from lean companies are adopted, "but the heart of
   Lean Thinking is lost" [2].
2. **Follow one request from the ask to the delivery.** Pick a kind of request the team gets often,
   and write down every step it passes and every wait between steps, from the moment a customer
   asks to the moment the change reaches them. "All lean approaches focus on eliminating waste by
   looking at the flow of value from request to delivery" [1]. The 2003 book lists value stream
   mapping among its tools [5], and the 2006 book has a section on mapping the value stream [4].
   Why: the 2003 essay counts waiting and handoffs among the seven wastes of software development
   [1], and a map of one request shows both.
3. **Measure its flow efficiency.** Divide the time the request would take with no waiting by the
   time it takes today. Why: Mary Poppendieck holds that this number "tells you how much of the
   time you are actually working on a problem as it moves through your process" [7]. For example
   (invented numbers), a change that needs 3 days of work and reaches the customer 15 working days
   after the request has a flow efficiency of 3 ÷ 15 = 20%; the map from step 2 shows where the
   other 12 days went. The
   span starts at the request, so it is wider than the Kanban Guide's cycle time, which starts when
   work on an item starts ([kanban.md](kanban.md) section 4); that
   comparison is this file's own.
4. **Remove the biggest wait first, and judge each change by flow.** A change counts as better when
   the request reaches the customer sooner, not when people are busier. Mary Poppendieck: "flow
   efficiency trumps resource efficiency almost all of the time" [6]. Why: in Modig and Åhlström's
   view, as she reports it, fully used machines and people "create huge traffic jams, which end up
   creating a lot of extra work" [6]. A limit on work in process is one way to cut waiting: the rule
   for a project is [principles.md](../project-management/principles.md) section 3, and Kanban's way
   is in [kanban.md](kanban.md). She holds that Kanban "gave teams a way to increase flow
   efficiency" [6].

Check: when the team adds a practice in the name of Lean, ask which wait in the
team's own flow it removes. A practice that removes none was copied (section 4).

## 4. Common mistakes

**Copying lean manufacturing tools into development.** It looks like a team that takes a practice
from production, such as reducing variation or following a plan and measuring the variance from
it, and runs it in development unchanged. People make it because development and production rest
on the same lean principles, so the practices look as if they would carry over too [6]. The cost:
Mary Poppendieck holds that "transferring lean practices from manufacturing to development has led
to some disastrous results", and that reducing variation is "exactly the wrong thing to do in
product development", where variation is how a team learns [6]. In 2019 she wrote that "Attempts
to apply lean production tools and practices to a development process have a dismal track record"
[7], and the 2006 book says that techniques that succeed in operations "are often inappropriate for
development work" [4]. The fix: derive the practice from the principle, as section 3 step 1 asks;
practices "must evolve from a deep understanding of fundamental lean principles adapted to a
development environment" [6].

**Optimising resource utilisation.** It looks like a manager who keeps every person and every
specialist fully busy, measures each part of the work apart, and gives idle people more work. Mary
Poppendieck ties it to IT departments run as cost centres: their performance is judged on cost,
salaries are their main cost, so their incentives favour resource efficiency, "keep everyone fully
utilized and outsource work to lower salaried regions" [7]. The cost: she calls these "two of the
best ways to decrease flow efficiency" [7], and her 2003 essay gives an example:
"Optimizing the use of testing resources, for example, decreases the ability of the overall system
to rapidly produce tested, working code" [1]. The fix: measure the flow (section 3 steps 3 and 4),
and measure performance one level higher than the person, as the 2003 essay advises: "Measure the
team's defect count, not that of individuals" [1].

## 5. Sources

Checked 2026-10-29 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Mary Poppendieck — Lean Software Development (Lean Essays, first published in C++ Magazine, 2003; opinion) — https://www.leanessays.com/2003/04/lean-software-development.html — checked 2026-10-30
- [2] Mary Poppendieck — An Introduction to Lean Software Development, interview by Gustaf Brandberg (Lean Essays, 2004; interview) — https://www.leanessays.com/2004/06/introduction-to-lean-software.html — checked 2026-10-30
- [3] Mary Poppendieck — Principles of Lean Thinking (Lean Essays, first published at OOPSLA Onward!, 2002; opinion) — https://www.leanessays.com/2002/11/principles-of-lean-thinking.html — checked 2026-10-30
- [4] Mary and Tom Poppendieck — Implementing Lean Software Development: From Concept to Cash, 1st edition, sample pages: front matter, contents and chapter 1 (Addison-Wesley, 2006; opinion) — https://www.informit.com/content/images/9780321437389/samplepages/0321437381.pdf — checked 2026-10-30
- [5] Mary and Tom Poppendieck — Lean Software Development: An Agile Toolkit, publisher's page with description and table of contents (InformIT, Addison-Wesley, 2003; kind not confirmed) — https://www.informit.com/store/lean-software-development-an-agile-toolkit-9780321150783 — checked 2026-10-30
- [6] Mary Poppendieck — Lean Software Development: The Backstory (Lean Essays, 2015, preprint of a chapter of the Routledge Companion to Lean Management; opinion) — https://www.leanessays.com/2015/06/lean-software-development-history.html — checked 2026-10-30
- [7] Mary Poppendieck — Grown-Up Lean (Lean Essays, 2019, working paper for The International Handbook of Lean Organization; opinion) — https://www.leanessays.com/2019/07/grown-up-lean.html — checked 2026-10-30
