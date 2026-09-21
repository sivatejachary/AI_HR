# Database Architecture & Single Source of Truth Model

## Core Philosophy
PostgreSQL serves as the single source of truth for Recruitment Pro. No SQLite fallback, duplicate memory caches, or secondary databases are permitted.

---

## Entity Relationship Summary

```
                      +-------------------+
                      |   Organizations   |
                      +-------------------+
                               | 1
                               |
                               | *
                      +-------------------+
                      |       Users       |
                      +-------------------+
                               | 1
                               |
                               | *
                      +-------------------+
                      |       Jobs        |
                      +-------------------+
                     /   |             |   \
                   1/   1|            1|    \*
                   /     |             |     \
  +------------------+  +---------------+  +-------------------+
  | ApplicationForm  |  | HiringWorkflow|  |    Candidates     |
  +------------------+  +---------------+  +-------------------+
                                                    | 1
                                                    |
                                                    | *
                                           +-------------------+
                                           |   Applications    |
                                           +-------------------+
                                           /     |           \
                                         1/     1|            1\
                                         /       |              \
                       +-------------------+ +--------------+ +-------------------+
                       |    Interviews     | |  Call Logs   | |   Evaluations     |
                       +-------------------+ +--------------+ +-------------------+
```

---

## Database Models & Integrations Schema

### Integration Table (`integrations`)
Stores organization-level OAuth credentials, tokens, and service configurations.

| Column | Type | Constraints / Description |
|---|---|---|
| `id` | VARCHAR | Primary Key |
| `organization_id` | VARCHAR | Foreign Key -> `organizations.id` |
| `provider` | VARCHAR | Integration provider (`google`, `n8n`, `elevenlabs`) |
| `status` | VARCHAR | `connected`, `disconnected`, `expired`, `error` |
| `access_token_encrypted` | TEXT | AES encrypted OAuth Access Token |
| `refresh_token_encrypted` | TEXT | AES encrypted OAuth Refresh Token |
| `token_expires_at` | DATETIME | Token expiration timestamp |
| `scopes` | VARCHAR | OAuth scopes granted by user |
| `config_json` | TEXT | Provider-specific extra JSON settings |
| `created_at` | DATETIME | Record creation timestamp |
| `updated_at` | DATETIME | Record update timestamp |

### ApplicationForm Table (`application_forms`)
Tracks live Google Form mappings to recruitment jobs.

| Column | Type | Constraints / Description |
|---|---|---|
| `id` | VARCHAR | Primary Key |
| `job_id` | VARCHAR | Foreign Key -> `jobs.id` |
| `title` | VARCHAR | Form title |
| `public_url_slug` | VARCHAR | Unique URL slug |
| `google_form_id` | VARCHAR | Google Forms API created ID |
| `google_form_url` | VARCHAR | Edit URL for Google Form |
| `google_responder_url` | VARCHAR | Shareable submission URL for candidates |
| `form_schema_json` | TEXT | Question & field definitions JSON |
| `is_published` | BOOLEAN | Form active status |

---

## Connection Pooling & Production Settings

In `backend/app/db/database.py`:
- `pool_size`: 10 persistent connections
- `max_overflow`: 20 temporary connections under peak loads
- `pool_pre_ping`: True (automatically tests connectivity before execution, preventing stale socket errors)
- `pool_recycle`: 3600 seconds
