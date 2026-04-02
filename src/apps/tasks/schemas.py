import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr
from uuid import UUID


class BaseTask(BaseModel):
    """
    Базовая схема задачи.
    """

    task: str
    description: str | None = None


class CreateTaskSchema(BaseTask):
    """
    Схема для создания новой задачи.
    """

    is_private: bool = False
    deadline: date = date(2100, 1, 1)


class UpdateTaskSchema(BaseModel):
    """
    Схема для обновления задачи.
    """

    task: str | None = None
    description: str | None = None
    is_private: bool | None = None
    is_done: bool | None = None
    deadline: date = date(2100, 1, 1)


class DeleteTaskSchema(BaseModel):
    """
    Схема для удаления задачи по ID.
    """

    id: uuid.UUID


class TaskSchema(BaseTask):
    """
    Полная схема задачи с метаданными.
    """

    id: uuid.UUID
    is_private: bool
    is_done: bool
    deadline: date = date(2100, 1, 1)
    created_at: datetime
    updated_at: datetime
    owner_id: uuid.UUID


class GetTaskSchema(BaseTask):
    """
    Схема для получения задачи.
    """

    id: uuid.UUID
    is_done: bool
    deadline: date = date(2100, 1, 1)


class GrantAccessSchema(BaseModel):
    """Схема для предоставления доступа к своим публичным задачам"""

    user_email: EmailStr  # Кому даем доступ


class RevokeAccessSchema(BaseModel):
    """Схема для отзыва доступа"""

    user_email: EmailStr  # У кого отзываем доступ


class PermissionInfoSchema(BaseModel):
    """Информация о выданном разрешении"""

    permission_id: UUID
    user_id: UUID
    user_email: str
    granted_at: datetime


class TaskWithOwnerSchema(TaskSchema):
    """Схема задачи с информацией о владельце"""

    owner_email: str
