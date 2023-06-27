from logging import getLogger
from typing import Any, Optional

from pydantic import BaseSettings, PostgresDsn, validator

from src.domain.commands import CommandChannelEnum
from src.domain.events import EventChannelEnum

logger = getLogger(__name__)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_CONFIG: Optional[dict[str, Any]] = None

    @validator("REDIS_CONFIG", pre=True)
    def assemble_redis_config(cls, v: Optional[str], values: dict[str, str]) -> Any:
        if isinstance(v, str):
            return v
        return {"host": values.get("REDIS_HOST"), "port": values.get("REDIS_PORT")}

    REDIS_SUBSCRIBE_CHANNELS: list[str] = []

    @validator("REDIS_SUBSCRIBE_CHANNELS", pre=True)
    def assemble_redis_subscribe_channels(
        cls, v: Optional[str], values: dict[str, Any]
    ) -> list[str]:
        event_channels = EventChannelEnum.get_event_channels()
        cmd_channels = CommandChannelEnum.get_command_channels()
        channels = event_channels + cmd_channels
        return channels

    DB_HOST: str
    DB_PORT: str
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, str]) -> str:
        if isinstance(v, str):
            return v
        dsn = PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("DB_HOST", ""),
            port=values.get("DB_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
        return dsn

    class Config:
        case_sensitive = True


settings = Settings()  # type: ignore


def logger_dict_config():
    conf = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s %(levelname)s %(filename)s: %(message)s"
            }
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "standard",
            }
        },
        "loggers": {
            "": {"handlers": ["default"], "level": "INFO", "propagate": True},
            "uvicorn.error": {"level": "INFO", "propagate": True},
            "uvicorn.access": {"level": "INFO", "propagate": True},
        },
    }
    return conf
