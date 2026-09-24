from redis.asyncio import Redis

from app.core.config.settings import settings

__all__ = ["redis_client"]

redis_client = Redis.from_url(settings.redis.URL, decode_responses=True)
