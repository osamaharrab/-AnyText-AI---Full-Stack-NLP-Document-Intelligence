"""Entity analytics for the AnyText AI dashboard."""

from __future__ import annotations

from itertools import combinations

import pandas as pd


def compute_top_entities(entity_df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Return the most frequent entity strings and labels."""
    if entity_df is None or entity_df.empty:
        return pd.DataFrame(columns=["entity_text", "label", "count", "document_count"])

    grouped = (
        entity_df.groupby(["entity_text", "label"], dropna=False)
        .agg(count=("entity_text", "size"), document_count=("document_id", "nunique"))
        .reset_index()
        .sort_values(["count", "document_count", "entity_text"], ascending=[False, False, True])
        .head(n)
    )
    return grouped.reset_index(drop=True)


def compute_label_counts(entity_df: pd.DataFrame) -> pd.DataFrame:
    """Count entity mentions by spaCy label."""
    if entity_df is None or entity_df.empty:
        return pd.DataFrame(columns=["label", "count"])

    return (
        entity_df.groupby("label", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )


def compute_co_occurrence(entity_df: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
    """Compute entity co-occurrence pairs, counting each entity once per document."""
    if entity_df is None or entity_df.empty:
        return pd.DataFrame(columns=["entity_1", "entity_2", "cooccurrence_count"])

    doc_entity_counts = (
        entity_df.drop_duplicates(["document_id", "entity_text"])
        .groupby("entity_text")["document_id"]
        .nunique()
        .sort_values(ascending=False)
    )
    top_entities = set(doc_entity_counts.head(top_n).index)

    pair_counts: dict[tuple[str, str], int] = {}
    for _, group in entity_df.groupby("document_id"):
        unique_entities = sorted(set(group["entity_text"].dropna()) & top_entities)
        for entity_1, entity_2 in combinations(unique_entities, 2):
            pair_counts[(entity_1, entity_2)] = pair_counts.get((entity_1, entity_2), 0) + 1

    rows = [
        {"entity_1": pair[0], "entity_2": pair[1], "cooccurrence_count": count}
        for pair, count in pair_counts.items()
    ]
    if not rows:
        return pd.DataFrame(columns=["entity_1", "entity_2", "cooccurrence_count"])

    return (
        pd.DataFrame(rows)
        .sort_values(["cooccurrence_count", "entity_1", "entity_2"], ascending=[False, True, True])
        .reset_index(drop=True)
    )


def compute_cross_category_patterns(entity_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize entity-label patterns across document categories."""
    if entity_df is None or entity_df.empty:
        return pd.DataFrame(columns=["category", "label", "entity_mentions", "unique_entities"])

    return (
        entity_df.groupby(["category", "label"], dropna=False)
        .agg(
            entity_mentions=("entity_text", "size"),
            unique_entities=("entity_text", "nunique"),
            documents=("document_id", "nunique"),
        )
        .reset_index()
        .sort_values(["category", "entity_mentions"], ascending=[True, False])
        .reset_index(drop=True)
    )


def aggregate_entity_stats(entity_df: pd.DataFrame, top_n: int = 20) -> dict:
    """Build the analytics bundle used by the app and report generator."""
    top_entities = compute_top_entities(entity_df, n=top_n)
    label_counts = compute_label_counts(entity_df)
    co_occurrence = compute_co_occurrence(entity_df, top_n=50)
    cross_category = compute_cross_category_patterns(entity_df)

    if entity_df is None or entity_df.empty:
        total_entities = 0
        unique_entities = 0
        documents_with_entities = 0
    else:
        total_entities = int(len(entity_df))
        unique_entities = int(entity_df["entity_text"].nunique())
        documents_with_entities = int(entity_df["document_id"].nunique())

    return {
        "total_entities": total_entities,
        "unique_entities": unique_entities,
        "documents_with_entities": documents_with_entities,
        "top_entities": top_entities,
        "label_counts": label_counts,
        "co_occurrence": co_occurrence,
        "cross_category": cross_category,
    }
