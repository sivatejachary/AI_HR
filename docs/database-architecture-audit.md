# Comprehensive Database Architecture & Schema Audit

## Executive Summary
This document provides an exhaustive audit of the Recruitment Pro codebase, SQLAlchemy models, database migrations, and integration points against the target PostgreSQL Single Source of Truth architecture specifications.

---

## 1. Current State vs. Target Specification Matrix

| Domain Category | Target Tables Required | Existing Model Status | Gaps / Required Enhancements |
|---|---|---|---|
| **Organizations & Settings** | `organizations`, `organization_settings` | `organizations` present | Missing `organization_settings`, missing TIMESTAMPTZ, missing slug/status indexes. |
| **RBAC & Auth Sessions** | `users`, `roles`, `permissions`, `user_roles`, `role_permissions`, `sessions` | `users` present | Missing `roles`, `permissions`, `user_roles`, `role_permissions`, `sessions`. `users` needs FK to `roles`, TIMESTAMPTZ, and email_verified_at. |
| **Jobs & Distribution** | `jobs`, `job_skills`, `job_locations`, `job_questions`, `job_distributions`, `job_distribution_events` | `jobs`, `job_distributions` present | Missing `job_skills`, `job_locations`, `job_questions`, `job_distribution_events`. Need UUID FKs and NUMERIC salary/experience. |
| **Hiring Workflows** | `hiring_workflows`, `hiring_workflow_versions`, `workflow_steps`, `workflow_step_conditions` | `hiring_workflows`, `hiring_workflow_versions`, `workflow_steps` present | Missing `workflow_step_conditions`. Need version pinning on workflow execution. |
| **Candidates & Profiles** | `candidates`, `candidate_profiles`, `candidate_skills`, `candidate_experience`, `candidate_education`, `candidate_links` | `candidates` present | Missing `candidate_profiles`, `candidate_skills`, `candidate_experience`, `candidate_education`, `candidate_links`. |
| **Applications & Tracking** | `applications`, `application_sources`, `application_events` | `applications` present | Missing `application_sources`, `application_events`. `applications` needs UNIQUE(candidate_id, job_id). |
| **Candidate Workflows** | `candidate_workflows`, `candidate_workflow_steps`, `workflow_events` | `candidate_workflows`, `candidate_workflow_steps`, `workflow_events` present | Enhance with `workflow_version_id` FK pinning and attempt tracking. |
| **Document Management** | `documents`, `document_versions`, `document_extractions` | None present | Missing complete document storage, checksum, and AI extraction schema. |
| **AI Resume Screening** | `screenings`, `screening_results`, `screening_evidence` | `screening_results` present | Missing parent `screenings` session table and `screening_evidence`. |
| **Google Workspace & Integrations** | `google_integrations`, `google_forms`, `google_form_fields`, `google_form_responses`, `google_sheets`, `google_sheet_rows` | `integrations`, `forms` present | Needs dedicated `google_integrations`, `google_forms`, `google_form_fields`, `google_form_responses`, `google_sheets`, `google_sheet_rows`. |
| **Data Ingestion** | `ingestion_events`, `ingestion_errors` | None present | Missing ingestion tracing for webhooks, Google Forms, Sheets, LinkedIn, Indeed. |
| **AI Voice Calls** | `calls`, `call_attempts`, `call_transcripts`, `call_events` | `calls` present | Missing `call_attempts`, `call_transcripts`, `call_events`. `conversation_id` requires unique index. |
| **Interviews & Availability** | `interviews`, `interview_availability`, `calendar_events` | `interviews` present | Missing `interview_availability`, `calendar_events`. Need TIMESTAMPTZ scheduled_start/end. |
| **Interview Sessions & Q&A** | `interview_sessions`, `interview_questions`, `interview_answers`, `interview_followups`, `interview_events` | `interview_sessions`, `interview_questions`, `interview_answers`, `interview_events` present | Missing `interview_followups`. Enhance stage & question sequence tracking. |
| **Meeting Platforms** | `meeting_sessions`, `meeting_participants`, `meeting_events` | `interviews` embedded fields present | Missing dedicated `meeting_sessions`, `meeting_participants`, `meeting_events` tables. |
| **Coding Interviews** | `coding_problems`, `coding_sessions`, `coding_events`, `coding_observations` | `coding_problems`, `coding_sessions` present | Missing `coding_events`, `coding_observations`. Strict screen-share data protection rules. |
| **Evaluations & Alignment** | `interview_evaluations`, `evaluation_competencies`, `evaluation_question_results`, `evaluation_evidence`, `evaluation_project_verification`, `evaluation_jd_alignment` | `interview_evaluations`, `evaluation_competencies`, `evaluation_question_results`, `evaluation_jd_alignment`, `evaluation_project_verification` present | Missing `evaluation_evidence`. Enhance with standard evaluation status codes. |
| **HR Decisions** | `candidate_decisions` | `hiring_decisions` present | Rename/align with `candidate_decisions` table contract. |
| **Offers & Management** | `offers`, `offer_versions`, `offer_documents`, `offer_events` | `offers` present | Missing `offer_versions`, `offer_documents`, `offer_events`. |
| **Background Verification** | `verification_cases`, `verification_checks`, `verification_documents`, `verification_events` | None present | Missing background check case tracking, checks, documents, and events. |
| **Onboarding** | `onboarding_cases`, `onboarding_tasks`, `onboarding_documents`, `onboarding_events` | `onboarding_tasks` present | Missing parent `onboarding_cases`, `onboarding_documents`, `onboarding_events`. |
| **Automation & AI Runs** | `automation_integrations`, `automation_runs`, `automation_events`, `ai_runs`, `ai_tool_calls` | None present | Missing n8n & AI agent execution tracking tables. |
| **Notifications** | `notifications`, `notification_templates`, `notification_deliveries` | None present | Missing notification dispatch & template tracking schema. |
| **Audit Logs & Idempotency** | `audit_logs`, `idempotency_keys`, `security_events` | `audit_logs` present | Missing `idempotency_keys` and `security_events`. `audit_logs` must be append-only. |
| **Knowledge & RAG** | `knowledge_collections`, `knowledge_documents`, `knowledge_chunks` | None present | Missing PostgreSQL metadata tracking for Qdrant vector point references. |

---

## 2. Technical Incompatibilities to Resolve

1. **ID Data Types**: String Primary Keys (`String`) must be transitioned to standard PostgreSQL `UUID` (`UUID(as_uuid=True)` with `uuid_generate_v4()` / `gen_random_uuid()` defaults) for all domain entities.
2. **Timestamp Standards**: Replace naive `DateTime` (`DateTime, default=datetime.utcnow`) with timezone-aware `TIMESTAMPTZ` (`DateTime(timezone=True)`).
3. **JSON Storage**: Standardize `JSON` columns to PostgreSQL native `JSONB` for optimized indexing and querying performance.
4. **Foreign Key Integrity**: Ensure all parent-child relationships enforce explicit Foreign Key constraints (`ForeignKey("table.id")`) with appropriate `ON DELETE` rules.
5. **Database Indexing**: Add missing indexes across high-traffic lookup columns (`organization_id`, `email`, `status`, `candidate_id`, `job_id`, `application_id`, `created_at`).
