import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_uow
from app.db.unit_of_work import UnitOfWork
from app.schemas.analysis import AnalysisMethod
from app.services.visualization.chart_service import ChartService
from app.utils.stats import calculate_rating_distribution

__all__ = ["router"]

router = APIRouter(prefix="/jobs", tags=["Visualizations"])
_chart_service = ChartService()


@router.get("/{job_id}/charts/rating-distribution")
def get_rating_distribution_chart(
    job_id: uuid.UUID,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> StreamingResponse:
    with uow:
        reviews = uow.reviews.get_by_job_id(job_id)
        if not reviews:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No reviews found for job_id='{job_id}'",
            )
        ratings = [r.rating for r in reviews]

    distribution = calculate_rating_distribution(ratings)
    buffer = _chart_service.rating_distribution_chart(distribution)

    return StreamingResponse(buffer, media_type="image/png")


@router.get("/{job_id}/charts/sentiment-distribution")
def get_sentiment_distribution_chart(
    job_id: uuid.UUID,
    method: AnalysisMethod,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> StreamingResponse:
    with uow:
        result = uow.results.get_by_job_and_method(job_id, method.value)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No analysis result for job_id='{job_id}', method='{method.value}'",
            )
        distribution = result.metrics.get("sentiment_distribution", {})

    buffer = _chart_service.sentiment_distribution_chart(distribution, method.value)
    return StreamingResponse(buffer, media_type="image/png")
