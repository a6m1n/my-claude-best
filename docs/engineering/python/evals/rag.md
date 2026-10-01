# Testing RAG

**Navigation**

- [1. Purpose and the one rule](#1-purpose-and-the-one-rule)
- [2. Retrieval, measured apart](#2-retrieval-measured-apart)
- [3. The answer](#3-the-answer)
- [4. Citations](#4-citations)
- [5. Questions the documents cannot answer](#5-questions-the-documents-cannot-answer)
- [6. The test set](#6-the-test-set)
- [7. Library metrics: same name, different meaning](#7-library-metrics-same-name-different-meaning)
- [8. Where it stops holding](#8-where-it-stops-holding)
- [9. Review checklist](#9-review-checklist)
- [10. Sources](#10-sources)

## 1. Purpose and the one rule

A RAG application retrieves passages from a document store and asks a model to answer from them.
This file is for anyone who builds or changes one: the chunking, the index, the retriever, the
number of passages, the prompt that answers. Its levels are those of [evals.md](evals.md) section 1,
and the method there holds.

The one rule: **measure retrieval and the answer apart, grade the answer against a reference
wherever one exists, and build the test set from questions real users asked.**

TruLens names the three parts to check the "RAG triad": whether the retrieved context fits the
question, whether the answer stays within the context, and whether the answer addresses the
question. The sections below take them in that order, plus citations and unanswerable questions.

## 2. Retrieval, measured apart

**Must.** Label a set of real questions with the ids of the documents or chunks that answer them,
and measure the retriever on it with your own code: the hit rate (at least one right document in
the top k), recall at k (the share of right documents in the top k) and, when the order matters,
MRR (how high the first right document sits). These are a few lines each and need no model.

```python
def recall_at_k(retrieved_ids: Sequence[str], relevant_ids: Set[str], k: int) -> float:
    """The share of the relevant documents that appear in the first k retrieved."""
    # A question no document answers has no recall; section 5 scores it.
    if not relevant_ids:
        raise ValueError("recall at k needs at least one relevant document")

    return len(set(retrieved_ids[:k]) & relevant_ids) / len(relevant_ids)
```

`Sequence` and `Set` come from `collections.abc`: the widest types the body uses
([python.md](../language/python.md) section 3).

Why: when the right passage never arrives, no prompt fixes the answer; Jason Liu measures recall
before he touches the prompt. In one production RAG system, whether any source was found explained
69 to 83% of the variance in answer quality. Split the numbers by question type: an average of 70%
can hide 5% on questions that need several documents.

**Must.** Keep the end-to-end eval of the answer too. A better retrieval number does not promise a
better answer: across six models and five datasets, a ranking metric (nDCG) and the answer's
accuracy correlated at 0.33 to 0.80, and more passages raised recall while the answer's quality rose
and then fell. Choose the number of passages on the answer's quality, not on recall.

**Must.** Never tune the retriever against relevance labels a model wrote without checking them.
Model-written labels ranked systems well overall and poorly at the top, and a system built to please
the labelling model ranked 5th by the model and 28th by people.

## 3. The answer

**Must.** Grade the answer against a reference answer wherever the question has one: exact values
by code, the rest by a reference-based judge ([judges.md](judges.md) section 2). Reference-based
correctness tracked graded factual errors closely in one study, while reference-free scores did not.

**Should.** Check that the answer stays within the retrieved context, claim by claim (faithfulness,
or groundedness). Use the score to compare versions over the whole set, and read the failing cases;
do not trust it on a single answer until you have checked it against your own labels
([judges.md](judges.md) section 6). Independent studies found generation metrics from Ragas,
DeepEval, RAGChecker and Opik agreed weakly with people on a business QA set; zero-shot judges found
hallucinations at a balanced accuracy of 66 to 69%, and 84% only with people's labelled examples in
the prompt; detectors got worse beyond 5,000 characters of context.

**Optional.** Answer relevance scores (whether the answer addresses the question). Ragas computes
it from questions a model generates back from the answer and their similarity to the real question;
it does not check correctness, and it breaks on refusals (section 5).

## 4. Citations

**Must**, when answers carry citations: check each cited passage against the sentence it is
attached to. Two numbers, from ALCE (Gao et al., 2023): **citation recall**, the share of sentences
whose cited passages support them, and **citation precision**, the share of citations that support
their sentence. Write the check yourself: none of Ragas, DeepEval, promptfoo or openevals ships a
citation metric. The support check is a judge or an entailment model, and it needs validating on
your own labels ([judges.md](judges.md) section 6): ALCE's model agreed with people at a kappa of
0.70 on recall and 0.53 on precision, and checkers that worked on short claims fell to near chance
on long answers.

## 5. Questions the documents cannot answer

**Must.** Put questions the documents cannot answer into the set, and score them apart, as a
two-by-two table:

| | The system answered | The system said the documents do not say |
|---|---|---|
| the documents hold the answer | right or wrong answer | a missed answer |
| the documents do not hold it | an invented answer | right |

Report the invented-answer rate and the missed-answer rate separately: they trade off (one benchmark
measured a correlation of −0.78 between them), and the best systems reached only 42.9 to 47.4% on
recent refusal benchmarks. In an agent that can search again, the search overrode a correct "not
found" in 20 to 67% of cases. How the prompt offers the way out is
[prompt-engineering.md](../../any-language/prompt-engineering/prompt-engineering.md) section 8's; this table is how
the eval scores it. Write the scoring yourself: no library ships a refusal score, and Ragas' answer
relevance returns 0 or no value at all on a refusal, depending on the version and the code path.

## 6. The test set

**Must.** Build the test set from questions real users asked, at least 50 to 100 before you trust a
ranking of two setups, and include questions the documents cannot answer (section 5). On a
university chatbot, real questions averaged 6.8 words against 15.7 for generated ones, half of the
real ones had no answer in the documents, and the best setup's hit rate fell from 0.90 on generated
questions to 0.53 on real ones, with the ranking of setups flipped.

**Optional.** Generated questions (Ragas' test set generator, or a model asked for a few questions
per chunk) to start before you have users, or to compare retrievers. Generated sets ranked
retrievers much as people's sets did, and ranked answer generators badly. A person reads each
generated question before it counts, and real questions replace them as they arrive.

## 7. Library metrics: same name, different meaning

**Must.** Pick one implementation of each metric, pin its library version, and never compare scores
across libraries or versions. The same name means different things:

- Ragas' "context recall" is the share of a reference answer's claims found in the retrieved
  context, not recall at k; its "context precision" is a rank-weighted average over the retrieved
  chunks, with and without a reference.
- Ragas counts a claim as faithful when the context supports it; DeepEval counts it when the context
  does not contradict it, which passes more claims.
- The same metric in different tools gave different results on the same answers, because the prompts
  behind it differ.

**Must.** Count cases that got no score as failures of the run, never drop them from the average
([evals.md](evals.md) section 6). Ragas drops rows that raised, returns a sentinel score when an
answer runs past the judge's context, and returns nothing or 0 on answers it reads as non-committal,
which drops refusals out of averages. Ragas has had no release since January 2026, and version 0.4.3
fails to import next to current LangChain packages ([tools.md](tools.md) section 3).

## 8. Where it stops holding

- **A RAG system over a closed, small corpus** where every question is known in advance: test it
  like a lookup, with an exact expected answer per question.
- **Agentic RAG**, where an agent decides when to search: [agents.md](agents.md) holds as well, and
  its tool-call checks cover the searches.

## 9. Review checklist

| Section | Level | Ask |
|---|---|---|
| 2 | Must | Is retrieval measured on labelled real questions with your own code, and is the end-to-end answer still evaluated? |
| 3 | Must, faithfulness Should | Is the answer graded against a reference where one exists, with reference-free scores used only across the set? |
| 4 | Must, with citations | Are citation recall and precision measured, with the checker validated on your labels? |
| 5 | Must | Are unanswerable questions in the set, with invented and missed answers reported apart? |
| 6 | Must | Are there at least 50 to 100 real questions before a ranking is trusted? |
| 7 | Must | Is each metric's implementation and version pinned, and are cases with no score counted as failures? |

## 10. Sources

- TruLens, "RAG triad" (trulens.org); Ragas metric docs (context precision, context recall,
  faithfulness, answer relevance, factual correctness), version 0.4.3; DeepEval metric docs
  (faithfulness, contextual precision, recall and relevancy), read 2026-09-30.
- Jason Liu, "Systematically improving RAG applications", jxnl.co, 2025-01-24; Eugene Yan, "An LLM
  eval process", 2025-04.
- Production encyclopedia RAG, arXiv:2605.27220, 2026; "Is relevance propagated from retriever to
  generator", arXiv:2502.15025, 2025; nDCG vs end-to-end accuracy, arXiv:2510.21440, 2025; "Long
  context and hard negatives", arXiv:2410.05983, 2024.
- UMBRELA on TREC 2024 RAG, arXiv:2412.17156, 2024; TREC 2024 support evaluation,
  arXiv:2504.15205, 2025.
- Orange telecom study of RAG metrics, arXiv:2607.07302, 2026; GroUSE, arXiv:2409.06595 (v3 2025);
  FaithBench and FaithJudge, arXiv:2505.04847 (v2 2025); Trivia++, arXiv:2605.11330, 2026; factual
  correctness vs judges, arXiv:2609.15561, 2026.
- Gao et al., "ALCE", arXiv:2305.14627, 2023 (origin); attribution scorers across datasets,
  arXiv:2606.23915, 2026; CiteEval, arXiv:2506.01829, 2025.
- RefusalBench, arXiv:2510.10390, 2025; HopRefusalBench, arXiv:2608.01358, 2026; Abstain-R1,
  arXiv:2604.17073, 2026.
- Kucia and Gawlik, arXiv:2609.14579, 2026; "Can we evaluate RAGs with synthetic data",
  arXiv:2508.11758, 2025.
- Ragas issues #3028, #2995, #3004; ragas `_answer_relevance.py` source; fasrc/archi issue #502.
