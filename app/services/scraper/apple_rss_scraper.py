import asyncio

import httpx
import pandas as pd

from app.core.config.settings import settings
from app.core.exceptions import AppNotFoundError, ScraperError
from app.core.logger import get_logger
from app.schemas.scraper import RawReviewDTO
from app.services.scraper.base import ReviewPoolFetcher, ScraperService
from app.utils.text_preprocessing import clean_text, is_meaningful_text

__all__ = ["AppleRSSScraper"]

logger = get_logger(__name__)

_SORT_MODES = ("mostrecent", "mosthelpful")
_REVIEWS_PER_PAGE = 50
_MAX_PAGES_PER_SORT = 5


class AppleRSSScraper(ScraperService, ReviewPoolFetcher):
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(
            timeout=10.0,
            headers={"User-Agent": "Mozilla/5.0 (compatible; AppleReviewAnalyzer/1.0)"},
        )

    async def fetch_pool(
        self, app_id: str, country: str, min_size: int
    ) -> pd.DataFrame:
        logger.info(
            f"Fetching fresh pool: app_id={app_id}, country={country}, min_size={min_size}"
        )

        await self._ensure_app_exists(app_id, country)

        raw_entries = await self._collect_from_all_sorts(app_id, country, min_size)
        if not raw_entries:
            raise ScraperError(f"No reviews found for app_id='{app_id}'")

        df = self._to_dataframe(raw_entries)
        logger.info(f"Fetched {len(df)} raw entries before processing")

        df = self._deduplicate(df)
        df = self._clean(df)
        logger.info(f"{len(df)} reviews remain after dedup and cleaning")

        return df

    async def fetch_reviews(
        self, app_id: str, country: str, count: int
    ) -> list[RawReviewDTO]:
        df = await self.fetch_pool(app_id, country, min_size=count)
        sampled_df = self._sample(df, count)
        return [self._row_to_dto(row) for row in sampled_df.to_dict("records")]

    async def _ensure_app_exists(self, app_id: str, country: str) -> None:
        url = f"{settings.scraper.BASE_URL}/lookup"
        try:
            response = await self._client.get(
                url, params={"id": app_id, "country": country}
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ScraperError(f"Failed to verify app_id='{app_id}': {exc}") from exc

        data = response.json()
        if data.get("resultCount", 0) == 0:
            raise AppNotFoundError(app_id)

    async def _collect_from_all_sorts(
        self, app_id: str, country: str, count: int
    ) -> list[dict]:
        pages_needed = min(_MAX_PAGES_PER_SORT, (count // _REVIEWS_PER_PAGE) + 2)
        tasks = [
            self._fetch_page(app_id, country, sort_mode, page)
            for sort_mode in _SORT_MODES
            for page in range(1, pages_needed + 1)
        ]
        pages_results = await self._gather_safely(tasks)
        return [entry for page in pages_results for entry in page]

    async def _gather_safely(self, tasks: list) -> list[list[dict]]:
        results = []
        for task in tasks:
            try:
                results.append(await task)
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    f"Page fetch failed with status {exc.response.status_code}: {exc.request.url}"
                )
            except httpx.HTTPError as exc:
                logger.warning(f"Page fetch failed: {exc}")
        return results

    async def _fetch_page(
        self, app_id: str, country: str, sort_mode: str, page: int, retries: int = 2
    ) -> list[dict]:
        url = (
            f"{settings.scraper.BASE_URL}/{country}/rss/customerreviews/"
            f"page={page}/id={app_id}/sortby={sort_mode}/json"
        )
        for attempt in range(retries + 1):
            response = await self._client.get(url)
            if response.status_code == 429 and attempt < retries:
                wait = 2**attempt
                logger.warning(f"Rate limited, retrying in {wait}s...")
                await asyncio.sleep(wait)
                continue
            response.raise_for_status()
            data = response.json()
            return data.get("feed", {}).get("entry", [])
        return []

    def _to_dataframe(self, raw_entries: list[dict]) -> pd.DataFrame:
        records = [
            {
                "external_id": entry.get("id", {}).get("label"),
                "title": entry.get("title", {}).get("label"),
                "text": entry.get("content", {}).get("label", ""),
                "rating": int(entry.get("im:rating", {}).get("label", 0)),
                "author": entry.get("author", {}).get("name", {}).get("label"),
            }
            for entry in raw_entries
        ]
        return pd.DataFrame.from_records(records)

    def _deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.drop_duplicates(subset="external_id", keep="first").reset_index(
            drop=True
        )

    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["text"] = df["text"].apply(clean_text)
        df = df[df["text"].apply(is_meaningful_text)]
        return df.reset_index(drop=True)

    def _sample(self, df: pd.DataFrame, count: int) -> pd.DataFrame:
        sample_size = min(count, len(df))
        return df.sample(n=sample_size).reset_index(drop=True)

    def _row_to_dto(self, row: dict) -> RawReviewDTO:
        return RawReviewDTO(
            external_id=row["external_id"],
            title=row["title"],
            text=row["text"],
            rating=row["rating"],
            author=row["author"],
        )
