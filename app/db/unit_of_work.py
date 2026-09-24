from types import TracebackType

from sqlalchemy.orm import Session, sessionmaker

from app.repositories.job import JobRepository
from app.repositories.result import ResultRepository
from app.repositories.review import ReviewRepository

__all__ = ["UnitOfWork"]


class UnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self.session: Session
        self.jobs: JobRepository
        self.reviews: ReviewRepository
        self.results: ResultRepository

    def __enter__(self) -> "UnitOfWork":
        self.session = self._session_factory()
        self.jobs = JobRepository(self.session)
        self.reviews = ReviewRepository(self.session)
        self.results = ResultRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
