from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    industry: str = Field(..., examples=["Technology"])
    location: str = Field(..., examples=["US"])
    primary_ai_tool: str = Field(..., examples=["ChatGPT"])
    daily_token_usage: int = Field(..., ge=0, le=1_000_000, examples=[5000])
    tasks_automated_per_week: int = Field(..., ge=0, le=200, examples=[15])
    experience_years: float = Field(..., ge=0, le=50, examples=[3.5])


class PredictionOutput(BaseModel):
    productivity_gain_percent: float
    confidence_interval: tuple[float, float]
    risk_level: str


class SummaryResponse(BaseModel):
    global_avg_productivity_gain: float
    most_used_tool: str
    median_daily_tokens: int
    by_industry: list[dict]
    by_location: list[dict]
    tool_usage: list[dict]
    token_usage_distribution: list[dict]
    tasks_automated_distribution: list[dict]
    feature_importance: list[dict]
    total_respondents: int
