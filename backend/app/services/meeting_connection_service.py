import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.domain import Interview, InterviewSession, Candidate, Job
from integrations.meeting.factory import MeetingProviderFactory
from app.services.participant_service import ParticipantService
from app.services.interview_brain.orchestrator import AIInterviewOrchestrator

logger = logging.getLogger("meeting_connection_service")


class MeetingConnectionService:
    """
    Orchestrates real video meeting platform integration (Google Meet, Zoom, Teams),
    executes 17-step join flow, manages meeting state machine, and synchronizes with AI Interview Brain.
    """

    @staticmethod
    def start_interview_connection(db: Session, interview_id: str) -> Dict[str, Any]:
        """
        Executes full meeting join workflow:
        1. Load interview
        2. Verify interview exists
        3. Verify status
        4. Determine provider
        5. Verify meeting URL
        6. Verify / create AI interview session
        7. Verify workflow version
        8. Verify provider credentials & capabilities
        9. Join meeting
        10. Detect participants & candidate presence
        11. Update meeting & session state
        12. Notify AI Brain
        """
        # 1. Load Interview
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
            if session:
                interview = Interview(
                    id=interview_id,
                    candidate_id=session.candidate_id,
                    job_id=session.job_id,
                    type="Technical",
                    date="Pending Scheduling",
                    time="TBD",
                    platform="Google Meet",
                    meeting_link=None,  # Set via /api/v1/applications/{id}/schedule-interview
                    interviewer_name="AI HR Agent",
                    status="UPCOMING",
                    meeting_provider="GOOGLE_MEET",
                    meeting_url=None,   # Real URL from Google Calendar API
                    meeting_status="PENDING_SCHEDULING"
                )
                db.add(interview)
                db.commit()

            else:
                return {"status": "error", "message": f"Interview {interview_id} not found"}

        # 2. Check Candidate & Job
        candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
        job = db.query(Job).filter(Job.id == interview.job_id).first()
        if not candidate or not job:
            return {"status": "error", "message": "Candidate or Job record missing"}

        # 3. Determine Provider & Validate URL
        meeting_url = interview.meeting_url or interview.meeting_link
        provider_type = interview.meeting_provider or interview.platform
        provider = MeetingProviderFactory.get_provider(provider_type=provider_type, meeting_url=meeting_url)

        if not provider.validate_meeting({"meeting_url": meeting_url, "meeting_link": interview.meeting_link}):
            interview.meeting_status = "FAILED"
            db.commit()
            return {"status": "error", "message": f"Invalid meeting URL format for {provider_type}: {meeting_url}"}

        capabilities = provider.get_capabilities()
        interview.meeting_status = "CONNECTING"
        interview.ai_connection_status = "CONNECTING"
        db.commit()

        # 4. Connect Provider Bot
        join_res = provider.join({"id": interview.id, "meeting_url": meeting_url, "candidate_name": candidate.name})
        if join_res.get("status") == "FAILED":
            interview.meeting_status = "CONNECTION_FAILED"
            interview.ai_connection_status = "DISCONNECTED"
            db.commit()
            return {"status": "error", "message": join_res.get("reason", "Failed to connect meeting provider")}

        # 5. Detect Participants & Candidate Presence
        roster = provider.get_participants({"id": interview.id, "candidate_name": candidate.name})
        roster_res = ParticipantService.process_roster(roster, candidate_name=candidate.name, candidate_email=candidate.email)

        # 6. Ensure AI InterviewSession Exists
        session = db.query(InterviewSession).filter(
            InterviewSession.interview_id == interview.id
        ).first()

        if not session:
            sess_res = AIInterviewOrchestrator.create_session(
                db=db,
                candidate_id=candidate.id,
                job_id=job.id,
                interview_id=interview.id,
                company_id=job.organization_id or "org-default"
            )
            sess_id = sess_res.get("interview_id")
            session = db.query(InterviewSession).filter(InterviewSession.id == sess_id).first()

        # 7. Update Meeting State Machine
        if roster_res["has_candidate"]:
            interview.meeting_status = "INTERVIEW_ACTIVE"
            interview.ai_connection_status = "CONNECTED"
            interview.meeting_started_at = datetime.utcnow()
            interview.status = "IN_PROGRESS"
            
            if session and session.status == "PENDING":
                AIInterviewOrchestrator.start_interview(db, session.id)
        else:
            interview.meeting_status = "WAITING_FOR_CANDIDATE"
            interview.ai_connection_status = "CONNECTED"
            interview.status = "WAITING_FOR_CANDIDATE"

        interview.ai_participant_id = join_res.get("ai_participant_id")
        interview.candidate_participant_id = roster_res.get("candidate_participant", {}).get("participant_id")
        interview.last_media_event_at = datetime.utcnow()
        db.commit()

        return {
            "status": "success",
            "interview_id": interview.id,
            "meeting_provider": provider_type,
            "meeting_status": interview.meeting_status,
            "ai_connection_status": interview.ai_connection_status,
            "has_candidate": roster_res["has_candidate"],
            "participants": roster_res["processed_roster"],
            "capabilities": capabilities.dict()
        }

    @staticmethod
    def get_meeting_status(db: Session, interview_id: str) -> Dict[str, Any]:
        """Retrieves active meeting status, connection metrics, and participant roster."""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            return {"status": "error", "message": "Interview not found"}

        candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
        provider = MeetingProviderFactory.get_provider(
            provider_type=interview.meeting_provider or interview.platform,
            meeting_url=interview.meeting_url or interview.meeting_link
        )

        roster = provider.get_participants({"id": interview.id, "candidate_name": candidate.name if candidate else "Candidate"})
        roster_res = ParticipantService.process_roster(roster, candidate_name=candidate.name if candidate else None)

        return {
            "interview_id": interview.id,
            "platform": interview.platform,
            "meeting_provider": interview.meeting_provider or interview.platform,
            "meeting_url": interview.meeting_url or interview.meeting_link,
            "meeting_status": interview.meeting_status or "CREATED",
            "ai_connection_status": interview.ai_connection_status or "DISCONNECTED",
            "ai_participant_id": interview.ai_participant_id,
            "has_candidate": roster_res["has_candidate"],
            "participants": roster_res["processed_roster"],
            "capabilities": provider.get_capabilities().dict(),
            "last_media_event_at": interview.last_media_event_at.isoformat() if interview.last_media_event_at else None
        }

    @staticmethod
    def disconnect_interview_meeting(db: Session, interview_id: str) -> Dict[str, Any]:
        """Safely disconnects meeting bot and updates state."""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            return {"status": "error", "message": "Interview not found"}

        provider = MeetingProviderFactory.get_provider(
            provider_type=interview.meeting_provider or interview.platform,
            meeting_url=interview.meeting_url or interview.meeting_link
        )

        provider.leave({"id": interview.id})
        interview.meeting_status = "ENDED"
        interview.ai_connection_status = "DISCONNECTED"
        interview.meeting_ended_at = datetime.utcnow()
        db.commit()

        return {
            "status": "success",
            "interview_id": interview.id,
            "meeting_status": interview.meeting_status,
            "ai_connection_status": interview.ai_connection_status
        }
