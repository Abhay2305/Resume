"""Add Gap Analysis Engine domain tables.

Creates:
  - gap_analyses: Main analysis record
  - gap_results: Individual category comparison results
  - recommendations: Deterministic recommendations

Revision: 004
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # gap_analyses
    op.create_table(
        "gap_analyses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("resume_profile_id", sa.String(36), sa.ForeignKey("resume_profiles.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("opportunity_id", sa.String(36), sa.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("overall_match_score", sa.Float, nullable=True),
        sa.Column("skill_match_score", sa.Float, nullable=True),
        sa.Column("technology_match_score", sa.Float, nullable=True),
        sa.Column("experience_match_score", sa.Float, nullable=True),
        sa.Column("education_match_score", sa.Float, nullable=True),
        sa.Column("certification_match_score", sa.Float, nullable=True),
        sa.Column("keyword_match_score", sa.Float, nullable=True),
        sa.Column("total_gaps", sa.Integer, nullable=True, server_default="0"),
        sa.Column("total_matches", sa.Integer, nullable=True, server_default="0"),
        sa.Column("total_recommendations", sa.Integer, nullable=True, server_default="0"),
        sa.Column("parser_version", sa.String(50), nullable=True, server_default="1.0"),
        sa.Column("processing_time_ms", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("user_id", "resume_profile_id", "opportunity_id", name="uq_gap_analysis_user_resume_opportunity"),
    )
    op.create_index("ix_gap_analyses_user_id", "gap_analyses", ["user_id"])
    op.create_index("ix_gap_analyses_status", "gap_analyses", ["status"])

    # gap_results
    op.create_table(
        "gap_results",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("gap_analysis_id", sa.String(36), sa.ForeignKey("gap_analyses.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("category", sa.String(50), nullable=False, index=True),
        sa.Column("match_score", sa.Float, nullable=True),
        sa.Column("matched_items", sa.Text, nullable=True),
        sa.Column("missing_items", sa.Text, nullable=True),
        sa.Column("partial_items", sa.Text, nullable=True),
        sa.Column("extra_items", sa.Text, nullable=True),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("gap_analysis_id", "category", name="uq_gap_result_analysis_category"),
    )
    op.create_index("ix_gap_results_category", "gap_results", ["category"])

    # recommendations
    op.create_table(
        "recommendations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("gap_analysis_id", sa.String(36), sa.ForeignKey("gap_analyses.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("category", sa.String(50), nullable=False, index=True),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("target_item", sa.String(255), nullable=True),
        sa.Column("is_applied", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_recommendations_priority", "recommendations", ["priority"])
    op.create_index("ix_recommendations_action", "recommendations", ["action"])


def downgrade() -> None:
    op.drop_table("recommendations")
    op.drop_table("gap_results")
    op.drop_table("gap_analyses")
