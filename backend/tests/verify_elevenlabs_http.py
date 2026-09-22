import os
BASE_URL = os.getenv("BACKEND_PUBLIC_URL", "https://ai-hrs.onrender.com")

def make_request(url, method="GET", body=None, headers=None):
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = "Bearer recruitment_pro_elevenlabs_secret_2026"
    
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(f"{BASE_URL}{url}", data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            return resp.status, json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        return e.code, json.loads(resp_body) if resp_body else {"error": str(e)}

def main():
    print("=== STARTING ELEVENLABS PHASE 2 LIVE HTTP E2E VERIFICATION ===")
    
    # 1. Start Test Session
    print("\n--- 1. START TEST SESSION ---")
    status, data = make_request("/api/v1/interviews/ai/start-test-session", method="POST")
    print(f"Status: {status} | Response: {data.get('status')}")
    assert status == 200, f"Expected 200, got {status}: {data}"
    interview_id = data["interview_id"]
    print(f"Interview ID: {interview_id}")
    assert "elevenlabs_session" in data
    print(f"ElevenLabs Session Signed URL: {data['elevenlabs_session']['signed_url']}")

    # 2. Tool 1: GET /api/ai-interview/{interview_id}/context
    print("\n--- 2. GET INTERVIEW CONTEXT ---")
    status, ctx = make_request(f"/api/ai-interview/{interview_id}/context")
    print(f"Candidate: {ctx.get('candidate_name')} | Job: {ctx.get('job_title')}")
    assert status == 200

    # 3. Tool 2: GET /api/ai-interview/{interview_id}/stage
    print("\n--- 3. GET CURRENT STAGE ---")
    status, stg = make_request(f"/api/ai-interview/{interview_id}/stage")
    print(f"Stage: {stg.get('stage')} | Difficulty: {stg.get('difficulty')}")
    assert status == 200

    # 4. Tool 3: POST /api/ai-interview/{interview_id}/next-question
    print("\n--- 4. GET NEXT QUESTION ---")
    status, q1 = make_request(f"/api/ai-interview/{interview_id}/next-question", method="POST", body={"reason": "start_stage"})
    print(f"Question ID: {q1.get('question_id')} | Question: {q1.get('question')}")
    assert status == 200
    q1_id = q1["question_id"]

    # 5. Tool 4: POST /api/ai-interview/{interview_id}/answer
    print("\n--- 5. SUBMIT CANDIDATE ANSWER ---")
    answer_payload = {
        "question_id": q1_id,
        "answer": "I have extensive experience building Python backend services, designing REST APIs with FastAPI, and optimizing SQL database queries.",
        "conversation_id": "conv_live_test_777"
    }
    status, ans = make_request(f"/api/ai-interview/{interview_id}/answer", method="POST", body=answer_payload)
    print(f"Answer Saved: {ans.get('saved')} | Quality: {ans.get('answer_quality')} | Next Action: {ans.get('next_action')}")
    assert status == 200

    # 6. Tool 5: POST /api/ai-interview/{interview_id}/next-action
    print("\n--- 6. GET NEXT ACTION ---")
    status, act = make_request(f"/api/ai-interview/{interview_id}/next-action", method="POST")
    print(f"Action: {act.get('action')} | Reason: {act.get('reason')}")
    assert status == 200

    # 7. Tool 6: POST /api/ai-interview/{interview_id}/event
    print("\n--- 7. LOG INTERVIEW EVENT ---")
    status, evt = make_request(f"/api/ai-interview/{interview_id}/event", method="POST", body={"event_type": "INTERRUPT_DETECTED", "metadata": {"ms": 250}})
    print(f"Event Logged: {evt.get('status')}")
    assert status == 200

    # 8. Tool 7 & 8: PAUSE & RESUME
    print("\n--- 8. PAUSE & RESUME ---")
    status, p = make_request(f"/api/ai-interview/{interview_id}/pause", method="POST")
    print(f"Paused Status: {p.get('status')}")
    assert status == 200
    status, r = make_request(f"/api/ai-interview/{interview_id}/resume", method="POST")
    print(f"Resumed Status: {r.get('status')}")
    assert status == 200

    # 9. Tool 9: COMPLETE INTERVIEW
    print("\n--- 9. COMPLETE INTERVIEW ---")
    status, c = make_request(f"/api/ai-interview/{interview_id}/complete", method="POST")
    print(f"Completed Status: {c.get('status')}")
    assert status == 200

    # 10. POST-CALL TELEMETRY
    print("\n--- 10. POST-CALL TELEMETRY WEBHOOK ---")
    tele_payload = {
        "conversation_id": "conv_live_test_777",
        "duration": 420,
        "transcript": [
            {"role": "agent", "message": "Hi Rahul, introduce yourself."},
            {"role": "user", "message": "I build scalable Python microservices."}
        ]
    }
    status, tele = make_request(f"/api/ai-interview/{interview_id}/elevenlabs-post-call", method="POST", body=tele_payload)
    print(f"Telemetry Saved: {tele.get('status')} | Duration: {tele.get('duration')}s")
    assert status == 200

    print("\n=== ALL ELEVENLABS PHASE 2 LIVE HTTP E2E TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    main()
