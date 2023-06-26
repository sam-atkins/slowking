"""
Benchmarking domain entities
"""
from __future__ import annotations

from datetime import datetime
from typing import NewType, Optional

TimeStamp = NewType("TimeStamp", datetime)


class Benchmark:
    def __init__(
        self,
        name,
        benchmark_type: str,
        release_version: str,
        target_instance: TargetInstance,
        project: Optional[Project],
        version_number: int = 0,
    ):
        self.name = name
        self.benchmark_type = benchmark_type
        self.release_version = release_version
        self.version_number = version_number
        self.target_instance = target_instance
        # artifacts (documents etc) - get from config? or hard code in the handler?
        self.project = project

    def __repr__(self):
        return f"<Benchmark {self.name}>"

    # ?
    def __eq__(self, other):
        if not isinstance(other, Benchmark):
            return NotImplemented
        return self.name == other.name and self.version_number == other.version_number

    def __hash__(self):
        return hash((self.name, self.version_number))


class TargetInstance:
    def __init__(
        self,
        target_infra: str,
        target_url: str,
        username: str,
        password: str,
    ):
        self.target_infra = target_infra
        self.target_url = target_url
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<TargetInstance {self.target_url}>"


class Project:
    def __init__(
        self, name: str, documents: list[Document], eigen_project_id: str = ""
    ):
        self.name = name
        self.documents = documents
        self.eigen_project_id = eigen_project_id

    def __repr__(self):
        return f"<Project {self.name}>"


class Document:
    upload_time_start: TimeStamp
    upload_time_end: TimeStamp

    def __init__(
        self,
        name: str,
        file_path: str,
        document_id: str = "",
        eigen_project_id: str = "",
    ):
        self.name = name
        self.file_path = file_path
        self.document_id = document_id
        self.eigen_project_id = eigen_project_id
        # self.version_number = version_number: int = 0,  # ?

    def __repr__(self):
        return f"<Document {self.name}>"

    # TODO is this method needed?
    # use uow to read the benchmark.project.documents and find documents.get(name) ?
    # document = benchmark.project.documents.get(name)
    # document.upload_time_start = datetime.now()  # timestamp provided by the client
    # def update(self):
    #     """
    #     Placeholder method to update a document
    #     """
    #     pass

    @property
    def upload_time(self):
        if not self.upload_time_start and not self.upload_time_end:
            return None
        return self.upload_time_end - self.upload_time_start
