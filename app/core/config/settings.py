from app.core.config.base import BaseConfig
from app.core.config.bert import BertConfig
from app.core.config.db import DataBaseConfig
from app.core.config.redis import RedisConfig
from app.core.config.scraper import ScraperConfig
from app.core.config.classical import ClassicalConfig

__all__ = ["Settings", "settings"]


class Settings(BaseConfig):
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    RELOAD: bool = True

    db: DataBaseConfig = DataBaseConfig()
    redis: RedisConfig = RedisConfig()
    bert: BertConfig = BertConfig()
    scraper: ScraperConfig = ScraperConfig()
    classical: ClassicalConfig = ClassicalConfig()


settings = Settings()
