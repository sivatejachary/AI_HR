import os
import sys
import unittest
from datetime import datetime

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal, init_db
from app.models.domain import Interview, Candidate, Job, Organization, Integration
from integrations.meeting.factory import MeetingProviderFactory
from integrations.meeting.google_meet import GoogleMeetProvider
from integrations.meeting.zoom import ZoomProvider
from integrations.meeting.teams import TeamsProvider
from app.services.participant_service import ParticipantService, ParticipantRole
from app.services.meeting_connection_service import MeetingConnectionService


class TestMeetingPhase3(unittest.TestCase):

    def setUp(self):
        init_db()
        self.db = SessionLocal()

        # Seed candidate
        cand = self.db.query(Candidate).filter(Candidate.id == "cand-phase3-test").first()
        if not cand:
            cand = Candidate(
                id="cand-phase3-test",
                organization_id="org-default",
                name="Sarah Connor",
                email="sarah.connor@cyberdyne.test",
                phone="+15559876543",
                location="Los Angeles, CA",
                skills=["Python", "FastAPI"],
                years_experience=7.0
            )
            self.db.add(cand)

        # Seed job
        job = self.db.query(Job).filter(Job.id == "job-phase3-test").first()
        if not job:
            job = Job(
                id="job-phase3-test",
                organization_id="org-default",
                workflow_id="wf-default",
                title="Senior Staff Backend Engineer",
                department="Engineering",
                employment_type="Full-time",
                location="Remote",
                description="Backend systems design.",
                responsibilities="API design.",
                requirements="Python, FastAPI",
                created_by="user-hr-admin"
            )
            self.db.add(job)

        # Seed interview
        intv = self.db.query(Interview).filter(Interview.id == "INT-MEET-PHASE3-1001").first()
        if not intv:
            intv = Interview(
                id="INT-MEET-PHASE3-1001",
                candidate_id="cand-phase3-test",
                job_id="job-phase3-test",
                type="Technical",
                date="Today",
                time="10:00 AM",
                platform="Google Meet",
                meeting_link="https://meet.google.com/abc-defg-hij",
                interviewer_name="Sarah Jenkins",
                status="UPCOMING",
                meeting_provider="GOOGLE_MEET",
                meeting_url="https://meet.google.com/abc-defg-hij",
                meeting_status="CREATED"
            )
            self.db.add(intv)

        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_provider_factory(self):
        """Test MeetingProviderFactory instantiates correct providers."""
        gmeet_prov = MeetingProviderFactory.get_provider(meeting_url="https://meet.google.com/abc-defg-hij")
        self.assertIsInstance(gmeet_prov, GoogleMeetProvider)
        self.assertEqual(gmeet_prov.get_capabilities().provider_name, "GOOGLE_MEET")

        zoom_prov = MeetingProviderFactory.get_provider(meeting_url="https://zoom.us/j/123456789")
        self.assertIsInstance(zoom_prov, ZoomProvider)
        self.assertEqual(zoom_prov.get_capabilities().provider_name, "ZOOM")

        teams_prov = MeetingProviderFactory.get_provider(meeting_url="https://teams.microsoft.com/l/meetup-join/123")
        self.assertIsInstance(teams_prov, TeamsProvider)
        self.assertEqual(teams_prov.get_capabilities().provider_name, "TEAMS")

    def test_google_meet_capabilities_and_validation(self):
        """Test GoogleMeetProvider capabilities and URL validation."""
        provider = GoogleMeetProvider()
        caps = provider.get_capabilities()
        self.assertTrue(caps.audioReceive)
        self.assertTrue(caps.audioSend)
        self.assertTrue(caps.videoReceive)
        self.assertTrue(caps.participantEvents)

        self.assertTrue(provider.validate_meeting({"meeting_url": "https://meet.google.com/abc-defg-hij"}))
        self.assertTrue(provider.validate_meeting({"meeting_url": "xyz-pqrs-tuv"}))
        self.assertFalse(provider.validate_meeting({"meeting_url": "https://invalid-url.com"}))

    def test_participant_service_identity(self):
        """Test ParticipantService role identification."""
        role_ai = ParticipantService.identify_role("Teja — Technical Interviewer")
        self.assertEqual(role_ai, ParticipantRole.AI)

        role_cand_email = ParticipantService.identify_role("Sarah C", email="sarah.connor@cyberdyne.test", candidate_email="sarah.connor@cyberdyne.test")
        self.assertEqual(role_cand_email, ParticipantRole.CANDIDATE)

        role_cand_name = ParticipantService.identify_role("Sarah Connor", candidate_name="Sarah Connor")
        self.assertEqual(role_cand_name, ParticipantRole.CANDIDATE)

        role_hr = ParticipantService.identify_role("HR Recruiter")
        self.assertEqual(role_hr, ParticipantRole.HR)

    def test_meeting_connection_service_lifecycle(self):
        """Test MeetingConnectionService join flow and state machine."""
        # 1. Start connection
        res = MeetingConnectionService.start_interview_connection(self.db, "INT-MEET-PHASE3-1001")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["meeting_status"], "INTERVIEW_ACTIVE")
        self.assertEqual(res["ai_connection_status"], "CONNECTED")
        self.assertTrue(res["has_candidate"])

        # 2. Get status
        st = MeetingConnectionService.get_meeting_status(self.db, "INT-MEET-PHASE3-1001")
        self.assertEqual(st["meeting_status"], "INTERVIEW_ACTIVE")
        self.assertIn("capabilities", st)

        # 3. Disconnect
        disc = MeetingConnectionService.disconnect_interview_meeting(self.db, "INT-MEET-PHASE3-1001")
        self.assertEqual(disc["status"], "success")
        self.assertEqual(disc["meeting_status"], "ENDED")
        self.assertEqual(disc["ai_connection_status"], "DISCONNECTED")

        print("\n=== PHASE 3 MEETING INTEGRATION UNIT TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    unittest.main()
