# Cosine similarity

1. **One-line definition**
Cosine similarity measures how much two embeddings point in the same direction. It ignores how long each arrow is.

2. **Why it exists** (the problem it solves)
Two passages can be about the same rule and still produce vectors with different magnitudes. Comparing direction answers "are these about the same thing?" better than comparing raw distance.

3. **Analogy**
Two people pointing at the same building are "similar" even if one arm is longer. Cosine looks at the angle between the arms, not the arm length.

4. **How it works** (step by step)
- **Step 1:** Take the dot product of the two vectors: multiply pairs of numbers and add them up.
- **Step 2:** Divide by the product of their lengths. The result is between -1 and 1. For text embeddings it is usually between 0 and 1. Closer to 1 means more similar.
- **Step 3:** If both vectors already have length 1, the division is unnecessary and cosine similarity is just the dot product. FinScope normalizes embeddings at creation time for that reason.
- **Step 4:** Phase 2 stores the vectors. Phase 3 will ask Postgres, via pgvector, for the chunks whose vectors are closest to a question. No similarity query runs yet, and there is no HNSW index yet.

5. **Where it is in FinScope** (file + function)
- Normalization that makes cosine a dot product: `embed_texts` in [backend/app/rag/embeddings.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/embeddings.py)
- The stored column: `DocumentChunk.embedding` in [backend/app/models/document.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/models/document.py)
- Nothing in Phase 2 computes a similarity score. That search arrives with retrieval in Phase 3.

6. **Common mistakes**
- Comparing vectors from two different models. Their directions do not share a space.
- Forgetting normalization and then treating a dot product as cosine. A longer vector would look "more similar" only because it is longer.
- Building a vector index before any query exists. The index does not change what is stored. It only speeds up search.

7. **Check yourself**
1. *What does a cosine of 1 mean?*
2. *Why can Phase 2 skip the HNSW index?*
3. *Why does `embed_texts` normalize vectors?*

---
**Answers:**
1. The two vectors point the same way. For normalized text embeddings, that is the strongest match this measure can give.
2. Nothing searches by similarity yet. A sequential scan is enough until Phase 3, and the index can be added in the migration that introduces that query.
3. So a later cosine comparison does not have to divide by vector length. Equal-length vectors make the dot product the cosine.
