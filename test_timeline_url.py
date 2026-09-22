import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BACKEND_URL = "https://ai-hrs.onrender.com"

# 1. Fetch Candidate Shiva
req = urllib.request.Request(f"{BACKEND_URL}/api/v1/candidates")
with urllib.request.urlopen(req, context=ctx) as resp:
    cands = json.loads(resp.read().decode('utf-8'))
    shiva = [c for c in cands if c.get("name") == "Shiva"][0]
    c_id = shiva.get("id") or shiva.get("candidate_id")
    print(f"Testing Candidate Shiva (ID: {c_id})")

# 2. Get steps-timeline
tl_url = f"{BACKEND_URL}/api/candidates/{c_id}/workflow/steps-timeline"
print(f"Fetching: {tl_url}")
req_tl = urllib.request.Request(tl_url)
with urllib.request.urlopen(req_tl, context=ctx) as resp_tl:
    data = json.loads(resp_tl.read().decode('utf-8'))
    print("Timeline Data:")
    print(json.dumps(data, indent=2))
