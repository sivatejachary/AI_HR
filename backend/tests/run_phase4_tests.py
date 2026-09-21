import sys
import os
import unittest
from datetime import datetime

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal, init_db
from app.models.domain import CodingProblem, CodingSession, InterviewSession, InterviewEvent, InterviewTechnicalEvidence
from integrations.coding.online_compiler import OnlineCodingProvider
from app.services.interview_brain.topic_engine import TechnicalTopicEngine
from app.services.interview_brain.difficulty_engine import DifficultyEngine
from app.services.interview_brain.coding_problem_service import CodingProblemService
from app.services.interview_brain.coding_vision_service import CodingVisionService
from app.services.interview_brain.orchestrator import AIInterviewOrchestrator

class TestPhase4OnlineCodingAndVision(unittest.TestCase):

    def setUp(self):
        init_db()
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_online_coding_provider(self):
        """Test vendor-neutral OnlineCodingProvider abstraction."""
        provider = OnlineCodingProvider(platform_name="Compiler Explorer", base_url="https://godbolt.org")
        url = provider.generate_coding_url(problem_id="prob-two-sum", language="python")
        self.assertIn("godbolt.org", url)
        self.assertIn("python", url)

        sess_meta = provider.create_candidate_session(problem_id="prob-two-sum", candidate_id="cand-123", language="python")
        self.assertEqual(sess_meta["coding_platform"], "Compiler Explorer")
        self.assertEqual(sess_meta["status"], "WAITING_FOR_SCREEN_SHARE")
        self.assertFalse(sess_meta["has_official_api"])

    def test_coding_problem_private_field_isolation(self):
        """Verify candidate payload EXCLUDES reference solutions, internal notes, and scoring rules."""
        service = CodingProblemService(self.db)
        problem = service.select_problem(difficulty="MEDIUM")
        self.assertIsNotNone(problem)

        payload = service.get_public_problem_payload(problem)
        self.assertIn("id", payload)
        self.assertIn("title", payload)
        self.assertIn("description", payload)
        self.assertIn("expected_complexity", payload)
        
        # Verify private internal fields are strictly stripped
        self.assertNotIn("reference_solution", payload)
        self.assertNotIn("private_evaluation_notes", payload)
        self.assertNotIn("internal_scoring_rules", payload)

    def test_vision_observation_processing(self):
        """Verify Vision AI frame analysis and error identification."""
        service = CodingVisionService()
        obs = service.process_screen_observation(
            screen_type="ONLINE_COMPILER",
            language="PYTHON",
            code_visible=True,
            error_visible=True,
            visible_error_text="IndexError: list index out of range at line 7"
        )
        self.assertEqual(obs["screen_type"], "ONLINE_COMPILER")
        self.assertTrue(obs["code_visible"])
        self.assertTrue(obs["error_visible"])
        self.assertIn("IndexError", obs["visible_error_text"])

    def test_topic_engine_time_management(self):
        """Test dynamic topic selection and wrap-up triggering when time is low."""
        engine = TechnicalTopicEngine()
        
        # Normal time (> 5 mins)
        res_normal = engine.select_topic(
            job_description="Python FastAPI Senior Developer",
            resume_text="Experienced in Python, SQL, and Docker",
            role="Senior Python Developer",
            remaining_time_minutes=25
        )
        self.assertTrue(res_normal["should_start_coding"])

        # Low time (< 5 mins) -> do NOT start long coding problem
        res_low = engine.select_topic(
            job_description="Python FastAPI Senior Developer",
            resume_text="Experienced in Python",
            role="Senior Python Developer",
            remaining_time_minutes=3
        )
        self.assertFalse(res_low["should_start_coding"])
        self.assertIn("Wrap-Up", res_low["topic"])

    def test_difficulty_engine(self):
        """Test adaptive difficulty transitions."""
        engine = DifficultyEngine()
        diff = engine.adapt_difficulty("MEDIUM", recent_scores=[0.9, 0.95], seniority="Senior")
        self.assertEqual(diff["new_difficulty"], "HARD")
        self.assertIn("Increasing difficulty", diff["reason"])

    def test_extended_stage_order(self):
        """Verify 19-stage pipeline ordering in AIInterviewOrchestrator."""
        stages = AIInterviewOrchestrator.STAGES_ORDER
        self.assertIn("CODING_INTRO", stages)
        self.assertIn("CODING", stages)
        self.assertIn("CODE_REVIEW", stages)
        self.assertIn("DEBUGGING", stages)
        self.assertIn("OPTIMIZATION", stages)
        self.assertIn("TECHNICAL_WRAP_UP", stages)
        self.assertIn("HR_REVIEW", stages)

    def test_experience_engine_bands(self):
        """Verify candidate experience band classification across all 5 bands."""
        from app.services.interview_brain.experience_engine import ExperienceEngine
        
        # Fresher (0 yrs)
        fresher_meta = ExperienceEngine.determine_experience_band(0.0, role_title="Fresher Software Engineer")
        self.assertEqual(fresher_meta["band"], "FRESHER")

        # Junior (1 yr)
        junior_meta = ExperienceEngine.determine_experience_band(1.0, role_title="Junior Developer")
        self.assertEqual(junior_meta["band"], "JUNIOR")

        # Mid-level (3.5 yrs)
        mid_meta = ExperienceEngine.determine_experience_band(3.5, role_title="Backend Developer")
        self.assertEqual(mid_meta["band"], "MID_LEVEL")

        # Senior (6 yrs)
        senior_meta = ExperienceEngine.determine_experience_band(6.0, role_title="Senior Python Engineer")
        self.assertEqual(senior_meta["band"], "SENIOR")

        # Staff (10 yrs)
        staff_meta = ExperienceEngine.determine_experience_band(10.0, role_title="Staff Systems Architect")
        self.assertEqual(staff_meta["band"], "STAFF")

    def test_resume_project_claim_extraction(self):
        """Verify extraction of project claims (e.g. RAG, Kafka, Redis, FastAPI)."""
        from app.services.interview_brain.experience_engine import ExperienceEngine
        resume_text = "Built a high-throughput RAG platform using FastAPI, Qdrant vector database, and Redis distributed caching."
        claims = ExperienceEngine.extract_project_claims(resume_text)
        self.assertTrue(len(claims) >= 3)
        categories = [c["category"] for c in claims]
        self.assertIn("RAG / Vector Search Platform", categories)
        self.assertIn("Web Application & REST API", categories)
        self.assertIn("Distributed Caching Layer", categories)

    def test_experience_aware_question_and_problem_generation(self):
        """Verify question engine adapts style to candidate experience level."""
        from app.services.interview_brain.question_engine import QuestionEngine

        # Test Fresher Question
        fresher_q = QuestionEngine.generate_next_question(
            stage="TECHNICAL_INTERVIEW",
            current_difficulty="EASY",
            job_context={"title": "Graduate Trainee"},
            candidate_context={"name": "Rahul", "experience_years": 0.0, "resume_summary": "College student project"},
            previous_questions=[]
        )
        self.assertEqual(fresher_q["experience_band"], "FRESHER")
        self.assertIn("duplicate", fresher_q["question_text"].lower())

        # Test Staff Question
        staff_q = QuestionEngine.generate_next_question(
            stage="TECHNICAL_INTERVIEW",
            current_difficulty="HARD",
            job_context={"title": "Staff Engineer"},
            candidate_context={"name": "Anita", "experience_years": 10.0, "resume_summary": "Distributed systems architect"},
            previous_questions=[]
        )
        self.assertEqual(staff_q["experience_band"], "STAFF")
        self.assertIn("multi-region", staff_q["question_text"].lower())

        # Test Experience-Aware Coding Problem Selection
        prob_service = CodingProblemService(self.db)
        fresher_prob = prob_service.select_problem(experience_band="FRESHER")
        self.assertEqual(fresher_prob.id, "prob-fresher-dup-prevention")

        staff_prob = prob_service.select_problem(experience_band="STAFF")
        self.assertEqual(staff_prob.id, "prob-staff-multi-region-scheduler")

if __name__ == "__main__":
    unittest.main()

