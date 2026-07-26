import { TrendingUp, Cpu, BarChart3 } from "lucide-react";

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="flex items-center gap-4 rounded-xl bg-white p-5 shadow-sm border border-gray-100">
      <div className={`rounded-lg p-3 ${color}`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
    </div>
  );
}

export default function MetricsBanner({ summary }) {
  if (!summary) return null;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <StatCard
        icon={TrendingUp}
        label="Global Avg Productivity Gain"
        value={`${summary.global_avg_productivity_gain}%`}
        color="bg-blue-600"
      />
      <StatCard
        icon={Cpu}
        label="Most Used AI Tool"
        value={summary.most_used_tool}
        color="bg-emerald-600"
      />
      <StatCard
        icon={BarChart3}
        label="Median Daily Tokens"
        value={summary.median_daily_tokens.toLocaleString()}
        color="bg-purple-600"
      />
    </div>
  );
}
