# Hallucination

1. **One-line definition**
A hallucination is a claim the model states that the retrieved documents do not support.

2. **Why it exists** (the problem it solves)
Language models are built to continue text, including when the source is silent. In a regulatory answer, an invented rule is worse than no answer.

3. **Analogy**
It is a student who writes a confident paragraph for a page that was not in the assigned reading.

4. **How it works** (step by step)
- **Step 1:** The model is told to use only the numbered chunks and to refuse when they are not enough.
- **Step 2:** If retrieval finds nothing, the API returns the refusal sentence and does not ask the model, so there is no chance to invent a source.
- **Step 3:** If the model answers, only `[n]` markers that match a real chunk are stored. An uncited claim is still visible in the text, and the missing citation is the signal to check it.
- **Step 4:** Phase 3 does not try to prove every sentence against the chunk. That check is the later RAGAS faithfulness evaluation.

5. **Where it is in FinScope** (file + function)
- The refusal path: `generate_answer` in [backend/app/rag/generation.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/generation.py)
- The "do not use outside knowledge" line: `build_prompt` in the same file
- Saved support, when the model cited it: `Citation` rows written by `answer_question`

6. **Common mistakes**
- Treating a fluent answer as a supported answer. Fluency is not evidence.
- Hiding the refusal and letting the model guess. Empty retrieval returns `NOT_ENOUGH` on purpose.
- Assuming citations make the answer true. They show which chunk the model pointed at. The reader still checks the page.

7. **Check yourself**
1. *What does FinScope return when no chunk is retrieved?*
2. *Does a citation prove the sentence is correct?*
3. *Which later phase measures whether the answer stays faithful to the context?*

---
**Answers:**
1. "The documents do not contain enough information to answer this." Gemini is not called.
2. No. It records the chunk the model named. A person, or a later evaluation, still has to see whether the chunk supports the claim.
3. Phase 6, with RAGAS faithfulness.
