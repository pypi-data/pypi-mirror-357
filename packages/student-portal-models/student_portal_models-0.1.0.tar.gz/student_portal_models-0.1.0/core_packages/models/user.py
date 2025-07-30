from sqlalchemy.orm import  Mapped, mapped_column , relationship
from sqlalchemy import String, Date
from db import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .application import Application
    from .user_subject import UserSubject
    from .user_gpa import UserGpa


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    third_name: Mapped[str | None] = mapped_column(String, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    student_id_number: Mapped[str | None] = mapped_column(String, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String, nullable=True)
    birth_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    passport_pin: Mapped[str | None] = mapped_column(String, nullable=True)
    passport_number: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    password: Mapped[str | None] = mapped_column(String, nullable=True)
    gender: Mapped[str | None] = mapped_column(String, nullable=True)
    university: Mapped[str | None] = mapped_column(String, nullable=True)
    specialty: Mapped[str | None] = mapped_column(String, nullable=True)
    student_status: Mapped[str | None] = mapped_column(String, nullable=True)
    education_form: Mapped[str | None] = mapped_column(String, nullable=True)
    education_type: Mapped[str | None] = mapped_column(String, nullable=True)
    payment_form: Mapped[str | None] = mapped_column(String, nullable=True)
    group: Mapped[str | None] = mapped_column(String, nullable=True)
    education_lang: Mapped[str | None] = mapped_column(String, nullable=True)
    faculty: Mapped[str | None] = mapped_column(String, nullable=True)
    level: Mapped[str | None] = mapped_column(String, nullable=True)
    semester: Mapped[str | None] = mapped_column(String, nullable=True)
    address: Mapped[str | None] = mapped_column(String, nullable=True)

    gpa: Mapped["UserGpa"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    subject: Mapped[list["UserSubject"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    application: Mapped["Application"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
