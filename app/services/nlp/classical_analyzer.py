import joblib

from app.core.logger import get_logger
from app.schemas.analysis import SentimentLabel
from app.services.nlp.base import RawPrediction, SentimentAnalyzer

__all__ = ["ClassicalAnalyzer"]

logger = get_logger(__name__)


class ClassicalAnalyzer(SentimentAnalyzer):
    def __init__(self, model_path: str) -> None:
        self._pipeline = joblib.load(model_path)
        logger.info(f"ClassicalAnalyzer loaded from {model_path}")

    @property
    def method_name(self) -> str:
        return "classical"

    def predict(self, texts: list[str]) -> list[RawPrediction]:
        labels = self._pipeline.predict(texts)
        probabilities = self._pipeline.predict_proba(texts)
        class_order = self._pipeline.classes_

        predictions = []
        for label_str, proba_row in zip(labels, probabilities, strict=True):
            confidence = self._extract_confidence(label_str, proba_row, class_order)
            predictions.append(
                RawPrediction(
                    label=SentimentLabel(label_str),
                    confidence=confidence,
                )
            )
        return predictions

    def _extract_confidence(self, label: str, proba_row, class_order) -> float:
        label_index = list(class_order).index(label)
        return round(float(proba_row[label_index]), 4)
