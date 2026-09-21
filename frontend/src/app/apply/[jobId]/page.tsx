'use client';

import React, { useState } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import { useHRState } from '../../../stores/useHRStore';
import {
  CheckCircle2,
  Building2,
  MapPin,
  DollarSign,
  Send,
  ShieldCheck
} from 'lucide-react';

export default function PublicCandidateApplyPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const hrState = useHRState();

  const jobIdOrSlug = params.jobId as string;
  const sourceParam = searchParams.get('source') || 'CAREER_PAGE';

  const job = hrState.jobs.find(j => j.id === jobIdOrSlug) || hrState.jobs[0] || {
    id: jobIdOrSlug,
    title: 'Open Position',
    department: 'General',
    location: 'Remote',
    salaryRange: 'Competitive'
  };

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    location: '',
    yearsExperience: 0,
    skills: '',
    resumeText: ''
  });

  const [submittedSuccess, setSubmittedSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await hrState.ingestCandidateApplication({
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        location: formData.location,
        jobId: job.id,
        jobTitle: job.title,
        source: sourceParam as any,
        resumeText: formData.resumeText,
        skills: formData.skills ? formData.skills.split(',').map(s => s.trim()) : [],
        yearsExperience: Number(formData.yearsExperience) || 0
      });
      setSubmittedSuccess(true);
    } catch (err) {
      console.error("Application submission failed:", err);
      alert("Submission failed. Please check network connection and try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F7F8FA] text-gray-900 p-4 md:p-8 flex flex-col items-center justify-center">
      <div className="w-full max-w-2xl space-y-6">
        {/* Header */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-xs flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded bg-blue-900 flex items-center justify-center text-white font-bold shrink-0">
              <Building2 size={18} />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900 tracking-tight">Careers Portal</h1>
              <p className="text-xs text-gray-500">Position: {job.title}</p>
            </div>
          </div>
          <span className="text-[10px] font-bold text-emerald-800 px-2.5 py-1 bg-emerald-50 border border-emerald-200 rounded uppercase">
            Accepting Applications
          </span>
        </div>

        {submittedSuccess ? (
          <div className="bg-white border border-gray-200 rounded-lg p-8 text-center space-y-4 shadow-xs">
            <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center justify-center mx-auto">
              <CheckCircle2 size={24} />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Application Received!</h2>
            <p className="text-xs text-gray-600 max-w-md mx-auto leading-relaxed">
              Thank you for applying for <strong className="text-gray-900">{job.title}</strong>. Our hiring team will review your application and update you.
            </p>
          </div>
        ) : (
          <div className="bg-white border border-gray-200 rounded-lg p-6 md:p-8 space-y-6 shadow-xs">
            {/* Job Details Card */}
            <div className="p-4 bg-gray-50 rounded border border-gray-200 space-y-2 text-xs">
              <h2 className="text-base font-semibold text-gray-900">{job.title}</h2>
              <div className="flex flex-wrap gap-4 text-gray-600">
                <span className="flex items-center gap-1.5"><Building2 size={14} className="text-gray-400" /> {job.department}</span>
                <span className="flex items-center gap-1.5"><MapPin size={14} className="text-gray-400" /> {job.location}</span>
                {job.salaryRange && <span className="flex items-center gap-1.5"><DollarSign size={14} className="text-gray-400" /> {job.salaryRange}</span>}
              </div>
            </div>

            {/* Candidate Form */}
            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Candidate Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-gray-700 font-medium block mb-1">Full Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="John Smith"
                    value={formData.name}
                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
                  />
                </div>

                <div>
                  <label className="text-gray-700 font-medium block mb-1">Email Address *</label>
                  <input
                    type="email"
                    required
                    placeholder="john.smith@example.com"
                    value={formData.email}
                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
                  />
                </div>

                <div>
                  <label className="text-gray-700 font-medium block mb-1">Phone Number *</label>
                  <input
                    type="tel"
                    required
                    placeholder="+1 (555) 000-0000"
                    value={formData.phone}
                    onChange={e => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
                  />
                </div>

                <div>
                  <label className="text-gray-700 font-medium block mb-1">Current Location *</label>
                  <input
                    type="text"
                    required
                    placeholder="City, Country"
                    value={formData.location}
                    onChange={e => setFormData({ ...formData, location: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
                  />
                </div>

                <div>
                  <label className="text-gray-700 font-medium block mb-1">Years of Experience *</label>
                  <input
                    type="number"
                    required
                    min="0"
                    placeholder="e.g. 4"
                    value={formData.yearsExperience || ''}
                    onChange={e => setFormData({ ...formData, yearsExperience: parseInt(e.target.value) || 0 })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
                  />
                </div>

                <div>
                  <label className="text-gray-700 font-medium block mb-1">Primary Technical Skills *</label>
                  <input
                    type="text"
                    required
                    placeholder="Python, PostgreSQL, React, AWS"
                    value={formData.skills}
                    onChange={e => setFormData({ ...formData, skills: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-3 py-1.5 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
                  />
                </div>
              </div>

              <div>
                <label className="text-gray-700 font-medium block mb-1">Resume Summary / Highlights *</label>
                <textarea
                  required
                  rows={4}
                  placeholder="Paste your resume summary, recent experience highlights, or key projects..."
                  value={formData.resumeText}
                  onChange={e => setFormData({ ...formData, resumeText: e.target.value })}
                  className="w-full bg-gray-50 border border-gray-300 rounded p-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white leading-relaxed"
                />
              </div>

              <div className="pt-4 flex items-center justify-between border-t border-gray-100">
                <span className="text-[11px] text-gray-400 flex items-center gap-1">
                  <ShieldCheck size={14} className="text-emerald-600" /> Secure application submission
                </span>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2.5 bg-blue-900 hover:bg-blue-800 text-white font-semibold rounded flex items-center gap-2 transition"
                >
                  <Send size={14} /> {isSubmitting ? 'Submitting...' : 'Submit Application'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
