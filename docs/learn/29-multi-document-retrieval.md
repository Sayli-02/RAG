# Multi-document retrieval

1. **One-line definition**
Multi-document retrieval searches only the documents you chose, then answers from those passages.

2. **Why it exists** (the problem it solves)
The assistant searches every indexed file you own. A question about two circulars can then be answered from a third file that happens to share the same words.

3. **Analogy**
You put two folders on the desk and leave the rest on the shelf. The search is allowed to open only the folders on the desk.

4. **How it works** (step by step)
- **Step 1:** The request lists at least two different document ids. Duplicates count once. Each id must belong to you and be indexed.
- **Step 2:** Vector search and BM25 add `document_id IN (...)` so the top matches come from those files.
- **Step 3:** `keep_selected` drops any leftover chunk whose document was not in the list, then the same reranker and Gemini path as the assistant run.
- **Step 4:** The question text is stored in `saved_queries`. The answer cites document, page, and excerpt. An empty retrieval uses the same refusal sentence as the assistant.

5. **Where it is in FinScope** (file + function)
- `keep_selected` and the `document_ids` argument of `hybrid_search` in `backend/app/rag/retrieval.py`
- `ask_across_documents` in `backend/app/services/research_service.py`
- `POST /research/cross-document` in `backend/app/api/research.py`

6. **Common mistakes**
- Filtering only after the top 10 are chosen. The selected document can be missing because other files filled the list.
- Treating two copies of the same id as two documents.
- Saving the answer as if the document list were stored. Only the question text is saved. Clicking it again fills the box. You still pick the documents.

7. **Check yourself**
1. *What is the minimum number of distinct documents?*
2. *What does `keep_selected` do when `document_ids` is None?*
3. *Which sentence is returned when those documents have no matching chunk?*

## Answers
1. Two.
2. It returns the chunks unchanged. That is how the assistant searches everything you own.
3. `The documents do not contain enough information to answer this.`
