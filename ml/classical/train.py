import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

from app.core.logger import get_logger
from ml.classical.evaluate import evaluate_predictions
from ml.config import (
    CLASSICAL_MODEL_PATH,
    RANDOM_STATE,
    RAW_DATASET_PATH,
    TFIDF_MAX_FEATURES,
    TFIDF_NGRAM_RANGE,
)
from ml.datasets.preprocessing import load_and_label_dataset, split_dataset

__all__ = ["build_pipeline", "train_and_evaluate"]

logger = get_logger(__name__)


def build_pipeline() -> Pipeline:
    """Build the TF-IDF + Logistic Regression pipeline as a single sklearn object."""
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=TFIDF_MAX_FEATURES,
                    ngram_range=TFIDF_NGRAM_RANGE,
                    stop_words="english",
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    random_state=RANDOM_STATE,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def train_and_evaluate() -> Pipeline:
    logger.info("Loading and labeling dataset...")
    df = load_and_label_dataset(str(RAW_DATASET_PATH))
    train_df, val_df, test_df = split_dataset(df)
    logger.info(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

    pipeline = build_pipeline()

    logger.info("Training pipeline on train set...")
    pipeline.fit(train_df["text"], train_df["label"])

    val_predictions = pipeline.predict(val_df["text"])
    evaluate_predictions(
        val_df["label"].tolist(), val_predictions.tolist(), "validation set"
    )

    test_predictions = pipeline.predict(test_df["text"])
    test_metrics = evaluate_predictions(
        test_df["label"].tolist(), test_predictions.tolist(), "test set"
    )

    CLASSICAL_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, CLASSICAL_MODEL_PATH)
    logger.info(f"Model saved to {CLASSICAL_MODEL_PATH}")

    return pipeline, test_metrics


if __name__ == "__main__":
    train_and_evaluate()
