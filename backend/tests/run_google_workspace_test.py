import os
import sys
import json
import urllib.request
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

opener = urllib.request.build_opener(NoRedirectHandler)

def http_get(path: str):
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "E2ETestRunner/1.0"})
    try:
        with opener.open(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            return e.code, {"redirect_url": e.headers.get("Location")}
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {}

def http_post(path: str, payload: dict = None):
    url = f"{API_BASE}{path}"
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "E2ETestRunner/1.0"}, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def run_workspace_test():
    print("============================================================")
    print("   RECRUITMENT PRO — GOOGLE WORKSPACE E2E TEST RUNNER")
    print("============================================================")

    # 1. Create a Test Job
    job_payload = {
        "title": "Senior AI Infrastructure Engineer",
        "department": "AI Engineering",
        "employmentType": "Full-time",
        "workplaceType": "HYBRID",
        "location": "Hyderabad",
        "minExperience": 3,
        "maxExperience": 6,
        "openings": 2,
        "description": "Building scalable AI pipelines & LLM services.",
        "requirements": "Python, FastAPI, PostgreSQL, Redis, Docker, LangChain",
        "preferredSkills": ["Python", "FastAPI", "PostgreSQL", "RAG"],
        "status": "PUBLISHED"
    }
    status, job_res = http_post("/jobs", job_payload)
    job_id = job_res.get("job_id") or job_res.get("id")
    print(f"1. Job Creation: Status {status}, Job ID: {job_id}")
    assert status == 200

    # 2. Test Google OAuth Status
    status, gstat_res = http_get("/integrations/google/status")
    print(f"2. Google OAuth Status: Status {status}, Connected: {gstat_res.get('connected')}")
    assert status == 200

    # 3. Test OAuth Callback Token Persistence
    status, _ = http_get("/integrations/google/callback?code=test_auth_code_999")
    print(f"3. OAuth Callback Code Exchange: Status {status}")

    # Re-verify Status
    status, gstat_res2 = http_get("/integrations/google/status")
    print(f"4. Verified Google Status After Connect: Email = {gstat_res2.get('email')}, Services = {gstat_res2.get('services')}")
    assert gstat_res2.get("connected") == True

    # 4. Create Google Form for Job
    status, form_res = http_post(f"/jobs/{job_id}/google-form")
    print(f"5. Google Form Creation: Status {status}, Form ID: {form_res.get('google_form_id')}")
    print(f"   Edit URL: {form_res.get('google_form_url')}")
    print(f"   Responder URL: {form_res.get('google_responder_url')}")
    assert status == 200
    assert form_res.get("google_form_id") is not None

    # Duplicate Form Creation Prevention Check
    status_dup_f, form_res_dup = http_post(f"/jobs/{job_id}/google-form")
    print(f"6. Duplicate Form Creation Prevention: Status = {form_res_dup.get('status')}")
    assert form_res_dup.get("status") == "EXISTS"

    # 5. Ingest Candidate Response via Google Form Submission
    submission_payload = {
        "google_form_id": form_res.get("google_form_id"),
        "google_response_id": "response-xyz-987654321",
        "job_id": job_id,
        "name": "Google Form Candidate Engineer",
        "email": f"gform.candidate.{int(datetime.utcnow().timestamp())}@recruitmentpro.internal",
        "phone": "+919876543219",
        "location": "Hyderabad",
        "years_experience": 4.0,
        "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "RAG"],
        "resume_text": "4 years experience in Python, FastAPI, vector search, and RAG systems."
    }
    status, sub_res = http_post("/integrations/google-forms/submissions", submission_payload)
    print(f"7. Candidate Ingestion from Google Form: Status {status}, Result: {sub_res.get('status')}")
    print(f"   Candidate ID: {sub_res.get('candidate_id')}, App ID: {sub_res.get('application_id')}, Match Score: {sub_res.get('match_score')}%")
    assert status == 200
    assert sub_res.get("status") == "SUCCESS"

    # 6. Idempotency Verification (Submitting same response twice)
    status_dup, sub_dup_res = http_post("/integrations/google-forms/submissions", submission_payload)
    print(f"8. Response Idempotency Check: Result = {sub_dup_res.get('status')}")
    assert sub_dup_res.get("status") == "ALREADY_PROCESSED"

    # 7. Disconnect Test
    status_disc, disc_res = http_post("/integrations/google/disconnect")
    print(f"9. Google OAuth Disconnect: Result = {disc_res.get('status')}")
    assert status_disc == 200

    print("\n============================================================")
    print("   ALL GOOGLE WORKSPACE & GOOGLE FORM TESTS PASSED PERFECTLY!")
    print("============================================================")

if __name__ == "__main__":
    run_workspace_test()
