import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.core.logger import get_logger
from app.schemas.analysis import SentimentLabel
from app.services.nlp.base import RawPrediction, SentimentAnalyzer

__all__ = ["BertAnalyzer"]

logger = get_logger(__name__)


class BertAnalyzer(SentimentAnalyzer):
    def __init__(self, model_path: str, max_length: int = 128) -> None:
        self._device = self._resolve_device()
        self._tokenizer = AutoTokenizer.from_pretrained(model_path)
        self._model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self._model.to(self._device)
        self._model.eval()
        self._max_length = max_length
        logger.info(f"BertAnalyzer loaded from {model_path} on device={self._device}")

    @property
    def method_name(self) -> str:
        return "bert"

    def predict(self, texts: list[str]) -> list[RawPrediction]:
        inputs = self._tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self._max_length,
            return_tensors="pt",
        ).to(self._device)

        with torch.no_grad():
            outputs = self._model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)

        predictions = []
        for proba_row in probabilities:
            label_id = int(torch.argmax(proba_row).item())
            label_str = self._model.config.id2label[label_id]
            confidence = round(float(proba_row[label_id].item()), 4)
            predictions.append(
                RawPrediction(label=SentimentLabel(label_str), confidence=confidence)
            )
        return predictions

    def _resolve_device(self) -> str:
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"
