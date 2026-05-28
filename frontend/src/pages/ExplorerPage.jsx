import { FileSearch } from 'lucide-react';
import { useMemo, useState } from 'react';
import { Card, CardBody, CardHeader } from '../components/Card.jsx';
import { DataTable } from '../components/DataTable.jsx';
import { EmptyState } from '../components/EmptyState.jsx';
import { formatNumber, formatUnknown, redactPreviewText, shortenId, truncate } from '../lib/format.js';

function MetadataCard({ label, value, title }) {
  return (
    <div className="min-w-0 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-xs font-semibold uppercase text-slate-500">{label}</p>
      <p className="mt-2 truncate text-base font-bold text-slate-950" title={title || String(value)}>
        {value}
      </p>
    </div>
  );
}

function MetadataList({ rows }) {
  return (
    <dl className="divide-y divide-slate-100 rounded-lg border border-slate-200">
      {rows.map((row) => (
        <div key={row.label} className="grid gap-1 px-4 py-3 sm:grid-cols-[12rem_1fr] sm:gap-4">
          <dt className="text-xs font-bold uppercase text-slate-500">{row.label}</dt>
          <dd className="min-w-0 break-words text-sm text-slate-800" title={row.title || String(row.value)}>
            {row.value}
          </dd>
        </div>
      ))}
    </dl>
  );
}

export function ExplorerPage({ analysis }) {
  const documents = analysis?.documents || [];
  const [selectedId, setSelectedId] = useState('');

  const selectedDocument = useMemo(() => {
    if (!documents.length) return null;
    return documents.find((document) => String(document.id) === String(selectedId)) || documents[0];
  }, [documents, selectedId]);

  if (!analysis || !documents.length) {
    return <EmptyState icon={FileSearch} title="No documents loaded" message="Load documents from the Input page." />;
  }

  const documentId = String(selectedDocument.id);
  const sourceName = formatUnknown(selectedDocument.source_name);
  const category = formatUnknown(selectedDocument.category);
  const language = formatUnknown(selectedDocument.language);
  const text = String(selectedDocument.text || '');
  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;
  const characterCount = Number(selectedDocument.text_length || text.length || 0);
  const documentEntities = (analysis.entity_mentions || []).filter(
    (entity) => String(entity.document_id) === documentId,
  );
  const documentKeywords = (analysis.document_keywords || []).filter(
    (keyword) => String(keyword.document_id) === documentId,
  );
  const safeDocumentEntities = documentEntities.map((entity) => ({
    ...entity,
    sentence: redactPreviewText(entity.sentence || ''),
  }));
  const safeDocumentKeywords = documentKeywords.map((keyword) => ({
    ...keyword,
    keyword: redactPreviewText(keyword.keyword || ''),
  }));
  const previewText = redactPreviewText(text);
  const safeMetadataRows = [
    { label: 'Document ID', value: documentId, title: documentId },
    { label: 'Source Name', value: sourceName, title: sourceName },
    { label: 'Category', value: category },
    { label: 'Language', value: language.toUpperCase() },
    { label: 'Text Length', value: formatNumber(characterCount) },
    { label: 'Word Count', value: formatNumber(wordCount) },
    { label: 'Entity Count', value: formatNumber(documentEntities.length) },
    { label: 'Keyword Count', value: formatNumber(documentKeywords.length) },
  ];

  return (
    <div className="space-y-6 overflow-hidden">
      <Card>
        <CardHeader
          title="Select Document"
          description="Inspect safe metadata, redacted preview text, document entities, and document keywords."
        />
        <CardBody>
          <select
            className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
            value={documentId}
            onChange={(event) => setSelectedId(event.target.value)}
          >
            {documents.map((document) => {
              const label = `${formatUnknown(document.source_name)} - ${formatUnknown(document.category)} - ${shortenId(
                document.id,
              )}`;
              return (
                <option key={document.id} value={document.id}>
                  {truncate(label, 140)}
                </option>
              );
            })}
          </select>
        </CardBody>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <MetadataCard label="Source" value={truncate(sourceName, 44)} title={sourceName} />
        <MetadataCard label="Category" value={category} />
        <MetadataCard label="Language" value={language.toUpperCase()} />
        <MetadataCard label="Words" value={formatNumber(wordCount)} />
        <MetadataCard label="Characters" value={formatNumber(characterCount)} />
        <MetadataCard label="Document ID" value={shortenId(documentId)} title={documentId} />
      </div>

      <Card>
        <CardHeader
          title="Raw Text Preview"
          description="Display-only preview with obvious emails and phone-like numbers redacted for safer screenshots."
        />
        <CardBody>
          <div className="whitespace-pre-wrap break-words max-h-80 overflow-y-auto rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-700">
            {previewText || 'No preview text available.'}
          </div>
          <p className="mt-3 text-xs leading-5 text-slate-500">
            Public demo note: avoid uploading sensitive documents. Previews are for local/browser display only.
          </p>
        </CardBody>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Entities in Document" description="Named entity mentions detected in this document." />
          <CardBody>
            <DataTable
              rows={safeDocumentEntities}
              columns={[
                { key: 'entity_text', label: 'Entity' },
                { key: 'label', label: 'Label' },
                { key: 'sentence', label: 'Sentence' },
              ]}
            />
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Keywords in Document" description="Top TF-IDF terms and phrases for this document." />
          <CardBody>
            <DataTable
              rows={safeDocumentKeywords}
              columns={[
                { key: 'keyword', label: 'Keyword' },
                { key: 'score', label: 'Score' },
                { key: 'rank', label: 'Rank' },
              ]}
            />
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader
          title="Full Metadata"
          description="Compact safe metadata only. Full text, normalized text, and search text are intentionally hidden here."
        />
        <CardBody>
          <MetadataList rows={safeMetadataRows} />
        </CardBody>
      </Card>
    </div>
  );
}
