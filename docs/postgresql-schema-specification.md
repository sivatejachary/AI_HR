# PostgreSQL Database Schema & Domain Specification

## Architecture Overview
Recruitment Pro uses a single PostgreSQL database instance (`hrs_n0h4` on Render) as the **Single Source of Truth** across all 42 application domain entities.

- **Primary Keys**: PostgreSQL `UUID` standard (`gen_random_uuid()` / `uuid-ossp`).
- **Timestamps**: `TIMESTAMPTZ` (`DateTime(timezone=True)`).
- **Flexible Data & Integrations**: PostgreSQL native `JSONB`.
- **Financial & Metrics**: `NUMERIC` with precise precision/scale.
- **Audit Trails**: Append-only log history.

---

## Complete Table Schema Reference

```
+-------------------------------------------------------------------------------------------------+
|                                 RECRUITMENT PRO POSTGRESQL SCHEMA                               |
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|  [Organizations] -----> [Users & RBAC] -----> [Jobs] -----> [Hiring Workflows]                  |
|         |                   |                   |                   |                           |
|         v                   v                   v                   v                           |
|  [Google/Integrations] [User Sessions]    [Job Dist & Skills]  [Workflow Steps & Conditions]     |
|                                                 |                   |                           |
|                                                 v                   v                           |
|  [Candidates] ----------------------------> [Applications] ----> [Candidate Workflows]          |
|    |                                            |                   |                           |
|    +--> [Candidate Profiles & Skills]           +--> [Screenings]   +--> [AI & Voice Calls]     |
|    +--> [Experience & Education]                +--> [Interviews]   +--> [Meeting Platforms]    |
|    +--> [Documents & Extractions]               +--> [Evaluations]  +--> [Coding Sessions]      |
|                                                 +--> [Decisions]   +--> [Offers & Onboarding]  |
|                                                                                                 |
+-------------------------------------------------------------------------------------------------+
```

---

## Domain Table Groups Summary

### 1. Organizations & RBAC (8 Tables)
- `organizations`: Primary tenant record (name, slug, legal_name, timezone, settings JSONB).
- `organization_settings`: Key-value configuration scoped by tenant.
- `users`: User profiles with password hashes, role assignment, and last login.
- `roles`: Role definitions (`SUPER_ADMIN`, `ORG_ADMIN`, `HR_ADMIN`, `RECRUITER`, `HIRING_MANAGER`, `INTERVIEWER`, `VIEWER`).
- `permissions`: Fine-grained permission rules (`resource` + `action`).
- `user_roles`: User to Role mapping junction.
- `role_permissions`: Role to Permission mapping junction.
- `sessions`: User authentication refresh token hashes and IP tracking.

### 2. Jobs & Sourcing (6 Tables)
- `jobs`: Job opening specifications, salary range, openings, and status.
- `job_skills`: Skill requirements, weights, and minimum experience.
- `job_locations`: Physical and remote workplace locations.
- `job_questions`: Custom application form screening questions.
- `job_distributions`: Job board syndication status (LinkedIn, Indeed, Naukri).
- `job_distribution_events`: Syndication activity and webhook audit history.

### 3. Hiring Workflows (4 Tables)
- `hiring_workflows`: Master workflow definitions and templates.
- `hiring_workflow_versions`: Version-controlled snapshots of hiring processes.
- `workflow_steps`: Ordered execution steps (Screening, Voice Call, AI Interview, Coding, Offer).
- `workflow_step_conditions`: Conditional branching rules and expressions.

### 4. Candidates & Profiles (6 Tables)
- `candidates`: Master candidate identity, email, phone, location, total experience.
- `candidate_profiles`: Extended profile metadata (links, salary expectations, notice period).
- `candidate_skills`: Extracted candidate skill proficiencies and experience.
- `candidate_experience`: Work history timeline.
- `candidate_education`: Academic qualifications.
- `candidate_links`: Social links (LinkedIn, GitHub, Portfolio).

### 5. Applications & Candidate Workflows (5 Tables)
- `applications`: Job application binding candidate to job with UNIQUE constraint.
- `application_sources`: Application attribution tracking.
- `application_events`: Lifecycle transition log.
- `candidate_workflows`: Active candidate workflow execution pinned to a specific version.
- `candidate_workflow_steps`: Step-level execution tracking, attempt counts, and status.

### 6. Documents & Resume Parsing (3 Tables)
- `documents`: Document file metadata, storage keys, mime types, and checksums.
- `document_versions`: Revision history for stored documents.
- `document_extractions`: Structured JSONB extractions from AI resume parsers.

### 7. AI Screening & Ingestion (5 Tables)
- `screenings`: Resume screening session records.
- `screening_results`: AI match score, recommendation, strengths, and gaps.
- `screening_evidence`: Supporting textual evidence for screening decisions.
- `ingestion_events`: Raw candidate ingestion payload logs from webhooks.
- `ingestion_errors`: Error tracking and retry counts for failed ingestion events.

### 8. Google Workspace Integrations (6 Tables)
- `google_integrations`: Encrypted OAuth tokens, scopes, and connection status.
- `google_forms`: Linked Google Form IDs, responder URLs, and edit links.
- `google_form_fields`: Question definitions synced with Google Forms API v1.
- `google_form_responses`: Candidate response payloads ingested from Google Forms.
- `google_sheets`: Linked Google Sheets for candidate tracking.
- `google_sheet_rows`: Row-level data ingested from Google Sheets.

### 9. AI HR Voice Calling (4 Tables)
- `calls`: ElevenLabs voice screening calls with conversation IDs and status.
- `call_attempts`: Outbound call retry attempts and failure reasons.
- `call_transcripts`: Textual transcripts and speaker turn JSON.
- `call_events`: Real-time call state change webhooks.

### 10. Interviews, Availability & Calendar (4 Tables)
- `interviews`: Scheduled interview events, candidate/job mapping, and meeting status.
- `interview_availability`: Candidate and interviewer free/busy time slots.
- `calendar_events`: Google Calendar / Outlook external event mappings.
- `interview_followups`: AI follow-up question linkage.

### 11. Interview Sessions, Questions & Answers (4 Tables)
- `interview_sessions`: Live interactive AI interview sessions.
- `interview_questions`: Technical & behavioral questions generated by AI Brain.
- `interview_answers`: Candidate responses, transcript segments, and scores.
- `interview_events`: Live meeting events (candidate joined, screen share, human takeover).

### 12. Meeting Platforms & Coding Sessions (7 Tables)
- `meeting_sessions`: Google Meet, Zoom, or Teams conference instances.
- `meeting_participants`: Participant join/leave audit log.
- `meeting_events`: Media and conference webhooks.
- `coding_problems`: Coding challenge specifications and constraints.
- `coding_sessions`: Candidate code execution and screen-share monitoring.
- `coding_events`: Live coding state transitions.
- `coding_observations`: AI observations from authorized screen-share sessions.

### 13. Evaluations & HR Decisions (8 Tables)
- `interview_evaluations`: Comprehensive interview scoring, strengths, and red flags.
- `evaluation_competencies`: Skill competency scores on 1-5 scale.
- `evaluation_question_results`: Per-question depth, correctness, and evidence.
- `evaluation_evidence`: Textual citations backing evaluation scores.
- `evaluation_project_verification`: Verification of candidate project claims.
- `evaluation_jd_alignment`: Candidate evidence match against job requirements.
- `candidate_decisions`: HR decision record (Advance, Hold, Reject, Request Interview).
- `hiring_decisions`: System hiring decision record.

### 14. Offers, Verification & Onboarding (12 Tables)
- `offers`: Formal employment offer terms, salary, and expiry dates.
- `offer_versions`: Offer revision history.
- `offer_documents`: Linked offer letters and PDF documents.
- `offer_events`: Offer lifecycle audit log (sent, accepted, declined).
- `verification_cases`: Background check cases.
- `verification_checks`: Individual verification checks (employment, criminal, education).
- `verification_documents`: Linked verification proof documents.
- `verification_events`: Verification state transitions.
- `onboarding_cases`: Candidate onboarding instances.
- `onboarding_tasks`: Pre-boarding and day-one task assignments.
- `onboarding_documents`: Onboarding compliance documentation.
- `onboarding_events`: Onboarding progress events.

### 15. System Automations, RAG Knowledge & Security (11 Tables)
- `automation_integrations`: n8n workflow engine connection definitions.
- `automation_runs`: n8n execution history.
- `automation_events`: Workflow trigger logs.
- `ai_runs`: AI agent execution sessions (LLM prompts & responses).
- `ai_tool_calls`: AI function calls and tool execution results.
- `notifications`: Dispatch logs for candidate and HR notifications.
- `notification_templates`: System message templates.
- `notification_deliveries`: Delivery provider receipts (Gmail, SendGrid, Twilio).
- `audit_logs`: Append-only system activity log.
- `idempotency_keys`: Event deduplication cache (Google Forms, ElevenLabs, n8n).
- `knowledge_collections`: Knowledge base collections for vector search.
- `knowledge_documents`: Source documents indexed in RAG system.
- `knowledge_chunks`: Text chunks mapped to Qdrant vector point IDs.
- `security_events`: Security and authentication audit log.
