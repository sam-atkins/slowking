import logging

import redis

from src import config
from src.domain import events

logger = logging.getLogger(__name__)


def publish(event: events.Event):
    """
    Publishes an event to the redis broker
    """
    message = event.dict()
    channel = message.get("channel")
    logger.info(f"publish channel_from_message: {channel}")

    subscribed_channels = config.get_redis_subscribe_channels()
    if channel is None or channel not in subscribed_channels:
        logger.warning(f"Channel {channel} not found in subscribed channels")
        return

    logging.info(f"publishing: channel={channel}, message={message}")
    broker = redis.Redis(**config.get_redis_host_and_port())
    broker.publish(channel=channel, message=event.json())
