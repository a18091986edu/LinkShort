import datetime

from database.mixins.id_mixins import IDMixin
from database.mixins.timestamp_mixins import TimestampsMixin
from database.models import Base
from sqlalchemy import UUID, Boolean, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Task(IDMixin, TimestampsMixin, Base):
    task: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    is_private: Mapped[bool | None] = mapped_column(Boolean, default=False)
    is_done: Mapped[bool | None] = mapped_column(Boolean, default=False)
    deadline: Mapped[datetime.date] = mapped_column(
        Date, default=lambda: datetime.date(2100, 1, 1)
    )
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    owner = relationship("User", back_populates="tasks")
