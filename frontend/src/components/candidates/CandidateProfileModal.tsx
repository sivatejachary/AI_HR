'use client';

import React, { useState } from 'react';
import { Candidate, CallLog, Interview, ActivityLogItem } from '../../types';
import {
  X,
  User,
  Mail,
  Phone,
  MapPin,
  Briefcase,
  FileText,
  PhoneCall,
  Calendar,
  MessageSquare,
  History,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Play,
  Pause,
  Volume2,
  ShieldAlert,
  ArrowRight,
  Bot,
  UserCheck
} from 'lucide-react';

export function CandidateProfileModal({
  candidate,
  onClose,
  onToggleTakeover,
  onTriggerCall,
  onStartInterview
}: {
  candidate: Candidate;
  onClose: () => void;
  onToggleTakeover: (id: string) => void;
  onTriggerCall: (c: Candidate) => void;
  onStartInterview: (c: Candidate) => void;
}) {
  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://ai-hrs.onrender.com';
  const [activeTab, setActiveTab] = useState<'overview' | 'resume' | 'workflow' | 'calls' | 'interviews' | 'timeline'>('overview');
  const [playingCallId, setPlayingCallId] = useState<string | null>(null);
  const [timelineData, setTimelineData] = useState<any>(null);
  const [loadingTimeline, setLoadingTimeline] = useState<boolean>(false);
  const [rescheduleStepId, setRescheduleStepId] = useState<string | null>(null);
  const [newScheduleTime, setNewScheduleTime] = useState<string>('');

  const fetchTimeline = async () => {
    try {
      setLoadingTimeline(true);
      const res = await fetch(`${BACKEND_URL}/api/candidates/${candidate.id}/workflow/steps-timeline`);
      if (res.ok) {
        const data = await res.json();
        setTimelineData(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingTimeline(false);
    }
  };

  React.useEffect(() => {
    if (activeTab === 'workflow') {
      fetchTimeline();
    }
  }, [activeTab]);

  const handleRunNow = async (stepId: string) => {
    try {
      await fetch(`${BACKEND_URL}/api/candidates/${candidate.id}/workflow/run-now`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ step_id: stepId })
      });
      fetchTimeline();
    } catch (e) {
      console.error(e);
    }
  };

  const handleSkip = async (stepId: string) => {
    try {
      await fetch(`${BACKEND_URL}/api/candidates/${candidate.id}/workflow/skip`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ step_id: stepId })
      });
      fetchTimeline();
    } catch (e) {
      console.error(e);
    }
  };

  const handleRescheduleSubmit = async (stepId: string) => {
    if (!newScheduleTime) return;
    try {
      await fetch(`${BACKEND_URL}/api/candidates/${candidate.id}/workflow/reschedule`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ step_id: stepId, scheduled_at: newScheduleTime })
      });
      setRescheduleStepId(null);
      fetchTimeline();
    } catch (e) {
      console.error(e);
    }
  };


  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-5xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Top Header */}
        <div className="p-6 border-b border-slate-800 bg-slate-900/90 flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xl font-bold shadow-lg shadow-indigo-500/20">
              {candidate.name.split(' ').map(n => n[0]).join('')}
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-bold text-white">{candidate.name}</h2>
                <span className="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                  ID: {candidate.id}
                </span>
                {candidate.isHumanTakeover ? (
                  <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                    <ShieldAlert size={12} /> HUMAN TAKEOVER
                  </span>
                ) : (
                  <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                    <Bot size={12} /> AI AGENT ACTIVE
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
                <Briefcase size={13} className="text-indigo-400" /> {candidate.jobTitle} • Current Stage:{' '}
                <span className="text-indigo-300 font-semibold">{candidate.currentStage}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Takeover toggle */}
            <button
              onClick={() => onToggleTakeover(candidate.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition ${
                candidate.isHumanTakeover
                  ? 'bg-emerald-600/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-600/30'
                  : 'bg-amber-600/20 text-amber-300 border border-amber-500/40 hover:bg-amber-600/30'
              }`}
            >
              {candidate.isHumanTakeover ? (
                <>
                  <Bot size={14} /> Resume AI Agent
                </>
              ) : (
                <>
                  <UserCheck size={14} /> HR Takeover
                </>
              )}
            </button>

            {/* AI Call button */}
            <button
              onClick={() => onTriggerCall(candidate)}
              className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition shadow-md shadow-indigo-600/30"
            >
              <PhoneCall size={14} /> AI Voice Call
            </button>

            {/* Close button */}
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-800 px-6 bg-slate-900/50 text-xs font-medium text-slate-400">
          {[
            { key: 'overview', label: 'Overview', icon: User },
            { key: 'resume', label: 'Resume', icon: FileText },
            { key: 'workflow', label: 'Workflow Progress', icon: CheckCircle2 },
            { key: 'calls', label: `AI HR Calls (${candidate.calls.length})`, icon: PhoneCall },
            { key: 'interviews', label: `Interviews (${candidate.interviews.length})`, icon: Calendar },
            { key: 'timeline', label: 'Activity Log', icon: History }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`py-3 px-4 border-b-2 font-medium flex items-center gap-2 transition ${
                  isActive
                    ? 'border-indigo-500 text-indigo-400 font-semibold bg-indigo-500/5'
                    : 'border-transparent hover:text-slate-200'
                }`}
              >
                <Icon size={14} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Modal Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2 space-y-6">
                <div className="bg-slate-800/40 border border-slate-800 rounded-xl p-5 space-y-4">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider text-indigo-400">Contact Information</h3>
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div>
                      <p className="text-slate-400">Email Address</p>
                      <p className="text-slate-200 font-medium mt-0.5 flex items-center gap-1.5">
                        <Mail size={13} className="text-slate-400" /> {candidate.email}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-400">Phone Number</p>
                      <p className="text-slate-200 font-medium mt-0.5 flex items-center gap-1.5">
                        <Phone size={13} className="text-slate-400" /> {candidate.phone}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-400">Location</p>
                      <p className="text-slate-200 font-medium mt-0.5 flex items-center gap-1.5">
                        <MapPin size={13} className="text-slate-400" /> {candidate.location}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-400">Application Date</p>
                      <p className="text-slate-200 font-medium mt-0.5">{candidate.appliedDate}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-800/40 border border-slate-800 rounded-xl p-5 space-y-3">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider text-indigo-400">AI Screening Summary</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {candidate.resumeText || 'Candidate exhibits strong backend engineering fundamentals with Python, FastAPI, and relational database tuning. Passed initial AI resume screening threshold (score: 92/100).'}
                  </p>
                </div>
              </div>

              {/* Right Summary Sidebar */}
              <div className="space-y-4">
                <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 space-y-4">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Assigned Workflow</h3>
                  <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-xs space-y-1">
                    <p className="font-semibold text-indigo-300">Software Engineer Workflow</p>
                    <p className="text-[11px] text-slate-400">Version 1 • Assigned automatically</p>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between text-slate-400">
                      <span>Assigned Owner:</span>
                      <span className="text-slate-200 font-medium">{candidate.ownerName}</span>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Last Activity:</span>
                      <span className="text-slate-200 font-medium">{candidate.lastActivity}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: RESUME */}
          {activeTab === 'resume' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between bg-slate-800/40 p-4 rounded-xl border border-slate-800">
                <div className="flex items-center gap-3">
                  <FileText size={24} className="text-indigo-400" />
                  <div>
                    <p className="text-sm font-semibold text-white">{candidate.name}_Resume.pdf</p>
                    <p className="text-xs text-slate-400">Parsed by AI Resume Parser Engine</p>
                  </div>
                </div>
                <a
                  href="#"
                  onClick={e => e.preventDefault()}
                  className="px-3 py-1.5 bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 hover:bg-indigo-600/30 text-xs font-semibold rounded-lg"
                >
                  Download Resume
                </a>
              </div>

              <div className="p-6 bg-slate-950 border border-slate-800 rounded-xl font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
                {candidate.resumeText || 'No plain text available.'}
              </div>
            </div>
          )}

          {/* TAB 3: WORKFLOW PROGRESS STEPPER & HR MANUAL SCHEDULER */}
          {activeTab === 'workflow' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider text-indigo-400">
                    Candidate Hiring Workflow Schedule & Progress
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">HR Manual Control & Single Source of Truth Engine Status</p>
                </div>
                {loadingTimeline && (
                  <span className="text-xs text-indigo-400 animate-pulse font-semibold">Loading engine schedule...</span>
                )}
              </div>

              {timelineData?.steps && timelineData.steps.length > 0 ? (
                <div className="space-y-4">
                  {timelineData.steps.map((st: any, idx: number) => {
                    const isCompleted = st.status === 'COMPLETED';
                    const isReady = st.status === 'READY';
                    const isWaitingHuman = st.status === 'WAITING_FOR_HUMAN';
                    const isSkipped = st.status === 'SKIPPED';
                    const isFailed = st.status === 'FAILED';

                    return (
                      <div
                        key={st.step_id || idx}
                        className={`p-4 rounded-xl border transition space-y-3 ${
                          isCompleted
                            ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-300'
                            : isReady
                            ? 'bg-indigo-950/40 border-indigo-700/60 text-indigo-200 shadow-md shadow-indigo-950/50'
                            : isWaitingHuman
                            ? 'bg-amber-950/30 border-amber-700/60 text-amber-200'
                            : isSkipped
                            ? 'bg-slate-900/60 border-slate-800 text-slate-400 opacity-75'
                            : isFailed
                            ? 'bg-red-950/30 border-red-800/50 text-red-300'
                            : 'bg-slate-900/40 border-slate-800 text-slate-400'
                        }`}
                      >
                        <div className="flex items-center justify-between gap-3">
                          <div className="flex items-center gap-3">
                            <div
                              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
                                isCompleted
                                  ? 'bg-emerald-500 text-slate-950'
                                  : isReady
                                  ? 'bg-indigo-500 text-white animate-pulse'
                                  : isWaitingHuman
                                  ? 'bg-amber-500 text-slate-950'
                                  : isFailed
                                  ? 'bg-red-500 text-white'
                                  : 'bg-slate-800 text-slate-400'
                              }`}
                            >
                              {isCompleted ? <CheckCircle2 size={16} /> : idx + 1}
                            </div>
                            <div>
                              <p className="font-bold text-sm text-white flex items-center gap-2">
                                {st.step_name}
                                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                                  {st.schedule_type}
                                </span>
                                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-indigo-900/50 text-indigo-300 border border-indigo-700/50">
                                  Executor: {st.executor}
                                </span>
                              </p>
                              <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-3">
                                {st.scheduled_at && (
                                  <span>Scheduled: <strong className="text-slate-200">{new Date(st.scheduled_at).toLocaleString()}</strong></span>
                                )}
                                {st.completed_at && (
                                  <span>Completed: <strong className="text-emerald-400">{new Date(st.completed_at).toLocaleString()}</strong></span>
                                )}
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <span
                              className={`text-[11px] font-extrabold px-2.5 py-1 rounded border ${
                                isCompleted
                                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                                  : isReady
                                  ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30'
                                  : isWaitingHuman
                                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                                  : isSkipped
                                  ? 'bg-slate-800 text-slate-400 border-slate-700'
                                  : isFailed
                                  ? 'bg-red-500/20 text-red-300 border-red-500/30'
                                  : 'bg-slate-800 text-slate-400 border-slate-700'
                              }`}
                            >
                              {st.status}
                            </span>
                          </div>
                        </div>

                        {/* HR Manual Controls Toolbar */}
                        {!isCompleted && !isSkipped && (
                          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => handleRunNow(st.step_id)}
                                className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-semibold text-[11px] flex items-center gap-1 transition shadow-xs"
                              >
                                <Play size={11} /> Run Now
                              </button>

                              <button
                                onClick={() => {
                                  setRescheduleStepId(rescheduleStepId === st.step_id ? null : st.step_id);
                                  setNewScheduleTime(st.scheduled_at ? new Date(st.scheduled_at).toISOString().slice(0, 16) : '');
                                }}
                                className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded font-semibold text-[11px] flex items-center gap-1 transition"
                              >
                                <Clock size={11} /> Reschedule
                              </button>

                              {st.allow_skip !== false && (
                                <button
                                  onClick={() => handleSkip(st.step_id)}
                                  className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-amber-300 border border-slate-700 rounded font-semibold text-[11px] flex items-center gap-1 transition"
                                >
                                  Skip Step
                                </button>
                              )}
                            </div>

                            {rescheduleStepId === st.step_id && (
                              <div className="flex items-center gap-2 bg-slate-950 p-2 rounded-lg border border-indigo-700">
                                <input
                                  type="datetime-local"
                                  value={newScheduleTime}
                                  onChange={e => setNewScheduleTime(e.target.value)}
                                  className="bg-slate-900 border border-slate-700 text-white text-xs rounded px-2 py-1"
                                />
                                <button
                                  onClick={() => handleRescheduleSubmit(st.step_id)}
                                  className="px-2 py-1 bg-indigo-600 text-white font-semibold rounded text-xs"
                                >
                                  Save
                                </button>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="space-y-4">
                  {(candidate.stageProgress || []).map((sp: any, idx: number) => (
                    <div
                      key={sp.stage}
                      className={`flex items-center gap-4 p-4 rounded-xl border transition ${
                        sp.status === 'completed'
                          ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-300'
                          : sp.status === 'current'
                          ? 'bg-indigo-950/40 border-indigo-700/60 text-indigo-200 shadow-md shadow-indigo-950/50'
                          : 'bg-slate-900/40 border-slate-800 text-slate-500'
                      }`}
                    >
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
                          sp.status === 'completed'
                            ? 'bg-emerald-500 text-slate-950'
                            : sp.status === 'current'
                            ? 'bg-indigo-500 text-white animate-pulse'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {sp.status === 'completed' ? <CheckCircle2 size={16} /> : idx + 1}
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold text-sm">{sp.stage}</p>
                        <p className="text-xs text-slate-400">
                          {sp.status === 'completed'
                            ? `Completed on ${sp.completedAt || 'Recently'}`
                            : sp.status === 'current'
                            ? 'In Progress (Active Stage)'
                            : 'Pending previous step completion'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}


          {/* TAB 4: AI HR CALLS */}
          {activeTab === 'calls' && (
            <div className="space-y-6">
              {candidate.calls.length === 0 ? (
                <div className="text-center py-12 bg-slate-800/20 border border-slate-800 rounded-xl">
                  <PhoneCall size={32} className="mx-auto text-slate-500 mb-2" />
                  <p className="text-sm font-semibold text-slate-300">No AI Calls Made Yet</p>
                  <button
                    onClick={() => onTriggerCall(candidate)}
                    className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-500 transition"
                  >
                    Initiate Outbound Call Now
                  </button>
                </div>
              ) : (
                candidate.calls.map(call => (
                  <div key={call.id} className="bg-slate-800/40 border border-slate-800 rounded-xl p-5 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 flex items-center justify-center">
                          <PhoneCall size={18} />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-white">Outbound Screening Call</p>
                          <p className="text-xs text-slate-400">{call.callDate} • Duration: {call.durationSeconds}s</p>
                        </div>
                      </div>
                      <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        {call.status}
                      </span>
                    </div>

                    <div className="p-3 bg-slate-900 rounded-lg text-xs text-slate-300 space-y-1">
                      <p className="font-semibold text-indigo-400">AI Call Summary:</p>
                      <p>{call.summary}</p>
                    </div>

                    {/* Audio Player Simulator */}
                    <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center gap-4">
                      <button
                        onClick={() => setPlayingCallId(playingCallId === call.id ? null : call.id)}
                        className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center hover:bg-indigo-500 transition shrink-0"
                      >
                        {playingCallId === call.id ? <Pause size={14} /> : <Play size={14} className="ml-0.5" />}
                      </button>
                      <div className="flex-1 space-y-1">
                        <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full bg-indigo-500 transition-all ${
                              playingCallId === call.id ? 'w-2/3 animate-pulse' : 'w-0'
                            }`}
                          />
                        </div>
                        <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                          <span>{playingCallId === call.id ? '01:24' : '00:00'}</span>
                          <span>04:05</span>
                        </div>
                      </div>
                      <Volume2 size={16} className="text-slate-400" />
                    </div>

                    {/* Transcript */}
                    {call.transcript && call.transcript.length > 0 && (
                      <div className="space-y-2 pt-2">
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Full Call Transcript</p>
                        <div className="space-y-2 max-h-48 overflow-y-auto p-3 bg-slate-950 rounded-lg text-xs">
                          {call.transcript.map((t, idx) => (
                            <div key={idx} className="flex gap-2">
                              <span className={`font-bold shrink-0 ${t.speaker === 'AI' ? 'text-indigo-400' : 'text-emerald-400'}`}>
                                {t.speaker}:
                              </span>
                              <span className="text-slate-300">{t.text}</span>
                              <span className="ml-auto text-[10px] text-slate-500 font-mono">{t.time}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* TAB 5: INTERVIEWS */}
          {activeTab === 'interviews' && (
            <div className="space-y-4">
              {candidate.interviews.length === 0 ? (
                <div className="text-center py-12 bg-slate-800/20 border border-slate-800 rounded-xl">
                  <Calendar size={32} className="mx-auto text-slate-500 mb-2" />
                  <p className="text-sm font-semibold text-slate-300">No Interviews Scheduled Yet</p>
                  <button
                    onClick={() => onStartInterview(candidate)}
                    className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-500 transition"
                  >
                    Launch AI Technical Interview Room
                  </button>
                </div>
              ) : (
                candidate.interviews.map(int => (
                  <div key={int.id} className="bg-slate-800/40 border border-slate-800 rounded-xl p-5 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-purple-500/20 border border-purple-500/40 text-purple-300 flex items-center justify-center">
                          <Calendar size={18} />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-white">{int.type.replace('_', ' ')}</p>
                          <p className="text-xs text-slate-400">{int.date} at {int.time} • Platform: {int.platform}</p>
                        </div>
                      </div>
                      <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        {int.status}
                      </span>
                    </div>
                    <div className="flex items-center justify-between pt-2">
                      <span className="text-xs text-slate-400">Interviewer: <strong className="text-slate-200">{int.interviewer}</strong></span>
                      <button
                        onClick={() => onStartInterview(candidate)}
                        className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition"
                      >
                        Enter AI Interview Room
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* TAB 6: TIMELINE */}
          {activeTab === 'timeline' && (
            <div className="space-y-4">
              <div className="border-l-2 border-indigo-500/40 pl-4 space-y-6">
                {[
                  { time: '10:08 AM', actor: 'AI HR Agent', action: 'Confirmation Email Dispatched', desc: 'Google Meet invite delivered via n8n' },
                  { time: '10:07 AM', actor: 'AI HR Agent', action: 'Interview Scheduled', desc: 'Booked on Thursday 2:00 PM PST' },
                  { time: '10:05 AM', actor: 'ElevenLabs Voice AI', action: 'Outbound Call Completed', desc: 'Candidate expressed interest' },
                  { time: '09:30 AM', actor: 'AI Resume Parser', action: 'Screening Passed', desc: 'Score: 92/100 threshold met' }
                ].map((item, idx) => (
                  <div key={idx} className="relative group">
                    <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-indigo-500 ring-4 ring-slate-900" />
                    <p className="text-[11px] font-mono text-indigo-400">{item.time} • {item.actor}</p>
                    <p className="text-sm font-semibold text-white mt-0.5">{item.action}</p>
                    <p className="text-xs text-slate-400 mt-0.5">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
