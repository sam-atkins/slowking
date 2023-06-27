import os
from logging import getLogger
from typing import Any, Optional

from pydantic import BaseSettings, validator

from src.domain.commands import CommandChannelEnum
from src.domain.events import EventChannelEnum

logger = getLogger(__name__)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # SERVER_NAME: str
    # SERVER_HOST: AnyHttpUrl

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_CONFIG: Optional[dict[str, Any]] = None

    @validator("REDIS_CONFIG", pre=True)
    def assemble_redis_config(cls, v: Optional[str], values: dict[str, Any]) -> Any:
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

    # POSTGRES_SERVER: str
    # POSTGRES_USER: str
    # POSTGRES_PASSWORD: str
    # POSTGRES_DB: str
    # SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    # @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    # def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
    #     if isinstance(v, str):
    #         return v
    #     return PostgresDsn.build(
    #         scheme="postgresql",
    #         user=values.get("POSTGRES_USER"),
    #         password=values.get("POSTGRES_PASSWORD"),
    #         host=values.get("POSTGRES_SERVER"),
    #         path=f"/{values.get('POSTGRES_DB') or ''}",
    #     )

    class Config:
        case_sensitive = True


settings = Settings()

# def get_redis_host_and_port():
#     host = os.environ.get("REDIS_HOST", "slowking-redis-broker")
#     port = os.environ.get("REDIS_PORT", 63791)
#     return {"host": host, "port": port}


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 54321 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "abc123")
    user = "slowking"
    return f"postgresql://{user}:{password}@{host}:{port}"


# def get_redis_subscribe_channels():
#     event_channels = EventChannelEnum.get_event_channels()
#     cmd_channels = CommandChannelEnum.get_command_channels()
#     channels = event_channels + cmd_channels
#     logger.info(f"get_redis_subscribe_channels: {channels}")
#     return channels


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
