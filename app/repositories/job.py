import uuid

from sqlalchemy import select

from app.models.job import AnalysisJob
from app.repositories.base import AbstractRepository

__all__ = ["JobRepository"]


class JobRepository(AbstractRepository[AnalysisJob]):
    def get(self, id: uuid.UUID) -> AnalysisJob | None:
        return self._session.get(AnalysisJob, id)

    def get_by_app_id(self, app_id: str, country: str) -> AnalysisJob | None:
        stmt = select(AnalysisJob).where(
            AnalysisJob.app_id == app_id, AnalysisJob.country == country
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def add(self, entity: AnalysisJob) -> AnalysisJob:
        self._session.add(entity)
        return entity

    def delete(self, entity: AnalysisJob) -> None:
        self._session.delete(entity)
