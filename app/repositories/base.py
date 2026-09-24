import uuid
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

__all__ = ["AbstractRepository"]

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    def __init__(self, session: Session) -> None:
        self._session = session

    @abstractmethod
    def get(self, id: uuid.UUID) -> T | None: ...

    @abstractmethod
    def add(self, entity: T) -> T: ...

    @abstractmethod
    def delete(self, entity: T) -> None: ...
