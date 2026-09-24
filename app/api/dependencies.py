from app.db.redis import redis_client
from app.db.session import SessionLocal
from app.db.unit_of_work import UnitOfWork
from app.services.cache_service import CacheService
from app.services.scraper.apple_rss_scraper import AppleRSSScraper
from app.services.scraper.base import ScraperService
from app.services.scraper.cached_scraper import CachedScraper

__all__ = ["get_uow"]


def get_uow() -> UnitOfWork:
    return UnitOfWork(SessionLocal)


def get_scraper() -> ScraperService:
    fetcher = AppleRSSScraper()
    cache = CacheService(redis_client)
    return CachedScraper(fetcher=fetcher, cache=cache)
