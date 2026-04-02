from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID
import uuid


class IDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
