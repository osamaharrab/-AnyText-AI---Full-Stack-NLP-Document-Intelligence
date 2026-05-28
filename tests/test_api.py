from __future__ import annotations

import spacy
from spacy.pipeline import EntityRuler

from api import services
from api.main import health, sample_endpoint


def _ruler_nlp():
    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")
    assert isinstance(ruler, EntityRuler)
    ruler.add_patterns(
        [
            {"label": "ORG", "pattern": "Apple"},
            {"label": "ORG", "pattern": "Microsoft"},
            {"label": "ORG", "pattern": "Google"},
            {"label": "ORG", "pattern": "United Nations"},
            {"label": "ORG", "pattern": "World Health Organization"},
            {"label": "GPE", "pattern": "Jordan"},
            {"label": "GPE", "pattern": "Amman"},
            {"label": "GPE", "pattern": "London"},
        ]
    )
    return nlp


def test_health_endpoint():
    assert health()["status"] == "ok"


def test_sample_endpoint_returns_analysis_bundle(monkeypatch):
    monkeypatch.setattr(services, "load_spacy_model", _ruler_nlp)

    payload = sample_endpoint()

    assert payload["corpus_stats"]["document_count"] >= 20
    assert payload["documents"]
    assert payload["top_entities"]
    assert payload["keywords"]
    assert "NLP Analysis Report" in payload["report_markdown"]
