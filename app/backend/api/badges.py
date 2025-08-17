from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db import session, schemas, models
from core import security

router = APIRouter()

@router.get("/badges", response_model=List[schemas.Badge])
def read_badges(
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get all available badges.
    """
    badges = db.query(models.Badge).order_by(models.Badge.name).all()
    return badges
