"""PROCS User Management Service.

Business logic layer for PROCS user management operations.
Follows the service pattern defined in PROCS_Development_Guide.md Section 5.4.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.identity import User, Profile, UserRole, Role, UserSession
from ..repositories.identity import UserRepository, ProfileRepository, UserRoleRepository
from ..services.audit_service import AuditService
from ..services.error_service import ErrorService

logger = logging.getLogger(__name__)


class UserManagementService:
    """Service for PROCS user management operations.

    Provides business logic for user listing, inspection, updates, and actions.
    Integrates with AuditService and ErrorService for observability.
    """

    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.profiles = ProfileRepository(db)
        self.user_roles = UserRoleRepository(db)
        self.audit = AuditService(db)
        self.error = ErrorService(db)

    def get_users(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get paginated user list with filters.

        Args:
            page: Page number (1-indexed)
            limit: Items per page
            search: Search term for email or name
            is_active: Filter by active status
            is_verified: Filter by verified status
            sort_by: Field to sort by
            sort_order: Sort direction ('asc' or 'desc')

        Returns:
            Dict with items, total, page, limit, totalPages
        """
        try:
            # Build query
            query = self.db.query(User).filter(User.deleted_at.is_(None))

            # Apply filters
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    (User.email.ilike(search_term)) |
                    (User.full_name.ilike(search_term))
                )

            if is_active is not None:
                query = query.filter(User.is_active == is_active)

            if is_verified is not None:
                query = query.filter(User.is_verified == is_verified)

            # Get total count
            total = query.count()

            # Apply sorting
            sort_column = getattr(User, sort_by, User.created_at)
            if sort_order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

            # Apply pagination
            page = max(1, page)
            limit = max(1, min(limit, 100))
            offset = (page - 1) * limit
            users = query.offset(offset).limit(limit).all()

            # Calculate total pages
            total_pages = max(1, (total + limit - 1) // limit)

            return {
                "items": users,
                "total": total,
                "page": page,
                "limit": limit,
                "totalPages": total_pages,
            }
        except Exception as e:
            logger.error("Failed to get users: %s", e)
            self.error.log_exception(e, context={"operation": "get_users"})
            raise

    def get_user_detail(self, user_id: str) -> Optional[User]:
        """Get user detail by ID.

        Args:
            user_id: User ID

        Returns:
            User object or None if not found
        """
        try:
            user = self.users.get(user_id)
            if not user or user.deleted_at:
                return None
            return user
        except Exception as e:
            logger.error("Failed to get user detail: %s", e)
            self.error.log_exception(e, context={"operation": "get_user_detail", "user_id": user_id})
            raise

    def get_user_roles(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user roles.

        Args:
            user_id: User ID

        Returns:
            List of role dicts
        """
        try:
            user_roles = (
                self.db.query(UserRole, Role)
                .join(Role, UserRole.role_id == Role.id)
                .filter(UserRole.user_id == user_id, UserRole.is_active == True)
                .all()
            )
            return [
                {
                    "id": ur.UserRole.id,
                    "role_id": ur.Role.id,
                    "role_name": ur.Role.name,
                    "assigned_at": ur.UserRole.created_at,
                }
                for ur in user_roles
            ]
        except Exception as e:
            logger.error("Failed to get user roles: %s", e)
            return []

    def update_user(
        self,
        user_id: str,
        data: Dict[str, Any],
        admin_id: str,
    ) -> Optional[User]:
        """Update user details.

        Args:
            user_id: User ID to update
            data: Update data
            admin_id: ID of admin performing the update

        Returns:
            Updated User object or None if not found
        """
        try:
            user = self.users.get(user_id)
            if not user or user.deleted_at:
                return None

            # Store old state for audit
            old_state = {
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "is_superuser": user.is_superuser,
            }

            # Update fields
            for field, value in data.items():
                if hasattr(user, field) and value is not None:
                    setattr(user, field, value)

            self.db.commit()
            self.db.refresh(user)

            # Audit log
            self.audit.log_update(
                entity_type="User",
                entity_id=user_id,
                old_state=old_state,
                new_state=data,
                user_id=admin_id,
            )

            return user
        except Exception as e:
            logger.error("Failed to update user: %s", e)
            self.error.log_exception(e, context={"operation": "update_user", "user_id": user_id})
            self.db.rollback()
            raise

    def soft_delete_user(self, user_id: str, admin_id: str) -> bool:
        """Soft delete a user.

        Args:
            user_id: User ID to delete
            admin_id: ID of admin performing the deletion

        Returns:
            True if deleted, False if not found
        """
        try:
            user = self.users.get(user_id)
            if not user or user.deleted_at:
                return False

            # Soft delete
            user.deleted_at = datetime.utcnow()
            user.is_active = False
            self.db.commit()

            # Audit log
            self.audit.log_delete(
                entity_type="User",
                entity_id=user_id,
                user_id=admin_id,
            )

            return True
        except Exception as e:
            logger.error("Failed to soft delete user: %s", e)
            self.error.log_exception(e, context={"operation": "soft_delete_user", "user_id": user_id})
            self.db.rollback()
            raise

    def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics.

        Returns:
            Dict with user counts
        """
        try:
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=7)
            month_start = today_start - timedelta(days=30)

            total = self.db.query(func.count(User.id)).filter(User.deleted_at.is_(None)).scalar() or 0
            active = self.db.query(func.count(User.id)).filter(
                User.is_active == True, User.deleted_at.is_(None)
            ).scalar() or 0
            verified = self.db.query(func.count(User.id)).filter(
                User.is_verified == True, User.deleted_at.is_(None)
            ).scalar() or 0
            superuser = self.db.query(func.count(User.id)).filter(
                User.is_superuser == True, User.deleted_at.is_(None)
            ).scalar() or 0
            new_today = self.db.query(func.count(User.id)).filter(
                User.created_at >= today_start, User.deleted_at.is_(None)
            ).scalar() or 0
            new_week = self.db.query(func.count(User.id)).filter(
                User.created_at >= week_start, User.deleted_at.is_(None)
            ).scalar() or 0
            new_month = self.db.query(func.count(User.id)).filter(
                User.created_at >= month_start, User.deleted_at.is_(None)
            ).scalar() or 0

            return {
                "total_users": total,
                "active_users": active,
                "verified_users": verified,
                "superuser_count": superuser,
                "new_users_today": new_today,
                "new_users_this_week": new_week,
                "new_users_this_month": new_month,
            }
        except Exception as e:
            logger.error("Failed to get user stats: %s", e)
            return {
                "total_users": 0,
                "active_users": 0,
                "verified_users": 0,
                "superuser_count": 0,
                "new_users_today": 0,
                "new_users_this_week": 0,
                "new_users_this_month": 0,
            }
