# Google Workspace & Google Forms Integration Audit

**Project:** Recruitment Pro  
**Date:** September 20, 2026  
**Status:** Audit Complete — Architectural Gap Analysis & Implementation Plan

---

## 1. Existing System Architecture Overview

Recruitment Pro is an enterprise AI HR & Recruitment platform built with:
* **Frontend:** Next.js 14, React, Tailwind CSS, Lucide icons, and custom HR state store (`useHRStore`).
* **Backend:** FastAPI (Python), SQLAlchemy ORM, SQLite/PostgreSQL, Uvicorn server (`http://localhost:8000`).
* **Database Models:** Single source of truth database defining `Organization`, `User`, `Job`, `Candidate`, `Application`, `HiringWorkflow`, `WorkflowStep`, `Integration`, `Call`, `InterviewSession`, `AIScreeningResult`, `ApplicationForm`, and `AuditLog`.
* **Automation:** n8n Cloud integration endpoints (`shivateja123.app.n8n.cloud`) and ElevenLabs Voice AI webhooks.

---

## 2. Existing Authentication & Google Services Audit

### 2.1 Backend Google Auth Router (`app/api/v1/google_auth_routes.py`)
* **Existing Endpoints:**
  - `GET /api/integrations/google/connect` — Initiates Google OAuth 2.0 flow.
  - `GET /api/integrations/google/callback` — Handles OAuth code callback.
  - `GET /api/integrations/google/status` — Checks connection status for `Google Meet / Workspace`.
  - `POST /api/integrations/google/disconnect` — Clears connection status.
* **Existing Configuration (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`):**
  - Uses environment variables with mock fallbacks.
* **Limitations in Existing Google Auth:**
  - Standard route prefixes missing `/v1` prefix (`/api/v1/integrations/google/...`).
  - Scopes are restricted to `calendar.readonly`, `userinfo.email`, `userinfo.profile`. Missing `forms.body`, `forms.responses.readonly`, `spreadsheets`, `calendar`, `gmail.send`.
  - OAuth tokens (access_token, refresh_token, token_expires_at) were not stored in encrypted columns on the `Integration` model.

### 2.2 Database Integration Model (`app/models/domain.py`)
* **Existing `Integration` Model:**
  - Columns: `id`, `organization_id`, `category`, `platform_name`, `is_connected`, `credentials_masked`, `last_tested_at`.
* **Missing Attributes for OAuth Token Management:**
  - `user_id`, `google_account_email`, `google_subject_id`, `access_token_encrypted`, `refresh_token_encrypted`, `token_expires_at`, `scopes`, `status`, `config_json`.

### 2.3 Application Form & Job Model (`app/models/domain.py`)
* **Existing `ApplicationForm` Model:**
  - Columns: `id`, `job_id`, `title`, `public_url_slug`, `is_published`, `fields_config`, `custom_questions`, `created_at`.
* **Missing Attributes for Real Google Form Linking:**
  - `google_form_id`, `google_form_url`, `google_responder_url`, `google_sheet_id`, `google_sheet_url`.

### 2.4 Existing n8n Integration (`shivateja123.app.n8n.cloud`)
* Active n8n Cloud webhooks registered for candidate intake, call telemetry, and scheduling.
* **Missing Ingestion Endpoint:** `POST /api/v1/integrations/google-forms/submissions` authenticated via `N8N_INTEGRATION_API_KEY` with idempotency protection on `(google_form_id, google_response_id)`.

---

## 3. Missing Components Required for Phase Implementation

1. **OAuth Scope Expansion & Encrypted Token Storage:**
   - Expand Google OAuth scopes to include Forms, Sheets, Calendar (full write), Gmail, User Info.
   - Store refresh and access tokens securely using symmetric encryption (`cryptography` fernet or salted token store) in DB.
   - Standardize API routes to `/api/v1/integrations/google/*`.

2. **Google Workspace Service Layer (`app/services/google_workspace_service.py`):**
   - Google Forms API client wrapper to construct dynamic Google Forms with default + job-specific fields.
   - Google Calendar API client wrapper to check free/busy slots and create Google Meet video calls.
   - Gmail API client wrapper to send confirmation emails.

3. **Job $\rightarrow$ Google Form API Endpoint:**
   - `POST /api/v1/jobs/{job_id}/google-form` to generate a real Google Form on Google's infrastructure and link its `google_form_id` and `google_form_url` to the Job and `ApplicationForm` DB record.

4. **Secure Google Form Submission Endpoint (`POST /api/v1/integrations/google-forms/submissions`):**
   - Secured via `Authorization: Bearer <N8N_INTEGRATION_API_KEY>`.
   - Normalizes Form responses to Candidate, Application, CandidateWorkflow, and WorkflowEvent models in PostgreSQL.
   - Implements idempotency key checks `(google_form_id + google_response_id)`.

5. **Frontend UI Enhancements:**
   - Extend `/integrations` & `/settings` cards to manage Google Workspace OAuth connection (showing connected email and active services: Forms, Sheets, Calendar, Gmail).
   - Add **[ Create Google Application Form ]** button on Job detail page (`/jobs/[id]`).

---

## 4. Exact Files to be Modified / Created

### New Files to Create:
1. `backend/app/services/google_workspace_service.py` — Real Google Forms, Sheets, Calendar & Gmail API logic.
2. `docs/google-workspace-integration.md` — Full integration guide.
3. `docs/google-forms-integration.md` — Google Forms setup & n8n webhook workflow guide.
4. `docs/google-oauth-test-report.md` — Verification & E2E test report.

### Existing Files to Modify:
1. `backend/app/models/domain.py` — Add OAuth token & Google Form metadata fields to `Integration`, `Job`, and `ApplicationForm`.
2. `backend/app/api/v1/google_auth_routes.py` — Update OAuth routes under `/api/v1/integrations/google/*` with expanded scopes, state CSRF verification, and token storage.
3. `backend/app/api/v1/endpoints.py` — Add `POST /api/v1/jobs/{job_id}/google-form` and `POST /api/v1/integrations/google-forms/submissions`.
4. `frontend/src/app/(dashboard)/integrations/page.tsx` — Add Google Workspace status card with `Connect Google` button and service indicators.
5. `frontend/src/app/(dashboard)/jobs/[id]/page.tsx` — Add `Create Application Form` action calling the Google Forms API endpoint.
6. `frontend/src/lib/api.ts` — Add API client methods for Google OAuth status, Google Form creation, and n8n webhook triggers.
