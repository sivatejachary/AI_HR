# Infrastructure & Dual-URL Architecture Configuration

## Executive Overview
Recruitment Pro uses a dual-network configuration pattern separating server-to-server internal networking from external public browser and webhook endpoints.

```
+-----------------------------------------------------------------------+
|                           INTERNAL NETWORK                            |
|                                                                       |
|  +-------------------+               +-----------------------------+  |
|  |  FastAPI Backend  | <-----------> |  PostgreSQL Single DB       |  |
|  |  (Internal: 8000) |               |  (Port: 5432)               |  |
|  +-------------------+               +-----------------------------+  |
|            ^                                    ^                     |
|            | internal API                       | DB connection       |
|            v                                    |                     |
|  +-------------------+                          |                     |
|  |    n8n Engine     | -------------------------+                     |
|  |  (Internal: 5678) |                                                |
|  +-------------------+                                                |
+-----------------------------------------------------------------------+
                                   |
                         Public Network & Webhooks
                                   v
+-----------------------------------------------------------------------+
|                            PUBLIC NETWORK                             |
|                                                                       |
|  +-------------------+     +------------------+   +----------------+  |
|  | Next.js Frontend  |     | External Webhook |   | Google OAuth   |  |
|  | (Public Port 3000)|     | (n8n Cloud / API)|   | Callback URI   |  |
|  +-------------------+     +------------------+   +----------------+  |
+-----------------------------------------------------------------------+
```

---

## Environment Variable Schema

### Backend (`backend/.env`)

```env
# Server & Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Database Connection (PostgreSQL Single Source of Truth)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/recruitment_pro

# Network & URL Routing Architecture
BACKEND_INTERNAL_URL=https://ai-hrs.onrender.com
BACKEND_PUBLIC_URL=https://ai-hrs.onrender.com
FRONTEND_PUBLIC_URL=https://ai-hr-nine.vercel.app
N8N_INTERNAL_URL=https://shivateja123.app.n8n.cloud
N8N_PUBLIC_URL=https://shivateja123.app.n8n.cloud

# Security & CORS
SECRET_KEY=dev_secret_key_change_in_production_32bytes_min
ENCRYPTION_KEY=32_byte_secret_key_for_encrypting_tokens!
CORS_ORIGINS=https://ai-hr-nine.vercel.app,https://ai-hrs.onrender.com

# Google Workspace Integration
GOOGLE_CLIENT_ID=186843356614-2k28sqllqgf4fo2nk38mspuipnfssl9q.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=[REDACTED_SET_IN_ENV]
GOOGLE_REDIRECT_URI=https://ai-hrs.onrender.com/api/v1/integrations/google/callback

# ElevenLabs AI Voice
ELEVENLABS_API_KEY=sk_dummy_key_for_testing
ELEVENLABS_AGENT_ID=agent_dummy_id

# n8n Automation Engine
N8N_API_KEY=n8n_dummy_api_key
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=https://ai-hrs.onrender.com/api/v1
NEXT_PUBLIC_BACKEND_URL=https://ai-hrs.onrender.com
```

---

## Security & Scoping Rules

1. **Credential Isolation**: Client secrets (`GOOGLE_CLIENT_SECRET`), DB strings, `ELEVENLABS_API_KEY`, and `N8N_API_KEY` are kept exclusively in `backend/.env` and are NEVER sent to the Next.js frontend or rendered into public bundles.
2. **CORS Enforcement**: FastAPI `CORSMiddleware` restricts cross-origin access to explicitly allowed domains (`http://localhost:3000`, `http://127.0.0.1:3000`).
3. **Encrypted Token Storage**: All OAuth access/refresh tokens are stored encrypted using standard AES symmetric token encryption (`ENCRYPTION_KEY`).
