import json

import pandas as pd
from redis.asyncio import Redis

from app.core.config.settings import settings
from app.core.logger import get_logger

__all__ = ["CacheService"]

logger = get_logger(__name__)


class CacheService:
    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client

    async def get_pool(self, app_id: str, country: str) -> pd.DataFrame | None:
        key = self._pool_key(app_id, country)
        raw = await self._redis.get(key)
        if raw is None:
            return None

        records = json.loads(raw)
        logger.info(f"Cache hit for {key}: {len(records)} reviews")
        return pd.DataFrame.from_records(records)

    async def set_pool(self, app_id: str, country: str, df: pd.DataFrame) -> None:
        key = self._pool_key(app_id, country)
        payload = json.dumps(df.to_dict("records"))
        await self._redis.set(key, payload, ex=settings.redis.TTL_SECONDS)
        logger.info(
            f"Cached {len(df)} reviews under {key} (TTL={settings.redis.TTL_SECONDS}s)"
        )

    def _pool_key(self, app_id: str, country: str) -> str:
        return f"reviews_pool:{app_id}:{country}"
