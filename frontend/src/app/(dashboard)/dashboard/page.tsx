'use client';

import React from 'react';
import Link from 'next/link';
import { useHRState } from '../../../stores/useHRStore';
import { EmptyState } from '../../../components/ui/EmptyState';
import {
  Briefcase,
  Users,
  CalendarCheck,
  FileCheck2,
  PhoneCall,
  Plus,
  Eye,
  ExternalLink
} from 'lucide-react';

export default function DashboardPage() {
  const hrState = useHRState();

  const openJobsCount = hrState.jobs.filter(j => j.status === 'PUBLISHED').length;
  const totalCandidatesCount = hrState.candidates.length;
  const totalAppsCount = hrState.applications.length;
  const reviewWaitingCount = hrState.applications.filter(a => a.status === 'AI_SHORTLISTED' || a.status === 'SCREENING').length;
  const callsPendingCount = hrState.applications.filter(a => a.status === 'CALL_PENDING' || a.status === 'HR_APPROVED').length;
  const interviewsScheduledCount = hrState.candidates.flatMap(c => c.interviews || []).filter(i => i.status === 'UPCOMING').length;
  const interviewsTodayCount = hrState.candidates.flatMap(c => c.interviews || []).filter(i => i.status === 'TODAY' || i.date === 'Today').length;
  const offersCount = hrState.offers.length;

  const allInterviews = hrState.candidates.flatMap(c => c.interviews || []);

  const pipelineStages = [
    { name: 'Applications', count: hrState.applications.filter(a => a.currentStage === 'Applied' || a.currentStage === 'Screening').length },
    { name: 'Screening', count: hrState.applications.filter(a => a.status === 'SCREENING').length },
    { name: 'HR Review', count: hrState.applications.filter(a => a.status === 'AI_SHORTLISTED').length },
    { name: 'Calling', count: hrState.applications.filter(a => a.currentStage === 'HR Call' || a.status === 'HR_APPROVED').length },
    { name: 'Interview', count: hrState.applications.filter(a => a.currentStage === 'Interview').length },
    { name: 'Decision', count: hrState.applications.filter(a => a.currentStage === 'Selected' || a.currentStage === 'Offer').length }
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-lg border border-gray-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">Dashboard</h1>
          <p className="text-xs text-gray-500 mt-0.5">Good morning, Recruiter · Hiring overview & pending tasks.</p>
        </div>
        <Link
          href="/jobs/create"
          className="px-4 py-2 bg-[#1D4ED8] hover:bg-[#1E40AF] text-white rounded-md text-xs font-medium flex items-center justify-center gap-1.5 transition shadow-xs"
        >
          <Plus size={15} /> Create Job
        </Link>
      </div>

      {/* Hiring Overview Metrics */}
      <div>
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Hiring Overview</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          <Link href="/jobs" className="bg-white border border-gray-200 hover:border-gray-300 p-4 rounded-lg shadow-xs transition space-y-1">
            <div className="flex items-center justify-between text-xs text-gray-500 font-medium">
              <span>Open Jobs</span>
              <Briefcase size={15} className="text-gray-400" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{openJobsCount}</p>
          </Link>

          <Link href="/candidates" className="bg-white border border-gray-200 hover:border-gray-300 p-4 rounded-lg shadow-xs transition space-y-1">
            <div className="flex items-center justify-between text-xs text-gray-500 font-medium">
              <span>Candidates</span>
              <Users size={15} className="text-gray-400" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{totalCandidatesCount}</p>
          </Link>

          <Link href="/candidates" className="bg-white border border-gray-200 hover:border-gray-300 p-4 rounded-lg shadow-xs transition space-y-1">
            <div className="flex items-center justify-between text-xs text-gray-500 font-medium">
              <span>Applications</span>
              <Users size={15} className="text-gray-400" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{totalAppsCount}</p>
          </Link>

          <Link href="/interviews" className="bg-white border border-gray-200 hover:border-gray-300 p-4 rounded-lg shadow-xs transition space-y-1">
            <div className="flex items-center justify-between text-xs text-gray-500 font-medium">
              <span>Interviews</span>
              <CalendarCheck size={15} className="text-gray-400" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{interviewsScheduledCount}</p>
          </Link>

          <Link href="/offers" className="bg-white border border-gray-200 hover:border-gray-300 p-4 rounded-lg shadow-xs transition space-y-1">
            <div className="flex items-center justify-between text-xs text-gray-500 font-medium">
              <span>Offers</span>
              <FileCheck2 size={15} className="text-gray-400" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{offersCount}</p>
          </Link>
        </div>
      </div>

      {/* Needs Attention Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-5 space-y-3 shadow-xs">
        <h2 className="text-sm font-semibold text-gray-900 border-b border-gray-100 pb-2.5">Needs Attention</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-gray-50 border border-gray-200 rounded-md flex items-center justify-between">
            <div>
              <p className="font-semibold text-gray-900">{reviewWaitingCount} candidates waiting for HR review</p>
              <p className="text-[11px] text-gray-500">Screened applicants pending review</p>
            </div>
            <Link
              href="/candidates?view=HR_REVIEW"
              className="px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-100 text-gray-700 font-medium rounded text-xs transition shrink-0"
            >
              View candidates
            </Link>
          </div>

          <div className="p-3 bg-gray-50 border border-gray-200 rounded-md flex items-center justify-between">
            <div>
              <p className="font-semibold text-gray-900">{interviewsTodayCount} interviews today</p>
              <p className="text-[11px] text-gray-500">Scheduled candidate sessions</p>
            </div>
            <Link
              href="/interviews?view=scheduling"
              className="px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-100 text-gray-700 font-medium rounded text-xs transition shrink-0"
            >
              View schedule
            </Link>
          </div>

          <div className="p-3 bg-gray-50 border border-gray-200 rounded-md flex items-center justify-between">
            <div>
              <p className="font-semibold text-gray-900">{callsPendingCount} pending calls</p>
              <p className="text-[11px] text-gray-500">Voice screening queue</p>
            </div>
            <Link
              href="/ai-calling"
              className="px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-100 text-gray-700 font-medium rounded text-xs transition shrink-0"
            >
              View calls
            </Link>
          </div>
        </div>
      </div>

      {/* Compact Hiring Funnel */}
      <div className="bg-white border border-gray-200 rounded-lg p-5 space-y-3 shadow-xs">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Candidate Funnel</h2>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {pipelineStages.map((stg, i, arr) => (
            <React.Fragment key={stg.name}>
              <div className="px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-md flex items-center gap-2">
                <span className="text-gray-600 font-medium">{stg.name}</span>
                <span className="font-bold text-gray-900 bg-white px-1.5 py-0.5 rounded border border-gray-200">{stg.count}</span>
              </div>
              {i < arr.length - 1 && <span className="text-gray-400">→</span>}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Recent Jobs Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-xs">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-900">Recent Jobs</h2>
          <Link href="/jobs" className="text-xs text-[#1D4ED8] font-medium hover:underline">
            View all jobs
          </Link>
        </div>

        {hrState.jobs.length === 0 ? (
          <div className="p-8 text-center text-xs text-gray-500 space-y-2">
            <p className="font-semibold text-gray-900">No jobs created yet</p>
            <p>Create your first job to start receiving candidates.</p>
            <Link href="/jobs/create" className="inline-block px-3.5 py-1.5 bg-[#1D4ED8] text-white rounded text-xs font-medium">
              Create Job
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-2.5 px-4">Job</th>
                  <th className="py-2.5 px-4">Department</th>
                  <th className="py-2.5 px-4">Location</th>
                  <th className="py-2.5 px-4 text-center">Applications</th>
                  <th className="py-2.5 px-4">Stage</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4 text-right">Updated</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 text-gray-700">
                {hrState.jobs.slice(0, 5).map(job => (
                  <tr key={job.id} className="hover:bg-gray-50/80 transition">
                    <td className="py-2.5 px-4">
                      <Link href={`/jobs/${job.id}`} className="font-semibold text-gray-900 hover:text-[#1D4ED8] transition">
                        {job.title}
                      </Link>
                    </td>
                    <td className="py-2.5 px-4">{job.department}</td>
                    <td className="py-2.5 px-4 text-gray-500">{job.location}</td>
                    <td className="py-2.5 px-4 text-center font-bold text-gray-900">{job.applicantsCount}</td>
                    <td className="py-2.5 px-4 text-gray-600">Active</td>
                    <td className="py-2.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        job.status === 'PUBLISHED' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {job.status === 'PUBLISHED' ? 'Open' : job.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-right text-gray-400">{job.createdAt || 'Today'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Upcoming Interviews Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-xs">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-900">Upcoming Interviews</h2>
          <Link href="/interviews" className="text-xs text-[#1D4ED8] font-medium hover:underline">
            View all interviews
          </Link>
        </div>

        {allInterviews.length === 0 ? (
          <div className="p-6 text-center text-xs text-gray-500">
            <p className="font-semibold text-gray-900">No interviews scheduled</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-2.5 px-4">Candidate</th>
                  <th className="py-2.5 px-4">Job Position</th>
                  <th className="py-2.5 px-4">Date & Time</th>
                  <th className="py-2.5 px-4">Interviewer</th>
                  <th className="py-2.5 px-4 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 text-gray-700">
                {allInterviews.slice(0, 5).map(int => (
                  <tr key={int.id} className="hover:bg-gray-50/80 transition">
                    <td className="py-2.5 px-4 font-semibold text-gray-900">{int.candidateName}</td>
                    <td className="py-2.5 px-4 text-gray-600">{int.jobTitle}</td>
                    <td className="py-2.5 px-4 text-gray-600">{int.date} at {int.time}</td>
                    <td className="py-2.5 px-4 text-gray-600">{int.interviewer}</td>
                    <td className="py-2.5 px-4 text-right">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-50 text-blue-800 border border-blue-200">
                        {int.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recent Activity Table */}
      <div className="bg-white border border-gray-200 rounded-lg p-5 space-y-3 shadow-xs">
        <div className="flex items-center justify-between border-b border-gray-100 pb-2.5">
          <h2 className="text-sm font-semibold text-gray-900">Recent Activity</h2>
          <Link href="/activity" className="text-xs text-[#1D4ED8] font-medium hover:underline">
            View activity log
          </Link>
        </div>

        {hrState.activityLogs.length === 0 ? (
          <p className="text-xs text-gray-500 py-4 text-center">No activity recorded yet.</p>
        ) : (
          <div className="divide-y divide-gray-100 text-xs">
            {hrState.activityLogs.slice(0, 5).map(log => (
              <div key={log.id} className="py-2 flex items-center justify-between">
                <div>
                  <span className="font-semibold text-gray-900">{log.action}</span>
                  <span className="text-gray-500 ml-2">{log.result}</span>
                </div>
                <span className="text-gray-400 text-[11px] font-mono">{log.timestamp}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
