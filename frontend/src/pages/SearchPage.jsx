import { Search } from 'lucide-react';
import { useState } from 'react';
import { Button } from '../components/Button.jsx';
import { Card, CardBody, CardHeader } from '../components/Card.jsx';
import { EmptyState } from '../components/EmptyState.jsx';
import { formatPercent } from '../lib/format.js';
import { searchDocuments } from '../lib/api.js';

const EXAMPLES = ['Apple', 'public health', 'Amman', 'climate policy', 'artificial intelligence'];

export function SearchPage({ analysis, setError }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);

  if (!analysis) {
    return <EmptyState icon={Search} title="Nothing to search" message="Load or analyze documents first." />;
  }

  async function runSearch(event) {
    event?.preventDefault();
    if (!query.trim()) return;
    setError('');
    setSearching(true);
    try {
      const response = await searchDocuments({
        query,
        documents: analysis.documents || [],
        topK: 8,
      });
      setResults(response.results || []);
    } catch (error) {
      setError(error.message);
    } finally {
      setSearching(false);
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader title="Search Documents" description="Keyword-based TF-IDF search with cosine similarity ranking." />
        <CardBody>
          <form className="flex flex-col gap-3 sm:flex-row" onSubmit={runSearch}>
            <input
              className="min-h-11 flex-1 rounded-md border border-slate-200 px-4 text-sm"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search organizations, places, themes, or policy topics"
            />
            <Button icon={Search} variant="primary" type="submit" disabled={searching || !query.trim()}>
              Search
            </Button>
          </form>
          <div className="mt-4 flex flex-wrap gap-2">
            {EXAMPLES.map((example) => (
              <button
                key={example}
                type="button"
                className="rounded-md border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:border-brand-500 hover:text-brand-700"
                onClick={() => setQuery(example)}
              >
                {example}
              </button>
            ))}
          </div>
        </CardBody>
      </Card>

      <div className="space-y-4">
        {results.length ? (
          results.map((result) => (
            <Card key={result.id}>
              <CardBody>
                <div className="grid gap-4 sm:grid-cols-[7rem_1fr]">
                  <div className="rounded-lg bg-brand-50 p-4 text-center">
                    <p className="text-xs font-bold uppercase text-brand-700">Match</p>
                    <p className="mt-2 text-2xl font-bold text-brand-700">
                      {formatPercent(result.similarity_score)}
                    </p>
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-950">{result.source_name || result.id}</h3>
                    <p className="mt-1 text-xs font-semibold uppercase text-slate-500">
                      {result.category || 'unknown'} / {String(result.language || 'unknown').toUpperCase()}
                    </p>
                    <p className="mt-3 text-sm leading-6 text-slate-700">{result.text_preview}</p>
                  </div>
                </div>
              </CardBody>
            </Card>
          ))
        ) : (
          <EmptyState icon={Search} title="No search results" message="Submit a query to see ranked document cards." />
        )}
      </div>
    </div>
  );
}
