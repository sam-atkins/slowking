"""
Notification adapters. More a placeholder than anything else, just logs right now but
could be extended to send emails, Slack messages, etc.
"""
import abc
import logging.config

from src.domain import events

logger = logging.getLogger(__name__)


class AbstractNotifications(abc.ABC):
    @abc.abstractmethod
    def send(self, event: events.Event, message: str):
        raise NotImplementedError


class LogNotifications(AbstractNotifications):
    def send(self, event: events.Event, message: str):
        logger.warning(
            f"Sending notification for event {event} with message: {message}"
        )
