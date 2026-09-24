from app.core.config.base import BaseConfig

__all__ = ["ScraperConfig"]


class ScraperConfig(BaseConfig):
    BASE_URL: str = "https://itunes.apple.com"
    DEFAULT_REVIEW_COUNT: int = 100
    MAX_REVIEW_COUNT: int = 500

    model_config = BaseConfig.model_config | {"env_prefix": "SCRAPER_"}
