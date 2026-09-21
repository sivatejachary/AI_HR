'use client';

import React from 'react';
import { useHRState } from '../../../stores/useHRStore';
import { PhoneCall, ArrowRight, UserCheck } from 'lucide-react';

export default function AICallingPage() {
  const hrState = useHRState();

  const approvedApps = hrState.applications.filter(a => a.status === 'HR_APPROVED' || a.currentStage === 'HR Call');

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-lg border border-gray-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight flex items-center gap-2">
            <PhoneCall size={22} className="text-blue-900" /> Voice Screening Calling Center
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            Outbound candidate phone screening calls connected to ElevenLabs voice agent.
          </p>
        </div>
      </div>

      {/* Execution Architecture */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 space-y-3 shadow-xs">
        <h2 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">
          Voice Screening Execution Pipeline
        </h2>
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-medium pt-1">
          {['HR Approves Candidate', 'Outbound Voice Call Initiated', 'Dynamic Candidate Screening', 'Transcript & Feedback Saved', 'HR Decision Updated'].map((step, idx, arr) => (
            <React.Fragment key={step}>
              <div className="p-2.5 bg-gray-50 border border-gray-200 rounded-md text-gray-800">
                {step}
              </div>
              {idx < arr.length - 1 && <ArrowRight size={14} className="text-gray-400 hidden md:block" />}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Candidate Voice Call List */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4 shadow-xs">
        <h2 className="text-base font-semibold text-gray-900">
          Approved Candidates Queue
        </h2>

        {hrState.candidates.length === 0 ? (
          <p className="text-xs text-gray-500 text-center py-6">No candidates in calling queue.</p>
        ) : (
          <div className="divide-y divide-gray-200 text-xs">
            {hrState.candidates.map(cand => (
              <div key={cand.id} className="py-3 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <p className="font-semibold text-gray-900 text-sm">{cand.name}</p>
                  <p className="text-gray-500">{cand.phone || '+1 (555) 000-0000'} · {cand.email}</p>
                </div>

                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded bg-gray-100 border border-gray-200 text-gray-700 font-medium text-[11px]">
                    Status: {cand.aiCallStatus || 'Pending'}
                  </span>

                  <button
                    onClick={() => hrState.triggerAICall(cand)}
                    className="px-3.5 py-1.5 bg-blue-900 hover:bg-blue-800 text-white font-medium rounded text-xs transition flex items-center gap-1.5"
                  >
                    <PhoneCall size={14} /> Start Call
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
