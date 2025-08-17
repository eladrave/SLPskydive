from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from typing import List

from db import session, schemas, models
from core import security, rbac

router = APIRouter()

mentee_only = rbac.RoleChecker([schemas.Role.mentee])

@router.post("/attendance", response_model=schemas.AttendanceRequest, status_code=status.HTTP_201_CREATED)
def create_attendance_request(
    *,
    db: Session = Depends(session.get_db),
    attendance_in: schemas.AttendanceRequestCreate,
    current_user: models.User = Depends(mentee_only),
):
    session_block = db.query(models.SessionBlock).get(attendance_in.session_block_id)
    if not session_block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session block not found")

    existing_request = db.query(models.AttendanceRequest).filter_by(
        mentee_id=current_user.id, session_block_id=attendance_in.session_block_id
    ).first()
    if existing_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attendance already requested for this block")

    db_attendance = models.AttendanceRequest(
        mentee_id=current_user.id, session_block_id=attendance_in.session_block_id, status=schemas.AttendanceStatus.pending
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.delete("/attendance/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance_request(
    *,
    attendance_id: uuid.UUID,
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    attendance = db.query(models.AttendanceRequest).get(attendance_id)
    if not attendance:
        return

    if attendance.mentee_id != current_user.id and current_user.role != schemas.Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db.delete(attendance)
    db.commit()
    return

@router.get("/preferences", response_model=schemas.Preference)
def get_preferences(
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(mentee_only),
):
    preferences = db.query(models.Preference).filter_by(mentee_id=current_user.id).first()
    if not preferences:
        return schemas.Preference(id=uuid.uuid4(), mentee_id=current_user.id, preferred_mentors=[], avoid_mentors=[], notes="")
    return preferences

@router.put("/preferences", response_model=schemas.Preference)
def update_preferences(
    *,
    db: Session = Depends(session.get_db),
    preferences_in: schemas.PreferenceUpdate,
    current_user: models.User = Depends(mentee_only),
):
    preferences = db.query(models.Preference).filter_by(mentee_id=current_user.id).first()

    if preferences:
        update_data = preferences_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preferences, field, value)
    else:
        preferences = models.Preference(**preferences_in.dict(), mentee_id=current_user.id)
        db.add(preferences)

    db.commit()
    db.refresh(preferences)
    return preferences
