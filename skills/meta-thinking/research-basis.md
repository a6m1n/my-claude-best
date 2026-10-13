# meta-thinking — research basis

The evidence behind `SKILL.md`: the full report of the `web-research` T3 run of 2026-10-11.
Read it when a rule in `SKILL.md` is challenged, when a critic asks "why is it like this", or
when the skill is refreshed. Each rule in `SKILL.md` names the ids it rests on (`F<n>`, `C<n>`).
The run was made in another setup: "the user" below is the person who asked for the run, and
the skills it names (`grill-me`, `web-research`, `debate-loop`) belong to that setup and are not
shipped here.

Researched 2026-10-11 · distrust after 2027-04-11

- Question: what does current research and practice say about a pre-task "meta-thinking" step
  for an LLM coding agent on LARGE tasks — an independent expert agent (fresh context) that,
  before any work, assesses all known information about the task, decides what to research
  (web) and what to ask the user, compares alternative approaches as 1-3 step-by-step routes
  with the reason for each step (not a full implementation plan), checks which available
  skills/tools fit and proposes them, then hands off?
- Tier T3 · scout + 3 lens rounds (10 lenses) + one expert-bought round (2 lenses) + two
  expert passes.
- Excluded from the run: Claude/Anthropic documentation (docs.claude.com, docs.anthropic.com,
  code.claude.com, support.claude.com, platform.claude.com), and guides or opinions from
  vendors of work-management tools (Shape Up / Basecamp items were read and dropped).
- Most sources are 2025–2026 arXiv preprints, many single-run and not replicated. Numbers came
  through a fetch tool that summarizes pages; re-check a table before quoting a number outside
  this file.

## Bottom line

Planning before work helps where the executor would otherwise fail and costs a little or hurts
slightly on tasks it would solve anyway (F1: −0.4 to −2.6 pp; F43, non-coding) (corrected
2026-10-11 after a debate-loop re-read), so the step needs an entry gate, which the PM standards and practitioners also call
for (F54, F76, F77). The value the step aims at is the decisions and missing requirements it
puts in front of the user (F20, F21; F6 found the questions surfaced requirements, but the
final output did not differ) (corrected 2026-10-11 after a debate-loop re-read), not the
model's pick among routes: an LLM choosing between designs without tests adds a few points,
about 2 in the coding ablation (F93, one run, confounded), +2.8 to +5.2 on SWE-bench Verified
and +3.9 to +10.2 on Terminal-Bench v2.0 for selection alone in a tournament study (F99), more
with a trained verifier (F103) (corrected 2026-10-11 after a debate-loop re-read). Hand-offs drop constraints unless they are written as explicit
imperative lines, and agents follow a given plan only in part (F36, F37, F104).
Confidence in the basis: moderate — many single-run 2026 preprints, no study of this exact
step, and the coding evidence is mostly on small tasks.
What would change this: a controlled study of a gated pre-task step on feature-size coding
tasks (W1, W2); a study of developers choosing among AI-written designs.
111 findings · 12 contradictions (1 unadjudicated) · expert: use 85 · skip 54 · 2 not established

## Findings

Every finding with its fields: `id claim | URL | date | source class | corroboration`.

- **F1** Persistent planning scaffold on SWE-bench Verified: +11.6 pp for a weak 30B model; −0.4…−2.6 pp for strong models but ~30% cheaper; one run per task | https://arxiv.org/html/2609.20804 | 2026-09 | measured | n=1
- **F2** TeamBench: adding the Planner (155-task reference ablation) +2.4 pts mean partial score; the quintile figures (+15.7 pt where Solo success is lowest, −6.8…−10.1 pt in upper quintiles) compare Full Team vs Solo and include the Verifier's effect, so they cannot be attributed to the Planner alone (corrected 2026-10-11 after a debate-loop re-read) | https://arxiv.org/html/2605.07073 | 2026-05 | measured | n=1 (direction "helps where executor would fail" also in F1, F3: n=3)
- **F3** AgentForge: removing the Planner 42→19/100 (GPT-4o, SWE-bench Lite first 100, one run, structure removed too) | https://arxiv.org/html/2604.13120 | 2026-04 | measured | n=1
- **F4** Planning frequency: intermediate best, always-plan worse (Crafter/POGS, non-coding) | https://arxiv.org/html/2509.03581v1 | 2025-09 | measured | n=1
- **F5** Delaying first edit correlates with success (rho +0.68); heavy early patching with failure (−0.78); observational, 9,374 trajectories | https://arxiv.org/html/2604.02547v1 | 2026-04 | measured | n=1
- **F6** Plan Mode user study (spreadsheet agent, N=24): fewer tokens, more turns/time, similar outputs, no notable difference in the final workbooks (corrected 2026-10-11 after a debate-loop re-read); users answered 88/99 clarifying questions and many requirements came from them; only 10/24 changed the first plan; preference stronger on creation/longer tasks | https://arxiv.org/html/2607.23670 | 2026-07 | measured | n=1
- **F7** Overthinking / analysis paralysis predicts lower SWE-bench resolve; steering away overthinking steps +5.8 pp | https://arxiv.org/html/2502.08235 ; https://arxiv.org/html/2605.05980 | 2025-02 / 2026-05 | measured | n=2
- **F8** Deciding upfront which problems to attempt and with what budget: negative efficiency for most configurations | https://arxiv.org/html/2605.13414v1 | 2026-05 | measured | n=1
- **F9** Frontier LLMs now match/beat the LAMA planner on satisficing PDDL (245/360 vs 204) — "LLMs can't plan" (LLM-Modulo 2402.01817, origin) is weaker today | https://arxiv.org/html/2511.09378 | 2026-05 v2 | measured | n=1
- **F10** Self-critique of a plan works when preconditions are checkable (Blocksworld 49.8→89.3%) and fails on open-ended reasoning (Huang 2310.01798, origin) | https://arxiv.org/html/2512.24103 | 2025-12 | measured | n=1
- **F11** LLM ideation fixates (fewer categories than humans); chain-of-thought / persona raises diversity | https://arxiv.org/html/2602.20408 | 2026-02 | measured | n=1
- **F12** One planning call that proposes 5 directions gives the best diversity per token (creative tasks) | https://arxiv.org/html/2605.30150 | 2026-05 | measured | n=1
- **F13** Output homogeneity: 79% of queries exceed 0.8 average pairwise similarity across 50 samples | https://arxiv.org/html/2510.22954v1 | 2025-10 | measured | n=1
- **F14** Critique: 20–32% of genuinely different pairs exceed 0.8, so the threshold does not establish homogeneity | https://arxiv.org/html/2609.33936 | 2026 | measured | n=1
- **F15** Ambig-SWE: interaction recovers ~54–89% of full-spec performance; most models detect underspecification poorly (best 0.89 with a strong prompt, Qwen3-Coder 0.50) | https://arxiv.org/html/2502.13069v3 | 2026-02 v3 | measured | n=1
- **F16** Ask or Assume: separate intent agent 69.4% vs same-agent per-turn check 61.2% (p<0.001) vs always-ask 70.4% (n.s.); $3.50 vs $2.03 (fully specified, no questions: $1.63) per task (corrected 2026-10-11 after a debate-loop re-read) | https://arxiv.org/html/2603.26233v1 | 2026-03 | measured | n=1 in coding (MAC https://arxiv.org/html/2512.13154v1, dialogue, +6, weakly verified)
- **F17** CLARITI: answerable targeted questions matter; CLARITI averages 3.0 questions vs 5.1 for baselines; volume beyond that plateaus (corrected 2026-10-11 after a debate-loop re-read); unanswerable questions degrade to near no-clarification | https://arxiv.org/html/2604.14624v1 | 2026-04 | measured | n=1
- **F18** QuestBench: models find the one missing variable only ~40–50% of the time on logic/planning problems | https://arxiv.org/abs/2503.22674 | 2025-10 v2 | measured | n=1
- **F19** RegretBench: both over-asking and under-asking occur; best model ~1.4 turns | https://arxiv.org/html/2607.21143 | 2026-07 | measured | n=1
- **F20** SWE-Bench Pro: GPT-5 25.9% with requirements + interface vs 8.4% with the problem statement alone | https://arxiv.org/html/2509.16941v2 | 2025-11 | measured | n=1
- **F21** SWE-RPG: 46.7% of runs fail mainly in clarification or planning; plan coverage falls from location 79.7% → approach 64.5% → constraints/validation 41.6% (LLM judge) | https://arxiv.org/html/2608.09072 | 2026-08 | measured | n=1
- **F22** SWE-EVO (release-size tasks, ~21 files): best 25%; >60% of GPT-5 failures are instruction-following (misreading release notes) (LLM-judge labels) | https://arxiv.org/html/2512.18470 | 2026-05 v6 | measured | n=1
- **F23** RACE-bench: intent comprehension is strong (9.37/10); reasoning recall falls files → tasks → steps | https://arxiv.org/html/2603.26337v1 | 2026-03 | measured | n=1
- **F24** Coherence Collapse: capable models reach the correct functions in 60–69% of failures and then produce bad patches (thrashing, overwriting correct code) — small tasks | https://arxiv.org/html/2603.24631 | 2026-05 v2 | measured | n=1
- **F25** HORIZON (non-SWE): early subplanning errors are path-dependent and costly to roll back | https://arxiv.org/html/2604.11978v1 | 2026-04 | measured | n=1
- **F26** Self-preference origin: models recognize and favor their own text | https://arxiv.org/abs/2404.13076 | 2024-04 | measured | origin
- **F27** Most measured self-preference is evaluator quality (89.6%); ~44% of experiments show none after correction | https://arxiv.org/html/2601.22548 | 2026-06 v4 | measured | n=1
- **F28** 17/20 models show self-preference; Claude Sonnet 4.5 favors other models' outputs | https://arxiv.org/html/2604.22891v2 | 2026-04 | measured | n=1
- **F29** Same-family judge preference is small but reliable (GFPS 0.067); a family-balanced panel flips 18.5% of outcomes | https://arxiv.org/html/2609.17857 | 2026-09 | measured | n=1
- **F30** Judge–model similarity correlates with scores (r=0.84); errors grow more correlated with capability | https://arxiv.org/html/2502.04313 | 2025-06 | measured | n=1
- **F31** Agents are overconfident about their own success (Claude 61% predicted vs 27% actual); pre-execution AUROC 0.53–0.64 | https://arxiv.org/html/2602.06948 ; https://arxiv.org/html/2512.24661 | 2026-02 | measured | n=2
- **F32** A cross-agent statistical model predicts task difficulty from the problem statement alone at AUC 0.787 (SWE-bench Verified) | https://arxiv.org/html/2604.00594v1 | 2026-04 | measured | n=1
- **F33** Pre-task time and token self-estimates are off by multiples (3.6–6.1× time; token Pearson ≤0.39) | https://arxiv.org/html/2604.00010 ; https://arxiv.org/html/2604.22750v3 | 2026-04 | measured | n=2
- **F34** Sycophancy: assistants follow user pushback (origin Sharma 2310.13548); reasoning models drop 26–29 pts after "No, that's incorrect" | https://arxiv.org/html/2506.09677v1 | 2025-06 | measured | n=2
- **F35** Cave-Bench: false accusations cause over-correction in agents; an evidence-required rule cut false-confession severity ~57%, a live-signal gate cut harm ~74% | https://arxiv.org/html/2609.32616v1 | 2026-09 | measured | n=1
- **F36** TeamBench: the Executor keeps ~0.21 of the Planner's spec-critical tokens; verifiers approved 49.4% of grader-rejected work | https://arxiv.org/html/2605.07073 | 2026-05 | measured | n=1 magnitude (direction n=3 with F37, F38)
- **F37** Hand-offs drop constraints while facts survive; an explicit imperative constraint leaked 2/48 vs a vague hedge 35/48 vs none 44/48 (synthetic, privacy setting) | https://arxiv.org/html/2608.29028 | 2026-08 | measured | n=1
- **F38** OrchBench: information transfer coverage correlates with quality (r=0.614), agent count does not (r≈0) | https://arxiv.org/html/2607.25656v1 | 2026-07 | measured (simulation) | n=1
- **F39** MAST: fail-to-ask-for-clarification 6.8%, disobey task spec 11.8%, information withholding 0.85%; multi-agent gains often minimal | https://arxiv.org/html/2503.13657v3 | 2025-10 v3 | measured | n=1
- **F40** Parallel sub-agents: missing-requirements briefs 2.9% of failure instances; Claude Code SWE-bench 59% concurrent vs 83% sequential | https://arxiv.org/html/2610.10263 | 2026-10 | measured | n=1
- **F41** PEAR: a weak planner degrades results more than a weak executor; plan channel injection success 82–89% | https://arxiv.org/html/2510.07505 | 2026-01 v4 | measured | n=1
- **F42** Enforced think steps: constraints recorded in private reasoning are left out of what the agent tells the user | https://arxiv.org/html/2602.07796 | 2026-08 v2 | measured | n=1
- **F43** A mid-task critic hurts tasks the agent would solve anyway; it helps only when the baseline failure rate is high | https://arxiv.org/html/2602.03338 | 2026-02 | measured (non-coding) | n=1
- **F44** The first feedback round corrects 46% of bad directions; later rounds 12.8% and 7.1% | https://arxiv.org/html/2609.29697 | 2026-08 | measured (security) | n=1
- **F45** Planner–actor state mismatch in 85% of failed trajectories (non-SWE) | https://arxiv.org/html/2609.38891 | 2026-09 | measured | n=1
- **F46** Cognition 2025: share full context; a subagent lacks the main agent's context | https://cognition.com/blog/dont-build-multi-agents | 2025-06 | practitioner | n=1
- **F47** Cognition 2026: a clean-context reviewer works best with no shared context; writes stay single-threaded | https://cognition.com/blog/multi-agents-working | 2026-04 | practitioner | n=1
- **F48** LLM-written context files: −0.5…−2 pp, +20–23% cost; developer-written +4 pp | https://arxiv.org/html/2602.11988v1 | 2026-02 | measured | n=1
- **F49** AGENTS.md cuts tokens ~16.6% and runtime ~28.6% at comparable success | https://arxiv.org/abs/2601.20404 | 2026-01 | measured | n=1
- **F50** SkillsBench: self-generated skills no benefit; curated +16.2 pp (SWE only +4.5); 1 skill +17.8, 2–3 skills +18.6 vs 4+ skills +5.9 (corrected 2026-10-11 after a debate-loop re-read); comprehensive −2.9 | https://arxiv.org/html/2602.12670v1 | 2026-02 | measured | n=2 for "self-written does not help" (with F51)
- **F51** Claude loaded available curated skills in 49% of runs (31% with distractors); retrieved skills +3.0; weaker models fell below baseline | https://arxiv.org/html/2604.04323v1 | 2026-04 | measured | n=1
- **F52** A bigger skill library worsens selection (drop 0.08 at 52 skills → 0.21 at 202), mostly "skill shadowing" | https://arxiv.org/html/2605.24050v1 | 2026-05 | measured | n=1
- **F53** SkillRet: skill retrieval left pass rate unchanged (65.5 vs 65.8) and cut cost ~10% | https://arxiv.org/html/2605.05726 | 2026-09 v3 | measured | n=1
- **F54** Skip or shrink the step on small/clear tasks | Böckeler https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html (2025-10); Osmani https://addyosmani.com/blog/good-spec/ (2026-01); Vincent https://blog.fsck.com/2026/10/09/what-a-year/ (2026-10); Google design docs https://www.industrialempathy.com/posts/design-docs-at-google/ (2020) | practitioner | n=4
- **F55** Long monolithic specs/plans degrade results and cost review time; "A plan longer than the code it describes has written the code instead." | Osmani; Böckeler; HN https://news.ycombinator.com/item?id=49834564 ; superpowers writing-plans https://raw.githubusercontent.com/obra/superpowers/main/skills/writing-plans/SKILL.md | 2025-10…2026-10 | practitioner | n=4
- **F56** Process steps written as long prose get skipped by agents | Vincent https://blog.fsck.com/agent-blog/2026/03/10/superpowers-v5-0-1/ ; Horthy (secondary) https://alexlavaee.me/blog/from-rpi-to-qrspi/ ; Böckeler | 2025-10…2026-03 | practitioner | n=3
- **F57** Early wrong assumptions are the main danger; persuasive plan prose hides them ("plan-reading illusion") | Horthy (secondary, alexlavaee + podwise = one origin); Huntley https://ghuntley.com/ralph/ ; Reed https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/ (2025-02, out of window) | practitioner | n=3
- **F58** Output converges on short markdown files a human reads and edits | Reed; Ronacher https://lucumr.pocoo.org/2025/12/17/what-is-plan-mode/ ; Osmani; HumanLayer ace-fca.md (no URL kept — unresolved); Böckeler (Kiro, spec-kit) | 2025…2026 | practitioner | n=5
- **F59** One question per message; "Options steer. Ask them to describe it first." | Reed; superpowers brainstorming https://raw.githubusercontent.com/obra/superpowers/main/skills/brainstorming/SKILL.md | practitioner | n=2
- **F60** superpowers brainstorming: entry gate "if the request is complete, do it"; Size the Work (quick / small / project); alternatives generated privately, not shown as a menu; Play It Back; approval gate; hand-off to one named skill | https://raw.githubusercontent.com/obra/superpowers/main/skills/brainstorming/SKILL.md | read 2026-10-11 | canonical (artifact) | n=1
- **F61** HumanLayer rpi: explicit invocation only; "Use the shortest path that gives the user useful review points"; design discussion = one decision at a time with options, trade-offs, recommendation; research questions 2–7, blind to the desired change | https://raw.githubusercontent.com/humanlayer/skills/main/plugins/rpi/skills/rpi/SKILL.md | 2026-10 | canonical (artifact) | n=1
- **F62** A fresh subagent or a different model reviewing the spec/plan improves it (no measurement) | Vincent https://blog.fsck.com/2026/03/09/superpowers-5/ ; HN waldopat https://news.ycombinator.com/item?id=46864948 | 2026 | practitioner | n=2
- **F63** The value of an explicit plan step shrinks as models get stronger | Cherny https://x.com/bcherny/status/2017742745365057733 → https://x.com/bcherny/status/2058519809214607704 ; HN 49834564 (plans shrink to gap-closers) | 2026 | practitioner | n=2
- **F64** The boundary is risk profile and verifiability, not complexity ("cannot verify the change in 30 s → plan first") | dev.to jsmanifest (no URL kept — unresolved) | 2026-10 | anecdote | n=1
- **F65** ~80% of agent-generated questions are useless, but the other 20% find missed points | HN Imanari https://news.ycombinator.com/item?id=46864948 | 2026 | anecdote | n=1
- **F66** aider architect/editor split: same model as architect + editor 80.5% vs 77.4% alone | https://aider.chat/2024/09/26/architect.html | 2024-09 | measured (out of window, old models) | n=1
- **F67** No practitioner artifact read has a "which of my skills fit" check; superpowers uses a mandate ("1% chance … MUST invoke") instead | superpowers using-superpowers SKILL.md; rpi SKILL.md (no URL kept — unresolved) | 2026-10 | canonical (absence in artifacts) | n=2
- **F68** Schoenfeld: Pólya heuristics alone did not transfer; training "control" (monitoring during work: What are you doing? Why? How does it help?) cut hasty-commit attempts from ~60% to <20% with more success | https://jwilson.coe.uga.edu/emat7050/Schoenfeld_MathThinking.pdf | 1992 | measured (pre/post) | origin
- **F69** Nutt: multiple options developed in <20% of decisions; success 56% → 70% when they were; "whether or not" decisions failed 52% vs 32% | https://cebma.org/assets/Uploads/Nutt-1999-gecomprimeerd.pdf (+ Heath secondary of Nutt 1993) | 1999 | measured (observational) | origin, n=1
- **F70** Experts rarely compare options (Klein fireground <12%); intuition is valid only in predictable environments with feedback (Kahneman & Klein 2009) | https://pubmed.ncbi.nlm.nih.gov/19739881/ | 2009 | canonical (peer-reviewed) | origin
- **F71** Decision framing: what we decide / do not decide / take as given / goals (Spetzler, Decision Quality) | https://decisioneducation.org/decision-focus/helpful-frame | undated | practitioner | n=1
- **F72** Choose what to research by value of information; "measurement inversion" (Hubbard) | https://pubsonline.informs.org/do/10.1287/LYTX.2014.03.01/full/ | 2014 | practitioner | n=1
- **F73** Reference class forecasting: compare with similar past projects; advantage largest for non-routine work; beat Monte Carlo and EVM on real data | https://arxiv.org/pdf/1302.3642 ; https://www.pmi.org/learning/library/practical-application-empirical-evaluation-rcf-10277 | 2006 / 2016 | measured | n=2
- **F74** Premortem: evidence thin; one quality-measured study (Gallop & Bischoff 2016) positive, read only secondhand | https://corporate.jcx.au/premortem ; https://hbr.org/2007/09/performing-a-project-premortem | 2007 / 2016 | practitioner (secondary) | n=1
- **F75** Cynefin has conceptual support only, no validation study | https://pmc.ncbi.nlm.nih.gov/articles/PMC8100038/ | 2021 | practitioner | n=1
- **F76** PMI tailoring (select development approach; tailor for the project by size and criticality) and PRINCE2 7 (tailor to needs, size, complexity, context) | https://www.pmi.org/-/media/pmi/documents/public/pdf/pmbok-standards/pmbok-tailoring-explainer-20-oct-2020.pdf ; https://www.peoplecert.org/browse-certifications/project-programme-and-portfolio-management/PRINCE2-2/PRINCE2-7-foundation-3579 | 2020 / current | canonical | n=2
- **F77** Google design docs: "Alternatives considered" and non-goals; no value in a doc when the problem is not ambiguous | https://www.industrialempathy.com/posts/design-docs-at-google/ | 2020 | practitioner | n=1
- **F78** Military courses of action must be distinguishable and complete; one COA under time pressure | https://www.army.mil/article/209253/ | 2018 | canonical-adjacent | n=1
- **F79** Backbrief: the executor restates intent and first steps before execution | https://www.globalsecurity.org/military/library/report/call/call_91-1_sec3.htm | 1991 | practitioner (doctrine) | n=1
- **F80** Bezos: reversible "two-way door" decisions get a light process; no one-size-fits-all process | https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders | 2017 | practitioner | n=1
- **F81** 85% of 106 executives say their organizations are bad at problem diagnosis (Wedell-Wedellsborg) | https://hbr.org/2017/01/are-you-solving-the-right-problems | 2017 | practitioner (survey) | n=1
- **F82** Automation bias: wrong advice raised wrong decisions (RR 1.26); prominent advice followed more | https://pmc.ncbi.nlm.nih.gov/articles/PMC3240751 | 2012 | measured (systematic review) | n=1
- **F83** Defaults read as endorsement (d=0.68) | https://ideas.repec.org/a/cup/bpubpo/v3y2019i02p159-186_00.html | 2019 | measured (meta-analysis) | n=1
- **F84** Choice overload: mean effect ~0 (Scheibehenne 2010) but significant under complexity and preference uncertainty (Chernev 2015) | https://ideas.repec.org/a/oup/jconrs/v37y2010i3p409-425.html | 2010 / 2015 | measured | n=2
- **F85** Evidence for/against each option with the recommendation hidden cut overreliance 73.9% → 53.3% (N=302 lay); Study 2 (N=14 clinically trained staff and researchers, 'not experts' per the authors): no significant accuracy difference (Brier 0.36 vs 0.40, p=0.35), ~29% more time | https://arxiv.org/html/2402.01292 | 2024-02 | measured | n=1
- **F86** Evaluative AI without a recommendation was not better in decision quality (N=375) | https://arxiv.org/html/2411.08583v1 | 2024-11 | measured | n=1
- **F87** Cognitive forcing reduces overreliance, but users rate it worst | https://arxiv.org/abs/2102.09692 | 2021 | measured | n=1
- **F88** First-person hedges ("I'm not sure, but…") reduce overreliance on wrong LLM answers (N=404) | https://arxiv.org/abs/2405.00623 | 2024-05 | measured (abstract) | n=1
- **F89** A reliance disclaimer was the only intervention that raised appropriate reliance; none changed accuracy (N=400) | https://arxiv.org/html/2412.15584v3 | 2024-12 | measured | n=1
- **F90** Developers review agent work by reading the plan ("plan as proxy"); agents state wrong reasons ~10% of the time while sounding confident (N=17 interviews) | https://arxiv.org/html/2606.05391 | 2026-06 | measured (qualitative) | n=1
- **F91** Developers adopt LLM suggestions without questioning ("suggester preference" 102×, n=14) | https://arxiv.org/html/2601.08045 | 2026-01 | measured (small) | n=1
- **F92** METR RCT: developers 19% slower with AI but felt 20% faster — felt benefit is not evidence (METR now calls the result out of date) | https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ ; https://metr.org/blog/2026-02-24-uplift-update/ | 2025-07 / 2026-02 | measured (stale) | n=1
- **F93** RAIM ablation (read in full by two lenses, one origin): full 34.21% → w/o multi-design 21.05% → w/o patch evaluation 22.81% (5 designs, LLM picks without test-based evaluation); the "39.47" snippet was Table 1 Gemini full system; single model DeepSeek-v3.2, n=114 NoCode-bench Verified, one run, temp 0, no cost; confound: 1 patch vs 5 patches + judge | https://arxiv.org/html/2603.01814 | 2026-03-02 | measured | n=1
- **F94** RAIM: more designs lower selection accuracy (88.6% → 71.7%); success 3 designs 31.58 · 5: 34.21 · 7: 32.46 · 9: 28.95; N=1/2 not tested | https://arxiv.org/html/2603.01814 | 2026-03 | measured | n=1
- **F95** CodeTeam: no N=1 architect arm; dynamic developer-plan ablation 51.7 vs 46.6 SketchBLEU (similarity metric, 19 tasks, Qwen2.5-72B, 3 seeds); its 4 architect plans share ~58–75% of files/APIs | https://arxiv.org/html/2606.22082 | 2026-06 | measured | n=1
- **F96** SGAgent: removing the suggestion/planning stage 51.3% → 38.0% on SWE-bench Lite (snippet only) | https://arxiv.org/html/2602.23647 | 2026 | measured (snippet) | n=1
- **F97** 85 agent plan files studied: no outcome metric; whether plans change outcomes is "the most pressing open question" | https://arxiv.org/html/2608.04661 | 2026-08 | measured (descriptive) | n=1
- **F98** PlanSearch (origin) often hurts pass@1, gains only at large k with oracle selection; per 10k tokens it loses to direct solving on LiveCodeBench-v6 | https://arxiv.org/html/2409.03733 ; https://arxiv.org/html/2605.27000 | 2024-10 / 2026-07 | measured | n=2
- **F99** LLM-only tournament selection over 16 rollouts, with no access to ground-truth outcomes, tests or test samples (§2.3), frontier models, Table 3: selection alone (Iter 0 → Select-K) gained +2.8 to +5.2 pts on SWE-bench Verified (Opus 70.94→75.00, Sonnet 67.41→72.60) and +3.9 to +10.2 pts on Terminal-Bench v2.0 (GPT-5 31.32→35.23, Sonnet 40.62→50.85); the ~0.4–2.1 pts over a random pick is the final stage, after refinement and a second selection, a different comparison (corrected 2026-10-11 after a debate-loop re-read); refinement conditioned on earlier attempts lowered oracle pass@16 | https://arxiv.org/html/2604.16529 | 2026-04 | measured | n=1
- **F100** At a fixed token budget, 10 parallel attempts gain only +2.8 pts on SWE-Bench Pro even with oracle selection; "Newer models therefore often extract more value from a single long trajectory." | https://arxiv.org/html/2606.17930v1 | 2026-06 | measured | n=1
- **F101** LLM selectors break 4.7–5.7% of already-correct samples; executed public tests capture ~69% of the oracle gap, self-generated tests ~23% | https://arxiv.org/html/2607.17531 | 2026-07 | measured | n=1
- **F102** Selecting what an LLM judge likes raises judge approval (0.20 → 0.588) while the true pass rate stays flat | https://arxiv.org/html/2607.05904 | 2026-07 | measured (small models) | n=1
- **F103** Execution-free selection is weak: verifiers lean on style and plateau ~43% vs oracle 64.4% (R2E-Gym); in R2E-Gym the execution-free verifier alone took single-rollout pass@1 34.4% to 42.8% best@26 (+8.4), with a trained verifier (corrected 2026-10-11 after a debate-loop re-read); judge selectors improve then decline with more candidates (Trae Agent); LLM selection without tests is worse than voting (CodeMonkeys) | https://arxiv.org/html/2504.07164v1 ; https://arxiv.org/html/2507.23370 ; https://arxiv.org/html/2501.14723v1 | 2025 | measured | n=3
- **F104** How good a plan looks to a judge does not predict success (|r| ≤ 0.181 on ALFWorld); Plan+ReAct agents keep their declared structure in only part of their trajectories: 22–45% typical, lowest 12.1% on SWE-bench (Gemma) (corrected 2026-10-11 after a debate-loop re-read) | https://arxiv.org/html/2609.38108v1 | 2026-09 | measured | n=1
- **F105** Agents follow given plans only partly; "A subpar plan hurts performance even more than no plan at all." | https://arxiv.org/html/2604.12147v2 | 2026-04 | measured | n=1
- **F106** Plan-then-code with a reasoning planner scored below the coder alone on HumanEval+ (75.6% vs 78.0%); planner guidance introduced errors (weak, counts do not reconcile) | https://arxiv.org/html/2603.03406v1 | 2026-03 | measured (weak) | n=1
- **F107** LLM-written "different" solutions fail together, same model too (§IV-B) (corrected 2026-10-11 after a debate-loop re-read); asking for an out-of-the-box solution barely changes failure correlation | https://arxiv.org/html/2607.02808 ; https://arxiv.org/html/2607.03174 | 2026-07 | measured | n=2
- **F108** Multi-agent gains may be extra test-time compute, not coordination: CoT-SC 57.09 vs best multi-agent 55.97 on SWE-bench Lite (GPT-5) | https://arxiv.org/html/2606.13003 | 2026-06 v2 | measured | n=1
- **F109** Involving users in LLM planning slightly lowered plan quality and raised frustration; "plausible plans generated by the LLMs can mislead users" (N=248, GPT-3.5, not coding) | https://arxiv.org/html/2502.01390v1 | 2025-02 | measured | n=1
- **F110** Choose a technology by building a prototype, not by comparing on paper (Willison) | https://simonwillison.net/guides/agentic-engineering-patterns/better-code/ | undated | practitioner | n=1
- **F111** FeatBench: the main feature-level failure is regressions from aggressive implementation, not the design choice | https://arxiv.org/html/2509.22237v1 | 2025-09 | measured (indirect) | n=1

## Contradictions

- **C1** F13 LLM outputs are homogeneous vs F14 the 0.8 threshold does not establish it — not averaged; the skill's response (routes differ on a named dimension) holds either way.
- **C2** F48 LLM-written context files cost more for no gain vs F49 AGENTS.md cuts tokens and runtime — resolved by boundary: they measure different things (pass rate vs efficiency).
- **C3** F26 self-preference is real vs F27 most of it is evaluator quality — not averaged; no model grades another's output in this step.
- **C4** F21 46.7% of failures sit in clarification/planning vs F23 intent comprehension is strong / F24 capable models localize then thrash — resolved by boundary: F21 counts unstated constraints and approach, F23 the stated goal; F24 is small-task, patch-time.
- **C5** F69 developing several options raises decision success vs F70 experts rarely compare and do well in predictable environments — resolved by boundary (Kahneman & Klein): compare at novel, irreversible choices; recognize on routine ones.
- **C6** F85 an evidence-for/against display cuts overreliance vs F86 evaluative AI without a recommendation is not better — open: no user adjudication; the expert acts on F86 (keep the recommendation) and adds F85's evidence per route.
- **C7** F63 the plan step's value shrinks as models get stronger vs F57/F6 reviewing a plan surfaces decisions and requirements early — resolved by boundary: model planning matters less, user decisions surfaced early do not.
- **C8** F46 share full context, avoid subagents vs F47 a clean-context reviewer works best — resolved by boundary: an advisor that writes nothing works in a clean context if its brief carries the full user context.
- **C9** F60 generate alternatives privately and show one vs F61 show options with trade-offs and a recommendation per decision — resolved toward F60 with a gate (expert, second pass): one route by default, full routes at a one-way door or a testable fork.
- **C10** F16 a separate assessor beats the same check inside the main agent vs F36/F37 a separate agent adds a lossy hand-off — resolved by design: keep the separate assessor, hand constraints over as imperative lines and end with a backbrief (F79).
- **C11** F93 five designs beat one (34.21 vs 21.05) vs F99/F103 LLM-only selection adds +2.8 to +5.2 points on SWE-bench Verified and +3.9 to +10.2 on Terminal-Bench v2.0 (F99, selection alone), more with a trained verifier (F103) (corrected 2026-10-11 after a debate-loop re-read) — resolved by RAIM's own no-evaluation arm (22.81): with RAIM's five designs, the gain needs test-backed selection; F99 shows a few points without tests over 16 rollouts.
- **C12** F96 a planning stage helps vs F104/F105 agents do not follow declared plans and a subpar plan is worse than none — resolved toward F104/F105 (F96 is a snippet): short checkable plan, a no-plan exit, constraints handed over explicitly.

## Open — where to dig next

- **F16** (G1) a second coding study of a separate clarifier vs the same check inside the main agent · arXiv cs.SE, "underspecified issue" + "clarification agent"
- **F36** (G1) a second measure of how much of a planner's spec survives into the executor · arXiv, "planner executor hand-off fidelity"
- **F74** (G1) the premortem quality study read first-hand · Gallop & Bischoff 2016 via ResearchGate or the author's dissertation
- **C6** (G2, unadjudicated) — F85 vs F86 — whether showing evidence per option without a recommendation helps expert developers · a developer study with planted errors in AI designs; none exists yet
- **L1** The Horizon Gap survey of long-horizon agents · https://arxiv.org/abs/2608.06663 · 2026-08 · unclassified · not pursued: a survey of studies the run already searched
- **L4** FEA-Bench / Commit0 failure analyses · https://arxiv.org/abs/2503.06680 · 2025 · unclassified · not pursued: F22 carries large-task failure analysis
- **L5** "Humans overrely on overconfident language models" · https://arxiv.org/abs/2507.06306 · 2025-07 · unclassified · not pursued: F82/F88 cover it
- **L6** Hills, "Could you be wrong" metacognitive prompt · https://arxiv.org/abs/2507.10124 · 2025-07 · unclassified · not pursued: PDF did not extract; F10 covers self-critique limits
- **L7** PreFlect pre-execution plan critique from past errors · https://arxiv.org/abs/2602.07187 · 2026-02 · measured (snippet) · not pursued: not in the ask
- **L8** Gallop & Bischoff 2016 premortem primary · https://www.tandfonline.com/doi/abs/10.1080/19488289.2016.1240118 · 2016 · measured (unread) · not pursued: HTTP 403
- **L9** Horthy primary talks on what went wrong with RPI · https://www.youtube.com/watch?v=H_1PygR7kwk · 2026 · practitioner · not pursued: no transcript reachable
- **L10** DCAS plan-source intervention full text · https://arxiv.org/abs/2608.06113 · 2026-08 · measured (abstract only) · not pursued: HTML 404, PDF no extract
- **L11** SkillAxe / EvoSkills: self-written skills help only with a verifier loop · https://arxiv.org/abs/2606.10546 · 2026 · measured (snippet) · not pursued: the skill never writes new skills
- **L12** ASPI: seeking clarification amplifies prompt-injection exposure · https://arxiv.org/html/2605.17324v1 · 2026-05 · measured (snippet) · not pursued: questions go to the user
- **F93** (G1, expert round) a second study of several designs vs one on feature-size coding tasks, with a cost-matched arm · arXiv cs.SE, "multi-design" + NoCode-bench / FeatBench
- **F104** (G1, expert round) a second measure of how often coding agents follow a given plan · arXiv, "plan adherence" + SWE-bench
- **F105** (G1, expert round) a second test of "a subpar plan is worse than no plan" on coding agents · arXiv, "plan quality ablation" + SWE-bench
- **L13** (expert round) EvoMAS: multi-agent beats best-of-10 at fewer tokens · https://arxiv.org/pdf/2602.06511 · 2026-02 · unclassified · not pursued: execution-time, not pre-task
- **L14** (expert round) SAGE: plans from a different model often resolve more · https://arxiv.org/abs/2511.05931 · 2025-11 · measured (snippet) · not pursued: the planner model is fixed at opus
- **L15** (expert round) order and primacy effects when an LLM recommends among its own options · https://arxiv.org/abs/2506.14092 · 2025-06 · unclassified · not pursued: F83 carries default effects
- **L16** (expert round) in human–LLM co-planning trust rises while verification declines · https://arxiv.org/abs/2605.23023 · 2026-05 · unclassified · not pursued: F82/F109 carry it

dead ends:
- a head-to-head of N plans vs one plan on software-engineering tasks under identical conditions — none found · empirical-plan
- gating on task size, uncertainty or reversibility tested as signals — none found · empirical-plan
- step-back / metacognitive prompting tested on current reasoning models — none found · empirical-ask
- fresh-context vs same-conversation anchoring of a reviewer — none found · empirical-ask
- a quantified skip threshold from a primary named practitioner — none (the "one sentence, <3 files" rule is third-party) · practitioner
- a controlled with-plan vs without-plan comparison on large or feature-level tasks — none found · empirical-long
- a study that plants a wrong assumption in an AI plan and measures developer detection — none found · empirical-review
- an LLM premortem measured against real risks — none found · empirical-review
- an independent reproduction of RAIM or CodeTeam — none · expert round
- a developer study choosing among 2–3 AI-written designs — none · expert round
- Cynefin validation study 2016–2026 — none · lateral
- Simon Willison's agentic engineering guide has no planning chapter · practitioner2

## Expert verdict

Final table of the second pass (fresh `research-expert`), row for row. Changed rows: 9 —
verdicts L2, L3 (open → skip); resolutions F11, F12, F60, F69, F78, C5, C9.

Design call (expert, second pass): one recommended route by default, one line per rejected
alternative with its reason; 2–3 full routes only at a one-way door or at a fork a cheap test
(a spike or prototype) can decide, each naming the deciding test; cap 3. Risk taken: no study
measures a human choosing between AI-written coding designs.

| item | verdict | why |
|---|---|---|
| F1 | use | Strong models gain little from planning, so the step's value must come from what the user decides. One run per task. |
| F2 | use | The Planner alone adds +2.4 points on the ablation; the team's loss in the upper quintiles includes the Verifier's effect, so F2 does not back the entry gate on its own (corrected 2026-10-11 after a debate-loop re-read). |
| F3 | skip | Removing the planner also removed structure. F1/F2 carry the direction (F96 is just as confounded). |
| F4 | skip | Not coding. F2 carries it. |
| F5 | use | Supports assessing before the first edit. Correlation only. |
| F6 | use | Core: the gain came from the user answering clarifying questions. The first route is usually the one taken (F82/F83). |
| F7 | use | Overthinking lowers resolve: hard bound on output length. |
| F8 | skip | Not a step here. F31/F33 cover estimates. |
| F9 | skip | PDDL skill does not change how routes are written. |
| F10 | use | Each step's "why" names something checkable. |
| F11 | use | changed from use ("routes must differ on a named dimension"), second pass: when routes are shown they still differ on the named one-way-door dimension; F107 shows persona or out-of-the-box prompting does not make failures independent, so the skill does not rely on those prompts for diversity. |
| F12 | use | changed from use ("generate 1–3 routes in one call"), second pass: when the alternatives gate fires, generate them in one call, not one agent per route; one call is no longer the default way to produce routes (F93/F98/F100). |
| F13 | skip | Disputed (F14). F11 carries the point. |
| F14 | skip | Matters only to C1. |
| F15 | use | Explicit gap checklist, not "ask if unclear". |
| F16 | use | Backs the separate-agent choice. One coding source, about 1.7x cost (corrected 2026-10-11 after a debate-loop re-read). Asking is the main value. |
| F17 | use | Cap at about 3 answerable questions. |
| F18 | use | The user still reviews the gap list. Never claim the list is complete. |
| F19 | use | Small question cap. |
| F20 | use | Pin requirements and interfaces before hand-off. |
| F21 | use | Each route names its constraints and how it is verified. |
| F22 | use | Release-size failures come from misreading instructions, so play the requirements back. |
| F23 | skip | F21 covers it. |
| F24 | skip | Small tasks, patch stage. |
| F25 | use | Check the route before work starts. Not SWE. |
| F26 | skip | No model grades another's output here. The user chooses. |
| F27 | skip | Same as F26. |
| F28 | skip | Same as F26. |
| F29 | skip | Same as F26. |
| F30 | use | A fresh context is independent in what it sees, not in its errors (F107: solutions from the same model tend to fail on the same inputs; F30 finds the same across models) (corrected 2026-10-11 after a debate-loop re-read). The user stays the check. |
| F31 | use | No success or confidence forecast in the output. |
| F32 | skip | Cross-agent model, cannot be prompted. |
| F33 | use | No time or token estimates in the output. |
| F34 | skip | Keeping a recommendation under pushback belongs to the interview skill and the project's instruction files, not to this step. |
| F35 | skip | Execution-time, not pre-task. |
| F36 | use | Constraints travel as explicit lines. The 21% figure has one source. |
| F37 | use | Constraints as imperative lines, not hedges. |
| F38 | skip | Simulation. F36/F37 carry it. |
| F39 | skip | General taxonomy. |
| F40 | use | Parallel subagents are read-only; writes happen in sequence. |
| F41 | use | The expert runs on opus. Research results enter the routes as data. |
| F42 | use | Explicit constraints section in the output contract. |
| F43 | use | Supports the entry gate. Not coding. |
| F44 | use | One user review of the route(s), not repeated loops. |
| F45 | skip | Not SWE. |
| F46 | use | The brief carries the user's stated facts and constraints in full. |
| F47 | use | The clean-context agent only assesses and writes nothing. |
| F48 | use | Output is task-specific and short, never a repo overview. |
| F49 | skip | About repo context files, not a task brief. |
| F50 | use | At most one existing skill per step (a hand-off choice; F50's best arm is 2–3 skills) (corrected 2026-10-11 after a debate-loop re-read). The step never writes a new skill. |
| F51 | use | Naming the fitting skill in the hand-off has value. |
| F52 | use | The description must say where it stops compared with decompose-and-delegate and plan-feature. |
| F53 | skip | Large-library retrieval. |
| F54 | use | Entry gate. |
| F55 | use | Length cap. |
| F56 | use | SKILL.md as numbered steps, not prose. |
| F57 | use | Assumptions get their own visible section. |
| F58 | use | One short markdown output the user reads and edits. |
| F59 | use | Open question first for the end goal. Decisions in grill-me format. |
| F60 | use | changed from use ("private alternatives overruled by user's ask (C9)"), second pass: take the entry gate, size check, play-back, approval gate and hand-off to one named skill; generating alternatives privately and showing one becomes the default, because a model's pick on paper adds a few points at most (F93 +1.8; F99 +2.8 to +10.2 over 16 rollouts) and each shown route costs reading (F55) (corrected 2026-10-11 after a debate-loop re-read); rejected alternatives appear as one line each, full routes only at the C9 gate. |
| F61 | use | Explicit invocation, shortest path to review points, research questions blind to the wanted answer. |
| F62 | use | Weak support for hardening the skill with debate-loop. F104 means it hardens the skill text and proves nothing about plan value. |
| F63 | use | Gate input only. |
| F64 | use | Gate on risk and verifiability, not only size. |
| F65 | skip | Anecdote. F17 sets the cap. |
| F66 | skip | Outside the time window. F1 carries it. |
| F67 | use | No precedent for a skill-fit check, so keep it light. Hand off to full-cycle on ticket work. |
| F68 | use | Schoenfeld control questions are the reason for each step, reused as checks during execution. |
| F69 | use | changed from use ("2–3 routes on large tasks"), second pass: supports human deciders comparing options on high-stakes, non-routine choices — the one-way-door case, not every large task; 1999 observational managers study, and F93/F103/F107 show LLM-written options compared on paper add a few points at most without tests. |
| F70 | use | Skip route comparison on routine, predictable tasks. |
| F71 | use | Frame section: decide / not decide / given / goals. |
| F72 | use | /web-research only for points whose answer could change the route choice. |
| F73 | skip | The skill produces no estimates. |
| F74 | skip | Thin evidence, and a premortem is not in the ask. |
| F75 | skip | No validation. |
| F76 | use | Standards backing for the gate. |
| F77 | use | Non-goals line. No route comparison when the choice is not ambiguous. |
| F78 | use | changed from use ("one route when only one is viable"), second pass: one route is the default; when the gate opens routes, they must be distinguishable and complete. |
| F79 | use | The hand-off ends with the main agent restating the intent and first steps. F104/F105 make this more important, since agents follow given plans only partly. |
| F80 | use | Spend comparison effort on one-way-door choices. This is now the main trigger for showing alternatives (C9). |
| F81 | skip | No design consequence. |
| F82 | use | Assumptions plus "what would make this wrong" next to the recommended route. |
| F83 | use | Same as F82. |
| F84 | use | Backs keeping the route list short under complexity; it does not fix the number 3 (corrected 2026-10-11 after a debate-loop re-read). |
| F85 | use | Evidence for and against per route. Recommendation kept (C6). |
| F86 | use | Keep the recommendation. |
| F87 | skip | F85/F86 cover it. |
| F88 | use | Plain first-person hedge on uncertain points. Abstract only. |
| F89 | skip | No change in accuracy. |
| F90 | use | Tie each reason to evidence (file:line, a source). |
| F91 | skip | n=14. F6/F82 carry it. |
| F92 | skip | The skill has no keep/kill check and no run log, so no rule rests on it. |
| F93 | use | Core to R1: five designs beat one only with test-backed patch selection; the LLM-picks-on-paper arm (22.81) is about the same as one design (21.05). So the skill defaults to one route and shows alternatives only where a test can decide. Risk: one model, one run, n=114, confounded. |
| F94 | use | More designs lower selection accuracy even with tests; success peaks at 5 designs (34.21, vs 31.58 at 3), so the cap of 3 when routes are shown is a reading-cost choice, not a measured optimum (corrected 2026-10-11 after a debate-loop re-read). N=1/2 was not tested. |
| F95 | skip | No N=1 arm, a similarity metric and 19 tasks. Its overlap between plans is carried by F107. |
| F96 | skip | Snippet only. C12 settles it against F104/F105. |
| F97 | skip | Whether plans change outcomes is open. Descriptive, and no rule rests on it since F92 was dropped. |
| F98 | use | Multiple plans hurt pass@1 and lose per token unless an oracle selects. Supports one route by default. n=2, competitive programming. |
| F99 | use | The expert's own pick among its routes, selection alone, adds +2.8 to +5.2 points on SWE-bench Verified and +3.9 to +10.2 on Terminal-Bench v2.0 (corrected 2026-10-11 after a debate-loop re-read). The output's value is the decisions it puts in front of the user, not the agent's choice. |
| F100 | use | At a fixed budget, newer models get more from one long trajectory. Supports one route by default and a short pre-step. |
| F101 | use | Executed tests close most of the selection gap, so a shown alternative names the test or spike that would decide it. |
| F102 | skip | Small models. F103 carries the point. |
| F103 | use | Execution-free selection is weak (n=3), so a paper comparison of routes is not treated as evidence for a pick. |
| F104 | use | Judged plan quality does not predict success on ALFWorld (corrected 2026-10-11 after a debate-loop re-read), and agents drop plan structure. So the skill does not polish the plan; it moves constraints as imperative lines and ends with a backbrief (F37/F79). |
| F105 | use | A subpar plan is worse than none. This backs the entry gate and a "no plan, just do it" exit, and keeps steps few and checkable. |
| F106 | skip | Weak, function-level HumanEval+, counts do not reconcile. |
| F107 | use | "Different" routes from one model fail together, so alternatives are never offered as a hedge; they must differ on the one-way-door dimension. n=2. |
| F108 | skip | Gains as extra compute changes no design choice. F30/F16 already limit the separate agent's claim. |
| F109 | use | "Plausible plans can mislead users", so user input is limited to decisions and answerable questions, not co-editing the plan. Also backs F82. Risk: GPT-3.5, not coding. |
| F110 | use | When routes differ on a technology choice that can be tested, the route's step is "prototype both", not a comparison on paper. Practitioner, n=1. |
| F111 | use | Feature failures come mainly from regressions, not design choice, so route steps spend effort on verification and regression checks rather than more alternatives. Indirect. |
| C1 | skip | The design response holds either way. |
| C2 | use | Act on F48. |
| C3 | skip | No model judges another here. |
| C4 | use | Act on F21 for large tasks. |
| C5 | use | changed from use ("act on F69 for large non-routine; F70 sets the skip"), second pass: act on F80 plus C11 — alternatives appear at one-way doors or forks a test can decide, not because the task is large. F70 still sets the skip. |
| C6 | use | Act on F86: keep the recommendation. F85 adds evidence per route. |
| C7 | use | Act on F6/F57: the value is decisions surfaced early. F63 informs the gate. |
| C8 | use | Act on F47. F46 limits it: the brief carries the full user context. |
| C9 | use | changed from use ("act on F61: user asked to see routes; F84 caps at 3"), second pass: resolve toward F60 with a gate — one recommended route plus one line per rejected alternative by default; 2–3 full routes only at a one-way door (F80) or a fork a cheap test can decide (F101/F110), capped at 3 as a reading-cost choice (corrected 2026-10-11 after a debate-loop re-read). Fits the user's "possibly" and R1's finding that paper selection adds a few points (F99, selection alone: +2.8 to +5.2 on SWE-bench Verified, +3.9 to +10.2 on Terminal-Bench v2.0) (corrected 2026-10-11 after a debate-loop re-read). |
| C10 | use | Act on F16. F36/F37 decide the hand-off format (imperative constraints plus F79). |
| C11 | use | Act on RAIM's own no-evaluation arm: with RAIM's five designs, several designs pay off only with test-backed selection (F99 shows a few points without tests over 16 rollouts). The skill shows alternatives only where a test can decide, and names the test. |
| C12 | use | Act on F104/F105 over F96 (snippet): the plan stays short and checkable, has a no-plan exit, and its constraints are handed over as imperative lines. |
| L1 | skip · not pursued | |
| L2 | skip | changed from open → R1, second pass: the round read CodeTeam (F95); no single-architect arm, and F95 is skipped. |
| L3 | skip | changed from open → R1, second pass: replaced by F93; the 39.5% snippet was a different configuration (Gemini full system). |
| L4 | skip · not pursued | F22 carries it. |
| L5 | skip · not pursued | F82/F88. |
| L6 | skip · not pursued | F10. |
| L7 | skip · not pursued | Not in the ask. |
| L8 | skip · not pursued | Premortem not in the ask. |
| L9 | skip · not pursued | F57 has 3 sources. |
| L10 | skip · not pursued | Content unknown. |
| L11 | skip · not pursued | The skill never writes new skills. |
| L12 | skip · not pursued | Questions go to the user. |
| L13 | skip · not pursued | Not read. Multi-agent at execution time, not pre-task. |
| L14 | skip · not pursued | Snippet. The planner model is fixed at opus (F41). |
| L15 | skip · not pursued | F83 carries default and order effects. Listing the recommended route first is already the design. |
| L16 | skip · not pursued | F82/F109 carry automation bias in co-planning. |

## What could not be established

- **W1** whether upfront planning helps MORE on large tasks than on small ones — every controlled planning comparison found runs on small SWE-bench-size tasks · would settle it: a with-plan vs without-plan ablation on feature- or release-size tasks (SWE-EVO, FeatBench, NoCode-bench) with a cost-matched arm
- **W2** whether a GATED pre-task step beats an always-on step or none — no study tests a gate · would settle it: an ablation with the gate on and off

## Injection attempts

none seen — the scout, the 12 lenses and both expert passes each reported none, and the
orchestrator's reads of the companion files found none.

## Recommendation

Build `meta-thinking` as a gated, offered-or-invoked skill whose value is the decisions it puts
in front of the user, not the model's own pick among routes:

1. An entry gate first: skip on small, clear, routine or cheap-to-undo tasks, and on single
   scoped changes (F54, F105) (corrected 2026-10-11 after a debate-loop re-read); gate on observable signals, never on the agent's own feeling
   of difficulty (F31).
2. One fresh-context assessor (opus, read-only, offline, cannot spawn), briefed with the user's
   words verbatim, the facts already settled and the constraints as imperative lines — never the
   orchestrator's own answer (F16, F37).
3. A short output (one markdown file the user reads and edits): the frame (goal, decide / not
   decide / given, non-goals), what is known vs assumed with "what would make this wrong",
   at most 3 answerable questions (more go to `/grill-me`), at most 3 research items whose answer
   could change the route, ONE recommended route as numbered "do — why — check" steps with at
   most one skill per step (a hand-off choice) (corrected 2026-10-11 after a debate-loop
   re-read), one line per rejected alternative, and 2–3 stop triggers for the execution; 2–3 full routes only at a one-way door or a fork a cheap test can decide, each
   naming that test (F6, F21, F93, F99). No success, time or token forecasts (F31).
4. One user review, then a backbrief (restate goal, route, constraints, first steps) and a
   hand-off to one named skill (F79, F104).

Every other design rule and the ids behind it are in the Expert verdict table above.

One departure from a verdict row: F59's "open question first for the end goal" is not used.
Section 3 questions go through `AskUserQuestion` with options and a recommendation, and its
free-text answer is always open.

## Source ledger

Every finding line above is a ledger row (URL · what it answered · source class · date) —
111 rows. Sources consumed that produced no finding:

| URL | what it answered | class | date |
|---|---|---|---|
| https://arxiv.org/abs/2608.06113 | DCAS: abstract only; HTML 404, PDF did not extract — no numbers | measured (unread) | 2026-08 |
| https://arxiv.org/abs/2609.23939 | XYEval: PDF unreadable | — | 2026-09 |
| https://arxiv.org/abs/2608.21377 | agentic scaffolding and sycophancy: HTTP 404 | — | 2026-08 |
| https://arxiv.org/abs/2605.17193 | semantic collapse: HTML 404, abstract only | — | 2026-05 |
| https://www.youtube.com/watch?v=YwZR6tc7qYg | Horthy talk: title only | practitioner | 2026-03 |
| https://www.humanlayer.dev/blog | no RPI post after 2025-08-29 | canonical (listing) | 2026-10 |
| https://simonwillison.net/guides/agentic-engineering-patterns/ | no planning chapter | practitioner | 2026-02 |
| https://www.tandfonline.com/doi/abs/10.1080/19488289.2016.1240118 | Gallop & Bischoff: HTTP 403 | — | 2016 |
| https://hbr.org/2007/11/a-leaders-framework-for-decision-making | Cynefin: teaser only | canonical (unread) | 2007-11 |
| https://hbr.org/2003/07/delusions-of-success-how-optimism-undermines-executives-decisions | paywalled, unread | — | 2003-07 |
| https://www.pmi.org/standards/pmbok | PMBOK 8th edition page: HTTP 403 | canonical (unread) | 2025-11 |
| https://en.wikipedia.org/wiki/Ralph_D._Stacey | Stacey reportedly dropped his matrix | anecdote | undated |
| https://www.ryansinger.co/pitfalls-when-adopting-shape-up/ | read, then excluded (work-management vendor exclusion) | practitioner | 2025-10 |
| https://agentpatterns.ai/workflows/research-plan-implement/ | aggregator of RPI; cites an excluded vendor domain; not cited | practitioner (secondary) | 2026-06 |
| https://github.com/matanshavit/qrspi | third-party QRSPI summary of Horthy (feeds F56, F57) | anecdote | undated |
| https://podwise.ai/episodes/7669928 | secondary summary of Horthy (feeds F56, F57) | practitioner (secondary) | 2026 |
