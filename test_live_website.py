import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

FRONTEND_URL = "https://ai-hr-git-main-shiva-s-projects27.vercel.app"
BACKEND_URL = "https://ai-hrs.onrender.com"

results = []

def test_endpoint(url, method="GET", data=None, headers=None):
    try:
        req = urllib.request.Request(url, method=method)
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        if data:
            req.add_header('Content-Type', 'application/json')
            encoded_data = json.dumps(data).encode('utf-8')
        else:
            encoded_data = None

        with urllib.request.urlopen(req, data=encoded_data, timeout=15, context=ctx) as response:
            status = response.status
            body = response.read().decode('utf-8')
            try:
                parsed = json.loads(body)
            except:
                parsed = body[:150] + "..." if len(body) > 150 else body
            return status, parsed, None
    except Exception as e:
        return None, None, str(e)

print("==================================================")
print("     LIVE PRODUCTION SYSTEM INTEGRATION TEST      ")
print("==================================================\n")

# 1. Test Frontend Vercel Pages
frontend_routes = ["/", "/candidates", "/workflows", "/settings", "/jobs", "/evaluations"]
print("--- 1. Testing Frontend Pages on Vercel ---")
for route in frontend_routes:
    full_url = f"{FRONTEND_URL}{route}"
    status, _, err = test_endpoint(full_url)
    if status == 200:
        print(f"  [OK 200] Frontend Route: {route}")
    else:
        print(f"  [FAIL {status}] Frontend Route: {route} - Error: {err}")

# 2. Test Backend API & PostgreSQL Database Health
print("\n--- 2. Testing Render Backend API & Database ---")
health_status, health_resp, err = test_endpoint(f"{BACKEND_URL}/health")
print(f"  Health Check: {health_status} -> {health_resp}")

db_status, db_resp, err = test_endpoint(f"{BACKEND_URL}/health/database")
print(f"  Database Check: {db_status} -> {db_resp}")

# 3. Test Core API Endpoints
print("\n--- 3. Testing Backend Data Endpoints ---")
cand_status, cand_resp, err = test_endpoint(f"{BACKEND_URL}/api/v1/candidates")
cand_count = len(cand_resp) if isinstance(cand_resp, list) else 0
print(f"  Candidates API: {cand_status} -> Found {cand_count} candidates in PostgreSQL DB")

jobs_status, jobs_resp, err = test_endpoint(f"{BACKEND_URL}/api/v1/jobs")
jobs_count = len(jobs_resp) if isinstance(jobs_resp, list) else 0
print(f"  Jobs API: {jobs_status} -> Found {jobs_count} active job postings")

wf_status, wf_resp, err = test_endpoint(f"{BACKEND_URL}/api/v1/workflows")
wf_count = len(wf_resp) if isinstance(wf_resp, list) else 0
print(f"  Workflows API: {wf_status} -> Found {wf_count} hiring workflows")

# 4. Test Hiring Workflow Execution Engine & Scheduling
print("\n--- 4. Testing Manual HR Scheduler Controls ---")
if isinstance(cand_resp, list) and len(cand_resp) > 0:
    first_cand = cand_resp[0]
    c_id = first_cand.get("id") or first_cand.get("candidate_id")
    print(f"  Testing Workflow Timeline for Candidate: {first_cand.get('name')} (ID: {c_id})")
    
    tl_status, tl_resp, err = test_endpoint(f"{BACKEND_URL}/api/v1/candidates/{c_id}/workflow/steps-timeline")
    print(f"  Timeline Endpoint: status={tl_status}")
    if isinstance(tl_resp, dict):
        steps = tl_resp.get("steps", [])
        print(f"  Total Timeline Steps: {len(steps)}")
        for idx, s in enumerate(steps[:3]):
            print(f"    Step {s.get('step_order')}: {s.get('name')} | Type={s.get('schedule_type')} | Exec={s.get('executor')} | Status={s.get('status')}")
            
    # Test Run Now Control
    run_status, run_resp, err = test_endpoint(f"{BACKEND_URL}/api/v1/candidates/{c_id}/workflow/run-now", method="POST", data={})
    print(f"  Manual Override 'Run Now': status={run_status} -> {run_resp}")

print("\n==================================================")
print("           END TO END TEST COMPLETE               ")
print("==================================================")
