import uuid

from sqlalchemy import select

from app.models.review import Review
from app.repositories.base import AbstractRepository

__all__ = ["ReviewRepository"]


class ReviewRepository(AbstractRepository[Review]):
    def get(self, id: uuid.UUID) -> Review | None:
        return self._session.get(Review, id)

    def get_by_job_id(self, job_id: uuid.UUID) -> list[Review]:
        stmt = select(Review).where(Review.job_id == job_id)
        return list(self._session.execute(stmt).scalars().all())

    def add(self, entity: Review) -> Review:
        self._session.add(entity)
        return entity

    def add_many(self, entities: list[Review]) -> list[Review]:
        self._session.add_all(entities)
        return entities

    def delete(self, entity: Review) -> None:
        self._session.delete(entity)
