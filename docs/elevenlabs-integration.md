# ElevenLabs AI Voice Interview Integration

## Overview
Recruitment Pro uses ElevenLabs Conversational AI to perform automated voice screening calls and interactive interview sessions.

---

## Configuration & Architecture

- **Backend Service**: `backend/app/services/elevenlabs_service.py`
- **Environment Variables**:
  - `ELEVENLABS_API_KEY`: API authentication key.
  - `ELEVENLABS_AGENT_ID`: Agent personality ID for HR voice calls.

---

## Voice Call Workflow

1. **Initiation**:
   When an application reaches the `phone_screen` or `ai_interview` step in the hiring workflow engine, FastAPI calls `ElevenLabsService.initiate_candidate_call(candidate_id, phone_number)`.
2. **Session Webhook**:
   ElevenLabs streams conversation audio and posts real-time transcripts back to backend `/api/v1/interviews/ai/{interview_id}/elevenlabs-session`.
3. **Evaluation & Persistence**:
   Transcripts and AI scoring criteria are evaluated and saved directly to the PostgreSQL `evaluations` table.
