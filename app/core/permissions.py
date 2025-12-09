from typing import List
from fastapi import HTTPException, status
from app.models.user import User, UserRole


class PermissionChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User) -> bool:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return True


def check_venue_owner(user: User, venue_owner_id: str) -> bool:
    """Проверяет, является ли пользователь владельцем заведения"""
    if user.role == UserRole.ADMIN:
        return True
    return str(user.id) == venue_owner_id


def check_staff_access(user: User, venue_id: str) -> bool:
    """Проверяет доступ персонала к заведению"""
    # TODO: Реализовать проверку через связь staff-venue
    return True

