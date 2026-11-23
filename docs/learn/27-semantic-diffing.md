# Semantic diffing

1. **One-line definition**
Semantic diffing pairs passages that mean the same thing even when the words changed.

2. **Why it exists** (the problem it solves)
"Penalty applies on late payment" and "A fee is charged when payment is late" share few characters. A text-only diff would call one removed and the other added.

3. **Analogy**
Two people describe the same rule in different words. You match the ideas, then note that the wording changed.

4. **How it works** (step by step)
- **Step 1:** Each chunk already has an embedding from ingestion.
- **Step 2:** `cosine` in the diff module compares those vectors. Missing embeddings score 0, and the text ratio still decides the pair.
- **Step 3:** When both sides have embeddings, the pair score is 0.45 times the text ratio plus 0.55 times the cosine, plus 0.05 when the page numbers match.
- **Step 4:** A pair is kept when the text ratio is at least 0.4 or the cosine is at least 0.75. High cosine and a lower text ratio is labeled modified, not added plus removed.

5. **Where it is in FinScope** (file + function)
- `cosine` and `_pair_score` in `backend/app/rag/diffing.py`
- Chunk vectors are loaded in `_chunk_payloads` in `backend/app/services/comparison_service.py`

6. **Common mistakes**
- Treating cosine as a substitute for reading the text. A high cosine still needs the before and after sentences in the report.
- Pairing one newer chunk with two older chunks. Each newer chunk is used once.
- Assuming embeddings exist. A failed or partial index can leave them empty, and the text ratio still runs.

7. **Check yourself**
1. *What problem does cosine solve that a character ratio does not?*
2. *What happens when a chunk has no embedding?*
3. *Can one newer chunk be the match for two older chunks?*

## Answers
1. It can pair a rewritten sentence that shares the same meaning.
2. Cosine is 0 and pairing uses the text ratio and the page bonus.
3. No. Each newer chunk is used at most once.
