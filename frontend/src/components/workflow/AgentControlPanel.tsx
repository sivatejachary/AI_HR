'use client';

import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { useHRState } from '../../stores/useHRStore';
import {
  Play,
  Pause,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Activity,
  Bot,
  ShieldCheck,
  UserCheck,
  Zap,
  ArrowRight
} from 'lucide-react';

interface Props {
  jobId?: string;
  workflowId?: string;
  isPaused?: boolean;
  onTogglePause?: () => void;
}

export function AgentControlPanel({ jobId, workflowId, isPaused = false, onTogglePause }: Props) {
  const hrState = useHRState();
  const [stats, setStats] = useState({
    running: 0,
    waiting_for_hr: 0,
    completed: 0,
    failed: 0,
    needs_attention: 0
  });

  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await api.getAutomationStats(jobId);
        if (data) setStats(data);
      } catch (err) {
        // Fallback local state calculation
        const apps = hrState.applications;
        const running = apps.filter(a => a.status === 'CALLING' || a.status === 'SCREENING').length;
        const waiting = apps.filter(a => a.status === 'HR_REVIEW' || a.status === 'AI_SHORTLISTED').length;
        const completed = apps.filter(a => a.status === 'HR_APPROVED' || a.status === 'INTERVIEW_COMPLETED' || a.status === 'SELECTED').length;
        const failed = apps.filter(a => a.status === 'HR_REJECTED' || a.status === 'REJECTED').length;
        setStats({
          running,
          waiting_for_hr: waiting,
          completed,
          failed,
          needs_attention: waiting + failed
        });
      }
    }

    loadStats();
  }, [jobId, hrState.applications]);

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-2xs space-y-4">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-100 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center font-bold">
            <Bot size={18} />
          </div>
          <div>
            <h3 className="text-xs font-bold text-gray-900 flex items-center gap-2">
              Workflow Execution Engine & AI Agent Status
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                isPaused ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
              }`}>
                {isPaused ? 'PAUSED BY HR' : 'ACTIVE EXECUTION'}
              </span>
            </h3>
            <p className="text-[11px] text-gray-500 mt-0.5">
              Source of truth process runner • Executing HR-configured pipeline rules
            </p>
          </div>
        </div>

        {onTogglePause && (
          <button
            onClick={onTogglePause}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
              isPaused
                ? 'bg-emerald-700 hover:bg-emerald-800 text-white shadow-xs'
                : 'bg-amber-50 text-amber-900 border border-amber-300 hover:bg-amber-100'
            }`}
          >
            {isPaused ? <Play size={14} /> : <Pause size={14} />}
            {isPaused ? 'Resume Workflow Execution' : 'Pause Workflow Execution'}
          </button>
        )}
      </div>

      {/* Operational Operational Counter Cards (Section 18) */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div className="p-3 bg-blue-50/50 border border-blue-100 rounded-lg">
          <div className="flex items-center justify-between text-[11px] font-semibold text-blue-700">
            <span>Running</span>
            <Activity size={14} />
          </div>
          <p className="text-xl font-extrabold text-blue-900 mt-1">{stats.running}</p>
          <span className="text-[10px] text-blue-600">Automated steps in progress</span>
        </div>

        <div className="p-3 bg-amber-50/50 border border-amber-200 rounded-lg">
          <div className="flex items-center justify-between text-[11px] font-semibold text-amber-800">
            <span>Waiting for HR</span>
            <Clock size={14} />
          </div>
          <p className="text-xl font-extrabold text-amber-900 mt-1">{stats.waiting_for_hr}</p>
          <span className="text-[10px] text-amber-700">Awaiting human sign-off</span>
        </div>

        <div className="p-3 bg-emerald-50/50 border border-emerald-100 rounded-lg">
          <div className="flex items-center justify-between text-[11px] font-semibold text-emerald-800">
            <span>Completed</span>
            <CheckCircle2 size={14} />
          </div>
          <p className="text-xl font-extrabold text-emerald-900 mt-1">{stats.completed}</p>
          <span className="text-[10px] text-emerald-700">Steps successfully passed</span>
        </div>

        <div className="p-3 bg-red-50/50 border border-red-100 rounded-lg">
          <div className="flex items-center justify-between text-[11px] font-semibold text-red-700">
            <span>Failed</span>
            <AlertTriangle size={14} />
          </div>
          <p className="text-xl font-extrabold text-red-900 mt-1">{stats.failed}</p>
          <span className="text-[10px] text-red-600">Errors requiring retry</span>
        </div>

        <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <div className="flex items-center justify-between text-[11px] font-semibold text-gray-700">
            <span>Needs Attention</span>
            <ShieldCheck size={14} />
          </div>
          <p className="text-xl font-extrabold text-gray-900 mt-1">{stats.needs_attention}</p>
          <span className="text-[10px] text-gray-500">Action items for HR</span>
        </div>
      </div>
    </div>
  );
}
