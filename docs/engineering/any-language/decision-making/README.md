# Decision-making

How a team decides, and how an AI agent takes part in deciding. Part one,
[decisions.md](decisions.md), covers a team's decision from the question to its review: how much
process it gets, input before the meeting, who decides and when a group votes, closing the
discussion, objections, the architecture decision record and its review. Its one rule: every
decision that others will live with has one named decider and a level of process set before the
input starts, and its record is written before the outcome is known and is never rewritten after.
Part two, [agents.md](agents.md), covers the decisions an agent makes while it works: what it
decides on its own, when it brings a decision back, the person who approves, several agents, and
what an agent records. Its one rule: an agent decides on its own only inside a written delegation
whose limits the tooling enforces, and every decision outside it comes back to a named person, who
decides from what the tool shows, not from the agent's account. Who decides each kind of decision,
DACI (Driver, Approver, Contributors, Informed) and the decision log belong to
[roles-and-decisions.md](../project-management/roles-and-decisions.md); this practice links them.

**Navigation**

- [When a team needs it, and when not](#when-a-team-needs-it-and-when-not)
- [What is here](#what-is-here)
- [How to adopt](#how-to-adopt)
- [The points to adapt](#the-points-to-adapt)
- [Sources](#sources)

## When a team needs it, and when not

The problem: a decision that nobody named a decider for is made by whoever pushes hardest, or made
twice, and a year later nobody can say why it was made. The practice gives a team the steps from the
question to a record, and gives an agent a written limit on what it may decide alone.

A team needs it for a decision that is hard to undo, that other teams live with, or whose problem
or answer is unclear: a data store, a framework, a schema, a public interface. It needs part two
when an agent works on a repository, a cloud account or data, since each such action is a decision
someone should have delegated.

It is too much for a choice inside one person's own work that is easy to undo and clear. Bezos
holds that most decisions can be undone, and that these "can and should be made quickly by high
judgment individuals or small groups" [1]. GitLab's handbook asks for a documented proposal only for
"Decisions that require input, buy-in, or awareness of others" [2], which draws the line at who
else is affected, not at how big the decision is. The simpler way for such a choice: the person
doing the work decides, and nothing is written ([decisions.md](decisions.md) section 3 sets the
levels). For agents, OWASP advises organisations to "avoid unnecessary autonomy; deploying agentic
behavior where it is not needed expands the attack surface without adding value" [3]. No source read
says when a written delegation is too much for a small project; [agents.md](agents.md) section 10
gives this practice's own view. Where each part stops holding: [decisions.md](decisions.md)
section 12 and [agents.md](agents.md) section 10.

## What is here

The two parts share the steps and the architecture decision record, so they stay in one folder. A
team with no agents reads part one only.

- [decisions.md](decisions.md) — part one: the steps of a decision, the three levels of process,
  gathering input before the decision, deciding after advice and when a group votes, closing the
  discussion, objections and commitment, architecture decision records, reviewing a decision, and
  what a record may say about people. Read it when you choose between options others will live
  with, close a discussion, record a technical decision as an architecture decision record, or
  review a decision that was made.
- [agents.md](agents.md) — part two: the delegation of an agent, how the delegation is enforced,
  when an agent brings a decision back, the person who approves, several agents answering one
  question, what an agent records, and the security threats of this work. Read it when you write or
  change what an AI agent may decide or do on its own, its approval steps, or how several agents
  reach one answer.
- [adr-example.md](adr-example.md) — one architecture decision record for a public API, with the
  reason for each part. Read it when you write an architecture decision record.
- [delegation-example.md](delegation-example.md) — one agent's delegation for dependency updates,
  with its enforcement table and the reason for each part. Read it when you write an agent's
  delegation.

## How to adopt

1. Copy this folder into your repository at `docs/engineering/any-language/decision-making/`.
2. Add one line to your `CLAUDE.md` or `AGENTS.md`: "Before you make a choice the task does not
   settle and that is hard to undo, crosses teams or has an unclear problem or answer (a data
   store, a framework, a schema, a public interface), close the discussion of such a choice, record
   a technical decision as an architecture decision record, review a recorded decision, or write or
   change what an AI agent may decide or do on its own (its delegation, its approval steps, or how
   several agents reach one answer), read `docs/engineering/any-language/decision-making/README.md`
   and the file it routes to for that work, and
   `docs/engineering/any-language/decision-making/adr-example.md` when you write an architecture
   decision record, `docs/engineering/any-language/decision-making/delegation-example.md` when you
   write an agent's delegation. The check: every architecture decision record the change adds names
   its decider, its options or the DACI page that holds them, its confidence and what would trigger
   a new look (`decisions.md` section 8); no accepted record's decision text changes in the diff,
   and a changed decision is a new record that supersedes it (`decisions.md` section 8); and every
   limit that a delegation the change adds must hold is enforced by a permission rule, a hook, a
   sandbox or a token scope the agent cannot change, or is marked in the delegation's enforcement
   part as a gap, with what catches a breach instead (`agents.md` sections 2 and 3)."
   Without it an agent never opens the folder; [agents.md](agents.md) section 13 says how an agent
   applies the practice once it has. The line that names who decides a decision and writes its
   decision-log entry stays in the project-management line, since
   [roles-and-decisions.md](../project-management/roles-and-decisions.md) owns it.
3. The files link other practices for the rules those own. Run
   `grep -rhoE '\]\(\.\./[^)#]+' docs/engineering/any-language/decision-making/ | sort -u` to print
   every link that leaves this folder. Copy each folder or file it names, or replace each link with
   your own rule for that topic.
4. In work that exists already, follow [decisions.md](decisions.md) section 14 for decisions that
   are already made, and [agents.md](agents.md) section 12 for agents that are already running.
5. Re-check each line that names a moving target six months after the date it carries, and
   distrust it from then until you have read it again.
   `grep -rnE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' docs/engineering/any-language/decision-making/` lists
   them. The six months is this practice's choice. Each file's Sources section opens with its
   `Checked <date>` line. The agent tool's settings and mechanisms that
   [agents.md](agents.md) section 3 names are the lines most likely to change.

## The points to adapt

The shape stays: one named decider for each decision; input gathered apart from the decision; the
decision text of an accepted record never rewritten; an agent's limits enforced by tooling it
cannot change. Within that shape, these are your choices; each rules file names the options and
their costs.

- The length of the comment window and the due date ([decisions.md](decisions.md) section 6).
- Where the records live, how they are numbered and named ([decisions.md](decisions.md) section 8).
- Which decisions fall on each of the three levels ([decisions.md](decisions.md) section 3).
- Which decision areas get a written delegation for an agent ([agents.md](agents.md) section 2).
- Which actions get a per-action prompt for the person who approves ([agents.md](agents.md)
  section 5).
- The enforcement mechanisms of your agent tool; [agents.md](agents.md) section 3 names Claude
  Code's.

## Sources

Checked 2026-10-30 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Jeff Bezos — 2015 Letter to Shareholders (Amazon.com, Inc., SEC Exhibit 99.1, 2016; opinion) — https://www.sec.gov/Archives/edgar/data/1018724/000119312516530910/d168744dex991.htm — checked 2026-10-29
- [2] GitLab — Handbook: Making Decisions — https://gitlab.com/gitlab-com/content-sites/handbook/-/raw/main/content/handbook/leadership/making-decisions.md — checked 2026-10-29
- [3] OWASP GenAI Security Project — OWASP Top 10 for Agentic Applications for 2026, Version 2026 — https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ — checked 2026-10-29
