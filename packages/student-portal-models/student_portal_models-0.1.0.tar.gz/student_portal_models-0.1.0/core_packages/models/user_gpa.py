from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, ForeignKey
from db import Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .user import User

class UserGpa(Base):
    __tablename__ = "user_gpas"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    gpa: Mapped[float] = mapped_column(Float, nullable=False)
    education_year: Mapped[str] = mapped_column(String, nullable=False)
    subjects: Mapped[int] = mapped_column(Integer, nullable=False)
    level: Mapped[str] = mapped_column(String, nullable=False)
    credit_sum: Mapped[str] = mapped_column(String, nullable=False)
    debt_subjects: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="gpa")