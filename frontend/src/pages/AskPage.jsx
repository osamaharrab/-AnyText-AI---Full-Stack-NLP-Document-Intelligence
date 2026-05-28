import { HelpCircle, Lightbulb, MessageSquareText } from 'lucide-react';
import { useState } from 'react';
import { Button } from '../components/Button.jsx';
import { Card, CardBody, CardHeader } from '../components/Card.jsx';
import { EmptyState } from '../components/EmptyState.jsx';
import { askDocuments } from '../lib/api.js';
import { formatPercent, formatUnknown, redactPreviewText, shortenId, truncate } from '../lib/format.js';

const EXAMPLE_QUESTIONS = [
  'What is this document about?',
  'What organizations are mentioned?',
  'What are the main dates?',
  'What risks or issues are discussed?',
  'What are the key recommendations?',
];

function EvidenceCard({ item }) {
  const source = formatUnknown(item.source_name || item.document_id);

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-bold text-slate-950" title={source}>
            {source}
          </h3>
          <p className="mt-1 text-xs font-semibold uppercase text-slate-500">
            {shortenId(item.document_id)} / {formatPercent(item.score)}
          </p>
        </div>
        <span className="rounded-md bg-brand-50 px-2.5 py-1 text-xs font-bold text-brand-700">
          Evidence
        </span>
      </div>
      <p className="mt-4 whitespace-pre-wrap break-words text-sm leading-6 text-slate-700">
        {redactPreviewText(item.snippet || '')}
      </p>
    </article>
  );
}

export function AskPage({ analysis, setError }) {
  const documents = analysis?.documents || [];
  const [question, setQuestion] = useState('');
  const [documentId, setDocumentId] = useState('all');
  const [result, setResult] = useState(null);
  const [asking, setAsking] = useState(false);

  if (!analysis || !documents.length) {
    return (
      <EmptyState
        icon={MessageSquareText}
        title="No corpus loaded"
        message="Load or analyze documents first, then ask a question about the current browser session documents."
      />
    );
  }

  async function runAsk(event) {
    event?.preventDefault();
    if (!question.trim()) return;

    setError('');
    setAsking(true);
    try {
      const response = await askDocuments({
        question,
        documents,
        documentId: documentId === 'all' ? null : documentId,
        topK: 5,
      });
      setResult(response);
    } catch (error) {
      setError(error.message);
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader
          eyebrow="Ask Your Documents"
          title="Ask a Grounded Question"
          description="Answers are generated only from retrieved snippets in the current document collection."
        />
        <CardBody className="space-y-5">
          <form className="space-y-4" onSubmit={runAsk}>
            <label className="block text-sm font-semibold text-slate-700">
              Question
              <textarea
                className="mt-1 min-h-28 w-full resize-y rounded-lg border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-800 shadow-sm"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask about facts, entities, dates, risks, or recommendations in your documents."
              />
            </label>

            <label className="block text-sm font-semibold text-slate-700">
              Scope
              <select
                className="mt-1 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                value={documentId}
                onChange={(event) => setDocumentId(event.target.value)}
              >
                <option value="all">Ask across all documents</option>
                {documents.map((document) => {
                  const source = formatUnknown(document.source_name);
                  const label = `${source} - ${formatUnknown(document.category)} - ${shortenId(document.id)}`;
                  return (
                    <option key={document.id} value={document.id}>
                      {truncate(label, 140)}
                    </option>
                  );
                })}
              </select>
            </label>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-wrap gap-2">
                {EXAMPLE_QUESTIONS.map((example) => (
                  <button
                    key={example}
                    type="button"
                    className="rounded-md border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:border-brand-500 hover:text-brand-700"
                    onClick={() => setQuestion(example)}
                  >
                    {example}
                  </button>
                ))}
              </div>
              <Button icon={HelpCircle} variant="primary" type="submit" disabled={asking || !question.trim()}>
                {asking ? 'Asking...' : 'Ask'}
              </Button>
            </div>
          </form>

          <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-900">
            Answers are generated only from the current browser session documents. Avoid uploading sensitive documents
            to public demos.
          </div>
        </CardBody>
      </Card>

      {result ? (
        <div className="space-y-6">
          <Card>
            <CardHeader
              title="Answer"
              description={result.mode === 'retrieval' ? 'Retrieval-only mode using TF-IDF document chunks.' : 'Grounded LLM mode.'}
            />
            <CardBody>
              <div className="whitespace-pre-wrap break-words rounded-lg border border-slate-200 bg-slate-50 p-5 text-sm leading-7 text-slate-800">
                {redactPreviewText(result.answer || '')}
              </div>
              {result.limitations ? (
                <p className="mt-4 flex gap-2 text-sm leading-6 text-slate-600">
                  <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-brand-600" aria-hidden="true" />
                  {result.limitations}
                </p>
              ) : null}
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Evidence Snippets" description="Top document chunks used to produce the answer." />
            <CardBody>
              {result.evidence?.length ? (
                <div className="grid gap-4">
                  {result.evidence.map((item, index) => (
                    <EvidenceCard key={`${item.document_id}-${index}`} item={item} />
                  ))}
                </div>
              ) : (
                <EmptyState
                  icon={MessageSquareText}
                  title="No evidence found"
                  message="Try a broader question or ask across all documents."
                />
              )}
            </CardBody>
          </Card>
        </div>
      ) : (
        <EmptyState
          icon={MessageSquareText}
          title="Ask a question"
          message="The answer and supporting evidence snippets will appear here."
        />
      )}
    </div>
  );
}
