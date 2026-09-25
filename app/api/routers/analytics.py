from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_baseline_metrics_service
from app.core.exceptions import BaselineMetricsReadError
from app.core.logger import get_logger
from app.schemas.baseline import BaselineMetricsResponse
from app.services.baseline_metrics_service import BaselineMetricsService
from app.services.visualization.chart_service import ChartService

__all__ = ["router"]

router = APIRouter(prefix="/analytics", tags=["Analytics"])
_chart_service = ChartService()

logger = get_logger(__name__)


@router.get("/baseline-metrics", response_model=BaselineMetricsResponse)
def get_baseline_metrics(
    service: Annotated[BaselineMetricsService, Depends(get_baseline_metrics_service)],
) -> BaselineMetricsResponse:
    try:
        return service.get_metrics()
    except BaselineMetricsReadError as exc:
        logger.error(str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc


@router.get("/charts/model-comparison", tags=["Analytics"])
def get_model_comparison_chart(
    service: Annotated[BaselineMetricsService, Depends(get_baseline_metrics_service)],
) -> StreamingResponse:
    try:
        metrics = service.get_metrics()
    except BaselineMetricsReadError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc

    macro_f1_by_method = {
        "VADER": metrics.vader.f1_macro,
        "Classical": metrics.classical.f1_macro,
        "BERT": metrics.bert.f1_macro,
    }
    buffer = _chart_service.model_comparison_chart(macro_f1_by_method)

    return StreamingResponse(buffer, media_type="image/png")
