from __future__ import annotations

import uuid
from datetime import date, time, datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


# Enums
class RoleEnum(str, Enum):
    mentor = "mentor"
    mentee = "mentee"
    admin = "admin"


class ComfortLevelEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AttendanceStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class AssignmentStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    declined = "declined"
    cancelled = "cancelled"


class ProgressionCategoryEnum(str, Enum):
    two_way = "2way"
    three_way = "3way"
    canopy = "canopy"


ROLE = SAEnum(RoleEnum, name="role_enum")
COMFORT = SAEnum(ComfortLevelEnum, name="comfort_level_enum")
ATTENDANCE = SAEnum(AttendanceStatusEnum, name="attendance_status_enum")
ASSIGNMENT = SAEnum(AssignmentStatusEnum, name="assignment_status_enum")
PROG_CAT = SAEnum(ProgressionCategoryEnum, name="progression_category_enum")


# Models
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(ROLE, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(32))
    uspa_license: Mapped[str | None] = mapped_column(String(16))
    jumps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    mentor_profile: Mapped["Mentor" | None] = relationship("Mentor", back_populates="user", uselist=False)
    mentee_profile: Mapped["Mentee" | None] = relationship("Mentee", back_populates="user", uselist=False)


class Mentor(Base):
    __tablename__ = "mentors"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    ratings: Mapped[str | None] = mapped_column(Text())
    coach_number: Mapped[str | None] = mapped_column(String(64))
    disciplines: Mapped[list[str] | None] = mapped_column(ARRAY(String()), default=list)
    max_concurrent_mentees: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    seniority_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dz_endorsement: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="mentor_profile")


class Mentee(Base):
    __tablename__ = "mentees"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    goals: Mapped[str | None] = mapped_column(Text())
    comfort_level: Mapped[ComfortLevelEnum | None] = mapped_column(COMFORT)
    canopy_size: Mapped[int | None] = mapped_column(Integer)
    last_currency_date: Mapped[date | None] = mapped_column(Date)

    user: Mapped[User] = relationship("User", back_populates="mentee_profile")


class Availability(Base):
    __tablename__ = "availability"
    __table_args__ = (
        Index("ix_availability_user_day", "user_id", "day_of_week"),
        CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name="ck_availability_day_of_week"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[RoleEnum] = mapped_column(ROLE, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time(timezone=False), nullable=False)
    end_time: Mapped[time] = mapped_column(Time(timezone=False), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    capacity_override: Mapped[int | None] = mapped_column(Integer)


class SessionBlock(Base):
    __tablename__ = "session_blocks"
    __table_args__ = (
        Index("ix_session_blocks_date_start_time", "date", "start_time"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time(timezone=False), nullable=False)
    end_time: Mapped[time] = mapped_column(Time(timezone=False), nullable=False)
    dz_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    load_interval_min: Mapped[int | None] = mapped_column(Integer)
    block_capacity_hint: Mapped[int | None] = mapped_column(Integer)


class AttendanceRequest(Base):
    __tablename__ = "attendance_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_block_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("session_blocks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[AttendanceStatusEnum] = mapped_column(
        ATTENDANCE, nullable=False, default=AttendanceStatusEnum.pending
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Preference(Base):
    __tablename__ = "preferences"
    __table_args__ = (UniqueConstraint("mentee_id", name="uq_preferences_mentee"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    preferred_mentors: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), server_default="{}"
    )
    avoid_mentors: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), server_default="{}")
    notes: Mapped[str | None] = mapped_column(Text())


class Assignment(Base):
    __tablename__ = "assignments"
    __table_args__ = (
        Index("ix_assignments_session_block", "session_block_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_block_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("session_blocks.id", ondelete="CASCADE"), nullable=False
    )
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mentee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[AssignmentStatusEnum] = mapped_column(
        ASSIGNMENT, default=AssignmentStatusEnum.pending, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class ProgressionStep(Base):
    __tablename__ = "progression_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[ProgressionCategoryEnum] = mapped_column(PROG_CAT, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text())
    reference_url: Mapped[str | None] = mapped_column(String(1024))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class StepCompletion(Base):
    __tablename__ = "step_completions"
    __table_args__ = (
        Index("ix_step_completion_mentee_date", "mentee_id", "completed_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("progression_steps.id", ondelete="CASCADE"), nullable=False
    )
    mentee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    evidence_url: Mapped[str | None] = mapped_column(String(1024))
    notes: Mapped[str | None] = mapped_column(Text())
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    criteria_json: Mapped[dict | None] = mapped_column(JSONB)


class Award(Base):
    __tablename__ = "awards"
    __table_args__ = (
        Index("ix_awards_mentee_date", "mentee_id", "awarded_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    badge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("badges.id", ondelete="CASCADE"), nullable=False
    )
    mentee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    awarded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text())


class JumpLog(Base):
    __tablename__ = "jump_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255))
    aircraft: Mapped[str | None] = mapped_column(String(64))
    exit_altitude: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text())


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    metadata_json: Mapped[dict | None] = mapped_column(JSONB)
