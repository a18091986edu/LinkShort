from typing import Annotated

from fastapi import APIRouter, Depends, Path
from starlette import status

from apps.auth.depends import get_current_user
from apps.auth.schemas import UserVerifySchema
from apps.tasks.schemas import (
    CreateTaskSchema,
    DeleteTaskSchema,
    TaskSchema,
    UpdateTaskSchema,
)
from apps.tasks.services import TasksService
from apps.tasks.permission_manager import PermissionManager
from apps.tasks.schemas import GrantAccessSchema, RevokeAccessSchema
from apps.tasks.schemas import TaskWithOwnerSchema

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.get(
    "/{task_id}",
    response_model=TaskSchema,
    status_code=status.HTTP_200_OK,
)
async def get_task(
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    task_id: str = Path(..., description="ID задачи"),
    service: TasksService = Depends(TasksService),
) -> TaskSchema:
    """
    Получает задачу по её ID.

    :param task_id: UUID задачи
    :param user: Авторизованный пользователь
    :returns: Задача
    """
    return await service.get_task(task_id=task_id, user=user)


@tasks_router.get(
    "/",
    response_model=list[TaskSchema],
    status_code=status.HTTP_200_OK,
)
async def get_user_tasks(
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    service: TasksService = Depends(TasksService),
) -> list[TaskSchema]:
    """
    Возвращает список задач текущего пользователя.

    :param user: Авторизованный пользователь
    :returns: Список задач
    """
    return await service.get_user_tasks(user=user)


@tasks_router.post(
    "/",
    response_model=TaskSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task_data: CreateTaskSchema,
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    service: TasksService = Depends(TasksService),
) -> TaskSchema:
    """
    Создает новую задачу для пользователя.

    :param task_data: Данные задачи
    :param user: Авторизованный пользователь
    :returns: Созданная задача
    """
    return await service.create_task(task_data=task_data, user=user)


@tasks_router.put(
    "/{task_id}",
    response_model=TaskSchema,
    status_code=status.HTTP_200_OK,
)
async def update_task(
    task_id: str = Path(..., description="ID задачи"),
    task_data: UpdateTaskSchema = None,
    user: Annotated[UserVerifySchema, Depends(get_current_user)] = None,
    service: TasksService = Depends(TasksService),
) -> TaskSchema:
    """
    Обновляет задачу пользователя.

    :param task_id: ID задачи
    :param task_data: Данные для обновления
    :param user: Авторизованный пользователь
    :returns: Обновленная задача
    """
    return await service.update_task(task_id=task_id, task_data=task_data, user=user)


@tasks_router.patch(
    "/{task_id}",
    response_model=TaskSchema,
    status_code=status.HTTP_200_OK,
)
async def partial_update_task(
    task_id: str = Path(..., description="ID задачи"),
    task_data: UpdateTaskSchema = None,
    user: Annotated[UserVerifySchema, Depends(get_current_user)] = None,
    service: TasksService = Depends(TasksService),
) -> TaskSchema:
    """
    Частично обновляет задачу пользователя (PATCH).

    :param task_id: ID задачи
    :param task_data: Данные для обновления
    :param user: Авторизованный пользователь
    :returns: Обновленная задача
    """
    return await service.update_task(task_id=task_id, task_data=task_data, user=user)


@tasks_router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task_data: DeleteTaskSchema,
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    service: TasksService = Depends(TasksService),
) -> None:
    """
    Удаляет задачу пользователя.

    :param task_data: Данные с ID задачи
    :param user: Авторизованный пользователь
    """
    await service.delete_task(task_data=task_data, user=user)


@tasks_router.post("/access/grant", status_code=status.HTTP_200_OK)
async def grant_access(
    data: GrantAccessSchema,
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    permission_manager: PermissionManager = Depends(PermissionManager),
) -> dict:
    """
    Дает доступ другому пользователю к своим ПУБЛИЧНЫМ задачам
    """
    return await permission_manager.grant_access(
        owner_id=user.id, target_email=data.user_email
    )


@tasks_router.delete("/access/revoke", status_code=status.HTTP_200_OK)
async def revoke_access(
    data: RevokeAccessSchema,
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    permission_manager: PermissionManager = Depends(PermissionManager),
) -> dict:
    """
    Отзывает доступ у пользователя
    """
    return await permission_manager.revoke_access(
        owner_id=user.id, target_email=data.user_email
    )


@tasks_router.get(
    "/access/granted-users", response_model=list[dict], status_code=status.HTTP_200_OK
)
async def get_granted_users(
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    permission_manager: PermissionManager = Depends(PermissionManager),
) -> list[dict]:
    """
    Возвращает список пользователей, которым вы дали доступ к своим задачам
    """
    return await permission_manager.get_granted_users(owner_id=user.id)


@tasks_router.get(
    "/accessible/public",
    response_model=list[TaskWithOwnerSchema],  # Изменено с TaskSchema
    status_code=status.HTTP_200_OK,
)
async def get_accessible_public_tasks(
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    permission_manager: PermissionManager = Depends(PermissionManager),
) -> list[TaskWithOwnerSchema]:
    """
    Возвращает публичные задачи пользователей, которые дали вам доступ,
    с указанием email владельца каждой задачи
    """
    tasks_with_owners = await permission_manager.get_accessible_public_tasks_with_owner(
        user_id=user.id
    )

    return [
        TaskWithOwnerSchema(
            **TaskSchema.model_validate(task, from_attributes=True).model_dump(),
            owner_email=owner_email,
        )
        for task, owner_email in tasks_with_owners
    ]


@tasks_router.get(
    "/access/granted-by-users",
    response_model=list[dict],
    status_code=status.HTTP_200_OK,
)
async def get_users_who_granted_access(
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    permission_manager: PermissionManager = Depends(PermissionManager),
) -> list[dict]:
    """
    Возвращает список пользователей, которые дали доступ текущему пользователю
    """
    return await permission_manager.get_users_who_granted_access(user_id=user.id)


@tasks_router.get(
    "/accessible/public/by-email/{owner_email}",
    response_model=list[TaskSchema],
    status_code=status.HTTP_200_OK,
)
async def get_accessible_public_tasks_by_email(
    owner_email: str,
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    permission_manager: PermissionManager = Depends(PermissionManager),
) -> list[TaskSchema]:
    """
    Возвращает публичные задачи конкретного пользователя по его email,
    если он дал доступ текущему пользователю
    """
    tasks = await permission_manager.get_accessible_public_tasks_by_email(
        user_id=user.id, owner_email=owner_email
    )
    return [TaskSchema.model_validate(task, from_attributes=True) for task in tasks]


@tasks_router.get(
    "/accessible/public-with-owner",
    response_model=list[TaskWithOwnerSchema],
    status_code=status.HTTP_200_OK,
)
async def get_accessible_public_tasks_with_owner(
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    permission_manager: PermissionManager = Depends(PermissionManager),
) -> list[TaskWithOwnerSchema]:
    """
    Возвращает публичные задачи пользователей, которые дали доступ,
    с указанием email владельца каждой задачи
    """
    tasks_with_owners = await permission_manager.get_accessible_public_tasks_with_owner(
        user_id=user.id
    )

    return [
        TaskWithOwnerSchema(
            **TaskSchema.model_validate(task, from_attributes=True).model_dump(),
            owner_email=owner_email,
        )
        for task, owner_email in tasks_with_owners
    ]
