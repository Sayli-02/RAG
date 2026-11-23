# Progress Log (newest at the bottom)

## Entry template
### [Date] Phase X: short title
- **Goal:**
- **What was done:** (files created/changed)
- **How to run/test it:**
- **Result:** (worked / partly / broken)
- **Concepts introduced:** (links to docs/learn/ notes)
- **Problems & fixes:**
- **Next step:**

---

### [2026-11-14] Phase 0: FastAPI Skeleton & Database Infrastructure
- **Goal:** Set up backend application skeleton, Docker Compose configuration for PostgreSQL + pgvector, full SQLAlchemy models from spec, baseline Alembic migration, `/health` endpoint, and unit tests.
- **What was done:**
  - Created backend folder layout: `backend/app/core/`, `backend/app/database/`, `backend/app/models/`, `backend/app/schemas/`, `backend/tests/`.
  - Created `docker-compose.yml` configuring `pgvector/pgvector:pg16` service.
  - Created `backend/requirements.txt`, `backend/.env.example`, and `backend/.env`.
  - Implemented application configuration in [backend/app/core/config.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/core/config.py).
  - Implemented database engine, session factory, and `get_db` generator dependency in [backend/app/database/session.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/database/session.py).
  - Implemented SQLAlchemy 2.0 ORM models for all tables specified in SPEC.md: `User`, `Document`, `DocumentVersion`, `DocumentChunk` (with `Vector(384)`), `Conversation`, `Message`, `Citation`, `ComparisonReport`, `ComplianceChecklist`, `ComplianceRequirement`, `SavedQuery`, and `EvaluationRun` across `backend/app/models/`.
  - Initialized Alembic and generated baseline migration script [backend/alembic/versions/0001_initial_schema.py](file:///c:/Users/Sayli/Downloads/RAG/backend/alembic/versions/0001_initial_schema.py) with `CREATE EXTENSION IF NOT EXISTS vector;` and table/index definitions.
  - Implemented `/health` endpoint in [backend/app/main.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/main.py).
  - Implemented unit tests in [backend/tests/test_health.py](file:///c:/Users/Sayli/Downloads/RAG/backend/tests/test_health.py) and [backend/tests/test_models.py](file:///c:/Users/Sayli/Downloads/RAG/backend/tests/test_models.py).
  - Authored concept notes in `docs/learn/` (REST APIs, FastAPI, ORM, Alembic migrations, Docker, pgvector).
- **How to run/test it:**
  - Run unit tests: `.\backend\.venv\Scripts\pytest.exe backend\tests -v`
  - Generate offline SQL schema: `cd backend; ..\backend\.venv\Scripts\alembic.exe upgrade head --sql`
  - Start the API server: `.\backend\.venv\Scripts\uvicorn.exe app.main:app --app-dir backend --reload`
- **Result:** worked (all 5 unit tests passing, offline Alembic SQL generation verified).
- **Concepts introduced:**
  - [REST APIs](learn/01-rest-apis.md)
  - [FastAPI](learn/02-fastapi.md)
  - [ORM and SQLAlchemy](learn/03-orm.md)
  - [Database Migrations and Alembic](learn/04-migrations.md)
  - [Docker and Docker Compose](learn/05-docker.md)
  - [Vector Extensions and pgvector](learn/06-vector-extensions.md)
- **Problems & fixes:**
  - SQLAlchemy 2.0+ default dialect: `postgresql://` defaulted to `psycopg3` which threw `ModuleNotFoundError: No module named 'psycopg'`. Updated URL to `postgresql+psycopg2://` matching `psycopg2-binary`.
  - Slow connect timeout: Added `connect_timeout: 3` so database health checks fail fast when Postgres is not running.
- **Next step:** Phase 1: User Registration, Login, and JWT Authentication.

---

### [2026-11-14] Phase 0: FastAPI Skeleton & Database Infrastructure
- **Goal:** Set up backend application skeleton, Docker Compose configuration for PostgreSQL + pgvector, full SQLAlchemy models from spec, baseline Alembic migration, `/health` endpoint, and unit tests.
- **What was done:**
  - Created backend folder layout: `backend/app/core/`, `backend/app/database/`, `backend/app/models/`, `backend/app/schemas/`, `backend/tests/`.
  - Created `docker-compose.yml` configuring `pgvector/pgvector:pg16` service.
  - Created `backend/requirements.txt`, `backend/.env.example`, and `backend/.env`.
  - Implemented application configuration in [backend/app/core/config.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/core/config.py).
  - Implemented database engine, session factory, and `get_db` generator dependency in [backend/app/database/session.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/database/session.py).
  - Implemented SQLAlchemy 2.0 ORM models for all tables specified in SPEC.md: `User`, `Document`, `DocumentVersion`, `DocumentChunk` (with `Vector(384)`), `Conversation`, `Message`, `Citation`, `ComparisonReport`, `ComplianceChecklist`, `ComplianceRequirement`, `SavedQuery`, and `EvaluationRun` across `backend/app/models/`.
  - Initialized Alembic and generated baseline migration script [backend/alembic/versions/0001_initial_schema.py](file:///c:/Users/Sayli/Downloads/RAG/backend/alembic/versions/0001_initial_schema.py) with `CREATE EXTENSION IF NOT EXISTS vector;` and table/index definitions.
  - Implemented `/health` endpoint in [backend/app/main.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/main.py).
  - Implemented unit tests in [backend/tests/test_health.py](file:///c:/Users/Sayli/Downloads/RAG/backend/tests/test_health.py) and [backend/tests/test_models.py](file:///c:/Users/Sayli/Downloads/RAG/backend/tests/test_models.py).
  - Authored concept notes in `docs/learn/` (REST APIs, FastAPI, ORM, Alembic migrations, Docker, pgvector).
- **How to run/test it:**
  - Run unit tests: `.\backend\.venv\Scripts\pytest.exe backend\tests -v`
  - Generate offline SQL schema: `cd backend; ..\backend\.venv\Scripts\alembic.exe upgrade head --sql`
  - Start the API server: `.\backend\.venv\Scripts\uvicorn.exe app.main:app --app-dir backend --reload`
- **Result:** worked (all 5 unit tests passing, offline Alembic SQL generation verified).
- **Concepts introduced:**
  - [REST APIs](learn/01-rest-apis.md)
  - [FastAPI](learn/02-fastapi.md)
  - [ORM and SQLAlchemy](learn/03-orm.md)
  - [Database Migrations and Alembic](learn/04-migrations.md)
  - [Docker and Docker Compose](learn/05-docker.md)
  - [Vector Extensions and pgvector](learn/06-vector-extensions.md)
- **Problems & fixes:**
  - SQLAlchemy 2.0+ default dialect: `postgresql://` defaulted to `psycopg3` which threw `ModuleNotFoundError: No module named 'psycopg'`. Updated URL to `postgresql+psycopg2://` matching `psycopg2-binary`.
  - Slow connect timeout: Added `connect_timeout: 3` so database health checks fail fast when Postgres is not running.
- **Next step:** Phase 1: User Registration, Login, and JWT Authentication.

---

### [2026-11-22] Phase 1: JWT authentication
- **Goal:** Register, login, and `/auth/me` with hashed passwords and an expiring JWT. Done when register and login work from Swagger UI.
- **What was done:**
  - Added `JWT_SECRET_KEY` and `JWT_EXPIRE_MINUTES` to backend/app/core/config.py, backend/.env, and backend/.env.example. Settings now load backend/.env by absolute path.
  - Password hashing and JWT sign/verify in backend/app/core/security.py.
  - Register, login, and current-user logic in backend/app/services/auth_service.py and backend/app/api/auth.py.
  - `get_current_user` in backend/app/core/dependencies.py.
  - Public schemas in backend/app/schemas/auth.py.
  - Tests in backend/tests/test_security.py and backend/tests/test_auth.py.
- **How to run/test it:**
  - Tests: `.\backend\.venv\Scripts\pytest.exe backend\tests -v`
  - API: `.\backend\.venv\Scripts\uvicorn.exe app.main:app --app-dir backend --reload`, then open `http://127.0.0.1:8000/docs`
  - In Swagger: POST `/auth/register` with JSON, POST `/auth/login` with username = email, click Authorize, then GET `/auth/me`.
- **Result:** worked (17 unit tests passing). Swagger was not clicked in a browser this session.
- **Concepts introduced:**
  - [Password hashing](learn/07-password-hashing.md)
  - [JWT](learn/08-jwt.md)
  - [Authentication vs authorization](learn/09-authentication-vs-authorization.md)
- **Problems & fixes:**
  - Auth tests used SQLite `:memory:`. Each new connection is an empty database, so queries reported `no such table: users`. `StaticPool` keeps one connection for the whole test.
- **Next step:** Phase 2: PDF upload, PyMuPDF extraction, cleaning, chunking, embeddings, and pgvector storage.


---

### [2026-11-22] Phase 2: PDF ingestion
- **Goal:** Upload a PDF, extract text with PyMuPDF, clean it, chunk it by page, embed the chunks, and store them with page numbers.
- **What was done:**
  - Migration `backend/alembic/versions/0002_document_owner.py` adds `documents.uploaded_by` and `documents.error_message`.
  - Extraction, cleaning, chunking, and embeddings in `backend/app/rag/`.
  - `POST /documents/upload`, `GET /documents`, `GET /documents/{id}`, `DELETE /documents/{id}` in `backend/app/api/documents.py`.
  - Tests in `backend/tests/test_ingestion.py` and `backend/tests/test_documents.py`.
- **How to run/test it:**
  - Tests: `pytest backend/tests -v` with the backend virtualenv.
  - Apply the migration before a real upload: from `backend/`, run `alembic upgrade head`.
  - Install the embedding library once: `pip install -r requirements.txt` inside `backend/`.
  - Upload from Swagger at `http://127.0.0.1:8000/docs` with a Bearer token. `username` on login is the email. Then poll `GET /documents/{id}` until status is `indexed`.
- **Result:** worked (27 unit tests passing). A real RBI PDF was not uploaded; that needs Postgres, the new migration, and the MiniLM download.
- **Concepts introduced:**
  - [PDF parsing](learn/10-pdf-parsing.md)
  - [Text cleaning](learn/11-text-cleaning.md)
  - [Chunking](learn/12-chunking.md)
  - [Embeddings](learn/13-embeddings.md)
  - [Cosine similarity](learn/14-cosine-similarity.md)
- **Problems & fixes:**
  - PyMuPDF 2.x pulls ONNX and marks `fitz` as deprecated. Requirements pin `pymupdf>=1.24.0,<2` so install stays the single 1.x wheel.
- **Next step:** Phase 3: hybrid retrieval, reranking, and Gemini answers with citations.

---

### [2026-11-22] Phase 3: Grounded answers
- **Goal:** A question returns an answer grounded in the user's indexed chunks, with page citations.
- **What was done:**
  - Hybrid retrieval and reciprocal rank fusion in `backend/app/rag/retrieval.py`.
  - Cross-encoder rerank in `backend/app/rag/reranking.py`.
  - Grounded Gemini prompt and citation markers in `backend/app/rag/generation.py`.
  - `POST /assistant/ask`, `GET /assistant/conversations`, and `GET /assistant/conversations/{id}` in `backend/app/api/assistant.py`.
  - HNSW cosine index in `backend/alembic/versions/0003_hnsw_index.py`.
  - Tests in `backend/tests/test_retrieval.py` and `backend/tests/test_assistant.py`.
- **How to run/test it:**
  - Tests: `pytest backend/tests -v` with the backend virtualenv.
  - From `backend/`, run `alembic upgrade head`, set `GEMINI_API_KEY` in `.env`, install `requirements.txt`, then ask from Swagger `POST /assistant/ask` after a document is `indexed`.
- **Result:** worked (35 unit tests passing). A live Gemini call was not made.
- **Concepts introduced:**
  - [Semantic vs keyword search](learn/15-semantic-vs-keyword.md)
  - [BM25](learn/16-bm25.md)
  - [Hybrid search](learn/17-hybrid-search.md)
  - [Reranking](learn/18-reranking.md)
  - [RAG](learn/19-rag.md)
  - [Prompt grounding](learn/20-prompt-grounding.md)
  - [Citations](learn/21-citations.md)
  - [Hallucination](learn/22-hallucination.md)
- **Problems & fixes:** none during the test run.
- **Next step:** Phase 4: frontend login, document library, chat UI, and citation cards.

---

### [2026-11-22] Phase 4: Frontend
- **Goal:** A logged-in user can upload a PDF and ask a question, with citation cards, in the light teal workspace.
- **What was done:**
  - Vite + React + Tailwind app in `frontend/`.
  - Login and register in `frontend/src/pages/Login.jsx`.
  - Document list, upload, search, delete, and detail polling in `frontend/src/pages/Documents.jsx` and `DocumentDetail.jsx`.
  - Assistant chat and `CitationCard` in `frontend/src/pages/Assistant.jsx`.
  - JWT interceptor in `frontend/src/services/api.js`. Dev proxy in `frontend/vite.config.js` leaves HTML navigations in React.
- **How to run/test it:**
  - From `frontend/`: `npm install` then `npm run dev`. Open `http://localhost:5173`.
  - The API must be on port 8000. From `backend/`: start Postgres, `alembic upgrade head`, then uvicorn.
- **Result:** partly. The production build succeeds. In the browser, account toggle, short-password check, login error when the API is down, and redirects from `/documents` and `/assistant` to `/login` all worked. Upload, delete, ask, and log out were not clicked against a live API because Docker Desktop was not running.
- **Concepts introduced:**
  - [React state and hooks](learn/23-react-state.md)
  - [API integration](learn/24-api-integration.md)
  - [Component design](learn/25-component-design.md)
- **Problems & fixes:**
  - Vite proxied the browser's GET of `/documents` to FastAPI, so the page was blank. The proxy now skips requests that accept HTML.
- **Next step:** Phase 5: regulatory comparison, then the compliance extractor.

---

### [2026-11-22] Phase 5: Document comparison
- **Goal:** Compare the latest version of two indexed documents and show added, removed, and modified chunks.
- **What was done:**
  - Pairing and labels in `backend/app/rag/diffing.py` (`build_diff`, `summarize_diff`).
  - `POST /comparison/compare`, `GET /comparison/reports`, and `GET /comparison/reports/{id}`.
  - Compare screen in `frontend/src/pages/Compare.jsx`, sidebar link, and Vite proxy for `/comparison`.
  - Tests in `backend/tests/test_comparison.py`.
- **How to run/test it:**
  - From `backend/`: `.\.venv\Scripts\pytest.exe tests\test_comparison.py -q`
  - With the API running, open Compare, pick two indexed documents, and press Compare.
- **Result:** worked (comparison tests passing). The screen was not clicked against a live API because Postgres was not running.
- **Concepts introduced:**
  - [Text diffing](learn/26-text-diffing.md)
  - [Semantic diffing](learn/27-semantic-diffing.md)
  - [Structured LLM output](learn/28-structured-llm-output.md)
- **Problems & fixes:** none in the unit tests.
- **Next step:** Phase 5 compliance extractor: checklist, review status, and CSV export.

---

### [2026-11-22] Project README
- **Goal:** One README at the repo root that describes FinScope as it exists after the comparison slice.
- **What was done:** Wrote `README.md`. Replaced the Vite template text in `frontend/README.md` with a pointer to that file.
- **How to run/test it:** Read `README.md` from the repo root.
- **Result:** worked.
- **Concepts introduced:** none.
- **Problems & fixes:** none.
- **Next step:** Phase 5 compliance extractor: checklist, review status, and CSV export.

---

### [2026-11-22] Phase 6: Cross-document research
- **Goal:** Ask one question across two or more indexed documents the user selects.
- **What was done:**
  - `document_ids` on vector search, BM25, and `hybrid_search`, plus `keep_selected` in `backend/app/rag/retrieval.py`.
  - `POST /research/cross-document` and `GET /research/queries`.
  - Research screen in `frontend/src/pages/Research.jsx`, sidebar link, and Vite proxy for `/research`.
  - Tests in `backend/tests/test_research.py`.
- **How to run/test it:**
  - From `backend/`: `.\.venv\Scripts\pytest.exe tests\test_research.py -q`
  - With the API running, open Research, tick two indexed documents, and ask.
- **Result:** worked (research tests passing). The screen was not clicked against a live API because Postgres was not running.
- **Concepts introduced:**
  - [Multi-document retrieval](learn/29-multi-document-retrieval.md)
- **Problems & fixes:** none in the unit tests.
- **Next step:** Phase 6 analytics summary, then retrieval evaluation. The Phase 5 compliance extractor is still unbuilt.

---

### [2026-11-22] Phase 5 compliance and Phase 6 dashboard
- **Goal:** Finish the compliance checklist, the analytics summary, and a stored retrieval score.
- **What was done:**
  - Requirement extraction in `backend/app/rag/requirements.py` and `POST /compliance/extract`, review `PATCH`, and CSV export.
  - `GET /analytics/summary` and the Dashboard page.
  - Recall@k, mean reciprocal rank, and word-overlap faithfulness in `backend/app/rag/evaluation.py`, scored from `sample_questions.json`.
  - Compliance and Dashboard screens, sidebar links, and Vite proxies.
  - Tests in `backend/tests/test_phase_remaining.py`.
- **How to run/test it:**
  - From `backend/`: `.\.venv\Scripts\pytest.exe tests\test_phase_remaining.py -q`
  - With the API running, open Compliance and Dashboard.
- **Result:** worked (49 tests passing). The new screens were not clicked against a live API because Postgres was not running.
- **Concepts introduced:**
  - [Requirement extraction](learn/30-requirement-extraction.md)
  - [Recall and mean reciprocal rank](learn/31-recall-and-mrr.md)
  - [Faithfulness](learn/32-faithfulness.md)
- **Problems & fixes:** none in the unit tests.
- **Next step:** Phase 7 deployment.

---

### [2026-11-22] Phase 7: Deploy config
- **Goal:** Prepare the repo for Supabase, Vercel, and a long-running API on Render or Railway.
- **What was done:**
  - `CORS_ORIGINS` in `backend/app/core/config.py` and the CORS middleware in `backend/app/main.py`.
  - `VITE_API_URL` as the Axios base URL in `frontend/src/services/api.js`.
  - `frontend/vercel.json`, `render.yaml`, and `backend/railway.toml`.
  - Deploy steps in `README.md`.
- **How to run/test it:**
  - From `backend/`: `.\.venv\Scripts\pytest.exe tests\test_cors.py -q`
  - Local `npm run dev` still uses the Vite proxy when `VITE_API_URL` is empty.
- **Result:** worked (config and the origin test). The three hosts were not created, so the app is not live.
- **Concepts introduced:**
  - [Split deployment](learn/33-split-deployment.md)
- **Problems & fixes:** none in the unit test.
- **Next step:** Create Supabase, Render or Railway, and Vercel, then set the env vars listed in the README.
