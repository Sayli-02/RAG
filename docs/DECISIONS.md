# Decisions Log

## Template
### [Date] Decision title
- **Options considered:**
- **Chosen:**
- **Why:**
- **Trade-offs:**

---

### [2026-11-14] Vector Embedding Model Dimensionality
- **Options considered:** 
  - 384 dimensions (`sentence-transformers/all-MiniLM-L6-v2` or `BAAI/bge-small-en-v1.5`)
  - 768 dimensions (`BAAI/bge-base-en-v1.5` or `nomic-embed-text`)
  - 1536 dimensions (OpenAI `text-embedding-3-small`)
- **Chosen:** 384 dimensions (`Vector(384)`).
- **Why:** Fits Hugging Face local open-source embedding models, executes fast on CPU without GPU overhead, and keeps memory footprint low while preserving strong retrieval performance for dense regulatory text.
- **Trade-offs:** Larger 768-dim models may capture slightly higher semantic granularity for subtle regulatory phrasing, but cost more memory and inference latency.

### [2026-11-14] Database Driver and Connection Handling
- **Options considered:**
  - `psycopg` (v3)
  - `psycopg2-binary` (v2)
  - `asyncpg` (fully async)
- **Chosen:** `psycopg2-binary` with connection dialect `postgresql+psycopg2://` and a 3-second connect timeout (`connect_timeout: 3`).
- **Why:** Mature, stable binary wheels with zero build requirements, straightforward synchronous session integration with FastAPI dependency injection (`get_db`), and fast failure detection during health checks.
- **Trade-offs:** Sync database access uses threadpools in FastAPI rather than non-blocking event loops; can be updated to `asyncpg` if high concurrent socket throughput is needed later.

### [2026-11-14] Health Check Fault Tolerance
- **Options considered:**
  - Throw 503 Service Unavailable / unhandled exception if DB connection fails.
  - Return HTTP 200 with degraded health status (`status: "degraded"`, `database: "disconnected"`).
- **Chosen:** Return HTTP 200 with detailed status breakdown (`status: "degraded"`, `database: "disconnected"`).
- **Why:** Allows monitoring agents and load balancers to distinguish between total service crashes and database reachability issues without breaking API responses.
- **Trade-offs:** Monitoring dashboards must inspect response JSON instead of relying strictly on HTTP status codes.

---

### [2026-11-14] Vector Embedding Model Dimensionality
- **Options considered:** 
  - 384 dimensions (`sentence-transformers/all-MiniLM-L6-v2` or `BAAI/bge-small-en-v1.5`)
  - 768 dimensions (`BAAI/bge-base-en-v1.5` or `nomic-embed-text`)
  - 1536 dimensions (OpenAI `text-embedding-3-small`)
- **Chosen:** 384 dimensions (`Vector(384)`).
- **Why:** Fits Hugging Face local open-source embedding models, executes fast on CPU without GPU overhead, and keeps memory footprint low while preserving strong retrieval performance for dense regulatory text.
- **Trade-offs:** Larger 768-dim models may capture slightly higher semantic granularity for subtle regulatory phrasing, but cost more memory and inference latency.

### [2026-11-14] Database Driver and Connection Handling
- **Options considered:**
  - `psycopg` (v3)
  - `psycopg2-binary` (v2)
  - `asyncpg` (fully async)
- **Chosen:** `psycopg2-binary` with connection dialect `postgresql+psycopg2://` and a 3-second connect timeout (`connect_timeout: 3`).
- **Why:** Mature, stable binary wheels with zero build requirements, straightforward synchronous session integration with FastAPI dependency injection (`get_db`), and fast failure detection during health checks.
- **Trade-offs:** Sync database access uses threadpools in FastAPI rather than non-blocking event loops; can be updated to `asyncpg` if high concurrent socket throughput is needed later.

### [2026-11-14] Health Check Fault Tolerance
- **Options considered:**
  - Throw 503 Service Unavailable / unhandled exception if DB connection fails.
  - Return HTTP 200 with degraded health status (`status: "degraded"`, `database: "disconnected"`).
- **Chosen:** Return HTTP 200 with detailed status breakdown (`status: "degraded"`, `database: "disconnected"`).
- **Why:** Allows monitoring agents and load balancers to distinguish between total service crashes and database reachability issues without breaking API responses.
- **Trade-offs:** Monitoring dashboards must inspect response JSON instead of relying strictly on HTTP status codes.
### [2026-11-22] Phase 1 authentication mechanics
- **Options considered:**
  - Password hash: bcrypt, or argon2.
  - Token library: PyJWT, or python-jose.
  - Login body: OAuth2 form (`username` = email), or JSON `{email, password}`.
  - Session: one 60-minute access token, or access token plus refresh token.
- **Chosen:** bcrypt, PyJWT, HS256, OAuth2 password form, one access token that expires in 60 minutes. Secret is `JWT_SECRET_KEY` in `.env`, with no default in code.
- **Why:** bcrypt and PyJWT cover the spec with two small libraries. The OAuth2 form is what Swagger UI's Authorize button already sends, and the phase is done when register and login work there. A refresh token would need storage and another endpoint the spec does not ask for.
- **Trade-offs:** The login field is called `username` even though it is an email. Argon2 is stronger against GPU guessing. There is no silent renewal: after 60 minutes the client must log in again. bcrypt rejects passwords longer than 72 bytes, so register does too.


### [2026-11-22] Phase 2 ingestion
- **Options considered:**
  - Document ownership: add `uploaded_by`, or leave documents visible to every logged-in user.
  - When to index: FastAPI background task, or finish indexing inside the upload request.
  - Vector index: add HNSW now, or wait until similarity search exists.
  - Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (384), which matches the column chosen in Phase 0.
- **Chosen:** `uploaded_by` is required. Upload returns while status is `processing` and a background task indexes the file. No HNSW index yet. Chunks stay inside one page, about 1000 characters, with 150 characters of overlap. Model is MiniLM L6, vectors normalized for cosine.
- **Why:** Ownership is the isolation rule in the spec, and it is cheaper to add before any PDFs exist. Background indexing matches the requirement that upload does not block. The index does not change what is stored, and nothing queries by similarity until Phase 3. Page-sized chunks keep a single page number on each citation.
- **Trade-offs:** The upload response is `processing`, so the client must read the document again to see `indexed` or `failed`. A long PDF still occupies this API process. A larger embedding model would need a new column width. Headers are removed only when the same short line is on every non-empty page, and only when there are at least three pages.

### [2026-11-22] Phase 3 answer pipeline
- **Options considered:**
  - Gemini client: `google-genai` one call, or LangChain around the same call.
  - Query rewrite: send the question as typed, or spend a second Gemini call to rewrite it.
  - Weak retrieval: call Gemini whenever at least one chunk came back, or skip Gemini below a score cutoff.
  - Vector index: add HNSW cosine now that search exists.
- **Chosen:** Direct `google-genai` with `GEMINI_API_KEY` in `.env` and model `gemini-2.5-flash`. No query rewrite. Gemini is called when hybrid search returns any chunk; the prompt tells it to refuse otherwise. HNSW index `idx_document_chunks_embedding_hnsw` uses `vector_cosine_ops`. Fusion is reciprocal rank fusion (k = 60). Reranker is `cross-encoder/ms-marco-MiniLM-L-6-v2`, keeping 4 chunks. Citations are the `[n]` markers in the answer.
- **Why:** One prompt does not need a chain framework. A rewrite call is another failure point. A score cutoff would be a guess. The index matches the cosine distance the query uses. Rank fusion avoids adding cosine and BM25 scores that are not on the same scale.
- **Trade-offs:** An answer that forgets its `[n]` markers is stored with no citations, so an unsupported sentence is visible but uncited. BM25 loads the user's indexed chunks into memory. LangChain remains unused until a later phase needs a multi-step chain.

### [2026-11-22] Phase 4 frontend shell
- **Options considered:**
  - Look: the revised light teal chat (approved mock), the paper-and-oxblood memo, or the split circular with a yellow highlight.
  - API calls during development: a Vite proxy to port 8000, or an absolute `http://127.0.0.1:8000` base URL.
- **Chosen:** The revised teal Assistant screen. Documents and login use the same shell. Vite proxies API paths and lets HTML navigations stay in React.
- **Why:** That mock is the one that was approved. A proxy keeps the token on the same origin as the app, so the browser does not need a separate CORS setup for local development.
- **Trade-offs:** Dashboard, comparison, compliance, research, and settings are not in this phase. The library is a list, not a second visual mock. Log out, upload, delete, and ask still need a running API before they can be clicked end to end.

### [2026-11-22] Phase 5 comparison
- **Options considered:**
  - What to compare: the latest version of two documents the user already uploaded, or a new "upload version 2" flow on one document.
  - Summary: Gemini JSON when the key is set, or always the count sentence.
- **Chosen:** Compare the latest indexed version of two documents the user owns. Pair chunks by text ratio and embedding cosine. Gemini writes `{summary, affected_requirements}` when `GEMINI_API_KEY` is set. Otherwise the summary is "N added, N removed, N modified."
- **Why:** Each upload already has version 1.0, so two documents are enough to show a change report. The count sentence keeps the feature working before a Gemini key exists, and a bad JSON reply cannot wipe the diff.
- **Trade-offs:** There is no button to attach a second PDF to the same document. A greedy pairing can miss the best global match. Compliance extraction is still a later slice of Phase 5.

### [2026-11-22] Phase 6 cross-document search
- **Options considered:**
  - One hybrid search over the documents the user picked, then one answer.
  - One search per document, then a second Gemini call that compares those answers.
- **Chosen:** One hybrid search limited with `document_ids`, then the same answer path as the assistant. The question text is stored in `saved_queries`.
- **Why:** The retrieval pipeline already exists. Restricting it keeps one model call and the same citation rules.
- **Trade-offs:** A point that appears in only one of the selected documents can be crowded out of the top chunks. Past questions do not remember which documents were ticked. The per-document-then-compare approach is still available if this turns out too coarse.

### [2026-11-22] Compliance checklist and retrieval scores
- **Options considered:**
  - Checklist text: Gemini JSON when the key is set, or only sentences that contain must, shall, or required.
  - Answer quality: the RAGAS library as a model judge, or the share of answer words that appear in the retrieved text.
  - Dashboard charts: a chart library, or counts and lists.
- **Chosen:** Gemini JSON with the sentence scanner as the fallback. Recall@k and mean reciprocal rank for vector, BM25, and hybrid search on `sample_questions.json`. Faithfulness is word overlap, stored only when the Gemini key is set. The dashboard shows counts and lists.
- **Why:** The checklist has to work before a key exists, and a bad JSON reply must not drop the obligations already in the text. RAGAS would add a large dependency and another model call that the tests would have to fake. The sample questions give the three retrievers the same labeled pages so the scores can be compared.
- **Trade-offs:** Word overlap can score a wrong sentence highly when it reuses the retrieved words. The sample questions expect pages 3, 5, and 2, so they do not measure a corpus that uses other pages. Chunk-size experiments would mean re-indexing and are not in this run.

### [2026-11-22] Phase 7 hosts
- **Options considered:**
  - Database: Render Postgres, Neon, or Supabase.
  - Website: Vercel.
  - API: Vercel serverless functions, or a long-running host (Render or Railway).
- **Chosen:** Supabase for Postgres, Vercel for the React app, and either Render or Railway for the API. The Render file is `render.yaml`. The Railway file is `backend/railway.toml`. Both run the same start command.
- **Why:** Supabase already provides Postgres and pgvector. Vercel fits a static Vite build. The API loads embedding models, writes PDFs to disk, and indexes after the response, which needs a process that stays up. The browser sends the JWT on the Authorization header, so CORS does not need cookies.
- **Trade-offs:** Uploaded PDFs disappear when the API restarts. Chunks in Supabase remain. Render and Railway free instances sleep when idle, so the first request is slow. The site is not live until those three accounts exist.
