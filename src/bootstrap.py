from typing import Callable, Type

from src.adapters.redis_event_publisher import publish
from src.domain import commands, events
from src.service_layer import handlers, messagebus


def bootstrap(
    # start_orm: bool = True,
    # uow: unit_of_work.AbstractUnitOfWork = unit_of_work.SqlAlchemyUnitOfWork(),
    # notifications: AbstractNotifications = None,
    publish: Callable = publish,
) -> messagebus.MessageBus:
    # if notifications is None:
    #     notifications = EmailNotifications()

    # if start_orm:
    #     orm.start_mappers()

    injected_command_handlers: dict[Type[commands.Command], Callable] = {
        commands.CreateBenchmark: lambda c: handlers.create_benchmark(c, publish),
        commands.CreateCustomer: lambda c: handlers.create_customer(c, publish),
    }

    injected_event_handlers: dict[Type[events.Event], list[Callable]] = {
        events.CustomerCreated: [
            lambda e: handlers.send_customer_email_event(e),
            lambda e: handlers.add_customer_to_model(e),
        ],
        events.CustomerGreeted: [lambda e: handlers.set_customer_greeted(e)],
    }

    return messagebus.MessageBus(
        command_handlers=injected_command_handlers,
        event_handlers=injected_event_handlers,
    )
