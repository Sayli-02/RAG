# Hybrid search

1. **One-line definition**
Hybrid search runs semantic search and keyword search, then merges the two ranked lists into one.

2. **Why it exists** (the problem it solves)
The two scores are not on the same scale. Adding a cosine similarity of 0.8 to a BM25 score of 12 does not mean anything. A merge that uses rank, instead of the raw score, stays fair to both lists.

3. **Analogy**
Two judges each hand you a top-10 list. A name that is third on both lists is a stronger pick than a name that is first on only one list. You do not add their point systems together.

4. **How it works** (step by step)
- **Step 1:** Semantic search returns up to 10 chunk ids, best first. BM25 returns up to 10.
- **Step 2:** Reciprocal rank fusion gives each id `1 / (60 + rank)`. Rank 1 contributes `1/61`. A chunk in both lists gets the sum.
- **Step 3:** The merged list is sorted by that sum.
- **Step 4:** The cross-encoder then reranks this shortlist. Fusion does not pick the final four by itself.

5. **Where it is in FinScope** (file + function)
- File: [backend/app/rag/retrieval.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/retrieval.py)
- Functions: `reciprocal_rank_fusion`, `fuse`, and `hybrid_search`
- The constant `RRF_K` is 60

6. **Common mistakes**
- Adding cosine and BM25 scores directly.
- Forgetting a chunk that appeared in only one list. Fusion keeps those too, with a smaller score.
- Using the fusion score as the citation score. The citation stores the later reranker score.

7. **Check yourself**
1. *Why is the fusion constant 60?*
2. *Which chunk wins if it is on both lists?*
3. *What is passed to the reranker?*

---
**Answers:**
1. It is the usual reciprocal-rank-fusion setting. It keeps the first rank from completely drowning out the second rank.
2. The one whose ranks, added as `1 / (60 + rank)`, produce the larger sum. Being high on both lists beats being high on only one.
3. The fused chunks, still in fusion order, before the reranker replaces the score.
