# Faithfulness

1. **One-line definition**
Faithfulness asks whether the words in the answer are supported by the text that was retrieved.

2. **Why it exists** (the problem it solves)
A high retrieval score only means the right page showed up. The model can still add a fact that was not on that page.

3. **Analogy**
You may only use the words on the cards in front of you. Faithfulness is the share of your sentence that you can point to on a card.

4. **How it works** (step by step)
- **Step 1:** Take the answer and the retrieved chunk text.
- **Step 2:** Keep answer words longer than three letters.
- **Step 3:** Count how many of those words appear in the retrieved text, and divide by the number of answer words.
- **Step 4:** The refusal sentence scores 1, because it adds no extra claim. This runs only when `GEMINI_API_KEY` is set. The RAGAS library, which would ask another model to judge the answer, is not installed.

5. **Where it is in FinScope** (file + function)
- `lexical_faithfulness` in `backend/app/rag/evaluation.py`
- Called from `run_evaluation` in `backend/app/services/evaluation_service.py`
- Shown on the Dashboard as Faithfulness

6. **Common mistakes**
- Treating a score of 1 as proof the answer is correct. Shared words can still be arranged into a wrong claim.
- Comparing this number with a published RAGAS faithfulness score. They are different procedures.
- Running it with an empty Gemini key and expecting a number. The field stays empty and the method is recorded as skipped.

7. **Check yourself**
1. *What does a score of 1 mean here?*
2. *What does the refusal sentence score?*
3. *Why is this not called a RAGAS score?*

## Answers
1. Every longer word in the answer also appears in the retrieved text.
2. 1.
3. RAGAS uses a model as a judge. FinScope counts overlapping words.
