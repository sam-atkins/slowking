"""
ORM module
"""
import logging.config

import sqlalchemy as sa
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import registry, relationship

from slowking.domain import model

metadata = sa.MetaData()
mapper_registry = registry()

logger = logging.getLogger(__name__)

benchmark = sa.Table(
    "benchmark",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("benchmark_type", sa.String(255)),
    sa.Column("_benchmark_type", sa.String(255)),
    sa.Column("eigen_platform_version", sa.String(255)),
    sa.Column("target_infra", sa.String(255)),
    sa.Column("target_url", sa.String(255)),
    sa.Column("password", sa.String(255)),
    sa.Column("username", sa.String(255)),
)


project = sa.Table(
    "project",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("benchmark_id", sa.Integer, sa.ForeignKey("benchmark.id")),
    sa.Column("name", sa.String(255)),
    sa.Column("eigen_project_id", sa.Integer(), nullable=True),
    sa.Column("all_docs_uploaded", sa.DateTime(), nullable=True),
)

document = sa.Table(
    "document",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("project_id", sa.Integer, sa.ForeignKey("project.id")),
    sa.Column("name", sa.String(255)),
    sa.Column("file_path", sa.String(255)),
    sa.Column("eigen_document_id", sa.Integer(), nullable=True),
    sa.Column("upload_time_start", sa.DateTime(), nullable=True),
    sa.Column("upload_time_end", sa.DateTime(), nullable=True),
)


def start_mappers():
    logger.info("Starting ORM mappers...")
    # NOTE: calling bootstrap.bootstrap() will call this function
    # and would raise an error if the mapping is already complete
    # Both the API and the Event Handler call bootstrap.bootstrap()
    # so for now (until a more refined approach is in place) we catch
    # the exception and move on.
    try:
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
    except ArgumentError:
        pass
