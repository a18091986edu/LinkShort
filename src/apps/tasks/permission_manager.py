# apps/tasks/permission_manager.py
import uuid

from core.core_dependency.db_dependency import DBDependency
from database.models.tasks import Task
from database.models.user_permission import UserPermission
from database.models.user import User
from fastapi import Depends, HTTPException
from sqlalchemy import and_, delete, select
from sqlalchemy.orm import selectinload


class PermissionManager:
    """Менеджер для управления доступом к публичным задачам"""

    def __init__(self, db: DBDependency = Depends(DBDependency)) -> None:
        self.db = db
        self.user_model = User
        self.permission_model = UserPermission
        self.task_model = Task

    async def grant_access(self, owner_id: uuid.UUID, target_email: str) -> dict:
        """
        Дает доступ другому пользователю к своим публичным задачам
        """
        async with self.db.db_session() as session:
            # Находим пользователя, которому даем доступ
            result = await session.execute(
                select(self.user_model).where(self.user_model.email == target_email)
            )
            target_user = result.scalar_one_or_none()

            if not target_user:
                raise HTTPException(
                    status_code=404, detail=f"User with email {target_email} not found"
                )

            if target_user.id == owner_id:
                raise HTTPException(
                    status_code=400, detail="Cannot grant access to yourself"
                )

            # Проверяем, не существует ли уже такое разрешение
            existing = await session.execute(
                select(self.permission_model).where(
                    and_(
                        self.permission_model.owner_id == owner_id,
                        self.permission_model.granted_to_id == target_user.id,
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=400, detail="Access already granted to this user"
                )

            # Создаем разрешение
            permission = self.permission_model(
                owner_id=owner_id, granted_to_id=target_user.id
            )
            session.add(permission)
            await session.commit()

            return {
                "message": f"Access granted to {target_email}",
                "user_email": target_email,
                "user_id": str(target_user.id),
            }

    async def revoke_access(self, owner_id: uuid.UUID, target_email: str) -> dict:
        """
        Отзывает доступ у пользователя
        """
        async with self.db.db_session() as session:
            # Находим пользователя
            result = await session.execute(
                select(self.user_model).where(self.user_model.email == target_email)
            )
            target_user = result.scalar_one_or_none()

            if not target_user:
                raise HTTPException(
                    status_code=404, detail=f"User with email {target_email} not found"
                )

            # Удаляем разрешение
            await session.execute(
                delete(self.permission_model).where(
                    and_(
                        self.permission_model.owner_id == owner_id,
                        self.permission_model.granted_to_id == target_user.id,
                    )
                )
            )
            await session.commit()

            return {"message": f"Access revoked from {target_email}"}

    async def get_granted_users(self, owner_id: uuid.UUID) -> list[dict]:
        """
        Возвращает список пользователей, которым дали доступ
        """
        async with self.db.db_session() as session:
            query = (
                select(self.permission_model)
                .where(self.permission_model.owner_id == owner_id)
                .options(selectinload(self.permission_model.granted_to))
            )
            result = await session.execute(query)
            permissions = result.scalars().all()

            return [
                {
                    "permission_id": str(p.id),
                    "user_id": str(p.granted_to.id),
                    "user_email": p.granted_to.email,
                    "granted_at": p.created_at,
                }
                for p in permissions
            ]

    async def get_users_who_granted_access(self, user_id: uuid.UUID) -> list[dict]:
        """
        Возвращает список пользователей, которые дали доступ текущему пользователю
        """
        async with self.db.db_session() as session:
            query = (
                select(self.permission_model)
                .where(self.permission_model.granted_to_id == user_id)
                .options(selectinload(self.permission_model.owner))
            )
            result = await session.execute(query)
            permissions = result.scalars().all()

            return [
                {
                    "user_id": str(p.owner.id),
                    "user_email": p.owner.email,
                    "granted_at": p.created_at,
                }
                for p in permissions
            ]

    async def get_accessible_public_tasks_by_email(
        self, user_id: uuid.UUID, owner_email: str
    ) -> list[Task]:
        """
        Возвращает публичные задачи конкретного пользователя,
        если он дал доступ текущему пользователю
        """
        async with self.db.db_session() as session:
            # Находим владельца по email
            owner_result = await session.execute(
                select(self.user_model).where(self.user_model.email == owner_email)
            )
            owner = owner_result.scalar_one_or_none()

            if not owner:
                raise HTTPException(
                    status_code=404, detail=f"User with email {owner_email} not found"
                )

            # Проверяем, дал ли владелец доступ текущему пользователю
            permission_result = await session.execute(
                select(self.permission_model).where(
                    and_(
                        self.permission_model.owner_id == owner.id,
                        self.permission_model.granted_to_id == user_id,
                    )
                )
            )
            permission = permission_result.scalar_one_or_none()

            if not permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"User {owner_email} has not granted you access to their public tasks",
                )

            # Получаем публичные задачи владельца
            tasks_query = (
                select(self.task_model)
                .where(
                    and_(
                        self.task_model.owner_id == owner.id,
                        self.task_model.is_private == False,  # noqa
                    )
                )
                .order_by(self.task_model.created_at.desc())
            )
            tasks_result = await session.execute(tasks_query)
            tasks = tasks_result.scalars().all()

            return tasks

    async def get_accessible_public_tasks_with_owner(
        self, user_id: uuid.UUID
    ) -> list[tuple[Task, str]]:
        """
        Возвращает публичные задачи с email владельца для всех, кто дал доступ
        """
        async with self.db.db_session() as session:
            # Находим всех, кто дал доступ текущему пользователю
            query = (
                select(self.permission_model)
                .where(self.permission_model.granted_to_id == user_id)
                .options(selectinload(self.permission_model.owner))
            )
            result = await session.execute(query)
            permissions = result.scalars().all()

            if not permissions:
                return []

            # Собираем ID владельцев
            owner_ids = [p.owner_id for p in permissions]
            owner_emails = {p.owner_id: p.owner.email for p in permissions}

            # Получаем все публичные задачи этих владельцев
            tasks_query = (
                select(self.task_model)
                .where(
                    and_(
                        self.task_model.owner_id.in_(owner_ids),
                        self.task_model.is_private == False,  # noqa
                    )
                )
                .order_by(self.task_model.created_at.desc())
            )
            tasks_result = await session.execute(tasks_query)
            tasks = tasks_result.scalars().all()

            # Возвращаем задачи вместе с email владельца
            return [(task, owner_emails[task.owner_id]) for task in tasks]
