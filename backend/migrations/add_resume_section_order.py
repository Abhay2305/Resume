"""Add section_order column to resumes for section ordering persistence.

Revision: 008
Down revision: 007
"""
from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("resumes", sa.Column("section_order", sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_column("resumes", "section_order")
