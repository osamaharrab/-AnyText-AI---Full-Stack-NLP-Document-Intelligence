from __future__ import annotations

import pandas as pd

from src.preprocessing import prepare_documents
from src.search import build_tfidf_index, search_documents


def test_tfidf_index_builds_and_search_returns_results():
    frame = prepare_documents(
        pd.DataFrame(
            [
                {
                    "id": "d1",
                    "source_name": "sample",
                    "text": "Apple and Microsoft announced a cloud partnership in London.",
                    "language": "en",
                    "category": "technology",
                },
                {
                    "id": "d2",
                    "source_name": "sample",
                    "text": "Doctors discussed public health policy in Jordan.",
                    "language": "en",
                    "category": "health",
                },
            ]
        )
    )

    vectorizer, matrix = build_tfidf_index(frame)
    results = search_documents("cloud Microsoft", frame, vectorizer, matrix, top_k=1)

    assert vectorizer is not None
    assert matrix is not None
    assert len(results) == 1
    assert results.iloc[0]["id"] == "d1"
    assert results.iloc[0]["similarity_score"] > 0
