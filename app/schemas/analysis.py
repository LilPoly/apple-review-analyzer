import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "AnalysisMethod",
    "SentimentLabel",
    "SentimentPredictionDTO",
    "AnalysisResultDTO",
]


class AnalysisMethod(StrEnum):
    VADER = "vader"
    CLASSICAL = "classical"
    BERT = "bert"


class SentimentLabel(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class SentimentPredictionDTO(BaseModel):
    review_id: uuid.UUID
    label: SentimentLabel
    confidence: float = Field(ge=0.0, le=1.0)


class AnalysisResultDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    method: AnalysisMethod
    sentiment_distribution: dict[SentimentLabel, float]
    negative_keywords: list[str]
    predictions: list[SentimentPredictionDTO]
    execution_time_seconds: float | None
    created_at: datetime | None = None
