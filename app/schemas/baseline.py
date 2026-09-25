from pydantic import BaseModel

__all__ = ["PerClassMetricsDTO", "MethodBaselineMetricsDTO", "BaselineMetricsResponse"]


class PerClassMetricsDTO(BaseModel):
    precision: float
    recall: float
    f1: float


class MethodBaselineMetricsDTO(BaseModel):
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    per_class: dict[str, PerClassMetricsDTO]


class BaselineMetricsResponse(BaseModel):
    vader: MethodBaselineMetricsDTO
    classical: MethodBaselineMetricsDTO
    bert: MethodBaselineMetricsDTO
