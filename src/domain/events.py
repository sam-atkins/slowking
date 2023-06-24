"""
Domain Events
"""
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class EventChannelEnum(StrEnum):
    CREATED_CUSTOMER = "created_customer"
    GREETED_CUSTOMER = "greeted_customer"

    @classmethod
    def get_event_channels(cls):
        return [channel.value for channel in list(cls)]


class Event(BaseModel):
    pass


class CustomerCreated(Event):
    channel: Literal[EventChannelEnum.CREATED_CUSTOMER]
    first_name: str
    surname: str


class CustomerGreeted(Event):
    channel: Literal[EventChannelEnum.GREETED_CUSTOMER]
    first_name: str
    surname: str
