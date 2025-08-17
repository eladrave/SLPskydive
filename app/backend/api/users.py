from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from typing import List, Optional

from db import session, schemas, models
from core import security

router = APIRouter()

@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(session.get_db),
    role: Optional[schemas.Role] = None,
    current_user: models.User = Depends(security.get_current_active_user),
):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    users = query.order_by(models.User.name).all()
    return users

@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: uuid.UUID,
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(session.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(security.get_current_active_user),
):
    user_data = user_in.dict(exclude_unset=True)
    for field, value in user_data.items():
        setattr(current_user, field, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
