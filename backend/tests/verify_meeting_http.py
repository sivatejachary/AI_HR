import os
BASE_URL = os.getenv("BACKEND_PUBLIC_URL", "https://ai-hrs.onrender.com")

def make_request(url, method="GET", body=None, headers=None):
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"
    
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
    print("=== STARTING PHASE 3 REAL MEETING PLATFORM INTEGRATION HTTP E2E VERIFICATION ===")
    
    # 1. Google Integration Status
    print("\n--- 1. GET GOOGLE INTEGRATION STATUS ---")
    status, g_st = make_request("/api/integrations/google/status")
    print(f"Status: {status} | Provider: {g_st.get('provider')} | Connected: {g_st.get('is_connected')}")
    assert status == 200

    # 2. Google OAuth Connect Link
    print("\n--- 2. GET GOOGLE OAUTH CONNECT LINK ---")
    status, g_conn = make_request("/api/integrations/google/connect?redirect=json")
    print(f"Status: {status} | Auth URL: {g_conn.get('auth_url')[:60]}...")
    assert status == 200

    # 3. First start a test AI Interview to have a valid interview ID
    print("\n--- 3. START TEST INTERVIEW SESSION ---")
    status, test_sess = make_request("/api/v1/interviews/ai/start-test-session", method="POST")
    print(f"Status: {status} | Interview ID: {test_sess.get('interview_id')}")
    assert status == 200
    interview_id = test_sess["interview_id"]

    # 4. Connect Meeting Bot (17-Step Join Flow)
    print("\n--- 4. CONNECT MEETING BOT (17-STEP JOIN FLOW) ---")
    status, conn_res = make_request(f"/api/interviews/{interview_id}/meeting/connect", method="POST")
    print(f"Status: {status} | Meeting Status: {conn_res.get('meeting_status')} | AI Connection: {conn_res.get('ai_connection_status')}")
    assert status == 200
    assert conn_res["meeting_status"] in ["INTERVIEW_ACTIVE", "WAITING_FOR_CANDIDATE"]

    # 5. Get Meeting Status
    print("\n--- 5. GET MEETING STATUS ---")
    status, m_st = make_request(f"/api/interviews/{interview_id}/meeting/status")
    print(f"Status: {status} | Meeting Provider: {m_st.get('meeting_provider')} | Meeting Status: {m_st.get('meeting_status')}")
    assert status == 200

    # 6. Get Meeting Participants
    print("\n--- 6. GET MEETING PARTICIPANTS ---")
    status, parts = make_request(f"/api/interviews/{interview_id}/meeting/participants")
    print(f"Status: {status} | Participant Count: {parts.get('count')}")
    assert status == 200

    # 7. Get Meeting Capabilities
    print("\n--- 7. GET MEETING CAPABILITIES ---")
    status, caps = make_request(f"/api/interviews/{interview_id}/meeting/capabilities")
    print(f"Status: {status} | Provider: {caps.get('provider_name')} | Audio Send: {caps.get('audioSend')} | Audio Recv: {caps.get('audioReceive')}")
    assert status == 200

    # 8. Disconnect Meeting Bot
    print("\n--- 8. DISCONNECT MEETING BOT ---")
    status, disc = make_request(f"/api/interviews/{interview_id}/meeting/disconnect", method="POST")
    print(f"Status: {status} | Meeting Status: {disc.get('meeting_status')} | AI Connection: {disc.get('ai_connection_status')}")
    assert status == 200
    assert disc["meeting_status"] == "ENDED"

    print("\n=== ALL PHASE 3 MEETING INTEGRATION LIVE HTTP E2E TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    main()
