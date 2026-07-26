import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";

export default function IndustryChart({ data }) {
  if (!data) return null;

  const chartData = data
    .map((d) => ({ name: d.Industry, gain: d.avg_productivity_gain }))
    .sort((a, b) => b.gain - a.gain);

  return (
    <div className="rounded-xl bg-white p-6 shadow-sm border border-gray-100">
      <h2 className="mb-4 text-lg font-semibold">Productivity Gain by Industry</h2>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={chartData} margin={{ bottom: 40, left: 0, right: 0, top: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="name" angle={-35} textAnchor="end" tick={{ fontSize: 12 }} />
          <YAxis unit="%" tick={{ fontSize: 12 }} />
          <Tooltip formatter={(v) => `${v}%`} />
          <Bar dataKey="gain" fill="#3b82f6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
