"""
Benchmarking domain entities
"""
from __future__ import annotations

import logging.config
from datetime import datetime

from slowking.domain.benchmarks import BenchmarkTypesEnum
from slowking.domain.exceptions import (
    InvalidBenchmarkTypeError,
)

logger = logging.getLogger(__name__)


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
    _benchmark_type: str

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

    @property
    def benchmark_type(self):
        return self._benchmark_type

    @benchmark_type.setter
    def benchmark_type(self, benchmark_type: str):
        """
        Validate the benchmark type
        """
        valid_benchmark_types = BenchmarkTypesEnum.get_benchmark_types()
        if benchmark_type not in valid_benchmark_types:
            msg = f"Invalid benchmark type: {benchmark_type}. Valid benchmark types are: {valid_benchmark_types}"  # noqa: E501
            raise InvalidBenchmarkTypeError(msg)

        self._benchmark_type = benchmark_type


class Project:
    def __init__(
        self,
        name: str,
        document: list[Document] = [],
        eigen_project_id: int = None,  # type: ignore
        all_docs_uploaded: datetime | None = None,
    ):
        self.name = name
        self.document = document
        self.eigen_project_id = eigen_project_id
        self.all_docs_uploaded = all_docs_uploaded

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
