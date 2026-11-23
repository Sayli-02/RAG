# Embeddings

1. **One-line definition**
An embedding is a list of numbers that stands for a piece of text, so that texts with similar meaning get similar lists.

2. **Why it exists** (the problem it solves)
Keyword search misses a passage that says "lenders must disclose the annual percentage rate" when the question says "what interest rate must be shown?". An embedding puts those two near each other even when the words differ.

3. **Analogy**
It is like placing each paragraph as a pin on a map. Paragraphs about the same rule land in the same neighborhood. Paragraphs about something else land far away.

4. **How it works** (step by step)
- **Step 1:** The model `sentence-transformers/all-MiniLM-L6-v2` reads a chunk and returns 384 numbers. That size is the `Vector(384)` column chosen in Phase 0.
- **Step 2:** The vectors are scaled to length 1 (`normalize_embeddings=True`), which is what cosine similarity expects.
- **Step 3:** `ingest_document` writes each vector into `document_chunks.embedding`.
- **Step 4:** The model is loaded on the first real ingestion. Tests pass a fake function instead, so they do not download the model.

5. **Where it is in FinScope** (file + function)
- File: [backend/app/rag/embeddings.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/embeddings.py)
- Functions: `embed_texts` and `_get_model`
- Stored by `ingest_document` in [backend/app/rag/ingestion.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/ingestion.py)

6. **Common mistakes**
- Changing the model without changing `VECTOR_DIMENSION`. A 768-dimension vector will not fit the column, and `embed_texts` raises before insert.
- Calling the model once per chunk. `embed_texts` encodes the whole list in one call.
- Importing `sentence_transformers` at startup. The import is inside `_get_model` so the API can boot without the download.

7. **Check yourself**
1. *Why 384 numbers and not "as many as the model wants"?*
2. *What does normalizing a vector do?*
3. *Why can unit tests run without the Hugging Face model on disk?*

---
**Answers:**
1. The database column was created as `vector(384)`. The list length has to match that column.
2. It makes the length of every vector 1, so a later cosine comparison is just the dot product.
3. `build_chunk_records` takes an `embed` argument. Tests pass a function that returns 384 zeros-and-an-index instead of calling `embed_texts`.
