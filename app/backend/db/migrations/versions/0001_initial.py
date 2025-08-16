"""
Initial schema: core entities, enums, and indexes

Revision ID: 0001_initial
Revises: 
Create Date: 2025-08-16
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql


# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    role_enum = sa.Enum("mentor", "mentee", "admin", name="role_enum")
    comfort_level_enum = sa.Enum("low", "medium", "high", name="comfort_level_enum")
    attendance_status_enum = sa.Enum(
        "pending", "confirmed", "cancelled", name="attendance_status_enum"
    )
    assignment_status_enum = sa.Enum(
        "pending", "confirmed", "declined", "cancelled", name="assignment_status_enum"
    )
    progression_category_enum = sa.Enum(
        "2way", "3way", "canopy", name="progression_category_enum"
    )

    bind = op.get_bind()
    role_enum.create(bind, checkfirst=True)
    comfort_level_enum.create(bind, checkfirst=True)
    attendance_status_enum.create(bind, checkfirst=True)
    assignment_status_enum.create(bind, checkfirst=True)
    progression_category_enum.create(bind, checkfirst=True)

    # users
    op.create_table(
        "users",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("uspa_license", sa.String(length=16), nullable=True),
        sa.Column("jumps", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_role", "users", ["role"], unique=False)

    # mentors
    op.create_table(
        "mentors",
        sa.Column(
            "user_id",
            psql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("ratings", sa.Text(), nullable=True),
        sa.Column("coach_number", sa.String(length=64), nullable=True),
        sa.Column("disciplines", psql.ARRAY(sa.String()), nullable=True),
        sa.Column("max_concurrent_mentees", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("seniority_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dz_endorsement", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    # mentees
    op.create_table(
        "mentees",
        sa.Column(
            "user_id",
            psql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("goals", sa.Text(), nullable=True),
        sa.Column("comfort_level", comfort_level_enum, nullable=True),
        sa.Column("canopy_size", sa.Integer(), nullable=True),
        sa.Column("last_currency_date", sa.Date(), nullable=True),
    )

    # session_blocks
    op.create_table(
        "session_blocks",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(timezone=False), nullable=False),
        sa.Column("end_time", sa.Time(timezone=False), nullable=False),
        sa.Column("dz_id", psql.UUID(as_uuid=True), nullable=True),
        sa.Column("load_interval_min", sa.Integer(), nullable=True),
        sa.Column("block_capacity_hint", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_session_blocks_date_start_time",
        "session_blocks",
        ["date", "start_time"],
        unique=False,
    )

    # availability
    op.create_table(
        "availability",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            psql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(timezone=False), nullable=False),
        sa.Column("end_time", sa.Time(timezone=False), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("capacity_override", sa.Integer(), nullable=True),
        sa.CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name="ck_availability_day_of_week"),
    )
    op.create_index(
        "ix_availability_user_day", "availability", ["user_id", "day_of_week"], unique=False
    )

    # attendance_requests
    op.create_table(
        "attendance_requests",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "mentee_id",
            psql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "session_block_id",
            psql.UUID(as_uuid=True),
            sa.ForeignKey("session_blocks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", attendance_status_enum, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_attendance_requests_mentee_id", "attendance_requests", ["mentee_id"], False)
    op.create_index(
        "ix_attendance_requests_session_block_id", "attendance_requests", ["session_block_id"], False
    )

    # preferences
    op.create_table(
        "preferences",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "mentee_id",
            psql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "preferred_mentors",
            psql.ARRAY(psql.UUID(as_uuid=True)),
            nullable=False,
            server_default=sa.text("'{}'::uuid[]"),
        ),
        sa.Column(
            "avoid_mentors",
            psql.ARRAY(psql.UUID(as_uuid=True)),
            nullable=False,
            server_default=sa.text("'{}'::uuid[]"),
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.UniqueConstraint("mentee_id", name="uq_preferences_mentee"),
    )

    # assignments
    op.create_table(
        "assignments",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "session_block_id",
            psql.UUID(as_uuid=True),
            sa.ForeignKey("session_blocks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "mentor_id",
            psql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "mentee_id",
            psql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", assignment_status_enum, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_assignments_session_block", "assignments", ["session_block_id"], unique=False)

    # progression_steps
    op.create_table(
        "progression_steps",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", progression_category_enum, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("reference_url", sa.String(length=1024), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_progression_steps_category", "progression_steps", ["category"], False)

    # step_completions
    op.create_table(
        "step_completions",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "step_id",
            psql.UUID(as_uuid=True),
            sa.ForeignKey("progression_steps.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("mentee_id", psql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mentor_id", psql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("evidence_url", sa.String(length=1024), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_step_completion_mentee_date", "step_completions", ["mentee_id", "completed_at"], unique=False
    )

    # badges
    op.create_table(
        "badges",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("criteria_json", psql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.UniqueConstraint("code", name="uq_badges_code"),
    )
    op.create_index("ix_badges_code", "badges", ["code"], unique=False)

    # awards
    op.create_table(
        "awards",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("badge_id", psql.UUID(as_uuid=True), sa.ForeignKey("badges.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mentee_id", psql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("awarded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_awards_mentee_date", "awards", ["mentee_id", "awarded_at"], unique=False)

    # jump_logs
    op.create_table(
        "jump_logs",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("mentee_id", psql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("aircraft", sa.String(length=64), nullable=True),
        sa.Column("exit_altitude", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_jump_logs_mentee_id", "jump_logs", ["mentee_id"], unique=False)

    # audit_events
    op.create_table(
        "audit_events",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", psql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("metadata_json", psql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("audit_events")
    op.drop_index("ix_jump_logs_mentee_id", table_name="jump_logs")
    op.drop_table("jump_logs")
    op.drop_index("ix_awards_mentee_date", table_name="awards")
    op.drop_table("awards")
    op.drop_index("ix_badges_code", table_name="badges")
    op.drop_table("badges")
    op.drop_index("ix_step_completion_mentee_date", table_name="step_completions")
    op.drop_table("step_completions")
    op.drop_index("ix_progression_steps_category", table_name="progression_steps")
    op.drop_table("progression_steps")
    op.drop_index("ix_assignments_session_block", table_name="assignments")
    op.drop_table("assignments")
    op.drop_table("preferences")
    op.drop_index("ix_attendance_requests_session_block_id", table_name="attendance_requests")
    op.drop_index("ix_attendance_requests_mentee_id", table_name="attendance_requests")
    op.drop_table("attendance_requests")
    op.drop_index("ix_availability_user_day", table_name="availability")
    op.drop_table("availability")
    op.drop_index("ix_session_blocks_date_start_time", table_name="session_blocks")
    op.drop_table("session_blocks")
    op.drop_table("mentees")
    op.drop_table("mentors")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    # Drop ENUM types last
    bind = op.get_bind()
    sa.Enum(name="progression_category_enum").drop(bind, checkfirst=True)
    sa.Enum(name="assignment_status_enum").drop(bind, checkfirst=True)
    sa.Enum(name="attendance_status_enum").drop(bind, checkfirst=True)
    sa.Enum(name="comfort_level_enum").drop(bind, checkfirst=True)
    sa.Enum(name="role_enum").drop(bind, checkfirst=True)
