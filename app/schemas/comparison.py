import uuid

from pydantic import BaseModel

from app.schemas.analysis import AnalysisMethod

__all__ = ["MethodMetricsDTO", "ComparisonResultDTO"]


class MethodMetricsDTO(BaseModel):
    method: AnalysisMethod
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    execution_time_seconds: float | None


class ComparisonResultDTO(BaseModel):
    job_id: uuid.UUID
    classical: MethodMetricsDTO
    bert: MethodMetricsDTO
    disagreement_rate: float
    disagreement_review_ids: list[uuid.UUID]
