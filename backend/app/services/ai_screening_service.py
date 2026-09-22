import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.domain import (
    Job, Candidate, Application, AIScreeningResult, ApplicationStatus
)

logger = logging.getLogger("ai_screening_service")


class GeminiScreeningService:
    """
    Real AI Resume Screening using Google Gemini API.
    PostgreSQL is the single source of truth for all screening results.
    The backend generates all scores — frontend never sends screening scores.
    """

    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    @staticmethod
    def _call_gemini(prompt: str) -> Optional[str]:
        """
        Calls the Gemini API synchronously and returns the response text.
        """
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set — screening will use fallback keyword match")
            return None

        import urllib.request
        import urllib.error

        url = f"{GeminiScreeningService.GEMINI_API_URL}?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1024
            }
        }
        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                candidates = result.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
        return None

    @staticmethod
    def screen_candidate(
        db: Session,
        application_id: str,
        candidate: Candidate,
        job: Job
    ) -> Dict[str, Any]:
        """
        Runs real Gemini AI screening of a candidate against a job.
        Stores the result in PostgreSQL and updates application status.
        Returns the screening result dict.
        """
        resume_text = candidate.resume_text or ""
        skills_text = ", ".join(candidate.skills or [])
        experience_years = float(candidate.years_experience or candidate.total_experience_years or 0)

        prompt = f"""You are an expert technical HR recruiter performing resume screening.

JOB DETAILS:
- Title: {job.title}
- Department: {job.department}
- Min Experience Required: {job.min_experience or job.experience_min or 0} years
- Max Experience: {job.max_experience or job.experience_max or 10} years
- Requirements: {job.requirements or 'Not specified'}
- Preferred Skills: {', '.join(job.preferred_skills or [])}
- Description: {(job.description or '')[:500]}

CANDIDATE PROFILE:
- Name: {candidate.name or candidate.full_name}
- Total Experience: {experience_years} years
- Skills: {skills_text}
- Education: {candidate.education or 'Not specified'}
- Resume: {resume_text[:2000] if resume_text else 'No resume text provided'}

Please analyze this candidate against the job requirements and respond ONLY with a valid JSON object (no markdown, no explanation) in exactly this format:
{{
  "match_score": <integer 0-100>,
  "recommendation": "SHORTLISTED" or "REJECTED" or "MANUAL_REVIEW",
  "screening_summary": "<2-3 sentence summary>",
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "experience_match": {{
    "required_years": <number>,
    "candidate_years": <number>,
    "is_match": <boolean>
  }},
  "strengths": ["strength1", "strength2"],
  "concerns": ["concern1", "concern2"]
}}

Scoring guide:
- 80-100: Excellent match, SHORTLISTED
- 60-79: Good match but review needed, MANUAL_REVIEW
- 0-59: Poor match, REJECTED

Respond ONLY with the JSON object."""

        gemini_result = None
        parsed = None

        gemini_text = GeminiScreeningService._call_gemini(prompt)
        if gemini_text:
            try:
                # Strip any markdown code blocks if present
                clean_text = gemini_text.strip()
                if clean_text.startswith("```"):
                    clean_text = clean_text.split("```")[1]
                    if clean_text.startswith("json"):
                        clean_text = clean_text[4:]
                parsed = json.loads(clean_text.strip())
            except json.JSONDecodeError as e:
                logger.warning(f"Gemini returned non-JSON response: {e}. Using fallback.")

        if not parsed:
            # Fallback: keyword-based scoring when Gemini is unavailable
            parsed = GeminiScreeningService._fallback_keyword_screen(candidate, job)

        match_score = int(parsed.get("match_score", 60))
        recommendation = parsed.get("recommendation", "MANUAL_REVIEW")
        if recommendation not in ("SHORTLISTED", "REJECTED", "MANUAL_REVIEW"):
            recommendation = "MANUAL_REVIEW"

        # Map recommendation to ApplicationStatus
        if recommendation == "SHORTLISTED":
            new_status = ApplicationStatus.AI_SHORTLISTED
        elif recommendation == "REJECTED":
            new_status = ApplicationStatus.SCREENING
        else:
            new_status = ApplicationStatus.SCREENING

        # Save screening result to PostgreSQL
        existing_scr = db.query(AIScreeningResult).filter(
            AIScreeningResult.application_id == application_id
        ).first()

        scr_data = {
            "match_score": match_score,
            "recommendation": recommendation,
            "explanation": parsed.get("screening_summary", ""),
            "required_skills_match": {s: "MATCH" for s in parsed.get("matched_skills", [])},
            "missing_requirements": parsed.get("missing_skills", []),
            "experience_match": parsed.get("experience_match", {}),
            "strengths": {"items": parsed.get("strengths", [])},
            "gaps": {"items": parsed.get("concerns", [])},
        }

        if existing_scr:
            for k, v in scr_data.items():
                setattr(existing_scr, k, v)
        else:
            scr = AIScreeningResult(
                id=f"scr-{int(datetime.utcnow().timestamp()*1000)}",
                application_id=application_id,
                **scr_data
            )
            db.add(scr)

        # Update application status
        app = db.query(Application).filter(Application.id == application_id).first()
        if app:
            app.status = new_status
            app.current_stage = "AI Screened" if recommendation != "SHORTLISTED" else "Shortlisted"

        db.commit()
        logger.info(f"Gemini screening complete for application {application_id}: score={match_score}, recommendation={recommendation}")

        return {
            "match_score": match_score,
            "recommendation": recommendation,
            "screening_summary": parsed.get("screening_summary", ""),
            "matched_skills": parsed.get("matched_skills", []),
            "missing_skills": parsed.get("missing_skills", []),
            "experience_match": parsed.get("experience_match", {}),
            "strengths": parsed.get("strengths", []),
            "concerns": parsed.get("concerns", []),
            "application_status": new_status.value if hasattr(new_status, "value") else str(new_status)
        }

    @staticmethod
    def _fallback_keyword_screen(candidate: Candidate, job: Job) -> Dict[str, Any]:
        """
        Fallback keyword-based screening used when Gemini API is unavailable.
        Better than hardcoded scores — uses actual candidate vs job keyword overlap.
        """
        resume_text = (candidate.resume_text or "").lower()
        skills_text = " ".join(candidate.skills or []).lower()
        combined_text = resume_text + " " + skills_text

        requirements_text = (job.requirements or "").lower()
        preferred_skills = [s.lower() for s in (job.preferred_skills or [])]

        # Count keyword matches
        req_words = [w for w in requirements_text.split() if len(w) > 3]
        if req_words:
            matches = sum(1 for w in req_words if w in combined_text)
            base_score = int((matches / len(req_words)) * 100)
        else:
            base_score = 50

        # Preferred skills bonus
        matched_skills = [s for s in preferred_skills if s in combined_text]
        skill_bonus = min(20, len(matched_skills) * 5)
        match_score = min(95, max(30, base_score + skill_bonus))

        # Experience check
        years_exp = float(candidate.years_experience or 0)
        min_exp = float(job.min_experience or job.experience_min or 0)
        exp_match = years_exp >= min_exp
        if not exp_match and min_exp > 0:
            match_score = max(30, match_score - 15)

        if match_score >= 75:
            recommendation = "SHORTLISTED"
        elif match_score >= 55:
            recommendation = "MANUAL_REVIEW"
        else:
            recommendation = "REJECTED"

        return {
            "match_score": match_score,
            "recommendation": recommendation,
            "screening_summary": f"Candidate has {years_exp} years experience. Keyword match score: {match_score}%. {'Experience meets requirements.' if exp_match else 'Experience below minimum requirement.'}",
            "matched_skills": matched_skills[:8],
            "missing_skills": [s for s in preferred_skills if s not in combined_text][:5],
            "experience_match": {"required_years": min_exp, "candidate_years": years_exp, "is_match": exp_match},
            "strengths": [f"Matched {len(matched_skills)} preferred skills"] if matched_skills else [],
            "concerns": [f"Below minimum experience ({min_exp} years required)"] if not exp_match else []
        }
