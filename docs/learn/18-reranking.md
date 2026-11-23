# Reranking

1. **One-line definition**
A reranker reads the question and one chunk together and assigns that pair a new score. The first-pass lists only decided who gets this slower look.

2. **Why it exists** (the problem it solves)
Cosine and BM25 score the question and the chunk separately. A cross-encoder sees both at once, so it can tell that a chunk uses the right words but answers a different question.

3. **Analogy**
The first pass is a quick scan of the shelf. Reranking is reading the shortlisted pages with the question in your hand.

4. **How it works** (step by step)
- **Step 1:** Fusion produces a shortlist.
- **Step 2:** `cross-encoder/ms-marco-MiniLM-L-6-v2` scores each pair `(question, chunk text)`.
- **Step 3:** The chunks are sorted by that score, highest first.
- **Step 4:** `RERANK_K` (4) chunks are kept for the prompt. Their scores are what citations store.

5. **Where it is in FinScope** (file + function)
- File: [backend/app/rag/reranking.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/reranking.py)
- Functions: `rerank` and `_cross_encoder_scores`
- Called at the end of `hybrid_search`

6. **Common mistakes**
- Running the cross-encoder on every chunk in the library. It is too slow for that. It only sees the fused shortlist.
- Loading the model at API startup. It loads on the first real question. Tests pass `score_pairs` and never load it.
- Keeping the fusion order after reranking. `rerank` replaces that order.

7. **Check yourself**
1. *Why not rerank every chunk?*
2. *What score ends up on a citation?*
3. *How do tests avoid downloading the cross-encoder?*

---
**Answers:**
1. Each pair is a separate model pass. The shortlist is already the candidates worth that cost.
2. The cross-encoder score, stored as `citations.relevance_score`.
3. `rerank` accepts a `score_pairs` function. Tests pass a function that returns numbers and never call `_cross_encoder_scores`.
