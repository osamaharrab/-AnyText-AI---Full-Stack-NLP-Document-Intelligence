"""Request schemas for the AnyText AI FastAPI backend."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalyzeTextRequest(BaseModel):
    """Analyze one pasted text document."""

    text: str = Field(..., min_length=1)
    category: str = Field(default="manual", max_length=80)
    top_n: int = Field(default=20, ge=5, le=100)


class SearchRequest(BaseModel):
    """Search a prepared document collection without storing server state."""

    query: str = Field(..., min_length=1)
    documents: list[dict[str, Any]] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=20)


class AskRequest(BaseModel):
    """Ask a question over a prepared document collection without storing server state."""

    question: str = Field(..., min_length=1)
    documents: list[dict[str, Any]] = Field(default_factory=list)
    document_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=10)


class ExportRequest(BaseModel):
    """Export an already generated analysis bundle."""

    analysis: dict[str, Any] = Field(default_factory=dict)
