import { Download, FileJson, FileSpreadsheet, FileText } from 'lucide-react';
import { useState } from 'react';
import { Button } from '../components/Button.jsx';
import { Card, CardBody, CardHeader } from '../components/Card.jsx';
import { EmptyState } from '../components/EmptyState.jsx';
import { exportJson, exportReport } from '../lib/api.js';
import { downloadJson, downloadText, toCsv } from '../lib/format.js';

function CsvButton({ label, filename, rows }) {
  return (
    <Button
      icon={Download}
      className="w-full justify-start"
      disabled={!rows?.length}
      onClick={() => downloadText(filename, toCsv(rows), 'text/csv')}
    >
      {label}
    </Button>
  );
}

export function DownloadsPage({ analysis, setError }) {
  const [busy, setBusy] = useState('');

  if (!analysis) {
    return <EmptyState icon={Download} title="No exports available" message="Run analysis from the Input page." />;
  }

  async function downloadServerReport() {
    setError('');
    setBusy('report');
    try {
      const response = await exportReport(analysis);
      downloadText(response.filename, response.content, response.mime_type);
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy('');
    }
  }

  async function downloadServerJson() {
    setError('');
    setBusy('json');
    try {
      const response = await exportJson(analysis);
      downloadJson(response.filename, response.content);
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy('');
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <Card>
        <CardHeader eyebrow="CSV" title="Tables" description="Flat exports for spreadsheets and lightweight analysis." />
        <CardBody className="space-y-3">
          <CsvButton label="Prepared documents" filename="prepared_documents.csv" rows={analysis.documents} />
          <CsvButton label="Extracted entities" filename="extracted_entities.csv" rows={analysis.entity_mentions} />
          <CsvButton label="Top entities" filename="top_entities.csv" rows={analysis.top_entities} />
          <CsvButton label="Entity label counts" filename="entity_label_counts.csv" rows={analysis.entity_label_counts} />
          <CsvButton label="Keywords" filename="keywords.csv" rows={analysis.keywords} />
          <CsvButton label="Document keywords" filename="document_keywords.csv" rows={analysis.document_keywords} />
          <CsvButton label="Co-occurrence" filename="entity_co_occurrence.csv" rows={analysis.co_occurrence} />
          <CsvButton
            label="Cross-category patterns"
            filename="cross_category_patterns.csv"
            rows={analysis.cross_category_patterns}
          />
        </CardBody>
      </Card>

      <Card>
        <CardHeader eyebrow="JSON" title="Analysis Bundle" description="Machine-readable output returned by the API." />
        <CardBody className="space-y-3">
          <Button
            icon={FileJson}
            variant="primary"
            className="w-full justify-start"
            onClick={downloadServerJson}
            disabled={busy === 'json'}
          >
            Full analysis JSON
          </Button>
          <Button
            icon={Download}
            className="w-full justify-start"
            onClick={() =>
              downloadJson('analysis_summary.json', {
                corpus_stats: analysis.corpus_stats,
                entities: analysis.entities,
                top_entities: analysis.top_entities,
                entity_label_counts: analysis.entity_label_counts,
                keywords: analysis.keywords,
                co_occurrence: analysis.co_occurrence,
                cross_category_patterns: analysis.cross_category_patterns,
              })
            }
          >
            Summary JSON
          </Button>
        </CardBody>
      </Card>

      <Card>
        <CardHeader eyebrow="Markdown" title="Report" description="Narrative report for review and sharing." />
        <CardBody className="space-y-3">
          <Button
            icon={FileText}
            variant="primary"
            className="w-full justify-start"
            onClick={downloadServerReport}
            disabled={busy === 'report'}
          >
            Markdown report
          </Button>
          <div className="rounded-lg bg-slate-50 p-4 text-sm leading-6 text-slate-600">
            Public demos should use the included sample corpus or sanitized documents. Do not upload sensitive,
            confidential, private, or regulated content to public deployments.
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
