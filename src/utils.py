"""Small UI and data utility helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to UTF-8 CSV bytes for in-memory downloads."""
    if df is None:
        df = pd.DataFrame()
    return df.to_csv(index=False).encode("utf-8")


def markdown_to_bytes(markdown: str) -> bytes:
    """Convert markdown text to UTF-8 bytes for in-memory downloads."""
    return (markdown or "").encode("utf-8")


def dict_to_json_bytes(data: dict) -> bytes:
    """Convert a dictionary to pretty UTF-8 JSON bytes for in-memory downloads."""
    return json.dumps(data or {}, ensure_ascii=False, indent=2, default=str).encode("utf-8")


def shorten_identifier(value, prefix_chars: int = 3, max_chars: int = 10) -> str:
    """Shorten generated identifiers for display while preserving recognizable prefixes."""
    text = str(value or "").strip()
    if len(text) <= max_chars:
        return text or "Unknown"

    if "_" in text:
        prefix, suffix = text.split("_", 1)
        if prefix and suffix:
            return f"{prefix}_{suffix[:prefix_chars]}…"

    return text[: max(max_chars - 1, 1)] + "…"


def shorten_filename(value, max_chars: int = 28) -> str:
    """Shorten long filenames for compact UI display while keeping extensions visible."""
    text = str(value or "").strip()
    if len(text) <= max_chars:
        return text or "Unknown"

    suffix = Path(text).suffix
    if suffix and len(suffix) < max_chars - 4:
        keep = max_chars - len(suffix) - 1
        return f"{text[:keep]}…{suffix}"

    keep_start = max((max_chars - 1) // 2, 1)
    keep_end = max(max_chars - keep_start - 1, 1)
    return f"{text[:keep_start]}…{text[-keep_end:]}"


def display_unknown(value) -> str:
    """Return a clean UI label for missing or unknown values."""
    text = str(value or "").strip()
    if not text or text.lower() in {"unknown", "none", "nan", "null"}:
        return "Unknown"
    return text


def metric_value(value) -> str:
    """Format large integer-like values for Streamlit metric cards."""
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)
