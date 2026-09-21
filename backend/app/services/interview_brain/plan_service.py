import logging
from typing import Dict, Any, List

logger = logging.getLogger("plan_service")

class InterviewPlanService:
    """
    Generates a structured Interview Plan specifying topic priorities
    and initial difficulty target based on candidate background & job requirements.
    """

    @staticmethod
    def generate_plan(candidate_context: Dict[str, Any], job_context: Dict[str, Any]) -> Dict[str, Any]:
        cand_skills = set(s.lower() for s in (candidate_context.get("skills") or []))
        req_skills = job_context.get("preferred_skills") or ["Python", "System Architecture", "SQL"]
        exp_years = candidate_context.get("experience_years", 3)

        topics = []
        for idx, skill in enumerate(req_skills):
            skill_lower = skill.lower()
            priority = "HIGH" if (skill_lower in cand_skills or idx < 2) else "MEDIUM"
            q_count = 3 if priority == "HIGH" else 2
            topics.append({
                "skill": skill,
                "priority": priority,
                "question_count": q_count
            })

        initial_difficulty = "HARD" if exp_years >= 7 else ("MEDIUM" if exp_years >= 2 else "EASY")

        return {
            "topics": topics,
            "difficulty": initial_difficulty
        }
