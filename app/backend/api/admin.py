from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import List

from db import session, schemas, models
from core import security, rbac

router = APIRouter()

admin_only = rbac.RoleChecker([schemas.Role.admin])

@router.get("/roster", response_model=List[schemas.Roster])
def get_roster(
    *,
    db: Session = Depends(session.get_db),
    date: date,
    current_user: models.User = Depends(admin_only),
):
    session_blocks = db.query(models.SessionBlock).filter(models.SessionBlock.date == date).order_by(models.SessionBlock.start_time).all()

    roster_list = []
    for block in session_blocks:
        assignments = db.query(models.Assignment).filter(models.Assignment.session_block_id == block.id).all()
        roster_list.append(schemas.Roster(session_block=block, assignments=assignments))

    return roster_list

@router.post("/steps", response_model=schemas.ProgressionStep)
def create_or_update_progression_step(
    *,
    db: Session = Depends(session.get_db),
    step_in: schemas.ProgressionStepCreate,
    current_user: models.User = Depends(admin_only),
):
    step = db.query(models.ProgressionStep).filter(models.ProgressionStep.code == step_in.code).first()

    if step:
        update_data = step_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(step, field, value)
    else:
        step = models.ProgressionStep(**step_in.dict())
        db.add(step)

    db.commit()
    db.refresh(step)
    return step

@router.get("/stats", response_model=schemas.AdminStats)
def get_stats(
    *,
    db: Session = Depends(session.get_db),
    from_date: date,
    to_date: date,
    current_user: models.User = Depends(admin_only),
):
    mentors_available = db.query(models.Availability.user_id).filter(
        models.Availability.is_recurring == True, models.Availability.role == schemas.Role.mentor
    ).distinct().count()

    mentees_requesting = db.query(models.AttendanceRequest.mentee_id).join(models.SessionBlock).filter(
        models.SessionBlock.date.between(from_date, to_date)
    ).distinct().count()

    assignments_made = db.query(models.Assignment).join(models.SessionBlock).filter(
        models.SessionBlock.date.between(from_date, to_date)
    ).count()

    completions = db.query(models.StepCompletion).filter(
        func.date(models.StepCompletion.completed_at).between(from_date, to_date)
    ).count()

    completion_rate = (completions / assignments_made) * 100 if assignments_made > 0 else 0

    return schemas.AdminStats(
        mentors_available=mentors_available,
        mentees_requesting=mentees_requesting,
        assignments_made=assignments_made,
        completion_rate=completion_rate,
    )
