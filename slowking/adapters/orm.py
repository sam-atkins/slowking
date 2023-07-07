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

from slowking.domain import model

metadata = MetaData()
mapper_registry = registry()

logger = logging.getLogger(__name__)

benchmark = Table(
    "benchmark",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255)),
    Column("benchmark_type", String(255)),
    Column("eigen_platform_version", String(255)),
    Column("target_infra", String(255)),
    Column("target_url", String(255)),
    Column("password", String(255)),
    Column("username", String(255)),
)


project = Table(
    "project",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("benchmark_id", ForeignKey("benchmark.id")),
    Column("name", String(255)),
    Column("eigen_project_id", Integer(), nullable=True),
)

document = Table(
    "document",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("project_id", ForeignKey("project.id")),
    Column("name", String(255)),
    Column("file_path", String(255)),
    Column("eigen_document_id", Integer(), nullable=True),
    Column("upload_time_start", DateTime()),
    Column("upload_time_end", DateTime()),
)


def start_mappers():
    logger.info("Starting ORM mappers...")
    document_mapper = mapper_registry.map_imperatively(model.Document, document)
    project_mapper = mapper_registry.map_imperatively(
        model.Project,
        project,
        properties={
            "document": relationship(document_mapper),
        },
    )
    mapper_registry.map_imperatively(
        model.Benchmark,
        benchmark,
        properties={
            "project": relationship(
                project_mapper,
                uselist=False,
            ),
        },
    )
    logger.info("ORM mapping complete.")
