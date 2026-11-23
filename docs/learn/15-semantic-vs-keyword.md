# Semantic search vs keyword search

1. **One-line definition**
Semantic search finds passages with a similar meaning. Keyword search finds passages that contain the same words.

2. **Why it exists** (the problem it solves)
A question can use different words from the circular and still mean the same thing. A question can also depend on a rare exact term, such as "NBFC", that a meaning match might rank too low.

3. **Analogy**
Semantic search is asking a librarian for "books about this idea." Keyword search is asking for "books that contain this word."

4. **How it works** (step by step)
- **Step 1:** Semantic search embeds the question with the same MiniLM model used on the chunks, then asks Postgres for the closest vectors by cosine distance.
- **Step 2:** Only chunks from this user's documents with status `indexed` are eligible.
- **Step 3:** Keyword search scores those same chunks with BM25.
- **Step 4:** Each list keeps 10 chunks. Hybrid search merges the two lists. Neither list is the final answer by itself.

5. **Where it is in FinScope** (file + function)
- Semantic: `vector_search` in [backend/app/rag/retrieval.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/retrieval.py)
- Keyword: `bm25_search` in the same file
- The distance operator is `cosine_distance`, which pgvector implements as `<=>`

6. **Common mistakes**
- Embedding the question with a different model than the chunks. The directions would not be comparable.
- Searching every user's documents. `uploaded_by` limits both queries.
- Treating cosine distance as "higher is better." Distance is lower when the meanings are closer. `vector_search` stores `1 - distance` so a higher score is a closer match.

7. **Check yourself**
1. *When does keyword search beat semantic search?*
2. *Which documents can a question see?*
3. *Why must the question use MiniLM too?*

---
**Answers:**
1. When the important part is a rare exact term that the embedding might not rank first.
2. Indexed documents uploaded by the logged-in user.
3. The chunk vectors were produced by MiniLM. A vector from another model does not live in the same space.
