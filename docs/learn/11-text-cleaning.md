# Text cleaning

1. **One-line definition**
Text cleaning rewrites extracted PDF text so line breaks and repeated headers stop looking like part of the sentence.

2. **Why it exists** (the problem it solves)
PDF text keeps the visual line breaks. A word split as `regula-` / `tion` across two lines would be stored as two tokens, and a running header copied onto every page would show up in almost every chunk.

3. **Analogy**
It is like retyping lecture notes that were written in a narrow column: you join the hyphenated words and cross out the page number that was printed at the top of every sheet.

4. **How it works** (step by step)
- **Step 1:** Remove null bytes and turn Windows line endings into `\n`.
- **Step 2:** Join a letter, a hyphen, a newline, and a letter into one word.
- **Step 3:** Collapse spaces on each line and squeeze three or more newlines into a paragraph break.
- **Step 4:** If the same short line appears on every non-empty page, and there are at least three pages, drop that line. Fewer than three pages is not enough evidence that the line is a header.

5. **Where it is in FinScope** (file + function)
- File: [backend/app/rag/cleaning.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/cleaning.py)
- Functions: `clean_page_text` and `drop_repeated_lines`
- Called from `build_chunk_records` in [backend/app/rag/ingestion.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/ingestion.py)

6. **Common mistakes**
- Removing every short line. A real heading can be short. We only drop a line when it is repeated on every page.
- Joining every hyphen. The pattern requires a line break between the hyphen and the next letter, so `e-mail` on one line stays as it is.
- Cleaning after chunking. Offsets and page splits should be computed on the cleaned text.

7. **Check yourself**
1. *Why does `regula-\ntion` become `regulation`?*
2. *Why do we wait for three pages before dropping a repeated line?*
3. *What happens to a blank line between paragraphs?*

---
**Answers:**
1. The regex treats a hyphen at the end of a line as a typesetting break, not as a real hyphen.
2. Two occurrences can be a coincidence or a repeated sentence. Three pages of the same short line is the usual pattern of a header or footer.
3. A single blank line is kept as a paragraph break. Three or more newlines are reduced to one blank line.
