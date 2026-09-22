# Real Google Workspace & Google Forms OAuth 2.0 Integration

## Overview
Recruitment Pro integrates directly with Google Workspace REST APIs (Forms v1, Calendar v3, Gmail v1, Meet) using OAuth 2.0 user authorization. Fake URLs, iframe simulations, and mock form generators are strictly disallowed.

---

## OAuth Configuration

- **Google Cloud Project**: `feisty-legend-450615-n5`
- **Client ID**: `186843356614-2k28sqllqgf4fo2nk38mspuipnfssl9q.apps.googleusercontent.com`
- **Client Secret**: `[REDACTED_SET_IN_ENV]`
- **Redirect URI**: `https://ai-hrs.onrender.com/api/v1/integrations/google/callback`

### Granted Scopes
- `https://www.googleapis.com/auth/forms.body` (Create & edit Google Forms)
- `https://www.googleapis.com/auth/forms.responses.readonly` (Read responses)
- `https://www.googleapis.com/auth/calendar` (Schedule Google Meet interviews)
- `https://www.googleapis.com/auth/gmail.send` (Send candidate notification emails)

---

## Google Forms API v1 Workflow

1. **Authorization Verification**:
   When a user requests to generate a Google Form for a Job (`POST /api/v1/jobs/{job_id}/google-form`), the `GoogleWorkspaceService` checks for active Google OAuth credentials in PostgreSQL.
2. **REST Call - Form Creation**:
   - `POST https://forms.googleapis.com/v1/forms`
   - Returns valid `formId` and `responderUri`.
3. **REST Call - Question Schema Injection**:
   - `POST https://forms.googleapis.com/v1/forms/{formId}:batchUpdate`
   - Programmatically builds text questions (Full Name, Email, Phone, LinkedIn, Resume Upload, Experience).
4. **Database Persistence**:
   - `ApplicationForm` record is saved in PostgreSQL with `google_form_id`, `google_form_url`, and `google_responder_url`.

---

## Unauthenticated Behavior & Error Handling
If Google OAuth is unauthenticated or expired:
- The system returns HTTP `400 Bad Request` with `detail: "Google OAuth is not connected. Please connect your Google account in Settings/Integrations before generating Google Forms."`.
- No mock/placeholder URLs are generated.
