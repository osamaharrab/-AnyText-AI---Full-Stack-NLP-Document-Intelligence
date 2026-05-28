"""Markdown report generation for AnyText AI."""

from __future__ import annotations

import pandas as pd


def _markdown_table(df: pd.DataFrame, columns: list[str], limit: int | None = None) -> str:
    if df is None or df.empty:
        return "_No data available._"
    view = df.loc[:, [column for column in columns if column in df.columns]].copy()
    if limit is not None:
        view = view.head(limit)
    if view.empty:
        return "_No data available._"

    def clean(value) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    header = "| " + " | ".join(clean(column) for column in view.columns) + " |"
    separator = "| " + " | ".join("---" for _ in view.columns) + " |"
    rows = [
        "| " + " | ".join(clean(row[column]) for column in view.columns) + " |"
        for _, row in view.iterrows()
    ]
    return "\n".join([header, separator] + rows)


def _value_counts_table(document_df: pd.DataFrame, column: str, count_name: str = "documents") -> pd.DataFrame:
    if document_df is None or document_df.empty or column not in document_df.columns:
        return pd.DataFrame(columns=[column, count_name])
    return (
        document_df[column]
        .fillna("unknown")
        .astype(str)
        .value_counts()
        .rename_axis(column)
        .reset_index(name=count_name)
    )


def generate_report(stats: dict, document_df: pd.DataFrame) -> str:
    """Generate a professional markdown report string without writing to disk."""
    stats = stats or {}
    document_df = document_df if document_df is not None else pd.DataFrame()

    total_docs = int(len(document_df))
    total_chars = int(document_df.get("text_length", pd.Series(dtype=int)).sum())
    categories = (
        ", ".join(sorted(document_df.get("category", pd.Series(dtype=str)).dropna().unique()))
        if not document_df.empty
        else "None"
    )
    languages = (
        ", ".join(sorted(document_df.get("language", pd.Series(dtype=str)).dropna().unique()))
        if not document_df.empty
        else "None"
    )

    label_counts = stats.get("label_counts", pd.DataFrame())
    top_entities = stats.get("top_entities", pd.DataFrame())
    co_occurrence = stats.get("co_occurrence", pd.DataFrame())
    cross_category = stats.get("cross_category", pd.DataFrame())
    keywords = stats.get("keywords", pd.DataFrame())
    language_distribution = _value_counts_table(document_df, "language")
    category_distribution = _value_counts_table(document_df, "category")

    top_category_lines = []
    if cross_category is not None and not cross_category.empty:
        for category, group in cross_category.groupby("category"):
            leader = group.sort_values("entity_mentions", ascending=False).iloc[0]
            top_category_lines.append(
                f"- **{category}** is led by `{leader['label']}` entities "
                f"with {int(leader['entity_mentions'])} mentions."
            )
    cross_category_summary = "\n".join(top_category_lines) or "_No category patterns available._"

    interpretation = (
        "The corpus contains a measurable entity signal that can support document triage, "
        "topic exploration, and lightweight knowledge discovery. Entity frequency highlights "
        "the most visible organizations, people, places, dates, and quantities, while "
        "co-occurrence patterns show which concepts tend to appear in the same document context."
        if stats.get("total_entities", 0)
        else "No English named entities were detected. This can happen when documents are short, "
        "non-English, scanned PDFs without extractable text, or outside the coverage of the "
        "default English spaCy model."
    )

    return f"""# NLP Analysis Report

## Corpus Summary

| Metric | Value |
|---|---:|
| Documents | {total_docs} |
| Total characters | {total_chars} |
| Languages | {languages} |
| Categories | {categories} |
| Entity mentions | {int(stats.get("total_entities", 0))} |
| Unique entities | {int(stats.get("unique_entities", 0))} |
| Documents with entities | {int(stats.get("documents_with_entities", 0))} |

## Language Distribution

{_markdown_table(language_distribution, ["language", "documents"])}

## Category Distribution

{_markdown_table(category_distribution, ["category", "documents"])}

## Top Entity Labels

{_markdown_table(label_counts, ["label", "count"])}

## Top 5 Entities

{_markdown_table(top_entities, ["entity_text", "label", "count", "document_count"], limit=5)}

## Top Keywords

{_markdown_table(keywords, ["keyword", "score", "document_count"], limit=10)}

## Top 3 Co-occurring Pairs

{_markdown_table(co_occurrence, ["entity_1", "entity_2", "cooccurrence_count"], limit=3)}

## Cross-category Findings

{cross_category_summary}

## Interpretation

{interpretation}

## Suggested Use Cases

- Rapid review of mixed document collections.
- Entity-based exploration for business, policy, research, and operations teams.
- Discovery of recurring organizations, locations, dates, amounts, and relationships.
- Searchable NLP summaries for portfolio demos, internal reports, and lightweight audits.

## Limitations

- English-first spaCy NER is used for named entity detection.
- The small spaCy model is lightweight and CPU-friendly, but entity labels may be imperfect.
- PDF extraction works only for embedded text, not scanned PDFs.
- TF-IDF search is keyword-based, not true semantic search.
- Entity labels and extracted insights require human review for high-stakes use.
"""
