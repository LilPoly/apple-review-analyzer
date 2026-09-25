from pydantic import field_validator
from app.core.config.base import BaseConfig

__all__ = ["DataBaseConfig"]


class DataBaseConfig(BaseConfig):
    URL: str = "postgresql+psycopg://user:password@localhost:5432/reviews_db"

    @field_validator("URL", mode="before")
    @classmethod
    def ensure_sqlalchemy_driver(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v

    model_config = BaseConfig.model_config | {"env_prefix": "DB_"}
