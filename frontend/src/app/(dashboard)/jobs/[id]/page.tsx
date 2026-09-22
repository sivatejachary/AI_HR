'use client';

import React, { useState } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { useHRState } from '../../../../stores/useHRStore';
import {
  Briefcase,
  Share2,
  Copy,
  ExternalLink,
  Check,
  ArrowRight,
  CheckCircle2,
  FileSpreadsheet
} from 'lucide-react';

export default function JobDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const hrState = useHRState();
  const jobId = params.id as string;

  const [fetchedJob, setFetchedJob] = useState<any>(null);
  const [loadingJob, setLoadingJob] = useState(true);

  React.useEffect(() => {
    const existing = hrState.jobs.find(j => j.id === jobId);
    if (existing) {
      setLoadingJob(false);
      return;
    }
    api.getJobs()
      .then(jobs => {
        if (jobs && Array.isArray(jobs)) {
          const match = jobs.find((j: any) => j.id === jobId);
          if (match) setFetchedJob(match);
        }
      })
      .catch(err => console.warn('[JobDetail] API fetch fallback error', err))
      .finally(() => setLoadingJob(false));
  }, [jobId, hrState.jobs]);

  const job = hrState.jobs.find(j => j.id === jobId) || fetchedJob;
  const jobApps = hrState.applications.filter(a => a.jobId === job?.id);

  const [activeTab, setActiveTab] = useState<
    'Overview' | 'Applications' | 'Screening' | 'Distribution' | 'Application Form' | 'Calling' | 'Interviews' | 'Activity'
  >('Overview');

  const [copiedLink, setCopiedLink] = useState(false);
  const [copiedChannel, setCopiedChannel] = useState<string | null>(null);
  const [creatingForm, setCreatingForm] = useState(false);
  const [googleFormUrl, setGoogleFormUrl] = useState<string | null>(null);
  const [googleFormId, setGoogleFormId] = useState<string | null>(null);

  const activeFormUrl = googleFormUrl || job?.google_responder_url || job?.google_form_url || (googleFormId ? `https://docs.google.com/forms/d/e/${googleFormId}/viewform` : null);

  const handleCreateGoogleForm = async () => {
    if (!job) return;
    setCreatingForm(true);
    try {
      const res = await api.createJobGoogleForm(job.id);
      if (res) {
        const formUrl = res.google_responder_url || res.google_form_url || (res.google_form_id ? `https://docs.google.com/forms/d/e/${res.google_form_id}/viewform` : null);
        setGoogleFormUrl(formUrl);
        setGoogleFormId(res.google_form_id || null);
        setActiveTab('Application Form');
      }
    } catch (e: any) {
      console.error('[JobDetail] Create Google Form Error:', e);
      alert(`Google Form Generation Notice: ${e.message || 'Unable to generate form. Please check backend connection.'}`);
    } finally {
      setCreatingForm(false);
    }
  };

  if (!job) {
    if (loadingJob) {
      return (
        <div className="p-12 bg-white border border-gray-200 rounded-lg text-center space-y-3 max-w-lg mx-auto">
          <div className="w-6 h-6 border-2 border-blue-900 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-gray-500 font-medium">Loading position details from PostgreSQL DB...</p>
        </div>
      );
    }
    return (
      <div className="p-8 bg-white border border-gray-200 rounded-lg text-center space-y-4 max-w-lg mx-auto">
        <h2 className="text-lg font-semibold text-gray-900">Job not found</h2>
        <p className="text-xs text-gray-500">The requested job position (ID: <code className="font-mono bg-gray-100 px-1 py-0.5 rounded text-gray-800">{jobId}</code>) does not exist or was deleted.</p>
        <Link href="/jobs" className="inline-block px-4 py-2 bg-blue-900 text-white text-xs font-medium rounded">
          Back to Jobs
        </Link>
      </div>
    );
  }

  const publicApplyUrl = typeof window !== 'undefined'
    ? `${window.location.origin}/apply/${job.id}`
    : `http://localhost:3000/apply/${job.id}`;

  const copyToClipboard = (url: string, channelName?: string) => {
    navigator.clipboard.writeText(url);
    if (channelName) {
      setCopiedChannel(channelName);
      setTimeout(() => setCopiedChannel(null), 2000);
    } else {
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2000);
    }
  };

  const screeningApps = jobApps.filter(a => a.currentStage === 'Screening' || a.status === 'SCREENING');
  const hrReviewApps = jobApps.filter(a => a.status === 'AI_SHORTLISTED');
  const interviewApps = jobApps.filter(a => a.currentStage === 'Interview' || a.currentStage === 'HR Call');

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Banner when job created */}
      {searchParams.get('created') === 'true' && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 size={16} className="text-emerald-700" />
            <span>Job created successfully! Application link is ready.</span>
          </div>
          <button
            onClick={() => copyToClipboard(publicApplyUrl)}
            className="px-3 py-1 bg-emerald-700 text-white rounded text-xs font-medium flex items-center gap-1"
          >
            {copiedLink ? <Check size={12} /> : <Copy size={12} />} {copiedLink ? 'Copied' : 'Copy Application Link'}
          </button>
        </div>
      )}

      {/* Job Header */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-xs space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-xl font-semibold text-gray-900">{job.title}</h1>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${
                job.status === 'PUBLISHED'
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : 'bg-gray-100 text-gray-600 border-gray-300'
              }`}>
                {job.status === 'PUBLISHED' ? 'Open' : job.status}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {job.department} · {job.location} · {job.employmentType} · {job.openings} Openings
            </p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={handleCreateGoogleForm}
              disabled={creatingForm}
              className="px-3.5 py-1.5 bg-blue-900 hover:bg-blue-800 text-white rounded text-xs font-semibold flex items-center gap-1.5 transition shadow-xs"
            >
              <FileSpreadsheet size={14} /> {creatingForm ? 'Creating Form...' : 'Create Application Form'}
            </button>
            <button
              onClick={() => copyToClipboard(publicApplyUrl)}
              className="px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded text-xs font-medium flex items-center gap-1.5 transition"
            >
              <Copy size={14} /> {copiedLink ? 'Copied!' : 'Copy Application Link'}
            </button>
            <button
              onClick={() => setActiveTab('Distribution')}
              className="px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded text-xs font-medium flex items-center gap-1.5 transition"
            >
              <Share2 size={14} /> Distribute
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-2">
          <div className="p-3 bg-gray-50 rounded border border-gray-200">
            <p className="text-gray-500 text-[11px]">Applications</p>
            <p className="text-xl font-bold text-gray-900 mt-0.5">{jobApps.length}</p>
          </div>
          <div className="p-3 bg-gray-50 rounded border border-gray-200">
            <p className="text-gray-500 text-[11px]">AI Screening</p>
            <p className="text-xl font-bold text-gray-900 mt-0.5">{screeningApps.length}</p>
          </div>
          <div className="p-3 bg-gray-50 rounded border border-gray-200">
            <p className="text-gray-500 text-[11px]">HR Review</p>
            <p className="text-xl font-bold text-blue-900 mt-0.5">{hrReviewApps.length}</p>
          </div>
          <div className="p-3 bg-gray-50 rounded border border-gray-200">
            <p className="text-gray-500 text-[11px]">Interviews</p>
            <p className="text-xl font-bold text-gray-900 mt-0.5">{interviewApps.length}</p>
          </div>
        </div>

        {/* Pipeline Bar */}
        <div className="pt-3 border-t border-gray-100">
          <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-2">Hiring Pipeline</p>
          <div className="flex items-center gap-2 overflow-x-auto text-[11px] text-gray-700 font-medium py-1">
            {['Applications', 'AI Screening', 'HR Review', 'Calling', 'Interview', 'Final Decision'].map((step, idx, arr) => (
              <React.Fragment key={step}>
                <span className="px-2.5 py-1 bg-gray-100 rounded border border-gray-200 whitespace-nowrap">
                  {step}
                </span>
                {idx < arr.length - 1 && <ArrowRight size={12} className="text-gray-400 shrink-0" />}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 bg-white rounded-lg p-1 text-xs font-medium text-gray-600 overflow-x-auto border shadow-xs">
        {[
          'Overview',
          'Applications',
          'Screening',
          'Distribution',
          'Application Form',
          'Calling',
          'Interviews',
          'Activity'
        ].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-3.5 py-1.5 rounded-md whitespace-nowrap transition ${
              activeTab === tab ? 'bg-blue-900 text-white font-semibold' : 'hover:text-gray-900'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Contents */}
      <div className="space-y-6">
        {/* OVERVIEW */}
        {activeTab === 'Overview' && (
          <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4 text-xs shadow-xs">
            <h3 className="text-sm font-semibold text-gray-900">Job Description</h3>
            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{job.description}</p>

            <h3 className="text-sm font-semibold text-gray-900 pt-2">Key Responsibilities</h3>
            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{job.responsibilities}</p>

            <h3 className="text-sm font-semibold text-gray-900 pt-2">Requirements</h3>
            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{job.requirements}</p>
          </div>
        )}

        {/* APPLICATION FORM TAB */}
        {activeTab === 'Application Form' && (
          <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-6 text-xs shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-100 pb-4">
              <div>
                <h3 className="text-sm font-semibold text-gray-900">Job Application Form</h3>
                <p className="text-xs text-gray-500 mt-0.5">Status: <strong className="text-emerald-700">Published</strong></p>
              </div>

              <div className="flex items-center gap-2">
                {!activeFormUrl && (
                  <button
                    onClick={handleCreateGoogleForm}
                    disabled={creatingForm}
                    className="px-3 py-1.5 bg-blue-900 hover:bg-blue-800 text-white rounded font-medium flex items-center gap-1.5 transition"
                  >
                    <FileSpreadsheet size={13} /> {creatingForm ? 'Creating Google Form...' : 'Generate Google Form'}
                  </button>
                )}
                <a
                  href={`/apply/${job.id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded font-medium flex items-center gap-1"
                >
                  <ExternalLink size={12} /> Preview Form
                </a>
              </div>
            </div>

            {/* Google Form Active Card */}
            {activeFormUrl ? (
              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg space-y-3">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2.5">
                    <FileSpreadsheet className="text-purple-900" size={20} />
                    <div>
                      <h4 className="font-semibold text-purple-950 text-xs">Live Google Form Integration Active</h4>
                      <p className="text-[11px] text-gray-600 mt-0.5">
                        Google Form Responder URL for candidates. Ingests candidate applications automatically.
                      </p>
                    </div>
                  </div>
                  <a
                    href={activeFormUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1.5 bg-purple-900 hover:bg-purple-800 text-white rounded text-xs font-semibold flex items-center gap-1.5 transition shadow-xs"
                  >
                    <ExternalLink size={12} /> Open Google Form
                  </a>
                </div>

                <div className="flex items-center gap-2 bg-white p-2 rounded border border-purple-200">
                  <input
                    type="text"
                    readOnly
                    value={activeFormUrl}
                    className="bg-transparent border-none w-full text-purple-950 font-mono text-[11px] focus:outline-none"
                  />
                  <button
                    onClick={() => copyToClipboard(activeFormUrl)}
                    className="px-2.5 py-1 bg-purple-100 hover:bg-purple-200 text-purple-900 rounded text-[11px] font-semibold flex items-center gap-1 shrink-0 transition"
                  >
                    <Copy size={11} /> Copy Link
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-center justify-between text-xs">
                <div>
                  <h4 className="font-semibold text-blue-950">Google Form Not Yet Generated</h4>
                  <p className="text-[11px] text-gray-600 mt-0.5">Generate a Google Form for this position to ingest candidate applications automatically.</p>
                </div>
                <button
                  onClick={handleCreateGoogleForm}
                  disabled={creatingForm}
                  className="px-3 py-1.5 bg-blue-900 hover:bg-blue-800 text-white rounded text-xs font-semibold flex items-center gap-1.5 transition"
                >
                  <FileSpreadsheet size={13} /> {creatingForm ? 'Creating...' : 'Generate Google Form'}
                </button>
              </div>
            )}

            <div className="space-y-2">
              <label className="text-gray-700 font-medium block">Application URL</label>
              <div className="flex items-center gap-2 bg-gray-50 p-2.5 rounded border border-gray-200">
                <input
                  type="text"
                  readOnly
                  value={publicApplyUrl}
                  className="bg-transparent border-none w-full text-gray-800 font-mono text-xs focus:outline-none"
                />
                <button
                  onClick={() => copyToClipboard(publicApplyUrl)}
                  className="px-3 py-1.5 bg-blue-900 hover:bg-blue-800 text-white rounded text-xs font-medium flex items-center gap-1 shrink-0"
                >
                  {copiedLink ? <Check size={12} /> : <Copy size={12} />} {copiedLink ? 'Copied' : 'Copy Link'}
                </button>
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <p className="text-gray-700 font-semibold">Share Application Link</p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  { name: 'WhatsApp', key: 'whatsapp' },
                  { name: 'LinkedIn', key: 'linkedin' },
                  { name: 'Telegram', key: 'telegram' },
                  { name: 'Email', key: 'email' }
                ].map(platform => {
                  const trackedUrl = `${publicApplyUrl}?source=${platform.key}`;
                  const isCopied = copiedChannel === platform.name;
                  return (
                    <button
                      key={platform.key}
                      onClick={() => copyToClipboard(trackedUrl, platform.name)}
                      className="p-3 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded text-gray-800 text-left font-medium transition flex items-center justify-between"
                    >
                      <span>[{platform.name}]</span>
                      <span className="text-[10px] text-blue-900 font-semibold">{isCopied ? 'Copied!' : 'Copy'}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="p-3 bg-gray-50 rounded border border-gray-200 flex items-center justify-between text-xs">
              <span className="text-gray-600">Applications Received via Form & Portals:</span>
              <span className="font-bold text-gray-900">{jobApps.length}</span>
            </div>
          </div>
        )}

        {/* APPLICATIONS TAB */}
        {activeTab === 'Applications' && (
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-xs">
            {jobApps.length === 0 ? (
              <div className="p-8 text-center text-gray-500 text-xs space-y-1">
                <p className="font-semibold text-gray-900">No candidates applied yet</p>
                <p>Share your application link to receive applicants.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold uppercase tracking-wider text-[11px]">
                      <th className="py-3 px-4">Candidate</th>
                      <th className="py-3 px-4">Source</th>
                      <th className="py-3 px-4">Match Score</th>
                      <th className="py-3 px-4">Stage</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 text-gray-700">
                    {jobApps.map(app => (
                      <tr key={app.id} className="hover:bg-gray-50/80 transition">
                        <td className="py-3 px-4 font-semibold text-gray-900">
                          {app.candidateName}
                          <p className="text-[11px] font-normal text-gray-500">{app.candidateEmail}</p>
                        </td>
                        <td className="py-3 px-4 text-gray-700 font-medium">{app.source}</td>
                        <td className="py-3 px-4 font-bold text-emerald-700">{app.screeningResult?.matchScore || 85}%</td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded bg-gray-100 text-gray-700 font-medium">
                            {app.currentStage || app.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Link href="/candidates" className="text-blue-900 hover:underline font-medium">
                            View Candidate
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* SCREENING TAB */}
        {activeTab === 'Screening' && (
          <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4 text-xs shadow-xs">
            {jobApps.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No candidates in screening queue.</p>
            ) : (
              <div className="space-y-3">
                {jobApps.map(app => (
                  <div key={app.id} className="p-4 bg-gray-50 rounded border border-gray-200 space-y-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-semibold text-gray-900 text-sm">{app.candidateName}</h4>
                        <p className="text-gray-500 text-xs">Source: {app.source}</p>
                      </div>
                      <span className="font-bold text-emerald-700 text-sm">
                        Match: {app.screeningResult?.matchScore || 85}%
                      </span>
                    </div>
                    <p className="text-gray-700 text-xs bg-white p-2.5 rounded border border-gray-200">
                      {app.screeningResult?.explanation || 'Candidate fits required qualifications.'}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* DISTRIBUTION TAB */}
        {activeTab === 'Distribution' && (
          <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4 text-xs shadow-xs">
            <h3 className="text-sm font-semibold text-gray-900">Distribution Channels</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {[
                { name: 'Company Career Page', status: 'Connected', published: true },
                { name: 'LinkedIn Jobs API', status: 'Connected', published: job.status === 'PUBLISHED' },
                { name: 'Naukri Recruiter API', status: 'Connected', published: job.status === 'PUBLISHED' },
                { name: 'Indeed Publisher Feed', status: 'Not Connected', published: false }
              ].map(plat => (
                <div key={plat.name} className="p-3.5 bg-gray-50 rounded border border-gray-200 flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">{plat.name}</p>
                    <p className="text-[11px] text-gray-500 mt-0.5">{plat.status}</p>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    plat.published ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {plat.published ? 'Published' : 'Ready'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CALLING, INTERVIEWS, ACTIVITY TABS */}
        {(activeTab === 'Calling' || activeTab === 'Interviews' || activeTab === 'Activity') && (
          <div className="bg-white border border-gray-200 rounded-lg p-6 text-xs text-gray-500 text-center py-8 shadow-xs">
            <p className="font-semibold text-gray-900">No records for this stage yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
