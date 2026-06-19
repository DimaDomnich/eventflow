from typing import TYPE_CHECKING
from datetime import datetime
import enum

from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Integer, String, func


if TYPE_CHECKING:
    from app.models.status import UserStatusModel
    from app.models.event import EventModel
    from app.models.order import OrderModel


class RoleEnum(enum.Enum):
    attendee = "attendee"
    organizer = "organizer"
    admin = "admin"


class UserRoleModel(db.Model):
    __tablename__ = "dict_user_roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class UserModel(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    email: Mapped[str] = mapped_column(String(80), unique=True)
    password: Mapped[str] = mapped_column(String(150))
    full_name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    status_id: Mapped[int] = mapped_column(
        ForeignKey("dict_user_statuses.id"), default=1
    )
    status: Mapped["UserStatusModel"] = relationship()

    role_id: Mapped[int] = mapped_column(ForeignKey("dict_user_roles.id"), default=1)
    role: Mapped["UserRoleModel"] = relationship()

    events: Mapped[list["EventModel"]] = relationship(
        back_populates="organizer"  # , cascade="all, delete-orphan"
    )
    orders: Mapped[list["OrderModel"]] = relationship(back_populates="user")
