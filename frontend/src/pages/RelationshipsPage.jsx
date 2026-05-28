import { GitBranch } from 'lucide-react';
import { Card, CardBody, CardHeader } from '../components/Card.jsx';
import { SimpleBarChart } from '../components/Charts.jsx';
import { DataTable } from '../components/DataTable.jsx';
import { EmptyState } from '../components/EmptyState.jsx';

export function RelationshipsPage({ analysis }) {
  if (!analysis) {
    return <EmptyState icon={GitBranch} title="No relationships yet" message="Run analysis from the Input page." />;
  }

  const coOccurrence = analysis.co_occurrence || [];
  const crossCategory = analysis.cross_category_patterns || [];
  const coOccurrenceChart = coOccurrence.slice(0, 12).map((row) => ({
    pair: `${row.entity_1} + ${row.entity_2}`,
    count: row.cooccurrence_count,
  }));

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader
          title="Entity Co-occurrence"
          description="Pairs are counted once per document, even if an entity appears multiple times."
        />
        <CardBody>
          <SimpleBarChart data={coOccurrenceChart} xKey="pair" yKey="count" height={320} />
          <div className="mt-5">
            <DataTable
              rows={coOccurrence}
              columns={[
                { key: 'entity_1', label: 'Entity 1' },
                { key: 'entity_2', label: 'Entity 2' },
                { key: 'cooccurrence_count', label: 'Documents' },
              ]}
            />
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Cross-category Patterns" description="Entity label patterns across document categories." />
        <CardBody>
          <SimpleBarChart
            data={crossCategory.slice(0, 16).map((row) => ({
              pattern: `${row.category} / ${row.label}`,
              mentions: row.entity_mentions,
            }))}
            xKey="pattern"
            yKey="mentions"
            height={320}
          />
          <div className="mt-5">
            <DataTable
              rows={crossCategory}
              columns={[
                { key: 'category', label: 'Category' },
                { key: 'label', label: 'Label' },
                { key: 'entity_mentions', label: 'Mentions' },
                { key: 'unique_entities', label: 'Unique Entities' },
                { key: 'documents', label: 'Documents' },
              ]}
            />
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
