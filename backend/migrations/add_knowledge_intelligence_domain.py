"""Add Knowledge Intelligence Engine domain tables.

Creates:
  - knowledge_documents: Knowledge source metadata
  - knowledge_sections: Sections within documents
  - knowledge_rules: Structured knowledge rules
  - knowledge_retrievals: Retrieval records
  - knowledge_contexts: Structured knowledge contexts

Revision: 005
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # knowledge_documents
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("document_key", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("version", sa.String(20), nullable=False, server_default="1.0"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0.8"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("total_rules", sa.Integer, nullable=True, server_default="0"),
        sa.Column("total_sections", sa.Integer, nullable=True, server_default="0"),
        sa.Column("metadata_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_knowledge_documents_key", "knowledge_documents", ["document_key"])
    op.create_index("ix_knowledge_documents_source", "knowledge_documents", ["source"])
    op.create_index("ix_knowledge_documents_type", "knowledge_documents", ["document_type"])

    # knowledge_sections
    op.create_table(
        "knowledge_sections",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("section_key", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("content_summary", sa.Text, nullable=True),
        sa.Column("rule_count", sa.Integer, nullable=True, server_default="0"),
        sa.Column("sort_order", sa.Integer, nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("document_id", "section_key", name="uq_knowledge_section_doc_key"),
    )
    op.create_index("ix_knowledge_sections_category", "knowledge_sections", ["category"])

    # knowledge_rules
    op.create_table(
        "knowledge_rules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("section_id", sa.String(36), sa.ForeignKey("knowledge_sections.id", ondelete="SET NULL"), nullable=True),
        sa.Column("rule_key", sa.String(100), nullable=False, unique=True),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("section_name", sa.String(100), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("instruction", sa.Text, nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("examples", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0.8"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_knowledge_rules_key", "knowledge_rules", ["rule_key"])
    op.create_index("ix_knowledge_rules_priority", "knowledge_rules", ["priority"])
    op.create_index("ix_knowledge_rules_category", "knowledge_rules", ["category"])
    op.create_index("ix_knowledge_rules_section", "knowledge_rules", ["section_name"])

    # knowledge_retrievals
    op.create_table(
        "knowledge_retrievals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("gap_analysis_id", sa.String(36), sa.ForeignKey("gap_analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("total_rules_retrieved", sa.Integer, nullable=False, server_default="0"),
        sa.Column("retrieval_strategy", sa.String(50), nullable=False, server_default="category_match"),
        sa.Column("processing_time_ms", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_knowledge_retrievals_gap_analysis", "knowledge_retrievals", ["gap_analysis_id"])

    # knowledge_contexts
    op.create_table(
        "knowledge_contexts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("retrieval_id", sa.String(36), sa.ForeignKey("knowledge_retrievals.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("gap_analysis_id", sa.String(36), sa.ForeignKey("gap_analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("summary_rules", sa.Text, nullable=True),
        sa.Column("experience_rules", sa.Text, nullable=True),
        sa.Column("skills_rules", sa.Text, nullable=True),
        sa.Column("education_rules", sa.Text, nullable=True),
        sa.Column("projects_rules", sa.Text, nullable=True),
        sa.Column("certifications_rules", sa.Text, nullable=True),
        sa.Column("ats_rules", sa.Text, nullable=True),
        sa.Column("formatting_rules", sa.Text, nullable=True),
        sa.Column("cover_letter_rules", sa.Text, nullable=True),
        sa.Column("total_rules", sa.Integer, nullable=False, server_default="0"),
        sa.Column("citations", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_knowledge_contexts_gap_analysis", "knowledge_contexts", ["gap_analysis_id"])


def downgrade() -> None:
    op.drop_table("knowledge_contexts")
    op.drop_table("knowledge_retrievals")
    op.drop_table("knowledge_rules")
    op.drop_table("knowledge_sections")
    op.drop_table("knowledge_documents")
