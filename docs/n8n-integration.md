# n8n Workflow Automation Engine Integration

## Overview
Recruitment Pro connects with **n8n** to drive event-based automated recruitment pipelines (e.g. form submission webhooks, candidate auto-screening, calendar scheduling triggers, and AI interview triggers).

---

## Webhook Architecture

- **Public n8n Cloud Instance**: `https://shivateja123.app.n8n.cloud`
- **Internal Server-to-Server**: `http://localhost:5678`

### Webhook Flow: Candidate Submission -> AI Screening
```
+------------------+         +------------------+         +------------------+
|  Google Form /   |  POST   |   n8n Webhook    |  POST   |  FastAPI Backend |
| External Form    | ------> |  Receiver Node   | ------> | Webhook Endpoint |
+------------------+         +------------------+         +------------------+
                                                                   |
                                                                   v
                                                          PostgreSQL Database
                                                          (Application Created)
```

---

## Endpoint Contracts

- **Google Form Webhook Sync**: `POST /api/v1/integrations/google-forms/submissions`
  - Body Payload:
    ```json
    {
      "form_id": "google_form_id_str",
      "candidate_name": "Jane Doe",
      "candidate_email": "jane@example.com",
      "candidate_phone": "+1234567890",
      "answers": {
        "Years of Experience": "5",
        "LinkedIn": "https://linkedin.com/in/janedoe"
      }
    }
    ```
  - Behavior: Creates/updates `Candidate` and `Application` in PostgreSQL, attaches responses, and triggers active job workflow execution.
