from app.core.config.base import BaseConfig

__all__ = ["RedisConfig"]


class RedisConfig(BaseConfig):
    URL: str = "redis://localhost:6379/0"
    TTL_SECONDS: int = 172800

    model_config = BaseConfig.model_config | {"env_prefix": "REDIS_"}
