import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint(
            "identity_issuer",
            "identity_subject",
            name = "uq_users_identity",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key = True,
        default  = uuid.uuid4,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("organizations.id", ondelete = "RESTRICT"),
        nullable = False,

    )

    identity_issuer: Mapped[str] = mapped_column(
        String(512),
        nullable = False,

    )

    identity_subject: Mapped[str] = mapped_column(
        String(255),
        nullable = False,
    )
    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable = False,

    )
    email: Mapped[str | None] = mapped_column(
    String(320),
    nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable = False,
        default = "ACTIVE",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        nullable = False,
        server_default = func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        nullable = False,
        server_default = func.now(),
        onupdate = func.now(),
    )