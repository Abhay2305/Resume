"""Tests for the Variable Interpolator.

Verifies safe substitution, required/optional variable validation,
nested context resolution, and error handling.
"""
import pytest

from app.services.prompt_intelligence_v2.interpolator import VariableInterpolator
from app.services.prompt_intelligence_v2.errors import MissingVariables


class TestVariableInterpolator:
    """Test the VariableInterpolator class."""

    def setup_method(self):
        self.interpolator = VariableInterpolator()

    # ------------------------------------------------------------------
    # Basic substitution
    # ------------------------------------------------------------------

    def test_single_variable_substitution(self):
        template = "Hello {name}"
        result = self.interpolator.interpolate(template, {"name": "Alice"})
        assert result == "Hello Alice"

    def test_multiple_variables_substitution(self):
        template = "{greeting} {name}, welcome to {place}"
        ctx = {"greeting": "Hi", "name": "Bob", "place": "Acme"}
        result = self.interpolator.interpolate(template, ctx)
        assert result == "Hi Bob, welcome to Acme"

    def test_no_placeholders(self):
        template = "No variables here"
        result = self.interpolator.interpolate(template, {})
        assert result == "No variables here"

    def test_empty_template(self):
        result = self.interpolator.interpolate("", {})
        assert result == ""

    def test_repeated_variable(self):
        template = "{name} is great. {name} really is."
        result = self.interpolator.interpolate(template, {"name": "X"})
        assert result == "X is great. X really is."

    # ------------------------------------------------------------------
    # Required variables
    # ------------------------------------------------------------------

    def test_required_variable_present(self):
        template = "{a} {b}"
        result = self.interpolator.interpolate(
            template, {"a": "1", "b": "2"}, required_variables=["a", "b"]
        )
        assert result == "1 2"

    def test_required_variable_missing_raises(self):
        template = "{a} {b}"
        with pytest.raises(MissingVariables) as exc_info:
            self.interpolator.interpolate(
                template, {"a": "1"}, required_variables=["a", "b"]
            )
        assert exc_info.value.missing == ["b"]

    def test_multiple_missing_required(self):
        template = "{a} {b} {c}"
        with pytest.raises(MissingVariables) as exc_info:
            self.interpolator.interpolate(
                template, {"a": "1"}, required_variables=["a", "b", "c"]
            )
        assert exc_info.value.missing == ["b", "c"]

    def test_required_not_in_context(self):
        template = "{x}"
        with pytest.raises(MissingVariables) as exc_info:
            self.interpolator.interpolate(template, {}, required_variables=["x"])
        assert exc_info.value.missing == ["x"]

    def test_required_and_optional_present(self):
        template = "{a} {b}"
        result = self.interpolator.interpolate(
            template, {"a": "1", "b": "2"},
            required_variables=["a"],
            optional_variables=["b"],
        )
        assert result == "1 2"

    # ------------------------------------------------------------------
    # Optional variables
    # ------------------------------------------------------------------

    def test_optional_variable_not_provided_defaults_empty(self):
        template = "{a} {b}"
        result = self.interpolator.interpolate(
            template, {"a": "1"},
            required_variables=["a"],
            optional_variables=["b"],
        )
        assert result == "1 "

    def test_optional_variable_provided(self):
        template = "{a} {b}"
        result = self.interpolator.interpolate(
            template, {"a": "1", "b": "2"},
            required_variables=["a"],
            optional_variables=["b"],
        )
        assert result == "1 2"

    def test_optional_not_in_template_no_effect(self):
        template = "{a}"
        result = self.interpolator.interpolate(
            template, {"a": "1"},
            required_variables=["a"],
            optional_variables=["extra"],
        )
        assert result == "1"

    def test_no_required_or_optional(self):
        template = "{a}"
        # Without required_variables, missing vars default to empty
        result = self.interpolator.interpolate(template, {})
        assert result == ""

    def test_optional_takes_priority_over_default(self):
        """If var is in both optional and provided, provided value wins."""
        template = "{a}"
        result = self.interpolator.interpolate(
            template, {"a": "provided"},
            optional_variables=["a"],
        )
        assert result == "provided"

    # ------------------------------------------------------------------
    # Nested context
    # ------------------------------------------------------------------

    def test_nested_context_single_level(self):
        template = "{resume.name}"
        ctx = {"resume": {"name": "Alice"}}
        result = self.interpolator.interpolate(template, ctx)
        assert result == "Alice"

    def test_nested_context_two_levels(self):
        template = "{resume.contact.email}"
        ctx = {"resume": {"contact": {"email": "a@b.com"}}}
        result = self.interpolator.interpolate(template, ctx)
        assert result == "a@b.com"

    def test_nested_context_missing_key(self):
        template = "{resume.missing}"
        ctx = {"resume": {"name": "X"}}
        result = self.interpolator.interpolate(template, ctx)
        assert result == ""

    def test_nested_context_missing_parent(self):
        template = "{other.key}"
        ctx = {"resume": {"name": "X"}}
        result = self.interpolator.interpolate(template, ctx)
        assert result == ""

    def test_nested_context_non_dict_parent(self):
        template = "{resume.length}"
        ctx = {"resume": "not a dict"}
        result = self.interpolator.interpolate(template, ctx)
        assert result == ""

    def test_nested_context_required_missing(self):
        template = "{resume.missing}"
        ctx = {"resume": {}}
        # resume exists but resume.missing does not → missing
        with pytest.raises(MissingVariables) as exc_info:
            self.interpolator.interpolate(
                template, ctx, required_variables=["resume.missing"]
            )
        assert exc_info.value.missing == ["resume.missing"]

    def test_nested_context_real_resume_example(self):
        """Simulates a real resume tailoring template."""
        template = "Skills: {resume.skills}, Experience: {resume.experience}"
        ctx = {
            "resume": {
                "skills": "Python, JavaScript",
                "experience": "5 years",
            }
        }
        result = self.interpolator.interpolate(template, ctx)
        assert result == "Skills: Python, JavaScript, Experience: 5 years"

    def test_mixed_flat_and_nested(self):
        template = "{name} works at {company.name}"
        ctx = {"name": "Alice", "company": {"name": "Acme"}}
        result = self.interpolator.interpolate(template, ctx)
        assert result == "Alice works at Acme"

    # ------------------------------------------------------------------
    # find_placeholders
    # ------------------------------------------------------------------

    def test_find_placeholders(self):
        template = "{a} {b} {a}"
        result = self.interpolator.find_placeholders(template)
        assert result == {"a", "b"}

    def test_find_placeholders_none(self):
        assert self.interpolator.find_placeholders("no vars") == set()

    def test_find_placeholders_nested(self):
        template = "{a.b} {c.d.e}"
        result = self.interpolator.find_placeholders(template)
        assert result == {"a.b", "c.d.e"}

    # ------------------------------------------------------------------
    # validate_template
    # ------------------------------------------------------------------

    def test_validate_template_all_declared(self):
        result = self.interpolator.validate_template(
            "{a} {b}", required_variables=["a"], optional_variables=["b"]
        )
        assert result["undeclared"] == []
        assert result["unused_required"] == []

    def test_validate_template_undeclared(self):
        result = self.interpolator.validate_template(
            "{a} {b} {c}",
            required_variables=["a"],
            optional_variables=["b"],
        )
        assert result["undeclared"] == ["c"]
        assert result["placeholders"] == ["a", "b", "c"]

    def test_validate_template_unused_required(self):
        result = self.interpolator.validate_template(
            "{a}",
            required_variables=["a", "b"],
        )
        assert result["unused_required"] == ["b"]

    def test_validate_template_empty(self):
        result = self.interpolator.validate_template("")
        assert result["placeholders"] == []
        assert result["undeclared"] == []
        assert result["unused_required"] == []

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_none_values_render_as_empty(self):
        template = "{a}"
        result = self.interpolator.interpolate(template, {"a": None})
        assert result == ""

    def test_int_values_rendered(self):
        template = "{count}"
        result = self.interpolator.interpolate(template, {"count": 42})
        assert result == "42"

    def test_bool_values_rendered(self):
        template = "{flag}"
        result = self.interpolator.interpolate(template, {"flag": True})
        assert result == "True"

    def test_list_values_rendered(self):
        template = "{items}"
        result = self.interpolator.interpolate(template, {"items": [1, 2, 3]})
        assert result == "[1, 2, 3]"

    def test_prompt_type_in_error(self):
        with pytest.raises(MissingVariables) as exc_info:
            self.interpolator.interpolate(
                "{x}", {}, required_variables=["x"], prompt_type="resume_bullets"
            )
        assert exc_info.value.prompt_type == "resume_bullets"

    def test_interpolation_with_actual_resume_bullets_template(self):
        """Verify interpolator works with a real template from prompt_builder."""
        from app.services.prompt_intelligence_v2.templates import PromptTemplates

        t = PromptTemplates()
        user = t.get_user("resume_bullets")
        ctx = {
            "role_title": "Software Engineer",
            "company": "Acme",
            "duration": "2020-2023",
            "responsibilities": "Built stuff",
            "technologies": "Python, JS",
            "achievements": "Shipped product",
            "num_bullets": "5",
        }
        result = self.interpolator.interpolate(user, ctx)
        assert "Acme" in result
        assert "Software Engineer" in result
        # No remaining placeholders
        assert "{" not in result
