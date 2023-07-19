"""
Domain Commands
"""
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, Self, Type


class CommandChannelEnum(StrEnum):
    CREATE_BENCHMARK = "create_benchmark"
    UPDATE_DOCUMENT = "update_document"

    @classmethod
    def get_command_channels(cls: Type[Self]) -> list[str]:
        return [channel.value for channel in list(cls)]


@dataclass
class Command:
    pass


@dataclass
class CreateBenchmark(Command):
    channel: Literal[CommandChannelEnum.CREATE_BENCHMARK]
    name: str
    benchmark_type: str
    target_infra: str
    target_url: str
    target_eigen_platform_version: str
    username: str
    password: str


@dataclass
class UpdateDocument(Command):
    channel: Literal[CommandChannelEnum.UPDATE_DOCUMENT]
    document_name: str
    eigen_document_id: str
    eigen_project_id: str
    benchmark_host_name: str  # TODO the same as target_url, rename?
    end_time: float | None
    start_time: float | None
