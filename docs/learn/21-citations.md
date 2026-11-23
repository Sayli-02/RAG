# Citations

1. **One-line definition**
A citation connects one sentence of an answer to the chunk, page, and document that support it.

2. **Why it exists** (the problem it solves)
An answer without a page forces the reader to trust the model. A citation lets them open the circular at that page and check the excerpt.

3. **Analogy**
It is a footnote. The number in the sentence points at a card that names the document, the page, and the passage.

4. **How it works** (step by step)
- **Step 1:** The prompt asks the model to write `[1]` or `[2]` when it uses that block.
- **Step 2:** `cited_indexes` reads those markers. Numbers that do not match a retrieved chunk are ignored. Duplicates are kept once.
- **Step 3:** If the answer contains the refusal sentence, every marker is dropped.
- **Step 4:** Each kept chunk becomes a `Citation` row (`message_id`, `chunk_id`, `relevance_score`). The API adds title, authority, page, section heading, and the chunk text as the excerpt.

5. **Where it is in FinScope** (file + function)
- Parsing: `cited_indexes` in [backend/app/rag/generation.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/generation.py)
- Saving: `answer_question` in [backend/app/services/assistant_service.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/services/assistant_service.py)
- Reading them back: `citation_from_row` in the same service, and `read_conversation` in [backend/app/api/assistant.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/api/assistant.py)

6. **Common mistakes**
- Citing every retrieved chunk even when the answer did not use it. Only markers in the answer are stored.
- Citing a number the prompt never showed, such as `[4]` when only two chunks were sent. Those markers are ignored.
- Storing the excerpt without the page. The page comes from `document_chunks.page_number`.

7. **Check yourself**
1. *Which chunks become citation rows?*
2. *What does a refusal do to markers in the same answer?*
3. *Where does the section name come from?*

---
**Answers:**
1. The retrieved chunks whose numbers appear in the answer as `[1]`, `[2]`, and so on.
2. `cited_indexes` returns an empty list, so no citation rows are saved.
3. `section_heading` in the chunk metadata, when cleaning found a short heading line.
