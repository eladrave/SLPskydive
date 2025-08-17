from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, time, timedelta, datetime
from typing import List

from db import session, schemas, models
from core import security, rbac

router = APIRouter()

admin_only = rbac.RoleChecker([schemas.Role.admin])

@router.get("/", response_model=List[schemas.SessionBlock])
def read_sessions(
    *,
    db: Session = Depends(session.get_db),
    date: date,
    current_user: models.User = Depends(security.get_current_active_user),
):
    sessions = db.query(models.SessionBlock).filter(models.SessionBlock.date == date).order_by(models.SessionBlock.start_time).all()
    return sessions

@router.post("/materialize", status_code=status.HTTP_201_CREATED)
def materialize_sessions(
    *,
    db: Session = Depends(session.get_db),
    request: schemas.SessionMaterializeRequest,
    current_user: models.User = Depends(admin_only),
):
    start_date = request.from_date
    end_date = request.to_date
    template = request.template

    try:
        start_time = time.fromisoformat(str(template["start_time"]))
        end_time = time.fromisoformat(str(template["end_time"]))
        interval_min = int(template["interval_min"])
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid template format: {e}")

    current_date = start_date
    created_count = 0
    while current_date <= end_date:
        current_time = start_time
        while True:
            current_datetime = datetime.combine(date.min, current_time)
            end_datetime = current_datetime + timedelta(minutes=interval_min)

            if end_datetime.time() > end_time:
                break

            block_end_time = end_datetime.time()

            exists = db.query(models.SessionBlock).filter_by(date=current_date, start_time=current_time).first()
            if not exists:
                db_session_block = models.SessionBlock(
                    date=current_date, start_time=current_time, end_time=block_end_time, load_interval_min=interval_min
                )
                db.add(db_session_block)
                created_count += 1

            current_time = block_end_time
            if current_time == end_time:
                break

        current_date += timedelta(days=1)

    db.commit()
    return {"message": f"Successfully created {created_count} new session blocks."}
