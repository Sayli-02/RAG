# Chunking

1. **One-line definition**
Chunking cuts a long document into smaller passages that can be embedded, retrieved, and cited on their own.

2. **Why it exists** (the problem it solves)
An embedding of an entire circular mixes every topic into one vector, and a citation of "the whole PDF" does not tell the reader where to look. Smaller passages stay about one idea and can point at a page.

3. **Analogy**
It is like cutting a newspaper into clippings. You keep the page number on each clipping. You do not glue the bottom of page 2 to the top of page 3.

4. **How it works** (step by step)
- **Step 1:** Each cleaned page is split on its own. Chunks never cross a page boundary, so each chunk has one page number.
- **Step 2:** A window of about 1,000 characters is taken. The cut prefers the last newline or space inside the window so it does not end mid-word.
- **Step 3:** The next window starts 150 characters before the previous cut, so a sentence that sat on the boundary appears in both chunks.
- **Step 4:** Metadata stores `chunk_index`, `start_char`, `end_char`, and a `section_heading` when the first line is short and does not end with a period.

5. **Where it is in FinScope** (file + function)
- File: [backend/app/rag/chunking.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/chunking.py)
- Function: `chunk_page`
- Sizes come from `CHUNK_SIZE` and `CHUNK_OVERLAP` in [backend/app/core/config.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/core/config.py)
- The heading rule is `_section_heading` in [backend/app/rag/ingestion.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/ingestion.py)

6. **Common mistakes**
- Overlap greater than or equal to the chunk size, which would repeat the same window forever. `chunk_page` treats that overlap as zero.
- Merging pages to fill a chunk. That makes the page citation ambiguous.
- Chunking the original PDF text and citing the cleaned text. Offsets are positions in the cleaned page.

7. **Check yourself**
1. *Why is there overlap between neighboring chunks?*
2. *Why can a chunk be shorter than 1,000 characters?*
3. *What is `chunk_index` counted across?*

---
**Answers:**
1. So a fact that sits on the cut is still fully inside at least one chunk.
2. The splitter breaks at a newline or space, and the last piece of a page is whatever remains.
3. The whole document, starting at 0, in reading order. It is not restarted on each page.
