'use client';

import React from 'react';
import { useHRState } from '../../../stores/useHRStore';
import { Activity } from 'lucide-react';

export default function ActivityPage() {
  const hrState = useHRState();

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-lg border border-gray-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight flex items-center gap-2">
            <Activity size={22} className="text-blue-900" /> Platform Audit Trail & Activity Log
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            Audit record of recruitment operations, HR approvals, and system executions.
          </p>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-3 shadow-xs">
        {hrState.activityLogs.length === 0 ? (
          <p className="text-xs text-gray-500 text-center py-8">No activity recorded yet.</p>
        ) : (
          <div className="divide-y divide-gray-200 text-xs">
            {hrState.activityLogs.map(log => (
              <div key={log.id} className="py-3 flex items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-900 text-sm">{log.action}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-gray-100 border border-gray-200 text-gray-600 font-medium">
                      {log.actorName}
                    </span>
                  </div>
                  <p className="text-gray-600 mt-0.5">{log.result}</p>
                </div>
                <span className="font-mono text-gray-400 text-xs shrink-0">{log.timestamp}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
