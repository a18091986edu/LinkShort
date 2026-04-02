from fastapi import Depends
from starlette.responses import JSONResponse

from apps.auth.handlers import AuthHandler
from apps.auth.schemas import UserVerifySchema
from apps.profile.managers import ProfileManager
from apps.profile.schemas import ChangeEmailRequest, ChangePasswordRequest


class ProfileService:
    """
    Сервис для работы с данными профиля пользователя.
    """

    def __init__(
        self,
        manager: ProfileManager = Depends(ProfileManager),
        handler: AuthHandler = Depends(AuthHandler),
    ) -> None:
        """
        Создает экземпляр сервиса профиля с необходимыми зависимостями.

        :param manager: Менеджер для выполнения операций с моделью пользователя.
        :type manager: ProfileManager
        :param handler: Обработчик аутентификации, предоставляющий функции хеширования и проверки пароля.
        :type handler: AuthHandler
        """
        self.manager = manager
        self.handler = handler

    async def change_email(
        self, data: ChangeEmailRequest, user: UserVerifySchema
    ) -> None:
        """
        Обновляет адрес электронной почты пользователя.

        :param data: Запрос с новым адресом электронной почты.
        :type data: ChangeEmailRequest
        :param user: Пользователь, для которого применяется изменение.
        :type user: UserVerifySchema
        :returns: None
        """
        return await self.manager.update_user_fields(
            user_id=user.id, email=data.new_email
        )

    async def change_password(
        self, data: ChangePasswordRequest, user: UserVerifySchema
    ) -> None | JSONResponse:
        """
        Изменяет пароль пользователя после проверки старого значения.

        :param data: Запрос, содержащий старый и новый пароль.
        :type data: ChangePasswordRequest
        :param user: Пользователь, выполняющий смену пароля.
        :type user: UserVerifySchema
        :returns: None при успешном обновлении либо JSON-ответ с ошибкой.
        :rtype: None | JSONResponse
        """
        current_password_hash = await self.manager.get_user_hashed_password(
            user_id=user.id
        )

        if await self.handler.verify_password(
            raw_password=data.old_password, hashed_password=current_password_hash
        ):
            hashed_password = await self.handler.get_password_hash(
                password=data.new_password
            )
            await self.manager.update_user_fields(
                user_id=user.id, hashed_password=hashed_password
            )
            return None

        return JSONResponse({"error": "Invalid password"}, status_code=401)
