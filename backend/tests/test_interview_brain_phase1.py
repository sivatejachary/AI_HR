from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.domain import Base, Candidate, Job, HiringWorkflow, Organization, InterviewSession, InterviewQuestion, InterviewAnswer, InterviewEvent
from app.services.interview_brain.orchestrator import AIInterviewOrchestrator
from app.services.interview_brain.context_service import InterviewContextService
from app.services.interview_brain.question_engine import QuestionEngine
from app.services.interview_brain.answer_analysis import AnswerAnalysisService
from app.services.interview_brain.followup_engine import FollowUpEngine

# Test Database setup (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_test_db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Seed org, candidate, job, workflow
    org = Organization(id="org-test", name="Test Enterprise Org", slug="test-org")
    session.add(org)
    
    wf = HiringWorkflow(id="WF-1001", organization_id="org-test", name="Senior Engineer Flow", version=3, is_active=True)
    session.add(wf)
    
    job = Job(
        id="JOB-1001",
        organization_id="org-test",
        workflow_id="WF-1001",
        title="Python Developer",
        department="Engineering",
        employment_type="Full-Time",
        location="Remote",
        description="Senior Python backend engineer role",
        responsibilities="Build APIs",
        requirements="Python, FastAPI, Postgres",
        preferred_skills=["Python", "FastAPI", "PostgreSQL"],
        created_by="user-admin"
    )
    session.add(job)
    
    cand = Candidate(
        id="CAND-1001",
        organization_id="org-test",
        name="Rahul Kumar",
        email="rahul@example.com",
        phone="+1234567890",
        location="San Francisco",
        skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
        years_experience=5,
        education="B.S. Computer Science"
    )
    session.add(cand)
    session.commit()
    return session

def test_create_and_start_session(db):
    res = AIInterviewOrchestrator.create_session(db, candidate_id="CAND-1001", job_id="JOB-1001", company_id="org-test")
    assert res["status"] == "PENDING"
    assert res["current_stage"] == "INTERVIEW_START"
    assert res["workflow_version"] == 3 # Version frozen

    started = AIInterviewOrchestrator.start_interview(db, res["interview_id"])
    assert started["status"] == "IN_PROGRESS"
    assert started["brain_status"] == "STARTING"

def test_context_loading(db):
    sess = AIInterviewOrchestrator.create_session(db, candidate_id="CAND-1001", job_id="JOB-1001", company_id="org-test")
    ctx = InterviewContextService.build_context(db, sess["interview_id"])
    assert ctx["candidate"]["name"] == "Rahul Kumar"
    assert ctx["job"]["title"] == "Python Developer"
    assert ctx["workflow_version"] == 3

def test_question_generation_and_duplicate_prevention(db):
    sess = AIInterviewOrchestrator.create_session(db, candidate_id="CAND-1001", job_id="JOB-1001", company_id="org-test")
    AIInterviewOrchestrator.start_interview(db, sess["interview_id"])
    
    q1 = AIInterviewOrchestrator.get_next_question(db, sess["interview_id"])
    assert q1["question"] is not None
    assert q1["question_number"] == 1

    # Duplicate detection check
    prev_qs = [{"question_text": q1["question"]}]
    is_dup = QuestionEngine.is_duplicate(q1["question"], prev_qs)
    assert is_dup is True

def test_answer_submission_analysis_and_followup(db):
    sess = AIInterviewOrchestrator.create_session(db, candidate_id="CAND-1001", job_id="JOB-1001", company_id="org-test")
    AIInterviewOrchestrator.start_interview(db, sess["interview_id"])
    q1 = AIInterviewOrchestrator.get_next_question(db, sess["interview_id"])

    ans_res = AIInterviewOrchestrator.submit_answer(
        db, sess["interview_id"], q1["question_id"],
        "I built async microservices in FastAPI connected to PostgreSQL with connection pooling."
    )
    assert ans_res["status"] == "success"
    assert ans_res["analysis"]["technical_depth"] >= 0.4
    assert ans_res["next_action"]["action"] in ["FOLLOW_UP", "CLARIFY", "NEXT_TOPIC", "INCREASE_DIFFICULTY", "DECREASE_DIFFICULTY", "MOVE_TO_NEXT_STAGE"]

def test_difficulty_escalation(db):
    sess = AIInterviewOrchestrator.create_session(db, candidate_id="CAND-1001", job_id="JOB-1001", company_id="org-test")
    AIInterviewOrchestrator.start_interview(db, sess["interview_id"])
    
    strong_analysis = {"technical_depth": 0.95, "relevance": 0.95, "completeness": 0.90}
    decision = FollowUpEngine.decide_next_action("TECHNICAL_INTERVIEW", "MEDIUM", strong_analysis, questions_asked_in_stage=1)
    assert decision["action"] == "INCREASE_DIFFICULTY"

def test_stage_transitions(db):
    sess = AIInterviewOrchestrator.create_session(db, candidate_id="CAND-1001", job_id="JOB-1001", company_id="org-test")
    AIInterviewOrchestrator.start_interview(db, sess["interview_id"])
    
    stage1 = AIInterviewOrchestrator.move_stage(db, sess["interview_id"])
    assert stage1["current_stage"] == "INTRODUCTION"
    
    stage2 = AIInterviewOrchestrator.move_stage(db, sess["interview_id"], target_stage="TECHNICAL_INTERVIEW")
    assert stage2["current_stage"] == "TECHNICAL_INTERVIEW"

def test_pause_resume_complete_controls(db):
    sess = AIInterviewOrchestrator.create_session(db, candidate_id="CAND-1001", job_id="JOB-1001", company_id="org-test")
    AIInterviewOrchestrator.start_interview(db, sess["interview_id"])
    
    paused = AIInterviewOrchestrator.pause_interview(db, sess["interview_id"])
    assert paused["session_status"] == "PAUSED"
    assert paused["brain_status"] == "PAUSED"

    # Attempting to get next question while paused should error out
    next_q = AIInterviewOrchestrator.get_next_question(db, sess["interview_id"])
    assert next_q["status"] == "error"

    resumed = AIInterviewOrchestrator.resume_interview(db, sess["interview_id"])
    assert resumed["session_status"] == "IN_PROGRESS"

    completed = AIInterviewOrchestrator.complete_interview(db, sess["interview_id"])
    assert completed["session_status"] == "COMPLETED"

def test_event_logging(db):
    sess = AIInterviewOrchestrator.create_session(db, candidate_id="CAND-1001", job_id="JOB-1001", company_id="org-test")
    events = db.query(InterviewEvent).filter(InterviewEvent.interview_id == sess["interview_id"]).all()
    assert len(events) >= 1
    assert events[0].event_type == "INTERVIEW_CREATED"

if __name__ == "__main__":
    db = get_test_db()
    test_create_and_start_session(db)
    print("test_create_and_start_session PASSED")
    test_context_loading(db)
    print("test_context_loading PASSED")
    test_question_generation_and_duplicate_prevention(db)
    print("test_question_generation_and_duplicate_prevention PASSED")
    test_answer_submission_analysis_and_followup(db)
    print("test_answer_submission_analysis_and_followup PASSED")
    test_difficulty_escalation(db)
    print("test_difficulty_escalation PASSED")
    test_stage_transitions(db)
    print("test_stage_transitions PASSED")
    test_pause_resume_complete_controls(db)
    print("test_pause_resume_complete_controls PASSED")
    test_event_logging(db)
    print("test_event_logging PASSED")
    print("=== ALL PHASE 1 TEST SUITE ASSERTIONS PASSED ===")
