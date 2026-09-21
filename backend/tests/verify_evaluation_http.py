import urllib.request
import json
import sys

BASE_URL = "http://localhost:8000"

def post(endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(data).encode('utf-8') if data else b""
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
    print("=== LIVE HTTP API VERIFICATION FOR PHASE 5 AI EVALUATION & HR REVIEW ===")
    
    # 0. Initialize Test Interview Session
    status, start_sess = post("/api/v1/interviews/ai/start-test-session")
    interview_id = start_sess.get("interview_id", "INT-TEST-PHASE5-001")
    print(f"Initialized Test Interview Session: {interview_id}")

    # 1. Trigger AI Evaluation
    print("\n1. Testing POST /api/interviews/ai/{interview_id}/evaluate ...")
    status, res = post(f"/api/interviews/ai/{interview_id}/evaluate", {"evaluation_version": "v1.0"})
    print(f"Status: {status}")
    print(f"Response Summary: {res.get('overall_summary')}")
    assert status == 200, f"Expected 200, got {status}"
    assert "evaluation_id" in res
    assert "competencies" in res

    # 2. Get Evaluation Details
    print("\n2. Testing GET /api/interviews/ai/{interview_id}/evaluation ...")
    status, res = get(f"/api/interviews/ai/{interview_id}/evaluation")
    print(f"Status: {status}")
    print(f"Competencies count: {len(res.get('competencies', []))}")
    assert status == 200

    # 3. Get Evaluation Evidence
    print("\n3. Testing GET /api/interviews/ai/{interview_id}/evaluation/evidence ...")
    status, res = get(f"/api/interviews/ai/{interview_id}/evaluation/evidence")
    print(f"Status: {status}")
    assert status == 200

    # 4. Get Evaluation Competencies
    print("\n4. Testing GET /api/interviews/ai/{interview_id}/evaluation/competencies ...")
    status, res = get(f"/api/interviews/ai/{interview_id}/evaluation/competencies")
    print(f"Status: {status}")
    assert status == 200

    # 5. Get JD Alignment Matrix
    print("\n5. Testing GET /api/interviews/ai/{interview_id}/evaluation/jd-alignment ...")
    status, res = get(f"/api/interviews/ai/{interview_id}/evaluation/jd-alignment")
    print(f"Status: {status}")
    assert status == 200
    assert len(res.get("jd_alignment", [])) > 0

    # 6. Re-evaluate (New Version v1.1)
    print("\n6. Testing POST /api/interviews/ai/{interview_id}/evaluation/re-evaluate ...")
    status, res = post(f"/api/interviews/ai/{interview_id}/evaluation/re-evaluate", {"evaluation_version": "v1.1"})
    print(f"Status: {status}")
    assert status == 200
    assert res.get("evaluation_version") == "v1.1"

    # 7. Record HR Decision
    print("\n7. Testing POST /api/interviews/{interview_id}/decision ...")
    status, res = post(f"/api/interviews/{interview_id}/decision", {
        "decision": "MOVE_TO_NEXT_STAGE",
        "reason": "Candidate demonstrated strong engineering competency in technical & coding evaluation."
    })
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")
    assert status == 200
    assert res.get("decision") == "MOVE_TO_NEXT_STAGE"

    print("\nALL PHASE 5 EVALUATION & HR REVIEW LIVE HTTP E2E TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
