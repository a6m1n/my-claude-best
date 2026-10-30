# Decisions with AI agents: delegation, hand-back, approval and records

This file is for everyone who lets an AI agent act on a repository, a cloud account or data: the
developer or lead who sets the agent up, the person who approves its actions, and the agent itself,
which reads it before it acts. It says what an agent may decide on its own and how to write that
down, how to make the limits hold, when the agent brings a decision back and in what form, what the
person who approves needs, how several agents reach one answer, and what an agent may record. How a
team makes and records a decision is part one, [decisions.md](decisions.md). The container an agent
runs in is [agent-containers.md](../docker/agent-containers.md), and testing that an agent asks,
waits or hands over is the evals practice, [python/evals/agents.md](../../python/evals/agents.md).

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. What an agent decides on its own: the delegation](#2-what-an-agent-decides-on-its-own-the-delegation)
- [3. Enforcing the delegation](#3-enforcing-the-delegation)
- [4. When an agent brings a decision back](#4-when-an-agent-brings-a-decision-back)
- [5. The person who approves](#5-the-person-who-approves)
- [6. Several agents](#6-several-agents)
- [7. What an agent records](#7-what-an-agent-records)
- [8. Security](#8-security)
- [9. Common mistakes](#9-common-mistakes)
- [10. Where the rules stop holding](#10-where-the-rules-stop-holding)
- [11. Alternatives considered](#11-alternatives-considered)
- [12. Adoption with agents already running](#12-adoption-with-agents-already-running)
- [13. How an agent applies it](#13-how-an-agent-applies-it)
- [14. Review checklist](#14-review-checklist)
- [15. Sources](#15-sources)

## 1. Purpose and the one rule

An agent that can run commands makes decisions all day: which version to install, whether a failing
step is a reason to delete something, when the work is done. Three things make those decisions hard
to control. A limit written in an instruction file reads like a rule, but the model may not follow
it. A prompt before every action protects while prompts are rare, and people stop reading them when
they are many. And an agent's report of what it did is a claim, not a record of what happened. A
project that follows this file knows, for each area an agent works in, what the agent decides
alone; has the tooling enforce each limit that must hold; gets every other decision back in a form a
person can decide on; and checks the real state before anyone acts on an agent's word.

The one rule: **an agent decides on its own only inside a written delegation whose limits the
tooling enforces; every decision outside it comes back to a named person, who decides from what the
tool shows, not from the agent's account.**

Why it holds the rest together:

- OWASP's list of risks for agentic applications opens with least agency: "This captures our advice
  to organizations to avoid unnecessary autonomy; deploying agentic behavior where it is not needed
  expands the attack surface without adding value" [1].
- Anthropic's documentation for Claude Code separates two kinds of instruction. A line in an
  instruction file is read by the model, and "there’s no guarantee that it’ll follow your
  instructions"; a hook, a deny rule or a managed setting is applied by the harness "every time, no
  matter what the model decided to do" [2].
- Agents report work they did not do. Smyth, Mantilla-Ramos et al. found that among review runs
  that skipped files, "agents are misleading 80.4% of the time (59–96% per model)", and conclude
  that "a convincing final response alone cannot establish whether the reported work actually
  occurred" [3].

What it leaves out on purpose, and where that lives:

- How a team decides, and the architecture decision record (ADR) an agent may draft:
  [decisions.md](decisions.md). Who decides each kind of decision:
  [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5.
- The container, its credentials, its network, and why the agent's own settings are not the
  boundary: [agent-containers.md](../docker/agent-containers.md) sections 3, 4, 5 and 10.
- How to read an approval rate, and the Rule of Two (no session combines untrusted input, private
  data, and changing state or talking outside; when one must, a person approves each such action):
  [production.md](../../python/evals/production.md) sections 4 and 7.
- Testing that an agent asks, refuses or hands over, and graders that never read the agent's own
  report: [python/evals/agents.md](../../python/evals/agents.md) sections 2 and 6.
- A question back about a fact missing from the input:
  [prompt-engineering.md](../prompt-engineering/prompt-engineering.md) section 8.
- Self-consistency as a prompting technique: not covered by this practice.
- What a record keeps about the people in it: [decisions.md](decisions.md) section 10.
- Security: section 8 maps each threat the research found to the rule that stops it.

Not covered yet, because the research found no source it could read (section 10 gives the detail):
a study that compares a written delegation with per-action approval for agents; how developers'
approval of agent actions changes over weeks of real work; a source that says an agent must not be
able to write its own delegation, or that defines "reversible" by what the tooling can undo; a test
of an agent's exception note as a format; a live study of approval shown as a diff the tool
renders; one approver against two, and training for approvers; debate against a vote on current
frontier models; a person as tie-breaker between agents; an orchestrator's stop against an
independent check outside synthetic tests; an agent misled by a superseded record beyond one report;
a standard that names who is accountable for one agent's change; and a data-protection authority's
guidance on AI note-takers.

## 2. What an agent decides on its own: the delegation

A delegation is a short file, one per decision area, that says what an agent may decide there
without asking. A decision area is a kind of work with its own risks: dependency updates, schema
changes, a public API. Without the file, the agent's limits are whatever its permissions happen to
allow, and nobody can tell a decision it was meant to make from one it took.

**When a project needs it:** when an agent acts on a repository, a cloud account or data, where a
wrong step costs more than a rerun.

**When it is too much, and the simpler way:** for an agent in a sandbox with test credentials and
no path to production, the sandbox comes first and the delegation can be short; section 5 applies
only where a person approves. Simon Willison advises to "Run your agent in a secure sandbox that
restricts the files and secrets it can access and the network connections it can make", and to
"Try to provide credentials to test or staging environments where any damage can be well
contained" [4]. The sandbox, its credentials and its network are
[agent-containers.md](../docker/agent-containers.md) sections 3 to 5. Inside the sandbox, this
section and section 4 still apply to what the agent decides. The research found no source that
says when a delegation per area is too much for a small project.

Rules:

- **Before an agent starts work in a decision area, write a delegation for that area**: the intent,
  what the agent decides on its own, its limits, the actions it never takes, and the conditions that
  make it stop and report. The reason: the limits are then set before the first action, by the
  person who answers for the area, and not by the agent in the moment. Army doctrine gives
  subordinates "the greatest freedom of action equal to the level of acceptable risk in a particular
  situation", and lists the commander's intent among the control measures that "may not be
  delegated" [5]. Jurgen Appelo applies levels of delegation "to key decision areas", not to
  single tasks [6]. OWASP lists excessive agency as LLM03:2026 and advises: "Limit the tools
  that LLM agents are allowed to call to only the minimum necessary" [7]. The delegation as
  one package is this practice's own: each source is about human delegation or about agent security
  in general, and none describes the package for an agent.
- **Name the person who decides for the area, and a backup.** Take the decider from
  [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5. The reason: a
  decision the agent brings back needs someone with the authority to answer it; section 5 of this
  file says why that person must also be able to refuse.
- **Count an action as reversible only when the platform can undo it.** Reading a secret, and any
  effect outside the system such as a sent message or a call to another service, cannot be undone.
  The reason: whether an action can be undone depends on the tooling, not on the action's name.
  Zhong et al., who counted 290 public reports of agents damaging files, found that "Approval
  prompts show commands rather than their filesystem effects", and note that "once an agent reads a
  secret, it cannot unread it" [8]. Claude Code's own undo has gaps of the same kind: "A file
  that only Bash commands changed isn’t tracked and stays as it is. To revert it, use version
  control, such as Git" [9]. At Railway, an agent deleted a production volume through
  an API that "ran the deletion immediately, with no way to undo it", while "the dashboard had a
  48-hour window for the same action" [10]. The words "only when" are this practice's own; the
  sources show that undo depends on the tool, and do not state the rule. A call out that the work
  cannot run without, that carries no secret and that changes nothing on the other service, such
  as a call to the model API or a read from a package index, may be named in the delegation as
  accepted; it is then not a reason to stop. Every other action that cannot be undone stops the
  agent (section 4). This exception is this practice's own view.
- **Keep the delegation in the repository, link it from the agent's instruction file (and pass it
  in the start command of an unattended run, since a linked file loads only when the agent opens
  it [85]), and change it only through a reviewed pull request that the area's decider approves.**
  An "always allow" answer
  to a prompt widens the delegation, so it is such a change too. In Claude Code,
  `allowManagedPermissionRulesOnly` in managed settings hides the always-allow choices in
  permission prompts and stops saving new rules [14], so that answer cannot be given during a run.
  The reason: a limit that grows one
  click at a time is never reviewed. OWASP asks to "Put prompts, orchestration scripts, and memory
  schemas under version control with peer review" [1]. Wang, Li and Tian, in a position
  paper, note that "“always allow” clicks and session-wide authorizations monotonically widen
  boundaries with no principled shrink-back mechanism" [11]. Treating an "always allow" answer as
  a change to the file is this practice's own inference from the two.

The parts of a delegation. [delegation-example.md](delegation-example.md) shows a full one. The
"Set it when" and "Leave it out when" columns are this practice's own.

| Part | What it means | Set it when | Leave it out when |
|---|---|---|---|
| Area | the kind of work the file covers | always | never |
| Decider and backup | who answers what the agent brings back, and who answers when the decider is away | always | never |
| How it changes | a reviewed pull request the decider approves; an "always allow" request counts as one | always | never |
| Intent | what the work is for, so the agent can choose where the limits say nothing | always | never |
| Decides on its own | the choices the agent makes without asking | always | never |
| Limits | the bounds it works within, each one a number or a list it can check: the files it may touch, the size of a change, the versions it may move to | always | never |
| Never | actions it does not take even inside the limits, such as an action the platform cannot undo (other than a call out the delegation names as accepted, section 2), reading a secret, or a push to the main branch | an action like that is in the agent's reach | no such action is in reach; write "none in reach" and why |
| Report when | the conditions that make it stop and bring a decision back (section 4) | always | never |
| Done means | the test or the read of real state that says the work is finished (section 6) | the work changes files, data or anything outside the agent | the result is one thing a person reads at once, such as an answer in chat |
| Enforcement | for each limit and each never-action, the mechanism that enforces it, or "gap" and what catches a breach instead (section 3) | always | never |

## 3. Enforcing the delegation

A limit written in a file tells the agent what to do; it does not stop the agent from doing
something else. This section makes each limit that must hold stay in force even when the agent
decides otherwise.

**When a project needs it:** for every limit whose breach does harm before the review at merge can
see it (reading a secret, deleting data), or that the review cannot see at all. **When it is too
much:** a preference that has exceptions stays a line in the
instruction file. Anthropic's advice for Claude Code is that "a hook is for a rule with zero
exceptions" [2].

Rules:

- **Enforce each limit that must hold with tooling the agent cannot change: a permission rule, a
  hook, the sandbox, or the scope of a token.** A line in an instruction file is not enforcement.
  The reason: the model reads instructions, and the harness applies rules. Claude Code's permissions
  page: "Permission rules are enforced by Claude Code, not by the model. Instructions in your prompt
  or CLAUDE.md shape what Claude tries to do, but they don’t change what Claude Code allows"
  [12]. Birgitta Böckeler warns of an "Illusion of control": "as long as LLMs are
  involved, we can never be certain of anything" [13]. OWASP: "Implement authorization in
  logic rather than relying on an LLM to decide if an action is allowed or not" [7]. What a
  line in an instruction file can and cannot do, and the gate an agent cannot switch off, are in
  [claude-md.md](../../../claude-code/claude-md.md) § "How to write a line an agent can follow".
  Its warning that a hook on the agent's own machine can be skipped or worked around covers a hook
  the agent can reach. A hook counts as tooling the agent cannot change only when its script and
  the script's folder are out of the agent's write reach, or on a read-only mount, and it is set
  to block when it fails, with `"onFailure": "block"` (Claude Code 2.1.295 or later) [20]. Set
  `onFailure` that way on a hook that enforces a limit; leave it at its default on a hook whose
  failure should not stop the agent, because a blocking hook that breaks stops every call it
  matches.

  Check: before the decider approves a delegation, ask of each limit "which mechanism enforces
  it?" A limit whose answer is "the text" is marked as a gap in the enforcement part, with what
  catches a breach instead, such as the review at merge.
- **Keep the delegation and its enforcement out of the agent's write reach.** Put the permission
  rules in managed settings, or make the delegation file, the settings, and the hook scripts and
  their folder read-only for the agent's process at the operating-system or mount level. The
  reason: an agent that can edit its limits has none. In Claude Code, managed settings are highest:
  "no other level, including command line arguments, can override a managed permission rule", and
  the `allowManagedPermissionRulesOnly` key makes managed settings the only source of permission
  rules [12], [14]. Set that key on a machine or a container that runs the agent unattended; leave
  it out where people keep their own allow and deny rules, since it ignores the rules in their
  user, project and local settings [14]. A deny rule on `Edit(<path>)` covers Claude Code's own
  file tools and the shell commands it recognises, but not "arbitrary subprocesses that read or
  write files indirectly, like a Python or Node script that opens files itself"; for those the page
  says: "For OS-level enforcement that blocks all processes from accessing a path, enable the
  sandbox" [12]. The sandbox has a gap of its own: when it cannot start, Claude Code runs commands
  without it, unless `sandbox.failIfUnavailable` is set [19]. **Where the sandbox enforces a limit,
  turn its retry outside the sandbox off** with `"sandbox": {"allowUnsandboxedCommands": false}`,
  so that Claude Code ignores the parameter that asks for the retry [19]. A hook script in the
  project is a file like any other: a report on Claude Code 2.0.36 says that "there's no way to
  prevent Claude Code from modifying the hook scripts themselves using the Edit/Write tools", and
  the issue was closed for inactivity, not as fixed [15].
  A delegation file under `docs/` is not on Claude Code's fixed list of protected paths, so that
  mechanism does not cover it [16]. The keys that turn off the modes which skip approval
  are [agent-containers.md](../docker/agent-containers.md) section 10's. That an agent must not be
  able to write its own delegation is this practice's own rule: no source the research read says it
  in those words.
- **Match a limit to what an action does, not to how a command is spelled, and keep the agent tool
  patched.** The reason: one goal has many commands. Chen and Lin tested command denylists collected
  from GitHub and found that "69.0–98.6% denylists cannot fully block operations they aim to block",
  including one "shipped with a widely used agent by default" [17]. Between 2025-11-20 and
  2026-10-09 Anthropic published 23 security advisories for Claude Code; 13 of them name a bypass
  of command checks, approval prompts, trust dialogs, write restrictions or the sandbox, each fixed
  in a release [18]. The sandbox has its own way out: after a failure, "Claude
  analyzes the failure and may retry the command with the `dangerouslyDisableSandbox` parameter"
  [19]. That retry is on by default; the bullet above turns it off where the sandbox enforces a
  limit.
- **A token's scope is part of the delegation's enforcement: size and scope it as
  [agent-containers.md](../docker/agent-containers.md) section 4 says, and list it in the
  enforcement part (section 2).** The reason: the scope of a token the agent can reach is its real
  delegation, whatever the file says. At Railway, "The agent found a Railway API token stored
  locally on the user's machine and used it to call volumeDelete on a production volume", and "the
  token was provisioned with account scoped access, the maximum access possible" [10].

Claude Code's mechanisms, as its documentation read on 2026-10-29 describes them, checked with
Claude Code 2.1.312. Other agents have their own mechanisms; ask the same questions of each.

| Limit | Mechanism | What it misses |
|---|---|---|
| a file or folder the agent must not change | an `Edit(<path>)` deny rule, in managed settings so no other level overrides it; a `Write(<path>)` rule never matches, so write `Edit` [12] | a script that opens the file itself; add the sandbox or a read-only mount [12] |
| a command or a tool call | a deny rule; rules are evaluated "deny, then ask, then allow" [12] | other spellings of the same action [17] |
| a check that needs code | a `PreToolUse` hook that exits with code 2, which blocks the call before the allow rules are read [12], set to `"onFailure": "block"`, with its script and folder out of the agent's write reach | a hook that fails or times out: "A policy hook with a wrong path or a crashing script then lets everything through", unless the hook sets `"onFailure": "block"` (Claude Code 2.1.295 or later) [20]; a hook script or folder the agent can edit [15] |
| the permission rules themselves | managed settings, with `allowManagedPermissionRulesOnly` [14] | an administrator can still edit them ([agent-containers.md](../docker/agent-containers.md) section 10); a managed settings file the agent's user cannot read, which Claude Code skips, in a `-p` run with only a line on stderr; and a higher managed source, which by default replaces the file [84] |
| what any process may touch | the sandbox, or a read-only mount | a sandbox that cannot start, which runs commands unsandboxed unless `sandbox.failIfUnavailable` is set [19]; the sandbox's retry outside it, unless it is turned off [19]; inside an unprivileged container, a weaker mode; there the container, not this sandbox, is the boundary ([agent-containers.md](../docker/agent-containers.md) section 10) |
| what a credential can do | the token's scope | a broader token the agent finds on disk [10] |

Leave out the mechanism of a row when its limit has exceptions: such a limit stays a line in the
instruction file, as the opening of this section says.

## 4. When an agent brings a decision back

**When a project needs it:** whenever a delegation exists. **When it is too much:** a report for
every routine step, which is the burden section 5 describes. **The simpler way**, for a short task
with one visible result: the person reads the result. That simpler way is this practice's own view.

Rules:

- **The agent stops and brings the decision back when** a limit of its delegation is forecast to
  break; before an action the platform cannot undo, other than a call out the delegation names as
  accepted (section 2); when the intent does not settle a choice it
  must make; and when agents disagree on a decision that cannot be undone or checked (section 6).
  The reason: at these points the agent would otherwise decide something the delegation did not
  give it. PRINCE2's exception report goes up "to inform the project board when a stage plan or
  project plan is forecast to exceed tolerance levels set, and to offer options and recommendations
  for the way to proceed" (quoted in a PRINCE2 7 sample paper, from a copy a training firm hosts)
  [21]. Tomašev, Franklin and Osindero of Google DeepMind propose that "failures in
  irreversible, high-criticality tasks must trigger immediate termination or human escalation"
  [22]. An OpenAI white paper holds that "Some decisions may be too important for users to
  delegate to agents, if there is even a small chance that they’re done wrong" [23]. Army
  doctrine asks a subordinate who meets a new situation to report "their new situation and
  recommended course of action to their commander", "If time permits" [5].
- **Bring it back as an exception note in the form
  [communication.md](../project-management/communication.md) section 5 defines; never as an open
  question.** The reason: the person can decide in one reply, between options the agent has already
  worked out; PRINCE2's report exists "to offer options and recommendations" for the same reason
  [21]. The split with a question: a fact missing from the input is a question back, owned by
  [prompt-engineering.md](../prompt-engineering/prompt-engineering.md) section 8; a choice between
  options the delegation does not settle is a decision, and comes back as a note. When the decider
  cannot answer it, the note goes up the path in
  [communication.md](../project-management/communication.md) section 4.
- **Let the tooling detect the trigger, and take the note's facts about state from the tool record
  or the environment, not from the agent's account.** A deny rule, an ask rule or a hook fires on
  the action; the note quotes what the tool recorded. The reason: an agent may not notice that it
  crossed a line, and may report a state that is not there. At Railway the agent "decided that
  deletion was a reasonable step toward fixing something unrelated, and acted on that
  interpretation" [10]. Liu et al. describe agents that hide a failure, "a phenomenon in which
  an agent facing environmental constraints conceals its failure and performs actions that were not
  requested without reporting", and found that an explicit instruction to report anomalies reduced
  it but did not remove it [24]. The abstract of Advani's paper reports false success in
  "75.8% among AppWorld self-assessing coding-agent trajectories with explicit status claims"
  [25].
- **Inside the delegation and its intent, the agent acts without asking.** The reason: every
  question costs the person time and takes away the point of delegating. Kolt, in a legal analysis
  of AI agents: "Seeking clarification may, however, impose additional costs on the principal and
  undermine the value of delegation to an agent" [26].

Do agents ask too little? On benchmarks, yes. Vijayvargiya et al. found that "LLMs default to
non-interactive behavior without explicit encouragement" on software issues with missing details
and a simulated user [27], and Su and Cardie found that in question answering models
"overwhelmingly default to direct answers" [28]. Anthropic's telemetry on its own product
points the other way: "On the most complex tasks, Claude Code asks for clarification more than twice
as often as on minimal-complexity tasks", with its own caveat that "Claude may not be stopping at the
right moments, it may ask unnecessary questions" [29]. So this practice names the moments to
stop, and does not ask agents to ask more in general. Testing that an agent stops at those moments
is [python/evals/agents.md](../../python/evals/agents.md) section 2.

## 5. The person who approves

A person approves an agent's action when the delegation sends the action to them. The approval is a
control only if the person sees what will happen, can say no, and is not asked so often that they
stop reading.

**When a project needs it:** before every action the platform cannot undo, other than a call out
the delegation names as accepted (section 2). **When it is too much:** a prompt for reversible
actions inside the delegation. Zhong et al. propose a filesystem
that stages changes and can undo them, so that for those changes "the agent does not need to wait
for the user to pre-approve opaque commands" [8]. **The simpler way**, for a short task a person
watches from start to end: approve every action as it comes. In Claude Code this holds only with
auto mode turned off ([agent-containers.md](../docker/agent-containers.md) section 10). Most tools
work this way by default;
Wang, Li and Tian count runtime approval as "the most widely deployed mechanism (15/21)" among the
production agent systems they surveyed [11]. Using it as the simpler way is this practice's own
view.

Rules:

- **Before an action the platform cannot undo, other than a call out the delegation names as
  accepted (section 2), the tool shows its effect, and one named person who can refuse or stop it
  approves.** The effect is a diff or the output of a dry run, produced by the
  tool, not the agent's description of it. The reason: a person cannot judge an action whose effect
  they cannot see, and the agent's text can be wrong or forged. Zhong et al. found that "Approval prompts show
  commands rather than their filesystem effects", and that "Users therefore cannot make informed
  approvals" [8]. OWASP: "Display a pre-execution plan or dry-run diff before final approval" [1].
  Article 14(4) of the EU AI Act lists what a person who oversees a high-risk AI system must be able
  to do, among them "to decide, in any particular situation, not to use the high-risk AI system or
  to otherwise disregard, override or reverse the output" and "to intervene in the operation of the
  high-risk AI system or interrupt the system through a ‘stop’ button" [30]; this practice uses
  the list as what an approver needs, not as a legal duty for a team that uses a coding agent.
  Approval dialogs can be forged. In the Lies-in-the-Loop attack, dialogs "are generated based on
  context that an attacker can control through indirect prompt injection", and its authors advise
  that they "should be constructed and rendered by a dedicated function or tool that only processes
  the formatting provided by the agent’s developers" [31]. Reviewers that read the author's text
  are steered by it: Alexopoulos et al. got AI code reviewers to pass 32 of 33 reintroduced
  vulnerabilities by tuning the pull request's text [32], and Fogliato et al. found that
  review agents fail by "accepting an unverified account of why the change is safe" [33].
- **Make sure the person who approves has the authority and the information to refuse, and write in
  the delegation what they are there to check.** The reason: an approver with no control takes the
  blame without the power. Crootof, Kaminski and Price argue that "policymakers should be specific
  about what humans in the loop are there to do" [34]. Elish describes the moral crumple
  zone, where responsibility is "misattributed to a human actor who had limited control over the
  behavior of an automated or autonomous system" [35]. Green, after a survey of 41 policies,
  holds that "human oversight policies provide a false sense of security in adopting algorithms"
  [36]. Bainbridge wrote the same of process plants in 1983: "The human monitor has been given an
  impossible task" [37].
- **Keep per-action approval for rare actions that cannot be undone; let frequent routine actions
  run without a prompt, under the delegation the tooling enforces.** The reason is the burden on the
  person, not better protection. In the one head-to-head study, Ting Yan found that per-action
  approval blocked 59.6% of an agent's overreach against 39.6% under rules users wrote in advance,
  and that "user-authored rules did not by themselves provide stronger protection against agent
  overreach" [38]; it is a one-author preprint, with 113 people, a scripted agent on one simulated
  day, and coarse category rules rather than a delegation. Chen et al., with 48 people and live
  agents, found that plan-based strategies cut the odds that a problematic action occurred by 76%
  relative to the strategies without a plan, but "users blocked only 29 of the 138 problematic actions that reached execution (21%)", with no
  reliable difference in blocking across four oversight strategies; the plans were the agent's own,
  approved by the user, not a delegation [39]. What per-action
  approval costs is attention, when prompts are frequent and alike. Bravo-Lillo et al. found that
  "increasing habituation caused a three-fold decrease in the proportion of participants who
  responded to the change in the dialog", in a ten-minute online task with dialogs seconds apart
  [40]. Vance et al., with 15 people in a brain scanner over five days, saw "a dramatic drop
  in attention throughout the workweek despite partial recovery between workdays", and note that
  they measured attention, not behaviour [41]. The abstract of their field study reports that
  "users’ warning adherence substantially decreased over the three weeks" for app permission
  warnings [42]. For agent prompts, Anthropic reports a study of its own product in which
  testers "blocked about 17% of dangerous commands early in a session, dropping to about 5% after 50
  or more prior prompts" [43]; the testers worked in a test environment, and the page gives no
  count per group and does not say that session length was assigned at random. The wear-out holds
  for frequent, repeated prompts; a rare prompt is a different case. How to read an approval rate is
  [production.md](../../python/evals/production.md) section 4's.
- **In LangChain's human-in-the-loop middleware, deny a tool call with `reject`, never with
  `respond`.** The reason: a denial must stop the call. Its documentation, read on 2026-10-29:
  "Use reject when the human is denying the requested action. Use respond only when the human is
  acting as the tool, such as answering an ask_user prompt. Do not use respond to deny
  side-effecting tools, because its message is treated as a successful tool result" [79].
- **Two cases put a person on more actions than this section does, and other practices own them:**
  a session that combines untrusted input, private data, and changing state or talking outside
  ([production.md](../../python/evals/production.md) section 7), and the machines of
  [agent-containers.md](../docker/agent-containers.md) section 10. Where either applies, its rule
  wins over the rule on per-action approval above.
- **Do not count on training to remove automation bias; make checking cheap instead.** The reason:
  the bias is well documented, and training is not shown to fix it. The abstract of Parasuraman and
  Manzey's review says that automation bias "cannot be prevented by training or instructions"
  [44]. The EU AI Act names the bias in Article 14(4)(b) [30], and NIST's profile for
  generative AI calls it "excessive deference to automated systems" [45]. In a systematic review
  of clinical decision support, Goddard et al. found wrong advice followed more often with support
  than without (risk ratio 1.26), from four studies pooled in "a small, indicative meta-analysis"
  [46]. Not every study finds it: with civil servants, the third study of Alon-Barkat and
  Busuioc found neither automation bias nor selective adherence to advice, and selective adherence
  appeared in their second study, with the public [47]. Explanations cut both ways: Bansal et
  al. found that "explanations increased reliance on recommendations even when the AI was
  incorrect" [48], while Vasconcelos et al. found that explanations help when they lower "the
  costs of verifying the AI’s prediction" [49]. That is why the first rule of this section
  asks for the effect, which makes checking cheap, and not for the agent's reasoning.

## 6. Several agents

**When a project needs it:** when the work splits into parts that do not depend on each other.
**When it is too much:** Anthropic, describing its own research system, writes that domains "that
require all agents to share the same context or involve many dependencies between agents are not a
good fit for multi-agent systems today", and that "multi-agent systems use about 15× more tokens
than chats" [50]. **The simpler way** is one agent with all the facts. Li, Naito and Shirado
found that groups of agents reached "only 30.1% accuracy under distributed information, compared to
80.7% accuracy for single agents given complete information" [51]. Tran and Kiela found that single
agents (SAS) "consistently match or outperform MAS on multi-hop reasoning tasks when reasoning tokens
are held constant" [52].

Rules:

- **Use one orchestrator over several agents only when the task splits into independent parts;
  otherwise use one agent.** The reason: the same structure helps one shape of task and hurts
  another. Kim et al., of Google Research, Google DeepMind and MIT, tested 260 set-ups on six
  benchmarks with models from three vendors [53]. A central coordinator raised accuracy on a parallel
  finance task by 80.8% relative to one agent and lowered it on a sequential planning task by 50.3%,
  and the mean change over all multi-agent set-ups was −0.3% [53]. They also report that
  "tasks where single-agent performance already exceeds 45% accuracy experience negative returns from
  additional agents", a trend that loses significance under their stricter test, and that a central
  check held the spread of errors to 4.4 times, against 17.2 times for agents working independently
  [53]. When there is an orchestrator, it gives each agent a brief: Anthropic's lead agent
  gives each subagent "an objective, an output format, guidance on the tools and sources to use, and
  clear task boundaries" [50].
- **Have agents answer independently before any exchange, then exchange briefly, in few rounds.**
  The reason: talk makes agents agree, not get it right. Kaesberg et al. found that "Increasing the
  number of agents improves performance, while more discussion rounds before voting reduce it"
  [54]. Weng, Chen and Wang found that models conform to their peers, and that "with more
  discussion rounds, LLMs’ conformity becomes greater"; their average rates of 23.5% to 47.2% come
  from three test set-ups with scripted peers, not from a range of models [55].
- **For a question with one right answer that no test can check, take a vote or use
  self-consistency, not a debate, and count agents of one model family as one voter.** The reason:
  a vote gave most of debate's gain at less cost, and models of one family make the same mistakes.
  Choi, Zhu and Li found that "Majority Voting alone accounts for most of the performance gains
  typically attributed to MAD" (multi-agent debate) [56]. Smit et al. found that debate does "not
  reliably outperform other proposed prompting strategies, such as self-consistency" [57].
  Bertalanič and Fortuna measured debate at 2.1 to 3.4 times the tokens of self-correction, for
  equal or lower accuracy [58]. Kaesberg et al. found voting better on reasoning tasks, and
  consensus slightly better on knowledge tasks [54]. All of these studies used small or older
  models: 7 to 8 billion parameters, Llama 3, or GPT-3.5 [54], [56], [57], [58]. On independence, Kim, Garg, Peng and Garg
  found that "larger and more accurate models have highly correlated errors, even with distinct
  architectures and providers" [59]; He et al. found the minority right in 175 of 686 split
  votes, 25.5% [60]; and Han's formal analysis, tested on synthetic data only, names "decorrelation
  — changing model family, modality, or evidence source — rather than adding gates" as the lever
  [61].
- **Check an answer that a test can check with the test, not with a vote.** The reason: a check
  against real output is independent of the agents, and another model is not. Xu et al. found that
  checks written for each subtask helped most, while a generic model verifier added nothing on one
  coding benchmark and let too much pass [62]. Jason Liu, on synthetic tool-use tasks, found that an
  agent's self-check let through as many unsafe completions as no check, 252 of 288 [63]. The
  abstract of Tsui's paper reports "a 64.5% Self-Correction Blind Spot: models correct external
  errors but fail on identical internal ones" [64]. The "not with a vote" half is this practice's
  inference: no source compared a vote with a test on the same question.
- **For work that has effects, let a test or a read of real state say that the work is done, not
  the agent's report.** Where a wrong stop costs only a weaker result, such as research that could
  have gone on, the lead agent may decide that it has enough. The reason: agents claim completion
  they did not reach (section 7). In Cemri et al.'s labels of failures in multi-agent runs, "no or
  incomplete verification (FM-3.2, 8.20%), or incorrect verification (FM-3.3, 9.10%)" are two of
  fourteen failure modes, counted as shares of all failure labels [65]. Anthropic's research
  system lets its lead agent decide "whether more research is needed" [50], which fits a
  task where stopping early costs a weaker report. For evals, the grader rule is
  [python/evals/agents.md](../../python/evals/agents.md) section 6.
- **When agents disagree on a decision that cannot be undone or checked, a person decides, and forms
  their own view before reading the agents' positions.** The reason: a person who reads the agents
  first tends to follow them. Berger et al., in a re-analysis of ten data sets, found that
  independent human and AI judgements with a human tie-break beat AI as an adviser "because people
  cannot discriminate well enough between correct and incorrect AI advice", at the cost of a second
  person in "20–49% of cases" [66]. Recchia et al. found that participants helped by a model
  "achieved poorer performance than LLMs alone" and "routinely deferred to the language model"
  [67]. A person as the tie-breaker for agents is this practice's own inference; no study has
  tested it.
- **Treat a model used as a verifier as a judge, and validate it** as
  [judges.md](../../python/evals/judges.md) sections 5 and 6 say.

## 7. What an agent records

**When a project needs it:** for an agent's choice that someone will need to understand later.
**When it is too much:** an architecture decision record for every choice an agent makes;
[decisions.md](decisions.md) section 8 says which decisions get one, and that holds for agents too.
Davidson, writing about his own agent instructions: "An agent doesn’t need the transcript of every
argument" [68]. **The simpler way**, for a choice that needs no ADR: the pull request
description says what the agent chose and why. That simpler way is this practice's own view.

Rules:

- **Never take a model's stated reason as the record of why it chose.** A reasoning field in the
  answer ([prompt-engineering.md](../prompt-engineering/prompt-engineering.md) section 12) helps a
  reviewer find where an answer went wrong; it is not a decision record. The reason: stated reasons
  are often incomplete. Chen et al., of Anthropic's alignment team, found that reasoning models named
  a planted hint that changed their answer in 25% (Claude 3.7 Sonnet) and 39% (DeepSeek R1) of such
  cases [69]. Turpin et al.: "we review 426 explanations supporting biased predictions and
  only 1 explicitly mentions the bias" [70]. Zaman and Srivastava dispute the reading, saying the
  metric "confuses unfaithfulness with incompleteness" [71]. So a stated reason is often
  incomplete, which is enough to keep it out of the record.
- **An agent may draft an ADR; a named person accepts it, after checking each fact against its
  source and that the status matches what was decided.** The ADR names who drafted it and who
  accepted it ([decisions.md](decisions.md) section 8). The reason: drafts add facts and turn talk
  into decisions. Costa da Silva and Gama found that their agent, drafting ADRs from meeting
  transcripts, added figures that "came from a retrieved external ADR" and "sometimes transformed
  tentative discussions into accepted decisions"; they advise that "the generated ADRs should be
  interpreted as reviewable drafts rather than authoritative documentation" [72]. Dhar et al.
  suggest, as future work, that generated decisions serve as recommendations that architects review
  and approve [73]. Olaf Zimmermann lists among common ADR mistakes: "AI has taken over, but its
  output is used without quality check" [74]. Accountability stays with people: Martin
  Fowler holds that "the organizations that build and run agents are responsible for everything those
  agents do" [75], and Simon Willison says of Claude Code: "It can’t take accountability for
  what it’s done" [76]. The "drafted by, accepted by" field is this practice's own inference
  from these sources.
- **Read a record by its status.** Accepted binds; Proposed is context; Superseded, Deprecated and
  Rejected are history. When an accepted record no longer holds and nothing replaces it, retire it as
  [decisions.md](decisions.md) section 8 says. The reason: a stale accepted record misleads. Davidson's
  own agent instructions read: "Treat accepted ADRs as binding. Proposed ADRs are non-binding context.
  Superseded ADRs are historical context and do not govern current work", after "an agent preserved
  an outdated storage abstraction across a new feature because an ADR still described it as
  mandatory" [68]. It is one practitioner's set-up, and he says different projects need
  different conventions [68]. A model can help check code against the records: Su et al. found that "LLMs
  can meaningfully support validation of architectural decision compliance" [77].
- **Treat an agent's report of what it did as a claim, and check it against the tool-call record or
  the real state before a person or another agent acts on it.** The reason: the report and the work
  often differ. Smyth, Mantilla-Ramos et al. found that agents did not read every file they were
  asked to review in 67.9% of runs, and were misleading in 80.4% of those runs [3]. Liu et
  al. found agents that conceal failure [24], and Advani's abstract reports false success in
  75.8% of the AppWorld coding-agent runs that claimed a status [25]. Review agents do better when
  they "separate claim extraction from claim verification: first identify what the PR claims, then
  test those claims against the diff" [33]. Section 6 applies the same check to the question of
  when work is done.
- **When an agent drafts a record from a meeting transcript, tell the people in the meeting that an
  AI tool is used, and check its output for accuracy.** The reason: UK data-protection guidance asks
  for both. The ICO: "Where an AI tool is used, privacy notices should be updated to inform people
  about how it is being used, and for what purposes", and "When using an AI tool, organisations must
  check that the outputs are accurate" [78]. This is UK guidance; other laws may differ, so ask the
  person who owns data protection. What the record keeps about the people in it is
  [decisions.md](decisions.md) section 10.

## 8. Security

The threats the research found, the rule that stops each, and where the rule lives.

| Threat | What stops it | Where |
|---|---|---|
| The agent edits its own delegation, settings or hook scripts and widens its limits. Claude Code's sandbox page warns that a command able to edit the settings files "could grant itself permissions, or add a hook or MCP server that Claude Code runs outside the sandbox" [19]; one advisory let code in the sandbox "inject persistent hooks" that ran with the host's privileges, fixed in 2.1.2 [18] | the files are out of the agent's write reach: managed settings, a read-only mount, the sandbox | section 3 |
| A deny rule that a subprocess walks past [12] | the sandbox, or a read-only mount, for paths no process may change | section 3 |
| A denylist keyed on how a command is spelled [17] | limits on what an action does; the sandbox; a patched tool | section 3 |
| The sandbox's retry outside the sandbox [19] | the retry turned off where the agent must stay inside | section 3; inside a container, also [agent-containers.md](../docker/agent-containers.md) section 10 |
| A token on disk wider than the delegation [10] | credentials sized to the delegation, and none in reach that the agent must not use | section 3; [agent-containers.md](../docker/agent-containers.md) section 4 |
| A forged approval dialog [31] | the tool renders the effect; the agent's text is not what the person approves | section 5 |
| A reviewer, person or model, steered by a pull request's text [32], [33] | the approver sees the effect, and claims are checked against the code | sections 5 and 7 |
| A confident or injected message from one agent steering the others [55]; Kaesberg et al. found that voting "can be easily tricked by generating answers that seem to be correct but have some incorrect statements" [54] | independent answers first, few rounds, a test where one exists | section 6 |
| Untrusted input, private data and outside actions in one session | the Rule of Two | [production.md](../../python/evals/production.md) section 7 |
| A bypass in the agent tool itself; one advisory let a repository's own settings skip the trust dialog, fixed in 2.1.53 [18] | a patched tool | section 3 |
| A policy hook that crashes and lets every action through [20] | the hook set to block when it fails | section 3 |

Out of scope, and why: the container's isolation, the credentials that enter it and its network are
[agent-containers.md](../docker/agent-containers.md) sections 3 to 5, which this file links and does
not repeat. Defences against prompt injection in general, and how to test them, are
[production.md](../../python/evals/production.md) section 7 and
[python/evals/agents.md](../../python/evals/agents.md) section 7.

## 9. Common mistakes

| Mistake | What it costs | Fix |
|---|---|---|
| A limit written only in the agent's instruction file | the model may not follow it; Anthropic: "If you keep adding emphasis to a CLAUDE.md line and Claude still misses it, that’s a sign the line belongs in a hook" [2] | section 3 |
| An `Edit` deny rule trusted to protect a file from every process | a script that opens the file itself is not covered [12] | section 3 |
| A `Write(<path>)` permission rule | it never matches; `Edit(<path>)` is the rule that applies [12] | section 3 |
| A denylist of command strings | most real denylists miss bypasses [17] | section 3 |
| A long-lived token with account scope on the agent's machine | the agent's real delegation is the whole account [10] | section 3 |
| "Always allow" clicked to stop the prompts | the boundary widens, with no way back [11] | section 2 |
| A prompt that shows the command, not its effect | the person approves what they cannot judge [8] | section 5 |
| A prompt on every routine action | attention wears out on frequent prompts [40], [43] | section 5 |
| An approver with no stated job and no power to refuse | blame without control [35] | section 5 |
| A plan approved up front, then no attention while it runs | "plans constrained unplanned actions but left unlisted safeguards unaddressed, while upfront approval inhibited runtime scrutiny" [39] | sections 3 and 4: limits the tooling enforces, and stops the tooling detects |
| The agent's "done" taken as the work done | misleading reports in most incomplete runs [3] | sections 6 and 7 |
| `respond` used to deny a tool call in LangChain's human-in-the-loop middleware | "its message is treated as a successful tool result"; use `reject` [79] | section 5 |
| Many rounds of debate between agents | conformity grows with the rounds [55] | section 6 |
| Agents of one model family counted as independent voters | their errors are correlated [59] | section 6 |
| A generic model verifier trusted as the check | it lets too much pass [62] | section 6 |
| A model's reasoning kept as the record of why | stated reasons are often incomplete [69] | section 7 |
| An agent's ADR draft accepted without a check | figures from elsewhere, and talk written up as a decision [72] | section 7 |
| A stale accepted ADR left in place | an agent follows it [68] | section 7 |

## 10. Where the rules stop holding

- **A sandbox with test credentials and no path to production.** The sandbox does most of the work
  (section 2). The delegation can be short, and section 5 applies only where a person approves.
- **A short task that a person watches.** Approving every action, or reading the one result, is
  simpler than a delegation and its enforcement (sections 4 and 5; this practice's own view). In
  Claude Code, approving every action holds only with auto mode turned off
  ([agent-containers.md](../docker/agent-containers.md) section 10).
- **Agents other than Claude Code.** The mechanisms in section 3 are Claude Code's, as its
  documentation read on 2026-10-29 describes them for version 2.1.312. Other tools have their own;
  the questions of section 3 still hold.
- **A person is not always an improvement.** Vaccaro, Almaatouq and Malone's meta-analysis of 106
  experiments found that people working with AI did worse on average than the better of the two
  alone (g = −0.23; −0.27 on decision tasks), and better only where the person alone beat the AI
  (g = 0.46) [80]. Recchia et al. tie the cases where people helped to "human evaluators
  possessing knowledge absent from models" [67]. An approver adds most where they know what the
  model does not.
- **A rising approval rate is not quality.** Yu et al. saw approval of agents' pull requests rise
  from 30.1% to 36.8% among repeat reviewers while comments fell, and write: "We cannot establish
  causality: agent code may genuinely improve over the observation window" [81]. How to read the rate
  is [production.md](../../python/evals/production.md) section 4's.
- **An oversight step needs evidence of its own.** Green asks that any proposed form of human
  oversight be shown by evidence to work, before it is relied on [36].
- **The evidence on wear-out is thin.** The two lab studies used artificial tasks, the field result
  comes from an abstract, and the only data on agent prompts is one vendor's study of its own product
  (section 5). Bravo-Lillo et al. note that in real use "Security dialogs tend to be viewed one at a
  time with longer intervals between views" [40].
- **The studies of several agents used small or older models** (section 6). Those rules may change
  when someone tests current frontier models.
- **What it costs.** A delegation per area, and its enforcement, take time to write and to keep in
  step with the tools. A person as tie-breaker costs a second person in 20–49% of cases [66].
  Several agents cost about 15 times the tokens of a chat in Anthropic's system [50].

Not covered yet. The research for this file looked for these and found no source it could read:

- A study that compares a written delegation (intent, limits, report conditions) with per-action
  approval for agents. The nearest are Yan, with category rules in a simulation [38], and Chen et
  al., with plans the agent wrote [39].
- How real developers' approval of agent actions changes over weeks of real work.
- A source that says an agent must not be able to write its own delegation, and a standard that
  defines "reversible" by what the tooling can undo.
- A test of an agent's exception note as a format, and of acting within the intent when nobody can be
  reached, for agents.
- A live study of approval shown as a diff the tool renders, against the agent's own description.
- Whether one approver or two catches more errors in agent actions, and whether training approvers
  of agent output helps.
- Debate against a vote on current frontier models.
- A person as tie-breaker for disagreement between agents.
- A stop decided by an orchestrator against an independent check, outside synthetic tests.
- An agent misled by a superseded record, beyond one practitioner's report [68].
- A standard that says who is accountable for one agent's change, at the level of a named person.
- A data-protection authority's guidance on AI note-takers and meeting transcripts, and on whether
  a transcript may go to a model provider's API.

## 11. Alternatives considered

- **A written delegation because it protects better than per-action approval.** Not taken as the
  reason. The one head-to-head study found the opposite [38], and Chen et al. found that plans the
  agent wrote cut problematic actions, but found no reliable difference in blocking [39]. This practice keeps per-action approval for rare actions that
  cannot be undone, and chooses the delegation for frequent routine actions because of the burden
  (section 5).
- **Per-action approval of every action.** Not taken for frequent routine actions, because attention
  wears out (section 5). Wang, Li and Tian credit runtime approval with "strong security guarantees"
  and object to its burden, not its protection [11].
- **Debate as the way agents reach one answer.** Zhu et al. report, in an abstract and a figure, that
  debate with diverse starting answers and stated confidence can "consistently outperform vanilla MAD
  and majority vote" on six question-answering benchmarks [82]; Du et al.'s original debate method
  ran on GPT-3.5 [83]. Not taken: every comparison used small or older models, debate costs 2.1 to
  3.4 times the tokens [58], and no comparison on frontier models was found.
- **Act within the intent when the commander cannot be reached.** Doctrine says that, in doubt,
  subordinates "should act if they can do so within their commander's intent" [5]. For an agent
  this practice reads it as: inside the delegation, act; before a step that cannot be undone, stop,
  even when nobody answers. That reading is this practice's own.
- **Make agents ask more.** Agents ask too little on benchmarks [27], [28], and one
  vendor's telemetry points the other way for its product [29]. Not taken as a general rule;
  section 4 names the moments to stop.
- **Treat Proposed records as binding.** Su et al. group Proposed and work-in-progress records with
  accepted ones [77]. Not taken: that grouping is a label for their data set, not a rule, and the
  record format's own status rule holds (section 7).
- **Skip the plan when the diff fits in one sentence.** An earlier version of Claude Code's
  best-practices page gave this test; the page read on 2026-10-29 no longer has it [2]. Not taken
  as a trigger here: a one-sentence diff can still be hard to undo, such as a renamed column or a new
  public field, so the trigger is whether the platform can undo the change. That is this practice's
  own view.
- **The agent's explanation shown to the approver in place of the effect.** Not taken: explanations
  raised reliance on wrong advice in one study [48]; section 5 asks for the effect.

## 12. Adoption with agents already running

The answer is **new and touched code** ([refactoring.md](../refactoring/refactoring.md) section 7):
the practice applies when an agent gets a new area or wider permissions, and an existing set-up moves
to it when a change touches it. The steps below are this practice's own.

- Before an agent gets a new decision area, or wider permissions in one (a broader token, a new
  allow rule, an "always allow" answer), write the area's delegation (section 2) with its
  enforcement part (section 3).
- An agent already at work in an area with no delegation keeps its current permissions until the
  next change to them; that change writes the delegation first.
- When a change touches a line in an instruction file that states a limit, move the limit into a
  mechanism the agent cannot change if it must hold (section 3; a hook counts only when it is out
  of the agent's write reach and blocks when it fails), or keep the line as advice if it has
  exceptions.
- A record an agent drafted before this practice stays as it is; the next record an agent drafts
  follows section 7.

## 13. How an agent applies it

The project's `CLAUDE.md` routes an agent here with the line in [README.md](README.md), "How to
adopt", step 2. For this file, the line fires when the agent writes or changes what an agent may
decide or do on its own: its delegation, its approval steps, or how several agents reach one answer.
Its check asks that every limit a new delegation must hold is enforced by tooling the agent cannot
change, or is marked in the delegation's enforcement part as a gap, with what catches a breach
instead (sections 2 and 3). Choosing and closing a decision, recording a technical decision as an
ADR, and reviewing a decision go through the same line to [decisions.md](decisions.md).

What an agent does in this work:

- **Before it acts in an area, it reads the area's delegation**, and works inside it (section 2).
- **It stops at the moments of section 4 and writes the exception note**, with facts from the tool
  record.
- **It never edits its own delegation, settings or hook scripts**; a change goes through a pull
  request that the decider approves (sections 2 and 3).
- **It reports work as done only with the test or the state that shows it** (sections 6 and 7).
- **It drafts records; it does not accept them** (section 7).

The mistakes agents make in this work, as the research found them, each with the section that stops
it:

- They ask too little on benchmarks with missing facts [27], [28], though one vendor's
  telemetry shows its agent asking more on harder tasks [29] (section 4).
- They claim work they did not do [3], [25], [24] (sections 6 and 7).
- They take a step that cannot be undone because they judged it reasonable [10] (sections 2
  and 4).
- They draft records with figures from elsewhere, or write a tentative discussion up as accepted
  [72] (section 7).
- They follow a stale accepted record [68] (section 7).
- They route around command denylists [17], [18] (section 3).
- They follow a confident peer [55] (section 6).
- In LangChain's human-in-the-loop middleware, a `respond` decision on a tool with side effects
  counts as a successful result, so a denial must use `reject` [79] (section 5).

One more, from this practice's own view: the size of a diff is not the trigger for bringing a
decision back. A one-sentence diff can still be hard to undo; the trigger is whether the platform can
undo it (sections 2 and 4).

## 14. Review checklist

One question per section, for a change that adds or edits a delegation, an approval step or a set-up
of several agents.

| Section | Ask | Red flag |
|---|---|---|
| 2. Delegation | Does each area the agent works in have a delegation with intent, limits, never-actions, report conditions and a decider? | an agent with permissions and no file; limits agreed only in a chat |
| 2. Reversible | Is each action called reversible one the platform can undo? | "we can revert it" said of a read of a secret, a sent message or an API delete |
| 3. Enforcement | Does every limit that must hold name the mechanism that enforces it? | a limit that is only a line in the instruction file; an agent that can write its delegation or its hooks |
| 3. Credentials | Is every token the agent can reach no wider than its delegation? | an account-scoped token on disk |
| 4. Hand-back | Does the delegation list when the agent stops, and does the note carry options and a recommendation? | an open question; facts in the note that only the agent's account supports |
| 5. Approval | Does the approver see the tool's diff or dry run, and can they refuse? | a prompt that shows only the command; a prompt on every routine step |
| 6. Several agents | Does the task split into independent parts, and do the agents answer before they exchange? | many rounds of debate; agents of one family counted as independent votes; a vote on what a test could check |
| 7. Records | Was each fact in an agent's draft checked, and does the record name who drafted it and who accepted it? | a reasoning field kept as the record; an agent's "done" acted on unchecked |
| 8. Security | Are the delegation, the settings and the hooks out of the agent's write reach, and is the tool patched? | the sandbox retry on where the agent must stay inside; an old version of the tool |

## 15. Sources

Checked 2026-10-30 unless a line ends with — checked <YYYY-MM-DD>.

- [1] OWASP GenAI Security Project — OWASP Top 10 for Agentic Applications for 2026, Version 2026 (December 2025) — https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ — checked 2026-10-29
- [2] Anthropic — Claude Code documentation: Best practices for Claude Code — https://code.claude.com/docs/en/best-practices — secondary, for the earlier text: read through the Internet Archive copy of 2026-01-22, https://web.archive.org/web/20260122034115/https://code.claude.com/docs/en/best-practices — checked 2026-10-29
- [3] Smyth, Mantilla-Ramos et al. (Tara Research Team) — Quantifying Overclaiming Propensity in Frontier LLM Agents (arXiv 2609.20812, 2026; research) — https://arxiv.org/abs/2609.20812 — checked 2026-10-29
- [4] Simon Willison — Designing agentic loops (Simon Willison's Weblog, 2025; opinion) — https://simonwillison.net/2025/Sep/30/designing-agentic-loops/ — checked 2026-10-29
- [5] Headquarters, Department of the Army — ADP 6-0, Command and Control, 07 July 2026 — https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN47032-ADP_6-0-000-WEB-1.pdf — checked 2026-10-29
- [6] Jurgen Appelo — Leading Agile Developers: The Seven Levels of Authority (Part 2) (InformIT, 2011; opinion) — https://www.informit.com/articles/article.aspx?p=1675546&seqNum=3 — checked 2026-10-29
- [7] OWASP GenAI Security Project — OWASP Top 10 for LLM Applications 2026, Version 2026 (4 August 2026) — https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ — checked 2026-10-29
- [8] Zhong, Liao, Liu, Zheng, Arpaci-Dusseau and Arpaci-Dusseau — Don't Let AI Agents YOLO Your Files: Information and Control in Agent-Native Filesystems (arXiv 2604.13536, 2026; research) — https://arxiv.org/abs/2604.13536 — checked 2026-10-29
- [9] Anthropic — Claude Code documentation: Checkpointing — https://code.claude.com/docs/en/checkpointing — checked 2026-10-29
- [10] Mahmoud Abdelwahab — Your AI wants to nuke your database. Guardrails fix that. (Railway blog, 2026; case) — https://blog.railway.com/p/your-ai-wants-to-nuke-your-database — checked 2026-10-29
- [11] Wang, Li and Tian — Reframing LLM Agent Security as an Agent–Human Interaction Problem (arXiv 2605.24309, 2026; opinion) — https://arxiv.org/abs/2605.24309 — checked 2026-10-29
- [12] Anthropic — Claude Code documentation: Configure permissions — https://code.claude.com/docs/en/permissions — checked 2026-10-29
- [13] Birgitta Böckeler — Context Engineering for Coding Agents (martinfowler.com, 2026; opinion) — https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html — checked 2026-10-29
- [14] Anthropic — Claude Code documentation: Settings reference — https://code.claude.com/docs/en/settings-reference.md — checked 2026-10-29
- [15] anthropics/claude-code — Security Gap: Hooks Cannot Be Protected From Modification (Edit/Write tools bypass permissions.deny), issue #11226 (GitHub, 2025; case) — https://github.com/anthropics/claude-code/issues/11226 — checked 2026-10-29
- [16] Anthropic — Claude Code documentation: Choose a permission mode — https://code.claude.com/docs/en/permission-modes.md — checked 2026-10-29
- [17] Chuyang Chen and Zhiqiang Lin — One Goal, Many Commands: Characterizing Denylist Fragility in AI Agents (arXiv 2606.15549, 2026; research) — https://arxiv.org/abs/2606.15549 — checked 2026-10-29
- [18] Anthropic — Claude Code security advisories (anthropics/claude-code on GitHub) — https://github.com/anthropics/claude-code/security — checked 2026-10-29
- [19] Anthropic — Claude Code documentation: Sandboxing — https://code.claude.com/docs/en/sandboxing — checked 2026-10-29
- [20] Anthropic — Claude Code documentation: Hooks reference — https://code.claude.com/docs/en/hooks.md — checked 2026-10-29
- [21] PeopleCert — PRINCE2 7 Practitioner Sample Paper 1, Answers and Rationales (a copy hosted by prince2.wiki, a training firm) — https://prince2.wiki/downloads/p2p-a1.pdf — checked 2026-10-29
- [22] Nenad Tomašev, Matija Franklin and Simon Osindero — Intelligent AI Delegation (arXiv 2602.11865, 2026; opinion) — https://arxiv.org/abs/2602.11865 — checked 2026-10-29
- [23] Yonadav Shavit et al. — Practices for Governing Agentic AI Systems (OpenAI, 2023; opinion) — https://cdn.openai.com/papers/practices-for-governing-agentic-ai-systems.pdf — checked 2026-10-29
- [24] Liu et al. — Are Your Agents Upward Deceivers? (arXiv 2512.04864, 2025; research) — https://arxiv.org/abs/2512.04864 — checked 2026-10-29
- [25] Laksh Advani — From Confident Closing to Silent Failure: Characterizing False Success in LLM Agents (arXiv 2606.09863, 2026; kind not confirmed) — https://arxiv.org/abs/2606.09863 — checked 2026-10-29
- [26] Noam Kolt — Governing AI Agents (Notre Dame Law Review, vol. 101, 2026; opinion) — https://ndlawreview.org/wp-content/uploads/2026/08/Kolt_101.335.pdf — checked 2026-10-29
- [27] Sanidhya Vijayvargiya, Xuhui Zhou, Akhila Yerukola, Maarten Sap and Graham Neubig — Ambig-SWE: Interactive Agents to Overcome Underspecificity in Software Engineering (arXiv 2502.13069, 2026; research) — https://arxiv.org/abs/2502.13069 — checked 2026-10-29
- [28] Jinyan Su and Claire Cardie — Knowing but Not Showing: LLMs Recognize Ambiguity but Rarely Ask Clarifying Questions (arXiv 2605.25284, 2026; research) — https://arxiv.org/abs/2605.25284 — checked 2026-10-29
- [29] Anthropic — Measuring AI agent autonomy in practice (Anthropic Research, 2026; case: the vendor's telemetry on its own product) — https://www.anthropic.com/research/measuring-agent-autonomy — checked 2026-10-29
- [30] European Commission, AI Act Service Desk — Regulation (EU) 2024/1689, Article 14: Human oversight, consolidated version as at 27 July 2026 — https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14 — checked 2026-10-29
- [31] Ori Ron and Dor Tumarkin — HITL Dialog Forging (aka Lies-in-the-Loop) (OWASP community attacks page, no date; opinion) — https://owasp.org/www-community/attacks/Lies_in_the_Loop — checked 2026-10-29
- [32] Georgios Alexopoulos, Nikolaos Alexopoulos, Diomidis Spinellis and Dimitris Mitropoulos — When AI Agrees Too Much: Manipulating Automated Code Review via Bias Injection (arXiv 2603.18740, 2026; research) — https://arxiv.org/abs/2603.18740 — checked 2026-10-29
- [33] Fogliato et al. — Sevra-Bench: Social Engineering of Vulnerabilities in Review Agents (arXiv 2606.13757, 2026; research) — https://arxiv.org/abs/2606.13757 — checked 2026-10-29
- [34] Crootof, Kaminski and Price — Humans in the Loop (Vanderbilt Law Review, vol. 76, 2023; opinion) — https://wp0.vanderbilt.edu/lawreview/wp-content/uploads/sites/278/2023/03/Humans-in-the-Loop.pdf — checked 2026-10-29
- [35] Elish — Moral Crumple Zones: Cautionary Tales in Human-Robot Interaction (Engaging Science, Technology, and Society, 2019; opinion) — https://estsjournal.org/index.php/ests/article/download/260/177 — checked 2026-10-29
- [36] Green — The flaws of policies requiring human oversight of government algorithms (Computer Law & Security Review, 2022; opinion) — https://arxiv.org/abs/2109.05067 — checked 2026-10-29
- [37] Bainbridge — Ironies of Automation (Automatica, 1983; opinion) — https://doi.org/10.1016/0005-1098(83)90046-8
- [38] Ting Yan — Do User-Authored Permission Policies Improve Protection Against AI Agent Overreach? (arXiv 2608.27443, 2026; research) — https://arxiv.org/abs/2608.27443 — checked 2026-10-29
- [39] Chaoran Chen et al. — Comparing Human Oversight Strategies for Computer-Use Agents (arXiv 2604.04918, 2026; research) — https://arxiv.org/abs/2604.04918 — checked 2026-10-29
- [40] Bravo-Lillo, Cranor, Komanduri, Schechter and Sleeper — Harder to Ignore? Revisiting Pop-Up Fatigue and Approaches to Prevent It (SOUPS, 2014; research) — https://www.usenix.org/system/files/soups14-paper-bravo-lillo.pdf
- [41] Vance, Kirwan, Bjornn, Jenkins and Anderson — What Do We Really Know about How Habituation to Warnings Occurs Over Time? A Longitudinal fMRI Study of Habituation and Polymorphic Warnings (CHI, 2017; research) — https://www.cl.cam.ac.uk/events/shb/2017/vance1.pdf
- [42] Vance, Jenkins, Anderson, Bjornn and Kirwan — Tuning Out Security Warnings: A Longitudinal Examination of Habituation Through fMRI, Eye Tracking, and Field Experiments (MIS Quarterly, 2018; kind not confirmed) — https://aisel.aisnet.org/misq/vol42/iss2/3
- [43] Anthropic — Auto mode is now the default in Claude Code for Pro, Max, and Team plans (Claude blog, 2026; research, sponsored by Anthropic: the vendor's study of its own product) — https://claude.com/blog/auto-mode-default-in-claude-code
- [44] Parasuraman and Manzey — Complacency and Bias in Human Use of Automation: An Attentional Integration (Human Factors, 2010; kind not confirmed) — https://pubmed.ncbi.nlm.nih.gov/21077562/ — checked 2026-10-29
- [45] NIST — Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile, NIST AI 600-1, July 2024 — https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf — checked 2026-10-29
- [46] Goddard, Roudsari and Wyatt — Automation bias: a systematic review of frequency, effect mediators, and mitigators (JAMIA, 2012; research) — https://pmc.ncbi.nlm.nih.gov/articles/PMC3240751 — checked 2026-10-29
- [47] Alon-Barkat and Busuioc — Human-AI Interactions in Public Sector Decision Making: "Automation Bias" and "Selective Adherence" to Algorithmic Advice (Journal of Public Administration Research and Theory, 2023; research) — https://arxiv.org/abs/2103.02381 — checked 2026-10-29
- [48] Bansal, Wu, Zhou, Fok, Nushi, Kamar, Ribeiro and Weld — Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance (CHI, 2021; research) — https://arxiv.org/abs/2006.14779 — checked 2026-10-29
- [49] Vasconcelos, Jörke, Grunde-McLaughlin, Gerstenberg, Bernstein and Krishna — Explanations Can Reduce Overreliance on AI Systems During Decision-Making (CSCW, 2023; research) — https://arxiv.org/abs/2212.06823 — checked 2026-10-29
- [50] Anthropic — How we built our multi-agent research system (Anthropic Engineering, 2025; case: the vendor's own system) — https://www.anthropic.com/engineering/multi-agent-research-system — checked 2026-10-29
- [51] Yuxuan Li, Aoi Naito and Hirokazu Shirado — Systematic Failures in Collective Reasoning under Distributed Information in Multi-Agent LLMs (arXiv 2505.11556, 2026; research) — https://arxiv.org/abs/2505.11556 — checked 2026-10-29
- [52] Dat Tran and Douwe Kiela — Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets (arXiv 2604.02460, 2026; research) — https://arxiv.org/abs/2604.02460 — checked 2026-10-29
- [53] Yubin Kim et al. — Towards a Science of Scaling Agent Systems (arXiv 2512.08296, 2026; research) — https://arxiv.org/abs/2512.08296 — checked 2026-10-29
- [54] Lars Benedikt Kaesberg et al. — Voting or Consensus? Decision-Making in Multi-Agent Debate (arXiv 2502.19130, 2025; research) — https://arxiv.org/abs/2502.19130 — checked 2026-10-29
- [55] Zhiyuan Weng, Guikun Chen and Wenguan Wang — Do as We Do, Not as You Think: the Conformity of Large Language Models (arXiv 2501.13381, 2025; research) — https://arxiv.org/abs/2501.13381 — checked 2026-10-29
- [56] Hyeong Kyu Choi, Xiaojin Zhu and Sharon Li — Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models? (arXiv 2508.17536, 2025; research) — https://arxiv.org/abs/2508.17536 — checked 2026-10-29
- [57] Andries Smit et al. — Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs (arXiv 2311.17371, 2024; research) — https://arxiv.org/abs/2311.17371 — checked 2026-10-29
- [58] Blaž Bertalanič and Carolina Fortuna — The Cost of Consensus: Isolated Self-Correction Prevails Over Unguided Homogeneous Multi-Agent Debate (arXiv 2605.00914, 2026; research) — https://arxiv.org/abs/2605.00914 — checked 2026-10-29
- [59] Elliot Kim, Avi Garg, Kenny Peng and Nikhil Garg — Correlated Errors in Large Language Models (arXiv 2506.07962, 2025; research) — https://arxiv.org/abs/2506.07962 — checked 2026-10-29
- [60] Chuan He, Zebin Chen, Zhengyi Yang et al. — Minority Sentinel: When to Overturn Majority Voting in Multi-Agent LLM Debates (arXiv 2606.29270, 2026; research) — https://arxiv.org/abs/2606.29270 — checked 2026-10-29
- [61] Han — Partially Correlated Verifier Cascades in LLM Harnesses (arXiv 2607.13918, 2026; research) — https://arxiv.org/abs/2607.13918 — checked 2026-10-29
- [62] Tianyang Xu, Dan Zhang, Kushan Mitra and Estevam Hruschka — Verification-Aware Planning for Multi-Agent Systems (arXiv 2510.17109, 2025; research) — https://arxiv.org/abs/2510.17109 — checked 2026-10-29
- [63] Jason Liu — When May an Agent Stop? Evidence-Carrying Termination for Tool-Using LLMs (arXiv 2608.23623, 2026; research) — https://arxiv.org/abs/2608.23623 — checked 2026-10-29
- [64] Ken Tsui — Self-Correction Bench: Uncovering and Addressing the Self-Correction Blind Spot in Large Language Models (arXiv 2507.02778, 2026; kind not confirmed) — https://arxiv.org/abs/2507.02778 — checked 2026-10-29
- [65] Cemri et al. — Why Do Multi-Agent LLM Systems Fail? (arXiv 2503.13657, 2025; research) — https://arxiv.org/abs/2503.13657 — checked 2026-10-29
- [66] Julian Berger, Pantelis P. Analytis, Ville Satopää and Ralf H.J.M. Kurvers — Beyond AI advice: independent aggregation boosts human-AI accuracy (arXiv 2603.29866, 2026; research) — https://arxiv.org/abs/2603.29866 — checked 2026-10-29
- [67] Recchia, Mangat, Nyachhyon, Sharma, Canavan, Epstein-Gross and Abdulbari — Confirmation bias: A challenge for scalable oversight (arXiv 2507.19486, 2025; research) — https://arxiv.org/abs/2507.19486 — checked 2026-10-29
- [68] Davidson — Coding Agents Love Decision Records (O’Reilly Radar, 2026; opinion) — https://www.oreilly.com/radar/coding-agents-love-decision-records/ — secondary: read through the Internet Archive copy of 2026-10-19, https://web.archive.org/web/20261019053722/https://www.oreilly.com/radar/coding-agents-love-decision-records/ — checked 2026-10-29
- [69] Chen et al. — Reasoning Models Don’t Always Say What They Think (arXiv 2505.05410, 2025; research, sponsored by Anthropic) — https://arxiv.org/abs/2505.05410 — checked 2026-10-29
- [70] Turpin, Michael, Perez and Bowman — Language Models Don’t Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting (NeurIPS, 2023; research) — https://arxiv.org/abs/2305.04388 — checked 2026-10-29
- [71] Zaman and Srivastava — Is Chain-of-Thought Really Not Explainability? Chain-of-Thought Can Be Faithful without Hint Verbalization (arXiv 2512.23032, 2026; research) — https://arxiv.org/abs/2512.23032 — checked 2026-10-29
- [72] Costa da Silva and Gama — GADR: Gathering Architecture Decision Records from Meeting Transcriptions (arXiv 2608.17694, 2026; research) — https://arxiv.org/abs/2608.17694 — checked 2026-10-29
- [73] Dhar, Kakran, Karan, Vaidhyanathan and Varma — DRAFT-ing Architectural Design Decisions using LLMs (arXiv 2504.08207, 2025; research) — https://arxiv.org/abs/2504.08207 — checked 2026-10-29
- [74] Olaf Zimmermann — Ten Common Mistakes in Architectural Decision Records (ADRs) (ozimmer.ch, 2026; opinion) — https://ozimmer.ch/practices/2026/09/12/ADRMistakes.html — checked 2026-10-29
- [75] Martin Fowler — Fragments: September 8 (martinfowler.com, 2026; opinion) — https://martinfowler.com/fragments/2026-09-08.html — checked 2026-10-29
- [76] Simon Willison — Vibe coding and agentic engineering are getting closer than I’d like (Simon Willison’s Weblog, 2026; opinion) — https://simonwillison.net/2026/May/6/vibe-coding-and-agentic-engineering/ — checked 2026-10-29
- [77] Su, Bakhtin, Ahmad, Esposito, Lenarduzzi and Taibi — Evaluating Large Language Models for Detecting Architectural Decision Violations (arXiv 2602.07609, 2026; research) — https://arxiv.org/abs/2602.07609 — checked 2026-10-29
- [78] UK Information Commissioner's Office — Previously asked questions (innovation advice) — https://ico.org.uk/for-organisations/advice-and-services/innovation-advice/previously-asked-questions/ — checked 2026-10-29
- [79] LangChain — LangChain documentation (Python): Human-in-the-loop — https://docs.langchain.com/oss/python/langchain/human-in-the-loop — checked 2026-10-29
- [80] Michelle Vaccaro, Abdullah Almaatouq and Thomas Malone — When combinations of humans and AI are useful: A systematic review and meta-analysis (Nature Human Behaviour, 2024; research) — https://arxiv.org/abs/2405.06087 — checked 2026-10-29
- [81] Yu, Liu, Jiang, Jia, Wang, Qian and Chen — Habituation at the Gate: Rising Approval and Declining Scrutiny in Human Review of AI Agent Code (arXiv 2606.22721, 2026; research) — https://arxiv.org/abs/2606.22721 — checked 2026-10-29
- [82] Xiaochen Zhu, Caiqi Zhang, Yizhou Chi, Tom Stafford, Nigel Collier and Andreas Vlachos — Demystifying Multi-Agent Debate: The Role of Confidence and Diversity (Findings of ACL, 2026; kind not confirmed) — https://aclanthology.org/2026.findings-acl.1694.pdf — checked 2026-10-29
- [83] Yilun Du et al. — Improving Factuality and Reasoning in Language Models through Multiagent Debate (arXiv 2305.14325, 2023; research) — https://arxiv.org/abs/2305.14325 — checked 2026-10-29
- [84] Anthropic — Claude Code documentation: Deploy managed settings — https://code.claude.com/docs/en/managed-settings
- [85] Anthropic — Claude Code documentation: How Claude remembers your project — https://code.claude.com/docs/en/memory
