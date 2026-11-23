from app.rag.evaluation import aggregate_retriever, hit_and_reciprocal, lexical_faithfulness
from app.rag.requirements import extract_requirements
from app.services.compliance_service import checklist_csv


class _Chunk:
    def __init__(self, page):
        self.page_number = page


class _Requirement:
    def __init__(self):
        self.requirement_text = "Lenders must disclose the annual percentage rate."
        self.category = "obligation"
        self.authority = "RBI"
        self.status = "pending_review"
        self.reviewer_notes = None
        self.source_chunk = _Chunk(3)


class _Checklist:
    requirements = [_Requirement()]


def test_heuristic_keeps_an_obligation_and_skips_a_description():
    chunks = [
        {
            "chunk_id": 7,
            "text": "This circular explains the background. Lenders must disclose the annual percentage rate.",
        }
    ]
    items = extract_requirements(chunks, None)
    assert len(items) == 1
    assert items[0]["chunk_id"] == 7
    assert items[0]["requirement_text"].startswith("Lenders must disclose")


def test_bad_model_json_falls_back_to_the_obligation_sentence():
    chunks = [{"chunk_id": 1, "text": "Lenders must disclose the annual percentage rate before sanction."}]
    items = extract_requirements(chunks, lambda _prompt: "not json")
    assert items[0]["chunk_id"] == 1


def test_model_json_uses_the_numbered_chunk():
    chunks = [
        {"chunk_id": 1, "text": "Background only."},
        {"chunk_id": 2, "text": "Lenders must disclose the annual percentage rate."},
    ]

    def complete(_prompt):
        return '{"requirements": [{"requirement_text": "Disclose the APR.", "category": "disclosure", "chunk_index": 2}]}'

    items = extract_requirements(chunks, complete)
    assert items == [
        {"requirement_text": "Disclose the APR.", "category": "disclosure", "chunk_id": 2}
    ]


def test_csv_includes_the_requirement_and_page():
    text = checklist_csv(_Checklist())
    assert "Lenders must disclose the annual percentage rate." in text
    assert ",3,pending_review," in text


def test_recall_and_mrr_reward_the_expected_page_near_the_top():
    assert hit_and_reciprocal([1, 3, 4], 3, k=4) == (1.0, 0.5)
    assert hit_and_reciprocal([1, 4], 3, k=4) == (0.0, 0.0)
    scores = aggregate_retriever([(3, [3, 1]), (5, [1, 2])], k=4)
    assert scores["recall_at_k"] == 0.5
    assert scores["mrr"] == 0.5


def test_faithfulness_is_the_share_of_answer_words_found_in_the_context():
    score = lexical_faithfulness(
        "Lenders must disclose the annual percentage rate.",
        "Lenders must disclose the annual percentage rate before sanction.",
    )
    assert score == 1.0
    outside = lexical_faithfulness("Volcano insurance is mandatory today.", "Lenders must disclose the rate.")
    assert outside < 1.0
    assert lexical_faithfulness(
        "The documents do not contain enough information to answer this.",
        "",
    ) == 1.0
