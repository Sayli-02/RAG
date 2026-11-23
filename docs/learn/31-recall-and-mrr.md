# Recall and mean reciprocal rank

1. **One-line definition**
Recall@k asks whether the expected page appeared in the top k results. Mean reciprocal rank asks how high that page was.

2. **Why it exists** (the problem it solves)
A search can return text that sounds related and still miss the page you wrote down as the right one. These two numbers make that miss visible.

3. **Analogy**
You hid a bookmark on page 3. Recall asks "was page 3 in the pile I was handed?" Reciprocal rank asks "was it the first sheet, the second, or missing?"

4. **How it works** (step by step)
- **Step 1:** A labeled question names one expected page.
- **Step 2:** A retriever returns pages in order. Only the first k count. FinScope uses `RERANK_K` for k.
- **Step 3:** If the expected page is missing, that question scores recall 0 and reciprocal rank 0.
- **Step 4:** If it is at position r (starting at 1), recall is 1 and reciprocal rank is 1/r. The run averages those scores for vector search, BM25, and hybrid search, then stores them on `evaluation_runs`.

5. **Where it is in FinScope** (file + function)
- `hit_and_reciprocal` and `aggregate_retriever` in `backend/app/rag/evaluation.py`
- `run_evaluation` in `backend/app/services/evaluation_service.py`
- The labeled questions are `backend/app/rag/sample_questions.json`

6. **Common mistakes**
- Reading a high score as "the answer was good." These scores only check the page number.
- Using questions whose expected pages are not in your uploaded PDFs. The sample questions expect pages 3, 5, and 2, so a different corpus scores zero.
- Comparing vector and BM25 scores from different k values.

7. **Check yourself**
1. *What is recall when the expected page is second in a list of four and k is 4?*
2. *What is the reciprocal rank in that same case?*
3. *Where is the number stored?*

## Answers
1. 1.
2. 1/2, which is 0.5.
3. `evaluation_runs.metrics_json`, returned by `GET /evaluation/latest`.
