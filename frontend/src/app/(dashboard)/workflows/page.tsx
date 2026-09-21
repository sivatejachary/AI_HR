'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useHRState } from '../../../stores/useHRStore';
import { WorkflowStatus } from '../../../types';
import {
  Plus,
  GitFork,
  Search,
  Filter,
  MoreVertical,
  Edit3,
  Copy,
  Archive,
  Trash2,
  CheckCircle2,
  Clock,
  Layers,
  FileText
} from 'lucide-react';

export default function WorkflowsPage() {
  const router = useRouter();
  const hrState = useHRState();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');

  // Active action dropdown
  const [activeMenuId, setActiveMenuId] = useState<string | null>(null);

  const workflows = hrState.workflows;

  const filteredWorkflows = workflows.filter(wf => {
    const matchesSearch =
      wf.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (wf.jobTitle || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDept = selectedDept === 'ALL' || wf.department === selectedDept;
    const matchesStatus = selectedStatus === 'ALL' || wf.status === selectedStatus;
    return matchesSearch && matchesDept && matchesStatus;
  });

  const uniqueDepartments = Array.from(
    new Set(workflows.map(w => w.department).filter(Boolean))
  );

  const handleDuplicate = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    hrState.duplicateWorkflow(id);
    setActiveMenuId(null);
  };

  const handleArchive = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    hrState.archiveWorkflow(id);
    setActiveMenuId(null);
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    hrState.deleteWorkflow(id);
    setActiveMenuId(null);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Banner Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-gray-200 shadow-2xs">
        <div>
          <h1 className="text-xl font-bold text-gray-900 tracking-tight flex items-center gap-2">
            <GitFork size={22} className="text-blue-700" /> Hiring Workflows
          </h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Create and manage role-based hiring workflows for your open positions.
          </p>
        </div>

        <Link
          href="/workflows/create"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white font-semibold text-xs rounded-lg shadow-xs transition"
        >
          <Plus size={15} /> Create Workflow
        </Link>
      </div>

      {/* Filter and Search Bar */}
      {workflows.length > 0 && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-gray-200 shadow-2xs">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" size={15} />
            <input
              type="text"
              placeholder="Search workflows by name or job role..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full border border-gray-300 rounded-lg pl-9 pr-4 py-1.5 text-xs text-gray-900 focus:ring-2 focus:ring-blue-600 outline-none"
            />
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs text-gray-600">
              <Filter size={14} className="text-gray-400" /> Department:
              <select
                value={selectedDept}
                onChange={e => setSelectedDept(e.target.value)}
                className="border border-gray-300 rounded-lg px-2.5 py-1 text-xs text-gray-900 bg-white"
              >
                <option value="ALL">All Departments</option>
                {uniqueDepartments.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-1.5 text-xs text-gray-600">
              Status:
              <select
                value={selectedStatus}
                onChange={e => setSelectedStatus(e.target.value)}
                className="border border-gray-300 rounded-lg px-2.5 py-1 text-xs text-gray-900 bg-white"
              >
                <option value="ALL">All Statuses</option>
                <option value="Published">Published</option>
                <option value="Draft">Draft</option>
                <option value="Archived">Archived</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      {workflows.length === 0 ? (
        /* Empty State */
        <div className="bg-white border border-gray-200 rounded-xl p-12 text-center shadow-2xs space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-700 flex items-center justify-center mx-auto">
            <GitFork size={28} />
          </div>
          <div className="space-y-1">
            <h2 className="text-base font-bold text-gray-900">No hiring workflows yet</h2>
            <p className="text-xs text-gray-500 max-w-sm mx-auto">
              Create a workflow for a job to define how candidates move through your hiring process.
            </p>
          </div>
          <Link
            href="/workflows/create"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white font-semibold text-xs rounded-lg shadow-xs transition"
          >
            <Plus size={15} /> Create Workflow
          </Link>
        </div>
      ) : (
        /* Workflows Data Table */
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-2xs">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 border-b border-gray-200 text-gray-500 font-semibold uppercase tracking-wider">
              <tr>
                <th className="p-3.5">Workflow Name</th>
                <th className="p-3.5">Job Role</th>
                <th className="p-3.5">Department</th>
                <th className="p-3.5">Steps</th>
                <th className="p-3.5">Version</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Updated</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredWorkflows.map(wf => (
                <tr
                  key={wf.id}
                  onClick={() => router.push(`/workflows/${wf.id}`)}
                  className="hover:bg-gray-50/80 cursor-pointer transition group"
                >
                  <td className="p-3.5 font-bold text-gray-900 group-hover:text-blue-700">
                    {wf.name}
                  </td>
                  <td className="p-3.5 text-gray-700 font-medium">
                    {wf.jobTitle || 'General / Unassigned'}
                  </td>
                  <td className="p-3.5 text-gray-600">
                    {wf.department || 'Engineering'}
                  </td>
                  <td className="p-3.5 text-gray-700">
                    <span className="font-semibold text-gray-900">{wf.steps.length}</span> steps
                  </td>
                  <td className="p-3.5 font-semibold text-gray-700">
                    v{wf.version}
                  </td>
                  <td className="p-3.5">
                    <span className={`px-2.5 py-1 rounded-md text-[11px] font-semibold border ${
                      wf.status === 'Published'
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                        : wf.status === 'Draft'
                        ? 'bg-amber-50 text-amber-700 border-amber-200'
                        : 'bg-gray-100 text-gray-600 border-gray-200'
                    }`}>
                      {wf.status}
                    </span>
                  </td>
                  <td className="p-3.5 text-gray-500">
                    {wf.updatedAt || wf.createdAt || 'Today'}
                  </td>
                  <td className="p-3.5 text-right relative" onClick={e => e.stopPropagation()}>
                    <button
                      onClick={() => setActiveMenuId(activeMenuId === wf.id ? null : wf.id)}
                      className="p-1.5 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition"
                    >
                      <MoreVertical size={16} />
                    </button>

                    {activeMenuId === wf.id && (
                      <div className="absolute right-3 top-10 w-44 bg-white border border-gray-200 rounded-lg shadow-lg z-50 py-1 text-xs text-left">
                        <button
                          onClick={() => {
                            setActiveMenuId(null);
                            router.push(`/workflows/${wf.id}`);
                          }}
                          className="w-full px-3 py-1.5 text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                        >
                          <Edit3 size={14} /> Edit Workflow
                        </button>
                        <button
                          onClick={(e) => handleDuplicate(wf.id, e)}
                          className="w-full px-3 py-1.5 text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                        >
                          <Copy size={14} /> Duplicate
                        </button>
                        <button
                          onClick={(e) => handleArchive(wf.id, e)}
                          className="w-full px-3 py-1.5 text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                        >
                          <Archive size={14} /> Archive
                        </button>
                        <button
                          onClick={(e) => handleDelete(wf.id, e)}
                          className="w-full px-3 py-1.5 text-red-600 hover:bg-red-50 flex items-center gap-2 border-t border-gray-100"
                        >
                          <Trash2 size={14} /> Delete
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
