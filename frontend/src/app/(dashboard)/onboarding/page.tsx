'use client';

import React from 'react';
import { useHRState } from '../../../stores/useHRStore';
import { UserCheck2, CheckCircle2 } from 'lucide-react';
import { EmptyState } from '../../../components/ui/EmptyState';

export default function OnboardingPage() {
  const hrState = useHRState();

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-lg border border-gray-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight flex items-center gap-2">
            <UserCheck2 size={22} className="text-blue-900" /> Employee Onboarding Tracker
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            Track document collection, background verification, and IT provisioning tasks.
          </p>
        </div>
      </div>

      {hrState.onboarding.length === 0 ? (
        <EmptyState
          icon={UserCheck2}
          title="No onboarding tasks active"
          description="Onboarding task lists will be generated once candidate offer letters are accepted."
        />
      ) : (
        <div className="space-y-4 text-xs">
          {hrState.onboarding.map(onb => (
            <div key={onb.id} className="bg-white border border-gray-200 rounded-lg p-6 space-y-4 shadow-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-100 pb-3">
                <div>
                  <h3 className="text-base font-semibold text-gray-900">{onb.candidateName}</h3>
                  <p className="text-xs text-gray-500">{onb.jobTitle} · Joining Date: {onb.joiningDate}</p>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="text-[11px] text-gray-500 font-medium">Onboarding Progress</p>
                    <p className="text-base font-bold text-emerald-700">{onb.progressPercent}%</p>
                  </div>
                  <div className="w-20 h-2 bg-gray-100 rounded-full overflow-hidden border border-gray-200">
                    <div className="h-full bg-emerald-600 rounded-full" style={{ width: `${onb.progressPercent}%` }} />
                  </div>
                </div>
              </div>

              {/* Subtasks checklist */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Required Onboarding Checklist</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {onb.tasks.map(task => (
                    <div key={task.id} className="p-2.5 bg-gray-50 border border-gray-200 rounded flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 size={15} className={task.isCompleted ? 'text-emerald-700' : 'text-gray-400'} />
                        <span className={task.isCompleted ? 'text-gray-500 line-through' : 'text-gray-800 font-medium'}>
                          {task.title}
                        </span>
                      </div>
                      <span className="text-[11px] text-gray-400">Due: {task.dueDate}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
