# Google Workspace Integration Guide

**Project:** Recruitment Pro  
**Architecture Version:** 2.0.0  
**Single Source of Truth:** PostgreSQL (`organizations`, `users`, `jobs`, `candidates`, `applications`, `integrations`)

---

## 1. Google OAuth 2.0 Server-Side Setup

Recruitment Pro implements an enterprise server-side OAuth 2.0 authorization code flow for Google Workspace.

### Endpoints
* `GET /api/v1/integrations/google/connect` — Initiates Google OAuth consent screen.
* `GET /api/v1/integrations/google/callback` — Handles authorization code exchange for access & refresh tokens.
* `GET /api/v1/integrations/google/status` — Returns connection state, authorized email, and scope availability.
* `POST /api/v1/integrations/google/disconnect` — Revokes session and marks integration as `DISCONNECTED`.

### Environment Configuration
Configure the following in `backend/.env`:

```env
GOOGLE_CLIENT_ID=your-google-oauth-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
GOOGLE_REDIRECT_URI=https://ai-hrs.onrender.com/api/v1/integrations/google/callback
```

### OAuth Scopes Requested
- `https://www.googleapis.com/auth/forms.body`
- `https://www.googleapis.com/auth/forms.responses.readonly`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/calendar`
- `https://www.googleapis.com/auth/gmail.send`
- `https://www.googleapis.com/auth/userinfo.email`
- `https://www.googleapis.com/auth/userinfo.profile`

---

## 2. Security & Token Persistence

1. **Client Secret Privacy:** `GOOGLE_CLIENT_SECRET` is used exclusively server-side in FastAPI and is never exposed in Next.js browser bundles.
2. **Encrypted Token Persistence:** `access_token` and `refresh_token` are stored in the PostgreSQL `integrations` table with expiration tracking.
3. **Tenant Isolation:** All integration operations validate `organization_id`.
