from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, func

from app.extensions import db

from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.event import EventModel
    from app.models.user import UserModel


class WaitlistModel(db.Model):
    __tablename__ = "waitlist"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserModel"] = relationship()

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    event: Mapped["EventModel"] = relationship()

    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())

    notified_at: Mapped[datetime] = mapped_column(nullable=True)
    expired_at: Mapped[datetime] = mapped_column(nullable=True)
