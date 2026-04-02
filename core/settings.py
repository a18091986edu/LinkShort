from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict


class DBSettings:
    db_name: str
    db_user: str
    db_pasword: SecretStr
    db_host: str
    dp_port: int
    db_echo: bool

    model_config = SettingsConfigDict(
        env_file="./env", env_file_encoding="utf8", extra="ignore"
    )
