from __future__ import annotations

from api.main import ask_endpoint
from api.schemas import AskRequest
from src.document_qa import ask_documents, chunk_documents, retrieve_relevant_chunks


def test_chunk_documents_uses_overlap_and_metadata():
    documents = [
        {
            "id": "doc_1",
            "source_name": "policy.txt",
            "text": " ".join(f"word{i}" for i in range(1, 181)),
        }
    ]

    chunks = chunk_documents(documents, max_words=60, overlap=15)

    assert len(chunks) == 4
    assert chunks[0]["document_id"] == "doc_1"
    assert chunks[0]["source_name"] == "policy.txt"
    assert chunks[0]["text"].split()[-15:] == chunks[1]["text"].split()[:15]


def test_retrieve_relevant_chunks_returns_matching_document():
    chunks = chunk_documents(
        [
            {
                "id": "finance",
                "source_name": "finance.txt",
                "text": "The company reported revenue growth and enterprise contracts.",
            },
            {
                "id": "health",
                "source_name": "health.txt",
                "text": "Doctors discussed hospital capacity and public health risks.",
            },
        ]
    )

    evidence = retrieve_relevant_chunks("What health risks are discussed?", chunks, top_k=1)

    assert len(evidence) == 1
    assert evidence[0]["document_id"] == "health"
    assert evidence[0]["score"] > 0


def test_ask_documents_returns_retrieval_answer_and_evidence():
    result = ask_documents(
        "What organizations are mentioned?",
        [
            {
                "id": "d1",
                "source_name": "sample.txt",
                "text": "Apple and Microsoft announced a cloud partnership in London.",
            }
        ],
    )

    assert result["mode"] == "retrieval"
    assert result["evidence"]
    assert "Based only on the retrieved document snippets" in result["answer"]


def test_ask_endpoint_with_sample_documents():
    payload = AskRequest(
        question="What risks are discussed?",
        documents=[
            {
                "id": "d1",
                "source_name": "risk-note.txt",
                "text": "The report warned about cybersecurity risk and delayed response planning.",
            },
            {
                "id": "d2",
                "source_name": "sports.txt",
                "text": "The marathon attracted runners and raised money for youth programs.",
            },
        ],
        top_k=1,
    )

    response = ask_endpoint(payload)

    assert response["mode"] == "retrieval"
    assert response["evidence"][0]["document_id"] == "d1"
    assert response["limitations"]
