"""
Domain Events
"""
import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Self, Type


class EventChannelEnum(StrEnum):
    ALL_DOCUMENTS_UPLOADED = "all_documents_uploaded"
    BENCHMARK_CREATED = "benchmark_created"
    DOCUMENT_UPDATED = "document_updated"
    PROJECT_CREATED = "project_created"

    @classmethod
    def get_event_channels(cls: Type[Self]) -> list[str]:
        return [channel.value for channel in list(cls)]


@dataclass
class Event:
    benchmark_id: int
    channel: str = ""

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict())


@dataclass
class BenchmarkCreated(Event):
    benchmark_id: int
    channel: str = EventChannelEnum.BENCHMARK_CREATED.value


@dataclass
class DocumentUpdated(Event):
    benchmark_id: int
    channel: str = EventChannelEnum.DOCUMENT_UPDATED.value


@dataclass
class ProjectCreated(Event):
    benchmark_id: int
    channel: str = EventChannelEnum.PROJECT_CREATED.value


@dataclass
class AllDocumentsUploaded(Event):
    benchmark_id: int
    channel: str = EventChannelEnum.ALL_DOCUMENTS_UPLOADED.value


@dataclass
class BenchmarkCompleted(Event):
    pass


@dataclass
class NoOp(Event):
    """
    Used when no more events are fired e.g. system is waiting for an external
    command
    """

    pass


EVENT_MAPPER: dict[str, Type[Event]] = {
    EventChannelEnum.ALL_DOCUMENTS_UPLOADED.value: AllDocumentsUploaded,
    EventChannelEnum.BENCHMARK_CREATED.value: BenchmarkCreated,
    EventChannelEnum.PROJECT_CREATED.value: ProjectCreated,
    EventChannelEnum.DOCUMENT_UPDATED.value: DocumentUpdated,
}
