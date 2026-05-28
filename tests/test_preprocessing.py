from __future__ import annotations

import unicodedata

import pandas as pd

from src.preprocessing import detect_language_simple, normalize_unicode, prepare_documents, preprocess_for_search


def test_normalize_unicode_uses_nfc():
    decomposed = "Cafe\u0301"

    normalized = normalize_unicode(decomposed)

    assert normalized == unicodedata.normalize("NFC", decomposed)


def test_detect_language_simple_falls_back_and_detects_english():
    assert detect_language_simple("") == "en"
    assert detect_language_simple("This is a clear English sentence about London.") == "en"


def test_preprocess_for_search_lowercases_and_removes_punctuation():
    text = "Apple, Microsoft & the U.K. signed a 2024 deal!"

    assert preprocess_for_search(text) == "apple microsoft the u k signed a 2024 deal"


def test_prepare_documents_adds_required_derived_columns():
    frame = pd.DataFrame({"text": ["Apple works in London."], "category": ["technology"]})

    prepared = prepare_documents(frame)

    assert {"id", "source_name", "language", "normalized_text", "search_text", "text_length"}.issubset(
        prepared.columns
    )
    assert prepared.iloc[0]["text"] == "Apple works in London."
    assert prepared.iloc[0]["search_text"] == "apple works in london"
