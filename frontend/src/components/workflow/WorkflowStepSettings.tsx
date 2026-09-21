'use client';

import React, { useState } from 'react';
import { WorkflowStep, StepOwner, AutomationLevel, WorkflowCondition } from '../../types';
import { Sliders, Trash2, Plus, Settings2, HelpCircle, Bell, ArrowRight, ShieldCheck } from 'lucide-react';

interface Props {
  step: WorkflowStep | null;
  onUpdateStep: (updatedStep: WorkflowStep) => void;
  onDeleteStep: (stepId: string) => void;
}

export function WorkflowStepSettings({ step, onUpdateStep, onDeleteStep }: Props) {
  if (!step) {
    return (
      <div className="h-full bg-white border border-gray-200 rounded-xl p-8 flex flex-col items-center justify-center text-center text-gray-500">
        <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mb-3 text-gray-400">
          <Sliders size={22} />
        </div>
        <h4 className="text-sm font-bold text-gray-900">No Step Selected</h4>
        <p className="text-xs text-gray-500 max-w-xs mt-1">
          Select a hiring step from the left panel to configure its owner, automation rules, questions, and conditions.
        </p>
      </div>
    );
  }

  const [newQuestionText, setNewQuestionText] = useState('');

  const handleFieldChange = (key: keyof WorkflowStep, value: any) => {
    onUpdateStep({ ...step, [key]: value });
  };

  const handleConfigChange = (key: string, value: any) => {
    onUpdateStep({
      ...step,
      config: { ...step.config, [key]: value }
    });
  };

  const handleAddQuestion = () => {
    if (!newQuestionText.trim()) return;
    const currentQuestions = step.questions || [];
    const updated = [
      ...currentQuestions,
      { id: `q-${Date.now()}`, question: newQuestionText.trim(), isRequired: true }
    ];
    onUpdateStep({ ...step, questions: updated });
    setNewQuestionText('');
  };

  const handleRemoveQuestion = (qId: string) => {
    const updated = (step.questions || []).filter(q => q.id !== qId);
    onUpdateStep({ ...step, questions: updated });
  };

  return (
    <div className="h-full bg-white border border-gray-200 rounded-xl flex flex-col overflow-hidden shadow-2xs">
      {/* Settings Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50/70 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-gray-900">Step Settings</span>
            <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
              {step.category}
            </span>
          </div>
          <p className="text-[11px] text-gray-500 mt-0.5">Configure step behavior & execution rules</p>
        </div>

        <button
          onClick={() => onDeleteStep(step.id)}
          className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition"
          title="Delete Step"
        >
          <Trash2 size={16} />
        </button>
      </div>

      {/* Settings Scroll Content */}
      <div className="flex-1 p-5 overflow-y-auto space-y-6 text-xs">
        {/* Basic Step Information */}
        <div className="space-y-3.5">
          <h5 className="font-bold text-gray-900 border-b border-gray-100 pb-1.5 flex items-center gap-1.5 text-xs">
            <Settings2 size={14} className="text-gray-500" /> Basic Properties
          </h5>

          <div>
            <label className="font-semibold text-gray-700 block mb-1">Step Name *</label>
            <input
              type="text"
              value={step.name}
              onChange={e => handleFieldChange('name', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-gray-900 font-medium text-xs focus:ring-2 focus:ring-blue-600 outline-none"
            />
          </div>

          <div>
            <label className="font-semibold text-gray-700 block mb-1">Purpose / Description</label>
            <textarea
              value={step.purpose || ''}
              onChange={e => handleFieldChange('purpose', e.target.value)}
              placeholder="What is expected during this hiring step?"
              className="w-full border border-gray-300 rounded-lg p-2.5 text-gray-900 text-xs focus:ring-2 focus:ring-blue-600 outline-none h-16"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="font-semibold text-gray-700 block mb-1">Step Owner</label>
              <select
                value={step.owner}
                onChange={e => handleFieldChange('owner', e.target.value as StepOwner)}
                className="w-full border border-gray-300 rounded-lg px-2.5 py-1.5 text-gray-900 text-xs bg-white focus:ring-2 focus:ring-blue-600 outline-none"
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
              <label className="font-semibold text-gray-700 block mb-1">Duration (Mins)</label>
              <input
                type="number"
                value={step.durationMinutes || 30}
                onChange={e => handleFieldChange('durationMinutes', parseInt(e.target.value) || 0)}
                className="w-full border border-gray-300 rounded-lg px-2.5 py-1.5 text-gray-900 text-xs focus:ring-2 focus:ring-blue-600 outline-none"
              />
            </div>
          </div>
        </div>

        {/* HR Control over Automation */}
        <div className="space-y-3.5 pt-2">
          <h5 className="font-bold text-gray-900 border-b border-gray-100 pb-1.5 flex items-center gap-1.5 text-xs">
            <ShieldCheck size={14} className="text-blue-700" /> Automation Level (HR Control)
          </h5>

          <div className="space-y-2">
            {[
              { level: 'Manual', title: 'Manual', desc: 'Step is fully handled by HR / Human interviewers.' },
              { level: 'AI-assisted', title: 'AI-assisted', desc: 'AI prepares recommendations, transcripts, or drafts for HR approval.' },
              { level: 'Fully automated', title: 'Fully automated', desc: 'Platform executes step automatically based on configured conditions.' }
            ].map(item => (
              <label
                key={item.level}
                onClick={() => handleFieldChange('automation', item.level as AutomationLevel)}
                className={`flex items-start gap-2.5 p-2.5 rounded-lg border cursor-pointer transition ${
                  step.automation === item.level
                    ? 'bg-blue-50/70 border-blue-300 text-blue-900 ring-1 ring-blue-500'
                    : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name="automation"
                  checked={step.automation === item.level}
                  onChange={() => {}}
                  className="mt-0.5 text-blue-700"
                />
                <div>
                  <span className="font-semibold text-xs block text-gray-900">{item.title}</span>
                  <span className="text-[11px] text-gray-500">{item.desc}</span>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Evaluation / Passing Conditions */}
        <div className="space-y-3.5 pt-2">
          <h5 className="font-bold text-gray-900 border-b border-gray-100 pb-1.5 flex items-center gap-1.5 text-xs">
            <ArrowRight size={14} className="text-amber-700" /> Passing Conditions & Stage Movement
          </h5>

          <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg space-y-3">
            <div>
              <label className="font-semibold text-gray-700 block mb-1">Minimum Required Score (% or points)</label>
              <input
                type="number"
                placeholder="e.g., 70"
                value={step.passingScore || ''}
                onChange={e => handleFieldChange('passingScore', parseInt(e.target.value) || undefined)}
                className="w-full border border-gray-300 rounded-lg px-2.5 py-1.5 text-gray-900 text-xs bg-white"
              />
            </div>

            <div className="text-[11px] text-gray-600 space-y-1">
              <p className="font-medium text-gray-800">Rule logic:</p>
              <p>• If candidate score ≥ {step.passingScore || 70}% → Automatically advance to next step</p>
              <p>• If candidate score &lt; {step.passingScore || 70}% → Flag for HR Review / Reject</p>
            </div>
          </div>
        </div>

        {/* Screening / Interview Questions */}
        <div className="space-y-3.5 pt-2">
          <h5 className="font-bold text-gray-900 border-b border-gray-100 pb-1.5 flex items-center justify-between text-xs">
            <span className="flex items-center gap-1.5">
              <HelpCircle size={14} className="text-purple-600" /> Stage Questions ({step.questions?.length || 0})
            </span>
          </h5>

          <div className="space-y-2">
            {(step.questions || []).map((q, idx) => (
              <div key={q.id} className="flex items-center justify-between gap-2 p-2 bg-gray-50 border border-gray-200 rounded-lg text-xs">
                <span className="text-gray-800 font-medium">{idx + 1}. {q.question}</span>
                <button
                  onClick={() => handleRemoveQuestion(q.id)}
                  className="text-gray-400 hover:text-red-600 transition p-1"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))}

            <div className="flex items-center gap-2 pt-1">
              <input
                type="text"
                placeholder="Add a screening or interview question..."
                value={newQuestionText}
                onChange={e => setNewQuestionText(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleAddQuestion()}
                className="flex-1 border border-gray-300 rounded-lg px-3 py-1.5 text-xs text-gray-900 focus:ring-2 focus:ring-blue-600 outline-none"
              />
              <button
                onClick={handleAddQuestion}
                className="px-3 py-1.5 bg-gray-900 hover:bg-gray-800 text-white rounded-lg text-xs font-semibold"
              >
                Add
              </button>
            </div>
          </div>
        </div>

        {/* Notifications & Reminders */}
        <div className="space-y-3 pt-2">
          <h5 className="font-bold text-gray-900 border-b border-gray-100 pb-1.5 flex items-center gap-1.5 text-xs">
            <Bell size={14} className="text-emerald-600" /> Notifications & Alerts
          </h5>

          <div className="space-y-2">
            <label className="flex items-center gap-2 text-gray-700 cursor-pointer">
              <input
                type="checkbox"
                checked={step.notifications?.notifyCandidate ?? true}
                onChange={e => handleFieldChange('notifications', { ...(step.notifications || {}), notifyCandidate: e.target.checked })}
                className="rounded text-blue-700"
              />
              <span>Send notification email to candidate upon entering this step</span>
            </label>

            <label className="flex items-center gap-2 text-gray-700 cursor-pointer">
              <input
                type="checkbox"
                checked={step.notifications?.notifyInterviewer ?? true}
                onChange={e => handleFieldChange('notifications', { ...(step.notifications || {}), notifyInterviewer: e.target.checked })}
                className="rounded text-blue-700"
              />
              <span>Alert step owner ({step.owner}) when candidate arrives</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}
