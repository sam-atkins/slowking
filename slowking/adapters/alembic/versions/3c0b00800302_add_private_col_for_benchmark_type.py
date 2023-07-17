"""
Add private col for benchmark_type

Revision ID: 3c0b00800302
Revises: 06c957226763
Create Date: 2023-07-17 14:39:18.703979
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3c0b00800302"
down_revision = "06c957226763"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        table_name="benchmark",
        column=sa.Column("_benchmark_type", sa.String(255)),
    )


def downgrade() -> None:
    op.drop_column(table_name="benchmark", column_name="_benchmark_type")
