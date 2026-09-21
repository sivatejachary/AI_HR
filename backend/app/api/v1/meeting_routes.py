import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.domain import Interview, Candidate
from integrations.meeting.factory import MeetingProviderFactory
from app.services.meeting_connection_service import MeetingConnectionService

logger = logging.getLogger("meeting_routes")

router = APIRouter(prefix="/api/interviews", tags=["Real Meeting Platform Integration"])


@router.post("/{interview_id}/meeting/connect")
def connect_meeting_bot(interview_id: str, db: Session = Depends(get_db)):
    """
    POST /api/interviews/{interview_id}/meeting/connect
    Executes 17-step meeting join flow, connects provider bot, verifies candidate presence,
    and initializes AI Interview Session.
    """
    res = MeetingConnectionService.start_interview_connection(db=db, interview_id=interview_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res


@router.post("/{interview_id}/meeting/disconnect")
def disconnect_meeting_bot(interview_id: str, db: Session = Depends(get_db)):
    """
    POST /api/interviews/{interview_id}/meeting/disconnect
    Safely leaves external meeting room and updates meeting status to ENDED.
    """
    res = MeetingConnectionService.disconnect_interview_meeting(db=db, interview_id=interview_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res


@router.get("/{interview_id}/meeting/status")
def get_meeting_status(interview_id: str, db: Session = Depends(get_db)):
    """
    GET /api/interviews/{interview_id}/meeting/status
    Returns active meeting lifecycle status, connection health, and participant roster.
    """
    res = MeetingConnectionService.get_meeting_status(db=db, interview_id=interview_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=404, detail=res.get("message"))
    return res


@router.get("/{interview_id}/meeting/participants")
def get_meeting_participants(interview_id: str, db: Session = Depends(get_db)):
    """
    GET /api/interviews/{interview_id}/meeting/participants
    Returns participant roster with assigned roles (AI, CANDIDATE, HR, OBSERVER, UNKNOWN).
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
    provider = MeetingProviderFactory.get_provider(
        provider_type=interview.meeting_provider or interview.platform,
        meeting_url=interview.meeting_url or interview.meeting_link
    )

    participants = provider.get_participants({"id": interview.id, "candidate_name": candidate.name if candidate else "Candidate"})
    return {
        "interview_id": interview.id,
        "count": len(participants),
        "participants": participants
    }


@router.get("/{interview_id}/meeting/capabilities")
def get_meeting_capabilities(interview_id: str, db: Session = Depends(get_db)):
    """
    GET /api/interviews/{interview_id}/meeting/capabilities
    Returns explicit capability matrix (audioReceive, audioSend, videoReceive, etc.) for interview meeting platform.
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    provider = MeetingProviderFactory.get_provider(
        provider_type=interview.meeting_provider or interview.platform,
        meeting_url=interview.meeting_url or interview.meeting_link
    )

    capabilities = provider.get_capabilities()
    return capabilities.dict()
