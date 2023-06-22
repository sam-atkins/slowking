import os
from logging import getLogger

from src.domain.commands import CommandChannelEnum
from src.domain.events import EventChannelEnum

logger = getLogger(__name__)


def get_redis_host_and_port():
    host = os.environ.get("REDIS_HOST", "redis-broker")
    port = os.environ.get("REDIS_PORT", 63791)
    return {"host": host, "port": port}


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 54321 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "abc123")
    user, db_name = "allocation", "allocation"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_redis_subscribe_channels():
    event_channels = EventChannelEnum.get_event_channels()
    cmd_channels = CommandChannelEnum.get_command_channels()
    channels = event_channels + cmd_channels
    logger.info(f"get_redis_subscribe_channels: {channels}")
    return channels


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
