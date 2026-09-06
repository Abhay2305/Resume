"""AI Response Intelligence Service.

Orchestrates the full validation pipeline:
Schema -> Truth -> Knowledge -> Gap -> Diff -> Confidence -> Approval Package
"""
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.ai_response_intelligence import (
    AIResponseValidation,
    ChangeSet,
    ConfidenceScore,
    ResumeDiff,
    ValidationReport,
    ValidationStatus,
)
from app.repositories.ai_execution import AIExecutionRepository
from app.repositories.ai_response_intelligence import (
    AIResponseValidationRepository,
    ChangeSetRepository,
    ConfidenceScoreRepository,
    ResumeDiffRepository,
    ValidationReportRepository,
)
from app.repositories.gap_analysis import GapAnalysisRepository, GapResultRepository
from app.repositories.knowledge_intelligence import KnowledgeRuleRepository
from app.repositories.prompt_intelligence import PromptPackageRepository
from app.repositories.resume_intelligence import ResumeKnowledgeRepository
from app.services.ai_response_intelligence.approval_builder import ApprovalPackageBuilder
from app.services.ai_response_intelligence.change_classifier import ChangeClassifier
from app.services.ai_response_intelligence.confidence_engine import ConfidenceEngine
from app.services.ai_response_intelligence.diff_engine import DiffEngine
from app.services.ai_response_intelligence.gap_validator import GapValidator
from app.services.ai_response_intelligence.knowledge_validator import KnowledgeValidator
from app.services.ai_response_intelligence.schema_validator import ResponseSchemaValidator
from app.services.ai_response_intelligence.truth_validator import TruthValidator

logger = logging.getLogger(__name__)


class AIResponseIntelligenceService:
    """Orchestrates the full AI response validation pipeline.

    Validates, analyzes, explains, and compares every AI response
    before it can become part of a resume.
    """

    def __init__(self, db: Session):
        self.db = db
        self.validation_repo = AIResponseValidationRepository(db)
        self.diff_repo = ResumeDiffRepository(db)
        self.change_repo = ChangeSetRepository(db)
        self.report_repo = ValidationReportRepository(db)
        self.confidence_repo = ConfidenceScoreRepository(db)
        self.execution_repo = AIExecutionRepository(db)
        self.package_repo = PromptPackageRepository(db)
        self.resume_knowledge_repo = ResumeKnowledgeRepository(db)
        self.gap_analysis_repo = GapAnalysisRepository(db)
        self.gap_result_repo = GapResultRepository(db)
        self.knowledge_rule_repo = KnowledgeRuleRepository(db)

        # Validators
        self.schema_validator = ResponseSchemaValidator()
        self.truth_validator = TruthValidator()
        self.knowledge_validator = KnowledgeValidator()
        self.gap_validator = GapValidator()
        self.diff_engine = DiffEngine()
        self.change_classifier = ChangeClassifier()
        self.confidence_engine = ConfidenceEngine()
        self.approval_builder = ApprovalPackageBuilder()

    def validate_ai_response(
        self,
        user_id: str,
        ai_execution_id: str,
    ) -> Dict[str, Any]:
        """Run the full validation pipeline on an AI response.

        Args:
            user_id: The user who owns the execution.
            ai_execution_id: The AI execution to validate.

        Returns:
            Validation result with approval package.
        """
        start_time = time.time()

        # Load execution
        execution = self.execution_repo.get_by_id(ai_execution_id)
        if not execution:
            raise ValueError(f"AI execution not found: {ai_execution_id}")

        if execution.user_id != user_id:
            raise ValueError("AI execution does not belong to user")

        if execution.status != "completed":
            raise ValueError(f"AI execution is not completed: {execution.status}")

        # Parse response
        response_data = execution.parsed_response
        if not response_data:
            try:
                response_data = json.loads(execution.raw_response) if execution.raw_response else {}
            except (json.JSONDecodeError, TypeError):
                response_data = {"text": execution.raw_response}

        # Load prompt package
        package = self.package_repo.get_by_id(execution.prompt_package_id)
        if not package:
            raise ValueError("Prompt package not found")

        # Load resume knowledge
        resume_knowledge = {}
        if package.gap_analysis_id:
            gap_analysis = self.gap_analysis_repo.get(package.gap_analysis_id)
            if gap_analysis:
                knowledge = self.resume_knowledge_repo.get_by_resume_profile_id(
                    gap_analysis.resume_profile_id
                )
                if knowledge:
                    resume_knowledge = {
                        "skills": knowledge.skills or [],
                        "technologies": knowledge.technologies or {},
                        "experience_summary": knowledge.experience_summary or [],
                        "education_summary": knowledge.education_summary or [],
                        "certifications": knowledge.certifications or [],
                        "projects": knowledge.projects or [],
                        "achievements": knowledge.achievements or [],
                        "summary": knowledge.summary or "",
                    }

        # Load gap results
        gap_results = []
        gap_analysis_data = {}
        if package.gap_analysis_id:
            gap_analysis = self.gap_analysis_repo.get(package.gap_analysis_id)
            if gap_analysis:
                gap_analysis_data = {
                    "id": gap_analysis.id,
                    "overall_match_score": gap_analysis.overall_match_score,
                    "total_gaps": gap_analysis.total_gaps,
                }
                gap_results_raw = self.gap_result_repo.get_by_gap_analysis_id(gap_analysis.id)
                gap_results = [
                    {
                        "id": g.id,
                        "category": g.category,
                        "match_score": g.match_score,
                        "missing_items": g.missing_items,
                        "matched_items": g.matched_items,
                    }
                    for g in gap_results_raw
                ]

        # Load knowledge rules
        knowledge_rules = []
        knowledge_rules_raw = self.knowledge_rule_repo.get_all()
        knowledge_rules = [
            {
                "rule_key": r.rule_key,
                "source": r.source,
                "section_name": r.section_name,
                "category": r.category,
                "instruction": r.instruction,
                "reason": r.reason,
                "priority": r.priority,
                "is_active": r.is_active,
            }
            for r in knowledge_rules_raw
        ]

        # Create validation record
        validation = self.validation_repo.create({
            "ai_execution_id": ai_execution_id,
            "prompt_package_id": execution.prompt_package_id,
            "user_id": user_id,
            "resume_profile_id": gap_analysis.resume_profile_id if gap_analysis else None,
            "gap_analysis_id": package.gap_analysis_id,
            "status": ValidationStatus.VALIDATING.value,
        })
        self.db.commit()

        try:
            # 1. Schema Validation
            schema_valid, schema_score, schema_issues, schema_details = (
                self.schema_validator.validate(response_data, package.output_schema)
            )
            self._save_validation_report(
                validation.id, "schema", schema_valid, schema_score,
                schema_issues, schema_details
            )

            # 2. Truth Validation
            truth_valid, truth_score, truth_issues, truth_details = (
                self.truth_validator.validate(response_data, resume_knowledge)
            )
            self._save_validation_report(
                validation.id, "truth", truth_valid, truth_score,
                truth_issues, truth_details
            )

            # 3. Knowledge Validation
            knowledge_valid, knowledge_score, knowledge_issues, knowledge_details = (
                self.knowledge_validator.validate(response_data, knowledge_rules)
            )
            self._save_validation_report(
                validation.id, "knowledge", knowledge_valid, knowledge_score,
                knowledge_issues, knowledge_details
            )

            # 4. Gap Validation
            gap_valid, gap_score, gap_issues, gap_details = (
                self.gap_validator.validate(response_data, gap_analysis_data, gap_results)
            )
            self._save_validation_report(
                validation.id, "gap", gap_valid, gap_score,
                gap_issues, gap_details
            )

            # 5. Generate Diff
            original_data = self._build_original_data(resume_knowledge)
            diffs, diff_summary = self.diff_engine.generate_diff(original_data, response_data)

            # Save diffs
            if diffs:
                diff_records = [
                    {
                        "validation_id": validation.id,
                        "section": d.get("section", "unknown"),
                        "change_type": d.get("change_type", "modified"),
                        "original_value": d.get("original_value"),
                        "new_value": d.get("new_value"),
                        "field_path": d.get("field_path"),
                    }
                    for d in diffs
                ]
                self.diff_repo.create_many(diff_records)

            # 6. Classify Changes
            classified_changes = self.change_classifier.classify(diffs, gap_results)

            # Save change sets
            if classified_changes:
                change_records = [
                    {
                        "validation_id": validation.id,
                        "category": c.get("category", "unknown"),
                        "change_type": c.get("change_type", "modified"),
                        "description": c.get("description", ""),
                        "original_value": c.get("original_value"),
                        "new_value": c.get("new_value"),
                        "risk_level": c.get("risk_level", "medium"),
                        "supporting_rule_id": c.get("supporting_rule_id"),
                        "supporting_gap_id": c.get("supporting_gap_id"),
                    }
                    for c in classified_changes
                ]
                self.change_repo.create_many(change_records)

            # 7. Calculate Confidence
            validation_reports = {
                "schema_valid": schema_valid,
                "truth_valid": truth_valid,
                "knowledge_valid": knowledge_valid,
                "gap_valid": gap_valid,
            }
            confidence_scores = self.confidence_engine.calculate(
                classified_changes, validation_reports, knowledge_rules, gap_results
            )

            # Save confidence scores
            if confidence_scores:
                score_records = []
                for i, cs in enumerate(confidence_scores):
                    change_set = self.change_repo.get_by_validation_id(validation.id)
                    if i < len(change_set):
                        score_records.append({
                            "validation_id": validation.id,
                            "change_set_id": change_set[i].id,
                            "score": cs.get("score", 50),
                            "risk_level": cs.get("risk_level", "medium"),
                            "supporting_gap_id": cs.get("supporting_gap_id"),
                            "supporting_rule_id": cs.get("supporting_rule_id"),
                            "validation_result": cs.get("validation_result"),
                            "reason": json.dumps(cs.get("reasons", [])),
                        })
                if score_records:
                    self.confidence_repo.create_many(score_records)

            # 8. Build Approval Package
            approval_package = self.approval_builder.build(
                classified_changes,
                confidence_scores,
                validation_reports,
                knowledge_rules,
                gap_results,
                diff_summary,
            )

            # Calculate overall confidence
            overall_confidence = self.confidence_engine.calculate_overall_confidence(confidence_scores)

            # Determine overall validity
            is_valid = all([schema_valid, truth_valid, knowledge_valid, gap_valid])

            # Update validation record
            processing_time = int((time.time() - start_time) * 1000)
            self.validation_repo.update(validation.id, {
                "status": ValidationStatus.VALIDATED.value if is_valid else ValidationStatus.REJECTED.value,
                "is_approved": is_valid,
                "schema_valid": schema_valid,
                "truth_valid": truth_valid,
                "knowledge_valid": knowledge_valid,
                "gap_valid": gap_valid,
                "overall_confidence": overall_confidence,
                "total_changes": len(classified_changes),
                "approved_changes": len(approval_package.get("approved_changes", [])),
                "rejected_changes": len(approval_package.get("rejected_changes", [])),
                "warning_count": len(approval_package.get("warnings", [])),
                "processing_time_ms": processing_time,
            })
            self.db.commit()

            return {
                "validation_id": validation.id,
                "status": validation.status,
                "is_approved": is_valid,
                "overall_confidence": overall_confidence,
                "approval_package": approval_package,
                "processing_time_ms": processing_time,
            }

        except Exception as e:
            self.validation_repo.update(validation.id, {
                "status": ValidationStatus.FAILED.value,
                "error_message": str(e),
            })
            self.db.commit()
            raise

    def get_validation(self, validation_id: str) -> Optional[AIResponseValidation]:
        """Get a validation by ID."""
        return self.validation_repo.get_by_id(validation_id)

    def get_validations_by_user(
        self, user_id: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[AIResponseValidation], int]:
        """Get validations for a user."""
        return self.validation_repo.get_by_user_id(user_id, skip=skip, limit=limit)

    def get_validation_diffs(self, validation_id: str) -> List[ResumeDiff]:
        """Get diffs for a validation."""
        return self.diff_repo.get_by_validation_id(validation_id)

    def get_validation_report(self, validation_id: str) -> List[ValidationReport]:
        """Get validation reports."""
        return self.report_repo.get_by_validation_id(validation_id)

    def get_validation_confidence(self, validation_id: str) -> List[ConfidenceScore]:
        """Get confidence scores."""
        return self.confidence_repo.get_by_validation_id(validation_id)

    def get_validation_changes(self, validation_id: str) -> List[ChangeSet]:
        """Get change sets."""
        return self.change_repo.get_by_validation_id(validation_id)

    def _save_validation_report(
        self,
        validation_id: str,
        validator_name: str,
        is_valid: bool,
        score: float,
        issues: List[Dict[str, Any]],
        details: Dict[str, Any],
    ) -> None:
        """Save a validation report."""
        self.report_repo.create({
            "validation_id": validation_id,
            "validator_name": validator_name,
            "is_valid": is_valid,
            "score": score,
            "issues": issues,
            "details": details,
        })
        self.db.commit()

    def _build_original_data(self, resume_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Build original data structure for diff comparison."""
        return {
            "summary": resume_knowledge.get("summary", ""),
            "experience": resume_knowledge.get("experience_summary", []),
            "skills": resume_knowledge.get("skills", []),
            "education": resume_knowledge.get("education_summary", []),
            "certifications": resume_knowledge.get("certifications", []),
            "projects": resume_knowledge.get("projects", []),
            "achievements": resume_knowledge.get("achievements", []),
        }
