import asyncio
import datetime
import uuid

from fastapi import HTTPException, status

import bcrypt
import jwt
from apps.auth.named_tuples import CreateTokenTuple
from core.settings import settings


class AuthHandler:
    secret = settings.secret_key.get_secret_value()

    async def get_password_hash(self, password: str) -> str:
        """Хэширование пароля"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    async def verify_password(self, raw_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(
            raw_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    async def create_access_token(self, user_id: uuid.UUID) -> CreateTokenTuple:
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            seconds=settings.access_token_expire
        )
        session_id = str(uuid.uuid4())

        data = {"exp": expire, "session_id": session_id, "user_id": str(user_id)}

        encoded_jwt = jwt.encode(payload=data, key=self.secret, algorithm="HS256")

        return CreateTokenTuple(encoded_jwt=encoded_jwt, session_id=session_id)

    async def decode_access_token(self, token: str) -> dict:
        try:
            return jwt.decode(jwt=token, key=self.secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )


if __name__ == "__main__":
    ah = AuthHandler()

    async def main():
        password = "tesat"
        hashed = await ah.get_password_hash(password)
        print(f"Hashed password: {hashed}")

        # Проверка
        is_valid = await ah.verify_password(password, hashed)
        print(f"Password valid: {is_valid}")

    asyncio.run(main())
