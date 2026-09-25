import time
import uuid

from app.core.logger import get_logger
from app.models.analysis_result import AnalysisResult
from app.db.unit_of_work import UnitOfWork
from app.schemas.analysis import (
    AnalysisMethod,
    AnalysisResultDTO,
    SentimentLabel,
    SentimentPredictionDTO,
)
from app.services.nlp.base import SentimentAnalyzer
from app.services.nlp.keyword_extractor import ContrastiveKeywordExtractor

__all__ = ["SentimentAnalysisService"]

logger = get_logger(__name__)


class SentimentAnalysisService:
    def __init__(
        self,
        uow: UnitOfWork,
        analyzers: list[SentimentAnalyzer],
        keyword_extractor: ContrastiveKeywordExtractor,
    ) -> None:
        self._uow = uow
        self._analyzers = analyzers
        self._keyword_extractor = keyword_extractor

    def analyze_job(self, job_id: uuid.UUID) -> list[AnalysisResultDTO]:
        with self._uow as uow:
            reviews = uow.reviews.get_by_job_id(job_id)
            if not reviews:
                raise ValueError(f"No reviews found for job_id='{job_id}'")

            texts = [review.text for review in reviews]
            review_ids = [review.id for review in reviews]

            results = []
            for analyzer in self._analyzers:
                result_dto = self._run_single_analyzer(
                    analyzer, texts, review_ids, job_id
                )
                results.append(result_dto)

                orm_result = AnalysisResult(
                    job_id=job_id,
                    method=analyzer.method_name,
                    metrics={
                        "sentiment_distribution": {
                            label.value: pct
                            for label, pct in result_dto.sentiment_distribution.items()
                        },
                        "negative_keywords": result_dto.negative_keywords,
                        "predictions": [
                            {
                                "review_id": str(pred.review_id),
                                "label": pred.label.value,
                                "confidence": pred.confidence,
                            }
                            for pred in result_dto.predictions
                        ],
                    },
                    execution_time_seconds=result_dto.execution_time_seconds,
                )
                uow.results.add(orm_result)

            uow.commit()
            return results

    def _run_single_analyzer(
        self,
        analyzer: SentimentAnalyzer,
        texts: list[str],
        review_ids: list[uuid.UUID],
        job_id: uuid.UUID,
    ) -> AnalysisResultDTO:
        logger.info(
            f"Running analyzer '{analyzer.method_name}' on {len(texts)} reviews"
        )

        start_time = time.perf_counter()
        raw_predictions = analyzer.predict(texts)
        execution_time = round(time.perf_counter() - start_time, 4)

        predictions = [
            SentimentPredictionDTO(
                review_id=review_id,
                label=raw.label,
                confidence=raw.confidence,
            )
            for review_id, raw in zip(review_ids, raw_predictions, strict=True)
        ]

        sentiment_distribution = self._calculate_distribution(predictions)

        negative_texts = [
            text
            for text, pred in zip(texts, predictions, strict=True)
            if pred.label == SentimentLabel.NEGATIVE
        ]
        positive_texts = [
            text
            for text, pred in zip(texts, predictions, strict=True)
            if pred.label == SentimentLabel.POSITIVE
        ]
        negative_keywords = self._keyword_extractor.extract(
            negative_texts, positive_texts
        )

        return AnalysisResultDTO(
            id=uuid.uuid4(),
            job_id=job_id,
            method=AnalysisMethod(analyzer.method_name),
            sentiment_distribution=sentiment_distribution,
            negative_keywords=negative_keywords,
            predictions=predictions,
            execution_time_seconds=execution_time,
            created_at=None,
        )

    def _calculate_distribution(
        self, predictions: list[SentimentPredictionDTO]
    ) -> dict[SentimentLabel, float]:
        total = len(predictions)
        if total == 0:
            return {label: 0.0 for label in SentimentLabel}

        counts = {label: 0 for label in SentimentLabel}
        for pred in predictions:
            counts[pred.label] += 1

        return {
            label: round((count / total) * 100, 2) for label, count in counts.items()
        }
