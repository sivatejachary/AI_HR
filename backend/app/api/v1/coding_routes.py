import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.domain import InterviewSession, CodingProblem, CodingSession, InterviewEvent, InterviewTechnicalEvidence
from app.services.interview_brain.orchestrator import AIInterviewOrchestrator
from app.services.interview_brain.coding_problem_service import CodingProblemService
from app.services.interview_brain.coding_vision_service import CodingVisionService
from app.services.interview_brain.experience_engine import ExperienceEngine
from integrations.coding.online_compiler import OnlineCodingProvider

logger = logging.getLogger("coding_routes")
router = APIRouter(prefix="/api/interviews/{interview_id}", tags=["Coding Interview"])

vision_service = CodingVisionService()

def _log_event(db: Session, interview_id: str, event_type: str, metadata: dict = None) -> InterviewEvent:
    unique_id = f"evt-{int(datetime.utcnow().timestamp()*1000)}-{uuid.uuid4().hex[:6]}"
    evt = InterviewEvent(
        id=unique_id,
        interview_id=interview_id,
        event_type=event_type,
        metadata_json=metadata or {},
        timestamp=datetime.utcnow()
    )
    db.add(evt)
    db.commit()
    return evt

@router.post("/coding/start")
def start_coding_session(
    interview_id: str,
    language: str = "python",
    db: Session = Depends(get_db)
):
    """
    POST /api/interviews/{interview_id}/coding/start
    Initializes coding section, selects problem, creates online coding session, and returns URLs.
    Does NOT execute candidate code on server.
    """
    # Build context to determine candidate experience band
    ctx = AIInterviewOrchestrator.get_context(db, interview_id)
    cand_info = ctx.get("candidate", {})
    job_info = ctx.get("job", {})
    
    exp_meta = ExperienceEngine.determine_experience_band(
        years_experience=cand_info.get("experience_years", 0),
        role_title=job_info.get("title", ""),
        job_requirements=job_info.get("requirements", ""),
        resume_text=cand_info.get("resume_summary", "")
    )
    exp_band = exp_meta["band"]

    prob_service = CodingProblemService(db)
    problem = prob_service.select_problem(language=language, difficulty="MEDIUM", experience_band=exp_band)

    provider = OnlineCodingProvider()
    sess_meta = provider.create_candidate_session(
        problem_id=problem.id,
        candidate_id=interview_id,
        language=language
    )

    coding_session_id = f"CS-{int(datetime.utcnow().timestamp()*1000)}"
    coding_sess = CodingSession(
        id=coding_session_id,
        interview_id=interview_id,
        problem_id=problem.id,
        coding_platform=provider.platform_name,
        coding_url=sess_meta["coding_url"],
        language=language.lower(),
        status="WAITING_FOR_SCREEN_SHARE",
        started_at=datetime.utcnow(),
        hints_allowed=3,
        hints_given=0,
        metadata_json={"session_token": sess_meta["session_token"]}
    )
    db.add(coding_sess)

    # Update interview session stage to CODING_INTRO
    sess = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if sess:
        sess.current_stage = "CODING_INTRO"

    db.commit()

    _log_event(db, interview_id, "coding.started", {"coding_session_id": coding_session_id, "problem_id": problem.id})
    _log_event(db, interview_id, "coding.problem.presented", {"title": problem.title, "difficulty": problem.difficulty})

    public_problem = prob_service.get_public_problem_payload(problem)

    return {
        "coding_session_id": coding_session_id,
        "problem": public_problem,
        "coding_platform": provider.platform_name,
        "coding_url": sess_meta["coding_url"],
        "status": coding_sess.status
    }

@router.get("/coding")
def get_coding_session(interview_id: str, db: Session = Depends(get_db)):
    """
    GET /api/interviews/{interview_id}/coding
    Returns active coding session status and platform details.
    """
    coding_sess = db.query(CodingSession).filter(CodingSession.interview_id == interview_id).order_by(CodingSession.started_at.desc()).first()
    if not coding_sess:
        raise HTTPException(status_code=404, detail="No active coding session found for this interview")

    prob = db.query(CodingProblem).filter(CodingProblem.id == coding_sess.problem_id).first()
    prob_payload = CodingProblemService(db).get_public_problem_payload(prob) if prob else None

    return {
        "coding_session_id": coding_sess.id,
        "interview_id": coding_sess.interview_id,
        "problem": prob_payload,
        "coding_platform": coding_sess.coding_platform,
        "coding_url": coding_sess.coding_url,
        "language": coding_sess.language,
        "status": coding_sess.status,
        "time_spent_seconds": coding_sess.time_spent_seconds,
        "hints_allowed": coding_sess.hints_allowed,
        "hints_given": coding_sess.hints_given
    }

@router.get("/coding/problem")
def get_coding_problem(interview_id: str, db: Session = Depends(get_db)):
    """
    GET /api/interviews/{interview_id}/coding/problem
    Returns public problem parameters for candidate display (strictly excluding reference solutions/internal notes).
    """
    coding_sess = db.query(CodingSession).filter(CodingSession.interview_id == interview_id).order_by(CodingSession.started_at.desc()).first()
    if not coding_sess:
        raise HTTPException(status_code=404, detail="No active coding problem found for this interview")

    prob = db.query(CodingProblem).filter(CodingProblem.id == coding_sess.problem_id).first()
    if not prob:
        raise HTTPException(status_code=404, detail="Coding problem detail not found")

    return CodingProblemService(db).get_public_problem_payload(prob)

@router.post("/coding/screen-share")
def update_screen_share_state(
    interview_id: str,
    action: str = Body(..., embed=True), # start | stop | request
    db: Session = Depends(get_db)
):
    """
    POST /api/interviews/{interview_id}/coding/screen-share
    Tracks candidate explicit screen share authorization state.
    """
    coding_sess = db.query(CodingSession).filter(CodingSession.interview_id == interview_id).order_by(CodingSession.started_at.desc()).first()
    if not coding_sess:
        raise HTTPException(status_code=404, detail="No active coding session found")

    act = action.lower()
    if act == "request":
        coding_sess.status = "WAITING_FOR_SCREEN_SHARE"
        _log_event(db, interview_id, "screen_share.requested", {"timestamp": datetime.utcnow().isoformat()})
    elif act == "start":
        coding_sess.status = "SCREEN_SHARE_ACTIVE"
        sess = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if sess:
            sess.current_stage = "CODING"
            sess.screen_consent_given = True
        _log_event(db, interview_id, "screen_share.started", {"timestamp": datetime.utcnow().isoformat()})
    elif act == "stop":
        coding_sess.status = "SCREEN_SHARE_STOPPED"
        sess = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if sess:
            sess.screen_consent_given = False
        _log_event(db, interview_id, "screen_share.stopped", {"timestamp": datetime.utcnow().isoformat()})
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use start, stop, or request.")

    db.commit()
    return {"status": "success", "session_status": coding_sess.status, "action": act}

@router.post("/coding/observations")
def add_vision_observation(
    interview_id: str,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    POST /api/interviews/{interview_id}/coding/observations
    Processes Vision AI frame analysis from authorized candidate screen share stream.
    """
    coding_sess = db.query(CodingSession).filter(CodingSession.interview_id == interview_id).order_by(CodingSession.started_at.desc()).first()
    if not coding_sess:
        raise HTTPException(status_code=404, detail="No active coding session found")

    observation = vision_service.process_screen_observation(
        screen_type=payload.get("screen_type", "ONLINE_COMPILER"),
        language=payload.get("language", coding_sess.language),
        code_visible=payload.get("code_visible", True),
        error_visible=payload.get("error_visible", False),
        output_visible=payload.get("output_visible", True),
        visible_error_text=payload.get("visible_error_text"),
        visible_output_text=payload.get("visible_output_text"),
        confidence=payload.get("confidence", 0.94)
    )

    # State machine transition if visible error detected
    if observation["error_visible"]:
        coding_sess.status = "DEBUGGING"
        sess = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if sess and sess.current_stage != "DEBUGGING":
            sess.current_stage = "DEBUGGING"
            _log_event(db, interview_id, "coding.debugging.started", {"error": observation.get("visible_error_text")})

    _log_event(db, interview_id, "vision.observation.created", observation)
    return {"status": "success", "observation": observation}

@router.get("/coding/observations")
def list_vision_observations(interview_id: str, db: Session = Depends(get_db)):
    """
    GET /api/interviews/{interview_id}/coding/observations
    Returns recent vision observations for HR Live Monitor.
    """
    events = db.query(InterviewEvent).filter(
        InterviewEvent.interview_id == interview_id,
        InterviewEvent.event_type == "vision.observation.created"
    ).order_by(InterviewEvent.timestamp.desc()).limit(10).all()

    return {"observations": [e.metadata_json for e in events]}

@router.post("/coding/hint")
def request_coding_hint(interview_id: str, db: Session = Depends(get_db)):
    """
    POST /api/interviews/{interview_id}/coding/hint
    Provides helpful guiding hint to candidate without revealing exact code solution.
    """
    coding_sess = db.query(CodingSession).filter(CodingSession.interview_id == interview_id).order_by(CodingSession.started_at.desc()).first()
    if not coding_sess:
        raise HTTPException(status_code=404, detail="No active coding session found")

    if coding_sess.hints_given >= coding_sess.hints_allowed:
        return {
            "status": "limit_reached",
            "hints_given": coding_sess.hints_given,
            "hints_allowed": coding_sess.hints_allowed,
            "hint": "You have reached the maximum number of allowed hints. Try breaking down the problem using small example inputs!"
        }

    coding_sess.hints_given += 1
    db.commit()

    hints = [
        "Consider using a Hash Map (Dictionary) to store previously seen elements for O(1) lookups.",
        "Check your loop boundary conditions to prevent list index errors.",
        "Think about what happens if the input array contains negative numbers or duplicate elements."
    ]
    selected_hint = hints[(coding_sess.hints_given - 1) % len(hints)]

    _log_event(db, interview_id, "coding.hint.provided", {"hint_number": coding_sess.hints_given, "hint": selected_hint})
    return {
        "status": "success",
        "hints_given": coding_sess.hints_given,
        "hints_allowed": coding_sess.hints_allowed,
        "hint": selected_hint
    }

@router.post("/coding/finish")
def finish_coding_session(interview_id: str, db: Session = Depends(get_db)):
    """
    POST /api/interviews/{interview_id}/coding/finish
    Finalizes coding challenge, transitions state machine to CODE_REVIEW / OPTIMIZATION.
    """
    coding_sess = db.query(CodingSession).filter(CodingSession.interview_id == interview_id).order_by(CodingSession.started_at.desc()).first()
    if not coding_sess:
        raise HTTPException(status_code=404, detail="No active coding session found")

    coding_sess.status = "COMPLETED"
    coding_sess.completed_at = datetime.utcnow()
    if coding_sess.started_at:
        coding_sess.time_spent_seconds = int((coding_sess.completed_at - coding_sess.started_at).total_seconds())

    sess = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if sess:
        sess.current_stage = "CODE_REVIEW"

    # Record technical evidence
    evidence = InterviewTechnicalEvidence(
        id=f"EVD-{int(datetime.utcnow().timestamp()*1000)}",
        interview_id=interview_id,
        competency="Problem Solving & Practical Coding",
        evidence_json={
            "platform": coding_sess.coding_platform,
            "coding_url": coding_sess.coding_url,
            "time_spent_seconds": coding_sess.time_spent_seconds,
            "hints_given": coding_sess.hints_given,
            "observation": "Candidate completed implementation on external online compiler."
        }
    )
    db.add(evidence)
    db.commit()

    _log_event(db, interview_id, "coding.code_review.started", {"time_spent": coding_sess.time_spent_seconds})
    _log_event(db, interview_id, "coding.completed", {"session_id": coding_sess.id})

    return {
        "status": "success",
        "coding_session_id": coding_sess.id,
        "current_stage": "CODE_REVIEW",
        "time_spent_seconds": coding_sess.time_spent_seconds
    }

@router.post("/questions/skip")
def skip_current_question(interview_id: str, db: Session = Depends(get_db)):
    """
    POST /api/interviews/{interview_id}/questions/skip
    HR override control to skip current question or coding problem.
    """
    sess = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Interview session not found")

    prev_stage = sess.current_stage
    AIInterviewOrchestrator.move_stage(db, interview_id)
    new_stage = sess.current_stage

    _log_event(db, interview_id, "hr.question.skipped", {"from_stage": prev_stage, "to_stage": new_stage})

    return {
        "status": "success",
        "message": f"Skipped question in stage {prev_stage}.",
        "current_stage": new_stage
    }
