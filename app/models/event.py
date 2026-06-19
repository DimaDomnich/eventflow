from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, String, func

from app.extensions import db
from sqlalchemy import Computed
from sqlalchemy.dialects.postgresql import TSVECTOR

from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from app.models.category import EventCategoryModel
    from app.models.status import EventStatusModel
    from app.models.tag import TagModel
    from app.models.ticket import TicketTypeModel
    from app.models.user import UserModel


class EventModel(db.Model):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(300))
    location: Mapped[str] = mapped_column(String(100))
    starts_at: Mapped[datetime] = mapped_column()
    ends_at: Mapped[datetime] = mapped_column()
    capacity: Mapped[int] = mapped_column()
    banner_url: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    organizer: Mapped["UserModel"] = relationship(back_populates="events")

    category_id: Mapped[int] = mapped_column(ForeignKey("event_categories.id"))
    category: Mapped["EventCategoryModel"] = relationship()

    status_id: Mapped[int] = mapped_column(
        ForeignKey("dict_event_statuses.id"), default=1
    )
    status: Mapped["EventStatusModel"] = relationship()

    tags: Mapped[list["TagModel"]] = relationship(
        secondary="event_tags", back_populates="events"
    )

    ticket_types: Mapped[list["TicketTypeModel"]] = relationship(back_populates="event")

    search_vector: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed(
            "setweight(to_tsvector('english', coalesce(title, '')), 'A') || "
            "setweight(to_tsvector('english', coalesce(description, '')), 'B') || "
            "setweight(to_tsvector('english', coalesce(location, '')), 'C')",
            persisted=True,
        ),
        nullable=True,
    )


class EventStatusHistoryModel(db.Model):
    __tablename__ = "events_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    changed_at: Mapped[datetime] = mapped_column(server_default=func.now())

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    event: Mapped["EventModel"] = relationship()

    status_id: Mapped[int] = mapped_column(ForeignKey("dict_event_statuses.id"))
    status: Mapped["EventStatusModel"] = relationship()

    changed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    changed_by: Mapped["UserModel"] = relationship()


# m:m join table for events and tags
class EventTagModel(db.Model):
    __tablename__ = "event_tags"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)


class EventsRatingModel(db.Model):
    __tablename__ = "events_rating"

    id: Mapped[int] = mapped_column(primary_key=True)

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    event: Mapped["EventModel"] = relationship()

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserModel"] = relationship()

    score: Mapped[int] = mapped_column()
    comment: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
