import logging.config
from typing import Callable, Type

from slowking.adapters import orm, redis_event_publisher
from slowking.adapters.db_engine import init_db
from slowking.adapters.notifications import AbstractNotifications, LogNotifications
from slowking.config import settings
from slowking.domain import commands, events
from slowking.service_layer import handlers, messagebus, unit_of_work

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

    injected_command_handlers: dict[Type[commands.Command], list[Callable]] = {
        commands.CreateBenchmark: [
            lambda c: handlers.create_benchmark(c, uow, publish)
        ],
        commands.UpdateDocument: [
            lambda e: handlers.update_document(e, uow, publish),
            lambda e: handlers.check_all_documents_uploaded(e, uow, publish),
        ],
    }

    injected_event_handlers: dict[Type[events.Event], list[Callable]] = {
        events.BenchmarkCreated: [
            lambda e: handlers.get_artifacts(e),
            lambda e: handlers.create_project(e, uow, publish),
        ],
        events.ProjectCreated: [
            lambda e: handlers.upload_documents(e),
        ],
        events.DocumentUpdated: [
            lambda e: handlers.check_all_documents_uploaded(e, uow, publish),
        ],
    }

    return messagebus.MessageBus(
        command_handlers=injected_command_handlers,
        event_handlers=injected_event_handlers,
    )
