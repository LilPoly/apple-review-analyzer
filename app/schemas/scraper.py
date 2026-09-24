from pydantic import BaseModel, Field

__all__ = ["RawReviewDTO"]


class RawReviewDTO(BaseModel):
    external_id: str | None = None
    title: str | None = None
    text: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)
    author: str | None = None
