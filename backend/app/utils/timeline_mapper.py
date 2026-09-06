"""Timeline event mapper.

Centralizes the mapping from AuditLog entries to timeline event DTOs.
Keeps the router thin and the mapping logic reusable.
"""
from typing import Any, Dict, Optional

from ..models.audit import AuditLog


# ---------------------------------------------------------------------------
# Action + entity_type → human-readable title, icon, severity
# ---------------------------------------------------------------------------

_EVENT_MAP: Dict[tuple, Dict[str, str]] = {
    # Auth events
    ("login", "admin_auth"):           {"icon": "LogIn",       "title": "Logged in",            "severity": "info"},
    ("login_failed", "admin_auth"):    {"icon": "LogIn",       "title": "Failed login attempt",  "severity": "warning"},
    ("logout", "admin_auth"):          {"icon": "LogOut",      "title": "Logged out",            "severity": "info"},

    # User management
    ("create", "admin_user"):          {"icon": "UserPlus",    "title": "Account created",       "severity": "info"},
    ("update", "admin_user"):          {"icon": "UserCog",     "title": "Account updated",       "severity": "info"},
    ("delete", "admin_user"):          {"icon": "UserMinus",   "title": "Account deleted",       "severity": "danger"},

    # Resume events
    ("create", "resume"):              {"icon": "FilePlus",    "title": "Resume created",        "severity": "info"},
    ("update", "resume"):              {"icon": "FileEdit",    "title": "Resume updated",        "severity": "info"},
    ("delete", "resume"):              {"icon": "FileMinus",   "title": "Resume deleted",        "severity": "warning"},

    # Security
    ("access_denied", "admin_auth"):   {"icon": "ShieldAlert", "title": "Access denied",         "severity": "danger"},
    ("password_change", "admin_auth"): {"icon": "Key",         "title": "Password changed",      "severity": "info"},
}

# Default mapping for unknown action + entity_type combinations
_DEFAULT_EVENT = {"icon": "Activity", "title": "Activity", "severity": "info"}


def map_audit_log_to_timeline_event(audit: AuditLog) -> Dict[str, Any]:
    """Convert an AuditLog row into a timeline event DTO.

    Returns a dict matching the UserTimelineEvent schema:
        id, icon, title, description, timestamp, actor, severity
    """
    lookup = (audit.action, audit.entity_type)
    mapping = _EVENT_MAP.get(lookup, _DEFAULT_EVENT)

    actor = "System"
    if audit.user_id:
        actor = audit.user_id

    return {
        "id": audit.id,
        "icon": mapping["icon"],
        "title": mapping["title"],
        "description": audit.description,
        "timestamp": audit.created_at.isoformat() if audit.created_at else "",
        "actor": actor,
        "severity": mapping["severity"],
    }
