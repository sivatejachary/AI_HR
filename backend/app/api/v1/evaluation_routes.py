import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.domain import (
    InterviewSession, InterviewEvaluation, EvaluationDecision,
    EvaluationCompetency, EvaluationJDAlignment, Application
)
from app.services.evaluation.evaluation_service import EvaluationService, EvidenceCollector
from app.services.workflow_engine import HiringWorkflowEngine

logger = logging.getLogger("evaluation_routes")

# Routers with dual prefixes to support required API routes
ai_router = APIRouter(prefix="/api/interviews/ai/{interview_id}", tags=["AI Evaluation"])
hr_router = APIRouter(prefix="/api/interviews/{interview_id}", tags=["HR Decision & Review"])

@ai_router.post("/evaluate")
def trigger_evaluation(
    interview_id: str,
    payload: Dict[str, Any] = Body(default={}),
    db: Session = Depends(get_db)
):
    """
    POST /api/interviews/ai/{interview_id}/evaluate
    Triggers asynchronous evaluation generation for an interview session.
    """
    eval_ver = payload.get("evaluation_version", "v1.0")
    result = EvaluationService.evaluate_interview(db, interview_id, evaluation_version=eval_ver)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result

@ai_router.get("/evaluation")
def get_evaluation(interview_id: str, db: Session = Depends(get_db)):
    """
    GET /api/interviews/ai/{interview_id}/evaluation
    Returns structured evaluation with competencies, JD alignment, project verification, and HR decision.
    """
    result = EvaluationService.get_evaluation(db, interview_id)
    if result.get("status") == "not_found":
        # Auto-trigger evaluation if interview is completed
        sess = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if sess and sess.status in ["COMPLETED", "IN_PROGRESS", "HUMAN_TAKEOVER"]:
            return EvaluationService.evaluate_interview(db, interview_id)
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result

@ai_router.get("/evaluation/evidence")
def get_evaluation_evidence(interview_id: str, db: Session = Depends(get_db)):
    """
    GET /api/interviews/ai/{interview_id}/evaluation/evidence
    Returns itemized evidence collected from transcript, Q&A, and coding logs.
    """
    evidence = EvidenceCollector.collect(db, interview_id)
    return {
        "interview_id": interview_id,
        "questions": evidence["questions"],
        "answers": evidence["answers"],
        "coding_observations": evidence.get("vision_observations", []),
        "project_claims": evidence.get("project_claims", [])
    }

@ai_router.get("/evaluation/competencies")
def get_evaluation_competencies(interview_id: str, db: Session = Depends(get_db)):
    """
    GET /api/interviews/ai/{interview_id}/evaluation/competencies
    Returns itemized 1–5 scale competency evaluation breakdown.
    """
    eval_res = EvaluationService.get_evaluation(db, interview_id)
    if eval_res.get("status") == "not_found":
        eval_res = EvaluationService.evaluate_interview(db, interview_id)
    return {"competencies": eval_res.get("competencies", [])}

@ai_router.get("/evaluation/jd-alignment")
def get_evaluation_jd_alignment(interview_id: str, db: Session = Depends(get_db)):
    """
    GET /api/interviews/ai/{interview_id}/evaluation/jd-alignment
    Returns JD requirement alignment grid (DEMONSTRATED, PARTIALLY_DEMONSTRATED, NOT_TESTED, NOT_DEMONSTRATED).
    """
    eval_res = EvaluationService.get_evaluation(db, interview_id)
    if eval_res.get("status") == "not_found":
        eval_res = EvaluationService.evaluate_interview(db, interview_id)
    return {"jd_alignment": eval_res.get("jd_alignment", [])}

@ai_router.post("/evaluation/re-evaluate")
def re_evaluate_interview(
    interview_id: str,
    payload: Dict[str, Any] = Body(default={}),
    db: Session = Depends(get_db)
):
    """
    POST /api/interviews/ai/{interview_id}/evaluation/re-evaluate
    Creates a new evaluation version (e.g. v1.1) without overwriting historical evaluations.
    """
    new_ver = payload.get("evaluation_version", f"v1.{int(datetime.utcnow().timestamp()) % 100}")
    result = EvaluationService.evaluate_interview(db, interview_id, evaluation_version=new_ver)
    return result

@ai_router.post("/evaluation/decision")
@hr_router.post("/decision")
def record_hr_decision(
    interview_id: str,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    POST /api/interviews/{interview_id}/decision
    Records human HR decision (MOVE_TO_NEXT_STAGE, REQUEST_HUMAN_REVIEW, HOLD, REJECT, ADVANCE_TO_OFFER, END_PROCESS)
    and advances application in WorkflowEngine.
    """
    decision_val = payload.get("decision")
    reason = payload.get("reason") or payload.get("decision_reason") or "HR review completed"
    user_id = payload.get("user_id", "hr_admin")

    if not decision_val:
        raise HTTPException(status_code=400, detail="Decision field is required")

    eval_res = EvaluationService.get_evaluation(db, interview_id)
    eval_id = eval_res.get("evaluation_id")
    if not eval_id:
        # Evaluate first if missing
        new_eval = EvaluationService.evaluate_interview(db, interview_id)
        eval_id = new_eval.get("evaluation_id")

    # Record HR Decision
    dec_obj = EvaluationDecision(
        id=f"DEC-{int(datetime.utcnow().timestamp()*1000)}",
        evaluation_id=eval_id,
        interview_id=interview_id,
        decision=decision_val,
        decided_by_user_id=user_id,
        decision_reason=reason,
        decided_at=datetime.utcnow()
    )
    db.add(dec_obj)
    db.commit()

    # Advance Workflow Engine if applicable
    sess = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    wf_result = None
    if sess:
        app_obj = db.query(Application).filter(Application.candidate_id == sess.candidate_id, Application.job_id == sess.job_id).first()
        if app_obj and decision_val in ["MOVE_TO_NEXT_STAGE", "ADVANCE_TO_OFFER"]:
            try:
                wf_result = HiringWorkflowEngine.advance_to_next_step(db, app_obj.id, hr_decision="APPROVE")
            except Exception as e:
                logger.warning(f"Could not advance workflow: {e}")

    return {
        "status": "success",
        "interview_id": interview_id,
        "decision": decision_val,
        "reason": reason,
        "decided_at": dec_obj.decided_at.isoformat(),
        "workflow_advancement": wf_result
    }
