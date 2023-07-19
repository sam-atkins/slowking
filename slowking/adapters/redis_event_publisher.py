import logging

import redis

from slowking.config import settings
from slowking.domain import events

logger = logging.getLogger(__name__)


def publish(event: events.Event):
    """
    Publishes an event to the redis broker
    """
    logger.info(f"publishing event {event} to channel {event.channel}")

    subscribed_channels = settings.REDIS_SUBSCRIBE_CHANNELS
    if event.channel is None or event.channel not in subscribed_channels:
        logger.warning(f"Channel {event.channel} not found in subscribed channels")
        return

    json_message = event.to_json()
    broker = redis.Redis(**settings.REDIS_CONFIG)  # type: ignore
    broker.publish(channel=event.channel, message=json_message)
