"""
Change document column name to eigen_document_id

Revision ID: e721ff10752f
Revises:
Create Date: 2023-07-06 17:41:41.755847
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e721ff10752f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        column_name="document_id",
        table_name="document",
        new_column_name="eigen_document_id",
        existing_type=sa.Integer(),
    )


def downgrade() -> None:
    op.alter_column(
        column_name="eigen_document_id",
        table_name="document",
        new_column_name="document_id",
        existing_type=sa.Integer(),
    )
