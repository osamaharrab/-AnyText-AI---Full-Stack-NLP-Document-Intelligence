from __future__ import annotations

import pandas as pd

from src.report import generate_report


def test_generate_report_includes_keywords_and_limitations():
    documents = pd.DataFrame(
        [
            {"id": "d1", "text_length": 100, "category": "technology", "language": "en"},
            {"id": "d2", "text_length": 80, "category": "health", "language": "en"},
        ]
    )
    stats = {
        "total_entities": 2,
        "unique_entities": 2,
        "documents_with_entities": 1,
        "label_counts": pd.DataFrame([{"label": "ORG", "count": 2}]),
        "top_entities": pd.DataFrame(
            [{"entity_text": "Apple", "label": "ORG", "count": 2, "document_count": 1}]
        ),
        "co_occurrence": pd.DataFrame(
            [{"entity_1": "Apple", "entity_2": "Microsoft", "cooccurrence_count": 1}]
        ),
        "cross_category": pd.DataFrame(
            [
                {
                    "category": "technology",
                    "label": "ORG",
                    "entity_mentions": 2,
                    "unique_entities": 2,
                    "documents": 1,
                }
            ]
        ),
        "keywords": pd.DataFrame([{"keyword": "cloud analytics", "score": 1.2, "document_count": 1}]),
    }

    report = generate_report(stats, documents)

    assert "## Top Keywords" in report
    assert "cloud analytics" in report
    assert "## Limitations" in report
    assert "English-first spaCy NER" in report
