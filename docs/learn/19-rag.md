# RAG (retrieval-augmented generation)

1. **One-line definition**
RAG answers a question by first retrieving passages from your documents and then asking a language model to write the answer from those passages.

2. **Why it exists** (the problem it solves)
A general model has not read this week's RBI circular. If it answers from memory it can sound sure and still be wrong. Giving it the retrieved chunks ties the answer to the library.

3. **Analogy**
It is an open-book exam. The model may write the sentence, but the book on the desk is the only source it is allowed to use.

4. **How it works** (step by step)
- **Step 1:** `POST /assistant/ask` embeds the question and runs hybrid search.
- **Step 2:** The top chunks are written into a prompt as numbered blocks.
- **Step 3:** Gemini writes the answer. If there are no chunks, Gemini is not called.
- **Step 4:** The question, the answer, and the citations are saved on a conversation.

5. **Where it is in FinScope** (file + function)
- File: [backend/app/services/assistant_service.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/services/assistant_service.py)
- Function: `answer_question`
- The route is `ask` in [backend/app/api/assistant.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/api/assistant.py)

6. **Common mistakes**
- Sending the whole PDF instead of the shortlisted chunks. The model then has too much text and no clear page to cite.
- Calling the model when retrieval returned nothing. FinScope returns the fixed "not enough information" sentence instead.
- Forgetting to store the turn. The next read of the conversation would have no history.

7. **Check yourself**
1. *What is retrieved before the model runs?*
2. *When is Gemini skipped?*
3. *Where is the answer saved?*

---
**Answers:**
1. Up to four reranked chunks from the current user's indexed documents.
2. When hybrid search returns no chunks.
3. As an assistant `Message` on the `Conversation`, with `Citation` rows for the chunks the answer marked.
