from __future__ import annotations

import json

from src.utils import dict_to_json_bytes, display_unknown, shorten_filename, shorten_identifier


def test_dict_to_json_bytes_returns_valid_utf8_json():
    payload = dict_to_json_bytes({"name": "AnyText AI", "count": 2})

    assert isinstance(payload, bytes)
    assert json.loads(payload.decode("utf-8"))["count"] == 2


def test_shorten_identifier_keeps_generated_prefix():
    assert shorten_identifier("docx_acbaeb690", prefix_chars=3) == "docx_acb…"
    assert shorten_identifier("pdf_45e04db9", prefix_chars=3) == "pdf_45e…"


def test_shorten_filename_keeps_extension_visible():
    shortened = shorten_filename("very_long_private_document_name_for_demo.pdf", max_chars=22)

    assert shortened.endswith(".pdf")
    assert "…" in shortened


def test_display_unknown_formats_missing_values():
    assert display_unknown("unknown") == "Unknown"
    assert display_unknown("") == "Unknown"
    assert display_unknown("business") == "business"
