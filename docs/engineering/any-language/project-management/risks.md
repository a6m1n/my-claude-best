# Risks

A risk is something that might happen and would change whether the project reaches its goal. This
file says how to record risks, rank them, answer them, plan for the moment one happens, and review
them. Read it in the planning phase, when you create the register, and again at each weekly review
and phase end. The
[project plan](project-plan.md) links the register; a threat that has happened becomes a work item
([tickets.md](tickets.md)).

**Navigation**

- [1. Terms](#1-terms)
- [2. The register](#2-the-register)
- [3. The score ranks attention](#3-the-score-ranks-attention)
- [4. One owner per risk](#4-one-owner-per-risk)
- [5. The five threat responses](#5-the-five-threat-responses)
- [6. Contingency plans and reserves](#6-contingency-plans-and-reserves)
- [7. Review](#7-review)
- [8. Find risks early](#8-find-risks-early)
- [9. Sources](#9-sources)

## 1. Terms

PMI Lexicon (2026):

- Risk: "An uncertain event or condition that, if it occurs, has a positive or negative effect on
  one or more portfolio, program, or project objectives."
- Threat: "A risk that would have a negative effect on one or more portfolio, program, or project
  objectives."
- Issue: "A current condition or situation that may have an impact on one or more objectives."

A risk has not happened; an issue has. This file covers threats. A positive risk (an opportunity)
has its own responses in PMI's Lexicon, and this practice does not use them.

## 2. The register

Create the register in planning, so the plan can include the responses before work starts, and keep every risk in it. PMI defines it as "A repository in
which outputs of risk management processes are recorded." (PMI Lexicon, 2026) The PMP exam outline
lists "Maintain a risk register"; Scrum has no register.

The columns come from Atlassian's Confluence risk register template, with PMI's terms:

| Column | What it holds |
|---|---|
| ID | A short key, such as R-1 |
| Risk | One sentence: cause, then event, then effect |
| Probability | 1 to 5 |
| Impact | 1 to 5 |
| Score | Probability times impact |
| Response | One of the five in section 5 |
| Actions | What is done now, each with a date |
| Owner | One person (section 4) |
| Trigger | The sign that the risk is about to happen |
| Status | Open, closed (did not happen), or happened (now an issue) |

Writing the risk as cause, event, effect keeps the row specific: a name like "provider risk" tells
nobody what to watch. A filled register is in [project-example.md](project-example.md) section 5.

Where it lives: keep the register as a Confluence page from Atlassian's risk register template,
linked to each deliverable epic ([charter.md](charter.md) section 5). Use a custom Risk work type
only when the team must report risks by JQL; Jira has no Risk work type by default. The ROAM risk board Atlassian describes belongs to SAFe planning, not to the default
setup. Pick one place and say which in the plan.

## 3. The score ranks attention

Use the score to decide which risks to discuss first, and decide each response in the discussion.
Risk matrices can rank risks wrongly: Cox (2008) showed that for risks whose frequency and
severity are negatively correlated they can be "worse than useless", leading to worse-than-random
decisions. A 15 is not always a bigger problem than a 12.

Check: at the review, ask whether any risk was left out of the discussion only because its score
was low.

## 4. One owner per risk

Give each risk one owner. PMI defines the risk owner as "The person responsible for monitoring the
risk and for selecting and implementing an appropriate risk response strategy." (PMI Lexicon,
2026) PMBOK 7 says responses should be "Owned by a responsible person." A risk with two owners
or none is a risk nobody watches.

## 5. The five threat responses

If you were told there are five ways to mitigate a risk, these are the five; mitigation is one of
them.

Choose one response per threat and write it in the register. The choice makes the owner's job
clear: they know whether to remove the threat, shrink it, pass it on or only watch it. PMI Lexicon
(2026):

- Escalation: "A risk response strategy that involves transferring the ownership of the risk to a
  relevant party in the organization because the risk is outside of scope or the team does not
  have sufficient authority to address it."
- Avoidance: "A risk response strategy that involves eliminating the threat or protecting the
  portfolio, program, or project from its impact."
- Transference: "A risk response strategy that involves shifting the impact of a threat to a third
  party, together with ownership of the response."
- Mitigation: "A risk response strategy that involves decreasing the probability of occurrence or
  impact of a threat."
- Acceptance: "A risk response strategy that involves acknowledging the risk and taking no action
  unless it occurs. Acceptance of the risk's implication(s) usually means using schedule and/or
  cost reserves and accepting scope and/or quality reduction(s)."

Mitigation is one of the five, not a general word for any action. PRINCE2 7 names six responses to
a threat: avoid, reduce, transfer, share, accept, and "prepare contingent plans" (PeopleCert, PRINCE2
7 Quick Reference Guide, 2023). Pages that list "fallback" in place of the last one describe the
2017 edition. The PMP exam outline names no threat strategies.

## 6. Contingency plans and reserves

For each open threat with an impact of 4 or 5, write a contingency plan when you choose its
response: the first actions the owner takes when the trigger fires, who takes them, and what they
cost in time or money. Put it in the Actions column, or link a page from there. PMI defines a
contingency plan as "A document that describes actions to take if predetermined trigger conditions
occur." (PMI Lexicon, 2026) The register's Trigger column is that condition. The reason: a plan made
before the trigger fires is made calmly, and one made after it is made during the damage. PRINCE2 7
counts "prepare contingent plans" as a response of its own (section 5).

Keep time and money for risks in two reserves, and keep them apart (PMI Lexicon, 2026):

| Reserve | PMI's definition | Where it sits | Who releases it |
|---|---|---|---|
| Contingency reserve | "Time or money allocated in the schedule or cost baseline for known risks with active response strategies." | Inside the baseline | The project manager, inside the tolerance of [project-plan.md](project-plan.md) section 4 (this practice's own) |
| Management reserve | "Time or money that management sets aside in addition to the schedule or cost baseline and releases for unforeseen work that is within the scope..." | Outside the baseline | The sponsor |

Name in the register the risk each part of the contingency reserve is for, and keep it out of the
estimates of single work items (this practice's own). The reason: a reserve spread inside every
estimate cannot be seen, so nobody can tell when it is used up.

When a threat happens and no plan exists, or the plan does not work, the first answer is a
workaround: "An immediate and temporary response to a realized risk for which a prior response has
not been planned or was not effective." (PMI Lexicon, 2026) Record it in the work item that the
happened risk becomes (section 7), and add the risk behind it to the register.

Check: at the review, ask whether each open threat with an impact of 4 or 5 has a trigger and a
contingency plan.

## 7. Review

Review the top risks every week, and the whole register at each phase end. Atlassian's template
asks for a weekly "top 5" list and reviews at milestones, so the register is read while it can
still change a decision.

When a threat happens, change its status and open a work item: it is now an issue in PMI's sense (section 1). The PMP exam
outline lists "Recognize when a risk becomes an issue" as its own task. The response is then done
by the work items in [tickets.md](tickets.md), and an incident follows [sla.md](sla.md).

A response can cause a new risk (PMI: a secondary risk, "A risk that arises as a direct result of
implementing a risk response") and leave some risk behind (a residual risk, "The risk that remains
after risk responses have been implemented"). Add both to the register as new rows, so each new or remaining risk has an owner too.

## 8. Find risks early

In planning, run a pre-mortem with the team: imagine the project has failed, and write down why.
This finds risks while the plan can still change. Atlassian's Team Playbook describes it as thinking
about "what could happen in a project - good or bad - and make a plan before it starts." Each
action that comes out gets an owner and a deadline, or it is not an action.

## 9. Sources

- [PMI Lexicon of Project Management Terms, v5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf), January 2026: risk, threat, issue, risk register, risk owner, the five responses, secondary and residual risk, contingency plan, contingency reserve, management reserve, workaround.
- [PMP examination content outline](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/new-pmp-examination-content-outline-2026.pdf), July 2026 exam: register, risk becomes issue, no threat strategies.
- [PMBOK 7, the 12 project management principles (PDF)](https://www.pmi.org/-/media/pmi/documents/public/pdf/pmbok-standards/12-project-management-principles.pdf?rev=03749f118ff84aca97a64af1d49bb1ac), 2021: risk principle.
- [Atlassian, Confluence risk register template](https://www.atlassian.com/software/confluence/templates/risk-register), undated: columns, weekly top 5.
- [Atlassian Team Playbook, pre-mortem](https://www.atlassian.com/team-playbook/plays/pre-mortem), undated.
- [Cox, What's wrong with risk matrices?, Risk Analysis, 2008](https://onlinelibrary.wiley.com/doi/10.1111/j.1539-6924.2008.01030.x): read from the abstract.
- PeopleCert, [PRINCE2 7 Foundation Quick Reference Guide](https://www.nilc.co.uk/wp-content/uploads/2023/10/PRINCE2-Quick-Reference-Guide.pdf), 2023, an official training PDF hosted by a training organisation: the six threat responses.