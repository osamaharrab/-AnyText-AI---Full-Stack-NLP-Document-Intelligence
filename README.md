# AnyText AI - Full-Stack NLP Document Intelligence

AnyText AI is a full-stack NLP Document Intelligence app that helps answer:

**What can this document collection tell me?**

It lets users paste text, upload supported document files, analyze entities and keywords, search a corpus, ask evidence-based questions, inspect document relationships, and export reports. The product uses a modern React dashboard with a stateless FastAPI backend while preserving the original Python NLP modules.

No OCR, authentication, database, tracking, payments, or heavy local transformer models are included.

## Live Demo

- Frontend: https://anytext-ai-document-intelligence.vercel.app/
- Backend health: https://anytext-ai-document-intelligence.onrender.com/health

## Features

- Paste text or upload TXT, CSV, PDF, and DOCX files.
- Load the included sample corpus.
- Prepare a standard document table.
- Run English-first spaCy named entity recognition.
- Extract TF-IDF corpus and document keywords.
- View overview metrics, language distribution, and category distribution.
- Explore entities with label/source/category/language filters.
- Drill into one entity across matching documents.
- Inspect one document with metadata, raw text, entities, and keywords.
- Review entity co-occurrence and cross-category patterns.
- Search documents with TF-IDF cosine similarity.
- Ask grounded questions over the current document collection with retrieval-only evidence snippets.
- Generate a Markdown NLP report.
- Export CSV, JSON, and Markdown outputs.

## Architecture

AnyText AI uses a split full-stack architecture:

- **FastAPI backend** in `api/` exposes stateless document analysis, search, Ask, and export endpoints.
- **React + Vite + Tailwind frontend** in `frontend/` is the main product UI.
- **Reusable NLP modules** in `src/` contain the document loading, preprocessing, NER, analytics, keyword, search, Ask, and report logic.
- **Legacy Streamlit prototype** in `app.py` is kept as a demo/reference UI, but the React frontend is the main product.

```text
anytext-ai/
├── api/
│   ├── main.py              # FastAPI app, CORS, and routes
│   ├── schemas.py           # API request schemas
│   └── services.py          # Stateless adapters around src/ NLP logic
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── App.jsx
│       ├── components/
│       ├── pages/
│       ├── lib/
│       └── styles.css
├── app.py                   # Legacy Streamlit prototype
├── data/
│   └── sample_text_corpus.csv
├── src/
│   ├── input_loader.py
│   ├── preprocessing.py
│   ├── ner.py
│   ├── analytics.py
│   ├── keywords.py
│   ├── search.py
│   ├── document_qa.py       # Ask Your Documents retrieval logic
│   ├── report.py
│   ├── utils.py
│   └── drilldown.py
└── tests/
```

## How The NLP Pipeline Works

The FastAPI backend calls the existing Python modules instead of rewriting algorithms:

- `src/input_loader.py`: loads pasted text, TXT, CSV, PDF, and DOCX inputs.
- `src/preprocessing.py`: standardizes documents, normalizes Unicode, detects language, and builds search text.
- `src/ner.py`: loads spaCy and extracts named entities.
- `src/analytics.py`: computes top entities, label counts, co-occurrence, and cross-category patterns.
- `src/keywords.py`: extracts TF-IDF keywords and document keywords.
- `src/search.py`: builds TF-IDF vectors and ranks search results with cosine similarity.
- `src/document_qa.py`: chunks documents and answers questions with TF-IDF retrieval over evidence snippets.
- `src/report.py`: generates the Markdown NLP report.
- `src/utils.py`: keeps export helpers for the legacy Streamlit app.

The API is stateless. Uploaded content is processed in memory and returned to the browser as JSON for the current session.

## API Endpoints

- `GET /health`
- `POST /api/analyze-text`
- `POST /api/analyze-files`
- `GET /api/sample`
- `POST /api/search`
- `POST /api/ask`
- `POST /api/export/report`
- `POST /api/export/json`

The main analysis response includes:

- `documents`
- `corpus_stats`
- `entity_mentions`
- `entities`
- `top_entities`
- `entity_label_counts`
- `keywords`
- `document_keywords`
- `co_occurrence`
- `cross_category_patterns`
- `report_markdown`
- `search_ready`
- `metadata`

## Local Setup

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

The Vite dev server will be available at:

```text
http://localhost:5173
```

### Legacy Streamlit Prototype

```bash
streamlit run app.py
```

`app.py` is a legacy/demo UI. The React frontend is the main product experience.

## Environment Variables

### Frontend local development

Create `frontend/.env` from `frontend/.env.example`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

### Render backend

After the frontend is deployed, set the deployed frontend URL on the backend:

```env
FRONTEND_ORIGIN=https://your-frontend.vercel.app
```

For multiple deployed frontends, use comma-separated origins:

```env
FRONTEND_ORIGINS=https://site1.vercel.app,https://site2.vercel.app
```

### Vercel frontend

Set the frontend build-time API URL:

```env
VITE_API_URL=https://your-backend.onrender.com
```

## How To Use

1. Open the React frontend.
2. Paste text, upload supported files, or load the sample corpus.
3. Run analysis.
4. Review Overview, Entities, Keywords, Explorer, Relationships, Search, Ask, Report, and Downloads.
5. Export CSV, JSON, or Markdown outputs.

## Accepted Inputs

- Pasted text
- `.txt`
- `.csv`
- `.pdf` with embedded text
- `.docx`

CSV uploads need a text-like column. The loader auto-detects common names such as `text`, `content`, `body`, `article`, `document`, and `description`.

Optional CSV columns:

- `id`
- `language`
- `category`


## Privacy Note

Do not upload sensitive, confidential, private, regulated, or customer documents to the public demo.

The app does not intentionally store uploaded content, add tracking, or write runtime analysis files. Documents are processed in memory by the API and kept in frontend browser state for the active session.

Explorer previews and Ask evidence snippets may show document text in the browser session. Use the included sample corpus or sanitized text for public screenshots, demos, and shared links.

## Testing

```bash
python -m compileall -q app.py src tests api
python -m pytest -q
cd frontend
npm run build
```

Tests cover the existing NLP modules, FastAPI endpoints, and retrieval-only Ask behavior.

## Deployment

### Render Backend

1. Create a Render Web Service.
2. Set the root directory to the repository root.
3. Use this build command:

```bash
pip install -r requirements.txt && python -m spacy download en_core_web_sm
```

4. Use this start command:

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

5. Deploy the service and confirm:

```text
https://your-backend.onrender.com/health
```

6. After the Vercel frontend URL exists, set this Render environment variable:

```env
FRONTEND_ORIGIN=https://your-frontend.vercel.app
```

### Vercel Frontend

1. Create a Vercel project from this repository.
2. Set the root directory to `frontend`.
3. Use this build command:

```bash
npm run build
```

4. Set the output directory to:

```text
dist
```

5. Set this environment variable:

```env
VITE_API_URL=https://your-backend.onrender.com
```

### CORS Troubleshooting

If the deployed frontend shows `Failed to fetch`, check:

- `VITE_API_URL` in Vercel points to the deployed backend URL.
- `FRONTEND_ORIGIN` in Render exactly matches the deployed frontend origin.
- The backend `/health` endpoint returns `{"status":"ok","service":"anytext-ai-api"}`.

### Other Deployment Options

- Backend: Railway, Fly.io, Azure App Service, AWS App Runner, or any container host that can run Uvicorn.
- Frontend: Netlify, Cloudflare Pages, or any static host that can build Vite.
- Legacy Streamlit: Streamlit Cloud can still run `app.py`, but it is no longer the main product architecture.

## Known Limitations

- spaCy NER is English-first.
- The small spaCy model is CPU-friendly but may miss entities or assign imperfect labels.
- PDF extraction only works for embedded text, not scanned PDFs.
- OCR is not implemented.
- TF-IDF search and Ask are retrieval/statistical, not deep semantic reasoning.
- Ask Your Documents returns evidence-based retrieval answers, not generative LLM answers.
- Keyword extraction is statistical, not a human-written topic model.
- Human review is required for high-stakes use.
- Large files are processed in memory and may be slow.
- No authentication, database, audit logging, or enterprise controls are included.

## Future Improvements

- New React screenshots.
- Optional ZIP export for all CSV/JSON/Markdown files.
- Better CSV preview and schema validation before analysis.
- Entity alias normalization and canonicalization.
- More robust multilingual NER.
- Optional OCR as a separate feature.
- Optional semantic search as a separate feature.

## Portfolio / LinkedIn Summary

AnyText AI is a full-stack NLP Document Intelligence app built with FastAPI, React, Vite, Tailwind CSS, spaCy, and scikit-learn. It analyzes pasted or uploaded document collections, extracts entities and keywords, supports TF-IDF search, answers evidence-based document questions, visualizes relationships, and exports reports while keeping processing stateless and in memory.
