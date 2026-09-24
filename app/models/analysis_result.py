import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.job import AnalysisJob

if TYPE_CHECKING:
    from app.models.job import AnalysisJob

__all__ = ["AnalysisResult"]


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    method: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "classical" | "bert"
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    execution_time_seconds: Mapped[float] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    job: Mapped["AnalysisJob"] = relationship(back_populates="results")
