'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useHRState } from '../../../../stores/useHRStore';
import { WORKFLOW_TEMPLATES, generateRecommendedWorkflow } from '../../../../data/workflowTemplates';
import { HiringWorkflow, WorkflowStep } from '../../../../types';
import { Search, Plus, Sparkles, LayoutTemplate, PenTool, CheckCircle2, ArrowRight, ArrowLeft, Briefcase, ChevronRight } from 'lucide-react';
import Link from 'next/link';

export default function CreateWorkflowPage() {
  const router = useRouter();
  const hrState = useHRState();

  const [step, setStep] = useState<1 | 2>(1);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [workflowName, setWorkflowName] = useState('');

  // Selected template state for Option 2
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>('tpl-software-engineer');

  const selectedJob = hrState.jobs.find(j => j.id === selectedJobId) || null;

  const filteredJobs = hrState.jobs.filter(j =>
    j.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    j.department.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSelectJob = (jobId: string) => {
    setSelectedJobId(jobId);
    const job = hrState.jobs.find(j => j.id === jobId);
    if (job) {
      setWorkflowName(`${job.title} Hiring Workflow`);
    }
    setStep(2);
  };

  const handleCreateFromRecommended = () => {
    if (!selectedJob) return;
    const rec = generateRecommendedWorkflow(selectedJob);

    const stepsWithIds: WorkflowStep[] = rec.steps.map((s, idx) => ({
      ...s,
      id: `st-${Date.now()}-${idx}`,
      order: idx + 1
    }));

    const newWf: HiringWorkflow = {
      id: `wf-${Date.now()}`,
      name: workflowName || `${selectedJob.title} Hiring Workflow`,
      jobId: selectedJob.id,
      jobTitle: selectedJob.title,
      department: selectedJob.department,
      version: 1,
      status: 'Draft',
      isActive: true,
      description: rec.explanation,
      ownerName: 'HR Recruiter',
      steps: stepsWithIds,
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0]
    };

    hrState.createWorkflow(newWf);
    router.push(`/workflows/${newWf.id}`);
  };

  const handleCreateFromTemplate = () => {
    if (!selectedJob) return;
    const tpl = WORKFLOW_TEMPLATES.find(t => t.id === selectedTemplateId) || WORKFLOW_TEMPLATES[0];

    const stepsWithIds: WorkflowStep[] = tpl.steps.map((s, idx) => ({
      ...s,
      id: `st-${Date.now()}-${idx}`,
      order: idx + 1
    }));

    const newWf: HiringWorkflow = {
      id: `wf-${Date.now()}`,
      name: workflowName || `${selectedJob.title} Hiring Workflow`,
      jobId: selectedJob.id,
      jobTitle: selectedJob.title,
      department: selectedJob.department,
      version: 1,
      status: 'Draft',
      isActive: true,
      description: tpl.description,
      ownerName: 'HR Recruiter',
      steps: stepsWithIds,
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0]
    };

    hrState.createWorkflow(newWf);
    router.push(`/workflows/${newWf.id}`);
  };

  const handleCreateFromScratch = () => {
    if (!selectedJob) return;
    const initialApplicationStep: WorkflowStep = {
      id: `st-${Date.now()}-1`,
      name: 'Application',
      category: 'Screening',
      type: 'DOCUMENT_COLLECTION',
      order: 1,
      purpose: 'Candidate applies for position.',
      owner: 'Recruiter',
      automation: 'Fully automated',
      isRequired: true,
      isEnabled: true,
      config: {}
    };

    const newWf: HiringWorkflow = {
      id: `wf-${Date.now()}`,
      name: workflowName || `${selectedJob.title} Hiring Workflow`,
      jobId: selectedJob.id,
      jobTitle: selectedJob.title,
      department: selectedJob.department,
      version: 1,
      status: 'Draft',
      isActive: true,
      description: 'Custom hiring workflow built from scratch.',
      ownerName: 'HR Recruiter',
      steps: [initialApplicationStep],
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0]
    };

    hrState.createWorkflow(newWf);
    router.push(`/workflows/${newWf.id}`);
  };

  const recommendedInfo = selectedJob ? generateRecommendedWorkflow(selectedJob) : null;

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Top Breadcrumb & Header */}
      <div className="flex items-center justify-between">
        <Link
          href="/workflows"
          className="text-xs font-semibold text-gray-600 hover:text-gray-900 flex items-center gap-1"
        >
          <ArrowLeft size={14} /> Back to Workflows
        </Link>
        <span className="text-xs font-semibold text-gray-400">Step {step} of 2</span>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-2xs space-y-2">
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">Create Hiring Workflow</h1>
        <p className="text-xs text-gray-500">
          Define how candidates move through your hiring process for an open job role.
        </p>
      </div>

      {/* STEP 1: Select Job / Role */}
      {step === 1 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-2xs space-y-6">
          <div>
            <h2 className="text-sm font-bold text-gray-900">Step 1: Select Job / Role</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Select an open job position from your database to configure its workflow.
            </p>
          </div>

          {/* Job Search Input */}
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder="Search jobs by title or department..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full border border-gray-300 rounded-lg pl-10 pr-4 py-2 text-xs text-gray-900 focus:ring-2 focus:ring-blue-600 outline-none"
            />
          </div>

          {/* Job List */}
          {hrState.jobs.length === 0 ? (
            <div className="p-8 text-center border border-dashed border-gray-200 rounded-xl space-y-3">
              <Briefcase size={32} className="mx-auto text-gray-400" />
              <div>
                <h3 className="text-xs font-bold text-gray-900">No jobs available</h3>
                <p className="text-xs text-gray-500 mt-1">Create a job first before defining its hiring workflow.</p>
              </div>
              <Link
                href="/jobs/create"
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-xs font-semibold shadow-xs"
              >
                <Plus size={14} /> Create Job
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden">
              {filteredJobs.map(job => (
                <div
                  key={job.id}
                  onClick={() => handleSelectJob(job.id)}
                  className="p-4 hover:bg-blue-50/50 cursor-pointer transition flex items-center justify-between group"
                >
                  <div>
                    <h3 className="text-xs font-bold text-gray-900 group-hover:text-blue-700">{job.title}</h3>
                    <p className="text-[11px] text-gray-500 mt-0.5">
                      Department: <span className="font-semibold text-gray-700">{job.department}</span> • Experience: <span className="font-semibold text-gray-700">{job.minExperience}–{job.maxExperience} years</span> • Location: {job.location}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-semibold text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                      {job.applicantsCount || 0} applicants
                    </span>
                    <ChevronRight size={16} className="text-gray-400 group-hover:text-blue-700" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* STEP 2: Choose Workflow Type */}
      {step === 2 && selectedJob && recommendedInfo && (
        <div className="space-y-6">
          {/* Selected Job Card Header */}
          <div className="bg-blue-50/70 border border-blue-200 rounded-xl p-4 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-blue-700 uppercase tracking-wider">Selected Job</span>
              <h3 className="text-sm font-bold text-gray-900">{selectedJob.title}</h3>
              <p className="text-xs text-gray-600 mt-0.5">
                {selectedJob.department} • {selectedJob.minExperience}–{selectedJob.maxExperience} yrs exp • {selectedJob.location}
              </p>
            </div>
            <button
              onClick={() => setStep(1)}
              className="text-xs font-semibold text-blue-700 hover:text-blue-900 underline"
            >
              Change Job
            </button>
          </div>

          {/* Workflow Name Input */}
          <div className="bg-white border border-gray-200 rounded-xl p-4">
            <label className="font-bold text-xs text-gray-800 block mb-1">Workflow Title</label>
            <input
              type="text"
              value={workflowName}
              onChange={e => setWorkflowName(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-xs font-semibold text-gray-900 focus:ring-2 focus:ring-blue-600 outline-none"
            />
          </div>

          <h2 className="text-sm font-bold text-gray-900">How would you like to create the hiring process?</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* OPTION 1: Recommended Workflow */}
            <div className="bg-white border-2 border-blue-200 hover:border-blue-600 rounded-xl p-5 shadow-2xs flex flex-col justify-between space-y-4 relative transition group">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                    <Sparkles size={16} />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-gray-900">Recommended workflow</h3>
                    <span className="text-[10px] text-blue-700 font-semibold">Tailored for {selectedJob.title}</span>
                  </div>
                </div>

                <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-xs space-y-2">
                  <p className="font-semibold text-gray-800 text-[11px]">Why this workflow?</p>
                  <p className="text-[11px] text-gray-600 leading-relaxed">{recommendedInfo.explanation}</p>
                </div>

                {/* Steps Preview */}
                <div className="space-y-1">
                  <p className="text-[11px] font-bold text-gray-500 uppercase">Suggested Stages ({recommendedInfo.steps.length})</p>
                  <div className="space-y-1">
                    {recommendedInfo.steps.map((s, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-[11px] text-gray-700 bg-gray-50 px-2.5 py-1 rounded border border-gray-100">
                        <span className="font-bold text-blue-700">{idx + 1}.</span>
                        <span className="font-medium">{s.name}</span>
                        <span className="text-[9px] ml-auto text-gray-400 uppercase">{s.automation}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <button
                onClick={handleCreateFromRecommended}
                className="w-full py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-xs font-semibold shadow-xs flex items-center justify-center gap-1.5 transition mt-4"
              >
                Use Recommended Workflow <ArrowRight size={14} />
              </button>
            </div>

            {/* OPTION 2: Start from template */}
            <div className="bg-white border border-gray-200 hover:border-gray-400 rounded-xl p-5 shadow-2xs flex flex-col justify-between space-y-4 transition">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-gray-100 text-gray-700 flex items-center justify-center font-bold">
                    <LayoutTemplate size={16} />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-gray-900">Start from template</h3>
                    <span className="text-[10px] text-gray-500">Industry standard templates</span>
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-gray-700 block mb-1">Select Role Template</label>
                  <select
                    value={selectedTemplateId}
                    onChange={e => setSelectedTemplateId(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-2.5 py-1.5 text-xs text-gray-900 bg-white"
                  >
                    <optgroup label="Technical Roles">
                      {WORKFLOW_TEMPLATES.filter(t => t.category === 'Technical').map(t => (
                        <option key={t.id} value={t.id}>{t.name}</option>
                      ))}
                    </optgroup>
                    <optgroup label="Non-Technical Roles">
                      {WORKFLOW_TEMPLATES.filter(t => t.category === 'Non-Technical').map(t => (
                        <option key={t.id} value={t.id}>{t.name}</option>
                      ))}
                    </optgroup>
                    <optgroup label="Leadership">
                      {WORKFLOW_TEMPLATES.filter(t => t.category === 'Leadership').map(t => (
                        <option key={t.id} value={t.id}>{t.name}</option>
                      ))}
                    </optgroup>
                  </select>
                </div>

                {/* Selected template info */}
                {(() => {
                  const currentTpl = WORKFLOW_TEMPLATES.find(t => t.id === selectedTemplateId);
                  return currentTpl ? (
                    <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-xs space-y-2">
                      <p className="text-[11px] text-gray-600">{currentTpl.description}</p>
                      <p className="text-[10px] font-bold text-gray-500 uppercase">{currentTpl.steps.length} predefined stages</p>
                    </div>
                  ) : null;
                })()}
              </div>

              <button
                onClick={handleCreateFromTemplate}
                className="w-full py-2 border border-gray-300 hover:bg-gray-50 text-gray-800 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition mt-4"
              >
                Choose Template <ArrowRight size={14} />
              </button>
            </div>

            {/* OPTION 3: Build manually */}
            <div className="bg-white border border-gray-200 hover:border-gray-400 rounded-xl p-5 shadow-2xs flex flex-col justify-between space-y-4 transition">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-gray-100 text-gray-700 flex items-center justify-center font-bold">
                    <PenTool size={16} />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-gray-900">Build manually</h3>
                    <span className="text-[10px] text-gray-500">Create every step yourself</span>
                  </div>
                </div>

                <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-xs text-gray-600">
                  Starts with an initial Application step. Add, reorder, and configure custom screening, interview, and approval stages.
                </div>
              </div>

              <button
                onClick={handleCreateFromScratch}
                className="w-full py-2 border border-gray-300 hover:bg-gray-50 text-gray-800 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition mt-4"
              >
                Start from Scratch <ArrowRight size={14} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
