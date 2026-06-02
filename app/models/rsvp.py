from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, func

from app.extensions import db

from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.event import EventModel
    from app.models.status import RsvpStatusModel
    from app.models.user import UserModel


class RsvpModel(db.Model):
    __tablename__ = "rsvps"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserModel"] = relationship(back_populates="rsvps")

    status_id: Mapped[int] = mapped_column(ForeignKey("dict_rsvp_statuses.id"))
    status: Mapped["RsvpStatusModel"] = relationship()

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    event: Mapped["EventModel"] = relationship()
