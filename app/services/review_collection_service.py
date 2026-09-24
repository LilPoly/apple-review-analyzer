from app.core.exceptions import InvalidAppUrlError
from app.models.job import AnalysisJob
from app.models.review import Review
from app.db.unit_of_work import UnitOfWork
from app.schemas.review import CollectReviewsRequest, CollectReviewsResponse
from app.services.scraper.base import ScraperService
from app.utils.stats import calculate_average_rating, calculate_rating_distribution
from app.utils.text_preprocessing import clean_text, is_meaningful_text
from app.utils.url_parser import parse_app_store_url
from app.core.logger import get_logger

logger = get_logger(__name__)

__all__ = ["ReviewCollectionService"]


class ReviewCollectionService:
    def __init__(self, uow: UnitOfWork, scraper: ScraperService) -> None:
        self._uow = uow
        self._scraper = scraper

    async def collect(self, request: CollectReviewsRequest) -> CollectReviewsResponse:
        app_id, country = self._resolve_app_reference(request)
        logger.info(f"Resolved app reference: app_id={app_id}, country={country}")

        raw_reviews = await self._scraper.fetch_reviews(
            app_id=app_id, country=country, count=request.count
        )

        job = AnalysisJob(app_id=app_id, country=country)
        reviews = [
            Review(
                job_id=job.id,
                external_review_id=raw.external_id,
                title=raw.title,
                text=clean_text(raw.text),
                rating=raw.rating,
                author=raw.author,
            )
            for raw in raw_reviews
            if is_meaningful_text(raw.text)
        ]

        with self._uow as uow:
            uow.jobs.add(job)
            uow.session.flush()  # generates job.id before attaching reviews

            for review in reviews:
                review.job_id = job.id
            uow.reviews.add_many(reviews)

            uow.commit()

        ratings = [review.rating for review in reviews]
        logger.info(f"Job {job.id} saved with {len(reviews)} reviews")
        return CollectReviewsResponse(
            job_id=job.id,
            app_id=app_id,
            country=country,
            reviews_count=len(reviews),
            average_rating=calculate_average_rating(ratings),
            rating_distribution=calculate_rating_distribution(ratings),
        )

    def _resolve_app_reference(self, request: CollectReviewsRequest) -> tuple[str, str]:
        if request.app_store_url:
            try:
                return parse_app_store_url(request.app_store_url)
            except InvalidAppUrlError:
                raise
        return request.app_id, request.country  # type: ignore[return-value]
