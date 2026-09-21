import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.database import SessionLocal, init_db
from app.models.domain import InterviewSession, Candidate, Job, Organization
from app.services.interview_brain.elevenlabs_service import ElevenLabsIntegrationService

client = TestClient(app)

class TestElevenLabsPhase2(unittest.TestCase):

    def setUp(self):
        init_db()
        db = SessionLocal()
        # Seed org
        org = db.query(Organization).filter(Organization.id == "org-default").first()
        if not org:
            org = Organization(id="org-default", name="Test Acme HR Corp", slug="acme-hr")
            db.add(org)
        
        # Seed Job
        job = db.query(Job).filter(Job.id == "job-test-phase2").first()
        if not job:
            job = Job(
                id="job-test-phase2",
                organization_id="org-default",
                workflow_id="wf-default",
                title="Senior Staff Backend Engineer",
                department="Engineering",
                employment_type="Full-time",
                location="Remote",
                description="Building high-scale distributed APIs.",
                responsibilities="API design, database scaling.",
                requirements="Python, FastAPI, SQL, System Architecture",
                created_by="user-hr-admin"
            )
            db.add(job)

        # Seed Candidate
        candidate = db.query(Candidate).filter(Candidate.id == "cand-test-phase2").first()
        if not candidate:
            candidate = Candidate(
                id="cand-test-phase2",
                organization_id="org-default",
                name="Sarah Connor",
                email="sarah.connor@cyberdyne.test",
                phone="+15559876543",
                location="Los Angeles, CA",
                skills=["Python", "FastAPI", "Distributed Systems", "SQL"],
                years_experience=7.0
            )
            db.add(candidate)
        
        db.commit()
        db.close()

    def test_elevenlabs_auth_validation(self):
        """Test webhook authentication validator."""
        self.assertTrue(ElevenLabsIntegrationService.validate_webhook_auth("Bearer recruitment_pro_elevenlabs_secret_2026"))
        self.assertTrue(ElevenLabsIntegrationService.validate_webhook_auth(token_param="recruitment_pro_elevenlabs_secret_2026"))

    def test_elevenlabs_phase2_full_workflow(self):
        """Tests complete ElevenLabs Webhook tool integration lifecycle."""
        # 1. Start Test Session
        resp = client.post("/api/v1/interviews/ai/start-test-session")
        self.assertEqual(resp.status_code, 200, resp.text)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        interview_id = data["interview_id"]
        self.assertIn("elevenlabs_session", data)

        # 2. Tool 1: GET /api/ai-interview/{interview_id}/context
        resp_ctx = client.get(f"/api/ai-interview/{interview_id}/context")
        self.assertEqual(resp_ctx.status_code, 200)
        ctx_data = resp_ctx.json()
        self.assertEqual(ctx_data["interview_id"], interview_id)
        self.assertEqual(ctx_data["candidate_name"], "Rahul Kumar")
        self.assertEqual(ctx_data["job_title"], "Senior Staff Backend Engineer")

        # 3. Tool 2: GET /api/ai-interview/{interview_id}/stage
        resp_stg = client.get(f"/api/ai-interview/{interview_id}/stage")
        self.assertEqual(resp_stg.status_code, 200)
        stg_data = resp_stg.json()
        self.assertEqual(stg_data["status"], "IN_PROGRESS")
        self.assertIn("difficulty", stg_data)

        # 4. Tool 3: POST /api/ai-interview/{interview_id}/next-question
        resp_q1 = client.post(f"/api/ai-interview/{interview_id}/next-question", json={"reason": "start_stage"})
        self.assertEqual(resp_q1.status_code, 200)
        q1_data = resp_q1.json()
        self.assertIn("question_id", q1_data)
        self.assertGreater(len(q1_data["question"]), 10)
        q1_id = q1_data["question_id"]

        # 5. Tool 4: POST /api/ai-interview/{interview_id}/answer
        answer_payload = {
            "question_id": q1_id,
            "answer": "I have 6 years of experience building Python and FastAPI microservices with PostgreSQL.",
            "conversation_id": "conv_test_12345"
        }
        resp_ans = client.post(f"/api/ai-interview/{interview_id}/answer", json=answer_payload)
        self.assertEqual(resp_ans.status_code, 200)
        ans_data = resp_ans.json()
        self.assertTrue(ans_data["saved"])
        self.assertIn("answer_quality", ans_data)
        self.assertIn("next_action", ans_data)

        # 6. Tool 5: POST /api/ai-interview/{interview_id}/next-action
        resp_act = client.post(f"/api/ai-interview/{interview_id}/next-action")
        self.assertEqual(resp_act.status_code, 200)
        act_data = resp_act.json()
        self.assertIn(act_data["action"], [
            "FOLLOW_UP", "CLARIFY", "NEXT_TOPIC", "INCREASE_DIFFICULTY",
            "DECREASE_DIFFICULTY", "MOVE_TO_NEXT_STAGE", "END_INTERVIEW"
        ])

        # 7. Tool 6: POST /api/ai-interview/{interview_id}/event
        resp_evt = client.post(
            f"/api/ai-interview/{interview_id}/event",
            json={"event_type": "CANDIDATE_SPEAKING", "metadata": {"volume": 0.8}}
        )
        self.assertEqual(resp_evt.status_code, 200)

        # 8. Tool 7: POST /api/ai-interview/{interview_id}/pause
        resp_pause = client.post(f"/api/ai-interview/{interview_id}/pause")
        self.assertEqual(resp_pause.status_code, 200)
        self.assertEqual(resp_pause.json()["status"], "PAUSED")

        # 9. Tool 8: POST /api/ai-interview/{interview_id}/resume
        resp_res = client.post(f"/api/ai-interview/{interview_id}/resume")
        self.assertEqual(resp_res.status_code, 200)
        self.assertEqual(resp_res.json()["status"], "IN_PROGRESS")

        # 10. Tool 9: POST /api/ai-interview/{interview_id}/complete
        resp_comp = client.post(f"/api/ai-interview/{interview_id}/complete")
        self.assertEqual(resp_comp.status_code, 200)
        self.assertEqual(resp_comp.json()["status"], "COMPLETED")

        # 11. Safeguard check: Cannot generate question after completion
        resp_q_fail = client.post(f"/api/ai-interview/{interview_id}/next-question", json={"reason": "after_answer"})
        self.assertEqual(resp_q_fail.status_code, 400)

        # 12. Post-call telemetry webhook
        post_call_payload = {
            "conversation_id": "conv_test_12345",
            "duration": 340,
            "transcript": [
                {"role": "agent", "message": "Hi Rahul, introduce yourself."},
                {"role": "user", "message": "I am a backend developer."}
            ]
        }
        resp_tele = client.post(f"/api/ai-interview/{interview_id}/elevenlabs-post-call", json=post_call_payload)
        self.assertEqual(resp_tele.status_code, 200)
        self.assertEqual(resp_tele.json()["status"], "success")
        print("\n=== ELEVENLABS PHASE 2 ALL UNIT TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    unittest.main()
