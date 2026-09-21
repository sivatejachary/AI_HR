'use client';

import React, { useState } from 'react';
import { useHRState } from '../../../stores/useHRStore';
import { EmptyState } from '../../../components/ui/EmptyState';
import { InterviewSessionDrawer } from '../../../components/interviews/InterviewSessionDrawer';
import { TestInterviewModal } from '../../../components/interviews/TestInterviewModal';
import { Calendar, ExternalLink, Bot, Eye, Sparkles } from 'lucide-react';
import { Interview } from '../../../types';

export default function InterviewsPage() {
  const hrState = useHRState();
  const [activeTab, setActiveTab] = useState<'UPCOMING' | 'TODAY' | 'COMPLETED'>('UPCOMING');
  const [selectedDrawerInterview, setSelectedDrawerInterview] = useState<Interview | null>(null);
  const [showTestModal, setShowTestModal] = useState<boolean>(false);

  const allInterviews = hrState.candidates.flatMap(c => c.interviews || []);

  const filteredInterviews = allInterviews.filter(i => {
    if (activeTab === 'UPCOMING') return i.status === 'UPCOMING';
    if (activeTab === 'TODAY') return i.status === 'TODAY' || i.date === 'Today';
    return i.status === 'COMPLETED';
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-lg border border-gray-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">Interviews</h1>
          <p className="text-xs text-gray-500 mt-1">
            Candidate interview schedules across Google Meet, Microsoft Teams, and Zoom powered by AI Interview Brain.
          </p>
        </div>

        <button
          onClick={() => setShowTestModal(true)}
          className="px-4 py-2 bg-gradient-to-r from-blue-900 to-indigo-900 hover:from-blue-800 hover:to-indigo-800 text-white rounded-lg text-xs font-semibold shadow-xs flex items-center gap-2 transition"
        >
          <Sparkles size={14} className="text-purple-300" /> Start Test AI Interview
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 bg-white rounded-lg p-1 text-xs font-medium text-gray-600 w-fit border shadow-xs">
        {[
          { key: 'UPCOMING', label: 'Upcoming Interviews' },
          { key: 'TODAY', label: "Today's Schedule" },
          { key: 'COMPLETED', label: 'Completed' }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-3.5 py-1.5 rounded-md transition ${
              activeTab === tab.key ? 'bg-blue-900 text-white font-semibold' : 'hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Interviews Table or Empty State */}
      {filteredInterviews.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="No interviews scheduled"
          description="Scheduled interviews will appear here."
        />
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Candidate</th>
                  <th className="py-3 px-4">Job Position</th>
                  <th className="py-3 px-4">Platform</th>
                  <th className="py-3 px-4">Date & Time</th>
                  <th className="py-3 px-4">Interviewer</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 text-gray-700">
                {filteredInterviews.map(int => (
                  <tr key={int.id} className="hover:bg-gray-50/80 transition">
                    <td className="py-3 px-4 font-semibold text-gray-900">
                      {int.candidateName}
                    </td>

                    <td className="py-3 px-4 text-gray-700">
                      {int.jobTitle}
                    </td>

                    <td className="py-3 px-4 text-gray-600">
                      {int.platform}
                    </td>

                    <td className="py-3 px-4 text-gray-600">
                      {int.date} at {int.time}
                    </td>

                    <td className="py-3 px-4 text-gray-600">
                      {int.interviewer}
                    </td>

                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-50 text-blue-800 border border-blue-200">
                        {int.status}
                      </span>
                    </td>

                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setSelectedDrawerInterview(int)}
                          className="px-2.5 py-1 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded text-xs font-medium transition flex items-center gap-1"
                        >
                          <Eye size={12} /> Monitor Session
                        </button>
                        <a
                          href={int.meetingLink}
                          target="_blank"
                          rel="noreferrer"
                          className="px-2.5 py-1 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded text-xs font-medium transition flex items-center gap-1"
                        >
                          Meeting <ExternalLink size={12} />
                        </a>
                        <button
                          onClick={() => {
                            const candidateObj = hrState.candidates.find(c => c.id === int.candidateId);
                            if (candidateObj) hrState.startAIInterview(candidateObj);
                          }}
                          className="px-2.5 py-1 bg-blue-900 hover:bg-blue-800 text-white rounded text-xs font-medium transition flex items-center gap-1"
                        >
                          <Bot size={12} /> Interview Room
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* AI Session Drawer */}
      {selectedDrawerInterview && (
        <InterviewSessionDrawer
          interview={selectedDrawerInterview}
          onClose={() => setSelectedDrawerInterview(null)}
          onApproveSuccess={() => {
            hrState.refreshAllData();
          }}
        />
      )}

      {/* Developer Test AI Interview Modal */}
      {showTestModal && (
        <TestInterviewModal onClose={() => setShowTestModal(false)} />
      )}
    </div>
  );
}
