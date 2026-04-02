from fastapi import Depends, HTTPException
from starlette import status

from apps.auth.schemas import UserVerifySchema
from apps.tasks.managers import TasksManager
from apps.tasks.schemas import (
    CreateTaskSchema,
    DeleteTaskSchema,
    TaskSchema,
    UpdateTaskSchema,
)


class TasksService:
    """
    Сервисный слой для работы с задачами пользователя.
    """

    def __init__(self, manager: TasksManager = Depends(TasksManager)) -> None:
        """
        Создает сервис со связанным менеджером задач.

        :param manager: Менеджер, выполняющий операции с базой данных.
        """
        self.manager = manager

    async def get_task(self, task_id: str, user: UserVerifySchema) -> TaskSchema:
        """
        Получает задачу по ID с проверкой прав.

        :param task_id: ID задачи.
        :param user: Текущий пользователь.
        :returns: Задача.
        """
        task = await self.manager.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this task",
            )

        return task

    async def get_user_tasks(self, user: UserVerifySchema) -> list[TaskSchema]:
        """
        Возвращает все задачи пользователя.

        :param user: Текущий пользователь.
        :returns: Список задач.
        """
        return await self.manager.get_user_tasks(user_id=user.id)

    async def create_task(
        self, task_data: CreateTaskSchema, user: UserVerifySchema
    ) -> TaskSchema:
        """
        Создает новую задачу для пользователя.

        :param task_data: Данные задачи.
        :param user: Текущий пользователь.
        :returns: Созданная задача.
        """
        return await self.manager.create_task(
            task=task_data.task,
            user_id=user.id,
            description=task_data.description,
            is_private=task_data.is_private,
            deadline=task_data.deadline,
        )

    async def update_task(
        self, task_id: str, task_data: UpdateTaskSchema, user: UserVerifySchema
    ) -> TaskSchema:
        """
        Обновляет задачу пользователя.

        :param task_id: ID задачи.
        :param task_data: Данные для обновления.
        :param user: Текущий пользователь.
        :returns: Обновленная задача.
        """
        return await self.manager.update_task(
            task_id=task_id,
            user_id=user.id,
            task=task_data.task,
            description=task_data.description,
            is_private=task_data.is_private,
            is_done=task_data.is_done,
            deadline=task_data.deadline,
        )

    async def delete_task(
        self, task_data: DeleteTaskSchema, user: UserVerifySchema
    ) -> None:
        """
        Удаляет задачу пользователя.

        :param task_data: Данные с ID задачи.
        :param user: Текущий пользователь.
        """
        await self.manager.delete_task(task_id=task_data.id, user_id=user.id)
