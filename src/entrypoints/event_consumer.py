import json
import logging.config

import redis

from src import bootstrap, config
from src.domain import commands, events

logger = logging.getLogger(__name__)


r = redis.Redis(**config.get_redis_host_and_port())


def main():
    logger.info("Eventbus starting...")
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(*config.get_redis_subscribe_channels())

    for message in pubsub.listen():
        logger.info(f"Eventbus message received: {message}")
        assign_channel_message_to_handler(message, bus)


def assign_channel_message_to_handler(message, bus):
    channel = message["channel"]
    logger.info(
        f"assign_channel_message_to_handler channel {channel} with message: {message}"
    )

    payload = json.loads(message["data"])
    topic = str(channel, "utf-8")
    match topic:
        case commands.CommandChannelEnum.CREATE_CUSTOMER.value:
            handle_create_customer(payload, bus)
        case events.EventChannelEnum.CREATED_CUSTOMER.value:
            handle_customer_created(payload, bus)
        case _:
            logger.warning(f"Channel {channel} not found in EVENTS_MAPPING")
            return


def handle_create_customer(message_payload, bus):
    logger.info(f"handle_create_customer with payload: {message_payload}")
    cmd = commands.CreateCustomer(
        channel=commands.CommandChannelEnum.CREATE_CUSTOMER,
        first_name=message_payload["first_name"],
        surname=message_payload["surname"],
    )
    bus.handle(cmd)


def handle_customer_created(message_payload, bus):
    logger.info(f"handle_create_customer with payload: {message_payload}")
    event = events.CustomerCreated(
        channel=events.EventChannelEnum.CREATED_CUSTOMER,
        first_name=message_payload["first_name"],
        surname=message_payload["surname"],
    )
    bus.handle(event)


if __name__ == "__main__":
    logging.config.dictConfig(config.logger_dict_config())
    main()
