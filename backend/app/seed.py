import json
import logging
from sqlalchemy.orm import Session
from .database import engine, SessionLocal, Base
from .models import Template, ResumeRule
from .models.identity import User, Profile, Subscription, Role, Permission, RolePermission, UserRole
from .models.audit import AuditConfig
from .models.error import ErrorCategory

logger = logging.getLogger(__name__)

TEMPLATES_DATA = [
    # ATS CATEGORY
    {
        "id": "harvard",
        "name": "Harvard Standard",
        "category": "ATS",
        "color_scheme": {"primary": "#000000", "secondary": "#4A4A4A", "text": "#1A1A1A", "accent": "#A51C30", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.75in", "headerStyle": "centered", "section_order": ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]}
    },
    {
        "id": "stanford",
        "name": "Stanford Clean",
        "category": "ATS",
        "color_scheme": {"primary": "#8C1515", "secondary": "#4D4F53", "text": "#2E2D29", "accent": "#8C1515", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "sans-serif", "margins": "0.75in", "headerStyle": "left", "section_order": ["summary", "experience", "education", "skills", "projects", "certifications", "achievements"]}
    },
    {
        "id": "mit",
        "name": "MIT Compact",
        "category": "ATS",
        "color_scheme": {"primary": "#A31F34", "secondary": "#8A8B8C", "text": "#111111", "accent": "#A31F34", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "monospace", "margins": "0.5in", "headerStyle": "left", "section_order": ["education", "skills", "experience", "projects", "certifications", "achievements"]}
    },
    {
        "id": "columbia",
        "name": "Columbia Classic",
        "category": "ATS",
        "color_scheme": {"primary": "#003087", "secondary": "#6CACE4", "text": "#1D252D", "accent": "#003087", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.8in", "headerStyle": "centered", "section_order": ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]}
    },
    {
        "id": "yale",
        "name": "Yale Editorial",
        "category": "ATS",
        "color_scheme": {"primary": "#00356B", "secondary": "#28619E", "text": "#0F0F0F", "accent": "#00356B", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.75in", "headerStyle": "centered", "section_order": ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]}
    },
    {
        "id": "princeton",
        "name": "Princeton Bold",
        "category": "ATS",
        "color_scheme": {"primary": "#EE7F2D", "secondary": "#222222", "text": "#1C1C1C", "accent": "#EE7F2D", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.75in", "headerStyle": "left", "section_order": ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]}
    },
    # CORPORATE CATEGORY
    {
        "id": "executive",
        "name": "Executive Elite",
        "category": "Corporate",
        "color_scheme": {"primary": "#0F172A", "secondary": "#475569", "text": "#1E293B", "accent": "#B45309", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.75in", "headerStyle": "centered", "section_order": ["summary", "experience", "education", "skills", "projects", "certifications", "achievements"]}
    },
    {
        "id": "consultant",
        "name": "Sleek Consultant",
        "category": "Corporate",
        "color_scheme": {"primary": "#1E293B", "secondary": "#64748B", "text": "#334155", "accent": "#0F766E", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "sans-serif", "margins": "0.7in", "headerStyle": "left", "section_order": ["summary", "experience", "projects", "education", "skills", "certifications", "achievements"]}
    },
    {
        "id": "finance",
        "name": "Wall Street Finance",
        "category": "Corporate",
        "color_scheme": {"primary": "#064E3B", "secondary": "#115E59", "text": "#0F172A", "accent": "#0D9488", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.75in", "headerStyle": "centered", "section_order": ["summary", "experience", "education", "skills", "certifications", "achievements"]}
    },
    {
        "id": "product_manager",
        "name": "SaaS PM",
        "category": "Corporate",
        "color_scheme": {"primary": "#4F46E5", "secondary": "#475569", "text": "#1E293B", "accent": "#4F46E5", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-right", "fontFamily": "sans-serif", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["education", "skills", "certifications", "achievements"]}
    },
    {
        "id": "operations",
        "name": "Operations Lead",
        "category": "Corporate",
        "color_scheme": {"primary": "#334155", "secondary": "#475569", "text": "#0F172A", "accent": "#2563EB", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "sans-serif", "margins": "0.75in", "headerStyle": "left", "section_order": ["summary", "experience", "education", "skills", "projects", "certifications", "achievements"]}
    },
    {
        "id": "management",
        "name": "Strategic Manager",
        "category": "Corporate",
        "color_scheme": {"primary": "#881337", "secondary": "#4C0519", "text": "#1F2937", "accent": "#9F1239", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.75in", "headerStyle": "centered", "section_order": ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]}
    },
    # TECHNOLOGY CATEGORY
    {
        "id": "software_engineer",
        "name": "Dev Standard",
        "category": "Technology",
        "color_scheme": {"primary": "#0F766E", "secondary": "#334155", "text": "#0F172A", "accent": "#0D9488", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-left", "fontFamily": "sans-serif", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education", "certifications", "achievements"]}
    },
    {
        "id": "data_scientist",
        "name": "Data Analyst",
        "category": "Technology",
        "color_scheme": {"primary": "#1E3A8A", "secondary": "#475569", "text": "#1E293B", "accent": "#3B82F6", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-left", "fontFamily": "sans-serif", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education", "certifications"]}
    },
    {
        "id": "ai_engineer",
        "name": "Neural AI Specialist",
        "category": "Technology",
        "color_scheme": {"primary": "#312E81", "secondary": "#4F46E5", "text": "#111827", "accent": "#F59E0B", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "monospace", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "skills", "experience", "projects", "education", "certifications"]}
    },
    {
        "id": "devops",
        "name": "Site Reliability DevOps",
        "category": "Technology",
        "color_scheme": {"primary": "#4C1D95", "secondary": "#6D28D9", "text": "#1F2937", "accent": "#8B5CF6", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "monospace", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "skills", "experience", "projects", "education"]}
    },
    {
        "id": "cloud_engineer",
        "name": "Cloud Systems Architect",
        "category": "Technology",
        "color_scheme": {"primary": "#0369A1", "secondary": "#0284C7", "text": "#0F172A", "accent": "#0EA5E9", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-left", "fontFamily": "sans-serif", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education", "certifications"]}
    },
    {
        "id": "cybersecurity",
        "name": "SecOps Consultant",
        "category": "Technology",
        "color_scheme": {"primary": "#065F46", "secondary": "#047857", "text": "#111827", "accent": "#10B981", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "monospace", "margins": "0.65in", "headerStyle": "left", "section_order": ["summary", "skills", "experience", "projects", "education", "certifications"]}
    },
    # CREATIVE CATEGORY
    {
        "id": "ui_ux",
        "name": "Design Portfolio",
        "category": "Creative",
        "color_scheme": {"primary": "#6B21A8", "secondary": "#DB2777", "text": "#1F2937", "accent": "#F472B6", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-left", "fontFamily": "sans-serif", "margins": "0.5in", "headerStyle": "banner", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education", "achievements"]}
    },
    {
        "id": "graphic_designer",
        "name": "Bold Art Studio",
        "category": "Creative",
        "color_scheme": {"primary": "#C2410C", "secondary": "#1E293B", "text": "#0F172A", "accent": "#EA580C", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "sans-serif", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "projects", "experience", "education", "skills"]}
    },
    {
        "id": "marketing",
        "name": "Growth Strategist",
        "category": "Creative",
        "color_scheme": {"primary": "#BE185D", "secondary": "#475569", "text": "#1E293B", "accent": "#F43F5E", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-right", "fontFamily": "sans-serif", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education", "certifications"]}
    },
    {
        "id": "content_creator",
        "name": "Social Media Hub",
        "category": "Creative",
        "color_scheme": {"primary": "#1D4ED8", "secondary": "#2563EB", "text": "#1E293B", "accent": "#F59E0B", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-left", "fontFamily": "sans-serif", "margins": "0.55in", "headerStyle": "left", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education"]}
    },
    {
        "id": "photographer",
        "name": "Minimalist Frame",
        "category": "Creative",
        "color_scheme": {"primary": "#1F2937", "secondary": "#4B5563", "text": "#111827", "accent": "#78350F", "background": "#FCFBF7"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.8in", "headerStyle": "centered", "section_order": ["summary", "projects", "experience", "education"]}
    },
    {
        "id": "creative_director",
        "name": "Avant-Garde Lead",
        "category": "Creative",
        "color_scheme": {"primary": "#000000", "secondary": "#111827", "text": "#222222", "accent": "#FBBF24", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-right", "fontFamily": "sans-serif", "margins": "0.5in", "headerStyle": "banner", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education", "achievements"]}
    }
]

# RULES_DATA removed — rules are now governed via KnowledgeRule DB.
# See scripts/seed_hand_authored.py and scripts/migrate_shadow1_rules.py

def _seed_role_permissions(db: Session) -> None:
    """Seed role-permission mappings for system roles."""
    # Get all permissions
    all_permissions = db.query(Permission).all()
    perm_map = {p.name: p.id for p in all_permissions}
    
    # Admin gets all permissions
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if admin_role:
        for perm_name, perm_id in perm_map.items():
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == admin_role.id,
                RolePermission.permission_id == perm_id,
            ).first()
            if not existing:
                db.add(RolePermission(role_id=admin_role.id, permission_id=perm_id))
    
    # User gets basic permissions
    user_role = db.query(Role).filter(Role.name == "user").first()
    user_perms = [
        "resume:create", "resume:read", "resume:update", "resume:delete",
        "cover_letter:create", "cover_letter:read", "cover_letter:update", "cover_letter:delete",
        "ai:use",
        "billing:read",
    ]
    if user_role:
        for perm_name in user_perms:
            if perm_name in perm_map:
                existing = db.query(RolePermission).filter(
                    RolePermission.role_id == user_role.id,
                    RolePermission.permission_id == perm_map[perm_name],
                ).first()
                if not existing:
                    db.add(RolePermission(role_id=user_role.id, permission_id=perm_map[perm_name]))
    
    # Premium gets user + extra AI
    premium_role = db.query(Role).filter(Role.name == "premium").first()
    premium_perms = user_perms + ["ai:unlimited"]
    if premium_role:
        for perm_name in premium_perms:
            if perm_name in perm_map:
                existing = db.query(RolePermission).filter(
                    RolePermission.role_id == premium_role.id,
                    RolePermission.permission_id == perm_map[perm_name],
                ).first()
                if not existing:
                    db.add(RolePermission(role_id=premium_role.id, permission_id=perm_map[perm_name]))
    
    # Viewer gets read-only permissions
    viewer_role = db.query(Role).filter(Role.name == "viewer").first()
    viewer_perms = ["resume:read", "cover_letter:read"]
    if viewer_role:
        for perm_name in viewer_perms:
            if perm_name in perm_map:
                existing = db.query(RolePermission).filter(
                    RolePermission.role_id == viewer_role.id,
                    RolePermission.permission_id == perm_map[perm_name],
                ).first()
                if not existing:
                    db.add(RolePermission(role_id=viewer_role.id, permission_id=perm_map[perm_name]))
    
    # Organization admin gets org management
    org_admin_role = db.query(Role).filter(Role.name == "organization_admin").first()
    org_admin_perms = user_perms + ["org:manage", "org:member"]
    if org_admin_role:
        for perm_name in org_admin_perms:
            if perm_name in perm_map:
                existing = db.query(RolePermission).filter(
                    RolePermission.role_id == org_admin_role.id,
                    RolePermission.permission_id == perm_map[perm_name],
                ).first()
                if not existing:
                    db.add(RolePermission(role_id=org_admin_role.id, permission_id=perm_map[perm_name]))
    
    db.commit()
    logger.info("Seeded role-permission mappings.")


def _seed_audit_configs(db: Session) -> None:
    """Seed default audit configurations for all entity types."""
    default_configs = [
        # User entity - track all mutations
        {
            "entity_type": "User",
            "is_enabled": True,
            "audit_create": True,
            "audit_read": False,
            "audit_update": True,
            "audit_delete": True,
            "retention_days": 730,  # 2 years for user accounts
            "archive_after_days": 180,
            "sensitive_fields": json.dumps(["hashed_password", "last_login_ip"]),
        },
        # Resume entity - track all mutations
        {
            "entity_type": "Resume",
            "is_enabled": True,
            "audit_create": True,
            "audit_read": False,
            "audit_update": True,
            "audit_delete": True,
            "retention_days": 365,
            "archive_after_days": 90,
        },
        # CoverLetter entity
        {
            "entity_type": "CoverLetter",
            "is_enabled": True,
            "audit_create": True,
            "audit_read": False,
            "audit_update": True,
            "audit_delete": True,
            "retention_days": 365,
            "archive_after_days": 90,
        },
        # Session entity - security critical
        {
            "entity_type": "Session",
            "is_enabled": True,
            "audit_create": True,
            "audit_read": False,
            "audit_update": True,
            "audit_delete": True,
            "retention_days": 365,
            "archive_after_days": 90,
            "sensitive_fields": json.dumps(["token_hash"]),
        },
        # LoginHistory - immutable, track all
        {
            "entity_type": "LoginHistory",
            "is_enabled": True,
            "audit_create": True,
            "audit_read": False,
            "audit_update": False,
            "audit_delete": False,
            "retention_days": 730,  # 2 years for security
            "archive_after_days": 365,
        },
        # Subscription entity
        {
            "entity_type": "Subscription",
            "is_enabled": True,
            "audit_create": True,
            "audit_read": False,
            "audit_update": True,
            "audit_delete": False,
            "retention_days": 1095,  # 3 years for billing
            "archive_after_days": 365,
        },
        # Payment entity - financial records
        {
            "entity_type": "Payment",
            "is_enabled": True,
            "audit_create": True,
            "audit_read": False,
            "audit_update": False,
            "audit_delete": False,
            "retention_days": 2555,  # 7 years for financial compliance
            "archive_after_days": 365,
        },
        # Organization entity
        {
            "entity_type": "Organization",
            "is_enabled": True,
            "audit_create": True,
            "audit_read": False,
            "audit_update": True,
            "audit_delete": True,
            "retention_days": 365,
            "archive_after_days": 90,
        },
        # Role entity - security critical
        {
            "entity_type": "Role",
            "is_enabled": True,
            "audit_create": True,
            "audit_read": False,
            "audit_update": True,
            "audit_delete": True,
            "retention_days": 730,
            "archive_after_days": 365,
        },
        # Permission entity
        {
            "entity_type": "Permission",
            "is_enabled": True,
            "audit_create": True,
            "audit_read": False,
            "audit_update": True,
            "audit_delete": True,
            "retention_days": 730,
            "archive_after_days": 365,
        },
        # HTTP requests - low retention
        {
            "entity_type": "http_request",
            "is_enabled": True,
            "audit_create": True,
            "audit_read": False,
            "audit_update": False,
            "audit_delete": False,
            "retention_days": 30,
            "archive_after_days": 7,
            "sample_rate": 100,
        },
        # PROCS entity: admin_user management
        {
            "entity_type": "admin_user",
            "is_enabled": True,
            "audit_create": False,
            "audit_read": False,
            "audit_update": True,
            "audit_delete": True,
            "retention_days": 730,
            "archive_after_days": 180,
            "sensitive_fields": json.dumps(["hashed_password"]),
        },
        # PROCS entity: admin_resume management
        {
            "entity_type": "admin_resume",
            "is_enabled": True,
            "audit_create": False,
            "audit_read": False,
            "audit_update": True,
            "audit_delete": True,
            "retention_days": 365,
            "archive_after_days": 90,
        },
        # PROCS entity: admin_template management
        {
            "entity_type": "admin_template",
            "is_enabled": True,
            "audit_create": False,
            "audit_read": False,
            "audit_update": True,
            "audit_delete": True,
            "retention_days": 365,
            "archive_after_days": 90,
        },
        # PROCS entity: admin_auth events (LOGIN, LOGOUT, ACCESS_DENIED)
        {
            "entity_type": "admin_auth",
            "is_enabled": True,
            "audit_create": True,
            "audit_read": False,
            "audit_update": False,
            "audit_delete": False,
            "retention_days": 730,
            "archive_after_days": 365,
        },
        # PROCS entity: admin_config changes
        {
            "entity_type": "admin_config",
            "is_enabled": True,
            "audit_create": False,
            "audit_read": False,
            "audit_update": True,
            "audit_delete": False,
            "retention_days": 365,
            "archive_after_days": 90,
        },
    ]
    
    for config_data in default_configs:
        existing = db.query(AuditConfig).filter(
            AuditConfig.entity_type == config_data["entity_type"]
        ).first()
        if not existing:
            config = AuditConfig(**config_data)
            db.add(config)
            logger.info("Seeding audit config: %s", config_data['entity_type'])
    
    db.commit()
    logger.info("Seeded audit configurations.")


def _seed_error_categories(db: Session) -> None:
    """Seed default error categories."""
    default_categories = [
        {
            "name": "Authentication",
            "description": "Login, registration, and authentication errors",
            "color": "#EF4444",
            "icon": "lock",
            "default_severity": "high",
            "patterns": json.dumps(["auth", "login", "password", "token", "jwt"]),
        },
        {
            "name": "Authorization",
            "description": "Permission and access control errors",
            "color": "#F59E0B",
            "icon": "shield",
            "default_severity": "high",
            "patterns": json.dumps(["permission", "forbidden", "unauthorized", "access"]),
        },
        {
            "name": "Validation",
            "description": "Input validation and data integrity errors",
            "color": "#3B82F6",
            "icon": "check-circle",
            "default_severity": "low",
            "patterns": json.dumps(["validation", "invalid", "required", "format"]),
        },
        {
            "name": "Database",
            "description": "Database connection and query errors",
            "color": "#8B5CF6",
            "icon": "database",
            "default_severity": "critical",
            "patterns": json.dumps(["database", "sql", "connection", "query", "integrity"]),
        },
        {
            "name": "API",
            "description": "External API and service integration errors",
            "color": "#EC4899",
            "icon": "globe",
            "default_severity": "high",
            "patterns": json.dumps(["api", "request", "timeout", "connection", "endpoint"]),
        },
        {
            "name": "AI Service",
            "description": "AI provider and model errors",
            "color": "#10B981",
            "icon": "cpu",
            "default_severity": "high",
            "patterns": json.dumps(["ai", "llm", "gemini", "openai", "model", "generation"]),
        },
        {
            "name": "File System",
            "description": "File I/O and storage errors",
            "color": "#6366F1",
            "icon": "file",
            "default_severity": "medium",
            "patterns": json.dumps(["file", "directory", "path", "storage", "upload"]),
        },
        {
            "name": "PDF Generation",
            "description": "PDF rendering and export errors",
            "color": "#14B8A6",
            "icon": "file-text",
            "default_severity": "medium",
            "patterns": json.dumps(["pdf", "render", "export", "template"]),
        },
        {
            "name": "Resume Processing",
            "description": "Resume parsing and processing errors",
            "color": "#F97316",
            "icon": "file",
            "default_severity": "medium",
            "patterns": json.dumps(["resume", "parse", "section", "content"]),
        },
        {
            "name": "System",
            "description": "System and infrastructure errors",
            "color": "#DC2626",
            "icon": "alert-triangle",
            "default_severity": "critical",
            "patterns": json.dumps(["system", "memory", "resource", "limit", "overflow"]),
        },
        {
            "name": "Network",
            "description": "Network and connectivity errors",
            "color": "#7C3AED",
            "icon": "wifi",
            "default_severity": "high",
            "patterns": json.dumps(["network", "connect", "dns", "socket", "refused"]),
        },
        {
            "name": "Subscription",
            "description": "Billing and subscription errors",
            "color": "#059669",
            "icon": "credit-card",
            "default_severity": "medium",
            "patterns": json.dumps(["subscription", "billing", "payment", "plan"]),
        },
    ]
    
    for cat_data in default_categories:
        existing = db.query(ErrorCategory).filter(ErrorCategory.name == cat_data["name"]).first()
        if not existing:
            category = ErrorCategory(**cat_data)
            db.add(category)
            logger.info("Seeding error category: %s", cat_data['name'])
    
    db.commit()
    logger.info("Seeded error categories.")


def seed_db():
    db: Session = SessionLocal()
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified.")

        # Seed sentinel guest user (required for FK constraints on guest data)
        guest_user = db.query(User).filter(User.id == "guest").first()
        if not guest_user:
            guest_user = User(
                id="guest",
                email="guest@promptresume.local",
                full_name="Guest User",
                is_active=False,  # Not a real user
                is_verified=False,
            )
            db.add(guest_user)
            db.flush()
            
            # Create guest profile
            guest_profile = Profile(user_id="guest")
            db.add(guest_profile)
            
            # Create guest subscription
            guest_sub = Subscription(user_id="guest", plan_type="free", status="active")
            db.add(guest_sub)
            
            logger.info("Seeded sentinel guest user.")
        
        # Seed Templates
        for t_info in TEMPLATES_DATA:
            existing = db.query(Template).filter(Template.id == t_info["id"]).first()
            if not existing:
                template = Template(
                    id=t_info["id"],
                    name=t_info["name"],
                    category=t_info["category"],
                    color_scheme=t_info["color_scheme"],
                    layout_schema=t_info["layout_schema"]
                )
                db.add(template)
                logger.info("Seeding template: %s", t_info['name'])
        
        # Rules seeding removed — rules are now governed via KnowledgeRule DB.
        # See scripts/seed_hand_authored.py and scripts/migrate_shadow1_rules.py
        
        # Seed Identity - System Roles
        default_roles = [
            {"name": "admin", "description": "Full system administrator with all permissions", "is_system": True},
            {"name": "user", "description": "Standard user with basic permissions", "is_system": True},
            {"name": "premium", "description": "Premium subscriber with enhanced features", "is_system": True},
            {"name": "organization_admin", "description": "Organization administrator", "is_system": True},
            {"name": "viewer", "description": "Read-only access", "is_system": True},
        ]
        for role_data in default_roles:
            existing = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing:
                role = Role(**role_data)
                db.add(role)
                logger.info("Seeding role: %s", role_data['name'])
        
        # Seed Identity - Permissions
        default_permissions = [
            # Resume permissions
            {"name": "resume:create", "resource": "resume", "action": "create"},
            {"name": "resume:read", "resource": "resume", "action": "read"},
            {"name": "resume:update", "resource": "resume", "action": "update"},
            {"name": "resume:delete", "resource": "resume", "action": "delete"},
            # Cover letter permissions
            {"name": "cover_letter:create", "resource": "cover_letter", "action": "create"},
            {"name": "cover_letter:read", "resource": "cover_letter", "action": "read"},
            {"name": "cover_letter:update", "resource": "cover_letter", "action": "update"},
            {"name": "cover_letter:delete", "resource": "cover_letter", "action": "delete"},
            # AI permissions
            {"name": "ai:use", "resource": "ai", "action": "use"},
            {"name": "ai:unlimited", "resource": "ai", "action": "unlimited"},
            # Subscription permissions
            {"name": "subscription:manage", "resource": "subscription", "action": "manage"},
            {"name": "billing:read", "resource": "billing", "action": "read"},
            # Admin permissions
            {"name": "admin:users", "resource": "admin", "action": "users"},
            {"name": "admin:system", "resource": "admin", "action": "system"},
            # Organization permissions
            {"name": "org:manage", "resource": "organization", "action": "manage"},
            {"name": "org:member", "resource": "organization", "action": "member"},
        ]
        for perm_data in default_permissions:
            existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
            if not existing:
                permission = Permission(**perm_data)
                db.add(permission)
                logger.info("Seeding permission: %s", perm_data['name'])
        
        db.commit()
        
        # Seed Role-Permission mappings
        _seed_role_permissions(db)

        # Seed admin user with superuser privileges
        admin_email = "admin@example.com"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            from .auth import get_password_hash
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("Admin123!"),
                full_name="Admin User",
                is_active=True,
                is_verified=True,
                is_superuser=True,
            )
            db.add(admin_user)
            db.flush()

            admin_profile = Profile(user_id=admin_user.id)
            db.add(admin_profile)

            admin_sub = Subscription(user_id=admin_user.id, plan_type="pro", status="active")
            db.add(admin_sub)

            logger.info("Seeded admin user: %s", admin_email)
        else:
            # Ensure existing admin user has superuser flag
            if not admin_user.is_superuser:
                admin_user.is_superuser = True
                logger.info("Updated admin user to is_superuser=True")

        # Ensure admin user has the admin role
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role and admin_user:
            existing_ur = db.query(UserRole).filter(
                UserRole.user_id == admin_user.id,
                UserRole.role_id == admin_role.id,
            ).first()
            if not existing_ur:
                db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id, is_active=True))
                logger.info("Assigned admin role to %s", admin_email)

        db.commit()

        # Seed Audit domain - Default configurations
        _seed_audit_configs(db)
        
        # Seed Error domain - Default categories
        _seed_error_categories(db)
        
        logger.info("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        logger.exception("Error seeding database")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
