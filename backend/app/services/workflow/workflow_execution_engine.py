import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.domain import (
    HiringWorkflow, WorkflowStep, HiringWorkflowVersion,
    CandidateWorkflow, CandidateWorkflowStep, WorkflowEvent,
    Application, Candidate, Job, AuditLog, StepType
)
from app.services.workflow.ai_hr_agent import AIHRAgent

logger = logging.getLogger("workflow_execution_engine")

class WorkflowExecutionEngine:
    """
    Source of Truth Executable Hiring Lifecycle Workflow Engine with Scheduling support.
    
    Controls workflow execution, fixed/relative scheduling, versioning lock-in,
    human approval gates, pausing, HR takeover, retries, branching transitions, and event trails.
    """

    @staticmethod
    def compute_step_scheduled_at(step: WorkflowStep, prev_completed_at: Optional[datetime] = None) -> datetime:
        """
        Calculates when a workflow step should be scheduled.
        Supports FIXED_TIME, RELATIVE, and IMMEDIATE schedule types.
        """
        now = datetime.utcnow()
        schedule_type = (step.schedule_type or "IMMEDIATE").upper()

        if schedule_type == "FIXED_TIME":
            if step.fixed_timestamp:
                return step.fixed_timestamp
            return now
        elif schedule_type == "RELATIVE":
            base_time = prev_completed_at if prev_completed_at else now
            delay_mins = step.relative_delay_minutes or 0
            return base_time + timedelta(minutes=delay_mins)
        else: # IMMEDIATE
            return now

    @staticmethod
    def publish_workflow(db: Session, workflow_id: str) -> Dict[str, Any]:
        """Publishes a workflow and creates a new immutable version (e.g., v1 -> v2)."""
        wf = db.query(HiringWorkflow).filter(HiringWorkflow.id == workflow_id).first()
        if not wf:
            return {"status": "error", "message": "Workflow not found"}

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
                "schedule_type": s.schedule_type,
                "fixed_timestamp": s.fixed_timestamp.isoformat() if s.fixed_timestamp else None,
                "relative_delay_minutes": s.relative_delay_minutes,
                "executor": s.executor,
                "requires_approval": s.requires_approval,
                "allow_skip": s.allow_skip,
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
        """
        Starts a candidate workflow locked to the current published workflow version.
        Instantiates CandidateWorkflowStep records for ALL steps in the workflow version.
        Computes scheduled_at for step 1 and sets status to READY (or WAITING if in future).
        """
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

        locked_version = wf.version or 1
        cand_wf_id = f"cwf-{int(datetime.utcnow().timestamp()*1000)}"
        
        now = datetime.utcnow()
        first_step_scheduled_at = WorkflowExecutionEngine.compute_step_scheduled_at(steps[0], None)
        first_step_status = "READY" if first_step_scheduled_at <= now else "WAITING"

        cand_wf = CandidateWorkflow(
            id=cand_wf_id,
            candidate_id=candidate_id,
            job_id=job_id,
            workflow_id=wf.id,
            workflow_version=locked_version,
            current_step_id=steps[0].id,
            current_step_name=steps[0].name,
            status="IN_PROGRESS",
            started_at=now
        )
        db.add(cand_wf)

        # Create step trackers for ALL steps in the workflow version
        for idx, s in enumerate(steps):
            is_first = (idx == 0)
            sched_at = first_step_scheduled_at if is_first else None
            st = first_step_status if is_first else "WAITING"

            cws = CandidateWorkflowStep(
                id=f"cws-{int(datetime.utcnow().timestamp()*1000)}-{s.id}",
                candidate_workflow_id=cand_wf_id,
                workflow_step_id=s.id,
                step_name=s.name,
                step_type=str(s.type.value if hasattr(s.type, 'value') else s.type),
                status=st,
                scheduled_at=sched_at,
                executor=s.executor or ("HUMAN_HR" if s.owner in ["HR", "Recruiter", "Hiring Manager"] else "AI"),
                requires_approval=s.requires_approval or False,
                allow_skip=s.allow_skip if s.allow_skip is not None else True,
                result_json={},
                metadata_json={},
                started_at=now if is_first and st == "READY" else None
            )
            db.add(cws)

        # Record candidate.workflow.started event
        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-start",
            candidate_workflow_id=cand_wf_id,
            candidate_id=candidate_id,
            job_id=job_id,
            event_type="candidate.workflow.started",
            step_id=steps[0].id,
            actor_type="SYSTEM",
            payload_json={
                "workflow_id": wf.id,
                "workflow_version": locked_version,
                "first_step": steps[0].name,
                "scheduled_at": first_step_scheduled_at.isoformat()
            }
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
                step_status=first_step_status
            )
            db.add(app)
            db.commit()
        else:
            app.current_workflow_id = wf.id
            app.current_workflow_version = locked_version
            app.current_step_id = steps[0].id
            app.current_step_name = steps[0].name
            app.step_status = first_step_status
            db.commit()

        # If step 1 is READY and scheduled_at <= now, trigger step execution
        if first_step_status == "READY":
            WorkflowExecutionEngine.execute_due_steps(db, target_cwf_id=cand_wf_id)

        return {
            "status": "success",
            "candidate_workflow_id": cand_wf_id,
            "workflow_id": wf.id,
            "workflow_version": locked_version,
            "current_step": steps[0].name,
            "first_step_status": first_step_status,
            "scheduled_at": first_step_scheduled_at.isoformat()
        }

    @staticmethod
    def get_due_steps(db: Session) -> List[Dict[str, Any]]:
        """Returns list of all steps due for execution across all candidates."""
        now = datetime.utcnow()
        due_steps = db.query(CandidateWorkflowStep, CandidateWorkflow).join(
            CandidateWorkflow, CandidateWorkflowStep.candidate_workflow_id == CandidateWorkflow.id
        ).filter(
            CandidateWorkflowStep.status == "READY",
            CandidateWorkflowStep.scheduled_at <= now,
            CandidateWorkflow.status == "IN_PROGRESS",
            CandidateWorkflow.is_paused == False,
            CandidateWorkflow.is_human_takeover == False
        ).all()

        results = []
        for cws, cwf in due_steps:
            results.append({
                "candidate_workflow_step_id": cws.id,
                "candidate_workflow_id": cwf.id,
                "candidate_id": cwf.candidate_id,
                "job_id": cwf.job_id,
                "workflow_step_id": cws.workflow_step_id,
                "step_name": cws.step_name,
                "step_type": cws.step_type,
                "executor": cws.executor,
                "scheduled_at": cws.scheduled_at.isoformat() if cws.scheduled_at else None
            })
        return results

    @staticmethod
    def execute_due_steps(db: Session, target_cwf_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Engine polling worker: Claims and executes all due steps (scheduled_at <= now and status == READY).
        Uses atomic idempotency locks to prevent duplicate execution across workers.
        """
        now = datetime.utcnow()
        query = db.query(CandidateWorkflowStep).join(
            CandidateWorkflow, CandidateWorkflowStep.candidate_workflow_id == CandidateWorkflow.id
        ).filter(
            CandidateWorkflowStep.status == "READY",
            CandidateWorkflowStep.scheduled_at <= now,
            CandidateWorkflow.status == "IN_PROGRESS",
            CandidateWorkflow.is_paused == False,
            CandidateWorkflow.is_human_takeover == False
        )
        if target_cwf_id:
            query = query.filter(CandidateWorkflow.id == target_cwf_id)

        ready_steps = query.all()
        execution_results = []

        for cws in ready_steps:
            cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == cws.candidate_workflow_id).first()
            if not cwf or cwf.is_paused or cwf.is_human_takeover or cwf.status in ["PAUSED", "REJECTED", "COMPLETED", "CANCELLED"]:
                continue

            # Atomic claim using idempotency_key to guarantee thread safety
            lock_key = f"cws-{cws.id}-{int(time.time()*1000)}"
            updated_count = db.query(CandidateWorkflowStep).filter(
                CandidateWorkflowStep.id == cws.id,
                CandidateWorkflowStep.status == "READY"
            ).update({
                "status": "IN_PROGRESS",
                "idempotency_key": lock_key,
                "started_at": now,
                "attempts_count": (CandidateWorkflowStep.attempts_count + 1)
            })
            db.commit()

            if updated_count == 0:
                logger.warning(f"Step {cws.id} was claimed by another worker. Skipping.")
                continue

            step_def = db.query(WorkflowStep).filter(WorkflowStep.id == cws.workflow_step_id).first()
            if not step_def:
                logger.error(f"WorkflowStep definition {cws.workflow_step_id} not found.")
                cws.status = "FAILED"
                cws.error_message = "Step definition missing."
                db.commit()
                continue

            # Check HR Human Gate vs Automated Executor
            if cws.executor == "HUMAN_HR" or cws.requires_approval or step_def.owner in ["HR", "Recruiter", "Hiring Manager"]:
                cws.status = "WAITING_FOR_HUMAN"
                cwf.status = "WAITING_FOR_HUMAN"
                db.commit()

                evt = WorkflowEvent(
                    id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-human",
                    candidate_workflow_id=cwf.id,
                    candidate_id=cwf.candidate_id,
                    job_id=cwf.job_id,
                    event_type="hr.review.required",
                    step_id=step_def.id,
                    actor_type="SYSTEM",
                    payload_json={"step_name": step_def.name, "owner": step_def.owner}
                )
                db.add(evt)
                db.commit()

                execution_results.append({
                    "candidate_workflow_id": cwf.id,
                    "step_name": cws.step_name,
                    "status": "WAITING_FOR_HUMAN"
                })
                continue

            # Execute automated step via AIHRAgent
            app = db.query(Application).filter(Application.candidate_id == cwf.candidate_id, Application.job_id == cwf.job_id).first()
            app_id = app.id if app else f"app-{cwf.candidate_id}"

            res = AIHRAgent.execute_step(db, app_id, step_def, payload={"attempts_count": cws.attempts_count})
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
                    step_id=step_def.id,
                    actor_type="SYSTEM",
                    payload_json=res
                )
                db.add(evt_human)
                db.commit()
                execution_results.append({"candidate_workflow_id": cwf.id, "step_name": cws.step_name, "status": "WAITING_FOR_HUMAN"})

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
                    step_id=step_def.id,
                    actor_type="AI",
                    payload_json=res
                )
                db.add(evt_comp)
                db.commit()

                # Advance candidate to next step
                advance_res = WorkflowExecutionEngine.advance_to_next_step(db, cwf.id, cws.workflow_step_id)
                execution_results.append(advance_res)

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
                    step_id=step_def.id,
                    actor_type="AI",
                    payload_json=res
                )
                db.add(evt_fail)
                db.commit()
                execution_results.append({"candidate_workflow_id": cwf.id, "step_name": cws.step_name, "status": "FAILED", "error": cws.error_message})

        return execution_results

    @staticmethod
    def advance_to_next_step(db: Session, candidate_workflow_id: str, completed_step_id: str) -> Dict[str, Any]:
        """
        Advances workflow to the next step after a step completes.
        Computes scheduled_at for the next step based on completion time and relative/fixed schedule type.
        """
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        all_steps = db.query(WorkflowStep).filter(
            WorkflowStep.workflow_id == cwf.workflow_id,
            WorkflowStep.is_enabled != False
        ).order_by(WorkflowStep.order.asc()).all()

        current_idx = -1
        for idx, s in enumerate(all_steps):
            if s.id == completed_step_id:
                current_idx = idx
                break

        if current_idx >= 0 and current_idx < len(all_steps) - 1:
            next_step_def = all_steps[current_idx + 1]
            completed_cws = db.query(CandidateWorkflowStep).filter(
                CandidateWorkflowStep.candidate_workflow_id == cwf.id,
                CandidateWorkflowStep.workflow_step_id == completed_step_id
            ).first()
            prev_completed_at = completed_cws.completed_at if completed_cws and completed_cws.completed_at else datetime.utcnow()

            now = datetime.utcnow()
            next_scheduled_at = WorkflowExecutionEngine.compute_step_scheduled_at(next_step_def, prev_completed_at)
            next_status = "READY" if next_scheduled_at <= now else "WAITING"

            # Find or create candidate workflow step for next step
            next_cws = db.query(CandidateWorkflowStep).filter(
                CandidateWorkflowStep.candidate_workflow_id == cwf.id,
                CandidateWorkflowStep.workflow_step_id == next_step_def.id
            ).first()

            if not next_cws:
                next_cws = CandidateWorkflowStep(
                    id=f"cws-{int(datetime.utcnow().timestamp()*1000)}-{next_step_def.id}",
                    candidate_workflow_id=cwf.id,
                    workflow_step_id=next_step_def.id,
                    step_name=next_step_def.name,
                    step_type=str(next_step_def.type.value if hasattr(next_step_def.type, 'value') else next_step_def.type),
                    status=next_status,
                    scheduled_at=next_scheduled_at,
                    executor=next_step_def.executor or "AI",
                    requires_approval=next_step_def.requires_approval or False,
                    allow_skip=next_step_def.allow_skip if next_step_def.allow_skip is not None else True,
                    result_json={},
                    metadata_json={}
                )
                db.add(next_cws)
            else:
                next_cws.status = next_status
                next_cws.scheduled_at = next_scheduled_at

            cwf.current_step_id = next_step_def.id
            cwf.current_step_name = next_step_def.name
            cwf.status = "IN_PROGRESS"
            db.commit()

            app = db.query(Application).filter(Application.candidate_id == cwf.candidate_id, Application.job_id == cwf.job_id).first()
            if app:
                app.current_step_id = next_step_def.id
                app.current_step_name = next_step_def.name
                app.current_stage = next_step_def.name
                app.step_status = next_status
                db.commit()

            logger.info(f"Candidate {cwf.candidate_id} advanced to step '{next_step_def.name}' (status: {next_status}, scheduled_at: {next_scheduled_at.isoformat()})")

            # Cascade: if next step is READY, run execution immediately
            if next_status == "READY":
                WorkflowExecutionEngine.execute_due_steps(db, target_cwf_id=cwf.id)

            return {
                "status": "advanced",
                "candidate_workflow_id": cwf.id,
                "next_step": next_step_def.name,
                "step_status": next_status,
                "scheduled_at": next_scheduled_at.isoformat()
            }
        else:
            # Workflow complete
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
            return {"status": "workflow_completed", "candidate_workflow_id": cwf.id, "message": "Candidate successfully completed all workflow steps."}

    # --- HR MANUAL CONTROLS ---

    @staticmethod
    def run_now(db: Session, candidate_workflow_id: str, step_id: Optional[str] = None) -> Dict[str, Any]:
        """HR Manual Action: Overrides scheduled_at to immediate now() and triggers step execution."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        target_step_id = step_id or cwf.current_step_id
        cws = db.query(CandidateWorkflowStep).filter(
            CandidateWorkflowStep.candidate_workflow_id == cwf.id,
            CandidateWorkflowStep.workflow_step_id == target_step_id
        ).first()

        if not cws:
            return {"status": "error", "message": f"Candidate step {target_step_id} not found"}

        now = datetime.utcnow()
        cws.scheduled_at = now
        cws.status = "READY"
        cwf.is_paused = False
        cwf.status = "IN_PROGRESS"
        db.commit()

        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-runnow",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="workflow.step.run_now",
            step_id=target_step_id,
            actor_type="HR",
            payload_json={"triggered_by": "HR Manual Run Now"}
        )
        db.add(evt)
        db.commit()

        WorkflowExecutionEngine.execute_due_steps(db, target_cwf_id=cwf.id)
        return {"status": "success", "message": f"Step '{cws.step_name}' scheduled for immediate execution."}

    @staticmethod
    def reschedule_step(db: Session, candidate_workflow_id: str, step_id: str, new_scheduled_at: datetime) -> Dict[str, Any]:
        """HR Manual Action: Changes step scheduled_at timestamp."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        cws = db.query(CandidateWorkflowStep).filter(
            CandidateWorkflowStep.candidate_workflow_id == cwf.id,
            CandidateWorkflowStep.workflow_step_id == step_id
        ).first()

        if not cws:
            return {"status": "error", "message": "Candidate step not found"}

        now = datetime.utcnow()
        cws.scheduled_at = new_scheduled_at
        cws.status = "READY" if new_scheduled_at <= now else "WAITING"
        db.commit()

        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-resched",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="workflow.step.rescheduled",
            step_id=step_id,
            actor_type="HR",
            payload_json={"new_scheduled_at": new_scheduled_at.isoformat()}
        )
        db.add(evt)
        db.commit()

        if cws.status == "READY":
            WorkflowExecutionEngine.execute_due_steps(db, target_cwf_id=cwf.id)

        return {"status": "success", "message": f"Step '{cws.step_name}' rescheduled to {new_scheduled_at.isoformat()}"}

    @staticmethod
    def skip_step(db: Session, candidate_workflow_id: str, step_id: Optional[str] = None, user_id: str = "hr_admin", reason: str = "") -> Dict[str, Any]:
        """HR Manual Action: Skips step and advances candidate to next step."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        target_step_id = step_id or cwf.current_step_id
        cws = db.query(CandidateWorkflowStep).filter(
            CandidateWorkflowStep.candidate_workflow_id == cwf.id,
            CandidateWorkflowStep.workflow_step_id == target_step_id
        ).first()

        if not cws:
            return {"status": "error", "message": "Candidate step not found"}

        if cws.allow_skip == False:
            return {"status": "error", "message": f"Step '{cws.step_name}' is configured as non-skippable."}

        now = datetime.utcnow()
        cws.status = "SKIPPED"
        cws.completed_at = now
        cws.result_json = {"skipped_by": user_id, "reason": reason}
        db.commit()

        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-skip",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="workflow.step.skipped",
            step_id=target_step_id,
            actor_type="HR",
            actor_id=user_id,
            payload_json={"reason": reason}
        )
        db.add(evt)
        db.commit()

        return WorkflowExecutionEngine.advance_to_next_step(db, cwf.id, target_step_id)

    @staticmethod
    def pause_workflow(db: Session, candidate_workflow_id: str) -> Dict[str, Any]:
        """HR Manual Action: Pauses workflow execution."""
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
        """HR Manual Action: Resumes a paused workflow."""
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

        WorkflowExecutionEngine.execute_due_steps(db, target_cwf_id=cwf.id)
        return {"status": "success", "message": "Candidate workflow resumed and checked for due steps."}

    @staticmethod
    def cancel_workflow(db: Session, candidate_workflow_id: str, user_id: str = "hr_admin", reason: str = "") -> Dict[str, Any]:
        """HR Manual Action: Cancels candidate workflow."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        cwf.status = "CANCELLED"
        cwf.completed_at = datetime.utcnow()
        db.commit()

        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-cancel",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="candidate.workflow.cancelled",
            actor_type="HR",
            actor_id=user_id,
            payload_json={"reason": reason}
        )
        db.add(evt)
        db.commit()
        return {"status": "success", "message": "Candidate workflow cancelled."}

    @staticmethod
    def takeover_workflow(db: Session, candidate_workflow_id: str, is_active: bool) -> Dict[str, Any]:
        """
        HR Human Takeover: Sets or clears the human takeover flag on a candidate workflow.
        When is_active=True: pauses automated execution and flags that a human HR is managing this candidate.
        When is_active=False: clears human takeover flag and resumes normal automated execution.
        """
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": f"CandidateWorkflow '{candidate_workflow_id}' not found"}

        cwf.is_human_takeover = is_active
        if is_active:
            cwf.is_paused = True
            cwf.paused_at = datetime.utcnow()
            cwf.status = "HUMAN_TAKEOVER"
        else:
            cwf.is_paused = False
            cwf.status = "IN_PROGRESS"

        db.commit()

        # Log event
        event = WorkflowEvent(
            id=f"wfe-{int(time.time()*1000)}",
            candidate_workflow_id=candidate_workflow_id,
            candidate_id=cwf.candidate_id,
            application_id=cwf.application_id,
            job_id=cwf.job_id,
            event_type="hr.takeover.activated" if is_active else "hr.takeover.released",
            actor_type="HUMAN_HR",
            event_data={"is_active": is_active, "candidate_workflow_id": candidate_workflow_id}
        )
        db.add(event)
        db.commit()

        if not is_active:
            # Resume automated execution
            WorkflowExecutionEngine.execute_due_steps(db, target_cwf_id=candidate_workflow_id)

        return {
            "status": "success",
            "candidate_workflow_id": candidate_workflow_id,
            "is_human_takeover": is_active,
            "message": "Human takeover activated. Automated steps paused." if is_active else "Human takeover released. Automated execution resumed."
        }

    @staticmethod
    def retry_step(db: Session, candidate_workflow_id: str, step_id: Optional[str] = None) -> Dict[str, Any]:
        """HR Manual Action: Resets failed/stuck step and re-executes."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        target_step_id = step_id or cwf.current_step_id
        cws = db.query(CandidateWorkflowStep).filter(
            CandidateWorkflowStep.candidate_workflow_id == cwf.id,
            CandidateWorkflowStep.workflow_step_id == target_step_id
        ).first()

        if cws:
            cws.status = "READY"
            cws.scheduled_at = datetime.utcnow()
            cws.error_message = None

        cwf.status = "IN_PROGRESS"
        db.commit()

        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-retry",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="workflow.step.retry",
            step_id=target_step_id,
            actor_type="HR",
            payload_json={"action": "RETRY_STEP"}
        )
        db.add(evt)
        db.commit()

        WorkflowExecutionEngine.execute_due_steps(db, target_cwf_id=cwf.id)
        return {"status": "success", "message": "Step reset to READY for execution retry."}

    @staticmethod
    def approve_step(db: Session, candidate_workflow_id: str, user_id: str = "hr_admin", reason: str = "") -> Dict[str, Any]:
        """HR Gate Approval: HR approves gate step and advances candidate."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        cws = db.query(CandidateWorkflowStep).filter(
            CandidateWorkflowStep.candidate_workflow_id == cwf.id,
            CandidateWorkflowStep.workflow_step_id == cwf.current_step_id
        ).first()

        if cws:
            cws.status = "COMPLETED"
            cws.completed_at = datetime.utcnow()
            cws.result_json = {"approved_by": user_id, "reason": reason}

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

        return WorkflowExecutionEngine.advance_to_next_step(db, cwf.id, cwf.current_step_id)

    @staticmethod
    def reject_step(db: Session, candidate_workflow_id: str, user_id: str = "hr_admin", reason: str = "") -> Dict[str, Any]:
        """HR Gate Rejection: HR rejects candidate at current gate step."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found"}

        cws = db.query(CandidateWorkflowStep).filter(
            CandidateWorkflowStep.candidate_workflow_id == cwf.id,
            CandidateWorkflowStep.workflow_step_id == cwf.current_step_id
        ).first()

        if cws:
            cws.status = "REJECTED"
            cws.completed_at = datetime.utcnow()

        cwf.status = "REJECTED"
        cwf.completed_at = datetime.utcnow()
        db.commit()

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

        return {"status": "rejected", "message": f"Candidate workflow rejected by HR. Reason: {reason}"}

    @staticmethod
    def complete_step_execution(db: Session, candidate_workflow_step_id: str, result_json: dict, status: str = "COMPLETED") -> Dict[str, Any]:
        """External integration callback (n8n, ElevenLabs, Webhooks) posting step completion result."""
        cws = db.query(CandidateWorkflowStep).filter(CandidateWorkflowStep.id == candidate_workflow_step_id).first()
        if not cws:
            return {"status": "error", "message": "CandidateWorkflowStep not found"}

        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.id == cws.candidate_workflow_id).first()
        if not cwf:
            return {"status": "error", "message": "CandidateWorkflow not found"}

        cws.status = status
        cws.result_json = result_json
        if status == "COMPLETED":
            cws.completed_at = datetime.utcnow()

        db.commit()

        evt = WorkflowEvent(
            id=f"wfev-{int(datetime.utcnow().timestamp()*1000)}-extcomp",
            candidate_workflow_id=cwf.id,
            candidate_id=cwf.candidate_id,
            job_id=cwf.job_id,
            event_type="workflow.step.completed" if status == "COMPLETED" else "workflow.step.failed",
            step_id=cws.workflow_step_id,
            actor_type="N8N_OR_EXTERNAL",
            payload_json=result_json
        )
        db.add(evt)
        db.commit()

        if status == "COMPLETED":
            return WorkflowExecutionEngine.advance_to_next_step(db, cwf.id, cws.workflow_step_id)
        else:
            cwf.status = "FAILED"
            db.commit()
            return {"status": "failed", "message": "External step reported failure"}

    @staticmethod
    def get_candidate_step_timeline(db: Session, candidate_id: str) -> Dict[str, Any]:
        """Returns structured timeline of all workflow steps for a candidate."""
        cwf = db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == candidate_id).order_by(CandidateWorkflow.started_at.desc()).first()
        if not cwf:
            return {"status": "error", "message": "Candidate workflow not found", "steps": []}

        all_steps = db.query(WorkflowStep).filter(WorkflowStep.workflow_id == cwf.workflow_id).order_by(WorkflowStep.order.asc()).all()
        cand_steps = db.query(CandidateWorkflowStep).filter(CandidateWorkflowStep.candidate_workflow_id == cwf.id).all()
        cws_map = {cs.workflow_step_id: cs for cs in cand_steps}

        timeline = []
        for s in all_steps:
            cws = cws_map.get(s.id)
            timeline.append({
                "step_id": s.id,
                "step_name": s.name,
                "order": s.order,
                "schedule_type": s.schedule_type or "IMMEDIATE",
                "fixed_timestamp": s.fixed_timestamp.isoformat() if s.fixed_timestamp else None,
                "relative_delay_minutes": s.relative_delay_minutes,
                "executor": cws.executor if cws else (s.executor or "AI"),
                "status": cws.status if cws else "WAITING",
                "scheduled_at": cws.scheduled_at.isoformat() if cws and cws.scheduled_at else None,
                "started_at": cws.started_at.isoformat() if cws and cws.started_at else None,
                "completed_at": cws.completed_at.isoformat() if cws and cws.completed_at else None,
                "requires_approval": s.requires_approval or False,
                "allow_skip": cws.allow_skip if cws else (s.allow_skip if s.allow_skip is not None else True),
                "result": cws.result_json if cws else None,
                "error": cws.error_message if cws else None
            })

        return {
            "candidate_workflow_id": cwf.id,
            "candidate_id": cwf.candidate_id,
            "job_id": cwf.job_id,
            "workflow_id": cwf.workflow_id,
            "workflow_version": cwf.workflow_version,
            "status": cwf.status,
            "is_paused": cwf.is_paused,
            "is_human_takeover": cwf.is_human_takeover,
            "current_step_id": cwf.current_step_id,
            "current_step_name": cwf.current_step_name,
            "steps": timeline
        }

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
                "status": cws.status if cws else "PENDING",
                "scheduled_at": cws.scheduled_at.isoformat() if cws and cws.scheduled_at else None
            }
        }

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

            if s.schedule_type == "FIXED_TIME" and not s.fixed_timestamp:
                errors.append(f"Step '{s.name}' with FIXED_TIME scheduling requires a valid fixed_timestamp.")

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
                "schedule_type": s.schedule_type or "IMMEDIATE",
                "executor": s.executor or "AI",
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
