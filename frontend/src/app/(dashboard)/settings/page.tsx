'use client';

import React, { useState } from 'react';
import { useHRState } from '../../../stores/useHRStore';
import { Settings, Save, CheckCircle2 } from 'lucide-react';

export default function SettingsPage() {
  const hrState = useHRState();
  const [policy, setPolicy] = useState(hrState.companyPolicy);
  const [elevenLabsKey, setElevenLabsKey] = useState('');
  const [n8nBaseUrl, setN8nBaseUrl] = useState('https://shivateja123.app.n8n.cloud/webhook/');
  const [webhooks, setWebhooks] = useState({
    candidateIntake: 'https://shivateja123.app.n8n.cloud/webhook/candidate-intake',
    postCall: 'https://shivateja123.app.n8n.cloud/webhook/elevenlabs-post-call',
    checkAvailability: 'https://shivateja123.app.n8n.cloud/webhook/check-interview-availability',
    scheduleInterview: 'https://shivateja123.app.n8n.cloud/webhook/schedule-interview',
    saveQA: 'https://shivateja123.app.n8n.cloud/webhook/save-interview-qa',
    transcript: 'https://shivateja123.app.n8n.cloud/webhook/interview-transcript',
    reschedule: 'https://shivateja123.app.n8n.cloud/webhook/reschedule-interview',
    cancel: 'https://shivateja123.app.n8n.cloud/webhook/cancel-interview'
  });
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSaveSettings = (e: React.FormEvent) => {
    e.preventDefault();
    hrState.setCompanyPolicy(policy);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-lg border border-gray-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight flex items-center gap-2">
            <Settings size={22} className="text-blue-900" /> Settings & Company Policy
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            Configure recruitment workflow constraints, ElevenLabs AI, and n8n webhook endpoints.
          </p>
        </div>

        {savedSuccess && (
          <span className="px-3 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded text-xs font-semibold flex items-center gap-1.5">
            <CheckCircle2 size={14} /> Settings Saved
          </span>
        )}
      </div>

      <form onSubmit={handleSaveSettings} className="space-y-6 text-xs">
        {/* Company Hiring Policy */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4 shadow-xs">
          <h2 className="text-base font-semibold text-gray-900 border-b border-gray-100 pb-3">
            Company Recruitment Policy
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-gray-700 font-medium block mb-1">Max Voice Call Attempts</label>
              <input
                type="number"
                value={policy.maxCallAttempts}
                onChange={e => setPolicy({ ...policy, maxCallAttempts: parseInt(e.target.value) || 1 })}
                className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-700"
              />
            </div>

            <div>
              <label className="text-gray-700 font-medium block mb-1">Working Hours Window</label>
              <input
                type="text"
                value={policy.workingHours}
                onChange={e => setPolicy({ ...policy, workingHours: e.target.value })}
                className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-700"
              />
            </div>

            <div>
              <label className="text-gray-700 font-medium block mb-1">Standard Interview Duration (Mins)</label>
              <input
                type="number"
                value={policy.interviewDurationMinutes}
                onChange={e => setPolicy({ ...policy, interviewDurationMinutes: parseInt(e.target.value) || 45 })}
                className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-700"
              />
            </div>

            <div>
              <label className="text-gray-700 font-medium block mb-1">Automated Reminder (Hours Before)</label>
              <input
                type="number"
                value={policy.reminderHoursBefore}
                onChange={e => setPolicy({ ...policy, reminderHoursBefore: parseInt(e.target.value) || 24 })}
                className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-700"
              />
            </div>
          </div>
        </div>

        {/* Integration Credentials */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4 shadow-xs">
          <h2 className="text-base font-semibold text-gray-900 border-b border-gray-100 pb-3 flex items-center justify-between">
            <span>Integration Credentials & n8n Live Webhooks</span>
            <span className="text-xs bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-mono">
              n8n Cloud: Active
            </span>
          </h2>

          <div className="space-y-4">
            <div>
              <label className="text-gray-700 font-medium block mb-1">ElevenLabs Voice API Key</label>
              <input
                type="password"
                value={elevenLabsKey}
                onChange={e => setElevenLabsKey(e.target.value)}
                className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-1.5 text-gray-900 font-mono focus:outline-none focus:border-blue-700"
              />
            </div>

            <div className="pt-2 border-t border-gray-100">
              <h3 className="font-semibold text-gray-800 mb-3">n8n Cloud Webhook Routing (shivateja123.app.n8n.cloud)</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="text-gray-600 text-[11px] block font-mono">Candidate Intake</label>
                  <input
                    type="text"
                    value={webhooks.candidateIntake}
                    onChange={e => setWebhooks({ ...webhooks, candidateIntake: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-2.5 py-1 text-[11px] font-mono text-gray-800"
                  />
                </div>
                <div>
                  <label className="text-gray-600 text-[11px] block font-mono">Post-call Webhook</label>
                  <input
                    type="text"
                    value={webhooks.postCall}
                    onChange={e => setWebhooks({ ...webhooks, postCall: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-2.5 py-1 text-[11px] font-mono text-gray-800"
                  />
                </div>
                <div>
                  <label className="text-gray-600 text-[11px] block font-mono">Check Availability</label>
                  <input
                    type="text"
                    value={webhooks.checkAvailability}
                    onChange={e => setWebhooks({ ...webhooks, checkAvailability: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-2.5 py-1 text-[11px] font-mono text-gray-800"
                  />
                </div>
                <div>
                  <label className="text-gray-600 text-[11px] block font-mono">Schedule Interview</label>
                  <input
                    type="text"
                    value={webhooks.scheduleInterview}
                    onChange={e => setWebhooks({ ...webhooks, scheduleInterview: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-2.5 py-1 text-[11px] font-mono text-gray-800"
                  />
                </div>
                <div>
                  <label className="text-gray-600 text-[11px] block font-mono">Save Q&A</label>
                  <input
                    type="text"
                    value={webhooks.saveQA}
                    onChange={e => setWebhooks({ ...webhooks, saveQA: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-2.5 py-1 text-[11px] font-mono text-gray-800"
                  />
                </div>
                <div>
                  <label className="text-gray-600 text-[11px] block font-mono">Transcript</label>
                  <input
                    type="text"
                    value={webhooks.transcript}
                    onChange={e => setWebhooks({ ...webhooks, transcript: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-2.5 py-1 text-[11px] font-mono text-gray-800"
                  />
                </div>
                <div>
                  <label className="text-gray-600 text-[11px] block font-mono">Reschedule</label>
                  <input
                    type="text"
                    value={webhooks.reschedule}
                    onChange={e => setWebhooks({ ...webhooks, reschedule: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-2.5 py-1 text-[11px] font-mono text-gray-800"
                  />
                </div>
                <div>
                  <label className="text-gray-600 text-[11px] block font-mono">Cancel Interview</label>
                  <input
                    type="text"
                    value={webhooks.cancel}
                    onChange={e => setWebhooks({ ...webhooks, cancel: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-300 rounded px-2.5 py-1 text-[11px] font-mono text-gray-800"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className="px-5 py-2 bg-blue-900 hover:bg-blue-800 text-white font-medium rounded-md flex items-center gap-1.5 transition"
          >
            <Save size={14} /> Save Settings
          </button>
        </div>
      </form>
    </div>
  );
}
