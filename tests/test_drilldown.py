from __future__ import annotations

import pandas as pd

from src.drilldown import get_entity_contexts
from src.preprocessing import prepare_documents


def test_get_entity_contexts_returns_document_contexts():
    documents = prepare_documents(
        pd.DataFrame(
            [
                {
                    "id": "d1",
                    "source_name": "manual_input",
                    "text": "Apple works with Microsoft in London on cloud infrastructure.",
                    "language": "en",
                    "category": "technology",
                }
            ]
        )
    )
    entities = pd.DataFrame(
        [
            {
                "document_id": "d1",
                "source_name": "manual_input",
                "category": "technology",
                "language": "en",
                "entity_text": "Apple",
                "label": "ORG",
                "start_char": 0,
                "end_char": 5,
                "sentence": "Apple works with Microsoft in London on cloud infrastructure.",
            }
        ]
    )

    contexts = get_entity_contexts(documents, entities, "Apple", window=20)

    assert len(contexts) == 1
    assert contexts.iloc[0]["mention_count"] == 1
    assert contexts.iloc[0]["labels"] == "ORG"
    assert "Apple works" in contexts.iloc[0]["context"]
