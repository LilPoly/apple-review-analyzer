from pathlib import Path

__all__ = [
    "RAW_DATASET_PATH",
    "PROCESSED_DATASET_PATH",
    "CLASSICAL_MODEL_PATH",
    "BERT_MODEL_PATH",
    "TEXT_COLUMN",
    "RATING_COLUMN",
    "RANDOM_STATE",
    "TEST_SIZE",
    "VAL_SIZE",
    "TFIDF_MAX_FEATURES",
    "TFIDF_NGRAM_RANGE",
    "LABELS",
]

_ML_ROOT = Path(__file__).parent

RAW_DATASET_PATH = _ML_ROOT / "data" / "raw" / "google_play_reviews.csv"
PROCESSED_DATASET_PATH = _ML_ROOT / "data" / "processed" / "labeled_reviews.csv"

CLASSICAL_MODEL_PATH = _ML_ROOT / "artifacts" / "classical" / "tfidf_logreg_v1.joblib"
BERT_MODEL_PATH = _ML_ROOT / "artifacts" / "bert" / "bert-sentiment-v1"

TEXT_COLUMN = "content"
RATING_COLUMN = "score"

RANDOM_STATE = 42
TEST_SIZE = 0.1
VAL_SIZE = 0.1

RATING_TO_LABEL = {
    1: "negative",
    2: "negative",
    3: "neutral",
    4: "positive",
    5: "positive",
}

TFIDF_MAX_FEATURES = 5000
TFIDF_NGRAM_RANGE = (1, 2)
LABELS = ["negative", "neutral", "positive"]

BERT_MODEL_NAME = "distilbert-base-uncased"
BERT_MAX_LENGTH = 128
BERT_BATCH_SIZE = 16
BERT_EPOCHS = 2
