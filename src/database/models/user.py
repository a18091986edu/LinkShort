from database.mixins.id_mixins import IDMixin
from database.mixins.timestamp_mixins import TimestampsMixin
from database.models.base import Base
from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(IDMixin, TimestampsMixin, Base):
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, unique=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    tasks: Mapped[list["Task"]] = relationship(  # noqa
        "Task", back_populates="owner", lazy="selectin"
    )

    granted_permissions: Mapped[list["UserPermission"]] = relationship(  # noqa
        "UserPermission",
        foreign_keys="UserPermission.owner_id",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Кто дал мне доступ к своим задачам
    received_permissions: Mapped[list["UserPermission"]] = relationship(  # noqa
        "UserPermission",
        foreign_keys="UserPermission.granted_to_id",
        back_populates="granted_to",
        lazy="selectin",
    )
