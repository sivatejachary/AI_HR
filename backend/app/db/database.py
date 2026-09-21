import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.models.domain import Base

from app.core.config import settings

logger = logging.getLogger("database")

SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL

if "postgresql" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes database tables and auto-migrates missing SQLite columns."""
    Base.metadata.create_all(bind=engine)
    
    # Auto-add missing columns for SQLite if DB existed prior to schema updates
    if "sqlite" in SQLALCHEMY_DATABASE_URL:
        with engine.connect() as conn:
            # Auto-migrate applications table
            app_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(applications)")).fetchall()]
            missing_app_cols = {
                "current_workflow_id": "TEXT",
                "current_workflow_version": "INTEGER DEFAULT 1",
                "current_step_id": "TEXT",
                "current_step_name": "TEXT DEFAULT 'Application'",
                "step_status": "TEXT DEFAULT 'COMPLETED'",
                "execution_id": "TEXT",
                "idempotency_key": "TEXT"
            }
            for col_name, col_type in missing_app_cols.items():
                if col_name not in app_cols:
                    try:
                        conn.execute(text(f"ALTER TABLE applications ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                        logger.info(f"Added column {col_name} to applications table")
                    except Exception as e:
                        logger.warning(f"Could not add column {col_name}: {e}")

            # Auto-migrate hiring_workflows table
            wf_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(hiring_workflows)")).fetchall()]
            missing_wf_cols = {
                "job_id": "TEXT",
                "job_title": "TEXT",
                "department": "TEXT",
                "status": "TEXT DEFAULT 'Published'",
                "is_paused": "BOOLEAN DEFAULT 0",
                "owner_name": "TEXT DEFAULT 'HR Recruiter'",
                "updated_at": "DATETIME"
            }
            for col_name, col_type in missing_wf_cols.items():
                if col_name not in wf_cols:
                    try:
                        conn.execute(text(f"ALTER TABLE hiring_workflows ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                        logger.info(f"Added column {col_name} to hiring_workflows table")
                    except Exception as e:
                        logger.warning(f"Could not add column {col_name}: {e}")

            # Auto-migrate interview_sessions table
            sess_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(interview_sessions)")).fetchall()] if "interview_sessions" in [r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()] else []
            if sess_cols:
                missing_sess_cols = {
                    "workflow_id": "TEXT",
                    "workflow_version": "INTEGER DEFAULT 1",
                    "organization_id": "TEXT DEFAULT 'org-default'",
                    "elevenlabs_agent_id": "TEXT",
                    "elevenlabs_conversation_id": "TEXT",
                    "brain_status": "TEXT DEFAULT 'IDLE'",
                    "current_stage": "TEXT DEFAULT 'INTERVIEW_START'",
                    "current_question_number": "INTEGER DEFAULT 0",
                    "difficulty": "TEXT DEFAULT 'MEDIUM'",
                    "started_at": "DATETIME",
                    "completed_at": "DATETIME",
                    "duration_seconds": "INTEGER DEFAULT 0",
                    "metadata_json": "JSON"
                }
                for col_name, col_type in missing_sess_cols.items():
                    if col_name not in sess_cols:
                        try:
                            conn.execute(text(f"ALTER TABLE interview_sessions ADD COLUMN {col_name} {col_type}"))
                            conn.commit()
                            logger.info(f"Added column {col_name} to interview_sessions table")
                        except Exception as e:
                            logger.warning(f"Could not add column {col_name}: {e}")

            # Auto-migrate interview_questions table
            q_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(interview_questions)")).fetchall()] if "interview_questions" in [r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()] else []
            if q_cols:
                missing_q_cols = {
                    "interview_id": "TEXT",
                    "session_id": "TEXT",
                    "stage": "TEXT DEFAULT 'TECHNICAL_INTERVIEW'",
                    "question_number": "INTEGER DEFAULT 1",
                    "question_type": "TEXT DEFAULT 'PRACTICAL'",
                    "skill": "TEXT",
                    "difficulty": "TEXT DEFAULT 'MEDIUM'",
                    "answered": "BOOLEAN DEFAULT 0",
                    "metadata_json": "JSON"
                }
                for col_name, col_type in missing_q_cols.items():
                    if col_name not in q_cols:
                        try:
                            conn.execute(text(f"ALTER TABLE interview_questions ADD COLUMN {col_name} {col_type}"))
                            conn.commit()
                            logger.info(f"Added column {col_name} to interview_questions table")
                        except Exception as e:
                            logger.warning(f"Could not add column {col_name}: {e}")

            # Auto-migrate interviews table
            int_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(interviews)")).fetchall()] if "interviews" in [r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()] else []
            if int_cols:
                missing_int_cols = {
                    "meeting_provider": "TEXT DEFAULT 'GOOGLE_MEET'",
                    "meeting_url": "TEXT",
                    "meeting_id": "TEXT",
                    "meeting_session_id": "TEXT",
                    "meeting_status": "TEXT DEFAULT 'CREATED'",
                    "meeting_started_at": "DATETIME",
                    "meeting_ended_at": "DATETIME",
                    "ai_participant_id": "TEXT",
                    "candidate_participant_id": "TEXT",
                    "interviewer_participant_id": "TEXT",
                    "ai_connection_status": "TEXT DEFAULT 'DISCONNECTED'",
                    "last_media_event_at": "DATETIME"
                }
                for col_name, col_type in missing_int_cols.items():
                    if col_name not in int_cols:
                        try:
                            conn.execute(text(f"ALTER TABLE interviews ADD COLUMN {col_name} {col_type}"))
                            conn.commit()
                            logger.info(f"Added column {col_name} to interviews table")
                        except Exception as e:
                            logger.warning(f"Could not add column {col_name}: {e}")

            # Auto-migrate workflow_steps table
            ws_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(workflow_steps)")).fetchall()] if "workflow_steps" in [r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()] else []
            if ws_cols:
                missing_ws_cols = {
                    "category": "TEXT DEFAULT 'Screening'",
                    "purpose": "TEXT",
                    "owner": "TEXT DEFAULT 'HR'",
                    "automation": "TEXT DEFAULT 'Manual'",
                    "duration_minutes": "INTEGER DEFAULT 30",
                    "passing_score": "INTEGER",
                    "is_required": "BOOLEAN DEFAULT 1",
                    "is_enabled": "BOOLEAN DEFAULT 1",
                    "conditions": "JSON",
                    "questions": "JSON",
                    "notifications": "JSON",
                    "config": "JSON"
                }
                for col_name, col_type in missing_ws_cols.items():
                    if col_name not in ws_cols:
                        try:
                            conn.execute(text(f"ALTER TABLE workflow_steps ADD COLUMN {col_name} {col_type}"))
                            conn.commit()
                            logger.info(f"Added column {col_name} to workflow_steps table")
                        except Exception as e:
                            logger.warning(f"Could not add column {col_name}: {e}")

def get_db():
    """Dependency for API endpoints to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
