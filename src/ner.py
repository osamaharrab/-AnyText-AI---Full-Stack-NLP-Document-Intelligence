"""Named Entity Recognition helpers built around spaCy."""

from __future__ import annotations

import pandas as pd
import streamlit as st


SPACY_MODEL_WHEEL = (
    "https://github.com/explosion/spacy-models/releases/download/"
    "en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl"
)
PRODUCT_OVERRIDES = {
    "iphone",
    "ipad",
    "macbook",
    "apple watch",
    "windows",
    "xbox",
}

ENTITY_COLUMNS = [
    "document_id",
    "source_name",
    "category",
    "language",
    "entity_text",
    "label",
    "start_char",
    "end_char",
    "sentence",
]


@st.cache_resource
def load_spacy_model(model_name: str = "en_core_web_sm"):
    """Load the English spaCy model, downloading it at runtime when needed."""
    if model_name != "en_core_web_sm":
        import spacy

        return spacy.load(model_name)

    import subprocess
    import sys

    try:
        import en_core_web_sm

        return en_core_web_sm.load()
    except ImportError:
        try:
            subprocess.run(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                check=True,
            )
        except subprocess.CalledProcessError:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", SPACY_MODEL_WHEEL],
                check=True,
            )
        import en_core_web_sm

        return en_core_web_sm.load()


def _empty_entities() -> pd.DataFrame:
    return pd.DataFrame(columns=ENTITY_COLUMNS)


def _clean_entity(entity) -> tuple[str, str, int, int]:
    text = entity.text.strip()
    label = entity.label_
    start_char = entity.start_char
    end_char = entity.end_char

    lower_text = text.lower()
    if label == "ORG" and lower_text.startswith("the "):
        text = text[4:].strip()
        start_char += 4
        lower_text = text.lower()

    for prefix in ("over ", "about ", "around ", "approximately "):
        if label == "MONEY" and lower_text.startswith(prefix):
            text = text[len(prefix) :].strip()
            start_char += len(prefix)
            lower_text = text.lower()
            break

    if lower_text in PRODUCT_OVERRIDES:
        label = "PRODUCT"

    return text, label, start_char, end_char


def _safe_sentence(entity) -> str:
    try:
        return entity.sent.text.strip() if entity.sent else ""
    except ValueError:
        return ""


def run_spacy_ner(df: pd.DataFrame, nlp, text_column: str = "text") -> pd.DataFrame:
    """Run spaCy NER and return one row per entity mention.

    English rows are preferred when reliable language metadata is present. If the
    language column is missing, empty, or filters out every document, the function
    falls back to all rows so NER does not silently skip a valid corpus.
    """
    if df is None or df.empty:
        return _empty_entities()

    working_df = df.copy()
    if text_column not in working_df.columns:
        if "text" in working_df.columns:
            text_column = "text"
        else:
            return _empty_entities()

    for column, default_value in {
        "id": "",
        "source_name": "unknown_source",
        "category": "unknown",
        "language": "unknown",
    }.items():
        if column not in working_df.columns:
            working_df[column] = default_value

    working_df[text_column] = working_df[text_column].fillna("").astype(str)
    working_df = working_df[working_df[text_column].str.strip() != ""].copy()
    if working_df.empty:
        return _empty_entities()

    language_series = working_df["language"].fillna("").astype(str).str.strip().str.lower()
    unreliable_values = {"", "unknown", "none", "nan", "null", "und"}
    language_is_unreliable = language_series.isin(unreliable_values).all()

    if language_is_unreliable:
        ner_df = working_df
    else:
        english_mask = language_series.str.startswith("en") | language_series.isin(unreliable_values)
        ner_df = working_df.loc[english_mask].copy()
        if ner_df.empty:
            ner_df = working_df

    texts = [str(t) if t else "" for t in ner_df[text_column].tolist()]
    metadata = ner_df[["id", "source_name", "category", "language"]].to_dict("records")

    rows = []
    for meta, doc in zip(metadata, nlp.pipe(texts, batch_size=32), strict=False):
        for entity in doc.ents:
            entity_text, label, start_char, end_char = _clean_entity(entity)
            rows.append(
                {
                    "document_id": meta["id"],
                    "source_name": meta["source_name"],
                    "category": meta["category"],
                    "language": meta["language"],
                    "entity_text": entity_text,
                    "label": label,
                    "start_char": start_char,
                    "end_char": end_char,
                    "sentence": _safe_sentence(entity),
                }
            )

    if not rows:
        return _empty_entities()

    return pd.DataFrame(rows, columns=ENTITY_COLUMNS)


def get_entity_label_descriptions() -> dict[str, str]:
    """Return concise descriptions for common spaCy English entity labels."""
    return {
        "PERSON": "People, including fictional characters.",
        "NORP": "Nationalities, religious groups, or political groups.",
        "FAC": "Buildings, airports, highways, bridges, and other facilities.",
        "ORG": "Companies, agencies, institutions, and organizations.",
        "GPE": "Countries, cities, and states.",
        "LOC": "Non-GPE locations, mountain ranges, and bodies of water.",
        "PRODUCT": "Objects, vehicles, foods, and other products.",
        "EVENT": "Named hurricanes, battles, wars, sports events, and similar events.",
        "WORK_OF_ART": "Titles of books, songs, paintings, and other creative works.",
        "LAW": "Named documents made into laws.",
        "LANGUAGE": "Named languages.",
        "DATE": "Absolute or relative dates and periods.",
        "TIME": "Times smaller than a day.",
        "PERCENT": "Percentages.",
        "MONEY": "Monetary values.",
        "QUANTITY": "Measurements such as weight or distance.",
        "ORDINAL": "Ordinal values.",
        "CARDINAL": "Numerals that do not fall under another label.",
    }
