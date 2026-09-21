# Google Forms & n8n Ingestion Integration Guide

**Project:** Recruitment Pro  
**Integration Pattern:** Job $\rightarrow$ Google Form $\rightarrow$ Google Responses $\rightarrow$ n8n $\rightarrow$ Recruitment Pro API $\rightarrow$ PostgreSQL

---

## 1. Creating Google Form from Job

1. Navigate to **Jobs Management** (`/jobs`).
2. Select target Job position (e.g. `AI/ML Engineer`).
3. Click **[ Create Application Form ]**.
4. Recruitment Pro generates a Google Form containing default candidate fields + job-specific questions:
   - Full Name *
   - Email *
   - Phone *
   - Resume (Text / Link) *
   - Total Experience (Years) *
   - Current Location *
   - Primary Skills *
   - Notice Period (Days)
   - Expected Salary
   - LinkedIn Profile
   - GitHub / Portfolio
   - Consent to Process Data *
   - Dynamic Job Questions (derived from `Job.preferred_skills`)

---

## 2. Response Ingestion Endpoint (`POST /api/v1/integrations/google-forms/submissions`)

n8n Cloud posts candidate responses to Recruitment Pro:

### Request Header
```http
Authorization: Bearer <N8N_INTEGRATION_API_KEY>
Content-Type: application/json
```

### Request Payload
```json
{
  "google_form_id": "1FAIpQLSe_1789890309640_job1",
  "google_response_id": "resp-987654321",
  "job_id": "job-1789890309640",
  "name": "Test Candidate AI Engineer",
  "email": "candidate.ai@test.com",
  "phone": "+919876543210",
  "location": "Hyderabad",
  "years_experience": 3.5,
  "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "RAG"],
  "resume_text": "3.5 years experience building production LLMs and FastAPI backend systems."
}
```

---

## 3. Idempotency & Database Persistence

1. **Idempotency Check:** Checks `(google_form_id, google_response_id)` key. If duplicate, returns `ALREADY_PROCESSED` without creating duplicate records.
2. **PostgreSQL Storage:** Single source of truth updates `Candidate`, `Application`, `CandidateWorkflow`, and `WorkflowEvent`.
3. **Workflow Continuation:** Automatically triggers `HiringWorkflowEngine` (AI Resume Screening $\rightarrow$ Shortlisting $\rightarrow$ ElevenLabs Voice Call $\rightarrow$ Google Calendar / Meet Scheduling).
