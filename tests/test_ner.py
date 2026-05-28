from __future__ import annotations

import pandas as pd
import spacy
from spacy.pipeline import EntityRuler

from src.ner import run_spacy_ner
from src.preprocessing import prepare_documents


def _ruler_nlp():
    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")
    assert isinstance(ruler, EntityRuler)
    ruler.add_patterns(
        [
            {"label": "ORG", "pattern": "Apple Inc."},
            {"label": "PERSON", "pattern": "Steve Jobs"},
            {"label": "GPE", "pattern": "Cupertino"},
            {"label": "GPE", "pattern": "California"},
            {"label": "DATE", "pattern": "1976"},
            {"label": "ORG", "pattern": "iPhone"},
            {"label": "MONEY", "pattern": "over $3 trillion"},
            {"label": "ORG", "pattern": "The United Nations"},
        ]
    )
    return nlp


def test_run_spacy_ner_falls_back_when_language_filter_has_no_english_rows():
    frame = prepare_documents(
        pd.DataFrame(
            [
                {
                    "id": "d1",
                    "source_name": "manual_input",
                    "text": "Apple Inc. was founded by Steve Jobs in Cupertino.",
                    "language": "zz",
                    "category": "manual",
                }
            ]
        )
    )

    entities = run_spacy_ner(frame, _ruler_nlp(), text_column="normalized_text")

    assert set(entities["entity_text"]) >= {"Apple Inc.", "Steve Jobs", "Cupertino"}


def test_run_spacy_ner_cleans_common_spacy_small_model_spans():
    frame = prepare_documents(
        pd.DataFrame(
            [
                {
                    "id": "d1",
                    "source_name": "manual_input",
                    "text": (
                        "The company launched the iPhone and is now worth over $3 trillion. "
                        "The United Nations held a summit."
                    ),
                    "language": "en",
                    "category": "manual",
                }
            ]
        )
    )

    entities = run_spacy_ner(frame, _ruler_nlp(), text_column="normalized_text")
    labels = dict(zip(entities["entity_text"], entities["label"], strict=False))

    assert labels["iPhone"] == "PRODUCT"
    assert labels["$3 trillion"] == "MONEY"
    assert labels["United Nations"] == "ORG"
