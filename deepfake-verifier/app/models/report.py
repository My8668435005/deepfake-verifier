from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Report(Base):
    __tablename__ = "reports"

    report_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    result_id: Mapped[int] = mapped_column(ForeignKey("analysis_results.result_id"), unique=True)
    file_path: Mapped[str] = mapped_column(String(500))
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    result: Mapped["AnalysisResult"] = relationship(back_populates="report")  # noqa: F821

    def download(self) -> bytes:
        return Path(self.file_path).read_bytes()
