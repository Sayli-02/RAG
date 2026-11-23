# Structured LLM output

1. **One-line definition**
Structured output asks the model for JSON and checks that the JSON matches a fixed shape before the app uses it.

2. **Why it exists** (the problem it solves)
A free-text summary cannot be stored as a list of affected requirements. If the model adds a greeting or breaks the JSON, the app needs a safe sentence anyway.

3. **Analogy**
You hand someone a form with two boxes. If they hand back a letter instead of the form, you fill the boxes yourself from the counts you already know.

4. **How it works** (step by step)
- **Step 1:** The prompt asks for JSON only, with `summary` and `affected_requirements`.
- **Step 2:** A regex takes the first `{...}` block in case the model wraps it in extra text.
- **Step 3:** Pydantic `model_validate_json` rejects a missing summary or a requirements value that is not a list of strings.
- **Step 4:** Any failure, or a missing `GEMINI_API_KEY`, stores the count sentence: "N added, N removed, N modified." The requirements list stays empty. Tests pass a fake `complete` function and never call Gemini.

5. **Where it is in FinScope** (file + function)
- `summarize_diff` in `backend/app/rag/diffing.py`
- `compare_documents` passes `complete_with_gemini` only when the key is set, in `backend/app/services/comparison_service.py`

6. **Common mistakes**
- Trusting the raw model string and writing it into the database without validation.
- Letting a bad summary fail the whole comparison. The diff itself is already known.
- Calling Gemini from unit tests. A fake function that returns a string is enough.

7. **Check yourself**
1. *Which two fields must the JSON contain?*
2. *What is stored if the model returns plain text?*
3. *When does the comparison skip Gemini?*

## Answers
1. `summary` (a string) and `affected_requirements` (a list of strings).
2. The count sentence, and an empty requirements list.
3. When `GEMINI_API_KEY` is empty. Tests also skip it by passing their own function or `None`.
