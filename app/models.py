"""SQLAlchemy models for the crawler domain."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from .database import Base


class Crawler(Base):
    """Model representing a crawler configuration."""

    __tablename__ = "crawlers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    target_url = Column(String(500), nullable=False)
    schedule = Column(String(100), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    last_run_at = Column(DateTime, nullable=True)
    last_run_status = Column(String(50), default="never", nullable=False)
    last_run_message = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def mark_run(self, status: str, message: str | None = None) -> None:
        """Update the crawler to reflect a simulated run."""
        self.last_run_at = datetime.utcnow()
        self.last_run_status = status
        self.last_run_message = message
        self.updated_at = datetime.utcnow()
