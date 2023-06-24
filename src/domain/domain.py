"""
Benchmarking domain entities
"""
from __future__ import annotations

from typing import Optional


class Benchmark:
    def __init__(
        self,
        name,
        benchmark_type: str,
        target_instance: TargetInstance,
        project: Optional[Project],
        version_number: int = 0,
    ):
        self.name = name
        self.benchmark_type = benchmark_type
        self.version_number = version_number
        self.target_instance = target_instance
        # artifacts (documents) - get from config? or at least hard code for now
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

    def create(self):
        """
        Placeholder method to create a benchmark
        """
        self.version_number += 1
        pass

    def get(self):
        """
        Placeholder method to get a benchmark
        """
        pass

    def update(self):
        """
        Placeholder method to update a benchmark
        """
        pass

    def add_project(self, project: Project):
        """
        Placeholder method to add a project to a benchmark
        """
        # self.project = project.create()
        pass

    def update_project(self, project: Project):
        """
        Placeholder method to update a project to a benchmark
        """
        # self.project = project.update()
        pass


class TargetInstance:
    def __init__(
        self,
        target_infra: str,
        target_url: str,
        target_release_version: str,
        username: str,
        password: str,
    ):
        self.target_infra = target_infra
        self.target_url = target_url
        self.target_release_version = target_release_version
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<TargetInstance {self.target_url}>"

    def create(self):
        """
        Placeholder method to create a target instance
        """
        pass

    def update(self):
        """
        Placeholder method to update a target instance
        """
        pass


class Project:
    def __init__(self, name: str, description: str = "", project_id: str = ""):
        self.name = name
        self.description = description
        self.project_id = project_id

    def __repr__(self):
        return f"<Project {self.name}>"

    def create(self):
        """
        Placeholder method to create a project
        """
        pass

    def update(self):
        """
        Placeholder method to update a project
        """
        pass

    def add_documents(self, documents: list):
        """
        Placeholder method to add documents to a project
        """
        pass
