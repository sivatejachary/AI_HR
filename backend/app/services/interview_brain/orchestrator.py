import logging
import threading
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.models.domain import (
    InterviewSession, InterviewQuestion, InterviewAnswer, InterviewEvent,
    Candidate, Job, HiringWorkflow, WorkflowStep
)
from app.services.interview_brain.context_service import InterviewContextService
from app.services.interview_brain.plan_service import InterviewPlanService
from app.services.interview_brain.question_engine import QuestionEngine
from app.services.interview_brain.answer_analysis import AnswerAnalysisService
from app.services.interview_brain.followup_engine import FollowUpEngine

logger = logging.getLogger("orchestrator")

# Concurrency Protection Lock Map
_SESSION_LOCKS: Dict[str, threading.Lock] = {}
_LOCK_MAP_MUTEX = threading.Lock()

def _get_session_lock(session_id: str) -> threading.Lock:
    with _LOCK_MAP_MUTEX:
        if session_id not in _SESSION_LOCKS:
            _SESSION_LOCKS[session_id] = threading.Lock()
        return _SESSION_LOCKS[session_id]

class AIInterviewOrchestrator:
    """
    Deterministic AI Interview Orchestrator & State Machine Engine.
    Controls stage progression, enforces workflow version freezing, ensures concurrency safety,
    stores structured event logs, and guarantees human override controls (Pause/Resume/Complete).
    """

    STAGES_ORDER = [
        "INTERVIEW_START",
        "WAITING_FOR_CANDIDATE",
        "INTRODUCTION",
        "BASIC_SCREENING",
        "RESUME_DISCUSSION",
        "TECHNICAL_INTERVIEW",
        "TECHNICAL_FOLLOW_UP",
        "CODING_INTRO",
        "CODING",
        "CODE_REVIEW",
        "DEBUGGING",
        "OPTIMIZATION",
        "TECHNICAL_WRAP_UP",
        "BEHAVIORAL",
        "CANDIDATE_QUESTIONS",
        "CLOSING",
        "EVALUATION",
        "HR_REVIEW",
        "COMPLETED"
    ]

    @staticmethod
    def _log_event(db: Session, session_id: str, event_type: str, metadata: dict = None) -> InterviewEvent:
        unique_id = f"evt-{int(datetime.utcnow().timestamp()*1000)}-{uuid.uuid4().hex[:6]}"
        evt = InterviewEvent(
            id=unique_id,
            interview_id=session_id,
            event_type=event_type,
            metadata_json=metadata or {},
            timestamp=datetime.utcnow()
        )
        db.add(evt)
        db.commit()
        return evt

    @staticmethod
    def create_session(db: Session, candidate_id: str, job_id: str, interview_id: Optional[str] = None, company_id: str = "org-default") -> Dict[str, Any]:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        job = db.query(Job).filter(Job.id == job_id).first()

        if not candidate or not job:
            return {"status": "error", "message": "Candidate or Job not found"}

        # Lock active workflow version
        wf = None
        if job.workflow_id:
            wf = db.query(HiringWorkflow).filter(HiringWorkflow.id == job.workflow_id).first()
        if not wf:
            wf = db.query(HiringWorkflow).filter(HiringWorkflow.is_active == True).first()

        wf_id = wf.id if wf else None
        wf_version = wf.version if wf else 1

        sess_id = f"INT-{int(datetime.utcnow().timestamp()*1000)}"
        session = InterviewSession(
            id=sess_id,
            interview_id=interview_id,
            candidate_id=candidate_id,
            job_id=job_id,
            workflow_id=wf_id,
            workflow_version=wf_version,
            organization_id=company_id,
            status="PENDING",
            brain_status="IDLE",
            current_stage="INTERVIEW_START",
            current_question_number=0,
            difficulty="MEDIUM",
            metadata_json={"created_by": "AIInterviewOrchestrator"}
        )
        db.add(session)
        db.commit()

        AIInterviewOrchestrator._log_event(db, sess_id, "INTERVIEW_CREATED", {"candidate_id": candidate_id, "job_id": job_id})
        return AIInterviewOrchestrator.get_state(db, sess_id)

    @staticmethod
    def start_interview(db: Session, session_id: str) -> Dict[str, Any]:
        lock = _get_session_lock(session_id)
        with lock:
            session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
            if not session:
                return {"status": "error", "message": "Session not found"}

            session.status = "IN_PROGRESS"
            session.brain_status = "STARTING"
            session.started_at = datetime.utcnow()
            session.current_stage = "INTERVIEW_START"
            db.commit()

            AIInterviewOrchestrator._log_event(db, session_id, "INTERVIEW_STARTED", {"stage": session.current_stage})
            return AIInterviewOrchestrator.get_state(db, session_id)

    @staticmethod
    def get_state(db: Session, session_id: str) -> Dict[str, Any]:
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            return {"status": "error", "message": "Session not found"}

        elapsed = 0
        if session.started_at:
            end_time = getattr(session, "ended_at", None) or getattr(session, "completed_at", None) or datetime.utcnow()
            elapsed = int((end_time - session.started_at).total_seconds())

        return {
            "interview_id": session.id,
            "status": session.status,
            "brain_status": session.brain_status,
            "current_stage": session.current_stage,
            "question_number": session.current_question_number,
            "difficulty": session.difficulty,
            "workflow_id": session.workflow_id,
            "workflow_version": session.workflow_version,
            "organization_id": session.organization_id,
            "elapsed_seconds": elapsed,
            "screen_consent_given": session.screen_consent_given
        }

    @staticmethod
    def get_context(db: Session, session_id: str) -> Dict[str, Any]:
        return InterviewContextService.build_context(db, session_id)

    @staticmethod
    def get_next_question(db: Session, session_id: str) -> Dict[str, Any]:
        lock = _get_session_lock(session_id)
        with lock:
            session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
            if not session:
                return {"status": "error", "message": "Session not found"}

            if session.status == "PAUSED":
                return {"status": "error", "message": "Interview is currently paused by HR."}

            session.brain_status = "THINKING"
            db.commit()

            ctx = InterviewContextService.build_context(db, session_id)
            prev_qs = ctx.get("previous_questions", [])
            prev_ans = ctx.get("previous_answers", [])

            q_data = QuestionEngine.generate_next_question(
                stage=session.current_stage,
                current_difficulty=session.difficulty,
                job_context=ctx["job"],
                candidate_context=ctx["candidate"],
                previous_questions=prev_qs,
                previous_answers=prev_ans
            )

            q_num = session.current_question_number + 1
            session.current_question_number = q_num
            session.brain_status = "QUESTION_READY"

            q_id = f"Q-{q_num:04d}-{int(datetime.utcnow().timestamp()*1000)}"
            q_obj = InterviewQuestion(
                id=q_id,
                interview_id=session_id,
                session_id=session_id,
                category=q_data.get("question_type", "TECHNICAL"),
                stage=session.current_stage,
                question_number=q_num,
                question_order=q_num,
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                skill=q_data["skill"],
                difficulty=session.difficulty,
                answered=False
            )
            db.add(q_obj)
            db.commit()

            AIInterviewOrchestrator._log_event(db, session_id, "QUESTION_GENERATED", {"question_id": q_id, "question_number": q_num})
            AIInterviewOrchestrator._log_event(db, session_id, "QUESTION_ASKED", {"question_id": q_id})

            return {
                "question_id": q_obj.id,
                "question": q_obj.question_text,
                "stage": q_obj.stage,
                "skill": q_obj.skill,
                "difficulty": q_obj.difficulty,
                "question_type": q_obj.question_type,
                "question_number": q_num
            }

    @staticmethod
    def submit_answer(db: Session, session_id: str, question_id: str, answer_text: str) -> Dict[str, Any]:
        lock = _get_session_lock(session_id)
        with lock:
            session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
            if not session:
                return {"status": "error", "message": "Session not found"}

            question = db.query(InterviewQuestion).filter(
                InterviewQuestion.id == question_id,
                InterviewQuestion.interview_id == session_id
            ).first()

            if not question:
                return {"status": "error", "message": "Question not found"}

            question.candidate_answer = answer_text
            question.answered = True

            # Analyze answer
            ctx = InterviewContextService.build_context(db, session_id)
            analysis = AnswerAnalysisService.analyze_answer(question.question_text, answer_text, ctx["candidate"], ctx["job"])

            ans_id = f"ANS-{int(datetime.utcnow().timestamp()*1000)}"
            ans_obj = InterviewAnswer(
                id=ans_id,
                interview_id=session_id,
                question_id=question_id,
                answer_text=answer_text,
                answer_quality=analysis["correctness"],
                technical_depth=analysis["technical_depth"],
                relevance=analysis["relevance"],
                completeness=analysis["completeness"],
                confidence=analysis["confidence"],
                missing_concepts=analysis["missing_concepts"]
            )
            db.add(ans_obj)
            db.commit()

            AIInterviewOrchestrator._log_event(db, session_id, "ANSWER_RECEIVED", {"question_id": question_id, "answer_id": ans_id})
            AIInterviewOrchestrator._log_event(db, session_id, "ANSWER_ANALYZED", {"analysis": analysis})

            # Decide next action
            next_action = AIInterviewOrchestrator.decide_next_action(db, session_id, analysis)
            return {
                "status": "success",
                "question_id": question_id,
                "answer_id": ans_id,
                "analysis": analysis,
                "next_action": next_action
            }

    @staticmethod
    def analyze_answer(db: Session, question_text: str, answer_text: str) -> Dict[str, Any]:
        return AnswerAnalysisService.analyze_answer(question_text, answer_text)

    @staticmethod
    def decide_next_action(db: Session, session_id: str, analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            return {"status": "error", "message": "Session not found"}

        if not analysis:
            answers = db.query(InterviewAnswer).filter(InterviewAnswer.interview_id == session_id).order_by(InterviewAnswer.created_at.desc()).all()
            if answers:
                analysis = {
                    "technical_depth": answers[0].technical_depth,
                    "relevance": answers[0].relevance,
                    "completeness": answers[0].completeness
                }
            else:
                analysis = {"technical_depth": 0.7, "relevance": 0.8, "completeness": 0.7}

        q_count = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == session_id,
            InterviewQuestion.stage == session.current_stage
        ).count()

        decision = FollowUpEngine.decide_next_action(
            current_stage=session.current_stage,
            current_difficulty=session.difficulty,
            analysis=analysis,
            questions_asked_in_stage=q_count,
            max_stage_questions=3
        )

        # Apply difficulty adjustments
        if decision["action"] == "INCREASE_DIFFICULTY" and session.difficulty != "HARD":
            session.difficulty = "HARD"
            db.commit()
            AIInterviewOrchestrator._log_event(db, session_id, "DIFFICULTY_CHANGED", {"difficulty": "HARD"})

        elif decision["action"] == "DECREASE_DIFFICULTY" and session.difficulty != "EASY":
            session.difficulty = "EASY"
            db.commit()
            AIInterviewOrchestrator._log_event(db, session_id, "DIFFICULTY_CHANGED", {"difficulty": "EASY"})

        elif decision["action"] == "MOVE_TO_NEXT_STAGE":
            AIInterviewOrchestrator.move_stage(db, session_id)

        return decision

    @staticmethod
    def move_stage(db: Session, session_id: str, target_stage: Optional[str] = None) -> Dict[str, Any]:
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            return {"status": "error", "message": "Session not found"}

        current = session.current_stage
        if target_stage and target_stage in AIInterviewOrchestrator.STAGES_ORDER:
            next_stage = target_stage
        else:
            current_idx = AIInterviewOrchestrator.STAGES_ORDER.index(current) if current in AIInterviewOrchestrator.STAGES_ORDER else 0
            if current_idx + 1 < len(AIInterviewOrchestrator.STAGES_ORDER):
                next_stage = AIInterviewOrchestrator.STAGES_ORDER[current_idx + 1]
            else:
                next_stage = "COMPLETED"

        session.current_stage = next_stage
        if next_stage == "COMPLETED":
            session.status = "COMPLETED"
            session.brain_status = "COMPLETED"
            session.completed_at = datetime.utcnow()

        db.commit()
        AIInterviewOrchestrator._log_event(db, session_id, "STAGE_CHANGED", {"from_stage": current, "to_stage": next_stage})
        return {"session_id": session_id, "current_stage": session.current_stage, "status": session.status}

    @staticmethod
    def pause_interview(db: Session, session_id: str) -> Dict[str, Any]:
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            return {"status": "error", "message": "Session not found"}

        session.status = "PAUSED"
        session.brain_status = "PAUSED"
        db.commit()
        AIInterviewOrchestrator._log_event(db, session_id, "INTERVIEW_PAUSED", {"action": "HR Pause Override"})
        return {"status": "success", "session_status": session.status, "brain_status": session.brain_status}

    @staticmethod
    def resume_interview(db: Session, session_id: str) -> Dict[str, Any]:
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            return {"status": "error", "message": "Session not found"}

        session.status = "IN_PROGRESS"
        session.brain_status = "THINKING"
        db.commit()
        AIInterviewOrchestrator._log_event(db, session_id, "INTERVIEW_RESUMED", {"action": "HR Resume Override"})
        return {"status": "success", "session_status": session.status, "brain_status": session.brain_status}

    @staticmethod
    def complete_interview(db: Session, session_id: str) -> Dict[str, Any]:
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            return {"status": "error", "message": "Session not found"}

        session.status = "COMPLETED"
        session.brain_status = "COMPLETED"
        session.current_stage = "COMPLETED"
        session.completed_at = datetime.utcnow()
        if session.started_at:
            session.duration_seconds = int((session.completed_at - session.started_at).total_seconds())

        db.commit()
        AIInterviewOrchestrator._log_event(db, session_id, "INTERVIEW_COMPLETED", {"duration": session.duration_seconds})
        return {"status": "success", "session_status": session.status, "brain_status": session.brain_status}

    @staticmethod
    def fail_interview(db: Session, session_id: str, reason: str = "Technical error") -> Dict[str, Any]:
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            return {"status": "error", "message": "Session not found"}

        session.status = "FAILED"
        session.brain_status = "ERROR"
        db.commit()
        AIInterviewOrchestrator._log_event(db, session_id, "INTERVIEW_FAILED", {"reason": reason})
        return {"status": "failed", "session_status": session.status, "reason": reason}
