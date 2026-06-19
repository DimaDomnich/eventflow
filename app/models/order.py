from typing import TYPE_CHECKING
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func

from app.extensions import db

from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .user import UserModel
    from .status import OrderStatusModel
    from .ticket import TicketModel


class OrderModel(db.Model):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_intent_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=True
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserModel"] = relationship(back_populates="orders")

    status_id: Mapped[int] = mapped_column(
        ForeignKey("dict_order_statuses.id"), default=1
    )
    status: Mapped["OrderStatusModel"] = relationship()

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tickets: Mapped[list["TicketModel"]] = relationship(back_populates="order")
