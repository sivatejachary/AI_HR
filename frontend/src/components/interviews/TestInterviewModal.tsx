'use client';

import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { CandidateCodingWorkspace } from './CandidateCodingWorkspace';
import {
  X,
  Mic,
  Volume2,
  Bot,
  Play,
  Pause,
  CheckSquare,
  Sparkles,
  Send,
  Loader2,
  AlertCircle,
  Code,
  Monitor,
  Eye,
  SkipForward
} from 'lucide-react';

export function TestInterviewModal({ onClose }: { onClose: () => void }) {
  const [loading, setLoading] = useState<boolean>(true);
  const [sessionData, setSessionData] = useState<any>(null);
  const [currentQuestion, setCurrentQuestion] = useState<any>(null);
  const [candidateAnswer, setCandidateAnswer] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [agentStatus, setAgentStatus] = useState<string>('SPEAKING'); // SPEAKING | LISTENING | THINKING | PAUSED | COMPLETED
  const [logs, setLogs] = useState<Array<{ time: string; text: string; role: 'agent' | 'user' | 'system' }>>([]);
  
  // Phase 4 Coding & Screen Share State
  const [codingActive, setCodingActive] = useState<boolean>(false);
  const [codingSessionData, setCodingSessionData] = useState<any>(null);
  const [screenShareActive, setScreenShareActive] = useState<boolean>(false);
  const [latestObservation, setLatestObservation] = useState<any>(null);

  const initTestSession = async () => {
    setLoading(true);
    try {
      const data = await api.startTestAIInterview();
      setSessionData(data);
      
      const session_id = data.interview_id;
      setLogs([
        { time: new Date().toLocaleTimeString(), text: `Initialized ElevenLabs Agent: ${data.elevenlabs_session?.agent_id || 'AI Technical Interviewer'}`, role: 'system' },
        { time: new Date().toLocaleTimeString(), text: `Runtime Context Loaded for ${data.candidate.name} (${data.job.title})`, role: 'system' },
        { time: new Date().toLocaleTimeString(), text: data.elevenlabs_session?.first_message || "Hi Rahul, thanks for joining. Let's start with a live technical challenge!", role: 'agent' }
      ]);

      // Fetch first question from Brain Engine
      const qRes = await api.getAINextQuestion(session_id);
      if (qRes && qRes.question) {
        setCurrentQuestion(qRes);
      }
    } catch (err) {
      console.error('Failed to init test session:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    initTestSession();
  }, []);

  const handleStartCoding = async () => {
    if (!sessionData) return;
    try {
      const res = await fetch(`http://localhost:8000/api/interviews/${sessionData.interview_id}/coding/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: 'python' })
      });
      const data = await res.json();
      setCodingSessionData(data);
      setCodingActive(true);
      setLogs(prev => [
        ...prev,
        { time: new Date().toLocaleTimeString(), text: `AI: "Let's do a practical coding problem: ${data.problem.title}. You will use our approved compiler."`, role: 'agent' },
        { time: new Date().toLocaleTimeString(), text: `Approved Online Platform: ${data.coding_platform} (${data.coding_url})`, role: 'system' }
      ]);
    } catch (err) {
      console.error('Failed to start coding session:', err);
    }
  };

  const handleToggleScreenShare = async (active: boolean) => {
    if (!sessionData) return;
    setScreenShareActive(active);
    try {
      await fetch(`http://localhost:8000/api/interviews/${sessionData.interview_id}/coding/screen-share`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: active ? 'start' : 'stop' })
      });
      setLogs(prev => [
        ...prev,
        { time: new Date().toLocaleTimeString(), text: active ? "Candidate explicitly authorized and started screen sharing." : "Candidate stopped screen sharing.", role: 'system' }
      ]);

      if (active) {
        // Send initial vision observation
        await handleSendVisionFrame("ONLINE_COMPILER", false);
      }
    } catch (err) {
      console.error('Failed to update screen share state:', err);
    }
  };

  const handleSendVisionFrame = async (screenType: string, errorVisible: boolean) => {
    if (!sessionData) return;
    try {
      const res = await fetch(`http://localhost:8000/api/interviews/${sessionData.interview_id}/coding/observations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          screen_type: screenType,
          language: 'PYTHON',
          code_visible: true,
          error_visible: errorVisible,
          output_visible: true,
          visible_error_text: errorVisible ? "IndexError: list index out of range at line 7" : null
        })
      });
      const data = await res.json();
      setLatestObservation(data.observation);
      setLogs(prev => [
        ...prev,
        {
          time: new Date().toLocaleTimeString(),
          text: `Vision AI Frame Analyzed: ${data.observation.screen_type} (Code Visible: ${data.observation.code_visible}, Error: ${data.observation.error_visible})`,
          role: 'system'
        }
      ]);

      if (errorVisible) {
        setLogs(prev => [
          ...prev,
          { time: new Date().toLocaleTimeString(), text: `AI: "I can see an IndexError in your code on line 7. What do you think is causing it?"`, role: 'agent' }
        ]);
      }
    } catch (err) {
      console.error('Failed to send vision frame:', err);
    }
  };

  const handleSkipQuestion = async () => {
    if (!sessionData) return;
    try {
      const res = await fetch(`http://localhost:8000/api/interviews/${sessionData.interview_id}/questions/skip`, {
        method: 'POST'
      });
      const data = await res.json();
      setLogs(prev => [
        ...prev,
        { time: new Date().toLocaleTimeString(), text: `HR skipped current question. Advanced to stage: ${data.current_stage}`, role: 'system' }
      ]);

      const nextQ = await api.getAINextQuestion(sessionData.interview_id);
      if (nextQ && nextQ.question) {
        setCurrentQuestion(nextQ);
      }
    } catch (err) {
      console.error('Failed to skip question:', err);
    }
  };

  const handleSubmitAnswer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!candidateAnswer.trim() || !sessionData || !currentQuestion || isSubmitting) return;

    const interview_id = sessionData.interview_id;
    const answerText = candidateAnswer;
    setCandidateAnswer('');
    setIsSubmitting(true);
    setAgentStatus('THINKING');

    setLogs(prev => [
      ...prev,
      { time: new Date().toLocaleTimeString(), text: answerText, role: 'user' }
    ]);

    try {
      const res = await api.submitAIAnswer(interview_id, currentQuestion.question_id || 'Q-1', answerText);
      
      setLogs(prev => [
        ...prev,
        { time: new Date().toLocaleTimeString(), text: `Answer Analyzed: Quality ${Math.round((res.answer_quality || 0.8) * 100)}% • Next Action: ${res.next_action}`, role: 'system' }
      ]);

      if (res.next_action === 'END_INTERVIEW' || res.next_action === 'COMPLETE') {
        setAgentStatus('COMPLETED');
        setLogs(prev => [
          ...prev,
          { time: new Date().toLocaleTimeString(), text: "Thank you for your time, Rahul. That concludes the interview. Have a great day!", role: 'agent' }
        ]);
      } else {
        const nextQ = await api.getAINextQuestion(interview_id);
        if (nextQ && nextQ.question) {
          setCurrentQuestion(nextQ);
          setAgentStatus('SPEAKING');
          setLogs(prev => [
            ...prev,
            { time: new Date().toLocaleTimeString(), text: nextQ.question, role: 'agent' }
          ]);
        }
      }
    } catch (err) {
      console.error('Error submitting answer:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePause = async () => {
    if (!sessionData) return;
    try {
      await api.pauseAIInterview(sessionData.interview_id);
      setAgentStatus('PAUSED');
      setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), text: 'HR Paused AI Interview Session', role: 'system' }]);
    } catch (err) {
      console.error('Pause failed:', err);
    }
  };

  const handleResume = async () => {
    if (!sessionData) return;
    try {
      await api.resumeAIInterview(sessionData.interview_id);
      setAgentStatus('SPEAKING');
      setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), text: 'HR Resumed AI Interview Session', role: 'system' }]);
    } catch (err) {
      console.error('Resume failed:', err);
    }
  };

  const handleComplete = async () => {
    if (!sessionData) return;
    try {
      await api.completeAIInterview(sessionData.interview_id);
      setAgentStatus('COMPLETED');
      setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), text: 'HR Completed Interview Session', role: 'system' }]);
    } catch (err) {
      console.error('Complete failed:', err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white border border-gray-200 w-full max-w-4xl rounded-xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="p-5 border-b border-gray-200 bg-gray-50/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-900 flex items-center justify-center text-white shadow-xs">
              <Bot size={20} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-semibold text-gray-900">Developer Test Mode: Phase 4 AI Technical Interviewer</h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-900 border border-purple-200">
                  Online Coding + Screen Vision
                </span>
              </div>
              <p className="text-xs text-gray-500">Live test environment for online compiler URLs, screen share authorization, and Vision AI</p>
            </div>
          </div>

          <button onClick={onClose} className="p-1.5 text-gray-400 hover:text-gray-700 rounded-lg hover:bg-gray-100 transition">
            <X size={20} />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 flex-1 overflow-y-auto max-h-[80vh]">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3">
              <Loader2 className="animate-spin text-blue-900" size={36} />
              <p className="text-xs text-gray-600 font-medium">Initializing Phase 4 Technical Interview Engine...</p>
            </div>
          ) : sessionData ? (
            <>
              {/* Voice Agent Visualizer Bar */}
              <div className="p-4 rounded-xl border bg-gradient-to-r from-blue-900 via-slate-900 to-indigo-950 text-white shadow-md flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center border-2 ${
                    agentStatus === 'SPEAKING'
                      ? 'bg-blue-600 border-blue-400 animate-pulse text-white'
                      : agentStatus === 'PAUSED'
                      ? 'bg-amber-600 border-amber-400 text-white'
                      : 'bg-slate-800 border-slate-700 text-gray-400'
                  }`}>
                    {agentStatus === 'SPEAKING' ? <Volume2 size={24} /> : <Bot size={24} />}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-semibold">Sarah Jenkins (AI Technical Interviewer)</h4>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        agentStatus === 'SPEAKING' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-slate-800 text-gray-300 border border-slate-700'
                      }`}>
                        {agentStatus}
                      </span>
                    </div>
                    <p className="text-xs text-gray-300 mt-0.5">
                      Candidate: <strong className="text-white">{sessionData.candidate.name}</strong> • Role: <strong className="text-white">{sessionData.job.title}</strong>
                    </p>
                  </div>
                </div>

                {/* Control Action Buttons */}
                <div className="flex items-center gap-2">
                  {!codingActive && (
                    <button
                      onClick={handleStartCoding}
                      className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition shadow-xs"
                    >
                      <Code size={14} /> Start Coding Problem
                    </button>
                  )}

                  <button
                    onClick={handleSkipQuestion}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition"
                  >
                    <SkipForward size={14} /> Skip Question
                  </button>

                  {agentStatus === 'PAUSED' ? (
                    <button
                      onClick={handleResume}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition"
                    >
                      <Play size={14} /> Resume AI
                    </button>
                  ) : (
                    <button
                      onClick={handlePause}
                      disabled={agentStatus === 'COMPLETED'}
                      className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50"
                    >
                      <Pause size={14} /> Pause AI
                    </button>
                  )}
                </div>
              </div>

              {/* Candidate Coding Workspace Section */}
              {codingActive && codingSessionData && (
                <div className="space-y-3 border-t border-b border-gray-200 py-4">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-gray-800 uppercase tracking-wider flex items-center gap-1.5">
                      <Code className="w-4 h-4 text-blue-900" /> Candidate Coding Challenge View
                    </span>

                    {/* Developer Vision Testing Buttons */}
                    <div className="flex items-center gap-2">
                      <span className="text-gray-500 font-mono text-[11px]">Simulate Vision Frame:</span>
                      <button
                        onClick={() => handleSendVisionFrame("ONLINE_COMPILER", false)}
                        className="px-2 py-1 bg-slate-100 hover:bg-slate-200 border text-[11px] rounded text-slate-700 flex items-center gap-1"
                      >
                        <Eye size={12} /> Normal Editor
                      </button>
                      <button
                        onClick={() => handleSendVisionFrame("ONLINE_COMPILER", true)}
                        className="px-2 py-1 bg-rose-50 hover:bg-rose-100 border border-rose-200 text-[11px] rounded text-rose-700 flex items-center gap-1 font-semibold"
                      >
                        <AlertCircle size={12} /> Runtime Error
                      </button>
                    </div>
                  </div>

                  <CandidateCodingWorkspace
                    interviewId={sessionData.interview_id}
                    problem={codingSessionData.problem}
                    codingPlatform={codingSessionData.coding_platform}
                    codingUrl={codingSessionData.coding_url}
                    screenShareActive={screenShareActive}
                    onToggleScreenShare={handleToggleScreenShare}
                    onFinishCoding={async () => {
                      await fetch(`http://localhost:8000/api/interviews/${sessionData.interview_id}/coding/finish`, { method: "POST" });
                      setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), text: "Candidate finished coding. Transitioned to CODE_REVIEW stage.", role: "system" }]);
                      setCodingActive(false);
                    }}
                  />
                </div>
              )}

              {/* Active Question Box */}
              {!codingActive && currentQuestion && agentStatus !== 'COMPLETED' && (
                <div className="p-4 bg-blue-50/60 border border-blue-200 rounded-xl space-y-2">
                  <div className="flex items-center justify-between text-xs text-blue-900 font-semibold">
                    <span className="flex items-center gap-1.5">
                      <Sparkles size={14} className="text-blue-900" /> Current Question #{currentQuestion.question_number || 1} [{currentQuestion.stage || 'TECHNICAL'}]
                    </span>
                    <span className="bg-blue-100 text-blue-900 px-2 py-0.5 rounded text-[10px] uppercase font-mono font-bold">
                      Difficulty: {currentQuestion.difficulty || 'MEDIUM'}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-gray-900 leading-relaxed">
                    "{currentQuestion.question}"
                  </p>
                </div>
              )}

              {/* Conversation Log Feed */}
              <div className="space-y-2">
                <h5 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Live Interview Transcript & Vision Event Log</h5>
                <div className="p-4 bg-slate-900 border border-slate-800 text-slate-200 rounded-xl max-h-56 overflow-y-auto space-y-3 font-sans text-xs">
                  {logs.map((log, idx) => (
                    <div
                      key={idx}
                      className={`flex gap-2.5 ${
                        log.role === 'agent'
                          ? 'text-cyan-300 font-medium'
                          : log.role === 'user'
                          ? 'text-emerald-300 font-semibold pl-4 border-l-2 border-emerald-500'
                          : 'text-slate-400 text-[11px] font-mono italic'
                      }`}
                    >
                      <span className="text-[10px] text-slate-500 font-mono shrink-0">{log.time}</span>
                      <div>
                        {log.role === 'agent' && <span className="text-cyan-400 font-bold mr-1.5">[AI Interviewer]:</span>}
                        {log.role === 'user' && <span className="text-emerald-400 font-bold mr-1.5">[Candidate]:</span>}
                        {log.role === 'system' && <span className="text-purple-400 font-bold mr-1.5">[Vision/System]:</span>}
                        <span>{log.text}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Candidate Input Simulator */}
              {agentStatus !== 'COMPLETED' && (
                <form onSubmit={handleSubmitAnswer} className="flex gap-2">
                  <input
                    type="text"
                    value={candidateAnswer}
                    onChange={(e) => setCandidateAnswer(e.target.value)}
                    placeholder="Type candidate spoken response to test AI Brain..."
                    className="flex-1 px-4 py-2.5 text-xs border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-900/20 focus:border-blue-900"
                    disabled={isSubmitting || agentStatus === 'PAUSED'}
                  />
                  <button
                    type="submit"
                    disabled={!candidateAnswer.trim() || isSubmitting || agentStatus === 'PAUSED'}
                    className="px-5 py-2.5 bg-blue-900 hover:bg-blue-800 text-white rounded-xl text-xs font-semibold flex items-center gap-2 transition disabled:opacity-50"
                  >
                    {isSubmitting ? <Loader2 className="animate-spin" size={14} /> : <Send size={14} />} Speak Answer
                  </button>
                </form>
              )}
            </>
          ) : (
            <div className="text-center py-10 text-xs text-gray-500">
              <AlertCircle size={24} className="mx-auto text-gray-400 mb-2" />
              <p>Failed to initialize developer test session.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

