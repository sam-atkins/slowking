"""
Domain Commands
"""
from enum import StrEnum
from typing import Literal, Self, Type

from pydantic import BaseModel, SecretStr


class CommandChannelEnum(StrEnum):
    CREATE_BENCHMARK = "create_benchmark"
    UPDATE_DOCUMENT = "update_document"

    @classmethod
    def get_command_channels(cls: Type[Self]) -> list[str]:
        return [channel.value for channel in list(cls)]


class Command(BaseModel):
    pass


class CreateBenchmark(Command):
    channel: Literal[CommandChannelEnum.CREATE_BENCHMARK]
    name: str
    benchmark_type: str
    target_infra: str
    target_url: str
    target_eigen_platform_version: str
    username: str
    password: SecretStr


class UpdateDocument(Command):
    channel: Literal[CommandChannelEnum.UPDATE_DOCUMENT]
    document_name: str
    eigen_document_id: str
    eigen_project_id: str
    benchmark_host_name: str  # TODO the same as target_url, rename?
    end_time: float | None
    start_time: float | None
