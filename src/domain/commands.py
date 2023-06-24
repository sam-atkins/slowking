"""
Domain Commands
"""
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, SecretStr


class CommandChannelEnum(StrEnum):
    CREATE_CUSTOMER = "create_customer"
    CREATE_BENCHMARK = "create_benchmark"

    @classmethod
    def get_command_channels(cls):
        return [channel.value for channel in list(cls)]


class Command(BaseModel):
    pass


class CreateBenchmark(Command):
    channel: Literal[CommandChannelEnum.CREATE_BENCHMARK]
    name: str
    benchmark_type: str
    target_infra: str
    target_url: str
    target_release_version: str
    username: str
    password: SecretStr
