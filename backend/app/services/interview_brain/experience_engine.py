import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("experience_engine")

class ExperienceEngine:
    """
    Experience-Aware Intelligence Engine for Recruitment Pro.
    Determines candidate experience band (FRESHER, JUNIOR, MID_LEVEL, SENIOR, STAFF),
    extracts resume project claims, calculates multi-signal effective experience,
    and guides target question depth (Level 1 to Level 6).
    """

    BANDS = {
        "FRESHER": {"min_yrs": 0, "max_yrs": 0.5, "max_level": 2, "label": "Fresher / Entry Level"},
        "JUNIOR": {"min_yrs": 0.5, "max_yrs": 2.0, "max_level": 3, "label": "Junior Engineer (0-2 Yrs)"},
        "MID_LEVEL": {"min_yrs": 2.0, "max_yrs": 5.0, "max_level": 4, "label": "Mid-Level Engineer (2-5 Yrs)"},
        "SENIOR": {"min_yrs": 5.0, "max_yrs": 8.0, "max_level": 5, "label": "Senior Engineer (5-8 Yrs)"},
        "STAFF": {"min_yrs": 8.0, "max_yrs": 99.0, "max_level": 6, "label": "Staff / Principal Engineer (8+ Yrs)"}
    }

    PROJECT_PATTERNS = [
        (r'rag|retrieval-augmented|vector|qdrant|chroma|pinecone|langchain|llm|embedding', "RAG / Vector Search Platform"),
        (r'fastapi|flask|django|express|nest|spring boot', "Web Application & REST API"),
        (r'kafka|rabbitmq|sqs|celery|event-driven|pub/sub', "Message Queue & Event Pipeline"),
        (r'redis|memcached|cache', "Distributed Caching Layer"),
        (r'postgresql|postgres|mysql|mongodb|dynamodb|sql', "Database & Storage Systems"),
        (r'kubernetes|k8s|docker|terraform|aws|gcp|azure|ci/cd', "DevOps & Cloud Infrastructure"),
        (r'payment|stripe|paypal|transaction|billing', "Payment & Financial Transactions"),
        (r'microservice|gRPC|protobuf', "Microservices Architecture")
    ]

    @staticmethod
    def extract_project_claims(resume_text: str) -> List[Dict[str, str]]:
        """Extracts candidate project claims and technology mentions from resume text."""
        claims = []
        if not resume_text:
            return claims

        lines = resume_text.split('\n')
        text_lower = resume_text.lower()

        for pattern, category in ExperienceEngine.PROJECT_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                # Find matching line snippet as evidence
                snippet = next((line.strip() for line in lines if any(m in line.lower() for m in matches)), "")
                claims.append({
                    "category": category,
                    "keyword_matched": matches[0],
                    "snippet": snippet[:160] if snippet else f"Experience with {category}"
                })

        return claims

    @staticmethod
    def determine_experience_band(
        years_experience: float,
        role_title: str = "",
        job_requirements: str = "",
        resume_text: str = "",
        previous_scores: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Calculates multi-signal effective experience band:
        `candidate_experience` + `role_requirements` + `resume_evidence` + `technical_answers`
        """
        title_lower = (role_title or "").lower()
        req_lower = (job_requirements or "").lower()
        text_lower = (resume_text or "").lower()

        # 1. Base experience from profile
        base_yrs = float(years_experience or 0.0)

        # 2. Adjust for explicitly stated role title seniority
        title_bonus = 0.0
        if "staff" in title_lower or "principal" in title_lower or "lead" in title_lower:
            title_bonus = 3.0
        elif "senior" in title_lower or "sr" in title_lower:
            title_bonus = 2.0
        elif "fresher" in title_lower or "intern" in title_lower:
            title_bonus = -1.0

        # 3. Resume complexity signals (production vs academic)
        resume_bonus = 0.0
        if any(kw in text_lower for kw in ["distributed", "sharding", "multi-region", "kubernetes", "50k req", "throughput", "high availability"]):
            resume_bonus += 1.5
        elif any(kw in text_lower for kw in ["college project", "academic", "coursework", "student", "intern"]):
            resume_bonus -= 0.5

        # 4. Demonstrated performance adjustment from previous answers
        answer_bonus = 0.0
        if previous_scores and len(previous_scores) > 0:
            avg_score = sum(previous_scores) / len(previous_scores)
            if avg_score >= 0.85:
                answer_bonus += 1.0
            elif avg_score < 0.5:
                answer_bonus -= 1.0

        effective_yrs = max(0.0, round(base_yrs + title_bonus + resume_bonus + answer_bonus, 1))

        # Assign band based on effective years
        if effective_yrs == 0 or ("fresher" in title_lower and base_yrs < 1.0):
            band = "FRESHER"
        elif effective_yrs <= 2.0:
            band = "JUNIOR"
        elif effective_yrs <= 5.0:
            band = "MID_LEVEL"
        elif effective_yrs <= 8.0:
            band = "SENIOR"
        else:
            band = "STAFF"

        band_info = ExperienceEngine.BANDS[band]
        project_claims = ExperienceEngine.extract_project_claims(resume_text)

        return {
            "band": band,
            "label": band_info["label"],
            "base_years": base_yrs,
            "effective_years": effective_yrs,
            "max_target_level": band_info["max_level"],
            "project_claims": project_claims,
            "rationale": f"Calculated {effective_yrs} effective years (Base: {base_yrs}y, Title adj: {title_bonus}, Resume adj: {resume_bonus}, Score adj: {answer_bonus}) -> Band: {band}"
        }
