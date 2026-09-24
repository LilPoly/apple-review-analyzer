import torch
from transformers import pipeline

from app.core.logger import get_logger
from ml.classical.evaluate import evaluate_predictions
from ml.config import BERT_MAX_LENGTH, BERT_MODEL_PATH, RAW_DATASET_PATH
from ml.datasets.preprocessing import load_and_label_dataset, split_dataset

__all__ = ["evaluate_saved_bert"]

logger = get_logger(__name__)


def evaluate_saved_bert() -> dict | None:
    """Load the fine-tuned BERT model from disk and evaluate it on the test set."""
    if not BERT_MODEL_PATH.exists():
        logger.error(
            f"Model not found at {BERT_MODEL_PATH}. Please run train.py first."
        )
        return None

    logger.info("Loading dataset for evaluation...")
    df = load_and_label_dataset(str(RAW_DATASET_PATH))
    _, _, test_df = split_dataset(df)

    logger.info(f"Loading BERT model from {BERT_MODEL_PATH} via pipeline...")
    device = (
        "cuda"
        if torch.cuda.is_available()
        else ("mps" if torch.backends.mps.is_available() else "cpu")
    )

    nlp_pipeline = pipeline(
        task="text-classification",
        model=str(BERT_MODEL_PATH),
        tokenizer=str(BERT_MODEL_PATH),
        device=device,
        truncation=True,
        max_length=BERT_MAX_LENGTH,
    )

    logger.info("Running predictions on test set...")
    raw_predictions = nlp_pipeline(test_df["text"].tolist())

    y_pred = [pred["label"] for pred in raw_predictions]
    y_true = test_df["label"].tolist()

    metrics = evaluate_predictions(y_true, y_pred, "test set (Saved BERT)")
    return metrics


if __name__ == "__main__":
    evaluate_saved_bert()
