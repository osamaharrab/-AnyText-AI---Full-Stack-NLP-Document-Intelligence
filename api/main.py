"""FastAPI entrypoint for the AnyText AI document intelligence API."""

from __future__ import annotations

import os
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import AnalyzeTextRequest, AskRequest, ExportRequest, SearchRequest
from api.services import (
    InMemoryUpload,
    analyze_sample_corpus,
    analyze_text,
    analyze_uploads,
    ask_analysis_documents,
    json_export,
    report_export,
    search_analysis_documents,
)


app = FastAPI(
    title="AnyText AI API",
    version="2.0.0",
    description="Stateless NLP document intelligence API backed by the existing AnyText AI Python logic.",
)


def _cors_origins() -> list[str]:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]
    configured = [os.getenv("FRONTEND_ORIGIN", ""), os.getenv("FRONTEND_ORIGINS", "")]
    for value in configured:
        for origin in value.split(","):
            origin = origin.strip().rstrip("/")
            if origin and origin != "*" and origin not in origins:
                origins.append(origin)
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "anytext-ai-api"}


@app.post("/api/analyze-text")
def analyze_text_endpoint(payload: AnalyzeTextRequest) -> dict:
    try:
        return analyze_text(payload.text, category=payload.category, top_n=payload.top_n)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/analyze-files")
async def analyze_files_endpoint(
    files: Annotated[list[UploadFile], File(description="TXT, CSV, PDF, or DOCX files")],
    category: Annotated[str, Form()] = "unknown",
    top_n: Annotated[int, Form(ge=5, le=100)] = 20,
    split_pdf_pages: Annotated[bool, Form()] = False,
    csv_text_col: Annotated[str | None, Form()] = None,
    csv_id_col: Annotated[str | None, Form()] = None,
    csv_language_col: Annotated[str | None, Form()] = None,
    csv_category_col: Annotated[str | None, Form()] = None,
) -> dict:
    uploads = [
        InMemoryUpload(name=file.filename or "uploaded_file", data=await file.read())
        for file in files
    ]
    try:
        return analyze_uploads(
            uploads,
            category=category,
            top_n=top_n,
            split_pdf_pages=split_pdf_pages,
            csv_text_col=(csv_text_col or "").strip() or None,
            csv_id_col=(csv_id_col or "").strip() or None,
            csv_language_col=(csv_language_col or "").strip() or None,
            csv_category_col=(csv_category_col or "").strip() or None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/sample")
def sample_endpoint(top_n: int = 20) -> dict:
    try:
        return analyze_sample_corpus(top_n=top_n)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/search")
def search_endpoint(payload: SearchRequest) -> dict:
    try:
        results = search_analysis_documents(payload.query, payload.documents, top_k=payload.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"query": payload.query, "results": results}


@app.post("/api/ask")
def ask_endpoint(payload: AskRequest) -> dict:
    try:
        return ask_analysis_documents(
            payload.question,
            payload.documents,
            document_id=payload.document_id,
            top_k=payload.top_k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/export/report")
def export_report_endpoint(payload: ExportRequest) -> dict:
    return report_export(payload.analysis)


@app.post("/api/export/json")
def export_json_endpoint(payload: ExportRequest) -> dict:
    return json_export(payload.analysis)
