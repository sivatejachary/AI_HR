'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useHRState } from '../../../../stores/useHRStore';
import { Job, WorkplaceType, JobDistribution } from '../../../../types';
import {
  Briefcase,
  Check,
  ArrowRight,
  ArrowLeft,
  Share2,
  FileSpreadsheet,
  Upload,
  Globe,
  Plus,
  Trash2
} from 'lucide-react';

export default function CreateJobWizardPage() {
  const router = useRouter();
  const hrState = useHRState();
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    title: '',
    department: 'Engineering',
    employmentType: 'Full-time',
    workplaceType: 'REMOTE' as WorkplaceType,
    location: '',
    minExperience: 2,
    maxExperience: 5,
    salaryRange: '$100,000 - $140,000',
    openings: 1,
    description: '',
    responsibilities: '',
    requirements: '',
    preferredSkills: '',
    education: "Bachelor's Degree in Computer Science or related field",
    noticePeriod: '30 Days',
    applicationDeadline: '',
    workflowId: hrState.workflows[0]?.id || 'wf-se-1',
    sourcingMethods: ['POST_JOB', 'CREATE_FORM'] as Array<'POST_JOB' | 'CREATE_FORM' | 'IMPORT_EXISTING'>,
    selectedPlatforms: ['CAREER_PAGE', 'LINKEDIN', 'NAUKRI'],
    customQuestions: [
      { id: 'q-1', question: 'What is your current notice period?', type: 'TEXT', required: true }
    ]
  });

  const [newQuestionText, setNewQuestionText] = useState('');

  const toggleSourcingMethod = (method: 'POST_JOB' | 'CREATE_FORM' | 'IMPORT_EXISTING') => {
    setFormData(prev => {
      const exists = prev.sourcingMethods.includes(method);
      const updated = exists
        ? prev.sourcingMethods.filter(m => m !== method)
        : [...prev.sourcingMethods, method];
      return { ...prev, sourcingMethods: updated.length > 0 ? updated : [method] };
    });
  };

  const togglePlatform = (platform: string) => {
    setFormData(prev => {
      const exists = prev.selectedPlatforms.includes(platform);
      const updated = exists ? prev.selectedPlatforms.filter(p => p !== platform) : [...prev.selectedPlatforms, platform];
      return { ...prev, selectedPlatforms: updated };
    });
  };

  const addCustomQuestion = () => {
    if (!newQuestionText.trim()) return;
    setFormData(prev => ({
      ...prev,
      customQuestions: [
        ...prev.customQuestions,
        { id: `q-${Date.now()}`, question: newQuestionText.trim(), type: 'TEXT', required: false }
      ]
    }));
    setNewQuestionText('');
  };

  const removeCustomQuestion = (id: string) => {
    setFormData(prev => ({
      ...prev,
      customQuestions: prev.customQuestions.filter(q => q.id !== id)
    }));
  };

  const handleFinishWizard = async (status: 'PUBLISHED' | 'DRAFT') => {
    if (!formData.title.trim()) {
      alert('Please enter a Job Title');
      return;
    }

    setIsSubmitting(true);
    const selectedWf = hrState.workflows.find(w => w.id === formData.workflowId);
    const jobId = `job-${Date.now()}`;

    const initialDists: JobDistribution[] = formData.selectedPlatforms.map(p => ({
      id: `dist-${Date.now()}-${p}`,
      jobId: jobId,
      platform: p as any,
      connectionStatus: 'CONNECTED',
      publicationStatus: status === 'PUBLISHED' ? 'PUBLISHED' : 'READY',
      publishedAt: status === 'PUBLISHED' ? new Date().toISOString().split('T')[0] : undefined
    }));

    const newJob: Job = {
      id: jobId,
      title: formData.title,
      department: formData.department,
      employmentType: formData.employmentType,
      workplaceType: formData.workplaceType,
      location: formData.location || 'Remote',
      minExperience: formData.minExperience,
      maxExperience: formData.maxExperience,
      salaryRange: formData.salaryRange,
      openings: formData.openings,
      description: formData.description || 'Job details pending...',
      responsibilities: formData.responsibilities || 'Responsibilities details pending...',
      requirements: formData.requirements || 'Requirements details pending...',
      preferredSkills: formData.preferredSkills ? formData.preferredSkills.split(',').map(s => s.trim()) : [],
      education: formData.education,
      noticePeriod: formData.noticePeriod,
      applicationDeadline: formData.applicationDeadline,
      hiringManager: 'HR Team',
      workflowId: formData.workflowId,
      workflowName: selectedWf?.name || 'Standard Recruitment Workflow',
      status: status,
      distributions: initialDists,
      sourcingMethods: formData.sourcingMethods,
      createdAt: new Date().toISOString().split('T')[0],
      applicantsCount: 0
    };

    try {
      const createdJob = await hrState.createJob(newJob);
      const targetId = createdJob?.id || jobId;

      if (formData.sourcingMethods.includes('CREATE_FORM')) {
        try {
          await api.createJobGoogleForm(targetId);
        } catch (err) {
          console.warn('[Wizard] Auto-create Google Form notice', err);
        }
      }
      router.push(`/jobs/${targetId}?created=true`);
    } catch (e) {
      console.error('[Wizard] Error creating job', e);
      router.push(`/jobs/${jobId}?created=true`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-xs flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900 tracking-tight">Create Job</h1>
          <p className="text-xs text-gray-500 mt-1">Define position requirements, sourcing channels, and distribution settings.</p>
        </div>
        <span className="text-xs font-medium text-gray-700 bg-gray-100 px-3 py-1 rounded border border-gray-200">
          Step {currentStep} of 4
        </span>
      </div>

      {/* Stepper Tabs */}
      <div className="grid grid-cols-4 gap-2 text-xs">
        {[
          { step: 1, label: '1. Job Details' },
          { step: 2, label: '2. Candidate Collection' },
          { step: 3, label: '3. Channel Configuration' },
          { step: 4, label: '4. Review & Launch' }
        ].map(item => (
          <div
            key={item.step}
            className={`py-2.5 px-3 rounded border text-center font-medium transition ${
              currentStep === item.step
                ? 'bg-blue-900 text-white border-blue-900 font-semibold'
                : currentStep > item.step
                ? 'bg-gray-100 text-gray-800 border-gray-300'
                : 'bg-white text-gray-400 border-gray-200'
            }`}
          >
            {item.label}
          </div>
        ))}
      </div>

      {/* STEP 1: JOB DETAILS */}
      {currentStep === 1 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-6 shadow-xs">
          <div className="border-b border-gray-100 pb-3">
            <h2 className="text-base font-semibold text-gray-900">Job Details</h2>
            <p className="text-xs text-gray-500">Enter general position requirements and metadata.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="text-gray-700 font-medium block mb-1">Job Title *</label>
              <input
                type="text"
                placeholder="e.g. Senior Python Developer"
                value={formData.title}
                onChange={e => setFormData({ ...formData, title: e.target.value })}
                className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
              />
            </div>

            <div>
              <label className="text-gray-700 font-medium block mb-1">Department *</label>
              <select
                value={formData.department}
                onChange={e => setFormData({ ...formData, department: e.target.value })}
                className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-700"
              >
                <option value="Engineering">Engineering</option>
                <option value="Product">Product</option>
                <option value="Design">Design</option>
                <option value="Sales">Sales</option>
                <option value="Marketing">Marketing</option>
                <option value="Human Resources">Human Resources</option>
              </select>
            </div>

            <div>
              <label className="text-gray-700 font-medium block mb-1">Employment Type *</label>
              <select
                value={formData.employmentType}
                onChange={e => setFormData({ ...formData, employmentType: e.target.value })}
                className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-700"
              >
                <option value="Full-time">Full-time</option>
                <option value="Part-time">Part-time</option>
                <option value="Contract">Contract</option>
                <option value="Internship">Internship</option>
              </select>
            </div>

            <div>
              <label className="text-gray-700 font-medium block mb-1">Workplace Type *</label>
              <select
                value={formData.workplaceType}
                onChange={e => setFormData({ ...formData, workplaceType: e.target.value as WorkplaceType })}
                className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-700"
              >
                <option value="REMOTE">Remote</option>
                <option value="HYBRID">Hybrid</option>
                <option value="ON_SITE">On-Site</option>
              </select>
            </div>

            <div>
              <label className="text-gray-700 font-medium block mb-1">Location *</label>
              <input
                type="text"
                placeholder="e.g. Hyderabad, India"
                value={formData.location}
                onChange={e => setFormData({ ...formData, location: e.target.value })}
                className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
              />
            </div>

            <div>
              <label className="text-gray-700 font-medium block mb-1">Experience Range (Years)</label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  placeholder="Min"
                  value={formData.minExperience}
                  onChange={e => setFormData({ ...formData, minExperience: parseInt(e.target.value) || 0 })}
                  className="w-1/2 bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 text-center focus:outline-none focus:border-blue-700"
                />
                <span className="text-gray-400">to</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={formData.maxExperience}
                  onChange={e => setFormData({ ...formData, maxExperience: parseInt(e.target.value) || 0 })}
                  className="w-1/2 bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 text-center focus:outline-none focus:border-blue-700"
                />
              </div>
            </div>

            <div>
              <label className="text-gray-700 font-medium block mb-1">Salary Range</label>
              <input
                type="text"
                placeholder="e.g. $100,000 - $140,000"
                value={formData.salaryRange}
                onChange={e => setFormData({ ...formData, salaryRange: e.target.value })}
                className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
              />
            </div>

            <div>
              <label className="text-gray-700 font-medium block mb-1">Number of Openings</label>
              <input
                type="number"
                value={formData.openings}
                onChange={e => setFormData({ ...formData, openings: parseInt(e.target.value) || 1 })}
                className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-700"
              />
            </div>
          </div>

          <div className="space-y-4 text-xs pt-2">
            <div>
              <label className="text-gray-700 font-medium block mb-1">Job Description</label>
              <textarea
                rows={4}
                placeholder="Enter detailed role overview and objectives..."
                value={formData.description}
                onChange={e => setFormData({ ...formData, description: e.target.value })}
                className="w-full bg-gray-50 border border-gray-300 rounded p-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
              />
            </div>

            <div>
              <label className="text-gray-700 font-medium block mb-1">Key Responsibilities</label>
              <textarea
                rows={3}
                placeholder="List key daily responsibilities..."
                value={formData.responsibilities}
                onChange={e => setFormData({ ...formData, responsibilities: e.target.value })}
                className="w-full bg-gray-50 border border-gray-300 rounded p-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
              />
            </div>

            <div>
              <label className="text-gray-700 font-medium block mb-1">Required Skills (Comma separated)</label>
              <input
                type="text"
                placeholder="e.g. Python, FastAPI, PostgreSQL, Docker"
                value={formData.requirements}
                onChange={e => setFormData({ ...formData, requirements: e.target.value })}
                className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
              />
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-gray-100">
            <button
              onClick={() => {
                if (!formData.title.trim()) {
                  alert('Please enter a job title before continuing.');
                  return;
                }
                setCurrentStep(2);
              }}
              className="px-4 py-2 bg-blue-900 hover:bg-blue-800 text-white text-xs font-medium rounded flex items-center gap-2 transition"
            >
              Continue <ArrowRight size={14} />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: CANDIDATE COLLECTION */}
      {currentStep === 2 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-6 shadow-xs">
          <div>
            <h2 className="text-base font-semibold text-gray-900">Candidate Collection</h2>
            <p className="text-xs text-gray-500 mt-0.5">How would you like to receive candidates for this position?</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Post Job Option */}
            <div
              onClick={() => toggleSourcingMethod('POST_JOB')}
              className={`p-4 rounded-md border cursor-pointer transition flex flex-col justify-between space-y-3 ${
                formData.sourcingMethods.includes('POST_JOB')
                  ? 'bg-blue-50 border-blue-700 text-gray-900'
                  : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <Share2 size={18} className={formData.sourcingMethods.includes('POST_JOB') ? 'text-blue-900' : 'text-gray-400'} />
                <div className={`w-4 h-4 rounded border flex items-center justify-center text-xs ${
                  formData.sourcingMethods.includes('POST_JOB') ? 'bg-blue-900 border-blue-900 text-white' : 'border-gray-300'
                }`}>
                  {formData.sourcingMethods.includes('POST_JOB') && <Check size={10} />}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-900">Post Job</h3>
                <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                  Publish to connected job boards and company career page.
                </p>
              </div>
            </div>

            {/* Application Form Option */}
            <div
              onClick={() => toggleSourcingMethod('CREATE_FORM')}
              className={`p-4 rounded-md border cursor-pointer transition flex flex-col justify-between space-y-3 ${
                formData.sourcingMethods.includes('CREATE_FORM')
                  ? 'bg-blue-50 border-blue-700 text-gray-900'
                  : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <FileSpreadsheet size={18} className={formData.sourcingMethods.includes('CREATE_FORM') ? 'text-blue-900' : 'text-gray-400'} />
                <div className={`w-4 h-4 rounded border flex items-center justify-center text-xs ${
                  formData.sourcingMethods.includes('CREATE_FORM') ? 'bg-blue-900 border-blue-900 text-white' : 'border-gray-300'
                }`}>
                  {formData.sourcingMethods.includes('CREATE_FORM') && <Check size={10} />}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-900">Create Application Form</h3>
                <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                  Create a dedicated application form link for this position.
                </p>
              </div>
            </div>

            {/* Import Existing Candidates Option */}
            <div
              onClick={() => toggleSourcingMethod('IMPORT_EXISTING')}
              className={`p-4 rounded-md border cursor-pointer transition flex flex-col justify-between space-y-3 ${
                formData.sourcingMethods.includes('IMPORT_EXISTING')
                  ? 'bg-blue-50 border-blue-700 text-gray-900'
                  : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <Upload size={18} className={formData.sourcingMethods.includes('IMPORT_EXISTING') ? 'text-blue-900' : 'text-gray-400'} />
                <div className={`w-4 h-4 rounded border flex items-center justify-center text-xs ${
                  formData.sourcingMethods.includes('IMPORT_EXISTING') ? 'bg-blue-900 border-blue-900 text-white' : 'border-gray-300'
                }`}>
                  {formData.sourcingMethods.includes('IMPORT_EXISTING') && <Check size={10} />}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-900">Import Candidates</h3>
                <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                  Import candidates from CSV, Excel, Google Sheets, or database.
                </p>
              </div>
            </div>
          </div>

          <div className="flex justify-between pt-4 border-t border-gray-100">
            <button
              onClick={() => setCurrentStep(1)}
              className="px-4 py-1.5 bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 rounded text-xs font-medium flex items-center gap-1.5 transition"
            >
              <ArrowLeft size={14} /> Back
            </button>
            <button
              onClick={() => setCurrentStep(3)}
              className="px-4 py-2 bg-blue-900 hover:bg-blue-800 text-white text-xs font-medium rounded flex items-center gap-2 transition"
            >
              Continue <ArrowRight size={14} />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: CHANNEL CONFIGURATION */}
      {currentStep === 3 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-6 shadow-xs">
          <div>
            <h2 className="text-base font-semibold text-gray-900">Channel Configuration</h2>
            <p className="text-xs text-gray-500 mt-0.5">Configure selected candidate collection channels.</p>
          </div>

          {/* Post Job Configuration */}
          {formData.sourcingMethods.includes('POST_JOB') && (
            <div className="bg-gray-50 p-4 rounded border border-gray-200 space-y-3">
              <h3 className="text-xs font-semibold text-gray-800 uppercase tracking-wider">Job Board Distribution</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                {[
                  { id: 'CAREER_PAGE', name: 'Company Career Page', connected: true },
                  { id: 'LINKEDIN', name: 'LinkedIn Jobs', connected: true },
                  { id: 'NAUKRI', name: 'Naukri', connected: true },
                  { id: 'INDEED', name: 'Indeed Publisher Feed', connected: false }
                ].map(plat => (
                  <div
                    key={plat.id}
                    onClick={() => togglePlatform(plat.id)}
                    className={`p-3 rounded border cursor-pointer flex items-center justify-between transition ${
                      formData.selectedPlatforms.includes(plat.id)
                        ? 'bg-white border-blue-700 text-gray-900 font-medium'
                        : 'bg-white border-gray-200 text-gray-500'
                    }`}
                  >
                    <div>
                      <p className="font-semibold">{plat.name}</p>
                      <p className="text-[11px] text-gray-400">{plat.connected ? 'Connected' : 'Not connected'}</p>
                    </div>
                    <div className={`w-4 h-4 rounded border flex items-center justify-center ${
                      formData.selectedPlatforms.includes(plat.id) ? 'bg-blue-900 border-blue-900 text-white' : 'border-gray-300'
                    }`}>
                      {formData.selectedPlatforms.includes(plat.id) && <Check size={10} />}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Application Form Configuration */}
          {formData.sourcingMethods.includes('CREATE_FORM') && (
            <div className="bg-gray-50 p-4 rounded border border-gray-200 space-y-4">
              <h3 className="text-xs font-semibold text-gray-800 uppercase tracking-wider">Application Form Fields</h3>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
                {['Full Name *', 'Email *', 'Phone *', 'Resume Upload *', 'Location *', 'Experience *', 'Notice Period', 'LinkedIn Profile', 'GitHub Portfolio'].map(field => (
                  <div key={field} className="p-2 bg-white rounded border border-gray-200 text-gray-700 font-medium">
                    ✓ {field}
                  </div>
                ))}
              </div>

              {/* Custom Questions */}
              <div className="space-y-2 pt-2">
                <p className="text-xs font-semibold text-gray-800">Custom Screening Questions</p>
                {formData.customQuestions.map((q) => (
                  <div key={q.id} className="flex items-center justify-between p-2.5 bg-white rounded border border-gray-200 text-xs text-gray-800">
                    <span>{q.question}</span>
                    <button
                      onClick={() => removeCustomQuestion(q.id)}
                      className="text-gray-400 hover:text-red-700 transition"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                ))}

                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Add custom question..."
                    value={newQuestionText}
                    onChange={e => setNewQuestionText(e.target.value)}
                    className="flex-1 bg-white border border-gray-300 rounded px-3 py-1.5 text-xs text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700"
                  />
                  <button
                    onClick={addCustomQuestion}
                    className="px-3 py-1.5 bg-white hover:bg-gray-50 text-gray-700 text-xs font-medium rounded border border-gray-300 flex items-center gap-1"
                  >
                    <Plus size={14} /> Add
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Import Existing Configuration */}
          {formData.sourcingMethods.includes('IMPORT_EXISTING') && (
            <div className="bg-gray-50 p-4 rounded border border-gray-200 space-y-3">
              <h3 className="text-xs font-semibold text-gray-800 uppercase tracking-wider">Candidate Import File</h3>
              <div className="border border-dashed border-gray-300 rounded p-6 text-center space-y-1 bg-white">
                <Upload size={20} className="mx-auto text-gray-400" />
                <p className="text-xs text-gray-700 font-medium">Upload CSV or Excel candidate file</p>
                <p className="text-[11px] text-gray-400">Supports .csv, .xlsx up to 10MB</p>
              </div>
            </div>
          )}

          <div className="flex justify-between pt-4 border-t border-gray-100">
            <button
              onClick={() => setCurrentStep(2)}
              className="px-4 py-1.5 bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 rounded text-xs font-medium flex items-center gap-1.5 transition"
            >
              <ArrowLeft size={14} /> Back
            </button>
            <button
              onClick={() => setCurrentStep(4)}
              className="px-4 py-2 bg-blue-900 hover:bg-blue-800 text-white text-xs font-medium rounded flex items-center gap-2 transition"
            >
              Review & Launch <ArrowRight size={14} />
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: REVIEW & LAUNCH */}
      {currentStep === 4 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-6 shadow-xs">
          <div>
            <h2 className="text-base font-semibold text-gray-900">Review & Launch Job</h2>
            <p className="text-xs text-gray-500 mt-0.5">Review job details before launching position.</p>
          </div>

          <div className="bg-gray-50 p-4 rounded border border-gray-200 space-y-4 text-xs">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pb-3 border-b border-gray-200">
              <div>
                <p className="text-gray-500 text-[11px]">Job Title</p>
                <p className="font-semibold text-gray-900 mt-0.5">{formData.title || 'Untitled Job'}</p>
              </div>
              <div>
                <p className="text-gray-500 text-[11px]">Department</p>
                <p className="font-semibold text-gray-900 mt-0.5">{formData.department}</p>
              </div>
              <div>
                <p className="text-gray-500 text-[11px]">Location</p>
                <p className="font-semibold text-gray-900 mt-0.5">{formData.location || 'Remote'}</p>
              </div>
              <div>
                <p className="text-gray-500 text-[11px]">Employment Type</p>
                <p className="font-semibold text-gray-900 mt-0.5">{formData.employmentType}</p>
              </div>
            </div>

            <div>
              <p className="text-gray-500 text-[11px] mb-1">Candidate Sourcing Channels</p>
              <div className="flex items-center gap-2 flex-wrap">
                {formData.sourcingMethods.map(m => (
                  <span key={m} className="px-2 py-0.5 bg-white border border-gray-300 text-gray-700 rounded font-medium">
                    ✓ {m === 'POST_JOB' ? 'Post Job' : m === 'CREATE_FORM' ? 'Application Form' : 'Import Existing'}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
            <button
              onClick={() => setCurrentStep(3)}
              className="px-4 py-1.5 bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 rounded text-xs font-medium flex items-center gap-1.5 transition"
            >
              <ArrowLeft size={14} /> Back
            </button>

            <div className="flex items-center gap-3">
              <button
                onClick={() => handleFinishWizard('DRAFT')}
                className="px-4 py-2 bg-white hover:bg-gray-50 text-gray-700 text-xs font-medium rounded border border-gray-300 transition"
              >
                Save as Draft
              </button>
              <button
                onClick={() => handleFinishWizard('PUBLISHED')}
                className="px-4 py-2 bg-blue-900 hover:bg-blue-800 text-white text-xs font-medium rounded flex items-center gap-2 transition"
              >
                <Globe size={15} /> Launch Job
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
