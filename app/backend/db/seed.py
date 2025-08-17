import logging
from datetime import date, time, timedelta

from sqlalchemy.orm import Session

from db import models, schemas
from core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_data(db: Session):
    if db.query(models.User).first():
        logger.info("Database already seeded. Skipping.")
        return

    logger.info("Seeding database with initial data...")

    hashed_password = get_password_hash("password")

    mentors_data = [
        models.User(
            email=f"m{i}@example.com",
            name=f"Mentor {i}",
            hashed_password=hashed_password,
            role=schemas.Role.mentor,
            is_active=True,
            jumps=100 + i * 10,
            mentor_profile=models.Mentor(
                ratings="Coach, AFFI", coach_number=f"C-{12345+i}", disciplines=["Belly", "Freefly"], seniority_score=i
            )
        ) for i in range(1, 11)
    ]
    mentors_data[0].email = "m1@example.com"

    mentees_data = [
        models.User(
            email=f"e{i}@example.com",
            name=f"Mentee {i}",
            hashed_password=hashed_password,
            role=schemas.Role.mentee,
            is_active=True,
            jumps=10 + i,
            mentee_profile=models.Mentee(
                goals="Learn belly skills", comfort_level=schemas.ComfortLevel.medium, canopy_size=210 - i*2
            )
        ) for i in range(1, 25)
    ]
    mentees_data[0].email = "e1@example.com"

    admin_user = models.User(
        email="admin@example.com", name="Admin User", hashed_password=get_password_hash("admin"), role=schemas.Role.admin, is_active=True
    )

    db.add_all(mentors_data)
    db.add_all(mentees_data)
    db.add(admin_user)
    db.commit()

    days = [1, 3, 5, 6]
    all_mentors = db.query(models.User).filter(models.User.role == schemas.Role.mentor).all()
    availability_data = [
        models.Availability(
            user_id=mentor.id, role=schemas.Role.mentor, day_of_week=day, start_time=time(8, 0), end_time=time(17, 0), is_recurring=True
        ) for mentor in all_mentors for day in days
    ]
    db.add_all(availability_data)

    progression_steps_data = [
        models.ProgressionStep(code="2W_SIDEBODY", title="Sidebody to Sidebody", description="Basic relative work drill.", category=schemas.ProgressionCategory.two_way),
        models.ProgressionStep(code="2W_360_DOCK", title="360 Dock", description="Perform a 360 turn and dock.", category=schemas.ProgressionCategory.two_way),
        models.ProgressionStep(code="3W_STAR", title="3-Way Star", description="Build a 3-way star formation.", category=schemas.ProgressionCategory.three_way, min_jumps_gate=25),
    ]
    db.add_all(progression_steps_data)

    badges_data = [
        models.Badge(code="FIRST_STAR", name="First Star", description="Complete your first 3-way star.", criteria_json={"step_code": "3W_STAR"}),
        models.Badge(code="STREAK_3", name="Streak-3", description="Attend 3 weekend days in a row.", criteria_json={"type": "attendance", "streak": 3}),
    ]
    db.add_all(badges_data)

    today = date.today()
    next_saturday = today + timedelta(days=(5 - today.weekday() + 7) % 7)
    session_dates = [next_saturday, next_saturday + timedelta(days=1)]
    session_times = [(time(8, 0), time(9, 30)), (time(9, 30), time(11, 0))]
    session_blocks_data = [
        models.SessionBlock(date=day, start_time=start, end_time=end)
        for day in session_dates for start, end in session_times
    ]
    db.add_all(session_blocks_data)

    db.commit()
    logger.info("Database seeding completed.")

if __name__ == "__main__":
    from db.session import SessionLocal
    db = SessionLocal()
    seed_data(db)
    db.close()
