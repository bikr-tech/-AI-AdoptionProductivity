from contextlib import asynccontextmanager
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from xgboost import XGBRegressor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import PredictionInput, PredictionOutput, SummaryResponse

_BACKEND_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = _BACKEND_DIR / "models/model.pkl"
RAW_DATA = _BACKEND_DIR.parent / "data/raw/global_ai_adoption.csv"
FEATURE_IMP_PATH = _BACKEND_DIR.parent / "output/figures/feature_importance.csv"

PROJECT_ROOT = _BACKEND_DIR.parent

CAT_FEATURES = ["Industry", "Location", "Primary_AI_Tool"]
NUM_FEATURES = ["Daily_Token_Usage", "Tasks_Automated_Per_Week", "Experience_Years"]
TARGET = "Productivity_Gain_Percent"

pipeline = None


def _bootstrap():
    global pipeline
    if MODEL_PATH.exists():
        pipeline = joblib.load(MODEL_PATH)
        return

    RAW_DATA.parent.mkdir(parents=True, exist_ok=True)
    FEATURE_IMP_PATH.parent.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(42)
    ind = ["Healthcare", "Finance", "Education", "Retail", "Manufacturing", "Technology", "Legal", "Media"]
    locs = ["US", "UK", "India", "Germany", "Brazil", "Japan", "Canada", "Australia"]
    tools = ["ChatGPT", "GitHub Copilot", "Midjourney", "Salesforce Einstein", "TensorFlow", "Tableau", "Jasper", "Notion AI"]
    ind_eff = {"Technology": 10, "Finance": 7, "Healthcare": 5, "Media": 8, "Education": 4, "Retail": 3, "Manufacturing": 2, "Legal": 1}
    tool_eff = {"GitHub Copilot": 8, "ChatGPT": 7, "Jasper": 5, "Notion AI": 4, "TensorFlow": 6, "Tableau": 3, "Midjourney": 9, "Salesforce Einstein": 5}

    recs = []
    for _ in range(10_000):
        i = rng.choice(ind)
        l = rng.choice(locs)
        t = rng.choice(tools)
        tok = int(rng.lognormal(7.0, 1.2))
        tasks = int(rng.poisson(12))
        exp = max(0, int(rng.normal(3.5, 2.5)))
        g = max(0, 15 + ind_eff.get(i, 0) + tool_eff.get(t, 0) + np.log1p(tok) * 2.5 + tasks * 0.8 + exp * 1.2 + rng.normal(0, 4.0))
        recs.append({"Industry": i, "Location": l, "Primary_AI_Tool": t, "Daily_Token_Usage": tok, "Tasks_Automated_Per_Week": tasks, "Experience_Years": exp, "Productivity_Gain_Percent": round(g, 2)})

    df = pd.DataFrame(recs)
    mask = rng.random(df.shape) < 0.015
    df = df.mask(mask)
    df.to_csv(RAW_DATA, index=False)

    df = df.dropna(subset=[TARGET])
    X, y = df[CAT_FEATURES + NUM_FEATURES], df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessor = ColumnTransformer([
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("encode", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))]), CAT_FEATURES),
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUM_FEATURES),
    ])
    X_train_p = preprocessor.fit_transform(X_train)
    X_test_p = preprocessor.transform(X_test)

    model = XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.08, subsample=0.8, colsample_bytree=0.8, random_state=42, verbosity=0)
    model.fit(X_train_p, y_train)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"preprocessor": preprocessor, "model": model}, MODEL_PATH)

    imp = pd.DataFrame({"feature": CAT_FEATURES + NUM_FEATURES, "importance": model.feature_importances_}).sort_values("importance", ascending=False)
    imp.to_csv(FEATURE_IMP_PATH, index=False)

    pipeline = {"preprocessor": preprocessor, "model": model}
    print("Bootstrap complete: synthetic data + model generated")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _bootstrap()
    yield
    global pipeline
    pipeline = None


app = FastAPI(title="Global AI Adoption & Productivity API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ai-adoptionproductivity.onrender.com",
        "https://ai-adoptionproductivity-1.onrender.com",
    ],
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
        "tool_usage": _to_tool_usage(df),
        "token_usage_distribution": _bucket(df, "Daily_Token_Usage", [0, 500, 2000, 10000, 50000, int(1e9)], ["0-500", "501-2K", "2K-10K", "10K-50K", "50K+"]),
        "tasks_automated_distribution": _bucket(df, "Tasks_Automated_Per_Week", [-1, 5, 15, 30, 100], ["0-5", "6-15", "16-30", "30+"]),
        "feature_importance": (pd.read_csv(FEATURE_IMP_PATH).to_dict(orient="records") if FEATURE_IMP_PATH.exists() else []),
        "total_respondents": len(df),
    }


def _to_tool_usage(df):
    vc = df["Primary_AI_Tool"].value_counts().reset_index()
    vc.columns = ["tool", "count"]
    return vc.to_dict(orient="records")


def _bucket(df, col, bins, labels):
    vc = pd.cut(df[col], bins=bins, labels=labels).value_counts()
    result = vc.reset_index()
    result.columns = ["range", "count"]
    return result.sort_values("range").to_dict(orient="records")


@app.get("/analytics/summary", response_model=SummaryResponse)
def analytics_summary():
    return _compute_summary()
