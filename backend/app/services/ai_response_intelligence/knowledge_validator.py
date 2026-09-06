"""Knowledge Validator.

Verifies that AI follows governed knowledge rules.
Every recommendation must be backed by at least one Knowledge Rule.
"""
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Default weak verbs — used only when DB is unavailable
_WEAK_VERBS_DEFAULT = ["responsible for", "helped", "assisted", "worked on", "involved in"]

# Default technical keywords — used only when DB is unavailable
_TECH_KEYWORDS_DEFAULT = [
    "python", "javascript", "java", "sql", "aws", "docker", "react", "node",
    "typescript", "angular", "kubernetes", "gcp", "azure", "redis", "postgresql",
    "mongodb", "api", "rest", "graphql", "microservice", "ci/cd", "git", "linux",
    "cloud", "machine learning", "tensorflow", "pytorch", "spark", "hadoop",
]


def _load_weak_verbs_from_db() -> Optional[List[str]]:
    """Load weak verbs from KnowledgeRule DB (INT_VER_002)."""
    try:
        from app.database import SessionLocal
        from app.repositories.knowledge_intelligence import KnowledgeRuleRepository
        db = SessionLocal()
        try:
            repo = KnowledgeRuleRepository(db)
            rule = repo.get_by_key("INT_VER_002")
            if rule and rule.examples:
                examples = rule.examples
                if isinstance(examples, str):
                    examples = json.loads(examples)
                if isinstance(examples, list) and examples:
                    return examples
        finally:
            db.close()
    except Exception as e:
        logger.debug("Failed to load weak verbs from DB: %s", e)
    return None


def _load_tech_keywords_from_db() -> Optional[List[str]]:
    """Load technical keywords from KnowledgeRule DB (INT_TECH_001)."""
    try:
        from app.database import SessionLocal
        from app.repositories.knowledge_intelligence import KnowledgeRuleRepository
        db = SessionLocal()
        try:
            repo = KnowledgeRuleRepository(db)
            rule = repo.get_by_key("INT_TECH_001")
            if rule and rule.examples:
                examples = rule.examples
                if isinstance(examples, str):
                    examples = json.loads(examples)
                if isinstance(examples, list) and examples:
                    return examples
        finally:
            db.close()
    except Exception as e:
        logger.debug("Failed to load tech keywords from DB: %s", e)
    return None


class KnowledgeValidator:
    """Validates AI response against knowledge rules.

    Ensures AI recommendations are backed by established knowledge rules
    from Harvard, MIT, Yale, ATS, and Internal sources.
    """

    def validate(
        self,
        response_data: Dict[str, Any],
        knowledge_rules: List[Dict[str, Any]],
    ) -> Tuple[bool, float, List[Dict[str, Any]], Dict[str, Any]]:
        """Validate AI response against knowledge rules.

        Args:
            response_data: The parsed AI response.
            knowledge_rules: List of knowledge rules to validate against.

        Returns:
            Tuple of (is_valid, score, issues, details).
        """
        issues = []
        details = {}
        score = 100.0

        if not response_data:
            return False, 0.0, [{"type": "empty_response", "message": "No response to validate"}], {}

        if not knowledge_rules:
            return True, 60.0, [{"type": "no_rules", "message": "No knowledge rules available"}], {}

        # Check summary follows rules
        summary_issues = self._validate_summary_rules(response_data, knowledge_rules)
        issues.extend(summary_issues)
        score -= len(summary_issues) * 5.0

        # Check experience follows rules
        experience_issues = self._validate_experience_rules(response_data, knowledge_rules)
        issues.extend(experience_issues)
        score -= len(experience_issues) * 5.0

        # Check skills follow rules
        skills_issues = self._validate_skills_rules(response_data, knowledge_rules)
        issues.extend(skills_issues)
        score -= len(skills_issues) * 3.0

        # Check formatting follows rules
        formatting_issues = self._validate_formatting_rules(response_data, knowledge_rules)
        issues.extend(formatting_issues)
        score -= len(formatting_issues) * 2.0

        # Check ATS compliance
        ats_issues = self._validate_ats_rules(response_data, knowledge_rules)
        issues.extend(ats_issues)
        score -= len(ats_issues) * 4.0

        # Verify each change has supporting rule
        unsupported_issues = self._verify_rule_coverage(response_data, knowledge_rules)
        issues.extend(unsupported_issues)
        score -= len(unsupported_issues) * 3.0

        score = max(0.0, min(100.0, score))
        is_valid = score >= 40.0

        details["total_issues"] = len(issues)
        details["rules_checked"] = len(knowledge_rules)
        details["categories_violated"] = list(set(i.get("category", "unknown") for i in issues))

        return is_valid, score, issues, details

    def _validate_summary_rules(
        self, response: Dict[str, Any], rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate summary against knowledge rules."""
        issues = []
        summary = response.get("summary", "")

        if not summary:
            return issues

        summary_rules = [r for r in rules if r.get("section_name") == "summary"]

        for rule in summary_rules:
            instruction = rule.get("instruction", "").lower()

            if "no first person" in instruction or "avoid i" in instruction:
                if " i " in summary.lower() or summary.lower().startswith("i "):
                    issues.append({
                        "type": "rule_violation",
                        "category": "summary",
                        "rule_id": rule.get("rule_key"),
                        "source": rule.get("source"),
                        "message": f"Summary violates rule: {rule.get('instruction')}",
                    })

            if "quantify" in instruction or "metrics" in instruction:
                import re
                if not re.search(r'\d+', summary):
                    issues.append({
                        "type": "rule_violation",
                        "category": "summary",
                        "rule_id": rule.get("rule_key"),
                        "source": rule.get("source"),
                        "message": f"Summary lacks quantified achievements per rule",
                    })

        return issues

    def _validate_experience_rules(
        self, response: Dict[str, Any], rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate experience against knowledge rules."""
        issues = []
        experience = response.get("experience", [])

        if not isinstance(experience, list):
            return issues

        exp_rules = [r for r in rules if r.get("section_name") == "experience"]

        for rule in exp_rules:
            instruction = rule.get("instruction", "").lower()

            if "action verb" in instruction or "strong verb" in instruction:
                weak_verbs = _load_weak_verbs_from_db() or _WEAK_VERBS_DEFAULT
                for i, entry in enumerate(experience):
                    if not isinstance(entry, dict):
                        continue
                    description = entry.get("description", [])
                    if not isinstance(description, list):
                        continue
                    for bullet in description:
                        if isinstance(bullet, str):
                            for weak_verb in weak_verbs:
                                if bullet.lower().startswith(weak_verb):
                                    issues.append({
                                        "type": "rule_violation",
                                        "category": "experience",
                                        "rule_id": rule.get("rule_key"),
                                        "source": rule.get("source"),
                                        "entry_index": i,
                                        "message": f"Experience entry uses weak verb: '{weak_verb}'",
                                    })

            if "quantify" in instruction or "metrics" in instruction:
                for i, entry in enumerate(experience):
                    if not isinstance(entry, dict):
                        continue
                    description = entry.get("description", [])
                    if not isinstance(description, list):
                        continue
                    has_metrics = any(
                        isinstance(b, str) and any(c.isdigit() for c in b)
                        for b in description
                    )
                    if not has_metrics and description:
                        issues.append({
                            "type": "rule_violation",
                            "category": "experience",
                            "rule_id": rule.get("rule_key"),
                            "source": rule.get("source"),
                            "entry_index": i,
                            "message": f"Experience entry lacks quantified achievements",
                        })

        return issues

    def _validate_skills_rules(
        self, response: Dict[str, Any], rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate skills against knowledge rules.

        Checks:
        - Skills section exists when rules require it
        - Skills are grouped by category when required
        - Technical skills are included when required
        - Skills match job-relevant keywords when available
        """
        issues = []
        skills = response.get("skills", [])

        if not isinstance(skills, list):
            return issues

        skills_rules = [r for r in rules if r.get("section_name") == "skills"]

        for rule in skills_rules:
            instruction = rule.get("instruction", "").lower()

            # Check: skills should not be empty if rules require them
            if ("include" in instruction or "list" in instruction) and not skills:
                issues.append({
                    "type": "rule_violation",
                    "category": "skills",
                    "rule_id": rule.get("rule_key"),
                    "source": rule.get("source"),
                    "message": f"Skills section is empty but rule requires skills: {rule.get('instruction')}",
                })

            # Check: skills should be grouped by category
            if "group" in instruction and "category" in instruction:
                has_grouping = any(
                    isinstance(s, dict) and "category" in s
                    for s in skills
                )
                if skills and not has_grouping:
                    issues.append({
                        "type": "rule_violation",
                        "category": "skills",
                        "rule_id": rule.get("rule_key"),
                        "source": rule.get("source"),
                        "message": "Skills should be grouped by category per rule",
                    })

            # Check: technical skills should be included
            if "technical" in instruction:
                technical_keywords = _load_tech_keywords_from_db() or _TECH_KEYWORDS_DEFAULT
                has_technical = any(
                    isinstance(s, str) and any(kw in s.lower() for kw in technical_keywords)
                    for s in skills
                )
                if skills and not has_technical:
                    issues.append({
                        "type": "rule_violation",
                        "category": "skills",
                        "rule_id": rule.get("rule_key"),
                        "source": rule.get("source"),
                        "message": "No technical skills found in skills section",
                    })

            # Check: skills should include relevant job keywords
            if "relevant" in instruction and "job" in instruction:
                if not skills:
                    issues.append({
                        "type": "rule_violation",
                        "category": "skills",
                        "rule_id": rule.get("rule_key"),
                        "source": rule.get("source"),
                        "message": "Skills section is empty - cannot validate job relevance",
                    })

            # Check: skills should not be too long
            if "concise" in instruction or "brief" in instruction:
                if len(skills) > 20:
                    issues.append({
                        "type": "rule_violation",
                        "category": "skills",
                        "rule_id": rule.get("rule_key"),
                        "source": rule.get("source"),
                        "message": f"Skills section has {len(skills)} items - should be more concise",
                    })

        return issues

    def _validate_formatting_rules(
        self, response: Dict[str, Any], rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate formatting against knowledge rules."""
        issues = []
        formatting_rules = [r for r in rules if r.get("section_name") == "formatting"]

        for rule in formatting_rules:
            instruction = rule.get("instruction", "").lower()

            if "consistent" in instruction:
                # Check for consistent date formats
                experience = response.get("experience", [])
                if isinstance(experience, list):
                    date_formats = set()
                    import re
                    for entry in experience:
                        if isinstance(entry, dict):
                            for date_field in ["startDate", "endDate"]:
                                date_val = entry.get(date_field, "")
                                if date_val:
                                    if re.match(r'\d{4}-\d{2}', str(date_val)):
                                        date_formats.add("iso")
                                    elif re.match(r'\w+ \d{4}', str(date_val)):
                                        date_formats.add("text")
                    if len(date_formats) > 1:
                        issues.append({
                            "type": "rule_violation",
                            "category": "formatting",
                            "rule_id": rule.get("rule_key"),
                            "source": rule.get("source"),
                            "message": "Inconsistent date formats detected",
                        })

        return issues

    def _validate_ats_rules(
        self, response: Dict[str, Any], rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate ATS compliance.

        Checks that keywords from the job description appear naturally
        in the resume content (summary and experience).
        """
        issues = []
        ats_rules = [r for r in rules if r.get("section_name") == "ats"]

        for rule in ats_rules:
            instruction = rule.get("instruction", "").lower()

            if "keyword" in instruction and "natural" in instruction:
                skills = response.get("skills", [])
                summary = response.get("summary", "")
                if isinstance(skills, list) and summary:
                    missing_from_summary = []
                    for skill in skills:
                        if isinstance(skill, str) and skill.lower() not in summary.lower():
                            missing_from_summary.append(skill)
                    if missing_from_summary and len(missing_from_summary) > len(skills) * 0.5:
                        issues.append({
                            "type": "ats_keyword_gap",
                            "category": "ats",
                            "rule_id": rule.get("rule_key"),
                            "source": rule.get("source"),
                            "message": f"Most skills ({len(missing_from_summary)}/{len(skills)}) not mentioned in summary — ATS may miss keywords",
                            "severity": "warning",
                        })

            if "format" in instruction and "keyword" in instruction:
                experience = response.get("experience", [])
                skills = response.get("skills", [])
                if isinstance(experience, list) and isinstance(skills, list):
                    exp_text = " ".join(
                        str(e.get("description", "")) + " " + str(e.get("bullets", ""))
                        for e in experience if isinstance(e, dict)
                    ).lower()
                    missing_in_exp = [s for s in skills if isinstance(s, str) and s.lower() not in exp_text]
                    if missing_in_exp and len(missing_in_exp) > len(skills) * 0.7:
                        issues.append({
                            "type": "ats_keyword_gap",
                            "category": "ats",
                            "rule_id": rule.get("rule_key"),
                            "source": rule.get("source"),
                            "message": f"Most skills ({len(missing_in_exp)}/{len(skills)}) not mentioned in experience — ATS may miss keywords",
                            "severity": "warning",
                        })

        return issues

    def _verify_rule_coverage(
        self, response: Dict[str, Any], rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Verify that changes have supporting knowledge rules.

        Checks:
        - Each modified section has at least one supporting rule
        - No section is modified without relevant rules
        - Summary changes have backing rules
        - Experience changes have backing rules
        - Skills changes have backing rules
        """
        issues = []

        # Build rule coverage map by section
        rules_by_section = {}
        for rule in rules:
            section = rule.get("section_name", "")
            if section:
                rules_by_section.setdefault(section, []).append(rule)

        # Check summary coverage
        summary = response.get("summary", "")
        if summary:
            summary_rules = rules_by_section.get("summary", [])
            if not summary_rules:
                issues.append({
                    "type": "unsupported_change",
                    "category": "summary",
                    "message": "Summary was modified but no summary rules available",
                })

        # Check experience coverage
        experience = response.get("experience", [])
        if isinstance(experience, list) and experience:
            exp_rules = rules_by_section.get("experience", [])
            if not exp_rules:
                issues.append({
                    "type": "unsupported_change",
                    "category": "experience",
                    "message": "Experience was modified but no experience rules available",
                })

        # Check skills coverage
        skills = response.get("skills", [])
        if isinstance(skills, list) and skills:
            skills_rules = rules_by_section.get("skills", [])
            if not skills_rules:
                issues.append({
                    "type": "unsupported_change",
                    "category": "skills",
                    "message": "Skills were modified but no skills rules available",
                })

        # Check education coverage
        education = response.get("education", [])
        if isinstance(education, list) and education:
            edu_rules = rules_by_section.get("education", [])
            if not edu_rules:
                issues.append({
                    "type": "unsupported_change",
                    "category": "education",
                    "message": "Education was modified but no education rules available",
                })

        return issues
