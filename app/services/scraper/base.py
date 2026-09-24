from abc import ABC, abstractmethod

import pandas as pd

from app.schemas.scraper import RawReviewDTO

__all__ = ["ScraperService"]


class ScraperService(ABC):
    @abstractmethod
    async def fetch_reviews(
        self, app_id: str, country: str, count: int
    ) -> list[RawReviewDTO]:
        """Fetch up to `count` reviews for the given app."""
        ...


class ReviewPoolFetcher(ABC):
    @abstractmethod
    async def fetch_pool(
        self, app_id: str, country: str, min_size: int
    ) -> pd.DataFrame:
        """Fetch, deduplicate and clean a pool of reviews, without sampling."""
        ...
