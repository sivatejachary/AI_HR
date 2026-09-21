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
    print("=== LIVE HTTP API VERIFICATION FOR PHASE 4 ONLINE CODING & VISION ===")
    
    # 0. Initialize Test Interview Session
    status, start_sess = post("/api/v1/interviews/ai/start-test-session")
    interview_id = start_sess.get("interview_id", "INT-TEST-PHASE4-001")
    print(f"Initialized Test Interview Session: {interview_id}")

    # 1. Start Coding Session
    print("\n1. Testing POST /api/interviews/{interview_id}/coding/start ...")
    status, res = post(f"/api/interviews/{interview_id}/coding/start", {"language": "python"})
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")
    assert status == 200, f"Expected 200, got {status}"
    assert "coding_session_id" in res
    assert "coding_url" in res
    assert "problem" in res
    assert "reference_solution" not in res["problem"], "Private reference_solution leaked!"
    assert "private_evaluation_notes" not in res["problem"], "Private notes leaked!"

    # 2. Get Coding Session Details
    print("\n2. Testing GET /api/interviews/{interview_id}/coding ...")
    status, res = get(f"/api/interviews/{interview_id}/coding")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")
    assert status == 200

    # 3. Get Public Coding Problem Details
    print("\n3. Testing GET /api/interviews/{interview_id}/coding/problem ...")
    status, res = get(f"/api/interviews/{interview_id}/coding/problem")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")
    assert status == 200
    assert "title" in res

    # 4. Update Screen Share State (Start)
    print("\n4. Testing POST /api/interviews/{interview_id}/coding/screen-share (start) ...")
    status, res = post(f"/api/interviews/{interview_id}/coding/screen-share", {"action": "start"})
    print(f"Status: {status}")
    print(f"Response: {res}")
    assert status == 200
    assert res["session_status"] == "SCREEN_SHARE_ACTIVE"

    # 5. Add Vision AI Frame Observation
    print("\n5. Testing POST /api/interviews/{interview_id}/coding/observations ...")
    status, res = post(f"/api/interviews/{interview_id}/coding/observations", {
        "screen_type": "ONLINE_COMPILER",
        "language": "PYTHON",
        "code_visible": True,
        "error_visible": True,
        "visible_error_text": "IndexError: list index out of range at line 7"
    })
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")
    assert status == 200
    assert res["observation"]["error_visible"] == True

    # 6. List Vision Observations
    print("\n6. Testing GET /api/interviews/{interview_id}/coding/observations ...")
    status, res = get(f"/api/interviews/{interview_id}/coding/observations")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")
    assert status == 200
    assert len(res["observations"]) > 0

    # 7. Request Coding Hint
    print("\n7. Testing POST /api/interviews/{interview_id}/coding/hint ...")
    status, res = post(f"/api/interviews/{interview_id}/coding/hint")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")
    assert status == 200
    assert "hint" in res

    # 8. Skip Question (HR Control)
    print("\n8. Testing POST /api/interviews/{interview_id}/questions/skip ...")
    status, res = post(f"/api/interviews/{interview_id}/questions/skip")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")
    assert status == 200

    # 9. Finish Coding Session
    print("\n9. Testing POST /api/interviews/{interview_id}/coding/finish ...")
    status, res = post(f"/api/interviews/{interview_id}/coding/finish")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")
    assert status == 200
    assert res["current_stage"] == "CODE_REVIEW"

    print("\nALL HTTP API VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
