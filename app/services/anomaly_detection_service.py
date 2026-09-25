import uuid

from app.core.logger import get_logger
from app.db.unit_of_work import UnitOfWork
from app.schemas.analysis import AnalysisMethod
from app.schemas.insights import AnomalyDTO, AnomalyReportDTO
from app.utils.rating_labels import rating_to_label

__all__ = ["AnomalyDetectionService"]

logger = get_logger(__name__)


class AnomalyDetectionService:
    def __init__(self, uow: UnitOfWork, top_n: int = 10) -> None:
        self._uow = uow
        self._top_n = top_n

    def detect(self, job_id: uuid.UUID, method: AnalysisMethod) -> AnomalyReportDTO:
        with self._uow as uow:
            reviews = uow.reviews.get_by_job_id(job_id)
            if not reviews:
                raise ValueError(f"No reviews found for job_id='{job_id}'")

            result = uow.results.get_by_job_and_method(job_id, method.value)
            if not result:
                raise ValueError(
                    f"No analysis result found for job_id='{job_id}', method='{method.value}'. "
                    "Run the analysis first."
                )

            predictions_by_review_id = self._extract_predictions(result)
            anomalies = self._find_anomalies(reviews, predictions_by_review_id)

        anomalies.sort(key=lambda a: a.confidence, reverse=True)

        return AnomalyReportDTO(
            job_id=job_id,
            method=method,
            total_reviews=len(reviews),
            anomalies_count=len(anomalies),
            anomaly_rate=round((len(anomalies) / len(reviews)) * 100, 2)
            if reviews
            else 0.0,
            top_anomalies=anomalies[: self._top_n],
        )

    def _extract_predictions(self, result) -> dict[uuid.UUID, dict]:
        """Extract per-review predictions from the stored AnalysisResult.metrics JSON."""
        predictions = result.metrics.get("predictions", [])
        return {uuid.UUID(p["review_id"]): p for p in predictions}

    def _find_anomalies(
        self, reviews, predictions_by_review_id: dict
    ) -> list[AnomalyDTO]:
        anomalies = []
        for review in reviews:
            prediction = predictions_by_review_id.get(review.id)
            if prediction is None:
                continue

            rating_based_label = rating_to_label(review.rating)
            predicted_label = prediction["label"]

            if predicted_label != rating_based_label.value:
                anomalies.append(
                    AnomalyDTO(
                        review_id=review.id,
                        text=review.text,
                        rating=review.rating,
                        rating_based_label=rating_based_label,
                        predicted_label=predicted_label,
                        confidence=prediction["confidence"],
                    )
                )
        return anomalies
