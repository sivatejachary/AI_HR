'use client';

import React from 'react';
import { useHRState } from '../../../stores/useHRStore';
import { BarChart3, Share2 } from 'lucide-react';

export default function ReportsPage() {
  const hrState = useHRState();

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-lg border border-gray-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight flex items-center gap-2">
            <BarChart3 size={22} className="text-blue-900" /> Source Analytics & Funnel Reports
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            Track candidate volumes, screening conversions, and hiring outcomes by sourcing channel.
          </p>
        </div>
      </div>

      {/* Sourcing Channel Performance Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-xs">
        <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
            <Share2 size={16} className="text-gray-500" /> Channel Conversion Funnel
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold uppercase tracking-wider text-[11px]">
                <th className="py-3 px-4">Sourcing Channel</th>
                <th className="py-3 px-4 text-center">Total Applications</th>
                <th className="py-3 px-4 text-center">Screening Passed</th>
                <th className="py-3 px-4 text-center">Interviews Scheduled</th>
                <th className="py-3 px-4 text-center">Selected Candidates</th>
                <th className="py-3 px-4 text-right">Conversion Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 text-gray-700">
              {hrState.sourceAnalytics.map(src => {
                const convRate = src.applicationsCount > 0 ? Math.round((src.selectedCount / src.applicationsCount) * 100) : 0;
                return (
                  <tr key={src.source} className="hover:bg-gray-50/80 transition">
                    <td className="py-3 px-4 font-semibold text-gray-900">
                      {src.source}
                    </td>
                    <td className="py-3 px-4 text-center font-bold text-gray-900">{src.applicationsCount}</td>
                    <td className="py-3 px-4 text-center font-medium text-gray-700">{src.screeningPassed}</td>
                    <td className="py-3 px-4 text-center font-medium text-gray-700">{src.interviewsScheduled}</td>
                    <td className="py-3 px-4 text-center font-bold text-emerald-700">{src.selectedCount}</td>
                    <td className="py-3 px-4 text-right">
                      <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                        {convRate}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
