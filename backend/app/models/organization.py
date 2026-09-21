import uuid
from datetime import datetime


from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID # this line is important for using UUIDs in PostgreSQL
from sqlalchemy.orm import Mapped, mapped_column # these packages are used for defining ORM models in SQLAlchemy which will handle the mapping between Python classes and database tables

from app.db.base import Base

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key = True,
        default  = uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default = "ACTIVE", # DEFINES THE STATUS ON THE SESSION/USER INTERFACE

    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        nullable = False,
        server_default = func.now(), # this line sets the default value of the created_at column to the current timestamp when a new record is inserted into the database
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone =True),
        nullable =False,
        server_default =func.now(),
        onupdate =func.now(), # this line sets the updated_at column to automatically update to the current timestamp whenever the record is updated
    )
