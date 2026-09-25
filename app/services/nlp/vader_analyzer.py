import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

from app.core.constants import NEGATIVE_THRESHOLD, POSITIVE_THRESHOLD
from app.core.logger import get_logger
from app.schemas.analysis import SentimentLabel
from app.services.nlp.base import RawPrediction, SentimentAnalyzer

__all__ = ["VaderAnalyzer"]

logger = get_logger(__name__)


class VaderAnalyzer(SentimentAnalyzer):
    def __init__(self) -> None:
        nltk.download("vader_lexicon", quiet=True)
        self._sia = SentimentIntensityAnalyzer()
        logger.info("VaderAnalyzer initialized")

    @property
    def method_name(self) -> str:
        return "vader"

    def predict(self, texts: list[str]) -> list[RawPrediction]:
        predictions = []
        for text in texts:
            compound = self._sia.polarity_scores(text)["compound"]
            predictions.append(
                RawPrediction(
                    label=self._score_to_label(compound),
                    confidence=self._compound_to_confidence(compound),
                )
            )
        return predictions

    def _score_to_label(self, compound: float) -> SentimentLabel:
        if compound >= POSITIVE_THRESHOLD:
            return SentimentLabel.POSITIVE
        if compound <= NEGATIVE_THRESHOLD:
            return SentimentLabel.NEGATIVE
        return SentimentLabel.NEUTRAL

    def _compound_to_confidence(self, compound: float) -> float:
        """Map VADER's compound score [-1, 1] to a [0, 1] confidence value."""
        return round(abs(compound), 4)
