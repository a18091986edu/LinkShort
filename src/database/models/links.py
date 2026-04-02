from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from database.mixins.id_mixins import IDMixin
from database.mixins.timestamp_mixins import CreatedAtMixin
from database.models import Base


class Link(IDMixin, CreatedAtMixin, Base):
    full_link: Mapped[str] = mapped_column(String)
    short_link: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
