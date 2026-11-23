# FinScope

FinScope is a regulatory research app for RBI, SEBI, and NPCI documents. You upload a PDF, the app indexes it, and you can ask questions that stay tied to a page, compare two indexed documents, or ask one question across the files you select.

Answers are research aids. They are not legal advice. If the indexed text does not support an answer, the assistant says so instead of guessing.

The full product spec is [docs/SPEC.md](docs/SPEC.md). What has actually been built is below. Concept notes for each idea are in [docs/learn/](docs/learn/00-roadmap.md).

## What works now

| Phase | What you can do |
|---|---|
| 0 | FastAPI app, Postgres with pgvector, SQLAlchemy models, Alembic, `GET /health` |
| 1 | Register, log in, and call protected routes with a JWT |
| 2 | Upload a PDF, extract and chunk the text, store embeddings, list and delete your documents |
| 3 | Ask a question. Hybrid search, reranking, and Gemini produce an answer with citations |
| 4 | Web app: login, document library, assistant chat, citation cards |
| 5 | Compare two indexed documents, and extract a compliance checklist you can review and export as CSV |
| 6 | Ask across selected documents, see library counts on the dashboard, and score retrieval on three sample questions |

The deploy files for Phase 7 are in the repo. The site is not live until you create Supabase, Render or Railway, and Vercel. URL import, a second version on the same document, OCR, refresh tokens, and role checks are not in the code.

A few spec items are not in the code yet: importing a PDF from a URL, uploading a second version onto the same document, OCR, refresh tokens, and role checks. LangChain is named in the spec and is not used. The question is embedded as typed, with no rewrite step.

## Stack

- API: Python, FastAPI, SQLAlchemy, Alembic, Pydantic
- Data: PostgreSQL 16 with pgvector
- Documents: PyMuPDF, page-bounded chunks, `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- Search: pgvector cosine, BM25, reciprocal rank fusion, `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Answers and comparison summaries: Gemini (`gemini-2.5-flash`) through `google-genai`
- Web: React, Vite, Tailwind, React Router, Axios

## Run it

You need Docker Desktop, Python 3.11+, and Node.js. Commands below are for PowerShell from the repo root.

1. Start the database.

```powershell
docker compose up -d
```

2. Create the API environment file and set a real JWT secret. Leave `GEMINI_API_KEY` empty until you want model-written answers or comparison summaries.

```powershell
Copy-Item backend\.env.example backend\.env
```

Generate a secret and paste it into `JWT_SECRET_KEY`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

`backend/.env.example` lists the other settings. The database defaults match `docker-compose.yml` (`postgres` / `postgres`, database `finscope`, port 5432).

3. Install the API and create the tables.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

Swagger is at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). The first upload downloads the embedding model. The first question downloads the reranker.

4. Start the web app in a second terminal.

```powershell
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The Vite dev server proxies `/auth`, `/documents`, `/assistant`, `/comparison`, `/research`, `/compliance`, `/analytics`, `/evaluation`, and `/health` to port 8000. Browser page loads stay in React.

## Using the app

1. Create an account. Passwords must be at least 8 characters and at most 72 bytes.
2. Upload a text PDF (max 20 MB). Authority is `RBI`, `SEBI`, `NPCI`, or `OTHER`. The upload returns while status is `processing`. Open the document and wait until it is `indexed`.
3. Ask a question in Assistant. Citations show the document, authority, page, section when known, and an excerpt. A weak retrieval returns: `The documents do not contain enough information to answer this.`
4. On Compare, pick two indexed documents. The report lists removed, modified, and added chunks. Saved reports stay on that page.
5. On Research, tick at least two indexed documents and ask one question. The search uses only those files. Saved questions fill the box again. You pick the documents each time.
6. On Compliance, extract a checklist from one indexed document, set each row to pending, reviewed, or not applicable, and export CSV.
7. On Dashboard, read counts for documents, reviews, recent comparisons, and frequent questions. Run scores to compare vector, BM25, and hybrid search on the three sample questions.

Without `GEMINI_API_KEY`, asking a question returns an error from the API, a comparison summary is the count sentence (`N added, N removed, N modified.`), and a checklist is built from sentences that say must, shall, or required. With the key set, Gemini writes the answer, the comparison summary, and the checklist JSON. A bad JSON reply falls back to the sentence scanner or the count sentence. Faithfulness on the dashboard runs only when the key is set.

Each user only sees their own documents, chats, and reports.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Process is up. Database down still returns 200 with a degraded status |
| POST | `/auth/register` | Create an account |
| POST | `/auth/login` | OAuth2 form. The username field is the email. Returns a 60-minute access token |
| GET | `/auth/me` | Current user |
| POST | `/documents/upload` | Multipart PDF upload. Indexing continues after the response |
| GET | `/documents` | Your documents. Filters: `status`, `authority`, `q` |
| GET | `/documents/{id}` | One document |
| DELETE | `/documents/{id}` | Delete a document you own |
| POST | `/assistant/ask` | Ask a question |
| GET | `/assistant/conversations` | Your chats |
| GET | `/assistant/conversations/{id}` | One chat with citations |
| POST | `/comparison/compare` | Body: `document_a_id`, `document_b_id` |
| GET | `/comparison/reports` | Saved comparisons |
| GET | `/comparison/reports/{id}` | One comparison |
| POST | `/research/cross-document` | Body: `question`, `document_ids` (at least two) |
| GET | `/research/queries` | Saved research questions |
| POST | `/compliance/extract` | Body: `document_id`. Builds a checklist |
| GET | `/compliance/checklists` | Your checklists |
| GET | `/compliance/checklists/{id}` | One checklist |
| GET | `/compliance/checklists/{id}/export` | CSV download |
| PATCH | `/compliance/requirements/{id}` | Body: `status`, `reviewer_notes` |
| GET | `/analytics/summary` | Counts for the current user |
| POST | `/evaluation/run` | Score the sample questions and store the run |
| GET | `/evaluation/latest` | Latest score run |

Protected routes expect `Authorization: Bearer <token>`.

## Tests

From `backend/`:

```powershell
.\.venv\Scripts\pytest.exe tests -q
```

The suite uses SQLite and fakes for embeddings, search, and Gemini. It does not need Postgres or an API key. The last full run was 50 passed.

## Layout

```text
backend/app/api/         HTTP routes
backend/app/services/    auth, documents, assistant, comparison, research, compliance, analytics, evaluation
backend/app/rag/         cleaning, chunking, embeddings, retrieval, reranking, generation, diffing, requirements, evaluation
backend/alembic/         schema migrations
frontend/src/pages/      Login, Documents, DocumentDetail, Assistant, Compare, Research, Compliance, Dashboard
docs/SPEC.md             product spec
docs/PROGRESS.md         what was finished, in order
docs/DECISIONS.md        choices and trade-offs
docs/learn/              short notes for each concept
```

## Deploy

Create three projects. Do not commit passwords or API keys.

1. **Supabase (database).** Create a project. In the SQL editor, run `create extension if not exists vector;`. In Connect, copy the **session pooler** URI (port 5432, host like `aws-0-....pooler.supabase.com`). Change the scheme from `postgresql://` to `postgresql+psycopg2://`. That value is `SQLALCHEMY_DATABASE_URI`. The transaction pooler on port 6543 is the wrong string for this app.

2. **Render or Railway (API).** Point the service at this repo with root directory `backend`. Render can use the root `render.yaml`. Railway uses `backend/railway.toml` when the service root is `backend`. Set:
   - `JWT_SECRET_KEY` to a long random string
   - `SQLALCHEMY_DATABASE_URI` to the Supabase URI from step 1
   - `CORS_ORIGINS` to the Vercel site URL, for example `https://your-app.vercel.app`
   - `GEMINI_API_KEY` when you want model-written answers
   The start command runs `alembic upgrade head` and then uvicorn. Give the service at least 1 GB of RAM. The first upload downloads the embedding model. Open `https://YOUR-API/health` and confirm `database` is `connected`.

3. **Vercel (website).** Import this repo, set the project root to `frontend`, and set `VITE_API_URL` to the API origin with no trailing slash. Redeploy after any change to that variable, because Vite bakes it in at build time. `frontend/vercel.json` sends refreshes of `/documents` and the other routes back to `index.html`.

After the Vercel URL exists, add it to `CORS_ORIGINS` on the API and redeploy the API.

Uploaded PDFs live on the API machine's disk. A restart deletes the files. Chunks already stored in Supabase remain searchable.

## Known limits

- Local Postgres still comes from Docker Compose. Supabase replaces it only for the hosted API.
- A Render or Railway restart deletes uploaded PDF files. Indexed chunks stay in Supabase.
- The web screens have not all been clicked through against a live API.
- Scanned PDFs are not read. Tables and multi-column pages can extract poorly.
- Comparison pairs the latest version of two separate uploads. It does not attach a new PDF as version 2 of one document.
- BM25 loads that user's indexed chunks into memory.
- Retrieval scores use three fixed questions that expect pages 3, 5, and 2. A library that does not contain those pages scores zero. Faithfulness counts overlapping words. It does not call the RAGAS library.
- Changing chunk size and re-indexing is not part of the score run.
