import os
import sys
import json
import urllib.request
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE_URL = os.getenv("BACKEND_PUBLIC_URL", "https://ai-hrs.onrender.com")

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

def main():
    print("=== LIVE HTTP API VERIFICATION FOR PHASE 6 HIRING WORKFLOW EXECUTION & AI HR AGENT ===")
    
    # 0. Setup Valid Test Workflow in DB
    from app.db.database import SessionLocal
    from app.models.domain import HiringWorkflow, WorkflowStep, Job, Candidate, StepType
    db = SessionLocal()
    try:
        # Cleanup
        db.query(WorkflowStep).filter(WorkflowStep.workflow_id == "wf-http-test").delete()
        db.query(HiringWorkflow).filter(HiringWorkflow.id == "wf-http-test").delete()
        db.query(Job).filter(Job.id == "job-http-p6-001").delete()
        db.query(Candidate).filter(Candidate.id == "cand-http-p6-001").delete()
        db.commit()

        # Seed valid records
        c = Candidate(id="cand-http-p6-001", organization_id="org-default", name="Jane Doe", email="jane@example.com", phone="+1234567890", location="SF")
        j = Job(id="job-http-p6-001", organization_id="org-default", workflow_id="wf-http-test", title="AI Engineer", department="Eng", employment_type="Full-time", location="Remote", description="Job", responsibilities="Resp", requirements="Req", created_by="user-1")
        wf = HiringWorkflow(id="wf-http-test", organization_id="org-default", job_id="job-http-p6-001", name="HTTP Test Workflow", version=1, status="Draft")
        s1 = WorkflowStep(id="ws-http-1", workflow_id="wf-http-test", name="Resume Screening", category="Screening", type=StepType.AI_ACTION, order=1, owner="AI", automation="Fully automated", is_enabled=True)
        s2 = WorkflowStep(id="ws-http-2", workflow_id="wf-http-test", name="AI HR Call", category="Communication", type=StepType.VOICE_CALL, order=2, owner="AI", automation="Fully automated", is_enabled=True)
        s3 = WorkflowStep(id="ws-http-3", workflow_id="wf-http-test", name="Hiring Manager Review", category="Decision", type=StepType.APPROVAL, order=3, owner="Hiring Manager", automation="Manual", is_enabled=True)
        
        db.add(c); db.add(j); db.add(wf); db.add(s1); db.add(s2); db.add(s3)
        db.commit()
    finally:
        db.close()

    workflow_id = "wf-http-test"
    candidate_id = "cand-http-p6-001"
    job_id = "job-http-p6-001"

    # 1. List Workflow Templates
    print("\n1. Testing GET /api/workflows/templates ...")
    status, res = get("/api/workflows/templates")
    print(f"Status: {status}, Templates count: {len(res)}")
    assert status == 200

    # 2. Validate Workflow
    print(f"\n2. Testing POST /api/workflows/{workflow_id}/validate ...")
    status, res = post(f"/api/workflows/{workflow_id}/validate")
    print(f"Status: {status}, Is Valid: {res.get('is_valid')}")
    assert status == 200

    # 3. Simulate Workflow (Dry-Run Mode)
    print(f"\n3. Testing POST /api/workflows/{workflow_id}/simulate ...")
    status, res = post(f"/api/workflows/{workflow_id}/simulate")
    print(f"Status: {status}, Simulated steps: {len(res.get('simulated_trace', []))}")
    assert status == 200

    # 4. Publish Workflow Version
    print(f"\n4. Testing POST /api/workflows/{workflow_id}/publish ...")
    status, res = post(f"/api/workflows/{workflow_id}/publish")
    print(f"Status: {status}, Version: {res.get('version')}")
    assert status == 200

    # 5. Start Candidate Workflow Execution
    print(f"\n5. Testing POST /api/candidates/{candidate_id}/workflow/start ...")
    status, res = post(f"/api/candidates/{candidate_id}/workflow/start", {
        "job_id": job_id,
        "workflow_id": workflow_id
    })
    print(f"Status: {status}, Execution Status: {res.get('status')}")
    assert status == 200

    # 6. Get Candidate Active Workflow State
    print(f"\n6. Testing GET /api/candidates/{candidate_id}/workflow ...")
    status, res = get(f"/api/candidates/{candidate_id}/workflow")
    print(f"Status: {status}, Current Step: {res.get('current_step', {}).get('name')}")
    assert status == 200

    # 7. Get Candidate Workflow Event Timeline
    print(f"\n7. Testing GET /api/candidates/{candidate_id}/workflow/timeline ...")
    status, res = get(f"/api/candidates/{candidate_id}/workflow/timeline")
    print(f"Status: {status}, Events count: {len(res.get('timeline', []))}")
    assert status == 200

    # 8. Pause Candidate Workflow
    print(f"\n8. Testing POST /api/candidates/{candidate_id}/workflow/pause ...")
    status, res = post(f"/api/candidates/{candidate_id}/workflow/pause")
    print(f"Status: {status}")
    assert status == 200

    # 9. Resume Candidate Workflow
    print(f"\n9. Testing POST /api/candidates/{candidate_id}/workflow/resume ...")
    status, res = post(f"/api/candidates/{candidate_id}/workflow/resume")
    print(f"Status: {status}")
    assert status == 200

    # 10. HR Takeover Mode Toggle
    print(f"\n10. Testing POST /api/candidates/{candidate_id}/workflow/takeover ...")
    status, res = post(f"/api/candidates/{candidate_id}/workflow/takeover", {"is_human_takeover": True})
    print(f"Status: {status}, Human Takeover: {res.get('is_human_takeover')}")
    assert status == 200

    # 11. HR Approve Step
    print(f"\n11. Testing POST /api/candidates/{candidate_id}/workflow/approve ...")
    status, res = post(f"/api/candidates/{candidate_id}/workflow/approve", {"reason": "Verified via live HTTP test."})
    print(f"Status: {status}")
    assert status == 200

    # 12. Workflow Analytics
    print(f"\n12. Testing GET /api/workflows/{workflow_id}/analytics ...")
    status, res = get(f"/api/workflows/{workflow_id}/analytics")
    print(f"Status: {status}, Entered count: {res.get('total_candidates_entered')}")
    assert status == 200

    print("\nALL PHASE 6 WORKFLOW EXECUTION & AI HR AGENT LIVE HTTP E2E TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
