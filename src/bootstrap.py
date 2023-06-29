import logging.config
from typing import Callable, Type

from src.adapters import orm, redis_event_publisher
from src.adapters.db_engine import init_db
from src.adapters.notifications import AbstractNotifications, LogNotifications
from src.config import settings
from src.domain import commands, events
from src.service_layer import handlers, messagebus, unit_of_work

logger = logging.getLogger(__name__)


def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = unit_of_work.SqlAlchemyUnitOfWork(),
    notifications: AbstractNotifications = None,  # type: ignore
    publish: Callable[[events.Event], None] = redis_event_publisher.publish,
) -> messagebus.MessageBus:
    if start_orm:
        init_db(db_uri=settings.SQLALCHEMY_DATABASE_URI, echo=True)  # type: ignore
        orm.start_mappers()
        logger.info("Bootstrap DB and ORM setup completed")

    if notifications is None:
        notifications = LogNotifications()

    injected_command_handlers: dict[Type[commands.Command], Callable] = {
        # commands.CreateBenchmark: lambda c: handlers.create_benchmark(c, publish),
        commands.CreateBenchmark: lambda c: handlers.create_benchmark(c, uow, publish),
    }

    injected_event_handlers: dict[Type[events.Event], list[Callable]] = {
        events.BenchmarkCreated: [
            lambda e: handlers.get_artifacts(e),
            lambda e: handlers.create_project(e, uow),
        ],
        events.ProjectCreated: [
            lambda e: handlers.upload_documents(e),
        ],
    }

    return messagebus.MessageBus(
        command_handlers=injected_command_handlers,
        event_handlers=injected_event_handlers,
    )
