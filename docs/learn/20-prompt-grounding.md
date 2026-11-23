# Prompt grounding

1. **One-line definition**
Grounding is an instruction that the model may use only the supplied context, and must say so when that context is not enough.

2. **Why it exists** (the problem it solves)
A model will otherwise fill gaps with plausible regulatory language. The prompt has to forbid outside knowledge and name the exact sentence to use when the chunks do not support an answer.

3. **Analogy**
It is like telling a witness: answer from this packet only, and if the packet does not say, reply with this one sentence.

4. **How it works** (step by step)
- **Step 1:** `build_prompt` numbers each chunk as `[1]`, `[2]`, with the document title and page.
- **Step 2:** The prompt says to use only that context, that the reply is not legal advice, and to cite a block by its number.
- **Step 3:** If the context is not enough, the model is told to reply with exactly: "The documents do not contain enough information to answer this."
- **Step 4:** The same sentence is returned without a model call when retrieval itself is empty.

5. **Where it is in FinScope** (file + function)
- File: [backend/app/rag/generation.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/rag/generation.py)
- Functions: `build_prompt` and `generate_answer`
- The refusal sentence is the constant `NOT_ENOUGH`

6. **Common mistakes**
- Putting the instruction after the question, where it is easier to ignore. Here the rules come first and the question comes last.
- Treating the instruction as a guarantee. The model can still drift. Citation markers are the check that follows.
- Rewriting the question with a second model call. Phase 3 sends the question as typed.

7. **Check yourself**
1. *What must the model reply when the chunks do not support an answer?*
2. *Why is the question at the end of the prompt?*
3. *What does the prompt say about legal advice?*

---
**Answers:**
1. Exactly `NOT_ENOUGH`: "The documents do not contain enough information to answer this."
2. The rules and the numbered context are in place before the question, so the model reads the constraint first.
3. It says the answer is not legal advice.
