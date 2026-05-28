"""Text normalization and corpus preparation utilities."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

import pandas as pd
from langdetect import detect


REQUIRED_COLUMNS = ["id", "source_name", "text", "language", "category"]


def normalize_unicode(text: Any) -> str:
    """Normalize text to NFC while preserving original content as much as possible."""
    if text is None:
        return ""
    return unicodedata.normalize("NFC", str(text))


def detect_language_simple(text: Any) -> str:
    """Detect a short ISO-like language code, falling back to English on errors."""
    try:
        value = normalize_unicode(text).strip()
        if len(value) < 3:
            return "en"
        return detect(value)
    except Exception:
        return "en"


def preprocess_for_search(text: Any) -> str:
    """Prepare text for TF-IDF search only."""
    value = normalize_unicode(text).lower()
    value = re.sub(r"[^\w\s]", " ", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value, flags=re.UNICODE).strip()
    return value


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if pd.isna(value):
        return True
    return str(value).strip() == ""


def prepare_documents(df: pd.DataFrame) -> pd.DataFrame:
    """Return a standardized document DataFrame ready for analytics and search."""
    prepared = df.copy() if df is not None else pd.DataFrame()

    for column in REQUIRED_COLUMNS:
        if column not in prepared.columns:
            prepared[column] = None

    prepared["text"] = prepared["text"].fillna("").astype(str)

    missing_ids = prepared["id"].apply(_is_missing)
    prepared.loc[missing_ids, "id"] = [
        f"doc_{idx + 1:04d}" for idx in range(int(missing_ids.sum()))
    ]
    prepared["id"] = prepared["id"].astype(str)

    prepared["source_name"] = prepared["source_name"].fillna("unknown_source").astype(str)
    prepared.loc[prepared["source_name"].str.strip() == "", "source_name"] = "unknown_source"

    prepared["category"] = prepared["category"].fillna("unknown").astype(str)
    prepared.loc[prepared["category"].str.strip() == "", "category"] = "unknown"

    missing_language = prepared["language"].apply(_is_missing)
    prepared.loc[missing_language, "language"] = prepared.loc[missing_language, "text"].apply(
        detect_language_simple
    )
    prepared["language"] = prepared["language"].fillna("en").astype(str)

    prepared["normalized_text"] = prepared["text"].apply(normalize_unicode)

    # NER must run on raw or normalized text, NOT on search_text.
    # Lowercasing breaks entity detection: "Apple" (ORG) becomes "apple" (fruit).
    # Removing punctuation breaks "U.K." and "U.S.A." spans.
    prepared["search_text"] = prepared["normalized_text"].apply(preprocess_for_search)
    prepared["text_length"] = prepared["text"].str.len()

    ordered = REQUIRED_COLUMNS + ["normalized_text", "search_text", "text_length"]
    extra_columns = [column for column in prepared.columns if column not in ordered]
    return prepared[ordered + extra_columns]
