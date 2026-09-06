"""Add provenance, state, and version columns to knowledge_rules.

The original migration (005) created knowledge_rules without the
provenance tracking, governance state, and versioning columns.
This migration adds them to match the KnowledgeRule model.

Revision: 006
"""
from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add provenance columns
    op.add_column("knowledge_rules", sa.Column("source_document", sa.String(255), nullable=True))
    op.add_column("knowledge_rules", sa.Column("source_page", sa.Integer, nullable=True))
    op.add_column("knowledge_rules", sa.Column("source_evidence", sa.Text, nullable=True))
    op.add_column("knowledge_rules", sa.Column("extraction_confidence", sa.Float, nullable=True))
    op.add_column("knowledge_rules", sa.Column("extraction_timestamp", sa.String(30), nullable=True))
    op.add_column("knowledge_rules", sa.Column("rule_hash", sa.String(64), nullable=True))

    # Add governance state and versioning columns
    op.add_column("knowledge_rules", sa.Column("state", sa.String(20), nullable=False, server_default="ACTIVE"))
    op.add_column("knowledge_rules", sa.Column("version", sa.Integer, nullable=False, server_default="1"))

    # Add index for rule_hash
    op.create_index("ix_knowledge_rules_hash", "knowledge_rules", ["rule_hash"])

    # Add index for state
    op.create_index("ix_knowledge_rules_state", "knowledge_rules", ["state"])


def downgrade() -> None:
    op.drop_index("ix_knowledge_rules_state", table_name="knowledge_rules")
    op.drop_index("ix_knowledge_rules_hash", table_name="knowledge_rules")
    op.drop_column("knowledge_rules", "version")
    op.drop_column("knowledge_rules", "state")
    op.drop_column("knowledge_rules", "rule_hash")
    op.drop_column("knowledge_rules", "extraction_timestamp")
    op.drop_column("knowledge_rules", "extraction_confidence")
    op.drop_column("knowledge_rules", "source_evidence")
    op.drop_column("knowledge_rules", "source_page")
    op.drop_column("knowledge_rules", "source_document")
