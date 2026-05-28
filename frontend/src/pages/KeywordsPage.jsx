import { KeyRound } from 'lucide-react';
import { Card, CardBody, CardHeader } from '../components/Card.jsx';
import { SimpleBarChart } from '../components/Charts.jsx';
import { DataTable } from '../components/DataTable.jsx';
import { EmptyState } from '../components/EmptyState.jsx';

export function KeywordsPage({ analysis }) {
  if (!analysis) {
    return <EmptyState icon={KeyRound} title="No keywords yet" message="Run analysis from the Input page." />;
  }

  const keywords = analysis.keywords || [];
  const documentKeywords = analysis.document_keywords || [];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader
          eyebrow="TF-IDF"
          title="Corpus Keywords"
          description="Keywords use statistical TF-IDF weighting over normalized search text with English stop-word removal."
        />
        <CardBody>
          <SimpleBarChart data={keywords.slice(0, 16)} xKey="keyword" yKey="score" height={320} />
          <div className="mt-5">
            <DataTable
              rows={keywords}
              columns={[
                { key: 'keyword', label: 'Keyword' },
                { key: 'score', label: 'Score' },
                { key: 'document_count', label: 'Documents' },
              ]}
            />
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Document Keywords" description="Top terms and phrases for each prepared document." />
        <CardBody>
          <DataTable
            rows={documentKeywords}
            columns={[
              { key: 'document_id', label: 'Document' },
              { key: 'source_name', label: 'Source' },
              { key: 'category', label: 'Category' },
              { key: 'keyword', label: 'Keyword' },
              { key: 'score', label: 'Score' },
              { key: 'rank', label: 'Rank' },
            ]}
          />
        </CardBody>
      </Card>
    </div>
  );
}
