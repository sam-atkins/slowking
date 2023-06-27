import logging

import redis

from src.config import settings
from src.domain import events

logger = logging.getLogger(__name__)


def publish(event: events.Event):
    """
    Publishes an event to the redis broker
    """
    logger.info(f"publish channel_from_message: {event.channel}")

    subscribed_channels = settings.REDIS_SUBSCRIBE_CHANNELS
    if event.channel is None or event.channel not in subscribed_channels:
        logger.warning(f"Channel {event.channel} not found in subscribed channels")
        return

    logging.info(f"publishing: channel={event.channel}, message={event.dict()}")
    broker = redis.Redis(**settings.REDIS_CONFIG)  # type: ignore
    broker.publish(channel=event.channel, message=event.json())
