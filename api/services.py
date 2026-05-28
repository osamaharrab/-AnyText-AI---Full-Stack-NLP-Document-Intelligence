"""Stateless services that adapt the existing NLP modules for the API."""

from __future__ import annotations

import json
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from src.analytics import aggregate_entity_stats
from src.document_qa import ask_documents
from src.input_loader import (
    load_csv_file,
    load_docx_file,
    load_manual_text,
    load_pdf_file,
    load_txt_file,
)
from src.keywords import extract_corpus_keywords, extract_document_keywords
from src.ner import get_entity_label_descriptions, load_spacy_model, run_spacy_ner
from src.preprocessing import prepare_documents
from src.report import generate_report
from src.search import build_tfidf_index, search_documents


APP_DIR = Path(__file__).resolve().parents[1]
SAMPLE_DATA_PATH = APP_DIR / "data" / "sample_text_corpus.csv"


@dataclass
class InMemoryUpload:
    """Small adapter matching the loader interface used by Streamlit uploads."""

    name: str
    data: bytes

    def __post_init__(self) -> None:
        self._buffer = BytesIO(self.data)

    def read(self) -> bytes:
        return self._buffer.read()

    def seek(self, position: int) -> None:
        self._buffer.seek(position)


def _records(df: pd.DataFrame | None) -> list[dict[str, Any]]:
    """Return JSON-safe dataframe records."""
    if df is None or df.empty:
        return []
    return json.loads(df.to_json(orient="records", force_ascii=False))


def _value_counts(df: pd.DataFrame, column: str, count_name: str = "documents") -> list[dict[str, Any]]:
    if df is None or df.empty or column not in df.columns:
        return []
    counts = (
        df[column]
        .fillna("unknown")
        .astype(str)
        .value_counts()
        .rename_axis(column)
        .reset_index(name=count_name)
    )
    return _records(counts)


def _analysis_metadata(warnings: Iterable[str] | None = None) -> dict[str, Any]:
    return {
        "ner_model": "en_core_web_sm",
        "keyword_method": "TF-IDF with unigrams and bigrams",
        "search_method": "TF-IDF cosine similarity",
        "privacy": "Processed in memory. The API does not persist uploaded content.",
        "warnings": list(warnings or []),
    }


def _corpus_stats(document_df: pd.DataFrame) -> dict[str, Any]:
    if document_df is None or document_df.empty:
        return {
            "document_count": 0,
            "total_characters": 0,
            "average_text_length": 0,
            "language_count": 0,
            "category_count": 0,
            "language_distribution": [],
            "category_distribution": [],
        }

    total_characters = int(document_df.get("text_length", pd.Series(dtype=int)).sum())
    return {
        "document_count": int(len(document_df)),
        "total_characters": total_characters,
        "average_text_length": round(float(document_df["text_length"].mean()), 2),
        "language_count": int(document_df["language"].nunique()),
        "category_count": int(document_df["category"].nunique()),
        "language_distribution": _value_counts(document_df, "language"),
        "category_distribution": _value_counts(document_df, "category"),
    }


def _stats_for_report(stats: dict[str, Any], keyword_df: pd.DataFrame) -> dict[str, Any]:
    report_stats = dict(stats)
    report_stats["keywords"] = keyword_df
    return report_stats


def analyze_documents(
    document_df: pd.DataFrame,
    *,
    top_n: int = 20,
    warnings: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Run the existing preparation, NER, keyword, analytics, search, and report flow."""
    prepared_df = prepare_documents(document_df)
    if prepared_df.empty or not prepared_df["normalized_text"].str.strip().any():
        raise ValueError("No non-empty text is available for analysis.")

    nlp = load_spacy_model()
    entity_df = run_spacy_ner(prepared_df, nlp, text_column="normalized_text")
    keyword_df = extract_corpus_keywords(prepared_df, top_n=top_n)
    document_keyword_df = extract_document_keywords(prepared_df, top_n=10)
    stats = aggregate_entity_stats(entity_df, top_n=top_n)
    report_markdown = generate_report(_stats_for_report(stats, keyword_df), prepared_df)

    vectorizer, matrix = build_tfidf_index(prepared_df)

    return {
        "documents": _records(prepared_df),
        "corpus_stats": _corpus_stats(prepared_df),
        "entity_mentions": _records(entity_df),
        "entities": {
            "total_mentions": int(stats.get("total_entities", 0)),
            "unique_entities": int(stats.get("unique_entities", 0)),
            "documents_with_entities": int(stats.get("documents_with_entities", 0)),
            "label_descriptions": get_entity_label_descriptions(),
        },
        "top_entities": _records(stats.get("top_entities")),
        "entity_label_counts": _records(stats.get("label_counts")),
        "keywords": _records(keyword_df),
        "document_keywords": _records(document_keyword_df),
        "co_occurrence": _records(stats.get("co_occurrence")),
        "cross_category_patterns": _records(stats.get("cross_category")),
        "report_markdown": report_markdown,
        "search_results": [],
        "search_ready": vectorizer is not None and matrix is not None,
        "metadata": _analysis_metadata(warnings),
    }


def analyze_text(text: str, *, category: str = "manual", top_n: int = 20) -> dict[str, Any]:
    frame = load_manual_text(text, category=category)
    if frame.empty:
        raise ValueError("Paste non-empty text before running analysis.")
    return analyze_documents(frame, top_n=top_n)


def analyze_sample_corpus(*, top_n: int = 20) -> dict[str, Any]:
    if not SAMPLE_DATA_PATH.exists():
        raise FileNotFoundError(f"Sample corpus not found: {SAMPLE_DATA_PATH}")
    return analyze_documents(pd.read_csv(SAMPLE_DATA_PATH), top_n=top_n)


def load_uploads(
    uploads: Iterable[InMemoryUpload],
    *,
    category: str = "unknown",
    split_pdf_pages: bool = False,
    csv_text_col: str | None = None,
    csv_id_col: str | None = None,
    csv_language_col: str | None = None,
    csv_category_col: str | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    """Load FastAPI uploads with the existing file loader functions."""
    frames: list[pd.DataFrame] = []
    warnings: list[str] = []

    for upload in uploads:
        source_name = upload.name or "uploaded_file"
        extension = Path(source_name).suffix.lower()

        try:
            if extension == ".txt":
                frame = load_txt_file(upload, category=category)
            elif extension == ".csv":
                frame = load_csv_file(
                    upload,
                    text_col=csv_text_col,
                    id_col=csv_id_col,
                    language_col=csv_language_col,
                    category_col=csv_category_col,
                    default_category=category,
                )
            elif extension == ".pdf":
                frame, warning = load_pdf_file(upload, category=category, split_pages=split_pdf_pages)
                if warning:
                    warnings.append(warning)
            elif extension == ".docx":
                frame = load_docx_file(upload, category=category)
            else:
                warnings.append(f"Unsupported file type for {source_name}.")
                continue

            if frame.empty:
                warnings.append(f"No usable text found in {source_name}.")
            else:
                frames.append(frame)
        except Exception as exc:
            warnings.append(f"Could not process {source_name}: {exc}")

    if not frames:
        return pd.DataFrame(), warnings

    return pd.concat(frames, ignore_index=True), warnings


def analyze_uploads(
    uploads: Iterable[InMemoryUpload],
    *,
    category: str = "unknown",
    top_n: int = 20,
    split_pdf_pages: bool = False,
    csv_text_col: str | None = None,
    csv_id_col: str | None = None,
    csv_language_col: str | None = None,
    csv_category_col: str | None = None,
) -> dict[str, Any]:
    frame, warnings = load_uploads(
        uploads,
        category=category,
        split_pdf_pages=split_pdf_pages,
        csv_text_col=csv_text_col,
        csv_id_col=csv_id_col,
        csv_language_col=csv_language_col,
        csv_category_col=csv_category_col,
    )
    if frame.empty:
        detail = "No usable documents were found in the uploaded files."
        if warnings:
            detail = f"{detail} {' '.join(warnings)}"
        raise ValueError(detail)
    return analyze_documents(frame, top_n=top_n, warnings=warnings)


def search_analysis_documents(
    query: str,
    documents: list[dict[str, Any]],
    *,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    if not documents:
        raise ValueError("Search requires analyzed documents.")

    document_df = prepare_documents(pd.DataFrame(documents))
    vectorizer, matrix = build_tfidf_index(document_df)
    results = search_documents(query, document_df, vectorizer, matrix, top_k=top_k)
    return _records(results)


def ask_analysis_documents(
    question: str,
    documents: list[dict[str, Any]],
    *,
    document_id: str | None = None,
    top_k: int = 5,
) -> dict[str, Any]:
    return ask_documents(question, documents, document_id=document_id, top_k=top_k)


def report_export(analysis: dict[str, Any]) -> dict[str, Any]:
    report = str(analysis.get("report_markdown") or "")
    if not report:
        documents = pd.DataFrame(analysis.get("documents") or [])
        keyword_df = pd.DataFrame(analysis.get("keywords") or [])
        stats = {
            "total_entities": analysis.get("entities", {}).get("total_mentions", 0),
            "unique_entities": analysis.get("entities", {}).get("unique_entities", 0),
            "documents_with_entities": analysis.get("entities", {}).get("documents_with_entities", 0),
            "label_counts": pd.DataFrame(analysis.get("entity_label_counts") or []),
            "top_entities": pd.DataFrame(analysis.get("top_entities") or []),
            "co_occurrence": pd.DataFrame(analysis.get("co_occurrence") or []),
            "cross_category": pd.DataFrame(analysis.get("cross_category_patterns") or []),
            "keywords": keyword_df,
        }
        report = generate_report(stats, documents)

    return {
        "filename": "nlp_analysis_report.md",
        "mime_type": "text/markdown",
        "content": report,
    }


def json_export(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "filename": "full_analysis_export.json",
        "mime_type": "application/json",
        "content": analysis,
    }
