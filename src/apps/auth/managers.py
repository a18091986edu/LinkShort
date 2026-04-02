import uuid

from apps.auth.schemas import (
    CreateUser,
    GetUserForAdmin,
    GetUserWithIDAndEmail,
    UserReturnData,
    UserVerifySchema,
)
from core.core_dependency.db_dependency import DBDependency
from core.core_dependency.redis_dependency import RedisDependency
from database.models import User
from fastapi import Depends, HTTPException
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError


class UserManager:
    def __init__(
        self,
        db: DBDependency = Depends(DBDependency),
        redis: RedisDependency = Depends(RedisDependency),
    ) -> None:
        self.db = db
        self.model = User
        self.redis = redis

    async def create_user(self, user: CreateUser) -> UserReturnData:
        async with self.db.db_session() as session:
            query = insert(self.model).values(**user.model_dump()).returning(self.model)

            try:
                result = await session.execute(query)
            except IntegrityError:
                raise HTTPException(status_code=400, detail="User already exists.")

            await session.commit()

            user_data = result.scalar_one()
            return UserReturnData(**user_data.__dict__)

    async def confirm_user(self, email: str) -> None:
        async with self.db.db_session() as session:
            query = (
                update(self.model)
                .where(self.model.email == email)
                .values(is_verified=True, is_active=True)
            )
            await session.execute(query)
            await session.commit()

    async def get_user_by_email(self, email: str) -> GetUserWithIDAndEmail | None:
        async with self.db.db_session() as session:
            query = select(
                self.model.id, self.model.email, self.model.hashed_password
            ).where(self.model.email == email)

            result = await session.execute(query)
            user = result.mappings().first()

            if user:
                return GetUserWithIDAndEmail(**user)

            return None

    async def store_access_token(
        self, token: str, user_id: uuid.UUID, session_id: str
    ) -> None:
        async with self.redis.get_client() as client:
            await client.set(f"{user_id}:{session_id}", token)

    async def get_access_token(
        self, user_id: uuid.UUID | str, session_id: str
    ) -> str | None:
        async with self.redis.get_client() as client:
            return await client.get(f"{user_id}:{session_id}")

    async def get_user_by_id(self, user_id: uuid.UUID | str) -> UserVerifySchema | None:
        async with self.db.db_session() as session:
            query = select(self.model.id, self.model.email).where(
                self.model.id == user_id
            )

            result = await session.execute(query)
            user = result.mappings().one_or_none()

            if user:
                return UserVerifySchema(**user)

            return None

    async def revoke_access_token(
        self, user_id: uuid.UUID | str, session_id: str
    ) -> None:
        async with self.redis.get_client() as client:
            await client.delete(f"{user_id}:{session_id}")

    async def get_user_by_email_for_admin(self, email: str) -> GetUserForAdmin | None:
        async with self.db.db_session() as session:
            query = select(
                self.model.id,
                self.model.email,
                self.model.hashed_password,
                self.model.is_superuser,
            ).where(self.model.email == email)

            result = await session.execute(query)
            user = result.mappings().first()

            if user:
                return GetUserForAdmin(**user)

            return None
