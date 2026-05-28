const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let message = `Request failed with ${response.status}`;
    try {
      const error = await response.json();
      message = error.detail || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  return response.json();
}

export function analyzeText({ text, category, topN }) {
  return request('/api/analyze-text', {
    method: 'POST',
    body: JSON.stringify({
      text,
      category,
      top_n: topN,
    }),
  });
}

export function analyzeFiles({
  files,
  category,
  topN,
  splitPdfPages,
  csvTextCol,
  csvIdCol,
  csvLanguageCol,
  csvCategoryCol,
}) {
  const form = new FormData();
  Array.from(files || []).forEach((file) => form.append('files', file));
  form.append('category', category || 'unknown');
  form.append('top_n', String(topN || 20));
  form.append('split_pdf_pages', String(Boolean(splitPdfPages)));
  form.append('csv_text_col', csvTextCol || '');
  form.append('csv_id_col', csvIdCol || '');
  form.append('csv_language_col', csvLanguageCol || '');
  form.append('csv_category_col', csvCategoryCol || '');

  return request('/api/analyze-files', {
    method: 'POST',
    body: form,
  });
}

export function loadSample(topN = 20) {
  return request(`/api/sample?top_n=${encodeURIComponent(topN)}`);
}

export function searchDocuments({ query, documents, topK }) {
  return request('/api/search', {
    method: 'POST',
    body: JSON.stringify({
      query,
      documents,
      top_k: topK,
    }),
  });
}

export function askDocuments({ question, documents, documentId, topK }) {
  return request('/api/ask', {
    method: 'POST',
    body: JSON.stringify({
      question,
      documents,
      document_id: documentId || null,
      top_k: topK,
    }),
  });
}

export function exportReport(analysis) {
  return request('/api/export/report', {
    method: 'POST',
    body: JSON.stringify({ analysis }),
  });
}

export function exportJson(analysis) {
  return request('/api/export/json', {
    method: 'POST',
    body: JSON.stringify({ analysis }),
  });
}
