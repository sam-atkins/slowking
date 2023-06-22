"""
MessageBus is a class that handles the communication between the application
"""
import logging
from typing import Callable, Type, Union

from src.domain import commands, events

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


class MessageBus:
    """
    MessageBus is a class that handles the communication between the application
    """

    def __init__(
        self,
        command_handlers: dict[Type[commands.Command], Callable],
        event_handlers: dict[Type[events.Event], list[Callable]],
    ):
        self.command_handlers = command_handlers
        self.event_handlers = event_handlers

    def handle(self, message: Message):
        """
        Evalutes the message and if a command, calls the handle_command method, else if
        an event, calls the handle_event method.
        """
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, events.Event):
                logger.info(f"handling event {message}")
                self.handle_event(message)
            elif isinstance(message, commands.Command):
                logger.info(f"handler: handling command {message}")
                self.handle_command(message)
            else:
                raise Exception(f"{message} was not an Event or Command")

    def handle_command(self, command: commands.Command):
        """
        Commands capture intent. They express our wish for the system to do something.
        As a result, when they fail, the sender needs to receive error information.

        Named - Imperative mood
        Error handling - fail noisily
        Sent to - one recipient
        """
        logger.info(f"handle_command: handling command {command}")
        try:
            handler = self.command_handlers[type(command)]
            handler(command)
            # self.queue.extend(self.uow.collect_new_events())
        except Exception:
            logger.exception(f"Exception handling command {command}")
            raise

    def handle_event(self, event):
        """
        Events are broadcast by an actor to all interested listeners.

        Named - Past tense
        Error handling - fail independently
        Sent to - All listeners
        """
        for handler in self.event_handlers[type(event)]:
            try:
                logger.info(f"handle_event {event} with handler {handler}")
                handler(event)
                # self.queue.extend(self.uow.collect_new_events())
            except Exception:
                logger.exception("Exception handling event %s", event)
                continue
