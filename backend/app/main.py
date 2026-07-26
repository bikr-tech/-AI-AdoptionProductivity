from contextlib import asynccontextmanager
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import PredictionInput, PredictionOutput, SummaryResponse

_BACKEND_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = _BACKEND_DIR / "models/model.pkl"
RAW_DATA = _BACKEND_DIR.parent / "data/raw/global_ai_adoption.csv"
FEATURE_IMP_PATH = _BACKEND_DIR.parent / "output/figures/feature_importance.csv"

CAT_FEATURES = ["Industry", "Location", "Primary_AI_Tool"]
NUM_FEATURES = ["Daily_Token_Usage", "Tasks_Automated_Per_Week", "Experience_Years"]
TARGET = "Productivity_Gain_Percent"

pipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline
    if MODEL_PATH.exists():
        pipeline = joblib.load(MODEL_PATH)
    yield
    pipeline = None


app = FastAPI(title="Global AI Adoption & Productivity API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": pipeline is not None}


@app.post("/predict", response_model=PredictionOutput)
def predict(input_data: PredictionInput):
    if pipeline is None:
        raise HTTPException(503, detail="Model not loaded. Run training first.")

    preprocessor = pipeline["preprocessor"]
    model = pipeline["model"]

    row = pd.DataFrame([{
        "Industry": input_data.industry,
        "Location": input_data.location,
        "Primary_AI_Tool": input_data.primary_ai_tool,
        "Daily_Token_Usage": input_data.daily_token_usage,
        "Tasks_Automated_Per_Week": input_data.tasks_automated_per_week,
        "Experience_Years": input_data.experience_years,
    }])

    X = preprocessor.transform(row[CAT_FEATURES + NUM_FEATURES])
    pred = float(model.predict(X)[0])

    conf_width = 3.5
    ci = (round(pred - conf_width, 2), round(pred + conf_width, 2))
    risk = "low" if pred < 15 else "medium" if pred < 30 else "high"

    return PredictionOutput(
        productivity_gain_percent=round(pred, 2),
        confidence_interval=ci,
        risk_level=risk,
    )


def _compute_summary() -> dict:
    df = pd.read_csv(RAW_DATA).dropna(subset=[TARGET])

    return {
        "global_avg_productivity_gain": round(float(df[TARGET].mean()), 2),
        "most_used_tool": str(df["Primary_AI_Tool"].mode().iloc[0]),
        "median_daily_tokens": int(df["Daily_Token_Usage"].median()),
        "by_industry": (
            df.groupby("Industry")[TARGET]
            .agg(["mean", "std", "count"])
            .round(2)
            .reset_index()
            .rename(columns={"mean": "avg_productivity_gain", "std": "std_productivity_gain", "count": "respondent_count"})
            .to_dict(orient="records")
        ),
        "by_location": (
            df.groupby("Location")[TARGET]
            .mean().round(2).reset_index().to_dict(orient="records")
        ),
        "tool_usage": (
            df["Primary_AI_Tool"].value_counts().reset_index()
            .rename(columns={"index": "tool", "Primary_AI_Tool": "count"})
            .to_dict(orient="records")
        ),
        "token_usage_distribution": _bucket(df, "Daily_Token_Usage", [0, 500, 2000, 10000, 50000, int(1e9)], ["0-500", "501-2K", "2K-10K", "10K-50K", "50K+"]),
        "tasks_automated_distribution": _bucket(df, "Tasks_Automated_Per_Week", [-1, 5, 15, 30, 100], ["0-5", "6-15", "16-30", "30+"]),
        "feature_importance": (pd.read_csv(FEATURE_IMP_PATH).to_dict(orient="records") if FEATURE_IMP_PATH.exists() else []),
        "total_respondents": len(df),
    }


def _bucket(df, col, bins, labels):
    vc = pd.cut(df[col], bins=bins, labels=labels).value_counts()
    result = vc.reset_index()
    result.columns = ["range", "count"]
    return result.sort_values("range").to_dict(orient="records")


@app.get("/analytics/summary", response_model=SummaryResponse)
def analytics_summary():
    return _compute_summary()
