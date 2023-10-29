from datetime import datetime, timezone
from logging import getLogger
from typing import Any, Optional

from pydantic import BaseSettings, PostgresDsn, validator

from slowking.domain.commands import CommandChannelEnum
from slowking.domain.events import EventChannelEnum

logger = getLogger(__name__)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    API_BENCHMARK_NAMESPACE_V1_STR: str = f"{API_V1_STR}/benchmarks"
    DB_MAX_RETRIES: int = 10
    DB_RETRY_INTERVAL: int = 1
    EMAIL_HOST: str = "slowking-mailhog"
    EMAIL_PORT: int = 1025
    EMAIL_HTTP_PORT: int = 8025
    OUTPUT_DIR: str = "/home/app/reports/"
    OUTPUT_FILENAME: str = (
        f"report_{datetime.now(timezone.utc).strftime('%Y_%m_%d__%H_%M_%S')}.csv"
    )

    SLOWKING_REDIS_HOST: str
    SLOWKING_REDIS_PORT: str
    REDIS_CONFIG: Optional[dict[str, Any]] = None

    @validator("REDIS_CONFIG", pre=True)
    def assemble_redis_config(cls, v: Optional[str], values: dict[str, str]) -> Any:
        if isinstance(v, str):
            return v
        return {
            "host": values.get("SLOWKING_REDIS_HOST"),
            "port": values.get("SLOWKING_REDIS_PORT"),
        }

    REDIS_SUBSCRIBE_CHANNELS: list[str] = []

    @validator("REDIS_SUBSCRIBE_CHANNELS", pre=True)
    def assemble_redis_subscribe_channels(
        cls, v: Optional[str], values: dict[str, Any]
    ) -> list[str]:
        event_channels = EventChannelEnum.get_event_channels()
        cmd_channels = CommandChannelEnum.get_command_channels()
        channels = event_channels + cmd_channels
        return channels

    SLOWKING_DB_HOST: str
    SLOWKING_DB_PORT: str
    SLOWKING_POSTGRES_DB: str
    SLOWKING_POSTGRES_PASSWORD: str
    SLOWKING_POSTGRES_USER: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, str]) -> str:
        if isinstance(v, str):
            return v
        dsn = PostgresDsn.build(
            scheme="postgresql",
            user=values.get("SLOWKING_POSTGRES_USER"),
            password=values.get("SLOWKING_POSTGRES_PASSWORD"),
            host=values.get("SLOWKING_DB_HOST", ""),
            port=values.get("SLOWKING_DB_PORT"),
            path=f"/{values.get('SLOWKING_POSTGRES_DB') or ''}",
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
