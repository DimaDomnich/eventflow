from sqlalchemy import Boolean, String

from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column


class UserStatusModel(db.Model):
    __tablename__ = "dict_user_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(80))
    is_terminal: Mapped[bool] = mapped_column(Boolean(), default=False)


class EventStatusModel(db.Model):
    __tablename__ = "dict_event_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(80))
    is_terminal: Mapped[bool] = mapped_column(Boolean(), default=False)


class OrderStatusModel(db.Model):
    __tablename__ = "dict_order_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(80))
    is_terminal: Mapped[bool] = mapped_column(Boolean(), default=False)


class TicketStatusModel(db.Model):
    __tablename__ = "dict_ticket_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(80))
    is_terminal: Mapped[bool] = mapped_column(Boolean(), default=False)


class RsvpStatusModel(db.Model):
    __tablename__ = "dict_rsvp_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(80))
    is_terminal: Mapped[bool] = mapped_column(Boolean(), default=False)
