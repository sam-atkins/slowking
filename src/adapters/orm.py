"""
ORM module
"""
import logging.config

import sqlalchemy as db
from sqlalchemy.orm import registry, relationship

from src.domain import model

metadata = db.MetaData()
mapper_registry = registry()

logger = logging.getLogger(__name__)

benchmarks = db.Table(
    "benchmarks",
    metadata,
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column("name", db.String(255)),
    db.Column("benchmark_type", db.String(255)),
)


target_instances = db.Table(
    "target_instances",
    metadata,
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column("benchmark_id", db.ForeignKey("benchmarks.id")),
    db.Column("target_infra", db.String(255)),
    db.Column("target_url", db.String(255)),
    db.Column("username", db.String(255)),
    db.Column("password", db.String(255)),
)

projects = db.Table(
    "projects",
    metadata,
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column("benchmark_id", db.ForeignKey("benchmarks.id")),
    db.Column("name", db.String(255)),
    db.Column("eigen_project_id", db.Integer()),
)

documents = db.Table(
    "documents",
    metadata,
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column("project_id", db.ForeignKey("projects.id")),
    db.Column("name", db.String(255)),
    db.Column("file_path", db.String(255)),
    db.Column("document_id", db.Integer()),
    db.Column("upload_time_start", db.DateTime()),
    db.Column("upload_time_end", db.DateTime()),
)

# FIXME FK constraint between target_instances and projects


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
