from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.analysis import SentimentLabel

__all__ = ["SentimentAnalyzer", "RawPrediction"]


@dataclass(frozen=True)
class RawPrediction:
    label: SentimentLabel
    confidence: float


class SentimentAnalyzer(ABC):
    @property
    @abstractmethod
    def method_name(self) -> str: ...

    @abstractmethod
    def predict(self, texts: list[str]) -> list[RawPrediction]:
        """Predict sentiment for a batch of texts, in the same order as the input."""
        ...
