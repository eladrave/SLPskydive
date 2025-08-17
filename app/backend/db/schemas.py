from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uuid
from datetime import date, time, datetime

from .models import Role, ComfortLevel, AttendanceStatus, AssignmentStatus, ProgressionCategory

# Base Schemas (common attributes)
class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    uspa_license: Optional[str] = None
    jumps: Optional[int] = 0
    is_active: Optional[bool] = True

class MentorBase(BaseModel):
    ratings: Optional[str] = None
    coach_number: Optional[str] = None
    disciplines: Optional[List[str]] = []
    max_concurrent_mentees: Optional[int] = 2
    seniority_score: Optional[int] = 0
    dz_endorsement: Optional[bool] = False

class MenteeBase(BaseModel):
    goals: Optional[str] = None
    comfort_level: Optional[ComfortLevel] = None
    canopy_size: Optional[int] = None
    last_currency_date: Optional[date] = None

# Create Schemas (for POST requests)
class UserCreate(UserBase):
    password: str
    role: Role

class MentorCreate(MentorBase):
    pass

class MenteeCreate(MenteeBase):
    pass

class UserCreateWithProfiles(UserCreate):
    mentor_profile: Optional[MentorCreate] = None
    mentee_profile: Optional[MenteeCreate] = None

# Update Schemas (for PUT/PATCH requests)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    uspa_license: Optional[str] = None
    jumps: Optional[int] = None

class MentorUpdate(MentorBase):
    pass

class MenteeUpdate(MenteeBase):
    pass

# Response Schemas (for GET requests, with ORM mode)
class Mentor(MentorBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class Mentee(MenteeBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class User(UserBase):
    id: uuid.UUID
    role: Role
    created_at: datetime
    mentor_profile: Optional[Mentor] = None
    mentee_profile: Optional[Mentee] = None

    class Config:
        orm_mode = True

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[Role] = None


# Availability
class AvailabilityBase(BaseModel):
    role: Role
    start_time: time
    end_time: time
    is_recurring: bool = False
    day_of_week: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    capacity_override: Optional[int] = None

class AvailabilityCreate(AvailabilityBase):
    user_id: uuid.UUID

class Availability(AvailabilityBase):
    id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        orm_mode = True


# Session Block
class SessionBlockBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    load_interval_min: Optional[int] = 20
    block_capacity_hint: Optional[int] = None

class SessionBlockCreate(SessionBlockBase):
    pass

class SessionBlock(SessionBlockBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class SessionMaterializeRequest(BaseModel):
    from_date: date
    to_date: date
    template: dict # e.g. { "start_time": "08:00", "end_time": "16:00", "interval_min": 90 }

# Attendance Request
class AttendanceRequestBase(BaseModel):
    session_block_id: uuid.UUID

class AttendanceRequestCreate(AttendanceRequestBase):
    pass

class AttendanceRequest(AttendanceRequestBase):
    id: uuid.UUID
    mentee_id: uuid.UUID
    status: AttendanceStatus

    class Config:
        orm_mode = True

# Preference
class PreferenceBase(BaseModel):
    preferred_mentors: Optional[List[uuid.UUID]] = []
    avoid_mentors: Optional[List[uuid.UUID]] = []
    notes: Optional[str] = None

class PreferenceCreate(PreferenceBase):
    pass

class PreferenceUpdate(PreferenceBase):
    pass

class Preference(PreferenceBase):
    id: uuid.UUID
    mentee_id: uuid.UUID

    class Config:
        orm_mode = True

# Assignment
class AssignmentBase(BaseModel):
    session_block_id: uuid.UUID
    mentor_id: uuid.UUID
    mentee_id: uuid.UUID
    status: AssignmentStatus

class Assignment(AssignmentBase):
    id: uuid.UUID
    created_at: datetime
    mentor: User
    mentee: User

    class Config:
        orm_mode = True

# Progression Step
class ProgressionStepBase(BaseModel):
    code: str
    title: str
    description: Optional[str] = None
    category: ProgressionCategory
    required: bool = True
    min_jumps_gate: int = 0
    references: Optional[dict] = None

class ProgressionStepCreate(ProgressionStepBase):
    pass

class ProgressionStep(ProgressionStepBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

# Step Completion
class StepCompletionBase(BaseModel):
    evidence_url: Optional[str] = None
    notes: Optional[str] = None

class StepCompletionCreate(StepCompletionBase):
    step_id: uuid.UUID
    mentor_id: uuid.UUID
    mentee_id: uuid.UUID

class StepCompletion(StepCompletionBase):
    id: uuid.UUID
    step_id: uuid.UUID
    mentor_id: uuid.UUID
    mentee_id: uuid.UUID
    completed_at: datetime

    class Config:
        orm_mode = True

# Badge
class BadgeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    criteria_json: dict

class BadgeCreate(BadgeBase):
    pass

class Badge(BadgeBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

# Award
class AwardBase(BaseModel):
    badge_id: uuid.UUID

class AwardCreate(AwardBase):
    mentee_id: uuid.UUID

class Award(AwardBase):
    id: uuid.UUID
    mentee_id: uuid.UUID
    awarded_at: datetime

    class Config:
        orm_mode = True

# Jump Log
class JumpLogBase(BaseModel):
    date: date
    jump_number: Optional[int] = None
    aircraft: Optional[str] = None
    exit_alt: Optional[int] = None
    freefall_time: Optional[int] = None
    deployment_alt: Optional[int] = None
    pattern_notes: Optional[str] = None
    drill_ref: Optional[str] = None
    mentor_id: Optional[uuid.UUID] = None

class JumpLogCreate(JumpLogBase):
    mentee_id: uuid.UUID

class JumpLog(JumpLogBase):
    id: uuid.UUID
    mentee_id: uuid.UUID

    class Config:
        orm_mode = True

# Admin
class Roster(BaseModel):
    session_block: SessionBlock
    assignments: List[Assignment]

class AdminStats(BaseModel):
    mentors_available: int
    mentees_requesting: int
    assignments_made: int
    completion_rate: float
