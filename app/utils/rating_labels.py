# app/utils/rating_labels.py
from app.schemas.analysis import SentimentLabel

__all__ = ["rating_to_label"]

_RATING_TO_LABEL = {
    1: SentimentLabel.NEGATIVE,
    2: SentimentLabel.NEGATIVE,
    3: SentimentLabel.NEUTRAL,
    4: SentimentLabel.POSITIVE,
    5: SentimentLabel.POSITIVE,
}


def rating_to_label(rating: int) -> SentimentLabel:
    return _RATING_TO_LABEL[rating]
