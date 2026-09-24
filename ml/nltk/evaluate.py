import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

from app.core.logger import get_logger
from ml.classical.evaluate import evaluate_predictions
from ml.config import RAW_DATASET_PATH
from ml.datasets.preprocessing import load_and_label_dataset, split_dataset

__all__ = ["evaluate_nltk"]

logger = get_logger(__name__)


def evaluate_nltk() -> dict:
    """Evaluate NLTK VADER performance on the test set."""
    logger.info("Downloading VADER lexicon (if not present)...")
    nltk.download("vader_lexicon", quiet=True)

    sia = SentimentIntensityAnalyzer()

    logger.info("Loading dataset for evaluation...")
    df = load_and_label_dataset(str(RAW_DATASET_PATH))
    _, _, test_df = split_dataset(df)

    logger.info("Running NLTK VADER predictions on test set...")
    y_pred = []
    for text in test_df["text"]:
        score = sia.polarity_scores(text)["compound"]

        if score >= 0.05:
            y_pred.append("positive")
        elif score <= -0.05:
            y_pred.append("negative")
        else:
            y_pred.append("neutral")

    y_true = test_df["label"].tolist()

    metrics = evaluate_predictions(y_true, y_pred, "test set (NLTK VADER)")
    return metrics


if __name__ == "__main__":
    evaluate_nltk()
