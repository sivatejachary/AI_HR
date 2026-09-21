import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("participant_service")

class ParticipantRole:
    AI = "AI"
    CANDIDATE = "CANDIDATE"
    HR = "HR"
    OBSERVER = "OBSERVER"
    UNKNOWN = "UNKNOWN"


class ParticipantService:
    """
    Manages meeting participant identity tracking, role assignment, and candidate detection.
    Enforces candidate identity verification before triggering AI Interview Brain start.
    """

    @staticmethod
    def identify_role(
        display_name: str,
        email: Optional[str] = None,
        candidate_name: Optional[str] = None,
        candidate_email: Optional[str] = None
    ) -> str:
        """
        Assigns participant role using multi-factor identity matching.
        Does not rely solely on substring matching.
        """
        name_clean = (display_name or "").strip().lower()
        cand_name_clean = (candidate_name or "").strip().lower()
        cand_email_clean = (candidate_email or "").strip().lower()

        # Check AI Bot Identity
        if "teja" in name_clean or "ai" in name_clean or "bot" in name_clean or "interviewer" in name_clean:
            return ParticipantRole.AI

        # Strongest match: Email match
        if email and cand_email_clean and email.strip().lower() == cand_email_clean:
            return ParticipantRole.CANDIDATE

        # High confidence name match
        if cand_name_clean and (name_clean == cand_name_clean or cand_name_clean in name_clean):
            return ParticipantRole.CANDIDATE

        # HR / Admin Identity
        if "hr" in name_clean or "admin" in name_clean or "recruiter" in name_clean:
            return ParticipantRole.HR

        return ParticipantRole.UNKNOWN

    @staticmethod
    def process_roster(
        roster: List[Dict[str, Any]],
        candidate_name: Optional[str] = None,
        candidate_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates active meeting roster and returns candidate presence, AI bot presence, and overall candidate status.
        """
        processed_roster = []
        has_candidate = False
        has_ai = False
        candidate_participant = None

        for p in roster:
            role = p.get("role")
            if not role or role == ParticipantRole.UNKNOWN:
                role = ParticipantService.identify_role(
                    display_name=p.get("display_name", ""),
                    email=p.get("email"),
                    candidate_name=candidate_name,
                    candidate_email=candidate_email
                )

            entry = {
                "participant_id": p.get("participant_id"),
                "display_name": p.get("display_name"),
                "email": p.get("email"),
                "role": role,
                "joined_at": p.get("joined_at", datetime.utcnow().isoformat()),
                "is_active": p.get("is_active", True)
            }
            processed_roster.append(entry)

            if role == ParticipantRole.CANDIDATE and entry["is_active"]:
                has_candidate = True
                candidate_participant = entry
            elif role == ParticipantRole.AI and entry["is_active"]:
                has_ai = True

        status = "CANDIDATE_PRESENT" if has_candidate else "WAITING_FOR_CANDIDATE"
        return {
            "status": status,
            "has_candidate": has_candidate,
            "has_ai": has_ai,
            "candidate_participant": candidate_participant,
            "processed_roster": processed_roster
        }
