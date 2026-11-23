# FINSCOPE
## AI-Powered Financial Regulatory Intelligence Platform

**Project Domain:** Artificial Intelligence, Machine Learning and Fintech
**Project Type:** Full-Stack AI Application
**Core Technologies:** Python, React, FastAPI, LangChain, Gemini API, Hugging Face, PostgreSQL and pgvector.

---

# 1. PROJECT OVERVIEW

FinScope is an AI-powered financial regulatory intelligence platform designed to simplify the process of understanding, searching, analyzing and comparing financial regulations.

Financial regulatory authorities such as the Reserve Bank of India (RBI), Securities and Exchange Board of India (SEBI) and National Payments Corporation of India (NPCI) regularly publish circulars, notifications, guidelines, amendments and policy documents. These documents are often lengthy, distributed across different sources and difficult to analyze manually.

FinScope addresses this problem by creating a centralized platform that uses Retrieval-Augmented Generation (RAG), Natural Language Processing (NLP), semantic search and Large Language Models (LLMs) to make regulatory information accessible and easier to understand.

Users can upload financial regulatory documents, ask questions in natural language, retrieve relevant information, compare different versions of regulations and extract structured compliance requirements.

The platform generates evidence-backed responses with references to original documents, allowing users to verify the information.

### Primary Objectives

- Centralize financial regulatory documents.
- Enable natural-language search across regulatory information.
- Generate context-aware answers using RAG.
- Provide source-level citations for AI-generated responses.
- Compare different versions of financial regulations.
- Extract and categorize regulatory requirements.
- Enable cross-document analysis.
- Evaluate retrieval accuracy and answer faithfulness.

### Guiding Principles

- **Grounded answers only:** every answer must be supported by retrieved text. If retrieval is weak, the system says so instead of guessing.
- **Verifiable:** every claim links back to a document, page and (where available) section.
- **Human in the loop:** compliance outputs are suggestions for human review, not legal advice.
- **Learning-first build:** code should be simple and readable, with each concept documented in `docs/learn/`.

---

# 2. CORE FEATURES AND FUNCTIONAL MODULES

## Module 1: Regulatory Document Intelligence

A centralized document management and processing system.

**Functionalities:**
- Upload regulatory PDFs.
- Import documents from official URLs.
- Extract text using PDF parsing.
- Extract document metadata such as title, authority, publication date and effective date.
- Categorize documents into RBI, SEBI, NPCI and other categories.
- Split documents into meaningful chunks.
- Generate embeddings.
- Store document chunks and embeddings.
- Search and filter documents.
- Track document processing status.

**Output:** A searchable financial regulatory knowledge base.

## Module 2: AI Regulatory Research Assistant

A RAG-based conversational assistant that answers questions using uploaded and indexed regulatory documents.

**Functionalities:**
- Natural-language question answering.
- Semantic search.
- Keyword-based retrieval.
- Hybrid search.
- Reranking of retrieved documents.
- Context-aware response generation.
- Conversational follow-up questions.
- Chat history.
- Source document citations.
- Page and section references.
- Handling questions with insufficient supporting information.

**Example Queries:**
- Explain RBI guidelines on digital lending.
- What are the KYC requirements mentioned in this circular?
- Summarize the important provisions of this document.
- Which documents discuss payment aggregators?
- What does the regulation mention about customer data protection?

**Output:** AI-generated answers supported by relevant regulatory documents.

## Module 3: Regulatory Change Detection

A document comparison system that identifies differences between different versions of financial regulations.

**Functionalities:**
- Upload two versions of a regulatory document.
- Identify newly added content.
- Identify removed content.
- Detect modified paragraphs.
- Compare corresponding sections.
- Generate summaries of changes.
- Identify potentially affected requirements.
- Display differences side by side.

**Output:** A structured regulatory change report showing added, modified, removed and unchanged sections, with source references.

## Module 4: Compliance Requirement Extractor

An AI-powered module that extracts regulatory requirements and converts them into structured checklists.

**Functionalities:**
- Extract requirements from regulatory documents.
- Categorize requirements.
- Identify the issuing authority.
- Map requirements to source documents.
- Generate evidence-backed checklists.
- Allow users to track review status.
- Save and export compliance checklists.

**Example Output:**

| Requirement | Source | Status |
|---|---|---|
| Requirement A | RBI Circular, Section 3 | Pending review |
| Requirement B | RBI Direction, Section 5 | Pending review |
| Requirement C | RBI Circular, Section 7 | Reviewed |

**Output:** Structured regulatory requirement checklists for human review.

## Module 5: Cross-Document Intelligence

An advanced retrieval and analysis module that retrieves information across multiple regulatory documents.

**Functionalities:**
- Retrieve information from multiple documents.
- Compare RBI and SEBI guidelines.
- Identify common regulatory themes.
- Identify differences between provisions.
- Connect related sections.
- Generate comparative summaries.
- Provide separate citations for each source.

**Example Query:**

"Compare how RBI and SEBI address customer data protection in their relevant guidelines."

**Output:** A multi-document analysis with supporting citations.

## Module 6: Research and Analytics Dashboard

A centralized dashboard for monitoring document and research activities.

**Functionalities:**
- Total documents indexed.
- Documents categorized by regulatory authority.
- Recently uploaded documents.
- Document processing status.
- Frequently researched topics.
- Saved research queries.
- Recent comparison reports.
- Compliance review progress.
- Document update history.

---

# 3. TECHNOLOGY STACK

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + Vite | User interface |
| Styling | Tailwind CSS | UI development |
| Routing | React Router | Page navigation |
| API Communication | Axios | Frontend-backend integration |
| Backend | Python + FastAPI | Application logic |
| RAG Framework | LangChain | RAG pipeline orchestration |
| LLM | Gemini API | Response generation |
| Embeddings | Hugging Face | Vector generation |
| Vector Database | pgvector | Semantic retrieval |
| Keyword Retrieval | BM25 | Keyword-based search |
| Reranking | Cross-Encoder | Retrieval optimization |
| Database | PostgreSQL | Structured data storage |
| ORM | SQLAlchemy | Database operations |
| Migrations | Alembic | Schema management |
| PDF Processing | PyMuPDF | Text extraction |
| Evaluation | RAGAS | RAG evaluation |
| Authentication | JWT | User authentication |
| Local Infrastructure | Docker Compose | Run PostgreSQL + pgvector locally |
| Version Control | Git + GitHub | Code management |
| Deployment | Vercel + Render / equivalent | Application hosting |

---

# 4. FRONTEND ARCHITECTURE

**Technology: React + Vite + Tailwind CSS**

The frontend will contain the following pages:

| Page | Functionalities |
|---|---|
| Login / Signup | User authentication and registration |
| Dashboard | Statistics, recent documents and activity |
| AI Assistant | Chat interface, answers and citations |
| Document Library | Upload, search, filter and manage documents |
| Document Details | Metadata, extracted text and versions |
| Regulatory Comparison | Compare document versions |
| Compliance Intelligence | Requirements and review checklists |
| Cross-Document Research | Multi-document analysis |
| Analytics | Charts and research statistics |
| Profile & Settings | Account information and preferences |

### Reusable Frontend Components

- Sidebar
- Navbar
- StatsCard
- DocumentCard
- UploadModal
- ChatWindow
- ChatMessage
- CitationCard
- ComparisonViewer
- RequirementTable
- FilterPanel
- ChartComponents

### Frontend Folder Structure

```text
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── common/
│   │   ├── dashboard/
│   │   ├── documents/
│   │   ├── assistant/
│   │   ├── comparison/
│   │   └── compliance/
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Assistant.jsx
│   │   ├── Documents.jsx
│   │   ├── Comparison.jsx
│   │   ├── Compliance.jsx
│   │   ├── Research.jsx
│   │   └── Settings.jsx
│   ├── services/
│   │   └── api.js
│   ├── hooks/
│   ├── context/
│   ├── layouts/
│   ├── App.jsx
│   └── main.jsx
├── package.json
└── vite.config.js
```

### Frontend Notes

- Auth token (JWT) is stored by the app and attached to every Axios request through an interceptor in `services/api.js`.
- Protected routes redirect unauthenticated users to Login.
- Citation cards must show: document title, authority, page number, section (if known), and the supporting excerpt.
- UI design work uses the ui-ux-pro-max and impeccable skills.

---

# 5. BACKEND ARCHITECTURE

**Technology: Python + FastAPI**

The backend will contain the following services.

| Service | Responsibilities |
|---|---|
| Authentication Service | Registration, login, JWT and authorization |
| Document Ingestion Service | PDF upload, text extraction, cleaning and chunking |
| Embedding Service | Generate document and query embeddings |
| RAG Service | Retrieval, reranking, context building and answer generation |
| Regulatory Comparison Service | Version comparison and change detection |
| Compliance Extraction Service | Requirement extraction and classification |
| Cross-Document Research Service | Multi-document retrieval and analysis |
| Evaluation Service | Retrieval and answer quality evaluation |

### RAG Pipeline

**A. Document Ingestion Pipeline**

1. Upload PDF.
2. Extract text using PyMuPDF.
3. Clean extracted text.
4. Extract document metadata.
5. Split text into chunks.
6. Generate embeddings using Hugging Face.
7. Store chunks and embeddings in PostgreSQL with pgvector.

**B. Question-Answering Pipeline**

1. Receive user query.
2. Preprocess and rewrite query when needed.
3. Generate query embedding.
4. Perform vector similarity search.
5. Perform BM25 keyword retrieval.
6. Combine retrieval results.
7. Rerank relevant chunks.
8. Pass retrieved context and user query to Gemini.
9. Generate a grounded response.
10. Attach source citations.
11. Save conversation and citations in PostgreSQL.

### Backend Folder Structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── documents.py
│   │   ├── assistant.py
│   │   ├── comparison.py
│   │   ├── compliance.py
│   │   └── analytics.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── models/
│   ├── schemas/
│   ├── database/
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── document_service.py
│   │   ├── comparison_service.py
│   │   └── compliance_service.py
│   ├── rag/
│   │   ├── ingestion.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── retrieval.py
│   │   ├── reranking.py
│   │   ├── generation.py
│   │   └── evaluation.py
│   ├── utils/
│   └── main.py
├── tests/
├── requirements.txt
└── .env.example
```

### Grounding Rules for Answer Generation

- The LLM prompt must instruct the model to answer **only** from the provided context.
- If the retrieved context does not support an answer, the response must say that the documents do not contain enough information.
- Every factual claim in an answer must map to at least one retrieved chunk, stored in the `citations` table.
- Responses are informational, not legal advice.

---

# 6. DATABASE ARCHITECTURE

**Technology: PostgreSQL + pgvector**

PostgreSQL will store structured application data, while pgvector will enable vector similarity search.

### Database Tables

| Table | Important Fields | Purpose |
|---|---|---|
| users | id, name, email, password_hash, role | User accounts |
| documents | id, title, authority, category, source_url, publication_date, status | Regulatory document metadata |
| document_versions | id, document_id, version_number, effective_date, parent_version_id | Document version management |
| document_chunks | id, document_id, version_id, chunk_text, page_number, metadata, embedding | Extracted text and vectors |
| conversations | id, user_id, title, created_at | Chat sessions |
| messages | id, conversation_id, role, content, created_at | Conversation messages |
| citations | id, message_id, chunk_id, relevance_score | Links AI answers to source chunks |
| comparison_reports | id, user_id, version_a_id, version_b_id, report_json, summary, created_at | Saved change-detection reports |
| compliance_checklists | id, user_id, title, document_id, created_at | Saved checklists |
| compliance_requirements | id, checklist_id, requirement_text, category, authority, source_chunk_id, status, reviewer_notes | Individual extracted requirements and review status |
| saved_queries | id, user_id, query_text, created_at | Saved research queries |
| evaluation_runs | id, run_name, dataset_name, metrics_json, created_at | RAGAS and retrieval evaluation results |

### Field Notes

- `documents.status`: `uploaded`, `processing`, `indexed`, `failed`.
- `documents.authority`: `RBI`, `SEBI`, `NPCI`, `OTHER`.
- `users.role`: `user`, `admin`.
- `messages.role`: `user`, `assistant`.
- `compliance_requirements.status`: `pending_review`, `reviewed`, `not_applicable`.
- `document_chunks.metadata` (JSONB): section heading, chunk index, character offsets.
- `document_chunks.embedding`: pgvector `vector(N)` column. `N` must match the chosen embedding model (record the model and dimension in `docs/DECISIONS.md`).
- `document_versions.parent_version_id` links a version to the one it replaced.

### Indexes

- Vector index on `document_chunks.embedding` (HNSW or IVFFlat, with cosine distance).
- Index on `document_chunks(document_id, version_id)`.
- Index on `documents(authority, category, status)`.
- Unique index on `users.email`.

### Migrations

All schema changes go through Alembic migrations. The first migration must run `CREATE EXTENSION IF NOT EXISTS vector;`.

---

# 7. API ENDPOINTS (PLANNED)

All endpoints except register and login require a valid JWT.

| Area | Method + Path | Purpose |
|---|---|---|
| System | GET /health | Health check |
| Auth | POST /auth/register | Create account |
| Auth | POST /auth/login | Return JWT |
| Auth | GET /auth/me | Current user |
| Documents | POST /documents/upload | Upload PDF and start ingestion |
| Documents | POST /documents/import-url | Import PDF from an official URL |
| Documents | GET /documents | List, search and filter documents |
| Documents | GET /documents/{id} | Metadata, versions, processing status |
| Documents | DELETE /documents/{id} | Remove document and its chunks |
| Assistant | POST /assistant/ask | Ask a question, return answer and citations |
| Assistant | GET /assistant/conversations | List chat sessions |
| Assistant | GET /assistant/conversations/{id} | Messages in a session |
| Comparison | POST /comparison/compare | Compare two document versions |
| Comparison | GET /comparison/reports | Saved reports |
| Compliance | POST /compliance/extract | Extract requirements from a document |
| Compliance | PATCH /compliance/requirements/{id} | Update review status |
| Compliance | GET /compliance/checklists/{id}/export | Export checklist (CSV) |
| Research | POST /research/cross-document | Multi-document analysis |
| Analytics | GET /analytics/summary | Dashboard statistics |

Exact paths may be refined during implementation. Record any changes in `docs/DECISIONS.md`.

---

# 8. EVALUATION PLAN

The platform must measure how well retrieval and generation work, not just demonstrate them.

**Test set:** 30 to 50 question-answer pairs written by hand from real RBI/SEBI/NPCI documents, each with the expected source page.

**Metrics:**

| Area | Metric | What it tells us |
|---|---|---|
| Retrieval | Hit rate / recall@k | Did the right chunk appear in the top k? |
| Retrieval | MRR | How high was the right chunk ranked? |
| Generation | Faithfulness (RAGAS) | Is the answer supported by retrieved context? |
| Generation | Answer relevancy (RAGAS) | Does the answer address the question? |
| Retrieval | Context precision / recall (RAGAS) | Was retrieved context useful and complete? |

**Experiments to report:**
- Vector-only vs BM25-only vs hybrid retrieval.
- With vs without cross-encoder reranking.
- Different chunk sizes and overlaps.

Results are stored in `evaluation_runs` and summarized in the dashboard and project report.

---

# 9. NON-FUNCTIONAL REQUIREMENTS

- **Security:** passwords hashed (bcrypt or argon2), JWT with expiry, secrets only in `.env`, file-type and size validation on uploads, per-user data isolation.
- **Performance:** document ingestion runs as a background task so uploads do not block; typical question answered within a few seconds.
- **Reliability:** failed ingestion sets document status to `failed` with an error message; re-processing is possible.
- **Maintainability:** type hints, Pydantic schemas, tests for backend logic, readable code with comments on non-obvious parts.
- **Reproducibility:** `docker compose up` starts the database; `.env.example` lists every required variable.

---

# 10. DEVELOPMENT PHASES

| Phase | Scope | Done when |
|---|---|---|
| 0 | FastAPI skeleton, Docker Compose for Postgres + pgvector, SQLAlchemy models, Alembic migration | `/health` works and tables are created |
| 1 | JWT authentication | Register and login work via Swagger UI |
| 2 | PDF upload, PyMuPDF extraction, cleaning, chunking, embeddings, pgvector storage | A real RBI PDF is stored as chunks with page numbers |
| 3 | Hybrid retrieval, reranking, Gemini answer generation with citations | A question returns a grounded answer with page references |
| 4 | Frontend: login, document library, chat UI, citation cards | End-to-end demo works |
| 5 | Regulatory comparison, then compliance extractor | Each has its own API and UI |
| 6 | Cross-document research, analytics dashboard, RAGAS evaluation | Metrics are reported |
| 7 | Deployment | App is live on Vercel + Render (or equivalent) |

**MVP = Phases 0 to 4.**

---

# 11. SCOPE, LIMITATIONS AND DISCLAIMER

- FinScope assists research and review. It does **not** provide legal or compliance advice, and outputs must be verified against the original documents.
- Answers are limited to documents the user has uploaded or imported.
- Scanned (image-only) PDFs may need OCR, which is out of scope for the MVP.
- Tables and multi-column layouts in PDFs can extract poorly; known issues are logged in `docs/PROGRESS.md`.
- Only documents from official sources should be used.

---

# 12. FUTURE SCOPE

- OCR support for scanned circulars.
- Automatic fetching of new circulars from RBI, SEBI and NPCI websites.
- Alerts when a new document affects saved checklists.
- Multilingual support (Hindi and regional languages).
- Role-based team workspaces.
- Fine-tuned or domain-specific embedding models.
