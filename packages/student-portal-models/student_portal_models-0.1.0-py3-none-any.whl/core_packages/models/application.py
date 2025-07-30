from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from db import Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .user import User

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    student_id_number: Mapped[str | None] = mapped_column(String, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String, nullable=True)
    group: Mapped[str | None] = mapped_column(String, nullable=True)
    faculty: Mapped[str | None] = mapped_column(String, nullable=True)
    gpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    application_file: Mapped[str | None] = mapped_column(String, nullable=True)
    response_file: Mapped[str | None] = mapped_column(String, nullable=True)
    create_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(microsecond=0))

    user: Mapped["User"] = relationship(back_populates="application")