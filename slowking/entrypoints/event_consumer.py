import json
import logging.config
from typing import Any

import redis

from slowking import bootstrap, config
from slowking.config import settings
from slowking.domain import events
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

    # Andrew feedback:
    # TODO consider a dict of topic: [functions] instead of a switch statement
    # functools.partial() may be useful here

    match topic:
        case events.EventChannelEnum.BENCHMARK_CREATED.value:
            event = events.BenchmarkCreated(**payload)
            bus.handle(event)
        case events.EventChannelEnum.PROJECT_CREATED.value:
            event = events.ProjectCreated(**payload)
            bus.handle(event)
        case events.EventChannelEnum.DOCUMENT_UPDATED.value:
            event = events.DocumentUpdated(**payload)
            bus.handle(event)
        case _:
            logger.warning(f"Channel {channel} not found for message: {message}")
            return


if __name__ == "__main__":
    logging.config.dictConfig(config.logger_dict_config())
    main()
