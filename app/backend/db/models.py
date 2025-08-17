import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Role(str, enum.Enum):
    mentor = "mentor"
    mentee = "mentee"
    admin = "admin"

class ComfortLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class AttendanceStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"

class AssignmentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    declined = "declined"
    cancelled = "cancelled"

class ProgressionCategory(str, enum.Enum):
    two_way = "2way"
    three_way = "3way"
    canopy = "canopy"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(SAEnum(Role), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String)
    uspa_license = Column(String)
    jumps = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    mentor_profile = relationship("Mentor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    mentee_profile = relationship("Mentee", back_populates="user", uselist=False, cascade="all, delete-orphan")
    availability = relationship("Availability", back_populates="user")
    audit_events = relationship("AuditEvent", back_populates="actor")

class Mentor(Base):
    __tablename__ = "mentors"
    id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    ratings = Column(Text)
    coach_number = Column(String)
    disciplines = Column(JSON) # Changed from ARRAY
    max_concurrent_mentees = Column(Integer, default=2)
    seniority_score = Column(Integer, default=0)
    dz_endorsement = Column(Boolean, default=False)
    user = relationship("User", back_populates="mentor_profile")
    assignments = relationship("Assignment", back_populates="mentor")
    step_completions = relationship("StepCompletion", back_populates="mentor")
    jump_logs = relationship("JumpLog", back_populates="mentor")

class Mentee(Base):
    __tablename__ = "mentees"
    id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    goals = Column(Text)
    comfort_level = Column(SAEnum(ComfortLevel))
    canopy_size = Column(Integer)
    last_currency_date = Column(Date)
    user = relationship("User", back_populates="mentee_profile")
    attendance_requests = relationship("AttendanceRequest", back_populates="mentee")
    preferences = relationship("Preference", back_populates="mentee", uselist=False)
    assignments = relationship("Assignment", back_populates="mentee")
    step_completions = relationship("StepCompletion", back_populates="mentee")
    awards = relationship("Award", back_populates="mentee")
    jump_logs = relationship("JumpLog", back_populates="mentee")

class Availability(Base):
    __tablename__ = "availability"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(SAEnum(Role), nullable=False)
    day_of_week = Column(Integer)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    is_recurring = Column(Boolean, default=False)
    capacity_override = Column(Integer)
    user = relationship("User", back_populates="availability")

class SessionBlock(Base):
    __tablename__ = "session_blocks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False, index=True)
    end_time = Column(Time, nullable=False)
    dz_id = Column(UUID(as_uuid=True))
    load_interval_min = Column(Integer, default=20)
    block_capacity_hint = Column(Integer)
    attendance_requests = relationship("AttendanceRequest", back_populates="session_block")
    assignments = relationship("Assignment", back_populates="session_block")

class AttendanceRequest(Base):
    __tablename__ = "attendance_requests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentee_id = Column(UUID(as_uuid=True), ForeignKey("mentees.id"), nullable=False)
    session_block_id = Column(UUID(as_uuid=True), ForeignKey("session_blocks.id"), nullable=False)
    status = Column(SAEnum(AttendanceStatus), default=AttendanceStatus.pending)
    mentee = relationship("Mentee", back_populates="attendance_requests")
    session_block = relationship("SessionBlock", back_populates="attendance_requests")

class Preference(Base):
    __tablename__ = "preferences"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentee_id = Column(UUID(as_uuid=True), ForeignKey("mentees.id"), nullable=False, unique=True)
    preferred_mentors = Column(JSON, default=[]) # Changed from ARRAY
    avoid_mentors = Column(JSON, default=[]) # Changed from ARRAY
    notes = Column(Text)
    mentee = relationship("Mentee", back_populates="preferences")

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_block_id = Column(UUID(as_uuid=True), ForeignKey("session_blocks.id"), nullable=False, index=True)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.id"), nullable=False)
    mentee_id = Column(UUID(as_uuid=True), ForeignKey("mentees.id"), nullable=False)
    status = Column(SAEnum(AssignmentStatus), default=AssignmentStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    session_block = relationship("SessionBlock", back_populates="assignments")
    mentor = relationship("Mentor", back_populates="assignments")
    mentee = relationship("Mentee", back_populates="assignments")

class ProgressionStep(Base):
    __tablename__ = "progression_steps"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(SAEnum(ProgressionCategory), nullable=False)
    required = Column(Boolean, default=True)
    min_jumps_gate = Column(Integer, default=0)
    references = Column(JSON) # Changed from JSONB
    completions = relationship("StepCompletion", back_populates="step")

class StepCompletion(Base):
    __tablename__ = "step_completions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentee_id = Column(UUID(as_uuid=True), ForeignKey("mentees.id"), nullable=False)
    step_id = Column(UUID(as_uuid=True), ForeignKey("progression_steps.id"), nullable=False)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.id"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    evidence_url = Column(String)
    notes = Column(Text)
    mentee = relationship("Mentee", back_populates="step_completions")
    step = relationship("ProgressionStep", back_populates="completions")
    mentor = relationship("Mentor", back_populates="step_completions")

class Badge(Base):
    __tablename__ = "badges"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    criteria_json = Column(JSON) # Changed from JSONB
    awards = relationship("Award", back_populates="badge")

class Award(Base):
    __tablename__ = "awards"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentee_id = Column(UUID(as_uuid=True), ForeignKey("mentees.id"), nullable=False)
    badge_id = Column(UUID(as_uuid=True), ForeignKey("badges.id"), nullable=False)
    awarded_at = Column(DateTime, default=datetime.utcnow)
    mentee = relationship("Mentee", back_populates="awards")
    badge = relationship("Badge", back_populates="awards")

class JumpLog(Base):
    __tablename__ = "jump_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentee_id = Column(UUID(as_uuid=True), ForeignKey("mentees.id"), nullable=False)
    date = Column(Date, nullable=False)
    jump_number = Column(Integer)
    aircraft = Column(String)
    exit_alt = Column(Integer)
    freefall_time = Column(Integer)
    deployment_alt = Column(Integer)
    pattern_notes = Column(Text)
    drill_ref = Column(String)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.id"))
    mentee = relationship("Mentee", back_populates="jump_logs")
    mentor = relationship("Mentor", back_populates="jump_logs")

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    type = Column(String, nullable=False)
    payload_json = Column(JSON) # Changed from JSONB
    at = Column(DateTime, default=datetime.utcnow)
    actor = relationship("User", back_populates="audit_events")
