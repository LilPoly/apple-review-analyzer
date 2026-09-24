import uuid

from sqlalchemy import select

from app.models.analysis_result import AnalysisResult
from app.repositories.base import AbstractRepository

__all__ = ["ResultRepository"]


class ResultRepository(AbstractRepository[AnalysisResult]):
    def get(self, id: uuid.UUID) -> AnalysisResult | None:
        return self._session.get(AnalysisResult, id)

    def get_by_job_and_method(
        self, job_id: uuid.UUID, method: str
    ) -> AnalysisResult | None:
        stmt = select(AnalysisResult).where(
            AnalysisResult.job_id == job_id, AnalysisResult.method == method
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def add(self, entity: AnalysisResult) -> AnalysisResult:
        self._session.add(entity)
        return entity

    def delete(self, entity: AnalysisResult) -> None:
        self._session.delete(entity)
