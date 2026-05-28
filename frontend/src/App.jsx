import {
  BarChart3,
  Download,
  FileSearch,
  FileText,
  GitBranch,
  HelpCircle,
  Home,
  KeyRound,
  Search,
  Tags,
} from 'lucide-react';
import { useMemo, useState } from 'react';
import { Button } from './components/Button.jsx';
import { InputPage } from './pages/InputPage.jsx';
import { OverviewPage } from './pages/OverviewPage.jsx';
import { EntitiesPage } from './pages/EntitiesPage.jsx';
import { KeywordsPage } from './pages/KeywordsPage.jsx';
import { ExplorerPage } from './pages/ExplorerPage.jsx';
import { RelationshipsPage } from './pages/RelationshipsPage.jsx';
import { SearchPage } from './pages/SearchPage.jsx';
import { AskPage } from './pages/AskPage.jsx';
import { ReportPage } from './pages/ReportPage.jsx';
import { DownloadsPage } from './pages/DownloadsPage.jsx';
import { formatNumber } from './lib/format.js';

const NAV_ITEMS = [
  { id: 'Input', icon: Home },
  { id: 'Overview', icon: BarChart3 },
  { id: 'Entities', icon: Tags },
  { id: 'Keywords', icon: KeyRound },
  { id: 'Explorer', icon: FileSearch },
  { id: 'Relationships', icon: GitBranch },
  { id: 'Search', icon: Search },
  { id: 'Ask', icon: HelpCircle },
  { id: 'Report', icon: FileText },
  { id: 'Downloads', icon: Download },
];

export default function App() {
  const [activePage, setActivePage] = useState('Input');
  const [analysis, setAnalysis] = useState(null);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');

  const status = useMemo(() => {
    if (busy) return busy;
    if (!analysis) return 'No corpus loaded';
    return `${formatNumber(analysis.corpus_stats?.document_count || 0)} documents analyzed`;
  }, [analysis, busy]);

  function handleAnalysis(result) {
    setAnalysis(result);
    setActivePage('Overview');
  }

  const pageProps = { analysis, setError };
  const page = {
    Input: (
      <InputPage
        analysis={analysis}
        onAnalysis={handleAnalysis}
        setBusy={setBusy}
        busy={busy}
        setError={setError}
      />
    ),
    Overview: <OverviewPage analysis={analysis} />,
    Entities: <EntitiesPage analysis={analysis} />,
    Keywords: <KeywordsPage analysis={analysis} />,
    Explorer: <ExplorerPage analysis={analysis} />,
    Relationships: <RelationshipsPage analysis={analysis} />,
    Search: <SearchPage {...pageProps} />,
    Ask: <AskPage {...pageProps} />,
    Report: <ReportPage analysis={analysis} />,
    Downloads: <DownloadsPage {...pageProps} />,
  }[activePage];

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 text-white">
                  <FileText className="h-5 w-5" aria-hidden="true" />
                </div>
                <div>
                  <p className="text-lg font-bold text-slate-950">AnyText AI</p>
                  <p className="text-sm text-slate-500">NLP Document Intelligence</p>
                </div>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <span className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700">
                {status}
              </span>
              <Button variant="subtle" onClick={() => setActivePage('Input')}>
                New analysis
              </Button>
            </div>
          </div>

          <nav className="table-scroll flex gap-2 overflow-x-auto pb-1" aria-label="Primary navigation">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const active = activePage === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  className={`inline-flex min-h-10 shrink-0 items-center gap-2 rounded-md border px-3 py-2 text-sm font-semibold transition ${
                    active
                      ? 'border-brand-600 bg-brand-600 text-white shadow-sm'
                      : 'border-slate-200 bg-white text-slate-700 hover:border-brand-500 hover:text-brand-700'
                  }`}
                  onClick={() => setActivePage(item.id)}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  {item.id}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {error ? (
          <div className="mb-6 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-800">
            {error}
          </div>
        ) : null}

        {analysis?.metadata?.warnings?.length ? (
          <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {analysis.metadata.warnings.join(' ')}
          </div>
        ) : null}

        {page}
      </main>
    </div>
  );
}
