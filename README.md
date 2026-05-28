# AnyText AI — NLP Document Intelligence

**AnyText AI** is a full-stack NLP Document Intelligence app that helps users analyze document collections, extract insights, search across documents, and ask evidence-based questions.

It answers one practical question:

> **What can this document collection tell me?**

Users can paste text or upload files such as TXT, CSV, PDF, and DOCX, then explore entities, keywords, relationships, search results, document details, and retrieval-based Q&A through a modern web dashboard.

---

## Live Demo

* **App:** https://anytext-ai-document-intelligence.vercel.app/
* **Backend health:** https://anytext-ai-document-intelligence.onrender.com/health
* **GitHub:** https://github.com/osamaharrab/anytext-ai-document-intelligence

---

## Built By

Built by **Osama Harrab**

* LinkedIn: https://www.linkedin.com/in/osama-harrab-694a2a381/
* GitHub: https://github.com/osamaharrab

---

## What It Can Do

* Upload or paste documents.
* Analyze TXT, CSV, PDF, and DOCX files.
* Extract named entities with spaCy.
* Extract TF-IDF keywords.
* Search documents with TF-IDF similarity.
* Ask questions about uploaded documents using retrieved evidence snippets.
* Explore entity relationships and cross-category patterns.
* Inspect each document with metadata, preview text, entities, and keywords.
* Export CSV, JSON, and Markdown reports.

---

## Key Features

### Document Analysis

AnyText AI standardizes uploaded content into a document collection, detects language, prepares searchable text, and runs NLP analysis over the corpus.

### Named Entity Recognition

The app extracts entities such as organizations, locations, dates, people, quantities, and other important terms using spaCy.

### Keyword Extraction

TF-IDF is used to identify important corpus-level and document-level keywords.

### Search

Users can search across the document collection and receive ranked results based on cosine similarity.

### Ask Your Documents

Users can ask questions about the uploaded documents. The app retrieves relevant snippets and answers based only on evidence found in the current document collection.

This feature is retrieval-based, not a generative LLM.

### Reports and Exports

The app can export analysis results as CSV, JSON, and Markdown reports.

---

## Screenshots


### Home

<img width="1734" height="957" alt="Screenshot From 2026-05-28 17-51-23" src="https://github.com/user-attachments/assets/a53690cb-b517-4d34-812c-b46a462400f1" />


### Entity Analysis

<img width="1365" height="952" alt="Screenshot From 2026-05-28 18-16-13" src="https://github.com/user-attachments/assets/52a1a150-83dd-45c6-b886-f27960fe3673" />


### Search

<img width="1365" height="952" alt="Screenshot From 2026-05-28 17-53-07" src="https://github.com/user-attachments/assets/d6e6bc5f-2172-46e7-bbbe-6ca829d7c64b" />


### Report

<img width="1365" height="952" alt="Screenshot From 2026-05-28 17-53-17" src="https://github.com/user-attachments/assets/a43d733d-2685-4fcd-a171-636d9115ee21" />


---

## Tech Stack

| Layer        | Tools                       |
| ------------ | --------------------------- |
| Frontend     | React, Vite, Tailwind CSS   |
| Backend      | FastAPI, Uvicorn            |
| NLP          | spaCy, scikit-learn, pandas |
| File Parsing | pypdf, python-docx          |
| Deployment   | Vercel, Render              |
| Testing      | pytest                      |

---

## Project Structure

```text
anytext-ai-document-intelligence/
├── api/          # FastAPI backend
├── frontend/     # React/Vite/Tailwind frontend
├── src/          # Reusable NLP modules
├── data/         # Sample corpus
├── docs/         # Screenshots
├── tests/        # Test suite
└── app.py        # Legacy Streamlit prototype
```

---

## Main NLP Modules

| Module             | Purpose                                    |
| ------------------ | ------------------------------------------ |
| `input_loader.py`  | Loads text, CSV, PDF, and DOCX inputs      |
| `preprocessing.py` | Normalizes and prepares documents          |
| `ner.py`           | Runs spaCy Named Entity Recognition        |
| `analytics.py`     | Computes entity and relationship analytics |
| `keywords.py`      | Extracts TF-IDF keywords                   |
| `search.py`        | Runs TF-IDF search                         |
| `document_qa.py`   | Powers Ask Your Documents retrieval        |
| `report.py`        | Generates Markdown reports                 |

---

## Privacy Note

Do not upload sensitive or confidential documents to the public demo.

Uploaded content is processed for the active session. Explorer previews and Ask evidence snippets may display text from uploaded documents in the browser.

Public screenshots should use sample data only.

---

## Limitations

* spaCy NER is English-first.
* PDF extraction only works for embedded text, not scanned PDFs.
* OCR is not included.
* Search and Ask use TF-IDF retrieval, not deep semantic reasoning.
* Ask Your Documents is retrieval-based, not a generative LLM.
* Large files may be slower because processing happens in memory.
* Human review is recommended for high-stakes use.

---

## Future Improvements

* Add a short demo video or GIF.
* Add optional ZIP export for all outputs.
* Improve CSV preview and schema validation.
* Add entity alias normalization.
* Improve multilingual NER.
* Add optional OCR for scanned PDFs.
* Add optional semantic search.

---

## Portfolio Summary

AnyText AI is a full-stack NLP Document Intelligence app built with FastAPI, React, Vite, Tailwind CSS, spaCy, and scikit-learn. It analyzes uploaded document collections, extracts entities and keywords, supports search, answers evidence-based document questions, visualizes relationships, and exports reports.
