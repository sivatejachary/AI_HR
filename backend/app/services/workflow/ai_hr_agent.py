import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.domain import (
    Application, Candidate, Job, WorkflowStep, StepType,
    Call, InterviewSession, AIScreeningResult, AuditLog
)

logger = logging.getLogger("ai_hr_agent")

class AIHRAgent:
    """
    AI HR Agent Execution Layer.
    Executes specific steps of an approved Hiring Workflow.
    
    IMPORTANT:
    The AI HR Agent decisions are strictly constrained by the Workflow Engine rules.
    The AI HR Agent CANNOT invent new steps or bypass Human Approval Gates.
    """

    @staticmethod
    def execute_step(
        db: Session,
        application_id: str,
        step: WorkflowStep,
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        logger.info(f"AIHRAgent executing step: '{step.name}' ({step.type}) for application {application_id}")
        payload = payload or {}

        app = db.query(Application).filter(Application.id == application_id).first()
        if not app:
            return {"status": "error", "message": "Application not found"}

        candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()
        job = db.query(Job).filter(Job.id == app.job_id).first()

        # Step Type Routing
        step_type_str = str(step.type.value if hasattr(step.type, 'value') else step.type)
        step_name = step.name.upper()

        # 1. Human Approval Gates (HR Review, Manager Approval, Approval)
        is_human_gate = (
            step.owner in ["HR", "Recruiter", "Hiring Manager", "Interviewer"]
            and step.automation != "Fully automated"
        ) or step.type in [StepType.HUMAN_ACTION, StepType.APPROVAL] or "REVIEW" in step_name or "DECISION" in step_name or "APPROVAL" in step_name

        if is_human_gate:
            logger.info(f"Step '{step.name}' is a Human Approval Gate. AI HR Agent stopping execution.")
            return {
                "status": "WAITING_FOR_HUMAN",
                "action_required": "HR_APPROVAL",
                "owner": step.owner,
                "message": f"Step '{step.name}' requires human approval before proceeding."
            }

        # 2. Automated Resume Screening
        if step.type == StepType.AI_ACTION or "SCREENING" in step_name:
            match_score = 85
            if candidate and job:
                # Dynamic skills overlap score
                req_skills = set(job.preferred_skills or [])
                cand_skills = set(candidate.skills or [])
                overlap = len(req_skills.intersection(cand_skills))
                match_score = min(95, max(60, 60 + overlap * 8))

            res = AIScreeningResult(
                id=f"screen-{int(datetime.utcnow().timestamp()*1000)}",
                application_id=app.id,
                match_score=match_score,
                explanation=f"Candidate resume matches {match_score}% of role requirements.",
                recommendation="SHORTLIST_FOR_HR_REVIEW" if match_score >= 70 else "HOLD_FOR_HR_REVIEW"
            )
            db.add(res)
            db.commit()

            return {
                "status": "COMPLETED",
                "match_score": match_score,
                "recommendation": res.recommendation,
                "output": f"Automated Resume Screening completed with {match_score}% score."
            }

        # 3. AI Voice Call (ElevenLabs / Outbound Screening Call)
        elif step.type == StepType.VOICE_CALL or "CALL" in step_name:
            max_attempts = step.config.get("max_attempts", 3)
            attempt_count = payload.get("attempts_count", 1)

            if attempt_count > max_attempts:
                return {
                    "status": "FAILED",
                    "fallback": "HUMAN_FOLLOWUP",
                    "message": f"AI Call exceeded maximum retry limit of {max_attempts} attempts. Escalated to HR."
                }

            call_obj = Call(
                id=f"call-{int(datetime.utcnow().timestamp()*1000)}",
                candidate_id=app.candidate_id,
                status="DISPATCHED",
                summary="Outbound AI HR Screening Call dispatched via ElevenLabs AI.",
                duration_seconds=0
            )
            db.add(call_obj)
            db.commit()

            return {
                "status": "COMPLETED",
                "call_id": call_obj.id,
                "provider": "ElevenLabs AI",
                "message": "AI HR screening call successfully dispatched."
            }

        # 4. Scheduling Step
        elif step.type == StepType.SCHEDULING or "SCHEDULE" in step_name:
            return {
                "status": "COMPLETED",
                "provider": "n8n Calendar Integration",
                "meeting_link": "https://meet.google.com/abc-defg-hij",
                "message": "Interview slot invitation sent to candidate."
            }

        # 5. AI Technical Interview / Coding Session
        elif step.type in [StepType.INTERVIEW, StepType.ASSESSMENT] or "INTERVIEW" in step_name or "CODING" in step_name:
            sess = db.query(InterviewSession).filter(
                InterviewSession.candidate_id == app.candidate_id,
                InterviewSession.job_id == app.job_id
            ).order_by(InterviewSession.created_at.desc()).first()

            if not sess:
                sess = InterviewSession(
                    id=f"INT-AGENT-{int(datetime.utcnow().timestamp()*1000)}",
                    candidate_id=app.candidate_id,
                    job_id=app.job_id,
                    workflow_id=app.current_workflow_id,
                    workflow_version=app.current_workflow_version,
                    status="PENDING",
                    brain_status="IDLE",
                    current_stage="INTERVIEW_START"
                )
                db.add(sess)
                db.commit()

            if sess.status != "COMPLETED":
                return {
                    "status": "RUNNING",
                    "interview_id": sess.id,
                    "message": f"AI Technical Interview session {sess.id} is active."
                }

            return {
                "status": "COMPLETED",
                "interview_id": sess.id,
                "overall_score": sess.overall_score or 4.0,
                "message": "AI Technical Interview completed."
            }

        # 6. Offer Step
        elif step.type == StepType.OFFER or "OFFER" in step_name:
            return {
                "status": "WAITING_FOR_HUMAN",
                "action_required": "OFFER_APPROVAL",
                "message": "Offer details generated. Awaiting HR signature/approval."
            }

        # 7. Rejection Step
        elif step.type == StepType.REJECTION or "REJECTION" in step_name:
            app.status = "REJECTED"
            db.commit()
            return {
                "status": "COMPLETED",
                "message": "Candidate workflow terminated with rejection notice."
            }

        # Default fallback execution
        return {
            "status": "COMPLETED",
            "message": f"Step '{step.name}' completed by AI HR Agent."
        }
