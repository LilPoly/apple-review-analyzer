import json

from app.core.logger import get_logger
from ml.bert.evaluate import evaluate_saved_bert
from ml.classical.train import train_and_evaluate
from ml.config import BASELINE_METRICS_PATH
from ml.nltk_ml.evaluate import evaluate_nltk

__all__ = ["generate_baseline_report"]

logger = get_logger(__name__)


def generate_baseline_report() -> None:
    logger.info("Evaluating VADER...")
    vader_metrics = evaluate_nltk()

    logger.info("Evaluating Classical (TF-IDF + LogisticRegression)...")
    _, classical_metrics = train_and_evaluate()

    logger.info("Evaluating BERT...")
    bert_metrics = evaluate_saved_bert()

    report = {
        "vader": vader_metrics,
        "classical": classical_metrics,
        "bert": bert_metrics,
    }

    BASELINE_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BASELINE_METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Baseline report saved to {BASELINE_METRICS_PATH}")


if __name__ == "__main__":
    generate_baseline_report()
