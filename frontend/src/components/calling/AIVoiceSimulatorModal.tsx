'use client';

import React, { useState, useEffect } from 'react';
import { Candidate } from '../../types';
import {
  X,
  Phone,
  PhoneCall,
  PhoneOff,
  Mic,
  MicOff,
  Volume2,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Sparkles,
  Bot,
  User,
  Zap,
  ArrowRight
} from 'lucide-react';

export function AIVoiceSimulatorModal({
  candidate,
  onClose,
  onCompleteCall
}: {
  candidate: Candidate;
  onClose: () => void;
  onCompleteCall: (candidateId: string, result: 'COMPLETED' | 'CALLBACK' | 'NOT_INTERESTED', summary: string, transcript: any[]) => void;
}) {
  const [callState, setCallState] = useState<'DIALING' | 'CONNECTED' | 'ENDED'>('DIALING');
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [transcript, setTranscript] = useState<Array<{ aiText: string; candidateText: string; time: string }>>([]);
  const [callDuration, setCallDuration] = useState(0);
  const [candidateResponse, setCandidateResponse] = useState<'INTERESTED' | 'CALLBACK' | 'NOT_INTERESTED' | null>(null);

  const callSteps = [
    {
      aiText: `Hello ${candidate.name}! This is Rachel calling from TechCorp Global HR. Am I speaking with ${candidate.name}?`,
      candidateText: "Yes, this is Pavan speaking. How can I help you?",
      time: "0:04"
    },
    {
      aiText: `Awesome! I'm reaching out regarding your application for the ${candidate.jobTitle} position. We reviewed your profile and were very impressed with your backend experience. Do you have 3 minutes to discuss the role?`,
      candidateText: "Yes, absolutely! I'm very interested in learning more about the tech stack and team.",
      time: "0:22"
    },
    {
      aiText: `Fantastic. Per our company hiring policy, I want to quickly confirm: Are you currently serving a notice period, and is your expected salary within the $140,000 - $175,000 range?`,
      candidateText: "My notice period is 30 days, and that salary range aligns perfectly with my expectations.",
      time: "0:45"
    },
    {
      aiText: `Great news! Our AI Technical Evaluator has an open slot for a technical interview this Thursday at 2:00 PM PST. Would that time work for you?`,
      candidateText: "Thursday at 2 PM PST works great for me!",
      time: "1:10"
    },
    {
      aiText: `Perfect! I have scheduled the interview and triggered our n8n calendar service to dispatch a Google Meet invitation to ${candidate.email}. Have a wonderful day!`,
      candidateText: "Thank you so much! Looking forward to the interview.",
      time: "1:35"
    }
  ];

  useEffect(() => {
    let timer: any;
    if (callState === 'CONNECTED') {
      timer = setInterval(() => {
        setCallDuration(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [callState]);

  useEffect(() => {
    // Dialing phase simulator
    const timeout = setTimeout(() => {
      setCallState('CONNECTED');
      // Add first conversation line
      setTranscript([callSteps[0]]);
    }, 2000);
    return () => clearTimeout(timeout);
  }, []);

  const handleNextDialogue = () => {
    if (currentStepIndex + 1 < callSteps.length) {
      const nextIdx = currentStepIndex + 1;
      setCurrentStepIndex(nextIdx);
      setTranscript(prev => [...prev, callSteps[nextIdx]]);
    } else {
      // Finished call steps
      handleEndCall('INTERESTED');
    }
  };

  const handleEndCall = (result: 'INTERESTED' | 'CALLBACK' | 'NOT_INTERESTED') => {
    setCallState('ENDED');
    setCandidateResponse(result);
    const summaryText = result === 'INTERESTED'
      ? `Candidate confirmed identity, expressed strong interest in ${candidate.jobTitle}, verified 30-day notice period and salary fit ($160k). Agreed to technical interview on Thursday 2:00 PM PST.`
      : result === 'CALLBACK'
      ? `Candidate requested callback from HR Manager to negotiate custom relocation terms.`
      : `Candidate declined opportunity due to existing job offer.`;

    setTimeout(() => {
      onCompleteCall(candidate.id, result === 'INTERESTED' ? 'COMPLETED' : result, summaryText, transcript);
      onClose();
    }, 1500);
  };

  const formatSeconds = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const remainder = sec % 60;
    return `${mins.toString().padStart(2, '0')}:${remainder.toString().padStart(2, '0')}`;
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-500/20">
              <Bot size={20} />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                ElevenLabs Voice AI Agent
                <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  n8n Integrated
                </span>
              </h3>
              <p className="text-xs text-slate-400">Outbound Call • Software Engineer Workflow v1</p>
            </div>
          </div>

          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition">
            <X size={20} />
          </button>
        </div>

        {/* Call Visualizer Area */}
        <div className="p-8 bg-gradient-to-b from-slate-900 via-slate-950 to-slate-900 flex flex-col items-center justify-center text-center space-y-6">
          {/* Avatar Ring */}
          <div className="relative">
            <div className={`w-28 h-28 rounded-full border-4 flex items-center justify-center transition-all ${
              callState === 'DIALING'
                ? 'border-indigo-500/40 animate-pulse bg-indigo-950/40 text-indigo-300'
                : callState === 'CONNECTED'
                ? 'border-emerald-500 bg-emerald-950/30 text-emerald-400 shadow-xl shadow-emerald-500/20'
                : 'border-slate-700 bg-slate-800 text-slate-500'
            }`}>
              <User size={48} />
            </div>

            {callState === 'CONNECTED' && (
              <span className="absolute -top-1 -right-1 flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-4 w-4 bg-emerald-500" />
              </span>
            )}
          </div>

          {/* Candidate Name & Dialing Status */}
          <div className="space-y-1">
            <h4 className="text-xl font-bold text-white">{candidate.name}</h4>
            <p className="text-xs text-slate-400 font-mono">{candidate.phone}</p>
            <p className="text-xs font-semibold text-indigo-400 mt-2 flex items-center justify-center gap-1.5">
              {callState === 'DIALING' && (
                <>
                  <RefreshCw size={14} className="animate-spin text-indigo-400" /> Dialing Candidate via Twilio...
                </>
              )}
              {callState === 'CONNECTED' && (
                <>
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" /> Connected • {formatSeconds(callDuration)}
                </>
              )}
              {callState === 'ENDED' && 'Call Terminated • Syncing state to n8n...'}
            </p>
          </div>

          {/* Audio Waveform Animation */}
          {callState === 'CONNECTED' && (
            <div className="flex items-center gap-1.5 h-8 px-6 py-2 bg-slate-900/80 rounded-full border border-slate-800">
              {[40, 70, 30, 90, 50, 80, 40, 100, 60, 30, 85, 45].map((h, i) => (
                <div
                  key={i}
                  className="w-1 bg-indigo-500 rounded-full animate-pulse"
                  style={{ height: `${h}%`, animationDelay: `${i * 0.1}s` }}
                />
              ))}
            </div>
          )}
        </div>

        {/* Live Transcript Stream */}
        <div className="p-6 bg-slate-950 border-t border-slate-800 space-y-3 max-h-52 overflow-y-auto">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Live Voice Transcript</span>
            <span className="text-[10px] text-indigo-400 font-normal">ElevenLabs Realtime STT/TTS</span>
          </p>
          <div className="space-y-3">
            {transcript.map((item, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex items-start gap-2">
                  <span className="text-xs font-bold text-indigo-400 shrink-0">AI HR:</span>
                  <p className="text-xs text-indigo-200 bg-indigo-950/60 p-2.5 rounded-xl border border-indigo-900/50">
                    {item.aiText}
                  </p>
                </div>
                <div className="flex items-start gap-2 pl-4">
                  <span className="text-xs font-bold text-emerald-400 shrink-0">Candidate:</span>
                  <p className="text-xs text-emerald-200 bg-emerald-950/60 p-2.5 rounded-xl border border-emerald-900/50">
                    {item.candidateText}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Call Controls Footer */}
        <div className="p-4 bg-slate-900 border-t border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleEndCall('CALLBACK')}
              disabled={callState !== 'CONNECTED'}
              className="px-3 py-2 bg-amber-600/20 text-amber-300 border border-amber-500/40 rounded-xl text-xs font-semibold hover:bg-amber-600/30 disabled:opacity-50 transition"
            >
              Request Callback
            </button>
            <button
              onClick={() => handleEndCall('NOT_INTERESTED')}
              disabled={callState !== 'CONNECTED'}
              className="px-3 py-2 bg-rose-600/20 text-rose-300 border border-rose-500/40 rounded-xl text-xs font-semibold hover:bg-rose-600/30 disabled:opacity-50 transition"
            >
              Not Interested
            </button>
          </div>

          <div className="flex items-center gap-3">
            {callState === 'CONNECTED' && currentStepIndex < callSteps.length - 1 && (
              <button
                onClick={handleNextDialogue}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition shadow-lg shadow-indigo-600/30"
              >
                Next Dialogue Step <ArrowRight size={14} />
              </button>
            )}

            <button
              onClick={() => handleEndCall('INTERESTED')}
              disabled={callState === 'ENDED'}
              className="px-5 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold flex items-center gap-2 transition shadow-lg shadow-rose-600/30"
            >
              <PhoneOff size={16} /> End Call & Sync Stage
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
