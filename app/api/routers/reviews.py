import io
import uuid
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_scraper, get_uow
from app.core.exceptions import AppNotFoundError, InvalidAppUrlError, ScraperError
from app.core.logger import get_logger
from app.db.unit_of_work import UnitOfWork
from app.schemas.review import CollectReviewsRequest, CollectReviewsResponse
from app.services.review_collection_service import ReviewCollectionService
from app.services.scraper.base import ScraperService

__all__ = ["router"]

router = APIRouter(prefix="/reviews", tags=["Reviews"])
logger = get_logger(__name__)


@router.post("/collect", response_model=CollectReviewsResponse)
async def collect_reviews(
    request: CollectReviewsRequest,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    scraper: Annotated[ScraperService, Depends(get_scraper)],
) -> CollectReviewsResponse:
    service = ReviewCollectionService(uow=uow, scraper=scraper)

    try:
        return await service.collect(request)
    except InvalidAppUrlError as exc:
        logger.warning(f"Invalid URL provided: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except AppNotFoundError as exc:
        logger.warning(f"App not found: {exc}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except ScraperError as exc:
        logger.error(f"Scraper failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)
        ) from exc


@router.get("/raw-data/{job_id}")
def download_raw_data(
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

        df = pd.DataFrame(
            [
                {
                    "id": str(review.id),
                    "title": review.title,
                    "text": review.text,
                    "rating": review.rating,
                    "author": review.author,
                    "created_at": review.created_at.isoformat(),
                }
                for review in reviews
            ]
        )

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=reviews_{job_id}.csv"},
    )
