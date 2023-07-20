"""
Add project column for all_docs_uploaded

Revision ID: 3bd51d191df3
Revises: 3c0b00800302
Create Date: 2023-07-20 09:35:19.596548
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3bd51d191df3"
down_revision = "3c0b00800302"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        table_name="project",
        column=sa.Column("all_docs_uploaded", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column(table_name="project", column_name="all_docs_uploaded")
