import { Download, FileText } from 'lucide-react';
import { Button } from '../components/Button.jsx';
import { Card, CardBody, CardHeader } from '../components/Card.jsx';
import { EmptyState } from '../components/EmptyState.jsx';
import { downloadText } from '../lib/format.js';

export function ReportPage({ analysis }) {
  if (!analysis) {
    return <EmptyState icon={FileText} title="No report yet" message="Run analysis from the Input page." />;
  }

  const report = analysis.report_markdown || '';

  return (
    <Card>
      <CardHeader
        title="Markdown Report"
        description="Corpus structure, entities, keywords, co-occurrence, category patterns, interpretation, and limitations."
        action={
          <Button
            icon={Download}
            onClick={() => downloadText('nlp_analysis_report.md', report, 'text/markdown')}
            disabled={!report}
          >
            Download
          </Button>
        }
      />
      <CardBody>
        <pre className="max-h-[70vh] overflow-auto whitespace-pre-wrap rounded-lg border border-slate-200 bg-slate-50 p-5 text-sm leading-7 text-slate-800">
          {report}
        </pre>
      </CardBody>
    </Card>
  );
}
