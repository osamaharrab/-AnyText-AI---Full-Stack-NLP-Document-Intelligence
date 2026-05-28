"""Lightweight TF-IDF keyword extraction helpers."""

from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


CORPUS_KEYWORD_COLUMNS = ["keyword", "score", "document_count"]
DOCUMENT_KEYWORD_COLUMNS = [
    "document_id",
    "source_name",
    "category",
    "language",
    "keyword",
    "score",
    "rank",
]


def _get_texts(documents_df: pd.DataFrame, text_column: str) -> list[str]:
    if documents_df is None or documents_df.empty or text_column not in documents_df.columns:
        return []
    return documents_df[text_column].fillna("").astype(str).tolist()


def _build_keyword_matrix(documents_df: pd.DataFrame, text_column: str):
    texts = _get_texts(documents_df, text_column)
    if not any(text.strip() for text in texts):
        return None, None

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        max_features=10000,
    )
    try:
        matrix = vectorizer.fit_transform(texts)
    except ValueError:
        return None, None

    return vectorizer, matrix


def extract_corpus_keywords(
    documents_df: pd.DataFrame,
    top_n: int = 25,
    text_column: str = "search_text",
) -> pd.DataFrame:
    """Return top corpus-level TF-IDF keywords and keyphrases."""
    vectorizer, matrix = _build_keyword_matrix(documents_df, text_column)
    if vectorizer is None or matrix is None:
        return pd.DataFrame(columns=CORPUS_KEYWORD_COLUMNS)

    feature_names = vectorizer.get_feature_names_out()
    scores = matrix.sum(axis=0).A1
    document_counts = (matrix > 0).sum(axis=0).A1

    rows = [
        {
            "keyword": feature_names[index],
            "score": round(float(scores[index]), 6),
            "document_count": int(document_counts[index]),
        }
        for index in range(len(feature_names))
    ]

    if not rows:
        return pd.DataFrame(columns=CORPUS_KEYWORD_COLUMNS)

    return (
        pd.DataFrame(rows)
        .sort_values(["score", "document_count", "keyword"], ascending=[False, False, True])
        .head(top_n)
        .reset_index(drop=True)
    )


def extract_document_keywords(
    documents_df: pd.DataFrame,
    top_n: int = 10,
    text_column: str = "search_text",
) -> pd.DataFrame:
    """Return top TF-IDF keywords/keyphrases for each document."""
    vectorizer, matrix = _build_keyword_matrix(documents_df, text_column)
    if vectorizer is None or matrix is None:
        return pd.DataFrame(columns=DOCUMENT_KEYWORD_COLUMNS)

    feature_names = vectorizer.get_feature_names_out()
    rows = []

    for row_index, (_, document) in enumerate(documents_df.reset_index(drop=True).iterrows()):
        row = matrix.getrow(row_index)
        if row.nnz == 0:
            continue

        ranked = sorted(
            zip(row.indices, row.data, strict=False),
            key=lambda item: (-float(item[1]), feature_names[item[0]]),
        )[:top_n]

        for rank, (feature_index, score) in enumerate(ranked, start=1):
            rows.append(
                {
                    "document_id": document.get("id", ""),
                    "source_name": document.get("source_name", ""),
                    "category": document.get("category", ""),
                    "language": document.get("language", ""),
                    "keyword": feature_names[feature_index],
                    "score": round(float(score), 6),
                    "rank": rank,
                }
            )

    if not rows:
        return pd.DataFrame(columns=DOCUMENT_KEYWORD_COLUMNS)

    return pd.DataFrame(rows, columns=DOCUMENT_KEYWORD_COLUMNS)
