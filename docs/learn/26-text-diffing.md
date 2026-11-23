# Text diffing

1. **One-line definition**
Text diffing measures how much two strings still match, character by character.

2. **Why it exists** (the problem it solves)
A regulation can keep the same sentence and change one phrase. Treating the whole chunk as brand new would hide that it is an edit.

3. **Analogy**
A teacher comparing two drafts lines up the words that stayed and circles the words that moved. The score is how much of the page still lines up.

4. **How it works** (step by step)
- **Step 1:** `SequenceMatcher` finds the longest shared pieces of the two strings.
- **Step 2:** `ratio()` is `2 * shared / (length of both strings)`. 1.0 means identical. 0 means nothing in common.
- **Step 3:** FinScope pairs an older chunk with the newer chunk that scores highest.
- **Step 4:** A ratio of 0.92 or more is labeled unchanged. A paired chunk below that is modified. A chunk with no partner is removed (older) or added (newer).

5. **Where it is in FinScope** (file + function)
- `text_ratio` and `build_diff` in `backend/app/rag/diffing.py`
- Saved on the report by `compare_documents` in `backend/app/services/comparison_service.py`

6. **Common mistakes**
- Calling a small wording change "added and removed" because the chunks were never paired.
- Using a ratio of 1.0 as the only "unchanged" cutoff. Tiny punctuation then looks like a rewrite.
- Diffing whole PDFs as one string. Page numbers and chunk ids are then lost.

7. **Check yourself**
1. *What does a ratio of 1.0 mean?*
2. *When is a paired chunk called modified?*
3. *Where does an older chunk go if nothing in the newer document pairs with it?*

## Answers
1. The two strings are the same.
2. When it has a partner but the text ratio is below 0.92.
3. Into `removed`.
