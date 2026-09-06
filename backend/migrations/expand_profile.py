"""Migration: Expand profiles table with resume sections.

Usage:
    python -m migrations.expand_profile
"""
import os
import sys

from sqlalchemy import Column, Text, String, Boolean

from .utils import add_column, create_index_if_not_exists, get_engine


def migrate() -> None:
    """Expand profiles table with resume section columns."""
    print("Expanding profiles table with resume sections...")
    print("=" * 60)

    engine = get_engine()

    columns = [
        Column("date_of_birth", String(20), nullable=True),
        Column("professional_headline", String(255), nullable=True),
        Column("portfolio", String(512), nullable=True),
        Column("other_links", Text, nullable=True),
        Column("education_json", Text, nullable=True),
        Column("experience_json", Text, nullable=True),
        Column("projects_json", Text, nullable=True),
        Column("skills_json", Text, nullable=True),
        Column("certifications_json", Text, nullable=True),
        Column("achievements_json", Text, nullable=True),
        Column("languages_json", Text, nullable=True),
        Column("interests_json", Text, nullable=True),
        Column("awards_json", Text, nullable=True),
        Column("publications_json", Text, nullable=True),
        Column("volunteer_json", Text, nullable=True),
        Column("extracurricular_json", Text, nullable=True),
    ]

    for col in columns:
        add_column(engine, "profiles", col)

    # Add profile_completed with default value for existing rows
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE profiles ADD COLUMN profile_completed BOOLEAN DEFAULT FALSE"))
        conn.commit()
    print("  Added column profiles.profile_completed")

    print("\nDone!")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    migrate()
