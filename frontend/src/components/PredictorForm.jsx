import { useState } from "react";
import { postPrediction } from "../api/client";
import { Loader2 } from "lucide-react";

const INDUSTRIES = [
  "Healthcare", "Finance", "Education", "Retail",
  "Manufacturing", "Technology", "Legal", "Media",
];
const LOCATIONS = ["US", "UK", "India", "Germany", "Brazil", "Japan", "Canada", "Australia"];
const TOOLS = [
  "ChatGPT", "GitHub Copilot", "Midjourney", "Salesforce Einstein",
  "TensorFlow", "Tableau", "Jasper", "Notion AI",
];

export default function PredictorForm() {
  const [form, setForm] = useState({
    industry: "Technology",
    location: "US",
    primary_ai_tool: "ChatGPT",
    daily_token_usage: 5000,
    tasks_automated_per_week: 15,
    experience_years: 3.5,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await postPrediction({
        ...form,
        daily_token_usage: Number(form.daily_token_usage),
        tasks_automated_per_week: Number(form.tasks_automated_per_week),
        experience_years: Number(form.experience_years),
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-xl bg-white p-6 shadow-sm border border-gray-100">
      <h2 className="mb-4 text-lg font-semibold">Predict Productivity Gain</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-600">Industry</label>
            <select name="industry" value={form.industry} onChange={handleChange}
              className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm">
              {INDUSTRIES.map((v) => <option key={v}>{v}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600">Location</label>
            <select name="location" value={form.location} onChange={handleChange}
              className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm">
              {LOCATIONS.map((v) => <option key={v}>{v}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600">Primary AI Tool</label>
            <select name="primary_ai_tool" value={form.primary_ai_tool} onChange={handleChange}
              className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm">
              {TOOLS.map((v) => <option key={v}>{v}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600">Daily Token Usage</label>
            <input type="number" name="daily_token_usage" value={form.daily_token_usage}
              onChange={handleChange} min={0} max={1000000}
              className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600">Tasks Automated / Week</label>
            <input type="number" name="tasks_automated_per_week" value={form.tasks_automated_per_week}
              onChange={handleChange} min={0} max={200}
              className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600">Experience (Years)</label>
            <input type="number" name="experience_years" value={form.experience_years}
              onChange={handleChange} min={0} max={50} step={0.5}
              className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm" />
          </div>
        </div>

        <button type="submit" disabled={loading}
          className="flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-2 text-white font-medium hover:bg-blue-700 disabled:opacity-50">
          {loading && <Loader2 className="h-4 w-4 animate-spin" />}
          {loading ? "Predicting..." : "Predict"}
        </button>
      </form>

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      {result && (
        <div className="mt-4 rounded-lg bg-gray-50 p-4">
          <p className="text-lg font-semibold">
            Predicted Gain: <span className="text-blue-600">{result.productivity_gain_percent}%</span>
          </p>
          <p className="text-sm text-gray-500">
            CI: ({result.confidence_interval[0]} – {result.confidence_interval[1]}) &middot;
            Risk: <span className={`font-medium ${result.risk_level === "low" ? "text-green-600" : result.risk_level === "medium" ? "text-yellow-600" : "text-red-600"}`}>
              {result.risk_level}
            </span>
          </p>
        </div>
      )}
    </div>
  );
}
