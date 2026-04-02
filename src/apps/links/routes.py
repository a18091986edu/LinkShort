from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from apps.auth.depends import get_current_user
from apps.auth.schemas import UserVerifySchema
from apps.links.schemas import (
    CreateLinkSchema,
    DeleteLinkSchema,
    GetLinkSchema,
    LinkSchema,
)
from apps.links.services import LinksService

links_router = APIRouter(prefix="/links", tags=["links"])


@links_router.get(
    "/get_link", response_model=GetLinkSchema | None, status_code=status.HTTP_200_OK
)
async def get_link(
    short_link: str, service: LinksService = Depends(LinksService)
) -> GetLinkSchema | None:
    """
    Создаёт новую сокращённую ссылку для пользователя.

    **Параметры:**
    - **link_data** — полный адрес ссылки

    **Возвращает:** созданную ссылку с коротким идентификатором.
    """

    return await service.get_link(short_link=short_link)


@links_router.get(
    "/get_user_links", response_model=list[LinkSchema], status_code=status.HTTP_200_OK
)
async def get_user_links(
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    service: LinksService = Depends(LinksService),
) -> list[LinkSchema]:
    """
    Возвращает список ссылок текущего пользователя.

    :param user: Авторизованный пользователь, для которого запрашиваются ссылки.
    :type user: UserVerifySchema
    :param service: Сервис ссылок, выполняющий выборку данных.
    :type service: LinksService
    :returns: Коллекция ссылок пользователя.
    :rtype: list[LinkSchema]
    """
    return await service.get_links(user=user)


@links_router.post(
    "/create_link", response_model=LinkSchema, status_code=status.HTTP_201_CREATED
)
async def create_link(
    link_data: CreateLinkSchema,
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    service: LinksService = Depends(LinksService),
) -> LinkSchema:
    """
    Создает новую сокращенную ссылку для пользователя.

    :param link_data: Данные с полным адресом ссылки.
    :type link_data: CreateLinkSchema
    :param user: Пользователь, для которого создается ссылка.
    :type user: UserVerifySchema
    :param service: Сервис ссылок, отвечающий за генерацию и сохранение записи.
    :type service: LinksService
    :returns: Созданная ссылка с коротким идентификатором.
    :rtype: LinkSchema
    """
    return await service.create_link(link_data=link_data, user=user)


@links_router.delete("/delete_link", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    link_data: DeleteLinkSchema,
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    service: LinksService = Depends(LinksService),
) -> None:
    """
    Удаляет ссылку, если она принадлежит текущему пользователю.

    :param link_data: Данные с идентификатором ссылки для удаления.
    :type link_data: DeleteLinkSchema
    :param user: Авторизованный пользователь, запрашивающий удаление.
    :type user: UserVerifySchema
    :param service: Сервис ссылок, выполняющий проверку владельца и удаление.
    :type service: LinksService
    :returns: None
    """
    await service.delete_link(link_data=link_data, user=user)
