"""
Domain Events
"""
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, SecretStr


class EventChannelEnum(StrEnum):
    BENCHMARK_CREATED = "benchmark_created"
    PROJECT_CREATED = "project_created"

    @classmethod
    def get_event_channels(cls):
        return [channel.value for channel in list(cls)]


class Event(BaseModel):
    pass


class BenchmarkCreated(Event):
    channel: Literal[EventChannelEnum.BENCHMARK_CREATED]
    name: str
    benchmark_type: str
    target_infra: str
    target_url: str
    target_release_version: str
    username: str
    # password: SecretStr  # FIXME: Object of type SecretStr is not JSON serializable
    password: str


class ProjectCreated(Event):
    channel: Literal[EventChannelEnum.PROJECT_CREATED]
    target_url: str
    project_id: str  # or int?
