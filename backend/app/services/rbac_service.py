"""RBAC domain service.

Provides role-based access control administration operations.
Handles role CRUD, permission management, and user role assignments.
"""
import logging
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from ..models.identity import Role, Permission, UserRole, RolePermission
from ..repositories.identity import (
    RoleRepository,
    PermissionRepository,
    UserRoleRepository,
)
from .audit_service import AuditService

logger = logging.getLogger(__name__)


class RBACService:
    """Service for RBAC administration operations.

    Usage:
        service = RBACService(db)
        roles = service.list_roles()
    """

    def __init__(self, db: Session):
        self.db = db
        self.roles = RoleRepository(db)
        self.permissions = PermissionRepository(db)
        self.user_roles = UserRoleRepository(db)
        self.audit = AuditService(db)

    # -----------------------------------------------------------------------
    # Role operations
    # -----------------------------------------------------------------------

    def list_roles(self, include_inactive: bool = False) -> List[Role]:
        """List all roles."""
        if include_inactive:
            return self.db.query(Role).filter(Role.deleted_at.is_(None)).all()
        return self.roles.get_active_roles()

    def get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        role = self.roles.get(role_id)
        if role and role.deleted_at is not None:
            return None
        return role

    def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        return self.roles.get_by_name(name)

    def create_role(
        self,
        name: str,
        description: Optional[str] = None,
        is_system: bool = False,
        user_id: Optional[str] = None,
    ) -> Role:
        """Create a new role."""
        existing = self.roles.get_by_name(name)
        if existing:
            raise ValueError(f"Role '{name}' already exists")

        role = self.roles.create({
            "name": name,
            "description": description,
            "is_system": is_system,
        })
        logger.info("Created role: %s (id=%s)", name, role.id)

        self.audit.log_create(
            entity_type="Role",
            entity_id=role.id,
            new_state={"name": name, "description": description, "is_system": is_system},
            description=f"Created role '{name}'",
            tags="rbac,role",
        )

        return role

    def update_role(
        self,
        role_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Role:
        """Update a role."""
        role = self.get_role(role_id)
        if not role:
            raise KeyError("Role not found")

        if role.is_system:
            raise ValueError("Cannot modify system role")

        previous_state = {"name": role.name, "description": role.description}

        update_data = {}
        if name is not None:
            existing = self.roles.get_by_name(name)
            if existing and existing.id != role_id:
                raise ValueError(f"Role name '{name}' already exists")
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description

        if update_data:
            self.roles.update(role, update_data)
            logger.info("Updated role: %s (id=%s)", role.name, role_id)

            self.audit.log_update(
                entity_type="Role",
                entity_id=role_id,
                previous_state=previous_state,
                new_state={**previous_state, **update_data},
                description=f"Updated role '{role.name}'",
                tags="rbac,role",
            )

        return self.get_role(role_id)

    def delete_role(self, role_id: str, user_id: Optional[str] = None) -> bool:
        """Soft-delete a role. System roles cannot be deleted."""
        role = self.get_role(role_id)
        if not role:
            raise KeyError("Role not found")

        if role.is_system:
            raise ValueError("Cannot delete system role")

        previous_state = {"name": role.name, "description": role.description}

        self.roles.soft_delete(role_id)
        logger.info("Deleted role: %s (id=%s)", role.name, role_id)

        self.audit.log_delete(
            entity_type="Role",
            entity_id=role_id,
            previous_state=previous_state,
            description=f"Deleted role '{role.name}'",
            tags="rbac,role",
        )

        return True

    # -----------------------------------------------------------------------
    # Permission operations
    # -----------------------------------------------------------------------

    def list_permissions(self) -> List[Permission]:
        """List all permissions."""
        return self.db.query(Permission).all()

    def get_permission(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        return self.permissions.get(permission_id)

    def get_role_permissions(self, role_id: str) -> List[Permission]:
        """Get all permissions for a role."""
        role = self.get_role(role_id)
        if not role:
            raise KeyError("Role not found")

        return (
            self.db.query(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .filter(RolePermission.role_id == role_id)
            .all()
        )

    def add_permission_to_role(self, role_id: str, permission_id: str, user_id: Optional[str] = None) -> RolePermission:
        """Add a permission to a role."""
        role = self.get_role(role_id)
        if not role:
            raise KeyError("Role not found")

        permission = self.permissions.get(permission_id)
        if not permission:
            raise KeyError("Permission not found")

        existing = (
            self.db.query(RolePermission)
            .filter(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
            .first()
        )
        if existing:
            return existing

        rp = RolePermission(role_id=role_id, permission_id=permission_id)
        self.db.add(rp)
        self.db.commit()
        logger.info(
            "Added permission %s to role %s",
            permission.name,
            role.name,
        )

        self.audit.log_update(
            entity_type="Role",
            entity_id=role_id,
            new_state={"permission_added": permission.name},
            description=f"Added permission '{permission.name}' to role '{role.name}'",
            tags="rbac,role,permission",
        )

        return rp

    def remove_permission_from_role(self, role_id: str, permission_id: str, user_id: Optional[str] = None) -> bool:
        """Remove a permission from a role."""
        rp = (
            self.db.query(RolePermission)
            .filter(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
            .first()
        )
        if not rp:
            return False

        self.db.delete(rp)
        self.db.commit()
        logger.info("Removed permission %s from role %s", permission_id, role_id)

        self.audit.log_update(
            entity_type="Role",
            entity_id=role_id,
            new_state={"permission_removed": permission_id},
            description=f"Removed permission '{permission_id}' from role '{role_id}'",
            tags="rbac,role,permission",
        )

        return True

    # -----------------------------------------------------------------------
    # User role assignment operations
    # -----------------------------------------------------------------------

    def get_user_roles(self, user_id: str) -> List[Tuple[UserRole, Role]]:
        """Get all active role assignments for a user with role details."""
        assignments = self.user_roles.get_user_roles(user_id)
        result = []
        for assignment in assignments:
            role = self.roles.get(assignment.role_id)
            if role:
                result.append((assignment, role))
        return result

    def assign_role(
        self,
        user_id: str,
        role_id: str,
        assigned_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> UserRole:
        """Assign a role to a user."""
        role = self.get_role(role_id)
        if not role:
            raise KeyError("Role not found")

        assignment = self.user_roles.assign_role(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by,
            expires_at=expires_at,
        )
        logger.info(
            "Assigned role %s to user %s (by=%s)",
            role.name,
            user_id,
            assigned_by,
        )

        self.audit.log_create(
            entity_type="UserRole",
            entity_id=assignment.id,
            new_state={"user_id": user_id, "role_id": role_id, "role_name": role.name},
            description=f"Assigned role '{role.name}' to user '{user_id}'",
            tags="rbac,user_role",
        )

        return assignment

    def revoke_role(self, user_id: str, role_id: str, revoked_by: Optional[str] = None) -> bool:
        """Revoke a role from a user."""
        role = self.get_role(role_id)
        role_name = role.name if role else role_id

        result = self.user_roles.revoke_role(user_id, role_id)
        if result:
            logger.info("Revoked role %s from user %s", role_id, user_id)

            self.audit.log_update(
                entity_type="UserRole",
                entity_id=role_id,
                previous_state={"user_id": user_id, "role_id": role_id, "role_name": role_name},
                new_state={"is_active": False},
                description=f"Revoked role '{role_name}' from user '{user_id}'",
                tags="rbac,user_role",
            )

        return result
