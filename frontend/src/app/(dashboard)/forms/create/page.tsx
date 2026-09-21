'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useHRState } from '../../../../stores/useHRStore';
import { ApplicationForm, FormField } from '../../../../types';
import { FileSpreadsheet, Plus, Trash2, Save, ArrowLeft, CheckCircle2 } from 'lucide-react';

export default function CreateFormPage() {
  const router = useRouter();
  const hrState = useHRState();

  const [selectedJobId, setSelectedJobId] = useState(hrState.jobs[0]?.id || 'job-101');
  const [title, setTitle] = useState('Senior Python Engineer Direct Application');
  const [publicUrlSlug, setPublicUrlSlug] = useState('senior-python-engineer-apply');

  const [fields, setFields] = useState<FormField[]>([
    { id: 'f1', label: 'Full Name', type: 'text', isRequired: true },
    { id: 'f2', label: 'Email Address', type: 'email', isRequired: true },
    { id: 'f3', label: 'Phone Number', type: 'phone', isRequired: true },
    { id: 'f4', label: 'Resume PDF', type: 'file', isRequired: true },
    { id: 'f5', label: 'Years of Experience', type: 'number', isRequired: true },
    { id: 'f6', label: 'Expected Salary ($)', type: 'text', isRequired: false }
  ]);

  const [customQuestions, setCustomQuestions] = useState<Array<{ id: string; question: string; isRequired: boolean }>>([
    { id: 'q1', question: 'Describe your experience building async Python FastAPI microservices.', isRequired: true }
  ]);

  const handleAddField = () => {
    const newF: FormField = {
      id: `f-${Date.now()}`,
      label: 'New Custom Field',
      type: 'text',
      isRequired: false
    };
    setFields([...fields, newF]);
  };

  const handleDeleteField = (id: string) => {
    setFields(fields.filter(f => f.id !== id));
  };

  const handleAddQuestion = () => {
    setCustomQuestions([...customQuestions, { id: `q-${Date.now()}`, question: 'What is your notice period?', isRequired: false }]);
  };

  const handleSaveForm = (e: React.FormEvent) => {
    e.preventDefault();
    const targetJob = hrState.jobs.find(j => j.id === selectedJobId);
    const newForm: ApplicationForm = {
      id: `form-${Date.now()}`,
      jobId: selectedJobId,
      jobTitle: targetJob?.title || 'Senior Python Engineer',
      title,
      publicUrlSlug,
      isPublished: true,
      fields,
      customQuestions,
      createdDate: new Date().toISOString().split('T')[0],
      submissionsCount: 0
    };

    hrState.addForm(newForm);
    router.push('/forms');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <FileSpreadsheet className="text-indigo-400" /> Form Builder
          </h1>
          <p className="text-xs text-slate-400 mt-1">Design candidate application form fields & custom screening questions.</p>
        </div>
        <button onClick={() => router.push('/forms')} className="p-2 text-slate-400 hover:text-white">
          <ArrowLeft size={20} />
        </button>
      </div>

      <form onSubmit={handleSaveForm} className="space-y-6 text-xs">
        {/* Basic Form Config */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-indigo-400">Form Configuration</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-slate-400 font-semibold block mb-1">Target Job Opening *</label>
              <select
                value={selectedJobId}
                onChange={e => setSelectedJobId(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white font-bold"
              >
                {hrState.jobs.map(j => (
                  <option key={j.id} value={j.id}>{j.title}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-slate-400 font-semibold block mb-1">Form Title *</label>
              <input
                type="text"
                value={title}
                onChange={e => setTitle(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white"
              />
            </div>

            <div className="md:col-span-2">
              <label className="text-slate-400 font-semibold block mb-1">Public URL Slug *</label>
              <div className="flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-400">
                <span className="font-mono text-indigo-300">/apply/</span>
                <input
                  type="text"
                  value={publicUrlSlug}
                  onChange={e => setPublicUrlSlug(e.target.value.toLowerCase().replace(/\s+/g, '-'))}
                  className="bg-transparent text-white font-mono flex-1 focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Fields Builder */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider text-indigo-400">Form Fields Configuration</h2>
            <button
              type="button"
              onClick={handleAddField}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center gap-1"
            >
              <Plus size={14} /> Add Field
            </button>
          </div>

          <div className="space-y-3">
            {fields.map((f, idx) => (
              <div key={f.id} className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between gap-4">
                <div className="flex-1 grid grid-cols-3 gap-3">
                  <input
                    type="text"
                    value={f.label}
                    onChange={e => {
                      const val = e.target.value;
                      setFields(fields.map(item => item.id === f.id ? { ...item, label: val } : item));
                    }}
                    className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white"
                  />
                  <select
                    value={f.type}
                    onChange={e => {
                      const val = e.target.value as any;
                      setFields(fields.map(item => item.id === f.id ? { ...item, type: val } : item));
                    }}
                    className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white"
                  >
                    <option value="text">Text Input</option>
                    <option value="email">Email</option>
                    <option value="phone">Phone</option>
                    <option value="file">File Upload (PDF)</option>
                    <option value="number">Number</option>
                    <option value="textarea">Text Area</option>
                  </select>
                  <label className="flex items-center gap-2 text-slate-300">
                    <input
                      type="checkbox"
                      checked={f.isRequired}
                      onChange={e => {
                        const checked = e.target.checked;
                        setFields(fields.map(item => item.id === f.id ? { ...item, isRequired: checked } : item));
                      }}
                      className="rounded bg-slate-800 border-slate-700 text-indigo-600"
                    />
                    Required Field
                  </label>
                </div>
                <button type="button" onClick={() => handleDeleteField(f.id)} className="p-1 text-rose-400 hover:bg-rose-950/40 rounded">
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Custom Questions */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider text-indigo-400">Custom Screening Questions</h2>
            <button
              type="button"
              onClick={handleAddQuestion}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center gap-1"
            >
              <Plus size={14} /> Add Question
            </button>
          </div>

          <div className="space-y-3">
            {customQuestions.map(q => (
              <div key={q.id} className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between gap-4">
                <input
                  type="text"
                  value={q.question}
                  onChange={e => {
                    const val = e.target.value;
                    setCustomQuestions(customQuestions.map(item => item.id === q.id ? { ...item, question: val } : item));
                  }}
                  className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white"
                />
                <button
                  type="button"
                  onClick={() => setCustomQuestions(customQuestions.filter(item => item.id !== q.id))}
                  className="p-1 text-rose-400 hover:bg-rose-950/40 rounded"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Save Form */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition"
          >
            <Save size={16} /> Save & Publish Application Form
          </button>
        </div>
      </form>
    </div>
  );
}
