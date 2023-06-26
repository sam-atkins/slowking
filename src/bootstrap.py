import logging.config
from typing import Callable, Type

from src import config
from src.adapters import orm
from src.adapters.db_engine import init_db
from src.adapters.redis_event_publisher import publish
from src.domain import commands, events
from src.service_layer import handlers, messagebus

logger = logging.getLogger(__name__)


def bootstrap(
    start_orm: bool = True,
    # uow: unit_of_work.AbstractUnitOfWork = unit_of_work.SqlAlchemyUnitOfWork(),
    # notifications: AbstractNotifications = None,
    publish: Callable = publish,
) -> messagebus.MessageBus:
    # if notifications is None:
    #     notifications = EmailNotifications()

    if start_orm:
        init_db(db_uri=config.get_postgres_uri(), echo=True)
        orm.start_mappers()
        logger.info("Bootstrap DB and ORM setup completed")

    injected_command_handlers: dict[Type[commands.Command], Callable] = {
        commands.CreateBenchmark: lambda c: handlers.create_benchmark(c, publish),
    }

    injected_event_handlers: dict[Type[events.Event], list[Callable]] = {
        events.BenchmarkCreated: [
            lambda e: handlers.get_artifacts(e),
            lambda e: handlers.create_project(e),
        ],
        events.ProjectCreated: [
            lambda e: handlers.upload_documents(e),
        ],
    }

    return messagebus.MessageBus(
        command_handlers=injected_command_handlers,
        event_handlers=injected_event_handlers,
    )
