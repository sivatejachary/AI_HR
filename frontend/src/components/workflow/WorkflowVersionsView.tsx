'use client';

import React from 'react';
import { HiringWorkflow } from '../../types';
import { GitBranch, CheckCircle2, Clock, Archive, ArrowUpRight } from 'lucide-react';

interface Props {
  workflow: HiringWorkflow;
  onPublishVersion: () => void;
  onArchiveWorkflow: () => void;
}

export function WorkflowVersionsView({ workflow, onPublishVersion, onArchiveWorkflow }: Props) {
  const versions = [
    {
      version: workflow.version,
      status: workflow.status,
      updatedAt: workflow.updatedAt || workflow.createdAt || 'Today',
      stepsCount: workflow.steps.length,
      author: workflow.ownerName || 'Sarah Jenkins (HR Recruiter)',
      isCurrent: true
    },
    ...(workflow.version > 1 ? [
      {
        version: workflow.version - 1,
        status: 'Published' as const,
        updatedAt: 'Previous version',
        stepsCount: Math.max(1, workflow.steps.length - 1),
        author: 'Sarah Jenkins (HR Recruiter)',
        isCurrent: false
      }
    ] : [])
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-2xs">
        <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
          <GitBranch size={18} className="text-blue-700" /> Version History & Management
        </h3>
        <p className="text-xs text-gray-500 mt-1">
          Active candidates follow the published workflow version. Edits can be saved as draft before publishing.
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-2xs">
        <table className="w-full text-left text-xs">
          <thead className="bg-gray-50 border-b border-gray-200 text-gray-500 font-semibold">
            <tr>
              <th className="p-3.5">Version</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5">Steps Count</th>
              <th className="p-3.5">Author</th>
              <th className="p-3.5">Last Updated</th>
              <th className="p-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {versions.map(v => (
              <tr key={v.version} className={v.isCurrent ? 'bg-blue-50/30 font-medium' : 'hover:bg-gray-50'}>
                <td className="p-3.5 font-bold text-gray-900 flex items-center gap-2">
                  <span>Version {v.version}</span>
                  {v.isCurrent && (
                    <span className="text-[10px] bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-semibold">
                      Current
                    </span>
                  )}
                </td>
                <td className="p-3.5">
                  <span className={`px-2.5 py-1 rounded-md text-[11px] font-semibold border ${
                    v.status === 'Published'
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      : v.status === 'Draft'
                      ? 'bg-amber-50 text-amber-700 border-amber-200'
                      : 'bg-gray-100 text-gray-600 border-gray-200'
                  }`}>
                    {v.status}
                  </span>
                </td>
                <td className="p-3.5 text-gray-700">{v.stepsCount} steps</td>
                <td className="p-3.5 text-gray-700">{v.author}</td>
                <td className="p-3.5 text-gray-500">{v.updatedAt}</td>
                <td className="p-3.5 text-right space-x-2">
                  {v.status === 'Draft' && (
                    <button
                      onClick={onPublishVersion}
                      className="px-3 py-1 bg-blue-700 hover:bg-blue-800 text-white font-semibold text-xs rounded-md shadow-2xs"
                    >
                      Publish Version
                    </button>
                  )}
                  {v.isCurrent && v.status !== 'Archived' && (
                    <button
                      onClick={onArchiveWorkflow}
                      className="px-3 py-1 border border-gray-300 text-gray-700 hover:bg-gray-100 font-medium text-xs rounded-md"
                    >
                      Archive
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
