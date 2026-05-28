"""Entity and document drilldown helpers."""

from __future__ import annotations

import re

import pandas as pd


ENTITY_CONTEXT_COLUMNS = [
    "document_id",
    "source_name",
    "category",
    "language",
    "labels",
    "mention_count",
    "context",
]


def _compact_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _make_context(text: str, entity: str, start_char=None, end_char=None, window: int = 120) -> str:
    raw_text = str(text or "")
    start = None
    end = None

    if start_char is not None and end_char is not None:
        try:
            start = int(start_char)
            end = int(end_char)
        except (TypeError, ValueError):
            start = None
            end = None

    if start is None or end is None or start < 0 or end <= start or start >= len(raw_text):
        match = re.search(re.escape(str(entity)), raw_text, flags=re.IGNORECASE)
        if match:
            start, end = match.span()

    if start is None or end is None:
        return _compact_text(raw_text[: window * 2])

    left = max(0, start - window)
    right = min(len(raw_text), end + window)
    prefix = "..." if left > 0 else ""
    suffix = "..." if right < len(raw_text) else ""
    return prefix + _compact_text(raw_text[left:right]) + suffix


def get_entity_contexts(
    documents_df: pd.DataFrame,
    entities_df: pd.DataFrame,
    selected_entity: str,
    window: int = 120,
) -> pd.DataFrame:
    """Return document-level contexts for one selected entity."""
    if (
        documents_df is None
        or documents_df.empty
        or entities_df is None
        or entities_df.empty
        or not selected_entity
    ):
        return pd.DataFrame(columns=ENTITY_CONTEXT_COLUMNS)

    matches = entities_df[entities_df["entity_text"].astype(str) == str(selected_entity)].copy()
    if matches.empty:
        return pd.DataFrame(columns=ENTITY_CONTEXT_COLUMNS)

    documents = documents_df.copy()
    if "id" not in documents.columns:
        return pd.DataFrame(columns=ENTITY_CONTEXT_COLUMNS)

    document_lookup = documents.set_index("id", drop=False)
    rows = []

    for document_id, group in matches.groupby("document_id", dropna=False):
        if document_id not in document_lookup.index:
            continue

        document = document_lookup.loc[document_id]
        if isinstance(document, pd.DataFrame):
            document = document.iloc[0]

        first_mention = group.iloc[0]
        context = _make_context(
            document.get("text", ""),
            selected_entity,
            first_mention.get("start_char"),
            first_mention.get("end_char"),
            window=window,
        )

        rows.append(
            {
                "document_id": document_id,
                "source_name": document.get("source_name", ""),
                "category": document.get("category", ""),
                "language": document.get("language", ""),
                "labels": ", ".join(sorted(group["label"].dropna().astype(str).unique())),
                "mention_count": int(len(group)),
                "context": context,
            }
        )

    if not rows:
        return pd.DataFrame(columns=ENTITY_CONTEXT_COLUMNS)

    return (
        pd.DataFrame(rows, columns=ENTITY_CONTEXT_COLUMNS)
        .sort_values(["mention_count", "source_name"], ascending=[False, True])
        .reset_index(drop=True)
    )
