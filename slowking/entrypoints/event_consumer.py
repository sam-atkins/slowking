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
    match topic:
        case events.EventChannelEnum.BENCHMARK_CREATED.value:
            publish_benchmark_created_event(payload, bus)
        case _:
            logger.warning(f"Channel {channel} not found for message: {message}")
            return


def publish_benchmark_created_event(message_payload, bus):
    logger.info(f"publish_benchmark_created_event with payload: {message_payload}")
    event = events.BenchmarkCreated(
        channel=events.EventChannelEnum.BENCHMARK_CREATED,
        name=message_payload["name"],
        benchmark_id=message_payload["benchmark_id"],
        benchmark_type=message_payload["benchmark_type"],
        target_infra=message_payload["target_infra"],
        target_url=message_payload["target_url"],
        target_release_version=message_payload["target_release_version"],
        username=message_payload["username"],
        password=message_payload["password"],
    )
    bus.handle(event)


if __name__ == "__main__":
    logging.config.dictConfig(config.logger_dict_config())
    main()