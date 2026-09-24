import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = [
    "CollectReviewsRequest",
    "CollectReviewsResponse",
    "ReviewDTO",
]


class CollectReviewsRequest(BaseModel):
    app_store_url: str | None = Field(default=None)
    app_id: str | None = Field(default=None)
    country: str = Field(default="us", min_length=2, max_length=2)
    count: int = Field(default=100, ge=10, le=500)

    @model_validator(mode="after")
    def check_app_reference_provided(self) -> "CollectReviewsRequest":
        if not self.app_store_url and not self.app_id:
            raise ValueError("Either 'app_store_url' or 'app_id' must be provided")
        return self


class ReviewDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str | None
    text: str
    rating: int = Field(ge=1, le=5)
    author: str | None
    created_at: datetime


class CollectReviewsResponse(BaseModel):
    job_id: uuid.UUID
    app_id: str
    country: str
    reviews_count: int
    average_rating: float
    rating_distribution: dict[int, float]
