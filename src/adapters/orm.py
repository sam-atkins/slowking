"""
ORM module
"""
import sqlalchemy as db
from sqlalchemy.orm import registry, relationship

from src.domain import model

metadata = db.MetaData()
mapper_registry = registry()


benchmark = db.Table(
    "benchmark",
    metadata,
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column("name", db.String(255)),
    db.Column("benchmark_type", db.String(255)),
)


target_instance = db.Table(
    "target_instance",
    metadata,
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column("benchmark_id", db.ForeignKey("benchmark.id")),
    db.Column("target_infra", db.String(255)),
    db.Column("target_url", db.String(255)),
    db.Column("username", db.String(255)),
    db.Column("password", db.String(255)),
)

project = db.Table(
    "project",
    metadata,
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column("benchmark_id", db.ForeignKey("benchmark.id")),
    db.Column("name", db.String(255)),
    db.Column("eigen_project_id", db.Integer()),
)

documents = db.Table(
    "documents",
    metadata,
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column("project_id", db.ForeignKey("project.id")),
    db.Column("name", db.String(255)),
    db.Column("file_path", db.String(255)),
    db.Column("document_id", db.Integer()),
    db.Column("upload_time_start", db.DateTime()),
    db.Column("upload_time_end", db.DateTime()),
)


def start_mappers():
    benchmark_mapper = mapper_registry.map_imperatively(
        model.Benchmark,
        benchmark,
        # TODO needed?
        # properties={
        #     "target_instance": relationship(
        #         target_instance,
        #         collection_class=set,
        #     ),
        #     "project": relationship(
        #         project,
        #         collection_class=set,
        #     ),
        # },
    )
    mapper_registry.map_imperatively(
        model.TargetInstance,
        target_instance,
        properties={
            "benchmark": relationship(
                benchmark_mapper,
                collection_class=set,
            )
        },
    )
    project_mapper = mapper_registry.map_imperatively(
        model.Project,
        project,
        properties={
            "benchmark": relationship(
                benchmark_mapper,
                collection_class=set,
            ),
            "documents": relationship(
                documents,
                collection_class=set,
            ),
        },
    )
    mapper_registry.map_imperatively(
        model.Document,
        documents,
        properties={
            "project": relationship(
                project_mapper,
                collection_class=set,
            )
        },
    )
