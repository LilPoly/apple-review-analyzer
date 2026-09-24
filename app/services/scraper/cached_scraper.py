import pandas as pd

from app.core.logger import get_logger
from app.schemas.scraper import RawReviewDTO
from app.services.cache_service import CacheService
from app.services.scraper.base import ReviewPoolFetcher, ScraperService

__all__ = ["CachedScraper"]

logger = get_logger(__name__)


class CachedScraper(ScraperService):
    def __init__(self, fetcher: ReviewPoolFetcher, cache: CacheService) -> None:
        self._fetcher = fetcher
        self._cache = cache

    async def fetch_reviews(
        self, app_id: str, country: str, count: int
    ) -> list[RawReviewDTO]:
        df = await self._get_or_fetch_pool(app_id, country, count)
        sample_size = min(count, len(df))
        sampled_df = df.sample(n=sample_size).reset_index(drop=True)

        return [
            RawReviewDTO(
                external_id=row["external_id"],
                title=row["title"],
                text=row["text"],
                rating=row["rating"],
                author=row["author"],
            )
            for row in sampled_df.to_dict("records")
        ]

    async def _get_or_fetch_pool(
        self, app_id: str, country: str, count: int
    ) -> pd.DataFrame:
        cached_df = await self._cache.get_pool(app_id, country)
        if cached_df is not None and len(cached_df) >= count:
            return cached_df

        logger.info(
            f"Cache miss for app_id={app_id}, country={country} — fetching fresh pool"
        )
        fresh_df = await self._fetcher.fetch_pool(app_id, country, min_size=count)
        await self._cache.set_pool(app_id, country, fresh_df)
        return fresh_df
