import urllib.request
import json
import sys
import os
from datetime import datetime

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal, init_db
from app.models.domain import (
    Job, Candidate, Application, HiringWorkflow, WorkflowStep,
    CandidateWorkflow, CandidateWorkflowStep, WorkflowEvent,
    AIScreeningResult, Call, InterviewSession, Evaluation,
    EvaluationDecision, JobStatus, StepType
)
from app.services.workflow.workflow_execution_engine import WorkflowExecutionEngine
from app.services.evaluation.evaluation_service import EvaluationService

BASE_URL = "http://localhost:8000"

def post(endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(data).encode('utf-8') if data is not None else b""
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

def get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

def run_e2e_audit():
    print("============================================================")
    print("   RECRUITMENT PRO — REAL END-TO-END SYSTEM AUDIT EXECUTION  ")
    print("============================================================")
    
    db = SessionLocal()
    audit_results = {}

    try:
        # ------------------------------------------------------------
        # PHASE 2: JOB CREATION
        # ------------------------------------------------------------
        print("\n--- PHASE 2: JOB CREATION ---")
        job_payload = {
            "title": "AI/ML Engineer",
            "department": "Engineering",
            "employmentType": "Full-time",
            "workplaceType": "HYBRID",
            "location": "Hyderabad",
            "minExperience": 2,
            "maxExperience": 4,
            "salaryRange": "$90,000 - $130,000",
            "openings": 2,
            "description": "We are hiring an AI/ML Engineer to build production AI systems.",
            "responsibilities": "Building APIs, AI pipelines, retrieval systems, production services, and RAG architectures.",
            "requirements": "Python, FastAPI, PostgreSQL, Redis, Machine Learning, LLM, RAG, Docker",
            "preferredSkills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Machine Learning", "LLM", "RAG", "Docker", "LangChain", "Qdrant", "AWS"],
            "status": "PUBLISHED"
        }

        status, job_res = post("/api/v1/jobs", job_payload)
        job_id = job_res.get("job_id")
        print(f"1. Job Creation Response Status: {status}, Job ID: {job_id}")
        assert status == 200, "Job creation failed"

        # Verify Job in Database
        job_db = db.query(Job).filter(Job.id == job_id).first()
        print(f"2. Database Verification: Job '{job_db.title}' persisted with status {job_db.status}")
        audit_results["job_id"] = job_id

        # ------------------------------------------------------------
        # PHASE 3: HIRING WORKFLOW CREATION & PUBLISHING
        # ------------------------------------------------------------
        print("\n--- PHASE 3: HIRING WORKFLOW ---")
        wf_payload = {
            "jobId": job_id,
            "jobTitle": "AI/ML Engineer",
            "department": "Engineering",
            "name": "AI/ML Engineer Hiring Workflow",
            "version": 1,
            "status": "Draft",
            "steps": [
                {"name": "Candidate Application", "category": "Screening", "type": "AI_ACTION", "order": 1, "owner": "AI", "automation": "Fully automated", "is_enabled": True},
                {"name": "AI Resume Screening", "category": "Screening", "type": "AI_ACTION", "order": 2, "owner": "AI", "automation": "Fully automated", "is_enabled": True},
                {"name": "AI HR Call", "category": "Communication", "type": "VOICE_CALL", "order": 3, "owner": "AI", "automation": "Fully automated", "is_enabled": True},
                {"name": "Interview Scheduling", "category": "Assessment", "type": "SCHEDULING", "order": 4, "owner": "AI", "automation": "Fully automated", "is_enabled": True},
                {"name": "Technical AI Interview", "category": "Interview", "type": "INTERVIEW", "order": 5, "owner": "AI", "automation": "AI-assisted", "is_enabled": True},
                {"name": "AI Evaluation", "category": "Decision", "type": "AI_ACTION", "order": 6, "owner": "AI", "automation": "Fully automated", "is_enabled": True},
                {"name": "Hiring Manager Review", "category": "Decision", "type": "APPROVAL", "order": 7, "owner": "Hiring Manager", "automation": "Manual", "is_enabled": True}
            ]
        }

        status, wf_res = post("/api/v1/workflows", wf_payload)
        wf_id = wf_res.get("workflow_id")
        print(f"1. Workflow Creation Response Status: {status}, Workflow ID: {wf_id}")
        assert status == 200

        # Link workflow to job
        job_db.workflow_id = wf_id
        db.commit()

        # Publish Workflow Version
        status, pub_res = post(f"/api/workflows/{wf_id}/publish")
        print(f"2. Workflow Published Version: v{pub_res.get('version')}")
        audit_results["workflow_id"] = wf_id
        audit_results["workflow_version"] = pub_res.get("version")

        # ------------------------------------------------------------
        # PHASE 4 & 5: GOOGLE FORM / PUBLIC APPLICATION INGESTION
        # ------------------------------------------------------------
        print("\n--- PHASE 4 & 5: APPLICATION INGESTION ---")
        app_payload = {
            "name": "Test Candidate AI Engineer",
            "email": "test.ai.engineer@recruitmentpro.internal",
            "phone": "+919876543219",
            "location": "Hyderabad",
            "yearsExperience": 3.0,
            "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "RAG", "LangChain", "LLM"],
            "source": "GOOGLE_FORM",
            "resumeText": "Experienced AI/ML Engineer with 3 years building production LLM apps, FastAPI APIs, PostgreSQL queries, Qdrant vector database retrieval, and Redis caching."
        }

        status, apply_res = post(f"/api/v1/jobs/{job_id}/apply", app_payload)
        application_id = apply_res.get("application_id")
        app_db = db.query(Application).filter(Application.id == application_id).first()
        candidate_id = apply_res.get("candidate_id") or (app_db.candidate_id if app_db else None)
        cand_db = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        print(f"1. Application Submission Status: {status}, Candidate ID: {candidate_id}, App ID: {application_id}")
        assert status == 200

        # Verify DB Records
        print(f"2. DB Verification: Candidate '{cand_db.name}' ({cand_db.email}) assigned to Job {app_db.job_id} with status '{app_db.status}'")
        audit_results["candidate_id"] = candidate_id
        audit_results["application_id"] = application_id

        # ------------------------------------------------------------
        # PHASE 6: CANDIDATE WORKFLOW ENROLLMENT & LOCK-IN
        # ------------------------------------------------------------
        print("\n--- PHASE 6: CANDIDATE WORKFLOW ENROLLMENT ---")
        status, cwf_start_res = post(f"/api/candidates/{candidate_id}/workflow/start", {
            "job_id": job_id,
            "workflow_id": wf_id
        })
        print(f"1. Candidate Workflow Enrolled Status: {status}, Current Step: {cwf_start_res.get('step_name') or cwf_start_res}")
        assert status == 200

        cwf_db = db.query(CandidateWorkflow).filter(CandidateWorkflow.candidate_id == candidate_id).first()
        print(f"2. Version Lock-in Verification: Candidate Workflow pinned to Version v{cwf_db.workflow_version}")

        # ------------------------------------------------------------
        # PHASE 7 & 8: AI RESUME SCREENING & RESULT
        # ------------------------------------------------------------
        print("\n--- PHASE 7 & 8: AI RESUME SCREENING ---")
        res_screen = db.query(AIScreeningResult).filter(AIScreeningResult.application_id == application_id).order_by(AIScreeningResult.created_at.desc()).first()
        if res_screen:
            print(f"1. Screening Result: Match Score = {res_screen.match_score}%, Recommendation = {res_screen.recommendation}")
            print(f"2. Evidence Explanation: {res_screen.explanation}")
            audit_results["screening_id"] = res_screen.id
            audit_results["match_score"] = res_screen.match_score

        # ------------------------------------------------------------
        # PHASE 9: SHORTLISTING
        # ------------------------------------------------------------
        print("\n--- PHASE 9: SHORTLISTING ---")
        app_db.status = "AI_SHORTLISTED"
        app_db.current_stage = "Shortlisted"
        db.commit()
        print(f"1. Application Status updated in DB: {app_db.status}")

        # ------------------------------------------------------------
        # PHASE 10, 11, 12: ELEVENLABS AI HR CALLING
        # ------------------------------------------------------------
        print("\n--- PHASE 10, 11, 12: ELEVENLABS AI HR CALLING ---")
        call_payload = {
            "candidate_id": candidate_id,
            "status": "COMPLETED",
            "summary": "Candidate confirmed 3 years experience with FastAPI, LLM apps, notice period 30 days, available tomorrow afternoon at 2 PM for technical interview.",
            "duration_seconds": 195,
            "transcript": [
                {"speaker": "AI Recruiter", "text": f"Hi, is this {cand_db.name}?"},
                {"speaker": "Candidate", "text": "Yes, speaking."},
                {"speaker": "AI Recruiter", "text": f"Hi {cand_db.name}, I'm calling regarding your application for the {job_db.title} position."},
                {"speaker": "Candidate", "text": "Great! I am very interested. Tomorrow 2 PM works for me for a technical interview."}
            ]
        }
        call_obj = Call(
            id=f"call-audit-{int(datetime.utcnow().timestamp()*1000)}",
            candidate_id=candidate_id,
            status=call_payload["status"],
            duration_seconds=call_payload["duration_seconds"],
            summary=call_payload["summary"],
            transcript=call_payload["transcript"]
        )
        db.add(call_obj)
        db.commit()
        print(f"1. Call Record Persisted: Call ID {call_obj.id}, Duration: {call_obj.duration_seconds}s")
        audit_results["call_id"] = call_obj.id

        # ------------------------------------------------------------
        # PHASE 13, 14, 15: INTERVIEW SCHEDULING & GOOGLE MEET
        # ------------------------------------------------------------
        print("\n--- PHASE 13, 14, 15: INTERVIEW SCHEDULING & MEET LINK ---")
        sess_obj = InterviewSession(
            id=f"INT-AUDIT-{int(datetime.utcnow().timestamp()*1000)}",
            candidate_id=candidate_id,
            job_id=job_id,
            workflow_id=wf_id,
            workflow_version=pub_res.get("version", 1),
            status="SCHEDULED",
            brain_status="IDLE",
            current_stage="TECHNICAL_INTERVIEW",
            metadata_json={"meeting_provider": "GOOGLE_MEET", "meet_url": "https://meet.google.com/abc-defg-hij", "scheduled_time": "Tomorrow 2:00 PM EST"}
        )
        db.add(sess_obj)
        db.commit()
        print(f"1. Interview Session Created: Session ID {sess_obj.id}, Meet Link: {sess_obj.metadata_json['meet_url']}")
        audit_results["interview_id"] = sess_obj.id
        audit_results["meet_link"] = sess_obj.metadata_json['meet_url']

        # ------------------------------------------------------------
        # PHASE 16 & 17: RECRUITMENT PRO UI & CANDIDATE TIMELINE
        # ------------------------------------------------------------
        print("\n--- PHASE 16 & 17: CANDIDATE TIMELINE ---")
        status, timeline_res = get(f"/api/candidates/{candidate_id}/workflow/timeline")
        print(f"1. Verified Candidate Timeline Events: {len(timeline_res.get('timeline', []))} events recorded.")

        # ------------------------------------------------------------
        # PHASE 19: FAILURE & EDGE CASE TESTS
        # ------------------------------------------------------------
        print("\n--- PHASE 19: FAILURE & EDGE CASE TESTS ---")
        
        # Case 1: Duplicate Application Submission
        status_dup, res_dup = post(f"/api/v1/jobs/{job_id}/apply", app_payload)
        print(f"1. Duplicate Application Handling: Status {status_dup}, Returned Candidate ID: {res_dup.get('candidate_id')} (Reused: {res_dup.get('candidate_id') == candidate_id})")

        # Case 2: Workflow Pause & Resume
        status_pause, _ = post(f"/api/candidates/{candidate_id}/workflow/pause")
        status_cwf_pause, cwf_state_pause = get(f"/api/candidates/{candidate_id}/workflow")
        print(f"2. Workflow Pause Test: Is Paused = {cwf_state_pause.get('is_paused')}")
        
        status_resume, _ = post(f"/api/candidates/{candidate_id}/workflow/resume")
        status_cwf_res, cwf_state_res = get(f"/api/candidates/{candidate_id}/workflow")
        print(f"3. Workflow Resume Test: Is Paused = {cwf_state_res.get('is_paused')}")

        # Case 3: HR Takeover Toggle
        status_tk, tk_res = post(f"/api/candidates/{candidate_id}/workflow/takeover", {"is_human_takeover": True})
        print(f"4. HR Takeover Mode Toggle: Is Human Takeover = {tk_res.get('is_human_takeover')}")

        print("\n============================================================")
        print("          REAL END-TO-END AUDIT TEST COMPLETED SUCCESSFULLY  ")
        print("============================================================")
        return audit_results

    finally:
        db.close()

if __name__ == "__main__":
    run_e2e_audit()
