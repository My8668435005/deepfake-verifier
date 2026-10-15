import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class FileType(str, enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Submission(Base):
    __tablename__ = "submissions"

    submission_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # cleared after analysis
    file_type: Mapped[FileType] = mapped_column(Enum(FileType))
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped[Optional["User"]] = relationship(back_populates="submissions")  # noqa: F821
    result: Mapped[Optional["AnalysisResult"]] = relationship(  # noqa: F821
        back_populates="submission", uselist=False, cascade="all, delete-orphan")

    def update_progress(self, percent: int) -> None:
        self.status = JobStatus.PROCESSING
        self.progress = max(0, min(100, int(percent)))

    def mark_completed(self) -> None:
        self.status = JobStatus.COMPLETED
        self.progress = 100
        self.completed_at = datetime.utcnow()

    def mark_failed(self, reason: str) -> None:
        self.status = JobStatus.FAILED
        self.error_message = reason[:500]
        self.completed_at = datetime.utcnow()
