import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BACKEND_URL = "https://ai-hrs.onrender.com"

# 1. Fetch Candidates and Jobs
with urllib.request.urlopen(f"{BACKEND_URL}/api/v1/candidates", context=ctx) as r:
    cands = json.loads(r.read().decode('utf-8'))
    shiva = [c for c in cands if c.get("name") == "Shiva"][0]

with urllib.request.urlopen(f"{BACKEND_URL}/api/v1/jobs", context=ctx) as r:
    jobs = json.loads(r.read().decode('utf-8'))
    job_id = jobs[0]["id"]

with urllib.request.urlopen(f"{BACKEND_URL}/api/v1/workflows", context=ctx) as r:
    wfs = json.loads(r.read().decode('utf-8'))
    wf_id = wfs[0]["id"]

cand_id = shiva.get("id") or shiva.get("candidate_id")
print(f"Starting workflow for Shiva ({cand_id}) with Job ({job_id}) & Workflow ({wf_id})...")

# Try starting candidate workflow
start_url = f"{BACKEND_URL}/api/candidates/{cand_id}/workflow/start"
payload = json.dumps({"jobId": job_id, "workflowId": wf_id}).encode('utf-8')
req = urllib.request.Request(start_url, data=payload, headers={"Content-Type": "application/json"}, method="POST")

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("Start Workflow Result:", json.dumps(res, indent=2))
except Exception as e:
    print("Start Workflow Error:", e)

# Now check steps-timeline again
tl_url = f"{BACKEND_URL}/api/candidates/{cand_id}/workflow/steps-timeline"
try:
    with urllib.request.urlopen(tl_url, context=ctx) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("Timeline Result:", json.dumps(res, indent=2))
except Exception as e:
    print("Timeline Error:", e)
