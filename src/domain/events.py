"""
Domain Events
"""
from enum import StrEnum
from typing import Literal, Self, Type

from pydantic import BaseModel


class EventChannelEnum(StrEnum):
    BENCHMARK_CREATED = "benchmark_created"
    DOCUMENT_UPDATED = "document_updated"
    PROJECT_CREATED = "project_created"

    @classmethod
    def get_event_channels(cls: Type[Self]) -> list[str]:
        return [channel.value for channel in list(cls)]


class Event(BaseModel):
    channel: str


class BenchmarkCreated(Event):
    channel: Literal[EventChannelEnum.BENCHMARK_CREATED]
    benchmark_id: int
    name: str
    benchmark_type: str
    target_infra: str
    target_url: str
    target_release_version: str
    username: str
    # Use .get_secret_value() method to see the secret's content
    # password: SecretStr
    password: str


class DocumentUpdated(Event):
    channel: Literal[EventChannelEnum.DOCUMENT_UPDATED]
    document_id: int
    document_name: str
    eigen_document_id: str
    eigen_project_id: str
    end_time: str | None  # TODO: change to datetime
    start_time: str | None  # TODO: change to datetime


class ProjectCreated(Event):
    channel: Literal[EventChannelEnum.PROJECT_CREATED]
    target_url: str
    project_id: int
