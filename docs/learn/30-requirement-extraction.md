# Requirement extraction

1. **One-line definition**
Requirement extraction turns a circular into a list of things a firm must do, each tied to the chunk it came from.

2. **Why it exists** (the problem it solves)
A long PDF is hard to review as prose. A checklist lets a person mark each obligation as reviewed or not applicable.

3. **Analogy**
You highlight every sentence that says "must" or "shall", copy those lines onto a form, and leave a checkbox beside each one.

4. **How it works** (step by step)
- **Step 1:** The latest indexed version's chunks are numbered.
- **Step 2:** When `GEMINI_API_KEY` is set, the model is asked for JSON: requirement text, a category, and the chunk number.
- **Step 3:** Pydantic checks that shape. A bad reply, a missing key, or an empty list falls back to sentences that contain must, shall, or required.
- **Step 4:** Each item is stored on a checklist with status `pending_review`, the document's authority, and the source chunk. A person can change the status and notes. CSV export writes one row per requirement.

5. **Where it is in FinScope** (file + function)
- `extract_requirements` in `backend/app/rag/requirements.py`
- `extract_checklist` and `checklist_csv` in `backend/app/services/compliance_service.py`
- `POST /compliance/extract`, `PATCH /compliance/requirements/{id}`, and `GET /compliance/checklists/{id}/export`

6. **Common mistakes**
- Treating the checklist as a legal opinion. It is a draft for a person to review.
- Trusting a model JSON list that points at a chunk number you did not send.
- Losing the page number. The page stays on the source chunk, and the CSV reads it from there.

7. **Check yourself**
1. *What status does a new requirement start with?*
2. *When does the sentence scanner run?*
3. *What three review statuses can be saved?*

## Answers
1. `pending_review`.
2. When there is no Gemini key, or the model reply is missing, invalid, or empty.
3. `pending_review`, `reviewed`, and `not_applicable`.
