import {
  Job,
  Candidate,
  Application,
  HiringWorkflow,
  Interview,
  Evaluation,
  Offer,
  OnboardingTask,
  ActivityLogItem,
  CompanyPolicy,
  AIAgentState,
  ApplicationForm,
  IntegrationItem,
  SourceAnalytics
} from '../types';

export const initialWorkflows: HiringWorkflow[] = [];

// Production Starts Empty — Zero Dummy Candidates or Fake Analytics
export const initialJobs: Job[] = [];
export const initialScreeningResults = [];
export const initialApplications: Application[] = [];
export const initialCandidates: Candidate[] = [];
export const initialForms: ApplicationForm[] = [];
export const initialEvaluations: Evaluation[] = [];
export const initialOffers: Offer[] = [];
export const initialOnboarding: OnboardingTask[] = [];
export const initialActivityLogs: ActivityLogItem[] = [];

export const initialIntegrations: IntegrationItem[] = [
  { id: 'intg-1', category: 'Job Boards', platformName: 'LinkedIn Jobs API', isConnected: false, credentialsMasked: 'client_id: Not Connected', description: 'Official LinkedIn Jobs Posting & ATS Sync Integration' },
  { id: 'intg-2', category: 'Job Boards', platformName: 'Indeed Publisher Feed', isConnected: false, credentialsMasked: 'feed_url: Not Connected', description: 'Automatic XML Feed Sync for Indeed' },
  { id: 'intg-3', category: 'Job Boards', platformName: 'Naukri Recruiter API', isConnected: false, credentialsMasked: 'key: Not Connected', description: 'Direct Job Posting & Application Sync' },
  { id: 'intg-4', category: 'Forms', platformName: 'Google Forms Integration', isConnected: false, credentialsMasked: 'oauth: Not Connected', description: 'Automated response webhooks & Candidate Database ingestion' },
  { id: 'intg-5', category: 'Forms', platformName: 'Microsoft Forms (Graph API)', isConnected: false, credentialsMasked: 'tenant: Not Connected', description: 'Power Automate & Graph API webhook ingestion' },
  { id: 'intg-6', category: 'Calling', platformName: 'ElevenLabs Voice AI', isConnected: true, credentialsMasked: 'key: ****eleven_live', description: 'Outbound voice screening call agent' },
  { id: 'intg-7', category: 'Calendar', platformName: 'Google Calendar API', isConnected: false, credentialsMasked: 'gcal_oauth: Not Connected', description: 'Automated candidate & interviewer slot booking' },
  { id: 'intg-8', category: 'Meetings', platformName: 'Google Meet / Zoom API', isConnected: false, credentialsMasked: 'zoom_jwt: Not Connected', description: 'Meeting link generation for technical interviews' },
  { id: 'intg-9', category: 'Automation', platformName: 'n8n Workflow Engine', isConnected: true, credentialsMasked: 'url: https://shivateja123.app.n8n.cloud/webhook/', description: 'Event-driven workflow execution layer (8 Active Webhooks Configured)' }
];

export const initialSourceAnalytics: SourceAnalytics[] = [
  { source: 'LinkedIn', applicationsCount: 0, screeningPassed: 0, interviewsScheduled: 0, selectedCount: 0 },
  { source: 'Naukri', applicationsCount: 0, screeningPassed: 0, interviewsScheduled: 0, selectedCount: 0 },
  { source: 'WhatsApp Sharing', applicationsCount: 0, screeningPassed: 0, interviewsScheduled: 0, selectedCount: 0 },
  { source: 'Telegram Sharing', applicationsCount: 0, screeningPassed: 0, interviewsScheduled: 0, selectedCount: 0 },
  { source: 'Career Page', applicationsCount: 0, screeningPassed: 0, interviewsScheduled: 0, selectedCount: 0 },
  { source: 'Google Forms', applicationsCount: 0, screeningPassed: 0, interviewsScheduled: 0, selectedCount: 0 }
];

export const defaultCompanyPolicy: CompanyPolicy = {
  maxCallAttempts: 3,
  workingHours: '9:00 AM - 6:00 PM EST (Mon-Fri)',
  interviewDurationMinutes: 45,
  requiredApprovals: ['HR Manager', 'Hiring Manager'],
  reminderHoursBefore: 24,
  allowedPlatforms: ['Google Meet', 'Zoom', 'Microsoft Teams'],
  candidateCommsRules: 'Strict EEOC compliance. No personal data requests during initial voice screening.',
  offerApprovalProcess: 'HR Manager approval required before offer email dispatch.'
};

export const defaultAgentState: AIAgentState = {
  isOnline: true,
  capabilities: [
    'Candidate Voice Calling (ElevenLabs)',
    'Candidate Interest & Availability Collection',
    'Automated Calendar Scheduling (n8n / GCal)',
    'Confirmation & Reminder Emails (Gmail)',
    'AI Technical Interview Execution',
    'Workflow Stage Progression'
  ],
  activeTask: 'Waiting for candidate workflow events...',
  tasksQueue: [],
  voiceId: 'Rachel (21m00Tcm4TlvDq8ikWAM)',
  lastCallTime: 'N/A'
};
