from fastapi import Depends, HTTPException, status

from core.security import get_current_active_user
from db import models, schemas

class RoleChecker:
    def __init__(self, allowed_roles: list[schemas.Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: models.User = Depends(get_current_active_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user does not have adequate privileges"
            )
        return user
