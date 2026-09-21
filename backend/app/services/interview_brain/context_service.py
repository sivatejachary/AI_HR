import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.models.domain import Candidate, Job, HiringWorkflow, WorkflowStep, InterviewSession, InterviewQuestion, InterviewAnswer

logger = logging.getLogger("context_service")

class InterviewContextService:
    """
    Loads normalized context for an AI interview session:
    - Candidate profile & resume skills/experience
    - Job role & job description details
    - Frozen Hiring Workflow version
    - Current interview stage & difficulty
    - History of asked questions and answers
    """

    @staticmethod
    def build_context(db: Session, session_id: str) -> Dict[str, Any]:
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            return {"status": "error", "message": f"InterviewSession {session_id} not found"}

        candidate = db.query(Candidate).filter(Candidate.id == session.candidate_id).first()
        job = db.query(Job).filter(Job.id == session.job_id).first()
        
        workflow = None
        if session.workflow_id:
            workflow = db.query(HiringWorkflow).filter(HiringWorkflow.id == session.workflow_id).first()
        if not workflow and job and job.workflow_id:
            workflow = db.query(HiringWorkflow).filter(HiringWorkflow.id == job.workflow_id).first()

        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == session_id
        ).order_by(InterviewQuestion.question_number.asc()).all()

        answers = db.query(InterviewAnswer).filter(
            InterviewAnswer.interview_id == session_id
        ).order_by(InterviewAnswer.created_at.asc()).all()

        # Build normalized candidate context
        cand_dict = {
            "id": candidate.id if candidate else session.candidate_id,
            "name": candidate.name if candidate else "Unknown Candidate",
            "email": candidate.email if candidate else "",
            "experience_years": candidate.years_experience if candidate else 0,
            "education": candidate.education if candidate else "",
            "skills": candidate.skills if candidate else [],
            "resume_summary": candidate.resume_text[:500] if candidate and candidate.resume_text else ""
        }

        # Build normalized job context
        job_dict = {
            "id": job.id if job else session.job_id,
            "title": job.title if job else "Software Engineer",
            "department": job.department if job else "Engineering",
            "description": job.description if job else "",
            "requirements": job.requirements if job else "",
            "preferred_skills": job.preferred_skills if job else []
        }

        # Format questions & answers list
        q_list = []
        for q in questions:
            ans_obj = next((a for a in answers if a.question_id == q.id), None)
            q_list.append({
                "id": q.id,
                "question_number": q.question_number,
                "stage": q.stage,
                "skill": q.skill,
                "question_type": q.question_type,
                "difficulty": q.difficulty,
                "question_text": q.question_text,
                "answered": q.answered,
                "answer_text": ans_obj.answer_text if ans_obj else (q.candidate_answer or None)
            })

        return {
            "interview_id": session.id,
            "status": session.status,
            "brain_status": session.brain_status,
            "current_stage": session.current_stage,
            "question_number": session.current_question_number,
            "difficulty": session.difficulty,
            "workflow_id": session.workflow_id,
            "workflow_version": session.workflow_version,
            "candidate": cand_dict,
            "job": job_dict,
            "skills": cand_dict["skills"] or job_dict["preferred_skills"],
            "previous_questions": q_list,
            "previous_answers": [
                {
                    "question_id": a.question_id,
                    "answer_text": a.answer_text,
                    "quality": a.answer_quality,
                    "technical_depth": a.technical_depth
                } for a in answers
            ]
        }
