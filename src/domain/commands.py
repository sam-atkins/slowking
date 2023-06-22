"""
Domain Commands
"""
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal


class CommandChannelEnum(StrEnum):
    CREATE_CUSTOMER = "create_customer"

    @classmethod
    def get_command_channels(cls):
        return [channel.value for channel in list(cls)]


class Command:
    pass


@dataclass
class CreateCustomer(Command):
    channel: Literal[CommandChannelEnum.CREATE_CUSTOMER]
    first_name: str
    surname: str
