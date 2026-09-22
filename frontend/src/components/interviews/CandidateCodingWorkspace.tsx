"use client";

import React, { useState } from "react";
import {
  Code,
  ExternalLink,
  Video,
  Mic,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Play,
  Monitor
} from "lucide-react";

interface CandidateCodingWorkspaceProps {
  interviewId: string;
  problem: {
    id: string;
    title: string;
    description: string;
    difficulty: string;
    input_format?: string;
    output_format?: string;
    examples?: Array<{ input: string; output: string; explanation?: string }>;
    constraints?: string[];
    expected_complexity?: { time?: string; space?: string };
  };
  codingPlatform: string;
  codingUrl: string;
  screenShareActive: boolean;
  onToggleScreenShare?: (active: boolean) => void;
  onRequestHint?: () => void;
  onFinishCoding?: () => void;
}

export const CandidateCodingWorkspace: React.FC<CandidateCodingWorkspaceProps> = ({
  interviewId,
  problem,
  codingPlatform,
  codingUrl,
  screenShareActive,
  onToggleScreenShare,
  onRequestHint,
  onFinishCoding,
}) => {
  const [hintsGiven, setHintsGiven] = useState(0);
  const [currentHint, setCurrentHint] = useState<string | null>(null);

  const handleOpenCompiler = () => {
    window.open(codingUrl, "_blank", "noopener,noreferrer");
  };

  const handleHintClick = async () => {
    if (onRequestHint) {
      onRequestHint();
    } else {
      try {
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://ai-hrs.onrender.com';
        const res = await fetch(`${backendUrl}/api/interviews/${interviewId}/coding/hint`, {
          method: "POST"
        });
        const data = await res.json();
        if (data.hint) {
          setCurrentHint(data.hint);
          setHintsGiven(data.hints_given || hintsGiven + 1);
        }
      } catch (err) {
        console.error("Failed to request hint:", err);
      }
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-slate-100 space-y-6 shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
              TECHNICAL CODING CHALLENGE
            </span>
            <span
              className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
                problem.difficulty === "EASY"
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : problem.difficulty === "MEDIUM"
                  ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                  : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
              }`}
            >
              {problem.difficulty}
            </span>
          </div>
          <h2 className="text-xl font-bold mt-1 text-white">{problem.title}</h2>
        </div>

        {/* Live Status Indicators */}
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
            <Monitor className={`w-4 h-4 ${screenShareActive ? "text-emerald-400 animate-pulse" : "text-slate-500"}`} />
            <span>Screen Sharing:</span>
            <span className={screenShareActive ? "text-emerald-400 font-medium" : "text-amber-400 font-medium"}>
              {screenShareActive ? "● Connected" : "● Stopped"}
            </span>
          </div>

          <div className="flex items-center gap-2 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
            <Mic className="w-4 h-4 text-purple-400 animate-pulse" />
            <span>AI Status:</span>
            <span className="text-purple-300 font-medium">● AI Interviewer Listening</span>
          </div>
        </div>
      </div>

      {/* Grid Layout: Problem Description & Coding Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Problem Details (2 cols) */}
        <div className="lg:col-span-2 space-y-4 bg-slate-950/60 p-5 rounded-lg border border-slate-800/80">
          <div>
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">Problem Statement</h3>
            <p className="text-slate-200 text-sm whitespace-pre-line leading-relaxed">{problem.description}</p>
          </div>

          {problem.input_format && (
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Input Format</h4>
              <code className="text-xs font-mono bg-slate-900 px-2 py-1 rounded text-cyan-300 border border-slate-800">
                {problem.input_format}
              </code>
            </div>
          )}

          {problem.examples && problem.examples.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Examples</h4>
              <div className="space-y-2">
                {problem.examples.map((ex, i) => (
                  <div key={i} className="bg-slate-900 p-3 rounded-md text-xs font-mono border border-slate-800 space-y-1">
                    <div>
                      <span className="text-slate-500">Input: </span>
                      <span className="text-slate-200">{ex.input}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Output: </span>
                      <span className="text-emerald-400">{ex.output}</span>
                    </div>
                    {ex.explanation && (
                      <div className="text-slate-400 text-[11px] font-sans italic pt-0.5">
                        Note: {ex.explanation}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {problem.constraints && problem.constraints.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Constraints</h4>
              <ul className="list-disc list-inside text-xs text-slate-300 space-y-1 font-mono">
                {problem.constraints.map((c, idx) => (
                  <li key={idx}>{c}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Right Column: Coding Environment Controls & Actions */}
        <div className="space-y-5 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="bg-slate-950/80 p-4 rounded-lg border border-slate-800 space-y-3">
              <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                <Code className="w-4 h-4 text-blue-400" />
                Approved Coding Platform
              </h3>
              <p className="text-xs text-slate-400">
                You will implement your solution on our approved online platform: <span className="text-blue-300 font-medium">{codingPlatform}</span>.
              </p>
              
              <button
                onClick={handleOpenCompiler}
                className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm py-2.5 px-4 rounded-lg transition-colors shadow-lg shadow-blue-900/30"
              >
                <ExternalLink className="w-4 h-4" />
                Open Online Compiler
              </button>
            </div>

            {/* Screen Share Control */}
            <div className="bg-slate-950/80 p-4 rounded-lg border border-slate-800 space-y-3">
              <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                <Monitor className="w-4 h-4 text-emerald-400" />
                Screen Share Authorization
              </h3>
              <p className="text-xs text-slate-400">
                Share only the browser window or monitor containing your online coding environment so the AI Interviewer can observe your progress.
              </p>
              
              <button
                onClick={() => onToggleScreenShare && onToggleScreenShare(!screenShareActive)}
                className={`w-full flex items-center justify-center gap-2 font-medium text-xs py-2 px-3 rounded-lg border transition-colors ${
                  screenShareActive
                    ? "bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border-rose-500/30"
                    : "bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                }`}
              >
                <Video className="w-3.5 h-3.5" />
                {screenShareActive ? "Stop Sharing Screen" : "Share Coding Screen"}
              </button>
            </div>

            {/* Hint Box */}
            {currentHint && (
              <div className="bg-amber-500/10 border border-amber-500/30 p-3 rounded-lg text-xs text-amber-200 flex items-start gap-2">
                <HelpCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold block text-amber-300 mb-0.5">AI Interviewer Hint #{hintsGiven}:</span>
                  {currentHint}
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="space-y-2 pt-2">
            <button
              onClick={handleHintClick}
              className="w-full flex items-center justify-center gap-1.5 text-xs text-slate-400 hover:text-amber-300 py-1.5 px-3 rounded border border-slate-800 hover:border-amber-500/30 transition-colors"
            >
              <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
              Request Hint from AI
            </button>

            {onFinishCoding && (
              <button
                onClick={onFinishCoding}
                className="w-full flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs py-2 px-3 rounded-lg border border-slate-700 transition-colors"
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                I Have Finished Coding
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
