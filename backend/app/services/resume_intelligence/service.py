"""Resume Intelligence Service.

Orchestrates the entire resume parsing pipeline:
Parser -> Normalizer -> Extractor -> Knowledge Builder -> Repository
"""
import time
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException

from app.models.resume_intelligence import ResumeProfile, ResumeProfileStatus
from app.repositories.resume_intelligence import (
    ParsedResumeDataRepository,
    ResumeEntityRepository,
    ResumeKnowledgeRepository,
    ResumeProfileRepository,
)
from app.schemas import (
    ResumeIntelligenceCreate,
    ResumeIntelligenceUpdate,
)
from app.services.audit_service import AuditService
from app.services.error_service import ErrorService
from app.services.resume_intelligence.extractors import ExtractorOrchestrator
from app.services.resume_intelligence.knowledge_builder import ResumeKnowledgeBuilder
from app.services.resume_intelligence.parsers.normalizer import ResumeNormalizer
from app.services.resume_intelligence.parsers.parser import ResumeParser


class ResumeIntelligenceService:
    """Service for managing resume profiles and orchestrating the parsing pipeline."""

    def __init__(self, db):
        self.db = db
        self.repo = ResumeProfileRepository(db)
        self.parsed_data_repo = ParsedResumeDataRepository(db)
        self.entities_repo = ResumeEntityRepository(db)
        self.knowledge_repo = ResumeKnowledgeRepository(db)
        self.parser = ResumeParser()
        self.normalizer = ResumeNormalizer()
        self.extractor = ExtractorOrchestrator()
        self.knowledge_builder = ResumeKnowledgeBuilder()
        self.audit = AuditService(db)
        self.error = ErrorService(db)

    def create_profile(self, user_id: str, data: ResumeIntelligenceCreate) -> ResumeProfile:
        """Create a new resume profile (without parsing)."""
        try:
            profile_data = {
                "user_id": user_id,
                "raw_text": data.raw_text,
                "title": data.title,
                "status": ResumeProfileStatus.PENDING.value,
            }
            profile = self.repo.create(profile_data)

            self.audit.log_create(
                user_id=user_id,
                entity_type="resume_profile",
                entity_id=profile.id,
                new_state={"status": profile.status, "title": profile.title},
            )

            return profile
        except Exception as e:
            self.error.log_exception(e, context={"user_id": user_id})
            raise HTTPException(status_code=500, detail=str(e))

    def get_profile(self, id: str, user_id: str) -> ResumeProfile:
        """Get a resume profile by ID with ownership check."""
        profile = self.repo.get_by_id(id)
        if not profile or profile.user_id != user_id:
            raise HTTPException(status_code=404, detail="Resume profile not found")
        return profile

    def list_profiles(
        self,
        user_id: str,
        *,
        page: int = 1,
        size: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[List[ResumeProfile], int]:
        """List resume profiles for a user with pagination and filtering."""
        skip = (page - 1) * size

        if status:
            items = self.repo.get_by_status(user_id, status)
            total = len(items)
            items = items[skip:skip + size]
        else:
            items, total = self.repo.get_by_user_id(user_id, skip=skip, limit=size)

        return items, total

    def update_profile(self, id: str, user_id: str, data: ResumeIntelligenceUpdate) -> ResumeProfile:
        """Update a resume profile."""
        profile = self.repo.get_by_id(id)
        if not profile or profile.user_id != user_id:
            raise HTTPException(status_code=404, detail="Resume profile not found")

        update_data = data.dict(exclude_unset=True)
        if not update_data:
            return profile

        try:
            old_state = {"status": profile.status, "title": profile.title}
            profile = self.repo.update(profile, update_data)
            new_state = {"status": profile.status, "title": profile.title}

            self.audit.log_update(
                user_id=user_id,
                entity_type="resume_profile",
                entity_id=profile.id,
                previous_state=old_state,
                new_state=new_state,
            )

            return profile
        except Exception as e:
            self.error.log_exception(e, context={"resume_profile_id": id})
            raise HTTPException(status_code=500, detail=str(e))

    def delete_profile(self, id: str, user_id: str) -> bool:
        """Soft delete a resume profile."""
        profile = self.repo.get_by_id(id)
        if not profile or profile.user_id != user_id:
            raise HTTPException(status_code=404, detail="Resume profile not found")

        try:
            old_state = {"status": profile.status}
            success = self.repo.soft_delete(id)

            if success:
                self.audit.log_delete(
                    user_id=user_id,
                    entity_type="resume_profile",
                    entity_id=id,
                    previous_state=old_state,
                )

            return success
        except Exception as e:
            self.error.log_exception(e, context={"resume_profile_id": id})
            raise HTTPException(status_code=500, detail=str(e))

    def trigger_parse(self, id: str, user_id: str) -> ResumeProfile:
        """Trigger the full parsing pipeline for a resume profile."""
        profile = self.repo.get_by_id(id)
        if not profile or profile.user_id != user_id:
            raise HTTPException(status_code=404, detail="Resume profile not found")

        self.repo.update(profile, {"status": ResumeProfileStatus.PARSING.value})

        start_time = time.time()

        try:
            parsed = self.parser.parse(profile.raw_text)
            normalized = self.normalizer.normalize(parsed)
            extracted = self.extractor.extract(
                normalized["sections"],
                normalized["metadata"],
            )

            parsed_data = extracted["parsed_data"]
            self.parsed_data_repo.upsert(profile.id, parsed_data)

            entities = extracted["entities"]
            if entities:
                self.entities_repo.bulk_create(profile.id, entities)

            knowledge = self.knowledge_builder.build(entities, parsed_data)
            self.knowledge_repo.upsert(profile.id, knowledge)

            processing_time_ms = int((time.time() - start_time) * 1000)

            update_data = {
                "status": ResumeProfileStatus.PARSED.value,
                "parser_version": "1.0.0",
                "processing_time_ms": processing_time_ms,
            }

            if not profile.title:
                name = knowledge.get("personal_info", {}).get("name")
                if name:
                    update_data["title"] = name

            profile = self.repo.update(profile, update_data)

            self.audit.log_update(
                user_id=user_id,
                entity_type="resume_profile",
                entity_id=profile.id,
                previous_state={"status": ResumeProfileStatus.PARSING.value},
                new_state={
                    "status": ResumeProfileStatus.PARSED.value,
                    "parser_version": "1.0.0",
                    "processing_time_ms": processing_time_ms,
                },
            )

            return profile

        except Exception as e:
            self.repo.update(profile, {
                "status": ResumeProfileStatus.FAILED.value,
                "error_message": str(e),
            })

            self.error.log_exception(e, context={"resume_profile_id": id})
            raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

    def get_parsed_data(self, id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get parsed data for a resume profile."""
        profile = self.repo.get_by_id(id)
        if not profile or profile.user_id != user_id:
            raise HTTPException(status_code=404, detail="Resume profile not found")

        parsed_data = self.parsed_data_repo.get_by_resume_profile_id(id)
        if not parsed_data:
            return None

        return {
            "id": parsed_data.id,
            "resume_profile_id": parsed_data.resume_profile_id,
            "summary": parsed_data.summary,
            "experience_entries": parsed_data.experience_entries,
            "education_entries": parsed_data.education_entries,
            "projects": parsed_data.projects,
            "raw_sections": parsed_data.raw_sections,
            "created_at": parsed_data.created_at,
            "updated_at": parsed_data.updated_at,
        }

    def get_entities(
        self, id: str, user_id: str, *, entity_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get entities for a resume profile."""
        profile = self.repo.get_by_id(id)
        if not profile or profile.user_id != user_id:
            raise HTTPException(status_code=404, detail="Resume profile not found")

        entities = self.entities_repo.get_by_resume_profile_id(id, entity_type=entity_type)
        return [
            {
                "id": e.id,
                "entity_type": e.entity_type,
                "entity_value": e.entity_value,
                "entity_metadata": e.entity_metadata,
                "created_at": e.created_at,
            }
            for e in entities
        ]

    def get_knowledge(self, id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get Resume Knowledge for a resume profile."""
        profile = self.repo.get_by_id(id)
        if not profile or profile.user_id != user_id:
            raise HTTPException(status_code=404, detail="Resume profile not found")

        knowledge = self.knowledge_repo.get_by_resume_profile_id(id)
        if not knowledge:
            return None

        return {
            "id": knowledge.id,
            "resume_profile_id": knowledge.resume_profile_id,
            "personal_info": knowledge.personal_info,
            "contact_info": knowledge.contact_info,
            "summary": knowledge.summary,
            "skills": knowledge.skills,
            "technologies": knowledge.technologies,
            "experience_summary": knowledge.experience_summary,
            "education_summary": knowledge.education_summary,
            "certifications": knowledge.certifications,
            "projects": knowledge.projects,
            "achievements": knowledge.achievements,
            "total_experience_years": knowledge.total_experience_years,
            "created_at": knowledge.created_at,
            "updated_at": knowledge.updated_at,
        }
