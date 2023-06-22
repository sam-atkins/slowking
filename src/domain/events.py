"""
Domain Events
"""
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal


class EventChannelEnum(StrEnum):
    CREATED_CUSTOMER = "created_customer"
    GREETED_CUSTOMER = "greeted_customer"

    @classmethod
    def get_event_channels(cls):
        return [channel.value for channel in list(cls)]


class Event:
    pass


@dataclass
class CustomerCreated(Event):
    channel: Literal[EventChannelEnum.CREATED_CUSTOMER]
    first_name: str
    surname: str


@dataclass
class CustomerGreeted(Event):
    channel: Literal[EventChannelEnum.GREETED_CUSTOMER]
    first_name: str
    surname: str
