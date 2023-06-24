import logging
from typing import Callable, Type

from src.domain import commands, events

logger = logging.getLogger(__name__)


def create_benchmark(cmd: commands.CreateBenchmark, publish: Callable):
    logger.info("=== Called CreateBenchmarkHandler CMD ===")
    logger.info(f"CreateBenchmarkHandler cmd: {cmd}")
    # TODO use UOW domain model to create a benchmark in the db
    # TODO emit event: BenchmarkCreated


def create_customer(cmd: commands.CreateCustomer, publish: Callable):
    logger.info("=== Called CreateCustomerHandler CMD ===")
    logger.info(f"CreateCustomerHandler cmd: {cmd}")
    logger.info(f"CreateCustomerHandler received first_name: {cmd.first_name}")
    logger.info(f"CreateCustomerHandler received surname: {cmd.surname}")

    publish(
        events.CustomerCreated(
            channel=events.EventChannelEnum.CREATED_CUSTOMER,
            first_name=cmd.first_name,
            surname=cmd.surname,
        ),
    )


def send_customer_email_event(event: events.CustomerGreeted):
    logger.info("=== Called send_customer_email_event ===")
    logger.info(f"send_customer_email_event event: {event}")


def add_customer_to_model(event: events.CustomerCreated):
    logger.info("=== Called add_customer_to_model ===")
    logger.info(f"add_customer_to_model event: {event}")


def set_customer_greeted(event: events.CustomerGreeted):
    logger.info("=== Called set_customer_greeted ===")
    logger.info(f"set_customer_greeted event: {event}")


COMMAND_HANDLERS: dict[Type[commands.Command], Callable] = {
    commands.CreateCustomer: create_customer,
}

EVENT_HANDLERS = {
    events.CustomerCreated: [send_customer_email_event, add_customer_to_model],
    events.CustomerGreeted: [set_customer_greeted],
}
