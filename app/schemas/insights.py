import uuid

from pydantic import BaseModel

from app.schemas.analysis import AnalysisMethod, SentimentLabel

__all__ = ["AnomalyDTO", "AnomalyReportDTO", "ActionableInsightsDTO"]


class AnomalyDTO(BaseModel):
    review_id: uuid.UUID
    text: str
    rating: int
    rating_based_label: SentimentLabel
    predicted_label: SentimentLabel
    confidence: float


class AnomalyReportDTO(BaseModel):
    job_id: uuid.UUID
    method: AnalysisMethod
    total_reviews: int
    anomalies_count: int
    anomaly_rate: float
    top_anomalies: list[AnomalyDTO]


class ActionableInsightsDTO(BaseModel):
    job_id: uuid.UUID
    method: str
    negative_keywords: list[str]
    insights: list[str]
    generated_by: str
