import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.domain import CandidateWorkflow, CandidateWorkflowStep, HiringWorkflow
from app.services.workflow.workflow_execution_engine import WorkflowExecutionEngine

logger = logging.getLogger("workflow_routes")

workflow_router = APIRouter(prefix="/api/workflows", tags=["Hiring Workflows"])
candidate_wf_router = APIRouter(prefix="/api/candidates/{candidate_id}/workflow", tags=["Candidate Workflow Execution"])

# --- 1. WORKFLOW PUBLISHING, SIMULATION & TEMPLATES ---

@workflow_router.post("/{workflow_id}/publish")
def publish_workflow_endpoint(workflow_id: str, db: Session = Depends(get_db)):
    """
    POST /api/workflows/{workflow_id}/publish
    Publishes a hiring workflow version (e.g., v1 -> v2) and locks it.
    """
    res = WorkflowExecutionEngine.publish_workflow(db, workflow_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@workflow_router.post("/{workflow_id}/validate")
def validate_workflow_endpoint(workflow_id: str, db: Session = Depends(get_db)):
    """
    POST /api/workflows/{workflow_id}/validate
    Validates a workflow configuration prior to publishing.
    """
    return WorkflowExecutionEngine.validate_workflow(db, workflow_id)

@workflow_router.post("/{workflow_id}/simulate")
def simulate_workflow_endpoint(workflow_id: str, db: Session = Depends(get_db)):
    """
    POST /api/workflows/{workflow_id}/simulate
    Dry-run simulation of workflow steps without contacting real candidates.
    """
    res = WorkflowExecutionEngine.simulate_workflow(db, workflow_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@workflow_router.get("/templates")
def list_workflow_templates_endpoint():
    """
    GET /api/workflows/templates
    Returns configurable System / Template hiring workflows.
    """
    return [
        {
            "id": "tpl-se-standard",
            "name": "Software Engineer Standard",
            "description": "Standard 6-stage technical hiring workflow.",
            "steps": [
                {"name": "Resume Screening", "type": "AI_ACTION"},
                {"name": "AI HR Call", "type": "VOICE_CALL"},
                {"name": "Technical Interview", "type": "INTERVIEW"},
                {"name": "Coding Discussion", "type": "ASSESSMENT"},
                {"name": "Hiring Manager Review", "type": "APPROVAL"},
                {"name": "Final HR Decision", "type": "OFFER"}
            ]
        },
        {
            "id": "tpl-ai-engineer",
            "name": "AI Engineer Advanced",
            "description": "Comprehensive 8-stage AI/ML hiring workflow.",
            "steps": [
                {"name": "Resume Screening", "type": "AI_ACTION"},
                {"name": "AI HR Screening Call", "type": "VOICE_CALL"},
                {"name": "Technical Deep-Dive", "type": "INTERVIEW"},
                {"name": "RAG Practical Task", "type": "ASSESSMENT"},
                {"name": "Coding Discussion", "type": "INTERVIEW"},
                {"name": "System Design", "type": "INTERVIEW"},
                {"name": "Hiring Manager Review", "type": "APPROVAL"},
                {"name": "Final Offer", "type": "OFFER"}
            ]
        }
    ]

@workflow_router.get("/{workflow_id}/analytics")
def get_workflow_analytics_endpoint(workflow_id: str, db: Session = Depends(get_db)):
    """
    GET /api/workflows/{workflow_id}/analytics
    Calculates workflow analytics (candidates per stage, bottleneck stats).
    """
    return WorkflowExecutionEngine.get_workflow_analytics(db, workflow_id)

# --- 2. CANDIDATE WORKFLOW EXECUTION APIs ---

@candidate_wf_router.post("/start")
def start_candidate_workflow(
    candidate_id: str,
    payload: Dict[str, Any] = Body(default={}),
    db: Session = Depends(get_db)
):
    """
    POST /api/candidates/{candidate_id}/workflow/start
    Starts a candidate workflow locked to the current published workflow version.
    """
    job_id = payload.get("job_id") or payload.get("jobId")
    workflow_id = payload.get("workflow_id") or payload.get("workflowId")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required")

    res = WorkflowExecutionEngine.start_workflow(db, candidate_id, job_id, workflow_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@candidate_wf_router.get("")
def get_candidate_workflow(candidate_id: str, db: Session = Depends(get_db)):
    """
    GET /api/candidates/{candidate_id}/workflow
    Fetches candidate workflow state and current active step.
    """
    cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == candidate_id).order_by(CandidateWorkflow.started_at.desc()).first()
    if not cwf:
        raise HTTPException(status_code=404, detail="Candidate workflow not found")

    return WorkflowExecutionEngine.get_current_step(db, cwf.id)

@candidate_wf_router.get("/timeline")
def get_candidate_workflow_timeline(candidate_id: str, db: Session = Depends(get_db)):
    """
    GET /api/candidates/{candidate_id}/workflow/timeline
    Returns real event history timeline for the candidate workflow.
    """
    return {
        "candidate_id": candidate_id,
        "timeline": WorkflowExecutionEngine.get_workflow_timeline(db, candidate_id)
    }

@candidate_wf_router.post("/pause")
def pause_candidate_workflow(candidate_id: str, db: Session = Depends(get_db)):
    """
    POST /api/candidates/{candidate_id}/workflow/pause
    Pauses candidate workflow execution.
    """
    cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == candidate_id).order_by(CandidateWorkflow.started_at.desc()).first()
    if not cwf:
        raise HTTPException(status_code=404, detail="Candidate workflow not found")
    return WorkflowExecutionEngine.pause_workflow(db, cwf.id)

@candidate_wf_router.post("/resume")
def resume_candidate_workflow(candidate_id: str, db: Session = Depends(get_db)):
    """
    POST /api/candidates/{candidate_id}/workflow/resume
    Resumes a paused candidate workflow.
    """
    cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == candidate_id).order_by(CandidateWorkflow.started_at.desc()).first()
    if not cwf:
        raise HTTPException(status_code=404, detail="Candidate workflow not found")
    return WorkflowExecutionEngine.resume_workflow(db, cwf.id)

@candidate_wf_router.post("/retry")
def retry_candidate_workflow(candidate_id: str, db: Session = Depends(get_db)):
    """
    POST /api/candidates/{candidate_id}/workflow/retry
    Resets failed step and retries execution.
    """
    cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == candidate_id).order_by(CandidateWorkflow.started_at.desc()).first()
    if not cwf:
        raise HTTPException(status_code=404, detail="Candidate workflow not found")
    return WorkflowExecutionEngine.retry_step(db, cwf.id)

@candidate_wf_router.post("/approve")
def approve_candidate_step(
    candidate_id: str,
    payload: Dict[str, Any] = Body(default={}),
    db: Session = Depends(get_db)
):
    """
    POST /api/candidates/{candidate_id}/workflow/approve
    HR approves current human gate step and advances candidate.
    """
    cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == candidate_id).order_by(CandidateWorkflow.started_at.desc()).first()
    if not cwf:
        raise HTTPException(status_code=404, detail="Candidate workflow not found")

    user_id = payload.get("user_id", "hr_admin")
    reason = payload.get("reason", "Approved by HR Admin")
    return WorkflowExecutionEngine.approve_step(db, cwf.id, user_id, reason)

@candidate_wf_router.post("/reject")
def reject_candidate_step(
    candidate_id: str,
    payload: Dict[str, Any] = Body(default={}),
    db: Session = Depends(get_db)
):
    """
    POST /api/candidates/{candidate_id}/workflow/reject
    HR rejects candidate at current workflow step.
    """
    cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == candidate_id).order_by(CandidateWorkflow.started_at.desc()).first()
    if not cwf:
        raise HTTPException(status_code=404, detail="Candidate workflow not found")

    user_id = payload.get("user_id", "hr_admin")
    reason = payload.get("reason", "Rejected by HR Admin")
    return WorkflowExecutionEngine.reject_step(db, cwf.id, user_id, reason)

@candidate_wf_router.post("/takeover")
def takeover_candidate_workflow(
    candidate_id: str,
    payload: Dict[str, Any] = Body(default={}),
    db: Session = Depends(get_db)
):
    """
    POST /api/candidates/{candidate_id}/workflow/takeover
    Toggles HR takeover mode (AI Active vs Human Active).
    """
    cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == candidate_id).order_by(CandidateWorkflow.started_at.desc()).first()
    if not cwf:
        raise HTTPException(status_code=404, detail="Candidate workflow not found")

    is_active = payload.get("is_human_takeover", True)
    return WorkflowExecutionEngine.takeover_workflow(db, cwf.id, is_active)

@candidate_wf_router.post("/complete")
def complete_candidate_workflow(candidate_id: str, db: Session = Depends(get_db)):
    """
    POST /api/candidates/{candidate_id}/workflow/complete
    Finalizes candidate workflow execution.
    """
    cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == candidate_id).order_by(CandidateWorkflow.started_at.desc()).first()
    if not cwf:
        raise HTTPException(status_code=404, detail="Candidate workflow not found")

    return WorkflowExecutionEngine.move_to_next_step(db, cwf.id, hr_decision="APPROVE")
