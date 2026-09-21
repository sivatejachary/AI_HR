export type Role =
  | 'SUPER_ADMIN'
  | 'ORG_ADMIN'
  | 'HR_ADMIN'
  | 'RECRUITER'
  | 'HIRING_MANAGER'
  | 'INTERVIEWER'
  | 'VIEWER';

export type JobStatus = 'DRAFT' | 'PUBLISHED' | 'PAUSED' | 'EXPIRED' | 'CLOSED';

export type WorkplaceType = 'ON_SITE' | 'HYBRID' | 'REMOTE';

export type DistributionStatus =
  | 'NOT_CONNECTED'
  | 'READY'
  | 'PUBLISHING'
  | 'PUBLISHED'
  | 'UPDATE_PENDING'
  | 'FAILED'
  | 'EXPIRED'
  | 'PAUSED';

export type ApplicationSource =
  | 'LINKEDIN'
  | 'INDEED'
  | 'NAUKRI'
  | 'FOUNDIT'
  | 'CAREER_PAGE'
  | 'AI_HR_FORM'
  | 'GOOGLE_FORM'
  | 'MICROSOFT_FORM'
  | 'CSV_IMPORT'
  | 'MANUAL';

export type ApplicationStatus =
  | 'NEW'
  | 'SCREENING'
  | 'AI_SHORTLISTED'
  | 'HR_REVIEW'
  | 'HR_APPROVED'
  | 'HR_REJECTED'
  | 'CALL_PENDING'
  | 'CALLING'
  | 'CALL_COMPLETED'
  | 'INTERVIEW_PENDING'
  | 'INTERVIEW_SCHEDULED'
  | 'INTERVIEW_COMPLETED'
  | 'SELECTED'
  | 'REJECTED'
  | 'WITHDRAWN';

export type CandidateStage =
  | 'Applied'
  | 'Screening'
  | 'HR Call'
  | 'Shortlisted'
  | 'Interview'
  | 'Evaluation'
  | 'Selected'
  | 'Offer'
  | 'Onboarding';

export type StepType =
  | 'HUMAN_ACTION'
  | 'AI_ACTION'
  | 'VOICE_CALL'
  | 'EMAIL'
  | 'SCHEDULING'
  | 'INTERVIEW'
  | 'ASSESSMENT'
  | 'APPROVAL'
  | 'CONDITION'
  | 'WAIT'
  | 'NOTIFICATION'
  | 'DOCUMENT_COLLECTION'
  | 'OFFER'
  | 'ONBOARDING';

export type OfferStatus =
  | 'DRAFT'
  | 'PENDING_APPROVAL'
  | 'APPROVED'
  | 'SENT'
  | 'ACCEPTED'
  | 'DECLINED'
  | 'EXPIRED';

export type ActorType = 'HUMAN' | 'AI' | 'SYSTEM';

export type StepCategory =
  | 'Screening'
  | 'Communication'
  | 'Assessment'
  | 'Interview'
  | 'Decision'
  | 'Other';

export type StepOwner =
  | 'HR'
  | 'Recruiter'
  | 'Hiring Manager'
  | 'Interviewer'
  | 'AI'
  | 'Other';

export type AutomationLevel = 'Manual' | 'AI-assisted' | 'Fully automated';

export type WorkflowStatus = 'Draft' | 'Published' | 'Archived';

export interface WorkflowCondition {
  id: string;
  field: string;
  operator: 'gte' | 'lte' | 'equals' | 'contains' | 'is_yes' | 'is_no';
  value: string | number;
  targetStepId?: string;
  action: 'ADVANCE' | 'REJECT' | 'HR_REVIEW' | 'HOLD';
}

export interface WorkflowStep {
  id: string;
  name: string;
  category: StepCategory;
  type: StepType;
  order: number;
  purpose?: string;
  owner: StepOwner;
  automation: AutomationLevel;
  durationMinutes?: number;
  isRequired: boolean;
  scheduleType?: 'IMMEDIATE' | 'FIXED_TIME' | 'RELATIVE';
  fixedTimestamp?: string;
  relativeDelayMinutes?: number;
  executor?: 'HUMAN_HR' | 'SYSTEM' | 'N8N' | 'ELEVENLABS' | 'AI';
  requiresApproval?: boolean;
  allowSkip?: boolean;
  questions?: Array<{ id: string; question: string; isRequired: boolean }>;
  passingScore?: number;
  conditions?: WorkflowCondition[];
  notifications?: {
    notifyCandidate: boolean;
    notifyInterviewer: boolean;
    templateId?: string;
  };
  config: {
    agent?: string;
    voice?: string;
    script?: string;
    maxAttempts?: number;
    platform?: string;
    templateId?: string;
    [key: string]: any;
  };
  isEnabled: boolean;
}

export interface HiringWorkflow {
  id: string;
  name: string;
  jobId?: string;
  jobTitle?: string;
  department?: string;
  version: number;
  status: WorkflowStatus;
  isActive: boolean;
  isPaused?: boolean;
  description: string;
  ownerName?: string;
  steps: WorkflowStep[];
  updatedAt?: string;
  createdAt: string;
}

export interface JobDistribution {
  id: string;
  jobId: string;
  platform: 'LINKEDIN' | 'INDEED' | 'NAUKRI' | 'FOUNDIT' | 'CAREER_PAGE';
  connectionStatus: 'CONNECTED' | 'NOT_CONNECTED';
  externalJobId?: string;
  publicationStatus: DistributionStatus;
  applicationUrl?: string;
  publishedAt?: string;
  expiresAt?: string;
  errorMessage?: string;
  lastSyncAt?: string;
}

export interface Job {
  id: string;
  title: string;
  department: string;
  employmentType: string;
  workplaceType: WorkplaceType;
  location: string;
  minExperience: number;
  maxExperience: number;
  salaryRange: string;
  openings: number;
  description: string;
  responsibilities: string;
  requirements: string;
  preferredSkills: string[];
  education?: string;
  certifications?: string;
  noticePeriod?: string;
  languages?: string[];
  applicationDeadline?: string;
  hiringManager: string;
  workflowId: string;
  workflowName: string;
  status: JobStatus;
  distributions: JobDistribution[];
  sourcingMethods: Array<'POST_JOB' | 'CREATE_FORM' | 'IMPORT_EXISTING'>;
  createdAt: string;
  applicantsCount: number;
}

export interface AIScreeningResult {
  id: string;
  applicationId: string;
  candidateId: string;
  matchScore: number;
  requiredSkillsMatch: Record<string, 'MATCH' | 'MISSING' | 'PARTIAL'>;
  missingRequirements: string[];
  experienceMatch: { required: string; candidate: string; isMatch: boolean };
  explanation: string;
  recommendation: 'SHORTLIST_FOR_HR_REVIEW' | 'MANUAL_REVIEW' | 'NOT_MEETING_REQ';
  screenedAt: string;
}

export interface Application {
  id: string;
  jobId: string;
  jobTitle: string;
  candidateId: string;
  candidateName: string;
  candidateEmail: string;
  candidatePhone: string;
  source: ApplicationSource;
  campaignSource?: string;
  status: ApplicationStatus;
  currentStage: CandidateStage;
  appliedAt: string;
  screeningResult?: AIScreeningResult;
  hrReviewedBy?: string;
  hrDecisionReason?: string;
}

export interface Candidate {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  skills: string[];
  yearsExperience: number;
  education: string;
  resumeUrl: string;
  resumeText?: string;
  resumeFingerprint?: string;
  isHumanTakeover: boolean;
  ownerName: string;
  createdDate: string;

  // Optional candidate application helpers
  jobTitle?: string;
  currentStage?: CandidateStage;
  aiCallStatus?: string;
  appliedDate?: string;
  lastActivity?: string;
  stageProgress?: Array<{ stage: CandidateStage; status: 'completed' | 'current' | 'pending'; completedAt?: string }>;

  applications: Application[];
  calls: CallLog[];
  interviews: Interview[];
}

export interface FormField {
  id: string;
  label: string;
  type: 'text' | 'email' | 'phone' | 'file' | 'select' | 'textarea' | 'number';
  isRequired: boolean;
  options?: string[];
}

export interface ApplicationForm {
  id: string;
  jobId: string;
  jobTitle: string;
  title: string;
  publicUrlSlug: string;
  isPublished: boolean;
  fields: FormField[];
  customQuestions: Array<{ id: string; question: string; isRequired: boolean }>;
  createdDate: string;
  submissionsCount: number;
}

export interface CallLog {
  id: string;
  candidateId: string;
  candidateName: string;
  callDate: string;
  durationSeconds: number;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'PENDING' | 'NO_ANSWER' | 'CALLBACK' | 'FAILED' | 'NOT_INTERESTED';
  attempts: number;
  summary: string;
  transcript: Array<{ aiText?: string; candidateText?: string; speaker?: string; text?: string; time: string }>;
  recordingUrl?: string;
}

export interface Interview {
  id: string;
  candidateId: string;
  candidateName: string;
  jobId: string;
  jobTitle: string;
  type: 'AI_TECHNICAL' | 'HUMAN_MANAGER' | 'CODING' | 'HR_SCREENING';
  date: string;
  time: string;
  platform: 'Google Meet' | 'Zoom' | 'Microsoft Teams';
  meetingLink: string;
  interviewer: string;
  status: 'UPCOMING' | 'TODAY' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED' | 'RESCHEDULED';
}

export interface Evaluation {
  id: string;
  candidateId: string;
  candidateName: string;
  jobTitle: string;
  interviewType: string;
  technicalScore: number;
  communicationScore: number;
  problemSolvingScore: number;
  experienceScore: number;
  codingScore: number;
  overallRecommendation: 'STRONG_HIRE' | 'HIRE' | 'NEUTRAL' | 'REJECT';
  summary: string;
  evidence: string[];
  humanApproved: boolean;
  approvedBy?: string;
  createdAt: string;
}

export interface Offer {
  id: string;
  candidateId: string;
  candidateName: string;
  jobTitle: string;
  salary: string;
  startDate: string;
  status: OfferStatus;
  approvalStatus: 'APPROVED' | 'PENDING' | 'REJECTED';
  sentDate?: string;
  acceptanceDate?: string;
}

export interface OnboardingTask {
  id: string;
  candidateId: string;
  candidateName: string;
  jobTitle: string;
  joiningDate: string;
  progressPercent: number;
  documentsVerified: boolean;
  backgroundCheck: 'COMPLETED' | 'IN_PROGRESS' | 'PENDING';
  equipmentAssigned: boolean;
  tasks: Array<{
    id: string;
    title: string;
    category: 'Document' | 'Verification' | 'IT' | 'HR' | 'Manager';
    isCompleted: boolean;
    dueDate: string;
  }>;
}

export interface ActivityLogItem {
  id: string;
  timestamp: string;
  actorType: ActorType;
  actorName: string;
  candidateName?: string;
  jobTitle?: string;
  action: string;
  result: string;
  stage?: string;
}

export interface CompanyPolicy {
  maxCallAttempts: number;
  workingHours: string;
  interviewDurationMinutes: number;
  requiredApprovals: string[];
  reminderHoursBefore: number;
  allowedPlatforms: string[];
  candidateCommsRules: string;
  offerApprovalProcess: string;
}

export interface AIAgentState {
  isOnline: boolean;
  capabilities: string[];
  activeTask?: string;
  tasksQueue: string[];
  voiceId: string;
  lastCallTime?: string;
}

export interface IntegrationItem {
  id: string;
  category: 'Job Boards' | 'Forms' | 'Communication' | 'Calling' | 'Calendar' | 'Meetings' | 'Automation';
  platformName: string;
  isConnected: boolean;
  credentialsMasked?: string;
  lastTestedAt?: string;
  description: string;
}

export interface SourceAnalytics {
  source: string;
  applicationsCount: number;
  screeningPassed: number;
  interviewsScheduled: number;
  selectedCount: number;
}

export interface InterviewQuestionItem {
  id: string;
  order: number;
  questionText: string;
  category: 'TECHNICAL' | 'BEHAVIORAL' | 'CODING';
  candidateAnswer?: string;
  aiFollowup?: string;
  score?: number;
  feedback?: string;
}

export interface InterviewSessionDetails {
  id: string;
  candidateId: string;
  candidateName: string;
  jobId: string;
  jobTitle: string;
  status: 'PENDING' | 'STARTING' | 'WAITING_FOR_CANDIDATE' | 'IN_PROGRESS' | 'PAUSED' | 'HUMAN_TAKEOVER' | 'COMPLETED' | 'EVALUATED' | 'HR_APPROVED' | 'FAILED' | 'CANCELLED';
  brainStatus?: 'IDLE' | 'STARTING' | 'LISTENING' | 'THINKING' | 'QUESTION_READY' | 'PAUSED' | 'COMPLETED' | 'ERROR';
  currentStage?: string;
  difficulty?: 'EASY' | 'MEDIUM' | 'HARD' | string;
  currentQuestionIndex: number;
  screenConsentGiven: boolean;
  userCode?: string;
  codeTestResults?: { passed: boolean; output: string };
  transcript: Array<{ speaker: string; text: string; timestamp: string }>;
  evaluation?: {
    overall_score: number;
    technical_score: number;
    coding_score: number;
    communication_score: number;
    problem_solving_score: number;
    recommendation: string;
    summary: string;
    evidence: string[];
    human_approved: boolean;
  };
  overallScore?: number;
  hrApproved: boolean;
  hrApprovedBy?: string;
  elevenlabsAgentId?: string;
  elevenlabsConversationId?: string;
  questions: InterviewQuestionItem[];
}

export interface ElevenLabsSessionInfo {
  signed_url: string;
  agent_id: string;
  dynamic_variables: Record<string, string>;
  first_message: string;
  is_dev_mode?: boolean;
}


