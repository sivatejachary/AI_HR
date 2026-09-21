'use client';

import React from 'react';
import { useHRState } from '../../../stores/useHRStore';
import { Award, UserCheck, ShieldCheck } from 'lucide-react';

export default function EvaluationsPage() {
  const hrState = useHRState();

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-lg border border-gray-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight flex items-center gap-2">
            <Award size={22} className="text-blue-900" /> Candidate Evaluation & Scorecards
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            Structured candidate scorecards. Human review required for hiring approval.
          </p>
        </div>
      </div>

      {/* Evaluations List */}
      <div className="space-y-4">
        {hrState.evaluations.length === 0 ? (
          <div className="text-center py-12 bg-white border border-gray-200 rounded-lg space-y-2 shadow-xs">
            <Award size={32} className="mx-auto text-gray-400 mb-2" />
            <p className="text-sm font-semibold text-gray-900">No Evaluations Recorded Yet</p>
            <p className="text-xs text-gray-500">Evaluations will appear when candidate interviews are completed.</p>
          </div>
        ) : (
          hrState.evaluations.map(ev => (
            <div key={ev.id} className="bg-white border border-gray-200 rounded-lg p-6 space-y-5 shadow-xs">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-100 pb-4">
                <div>
                  <h3 className="text-base font-semibold text-gray-900">{ev.candidateName}</h3>
                  <p className="text-xs text-gray-500">{ev.jobTitle} · {ev.interviewType}</p>
                </div>

                <div className="flex items-center gap-3">
                  <span className="px-2.5 py-1 rounded bg-blue-50 border border-blue-200 text-blue-900 text-xs font-semibold uppercase">
                    {ev.overallRecommendation.replace('_', ' ')}
                  </span>

                  {ev.humanApproved ? (
                    <span className="px-3 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded text-xs font-semibold flex items-center gap-1.5">
                      <ShieldCheck size={14} /> Approved by {ev.approvedBy}
                    </span>
                  ) : (
                    <button
                      onClick={() => hrState.approveEvaluation(ev.id)}
                      className="px-3.5 py-1.5 bg-blue-900 hover:bg-blue-800 text-white rounded text-xs font-medium transition flex items-center gap-1.5"
                    >
                      <UserCheck size={14} /> Approve Recommendation
                    </button>
                  )}
                </div>
              </div>

              {/* Score Summary Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
                {[
                  { label: 'Technical Mastery', score: ev.technicalScore },
                  { label: 'Communication', score: ev.communicationScore },
                  { label: 'Problem Solving', score: ev.problemSolvingScore },
                  { label: 'Relevant Exp.', score: ev.experienceScore },
                  { label: 'Coding Test', score: ev.codingScore }
                ].map(s => (
                  <div key={s.label} className="p-3 bg-gray-50 rounded border border-gray-200">
                    <p className="text-[11px] font-medium text-gray-500">{s.label}</p>
                    <p className="text-lg font-bold text-gray-900 mt-0.5">{s.score}/100</p>
                  </div>
                ))}
              </div>

              {/* Evaluation Summary */}
              <div className="p-4 bg-gray-50 border border-gray-200 rounded text-xs space-y-2">
                <p className="font-semibold text-gray-900">Evaluation Summary:</p>
                <p className="text-gray-700 leading-relaxed">{ev.summary}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
