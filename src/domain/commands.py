"""
Domain Commands
"""
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from pydantic import SecretStr


class CommandChannelEnum(StrEnum):
    CREATE_CUSTOMER = "create_customer"
    CREATE_BENCHMARK = "create_benchmark"

    @classmethod
    def get_command_channels(cls):
        return [channel.value for channel in list(cls)]


class Command:
    pass


# TODO can we make these pydantic basemodels instead? need to convert when publishing
@dataclass
class CreateBenchmark(Command):
    channel: Literal[CommandChannelEnum.CREATE_BENCHMARK]
    name: str
    benchmark_type: str
    target_infra: str
    target_url: str
    target_release_version: str
    username: str
    # password: str  # TODO: make this a secret str?
    password: SecretStr


@dataclass
class CreateCustomer(Command):
    channel: Literal[CommandChannelEnum.CREATE_CUSTOMER]
    first_name: str
    surname: str
