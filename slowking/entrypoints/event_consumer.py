import json
import logging.config
from typing import Any

import redis

from slowking import bootstrap, config
from slowking.config import settings
from slowking.domain.events import EVENT_MAPPER
from slowking.service_layer import messagebus

logger = logging.getLogger(__name__)


r = redis.Redis(**settings.REDIS_CONFIG)  # type: ignore


def main():
    logger.info("Eventbus starting...")
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(*settings.REDIS_SUBSCRIBE_CHANNELS)

    for message in pubsub.listen():
        logger.info(f"Eventbus message received: {message}")
        assign_channel_event_to_handler(message, bus)


def assign_channel_event_to_handler(
    message: dict[Any, Any], bus: messagebus.MessageBus
):
    """
    Assigns a channel message event to a function which will call the message bus
    """
    channel = message["channel"]
    logger.info(
        f"assign_channel_event_to_handler channel {channel} with message: {message}"
    )

    payload = json.loads(message["data"])
    topic = str(channel, "utf-8")

    event = EVENT_MAPPER.get(topic, None)
    if event is None:
        logger.warning(f"Channel {channel} not found for message: {message}")
        return

    e = event(**payload)
    bus.handle(e)


if __name__ == "__main__":
    logging.config.dictConfig(config.logger_dict_config())
    main()
