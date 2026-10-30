# Deciding as a team: input, the decision, its record and its review

This file is for everyone who takes part in a decision that other people will live with: a
developer who proposes a change, a tech lead or a project manager who decides, a maintainer of an
open-source project, and an AI agent asked to choose between options or to write a decision down.
It says how much process a decision gets, how to gather input before it, how a discussion closes,
what happens to objections, how an architecture decision record is written and kept, and how a
decision is reviewed later. Who decides each kind of decision, the roles of DACI (Driver,
Approver, Contributors, Informed) and the decision log belong to
[roles-and-decisions.md](../project-management/roles-and-decisions.md) sections 5 to 8; this file
links them and adds the steps around them. What an AI agent may decide on its own, and
what the person who approves its actions needs, is part two: [agents.md](agents.md).

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. The steps of a decision](#2-the-steps-of-a-decision)
- [3. How much process a decision gets](#3-how-much-process-a-decision-gets)
- [4. Gathering input before the decision](#4-gathering-input-before-the-decision)
- [5. Deciding after advice, and when a group votes](#5-deciding-after-advice-and-when-a-group-votes)
- [6. Closing the discussion](#6-closing-the-discussion)
- [7. Objections and commitment](#7-objections-and-commitment)
- [8. Architecture decision records](#8-architecture-decision-records)
- [9. Reviewing a decision](#9-reviewing-a-decision)
- [10. People in the record](#10-people-in-the-record)
- [11. Common mistakes](#11-common-mistakes)
- [12. Where the rules stop holding](#12-where-the-rules-stop-holding)
- [13. Alternatives considered](#13-alternatives-considered)
- [14. Adoption in existing work](#14-adoption-in-existing-work)
- [15. Review checklist](#15-review-checklist)
- [16. Sources](#16-sources)

## 1. Purpose and the one rule

Most decisions a team makes go well with no process at all. The ones that go wrong tend to go
wrong the same way: nobody is sure who decides, the person who holds the key fact hears the boss's
view first and stays quiet, the discussion never ends, an objection gets lost, and a year later
nobody knows why the team chose what it chose. A team that follows this file names the decider and
the weight of each decision before the argument starts, hears the facts before the preferences,
closes the discussion on a date, answers each objection in writing, and keeps a record of its
hard-to-undo technical choices that a later reader can trust.

The one rule: **every decision that others will live with has one named decider and a level of
process set before the input starts, and its record is written before the outcome is known and is
never rewritten after.**

Why it holds the rest together:

- Skipping the people affected costs the most. Nutt studied 356 decisions by senior managers in
  organisations in the US and Canada: "Edicts were observed in 40 percent of the cases and had the
  highest failure rate. When implementation was attempted by edict, 53 percent of the decisions
  were sustained for two years, and only 35 percent were fully used" [1]. It is a field study
  the author coded himself, with no group that consulted and then let one person decide, so it is
  a reason not to skip consultation, not proof that the steps below are the best ones.
- Facts that only one person holds get lost in an open discussion. The abstract of Lu, Yuan and
  McLeod's meta-analysis of 65 studies, mostly laboratory groups, reports that "hidden profile
  groups were eight times less likely to find the solution than were groups having full
  information" [2].
- People judge a decision by how it turned out. In Baron and Hershey's five studies with
  undergraduates, "Although subjects who were asked felt that they should not consider outcomes in
  making these evaluations, they did so" [3]. A record made before the outcome is what a
  later review can judge the decision against (section 9).
- A decision nobody wrote down gets made again. Microsoft's architecture guidance: "A decision
  that's made but never recorded will likely be forgotten, leading to repeated debates or later
  changes that unknowingly contradict the original intent" [4].

What it leaves out on purpose, and where that lives:

- Who decides each kind of decision, the DACI roles and the due date, the decision log, and the
  RACI matrix against the decider:
  [roles-and-decisions.md](../project-management/roles-and-decisions.md) sections 5, 6, 7 and 8.
- The escalation path, and the exception note that brings a decision to a higher level:
  [communication.md](../project-management/communication.md) sections 4 and 5.
- The pre-mortem: [risks.md](../project-management/risks.md) section 8.
- The go or no-go decider and the rollback decider:
  [release.md](../project-management/release.md) section 3 and
  [rollback-plan.md](../project-management/rollback-plan.md) section 2.
- The rule that a meeting names the decision it makes:
  [meetings.md](../project-management/meetings.md) section 1.
- Decisions with AI agents: [agents.md](agents.md). How an agent applies this file, with the
  routing line and the mistakes agents make, is [agents.md](agents.md) section 13, which covers
  both files.
- Security: there are no known security impacts of the rules in this file. The threats that come
  with AI agents are mapped in [agents.md](agents.md) section 8. What a record may say about the
  people in it is section 10.

Not covered yet, because the research found no source it could read (section 12 gives the
detail): the text of the decision clauses of ISO/IEC/IEEE 15288:2023 and 42010:2022, the decision
techniques of PMBOK 8 and the current Agile Practice Guide, the mediating assessments protocol in
its authors' words, the sample of Schweiger et al. 1986, a comparison of consensus, majority vote
and a single decider, a measured test of a written input round and of "the leader speaks last", a
measured study of recording dissent and committing while disagreeing, a study that records help
later maintainers, the cost of writing a record, a validation of the six elements of decision
quality, a phase-end review of decisions as a published rule, and how often teams misjudge whether
a decision can be undone.

## 2. The steps of a decision

A decision that others will live with needs these steps. A choice inside one person's own work
that is easy to undo and clear does not: the person doing the work decides
([roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5, the row "How a
work item is built"). GitLab's handbook says the same of its directly responsible individual: "The
DRI has final decision-making power but should consult and collaborate with relevant stakeholders
to gather input and divide tasks effectively" [5]. Section 3 says which decisions need
which steps.

- **Before any input is asked for, write the question the decision answers and name its decider**,
  from [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5 or, in a
  group with no single decider, from the group's written rule (section 5 here), so everyone knows
  who decides before they argue. SEBoK's decision management holds that "The best practice is to
  identify a decision problem statement that defines the decision in terms of the system life
  cycle" [6]. Atlassian's DACI play titles its page with the question the team is trying to
  answer [7].
- **Keep the two phases apart: first gather input, then decide.** GitLab names "A data gathering
  phase in which folks are actively asked to contribute data and perspectives that can inform
  decision making." and "A decision phase in which an informed individual can make a decision
  without getting an approval from others" [8]. Apache keeps them in separate threads: "A
  consensus-building thread is often indicated by a subject line starting with [DISCUSS]." and a
  vote then starts "a new thread with a subject line starting with [VOTE]" [9]. Rust's
  process runs a discussion, then a "motion for final comment period" with "a *disposition* for the
  RFC (merge, close, or postpone)" [10].
- **Run the steps in this order**, which is this practice's own sequence of the sections below;
  each step carries its own sources there:

  1. Frame the question and name the decider (this section).
  2. Set the level (section 3).
  3. Gather input (section 4).
  4. Close the discussion on its date with a disposition (section 6).
  5. The decider decides and records it: an architecture decision record for a technical choice
     (section 8), and the log line of
     [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 7 when that
     section asks for one.
  6. People act on it, and reopen it only with new facts (section 7).
  7. Review it when a trigger fires (section 9).

## 3. How much process a decision gets

Process costs time, and most decisions do not need much of it. Jeff Bezos, writing about Amazon,
holds that some decisions are "one-way doors" that "must be made methodically, carefully, slowly,
with great deliberation and consultation", while "most decisions aren’t like that – they are
changeable, reversible – they’re two-way doors" [11]. He adds that "Type 2 decisions can and
should be made quickly by high judgment individuals or small groups", and that large organisations
tend "to use the heavy-weight Type 1 decision-making process on most decisions, including many
Type 2 decisions" [11]. A year later he put it as "never use a one-size-fits-all
decision-making process" [12]. The levels below are needed from the first decision a team
shares; filling them in as a form for an easy and clear choice inside one person's work is too much. The
simpler way for such a choice: the decider of
[roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5 decides, and a
line in the section 7 log is the record when the log asks for one.

- **Before the first input is asked for, set the decision's level by three signs read together:
  whether it is hard to undo, whether it changes other people's work or crosses teams, and whether
  the problem or the answer is unclear.** No source read uses reversibility alone. GitLab sets the
  line by who else is involved: "Decisions that require input, buy-in, or awareness of others
  should be accompanied by a brief, documented proposal" [8]. Malte Ubl, writing about
  design docs at Google, sets it by how unclear the design is: if the solution is not ambiguous,
  "then there is little value in going through the process of writing a doc" [13]. Rust asks for
  its process only for changes it calls "substantial" [10], and Python's PEP 1 says "Most
  enhancements and bug fixes don’t need a PEP and can be submitted directly to the Python issue
  tracker" [14].
- **Use three levels.** Each one adds steps to the one before. The UK government's framework for
  architecture decision records sets four levels, from a team up to all of government, each with
  its own decision-makers and the criterion that sends a decision one level up [15]. Gergely
  Orosz reports that at Uber, where "hundreds of RFCs went out weekly", the company moved to "A
  tiered approach. The company defined the process to decide how “critical” a change was" [16].
  The three levels here, and how they map onto
  [roles-and-decisions.md](../project-management/roles-and-decisions.md) sections 5 to 7, are this
  practice's own:

  | Level | What it means | Set it when | Leave it out when |
  |---|---|---|---|
  | 1. Own work | The person doing the work decides alone; nothing is written beforehand | the choice is easy to undo, touches only the decider's own work, and the problem and the answer are clear | any sign of level 2 or 3 holds |
  | 2. Others affected | The decider writes a short note of intent and waits a short window for objections before acting | the choice is easy to undo, but other people's work or a shared part changes | the choice is hard to undo, crosses teams or is unclear: that is level 3 |
  | 3. Hard to undo, crosses teams, or unclear | All the steps of section 2: a named decider, an input round, a comment window and a record; DACI where [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 6 calls for it | any one of the three signs holds | none of the three signs holds |

  | Level | Decider | Written proposal | Window to object | Record |
  |---|---|---|---|---|
  | 1 | the person doing the work ([roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5) | none | none | none required |
  | 2 | the decider section 5 names | a short note of intent | a short one, such as Apache's lazy consensus (section 6) | the log line, where [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 7 asks for one |
  | 3 | the Approver ([roles-and-decisions.md](../project-management/roles-and-decisions.md) section 6) when DACI runs, otherwise the decider [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5 names, or the group's rule of section 5 here | the DACI page where [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 6 calls for one; otherwise a written proposal with advice gathered on it, or the group's proposal | the comment window of section 6 | the DACI page when one runs, an architecture decision record for a technical choice (section 8), and the log line |

- **When the decision is easy to undo and the team will notice and fix a wrong call, decide before
  every gap in the facts is closed, and write down what is not known** (the Confidence field
  of the record, section 8). GitLab: "It is ok to make a judgment call with limited data, but make
  sure that is known" [8]. Bezos holds that "most decisions should probably be made with
  somewhere around 70% of the information you wish you had", on his own condition: "you need to be
  good at quickly recognizing and correcting bad decisions" [12]. The 70% is one person's
  rule of thumb, not a measured threshold, so this file does not use it as one.
- **Judge "hard to undo" by what undoing would take: data already stored, a published interface, a
  contract, or other teams' code built on it.** This test is the practice's own; no source read
  gives one for decisions people make. For an action an AI agent takes, what the platform can undo
  decides it ([agents.md](agents.md) section 2).

## 4. Gathering input before the decision

When the people in a decision hold different facts, an open discussion tends to lose the facts
only one person has. Stasser and Titus gave groups of four students the facts about three
candidates: "In the shared condition, 83% of the 18 groups chose Candidate A whereas only 18% of
the 38 groups in the unshared conditions chose A" [17]. When everyone already holds the same
facts this failure does not arise, so the input round adds little; that is this practice's own
reading of the shared condition in their study. The round is too much at levels 1 and 2. The
simpler way there: the decider asks the one or two people who know the area, as GitLab's
directly responsible individual "should consult" [5]. Andrew Harmel-Law holds that a
long list of people to consult is a sign the decision should be split into smaller ones
[18].

The evidence for asking at all: besides Nutt's edicts (section 1) [1], Wagner's review of the
research finds that "participation can have statistically significant effects on performance and
satisfaction, but the average size of these effects is small enough to raise concerns about
practical significance" [19]. The two measure different things, so both hold: do not skip
consultation, and do not expect a large gain from adding more of it.

- **Before the meeting that decides, or before the decider reads the thread, ask each Contributor
  for facts, concerns and estimates in writing, each on their own, before anyone, the Approver
  included, says which option they prefer.** The reason is in the abstracts of three laboratory
  studies of hidden-profile tasks, where the right answer is set by the experimenters. Mojzisch and
  Schulz-Hardt found that "learning the other group members' preferences at the beginning of a
  discussion impedes the solution of hidden profiles" [20]. Schulz-Hardt et al., with 135
  three-person groups, found that groups whose members started from the same wrong preference
  "hardly ever solved the hidden profile", while "solution rates were significantly higher in groups
  with prediscussion dissent" [21]. No study read tested a written round; "in writing" is
  this practice's own way to keep the views apart.
- **Ask for facts and concerns in that first round, not for a preferred option.** Faulmüller et al.
  found in two laboratory experiments that "group members tend to stick to their suboptimal initial
  decision preferences due to preference-consistent evaluation of information" [22]. The
  abstract of Greitemeyer et al. reports that advocacy groups discussed more shared and more
  unshared facts than free-discussion groups, "Yet advocacy groups did not significantly improve
  their decision quality with experience" [23]. This practice reads that as a reason to keep
  preferences out of the first round, and not only to pool more facts.
- **After the round, reason about the problem together; do not just add up the first answers.**
  Navajas et al. ran a live crowd of 5,180 people on estimates with a true answer: "Participants
  first answered individually, then deliberated and made consensus decisions in groups of five",
  and "averaging consensus decisions was substantially more accurate than aggregating the initial
  independent opinions" [24]. Barrera-Lemarchand et al., in online group chats, found that
  "groups instructed to apply problem decomposition outperform groups instructed to combine their
  initial guesses" [25].
- **The Approver states no preference before the input is in, and speaks last in the meeting.** In
  Leana's experiment with 208 students, "Groups with directive leaders were also willing to comply
  with the leaders' proposed solutions when the leaders stated their preferences early in the group
  discussion" [26]. The abstract of Richardson Ahlfinger and Esser reports that "Groups with
  promotional leaders produced more symptoms of groupthink, discussed fewer facts, and reached a
  decision more quickly" [27]. Amazon describes its own meetings: "The most senior
  attendees tend to speak last, to avoid influencing others" [28]. No study tests "speak last"
  as a step; the rule is this practice's inference from these.
- **Before the decision, ask the people most likely to object for their objections.** Will Larson
  advises "mining for dissent from the folks who are most likely to have objections" [29]. The
  abstract of Nemeth et al. reports that "the authentic minority was superior to all three forms of
  ‘devil's advocate,’" [30], so a real objector is worth more than a role played.
- **When the decider decides, write how the advice changed the decision: what changed and why, or
  why it did not.** Across many studies of advice on numeric estimates, mostly by students, Bailey
  et al. found that "the overall pooled weight of advice (k = 346) was 0.39, 95% CI [0.37, 0.42]"
  [31]. People move well short of the advice they get, and carrying that to team decisions is
  an inference. Harmel-Law's advice process asks the same of the decider: "they must listen to and
  record it" [18].
- **A meeting that decides opens with time to read the proposal.** AWS: "The review meeting should
  start with a dedicated time slot to read the ADR. On average, 10 to 15 minutes should be enough"
  [32]. Bezos describes the same at Amazon: "We silently read one at the beginning of each meeting
  in a kind of “study hall”" [33]. A shared read gives everyone the same facts; it does not
  keep views apart, which is the first rule's job.
- **Before the input round, the Driver checks whether someone on the Informed list holds facts the
  decision needs, and makes that person a Contributor.** The check itself is this practice's own,
  from the hidden-profile findings above;
  the roles stay as [roles-and-decisions.md](../project-management/roles-and-decisions.md) section
  6 defines them. An Informed person who holds no fact the decision needs stays Informed and hears
  the result.

## 5. Deciding after advice, and when a group votes

A team with a named decider does not need a voting rule; a written voting rule there adds a second
decider. A group with no single decider needs one.

| Method | What it means | Set it when | Leave it out when |
|---|---|---|---|
| Decide after advice | One named person decides after asking the Contributors (with DACI), or the people affected and the experts (without DACI) | always, in a team with a named decider: this is the default | the group has no single decider |
| A vote under written rules | Members with a binding vote decide by a count the rules fix | a group with no single decider, such as an open-source community | a team that has a named decider |
| Rough consensus | A chair judges that every issue was addressed, with an appeal | a group with a chair who judges, such as a standards working group | a group with no one to judge, or a team with a named decider |
| Consent | A proposal passes when nobody holds an objection | a policy a whole group must live with, when the group agrees to use the method | a group that has not agreed to use it |

- **In a team with a named decider, the decider decides after advice; the team does not vote.**
  Harmel-Law: "The Rule: anyone can make an architectural decision." The qualifier is that "the
  decision-taker must consult two groups: The first is everyone who will be meaningfully affected
  by the decision. The second is people with expertise in the area the decision is being taken."
  The decider is "in no way obliged to agree with the advice" [18]. GitLab holds that "Voting
  on material decisions shows a lack of informed leadership" [8]. In a DACI team the
  Contributors have no vote
  ([roles-and-decisions.md](../project-management/roles-and-decisions.md) section 6).

Advanced use: **a group with no single decider**, such as an open-source community or a standards
group.

- **Decide by a vote under written rules that say who has a binding vote, how many binding votes
  pass a decision, how long the vote runs, and that a veto needs a reason.** Apache: "A veto without
  a justification is invalid and has no weight" [34]. Its lightest form is "Lazy consensus
  is simply an announcement of 'silence gives assent.'" [34], and its glossary defines
  consensus approval as "a vote (sense 1) which has completed with at least three binding +1 votes
  and no vetos" [35]. Both Apache and Python treat the vote as a last step: "In ASF
  projects we don’t like to vote" [9], and PEP 13 tells Python's council: "Instead of
  voting, it’s better to seek consensus" [36].
- **Use rough consensus only where a chair judges whether each issue was addressed.** RFC 7282:
  "Rough consensus is achieved when all issues are addressed, but not necessarily accommodated"
  [37]. The chair declares it when "the working group has made an informed decision that the
  objection has been answered or is not enough of a technical problem to prevent moving forward"
  [37], and an objector who disagrees can appeal. With no chair there is nobody to judge, so
  it is not a method for a group with no decider.
- **Use consent for a policy the whole group must live with, when the group has agreed to use it.**
  Sociocracy 3.0 defines an objection as "an argument … that reveals consequences or risks that are
  preferably avoided for the organization or that demonstrates worthwhile ways to improve." and
  names "a policy or other significant decisions" as its most common use [38]. It asks groups new
  to the method to follow its steps strictly [38].

## 6. Closing the discussion

A discussion with no end date goes on until someone acts, and people learn of the decision after
it is made. The comment window is needed at level 3, a short one at level 2, and none at level 1.
The simpler way at level 2 is lazy consensus: the decider states the intent and waits; at Apache
that means "waiting an appropriate amount of time (usually 72 hours) for anyone to object"
[9].

- **When the comment window opens, announce its end date**, so nobody learns of the decision after
  it is made. The date by which the decision is due is
  [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 6's. Use 3 to 5
  business days as the default window. Oxide Computer's practice: "As a guideline, 3-5 business
  days to comment on your RFD before merging seems reasonable — but circumstances (e.g., time
  zones, availability of particular expertise, length of RFD) may dictate a different timeline"
  [39]. An open community with people in many time zones needs longer: in Rust, "The FCP lasts
  ten calendar days, so that it is open for at least 5 business days" [10].
- **End the window with one of three dispositions.** Rust ends its final comment period with "merge,
  close, or postpone" [10]. AWS ends its review when "the team accepts the ADR, determines that
  it needs rework, or rejects the ADR" [32]. No source read names the three below together; the
  set, and the date on a postponed decision, are this practice's own:

  | Disposition | What it means | Set it when | Leave it out when |
  |---|---|---|---|
  | Accept | The decider takes the proposal; the record moves to Accepted (section 8) | the open issues are answered | an issue is still open that the decider has not answered |
  | Reject, with the reason written in the record | The decider turns the proposal down and says why | the proposal will not go ahead | the proposal could go ahead after more work: postpone it |
  | Postpone, with the date it comes back | The record stays Proposed with the work it needs and a date | the proposal needs more work or a fact nobody has yet | the decider can decide now |

  The written reason for a rejection saves the next argument. AWS: "the ADR owner adds a reason for
  the rejection to prevent future discussions on the same topic" [32]. AWS's rework is the
  postpone case: "If the team finds action points to improve the ADR, the state of the ADR stays
  Proposed" [32].
- **Close on the open issues, never on a count of heads.** RFC 7282: "Simply having a large
  majority of people agreeing to dismiss an objection is not enough to claim there is rough
  consensus" [37].

## 7. Objections and commitment

An objection that reaches the decider is not enough; the answer to it is what counts. Noort et al.
coded the cockpit voice recordings of 172 aviation accidents and found that "flight crew spoke-up in
all but two accidents", concluding that "accidents cannot be assumed to emerge from a lack of safety
voice, or that the behaviour is sufficient for avoiding harm" [40]. In their data, poor
listening went with more damage, which puts the duty on the decider to answer. No source read says
when rules on objections are too much. The simpler way at levels 1 and 2: the objection goes to
the decider in person, and the note of intent records it only if the decider keeps the choice.

- **Record each objection raised before the decision, with the decision and with the decider's
  answer to it.** Which record holds it is set by
  [roles-and-decisions.md](../project-management/roles-and-decisions.md) sections 6 and 7, and by
  the Objections and answers field of section 8 for an architecture decision record. PEP 1
  makes the author "responsible for building consensus within the community and documenting
  dissenting opinions" [14]. NASA's formal dissent process asks that "When time permits, the
  disagreeing parties jointly document the issue, including agreed-to facts, discussion of the
  differing positions with rationale and impacts, and the parties, recommendations" [41]. What
  the record says about the person who objected is section 10.
- **After the decision, people who objected act on it, and may bring it back to the decider with
  new facts; the decider, too, reopens it only with new facts, through a new record (section
  8).** Bezos: "Third, use the phrase “disagree and
  commit.” This phrase will save a lot of time." and "This isn’t one way. If you’re the boss, you
  should do this too" [12]. GitLab: "Any past decisions and guidelines are open to questioning
  as long as you act in accordance with them until they are changed." and "You should communicate
  with the DRI who can change the decision instead of someone who can't" [42]. The
  measured support is indirect. The abstract of Dooley and Fryxell, on 86 strategic
  decision-making teams in US hospitals, reports that "Perceptions of within-team competence
  strengthen the relationship between dissent and decision commitment" [43]. The abstract of
  Korsgaard et al., an experiment with management teams, reports that "perceived fairness partially
  mediated the impact of procedures on commitment, attachment, and trust" [44]. No study
  read measures committing while disagreeing; the rule rests on the owners' texts and
  practitioners above.

Advanced use: **an objection about safety, or one the objector holds to be of real importance.**

- **It goes up the escalation path of [communication.md](../project-management/communication.md)
  section 4, starting above the decider, and the decider may go on at their own risk while it is
  open.** NASA's formal dissent "is documented and communicated by the dissenter in coordination with
  the disagreeing party at a minimum of two levels of management above the original program or
  project decision" [41]. While it is open, "the program/project manager has the authority to
  proceed at risk in parallel with the pursuit of a resolution" [41]. NASA keeps this for
  disagreements of importance, not for every objection. Mapping NASA's two levels onto the
  escalation path is this practice's own. TeamSTEPPS's two-challenge rule goes further: it
  "Empowers all team members to “stop the line” if they sense or discover an essential safety
  breach" [45]. It is written for an action under way in patient care, which is why this
  file does not let an objection stop a decision by itself.
- **Never use the record against the person who objected.** NASA: "Diverse views are to be fostered
  and respected in an environment of integrity and trust with no suppression or retribution"
  [41].

## 8. Architecture decision records

An architecture decision record (ADR) is a short file that holds one technical decision: its
context, the options, the choice, its consequences and its status. It is needed for a technical
choice that changes the system's structure or a key quality attribute, or is hard to reverse.
Microsoft's guidance: "Only include choices that affect the system's structure, key quality
attributes, or are difficult to reverse" [4]. A record for every small choice is too much.
Pureur and Bittner hold that "if every decision is architectural, no decision is architectural"
[46]. Olaf Zimmermann: "Not all decisions are worth capturing; triages are required" [47].
The UK's Government Digital Service: "While it won’t be mandated for day-to-day team decisions, it
will be needed for anything brought to the TDC" [48]. That is a scope for decisions sent to its
cross-government council, not advice against records in a team. No source read says that records
are too much for a small project. The simpler way for a choice below this bar: a line in the log of
[roles-and-decisions.md](../project-management/roles-and-decisions.md) section 7, or, in a project
with no such log, a note in the pull request that made the change (this practice's own
suggestion). Adoption is low in the open: the abstract of Buchgeher et al., on GitHub
repositories, reports that "the adoption of ADRs is still low" [49]. A worked record is in
[adr-example.md](adr-example.md).

- **Write an ADR for a technical choice that changes the system's structure or a key quality
  attribute, or is hard to reverse.** In a project that uses
  [roles-and-decisions.md](../project-management/roles-and-decisions.md), that includes every
  technical choice its section 5 names and its section 6 sends to DACI.
- **Open the ADR at Proposed, while the decision is under discussion; the decider sets it to
  Accepted or Rejected at the decision.** The ADR is the proposal, and it becomes the record by a
  status change. AWS: "the ADR owner provides the ADR in the Proposed state at the beginning of the
  process" [32]. Martin Fowler: "“proposed” while it is under discussion, “accepted” once the team
  accepts it and it is active" [50]. The abstract of Santana Junior et al. shows what goes
  wrong otherwise: "of a total of 5,800 ADRs, approximately 3,674 (about 63%) were opened directly
  with a status of “accepted” or equivalent, thereby bypassing the deliberative context that ADRs
  are intended to capture" [51].
- **Use Michael Nygard's short form [52] plus the fields below.** In a
  controlled experiment with undergraduates, "Nygard's template outperformed MADR in terms of the
  Overall Score" [53]. That supports a short form, with an options field added. The abstract
  of Falessi et al. argues for writing less: documenting only the items needed at least half the
  time "leads to a customized DRD containing about half the information items of a full
  documentation" [54].

  | Field | What it means | Set it when | Leave it out when |
  |---|---|---|---|
  | Title | The decision as a short phrase [52] | always | never |
  | Status | One value from the status table below, with the date of each change. The dates are this practice's own: MADR keeps one date, when the record was last updated [55], and AWS adds a timestamp when the team accepts [32]. | always | never |
  | Decider | The one person who sets the status: from [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5, or the group's rule of section 5 here. MADR's nearest field, "decision-makers", lists "everyone involved in the decision" [55]; one person is [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5's rule. | always | never |
  | Context | The problem and the forces at work [52] | always | never |
  | Options considered | Each serious option with its pros and cons and why it lost. Fowler: "explicitly list all the serious alternatives that were considered, together with their pros and cons" [50]. When DACI runs, a link to the DACI page's "Options considered" instead ([roles-and-decisions.md](../project-management/roles-and-decisions.md) section 6) | always; the link form when DACI runs | never; with only one real choice, say so and why (the check at the end of this section) |
  | Decision | The chosen option and why | always | never |
  | Consequences | Good and bad, technical and other. Nygard: "All consequences should be listed here, not just the "positive" ones" [52]. | always | never |
  | Objections and answers | Each objection raised, its author's name, job title and date, and the decider's answer (sections 7 and 10) | someone objected and no DACI page holds the objections | nobody objected, or the DACI page holds them |
  | Confidence | How sure the decider is, and what is not known. Microsoft: "Record the confidence level of the decision" [4]. | always | never |
  | Revisit when | The changes that would trigger a new look. Fowler: "This is a good place to mention any changes in the product context that should trigger the team to reevaluate the decision" [50]. | always | never |
  | Confirmation | How the team will check the decision was carried out, and what it expects to see if the decision works. MADR asks "how the implementation of/compliance with the ADR can/will be confirmed" [55]. The expected outcome is this practice's addition, from the decision journal Shane Parrish describes: "A paragraph explaining what you expect to happen" [56] | always; "no check planned" is a value | never |
  | Drafted by, accepted by | The agent that drafted the record and the person who accepted it ([agents.md](agents.md) section 7) | an agent drafted it | a person drafted it |
  | Links | The DACI page, the log entry, the work items | they exist | they do not |
  | Notes | Dated notes added after acceptance (the never-rewrite rule below) | a review or a later fact adds something | nothing was added after acceptance |

  | Status | What it means | Set it when | Leave it out when |
  |---|---|---|---|
  | Proposed | Under discussion; not binding | the record is opened | the decision is made |
  | Accepted | The decision in force | the decider accepts it | it was rejected, or never decided |
  | Rejected | Turned down, with the reason | the decider rejects it (section 6) | it was accepted |
  | Deprecated | No longer holds, and nothing replaces it | a decision stops holding with no successor | a new record replaces it: use Superseded |
  | Superseded by ADR-n | Replaced by a later record, named in the status | a new record changes the decision | the decision stands |

  Nygard names proposed, accepted, deprecated and superseded [52]; MADR adds rejected and the
  form "superseded by ADR-0123" [55].
- **Which record holds the options, the DACI page or the ADR, is
  [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 6's rule; the
  ADR's Options field holds them, or the link to the page that does.**
- **The decider sets the status, after the team has read and challenged the proposal; a group with
  no decider accepts by its written rule (section 5).** One decider per decision is
  [roles-and-decisions.md](../project-management/roles-and-decisions.md) section 5's rule.
  Zimmermann asks that "At least one mentor or peer and the team have challenged the AD and agree
  with outcome and rationale" [58]. At AWS the team approves and the owner records it: "If the
  team approves the ADR, the owner adds a timestamp, version, and list of stakeholders. The owner
  then updates the state to Accepted" [32]. Team acceptance is under Alternatives considered
  (section 13).
- **After Accepted or Rejected, never change the decision text.** Add dated notes below it. The
  one edit to the old record is its status line, when a later record supersedes it or the decision
  is deprecated. A changed decision is a new ADR that supersedes the old one, and each links the
  other. Microsoft: "The ADR serves as an append-only log. Don't go back and edit accepted records.
  If a decision changes, write a new record that supersedes the original and link the two
  together" [4]. AWS: "The team should treat ADRs as immutable documents after the team accepts
  or rejects them" [32]. Fowler: "Once an ADR is accepted, it should never be reopened or
  changed - instead it should be superseded. That way we have a clear log of decisions and how long they
  governed the work" [50]. Nygard: "If a decision is reversed, we will keep the old one around,
  but mark it as superseded" [52]. Allowing dated notes is this practice's middle way between
  these owners and the teams that edit records in place (section 13). A decision recorded only in
  the decision log follows the same rule for its entries
  ([roles-and-decisions.md](../project-management/roles-and-decisions.md) section 7).
- **When a decision no longer holds and nothing replaces it, set it to Deprecated, with the date
  and the reason.** A stale accepted record still reads as binding. One practitioner, Davidson,
  reports from the author's own projects: "In one case, an agent preserved an outdated storage abstraction
  across a new feature because an ADR still described it as mandatory" [59].
- **Keep ADRs in the repository the decision is about, one decision per file, numbered, under
  `docs/adr/`; a decision that covers several repositories goes where every team it affects
  reads.** Fowler keeps them in the code repository and notes that this does not work for records
  that cover more than one code base [50]. At IBM, Keeling and Runde's team kept one decision
  per record with the code, and a newcomer quoted in their report said: "I read the complete
  history of a few services and felt much better about this crazy ride I had signed up for"
  [60]. In Ahmeti et al.'s study at one company, where records were stored shaped how useful
  people found them [61]. The folder name `docs/adr/` is this practice's choice inside the
  `docs/` folder of [file-structure.md](../file-structure/file-structure.md) section 9.

Check: before the decider sets Accepted, read the record against Zimmermann's definition of done
[58]: does it hold the evidence, at least two real options compared (or the one real choice
and why), a challenge by a peer and the team, a place the team can read it, and a trigger or date
to look at it again? Zimmermann warns against made-up options added only to fill the template; when
there is one real choice, the record says so and why [58].

## 9. Reviewing a decision

A review asks whether a decision still holds, and whether the way it was made was sound. Reviews
help: the abstract of Tannenbaum and Cerasoli's meta-analysis reports that "debriefs improve
effectiveness over a control group by approximately 25% (d = .67)" [62]. No source read
says a decision is too small to review. This practice reviews only decisions that have an ADR or a
log entry, so level 1 decisions are not reviewed (its own line, from section 3). The simpler way:
when a trigger fires, the decider reads the record and adds one dated note.

- **Review a decision when a trigger in its Revisit-when field fires, when its outcome surprises the
  team, or when someone asks whether to keep a course that is failing.** Fowler's triggers are the
  changes "that should trigger the team to reevaluate the decision" [50]. Atlassian's
  decision-making retro, a vendor play for one or two people, starts "After a period with several
  impactful decisions, such as a major release, a contentious decision, or a surprise outcome"
  [63]. Sleesman et al. open their meta-analysis of 166 samples by calling escalation of
  commitment "One of the most robust and costly decision errors" [64], which is the authors'
  framing of the field.
- **When a record is accepted with a trigger tied to a date or a number, or a decision is
  postponed to a date (section 6), give that date or number a dated work item or an alert with an
  owner, and link it from the record's Links.** The reason: a trigger that nobody watches never
  starts a review. This is the practice's own view; no source read says it.
- **A team that holds a phase-end review
  ([life-cycle.md](../project-management/life-cycle.md) section 2) may look there at the ADRs whose
  triggers it cannot watch day to day.** This placement is this practice's own. Lovallo and Sibony,
  in a survey for McKinsey of 1,048 decisions in which managers rated both the process and the
  outcome, advise building such reviews into routine procedures: "It can be stimulated both by
  conducting postmortems of past decisions and by observing current decision processes"
  [65].
- **Read the record made before the outcome first; then judge the process by the six elements of
  decision quality.** The Decision Education Foundation names them: "Every one of the six elements
  is necessary to reach a quality decision: helpful frame, creative alternatives, useful
  information, clear values, sound reasoning, and commitment to follow through." It adds that "a
  decision is only as strong as the weakest link" [66]. The record comes first because outcomes
  bias the judge (section 1) [3]. Aiyer et al. replicated that bias with 692 people online
  judging one medical decision; the effect held "even for participants who stated that outcomes
  should not be taken into consideration when evaluating decisions (d = 0.64 [0.21, 1.08])"
  [67]. That last figure comes from a subgroup of 44 people. The abstract of Keiser and Arthur's
  meta-analysis of after-action reviews found that "objective performance review media" was one of
  two traits that "consistently contributed" to effective reviews [68]; the record made before
  the outcome plays that part.
- **On a complex decision, also look at the outcome data; never judge by the outcome alone.**
  Sharon et al., across 7 studies with 1,080 people, found that "outcome accountability exerts a
  beneficial effect in complex tasks (mean = −0.48 [95%CI: −0.62, −0.33]) whereas process
  accountability improves the performance in simpler tasks" [69]. Tetlock and Mellers warn
  that process accountability can turn into "impression management aimed at convincing superiors of
  how rigorous their analytical processes are" [70].
- **The decider or the team may lead the review; when the question is whether to keep a failing
  course, bring in someone who did not make the call.** Keiser and Arthur name "the self-led
  facilitation approach coupled with a team-aligned AAR, and the self-led approach coupled with
  objective media" as the most effective combinations [68]. For a failing course, Sleesman et
  al. report the advice "to shift escalation decisions to someone other than the initial decision
  maker" [64]. That is advice scholars have given, not a tested step; their data add that
  felt responsibility drives escalation "even if responsibility is merely assigned to decision
  makers" [64].
- **Write the result into the record: a dated note when the decision holds, a new ADR that
  supersedes it when it changes** (section 8), or, for a decision recorded only in the log, a new
  log entry that supersedes it ([roles-and-decisions.md](../project-management/roles-and-decisions.md)
  section 7). A note such as "reviewed on <date> by <name> after
  <trigger>; the decision holds" is enough; no source read says how a review that keeps a decision
  is logged, so this form is this practice's own. For the process, ask Atlassian's question: "Who
  needed to be involved but wasn’t (or vice versa)?" [63].
- **The pre-mortem is [risks.md](../project-management/risks.md) section 8's.** Its evidence for
  decisions is thin: Keysor et al.'s poster notes that "Few controlled, randomized experiments have
  been conducted to evaluate plan evaluation techniques and more are needed" and reports two small
  student experiments that measured confidence, not better plans [71].

## 10. People in the record

A decision record names people: the decider, the people who objected, and, when it is built from a
meeting, the people who spoke. This section applies to every record that names a person; no source
read gives a case where it is too much. The rules come from guidance by the UK Information
Commissioner's Office (ICO); other laws may differ, so ask the person who owns data protection in
your organisation. This section is the owner for both files of this practice; [agents.md](agents.md)
section 7 adds what an agent must do when it drafts a record.

- **Record what an objection says, its facts, the risk and the view it argues, and its author's
  name, job title and date where the record's purpose needs them; never write about the person's
  attitudes, motives or character.** The ICO says a record of an opinion "should state the date and
  the author’s name and position" [72]. Its guidance on access to information treats a recorded opinion as the speaker's own
  personal data when "it relates to her attitudes, state of mind and possibly her political
  beliefs" [73], and not when it is only about the subject under discussion. A person
  can ask for notes about them: in the ICO's example the employer "provided the notes that directly
  related to the worker’s own performance, but redacted the details about the performance of others
  on the team" [74].
- **A record built from a meeting transcript names its purpose and keeps the decision, the options,
  the decider and the objections with their authors; it leaves out what others said, and the raw
  transcript stays outside the repository.** The ICO: "So you should identify the minimum amount of
  personal data you need to fulfil your purpose. You should hold that much information, but no
  more" [72]. Only the first clause rests on that guidance; what the record keeps and leaves
  out is this practice's own reading of it.
- **Do not record the audio of a meeting by default.** The ICO's guidance on monitoring workers:
  "You should switch off by default any capability to record audio" [75]. The guidance is
  about monitoring, so this applies it to meetings by analogy.

## 11. Common mistakes

| Mistake | What it costs | Fix |
|---|---|---|
| The heavy process on most decisions | slowness, as Bezos describes for large organisations [11] | levels, section 3 |
| A vote in a team that has a named decider | a second decider; "a lack of informed leadership" [8] | section 5 |
| The Approver states a preference first | fewer options and facts, and compliance [26], [27] | section 4 |
| The first round asks for a preferred option | members stick to it [22] | facts and concerns first, section 4 |
| Advice collected and not weighed | people move well short of the advice [31] | write how the advice changed the decision, section 4 |
| A veto with no reason | "invalid and has no weight" under Apache's rules [34] | section 5 |
| Counting heads to close | a large majority "is not enough" [37] | close on the issues, section 6 |
| An objection heard and not answered | the response, not the voice, was the weak link in the accidents studied [40] | the answer in the record, section 7 |
| An ADR with no options | Zimmermann: "A decision that does not identify alternatives and chooses one of them is not a decision" [76]. Miccio et al. found "Considered Options" "absent or misplaced in most ADRs" in 4,316 open-source records [77] | the Options field, section 8 |
| An ADR opened as already accepted | about 63% in open source skipped the discussion [51] | open at Proposed, section 8 |
| Criteria built from the preferred option | "The criteria are reverse engineered solely from the properties of a preferred design option" [76]. | options and criteria before the choice, section 8 |
| No bad consequences listed | "No negative consequences are stated" [76]. | the Consequences field, section 8 |
| A record for every choice | "no decision is architectural" [46] | triage, section 8 |
| An accepted record edited in place | readers lose what governed the work and for how long [50] | dated notes and a superseding record, section 8 |
| An AI draft accepted without a check | "AI has taken over, but its output is used without quality check" [76]. One generator "sometimes transformed tentative discussions into accepted decisions" [78] | a person checks each fact and the status, [agents.md](agents.md) section 7 |
| A stale accepted record left as Accepted | an agent followed an obsolete rule [59] | Deprecated, section 8 |
| Judging a decision by its outcome | the judge rates the same decision better or worse by luck [3], [67] | the record first, section 9 |
| Keeping a failing course because one made the call | escalation of commitment [64] | someone else reviews, section 9 |

## 12. Where the rules stop holding

When a rule does not fit, and what following it costs:

- **A group with no single decider.** Decide-after-advice has nobody to decide; use a vote under
  written rules, rough consensus or consent (section 5).
- **Everyone holds the same facts.** The input round of section 4 adds little; give the time to the
  joint reasoning [25].
- **Disagree and commit has critics.** Christoph Nakazawa holds that it "makes visible disagreements
  disappear temporarily, but it keeps the underlying differences unresolved" [79]. This file
  keeps the rule because of the right to bring a decision back with new facts (section 7), and
  because no measured study supports either side.
- **The evidence is mostly from the laboratory.** The input rules rest on hidden-profile tasks with
  a right answer set by experimenters, mostly with students (section 4). The evidence for reducing
  bias in organisations is thin: the abstract of Fasolo et al.'s review says "Observing a lack of
  comparative studies, we propose a novel framework" [80].
- **What it costs.** A proposal takes writing time; Ubl: "Writing design docs is overhead" [13].
  A pre-read takes 10 to 15 minutes of each meeting [32]. Records must fit the team's work: the
  UK's Government Digital Service warns that "ADRs only work if they’re part of the team’s normal
  rhythm rather than bolt-ons or box-ticking exercises" [48], and in Ahmeti et al.'s case "some
  developers had difficulties integrating the creation of ADRs into their daily workflow" [61].

Not covered yet. The research for this file looked for these and found no source it could read:

- The decision management clause 6.3.3 of ISO/IEC/IEEE 15288:2023: only its table of contents was
  readable. SEBoK quotes the purpose from the 2015 edition [6].
- What ISO/IEC/IEEE 42010:2022 clauses 5.2.12 and 6.10 require: only their titles and the scope
  were readable, and the scope sentence "This document does not specify any format or media for
  recording an AD" [81] is about the architecture description as a whole.
- The decision techniques of PMBOK 8 and of the current Agile Practice Guide: neither text was
  readable.
- The mediating assessments protocol in its authors' own words: only secondary summaries were
  found.
- The sample and task of Schweiger et al. 1986: only the first sentence of the abstract was
  readable (section 13) [82].
- A meta-analysis that compares consensus, majority vote and a single decider. The nearest is a
  simulation by Hastie and Kameda, whose abstract reports that "the majority and plurality rules
  fare quite well" on tasks with a right answer [83]; it does not test a single decider.
- A measured test of an independent written input round, or of "the leader speaks last", in work
  teams.
- A measured study of recording dissent, committing while disagreeing, reopening with new facts, or
  escalating past the decider.
- A study that ADRs help later maintainers. The nearest evidence: the abstract of Shahin et al.
  reports that one experiment and the family of experiments "achieved a significantly better
  understanding of architecture design when using ADDs" [84]; Falessi et al. argue for writing
  less [54]; Ahmeti et al. found their study "too short to determine whether the use of ADRs
  makes the onboarding process less dependent on meetings with experienced team members" [61];
  Keeling and Runde report newcomers' own words [60]; and the abstract of Santana Junior et
  al. reports "predominantly small correlations with project quality metrics" [51].
- The cost of writing an ADR, and harm from long chains of superseded records.
- An empirical validation of the six elements of decision quality, and the wording of the
  consultancy that defined them.
- A phase-end review of decisions as a published rule.
- How often teams misjudge whether a decision can be undone.

## 13. Alternatives considered

- **Vroom's five decision styles as the vocabulary for who takes part.** Vroom's styles run from
  "Decide: You make the decision alone and either announce or sell it to the group." to "Delegate:
  You permit the group to make the decision within prescribed limits" [85]. Not taken: DACI
  already names the roles ([roles-and-decisions.md](../project-management/roles-and-decisions.md)
  section 6), and the validation is weak and self-reported. De la Poza Pérez's review reports that
  in the model's own test with 96 managers, 68% of the decisions they rated as successful fitted the
  model and 78% of the failed ones did not, and that a later field test of the 1988 version with 36
  officers found 48.4% [86]. With the styles not taken, their current attributes are not
  needed either.
- **Consent or rough consensus as the default for a decision the whole team lives with.** Not taken:
  no source read compares either with a deciding person on quality or acceptance, and each owner
  scopes its method (section 5) [38], [37].
- **A menu of decision techniques.** PMBOK's sixth edition listed voting and autocratic decision
  making; its errata add "Fig 5-4. Added bullet for autocratic decision making as tool & technique
  for decision making" [87]. The seventh edition's FAQ says the process groups and their tools
  "are no longer fully included in the publication" [88]. Not taken: a list with no rule for
  choosing gives a reader nothing to act on; section 5 names one default and the conditions for the
  others.
- **Ask every affected person before the decision, as the advice process does** [18]. Not taken
  where DACI runs: its Informed people hear the result
  ([roles-and-decisions.md](../project-management/roles-and-decisions.md) section 6), and no source
  read measured asking them against telling them. Without DACI, the advice process is the default
  (section 5).
- **The team accepts the ADR**, as AWS [32] and Fowler [50] describe. Not taken where DACI
  runs, because its Contributors have "a voice, but not a vote" [7] and a team acceptance would
  add a second decider. It stays the form for a group with no named decider (section 5).
- **The ADR holds the options even when DACI runs**, as Microsoft's and Fowler's records do
  [4], [50]. Not taken: the DACI play already has the Driver put the options on its page
  [7], and two copies drift apart. With no DACI page the ADR holds them (section 8).
- **Update the record in place.** The UK framework asks teams to "Regularly review and update the
  ADR to reflect any changes in the context or consequences of the decision" [15]. Joel Parker
  Henderson's collection reports: "In theory, immutability is ideal. In practice, mutability has
  worked better for our teams." His README also lists "Immutable: Don't alter existing information
  in an ADR" [89]. Not taken: the owners that define the life cycle keep the old text, so a
  reader sees what governed the work and for how long [50]. The dated note of section 8 gives a
  review a place without an edit.
- **Dates and a change log in place of statuses**, as the UK framework's template uses [15]. Not
  taken, because the change log edits the record in place.
- **A devil's advocate in place of a real objector.** Not taken: the authentic minority beat all
  three devil's-advocate forms in Nemeth et al.'s experiment [30]. Schweiger et al. compared
  devil's advocacy, dialectical inquiry and consensus: "This laboratory study compared the
  effectiveness of the dialectical inquiry, devil's advocacy, and consensus approaches to strategic
  decision making by groups" [82]. Its results and sample could not be read.
- **"Edicts fail" against "participation helps only a little".** Both are kept, with no averaging:
  Nutt compares how long decisions stayed in use by how they were carried out [1], and Wagner
  averages the link between participation and performance [19]. Do not skip consultation, and
  do not expect much from more of it.
- **A different person must review every decision.** Not taken: self-led reviews against an
  objective record were among the most effective [68]. Someone else comes in only for a
  failing course (section 9).
- **Review the process only, never the outcome.** Not taken: on complex tasks, outcome
  accountability helped [69].
- **"70% of the information" as a threshold.** Not taken: it is one person's rule of thumb with its
  own condition [12]; section 3 uses the condition instead.

## 14. Adoption in existing work

The answer is **new and touched code** ([refactoring.md](../refactoring/refactoring.md)
section 7): the rules apply to the decisions a team makes from now on, and an old decision moves to
them when a change touches it.

- A decision made before the practice keeps the record it has. Nobody rewrites old records to the
  new form.
- A change that touches an old technical decision may add an ADR for it when the facts are still
  available. Microsoft allows records made after the fact when the data is available [4], and
  Zimmermann notes that a record of a decision found in an existing system need not discuss the
  options in depth [76].
- An accepted record found to be stale is set to Deprecated (section 8) when someone finds it.
- The levels, the input round and the comment window start with the next decision. A decision log
  that exists stays; new entries link their ADRs
  ([roles-and-decisions.md](../project-management/roles-and-decisions.md) section 7).
- Agents already running: [agents.md](agents.md) section 12.

## 15. Review checklist

One question per section, for a proposal, a DACI page, an ADR, or a review.

| Section | Ask | Red flag |
|---|---|---|
| 2. Steps | Were the question and the decider named before the input started? | two people who each think they decide; a decision nobody framed |
| 3. Level | Was the level set by the three signs? | a level 3 process on an easy and clear choice inside one person's work; a hard-to-undo or unclear choice made at level 1 |
| 4. Input | Did each Contributor give facts and concerns before anyone stated a preference, and does the record say how the advice changed the decision? | the Approver's view at the top of the thread; advice listed with no answer |
| 5. Method | One named decider, or a written rule where there is none? | a vote in a team that has a decider; a veto with no reason |
| 6. Closing | An end date announced, and one of the three dispositions? | a thread with no end; a rejection with no reason; a postponement with no date |
| 7. Objections | Is each objection in the record with the decider's answer? | an objection that went unanswered; a safety objection that stayed with the decider |
| 8. ADR | Decider, options or the DACI link, confidence, revisit triggers, confirmation; opened at Proposed? | no options; opened as Accepted; an accepted decision text changed in the diff |
| 9. Review | Was the record read before the outcome was judged? | a decision called bad only because it turned out badly |
| 10. People | Does the record keep what the objection says, and nothing on the person? | remarks on someone's attitude; a raw transcript in the repository |

## 16. Sources

Checked 2026-10-30 unless a line ends with — checked <YYYY-MM-DD>.

- [1] Paul C. Nutt — Surprising but true: Half the decisions in organizations fail (Academy of Management Executive, 1999; research) — https://cebma.org/assets/Uploads/Nutt-1999-gecomprimeerd.pdf — checked 2026-10-29
- [2] Lu, Yuan and McLeod — Twenty-five years of hidden profiles in group decision making: a meta-analysis (Personality and Social Psychology Review, 2012; kind not confirmed) — https://doi.org/10.1177/1088868311417243
- [3] Jonathan Baron and John C. Hershey — Outcome bias in decision evaluation (Journal of Personality and Social Psychology, 1988; kind not confirmed) — https://pubmed.ncbi.nlm.nih.gov/3367280/ — checked 2026-10-29
- [4] Microsoft — Azure Well-Architected Framework: Maintain an architecture decision record (ADR) — https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record — checked 2026-10-29
- [5] GitLab — Handbook: Directly Responsible Individuals (DRI) — https://gitlab.com/gitlab-com/content-sites/handbook/-/raw/main/content/handbook/people-group/directly-responsible-individuals.md — checked 2026-10-29
- [6] SEBoK — Decision Management, v2.14 — https://www.sebokwiki.org/wiki/Decision_Management — checked 2026-10-29
- [7] Atlassian — DACI: a decision-making framework (Team Playbook) — https://www.atlassian.com/team-playbook/plays/daci
- [8] GitLab — Handbook: Making Decisions — https://gitlab.com/gitlab-com/content-sites/handbook/-/raw/main/content/handbook/leadership/making-decisions.md — checked 2026-10-29
- [9] Apache Software Foundation — Decision Making — https://community.apache.org/committers/decisionMaking.html — checked 2026-10-29
- [10] The Rust Project — The Rust RFC process (rust-lang/rfcs README) — https://github.com/rust-lang/rfcs/blob/master/README.md — checked 2026-10-29
- [11] Jeff Bezos — 2015 Letter to Shareholders (Amazon.com, Inc., SEC Exhibit 99.1, 2016; opinion) — https://www.sec.gov/Archives/edgar/data/1018724/000119312516530910/d168744dex991.htm — checked 2026-10-29
- [12] Jeff Bezos — 2016 Letter to Shareholders (About Amazon, 2017; opinion) — https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders — checked 2026-10-29
- [13] Malte Ubl — Design Docs at Google (Industrial Empathy, 2020; opinion) — https://www.industrialempathy.com/posts/design-docs-at-google/ — checked 2026-10-29
- [14] Python — PEP 1, PEP Purpose and Guidelines — https://peps.python.org/pep-0001/ — checked 2026-10-29
- [15] UK Government (DSIT and GDS) — Architectural Decision Record Framework — https://www.gov.uk/government/publications/architectural-decision-record-framework/architectural-decision-record-framework — checked 2026-10-29
- [16] Gergely Orosz — Engineering Planning with RFCs, Design Documents and ADRs (The Pragmatic Engineer, 2022; opinion) — https://newsletter.pragmaticengineer.com/p/rfcs-and-design-docs — checked 2026-10-29
- [17] Garold Stasser and William Titus — Pooling of Unshared Information in Group Decision Making: Biased Information Sampling During Discussion (Journal of Personality and Social Psychology, 1985; research) — https://www.uni-muenster.de/imperia/md/content/psyifp/aeechterhoff/vorlesungkommunikation/stasser_titus_unsharedinfogroupdisc_jpsp1985.pdf — checked 2026-10-29
- [18] Andrew Harmel-Law — Scaling the Practice of Architecture, Conversationally (martinfowler.com, 2021; opinion) — https://martinfowler.com/articles/scaling-architecture-conversationally.html — checked 2026-10-29
- [19] John A. Wagner III — Participation's Effects on Performance and Satisfaction: A Reconsideration of Research Evidence (Academy of Management Review, 1994; kind not confirmed) — https://doi.org/10.2307/258707
- [20] Mojzisch and Schulz-Hardt — Knowing others' preferences degrades the quality of group decisions (Journal of Personality and Social Psychology, 2010; kind not confirmed) — https://doi.org/10.1037/a0017627
- [21] Schulz-Hardt, Brodbeck, Mojzisch, Kerschreiter and Frey — Group decision making in hidden profile situations: dissent as a facilitator for decision quality (Journal of Personality and Social Psychology, 2006; kind not confirmed) — https://doi.org/10.1037/0022-3514.91.6.1080
- [22] Nadira Faulmüller, Rudolf Kerschreiter, Andreas Mojzisch and Stefan Schulz-Hardt — Beyond group-level explanations for the failure of groups to solve hidden profiles: The individual preference effect revisited (Group Processes & Intergroup Relations, 2010; research) — https://epub.ub.uni-muenchen.de/15558/1/beyond_group-level.pdf — checked 2026-10-29
- [23] Tobias Greitemeyer, Stefan Schulz-Hardt, Felix C. Brodbeck and Dieter Frey — Information sampling and group decision making: The effects of an advocacy decision procedure and task experience (Journal of Experimental Psychology: Applied, 2006; kind not confirmed) — https://doi.org/10.1037/1076-898x.12.1.31
- [24] Joaquin Navajas, Tamara Niella, Gerry Garbulsky, Bahador Bahrami and Mariano Sigman — Aggregated knowledge from a small number of debates outperforms the wisdom of large crowds (Nature Human Behaviour, 2018; research) — https://arxiv.org/abs/1703.00045v1
- [25] Federico Barrera-Lemarchand, Victoria Lescano-Charreau, Julieta Ruiz, Nuria Cáceres, Facundo Carrillo, Mariano Sigman and Joaquin Navajas — Collective problem decomposition improves the wisdom of deliberative crowds (Nature Communications, 2026; research) — https://www.nature.com/articles/s41467-026-76365-y — checked 2026-10-29
- [26] Leana — A partial test of Janis' groupthink model: effects of group cohesiveness and leader behavior on defective decision making (Journal of Management, 1985; kind not confirmed) — https://doi.org/10.1177/014920638501100102
- [27] Richardson Ahlfinger and Esser — Testing the groupthink model: Effects of promotional leadership and conformity predisposition (Social Behavior and Personality, 2001; kind not confirmed) — https://doi.org/10.2224/sbp.2001.29.1.31
- [28] Amazon Staff — An insider look at Amazon's culture and processes (About Amazon, no date; case) — https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes — checked 2026-10-29
- [29] Will Larson — Mailbag: Building alignment around a new strategy (Irrational Exuberance, 2021; opinion) — https://lethain.com/socializing-strategy/ — checked 2026-10-29
- [30] Charlan Nemeth, Keith Brown and John Rogers — Devil's advocate versus authentic dissent: stimulating quantity and quality (European Journal of Social Psychology, 2001; kind not confirmed) — https://doi.org/10.1002/ejsp.58
- [31] Phoebe E. Bailey, Tarren Leon, Natalie C. Ebner, Ahmed A. Moustafa and Gabrielle Weidemann — A meta-analysis of the weight of advice in decision-making (Current Psychology, 2022; research) — https://doi.org/10.1007/s12144-022-03573-2
- [32] AWS — Prescriptive Guidance: Architectural decision record process — https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html — checked 2026-10-29
- [33] Jeff Bezos — 2017 Letter to Shareholders (About Amazon, 2018; opinion) — https://www.aboutamazon.com/news/company-news/2017-letter-to-shareholders — checked 2026-10-29
- [34] Apache Software Foundation — Voting — https://www.apache.org/foundation/voting.html — checked 2026-10-29
- [35] Apache Software Foundation — Apache Glossary — https://www.apache.org/foundation/glossary.html — checked 2026-10-29
- [36] Python — PEP 13, Python Language Governance — https://peps.python.org/pep-0013/ — checked 2026-10-29
- [37] IETF — RFC 7282, On Consensus and Humming in the IETF, June 2014 — https://www.rfc-editor.org/rfc/rfc7282.html
- [38] Sociocracy 3.0 — Consent Decision-Making, v2026-01-26 — https://patterns.sociocracy30.org/consent-decision-making.html — checked 2026-10-29
- [39] Oxide Computer Company — RFD 1, Requests for Discussion — https://rfd.shared.oxide.computer/rfd/0001 — checked 2026-10-29
- [40] M.C. Noort, T.W. Reader and A. Gillespie — Safety voice and safety listening during aviation accidents: cockpit voice recordings reveal that speaking-up to power is not enough (Safety Science, 2021; research) — https://doi.org/10.1016/j.ssci.2021.105260
- [41] NASA — NPR 7120.5F, Chapter 3, with Change 4 — https://nodis3.gsfc.nasa.gov/displayDir.cfm?Internal_ID=N_PR_7120_005F_&page_name=Chapter3 — checked 2026-10-29
- [42] GitLab — Handbook: GitLab Values — https://gitlab.com/gitlab-com/content-sites/handbook/-/raw/main/content/handbook/values/_index.md — checked 2026-10-29
- [43] R.S. Dooley and G.E. Fryxell — Attaining decision quality and commitment from dissent: the moderating effects of loyalty and competence in strategic decision-making teams (Academy of Management Journal, 1999; kind not confirmed) — https://doi.org/10.5465/257010
- [44] M.A. Korsgaard, D.M. Schweiger and H.J. Sapienza — Building commitment, attachment, and trust in strategic decision-making teams: the role of procedural justice (Academy of Management Journal, 1995; kind not confirmed) — https://doi.org/10.5465/256728
- [45] AHRQ and U.S. Department of Defense — TeamSTEPPS Pocket Guide, AHRQ Pub. No. 23-0043, revised May 2023 — https://nachc.org/wp-content/uploads/2023/10/Teamstepps-pocket-guide.pdf — checked 2026-10-29
- [46] Pierre Pureur and Kurt Bittner — Has Your Architectural Decision Record Lost Its Purpose? (InfoQ, 2023; opinion) — https://www.infoq.com/articles/architectural-decision-record-purpose/ — checked 2026-10-29
- [47] Olaf Zimmermann — ADR = Any Decision Record? Architecture, Design and Beyond (ozimmer.ch, 2021; opinion) — https://ozimmer.ch/practices/2021/04/23/AnyDecisionRecords.html — checked 2026-10-29
- [48] Nabil Nazar — The Architecture Decision Record (ADR) framework (GOV.UK Technology in government blog, 2025; opinion) — https://technology.blog.gov.uk/2025/12/08/the-architecture-decision-record-adr-framework-making-better-technology-decisions-across-the-public-sector/ — checked 2026-10-29
- [49] Georg Buchgeher, Stefan Schöberl, Verena Geist, Bernhard Dorninger, Philipp Haindl and Rainer Weinreich — Using Architecture Decision Records in Open Source Projects - An MSR Study on GitHub (IEEE Access, 2023; kind not confirmed) — https://research.jku.at/en/publications/using-architecture-decision-records-in-open-source-projects-an-ms/ — checked 2026-10-29
- [50] Martin Fowler — Architecture Decision Record (martinfowler.com, 2026; opinion) — https://martinfowler.com/bliki/ArchitectureDecisionRecord.html — checked 2026-10-29
- [51] Enio Garcia de Santana Junior, Gustavo B. Figueiredo, Maycon Peixoto, Frederico Araujo, Cassio Prazeres, Ivan Machado, Paulo A. M. S. Neto and Eduardo Almeida — Architecture Decision Records: Adoption, Impact, and Developer Engagement in Open-Source Software (ICSA, 2026; kind not confirmed) — https://conf.researchr.org/details/icsa-2026/icsa-2026-papers/34/Architecture-Decision-Records-Adoption-Impact-and-Developer-Engagement-in-Open-Sou — checked 2026-10-29
- [52] Michael Nygard — Documenting Architecture Decisions (Cognitect blog, 2011; opinion) — https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions — checked 2026-10-29
- [53] Fernando Nogueira, Nabson Silva and Tayana Conte — One Size Fits All? An Empirical Comparison of ADR Templates regarding Comprehension, Usability, and Ease of Adoption (arXiv preprint, 2026; research) — https://arxiv.org/abs/2604.27333v1
- [54] Davide Falessi, Lionel Briand, Giovanni Cantone, Rafael Capilla and Philippe Kruchten — The value of design rationale information (ACM Transactions on Software Engineering and Methodology, 2013; kind not confirmed) — https://doi.org/10.1145/2491509.2491515
- [55] MADR — Markdown Architectural Decision Records template, 4.0.0 — https://raw.githubusercontent.com/adr/madr/4.0.0/template/adr-template.md
- [56] Shane Parrish — How a Decision Journal Changed the Way I make Decisions (Template Included) (Farnam Street, no date; opinion) — https://fs.blog/decision-journal/ — checked 2026-10-29
- [58] Olaf Zimmermann — A Definition of Done for Architectural Decision Making (ozimmer.ch, 2020; opinion) — https://ozimmer.ch/practices/2020/05/22/ADDefinitionOfDone.html — checked 2026-10-29
- [59] Davidson — Coding Agents Love Decision Records (O’Reilly Radar, 2026; opinion) — https://www.oreilly.com/radar/coding-agents-love-decision-records/ — secondary: read through the Internet Archive copy of 2026-10-19, https://web.archive.org/web/20261019053722/https://www.oreilly.com/radar/coding-agents-love-decision-records/ — checked 2026-10-29
- [60] Michael Keeling and Joe Runde — Share the Load: Distribute Design Authority with Architecture Decision Records (Agile Alliance, Agile 2018 experience report, 2018; case) — https://www.agilealliance.org/?p=8045735 — checked 2026-10-29
- [61] Bardha Ahmeti, Maja Linder, Raffaela Groner and Rebekka Wohlrab — Architecture Decision Records in Practice: An Action Research Study (ECSA, 2024; case) — https://rebekkaa.github.io/files/2024_ECSA.pdf — checked 2026-10-29
- [62] Scott I. Tannenbaum and Christopher P. Cerasoli — Do team and individual debriefs enhance performance? A meta-analysis (Human Factors, 2013; kind not confirmed) — https://pubmed.ncbi.nlm.nih.gov/23516804/ — checked 2026-10-29
- [63] Atlassian — Team Playbook: Decision-Making Retro — https://www.atlassian.com/team-playbook/plays/decision-making-retro — checked 2026-10-29
- [64] Dustin J. Sleesman, Donald E. Conlon, Gerry McNamara and Jonathan E. Miles — Cleaning Up the Big Muddy: A Meta-Analytic Review of the Determinants of Escalation of Commitment (Academy of Management Journal, 2012; research) — https://www.gwern.net/doc/psychology/cognitive-bias/sunk-cost/2012-sleesman.pdf — checked 2026-10-29
- [65] Dan Lovallo and Olivier Sibony — The case for behavioral strategy (McKinsey Quarterly, 2010; research, sponsored by McKinsey & Company) — https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/the-case-for-behavioral-strategy — checked 2026-10-29
- [66] Decision Education Foundation — Defining Decision Quality (Decision Education Foundation, no date; opinion) — https://www.decisioneducation.org/principles-of-decision-quality/defining-decision-quality — checked 2026-10-29
- [67] Sriraj Aiyer, Hoi Ching Kam, Ka Yuk Ng and co-authors — Outcomes Affect Evaluations of Decision Quality: Replication and Extensions of Baron and Hershey's (1988) "Outcome Bias Experiment 1" (International Review of Social Psychology, 2023; research) — https://pmc.ncbi.nlm.nih.gov/articles/PMC12372742/ — checked 2026-10-29
- [68] Nathanael L. Keiser and Winfred Arthur Jr. — A meta-analysis of the effectiveness of the after-action review (or debrief) and factors that influence its effectiveness (Journal of Applied Psychology, 2021; kind not confirmed) — https://doi.org/10.1037/apl0000821
- [69] Ira Sharon, Anat Drach-Zahavy and Einav Srulovici — The Effect of Outcome vs. Process Accountability-Focus on Performance: A Meta-Analysis (Frontiers in Psychology, 2022; research) — https://www.frontiersin.org/articles/10.3389/fpsyg.2022.795117/full — checked 2026-10-29
- [70] Philip E. Tetlock and Barbara A. Mellers — Structuring Accountability Systems in Organizations: Key Trade-Offs and Critical Unknowns (National Academies Press, 2011; research) — https://nap.nationalacademies.org/read/13062/chapter/16 — checked 2026-10-29
- [71] Elizabeth Keysor, Aliyah Wojtyna and Elizabeth S. Veinott — Premortem: Evaluating two structured analytic techniques for group brainstorming (SJDM poster, 2020; research) — https://sjdm.org/presentations/2020-Poster-Elizabeth-premortem-confidence-brainstorming.pdf — checked 2026-10-29
- [72] Information Commissioner's Office — Principle (c): Data minimisation — https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/ — checked 2026-10-29
- [73] Information Commissioner's Office — Access to information held in complaint files, version 3.1 — https://ico.org.uk/media2/migrated/2619040/s40-access-to-information-held-in-complaint-files-final-v-31.pdf — checked 2026-10-29
- [74] Information Commissioner's Office — Subject access request Q and As for employers — https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/subject-access-request-q-and-as-for-employers/ — checked 2026-10-29
- [75] Information Commissioner's Office — Specific data protection considerations for different ways or methods of monitoring workers — https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/specific-data-protection-considerations-for-different-ways-or-methods-of-monitoring-workers/ — checked 2026-10-29
- [76] Olaf Zimmermann — Ten Common Mistakes in Architectural Decision Records (ADRs) (ozimmer.ch, 2026; opinion) — https://ozimmer.ch/practices/2026/09/12/ADRMistakes.html — checked 2026-10-29
- [77] Nicolas Miccio, Antonela Tommasel and J. Andres Diaz-Pace — A Text Mining and Classification Approach for Analyzing Architecture Decision Records (arXiv preprint, 2026; research) — https://arxiv.org/abs/2609.07375v1
- [78] Costa da Silva and Gama — GADR: Gathering Architecture Decision Records from Meeting Transcriptions (arXiv preprint, 2026; research) — https://arxiv.org/abs/2608.17694v1
- [79] Christoph Nakazawa — Don't Disagree & Commit (Christoph's Notes, 2026; opinion) — https://cpojer.net/notes/dont-disagree-commit — checked 2026-10-29
- [80] Barbara Fasolo, Claire Heard and Irene Scopelliti — Mitigating Cognitive Bias to Improve Organizational Decisions: An Integrative Review, Framework, and Research Agenda (Journal of Management, 2024; kind not confirmed) — https://doi.org/10.1177/01492063241287188
- [81] ISO/IEC/IEEE — ISO/IEC/IEEE 42010:2022, Software, systems and enterprise — Architecture description, second edition (preview: front matter, contents and scope) — https://cdn.standards.iteh.ai/samples/74393/fc7b7f103d8446a4b87a3261e31370d3/ISO-IEC-IEEE-42010-2022.pdf
- [82] David M. Schweiger, William R. Sandberg and James W. Ragan — Group Approaches for Improving Strategic Decision Making: A Comparative Analysis of Dialectical Inquiry, Devil's Advocacy, and Consensus (Academy of Management Journal, 1986; kind not confirmed) — https://doi.org/10.2307/255859
- [83] Hastie and Kameda — The robust beauty of majority rules in group decisions (Psychological Review, 2005; kind not confirmed) — https://doi.org/10.1037/0033-295X.112.2.494
- [84] Mojtaba Shahin, Peng Liang and Zengyang Li — Do Architectural Design Decisions Improve the Understanding of Software Architecture? Two Controlled Experiments (ICPC, 2014; kind not confirmed) — https://doi.org/10.1145/2597008.2597139
- [85] Victor H. Vroom — Decision Making for Leaders: Lestan Cases (decisionmakingforleaders.com, 2023; opinion) — https://www.decisionmakingforleaders.com/dmfl/cases-english.pdf — checked 2026-10-29
- [86] Juan de la Poza Pérez — Evaluación crítica del modelo de liderazgo participativo de Vroom-Yetton (1973) y Vroom-Jago (1988) (Revista de Psicología del Trabajo y de las Organizaciones, 1998; opinion) — https://journals.copmadrid.org/jwop/archivos/47544.pdf — checked 2026-10-29
- [87] PMI — A Guide to the Project Management Body of Knowledge (PMBOK Guide), Sixth Edition, errata, fourth printing — https://www.pmi.org/-/media/pmi/documents/public/pdf/pmbok-standards/pmbok-guide-6th-edition-errata-4th-printing.pdf — checked 2026-10-29
- [88] PMI — PMBOK Guide, Seventh Edition, public FAQs — https://www.pmi.org/-/media/pmi/documents/public/pdf/pmbok-standards/pmbok-guide-public-faqs-1-july-2021.pdf — checked 2026-10-29
- [89] Joel Parker Henderson — architecture-decision-record, README (GitHub, no date; opinion) — https://github.com/joelparkerhenderson/architecture-decision-record — checked 2026-10-29
