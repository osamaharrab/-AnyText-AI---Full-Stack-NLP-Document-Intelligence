import { Filter, Search, Tags } from 'lucide-react';
import { useMemo, useState } from 'react';
import { Card, CardBody, CardHeader } from '../components/Card.jsx';
import { SimpleBarChart } from '../components/Charts.jsx';
import { DataTable } from '../components/DataTable.jsx';
import { EmptyState } from '../components/EmptyState.jsx';
import { MetricCard } from '../components/MetricCard.jsx';
import { groupEntityContexts, uniqueValues } from '../lib/format.js';

function MultiFilter({ label, options, value, onChange }) {
  return (
    <label className="block text-sm font-semibold text-slate-700">
      {label}
      <select
        multiple
        className="mt-1 h-28 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
        value={value}
        onChange={(event) => onChange(Array.from(event.target.selectedOptions, (option) => option.value))}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

export function EntitiesPage({ analysis }) {
  const [labels, setLabels] = useState([]);
  const [sources, setSources] = useState([]);
  const [categories, setCategories] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [selectedEntity, setSelectedEntity] = useState('');

  const mentions = analysis?.entity_mentions || [];
  const filtered = useMemo(() => {
    return mentions.filter((entity) => {
      if (labels.length && !labels.includes(String(entity.label))) return false;
      if (sources.length && !sources.includes(String(entity.source_name))) return false;
      if (categories.length && !categories.includes(String(entity.category))) return false;
      if (languages.length && !languages.includes(String(entity.language))) return false;
      return true;
    });
  }, [mentions, labels, sources, categories, languages]);

  const entityOptions = uniqueValues(filtered, 'entity_text');
  const drilldownEntity = entityOptions.includes(selectedEntity) ? selectedEntity : entityOptions[0] || '';
  const contexts = groupEntityContexts(analysis, drilldownEntity);

  if (!analysis) {
    return <EmptyState icon={Tags} title="No analysis yet" message="Run analysis from the Input page." />;
  }

  if (!mentions.length) {
    return <EmptyState icon={Tags} title="No entities found" message="The current corpus did not produce named entities." />;
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-3">
        <MetricCard label="Mentions" value={analysis.entities?.total_mentions || 0} icon={Tags} tone="blue" />
        <MetricCard label="Unique Entities" value={analysis.entities?.unique_entities || 0} icon={Search} tone="violet" />
        <MetricCard
          label="Documents With Entities"
          value={analysis.entities?.documents_with_entities || 0}
          icon={Filter}
          tone="teal"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <CardHeader title="Top Entities" description="Most frequent named entity strings and labels." />
          <CardBody>
            <SimpleBarChart data={(analysis.top_entities || []).slice(0, 12)} xKey="entity_text" yKey="count" />
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Entity Label Distribution" description="Mention counts by spaCy label." />
          <CardBody>
            <SimpleBarChart data={analysis.entity_label_counts || []} xKey="label" yKey="count" />
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader title="Entity Filters" description="Filter mentions by label, source, category, or language." />
        <CardBody>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MultiFilter label="Labels" options={uniqueValues(mentions, 'label')} value={labels} onChange={setLabels} />
            <MultiFilter label="Sources" options={uniqueValues(mentions, 'source_name')} value={sources} onChange={setSources} />
            <MultiFilter
              label="Categories"
              options={uniqueValues(mentions, 'category')}
              value={categories}
              onChange={setCategories}
            />
            <MultiFilter
              label="Languages"
              options={uniqueValues(mentions, 'language')}
              value={languages}
              onChange={setLanguages}
            />
          </div>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <MetricCard label="Filtered Mentions" value={filtered.length} tone="slate" />
            <MetricCard label="Filtered Unique Entities" value={uniqueValues(filtered, 'entity_text').length} tone="slate" />
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Entity Table" description="Raw entity mentions with source metadata and sentence context." />
        <CardBody>
          <DataTable
            rows={filtered}
            columns={[
              { key: 'entity_text', label: 'Entity' },
              { key: 'label', label: 'Label' },
              { key: 'source_name', label: 'Source' },
              { key: 'category', label: 'Category' },
              { key: 'language', label: 'Language' },
              { key: 'sentence', label: 'Sentence' },
            ]}
          />
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Entity Drilldown" description="Document-level contexts for one selected entity." />
        <CardBody className="space-y-4">
          <label className="block max-w-md text-sm font-semibold text-slate-700">
            Entity
            <select
              className="mt-1 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
              value={drilldownEntity}
              onChange={(event) => setSelectedEntity(event.target.value)}
            >
              {entityOptions.map((entity) => (
                <option key={entity} value={entity}>
                  {entity}
                </option>
              ))}
            </select>
          </label>
          <DataTable
            rows={contexts}
            columns={[
              { key: 'source_name', label: 'Source' },
              { key: 'category', label: 'Category' },
              { key: 'language', label: 'Language' },
              { key: 'labels', label: 'Labels' },
              { key: 'mention_count', label: 'Mentions' },
              { key: 'context', label: 'Context' },
            ]}
          />
        </CardBody>
      </Card>
    </div>
  );
}
