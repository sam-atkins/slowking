"""
Benchmarking domain entities
"""
from __future__ import annotations

from datetime import datetime


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
        # need a count of the docs. include here? or get len(documents)?
        # artifact?
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
        upload_time = self.upload_time_end - self.upload_time_start
        return upload_time.total_seconds()
