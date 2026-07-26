import { useState, useEffect } from "react";
import { fetchSummary } from "./api/client";
import MetricsBanner from "./components/MetricsBanner";
import PredictorForm from "./components/PredictorForm";
import IndustryChart from "./components/IndustryChart";
import FeatureImportance from "./components/FeatureImportance";
import { BarChart3, AlertCircle } from "lucide-react";

export default function App() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSummary()
      .then(setSummary)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b bg-white shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center gap-2 px-6 py-4">
          <BarChart3 className="h-6 w-6 text-blue-600" />
          <h1 className="text-xl font-bold">Global AI Adoption & Productivity</h1>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 px-6 py-8">
        {loading && (
          <div className="flex items-center justify-center py-20 text-gray-400">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center gap-2 py-20 text-red-500">
            <AlertCircle className="h-5 w-5" />
            <p>Failed to load dashboard: {error}</p>
          </div>
        )}

        {summary && (
          <>
            <MetricsBanner summary={summary} />

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <PredictorForm />
              <IndustryChart data={summary.by_industry} />
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <FeatureImportance data={summary.feature_importance} />
              <div className="rounded-xl bg-white p-6 shadow-sm border border-gray-100">
                <h2 className="mb-4 text-lg font-semibold">Token Usage Distribution</h2>
                <ul className="space-y-2">
                  {summary.token_usage_distribution.map((t) => (
                    <li key={t.range} className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">{t.range}</span>
                      <span className="font-medium">{t.count.toLocaleString()}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
