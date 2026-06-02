from typing import TYPE_CHECKING
from sqlalchemy import Integer, String

from app.extensions import db

from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.event import EventModel


class TagModel(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)

    events: Mapped[list["EventModel"]] = relationship(
        secondary="event_tags", back_populates="tags"
    )
