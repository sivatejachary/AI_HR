'use client';

import React, { useState } from 'react';
import { HiringWorkflow, WorkflowStep } from '../../types';
import { CategorizedAddStepMenu } from './CategorizedAddStepMenu';
import { WorkflowStepSettings } from './WorkflowStepSettings';
import { WorkflowFlowView } from './WorkflowFlowView';
import { WorkflowCandidatesView } from './WorkflowCandidatesView';
import { WorkflowVersionsView } from './WorkflowVersionsView';
import { AgentControlPanel } from './AgentControlPanel';
import { useHRState } from '../../stores/useHRStore';
import {
  GitFork,
  Save,
  CheckCircle2,
  List,
  Network,
  Users,
  History,
  GitBranch,
  ArrowUp,
  ArrowDown,
  Copy,
  Trash2,
  UserCheck,
  Bot,
  Sliders,
  Sparkles,
  ChevronRight
} from 'lucide-react';

interface Props {
  workflow: HiringWorkflow;
  onSaveWorkflow?: (steps: WorkflowStep[]) => void;
}

export function WorkflowEditor({ workflow, onSaveWorkflow }: Props) {
  const hrState = useHRState();
  const [activeTab, setActiveTab] = useState<'Workflow' | 'Candidates' | 'Activity' | 'Versions'>('Workflow');
  const [viewMode, setViewMode] = useState<'List' | 'Flow'>('List');
  
  const [currentWorkflow, setCurrentWorkflow] = useState<HiringWorkflow>(workflow);
  const [selectedStepId, setSelectedStepId] = useState<string | null>(workflow.steps[0]?.id || null);

  // Sync if prop changes
  React.useEffect(() => {
    setCurrentWorkflow(workflow);
    if (workflow.steps.length > 0 && !selectedStepId) {
      setSelectedStepId(workflow.steps[0].id);
    }
  }, [workflow]);

  const selectedStep = currentWorkflow.steps.find(s => s.id === selectedStepId) || null;

  // Step manipulation handlers
  const handleAddStep = (partialStep: Partial<WorkflowStep>) => {
    const newStep: WorkflowStep = {
      id: `step-${Date.now()}`,
      name: partialStep.name || 'New Step',
      category: partialStep.category || 'Screening',
      type: partialStep.type || 'HUMAN_ACTION',
      order: currentWorkflow.steps.length + 1,
      purpose: partialStep.purpose || '',
      owner: partialStep.owner || 'HR',
      automation: partialStep.automation || 'Manual',
      durationMinutes: partialStep.durationMinutes || 30,
      isRequired: partialStep.isRequired ?? true,
      isEnabled: true,
      questions: [],
      config: partialStep.config || {}
    };

    const updatedSteps = [...currentWorkflow.steps, newStep];
    const updatedWf = { ...currentWorkflow, steps: updatedSteps };
    setCurrentWorkflow(updatedWf);
    setSelectedStepId(newStep.id);
  };

  const handleUpdateStep = (updatedStep: WorkflowStep) => {
    const updatedSteps = currentWorkflow.steps.map(s => s.id === updatedStep.id ? updatedStep : s);
    setCurrentWorkflow({ ...currentWorkflow, steps: updatedSteps });
  };

  const handleDeleteStep = (stepId: string) => {
    const filteredSteps = currentWorkflow.steps
      .filter(s => s.id !== stepId)
      .map((s, idx) => ({ ...s, order: idx + 1 }));

    setCurrentWorkflow({ ...currentWorkflow, steps: filteredSteps });
    if (selectedStepId === stepId) {
      setSelectedStepId(filteredSteps[0]?.id || null);
    }
  };

  const handleMoveUp = (index: number) => {
    if (index === 0) return;
    const stepsCopy = [...currentWorkflow.steps];
    const temp = stepsCopy[index - 1];
    stepsCopy[index - 1] = stepsCopy[index];
    stepsCopy[index] = temp;
    
    // Reassign order
    const reordered = stepsCopy.map((s, idx) => ({ ...s, order: idx + 1 }));
    setCurrentWorkflow({ ...currentWorkflow, steps: reordered });
  };

  const handleMoveDown = (index: number) => {
    if (index === currentWorkflow.steps.length - 1) return;
    const stepsCopy = [...currentWorkflow.steps];
    const temp = stepsCopy[index + 1];
    stepsCopy[index + 1] = stepsCopy[index];
    stepsCopy[index] = temp;

    // Reassign order
    const reordered = stepsCopy.map((s, idx) => ({ ...s, order: idx + 1 }));
    setCurrentWorkflow({ ...currentWorkflow, steps: reordered });
  };

  const handleDuplicateStep = (step: WorkflowStep) => {
    const duplicated: WorkflowStep = {
      ...step,
      id: `step-${Date.now()}`,
      name: `${step.name} (Copy)`,
      order: currentWorkflow.steps.length + 1
    };
    const updatedSteps = [...currentWorkflow.steps, duplicated];
    setCurrentWorkflow({ ...currentWorkflow, steps: updatedSteps });
    setSelectedStepId(duplicated.id);
  };

  const handleSaveDraft = () => {
    hrState.updateWorkflow({ ...currentWorkflow, status: 'Draft' });
    if (onSaveWorkflow) onSaveWorkflow(currentWorkflow.steps);
  };

  const handlePublish = () => {
    hrState.publishWorkflow(currentWorkflow.id);
    if (onSaveWorkflow) onSaveWorkflow(currentWorkflow.steps);
  };

  const handleArchive = () => {
    hrState.archiveWorkflow(currentWorkflow.id);
  };

  const handleDuplicateWorkflow = () => {
    hrState.duplicateWorkflow(currentWorkflow.id);
  };

  return (
    <div className="flex flex-col h-full bg-[#F8F9FB] space-y-4">
      {/* Top Header Card */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-2xs shrink-0 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5">
              <h2 className="text-lg font-bold text-gray-900 tracking-tight">{currentWorkflow.name}</h2>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                currentWorkflow.status === 'Published'
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : currentWorkflow.status === 'Draft'
                  ? 'bg-amber-50 text-amber-700 border-amber-200'
                  : 'bg-gray-100 text-gray-600 border-gray-200'
              }`}>
                {currentWorkflow.status}
              </span>
              <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600 font-semibold border border-gray-200">
                v{currentWorkflow.version}
              </span>
            </div>
            <p className="text-xs text-gray-500">
              Role: <span className="font-semibold text-gray-800">{currentWorkflow.jobTitle || 'Unassigned Role'}</span> • Department: <span className="font-semibold text-gray-800">{currentWorkflow.department || 'General'}</span>
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2.5 flex-wrap">
            <button
              onClick={handleSaveDraft}
              className="px-3.5 py-1.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-xs font-semibold shadow-2xs transition flex items-center gap-1.5"
            >
              <Save size={14} /> Save Draft
            </button>

            <button
              onClick={handlePublish}
              className="px-4 py-1.5 bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold rounded-lg shadow-xs transition flex items-center gap-1.5"
            >
              <CheckCircle2 size={14} /> Publish Version
            </button>

            <button
              onClick={handleDuplicateWorkflow}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-xs font-medium transition"
              title="Duplicate Workflow"
            >
              Duplicate
            </button>

            <button
              onClick={handleArchive}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-gray-500 hover:text-red-700 hover:bg-red-50 text-xs font-medium transition"
              title="Archive Workflow"
            >
              Archive
            </button>
          </div>
        </div>

        {/* Navigation Tabs & View Mode Switcher */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t border-gray-100 pt-3">
          <div className="flex items-center gap-1 border-b sm:border-b-0 border-gray-200">
            {[
              { key: 'Workflow', label: 'Workflow Builder', icon: GitFork },
              { key: 'Candidates', label: `Candidates (${hrState.applications.length})`, icon: Users },
              { key: 'Activity', label: 'Activity Log', icon: History },
              { key: 'Versions', label: `Versions (v${currentWorkflow.version})`, icon: GitBranch }
            ].map(tab => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.key;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition ${
                    isActive
                      ? 'bg-blue-50 text-blue-800 font-bold border border-blue-200'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <Icon size={14} /> {tab.label}
                </button>
              );
            })}
          </div>

          {/* View Toggle (List View vs Flow View) */}
          {activeTab === 'Workflow' && (
            <div className="flex items-center p-0.5 bg-gray-100 border border-gray-200 rounded-lg text-xs">
              <button
                onClick={() => setViewMode('List')}
                className={`px-3 py-1 rounded-md text-xs font-semibold flex items-center gap-1.5 transition ${
                  viewMode === 'List' ? 'bg-white text-gray-900 shadow-2xs font-bold' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <List size={13} /> List View
              </button>
              <button
                onClick={() => setViewMode('Flow')}
                className={`px-3 py-1 rounded-md text-xs font-semibold flex items-center gap-1.5 transition ${
                  viewMode === 'Flow' ? 'bg-white text-gray-900 shadow-2xs font-bold' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Network size={13} /> Flow View
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Tab Content */}
      <div className="flex-1 overflow-hidden space-y-4">
        {activeTab === 'Workflow' && (
          <>
            <AgentControlPanel
              workflowId={currentWorkflow.id}
              jobId={currentWorkflow.jobId}
              isPaused={currentWorkflow.isPaused}
              onTogglePause={() => setCurrentWorkflow(prev => ({ ...prev, isPaused: !prev.isPaused }))}
            />

            <div className="h-[calc(100vh-380px)] min-h-[480px] flex flex-col md:flex-row gap-5">
            {/* Left Panel: Steps List (List View or Flow Canvas) */}
            {viewMode === 'List' ? (
              <div className="flex-1 bg-white border border-gray-200 rounded-xl flex flex-col overflow-hidden shadow-2xs">
                {/* Steps List Bar */}
                <div className="p-4 border-b border-gray-200 bg-gray-50/70 flex items-center justify-between">
                  <div>
                    <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                      Workflow Pipeline ({currentWorkflow.steps.length} Steps)
                    </h3>
                    <p className="text-[11px] text-gray-500">Drag or reorder steps candidates will pass through</p>
                  </div>
                  <CategorizedAddStepMenu onAddStep={handleAddStep} />
                </div>

                {/* Steps List Scroll area */}
                <div className="flex-1 p-4 overflow-y-auto space-y-2.5">
                  {currentWorkflow.steps.length === 0 ? (
                    <div className="p-8 text-center text-gray-500 text-xs">
                      <p className="font-semibold text-gray-700">No steps in this workflow yet</p>
                      <p className="mt-1 text-gray-400">Click &quot;+ Add Step&quot; above to begin defining hiring stages.</p>
                    </div>
                  ) : (
                    currentWorkflow.steps.map((step, idx) => {
                      const isSelected = step.id === selectedStepId;
                      return (
                        <div
                          key={step.id}
                          onClick={() => setSelectedStepId(step.id)}
                          className={`p-3.5 rounded-xl border transition cursor-pointer flex items-center justify-between gap-3 ${
                            isSelected
                              ? 'bg-blue-50/60 border-blue-600 ring-1 ring-blue-600 shadow-2xs'
                              : 'bg-white border-gray-200 hover:border-gray-300 hover:bg-gray-50/50'
                          }`}
                        >
                          <div className="flex items-center gap-3 min-w-0">
                            <div className={`w-7 h-7 rounded-lg font-bold text-xs flex items-center justify-center shrink-0 ${
                              isSelected ? 'bg-blue-700 text-white' : 'bg-gray-100 text-gray-700'
                            }`}>
                              {idx + 1}
                            </div>

                            <div className="min-w-0">
                              <div className="flex items-center gap-2">
                                <h4 className="text-xs font-bold text-gray-900 truncate">{step.name}</h4>
                                <span className="text-[10px] uppercase font-bold px-1.5 py-0.2 rounded bg-gray-100 text-gray-600">
                                  {step.category}
                                </span>
                              </div>
                              <p className="text-[11px] text-gray-500 truncate mt-0.5">
                                Owner: <span className="font-medium text-gray-700">{step.owner}</span> • {step.purpose || 'No description'}
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2 shrink-0" onClick={e => e.stopPropagation()}>
                            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${
                              step.automation === 'Fully automated'
                                ? 'bg-purple-50 text-purple-700 border-purple-200'
                                : step.automation === 'AI-assisted'
                                ? 'bg-indigo-50 text-indigo-700 border-indigo-200'
                                : 'bg-gray-100 text-gray-700 border-gray-200'
                            }`}>
                              {step.automation}
                            </span>

                            {/* Move Up/Down Controls */}
                            <div className="flex items-center border border-gray-200 rounded-lg bg-white">
                              <button
                                disabled={idx === 0}
                                onClick={() => handleMoveUp(idx)}
                                className="p-1 hover:bg-gray-100 text-gray-600 disabled:opacity-30 rounded-l-lg"
                                title="Move Up"
                              >
                                <ArrowUp size={13} />
                              </button>
                              <button
                                disabled={idx === currentWorkflow.steps.length - 1}
                                onClick={() => handleMoveDown(idx)}
                                className="p-1 hover:bg-gray-100 text-gray-600 disabled:opacity-30 rounded-r-lg border-l border-gray-200"
                                title="Move Down"
                              >
                                <ArrowDown size={13} />
                              </button>
                            </div>

                            <button
                              onClick={() => handleDuplicateStep(step)}
                              className="p-1 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
                              title="Duplicate Step"
                            >
                              <Copy size={13} />
                            </button>

                            <button
                              onClick={() => handleDeleteStep(step.id)}
                              className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg"
                              title="Delete Step"
                            >
                              <Trash2 size={13} />
                            </button>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            ) : (
              <div className="flex-1 bg-white border border-gray-200 rounded-xl overflow-hidden shadow-2xs">
                <WorkflowFlowView
                  steps={currentWorkflow.steps}
                  selectedStepId={selectedStepId}
                  onSelectStep={setSelectedStepId}
                />
              </div>
            )}

            {/* Right Panel: Step Settings */}
            <div className="w-full md:w-[380px] shrink-0 h-full">
              <WorkflowStepSettings
                step={selectedStep}
                onUpdateStep={handleUpdateStep}
                onDeleteStep={handleDeleteStep}
              />
            </div>
          </div>
        </>
      )}

        {activeTab === 'Candidates' && (
          <WorkflowCandidatesView
            steps={currentWorkflow.steps}
            applications={hrState.applications}
            candidates={hrState.candidates}
          />
        )}

        {activeTab === 'Activity' && (
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-2xs">
            <div className="p-4 border-b border-gray-200 bg-gray-50/60 font-bold text-xs text-gray-900">
              Workflow Activity Audit Log
            </div>
            <div className="divide-y divide-gray-100 text-xs">
              {hrState.activityLogs.slice(0, 10).map(log => (
                <div key={log.id} className="p-3.5 flex items-center justify-between">
                  <div>
                    <span className="font-semibold text-gray-900">{log.action}</span>
                    <p className="text-[11px] text-gray-500 mt-0.5">{log.result}</p>
                  </div>
                  <span className="text-[11px] text-gray-400">{log.timestamp}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'Versions' && (
          <WorkflowVersionsView
            workflow={currentWorkflow}
            onPublishVersion={handlePublish}
            onArchiveWorkflow={handleArchive}
          />
        )}
      </div>
    </div>
  );
}
