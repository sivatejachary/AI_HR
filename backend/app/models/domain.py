import uuid
from datetime import datetime, date, time
from enum import Enum as PyEnum
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    String, Integer, BigInteger, Boolean, DateTime, Date, Time, Text, ForeignKey,
    Numeric, UniqueConstraint, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB as PG_JSONB, INET
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Cross-dialect JSONB definition (Native PostgreSQL JSONB with standard JSON fallback for SQLite/tests)
JSONB = JSON().with_variant(PG_JSONB, "postgresql")

class Base(DeclarativeBase):
    pass

# Helper function for generating stringified UUIDs where needed
def gen_uuid_str() -> str:
    return str(uuid.uuid4())

# ============================================================
# ENUM DEFINITIONS
# ============================================================

class UserRole(str, PyEnum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    HR_ADMIN = "HR_ADMIN"
    RECRUITER = "RECRUITER"
    HIRING_MANAGER = "HIRING_MANAGER"
    INTERVIEWER = "INTERVIEWER"
    VIEWER = "VIEWER"

class JobStatus(str, PyEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    PAUSED = "PAUSED"
    EXPIRED = "EXPIRED"
    CLOSED = "CLOSED"

class WorkplaceType(str, PyEnum):
    ON_SITE = "ON_SITE"
    HYBRID = "HYBRID"
    REMOTE = "REMOTE"

class DistributionStatus(str, PyEnum):
    NOT_CONNECTED = "NOT_CONNECTED"
    READY = "READY"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    UPDATE_PENDING = "UPDATE_PENDING"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    PAUSED = "PAUSED"

class ApplicationSource(str, PyEnum):
    LINKEDIN = "LINKEDIN"
    INDEED = "INDEED"
    NAUKRI = "NAUKRI"
    FOUNDIT = "FOUNDIT"
    CAREER_PAGE = "CAREER_PAGE"
    AI_HR_FORM = "AI_HR_FORM"
    GOOGLE_FORM = "GOOGLE_FORM"
    MICROSOFT_FORM = "MICROSOFT_FORM"
    CSV_IMPORT = "CSV_IMPORT"
    MANUAL = "MANUAL"

class ApplicationStatus(str, PyEnum):
    NEW = "NEW"
    SCREENING = "SCREENING"
    AI_SHORTLISTED = "AI_SHORTLISTED"
    HR_REVIEW = "HR_REVIEW"
    HR_APPROVED = "HR_APPROVED"
    HR_REJECTED = "HR_REJECTED"
    CALL_PENDING = "CALL_PENDING"
    CALLING = "CALLING"
    CALL_COMPLETED = "CALL_COMPLETED"
    INTERVIEW_PENDING = "INTERVIEW_PENDING"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    INTERVIEW_COMPLETED = "INTERVIEW_COMPLETED"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

class StepType(str, PyEnum):
    RESUME_SCREENING = "RESUME_SCREENING"
    HR_CALL = "HR_CALL"
    SCHEDULE_INTERVIEW = "SCHEDULE_INTERVIEW"
    AI_INTERVIEW = "AI_INTERVIEW"
    CODING_INTERVIEW = "CODING_INTERVIEW"
    BEHAVIORAL_INTERVIEW = "BEHAVIORAL_INTERVIEW"
    HUMAN_INTERVIEW = "HUMAN_INTERVIEW"
    ASSESSMENT = "ASSESSMENT"
    HR_REVIEW = "HR_REVIEW"
    HIRING_MANAGER_REVIEW = "HIRING_MANAGER_REVIEW"
    APPROVAL = "APPROVAL"
    REJECTION = "REJECTION"
    OFFER = "OFFER"
    CUSTOM_ACTION = "CUSTOM_ACTION"
    WAIT = "WAIT"
    NOTIFICATION = "NOTIFICATION"
    HUMAN_ACTION = "HUMAN_ACTION"
    AI_ACTION = "AI_ACTION"
    VOICE_CALL = "VOICE_CALL"
    EMAIL = "EMAIL"
    SCHEDULING = "SCHEDULING"
    INTERVIEW = "INTERVIEW"
    DOCUMENT_COLLECTION = "DOCUMENT_COLLECTION"
    CONDITION = "CONDITION"
    ONBOARDING = "ONBOARDING"


# ============================================================
# 5. ORGANIZATION TABLES
# ============================================================

class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255))
    industry: Mapped[Optional[str]] = mapped_column(String(150))
    website: Mapped[Optional[str]] = mapped_column(String(500))
    logo_url: Mapped[Optional[str]] = mapped_column(Text)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    address: Mapped[Optional[str]] = mapped_column(Text)
    timezone: Mapped[str] = mapped_column(String(100), default="UTC")
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", index=True)
    settings: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class OrganizationSetting(Base):
    __tablename__ = "organization_settings"
    __table_args__ = (UniqueConstraint("organization_id", "setting_key", name="uq_org_setting_key"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    setting_key: Mapped[str] = mapped_column(String(150), nullable=False)
    setting_value: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================
# 6. USERS & RBAC
# ============================================================

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("organization_id", "email", name="uq_user_org_email"),
        Index("idx_users_org_id", "organization_id"),
        Index("idx_users_email", "email"),
        Index("idx_users_status", "status")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(Text)
    hashed_password: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    job_title: Mapped[Optional[str]] = mapped_column(String(150))
    role: Mapped[str] = mapped_column(String(50), default="RECRUITER")
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_role_org_name"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class UserRoleAssoc(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[str] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class UserSession(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token_hash: Mapped[Optional[str]] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 7. JOB TABLES
# ============================================================

class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        Index("idx_jobs_org_id", "organization_id"),
        Index("idx_jobs_status", "status"),
        Index("idx_jobs_created_by", "created_by")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    workflow_id: Mapped[Optional[str]] = mapped_column(ForeignKey("hiring_workflows.id"))
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_code: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    department: Mapped[str] = mapped_column(String(150), nullable=False)
    employment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    workplace_type: Mapped[str] = mapped_column(String(30), default="REMOTE")
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    experience_min: Mapped[Optional[float]] = mapped_column(Numeric(4, 1), default=0.0)
    experience_max: Mapped[Optional[float]] = mapped_column(Numeric(4, 1), default=10.0)
    min_experience: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    max_experience: Mapped[Optional[int]] = mapped_column(Integer, default=10)
    salary_min: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    salary_max: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    salary_currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD")
    work_mode: Mapped[Optional[str]] = mapped_column(String(30), default="REMOTE")
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    openings: Mapped[int] = mapped_column(Integer, default=1)
    responsibilities: Mapped[Optional[str]] = mapped_column(Text)
    requirements: Mapped[Optional[str]] = mapped_column(Text)
    preferred_skills: Mapped[List[str]] = mapped_column(JSONB, default=list)
    education: Mapped[Optional[str]] = mapped_column(String(255))
    certifications: Mapped[Optional[str]] = mapped_column(String(255))
    notice_period: Mapped[Optional[str]] = mapped_column(String(100))
    languages: Mapped[List[str]] = mapped_column(JSONB, default=list)
    application_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    google_form_id: Mapped[Optional[str]] = mapped_column(String(255))
    google_form_url: Mapped[Optional[str]] = mapped_column(Text)
    google_responder_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class JobSkill(Base):
    __tablename__ = "job_skills"
    __table_args__ = (
        Index("idx_job_skills_job_id", "job_id"),
        Index("idx_job_skills_name", "skill_name")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(150), nullable=False)
    skill_type: Mapped[Optional[str]] = mapped_column(String(30))
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    minimum_experience: Mapped[Optional[float]] = mapped_column(Numeric(4, 1))
    weight: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class JobLocation(Base):
    __tablename__ = "job_locations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class JobQuestion(Base):
    __tablename__ = "job_questions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    options: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class JobDistribution(Base):
    __tablename__ = "job_distributions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    connection_status: Mapped[str] = mapped_column(String(30), default="CONNECTED")
    external_job_id: Mapped[Optional[str]] = mapped_column(String(255))
    external_url: Mapped[Optional[str]] = mapped_column(Text)
    publication_status: Mapped[str] = mapped_column(String(30), default="READY")
    status: Mapped[Optional[str]] = mapped_column(String(30))
    application_url: Mapped[Optional[str]] = mapped_column(Text)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    response_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class JobDistributionEvent(Base):
    __tablename__ = "job_distribution_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    job_distribution_id: Mapped[str] = mapped_column(ForeignKey("job_distributions.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 8. HIRING WORKFLOW TABLES
# ============================================================

class HiringWorkflow(Base):
    __tablename__ = "hiring_workflows"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    job_id: Mapped[Optional[str]] = mapped_column(ForeignKey("jobs.id"))
    job_title: Mapped[Optional[str]] = mapped_column(String(255))
    department: Mapped[Optional[str]] = mapped_column(String(150))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    workflow_type: Mapped[Optional[str]] = mapped_column(String(50))
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(30), default="Published")
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False)
    owner_name: Mapped[Optional[str]] = mapped_column(String(150), default="HR Recruiter")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class HiringWorkflowVersion(Base):
    __tablename__ = "hiring_workflow_versions"
    __table_args__ = (UniqueConstraint("workflow_id", "version_number", name="uq_wf_version_num"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    workflow_id: Mapped[str] = mapped_column(ForeignKey("hiring_workflows.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(30), default="Published")
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    steps_snapshot: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    workflow_version_id: Mapped[Optional[str]] = mapped_column(ForeignKey("hiring_workflow_versions.id", ondelete="CASCADE"))
    workflow_id: Mapped[Optional[str]] = mapped_column(ForeignKey("hiring_workflows.id", ondelete="CASCADE"))
    step_key: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    step_type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), default="Screening")
    type: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    order: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    purpose: Mapped[Optional[str]] = mapped_column(Text)
    owner: Mapped[Optional[str]] = mapped_column(String(100), default="HR")
    automation: Mapped[Optional[str]] = mapped_column(String(100), default="Manual")
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, default=30)
    passing_score: Mapped[Optional[int]] = mapped_column(Integer)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    configuration: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    timeout_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    retry_limit: Mapped[int] = mapped_column(Integer, default=0)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    conditions: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    questions: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    notifications: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    config: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkflowStepCondition(Base):
    __tablename__ = "workflow_step_conditions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    workflow_step_id: Mapped[str] = mapped_column(ForeignKey("workflow_steps.id", ondelete="CASCADE"), nullable=False)
    condition_type: Mapped[str] = mapped_column(String(50), nullable=False)
    condition_expression: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    next_step_id: Mapped[str] = mapped_column(ForeignKey("workflow_steps.id"), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 9. CANDIDATES & PROFILES
# ============================================================

class Candidate(Base):
    __tablename__ = "candidates"
    __table_args__ = (
        Index("idx_candidates_org_id", "organization_id"),
        Index("idx_candidates_email", "email"),
        Index("idx_candidates_phone", "phone"),
        Index("idx_candidates_status", "status")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    current_location: Mapped[Optional[str]] = mapped_column(String(255))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    current_company: Mapped[Optional[str]] = mapped_column(String(255))
    current_title: Mapped[Optional[str]] = mapped_column(String(255))
    total_experience_years: Mapped[Optional[float]] = mapped_column(Numeric(4, 1), default=0.0)
    years_experience: Mapped[Optional[float]] = mapped_column(Numeric(4, 1), default=0.0)
    resume_url: Mapped[Optional[str]] = mapped_column(Text)
    resume_text: Mapped[Optional[str]] = mapped_column(Text)
    resume_fingerprint: Mapped[Optional[str]] = mapped_column(String(255))
    skills: Mapped[List[str]] = mapped_column(JSONB, default=list)
    education: Mapped[Optional[str]] = mapped_column(String(255))
    source: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="NEW")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), unique=True, nullable=False)
    headline: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    notice_period_days: Mapped[Optional[int]] = mapped_column(Integer)
    expected_salary: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    current_salary: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    preferred_locations: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    preferred_work_mode: Mapped[Optional[str]] = mapped_column(String(50))
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text)
    github_url: Mapped[Optional[str]] = mapped_column(Text)
    portfolio_url: Mapped[Optional[str]] = mapped_column(Text)
    website_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(150), nullable=False)
    skill_category: Mapped[Optional[str]] = mapped_column(String(100))
    proficiency: Mapped[Optional[str]] = mapped_column(String(50))
    years_experience: Mapped[Optional[float]] = mapped_column(Numeric(4, 1))
    source: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class CandidateExperience(Base):
    __tablename__ = "candidate_experience"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    job_title: Mapped[Optional[str]] = mapped_column(String(255))
    employment_type: Mapped[Optional[str]] = mapped_column(String(50))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class CandidateEducation(Base):
    __tablename__ = "candidate_education"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    institution: Mapped[Optional[str]] = mapped_column(String(255))
    degree: Mapped[Optional[str]] = mapped_column(String(255))
    field_of_study: Mapped[Optional[str]] = mapped_column(String(255))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    grade: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class CandidateLink(Base):
    __tablename__ = "candidate_links"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    link_type: Mapped[Optional[str]] = mapped_column(String(50))
    url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 10. APPLICATIONS
# ============================================================

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("candidate_id", "job_id", name="uq_app_candidate_job"),
        Index("idx_apps_candidate_id", "candidate_id"),
        Index("idx_apps_job_id", "job_id"),
        Index("idx_apps_status", "status"),
        Index("idx_apps_org_id", "organization_id")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="NEW")
    current_stage: Mapped[Optional[str]] = mapped_column(String(100), default="Application")
    source: Mapped[Optional[str]] = mapped_column(String(50), default="CAREER_PAGE")
    source_id: Mapped[Optional[str]] = mapped_column(String(255))
    campaign_source: Mapped[Optional[str]] = mapped_column(String(255))
    current_workflow_id: Mapped[Optional[str]] = mapped_column(ForeignKey("hiring_workflows.id"))
    current_workflow_version: Mapped[int] = mapped_column(Integer, default=1)
    current_step_id: Mapped[Optional[str]] = mapped_column(String(255))
    current_step_name: Mapped[Optional[str]] = mapped_column(String(255), default="Application")
    step_status: Mapped[Optional[str]] = mapped_column(String(50), default="COMPLETED")
    execution_id: Mapped[Optional[str]] = mapped_column(String(255))
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class ApplicationSourceModel(Base):
    __tablename__ = "application_sources"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_name: Mapped[Optional[str]] = mapped_column(String(100))
    external_id: Mapped[Optional[str]] = mapped_column(String(255))
    external_url: Mapped[Optional[str]] = mapped_column(Text)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class ApplicationEvent(Base):
    __tablename__ = "application_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    old_status: Mapped[Optional[str]] = mapped_column(String(50))
    new_status: Mapped[Optional[str]] = mapped_column(String(50))
    actor_type: Mapped[Optional[str]] = mapped_column(String(30))
    actor_id: Mapped[Optional[str]] = mapped_column(String)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 11. CANDIDATE WORKFLOW EXECUTION
# ============================================================

class CandidateWorkflow(Base):
    __tablename__ = "candidate_workflows"
    __table_args__ = (
        Index("idx_cand_wf_candidate", "candidate_id"),
        Index("idx_cand_wf_application", "application_id"),
        Index("idx_cand_wf_status", "status"),
        Index("idx_cand_wf_step", "current_step_id")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id"), nullable=False)
    job_id: Mapped[Optional[str]] = mapped_column(ForeignKey("jobs.id"))
    workflow_id: Mapped[str] = mapped_column(ForeignKey("hiring_workflows.id"), nullable=False)
    workflow_version_id: Mapped[Optional[str]] = mapped_column(ForeignKey("hiring_workflow_versions.id"))
    workflow_version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="IN_PROGRESS")
    current_step_id: Mapped[Optional[str]] = mapped_column(ForeignKey("workflow_steps.id"))
    current_step_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False)
    is_human_takeover: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class CandidateWorkflowStep(Base):
    __tablename__ = "candidate_workflow_steps"
    __table_args__ = (
        Index("idx_cand_wf_steps_wf", "candidate_workflow_id"),
        Index("idx_cand_wf_steps_step", "workflow_step_id"),
        Index("idx_cand_wf_steps_status", "status")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    candidate_workflow_id: Mapped[str] = mapped_column(ForeignKey("candidate_workflows.id", ondelete="CASCADE"), nullable=False)
    workflow_step_id: Mapped[str] = mapped_column(ForeignKey("workflow_steps.id"), nullable=False)
    step_name: Mapped[Optional[str]] = mapped_column(String(255))
    step_type: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    attempts_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    skipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    result_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkflowExecutionLog(Base):
    __tablename__ = "workflow_execution_logs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    execution_id: Mapped[str] = mapped_column(String(255), index=True)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id"))
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"))
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"))
    workflow_id: Mapped[str] = mapped_column(ForeignKey("hiring_workflows.id"))
    workflow_version: Mapped[int] = mapped_column(Integer, default=1)
    step_id: Mapped[str] = mapped_column(String(255), nullable=False)
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    step_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    result_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    triggered_by: Mapped[str] = mapped_column(String(100), default="WorkflowEngine")
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), index=True)


# ============================================================
# 12. DOCUMENTS & RESUMES
# ============================================================

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    candidate_id: Mapped[Optional[str]] = mapped_column(ForeignKey("candidates.id"))
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="LOCAL")
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    checksum: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[Optional[str]] = mapped_column(String(30), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = (UniqueConstraint("document_id", "version_number", name="uq_doc_version_num"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    checksum: Mapped[Optional[str]] = mapped_column(String(255))
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class DocumentExtraction(Base):
    __tablename__ = "document_extractions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    extraction_type: Mapped[Optional[str]] = mapped_column(String(50))
    extracted_text: Mapped[Optional[str]] = mapped_column(Text)
    structured_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    model_name: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[Optional[str]] = mapped_column(String(30), default="COMPLETED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================
# 13. AI RESUME SCREENING
# ============================================================

class Screening(Base):
    __tablename__ = "screenings"
    __table_args__ = (
        Index("idx_screenings_app", "application_id"),
        Index("idx_screenings_cand", "candidate_id"),
        Index("idx_screenings_job", "job_id"),
        Index("idx_screenings_status", "status")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    screening_type: Mapped[Optional[str]] = mapped_column(String(50), default="RESUME_PARSER")
    status: Mapped[str] = mapped_column(String(30), default="COMPLETED")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    model_name: Mapped[Optional[str]] = mapped_column(String(100), default="Gemini-Pro-HR")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AIScreeningResult(Base):
    __tablename__ = "screening_results"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    screening_id: Mapped[Optional[str]] = mapped_column(ForeignKey("screenings.id"))
    application_id: Mapped[Optional[str]] = mapped_column(ForeignKey("applications.id"))
    overall_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    match_score: Mapped[Optional[int]] = mapped_column(Integer, default=85)
    match_percentage: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    recommendation: Mapped[Optional[str]] = mapped_column(String(50), default="SHORTLIST_FOR_HR_REVIEW")
    summary: Mapped[Optional[str]] = mapped_column(Text)
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    required_skills_match: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    missing_requirements: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    experience_match: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    strengths: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    gaps: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class ScreeningEvidence(Base):
    __tablename__ = "screening_evidence"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    screening_id: Mapped[str] = mapped_column(ForeignKey("screenings.id", ondelete="CASCADE"), nullable=False)
    requirement: Mapped[Optional[str]] = mapped_column(Text)
    evidence: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(100))
    match_status: Mapped[Optional[str]] = mapped_column(String(50))
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 14-16. GOOGLE INTEGRATIONS, FORMS & SHEETS
# ============================================================

class GoogleIntegration(Base):
    __tablename__ = "google_integrations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    google_subject_id: Mapped[str] = mapped_column(String(255), nullable=False)
    google_email: Mapped[str] = mapped_column(String(255), nullable=False)
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    scopes: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(30), default="CONNECTED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class GoogleForm(Base):
    __tablename__ = "google_forms"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    google_integration_id: Mapped[Optional[str]] = mapped_column(ForeignKey("google_integrations.id"))
    google_form_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    responder_url: Mapped[str] = mapped_column(Text, nullable=False)
    edit_url: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(30), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class GoogleFormField(Base):
    __tablename__ = "google_form_fields"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    google_form_id: Mapped[str] = mapped_column(ForeignKey("google_forms.id", ondelete="CASCADE"), nullable=False)
    google_item_id: Mapped[Optional[str]] = mapped_column(String(255))
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(String(50), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    configuration: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class GoogleFormResponse(Base):
    __tablename__ = "google_form_responses"
    __table_args__ = (UniqueConstraint("google_form_id", "google_response_id", name="uq_gform_resp"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    google_form_id: Mapped[str] = mapped_column(ForeignKey("google_forms.id", ondelete="CASCADE"), nullable=False)
    google_response_id: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_id: Mapped[Optional[str]] = mapped_column(ForeignKey("candidates.id"))
    raw_response: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    processing_status: Mapped[str] = mapped_column(String(30), default="INGESTED")
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class GoogleSheet(Base):
    __tablename__ = "google_sheets"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    google_integration_id: Mapped[str] = mapped_column(ForeignKey("google_integrations.id"), nullable=False)
    google_sheet_id: Mapped[str] = mapped_column(String(255), nullable=False)
    sheet_name: Mapped[Optional[str]] = mapped_column(String(255))
    sheet_url: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(30), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class GoogleSheetRow(Base):
    __tablename__ = "google_sheet_rows"
    __table_args__ = (UniqueConstraint("google_sheet_id", "sheet_tab_name", "row_number", name="uq_gsheet_tab_row"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    google_sheet_id: Mapped[str] = mapped_column(ForeignKey("google_sheets.id", ondelete="CASCADE"), nullable=False)
    sheet_tab_name: Mapped[Optional[str]] = mapped_column(String(255), default="Sheet1")
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_id: Mapped[Optional[str]] = mapped_column(ForeignKey("candidates.id"))
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    processing_status: Mapped[Optional[str]] = mapped_column(String(30), default="INGESTED")
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class ApplicationForm(Base):
    __tablename__ = "forms"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    public_url_slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    fields_config: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    custom_questions: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    google_form_id: Mapped[Optional[str]] = mapped_column(String)
    google_form_url: Mapped[Optional[str]] = mapped_column(String)
    google_responder_url: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 17. DATA INGESTION
# ============================================================

class IngestionEvent(Base):
    __tablename__ = "ingestion_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_external_id: Mapped[Optional[str]] = mapped_column(String(255))
    event_type: Mapped[Optional[str]] = mapped_column(String(100))
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    processing_status: Mapped[Optional[str]] = mapped_column(String(30), default="RECEIVED")
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class IngestionError(Base):
    __tablename__ = "ingestion_errors"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    ingestion_event_id: Mapped[str] = mapped_column(ForeignKey("ingestion_events.id", ondelete="CASCADE"), nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(String(100))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 18. AI HR VOICE CALLING
# ============================================================

class Call(Base):
    __tablename__ = "calls"
    __table_args__ = (
        Index("idx_calls_cand", "candidate_id"),
        Index("idx_calls_app", "application_id"),
        Index("idx_calls_interview", "interview_id"),
        Index("idx_calls_conv_id", "conversation_id"),
        Index("idx_calls_status", "status")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[Optional[str]] = mapped_column(ForeignKey("organizations.id"))
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    application_id: Mapped[Optional[str]] = mapped_column(ForeignKey("applications.id"))
    interview_id: Mapped[Optional[str]] = mapped_column(ForeignKey("interviews.id"))
    phone_number: Mapped[Optional[str]] = mapped_column(String(50))
    provider: Mapped[str] = mapped_column(String(50), default="ELEVENLABS")
    external_call_id: Mapped[Optional[str]] = mapped_column(String(255))
    conversation_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="INITIATED")
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    call_summary: Mapped[Optional[str]] = mapped_column(Text)
    transcript: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class CallAttempt(Base):
    __tablename__ = "call_attempts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    call_id: Mapped[str] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"), nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class CallTranscript(Base):
    __tablename__ = "call_transcripts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    call_id: Mapped[str] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"), nullable=False)
    transcript: Mapped[Optional[str]] = mapped_column(Text)
    transcript_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    language: Mapped[Optional[str]] = mapped_column(String(50), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class CallEvent(Base):
    __tablename__ = "call_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    call_id: Mapped[str] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 19-21. INTERVIEWS, AVAILABILITY & CALENDAR
# ============================================================

class Interview(Base):
    __tablename__ = "interviews"
    __table_args__ = (
        Index("idx_interviews_cand", "candidate_id"),
        Index("idx_interviews_app", "application_id"),
        Index("idx_interviews_job", "job_id"),
        Index("idx_interviews_status", "status"),
        Index("idx_interviews_start", "scheduled_start")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[Optional[str]] = mapped_column(ForeignKey("organizations.id"))
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    application_id: Mapped[Optional[str]] = mapped_column(ForeignKey("applications.id"))
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    interview_type: Mapped[str] = mapped_column(String(50), default="Technical")
    type: Mapped[Optional[str]] = mapped_column(String(50), default="Technical")
    date: Mapped[Optional[str]] = mapped_column(String(50))
    time: Mapped[Optional[str]] = mapped_column(String(50))
    platform: Mapped[Optional[str]] = mapped_column(String(50), default="Google Meet")
    meeting_link: Mapped[Optional[str]] = mapped_column(Text)
    interviewer_name: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="UPCOMING")
    scheduled_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    scheduled_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    timezone: Mapped[Optional[str]] = mapped_column(String(100), default="UTC")
    interviewer_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    calendar_event_id: Mapped[Optional[str]] = mapped_column(String)
    meeting_id: Mapped[Optional[str]] = mapped_column(String)
    meeting_provider: Mapped[Optional[str]] = mapped_column(String(50), default="GOOGLE_MEET")
    meeting_url: Mapped[Optional[str]] = mapped_column(Text)
    meeting_session_id: Mapped[Optional[str]] = mapped_column(String)
    meeting_status: Mapped[Optional[str]] = mapped_column(String(50), default="CREATED")
    meeting_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    meeting_ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ai_participant_id: Mapped[Optional[str]] = mapped_column(String)
    candidate_participant_id: Mapped[Optional[str]] = mapped_column(String)
    interviewer_participant_id: Mapped[Optional[str]] = mapped_column(String)
    ai_connection_status: Mapped[Optional[str]] = mapped_column(String(50), default="DISCONNECTED")
    last_media_event_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class InterviewAvailability(Base):
    __tablename__ = "interview_availability"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    interview_id: Mapped[str] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    available_date: Mapped[Optional[date]] = mapped_column(Date)
    start_time: Mapped[Optional[time]] = mapped_column(Time)
    end_time: Mapped[Optional[time]] = mapped_column(Time)
    timezone: Mapped[Optional[str]] = mapped_column(String(100), default="UTC")
    source: Mapped[Optional[str]] = mapped_column(String(50))
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    __table_args__ = (UniqueConstraint("provider", "external_event_id", name="uq_cal_provider_evt"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    interview_id: Mapped[Optional[str]] = mapped_column(ForeignKey("interviews.id"))
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="GOOGLE_CALENDAR")
    external_event_id: Mapped[str] = mapped_column(String(255), nullable=False)
    calendar_id: Mapped[Optional[str]] = mapped_column(String(255))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    timezone: Mapped[Optional[str]] = mapped_column(String(100), default="UTC")
    meeting_url: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(30), default="CONFIRMED")
    raw_response: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================
# 22-25. INTERVIEW SESSIONS, QUESTIONS & MEETINGS
# ============================================================

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    __table_args__ = (
        Index("idx_int_sessions_interview", "interview_id"),
        Index("idx_int_sessions_status", "status")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    interview_id: Mapped[Optional[str]] = mapped_column(ForeignKey("interviews.id"))
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    session_number: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    current_stage: Mapped[Optional[str]] = mapped_column(String(100), default="INTERVIEW_START")
    current_question_id: Mapped[Optional[str]] = mapped_column(String(255))
    ai_mode: Mapped[Optional[str]] = mapped_column(String(50), default="AI_ACTIVE")
    workflow_id: Mapped[Optional[str]] = mapped_column(ForeignKey("hiring_workflows.id"))
    workflow_version: Mapped[int] = mapped_column(Integer, default=1)
    organization_id: Mapped[str] = mapped_column(String, default="org-default")
    elevenlabs_agent_id: Mapped[Optional[str]] = mapped_column(String)
    elevenlabs_conversation_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    brain_status: Mapped[Optional[str]] = mapped_column(String(50), default="IDLE")
    current_question_number: Mapped[int] = mapped_column(Integer, default=0)
    current_question_index: Mapped[int] = mapped_column(Integer, default=0)
    difficulty: Mapped[Optional[str]] = mapped_column(String(30), default="MEDIUM")
    screen_consent_given: Mapped[bool] = mapped_column(Boolean, default=False)
    user_code: Mapped[Optional[str]] = mapped_column(Text)
    code_test_results: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    transcript: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    overall_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    evaluation_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    hr_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    hr_approved_by: Mapped[Optional[str]] = mapped_column(String)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    __table_args__ = (Index("idx_int_questions_session", "session_id"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    interview_id: Mapped[Optional[str]] = mapped_column(String)
    session_id: Mapped[str] = mapped_column(ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), default="TECHNICAL")
    stage: Mapped[Optional[str]] = mapped_column(String(100), default="TECHNICAL_INTERVIEW")
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[Optional[str]] = mapped_column(String(50), default="PRACTICAL")
    difficulty: Mapped[Optional[str]] = mapped_column(String(30), default="MEDIUM")
    sequence_number: Mapped[int] = mapped_column(Integer, default=1)
    question_number: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    question_order: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    parent_question_id: Mapped[Optional[str]] = mapped_column(ForeignKey("interview_questions.id"))
    generated_by: Mapped[Optional[str]] = mapped_column(String(50), default="AI_BRAIN")
    skill: Mapped[Optional[str]] = mapped_column(String(150))
    answered: Mapped[bool] = mapped_column(Boolean, default=False)
    candidate_answer: Mapped[Optional[str]] = mapped_column(Text)
    ai_followup: Mapped[Optional[str]] = mapped_column(Text)
    score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    asked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class InterviewAnswer(Base):
    __tablename__ = "interview_answers"
    __table_args__ = (Index("idx_int_answers_session", "session_id"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    interview_id: Mapped[Optional[str]] = mapped_column(String)
    question_id: Mapped[str] = mapped_column(ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str] = mapped_column(ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    answer_text: Mapped[Optional[str]] = mapped_column(Text)
    transcript_segment: Mapped[Optional[str]] = mapped_column(Text)
    answer_source: Mapped[Optional[str]] = mapped_column(String(50), default="CANDIDATE_SPEECH")
    answer_quality: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=0.8)
    technical_depth: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=0.8)
    relevance: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=0.8)
    completeness: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=0.8)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=0.8)
    missing_concepts: Mapped[Optional[List[str]]] = mapped_column(JSONB, default=list)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class InterviewFollowup(Base):
    __tablename__ = "interview_followups"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    session_id: Mapped[str] = mapped_column(ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    parent_question_id: Mapped[str] = mapped_column(ForeignKey("interview_questions.id"), nullable=False)
    followup_question_id: Mapped[str] = mapped_column(ForeignKey("interview_questions.id"), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class InterviewEvent(Base):
    __tablename__ = "interview_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    interview_id: Mapped[str] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column(ForeignKey("interview_sessions.id"))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_type: Mapped[Optional[str]] = mapped_column(String(30))
    actor_id: Mapped[Optional[str]] = mapped_column(String)
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class MeetingSession(Base):
    __tablename__ = "meeting_sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    interview_id: Mapped[str] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="GOOGLE_MEET")
    external_meeting_id: Mapped[Optional[str]] = mapped_column(String(255))
    meeting_url: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(50), default="CREATED")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class MeetingParticipant(Base):
    __tablename__ = "meeting_participants"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    meeting_session_id: Mapped[str] = mapped_column(ForeignKey("meeting_sessions.id", ondelete="CASCADE"), nullable=False)
    external_participant_id: Mapped[Optional[str]] = mapped_column(String(255))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    participant_type: Mapped[Optional[str]] = mapped_column(String(50), default="CANDIDATE")
    joined_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class MeetingEvent(Base):
    __tablename__ = "meeting_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    meeting_session_id: Mapped[str] = mapped_column(ForeignKey("meeting_sessions.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 26. CODING INTERVIEW
# ============================================================

class CodingProblem(Base):
    __tablename__ = "coding_problems"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[Optional[str]] = mapped_column(ForeignKey("organizations.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Optional[str]] = mapped_column(String(30), default="MEDIUM")
    problem_type: Mapped[Optional[str]] = mapped_column(String(50), default="ALGORITHM")
    skills: Mapped[Optional[List[str]]] = mapped_column(JSONB, default=list)
    language_options: Mapped[Optional[List[str]]] = mapped_column(JSONB, default=list)
    experience_level: Mapped[Optional[str]] = mapped_column(String(50))
    constraints: Mapped[Optional[str]] = mapped_column(Text)
    input_format: Mapped[Optional[str]] = mapped_column(Text)
    output_format: Mapped[Optional[str]] = mapped_column(Text)
    examples: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB)
    expected_complexity: Mapped[Optional[Dict[str, str]]] = mapped_column(JSONB)
    reference_solution: Mapped[Optional[str]] = mapped_column(Text)
    private_evaluation_notes: Mapped[Optional[str]] = mapped_column(Text)
    internal_scoring_rules: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class CodingSession(Base):
    __tablename__ = "coding_sessions"
    __table_args__ = (
        Index("idx_coding_sessions_interview", "interview_id"),
        Index("idx_coding_sessions_cand", "candidate_id"),
        Index("idx_coding_sessions_status", "status")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    interview_id: Mapped[str] = mapped_column(ForeignKey("interviews.id"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    problem_id: Mapped[str] = mapped_column(ForeignKey("coding_problems.id"), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(String(50), default="NOT_STARTED")
    language: Mapped[Optional[str]] = mapped_column(String(50), default="python")
    external_platform: Mapped[Optional[str]] = mapped_column(String(100), default="OnlineCompiler")
    external_url: Mapped[Optional[str]] = mapped_column(Text)
    coding_platform: Mapped[Optional[str]] = mapped_column(String(100))
    coding_url: Mapped[Optional[str]] = mapped_column(Text)
    screen_share_session_id: Mapped[Optional[str]] = mapped_column(String)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completion_detected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    coding_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    completion_source: Mapped[Optional[str]] = mapped_column(String(50))
    hints_allowed: Mapped[Optional[int]] = mapped_column(Integer, default=3)
    hints_given: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class CodingEvent(Base):
    __tablename__ = "coding_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    coding_session_id: Mapped[str] = mapped_column(ForeignKey("coding_sessions.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class CodingObservation(Base):
    __tablename__ = "coding_observations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    coding_session_id: Mapped[str] = mapped_column(ForeignKey("coding_sessions.id", ondelete="CASCADE"), nullable=False)
    observation_type: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    visible_code: Mapped[Optional[str]] = mapped_column(Text)
    visible_output: Mapped[Optional[str]] = mapped_column(Text)
    visible_error: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    observed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 27-30. EVALUATIONS & HR DECISIONS
# ============================================================

class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"
    __table_args__ = (
        Index("idx_evals_interview", "interview_id"),
        Index("idx_evals_cand", "candidate_id"),
        Index("idx_evals_job", "job_id")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    interview_id: Mapped[str] = mapped_column(ForeignKey("interviews.id"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    evaluation_version: Mapped[int] = mapped_column(Integer, default=1)
    overall_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    overall_summary: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=0.85)
    status: Mapped[Optional[str]] = mapped_column(String(30), default="COMPLETED")
    strengths: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    gaps: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    red_flags: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB)
    limitations: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    technical_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=0.0)
    human_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[Optional[str]] = mapped_column(String)
    workflow_id: Mapped[Optional[str]] = mapped_column(ForeignKey("hiring_workflows.id"))
    workflow_version: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reviewed_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class EvaluationCompetency(Base):
    __tablename__ = "evaluation_competencies"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("interview_evaluations.id", ondelete="CASCADE"), nullable=False)
    competency_name: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=3.0)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=0.85)
    status: Mapped[Optional[str]] = mapped_column(String(50), default="DEMONSTRATED")
    summary: Mapped[Optional[str]] = mapped_column(Text)
    evidence: Mapped[Optional[str]] = mapped_column(Text)
    limitations: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class EvaluationQuestionResult(Base):
    __tablename__ = "evaluation_question_results"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("interview_evaluations.id", ondelete="CASCADE"), nullable=False)
    question_id: Mapped[str] = mapped_column(ForeignKey("interview_questions.id"), nullable=False)
    competency: Mapped[Optional[str]] = mapped_column(String(100))
    understanding: Mapped[Optional[str]] = mapped_column(Text)
    correctness: Mapped[Optional[str]] = mapped_column(Text)
    depth: Mapped[Optional[str]] = mapped_column(Text)
    evidence: Mapped[Optional[str]] = mapped_column(Text)
    score: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=3.0)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=0.85)
    assessment: Mapped[Optional[str]] = mapped_column(Text)
    observation_status: Mapped[Optional[str]] = mapped_column(String(50), default="OBSERVED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class EvaluationEvidence(Base):
    __tablename__ = "evaluation_evidence"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("interview_evaluations.id", ondelete="CASCADE"), nullable=False)
    competency_id: Mapped[Optional[str]] = mapped_column(ForeignKey("evaluation_competencies.id"))
    question_result_id: Mapped[Optional[str]] = mapped_column(ForeignKey("evaluation_question_results.id"))
    evidence_type: Mapped[Optional[str]] = mapped_column(String(50))
    evidence_text: Mapped[Optional[str]] = mapped_column(Text)
    source_reference: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class EvaluationProjectVerification(Base):
    __tablename__ = "evaluation_project_verification"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("interview_evaluations.id", ondelete="CASCADE"), nullable=False)
    project_name: Mapped[Optional[str]] = mapped_column(String(255))
    claim: Mapped[Optional[str]] = mapped_column(Text)
    evidence: Mapped[Optional[str]] = mapped_column(Text)
    resume_claim: Mapped[Optional[str]] = mapped_column(Text)
    interview_evidence: Mapped[Optional[str]] = mapped_column(Text)
    verification_status: Mapped[Optional[str]] = mapped_column(String(50), default="NOT_VERIFIED")
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class EvaluationJDAlignment(Base):
    __tablename__ = "evaluation_jd_alignment"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("interview_evaluations.id", ondelete="CASCADE"), nullable=False)
    requirement: Mapped[Optional[str]] = mapped_column(Text)
    requirement_name: Mapped[Optional[str]] = mapped_column(String(255))
    candidate_evidence: Mapped[Optional[str]] = mapped_column(Text)
    evidence: Mapped[Optional[str]] = mapped_column(Text)
    alignment_status: Mapped[Optional[str]] = mapped_column(String(50), default="NOT_TESTED")
    status: Mapped[Optional[str]] = mapped_column(String(50), default="NOT_TESTED")
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class CandidateDecision(Base):
    __tablename__ = "candidate_decisions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id"), nullable=False)
    evaluation_id: Mapped[Optional[str]] = mapped_column(ForeignKey("interview_evaluations.id"))
    decision: Mapped[str] = mapped_column(String(50), nullable=False) # ADVANCE | HOLD | REJECT | REQUEST_INTERVIEW
    reason: Mapped[Optional[str]] = mapped_column(Text)
    decision_reason: Mapped[Optional[str]] = mapped_column(Text)
    decided_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    decided_by_user_id: Mapped[Optional[str]] = mapped_column(String(255))
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class EvaluationDecision(Base):
    __tablename__ = "evaluation_decisions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("interview_evaluations.id", ondelete="CASCADE"), nullable=False)
    interview_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    decided_by_user_id: Mapped[str] = mapped_column(String(255), default="hr_admin")
    decision_reason: Mapped[str] = mapped_column(Text, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class EvaluationEvent(Base):
    __tablename__ = "evaluation_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    evaluation_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class HiringDecision(Base):
    __tablename__ = "hiring_decisions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id"), nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    decided_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    decision_reason: Mapped[str] = mapped_column(Text, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 31. OFFERS
# ============================================================

class Offer(Base):
    __tablename__ = "offers"
    __table_args__ = (
        Index("idx_offers_cand", "candidate_id"),
        Index("idx_offers_app", "application_id"),
        Index("idx_offers_status", "status")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id"), nullable=False)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT")
    position_title: Mapped[Optional[str]] = mapped_column(String(255))
    salary: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD")
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    approval_status: Mapped[Optional[str]] = mapped_column(String(50), default="PENDING")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    approved_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    declined_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class OfferVersion(Base):
    __tablename__ = "offer_versions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    offer_id: Mapped[str] = mapped_column(ForeignKey("offers.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    salary: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    terms: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class OfferDocument(Base):
    __tablename__ = "offer_documents"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    offer_id: Mapped[str] = mapped_column(ForeignKey("offers.id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class OfferEvent(Base):
    __tablename__ = "offer_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    offer_id: Mapped[str] = mapped_column(ForeignKey("offers.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_type: Mapped[Optional[str]] = mapped_column(String(30))
    actor_id: Mapped[Optional[str]] = mapped_column(String)
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 32. BACKGROUND VERIFICATION
# ============================================================

class VerificationCase(Base):
    __tablename__ = "verification_cases"
    __table_args__ = (
        Index("idx_verif_cand", "candidate_id"),
        Index("idx_verif_app", "application_id")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="INITIATED")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class VerificationCheck(Base):
    __tablename__ = "verification_checks"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    verification_case_id: Mapped[str] = mapped_column(ForeignKey("verification_cases.id", ondelete="CASCADE"), nullable=False)
    check_type: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[Optional[str]] = mapped_column(String(50), default="PENDING")
    provider: Mapped[Optional[str]] = mapped_column(String(100))
    result: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class VerificationDocument(Base):
    __tablename__ = "verification_documents"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    verification_case_id: Mapped[str] = mapped_column(ForeignKey("verification_cases.id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    document_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class VerificationEvent(Base):
    __tablename__ = "verification_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    verification_case_id: Mapped[str] = mapped_column(ForeignKey("verification_cases.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 33. ONBOARDING
# ============================================================

class OnboardingCase(Base):
    __tablename__ = "onboarding_cases"
    __table_args__ = (
        Index("idx_onboard_cand", "candidate_id"),
        Index("idx_onboard_app", "application_id")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id"), nullable=False)
    offer_id: Mapped[Optional[str]] = mapped_column(ForeignKey("offers.id"))
    status: Mapped[Optional[str]] = mapped_column(String(50), default="PREPARING")
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    onboarding_case_id: Mapped[Optional[str]] = mapped_column(ForeignKey("onboarding_cases.id", ondelete="CASCADE"))
    candidate_id: Mapped[Optional[str]] = mapped_column(ForeignKey("candidates.id"))
    task_name: Mapped[Optional[str]] = mapped_column(String(255))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    assigned_to: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    status: Mapped[Optional[str]] = mapped_column(String(50), default="PENDING")
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class OnboardingDocument(Base):
    __tablename__ = "onboarding_documents"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    onboarding_case_id: Mapped[str] = mapped_column(ForeignKey("onboarding_cases.id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    document_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class OnboardingEvent(Base):
    __tablename__ = "onboarding_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    onboarding_case_id: Mapped[str] = mapped_column(ForeignKey("onboarding_cases.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 34-36. AUTOMATION, AI AGENT RUNS & NOTIFICATIONS
# ============================================================

class AutomationIntegration(Base):
    __tablename__ = "automation_integrations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(50), default="N8N")
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    base_url: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(30), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AutomationRun(Base):
    __tablename__ = "automation_runs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(50), default="N8N")
    workflow_external_id: Mapped[Optional[str]] = mapped_column(String(255))
    execution_external_id: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[Optional[str]] = mapped_column(String(30), default="COMPLETED")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class AutomationEvent(Base):
    __tablename__ = "automation_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    event_type: Mapped[Optional[str]] = mapped_column(String(100))
    source: Mapped[Optional[str]] = mapped_column(String(50))
    external_event_id: Mapped[Optional[str]] = mapped_column(String(255))
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class AIRun(Base):
    __tablename__ = "ai_runs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    candidate_id: Mapped[Optional[str]] = mapped_column(ForeignKey("candidates.id"))
    application_id: Mapped[Optional[str]] = mapped_column(ForeignKey("applications.id"))
    interview_id: Mapped[Optional[str]] = mapped_column(ForeignKey("interviews.id"))
    agent_type: Mapped[Optional[str]] = mapped_column(String(100))
    workflow_step_id: Mapped[Optional[str]] = mapped_column(ForeignKey("workflow_steps.id"))
    model_name: Mapped[Optional[str]] = mapped_column(String(100), default="Gemini-Pro")
    status: Mapped[Optional[str]] = mapped_column(String(30), default="COMPLETED")
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class AIToolCall(Base):
    __tablename__ = "ai_tool_calls"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    ai_run_id: Mapped[str] = mapped_column(ForeignKey("ai_runs.id", ondelete="CASCADE"), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    arguments: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    status: Mapped[Optional[str]] = mapped_column(String(30), default="SUCCESS")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    candidate_id: Mapped[Optional[str]] = mapped_column(ForeignKey("candidates.id"))
    type: Mapped[Optional[str]] = mapped_column(String(50))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    message: Mapped[Optional[str]] = mapped_column(Text)
    channel: Mapped[Optional[str]] = mapped_column(String(30), default="EMAIL")
    status: Mapped[Optional[str]] = mapped_column(String(30), default="SENT")
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(150))
    channel: Mapped[Optional[str]] = mapped_column(String(30), default="EMAIL")
    subject: Mapped[Optional[str]] = mapped_column(Text)
    body: Mapped[Optional[str]] = mapped_column(Text)
    variables: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    status: Mapped[Optional[str]] = mapped_column(String(30), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    notification_id: Mapped[str] = mapped_column(ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(50), default="GMAIL")
    external_id: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[Optional[str]] = mapped_column(String(30), default="DELIVERED")
    attempt_count: Mapped[int] = mapped_column(Integer, default=1)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# 37-41. AUDIT, WORKFLOW EVENTS, IDEMPOTENCY, RAG & SECURITY
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_org", "organization_id"),
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_created", "created_at")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    actor_type: Mapped[Optional[str]] = mapped_column(String(30), default="USER")
    actor_id: Mapped[Optional[str]] = mapped_column(String)
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity: Mapped[Optional[str]] = mapped_column(String(100))
    entity_type: Mapped[Optional[str]] = mapped_column(String(100))
    entity_id: Mapped[Optional[str]] = mapped_column(String)
    old_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    new_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class WorkflowEvent(Base):
    __tablename__ = "workflow_events"
    __table_args__ = (
        Index("idx_wf_events_cand", "candidate_id"),
        Index("idx_wf_events_app", "application_id"),
        Index("idx_wf_events_wf", "candidate_workflow_id"),
        Index("idx_wf_events_created", "created_at")
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[Optional[str]] = mapped_column(ForeignKey("organizations.id"))
    candidate_workflow_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    candidate_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    application_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    job_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    workflow_step_id: Mapped[Optional[str]] = mapped_column(String)
    step_id: Mapped[Optional[str]] = mapped_column(String)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_type: Mapped[Optional[str]] = mapped_column(String(30), default="SYSTEM")
    actor_id: Mapped[Optional[str]] = mapped_column(String)
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    payload_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    __table_args__ = (UniqueConstraint("organization_id", "idempotency_key", name="uq_idempotency_org_key"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    operation: Mapped[str] = mapped_column(String(100), nullable=False)
    request_hash: Mapped[Optional[str]] = mapped_column(String(255))
    response_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    status: Mapped[Optional[str]] = mapped_column(String(30), default="PROCESSED")
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class KnowledgeCollection(Base):
    __tablename__ = "knowledge_collections"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    collection_id: Mapped[Optional[str]] = mapped_column(ForeignKey("knowledge_collections.id", ondelete="CASCADE"))
    document_id: Mapped[Optional[str]] = mapped_column(ForeignKey("documents.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[Optional[str]] = mapped_column(String(50))
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(30), default="INDEXED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    knowledge_document_id: Mapped[str] = mapped_column(ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[Optional[str]] = mapped_column(Text)
    token_count: Mapped[Optional[int]] = mapped_column(Integer)
    qdrant_collection: Mapped[Optional[str]] = mapped_column(String(255))
    qdrant_point_id: Mapped[Optional[str]] = mapped_column(String(255))
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class SecurityEvent(Base):
    __tablename__ = "security_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[Optional[str]] = mapped_column(ForeignKey("organizations.id"))
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class Integration(Base):
    __tablename__ = "integrations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(String, nullable=False)
    platform_name: Mapped[str] = mapped_column(String, nullable=False)
    is_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    credentials_masked: Mapped[Optional[str]] = mapped_column(String)
    google_account_email: Mapped[Optional[str]] = mapped_column(String)
    google_subject_id: Mapped[Optional[str]] = mapped_column(String)
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    scopes: Mapped[Optional[List[str]]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String, default="DISCONNECTED")
    config_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    last_tested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

class InterviewTechnicalEvidence(Base):
    __tablename__ = "interview_technical_evidence"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid_str)
    interview_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    competency: Mapped[str] = mapped_column(String, nullable=False)
    evidence_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

# Backwards compatibility alias
Evaluation = InterviewEvaluation
