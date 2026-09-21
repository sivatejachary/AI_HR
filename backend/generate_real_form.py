import urllib.request
import json

BASE_URL = "http://localhost:8000/api/v1"

def generate_form():
    # 1. Create Real Job
    job_payload = {
        "title": "AI/ML Lead Architect",
        "department": "Artificial Intelligence",
        "employmentType": "Full-time",
        "workplaceType": "HYBRID",
        "location": "Hyderabad, India",
        "minExperience": 4,
        "maxExperience": 8,
        "openings": 1,
        "description": "We are hiring an AI/ML Lead Architect to design production LLM, RAG, vector search, and multi-agent AI systems.",
        "responsibilities": "Design scalable RAG pipelines, FastAPI services, vector databases, model deployment, and cloud AI infrastructure.",
        "requirements": "Python, FastAPI, PostgreSQL, Redis, Machine Learning, LLM, RAG, Docker, Qdrant, AWS",
        "preferredSkills": ["Python", "FastAPI", "PostgreSQL", "Redis", "RAG", "LangChain", "Qdrant", "AWS"],
        "status": "PUBLISHED"
    }

    req = urllib.request.Request(
        f"{BASE_URL}/jobs",
        data=json.dumps(job_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        job_res = json.loads(resp.read().decode("utf-8"))

    job_id = job_res["job_id"]
    print(f"Created Real Job: {job_id}")

    # 2. Generate Real Form for the Job
    req_form = urllib.request.Request(
        f"{BASE_URL}/jobs/{job_id}/google-form",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req_form) as resp_form:
            form_res = json.loads(resp_form.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return {}

    # 3. Output Form Generation Details
    result = {
        "job_id": job_id,
        "job_title": job_payload["title"],
        "department": job_payload["department"],
        "location": job_payload["location"],
        "google_form_id": form_res.get("google_form_id"),
        "google_form_edit_url": form_res.get("google_form_url"),
        "google_form_responder_url": form_res.get("google_responder_url"),
        "internal_apply_url": f"http://localhost:3000/apply/{job_id}",
        "status": form_res.get("status")
    }

    print("\n============================================================")
    print("   REAL APPLICATION FORM GENERATED SUCCESSFULLY")
    print("============================================================")
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    generate_form()
