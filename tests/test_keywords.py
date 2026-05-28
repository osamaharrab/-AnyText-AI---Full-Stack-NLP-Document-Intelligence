from __future__ import annotations

import pandas as pd

from src.keywords import extract_corpus_keywords, extract_document_keywords
from src.preprocessing import prepare_documents


def _documents() -> pd.DataFrame:
    return prepare_documents(
        pd.DataFrame(
            [
                {
                    "id": "d1",
                    "source_name": "sample",
                    "text": "Apple cloud analytics support Microsoft cloud teams.",
                    "language": "en",
                    "category": "technology",
                },
                {
                    "id": "d2",
                    "source_name": "sample",
                    "text": "Public health policy supports hospital analytics.",
                    "language": "en",
                    "category": "health",
                },
            ]
        )
    )


def test_extract_corpus_keywords_returns_ranked_terms():
    keywords = extract_corpus_keywords(_documents(), top_n=5)

    assert not keywords.empty
    assert list(keywords.columns) == ["keyword", "score", "document_count"]
    assert "cloud" in set(keywords["keyword"])
    assert keywords.iloc[0]["score"] >= keywords.iloc[-1]["score"]


def test_extract_document_keywords_includes_document_metadata():
    keywords = extract_document_keywords(_documents(), top_n=3)

    assert not keywords.empty
    assert {"document_id", "source_name", "category", "language", "keyword", "score", "rank"}.issubset(
        keywords.columns
    )
    assert set(keywords["document_id"]) == {"d1", "d2"}
    assert keywords.groupby("document_id")["rank"].max().max() <= 3
