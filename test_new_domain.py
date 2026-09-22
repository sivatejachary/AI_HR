import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

FRONTEND_URL = "https://ai-hr-nine.vercel.app"
BACKEND_URL = "https://ai-hrs.onrender.com"

print("==================================================")
print("   TESTING NEW FRONTEND DOMAIN: ai-hr-nine.vercel.app")
print("==================================================\n")

routes = ["/", "/candidates", "/workflows", "/settings", "/jobs", "/evaluations"]

for r in routes:
    url = f"{FRONTEND_URL}{r}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            print(f"  [OK {resp.status}] Frontend Route: {r} -> {url}")
    except Exception as e:
        print(f"  [FAIL] Frontend Route: {r} -> Error: {e}")

# Check Backend API & PostgreSQL DB
try:
    with urllib.request.urlopen(f"{BACKEND_URL}/health", context=ctx, timeout=10) as resp:
        print(f"\n  [OK {resp.status}] Backend API Health: {resp.read().decode('utf-8')}")
    with urllib.request.urlopen(f"{BACKEND_URL}/health/database", context=ctx, timeout=10) as resp:
        print(f"  [OK {resp.status}] PostgreSQL DB Health: {resp.read().decode('utf-8')}")
except Exception as e:
    print(f"  [FAIL] Backend/DB Health Error: {e}")
