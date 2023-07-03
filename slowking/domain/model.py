"""
Benchmarking domain entities
"""
from __future__ import annotations

from datetime import datetime
from typing import NewType

TimeStamp = NewType("TimeStamp", datetime)


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
        release_version: str,
        target_infra: str,
        target_url: str,
        username: str,
        password: str,
        project: Project,
        version_number: int = 0,
    ):
        self.name = name
        self.benchmark_type = benchmark_type
        self.release_version = release_version
        self.version_number = version_number
        self.target_infra = target_infra
        self.target_url = target_url
        self.username = username
        self.password = password
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


class Project:
    def __init__(
        self,
        name: str,
        documents: list[Document] = [],
        eigen_project_id: int | None = None,
    ):
        self.name = name
        self.documents = documents
        # need a count of the docs. include here? or get len(documents)?
        # artifact?
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
        eigen_document_id: str = "",
        eigen_project_id: str = "",
    ):
        self.name = name
        self.file_path = file_path
        self.eigen_document_id = eigen_document_id
        self.eigen_project_id = eigen_project_id
        # self.version_number = version_number: int = 0,  # ?

    def __repr__(self):
        return f"<Document {self.name}>"

    @property
    def upload_time(self):
        if not self.upload_time_start and not self.upload_time_end:
            return None
        return self.upload_time_end - self.upload_time_start
