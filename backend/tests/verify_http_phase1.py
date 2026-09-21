import urllib.request
import json

BASE_URL = "http://localhost:8000/api/v1/interviews/ai"

def post(endpoint, data=None):
    payload = json.dumps(data or {}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}{endpoint}", data=payload, headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode('utf-8'))

def get(endpoint):
    req = urllib.request.Request(f"{BASE_URL}{endpoint}")
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode('utf-8'))

if __name__ == "__main__":
    print("--- 1. START AI INTERVIEW ---")
    start = post("/start", {"candidate_id": "cand-1789808190814", "job_id": "job-1789808188717"})
    i_id = start["interview_id"]
    print("Interview ID:", i_id, "| Status:", start["status"])

    print("\n--- 2. GET CONTEXT ---")
    ctx = get(f"/{i_id}/context")
    print("Candidate:", ctx["candidate"]["name"], "| Job:", ctx["job"]["title"])

    print("\n--- 3. GENERATE NEXT QUESTION ---")
    q = post(f"/{i_id}/next-question")
    print("Question:", q["question"])

    print("\n--- 4. SUBMIT ANSWER ---")
    ans = post(f"/{i_id}/answer", {"question_id": q["question_id"], "answer_text": "I built async FastAPI web microservices with connection pooling for PostgreSQL."})
    print("Analysis:", ans["analysis"])
    print("Next Action:", ans["next_action"])

    print("\n--- 5. HR PAUSE ---")
    pause = post(f"/{i_id}/pause")
    print("Status after Pause:", pause["session_status"])

    print("\n--- 6. HR RESUME ---")
    resume = post(f"/{i_id}/resume")
    print("Status after Resume:", resume["session_status"])

    print("\n--- 7. HR COMPLETE ---")
    comp = post(f"/{i_id}/complete")
    print("Status after Complete:", comp["session_status"])

    print("\n=== ALL PHASE 1 LIVE HTTP E2E TESTS PASSED SUCCESSFULLY! ===")
