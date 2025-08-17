from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from typing import List

from db import session, schemas, models
from core import security

router = APIRouter()

@router.post("/", response_model=schemas.Availability, status_code=status.HTTP_201_CREATED)
def create_availability(
    *,
    db: Session = Depends(session.get_db),
    availability_in: schemas.AvailabilityBase,
    current_user: models.User = Depends(security.get_current_active_user),
):
    if availability_in.role != current_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create availability for your own role."
        )

    db_availability = models.Availability(**availability_in.dict(), user_id=current_user.id)
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability

@router.get("/", response_model=List[schemas.Availability])
def read_availability(
    user_id: uuid.UUID,
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    availabilities = db.query(models.Availability).filter(models.Availability.user_id == user_id).all()
    return availabilities

@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability(
    *,
    availability_id: uuid.UUID,
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    availability = db.query(models.Availability).get(availability_id)
    if not availability:
        return

    if availability.user_id != current_user.id and current_user.role != schemas.Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this availability"
        )

    db.delete(availability)
    db.commit()
    return
