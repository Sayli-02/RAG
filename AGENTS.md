# FinScope: Agent Instructions

## Project
AI-powered financial regulatory intelligence platform (RAG over RBI/SEBI/NPCI documents).
Full spec: docs/SPEC.md. Read it before any task.

## Stack
Backend: Python, FastAPI, SQLAlchemy, Alembic, LangChain, PyMuPDF, BM25, cross-encoder reranker, Gemini API, Hugging Face embeddings
DB: PostgreSQL + pgvector
Frontend: React + Vite + Tailwind, React Router, Axios
Folder structure: follow docs/SPEC.md sections 4 and 5.

## Rules
- Work on one phase/module at a time. Do not touch unrelated files.
- Always give a short plan first and wait for my approval before coding.
- Every RAG answer must include citations (document, page, section). If retrieval is weak, say so instead of guessing.
- Write tests for backend logic. Never hardcode secrets; use .env.
- UI work only: use the ui-ux-pro-max and impeccable skills.

## Session start protocol
1. Read AGENTS.md, then docs/PROGRESS.md (latest entries) and the "Current status" below.
2. Tell me in 2-3 lines where we left off.

## End-of-task protocol (mandatory, every task)
1. Append an entry to docs/PROGRESS.md (template inside that file).
2. If we made a design choice, add it to docs/DECISIONS.md.
3. Create or update a concept note in docs/learn/ for every new concept used (see Learning rules).
4. Update "Current status" below.
5. Suggest a git commit message.

## Learning rules
I am building this to learn, not just to ship.
- Before implementing, explain each new concept in 3-5 plain-language lines.
- After implementing, point to the exact file/function where the concept appears.
- Write concept notes in docs/learn/ using the template in docs/learn/00-roadmap.md.
- Prefer simple, readable code over clever code. Comment the non-obvious parts.
- Do not silently make big choices. Offer options with trade-offs.

## Current status
- Phase: 7 (accounts still to create)
- Last completed: Deploy config for Supabase, Vercel, and Render or Railway
- Next step: Create the Supabase database, the API service, and the Vercel site, then set the env vars in the README Deploy section
- Known issues: Docker Desktop was not running, so the UI was not clicked through against a live API. Start Postgres, run `alembic upgrade head`, set `GEMINI_API_KEY`, then `npm run dev` in `frontend/`.
