import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.domain import InterviewSession, Candidate, Job
from app.services.interview_brain.orchestrator import AIInterviewOrchestrator
from app.services.interview_brain.elevenlabs_service import ElevenLabsIntegrationService

logger = logging.getLogger("elevenlabs_routes")

router = APIRouter(prefix="/api/ai-interview", tags=["ElevenLabs AI Interview Webhooks"])


# Request Schemas
class NextQuestionRequest(BaseModel):
    reason: str = Field(default="after_answer", description="start_stage | after_answer | follow_up")

class SubmitAnswerRequest(BaseModel):
    question_id: str
    answer: str
    conversation_id: Optional[str] = None
    timestamp: Optional[str] = None

class EventLogRequest(BaseModel):
    event_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


def verify_elevenlabs_auth(
    authorization: Optional[str] = Header(None),
    auth_token: Optional[str] = Query(None)
):
    """Validates authorization for ElevenLabs Webhook Tools."""
    if not ElevenLabsIntegrationService.validate_webhook_auth(authorization, auth_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing ElevenLabs webhook authorization token"
        )


@router.get("/{interview_id}/context", dependencies=[Depends(verify_elevenlabs_auth)])
def get_interview_context(interview_id: str, db: Session = Depends(get_db)):
    """TOOL 1: get_interview_context - Returns dynamic normalized interview context for ElevenLabs."""
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    candidate = db.query(Candidate).filter(Candidate.id == session.candidate_id).first()
    job = db.query(Job).filter(Job.id == session.job_id).first()

    return {
        "interview_id": session.id,
        "candidate_name": candidate.name if candidate else "Candidate",
        "job_title": job.title if job else "Software Engineer",
        "current_stage": session.current_stage or "INTRODUCTION",
        "difficulty": session.difficulty or "MEDIUM",
        "question_number": session.current_question_number or 1,
        "workflow_version": session.workflow_version or 1
    }


@router.get("/{interview_id}/stage", dependencies=[Depends(verify_elevenlabs_auth)])
def get_current_stage(interview_id: str, db: Session = Depends(get_db)):
    """TOOL 2: get_current_stage - Returns current stage, session status, and difficulty."""
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    return {
        "stage": session.current_stage or "INTRODUCTION",
        "status": session.status or "IN_PROGRESS",
        "difficulty": session.difficulty or "MEDIUM"
    }


@router.post("/{interview_id}/next-question", dependencies=[Depends(verify_elevenlabs_auth)])
def get_next_question(
    interview_id: str,
    req: NextQuestionRequest,
    db: Session = Depends(get_db)
):
    """TOOL 3: get_next_question - Generates 1-by-1 dynamic question using Phase 1 Question Engine."""
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if session.status in ["COMPLETED", "CANCELLED"]:
        raise HTTPException(status_code=400, detail=f"Cannot generate question for session in status {session.status}")

    try:
        q_data = AIInterviewOrchestrator.get_next_question(db=db, session_id=interview_id)
        if q_data.get("status") == "error":
            raise HTTPException(status_code=400, detail=q_data.get("message"))
            
        return {
            "question_id": q_data.get("question_id") or f"Q-{session.current_question_number}",
            "question": q_data.get("question", "Could you tell me about your background?"),
            "stage": q_data.get("stage", session.current_stage or "INTRODUCTION"),
            "question_type": q_data.get("question_type", "PRACTICAL"),
            "skill": q_data.get("skill"),
            "difficulty": q_data.get("difficulty", session.difficulty or "MEDIUM")
        }
    except Exception as e:
        logger.error(f"Error in get_next_question tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interview_id}/answer", dependencies=[Depends(verify_elevenlabs_auth)])
def submit_candidate_answer(
    interview_id: str,
    req: SubmitAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    TOOL 4: submit_candidate_answer - Saves answer, evaluates technical quality/completeness,
    determines next action and updates session state.
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if session.status == "PAUSED":
        return {
            "saved": False,
            "status": "PAUSED",
            "message": "Interview is currently paused by HR."
        }

    if req.conversation_id:
        session.elevenlabs_conversation_id = req.conversation_id
        db.commit()

    try:
        result = AIInterviewOrchestrator.submit_answer(
            db=db,
            session_id=interview_id,
            question_id=req.question_id,
            answer_text=req.answer
        )
        
        analysis = result.get("analysis", {})
        next_act = result.get("next_action", {})

        return {
            "saved": True,
            "answer_quality": round(analysis.get("correctness", 0.8), 2),
            "technical_depth": round(analysis.get("technical_depth", 0.75), 2),
            "next_action": next_act.get("action", "NEXT_QUESTION"),
            "next_question": next_act.get("question"),
            "difficulty": next_act.get("difficulty", session.difficulty or "MEDIUM")
        }
    except Exception as e:
        logger.error(f"Error submitting answer in tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interview_id}/next-action", dependencies=[Depends(verify_elevenlabs_auth)])
def get_next_action(interview_id: str, db: Session = Depends(get_db)):
    """
    TOOL 5: get_next_action - Evaluates current state and returns next action:
    FOLLOW_UP | CLARIFY | NEXT_TOPIC | INCREASE_DIFFICULTY | DECREASE_DIFFICULTY | MOVE_TO_NEXT_STAGE | END_INTERVIEW
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if session.status == "COMPLETED":
        return {
            "action": "END_INTERVIEW",
            "reason": "Interview session marked as COMPLETED",
            "question": None,
            "difficulty": session.difficulty or "MEDIUM"
        }

    # Fetch latest question/answer state
    q_data = AIInterviewOrchestrator.get_next_question(db=db, session_id=interview_id)
    return {
        "action": "NEXT_TOPIC" if session.current_question_number > 1 else "FOLLOW_UP",
        "reason": "Continuing interview plan sequence",
        "question": q_data.get("question") if isinstance(q_data, dict) else None,
        "difficulty": session.difficulty or "MEDIUM"
    }


@router.post("/{interview_id}/event", dependencies=[Depends(verify_elevenlabs_auth)])
def save_interview_event(
    interview_id: str,
    req: EventLogRequest,
    db: Session = Depends(get_db)
):
    """TOOL 6: save_interview_event - Logs event to interview event audit log."""
    try:
        AIInterviewOrchestrator._log_event(
            db=db,
            session_id=interview_id,
            event_type=req.event_type,
            metadata=req.metadata
        )
        return {"status": "success", "event_type": req.event_type}
    except Exception as e:
        logger.error(f"Error logging event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interview_id}/pause", dependencies=[Depends(verify_elevenlabs_auth)])
def pause_interview(interview_id: str, db: Session = Depends(get_db)):
    """TOOL 7: pause_interview - HR or Agent pauses active interview."""
    res = AIInterviewOrchestrator.pause_interview(db=db, session_id=interview_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return {
        "status": res.get("session_status", "PAUSED"),
        "brain_status": res.get("brain_status", "PAUSED"),
        "message": "AI Interview paused successfully."
    }


@router.post("/{interview_id}/resume", dependencies=[Depends(verify_elevenlabs_auth)])
def resume_interview(interview_id: str, db: Session = Depends(get_db)):
    """TOOL 8: resume_interview - HR or Agent resumes paused interview."""
    res = AIInterviewOrchestrator.resume_interview(db=db, session_id=interview_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return {
        "status": res.get("session_status", "IN_PROGRESS"),
        "brain_status": res.get("brain_status", "THINKING"),
        "message": "AI Interview resumed successfully."
    }


@router.post("/{interview_id}/complete", dependencies=[Depends(verify_elevenlabs_auth)])
def complete_interview(interview_id: str, db: Session = Depends(get_db)):
    """TOOL 9: complete_interview - Completes interview and finalizes session."""
    res = AIInterviewOrchestrator.complete_interview(db=db, session_id=interview_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return {
        "status": res.get("session_status", "COMPLETED"),
        "brain_status": res.get("brain_status", "COMPLETED"),
        "message": "AI Interview completed successfully."
    }


@router.post("/{interview_id}/elevenlabs-post-call")
def elevenlabs_post_call_webhook(
    interview_id: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """POST-CALL TELEMETRY: Captures final transcript, audio, duration, and metrics from ElevenLabs."""
    result = ElevenLabsIntegrationService.process_post_call_telemetry(
        interview_id=interview_id,
        post_call_data=payload,
        db=db
    )
    return result


@router.get("/{interview_id}/elevenlabs-session")
def get_elevenlabs_session(interview_id: str, db: Session = Depends(get_db)):
    """CLIENT AUTH: Generates signed session token / URL for browser Web SDK integration."""
    try:
        data = ElevenLabsIntegrationService.generate_signed_url(interview_id=interview_id, db=db)
        return data
    except Exception as e:
        logger.error(f"Error generating ElevenLabs session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
