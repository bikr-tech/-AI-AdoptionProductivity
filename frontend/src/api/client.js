const BASE = import.meta.env.DEV
  ? "http://localhost:8000"
  : "";

export async function fetchSummary() {
  const res = await fetch(`${BASE}/analytics/summary`);
  if (!res.ok) throw new Error(`Summary fetch failed: ${res.status}`);
  return res.json();
}

export async function postPrediction(data) {
  const res = await fetch(`${BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Prediction failed: ${res.status}`);
  return res.json();
}
