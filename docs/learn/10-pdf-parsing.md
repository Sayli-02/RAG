# PDF parsing

1. **One-line definition**
PDF parsing reads the text stored on each page of a PDF, together with that page's number.

2. **Why it exists** (the problem it solves)
A PDF is a drawing of a page, not a list of paragraphs. Before we can search a circular we have to pull the words back out, and we have to remember which page they came from so an answer can cite it.

3. **Analogy**
It is like transcribing a printed book onto index cards, one card per page, instead of photographing the pages and hoping someone can read the photo later.

4. **How it works** (step by step)
- **Step 1:** PyMuPDF opens the file from a path or from the raw bytes.
- **Step 2:** Each page is visited in order. Page numbers start at 1, matching the way people count pages.
- **Step 3:** `get_text()` returns the characters on that page. A scanned page with no text layer returns an empty string. This phase does not run OCR.
- **Step 4:** The file is closed even if reading fails partway through.

5. **Where it is in FinScope** (file + function)
- File: [backend/app/rag/ingestion.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/ingestion.py)
- Function: `extract_pages`
- Called by `build_chunk_records` in the same file

6. **Common mistakes**
- Treating the PDF page index as zero-based in the API. Readers expect page 1 to be the first page.
- Assuming every page has text. A scan looks like a successful upload and then produces no chunks.
- Forgetting to close the document, which keeps the file locked on Windows.

7. **Check yourself**
1. *What does an empty string from a page usually mean?*
2. *Why do we number the first page 1?*
3. *Where is the page number stored after ingestion?*

---
**Answers:**
1. The page has no text layer. It may be a scan or a page of only images. FinScope does not OCR it in this phase.
2. Citations are for humans. "Page 1" should mean the first page of the PDF.
3. On `document_chunks.page_number`, set in `ingest_document` from each `ChunkRecord`.
