import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";

export default function FeatureImportance({ data }) {
  if (!data) return null;

  const chartData = [...data]
    .sort((a, b) => a.importance - b.importance)
    .map((d) => ({ name: d.feature, importance: +(d.importance * 100).toFixed(1) }));

  return (
    <div className="rounded-xl bg-white p-6 shadow-sm border border-gray-100">
      <h2 className="mb-4 text-lg font-semibold">Feature Importance</h2>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 80, right: 20, top: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis type="number" unit="%" tick={{ fontSize: 12 }} />
          <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={120} />
          <Tooltip formatter={(v) => `${v}%`} />
          <Bar dataKey="importance" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
