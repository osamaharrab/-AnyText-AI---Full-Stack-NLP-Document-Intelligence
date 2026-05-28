import { truncate } from '../lib/format.js';

function renderValue(value) {
  if (value === null || value === undefined || value === '') return 'Unknown';
  if (typeof value === 'number') return Number.isInteger(value) ? value.toLocaleString() : value.toFixed(4);
  return truncate(value, 180);
}

export function DataTable({ rows, columns, empty = 'No data available.', limit, className = '' }) {
  const data = limit ? (rows || []).slice(0, limit) : rows || [];
  const resolvedColumns =
    columns ||
    Array.from(
      data.reduce((set, row) => {
        Object.keys(row || {}).forEach((key) => set.add(key));
        return set;
      }, new Set()),
    ).map((key) => ({ key, label: key.replaceAll('_', ' ') }));

  if (!data.length) {
    return <div className="rounded-lg border border-slate-200 bg-slate-50 p-5 text-sm text-slate-500">{empty}</div>;
  }

  return (
    <div className={`table-scroll overflow-auto rounded-lg border border-slate-200 ${className}`}>
      <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
        <thead className="bg-slate-50">
          <tr>
            {resolvedColumns.map((column) => (
              <th
                key={column.key}
                scope="col"
                className={`whitespace-nowrap px-4 py-3 text-xs font-bold uppercase text-slate-500 ${
                  column.className || ''
                }`}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {data.map((row, index) => (
            <tr key={`${row?.id || row?.document_id || row?.entity_text || 'row'}-${index}`} className="align-top">
              {resolvedColumns.map((column) => (
                <td key={column.key} className={`px-4 py-3 text-slate-700 ${column.cellClassName || ''}`}>
                  {column.render ? column.render(row) : renderValue(row?.[column.key])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
