import { FileText, FolderTree, Languages, Tags } from 'lucide-react';
import { Card, CardBody, CardHeader } from '../components/Card.jsx';
import { DonutChart, SimpleBarChart } from '../components/Charts.jsx';
import { DataTable } from '../components/DataTable.jsx';
import { EmptyState } from '../components/EmptyState.jsx';
import { MetricCard } from '../components/MetricCard.jsx';

export function OverviewPage({ analysis }) {
  if (!analysis) {
    return <EmptyState icon={FileText} title="No corpus loaded" message="Load documents from the Input page." />;
  }

  const stats = analysis.corpus_stats || {};

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Documents" value={stats.document_count || 0} icon={FileText} tone="blue" />
        <MetricCard label="Languages" value={stats.language_count || 0} icon={Languages} tone="teal" />
        <MetricCard label="Categories" value={stats.category_count || 0} icon={FolderTree} tone="violet" />
        <MetricCard label="Entity Mentions" value={analysis.entities?.total_mentions || 0} icon={Tags} tone="emerald" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Category Distribution" description="Document counts by assigned category." />
          <CardBody>
            <SimpleBarChart data={stats.category_distribution || []} xKey="category" yKey="documents" />
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Language Distribution" description="Detected language mix across the corpus." />
          <CardBody>
            <DonutChart data={stats.language_distribution || []} nameKey="language" valueKey="documents" />
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader title="Prepared Document Table" description="The standardized table used by NER, keywords, search, and exports." />
        <CardBody>
          <DataTable
            rows={analysis.documents || []}
            columns={[
              { key: 'id', label: 'ID' },
              { key: 'source_name', label: 'Source' },
              { key: 'category', label: 'Category' },
              { key: 'language', label: 'Language' },
              { key: 'text_length', label: 'Characters' },
              { key: 'text', label: 'Preview' },
            ]}
          />
        </CardBody>
      </Card>
    </div>
  );
}
