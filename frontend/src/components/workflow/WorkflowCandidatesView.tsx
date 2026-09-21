'use client';

import React, { useState } from 'react';
import { WorkflowStep, Application, Candidate } from '../../types';
import { User, Phone, Mail, FileText, CheckCircle2, ChevronRight, UserCheck } from 'lucide-react';

interface Props {
  steps: WorkflowStep[];
  applications: Application[];
  candidates: Candidate[];
}

export function WorkflowCandidatesView({ steps, applications, candidates }: Props) {
  const [selectedStageName, setSelectedStageName] = useState<string>(steps[0]?.name || 'Application');

  // Map candidates to workflow steps
  const stageCandidatesMap: Record<string, Application[]> = {};
  
  steps.forEach(step => {
    stageCandidatesMap[step.name] = applications.filter(app => {
      // Fuzzy or exact stage match
      const appStage = (app.currentStage || '').toLowerCase();
      const stepName = step.name.toLowerCase();
      return appStage.includes(stepName) || stepName.includes(appStage);
    });
  });

  // Catch-all fallback for first step if applications exist
  if (steps.length > 0 && applications.length > 0) {
    const firstStepName = steps[0].name;
    const matchedCount = Object.values(stageCandidatesMap).reduce((sum, list) => sum + list.length, 0);
    if (matchedCount === 0) {
      stageCandidatesMap[firstStepName] = applications;
    }
  }

  const activeApps = stageCandidatesMap[selectedStageName] || [];

  return (
    <div className="space-y-6">
      {/* Stage Buckets Header */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {steps.map(step => {
          const count = (stageCandidatesMap[step.name] || []).length;
          const isSelected = selectedStageName === step.name;
          return (
            <button
              key={step.id}
              onClick={() => setSelectedStageName(step.name)}
              className={`p-3.5 rounded-xl border text-left transition ${
                isSelected
                  ? 'bg-blue-50/70 border-blue-600 ring-1 ring-blue-600 shadow-2xs'
                  : 'bg-white border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider line-clamp-1">
                {step.name}
              </div>
              <div className="flex items-baseline justify-between mt-1">
                <span className="text-xl font-extrabold text-gray-900">{count}</span>
                <span className="text-[11px] text-gray-400 font-medium">candidates</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Candidates List for Selected Stage */}
      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-2xs">
        <div className="p-4 border-b border-gray-200 bg-gray-50/60 flex items-center justify-between">
          <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
            Candidates in <span className="text-blue-700">{selectedStageName}</span> stage
            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 font-semibold">
              {activeApps.length}
            </span>
          </h3>
        </div>

        {activeApps.length === 0 ? (
          <div className="p-12 text-center text-gray-500 text-xs">
            <UserCheck size={28} className="mx-auto text-gray-400 mb-2" />
            <p className="font-semibold text-gray-700">No candidates currently in this stage</p>
            <p className="text-gray-400 mt-1">As candidates progress through the hiring workflow, they will appear here.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {activeApps.map(app => {
              const cand = candidates.find(c => c.id === app.candidateId);
              return (
                <div key={app.id} className="p-4 hover:bg-gray-50/80 transition flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-blue-100 text-blue-900 font-bold text-xs flex items-center justify-center">
                      {(app.candidateName || 'C')[0]}
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-gray-900">{app.candidateName}</h4>
                      <p className="text-[11px] text-gray-500 flex items-center gap-3 mt-0.5">
                        <span>Role: {app.jobTitle}</span>
                        <span>•</span>
                        <span>Source: {app.source}</span>
                        <span>•</span>
                        <span>Applied: {app.appliedAt}</span>
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {app.screeningResult && (
                      <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200">
                        Match Score: {app.screeningResult.matchScore}%
                      </span>
                    )}
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-gray-100 text-gray-700 border border-gray-200">
                      {app.status}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
