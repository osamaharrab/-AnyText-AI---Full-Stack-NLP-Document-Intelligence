from __future__ import annotations

import pandas as pd

from src.analytics import compute_co_occurrence, compute_label_counts, compute_top_entities


def _entity_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"document_id": "d1", "entity_text": "Apple", "label": "ORG", "category": "technology"},
            {"document_id": "d1", "entity_text": "Apple", "label": "ORG", "category": "technology"},
            {"document_id": "d1", "entity_text": "Microsoft", "label": "ORG", "category": "technology"},
            {"document_id": "d2", "entity_text": "Apple", "label": "ORG", "category": "business"},
            {"document_id": "d2", "entity_text": "London", "label": "GPE", "category": "business"},
        ]
    )


def test_compute_top_entities_counts_mentions_and_documents():
    top = compute_top_entities(_entity_frame(), n=3)

    apple = top[top["entity_text"] == "Apple"].iloc[0]
    assert apple["count"] == 3
    assert apple["document_count"] == 2


def test_compute_label_counts():
    counts = compute_label_counts(_entity_frame())

    assert counts[counts["label"] == "ORG"].iloc[0]["count"] == 4
    assert counts[counts["label"] == "GPE"].iloc[0]["count"] == 1


def test_compute_co_occurrence_does_not_double_count_duplicate_entity_in_document():
    pairs = compute_co_occurrence(_entity_frame())

    apple_microsoft = pairs[
        (pairs["entity_1"] == "Apple") & (pairs["entity_2"] == "Microsoft")
    ].iloc[0]
    assert apple_microsoft["cooccurrence_count"] == 1
