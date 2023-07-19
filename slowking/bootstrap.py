import logging.config
from typing import Callable, Type

from slowking.adapters import orm, redis_event_publisher
from slowking.adapters.http import EigenClient
from slowking.adapters.notifications import AbstractNotifications, EmailNotifications
from slowking.domain import commands, events
from slowking.service_layer import handlers, messagebus, unit_of_work

logger = logging.getLogger(__name__)


def bootstrap(
    start_orm: bool = True,
    notifications: AbstractNotifications = None,  # type: ignore
    publish: Callable[[events.Event], None] = redis_event_publisher.publish,
    uow: unit_of_work.AbstractUnitOfWork = unit_of_work.SqlAlchemyUnitOfWork(),
    client: Type[EigenClient] = EigenClient,
) -> messagebus.MessageBus:
    if start_orm:
        orm.start_mappers()
        logger.info("Bootstrap DB and ORM setup completed")

    if notifications is None:
        notifications = EmailNotifications()

    injected_command_handlers: dict[Type[commands.Command], list[Callable]] = {
        commands.CreateBenchmark: [
            lambda c: handlers.create_benchmark(c, uow, publish)
        ],
        commands.UpdateDocument: [
            lambda e: handlers.update_document(
                e,
                uow,
                publish,
            ),
        ],
    }

    injected_event_handlers: dict[Type[events.Event], list[Callable]] = {
        events.BenchmarkCreated: [
            lambda e: handlers.create_project(e, uow, publish, client),
        ],
        events.ProjectCreated: [
            lambda e: handlers.upload_documents(e, client, uow),
        ],
        events.DocumentUpdated: [
            lambda e: handlers.check_all_documents_uploaded(e, uow, publish),
        ],
        events.AllDocumentsUploaded: [
            lambda e: handlers.create_report(e, uow, notifications),
        ],
    }

    return messagebus.MessageBus(
        uow=uow,
        command_handlers=injected_command_handlers,
        event_handlers=injected_event_handlers,
    )
