import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Label(str, enum.Enum):
    LIKELY_AUTHENTIC = "LIKELY_AUTHENTIC"
    SUSPICIOUS = "SUSPICIOUS"
    LIKELY_FAKE = "LIKELY_FAKE"


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    result_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[Optional[int]] = mapped_column(ForeignKey("submissions.submission_id"), unique=True, nullable=True)
    suspicious_score: Mapped[float] = mapped_column(Float)
    label: Mapped[Label] = mapped_column(Enum(Label))
    confidence: Mapped[float] = mapped_column(Float)
    summary: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submission: Mapped[Optional["Submission"]] = relationship(back_populates="result")  # noqa: F821
    module_results: Mapped[list["ModuleResult"]] = relationship(
        back_populates="result", cascade="all, delete-orphan")
    report: Mapped[Optional["Report"]] = relationship(  # noqa: F821
        back_populates="result", uselist=False, cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "result_id": self.result_id,
            "submission_id": self.submission_id,
            "suspicious_score": self.suspicious_score,
            "label": self.label.value,
            "confidence": self.confidence,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modules": [m.to_dict() for m in self.module_results],
        }


class ModuleResult(Base):
    """What every detection module returns (also stored in the DB)."""
    __tablename__ = "module_results"

    module_result_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    result_id: Mapped[Optional[int]] = mapped_column(ForeignKey("analysis_results.result_id"), nullable=True)
    module_name: Mapped[str] = mapped_column(String(50))
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)   # 0..1, None = not applicable
    weight: Mapped[float] = mapped_column(Float, default=0.0)             # set by ScoreFusion
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    artifact_paths: Mapped[list] = mapped_column(JSON, default=list)

    result: Mapped[Optional["AnalysisResult"]] = relationship(back_populates="module_results")

    def is_applicable(self) -> bool:
        return self.score is not None

    def to_dict(self) -> dict:
        return {
            "module_name": self.module_name,
            "score": self.score,
            "weight": self.weight,
            "evidence": self.evidence or {},
            "artifact_paths": self.artifact_paths or [],
        }
