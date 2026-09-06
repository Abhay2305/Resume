"""Prompt Version Service.

Tracks prompt evolution with version history.
"""
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.prompt_intelligence import PromptTemplate, PromptVersion
from app.repositories.prompt_intelligence import PromptVersionRepository


class PromptVersionService:
    """Service for prompt versioning."""

    def __init__(self, db: Session):
        self.db = db
        self.version_repo = PromptVersionRepository(db)

    def create_version(
        self,
        template_id: str,
        system_prompt: str,
        template_version: str = "1.0",
        rules_version: str = "1.0",
        knowledge_version: str = "1.0",
        changes: Optional[str] = None,
    ) -> PromptVersion:
        latest = self.version_repo.get_latest(template_id)
        if latest:
            parts = latest.version.split(".")
            major = int(parts[0]) if parts[0].isdigit() else 1
            minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            new_version = f"{major}.{minor + 1}"
        else:
            new_version = "1.0"

        prompt_hash = hashlib.sha256(system_prompt.encode()).hexdigest()[:16]

        return self.version_repo.create({
            "template_id": template_id,
            "version": new_version,
            "system_prompt_hash": prompt_hash,
            "template_version": template_version,
            "rules_version": rules_version,
            "knowledge_version": knowledge_version,
            "changes": changes,
            "is_active": True,
        })

    def get_versions(self, template_id: str) -> List[PromptVersion]:
        return self.version_repo.get_by_template_id(template_id)

    def get_latest_version(self, template_id: str) -> Optional[PromptVersion]:
        return self.version_repo.get_latest(template_id)

    def get_version(self, template_id: str, version: str) -> Optional[PromptVersion]:
        return self.version_repo.get_by_version(template_id, version)
