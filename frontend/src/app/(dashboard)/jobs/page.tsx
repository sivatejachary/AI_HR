'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useHRState } from '../../../stores/useHRStore';
import { EmptyState } from '../../../components/ui/EmptyState';
import {
  Briefcase,
  Plus,
  Search,
  Eye
} from 'lucide-react';

export default function JobsPage() {
  const hrState = useHRState();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [departmentFilter, setDepartmentFilter] = useState<string>('ALL');

  const filteredJobs = hrState.jobs.filter(j => {
    const matchesSearch = j.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          j.department.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (j.location && j.location.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus = statusFilter === 'ALL' || j.status === statusFilter;
    const matchesDept = departmentFilter === 'ALL' || j.department === departmentFilter;
    return matchesSearch && matchesStatus && matchesDept;
  });

  const departments = Array.from(new Set(hrState.jobs.map(j => j.department))).filter(Boolean);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-lg border border-gray-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">Jobs</h1>
          <p className="text-xs text-gray-500 mt-1">Manage your open positions and hiring pipelines.</p>
        </div>
        <Link
          href="/jobs/create"
          className="px-4 py-2 bg-blue-900 hover:bg-blue-800 text-white rounded-md text-xs font-medium flex items-center justify-center gap-1.5 transition shadow-xs"
        >
          <Plus size={16} /> Create Job
        </Link>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-4 rounded-lg border border-gray-200 shadow-xs text-xs">
        <div className="relative flex-1 min-w-[240px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search jobs..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full bg-gray-50 border border-gray-300 rounded-md pl-9 pr-4 py-1.5 text-xs text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-gray-500 font-medium">Status:</span>
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="bg-gray-50 border border-gray-300 rounded-md px-3 py-1.5 text-xs text-gray-900 focus:outline-none focus:border-blue-700"
            >
              <option value="ALL">All Statuses</option>
              <option value="PUBLISHED">Open</option>
              <option value="DRAFT">Draft</option>
              <option value="PAUSED">Paused</option>
              <option value="CLOSED">Closed</option>
            </select>
          </div>

          {departments.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-gray-500 font-medium">Department:</span>
              <select
                value={departmentFilter}
                onChange={e => setDepartmentFilter(e.target.value)}
                className="bg-gray-50 border border-gray-300 rounded-md px-3 py-1.5 text-xs text-gray-900 focus:outline-none focus:border-blue-700"
              >
                <option value="ALL">All Departments</option>
                {departments.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Enterprise Data Table */}
      {filteredJobs.length === 0 ? (
        <EmptyState
          icon={Briefcase}
          title="No jobs yet"
          description="Create your first job to start receiving candidates."
          actionLabel="Create Job"
          actionHref="/jobs/create"
        />
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Job</th>
                  <th className="py-3 px-4">Department</th>
                  <th className="py-3 px-4">Location</th>
                  <th className="py-3 px-4 text-center">Applications</th>
                  <th className="py-3 px-4">Stage</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Created</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 text-gray-700">
                {filteredJobs.map((job) => {
                  const appsForJob = hrState.applications.filter(a => a.jobId === job.id);
                  const hrReviewCount = appsForJob.filter(a => a.status === 'AI_SHORTLISTED').length;
                  const currentStageText = hrReviewCount > 0 ? `${hrReviewCount} HR Review` : 'Active';

                  return (
                    <tr key={job.id} className="hover:bg-gray-50/80 transition">
                      <td className="py-3 px-4">
                        <Link href={`/jobs/${job.id}`} className="font-semibold text-gray-900 hover:text-blue-900 transition text-sm">
                          {job.title}
                        </Link>
                        <p className="text-[11px] text-gray-500">{job.employmentType} · {job.openings} Openings</p>
                      </td>

                      <td className="py-3 px-4 font-medium text-gray-800">
                        {job.department}
                      </td>

                      <td className="py-3 px-4 text-gray-600">
                        {job.location}
                      </td>

                      <td className="py-3 px-4 text-center font-bold text-gray-900">
                        {job.applicantsCount}
                      </td>

                      <td className="py-3 px-4 text-gray-600">
                        <span className="px-2 py-0.5 rounded bg-gray-100 border border-gray-200 text-gray-700 text-[11px]">
                          {currentStageText}
                        </span>
                      </td>

                      <td className="py-3 px-4">
                        <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${
                          job.status === 'PUBLISHED'
                            ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                            : job.status === 'PAUSED'
                            ? 'bg-amber-50 text-amber-800 border-amber-200'
                            : 'bg-gray-100 text-gray-600 border-gray-300'
                        }`}>
                          {job.status === 'PUBLISHED' ? 'Open' : job.status}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-gray-500">
                        {job.createdAt || 'Just now'}
                      </td>

                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            href={`/jobs/${job.id}`}
                            className="px-2.5 py-1 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded text-xs font-medium transition flex items-center gap-1"
                          >
                            <Eye size={13} /> View
                          </Link>
                          {job.status === 'PUBLISHED' ? (
                            <button
                              onClick={() => hrState.updateJobStatus(job.id, 'PAUSED')}
                              className="px-2.5 py-1 bg-amber-50 text-amber-800 border border-amber-200 hover:bg-amber-100 rounded text-xs transition"
                            >
                              Pause
                            </button>
                          ) : (
                            <button
                              onClick={() => hrState.updateJobStatus(job.id, 'PUBLISHED')}
                              className="px-2.5 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 hover:bg-emerald-100 rounded text-xs transition"
                            >
                              Publish
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
