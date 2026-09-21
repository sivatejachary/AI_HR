'use client';

import React, { useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useHRState } from '../../../stores/useHRStore';
import { EmptyState } from '../../../components/ui/EmptyState';
import { Users, Search, Filter } from 'lucide-react';

function CandidatesContent() {
  const searchParams = useSearchParams();
  const viewFilter = searchParams.get('view') || 'ALL';
  const hrState = useHRState();

  const [searchTerm, setSearchTerm] = useState('');
  const [jobFilter, setJobFilter] = useState('ALL');

  const filteredApps = hrState.applications.filter(app => {
    const term = searchTerm.toLowerCase();
    const matchesSearch =
      app.candidateName.toLowerCase().includes(term) ||
      app.candidateEmail.toLowerCase().includes(term) ||
      app.candidatePhone.toLowerCase().includes(term) ||
      app.id.toLowerCase().includes(term);

    const matchesJob = jobFilter === 'ALL' || app.jobId === jobFilter;

    let matchesView = true;
    if (viewFilter === 'AI_SHORTLISTED') matchesView = app.status === 'AI_SHORTLISTED';
    else if (viewFilter === 'HR_REVIEW') matchesView = app.status === 'HR_REVIEW' || app.status === 'SCREENING' || app.status === 'AI_SHORTLISTED';
    else if (viewFilter === 'Calling') matchesView = app.currentStage === 'HR Call' || app.status === 'HR_APPROVED';
    else if (viewFilter === 'Interview') matchesView = app.currentStage === 'Interview';
    else if (viewFilter === 'Selected') matchesView = app.status === 'SELECTED';
    else if (viewFilter === 'Rejected') matchesView = app.status === 'HR_REJECTED' || app.status === 'REJECTED';

    return matchesSearch && matchesJob && matchesView;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-lg border border-gray-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">Candidates</h1>
          <p className="text-xs text-gray-500 mt-1">
            View Filter: <strong className="text-gray-900">{viewFilter.replace('_', ' ')}</strong> · Ingested candidate applications across all sources.
          </p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-4 rounded-lg border border-gray-200 shadow-xs text-xs">
        <div className="relative flex-1 min-w-[240px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search candidates by name, email, phone..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full bg-gray-50 border border-gray-300 rounded-md pl-9 pr-4 py-1.5 text-xs text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-gray-500 font-medium">Job Position:</span>
          <select
            value={jobFilter}
            onChange={e => setJobFilter(e.target.value)}
            className="bg-gray-50 border border-gray-300 rounded-md px-3 py-1.5 text-xs text-gray-900 focus:outline-none focus:border-blue-700"
          >
            <option value="ALL">All Jobs</option>
            {hrState.jobs.map(j => (
              <option key={j.id} value={j.id}>{j.title}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Candidate Data Table */}
      {filteredApps.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No candidates yet"
          description="Candidates will appear here when applications are received through your job posts or application links."
          actionLabel="Create Job"
          actionHref="/jobs/create"
        />
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Candidate</th>
                  <th className="py-3 px-4">Job</th>
                  <th className="py-3 px-4">Source</th>
                  <th className="py-3 px-4">Screening</th>
                  <th className="py-3 px-4">Stage</th>
                  <th className="py-3 px-4">Applied</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 text-gray-700">
                {filteredApps.map((app) => (
                  <tr key={app.id} className="hover:bg-gray-50/80 transition">
                    <td className="py-3 px-4">
                      <span className="font-semibold text-gray-900 text-sm block">{app.candidateName}</span>
                      <span className="text-[11px] text-gray-500">{app.candidateEmail}</span>
                    </td>

                    <td className="py-3 px-4 font-medium text-gray-800">
                      {app.jobTitle}
                    </td>

                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-gray-100 border border-gray-200 text-gray-700 font-medium">
                        {app.source}
                      </span>
                    </td>

                    <td className="py-3 px-4 font-semibold text-emerald-700">
                      {app.screeningResult?.matchScore ? `${app.screeningResult.matchScore}% Match` : 'Matched'}
                    </td>

                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-blue-50 border border-blue-200 text-blue-800 font-medium">
                        {app.currentStage || app.status}
                      </span>
                    </td>

                    <td className="py-3 px-4 text-gray-500">
                      {app.appliedAt || 'Today'}
                    </td>

                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {app.status === 'AI_SHORTLISTED' || app.status === 'SCREENING' ? (
                          <>
                            <button
                              onClick={() => hrState.hrApproveApplication(app.id)}
                              className="px-2.5 py-1 bg-emerald-700 hover:bg-emerald-800 text-white rounded text-xs font-medium transition"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => hrState.hrRejectApplication(app.id)}
                              className="px-2.5 py-1 bg-white border border-gray-300 hover:bg-gray-100 text-red-700 rounded text-xs font-medium transition"
                            >
                              Reject
                            </button>
                          </>
                        ) : (
                          <span className="text-[11px] text-gray-400 font-medium">{app.status}</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default function CandidatesPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs text-gray-500">Loading candidate directory...</div>}>
      <CandidatesContent />
    </Suspense>
  );
}
