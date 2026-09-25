import os
from pathlib import Path
from huggingface_hub import snapshot_download
from app.core.logger import get_logger

logger = get_logger(__name__)

MODEL_REPO = "LizaPolozenko/apple-review-bert-sentiment"


def ensure_model_downloaded(local_path: str) -> None:
    path = Path(local_path)
    if path.exists() and any(path.iterdir()):
        logger.info(f"Model already present at {local_path}, skipping download.")
        return

    logger.info(f"Downloading model '{MODEL_REPO}' into {local_path}...")
    snapshot_download(
        repo_id=MODEL_REPO,
        local_dir=local_path,
    )
    logger.info("Model download complete.")


if __name__ == "__main__":
    model_path = os.environ.get(
        "BERT_MODEL_PATH", "ml/artifacts/bert/bert-sentiment-v1"
    )
    ensure_model_downloaded(model_path)
