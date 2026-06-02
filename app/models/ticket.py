from typing import TYPE_CHECKING
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, func

from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.event import EventModel
    from app.models.order import OrderModel
    from app.models.status import TicketStatusModel
    from app.models.user import UserModel


class TicketTypeModel(db.Model):
    __tablename__ = "ticket_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    quantity: Mapped[int] = mapped_column()
    sold_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
    )
    event: Mapped["EventModel"] = relationship(back_populates="ticket_types")


class TicketModel(db.Model):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    qr_code: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    order: Mapped["OrderModel"] = relationship(back_populates="tickets")

    ticket_type_id: Mapped[int] = mapped_column(ForeignKey("ticket_types.id"))
    ticket_type: Mapped["TicketTypeModel"] = relationship()

    status_id: Mapped[int] = mapped_column(ForeignKey("dict_ticket_statuses.id"))
    status: Mapped["TicketStatusModel"] = relationship()


class TicketStatusHistoryModel(db.Model):
    __tablename__ = "tickets_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    ticket: Mapped["TicketModel"] = relationship()

    status_id: Mapped[int] = mapped_column(ForeignKey("dict_ticket_statuses.id"))
    status: Mapped["TicketStatusModel"] = relationship()

    changed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserModel"] = relationship()

    changed_at: Mapped[datetime] = mapped_column(server_default=func.now())


class TicketCheckIns(db.Model):
    __tablename__ = "ticket_check_ins"

    id: Mapped[int] = mapped_column(primary_key=True)

    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), unique=True)
    ticket: Mapped["TicketModel"] = relationship()

    checked_in_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    checked_in_by: Mapped["UserModel"] = relationship()

    checked_in_at: Mapped[datetime] = mapped_column(server_default=func.now())
