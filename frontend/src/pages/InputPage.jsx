import { Database, FileText, Play, ShieldCheck, UploadCloud } from 'lucide-react';
import { useState } from 'react';
import { Button } from '../components/Button.jsx';
import { Card, CardBody, CardHeader } from '../components/Card.jsx';
import { DataTable } from '../components/DataTable.jsx';
import { MetricCard } from '../components/MetricCard.jsx';
import { analyzeFiles, analyzeText, loadSample } from '../lib/api.js';

export function InputPage({ analysis, onAnalysis, setBusy, busy, setError }) {
  const [text, setText] = useState('');
  const [textCategory, setTextCategory] = useState('manual');
  const [fileCategory, setFileCategory] = useState('unknown');
  const [files, setFiles] = useState([]);
  const [topN, setTopN] = useState(20);
  const [splitPdfPages, setSplitPdfPages] = useState(false);
  const [csvTextCol, setCsvTextCol] = useState('');
  const [csvIdCol, setCsvIdCol] = useState('');
  const [csvLanguageCol, setCsvLanguageCol] = useState('');
  const [csvCategoryCol, setCsvCategoryCol] = useState('');

  async function run(label, task) {
    setError('');
    setBusy(label);
    try {
      const result = await task();
      onAnalysis(result);
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy('');
    }
  }

  const disabled = Boolean(busy);

  return (
    <div className="space-y-6">
      <Card className="overflow-hidden">
        <div className="grid gap-6 p-6 lg:grid-cols-[1.15fr_0.85fr] lg:p-8">
          <div>
            <p className="text-sm font-bold uppercase text-brand-600">Document Intelligence</p>
            <h1 className="mt-2 max-w-3xl text-4xl font-bold text-slate-950">
              What can this document collection tell me?
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">
              Analyze pasted text or supported files with the existing AnyText AI NLP pipeline: spaCy NER,
              TF-IDF keywords, entity relationships, search, and reports.
            </p>
            <p className="mt-4 max-w-2xl rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-xs leading-5 text-slate-600">
              Privacy note: avoid uploading sensitive or confidential documents to the public demo. Files are processed
              for this session only.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Button icon={Database} onClick={() => run('Loading sample corpus...', () => loadSample(topN))} disabled={disabled}>
                Load sample corpus
              </Button>
              <Button
                icon={Play}
                variant="primary"
                onClick={() =>
                  run('Analyzing pasted text...', () => analyzeText({ text, category: textCategory, topN }))
                }
                disabled={disabled || !text.trim()}
              >
                Run analysis
              </Button>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
            <MetricCard
              label="Current corpus"
              value={analysis?.corpus_stats?.document_count || 0}
              note="Documents stay in browser state unless you submit a new analysis."
              icon={FileText}
              tone="blue"
            />
            <MetricCard
              label="Processing"
              value={busy ? 'Running' : 'Ready'}
              note="The backend processes uploads in memory and returns JSON."
              icon={ShieldCheck}
              tone="emerald"
            />
          </div>
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader
            eyebrow="Input"
            title="Paste Text"
            description="Use a memo, article, transcript, policy note, or report excerpt."
          />
          <CardBody className="space-y-4">
            <textarea
              className="min-h-72 w-full resize-y rounded-lg border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-800 shadow-sm"
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder="Paste document text here..."
            />
            <div className="grid gap-3 sm:grid-cols-[1fr_9rem]">
              <label className="block text-sm font-semibold text-slate-700">
                Category
                <input
                  className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  value={textCategory}
                  onChange={(event) => setTextCategory(event.target.value)}
                />
              </label>
              <label className="block text-sm font-semibold text-slate-700">
                Top entities
                <input
                  className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  type="number"
                  min="5"
                  max="100"
                  value={topN}
                  onChange={(event) => setTopN(Number(event.target.value))}
                />
              </label>
            </div>
            <Button
              icon={Play}
              variant="primary"
              className="w-full"
              onClick={() => run('Analyzing pasted text...', () => analyzeText({ text, category: textCategory, topN }))}
              disabled={disabled || !text.trim()}
            >
              Analyze pasted text
            </Button>
          </CardBody>
        </Card>

        <Card>
          <CardHeader
            eyebrow="Files"
            title="Upload Documents"
            description="TXT, CSV, PDF with embedded text, and DOCX are routed through the existing loaders."
          />
          <CardBody className="space-y-4">
            <label className="flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 text-center transition hover:border-brand-500 hover:bg-brand-50">
              <UploadCloud className="h-8 w-8 text-brand-600" aria-hidden="true" />
              <span className="mt-3 text-sm font-semibold text-slate-800">Choose files</span>
              <span className="mt-1 text-xs text-slate-500">TXT, CSV, PDF, DOCX</span>
              <input
                className="sr-only"
                type="file"
                multiple
                accept=".txt,.csv,.pdf,.docx"
                onChange={(event) => setFiles(Array.from(event.target.files || []))}
              />
            </label>
            {files.length ? (
              <div className="rounded-lg bg-slate-50 p-3 text-sm text-slate-600">
                {files.map((file) => (
                  <div key={`${file.name}-${file.size}`} className="truncate">
                    {file.name}
                  </div>
                ))}
              </div>
            ) : null}
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block text-sm font-semibold text-slate-700">
                Fallback category
                <input
                  className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  value={fileCategory}
                  onChange={(event) => setFileCategory(event.target.value)}
                />
              </label>
              <label className="flex items-end gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700">
                <input
                  type="checkbox"
                  checked={splitPdfPages}
                  onChange={(event) => setSplitPdfPages(event.target.checked)}
                />
                Split PDFs by page
              </label>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <input
                className="rounded-md border border-slate-200 px-3 py-2 text-sm"
                value={csvTextCol}
                onChange={(event) => setCsvTextCol(event.target.value)}
                placeholder="CSV text column"
              />
              <input
                className="rounded-md border border-slate-200 px-3 py-2 text-sm"
                value={csvIdCol}
                onChange={(event) => setCsvIdCol(event.target.value)}
                placeholder="CSV ID column"
              />
              <input
                className="rounded-md border border-slate-200 px-3 py-2 text-sm"
                value={csvLanguageCol}
                onChange={(event) => setCsvLanguageCol(event.target.value)}
                placeholder="CSV language column"
              />
              <input
                className="rounded-md border border-slate-200 px-3 py-2 text-sm"
                value={csvCategoryCol}
                onChange={(event) => setCsvCategoryCol(event.target.value)}
                placeholder="CSV category column"
              />
            </div>
            <Button
              icon={UploadCloud}
              variant="primary"
              className="w-full"
              disabled={disabled || files.length === 0}
              onClick={() =>
                run('Analyzing uploaded files...', () =>
                  analyzeFiles({
                    files,
                    category: fileCategory,
                    topN,
                    splitPdfPages,
                    csvTextCol,
                    csvIdCol,
                    csvLanguageCol,
                    csvCategoryCol,
                  }),
                )
              }
            >
              Analyze uploaded files
            </Button>
          </CardBody>
        </Card>
      </div>

      {analysis?.documents?.length ? (
        <Card>
          <CardHeader title="Current Documents" description="Prepared rows returned by the backend." />
          <CardBody>
            <DataTable
              rows={analysis.documents}
              limit={8}
              columns={[
                { key: 'id', label: 'ID' },
                { key: 'source_name', label: 'Source' },
                { key: 'category', label: 'Category' },
                { key: 'language', label: 'Language' },
                { key: 'text_length', label: 'Characters' },
              ]}
            />
          </CardBody>
        </Card>
      ) : null}
    </div>
  );
}
