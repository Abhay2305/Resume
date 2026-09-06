"""Add source_section column to knowledge_rules.

Adds the missing provenance column referenced by ProvenanceTracker
but not present in the original KnowledgeRule model.

Revision: 007
"""
from alembic import op
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "knowledge_rules",
        sa.Column("source_section", sa.String(100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("knowledge_rules", "source_section")
