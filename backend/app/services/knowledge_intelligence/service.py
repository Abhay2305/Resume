"""Knowledge Intelligence Service.

Orchestrates the complete knowledge intelligence pipeline.
No AI involved - deterministic knowledge retrieval.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.gap_analysis import GapAnalysis
from app.models.knowledge_intelligence import KnowledgeContext, KnowledgeRetrieval
from app.repositories.knowledge_intelligence import (
    KnowledgeContextRepository,
    KnowledgeDocumentRepository,
    KnowledgeRetrievalRepository,
    KnowledgeRuleRepository,
    KnowledgeSectionRepository,
)
from app.services.audit_service import AuditService
from app.services.knowledge_intelligence.context_builder import KnowledgeContextBuilder
from app.services.knowledge_intelligence.indexer import KnowledgeIndexer
from app.services.knowledge_intelligence.ranker import KnowledgeRanker
from app.services.knowledge_intelligence.retriever import KnowledgeRetriever
from app.services.knowledge_intelligence.rule_extractor import KnowledgeRuleExtractor
from app.services.knowledge_intelligence.rule_approval import RuleApproval
from app.services.knowledge_intelligence.provenance_tracker import ProvenanceTracker
from app.services.knowledge_intelligence.section_service import KnowledgeSectionService


class KnowledgeIntelligenceService:
    """Service for knowledge intelligence operations."""

    def __init__(self, db: Session):
        self.db = db
        self.document_repo = KnowledgeDocumentRepository(db)
        self.section_repo = KnowledgeSectionRepository(db)
        self.rule_repo = KnowledgeRuleRepository(db)
        self.retrieval_repo = KnowledgeRetrievalRepository(db)
        self.context_repo = KnowledgeContextRepository(db)
        self.audit_service = AuditService(db)
        self.rule_extractor = KnowledgeRuleExtractor()
        self.indexer = KnowledgeIndexer()
        self.ranker = KnowledgeRanker()
        self.retriever = KnowledgeRetriever()
        self.context_builder = KnowledgeContextBuilder()
        self.section_service = KnowledgeSectionService(db)
        self.rule_approval = RuleApproval()
        self.provenance_tracker = ProvenanceTracker()

    def retrieve_knowledge(
        self,
        gap_analysis_id: str,
        user_id: str,
        max_rules: int = 30,
    ) -> Dict[str, Any]:
        """Retrieve relevant knowledge based on gap analysis.

        Args:
            gap_analysis_id: Gap analysis ID.
            user_id: User ID.
            max_rules: Maximum rules to retrieve.

        Returns:
            Dictionary with retrieval results and context.
        """
        start_time = datetime.utcnow()

        gap_analysis = self.db.query(GapAnalysis).filter(
            GapAnalysis.id == gap_analysis_id
        ).first()
        if not gap_analysis:
            raise ValueError(f"Gap analysis not found: {gap_analysis_id}")

        all_rules = self._get_all_active_rules()

        gap_results = self._build_gap_results(gap_analysis)

        retrieved_rules = self.retriever.retrieve(
            all_rules, gap_results, max_rules
        )

        context = self.context_builder.build(retrieved_rules)

        end_time = datetime.utcnow()
        processing_time = int((end_time - start_time).total_seconds() * 1000)

        retrieval = self.retrieval_repo.create({
            "gap_analysis_id": gap_analysis_id,
            "user_id": user_id,
            "total_rules_retrieved": len(retrieved_rules),
            "retrieval_strategy": "category_match",
            "processing_time_ms": processing_time,
        })

        context_data = {
            "retrieval_id": retrieval.id,
            "gap_analysis_id": gap_analysis_id,
            "summary_rules": context.get("summary_rules"),
            "experience_rules": context.get("experience_rules"),
            "skills_rules": context.get("skills_rules"),
            "education_rules": context.get("education_rules"),
            "projects_rules": context.get("projects_rules"),
            "certifications_rules": context.get("certifications_rules"),
            "ats_rules": context.get("ats_rules"),
            "formatting_rules": context.get("formatting_rules"),
            "cover_letter_rules": context.get("cover_letter_rules"),
            "total_rules": context.get("total_rules", 0),
            "citations": context.get("citations"),
        }
        knowledge_context = self.context_repo.create(context_data)

        self.audit_service.log_create(
            user_id=user_id,
            entity_type="knowledge_retrieved",
            entity_id=retrieval.id,
            details={
                "gap_analysis_id": gap_analysis_id,
                "total_rules": len(retrieved_rules),
                "processing_time_ms": processing_time,
            },
        )

        return {
            "retrieval": retrieval,
            "context": knowledge_context,
            "rules": retrieved_rules,
        }

    def get_context_by_gap_analysis(
        self, gap_analysis_id: str
    ) -> Optional[KnowledgeContext]:
        """Get knowledge context by gap analysis ID."""
        return self.context_repo.get_by_gap_analysis_id(gap_analysis_id)

    def get_retrieval_by_id(self, retrieval_id: str) -> Optional[KnowledgeRetrieval]:
        """Get retrieval by ID."""
        return self.retrieval_repo.get_by_id(retrieval_id)

    def get_context_by_retrieval_id(self, retrieval_id: str) -> Optional[KnowledgeContext]:
        """Get context by retrieval ID."""
        return self.context_repo.get_by_retrieval_id(retrieval_id)

    def get_all_rules(
        self, *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all knowledge rules."""
        rules = self.rule_repo.get_active()
        total = len(rules)
        paginated = rules[skip:skip + limit]
        return [self._rule_to_dict(r) for r in paginated], total

    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get rule by ID."""
        rule = self.rule_repo.get_by_id(rule_id)
        if rule:
            return self._rule_to_dict(rule)
        return None

    def search_rules(
        self, q: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Search knowledge rules."""
        rules, total = self.rule_repo.search(q, skip=skip, limit=limit)
        return [self._rule_to_dict(r) for r in rules], total

    def _get_all_active_rules(self) -> List[Dict[str, Any]]:
        """Get all active rules, ensuring mandatory rules are always included.

        Mandatory rules (core writing principles, vocabulary guidance) are
        always injected regardless of category-based retrieval.
        """
        rules = self.rule_repo.get_active()
        rule_dicts = [self._rule_to_dict(r) for r in rules]

        # Ensure mandatory rules are always present
        mandatory_keys = [
            "INT_BUL_001", "INT_BUL_002", "INT_BUL_003", "INT_BUL_004", "INT_BUL_005",
            "INT_VER_001", "INT_VER_002", "INT_PHR_001", "INT_PHR_002",
        ]
        present_keys = {r["rule_id"] for r in rule_dicts}
        for key in mandatory_keys:
            if key not in present_keys:
                rule = self.rule_repo.get_by_key(key)
                if rule:
                    rule_dicts.append(self._rule_to_dict(rule))

        return rule_dicts

    def _rule_to_dict(self, rule) -> Dict[str, Any]:
        """Convert a rule model to dictionary including provenance fields."""
        return {
            "rule_id": rule.rule_key,
            "source": rule.source,
            "section_name": rule.section_name,
            "priority": rule.priority,
            "category": rule.category,
            "instruction": rule.instruction,
            "reason": rule.reason,
            "examples": rule.examples,
            "confidence": rule.confidence,
            "source_document": getattr(rule, "source_document", None),
            "source_page": getattr(rule, "source_page", None),
            "source_evidence": getattr(rule, "source_evidence", None),
            "extraction_confidence": getattr(rule, "extraction_confidence", None),
            "extraction_timestamp": getattr(rule, "extraction_timestamp", None),
            "rule_hash": getattr(rule, "rule_hash", None),
            "state": getattr(rule, "state", "ACTIVE"),
            "version": getattr(rule, "version", 1),
        }

    def _build_gap_results(self, gap_analysis: GapAnalysis) -> Dict[str, Any]:
        """Build gap results dictionary from gap analysis model."""
        return {
            "skills": {"required": {"missing": [], "matched": []}, "preferred": {"missing": []}, "score": gap_analysis.skill_match_score or 0},
            "technology": {"categories": {}, "score": gap_analysis.technology_match_score or 0},
            "experience": {"years": {"sufficient": True}, "roles": {"missing": []}, "score": gap_analysis.experience_match_score or 0},
            "education": {"degree": {"sufficient": True}, "field": {"match": True}, "score": gap_analysis.education_match_score or 0},
            "certifications": {"required": {"missing": []}, "preferred": {"missing": []}, "score": gap_analysis.certification_match_score or 0},
            "keywords": {"missing": [], "weak": [], "score": gap_analysis.keyword_match_score or 0},
        }

    def initialize_document_rules(self, document_id: str, document_key: str) -> int:
        """Initialize rules for a document from extracted rules.

        Args:
            document_id: Document ID.
            document_key: Document key.

        Returns:
            Number of rules created.
        """
        extracted_rules = self.rule_extractor.extract_from_document(document_key)
        if not extracted_rules:
            return 0

        rules_to_create = []
        for rule in extracted_rules:
            normalized = self.rule_extractor.normalize_rule(rule)
            normalized["document_id"] = document_id
            normalized["rule_key"] = normalized.pop("rule_id")
            rules_to_create.append(normalized)

        created = self.rule_repo.create_many(rules_to_create)

        self.document_repo.update(document_id, {"total_rules": len(created)})

        return len(created)

    def ingest_pdf_rules(
        self,
        pdf_rules: List[Dict[str, Any]],
        document_id: str,
    ) -> int:
        """Ingest PDF-extracted rules into the knowledge repository.

        Rules start at state=VERIFIED and is_active=False.
        They must pass through APPROVED -> ACTIVE before becoming
        runtime knowledge. This enforces the governance lifecycle:
        DISCOVERED -> EXTRACTED -> CLASSIFIED -> VERIFIED -> APPROVED -> ACTIVE

        Args:
            pdf_rules: List of rules extracted from PDFs (with provenance).
            document_id: Document ID to associate rules with.

        Returns:
            Number of rules ingested.
        """
        rules_to_create = []
        for rule in pdf_rules:
            rule_data = {
                "document_id": document_id,
                "rule_key": rule.get("rule_id", ""),
                "source": rule.get("source_document", "unknown"),
                "section_name": rule.get("section_name", "general"),
                "priority": rule.get("priority", "medium"),
                "category": rule.get("category", "General"),
                "instruction": rule.get("instruction", ""),
                "reason": rule.get("reason", ""),
                "examples": rule.get("examples", []),
                "confidence": rule.get("confidence", 0.8),
                "is_active": False,  # NOT active until approved
                "source_document": rule.get("source_document"),
                "source_page": rule.get("source_page"),
                "source_evidence": rule.get("source_evidence"),
                "extraction_confidence": rule.get("confidence"),
                "extraction_timestamp": rule.get("extraction_timestamp"),
                "rule_hash": rule.get("rule_hash"),
                "state": "VERIFIED",  # Must go through APPROVED -> ACTIVE
                "version": 1,
            }
            rules_to_create.append(rule_data)

        created = self.rule_repo.create_many(rules_to_create)

        self.document_repo.update(document_id, {"total_rules": len(created)})

        return len(created)

    def seed_hand_authored_rules(self, document_id: str) -> int:
        """Seed hand-authored rules from knowledge_rules.json with provenance.

        Args:
            document_id: Document ID to associate rules with.

        Returns:
            Number of rules seeded.
        """
        seed_rules = self.rule_approval.load_seed_rules_from_json()
        if not seed_rules:
            return 0

        seeded = self.rule_approval.seed_hand_authored_rules(seed_rules)

        rules_to_create = []
        for rule in seeded:
            rule_data = {
                "document_id": document_id,
                "rule_key": rule.get("rule_id", ""),
                "source": rule.get("source", "hand-authored"),
                "section_name": rule.get("section_name", "general"),
                "priority": rule.get("priority", "medium"),
                "category": rule.get("category", "General"),
                "instruction": rule.get("instruction", ""),
                "reason": rule.get("reason", ""),
                "examples": rule.get("examples", []),
                "confidence": 1.0,
                "is_active": True,
                "source_document": "hand-authored",
                "source_page": None,
                "source_evidence": None,
                "extraction_confidence": 1.0,
                "extraction_timestamp": rule.get("extraction_timestamp"),
                "rule_hash": rule.get("rule_hash"),
                "state": "ACTIVE",
                "version": 1,
            }
            rules_to_create.append(rule_data)

        created = self.rule_repo.create_many(rules_to_create)

        self.document_repo.update(document_id, {"total_rules": len(created)})

        return len(created)

    def get_rules_by_state(self, state: str) -> List[Dict[str, Any]]:
        """Get all rules with a specific governance state.

        Args:
            state: Governance state (e.g., 'ACTIVE', 'VERIFIED', 'DISCOVERED').

        Returns:
            List of rules in the specified state.
        """
        from app.models.knowledge_intelligence import KnowledgeRule
        rules = self.db.query(KnowledgeRule).filter(
            KnowledgeRule.state == state,
        ).all()
        return [self._rule_to_dict(r) for r in rules]

    def get_rules_by_source_document(self, source_document: str) -> List[Dict[str, Any]]:
        """Get all rules from a specific source document.

        Args:
            source_document: Source document name (e.g., 'harvard.pdf' or 'hand-authored').

        Returns:
            List of rules from the specified source.
        """
        from app.models.knowledge_intelligence import KnowledgeRule
        rules = self.db.query(KnowledgeRule).filter(
            KnowledgeRule.source_document == source_document,
            KnowledgeRule.is_active == True,
        ).all()
        return [self._rule_to_dict(r) for r in rules]

    def get_rule_provenance(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get provenance information for a specific rule.

        Args:
            rule_id: Rule key/ID.

        Returns:
            Provenance dictionary or None if rule not found.
        """
        rule = self.rule_repo.get_by_key(rule_id)
        if not rule:
            return None
        return {
            "rule_id": rule.rule_key,
            "source_document": getattr(rule, "source_document", None),
            "source_page": getattr(rule, "source_page", None),
            "source_evidence": getattr(rule, "source_evidence", None),
            "extraction_confidence": getattr(rule, "extraction_confidence", None),
            "extraction_timestamp": getattr(rule, "extraction_timestamp", None),
            "rule_hash": getattr(rule, "rule_hash", None),
            "state": getattr(rule, "state", "ACTIVE"),
            "version": getattr(rule, "version", 1),
        }

    # ========================================================================
    # Governance Methods
    # ========================================================================

    def approve_rule(
        self, rule_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Approve a rule: VERIFIED → APPROVED.

        Enforces:
        - Rule must exist
        - Rule must be in VERIFIED state
        - Provenance must be valid for PDF-derived rules
        - Only VERIFIED → APPROVED transition is allowed

        Args:
            rule_id: Rule primary key (UUID).
            user_id: ID of the user performing the action.

        Returns:
            Dictionary with governance action result.

        Raises:
            ValueError: If rule not found, invalid state, or provenance invalid.
        """
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise ValueError(f"Rule not found: {rule_id}")

        previous_state = rule.state

        if previous_state != "VERIFIED":
            raise ValueError(
                f"Cannot approve rule in state '{previous_state}': "
                f"only VERIFIED rules can be approved"
            )

        # Provenance gate: verify provenance before approval
        if rule.source_document and rule.source_document != "hand-authored":
            provenance_valid = self._validate_provenance_for_approval(rule)
            if not provenance_valid["valid"]:
                raise ValueError(
                    f"Provenance validation failed: {'; '.join(provenance_valid['issues'])}"
                )

        # Transition state
        rule.state = "APPROVED"
        rule.version = (rule.version or 1) + 1
        self.db.flush()

        # Log audit
        self.audit_service.log_create(
            user_id=user_id,
            entity_type="knowledge_rule_governance",
            entity_id=rule.id,
            details={
                "action": "approve",
                "rule_key": rule.rule_key,
                "previous_state": previous_state,
                "new_state": "APPROVED",
                "source_document": rule.source_document,
            },
        )

        return {
            "rule_id": rule.id,
            "rule_key": rule.rule_key,
            "previous_state": previous_state,
            "new_state": rule.state,
            "previous_is_active": rule.is_active,
            "new_is_active": rule.is_active,
            "message": f"Rule approved: {previous_state} → APPROVED",
        }

    def activate_rule(
        self, rule_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Activate a rule: APPROVED → ACTIVE.

        Enforces:
        - Rule must exist
        - Rule must be in APPROVED state
        - Sets is_active=True

        Args:
            rule_id: Rule primary key (UUID).
            user_id: ID of the user performing the action.

        Returns:
            Dictionary with governance action result.

        Raises:
            ValueError: If rule not found or invalid state.
        """
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise ValueError(f"Rule not found: {rule_id}")

        previous_state = rule.state

        if previous_state != "APPROVED":
            raise ValueError(
                f"Cannot activate rule in state '{previous_state}': "
                f"only APPROVED rules can be activated"
            )

        # Transition state and activate
        rule.state = "ACTIVE"
        rule.is_active = True
        rule.version = (rule.version or 1) + 1
        self.db.flush()

        # Log audit
        self.audit_service.log_create(
            user_id=user_id,
            entity_type="knowledge_rule_governance",
            entity_id=rule.id,
            details={
                "action": "activate",
                "rule_key": rule.rule_key,
                "previous_state": previous_state,
                "new_state": "ACTIVE",
                "source_document": rule.source_document,
            },
        )

        return {
            "rule_id": rule.id,
            "rule_key": rule.rule_key,
            "previous_state": previous_state,
            "new_state": rule.state,
            "previous_is_active": False,
            "new_is_active": True,
            "message": f"Rule activated: {previous_state} → ACTIVE",
        }

    def deactivate_rule(
        self, rule_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Deactivate a rule: sets is_active=False and transitions state.

        For ACTIVE rules, transitions to REJECTED (removes from runtime
        and governance). The rule must be re-approved to become active again.

        Args:
            rule_id: Rule primary key (UUID).
            user_id: ID of the user performing the action.

        Returns:
            Dictionary with governance action result.

        Raises:
            ValueError: If rule not found.
        """
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise ValueError(f"Rule not found: {rule_id}")

        previous_state = rule.state
        previous_is_active = rule.is_active

        # Transition state and deactivate
        if rule.state == "ACTIVE":
            rule.state = "REJECTED"
        rule.is_active = False
        self.db.flush()

        new_state = rule.state

        # Log audit
        self.audit_service.log_create(
            user_id=user_id,
            entity_type="knowledge_rule_governance",
            entity_id=rule.id,
            details={
                "action": "deactivate",
                "rule_key": rule.rule_key,
                "previous_state": previous_state,
                "new_state": new_state,
                "previous_is_active": previous_is_active,
                "new_is_active": False,
            },
        )

        return {
            "rule_id": rule.id,
            "rule_key": rule.rule_key,
            "previous_state": previous_state,
            "new_state": new_state,
            "previous_is_active": previous_is_active,
            "new_is_active": False,
            "message": f"Rule deactivated: {previous_state} → {new_state}",
        }

    def reject_rule(
        self, rule_id: str, user_id: str, reason: str = ""
    ) -> Dict[str, Any]:
        """Reject a rule: transitions to REJECTED state.

        Validates the state transition against STATE_TRANSITIONS before
        allowing rejection. All states allow transition to REJECTED.

        Args:
            rule_id: Rule primary key (UUID).
            user_id: ID of the user performing the action.
            reason: Optional rejection reason.

        Returns:
            Dictionary with governance action result.

        Raises:
            ValueError: If rule not found or transition not allowed.
        """
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise ValueError(f"Rule not found: {rule_id}")

        # Validate state transition
        from app.services.knowledge_intelligence.rule_approval import STATE_TRANSITIONS
        allowed = STATE_TRANSITIONS.get(rule.state, [])
        if "REJECTED" not in allowed:
            raise ValueError(
                f"Cannot reject rule in state {rule.state}. "
                f"Allowed transitions: {allowed}"
            )

        previous_state = rule.state
        rule.state = "REJECTED"
        rule.is_active = False
        rule.version = (rule.version or 1) + 1
        self.db.flush()

        # Log audit
        self.audit_service.log_create(
            user_id=user_id,
            entity_type="knowledge_rule_governance",
            entity_id=rule.id,
            details={
                "action": "reject",
                "rule_key": rule.rule_key,
                "previous_state": previous_state,
                "new_state": "REJECTED",
                "reason": reason,
            },
        )

        return {
            "rule_id": rule.id,
            "rule_key": rule.rule_key,
            "previous_state": previous_state,
            "new_state": rule.state,
            "previous_is_active": rule.is_active,
            "new_is_active": False,
            "message": f"Rule rejected: {previous_state} → REJECTED",
        }

    def _validate_provenance_for_approval(self, rule) -> Dict[str, Any]:
        """Validate provenance is complete before approval.

        For PDF-derived rules, requires:
        - source_document
        - source_page
        - source_evidence (optional but recommended)
        - extraction_confidence
        - extraction_timestamp
        - rule_hash

        Args:
            rule: KnowledgeRule ORM instance.

        Returns:
            Dictionary with 'valid' bool and 'issues' list.
        """
        issues = []

        if not rule.source_document:
            issues.append("Missing source_document")

        if rule.source_page is None:
            issues.append("Missing source_page")

        if rule.extraction_confidence is None:
            issues.append("Missing extraction_confidence")
        elif not (0.0 <= rule.extraction_confidence <= 1.0):
            issues.append(f"Invalid extraction_confidence: {rule.extraction_confidence}")

        if not rule.extraction_timestamp:
            issues.append("Missing extraction_timestamp")

        if not rule.rule_hash:
            issues.append("Missing rule_hash")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

    def list_rules_by_state(
        self, state: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List rules filtered by governance state.

        Args:
            state: Governance state to filter by.
            skip: Pagination offset.
            limit: Maximum rules to return.

        Returns:
            Tuple of (rules as dicts, total count).
        """
        rules, total = self.rule_repo.get_by_state(state, skip=skip, limit=limit)
        return [self._rule_to_dict(r) for r in rules], total

    def get_governance_stats(self) -> Dict[str, Any]:
        """Get governance statistics: rules by state and source.

        Returns:
            Dictionary with total count, counts by state, and counts by source.
        """
        by_state = self.rule_repo.count_by_state()

        from app.models.knowledge_intelligence import KnowledgeRule
        from sqlalchemy import func
        source_results = self.db.query(
            KnowledgeRule.source_document, func.count(KnowledgeRule.id)
        ).group_by(KnowledgeRule.source_document).all()
        by_source = {src: count for src, count in source_results}

        return {
            "total_rules": sum(by_state.values()),
            "by_state": by_state,
            "by_source": by_source,
        }
