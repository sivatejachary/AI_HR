'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Plus, ChevronRight, UserCheck, Bot, PhoneCall, Mail, Calendar, Code2, FileCheck, CheckCircle2, ShieldAlert, Sparkles, MessageSquare } from 'lucide-react';
import { StepCategory, StepType, StepOwner, WorkflowStep } from '../../types';

interface AddStepOption {
  name: string;
  category: StepCategory;
  type: StepType;
  purpose: string;
  defaultOwner: WorkflowStep['owner'];
  defaultAutomation: WorkflowStep['automation'];
  icon: any;
}

const STEP_OPTIONS: AddStepOption[] = [
  // Screening
  { name: 'Resume Screening', category: 'Screening', type: 'AI_ACTION', purpose: 'Automated skill match against job requirements.', defaultOwner: 'AI', defaultAutomation: 'AI-assisted', icon: Bot },
  { name: 'HR Review', category: 'Screening', type: 'HUMAN_ACTION', purpose: 'HR recruiter manual shortlist review.', defaultOwner: 'HR', defaultAutomation: 'Manual', icon: UserCheck },
  { name: 'AI Screening', category: 'Screening', type: 'AI_ACTION', purpose: 'Automated candidate qualifications check.', defaultOwner: 'AI', defaultAutomation: 'Fully automated', icon: Sparkles },

  // Communication
  { name: 'HR Call', category: 'Communication', type: 'VOICE_CALL', purpose: 'HR screening call for interest and notice period.', defaultOwner: 'Recruiter', defaultAutomation: 'Manual', icon: PhoneCall },
  { name: 'AI HR Call', category: 'Communication', type: 'VOICE_CALL', purpose: 'Outbound AI voice screen for interest & salary expectations.', defaultOwner: 'AI', defaultAutomation: 'Fully automated', icon: PhoneCall },
  { name: 'Email Notification', category: 'Communication', type: 'EMAIL', purpose: 'Send automated email status or questionnaire.', defaultOwner: 'Recruiter', defaultAutomation: 'Fully automated', icon: Mail },
  { name: 'WhatsApp Message', category: 'Communication', type: 'NOTIFICATION', purpose: 'Send candidate updates or links via WhatsApp.', defaultOwner: 'Recruiter', defaultAutomation: 'Fully automated', icon: MessageSquare },

  // Assessment
  { name: 'Technical Assessment', category: 'Assessment', type: 'ASSESSMENT', purpose: 'Automated technical coding test or skill challenge.', defaultOwner: 'Interviewer', defaultAutomation: 'Fully automated', icon: Code2 },
  { name: 'Coding Test', category: 'Assessment', type: 'ASSESSMENT', purpose: 'Live or asynchronous code execution challenge.', defaultOwner: 'Interviewer', defaultAutomation: 'Fully automated', icon: Code2 },
  { name: 'Aptitude Test', category: 'Assessment', type: 'ASSESSMENT', purpose: 'Logical reasoning and problem solving evaluation.', defaultOwner: 'Recruiter', defaultAutomation: 'Fully automated', icon: FileCheck },
  { name: 'Communication Test', category: 'Assessment', type: 'ASSESSMENT', purpose: 'Language proficiency and writing skills test.', defaultOwner: 'Recruiter', defaultAutomation: 'Fully automated', icon: MessageSquare },
  { name: 'Custom Assessment', category: 'Assessment', type: 'ASSESSMENT', purpose: 'Custom project or take-home assignment.', defaultOwner: 'Hiring Manager', defaultAutomation: 'Manual', icon: FileCheck },

  // Interview
  { name: 'HR Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Behavioral and cultural fit interview.', defaultOwner: 'HR', defaultAutomation: 'Manual', icon: UserCheck },
  { name: 'Technical Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Live system design and engineering deep-dive.', defaultOwner: 'Interviewer', defaultAutomation: 'Manual', icon: Code2 },
  { name: 'Manager Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Hiring manager team fit and alignment interview.', defaultOwner: 'Hiring Manager', defaultAutomation: 'Manual', icon: UserCheck },
  { name: 'Panel Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Multi-interviewer team panel discussion.', defaultOwner: 'Interviewer', defaultAutomation: 'Manual', icon: UserCheck },
  { name: 'AI Interview', category: 'Interview', type: 'INTERVIEW', purpose: 'Automated AI audio/video technical interview room.', defaultOwner: 'AI', defaultAutomation: 'AI-assisted', icon: Bot },

  // Decision
  { name: 'Hiring Manager Approval', category: 'Decision', type: 'APPROVAL', purpose: 'Hiring manager review and decision sign-off.', defaultOwner: 'Hiring Manager', defaultAutomation: 'Manual', icon: CheckCircle2 },
  { name: 'Final HR Decision', category: 'Decision', type: 'APPROVAL', purpose: 'Final HR authorization and compensation check.', defaultOwner: 'HR', defaultAutomation: 'Manual', icon: CheckCircle2 },
  { name: 'Offer Letter', category: 'Decision', type: 'OFFER', purpose: 'Generate and dispatch employment offer letter.', defaultOwner: 'HR', defaultAutomation: 'AI-assisted', icon: FileCheck },
  { name: 'Rejection Notice', category: 'Decision', type: 'NOTIFICATION', purpose: 'Send respectful candidate rejection communication.', defaultOwner: 'Recruiter', defaultAutomation: 'Fully automated', icon: ShieldAlert },

  // Other
  { name: 'Reference Check', category: 'Other', type: 'DOCUMENT_COLLECTION', purpose: 'Collect and verify professional references.', defaultOwner: 'Recruiter', defaultAutomation: 'Manual', icon: FileCheck },
  { name: 'Background Verification', category: 'Other', type: 'DOCUMENT_COLLECTION', purpose: 'Employment history and identity verification.', defaultOwner: 'HR', defaultAutomation: 'Manual', icon: ShieldAlert },
  { name: 'Custom Step', category: 'Other', type: 'HUMAN_ACTION', purpose: 'Define a custom hiring workflow stage.', defaultOwner: 'HR', defaultAutomation: 'Manual', icon: Plus }
];

interface Props {
  onAddStep: (stepData: Partial<WorkflowStep>) => void;
  buttonText?: string;
  className?: string;
}

export function CategorizedAddStepMenu({ onAddStep, buttonText = 'Add Step', className = '' }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<StepCategory>('Screening');
  const [showCustomModal, setShowCustomModal] = useState(false);
  
  // Custom step form
  const [customName, setCustomName] = useState('');
  const [customPurpose, setCustomPurpose] = useState('');
  const [customOwner, setCustomOwner] = useState<WorkflowStep['owner']>('HR');
  const [customAutomation, setCustomAutomation] = useState<WorkflowStep['automation']>('Manual');

  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const categories: StepCategory[] = ['Screening', 'Communication', 'Assessment', 'Interview', 'Decision', 'Other'];

  const handleSelectOption = (opt: AddStepOption) => {
    if (opt.name === 'Custom Step') {
      setIsOpen(false);
      setShowCustomModal(true);
      return;
    }

    onAddStep({
      name: opt.name,
      category: opt.category,
      type: opt.type,
      purpose: opt.purpose,
      owner: opt.defaultOwner,
      automation: opt.defaultAutomation,
      isRequired: true,
      isEnabled: true,
      durationMinutes: opt.category === 'Interview' ? 45 : opt.category === 'Communication' ? 15 : 30,
      config: {}
    });
    setIsOpen(false);
  };

  const handleSaveCustom = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customName.trim()) return;

    onAddStep({
      name: customName.trim(),
      category: 'Other',
      type: 'HUMAN_ACTION',
      purpose: customPurpose.trim() || 'Custom hiring step',
      owner: customOwner,
      automation: customAutomation,
      isRequired: true,
      isEnabled: true,
      config: {}
    });

    setCustomName('');
    setCustomPurpose('');
    setShowCustomModal(false);
  };

  return (
    <div className="relative inline-block text-left" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`inline-flex items-center gap-2 px-3.5 py-2 bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold rounded-lg shadow-xs transition ${className}`}
      >
        <Plus size={15} /> {buttonText}
      </button>

      {isOpen && (
        <div className="absolute left-0 mt-2 w-[480px] bg-white border border-gray-200 rounded-xl shadow-lg z-50 overflow-hidden flex divide-x divide-gray-100 animate-in fade-in zoom-in-95 duration-100">
          {/* Category List Sidebar */}
          <div className="w-44 bg-gray-50/70 p-2 space-y-0.5 shrink-0">
            <div className="px-2 py-1 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Categories</div>
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`w-full text-left px-2.5 py-1.5 rounded-md text-xs font-medium flex items-center justify-between transition ${
                  selectedCategory === cat
                    ? 'bg-white text-blue-700 font-semibold shadow-2xs border border-gray-200'
                    : 'text-gray-700 hover:bg-gray-100/80 hover:text-gray-900'
                }`}
              >
                <span>{cat}</span>
                <ChevronRight size={13} className={selectedCategory === cat ? 'text-blue-700' : 'text-gray-400'} />
              </button>
            ))}
          </div>

          {/* Options for Selected Category */}
          <div className="flex-1 p-3 max-h-[340px] overflow-y-auto space-y-1">
            <div className="px-1 pb-1 text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
              {selectedCategory} Steps
            </div>
            {STEP_OPTIONS.filter(o => o.category === selectedCategory).map(opt => {
              const Icon = opt.icon;
              return (
                <button
                  key={opt.name}
                  onClick={() => handleSelectOption(opt)}
                  className="w-full text-left p-2 rounded-lg hover:bg-blue-50/60 border border-transparent hover:border-blue-100 transition group flex items-start gap-2.5"
                >
                  <div className="w-7 h-7 rounded-md bg-gray-100 group-hover:bg-blue-100 text-gray-600 group-hover:text-blue-700 flex items-center justify-center shrink-0 mt-0.5">
                    <Icon size={14} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1">
                      <span className="text-xs font-semibold text-gray-900 group-hover:text-blue-900">{opt.name}</span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded font-medium bg-gray-100 text-gray-600 group-hover:bg-blue-100 group-hover:text-blue-800">
                        {opt.defaultAutomation}
                      </span>
                    </div>
                    <p className="text-[11px] text-gray-500 line-clamp-1 mt-0.5">{opt.purpose}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Custom Step Modal */}
      {showCustomModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white border border-gray-200 rounded-xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95">
            <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
              <h3 className="text-sm font-bold text-gray-900">Add Custom Hiring Step</h3>
              <button onClick={() => setShowCustomModal(false)} className="text-gray-400 hover:text-gray-600 text-xs">✕</button>
            </div>
            <form onSubmit={handleSaveCustom} className="p-5 space-y-4 text-xs">
              <div>
                <label className="font-semibold text-gray-700 block mb-1">Step Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Portfolio Review, Background Check"
                  value={customName}
                  onChange={e => setCustomName(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-gray-900 text-xs focus:ring-2 focus:ring-blue-600 outline-none"
                />
              </div>

              <div>
                <label className="font-semibold text-gray-700 block mb-1">Purpose / Description</label>
                <textarea
                  placeholder="Describe what happens in this stage..."
                  value={customPurpose}
                  onChange={e => setCustomPurpose(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg p-2.5 text-gray-900 text-xs focus:ring-2 focus:ring-blue-600 outline-none h-20"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-gray-700 block mb-1">Step Owner</label>
                  <select
                    value={customOwner}
                    onChange={e => setCustomOwner(e.target.value as StepOwner)}
                    className="w-full border border-gray-300 rounded-lg px-2.5 py-1.5 text-gray-900 text-xs bg-white"
                  >
                    <option value="HR">HR</option>
                    <option value="Recruiter">Recruiter</option>
                    <option value="Hiring Manager">Hiring Manager</option>
                    <option value="Interviewer">Interviewer</option>
                    <option value="AI">AI</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="font-semibold text-gray-700 block mb-1">Automation Level</label>
                  <select
                    value={customAutomation}
                    onChange={e => setCustomAutomation(e.target.value as WorkflowStep['automation'])}
                    className="w-full border border-gray-300 rounded-lg px-2.5 py-1.5 text-gray-900 text-xs bg-white"
                  >
                    <option value="Manual">Manual</option>
                    <option value="AI-assisted">AI-assisted</option>
                    <option value="Fully automated">Fully automated</option>
                  </select>
                </div>
              </div>

              <div className="pt-3 border-t border-gray-200 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowCustomModal(false)}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-xs font-semibold shadow-xs"
                >
                  Save Step
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
