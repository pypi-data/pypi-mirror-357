from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from db import Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .user import User

class UserSubject(Base):
    __tablename__ = "user_subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    subject_name: Mapped[str] = mapped_column(String, nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    semester_code: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="subjects")