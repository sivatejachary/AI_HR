'use client';

import { useState, useEffect } from 'react';
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
  CallLog,
  ApplicationForm,
  IntegrationItem,
  SourceAnalytics,
  AIScreeningResult
} from '../types';
import {
  initialJobs,
  initialCandidates,
  initialApplications,
  initialWorkflows,
  initialEvaluations,
  initialOffers,
  initialOnboarding,
  initialActivityLogs,
  initialForms,
  initialIntegrations,
  initialSourceAnalytics,
  defaultCompanyPolicy,
  defaultAgentState
} from '../data/mockData';
import { api } from '../lib/api';

export function useHRState() {
  const [jobs, setJobs] = useState<Job[]>(initialJobs);
  const [candidates, setCandidates] = useState<Candidate[]>(initialCandidates);
  const [applications, setApplications] = useState<Application[]>(initialApplications);
  const [workflows, setWorkflows] = useState<HiringWorkflow[]>(initialWorkflows);
  const [forms, setForms] = useState<ApplicationForm[]>(initialForms);
  const [integrations, setIntegrations] = useState<IntegrationItem[]>(initialIntegrations);
  const [sourceAnalytics, setSourceAnalytics] = useState<SourceAnalytics[]>(initialSourceAnalytics);
  const [evaluations, setEvaluations] = useState<Evaluation[]>(initialEvaluations);
  const [offers, setOffers] = useState<Offer[]>(initialOffers);
  const [onboarding, setOnboarding] = useState<OnboardingTask[]>(initialOnboarding);
  const [activityLogs, setActivityLogs] = useState<ActivityLogItem[]>(initialActivityLogs);
  const [companyPolicy, setCompanyPolicy] = useState<CompanyPolicy>(defaultCompanyPolicy);
  const [agentState, setAgentState] = useState<AIAgentState>(defaultAgentState);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Modals visibility state
  const [isCandidateModalOpen, setIsCandidateModalOpen] = useState(false);
  const [isCallingModalOpen, setIsCallingModalOpen] = useState(false);
  const [isInterviewModalOpen, setIsInterviewModalOpen] = useState(false);
  const [activeCallCandidate, setActiveCallCandidate] = useState<Candidate | null>(null);
  const [activeInterviewCandidate, setActiveInterviewCandidate] = useState<Candidate | null>(null);

  // Sync state from Backend API
  const refreshAllData = async () => {
    setIsLoading(true);
    try {
      const [jobsData, appsData, candsData, formsData, itgsData, logsData] = await Promise.all([
        api.getJobs().catch(() => null),
        api.getApplications().catch(() => null),
        api.getCandidates().catch(() => null),
        api.getForms().catch(() => null),
        api.getIntegrations().catch(() => null),
        api.getActivityLogs().catch(() => null)
      ]);

      if (jobsData) setJobs(jobsData);
      if (appsData) setApplications(appsData);
      if (candsData) setCandidates(candsData);
      if (formsData) setForms(formsData);
      if (itgsData) setIntegrations(itgsData);
      if (logsData) setActivityLogs(logsData);
    } catch (err) {
      console.warn('[useHRStore] API sync fallback', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshAllData();
  }, []);

  // Actions

  const addJob = async (newJob: Job) => {
    setJobs(prev => [newJob, ...prev]);
    try {
      await api.createJob({
        title: newJob.title,
        department: newJob.department,
        employmentType: newJob.employmentType,
        workplaceType: newJob.workplaceType,
        location: newJob.location,
        minExperience: newJob.minExperience,
        maxExperience: newJob.maxExperience,
        openings: newJob.openings,
        description: newJob.description,
        responsibilities: newJob.responsibilities,
        requirements: newJob.requirements,
        preferredSkills: newJob.preferredSkills,
        workflowId: newJob.workflowId,
        status: newJob.status
      });
      refreshAllData();
    } catch (e) {
      console.warn('API save fallback');
    }
    logActivity('HUMAN', 'HR Recruiter', `Created Job: ${newJob.title}`, `Status: ${newJob.status}`);
  };

  const updateJobStatus = async (jobId: string, status: Job['status']) => {
    setJobs(prev => prev.map(j => j.id === jobId ? { ...j, status } : j));
    try {
      await api.updateJobStatus(jobId, status);
    } catch (e) {}
    logActivity('HUMAN', 'HR Recruiter', `Updated Job Status`, `Job ${jobId} set to ${status}`);
  };

  const updateJobDistribution = (jobId: string, platform: 'LINKEDIN' | 'INDEED' | 'NAUKRI' | 'FOUNDIT' | 'CAREER_PAGE', status: 'PUBLISHED' | 'PAUSED' | 'FAILED') => {
    setJobs(prev =>
      prev.map(j => {
        if (j.id === jobId) {
          const updatedDists = j.distributions.map(d => d.platform === platform ? { ...d, publicationStatus: status, publishedAt: new Date().toISOString().split('T')[0] } : d);
          return { ...j, distributions: updatedDists };
        }
        return j;
      })
    );
    logActivity('SYSTEM', 'JobDistributionEngine', `Updated Platform Distribution`, `Job ${jobId} platform ${platform} set to ${status}`);
  };

  const addForm = async (newForm: ApplicationForm) => {
    setForms(prev => [newForm, ...prev]);
    logActivity('HUMAN', 'HR Recruiter', `Created Application Form`, `Public URL: /apply/${newForm.publicUrlSlug}`);
  };

  const ingestCandidateApplication = async (data: {
    name: string;
    email: string;
    phone: string;
    location: string;
    jobId: string;
    jobTitle: string;
    source: Application['source'];
    campaignSource?: string;
    resumeText?: string;
    skills: string[];
    yearsExperience: number;
  }) => {
    try {
      await api.applyToJob(data.jobId, data);
      await refreshAllData();
    } catch (e) {
      // Local fallback if API offline
      const candId = `cand-${Date.now()}`;
      const newCand: Candidate = {
        id: candId,
        name: data.name,
        email: data.email,
        phone: data.phone,
        location: data.location,
        skills: data.skills,
        yearsExperience: data.yearsExperience,
        education: 'BS Computer Science',
        resumeUrl: '/resumes/uploaded.pdf',
        resumeText: data.resumeText || 'Candidate submitted resume text',
        isHumanTakeover: false,
        ownerName: 'AI HR Agent',
        createdDate: new Date().toISOString().split('T')[0],
        applications: [],
        calls: [],
        interviews: []
      };
      setCandidates(prev => [newCand, ...prev]);

      const matchScore = 88;
      const newApp: Application = {
        id: `app-${Date.now()}`,
        jobId: data.jobId,
        jobTitle: data.jobTitle,
        candidateId: candId,
        candidateName: data.name,
        candidateEmail: data.email,
        candidatePhone: data.phone,
        source: data.source,
        campaignSource: data.campaignSource,
        status: 'AI_SHORTLISTED',
        currentStage: 'Screening',
        appliedAt: new Date().toISOString().split('T')[0],
        screeningResult: {
          id: `scr-${Date.now()}`,
          applicationId: `app-${Date.now()}`,
          candidateId: candId,
          matchScore,
          requiredSkillsMatch: { Python: 'MATCH', PostgreSQL: 'MATCH' },
          missingRequirements: [],
          experienceMatch: { required: '3+ years', candidate: `${data.yearsExperience} years`, isMatch: true },
          explanation: `Calculated candidate requirement fit: ${matchScore}%.`,
          recommendation: 'SHORTLIST_FOR_HR_REVIEW',
          screenedAt: new Date().toISOString().split('T')[0]
        }
      };
      setApplications(prev => [newApp, ...prev]);
    }
    logActivity('SYSTEM', 'CandidateIngestionService', `Ingested Application from ${data.name}`, `Source: ${data.source}`);
  };

  const hrApproveApplication = async (applicationId: string, reviewerName: string = 'Sarah Jenkins (HR)') => {
    setApplications(prev =>
      prev.map(app => app.id === applicationId ? { ...app, status: 'HR_APPROVED', currentStage: 'HR Call', hrReviewedBy: reviewerName } : app)
    );
    try {
      await api.approveApplication(applicationId);
    } catch (e) {}
    logActivity('HUMAN', reviewerName, `HR Approved Candidate Application`, `Moved to Outbound AI Calling Queue`);
  };

  const hrRejectApplication = async (applicationId: string, reason: string = 'Did not meet requirement threshold', reviewerName: string = 'Sarah Jenkins (HR)') => {
    setApplications(prev =>
      prev.map(app => app.id === applicationId ? { ...app, status: 'HR_REJECTED', hrReviewedBy: reviewerName, hrDecisionReason: reason } : app)
    );
    try {
      await api.rejectApplication(applicationId, reason);
    } catch (e) {}
    logActivity('HUMAN', reviewerName, `HR Rejected Candidate Application`, `Reason: ${reason}`);
  };

  const toggleIntegration = (integrationId: string) => {
    setIntegrations(prev =>
      prev.map(intg => {
        if (intg.id === integrationId) {
          const nextState = !intg.isConnected;
          logActivity('HUMAN', 'HR Administrator', `${nextState ? 'Connected' : 'Disconnected'} Integration`, `Platform: ${intg.platformName}`);
          return { ...intg, isConnected: nextState, lastTestedAt: new Date().toISOString().split('T')[0] };
        }
        return intg;
      })
    );
  };

  const toggleHumanTakeover = (candidateId: string) => {
    setCandidates(prev =>
      prev.map(c => {
        if (c.id === candidateId) {
          const newTakeoverState = !c.isHumanTakeover;
          logActivity('HUMAN', 'HR Manager', newTakeoverState ? 'Initiated Human Takeover' : 'Released Control to AI Agent', `Candidate: ${c.name}`);
          return {
            ...c,
            isHumanTakeover: newTakeoverState,
            ownerName: newTakeoverState ? 'Sarah Jenkins (HR)' : 'AI HR Agent'
          };
        }
        return c;
      })
    );
  };

  const toggleAgentOnline = () => {
    setAgentState(prev => {
      const nextState = !prev.isOnline;
      logActivity('HUMAN', 'HR Administrator', nextState ? 'Started AI HR Agent' : 'Paused AI HR Agent', nextState ? 'Agent status: ONLINE' : 'Agent status: PAUSED');
      return { ...prev, isOnline: nextState };
    });
  };

  const triggerAICall = (candidate: Candidate) => {
    setActiveCallCandidate(candidate);
    setIsCallingModalOpen(true);
    logActivity('AI', 'AI HR Calling Engine', `Initiated Outbound Voice Call`, `Candidate: ${candidate.name}`);
  };

  const completeAICall = (candidateId: string, resultStatus: 'COMPLETED' | 'CALLBACK' | 'NOT_INTERESTED', summary: string, transcript: any[]) => {
    setCandidates(prev =>
      prev.map(c => {
        if (c.id === candidateId) {
          const newCall: CallLog = {
            id: `call-${Date.now()}`,
            candidateId: c.id,
            candidateName: c.name,
            callDate: 'Just now',
            durationSeconds: 195,
            status: resultStatus,
            attempts: 1,
            summary,
            transcript
          };
          return { ...c, calls: [newCall, ...(c.calls || [])] };
        }
        return c;
      })
    );
    logActivity('AI', 'ElevenLabs Voice AI', `Completed Voice Call for Candidate ${candidateId}`, `Result: ${resultStatus}`);
  };

  const startAIInterview = (candidate: Candidate) => {
    setActiveInterviewCandidate(candidate);
    setIsInterviewModalOpen(true);
    logActivity('AI', 'AI Technical Interviewer', `Launched Technical Interview Room`, `Candidate: ${candidate.name}`);
  };

  const completeAIInterview = (candidateId: string, evalResult: Evaluation) => {
    setEvaluations(prev => [evalResult, ...prev]);
    logActivity('AI', 'AI Technical Interviewer', `Generated Technical Evaluation Scorecard`, `Score: ${evalResult.technicalScore}/100`);
  };

  const approveEvaluation = (evalId: string) => {
    setEvaluations(prev =>
      prev.map(e => e.id === evalId ? { ...e, humanApproved: true, approvedBy: 'David Miller (Hiring Manager)' } : e)
    );
    logActivity('HUMAN', 'David Miller (Hiring Manager)', `Approved Technical Evaluation`, `Evaluation ID: ${evalId}`);
  };

  const approveOffer = (offerId: string) => {
    setOffers(prev => prev.map(o => o.id === offerId ? { ...o, status: 'APPROVED', approvalStatus: 'APPROVED' } : o));
    logActivity('HUMAN', 'HR Manager', `Approved Offer Letter`, `Offer ID: ${offerId}`);
  };

  const sendOfferEmail = (offerId: string) => {
    setOffers(prev => prev.map(o => o.id === offerId ? { ...o, status: 'SENT', sentDate: new Date().toISOString().split('T')[0] } : o));
    logActivity('AI', 'n8n Email Engine', `Dispatched Offer Email via Gmail`, `Offer ID: ${offerId}`);
  };

  const createWorkflow = (newWf: HiringWorkflow) => {
    setWorkflows(prev => [newWf, ...prev]);
    // Also associate job if jobId is set
    if (newWf.jobId) {
      setJobs(prevJobs =>
        prevJobs.map(j => j.id === newWf.jobId ? { ...j, workflowId: newWf.id, workflowName: newWf.name } : j)
      );
    }
    logActivity('HUMAN', 'HR Recruiter', `Created Hiring Workflow: ${newWf.name}`, `Status: ${newWf.status}`);
  };

  const updateWorkflow = (updatedWf: HiringWorkflow) => {
    setWorkflows(prev =>
      prev.map(wf => wf.id === updatedWf.id ? { ...updatedWf, updatedAt: new Date().toISOString().split('T')[0] } : wf)
    );
    logActivity('HUMAN', 'HR Recruiter', `Updated Workflow: ${updatedWf.name}`, `Version: v${updatedWf.version}`);
  };

  const updateWorkflowSteps = (workflowId: string, updatedSteps: any[]) => {
    setWorkflows(prev =>
      prev.map(wf => wf.id === workflowId ? { ...wf, steps: updatedSteps, updatedAt: new Date().toISOString().split('T')[0] } : wf)
    );
    logActivity('HUMAN', 'HR Manager', `Updated Hiring Workflow Steps`, `Workflow ID: ${workflowId}`);
  };

  const publishWorkflow = (workflowId: string) => {
    setWorkflows(prev =>
      prev.map(wf => wf.id === workflowId ? { ...wf, status: 'Published', version: wf.version + 1, updatedAt: new Date().toISOString().split('T')[0] } : wf)
    );
    logActivity('HUMAN', 'HR Manager', `Published Workflow`, `Workflow ID: ${workflowId}`);
  };

  const archiveWorkflow = (workflowId: string) => {
    setWorkflows(prev =>
      prev.map(wf => wf.id === workflowId ? { ...wf, status: 'Archived', updatedAt: new Date().toISOString().split('T')[0] } : wf)
    );
    logActivity('HUMAN', 'HR Manager', `Archived Workflow`, `Workflow ID: ${workflowId}`);
  };

  const duplicateWorkflow = (workflowId: string) => {
    const source = workflows.find(w => w.id === workflowId);
    if (!source) return;
    const newWf: HiringWorkflow = {
      ...source,
      id: `wf-${Date.now()}`,
      name: `${source.name} (Copy)`,
      version: 1,
      status: 'Draft',
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0]
    };
    setWorkflows(prev => [newWf, ...prev]);
    logActivity('HUMAN', 'HR Recruiter', `Duplicated Workflow`, `New Workflow ID: ${newWf.id}`);
  };

  const deleteWorkflow = (workflowId: string) => {
    setWorkflows(prev => prev.filter(w => w.id !== workflowId));
    logActivity('HUMAN', 'HR Manager', `Deleted Workflow`, `Workflow ID: ${workflowId}`);
  };

  const logActivity = (actorType: 'HUMAN' | 'AI' | 'SYSTEM', actorName: string, action: string, result: string) => {
    const newLog: ActivityLogItem = {
      id: `act-${Date.now()}`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      actorType,
      actorName,
      action,
      result
    };
    setActivityLogs(prev => [newLog, ...prev]);
  };

  return {
    jobs,
    candidates,
    applications,
    workflows,
    forms,
    integrations,
    sourceAnalytics,
    evaluations,
    offers,
    onboarding,
    activityLogs,
    companyPolicy,
    agentState,
    selectedCandidate,
    setSelectedCandidate,
    isCandidateModalOpen,
    setIsCandidateModalOpen,
    isCallingModalOpen,
    setIsCallingModalOpen,
    isInterviewModalOpen,
    setIsInterviewModalOpen,
    activeCallCandidate,
    activeInterviewCandidate,
    isLoading,
    refreshAllData,
    addJob,
    createJob: addJob,
    updateJobStatus,
    updateJobDistribution,
    addForm,
    ingestCandidateApplication,
    hrApproveApplication,
    hrRejectApplication,
    toggleIntegration,
    toggleHumanTakeover,
    toggleAgentOnline,
    triggerAICall,
    completeAICall,
    startAIInterview,
    completeAIInterview,
    approveEvaluation,
    approveOffer,
    sendOfferEmail,
    createWorkflow,
    updateWorkflow,
    updateWorkflowSteps,
    publishWorkflow,
    archiveWorkflow,
    duplicateWorkflow,
    deleteWorkflow,
    setCompanyPolicy
  };
}
