from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from typing import List, Optional

from db import session, schemas, models
from core import security, rbac
from pydantic import BaseModel

progression_router = APIRouter()
jumps_awards_router = APIRouter()

mentor_only = rbac.RoleChecker([schemas.Role.mentor])
mentee_only = rbac.RoleChecker([schemas.Role.mentee])

@progression_router.get("/steps", response_model=List[schemas.ProgressionStep])
def read_progression_steps(
    *,
    db: Session = Depends(session.get_db),
    category: Optional[schemas.ProgressionCategory] = None,
    current_user: models.User = Depends(security.get_current_active_user),
):
    query = db.query(models.ProgressionStep)
    if category:
        query = query.filter(models.ProgressionStep.category == category)
    steps = query.order_by(models.ProgressionStep.code).all()
    return steps

class StepCompletionRequest(BaseModel):
    mentee_id: uuid.UUID
    evidence_url: Optional[str] = None
    notes: Optional[str] = None

@progression_router.post("/{step_id}/complete", response_model=schemas.StepCompletion)
def complete_progression_step(
    *,
    db: Session = Depends(session.get_db),
    step_id: uuid.UUID,
    completion_in: StepCompletionRequest,
    current_user: models.User = Depends(mentor_only),
):
    step = db.query(models.ProgressionStep).get(step_id)
    if not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Progression step not found")

    mentee = db.query(models.User).filter(models.User.id == completion_in.mentee_id, models.User.role == schemas.Role.mentee).first()
    if not mentee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentee not found")

    existing_completion = db.query(models.StepCompletion).filter_by(mentee_id=completion_in.mentee_id, step_id=step_id).first()
    if existing_completion:
        return existing_completion

    db_completion = models.StepCompletion(
        mentee_id=completion_in.mentee_id, step_id=step_id, mentor_id=current_user.id,
        evidence_url=completion_in.evidence_url, notes=completion_in.notes
    )
    db.add(db_completion)
    db.commit()
    db.refresh(db_completion)
    return db_completion

@jumps_awards_router.get("/completions", response_model=List[schemas.StepCompletion])
def read_completions(
    *,
    db: Session = Depends(session.get_db),
    mentee_id: uuid.UUID,
    current_user: models.User = Depends(security.get_current_active_user),
):
    completions = db.query(models.StepCompletion).filter(models.StepCompletion.mentee_id == mentee_id).all()
    return completions

@jumps_awards_router.post("/jumps", response_model=schemas.JumpLog, status_code=status.HTTP_201_CREATED)
def create_jump_log(
    *,
    db: Session = Depends(session.get_db),
    jump_in: schemas.JumpLogBase,
    current_user: models.User = Depends(mentee_only),
):
    db_jump = models.JumpLog(**jump_in.dict(), mentee_id=current_user.id)
    db.add(db_jump)
    db.commit()
    db.refresh(db_jump)
    return db_jump

@jumps_awards_router.get("/awards", response_model=List[schemas.Award])
def read_awards(
    *,
    db: Session = Depends(session.get_db),
    mentee_id: uuid.UUID,
    current_user: models.User = Depends(security.get_current_active_user),
):
    awards = db.query(models.Award).filter(models.Award.mentee_id == mentee_id).all()
    return awards
