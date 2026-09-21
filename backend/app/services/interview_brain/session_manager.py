import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.models.domain import (
    InterviewSession, InterviewQuestion, Candidate, Job, Interview, Evaluation, AuditLog
)

logger = logging.getLogger("session_manager")

class SessionManager:
    """
    Manages active interview session lifecycle in PostgreSQL database.
    """

    @staticmethod
    def create_session(db: Session, candidate_id: str, job_id: str, interview_id: Optional[str] = None) -> InterviewSession:
        session_id = f"sess-{int(datetime.utcnow().timestamp()*1000)}"
        
        session = InterviewSession(
            id=session_id,
            interview_id=interview_id,
            candidate_id=candidate_id,
            job_id=job_id,
            status="PENDING",
            current_question_index=0,
            screen_consent_given=False,
            transcript=[],
            created_at=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[InterviewSession]:
        return db.query(InterviewSession).filter(InterviewSession.id == session_id).first()

    @staticmethod
    def update_consent(db: Session, session_id: str, granted: bool) -> Optional[InterviewSession]:
        session = SessionManager.get_session(db, session_id)
        if session:
            session.screen_consent_given = granted
            db.commit()
            db.refresh(session)
        return session

    @staticmethod
    def save_user_code(db: Session, session_id: str, code: str, test_results: Optional[Dict[str, Any]] = None) -> Optional[InterviewSession]:
        session = SessionManager.get_session(db, session_id)
        if session:
            session.user_code = code
            if test_results:
                session.code_test_results = test_results
            db.commit()
            db.refresh(session)
        return session
