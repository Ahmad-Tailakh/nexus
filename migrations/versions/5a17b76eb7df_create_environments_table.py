"""create environments table

Revision ID: 5a17b76eb7df
Revises: 24313238392f
Create Date: 2026-10-12 10:18:56.744288
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5a17b76eb7df"
down_revision: Union[str, Sequence[str], None] = "24313238392f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the environments table."""
    op.create_table(
        "environments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "name",
            name="uq_environments_project_id_name",
        ),
    )


def downgrade() -> None:
    """Drop the environments table."""
    op.drop_table("environments")