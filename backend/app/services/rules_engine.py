"""Rules Engine for resume and cover letter validation.

Validates AI-generated content against curated writing rules.
The Rules Engine is separate from the LLM - it validates, not generates.
Vocabulary lists are loaded from the KnowledgeRule DB at initialization.
Hardcoded sets serve as explicitly authorized DEFAULT_FALLBACK only.
"""
import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class Severity(str, Enum):
    """Rule violation severity levels."""
    ERROR = "error"  # Must fix, blocks saving
    WARNING = "warning"  # Should fix, allows saving
    INFO = "info"  # Suggestion, optional


class RuleCategory(str, Enum):
    """Rule categories."""
    ACTION_VERB = "action_verb"
    TECHNICAL = "technical"
    QUANTIFICATION = "quantification"
    ATS = "ats"
    STYLE = "style"
    CONTENT = "content"
    STRUCTURE = "structure"


@dataclass
class RuleViolation:
    """A single rule violation."""
    rule_name: str
    category: RuleCategory
    severity: Severity
    message: str
    field_path: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Aggregated validation result."""
    is_valid: bool
    violations: List[RuleViolation] = field(default_factory=list)
    score: float = 100.0
    passed_rules: int = 0
    failed_rules: int = 0

    def add_violation(self, violation: RuleViolation):
        self.violations.append(violation)
        if violation.severity == Severity.ERROR:
            self.is_valid = False
            self.score -= 10
        elif violation.severity == Severity.WARNING:
            self.score -= 3
        else:
            self.score -= 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "score": max(0, self.score),
            "violations": [
                {
                    "rule": v.rule_name,
                    "category": v.category.value,
                    "severity": v.severity.value,
                    "message": v.message,
                    "field": v.field_path,
                    "suggestion": v.suggestion,
                }
                for v in self.violations
            ],
            "passed_rules": self.passed_rules,
            "failed_rules": self.failed_rules,
        }


# ── DEFAULT FALLBACK vocabulary (explicitly authorized in SHADOW-1 spec) ──
# Used only when DB is unavailable. Not an independent authority.
STRONG_ACTION_VERBS_DEFAULT: Set[str] = {
    "developed", "implemented", "designed", "architected", "built", "created",
    "optimized", "reduced", "increased", "improved", "enhanced", "streamlined",
    "automated", "engineered", "deployed", "migrated", "refactored", "scaled",
    "led", "managed", "directed", "coordinated", "supervised", "mentored",
    "analyzed", "evaluated", "assessed", "identified", "resolved", "diagnosed",
    "configured", "integrated", "established", "launched", "delivered", "shipped",
    "orchestrated", "spearheaded", "pioneered", "championed", "facilitated",
    "eliminated", "minimized", "maximized", "accelerated",
    "authored", "documented", "presented", "collaborated", "partnered",
    "researched", "investigated", "explored", "discovered", "validated",
}

WEAK_VERBS_DEFAULT: Set[str] = {
    "helped", "worked", "was", "had", "did", "made", "got", "used",
    "responsible for", "tasked with", "involved in", "participated in",
    "assisted with", "contributed to", "supported", "handled",
}

VAGUE_PHRASES_DEFAULT: Set[str] = {
    "team player", "self-starter", "go-getter", "results-driven",
    "detail-oriented", "problem solver", "critical thinker",
    "excellent communication", "strong work ethic", "fast learner",
    "passionate", "dedicated", "motivated", "enthusiastic",
    "synergy", "leverage", "ecosystem", "paradigm",
}

GENERIC_PHRASES_DEFAULT: Set[str] = {
    "various tasks", "multiple projects", "different areas",
    "many responsibilities", "several initiatives", "diverse projects",
    "wide range", "broad experience", "extensive knowledge",
}

# Legacy aliases for backward compatibility
STRONG_ACTION_VERBS = STRONG_ACTION_VERBS_DEFAULT
WEAK_VERBS = WEAK_VERBS_DEFAULT
VAGUE_PHRASES = VAGUE_PHRASES_DEFAULT
GENERIC_PHRASES = GENERIC_PHRASES_DEFAULT


class Rule:
    """A single validation rule."""

    def __init__(
        self,
        name: str,
        category: RuleCategory,
        severity: Severity,
        check_fn: Callable[..., Optional[RuleViolation]],
        description: str = "",
    ):
        self.name = name
        self.category = category
        self.severity = severity
        self.check_fn = check_fn
        self.description = description

    def check(self, *args, **kwargs) -> Optional[RuleViolation]:
        return self.check_fn(*args, **kwargs)


class RulesEngine:
    """Modular and extensible rules engine for resume validation.

    Vocabulary lists (strong verbs, weak verbs, vague phrases, generic phrases)
    are loaded from the KnowledgeRule DB at initialization. If DB is unavailable,
    explicitly authorized DEFAULT_FALLBACK sets are used.

    Usage:
        engine = RulesEngine()
        result = engine.validate_bullet("Built a system that improved performance")
        result = engine.validate_resume(resume_data)
    """

    def __init__(self, db_session=None):
        self.rules: List[Rule] = []
        self._db_session = db_session
        # Start with explicitly authorized defaults
        self.strong_action_verbs: Set[str] = STRONG_ACTION_VERBS_DEFAULT.copy()
        self.weak_verbs: Set[str] = WEAK_VERBS_DEFAULT.copy()
        self.vague_phrases: Set[str] = VAGUE_PHRASES_DEFAULT.copy()
        self.generic_phrases: Set[str] = GENERIC_PHRASES_DEFAULT.copy()

        # Load from DB if session provided
        if db_session:
            try:
                self._load_vocabulary_from_db(db_session)
            except Exception:
                logger.warning("RulesEngine: Failed to load vocabulary from DB, using defaults")

        self._register_default_rules()

    def _load_vocabulary_from_db(self, db_session):
        """Load vocabulary lists from KnowledgeRule database."""
        from app.models.knowledge_intelligence import KnowledgeRule

        vocabulary_map = {
            "INT_VER_001": "strong_action_verbs",
            "INT_VER_002": "weak_verbs",
            "INT_PHR_001": "vague_phrases",
            "INT_PHR_002": "generic_phrases",
        }

        loaded_any = False
        for rule_key, attr_name in vocabulary_map.items():
            rule = db_session.query(KnowledgeRule).filter(
                KnowledgeRule.rule_key == rule_key,
                KnowledgeRule.state == "ACTIVE",
                KnowledgeRule.is_active == True,
            ).first()
            if rule and rule.examples:
                try:
                    examples = json.loads(rule.examples) if isinstance(rule.examples, str) else rule.examples
                    setattr(self, attr_name, set(examples))
                    loaded_any = True
                except (json.JSONDecodeError, TypeError):
                    logger.warning("RulesEngine: Failed to parse examples for %s", rule_key)

        if loaded_any:
            logger.info("RulesEngine: Vocabulary loaded from DB")
        else:
            logger.warning("RulesEngine: No vocabulary rules found in DB, using defaults")

    def _register_default_rules(self):
        """Register all default validation rules."""
        # Action verb rules
        self.add_rule(Rule(
            name="bullet_starts_with_verb",
            category=RuleCategory.ACTION_VERB,
            severity=Severity.ERROR,
            check_fn=self._check_bullet_starts_with_verb,
            description="Every bullet must start with a strong action verb",
        ))
        self.add_rule(Rule(
            name="no_weak_verbs",
            category=RuleCategory.ACTION_VERB,
            severity=Severity.WARNING,
            check_fn=self._check_no_weak_verbs,
            description="Avoid weak verbs like 'helped', 'worked', 'responsible for'",
        ))

        # Technical rules
        self.add_rule(Rule(
            name="mentions_technology",
            category=RuleCategory.TECHNICAL,
            severity=Severity.WARNING,
            check_fn=self._check_mentions_technology,
            description="Technology stack should be mentioned when applicable",
        ))

        # Quantification rules
        self.add_rule(Rule(
            name="has_quantifiable_impact",
            category=RuleCategory.QUANTIFICATION,
            severity=Severity.WARNING,
            check_fn=self._check_has_quantifiable_impact,
            description="Quantifiable impact should be included when possible",
        ))

        # Style rules
        self.add_rule(Rule(
            name="no_vague_phrases",
            category=RuleCategory.STYLE,
            severity=Severity.WARNING,
            check_fn=self._check_no_vague_phrases,
            description="Avoid vague or marketing-style statements",
        ))
        self.add_rule(Rule(
            name="no_generic_phrases",
            category=RuleCategory.STYLE,
            severity=Severity.WARNING,
            check_fn=self._check_no_generic_phrases,
            description="Avoid generic phrases like 'various tasks'",
        ))
        self.add_rule(Rule(
            name="bullet_concise",
            category=RuleCategory.STYLE,
            severity=Severity.WARNING,
            check_fn=self._check_bullet_concise,
            description="Bullets should be concise (under 2 lines ideally)",
        ))

        # ATS rules
        self.add_rule(Rule(
            name="no_special_characters",
            category=RuleCategory.ATS,
            severity=Severity.WARNING,
            check_fn=self._check_no_special_characters,
            description="Avoid special characters that ATS cannot parse",
        ))

        # Structure rules
        self.add_rule(Rule(
            name="no_first_person",
            category=RuleCategory.STRUCTURE,
            severity=Severity.WARNING,
            check_fn=self._check_no_first_person,
            description="Avoid first-person pronouns in resume bullets",
        ))

    def add_rule(self, rule: Rule):
        """Add a custom rule to the engine."""
        self.rules.append(rule)

    def remove_rule(self, rule_name: str):
        """Remove a rule by name."""
        self.rules = [r for r in self.rules if r.name != rule_name]

    def validate_bullet(self, bullet: str) -> ValidationResult:
        """Validate a single bullet point."""
        result = ValidationResult(is_valid=True)
        for rule in self.rules:
            violation = rule.check(bullet=bullet)
            if violation:
                result.add_violation(violation)
                result.failed_rules += 1
            else:
                result.passed_rules += 1
        result.score = max(0, min(100, result.score))
        return result

    def validate_bullets(self, bullets: List[str]) -> ValidationResult:
        """Validate multiple bullet points."""
        result = ValidationResult(is_valid=True)
        for i, bullet in enumerate(bullets):
            bullet_result = self.validate_bullet(bullet)
            for v in bullet_result.violations:
                v.field_path = f"bullets[{i}]"
                result.add_violation(v)
            result.passed_rules += bullet_result.passed_rules
            result.failed_rules += bullet_result.failed_rules
        result.score = max(0, min(100, result.score))
        return result

    def validate_resume(self, resume_data: Dict[str, Any]) -> ValidationResult:
        """Validate a complete resume structure."""
        result = ValidationResult(is_valid=True)

        # Check required sections
        required_sections = ["summary", "experience", "education", "skills"]
        for section in required_sections:
            if section not in resume_data or not resume_data[section]:
                result.add_violation(RuleViolation(
                    rule_name=f"has_{section}",
                    category=RuleCategory.STRUCTURE,
                    severity=Severity.ERROR,
                    message=f"Resume missing required section: {section}",
                    field_path=section,
                ))

        # Validate experience bullets
        if "experience" in resume_data and resume_data["experience"]:
            for i, exp in enumerate(resume_data["experience"]):
                if "bullets" in exp and exp["bullets"]:
                    bullets_result = self.validate_bullets(exp["bullets"])
                    for v in bullets_result.violations:
                        v.field_path = f"experience[{i}].bullets"
                        result.add_violation(v)
                    result.passed_rules += bullets_result.passed_rules
                    result.failed_rules += bullets_result.failed_rules

        # Validate summary
        if "summary" in resume_data and resume_data["summary"]:
            summary_result = self._validate_summary(resume_data["summary"])
            for v in summary_result.violations:
                v.field_path = "summary"
                result.add_violation(v)
            result.passed_rules += summary_result.passed_rules
            result.failed_rules += summary_result.failed_rules

        result.score = max(0, min(100, result.score))
        return result

    def _validate_summary(self, summary: str) -> ValidationResult:
        """Validate professional summary."""
        result = ValidationResult(is_valid=True)

        # Check length
        if len(summary) > 500:
            result.add_violation(RuleViolation(
                rule_name="summary_concise",
                category=RuleCategory.STYLE,
                severity=Severity.WARNING,
                message="Summary should be under 3-4 sentences",
                suggestion="Keep summary concise and impactful",
            ))

        # Check for first person
        first_person_check = self._check_no_first_person(bullet=summary)
        if first_person_check:
            result.add_violation(first_person_check)

        return result

    # -----------------------------------------------------------------------
    # Rule check implementations
    # -----------------------------------------------------------------------

    def _check_bullet_starts_with_verb(self, bullet: str) -> Optional[RuleViolation]:
        """Check if bullet starts with a strong action verb."""
        first_word = bullet.strip().split()[0].lower().rstrip(",.:;!?") if bullet.strip() else ""
        if first_word not in self.strong_action_verbs:
            return RuleViolation(
                rule_name="bullet_starts_with_verb",
                category=RuleCategory.ACTION_VERB,
                severity=Severity.ERROR,
                message=f"Bullet should start with a strong action verb, got '{first_word}'",
                suggestion=f"Start with a verb like: developed, implemented, designed, led",
            )
        return None

    def _check_no_weak_verbs(self, bullet: str) -> Optional[RuleViolation]:
        """Check for weak verbs."""
        bullet_lower = bullet.lower()
        for weak in self.weak_verbs:
            if weak in bullet_lower:
                return RuleViolation(
                    rule_name="no_weak_verbs",
                    category=RuleCategory.ACTION_VERB,
                    severity=Severity.WARNING,
                    message=f"Contains weak phrasing: '{weak}'",
                    suggestion="Replace with a specific action verb",
                )
        return None

    def _check_mentions_technology(self, bullet: str) -> Optional[RuleViolation]:
        """Check if technology is mentioned."""
        # Default tech indicators — used only when DB is unavailable
        tech_indicators_default = [
            "python", "java", "javascript", "typescript", "react", "angular",
            "node", "aws", "azure", "gcp", "docker", "kubernetes", "sql",
            "nosql", "redis", "postgresql", "mongodb", "api", "rest",
            "graphql", "microservice", "ci/cd", "git", "linux", "cloud",
            "machine learning", "tensorflow", "pytorch", "spark", "hadoop",
            "xgboost", "scikit", "pandas", "numpy", "fastapi", "django",
            "flask", "spring", "rails", "go", "rust", "c++", "scala",
        ]

        # Try loading from DB first
        tech_indicators = self._load_tech_indicators_from_db() or tech_indicators_default

        bullet_lower = bullet.lower()
        has_tech = any(tech in bullet_lower for tech in tech_indicators)
        if not has_tech:
            return RuleViolation(
                rule_name="mentions_technology",
                category=RuleCategory.TECHNICAL,
                severity=Severity.WARNING,
                message="No technology stack mentioned",
                suggestion="Include relevant technologies used",
            )
        return None

    def _load_tech_indicators_from_db(self) -> Optional[List[str]]:
        """Load tech indicators from KnowledgeRule DB (INT_TECH_001)."""
        try:
            if not self._db_session:
                return None
            from app.repositories.knowledge_intelligence import KnowledgeRuleRepository
            repo = KnowledgeRuleRepository(self._db_session)
            rule = repo.get_by_key("INT_TECH_001")
            if rule and rule.examples:
                examples = rule.examples
                if isinstance(examples, str):
                    import json
                    examples = json.loads(examples)
                if isinstance(examples, list) and examples:
                    return examples
        except Exception:
            pass
        return None

    def _check_has_quantifiable_impact(self, bullet: str) -> Optional[RuleViolation]:
        """Check if quantifiable impact is included."""
        impact_patterns = [
            r"\d+%",  # Percentages
            r"\$\d+",  # Dollar amounts
            r"\d+x",  # Multipliers
            r"\d+ [kmb]?",  # Numbers with optional suffix
            r"reduced by", r"increased by", r"improved by",
            r"saved", r"generated", r"processed", r"handled",
            r"users", r"requests", r"transactions", r"records",
        ]
        has_impact = any(re.search(p, bullet.lower()) for p in impact_patterns)
        if not has_impact:
            return RuleViolation(
                rule_name="has_quantifiable_impact",
                category=RuleCategory.QUANTIFICATION,
                severity=Severity.WARNING,
                message="No quantifiable impact detected",
                suggestion="Add metrics: percentages, dollar amounts, user counts, etc.",
            )
        return None

    def _check_no_vague_phrases(self, bullet: str) -> Optional[RuleViolation]:
        """Check for vague or marketing-style phrases."""
        bullet_lower = bullet.lower()
        for phrase in self.vague_phrases:
            if phrase in bullet_lower:
                return RuleViolation(
                    rule_name="no_vague_phrases",
                    category=RuleCategory.STYLE,
                    severity=Severity.WARNING,
                    message=f"Contains vague phrase: '{phrase}'",
                    suggestion="Replace with specific, measurable achievement",
                )
        return None

    def _check_no_generic_phrases(self, bullet: str) -> Optional[RuleViolation]:
        """Check for generic phrases."""
        bullet_lower = bullet.lower()
        for phrase in self.generic_phrases:
            if phrase in bullet_lower:
                return RuleViolation(
                    rule_name="no_generic_phrases",
                    category=RuleCategory.STYLE,
                    severity=Severity.WARNING,
                    message=f"Contains generic phrase: '{phrase}'",
                    suggestion="Be specific about what was done",
                )
        return None

    def _check_bullet_concise(self, bullet: str) -> Optional[RuleViolation]:
        """Check if bullet is concise."""
        if len(bullet) > 200:
            return RuleViolation(
                rule_name="bullet_concise",
                category=RuleCategory.STYLE,
                severity=Severity.WARNING,
                message=f"Bullet is too long ({len(bullet)} chars)",
                suggestion="Keep bullets under 2 lines, focus on key achievements",
            )
        return None

    def _check_no_special_characters(self, bullet: str) -> Optional[RuleViolation]:
        """Check for special characters that ATS cannot parse."""
        special_chars = r"[|\\{}<>]"
        if re.search(special_chars, bullet):
            return RuleViolation(
                rule_name="no_special_characters",
                category=RuleCategory.ATS,
                severity=Severity.WARNING,
                message="Contains special characters that may break ATS parsing",
                suggestion="Remove special characters: |, \\, {}, <, >",
            )
        return None

    def _check_no_first_person(self, bullet: str) -> Optional[RuleViolation]:
        """Check for first-person pronouns."""
        first_person = ["i ", "i' ", "my ", "me ", "we ", "our ", "us "]
        bullet_lower = bullet.lower()
        for pronoun in first_person:
            if bullet_lower.startswith(pronoun) or f" {pronoun}" in bullet_lower:
                return RuleViolation(
                    rule_name="no_first_person",
                    category=RuleCategory.STRUCTURE,
                    severity=Severity.WARNING,
                    message=f"Contains first-person pronoun: '{pronoun.strip()}'",
                    suggestion="Remove pronouns, start directly with action verb",
                )
        return None
