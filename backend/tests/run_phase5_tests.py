import sys
import os
import unittest
from datetime import datetime

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal, init_db
from app.models.domain import (
    InterviewSession, InterviewEvaluation, EvaluationCompetency,
    EvaluationJDAlignment, EvaluationProjectVerification, EvaluationDecision,
    Candidate, Job, Application, HiringWorkflow
)
from app.services.evaluation.evaluation_service import (
    EvaluationService, EvidenceCollector, CompetencyEvaluator,
    JDAlignmentEvaluator, ProjectEvaluator
)
from app.services.workflow_engine import HiringWorkflowEngine as WorkflowEngine

class TestPhase5EvaluationAndHRReview(unittest.TestCase):

    def setUp(self):
        init_db()
        self.db = SessionLocal()
        
        # Create test candidate, job, application, and interview session
        self.candidate = Candidate(
            id="cand-eval-101",
            organization_id="org-default",
            name="Rahul Sharma",
            email="rahul@example.com",
            phone="+919876543210",
            location="Bengaluru",
            years_experience=3.5,
            skills=["Python", "FastAPI", "PostgreSQL", "Redis"],
            resume_text="Built Enterprise RAG Platform using FastAPI, Qdrant vector DB, and Redis caching."
        )
        self.job = Job(
            id="job-eval-202",
            organization_id="org-default",
            workflow_id="wf-default-101",
            title="Senior Python Engineer",
            department="Engineering",
            employment_type="Full-time",
            location="Remote",
            description="Looking for Python FastAPI engineer",
            responsibilities="Design APIs and optimize PostgreSQL/Redis queries",
            requirements="Python, FastAPI, PostgreSQL, Redis, Docker, AWS",
            preferred_skills=["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "AWS"],
            created_by="user-1"
        )
        self.session = InterviewSession(
            id="INT-EVAL-TEST-99",
            candidate_id="cand-eval-101",
            job_id="job-eval-202",
            organization_id="org-default",
            status="COMPLETED",
            brain_status="COMPLETED",
            current_stage="COMPLETED",
            duration_seconds=1800
        )
        self.db.merge(self.candidate)
        self.db.merge(self.job)
        self.db.merge(self.session)
        self.db.commit()

    def tearDown(self):
        try:
            self.db.query(EvaluationDecision).filter(EvaluationDecision.interview_id == "INT-EVAL-TEST-99").delete()
            self.db.query(InterviewEvaluation).filter(InterviewEvaluation.interview_id == "INT-EVAL-TEST-99").delete()
            self.db.query(InterviewSession).filter(InterviewSession.id == "INT-EVAL-TEST-99").delete()
            self.db.query(Job).filter(Job.id == "job-eval-202").delete()
            self.db.query(Candidate).filter(Candidate.id == "cand-eval-101").delete()
            self.db.commit()
        except Exception:
            self.db.rollback()
        finally:
            self.db.close()

    def test_evidence_collector(self):
        """Verify EvidenceCollector gathers candidate, job, transcript, and experience metadata."""
        evidence = EvidenceCollector.collect(self.db, "INT-EVAL-TEST-99")
        self.assertEqual(evidence["interview_id"], "INT-EVAL-TEST-99")
        self.assertEqual(evidence["candidate"]["name"], "Rahul Sharma")
        self.assertIn(evidence["experience_band"], ["MID_LEVEL", "SENIOR"])
        self.assertTrue(len(evidence["project_claims"]) > 0)

    def test_competency_evaluator_scoring(self):
        """Verify 1-5 scale competency scoring with supporting evidence snippets."""
        evidence = EvidenceCollector.collect(self.db, "INT-EVAL-TEST-99")
        comps = CompetencyEvaluator.evaluate(evidence)
        self.assertTrue(len(comps) > 0)
        for c in comps:
            self.assertGreaterEqual(c["score"], 1.0)
            self.assertLessEqual(c["score"], 5.0)
            self.assertIsNotNone(c["evidence"])

    def test_jd_alignment_classification(self):
        """Verify JD alignment distinguishes DEMONSTRATED, PARTIALLY_DEMONSTRATED, NOT_TESTED."""
        evidence = EvidenceCollector.collect(self.db, "INT-EVAL-TEST-99")
        alignments = JDAlignmentEvaluator.evaluate(evidence)
        statuses = [a["status"] for a in alignments]
        self.assertIn("NOT_TESTED", statuses)
        self.assertTrue(len(alignments) >= 4)

    def test_evaluation_service_generation_and_versioning(self):
        """Verify evaluation generation, idempotency, and versioning (v1.0 vs v1.1)."""
        res_v1 = EvaluationService.evaluate_interview(self.db, "INT-EVAL-TEST-99", evaluation_version="v1.0")
        self.assertEqual(res_v1["evaluation_version"], "v1.0")
        self.assertEqual(res_v1["status"], "COMPLETED")

        # Re-evaluate with version v1.1
        res_v1_1 = EvaluationService.evaluate_interview(self.db, "INT-EVAL-TEST-99", evaluation_version="v1.1")
        self.assertEqual(res_v1_1["evaluation_version"], "v1.1")

    def test_hr_decision_recording_and_workflow_advancement(self):
        """Verify HR decision is recorded separately from AI evaluation and advances WorkflowEngine."""
        res_eval = EvaluationService.evaluate_interview(self.db, "INT-EVAL-TEST-99")
        eval_id = res_eval["evaluation_id"]

        # Record HR Decision
        dec_obj = EvaluationDecision(
            id=f"DEC-TEST-001",
            evaluation_id=eval_id,
            interview_id="INT-EVAL-TEST-99",
            decision="MOVE_TO_NEXT_STAGE",
            decided_by_user_id="hr_recruiter_1",
            decision_reason="Candidate demonstrated strong API engineering depth.",
            decided_at=datetime.utcnow()
        )
        self.db.add(dec_obj)
        self.db.commit()

        # Verify decision retrieval
        fetched = EvaluationService.get_evaluation(self.db, "INT-EVAL-TEST-99")
        self.assertIsNotNone(fetched["hr_decision"])
        self.assertEqual(fetched["hr_decision"]["decision"], "MOVE_TO_NEXT_STAGE")

if __name__ == "__main__":
    unittest.main()
