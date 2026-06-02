from sqlalchemy import Integer, String

from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column


class EventCategoryModel(db.Model):
    __tablename__ = "event_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
