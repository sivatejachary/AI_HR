import logging
import re
from typing import Dict, Any, List, Optional
from app.services.interview_brain.experience_engine import ExperienceEngine

logger = logging.getLogger("question_engine")

class QuestionEngine:
    """
    Experience-Aware Real-World Question Engine for Recruitment Pro.
    Tailors question difficulty, depth, scenario style, and resume project claim verification
    to candidate's actual experience band (FRESHER, JUNIOR, MID_LEVEL, SENIOR, STAFF).
    """

    PROGRESSION_LEVELS = {
        1: "LEVEL_1_BASIC_UNDERSTANDING",
        2: "LEVEL_2_PRACTICAL_IMPLEMENTATION",
        3: "LEVEL_3_REAL_WORLD_SCENARIO",
        4: "LEVEL_4_FAILURE_AND_EDGE_CASES",
        5: "LEVEL_5_SCALE_AND_PERFORMANCE",
        6: "LEVEL_6_ARCHITECTURE_AND_TRADEOFFS"
    }

    @staticmethod
    def _clean_text(text: str) -> str:
        return re.sub(r'[^a-z0-9\s]', '', text.lower()).strip()

    @staticmethod
    def is_duplicate(new_question: str, previous_questions: List[Dict[str, Any]]) -> bool:
        clean_new = QuestionEngine._clean_text(new_question)
        new_words = set(clean_new.split())
        
        for q in previous_questions:
            existing_text = q.get("question_text", "")
            clean_exist = QuestionEngine._clean_text(existing_text)
            if clean_exist == clean_new:
                return True
                
            exist_words = set(clean_exist.split())
            if not new_words or not exist_words:
                continue
                
            overlap = len(new_words.intersection(exist_words)) / max(len(new_words), len(exist_words))
            if overlap > 0.8:
                return True
                
        return False

    @staticmethod
    def generate_next_question(
        stage: str,
        current_difficulty: str,
        job_context: Dict[str, Any],
        candidate_context: Dict[str, Any],
        previous_questions: List[Dict[str, Any]],
        previous_answers: List[Dict[str, Any]] = None,
        target_skill: Optional[str] = None
    ) -> Dict[str, Any]:

        job_title = job_context.get("title", "Software Engineer")
        job_reqs = job_context.get("requirements", "")
        cand_name = candidate_context.get("name", "Candidate")
        cand_exp_yrs = candidate_context.get("experience_years", 0)
        resume_text = candidate_context.get("resume_summary", "")

        # 1. Determine multi-signal experience band
        scores = [a.get("quality", 0.8) for a in (previous_answers or [])]
        exp_meta = ExperienceEngine.determine_experience_band(
            years_experience=cand_exp_yrs,
            role_title=job_title,
            job_requirements=job_reqs,
            resume_text=resume_text,
            previous_scores=scores
        )

        band = exp_meta["band"] # FRESHER | JUNIOR | MID_LEVEL | SENIOR | STAFF
        project_claims = exp_meta["project_claims"]

        # Calculate current progression level (Level 1 to Level 6)
        questions_asked = len(previous_questions)
        max_allowed_level = exp_meta["max_target_level"]
        current_level = min(questions_asked + 1, max_allowed_level)

        skills = candidate_context.get("skills") or job_context.get("preferred_skills") or ["Software Engineering"]
        selected_skill = target_skill or (skills[questions_asked % len(skills)] if skills else "Application Development")

        # Handle stage-specific introductory or closing questions
        if stage in ["INTERVIEW_START", "INTRODUCTION"]:
            q_text = f"Welcome {cand_name}! Thanks for taking the time today. To get started, could you briefly introduce yourself and share a brief summary of your background in {selected_skill}?"
            q_type = "FUNDAMENTAL"

        elif stage == "BEHAVIORAL":
            q_text = f"Can you describe a situation where you encountered a tricky technical problem in a {job_title} role, and how you worked through it?"
            q_type = "SCENARIO"

        elif stage == "CANDIDATE_QUESTIONS":
            q_text = f"That covers our core technical discussion! Do you have any questions for us about the team, architecture, or tech stack?"
            q_type = "FUNDAMENTAL"

        elif stage == "CLOSING":
            q_text = f"Thank you so much for your time today, {cand_name}! We appreciate you sharing your technical experience. Have a wonderful day!"
            q_type = "FUNDAMENTAL"

        # Resume Project Claim Verification Flow
        elif project_claims and (stage in ["BASIC_SCREENING", "RESUME_DISCUSSION"] or (questions_asked % 3 == 1 and current_level <= 4)):
            claim = project_claims[questions_asked % len(project_claims)]
            category = claim["category"]
            
            if "RAG" in category:
                if current_level == 1:
                    q_text = f"You mentioned working on {category}. Can you walk me through the high-level architecture of your retrieval pipeline?"
                elif current_level == 2:
                    q_text = f"On that {category} project, how did you handle document chunking and vector embedding generation?"
                elif current_level >= 3:
                    q_text = f"Imagine retrieval quality dropped after your document collection grew from 100,000 to 10 million chunks. How would you investigate precision loss and reduce query latency?"
                q_type = "PROJECT_BASED"
            else:
                q_text = f"In your resume, you highlighted experience with {category}. Could you walk me through the architecture and your specific role in building it?"
                q_type = "PROJECT_BASED"

        # Technical Deep-Dive & Coding Follow-Ups (Experience-Aware)
        else:
            if band == "FRESHER":
                if current_level == 1:
                    q_text = f"You are building a college placement application. Students submit details via an API, but sometimes a student clicks Submit twice. How would you prevent duplicate records?"
                    q_type = "PRACTICAL_IMPLEMENTATION"
                elif current_level == 2:
                    q_text = f"If two placement requests arrive at the exact same millisecond, what boundary condition could cause a duplicate record?"
                    q_type = "BASIC_DEBUGGING"
                else:
                    q_text = f"How do you structure basic error handling and data validation when receiving user input in {selected_skill}?"
                    q_type = "API"

            elif band == "JUNIOR":
                if current_level == 1:
                    q_text = f"Your employee API endpoint receives an invalid email format or missing fields. How would you implement request validation and return structured error responses?"
                    q_type = "API"
                elif current_level == 2:
                    q_text = f"How would you structure database query filtering and basic response caching in {selected_skill} to improve API performance?"
                    q_type = "DATABASE"
                else:
                    q_text = f"When debugging a runtime error or unexpected null pointer in {selected_skill}, what log signals and tools do you inspect first?"
                    q_type = "DEBUGGING"

            elif band == "MID_LEVEL":
                if current_level <= 2:
                    q_text = f"In an interview scheduling service, two HR users click Schedule at almost the exact same millisecond for the same slot. How would you implement double-booking prevention?"
                    q_type = "CONCURRENCY"
                elif current_level == 3:
                    q_text = f"Comparing a Redis distributed lock vs a PostgreSQL 'FOR UPDATE' row lock, what trade-offs in lock contention and transaction rollback would you consider?"
                    q_type = "CACHING"
                else:
                    q_text = f"How do you design background worker queues (like Celery/Redis) with retries and idempotency keys to handle transient API failures?"
                    q_type = "BACKGROUND_JOBS"

            elif band == "SENIOR":
                if current_level <= 3:
                    q_text = f"Your candidate search API handles 50,000 requests/min. PostgreSQL CPU is normal, but Redis hit rate dropped and latency jumped from 300ms to 4s. How would you investigate and resolve this?"
                    q_type = "PRODUCTION_INCIDENT"
                elif current_level == 4:
                    q_text = f"How would you prevent cache stampedes (dog-piling) when hot cache keys expire during peak traffic?"
                    q_type = "PERFORMANCE"
                else:
                    q_text = f"If traffic increased 10x from 50k to 500k req/min, what database sharding, indexing, or read-replica strategy would you introduce?"
                    q_type = "SYSTEM_DESIGN"

            else: # STAFF (8+ Yrs)
                if current_level <= 3:
                    q_text = f"Design a multi-region interview scheduling platform operating across US-East, EU-West, and AP-South. How do you prevent double-booking during regional network partitions?"
                    q_type = "ARCHITECTURE"
                elif current_level == 4:
                    q_text = f"What distributed consistency model (eventual vs strong) and fencing token mechanism would you choose to guarantee zero double bookings during failover?"
                    q_type = "DISTRIBUTED_SYSTEMS"
                else:
                    q_text = f"How would you observe, trace, and debug cascading failures across multi-region microservices without incurring massive log storage overhead?"
                    q_type = "OBSERVABILITY"

        # Prevent duplicates
        if QuestionEngine.is_duplicate(q_text, previous_questions):
            q_text = f"Building on your experience in {selected_skill}, what core trade-offs do you evaluate when choosing between different architectural frameworks or design patterns?"
            q_type = "ARCHITECTURE"

        return {
            "question_text": q_text,
            "question_type": q_type,
            "skill": selected_skill,
            "difficulty": current_difficulty,
            "stage": stage,
            "experience_band": band,
            "progression_level": current_level,
            "progression_label": QuestionEngine.PROGRESSION_LEVELS.get(current_level, "LEVEL_1")
        }
