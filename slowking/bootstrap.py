import logging.config
from typing import Callable, Type

from slowking.adapters import orm, redis_event_publisher
from slowking.adapters.notifications import AbstractNotifications, LogNotifications
from slowking.domain import commands, events
from slowking.service_layer import handlers, messagebus

logger = logging.getLogger(__name__)


# Note, unit_of_work.SqlAlchemyUnitOfWork() is not injected into the handlers
# to avoid concurrency issues with the db session
def bootstrap(
    start_orm: bool = True,
    notifications: AbstractNotifications = None,  # type: ignore
    publish: Callable[[events.Event], None] = redis_event_publisher.publish,
) -> messagebus.MessageBus:
    if start_orm:
        orm.start_mappers()
        logger.info("Bootstrap DB and ORM setup completed")

    if notifications is None:
        notifications = LogNotifications()

    injected_command_handlers: dict[Type[commands.Command], list[Callable]] = {
        commands.CreateBenchmark: [lambda c: handlers.create_benchmark(c, publish)],
        commands.UpdateDocument: [
            lambda e: handlers.update_document(e, publish),
        ],
    }

    injected_event_handlers: dict[Type[events.Event], list[Callable]] = {
        events.BenchmarkCreated: [
            lambda e: handlers.get_artifacts(e),
            lambda e: handlers.create_project(e, publish),
        ],
        events.ProjectCreated: [
            lambda e: handlers.upload_documents(e),
        ],
        events.DocumentUpdated: [
            lambda e: handlers.check_all_documents_uploaded(e, publish),
        ],
        events.AllDocumentsUploaded: [
            lambda e: handlers.create_report(e),
        ],
    }

    return messagebus.MessageBus(
        command_handlers=injected_command_handlers,
        event_handlers=injected_event_handlers,
    )
