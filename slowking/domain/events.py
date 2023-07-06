"""
Domain Events
"""
from enum import StrEnum
from typing import Literal, Self, Type

from pydantic import BaseModel, SecretStr


class EventChannelEnum(StrEnum):
    ALL_DOCUMENTS_UPLOADED = "all_documents_uploaded"
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
    target_eigen_platform_version: str
    username: str
    # Use .get_secret_value() method to see the secret's content
    password: SecretStr


class DocumentUpdated(Event):
    channel: Literal[EventChannelEnum.DOCUMENT_UPDATED]
    benchmark_id: int
    document_id: int  # NOTE this is the eigen document id
    document_name: str
    eigen_project_id: int


class ProjectCreated(Event):
    channel: Literal[EventChannelEnum.PROJECT_CREATED]
    eigen_project_id: int
    password: SecretStr
    target_url: str
    username: str


class AllDocumentsUploaded(Event):
    channel: Literal[EventChannelEnum.ALL_DOCUMENTS_UPLOADED]
    benchmark_id: int


EVENT_MAPPER = {
    EventChannelEnum.ALL_DOCUMENTS_UPLOADED.value: AllDocumentsUploaded,
    EventChannelEnum.BENCHMARK_CREATED.value: BenchmarkCreated,
    EventChannelEnum.PROJECT_CREATED.value: ProjectCreated,
    EventChannelEnum.DOCUMENT_UPDATED.value: DocumentUpdated,
}  # type: dict[str, Type[Event]]
