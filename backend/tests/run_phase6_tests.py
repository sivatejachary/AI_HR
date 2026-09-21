import sys
import os
import unittest
from datetime import datetime

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal, init_db
from app.models.domain import (
    HiringWorkflow, WorkflowStep, HiringWorkflowVersion,
    CandidateWorkflow, CandidateWorkflowStep, WorkflowEvent,
    Candidate, Job, Application, StepType
)
from app.services.workflow.workflow_execution_engine import WorkflowExecutionEngine
from app.services.workflow.ai_hr_agent import AIHRAgent

class TestPhase6HiringWorkflowExecutionEngine(unittest.TestCase):

    def setUp(self):
        init_db()
        self.db = SessionLocal()

        # Clean up existing test data if any
        self.tearDown()

        # Create test records
        self.candidate = Candidate(
            id="cand-wf-101",
            organization_id="org-default",
            name="Alexander Wright",
            email="alex@example.com",
            phone="+14155552671",
            location="San Francisco, CA",
            years_experience=6.0,
            skills=["Python", "FastAPI", "Distributed Systems"]
        )
        self.job = Job(
            id="job-wf-202",
            organization_id="org-default",
            workflow_id="wf-test-phase6",
            title="Lead AI Systems Architect",
            department="Engineering",
            employment_type="Full-time",
            location="Remote",
            description="Build scalable AI hiring workflows.",
            responsibilities="Design distributed workflow engines.",
            requirements="Python, System Design, Distributed Systems",
            created_by="user-1"
        )
        self.workflow = HiringWorkflow(
            id="wf-test-phase6",
            organization_id="org-default",
            job_id="job-wf-202",
            name="AI Engineer Executable Hiring Lifecycle",
            version=1,
            status="Draft",
            is_active=True
        )

        self.step1 = WorkflowStep(
            id="step-101",
            workflow_id="wf-test-phase6",
            name="Automated Resume Screening",
            category="Screening",
            type=StepType.AI_ACTION,
            order=1,
            owner="AI",
            automation="Fully automated",
            is_enabled=True
        )
        self.step2 = WorkflowStep(
            id="step-102",
            workflow_id="wf-test-phase6",
            name="AI HR Screening Call",
            category="Communication",
            type=StepType.VOICE_CALL,
            order=2,
            owner="AI",
            automation="Fully automated",
            is_enabled=True
        )
        self.step3 = WorkflowStep(
            id="step-103",
            workflow_id="wf-test-phase6",
            name="Technical AI Interview",
            category="Interview",
            type=StepType.INTERVIEW,
            order=3,
            owner="AI",
            automation="AI-assisted",
            duration_minutes=45,
            is_enabled=True
        )
        self.step4 = WorkflowStep(
            id="step-104",
            workflow_id="wf-test-phase6",
            name="Hiring Manager Review Gate",
            category="Decision",
            type=StepType.APPROVAL,
            order=4,
            owner="Hiring Manager",
            automation="Manual",
            is_enabled=True
        )

        self.db.add(self.candidate)
        self.db.add(self.job)
        self.db.add(self.workflow)
        self.db.add(self.step1)
        self.db.add(self.step2)
        self.db.add(self.step3)
        self.db.add(self.step4)
        self.db.commit()

    def tearDown(self):
        try:
            self.db.query(WorkflowEvent).filter(WorkflowEvent.job_id == "job-wf-202").delete()
            self.db.query(CandidateWorkflowStep).delete()
            self.db.query(CandidateWorkflow).filter(CandidateWorkflow.job_id == "job-wf-202").delete()
            self.db.query(HiringWorkflowVersion).filter(HiringWorkflowVersion.workflow_id == "wf-test-phase6").delete()
            self.db.query(WorkflowStep).filter(WorkflowStep.workflow_id == "wf-test-phase6").delete()
            self.db.query(HiringWorkflow).filter(HiringWorkflow.id == "wf-test-phase6").delete()
            self.db.query(Job).filter(Job.id == "job-wf-202").delete()
            self.db.query(Candidate).filter(Candidate.id == "cand-wf-101").delete()
            self.db.commit()
        except Exception:
            self.db.rollback()
        finally:
            self.db.close()

    def test_workflow_validation_and_publishing(self):
        """1. Verify workflow validation rules and publishing versioning."""
        # Validation
        val_res = WorkflowExecutionEngine.validate_workflow(self.db, "wf-test-phase6")
        self.assertTrue(val_res["is_valid"])
        self.assertEqual(val_res["step_count"], 4)

        # Publish v1 -> v2
        pub_res = WorkflowExecutionEngine.publish_workflow(self.db, "wf-test-phase6")
        self.assertEqual(pub_res["status"], "success")
        self.assertEqual(pub_res["version"], 1)

    def test_candidate_workflow_start_and_version_lock(self):
        """2. Verify candidate workflow initialization and version lock-in."""
        WorkflowExecutionEngine.publish_workflow(self.db, "wf-test-phase6")
        
        start_res = WorkflowExecutionEngine.start_workflow(self.db, "cand-wf-101", "job-wf-202")
        self.assertIn(start_res["status"].upper(), ["COMPLETED", "WORKFLOW_COMPLETED", "WAITING_FOR_HUMAN", "IN_PROGRESS", "RUNNING"])

        # Check candidate workflow record
        cwf = self.db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == "cand-wf-101").first()
        self.assertIsNotNone(cwf)
        self.assertEqual(cwf.workflow_version, 1)

        # Publish v2
        WorkflowExecutionEngine.publish_workflow(self.db, "wf-test-phase6")

        # Existing candidate must stay locked on v1!
        cwf_refreshed = self.db.query(CandidateWorkflow).filter(CandidateWorkflow.id == cwf.id).first()
        self.assertEqual(cwf_refreshed.workflow_version, 1)

    def test_human_approval_gate_and_hr_action(self):
        """3. Verify AI Agent stops at Human Approval Gates and HR can approve/advance."""
        WorkflowExecutionEngine.publish_workflow(self.db, "wf-test-phase6")
        start_res = WorkflowExecutionEngine.start_workflow(self.db, "cand-wf-101", "job-wf-202")
        cwf = self.db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == "cand-wf-101").first()

        # Jump current step directly to step 4 (Hiring Manager Review Gate)
        cwf.current_step_id = "step-104"
        cwf.current_step_name = "Hiring Manager Review Gate"
        self.db.commit()

        exec_res = WorkflowExecutionEngine.execute_current_step(self.db, cwf.id)
        self.assertEqual(exec_res["status"], "waiting_for_human")

        # HR Approves
        app_res = WorkflowExecutionEngine.approve_step(self.db, cwf.id, user_id="manager_1", reason="Strong candidate fit.")
        self.assertEqual(app_res["status"], "workflow_completed")

    def test_workflow_pause_resume_and_takeover(self):
        """4. Verify workflow pause/resume and HR takeover toggles."""
        WorkflowExecutionEngine.publish_workflow(self.db, "wf-test-phase6")
        WorkflowExecutionEngine.start_workflow(self.db, "cand-wf-101", "job-wf-202")
        cwf = self.db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == "cand-wf-101").first()

        # Pause
        p_res = WorkflowExecutionEngine.pause_workflow(self.db, cwf.id)
        self.assertEqual(p_res["status"], "success")

        e_res = WorkflowExecutionEngine.execute_current_step(self.db, cwf.id)
        self.assertEqual(e_res["status"], "paused")

        # Resume
        r_res = WorkflowExecutionEngine.resume_workflow(self.db, cwf.id)
        self.assertNotEqual(r_res["status"], "error")

        # HR Takeover
        t_res = WorkflowExecutionEngine.takeover_workflow(self.db, cwf.id, is_active=True)
        self.assertTrue(t_res["is_human_takeover"])

    def test_workflow_simulation_mode_and_analytics(self):
        """5. Verify dry-run simulation mode and workflow analytics calculation."""
        sim_res = WorkflowExecutionEngine.simulate_workflow(self.db, "wf-test-phase6")
        self.assertEqual(sim_res["status"], "success")
        self.assertEqual(len(sim_res["simulated_trace"]), 4)

        analytics = WorkflowExecutionEngine.get_workflow_analytics(self.db, "wf-test-phase6")
        self.assertEqual(analytics["workflow_id"], "wf-test-phase6")
        self.assertIn("total_candidates_entered", analytics)

if __name__ == "__main__":
    unittest.main()
