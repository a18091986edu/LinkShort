import uuid
from datetime import date

from fastapi import Depends
from sqlalchemy import delete, select, update, insert

from apps.tasks.permission_manager import PermissionManager
from apps.tasks.schemas import TaskSchema
from core.core_dependency.db_dependency import DBDependency
from database.models import Task
from fastapi import HTTPException


class TasksManager:
    """
    Менеджер для выполнения операций над задачами в базе данных.
    """

    def __init__(self, db: DBDependency = Depends(DBDependency)) -> None:
        """
        Инициализирует менеджер с зависимостью доступа к базе данных.

        :param db: Объект для получения асинхронных сессий с базой данных.
        """
        self.db = db
        self.task_model = Task

    async def get_task(self, task_id: uuid.UUID) -> TaskSchema | None:
        """
        Возвращает задачу по её ID.

        :param task_id: Идентификатор задачи.
        :returns: Найденная задача или None.
        """
        async with self.db.db_session() as session:
            query = select(self.task_model).where(self.task_model.id == task_id)
            result = await session.execute(query)
            task = result.scalar_one_or_none()

            if task:
                return TaskSchema.model_validate(task, from_attributes=True)

            return None

    async def get_user_tasks(self, user_id: uuid.UUID) -> list[TaskSchema]:
        """
        Получает список задач, принадлежащих пользователю.

        :param user_id: Идентификатор владельца задач.
        :returns: Список задач пользователя.
        """
        async with self.db.db_session() as session:
            query = (
                select(self.task_model)
                .where(self.task_model.owner_id == user_id)
                .order_by(self.task_model.created_at.desc())
            )

            result = await session.execute(query)
            tasks = result.scalars().all()

            return [
                TaskSchema.model_validate(task, from_attributes=True) for task in tasks
            ]

    async def create_task(
        self,
        task: str,
        user_id: uuid.UUID,
        description: str | None = None,
        is_private: bool = False,
        deadline: date | None = None,
    ) -> TaskSchema:
        """
        Создает новую задачу.

        :param task: Название задачи.
        :param user_id: ID владельца.
        :param description: Описание задачи.
        :param is_private: Приватная ли задача.
        :param deadline: Дедлайн задачи.
        :returns: Созданная задача.
        """
        async with self.db.db_session() as session:
            task_data = {
                "task": task,
                "owner_id": user_id,
                "description": description,
                "is_private": is_private,
                "deadline": deadline,
            }

            query = (
                insert(self.task_model).values(**task_data).returning(self.task_model)
            )

            result = await session.execute(query)
            await session.commit()
            task_obj = result.scalar()

            return TaskSchema.model_validate(task_obj, from_attributes=True)

    async def update_task(
        self, task_id: uuid.UUID, user_id: uuid.UUID, **kwargs
    ) -> TaskSchema:
        """
        Обновляет задачу.

        :param task_id: ID задачи.
        :param user_id: ID владельца (для проверки).
        :param kwargs: Поля для обновления.
        :returns: Обновленная задача.
        :raises HTTPException: Если задача не найдена или нет прав.
        """
        # Убираем None значения
        update_data = {k: v for k, v in kwargs.items() if v is not None}

        if not update_data:
            task = await self.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            return task

        async with self.db.db_session() as session:
            query = (
                update(self.task_model)
                .where(
                    self.task_model.id == task_id,
                    self.task_model.owner_id == user_id,
                )
                .values(**update_data)
                .returning(self.task_model)
            )

            result = await session.execute(query)
            await session.commit()
            task_obj = result.scalar_one_or_none()

            if not task_obj:
                raise HTTPException(
                    status_code=404, detail="Task not found or access denied"
                )

            return TaskSchema.model_validate(task_obj, from_attributes=True)

    async def delete_task(self, task_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """
        Удаляет задачу.

        :param task_id: ID задачи.
        :param user_id: ID владельца (для проверки).
        :raises HTTPException: Если задача не найдена или нет прав.
        """
        async with self.db.db_session() as session:
            query = delete(self.task_model).where(
                self.task_model.id == task_id, self.task_model.owner_id == user_id
            )

            result = await session.execute(query)
            await session.commit()

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404, detail="Task not found or access denied"
                )

    async def get_all_accessible_tasks(self, user_id: uuid.UUID) -> list[TaskSchema]:
        """
        Возвращает все задачи пользователя:
        - свои задачи (все)
        - публичные задачи тех, кто дал доступ
        """
        async with self.db.db_session() as session:
            # Свои задачи
            own_tasks_query = select(self.task_model).where(
                self.task_model.owner_id == user_id
            )
            own_result = await session.execute(own_tasks_query)
            own_tasks = own_result.scalars().all()

            # Публичные задачи от тех, кто дал доступ
            permission_manager = PermissionManager(self.db)
            accessible_tasks = await permission_manager.get_accessible_public_tasks(
                user_id
            )

            # Объединяем
            all_tasks = own_tasks + accessible_tasks

            # Убираем дубликаты на всякий случай
            unique_tasks = {task.id: task for task in all_tasks}.values()

            return [
                TaskSchema.model_validate(task, from_attributes=True)
                for task in unique_tasks
            ]
