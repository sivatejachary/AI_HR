'use client';

import React, { useState, useEffect } from 'react';
import { Interview, InterviewSessionDetails } from '../../types';
import { api } from '../../lib/api';
import {
  X,
  Bot,
  CheckCircle2,
  Clock,
  MessageSquare,
  Award,
  Loader2,
  AlertCircle,
  ExternalLink,
  Play,
  Pause,
  CheckSquare,
  UserCheck
} from 'lucide-react';

export function InterviewSessionDrawer({
  interview,
  onClose,
  onApproveSuccess
}: {
  interview: Interview;
  onClose: () => void;
  onApproveSuccess?: () => void;
}) {
  const [session, setSession] = useState<InterviewSessionDetails | null>(null);
  const [meetingInfo, setMeetingInfo] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isActionLoading, setIsActionLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'MONITOR' | 'EVALUATION'>('MONITOR');
  const [evaluationData, setEvaluationData] = useState<any>(null);
  const [selectedDecision, setSelectedDecision] = useState<string>('MOVE_TO_NEXT_STAGE');
  const [decisionReason, setDecisionReason] = useState<string>('');
  const [decisionSuccess, setDecisionSuccess] = useState<string | null>(null);

  const STAGES_TIMELINE = [
    { key: 'INTRODUCTION', label: 'Introduction' },
    { key: 'RESUME_DISCUSSION', label: 'Resume Discussion' },
    { key: 'TECHNICAL_INTERVIEW', label: 'Technical Interview' },
    { key: 'BEHAVIORAL', label: 'Behavioral' },
    { key: 'CANDIDATE_QUESTIONS', label: 'Candidate Q&A' },
    { key: 'CLOSING', label: 'Closing' },
    { key: 'EVALUATION', label: 'Evaluation' }
  ];

  const fetchSession = async () => {
    setIsLoading(true);
    try {
      const startRes = await api.startInterviewSession(interview.candidateId, interview.jobId, interview.id);
      if (startRes && (startRes.session_id || startRes.interview_id)) {
        const sessId = startRes.session_id || startRes.interview_id;
        const details = await api.getInterviewSession(sessId);
        setSession(details);
      }
    } catch (err) {
      console.warn('Failed to load session details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchMeetingStatus = async () => {
    try {
      const st = await api.getMeetingStatus(interview.id);
      if (st && st.meeting_status) {
        setMeetingInfo(st);
      }
    } catch (err) {
      console.warn('Meeting status offline:', err);
    }
  };

  const fetchEvaluation = async () => {
    try {
      const ev = await api.getEvaluation(interview.id);
      if (ev && ev.evaluation_id) {
        setEvaluationData(ev);
      }
    } catch (err) {
      console.warn('Evaluation not ready yet:', err);
    }
  };

  useEffect(() => {
    fetchSession();
    fetchMeetingStatus();
    fetchEvaluation();
  }, [interview.id]);

  const handleHRDecisionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!decisionReason.trim()) return;
    setIsActionLoading(true);
    try {
      const res = await api.submitHRDecision(interview.id, selectedDecision, decisionReason);
      setDecisionSuccess(`HR Decision recorded: ${selectedDecision}. Workflow advanced.`);
      fetchEvaluation();
      if (onApproveSuccess) onApproveSuccess();
    } catch (err) {
      console.error('Failed to submit HR decision:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleConnectMeeting = async () => {
    setIsActionLoading(true);
    try {
      const res = await api.connectMeetingBot(interview.id);
      if (res) setMeetingInfo(res);
    } catch (err) {
      console.error('Failed to connect meeting bot:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleDisconnectMeeting = async () => {
    setIsActionLoading(true);
    try {
      const res = await api.disconnectMeetingBot(interview.id);
      if (res) setMeetingInfo(res);
    } catch (err) {
      console.error('Failed to disconnect meeting bot:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handlePause = async () => {
    if (!session) return;
    setIsActionLoading(true);
    try {
      await api.pauseAIInterview(session.id);
      const updated = await api.getInterviewSession(session.id);
      setSession(updated);
    } catch (err) {
      console.error('Pause failed:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleResume = async () => {
    if (!session) return;
    setIsActionLoading(true);
    try {
      await api.resumeAIInterview(session.id);
      const updated = await api.getInterviewSession(session.id);
      setSession(updated);
    } catch (err) {
      console.error('Resume failed:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleComplete = async () => {
    if (!session) return;
    setIsActionLoading(true);
    try {
      await api.completeAIInterview(session.id);
      const updated = await api.getInterviewSession(session.id);
      setSession(updated);
      if (onApproveSuccess) onApproveSuccess();
    } catch (err) {
      console.error('Complete failed:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const currentStage = session?.currentStage || 'TECHNICAL_INTERVIEW';
  const brainStatus = session?.brainStatus || 'IDLE';

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex justify-end">
      <div className="bg-white border-l border-gray-200 w-full max-w-2xl h-full flex flex-col shadow-2xl overflow-hidden animate-in slide-in-from-right duration-200">
        {/* Drawer Header */}
        <div className="p-6 border-b border-gray-200 flex items-center justify-between bg-gray-50/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-900 flex items-center justify-center text-white shadow-xs">
              <Bot size={20} />
            </div>
            <div>
              <h3 className="text-base font-semibold text-gray-900">AI Interview Session Monitor</h3>
              <p className="text-xs text-gray-500">Candidate: <strong className="text-gray-800">{interview.candidateName}</strong> • {interview.jobTitle}</p>
            </div>
          </div>

          <button onClick={onClose} className="p-1.5 text-gray-400 hover:text-gray-700 rounded-lg hover:bg-gray-100 transition">
            <X size={20} />
          </button>
        </div>

        {/* Meeting Details & HR Controls Bar */}
        <div className="px-6 py-3 bg-blue-50/60 border-b border-blue-100 flex items-center justify-between text-xs text-blue-900">
          <span className="font-medium flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${session?.status === 'PAUSED' ? 'bg-amber-500' : 'bg-emerald-500 animate-pulse'}`} />
            Platform: <strong>{interview.platform}</strong> ({interview.date} at {interview.time})
          </span>

          <div className="flex items-center gap-2">
            {meetingInfo?.meeting_status === 'INTERVIEW_ACTIVE' || meetingInfo?.meeting_status === 'CONNECTED' ? (
              <button
                onClick={handleDisconnectMeeting}
                disabled={isActionLoading}
                className="px-3 py-1 bg-rose-700 hover:bg-rose-600 text-white rounded text-[11px] font-semibold flex items-center gap-1 transition"
              >
                Disconnect Bot
              </button>
            ) : (
              <button
                onClick={handleConnectMeeting}
                disabled={isActionLoading}
                className="px-3 py-1 bg-indigo-900 hover:bg-indigo-800 text-white rounded text-[11px] font-semibold flex items-center gap-1 transition shadow-2xs"
              >
                Connect Meeting Bot
              </button>
            )}

            {session?.status === 'PAUSED' ? (
              <button
                onClick={handleResume}
                disabled={isActionLoading}
                className="px-3 py-1 bg-emerald-700 hover:bg-emerald-600 text-white rounded text-[11px] font-semibold flex items-center gap-1 transition"
              >
                <Play size={12} /> Resume AI
              </button>
            ) : (
              <button
                onClick={handlePause}
                disabled={isActionLoading || session?.status === 'COMPLETED'}
                className="px-3 py-1 bg-amber-600 hover:bg-amber-500 text-white rounded text-[11px] font-semibold flex items-center gap-1 transition disabled:opacity-50"
              >
                <Pause size={12} /> Pause AI
              </button>
            )}

            <button
              onClick={async () => {
                if (!session) return;
                setIsActionLoading(true);
                try {
                  await fetch(`http://localhost:8000/api/interviews/${session.id}/questions/skip`, { method: "POST" });
                  const updated = await api.getInterviewSession(session.id);
                  setSession(updated);
                } catch (err) {
                  console.error('Skip failed:', err);
                } finally {
                  setIsActionLoading(false);
                }
              }}
              disabled={isActionLoading || session?.status === 'COMPLETED'}
              className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-100 rounded text-[11px] font-semibold flex items-center gap-1 transition disabled:opacity-50"
            >
              Skip Question
            </button>

            <button
              onClick={handleComplete}
              disabled={isActionLoading || session?.status === 'COMPLETED'}
              className="px-3 py-1 bg-blue-900 hover:bg-blue-800 text-white rounded text-[11px] font-semibold flex items-center gap-1 transition disabled:opacity-50"
            >
              <CheckSquare size={12} /> Complete
            </button>
          </div>
        </div>

        {/* Tab Navigation Header */}
        <div className="flex border-b border-gray-200 bg-gray-100/70 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('MONITOR')}
            className={`flex-1 py-2.5 px-4 text-center border-b-2 transition ${
              activeTab === 'MONITOR'
                ? 'border-blue-900 text-blue-900 bg-white font-bold'
                : 'border-transparent text-gray-500 hover:text-gray-800'
            }`}
          >
            Monitor & Live Session
          </button>
          <button
            onClick={() => {
              setActiveTab('EVALUATION');
              if (!evaluationData) fetchEvaluation();
            }}
            className={`flex-1 py-2.5 px-4 text-center border-b-2 transition flex items-center justify-center gap-1.5 ${
              activeTab === 'EVALUATION'
                ? 'border-blue-900 text-blue-900 bg-white font-bold'
                : 'border-transparent text-gray-500 hover:text-gray-800'
            }`}
          >
            <Award size={14} className="text-purple-700" />
            AI Evaluation & HR Review
            {evaluationData && (
              <span className="ml-1 px-1.5 py-0.2 rounded text-[10px] bg-purple-100 text-purple-900 font-mono">
                {evaluationData.confidence ? `${Math.round(evaluationData.confidence * 100)}%` : 'Ready'}
              </span>
            )}
          </button>
        </div>

        {/* Drawer Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 text-gray-400 gap-3">
              <Loader2 className="animate-spin text-blue-900" size={32} />
              <p className="text-xs">Connecting to AI Interview Brain Engine...</p>
            </div>
          ) : activeTab === 'EVALUATION' ? (
            /* Phase 5 AI Evaluation & HR Review View */
            <div className="space-y-6">
              {evaluationData ? (
                <>
                  {/* Executive Summary Card */}
                  <div className="p-5 bg-gradient-to-r from-purple-950 via-slate-900 to-indigo-950 text-white rounded-xl shadow-md space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Award className="w-5 h-5 text-purple-400" />
                        <h4 className="text-sm font-bold text-white uppercase tracking-wider">AI Evaluation Executive Summary</h4>
                      </div>
                      <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                        Confidence: {Math.round((evaluationData.confidence || 0.85) * 100)}% ({evaluationData.evaluation_version || 'v1.0'})
                      </span>
                    </div>
                    <p className="text-xs text-slate-200 leading-relaxed font-sans bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                      "{evaluationData.overall_summary}"
                    </p>
                  </div>

                  {/* Competency Evaluation (1-5 Scale) */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider">Competency Evaluation (1-5 Scale)</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {evaluationData.competencies?.map((c: any, idx: number) => (
                        <div key={idx} className="p-3.5 bg-white border border-gray-200 rounded-lg text-xs space-y-1.5 shadow-2xs">
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-gray-900">{c.competency_name}</span>
                            <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-purple-50 text-purple-900 border border-purple-200">
                              {c.score} / 5
                            </span>
                          </div>
                          <p className="text-[11px] text-gray-600 leading-normal">{c.evidence}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* JD Requirements Alignment */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider">Job Description Requirements Alignment</h4>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
                      {evaluationData.jd_alignment?.map((j: any, idx: number) => {
                        const isDem = j.status === 'DEMONSTRATED';
                        const isPart = j.status === 'PARTIALLY_DEMONSTRATED';
                        const isUntested = j.status === 'NOT_TESTED';
                        return (
                          <div
                            key={idx}
                            className={`p-2.5 rounded-lg border flex flex-col justify-between ${
                              isDem
                                ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900'
                                : isPart
                                ? 'bg-amber-50/70 border-amber-200 text-amber-900'
                                : isUntested
                                ? 'bg-slate-50 border-slate-200 text-slate-600'
                                : 'bg-rose-50/70 border-rose-200 text-rose-900'
                            }`}
                          >
                            <span className="font-bold text-[11px]">{j.requirement_name}</span>
                            <span className="text-[10px] font-mono font-semibold uppercase mt-1">
                              {isDem ? '✓ Demonstrated' : isPart ? '◐ Partially' : isUntested ? '? Not Tested' : '✗ Missing'}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Resume Project Verification */}
                  {evaluationData.project_verification && evaluationData.project_verification.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider">Resume Project Verification</h4>
                      <div className="space-y-2">
                        {evaluationData.project_verification.map((p: any, idx: number) => (
                          <div key={idx} className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-xs space-y-1">
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-blue-950">{p.project_name}</span>
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-900 border">
                                {p.verification_status}
                              </span>
                            </div>
                            <p className="text-[11px] text-gray-700 italic">Claim: "{p.resume_claim}"</p>
                            <p className="text-[11px] text-gray-600">Evidence: {p.interview_evidence}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* HR Decision Form Card */}
                  <div className="p-5 bg-white border-2 border-blue-900 rounded-xl space-y-4 shadow-md">
                    <h4 className="text-xs font-bold text-blue-900 uppercase tracking-wider">Record Final HR Decision</h4>
                    
                    {decisionSuccess && (
                      <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 font-medium">
                        ✓ {decisionSuccess}
                      </div>
                    )}

                    <form onSubmit={handleHRDecisionSubmit} className="space-y-3 text-xs">
                      <div>
                        <label className="block font-semibold text-gray-700 mb-1">Select HR Hiring Action:</label>
                        <select
                          value={selectedDecision}
                          onChange={(e) => setSelectedDecision(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-900 focus:outline-none bg-white font-medium"
                        >
                          <option value="MOVE_TO_NEXT_STAGE">Move to Next Stage (Advance Workflow)</option>
                          <option value="ADVANCE_TO_OFFER">Advance to Offer Workflow</option>
                          <option value="REQUEST_HUMAN_REVIEW">Request Additional Human Review</option>
                          <option value="HOLD">Hold Application</option>
                          <option value="REJECT">Reject Candidate</option>
                        </select>
                      </div>

                      <div>
                        <label className="block font-semibold text-gray-700 mb-1">Decision Reason / Notes:</label>
                        <textarea
                          rows={3}
                          value={decisionReason}
                          onChange={(e) => setDecisionReason(e.target.value)}
                          placeholder="Provide rationale for HR review audit log..."
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-900 focus:outline-none"
                          required
                        />
                      </div>

                      <button
                        type="submit"
                        disabled={isActionLoading || !decisionReason.trim()}
                        className="w-full py-2.5 bg-blue-900 hover:bg-blue-800 text-white font-semibold rounded-lg shadow-xs transition disabled:opacity-50"
                      >
                        Submit HR Decision & Advance Workflow
                      </button>
                    </form>
                  </div>
                </>
              ) : (
                <div className="flex flex-col items-center justify-center py-16 text-center space-y-3">
                  <Loader2 className="animate-spin text-purple-700" size={32} />
                  <p className="text-xs text-gray-600 font-medium">Generating Evidence-Based AI Evaluation...</p>
                  <button
                    onClick={async () => {
                      await api.triggerEvaluation(interview.id);
                      fetchEvaluation();
                    }}
                    className="px-4 py-2 bg-purple-900 hover:bg-purple-800 text-white font-semibold text-xs rounded-lg transition shadow-xs"
                  >
                    Trigger Evaluation Now
                  </button>
                </div>
              )}
            </div>
          ) : session ? (
            <>
              {/* Session Status & Brain Status Cards */}
              <div className="p-4 rounded-lg border bg-white shadow-2xs space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Interview Session</span>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-gray-100 text-gray-700 border">
                      Brain: {brainStatus}
                    </span>
                    <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase border ${
                      session.status === 'COMPLETED' || session.hrApproved
                        ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                        : session.status === 'PAUSED'
                        ? 'bg-amber-50 text-amber-800 border-amber-200'
                        : 'bg-blue-50 text-blue-800 border-blue-200'
                    }`}>
                      {session.status}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 text-xs pt-1 border-t border-gray-100">
                  <div>
                    <span className="text-gray-400 text-[11px]">Current Stage:</span>
                    <p className="font-semibold text-blue-900">{session.currentStage}</p>
                  </div>
                  <div>
                    <span className="text-gray-400 text-[11px]">Difficulty Level:</span>
                    <p className="font-semibold text-gray-800 uppercase font-mono">{session.difficulty || 'MEDIUM'}</p>
                  </div>
                  <div>
                    <span className="text-gray-400 text-[11px]">Questions Asked:</span>
                    <p className="font-semibold text-gray-900">{session.currentQuestionIndex || session.questions.length}</p>
                  </div>
                </div>
              </div>

              {/* Phase 3: Real Meeting Platform Integration & Participant Roster Card */}
              {meetingInfo && (
                <div className="p-4 rounded-lg border bg-gradient-to-r from-slate-900 to-indigo-950 text-white shadow-sm space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                        Meeting Integration: {meetingInfo.meeting_provider || interview.platform}
                      </h4>
                    </div>

                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono border ${
                      meetingInfo.meeting_status === 'INTERVIEW_ACTIVE'
                        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                        : meetingInfo.meeting_status === 'WAITING_FOR_CANDIDATE'
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                        : 'bg-slate-800 text-slate-300 border-slate-700'
                    }`}>
                      {meetingInfo.meeting_status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs pt-2 border-t border-slate-800">
                    <div>
                      <span className="text-slate-400 text-[11px]">AI Bot Connection:</span>
                      <p className="font-semibold text-emerald-400">{meetingInfo.ai_connection_status}</p>
                    </div>
                    <div>
                      <span className="text-slate-400 text-[11px]">Candidate Presence:</span>
                      <p className="font-semibold text-slate-200">
                        {meetingInfo.has_candidate ? '✓ Candidate Joined' : '⏳ Waiting for Candidate'}
                      </p>
                    </div>
                  </div>

                  {meetingInfo.participants && meetingInfo.participants.length > 0 && (
                    <div className="space-y-1.5 pt-2 border-t border-slate-800 text-[11px]">
                      <span className="text-slate-400 font-medium">Meeting Roster ({meetingInfo.participants.length}):</span>
                      <div className="flex flex-wrap gap-1.5">
                        {meetingInfo.participants.map((p: any, i: number) => (
                          <span
                            key={i}
                            className={`px-2 py-0.5 rounded text-[10px] font-medium border ${
                              p.role === 'AI'
                                ? 'bg-purple-900/60 text-purple-200 border-purple-700'
                                : p.role === 'CANDIDATE'
                                ? 'bg-emerald-900/60 text-emerald-200 border-emerald-700'
                                : 'bg-slate-800 text-slate-300 border-slate-700'
                            }`}
                          >
                            {p.display_name} ({p.role})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Stage Progression Timeline */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Interview Stage Timeline</h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                  {STAGES_TIMELINE.map((s, idx) => {
                    const isCurrent = currentStage === s.key;
                    const isPast = STAGES_TIMELINE.findIndex(x => x.key === currentStage) > idx;
                    return (
                      <div
                        key={s.key}
                        className={`p-2 rounded border transition text-center font-medium ${
                          isCurrent
                            ? 'bg-blue-900 text-white border-blue-900 font-bold'
                            : isPast
                            ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                            : 'bg-gray-50 text-gray-400 border-gray-200'
                        }`}
                      >
                        {isPast ? '✓ ' : isCurrent ? '● ' : '○ '}{s.label}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Dynamic Questions Bank */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider flex items-center gap-1.5">
                  <MessageSquare size={14} className="text-blue-900" /> Dynamic Interview Questions ({session.questions.length})
                </h4>

                <div className="space-y-2.5">
                  {session.questions.map((q, idx) => (
                    <div key={q.id} className="p-3.5 bg-gray-50 border border-gray-200 rounded-lg text-xs space-y-2">
                      <div className="flex items-center justify-between text-[11px] font-semibold text-blue-900">
                        <span>Question #{idx + 1} [{q.category}]</span>
                        {q.candidateAnswer && (
                          <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 flex items-center gap-1">
                            <CheckCircle2 size={10} /> Answered
                          </span>
                        )}
                      </div>
                      <p className="text-gray-800 font-medium leading-relaxed">"{q.questionText}"</p>
                      {q.candidateAnswer && (
                        <div className="p-2.5 bg-white border border-gray-200 rounded text-gray-600 text-[11px] italic">
                          Answer: "{q.candidateAnswer}"
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* AI Evaluation Card */}
              {session.evaluation && (
                <div className="p-5 bg-purple-50/60 border border-purple-200 rounded-lg space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-purple-950 uppercase tracking-wider flex items-center gap-1.5">
                      <Award size={16} className="text-purple-700" /> AI Evaluation Breakdown
                    </h4>
                    <span className="text-xs font-mono font-bold px-2 py-0.5 bg-purple-100 text-purple-900 rounded">
                      Score: {session.evaluation.overall_score}%
                    </span>
                  </div>

                  <p className="text-xs text-gray-700 leading-relaxed bg-white p-3 rounded border border-purple-100">
                    {session.evaluation.summary}
                  </p>

                  <div className="space-y-1.5 text-xs text-gray-700">
                    <span className="font-semibold text-purple-950">Evaluation Evidence:</span>
                    <ul className="list-disc pl-4 space-y-1 text-gray-600 text-[11px]">
                      {session.evaluation.evidence.map((ev, i) => (
                        <li key={i}>{ev}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-10 text-xs text-gray-500 space-y-2">
              <AlertCircle size={24} className="mx-auto text-gray-400" />
              <p>No active AI interview session found for this candidate.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
