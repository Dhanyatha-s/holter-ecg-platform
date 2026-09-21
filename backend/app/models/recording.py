import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Recording(Base):
    __tablename__ = "recordings"

    __table_args__ = (
        CheckConstraint(
            "lead_count BETWEEN 1 AND 12",
            name="ck_recordings_lead_count",
        ),
        CheckConstraint(
            "sample_rate > 0",
            name="ck_recordings_sample_rate_positive",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    holter_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("holter_sessions.id", ondelete="RESTRICT"),
        nullable=False,
    )

    acquisition_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("acquisition_sessions.id", ondelete="RESTRICT"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="RECEIVING",
    )

    format: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    lead_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    sample_rate: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    recording_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    recording_ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    size_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    checksum: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    storage_bucket: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    storage_object_key: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )