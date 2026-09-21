'use client';

import React from 'react';
import { useHRState } from '../../../stores/useHRStore';
import {
  Bot,
  Zap,
  CheckCircle2,
  Clock,
  Play,
  Pause,
  ListTodo,
  Settings,
  ShieldAlert,
  Activity
} from 'lucide-react';

export default function AgentPage() {
  const hrState = useHRState();
  const agent = hrState.agentState;

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Bot className="text-indigo-400" /> AI HR Autonomous Agent Control Center
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Monitor, start, pause, or override the AI HR Agent execution engine.
          </p>
        </div>

        <button
          onClick={hrState.toggleAgentOnline}
          className={`px-6 py-2.5 rounded-xl font-bold text-xs flex items-center gap-2 transition shadow-lg ${
            agent.isOnline
              ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/30'
              : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/30'
          }`}
        >
          {agent.isOnline ? <Pause size={16} /> : <Play size={16} />}
          {agent.isOnline ? 'Pause Agent Execution' : 'Start Agent Execution'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Capabilities & Status */}
        <div className="space-y-6">
          {/* Agent Status Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider text-indigo-400">Agent Status</h3>
            <div className={`p-4 rounded-2xl border flex items-center justify-between ${
              agent.isOnline ? 'bg-emerald-950/40 border-emerald-800/50 text-emerald-300' : 'bg-amber-950/40 border-amber-800/50 text-amber-300'
            }`}>
              <div className="flex items-center gap-3">
                <span className="relative flex h-3 w-3">
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${agent.isOnline ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                  <span className={`relative inline-flex rounded-full h-3 w-3 ${agent.isOnline ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                </span>
                <div>
                  <p className="font-bold text-sm">{agent.isOnline ? 'ONLINE & ACTIVE' : 'PAUSED BY HR'}</p>
                  <p className="text-[11px] opacity-80">{agent.isOnline ? 'Listening for workflow events' : 'Human override active'}</p>
                </div>
              </div>
            </div>

            <div className="space-y-2 text-xs text-slate-400 pt-2">
              <div className="flex justify-between">
                <span>Voice Engine:</span>
                <span className="text-white font-medium">{agent.voiceId}</span>
              </div>
              <div className="flex justify-between">
                <span>Last Action Time:</span>
                <span className="text-white font-medium">{agent.lastCallTime}</span>
              </div>
            </div>
          </div>

          {/* Capabilities Checklist */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider text-indigo-400">Enabled Capabilities</h3>
            <div className="space-y-2.5 text-xs">
              {agent.capabilities.map((cap: string) => (
                <div key={cap} className="flex items-center gap-2.5 p-2.5 bg-slate-950/80 rounded-xl border border-slate-800 text-slate-200">
                  <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
                  <span>{cap}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Live Task Queue & Activity */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active & Queued Tasks */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <ListTodo size={18} className="text-indigo-400" /> Active Tasks Queue
            </h3>

            {agent.activeTask && (
              <div className="p-4 bg-indigo-950/40 border border-indigo-800/60 rounded-2xl space-y-1">
                <p className="text-[10px] uppercase font-bold text-indigo-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" /> Currently Executing:
                </p>
                <p className="text-sm font-bold text-white">{agent.activeTask}</p>
              </div>
            )}

            <div className="space-y-3 pt-2">
              <p className="text-xs font-semibold text-slate-400">Upcoming Queued Actions ({agent.tasksQueue.length})</p>
              {agent.tasksQueue.map((task: string, idx: number) => (
                <div key={idx} className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl flex items-center gap-3 text-xs text-slate-300">
                  <Clock size={16} className="text-slate-500 shrink-0" />
                  <span>{task}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
