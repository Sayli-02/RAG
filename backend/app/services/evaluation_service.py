import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.evaluation import EvaluationRun
from app.rag.embeddings import embed_texts
from app.rag.evaluation import aggregate_retriever, lexical_faithfulness
from app.rag.generation import complete_with_gemini, generate_answer
from app.rag.retrieval import bm25_search, hybrid_search, vector_search

SAMPLE_PATH = Path(__file__).resolve().parents[1] / "rag" / "sample_questions.json"


def load_sample_cases() -> list[dict]:
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


def run_evaluation(db: Session, user_id: int, run_name: str = "sample") -> EvaluationRun:
    """Score vector, BM25, and hybrid search on the labeled questions and store the run.

    Faithfulness is the share of answer words found in the retrieved text. It is recorded
    only when GEMINI_API_KEY is set. The labeled questions live in sample_questions.json.
    """
    cases = load_sample_cases()
    k = settings.RERANK_K
    complete = complete_with_gemini if settings.GEMINI_API_KEY else None
    vector_hits = []
    keyword_hits = []
    hybrid_hits = []
    faith_scores = []
    for case in cases:
        question = case["question"]
        expected = int(case["expected_page"])
        query_vector = embed_texts([question])[0]
        vector_pages = [chunk.page_number for chunk in vector_search(db, user_id, query_vector, k)]
        keyword_pages = [chunk.page_number for chunk in bm25_search(db, user_id, question, k)]
        hybrid_chunks = hybrid_search(db, user_id, question, query_vector)
        hybrid_pages = [chunk.page_number for chunk in hybrid_chunks]
        vector_hits.append((expected, vector_pages))
        keyword_hits.append((expected, keyword_pages))
        hybrid_hits.append((expected, hybrid_pages))
        if complete is not None:
            answer, _indexes = generate_answer(question, hybrid_chunks, complete)
            context = "\n".join(chunk.text for chunk in hybrid_chunks)
            faith_scores.append(lexical_faithfulness(answer, context))
    metrics = {
        "k": k,
        "cases": len(cases),
        "vector": aggregate_retriever(vector_hits, k),
        "bm25": aggregate_retriever(keyword_hits, k),
        "hybrid": aggregate_retriever(hybrid_hits, k),
        "faithfulness": (sum(faith_scores) / len(faith_scores)) if faith_scores else None,
        "faithfulness_method": "lexical_overlap",
    }
    if complete is None:
        metrics["faithfulness_method"] = "skipped_without_gemini_key"
    run = EvaluationRun(run_name=run_name, dataset_name="sample_questions", metrics_json=metrics)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def latest_run(db: Session) -> EvaluationRun | None:
    return db.scalars(select(EvaluationRun).order_by(EvaluationRun.created_at.desc())).first()
