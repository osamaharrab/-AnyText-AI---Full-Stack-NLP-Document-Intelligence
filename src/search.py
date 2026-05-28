"""TF-IDF document search helpers."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocessing import preprocess_for_search


RESULT_COLUMNS = [
    "id",
    "source_name",
    "category",
    "language",
    "text_preview",
    "similarity_score",
]


@st.cache_data(show_spinner=False)
def build_tfidf_index(df: pd.DataFrame, text_column: str = "search_text"):
    """Build and cache a TF-IDF vectorizer and sparse document matrix."""
    if df is None or df.empty or text_column not in df.columns:
        return None, None

    texts = df[text_column].fillna("").astype(str).tolist()
    if not any(text.strip() for text in texts):
        return None, None

    vectorizer = TfidfVectorizer(max_features=20000, ngram_range=(1, 2), min_df=1)
    try:
        matrix = vectorizer.fit_transform(texts)
    except ValueError:
        return None, None

    return vectorizer, matrix


def search_documents(
    query: str,
    df: pd.DataFrame,
    vectorizer,
    matrix,
    top_k: int = 5,
) -> pd.DataFrame:
    """Search prepared documents with cosine similarity over TF-IDF vectors."""
    if (
        not query
        or df is None
        or df.empty
        or vectorizer is None
        or matrix is None
    ):
        return pd.DataFrame(columns=RESULT_COLUMNS)

    query_text = preprocess_for_search(query)
    if not query_text:
        return pd.DataFrame(columns=RESULT_COLUMNS)

    query_vector = vectorizer.transform([query_text])
    similarities = cosine_similarity(query_vector, matrix).ravel()
    top_indices = similarities.argsort()[::-1][:top_k]

    rows = []
    for index in top_indices:
        score = float(similarities[index])
        if score <= 0:
            continue
        document = df.iloc[index]
        preview = " ".join(str(document.get("text", "")).split())[:320]
        rows.append(
            {
                "id": document.get("id", ""),
                "source_name": document.get("source_name", ""),
                "category": document.get("category", ""),
                "language": document.get("language", ""),
                "text_preview": preview,
                "similarity_score": round(score, 4),
            }
        )

    return pd.DataFrame(rows, columns=RESULT_COLUMNS)
