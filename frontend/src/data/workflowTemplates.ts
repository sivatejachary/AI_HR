import { HiringWorkflow, WorkflowStep } from '../types';

export interface WorkflowTemplate {
  id: string;
  name: string;
  category: 'Technical' | 'Non-Technical' | 'Leadership';
  description: string;
  steps: Array<Omit<WorkflowStep, 'id' | 'order'>>;
}

export const WORKFLOW_TEMPLATES: WorkflowTemplate[] = [
  // TECHNICAL ROLES
  {
    id: 'tpl-software-engineer',
    name: 'Software Engineer',
    category: 'Technical',
    description: 'Standard technical engineering pipeline with coding assessment and technical interview.',
    steps: [
      {
        name: 'Application',
        category: 'Screening',
        type: 'DOCUMENT_COLLECTION',
        purpose: 'Candidate applies via job portal, referral, or form.',
        owner: 'Recruiter',
        automation: 'Fully automated',
        isRequired: true,
        isEnabled: true,
        config: {}
      },
      {
        name: 'Resume Screening',
        category: 'Screening',
        type: 'AI_ACTION',
        purpose: 'Automated skill and experience match evaluation against job requirements.',
        owner: 'AI',
        automation: 'AI-assisted',
        isRequired: true,
        isEnabled: true,
        config: {}
      },
      {
        name: 'HR Review',
        category: 'Screening',
        type: 'HUMAN_ACTION',
        purpose: 'HR Recruiter reviews AI recommendations and shortlists candidate.',
        owner: 'HR',
        automation: 'Manual',
        isRequired: true,
        isEnabled: true,
        config: {}
      },
      {
        name: 'HR Screening Call',
        category: 'Communication',
        type: 'VOICE_CALL',
        purpose: 'Check candidate availability, notice period, and salary expectations.',
        owner: 'Recruiter',
        automation: 'AI-assisted',
        durationMinutes: 15,
        isRequired: true,
        isEnabled: true,
        config: { maxAttempts: 3 }
      },
      {
        name: 'Technical Assessment',
        category: 'Assessment',
        type: 'ASSESSMENT',
        purpose: 'Automated coding and algorithm challenge test.',
        owner: 'Interviewer',
        automation: 'Fully automated',
        durationMinutes: 60,
        passingScore: 70,
        isRequired: true,
        isEnabled: true,
        config: { platform: 'HackerRank / Custom Coding' }
      },
      {
        name: 'Technical Interview',
        category: 'Interview',
        type: 'INTERVIEW',
        purpose: 'Deep-dive live system design and code architecture evaluation.',
        owner: 'Interviewer',
        automation: 'Manual',
        durationMinutes: 45,
        isRequired: true,
        isEnabled: true,
        config: { platform: 'Google Meet' }
      },
      {
        name: 'Hiring Manager Interview',
        category: 'Interview',
        type: 'INTERVIEW',
        purpose: 'Culture fit, team dynamic, and project alignment interview.',
        owner: 'Hiring Manager',
        automation: 'Manual',
        durationMinutes: 45,
        isRequired: true,
        isEnabled: true,
        config: { platform: 'Google Meet' }
      },
      {
        name: 'Final Decision',
        category: 'Decision',
        type: 'APPROVAL',
        purpose: 'Final hiring decision and offer recommendation by HR & Manager.',
        owner: 'Hiring Manager',
        automation: 'Manual',
        isRequired: true,
        isEnabled: true,
        config: {}
      }
    ]
  },
  {
    id: 'tpl-frontend-developer',
    name: 'Frontend Developer',
    category: 'Technical',
    description: 'Frontend pipeline emphasizing UI/UX evaluation and React/JS live coding.',
    steps: [
      { name: 'Application', category: 'Screening', type: 'DOCUMENT_COLLECTION', purpose: 'Candidate application ingestion.', owner: 'Recruiter', automation: 'Fully automated', isRequired: true, isEnabled: true, config: {} },
      { name: 'Resume Screening', category: 'Screening', type: 'AI_ACTION', purpose: 'Skill parsing for React, TypeScript, CSS, and UI frameworks.', owner: 'AI', automation: 'AI-assisted', isRequired: true, isEnabled: true, config: {} },
      { name: 'HR Screening Call', category: 'Communication', type: 'VOICE_CALL', purpose: 'Initial phone screen for interest and notice period.', owner: 'HR', automation: 'AI-assisted', durationMinutes: 15, isRequired: true, isEnabled: true, config: {} },
      { name: 'UI Take-Home Test', category: 'Assessment', type: 'ASSESSMENT', purpose: 'Build a responsive component or UI feature.', owner: 'Interviewer', automation: 'Manual', durationMinutes: 120, isRequired: true, isEnabled: true, config: {} },
      { name: 'Frontend Technical Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Code review of take-home test & web performance questions.', owner: 'Interviewer', automation: 'Manual', durationMinutes: 45, isRequired: true, isEnabled: true, config: {} },
      { name: 'Hiring Manager Approval', category: 'Decision', type: 'APPROVAL', purpose: 'Final manager review and offer approval.', owner: 'Hiring Manager', automation: 'Manual', isRequired: true, isEnabled: true, config: {} }
    ]
  },
  {
    id: 'tpl-backend-developer',
    name: 'Backend Developer',
    category: 'Technical',
    description: 'Backend pipeline focused on databases, API design, and microservices.',
    steps: [
      { name: 'Application', category: 'Screening', type: 'DOCUMENT_COLLECTION', purpose: 'Application ingestion.', owner: 'Recruiter', automation: 'Fully automated', isRequired: true, isEnabled: true, config: {} },
      { name: 'Resume Screening', category: 'Screening', type: 'AI_ACTION', purpose: 'Match Python, Java, Node, SQL, and cloud infrastructure.', owner: 'AI', automation: 'AI-assisted', isRequired: true, isEnabled: true, config: {} },
      { name: 'HR Call', category: 'Communication', type: 'VOICE_CALL', purpose: 'Availability and expectation screen.', owner: 'HR', automation: 'AI-assisted', durationMinutes: 15, isRequired: true, isEnabled: true, config: {} },
      { name: 'Backend Technical Test', category: 'Assessment', type: 'ASSESSMENT', purpose: 'Database queries and API building test.', owner: 'Interviewer', automation: 'Fully automated', durationMinutes: 60, isRequired: true, isEnabled: true, config: {} },
      { name: 'System Architecture Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'System scalability and database indexing evaluation.', owner: 'Interviewer', automation: 'Manual', durationMinutes: 60, isRequired: true, isEnabled: true, config: {} },
      { name: 'Hiring Manager Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Team fit and engineering philosophy.', owner: 'Hiring Manager', automation: 'Manual', durationMinutes: 45, isRequired: true, isEnabled: true, config: {} },
      { name: 'Final Decision', category: 'Decision', type: 'APPROVAL', purpose: 'Hiring decision and offer decision.', owner: 'HR', automation: 'Manual', isRequired: true, isEnabled: true, config: {} }
    ]
  },
  {
    id: 'tpl-data-scientist',
    name: 'Data Scientist',
    category: 'Technical',
    description: 'Data science & analytics pipeline with modeling and statistics assessment.',
    steps: [
      { name: 'Application', category: 'Screening', type: 'DOCUMENT_COLLECTION', purpose: 'Application intake.', owner: 'Recruiter', automation: 'Fully automated', isRequired: true, isEnabled: true, config: {} },
      { name: 'Resume Screening', category: 'Screening', type: 'AI_ACTION', purpose: 'Screening for Python, R, ML models, and statistics.', owner: 'AI', automation: 'AI-assisted', isRequired: true, isEnabled: true, config: {} },
      { name: 'HR Review', category: 'Screening', type: 'HUMAN_ACTION', purpose: 'Manual candidate review.', owner: 'HR', automation: 'Manual', isRequired: true, isEnabled: true, config: {} },
      { name: 'HR Screening Call', category: 'Communication', type: 'VOICE_CALL', purpose: 'Background and motivation check.', owner: 'HR', automation: 'AI-assisted', durationMinutes: 15, isRequired: true, isEnabled: true, config: {} },
      { name: 'Data Analysis Test', category: 'Assessment', type: 'ASSESSMENT', purpose: 'Dataset cleaning, modeling, and hypothesis testing.', owner: 'Interviewer', automation: 'Fully automated', durationMinutes: 90, isRequired: true, isEnabled: true, config: {} },
      { name: 'Technical & ML Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Machine learning model trade-offs & SQL evaluation.', owner: 'Interviewer', automation: 'Manual', durationMinutes: 60, isRequired: true, isEnabled: true, config: {} },
      { name: 'Hiring Manager Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Business impact and cross-functional alignment.', owner: 'Hiring Manager', automation: 'Manual', durationMinutes: 45, isRequired: true, isEnabled: true, config: {} },
      { name: 'Final Decision', category: 'Decision', type: 'APPROVAL', purpose: 'Final hire decision.', owner: 'Hiring Manager', automation: 'Manual', isRequired: true, isEnabled: true, config: {} }
    ]
  },

  // NON-TECHNICAL ROLES
  {
    id: 'tpl-sales-executive',
    name: 'Sales Executive',
    category: 'Non-Technical',
    description: 'Sales pipeline focused on verbal communication, pitch assessment, and quota track record.',
    steps: [
      { name: 'Application', category: 'Screening', type: 'DOCUMENT_COLLECTION', purpose: 'Application intake.', owner: 'Recruiter', automation: 'Fully automated', isRequired: true, isEnabled: true, config: {} },
      { name: 'Resume Screening', category: 'Screening', type: 'AI_ACTION', purpose: 'Quota achievement, target market, and industry experience check.', owner: 'AI', automation: 'AI-assisted', isRequired: true, isEnabled: true, config: {} },
      { name: 'HR Review', category: 'Screening', type: 'HUMAN_ACTION', purpose: 'Recruiter shortlist review.', owner: 'HR', automation: 'Manual', isRequired: true, isEnabled: true, config: {} },
      { name: 'HR Calling', category: 'Communication', type: 'VOICE_CALL', purpose: 'Verbal communication and sales drive screen.', owner: 'HR', automation: 'AI-assisted', durationMinutes: 15, isRequired: true, isEnabled: true, config: {} },
      { name: 'Sales Roleplay Pitch Assessment', category: 'Assessment', type: 'ASSESSMENT', purpose: 'Mock product presentation and objection handling.', owner: 'Hiring Manager', automation: 'Manual', durationMinutes: 30, isRequired: true, isEnabled: true, config: {} },
      { name: 'Sales Manager Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Commission structure, pipeline management, and methodology.', owner: 'Hiring Manager', automation: 'Manual', durationMinutes: 45, isRequired: true, isEnabled: true, config: {} },
      { name: 'Final Decision', category: 'Decision', type: 'APPROVAL', purpose: 'Final hiring approval and offer setup.', owner: 'HR', automation: 'Manual', isRequired: true, isEnabled: true, config: {} }
    ]
  },
  {
    id: 'tpl-customer-support',
    name: 'Customer Support Executive',
    category: 'Non-Technical',
    description: 'Customer service pipeline prioritizing empathy, language skills, and conflict resolution.',
    steps: [
      { name: 'Application', category: 'Screening', type: 'DOCUMENT_COLLECTION', purpose: 'Application intake.', owner: 'Recruiter', automation: 'Fully automated', isRequired: true, isEnabled: true, config: {} },
      { name: 'Resume Screening', category: 'Screening', type: 'AI_ACTION', purpose: 'Check customer service experience and shifts availability.', owner: 'AI', automation: 'AI-assisted', isRequired: true, isEnabled: true, config: {} },
      { name: 'HR Review', category: 'Screening', type: 'HUMAN_ACTION', purpose: 'HR candidate verification.', owner: 'HR', automation: 'Manual', isRequired: true, isEnabled: true, config: {} },
      { name: 'Communication Assessment', category: 'Assessment', type: 'ASSESSMENT', purpose: 'Written English & typing speed evaluation.', owner: 'AI', automation: 'Fully automated', durationMinutes: 20, isRequired: true, isEnabled: true, config: {} },
      { name: 'HR Call', category: 'Communication', type: 'VOICE_CALL', purpose: 'Voice tone, clarity, and availability check.', owner: 'HR', automation: 'AI-assisted', durationMinutes: 15, isRequired: true, isEnabled: true, config: {} },
      { name: 'Support Manager Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Escalation handling and scenario questions.', owner: 'Hiring Manager', automation: 'Manual', durationMinutes: 30, isRequired: true, isEnabled: true, config: {} },
      { name: 'Final Decision', category: 'Decision', type: 'APPROVAL', purpose: 'Final hiring decision.', owner: 'Hiring Manager', automation: 'Manual', isRequired: true, isEnabled: true, config: {} }
    ]
  },
  {
    id: 'tpl-hr-executive',
    name: 'HR Executive',
    category: 'Non-Technical',
    description: 'HR recruitment pipeline assessing labor compliance, employee relations, and ATS tools.',
    steps: [
      { name: 'Application', category: 'Screening', type: 'DOCUMENT_COLLECTION', purpose: 'Application submission.', owner: 'Recruiter', automation: 'Fully automated', isRequired: true, isEnabled: true, config: {} },
      { name: 'Resume Screening', category: 'Screening', type: 'AI_ACTION', purpose: 'Screening HR certifications, HRIS tools, and recruiting metrics.', owner: 'AI', automation: 'AI-assisted', isRequired: true, isEnabled: true, config: {} },
      { name: 'HR Screening Call', category: 'Communication', type: 'VOICE_CALL', purpose: 'Notice period, expected CTC, and location check.', owner: 'HR', automation: 'Manual', durationMinutes: 20, isRequired: true, isEnabled: true, config: {} },
      { name: 'Case Study Assessment', category: 'Assessment', type: 'ASSESSMENT', purpose: 'Employee grievance case analysis.', owner: 'Hiring Manager', automation: 'Manual', durationMinutes: 45, isRequired: true, isEnabled: true, config: {} },
      { name: 'HR Head Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Organizational culture and HR strategy interview.', owner: 'Hiring Manager', automation: 'Manual', durationMinutes: 45, isRequired: true, isEnabled: true, config: {} },
      { name: 'Final Decision', category: 'Decision', type: 'APPROVAL', purpose: 'Final offer approval.', owner: 'HR', automation: 'Manual', isRequired: true, isEnabled: true, config: {} }
    ]
  },

  // LEADERSHIP
  {
    id: 'tpl-engineering-manager',
    name: 'Engineering Manager',
    category: 'Leadership',
    description: 'Leadership pipeline for engineering managers focusing on team leadership, architecture, and strategy.',
    steps: [
      { name: 'Application', category: 'Screening', type: 'DOCUMENT_COLLECTION', purpose: 'Application intake.', owner: 'Recruiter', automation: 'Fully automated', isRequired: true, isEnabled: true, config: {} },
      { name: 'Executive Resume Review', category: 'Screening', type: 'HUMAN_ACTION', purpose: 'Senior HR review of team sizes managed and tech stack background.', owner: 'HR', automation: 'Manual', isRequired: true, isEnabled: true, config: {} },
      { name: 'HR Executive Screen', category: 'Communication', type: 'VOICE_CALL', purpose: 'Leadership aspirations, salary expectations, and notice period.', owner: 'Recruiter', automation: 'Manual', durationMinutes: 30, isRequired: true, isEnabled: true, config: {} },
      { name: 'System Architecture & Management Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Technical leadership and system scaling panel.', owner: 'Interviewer', automation: 'Manual', durationMinutes: 60, isRequired: true, isEnabled: true, config: {} },
      { name: 'People Management & Conflict Resolution', category: 'Interview', type: 'INTERVIEW', purpose: 'Performance management, hiring, and mentoring interview.', owner: 'Hiring Manager', automation: 'Manual', durationMinutes: 45, isRequired: true, isEnabled: true, config: {} },
      { name: 'VP of Engineering / Director Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Strategic roadmapping and department vision.', owner: 'Hiring Manager', automation: 'Manual', durationMinutes: 45, isRequired: true, isEnabled: true, config: {} },
      { name: 'Executive Panel Final Approval', category: 'Decision', type: 'APPROVAL', purpose: 'Executive offer approval.', owner: 'Hiring Manager', automation: 'Manual', isRequired: true, isEnabled: true, config: {} }
    ]
  },
  {
    id: 'tpl-product-manager',
    name: 'Product Manager',
    category: 'Leadership',
    description: 'Product pipeline emphasizing product sense, user metrics, prioritization, and roadmapping.',
    steps: [
      { name: 'Application', category: 'Screening', type: 'DOCUMENT_COLLECTION', purpose: 'Application intake.', owner: 'Recruiter', automation: 'Fully automated', isRequired: true, isEnabled: true, config: {} },
      { name: 'Resume Screening', category: 'Screening', type: 'AI_ACTION', purpose: 'Product metric wins, B2B/B2C domain, and PRD experience.', owner: 'AI', automation: 'AI-assisted', isRequired: true, isEnabled: true, config: {} },
      { name: 'HR Screening Call', category: 'Communication', type: 'VOICE_CALL', purpose: 'Initial phone screen.', owner: 'HR', automation: 'AI-assisted', durationMinutes: 15, isRequired: true, isEnabled: true, config: {} },
      { name: 'Product Sense & Design Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Evaluate user problem solving and UI/UX prioritization.', owner: 'Interviewer', automation: 'Manual', durationMinutes: 45, isRequired: true, isEnabled: true, config: {} },
      { name: 'Product Strategy Presentation', category: 'Assessment', type: 'ASSESSMENT', purpose: 'Present product roadmap solution for sample case.', owner: 'Hiring Manager', automation: 'Manual', durationMinutes: 60, isRequired: true, isEnabled: true, config: {} },
      { name: 'Engineering & Leadership Alignment', category: 'Interview', type: 'INTERVIEW', purpose: 'Cross-functional engineering and design collaboration.', owner: 'Hiring Manager', automation: 'Manual', durationMinutes: 45, isRequired: true, isEnabled: true, config: {} },
      { name: 'Final Hiring Decision', category: 'Decision', type: 'APPROVAL', purpose: 'Final hiring manager decision.', owner: 'Hiring Manager', automation: 'Manual', isRequired: true, isEnabled: true, config: {} }
    ]
  }
];

// Helper function: Generate AI recommendation for a specific job title/dept
export function generateRecommendedWorkflow(job: {
  title: string;
  department: string;
  minExperience?: number;
  description?: string;
}): { explanation: string; steps: Array<Omit<WorkflowStep, 'id' | 'order'>> } {
  const titleLower = job.title.toLowerCase();
  const deptLower = job.department.toLowerCase();

  if (titleLower.includes('sales') || titleLower.includes('business development') || titleLower.includes('account')) {
    const tpl = WORKFLOW_TEMPLATES.find(t => t.id === 'tpl-sales-executive')!;
    return {
      explanation: `Recommended for ${job.title}: Includes initial resume screening, AI interest call, practical sales roleplay presentation, and sales manager review to assess revenue impact and communication.`,
      steps: tpl.steps
    };
  }

  if (titleLower.includes('support') || titleLower.includes('customer') || titleLower.includes('client')) {
    const tpl = WORKFLOW_TEMPLATES.find(t => t.id === 'tpl-customer-support')!;
    return {
      explanation: `Recommended for ${job.title}: Standard customer service pipeline with communication test, automated AI phone screen, and scenario-based manager interview.`,
      steps: tpl.steps
    };
  }

  if (titleLower.includes('data') || titleLower.includes('machine learning') || titleLower.includes('ai') || titleLower.includes('analytics')) {
    const tpl = WORKFLOW_TEMPLATES.find(t => t.id === 'tpl-data-scientist')!;
    return {
      explanation: `Recommended for ${job.title}: Features technical data analysis assessment, machine learning modeling interview, and hiring manager evaluation.`,
      steps: tpl.steps
    };
  }

  if (titleLower.includes('manager') || titleLower.includes('head') || titleLower.includes('director') || titleLower.includes('lead')) {
    const tpl = WORKFLOW_TEMPLATES.find(t => t.id === 'tpl-engineering-manager')!;
    return {
      explanation: `Recommended for ${job.title}: Enterprise leadership pipeline with multi-stage technical architecture, people management, and executive alignment.`,
      steps: tpl.steps
    };
  }

  if (titleLower.includes('frontend') || titleLower.includes('ui') || titleLower.includes('react')) {
    const tpl = WORKFLOW_TEMPLATES.find(t => t.id === 'tpl-frontend-developer')!;
    return {
      explanation: `Recommended for ${job.title}: Frontend engineering workflow with UI take-home test and live component architecture review.`,
      steps: tpl.steps
    };
  }

  // Default Technical engineering workflow
  const defaultTpl = WORKFLOW_TEMPLATES.find(t => t.id === 'tpl-software-engineer')!;
  return {
    explanation: `Recommended for ${job.title} (${job.department}): Standard enterprise engineering hiring process with resume screening, HR screening call, technical assessment, technical interview, and hiring manager decision.`,
    steps: defaultTpl.steps
  };
}
