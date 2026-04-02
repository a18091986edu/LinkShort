from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from apps.auth.depends import get_current_user
from apps.auth.schemas import UserVerifySchema
from apps.profile.schemas import ChangeEmailRequest, ChangePasswordRequest
from apps.profile.services import ProfileService

profile_router = APIRouter(prefix="/profile", tags=["profile"])


@profile_router.post("/change-email", status_code=status.HTTP_200_OK)
async def change_email(
    data: ChangeEmailRequest,
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    service: ProfileService = Depends(ProfileService),
) -> None:
    """
    Изменяет адрес электронной почты текущего пользователя.

    :param data: Данные с новым адресом электронной почты пользователя.
    :type data: ChangeEmailRequest
    :param user: Авторизованный пользователь, инициирующий изменение почты.
    :type user: UserVerifySchema
    :param service: Сервисный слой, выполняющий бизнес-логику профиля.
    :type service: ProfileService
    :returns: None
    """
    return await service.change_email(data=data, user=user)


@profile_router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    data: ChangePasswordRequest,
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    service: ProfileService = Depends(ProfileService),
) -> Response:
    """
    Обновляет пароль авторизованного пользователя.

    :param data: Данные с текущим и новым паролем.
    :type data: ChangePasswordRequest
    :param user: Пользователь, для которого выполняется смена пароля.
    :type user: UserVerifySchema
    :param service: Сервис профиля, реализующий проверку и обновление данных.
    :type service: ProfileService
    :returns: HTTP-ответ, подтверждающий успешную операцию либо ошибку.
    :rtype: Response
    """
    return await service.change_password(data=data, user=user)
