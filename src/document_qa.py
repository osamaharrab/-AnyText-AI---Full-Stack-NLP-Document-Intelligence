"""Retrieval-only question answering over in-memory document text."""

from __future__ import annotations

import re
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


NO_EVIDENCE_ANSWER = "I could not find enough evidence in the uploaded documents to answer this confidently."
LIMITATIONS = (
    "Retrieval-only answers are based on TF-IDF matching against document chunks. "
    "They may miss answers that use different wording and should be reviewed by a human."
)


def _compact_text(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _question_text(question: str) -> str:
    value = _compact_text(question)
    lower_value = value.lower()
    expansions = []

    if "organization" in lower_value or "organisation" in lower_value:
        expansions.append("company companies agency institution group partner")
    if "date" in lower_value or "when" in lower_value:
        expansions.append("year month day 2024 2030 timeline")
    if "risk" in lower_value or "issue" in lower_value:
        expansions.append("risk issue concern challenge problem warned")
    if "recommendation" in lower_value or "recommend" in lower_value:
        expansions.append("recommend proposed urged should plan initiative")
    if "about" in lower_value or "main" in lower_value:
        expansions.append("topic focus discusses describes")

    return " ".join([value] + expansions)


def chunk_documents(
    documents: list[dict[str, Any]],
    max_words: int = 120,
    overlap: int = 30,
) -> list[dict[str, Any]]:
    """Split document text into overlapping word chunks with source metadata."""
    if max_words <= 0:
        raise ValueError("max_words must be greater than zero.")
    if overlap < 0:
        raise ValueError("overlap must be zero or greater.")
    if overlap >= max_words:
        overlap = max(max_words // 4, 0)

    chunks: list[dict[str, Any]] = []
    step = max(max_words - overlap, 1)

    for document_index, document in enumerate(documents or []):
        text = _compact_text(document.get("text") or document.get("normalized_text") or "")
        if not text:
            continue

        words = text.split()
        document_id = str(document.get("id") or f"doc_{document_index + 1}")
        source_name = str(document.get("source_name") or "unknown_source")

        if len(words) <= max_words:
            chunks.append(
                {
                    "document_id": document_id,
                    "source_name": source_name,
                    "chunk_index": 0,
                    "text": text,
                }
            )
            continue

        chunk_index = 0
        for start in range(0, len(words), step):
            chunk_words = words[start : start + max_words]
            if not chunk_words:
                continue
            chunks.append(
                {
                    "document_id": document_id,
                    "source_name": source_name,
                    "chunk_index": chunk_index,
                    "text": " ".join(chunk_words),
                }
            )
            chunk_index += 1
            if start + max_words >= len(words):
                break

    return chunks


def retrieve_relevant_chunks(
    question: str,
    chunks: list[dict[str, Any]],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Rank chunks by TF-IDF cosine similarity to the question."""
    raw_question = _compact_text(question)
    query = _question_text(question)
    if not query:
        raise ValueError("Question cannot be empty.")
    if not chunks:
        return []

    texts = [str(chunk.get("text") or "") for chunk in chunks]
    if not any(text.strip() for text in texts):
        return []

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    try:
        matrix = vectorizer.fit_transform(texts)
        query_vector = vectorizer.transform([query])
    except ValueError:
        return []

    scores = cosine_similarity(query_vector, matrix).ravel()
    ranked_indices = scores.argsort()[::-1][: max(int(top_k or 5), 1)]
    evidence = []

    for index in ranked_indices:
        score = float(scores[index])
        if score <= 0:
            continue
        chunk = chunks[index]
        evidence.append(
            {
                "document_id": chunk.get("document_id", ""),
                "source_name": chunk.get("source_name", ""),
                "score": round(score, 4),
                "snippet": chunk.get("text", ""),
            }
        )

    if evidence:
        return evidence

    return _fallback_relevant_chunks(raw_question, chunks, top_k=top_k)


def _fallback_relevant_chunks(
    question: str,
    chunks: list[dict[str, Any]],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Handle common generic questions that do not share terms with evidence."""
    lower_question = question.lower()
    scored_chunks: list[tuple[float, dict[str, Any]]] = []

    for chunk in chunks:
        text = str(chunk.get("text") or "")
        score = 0.0

        if "organization" in lower_question or "organisation" in lower_question:
            capitalized_terms = re.findall(r"\b[A-Z][A-Za-z&.-]+(?:\s+[A-Z][A-Za-z&.-]+)*\b", text)
            score += min(len(capitalized_terms) * 0.05, 0.5)

        if "date" in lower_question or "when" in lower_question:
            years = re.findall(r"\b(?:19|20)\d{2}\b", text)
            months = re.findall(
                r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
                r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b",
                text,
                flags=re.IGNORECASE,
            )
            score += min((len(years) + len(months)) * 0.08, 0.5)

        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    evidence = []
    for score, chunk in scored_chunks[: max(int(top_k or 5), 1)]:
        evidence.append(
            {
                "document_id": chunk.get("document_id", ""),
                "source_name": chunk.get("source_name", ""),
                "score": round(float(score), 4),
                "snippet": chunk.get("text", ""),
            }
        )

    return evidence


def generate_retrieval_answer(question: str, evidence: list[dict[str, Any]]) -> str:
    """Build a conservative answer from retrieved snippets only."""
    if not evidence:
        return NO_EVIDENCE_ANSWER

    lines = [
        "Based only on the retrieved document snippets, the strongest evidence I found is:",
    ]
    for item in evidence[:3]:
        source = item.get("source_name") or item.get("document_id") or "Unknown source"
        snippet = _compact_text(item.get("snippet", ""))
        lines.append(f"- {source}: {snippet}")

    lines.append("Use the evidence snippets below to verify the answer.")
    return "\n".join(lines)


def ask_documents(
    question: str,
    documents: list[dict[str, Any]],
    document_id: str | None = None,
    top_k: int = 5,
) -> dict[str, Any]:
    """Answer a question using retrieval over the supplied in-memory documents."""
    if not _compact_text(question):
        raise ValueError("Question cannot be empty.")
    if not documents:
        raise ValueError("Ask requires analyzed documents.")

    selected_documents = documents
    if document_id:
        selected_documents = [
            document for document in documents if str(document.get("id")) == str(document_id)
        ]
        if not selected_documents:
            raise ValueError(f"Document not found: {document_id}")

    chunks = chunk_documents(selected_documents)
    evidence = retrieve_relevant_chunks(question, chunks, top_k=top_k)
    return {
        "answer": generate_retrieval_answer(question, evidence),
        "mode": "retrieval",
        "evidence": evidence,
        "limitations": LIMITATIONS,
    }
