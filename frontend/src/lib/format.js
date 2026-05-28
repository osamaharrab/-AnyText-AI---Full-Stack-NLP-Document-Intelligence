export function formatNumber(value) {
  const number = Number(value || 0);
  if (!Number.isFinite(number)) return '0';
  return new Intl.NumberFormat('en-US').format(number);
}

export function formatPercent(value) {
  const number = Number(value || 0);
  if (!Number.isFinite(number)) return '0%';
  return `${Math.round(number * 100)}%`;
}

export function truncate(value, length = 120) {
  const text = String(value || '').replace(/\s+/g, ' ').trim();
  if (text.length <= length) return text;
  return `${text.slice(0, length - 1)}...`;
}

export function formatUnknown(value) {
  const text = String(value ?? '').trim();
  if (!text || ['unknown', 'none', 'nan', 'null'].includes(text.toLowerCase())) {
    return 'Unknown';
  }
  return text;
}

export function shortenId(value, length = 18) {
  const text = formatUnknown(value);
  if (text === 'Unknown' || text.length <= length) return text;
  const keepStart = Math.max(Math.floor((length - 3) * 0.55), 4);
  const keepEnd = Math.max(length - keepStart - 3, 4);
  return `${text.slice(0, keepStart)}...${text.slice(-keepEnd)}`;
}

export function redactPreviewText(value) {
  const text = String(value || '');
  const emailPattern = /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi;
  const phonePattern = /(?:\+?\d[\d\s().-]{7,}\d)/g;

  return text.replace(emailPattern, '[email redacted]').replace(phonePattern, (match) => {
    const digits = match.replace(/\D/g, '');
    return digits.length >= 8 ? '[phone redacted]' : match;
  });
}

export function uniqueValues(rows, key) {
  return Array.from(
    new Set((rows || []).map((row) => row?.[key]).filter((value) => value !== undefined && value !== null && value !== '')),
  ).sort((a, b) => String(a).localeCompare(String(b)));
}

export function toCsv(rows) {
  const data = rows || [];
  if (!data.length) return '';

  const columns = Array.from(
    data.reduce((set, row) => {
      Object.keys(row || {}).forEach((key) => set.add(key));
      return set;
    }, new Set()),
  );

  const escapeCell = (value) => {
    const text = value === null || value === undefined ? '' : String(value);
    return `"${text.replaceAll('"', '""')}"`;
  };

  return [
    columns.map(escapeCell).join(','),
    ...data.map((row) => columns.map((column) => escapeCell(row?.[column])).join(',')),
  ].join('\n');
}

export function downloadText(filename, content, mimeType = 'text/plain') {
  const blob = new Blob([content], { type: `${mimeType};charset=utf-8` });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export function downloadJson(filename, content) {
  downloadText(filename, JSON.stringify(content || {}, null, 2), 'application/json');
}

export function groupEntityContexts(analysis, entityText, windowSize = 140) {
  if (!analysis || !entityText) return [];

  const documents = new Map((analysis.documents || []).map((document) => [String(document.id), document]));
  const matches = (analysis.entity_mentions || []).filter(
    (entity) => String(entity.entity_text) === String(entityText),
  );
  const grouped = matches.reduce((map, entity) => {
    const key = String(entity.document_id);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(entity);
    return map;
  }, new Map());

  return Array.from(grouped.entries())
    .map(([documentId, entities]) => {
      const document = documents.get(documentId);
      const text = String(document?.text || '');
      const first = entities[0] || {};
      const start = Number(first.start_char);
      const end = Number(first.end_char);
      let context = truncate(text, windowSize * 2);

      if (Number.isFinite(start) && Number.isFinite(end) && end > start && start < text.length) {
        const left = Math.max(0, start - windowSize);
        const right = Math.min(text.length, end + windowSize);
        context = `${left > 0 ? '...' : ''}${text.slice(left, right).replace(/\s+/g, ' ').trim()}${
          right < text.length ? '...' : ''
        }`;
      }

      return {
        document_id: documentId,
        source_name: document?.source_name || first.source_name || '',
        category: document?.category || first.category || '',
        language: document?.language || first.language || '',
        labels: Array.from(new Set(entities.map((entity) => entity.label))).join(', '),
        mention_count: entities.length,
        context,
      };
    })
    .sort((a, b) => b.mention_count - a.mention_count || a.source_name.localeCompare(b.source_name));
}
