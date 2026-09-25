import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_anomaly_detection_service,
    get_insights_generator,
    get_sentiment_analysis_service,
    get_uow,
)
from app.core.logger import get_logger
from app.db.unit_of_work import UnitOfWork
from app.schemas.analysis import AnalysisMethod, AnalysisResultDTO
from app.schemas.insights import ActionableInsightsDTO, AnomalyReportDTO
from app.services.anomaly_detection_service import AnomalyDetectionService
from app.services.insights.base import InsightsGenerator
from app.services.sentiment_analysis_service import SentimentAnalysisService

__all__ = ["router"]

router = APIRouter(prefix="/jobs", tags=["Analysis"])
logger = get_logger(__name__)


@router.post("/{job_id}/insights", response_model=list[AnalysisResultDTO])
def analyze_job_insights(
    job_id: uuid.UUID,
    service: Annotated[
        SentimentAnalysisService, Depends(get_sentiment_analysis_service)
    ],
) -> list[AnalysisResultDTO]:
    try:
        return service.analyze_job(job_id)
    except ValueError as exc:
        logger.warning(f"Analysis failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.get("/{job_id}/anomalies", response_model=AnomalyReportDTO)
def get_anomalies(
    job_id: uuid.UUID,
    method: AnalysisMethod,
    service: Annotated[AnomalyDetectionService, Depends(get_anomaly_detection_service)],
) -> AnomalyReportDTO:
    try:
        return service.detect(job_id, method)
    except ValueError as exc:
        logger.warning(f"Anomaly detection failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.get("/{job_id}/actionable-insights", response_model=ActionableInsightsDTO)
def get_actionable_insights(
    job_id: uuid.UUID,
    method: AnalysisMethod,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    generator: Annotated[InsightsGenerator, Depends(get_insights_generator)],
) -> ActionableInsightsDTO:
    with uow:
        result = uow.results.get_by_job_and_method(job_id, method.value)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No analysis result for job_id='{job_id}', method='{method.value}'",
            )

        negative_keywords = result.metrics.get("negative_keywords", [])
        predictions = result.metrics.get("predictions", [])
        negative_review_ids = {
            uuid.UUID(p["review_id"]) for p in predictions if p["label"] == "negative"
        }

        reviews = uow.reviews.get_by_job_id(job_id)
        negative_texts = [r.text for r in reviews if r.id in negative_review_ids]

    insights = generator.generate(negative_keywords, negative_texts)

    return ActionableInsightsDTO(
        job_id=job_id,
        method=method.value,
        negative_keywords=negative_keywords,
        insights=insights,
        generated_by=generator.generator_type,
    )
