from typing import Annotated
from apps.auth.depends import get_current_user
from apps.auth.schemas import AuthUser, UserReturnData, UserVerifySchema
from apps.auth.services import UserService
from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register", response_model=UserReturnData, status_code=status.HTTP_201_CREATED
)
async def registration(
    user: AuthUser, service: UserService = Depends(UserService)
) -> UserReturnData:
    return await service.register_user(user=user)


@auth_router.get(path="/register_confirm", status_code=status.HTTP_200_OK)
async def confirm_registration(
    token: str, service: UserService = Depends(UserService)
) -> dict[str, str]:
    await service.confirm_user(token=token)
    return {"message": "Электронная почта подтверждена"}


@auth_router.post(path="/login", status_code=status.HTTP_200_OK)
async def login(
    user: AuthUser, service: UserService = Depends(UserService)
) -> JSONResponse:
    return await service.login_user(user=user)


@auth_router.get(path="/logout", status_code=status.HTTP_200_OK)
async def logout(
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
    service: UserService = Depends(UserService),
) -> JSONResponse:
    return await service.logout_user(user=user)


@auth_router.get(
    path="/get-user", status_code=status.HTTP_200_OK, response_model=UserVerifySchema
)
async def get_auth_user(
    user: Annotated[UserVerifySchema, Depends(get_current_user)],
) -> UserVerifySchema:
    return user
