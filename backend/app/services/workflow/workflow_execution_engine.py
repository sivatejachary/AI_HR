import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.models.domain import (
    HiringWorkflow, WorkflowStep, HiringWorkflowVersion,
    CandidateWorkflow, CandidateWorkflowStep, WorkflowEvent,
    Application, Candidate, Job, AuditLog, StepType
)
from app.services.workflow.ai_hr_agent import AIHRAgent

logger = logging.getLogger("workflow_execution_engine")

class WorkflowExecutionEngine:
    """
    Source of Truth Executable Hiring Lifecycle Workflow Engine.
    
    Controls workflow execution, versioning lock-in, human approval gates,
    pausing, HR takeover, retries, branching transitions, and event trails.
    """

    @staticmethod
    def publish_workflow(db: Session, workflow_id: str) -> Dict[str, Any]:
        """Publishes a workflow and creates a new immutable version (e.g., v1 -> v2)."""
        wf = db.query(HiringWorkflow).filter(HiringWorkflow.id == workflow_id).first()
        if not wf:
            return {"status": "error", "message": "Workflow not found"}

        # Validate workflow before publishing
        val_res = WorkflowExecutionEngine.validate_workflow(db, workflow_id)
        if not val_res["is_valid"]:
            return {"status": "error", "message": f"Validation failed: {', '.join(val_res['errors'])}"}

        steps = db.query(WorkflowStep).filter(WorkflowStep.workflow_id == wf.id, WorkflowStep.is_enabled != False).order_by(WorkflowStep.order.asc()).all()
        steps_snapshot = [
            {
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "type": str(s.type.value if hasattr(s.type, 'value') else s.type),
                "order": s.order,
                "owner": s.owner,
                "automation": s.automation,
                "passing_score": s.passing_score,
                "is_required": s.is_required,
                "config": s.config or {}
            } for s in steps
        ]

        new_version_num = (wf.version or 1) + (1 if wf.status == "Published" else 0)
        wf.version = new_version_num
        wf.status = "Published"

        wf_version = HiringWorkflowVersion(
            id=f"wfver-{int(datetime.utcnow().timestamp()*1000)}-v{new_version_num}",
            workflow_id=wf.id,
            version=new_version_num,
            status="Published",
            published_at=datetime.utcnow(),
            steps_snapshot=steps_snapshot
        )
        db.add(wf_version)
        db.commit()

        logger.info(f"Published Workflow {wf.id} Version v{new_version_num}")
        return {
            "status": "success",
            "workflow_id": wf.id,
            "version": new_version_num,
            "published_at": wf_version.published_at.isoformat()
        }

    @staticmethod
    def start_workflow(db: Session, candidate_id: str, job_id: str, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Starts a candidate workflow locked to the current published workflow version."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"status": "error", "message": "Job opening not found"}

        target_wf_id = workflow_id or job.workflow_id
        wf = db.query(HiringWorkflow).filter(HiringWorkflow.id == target_wf_id).first()
        if not wf:
            wf = db.query(HiringWorkflow).filter(HiringWorkflow.is_active == True).first()
        if not wf:
            return {"status": "error", "message": "No active workflow available for job"}

        steps = db.query(WorkflowStep).filter(WorkflowStep.workflow_id == wf.id, WorkflowStep.is_enabled != False).order_by(WorkflowStep.order.asc()).all()
        if not steps:
            return {"status": "error", "message": "Workflow has no enabled steps"}

        # Lock candidate workflow to published version number
        locked_version = wf.version or 1

        cand_wf_id = f"cwf-{int(datetime.utcnow().timestamp()*1000)}"
        cand_wf = CandidateWorkflow(
            id=cand_wf_id,
            candidate_id=candidate_id,
            job_id=job_id,
            workflow_id=wf.id,
            workflow_version=locked_version,
            current_step_id=steps[0].id,
            current_step_name=steps[0].name,
            status="IN_PROGRESS",
            started_at=datetime.utcnow()
        )
        db.add(cand_wf)

        # Create step tracker
        cand_step = CandidateWorkflowStep(
            id=f"cws-{int(datetime.utcnow().timestamp()*1000)}-{steps[0].id}",
            candidate_workflow_id=cand_wf_id,
            workflow_step_id=steps[0].id,
            step_name=steps[0].name,
            step_type=str(steps[0].type.value if hasattr(steps[0].type, 'value') else steps[0].type),
            status="PENDING",
            started_at=datetime.utcnow()
        )
        db.add(cand_step)

        # Record candidate.workflow.started event
        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-start",
            candidate_workflow_id=cand_wf_id,
            candidate_id=candidate_id,
            job_id=job_id,
            event_type="candidate.workflow.started",
            step_id=steps[0].id,
            actor_type="SYSTEM",
            payload_json={"workflow_id": wf.id, "workflow_version": locked_version, "first_step": steps[0].name}
        )
        db.add(evt)
        db.commit()

        # Update or create application reference
        app = db.query(Application).filter(Application.candidate_id == candidate_id, Application.job_id == job_id).first()
        if not app:
            app = Application(
                id=f"app-{int(datetime.utcnow().timestamp()*1000)}",
                job_id=job_id,
                candidate_id=candidate_id,
                source="CAREER_PAGE",
                status="NEW",
                current_stage=steps[0].name,
                current_workflow_id=wf.id,
                current_workflow_version=locked_version,
                current_step_id=steps[0].id,
                current_step_name=steps[0].name,
                step_status="PENDING"
            )
            db.add(app)
            db.commit()
        else:
            app.current_workflow_id = wf.id
            app.current_workflow_version = locked_version
            app.current_step_id = steps[0].id
            app.current_step_name = steps[0].name
            app.step_status = "PENDING"
            db.commit()

        # Execute first step
        return WorkflowExecutionEngine.execute_current_step(db, cand_wf_id, trigger_event="WORKFLOW_START")

    @staticmethod
    def get_current_step(db: Session, candidate_workflow_id: str) -> Dict[str, Any]:
        """Gets current active step details for a candidate workflow."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        step = db.query(WorkflowStep).filter(WorkflowStep.id == cwf.current_step_id).first()
        cws = db.query(CandidateWorkflowStep).filter(
            CandidateWorkflowStep.candidate_workflow_id == cwf.id,
            CandidateWorkflowStep.workflow_step_id == cwf.current_step_id
        ).order_by(CandidateWorkflowStep.started_at.desc()).first()

        return {
            "candidate_workflow_id": cwf.id,
            "candidate_id": cwf.candidate_id,
            "job_id": cwf.job_id,
            "workflow_id": cwf.workflow_id,
            "workflow_version": cwf.workflow_version,
            "status": cwf.status,
            "is_paused": cwf.is_paused,
            "is_human_takeover": cwf.is_human_takeover,
            "current_step": {
                "id": step.id if step else cwf.current_step_id,
                "name": step.name if step else cwf.current_step_name,
                "type": str(step.type.value if step and hasattr(step.type, 'value') else (step.type if step else "UNKNOWN")),
                "owner": step.owner if step else "HR",
                "status": cws.status if cws else "PENDING"
            }
        }

    @staticmethod
    def execute_current_step(db: Session, candidate_workflow_id: str, trigger_event: str = "MANUAL", payload: dict = None) -> Dict[str, Any]:
        """Executes the current step of a candidate workflow through AIHRAgent or Human Approval Gate."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        if cwf.is_paused:
            cwf.status = "PAUSED"
            db.commit()
            return {"status": "paused", "message": "Candidate workflow is currently paused by HR."}

        if cwf.is_human_takeover:
            cwf.status = "WAITING_FOR_HUMAN"
            db.commit()
            return {"status": "human_active", "message": "HR takeover active. AI Agent execution suspended."}

        step = db.query(WorkflowStep).filter(WorkflowStep.id == cwf.current_step_id).first()
        if not step:
            return {"status": "error", "message": f"Step {cwf.current_step_id} not found"}

        cws = db.query(CandidateWorkflowStep).filter(
            CandidateWorkflowStep.candidate_workflow_id == cwf.id,
            CandidateWorkflowStep.workflow_step_id == step.id
        ).order_by(CandidateWorkflowStep.started_at.desc()).first()

        if not cws:
            cws = CandidateWorkflowStep(
                id=f"cws-{int(datetime.utcnow().timestamp()*1000)}-{step.id}",
                candidate_workflow_id=cwf.id,
                workflow_step_id=step.id,
                step_name=step.name,
                step_type=str(step.type.value if hasattr(step.type, 'value') else step.type),
                status="RUNNING",
                started_at=datetime.utcnow()
            )
            db.add(cws)

        cws.status = "RUNNING"
        cws.attempts_count = (cws.attempts_count or 0) + 1
        db.commit()

        # Log event: workflow.step.started
        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-stepstart",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="workflow.step.started",
            step_id=step.id,
            actor_type="AI",
            payload_json={"step_name": step.name, "attempt": cws.attempts_count, "triggered_by": trigger_event}
        )
        db.add(evt)
        db.commit()

        # Find application
        app = db.query(Application).filter(Application.candidate_id == cwf.candidate_id, Application.job_id == cwf.job_id).first()
        app_id = app.id if app else f"app-fake-{cwf.candidate_id}"

        # Delegate execution to AIHRAgent
        res = AIHRAgent.execute_step(db, app_id, step, payload={"attempts_count": cws.attempts_count})
        res_status = res.get("status", "COMPLETED")

        cws.result_json = res

        if res_status == "WAITING_FOR_HUMAN":
            cws.status = "WAITING_FOR_HUMAN"
            cwf.status = "WAITING_FOR_HUMAN"
            if app:
                app.step_status = "WAITING_FOR_HR"
            db.commit()

            evt_human = WorkflowEvent(
                id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-human",
                candidate_workflow_id=cwf.id,
                candidate_id=cwf.candidate_id,
                job_id=cwf.job_id,
                event_type="hr.review.required",
                step_id=step.id,
                actor_type="SYSTEM",
                payload_json=res
            )
            db.add(evt_human)
            db.commit()
            return {"status": "waiting_for_human", "step_name": step.name, "message": res.get("message")}

        elif res_status == "COMPLETED":
            cws.status = "COMPLETED"
            cws.completed_at = datetime.utcnow()
            db.commit()

            evt_comp = WorkflowEvent(
                id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-stepcomp",
                candidate_workflow_id=cwf.id,
                candidate_id=cwf.candidate_id,
                job_id=cwf.job_id,
                event_type="workflow.step.completed",
                step_id=step.id,
                actor_type="AI",
                payload_json=res
            )
            db.add(evt_comp)
            db.commit()

            # Advance to next step
            return WorkflowExecutionEngine.move_to_next_step(db, cwf.id)

        elif res_status == "FAILED":
            cws.status = "FAILED"
            cws.error_message = res.get("message", "Step execution failed")
            cwf.status = "FAILED"
            if app:
                app.step_status = "FAILED"
            db.commit()

            evt_fail = WorkflowEvent(
                id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-stepfail",
                candidate_workflow_id=cwf.id,
                candidate_id=cwf.candidate_id,
                job_id=cwf.job_id,
                event_type="workflow.step.failed",
                step_id=step.id,
                actor_type="AI",
                payload_json=res
            )
            db.add(evt_fail)
            db.commit()
            return {"status": "failed", "step_name": step.name, "error": cws.error_message}

        return {"status": res_status, "step_name": step.name, "details": res}

    @staticmethod
    def move_to_next_step(db: Session, candidate_workflow_id: str, hr_decision: str = "APPROVE") -> Dict[str, Any]:
        """Moves candidate workflow to the next ordered step."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        steps = db.query(WorkflowStep).filter(WorkflowStep.workflow_id == cwf.workflow_id, WorkflowStep.is_enabled != False).order_by(WorkflowStep.order.asc()).all()
        if not steps:
            return {"status": "error", "message": "No steps in workflow"}

        current_idx = 0
        if cwf.current_step_id:
            for idx, s in enumerate(steps):
                if s.id == cwf.current_step_id:
                    current_idx = idx
                    break

        if hr_decision == "REJECT":
            cwf.status = "REJECTED"
            cwf.completed_at = datetime.utcnow()
            db.commit()

            evt = WorkflowEvent(
                id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-reject",
                candidate_workflow_id=cwf.id,
                candidate_id=cwf.candidate_id,
                job_id=cwf.job_id,
                event_type="candidate.workflow.rejected",
                actor_type="HR",
                payload_json={"reason": "HR Rejection"}
            )
            db.add(evt)
            db.commit()
            return {"status": "rejected", "message": "Candidate workflow rejected by HR."}

        if current_idx < len(steps) - 1:
            next_step = steps[current_idx + 1]
            cwf.current_step_id = next_step.id
            cwf.current_step_name = next_step.name
            cwf.status = "IN_PROGRESS"
            db.commit()

            app = db.query(Application).filter(Application.candidate_id == cwf.candidate_id, Application.job_id == cwf.job_id).first()
            if app:
                app.current_step_id = next_step.id
                app.current_step_name = next_step.name
                app.current_stage = next_step.name
                app.step_status = "PENDING"
                db.commit()

            # Execute newly assigned step
            return WorkflowExecutionEngine.execute_current_step(db, cwf.id, trigger_event="NEXT_STEP_ADVANCE")
        else:
            cwf.status = "COMPLETED"
            cwf.completed_at = datetime.utcnow()
            db.commit()

            app = db.query(Application).filter(Application.candidate_id == cwf.candidate_id, Application.job_id == cwf.job_id).first()
            if app:
                app.status = "SELECTED"
                app.step_status = "COMPLETED"
                db.commit()

            evt = WorkflowEvent(
                id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-complete",
                candidate_workflow_id=cwf.id,
                candidate_id=cwf.candidate_id,
                job_id=cwf.job_id,
                event_type="workflow.completed",
                actor_type="SYSTEM",
                payload_json={"status": "COMPLETED"}
            )
            db.add(evt)
            db.commit()
            return {"status": "workflow_completed", "message": "Candidate successfully completed all workflow steps."}

    @staticmethod
    def pause_workflow(db: Session, candidate_workflow_id: str) -> Dict[str, Any]:
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        cwf.is_paused = True
        cwf.status = "PAUSED"
        db.commit()

        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-pause",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="workflow.paused",
            actor_type="HR",
            payload_json={"paused_by": "HR Admin"}
        )
        db.add(evt)
        db.commit()
        return {"status": "success", "message": "Candidate workflow paused."}

    @staticmethod
    def resume_workflow(db: Session, candidate_workflow_id: str) -> Dict[str, Any]:
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        cwf.is_paused = False
        cwf.status = "IN_PROGRESS"
        db.commit()

        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-resume",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="workflow.resumed",
            actor_type="HR",
            payload_json={"resumed_by": "HR Admin"}
        )
        db.add(evt)
        db.commit()

        return WorkflowExecutionEngine.execute_current_step(db, cwf.id, trigger_event="RESUME_WORKFLOW")

    @staticmethod
    def takeover_workflow(db: Session, candidate_workflow_id: str, is_active: bool = True) -> Dict[str, Any]:
        """Toggles HR Takeover / Human Active mode."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        cwf.is_human_takeover = is_active
        cwf.status = "WAITING_FOR_HUMAN" if is_active else "IN_PROGRESS"
        db.commit()

        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-takeover",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="hr.takeover.activated" if is_active else "hr.takeover.deactivated",
            actor_type="HR",
            payload_json={"is_human_takeover": is_active}
        )
        db.add(evt)
        db.commit()
        return {"status": "success", "is_human_takeover": is_active}

    @staticmethod
    def approve_step(db: Session, candidate_workflow_id: str, user_id: str = "hr_admin", reason: str = "") -> Dict[str, Any]:
        """HR approves current gate step and advances candidate."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-approved",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="hr.review.completed",
            step_id=cwf.current_step_id,
            actor_type="HR",
            actor_id=user_id,
            payload_json={"decision": "APPROVED", "reason": reason}
        )
        db.add(evt)
        db.commit()

        return WorkflowExecutionEngine.move_to_next_step(db, cwf.id, hr_decision="APPROVE")

    @staticmethod
    def reject_step(db: Session, candidate_workflow_id: str, user_id: str = "hr_admin", reason: str = "") -> Dict[str, Any]:
        """HR rejects candidate at current gate step."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-rejected",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="hr.review.rejected",
            step_id=cwf.current_step_id,
            actor_type="HR",
            actor_id=user_id,
            payload_json={"decision": "REJECTED", "reason": reason}
        )
        db.add(evt)
        db.commit()

        return WorkflowExecutionEngine.move_to_next_step(db, cwf.id, hr_decision="REJECT")

    @staticmethod
    def retry_step(db: Session, candidate_workflow_id: str) -> Dict[str, Any]:
        """Resets failed or stuck step and re-triggers execution."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        cwf.status = "IN_PROGRESS"
        db.commit()

        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-retry",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="workflow.step.retry",
            step_id=cwf.current_step_id,
            actor_type="HR",
            payload_json={"action": "RETRY_STEP"}
        )
        db.add(evt)
        db.commit()

        return WorkflowExecutionEngine.execute_current_step(db, cwf.id, trigger_event="HR_RETRY")

    @staticmethod
    def validate_workflow(db: Session, workflow_id: str) -> Dict[str, Any]:
        """Validates a workflow structure before publishing."""
        wf = db.query(HiringWorkflow).filter(HiringWorkflow.id == workflow_id).first()
        if not wf:
            return {"is_valid": False, "errors": ["Workflow not found"]}

        steps = db.query(WorkflowStep).filter(WorkflowStep.workflow_id == wf.id, WorkflowStep.is_enabled == True).order_by(WorkflowStep.order.asc()).all()
        errors = []

        if len(steps) == 0:
            errors.append("Workflow must contain at least one step.")

        for s in steps:
            s_type = str(s.type.value if hasattr(s.type, 'value') else s.type)
            if not s.name or not s.name.strip():
                errors.append(f"Step {s.id} is missing a valid name.")

            if s_type in ["HUMAN_ACTION", "APPROVAL"] and not s.owner:
                errors.append(f"Approval step '{s.name}' requires an assigned approver owner.")

            if "INTERVIEW" in s.name.upper() and s.duration_minutes <= 0:
                errors.append(f"Interview step '{s.name}' requires duration > 0 minutes.")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "step_count": len(steps)
        }

    @staticmethod
    def simulate_workflow(db: Session, workflow_id: str) -> Dict[str, Any]:
        """Dry-run simulation of workflow steps without contacting real candidates or sending calls/emails."""
        wf = db.query(HiringWorkflow).filter(HiringWorkflow.id == workflow_id).first()
        if not wf:
            return {"status": "error", "message": "Workflow not found"}

        val_res = WorkflowExecutionEngine.validate_workflow(db, workflow_id)
        if not val_res["is_valid"]:
            return {"status": "error", "message": f"Simulation blocked by validation errors: {', '.join(val_res['errors'])}"}

        steps = db.query(WorkflowStep).filter(WorkflowStep.workflow_id == wf.id, WorkflowStep.is_enabled == True).order_by(WorkflowStep.order.asc()).all()

        simulated_trace = []
        for idx, s in enumerate(steps):
            s_type = str(s.type.value if hasattr(s.type, 'value') else s.type)
            sim_status = "PASSED"
            note = f"Simulated execution for {s.name} ({s_type})"

            if s.owner in ["HR", "Recruiter", "Hiring Manager"] or s_type in ["HUMAN_ACTION", "APPROVAL"]:
                sim_status = "WAITING_FOR_HUMAN"
                note = f"Step '{s.name}' requires HR approval gate during simulation."

            simulated_trace.append({
                "step_order": idx + 1,
                "step_name": s.name,
                "step_type": s_type,
                "simulation_status": sim_status,
                "note": note
            })

        return {
            "status": "success",
            "workflow_name": wf.name,
            "total_steps": len(steps),
            "simulated_trace": simulated_trace
        }

    @staticmethod
    def get_workflow_timeline(db: Session, candidate_id: str) -> List[Dict[str, Any]]:
        """Returns verified audit event timeline for a candidate workflow."""
        evts = db.query(WorkflowEvent).filter(WorkflowEvent.candidate_id == candidate_id).order_by(WorkflowEvent.timestamp.asc()).all()
        return [
            {
                "id": e.id,
                "event_type": e.event_type,
                "step_id": e.step_id,
                "actor_type": e.actor_type,
                "actor_id": e.actor_id,
                "payload": e.payload_json,
                "timestamp": e.timestamp.isoformat()
            } for e in evts
        ]

    @staticmethod
    def get_workflow_analytics(db: Session, workflow_id: str) -> Dict[str, Any]:
        """Calculates real data analytics for a hiring workflow."""
        cwfs = db.query(CandidateWorkflow).filter(CandidateWorkflow.workflow_id == workflow_id).all()
        total_entered = len(cwfs)
        in_progress = sum(1 for c in cwfs if c.status == "IN_PROGRESS")
        waiting_human = sum(1 for c in cwfs if c.status == "WAITING_FOR_HUMAN")
        completed = sum(1 for c in cwfs if c.status == "COMPLETED")
        rejected = sum(1 for c in cwfs if c.status == "REJECTED")
        paused = sum(1 for c in cwfs if c.status == "PAUSED")

        # Stage breakdown
        steps = db.query(WorkflowStep).filter(WorkflowStep.workflow_id == workflow_id, WorkflowStep.is_enabled == True).order_by(WorkflowStep.order.asc()).all()
        stage_counts = []
        for s in steps:
            cnt = sum(1 for c in cwfs if c.current_step_id == s.id)
            stage_counts.append({"step_name": s.name, "candidate_count": cnt})

        return {
            "workflow_id": workflow_id,
            "total_candidates_entered": total_entered,
            "in_progress": in_progress,
            "waiting_for_hr": waiting_human,
            "completed": completed,
            "rejected": rejected,
            "paused": paused,
            "stage_breakdown": stage_counts
        }
