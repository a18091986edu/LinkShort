from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class MC(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf8", extra="ignore", case_sensitive=False
    )


class DBSettings(MC):
    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str
    db_port: int
    db_echo: bool

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}"


class EmailSettings(MC):
    email_host: str
    email_port: int
    email_username: str
    email_password: SecretStr


class RedisSettings(MC):
    redis_host: str
    redis_port: int
    redis_db: int

    @property
    def redis_url(self):
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


class Settings(MC):
    db_settings: DBSettings = DBSettings()
    email_settings: EmailSettings = EmailSettings()
    redis_settings: RedisSettings = RedisSettings()
    secret_key: SecretStr
    frontend_url: str
    access_token_expire: int
    link_length: int = 12

    @property
    def templates_path(self) -> Path:
        """Возвращает абсолютный путь к директории шаблонов"""
        root_dir = Path(__file__).parent.parent
        print
        return root_dir / "templates"


settings = Settings()
