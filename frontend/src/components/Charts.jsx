import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const COLORS = ['#2563eb', '#7c3aed', '#0891b2', '#059669', '#d97706', '#db2777', '#475569'];

export function SimpleBarChart({ data, xKey, yKey, height = 280 }) {
  if (!data?.length) {
    return <div className="rounded-lg bg-slate-50 p-5 text-sm text-slate-500">No chart data available.</div>;
  }

  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 16, bottom: 24, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
          <XAxis dataKey={xKey} tick={{ fontSize: 12 }} stroke="#64748b" interval={0} angle={-18} textAnchor="end" />
          <YAxis tick={{ fontSize: 12 }} stroke="#64748b" width={44} />
          <Tooltip
            cursor={{ fill: '#f1f5f9' }}
            contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }}
          />
          <Bar dataKey={yKey} radius={[6, 6, 0, 0]}>
            {data.map((_, index) => (
              <Cell key={`bar-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function DonutChart({ data, nameKey, valueKey, height = 260 }) {
  if (!data?.length) {
    return <div className="rounded-lg bg-slate-50 p-5 text-sm text-slate-500">No chart data available.</div>;
  }

  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey={valueKey}
            nameKey={nameKey}
            innerRadius={54}
            outerRadius={88}
            paddingAngle={2}
          >
            {data.map((_, index) => (
              <Cell key={`slice-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
