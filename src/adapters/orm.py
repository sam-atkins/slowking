"""
ORM module
"""
import logging.config

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.orm import registry, relationship

from src.domain import model

metadata = MetaData()
mapper_registry = registry()

logger = logging.getLogger(__name__)

benchmarks = Table(
    "benchmarks",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255)),
    Column("benchmark_type", String(255)),
)


target_instances = Table(
    "target_instances",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("benchmark_id", ForeignKey("benchmarks.id")),
    Column("target_infra", String(255)),
    Column("target_url", String(255)),
    Column("username", String(255)),
    Column("password", String(255)),
)

projects = Table(
    "projects",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("benchmark_id", ForeignKey("benchmarks.id")),
    Column("target_instance_id", ForeignKey("target_instances.id")),
    Column("name", String(255)),
    Column("eigen_project_id", Integer(), nullable=True),
)

documents = Table(
    "documents",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("project_id", ForeignKey("projects.id")),
    Column("name", String(255)),
    Column("file_path", String(255)),
    Column("document_id", Integer()),
    Column("upload_time_start", DateTime()),
    Column("upload_time_end", DateTime()),
)


def start_mappers():
    logger.info("Starting ORM mappers...")
    documents_mapper = mapper_registry.map_imperatively(model.Document, documents)
    project_mapper = mapper_registry.map_imperatively(
        model.Project,
        projects,
        properties={
            "documents": relationship(documents_mapper),
        },
    )
    mapper_registry.map_imperatively(
        model.TargetInstance,
        target_instances,
    )

    mapper_registry.map_imperatively(
        model.Benchmark,
        benchmarks,
        properties={
            "projects": relationship(project_mapper, secondary=target_instances)
        },
    )
    logger.info("ORM mapping complete.")
