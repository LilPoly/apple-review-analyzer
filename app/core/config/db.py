from app.core.config.base import BaseConfig

__all__ = ["DataBaseConfig"]


class DataBaseConfig(BaseConfig):
    URL: str = "postgresql+psycopg://user:password@localhost:5432/reviews_db"

    model_config = BaseConfig.model_config | {"env_prefix": "DB_"}
