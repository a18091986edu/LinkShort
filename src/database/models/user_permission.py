# database/models/user_permission.py
import uuid
from sqlalchemy import UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.mixins.id_mixins import IDMixin
from database.mixins.timestamp_mixins import CreatedAtMixin
from database.models.base import Base


class UserPermission(IDMixin, CreatedAtMixin, Base):
    """
    Модель для предоставления доступа к своим публичным задачам
    """

    __tablename__ = "user_permission"
    __table_args__ = (
        UniqueConstraint("owner_id", "granted_to_id", name="uq_owner_granted_to"),
    )

    # Владелец задач (кто дает доступ)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    # Кому дается доступ (кто сможет видеть публичные задачи владельца)
    granted_to_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    # Отношения
    owner = relationship(
        "User", foreign_keys=[owner_id], back_populates="granted_permissions"
    )
    granted_to = relationship(
        "User", foreign_keys=[granted_to_id], back_populates="received_permissions"
    )
