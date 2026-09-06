"""Opportunity Service.

Orchestrates the entire opportunity parsing pipeline:
Parser -> Normalizer -> Extractor -> Repository
"""
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException

from app.models.opportunity import Opportunity, OpportunityStatus
from app.repositories.opportunity import (
    OpportunityEntityRepository,
    OpportunityRepository,
    ParsedOpportunityDataRepository,
)
from app.schemas import (
    OpportunityCreate,
    OpportunityUpdate,
)
from app.services.audit_service import AuditService
from app.services.error_service import ErrorService
from app.services.opportunity.extractors import ExtractorOrchestrator
from app.services.opportunity.parsers.normalizer import OpportunityNormalizer
from app.services.opportunity.parsers.parser import OpportunityParser


class OpportunityService:
    """Service for managing opportunities and orchestrating the parsing pipeline."""

    def __init__(self, db):
        self.db = db
        self.repo = OpportunityRepository(db)
        self.parsed_data_repo = ParsedOpportunityDataRepository(db)
        self.entities_repo = OpportunityEntityRepository(db)
        self.parser = OpportunityParser()
        self.normalizer = OpportunityNormalizer()
        self.extractor = ExtractorOrchestrator()
        self.audit = AuditService(db)
        self.error = ErrorService(db)

    def create_opportunity(self, user_id: str, data: OpportunityCreate) -> Opportunity:
        """Create a new opportunity (without parsing).

        Args:
            user_id: The user ID.
            data: Opportunity creation data.

        Returns:
            Created opportunity.
        """
        try:
            opp_data = {
                "user_id": user_id,
                "raw_text": data.raw_text,
                "title": data.title,
                "company": data.company,
                "url": data.url,
                "status": OpportunityStatus.PENDING.value,
            }
            opportunity = self.repo.create(opp_data)

            # Audit log
            self.audit.log_create(
                user_id=user_id,
                entity_type="opportunity",
                entity_id=opportunity.id,
                new_state={"status": opportunity.status, "title": opportunity.title},
            )

            return opportunity
        except Exception as e:
            self.error.log_exception(e, context={"user_id": user_id})
            raise HTTPException(status_code=500, detail=str(e))

    def get_opportunity(self, id: str, user_id: str) -> Opportunity:
        """Get an opportunity by ID with ownership check.

        Args:
            id: Opportunity ID.
            user_id: The user ID.

        Returns:
            The opportunity.

        Raises:
            HTTPException: If opportunity not found or unauthorized.
        """
        opportunity = self.repo.get_by_id(id)
        if not opportunity or opportunity.user_id != user_id:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        return opportunity

    def list_opportunities(
        self,
        user_id: str,
        *,
        page: int = 1,
        size: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[List[Opportunity], int]:
        """List opportunities for a user with pagination and filtering.

        Args:
            user_id: The user ID.
            page: Page number (1-indexed).
            size: Page size.
            status: Filter by status.

        Returns:
            Tuple of (opportunities, total count).
        """
        skip = (page - 1) * size

        if status:
            items = self.repo.get_by_status(user_id, status)
            total = len(items)
            items = items[skip:skip + size]
        else:
            items, total = self.repo.get_by_user_id(user_id, skip=skip, limit=size)

        return items, total

    def update_opportunity(self, id: str, user_id: str, data: OpportunityUpdate) -> Opportunity:
        """Update an opportunity.

        Args:
            id: Opportunity ID.
            user_id: The user ID.
            data: Update data.

        Returns:
            Updated opportunity.

        Raises:
            HTTPException: If opportunity not found or unauthorized.
        """
        opportunity = self.repo.get_by_id(id)
        if not opportunity or opportunity.user_id != user_id:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        update_data = data.dict(exclude_unset=True)
        if not update_data:
            return opportunity

        try:
            old_state = {"status": opportunity.status, "title": opportunity.title}
            opportunity = self.repo.update(opportunity, update_data)
            new_state = {"status": opportunity.status, "title": opportunity.title}

            # Audit log
            self.audit.log_update(
                user_id=user_id,
                entity_type="opportunity",
                entity_id=opportunity.id,
                previous_state=old_state,
                new_state=new_state,
            )

            return opportunity
        except Exception as e:
            self.error.log_exception(e, context={"opportunity_id": id})
            raise HTTPException(status_code=500, detail=str(e))

    def delete_opportunity(self, id: str, user_id: str) -> bool:
        """Soft delete an opportunity.

        Args:
            id: Opportunity ID.
            user_id: The user ID.

        Returns:
            True if deleted.

        Raises:
            HTTPException: If opportunity not found or unauthorized.
        """
        opportunity = self.repo.get_by_id(id)
        if not opportunity or opportunity.user_id != user_id:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        try:
            old_state = {"status": opportunity.status}
            success = self.repo.soft_delete(id)

            if success:
                # Audit log
                self.audit.log_delete(
                    user_id=user_id,
                    entity_type="opportunity",
                    entity_id=id,
                    previous_state=old_state,
                )

            return success
        except Exception as e:
            self.error.log_exception(e, context={"opportunity_id": id})
            raise HTTPException(status_code=500, detail=str(e))

    def trigger_parse(self, id: str, user_id: str) -> Opportunity:
        """Trigger the full parsing pipeline for an opportunity.

        Args:
            id: Opportunity ID.
            user_id: The user ID.

        Returns:
            Updated opportunity with parsed data.

        Raises:
            HTTPException: If opportunity not found or unauthorized.
        """
        opportunity = self.repo.get_by_id(id)
        if not opportunity or opportunity.user_id != user_id:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        # Set status to parsing
        self.repo.update(opportunity, {"status": OpportunityStatus.PARSING.value})

        start_time = time.time()

        try:
            # 1. Parse
            parsed = self.parser.parse(opportunity.raw_text)

            # 2. Normalize
            normalized = self.normalizer.normalize(parsed)

            # 3. Extract
            extracted = self.extractor.extract(
                normalized["sections"],
                normalized["metadata"],
            )

            # 4. Store parsed data (only valid columns for ParsedOpportunityData)
            parsed_data = extracted["parsed_data"]
            valid_columns = {"responsibilities", "benefits", "ats_keywords", "raw_sections"}
            filtered_parsed_data = {k: v for k, v in parsed_data.items() if k in valid_columns}
            self.parsed_data_repo.upsert(opportunity.id, filtered_parsed_data)

            # 5. Store entities
            entities = extracted["entities"]
            if entities:
                self.entities_repo.bulk_create(opportunity.id, entities)

            # 6. Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            # 7. Update opportunity
            update_data = {
                "status": OpportunityStatus.PARSED.value,
                "parser_version": "1.0.0",
                "processing_time_ms": processing_time_ms,
            }

            # Extract title and company from text if not provided
            if not opportunity.title:
                title = self._extract_title(normalized["sections"])
                if title:
                    update_data["title"] = title

            if not opportunity.company:
                company = self._extract_company(normalized["sections"])
                if company:
                    update_data["company"] = company

            opportunity = self.repo.update(opportunity, update_data)

            # 8. Audit log
            self.audit.log_update(
                user_id=user_id,
                entity_type="opportunity",
                entity_id=opportunity.id,
                previous_state={"status": OpportunityStatus.PARSING.value},
                new_state={
                    "status": OpportunityStatus.PARSED.value,
                    "parser_version": "1.0.0",
                    "processing_time_ms": processing_time_ms,
                },
            )

            return opportunity

        except Exception as e:
            # Update status to failed
            self.repo.update(opportunity, {
                "status": OpportunityStatus.FAILED.value,
                "error_message": str(e),
            })

            self.error.log_exception(e, context={"opportunity_id": id})
            raise HTTPException(status_code=500, detail=f"Failed to parse opportunity: {str(e)}")

    def get_parsed_data(self, id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get parsed data for an opportunity.

        Args:
            id: Opportunity ID.
            user_id: The user ID.

        Returns:
            Parsed data dictionary or None.

        Raises:
            HTTPException: If opportunity not found or unauthorized.
        """
        opportunity = self.repo.get_by_id(id)
        if not opportunity or opportunity.user_id != user_id:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        parsed_data = self.parsed_data_repo.get_by_opportunity_id(id)
        if not parsed_data:
            return None

        return {
            "id": parsed_data.id,
            "opportunity_id": parsed_data.opportunity_id,
            "responsibilities": parsed_data.responsibilities,
            "benefits": parsed_data.benefits,
            "ats_keywords": parsed_data.ats_keywords,
            "raw_sections": parsed_data.raw_sections,
            "created_at": parsed_data.created_at,
            "updated_at": parsed_data.updated_at,
        }

    def get_entities(
        self, id: str, user_id: str, *, entity_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get entities for an opportunity.

        Args:
            id: Opportunity ID.
            user_id: The user ID.
            entity_type: Filter by entity type.

        Returns:
            List of entity dictionaries.

        Raises:
            HTTPException: If opportunity not found or unauthorized.
        """
        opportunity = self.repo.get_by_id(id)
        if not opportunity or opportunity.user_id != user_id:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        entities = self.entities_repo.get_by_opportunity_id(id, entity_type=entity_type)
        return [
            {
                "id": e.id,
                "entity_type": e.entity_type,
                "entity_value": e.entity_value,
                "is_required": e.is_required,
                "created_at": e.created_at,
            }
            for e in entities
        ]

    def _extract_title(self, sections: Dict[str, str]) -> Optional[str]:
        """Extract title from sections.

        Args:
            sections: Detected sections.

        Returns:
            Extracted title or None.
        """
        # Try to get title from the first line of general section
        general = sections.get("general", "")
        if general:
            first_line = general.split("\n")[0].strip()
            if len(first_line) < 100:  # Reasonable title length
                return first_line
        return None

    def _extract_company(self, sections: Dict[str, str]) -> Optional[str]:
        """Extract company from sections.

        Args:
            sections: Detected sections.

        Returns:
            Extracted company or None.
        """
        # Try to extract company from about section
        about = sections.get("about", "")
        if about:
            # Look for common patterns
            import re
            patterns = [
                r"(?:about|at|join)\s+([A-Z][A-Za-z\s&]+)",
                r"([A-Z][A-Za-z\s&]+)\s+(?:is|was|are|were)",
            ]
            for pattern in patterns:
                match = re.search(pattern, about)
                if match:
                    company = match.group(1).strip()
                    if len(company) < 100:  # Reasonable company name length
                        return company
        return None
