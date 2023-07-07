"""
change document column name to eigen_document_id

Revision ID: 06c957226763
Revises: 2018945ef499
Create Date: 2023-07-07 09:23:44.784643
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "06c957226763"
down_revision = "2018945ef499"
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
