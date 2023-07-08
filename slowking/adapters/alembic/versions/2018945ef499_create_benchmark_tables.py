"""
create benchmark tables

Revision ID: 2018945ef499
Revises: e721ff10752f
Create Date: 2023-07-07 09:21:52.581585
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2018945ef499"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "benchmark",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("benchmark_type", sa.String(255)),
        sa.Column("eigen_platform_version", sa.String(255)),
        sa.Column("target_infra", sa.String(255)),
        sa.Column("target_url", sa.String(255)),
        sa.Column("password", sa.String(255)),
        sa.Column("username", sa.String(255)),
    )
    op.create_table(
        "project",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("benchmark_id", sa.Integer, sa.ForeignKey("benchmark.id")),
        sa.Column("name", sa.String(255)),
        sa.Column("eigen_project_id", sa.Integer(), nullable=True),
    )
    op.create_table(
        "document",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("project.id")),
        sa.Column("name", sa.String(255)),
        sa.Column("file_path", sa.String(255)),
        sa.Column("document_id", sa.Integer(), nullable=True),
        sa.Column("upload_time_start", sa.DateTime(), nullable=True),
        sa.Column("upload_time_end", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("benchmark")
    op.drop_table("project")
    op.drop_table("document")
