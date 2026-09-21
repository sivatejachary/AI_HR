const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const RAW_BACKEND_URL = API_BASE_URL.replace(/\/api\/v1\/?$/, '');

async function fetchJSON<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers
      },
      ...options
    });

    if (!res.ok) {
      throw new Error(`API error ${res.status}: ${res.statusText}`);
    }

    return await res.json();
  } catch (err) {
    console.warn(`[API Client] Fetch failed for ${endpoint}. Backend may be offline or starting up.`, err);
    throw err;
  }
}

export const api = {
  getDashboardSummary: () => fetchJSON<any>('/dashboard/summary'),

  // Jobs
  getJobs: (status?: string) => fetchJSON<any[]>(`/jobs${status ? `?status=${status}` : ''}`),
  createJob: (payload: any) => fetchJSON<any>('/jobs', { method: 'POST', body: JSON.stringify(payload) }),
  updateJobStatus: (id: string, status: string) => fetchJSON<any>(`/jobs/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }),

  // Public Apply
  applyToJob: (jobId: string, payload: any) => fetchJSON<any>(`/jobs/${jobId}/apply`, { method: 'POST', body: JSON.stringify(payload) }),

  // Applications & Candidates
  getApplications: (status?: string) => fetchJSON<any[]>(`/applications${status ? `?status=${status}` : ''}`),
  approveApplication: (id: string) => fetchJSON<any>(`/applications/${id}/approve`, { method: 'PATCH' }),
  rejectApplication: (id: string, reason?: string) => fetchJSON<any>(`/applications/${id}/reject`, { method: 'PATCH', body: JSON.stringify({ reason }) }),
  getCandidates: () => fetchJSON<any[]>('/candidates'),

  // Forms & Integrations
  getForms: () => fetchJSON<any[]>('/forms'),
  createForm: (payload: any) => fetchJSON<any>('/forms', { method: 'POST', body: JSON.stringify(payload) }),
  getIntegrations: () => fetchJSON<any[]>('/integrations'),
  getActivityLogs: () => fetchJSON<any[]>('/activity-logs'),

  // Hiring Workflows & Execution Engine
  getWorkflows: (status?: string) => fetchJSON<any[]>(`/workflows${status ? `?status=${status}` : ''}`),
  createWorkflow: (payload: any) => fetchJSON<any>('/workflows', { method: 'POST', body: JSON.stringify(payload) }),
  publishWorkflow: (id: string) => fetchJSON<any>(`/workflows/${id}/publish`, { method: 'PATCH' }),
  togglePauseWorkflow: (id: string) => fetchJSON<any>(`/workflows/${id}/toggle-pause`, { method: 'PATCH' }),
  executeWorkflowStep: (applicationId: string, event?: string) => fetchJSON<any>('/workflows/execute-step', { method: 'POST', body: JSON.stringify({ applicationId, event }) }),
  retryFailedStep: (applicationId: string) => fetchJSON<any>('/workflows/retry-step', { method: 'POST', body: JSON.stringify({ applicationId }) }),
  manualCompleteStep: (applicationId: string, action: string, reason?: string) => fetchJSON<any>('/workflows/manual-complete-step', { method: 'POST', body: JSON.stringify({ applicationId, action, reason }) }),
  getAutomationStats: (jobId?: string) => fetchJSON<any>(`/workflows/automation-stats${jobId ? `?job_id=${jobId}` : ''}`),
  getWorkflowLogs: (id: string) => fetchJSON<any[]>(`/workflows/${id}/logs`),

  // AI Interview Brain
  startInterviewSession: (candidateId: string, jobId: string, interviewId?: string) => fetchJSON<any>('/interview-brain/sessions', { method: 'POST', body: JSON.stringify({ candidateId, jobId, interviewId }) }),
  getInterviewSession: (sessionId: string) => fetchJSON<any>(`/interview-brain/sessions/${sessionId}`),
  submitInterviewAnswer: (sessionId: string, questionId: string, answerText: string) => fetchJSON<any>(`/interview-brain/sessions/${sessionId}/answer`, { method: 'POST', body: JSON.stringify({ questionId, answerText }) }),
  updateScreenConsent: (sessionId: string, granted: boolean) => fetchJSON<any>(`/interview-brain/sessions/${sessionId}/consent`, { method: 'POST', body: JSON.stringify({ granted }) }),
  completeInterviewSession: (sessionId: string, userCode?: string, codeTestResults?: any) => fetchJSON<any>(`/interview-brain/sessions/${sessionId}/complete`, { method: 'POST', body: JSON.stringify({ userCode, codeTestResults }) }),
  approveInterviewEvaluation: (sessionId: string, approverName?: string) => fetchJSON<any>(`/interview-brain/sessions/${sessionId}/approve`, { method: 'POST', body: JSON.stringify({ approverName }) }),

  // Phase 1 Specific AI Interview Brain Endpoints (/interviews/ai/*)
  startAIInterview: (candidateId: string, jobId: string, interviewId?: string) => fetchJSON<any>('/interviews/ai/start', { method: 'POST', body: JSON.stringify({ candidate_id: candidateId, job_id: jobId, interview_id: interviewId }) }),
  getAIInterviewState: (interviewId: string) => fetchJSON<any>(`/interviews/ai/${interviewId}`),
  getAIInterviewContext: (interviewId: string) => fetchJSON<any>(`/interviews/ai/${interviewId}/context`),
  getAINextQuestion: (interviewId: string) => fetchJSON<any>(`/interviews/ai/${interviewId}/next-question`, { method: 'POST' }),
  submitAIAnswer: (interviewId: string, questionId: string, answerText: string) => fetchJSON<any>(`/interviews/ai/${interviewId}/answer`, { method: 'POST', body: JSON.stringify({ question_id: questionId, answer_text: answerText }) }),
  pauseAIInterview: (interviewId: string) => fetchJSON<any>(`/interviews/ai/${interviewId}/pause`, { method: 'POST' }),
  resumeAIInterview: (interviewId: string) => fetchJSON<any>(`/interviews/ai/${interviewId}/resume`, { method: 'POST' }),
  completeAIInterview: (interviewId: string) => fetchJSON<any>(`/interviews/ai/${interviewId}/complete`, { method: 'POST' }),

  // Phase 2 ElevenLabs & Developer Test Mode
  startTestAIInterview: () => fetchJSON<any>('/interviews/ai/start-test-session', { method: 'POST' }),
  getElevenLabsSession: (interviewId: string) => fetch(`${RAW_BACKEND_URL}/api/ai-interview/${interviewId}/elevenlabs-session`).then(r => r.json()),

  // Real Meeting Platform Integration & Google OAuth
  getGoogleIntegrationStatus: () => fetchJSON<any>('/integrations/google/status'),
  connectGoogleOAuth: () => { window.location.href = `${API_BASE_URL}/integrations/google/connect`; },
  disconnectGoogleOAuth: () => fetchJSON<any>('/integrations/google/disconnect', { method: 'POST' }),
  createJobGoogleForm: (jobId: string) => fetchJSON<any>(`/jobs/${jobId}/google-form`, { method: 'POST' }),
  
  connectMeetingBot: (interviewId: string) => fetch(`${RAW_BACKEND_URL}/api/interviews/${interviewId}/meeting/connect`, { method: 'POST' }).then(r => r.json()),
  disconnectMeetingBot: (interviewId: string) => fetch(`${RAW_BACKEND_URL}/api/interviews/${interviewId}/meeting/disconnect`, { method: 'POST' }).then(r => r.json()),
  getMeetingStatus: (interviewId: string) => fetch(`${RAW_BACKEND_URL}/api/interviews/${interviewId}/meeting/status`).then(r => r.json()),
  getMeetingParticipants: (interviewId: string) => fetch(`${RAW_BACKEND_URL}/api/interviews/${interviewId}/meeting/participants`).then(r => r.json()),
  getMeetingCapabilities: (interviewId: string) => fetch(`${RAW_BACKEND_URL}/api/interviews/${interviewId}/meeting/capabilities`).then(r => r.json()),

  // Phase 5 Evaluation & HR Decision API Endpoints
  getEvaluation: (interviewId: string) => fetch(`${RAW_BACKEND_URL}/api/interviews/ai/${interviewId}/evaluation`).then(r => r.json()),
  triggerEvaluation: (interviewId: string, version?: string) => fetch(`${RAW_BACKEND_URL}/api/interviews/ai/${interviewId}/evaluate`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ evaluation_version: version || 'v1.0' }) }).then(r => r.json()),
  submitHRDecision: (interviewId: string, decision: string, reason: string) => fetch(`${RAW_BACKEND_URL}/api/interviews/${interviewId}/decision`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ decision, reason }) }).then(r => r.json()),

  // Phase 6 Hiring Workflow Execution Engine API Endpoints
  validateWorkflow: (workflowId: string) => fetch(`${RAW_BACKEND_URL}/api/workflows/${workflowId}/validate`, { method: 'POST' }).then(r => r.json()),
  simulateWorkflow: (workflowId: string) => fetch(`${RAW_BACKEND_URL}/api/workflows/${workflowId}/simulate`, { method: 'POST' }).then(r => r.json()),
  publishWorkflowVersion: (workflowId: string) => fetch(`${RAW_BACKEND_URL}/api/workflows/${workflowId}/publish`, { method: 'POST' }).then(r => r.json()),
  getWorkflowTemplates: () => fetch(`${RAW_BACKEND_URL}/api/workflows/templates`).then(r => r.json()),
  getWorkflowAnalytics: (workflowId: string) => fetch(`${RAW_BACKEND_URL}/api/workflows/${workflowId}/analytics`).then(r => r.json()),
  startCandidateWorkflow: (candidateId: string, jobId: string, workflowId?: string) => fetch(`${RAW_BACKEND_URL}/api/candidates/${candidateId}/workflow/start`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ jobId, workflowId }) }).then(r => r.json()),
  getCandidateWorkflow: (candidateId: string) => fetch(`${RAW_BACKEND_URL}/api/candidates/${candidateId}/workflow`).then(r => r.json()),
  getCandidateWorkflowTimeline: (candidateId: string) => fetch(`${RAW_BACKEND_URL}/api/candidates/${candidateId}/workflow/timeline`).then(r => r.json()),
  approveCandidateStep: (candidateId: string, reason?: string) => fetch(`${RAW_BACKEND_URL}/api/candidates/${candidateId}/workflow/approve`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ reason }) }).then(r => r.json()),
  rejectCandidateStep: (candidateId: string, reason?: string) => fetch(`${RAW_BACKEND_URL}/api/candidates/${candidateId}/workflow/reject`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ reason }) }).then(r => r.json()),
  toggleCandidateTakeover: (candidateId: string, isTakeover: boolean) => fetch(`${RAW_BACKEND_URL}/api/candidates/${candidateId}/workflow/takeover`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ is_human_takeover: isTakeover }) }).then(r => r.json())
};
