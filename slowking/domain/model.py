"""
Benchmarking domain entities
"""
from __future__ import annotations

from datetime import datetime
from typing import Type

from slowking.domain import commands, events
from slowking.domain.exceptions import MessageNotAssignedToBenchmarkError


class Benchmark:
    """
    The Benchmark domain entity represents a benchmarking run. It is an aggregate.

    An aggregate is a domain object that contains other domain objects and lets us treat
    the whole collection as a single unit. The only way to modify the objects inside the
    aggregate is to load the whole thing, and to call methods on the aggregate itself.

    The Benchmark entity contains the following entities:
        - Project
            - Document
    """

    id: int

    def __init__(
        self,
        name: str,
        benchmark_type: str,
        eigen_platform_version: str,
        target_infra: str,
        target_url: str,
        username: str,
        password: str,
        project: Project,
    ):
        self.name = name
        self.benchmark_type = benchmark_type
        self.eigen_platform_version = eigen_platform_version
        self.target_infra = target_infra
        self.target_url = target_url
        self.username = username
        self.password = password
        self.project = project

    def __repr__(self):
        return f"<Benchmark {self.name}>"


class Project:
    def __init__(
        self,
        name: str,
        document: list[Document] = [],
        eigen_project_id: int | None = None,
    ):
        self.name = name
        self.document = document
        self.eigen_project_id = eigen_project_id

    def __repr__(self):
        return f"<Project {self.name}>"


class Document:
    upload_time_start: datetime
    upload_time_end: datetime

    def __init__(
        self,
        name: str,
        file_path: str,
        eigen_document_id: int | None = None,
    ):
        self.name = name
        self.file_path = file_path
        self.eigen_document_id = eigen_document_id

    def __repr__(self):
        return f"<Document {self.name}>"

    @property
    def upload_time(self):
        """Calculate the upload time of the document"""
        if self.upload_time_start is None or self.upload_time_end is None:
            return None
        upload_time = self.upload_time_end - self.upload_time_start
        return upload_time.total_seconds()


class BenchmarkType:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"<BenchmarkType {self.name}>"


class LatencyBenchmark(BenchmarkType):
    message_queue: list[Type[events.Event] | Type[commands.Command]] = [
        events.BenchmarkCreated,
        events.ProjectCreated,
        commands.UpdateDocument,
        events.DocumentUpdated,
        events.AllDocumentsUploaded,
    ]

    def get_next_message(
        self, current_message: Type[events.Event] | Type[commands.Command]
    ):
        try:
            return self.message_queue[self.message_queue.index(current_message) + 1]
        except IndexError:
            return None
        except ValueError:
            raise MessageNotAssignedToBenchmarkError(
                f"{current_message} is not in LatencyBenchmark"
            )
