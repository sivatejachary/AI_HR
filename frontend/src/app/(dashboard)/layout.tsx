'use client';

import React from 'react';
import { Sidebar } from '../../components/layout/Sidebar';
import { Header } from '../../components/layout/Header';
import { useHRState } from '../../stores/useHRStore';
import { CandidateProfileModal } from '../../components/candidates/CandidateProfileModal';
import { AIVoiceSimulatorModal } from '../../components/calling/AIVoiceSimulatorModal';
import { AIInterviewSimulatorModal } from '../../components/interviews/AIInterviewSimulatorModal';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const hrState = useHRState();

  return (
    <div className="flex h-screen overflow-hidden bg-[#F8F9FB]">
      {/* Sidebar Navigation */}
      <Sidebar isAgentOnline={hrState.agentState.isOnline} />

      {/* Main Page Area */}
      <div className="flex-1 flex flex-col md:pl-64 transition-all duration-200 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {children}
        </main>
      </div>

      {/* Global Modals */}
      {hrState.isCandidateModalOpen && hrState.selectedCandidate && (
        <CandidateProfileModal
          candidate={hrState.selectedCandidate}
          onClose={() => hrState.setIsCandidateModalOpen(false)}
          onToggleTakeover={hrState.toggleHumanTakeover}
          onTriggerCall={(c) => {
            hrState.setIsCandidateModalOpen(false);
            hrState.triggerAICall(c);
          }}
          onStartInterview={(c) => {
            hrState.setIsCandidateModalOpen(false);
            hrState.startAIInterview(c);
          }}
        />
      )}

      {hrState.isCallingModalOpen && hrState.activeCallCandidate && (
        <AIVoiceSimulatorModal
          candidate={hrState.activeCallCandidate}
          onClose={() => hrState.setIsCallingModalOpen(false)}
          onCompleteCall={hrState.completeAICall}
        />
      )}

      {hrState.isInterviewModalOpen && hrState.activeInterviewCandidate && (
        <AIInterviewSimulatorModal
          candidate={hrState.activeInterviewCandidate}
          onClose={() => hrState.setIsInterviewModalOpen(false)}
          onCompleteInterview={hrState.completeAIInterview}
        />
      )}
    </div>
  );
}
