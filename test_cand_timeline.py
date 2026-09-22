import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BACKEND_URL = "https://ai-hrs.onrender.com"

req = urllib.request.Request(f"{BACKEND_URL}/api/v1/candidates")
with urllib.request.urlopen(req, context=ctx) as resp:
    cands = json.loads(resp.read().decode('utf-8'))
    print(f"Candidates list ({len(cands)} items):")
    for c in cands:
        cid = c.get("id") or c.get("candidate_id")
        print(f"  Candidate: {c.get('name')} | ID: {cid} | Email: {c.get('email')}")
        
        # Check timeline
        tl_req = urllib.request.Request(f"{BACKEND_URL}/api/v1/candidates/{cid}/workflow/steps-timeline")
        try:
            with urllib.request.urlopen(tl_req, context=ctx) as tl_resp:
                tl_data = json.loads(tl_resp.read().decode('utf-8'))
                steps = tl_data.get("steps", [])
                print(f"    Timeline Status: 200 OK | Steps: {len(steps)}")
                for s in steps[:4]:
                    print(f"      Order {s.get('step_order')}: {s.get('name')} | Status={s.get('status')} | SchedType={s.get('schedule_type')} | Exec={s.get('executor')}")
        except Exception as e:
            print(f"    Timeline Exception: {e}")
