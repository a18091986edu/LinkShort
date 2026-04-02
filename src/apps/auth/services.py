from fastapi.responses import JSONResponse
from apps.auth.handlers import AuthHandler
from apps.auth.managers import UserManager
from apps.auth.schemas import AuthUser, CreateUser, UserReturnData, UserVerifySchema
from apps.auth.tasks import send_confirmation_email
from core.settings import settings
from fastapi import Depends, HTTPException, status
from itsdangerous import BadSignature, URLSafeTimedSerializer


class UserService:
    def __init__(
        self,
        manager: UserManager = Depends(UserManager),
        handler: AuthHandler = Depends(AuthHandler),
    ):
        self.manager = manager
        self.handler = handler
        self.serializer = URLSafeTimedSerializer(
            secret_key=settings.secret_key.get_secret_value()
        )

    async def register_user(self, user: AuthUser) -> UserReturnData:
        hashed_password = await self.handler.get_password_hash(user.password)

        new_user = CreateUser(email=user.email, hashed_password=hashed_password)

        user_data = await self.manager.create_user(user=new_user)

        confirmation_token = self.serializer.dumps(user_data.email)
        send_confirmation_email.delay(
            to_email=user_data.email, token=confirmation_token
        )

        return user_data

    async def confirm_user(self, token: str) -> None:
        try:
            email = self.serializer.loads(token, max_age=3600)
        except BadSignature:
            raise HTTPException(
                status_code=400, detail="Неверный или просроченный токен"
            )

        await self.manager.confirm_user(email=email)

    async def login_user(self, user: AuthUser) -> JSONResponse:
        exist_user = await self.manager.get_user_by_email(email=user.email)

        if exist_user is None or not await self.handler.verify_password(
            hashed_password=exist_user.hashed_password, raw_password=user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong email or password",
            )

        token, session_id = await self.handler.create_access_token(
            user_id=exist_user.id
        )

        await self.manager.store_access_token(
            token=token, user_id=exist_user.id, session_id=session_id
        )

        response = JSONResponse(content={"message": "Вход успешен"})
        response.set_cookie(
            key="Authorization",
            value=token,
            httponly=True,
            max_age=settings.access_token_expire,
        )

        return response

    async def logout_user(self, user: UserVerifySchema) -> JSONResponse:
        await self.manager.revoke_access_token(
            user_id=user.id, session_id=user.session_id
        )

        response = JSONResponse(content={"message": "Logged out"})
        response.delete_cookie(key="Authorization")

        return response
