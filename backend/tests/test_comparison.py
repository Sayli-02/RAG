from app.rag.diffing import build_diff, count_summary, summarize_diff


def _chunk(text, page, chunk_id, embedding=None):
    return {"text": text, "page": page, "chunk_id": chunk_id, "embedding": embedding}


def test_identical_chunks_are_unchanged():
    chunks = [_chunk("Lenders must disclose the annual percentage rate.", 1, 1)]
    diff = build_diff(chunks, chunks)
    assert diff["unchanged_count"] == 1
    assert diff["added"] == []
    assert diff["removed"] == []
    assert diff["modified"] == []


def test_wording_change_on_the_same_page_is_modified():
    older = [_chunk("Lenders must disclose the APR before sanction.", 1, 1)]
    newer = [_chunk("Lenders must disclose the annual percentage rate before sanction.", 1, 2)]
    diff = build_diff(older, newer)
    assert diff["modified"][0]["before"].startswith("Lenders must disclose the APR")
    assert "annual percentage rate" in diff["modified"][0]["after"]
    assert diff["added"] == []
    assert diff["removed"] == []


def test_rewritten_sentence_pairs_by_embedding():
    older = [_chunk("Penalty applies on late payment.", 2, 1, [1.0, 0.0])]
    newer = [_chunk("A fee is charged when payment is late.", 4, 2, [0.96, 0.28])]
    diff = build_diff(older, newer)
    assert len(diff["modified"]) == 1
    assert diff["added"] == []
    assert diff["removed"] == []
    assert diff["modified"][0]["page"] == 4


def test_unmatched_chunks_are_added_and_removed():
    older = [_chunk("Old cooling-off rule.", 2, 1)]
    newer = [_chunk("New disclosure rule.", 3, 2)]
    diff = build_diff(older, newer)
    assert diff["removed"][0]["text"] == "Old cooling-off rule."
    assert diff["added"][0]["text"] == "New disclosure rule."
    assert count_summary(diff) == "1 added, 1 removed, 0 modified."


def test_summary_reads_json_and_falls_back_when_it_is_not_json():
    diff = build_diff([_chunk("Old cooling-off rule.", 2, 1)], [_chunk("New disclosure rule.", 3, 2)])

    def good(_prompt):
        return '{"summary": "The cooling-off rule was replaced.", "affected_requirements": ["Cooling-off"]}'

    summary, affected = summarize_diff(diff, good)
    assert summary == "The cooling-off rule was replaced."
    assert affected == ["Cooling-off"]

    fallback, empty = summarize_diff(diff, lambda _prompt: "not json")
    assert fallback == "1 added, 1 removed, 0 modified."
    assert empty == []

    plain, none = summarize_diff(diff, None)
    assert plain == "1 added, 1 removed, 0 modified."
    assert none == []
