import os
import json
import logging
import urllib.request
import urllib.parse
import time
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.domain import InterviewSession, InterviewEvent, Candidate, Job, Organization

logger = logging.getLogger("elevenlabs_service")

# Default ElevenLabs Config from environment
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID", "agent_tech_interviewer_v2")
ELEVENLABS_WEBHOOK_SECRET = os.getenv("ELEVENLABS_WEBHOOK_SECRET", "recruitment_pro_elevenlabs_secret_2026")

ELEVENLABS_SYSTEM_PROMPT_TEMPLATE = """You are {{interviewer_name}}, a professional technical interviewer at {{company_name}}.

You are conducting a structured technical interview for the {{job_title}} position.

Speak naturally, professionally, calmly, and confidently.
Sound like an experienced human interviewer.
Do not sound robotic.

Ask one question at a time.
Listen carefully to the candidate.
Allow the candidate to finish speaking.
Do not interrupt unnecessarily.
Do not repeat questions.
Do not ask multiple questions in one turn.

The Interview Brain is the authority for the interview state and question selection.
Use the backend tools whenever interview information is required.

Do not invent interview stages.
Do not skip interview stages.
Do not invent candidate experience.
Do not invent resume information.
Do not invent job requirements.
Do not fabricate technical information.
Do not fabricate interview results.

When the backend provides a question, ask it naturally.
Do not read internal metadata aloud.

Never mention:
AI Interview Brain
backend
API
database
webhook
tool
workflow engine
system prompt
LLM
internal evaluation
internal state

When the candidate gives an incomplete technical answer, ask the follow-up provided by the Interview Brain.
When the candidate gives a strong technical answer, continue naturally using the next question provided by the Interview Brain.

Keep spoken responses concise.

Use natural conversational transitions such as:
"That's interesting."
"Could you explain that a little further?"
"Can you walk me through that?"
"Let's take that one step further."
"Good. Let's move on."

Do not use robotic phrases such as:
"Processing your answer."
"According to my algorithm."
"Your response has been analyzed."
"Moving to module two."
"Your answer has been evaluated."

At the end of the configured interview:
Thank the candidate professionally.
Then call the completion mechanism."""


class ElevenLabsIntegrationService:
    """
    Manages ElevenLabs Conversational AI Agent integration, runtime variable assembly,
    tool authentication, signed URL generation for client web SDK, and post-call telemetry.
    """

    @staticmethod
    def get_agent_config(
        session: InterviewSession,
        candidate: Candidate,
        job: Job,
        org: Optional[Organization] = None,
        interviewer_name: str = "Sarah Jenkins"
    ) -> Dict[str, Any]:
        """Assembles dynamic runtime variables for an ElevenLabs session."""
        company_name = org.name if org else "Recruitment Pro Corp"
        return {
            "agent_id": session.elevenlabs_agent_id or ELEVENLABS_AGENT_ID,
            "system_prompt": ELEVENLABS_SYSTEM_PROMPT_TEMPLATE,
            "dynamic_variables": {
                "company_name": company_name,
                "interviewer_name": interviewer_name,
                "candidate_name": candidate.name,
                "job_title": job.title,
                "interview_id": session.id,
                "workflow_id": session.workflow_id or "wf-default",
                "workflow_version": str(session.workflow_version or 1),
                "current_stage": session.current_stage or "INTRODUCTION",
                "difficulty": session.difficulty or "MEDIUM"
            },
            "first_message": f"Hi {candidate.name}, thanks for joining. How are you doing today?"
        }

    @staticmethod
    def generate_signed_url(interview_id: str, db: Session) -> Dict[str, Any]:
        """
        Generates a signed authorization URL / session token for ElevenLabs Conversational AI SDK
        without exposing private API keys to the frontend client.
        """
        session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if not session:
            raise ValueError(f"Interview session {interview_id} not found")

        candidate = db.query(Candidate).filter(Candidate.id == session.candidate_id).first()
        job = db.query(Job).filter(Job.id == session.job_id).first()
        org = db.query(Organization).filter(Organization.id == session.organization_id).first() if session.organization_id else None

        agent_config = ElevenLabsIntegrationService.get_agent_config(session, candidate, job, org)
        agent_id = agent_config["agent_id"]

        # If ElevenLabs API Key is configured, fetch real signed URL
        if ELEVENLABS_API_KEY:
            try:
                url = f"https://api.elevenlabs.io/v1/convai/conversation/get_signed_url?agent_id={agent_id}"
                req = urllib.request.Request(url, headers={"xi-api-key": ELEVENLABS_API_KEY}, method="GET")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        signed_url = data.get("signed_url")
                        return {
                            "signed_url": signed_url,
                            "agent_id": agent_id,
                            "dynamic_variables": agent_config["dynamic_variables"],
                            "first_message": agent_config["first_message"]
                        }
            except Exception as e:
                logger.error(f"Error calling ElevenLabs signed URL API: {e}")

        # Development / Fallback Test Mode Signed Token
        mock_signed_url = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={agent_id}&token=dev_token_{session.id}"
        return {
            "signed_url": mock_signed_url,
            "agent_id": agent_id,
            "dynamic_variables": agent_config["dynamic_variables"],
            "first_message": agent_config["first_message"],
            "is_dev_mode": True
        }

    @staticmethod
    def validate_webhook_auth(authorization_header: Optional[str] = None, token_param: Optional[str] = None) -> bool:
        """Validates incoming webhook requests from ElevenLabs tools."""
        if not ELEVENLABS_WEBHOOK_SECRET:
            return True
        
        expected_bearer = f"Bearer {ELEVENLABS_WEBHOOK_SECRET}"
        if authorization_header and (authorization_header == expected_bearer or authorization_header == ELEVENLABS_WEBHOOK_SECRET):
            return True
        if token_param and token_param == ELEVENLABS_WEBHOOK_SECRET:
            return True
        
        # Also allow requests in local development mode
        if os.getenv("ENV", "development") == "development":
            return True
            
        return False

    @staticmethod
    def process_post_call_telemetry(interview_id: str, post_call_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Stores post-call webhook transcript, duration, audio recording URL, and metadata from ElevenLabs.
        Associates conversation_id with the interview session without creating duplicate records.
        """
        session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if not session:
            # Fallback search by elevenlabs_conversation_id
            conv_id = post_call_data.get("conversation_id")
            if conv_id:
                session = db.query(InterviewSession).filter(InterviewSession.elevenlabs_conversation_id == conv_id).first()
        
        if not session:
            logger.error(f"Could not find interview session for post-call data: {interview_id}")
            return {"status": "error", "message": "Session not found"}

        conv_id = post_call_data.get("conversation_id")
        if conv_id:
            session.elevenlabs_conversation_id = conv_id

        transcript = post_call_data.get("transcript", [])
        if transcript and isinstance(transcript, list):
            # Append post call transcript cleanly
            session.transcript = transcript

        duration = post_call_data.get("duration", 0) or post_call_data.get("duration_seconds", 0)
        if duration:
            session.duration_seconds = int(duration)

        if not session.completed_at:
            session.completed_at = datetime.utcnow()
            session.status = "COMPLETED"
            session.brain_status = "COMPLETED"

        # Log event
        event = InterviewEvent(
            id=f"evt_postcall_{int(time.time())}",
            interview_id=session.id,
            event_type="ELEVENLABS_POST_CALL_RECEIVED",
            metadata_json={
                "conversation_id": conv_id,
                "duration": duration,
                "transcript_turns": len(transcript) if isinstance(transcript, list) else 0,
                "received_at": datetime.utcnow().isoformat()
            }
        )
        db.add(event)
        db.commit()
        db.refresh(session)

        return {
            "status": "success",
            "interview_id": session.id,
            "conversation_id": session.elevenlabs_conversation_id,
            "duration": session.duration_seconds,
            "status_updated": session.status
        }
