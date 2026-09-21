# Infrastructure & Configuration Audit Document

**Project:** Recruitment Pro  
**Date:** September 21, 2026  
**Auditor:** Antigravity AI Agent  
**Purpose:** Comprehensive audit of database connections, internal/external URL routing, environment variables, CORS, webhooks, and third-party integrations prior to central infrastructure consolidation.

---

## 1. Database Architecture Audit

| Property | Current Configuration | Target Production Configuration |
| :--- | :--- | :--- |
| **Primary Database** | SQLite (`sqlite:///./sql_app.db`) as fallback / PostgreSQL when `DATABASE_URL` set | **PostgreSQL (Single Source of Truth)** via `DATABASE_URL` |
| **Driver / Connection** | SQLAlchemy ORM with `create_engine` | `postgresql+psycopg://USER:PASS@HOST:PORT/DB` |
| **Tenant Isolation** | `organization_id` column on domain models | Preserved & enforced |
| **Tables Defined** | `organizations`, `users`, `jobs`, `job_distributions`, `candidates`, `applications`, `hiring_workflows`, `hiring_workflow_versions`, `workflow_steps`, `candidate_workflows`, `workflow_events`, `workflow_execution_logs`, `screening_results`, `calls`, `interviews`, `interview_sessions`, `interview_questions`, `evaluations`, `offers`, `onboarding_tasks`, `hiring_decisions`, `integrations`, `forms`, `audit_logs` | All 24 tables mapped to single PostgreSQL instance |

---

## 2. URL & Network Architecture Audit

### 2.1 Current URLs Identified in Codebase
* **Backend Base URL:** `http://localhost:8000` (FastAPI)
* **Frontend Base URL:** `http://localhost:3000` (Next.js 14)
* **n8n Cloud Webhook Base URL:** `https://shivateja123.app.n8n.cloud/webhook/`
* **Google OAuth Callback URL:** `http://localhost:8000/api/v1/integrations/google/callback`
* **Google OAuth Client ID:** `186843356614-2k28sqllqgf4fo2nk38mspuipnfssl9q.apps.googleusercontent.com`
* **ElevenLabs Webhook Route:** `POST /api/v1/calls/elevenlabs-webhook` & `/api/ai-interview/{interview_id}/elevenlabs-post-call`

### 2.2 Hardcoded & Localhost References to Consolidate
1. **`frontend/src/lib/api.ts`**:
   - `const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';`
   - Hardcoded fetch URLs pointing to `http://localhost:8000/...` in phase-specific methods (lines 79, 84, 85, 86, 88, 89, 90, 91, 92, 95, 96, 97, 100-110).
2. **`backend/app/services/google_workspace_service.py`**:
   - `GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/integrations/google/callback")`
3. **`backend/app/api/v1/google_auth_routes.py`**:
   - Hardcoded redirect fallback `http://localhost:3000/integrations?status=connected`.
4. **`backend/app/main.py`**:
   - `allow_origins=["*"]` (Needs environment variable `CORS_ORIGINS`).

---

## 3. Environment Variables Audit

### Existing Backend `.env`:
* `GOOGLE_CLIENT_ID`
* `GOOGLE_CLIENT_SECRET`
* `GOOGLE_REDIRECT_URI`
* `N8N_INTEGRATION_API_KEY`
* `SECRET_KEY`

### Missing Centralized Settings (`backend/app/core/config.py`):
- `APP_ENV` (`development` | `staging` | `production`)
- `DATABASE_URL` (`postgresql+psycopg://...`)
- `BACKEND_PUBLIC_URL` (Used for public Google OAuth callback & ElevenLabs webhooks)
- `BACKEND_INTERNAL_URL` (Used for trusted server-to-server n8n communication)
- `FRONTEND_PUBLIC_URL` (Used for post-auth browser redirects & candidate application URLs)
- `N8N_PUBLIC_URL` & `N8N_INTERNAL_URL` & `N8N_API_KEY`
- `ELEVENLABS_API_KEY`, `ELEVENLABS_AGENT_ID`, `ELEVENLABS_WEBHOOK_URL`
- `CORS_ORIGINS` (Comma-separated trusted origins)

---

## 4. Webhook & Integration Mapping

| Integration | Route Path | Communication Type | URL Config Key |
| :--- | :--- | :--- | :--- |
| **Google OAuth Callback** | `/api/v1/integrations/google/callback` | External (Public Browser Redirect) | `GOOGLE_OAUTH_REDIRECT_URI` |
| **Google Forms Ingestion** | `/api/v1/integrations/google-forms/submissions` | Internal/External Server-to-Server | `GOOGLE_FORMS_WEBHOOK_URL` |
| **ElevenLabs Webhook** | `/api/v1/calls/elevenlabs-webhook` | External (Public ElevenLabs Cloud) | `ELEVENLABS_WEBHOOK_URL` |
| **n8n Workflow Execution** | `/api/v1/workflows/execute-step` | Server-to-Server | `N8N_INTERNAL_URL` |
| **Public Candidate Apply** | `/apply/[job_id]` | Public Candidate Browser | `CANDIDATE_APPLICATION_BASE_URL` |

---

## 5. Implementation Roadmap & Modifications Required

1. **Create `backend/app/core/config.py`**: Centralized Pydantic Settings class parsing environment variables with production validation.
2. **Database Engine Consolidation (`backend/app/db/database.py`)**: Ensure PostgreSQL is used as sole source of truth when `DATABASE_URL` is set, with database health check endpoints (`/health` and `/health/database`).
3. **CORS & Startup Validation (`backend/app/main.py`)**: Restrict CORS origins via `CORS_ORIGINS` and validate URLs at startup.
4. **Admin Integration Health API (`GET /api/v1/admin/integrations/health`)**: Report connection status for PostgreSQL, n8n, Google Workspace, ElevenLabs, etc.
5. **Frontend API Client Refactoring (`frontend/src/lib/api.ts`)**: Replace all hardcoded `http://localhost:8000` URLs with `NEXT_PUBLIC_API_URL`.
6. **Environment Templates**: Create `backend/.env.example` and `frontend/.env.example`.
